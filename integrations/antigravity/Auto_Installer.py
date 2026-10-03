#!/usr/bin/env python3
"""
==============================================================================
ZNVE SKILL AUTO-INSTALLER FOR ANTIGRAVITY (Python Stdlib Only)
Axiom: "Heavy intelligence in the design; near-zero footprint in execution."
==============================================================================

Instala la skill ZNVE en el workspace actual, en la ruta que lee Antigravity:

    .agents/skills/znve/SKILL.md                 <-- skill del IDE / Antigravity 2.0 / CLI
    .agents/skills/znve/scripts/znve_skill.py    <-- módulo para el Antigravity SDK

Ambos archivos se copian desde esta carpeta (los genera znve-auto/builder.py).
También retira la instalación antigua en .antigravity/ si existe.

Uso (desde la raíz del proyecto donde se quiere instalar):
    python <ruta>/znve-spec/integrations/antigravity/Auto_Installer.py
"""

import json
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
CANONICAL_SKILL_MD = SKILL_DIR / "SKILL.md"
CANONICAL_MODULE = SKILL_DIR / "znve_skill.py"

sys.path.insert(0, str(SKILL_DIR))
from znve_skill import ZNVE_NAME, ZNVE_VERSION  # noqa: E402

# Claves con las que versiones anteriores registraban la skill en .antigravity/antigravity.json.
LEGACY_CONFIG_KEYS = ("zero_noise_vibe_engineering", ZNVE_NAME)


def remove_legacy_install(workspace_root: Path) -> None:
    """Retira .antigravity/skills/znve/ y su registro; conserva lo que no sea de ZNVE."""
    legacy_root = workspace_root / ".antigravity"
    legacy_dir = legacy_root / "skills" / "znve"
    if legacy_dir.is_dir():
        shutil.rmtree(legacy_dir)
        print(f"[+] Instalación antigua eliminada: {legacy_dir.relative_to(workspace_root)}")

    config_file = legacy_root / "antigravity.json"
    if not config_file.exists():
        return
    try:
        config_data = json.loads(config_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[!] {config_file.relative_to(workspace_root)} no es JSON válido ({exc}); se deja intacto.")
        return
    skills = config_data.get("skills", {})
    removed = [key for key in LEGACY_CONFIG_KEYS if skills.pop(key, None) is not None]
    if not removed:
        return
    if not skills:
        config_data.pop("skills", None)
    if config_data:
        config_file.write_text(json.dumps(config_data, indent=2) + "\n", encoding="utf-8")
    else:
        config_file.unlink()
    print(f"[+] Registro antiguo retirado de {config_file.relative_to(workspace_root)}: {', '.join(removed)}")

    for folder in (legacy_root / "skills", legacy_root):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()


def run_installer(workspace_root: Path | None = None) -> Path:
    workspace_root = (workspace_root or Path.cwd()).resolve()
    print(f"[*] Instalando la skill ZNVE v{ZNVE_VERSION} en {workspace_root}...")

    if not CANONICAL_SKILL_MD.exists():
        raise SystemExit(f"[!] Falta {CANONICAL_SKILL_MD}. Genera los artefactos con: python znve-auto/builder.py")

    # 1. Skill que lee Antigravity
    target_dir = workspace_root / ".agents" / "skills" / ZNVE_NAME
    (target_dir / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CANONICAL_SKILL_MD, target_dir / "SKILL.md")
    print(f"[+] Skill: {(target_dir / 'SKILL.md').relative_to(workspace_root)}")

    # 2. Módulo para el SDK (instrucción de sistema + 6 herramientas)
    shutil.copyfile(CANONICAL_MODULE, target_dir / "scripts" / "znve_skill.py")
    print(f"[+] Módulo SDK: {(target_dir / 'scripts' / 'znve_skill.py').relative_to(workspace_root)}")

    # 3. Migración desde .antigravity/
    remove_legacy_install(workspace_root)

    # 4. Comprobar el SDK (opcional: solo hace falta para agentes programáticos)
    try:
        import google.antigravity  # noqa: F401
        print("[ok] SDK de Google Antigravity detectado.")
    except ImportError:
        print("[i] 'google-antigravity' no está instalado. Solo lo necesitas para el SDK: pip install google-antigravity")

    print(f"\n[ok] Skill ZNVE v{ZNVE_VERSION} instalada. Recarga Antigravity y prueba con '/znve-help'.")
    return target_dir


if __name__ == "__main__":
    run_installer()
