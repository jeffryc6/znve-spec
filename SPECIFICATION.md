# SPECIFICATION.md: Zero-Noise Vibe Engineering (ZNVE)
**Norma Técnica Universal y Gobernanza Agéntica v2.3.0**
*Status: Standard | Classification: Spec-Driven Agentic Software Architecture*

---

## 1. PREÁMBULO Y FUNDAMENTOS FILOSÓFICOS

Zero-Noise Vibe Engineering (ZNVE) es una norma técnica y metaprotocolo de arquitectura de software diseñado para transformar la programación asistida por Inteligencia Artificial (LLMs, agentes autónomos y asistentes de IDE) en una disciplina quirúrgica, determinista y de alta precisión.

ZNVE resuelve estructuralmente el "bucle de degradación agéntica" (*AI agentic drift*) y la acumulación de deuda técnica derivados de la generación no restringida de código.

### 1.1 Axiomas Inmutables
1. **Axioma 1 (Diseño Pesado, Ejecución Silenciosa):** *Inteligencia concentrada en la fase de diseño y contrato; huella física y computacional mínima en la ejecución.*
2. **Axioma 2 (Ejecución de Contratos Deterministas):** *La IA no inventa arquitectura ni improvisa tipos; ejecuta contratos estrictos y preaprobados.*

### 1.2 Roles
* **Director de Arquitectura (humano):** delimita el perímetro, aprueba contratos y certifica la paridad.
* **Ejecutor Táctico (IA):** produce sintaxis determinista que satisface el contrato, sin cambios estructurales no autorizados.

---

## 2. LOS 5 PILARES DE ZNVE

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          LOS 5 PILARES DE ZNVE                           │
├───────────────┬───────────────┬───────────────┬───────────────┬──────────┤
│ 1. CERO RUIDO │ 2. CONTRATOS  │ 3. EFICIENCIA │ 4. ESTADO     │ 5. SEG.  │
│    (ANTI-     │    PRIMERO    │   ASIMÉTRICA  │    AGNÓSTICO  │ DEFENSIVA│
│    BLOAT)     │ (CONTRACT-1st)│ (LOW-FOOTPRINT│ (PROYECCIONES)│ & FORENS.│
└───────────────┴───────────────┴───────────────┴───────────────┴──────────┘
```

### Pilar 1: Cero Ruido (Zero-Noise Operations & Anti-Bloat Fence)
* Prohibición absoluta de librerías de terceros no esenciales o parásitas.
* Prohibida la emisión de logs rutinarios de confirmación en entornos de producción. La telemetría opera por excepción.

### Pilar 2: Contratos Primero (Contract-First AI)
* Antes de escribir una sola línea de lógica de negocio, se debe definir el contrato inmutable en la carpeta `contracts/` (DTOs, Zod, Pydantic v2 o JSON Schema).
* Poda de Contexto (*Context Boundary Pruning*): los agentes de IA reciben únicamente el contrato activo y el archivo objetivo (`TARGET_FILE`).

### Pilar 3: Eficiencia Asimétrica y Respeto a Recursos
* Consumo mínimo de CPU y RAM. Liberación determinista de recursos (`close`, `dispose`, `finally`, `unbinding`).
* Garantía de hilos no bloqueantes (I/O asíncrono obligatorio).

### Pilar 4: Dominio de Estado Agnóstico
* Consultas y mutaciones de estado estrictamente proyectadas.
* Prohibidas las consultas ciegas o escaneos masivos en memoria.

### Pilar 5: Seguridad Defensiva y Diagnóstico Forense
* Validación y sanitización estricta en fronteras de entrada.
* Prohibidos los bloques `try/catch` vacíos o el silenciamiento de excepciones. Trazabilidad con `X-Run-ID`.

### 2.6 Guardrails operativos
Las directivas de los asistentes traducen los 5 pilares en 7 guardrails que el agente aplica en cada respuesta:

| # | Guardrail | Pilar |
|---|---|---|
| 1 | Higiene radical de dependencias (Anti-Bloat Fence) | 1 |
| 2 | Cero ruido en runtime | 1 |
| 3 | Contrato primero | 2 |
| 4 | Respeto al hilo principal | 3 |
| 5 | Persistencia eficiente y agnóstica | 4 |
| 6 | Cero supresión silenciosa | 5 |
| 7 | Cero relleno conversacional | 1 |

---

## 3. FLUJO DE CONTRATOS Y CONTROL ANTI-BUCLE

### 3.1 Análisis Tecnológico por Plataforma (`--platform`)
Al activar `/znve-contract`, la IA evalúa el tipo de aplicación y sugiere el stack con cero peso parásito:

* **Escritorio (Windows / macOS / Linux), `desktop`:** Rust + Tauri v2 o WinUI 3 nativo | Persistencia: SQLite (WAL mode) / DuckDB.
* **macOS Nativo, `desktop`:** Swift 6 + SwiftUI | Persistencia: SwiftData.
* **Web-App, `web`:** Vite + TypeScript / Next.js App Router | Persistencia: IndexedDB nativo (Dexie.js solo como excepción justificada).
* **Híbrida (Mobile / Desktop), `hybrid`:** Tauri Mobile / Flutter / React Native Bare | Persistencia: almacenamiento nativo de la plataforma (MMKV o WatermelonDB solo como excepción justificada).
* **Android Nativo, `mobile`:** Kotlin + Jetpack Compose + Corrutinas | Persistencia: Room DB.
* **iOS / iPadOS Nativo, `mobile`:** Swift 6 + SwiftUI | Persistencia: SwiftData.

**Excepciones al Anti-Bloat Fence:** una librería de terceros solo entra si el SDK nativo no ofrece la capacidad, y el contrato lo justifica en la Anti-Bloat Fence: qué resuelve, su peso y la alternativa nativa descartada.

### 3.2 Lista de Chequeo de Solidez y Criterio de Parada
Para evitar sugerencias infinitas de la IA, el contrato debe cumplir 4 puntos antes de programar:

1. `[x]` **Estructura Invariable:** Entradas, salidas, entidades y Enums tipados.
2. `[x]` **Defensas de Frontera:** Excepciones y errores explicitados (sin `any` ni `catch` genéricos).
3. `[x]` **Cero Dependencias Parásitas:** Uso exclusivo del SDK nativo, el runtime aprobado o una excepción justificada en la Anti-Bloat Fence.
4. `[x]` **Filtro de Diferimiento:** Ideas secundarias movidas a `contracts/CONTRACT_BACKLOG.md`.

> **🛑 CRITERIO DE PARADA OBLIGATORIO (STOP CRITERION):**
> Al cumplirse los 4 puntos, la IA emite: *“Contrato v1 sólido y cerrado. Listo para /znve-execute.”* y DETIENE la generación.

### 3.3 Análisis Delta (`/znve-contract --delta`)
Para proyectos en desarrollo o actualización de versiones:
1. Audita discrepancias entre `contracts/` y `src/`.
2. Clasifica en **Cubo A (Requerido Ya / Etapa Activa)** y **Cubo B (Diferido a `CONTRACT_BACKLOG.md`)**.
3. Sincroniza y re-congela el contrato antes de modificar código.

---

## 4. LOS 6 MODOS OPERATIVOS UNIVERSALES

| Modo | Nombre | Flujo de comandos |
|---|---|---|
| 🟢 1 | **Greenfield** (proyectos nuevos, día 0) | `/znve-contract` → `/znve-execute` |
| 🔵 2 | **In-Flight** (proyectos activos y nuevas capacidades) | `/znve-contract --delta` → `/znve-execute` |
| 🟠 3 | **Hotfix & Recovery** (triaje de crisis en producción) | `/znve-triage` → `/znve-hotfix` |
| 🟣 4 | **Modern Maintenance** (migración de SDKs y breaking changes) | `/znve-upgrade` |
| 🟡 5 | **Legacy Rescue** (refactorización en 5 fases de monolitos críticos) | `/znve-forensic` → `/znve-harness` → `/znve-legacy-rescue` |
| 🔴 6 | **Audit & Hardening** (higiene técnica, memoria y seguridad) | `/znve-audit` |

Las 5 fases de Legacy Rescue son: ingesta pasiva, reporte forense, arnés Golden Master, Shadow Run (`Salida(Nuevo) == Salida(Legacy)`) y Strangler Fig. No se avanza de fase sin que la anterior esté verificada.

---

## 5. CAPA CAMALEÓNICA (PLATFORM-SPECIFIC ADAPTERS)

Restricciones adicionales por stack. Se suman a los guardrails globales; no los reemplazan.

* **Android:** `WorkManager`, `LifecycleOwner` y `StateFlow`; sin `WakeLock` innecesarios, sin retener contextos de Activity ni bloquear el hilo de UI.
* **iOS / macOS (Swift):** SwiftUI sobre `@MainActor` solo para vistas, trabajo pesado en `Actors` de fondo y `BGTaskScheduler`; sin capturas fuertes de `self` (`[weak self]`).
* **Windows Desktop (C# / WinUI / WPF / C++):** `IDisposable` estricto, `async/await` puro sin `.Result`/`.Wait()`, mutex de instancia única y ciclos de render aislados.
* **Híbridos (Tauri / Flutter / React Native):** IPC liviano con payloads mínimos y aislamiento de procesos nativos.
* **Web / Backend:** APIs nativas, contratos OpenAPI / JSON Schema, proyecciones, timeouts estrictos, middleware de sanitización y apagado elegante.

---

## 6. GOBERNANZA AGÉNTICA Y COMANDOS `/znve-*`

Cada comando impone un rol cerrado y un formato de salida con encabezados fijos (ver [protocols/COMMANDS.md](protocols/COMMANDS.md)). Las formas `/znve-contract`, `/znve contract` y `/znve -contract` son equivalentes; `/znve` solo equivale a `/znve-help`.

<!-- >>> znve:generated (znve-auto/builder.py desde master_spec.json; no editar a mano) -->
* `/znve-help` (todos): Manual operativo e índice de comandos. Solo lectura.
* `/znve-contract [--platform=desktop|web|mobile|hybrid] [--delta]` (modo 1, 2, 4): Diseño de interfaces inmutables, DTOs y Anti-Bloat Fence.
* `/znve-execute --target=<ruta/archivo>` (modo 1, 2, 4, 5): Implementación atómica en TARGET_FILE con desecho de recursos.
* `/znve-triage` (modo 3): Diagnóstico y contención de radio de impacto ante caídas. Solo lectura.
* `/znve-hotfix --incident=<ID>` (modo 3): Parche quirúrgico atómico con test de regresión obligatorio.
* `/znve-upgrade --dependency=<librería>` (modo 4): Migración de dependencias mediante Adaptador desacoplado.
* `/znve-forensic --target=<ruta/módulo>` (modo 2, 5, 6): Ingesta en solo lectura, matriz I/O y efectos secundarios. Solo lectura.
* `/znve-harness --target=<archivo_legacy>` (modo 5): Suite Golden Master de caja negra sobre código intacto.
* `/znve-legacy-rescue` (modo 5): Orquestación integral en 5 fases para código legacy.
* `/znve-audit --target=<módulo>` (modo 6): Hardening de hilos, memoria, descriptores y seguridad. Solo lectura.
<!-- <<< znve:generated -->

---

## 7. FORMATO DE RESPUESTA POR DEFECTO

Toda consulta técnica sin comando se responde en 4 bloques cerrados:

1. **BLOQUE 1: SYSTEM BLUEPRINT & CONTRATO:** límites, plataforma, Anti-Bloat Fence y contrato estricto (DTO/interfaz).
2. **BLOQUE 2: RACIONAL DE INGENIERÍA:** 2-3 viñetas que justifican la mínima huella y la ausencia de dependencias parásitas.
3. **BLOQUE 3: TAREAS ATÓMICAS DE IMPLEMENTACIÓN:** `TARGET_FILE` único, acción quirúrgica y restricciones aplicadas.
4. **BLOQUE 4: VERIFICACIÓN ATÓMICA:** comando de terminal determinista o prueba reproducible.

Las preguntas conceptuales se responden de forma directa, sin forzar los 4 bloques.

---

## 8. HERRAMIENTAS MCP (`znve_*`)

El servidor de referencia (`protocols/mcp/znve-mcp-server.ts`, transporte stdio) convierte las cláusulas en barandillas físicas para agentes autónomos. Las rutas se resuelven contra `ZNVE_WORKSPACE`.

| Herramienta | Fase | Garantía |
|---|---|---|
| `znve_help` | Ayuda | Sirve el manual `protocols/COMMANDS.md`, completo o por tema. |
| `znve_forensic_scan` | Ingesta | Lectura de texto (hasta 1 MiB) sin escritura en disco. |
| `znve_validate_contract` | Contrato | Rechaza `SELECT *`, `.find({})` y la importación de librerías vetadas. |
| `znve_scaffold_harness` | Aislamiento | Solo escribe bajo `tests/` o `sandbox/`. |
| `znve_surgical_write` | Escritura | Escritura atómica; rechaza `catch`/`except` que silencian errores, `.git/`, `node_modules/` y recursos abiertos sin patrón de desecho. |
| `znve_audit_resources` | Hardening | Detecta bloqueos síncronos, busy-waiting y `WakeLock.acquire()`. |

Ninguna herramienta lee ni escribe fuera de `ZNVE_WORKSPACE`, tampoco a través de enlaces simbólicos.

---

## 9. IMPLEMENTACIÓN DE REFERENCIA Y CONFORMIDAD

### 9.1 Fuente única de verdad
La versión, los axiomas, los guardrails, los escenarios, los comandos, la Capa Camaleónica y las herramientas MCP se declaran una sola vez en `znve-auto/master_spec.json`. El compilador `znve-auto/builder.py` (biblioteca estándar de Python) genera a partir de ella las directivas de Claude, Gemini, Copilot, Cursor, DeepSeek, Ollama, OpenRouter y Antigravity, los manuales de comandos y los bloques gestionados de esta especificación, el README y la página web.

### 9.2 Conformidad
Una directiva o herramienta es conforme con ZNVE v2.3.0 si:
1. Expone los 10 comandos con los encabezados de salida definidos en `protocols/COMMANDS.md`.
2. Aplica los 7 guardrails de la sección 2.6 y la Capa Camaleónica del stack detectado.
3. Respeta el criterio de parada de la sección 3.2 y el formato por defecto de la sección 7.
4. Cita una única versión de ZNVE, la de esta especificación.

`znve-auto/test_sync.py` certifica estos puntos para los artefactos del repositorio y se ejecuta en el CI (`.github/workflows/znve-parity.yml`) en cada push y pull request.

---

## 10. VERSIONADO

ZNVE sigue SemVer:
* **Mayor:** cambios en axiomas, pilares o en la semántica de un comando existente.
* **Menor:** comandos, opciones (`--platform`, `--delta`) o modos nuevos compatibles con los anteriores.
* **Parche:** correcciones de redacción, ejemplos o formato.

Las propuestas de cambio siguen el proceso de RFC descrito en [CONTRIBUTING.md](CONTRIBUTING.md).
