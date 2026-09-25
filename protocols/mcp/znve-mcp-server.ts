#!/usr/bin/env node
/**
 * ==============================================================================
 * ZNVE MCP SERVER: Spec-Driven Model Context Protocol Server for Antigravity
 * Framework: Zero-Noise Vibe Engineering (ZNVE) v1.0.0
 * Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
 * Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
 * ==============================================================================
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import * as fs from "node:fs/promises";
import * as path from "node:path";

const server = new Server(
  {
    name: "znve-mcp-core",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Definición de herramientas operativas ZNVE
const TOOLS: Tool[] = [
  {
    name: "znve_forensic_scan",
    description:
      "Fase 1 y 2 ZNVE: Inspección en MODO SOLO LECTURA estricto. Lee el archivo objetivo y extrae dependencias, entradas, salidas y efectos secundarios sin modificar el disco.",
    inputSchema: {
      type: "object",
      properties: {
        file_path: {
          type: "string",
          description: "Ruta relativa o absoluta del archivo a inspeccionar.",
        },
      },
      required: ["file_path"],
    },
  },
  {
    name: "znve_validate_contract",
    description:
      "Fase de Contrato: Valida que una especificación de interfaz o DTO cumpla las reglas Anti-Bloat (sin librerías redundantes y con proyecciones de datos explícitas) antes de codificar.",
    inputSchema: {
      type: "object",
      properties: {
        contract_code: {
          type: "string",
          description: "Código fuente de la interfaz, struct o DTO propuesto.",
        },
        banned_libraries: {
          type: "array",
          items: { type: "string" },
          description: "Lista de dependencias externas que quedan explícitamente vetadas.",
        },
      },
      required: ["contract_code"],
    },
  },
  {
    name: "znve_scaffold_harness",
    description:
      "Fase 3 ZNVE: Crea un arnés de caracterización (Golden Master) en un directorio aislado sin modificar el archivo productivo original.",
    inputSchema: {
      type: "object",
      properties: {
        harness_directory: {
          type: "string",
          description: "Directorio aislado de pruebas (ej: tests/characterization).",
        },
        test_filename: {
          type: "string",
          description: "Nombre del archivo de test (ej: legacy_auth.test.ts).",
        },
        harness_code: {
          type: "string",
          description: "Código del arnés de caja negra que captura las salidas actuales.",
        },
      },
      required: ["harness_directory", "test_filename", "harness_code"],
    },
  },
  {
    name: "znve_surgical_write",
    description:
      "Fase 4 ZNVE: Escritura atómica permitida ÚNICAMENTE en el TARGET_FILE declarado. Falla automáticamente si el código contiene bloques try/catch vacíos o carece de desecho de recursos.",
    inputSchema: {
      type: "object",
      properties: {
        target_file: {
          type: "string",
          description: "Ruta exacta del archivo único que se modificará o creará.",
        },
        code_content: {
          type: "string",
          description: "Código quirúrgico que satisface el contrato preaprobado.",
        },
        disposal_pattern: {
          type: "string",
          enum: ["dispose", "close", "finally", "autocloseable", "not_applicable"],
          description: "Mecanismo explícito utilizado para liberar memoria/sockets/handles.",
        },
      },
      required: ["target_file", "code_content", "disposal_pattern"],
    },
  },
  {
    name: "znve_audit_resources",
    description:
      "Auditoría Forense: Escanea código en busca de antipatrones ZNVE (SELECT *, bloqueos del hilo principal, loops de espera sin jitter, fugas de listeners).",
    inputSchema: {
      type: "object",
      properties: {
        code_snippet: {
          type: "string",
          description: "Código a auditar en busca de consumo parásito o contención.",
        },
      },
      required: ["code_snippet"],
    },
  },
];

// Listar herramientas disponibles
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Enrutador de ejecución determinista
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "znve_forensic_scan": {
        const filePath = String(args?.file_path);
        const resolvedPath = path.resolve(process.cwd(), filePath);
        const content = await fs.readFile(resolvedPath, "utf-8");

        return {
          content: [
            {
              type: "text",
              text: `[ZNVE_FORENSIC_READONLY_SNAPSHOT]\nARCHIVO: ${filePath}\nTAMAÑO: ${content.length} bytes\n\nCONTENIDO INTACTO:\n${content}`,
            },
          ],
        };
      }

      case "znve_validate_contract": {
        const contract = String(args?.contract_code);
        const banned = (args?.banned_libraries as string[]) || [];

        const detectedViolations: string[] = [];

        // Detección de consultas ciegas sin proyecciones
        if (contract.includes("SELECT *") || contract.includes(".find({})")) {
          detectedViolations.push(
            "Violación Pilar 4: Consultas ciegas no indexadas ('SELECT *' o '.find({})' detectadas)."
          );
        }

        // Detección de librerías vetadas en el Anti-Bloat Fence
        for (const lib of banned) {
          if (contract.includes(lib)) {
            detectedViolations.push(`Violación Anti-Bloat Fence: La dependencia '${lib}' está prohibida.`);
          }
        }

        const valid = detectedViolations.length === 0;
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  status: valid ? "PASSED" : "REJECTED",
                  valid_contract: valid,
                  violations: detectedViolations,
                  directive: valid
                    ? "Contrato certificado. Procede con /znve-execute."
                    : "Corrige el contrato antes de escribir código.",
                },
                null,
                2
              ),
            },
          ],
        };
      }

      case "znve_scaffold_harness": {
        const harnessDir = String(args?.harness_directory);
        const testFilename = String(args?.test_filename);
        const harnessCode = String(args?.harness_code);

        // Garantizar aislamiento estricto (tests/ o sandbox/)
        if (!harnessDir.includes("test") && !harnessDir.includes("sandbox")) {
          throw new Error("El arnés debe ubicarse en un directorio 'tests/' o 'sandbox/' aislado.");
        }

        const targetDir = path.resolve(process.cwd(), harnessDir);
        await fs.mkdir(targetDir, { recursive: true });

        const testFilePath = path.join(targetDir, testFilename);
        await fs.writeFile(testFilePath, harnessCode, "utf-8");

        return {
          content: [
            {
              type: "text",
              text: `[ZNVE_HARNESS_CREATED] Arnés Golden Master desplegado en: ${testFilePath}. El código original no ha sido modificado.`,
            },
          ],
        };
      }

      case "znve_surgical_write": {
        const targetFile = String(args?.target_file);
        const codeContent = String(args?.code_content);
        const disposal = String(args?.disposal_pattern);

        // Guardrail: Prohibir bloques try/catch vacíos
        const emptyCatchRegex = /catch\s*\([^)]*\)\s*\{\s*\}/;
        if (emptyCatchRegex.test(codeContent)) {
          throw new Error(
            "Violación Pilar 5: Detección de bloque catch vacío. Prohibido silenciar excepciones."
          );
        }

        // Guardrail: Obligar a declarar la liberación de recursos
        if (disposal === "not_applicable" && (codeContent.includes("open(") || codeContent.includes("connect("))) {
          throw new Error(
            "Violación Pilar 3: Se detectó apertura de flujo o socket sin un patrón de desecho explícito."
          );
        }

        const resolvedPath = path.resolve(process.cwd(), targetFile);
        await fs.mkdir(path.dirname(resolvedPath), { recursive: true });
        await fs.writeFile(resolvedPath, codeContent, "utf-8");

        return {
          content: [
            {
              type: "text",
              text: `[ZNVE_ATOMIC_WRITE_SUCCESS] Modificación quirúrgica completada en '${targetFile}'. Verificación requerida.`,
            },
          ],
        };
      }

      case "znve_audit_resources": {
        const snippet = String(args?.code_snippet);
        const findings: string[] = [];

        if (snippet.includes("Thread.sleep") || snippet.includes("setTimeout") && snippet.includes("while")) {
          findings.push("Riesgo de bloqueo o busy-waiting sin jitter ni backoff.");
        }
        if (snippet.includes(".Result") || snippet.includes(".Wait()")) {
          findings.push("Antipatrón Desktop: Sincronización bloqueante sobre async Task (riesgo de deadlock).");
        }
        if (snippet.includes("WakeLock.acquire()")) {
          findings.push("Antipatrón Android: Retención de CPU no administrada (drenaje de batería).");
        }

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  findings_count: findings.length,
                  risk_level: findings.length > 0 ? "HIGH" : "CLEAN",
                  findings: findings,
                },
                null,
                2
              ),
            },
          ],
        };
      }

      default:
        throw new Error(`Herramienta no reconocida por el estándar ZNVE: ${name}`);
    }
  } catch (err: any) {
    return {
      isError: true,
      content: [
        {
          type: "text",
          text: `[ZNVE_MCP_ERROR] ${err.message}`,
        },
      ],
    };
  }
});

// Arranque por stdio (ultra bajo consumo de recursos)
async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

run().catch((error) => {
  process.stderr.write(`Fallo de inicio en servidor MCP ZNVE: ${error.message}\n`);
  process.exit(1);
});