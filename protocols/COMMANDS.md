```markdown
# ==============================================================================
# ZNVE COMMANDS & TOOLS SPECIFICATION (MANUAL DE COMANDOS Y MCP)
# Archivo: protocols/COMMANDS.md
# Versión: 2.2.0
# Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
# Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
# ==============================================================================

Este documento recopila el catálogo maestro de comandos agénticos (`/znve-*`), herramientas de contexto de modelo (MCP Tools) y directivas de ejecución utilizadas durante el ciclo de vida del software bajo el estándar Zero-Noise Vibe Engineering (ZNVE).

---

## 🧭 TABLA DE REFERENCIA RÁPIDA

| Comando / Herramienta | Tipo | Modos Aplicables | Entornos e IAs Compatibles |
|---|---|---|---|
| `/znve-forensic` | Slash Command | Modo 2, 5, 6 | Claude, Cursor, Copilot, DeepSeek, OpenRouter, Ollama |
| `/znve-contract` | Slash Command | Modo 1, 2, 4 | Claude, Cursor, Copilot, DeepSeek, OpenRouter, Ollama |
| `/znve-harness` | Slash Command | Modo 5 | Claude, Cursor, Copilot, DeepSeek, OpenRouter, Ollama |
| `/znve-execute` | Slash Command | Modo 1, 2, 4, 5 | Claude, Cursor, Copilot, DeepSeek, OpenRouter, Ollama |
| `/znve-triage` | Slash Command | Modo 3 (Hotfix) | Claude, Cursor, Copilot, DeepSeek, OpenRouter |
| `/znve-hotfix` | Slash Command | Modo 3 (Hotfix) | Claude, Cursor, Copilot, DeepSeek, OpenRouter |
| `/znve-upgrade` | Slash Command | Modo 4 (Upgrade) | Claude, Cursor, Copilot, DeepSeek, OpenRouter |
| `/znve-audit` | Slash Command | Modo 6 (Hardening) | Claude, Cursor, Copilot, DeepSeek, OpenRouter, Ollama |
| `/znve-legacy-rescue` | Slash Command | Modo 5 (Legacy) | Claude, Cursor, Copilot, DeepSeek, OpenRouter |
| `znve_forensic_scan` | MCP Tool (JSON-RPC) | Fases de Ingesta | Antigravity, Cursor MCP, Claude Desktop, Windsurf |
| `znve_validate_contract` | MCP Tool (JSON-RPC) | Fase Contractual | Antigravity, Cursor MCP, Claude Desktop, Windsurf |
| `znve_scaffold_harness` | MCP Tool (JSON-RPC) | Fase de Aislamiento | Antigravity, Cursor MCP, Claude Desktop, Windsurf |
| `znve_surgical_write` | MCP Tool (JSON-RPC) | Fase de Escritura | Antigravity, Cursor MCP, Claude Desktop, Windsurf |
| `znve_audit_resources` | MCP Tool (JSON-RPC) | Fase de Hardening | Antigravity, Cursor MCP, Claude Desktop, Windsurf |

---

## 🎛️ SECCIÓN 1: COMANDOS DE BARRA (`/znve-*`) PARA ASISTENTES Y AGENTES

Los comandos de barra son palabras clave de activación que instruyen al modelo de lenguaje a adoptar un rol técnico cerrado, restringir sus capacidades generativas e imponer un formato de salida estandarizado.

### 1. `/znve-forensic` (Ingesta Pasiva & Radiografía)
* **Propósito:** Analizar un archivo o repositorio desconocido extrayendo su grafo de ejecución y efectos secundarios sin modificar el disco.
* **Entornos recomendados:**
  * **Claude:** Modo Projects o Claude Code CLI.
  * **DeepSeek (R1):** Aprovecha la cadena de razonamiento `<think>` para trazar flujos sin emitir código.
  * **GitHub Copilot:** `@workspace /znve-forensic` en la ventana de chat.
  * **Cursor / Windsurf:** En el Composer o Chat en modo lectura.
* **Restricción estricta:** MODO SOLO LECTURA. Prohibido proponer código de reemplazo, refactorizaciones o parches.
* **Formato de entrega:**
  1. `RESUMEN DE DOMINIO`: Propósito operativo del archivo.
  2. `MATRIZ IO`: Parámetros de entrada, variables globales y estado mutado.
  3. `SIDE EFFECTS`: Operaciones en almacenamiento, red, disco e IPC.
  4. `EQUILIBRIOS ACCIDENTALES`: Funciones duplicadas o código contradictorio con coexistencia funcional por orden de evaluación.
  5. `ZONAS ROJAS`: Riesgos de fuga, condiciones de carrera, bloqueos o excepciones no gestionadas.
* **Ejemplo de uso:**
  ```text
  /znve-forensic Analiza el archivo server/transfers/processor.ts y entrega la radiografía forense sin alterar nada.

```

---

### 2. `/znve-contract` (Diseño de Contratos Deterministas)

* **Propósito:** Definir formalmente las fronteras de datos, tipos de error y restricciones operativas antes de escribir cualquier algoritmo interno.


* **Entornos recomendados:** Claude 3.5 Sonnet, GPT-4o (OpenRouter), DeepSeek V3, Ollama (`qwen2.5-coder`).


* **Restricción estricta:** Prohibido escribir lógica de negocio interna. Definir únicamente estructuras de datos, interfaces y esquemas inmutables.


* **Formato de entrega:**
1. `CONTRATO IO`: DTOs e interfaces inmutables de entrada y salida con tipos cerrados.


2. `CONTRATO PERSISTENCIA`: Esquema agnóstico al motor con proyecciones y claves indexadas explícitas.


3. `CONTRATO ERRORES`: Tipos cerrados con los modos de fallo tolerados.


4. `ANTI-BLOAT FENCE`: Lista explícita de librerías externas vetadas y prohibiciones arquitectónicas.




* **Ejemplo de uso:**
```text
/znve-contract Diseña el contrato DTO y persistencia para un almacén local clave-valor persistente en disco.

```



---

### 3. `/znve-harness` (Arnés de Caracterización / Golden Master)

* **Propósito:** Congelar el comportamiento actual de código legacy sin tests mediante pruebas de caja negra, garantizando paridad antes de modernizar.


* **Entornos recomendados:** Claude Projects, Cursor, Copilot Chat, DeepSeek Reasoner.


* **Restricción estricta:** EL CÓDIGO PRODUCTIVO ORIGINAL NO SE MODIFICA. El arnés reside exclusivamente en un directorio aislado (`tests/characterization/` o `sandbox/`).


* **Formato de entrega:**
1. `UBICACIÓN`: Directorio aislado de pruebas.


2. `BATERÍA DE INYECCIÓN`: Casos válidos, límites numéricos, cadenas vacías y datos corruptos.


3. `SNAPSHOTS`: Registro de salidas reales actuales (incluso comportamientos accidentales tolerados).


4. `COMANDO EJECUTABLE`: Comando de terminal exacto para certificar 100% de éxito contra el código legacy intacto.




* **Ejemplo de uso:**
```text
/znve-harness Construye una batería Golden Master en tests/characterization/ para congelar el comportamiento de legacy_calc.py.

```



---

### 4. `/znve-execute` (Implementación Quirúrgica Atómica)

* **Propósito:** Generar la implementación de código que cumple estrictamente un contrato previamente aprobado.


* **Entornos recomendados:** Cursor Composer, Copilot Edits, Windsurf, Claude Code CLI, Ollama Local.


* **Restricción estricta:** Prohibido agregar librerías externas parásitas. Prohibido inventar propiedades fuera del contrato. Prohibido añadir bloques `catch` vacíos.


* **Formato de entrega:**
1. `TARGET_FILE`: Ruta exacta del único archivo a crear o intervenir.


2. `CÓDIGO ATÓMICO`: Implementación quirúrgica basada en APIs nativas y mínimas operaciones.


3. `LIBERACIÓN DE RECURSOS`: Bloque determinista de desecho (`dispose`, `close`, `finally`).


4. `VERIFICACIÓN ATÓMICA`: Test ejecutable o comando terminal para validar la paridad de inmediato.




* **Ejemplo de uso:**
```text
/znve-execute Implementa el contrato UserSessionContract en src/auth/session.ts utilizando utilidades nativas de crypto.

```



---

### 5. `/znve-triage` (Diagnóstico de Emergencia en Producción)

* **Propósito:** Analizar caídas de servicio, bloqueos o excepciones no controladas en aplicaciones modernas activas (Modo 3).


* **Entornos recomendados:** Claude, Cursor, Copilot, DeepSeek R1.


* **Restricción estricta:** MODO SOLO LECTURA. Prohibido aplicar parches a ciegas (*monkey-patching*) o alterar contratos de datos públicos.


* **Formato de entrega:**
1. `COMPONENTE AFECTADO`: Archivo, endpoint o vista que manifiesta el síntoma.


2. `CAUSA RAÍZ`: Diagnóstico determinista (deadlock, pool agotado, fuga de memoria, timeout).


3. `RADIO DE IMPACTO & CONTENCIÓN`: Plan de aislamiento inmediato (fallback local, degradación elegante) sin mutar contratos públicos.




* **Ejemplo de uso:**
```text
/znve-triage Analiza este log de error de conexión a la base de datos y aísla el radio de impacto: [pegar stack trace].

```



---

### 6. `/znve-hotfix` (Parche Quirúrgico Bounded de Producción)

* **Propósito:** Remediar una falla crítica en producción diagnosticada previamente mediante `/znve-triage` (Modo 3).


* **Entornos recomendados:** Cursor, Claude Code, GitHub Copilot.


* **Restricción estricta:** Modificación restringida estrictamente a un único `TARGET_FILE`. Prohibido alterar firmas públicas de métodos.


* **Formato de entrega:**
1. `TARGET_FILE`: Ruta exacta del archivo con la falla.


2. `CÓDIGO QUIRÚRGICO`: Parche atómico acotado.


3. `TEST DE REGRESIÓN`: Prueba unitaria que falla sin el hotfix y pasa al 100% tras aplicarlo.


4. `COMANDO DE VALIDACIÓN`: Orden terminal para ejecutar la prueba de forma reproducible.




* **Ejemplo de uso:**
```text
/znve-hotfix Aplica el parche correctivo sobre src/network/http_client.ts con su respectivo test de regresión.

```



---

### 7. `/znve-upgrade` (Migración con Capa Anti-Corrupción)

* **Propósito:** Actualizar versiones mayores de SDKs, APIs de terceros o dependencias que introducen *breaking changes* (Modo 4).


* **Entornos recomendados:** Claude Projects, Cursor, DeepSeek.


* **Restricción estricta:** Prohibido modificar la lógica del dominio central; los cambios disruptivos deben aislarse detrás de un adaptador.


* **Formato de entrega:**
1. `MATRIZ DE BREAKING CHANGES`: Tabla comparando versión previa vs. versión objetivo.


2. `DISEÑO DE ADAPTADOR`: Interfaz interna (`Port`) y adaptador desacoplado (`Adapter`).


3. `VERIFICACIÓN DUAL`: Pruebas de paridad funcional y huella de memoria.




* **Ejemplo de uso:**
```text
/znve-upgrade Planifica la migración de Axios a fetch nativo diseñando un adaptador HTTP interno desacoplado.

```



---

### 8. `/znve-audit` (Auditoría Forense y Rendimiento)

* **Propósito:** Diagnóstico de consumo de CPU, retención de sockets, contención de hilos de interfaz gráfica o puertos expuestos (Modo 6).


* **Entornos recomendados:** DeepSeek R1, Claude, Copilot, Ollama.


* **Restricción estricta:** Prohibido aplicar parches cosméticos o retardos arbitrarios (`sleep`, `setTimeout`).


* **Formato de entrega:**
1. `HILOS Y CONCURRENCIA`: Bloqueos de UI Thread, sincronización bloqueante (.Result/.Wait()).


2. `SUPERFICIE DE RED`: Puertos expuestos fuera de loopback y políticas de timeout.


3. `FUGAS Y CICLO DE VIDA`: Descriptores abiertos, listeners huérfanos y memory leaks.


4. `HOJA DE REMEDIACIÓN`: Lista priorizada de acciones atómicas por causa raíz.




* **Ejemplo de uso:**
```text
/znve-audit Audita este worker en segundo plano para certificar que libera sockets y no mantiene la CPU despierta.

```



---

### 9. `/znve-legacy-rescue` (Protocolo Integral en 5 Fases)

* **Propósito:** Orquestar de punta a punta la modernización de un archivo monolítico sin tests (Modo 5).


* **Entornos recomendados:** Claude Projects, Cursor Composer.


* **Flujo inmutable:**
* Fase 1 y 2: Radiografía e Ingesta Pasiva (`/znve-forensic`).


* Fase 3: Arnés de Caracterización Golden Master (`/znve-harness`).


* Fase 4: Shadow Run en módulo desacoplado validando `Salida(Nuevo) == Salida(Legacy)`.


* Fase 5: Conmutación gradual (Strangler Fig) sin downtime.




* **Ejemplo de uso:**
```text
/znve-legacy-rescue Inicia el rescate integral del monolito legacy_billing.py siguiendo las 5 fases.

```



---

## 🛠️ SECCIÓN 2: HERRAMIENTAS MCP (`znve_*`) PARA AGENTES AUTÓNOMOS

Las herramientas del Model Context Protocol (MCP) actúan como barandillas físicas expuestas por el servidor `protocols/mcp/znve-mcp-server.ts`. Los agentes como **Antigravity**, **Cursor** o **Claude Desktop** invocan estas funciones mediante llamadas a herramientas estructuradas (JSON-RPC).

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENTE AUTÓNOMO                          │
│               (Antigravity / Cursor / Claude)               │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON-RPC (Tool Calls)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 ZNVE MCP PROTOCOL SERVER                    │
│                                                             │
│  1. znve_forensic_scan      --> Ingesta en solo lectura     │
│  2. znve_validate_contract  --> Validación Anti-Bloat       │
│  3. znve_scaffold_harness   --> Despliegue Golden Master    │
│  4. znve_surgical_write     --> Escritura en TARGET_FILE    │
│  5. znve_audit_resources    --> Detección de antipatrones   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Aislamiento en disco
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE ARCHIVOS                      │
└─────────────────────────────────────────────────────────────┘

```

### 1. `znve_forensic_scan`

* **Definición:** Lee el contenido íntegro de un archivo objetivo en modo estrictamente de solo lectura.


* **Cuándo se usa:** En las Fases 1 y 2 para alimentar el contexto del agente sin permitirle escribir en disco.


* **Parámetros (`inputSchema`):**
* `file_path` *(string, obligatorio)*: Ruta relativa o absoluta del archivo a inspeccionar.




* **Respuesta del servidor:** Snapshot inmutable con el recuento exacto de bytes y contenido intacto.



### 2. `znve_validate_contract`

* **Definición:** Valida que una especificación de interfaz o DTO cumpla las cláusulas de higiene de dependencias y proyección de datos antes de programar.


* **Cuándo se usa:** Tras definir un DTO y antes de autorizar la escritura de código.


* **Parámetros (`inputSchema`):**
* `contract_code` *(string, obligatorio)*: Código fuente de la interfaz, struct o DTO propuesto.


* `banned_libraries` *(array de strings, opcional)*: Lista de librerías vetadas por el Anti-Bloat Fence.




* **Comportamiento determinista:** Falla automáticamente y devuelve `REJECTED` si detecta consultas no proyectadas (`SELECT *`, `find({})`) o dependencias prohibidas.



### 3. `znve_scaffold_harness`

* **Definición:** Crea una suite de caracterización (Golden Master) en un directorio de aislamiento sin modificar los archivos de producción.


* **Cuándo se usa:** En la Fase 3 del rescate legacy.


* **Parámetros (`inputSchema`):**
* `harness_directory` *(string, obligatorio)*: Directorio aislado (debe contener obligatoriamente `test` o `sandbox`).


* `test_filename` *(string, obligatorio)*: Nombre del archivo de prueba.


* `harness_code` *(string, obligatorio)*: Código de la prueba de caja negra.




* **Comportamiento determinista:** El servidor rechaza la creación si el directorio de destino intenta mezclarse con la raíz de producción.



### 4. `znve_surgical_write`

* **Definición:** Permite persistir cambios en disco de forma atómica y controlada.


* **Cuándo se usa:** En la Fase 4 de implementación tras aprobar el contrato.


* **Parámetros (`inputSchema`):**
* `target_file` *(string, obligatorio)*: Ruta exacta del único archivo a escribir.


* `code_content` *(string, obligatorio)*: Contenido fuente que satisface el contrato.


* `disposal_pattern` *(enum, obligatorio)*: Patrón de desecho de recursos (`dispose`, `close`, `finally`, `autocloseable`, `not_applicable`).




* **Comportamiento determinista:** Falla automáticamente y aborta la escritura si:
* El código contiene bloques `catch` vacíos.


* Se abren sockets, conexiones o flujos declarando `disposal_pattern: "not_applicable"`.





### 5. `znve_audit_resources`

* **Definición:** Analizador estático de código que detecta patrones lesivos para la memoria, hilos y CPU.


* **Cuándo se usa:** En auditorías de hardening o durante revisiones previas al commit.


* **Parámetros (`inputSchema`):**
* `code_snippet` *(string, obligatorio)*: Fragmento de código a evaluar.




* **Detección automática:** Identifica bloqueos del despachador de UI (`.Result`, `.Wait()`), busy-waiting sin jitter, y retenciones no administradas como `WakeLock.acquire()`.



---

## 💻 SECCIÓN 3: MATRIZ DE CONFIGURACIÓN POR HERRAMIENTA E IA

Instrucciones exactas de integración para activar los comandos y herramientas según la plataforma elegida:

### 1. Claude (Anthropic)

* **Dónde configurar:** En la sección **Project Instructions** (Claude Projects) o en el archivo de reglas locales.


* **Archivo de origen:** Pegar el contenido de `protocols/agents/claude-system-skills.md`.


* **Invocación:** Directa mediante barra (`/znve-forensic`, `/znve-contract`, etc.).



### 2. GitHub Copilot (VS Code / JetBrains / Visual Studio)

* **Dónde configurar:** En `.github/copilot-instructions.md` en la raíz del repositorio.


* **Comportamiento:** Indexa las reglas de autocompletado inline y habilita los comandos en el panel de chat invocando `@workspace /znve-*`.



### 3. DeepSeek (Web, API o IDE Extension)

* **Dónde configurar:** Inyectar `protocols/agents/deepseek-directive.md` como mensaje inicial con rol `system`.


* **Modo R1 Reasoner:** El modelo canaliza las 4 fases de validación mental dentro de su bloque `<think>` antes de emitir los artefactos técnicos.



### 4. Ollama (Modelos Locales CLI)

* **Dónde configurar:** Compilar el agente local mediante `protocols/agents/ollama/Modelfile`:


```bash
ollama create znve-agent -f ./protocols/agents/ollama/Modelfile
ollama run znve-agent

```


* **Invocación:** Escribir el comando directamente en el prompt interactivo de la terminal.



### 5. Antigravity & IDEs con Soporte MCP (Cursor, Windsurf, Claude Desktop)

* **Dónde configurar:** Registrar el servidor en el archivo de configuración JSON del cliente MCP (`mcp_config.json`):


```json
{
  "mcpServers": {
    "znve-core": {
      "command": "node",
      "args": ["protocols/mcp/znve-mcp-server.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}

```


* **Operación:** El agente detecta las capacidades expuestas y llama automáticamente a `znve_forensic_scan`, `znve_validate_contract` o `znve_surgical_write` según la fase de la tarea.



---

## 🔄 SECCIÓN 4: FLUJOS OPERATIVOS COMPLETOS (WORKFLOWS PASO A PASO)

### Flujo A: Creación de Módulo Nuevo (Modo 1 - Greenfield)

```text
1. Usuario  --> Inyecta requerimiento con /znve-contract
2. Agente   --> Retorna DTO tipado + Esquema + Anti-Bloat Fence
3. Usuario  --> Revisa y aprueba el contrato inmutable
4. Usuario  --> Dispara /znve-execute sobre el contrato aprobado
5. Agente   --> Genera TARGET_FILE con desecho de recursos y test atómico
6. Terminal --> Ejecuta el comando de validación para certificar la paridad

```

### Flujo B: Crisis en Producción (Modo 3 - Hotfix)

```text
1. Usuario  --> Pega el error o stack trace acompañado de /znve-triage
2. Agente   --> Identifica causa raíz determinista y delimita radio de impacto (solo lectura)
3. Usuario  --> Autoriza la intervención y dispara /znve-hotfix
4. Agente   --> Modifica exclusivamente un único TARGET_FILE e incluye test de regresión
5. Terminal --> Corre el test de regresión (100% verde) antes de desplegar a producción

```

### Flujo C: Rescate de Monolito Legacy (Modo 5 - Legacy Rescue)

```text
1. Usuario  --> Ejecuta /znve-forensic sobre el archivo monolítico (Zero-Touch)
2. Agente   --> Emite el Reporte Forense con contratos implícitos y zonas rojas
3. Usuario  --> Ejecuta /znve-harness
4. Agente   --> Despliega suite Golden Master en tests/characterization/ (Legacy intacto)
5. Usuario  --> Verifica que el test sobre el código original quede 100% verde
6. Usuario  --> Ejecuta /znve-execute para diseñar el nuevo módulo en sandbox
7. Agente   --> Realiza ejecución dual en sombra validando Salida(Nuevo) == Salida(Legacy)
8. Usuario  --> Despliega el módulo nuevo gradualmente mediante Strangler Fig

```

```

```
