# GUÍA MAESTRA DE PROMPTS ZNVE (ZERO-NOISE VIBE ENGINEERING)
**Catálogo de Prompts Genéricos para Agentes de IA (Claude, Gemini, Cursor, Windsurf, Copilot, DeepSeek, Ollama, OpenRouter, Antigravity)**
*Versión: 2.3.0 | Estándar: Spec-Driven Agentic Architecture*

---

## 🎯 PROPÓSITO
Esta guía contiene las plantillas de prompts optimizadas para ejecutar los comandos del estándar **ZNVE**. Cada prompt establece de manera estricta el **perímetro de acción**, las **restricciones absolutas**, el **objetivo atómico (`TARGET_FILE`)** y los **criterios de parada** para eliminar el "bucle de muerte de la IA" (*AI agentic drift*), evitar la inyección de código parásito y asegurar entregas deterministas.

**Determinismo.** El determinismo de ZNVE viene del contrato y de los tests, no de los parámetros de muestreo: en modo de razonamiento varios proveedores ignoran `temperature`, y dos peticiones idénticas pueden responder distinto aunque una se sirva desde la caché. Bajar la temperatura reduce la variación, no la garantiza; lo que se verifica es el resultado contra el contrato.

Los formatos de salida exactos de cada comando están en [COMMANDS.md](COMMANDS.md). Los comandos se pueden escribir como `/znve-contract`, `/znve contract` o `/znve -contract`.

---

## 📋 ÍNDICE DE COMANDOS

| # | Comando | Modo | Cuándo usarlo |
|---|---|---|---|
| 0 | [`/znve-help`](#0-znve-help-catálogo-y-ayuda) | Todos | Ver el catálogo de comandos y la regla de 4 bloques. |
| 1 | [`/znve-contract`](#1-znve-contract-inicio-greenfield--recomendación-de-stack) | 1, 4 | Iniciar un proyecto y recomendar el stack por plataforma. |
| 2 | [`/znve-contract --delta`](#2-znve-contract---delta-análisis-incremental-en-proyectos-iniciados) | 2 | Añadir capacidades a un proyecto en desarrollo. |
| 3 | [`/znve-execute`](#3-znve-execute-ejecución-quirúrgica-de-código) | 1, 2, 4, 5 | Implementar bajo un contrato aprobado. |
| 4 | [`/znve-triage`](#4-znve-triage-diagnóstico-de-emergencia) | 3 | Diagnosticar una caída en producción, en solo lectura. |
| 5 | [`/znve-hotfix`](#5-znve-hotfix-parche-quirúrgico-acotado) | 3 | Aplicar el parche tras el triaje, con test de regresión. |
| 6 | [`/znve-upgrade`](#6-znve-upgrade-actualización-de-dependencias-con-breaking-changes) | 4 | Migrar un SDK con breaking changes mediante un adaptador. |
| 7 | [`/znve-forensic`](#7-znve-forensic-diagnóstico-estático-de-solo-lectura) | 2, 5, 6 | Analizar código sin tocar el disco (*Zero-Touch*). |
| 8 | [`/znve-harness`](#8-znve-harness-arnés-de-caracterización-golden-master) | 5 | Congelar código frágil en una suite Golden Master. |
| 9 | [`/znve-legacy-rescue`](#9-znve-legacy-rescue-rescate-integral-en-5-fases) | 5 | Orquestar el rescate legacy completo. |
| 10 | [`/znve-audit`](#10-znve-audit-auditoría-de-recursos-rendimiento-y-ruido) | 6 | Auditar hilos, memoria, red, seguridad y ruido. |

---

## 0. `/znve-help` (Catálogo y Ayuda)

**Cuándo usar:** Para comprobar que ZNVE está instalado en el asistente o recordar los comandos disponibles.

```text
/znve-help
```

La respuesta esperada es el catálogo de 10 comandos, la regla de 4 bloques y un ejemplo de uso, sin texto adicional.

---

## 1. `/znve-contract` (Inicio Greenfield & Recomendación de Stack)

**Cuándo usar:** Al iniciar un módulo o proyecto nuevo desde cero.

```text
/znve-contract --platform=[desktop|web|mobile|hybrid]
Iniciaremos el diseño del módulo [NOMBRE_DEL_MÓDULO] para una aplicación tipo [ESCRITORIO / WEB / ANDROID / HÍBRIDA / MACOS].

RESTRICCIONES ABSOLUTAS:
1. Poda de Contexto: Prohibido escribir código de implementación en src/.
2. Anti-Bloat Fence: Prohibido agregar librerías externas que no pertenezcan al SDK nativo o runtime base, salvo excepción justificada (el SDK nativo no ofrece la capacidad; documenta qué resuelve, su peso y la alternativa nativa descartada).

REQUERIMIENTO DE EJECUCIÓN:
1. Recomienda el stack técnico optimizado (Tooling, Persistencia/BD y UI si aplica) para la plataforma [TIPO_DE_APP].
2. Diseña los DTOs e Interfaces inmutables en `contracts/[modulo].contract.[ts/py]`.
3. Aplica la Lista de Chequeo de Solidez:
   [ ] Estructura invariable (Entradas, salidas, entidades y Enums tipados).
   [ ] Defensas de frontera (Tipos de error explicitados, sin 'any').
   [ ] Cero dependencias parásitas (Solo primitivos, SDKs autorizados o excepciones justificadas).
   [ ] Filtro de diferimiento (Ideas secundarias a contracts/CONTRACT_BACKLOG.md).
4. Si la lista se cumple al 100%, emite el Criterio de Parada Obligatorio: "Contrato v1 sólido y cerrado. Listo para /znve-execute." y DETÉN la generación.
```

---

## 2. `/znve-contract --delta` (Análisis Incremental en Proyectos Iniciados)

**Cuándo usar:** Para agregar nuevas capacidades a un módulo existente o reorientar el desarrollo por etapas.

```text
/znve-contract --delta
Realizaremos una auditoría de discrepancias para incorporar la nueva capacidad [DESCRIPCIÓN_DE_LA_FUNCIONALIDAD] en el módulo [NOMBRE_DEL_MÓDULO].

TARGET CONTRATO: `contracts/[modulo].contract.[ts/py]`
TARGET CÓDIGO ACTUAL: `src/[ruta/modulo_existente]`

REQUERIMIENTO DE EJECUCIÓN:
1. Compara el contrato en contracts/ con la implementación real e identifica tipos o campos faltantes.
2. Clasifica los cambios en dos cubos:
   - CUBO A (Requerido Ya): Tipos mínimos indispensables para la etapa actual.
   - CUBO B (Diferido): Sugerencias secundarias. Escríbelas en `contracts/CONTRACT_BACKLOG.md`.
3. Los contratos existentes se extienden, no se alteran.
4. Muestra el diff del contrato actualizado para el CUBO A y solicita mi aprobación antes de cualquier escritura de código.
```

---

## 3. `/znve-execute` (Ejecución Quirúrgica de Código)

**Cuándo usar:** Para escribir la lógica interna de un archivo específico una vez que el contrato en `contracts/` está congelado y aprobado.

```text
/znve-execute --target=src/[modulo]/[servicio_especifico].[ext]
Contrato aprobado. Implementa la lógica de negocio.

RESTRICCIONES ABSOLUTAS:
1. Prohibido tocar cualquier archivo fuera de TARGET_FILE.
2. Desecho Determinista: Implementa explícitamente el patrón de liberación de recursos (finally / dispose / close / unbind).
3. Cero Ruido: Prohibidos bloques try/catch vacíos y logs rutinarios de depuración ("OK", "Paso por aquí").
4. Tipado Estricto: Usa exclusivamente los DTOs definidos en `contracts/[modulo].contract.[ext]`.

ENTREGA ESPERADA:
1. Código completo y quirúrgico del TARGET_FILE.
2. Comando terminal ejecutable para correr la prueba unitaria de verificación.
```

---

## 4. `/znve-triage` (Diagnóstico de Emergencia)

**Cuándo usar:** Ante una caída de servicio, un bloqueo de UI o una excepción imprevista en producción, antes de tocar código.

```text
/znve-triage
Incidente: [CÓDIGO_O_DESCRIPCIÓN_DEL_INCIDENTE] en el servicio [NOMBRE_DEL_SERVICIO].
Evidencia: [STACK TRACE / LOGS / MÉTRICAS]

DIRECTIVA: MODO SOLO LECTURA. Prohibido proponer parches a ciegas o alterar contratos públicos.

ENTREGA:
1. COMPONENTE AFECTADO: archivo, endpoint o vista donde se manifiesta la falla.
2. CAUSA RAÍZ DETERMINISTA: deadlock, pool agotado, timeout, fuga de memoria, etc.
3. RADIO DE IMPACTO: componentes en riesgo.
4. PLAN DE CONTENCIÓN INMEDIATA: fallback local o degradación elegante sin alterar contratos de datos.
```

---

## 5. `/znve-hotfix` (Parche Quirúrgico Acotado)

**Cuándo usar:** Tras el diagnóstico de `/znve-triage`, para corregir el fallo conteniendo el radio de impacto dentro de la capa de adaptación.

```text
/znve-hotfix --incident=[ID]
Aplica el parche para el incidente diagnosticado en [NOMBRE_DEL_SERVICIO].

PERÍMETRO DE CONTENCIÓN:
- TARGET_FILE: `src/adapters/[adaptador_afectado].[ext]`
- BLAST RADIUS: La corrección debe estar aislada dentro del adaptador. Prohibido reestructurar la base de datos, el núcleo de la aplicación o las firmas públicas.

REQUERIMIENTO:
1. Inyecta un identificador de trazabilidad (X-Run-ID / correlation_id) en el punto de fallo.
2. Aplica el parche mínimo defensivo con validación estricta de frontera, sin catch vacíos.
3. Escribe el test de regresión en `tests/regression/test_incident_[ID].[ext]`: debe fallar sin el parche y pasar al 100% con él.
4. Entrega el diff quirúrgico y el comando exacto de validación.
```

---

## 6. `/znve-upgrade` (Actualización de Dependencias con Breaking Changes)

**Cuándo usar:** Para migrar o actualizar SDKs/librerías externas aislando las roturas mediante una Capa Anti-Corrupción.

```text
/znve-upgrade --dependency=[NOMBRE_LIBRERÍA]
Migraremos la integración de [NOMBRE_LIBRERÍA_ANTIGUA] a [NOMBRE_LIBRERÍA_NUEVA], que introduce breaking changes.

ESTRATEGIA ANTI-CORRUPCIÓN:
1. Entrega la matriz de breaking changes (versión previa vs. versión objetivo).
2. Mantén inmutable el contrato interno en `contracts/[servicio].contract.[ext]`.
3. TARGET_FILE: Construye o actualiza el adaptador en `src/adapters/[servicio]_adapter.[ext]`.
4. Absorbe todos los breaking changes de la nueva librería dentro del adaptador. El resto de la aplicación no debe enterarse del cambio de SDK.
5. Muestra la prueba unitaria que valida la compatibilidad con el contrato interno y la comprobación de huella de memoria.
```

---

## 7. `/znve-forensic` (Diagnóstico Estático de Solo Lectura)

**Cuándo usar:** Para investigar código desconocido, errores o cuellos de botella sin modificar nada.

```text
/znve-forensic --target=src/[modulo]/[archivo_o_directorio]
Diagnóstico de causa raíz sobre el comportamiento detectado en [DESCRIPCIÓN_DEL_PROBLEMA / ERROR].

DIRECTIVA DE NO-INTERVENCIÓN:
- MODO SOLO LECTURA (Zero-Touch): Prohibido crear, modificar o borrar cualquier archivo en el disco.

ENTREGA:
1. RESUMEN DE DOMINIO: función operativa real, en un párrafo.
2. MATRIZ DE ENTRADAS, SALIDAS Y ESTADO.
3. EFECTOS SECUNDARIOS: persistencia, red, I/O e IPC.
4. EQUILIBRIOS ACCIDENTALES: código contradictorio que funciona por orden de evaluación.
5. ZONAS ROJAS: condiciones de carrera, desconexiones, nulos o saturación.
```

---

## 8. `/znve-harness` (Arnés de Caracterización Golden Master)

**Cuándo usar:** Antes de tocar o refactorizar un archivo frágil o sin pruebas, para congelar su comportamiento en snapshots.

```text
/znve-harness --target=src/[ruta/componente_fragil].[ext]
Crearemos un arnés de caracterización Golden Master para aislar el comportamiento del componente [NOMBRE_DEL_COMPONENTE].

RESTRICCIÓN ABSOLUTA: Prohibido modificar el código de producción. Permanece intocable.

DISEÑA EL ARNÉS EN: `tests/characterization/test_[componente]_harness.[ext]`
1. Invoca el componente como caja negra.
2. Inyecta entradas representativas y casos límite ([DESCRIPCIÓN_DE_CASOS_LÍMITE]).
3. Captura las salidas actuales en snapshots o aserciones deterministas.
4. Entrega la suite de pruebas aislada y el comando exacto para ejecutarla.
```

---

## 9. `/znve-legacy-rescue` (Rescate Integral en 5 Fases)

**Cuándo usar:** Para modernizar un monolito o módulo legacy sin tests siguiendo [ZNVE_LEGACY_PROTOCOL.md](ZNVE_LEGACY_PROTOCOL.md).

```text
/znve-legacy-rescue
Inicia el rescate integral de [RUTA_DEL_MONOLITO].

FASES (no avances sin verificar la anterior):
1-2. Ingesta pasiva y reporte forense (/znve-forensic).
3.   Golden Master sobre el código intacto (/znve-harness), 100% en verde.
4.   Shadow Run del módulo nuevo: Salida(Nuevo) == Salida(Legacy).
5.   Conmutación gradual con Strangler Fig.

ENTREGA EN ESTA RESPUESTA: solo el Reporte Forense (fases 1 y 2) y el diseño del arnés (fase 3).
```

---

## 10. `/znve-audit` (Auditoría de Recursos, Rendimiento y Ruido)

**Cuándo usar:** Para auditar código en busca de bloqueos de interfaz, fugas de memoria, puertos expuestos o logs ruidosos.

```text
/znve-audit --target=src/[modulo]/
Auditoría de higiene técnica y optimización de recursos sobre el módulo [NOMBRE_DEL_MÓDULO].

DIRECTIVA: Diagnostica la causa raíz; nada de parches cosméticos ni retardos arbitrarios. No modifiques archivos: entrega la hoja de remediación para aprobación.

ENTREGA:
1. CONCURRENCIA E HILOS: bloqueos síncronos en el hilo principal (`.Result`, `.Wait()`, bloqueos sin `await`), procesos zombis.
2. SUPERFICIE DE RED Y SEGURIDAD: puertos expuestos, timeouts y manejo de desconexión.
3. CICLO DE VIDA Y RECURSOS: handles, conexiones, sockets o `WakeLock` sin desecho explícito (`IDisposable`, `finally`); listeners huérfanos.
4. HOJA DE REMEDIACIÓN: acciones atómicas priorizadas por causa raíz, cada una con TARGET_FILE y verificación. Incluye la purga de logs rutinarios (`console.log("ok")`, `print("DEBUG")`).
```

---

## 11. Rendimiento y caché

ZNVE aplica «cero ruido» también al contexto del agente (guardrail 8): cada token que entra cuesta, resta atención al contrato y se retiene en el proveedor. El agente no controla la caché del servidor; controla **qué entra en cada turno, cuánto escribe y si respeta la verificación**.

### 11.1 Orden estable → volátil

Ordena todo lo que le das a la IA de lo más fijo a lo más cambiante:

1. Directiva de ZNVE y perfil del asistente (fijos; es lo que se cachea).
2. Reglas del proyecto y contratos ya aprobados.
3. El contrato activo y el `TARGET_FILE`, **al final**: es donde la atención del modelo es más fuerte, sobre todo en modelos con ventana deslizante.

### 11.2 Prácticas de sesión

- Cada fase es una sesión: corta al cerrar una fase verificada (el perfil de tu asistente dice cómo).
- No cambies de modelo, skills, servidores MCP, herramientas ni esquemas de salida a mitad de fase. Las herramientas se **restringen**, no se quitan.
- No edites las directivas con la sesión abierta.
- No compactes ni pidas resúmenes a mitad de fase.
- Agrupa en un mismo turno las lecturas independientes y pide rangos de líneas, no archivos completos.
- Con razonamiento alto para diseñar (`contract`, `forensic`, `triage`, `audit`) y el modelo más rápido que cumpla el contrato para ejecutar (`execute`, `hotfix`, `harness`).

### 11.3 Protocolo de medición

Mide con los campos de uso que devuelve la API de cada proveedor, no con estimaciones:

| Proveedor | Campos |
|---|---|
| Gemini | `usage_metadata.cached_content_token_count` |
| Anthropic | `cache_read_input_tokens`, `cache_creation_input_tokens` |
| DeepSeek | `prompt_cache_hit_tokens`, `prompt_cache_miss_tokens` |
| OpenAI | `input_tokens_details.cached_tokens` |
| OpenRouter | `usage.prompt_tokens_details.cached_tokens` (el cliente de `integrations/openrouter/` los escribe en `stderr` con `ZNVE_OPENROUTER_USAGE=1`) |
| Ollama | `prompt_eval_count` (baja cuando reutiliza el prefijo) |

Indicadores: tokens sin caché por turno, porcentaje de aciertos de caché, y tokens de entrada y de salida por ciclo de verificación. Compara siempre la misma tarea con y sin la directiva, varias veces, y conserva las sondas de seguridad (instrucción inyectada en el código, secreto canario y test existente incorrecto).

Mantén estable `integrations/openrouter/response-schema.json`: cambiar el esquema de salida invalida la caché del prefijo.

### 11.4 Cifras de referencia (octubre de 2026)

Las cifras caducan; verifícalas en la documentación del proveedor antes de decidir con ellas. Por eso viven aquí y no en las directivas.

- Los tokens servidos desde la caché cuestan una fracción de los nuevos: del orden de 10 a 20 veces menos en OpenAI, Gemini y Anthropic, de 30 a 50 veces menos en DeepSeek V4 y hasta unas 120 veces menos en MiMo V2.6 Pro (cifra del fabricante, sin verificación independiente).
- Latencia: recortar a la mitad la **salida** la reduce cerca de un 50 %; recortar a la mitad la **entrada** solo la reduce entre un 1 y un 5 % en la nube. En local (Ollama) sí pesa la entrada, porque el procesado del prompt corre a cientos de tokens por segundo. Por eso la salida mínima (diffs en lugar de archivos completos) importa más que la entrada mínima para la velocidad.
- La caché del proveedor retiene lo que entra (hasta 24 horas en algunos casos) y puede inferirse por tiempo de respuesta: otro motivo para que los secretos no entren al contexto.
- Ollama: el KV cache crece con `num_ctx`; con `qwen2.5-coder:14b` a 32k tokens ronda los 6 GB, y `OLLAMA_FLASH_ATTENTION=1` con `OLLAMA_KV_CACHE_TYPE=q8_0` lo reduce a la mitad.
