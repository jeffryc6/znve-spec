# ==============================================================================
# ZERO-NOISE VIBE ENGINEERING (ZNVE) — PROTOCOLO DE RESCATE LEGACY
# Archivo: protocols/ZNVE_LEGACY_PROTOCOL.md
# Versión: 2.0.0
# Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
# Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
# ==============================================================================

Este protocolo establece el estándar técnico obligatorio para auditar, caracterizar
y modernizar sistemas heredados (legacy), archivos "Dios" (God Objects), código 
espagueti o módulos monolíticos en producción sin pruebas automatizadas.

Aplica a cualquier entorno y lenguaje (Mobile, Desktop, Backend, Web, Scripts o CLI)
y cualquier motor de datos (SQL, NoSQL, Key-Value, archivos locales o memoria).

---

## 1. GUARDRAILS INVIOLABLES DE NO-INTERVENCIÓN

1. **Modo Solo Lectura Estricto:** Durante las Fases 1 a 4, queda terminantemente prohibido modificar, renombrar, mover o eliminar líneas del código original existente.
2. **Cero Dependencias Nuevas en el Código Base:** No se instalarán paquetes o bibliotecas en el runtime de producción para facilitar la inspección.
3. **Respeto a los "Equilibrios Accidentales":** Comportamientos aparentemente contradictorios, código redundante o errores silenciados no se consideran bugs por defecto; se asumen como comportamientos emergentes requeridos por la operación activa hasta demostrar lo contrario.
4. **Pruebas Siempre en Aislamiento:** Toda prueba unitaria, script de caracterización o mock se construye en un directorio aislado (`tests/characterization/` o `sandbox/`), nunca dentro de las fuentes originales.

---

## 2. EL PIPELINE DE RESCATE EN 5 FASES

[ FASE 1: Ingesta Pasiva ]       --> Lectura forense sin mutaciones (Zero-Touch)
↓
[ FASE 2: Reporte Forense ]      --> Mapeo de contratos implícitos y dependencias
↓
[ FASE 3: Golden Master ]        --> Arnés de caracterización sobre código intacto
↓
[ FASE 4: Shadow Run ]           --> Ejecución dual paralela y paridad bit a bit
↓
[ FASE 5: Strangler Fig ]        --> Conmutación gradual y desmantelamiento seguro


---

### FASE 1: INGESTA PASIVA & RADIOGRAFÍA (ZERO-TOUCH)
* **Objetivo:** Comprender la semántica operativa y el flujo de control sin alterar el entorno.
* **Entrada:** Ruta del archivo monolítico o módulo legacy.
* **Acciones del Agente:**
  1. Identificar todos los puntos de entrada (eventos de UI, endpoints, llamadas CLI, listeners de cola).
  2. Mapear estado global, lecturas de variables de entorno y recursos del sistema operativo (handles, sockets, hilos).
  3. Mapear I/O hacia bases de datos, APIs de terceros o almacenamiento local.
* **Criterio de Salida:** Mapeo completo de dependencias documentado. Prohibido sugerir código nuevo.

---

### FASE 2: REPORTE FORENSE & CONTRATOS IMPLÍCITOS
* **Objetivo:** Traducir el código legacy no documentado a especificaciones y contratos tipados.
* **Acciones del Agente:**
  1. Extraer los contratos implícitos: tipos de datos reales esperados en entradas y salidas.
  2. Documentar la matriz de efectos secundarios (*side effects*).
  3. Identificar zonas rojas: fragmentos con riesgo de condiciones de carrera, bloqueos de UI, fugas de memoria o punteros nulos.
* **Entregable Obligatorio:** `ARTEFACTO A: Reporte Forense` (ver plantilla en Sección 3).

---

### FASE 3: ARNÉS DE CARACTERIZACIÓN (GOLDEN MASTER TESTING)
* **Objetivo:** Congelar el comportamiento observable actual del software mediante pruebas de caja negra, garantizando una línea base reproducible contra regresiones.
* **Acciones del Agente:**
  1. Diseñar una suite de pruebas en `tests/characterization/` que invoque el código legacy intacto (mediante importación pasiva, invocación CLI o subproceso).
  2. Generar una matriz de inyección: entradas válidas, casos límite, valores nulos/vacíos y payloads malformados.
  3. Capturar y almacenar en snapshots (*Golden Master*) las respuestas exactas actuales (incluyendo códigos de error preexistentes o formatos particulares que producción ya tolera).
* **Criterio de Salida:** La suite de caracterización debe ejecutarse de forma determinista y registrar 100% de éxito contra el código original no modificado.

---

### FASE 4: EJECUCIÓN EN SOMBRA (SHADOW RUN & PARIDAD)
* **Objetivo:** Diseñar el reemplazo modular bajo el estándar ZNVE y validar paridad funcional en un entorno aislado.
* **Acciones del Agente:**
  1. Escribir el nuevo módulo en una ruta desacoplada (`src/modules/v2/` o similar) cumpliendo con:
     - Cero dependencias externas parásitas (solo APIs nativas o utilidades existentes).
     - Tipado estricto e inmutable basado en el contrato aprobado.
     - Cero bloqueos en el hilo principal y desecho explícito de recursos (`dispose`, `close`, `finally`).
  2. Implementar una prueba comparativa dual (*Dual Execution Harness*): alimentar con idénticos inputs al módulo Legacy y al módulo Nuevo.
  3. Comparar salidas y mutaciones de estado:
     $$\text{Salida}(\text{Nuevo}) == \text{Salida}(\text{Legacy})$$
     Cualquier discrepancia debe justificarse como corrección deliberada aprobada por el Director de Arquitectura o resolverse hasta alcanzar paridad total.

---

### FASE 5: CONMUTACIÓN GRADUAL (STRANGLER FIG)
* **Objetivo:** Reemplazar el monolito en producción de forma atómica y sin riesgo de inactividad operativa.
* **Estrategia de Despliegue:**
  1. **Enrutamiento en Frontera:** Desviar una fracción controlada del tráfico (1% -> 10% -> 100%) hacia el nuevo módulo mediante feature flags o proxys locales.
  2. **Monitoreo de Telemetría Silenciosa:** Alertar únicamente si se detectan anomalías de severidad media/alta o excepciones no controladas.
  3. **Desmantelamiento Quirúrgico:** Una vez que el nuevo módulo opera al 100% sin incidencias, eliminar el código legacy en un commit dedicado exclusivamente a limpieza.

---

## 3. PLANTILLAS DE SALIDA ESTANDARIZADAS

Todo agente de IA debe estructurar sus respuestas utilizando exclusivamente las siguientes plantillas según la fase activa:

### ARTEFACTO A: REPORTE FORENSE (Fases 1 y 2)

```markdown
### 1. RESUMEN DE DOMINIO Y PROPÓSITO
[Descripción concisa del objetivo de negocio que resuelve el archivo.]

### 2. MATRIZ DE ENTRADAS, SALIDAS Y ESTADO
- **Puntos de Entrada:** [Parámetros, llamadas de red, eventos UI, CLI]
- **Estado Mutado:** [Variables globales, registros en memoria, singletons]
- **Salidas Emitidas:** [Retornos, códigos de salida, eventos despachados]

### 3. CATÁLOGO DE EFECTOS SECUNDARIOS (SIDE EFFECTS)
- **Persistencia:** [Queries directas, mutaciones en BD/archivos]
- **Red / IPC:** [Llamadas HTTP, sockets, mensajería entre procesos]
- **Recursos OS:** [Timers activos, hilos secundarios, descriptores de archivo]

### 4. EQUILIBRIOS ACCIDENTALES Y COMPORTAMIENTOS EMERGENTES
- [Detalle de funciones redundantes o código contradictorio que coexiste por orden de evaluación]

### 5. ZONAS ROJAS DE RIESGO
- [Puntos vulnerables a timeouts, nulos, concurrencia o saturación de memoria]
ARTEFACTO B: COMPARATIVA DE PARIDAD SHADOW (Fase 4)
Markdown
### 1. EVALUACIÓN DE PARIDAD FUNCIONAL
| Caso de Prueba | Entrada | Salida Legacy | Salida Nuevo (ZNVE) | Estado |
|---|---|---|---|---|
| Happy Path | `{id: 10}` | `{status: "OK", v: 1}` | `{status: "OK", v: 1}` | ✅ IDÉNTICO |
| Edge Case Null | `{id: null}` | `{status: "ERR_01"}` | `{status: "ERR_01"}` | ✅ IDÉNTICO |
| Divergencia | `{id: -1}` | `null` | `{status: "INVALID"}` | ⚠️ JUSTIFICADO |

### 2. AUDITORÍA DE HUELLA Y RECURSOS
- **Líneas de código:** [Reducción neta %]
- **Dependencias añadidas:** 0 (Uso exclusivo de APIs nativas)
- **Manejo de hilos:** [Asíncrono / Fuera de UI Thread / Pool acotado]
- **Liberación de recursos:** [Verificada en bloque finally/dispose]
4. DIRECTIVAS DE ACCIÓN INMEDIATA (PROMPTS DE DISPARO)
Copia y pega la directiva correspondiente para ordenar la ejecución al agente:

Disparo Fase 1 y 2: Diagnóstico Inicial
Plaintext
Bajo el protocolo ZNVE_LEGACY_PROTOCOL.md, asume el rol de Ingeniero Forense.
Analiza el archivo [RUTA_DEL_ARCHIVO] en MODO SOLO LECTURA.
RESTRICCIÓN: Prohibido modificar archivos, prohibido proponer refactorizaciones 
y prohibido agregar dependencias.
Entrega exclusivamente el ARTEFACTO A: Reporte Forense completo.
Disparo Fase 3: Arnés de Pruebas
Plaintext
Bajo el protocolo ZNVE_LEGACY_PROTOCOL.md, genera la FASE 3: Arnés de Caracterización (Golden Master).
Objetivo: Probar [RUTA_DEL_ARCHIVO] como caja negra SIN ALTERAR UNA SOLA LÍNEA de su código.
Construye las pruebas en un archivo dentro de tests/characterization/ cubriendo casos estándar, 
límites y valores erróneos. Entrega el código de prueba y el comando exacto para ejecutarlo.
Disparo Fase 4 y 5: Implementación en Sombra y Migración
Plaintext
Bajo el protocolo ZNVE_LEGACY_PROTOCOL.md, ejecuta las FASES 4 y 5 sobre [RUTA_DEL_ARCHIVO]:
1. Implementa el módulo nuevo desacoplado en [RUTA_NUEVA] bajo contrato estricto ZNVE 
   (mínima huella, cero librerías parásitas, tipado estricto).
2. Proporciona la suite comparativa dual que verifique: Salida(Nuevo) == Salida(Legacy).
3. Entrega el ARTEFACTO B con la comparativa y el plan de conmutación Strangler Fig.
RESTRICCIÓN: El archivo legacy de producción permanece intacto.