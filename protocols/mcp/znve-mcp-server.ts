#!/usr/bin/env node
/**
 * ==============================================================================
 * ZNVE MCP SERVER: Spec-Driven Model Context Protocol Server for Antigravity
 * >>> znve:generated (znve-auto/builder.py desde master_spec.json; no editar a mano)
 * Framework: Zero-Noise Vibe Engineering (ZNVE) v2.3.0
 * Axioma 1: "Inteligencia pesada en el diseño; huella casi nula en la ejecución."
 * Axioma 2: "La IA no inventa arquitectura; ejecuta contratos deterministas."
 * <<< znve:generated
 * ==============================================================================
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import * as fs from "node:fs/promises";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

// Antigravity lanza el proceso con un cwd arbitrario: la raíz del workspace se declara con ZNVE_WORKSPACE.
const WORKSPACE_ROOT = path.resolve(process.env.ZNVE_WORKSPACE || process.cwd());
const SERVER_DIR = path.dirname(fileURLToPath(import.meta.url));

// Fuente única de verdad del manual: relativo al servidor (fuente o dist/) o al workspace como respaldo.
const MANUAL_CANDIDATES = [
  path.resolve(SERVER_DIR, "../COMMANDS.md"),
  path.resolve(SERVER_DIR, "../../COMMANDS.md"),
  path.resolve(WORKSPACE_ROOT, "protocols/COMMANDS.md"),
];

// Encabezados "## " de COMMANDS.md que corresponden a cada tema de znve_help.
const HELP_TOPIC_HEADINGS: Record<string, string> = {
  commands: "SECCIÓN 1",
  mcp_tools: "SECCIÓN 2",
  modes: "SECCIÓN 4",
};

// >>> znve:generated:fallback (znve-auto/builder.py desde master_spec.json; no editar a mano)
const HELP_FALLBACK =
  "[ZNVE_HELP_FALLBACK] protocols/COMMANDS.md no disponible. Comandos ZNVE v2.3.0: /znve-help, /znve-contract, /znve-execute, /znve-triage, /znve-hotfix, /znve-upgrade, /znve-forensic, /znve-harness, /znve-legacy-rescue, /znve-audit.";
// <<< znve:generated:fallback

// >>> znve:generated:tools (znve-auto/builder.py desde master_spec.json; no editar a mano)
const TOOL_DOCS: Record<string, { description: string; params: Record<string, string> }> = {
  "znve_help": {
    "description": "Devuelve el manual `protocols/COMMANDS.md` completo o una sección: `commands`, `mcp_tools` o `modes`. Un `topic` desconocido es un error. Si el manual no existe, devuelve un catálogo corto de respaldo; cualquier otro error se informa.",
    "params": {
      "topic": "`all` (por defecto), `commands`, `mcp_tools` o `modes`."
    }
  },
  "znve_forensic_scan": {
    "description": "Lee un archivo del workspace en modo estrictamente de solo lectura. Rechaza rutas fuera de `ZNVE_WORKSPACE` (también a través de enlaces), directorios, binarios y archivos de más de 1 MiB. Devuelve el contenido intacto y su tamaño en bytes; nunca escribe en disco.",
    "params": {
      "file_path": "Ruta del archivo, relativa a `ZNVE_WORKSPACE` (o absoluta dentro de él)."
    }
  },
  "znve_validate_contract": {
    "description": "Valida que un DTO o interfaz cumpla el Anti-Bloat Fence y la proyección de datos. Rechaza el contrato si detecta `SELECT *` o `.find({})` (sin distinguir mayúsculas ni espacios) o la importación de una librería vetada (`import`, `require`, `from … import` o `using`).",
    "params": {
      "contract_code": "Código de la interfaz, struct o DTO propuesto.",
      "banned_libraries": "Librerías vetadas por el Anti-Bloat Fence."
    }
  },
  "znve_scaffold_harness": {
    "description": "Crea una suite Golden Master en un directorio aislado sin tocar producción. Rechaza directorios fuera de `tests/` o `sandbox/`, nombres de archivo con rutas y cualquier escape del workspace.",
    "params": {
      "harness_directory": "Directorio aislado bajo `tests/` o `sandbox/` en la raíz de `ZNVE_WORKSPACE`.",
      "test_filename": "Nombre del archivo de prueba, sin rutas.",
      "harness_code": "Código de la prueba de caja negra."
    }
  },
  "znve_surgical_write": {
    "description": "Escribe un único `TARGET_FILE` tras aprobar el contrato. Rechaza rutas fuera de `ZNVE_WORKSPACE` o dentro de `.git/` y `node_modules/`, y aborta si un `catch`/`except` silencia el error o si se abren sockets o flujos con `not_applicable`. Escribe de forma atómica (archivo temporal y renombrado).",
    "params": {
      "target_file": "Ruta exacta del único archivo a escribir, dentro de `ZNVE_WORKSPACE`.",
      "code_content": "Contenido que satisface el contrato.",
      "disposal_pattern": "`dispose`, `close`, `finally`, `autocloseable` o `not_applicable`."
    }
  },
  "znve_audit_resources": {
    "description": "Analiza un fragmento de código en busca de antipatrones de hilos, memoria y CPU. Marca `.Result`, `.Wait()` y `.GetAwaiter().GetResult()` (riesgo `HIGH`), `WakeLock.acquire()` (`HIGH`) y busy-waiting sin backoff (`MEDIUM`). `risk_level` es el mayor riesgo encontrado, o `CLEAN`.",
    "params": {
      "code_snippet": "Fragmento de código a evaluar."
    }
  }
};
// <<< znve:generated:tools

// Únicos directorios (primer segmento bajo el workspace) donde znve_scaffold_harness puede escribir.
const HARNESS_ROOTS = ["tests", "sandbox"];
// Directorios en los que ninguna herramienta escribe, a cualquier profundidad.
const PROTECTED_DIRS = [".git", "node_modules"];
const DISPOSAL_PATTERNS = ["dispose", "close", "finally", "autocloseable", "not_applicable"];
const HELP_TOPICS = ["all", "commands", "mcp_tools", "modes"];
const MAX_SCAN_BYTES = 1024 * 1024;

type Args = Record<string, unknown>;

// La versión del servidor vive solo en package.json (junto al .ts o un nivel por encima de dist/).
function readServerVersion(): string {
  for (const candidate of [path.join(SERVER_DIR, "package.json"), path.join(SERVER_DIR, "..", "package.json")]) {
    try {
      const pkg = JSON.parse(readFileSync(candidate, "utf-8"));
      if (pkg.name === "znve-mcp-server") return String(pkg.version);
    } catch (err: any) {
      if (err.code !== "ENOENT") throw err;
    }
  }
  process.stderr.write("[znve-mcp] package.json no encontrado: versión del servidor desconocida.\n");
  return "0.0.0-unknown";
}

function requireString(args: Args, key: string): string {
  const value = args[key];
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`Falta el argumento '${key}' (texto no vacío).`);
  }
  return value;
}

function requireEnum(args: Args, key: string, allowed: string[], fallback?: string): string {
  const value = args[key] ?? fallback;
  if (typeof value !== "string" || !allowed.includes(value)) {
    throw new Error(`'${key}' debe ser uno de: ${allowed.join(", ")}.`);
  }
  return value;
}

function optionalStringList(args: Args, key: string): string[] {
  const value = args[key];
  if (value === undefined) return [];
  if (!Array.isArray(value) || value.some((v) => typeof v !== "string" || v.trim() === "")) {
    throw new Error(`'${key}' debe ser una lista de textos no vacíos.`);
  }
  return value.map((v: string) => v.trim());
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\/]/g, "\\$&");
}

// ---------------------------------------------------------------------------
// Rutas
// ---------------------------------------------------------------------------

function isInside(root: string, target: string): boolean {
  const rel = path.relative(root, target);
  return rel === "" || (rel !== ".." && !rel.startsWith(`..${path.sep}`) && !path.isAbsolute(rel));
}

// Ruta real del ancestro existente más profundo más el resto sin crear: detecta escapes por symlink o junction.
async function realpathOfExisting(target: string): Promise<string> {
  let existing = target;
  const tail: string[] = [];
  for (;;) {
    try {
      return path.join(await fs.realpath(existing), ...tail);
    } catch (err: any) {
      if (err.code !== "ENOENT") throw err;
      const parent = path.dirname(existing);
      if (parent === existing) return target;
      tail.unshift(path.basename(existing));
      existing = parent;
    }
  }
}

interface WorkspacePath {
  absolute: string;
  /** Relativa al workspace tal como se pidió. */
  relative: string;
  /** Relativa al workspace tras resolver enlaces. */
  realRelative: string;
}

/** Resuelve p contra ZNVE_WORKSPACE y rechaza todo lo que quede fuera, también a través de enlaces. */
async function resolveInWorkspace(p: string): Promise<WorkspacePath> {
  const absolute = path.resolve(WORKSPACE_ROOT, p);
  const outside = new Error(`'${p}' queda fuera de ZNVE_WORKSPACE.`);
  if (!isInside(WORKSPACE_ROOT, absolute)) throw outside;
  const realRoot = await realpathOfExisting(WORKSPACE_ROOT);
  const real = await realpathOfExisting(absolute);
  if (!isInside(realRoot, real)) throw outside;
  return { absolute, relative: path.relative(WORKSPACE_ROOT, absolute), realRelative: path.relative(realRoot, real) };
}

function assertWritable(target: WorkspacePath): void {
  for (const rel of [target.relative, target.realRelative]) {
    const blocked = rel.split(path.sep).find((part) => PROTECTED_DIRS.includes(part.toLowerCase()));
    if (blocked) throw new Error(`Escritura denegada dentro de '${blocked}/': '${target.relative}'.`);
  }
}

// Temporal en el mismo directorio + rename: el TARGET_FILE nunca queda a medio escribir.
async function atomicWrite(file: string, content: string): Promise<void> {
  await fs.mkdir(path.dirname(file), { recursive: true });
  const temp = path.join(path.dirname(file), `.${path.basename(file)}.${randomUUID()}.znve-tmp`);
  try {
    await fs.writeFile(temp, content, { encoding: "utf-8", flag: "wx" });
    const mode = await fs.stat(file).then(
      (st) => st.mode,
      (err) => {
        if (err.code === "ENOENT") return undefined;
        throw err;
      }
    );
    if (mode !== undefined) await fs.chmod(temp, mode);
    await fs.rename(temp, file);
  } catch (err) {
    await fs.rm(temp, { force: true });
    throw err;
  }
}

// ---------------------------------------------------------------------------
// Detectores
// ---------------------------------------------------------------------------

// catch vacío o con solo comentarios (con o sin binding) y .catch(() => {}) de promesas.
const SILENT_CATCH = [
  /\bcatch\s*(?:\([^)]*\))?\s*\{(?:\s|\/\/[^\n]*|\/\*[\s\S]*?\*\/)*\}/,
  /\.catch\(\s*(?:\(\s*\w*\s*\)|\w+)\s*=>\s*\{(?:\s|\/\/[^\n]*|\/\*[\s\S]*?\*\/)*\}\s*\)/,
];

function indentOf(line: string): number {
  return line.length - line.trimStart().length;
}

/** true si algún catch/except solo descarta el error. */
function silencesErrors(code: string): boolean {
  if (SILENT_CATCH.some((re) => re.test(code))) return true;
  const lines = code.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const match = /^([ \t]*)except\b[^:]*:(.*)$/.exec(lines[i]);
    if (!match) continue;
    const inline = match[2].replace(/#.*$/, "").trim();
    const body = inline ? [inline] : [];
    for (let j = i + 1; !inline && j < lines.length; j++) {
      const statement = lines[j].replace(/#.*$/, "");
      if (!statement.trim()) continue;
      if (indentOf(lines[j]) <= match[1].length) break;
      body.push(statement.trim());
    }
    if (body.length > 0 && body.every((s) => s === "pass" || s === "...")) return true;
  }
  return false;
}

/** true si el código importa la librería (JS/TS, Python, C#). Coincidencia por módulo, no por substring. */
function importsLibrary(code: string, lib: string): boolean {
  const name = escapeRegExp(lib);
  const sub = "(?:[/.][\\w.\\-/]*)?";
  return [
    new RegExp(`\\bimport\\s+(?:[^'";]*?\\bfrom\\s*)?['"]${name}${sub}['"]`, "i"),
    new RegExp(`\\b(?:require|import)\\s*\\(\\s*['"]${name}${sub}['"]\\s*\\)`, "i"),
    new RegExp(`^\\s*import\\s+${name}(?:\\.[\\w.]*)?\\s*(?:[,;]|\\bas\\b|$)`, "im"),
    new RegExp(`^\\s*from\\s+${name}(?:\\.[\\w.]*)?\\s+import\\b`, "im"),
    new RegExp(`^\\s*using\\s+(?:static\\s+)?${name}(?:\\.[\\w.]*)?\\s*;`, "im"),
  ].some((re) => re.test(code));
}

const BLIND_QUERY = [/\bselect\s+\*/i, /\.find\(\s*\{\s*\}\s*\)/];

type Risk = "HIGH" | "MEDIUM";
const AUDIT_RULES: { risk: Risk; test: (code: string) => boolean; finding: string }[] = [
  {
    risk: "HIGH",
    test: (code) => /\.Result\b(?!\s*\()|\.Wait\s*\(|\.GetAwaiter\(\)\s*\.GetResult\(\)/.test(code),
    finding: "Antipatrón Desktop: Sincronización bloqueante sobre async Task (riesgo de deadlock).",
  },
  {
    risk: "HIGH",
    test: (code) => /wakelock\w*\.acquire\s*\(/i.test(code),
    finding: "Antipatrón Android: Retención de CPU no administrada (drenaje de batería).",
  },
  {
    risk: "MEDIUM",
    test: (code) =>
      /\bThread\.sleep\b|while\s*\(\s*true\s*\)\s*\{\s*\}|while\s+True\s*:\s*pass\b/.test(code) ||
      (/\bsetTimeout\b/.test(code) && /\bwhile\b/.test(code)),
    finding: "Riesgo de bloqueo o busy-waiting sin jitter ni backoff.",
  },
];

// ---------------------------------------------------------------------------
// Manual
// ---------------------------------------------------------------------------

async function readManual(): Promise<string | null> {
  for (const candidate of MANUAL_CANDIDATES) {
    try {
      return await fs.readFile(candidate, "utf-8");
    } catch (err: any) {
      if (err.code !== "ENOENT") throw err;
    }
  }
  return null;
}

// Los errores de fs incluyen rutas absolutas del host: se sustituyen por ZNVE_WORKSPACE.
async function publicMessage(err: any): Promise<string> {
  const realRoot = await realpathOfExisting(WORKSPACE_ROOT).catch(() => WORKSPACE_ROOT);
  let message = String(err?.message ?? err);
  for (const root of [WORKSPACE_ROOT, realRoot].sort((a, b) => b.length - a.length)) {
    message = message.split(root).join("ZNVE_WORKSPACE");
  }
  return message;
}

// ---------------------------------------------------------------------------
// Servidor
// ---------------------------------------------------------------------------

const server = new Server(
  {
    name: "znve-mcp-core",
    version: readServerVersion(),
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const doc = (tool: string) => TOOL_DOCS[tool]?.description ?? "";
const param = (tool: string, name: string) => TOOL_DOCS[tool]?.params[name] ?? "";
const READ_ONLY = { readOnlyHint: true, openWorldHint: false };
const WRITES_FILES = { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: false };

// Definición de herramientas operativas ZNVE (los textos salen de master_spec.json vía TOOL_DOCS)
const TOOLS: Tool[] = [
  {
    name: "znve_forensic_scan",
    description: doc("znve_forensic_scan"),
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      properties: {
        file_path: { type: "string", description: param("znve_forensic_scan", "file_path") },
      },
      required: ["file_path"],
    },
  },
  {
    name: "znve_validate_contract",
    description: doc("znve_validate_contract"),
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      properties: {
        contract_code: { type: "string", description: param("znve_validate_contract", "contract_code") },
        banned_libraries: {
          type: "array",
          items: { type: "string" },
          description: param("znve_validate_contract", "banned_libraries"),
        },
      },
      required: ["contract_code"],
    },
  },
  {
    name: "znve_scaffold_harness",
    description: doc("znve_scaffold_harness"),
    annotations: WRITES_FILES,
    inputSchema: {
      type: "object",
      properties: {
        harness_directory: { type: "string", description: param("znve_scaffold_harness", "harness_directory") },
        test_filename: { type: "string", description: param("znve_scaffold_harness", "test_filename") },
        harness_code: { type: "string", description: param("znve_scaffold_harness", "harness_code") },
      },
      required: ["harness_directory", "test_filename", "harness_code"],
    },
  },
  {
    name: "znve_surgical_write",
    description: doc("znve_surgical_write"),
    annotations: WRITES_FILES,
    inputSchema: {
      type: "object",
      properties: {
        target_file: { type: "string", description: param("znve_surgical_write", "target_file") },
        code_content: { type: "string", description: param("znve_surgical_write", "code_content") },
        disposal_pattern: {
          type: "string",
          enum: DISPOSAL_PATTERNS,
          description: param("znve_surgical_write", "disposal_pattern"),
        },
      },
      required: ["target_file", "code_content", "disposal_pattern"],
    },
  },
  {
    name: "znve_audit_resources",
    description: doc("znve_audit_resources"),
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      properties: {
        code_snippet: { type: "string", description: param("znve_audit_resources", "code_snippet") },
      },
      required: ["code_snippet"],
    },
  },
  {
    name: "znve_help",
    description: doc("znve_help"),
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      properties: {
        topic: { type: "string", enum: HELP_TOPICS, description: param("znve_help", "topic") },
      },
    },
  },
];

// Listar herramientas disponibles
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Enrutador de ejecución determinista
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name } = request.params;
  const args: Args = request.params.arguments ?? {};

  try {
    switch (name) {
      case "znve_forensic_scan": {
        const filePath = requireString(args, "file_path");
        const target = await resolveInWorkspace(filePath);
        const stat = await fs.stat(target.absolute).catch((err) => {
          throw err.code === "ENOENT" ? new Error(`No existe '${filePath}' en ZNVE_WORKSPACE.`) : err;
        });
        if (!stat.isFile()) throw new Error(`'${filePath}' no es un archivo.`);
        if (stat.size > MAX_SCAN_BYTES) {
          throw new Error(`'${filePath}' pesa ${stat.size} bytes y supera el tope de ${MAX_SCAN_BYTES} bytes.`);
        }
        const buffer = await fs.readFile(target.absolute);
        if (buffer.includes(0)) throw new Error(`'${filePath}' es binario; znve_forensic_scan solo lee texto.`);

        return {
          content: [
            {
              type: "text",
              text: `[ZNVE_FORENSIC_READONLY_SNAPSHOT]\nARCHIVO: ${filePath}\nTAMAÑO: ${buffer.length} bytes\n\nCONTENIDO INTACTO:\n${buffer.toString("utf-8")}`,
            },
          ],
        };
      }

      case "znve_validate_contract": {
        const contract = requireString(args, "contract_code");
        const banned = optionalStringList(args, "banned_libraries");

        const detectedViolations: string[] = [];

        if (BLIND_QUERY.some((re) => re.test(contract))) {
          detectedViolations.push(
            "Violación Pilar 4: Consultas ciegas no indexadas ('SELECT *' o '.find({})' detectadas)."
          );
        }

        for (const lib of banned) {
          if (importsLibrary(contract, lib)) {
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
        const harnessDir = requireString(args, "harness_directory");
        const testFilename = requireString(args, "test_filename");
        const harnessCode = requireString(args, "harness_code");

        if (testFilename !== path.basename(testFilename) || /[\\/:]/.test(testFilename) || /^\.+$/.test(testFilename)) {
          throw new Error(`'test_filename' debe ser un nombre de archivo sin rutas: '${testFilename}'.`);
        }

        // Se valida la ruta final del archivo, no solo el directorio: un enlace dentro de tests/ tampoco puede escapar.
        const target = await resolveInWorkspace(path.join(harnessDir, testFilename));
        const underRoot = (rel: string) => {
          const parts = rel.split(path.sep);
          return parts.length >= 2 && HARNESS_ROOTS.includes(parts[0].toLowerCase());
        };
        if (!underRoot(target.relative) || !underRoot(target.realRelative)) {
          throw new Error(`El arnés debe ubicarse bajo ${HARNESS_ROOTS.map((r) => `${r}/`).join(" o ")} en la raíz de ZNVE_WORKSPACE.`);
        }
        assertWritable(target);
        await atomicWrite(target.absolute, harnessCode);

        return {
          content: [
            {
              type: "text",
              text: `[ZNVE_HARNESS_CREATED] Arnés Golden Master desplegado en: ${target.relative}. El código original no ha sido modificado.`,
            },
          ],
        };
      }

      case "znve_surgical_write": {
        const targetFile = requireString(args, "target_file");
        const codeContent = requireString(args, "code_content");
        const disposal = requireEnum(args, "disposal_pattern", DISPOSAL_PATTERNS);

        if (silencesErrors(codeContent)) {
          throw new Error(
            "Violación Pilar 5: Detección de bloque catch/except que silencia el error. Prohibido silenciar excepciones."
          );
        }

        if (disposal === "not_applicable" && (codeContent.includes("open(") || codeContent.includes("connect("))) {
          throw new Error(
            "Violación Pilar 3: Se detectó apertura de flujo o socket sin un patrón de desecho explícito."
          );
        }

        const target = await resolveInWorkspace(targetFile);
        assertWritable(target);
        await atomicWrite(target.absolute, codeContent);

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
        const snippet = requireString(args, "code_snippet");
        const hits = AUDIT_RULES.filter((rule) => rule.test(snippet));
        const risk = hits.some((h) => h.risk === "HIGH") ? "HIGH" : hits.length > 0 ? "MEDIUM" : "CLEAN";

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  findings_count: hits.length,
                  risk_level: risk,
                  findings: hits.map((h) => h.finding),
                },
                null,
                2
              ),
            },
          ],
        };
      }

      case "znve_help": {
        const topic = requireEnum(args, "topic", HELP_TOPICS, "all");
        const manual = await readManual();
        if (manual === null) {
          return { content: [{ type: "text", text: HELP_FALLBACK }] };
        }

        let text = manual;
        const heading = HELP_TOPIC_HEADINGS[topic];
        if (heading) {
          // Se compara solo la línea del encabezado, no el cuerpo de la sección.
          const section = manual
            .split(/^(?=## )/m)
            .find((s) => s.startsWith("## ") && s.split("\n", 1)[0].includes(heading));
          if (!section) throw new Error(`protocols/COMMANDS.md no contiene la sección '${heading}' del tema '${topic}'.`);
          text = section;
        }

        return { content: [{ type: "text", text }] };
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
          text: `[ZNVE_MCP_ERROR] ${await publicMessage(err)}`,
        },
      ],
    };
  }
});

// Arranque por stdio
async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // stdout está reservado para JSON-RPC: todo diagnóstico va a stderr.
  process.stderr.write(`[znve-mcp] listo (stdio). Workspace: ${WORKSPACE_ROOT}\n`);
}

run().catch((error) => {
  process.stderr.write(`Fallo de inicio en servidor MCP ZNVE: ${error.message}\n`);
  process.exit(1);
});
