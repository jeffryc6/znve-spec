from google.antigravity import Agent
from skills.znve.znve_skill import get_znve_skill

# 1. Obtener la definición de ZNVE Skill
znve_skill = get_znve_skill()

# 2. Instanciar el agente con el skill incorporado
agent = Agent(
    model="gemini-2.5-pro", # O el modelo configurado en tu entorno Antigravity
    skills=[znve_skill]
)

# 3. Ejecución determinista
if __name__ == "__main__":
    response = agent.run("/znve-help")
    print(response.text)