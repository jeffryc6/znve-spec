<p align="right">
  <a href="https://translate.google.com/translate?sl=es&tl=en&u=https://github.com/jeffryc6/znve-spec/blob/main/rfcs/0003-base-repair-and-next-version.md">
    <img src="https://img.shields.io/badge/Translate_to-English-blue?style=flat-square&logo=googletranslate" alt="Translate to English">
  </a>
</p>

# RFC 0003: Reparación de la base v2.3.x y antesala de la versión 2.4.0
- **Autor:** Jeffry Carmona (@jeffryc6)
- **Fecha:** 2026-10-03
- **Estado:** Implemented (v2.4.0) · registro histórico
- **Componente Afectado:** MCP Server | Agent Directives | Core Pillars | Repositorio
- **Versión objetivo:** v2.3.x (reparación, sin subir la versión de la norma) → v2.4.0 (nueva versión)

> Registro histórico de la reparación, ya aplicada y publicada en la v2.4.0. Los documentos `rfcs/LOCAL-*.md` que menciona son notas de trabajo del autor y no forman parte del repositorio.
> Este documento cierra la reparación de la base y prepara la siguiente versión. No contiene cambios por sí mismo: registra lo hecho, lo pendiente y el procedimiento acordado.
> Publicar solo junto con los commits de la reparación o después de ellos: la Parte A describe fallos de seguridad del servidor MCP que esos commits corrigen.

## 1. Motivación y Resumen Ejecutivo

Antes de abordar las actualizaciones grandes (Harness y KV Cache / RFC 0002), se auditó el repositorio completo y se reparó la base actual. La auditoría (77 archivos, incluidas subcarpetas y archivos sin rastrear) encontró que la cadena "fuente única → artefactos → CI" funcionaba bien, pero que **las herramientas MCP y sus equivalentes en Python no cumplían las garantías que publica la norma**. Por ejemplo, `znve_forensic_scan` leía cualquier archivo del disco y `znve_scaffold_harness` podía sobrescribir producción mientras respondía que "el código original no ha sido modificado". La suite de paridad no lo detectaba porque solo comparaba nombres, no comportamiento.

Resultado de la reparación:

| Antes | Después |
|---|---|
| 22 tests de paridad, 0 de comportamiento | 39 tests Python + 59 tests del servidor MCP (`node:test`) |
| CI solo con Python | CI con Python, Node (build + suite MCP) y type-check del cliente OpenRouter |
| 10 casos hostiles de la sonda aceptados | 10 de 10 rechazados, sin escrituras fuera del workspace |
| Descripciones de herramientas escritas a mano (desfasadas) | Generadas desde `master_spec.json` (región `tools`) |
| CRLF y LF mezclados, cachés sin ignorar | LF en todo el repo (`.gitattributes`), `.gitignore` en la raíz |

## 2. Especificación Técnica Detallada

### 2.1 Parte A: lo que se hizo (aplicado)

**Método.** Auditoría → plan por prioridades → para cada bloque, primero un test que falla, después el parche mínimo y al final la verificación. Lo generado se cambió en `znve-auto/master_spec.json` y plantillas, y se regeneró. `protocols/agents/deepseek/` no se tocó. La versión de la norma se mantuvo en **2.3.0**: subirla obliga a editar archivos de DeepSeek (ver Parte B).

| Bloque | Contenido | Hallazgos cubiertos |
|---|---|---|
| **P0 · Red de seguridad** | Suite `protocols/mcp/test/server.test.mjs` (`node:test`, cero dependencias, servidor real por stdio contra un workspace temporal). Clase `SkillToolBehaviorTests` en `test_sync.py`. Los tests de DSH se omiten si falta su `AGENTS.md`. Job `mcp-server` en el CI y `permissions: contents: read`. | C1, C2, E3 (parcial) |
| **P1 · Seguridad** | Contención de rutas en `ZNVE_WORKSPACE`, comprobando la ruta pedida y la real (cierra `../`, rutas absolutas, symlinks y junctions). Arnés solo bajo `tests/` o `sandbox/` en la raíz, con `test_filename` sin rutas. Validación estricta de argumentos (strings no vacíos, enums, listas). Mismas reglas en `znve_skill.py`. | A1, A2, A3, B1, F1 |
| **P2 · Barandillas correctas** | Escritura atómica (temporal + renombrado, conserva permisos) y bloqueo de `.git/` y `node_modules/`. Detector común de errores silenciados (`catch {}`, `catch` con solo comentarios, `.catch(() => {})`, `except …: pass`). Importaciones vetadas por módulo, no por substring. `SELECT *` y `find({})` sin distinguir mayúsculas. Auditoría sin falsos positivos y con nivel de riesgo. `forensic_scan` con bytes reales y tope de 1 MiB, rechazando binarios y directorios. `znve_help` por encabezado y temas desconocidos como error. Anotaciones MCP. Errores sin rutas del host. Descripciones generadas desde la spec. Servidor 1.2.0 con la versión leída de `package.json`. | A4-A9 (A9 parcial), B2, B3, B5, C5 |
| **P3 · Higiene** | `.gitignore` y `.gitattributes` en la raíz; 6 archivos normalizados a LF. `znve.zip` sin cachés ni ocultos. El instalador valida los nombres exactos de las herramientas. SDK MCP 1.32.0 (0 vulnerabilidades). Cliente OpenRouter compilable (`"type": "module"`, error `[ZNVE_OR_SCHEMA]`). | E1, E2, E5, C6 (parcial), D2 |
| **P4 · Documentación** | macOS pasa a `desktop` (iOS sigue en `mobile`). **Regla de excepción del Anti-Bloat Fence** (decisión 4.7, opción a): una librería de terceros solo entra si el SDK nativo no ofrece la capacidad, y el contrato justifica qué resuelve, su peso y la alternativa nativa descartada. Hotfix = un `TARGET_FILE` más su test. `/znve-legacy-rescue` con sus 5 fases. Configuración MCP por cliente (Antigravity, Claude Desktop, Cursor, Windsurf). Copilot sin "slash commands" falsos. Glosario, README, `znve-auto/README`. Animación de `index.html` a 30 fps. | F2-F8, C6 |

**Decisiones registradas durante la reparación:**

| Decisión | Resolución |
|---|---|
| Carpeta `protocols/agents/deepseek/` | Queda como está, sin versionar; sus tests se omiten si falta. |
| Raíces permitidas para el arnés | Solo `tests/` y `sandbox/` en la raíz del workspace. |
| Valor por defecto de `znve_help` | Sin cambios (`all`); se revisa en la RFC 0002. |
| Versión de la norma / del servidor | Norma 2.3.0 sin cambios; servidor MCP 1.2.0. |
| Anti-Bloat Fence frente a Dexie.js, MMKV y WatermelonDB | Opción a: excepciones justificadas. |

**Commits** (rama `main`, sobre `origin/main` = `02c6cc6`; **sin push**):

| Commit | Contenido |
|---|---|
| `4eee4c5` | Normalize line endings to LF and ignore Python caches |
| `17d637d` | Repair MCP server and skill guardrails, with regression tests |
| `8eb7ad4` | Align hand-written docs with the repaired base |

**Verificación final** (y sobre una exportación limpia del índice, como la verá el CI): `builder.py --verify` 26/26 · `test_sync.py` 39/39 · `npm test` 59/59 · `check:openrouter` OK · `npm audit` 0 vulnerabilidades · enlaces y codificación sin errores.

Documentos locales de trabajo (excluidos vía `.git/info/exclude`): `rfcs/LOCAL-audit-2026-10-03.md` (reporte completo), `rfcs/LOCAL-base-repair-plan.md` (plan P0-P4) y `rfcs/LOCAL-next-release-backlog.md`.

### 2.2 Parte B: pendiente (diferido a después de la base)

| Tema | Ítems | Motivo |
|---|---|---|
| **Harness** | Backlog §2.2 (determinismo del Golden Master), §2.3 (verificación demostrada) | Cambia la semántica del comando `harness` |
| **KV Cache / RFC 0002** | Guardrail 8, perfiles de agente, rangos en `forensic_scan` (A6), valor por defecto de `znve_help` (A7) | Concepto nuevo, v2.4.0 |
| **DeepSeek** | Versionar la carpeta, `AGENTS.md` generado (C3), `.ps1` en el chequeo de versión (C4), `install-dsh.ps1` (D1), anécdota en `DSH_PROTOCOL.md` (F7) | Indicación: dejar como está |
| **Versión de la norma 2.3.1** | Subida única de versión | Afecta a archivos de DeepSeek; se hace al retomarlo |
| **Contrato de respuesta unificado** | B4 | Rompe a quien consume las respuestas actuales → v2.4.0 |
| **Refactor del servidor** | Migración a `McpServer.registerTool` (A9) | Refactor sin bug asociado |
| **Renombres** | Copias de Copilot y errata `instrucctions` (E4) | Rompe enlaces externos |
| **Verificación externa** | Caso de estudio 02, referencias de DSH, OpenRouter y Antigravity (F9) | Requiere investigación fuera del repo |

**Pendientes menores** detectados en la auditoría que no figuraban en la tabla. Se añaden aquí para que no se pierdan:

| Ítem | Detalle |
|---|---|
| D3 | `antigravity_sdk_example.py`: verificar si `env={…}` reemplaza el entorno completo (incluido `PATH`) en el SDK; sangría de 2 espacios. |
| C6 (resto) | El builder no detecta artefactos huérfanos (un archivo generado cuya plantilla se retiró). |
| Test de symlink en Python | El servidor MCP prueba el escape por enlaces; `znve_skill.py` no (en Windows, crear symlinks desde Python requiere permisos). |
| E3 (resto) | Fijar las acciones del CI a SHA y valorar una matriz de Python (CI 3.11, local 3.14). |
| Push | `main` va 3 commits por delante de `origin/main`; el push queda a decisión del autor. |

### 2.3 Parte C: antesala de la nueva versión

#### 2.3.1 Número de versión

La versión que sigue es **v2.4.0**:

- La reparación aplicada corrige garantías sin cambiar la semántica de ningún comando (nivel de parche). La subida a 2.3.1 se difirió, así que quedará absorbida por la siguiente versión menor.
- Harness (§2.2/§2.3 del backlog) añade exigencias a la salida de `/znve-harness`, y KV Cache (RFC 0002) introduce un concepto con nombre (guardrail 8, Capa de Agente). Según `SPECIFICATION.md` §10, eso es una versión **menor**.
- Si el contrato de respuesta unificado (B4) cambia la forma de las respuestas MCP, la ruptura afecta al **servidor** (versionado aparte: 1.2.0 → 2.0.0), no a la norma.

Nota técnica: `test_sync.py` exige SemVer estricto (`^\d+\.\d+\.\d+$`). Mientras la versión esté en desarrollo, `master_spec.json` debe seguir en 2.3.0 y subir a 2.4.0 en un único commit al cerrar, o se amplía el test para aceptar `-rc.N`.

#### 2.3.2 Dónde se crea la copia

**Propuesta original:** copiar la carpeta reparada a `D:\New folder\github\znve-spec\ver X.X.X`.

**Recomendación aplicada:** crearla **al lado** del repositorio, no dentro, y mediante `git worktree`:

```text
D:\New folder\github\znve-spec\           ← v2.3.x reparada (rama main), queda intacta como referencia
D:\New folder\github\znve-spec-v2.4.0\    ← nueva versión (rama release/2.4.0)
```

| Problema de una copia dentro del repo (`znve-spec\ver 2.4.0\`) | Efecto |
|---|---|
| Queda dentro del árbol de trabajo de git | `git status` muestra toda la copia como archivos nuevos, con riesgo de subirla por error |
| `test_sync.py` recorre el repo con `rglob` | El chequeo de versiones y los verificadores escanearían cada archivo dos veces |
| Dos `master_spec.json`, dos `.github/`, dos `.agents/` anidados | Ambigüedad sobre cuál es la fuente única de verdad |
| Espacio en el nombre (`ver 2.4.0`) | Rutas con espacios en comandos, configuraciones MCP y CI |

**Por qué `git worktree` y no una copia simple:**

1. **Solo copia archivos propios de ZNVE por construcción**: un worktree contiene únicamente los archivos rastreados. Ni `node_modules/`, ni `dist/`, ni `__pycache__/`, ni `.claude/`, ni backups.
2. **Conserva el historial**: la nueva versión es una rama (`release/2.4.0`), con `git log`, `git blame` y `git mv` (los renombres conservan la historia).
3. **Comparte `.git/info/exclude`**: los `rfcs/LOCAL-*.md` siguen siendo locales en la copia.
4. **Reversible**: `git worktree remove` deshace la copia sin tocar `main`.

#### 2.3.3 Procedimiento (cuando se autorice)

```bash
git -C "D:/New folder/github/znve-spec" worktree add "../znve-spec-v2.4.0" -b release/2.4.0
```

Después se copian a mano los archivos propios de ZNVE que **no** están rastreados (para mantener el orden de las RFC y el estado de trabajo):

| Copiar | Motivo |
|---|---|
| `protocols/agents/deepseek/` (tal cual) | Integración DSH, se retoma en esta versión |
| `rfcs/0002-agent-layer.md` | RFC de KV Cache, núcleo de la v2.4.0 |
| `rfcs/0003-base-repair-and-next-version.md` | Este documento (si no se ha versionado antes) |
| `rfcs/LOCAL-*.md` | Backlog, auditoría y plan (siguen locales) |

| No copiar nunca | Motivo |
|---|---|
| `.git/` (lo gestiona el worktree), `node_modules/`, `dist/`, `__pycache__/`, `*.pyc` | Cachés y artefactos reproducibles (`npm ci`, `npm run build`) |
| `.claude/settings.local.json`, `*.bak-*`, temporales | Configuración local o basura |

**Alternativa** (si se prefiere una copia sin historial): copiar con exclusiones e iniciar un repositorio nuevo. Pierde `git log`/`git blame` y la relación con `origin`.

```powershell
robocopy "D:\New folder\github\znve-spec" "D:\New folder\github\znve-spec-v2.4.0" /E /XD .git node_modules dist __pycache__ .claude /XF *.pyc *.bak-*
```

#### 2.3.4 Estructura propuesta, ordenada por relevancia

Criterio de orden: primero la norma (qué es ZNVE), luego cómo se trabaja (protocolos para humanos), después dónde se instala (una carpeta por asistente), luego el servidor MCP (código) y por último la gobernanza y las herramientas del repositorio.

```text
znve-spec-v2.4.0/
├── README.md                  1 · Entrada: qué es, instalación, comandos
├── SPECIFICATION.md           2 · La norma
├── GLOSSARY.md                3 · Vocabulario
├── CHANGELOG.md               4 · NUEVO: historial por versión y notas de migración
├── CONTRIBUTING.md · LICENSE · index.html
├── .github/                   copilot-instructions.md (única copia) · workflows/
├── protocols/                 5 · Cómo se trabaja (humanos)
│   ├── ZNVE_PROTOCOL.md             maestro, modos 1-6
│   ├── GREENFIELD_STARTER.md        modo 1
│   ├── ZNVE_MODERN_APPS_PROTOCOL.md modos 3-4
│   ├── ZNVE_LEGACY_PROTOCOL.md      modo 5
│   ├── PROMPT_GUIDE.md
│   └── COMMANDS.md                  generado; lo sirve znve_help
├── integrations/              6 · Dónde se instala (una carpeta por asistente)
│   ├── README.md                    NUEVO, generado: qué archivo usar en cada asistente
│   ├── claude/                      skills/znve/ · znve.zip · project-instructions.md · GUIA_CREAR_SKILL.md
│   ├── gemini/                      skills/znve/ · INSTALL_GEMINI.md
│   ├── cursor/                      cursorrules.md
│   ├── deepseek/                    directive.md (web/API) · harness/ (AGENTS.md, DSH_PROTOCOL.md, install-dsh.ps1, README.md)
│   ├── ollama/                      Modelfile
│   ├── openrouter/                  system-prompt.md · response-schema.json · client.ts · package.json
│   ├── antigravity/                 skill/ (SKILL.md, INSTALL, .agents/) · sdk/ (znve_skill.py, agent.py) · installers
│   └── mcp-server/                  7 · Código: src, test/, package.json, instalador, ejemplos
├── case-studies/              8 · Evidencia
├── rfcs/                      9 · Gobernanza (0000-template, 0001, 0002, 0003, LOCAL-*)
└── znve-auto/                 10 · Fuente única: master_spec.json, plantillas, builder, tests
```

**Mapa de rutas (actual → v2.4.0):**

| Actual | v2.4.0 | Nota |
|---|---|---|
| `protocols/agents/claude/…`, `protocols/agents/claude-system-skills.md` | `integrations/claude/…`, `integrations/claude/project-instructions.md` | |
| `protocols/agents/gemini/…` | `integrations/gemini/…` | Cambia el `--path` de `gemini skills install` |
| `protocols/agents/cursor-rules.md` | `integrations/cursor/cursorrules.md` | |
| `protocols/agents/deepseek-directive.md` · `protocols/agents/deepseek/` | `integrations/deepseek/directive.md` · `integrations/deepseek/harness/` | Una sola carpeta para las dos vías de DeepSeek |
| `protocols/agents/ollama/`, `protocols/agents/openrouter/` | `integrations/ollama/`, `integrations/openrouter/` | |
| `protocols/Antigravity/Skills/` | `integrations/antigravity/` (subcarpetas `skill/`, `sdk/`) | Nombre en minúsculas, como el resto |
| `protocols/mcp/` | `integrations/mcp-server/` | Rompe las configuraciones MCP existentes que apuntan a `…/protocols/mcp/dist/`: hay que volver a ejecutar el instalador |
| `copilot-instructions.md` (raíz), `protocols/agents/copilot-instrucctions.md` | se eliminan | Queda solo `.github/copilot-instructions.md`. Resuelve E4 |

**Qué hay que actualizar junto con los movimientos** (en el mismo bloque, para que los tests sigan en verde):

- `master_spec.json`: `targets`, `regions`, `mirrors`, `bundles`, `mcp.server_file` e `integrations`.
- Plantillas con rutas (instalación, README de integraciones).
- `test_sync.py`: constantes de rutas (`MCP_SERVER`, `OPENROUTER_SCHEMA`, `DEEPSEEK_AGENTS`, `SKILL_FILES`, `ANTIGRAVITY_DIR`).
- Servidor MCP: `MANUAL_CANDIDATES` (ruta relativa a `protocols/COMMANDS.md`).
- Instaladores: `REPO_ROOT` en `install-antigravity.mjs` y rutas de `Auto_Installer.py` e `install_znve_global.py`.
- CI: `working-directory` y `cache-dependency-path`.
- `index.html` y `README.md`: enlaces internos y URLs `raw.githubusercontent.com`.
- `LICENSE`: las licencias se asignan por carpeta (`/protocols` es CC BY 4.0 + MIT); hay que extender la doble licencia a `/integrations`.
- `CHANGELOG.md`: tabla de migración de rutas para quien tenga enlaces o instalaciones previas.

#### 2.3.5 Orden de trabajo propuesto para la v2.4.0

Cada paso termina con la puerta de verificación de la sección 4 y su propio commit.

1. **Copia y reestructuración (solo movimientos).** `git mv` según el mapa, más las rutas actualizadas. Sin cambios de contenido, para que el diff se lea como renombres. Incluye E4.
2. **DeepSeek.** Versionar la carpeta, generar `AGENTS.md` desde una plantilla con presupuesto de bytes (C3), incluir `.ps1` en el chequeo de versión (C4) y corregir `install-dsh.ps1` (D1, F7). Desbloquea la subida de versión.
3. **Harness.** Backlog §2.2 y §2.3 en `master_spec.json` (una frase por campo).
4. **KV Cache (RFC 0002).** Guardrail 8, perfiles de agente, rangos en `forensic_scan`, valor por defecto de `znve_help`. Incluye la prueba de campo A/B de su sección 4.2.
5. **Contrato de respuesta unificado (B4) + `McpServer.registerTool` (A9).** Tocan los mismos archivos: van juntos. Servidor MCP 2.0.0.
6. **Pendientes menores** (D3, C6, symlink en Python, E3) y **verificación externa** (F9).
7. **Cierre.** `master_spec.json` → 2.4.0, regenerar, `CHANGELOG.md`, verificación completa. El merge a `main` y el push quedan a decisión del autor.

## 3. Demostración de Cero Ruido (Zero-Noise Proof)

- **Parte A:** ninguna dependencia nueva de runtime. Los tests usan `node:test` y `unittest` (bibliotecas estándar). La única actualización es el SDK MCP, que ya era dependencia (1.30.1 → 1.32.0).
- **Parte C:** la reestructuración **elimina** dos copias duplicadas de las instrucciones de Copilot (~19 KB) y no añade comandos ni conceptos. Los únicos archivos nuevos son `CHANGELOG.md` y un índice de integraciones generado.
- **Copia sin ruido por construcción:** el worktree solo contiene archivos rastreados; las cachés y los temporales no pueden colarse.

## 4. Plan de Verificación y Pruebas

**Puerta de verificación** (después de cada paso de la sección 2.3.5):

```bash
python znve-auto/builder.py --verify
```
```bash
python znve-auto/test_sync.py
```
```bash
cd integrations/mcp-server && npm ci && npm test && npm run check:openrouter
```

(Hasta el paso 1, la ruta del último comando sigue siendo `protocols/mcp`.)

**Comprobaciones específicas del paso 1 (reestructuración):**

- `git diff --stat -M main` muestra los movimientos como renombres (`R`) sin cambios de contenido, salvo las rutas actualizadas.
- Cero enlaces relativos rotos en `.md` y `.html`, y cero referencias a `protocols/agents/`, `protocols/Antigravity/` o `protocols/mcp/` fuera de `CHANGELOG.md`.
- El instalador MCP (`--dry-run --skip-build`) expone las 6 herramientas desde la nueva ruta.
- `git status` en `D:\New folder\github\znve-spec` sigue limpio: la copia no afecta a la v2.3.x.

**Criterio de aceptación de la Parte C:** la copia existe, la reestructuración pasa la puerta de verificación y `main` (v2.3.x reparada) queda intacta como referencia.
