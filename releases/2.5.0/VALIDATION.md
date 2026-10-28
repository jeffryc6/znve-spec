# Validación local — ZNVE 2.5.0

Fecha: 2026-10-27 (America/Costa_Rica). Windows, Node v24.18.0, Python 3.14.6. MCP compartido 2.1.0, SDK MCP 1.32.0, Zod 4.6.7. La carpeta de origen conserva ZNVE 2.4.2; esta entrega usa una copia selectiva de su checkout, incluidos cambios locales relevantes, sin `.git`, configuración personal, workspaces de benchmarks ni caches previas.

## Comprobaciones ejecutadas

| Comando | Resultado |
|---|---|
| `python znve-auto/builder.py --verify` | 43 artefactos sincronizados |
| `python znve-auto/test_sync.py` | 54 pruebas correctas |
| `python znve-auto/test_workflow_sync.py` | 6 pruebas correctas |
| `npm test` en integrations/mcp-server | 253 tests: 251 correctos, 0 fallos, 2 omitidos por plataforma/permisos |
| `npm run check:openrouter` | Type-check correcto; sin llamada al proveedor |
| Handshake real vía install-common.mjs, con skipBuild | initialize + tools/list: 7 herramientas esperadas |
| `npm audit --json` | 0 vulnerabilidades conocidas en la consulta realizada |
| `npm ls zod` | 4.6.7 coherente y deduplicado |

Las dos omisiones del MCP corresponden a un caso POSIX de componente intermedio y a symlink de archivo que Windows no permitió crear. Los tests de junctions, escape de workspace y estado enlazado sí se ejecutaron.

## Qué cubre el flujo nuevo

Procesos reales exitosos, fallidos, con timeout y exceso de salida; no heredar un canario de API; no conservar stdout/argv crudos; gate sin evidencia; supuestos materiales sin resolver; cambios en spec, archivos y durante una prueba; checkpoint/resume; claims entre instancias; conflictos de hash, scope y expiración; creación sin sobrescritura; rutas inválidas; secretos y estado protegido. El ciclo completo se ejecutó también por stdio MCP, incluyendo apply y posterior invalidación del gate.

Se conservan los 63 casos compartidos legacy y las regresiones del servidor. Las pruebas del motor Python retirado se sustituyeron por comprobaciones de error de migración; no se alteraron los casos legacy para obtener verde.

## Límites y comprobaciones pendientes

- El validador auxiliar quick_validate.py de skill-creator no pudo arrancar porque ambos Python disponibles carecen de PyYAML. La suite propia sí validó frontmatter, metadatos, referencias y contenido de paquetes. No se instaló PyYAML como dependencia del proyecto.
- No se ejecutaron sesiones reales de Claude, Gemini, Antigravity, Grok, Ollama ni OpenRouter. Sus integraciones externas permanecen NO INTEGRADAS en el sentido de smoke test por host. Sí se verificó el MCP real y sus instaladores sobre directorios temporales.
- No se ejecutó GitHub Actions, no se publicó ni se modificaron instalaciones globales.
- No hay prueba de ahorro de tokens ni medición conductual de reducción de drift en 2.5.0. Los experimentos anteriores son históricos; los que importaban el motor Python necesitan migración de su arnés.
- El runner no es sandbox, los claims son cooperativos y la evidencia local no resiste manipulación por el dueño del host. El gate solo evalúa checks e inputs declarados.

La auditoría corrigió seis dependencias compatibles del lockfile. “0 vulnerabilidades” describe la base de avisos consultada, no una garantía absoluta de seguridad.
