# GREENFIELD STARTER: ZERO-NOISE VIBE ENGINEERING (ZNVE)
**Plantilla de Inicio Rápido para Proyectos Nuevos (Día 0)**
*Versión: 2.4.0 | Estándar: Spec-Driven Agentic Architecture | Modo 1 de [ZNVE_PROTOCOL.md](ZNVE_PROTOCOL.md)*

---

## 🎯 PROPÓSITO
Esta plantilla proporciona la estructura mínima inviolable y el conjunto de comandos necesarios para **iniciar un proyecto nuevo con el pie derecho**. Elimina el "bucle de muerte de la IA" (*AI agentic drift*), previene la inyección de dependencias parásitas y asegura que el desarrollo avance con contratos deterministas desde la primera línea de código.

---

## 📂 ESTRUCTURA MÍNIMA DEL PROYECTO (REPO LAYOUT)

```text
my-new-project/
├── .cursorrules                       <-- Directiva agéntica (Cursor / Windsurf), o la de tu asistente
├── contracts/                         <-- FRONTERA DE DATOS (Contratos inmutables)
│   ├── [modulo].contract.ts           <-- DTOs e Interfaces del módulo
│   ├── schemas/                       <-- Esquemas de validación (Zod / TypeBox / Pydantic)
│   └── CONTRACT_BACKLOG.md            <-- Ideas diferidas (Cubo B)
├── src/                               <-- CÓDIGO QUIRÚRGICO DE IMPLEMENTACIÓN
│   └── ...                            <-- Archivos objetivo (TARGET_FILE)
├── tests/                             <-- BATERÍA DE VERIFICACIÓN ATÓMICA
│   └── unit/                          <-- Pruebas de contrato y no-regresión
└── README.md                          <-- Documentación y comandos de arranque
```

---

## 🚀 FLUJO DE INICIO RÁPIDO EN 4 PASOS (GREENFIELD WORKFLOW)

```text
┌─────────────────────────────────────────────────────────────┐
│ PASO 1: INSTALAR ZNVE EN TU ASISTENTE                       │
│        --> Skill, directiva o servidor MCP (ver tabla).     │
├─────────────────────────────────────────────────────────────┤
│ PASO 2: ISLA DE ALCANCE (ANTI-BLOAT FENCE)                  │
│        --> Delimitar qué resuelve el MVP y vetar paquetes.  │
├─────────────────────────────────────────────────────────────┤
│ PASO 3: CONTRATO PRIMERO (/znve-contract --platform=...)    │
│        --> DTOs en contracts/ + lista de chequeo de 4       │
│            puntos + criterio de parada.                     │
├─────────────────────────────────────────────────────────────┤
│ PASO 4: EJECUCIÓN ATÓMICA (/znve-execute --target=...)      │
│        --> Implementar únicamente en TARGET_FILE y          │
│            ejecutar la prueba de verificación.              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ PASO A PASO: DEL PROMPT AL CÓDIGO PRODUCTIVO

### Paso 1: Instalar ZNVE en tu asistente

| Asistente | Qué usar |
|---|---|
| Claude (claude.ai) | Sube `integrations/claude/skills/znve.zip` en *Settings → Capabilities → Skills*. |
| Claude Code | Copia `integrations/claude/skills/znve/` a `~/.claude/skills/` o a `.claude/skills/` del proyecto. |
| Claude Projects | Pega `integrations/claude/project-instructions.md` en *Project Instructions* o en `CLAUDE.md`. |
| Gemini (app y CLI) | Sube la carpeta `integrations/gemini/skills/znve/` en *Settings → Skills*, o en Gemini CLI: `gemini skills install`. Ver `integrations/gemini/INSTALL_GEMINI.md`. |
| GitHub Copilot | Copia `.github/copilot-instructions.md` a tu proyecto. |
| Cursor / Windsurf | Copia `integrations/cursor/cursorrules.md` como `.cursorrules`. |
| DeepSeek / OpenRouter / Ollama | `integrations/deepseek/directive.md`, `integrations/openrouter/system-prompt.md` u `integrations/ollama/Modelfile`. |
| Antigravity | Skill: `integrations/antigravity/INSTALL_ANTIGRAVITY.md`. MCP: `integrations/mcp-server/ANTIGRAVITY_INSTALL.md`. |

Comprueba la instalación escribiendo `/znve-help`: debe aparecer el catálogo de 10 comandos.

### Paso 2: Declarar el Perímetro y el Contrato Inicial (MODO 1)
Envía este prompt a tu asistente de IA:

```text
/znve-contract --platform=[desktop|web|mobile|hybrid]
Bajo ZNVE Modo 1 (Greenfield), vamos a iniciar el desarrollo del módulo [NOMBRE_DEL_MÓDULO].

1. Delimita el Anti-Bloat Fence: por defecto, solo APIs nativas del runtime/SDK. Una librería de terceros solo entra como excepción justificada (el SDK nativo no ofrece la capacidad; documenta qué resuelve, su peso y la alternativa nativa descartada).
2. Recomienda el stack para la plataforma y diseña el contrato DTO y la interfaz de datos inmutable en `contracts/[modulo].contract.ts`.
3. Aplica la lista de chequeo de solidez y, si se cumple, emite el criterio de parada.
4. No escribas código de implementación todavía. Espera mi aprobación del contrato.
```

### Paso 3: Revisión y Congelación del Contrato
Aprueba el contrato solo si cumple la **lista de chequeo de solidez**:
- [ ] **Estructura invariable:** entradas, salidas, entidades y enums tipados.
- [ ] **Defensas de frontera:** tipos de error explícitos (enums o uniones discriminadas), sin `any` ni `catch` genéricos.
- [ ] **Cero dependencias parásitas:** solo el SDK nativo, el runtime aprobado o una excepción justificada en la Anti-Bloat Fence.
- [ ] **Filtro de diferimiento:** ideas secundarias movidas a `contracts/CONTRACT_BACKLOG.md`.

Con los 4 puntos cumplidos, la IA debe responder *"Contrato v1 sólido y cerrado. Listo para /znve-execute."* y dejar de proponer cambios.

### Paso 4: Orden de Ejecución Quirúrgica
Una vez aprobado el contrato, ordena la implementación:

```text
/znve-execute --target=src/[modulo]/[servicio].ts
Contrato aprobado. Implementa la lógica interna.

RESTRICCIONES ESTRICTAS:
- TARGET_FILE exclusivo: `src/[modulo]/[servicio].ts`.
- Aplica desecho determinista de recursos (finally / dispose / close).
- Prohibidos bloques try/catch vacíos.
- Incluye el comando de verificación atómica ejecutable.
```

Para añadir capacidades más adelante, usa `/znve-contract --delta` (Modo 2): la IA separa lo requerido ya (Cubo A) de lo diferido (Cubo B) antes de tocar código.

---

## 📋 VERIFICACIÓN DE SALIDA OBLIGATORIA (RESPUESTA EN 4 BLOQUES)

Toda consulta técnica sin comando debe responderse con la siguiente estructura:

1. **BLOQUE 1: SYSTEM BLUEPRINT & CONTRATO:** Delimitación de alcance, plataforma objetivo y contrato inmutable (`contracts/`).
2. **BLOQUE 2: RACIONAL DE INGENIERÍA:** 2-3 viñetas justificando la huella mínima de CPU/RAM y la ausencia de dependencias parásitas.
3. **BLOQUE 3: TAREAS ATÓMICAS DE IMPLEMENTACIÓN:** `TARGET_FILE` único, acción quirúrgica y restricciones aplicadas.
4. **BLOQUE 4: VERIFICACIÓN ATÓMICA:** Comando terminal ejecutable o prueba unitaria (`tests/unit/`) para certificar el funcionamiento.

---

## 🛡️ LISTA DE CHEQUEO DÍA 0 (GREENFIELD CHECKLIST)

- [ ] ZNVE instalado en el asistente y `/znve-help` responde con el catálogo.
- [ ] Directorio `contracts/` creado con DTOs/interfaces aprobados y `CONTRACT_BACKLOG.md` para lo diferido.
- [ ] Cero dependencias externas agregadas a `package.json` / `requirements.txt` / `Cargo.toml`, salvo excepciones justificadas en la Anti-Bloat Fence.
- [ ] Pruebas unitarias de frontera ejecutadas y en verde.
- [ ] Cero logs de confirmación rutinaria (`"OK"`, `"Success"`) en el código de producción.
