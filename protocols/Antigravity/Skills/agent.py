"""
Ejemplo mínimo: agente del Antigravity SDK con la instrucción de sistema y las 6
herramientas de ZNVE.

Requisitos: pip install google-antigravity
Uso (desde esta carpeta): python agent.py

Importa el módulo canónico znve_skill.py de esta carpeta. En un proyecto donde se
ejecutó Auto_Installer.py, el mismo módulo queda en .agents/skills/znve/scripts/.
La autenticación sigue la del SDK; para pasar la clave a mano:
get_znve_config(api_key="...").
"""

import asyncio

from google.antigravity import Agent

from znve_skill import ZNVE_VERSION, get_znve_config


async def main() -> None:
    async with Agent(get_znve_config()) as agent:
        # Comprobación: debe devolver el catálogo de ZNVE
        response = await agent.chat("/znve-help")
        print(f"ZNVE v{ZNVE_VERSION}\n{await response.text()}")


if __name__ == "__main__":
    asyncio.run(main())
