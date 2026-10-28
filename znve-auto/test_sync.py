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
    "integrations/codex/skills/znve/SKILL.md",
)
# Plugin de Codex/ChatGPT (formato portable) y marketplace del repositorio que lo publica.
CODEX_PLUGIN = "integrations/codex/plugin.json"
CODEX_MARKETPLACE = ".agents/plugins/marketplace.json"
ANTIGRAVITY_DIR = REPO / "integrations" / "antigravity"
# Grok solo admite frontmatter plano: una línea `clave: valor` por campo, sin YAML anidado.
GROK_SKILL = "integrations/grok/skills/znve/SKILL.md"
GROK_KEYS = {"name", "description", "license", "version", "author", "source"}
# field-tests conserva datos archivados (directivas y transcripciones de versiones anteriores): no se actualizan.
HAND_MAINTAINED_SKIP = {".git", "node_modules", "dist", "znve-auto", "field-tests"}
# Presupuestos en bytes (RFC 0002 §3, medidos; Verificación Inviolable sube de 400 a 700 B al absorber la regla anti-simulacro): un guardrail es una línea del prefijo de cada petición.
GUARDRAIL_MAX_BYTES = {"Cerca de Contexto (Context Fence)": 700, "Verificación Inviolable": 700}
# Regla común de fases más el perfil del asistente. La RFC proponía 900 B; la regla sola ya pesa más de 600 B.
AGENT_BLOCK_MAX_BYTES = 1400
# Descripciones de las herramientas MCP: viajan en el prefijo de cada petición (línea base v2.3.0: unos 2 KiB).
MCP_TOOL_DOCS_MAX_BYTES = 4200
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

    def test_directives_fit_the_render_budget(self):
        """Ninguna directiva generada supera el presupuesto de render de DeepSeek Harness (65.536 bytes)."""
        for output, text in self.rendered.items():
            if output.endswith(".html"):
                continue  # la página web no es una directiva
            size = len(text.encode("utf-8"))
            self.assertLessEqual(size, 65536, f"{output} pesa {size} B")

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

    def test_codex_plugin_and_marketplace(self):
        """El plugin de Codex lleva la versión de la especificación y el marketplace apunta a su carpeta con la skill."""
        plugin = json.loads(self.rendered[CODEX_PLUGIN])
        self.assertEqual(plugin["name"], self.spec["name"])
        self.assertRegex(plugin["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertEqual(plugin["version"], self.spec["version"])
        self.assertNotIn("(", plugin["license"], "la licencia del manifiesto debe ser una expresión SPDX")
        market = json.loads(self.rendered[CODEX_MARKETPLACE])
        entry = next(p for p in market["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(entry["source"]["source"], "local")
        root = entry["source"]["path"]
        self.assertTrue(root.startswith("./"), root)
        self.assertEqual(f"{root[2:]}/plugin.json", CODEX_PLUGIN)
        self.assertIn(f"{root[2:]}/skills/{plugin['name']}/SKILL.md", self.rendered)

    def test_codex_openai_yaml_is_flat(self):
        """agents/openai.yaml solo usa las secciones documentadas y comillas en cada valor de texto."""
        text = self.rendered["integrations/codex/skills/znve/agents/openai.yaml"]
        sections = re.findall(r"(?m)^([a-z_]+):\s*$", text)
        self.assertLessEqual(set(sections), {"interface", "policy", "dependencies"})
        for line in re.findall(r"(?m)^  (?:display_name|short_description|default_prompt): (.*)$", text):
            self.assertRegex(line, r'^"[^"\\]*"$')

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
