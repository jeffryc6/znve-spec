# ==============================================================================
# ZERO-NOISE VIBE ENGINEERING (ZNVE) — PROTOCOLO PARA APLICACIONES MODERNAS
# Archivo: protocols/ZNVE_ModernApps_Protocol.MD
# Versión: 1.0.0
# Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
# Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
# ==============================================================================

Este protocolo rige la intervención, triaje de incidentes, mitigación de fallas críticas (hotfix),
mantenimiento evolutivo y actualización de dependencias con breaking changes en
APLICACIONES MODERNAS EN PRODUCCIÓN.

Aplica a proyectos estructurados (Clean Architecture, Hexagonal, Modular, Microservicios,
Mobile moderno Android/iOS, Desktop WinUI/Tauri y Web Apps reactivas) donde existe código
organizado y pruebas, pero que sufren fallas en tiempo de ejecución o requieren modernización.

---

## 🛑 EL PROBLEMA DE LA IA EN APLICACIONES MODERNAS

Cuando se solicita a una IA intervenir una aplicación moderna con fallos o dependencias desactualizadas:
1. **Parches Ciegos (Monkey-Patching):** Agrega bloques `try/catch` vacíos, silencia errores con valores por defecto o añade reintentos ciegos que saturan los servidores.
2. **Contaminación en Cascada:** Al actualizar una librería o resolver un bug, muta interfaces compartidas, rompiendo módulos adyacentes no relacionados.
3. **Alucinación de Dependencias:** Instala wrappers externos innecesarios en lugar de resolver la incompatibilidad mediante adaptadores nativos.

**Regla de Oro en Apps Modernas:** 
*Ningún hotfix rompe contratos públicos existentes. Ninguna actualización externa contamina el dominio central.*

---

## 🎛️ FLUJOS OPERATIVOS DEL PROTOCOLO MODERNO

El protocolo define dos procedimientos de alta precisión:
1. **Flujo A: Protocolo Hotfix & Incident Recovery (Modo 3)** -> Producción caída o degradada.
2. **Flujo B: Protocolo Modern Maintenance & Upgrades (Modo 4)** -> Migración de SDKs, APIs y Breaking Changes.

┌────────────────────────────────────────────────────────────────────────┐
│                   FLUJO A: HOTFIX & INCIDENT RECOVERY                  │
│                                                                        │
│ [ Fase A.1 ] Contención y Aislamiento del Radio de Impacto             │
│      ↓                                                                 │
│ [ Fase A.2 ] Diagnóstico Causal Forense (Zero-Patching)                │
│      ↓                                                                 │
│ [ Fase A.3 ] Hotfix Atómico por Contrato Bounded                       │
│      ↓                                                                 │
│ [ Fase A.4 ] Test de Regresión Inmediato & Despliegue Silencioso       │
├────────────────────────────────────────────────────────────────────────┤
│                FLUJO B: MODERN MAINTENANCE & UPGRADES                  │
│                                                                        │
│ [ Fase B.1 ] Diff Contractual y Matriz de Breaking Changes             │
│      ↓                                                                 │
│ [ Fase B.2 ] Capa Anti-Corrupción (Adapter Pattern ZNVE)               │
│      ↓                                                                 │
│ [ Fase B.3 ] Migración Quirúrgica Aislada                              │
│      ↓                                                                 │
│ [ Fase B.4 ] Verificación de Rendimiento y Descarte de Deprecaciones   │
└────────────────────────────────────────────────────────────────────────┘


---

## 🚨 FLUJO A: PROTOCOLO HOTFIX & INCIDENT RECOVERY (PRODUCCIÓN EN CRISIS)

### FASE A.1: CONTENCIÓN Y AISLAMIENTO DEL RADIO DE IMPACTO (BLAST RADIUS FENCE)
* **Objetivo:** Detener la degradación del servicio sin intentar refactorizar la aplicación en caliente.
* **Acciones Obligatorias del Agente:**
  1. Identificar si el fallo está colapsando el proceso completo (CrashLoop), bloqueando el hilo de interfaz, o saturando recursos compartidos (conexiones, memoria, sockets).
  2. Implementar una contención inmediata que no altere el modelo de datos:
     - Activar fallback local (devolviendo caché fría o estado offline consistente).
     - Aislar el endpoint o componente degradado mediante Circuit Breaker sin tumbar el resto de la aplicación.
* **Restricción:** Prohibido modificar esquemas de base de datos o firmas de APIs públicas durante la contención.

### FASE A.2: DIAGNÓSTICO CAUSAL FORENSE (ZERO-PATCHING)
* **Objetivo:** Encontrar el defecto raíz reproducible sin colocar parches cosméticos.
* **Acciones Obligatorias del Agente:**
  1. Analizar el stack trace y las condiciones de contorno:
     - ¿Es una condición de carrera (concurrencia, falta de sincronización)?
     - ¿Es un agotamiento de recursos (descriptores abiertos, leaks de memoria, pool saturado)?
     - ¿Es una discrepancia de contrato (payload nulo, tipo inesperado de un servicio tercero)?
  2. Elaborar el **Reporte de Incidente Atómico** (Plantilla 1).
* **Restricción:** Prohibido añadir retardos arbitrarios (`sleep`, `setTimeout`) para ocultar condiciones de carrera.

### FASE A.3: HOTFIX ATÓMICO POR CONTRATO BOUNDED
* **Objetivo:** Corregir el defecto interviniendo el menor número de líneas posibles.
* **Acciones Obligatorias del Agente:**
  1. Delimitar un único archivo objetivo (`TARGET_FILE`). Si el cambio requiere tocar más de dos archivos, el diseño del hotfix es incorrecto y debe aislarse mejor.
  2. Aplicar la corrección respetando las invariantes del módulo:
     - Manejo explícito de excepciones sin bloques `catch` vacíos.
     - Garantizar la liberación de recursos en cláusula `finally` / `dispose`.
     - Conservar exactamente la firma y el contrato público del módulo.

### FASE A.4: TEST DE REGRESIÓN INMEDIATO & VERIFICACIÓN
* **Objetivo:** Demostrar matemáticamente que el hotfix resuelve la falla y no crea nuevos defectos.
* **Acciones Obligatorias del Agente:**
  1. Escribir un test unitario o de integración (`tests/regression/issue_XXX_test.*`) que:
     - Falle al ejecutarse contra el código sin parchear (reproducción fehaciente del bug).
     - Pase al 100% en verde con el hotfix aplicado.
  2. Proporcionar el comando exacto para ejecutar la prueba en local o CI antes del despliegue.

---

## 📦 FLUJO B: MODERN MAINTENANCE & UPGRADES (SDKs, APIs Y BREAKING CHANGES)

### FASE B.1: DIFF CONTRACTUAL Y MATRIZ DE RUPTURA
* **Objetivo:** Mapear con precisión quirúrgica qué cambió entre la versión instalada y la versión objetivo.
* **Acciones Obligatorias del Agente:**
  1. Identificar los *Breaking Changes* formales del changelog oficial:
     - Métodos renombrados o eliminados.
     - Tipos de retorno modificados.
     - Cambios en el modelo de hilos o concurrencia (ej. callbacks -> async/await, corrutinas).
  2. Identificar qué archivos del proyecto importan directamente la dependencia.

### FASE B.2: CAPA ANTI-CORRUPCIÓN (ADAPTER PATTERN ZNVE)
* **Objetivo:** Blindar la lógica de negocio para que la actualización no obligue a reescribir código interno.
* **Acciones Obligatorias del Agente:**
  1. Si la librería de terceros se usaba directamente en la lógica de negocio, diseñar un contrato interno ZNVE (`Port / Interface`) propio del proyecto.
  2. Crear un adaptador (`Adapter`) que encapsule la nueva versión de la librería externa:
     - Toda incompatibilidad de tipos se resuelve dentro del adaptador.
     - El resto de la aplicación consume únicamente el contrato interno inmutable.

### FASE B.3: MIGRACIÓN QUIRÚRGICA AISLADA
* **Objetivo:** Actualizar la dependencia en el manifiesto de paquetes y compilar sin advertencias.
* **Acciones Obligatorias del Agente:**
  1. Modificar el gestor de paquetes (Gradle, SwiftPM, package.json, Cargo, Nuget) fijando la versión exacta.
  2. Implementar los cambios exclusivamente en los adaptadores correspondientes.
  3. Resolver deprecaciones de plataforma sin recurrir a supresores de advertencias (`@SuppressWarnings`, `#pragma warning disable`) a menos que no exista alternativa nativa.

### FASE B.4: VERIFICACIÓN DE HUELLA Y REGRESIÓN
* **Objetivo:** Certificar que la nueva versión no introdujo sobreconsumo de CPU, memoria o bloatware.
* **Acciones Obligatorias del Agente:**
  1. Ejecutar la suite completa de tests de la aplicación.
  2. Medir que el tamaño del binario resultante y el consumo en reposo cumplan con el principio de mínima huella ZNVE.

---

## 📋 PLANTILLAS DE REPORTE Y SALIDA ESTANDARIZADAS

### PLANTILLA 1: REPORTE DE INCIDENTE & HOTFIX (MODO 3)

```markdown
### 1. REPORTE DE INCIDENTE TÉCNICO (ROOT CAUSE)
- **Componente Afectado:** [Ruta del archivo / módulo]
- **Síntoma en Producción:** [CrashLoop / Deadlock / Memory Leak / 500 Error / UI Freeze]
- **Causa Raíz Determinista:** [Explicación técnica exacta del fallo, sin conjeturas]
- **Radio de Impacto:** [Aislado a un endpoint / General / Fallback activo]

### 2. ESPECIFICACIÓN DEL HOTFIX (BOUNDED CONTRACT)
- **TARGET_FILE:** [Ruta exacta del único archivo modificado]
- **Modificación Quirúrgica:** [Descripción técnica del cambio]
- **Garantía Anti-Crash:** [Cómo se previene la reaparición del error sin usar catch vacíos]

### 3. TEST DE REGRESIÓN DETERMINISTA
- **Archivo de Test:** `tests/regression/test_incident_[ID].[ext]`
- **Comando de Verificación:** `[comando exacto de ejecución]`
- **Resultado:** Fallo reproducido en código base -> Éxito 100% verde con hotfix.
PLANTILLA 2: MATRIZ DE MIGRACIÓN & UPGRADE (MODO 4)
Markdown
### 1. MATRIZ DE BREAKING CHANGES
| Dependencia / SDK | Versión Previa | Versión Objetivo | Breaking Changes Detectados |
|---|---|---|---|
| [Nombre SDK] | `v1.2.0` | `v2.0.0` | [Firma de método cambiada a async, DTO obsoleto] |

### 2. DISEÑO DEL ADAPTADOR ANTI-CORRUPCIÓN
- **Contrato Interno:** `src/core/ports/[nombre].contract.ts`
- **Adaptador Externo:** `src/infrastructure/adapters/[nombre].adapter.ts`
- **Archivos de Negocio Mutados:** 0 (Aislamiento total de lógica de dominio)

### 3. VERIFICACIÓN Y HUELLA
- **Tests del Adaptador:** [100% verde]
- **Impacto en Binario/Memoria:** [Variación neta en KB / RAM en reposo estable]
- **Comando de Verificación:** `[comando exacto de compilación y tests]`