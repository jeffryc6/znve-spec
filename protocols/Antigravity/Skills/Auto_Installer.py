#!/usr/bin/env python3
"""
==============================================================================
ZNVE SKILL AUTO-INSTALLER FOR ANTIGRAVITY (Python Stdlib Only)
Axiom: "Heavy intelligence in the design; near-zero footprint in execution."
==============================================================================
"""

import sys
import os
import shutil
import json
from pathlib import Path

# Código canónico del Skill para generar el artefacto autónomamente
SKILL_SOURCE = '''"""
ZNVE (Zero-Noise Vibe Engineering) Skill for Google Antigravity SDK.
Generated automatically by ZNVE Auto-Installer.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

ZNVE_SYSTEM_INSTRUCTION = """
Eres el Agente Principal de Arquitectura, Ingeniería Forense y Ejecución Quirúrgica bajo el estándar ZNVE v2.2.0.
Tu objetivo es garantizar contratos deterministas inmutables, cero dependencias parásitas, mínima huella de ejecución (CPU/RAM/I/O) y cero ruido operativo.

🛑 REGLAS DE GOBERNANZA INVIOLABLES:
1. HIGIENE DE DEPENDENCIAS (Anti-Bloat Fence): Prohibido usar o sugerir librerías de terceros si la biblioteca estándar o API nativa resuelve el problema.
2. SILENCIO EN RUNTIME: Prohibido emitir logs informativos rutinarios ("OK", "Connecting...", "Success"). La telemetría se reserva exclusivamente para anomalías.
3. CONTRATO PRIMERO: Prohibido generar código productivo sin antes validar un contrato tipado (DTO, esquema, interfaz).
4. RESPETO AL HILO PRINCIPAL: El hilo principal (UI Thread / Event Loop) nunca debe bloquearse con I/O síncrono, cómputo masivo o criptografía.
5. PERSISTENCIA EFICIENTE: Prohibido el escaneo ciego (SELECT *, find({}) sin proyecciones). Las lecturas deben proyectar campos explícitos e indexados.
6. LIBERACIÓN DETERMINISTA: Todo recurso abierto debe cerrarse explícitamente (dispose, close, finally).

📋 ESTRUCTURA DE RESPUESTA POR DEFECTO:
BLOQUE 1: SYSTEM BLUEPRINT (Límites, entorno y contrato estricto DTO/interfaz)
BLOQUE 2: RACIONAL DE INGENIERÍA (Justificación de mínima huella y cero paquetes externos)
BLOQUE 3: TAREAS ATÓMICAS (Ruta TARGET_FILE, acción quirúrgica y restricciones)
BLOQUE 4: VERIFICACIÓN ATÓMICA (Comando de terminal determinista o test reproducible)
"""

def znve_help(topic: str = "all") -> str:
    return """
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
""".strip()

def znve_forensic_scan(file_path: str) -> Dict[str, Any]:
    target = Path(file_path)
    if not target.exists() or not target.is_file():
        return {"status": "ERROR", "message": f"El archivo '{file_path}' no existe."}
    content = target.read_text(encoding="utf-8", errors="replace")
    return {
        "status": "SUCCESS",
        "file": str(target),
        "total_lines": len(content.splitlines()),
        "side_effects": {
            "has_io": bool(re.search(r"\\b(open|read|write|fs|file)\\b", content, re.I)),
            "has_net": bool(re.search(r"\\b(fetch|http|socket|urllib|curl)\\b", content, re.I)),
            "has_db": bool(re.search(r"\\b(select|insert|update|delete|find)\\b", content, re.I))
        },
        "read_only": True
    }

def znve_validate_contract(contract_code: str, banned_libraries: Optional[List[str]] = None) -> Dict[str, Any]:
    violations = []
    banned = banned_libraries or ["lodash", "axios", "moment", "requests", "jquery"]
    for lib in banned:
        if re.search(rf"\\b(import|require|using|from)\\s+['\\\"].*{re.escape(lib)}.*['\\\"]", contract_code):
            violations.append(f"Anti-Bloat: Librería externa prohibida '{lib}'.")
    if re.search(r"SELECT\\s+\\*\\s+FROM", contract_code, re.I):
        violations.append("Prohibida consulta ciega 'SELECT *'.")
    return {"status": "APPROVED" if not violations else "REJECTED", "passed": not violations, "violations": violations}

def znve_surgical_write(target_file: str, code_content: str, disposal_pattern: str) -> Dict[str, Any]:
    if re.search(r"except\\s*:\\s*(?:pass|\\.\\.\\.)|catch\\s*\\([^)]*\\)\\s*\\{\\s*\\}", code_content):
        return {"status": "REJECTED", "message": "Prohibido silenciar excepciones con bloques vacíos."}
    dest = Path(target_file)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(code_content, encoding="utf-8")
    return {"status": "SUCCESS", "target_file": str(dest), "disposal": disposal_pattern}

def znve_audit_resources(code_snippet: str) -> Dict[str, Any]:
    findings = []
    if re.search(r"(\\bWakeLock\\.acquire|Thread\\.sleep|time\\.sleep|\\.Result|\\.Wait\\(\\))", code_snippet):
        findings.append("Posible bloqueo de hilos o contención de batería.")
    return {"status": "AUDIT_COMPLETE", "clean": len(findings) == 0, "findings": findings}

def get_znve_skill():
    try:
        from google.antigravity import Skill, Tool  # type: ignore
        return Skill(
            name="zero_noise_vibe_engineering",
            description="ZNVE v2.2.0 deterministic architectural governance.",
            system_instruction=ZNVE_SYSTEM_INSTRUCTION,
            tools=[
                Tool.from_callable(znve_help),
                Tool.from_callable(znve_forensic_scan),
                Tool.from_callable(znve_validate_contract),
                Tool.from_callable(znve_surgical_write),
                Tool.from_callable(znve_audit_resources)
            ]
        )
    except ImportError:
        return {
            "name": "zero_noise_vibe_engineering",
            "system_instruction": ZNVE_SYSTEM_INSTRUCTION,
            "tools": [znve_help, znve_forensic_scan, znve_validate_contract, znve_surgical_write, znve_audit_resources]
        }
'''


def run_installer():
    print("[*] Iniciando Auto-Instalador de Skill ZNVE para Google Antigravity...")
    
    # 1. Definir rutas objetivo
    workspace_root = Path.cwd()
    target_skill_dir = workspace_root / ".antigravity" / "skills" / "znve"
    config_file = workspace_root / ".antigravity" / "antigravity.json"
    
    print(f"[*] Directorio de instalación: {target_skill_dir}")
    target_skill_dir.mkdir(parents=True, exist_ok=True)

    # 2. Desplegar znve_skill.py
    skill_file = target_skill_dir / "znve_skill.py"
    skill_file.write_text(SKILL_SOURCE.strip(), encoding="utf-8")
    print(f"[+] Archivo de skill generado: {skill_file.relative_to(workspace_root)}")

    # 3. Crear __init__.py para facilitar importación modular
    init_file = target_skill_dir / "__init__.py"
    init_file.write_text("from .znve_skill import get_znve_skill\n", encoding="utf-8")
    print(f"[+] Archivo de módulo generado: {init_file.relative_to(workspace_root)}")

    # 4. Actualizar o crear configuración de Antigravity
    config_data = {}
    if config_file.exists():
        try:
            config_data = json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            config_data = {}

    if "skills" not in config_data:
        config_data["skills"] = {}

    config_data["skills"]["zero_noise_vibe_engineering"] = {
        "enabled": True,
        "entrypoint": ".antigravity.skills.znve.znve_skill:get_znve_skill",
        "protocol_version": "2.2.0",
        "strict_mode": True
    }

    config_file.write_text(json.dumps(config_data, indent=2), encoding="utf-8")
    print(f"[+] Configuración actualizada en: {config_file.relative_to(workspace_root)}")

    # 5. Verificación de entorno de ejecución
    try:
        import google.antigravity
        print("[✓] SDK de Google Antigravity detectado en el entorno de Python.")
    except ImportError:
        print("[!] Nota: 'google-antigravity' no está en el entorno local activo.")
        print("    Para completar la integración, ejecuta: pip install google-antigravity")

    print("\n[✓] Instalación completada con éxito. Skill ZNVE listo para producción.")
    print("    Comando de prueba sugerido al agente: '/znve-help'")


if __name__ == "__main__":
    run_installer()