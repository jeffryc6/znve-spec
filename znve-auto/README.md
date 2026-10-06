# znve-auto: fuente única de verdad de ZNVE

`master_spec.json` define la versión, los axiomas, los guardrails, los escenarios, los 10 comandos, la Capa Camaleónica, las herramientas MCP y los flujos. `builder.py` genera con ella todas las directivas de los asistentes. Solo usa la biblioteca estándar de Python (3.10 o superior).

## Uso

```bash
python znve-auto/builder.py
```

Genera o sincroniza los artefactos. Solo reescribe los que cambian.

```bash
python znve-auto/builder.py --verify
```

Compara sin escribir y sale con código 1 si algún artefacto no coincide. Añade `--diff` para ver las diferencias.

```bash
python znve-auto/test_sync.py
```

Ejecuta la suite de paridad. Es lo que corre el workflow `.github/workflows/znve-parity.yml` en cada push y pull request a `main`.

## Cómo cambiar un comando o una regla

1. Edita `master_spec.json`. Para cambiar la redacción propia de una plataforma, edita su plantilla en `templates/`.
2. Ejecuta `python znve-auto/builder.py`.
3. Ejecuta `python znve-auto/test_sync.py` y haz commit de la especificación junto con los artefactos regenerados.

No edites los archivos generados: llevan un aviso en la cabecera y el CI falla si se desvían de la especificación.

## Qué genera

| Plantilla | Artefacto |
|---|---|
| `claude_skill.md.tmpl` | `integrations/claude/skills/znve/SKILL.md` |
| `chameleon_layer.md.tmpl` | `integrations/claude/skills/znve/references/chameleon-layer.md` |
| (paquete) | `integrations/claude/skills/znve.zip`, reproducible byte a byte |
| `claude_project.md.tmpl` | `integrations/claude/project-instructions.md` |
| `copilot_instructions.md.tmpl` | `.github/copilot-instructions.md` (única copia: es la ruta que lee Copilot) |
| `cursor_rules.md.tmpl` | `integrations/cursor/cursorrules.md` (en inglés) |
| `deepseek_directive.md.tmpl` | `integrations/deepseek/directive.md` (web y API) |
| `deepseek_harness_agents.md.tmpl` | `integrations/deepseek/harness/AGENTS.md` (global de DeepSeek Harness; el target declara `max_bytes`) |
| `ollama_modelfile.tmpl` | `integrations/ollama/Modelfile` |
| `openrouter_system.md.tmpl` | `integrations/openrouter/system-prompt.md` |
| `antigravity_skill.md.tmpl` | `integrations/antigravity/SKILL.md` |
| `commands_manual.md.tmpl` | `protocols/COMMANDS.md` (manual que sirve `znve_help` del MCP) |
| `antigravity_install.md.tmpl` | `integrations/antigravity/INSTALL_ANTIGRAVITY.md` |
| `gemini_skill.md.tmpl` | `integrations/gemini/skills/znve/SKILL.md` (app de Gemini y Gemini CLI) |
| `chameleon_layer.md.tmpl` | `integrations/gemini/skills/znve/references/chameleon-layer.md` |
| `gemini_install.md.tmpl` | `integrations/gemini/INSTALL_GEMINI.md` |
| `integrations_index.md.tmpl` | `integrations/README.md` (índice: qué archivo usar en cada asistente) |

Cada target admite dos campos opcionales: `agent` (id de un perfil de `agent_profiles`; la plantilla recibe `{{agent_layer_md}}`, `{{agent_layer_plain}}`, `{{agent_layer_en}}` y `{{agent_layer_body_md}}` con la regla común de fases y **solo el perfil de ese asistente**; un target sin `agent` que use esos marcadores falla) y `max_bytes` (presupuesto del artefacto, comprobado por test).

Además de las plantillas hay dos tipos de artefacto:

- **Bloques gestionados (`regions`).** En un archivo escrito a mano, el builder solo reescribe lo que hay entre `>>> znve:generated[:nombre]` y `<<< znve:generated[:nombre]`; el resto se mantiene a mano.
  - `integrations/antigravity/znve_skill.py`: nombre, versión, instrucción de sistema, catálogo de `/znve-help` y modos. Las herramientas se mantienen a mano. `Auto_Installer.py` e `install_znve_global.py` importan esas constantes, así que no llevan copias propias.
  - `integrations/mcp-server/znve-mcp-server.ts` y `integrations/antigravity/znve_skill.py`: el bloque `secrets` (lista de secretos denegada y permitida, de `secrets` en la especificación; una sola fuente para las dos implementaciones).
  - `integrations/mcp-server/znve-mcp-server.ts`: tres bloques más. La cabecera (versión de ZNVE y axiomas, dentro de `/** ... */`), `fallback` (catálogo corto de `znve_help` si falta el manual) y `tools` (`TOOL_DOCS`: descripciones de las herramientas y de sus parámetros, desde `mcp.tools`).
  - `README.md`, `SPECIFICATION.md` e `index.html`: el catálogo de comandos.
- **Paquetes (`bundles`).** `znve.zip` reúne la carpeta de la skill de Claude, reproducible byte a byte. Las cachés y los archivos ocultos (`__pycache__`, `*.pyc`, `.DS_Store`) nunca entran.
- **Copias (`mirrors`).** `integrations/antigravity/.agents/skills/znve/` contiene `SKILL.md` y `scripts/znve_skill.py`, copias exactas de los originales: es el mismo árbol que deja `Auto_Installer.py` en cada proyecto.

Las plantillas que empiezan por `_` son fragmentos compartidos: se incluyen con `{{> _nombre.md.tmpl}}`. Los bloques calculados desde la especificación se insertan con `{{clave}}`; la lista completa está en `build_context()` de `builder.py`.

## Qué verifica `test_sync.py`

- La especificación: nombre `znve`, versión SemVer, comandos únicos y 6 modos más ayuda.
- Que ningún artefacto se haya desviado de la especificación.
- Que cada directiva mencione los 10 comandos y cite una sola versión de ZNVE.
- Que cada directiva con guardrails los lleve todos y en orden, con la regla común de fases de la Capa de Agente, y que los ajustes de comandos (salida mínima, dos pasos, rangos, Zona Roja) estén en la especificación.
- Que cada directiva con guardrails incluya el de Verificación Inviolable, que `SPECIFICATION.md`, `GLOSSARY.md` e `index.html` citen el número real de guardrails y que la salida de `/znve-harness` conserve el determinismo del Golden Master y la verificación en dos pasos.
- Que no queden marcas `[cite: N]`, vallas ` ```markdown ` iniciales ni enlaces `utm_source`.
- Que las skills de Claude y Gemini cumplan las reglas de subida (claves del frontmatter, nombre en minúsculas con guiones, descripción de hasta 1024 caracteres) y que sus enlaces a `references/` apunten a archivos generados.
- Que las herramientas MCP documentadas sean las que expone `integrations/mcp-server/znve-mcp-server.ts` y que `protocols/COMMANDS.md` conserve las secciones que filtra `znve_help`.
- Que el enum de escenarios de `integrations/openrouter/response-schema.json` coincida con la especificación.
- Que los artefactos con `max_bytes` en `targets` respeten su presupuesto (un global grande, como el `AGENTS.md` de DeepSeek Harness, compite con los proyectos y DSH puede descartarlo), que los guardrails, el bloque de Capa de Agente y las descripciones de las herramientas MCP respeten los suyos, y que ningún artefacto generado contenga fechas ni rutas del host (prefijo estable).
- Que cada target con `agent` use un perfil existente, que todo perfil se use, que los perfiles no tengan cifras en español (caducan) y que cada artefacto lleve su perfil y ninguno de los otros.
- Que el bloque de `GEMINI.md` de `install_znve_global.py` sea estático y no repita el catálogo de comandos.
- Que `install-dsh.ps1` no lleve versiones de ZNVE escritas a mano y que, ejecutado contra un `$DSH_HOME` temporal, instale la directiva como bloque sin tocar el resto del `AGENTS.md`, sea idempotente, migre una instalación antigua y no borre un global ajeno al desinstalar. Se omite si no hay PowerShell.
- Que las herramientas de `znve_skill.py` cumplan sus barandillas: contención en `ZNVE_WORKSPACE` (o el cwd), arnés solo bajo `tests/` o `sandbox/` y que solo crea (nunca sobrescribe), escritura atómica y sin `.git/` ni `node_modules/`, detección de `catch`/`except` que silencian errores, importaciones vetadas, consultas ciegas y bloqueos.
- Que `znve.zip` excluya las cachés y los archivos ocultos.
- Que `znve_skill.py` exponga la versión y el catálogo de la especificación, que la skill se llame `znve` y tenga 6 herramientas, que `get_znve_skill()` entregue las 6 herramientas con docstring, que `Auto_Installer.py` instale en `.agents/skills/znve/` y retire la instalación de `.antigravity/`, que `install_znve_global.py` instale en `~/.gemini/config/skills/znve/` y retire la copia legacy, y que reemplace la regla de `GEMINI.md` sin duplicarla.

Al final avisa, sin fallar, de los archivos mantenidos a mano (`.md`, `.py`, `.ts`, `.json`, `.html`, `.mjs` y `.ps1`) que citan otra versión de ZNVE.

El comportamiento del servidor MCP se prueba aparte, con su propia suite (`node:test`, sin dependencias). Arranca el servidor por stdio contra un workspace temporal y cubre contención de rutas, validación de argumentos, barandillas, anotaciones y que `tools/list` coincida con `mcp.tools`:

```bash
cd integrations/mcp-server && npm ci && npm test
```

El workflow de CI ejecuta las dos suites y, además, `npm run check:openrouter` (type-check del cliente de OpenRouter).
