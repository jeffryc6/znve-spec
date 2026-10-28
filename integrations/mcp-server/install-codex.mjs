#!/usr/bin/env node
/**
 * ZNVE MCP — Auto-installer para Codex (CLI, extensión del IDE y app). Cero dependencias.
 *
 *   node install-codex.mjs [--workspace <dir>] [--project] [--config <config.toml>] [--skills-dir <dir>]
 *                          [--name <id>] [--skip-skill] [--skip-build] [--dry-run] [--uninstall]
 *
 * Pasos: npm ci -> tsc -> handshake MCP real (initialize + tools/list) -> bloque [mcp_servers.<id>] en config.toml
 * (con backup) -> copia de la skill generada a la carpeta de skills de Codex.
 */
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { pathToFileURL } from "node:url";
import { REPO_ROOT, SERVER_JS, buildAndVerify, fail, log, toPosix } from "./install-common.mjs";

const SKILL_SOURCE = path.join(REPO_ROOT, "integrations", "codex", "skills", "znve");
// Solo se reemplaza o borra una carpeta de skill que lleve el aviso de archivo generado: nunca una skill ajena.
const GENERATED_NOTICE = "Archivo generado por znve-auto/builder.py";

function parseArgs(argv) {
  const opts = {
    name: "znve-engine", workspace: REPO_ROOT, project: false, config: null, skillsDir: null,
    skipSkill: false, skipBuild: false, dryRun: false, uninstall: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => {
      const v = argv[++i];
      if (!v) fail(`Falta el valor de ${a}`);
      return v;
    };
    if (a === "--workspace") opts.workspace = path.resolve(next());
    else if (a === "--project") opts.project = true;
    else if (a === "--config") opts.config = path.resolve(next());
    else if (a === "--skills-dir") opts.skillsDir = path.resolve(next());
    else if (a === "--name") opts.name = next();
    else if (a === "--skip-skill") opts.skipSkill = true;
    else if (a === "--skip-build") opts.skipBuild = true;
    else if (a === "--dry-run") opts.dryRun = true;
    else if (a === "--uninstall") opts.uninstall = true;
    else fail(`Argumento desconocido: ${a}`);
  }
  if (!/^[A-Za-z0-9_-]+$/.test(opts.name)) fail(`--name solo admite letras, dígitos, '-' y '_': ${opts.name}`);
  // Rutas documentadas: ~/.codex/config.toml y ~/.agents/skills (usuario); .codex/config.toml y .agents/skills (proyecto).
  const base = opts.project ? opts.workspace : os.homedir();
  opts.config ??= path.join(base, ".codex", "config.toml");
  opts.skillsDir ??= path.join(base, ".agents", "skills");
  return opts;
}

// ---------------------------------------------------------------------------
// config.toml: un bloque delimitado y nada más (no hay parser TOML sin dependencias)
// ---------------------------------------------------------------------------

export function tomlString(value) {
  return `"${String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n")}"`;
}

function markers(name) {
  return { start: `# >>> ${name} (install-codex.mjs; no lo edites a mano)`, end: `# <<< ${name}` };
}

export function renderBlock(name, { command, server, workspace }) {
  const { start, end } = markers(name);
  return [
    start,
    `[mcp_servers.${name}]`,
    `command = ${tomlString(command)}`,
    `args = [${tomlString(server)}]`,
    "startup_timeout_sec = 20",
    "",
    `[mcp_servers.${name}.env]`,
    `ZNVE_WORKSPACE = ${tomlString(workspace)}`,
    `NODE_ENV = "production"`,
    end,
  ].join("\n");
}

function blockPattern(name) {
  const { start, end } = markers(name);
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`^${esc(start)}\\r?\\n[\\s\\S]*?^${esc(end)}[ \\t]*(?:\\r?\\n|$)`, "m");
}

/** Tabla del servidor escrita fuera del bloque (a mano o con `codex mcp add`): no se reescribe TOML ajeno. */
export function hasForeignTable(text, name) {
  const outside = text.replace(blockPattern(name), "");
  const id = name.replace(/-/g, "\\-");
  return new RegExp(`^[ \\t]*\\[[ \\t]*mcp_servers[ \\t]*\\.[ \\t]*(?:${id}|"${id}"|'${id}')[ \\t]*[.\\]]`, "m").test(outside);
}

/** Sustituye el bloque si existe; si no, lo añade al final (una tabla TOML nueva solo es segura al final). */
export function upsertBlock(text, name, block) {
  if (hasForeignTable(text, name)) {
    throw new Error(`ya hay una tabla [mcp_servers.${name}] fuera del bloque gestionado. Retírala (o usa 'codex mcp remove ${name}') y repite.`);
  }
  const pattern = blockPattern(name);
  if (pattern.test(text)) return text.replace(pattern, `${block}\n`);
  const body = text.replace(/\s+$/, "");
  return (body ? `${body}\n\n` : "") + `${block}\n`;
}

export function removeBlock(text, name) {
  return text.replace(blockPattern(name), "").replace(/\n{3,}/g, "\n\n");
}

function readText(file) {
  return fs.existsSync(file) ? fs.readFileSync(file, "utf-8").replace(/^﻿/, "") : "";
}

function writeConfig(configPath, name, before, after, dryRun) {
  if (after === before) return log(`${configPath} ya está al día.`);
  if (dryRun) return log(`[dry-run] ${configPath} quedaría así en la parte gestionada:\n${after.match(blockPattern(name))?.[0] ?? "(bloque eliminado)\n"}`);
  fs.mkdirSync(path.dirname(configPath), { recursive: true });
  if (fs.existsSync(configPath)) {
    const backup = `${configPath}.bak-${Date.now()}`;
    fs.copyFileSync(configPath, backup);
    log(`Backup: ${backup}`);
  }
  fs.writeFileSync(configPath, after, "utf-8");
  log(`Config actualizado: ${configPath}`);
}

// ---------------------------------------------------------------------------
// Skill
// ---------------------------------------------------------------------------

function isOurSkill(dir) {
  const skill = path.join(dir, "SKILL.md");
  return fs.existsSync(skill) && fs.readFileSync(skill, "utf-8").includes(GENERATED_NOTICE);
}

function installSkill(skillsDir, dryRun) {
  const target = path.join(skillsDir, "znve");
  if (!isOurSkill(SKILL_SOURCE)) fail(`No existe la skill generada en ${SKILL_SOURCE}. Ejecuta: python znve-auto/builder.py`);
  if (fs.existsSync(target) && !isOurSkill(target)) fail(`${target} ya existe y no es la skill generada de ZNVE; no se sobrescribe.`);
  if (dryRun) return log(`[dry-run] copiaría ${SKILL_SOURCE} -> ${target}`);
  fs.rmSync(target, { recursive: true, force: true });
  fs.mkdirSync(skillsDir, { recursive: true });
  fs.cpSync(SKILL_SOURCE, target, { recursive: true });
  log(`Skill copiada: ${target}`);
}

function uninstallSkill(skillsDir, dryRun) {
  const target = path.join(skillsDir, "znve");
  if (!fs.existsSync(target)) return log(`No hay skill en ${target}. Nada que hacer.`);
  if (!isOurSkill(target)) return log(`${target} no es la skill generada de ZNVE; se deja intacta.`);
  if (dryRun) return log(`[dry-run] borraría ${target}`);
  fs.rmSync(target, { recursive: true, force: true });
  log(`Skill retirada: ${target}`);
}

// ---------------------------------------------------------------------------

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const before = readText(opts.config);

  if (opts.uninstall) {
    writeConfig(opts.config, opts.name, before, removeBlock(before, opts.name), opts.dryRun);
    if (!opts.skipSkill) uninstallSkill(opts.skillsDir, opts.dryRun);
    return log("Desinstalado. Reinicia Codex para que deje de cargar el servidor.");
  }

  await buildAndVerify(opts);

  const block = renderBlock(opts.name, {
    // Ruta absoluta a node: Codex no siempre hereda el PATH del shell (nvm, fnm, Volta).
    command: toPosix(process.execPath),
    server: toPosix(SERVER_JS),
    workspace: toPosix(opts.workspace),
  });
  let after;
  try {
    after = upsertBlock(before, opts.name, block);
  } catch (err) {
    fail(`${opts.config}: ${err.message}`);
  }
  writeConfig(opts.config, opts.name, before, after, opts.dryRun);
  if (!opts.skipSkill) installSkill(opts.skillsDir, opts.dryRun);

  if (opts.project) log("Codex solo carga .codex/config.toml en proyectos de confianza: márcalo como tal al abrirlo.");
  log("Listo. Reinicia Codex y comprueba con 'codex mcp list' o '/mcp' dentro de una sesión; la skill se invoca con $znve.");
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main();
