#!/usr/bin/env node
/**
 * ZNVE MCP — Auto-installer para Google Antigravity (cero dependencias).
 *
 *   node install-antigravity.mjs [--workspace <dir>] [--config <mcp_config.json>]
 *                                [--name <id>] [--skip-build] [--dry-run] [--uninstall]
 *
 * Pasos: npm install -> tsc -> handshake MCP real (initialize + tools/list) -> merge en mcp_config.json (con backup).
 */
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { REPO_ROOT, SERVER_JS, buildAndVerify, fail, log, toPosix } from "./install-common.mjs";

// Rutas del config de Antigravity. La documentada (https://antigravity.google/docs/mcp) es la global
// ~/.gemini/config/mcp_config.json; las otras dos son de instalaciones anteriores.
// Reglas: (1) si el servidor ya está registrado en alguno, se actualiza ahí mismo (en todos los que lo tengan), para no
// dejar una entrada antigua apuntando a una ruta que ya no existe; (2) si no, el primer config que exista;
// (3) si no hay ninguno, se crea el documentado.
const CONFIG_CANDIDATES = [
  path.join(os.homedir(), ".gemini", "config", "mcp_config.json"),
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

function registersServer(configPath, name) {
  try {
    const raw = fs.readFileSync(configPath, "utf-8").replace(/^﻿/, "").trim();
    return Boolean(raw) && Object.hasOwn(JSON.parse(raw).mcpServers ?? {}, name);
  } catch {
    return false; // ilegible o inválido: no es un candidato; si hay que escribirlo, readConfig avisa
  }
}

function resolveConfigPaths(explicit, name) {
  if (explicit) return [explicit];
  const registered = CONFIG_CANDIDATES.filter((p) => fs.existsSync(p) && registersServer(p, name));
  if (registered.length > 0) return registered;
  return [CONFIG_CANDIDATES.find((p) => fs.existsSync(p)) ?? CONFIG_CANDIDATES[0]];
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

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const configPaths = resolveConfigPaths(opts.config, opts.name);

  if (opts.uninstall) {
    let removed = 0;
    for (const configPath of configPaths) {
      const json = readConfig(configPath);
      if (!json.mcpServers[opts.name]) {
        log(`'${opts.name}' no está registrado en ${configPath}. Nada que hacer.`);
        continue;
      }
      delete json.mcpServers[opts.name];
      writeConfig(configPath, json, opts.name, opts.dryRun);
      removed++;
    }
    return removed > 0 ? log("Desinstalado. Pulsa 'Refresh' en Manage MCP Servers de Antigravity.") : undefined;
  }

  await buildAndVerify(opts);

  for (const configPath of configPaths) {
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
  }

  log("Listo. En Antigravity: panel Agent -> menú '...' -> MCP Servers -> Manage MCP Servers -> Refresh.");
}

main();
