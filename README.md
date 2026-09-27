# Zero-Noise Vibe Engineering (ZNVE) v2.3.0
> **Spec-Driven Agentic Architecture & Zero-Noise AI Software Engineering**  
> *Arquitectura Agéntica Basada en Especificaciones e Ingeniería de Software IA Cero Ruido*

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code License: MIT](https://img.shields.io/badge/Code%20License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Standard: ZNVE v2.3.0](https://img.shields.io/badge/Standard-ZNVE%20v2.3.0-purple.svg)](SPECIFICATION.md)
[![MCP Server: Ready](https://img.shields.io/badge/MCP%20Server-Ready-orange.svg)](protocols/mcp/)

---

## 🌐 Language / Idioma
- 🇬🇧 [English Summary](#-english-overview)
- 🇪🇸 [Resumen en Español](#-resumen-en-español)

---

## 🇬🇧 English Overview

### What is ZNVE?
**Zero-Noise Vibe Engineering (ZNVE)** is an open, deterministic technical standard and agentic governance framework designed to eliminate the **"AI Agentic Drift"** and **AI death loops** during AI-assisted software development.

Unlike casual "vibe coding" that leads to bloated dependencies, infinite repair loops, and degraded context windows, ZNVE establishes a **contract-first architecture**. Human developers act as **Directors of Architecture**, while AI models (Cursor, Windsurf, Claude Code, Antigravity, Copilot, DeepSeek, Ollama) operate as **surgical tactical compilers**.

### Core Axioms
1. **Axiom 1 (Asymmetric Efficiency):** *Heavy intelligence in design; near-zero footprint during execution.*
2. **Axiom 2 (Deterministic Execution):** *The AI never invents architecture; it compiles strict, pre-approved contracts.*

### The 5 Immutable Pillars
1. **Zero-Noise Operations & UX:** Silent by default. No parasitic logging (`"OK"`, `"DEBUG"`) in production.
2. **Contract-First AI (Contract Boundaries):** Immutable DTOs/Schemas (`contracts/`) defined *before* generating implementation code.
3. **Asymmetric Efficiency:** Lightweight processes with strict memory disposal (`IDisposable`, `finally`, socket closure) and non-blocking threads.
4. **Agnostic State Domain:** Typed, explicit projections without blind database or state dumps.
5. **Defensive Security & Forensics:** Zero-Trust boundary validation, traceability (`X-Run-ID`), and no empty `catch/except` blocks.

### Key New Features in v2.3.0
- **Context Boundary Pruning:** Feeds only the active contract and target file to the AI, preventing context overload and hallucination loops.
- **Platform-Aware Stack Analysis:** Recommends zero-bloat tech stacks tailored for Desktop (WinUI/Tauri), Web, Android, iOS/macOS, or Hybrid apps.
- **Anti-AI-Loop Checklist & Stop Criterion:** Forces the AI to stop proposing features once a contract reaches 100% solidity.
- **Delta Contract Workflow (`/znve-contract --delta`):** Safely updates existing projects by separating current requirements (Bucket A) from future backlog ideas (Bucket B).

---

## 🇪🇸 Resumen en Español

### ¿Qué es ZNVE?
**Zero-Noise Vibe Engineering (ZNVE)** es un estándar técnico abierto y marco de gobernanza agéntica diseñado para eliminar la **degradación del contexto de la IA** y los **bucles infinitos de reparación** en el desarrollo asistido por IA.

A diferencia del "vibe coding" caótico que acumula librerías parásitas y código de baja calidad, ZNVE establece una **arquitectura basada en contratos**. El desarrollador humano actúa como **Director de Arquitectura**, mientras que los modelos de IA (Cursor, Windsurf, Claude Code, Antigravity, Copilot, DeepSeek, Ollama) se desempeñan como **compiladores quirúrgicos de sintaxis**.

### Axiomas Centrales
1. **Axioma 1 (Eficiencia Asimétrica):** *Inteligencia pesada en el diseño; huella casi nula en la ejecución.*
2. **Axioma 2 (Ejecución Determinista):** *La IA nunca inventa arquitectura; compila contratos estrictos previamente aprobados.*

### Los 5 Pilares Inmutables
1. **Operaciones Cero Ruido:** Silencio operativo por defecto. Prohibidos logs de rutina (`"OK"`, `"Paso por aquí"`).
2. **Contratos Primero:** DTOs y Esquemas inmutables (`contracts/`) definidos *antes* de escribir lógica de negocio.
3. **Eficiencia Asimétrica:** Procesos ultraligeros con desecho explícito de recursos y respetuosos del hilo principal.
4. **Dominio de Estado Agnóstico:** Consultas explícitas tipadas sin dumps ciegos de base de datos.
5. **Seguridad Defensiva y Forensia:** Validación Zero-Trust en frontera, trazabilidad por `X-Run-ID` y prohibición de bloques `catch` vacíos.

---

## 🛠️ Slash Commands Catalogue / Catálogo de Comandos Agénticos

Both in English and Spanish, ZNVE provides a unified suite of slash commands (`/znve-*`) supported across IDEs and Agents:

| Command / Comando | Scope / Propósito | Output / Entrega |
| :--- | :--- | :--- |
| `/znve-contract` | Platform-aware DTO & stack design | `contracts/[module].contract.[ts/py]` |
| `/znve-contract --delta` | Incremental analysis for existing code | Syncs contract & updates `CONTRACT_BACKLOG.md` |
| `/znve-execute` | Surgical code implementation | Writes exclusively to single `TARGET_FILE` |
| `/znve-forensic` | Read-only static diagnosis (Zero-Touch) | Root cause matrix without touching disk |
| `/znve-harness` | Golden Master characterization test suite | Isolated test in `tests/characterization/` |
| `/znve-hotfix` | Production crisis containment | Isolated patch inside adapter with `X-Run-ID` |
| `/znve-upgrade` | SDK/API dependency upgrade | Anti-Corruption Adapter shielding core app |
| `/znve-audit` | Resource, thread & noise cleanup | Purges thread locks, memory leaks & logs |

---

## 📂 Repository Layout / Estructura del Repositorio

```text
znve-spec/
├── .github/
│   └── copilot-instructions.md               <-- GitHub Copilot official instruction engine
├── case-studies/                             <-- Real-world validation cases
│   ├── 01-anti-bot-detection-lab/            <-- TLS JA3/JA4 & HTTP Header inspection
│   └── 02-legacy-monolith-rescue/            <-- Golden Master legacy modernization
├── contracts/                                <-- Master DTOs & Validation Schemas
├── protocols/                                <-- Master Operational Protocols
│   ├── ZNVE_PROTOCOL.md                      <-- Universal Master Protocol (6 Modes)
│   ├── ZNVE_ModernApps_Protocol.MD           <-- Incident Triage & Hotfix Protocol
│   ├── ZNVE_LEGACY_PROTOCOL.md               <-- 5-Phase Legacy Rescue Protocol
│   ├── GREENFIELD_STARTER.md                 <-- Quickstart guide for Day 0 projects
│   ├── ZNVE_CONTRACT_WORKFLOW.md             <-- Platform stack & Delta contract guide
│   ├── PROMPT_GUIDE.md                       <-- Generic prompt templates
│   ├── COMMANDS.md                           <-- Master Command Catalogue
│   ├── agents/                               <-- Multi-Provider Directives
│   │   ├── claude-system-skills.md           <-- Claude Projects & Claude Code CLI
│   │   ├── deepseek-directive.md             <-- DeepSeek R1/V3 Reasoner directive
│   │   ├── copilot-instructions.md           <-- Copilot mirror reference
│   │   ├── ollama/Modelfile                  <-- Deterministic Ollama Modelfile
│   │   └── openrouter/                       <-- OpenRouter unified JSON Schema & Prompt
│   └── mcp/                                  <-- Model Context Protocol Server
│       ├── package.json
│       ├── znve-mcp-server.ts                <-- stdio MCP server for IDEs
│       └── antigravity-config.example.json   <-- Antigravity / Cursor JSON config
├── rfcs/                                     <-- Request for Comments (IETF Governance)
├── CONTRIBUTING.md                           <-- Contribution Guidelines
├── LICENSE                                   <-- Dual License Terms (CC BY 4.0 + MIT)
├── README.md                                 <-- Project Portal (Bilingual)
├── SPECIFICATION.md                          <-- Formal Technical Specification v2.3.0
└── index.html                                <-- Interactive Landing Page (GitHub Pages)
```

---

## 🚀 Quick Start / Inicio Rápido

### English
1. **Copy Guardrails:** Copy `.cursorrules` (or `protocols/agents/claude-system-skills.md`) to your project root.
2. **Run Contract Command:** Issue `/znve-contract` specifying your target platform (e.g., Desktop, Web, Android, Hybrid).
3. **Approve & Execute:** Verify the 4-point solidity checklist, lock the contract, and run `/znve-execute` for surgical implementation.

### Español
1. **Copiar Barandillas:** Copia `.cursorrules` (o `protocols/agents/claude-system-skills.md`) en la raíz de tu proyecto.
2. **Ejecutar Comando de Contrato:** Envía `/znve-contract` indicando tu plataforma objetivo (ej. Escritorio, Web, Android, Híbrida).
3. **Aprobar y Ejecutar:** Verifica la lista de chequeo de solidez de 4 puntos, congela el contrato y ejecuta `/znve-execute` para la implementación quirúrgica.

---

## 📜 Dual License / Licenciamiento Dual

- **Specification & Documentation (`SPECIFICATION.md`, `ZNVE_PROTOCOL.md`, Manifestos):** Licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).
- **Code, Tooling, Schemas & MCP Server (`contracts/`, `protocols/mcp/`, `.cursorrules`, Scripts):** Licensed under the [MIT License](LICENSE).

---

<p align="center">
  <b>Zero-Noise Vibe Engineering (ZNVE)</b> — <i>Surgical Rigor in AI-Assisted Architecture</i>
</p>
