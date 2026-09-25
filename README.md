# Zero-Noise Vibe Engineering (ZNVE)

[![Specification Version](https://img.shields.io/badge/spec-v1.0.0-00f2fe.svg)](SPECIFICATION.md)
[![License: CC BY 4.0 & MIT](https://img.shields.io/badge/License-CC_BY_4.0_%2F_MIT-10b981.svg)](LICENSE)
[![Architecture: Contract--First](https://img.shields.io/badge/Architecture-Contract--First-111827.svg)](SPECIFICATION.md)

> **Axioma 1:** *"Inteligencia pesada en el diseño; huella casi nula en la ejecución."*  
> **Axioma 2:** *"La IA no inventa arquitectura; ejecuta contratos deterministas."*

**Zero-Noise Vibe Engineering (ZNVE)** es una especificación técnica de arquitectura y desarrollo asistido por IA (Contract-First Agentic Architecture). Transforma la velocidad conversacional del *vibe coding* en un estándar de ingeniería riguroso, asimétrico y libre de deuda técnica.

---

## 🎯 ¿Por qué ZNVE?

El *vibe coding* convencional delega decisiones de arquitectura en modelos de lenguaje probabilísticos, generando:
- Acumulación masiva de paquetes y dependencias parásitas.
- Bloques `try/catch` vacíos que enmascaran fallos críticos de fondo.
- Fugas de memoria, bloqueos de hilos de interfaz y saturación de bases de datos con consultas sin proyecciones.

Bajo **ZNVE**, el desarrollador asume el rol de **Director de Arquitectura**, definiendo perímetros cerrados y contratos inmutables (DTOs, esquemas tipados, interfaces)[cite: 7]. Los agentes de IA (Claude, Cursor, Copilot, Windsurf) operan como compiladores sintácticos de precisión quirúrgica.

---

## 🏛️ Los 5 Pilares Inmutables

1. **Cero Ruido Operativo (Zero-Noise Operations & UX):** Prohibido el código muerto y las dependencias parásitas. Telemetría por excepción: nunca emitir confirmaciones rutinarias de estado saludable en rutas calientes; solo alertar ante anomalías confirmadas.
2. **Contratos Deterministas (Contract-First AI):** Ninguna IA genera código de producción sin un contrato previo tipado (DTO, interfaces, esquemas de validación).
3. **Eficiencia Asimétrica y Minimalismo:** *"Cerebro en el diseño, reflejo en el dispositivo"*. El hilo principal de UI nunca se bloquea; la persistencia y la memoria se liberan deterministamente.
4. **Dominio de Estado y Persistencia Agnóstica:** Aplicable a motores relacionales (SQL), documentales (NoSQL), clave-valor, series temporales o almacenamiento local. Cero escaneos globales no indexados; proyecciones explícitas obligatorias.
5. **Seguridad Defensiva y Diagnóstico Forense:** Postura Zero-Trust. Validación estricta en frontera, cero secretos en repositorio y erradicación de fallos hasta la causa raíz.

---

## 📂 Estructura del Repositorio

- [`SPECIFICATION.md`](SPECIFICATION.md): La norma técnica formal v1.0.0.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): El proceso formal de RFC para proponer extensiones.
- [`protocols/`](protocols/):
  - `ZNVE_PROTOCOL.md`: Protocolo universal aplicable a proyectos nuevos y modernización.
  - `ZNVE_LEGACY_PROTOCOL.md`: Protocolo de 5 fases para rescatar sistemas legacy sin riesgo en producción.
  - `agents/`: System prompts y directivas listas para Claude Projects, Cursor (`.cursorrules`), Windsurf y Copilot.
- [`case-studies/`](case-studies/):
  - `01-anti-bot-detection-lab/`: Laboratorio de red, TLS (JA3/JA4) y mitigación de fugas de memoria.
  - `02-legacy-monolith-rescue/`: Modernización de un God Object mediante pruebas Golden Master.

---

## 🚀 Inicio Rápido con tu Agente de IA

Copia el contenido de [`protocols/agents/claude-system-skills.md`](protocols/agents/claude-system-skills.md) en las instrucciones de sistema de tu modelo (Claude Project, Cursor Rules o Custom GPT) y activa el modo deseado:

```text
# Para diseñar un nuevo servicio:
/znve-contract Define el contrato de datos para el módulo de facturación offline.

# Para auditar un archivo monolítico peligroso sin tocar el código:
/znve-forensic Analiza este script legacy monolítico en modo SOLO LECTURA.

# Para refactorizar código legacy con pruebas Golden Master:
/znve-legacy-rescue Inicia el proceso de modernización gradual en sombra.
