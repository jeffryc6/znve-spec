# GREENFIELD STARTER: ZERO-NOISE VIBE ENGINEERING (ZNVE)
**Plantilla de Inicio Rápido para Proyectos Nuevos (Día 0)**
*Versión: 2.2.0 | Estándar: Spec-Driven Agentic Architecture*

---

## 🎯 PROPÓSITO
Esta plantilla proporciona la estructura mínima inviolable y el conjunto de comandos necesarios para **iniciar un proyecto nuevo con el pie derecho**. Elimina el "bucle de muerte de la IA" (*AI agentic drift*), previene la inyección de dependencias parásitas y asegura que el desarrollo avance con contratos deterministas desde la primera línea de código.

---

## 📂 ESTRUCTURA MÍNIMA DEL PROYECTO (SCRUM / REPO LAYOUT)

```text
my-new-project/
├── .cursorrules                       <-- Directiva agéntica local para Cursor / Windsurf / Roo Code
├── ZNVE_PROTOCOL.md                   <-- Protocolo operativo universal (6 Modos)
├── contracts/                         <-- FRONTERA DE DATOS (Contratos inmutables)
│   ├── index.ts                       <-- Exportación de DTOs e Interfaces
│   └── schemas/                       <-- Esquemas de validación (Zod / TypeBox / Pydantic)
├── src/                               <-- CÓDIGO QUIRÚRGICO DE IMPLEMENTACIÓN
│   └── ...                            <-- Archivos objetivo (TARGET_FILE)
├── tests/                             <-- BATERÍA DE VERIFICACIÓN ATÓMICA
│   └── unit/                          <-- Pruebas de contrato y no-regresión
└── README.md                          <-- Documentación y comandos de arranque
```

---

## 🚀 FLUJO DE INICIO RÁPIDO EN 4 PASOS (GREENFIELD WORKFLOW)

```
┌─────────────────────────────────────────────────────────────┐
│ PASO 1: INSTALACIÓN DE BARANDILLAS (.cursorrules)          │
│        --> Copiar .cursorrules en la raíz del proyecto.     │
├─────────────────────────────────────────────────────────────┤
│ PASO 2: ISLA DE ALCANCE (ANTI-BLOAT FENCE)                  │
│        --> Delimitar qué resuelve el MVP y vetar paquetes.  │
├─────────────────────────────────────────────────────────────┤
│ PASO 3: CONTRATO PRIMERO (/znve-contract)                   │
│        --> Diseñar DTOs/Interfaces en contracts/ antes      │
│            de generar código de negocio.                    │
├─────────────────────────────────────────────────────────────┤
│ PASO 4: EJECUCIÓN ATÓMICA (/znve-execute)                  │
│        --> Implementar únicamente en TARGET_FILE y          │
│            ejecutar la prueba de verificación.             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ PASO A PASO: DEL PROMPT AL CÓDIGO PRODUCTIVO

### Paso 1: Configurar las Barandillas Agénticas
Copia el archivo `.cursorrules` (o `protocols/agents/claude-system-skills.md` en tu proyecto de Claude/Windsurf) en la raíz.

### Paso 2: Declarar el Perímetro y el Comando Inicial (GREENFIELD MODO 1)
Envía este prompt a tu asistente de IA (Cursor, Windsurf, Claude, Copilot):

```text
Bajo ZNVE Modo 1 (Greenfield), vamos a iniciar el desarrollo del módulo [NOMBRE_DEL_MÓDULO].

1. Delimita el Anti-Bloat Fence: Prohibido instalar librerías de terceros; usaremos exclusivamente las APIs nativas del runtime/SDK.
2. Ejecuta /znve-contract: Diseña el contrato DTO y la interfaz de datos inmutable en `contracts/[modulo].contract.ts`.
3. No escribas código de implementación todavía. Espera mi aprobación del contrato.
```

### Paso 3: Revisión y Congelación del Contrato
Asegúrate de que la salida del Bloque 1 de la IA contenga:
- DTOs con tipos primitivos o cerrados.
- Tipos de error previstos (`Enum` o uniones discriminadas).
- Ausencia total de campos opcionales no solicitados o abstracciones prematuras.

### Paso 4: Orden de Ejecución Quirúrgica
Una vez aprobado el contrato, ordena la implementación:

```text
Contrato aprobado. Ejecuta /znve-execute para implementar la lógica interna en `src/[modulo]/[servicio].ts`.

RESTRICCIONES STRICTAS:
- TARGET_FILE exclusivo: `src/[modulo]/[servicio].ts`.
- Aplica desecho determinista de recursos (finally / dispose / close).
- Prohibidos bloques try/catch vacíos.
- Incluye el comando de verificación atómica ejecutable.
```

---

## 📋 VERIFICACIÓN DE SALIDA OBLIGATORIA (RESPUESTA EN 4 BLOQUES)

Toda IA trabajando en este proyecto Greenfield DEBE responder con la siguiente estructura:

1. **BLOQUE 1: SYSTEM BLUEPRINT & CONTRATO:** Delimitación de alcance, plataforma objetivo y contrato inmutable (`contracts/`).
2. **BLOQUE 2: RACIONAL DE INGENIERÍA:** 2 viñetas justificando la huella mínima de CPU/RAM y la ausencia de dependencias parásitas.
3. **BLOQUE 3: TAREAS ATÓMICAS DE IMPLEMENTACIÓN:** `TARGET_FILE` único, acción quirúrgica y restricciones aplicadas.
4. **BLOQUE 4: VERIFICACIÓN ATÓMICA:** Comando terminal ejecutable o prueba unitaria (`tests/unit/`) para certificar el funcionamiento.

---

## 🛡️ LISTA DE CHEQUEO DÍA 0 (GREENFIELD CHECKLIST)

- [ ] `.cursorrules` / Directiva agéntica colocada en la raíz.
- [ ] Directorio `contracts/` creado con DTOs/interfaces aprobados.
- [ ] Cero dependencias externas agregadas a `package.json` / `requirements.txt` / `Cargo.toml`.
- [ ] Pruebas unitarias de frontera ejecutadas y en verde.
- [ ] Cero logs de confirmación rutinaria (`"OK"`, `"Success"`) en el código de producción.
