# Zero-Noise Vibe Engineering — ZNVE v2.6.0

**Programmer-Grounded Spec Engineering.** Gobernanza para reducir deriva agéntica mediante especificaciones, alcance explícito y evidencia vigente proporcional al riesgo. Compatible con las specs de 2.5.0 y los comandos de 2.4.2; sin prometer determinismo del modelo ni eliminar todo el drift.

## Qué añade 2.6

La spec puede registrar el razonamiento de un programador y enlazarlo a evidencia. Todos los campos son opcionales: una spec 2.5.0 sigue siendo válida.

- Intención humana, resultados observables (enlazados a criterios obligatorios), invariantes (enlazados a checks), transiciones de estado, efectos permitidos y reversibilidad.
- Decisiones con alternativa elegida, alternativas descartadas, razón, condición de reapertura y lente técnica opcional (fundamentos, lenguaje, sistemas, datos, seguridad, producto, plataforma, escala, restricción).
- `risk_budget` (impacto, incertidumbre, evidencia mínima) y `evidence_kind` por check: `local`, `component_real` o `production_like`.
- Con impacto alto, la spec se rechaza si falta intención, resultado observable, invariante o decisión, o si la evidencia de un invariante es inferior a la mínima. Con incertidumbre alta exige un supuesto material.
- `gate` no acepta mientras un invariante no tenga evidencia vigente y devuelve `unresolved_invariants`.
- Proporcionalidad: los campos se añaden solo si reducen una ambigüedad o un riesgo material; un cambio local P0 no requiere DTO, tests ni texto ceremonial.

`evidence_kind` es una declaración revisada por quien aprueba el hash de la spec: el motor comprueba la coherencia de lo declarado, no que el entorno sea realmente production-like. No detecta drift de intención que no esté enlazado a un criterio.

### Base 2.5

- `spec`, `verify`, `checkpoint` y `resume`, además de los diez comandos anteriores.
- Estados separados de origen, respaldo, ejecución y vigencia.
- Specs aprobadas por hash del host, checks reales y gate calculado por código.
- Claims entre agentes cooperativos y escritura optimista dentro de una allowlist.
- Un único MCP TypeScript con siete herramientas; Python de Antigravity se retira explícitamente.
- Copilot conserva `.github/copilot-instructions.md`. Grok sigue documentado, sin carpeta dedicada.

No se incorporan derivadas, integrales, base vectorial ni un servicio adicional de memoria. No hay cifras de mejora conductual hasta repetir evaluaciones adecuadas.

## Inicio

Lee [la especificación](SPECIFICATION.md) y [el flujo spec-driven](protocols/SPEC_DRIVEN.md). Instala solo cuando decidas adoptar esta versión:

```text
cd integrations/mcp-server
npm ci
npm test
```

Desde esa carpeta registra el mismo MCP en el host elegido:

```text
node install-codex.mjs --workspace "<proyecto>"
node install-antigravity.mjs --workspace "<proyecto>"
```

Son alternativas de registro; no motores diferentes. Otros clientes usan el mismo `dist/znve-mcp-server.js` con `ZNVE_WORKSPACE`. Las skills y las instrucciones de instalación están en [integrations/README.md](integrations/README.md).

Los instaladores conservan su comportamiento de configuración; esta entrega local no los ejecuta contra tu configuración global. La autorización de nuevas operaciones se explica en [VERIFICATION.md](protocols/VERIFICATION.md). El runner no es sandbox y no debe ejecutar cargas hostiles.

## Comandos

En hosts que reservan `/`, usa `znve spec`, `$znve spec` o la forma que admita su selector de skills. Son protocolos del agente, no promesas de comandos nativos de todas las aplicaciones.

<!-- >>> znve:generated (znve-auto/builder.py desde master_spec.json; no editar a mano) -->
| Command / Comando | Mode / Modo | Purpose | Propósito |
| :--- | :--- | :--- | :--- |
| `/znve-help` | — | Operating manual and command index. | Manual operativo e índice de comandos. |
| `/znve-contract [--platform=desktop|web|mobile|hybrid] [--delta]` | 1, 2, 4 | Immutable interfaces, DTOs and Anti-Bloat Fence. | Diseño de interfaces inmutables, DTOs y Anti-Bloat Fence. |
| `/znve-execute --target=<ruta/archivo>` | 1, 2, 4, 5 | Atomic implementation in TARGET_FILE with resource disposal. | Implementación atómica en TARGET_FILE con desecho de recursos. |
| `/znve-triage` | 3 | Root-cause diagnosis and blast-radius containment. | Diagnóstico y contención de radio de impacto ante caídas. |
| `/znve-hotfix --incident=<ID>` | 3 | Atomic patch with mandatory regression test. | Parche quirúrgico atómico con test de regresión obligatorio. |
| `/znve-upgrade --dependency=<librería>` | 4 | Dependency migration behind a decoupled Adapter. | Migración de dependencias mediante Adaptador desacoplado. |
| `/znve-forensic --target=<ruta/módulo>` | 2, 5, 6 | Read-only ingestion, I/O matrix and side effects. | Ingesta en solo lectura, matriz I/O y efectos secundarios. |
| `/znve-harness --target=<archivo_legacy>` | 5 | Black-box Golden Master suite on intact code. | Suite Golden Master de caja negra sobre código intacto. |
| `/znve-legacy-rescue` | 5 | End-to-end 5-phase legacy orchestration. | Orquestación integral en 5 fases para código legacy. |
| `/znve-audit --target=<módulo>` | 6 | Hardening of threads, memory, descriptors and security. | Hardening de hilos, memoria, descriptores y seguridad. |
| `/znve-spec --spec=<ruta>` | 1, 2, 3, 4, 5, 6 | Design a verifiable specification. | Diseña comportamiento, interfaces, límites, efectos, supuestos y criterios de aceptación. |
| `/znve-verify --spec=<ruta>` | 1, 2, 3, 4, 5, 6 | Run authorized checks and evaluate the gate. | Ejecuta checks autorizados y evalúa criterios con gate. |
| `/znve-checkpoint --spec=<ruta>` | 1, 2, 3, 4, 5, 6 | Persist task state and evidence references. | Persiste pendientes, hashes y referencias a evidencia. |
| `/znve-resume --spec=<ruta>` | 1, 2, 3, 4, 5, 6 | Resume against current spec and file hashes. | Contrasta checkpoint, spec y archivos actuales. |
<!-- <<< znve:generated -->

## Documentación

- [Spec-driven](protocols/SPEC_DRIVEN.md): estructura, aprobación y compatibilidad.
- [Verificación](protocols/VERIFICATION.md): runner, gate, errores y límites.
- [Memoria y handoff](protocols/MEMORY_AND_HANDOFF.md): checkpoints, vigencia y concurrencia.
- [Manual generado](protocols/COMMANDS.md): comandos, herramientas e integraciones.
- [Workflows](protocols/workflows/README.md): hotfix, upgrade, legacy y hardening.
- [Notas 2.5.0](releases/2.5.0/README.md): migración y alcance de entrega.

`field-tests/`, `rfcs/` y `releases/2.4.2/` conservan historia. Sus resultados, transcripciones y versiones no se actualizan para aparentar una nueva evaluación.

## Fuente única y validación

`znve-auto/master_spec.json` genera directivas, schemas y paquetes reproducibles. No edites artefactos generados a mano.

```text
python znve-auto/builder.py --verify
python znve-auto/test_sync.py
python znve-auto/test_workflow_sync.py
```

Después, desde `integrations/mcp-server/`, ejecuta `npm test` y `npm run check:openrouter`. El CI ejecuta las mismas comprobaciones. Detalles en [znve-auto/README.md](znve-auto/README.md).

## English overview

ZNVE 2.5 adds verifiable specifications, host-approved execution, current evidence, acceptance gates and resumable task state. All supported hosts consume one shared MCP implementation. Existing tools remain compatible; the retired Antigravity Python engine fails explicitly. Grok remains documented without a dedicated distribution. Runtime isolation depends on the host. Passing checks do not prove specification completeness or universal agent reliability.

ZNVE 2.6 lets a spec record a programmer's reasoning — human intent, observable outcomes, invariants, decisions with rejected alternatives and reopen conditions, state transitions, effects, reversibility and a risk budget — and links it to evidence. All new fields are optional, so 2.5 specs remain valid. High-impact specs must link every invariant to checks of sufficient declared evidence kind, and the gate stays closed while any invariant lacks current evidence. Evidence kinds are declarations reviewed by whoever approves the spec hash, not proof of the environment.

## Licencias

Consulta [LICENSE](LICENSE): documentación bajo CC BY 4.0; protocolos e integraciones con CC BY 4.0 y MIT; herramientas de generación y schemas bajo MIT. No se modifica el licenciamiento de datos externos archivados.
