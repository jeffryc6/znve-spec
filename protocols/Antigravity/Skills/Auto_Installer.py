#!/usr/bin/env python3
"""
==============================================================================
ZNVE SKILL AUTO-INSTALLER FOR ANTIGRAVITY (Python Stdlib Only)
Axiom: "Heavy intelligence in the design; near-zero footprint in execution."
==============================================================================

Instala la skill ZNVE en el workspace actual (.antigravity/skills/znve/) copiando
el módulo canónico znve_skill.py que está junto a este script. La versión y el
catálogo salen de ese módulo, que genera znve-auto/builder.py.

Uso (desde la raíz del proyecto donde se quiere instalar):
    python <ruta>/znve-spec/protocols/Antigravity/Skills/Auto_Installer.py
"""

import json
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
CANONICAL_SKILL = SKILL_DIR / "znve_skill.py"

sys.path.insert(0, str(SKILL_DIR))
from znve_skill import ZNVE_NAME, ZNVE_VERSION  # noqa: E402

# Clave con la que versiones anteriores registraban la skill en antigravity.json.
LEGACY_CONFIG_KEYS = ("zero_noise_vibe_engineering",)


def load_config(config_file: Path) -> dict:
    if not config_file.exists():
        return {}
    try:
        return json.loads(config_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"[!] {config_file} no es JSON válido ({exc}). Corrígelo o muévelo antes de instalar; no se sobrescribe."
        ) from exc


def run_installer():
    print(f"[*] Instalando la skill ZNVE v{ZNVE_VERSION} para Google Antigravity...")

    # 1. Rutas objetivo
    workspace_root = Path.cwd()
    target_skill_dir = workspace_root / ".antigravity" / "skills" / "znve"
    config_file = workspace_root / ".antigravity" / "antigravity.json"
    target_skill_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copiar el módulo canónico
    skill_file = target_skill_dir / "znve_skill.py"
    shutil.copyfile(CANONICAL_SKILL, skill_file)
    print(f"[+] Skill copiada: {skill_file.relative_to(workspace_root)}")

    # 3. __init__.py para la importación modular
    init_file = target_skill_dir / "__init__.py"
    init_file.write_text("from .znve_skill import get_znve_skill\n", encoding="utf-8")
    print(f"[+] Módulo: {init_file.relative_to(workspace_root)}")

    # 4. Registrar la skill (y retirar la clave antigua si existe)
    config_data = load_config(config_file)
    skills = config_data.setdefault("skills", {})
    for legacy in LEGACY_CONFIG_KEYS:
        if skills.pop(legacy, None) is not None:
            print(f"[+] Registro antiguo '{legacy}' sustituido por '{ZNVE_NAME}'.")
    skills[ZNVE_NAME] = {
        "enabled": True,
        "entrypoint": ".antigravity.skills.znve.znve_skill:get_znve_skill",
        "protocol_version": ZNVE_VERSION,
        "strict_mode": True,
    }
    config_file.write_text(json.dumps(config_data, indent=2) + "\n", encoding="utf-8")
    print(f"[+] Configuración: {config_file.relative_to(workspace_root)}")

    # 5. Comprobar el SDK
    try:
        import google.antigravity  # noqa: F401
        print("[ok] SDK de Google Antigravity detectado.")
    except ImportError:
        print("[!] 'google-antigravity' no está instalado en este entorno. Ejecuta: pip install google-antigravity")

    print(f"\n[ok] Skill ZNVE v{ZNVE_VERSION} instalada. Prueba con '/znve-help'.")


if __name__ == "__main__":
    run_installer()
