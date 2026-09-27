# GUÍA MAESTRA DE PROMPTS ZNVE (ZERO-NOISE VIBE ENGINEERING)
**Catálogo de Prompts Genéricos para Agentes de IA (Cursor, Windsurf, Claude, Copilot, Roo Code, Antigravity)**
*Versión: 2.3.0 | Estándar: Spec-Driven Agentic Architecture*

---

## 🎯 PROPÓSITO
Esta guía contiene las plantillas de prompts optimizadas para ejecutar los comandos del estándar **ZNVE**. Cada prompt establece de manera estricta el **perímetro de acción**, las **restricciones absolutas**, el **objetivo atómico (`TARGET_FILE`)** y los **criterios de parada** para eliminar el "bucle de muerte de la IA" (*AI agentic drift*), evitar la inyección de código parásito y asegurar entregas deterministas.

---

## 📋 ÍNDICE DE COMANDOS

1. [`/znve-contract`](#1-znve-contract-inicio-greenfield--recomendación-de-stack) — Inicio de proyecto Greenfield y recomendación de stack por plataforma.
2. [`/znve-contract --delta`](#2-znve-contract---delta-análisis-incremental-en-proyectos-iniciados) — Auditoría e incremento de contratos en proyectos en desarrollo.
3. [`/znve-execute`](#3-znve-execute-ejecución-quirúrgica-de-código) — Implementación de código de negocio bajo contrato aprobado.
4. [`/znve-forensic`](#4-znve-forensic-diagnóstico-estático-de-solo-lectura) — Análisis de causa raíz en modo *Zero-Touch*.
5. [`/znve-harness`](#5-znve-harness-arnés-de-caracterización-golden-master) — Aislamiento de código legacy o frágil en suites de caracterización.
6. [`/znve-hotfix`](#6-znve-hotfix--znve-triage-crisis-en-producción--aislamiento) — Triaje y contención de incidentes críticos en producción.
7. [`/znve-upgrade`](#7-znve-upgrade-actualización-de-dependencias-con-breaking-changes) — Migración de SDKs mediante la Capa Anti-Corrupción (*Adapter Pattern*).
8. [`/znve-audit`](#8-znve-audit-auditoría-de-recursos-rendimiento-y-ruido) — Limpieza de hilos bloqueantes, fugas de memoria y logs de depuración.

---

## 1. `/znve-contract` (Inicio Greenfield & Recomendación de Stack)

**Cuándo usar:** Al iniciar un módulo o proyecto nuevo desde cero.

```text
Bajo /znve-contract, iniciaremos el diseño del módulo [NOMBRE_DEL_MÓDULO] para una aplicación tipo [ESCRITORIO / WEB / ANDROID / HÍBRIDA / MACOS].

RESTRICCIONES ABSOLUTAS:
1. Poda de Contexto: Prohibido escribir código de implementación en src/.
2. Anti-Bloat Fence: Prohibido agregar librerías externas que no pertenezcan al SDK nativo o runtime base salvo justificación de peso cero.

REQUERIMIENTO DE EJECUCIÓN:
1. Recomienda el stack técnico optimizado (Tooling, Persistencia/BD y UI si aplica) para la plataforma [TIPO_DE_APP].
2. Diseña los DTOs e Interfaces inmutables en `contracts/[modulo].contract.[ts/py]`.
3. Aplica la Lista de Chequeo de Solidez:
   [ ] Estructura invariable (Entradas, salidas, entidades y Enums tipados).
   [ ] Defensas de frontera (Tipos de error explicitados, sin 'any').
   [ ] Cero dependencias parásitas (Solo primitivos y SDKs autorizados).
   [ ] Filtro de diferimiento (Ideas secundarias a contracts/CONTRACT_BACKLOG.md).
4. Si la lista se cumple al 100%, emite el Criterio de Parada Obligatorio: "Contrato v1 sólido y cerrado. Listo para /znve-execute." y DETÉN la generación.
```

---

## 2. `/znve-contract --delta` (Análisis Incremental en Proyectos Iniciados)

**Cuándo usar:** Para agregar nuevas capacidades a un módulo existente o reorientar el desarrollo por etapas.

```text
Bajo /znve-contract --delta, realizaremos una auditoría de discrepancias para incorporar la nueva capacidad [DESCRIPCIÓN_DE_LA_FUNCIONALIDAD] en el módulo [NOMBRE_DEL_MÓDULO].

TARGET CONTRATO: `contracts/[modulo].contract.[ts/py]`
TARGET CÓDIGO ACTUAL: `src/[ruta/modulo_existente]`

REQUERIMIENTO DE EJECUCIÓN:
1. Compara el contrato en contracts/ con la implementación real e identifica tipos o campos faltantes.
2. Clasifica los cambios en dos cubos:
   - CUBO A (Requerido Ya): Tipos mínimos indispensables para la etapa actual.
   - CUBO B (Diferido): Sugerencias secundarias. Escríbelas en `contracts/CONTRACT_BACKLOG.md`.
3. Muestra el diff del contrato actualizado para el CUBO A y solicita mi aprobación antes de cualquier escritura de código.
```

---

## 3. `/znve-execute` (Ejecución Quirúrgica de Código)

**Cuándo usar:** Para escribir la lógica interna de un archivo específico una vez que el contrato en `contracts/` está congelado y aprobado.

```text
Contrato aprobado. Activamos /znve-execute para implementar la lógica de negocio.

TARGET_FILE EXCLUSIVO: `src/[modulo]/[servicio_especifico].[ext]`

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

## 4. `/znve-forensic` (Diagnóstico Estático de Solo Lectura)

**Cuándo usar:** Para investigar errores, comportamientos anómalos o cuellos de botella sin modificar el código.

```text
Bajo /znve-forensic, realizaremos un diagnóstico de causa raíz sobre el comportamiento anómalo detectado en [DESCRIPCIÓN_DEL_PROBLEMA / ERROR].

TARGET DE INSPECCIÓN: `src/[modulo]/[archivo_o_directorio]`

DIRECTIVA DE NO-INTERVENCIÓN:
- MODO SOLO LECTURA (Zero-Touch): Prohibido crear, modificar o borrar cualquier archivo en el disco.

ANALIZA Y REPORTA:
1. Grafo de llamadas y efectos secundarios (I/O, Red, Estado).
2. Puntos exactos de fallo (Líneas de código, violaciones de hilos, recursos sin liberar).
3. Matriz de Causa Raíz e impacto sin proponer parches masivos.
4. Entrega el informe forense estructurado.
```

---

## 5. `/znve-harness` (Arnés de Caracterización Golden Master)

**Cuándo usar:** Antes de tocar o refactorizar un archivo frágil o sin pruebas, para congelar su comportamiento en snapshots.

```text
Bajo /znve-harness, crearemos un arnés de caracterización Golden Master para aislar el comportamiento del componente [NOMBRE_DEL_COMPONENTE].

TARGET PRODUCCIÓN: `src/[ruta/componente_fragil].[ext]`
RESTRICCIÓN ABSOLUTA: Prohibido modificar el código de producción. Permanece intocable.

DISEÑA EL ARNÉS EN: `tests/characterization/test_[componente]_harness.[ext]`
1. Invoca el componente como caja negra.
2. Inyecta entradas representativas y casos límite ([DESCRIPCIÓN_DE_CASOS_LÍMITE]).
3. Captura las salidas actuales en snapshots o aserciones deterministas.
4. Entrega la suite de pruebas aislada y el comando exacto para ejecutarla.
```

---

## 6. `/znve-hotfix` / `/znve-triage` (Crisis en Producción & Aislamiento)

**Cuándo usar:** Para resolver fallos urgentes en producción conteniendo el radio de impacto dentro de la capa de adaptación.

```text
Bajo /znve-hotfix, atenderemos el incidente crítico [CÓDIGO_O_DESCRIPCIÓN_DEL_INCIDENTE] afectando el servicio [NOMBRE_DEL_SERVICIO].

PERÍMETRO DE CONTENCIÓN:
- TARGET_FILE: `src/adapters/[adaptador_afectado].[ext]`
- BLAST RADIUS: La corrección debe estar aislada dentro del adaptador. Prohibido reestructurar la base de datos o el núcleo de la aplicación.

REQUERIMIENTO:
1. Inyecta un identificador de trazabilidad (X-Run-ID / correlation_id) en el punto de fallo.
2. Aplica el parche mínimo defensivo con validación estricta de frontera.
3. Entrega el diff quirúrgico y el comando de verificación atómica para validar la contención.
```

---

## 7. `/znve-upgrade` (Actualización de Dependencias con Breaking Changes)

**Cuándo usar:** Para migrar o actualizar SDKs/librerías externas aislando las roturas mediante una Capa Anti-Corrupción.

```text
Bajo /znve-upgrade, migraremos la integración de [NOMBRE_LIBRERÍA_ANTIGUA] a [NOMBRE_LIBRERÍA_NUEVA] que introduce breaking changes.

ESTRATEGIA ANTI-CORRUPCIÓN:
1. Mantén inmutable el contrato interno en `contracts/[servicio].contract.[ext]`.
2. TARGET_FILE: Construye o actualiza el adaptador en `src/adapters/[servicio]_adapter.[ext]`.
3. Absorbe todos los breaking changes de la nueva librería dentro del adaptador. El resto de la aplicación no debe enterarse del cambio de SDK.
4. Muestra la prueba unitaria que valida la compatibilidad con el contrato interno.
```

---

## 8. `/znve-audit` (Auditoría de Recursos, Rendimiento y Ruido)

**Cuándo usar:** Para auditar y depurar código en busca de bloqueos de interfaz, fugas de memoria o basura acumulada.

```text
Bajo /znve-audit, realizaremos una limpieza de higiene técnica y optimización de recursos sobre el módulo [NOMBRE_DEL_MÓDULO].

TARGET: `src/[modulo]/`

ANALIZA Y CORRIGE (Solo bajo aprobación previa de la lista):
1. HILOS Y UI: Detecta y elimina bloqueos síncronos en el hilo principal (`.Result`, `.Wait()`, bloqueos sin `await`).
2. RECURSOS: Identifica handles, conexiones, sockets o `WakeLock` sin desecho explícito (`IDisposable`, `finally`).
3. PURGA DE RUIDO: Elimina logs rutinarios (`console.log("ok")`, `print("DEBUG")`) dejando únicamente eventos estructurados para excepciones.
4. Entrega la tabla de hallazgos y las correcciones quirúrgicas sugeridas.
```
