# Changelog

Historial de cambios de Zero-Noise Vibe Engineering por versión, con notas de migración. El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y las versiones, [SemVer](https://semver.org/lang/es/) (ver `SPECIFICATION.md` §10).

## [2.4.0] — en desarrollo

### Cambiado
- **Reestructuración por relevancia.** Las integraciones de cada asistente salen de `protocols/` y pasan a `integrations/`, con una carpeta por asistente. `protocols/` queda solo para los protocolos de trabajo y el manual de comandos.
- **Servidor MCP** en `integrations/mcp-server/`.
- **Instrucciones de GitHub Copilot:** una sola copia, en `.github/copilot-instructions.md` (la ruta que lee Copilot).
- **DeepSeek Harness** pasa a estar versionado en `integrations/deepseek/harness/`.
- **`AGENTS.md` de DeepSeek Harness generado** desde `master_spec.json` (plantilla `deepseek_harness_agents.md.tmpl`), con un presupuesto de 16 KiB comprobado por test. Ya no repite pilares ni comandos a mano. Se omite la sección de pilares, como en el resto de las directivas generadas.
- **`install-dsh.ps1`** instala la directiva como un bloque entre marcadores (`<!-- znve:start -->`) y conserva el resto de tu `AGENTS.md` global; migra la instalación anterior de archivo entero; la desinstalación retira solo el bloque y nunca borra un global ajeno a ZNVE. La versión ya no está escrita en el script: la lee de `AGENTS.md`.
- `LICENSE`: la licencia dual (CC BY 4.0 y MIT) se extiende a `/integrations`.

### Añadido
- **Guardrail «Verificación Inviolable»** (N2): no se modifican tests, snapshots ni configuración de pruebas existentes para obtener verde; un test sospechoso se reporta y se detiene; no se declara un resultado que no se ejecutó. Pasa de 7 a 8 guardrails (0 comandos nuevos).
- **`/znve-harness`:** Golden Master determinista (semilla, `TZ`, locale y reloj fijos; campos volátiles enmascarados; volver a capturar un snapshot requiere aprobación humana) y verificación en dos pasos con formato atómico de fallo (`FALLO <archivo>:<línea> · esperado <x> · recibido <y>`).
- **`znve_scaffold_harness` solo crea** (servidor MCP y skill de Antigravity): se niega a sobrescribir un archivo existente, también un enlace, y no deja temporales.
- `integrations/README.md`: índice generado con el archivo que usar en cada asistente.
- Este `CHANGELOG.md`.

### Eliminado
- `copilot-instructions.md` en la raíz y `protocols/agents/copilot-instrucctions.md` (copias que Copilot no lee; la segunda tenía una errata en el nombre).

### Migración de rutas

Si tienes enlaces, scripts o instalaciones que apuntan a las rutas anteriores, actualízalos:

| Antes | Ahora |
|---|---|
| `protocols/agents/claude/…` | `integrations/claude/…` |
| `protocols/agents/claude-system-skills.md` | `integrations/claude/project-instructions.md` |
| `protocols/agents/gemini/…` | `integrations/gemini/…` (cambia el `--path` de `gemini skills install`) |
| `protocols/agents/cursor-rules.md` | `integrations/cursor/cursorrules.md` |
| `protocols/agents/deepseek-directive.md` | `integrations/deepseek/directive.md` |
| `protocols/agents/deepseek/` | `integrations/deepseek/harness/` |
| `protocols/agents/ollama/Modelfile` | `integrations/ollama/Modelfile` |
| `protocols/agents/openrouter/…` | `integrations/openrouter/…` |
| `protocols/Antigravity/Skills/…` | `integrations/antigravity/…` |
| `protocols/mcp/…` | `integrations/mcp-server/…` |
| `copilot-instructions.md` (raíz), `protocols/agents/copilot-instrucctions.md` | `.github/copilot-instructions.md` |

**Servidor MCP ya registrado:** las configuraciones que apuntan a `…/protocols/mcp/dist/znve-mcp-server.js` dejan de funcionar. Vuelve a ejecutar el instalador desde la nueva ruta o actualiza la ruta a mano:

```bash
cd integrations/mcp-server && node install-antigravity.mjs --workspace "<ruta>/tu-proyecto"
```

**Skill de Antigravity ya instalada:** sigue funcionando; para actualizarla, ejecuta los instaladores desde `integrations/antigravity/`.

## [2.3.0]

Versión publicada de la norma. La reparación de la base posterior (servidor MCP 1.2.0, suites de regresión, CI con Node, contención de rutas y barandillas aplicadas por código) se documenta en `rfcs/0003-base-repair-and-next-version.md`, Parte A.
