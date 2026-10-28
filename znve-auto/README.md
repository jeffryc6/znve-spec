# Generador ZNVE 2.5

`master_spec.json` es fuente única de versión, axiomas, nueve guardrails legacy, catorce comandos, perfiles, siete herramientas y cuatro schemas. `builder.py` usa solo Python estándar. Targets y regions declaran artefactos; mirrors reproducen una skill, sin duplicar motor; bundles crean ZIP reproducibles y rechazan archivos huérfanos.

```text
python znve-auto/builder.py
python znve-auto/builder.py --verify
python znve-auto/test_sync.py
python znve-auto/test_workflow_sync.py
```

La última suite comprueba schemas generados, retiro explícito de Python, ausencia de carpeta Grok, ubicación de Copilot y compatibilidad de los 63 casos legacy. Los tests de la implementación Python retirada se sustituyen por pruebas de migración; las regresiones del servidor MCP se conservan.

Desde `integrations/mcp-server/`, `npm test` compila y ejecuta tests reales del MCP y workflow (runner local, vigencia, gate, claims, conflictos y seguridad). `npm run check:openrouter` verifica tipos del cliente; no llama al proveedor ni acredita integración externa.

La paridad de directivas no certifica obediencia del modelo. Los experimentos de `field-tests/` conservan sus datos históricos; los que importaban el motor Python necesitan adaptar su arnés antes de reevaluar 2.5. No se alteran transcripciones ni se recalculan resultados antiguos para aparentar mejoras.

## Cambios de mantenimiento

- Edita fuente y plantillas, luego genera; no edites skills ni schemas generados a mano.
- `workflow.schemas` contiene el subconjunto JSON Schema que valida el motor; no añadas keywords de validación sin implementarlas y probarlas.
- Los comandos legacy conservan cuatro bloques y reglas de fase. Las extensiones 2.5 se generan desde `workflow.rules_es` y documentan su alcance.
- Los stubs de Antigravity solo indican migración. No contienen reglas ni acceso a filesystem del proyecto.
- Nuevos esquemas de operaciones requieren actualizar el enum MCP, el dispatcher y pruebas de comportamiento.

Los presupuestos de artefactos limitan crecimiento, sin afirmar ahorro de tokens. Las verificaciones de versiones distinguen documentos actuales de notas históricas.
