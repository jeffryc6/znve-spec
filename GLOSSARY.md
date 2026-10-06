# GLOSSARY.md: Glosario técnico de ZNVE / ZNVE Technical Glossary

Términos formales de Zero-Noise Vibe Engineering (ZNVE v2.3.0) en español e inglés. La norma completa está en [SPECIFICATION.md](SPECIFICATION.md) y el catálogo de comandos en [protocols/COMMANDS.md](protocols/COMMANDS.md).

---

## 1. Axiomas y filosofía base

* **Zero-Noise Vibe Engineering (ZNVE) / Ingeniería Vibe de Cero Ruido:** metamodelo de arquitectura y gobernanza para el desarrollo de software asistido por agentes de IA (*Contract-First Agentic Architecture*). Convierte la velocidad conversacional del *vibe coding* en un estándar de ingeniería riguroso, minimalista y libre de deuda técnica.

* **Axioma 1: Asimetría Computacional / Axiom 1: Computational Asymmetry:** *"Inteligencia pesada en el diseño; huella casi nula en la ejecución"*. La complejidad reflexiva y el modelado de datos se resuelven en el diseño, para que el artefacto en producción consuma el mínimo de CPU, memoria, batería y red.

* **Axioma 2: Determinismo Contractual / Axiom 2: Contractual Determinism:** *"La IA no inventa arquitectura; ejecuta contratos deterministas"*. Prohíbe a los modelos probabilísticos deducir, extrapolar o crear arquitecturas de forma autónoma.

* **Vibe Coding Convencional / Conventional Vibe Coding:** práctica informal basada en prompts narrativos que delega decisiones estructurales a la IA sin validación técnica, y que deriva en dependencias parásitas, bloques `try/catch` vacíos y fragilidad operativa.

* **Cero Ruido Operativo / Zero-Noise Operations:** disciplina que prohíbe el código muerto, los paquetes redundantes y la telemetría de confirmación rutinaria (*"OK"*, *"Success"*). La observabilidad se reserva para excepciones y transiciones críticas.

* **Cero Relleno Conversacional / Zero Conversational Filler:** supresión de disculpas, cortesías, preámbulos y divagaciones en las respuestas del agente, que entrega directamente artefactos técnicos.

* **Poda de Contexto / Context Boundary Pruning:** regla que entrega al agente solo el contrato activo y el archivo objetivo (`TARGET_FILE`), para evitar la sobrecarga de contexto y los bucles de alucinación.

---

## 2. Gobernanza agéntica y roles

* **Director de Arquitectura / Chief Architect:** rol del desarrollador humano. Delimita el perímetro del problema, diseña o aprueba los contratos inmutables y certifica la paridad funcional.

* **Ejecutor Táctico / Tactical Executor:** rol del modelo o agente de IA. Genera sintaxis que cumple con exactitud el contrato, sin abstracciones prematuras ni lógica especulativa.

* **Desvío Agéntico / Agentic Drift:** fenómeno en el que un agente pierde el contexto original, alucina dependencias, reescribe arquitecturas sin autorización o introduce código no solicitado.

* **Archivo Objetivo / Target File (`TARGET_FILE`):** directiva que confina la intervención de la IA a una única ruta de archivo por tarea atómica, para impedir mutaciones en cascada.

* **Barrera Anti-Sobrepeso / Anti-Bloat Fence:** restricción que veta paquetes externos, métodos redundantes o dependencias cuando el runtime, el SDK nativo o la biblioteca estándar resuelven el problema. Una librería de terceros solo entra como excepción justificada en el propio contrato: qué resuelve, su peso y la alternativa nativa descartada.

* **Cerca de Contexto / Context Fence:** guardrail 8. El contexto del agente es por excepción, igual que la telemetría: rangos en lugar de archivos completos, verificaciones silenciosas, contratos por ruta, cero secretos y todo contenido externo tratado como dato, nunca como instrucción. Se aplica también por código en el servidor MCP.

* **Verificación Inviolable / Inviolable Verification:** guardrail 9. No se modifican tests, snapshots ni configuración de pruebas existentes para obtener verde, y no se declara un resultado que no se ejecutó. Un test sospechoso se reporta y el agente se detiene hasta que el humano lo apruebe.

* **Arnés de caracterización / Characterization Harness:** suite Golden Master que `/znve-harness` crea sobre código legacy intacto para congelar su comportamiento. No es el *arnés de agente* (*agent harness*, como DeepSeek Harness), que es el entorno que ejecuta al agente: herramientas, contexto y permisos.

* **Guardrail / Guardrail:** regla operativa que el agente aplica en cada respuesta. ZNVE traduce sus 5 pilares en 9 guardrails (ver [SPECIFICATION.md §2.6](SPECIFICATION.md)).

---

## 3. Contratos, datos y persistencia

* **Contrato Determinista / Deterministic Contract:** estructura tipada e inmutable (DTO, interfaz, esquema Zod, TypeBox, Pydantic o JSON Schema) que define entradas, salidas, tipos, límites y modos de fallo tolerados de un módulo.

  ```typescript
  interface UserSessionContract {
    readonly userId: string;
    readonly roles: readonly ('admin' | 'operator')[];
    readonly expiresAtEpochMs: number;
  }
  ```

* **DTO (Data Transfer Object) / Objeto de Transferencia de Datos:** modelo de datos plano y tipado que actúa como frontera formal entre capas o servicios. En ZNVE congela la comunicación antes de que la IA genere lógica interna.

* **Lista de Chequeo de Solidez / Solidity Checklist:** 4 condiciones que un contrato debe cumplir antes de programar: estructura invariable, defensas de frontera, cero dependencias parásitas y filtro de diferimiento.

* **Criterio de Parada / Stop Criterion:** al cumplirse la lista de chequeo, la IA emite *"Contrato v1 sólido y cerrado. Listo para /znve-execute."* y deja de proponer cambios.

* **Análisis Delta / Delta Analysis (`/znve-contract --delta`):** auditoría incremental entre `contracts/` y `src/` en proyectos en curso, que re-congela el contrato antes de modificar código.

* **Cubo A y Cubo B / Bucket A & Bucket B:** clasificación del análisis delta. El Cubo A reúne lo requerido en la etapa activa; el Cubo B, las ideas diferidas a `contracts/CONTRACT_BACKLOG.md`.

* **Persistencia Agnóstica / Agnostic Persistence:** principio que aplica el mismo rigor a almacenes relacionales, documentales, clave-valor, series temporales, grafos, vectoriales o almacenamiento local embebido.

* **SQL en ZNVE / SQL in ZNVE:** se exige integridad referencial, transacciones ACID y proyecciones explícitas.
  * No permitido: `SELECT * FROM audits;`
  * Permitido: `SELECT id, bot_score, created_at FROM audits WHERE run_id = $1;`

* **Persistencia NoSQL / NoSQL Persistence:** motores documentales (MongoDB, Firestore) en los que el contrato impone validación de esquema en frontera.
  * No permitido: `db.collection.find({})`
  * Permitido: `db.collection.find({ run_id }, { projection: { ja4: 1, bot_score: 1 } })`

* **Persistencia Clave-Valor y en Memoria / Key-Value & In-Memory Store:** almacenes como Redis o Valkey, donde el contrato exige claves deterministas y TTL obligatorio para evitar la saturación silenciosa de RAM. Ejemplo de clave tipada: ``type SessionKey = `rl:${string}:${number}`;``

* **Proyecciones Explícitas / Explicit Projections:** prohibición de consultar colecciones, tablas o documentos completos por defecto; solo se seleccionan los campos del contrato.

* **Rutas Indexadas / Indexed Access Paths:** obligación de apoyar toda lectura en índices existentes (B-Tree, TTL, claves primarias o foráneas) para evitar escaneos lineales completos.

---

## 4. Técnicas de ejecución y rescate legacy

* **Ingesta Pasiva / Passive Ingestion (Zero-Touch):** primera fase de análisis de un sistema existente, en solo lectura estricta: mapea entradas, salidas, dependencias y contratos implícitos sin alterar el código.

* **Arnés de Caracterización / Characterization Test Harness (Golden Master):** batería de pruebas de caja negra en un directorio aislado (`tests/characterization/`) que congela las salidas exactas del sistema legacy intacto, incluidos los comportamientos accidentales tolerados.

* **Ejecución en Sombra / Shadow Run:** el código nuevo y el original se ejecutan con las mismas entradas para certificar `Salida(Nuevo) == Salida(Legacy)`.

* **Patrón Estrangulador / Strangler Fig Pattern:** sustitución gradual de componentes monolíticos por módulos desacoplados hasta retirar el código antiguo sin caídas.

* **Equilibrios Accidentales / Accidental Balances:** código contradictorio o redundante en sistemas legacy que funciona por orden de evaluación y que no debe tratarse como fallo sin verificación forense previa.

* **Radio de Impacto / Blast Radius:** alcance máximo de archivos o componentes afectados por un fallo o permitidos en una reparación de emergencia.

* **Capa Anti-Corrupción / Anti-Corruption Layer (Adapter Pattern):** aislamiento de una dependencia externa con *breaking changes* detrás de un puerto (`Port`) y un adaptador (`Adapter`), para que no contamine el dominio.

* **Trazabilidad `X-Run-ID` / `X-Run-ID` Traceability:** identificador de ejecución propagado entre componentes para reconstruir un incidente sin logs rutinarios.

---

## 5. Modos de operación y plataforma

* **Modo Greenfield / Greenfield Mode (Modo 1):** desarrollo desde cero bajo perímetros acotados, contrato previo y código de mínima huella.

* **Modo In-Flight / In-Flight Mode (Modo 2):** nuevas capacidades en sistemas activos sin mutar los contratos existentes, mediante análisis delta.

* **Modo Hotfix y Recuperación / Hotfix & Recovery Mode (Modo 3):** emergencia en producción: contención del radio de impacto, causa raíz y parche atómico con test de regresión.

* **Modo Mantenimiento Moderno / Modern Maintenance Mode (Modo 4):** migración de versiones mayores de SDKs o APIs encapsulando los cambios en adaptadores.

* **Modo Rescate Legacy / Legacy Rescue Mode (Modo 5):** metodología en 5 fases (ingesta pasiva, reporte forense, Golden Master, Shadow Run y Strangler Fig) para monolitos sin pruebas.

* **Modo Auditoría y Blindaje / Audit & Hardening Mode (Modo 6):** auditoría forense de contención de hilos, puertos expuestos, fugas de memoria, ruido de logs y consumo parásito.

* **Capa Camaleónica / Chameleon Layer:** matriz que ajusta las restricciones técnicas al stack anfitrión (Android, iOS/macOS, Windows Desktop, Híbrido o Web/Backend).

* **Hilo Principal Sagrado / Sacred Main Thread (UI Thread / Event Loop):** prohibición de ejecutar I/O síncrono, criptografía pesada o transformaciones masivas en el hilo de interfaz o en el bucle de eventos.

---

## 6. Comandos y herramientas

* **Comando de Barra / Slash Command (`/znve-*`):** palabra clave que impone al agente un rol cerrado y un formato de salida con encabezados fijos. Las formas `/znve-contract`, `/znve contract` y `/znve -contract` son equivalentes.

* **Formato de 4 Bloques / Default 4-Block Format:** estructura obligatoria de toda respuesta técnica sin comando: Blueprint y Contrato, Racional, Tarea Atómica y Verificación.

* **Herramienta MCP / MCP Tool (`znve_*`):** función expuesta por el servidor MCP de ZNVE (Model Context Protocol, transporte stdio) que convierte una cláusula en una barandilla física; por ejemplo, `znve_surgical_write` rechaza `catch` vacíos.

* **`ZNVE_WORKSPACE`:** variable de entorno que fija la raíz del proyecto contra la que el servidor MCP resuelve las rutas.

* **Skill `znve` / `znve` Skill:** paquete instalable que enseña ZNVE a Claude (claude.ai y Claude Code), a Gemini (app y Gemini CLI) y a Antigravity.

---

## 7. Automatización y paridad

* **Fuente Única de Verdad / Single Source of Truth (SSoT):** `znve-auto/master_spec.json`, el único lugar donde se declaran la versión, los guardrails, los modos y los comandos.

* **Artefacto Generado / Generated Artifact:** archivo que produce `znve-auto/builder.py` desde la fuente única, como las directivas de cada asistente o los manuales de comandos. Lleva un aviso y no se edita a mano.

* **Bloque Gestionado / Managed Region:** fragmento de un archivo escrito a mano, delimitado por los marcadores `>>> znve:generated` y `<<< znve:generated`, que el compilador reescribe sin tocar el resto.

* **Detector de Desviación / Drift Detector:** suite `znve-auto/test_sync.py` que falla cuando un artefacto se aparta de la fuente única. Se ejecuta en el CI en cada push y pull request.

* **Paridad entre Plataformas / Cross-Platform Parity:** garantía de que todos los asistentes reciben los mismos comandos, guardrails y versión de ZNVE.

---

## 8. Matriz de traducción de términos clave

| Término (Español) | Term (English) | Contexto en ZNVE |
| --- | --- | --- |
| **Contrato Determinista** | Deterministic Contract | Interfaz o esquema inmutable obligatorio antes de generar código. |
| **Objeto de Transferencia de Datos** | Data Transfer Object (DTO) | Frontera de datos fuertemente tipada. |
| **Criterio de Parada** | Stop Criterion | Cierre del contrato al cumplir la lista de chequeo de solidez. |
| **Cubo A / Cubo B** | Bucket A / Bucket B | Requerido ya frente a diferido en el análisis delta. |
| **Persistencia Agnóstica** | Agnostic Persistence | Independencia del motor de datos (SQL, NoSQL, clave-valor). |
| **Barrera Anti-Sobrepeso** | Anti-Bloat Fence | Veto a dependencias si el SDK nativo resuelve la tarea. |
| **Poda de Contexto** | Context Boundary Pruning | El agente solo recibe el contrato activo y el `TARGET_FILE`. |
| **Arnés de Caracterización** | Characterization Test Harness | Pruebas de caja negra aisladas para congelar código legacy. |
| **Ejecución en Sombra** | Shadow Run | Comparación paralela de salidas entre sistema antiguo y nuevo. |
| **Ingesta Pasiva** | Passive Ingestion (Zero-Touch) | Lectura forense en solo lectura de código preexistente. |
| **Radio de Impacto** | Blast Radius | Frontera restringida para la remediación de incidentes. |
| **Capa Camaleónica** | Chameleon Layer | Adaptación de restricciones a Android, iOS, Windows, Web o Híbrido. |
| **Observabilidad Silenciosa** | Zero-Noise Observability | Logs y alertas solo ante fallos o anomalías. |
| **Fuente Única de Verdad** | Single Source of Truth | `znve-auto/master_spec.json` genera todas las directivas. |
| **Detector de Desviación** | Drift Detector | `znve-auto/test_sync.py` certifica la paridad en el CI. |
