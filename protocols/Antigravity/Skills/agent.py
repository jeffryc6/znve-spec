"""
Ejemplo mínimo: agente del Antigravity SDK con la skill ZNVE.

Requisitos: pip install google-antigravity
Uso (desde esta carpeta): python agent.py

Importa el módulo canónico znve_skill.py de esta carpeta. En un proyecto donde se
ejecutó Auto_Installer.py, la misma skill queda en .antigravity/skills/znve/.
"""

from google.antigravity import Agent

from znve_skill import ZNVE_VERSION, get_znve_skill

# 1. Skill ZNVE (instrucción de sistema + 6 herramientas)
znve_skill = get_znve_skill()

# 2. Agente con la skill incorporada
agent = Agent(
    model="gemini-2.5-pro",  # o el modelo configurado en tu entorno Antigravity
    skills=[znve_skill],
)

# 3. Comprobación: debe devolver el catálogo de ZNVE
if __name__ == "__main__":
    response = agent.run("/znve-help")
    print(f"ZNVE v{ZNVE_VERSION}\n{response.text}")
