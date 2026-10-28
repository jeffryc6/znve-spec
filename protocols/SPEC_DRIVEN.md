# ZNVE 2.5 — Spec-Driven Agent Engineering

La spec amplía los contratos de datos: objetivo, revisión, archivos permitidos, entradas requeridas, criterios, checks y supuestos materiales. Los axiomas existentes siguen vigentes como dirección de diseño, sin prometer determinismo del modelo.

## Flujo

1. Diseña `specs/<tarea>.json` según `schemas/specification.schema.json`.
2. `znve_workflow` con `operation=spec_validate` devuelve el SHA-256 de los bytes de la spec, no aprobación semántica.
3. El operador revisa la spec y autoriza su hash al arrancar el MCP (`ZNVE_APPROVED_SPECS`, lista separada por comas). Modificar la spec requiere otro hash aprobado.
4. `preflight` comprueba entradas y runners. `claim` reserva archivos. `apply` exige claim vigente y hash base (`missing` para archivo nuevo).
5. `verify` ejecuta checks autorizados. `gate` verifica evidencia y supuestos; un criterio obligatorio sin prueba vigente queda abierto.
6. `checkpoint` / `resume` conservan continuidad sin copiar la conversación.

`allowed_files` y `required_files` son listas disjuntas de rutas canónicas con `/`; la spec vive fuera de ambas. Declara todas las entradas que condicionan los checks: manifests, scripts y configuración. La vigencia cubre solo archivos declarados; cambios externos o transitivos exigen revisión aunque esos hashes coincidan.

## Ejemplo

```json
{
  "id":"feature-1", "revision":1,
  "objective":"El módulo satisface la prueba de regresión existente",
  "allowed_files":["src/value.js"],
  "required_files":["tests/value.test.mjs","package.json"],
  "criteria":[{"id":"value","description":"Regresión verificada","required":true,"check_id":"unit"}],
  "checks":[{"id":"unit","runner":"node","argv":["--test","tests/value.test.mjs"],"timeout_ms":10000}],
  "assumptions":[]
}
```

MCP: `znve_workflow({operation:"spec_validate",payload:{spec_path:"specs/feature.json"}})`.

La allowlist puede contener código, tests nuevos y configuración. No autoriza cambiar tests existentes para obtener verde: revisa antes su intención y la spec. Cada escritura es atómica por archivo; no hay transacción de varios archivos.

## Lógica y compatibilidad

Origen: `observed/inferred/external`. Respaldo: `support/refute/both/none`. El gate requiere que cada supuesto material sea observado y respaldado; estas anotaciones son declaraciones revisadas por el humano, no pruebas semánticas automáticas.

Las seis herramientas y diez comandos legacy conservan su contrato. `contract` sigue diseñando datos; `spec` es el flujo nuevo y `execute --spec` usa su allowlist. Cuatro bloques y corte de sesión por fase pertenecen al modo legacy. Los nuevos comandos presentan artefacto, estado y pendientes. No se añaden derivadas, integrales, base vectorial ni servicio de memoria.
