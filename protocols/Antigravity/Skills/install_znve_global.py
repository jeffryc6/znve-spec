#!/usr/bin/env python3
"""
==============================================================================
ZNVE GLOBAL AUTO-INSTALLER FOR GOOGLE ANTIGRAVITY IDE
Instala el Skill, el Workflow (/znve-help) y las Reglas Globales de Gemini
en el perfil del sistema para que funcionen en CUALQUIER proyecto.
==============================================================================

El contenido sale de dos archivos generados por znve-auto/builder.py:
- SKILL.md (skill de Antigravity), junto a este script.
- znve_skill.py (versión, catálogo de /znve-help y formato por defecto).
"""

import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
SKILL_MD = SKILL_DIR / "SKILL.md"

sys.path.insert(0, str(SKILL_DIR))
from znve_skill import ZNVE_DEFAULT_FORMAT_SHORT, ZNVE_HELP_CATALOG, ZNVE_NAME, ZNVE_VERSION  # noqa: E402

RULE_START = "<!-- znve:start -->"
RULE_END = "<!-- znve:end -->"
# Bloque que añadían las versiones anteriores del instalador, sin marcadores.
LEGACY_RULE = re.compile(r"^# DIRECTIVA GLOBAL ZNVE v[\d.]+[^\n]*\n(?:(?:Cuando |\d\. )[^\n]*\n?)*", re.M)
MANAGED_RULE = re.compile(re.escape(RULE_START) + r".*?" + re.escape(RULE_END) + r"\n?", re.S)

# Workflow global que registra el slash command /znve-help
WORKFLOW_MD = f"""---
description: Muestra el catálogo maestro de comandos y modos de operación de ZNVE v{ZNVE_VERSION}.
---

Imprime de inmediato el siguiente manual de referencia operativa en formato exacto:

{ZNVE_HELP_CATALOG}
"""

# Directiva base global (GEMINI.md)
GLOBAL_RULE_MD = f"""{RULE_START}
# DIRECTIVA GLOBAL ZNVE v{ZNVE_VERSION} (Zero-Noise Vibe Engineering)
Cuando el usuario mencione comandos `/znve-*` o solicite arquitectura y código:
1. Aplica arquitectura Contract-First (DTOs, proyecciones explícitas, cero dependencias innecesarias).
2. Protege el hilo principal y asegura la liberación determinista de recursos (`close`, `dispose`, `finally`).
3. Responde en 4 bloques cerrados si no se especifica un comando: {ZNVE_DEFAULT_FORMAT_SHORT}.
{RULE_END}
"""


def upsert_rule(current: str) -> str:
    """Sustituye el bloque ZNVE existente (con o sin marcadores) o lo añade al final."""
    if MANAGED_RULE.search(current):
        return MANAGED_RULE.sub(lambda _: GLOBAL_RULE_MD, current, count=1)
    if LEGACY_RULE.search(current):
        return LEGACY_RULE.sub(lambda _: GLOBAL_RULE_MD, current, count=1)
    separator = "" if not current or current.endswith("\n") else "\n"
    return f"{current}{separator}\n{GLOBAL_RULE_MD}"


def install():
    if not SKILL_MD.exists():
        raise SystemExit(f"[!] Falta {SKILL_MD}. Genera los artefactos con: python znve-auto/builder.py")

    home = Path.home()
    global_skills_dir = home / ".gemini" / "antigravity" / "skills" / "znve"
    global_workflows_dir = home / ".gemini" / "config" / "global_workflows"
    global_gemini_rule = home / ".gemini" / "GEMINI.md"

    print(f"[*] Configurando Antigravity IDE de forma global (ZNVE v{ZNVE_VERSION})...")

    # A. Skill global
    global_skills_dir.mkdir(parents=True, exist_ok=True)
    skill_file = global_skills_dir / "SKILL.md"
    skill_file.write_text(SKILL_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[ok] Skill global instalada en: {skill_file}")

    # B. Workflow global (/znve-help)
    global_workflows_dir.mkdir(parents=True, exist_ok=True)
    workflow_file = global_workflows_dir / "znve-help.md"
    workflow_file.write_text(WORKFLOW_MD, encoding="utf-8")
    print(f"[ok] Slash command global (/znve-help) instalado en: {workflow_file}")

    # C. Regla global (GEMINI.md): se sustituye el bloque ZNVE, nunca se duplica
    global_gemini_rule.parent.mkdir(parents=True, exist_ok=True)
    current_rule = global_gemini_rule.read_text(encoding="utf-8") if global_gemini_rule.exists() else ""
    updated_rule = upsert_rule(current_rule)
    if updated_rule != current_rule:
        global_gemini_rule.write_text(updated_rule, encoding="utf-8")
        print(f"[ok] Regla ZNVE v{ZNVE_VERSION} escrita en: {global_gemini_rule}")
    else:
        print(f"[i] La regla ZNVE v{ZNVE_VERSION} ya estaba al día en: {global_gemini_rule}")

    print("\n[ok] Instalación global completada.")
    print("[*] Para verificar:")
    print("    1. Reinicia o recarga la ventana de Antigravity IDE.")
    print("    2. Abre cualquier proyecto.")
    print(f"    3. En el chat, escribe /skills: deberás ver '{ZNVE_NAME}'.")
    print("    4. Escribe /znve-help: aparecerá en la lista de comandos.")


if __name__ == "__main__":
    install()
