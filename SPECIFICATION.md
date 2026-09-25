# ZNVE Specification (v1.1.0)
**Status:** Stable  
**Category:** Architecture & AI-Agent Governance  
**Author:** Jeffry Carmona (jeffryc6)  
**Date:** 2026-09-25  

## 1. Alcance y Terminología
La presente especificación establece las cláusulas normativas que gobiernan la interacción entre desarrolladores de software y modelos de inteligencia artificial generativa durante el ciclo de vida del software (desarrollo nuevo, mantenimiento, recuperación ante incidentes y refactorización legacy).

- **Director de Arquitectura (Humano):** Responsable exclusivo de delimitar el perímetro del problema, validar contratos tipados y certificar la paridad funcional.
- **Ejecutor Táctico (Agente de IA):** Entidad algorítmica restringida a la generación de sintaxis determinista que satisface contratos sin introducir modificaciones estructurales no autorizadas.
- **Contrato:** Estructura tipada e inmutable (DTO, interfaz, esquema Zod o modelo relacional estricto) que define entradas, salidas, efectos secundarios y modos de fallo tolerados.
- **Radio de Impacto (Blast Radius):** Alcance máximo de archivos o componentes que pueden ser intervenidos durante una remediación de emergencia.

## 2. Los Dos Axiomas de Gobernanza
- **Axioma 1 (Asimetría Computacional):** Toda complejidad analítica y modelado de datos debe resolverse en la fase de diseño. El artefacto final en tiempo de ejecución debe operar con una huella de memoria, CPU y red cercana a cero.
- **Axioma 2 (Determinismo Contractual):** La IA tiene prohibido deducir o improvisar esquemas de datos, topologías o dependencias externas. Toda lógica generada debe derivar de un contrato preaprobado.

## 3. Cláusulas Normativas Universales

### 3.1. Cláusula de Higiene de Dependencias (Anti-Bloat Fence)
Queda prohibido incorporar paquetes de terceros cuando la funcionalidad requerida pueda resolverse mediante las APIs estándar provistas por el lenguaje, runtime o SDK del sistema anfitrión.

### 3.2. Cláusula de Observabilidad Silenciosa (Zero-Noise Runtime)
La telemetría en rutas críticas debe operar bajo el principio de reporte por excepción. Queda prohibida la emisión de registros rutinarios de confirmación de estado saludable (`"OK"`, `"Success"`). Las alertas se reservan exclusivamente para anomalías operativas de severidad media o alta.

### 3.3. Cláusula de Persistencia y Proyección Explícita
Toda interacción con motores de almacenamiento (relacionales, documentales, clave-valor o en memoria) debe ejecutarse mediante proyecciones de campos explícitos. Quedan prohibidas las consultas de barrido completo (`SELECT *`, `find({})` sin filtros) sin rutas indexadas.

### 3.4. Cláusula de Contención y Hotfix Quirúrgico (Blast Radius Fence)
Ante incidentes críticos o fallos en aplicaciones modernas en producción:
1. Queda prohibido aplicar soluciones cosméticas (*monkey-patching*), bloques `try/catch` vacíos o retardos arbitrarios (`sleep`).
2. La remediación debe limitarse a un único archivo causante (`TARGET_FILE`).
3. El parche debe conservar intactos los contratos públicos y venir acompañado obligatoriamente de una prueba de regresión determinista que reproduzca la falla y valide su resolución.

### 3.5. Cláusula de Aislamiento de Dependencias Modernas (Adapter Anti-Corrupción)
Al actualizar dependencias externas, frameworks o SDKs que contengan *breaking changes*, el agente de IA tiene prohibido mutar la lógica de negocio central. Toda incompatibilidad debe encapsularse detrás de una interfaz interna (*Port*) y un adaptador desacoplado (*Adapter*).

### 3.6. Cláusula de No-Intervención Legacy (Zero-Touch Assurance)
Ningún agente de IA modificará un archivo catalogado como legacy sin haber generado previamente un arnés de caracterización de caja negra (*Golden Master*) en un directorio aislado que certifique paridad matemática sobre el código original intacto.

## 4. Clasificación de Modos Operativos
Toda tarea ejecutada bajo ZNVE debe encuadrarse en uno de los 6 modos normativos:
- **Modo 1 (Greenfield):** Desarrollo desde cero con perímetro acotado y contrato previo.
- **Modo 2 (In-Flight):** Expansión modular sobre proyectos activos sin alterar contratos base.
- **Modo 3 (Hotfix & Recovery):** Triage forense, contención y parches atómicos en crisis de producción.
- **Modo 4 (Modern Maintenance):** Migración de SDKs y breaking changes vía capas de adaptación.
- **Modo 5 (Legacy Rescue):** Modernización de sistemas monolíticos en 5 fases controladas.
- **Modo 6 (Audit & Hardening):** Mitigación de fugas, contención de sockets y aislamiento de hilos.
