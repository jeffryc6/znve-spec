# ==============================================================================
# ZERO-NOISE VIBE ENGINEERING (ZNVE) — PROTOCOLO OPERATIVO UNIVERSAL
# Framework: Zero-Noise Vibe Engineering (ZNVE)
# Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
# Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
# ==============================================================================

Este documento es la especificación técnica inmutable que rige el trabajo entre el 
humano (Director de Arquitectura) y los agentes de Inteligencia Artificial 
(Claude, Cursor, Windsurf, Copilot, ChatGPT, Antigravity).

Aplica con igual rigor a:
- Aplicaciones Móviles (Android nativo / iOS nativo).
- Aplicaciones de Escritorio (Windows WinUI/WPF/C#, macOS, Linux, C++, Rust).
- Aplicaciones Híbridas y Multiplataforma (Flutter, Tauri, React Native, Electron).
- Aplicaciones Web, Servicios Backend, Microservicios, CLIs y Sistemas Embebidos.

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
- Cada falla se investiga hasta su causa de fondo: desbordamiento de memoria, bloqueos mutuos (deadlocks), contención de hilos o incompatibilidad con el sistema operativo anfitrión.

---

## 🧭 MATRIZ DE ADAPTACIÓN POR PLATAFORMA (CHAMELEON LAYER)

Al intervenir en un stack específico, la IA debe activar automáticamente los criterios de la plataforma correspondiente:

| Plataforma | Prioridades de Ejecución ZNVE | Anti-patrones Prohibidos para la IA |
|---|---|---|
| **Android** | Respetar `LifecycleOwner`, trabajo diferido con `WorkManager`, StateFlow/Flows eficientes, arranque rápido (*Cold Boot*). | Despertar la CPU con `WakeLock` innecesarios, bloquear el Main Thread, ignorar muerte del proceso por el sistema operativo. |
| **Windows Desktop** | Liberación de recursos no administrados (`IDisposable`), procesamiento asíncrono (`async/await` sin `Wait()`), instancia única (*Single Instance Mutex*). | Bloquear el despachador de UI (UI Dispatcher), dependencias masivas en runtime, dejar procesos secundarios en segundo plano al salir. |
| **Híbrido (Tauri / Flutter / RN)** | Mensajería binaria optimizada a través del puente (Bridge/IPC), inmutabilidad de estado, mínimo tamaño de binario compilado. | Pasar objetos JSON gigantescos por el puente nativo en cada frame, re-renderizar todo el árbol de vistas por cambios locales. |
| **Web & Backend** | Modularidad sin dependencias redundantes, contención de concurrencia, límites estrictos de memoria por worker, compresión de transferencias. | Cargar librerías de utilidad completas para funciones triviales, escaneos no indexados en la base de datos, fugas en event listeners. |

---

## 🎛️ MODOS OPERATIVOS UNIVERSALES

Antes de iniciar una tarea, se declara el **MODO ACTIVO** de la intervención:

### 🟢 MODO 1: GREENFIELD (CREACIÓN DESDE CERO)
*Aplicar cuando se diseña un módulo, pantalla, servicio o cliente nuevo.*
1. **Definir Perímetro:** Delimitar qué resuelve el MVP y qué queda explícitamente fuera (Anti-Bloat Fence).
2. **Definir Contrato:** Redactar el DTO, interfaz de estado o firma de eventos antes de escribir lógica interna.
3. **Implementación Atómica:** Generar la lógica mínima y eficiente que satisface el contrato.
4. **Verificación:** Ejecutar una prueba atómica (test unitario, verificación de compilación o benchmark local).

### 🟡 MODO 2: LEGACY RESCUE (REFACTORIZACIÓN DE SISTEMAS CRÍTICOS)
*Aplicar al intervenir archivos monolíticos, código espagueti o sistemas legacy en producción.*
1. **Fase 1 (Ingesta Pasiva - Zero Touch):** La IA analiza el código en modo estrictamente de lectura. Prohibido sugerir o escribir cambios en este paso.
2. **Fase 2 (Reporte Forense):** La IA documenta entradas, salidas, efectos secundarios (llamadas a disco, hardware, base de datos, APIs) y dependencias ocultas.
3. **Fase 3 (Arnés de Caracterización):** Se construyen pruebas de caja negra contra el código original intacto para congelar su comportamiento actual (Snapshot).
4. **Fase 4 (Extracción Quirúrgica):** Se extrae módulo por módulo bajo nuevos contratos tipados, garantizando que el arnés de pruebas se mantenga en verde.

### 🔴 MODO 3: HARDENING, RENDIMIENTO & AUDITORÍA
*Aplicar en optimización de rendimiento, contención de fallos, auditoría de seguridad y concurrencia.*
1. **Auditoría de Superficie y Recursos:** Identificar fugas de memoria, descriptores abiertos, consumo parásito de CPU/batería o puertos/interfaces expuestas innecesariamente.
2. **Aislamiento de Tareas Pesadas:** Desacoplar el trabajo de computación pesada del hilo principal o de la interfaz de usuario mediante workers, colas o hilos en segundo plano.
3. **Pruebas de Esfuerzo y Fallo Controlado:** Verificar la resiliencia del sistema ante desconexión total de red, datos corruptos y apagado abrupto.

---

## 📋 DIRECTIVA DE EJECUCIÓN PARA AGENTES DE IA (AI DIRECTIVE)

Al recibir una tarea bajo el protocolo ZNVE, responde obligatoriamente con la siguiente estructura de 4 bloques:

### BLOQUE 1: SYSTEM BLUEPRINT / ESPECIFICACIÓN
- **Objetivo y Límites:** Qué resuelve la tarea y qué queda estrictamente fuera de alcance.
- **Plataforma y Entorno:** Plataforma objetivo (Android, Windows, Web, Híbrido, etc.) y modelo de hilos aplicable.
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