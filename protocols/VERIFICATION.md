# Verificación ejecutable 2.5

Un único MCP sirve a todos los hosts. `znve_workflow` agrupa operaciones; sus payloads están en `$defs` de `schemas/workflow.schema.json`. Las herramientas legacy mantienen respuestas como `APPROVED` y `CLEAN`: sus filtros léxicos no encontraron patrones conocidos; no son aprobación humana ni ausencia de defectos.

## Autorización

Por defecto no hay specs ni runners autorizados. Configura el proceso MCP desde un ámbito controlado por el operador:

```json
{
  "ZNVE_WORKSPACE":"<ruta absoluta del proyecto>",
  "ZNVE_APPROVED_SPECS":"<sha256 revisado de la spec>",
  "ZNVE_RUNNERS":"{\"node\":\"<ruta absoluta a node>\"}"
}
```

Escapa barras invertidas dentro de JSON en Windows. Revisa el contenido y argumentos exactos de los checks antes de aprobar su hash. Obtén el hash con `spec_validate` o `Get-FileHash -Algorithm SHA256`. Reinicia el MCP al cambiar la configuración. El agente no debe poder reescribir esa configuración de confianza.

## Runner

`verify` usa spawn sin shell, cwd del proyecto, timeout de hasta 60 segundos y salida de hasta 64 KiB. Solo hereda PATH, variables de sistema/temporales, locale y TZ; no claves API. Registra estado, exit code, límites, tamaño/digest de salida y hashes. No imprime ni persiste stdout/stderr crudos. Para diagnóstico detallado, el operador ejecuta el comando aprobado y comparte un fragmento sin secretos.

El proceso usa permisos del usuario. **No es sandbox**: programa e hijos pueden acceder a red/disco o sobrevivir al padre. El host debe controlar efectos y aislar procesos de riesgo. No se garantiza terminar árboles de procesos; no ejecutes cargas no confiables.

## Gate y vigencia

`gate` carga IDs generados por el motor desde `.znve/state/`, contrasta check, hash de spec y snapshot actual. Evidencia fallida, ausente u obsoleta no cierra criterios obligatorios. Se capturan archivos antes/después: si cambian durante el check, la evidencia nace stale.

Exit code cero solo demuestra terminación correcta de ese comando; no demuestra existencia ni calidad de tests o completitud de la spec. Revisa los checks. Los registros locales no son firmas ni protección frente al dueño del host.

`status=SUCCESS` significa que la herramienta respondió; puede acompañar `accepted=false`, `ready=false` o un check `failed`. Los errores workflow incluyen BAD_ARGUMENT, BUSY, EXECUTION_DISABLED, SPEC_NOT_APPROVED, OUT_OF_SCOPE y CONFLICT; filesystem se informa como IO_ERROR.

## Límites

El MCP reutiliza protección de rutas y secretos. Las APIs públicas no acceden a `.znve`; el estado interno rechaza enlaces y usa lock entre procesos cooperativos. Un proceso hostil con los mismos permisos puede manipular estado o competir durante comprobaciones: usa sandbox/ACL del host. No se promete protección TOCTOU frente a ese adversario.

La invalidación se calcula al consultar evidencia; no necesita daemon. Solo cubre archivos declarados. Un hash no acredita la corrección semántica ni la independencia del evaluador.
