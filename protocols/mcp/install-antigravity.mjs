#!/usr/bin/env node
/**
 * ZNVE MCP — Auto-installer para Google Antigravity (cero dependencias).
 *
 *   node install-antigravity.mjs [--workspace <dir>] [--config <mcp_config.json>]
 *                                [--name <id>] [--skip-build] [--dry-run] [--uninstall]
 *
 * Pasos: npm install -> tsc -> handshake MCP real (initialize + tools/list) -> merge en mcp_config.json (con backup).
 */
import { spawn, spawnSync } from "node:child_process";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(HERE, "../..");
const SERVER_JS = path.join(HERE, "dist", "znve-mcp-server.js");
const SPEC_PATH = path.join(REPO_ROOT, "znve-auto", "master_spec.json");

// Rutas conocidas del config de Antigravity (la primera existente gana; la última es la documentada por defecto).
const CONFIG_CANDIDATES = [
  path.join(os.homedir(), ".gemini", "antigravity-ide", "mcp_config.json"),
  path.join(os.homedir(), ".gemini", "antigravity", "mcp_config.json"),
];

function parseArgs(argv) {
  const opts = { name: "znve-engine", workspace: REPO_ROOT, config: null, skipBuild: false, dryRun: false, uninstall: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => {
      const v = argv[++i];
      if (!v) fail(`Falta el valor de ${a}`);
      return v;
    };
    if (a === "--workspace") opts.workspace = path.resolve(next());
    else if (a === "--config") opts.config = path.resolve(next());
    else if (a === "--name") opts.name = next();
    else if (a === "--skip-build") opts.skipBuild = true;
    else if (a === "--dry-run") opts.dryRun = true;
    else if (a === "--uninstall") opts.uninstall = true;
    else fail(`Argumento desconocido: ${a}`);
  }
  return opts;
}

function log(msg) {
  process.stdout.write(`[znve-install] ${msg}\n`);
}

function fail(msg) {
  process.stderr.write(`[znve-install] ERROR: ${msg}\n`);
  process.exit(1);
}

function toPosix(p) {
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

function resolveConfigPath(explicit) {
  if (explicit) return explicit;
  return CONFIG_CANDIDATES.find((p) => fs.existsSync(p)) ?? CONFIG_CANDIDATES[CONFIG_CANDIDATES.length - 1];
}

function readConfig(configPath) {
  if (!fs.existsSync(configPath)) return { mcpServers: {} };
  const raw = fs.readFileSync(configPath, "utf-8").replace(/^﻿/, "").trim();
  if (!raw) return { mcpServers: {} };
  try {
    const json = JSON.parse(raw);
    json.mcpServers ??= {};
    return json;
  } catch (err) {
    fail(`${configPath} no es JSON válido (${err.message}). Corrígelo a mano; no se sobrescribe.`);
  }
}

function writeConfig(configPath, json, name, dryRun) {
  const body = JSON.stringify(json, null, 2) + "\n";
  if (dryRun) {
    // Solo la entrada propia: el resto del config puede contener tokens de otros servidores.
    const entry = json.mcpServers[name];
    log(`[dry-run] ${configPath} -> mcpServers.${name} = ${entry ? JSON.stringify(entry, null, 2) : "(eliminado)"}`);
    return;
  }
  fs.mkdirSync(path.dirname(configPath), { recursive: true });
  if (fs.existsSync(configPath)) {
    const backup = `${configPath}.bak-${Date.now()}`;
    fs.copyFileSync(configPath, backup);
    log(`Backup: ${backup}`);
  }
  fs.writeFileSync(configPath, body, "utf-8");
  log(`Config actualizado: ${configPath}`);
}

// Handshake MCP real por stdio: prueba lo mismo que hará Antigravity al arrancar el servidor.
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

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const configPath = resolveConfigPath(opts.config);

  if (opts.uninstall) {
    const json = readConfig(configPath);
    if (!json.mcpServers[opts.name]) return log(`'${opts.name}' no está registrado en ${configPath}. Nada que hacer.`);
    delete json.mcpServers[opts.name];
    writeConfig(configPath, json, opts.name, opts.dryRun);
    return log("Desinstalado. Pulsa 'Refresh' en Manage MCP Servers de Antigravity.");
  }

  const [major] = process.versions.node.split(".").map(Number);
  if (major < 18) fail(`Node >= 18 requerido (actual ${process.versions.node}).`);
  if (!fs.existsSync(opts.workspace)) fail(`El workspace no existe: ${opts.workspace}`);

  if (!opts.skipBuild) {
    run(fs.existsSync(path.join(HERE, "package-lock.json")) ? "npm ci" : "npm install");
    run("npm run build");
  }
  if (!fs.existsSync(SERVER_JS)) fail(`No existe ${SERVER_JS}. Ejecuta sin --skip-build.`);

  log("Verificando handshake MCP (initialize + tools/list)...");
  const tools = await smokeTest(opts.workspace).catch((err) => fail(`Smoke test fallido: ${err.message}`));
  const expected = expectedTools();
  if (JSON.stringify([...tools].sort()) !== JSON.stringify(expected)) {
    fail(`El servidor expone [${tools.join(", ")}] y la especificación declara [${expected.join(", ")}].`);
  }
  log(`OK: ${tools.length} herramientas -> ${tools.join(", ")}`);

  const json = readConfig(configPath);
  json.mcpServers[opts.name] = {
    // Ruta absoluta a node: el IDE no siempre hereda el PATH del shell (nvm, fnm, Volta).
    command: toPosix(process.execPath),
    args: [toPosix(SERVER_JS)],
    env: {
      ZNVE_WORKSPACE: toPosix(opts.workspace),
      NODE_ENV: "production",
    },
  };
  writeConfig(configPath, json, opts.name, opts.dryRun);

  log("Listo. En Antigravity: panel Agent -> menú '...' -> MCP Servers -> Manage MCP Servers -> Refresh.");
}

main();
