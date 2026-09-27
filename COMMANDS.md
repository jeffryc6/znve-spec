# COMMANDS.md: Catálogo de Comandos y Herramientas ZNVE
**Ecosistema Agéntico v2.3.0**

---

## 🛠️ COMANDOS AGÉNTICOS DE BARRA (`/znve-*`)

### 1. `/znve-contract`
* **Definición:** Diseña o actualiza el contrato DTO/Zod/Pydantic y selecciona el stack técnico ideal por plataforma.
* **Sintaxis:** `/znve-contract [--platform=desktop|web|mobile|hybrid] [--delta]`
* **Flujo Operativo:**
  1. Identifica el tipo de plataforma (Escritorio, Web, Android, iOS/macOS, Híbrida).
  2. Muestra la recomendación de stack (Tooling, BD/Persistencia, UI).
  3. Genera DTOs e Interfaces en `contracts/`.
  4. Valida la Lista de Chequeo de Solidez (4 puntos).
  5. Aplica el **Stop Criterion** y se detiene.

### 2. `/znve-contract --delta`
* **Definición:** Sincroniza incrementalmente el contrato en proyectos en desarrollo.
* **Flujo Operativo:**
  1. Compara `contracts/` vs `src/`.
  2. Divide sugerencias en **Cubo A (Requerido Ya)** y **Cubo B (Diferido a `CONTRACT_BACKLOG.md`)**.
  3. Actualiza el contrato y re-congela antes de escribir código.

### 3. `/znve-execute`
* **Definición:** Ejecución quirúrgica de lógica de negocio bajo contrato aprobado.
* **Sintaxis:** `/znve-execute --target=src/[ruta/archivo]`
* **Restricciones:** Modifica únicamente el `TARGET_FILE` asignado. Aplica patrón de desecho de recursos y prohíbe bloques `try/catch` vacíos.

### 4. `/znve-forensic`
* **Definición:** Diagnóstico estático de solo lectura (*Zero-Touch*).
* **Sintaxis:** `/znve-forensic --target=src/[ruta/modulo]`
* **Restricciones:** Prohibido modificar el disco. Devuelve mapa de causa raíz, efectos secundarios y cuellos de botella.

### 5. `/znve-harness`
* **Definición:** Genera una suite de caracterización Golden Master para aislar código frágil.
* **Sintaxis:** `/znve-harness --target=src/[ruta/archivo_legacy]`
* **Ubicación de Salida:** `tests/characterization/test_[modulo]_harness.[ext]`

### 6. `/znve-hotfix`
* **Definición:** Triaje y contención de fallos críticos en producción.
* **Sintaxis:** `/znve-hotfix --incident=[ID]`
* **Restricciones:** Actúa sobre la frontera del adaptador sin alterar el núcleo de la aplicación. Inyecta `X-Run-ID`.

### 7. `/znve-upgrade`
* **Definición:** Actualización de SDKs o dependencias externas con breaking changes.
* **Sintaxis:** `/znve-upgrade --dependency=[LIBRERÍA]`
* **Patrón:** Implementa la Capa Anti-Corrupción (Adapter Pattern) para absorber el cambio.

### 8. `/znve-audit`
* **Definición:** Auditoría y purga de higiene técnica.
* **Sintaxis:** `/znve-audit --target=src/[modulo]`
* **Acciones:** Elimina bloqueos de hilos en UI, detecta handles sin liberar y purga logs rutinarios de depuración.

---

## 🔌 HERRAMIENTAS MCP (`znve_*`)

Para agentes conectados vía Model Context Protocol (stdio):

* `znve_forensic_scan`: Inspección analítica de árbol de archivos y dependencias.
* `znve_validate_contract`: Validación sintáctica y semántica de esquemas DTO.
* `znve_scaffold_harness`: Despliegue de suite de caracterización aislada.
* `znve_surgical_write`: Escritura atómica condicionada con verificación de recursos y try/catch.
* `znve_audit_resources`: Detección de bloqueos síncronos y pérdidas de memoria.
