# Zero-Noise Vibe Engineering (ZNVE)
**Norma Técnica Universal, Gobernanza Agéntica y Ecosistema de Protocolos v2.3.0**

[![Specification Version](https://img.shields.io/badge/ZNVE-v2.3.0-blue.svg)](SPECIFICATION.md)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](LICENSE)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP Server Ready](https://img.shields.io/badge/MCP-Server_v1.0-green.svg)](protocols/mcp/)

---

## 🎯 ¿Qué es ZNVE?

**Zero-Noise Vibe Engineering (ZNVE)** es una norma técnica universal y marco operativo que transforma la programación asistida por Inteligencia Artificial (Cursor, Windsurf, Claude Code, Copilot, Antigravity, Roo Code) en un proceso quirúrgico, de alta precisión y sin bucles infinitos de reparación (*AI agentic drift*).

Basado en dos axiomas fundamentales:
1. **Inteligencia en el diseño; huella mínima en la ejecución.**
2. **Ejecución basada en contratos deterministas; la IA no inventa arquitectura.**

---

## 🚀 Innovaciones Clave en v2.3.0

* **Poda de Contexto (*Context Boundary Pruning*):** Eliminación del ruido en la ventana de contexto aislando la IA dentro de `contracts/` y un `TARGET_FILE` único.
* **Análisis Tecnológico por Plataforma:** Recomendaciones automáticas de stack técnico (Escritorio, Web, Android, iOS/macOS, Híbrido) sin dependencias parásitas.
* **Lista de Chequeo de Solidez & Criterio de Parada:** Detiene las sugerencias infinitas de la IA en el momento exacto en que el contrato es sólido.
* **Análisis Delta (`/znve-contract --delta`):** Sincronización transparente para proyectos iniciados dividiendo sugerencias en **Cubo A (Actual)** y **Cubo B (Backlog Diferido)**.
* **Servidor MCP Nivel IDE:** Integración física con Antigravity, Cursor, Windsurf y Claude Desktop.

---

## 📂 Layout del Repositorio (`znve-spec/`)

```text
znve-spec/
├── .github/
│   └── copilot-instructions.md               <-- Instrucciones oficiales para GitHub Copilot
├── case-studies/
│   ├── 01-anti-bot-detection-lab/            <-- Laboratorio de huellas TLS (JA3/JA4) y mitmproxy
│   └── 02-legacy-monolith-rescue/            <-- Caso de estudio Golden Master
├── contracts/                                <-- Contratos de ejemplo (TS, Python, JSON Schema)
├── protocols/
│   ├── ZNVE_PROTOCOL.md                      <-- Protocolo maestro (6 Modos Operativos)
│   ├── ZNVE_ModernApps_Protocol.MD           <-- Protocolo de Hotfixes y Upgrades
│   ├── ZNVE_LEGACY_PROTOCOL.md               <-- Protocolo de rescate legacy (Golden Master)
│   ├── GREENFIELD_STARTER.md                 <-- Plantilla de inicio rápido Día 0
│   ├── ZNVE_CONTRACT_WORKFLOW.md             <-- Guía paso a paso del flujo de contratos
│   ├── PROMPT_GUIDE.md                       <-- Guía de prompts genéricos accionables
│   ├── COMMANDS.md                           <-- Catálogo completo de comandos /znve-*
│   ├── agents/                               <-- Directivas por proveedor (Claude, DeepSeek, Ollama, OpenRouter)
│   └── mcp/                                  <-- Servidor Model Context Protocol (stdio)
├── rfcs/                                     <-- Sistema de RFCs para evolución del estándar
├── CONTRIBUTING.md                           <-- Guía para contribuir a ZNVE
├── LICENSE                                   <-- Licencia dual (CC BY 4.0 / MIT)
├── README.md                                 <-- Este archivo
├── SPECIFICATION.md                          <-- Especificación técnica formal v2.3.0
└── INDEX_HTML.md                             <-- Código fuente de la Landing Page interactiva
```

---

## 🛠️ Catálogo de Comandos Agénticos (`/znve-*`)

| Comando | Propósito | Salida / Acción |
| :--- | :--- | :--- |
| `/znve-contract` | Diseña contratos y sugiere stack por plataforma. | DTOs + Lista de Chequeo + Stop Criterion. |
| `/znve-contract --delta` | Sincroniza contrato en proyectos iniciados. | Diff + Cubos A (Actual) y B (Diferido). |
| `/znve-execute` | Implementación quirúrgica en código. | Código en `TARGET_FILE` + Prueba unitaria. |
| `/znve-forensic` | Diagnóstico estático de solo lectura. | Reporte forense y mapa de causa raíz. |
| `/znve-harness` | Despliega arnés Golden Master. | Suite en `tests/characterization/`. |
| `/znve-hotfix` | Triaje de incidentes críticos en producción. | Parche defensivo en adaptador aislado. |
| `/znve-upgrade` | Migración de SDKs con breaking changes. | Capa Anti-Corrupción (Adapter Pattern). |
| `/znve-audit` | Purga de memoria, hilos bloqueados y logs. | Tabla de hallazgos y corrección atómica. |

---

## 📜 Licencia

Este proyecto utiliza un esquema de **Licencia Dual**:
* **CC BY 4.0 (Creative Commons Attribution 4.0 International):** Para la Especificación (`SPECIFICATION.md`), Manifiesto, Protocolos y Documentación.
* **MIT License:** Para el Servidor MCP, scripts de automatización, contratos DTO y código de ejemplo.
