<!-- Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano. -->

# Integraciones de ZNVE v2.3.0

Una carpeta por asistente. Las directivas, skills y guías se generan desde `znve-auto/master_spec.json`; el código (servidor MCP, cliente de OpenRouter, instaladores) y la integración de DeepSeek Harness se mantienen a mano.

| Carpeta | Asistente | Qué usar |
|---|---|---|
| [`claude/`](claude/) | Claude (claude.ai, Claude Code y Claude Projects) | `skills/znve/`, `skills/znve.zip` o `project-instructions.md` |
| [`gemini/`](gemini/) | Gemini (app y Gemini CLI) | `skills/znve/` y `INSTALL_GEMINI.md` |
| [`antigravity/`](antigravity/) | Google Antigravity (IDE, CLI y SDK) | `SKILL.md`, `INSTALL_ANTIGRAVITY.md` e instaladores |
| [`cursor/`](cursor/) | Cursor y Windsurf | `cursorrules.md` |
| [`deepseek/`](deepseek/) | DeepSeek (web, API y DeepSeek Harness) | `directive.md` y `harness/` |
| [`ollama/`](ollama/) | Ollama (modelos locales) | `Modelfile` |
| [`openrouter/`](openrouter/) | OpenRouter | `system-prompt.md`, `response-schema.json` y el cliente |
| [`mcp-server/`](mcp-server/) | Antigravity y otros clientes MCP | `znve-mcp-server.ts` e `install-antigravity.mjs` |

GitHub Copilot lee [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) en la raíz del repositorio.

## Instalación por asistente

### 1. Claude (claude.ai, Claude Code y Claude Projects)

- claude.ai: sube `integrations/claude/skills/znve.zip` en **Settings → Capabilities → Skills**.
- Claude Code: copia la carpeta `integrations/claude/skills/znve/` a `~/.claude/skills/` o a `.claude/skills/` del proyecto.
- Claude Projects: pega `integrations/claude/project-instructions.md` en **Project Instructions** o en `CLAUDE.md`.
- Invocación: `/znve-contract`, `/znve contract` o `/znve -contract`.

### 2. GitHub Copilot (VS Code, Visual Studio, JetBrains)

- Usa `.github/copilot-instructions.md`: es la ruta que Copilot lee.
- En el chat escribe `/znve-contract …` como texto normal: Copilot aplica las instrucciones del repositorio (no son slash commands nativos de Copilot).

### 3. Cursor y Windsurf

- Copia `integrations/cursor/cursorrules.md` a `.cursorrules` en la raíz del proyecto.

### 4. DeepSeek (web, API o extensión)

- Inyecta `integrations/deepseek/directive.md` como mensaje con rol `system`.
- En R1 (Reasoner), las 4 fases de validación ocurren dentro de `<think>`.

### 5. Ollama (modelos locales)

- Compila el agente local con el `Modelfile`:

```bash
ollama create znve-agent -f ./integrations/ollama/Modelfile
ollama run znve-agent
```

- Memoria: el KV cache crece con `num_ctx`; con `qwen2.5-coder:14b` a 32k tokens ronda los 6 GB (cálculo aproximado). `OLLAMA_FLASH_ATTENTION=1` y `OLLAMA_KV_CACHE_TYPE=q8_0` en el servidor lo reducen a la mitad.

### 6. Gemini (app web/Mac y Gemini CLI)

- App de Gemini: en **Settings → Skills → Upload**, sube la carpeta `integrations/gemini/skills/znve/`.
- Gemini CLI: `gemini skills install https://github.com/jeffryc6/znve-spec.git --path integrations/gemini/skills/znve`, o copia la carpeta a `~/.gemini/skills/` o a `.gemini/skills/` del proyecto.
- Invocación: `znve-contract …` sin barra en Gemini CLI (la CLI reserva `/`); en la app también vale `/znve-contract …`.
- Guía completa: `integrations/gemini/INSTALL_GEMINI.md`.

### 7. OpenRouter

- Usa `integrations/openrouter/system-prompt.md` como prompt de sistema y `response-schema.json` como `response_format`.

### 8. Antigravity y otros clientes MCP (Claude Desktop, Cursor, Windsurf)

- Antigravity: el instalador compila el servidor, verifica sus herramientas y registra `znve-engine`:

```bash
cd integrations/mcp-server
node install-antigravity.mjs --workspace "<ruta>/tu-proyecto"
```

- Registro manual: compila con `npm ci && npm run build` y añade este bloque `mcpServers` al archivo de configuración de tu cliente:

```json
{
  "mcpServers": {
    "znve-engine": {
      "command": "node",
      "args": ["<ruta>/znve-spec/integrations/mcp-server/dist/znve-mcp-server.js"],
      "env": {
        "ZNVE_WORKSPACE": "<ruta>/tu-proyecto",
        "NODE_ENV": "production"
      }
    }
  }
}
```

- Antigravity: `~/.gemini/antigravity/mcp_config.json` (o **Manage MCP Servers → View raw config**).
- Claude Desktop: `claude_desktop_config.json` (**Settings → Developer → Edit Config**).
- Cursor: `.cursor/mcp.json` en el proyecto o `~/.cursor/mcp.json` global.
- Windsurf: `~/.codeium/windsurf/mcp_config.json`.
