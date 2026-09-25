---

#### `SPECIFICATION.md`
```markdown
# ZNVE Specification (v1.0.0)
**Status:** Stable  
**Category:** Architecture & AI-Agent Governance  
**Author:** Jeffry Carmona (jeffryc6)  
**Date:** 2026-09-24  

## 1. Alcance y Terminología
La presente especificación establece las reglas formales que gobiernan la interacción entre desarrolladores humanos y modelos de inteligencia artificial generativa durante el ciclo de vida del software.

- **Director de Arquitectura (Humano):** Responsable exclusivo de delimitar el perímetro, aprobar contratos y certificar la paridad funcional.
- **Ejecutor Táctico (Agente de IA):** Entidad algorítmica restringida a la generación de sintaxis determinista que satisfaga los contratos sin introducir modificaciones estructurales no solicitadas.
- **Contrato:** Estructura tipada e inmutable (DTO, interfaz, esquema Zod, TypeBox o JSON Schema) que delimita entradas, salidas, efectos secundarios y modos de fallo tolerados.

## 2. Los Dos Axiomas de Gobernanza
- **Axioma 1 (Asimetría Computacional):** Toda complejidad reflexiva y modelado de datos debe resolverse en la fase de diseño. El artefacto final en tiempo de ejecución debe poseer una huella de memoria, CPU y red cercana a cero.
- **Axioma 2 (Determinismo Contractual):** La IA tiene prohibido deducir, extrapolar o inventar esquemas de datos o topologías de red. Toda lógica generada debe ser la consecuencia directa de un contrato preaprobado.

## 3. Cláusulas Normativas

### 3.1. Cláusula de Higiene de Dependencias (Anti-Bloat)
Queda prohibido incorporar paquetes de terceros cuando la funcionalidad requerida pueda resolverse mediante las APIs estándar provistas por el lenguaje, runtime o SDK del sistema anfitrión.

### 3.2. Cláusula de Observabilidad Silenciosa
La telemetría en rutas críticas de ejecución debe operar bajo el principio de reporte por excepción. Queda prohibida la emisión de registros rutinarios de confirmación de operatividad normal. Las alertas se reservan exclusivamente para anomalías o fallos de severidad media y alta.

### 3.3. Cláusula de Persistencia y Proyección
Toda interacción con motores de almacenamiento (relacionales, documentales, clave-valor o en memoria) debe ejecutarse mediante proyecciones de campos explícitos. Quedan prohibidas las consultas de barrido completo o comodines sin rutas indexadas.

### 3.4. Cláusula de No Intervención Legacy (Zero-Touch)
Ningún agente de IA modificará un archivo catalogado como legacy sin haber generado previamente un arnés de caracterización de caja negra (Golden Master) en un directorio aislado que certifique paridad matemática sobre el código intacto.

## 4. Capa Camaleónica (Chameleon Layer)
La especificación se adapta al entorno de despliegue mediante restricciones de plataforma:
- **Mobile (Android/iOS):** Prioridad a tareas diferidas, respeto estricto al ciclo de vida del sistema y reposo profundo sin consumo de batería.
- **Desktop (Windows/macOS/Linux):** Manejo explícito de desecho de recursos no administrados, operaciones asíncronas puras y aislamiento de tareas pesadas fuera del hilo principal de la interfaz gráfica.
- **Backend / Microservicios:** Timeouts cerrados, contención de concurrencia y apagado elegante (graceful shutdown).