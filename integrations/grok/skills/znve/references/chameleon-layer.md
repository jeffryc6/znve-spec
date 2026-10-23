# 🦎 Capa Camaleónica de Plataforma (Chameleon Layer)

<!-- Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano. -->

Restricciones adicionales por stack. Se suman a los guardrails globales de ZNVE; no los reemplazan.

| Plataforma | Prioridades ZNVE | Antipatrones prohibidos |
|---|---|---|
| **Android** | `WorkManager`, `LifecycleOwner`, `StateFlow` nativo. | `WakeLock` innecesarios, retener contextos de Activity, bloquear el hilo de UI. |
| **iOS / macOS (Swift)** | SwiftUI sobre `@MainActor` solo para vistas; trabajo pesado en `Actors` de fondo; tareas diferidas con `BGTaskScheduler`; persistencia ligera con SwiftData o SQLite. | Bloquear el hilo principal; capturas fuertes de `self` en closures (usa `[weak self]`); tareas de fondo infinitas que provoquen la terminación por el Watchdog. |
| **Windows Desktop (C# / WinUI / WPF / C++)** | `IDisposable` en recursos no administrados; `async/await` puro; mutex de instancia única. | `.Result` o `.Wait()` bloqueantes; procesos zombis en segundo plano. |
| **Híbrido (Tauri / Flutter / React Native)** | Payloads mínimos por el puente nativo/IPC. | Serializaciones JSON masivas por el puente; re-renders innecesarios. |
| **Web & Backend** | APIs nativas (`fetch`, `crypto`, streams); proyecciones de campos; timeouts estrictos; límites de memoria por worker; apagado elegante (*graceful shutdown*). | Clientes HTTP sin timeout; consultas sin proyección; dependencias para lo que resuelve la plataforma. |

## Verificación sugerida por plataforma

- **Android:** Android Studio Profiler (memoria/CPU), StrictMode activado en debug.
- **iOS / macOS:** `leaks` e Instruments; cero advertencias con `-strict-concurrency=complete`.
- **Windows Desktop:** analizadores de `IDisposable` (CA2000) y Visual Studio Diagnostic Tools.
- **Web & Backend:** heap snapshots, `--inspect` en Node, pruebas de carga con límites de memoria.
