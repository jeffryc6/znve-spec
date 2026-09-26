# ZNVE Specification (v1.1.0)
**Status:** Stable  
**Category:** Architecture & AI-Agent Governance  
**Author:** Jeffry Carmona (jeffryc6)  
**Date:** 2026-09-25  

> 🌐 **Idioma / Language:** Haz clic para desplegar tu idioma preferido | Click to expand your preferred language.

<details open>
<summary><b>🇪🇸 Versión en Español (Click para colapsar)</b></summary>
<br>

## 1. Alcance y Terminología
La presente especificación establece las cláusulas normativas que gobiernan la interacción entre desarrolladores de software y modelos de inteligencia artificial generativa durante el ciclo de vida del software (desarrollo nuevo, mantenimiento, recuperación ante incidentes y refactorización legacy).

- **Director de Arquitectura (Humano):** Responsable exclusivo de delimitar el perímetro del problema, validar contratos tipados y certificar la paridad funcional.
- **Ejecutor Táctico (Agente de IA):** Entidad algorítmica restringida a la generación de sintaxis determinista que satisface contratos sin introducir modificaciones estructurales no autorizadas.
- **Contrato:** Estructura tipada e inmutable (DTO, interfaz, esquema Zod o modelo relacional estricto) que define entradas, salidas, efectos secundarios y modos de fallo tolerados.
- **Radio de Impacto (Blast Radius):** Alcance máximo de archivos o componentes que pueden ser intervenidos durante una remediación de emergencia.

## 2. Los Dos Axiomas de Gobernanza
- **Axioma 1 (Asimetría Computacional):** Toda complejidad analítica y modelado de datos debe resolverse en la fase de diseño. El artefacto final en tiempo de ejecución debe operar con una huella de memoria, CPU y red cercana a cero.
- **Axioma 2 (Determinismo Contractual):** La IA tiene prohibido deducir o improvisar esquemas de datos, topologías o dependencias externas. Toda lógica generada debe derivar de un contrato preaprobado.

## 3. Cláusulas Normativas Universales

### 3.1. Cláusula de Higiene de Dependencias (Anti-Bloat Fence)
Queda prohibido incorporar paquetes de terceros cuando la funcionalidad requerida pueda resolverse mediante las APIs estándar provistas por el lenguaje, runtime o SDK del sistema anfitrión.

### 3.2. Cláusula de Observabilidad Silenciosa (Zero-Noise Runtime)
La telemetría en rutas críticas debe operar bajo el principio de reporte por excepción. Queda prohibida la emisión de registros rutinarios de confirmación de estado saludable (`"OK"`, `"Success"`). Las alertas se reservan exclusivamente para anomalías operativas de severidad media o alta.

### 3.3. Cláusula de Persistencia y Proyección Explícita
Toda interacción con motores de almacenamiento (relacionales, documentales, clave-valor o en memoria) debe ejecutarse mediante proyecciones de campos explícitos. Quedan prohibidas las consultas de barrido completo (`SELECT *`, `find({})` sin filtros) sin rutas indexadas.

### 3.4. Cláusula de Contención y Hotfix Quirúrgico (Blast Radius Fence)
Ante incidentes críticos o fallos en aplicaciones modernas en producción:
1. Queda prohibido aplicar soluciones cosméticas (*monkey-patching*), bloques `try/catch` vacíos o retardos arbitrarios (`sleep`).
2. La remediación debe limitarse a un único archivo causante (`TARGET_FILE`).
3. El parche debe conservar intactos los contratos públicos y venir acompañado obligatoriamente de una prueba de regresión determinista que reproduzca la falla y valide su resolución.

### 3.5. Cláusula de Aislamiento de Dependencias Modernas (Adapter Anti-Corrupción)
Al actualizar dependencias externas, frameworks o SDKs que contengan *breaking changes*, el agente de IA tiene prohibido mutar la lógica de negocio central. Toda incompatibilidad debe encapsularse detrás de una interfaz interna (*Port*) y un adaptador desacoplado (*Adapter*).

### 3.6. Cláusula de No-Intervención Legacy (Zero-Touch Assurance)
Ningún agente de IA modificará un archivo catalogado como legacy sin haber generado previamente un arnés de caracterización de caja negra (*Golden Master*) en un directorio aislado que certifique paridad matemática sobre el código original intacto.

## 4. Clasificación de Modos Operativos
Toda tarea ejecutada bajo ZNVE debe encuadrarse en uno de los 6 modos normativos:
- **Modo 1 (Greenfield):** Desarrollo desde cero con perímetro acotado y contrato previo.
- **Modo 2 (In-Flight):** Expansión modular sobre proyectos activos sin alterar contratos base.
- **Modo 3 (Hotfix & Recovery):** Triage forense, contención y parches atómicos en crisis de producción.
- **Modo 4 (Modern Maintenance):** Migración de SDKs y breaking changes vía capas de adaptación.
- **Modo 5 (Legacy Rescue):** Modernización de sistemas monolíticos en 5 fases controladas.
- **Modo 6 (Audit & Hardening):** Mitigación de fugas, contención de sockets y aislamiento de hilos.

</details>

<details open>
<summary><b>🇬🇧 English Version (Click to collapse)</b></summary>
<br>

## 1. Scope and Terminology
This specification establishes the normative clauses governing the interaction between software developers and generative artificial intelligence models throughout the software lifecycle (new development, maintenance, incident recovery and legacy refactoring).

- **Architecture Director (Human):** Solely responsible for delimiting the problem perimeter, validating typed contracts and certifying functional parity.
- **Tactical Executor (AI Agent):** Algorithmic entity restricted to generating deterministic syntax that satisfies contracts without introducing unauthorized structural changes.
- **Contract:** Typed, immutable structure (DTO, interface, Zod schema or strict relational model) that defines inputs, outputs, side effects and tolerated failure modes.
- **Blast Radius:** Maximum scope of files or components that may be touched during an emergency remediation.

## 2. The Two Governance Axioms
- **Axiom 1 (Computational Asymmetry):** All analytical complexity and data modeling must be resolved in the design phase. The final runtime artifact must operate with a near-zero memory, CPU and network footprint.
- **Axiom 2 (Contractual Determinism):** AI is forbidden from inferring or improvising data schemas, topologies or external dependencies. All generated logic must derive from a pre-approved contract.

## 3. Universal Normative Clauses

### 3.1. Dependency Hygiene Clause (Anti-Bloat Fence)
Adding third-party packages is forbidden when the required functionality can be achieved with the standard APIs provided by the host system's language, runtime or SDK.

### 3.2. Silent Observability Clause (Zero-Noise Runtime)
Telemetry on critical paths must follow the report-by-exception principle. Emitting routine healthy-state confirmation logs (`"OK"`, `"Success"`) is forbidden. Alerts are reserved exclusively for medium- or high-severity operational anomalies.

### 3.3. Persistence and Explicit Projection Clause
Every interaction with storage engines (relational, document, key-value or in-memory) must use explicit field projections. Full-scan queries (`SELECT *`, unfiltered `find({})`) without indexed paths are forbidden.

### 3.4. Containment and Surgical Hotfix Clause (Blast Radius Fence)
When facing critical incidents or failures in modern production applications:
1. Cosmetic fixes (*monkey-patching*), empty `try/catch` blocks and arbitrary delays (`sleep`) are forbidden.
2. Remediation must be limited to a single offending file (`TARGET_FILE`).
3. The patch must keep public contracts intact and must be accompanied by a deterministic regression test that reproduces the failure and validates its resolution.

### 3.5. Modern Dependency Isolation Clause (Anti-Corruption Adapter)
When upgrading external dependencies, frameworks or SDKs that contain *breaking changes*, the AI agent is forbidden from mutating core business logic. Every incompatibility must be encapsulated behind an internal interface (*Port*) and a decoupled adapter (*Adapter*).

### 3.6. Legacy Non-Intervention Clause (Zero-Touch Assurance)
No AI agent shall modify a file classified as legacy without first generating a black-box characterization harness (*Golden Master*) in an isolated directory that certifies mathematical parity against the untouched original code.

## 4. Operating Mode Classification
Every task executed under ZNVE must fall into one of the 6 normative modes:
- **Mode 1 (Greenfield):** Development from scratch with a bounded perimeter and a prior contract.
- **Mode 2 (In-Flight):** Modular expansion of active projects without altering base contracts.
- **Mode 3 (Hotfix & Recovery):** Forensic triage, containment and atomic patches during production crises.
- **Mode 4 (Modern Maintenance):** SDK migrations and breaking changes through adaptation layers.
- **Mode 5 (Legacy Rescue):** Modernization of monolithic systems in 5 controlled phases.
- **Mode 6 (Audit & Hardening):** Leak mitigation, socket containment and thread isolation.

</details>
