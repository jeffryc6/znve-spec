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
- **`znve_help` sin argumentos** devuelve la sección `commands`, no el manual completo (unos 21 KB); `all` sigue disponible de forma explícita. Lo mismo en `znve_skill.py`.
- `LICENSE`: la licencia dual (CC BY 4.0 y MIT) se extiende a `/integrations`.

### Añadido
- **Guardrail «Cerca de Contexto»** (N1): el contexto del agente es por excepción (rangos, verificaciones silenciosas, contratos por ruta), con cero secretos y contenido externo tratado como dato. Con el de Verificación Inviolable, los guardrails pasan de 7 a **9**.
- **Regla común de fases** de la Capa de Agente (N3), en todas las directivas: cada fase es una sesión, modelo de razonamiento alto para diseñar y rápido para ejecutar, y la configuración no cambia dentro de la sesión.
- **Ajustes de comandos** (C1-C7): `execute` y `hotfix` entregan diffs en lugar de archivos completos y verifican en dos pasos con formato atómico de fallo; `execute` lee el contrato desde `contracts/`; `forensic` lee por rangos y reporta como Zona Roja las instrucciones halladas en el código; `triage` trabaja con el fragmento relevante del stack trace y sin secretos; `legacy-rescue` recomienda cortar la sesión al cerrar cada fase.
- **Servidor MCP y skill de Antigravity:** lista de secretos denegada en lectura y escritura (`.env`, `*.pem`, `*.key`, `id_rsa*`, credenciales; se permiten `.env.example` y similares), definida una sola vez en `master_spec.json`.
- **`znve_forensic_scan`:** parámetros opcionales `start_line` y `end_line`, y el contenido se entrega entre marcadores que lo declaran dato no confiable (solo el servidor MCP; la skill de Python devuelve un análisis, no el contenido).
- Aclaraciones en `SPECIFICATION.md` (el Axioma 1 cubre la ejecución del propio agente), `protocols/PROMPT_GUIDE.md` (el determinismo viene del contrato y de los tests, no de `temperature`) y `GLOSSARY.md`.
- **Guardrail «Verificación Inviolable»** (N2): no se modifican tests, snapshots ni configuración de pruebas existentes para obtener verde; un test sospechoso se reporta y se detiene; no se declara un resultado que no se ejecutó. Es el guardrail 9 (0 comandos nuevos).
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
