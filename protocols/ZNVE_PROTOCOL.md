# ==============================================================================
# ZERO-NOISE VIBE ENGINEERING (ZNVE) — PROTOCOLO OPERATIVO UNIVERSAL
# Archivo: protocols/ZNVE_PROTOCOL.md
# Versión: 2.3.0
# Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
# Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
# ==============================================================================

Este documento es el protocolo operativo que rige el trabajo entre el humano
(Director de Arquitectura) y los agentes de Inteligencia Artificial (Claude,
Gemini, Cursor, Windsurf, Copilot, DeepSeek, Ollama, OpenRouter, Antigravity). La norma
formal está en [SPECIFICATION.md](../SPECIFICATION.md) y el catálogo de comandos
en [COMMANDS.md](COMMANDS.md).

Aplica con igual rigor a:
- Aplicaciones Móviles (Android nativo / iOS nativo).
- Aplicaciones de Escritorio (Windows WinUI/WPF/C#, macOS, Linux, C++, Rust).
- Aplicaciones Híbridas y Multiplataforma (Flutter, Tauri, React Native, Electron).
- Aplicaciones Web, Servicios Backend, Microservicios, CLIs y Sistemas Embebidos.

Protocolos especializados:
- [ZNVE_MODERN_APPS_PROTOCOL.md](ZNVE_MODERN_APPS_PROTOCOL.md): modos 3 y 4 (hotfix y upgrades).
- [ZNVE_LEGACY_PROTOCOL.md](ZNVE_LEGACY_PROTOCOL.md): modo 5 (rescate legacy en 5 fases).
- [GREENFIELD_STARTER.md](GREENFIELD_STARTER.md): modo 1 paso a paso.

---

## 🏛️ LOS 5 PILARES UNIVERSALES DE ZNVE

### 1. Cero Ruido Operativo y de Experiencia (Zero-Noise Operations & UX)
- **Higiene de Dependencias:** Prohibido instalar paquetes externos para tareas que se resuelven con las APIs nativas del SDK, lenguaje o plataforma anfitriona.
- **Silencio en Runtime y Batería:** Prohibido emitir logs rutinarios de confirmación en rutas críticas. Cero sondeos continuos (polling) que impidan el reposo de la CPU o drenen la batería.
- **Higiene Visual y Notificaciones:** Cero alertas o notificaciones intrusivas al usuario final; la interacción solo se activa ante eventos accionables o anomalías críticas.
- **Sin Relleno Conversacional:** Las respuestas técnicas de la IA deben ser quirúrgicas, directas al artefacto, sin preámbulos decorativos ni disculpas.

### 2. Contratos Deterministas (Contract-First AI)
- La IA nunca genera código de producción sin un contrato explícito previo:
  - En datos: DTOs, esquemas tipados, modelos inmutables o entidades validadas.
  - En UI/Plataforma: Interfaces de eventos, contratos de estado (State Machines) o protocolos de enlace IPC.
- El código generado debe satisfacer el contrato al 100%, sin agregar propiedades inventadas, abstracciones prematuras ni lógica especulativa.
- **Poda de Contexto:** el agente trabaja solo con el contrato activo y el archivo objetivo (`TARGET_FILE`).

### 3. Eficiencia Asimétrica y Mínima Huella de Recursos
- **"Cerebro en el diseño, reflejo en el dispositivo":**
  - **Hilo Principal Sagrado:** El hilo de interfaz gráfica (UI Thread / Main Loop) jamás debe bloquearse con I/O, criptografía o cálculos pesados.
  - **Gestión Estricta de Recursos:** Liberación determinista de handles del sistema operativo, listeners, suscripciones y memoria. Cero procesos huérfanos al cerrar la aplicación.
  - **Ciclo de Vida Consciente:** En entornos móviles o de escritorio, el software debe respetar las transiciones de estado (primer plano, segundo plano, suspensión, hibernación) y entrar en reposo profundo cuando no esté en uso.

### 4. Dominio de Estado y Persistencia Agnóstica
- **Motor Agnóstico:** Aplica a bases de datos relacionales, documentales (NoSQL), almacenes clave-valor, SQLite local, DataStore/Room, Realm, o archivos planos atómicos.
- **Proyecciones Explícitas y Acceso Indexado:** Prohibido extraer colecciones, documentos o tablas enteras por defecto. Las consultas deben proyectar únicamente los campos requeridos y utilizar rutas indexadas.
- **Resiliencia Offline-First:** El estado del cliente debe tolerar la pérdida total de red mediante cachés locales consistentes y conciliación silenciosa al reanudar la conexión.

### 5. Seguridad Defensiva y Diagnóstico Forense (Zero-Trust & Zero-Crash)
- Cualquier entrada externa, parámetro de red, evento de hardware o intent del sistema se asume hostil y no sanitizado.
- Prohibido enmascarar excepciones con bloques defensivos vacíos o retardos arbitrarios (`sleep` / `setTimeout`).
- Cada falla se investiga hasta su causa de fondo: desbordamiento de memoria, bloqueos mutuos (deadlocks), contención de hilos o incompatibilidad con el sistema operativo anfitrión. La trazabilidad se apoya en `X-Run-ID`, no en logs rutinarios.

---

## 🧭 MATRIZ DE ADAPTACIÓN POR PLATAFORMA (CHAMELEON LAYER)

Al intervenir en un stack específico, la IA debe activar automáticamente los criterios de la plataforma correspondiente:

| Plataforma | Prioridades de Ejecución ZNVE | Anti-patrones Prohibidos para la IA |
|---|---|---|
| **Android** | Respetar `LifecycleOwner`, trabajo diferido con `WorkManager`, StateFlow/Flows eficientes, arranque rápido (*Cold Boot*). | Despertar la CPU con `WakeLock` innecesarios, bloquear el Main Thread, ignorar muerte del proceso por el sistema operativo. |
| **iOS / macOS (Swift)** | SwiftUI sobre `@MainActor` solo para vistas, trabajo pesado en `Actors` de fondo, tareas diferidas con `BGTaskScheduler`, persistencia ligera con SwiftData o SQLite. | Bloquear el hilo principal, capturas fuertes de `self` en closures (usar `[weak self]`), tareas de fondo infinitas que provoquen la terminación por el Watchdog. |
| **Windows Desktop** | Liberación de recursos no administrados (`IDisposable`), procesamiento asíncrono (`async/await` sin `Wait()`), instancia única (*Single Instance Mutex*). | Bloquear el despachador de UI (UI Dispatcher), dependencias masivas en runtime, dejar procesos secundarios en segundo plano al salir. |
| **Híbrido (Tauri / Flutter / RN)** | Mensajería binaria optimizada a través del puente (Bridge/IPC), inmutabilidad de estado, mínimo tamaño de binario compilado. | Pasar objetos JSON gigantescos por el puente nativo en cada frame, re-renderizar todo el árbol de vistas por cambios locales. |
| **Web & Backend** | Modularidad sin dependencias redundantes, contención de concurrencia, límites estrictos de memoria por worker, timeouts explícitos y apagado elegante. | Cargar librerías de utilidad completas para funciones triviales, escaneos no indexados en la base de datos, fugas en event listeners. |

---

## 🎛️ LOS 6 MODOS OPERATIVOS UNIVERSALES

Antes de iniciar una tarea, se declara el **MODO ACTIVO** de la intervención. Cada modo tiene su secuencia de comandos `/znve-*`.

### 🟢 MODO 1: GREENFIELD (CREACIÓN DESDE CERO)
*Aplicar cuando se diseña un módulo, pantalla, servicio o cliente nuevo.* Comandos: `/znve-contract` → `/znve-execute`.
1. **Definir Perímetro:** Delimitar qué resuelve el MVP y qué queda explícitamente fuera (Anti-Bloat Fence).
2. **Definir Contrato:** `/znve-contract --platform=<desktop|web|mobile|hybrid>` redacta los DTOs, la interfaz de estado o la firma de eventos y recomienda el stack. La IA se detiene al cumplir la lista de chequeo de solidez: *"Contrato v1 sólido y cerrado. Listo para /znve-execute."*
3. **Implementación Atómica:** `/znve-execute --target=<archivo>` genera la lógica mínima que satisface el contrato.
4. **Verificación:** Ejecutar una prueba atómica (test unitario, verificación de compilación o benchmark local).

### 🔵 MODO 2: IN-FLIGHT (PROYECTOS ACTIVOS Y NUEVAS CAPACIDADES)
*Aplicar al añadir funcionalidades a un sistema en desarrollo o en producción.* Comandos: `/znve-contract --delta` → `/znve-execute`.
1. **Análisis Delta:** Comparar `contracts/` con `src/` y clasificar los cambios en **Cubo A** (requerido ya) y **Cubo B** (diferido a `contracts/CONTRACT_BACKLOG.md`).
2. **Extensión, no mutación:** Los contratos activos se extienden; nunca se alteran sus campos o firmas existentes.
3. **Re-congelación:** Mostrar el diff del Cubo A y esperar aprobación antes de modificar código.
4. **Implementación y verificación:** `/znve-execute` sobre un único `TARGET_FILE` por tarea.

### 🟠 MODO 3: HOTFIX & RECOVERY (CRISIS EN PRODUCCIÓN)
*Aplicar ante caídas, bloqueos o excepciones en producción.* Comandos: `/znve-triage` → `/znve-hotfix`. Detalle en [ZNVE_MODERN_APPS_PROTOCOL.md](ZNVE_MODERN_APPS_PROTOCOL.md), Flujo A.
1. **Contención:** Aislar el radio de impacto (fallback local, circuit breaker) sin alterar contratos públicos.
2. **Diagnóstico Causal:** `/znve-triage` en solo lectura hasta encontrar la causa raíz reproducible.
3. **Hotfix Atómico:** `/znve-hotfix --incident=<ID>` sobre un único `TARGET_FILE`, con `X-Run-ID` en el punto de fallo.
4. **Regresión:** Test que falla sin el parche y pasa al 100% con él.

### 🟣 MODO 4: MODERN MAINTENANCE (SDKs Y BREAKING CHANGES)
*Aplicar al actualizar dependencias, SDKs o APIs externas con cambios disruptivos.* Comando: `/znve-upgrade`. Detalle en [ZNVE_MODERN_APPS_PROTOCOL.md](ZNVE_MODERN_APPS_PROTOCOL.md), Flujo B.
1. **Matriz de Breaking Changes:** versión previa frente a versión objetivo.
2. **Capa Anti-Corrupción:** contrato interno (`Port`) y adaptador (`Adapter`) que absorbe los cambios.
3. **Migración Aislada:** los cambios viven solo en el adaptador; el dominio no se entera.
4. **Verificación Dual:** paridad funcional y huella de memoria/binario.

### 🟡 MODO 5: LEGACY RESCUE (REFACTORIZACIÓN DE SISTEMAS CRÍTICOS)
*Aplicar al intervenir archivos monolíticos, código espagueti o sistemas legacy en producción.* Comandos: `/znve-forensic` → `/znve-harness` → `/znve-legacy-rescue`. Detalle en [ZNVE_LEGACY_PROTOCOL.md](ZNVE_LEGACY_PROTOCOL.md).
1. **Fase 1 (Ingesta Pasiva - Zero Touch):** La IA analiza el código en modo estrictamente de lectura. Prohibido sugerir o escribir cambios en este paso.
2. **Fase 2 (Reporte Forense):** La IA documenta entradas, salidas, efectos secundarios (llamadas a disco, hardware, base de datos, APIs) y dependencias ocultas.
3. **Fase 3 (Arnés de Caracterización):** Se construyen pruebas de caja negra contra el código original intacto para congelar su comportamiento actual (Golden Master).
4. **Fase 4 (Shadow Run):** El módulo nuevo se ejecuta en sombra hasta confirmar `Salida(Nuevo) == Salida(Legacy)`.
5. **Fase 5 (Strangler Fig):** Conmutación gradual sin downtime y retirada del código legacy en un commit dedicado.

### 🔴 MODO 6: AUDIT & HARDENING (HIGIENE TÉCNICA, MEMORIA Y SEGURIDAD)
*Aplicar en optimización de rendimiento, contención de fallos, auditoría de seguridad y concurrencia.* Comando: `/znve-audit`.
1. **Auditoría de Superficie y Recursos:** Identificar fugas de memoria, descriptores abiertos, consumo parásito de CPU/batería, logs ruidosos o puertos/interfaces expuestos innecesariamente.
2. **Aislamiento de Tareas Pesadas:** Desacoplar el trabajo de computación pesada del hilo principal o de la interfaz de usuario mediante workers, colas o hilos en segundo plano.
3. **Pruebas de Esfuerzo y Fallo Controlado:** Verificar la resiliencia del sistema ante desconexión total de red, datos corruptos y apagado abrupto.
4. **Hoja de Remediación:** Acciones atómicas priorizadas por causa raíz, cada una con su `TARGET_FILE` y verificación, entregadas para aprobación antes de tocar código.

---

## 📋 DIRECTIVA DE EJECUCIÓN PARA AGENTES DE IA (AI DIRECTIVE)

Si la tarea usa un comando `/znve-*`, la respuesta sigue el formato de salida de ese comando ([COMMANDS.md](COMMANDS.md)). Sin comando, responde obligatoriamente con la siguiente estructura de 4 bloques:

### BLOQUE 1: SYSTEM BLUEPRINT / ESPECIFICACIÓN
- **Objetivo y Límites:** Qué resuelve la tarea y qué queda estrictamente fuera de alcance.
- **Plataforma y Entorno:** Plataforma objetivo (Android, iOS, Windows, Web, Híbrido, etc.) y modelo de hilos aplicable.
- **Contrato de Datos y Estado:** Interfaces inmutables, DTOs, firmas de eventos o esquemas de persistencia.

### BLOQUE 2: RACIONAL DE INGENIERÍA
- 2 o 3 viñetas concisas justificando la solución técnica: por qué garantiza huella mínima de CPU/memoria, cero dependencias parásitas y fluidez en la plataforma.

### BLOQUE 3: TAREAS ATÓMICAS DE IMPLEMENTACIÓN
Lista numerada de cambios quirúrgicos. Cada tarea debe indicar:
- `TARGET_FILE`: Ruta exacta del archivo afectado.
- `ACTION`: Modificación exacta respetando el contrato del Bloque 1.
- `RESTRICTION`: Práctica prohibida en ese paso (ej. "No bloquear el UI thread", "No agregar librerías externas", "Liberar recursos en OnDestroy/Dispose").

### BLOQUE 4: PLAN DE VERIFICACIÓN ATÓMICA
- Comandos de terminal, tests unitarios, perfiles de memoria o pruebas de ejecución para validar que el cambio funciona, no tiene fugas de recursos ni introduce regresiones.

Las preguntas conceptuales se responden de forma directa y breve, sin forzar los 4 bloques.
