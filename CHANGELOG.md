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
- **Capa de Agente con perfiles** (K1-K10): una sección `agent_profiles` en `master_spec.json` (comportamiento, sin cifras) con un perfil por asistente: prefijo fijo, qué invalida su caché, corte de sesión, configuración por fase y campos de medición. Cada directiva lleva **solo su perfil** (campo `agent` de `targets`); el manual (`COMMANDS.md`, sección 5) reúne la tabla completa y las guías de instalación de Gemini y Antigravity añaden «Rendimiento y caché». Perfil de DeepSeek con la nota del `reasoning_content` acumulado.
- **`protocols/PROMPT_GUIDE.md`, sección 11:** orden estable → volátil, prácticas de sesión, protocolo de medición por proveedor y cifras de referencia fechadas.
- **Presupuestos de bytes** (`max_bytes` en `targets`) para todos los artefactos generados, con tests de presupuesto para los guardrails, el bloque de Capa de Agente y las descripciones de las herramientas MCP; test de prefijo estable (sin fechas ni rutas del host en los artefactos generados).
- **Cliente de OpenRouter:** con `ZNVE_OPENROUTER_USAGE=1` escribe en `stderr` los campos de uso (instrumento de la prueba A/B); sin la variable no imprime nada.
- **Modelfile de Ollama:** nota de que una temperatura baja no garantiza el determinismo; guía de memoria del KV cache (`num_ctx`, `OLLAMA_FLASH_ATTENTION`, `OLLAMA_KV_CACHE_TYPE`).
- **Bloque `GEMINI.md` de `install_znve_global.py`:** sigue mínimo y estático; añade una línea para la Cerca de Contexto y otra para la Verificación Inviolable.
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

### Mantenimiento
- **Builder:** un archivo suelto en la carpeta del paquete `znve.zip` ya no se empaqueta en silencio: el builder falla indicando su ruta (los miembros escritos a mano se declaran en `include`).
- **`antigravity_sdk_example.py`:** pasa al servidor un entorno mínimo explícito (lo que node necesita más `ZNVE_WORKSPACE`), sin depender de cómo trate el SDK `env`, y usa sangría de 4 espacios.
- **`test_sync.py`:** la heurística de versiones ya no confunde `ZNVE_OR_ERROR` y similares con una cita de versión; las comprobaciones de versión incluyen los `.ps1`; tests de escape por enlaces simbólicos en `znve_skill.py`.
- **CI:** la verificación de paridad corre en una matriz de Python 3.11 y 3.14.

### Servidor MCP 2.0.0 (cambios incompatibles)

El servidor pasa de 1.2.0 a **2.0.0**: unifica su contrato con `znve_skill.py`, migra a `McpServer.registerTool` y fija su lista de herramientas. La norma sigue en 2.3.0; esta ruptura afecta solo a quien consuma las respuestas del servidor o de la skill de Python.

- **Contrato de respuesta común (M6).** Las seis herramientas responden un único objeto JSON compacto, con `status` primero (`SUCCESS`, `APPROVED`, `REJECTED` o `ERROR`) y, en rechazos y errores, `code` (15 códigos deterministas, p. ej. `OUTSIDE_WORKSPACE`, `SECRET_DENIED`, `BAD_RANGE`) y `message`. `isError` del protocolo es verdadero con `REJECTED` y `ERROR`. Las rutas son relativas al workspace. Documentado en `protocols/COMMANDS.md`, sección 2, y comprobado por 48 casos que ejecutan las dos implementaciones.
- **`McpServer.registerTool` (M7)** en lugar de los manejadores de bajo nivel. Los esquemas se validan en el SDK: un tipo equivocado, un campo obligatorio ausente o un valor fuera del enum los rechaza el SDK (`isError`, texto del SDK, sin `code`); `znve_skill.py` devuelve `BAD_ARGUMENT` en esos casos. `zod` pasa a declararse como dependencia directa (el SDK ya lo exige como dependencia par; no añade paquetes).
- **Lista de herramientas estable (M8):** las seis, siempre, en el orden de `master_spec.json`, con descripciones generadas y anotaciones de solo lectura o escritura.
- **Migración de respuestas.**

| Herramienta | Antes (1.x) | Ahora (2.0.0) |
|---|---|---|
| `znve_help` | texto Markdown | `{status, topic, text}`; en Python, dict en lugar de texto; Python admite `mcp_tools` |
| `znve_forensic_scan` | MCP: texto con el contenido; Python: métricas sin contenido | los dos: `file`, `size_bytes`, `total_lines`, `range`, `side_effects`, `red_zones`, `notice` y `content` (con marcadores de dato no confiable); `file` es relativa (antes, en Python, absoluta) |
| `znve_validate_contract` | MCP: `PASSED`/`valid_contract`; Python: `APPROVED`/`passed` | los dos: `APPROVED` o `REJECTED` con `passed` y `violations`; mismas librerías vetadas por defecto (`lodash`, `axios`, `moment`, `requests`, `jquery`) |
| `znve_audit_resources` | MCP: `risk_level`; Python: `clean` | los dos: `risk_level`, `clean`, `findings_count` y `findings`, con los mismos textos |
| `znve_scaffold_harness`, `znve_surgical_write` | texto en el MCP; `harness_file`/`file` absolutas en Python | `file` relativa, `message` y, al escribir, `bytes_written`; errores con `code` |

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
