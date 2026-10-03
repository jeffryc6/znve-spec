# Zero-Noise Vibe Engineering (ZNVE) v2.3.0
> **Spec-Driven Agentic Architecture & Zero-Noise AI Software Engineering**
> *Arquitectura Agéntica Basada en Especificaciones e Ingeniería de Software IA Cero Ruido*

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](LICENSE)
[![Code License: MIT](https://img.shields.io/badge/Code%20License-MIT-green.svg)](LICENSE)
[![Standard: ZNVE v2.3.0](https://img.shields.io/badge/Standard-ZNVE%20v2.3.0-purple.svg)](SPECIFICATION.md)
[![Glossary](https://img.shields.io/badge/Glossary-ES%20%2F%20EN-lightgrey.svg)](GLOSSARY.md)
[![MCP Server](https://img.shields.io/badge/MCP%20Server-6%20tools-orange.svg)](protocols/mcp/)
[![Parity Check](https://github.com/jeffryc6/znve-spec/actions/workflows/znve-parity.yml/badge.svg)](.github/workflows/znve-parity.yml)

---

## 🌐 Language / Idioma
- 🇬🇧 [English Overview](#-english-overview)
- 🇪🇸 [Resumen en Español](#-resumen-en-español)

---

## 🇬🇧 English Overview

### What is ZNVE?
**Zero-Noise Vibe Engineering (ZNVE)** is an open, deterministic technical standard and agentic governance framework designed to eliminate **AI agentic drift** and **AI death loops** in AI-assisted software development.

Unlike casual "vibe coding", which leads to bloated dependencies, endless repair loops and degraded context windows, ZNVE establishes a **contract-first architecture**. Human developers act as **Directors of Architecture**, while AI models (Claude, Gemini, Cursor, Windsurf, Copilot, DeepSeek, Ollama, OpenRouter, Antigravity) operate as **surgical tactical executors**.

### Core Axioms
1. **Axiom 1 (Asymmetric Efficiency):** *Heavy intelligence in design; near-zero footprint during execution.*
2. **Axiom 2 (Deterministic Execution):** *The AI never invents architecture; it executes strict, pre-approved contracts.*

### The 5 Immutable Pillars
1. **Zero-Noise Operations:** Silent by default. No parasitic dependencies or routine logging (`"OK"`, `"DEBUG"`) in production.
2. **Contract-First AI:** Immutable DTOs and schemas (`contracts/`) defined *before* any implementation code.
3. **Asymmetric Efficiency:** Lightweight processes, deterministic resource disposal (`IDisposable`, `finally`, socket closure) and non-blocking threads.
4. **Agnostic State Domain:** Typed, explicit projections; no blind database or state dumps.
5. **Defensive Security & Forensics:** Zero-trust boundary validation, `X-Run-ID` traceability and no empty `catch`/`except` blocks.

### What's new in v2.3.0
- **Platform-aware stack analysis (`--platform`):** zero-bloat stacks for Desktop, Web, Hybrid, Android and iOS/macOS.
- **Solidity checklist & stop criterion:** the AI stops proposing once the contract passes the 4-point checklist.
- **Delta contracts (`/znve-contract --delta`):** Bucket A (needed now) vs. Bucket B (deferred to `CONTRACT_BACKLOG.md`).
- **Single source of truth (`znve-auto/`):** every assistant directive, the Claude and Antigravity skills and the command manuals are generated from `znve-auto/master_spec.json`, and CI fails on any drift.

---

## 🇪🇸 Resumen en Español

### ¿Qué es ZNVE?
**Zero-Noise Vibe Engineering (ZNVE)** es un estándar técnico abierto y un marco de gobernanza agéntica diseñado para eliminar la **degradación del contexto de la IA** (*agentic drift*) y los **bucles infinitos de reparación** en el desarrollo asistido por IA.

A diferencia del "vibe coding" caótico, que acumula librerías parásitas y código frágil, ZNVE establece una **arquitectura basada en contratos**. El desarrollador humano actúa como **Director de Arquitectura** y los modelos de IA (Claude, Gemini, Cursor, Windsurf, Copilot, DeepSeek, Ollama, OpenRouter, Antigravity) como **ejecutores tácticos quirúrgicos**.

### Axiomas centrales
1. **Axioma 1 (Eficiencia Asimétrica):** *Inteligencia pesada en el diseño; huella casi nula en la ejecución.*
2. **Axioma 2 (Ejecución Determinista):** *La IA no inventa arquitectura; ejecuta contratos estrictos previamente aprobados.*

### Los 5 pilares inmutables
1. **Operaciones Cero Ruido:** silencio operativo por defecto. Sin dependencias parásitas ni logs rutinarios (`"OK"`, `"Paso por aquí"`).
2. **Contratos Primero:** DTOs y esquemas inmutables (`contracts/`) definidos *antes* de escribir lógica de negocio.
3. **Eficiencia Asimétrica:** procesos ligeros, liberación determinista de recursos e hilos no bloqueantes.
4. **Dominio de Estado Agnóstico:** consultas tipadas con proyecciones explícitas, sin volcados ciegos.
5. **Seguridad Defensiva y Forense:** validación Zero-Trust en frontera, trazabilidad con `X-Run-ID` y prohibición de `catch` vacíos.

### Novedades de v2.3.0
- **Análisis de stack por plataforma (`--platform`):** stacks sin peso parásito para Escritorio, Web, Híbrida, Android e iOS/macOS.
- **Lista de chequeo de solidez y criterio de parada:** la IA deja de proponer en cuanto el contrato cumple los 4 puntos.
- **Contratos delta (`/znve-contract --delta`):** Cubo A (requerido ya) frente a Cubo B (diferido a `CONTRACT_BACKLOG.md`).
- **Fuente única de verdad (`znve-auto/`):** todas las directivas de los asistentes, las skills de Claude y Antigravity y los manuales de comandos se generan desde `znve-auto/master_spec.json`, y el CI falla ante cualquier desviación.

---

## 🛠️ Slash Commands / Comandos Agénticos

The same 10 commands work across every assistant. They can be written as `/znve-contract`, `/znve contract` or `/znve -contract`. Without a command, every technical answer follows 4 blocks: Blueprint & Contract → Rationale → Atomic Task → Verification.

Los mismos 10 comandos funcionan en todos los asistentes. Se escriben como `/znve-contract`, `/znve contract` o `/znve -contract`. Sin comando, toda respuesta técnica sigue 4 bloques: Blueprint y Contrato → Racional → Tarea Atómica → Verificación.

<!-- >>> znve:generated (znve-auto/builder.py desde master_spec.json; no editar a mano) -->
| Command / Comando | Mode / Modo | Purpose | Propósito |
| :--- | :--- | :--- | :--- |
| `/znve-help` | — | Operating manual and command index. | Manual operativo e índice de comandos. |
| `/znve-contract [--platform=desktop|web|mobile|hybrid] [--delta]` | 1, 2, 4 | Immutable interfaces, DTOs and Anti-Bloat Fence. | Diseño de interfaces inmutables, DTOs y Anti-Bloat Fence. |
| `/znve-execute --target=<ruta/archivo>` | 1, 2, 4, 5 | Atomic implementation in TARGET_FILE with resource disposal. | Implementación atómica en TARGET_FILE con desecho de recursos. |
| `/znve-triage` | 3 | Root-cause diagnosis and blast-radius containment. | Diagnóstico y contención de radio de impacto ante caídas. |
| `/znve-hotfix --incident=<ID>` | 3 | Atomic patch with mandatory regression test. | Parche quirúrgico atómico con test de regresión obligatorio. |
| `/znve-upgrade --dependency=<librería>` | 4 | Dependency migration behind a decoupled Adapter. | Migración de dependencias mediante Adaptador desacoplado. |
| `/znve-forensic --target=<ruta/módulo>` | 2, 5, 6 | Read-only ingestion, I/O matrix and side effects. | Ingesta en solo lectura, matriz I/O y efectos secundarios. |
| `/znve-harness --target=<archivo_legacy>` | 5 | Black-box Golden Master suite on intact code. | Suite Golden Master de caja negra sobre código intacto. |
| `/znve-legacy-rescue` | 5 | End-to-end 5-phase legacy orchestration. | Orquestación integral en 5 fases para código legacy. |
| `/znve-audit --target=<módulo>` | 6 | Hardening of threads, memory, descriptors and security. | Hardening de hilos, memoria, descriptores y seguridad. |
<!-- <<< znve:generated -->

Full manual with output formats, MCP tools and per-assistant setup / Manual completo con formatos de salida, herramientas MCP y configuración por asistente: [protocols/COMMANDS.md](protocols/COMMANDS.md).

---

## 🚀 Quick Start / Inicio Rápido

| Assistant / Asistente | Setup / Instalación |
| :--- | :--- |
| **Claude (claude.ai)** | Upload / Sube [`znve.zip`](protocols/agents/claude/skills/znve.zip) in *Settings → Capabilities → Skills* |
| **Claude Code** | Copy / Copia [`protocols/agents/claude/skills/znve/`](protocols/agents/claude/skills/znve/) to `~/.claude/skills/` |
| **Claude Projects** | Paste / Pega [`claude-system-skills.md`](protocols/agents/claude-system-skills.md) in *Project Instructions* |
| **Gemini (app & CLI)** | Upload / Sube [`gemini/skills/znve/`](protocols/agents/gemini/skills/znve/) in *Settings → Skills* · CLI: `gemini skills install` ([`INSTALL_GEMINI.md`](protocols/agents/gemini/INSTALL_GEMINI.md)) |
| **GitHub Copilot** | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) (already in place / ya incluido) |
| **Cursor / Windsurf** | Copy / Copia [`cursor-rules.md`](protocols/agents/cursor-rules.md) as / como `.cursorrules` |
| **DeepSeek** | [`deepseek-directive.md`](protocols/agents/deepseek-directive.md) as the `system` message / como mensaje `system` |
| **Ollama** | `ollama create znve-agent -f ./protocols/agents/ollama/Modelfile` |
| **OpenRouter** | [`system-prompt.md`](protocols/agents/openrouter/system-prompt.md) + [`response-schema.json`](protocols/agents/openrouter/response-schema.json) |
| **Antigravity** | [`INSTALL_ANTIGRAVITY.md`](protocols/Antigravity/Skills/INSTALL_ANTIGRAVITY.md) (skill) · [`ANTIGRAVITY_INSTALL.md`](protocols/mcp/ANTIGRAVITY_INSTALL.md) (MCP) |

### English
1. **Install ZNVE** in your assistant using the table above.
2. **Design the contract:** send `/znve-contract --platform=<desktop|web|mobile|hybrid>` with your requirement.
3. **Approve and execute:** check the 4-point solidity checklist, freeze the contract and run `/znve-execute --target=<file>`.

See [protocols/GREENFIELD_STARTER.md](protocols/GREENFIELD_STARTER.md) for a Day 0 walkthrough and [protocols/PROMPT_GUIDE.md](protocols/PROMPT_GUIDE.md) for ready-to-use prompts.

### Español
1. **Instala ZNVE** en tu asistente con la tabla anterior.
2. **Diseña el contrato:** envía `/znve-contract --platform=<desktop|web|mobile|hybrid>` con tu requerimiento.
3. **Aprueba y ejecuta:** verifica la lista de chequeo de 4 puntos, congela el contrato y ejecuta `/znve-execute --target=<archivo>`.

Consulta [protocols/GREENFIELD_STARTER.md](protocols/GREENFIELD_STARTER.md) para un recorrido de día 0 y [protocols/PROMPT_GUIDE.md](protocols/PROMPT_GUIDE.md) para prompts listos para usar.

---

## 📂 Repository Layout / Estructura del Repositorio

```text
znve-spec/
├── .github/
│   ├── copilot-instructions.md        <-- GitHub Copilot directive (generated)
│   └── workflows/znve-parity.yml      <-- CI: spec parity & drift check
├── case-studies/
│   └── 02-legacy-monolith-rescue/     <-- Golden Master legacy modernization
├── protocols/
│   ├── ZNVE_PROTOCOL.md               <-- Universal master protocol (6 modes)
│   ├── ZNVE_MODERN_APPS_PROTOCOL.md   <-- Modern apps: triage, hotfix & upgrades
│   ├── ZNVE_LEGACY_PROTOCOL.md        <-- 5-phase legacy rescue protocol
│   ├── GREENFIELD_STARTER.md          <-- Day 0 quickstart
│   ├── PROMPT_GUIDE.md                <-- Prompt templates per command
│   ├── COMMANDS.md                    <-- Full command & MCP manual (generated)
│   ├── agents/
│   │   ├── claude/skills/znve/        <-- Claude skill + znve.zip (generated)
│   │   ├── claude-system-skills.md    <-- Claude Projects / CLAUDE.md (generated)
│   │   ├── gemini/skills/znve/        <-- Gemini app & Gemini CLI skill (generated)
│   │   ├── copilot-instrucctions.md   <-- Copilot mirror (generated)
│   │   ├── cursor-rules.md            <-- Cursor / Windsurf rules (generated)
│   │   ├── deepseek-directive.md      <-- DeepSeek V3 / R1 (generated)
│   │   ├── ollama/Modelfile           <-- Ollama local agent (generated)
│   │   └── openrouter/                <-- System prompt (generated), JSON schema & client
│   ├── Antigravity/Skills/            <-- Antigravity skill, SDK module & installers
│   └── mcp/                           <-- stdio MCP server (6 tools) & Antigravity installer
├── rfcs/                              <-- Request for Comments
├── znve-auto/                         <-- Single source of truth: spec, builder & parity tests
├── CONTRIBUTING.md                    <-- Contribution guidelines
├── GLOSSARY.md                        <-- Technical glossary (ES/EN)
├── LICENSE                            <-- Dual license (CC BY 4.0 + MIT)
├── README.md                          <-- This file
├── SPECIFICATION.md                   <-- Formal technical specification v2.3.0
└── index.html                         <-- GitHub Pages landing page
```

---

## 🔁 Maintaining ZNVE / Mantenimiento

Commands, guardrails and the version live in [`znve-auto/master_spec.json`](znve-auto/master_spec.json). Files marked *generated* must not be edited by hand.

Los comandos, los guardrails y la versión viven en [`znve-auto/master_spec.json`](znve-auto/master_spec.json). Los archivos marcados como *generated* no se editan a mano.

```bash
python znve-auto/builder.py
```

```bash
python znve-auto/test_sync.py
```

```bash
cd protocols/mcp && npm ci && npm test
```

The first command regenerates every artifact; the second certifies parity; the third builds the MCP server and runs its regression suite. All of them run in CI on every push and pull request. Details in [znve-auto/README.md](znve-auto/README.md).

El primero regenera todos los artefactos; el segundo certifica la paridad; el tercero compila el servidor MCP y ejecuta su suite de regresión. Todos se ejecutan en el CI en cada push y pull request. Detalles en [znve-auto/README.md](znve-auto/README.md).

---

## 📜 Dual License / Licenciamiento Dual

- **Specification & documentation / Especificación y documentación** (`SPECIFICATION.md`, `README.md`, `GLOSSARY.md`, `CONTRIBUTING.md`, `rfcs/`, `case-studies/`): [CC BY 4.0](LICENSE).
- **Protocols / Protocolos** (`protocols/`: protocols, command manual, agent directives, skills, MCP server / protocolos, manual de comandos, directivas, skills, servidor MCP): [CC BY 4.0 **and** MIT](LICENSE). Both licenses apply together; use whichever fits / Ambas licencias a la vez; elige la que te convenga.
- **Repository tooling / Herramientas del repositorio** (`znve-auto/`, `.github/`, `copilot-instructions.md`, `index.html`): [MIT](LICENSE).

---

<p align="center">
  <b>Zero-Noise Vibe Engineering (ZNVE)</b> — <i>Surgical Rigor in AI-Assisted Architecture</i>
</p>
