# ZNVE MCP Server: instalación en Google Antigravity

Servidor MCP por **stdio** (`@modelcontextprotocol/sdk`) que expone 6 herramientas:
`znve_help`, `znve_forensic_scan`, `znve_validate_contract`, `znve_scaffold_harness`,
`znve_surgical_write` y `znve_audit_resources`.

Referencias: [Model Context Protocol](https://modelcontextprotocol.io) ·
[Antigravity SDK: MCP](https://antigravity.google/docs/sdk/mcp/#model-context-protocol-mcp-integration) ·
[mcp_tools.py](https://github.com/google-antigravity/antigravity-sdk-python/blob/main/examples/getting_started/mcp_tools.py)

Este documento cubre el **servidor MCP**. Para instalar la **skill** `znve` (instrucciones de sistema y comandos `/znve-*`) en Antigravity, consulta [INSTALL_ANTIGRAVITY.md](../Antigravity/Skills/INSTALL_ANTIGRAVITY.md). Ambas piezas se complementan: la skill le enseña la metodología al agente y el servidor MCP le da las barandillas físicas.

---

## Por qué "se instalaba pero no pasaba nada"

| Causa | Efecto | Corrección |
|---|---|---|
| El config apuntaba a `protocols/mcp/znve-mcp-server.js`, que no existe. `tsc` compila a `dist/`. | Node falla al arrancar y Antigravity muestra el servidor sin herramientas. | `args` → `.../protocols/mcp/dist/znve-mcp-server.js` |
| El `.ts` nunca se compilaba (no había `node_modules/` ni `dist/`). | No existía ningún JS que ejecutar. | El auto-installer ejecuta `npm ci` + `npm run build`. |
| Las rutas se resolvían contra `process.cwd()`. Antigravity lanza el proceso con un cwd arbitrario. | `znve_help` devolvía el fallback y `znve_forensic_scan` no encontraba los archivos. | Nueva variable `ZNVE_WORKSPACE`. `COMMANDS.md` se busca relativo al propio servidor. |
| `"command": "node"` depende del `PATH` del IDE. | Con nvm, fnm o Volta el IDE no encuentra `node`. | El installer escribe la ruta absoluta de `node`. |

---

## 1. Auto-installer (recomendado)

Requisitos: **Node.js ≥ 18** y **npm**.

```bash
cd protocols/mcp
node install-antigravity.mjs --workspace "D:/ruta/a/tu-proyecto"
```

Qué hace, en orden (aborta en el primer fallo):

1. `npm ci` (o `npm install` si no hay lockfile).
2. `npm run build`, que genera `dist/znve-mcp-server.js`.
3. **Smoke test MCP real**: arranca el servidor desde un cwd ajeno y envía `initialize` → `notifications/initialized` → `tools/list`. Exige exactamente las 6 herramientas que declara `znve-auto/master_spec.json` y que stdout no tenga ruido fuera de JSON-RPC.
4. Localiza el `mcp_config.json` de Antigravity. Usa el primero que exista:
   - `~/.gemini/antigravity-ide/mcp_config.json`
   - `~/.gemini/antigravity/mcp_config.json` (se crea si no existe ninguno)
5. Guarda un backup (`mcp_config.json.bak-<timestamp>`) y **fusiona** la entrada `znve-engine`. Los demás servidores quedan intactos.

Después, en Antigravity: **panel Agent → menú `…` → MCP Servers → Manage MCP Servers → Refresh**.
`znve-engine` debe aparecer con 6 herramientas.

### Opciones

| Flag | Descripción | Default |
|---|---|---|
| `--workspace <dir>` | Raíz contra la que se resuelven `file_path`, `target_file` y `harness_directory`. | raíz de `znve-spec` |
| `--config <file>` | Ruta explícita del `mcp_config.json`. | autodetectado |
| `--name <id>` | Clave dentro de `mcpServers`. | `znve-engine` |
| `--skip-build` | No ejecuta npm (requiere `dist/` ya compilado). | — |
| `--dry-run` | Compila y verifica, pero no escribe el config. Solo imprime la entrada `znve-engine`. | — |
| `--uninstall` | Elimina la entrada del config (con backup). | — |

Atajos npm: `npm run install:antigravity` · `npm run uninstall:antigravity`.

### Prompt de auto-instalación para el agente de Antigravity

Pega esto en el chat del agente de Antigravity con el repo `znve-spec` abierto:

> Instala el servidor MCP de ZNVE. Ejecuta en la terminal:
> `cd protocols/mcp && node install-antigravity.mjs --workspace "<RUTA_ABSOLUTA_DE_MI_PROYECTO>"`.
> Si el comando termina con `[znve-install] Listo`, pídeme que refresque **Manage MCP Servers**.
> Si falla, muéstrame la línea `ERROR:` y no edites `mcp_config.json` a mano.

---

## 2. Instalación manual (IDE)

```bash
cd protocols/mcp
npm ci
npm run build
```

Añade esto dentro de `mcpServers` en `mcp_config.json`. También puedes abrirlo desde **Manage MCP Servers → View raw config**. Usa rutas absolutas con `/`:

```json
{
  "mcpServers": {
    "znve-engine": {
      "command": "C:/Program Files/nodejs/node.exe",
      "args": ["D:/ruta/a/znve-spec/protocols/mcp/dist/znve-mcp-server.js"],
      "env": {
        "ZNVE_WORKSPACE": "D:/ruta/a/tu-proyecto",
        "NODE_ENV": "production"
      }
    }
  }
}
```

Plantilla: [`antigravity-config.example.json`](antigravity-config.example.json).

---

## 3. Antigravity SDK (Python, programático)

El SDK no lee `mcp_config.json`. Los servidores se declaran con `types.McpStdioServer` dentro de `LocalAgentConfig`:

```python
znve = types.McpStdioServer(
    name="znve-engine",
    command="node",
    args=["/ruta/a/znve-spec/protocols/mcp/dist/znve-mcp-server.js"],
    env={"ZNVE_WORKSPACE": "/ruta/a/tu-proyecto"},
)
config = LocalAgentConfig(mcp_servers=[znve], policies=[...])
```

Ejemplo completo con políticas (solo lectura por defecto, escritura denegada):
[`antigravity_sdk_example.py`](antigravity_sdk_example.py).

```bash
pip install google-antigravity
python protocols/mcp/antigravity_sdk_example.py
```

---

## Diagnóstico

| Síntoma | Comprobación |
|---|---|
| El servidor aparece en rojo o sin herramientas | `node install-antigravity.mjs --dry-run --skip-build` repite el handshake y muestra el error. |
| `Cannot find module .../dist/...` | Falta el build: `npm run build`. |
| `znve_help` devuelve `[ZNVE_HELP_FALLBACK]` | No encuentra `protocols/COMMANDS.md`. No muevas `dist/` fuera del repo. |
| Los archivos "no existen" | Revisa `ZNVE_WORKSPACE`. El log de arranque (stderr) imprime `[znve-mcp] listo (stdio). Workspace: …`. |
| `… queda fuera de ZNVE_WORKSPACE` | Barandilla, no fallo: las herramientas solo leen y escriben dentro del workspace (también a través de enlaces), y `znve_scaffold_harness` solo bajo `tests/` o `sandbox/`. Apunta `ZNVE_WORKSPACE` al proyecto correcto. |
| Cambiaste el `.ts` | `npm run build` y **Refresh** en Manage MCP Servers. |

> Regla stdio: **stdout está reservado para JSON-RPC.** Cualquier `console.log` en el servidor rompe el protocolo. Usa `process.stderr.write`.
