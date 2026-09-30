# Manual de comandos y herramientas ZNVE v2.3.0

<!-- Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano. -->

> **Axioma 1:** "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
> **Axioma 2:** "La IA no inventa arquitectura; ejecuta contratos deterministas."

Este documento recopila el catálogo maestro de comandos agénticos (`/znve-*`), las herramientas MCP (`znve_*`) y la forma de activarlos en cada asistente bajo el estándar Zero-Noise Vibe Engineering (ZNVE).

---

## 🧭 TABLA DE REFERENCIA RÁPIDA

| Comando / Herramienta | Tipo | Modos o fase |
|---|---|---|
| `/znve-help` | Comando de barra | Todos |
| `/znve-contract` | Comando de barra | Modo 1, 2, 4 |
| `/znve-execute` | Comando de barra | Modo 1, 2, 4, 5 |
| `/znve-triage` | Comando de barra | Modo 3 |
| `/znve-hotfix` | Comando de barra | Modo 3 |
| `/znve-upgrade` | Comando de barra | Modo 4 |
| `/znve-forensic` | Comando de barra | Modo 2, 5, 6 |
| `/znve-harness` | Comando de barra | Modo 5 |
| `/znve-legacy-rescue` | Comando de barra | Modo 5 |
| `/znve-audit` | Comando de barra | Modo 6 |
| `znve_help` | Herramienta MCP | Ayuda |
| `znve_forensic_scan` | Herramienta MCP | Ingesta |
| `znve_validate_contract` | Herramienta MCP | Contrato |
| `znve_scaffold_harness` | Herramienta MCP | Aislamiento |
| `znve_surgical_write` | Herramienta MCP | Escritura |
| `znve_audit_resources` | Herramienta MCP | Hardening |

---

## 🎛️ SECCIÓN 1: COMANDOS DE BARRA (`/znve-*`) PARA ASISTENTES Y AGENTES

Los comandos de barra son palabras clave que instruyen al modelo a adoptar un rol técnico cerrado, restringir su generación e imponer un formato de salida estándar. Formas de invocación equivalentes:

- `/znve-contract …` (forma canónica)
- `/znve contract …` o `/znve -contract …` (skill elegida en el menú y comando a continuación)

Sin comando, toda respuesta técnica sigue los 4 bloques: [1] Blueprint y Contrato -> [2] Racional -> [3] Tarea Atómica -> [4] Verificación.

### 1. `/znve-help` — Manual operativo y ayuda rápida

- **Sintaxis:** `/znve-help`
- **Cuándo se usa:** El usuario escribe `/znve-?`, `/znve-help`, `/znve help`, solo `/znve`, o pregunta cómo usar ZNVE.
- **Restricción:** Solo lectura. No inspecciones ni generes código del proyecto; imprime el catálogo y la regla por defecto en 4 bloques.
- **Entornos recomendados:** Todos los asistentes; en MCP, la herramienta `znve_help`.
- **Salida:** el catálogo de comandos:

```text
🛠️ CATÁLOGO DE COMANDOS ZNVE v2.3.0:
• /znve-help         : Manual operativo e índice de comandos.
• /znve-contract     : Diseño de interfaces inmutables, DTOs y Anti-Bloat Fence.
• /znve-execute      : Implementación atómica en TARGET_FILE con desecho de recursos.
• /znve-triage       : Diagnóstico y contención de radio de impacto ante caídas.
• /znve-hotfix       : Parche quirúrgico atómico con test de regresión obligatorio.
• /znve-upgrade      : Migración de dependencias mediante Adaptador desacoplado.
• /znve-forensic     : Ingesta en solo lectura, matriz I/O y efectos secundarios.
• /znve-harness      : Suite Golden Master de caja negra sobre código intacto.
• /znve-legacy-rescue: Orquestación integral en 5 fases para código legacy.
• /znve-audit        : Hardening de hilos, memoria, descriptores y seguridad.

📋 REGLA POR DEFECTO (SIN COMANDO):
Toda respuesta técnica se estructura en 4 bloques:
[1] Blueprint y Contrato -> [2] Racional -> [3] Tarea Atómica -> [4] Verificación.

💡 USO: /znve <comando> <petición>   (ej.: /znve contract Diseña el DTO de usuario)
```

- **Ejemplo:**

```text
/znve-help
```

### 2. `/znve-contract` — Diseño de contratos deterministas

- **Sintaxis:** `/znve-contract [--platform=desktop|web|mobile|hybrid] [--delta]`
- **Cuándo se usa:** Antes de programar cualquier funcionalidad, endpoint, pantalla o módulo.
- **Restricción:** No escribas lógica de negocio; define solo las fronteras estructurales. En In-Flight, los contratos existentes no se alteran: se extienden.
- **Entornos recomendados:** Claude, OpenRouter, DeepSeek V3, Ollama (`qwen2.5-coder`).
- **Formato de entrega:**
  1. `CONTRATO DE ENTRADA Y SALIDA` — DTOs tipados con validación estricta de límites.
  2. `CONTRATO DE PERSISTENCIA` — esquema agnóstico con proyecciones y claves indexadas explícitas.
  3. `CONTRATO DE ERRORES` — enums o tipos cerrados con los modos de fallo previstos.
  4. `ANTI-BLOAT FENCE` — campos descartados, abstracciones innecesarias y paquetes prohibidos.
- **Stack por plataforma (`--platform`):**
  - **Escritorio (Windows / macOS / Linux)** (`desktop`): Rust + Tauri v2 o WinUI 3 nativo · persistencia: SQLite (WAL mode) / DuckDB.
  - **Web-App** (`web`): Vite + TypeScript / Next.js App Router · persistencia: IndexedDB (Dexie.js).
  - **Híbrida (Mobile / Desktop)** (`hybrid`): Tauri Mobile / Flutter / React Native Bare · persistencia: MMKV / WatermelonDB.
  - **Android nativo** (`mobile`): Kotlin + Jetpack Compose + Corrutinas · persistencia: Room DB.
  - **macOS / iOS nativo** (`mobile`): Swift 6 + SwiftUI · persistencia: SwiftData.
- **Lista de chequeo de solidez:**
  1. **Estructura invariable:** entradas, salidas, entidades y enums tipados.
  2. **Defensas de frontera:** errores explicitados, sin `any` ni `catch` genéricos.
  3. **Cero dependencias parásitas:** solo el SDK nativo o el runtime aprobado.
  4. **Filtro de diferimiento:** ideas secundarias movidas a `contracts/CONTRACT_BACKLOG.md`.
- **Criterio de parada:** al cumplirse los 4 puntos, emite "Contrato v1 sólido y cerrado. Listo para /znve-execute." y detén la generación.
- **Modo `--delta` (In-Flight):**
  1. Audita las discrepancias entre `contracts/` y `src/`.
  2. Clasifica los cambios en **Cubo A** (requerido ya, etapa activa) y **Cubo B** (diferido a `contracts/CONTRACT_BACKLOG.md`).
  3. Muestra el diff del Cubo A y re-congela el contrato antes de modificar código.
- **Ejemplo:**

```text
/znve-contract --platform=desktop Diseña el contrato DTO y de persistencia para un almacén local clave-valor en disco.
```

### 3. `/znve-execute` — Implementación quirúrgica atómica

- **Sintaxis:** `/znve-execute --target=<ruta/archivo>`
- **Cuándo se usa:** Tras la aprobación de un contrato de `/znve-contract`. Si no hay contrato aprobado, pídelo antes de escribir código.
- **Restricción:** Cero dependencias nuevas, cero `catch` vacíos, cero campos o parámetros fuera del contrato. Solo se modifica el `TARGET_FILE`.
- **Entornos recomendados:** Cursor Composer, Copilot Edits, Windsurf, Claude Code, Ollama.
- **Formato de entrega:**
  1. `TARGET_FILE` — ruta exacta del archivo objetivo.
  2. `CÓDIGO QUIRÚRGICO` — implementación modular, mínima y de huella casi nula.
  3. `LIBERACIÓN DE RECURSOS` — desecho explícito (`close`, `dispose`, `finally`, desuscripción de listeners).
  4. `VERIFICACIÓN ATÓMICA` — comando de terminal o test exacto para validar de inmediato.
- **Ejemplo:**

```text
/znve-execute --target=src/auth/session.ts Implementa el contrato UserSessionContract con las utilidades nativas de crypto.
```

### 4. `/znve-triage` — Diagnóstico de emergencia y blast radius

- **Sintaxis:** `/znve-triage`
- **Cuándo se usa:** Caídas de servicio, bloqueos de UI o excepciones imprevistas en producción.
- **Restricción:** Solo lectura estricta. Nada de parches a ciegas: un parche sin diagnóstico suele mover el fallo a otro sitio.
- **Entornos recomendados:** Claude, Cursor, Copilot, DeepSeek R1.
- **Formato de entrega:**
  1. `COMPONENTE AFECTADO` — endpoint, servicio o vista donde se manifiesta la falla.
  2. `CAUSA RAÍZ DETERMINISTA` — deadlock, pool agotado, timeout, fuga de memoria, etc.
  3. `RADIO DE IMPACTO (BLAST RADIUS)` — componentes en riesgo.
  4. `PLAN DE CONTENCIÓN INMEDIATA` — fallback local o degradación elegante sin alterar contratos de datos.
- **Ejemplo:**

```text
/znve-triage Analiza este log de error de conexión a la base de datos y aísla el radio de impacto: [stack trace].
```

### 5. `/znve-hotfix` — Parche quirúrgico acotado

- **Sintaxis:** `/znve-hotfix --incident=<ID>`
- **Cuándo se usa:** Remediación tras el diagnóstico de `/znve-triage`.
- **Restricción:** Modifica un único `TARGET_FILE` en la frontera del adaptador, sin tocar el núcleo. No rompas firmas públicas ni silencies errores; propaga `X-Run-ID` para la trazabilidad.
- **Entornos recomendados:** Cursor, Claude Code, GitHub Copilot.
- **Formato de entrega:**
  1. `TARGET_FILE` — ruta exacta del archivo defectuoso.
  2. `CÓDIGO QUIRÚRGICO` — parche atómico acotado.
  3. `TEST DE REGRESIÓN` — prueba que falla sin el parche y pasa al 100 % con él.
  4. `COMANDO DE VALIDACIÓN` — orden de terminal reproducible.
- **Ejemplo:**

```text
/znve-hotfix --incident=INC-142 Aplica el parche sobre src/network/http_client.ts con su test de regresión.
```

### 6. `/znve-upgrade` — Migración con capa anti-corrupción

- **Sintaxis:** `/znve-upgrade --dependency=<librería>`
- **Cuándo se usa:** Actualización de SDKs, APIs de terceros o librerías con breaking changes.
- **Restricción:** Las incompatibilidades externas no se propagan al dominio; quedan encapsuladas tras un `Port` y un `Adapter`.
- **Entornos recomendados:** Claude Projects, Cursor, DeepSeek.
- **Formato de entrega:**
  1. `MATRIZ DE BREAKING CHANGES` — versión previa vs. versión objetivo.
  2. `DISEÑO DE ADAPTADOR ANTI-CORRUPCIÓN` — interfaz interna (`Port`) y adaptador (`Adapter`).
  3. `CÓDIGO DEL ADAPTADOR` — implementación aislada sin tocar el dominio.
  4. `VERIFICACIÓN DUAL DE PARIDAD` — tests de paridad funcional y comprobación de huella de memoria.
- **Ejemplo:**

```text
/znve-upgrade --dependency=axios Planifica la migración a fetch nativo con un adaptador HTTP interno desacoplado.
```

### 7. `/znve-forensic` — Ingesta pasiva y radiografía forense

- **Sintaxis:** `/znve-forensic --target=<ruta/módulo>`
- **Cuándo se usa:** Análisis inicial de archivos, repositorios desconocidos o monolitos legacy.
- **Restricción:** Solo lectura estricta. No propongas código de reemplazo ni dependencias.
- **Entornos recomendados:** Claude (Projects o Claude Code), DeepSeek R1 (razonamiento `<think>`), Copilot (`@workspace /znve-forensic`), Cursor en modo lectura.
- **Formato de entrega:**
  1. `RESUMEN DE DOMINIO` — función operativa real, en un párrafo.
  2. `MATRIZ DE ENTRADAS, SALIDAS Y ESTADO` — variables de entorno, parámetros, estado mutado y globales.
  3. `EFECTOS SECUNDARIOS` — persistencia, red, I/O e IPC.
  4. `EQUILIBRIOS ACCIDENTALES` — código duplicado o contradictorio que funciona por orden de evaluación. No lo "limpies": suele sostener comportamientos de negocio no documentados.
  5. `ZONAS ROJAS` — condiciones de carrera, desconexiones, nulos o saturación.
- **Ejemplo:**

```text
/znve-forensic --target=server/transfers/processor.ts Entrega la radiografía forense sin alterar nada.
```

### 8. `/znve-harness` — Arnés de caracterización (Golden Master)

- **Sintaxis:** `/znve-harness --target=<archivo_legacy>`
- **Cuándo se usa:** Antes de modernizar código legacy sin tests.
- **Restricción:** El archivo de producción no se modifica. El arnés vive aislado (`tests/characterization/` o `sandbox/`).
- **Entornos recomendados:** Claude Projects, Cursor, Copilot Chat, DeepSeek Reasoner.
- **Formato de entrega:**
  1. `CONFIGURACIÓN DE AISLAMIENTO` — invocación del módulo original intacto (CLI, importación o sandbox).
  2. `BATERÍA DE INYECCIÓN` — casos estándar, límites, strings vacíos y datos corruptos.
  3. `SNAPSHOTS GOLDEN MASTER` — salidas reales actuales, incluidos los comportamientos accidentales tolerados.
  4. `COMANDO DE EJECUCIÓN` — orden de terminal que certifique 100 % de éxito contra el original.
- **Ejemplo:**

```text
/znve-harness --target=legacy_calc.py Construye la batería Golden Master en tests/characterization/.
```

### 9. `/znve-legacy-rescue` — Protocolo integral en 5 fases

- **Sintaxis:** `/znve-legacy-rescue`
- **Cuándo se usa:** Rescate de un monolito o módulo legacy sin tests.
- **Restricción:** Orquesta el rescate de punta a punta y no avances de fase sin que la anterior esté verificada. En la primera respuesta entrega solo el reporte forense (fases 1 y 2) y el diseño del arnés (fase 3).
- **Entornos recomendados:** Claude Projects, Cursor Composer.
- **Fases:**
  1. **Fases 1 y 2 — Ingesta y reporte forense:** con `/znve-forensic`.
  2. **Fase 3 — Golden Master:** con `/znve-harness` sobre el código intacto; debe quedar 100 % en verde.
  3. **Fase 4 — Shadow Run:** nuevo módulo aislado (`/znve-contract` + `/znve-execute`) ejecutado en sombra hasta confirmar `Salida(Nuevo) == Salida(Legacy)`.
  4. **Fase 5 — Strangler Fig:** conmutación gradual sin downtime.
- **Ejemplo:**

```text
/znve-legacy-rescue Inicia el rescate integral del monolito legacy_billing.py.
```

### 10. `/znve-audit` — Auditoría forense de recursos y seguridad

- **Sintaxis:** `/znve-audit --target=<módulo>`
- **Cuándo se usa:** Fugas de memoria, cuellos de botella, bloqueos de UI, logs ruidosos o puertos expuestos.
- **Restricción:** Nada de parches cosméticos ni retardos arbitrarios; ataca la causa raíz y entrega la hoja de remediación para aprobación.
- **Entornos recomendados:** DeepSeek R1, Claude, Copilot, Ollama.
- **Formato de entrega:**
  1. `CONCURRENCIA E HILOS` — contención, bloqueos del UI Thread o procesos zombis.
  2. `SUPERFICIE DE RED Y SEGURIDAD` — timeouts, puertos expuestos y manejo de desconexión.
  3. `CICLO DE VIDA Y RECURSOS` — handles no liberados, listeners huérfanos o buffers saturados.
  4. `HOJA DE REMEDIACIÓN` — acciones atómicas priorizadas por severidad.
- **Ejemplo:**

```text
/znve-audit --target=src/workers Certifica que el worker libera sockets y no mantiene la CPU despierta.
```

---

## 🛠️ SECCIÓN 2: HERRAMIENTAS MCP (`znve_*`) PARA AGENTES AUTÓNOMOS

El servidor `protocols/mcp/znve-mcp-server.ts` expone estas herramientas por JSON-RPC (stdio). Las rutas se resuelven contra la variable `ZNVE_WORKSPACE`.

### 1. `znve_help`

- **Fase:** Ayuda
- **Qué hace:** Devuelve este manual completo o una sección: `commands`, `mcp_tools` o `modes`.
- **Parámetros:**
  - `topic` (enum, opcional): `all` (por defecto), `commands`, `mcp_tools` o `modes`.
- **Comportamiento:** Si el manual no existe, devuelve un catálogo corto de respaldo; cualquier otro error se informa.

### 2. `znve_forensic_scan`

- **Fase:** Ingesta
- **Qué hace:** Lee un archivo del workspace en modo estrictamente de solo lectura.
- **Parámetros:**
  - `file_path` (string, obligatorio): Ruta del archivo, relativa a `ZNVE_WORKSPACE`.
- **Comportamiento:** Devuelve el contenido intacto y su tamaño; nunca escribe en disco.

### 3. `znve_validate_contract`

- **Fase:** Contrato
- **Qué hace:** Valida que un DTO o interfaz cumpla el Anti-Bloat Fence y la proyección de datos.
- **Parámetros:**
  - `contract_code` (string, obligatorio): Código de la interfaz, struct o DTO propuesto.
  - `banned_libraries` (string[], opcional): Librerías vetadas por el Anti-Bloat Fence.
- **Comportamiento:** Rechaza el contrato si detecta `SELECT *`, `.find({})` o una librería vetada.

### 4. `znve_scaffold_harness`

- **Fase:** Aislamiento
- **Qué hace:** Crea una suite Golden Master en un directorio aislado sin tocar producción.
- **Parámetros:**
  - `harness_directory` (string, obligatorio): Directorio aislado; debe contener `test` o `sandbox`.
  - `test_filename` (string, obligatorio): Nombre del archivo de prueba.
  - `harness_code` (string, obligatorio): Código de la prueba de caja negra.
- **Comportamiento:** Rechaza directorios que no sean de pruebas o sandbox.

### 5. `znve_surgical_write`

- **Fase:** Escritura
- **Qué hace:** Escribe un único `TARGET_FILE` tras aprobar el contrato.
- **Parámetros:**
  - `target_file` (string, obligatorio): Ruta exacta del único archivo a escribir.
  - `code_content` (string, obligatorio): Contenido que satisface el contrato.
  - `disposal_pattern` (enum, obligatorio): `dispose`, `close`, `finally`, `autocloseable` o `not_applicable`.
- **Comportamiento:** Aborta si hay un `catch` vacío o si se abren sockets o flujos con `not_applicable`.

### 6. `znve_audit_resources`

- **Fase:** Hardening
- **Qué hace:** Analiza un fragmento de código en busca de antipatrones de hilos, memoria y CPU.
- **Parámetros:**
  - `code_snippet` (string, obligatorio): Fragmento de código a evaluar.
- **Comportamiento:** Marca `.Result`/`.Wait()`, busy-waiting sin backoff y `WakeLock.acquire()`.

---

## 💻 SECCIÓN 3: CONFIGURACIÓN POR HERRAMIENTA E IA

### 1. Claude (claude.ai, Claude Code y Claude Projects)

- claude.ai: sube `protocols/agents/claude/skills/znve.zip` en **Settings → Capabilities → Skills**.
- Claude Code: copia la carpeta `protocols/agents/claude/skills/znve/` a `~/.claude/skills/` o a `.claude/skills/` del proyecto.
- Claude Projects: pega `protocols/agents/claude-system-skills.md` en **Project Instructions** o en `CLAUDE.md`.
- Invocación: `/znve-contract`, `/znve contract` o `/znve -contract`.

### 2. GitHub Copilot (VS Code, Visual Studio, JetBrains)

- Usa `.github/copilot-instructions.md`: es la ruta que Copilot lee.
- En el chat: `@workspace /znve-*`.

### 3. Cursor y Windsurf

- Copia `protocols/agents/cursor-rules.md` a `.cursorrules` en la raíz del proyecto.

### 4. DeepSeek (web, API o extensión)

- Inyecta `protocols/agents/deepseek-directive.md` como mensaje con rol `system`.
- En R1 (Reasoner), las 4 fases de validación ocurren dentro de `<think>`.

### 5. Ollama (modelos locales)

- Compila el agente local con el `Modelfile`:

```bash
ollama create znve-agent -f ./protocols/agents/ollama/Modelfile
ollama run znve-agent
```

### 6. OpenRouter

- Usa `protocols/agents/openrouter/system-prompt.md` como prompt de sistema y `response-schema.json` como `response_format`.

### 7. Antigravity y clientes MCP (Cursor, Windsurf, Claude Desktop)

- Instala el servidor MCP (compila, verifica las 6 herramientas y registra `znve-engine`):

```bash
cd protocols/mcp
node install-antigravity.mjs --workspace "<ruta>/tu-proyecto"
```

- O regístralo a mano en `mcp_config.json`:

```json
{
  "mcpServers": {
    "znve-engine": {
      "command": "node",
      "args": ["<ruta>/znve-spec/protocols/mcp/dist/znve-mcp-server.js"],
      "env": {
        "ZNVE_WORKSPACE": "<ruta>/tu-proyecto",
        "NODE_ENV": "production"
      }
    }
  }
}
```

---

## 🔄 SECCIÓN 4: MODOS OPERATIVOS Y FLUJOS PASO A PASO

1. **Modo 1: Greenfield (proyectos nuevos, día 0)** — `/znve-contract` → `/znve-execute`
2. **Modo 2: In-Flight (proyectos activos y nuevas capacidades)** — `/znve-contract --delta` → `/znve-execute`
3. **Modo 3: Hotfix & Recovery (triaje de crisis en producción)** — `/znve-triage` → `/znve-hotfix`
4. **Modo 4: Modern Maintenance (migración de SDKs y breaking changes)** — `/znve-upgrade`
5. **Modo 5: Legacy Rescue (refactorización en 5 fases de monolitos críticos)** — `/znve-forensic`, `/znve-harness`, `/znve-legacy-rescue`
6. **Modo 6: Audit & Hardening (higiene técnica, memoria y seguridad)** — `/znve-audit`

### Flujo A: Creación de módulo nuevo (Modo 1 - Greenfield)

```text
1. Usuario  --> Inyecta el requerimiento con /znve-contract
2. Agente   --> Retorna DTO tipado + esquema + Anti-Bloat Fence y se detiene
3. Usuario  --> Revisa y aprueba el contrato inmutable
4. Usuario  --> Dispara /znve-execute sobre el contrato aprobado
5. Agente   --> Genera TARGET_FILE con desecho de recursos y test atómico
6. Terminal --> Ejecuta el comando de validación para certificar la paridad
```

### Flujo B: Crisis en producción (Modo 3 - Hotfix)

```text
1. Usuario  --> Pega el error o stack trace con /znve-triage
2. Agente   --> Identifica la causa raíz y delimita el radio de impacto (solo lectura)
3. Usuario  --> Autoriza la intervención y dispara /znve-hotfix
4. Agente   --> Modifica un único TARGET_FILE e incluye test de regresión
5. Terminal --> Corre el test de regresión (100 % verde) antes de desplegar
```

### Flujo C: Rescate de monolito legacy (Modo 5 - Legacy Rescue)

```text
1. Usuario  --> Ejecuta /znve-forensic sobre el archivo monolítico (Zero-Touch)
2. Agente   --> Emite el reporte forense con contratos implícitos y zonas rojas
3. Usuario  --> Ejecuta /znve-harness
4. Agente   --> Despliega la suite Golden Master en tests/characterization/ (legacy intacto)
5. Usuario  --> Verifica que el test sobre el código original quede 100 % verde
6. Usuario  --> Ejecuta /znve-execute para el nuevo módulo en sandbox
7. Agente   --> Ejecuta en sombra validando Salida(Nuevo) == Salida(Legacy)
8. Usuario  --> Despliega el módulo nuevo gradualmente con Strangler Fig
```
