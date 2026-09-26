<p align="right">
  <a href="https://translate.google.com/translate?sl=es&tl=en&u=https://github.com/jeffryc6/znve-spec/blob/main/rfcs/0001-ios-swift-chameleon.md">
    <img src="https://img.shields.io/badge/Translate_to-English-blue?style=flat-square&logo=googletranslate" alt="Translate to English">
  </a>
</p>

# RFC 0001: Adaptación de la Capa Camaleónica para iOS / Swift Nativo
- **Autor:** Jeffry Carmona (@jeffryc6)
- **Fecha:** 2026-09-24
- **Estado:** Accepted
- **Componente Afectado:** Chameleon Layer

## 1. Motivación
La matriz camaleónica contemplaba Android nativo, Windows Desktop y Web, pero requería formalizar las restricciones operativas para el ecosistema Apple (iOS/iPadOS/macOS) en Swift moderno (Swift Concurrency, Actors, SwiftUI).

## 2. Especificación Técnica
Se incorporan las siguientes reglas obligatorias para agentes al interactuar con stacks Swift/Apple:

| Plataforma | Prioridades ZNVE | Anti-patrones Prohibidos para la IA |
|---|---|---|
| **iOS / Swift** | Aislamiento en el `@MainActor` exclusivamente para vistas SwiftUI; ejecución pesada en `Actors` de fondo; persistencia local ligera con SwiftData o SQLite directo; tareas diferidas mediante `BGTaskScheduler`. | Bloquear el hilo principal con cálculos o I/O; capturas fuertes de `self` en closures que provoquen ciclos de retención de memoria (fugas de memoria); tareas infinitas en segundo plano que provoquen terminación forzada por el Watchdog del sistema operativo. |

## 3. Demostración de Cero Ruido
Promueve el uso exclusivo de las APIs nativas del framework Foundation y Swift Concurrency, erradicando dependencias pesadas de terceros para gestión de redes o reactividad.

## 4. Plan de Verificación
- Análisis de fugas con `leaks` y `Instruments`.
- Cero advertencias de concurrencia estricta (`-strict-concurrency=complete`).