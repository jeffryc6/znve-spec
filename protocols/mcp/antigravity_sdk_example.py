"""ZNVE MCP + Google Antigravity SDK (Python).

Conecta un agente del Antigravity SDK al servidor ZNVE por stdio, siguiendo
examples/getting_started/mcp_tools.py del repositorio oficial.

Requisitos:
  1. cd protocols/mcp && npm ci && npm run build
  2. pip install google-antigravity
  3. python antigravity_sdk_example.py
"""

import asyncio
import os
import shutil

from google.antigravity import Agent
from google.antigravity import LocalAgentConfig
from google.antigravity import types
from google.antigravity.hooks import policy

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER_JS = os.path.join(HERE, "dist", "znve-mcp-server.js")
WORKSPACE = os.environ.get("ZNVE_WORKSPACE", os.path.abspath(os.path.join(HERE, "..", "..")))


async def main() -> None:
  if not os.path.exists(SERVER_JS):
    raise SystemExit(f"No existe {SERVER_JS}. Ejecuta 'npm ci && npm run build' en {HERE}.")

  znve = types.McpStdioServer(
      name="znve-engine",
      command=shutil.which("node") or "node",
      args=[SERVER_JS],
      env={"ZNVE_WORKSPACE": WORKSPACE},
  )

  # Solo lectura por defecto: las herramientas que escriben en disco quedan bloqueadas.
  policies = [
      policy.deny_all(),
      policy.allow(znve, [
          "znve_help",
          "znve_forensic_scan",
          "znve_validate_contract",
          "znve_audit_resources",
      ]),
      policy.deny(znve, ["znve_surgical_write", "znve_scaffold_harness"]),
  ]

  config = LocalAgentConfig(mcp_servers=[znve], policies=policies)

  async with Agent(config) as agent:
    prompt = "Usa znve_help con topic 'mcp_tools' y resume las herramientas disponibles."
    print(f"User: {prompt}")
    response = await agent.chat(prompt)
    print(f"Agent: {await response.text()}")


if __name__ == "__main__":
  asyncio.run(main())
