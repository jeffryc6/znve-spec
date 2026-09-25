# ==============================================================================
# ZERO-NOISE VIBE ENGINEERING (ZNVE) — PROTOCOLO OPERATIVO UNIVERSAL
# Archivo: protocols/ZNVE_PROTOCOL.md
# Versión: 2.2.0
# Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
# Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
# ==============================================================================

Este documento es la especificación técnica inmutable que rige la interacción entre el
humano (Director de Arquitectura) y los agentes de Inteligencia Artificial
(Claude, Cursor, Windsurf, Copilot, ChatGPT, Antigravity y afines).

Aplica con idéntico rigor técnico a:
- Aplicaciones Móviles (Android nativo / iOS nativo).
- Aplicaciones de Escritorio (Windows WinUI/WPF/C#, macOS, Linux, C++, Rust).
- Aplicaciones Híbridas y Multiplataforma (Flutter, Tauri, React Native, Electron).
- Aplicaciones Web Modernas, SPAs, APIs, Microservicios, Sistemas Distribuidos y CLIs.

---

## 🏛️ LOS 5 PILARES INMUTABLES DE ZNVE

### 1. Cero Ruido Operativo, de Contexto y UX (Zero-Noise Operations)
- **Higiene Radical de Dependencias:** Baneo total de librerías externas para tareas resolubles con las APIs nativas del lenguaje, runtime o SDK anfitrión.
- **Silencio en Runtime:** Prohibido emitir logs rutinarios de confirmación en rutas calientes ("OK", "Success", "Connecting..."). La observabilidad se activa exclusivamente ante fallos, anomalías confirmadas o transiciones de estado de severidad media/alta.
- **Cero Ruido de Contexto (Anti-Drift):** La IA debe omitir saludos, disculpas, felicitaciones y código especulativo. Se comunica exclusivamente mediante artefactos técnicos estructurados.
- **Higiene de Interfaz (UX):** Cero alertas o notificaciones no accionables al usuario final.

### 2. Contratos Deterministas (Contract-First AI)
- La IA nunca genera código de producción sin un contrato previo tipado e inmutable:
  - **En Datos:** DTOs, esquemas inmutables, interfaces o validaciones de frontera tipadas.
  - **En UI y Plataforma:** Máquinas de estado finitas, contratos de eventos o protocolos IPC/Bridge tipados.
- El código generado debe satisfacer el contrato al 100%, sin introducir propiedades no solicitadas ni abstracciones prematuras.

### 3. Eficiencia Asimétrica y Mínima Huella de Recursos
- **"Cerebro en el diseño, reflejo en el dispositivo":** La complejidad se resuelve en el modelado; el artefacto en ejecución debe tener huella mínima de CPU, memoria y batería.
- **Hilo Principal Sagrado:** El hilo de interfaz gráfica (UI Thread / Event Loop) jamás se bloquea con I/O síncrono, criptografía, parseos pesados o consultas.
- **Ciclo de Vida Consciente:** Liberación determinista obligatoria de recursos (`dispose`, `close`, `finally`, desuscripción de listeners y cancelación de timers/corrutinas).

### 4. Dominio de Estado y Persistencia Agnóstica
- **Motor Agnóstico:** Aplica a motores relacionales (SQL), documentales (NoSQL), almacenes clave-valor, series temporales, SQLite local o archivos atómicos.
- **Proyecciones Explícitas:** Prohibido el escaneo ciego (`SELECT *`, `find({})` sin proyecciones). Toda lectura debe proyectar únicamente los campos requeridos apoyándose en rutas indexadas.
- **Resiliencia Offline-First:** El estado del cliente debe tolerar la pérdida total de conectividad mediante cachés consistentes y conciliación silenciosa.

### 5. Seguridad Defensiva y Diagnóstico Forense (Zero-Trust & Zero-Crash)
- Cualquier parámetro de red, entrada de usuario o evento externo se asume hostil y no sanitizado.
- Prohibido enmascarar excepciones con bloques `try/catch` vacíos o retardos arbitrarios (`sleep`, `setTimeout`).
- Toda falla se investiga hasta su causa de fondo: agotamiento de pools, bloqueos mutuos (deadlocks), contención de hilos o discrepancias de esquemas.

---

## 🦎 CAPA CAMALEÓNICA DE PLATAFORMA (CHAMELEON LAYER)

| Entorno / Stack | Prioridades Obligatorias ZNVE | Anti-patrones Prohibidos para la IA |
|---|---|---|
| **Android (Kotlin)** | `WorkManager` para diferibles, `LifecycleOwner`, `StateFlow` nativo, inicio en frío ultra-rápido. | Retener contexto de Activity en singletons, bloquear el Main Thread, invocar `WakeLock` innecesarios. |
| **iOS / macOS (Swift)** | SwiftUI impulsado por `@Observable`/Actors, tareas de fondo con `BGTaskScheduler`, Swift Concurrency nativa. | Fugas de memoria por retención cíclica (falta de `[weak self]`), bloquear el `@MainActor` con tareas de I/O. |
| **Windows Desktop (C# / WinUI / WPF / C++)** | Manejo de desecho de recursos no administrados (`IDisposable`), `async/await` puro sin `.Result`/`.Wait()`, mutex de instancia única. | Bloquear el UI Dispatcher, spawn de procesos zombis en segundo plano al salir de la aplicación. |
| **Híbrido (Tauri / Flutter / React Native)** | Mensajería binaria/compacta en el puente IPC, inmutabilidad de estado, mínimo binario. | Pasar payloads JSON masivos por el puente nativo en cada frame, invalidar y re-renderizar todo el árbol de vistas. |
| **Web & Backend (Node, Go, Rust, Python, C#)** | Modularidad nativa, límites de memoria por worker, compresión de transferencias, timeouts estrictos y graceful shutdown. | Librerías masivas para operaciones triviales, escaneos no indexados en base de datos, listeners huérfanos. |

---

## 🎛️ LOS 6 MODOS OPERATIVOS UNIVERSALES

Antes de ejecutar cualquier tarea, el humano o la IA declaran el **MODO ACTIVO**:

┌────────────────────────────────────────────────────────────────────────┐
│ 🟢 MODO 1: GREENFIELD          --> Creación desde cero con base limpia │
│ 🔵 MODO 2: IN-FLIGHT           --> Proyecto activo / Nuevas features   │
│ 🟠 MODO 3: HOTFIX & RECOVERY   --> Triage y contención en producción   │
│ 🟣 MODO 4: MODERN MAINTENANCE  --> Upgrades, SDKs y Breaking Changes   │
│ 🟡 MODO 5: LEGACY RESCUE       --> Monolitos críticos sin tests (5 Fases)│
│ 🔴 MODO 6: AUDIT & HARDEN      --> Memoria, concurrencia, hilos y red  │
└────────────────────────────────────────────────────────────────────────┘


### 🟢 MODO 1: GREENFIELD (CREACIÓN DESDE CERO)
*Aplicar al iniciar un proyecto, módulo o servicio nuevo.*
1. **Definir Perímetro y Anti-Bloat Fence:** Delimitar qué resuelve el MVP y prohibir librerías redundantes.
2. **Definir Semilla de Contrato:** Redactar los DTOs, esquemas tipados o interfaces antes de implementar lógica.
3. **Implementación Atómica:** Generar la lógica mínima y autosuficiente que cumple el contrato.
4. **Verificación:** Ejecutar una prueba atómica o benchmark ejecutable.

### 🔵 MODO 2: IN-FLIGHT (PROYECTOS ACTIVOS / EXPANSIONES)
*Aplicar al agregar nuevas funciones en código modular existente sin romper la arquitectura activa.*
1. **Ingesta Focalizada:** Inspección exclusiva del módulo receptor y sus contratos inmediatos.
2. **Frontera Contractual:** La nueva función se aísla bajo un contrato nuevo sin mutar contratos existentes.
3. **Acoplamiento Mínimo:** Conexión mediante inyección de dependencias o interfaces desacopladas.
4. **Verificación de No-Regresión:** Ejecución de la suite previa antes de integrar.

### 🟠 MODO 3: HOTFIX & INCIDENT RECOVERY (PRODUCCIÓN EN CRISIS)
*Aplicar ante caídas de servicio, degradación crítica o excepciones imprevistas en producción.*
*Detalle operativo completo en `ZNVE_ModernApps_Protocol.MD`.*
1. **Aislamiento del Radio de Impacto (Blast Radius Fence):** Contener la hemorragia sin alterar la arquitectura. Activar circuit breakers, fallbacks locales o modo offline-first[cite: 1, 2].
2. **Diagnóstico Causal Determinista:** Identificar la causa raíz exacta (deadlocks, memory leak, pool agotado, timeout mal configurado)[cite: 1, 4]. Prohibidos bloques `try/catch` vacíos[cite: 1, 4].
3. **Hotfix Atómico Bounded:** Parche quirúrgico restringido al archivo y función causante (`TARGET_FILE` único)[cite: 1, 4]. Prohibido alterar contratos públicos[cite: 1].
4. **Test de Regresión Inmediato:** Creación de una prueba unitaria que reproduzca el fallo y valide la resolución antes de desplegar[cite: 1].

### 🟣 MODO 4: MODERN MAINTENANCE & UPGRADES (EVOLUTIVO MODERNO)
*Aplicar al actualizar versiones mayores de frameworks, SDKs de plataforma o APIs con breaking changes.*
*Detalle operativo completo en `ZNVE_ModernApps_Protocol.MD`.*
1. **Diff Contractual de Frontera:** Mapear discrepancias entre la API/SDK actual y la versión objetivo.
2. **Capa Anti-Corrupción (Adapter Pattern):** Aislar la nueva dependencia detrás de una interfaz ZNVE interna para no propagar cambios de terceros al dominio.
3. **Aislamiento de Deprecaciones:** Actualización archivo por archivo con verificación de compilación estricta.
4. **Verificación Dual / Shadow Test:** Garantizar paridad de comportamiento y huella de recursos antes del corte definitivo.

### 🟡 MODO 5: LEGACY RESCUE (SISTEMAS HEREDADOS Y CRÍTICOS)
*Aplicar al intervenir archivos monolíticos, código espagueti o sistemas en producción sin tests.*
Se rige estrictamente por las 5 fases de `ZNVE_LEGACY_PROTOCOL.md`:
1. Ingesta Pasiva (Zero-Touch en solo lectura).
2. Reporte Forense y Contratos Implícitos.
3. Arnés de Caracterización (Golden Master sobre código intacto).
4. Ejecución en Sombra (Shadow Run) con paridad bit a bit.
5. Conmutación gradual vía patrón Strangler Fig.

### 🔴 MODO 6: AUDIT, HARDENING & RENDIMIENTO
*Aplicar en optimización de recursos, mitigación de fugas de memoria o auditoría de seguridad.*
1. **Auditoría de Superficie y Fugas:** Detección de descriptores abiertos, listeners huérfanos o buffers saturados.
2. **Aislamiento de Cómputo:** Desacoplamiento de tareas intensivas fuera del hilo principal de UI.
3. **Pruebas de Esfuerzo Silencioso:** Resiliencia ante caídas de red, jitter y recuperación limpia de estado.

---

## 📋 DIRECTIVA DE RESPUESTA OBLIGATORIA PARA LA IA (4 BLOQUES)

Al recibir cualquier instrucción bajo ZNVE, responde obligatoriamente en 4 bloques cerrados:
1. `BLOQUE 1: SYSTEM BLUEPRINT & CONTRATO`: Límites, plataforma, restricciones y esquema tipado.
2. `BLOQUE 2: RACIONAL DE INGENIERÍA`: 2-3 viñetas justificando la huella mínima y la ausencia de dependencias parásitas.
3. `BLOQUE 3: TAREAS ATÓMICAS DE IMPLEMENTACIÓN`: `TARGET_FILE`, `ACTION` y `RESTRICTION` por cada paso.
4. `BLOQUE 4: VERIFICACIÓN ATÓMICA`: Comandos terminales, tests reproducibles o perfiles de recursos.
