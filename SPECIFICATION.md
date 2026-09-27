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

---

## 2. LOS 5 PILARES DE ZNVE

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          LOS 5 PILARES DE ZNVE                           │
├───────────────┬───────────────┬───────────────┬───────────────┬──────────┤
│ 1. CERO RUIDO │ 2. CONTRATOS  │ 3. EFICIENCIA │ 4. ESTADO     │ 5. SEG.  │
│    (ANTI-     │    PRIMERO    │   ASIMÉTRICA  │    AG NÓSTICO │ DEFENSIVA│
│    BLOAT)     │ (CONTRACT-1st)│ (LOW-FOOTPRINT│ (PROYECCIONES)│ & FORENS.│
└───────────────┴───────────────┴───────────────┴───────────────┴──────────┘
```

### Pilar 1: Cero Ruido (Zero-Noise Operations & Anti-Bloat Fence)
* Prohibición absoluta de librerías de terceros no esenciales o parásitas.
* Prohibida la emisión de logs rutinarios de confirmación en entornos de producción. La telemetría opera por excepción.

### Pilar 2: Contratos Primero (Contract-First AI)
* Antes de escribir una sola línea de lógica de negocio, se debe definir el contrato inmutable en la carpeta `contracts/` (DTOs, Zod, Pydantic v2 o JSON Schema).
* Poda de Contexto (*Context Boundary Pruning*): Los agentes de IA reciben únicamente el contrato activo y el archivo objetivo (`TARGET_FILE`).

### Pilar 3: Eficiencia Asimétrica y Respeto a Recursos
* Consumo mínimo de CPU y RAM. Liberación determinista de recursos (`close`, `dispose`, `finally`, `unbinding`).
* Garantía de hilos no bloqueantes (I/O asíncrono obligatorio).

### Pilar 4: Dominio de Estado Agnóstico
* Consultas y mutaciones de estado estrictamente proyectadas.
* Prohibidas las consultas ciegas o escaneos masivos en memoria.

### Pilar 5: Seguridad Defensiva y Diagnóstico Forense
* Validación y sanitización estricta en fronteras de entrada.
* Prohibidos los bloques `try/catch` vacíos o el silenciamiento de excepciones. Trazabilidad con `X-Run-ID`.

---

## 3. FLUJO DE CONTRATOS Y CONTROL ANTI-BUCLE

### 3.1 Análisis Tecnológico por Plataforma
Al activar `/znve-contract`, la IA evalúa el tipo de aplicación y sugiere el stack con cero peso parásito:

* **Escritorio (Windows / macOS / Linux):** Rust + Tauri v2 o WinUI 3 nativo | Persistencia: SQLite (WAL mode) / DuckDB.
* **Web-App:** Vite + TypeScript / Next.js App Router | Persistencia: IndexedDB (Dexie.js).
* **Híbrida (Mobile / Desktop):** Tauri Mobile / Flutter / React Native Bare | Persistencia: MMKV / WatermelonDB.
* **Android Nativo:** Kotlin + Jetpack Compose + Room DB + Corrutinas.
* **macOS / iOS Nativo:** Swift 6 + SwiftUI + SwiftData.

### 3.2 Lista de Chequeo de Solidez y Criterio de Parada
Para evitar sugerencias infinitas de la IA, el contrato debe cumplir 4 puntos antes de programar:

1. `[x]` **Estructura Invariable:** Entradas, salidas, entidades y Enums tipados.
2. `[x]` **Defensas de Frontera:** Excepciones y errores explicitados (sin `any` ni `catch` genéricos).
3. `[x]` **Cero Dependencias Parásitas:** Uso exclusivo del SDK nativo o runtime aprobado.
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

1. 🟢 **Modo 1: Greenfield (Proyectos Nuevos Día 0)**
2. 🔵 **Modo 2: In-Flight (Proyectos Activos & Nuevas Capacidades)**
3. 🟠 **Modo 3: Hotfix & Recovery (Triaje de Crisis en Producción)**
4. 🟣 **Modo 4: Modern Maintenance (Migración de SDKs & Breaking Changes)**
5. 🟡 **Modo 5: Legacy Rescue (Refactorización en 5 Fases de Monolitos Críticos)**
6. 🔴 **Modo 6: Audit & Hardening (Higiene Técnica, Memoria y Seguridad)**

---

## 5. CAPA CAMALEÓNICA (PLATFORM-SPECIFIC ADAPTERS)

* **Android:** Cumplimiento de `WorkManager`, liberación de `WakeLock`, prevención de bloqueos en hilo UI.
* **Windows Desktop:** Manejo estricto de `IDisposable`, ciclos de render WinUI/WPF aislados.
* **Híbridos (Tauri/Flutter/React Native):** IPC liviano, aislamiento de procesos nativos.
* **Web / Backend:** Contratos OpenAPI / JSON Schema, respuestas tipadas y middleware de sanitización.

---

## 6. GOBERNANZA AGÉNTICA Y COMANDOS `/znve-*`

* `/znve-contract`: Diseña/actualiza contratos y sugiere stack por plataforma.
* `/znve-contract --delta`: Análisis incremental y control de backlog.
* `/znve-execute`: Escritura quirúrgica sobre `TARGET_FILE` único.
* `/znve-forensic`: Análisis estático de solo lectura (*Zero-Touch*).
* `/znve-harness`: Despliegue de arnés de caracterización Golden Master.
* `/znve-hotfix`: Contención de incidentes en producción.
* `/znve-upgrade`: Migración con Adapter Pattern para absorción de breaking changes.
* `/znve-audit`: Purga de logs, bloqueos de hilos y fugas de memoria.
