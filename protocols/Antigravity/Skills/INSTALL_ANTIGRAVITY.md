# Instalación del Skill ZNVE en Antigravity

<!-- Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano. -->

Este documento explica cómo integrar el Skill **Zero-Noise Vibe Engineering (ZNVE v2.3.0)** en Google Antigravity, por proyecto o de forma global, y cómo usarlo desde el Antigravity SDK.

Referencia: [Agent Skills en Antigravity](https://antigravity.google/docs/skills).

---

## 1. Requisitos previos

- Python 3.10 o superior para los instaladores.
- Solo para agentes programáticos, el SDK en el entorno virtual activo:

```bash
pip install google-antigravity
```

## 2. Instalación en un proyecto

Desde la raíz del proyecto:

```bash
python <ruta>/znve-spec/protocols/Antigravity/Skills/Auto_Installer.py
```

Crea la skill en la ruta de workspace que lee Antigravity (IDE, Antigravity 2.0 y CLI):

```text
<proyecto>/.agents/skills/znve/
├── SKILL.md                 <-- skill znve v2.3.0
└── scripts/znve_skill.py    <-- instrucción de sistema y 6 herramientas para el SDK
```

Si el proyecto tiene una instalación antigua en `.antigravity/skills/znve/`, la elimina y retira los registros `znve` y `zero_noise_vibe_engineering` de `.antigravity/antigravity.json`, conservando el resto del archivo.

## 3. Instalación global

```bash
python <ruta>/znve-spec/protocols/Antigravity/Skills/install_znve_global.py
```

- Copia `SKILL.md` a `~/.gemini/config/skills/znve/`, la ruta global de Antigravity IDE y Antigravity 2.0.
- Elimina la copia antigua de `~/.gemini/antigravity/skills/znve/` (ruta legacy) para que no compita con la nueva. Si esa carpeta contiene otros archivos, avisa y no la toca.
- Registra el workflow `/znve-help` en `~/.gemini/config/global_workflows/`.
- Escribe la regla ZNVE en `~/.gemini/GEMINI.md`. Si ya hay una de una versión anterior, la sustituye en lugar de añadir otra.

Si una skill de proyecto y una global se llaman igual, revisa cuál está activa con `/skills`.

## 4. Uso desde el Antigravity SDK

`znve_skill.py` expone la configuración lista para el SDK: la instrucción de sistema de ZNVE y las 6 funciones como herramientas.

```python
import asyncio
from google.antigravity import Agent
from znve_skill import get_znve_config

async def main():
    async with Agent(get_znve_config()) as agent:
        response = await agent.chat("/znve-help")
        print(await response.text())

asyncio.run(main())
```

`get_znve_config(**kwargs)` pasa los argumentos extra (`api_key`, `mcp_servers`, `policies`...) a `LocalAgentConfig`. Ejemplo ejecutable: `agent.py`. Para añadir el servidor MCP de ZNVE, consulta `protocols/mcp/ANTIGRAVITY_INSTALL.md`.

## 5. Verificación

1. Recarga la ventana de Antigravity.
2. Escribe `/skills`: debe aparecer `znve` (no `zero-noise-vibe-engineering`).
3. Escribe `/znve-help`: debe imprimir el catálogo de ZNVE v2.3.0.

## 6. Mantenimiento

`SKILL.md`, este documento, el bloque de constantes de `znve_skill.py` y la copia de ejemplo en `.agents/skills/znve/` los genera `znve-auto/builder.py` desde `znve-auto/master_spec.json`. Para cambiar un comando o la versión, edita la especificación y ejecuta:

```bash
python znve-auto/builder.py
```
