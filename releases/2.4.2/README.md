# ZNVE v2.4.2 — Notas de la versión

**Fecha:** 2026-10-23 · **Tipo:** parche (SemVer §10: sin comandos, axiomas ni pilares nuevos) · **Anterior:** [2.4.1](../../CHANGELOG.md)

Corrige dos grupos de detectores que no cumplían lo que la especificación promete y añade la suite de seguridad del servidor MCP que faltaba. El detalle completo está en el [CHANGELOG](../../CHANGELOG.md).

## Qué cambia

| Área | Antes (2.4.1) | Ahora (2.4.2) |
|---|---|---|
| `znve_validate_contract` (Pilar 4) | Solo rechazaba `SELECT *` literal. Aceptaba `SELECT DISTINCT *`, `ALL *`, `TOP n *`, `alias.*`, `*` tras otras columnas y `SELECT /* x */ *`; `.FIND({})` no se detectaba aunque el manual prometía "sin distinguir mayúsculas" | Rechaza todas esas formas. Sigue aprobando `COUNT(*)`, `a*b` y `find({}, { campo: 1 })` |
| `znve_audit_resources` | `Thread.Sleep` (C#) y `time.sleep` (Python) daban `CLEAN`; `for (;;) {}` tampoco se marcaba | Los marca `MEDIUM`. `Task.Delay` sigue `CLEAN` porque no bloquea |
| `znve_forensic_scan` | Contaba `time.sleep` pero no `Thread.Sleep`, distinto de la auditoría | Misma definición que la auditoría, sin distinguir mayúsculas |
| Tests del servidor MCP | 132 | 211 (se añade `security-gaps.test.mjs`, incluido en `npm test`) |
| Casos de conformidad compartidos | 50 | 63 (los ejecutan el servidor y `znve_skill.py`) |

La misma lógica vive en dos implementaciones (servidor TypeScript y skill de Python); ambas se corrigieron con los mismos patrones y los mismos casos.

## Evidencia de verificación

Ejecutada sobre el árbol final de esta versión:

| Comprobación | Comando | Resultado |
|---|---|---|
| Artefactos sincronizados con la spec | `python znve-auto/builder.py --verify` | 32 sincronizados (v2.4.2) |
| Paridad y comportamiento | `python znve-auto/test_sync.py` | 91 pruebas, OK (1 omitida) |
| Servidor MCP | `npm test` en `integrations/mcp-server` | 211 pruebas: 209 pasan, 0 fallan, 2 omitidas |
| Tipado del cliente OpenRouter | `npm run check:openrouter` | sin errores |

Las 2 pruebas omitidas del servidor dependen de la plataforma: una exige poder crear enlaces simbólicos de archivo y otra solo se ejecuta fuera de Windows.

### De dónde salen los cambios

Un análisis con mutation testing (Stryker) sobre `znve-mcp-server.ts` midió que la suite anterior detectaba el 64,8 % de las mutaciones (83,2 % si se excluyen mensajes de texto y expresiones regulares) y dejaba sin cubrir condiciones de seguridad concretas. Los tests nuevos suben la puntuación en su alcance (233 mutaciones comparables) del 70,4 % al 78,1 %. Las 51 mutaciones restantes parecen equivalentes, inalcanzables o dependientes de plataforma, pero no se demostró su equivalencia una a una. Las sondas que confirmaron los falsos negativos de los detectores se hicieron sobre la skill de Python, con la misma lógica que el servidor.

## Notas de migración

- **Sin cambios de interfaz:** ningún comando, parámetro ni código de error cambia. No hay nada que migrar.
- **Comportamiento más estricto:** un contrato que antes se aprobaba con `SELECT DISTINCT *`, `SELECT t.*` o `.FIND({})` ahora se rechaza con `CONTRACT_VIOLATION`; un fragmento con `Thread.Sleep` o `time.sleep` pasa de `CLEAN` a `MEDIUM`. Es la corrección de un falso negativo, pero puede aparecer en flujos que ya los usaban.
- **Regenerar las integraciones instaladas:** el servidor MCP, `znve_skill.py` y las directivas regeneradas llevan la versión 2.4.2. Quien tenga el instalador global de Antigravity debe volver a ejecutarlo para recibir la skill nueva.

## Límites conocidos

- La medición con Stryker cubre solo `znve-mcp-server.ts` (dos tercios del archivo, una ejecución). La skill de Python no se ha medido con mutation testing.
- La condición del nombre de archivo del harness solo se verifica por completo en POSIX; en Windows una de sus ramas es redundante.
- Las nuevas expresiones de `SELECT *` se probaron con 11 casos negativos, no con código real: pueden quedar formas sin cubrir (por ejemplo dentro de CTEs o con identificadores entrecomillados) y no se descartan falsos positivos en SQL poco habitual.
- La mejora de eficiencia en tokens por turno sigue sin demostrarse (ver la evidencia de la 2.4.0).

## Archivos de esta versión

| Tipo | Archivos |
|---|---|
| Fuente única | `znve-auto/master_spec.json`, `znve-auto/tool_contract_cases.json` |
| Implementaciones | `integrations/mcp-server/znve-mcp-server.ts`, `integrations/antigravity/znve_skill.py` (y su copia derivada) |
| Tests | `integrations/mcp-server/test/security-gaps.test.mjs` (nuevo), `integrations/mcp-server/package.json` |
| Regenerados por `builder.py` | Directivas y skills de todos los asistentes, `protocols/COMMANDS.md`, `integrations/claude/skills/znve.zip` |
| A mano | `README.md`, `SPECIFICATION.md`, `GLOSSARY.md`, `index.html`, `protocols/*`, `integrations/deepseek/harness/README.md`, `znve-auto/README.md`, `CHANGELOG.md` |
