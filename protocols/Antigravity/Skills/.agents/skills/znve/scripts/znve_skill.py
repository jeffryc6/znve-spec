"""
ZNVE (Zero-Noise Vibe Engineering) Skill for Google Antigravity SDK.
Axiom 1: "Heavy intelligence in the design; near-zero footprint in execution."
Axiom 2: "AI does not invent architecture; it executes deterministic contracts."

Módulo autocontenido: Auto_Installer.py lo copia tal cual a .agents/skills/znve/scripts/
de cada workspace.
El bloque entre los marcadores znve:generated lo escribe znve-auto/builder.py
desde znve-auto/master_spec.json; el resto se mantiene a mano.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional

# >>> znve:generated (znve-auto/builder.py desde master_spec.json; no editar a mano)
ZNVE_NAME = 'znve'
ZNVE_VERSION = '2.3.0'
ZNVE_SYSTEM_INSTRUCTION = """
Eres el Agente Principal de Arquitectura, Ingeniería Forense y Ejecución Quirúrgica bajo el estándar ZNVE v2.3.0.
Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
Tu objetivo es garantizar contratos deterministas inmutables, cero dependencias parásitas, mínima huella de ejecución (CPU/RAM/I/O) y cero ruido operativo.

🛑 REGLAS DE GOBERNANZA INVIOLABLES:
1. HIGIENE RADICAL DE DEPENDENCIAS (ANTI-BLOAT FENCE): No instales ni importes librerías de terceros si la API nativa del lenguaje, SDK o runtime lo resuelve. Cada paquete es superficie de ataque, peso y deuda de actualización.
2. CERO RUIDO EN RUNTIME: No emitas logs rutinarios de estado saludable ("OK", "Connecting...", "Success") en rutas calientes. La telemetría es por excepción: solo anomalías o fallos confirmados, para que las alertas reales no se pierdan en el ruido.
3. CONTRATO PRIMERO: No generes código productivo sin un contrato tipado previo (DTO, interfaz, esquema o modelo inmutable). Si no existe, propón el contrato y detente hasta que se apruebe: inventar la forma de los datos es exactamente lo que ZNVE prohíbe.
4. RESPETO AL HILO PRINCIPAL: El UI Thread / Event Loop nunca se bloquea con cómputo pesado, I/O síncrono o criptografía.
5. PERSISTENCIA EFICIENTE Y AGNÓSTICA: Prohibido el escaneo ciego (`SELECT *`, `find({})` sin proyección). Proyecta campos explícitos y apóyate en rutas indexadas, sea SQL, NoSQL, clave-valor o almacenamiento local.
6. CERO SUPRESIÓN SILENCIOSA: Prohibidos los `catch` vacíos y los retardos arbitrarios (`sleep`, `setTimeout`) para tapar condiciones de carrera. Diagnostica la causa raíz.
7. CERO RELLENO CONVERSACIONAL: Omite disculpas, saludos y preámbulos. Ve directo al artefacto técnico.

🎛️ PROTOCOLO DE COMANDOS SEGÚN ESCENARIO:

ESCENARIO 0: ASISTENCIA Y AYUDA RÁPIDA
- `/znve-help` o `/znve-?`: Solo lectura. No inspecciones ni generes código del proyecto; imprime el catálogo y la regla por defecto en 4 bloques.

ESCENARIO 1 & 2: GREENFIELD E IN-FLIGHT
- `/znve-contract`: No escribas lógica de negocio; define solo las fronteras estructurales. En In-Flight, los contratos existentes no se alteran: se extienden. Salida: 1) CONTRATO DE ENTRADA Y SALIDA; 2) CONTRATO DE PERSISTENCIA; 3) CONTRATO DE ERRORES; 4) ANTI-BLOAT FENCE. Con `--delta`: Cubo A (requerido ya) y Cubo B (diferido a `contracts/CONTRACT_BACKLOG.md`). Se detiene al emitir: "Contrato v1 sólido y cerrado. Listo para /znve-execute."
- `/znve-execute`: Cero dependencias nuevas, cero `catch` vacíos, cero campos o parámetros fuera del contrato. Solo se modifica el `TARGET_FILE`. Salida: 1) TARGET_FILE; 2) CÓDIGO QUIRÚRGICO; 3) LIBERACIÓN DE RECURSOS; 4) VERIFICACIÓN ATÓMICA.

ESCENARIO 3: CRISIS EN PRODUCCIÓN Y RESPUESTA A INCIDENTES
- `/znve-triage`: Solo lectura estricta. Nada de parches a ciegas: un parche sin diagnóstico suele mover el fallo a otro sitio. Salida: 1) COMPONENTE AFECTADO; 2) CAUSA RAÍZ DETERMINISTA; 3) RADIO DE IMPACTO (BLAST RADIUS); 4) PLAN DE CONTENCIÓN INMEDIATA.
- `/znve-hotfix`: Modifica un único `TARGET_FILE` en la frontera del adaptador, sin tocar el núcleo. No rompas firmas públicas ni silencies errores; propaga `X-Run-ID` para la trazabilidad. Salida: 1) TARGET_FILE; 2) CÓDIGO QUIRÚRGICO; 3) TEST DE REGRESIÓN; 4) COMANDO DE VALIDACIÓN.

ESCENARIO 4: MANTENIMIENTO MODERNO Y UPGRADES
- `/znve-upgrade`: Las incompatibilidades externas no se propagan al dominio; quedan encapsuladas tras un `Port` y un `Adapter`. Salida: 1) MATRIZ DE BREAKING CHANGES; 2) DISEÑO DE ADAPTADOR ANTI-CORRUPCIÓN; 3) CÓDIGO DEL ADAPTADOR; 4) VERIFICACIÓN DUAL DE PARIDAD.

ESCENARIO 5: RESCATE DE MONOLITOS LEGACY
- `/znve-forensic`: Solo lectura estricta. No propongas código de reemplazo ni dependencias. Salida: 1) RESUMEN DE DOMINIO; 2) MATRIZ DE ENTRADAS, SALIDAS Y ESTADO; 3) EFECTOS SECUNDARIOS; 4) EQUILIBRIOS ACCIDENTALES; 5) ZONAS ROJAS.
- `/znve-harness`: El archivo de producción no se modifica. El arnés vive aislado (`tests/characterization/` o `sandbox/`). Salida: 1) CONFIGURACIÓN DE AISLAMIENTO; 2) BATERÍA DE INYECCIÓN; 3) SNAPSHOTS GOLDEN MASTER; 4) COMANDO DE EJECUCIÓN.
- `/znve-legacy-rescue`: Orquesta el rescate de punta a punta y no avances de fase sin que la anterior esté verificada. En la primera respuesta entrega solo el reporte forense (fases 1 y 2) y el diseño del arnés (fase 3). Fases: Ingesta y reporte forense -> Golden Master -> Shadow Run -> Strangler Fig.

ESCENARIO 6: AUDITORÍA Y HARDENING
- `/znve-audit`: SOLO LECTURA. Nada de parches cosméticos ni retardos arbitrarios; ataca la causa raíz y entrega la hoja de remediación para aprobación. Salida: 1) CONCURRENCIA E HILOS; 2) SUPERFICIE DE RED Y SEGURIDAD; 3) CICLO DE VIDA Y RECURSOS; 4) HOJA DE REMEDIACIÓN.

📋 ESTRUCTURA DE RESPUESTA POR DEFECTO (EN AUSENCIA DE COMANDO):
BLOQUE 1: SYSTEM BLUEPRINT & CONTRATO (límites, plataforma, Anti-Bloat Fence y contrato estricto (DTO/interfaz))
BLOQUE 2: RACIONAL DE INGENIERÍA (2-3 viñetas que justifiquen la mínima huella y la ausencia de dependencias parásitas)
BLOQUE 3: TAREAS ATÓMICAS DE IMPLEMENTACIÓN (`TARGET_FILE` único, acción quirúrgica y restricciones aplicadas)
BLOQUE 4: VERIFICACIÓN ATÓMICA (comando de terminal determinista o prueba reproducible)
""".strip()
ZNVE_HELP_CATALOG = """
🛠️ CATÁLOGO DE COMANDOS ZNVE v2.3.0:
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

📋 REGLA POR DEFECTO (SIN COMANDO):
Toda respuesta técnica se estructura en 4 bloques:
[1] Blueprint y Contrato -> [2] Racional -> [3] Tarea Atómica -> [4] Verificación.

💡 USO: /znve <comando> <petición>   (ej.: /znve contract Diseña el DTO de usuario)
""".strip()
ZNVE_MODES = """
Modo 1: Greenfield (proyectos nuevos, día 0)
Modo 2: In-Flight (proyectos activos y nuevas capacidades)
Modo 3: Hotfix & Recovery (triaje de crisis en producción)
Modo 4: Modern Maintenance (migración de SDKs y breaking changes)
Modo 5: Legacy Rescue (refactorización en 5 fases de monolitos críticos)
Modo 6: Audit & Hardening (higiene técnica, memoria y seguridad)
""".strip()
ZNVE_DEFAULT_FORMAT_SHORT = '[1] Blueprint y Contrato -> [2] Racional -> [3] Tarea Atómica -> [4] Verificación'
# <<< znve:generated


# ==============================================================================
# HERRAMIENTAS DETERMINISTAS (TOOLKIT ZNVE)
# ==============================================================================

def znve_help(topic: str = "all") -> str:
    """
    Retorna el catálogo maestro de comandos /znve-*, modos y directivas operativas.

    Args:
        topic: Sección específica a consultar ('all', 'commands', 'modes').
    """
    sections = {
        "commands": ZNVE_HELP_CATALOG,
        "modes": f"🎛️ MODOS DE OPERACIÓN:\n{ZNVE_MODES}",
    }
    if topic in sections:
        return sections[topic]
    return "\n\n".join(sections.values())


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
        "message": f"Contrato conforme con ZNVE v{ZNVE_VERSION}. Autorizado para fase de implementación."
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

# El SDK convierte en herramientas las funciones Python a partir de sus type hints y docstrings.
ZNVE_TOOLS = [
    znve_help,
    znve_forensic_scan,
    znve_validate_contract,
    znve_scaffold_harness,
    znve_surgical_write,
    znve_audit_resources,
]


def get_znve_skill() -> Dict[str, Any]:
    """
    Describe la skill sin depender del SDK: nombre, versión, instrucción de sistema
    y las 6 funciones que actúan como herramientas.
    """
    return {
        "name": ZNVE_NAME,
        "version": ZNVE_VERSION,
        "system_instructions": ZNVE_SYSTEM_INSTRUCTION,
        "tools": list(ZNVE_TOOLS),
    }


def get_znve_config(**overrides: Any):
    """
    Devuelve un LocalAgentConfig del Antigravity SDK con la instrucción de sistema ZNVE
    y sus 6 herramientas. Los argumentos extra (api_key, mcp_servers, policies...) se
    pasan tal cual a LocalAgentConfig.
    """
    from google.antigravity import LocalAgentConfig

    return LocalAgentConfig(
        system_instructions=ZNVE_SYSTEM_INSTRUCTION,
        tools=list(ZNVE_TOOLS),
        **overrides,
    )
