#!/usr/bin/env python3
"""
ZNVE Drift Detector: suite de paridad determinista (solo biblioteca estándar).

Certifica que master_spec.json es coherente, que cada artefacto generado coincide
con ella y que los contratos externos (servidor MCP, esquema de OpenRouter, paquete
de la skill) siguen alineados. Al final avisa, sin fallar, de los archivos
mantenidos a mano que citan otra versión de ZNVE.

Uso:
    python znve-auto/test_sync.py
"""

from __future__ import annotations

import ast
import base64
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import builder  # noqa: E402

REPO = builder.REPO_ROOT
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
# \b tras ZNVE: ZNVE_OR_ERROR o ZNVE_MCP_ERROR son identificadores, no citas de versión.
ZNVE_VERSION_REF = re.compile(r"ZNVE\b[^\n\d]{0,40}?v?(\d+\.\d+\.\d+)")
SKILL_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
MCP_SERVER = REPO / "integrations" / "mcp-server" / "znve-mcp-server.ts"
CONTRACT_CASES = REPO / "znve-auto" / "tool_contract_cases.json"
OPENROUTER_SCHEMA = REPO / "integrations" / "openrouter" / "response-schema.json"
# Instalador de la directiva global de DeepSeek Harness (el AGENTS.md que instala se genera).
DSH_INSTALLER = REPO / "integrations" / "deepseek" / "harness" / "install-dsh.ps1"
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")
SKILL_FILES = (
    "integrations/claude/skills/znve/SKILL.md",
    "integrations/gemini/skills/znve/SKILL.md",
)
ANTIGRAVITY_DIR = REPO / "integrations" / "antigravity"
# field-tests conserva datos archivados (directivas y transcripciones de versiones anteriores): no se actualizan.
HAND_MAINTAINED_SKIP = {".git", "node_modules", "dist", "znve-auto", "field-tests"}
# Presupuestos en bytes (RFC 0002 §3, medidos): un guardrail es una línea del prefijo de cada petición.
GUARDRAIL_MAX_BYTES = {"Cerca de Contexto (Context Fence)": 700, "Verificación Inviolable": 400}
# Regla común de fases más el perfil del asistente. La RFC proponía 900 B; la regla sola ya pesa más de 600 B.
AGENT_BLOCK_MAX_BYTES = 1400
# Descripciones de las herramientas MCP: viajan en el prefijo de cada petición (línea base v2.3.0: unos 2 KiB).
MCP_TOOL_DOCS_MAX_BYTES = 3200
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
HOST_PATH = re.compile(r"[A-Za-z]:\\Users\\|/Users/\w|/home/\w")


def frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    keys = {}
    for line in match.group(1).splitlines():
        if line and not line.startswith(" "):
            key, _, value = line.partition(":")
            keys[key.strip()] = value.strip()
    return keys


class SpecTests(unittest.TestCase):
    """Coherencia interna de master_spec.json."""

    @classmethod
    def setUpClass(cls):
        cls.spec = builder.load_spec()

    def test_identity(self):
        """Identificador canónico 'znve' y versión SemVer."""
        self.assertEqual(self.spec["name"], "znve")
        self.assertRegex(self.spec["version"], SEMVER)

    def test_commands(self):
        """Al menos 10 comandos únicos /znve-*, cada uno en una sola sección y con salida definida."""
        cmds = self.spec["commands"]
        self.assertGreaterEqual(len(cmds), 10)
        names = [c["name"] for c in cmds]
        self.assertEqual(len(names), len(set(names)), "nombres de comando duplicados")
        for c in cmds:
            self.assertTrue(c["name"].startswith("/znve-"), c["name"])
            self.assertTrue(c["summary_es"] and c["summary_en"], c["name"])
            if c["id"] != "help":
                self.assertTrue(c["outputs"] or c.get("phases"), f"{c['name']} no define salida")
        placed = [cid for s in self.spec["sections"] for cid in s["commands"]]
        self.assertCountEqual(placed, [c["id"] for c in cmds], "cada comando debe estar en exactamente una sección")

    def test_scenarios(self):
        """Seis modos operativos más el escenario de ayuda."""
        ids = [s["id"] for s in self.spec["scenarios"]]
        self.assertEqual(ids, list(range(7)))

    def test_guardrail_count_in_docs(self):
        """Los documentos escritos a mano citan el número real de guardrails."""
        total = len(self.spec["guardrails"])
        quoted = {
            "SPECIFICATION.md": r"en (\d+) guardrails|Aplica los (\d+) guardrails",
            "GLOSSARY.md": r"en (\d+) guardrails",
            "index.html": r"(\d+) reglas que el agente|(\d+) rules the agent",
        }
        for rel, pattern in quoted.items():
            found = [int(n) for groups in re.findall(pattern, (REPO / rel).read_text(encoding="utf-8")) for n in groups if n]
            self.assertTrue(found, f"{rel} ya no cita el número de guardrails")
            self.assertEqual(set(found), {total}, f"{rel} cita {sorted(set(found))} y la especificación tiene {total}")

    def test_agent_profiles_are_consistent(self):
        """Cada target con 'agent' usa un perfil existente y todo perfil se usa al menos una vez."""
        ids = [p["id"] for p in self.spec["agent_profiles"]]
        self.assertEqual(len(ids), len(set(ids)))
        used = {t["agent"] for t in self.spec["targets"] if "agent" in t}
        self.assertLessEqual(used, set(ids))
        self.assertEqual(set(ids), used, f"perfiles sin usar: {sorted(set(ids) - used)}")

    def test_agent_profiles_have_no_volatile_figures(self):
        """Los perfiles solo describen comportamiento: sin dígitos (precios, mínimos, versiones de modelo)."""
        for profile in self.spec["agent_profiles"]:
            for key, value in profile.items():
                if key.endswith("_es") or key == "name":
                    self.assertNotRegex(value, r"\d", f"{profile['id']}.{key}")
            for key in ("prefix", "invalidators", "session_cut", "phase_config"):
                self.assertTrue(profile[f"{key}_es"] and profile[f"{key}_en"], f"{profile['id']}.{key}")

    def test_guardrail_budgets(self):
        """Los guardrails de la Capa de Agente respetan el presupuesto de bytes de la RFC 0002."""
        for guardrail in self.spec["guardrails"]:
            limit = GUARDRAIL_MAX_BYTES.get(guardrail["title_es"])
            if limit:
                for lang in ("es", "en"):
                    size = len(guardrail[f"text_{lang}"].encode("utf-8"))
                    self.assertLessEqual(size, limit, f"{guardrail['title_es']} ({lang}) pesa {size} B")

    def test_mcp_tool_docs_budget(self):
        """Las descripciones de las herramientas MCP, que viajan en cada petición, no crecen sin control."""
        total = sum(
            len(f"{t['summary_es']} {t['behavior_es']}".encode("utf-8")) + sum(len(p["desc_es"].encode("utf-8")) for p in t["params"])
            for t in self.spec["mcp"]["tools"]
        )
        self.assertLessEqual(total, MCP_TOOL_DOCS_MAX_BYTES, f"las descripciones pesan {total} B")

    def test_default_format(self):
        """La respuesta por defecto tiene exactamente 4 bloques."""
        self.assertEqual(len(self.spec["default_format"]["blocks"]), 4)


class ArtifactTests(unittest.TestCase):
    """Paridad entre la especificación y los artefactos del repositorio."""

    @classmethod
    def setUpClass(cls):
        cls.spec = builder.load_spec()
        cls.rendered = builder.render_targets(cls.spec)

    def test_no_drift(self):
        """Todos los artefactos del repositorio coinciden con master_spec.json."""
        drift = builder.build(self.spec, verify_only=True)
        self.assertEqual(drift, [], "desfasados; ejecuta: python znve-auto/builder.py")

    def test_every_command_everywhere(self):
        """Cada directiva de agente menciona los 10 comandos."""
        for target in self.spec["targets"]:
            if not target.get("catalog", True):
                continue
            text = self.rendered[target["output"]]
            for c in self.spec["commands"]:
                self.assertIn(c["name"], text, f"{c['name']} falta en {target['output']}")

    def test_inviolable_verification_everywhere(self):
        """Cada directiva de agente lleva el guardrail de Verificación Inviolable (en español o en inglés)."""
        guard = next(g for g in self.spec["guardrails"] if g["title_es"] == "Verificación Inviolable")
        first = self.spec["guardrails"][0]
        checked = 0
        for target in self.spec["targets"]:
            text = self.rendered[target["output"]]
            if first["text_es"] not in text and first["text_en"] not in text:
                continue  # no es una directiva con guardrails (manual, instaladores, referencias)
            checked += 1
            self.assertTrue(
                guard["text_es"] in text or guard["text_en"] in text,
                f"{target['output']} no incluye el guardrail de Verificación Inviolable",
            )
        self.assertGreaterEqual(checked, 8, "se esperaban al menos 8 directivas con guardrails")

    def test_guardrails_in_order_everywhere(self):
        """Cada directiva que lista guardrails los lleva todos y en el orden de la especificación."""
        checked = 0
        for target in self.spec["targets"]:
            text = self.rendered[target["output"]]
            first = self.spec["guardrails"][0]
            if first["text_es"] not in text and first["text_en"] not in text:
                continue
            checked += 1
            positions = []
            for g in self.spec["guardrails"]:
                found = [text.find(t) for t in (g["text_es"], g["text_en"]) if t in text]
                self.assertTrue(found, f"{target['output']} no incluye el guardrail '{g['title_es']}'")
                positions.append(found[0])
            self.assertEqual(positions, sorted(positions), f"{target['output']}: guardrails desordenados")
        self.assertGreaterEqual(checked, 8)

    def test_command_adjustments(self):
        """Los ajustes de una frase de la Cerca de Contexto están en sus comandos (salida mínima, dos pasos, rangos...)."""
        cmds = {c["id"]: c for c in self.spec["commands"]}
        for cid, label in (("execute", "CÓDIGO QUIRÚRGICO"), ("hotfix", "CÓDIGO QUIRÚRGICO")):
            out = {o["label_es"]: o["desc_es"] for o in cmds[cid]["outputs"]}[label]
            self.assertIn("diff o edición acotada", out, cid)
        for cid, label in (("execute", "VERIFICACIÓN ATÓMICA"), ("hotfix", "COMANDO DE VALIDACIÓN")):
            out = {o["label_es"]: o["desc_es"] for o in cmds[cid]["outputs"]}[label]
            for needle in ("dos pasos", "primer fallo", "FALLO <archivo>:<línea>", "conteo de fallos"):
                self.assertIn(needle, out, f"{cid}: {needle}")
        self.assertIn("`contracts/`", cmds["execute"]["activation_es"])
        self.assertIn("Zona Roja", cmds["forensic"]["directive_es"])
        self.assertIn("rangos", cmds["forensic"]["directive_es"])
        self.assertIn("stack trace", cmds["triage"]["directive_es"])
        self.assertIn("corte de sesión", cmds["legacy-rescue"]["directive_es"])
        self.assertEqual(self.spec["contract_rules"]["stop_criterion"], "Contrato v1 sólido y cerrado. Listo para /znve-execute.")

    def test_phase_rule_everywhere(self):
        """Toda directiva con guardrails lleva la regla común de fases (en español o en inglés)."""
        layer = self.spec["agent_layer"]
        for target in self.spec["targets"]:
            text = self.rendered[target["output"]]
            if self.spec["guardrails"][0]["text_es"] not in text and self.spec["guardrails"][0]["text_en"] not in text:
                continue
            self.assertTrue(
                layer["phase_rule_es"] in text or layer["phase_rule_en"] in text,
                f"{target['output']} no incluye la regla común de fases",
            )

    def test_each_directive_has_only_its_profile(self):
        """Cada artefacto con 'agent' lleva el perfil de su asistente y ninguno de los otros."""
        profiles = {p["id"]: p for p in self.spec["agent_profiles"]}
        for target in self.spec["targets"]:
            if "agent" not in target:
                continue
            text = self.rendered[target["output"]]
            mine = profiles[target["agent"]]
            self.assertTrue(
                mine["prefix_es"] in text or mine["prefix_en"] in text, f"{target['output']} no incluye su perfil '{mine['id']}'"
            )
            for other in profiles.values():
                if other["id"] != mine["id"] and other["prefix_es"] != mine["prefix_es"]:
                    self.assertNotIn(other["prefix_es"], text, f"{target['output']} incluye el perfil de '{other['id']}'")
                    self.assertNotIn(other["prefix_en"], text, f"{target['output']} incluye el perfil de '{other['id']}'")

    def test_agent_block_budget(self):
        """El bloque de Capa de Agente (regla de fases y perfil) de cada asistente cabe en su presupuesto."""
        for profile in self.spec["agent_profiles"]:
            for render in (builder.agent_layer_body_md, builder.agent_layer_en):
                size = len(render(self.spec, profile["id"]).encode("utf-8"))
                self.assertLessEqual(size, AGENT_BLOCK_MAX_BYTES, f"{profile['id']}: {render.__name__} pesa {size} B")

    def test_manual_has_all_profiles(self):
        """El manual reúne la tabla completa de perfiles."""
        manual = self.rendered["protocols/COMMANDS.md"]
        for profile in self.spec["agent_profiles"]:
            self.assertIn(profile["name"], manual)

    def test_stable_prefix(self):
        """Prefijo estable por construcción: ningún artefacto generado contiene fechas ni rutas del host."""
        for target in self.spec["targets"]:  # los archivos con bloques gestionados (README, index.html) son de edición manual
            rel, text = target["output"], self.rendered[target["output"]]
            self.assertIsNone(DATE.search(text), f"{rel} contiene una fecha")
            self.assertIsNone(HOST_PATH.search(text), f"{rel} contiene una ruta de usuario del host")

    def test_harness_output_is_deterministic_and_verified(self):
        """El comando harness fija el determinismo del Golden Master y la verificación en dos pasos."""
        harness = next(c for c in self.spec["commands"] if c["id"] == "harness")
        outputs = {o["label_es"]: o["desc_es"] for o in harness["outputs"]}
        snapshots = outputs["SNAPSHOTS GOLDEN MASTER"]
        for needle in ("semilla", "`TZ`", "locale", "reloj", "volátiles", "aprobación humana"):
            self.assertIn(needle, snapshots)
        run = outputs["COMANDO DE EJECUCIÓN"]
        for needle in ("dos pasos", "primer fallo", "FALLO <archivo>:<línea>", "conteo de fallos"):
            self.assertIn(needle, run)

    def test_single_version(self):
        """Ningún artefacto generado cita una versión de ZNVE distinta de la especificación."""
        version = self.spec["version"]
        for rel, text in self.rendered.items():
            found = set(ZNVE_VERSION_REF.findall(text))
            self.assertLessEqual(found, {version}, f"{rel} cita {found - {version}}")

    def test_size_budgets(self):
        """Los artefactos con 'max_bytes' (p. ej. el AGENTS.md global de DSH) respetan su presupuesto."""
        budgeted = [t for t in self.spec["targets"] if "max_bytes" in t]
        self.assertTrue(budgeted, "ningún artefacto declara max_bytes")
        for target in budgeted:
            size = len(self.rendered[target["output"]].encode("utf-8"))
            self.assertLessEqual(size, target["max_bytes"], f"{target['output']} pesa {size} B")

    def test_no_residue(self):
        """Sin marcas [cite: N], vallas ```markdown iniciales ni enlaces de rastreo."""
        for rel, text in self.rendered.items():
            self.assertNotIn("[cite", text, rel)
            self.assertNotIn("utm_source=", text, rel)
            self.assertFalse(text.startswith("```"), f"{rel} empieza con una valla de código")

    def test_skill_frontmatter(self):
        """Las skills de Claude y Gemini cumplen las reglas de subida (formato Agent Skills)."""
        for rel in SKILL_FILES:
            with self.subTest(skill=rel):
                keys = frontmatter(self.rendered[rel])
                self.assertTrue(keys, "falta el frontmatter")
                self.assertLessEqual(set(keys), SKILL_KEYS, f"claves no permitidas: {set(keys) - SKILL_KEYS}")
                self.assertRegex(keys["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
                self.assertLessEqual(len(keys["name"]), 64)
                self.assertLessEqual(len(keys["description"]), 1024)
                self.assertNotRegex(keys["description"], r"[<>]")

    def test_skill_references_exist(self):
        """Cada enlace relativo de una skill apunta a un archivo generado dentro de su carpeta."""
        for rel in SKILL_FILES:
            folder = rel.rsplit("/", 1)[0]
            for link in re.findall(r"\]\((references/[^)]+)\)", self.rendered[rel]):
                self.assertIn(f"{folder}/{link}", self.rendered, f"{rel} enlaza {link}, que no se genera")

    def test_skill_bundle(self):
        """znve.zip contiene exactamente la carpeta de la skill."""
        for bundle in self.spec["bundles"]:
            with zipfile.ZipFile(REPO / bundle["output"]) as zf:
                names = sorted(zf.namelist())
            expected = sorted(builder.bundle_members(bundle, self.rendered))
            self.assertEqual(names, expected)
            self.assertIn(f"{bundle['folder']}/SKILL.md", names)

    def test_bundle_ignores_caches(self):
        """Las cachés y los archivos ocultos no entran en znve.zip."""
        for rel in ("__pycache__/x.cpython-314.pyc", ".DS_Store", "references/.cache/a.md", "scripts/x.pyc"):
            self.assertTrue(builder.bundle_ignored(rel), rel)
        for rel in ("SKILL.md", "references/chameleon-layer.md"):
            self.assertFalse(builder.bundle_ignored(rel), rel)


class ExternalContractTests(unittest.TestCase):
    """Contratos que viven fuera de las plantillas pero dependen de la especificación."""

    @classmethod
    def setUpClass(cls):
        cls.spec = builder.load_spec()
        cls.server = MCP_SERVER.read_text(encoding="utf-8")

    def test_mcp_tools_match_server(self):
        """Las herramientas MCP documentadas son las que expone el servidor."""
        exposed = set(re.findall(r'registerTool\(\s*"(znve_\w+)"', self.server))
        documented = {t["name"] for t in self.spec["mcp"]["tools"]}
        self.assertEqual(documented, exposed)

    def test_mcp_help_sections(self):
        """protocols/COMMANDS.md conserva las secciones que filtra znve_help."""
        manual = builder.render_targets(self.spec)["protocols/COMMANDS.md"]
        headings = [line for line in manual.splitlines() if line.startswith("## ")]
        for section in re.findall(r'\w+:\s*"(SECCIÓN \d)"', self.server):
            self.assertTrue(any(section in h for h in headings), f"falta el encabezado {section}")

    def test_openrouter_scenarios(self):
        """El enum de escenarios de OpenRouter coincide con los escenarios de la especificación."""
        schema = json.loads(OPENROUTER_SCHEMA.read_text(encoding="utf-8"))
        enum = schema["json_schema"]["schema"]["properties"]["scenario"]["enum"]
        self.assertEqual(enum, [s["key"] for s in self.spec["scenarios"]] + ["unspecified"])


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AntigravityPythonTests(unittest.TestCase):
    """Los módulos Python de Antigravity leen versión y catálogo de la especificación."""

    @classmethod
    def setUpClass(cls):
        cls.spec = builder.load_spec()
        sys.path.insert(0, str(ANTIGRAVITY_DIR))
        cls.skill = load_module("znve_skill", ANTIGRAVITY_DIR / "znve_skill.py")

    def test_constants_match_spec(self):
        """znve_skill.py expone la versión, el nombre y el catálogo de la especificación."""
        self.assertEqual(self.skill.ZNVE_VERSION, self.spec["version"])
        self.assertEqual(self.skill.ZNVE_NAME, self.spec["name"])
        self.assertEqual(self.skill.znve_help("commands")["text"], builder.help_block(self.spec))
        for c in self.spec["commands"]:
            self.assertIn(c["name"], self.skill.ZNVE_SYSTEM_INSTRUCTION)

    def test_skill_descriptor(self):
        """get_znve_skill() describe la skill 'znve' con sus 6 herramientas sin importar el SDK."""
        skill = self.skill.get_znve_skill()
        self.assertEqual(skill["name"], "znve")
        self.assertEqual(skill["system_instructions"], self.skill.ZNVE_SYSTEM_INSTRUCTION)
        self.assertEqual(len(skill["tools"]), 6)
        for tool in skill["tools"]:
            self.assertTrue(tool.__doc__, f"{tool.__name__} necesita docstring para el SDK")

    def test_no_legacy_skill_name(self):
        """Los artefactos de Antigravity usan 'znve', no el nombre largo antiguo."""
        rendered = builder.render_targets(self.spec)
        for rel, text in rendered.items():
            if rel.startswith("integrations/antigravity/") and not rel.endswith(".md"):
                self.assertNotRegex(text, r"zero[-_]noise[-_]vibe[-_]engineering", rel)

    def test_workspace_installer_migrates(self):
        """Auto_Installer instala en .agents/skills/znve/ y retira la instalación de .antigravity/."""
        installer = load_module("znve_auto_installer", ANTIGRAVITY_DIR / "Auto_Installer.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / ".antigravity"
            (legacy / "skills" / "znve").mkdir(parents=True)
            (legacy / "skills" / "znve" / "znve_skill.py").write_text("# antiguo\n", encoding="utf-8")
            (legacy / "antigravity.json").write_text(json.dumps({"skills": {
                "zero_noise_vibe_engineering": {"protocol_version": "2.2.0"},
                "znve": {"protocol_version": "2.3.0"},
                "otra": {"enabled": True},
            }}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                target = installer.run_installer(root)

            self.assertEqual(target, (root / ".agents" / "skills" / "znve").resolve())
            self.assertEqual((target / "SKILL.md").read_bytes(), (ANTIGRAVITY_DIR / "SKILL.md").read_bytes())
            self.assertEqual(
                (target / "scripts" / "znve_skill.py").read_bytes(), (ANTIGRAVITY_DIR / "znve_skill.py").read_bytes()
            )
            self.assertFalse((legacy / "skills").exists())
            skills = json.loads((legacy / "antigravity.json").read_text(encoding="utf-8"))["skills"]
            self.assertEqual(list(skills), ["otra"])

    def test_global_installer_paths(self):
        """install_znve_global escribe en ~/.gemini/config/skills/znve y retira la copia legacy."""
        installer = load_module("znve_global_installer_paths", ANTIGRAVITY_DIR / "install_znve_global.py")
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            legacy = home / ".gemini" / "antigravity" / "skills" / "znve"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("---\nname: zero-noise-vibe-engineering\n---\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                installer.install(home)
            installed = home / ".gemini" / "config" / "skills" / "znve" / "SKILL.md"
            self.assertEqual(installed.read_text(encoding="utf-8"), (ANTIGRAVITY_DIR / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse(legacy.exists())
            self.assertTrue((home / ".gemini" / "config" / "global_workflows" / "znve-help.md").exists())
            self.assertEqual((home / ".gemini" / "GEMINI.md").read_text(encoding="utf-8").count("znve:start"), 1)

    def test_global_gemini_block_is_static_and_minimal(self):
        """El bloque de GEMINI.md es mínimo y estático: sin catálogo de comandos (lo da la skill) ni fechas."""
        installer = load_module("znve_global_installer_block", ANTIGRAVITY_DIR / "install_znve_global.py")
        rule = installer.upsert_rule("")
        self.assertIn("Cerca de Contexto", rule)
        self.assertIn("Verificación Inviolable", rule)
        for command in self.spec["commands"]:
            if command["id"] != "help":
                self.assertNotIn(command["name"], rule, "el bloque no debe repetir el catálogo")
        self.assertIsNone(DATE.search(rule))
        self.assertLessEqual(len(rule.encode("utf-8")), 1400)
        self.assertEqual(installer.upsert_rule(rule), rule)

    def test_global_rule_is_replaced(self):
        """install_znve_global sustituye la regla de GEMINI.md en vez de duplicarla."""
        installer = load_module("znve_global_installer", ANTIGRAVITY_DIR / "install_znve_global.py")
        legacy = (
            "Mis reglas.\n\n# DIRECTIVA GLOBAL ZNVE v2.2.0 (Zero-Noise Vibe Engineering)\n"
            "Cuando el usuario mencione comandos `/znve-*`:\n1. Uno.\n2. Dos.\n3. Tres.\n\nOtra regla.\n"
        )
        once = installer.upsert_rule(legacy)
        self.assertNotIn("v2.2.0", once)
        self.assertIn(f"ZNVE v{self.spec['version']}", once)
        self.assertTrue(once.startswith("Mis reglas.") and once.rstrip().endswith("Otra regla."))
        self.assertEqual(installer.upsert_rule(once), once)
        self.assertEqual(installer.upsert_rule("").count("znve:start"), 1)


class SkillToolBehaviorTests(unittest.TestCase):
    """Las herramientas de znve_skill.py cumplen las barandillas que anuncian.

    Las rutas relativas se resuelven contra ZNVE_WORKSPACE. El cwd del test es otro
    directorio temporal, así que nada se escribe fuera del temporal aunque falle una barandilla.
    """

    MAX_SCAN_BYTES = 1024 * 1024

    @classmethod
    def setUpClass(cls):
        cls.skill = load_module("znve_skill_behavior", ANTIGRAVITY_DIR / "znve_skill.py")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name).resolve()
        self.ws = self.tmp / "ws"
        self.outside = self.tmp / "outside"
        for folder in (self.ws, self.outside, self.tmp / "cwd", self.ws / ".git"):
            folder.mkdir(parents=True)
        (self.outside / "secret.txt").write_text("TOP-SECRET", encoding="utf-8")
        (self.ws / "prod.py").write_text("X = 1\n", encoding="utf-8")
        (self.ws / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        self._cwd = os.getcwd()
        os.chdir(self.tmp / "cwd")
        self._env = mock.patch.dict(os.environ, {"ZNVE_WORKSPACE": str(self.ws)})
        self._env.start()

    def tearDown(self):
        self._env.stop()
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def assertRejected(self, result: dict, msg: str = ""):
        self.assertNotEqual(result["status"], "SUCCESS", msg or result)

    # --- Contención de rutas (P1) ---------------------------------------------

    def test_forensic_reads_inside_workspace(self):
        result = self.skill.znve_forensic_scan("prod.py")
        self.assertEqual(result["status"], "SUCCESS", result)

    def test_forensic_rejects_escape(self):
        for target in ("../outside/secret.txt", str(self.outside / "secret.txt")):
            self.assertRejected(self.skill.znve_forensic_scan(target), target)

    def test_harness_rejects_filename_escape(self):
        result = self.skill.znve_scaffold_harness("tests/characterization", "../../prod.py", "OVERWRITTEN")
        self.assertRejected(result)
        self.assertEqual((self.ws / "prod.py").read_text(encoding="utf-8"), "X = 1\n")

    def test_harness_rejects_non_test_directories(self):
        for folder in ("latest", "src/tests", "../outside/tests"):
            self.assertRejected(self.skill.znve_scaffold_harness(folder, "h.py", "pass\n"), folder)
        self.assertFalse((self.outside / "tests").exists())

    def test_harness_writes_under_tests(self):
        result = self.skill.znve_scaffold_harness("tests/characterization", "test_legacy.py", "pass\n")
        self.assertEqual(result["status"], "SUCCESS", result)
        self.assertTrue((self.ws / "tests" / "characterization" / "test_legacy.py").is_file())

    def test_harness_never_overwrites(self):
        """Aplica la Verificación Inviolable por código: un arnés o snapshot existente no se sobrescribe."""
        first = self.skill.znve_scaffold_harness("tests/characterization", "test_legacy.py", "ORIGINAL\n")
        self.assertEqual(first["status"], "SUCCESS", first)
        again = self.skill.znve_scaffold_harness("tests/characterization", "test_legacy.py", "CAMBIADO\n")
        self.assertRejected(again)
        folder = self.ws / "tests" / "characterization"
        self.assertEqual((folder / "test_legacy.py").read_text(encoding="utf-8"), "ORIGINAL\n")
        self.assertEqual([p.name for p in folder.iterdir()], ["test_legacy.py"], "sin temporales residuales")

    # --- Escape por enlaces (S7) ----------------------------------------------

    def link_dir(self, link: Path, target: Path) -> None:
        """Enlace de directorio: symlink, o junction en Windows (no necesita privilegios)."""
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            made = os.name == "nt" and subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True
            ).returncode == 0
            if not made:
                self.skipTest("no se pudo crear el enlace en este sistema")

    def test_directory_link_cannot_escape(self):
        self.link_dir(self.ws / "link", self.outside)
        read = self.skill.znve_forensic_scan("link/secret.txt")
        self.assertRejected(read)
        self.assertEqual(read["code"], "OUTSIDE_WORKSPACE")
        self.assertNotIn("TOP-SECRET", str(read))
        write = self.skill.znve_surgical_write("link/pwned.txt", "x", "not_applicable")
        self.assertEqual(write["code"], "OUTSIDE_WORKSPACE")
        self.assertFalse((self.outside / "pwned.txt").exists())

    def test_link_inside_tests_cannot_take_the_harness_out(self):
        (self.ws / "tests").mkdir(exist_ok=True)
        self.link_dir(self.ws / "tests" / "out", self.outside)
        result = self.skill.znve_scaffold_harness("tests/out", "h.py", "pass\n")
        self.assertEqual(result["code"], "OUTSIDE_WORKSPACE")
        self.assertFalse((self.outside / "h.py").exists())

    def test_file_link_to_a_secret_is_denied(self):
        (self.ws / ".env").write_text("TOKEN=CANARY", encoding="utf-8")
        try:
            os.symlink(self.ws / ".env", self.ws / "notas.txt")
        except (OSError, NotImplementedError):
            self.skipTest("no se pudo crear el enlace en este sistema")
        result = self.skill.znve_forensic_scan("notas.txt")
        self.assertEqual(result["code"], "SECRET_DENIED")
        self.assertNotIn("CANARY", str(result))

    # --- Cerca de Contexto por código (M1-M3) ---------------------------------

    def test_forensic_range(self):
        (self.ws / "lines.py").write_text("a = 1\nb = 2\nopen('x')\nd = 4\n", encoding="utf-8")
        whole = self.skill.znve_forensic_scan("lines.py")
        self.assertEqual(whole["status"], "SUCCESS", whole)
        self.assertTrue(whole["side_effects"]["file_system_io"])
        self.assertIsNone(whole["range"])
        part = self.skill.znve_forensic_scan("lines.py", start_line=1, end_line=2)
        self.assertEqual(part["status"], "SUCCESS", part)
        self.assertFalse(part["side_effects"]["file_system_io"], "solo se analiza el rango pedido")
        self.assertEqual(part["range"], {"start_line": 1, "end_line": 2})
        self.assertEqual(part["total_lines"], 4)
        self.assertEqual(self.skill.znve_forensic_scan("lines.py", start_line=4)["status"], "SUCCESS")

    def test_forensic_rejects_bad_ranges(self):
        (self.ws / "lines.py").write_text("a = 1\nb = 2\n", encoding="utf-8")
        for kwargs in (
            {"start_line": 2, "end_line": 1},
            {"start_line": 0},
            {"start_line": -3},
            {"end_line": 1.5},
            {"start_line": True},
            {"start_line": 3},
            {"end_line": 99},
        ):
            self.assertRejected(self.skill.znve_forensic_scan("lines.py", **kwargs), str(kwargs))

    def test_secrets_are_denied_for_read_and_write(self):
        for name in (".env", ".env.local", "id_rsa", "server.pem", "credentials.json", ".ENV"):
            (self.ws / name).write_text("TOKEN=CANARY", encoding="utf-8")
            result = self.skill.znve_forensic_scan(name)
            self.assertRejected(result, name)
            self.assertNotIn("CANARY", str(result))
            self.assertRejected(self.skill.znve_surgical_write(name, "X=1", "not_applicable"), name)
            self.assertEqual((self.ws / name).read_text(encoding="utf-8"), "TOKEN=CANARY", name)
        self.assertRejected(self.skill.znve_surgical_write("deploy.key", "X=1", "not_applicable"))
        self.assertFalse((self.ws / "deploy.key").exists())
        self.assertRejected(self.skill.znve_scaffold_harness("tests/secretos", ".env", "X=1"))

    def test_secret_templates_are_allowed(self):
        (self.ws / ".env.example").write_text("TOKEN=changeme", encoding="utf-8")
        self.assertEqual(self.skill.znve_forensic_scan(".env.example")["status"], "SUCCESS")
        self.assertEqual(self.skill.znve_surgical_write(".env.sample", "X=", "not_applicable")["status"], "SUCCESS")

    def test_help_defaults_to_commands(self):
        commands = self.skill.znve_help()
        self.assertEqual(commands["topic"], "commands")
        self.assertEqual(commands, self.skill.znve_help("commands"))
        self.assertNotIn("MODOS DE OPERACIÓN", commands["text"])
        everything = self.skill.znve_help("all")["text"]
        self.assertIn(commands["text"], everything)
        self.assertIn("MODOS DE OPERACIÓN", everything)
        self.assertIn("znve_forensic_scan", self.skill.znve_help("mcp_tools")["text"])
        self.assertRejected(self.skill.znve_help("nope"))

    def test_write_rejects_escape(self):
        result = self.skill.znve_surgical_write("../outside/pwned.txt", "x", "not_applicable")
        self.assertRejected(result)
        self.assertFalse((self.outside / "pwned.txt").exists())

    def test_write_rejects_protected_folders(self):
        for target in (".git/config", "node_modules/pkg/index.js"):
            self.assertRejected(self.skill.znve_surgical_write(target, "x", "not_applicable"), target)
        self.assertEqual((self.ws / ".git" / "config").read_text(encoding="utf-8"), "[core]\n")

    def test_write_inside_workspace(self):
        result = self.skill.znve_surgical_write("app/ok.py", "X = 2\n", "not_applicable")
        self.assertEqual(result["status"], "SUCCESS", result)
        self.assertEqual((self.ws / "app" / "ok.py").read_text(encoding="utf-8"), "X = 2\n")
        self.assertEqual(sorted(p.name for p in (self.ws / "app").iterdir()), ["ok.py"])

    # --- Barandillas de análisis (P2) -----------------------------------------

    def test_write_rejects_silenced_errors(self):
        silenced = (
            "try { f(); } catch (e) {}",
            "try { f(); } catch {}",
            "try { f(); } catch (e) {\n  // se ignora\n}",
            "try { f(); } catch (e) { /* nada */ }",
            "try:\n    f()\nexcept:\n    pass\n",
            "try:\n    f()\nexcept Exception:\n    pass\n",
            "try:\n    f()\nexcept (ValueError, KeyError) as e:\n    ...\n",
            "load().catch(() => {});",
        )
        for code in silenced:
            self.assertRejected(self.skill.znve_surgical_write("app/silenced.txt", code, "finally"), code)

    def test_validate_detects_banned_imports(self):
        for code in (
            "import _ from 'lodash';",
            "const _ = require('lodash');",
            'const axios = require("axios");',
            "import requests",
            "from requests import get",
            "using Lodash;",
        ):
            self.assertEqual(self.skill.znve_validate_contract(code, ["lodash", "axios", "requests"])["status"], "REJECTED", code)

    def test_validate_detects_blind_queries(self):
        for code in ("q = 'select * from users'", "q = 'SELECT   * FROM users'", "db.users.find({ })"):
            self.assertEqual(self.skill.znve_validate_contract(code, ["lodash"])["status"], "REJECTED", code)

    def test_write_accepts_handled_errors(self):
        code = "try:\n    f()\nexcept ValueError as exc:\n    raise RuntimeError('f falló') from exc\n"
        self.assertEqual(self.skill.znve_surgical_write("app/handled.py", code, "finally")["status"], "SUCCESS")

    def test_validate_ignores_substrings(self):
        result = self.skill.znve_validate_contract("class Ratio:\n    radio: int\n", ["io", "rat"])
        self.assertEqual(result["status"], "APPROVED", result)

    def test_audit_result_property_is_not_blocking(self):
        self.assertTrue(self.skill.znve_audit_resources("var a = api.ResultSet; y.ResultCode = 0;")["clean"])
        for code in ("var r = task.Result;", "task.GetAwaiter().GetResult();", "mWakeLock.acquire();"):
            self.assertFalse(self.skill.znve_audit_resources(code)["clean"], code)

    def test_forensic_database_detection(self):
        (self.ws / "arrays.js").write_text("const n = items.find((x) => x.ok);\ndelete cache.key;\n", encoding="utf-8")
        (self.ws / "repo.sql").write_text("DELETE FROM sessions WHERE expires_at < now();\n", encoding="utf-8")
        self.assertFalse(self.skill.znve_forensic_scan("arrays.js")["side_effects"]["database_mutations"])
        self.assertTrue(self.skill.znve_forensic_scan("repo.sql")["side_effects"]["database_mutations"])

    def test_forensic_rejects_large_and_binary_files(self):
        (self.ws / "big.txt").write_bytes(b"a" * (self.MAX_SCAN_BYTES + 1))
        (self.ws / "bin.dat").write_bytes(b"PK\x00\x03\x04")
        for target in ("big.txt", "bin.dat", "."):
            self.assertRejected(self.skill.znve_forensic_scan(target), target)


class DshInstallerTests(unittest.TestCase):
    """install-dsh.ps1 instala la directiva como un bloque y nunca toca lo que no es de ZNVE."""

    START, END = "<!-- znve:start -->", "<!-- znve:end -->"

    @classmethod
    def setUpClass(cls):
        cls.spec = builder.load_spec()
        cls.source = (DSH_INSTALLER.parent / "AGENTS.md").read_text(encoding="utf-8")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.agents = self.home / "AGENTS.md"

    def tearDown(self):
        self._tmp.cleanup()

    def run_installer(self, *flags: str) -> subprocess.CompletedProcess:
        policy = ["-ExecutionPolicy", "Bypass"] if os.name == "nt" else []  # la política de ejecución es solo de Windows
        cmd = [POWERSHELL, "-NoProfile", *policy, "-File", str(DSH_INSTALLER), "-DshHome", str(self.home), *flags]
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)

    def backups(self) -> list[str]:
        return sorted(p.name for p in self.home.glob("AGENTS.md.bak-*"))

    def test_installer_cites_only_spec_version(self):
        """El instalador no lleva versiones escritas a mano que se queden atrás al subir de versión."""
        refs = set(ZNVE_VERSION_REF.findall(DSH_INSTALLER.read_text(encoding="utf-8")))
        self.assertLessEqual(refs, {self.spec["version"]}, f"cita {sorted(refs - {self.spec['version']})}")

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_install_into_empty_home(self):
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.agents.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(self.START) and text.rstrip().endswith(self.END))
        self.assertIn(self.source.strip(), text)
        self.assertNotIn("\r", text)

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_install_keeps_existing_content_and_is_idempotent(self):
        self.agents.write_text("Mis reglas.\n", encoding="utf-8")
        self.assertEqual(self.run_installer().returncode, 0)
        once = self.agents.read_text(encoding="utf-8")
        self.assertTrue(once.startswith("Mis reglas.\n"))
        self.assertEqual(once.count(self.START), 1)
        self.assertEqual(len(self.backups()), 1)
        self.assertEqual(self.run_installer().returncode, 0)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), once)
        self.assertEqual(len(self.backups()), 1, "una reinstalación idéntica no debe crear copias")

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_install_replaces_stale_block(self):
        self.agents.write_text(f"Antes.\n\n{self.START}\nviejo\n{self.END}\n\nDespués.\n", encoding="utf-8")
        self.assertEqual(self.run_installer().returncode, 0)
        text = self.agents.read_text(encoding="utf-8")
        self.assertNotIn("viejo", text)
        self.assertTrue(text.startswith("Antes.") and text.rstrip().endswith("Después."))
        self.assertEqual(text.count(self.START), 1)

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_install_migrates_whole_file_install(self):
        self.agents.write_text(self.source, encoding="utf-8")
        self.assertEqual(self.run_installer().returncode, 0)
        text = self.agents.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(self.START))
        self.assertEqual(text.count("Estándar activo:"), 1)

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_dry_run_writes_nothing(self):
        self.agents.write_text("Mis reglas.\n", encoding="utf-8")
        self.assertEqual(self.run_installer("-DryRun").returncode, 0)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), "Mis reglas.\n")
        self.assertEqual(self.backups(), [])

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_uninstall_removes_only_the_block(self):
        self.agents.write_text("Mis reglas.\n", encoding="utf-8")
        self.run_installer()
        self.assertEqual(self.run_installer("-Uninstall").returncode, 0)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), "Mis reglas.\n")

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_uninstall_deletes_file_left_empty(self):
        self.run_installer()
        self.assertEqual(self.run_installer("-Uninstall").returncode, 0)
        self.assertFalse(self.agents.exists())

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_uninstall_never_touches_foreign_global(self):
        """Sin la directiva de ZNVE, desinstalar no borra ni modifica el AGENTS.md del usuario."""
        self.agents.write_text("Reglas ajenas a ZNVE.\n", encoding="utf-8")
        self.assertEqual(self.run_installer("-Uninstall").returncode, 0)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), "Reglas ajenas a ZNVE.\n")
        self.assertEqual(self.backups(), [])

    @unittest.skipUnless(POWERSHELL, "PowerShell no está disponible")
    def test_uninstall_legacy_restores_newest_backup_by_name(self):
        """Una instalación antigua (archivo entero) restaura la copia más reciente por nombre, no por fecha."""
        self.agents.write_text(self.source, encoding="utf-8")
        old = self.home / "AGENTS.md.bak-20260101-000000"
        new = self.home / "AGENTS.md.bak-20260201-000000"
        new.write_text("Reglas nuevas.\n", encoding="utf-8")
        old.write_text("Reglas viejas.\n", encoding="utf-8")
        os.utime(new, (1_000_000_000, 1_000_000_000))  # la más reciente por nombre es la más antigua por fecha
        self.assertEqual(self.run_installer("-Uninstall").returncode, 0)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), "Reglas nuevas.\n")


class ToolContractTests(unittest.TestCase):
    """Contrato de respuesta común (RFC 0004, paso 5): el servidor MCP y znve_skill.py responden lo mismo."""

    @classmethod
    def setUpClass(cls):
        cls.spec = builder.load_spec()
        cls.cases = json.loads(CONTRACT_CASES.read_text(encoding="utf-8"))
        cls.skill = load_module("znve_skill_contract", ANTIGRAVITY_DIR / "znve_skill.py")
        cls.codes = {e["code"]: e["status"] for e in cls.spec["mcp"]["contract"]["error_codes"]}

    @staticmethod
    def write_files(root: Path, files: dict) -> None:
        for name, spec in files.items():
            target = root / name
            if name.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(spec, str):
                target.write_text(spec, encoding="utf-8", newline="")
            elif "base64" in spec:
                target.write_bytes(base64.b64decode(spec["base64"]))
            else:
                target.write_bytes(spec["fill"].encode() * spec["bytes"])

    def assert_subset(self, actual, expected, where: str) -> None:
        if isinstance(expected, dict):
            self.assertIsInstance(actual, dict, f"{where}: se esperaba un objeto")
            for key, value in expected.items():
                self.assertIn(key, actual, f"{where}.{key} falta")
                self.assert_subset(actual[key], value, f"{where}.{key}")
        else:
            self.assertEqual(actual, expected, where)

    def test_cases_match_the_shared_contract(self):
        """Cada caso de tool_contract_cases.json da el resultado esperado (los mismos que ejecuta el servidor MCP)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            ws, outside, cwd = root / "ws", root / "outside", root / "cwd"
            for folder in (ws, outside, cwd):
                folder.mkdir()
            self.write_files(ws, self.cases["files"])
            self.write_files(outside, self.cases["outside_files"])
            previous = os.getcwd()
            os.chdir(cwd)
            try:
                with mock.patch.dict(os.environ, {"ZNVE_WORKSPACE": str(ws)}):
                    for case in self.cases["cases"]:
                        with self.subTest(case["id"]):
                            result = getattr(self.skill, case["tool"])(**case["args"])
                            text = json.dumps(result, ensure_ascii=False)
                            self.assertEqual(list(result)[0], "status", text)
                            self.assert_subset(result, case["expect"], case["id"])
                            for key, length in case.get("counts", {}).items():
                                self.assertEqual(len(result[key]), length, f"{case['id']}.{key}")
                            for needle in case.get("content_contains", []):
                                self.assertIn(needle, result["content"], case["id"])
                            for needle in case.get("content_excludes", []):
                                self.assertNotIn(needle, result["content"], case["id"])
                            for needle in case.get("result_excludes", []):
                                self.assertNotIn(needle, text, case["id"])
                            self.assertNotIn(str(ws), text, f"{case['id']}: expone la ruta del host")
                            self.assertNotIn(str(ws).replace("\\", "\\\\"), text)
                    self.assertEqual((ws / ".env").read_text(encoding="utf-8"), "TOKEN=CANARY-12345")
                    self.assertFalse((outside / "pwned.txt").exists())
                    self.assertEqual((ws / "tests" / "characterization" / "test_legacy.py").read_text(encoding="utf-8"), "pass\n")
            finally:
                os.chdir(previous)

    def test_every_code_has_the_status_the_spec_declares(self):
        """Los casos compartidos cubren cada código de error y su status coincide con el de la especificación."""
        covered = set()
        for case in self.cases["cases"]:
            code = case["expect"].get("code")
            if code:
                self.assertEqual(case["expect"]["status"], self.codes[code], case["id"])
                covered.add(code)
        self.assertEqual(covered, set(self.codes) - {"IO_ERROR"}, "códigos sin caso compartido")
        self.assertEqual(self.skill.ERROR_STATUS, self.codes)

    def test_both_implementations_use_the_same_codes(self):
        """Los códigos usados en el servidor MCP y en znve_skill.py son los de la especificación, y los dos usan todos."""
        usage = re.compile(r"(?:_?fail|_?failure|ZnveError)\(\s*[\"']([A-Z_]+)[\"']|code[\"']?\s*[:=]\s*[\"']([A-Z_]+)[\"']")

        def used(path: Path) -> set:
            return {a or b for a, b in usage.findall(path.read_text(encoding="utf-8"))}

        server = used(MCP_SERVER)
        python = used(ANTIGRAVITY_DIR / "znve_skill.py")
        self.assertEqual(server, set(self.codes))
        self.assertEqual(python, set(self.codes))

    def test_default_banned_libraries_are_shared(self):
        self.assertEqual(list(self.skill.DEFAULT_BANNED_LIBRARIES), self.spec["mcp"]["contract"]["default_banned_libraries"])
        self.assertIn(json.dumps(self.spec["mcp"]["contract"]["default_banned_libraries"], ensure_ascii=False), MCP_SERVER.read_text(encoding="utf-8"))

    def test_server_version_is_the_contract_version(self):
        package = json.loads((MCP_SERVER.parent / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["version"], self.spec["mcp"]["contract"]["server_version"])
        self.assertIn("zod", package["dependencies"])

    def test_manual_documents_the_contract(self):
        """COMMANDS.md (SECCIÓN 2) documenta los estados, los campos de cada herramienta y todos los códigos."""
        manual = builder.render_targets(self.spec)["protocols/COMMANDS.md"]
        self.assertIn("### Contrato de respuesta", manual)
        for code in self.codes:
            self.assertIn(f"`{code}`", manual)
        for tool in self.spec["mcp"]["tools"]:
            self.assertIn(f"| `{tool['name']}` |", manual)


class BundleTests(unittest.TestCase):
    """El paquete de la skill contiene solo lo generado o lo declarado: un archivo suelto es un error."""

    BUNDLE = {"output": "skills/znve.zip", "root": "skills", "folder": "znve"}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._patch = mock.patch.object(builder, "REPO_ROOT", self.root)
        self._patch.start()
        self.folder = self.root / "skills" / "znve"
        (self.folder / "references").mkdir(parents=True)
        (self.folder / "SKILL.md").write_text("generado", encoding="utf-8")

    def tearDown(self):
        self._patch.stop()
        self._tmp.cleanup()

    def test_stray_files_are_orphans_but_caches_are_not(self):
        (self.folder / "notas.txt").write_text("suelto", encoding="utf-8")
        (self.folder / "references" / "viejo.md").write_text("suelto", encoding="utf-8")
        (self.folder / ".DS_Store").write_text("", encoding="utf-8")
        (self.folder / "__pycache__").mkdir()
        (self.folder / "__pycache__" / "x.pyc").write_text("", encoding="utf-8")
        rendered = {"skills/znve/SKILL.md": "generado"}
        self.assertEqual(
            builder.bundle_orphans(self.BUNDLE, rendered), ["skills/znve/notas.txt", "skills/znve/references/viejo.md"]
        )
        self.assertEqual(sorted(builder.bundle_members(self.BUNDLE, rendered)), ["znve/SKILL.md"], "un huérfano no entra en el zip")

    def test_include_declares_a_manual_member(self):
        (self.folder / "scripts").mkdir()
        (self.folder / "scripts" / "helper.py").write_text("print()", encoding="utf-8")
        rendered = {"skills/znve/SKILL.md": "generado"}
        bundle = {**self.BUNDLE, "include": ["scripts/helper.py"]}
        self.assertEqual(builder.bundle_orphans(bundle, rendered), [])
        self.assertEqual(sorted(builder.bundle_members(bundle, rendered)), ["znve/SKILL.md", "znve/scripts/helper.py"])

    def test_missing_include_is_an_error(self):
        bundle = {**self.BUNDLE, "include": ["no-existe.py"]}
        with self.assertRaises(builder.SpecError):
            builder.bundle_members(bundle, {})

    def test_build_refuses_orphans(self):
        (self.folder / "notas.txt").write_text("suelto", encoding="utf-8")
        spec = {"bundles": [self.BUNDLE]}
        with mock.patch.object(builder, "render_targets", return_value={"skills/znve/SKILL.md": "generado"}):
            with self.assertRaisesRegex(builder.SpecError, "notas.txt"):
                builder.build(spec, verify_only=True)


class VersionReferenceTests(unittest.TestCase):
    """La heurística de versiones ignora identificadores como ZNVE_OR_ERROR y detecta las citas reales."""

    def test_detects_real_citations(self):
        for text in (
            "ZNVE v2.3.0",
            "Zero-Noise Vibe Engineering (ZNVE) v2.3.0",
            "Norma ZNVE 2.3.0",
            "directiva global ZNVE v2.3.0 (resumen)",
        ):
            self.assertEqual(ZNVE_VERSION_REF.findall(text), ["2.3.0"], text)

    def test_ignores_identifiers_followed_by_other_versions(self):
        for text in (
            "[ZNVE_OR_ERROR] 429: el SDK de MCP 1.32.0",
            "ZNVE_MCP_ERROR con el SDK 1.32.0",
            "ZNVE_WORKSPACE apunta a node 22.1.0",
        ):
            self.assertEqual(ZNVE_VERSION_REF.findall(text), [], text)


class SdkExampleTests(unittest.TestCase):
    """El ejemplo del SDK de Antigravity (no se puede importar sin el SDK) es válido y no filtra el entorno."""

    SOURCE = (REPO / "integrations" / "mcp-server" / "antigravity_sdk_example.py").read_text(encoding="utf-8")

    def test_is_valid_python(self):
        ast.parse(self.SOURCE)

    def test_passes_a_minimal_explicit_environment(self):
        self.assertIn("ZNVE_WORKSPACE", self.SOURCE)
        self.assertIn('"PATH"', self.SOURCE, "el servidor necesita PATH si el SDK sustituye el entorno")
        self.assertNotIn("**os.environ", self.SOURCE)
        self.assertNotIn("dict(os.environ", self.SOURCE)
        self.assertNotRegex(self.SOURCE, r"env=os\.environ")


class CiWorkflowTests(unittest.TestCase):
    """Cadena de suministro del CI: acciones fijadas a un commit y permisos mínimos."""

    WORKFLOWS = sorted((REPO / ".github" / "workflows").glob("*.yml"))

    def test_workflows_exist(self):
        self.assertTrue(self.WORKFLOWS)

    def test_actions_are_pinned_to_a_commit_sha(self):
        for workflow in self.WORKFLOWS:
            for number, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), 1):
                match = re.search(r"uses:\s*(\S+)", line)
                if not match or match.group(1).startswith("./"):
                    continue
                self.assertRegex(
                    match.group(1), r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$", f"{workflow.name}:{number} no está fijada a un SHA"
                )

    def test_workflows_default_to_read_only_token(self):
        for workflow in self.WORKFLOWS:
            self.assertRegex(workflow.read_text(encoding="utf-8"), r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", workflow.name)


def stale_hand_maintained(spec: dict) -> list[str]:
    """Archivos no generados que citan una versión de ZNVE distinta de la especificación."""
    generated = {t["output"] for t in spec["targets"]} | {b["output"] for b in spec["bundles"]}
    stale = []
    for path in sorted(REPO.rglob("*")):
        rel = path.relative_to(REPO).as_posix()
        if not path.is_file() or rel in generated or HAND_MAINTAINED_SKIP & set(path.parts):
            continue
        if path.suffix.lower() not in {".md", ".py", ".ts", ".json", ".html", ".mjs", ".ps1"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            stale.append(f"{rel} (no es UTF-8)")
            continue
        versions = set(ZNVE_VERSION_REF.findall(text)) - {spec["version"]}
        if versions:
            stale.append(f"{rel} (cita {', '.join(sorted(versions))})")
    return stale


def main() -> int:
    print("[*] Arnés de verificación ZNVE", flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

    spec = builder.load_spec()
    stale = stale_hand_maintained(spec)
    if stale:
        print(f"\n[aviso] {len(stale)} archivos mantenidos a mano citan otra versión de ZNVE (no bloquea):")
        for item in stale:
            print(f"    - {item}")

    if not result.wasSuccessful():
        print("\n[fail] La certificación ZNVE falló.")
        return 1
    print(f"\n[ok] Certificación ZNVE v{spec['version']} completada: paridad total entre plataformas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
