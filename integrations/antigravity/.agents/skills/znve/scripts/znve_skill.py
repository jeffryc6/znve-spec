"""
ZNVE (Zero-Noise Vibe Engineering) Skill for Google Antigravity SDK.
Axiom 1: "Heavy intelligence in the design; near-zero footprint in execution."
Axiom 2: "AI does not invent architecture; it executes deterministic contracts."

Módulo autocontenido: Auto_Installer.py lo copia tal cual a .agents/skills/znve/scripts/
de cada workspace.
El bloque entre los marcadores znve:generated lo escribe znve-auto/builder.py
desde znve-auto/master_spec.json; el resto se mantiene a mano.
"""

import os
import re
import shutil
import tempfile
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
8. VERIFICACIÓN INVIOLABLE: No modifiques tests, snapshots ni la configuración de pruebas existentes para obtener verde. Si un test parece incorrecto, repórtalo y detente hasta que el humano lo apruebe. No declares un resultado que no ejecutaste: entrega el comando y, solo si lo ejecutaste, su salida real.

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
- `/znve-legacy-rescue`: Orquesta el rescate de punta a punta y no avances de fase sin que la anterior esté verificada. En la primera respuesta entrega solo el reporte forense (fases 1 y 2) y el diseño del arnés (fase 3). Fases: Ingesta pasiva -> Reporte forense -> Golden Master -> Shadow Run -> Strangler Fig.

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
# CONTENCIÓN DE RUTAS
# ==============================================================================

# Únicos directorios (primer segmento bajo el workspace) donde znve_scaffold_harness puede escribir.
HARNESS_ROOTS = ("tests", "sandbox")


def _workspace_root() -> Path:
    """Raíz contra la que se resuelven las rutas: ZNVE_WORKSPACE o, si no está definida, el cwd."""
    return Path(os.environ.get("ZNVE_WORKSPACE") or os.getcwd()).resolve()


def _is_inside(root: Path, target: Path) -> bool:
    return target == root or root in target.parents


def _resolve_in_workspace(raw: str) -> Path:
    """Ruta dentro del workspace; ValueError si escapa, también a través de enlaces o junctions."""
    root = _workspace_root()
    candidate = Path(os.path.abspath(root / raw))
    if not _is_inside(root, candidate) or not _is_inside(root, candidate.resolve()):
        raise ValueError(f"'{raw}' queda fuera de ZNVE_WORKSPACE.")
    return candidate


def _rejected(message: str) -> Dict[str, Any]:
    return {"status": "REJECTED", "message": message}


# Directorios en los que ninguna herramienta escribe, a cualquier profundidad.
PROTECTED_DIRS = (".git", "node_modules")
MAX_SCAN_BYTES = 1024 * 1024


def _write_denied(destination: Path) -> Optional[str]:
    """Motivo de rechazo si la ruta (pedida o real) cae dentro de un directorio protegido."""
    root = _workspace_root()
    for path in (destination, destination.resolve()):
        blocked = next((p for p in path.relative_to(root).parts if p.lower() in PROTECTED_DIRS), None)
        if blocked:
            return f"Escritura denegada dentro de '{blocked}/': '{destination.relative_to(root)}'."
    return None


def _atomic_create(destination: Path, content: str) -> None:
    """Como _atomic_write, pero solo crea: FileExistsError si el destino existe (también un enlace)."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".znve-tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        os.link(temp, destination)
    finally:
        Path(temp).unlink(missing_ok=True)


def _atomic_write(destination: Path, content: str) -> None:
    """Temporal en el mismo directorio + os.replace: el archivo nunca queda a medio escribir."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".znve-tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        if destination.exists():
            shutil.copymode(destination, temp)
        os.replace(temp, destination)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


# ==============================================================================
# DETECTORES (misma semántica que integrations/mcp-server/znve-mcp-server.ts)
# ==============================================================================

# catch vacío o con solo comentarios (con o sin binding) y .catch(() => {}) de promesas.
_SILENT_CATCH = (
    re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{(?:\s|//[^\n]*|/\*[\s\S]*?\*/)*\}"),
    re.compile(r"\.catch\(\s*(?:\(\s*\w*\s*\)|\w+)\s*=>\s*\{(?:\s|//[^\n]*|/\*[\s\S]*?\*/)*\}\s*\)"),
)
_EXCEPT = re.compile(r"^([ \t]*)except\b[^:]*:(.*)$")
_BLIND_QUERY = (re.compile(r"\bselect\s+\*", re.IGNORECASE), re.compile(r"\.find\(\s*\{\s*\}\s*\)"))
_BLOCKING_TASK = re.compile(r"\.Result\b(?!\s*\()|\.Wait\s*\(|\.GetAwaiter\(\)\s*\.GetResult\(\)")
_WAKELOCK = re.compile(r"wakelock\w*\.acquire\s*\(", re.IGNORECASE)
_BUSY_WAIT = re.compile(r"\bThread\.sleep\b|while\s*\(\s*true\s*\)\s*\{\s*\}|while\s+True\s*:\s*pass\b")
_DB_MUTATION = re.compile(
    r"\b(?:INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|MERGE\s+INTO|DROP\s+TABLE|TRUNCATE\s+TABLE)\b"
    r"|\.(?:insert|update|delete|replace)(?:One|Many)\s*\(|\.bulkWrite\s*\(",
    re.IGNORECASE,
)


def _silent_error_blocks(code: str) -> int:
    """Número de catch/except que solo descartan el error."""
    count = sum(len(pattern.findall(code)) for pattern in _SILENT_CATCH)
    lines = code.splitlines()
    for i, line in enumerate(lines):
        match = _EXCEPT.match(line)
        if not match:
            continue
        inline = re.sub(r"#.*$", "", match.group(2)).strip()
        body = [inline] if inline else []
        for following in ([] if inline else lines[i + 1:]):
            statement = re.sub(r"#.*$", "", following)
            if not statement.strip():
                continue
            if len(following) - len(following.lstrip()) <= len(match.group(1)):
                break
            body.append(statement.strip())
        if body and all(s in ("pass", "...") for s in body):
            count += 1
    return count


def _imports_library(code: str, lib: str) -> bool:
    """True si el código importa la librería (JS/TS, Python, C#). Coincidencia por módulo, no por substring."""
    name = re.escape(lib)
    sub = r"(?:[/.][\w.\-/]*)?"
    patterns = (
        rf"\bimport\s+(?:[^'\";]*?\bfrom\s*)?['\"]{name}{sub}['\"]",
        rf"\b(?:require|import)\s*\(\s*['\"]{name}{sub}['\"]\s*\)",
        rf"^\s*import\s+{name}(?:\.[\w.]*)?\s*(?:[,;]|\bas\b|$)",
        rf"^\s*from\s+{name}(?:\.[\w.]*)?\s+import\b",
        rf"^\s*using\s+(?:static\s+)?{name}(?:\.[\w.]*)?\s*;",
    )
    return any(re.search(p, code, re.IGNORECASE | re.MULTILINE) for p in patterns)


def _busy_waits(code: str) -> bool:
    return bool(_BUSY_WAIT.search(code)) or (
        bool(re.search(r"\bsetTimeout\b", code)) and bool(re.search(r"\bwhile\b", code))
    )


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
    Inspección estricta de solo lectura (Zero-Touch) de un archivo de texto para extraer
    sus efectos secundarios y zonas rojas sin alterar el disco. Rechaza directorios,
    binarios y archivos de más de 1 MiB.

    Args:
        file_path: Ruta del archivo, relativa a ZNVE_WORKSPACE (o al cwd) o absoluta dentro de él.
    """
    try:
        target = _resolve_in_workspace(file_path)
    except ValueError as exc:
        return _rejected(str(exc))
    if not target.exists():
        return {"status": "ERROR", "message": f"No existe '{file_path}' en ZNVE_WORKSPACE."}
    if not target.is_file():
        return _rejected(f"'{file_path}' no es un archivo.")
    size = target.stat().st_size
    if size > MAX_SCAN_BYTES:
        return _rejected(f"'{file_path}' pesa {size} bytes y supera el tope de {MAX_SCAN_BYTES} bytes.")

    try:
        raw = target.read_bytes()
    except OSError as exc:
        return {"status": "ERROR", "message": f"Fallo de lectura: {exc}"}
    if b"\x00" in raw:
        return _rejected(f"'{file_path}' es binario; znve_forensic_scan solo lee texto.")
    content = raw.decode("utf-8", errors="replace")

    # Detección determinista de efectos secundarios
    has_fs = bool(re.search(r"\b(open|readFile|writeFile|fs\.|std::fs|Path\.)", content))
    has_net = bool(re.search(r"\b(fetch|http|socket|requests|urllib|curl)", content, re.IGNORECASE))
    has_db = bool(_DB_MUTATION.search(content))

    # Detección de zonas rojas operativas
    empty_catches = _silent_error_blocks(content)
    blocking_calls = len(_BLOCKING_TASK.findall(content)) + len(re.findall(r"\b(?:Thread|time)\.sleep\b", content))

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
        if _imports_library(contract_code, lib):
            violations.append(f"Anti-Bloat Fence: Librería externa prohibida '{lib}' detectada.")

    if _BLIND_QUERY[0].search(contract_code):
        violations.append("Cláusula 2.4: Prohibida la consulta ciega 'SELECT *'. Debe proyectar campos específicos.")

    if _BLIND_QUERY[1].search(contract_code):
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
        harness_directory: Directorio de aislamiento bajo 'tests/' o 'sandbox/' en la raíz del workspace.
        test_filename: Nombre del archivo de pruebas, sin rutas.
        harness_code: Código del test de caja negra.
    """
    if test_filename != Path(test_filename).name or re.search(r"[\\/:]|^\.+$", test_filename):
        return _rejected(f"'test_filename' debe ser un nombre de archivo sin rutas: '{test_filename}'.")
    try:
        target_path = _resolve_in_workspace(os.path.join(harness_directory, test_filename))
    except ValueError as exc:
        return _rejected(str(exc))

    # Se comprueba la ruta escrita y la real: un enlace dentro de tests/ tampoco puede salir de tests/.
    root = _workspace_root()
    for path in (target_path, target_path.resolve()):
        parts = path.relative_to(root).parts
        if len(parts) < 2 or parts[0].lower() not in HARNESS_ROOTS:
            return _rejected(
                "El arnés debe residir bajo 'tests/' o 'sandbox/' en la raíz de ZNVE_WORKSPACE."
            )
    denied = _write_denied(target_path)
    if denied:
        return _rejected(denied)

    try:
        _atomic_create(target_path, harness_code)
    except FileExistsError:
        return _rejected(
            f"'{target_path.name}' ya existe: el arnés solo crea archivos, nunca sobrescribe tests ni snapshots."
        )

    return {
        "status": "SUCCESS",
        "harness_file": str(target_path),
        "message": "Arnés Golden Master generado en aislamiento. El código de producción permanece intacto."
    }


def znve_surgical_write(target_file: str, code_content: str, disposal_pattern: str) -> Dict[str, Any]:
    """
    Escribe el cambio en disco de forma atómica sobre un único TARGET_FILE, verificando
    previamente que ningún catch/except silencie errores y la política de liberación de recursos.
    Rechaza rutas fuera de ZNVE_WORKSPACE o dentro de .git/ y node_modules/.

    Args:
        target_file: Ruta exacta del único archivo modificado, dentro de ZNVE_WORKSPACE (o del cwd).
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
    if _silent_error_blocks(code_content):
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

    try:
        destination = _resolve_in_workspace(target_file)
    except ValueError as exc:
        return _rejected(str(exc))
    denied = _write_denied(destination)
    if denied:
        return _rejected(denied)
    _atomic_write(destination, code_content)

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

    if _BLOCKING_TASK.search(code_snippet):
        findings.append("Alerta Concurrencia: Bloqueo sincrónico del despachador de interfaz detectado (.Result / .Wait()).")

    if _WAKELOCK.search(code_snippet):
        findings.append("Alerta Batería: WakeLock detectado sin liberación asegurada.")

    if _busy_waits(code_snippet):
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
