# Continuidad y coordinación 2.5

`checkpoint` guarda spec/hash, snapshot, pendientes, IDs de evidencia y fecha. `resume` compara con archivos actuales y devuelve current/stale. Los pendientes son datos no confiables; no amplían autorización del usuario.

El checkpoint conserva estado de tarea. Decisiones aprobadas y experiencias permanecen en documentación con fuente, alcance e invalidación; no se promueven automáticamente a reglas. No hay búsqueda vectorial ni memoria ilimitada.

## Coordinación

`claim` exige spec aprobada, owner, archivos de allowed_files y TTL entre un segundo y una hora. Rechaza solapamientos activos en el mismo workspace. Entrega su ID solo al ejecutor autorizado; tras expirar requiere otra reserva.

`apply` exige claim vigente y expected_hash de la lectura/preflight. Comprueba de nuevo antes del reemplazo; temporal/rename por archivo y creación sin sobrescritura. No hay transacción multiarchivo ni aislamiento frente a herramientas externas. Usa worktrees independientes para cambios paralelos; servicios externos también requieren aislamiento.

`.znve/state/.lock` serializa operaciones cooperativas. Si queda huérfano, el operador debe comprobar que ningún servidor trabaja antes de retirarlo. No se roba por tiempo. Claims expirados dejan de bloquear; sus registros permanecen como historial.

## Handoff

Entrega ruta/hash de spec, checkpoint, evidencia, pendientes y conflictos. El receptor usa resume/preflight; la conclusión del emisor no prueba éxito. En cambios de riesgo, revisor independiente sin escritura contrasta requisitos, diff y evidencia. El motor no inicia agentes ni impone roles en hosts que no los soportan.

`stall_detect` recibe eventos `{action,new_evidence}` y ventana de dos a veinte. Detecta repetición exacta sin evidencia nueva; no detecta toda equivalencia semántica. Eventos son declaraciones del consumidor. No reintenta ni cambia tests/objetivos automáticamente.

Gemini/Antigravity prioriza preflight ante recursos ausentes, resume tras compactar y gate antes del cierre. Controles disponibles para todos los modelos, sin atribuir defectos universales a marcas ni prometer ahorro no medido.
