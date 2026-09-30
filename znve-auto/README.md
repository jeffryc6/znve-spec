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
| `claude_skill.md.tmpl` | `protocols/agents/claude/skills/znve/SKILL.md` |
| `chameleon_layer.md.tmpl` | `protocols/agents/claude/skills/znve/references/chameleon-layer.md` |
| (paquete) | `protocols/agents/claude/skills/znve.zip`, reproducible byte a byte |
| `claude_project.md.tmpl` | `protocols/agents/claude-system-skills.md` |
| `copilot_instructions.md.tmpl` | `.github/copilot-instructions.md`, `copilot-instructions.md` y `protocols/agents/copilot-instrucctions.md` |
| `cursor_rules.md.tmpl` | `protocols/agents/cursor-rules.md` (en inglés) |
| `deepseek_directive.md.tmpl` | `protocols/agents/deepseek-directive.md` |
| `ollama_modelfile.tmpl` | `protocols/agents/ollama/Modelfile` |
| `openrouter_system.md.tmpl` | `protocols/agents/openrouter/system-prompt.md` |
| `antigravity_skill.md.tmpl` | `protocols/Antigravity/Skills/SKILL.md` |
| `commands_manual.md.tmpl` | `protocols/COMMANDS.md` (manual que sirve `znve_help` del MCP) |
| `antigravity_install.md.tmpl` | `protocols/Antigravity/Skills/INSTALL_ANTIGRAVITY.md` |
| `antigravity_workspace.json.tmpl` | `protocols/Antigravity/Skills/.antigravity/antigravity.json` |

Además de las plantillas hay dos tipos de artefacto:

- **Bloques gestionados (`regions`).** En `protocols/Antigravity/Skills/znve_skill.py`, el builder solo reescribe lo que hay entre `# >>> znve:generated` y `# <<< znve:generated`: nombre, versión, instrucción de sistema, catálogo de `/znve-help` y modos. El resto del módulo (las herramientas) se mantiene a mano. `Auto_Installer.py` e `install_znve_global.py` importan esas constantes, así que no llevan copias propias. En `protocols/mcp/znve-mcp-server.ts` el bloque es la cabecera (versión de ZNVE y axiomas), dentro del comentario `/** ... */`.
- **Copias (`mirrors`).** `.antigravity/skills/znve/znve_skill.py` es una copia exacta del módulo canónico, igual a la que deja `Auto_Installer.py` en cada proyecto.

Las plantillas que empiezan por `_` son fragmentos compartidos: se incluyen con `{{> _nombre.md.tmpl}}`. Los bloques calculados desde la especificación se insertan con `{{clave}}`; la lista completa está en `build_context()` de `builder.py`.

## Qué verifica `test_sync.py`

- La especificación: nombre `znve`, versión SemVer, comandos únicos y 6 modos más ayuda.
- Que ningún artefacto se haya desviado de la especificación.
- Que cada directiva mencione los 10 comandos y cite una sola versión de ZNVE.
- Que no queden marcas `[cite: N]`, vallas ` ```markdown ` iniciales ni enlaces `utm_source`.
- Que la skill de Claude cumpla las reglas de subida de claude.ai (claves del frontmatter, nombre y descripción de hasta 1024 caracteres).
- Que las herramientas MCP documentadas sean las que expone `protocols/mcp/znve-mcp-server.ts` y que `protocols/COMMANDS.md` conserve las secciones que filtra `znve_help`.
- Que el enum de escenarios de `protocols/agents/openrouter/response-schema.json` coincida con la especificación.
- Que `znve_skill.py` exponga la versión y el catálogo de la especificación, que la skill se llame `znve` y tenga 6 herramientas, que `Auto_Installer.py` sustituya el registro antiguo `zero_noise_vibe_engineering` y que `install_znve_global.py` reemplace la regla de `GEMINI.md` sin duplicarla.

Al final avisa, sin fallar, de los archivos mantenidos a mano que citan otra versión de ZNVE.
