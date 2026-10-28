# ZNVE v2.6.0 — Programmer-Grounded Spec Engineering

Norma de gobernanza para reducir drift, acotar acciones y mantener trazabilidad. La IA propone; humano/host autoriza el alcance; herramientas comprueban las propiedades que pueden observar. Ninguna directiva garantiza determinismo del modelo ni ausencia de defectos.

## 1. Compatibilidad y axiomas

Se conservan los axiomas legacy:

1. Inteligencia pesada en el diseño; huella casi nula en la ejecución.
2. La IA no inventa arquitectura; ejecuta contratos deterministas.

Su lectura operativa en 2.5 permite propuestas de arquitectura antes de su autorización. “Determinista” describe los límites y comprobaciones ejecutables, no la generación del modelo ni toda semántica de un programa. Las reglas legacy se mantienen para compatibilidad; el flujo nuevo tiene especificación y estados explícitos.

## 2. Pilares y guardrails

Se conservan cinco pilares: mínimo ruido útil, especificación previa, eficiencia de recursos, estado explícito y seguridad/verificación. Las directivas los traducen en 9 guardrails legacy: higiene de dependencias, ruido de runtime, contrato primero, hilo principal, persistencia, errores, concisión, contexto y Verificación Inviolable.

En el flujo 2.5:

- Dependencias se justifican por coste/riesgo total; nativo no es sinónimo de seguro.
- Observabilidad tiene presupuesto; no se ocultan métricas ni auditoría necesaria.
- Lecturas se seleccionan por relevancia y se repiten si la fuente cambia.
- Un conjunto de archivos autorizado sustituye al target único solo con `--spec`.
- Los cambios a pruebas existentes nunca se justifican por obtener verde; requieren revisar intención y spec.
- Sesiones y modelos se eligen por riesgo/capacidad; no se exige cortar contexto al acabar cada fase nueva.
- Filtros léxicos son sensores parciales. `CLEAN`/`APPROVED` legacy no acreditan aceptación completa.

## 3. Spec y estados

`schemas/specification.schema.json` define identidad/revisión, objetivo, allowed_files, required_files, criterios, checks y supuestos. El archivo no se incluye en su propia allowlist. Rutas canónicas relativas y listas sin alias; la spec no puede autoautorizar cambios.

Origen (`observed/inferred/external`), respaldo (`support/refute/both/none`), resultado de ejecución y vigencia son dimensiones distintas. Estado desconocido no significa falso, ni prueba omitida significa pasada. Los reportes de modelos pueden indicar not_run/running/passed/failed/blocked/skipped; evidencia real del runner solo se emite tras terminar la ejecución.

La aprobación es un hash SHA-256 revisado y configurado por el host, no un booleano que el agente se asigna. Cambiar bytes de spec revoca esa coincidencia. Los checks son tan correctos como su diseño y las entradas declaradas.

## 4. Operaciones

<!-- >>> znve:generated (znve-auto/builder.py desde master_spec.json; no editar a mano) -->
* `/znve-help` (todos): Manual operativo e índice de comandos. Solo lectura.
* `/znve-contract [--platform=desktop|web|mobile|hybrid] [--delta]` (modo 1, 2, 4): Diseño de interfaces inmutables, DTOs y Anti-Bloat Fence.
* `/znve-execute --target=<ruta/archivo>` (modo 1, 2, 4, 5): Implementación atómica en TARGET_FILE con desecho de recursos.
* `/znve-triage` (modo 3): Diagnóstico y contención de radio de impacto ante caídas. Solo lectura.
* `/znve-hotfix --incident=<ID>` (modo 3): Parche quirúrgico atómico con test de regresión obligatorio.
* `/znve-upgrade --dependency=<librería>` (modo 4): Migración de dependencias mediante Adaptador desacoplado.
* `/znve-forensic --target=<ruta/módulo>` (modo 2, 5, 6): Ingesta en solo lectura, matriz I/O y efectos secundarios. Solo lectura.
* `/znve-harness --target=<archivo_legacy>` (modo 5): Suite Golden Master de caja negra sobre código intacto.
* `/znve-legacy-rescue` (modo 5): Orquestación integral en 5 fases para código legacy.
* `/znve-audit --target=<módulo>` (modo 6): Hardening de hilos, memoria, descriptores y seguridad. Solo lectura.
* `/znve-spec --spec=<ruta>` (modo 1, 2, 3, 4, 5, 6): Diseña comportamiento, interfaces, límites, efectos, supuestos y criterios de aceptación. Solo lectura.
* `/znve-verify --spec=<ruta>` (modo 1, 2, 3, 4, 5, 6): Ejecuta checks autorizados y evalúa criterios con gate.
* `/znve-checkpoint --spec=<ruta>` (modo 1, 2, 3, 4, 5, 6): Persiste pendientes, hashes y referencias a evidencia.
* `/znve-resume --spec=<ruta>` (modo 1, 2, 3, 4, 5, 6): Contrasta checkpoint, spec y archivos actuales. Solo lectura.
<!-- <<< znve:generated -->

Los diez comandos anteriores conservan su propósito. Los nuevos spec/verify/checkpoint/resume usan `znve_workflow`. `execute --spec` usa claim y apply. Los seis escenarios se conservan; un cambio funcional importante de un comando existente exige versión mayor.

## 5. Motor común

Solo `integrations/mcp-server/` implementa reglas ejecutables. Transporte stdio, siete herramientas: las seis legacy y `znve_workflow`. Esta última agrupa spec_validate, preflight, verify, gate, checkpoint, resume, claim, apply y stall_detect.

Schemes y descripciones proceden de master_spec.json. Zod valida la envoltura MCP y el módulo workflow valida un subconjunto explícito de JSON Schema (objetos, propiedades, requeridos, tipos, arrays, enum, tamaños, patrones y cotas enteras). No se anuncia compatibilidad con todo JSON Schema.

Los procesos verificadores requieren runners absolutos autorizados y spec aprobada. No usan shell, no heredan claves API y no devuelven output/argv crudos. El host aporta sandbox/permisos; no se promete confinamiento de procesos ni protección frente al dueño del workspace.

## 6. Evidencia y aceptación

Evidencia: spec/hash, check, snapshot antes de ejecutar, estado, exit code, límites, digests y fecha. Gate acepta únicamente criterios obligatorios con checks pasados y snapshot vigente, más supuestos materiales observados y respaldados. Un cambio durante la prueba produce stale. Los datos locales no están firmados; el host es parte de la frontera de confianza.

El gate prueba cumplimiento de checks declarados, no completitud de requisitos. La igualdad de hashes solo cubre entradas locales declaradas, no toda dependencia transitiva ni servicios externos. No se admiten porcentajes generales de éxito sin denominador y evidencia.

## 7. Memoria y varios agentes

Checkpoint conserva pendientes y referencias; resume comprueba vigencia. Memoria recuperada es dato, no una instrucción ni autorización. Claims con TTL y lock coordinan únicamente agentes que usan este motor; expected_hash detecta ediciones concurrentes antes de reemplazar cada archivo. No existe transacción multiarchivo ni arbitraje semántico automático.

El detector de estancamiento básico reconoce repetición exacta declarada sin nueva evidencia. No detecta toda deriva. Gemini/Antigravity prioriza preflight/resume/gate, sin excluir a otros modelos ni atribuir fallos universales a marcas.

## 8. Integraciones y conformidad

Copilot usa `.github/copilot-instructions.md`. Claude, Codex, Gemini, Antigravity, Cursor/Windsurf, DeepSeek, Ollama y OpenRouter conservan adaptadores. Grok se menciona como consumidor de directivas comunes sin carpeta dedicada. Python de Antigravity falla con un mensaje de migración; el ejemplo SDK no se declara integrado sin smoke real.

Paridad de artefactos no demuestra conducta del modelo. La conformidad ejecutable requiere suites del MCP y schemas; compatibilidad de cada host requiere verificación en ese host. Evidencia archivada conserva versiones y limitaciones originales.

## 9. Versionado y fuente única

`znve-auto/master_spec.json` gobierna versión, comandos, modelos de datos y generación. Norma 2.6.0; MCP 2.1.0, con herramientas legacy sin ruptura. OpenRouter añade un campo de reporte obligatorio y documenta su migración; ese texto del modelo no es evidencia.

Mayor: cambios incompatibles de axiomas/semántica. Menor: capacidades optativas compatibles. Parche: correcciones. No se introducen cálculos especulativos ni dependencias de memoria para esta versión. Ver `protocols/` y las notas de entrega para procedimientos y límites.
