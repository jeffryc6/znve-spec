# Zero-Noise Vibe Engineering (ZNVE)

[![Specification Version](https://img.shields.io/badge/spec-v1.1.0-00f2fe.svg)](SPECIFICATION.md)
[![Protocol Version](https://img.shields.io/badge/protocols-v2.2.0-10b981.svg)](protocols/ZNVE_PROTOCOL.md)
[![License: CC BY 4.0 & MIT](https://img.shields.io/badge/License-CC_BY_4.0_%2F_MIT-10b981.svg)](LICENSE)
[![Architecture: Contract--First](https://img.shields.io/badge/Architecture-Contract--First-111827.svg)](SPECIFICATION.md)

> **Axioma 1:** *"Inteligencia pesada en el diseño; huella casi nula en la ejecución."*
> **Axioma 2:** *"La IA no inventa arquitectura; ejecuta contratos deterministas."*

**Zero-Noise Vibe Engineering (ZNVE)** es una especificación técnica de arquitectura y gobernanza para el desarrollo asistido por agentes de IA (Contract-First Agentic Architecture). Transforma la velocidad conversacional del *vibe coding* en un estándar de ingeniería riguroso, asimétrico y libre de deuda técnica.

Abarca el ciclo de vida completo del software: desde la concepción en hoja limpia (*Greenfield*) hasta la contención de crisis en producción (*Hotfix*), rescate de monolitos (*Legacy Rescue*) y migración de dependencias modernas con *breaking changes*.

---

## 🎯 ¿Por qué ZNVE?

El *vibe coding* convencional delega decisiones críticas de diseño en modelos de lenguaje probabilísticos, generando:
- Acumulación masiva de paquetes y dependencias parásitas.
- Bloques `try/catch` vacíos o retrasos arbitrarios que enmascaran caídas en producción.
- Ruido operativo en logs, fugas de memoria y saturación del hilo principal de UI.
- Mutaciones no controladas en bases de código modernas al intentar corregir un bug puntual.

Bajo **ZNVE**, el desarrollador asume el rol de **Director de Arquitectura**, definiendo perímetros cerrados y contratos inmutables (DTOs, esquemas tipados, interfaces). Los agentes de IA (Claude, Cursor, Copilot, Windsurf, Antigravity) operan como compiladores sintácticos de precisión quirúrgica gobernados por contratos.

---

## 🏛️ Los 5 Pilares Inmutables

1. **Cero Ruido Operativo (Zero-Noise Operations & UX):** Prohibido el código muerto y las dependencias parásitas. Telemetría por excepción: nunca emitir confirmaciones rutinarias de estado saludable en rutas calientes; solo alertar ante anomalías confirmadas.
2. **Contratos Deterministas (Contract-First AI):** Ninguna IA genera código de producción sin un contrato previo tipado (DTO, interfaces, esquemas de validación).
3. **Eficiencia Asimétrica y Minimalismo:** *"Cerebro en el diseño, reflejo en el dispositivo"*. El hilo principal de UI nunca se bloquea; la memoria, sockets y handles se liberan deterministamente.
4. **Dominio de Estado y Persistencia Agnóstica:** Aplicable a motores relacionales (SQL), documentales (NoSQL), clave-valor, series temporales o almacenamiento local. Proyecciones de campos explícitos y rutas indexadas obligatorias.
5. **Seguridad Defensiva y Diagnóstico Forense:** Postura Zero-Trust. Validación estricta en frontera, erradicación de fallos hasta la causa raíz y prohibición expresa de silenciar excepciones.

---

## 🎛️ La Matriz de los 6 Modos Operativos

Antes de interactuar con el agente de IA, se declara el **MODO ACTIVO** de la intervención:

| Modo | Escenario de Aplicación | Protocolo Rector |
|---|---|---|
| 🟢 **Modo 1: Greenfield** | Creación de proyectos, módulos o servicios desde cero con base limpia. | `ZNVE_PROTOCOL.md` |
| 🔵 **Modo 2: In-Flight** | Proyectos activos: adición de funciones sin mutar contratos existentes. | `ZNVE_PROTOCOL.md` |
| 🟠 **Modo 3: Hotfix & Recovery** | Crisis en producción: contención de impacto, diagnóstico de causa raíz y parche atómico acotado. | `ZNVE_ModernApps_Protocol.MD` |
| 🟣 **Modo 4: Modern Maintenance** | Actualizaciones mayores de SDKs/APIs con *breaking changes* mediante adaptadores anti-corrupción. | `ZNVE_ModernApps_Protocol.MD` |
| 🟡 **Modo 5: Legacy Rescue** | Refactorización de monolitos críticos sin tests vía Golden Master y ejecución dual en sombra. | `ZNVE_LEGACY_PROTOCOL.md` |
| 🔴 **Modo 6: Audit & Hardening** | Mitigación de fugas de memoria, contención de sockets, hilos y auditoría de superficie. | `ZNVE_PROTOCOL.md` |

---

## 📂 Estructura del Repositorio

znve-spec/
├── .github/
│   └── copilot-instructions.md               <-- [4] GITHUB COPILOT (Ubicación oficial del motor)
├── case-studies/
│   ├── 01-anti-bot-detection-lab/
│   └── 02-legacy-monolith-rescue/
├── protocols/
│   ├── ZNVE_PROTOCOL.md                      <-- Protocolo universal maestro (6 Modos)
│   ├── ZNVE_ModernApps_Protocol.MD           <-- Protocolo de apps modernas (Hotfix/Upgrades)
│   ├── ZNVE_LEGACY_PROTOCOL.md               <-- Protocolo de rescate legacy (Golden Master)
│   ├── agents/                               <-- DIRECTIVAS Y SKILLS POR AGENTE
│   │   ├── claude-system-skills.md           <-- [Claude] Skills y comandos (/znve-*)
│   │   ├── deepseek-directive.md             <-- [1] DEEPSEEK (Modo Reasoner R1 / V3)
│   │   ├── copilot-instructions.md           <-- [4] COPILOT (Copia espejo referencial)
│   │   ├── ollama/
│   │   │   └── Modelfile                     <-- [2] OLLAMA (Modelfile determinista)
│   │   └── openrouter/
│   │       ├── system-prompt.md              <-- [3] OPENROUTER (Directiva de sistema unificada)
│   │       ├── response-schema.json          <-- [3] OPENROUTER (Structured Output JSON Schema)
│   │       └── znve-openrouter-client.ts     <-- [3] OPENROUTER (Cliente nativo Node/TS)
│   └── mcp/                                  <-- [5] SERVIDOR MCP PARA ANTIGRAVITY & IDEs
│       ├── package.json
│       ├── znve-mcp-server.ts                <-- Código fuente del servidor MCP stdio
│       ├── tsconfig.json
│       └── antigravity-config.example.json   <-- Configuración JSON para Antigravity/Cursor
├── rfcs/
│   ├── 0000-template.md
│   └── 0001-ios-swift-chameleon.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── SPECIFICATION.md
