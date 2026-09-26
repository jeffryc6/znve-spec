"docs: add formal ZNVE technical glossary (ES/EN)"
### 1. Axiomas y Filosofía Base

* **Zero-Noise Vibe Engineering (ZNVE) / Ingeniería Vibe de Cero Ruido:** Metamodelo de arquitectura y gobernanza para el desarrollo de software asistido por agentes de IA (*Contract-First Agentic Architecture*), diseñado para transformar la intuición y velocidad conversacional del *vibe coding* en un estándar de ingeniería riguroso, minimalista y libre de deuda técnica.


* **Axioma 1: Asimetría Computacional / Axiom 1: Computational Asymmetry:** Regla inmutable que dicta: *"Inteligencia pesada en el diseño; huella casi nula en la ejecución"*. Toda la complejidad reflexiva y modelado de datos debe resolverse en la fase de diseño, garantizando que el artefacto en producción opere con mínimo consumo de CPU, memoria, batería y red.


* **Axioma 2: Determinismo Contractual / Axiom 2: Contractual Determinism:** Regla inmutable que dicta: *"La IA no inventa arquitectura; ejecuta contratos deterministas"*. Prohíbe a los modelos probabilísticos deducir, extrapolar o crear arquitecturas de forma autónoma.


* **Vibe Coding Convencional / Conventional Vibe Coding:** Práctica informal de desarrollo basada en prompts narrativos donde se delegan decisiones estructurales y sintácticas a la IA sin validación técnica estricta, derivando en dependencias parásitas, bloques `try/catch` vacíos y fragilidad operativa.


* **Cero Ruido Operativo / Zero-Noise Operations:** Disciplina que prohíbe la acumulación de código muerto, paquetes redundantes y emisión de telemetría de confirmación rutinaria (*"OK"*, *"Success"*); la observabilidad se reserva únicamente para excepciones o transiciones críticas.


* **Cero Ruido de Contexto (Anti-Drift) / Context Boundary Pruning:** Supresión de disculpas, cortesías, preámbulos conversacionales y divagaciones en las respuestas de los agentes de IA, forzando la interacción mediante artefactos técnicos atómicos.



---

### 2. Gobernanza Agéntica y Roles

* **Director de Arquitectura / Chief Architect:** Rol asumido por el desarrollador humano responsable exclusivo de delimitar el perímetro del problema, diseñar/aprobar los contratos inmutables y certificar la paridad funcional.


* **Ejecutor Táctico / Tactical Executor:** Rol asignado al modelo de lenguaje o agente de IA, restringido a generar sintaxis y código que cumpla con exactitud matemática el contrato establecido, sin agregar abstracciones prematuras ni lógica especulativa.


* **Desvío Agéntico / Agentic Drift:** Fenómeno en el cual un agente de IA pierde el contexto original, alucina dependencias externas, reescribe arquitecturas sin autorización o introduce código basura no solicitado.


* **Archivo Objetivo / Target File (`TARGET_FILE`):** Directiva estricta que confina la intervención de la IA a una única ruta de archivo por tarea atómica, impidiendo mutaciones en cascada en el resto del proyecto.


* **Barrera Anti-Sobrepeso / Anti-Bloat Fence:** Restricción obligatoria en la especificación que veta explícitamente paquetes externos, métodos redundantes o dependencias cuando el runtime, SDK nativo o biblioteca estándar anfitriona pueden resolver el problema.



---

### 3. Contratos, Datos y Persistencia

* **Contrato Determinista / Deterministic Contract:** Estructura tipada e inmutable (DTO, interfaz, esquema Zod, TypeBox o JSON Schema) que define estrictamente las entradas, salidas, tipos de datos, límites y modos de fallo tolerados de un módulo.


* *Ejemplo (TypeScript):*
```typescript
interface UserSessionContract {
  readonly userId: string;
  readonly roles: readonly ('admin' | 'operator')[];
  readonly expiresAtEpochMs: number;
}

```




* **DTO (Data Transfer Object) / Objeto de Transferencia de Datos:** Modelo de datos plano y tipado utilizado como frontera formal entre capas o servicios. En ZNVE se utiliza para congelar la comunicación antes de que la IA genere cualquier lógica interna.


* **Datos y Persistencia Agnóstica / Agnostic Persistence & Data Domain:** Principio que desacopla la metodología ZNVE de un motor de persistencia específico, gobernando con el mismo rigor técnico a almacenes relacionales, documentales, clave-valor, series temporales, grafos, vectoriales o almacenamiento local embebido.


* **SQL (Structured Query Language) en ZNVE / SQL in ZNVE:** Lenguaje de consulta declarativo para bases de datos relacionales. Bajo ZNVE, se exige el uso de integridad referencial, transacciones ACID y la prohibición expresa de consultas ciegas sin proyección.


* *Ejemplo de consulta no permitida:* `SELECT * FROM audits;`.


* *Ejemplo permitido bajo ZNVE:* `SELECT id, bot_score, created_at FROM audits WHERE run_id = $1;`.




* **Persistencia NoSQL / NoSQL Persistence:** Motores orientados a documentos (ej. MongoDB, Firestore) donde el contrato impone esquemas estrictos de validación en frontera para evitar almacenar cargas útiles no tipadas o registros no proyectados.


* *Ejemplo (MongoDB):* Prohibido `db.collection.find({})`; obligatorio usar proyecciones como `db.collection.find({ run_id }, { projection: { ja4: 1, bot_score: 1 } })`.




* **Persistencia Clave-Valor y En Memoria / Key-Value & In-Memory Store:** Almacenamiento rápido (ej. Redis, Valkey) donde el contrato exige estructuras de claves deterministas y políticas de expiración (TTL) obligatorias para evitar la saturación silenciosa de RAM.


* *Ejemplo de clave tipada:* `type SessionKey = \`rl:${string}:${number}`;`.




* **Proyecciones Explícitas / Explicit Projections:** Regla de datos que prohíbe volcar o consultar colecciones, tablas o documentos completos por defecto (`SELECT *`, comodines o consultas sin filtro), obligando a seleccionar únicamente los campos descritos en el contrato.


* **Rutas Indexadas / Indexed Access Paths:** Obligación técnica de apoyar toda lectura o consulta a la base de datos en índices existentes (B-Tree, TTL, claves primarias/foráneas) para erradicar escaneos lineales completos de disco o memoria.



---

### 4. Técnicas de Ejecución y Rescate Legacy

* **Ingesta Pasiva (Cero Modificaciones) / Passive Ingestion (Zero-Touch):** Primera fase de análisis de sistemas existentes donde la IA opera en modo de solo lectura estricto, mapeando entradas, salidas, dependencias y contratos implícitos sin alterar un solo byte del código original.


* **Arnés de Caracterización (Maestro Dorado) / Characterization Test Harness (Golden Master):** Batería de pruebas de caja negra construida en un directorio aislado (`tests/characterization/`) que congela y valida las salidas exactas del sistema legacy intacto (incluso comportamientos accidentales tolerados) antes de cualquier intervención.


* **Ejecución en Sombra / Shadow Run (Shadow Execution):** Técnica de validación en la que el nuevo código refactorizado y el módulo original se ejecutan de manera concurrente con las mismas entradas para certificar paridad matemática de salida bit a bit.


* **Patrón Estrangulador / Strangler Fig Pattern:** Estrategia de modernización gradual que sustituye componentes monolíticos legacy por nuevos módulos desacoplados de forma incremental, hasta retirar el código antiguo sin generar caídas operativas.


* **Equilibrios Accidentales / Accidental Balances:** Comportamientos emergentes, código contradictorio o lógica redundante en sistemas legacy que mantienen el sistema en producción funcionando por orden de evaluación y que no deben ser clasificados como fallos sin verificación forense previa.


* **Radio de Impacto / Blast Radius Containment:** Delimitación del alcance máximo de archivos o componentes permitidos durante una reparación crítica o remediación de emergencia, evitando fallos colaterales en cascada.


* **Capa Anti-Corrupción (Adaptador) / Anti-Corruption Layer (Adapter Pattern):** Aislamiento de una dependencia externa o SDK con cambios disruptivos (*breaking changes*) detrás de un puerto o interfaz interna, garantizando que las incompatibilidades no contaminen la lógica de negocio central.



---

### 5. Modos de Operación y Plataforma

* **Modo Greenfield / Greenfield Mode (Modo 1):** Protocolo aplicable al desarrollo de módulos, servicios o aplicaciones desde cero bajo perímetros acotados, diseño contractual previo y generación de código de mínima huella.


* **Modo In-Flight / In-Flight Mode (Modo 2):** Protocolo para integrar nuevas características o componentes en sistemas activos sin mutar los contratos existentes ni alterar la estabilidad del código base.


* **Modo Hotfix & Recuperación de Incidentes / Hotfix & Incident Recovery Mode (Modo 3):** Procedimiento de emergencia en producción enfocado en la contención del radio de impacto, diagnóstico de causa raíz y aplicación de un parche quirúrgico atómico con test de regresión.


* **Modo Mantenimiento Moderno / Modern Maintenance & Upgrades (Modo 4):** Protocolo para migrar versiones mayores de SDKs o APIs externas encapsulando los cambios disruptivos mediante adaptadores.


* **Modo Rescate Legacy / Legacy Rescue Mode (Modo 5):** Metodología en 5 fases (Ingesta Pasiva, Reporte Forense, Arnés Golden Master, Shadow Run y Strangler Fig) para intervenir archivos monolíticos sin pruebas.


* **Modo Auditoría y Blindaje / Audit & Hardening Mode (Modo 6):** Auditoría forense orientada a detectar contención de hilos, puertos expuestos, fugas de memoria y consumo parásito de batería o CPU.


* **Capa Camaleónica / Chameleon Layer:** Matriz de adaptación que ajusta automáticamente las directivas y restricciones técnicas según el stack y la plataforma anfitriona (Android, iOS/Swift, Windows Desktop, Híbrido o Web/Backend).


* **Hilo Principal Sagrado / Sacred Main Thread (UI Thread / Event Loop):** Cláusula que prohíbe terminantemente ejecutar operaciones síncronas de I/O, criptografía pesada o transformaciones masivas de datos en el hilo principal de la interfaz gráfica o en el bucle de eventos.



---

### 6. Matriz de Traducción de Términos Clave

| Término (Español) | Term (English) | Contexto de Aplicación en ZNVE |
| --- | --- | --- |
| **Contrato Determinista** | Deterministic Contract | Interfaz o esquema inmutable obligatorio antes de generar código.

 |
| **Objeto de Transferencia de Datos** | Data Transfer Object (DTO) | Frontera de datos fuertemente tipada.

 |
| **Persistencia Agnóstica** | Data Store Agnostic Persistence | Independencia tecnológica de la base de datos (SQL, NoSQL, Key-Value).

 |
| **Lenguaje de Consulta Estructurado** | Structured Query Language (SQL) | Consultas relacionales con proyecciones explícitas e índices.

 |
| **Barrera Anti-Sobrepeso** | Anti-Bloat Fence | Veto a dependencias de terceros si el SDK nativo resuelve la tarea.

 |
| **Arnés de Caracterización** | Characterization Test Harness | Pruebas de caja negra aisladas para congelar código legacy.

 |
| **Ejecución en Sombra** | Shadow Run | Comparación paralela de salidas entre sistema antiguo y nuevo.

 |
| **Ingesta Pasiva** | Passive Ingestion (Zero-Touch) | Lectura forense en modo solo lectura de código preexistente.

 |
| **Radio de Impacto** | Blast Radius | Frontera física restringida para remediación de incidentes.

 |
| **Capa Camaleónica** | Chameleon Layer | Adaptación de restricciones a Android, iOS, Windows, Web o Híbrido.

 |
| **Observabilidad Silenciosa** | Zero-Noise Observability | Emisión de logs y alertas exclusivamente ante fallos o anomalías.

 |
