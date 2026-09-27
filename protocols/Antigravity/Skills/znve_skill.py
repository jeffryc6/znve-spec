"""
ZNVE (Zero-Noise Vibe Engineering) Skill for Google Antigravity SDK.
Axiom 1: "Heavy intelligence in the design; near-zero footprint in execution."
Axiom 2: "AI does not invent architecture; it executes deterministic contracts."
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# System instructions inyectadas al agente Antigravity
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

📋 ESTRUCTURA DE RESPUESTA POR DEFECTO (EN AUSENCIA DE COMANDO):
BLOQUE 1: SYSTEM BLUEPRINT (Límites, entorno y contrato estricto DTO/interfaz)
BLOQUE 2: RACIONAL DE INGENIERÍA (Justificación de mínima huella y cero paquetes externos)
BLOQUE 3: TAREAS ATÓMICAS (Ruta TARGET_FILE, acción quirúrgica y restricciones)
BLOQUE 4: VERIFICACIÓN ATÓMICA (Comando de terminal determinista o test reproducible)
"""


# ==============================================================================
# HERRAMIENTAS DETERMINISTAS (TOOLKIT ZNVE)
# ==============================================================================

def znve_help(topic: str = "all") -> str:
    """
    Retorna el catálogo maestro de comandos /znve-*, modos y directivas operativas.
    
    Args:
        topic: Sección específica a consultar ('all', 'commands', 'modes').
    """
    commands_guide = """
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

🎛️ MODOS DE OPERACIÓN:
Modo 1: Greenfield (Proyectos nuevos) | Modo 2: In-Flight (Expansión activa)
Modo 3: Hotfix & Recovery (Crisis)    | Modo 4: Modern Upgrade (Breaking changes)
Modo 5: Legacy Rescue (Golden Master) | Modo 6: Audit & Hardening (Recursos)
"""
    return commands_guide.strip()


def znve_forensic_scan(file_path: str) -> Dict[str, Any]:
    """
    Inspección estricta de solo lectura (Zero-Touch) de un archivo para extraer
    su grafo de dependencias, efectos secundarios y zonas rojas sin alterar el disco.
    
    Args:
        file_path: Ruta relativa o absoluta del archivo a inspeccionar.
    """
    target = Path(file_path)
    if not target.exists() or not target.is_file():
        return {
            "status": "ERROR",
            "message": f"El archivo '{file_path}' no existe o no es accesible."
        }

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {"status": "ERROR", "message": f"Fallo de lectura: {str(exc)}"}

    # Detección determinista de efectos secundarios
    has_fs = bool(re.search(r"\b(open|readFile|writeFile|fs\.|std::fs|Path\.)", content))
    has_net = bool(re.search(r"\b(fetch|http|socket|requests|urllib|curl)", content, re.IGNORECASE))
    has_db = bool(re.search(r"\b(SELECT|INSERT|UPDATE|DELETE|find|aggregate|db\.)", content, re.IGNORECASE))
    
    # Detección de zonas rojas operativas
    empty_catches = len(re.findall(r"except\s*:\s*(?:pass|\.\.\.)|catch\s*\([^)]*\)\s*\{\s*\}", content))
    blocking_calls = len(re.findall(r"(\.Result|\.Wait\(\)|Thread\.sleep|time\.sleep)", content))

    return {
        "status": "SUCCESS",
        "file": str(target),
        "total_lines": len(content.splitlines()),
        "side_effects": {
            "file_system_io": has_fs,
            "network_calls": has_net,
            "database_mutations": has_db
        },
        "red_zones_detected": {
            "empty_catch_blocks": empty_catches,
            "thread_blocking_calls": blocking_calls
        },
        "read_only_confirmation": True
    }


def znve_validate_contract(contract_code: str, banned_libraries: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Valida un contrato de interfaz o DTO garantizando que no contenga código especulativo,
    consultas ciegas (SELECT *, find({}) sin proyecciones) ni paquetes vetados.
    
    Args:
        contract_code: Definición tipada del DTO o interfaz.
        banned_libraries: Lista de librerías vetadas por el Anti-Bloat Fence.
    """
    violations = []
    banned = banned_libraries or ["lodash", "axios", "moment", "requests", "jquery"]

    for lib in banned:
        if re.search(rf"\b(import|require|using|from)\s+['\"].*{re.escape(lib)}.*['\"]", contract_code):
            violations.append(f"Anti-Bloat Fence: Librería externa prohibida '{lib}' detectada.")

    if re.search(r"SELECT\s+\*\s+FROM", contract_code, re.IGNORECASE):
        violations.append("Cláusula 2.4: Prohibida la consulta ciega 'SELECT *'. Debe proyectar campos específicos.")

    if re.search(r"\.find\(\s*\{\s*\}\s*\)", contract_code):
        violations.append("Cláusula 2.4: Prohibido 'find({})' sin proyección ni filtros indexados.")

    if violations:
        return {
            "status": "REJECTED",
            "passed": False,
            "violations": violations
        }

    return {
        "status": "APPROVED",
        "passed": True,
        "message": "Contrato conforme con ZNVE v2.2.0. Autorizado para fase de implementación."
    }


def znve_scaffold_harness(harness_directory: str, test_filename: str, harness_code: str) -> Dict[str, Any]:
    """
    Crea un arnés de caracterización Golden Master en un directorio aislado
    asegurando que el código original de producción no sea modificado.
    
    Args:
        harness_directory: Directorio de aislamiento (debe contener 'test', 'tests' o 'sandbox').
        test_filename: Nombre del archivo de pruebas.
        harness_code: Código del test de caja negra.
    """
    normalized_dir = harness_directory.lower().replace("\\", "/")
    if not any(token in normalized_dir for token in ["test", "tests", "sandbox", "characterization"]):
        return {
            "status": "REJECTED",
            "message": "El arnés debe residir obligatoriamente en un directorio de aislamiento ('tests/', 'characterization/' o 'sandbox/')."
        }

    target_dir = Path(harness_directory)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / test_filename

    target_path.write_text(harness_code, encoding="utf-8")

    return {
        "status": "SUCCESS",
        "harness_file": str(target_path),
        "message": "Arnés Golden Master generado en aislamiento. El código de producción permanece intacto."
    }


def znve_surgical_write(target_file: str, code_content: str, disposal_pattern: str) -> Dict[str, Any]:
    """
    Escribe el cambio en disco de forma atómica sobre un único TARGET_FILE, verificando
    previamente la ausencia de bloques catch vacíos y la política de liberación de recursos.
    
    Args:
        target_file: Ruta exacta del único archivo modificado.
        code_content: Código fuente que satisface el contrato aprobado.
        disposal_pattern: Mecanismo de desecho ('dispose', 'close', 'finally', 'autocloseable', 'not_applicable').
    """
    valid_disposals = {"dispose", "close", "finally", "autocloseable", "not_applicable"}
    if disposal_pattern.lower() not in valid_disposals:
        return {
            "status": "REJECTED",
            "message": f"Patrón de desecho inválido. Opciones válidas: {list(valid_disposals)}"
        }

    # Prohibición de enmascaramiento de excepciones
    if re.search(r"except\s*:\s*(?:pass|\.\.\.)|catch\s*\([^)]*\)\s*\{\s*\}", code_content):
        return {
            "status": "REJECTED",
            "message": "Cláusula 2.5: Prohibido escribir bloques catch/except vacíos que enmascaren fallos de fondo."
        }

    # Verificación de liberación si se manejan recursos de I/O
    handles_resources = bool(re.search(r"\b(open|socket|connect|createReadStream|HttpClient)\b", code_content))
    if handles_resources and disposal_pattern.lower() == "not_applicable":
        return {
            "status": "REJECTED",
            "message": "Cláusula 2.3: Se detectó apertura de recursos I/O pero el disposal_pattern fue declarado como 'not_applicable'."
        }

    destination = Path(target_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(code_content, encoding="utf-8")

    return {
        "status": "SUCCESS",
        "file": str(destination),
        "bytes_written": len(code_content.encode("utf-8")),
        "message": f"Escritura quirúrgica ejecutada exitosamente en '{target_file}' con patrón '{disposal_pattern}'."
    }


def znve_audit_resources(code_snippet: str) -> Dict[str, Any]:
    """
    Analizador estático de patrones lesivos para concurrencia, memoria y CPU.
    
    Args:
        code_snippet: Fragmento de código a evaluar.
    """
    findings = []

    if re.search(r"(\.Result|\.GetAwaiter\(\)\.GetResult\(\)|\.Wait\(\))", code_snippet):
        findings.append("Alerta Concurrencia: Bloqueo sincrónico del despachador de interfaz detectado (.Result / .Wait()).")

    if re.search(r"\bWakeLock\.acquire\b", code_snippet):
        findings.append("Alerta Batería: WakeLock detectado sin liberación asegurada.")

    if re.search(r"while\s*\(\s*true\s*\)\s*\{\s*\}|while\s+True:\s+pass", code_snippet):
        findings.append("Alerta CPU: Bucle infinito sin jitter ni tiempo de reposo (busy-waiting).")

    return {
        "status": "AUDIT_COMPLETE",
        "clean": len(findings) == 0,
        "findings": findings
    }


# ==============================================================================
# INTEGRACIÓN CON ANTIGRAVITY SDK
# ==============================================================================

def get_znve_skill():
    """
    Empaqueta el skill y las herramientas para ser registradas en un Agente Antigravity.
    Compatible con google.antigravity.types y Skill definitions del SDK.
    """
    try:
        # Intentar importación nativa del SDK de Antigravity si está instalado
        from google.antigravity import Skill, Tool  # type: ignore

        tools = [
            Tool.from_callable(znve_help),
            Tool.from_callable(znve_forensic_scan),
            Tool.from_callable(znve_validate_contract),
            Tool.from_callable(znve_scaffold_harness),
            Tool.from_surgical(znve_surgical_write) if hasattr(Tool, "from_surgical") else Tool.from_callable(znve_surgical_write),
            Tool.from_callable(znve_audit_resources),
        ]

        return Skill(
            name="zero_noise_vibe_engineering",
            description="Aplica el protocolo ZNVE v2.2.0 para arquitectura basada en contratos, rescate legacy, auditoría de recursos y generación quirúrgica.",
            system_instruction=ZNVE_SYSTEM_INSTRUCTION,
            tools=tools
        )
    except (ImportError, AttributeError):
        # Modo compatible desacoplado (Diccionario canónico si el SDK aún no se importa)
        return {
            "name": "zero_noise_vibe_engineering",
            "system_instruction": ZNVE_SYSTEM_INSTRUCTION,
            "tools": [
                znve_help,
                znve_forensic_scan,
                znve_validate_contract,
                znve_scaffold_harness,
                znve_surgical_write,
                znve_audit_resources
            ]
        }