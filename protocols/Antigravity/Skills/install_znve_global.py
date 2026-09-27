#!/usr/bin/env python3
"""
==============================================================================
ZNVE GLOBAL AUTO-INSTALLER FOR GOOGLE ANTIGRAVITY IDE
Instala el Skill, el Workflow (/znve-help) y las Reglas Globales de Gemini
en el perfil del sistema para que funcionen en CUALQUIER proyecto.
==============================================================================
"""

import os
import sys
from pathlib import Path

# 1. Contenido del Skill según la especificación de Antigravity IDE
ANTIGRAVITY_SKILL_MD = """---
name: zero-noise-vibe-engineering
description: Metodología y gobernanza ZNVE v2.2.0. Aplica arquitectura contract-first, cero dependencias parásitas, arneses Golden Master para legacy, auditoría de recursos y generación quirúrgica. Úsalo ante /znve-* o al diseñar arquitecturas y resolver incidencias.
---

# Zero-Noise Vibe Engineering (ZNVE) Skill

Actúas bajo los principios de Zero-Noise Vibe Engineering v2.2.0:
- **Axioma 1:** Inteligencia pesada en el diseño; huella casi nula en la ejecución.
- **Axioma 2:** La IA no inventa arquitectura; ejecuta contratos deterministas.

## Guardrails Inviolables:
1. **Anti-Bloat Fence:** Prohibido agregar paquetes externos si la API nativa o biblioteca estándar lo resuelve.
2. **Silencio en Runtime:** Prohibidos logs informativos rutinarios ("OK", "Connecting"). Solo alertar anomalías.
3. **Contrato Primero:** Prohibido generar código sin contratos tipados previos (DTOs, esquemas, interfaces).
4. **Respeto al Hilo de UI:** Prohibido bloquear el hilo principal con cómputo síncrono, I/O o criptografía.
5. **Persistencia Eficiente:** Prohibido el escaneo ciego (`SELECT *`, `find({})` sin proyecciones explícitas).
6. **Cero Excepciones Silenciadas:** Prohibidos los bloques `try/catch` vacíos.

## Comandos ZNVE Disponibles:
- `/znve-help`: Manual operativo e índice de comandos.
- `/znve-contract`: Definición tipada de entradas, salidas, persistencia y límites.
- `/znve-execute`: Implementación atómica en `TARGET_FILE` con desecho de recursos.
- `/znve-triage`: Diagnóstico de causa raíz y radio de impacto (solo lectura).
- `/znve-hotfix`: Parche quirúrgico atómico con test de regresión obligatorio.
- `/znve-upgrade`: Migración mediante Adaptador desacoplado anti-corrupción.
- `/znve-forensic`: Inspección en solo lectura (Zero-Touch), matriz I/O y efectos secundarios.
- `/znve-harness`: Suite Golden Master de caja negra sobre código intacto.
- `/znve-legacy-rescue`: Orquestación integral en 5 fases para código legacy.
- `/znve-audit`: Hardening de hilos, memoria, descriptores y seguridad.
"""

# 2. Contenido del Workflow global para registrar el slash command nativo
ANTIGRAVITY_WORKFLOW_MD = """---
description: Muestra el catálogo maestro de comandos y modos de operación de ZNVE.
---

Imprime de inmediato el siguiente manual de referencia operativa en formato exacto:

🛠️ CATÁLOGO DE COMANDOS ZNVE:
• /znve-help         : Manual operativo e índice de comandos.
• /znve-contract     : Diseño de interfaces inmutables, DTOs y Anti-Bloat Fence.
• /znve-execute      : Implementación atómica en TARGET_FILE con desecho de recursos.
• /znve-triage       : Diagnóstico y contención de radio de impacto ante caídas.
• /znve-hotfix       : Parche quirúrgico atómico con test de regresión obligatorio.
• /znve-upgrade      : Migración de dependencias mediante Adaptador desacoplado.
• /znve-forensic     : Ingesta en solo lectura, matriz I/O y efectos secundarios.
• /znve-harness      : Suite Golden Master de caja negra sobre código intacto.
• /znve-legacy-rescue: Orquestación integral en 5 fases para código legacy.
• /znve-audit        : Hardening de hilos, memoria, descriptores y seguridad.

📋 ESTRUCTURA DE RESPUESTA POR DEFECTO (EN AUSENCIA DE COMANDO):
BLOQUE 1: SYSTEM BLUEPRINT (Límites, entorno y contrato estricto DTO/interfaz)
BLOQUE 2: RACIONAL DE INGENIERÍA (Mínima huella de memoria/CPU, cero dependencias parásitas)
BLOQUE 3: TAREAS ATÓMICAS (Ruta TARGET_FILE, acción quirúrgica y restricciones)
BLOQUE 4: VERIFICACIÓN ATÓMICA (Comando terminal determinista o test reproducible)
"""

# 3. Directiva base global (GEMINI.md)
GLOBAL_RULE_MD = """
# DIRECTIVA GLOBAL ZNVE v2.2.0 (Zero-Noise Vibe Engineering)
Cuando el usuario mencione comandos `/znve-*` o solicite arquitectura y código:
1. Aplica arquitectura Contract-First (DTOs, proyecciones explícitas, cero dependencias innecesarias).
2. Protege el hilo principal y asegura la liberación determinista de recursos (`close`, `dispose`, `finally`).
3. Responde en 4 bloques cerrados si no se especifica un comando: [1] Blueprint -> [2] Racional -> [3] Implementación Atómica -> [4] Verificación.
"""

def install():
    home = Path.home()
    
    # Rutas globales de Antigravity y Gemini
    global_skills_dir = home / ".gemini" / "antigravity" / "skills" / "znve"
    global_workflows_dir = home / ".gemini" / "config" / "global_workflows"
    global_gemini_rule = home / ".gemini" / "GEMINI.md"

    print("[*] Configurando Antigravity IDE de forma global...")

    # A. Crear Skill Global
    global_skills_dir.mkdir(parents=True, exist_ok=True)
    skill_file = global_skills_dir / "SKILL.md"
    skill_file.write_text(ANTIGRAVITY_SKILL_MD.strip(), encoding="utf-8")
    print(f"[✓] Global Skill instalado en: {skill_file}")

    # B. Crear Workflow Global (/znve-help)
    global_workflows_dir.mkdir(parents=True, exist_ok=True)
    workflow_file = global_workflows_dir / "znve-help.md"
    workflow_file.write_text(ANTIGRAVITY_WORKFLOW_MD.strip(), encoding="utf-8")
    print(f"[✓] Global Slash Command (/znve-help) instalado en: {workflow_file}")

    # C. Registrar o actualizar Regla Global (GEMINI.md)
    global_gemini_rule.parent.mkdir(parents=True, exist_ok=True)
    current_rule = ""
    if global_gemini_rule.exists():
        current_rule = global_gemini_rule.read_text(encoding="utf-8")
    
    if "ZNVE v2.2.0" not in current_rule:
        with open(global_gemini_rule, "a", encoding="utf-8") as f:
            f.write("\n" + GLOBAL_RULE_MD.strip() + "\n")
        print(f"[✓] Regla ZNVE añadida a: {global_gemini_rule}")
    else:
        print(f"[i] Regla ZNVE ya existente en: {global_gemini_rule}")

    print("\n[+] ¡Instalación global completada exitosamente!")
    print("[*] Instrucciones para verificar:")
    print("    1. Reinicia o recarga la ventana de Antigravity IDE.")
    print("    2. Abre cualquier proyecto nuevo.")
    print("    3. En el chat, escribe: /skills (deberás ver 'zero-noise-vibe-engineering').")
    print("    4. Escribe: /znve-help (aparecerá reconocido en la lista de comandos).")

if __name__ == "__main__":
    install()