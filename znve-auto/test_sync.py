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

import contextlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import builder  # noqa: E402

REPO = builder.REPO_ROOT
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
ZNVE_VERSION_REF = re.compile(r"ZNVE[^\n\d]{0,40}?v?(\d+\.\d+\.\d+)")
SKILL_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
MCP_SERVER = REPO / "protocols" / "mcp" / "znve-mcp-server.ts"
OPENROUTER_SCHEMA = REPO / "protocols" / "agents" / "openrouter" / "response-schema.json"
SKILL_FILES = (
    "protocols/agents/claude/skills/znve/SKILL.md",
    "protocols/agents/gemini/skills/znve/SKILL.md",
)
ANTIGRAVITY_DIR = REPO / "protocols" / "Antigravity" / "Skills"
HAND_MAINTAINED_SKIP = {".git", "node_modules", "dist", "znve-auto"}


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

    def test_single_version(self):
        """Ningún artefacto generado cita una versión de ZNVE distinta de la especificación."""
        version = self.spec["version"]
        for rel, text in self.rendered.items():
            found = set(ZNVE_VERSION_REF.findall(text))
            self.assertLessEqual(found, {version}, f"{rel} cita {found - {version}}")

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


class ExternalContractTests(unittest.TestCase):
    """Contratos que viven fuera de las plantillas pero dependen de la especificación."""

    @classmethod
    def setUpClass(cls):
        cls.spec = builder.load_spec()
        cls.server = MCP_SERVER.read_text(encoding="utf-8")

    def test_mcp_tools_match_server(self):
        """Las herramientas MCP documentadas son las que expone el servidor."""
        exposed = set(re.findall(r'name:\s*"(znve_\w+)"', self.server))
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
        self.assertEqual(self.skill.znve_help("commands"), builder.help_block(self.spec))
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
            if rel.startswith("protocols/Antigravity/") and not rel.endswith(".md"):
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


def stale_hand_maintained(spec: dict) -> list[str]:
    """Archivos no generados que citan una versión de ZNVE distinta de la especificación."""
    generated = {t["output"] for t in spec["targets"]} | {b["output"] for b in spec["bundles"]}
    stale = []
    for path in sorted(REPO.rglob("*")):
        rel = path.relative_to(REPO).as_posix()
        if not path.is_file() or rel in generated or HAND_MAINTAINED_SKIP & set(path.parts):
            continue
        if path.suffix.lower() not in {".md", ".py", ".ts", ".json", ".html", ".mjs"}:
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
