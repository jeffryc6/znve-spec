# ZNVE v2.6.0 en Gemini / Antigravity

<!-- Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano. -->

La skill contiene instrucciones; el único motor ejecutable es el MCP compartido de `integrations/mcp-server/`. No hay implementación Python alternativa.

## 🧠 Capa de Agente

Cada fase es una sesión. Las fases de diseño (`contract`, `forensic`, `triage`, `audit`) usan el modelo o nivel de razonamiento más alto disponible; las de ejecución (`execute`, `hotfix`, `harness`), el más rápido que cumpla el contrato. La configuración se elige al abrir la sesión. Solo cambia dentro de ella si el host lo permite sin reescribir el prefijo; si no, cambiar de modelo, de nivel de razonamiento, de herramientas o de esquema de salida invalida la caché. Al cerrar una fase verificada, recomienda el corte de sesión del perfil activo.

**Perfil activo: Antigravity (IDE, CLI y SDK).**
- **Prefijo fijo:** `~/.gemini/GEMINI.md` y la skill `znve` (en `.agents/skills/` del proyecto o global).
- **Invalida la caché:** editar reglas con la conversación abierta; activar o desactivar servidores MCP (`znve-engine`); cambiar de modelo.
- **Corte de sesión:** conversación nueva al cerrar cada fase.
- **Configuración por fase:** selector de modelo al abrir la conversación.
- **Medición:** no visible en el cliente.

Desde `integrations/mcp-server/`:

```text
npm ci
npm test
node install-antigravity.mjs --workspace "<proyecto>"
```

El instalador registra `znve-engine` y hace un handshake real; no certifica el SDK de Antigravity ni el comportamiento del modelo. Copia `SKILL.md` a la carpeta de skills que tu host admita, sin instalar los antiguos scripts Python. Comprueba las rutas globales en la documentación de tu host.

## Migración desde Python

`znve_skill.py`, `Auto_Installer.py`, `install_znve_global.py` y `agent.py` fallan con `ZNVE_MIGRATION_REQUIRED`. Las copias instaladas fuera de este repositorio no se modifican: retira su registro después de comprobar el MCP. No registres ambos motores a la vez.

`../mcp-server/antigravity_sdk_example.py` conecta al mismo MCP con política de solo lectura. Sin ejecución contra el SDK real: **NO INTEGRADO con ese SDK**.

## Uso 2.5

`znve spec` diseña; `znve verify` usa runner/gate. `znve checkpoint` / `znve resume` conservan pendientes y vigencia. Preflight identifica recursos ausentes antes de repetir búsquedas. Un walkthrough escrito por el modelo no es evidencia ejecutada.

Consulta `../../protocols/VERIFICATION.md` y `../../protocols/MEMORY_AND_HANDOFF.md`. Sin MCP declara modo de instrucciones, sin inventar resultados.
