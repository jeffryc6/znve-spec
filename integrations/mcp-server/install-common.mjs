/**
 * ZNVE MCP — piezas comunes de los instaladores (Antigravity y Codex). Cero dependencias.
 *
 * Compila el servidor, hace un handshake MCP real (initialize + tools/list) y comprueba que las
 * herramientas expuestas coinciden con las de master_spec.json.
 */
import { spawn, spawnSync } from "node:child_process";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

export const HERE = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(HERE, "../..");
export const SERVER_JS = path.join(HERE, "dist", "znve-mcp-server.js");
const SPEC_PATH = path.join(REPO_ROOT, "znve-auto", "master_spec.json");

export function log(msg) {
  process.stdout.write(`[znve-install] ${msg}\n`);
}

export function fail(msg) {
  process.stderr.write(`[znve-install] ERROR: ${msg}\n`);
  process.exit(1);
}

export function toPosix(p) {
  return p.split(path.sep).join("/");
}

function run(command) {
  log(`> ${command}`);
  // Cadena única + shell: npm es npm.cmd en Windows y no se puede lanzar sin shell.
  const res = spawnSync(command, { cwd: HERE, stdio: "inherit", shell: true });
  if (res.status !== 0) fail(`'${command}' terminó con código ${res.status}`);
}

// Las herramientas que debe exponer el servidor salen de la fuente única de verdad.
function expectedTools() {
  try {
    return JSON.parse(fs.readFileSync(SPEC_PATH, "utf-8")).mcp.tools.map((t) => t.name).sort();
  } catch (err) {
    fail(`No se pudo leer la lista de herramientas de ${SPEC_PATH} (${err.message}).`);
  }
}

// Handshake MCP real por stdio: prueba lo mismo que hará el cliente al arrancar el servidor.
function smokeTest(workspace) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [SERVER_JS], {
      cwd: os.homedir(), // cwd arbitrario a propósito, igual que el IDE
      env: { ...process.env, ZNVE_WORKSPACE: workspace },
      stdio: ["pipe", "pipe", "pipe"],
    });
    let buffer = "";
    let stderr = "";
    let done = false;
    const timer = setTimeout(() => finish(new Error(`timeout sin respuesta a tools/list. stderr:\n${stderr}`)), 15000);

    // Solo cuenta el primer desenlace: el 'exit' que provoca child.kill() llega después y se ignora.
    function finish(err, value) {
      if (done) return;
      done = true;
      clearTimeout(timer);
      child.kill();
      err ? reject(err) : resolve(value);
    }
    const send = (msg) => child.stdin.write(JSON.stringify({ jsonrpc: "2.0", ...msg }) + "\n");

    child.on("error", (err) => finish(err));
    child.on("exit", (code) => finish(new Error(`el servidor terminó (código ${code}). stderr:\n${stderr}`)));
    child.stderr.on("data", (d) => (stderr += d));
    child.stdout.on("data", (d) => {
      buffer += d;
      let nl;
      while ((nl = buffer.indexOf("\n")) >= 0) {
        const line = buffer.slice(0, nl).trim();
        buffer = buffer.slice(nl + 1);
        if (!line) continue;
        let msg;
        try {
          msg = JSON.parse(line);
        } catch {
          return finish(new Error(`stdout contaminado con texto no JSON-RPC: ${line}`));
        }
        if (msg.error) {
          return finish(new Error(`el servidor respondió con error a la petición ${msg.id}: ${JSON.stringify(msg.error)}`));
        }
        if (msg.id === 1) {
          send({ method: "notifications/initialized" });
          send({ id: 2, method: "tools/list", params: {} });
        } else if (msg.id === 2) {
          finish(null, (msg.result?.tools ?? []).map((t) => t.name));
        }
      }
    });

    send({
      id: 1,
      method: "initialize",
      params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "znve-installer", version: "1.0.0" } },
    });
  });
}

/** Comprueba Node y el workspace, compila (salvo skipBuild) y verifica el handshake contra la especificación. */
export async function buildAndVerify({ workspace, skipBuild }) {
  const [major] = process.versions.node.split(".").map(Number);
  if (major < 18) fail(`Node >= 18 requerido (actual ${process.versions.node}).`);
  if (!fs.existsSync(workspace)) fail(`El workspace no existe: ${workspace}`);

  if (!skipBuild) {
    run(fs.existsSync(path.join(HERE, "package-lock.json")) ? "npm ci" : "npm install");
    run("npm run build");
  }
  if (!fs.existsSync(SERVER_JS)) fail(`No existe ${SERVER_JS}. Ejecuta sin --skip-build.`);

  log("Verificando handshake MCP (initialize + tools/list)...");
  const tools = await smokeTest(workspace).catch((err) => fail(`Smoke test fallido: ${err.message}`));
  const expected = expectedTools();
  if (JSON.stringify([...tools].sort()) !== JSON.stringify(expected)) {
    fail(`El servidor expone [${tools.join(", ")}] y la especificación declara [${expected.join(", ")}].`);
  }
  log(`OK: ${tools.length} herramientas -> ${tools.join(", ")}`);
}
