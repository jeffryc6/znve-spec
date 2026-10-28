<!-- Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano. -->

# ZNVE v2.5.0: skill, plugin y servidor MCP para Codex y ChatGPT

La integración tiene tres piezas, todas en este repositorio:

```text
.agents/plugins/marketplace.json  <-- marketplace del repositorio (plugin "znve")
integrations/codex/
├── plugin.json                   <-- manifiesto del plugin (formato portable)
└── skills/
    ├── znve.zip                  <-- la skill empaquetada para subirla a ChatGPT
    └── znve/
        ├── SKILL.md              <-- instrucciones y catálogo de comandos
        ├── agents/openai.yaml    <-- nombre visible e invocación implícita
        └── references/
            └── chameleon-layer.md
integrations/mcp-server/
├── znve-mcp-server.ts            <-- servidor MCP "znve-engine" (stdio)
└── install-codex.mjs             <-- instalador para Codex
```

Referencias: [Skills y plugins](https://learn.chatgpt.com/docs/skills-and-plugins) · [Crear skills](https://learn.chatgpt.com/docs/build-skills) · [MCP en Codex](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) · [Crear plugins](https://developers.openai.com/plugins/build/plugins)

---

## 1. Codex CLI, extensión del IDE y app: instalador

Requisitos: Node.js 18 o superior.

```bash
cd integrations/mcp-server
node install-codex.mjs --workspace "<ruta>/tu-proyecto"
```

El instalador:

1. Compila el servidor (`npm ci` y `npm run build`).
2. Hace un handshake MCP real (`initialize` y `tools/list`) y comprueba que expone las herramientas de la especificación.
3. Escribe la tabla `[mcp_servers.znve-engine]` en `~/.codex/config.toml` dentro de un bloque delimitado (`# >>> znve-engine` / `# <<< znve-engine`) y guarda un backup del archivo anterior. El resto del archivo no se toca.
4. Copia la skill a `~/.agents/skills/znve/`.

Opciones:

| Opción | Efecto |
|---|---|
| `--project` | Usa `<workspace>/.codex/config.toml` y `<workspace>/.agents/skills/znve/` (Codex solo carga el `config.toml` de proyectos de confianza) |
| `--config <archivo>` | Escribe en otro `config.toml` |
| `--skills-dir <dir>` | Copia la skill a otra carpeta de skills |
| `--skip-skill` | Solo registra el servidor MCP |
| `--skip-build` | No ejecuta `npm ci` ni `npm run build` |
| `--dry-run` | Muestra el bloque que escribiría, sin escribir nada |
| `--uninstall` | Retira el bloque `znve-engine` y la skill copiada |

El bloque que se escribe es este (con rutas absolutas; la de `node` se fija porque Codex no siempre hereda el `PATH` del shell):

```toml
[mcp_servers.znve-engine]
command = "<ruta>/node"
args = ["<ruta>/znve-spec/integrations/mcp-server/dist/znve-mcp-server.js"]
startup_timeout_sec = 20

[mcp_servers.znve-engine.env]
ZNVE_WORKSPACE = "<ruta>/tu-proyecto"
NODE_ENV = "production"
```

Si ya tenías una tabla `[mcp_servers.znve-engine]` escrita a mano fuera del bloque, el instalador se detiene y te pide retirarla: no reescribe TOML ajeno.

Registro manual equivalente, sin el instalador:

```bash
codex mcp add znve-engine --env ZNVE_WORKSPACE="<ruta>/tu-proyecto" --env NODE_ENV=production -- node "<ruta>/znve-spec/integrations/mcp-server/dist/znve-mcp-server.js"
```

Comprueba el registro con `codex mcp list` y, dentro de una sesión, con `/mcp`.

---

## 2. Codex: plugin desde el marketplace del repositorio

```bash
codex plugin marketplace add jeffryc6/znve-spec
```

El marketplace (`.agents/plugins/marketplace.json`) ofrece el plugin `znve`, que contiene la skill. Para activarlo en un proyecto, añade a `.codex/config.toml`:

```toml
[plugins."znve@znve-spec"]
enabled = true
```

El plugin no incluye el servidor MCP: es un proceso local por stdio que necesita Node y la ruta de tu workspace. Regístralo con el instalador (`--skip-skill` si ya usas la skill del plugin, para no tenerla dos veces).

---

## 3. ChatGPT (web y app de escritorio)

1. Sube `integrations/codex/skills/znve.zip` como skill (una sola carpeta `znve/` en la raíz del zip).
2. Invócala con `@znve help` o deja que ChatGPT la elija cuando la petición coincida con su descripción.

ChatGPT web solo conecta servidores MCP remotos por HTTPS; `znve-engine` es local (stdio) y lee archivos de tu workspace, así que allí la skill funciona sin sus herramientas.

---

## 4. Uso

- `$znve help` muestra el catálogo; `$znve contract Diseña el DTO de usuario` abre el Modo 1.
- `znve-contract …` sin barra también vale. Evita `/znve-…` en Codex: la barra abre sus comandos internos.
- Con `znve-engine` activo, la skill usa `znve_validate_contract`, `znve_surgical_write`, `znve_audit_resources` y las demás herramientas en sus fases.
- Sin `ZNVE_WORKSPACE`, el servidor usaría el directorio desde el que Codex lo lanza; el instalador lo fija siempre.

## 🧠 Capa de Agente

Cada fase es una sesión. Las fases de diseño (`contract`, `forensic`, `triage`, `audit`) usan el modelo o nivel de razonamiento más alto disponible; las de ejecución (`execute`, `hotfix`, `harness`), el más rápido que cumpla el contrato. La configuración se elige al abrir la sesión. Solo cambia dentro de ella si el host lo permite sin reescribir el prefijo; si no, cambiar de modelo, de nivel de razonamiento, de herramientas o de esquema de salida invalida la caché. Al cerrar una fase verificada, recomienda el corte de sesión del perfil activo.

**Perfil activo: Codex y ChatGPT.**
- **Prefijo fijo:** `AGENTS.md` del proyecto y la skill `znve` (en `~/.agents/skills/znve/` o `.agents/skills/` del repositorio).
- **Invalida la caché:** editar `AGENTS.md` o la skill con la sesión abierta; activar o desactivar servidores MCP (`znve-engine`); cambiar de modelo o de nivel de razonamiento.
- **Corte de sesión:** sesión nueva (`/new`) al cerrar cada fase.
- **Configuración por fase:** `/model` al abrir la sesión, o un perfil por fase en `config.toml`.
- **Medición:** `cached_input_tokens`.

---

## 5. Actualizar y desinstalar

- Actualizar: `git pull` y vuelve a ejecutar `node install-codex.mjs` con las mismas opciones. Reinicia Codex: las skills y `config.toml` se leen al arrancar.
- Desinstalar: `node install-codex.mjs --uninstall` (añade `--project` si instalaste en el proyecto).
