// Tests dirigidos a los mutantes que sobrevivieron a Stryker en rutas, secretos, directorios protegidos y límites.
// Autocontenido: arranca su propio servidor por stdio sobre un workspace temporal.
import { describe, test, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const MCP_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SERVER_JS = path.join(MCP_DIR, "dist", "znve-mcp-server.js");
const MAX_SCAN_BYTES = 1024 * 1024;

let ws, outside, child;
// Enlaces de directorio: junction en Windows (no exige privilegios), symlink en POSIX. Se decide al cargar para poder usar skip.
const linkType = process.platform === "win32" ? "junction" : "dir";
const linkOk = (() => { const d = fs.mkdtempSync(path.join(os.tmpdir(), "znve-lnk-")); try { fs.mkdirSync(path.join(d, "t")); fs.symlinkSync(path.join(d, "t"), path.join(d, "l"), linkType); return true; } catch { return false; } finally { fs.rmSync(d, { recursive: true, force: true }); } })();
const pending = new Map();
let buf = "", nextId = 0;

const request = (method, params) =>
  new Promise((resolve, reject) => {
    const id = ++nextId;
    const timer = setTimeout(() => reject(new Error(`timeout en ${method}`)), 10_000);
    pending.set(id, (m) => { clearTimeout(timer); resolve(m); });
    child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
  });

async function call(name, args) {
  const msg = await request("tools/call", { name, arguments: args });
  if (msg.error) return { isError: true, body: { code: "PROTOCOL", message: String(msg.error.message) } };
  const text = msg.result.content.map((c) => c.text).join("\n");
  let body; try { body = JSON.parse(text); } catch { body = { raw: text }; }
  return { isError: Boolean(msg.result.isError), body };
}
const write = (rel, content = "x") => { const p = path.join(ws, rel); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, content); return p; };
const exists = (rel) => fs.existsSync(path.join(ws, rel));
const scan = (p, s, e) => call("znve_forensic_scan", { file_path: p, ...(s !== undefined && { start_line: s }), ...(e !== undefined && { end_line: e }) });
const harness = (dir, name, code = "// h") => call("znve_scaffold_harness", { harness_directory: dir, test_filename: name, harness_code: code });
const swrite = (file, code, disposal = "close") => call("znve_surgical_write", { target_file: file, code_content: code, disposal_pattern: disposal });

before(async () => {
  ws = fs.mkdtempSync(path.join(os.tmpdir(), "znve-sec-"));
  outside = fs.mkdtempSync(path.join(os.tmpdir(), "znve-out-"));
  child = spawn(process.execPath, [SERVER_JS], { env: { ...process.env, ZNVE_WORKSPACE: ws }, stdio: ["pipe", "pipe", "pipe"] });
  child.stdout.setEncoding("utf-8");
  child.stdout.on("data", (c) => { buf += c; let nl; while ((nl = buf.indexOf("\n")) >= 0) { const l = buf.slice(0, nl).trim(); buf = buf.slice(nl + 1); if (!l) continue; const m = JSON.parse(l); pending.get(m.id)?.(m); pending.delete(m.id); } });
  await request("initialize", { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "sec", version: "0" } });
  child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
});
after(() => { child?.kill(); fs.rmSync(ws, { recursive: true, force: true }); fs.rmSync(outside, { recursive: true, force: true }); });

describe("requireText: espacios en blanco cuentan como vacío", () => {
  for (const blank of [" ", "   ", "\t", "\n", " \t\n "]) {
    test(`file_path ${JSON.stringify(blank)} -> BAD_ARGUMENT`, async () => {
      const r = await scan(blank);
      assert.equal(r.isError, true);
      assert.equal(r.body.code, "BAD_ARGUMENT");
    });
  }
});

describe("contención de rutas (isInside)", () => {
  test("'..' exacto queda fuera", async () => { const r = await scan(".."); assert.equal(r.body.code, "OUTSIDE_WORKSPACE"); });
  test("directorio hermano con el mismo prefijo queda fuera", async () => {
    const sibling = path.basename(ws) + "-evil";
    fs.mkdirSync(path.join(path.dirname(ws), sibling), { recursive: true });
    try {
      fs.writeFileSync(path.join(path.dirname(ws), sibling, "f.txt"), "x");
      const r = await scan(`../${sibling}/f.txt`);
      assert.equal(r.body.code, "OUTSIDE_WORKSPACE");
    } finally { fs.rmSync(path.join(path.dirname(ws), sibling), { recursive: true, force: true }); }
  });
  test("ruta absoluta fuera del workspace queda fuera", async () => {
    fs.writeFileSync(path.join(outside, "o.txt"), "x");
    const r = await scan(path.join(outside, "o.txt"));
    assert.equal(r.body.code, "OUTSIDE_WORKSPACE");
  });
  test("la raíz del workspace es interna: '.' no es OUTSIDE_WORKSPACE sino NOT_A_FILE", async () => {
    const r = await scan(".");
    assert.equal(r.body.code, "NOT_A_FILE");
  });
  test("ruta interna normal con '..' que vuelve dentro es válida", async () => {
    write("deep/a.txt", "hola\n");
    const r = await scan("deep/../deep/a.txt");
    assert.equal(r.isError, false);
    assert.equal(r.body.file, "deep/a.txt");
  });
  test("componente intermedio que es un archivo no se trata como ausente (error distinto de NOT_FOUND)", { skip: process.platform === "win32" }, async () => {
    write("plain.txt", "x");
    const r = await scan("plain.txt/child");
    assert.equal(r.isError, true);
    assert.notEqual(r.body.code, "NOT_FOUND");
  });
  test("enlace (junction) que apunta fuera del workspace se rechaza", { skip: !linkOk }, async () => {
    fs.writeFileSync(path.join(outside, "secret-data.txt"), "datos");
    fs.symlinkSync(outside, path.join(ws, "escape"), linkType);
    const r = await scan("escape/secret-data.txt");
    assert.equal(r.body.code, "OUTSIDE_WORKSPACE");
  });
});

describe("znve_scaffold_harness: nombre de archivo", () => {
  test("'..' solo se rechaza como BAD_ARGUMENT", async () => { const r = await harness("tests", ".."); assert.equal(r.body.code, "BAD_ARGUMENT"); });
  test("'.' y '...' se rechazan", async () => {
    for (const n of [".", "...", "...."]) { const r = await harness("tests", n); assert.equal(r.body.code, "BAD_ARGUMENT", n); }
  });
  test("separadores y ':' se rechazan", async () => {
    for (const n of ["a/b.test.ts", "a\\b.test.ts", "c:evil.ts", "x:y"]) { const r = await harness("tests", n); assert.equal(r.body.code, "BAD_ARGUMENT", n); assert.equal(exists("tests/" + n), false); }
  });
  test("nombre normal y nombre con puntos internos se aceptan", async () => {
    assert.equal((await harness("tests/ok1", "a.test.ts")).isError, false);
    assert.equal((await harness("tests/ok1", "..hidden.snap")).isError, false);
  });
});

describe("znve_scaffold_harness: ubicación", () => {
  test("directorio raíz permitido pero solo 'tests' o 'sandbox' (sin distinguir mayúsculas)", async () => {
    assert.equal((await harness("sandbox/a", "x.test.ts")).isError, false);
    assert.equal((await harness("TESTS/a", "y.test.ts")).isError, false);
    assert.equal((await harness("src/a", "z.test.ts")).body.code, "NOT_HARNESS_DIR");
  });
  test("archivo directamente en la raíz con nombre 'tests' no cuenta como directorio de arnés", async () => {
    const r = await harness(".", "tests");
    assert.equal(r.body.code, "NOT_HARNESS_DIR");
    assert.equal((await harness(".", "sandbox")).body.code, "NOT_HARNESS_DIR");
  });
  test("enlace dentro de tests/ que apunta a otro directorio del workspace se rechaza y no escribe", { skip: !linkOk }, async () => {
    fs.mkdirSync(path.join(ws, "src-real"), { recursive: true });
    fs.mkdirSync(path.join(ws, "tests"), { recursive: true });
    fs.symlinkSync(path.join(ws, "src-real"), path.join(ws, "tests", "evil"), linkType);
    const r = await harness("tests/evil", "x.test.ts");
    assert.equal(r.body.code, "NOT_HARNESS_DIR");
    assert.equal(exists("src-real/x.test.ts"), false);
  });
  test("enlace fuera de tests/ que apunta a tests/ también se rechaza y no escribe", { skip: !linkOk }, async () => {
    fs.mkdirSync(path.join(ws, "tests", "real"), { recursive: true });
    fs.symlinkSync(path.join(ws, "tests", "real"), path.join(ws, "alias"), linkType);
    const r = await harness("alias", "x.test.ts");
    assert.equal(r.body.code, "NOT_HARNESS_DIR");
    assert.equal(exists("tests/real/x.test.ts"), false);
  });
  test("nunca sobrescribe: segundo intento falla y conserva el contenido", async () => {
    assert.equal((await harness("tests/once", "g.test.ts", "PRIMERO")).isError, false);
    const r = await harness("tests/once", "g.test.ts", "SEGUNDO");
    assert.equal(r.body.code, "ALREADY_EXISTS");
    assert.equal(fs.readFileSync(path.join(ws, "tests/once/g.test.ts"), "utf-8"), "PRIMERO");
  });
});

describe("directorios protegidos (assertWritable)", () => {
  for (const dir of [".git", "node_modules", ".GIT", "Node_Modules"]) {
    test(`surgical_write dentro de ${dir}/ -> PROTECTED_DIR`, async () => {
      const r = await swrite(`pkg/${dir}/x.js`, "const a = 1;");
      assert.equal(r.body.code, "PROTECTED_DIR");
      assert.equal(exists(`pkg/${dir}/x.js`), false);
    });
    test(`scaffold_harness dentro de tests/${dir}/ -> PROTECTED_DIR`, async () => {
      const r = await harness(`tests/${dir}`, "x.test.ts");
      assert.equal(r.body.code, "PROTECTED_DIR");
      assert.equal(exists(`tests/${dir}/x.test.ts`), false);
    });
  }
  test("un nombre que solo contiene 'node_modules' como subcadena no está protegido", async () => {
    const r = await swrite("my_node_modules_backup/x.js", "const a = 1;");
    assert.equal(r.isError, false);
  });
});

describe("secretos", () => {
  const denied = [".env", ".ENV", ".env.local", "id_rsa", "id_rsa.bak", "server.pem", "KEY.PEM", "a.key", "credentials.json", "service-account-prod.json", ".npmrc", ".netrc"];
  for (const n of denied) test(`lectura de ${n} -> SECRET_DENIED`, async () => { write("sec/" + n, "TOKEN=1"); assert.equal((await scan("sec/" + n)).body.code, "SECRET_DENIED"); });
  for (const n of denied.slice(0, 4)) test(`escritura de ${n} -> SECRET_DENIED`, async () => { assert.equal((await swrite("sec2/" + n, "const a = 1;")).body.code, "SECRET_DENIED"); assert.equal(exists("sec2/" + n), false); });
  for (const n of [".env.example", ".env.sample", ".env.template", "clave.pub", "environment.ts", "my.env", "keyboard.ts"]) {
    test(`lectura de ${n} se permite`, async () => { write("ok/" + n, "A=1"); assert.equal((await scan("ok/" + n)).isError, false); });
  }
});

describe("znve_forensic_scan: límites y forma", () => {
  test("archivo de exactamente el tope se lee; un byte más -> TOO_LARGE", async () => {
    write("big/eq.txt", "a".repeat(MAX_SCAN_BYTES));
    write("big/gt.txt", "a".repeat(MAX_SCAN_BYTES + 1));
    const eq = await scan("big/eq.txt"); assert.equal(eq.isError, false); assert.equal(eq.body.size_bytes, MAX_SCAN_BYTES);
    assert.equal((await scan("big/gt.txt")).body.code, "TOO_LARGE");
  });
  test("binario se rechaza; byte nulo en cualquier posición", async () => {
    write("bin/a.bin", Buffer.from([0x61, 0x00, 0x62]).toString("latin1"));
    fs.writeFileSync(path.join(ws, "bin/b.bin"), Buffer.from([0x00]));
    assert.equal((await scan("bin/a.bin")).body.code, "BINARY_FILE");
    assert.equal((await scan("bin/b.bin")).body.code, "BINARY_FILE");
  });
  test("inexistente -> NOT_FOUND; directorio -> NOT_A_FILE", async () => {
    assert.equal((await scan("nada.txt")).body.code, "NOT_FOUND");
    fs.mkdirSync(path.join(ws, "dir1"), { recursive: true });
    assert.equal((await scan("dir1")).body.code, "NOT_A_FILE");
  });
  test("conteo de líneas con y sin salto final", async () => {
    write("l/a.txt", "a\nb\n"); write("l/b.txt", "a\nb"); write("l/c.txt", "a\n\n"); write("l/d.txt", "a\r\nb\r\n"); write("l/e.txt", "");
    assert.equal((await scan("l/a.txt")).body.total_lines, 2);
    assert.equal((await scan("l/b.txt")).body.total_lines, 2);
    assert.equal((await scan("l/c.txt")).body.total_lines, 2);
    assert.equal((await scan("l/d.txt")).body.total_lines, 2);
    assert.equal((await scan("l/e.txt")).body.total_lines, 0);
  });
  test("rangos: válido, completo, invertido y fuera de archivo", async () => {
    write("r/a.txt", "1\n2\n3\n");
    const ok = await scan("r/a.txt", 2, 3); assert.equal(ok.isError, false); assert.deepEqual(ok.body.range, { start_line: 2, end_line: 3 });
    assert.match(ok.body.content, /\n2\n3\n/);
    assert.deepEqual((await scan("r/a.txt", 1, 3)).body.range, { start_line: 1, end_line: 3 });
    assert.deepEqual((await scan("r/a.txt", 3)).body.range, { start_line: 3, end_line: 3 });
    assert.deepEqual((await scan("r/a.txt", undefined, 2)).body.range, { start_line: 1, end_line: 2 });
    assert.equal((await scan("r/a.txt", 3, 2)).body.code, "BAD_RANGE");
    assert.equal((await scan("r/a.txt", 1, 4)).body.code, "BAD_RANGE");
    assert.equal((await scan("r/a.txt", 4, 5)).body.code, "BAD_RANGE");
    assert.equal((await scan("r/a.txt", 4)).body.code, "BAD_RANGE");
  });
  test("el id del marcador depende del contenido y el contenido va delimitado", async () => {
    write("m/a.txt", "uno"); write("m/b.txt", "dos");
    const a = (await scan("m/a.txt")).body.content, b = (await scan("m/b.txt")).body.content;
    assert.match(a, /^<<<ZNVE_UNTRUSTED_DATA id=[0-9a-f]{12}>>>\nuno\n<<<END_ZNVE_UNTRUSTED_DATA id=[0-9a-f]{12}>>>$/);
    assert.notEqual(a.match(/id=([0-9a-f]+)/)[1], b.match(/id=([0-9a-f]+)/)[1]);
  });
});

describe("znve_surgical_write: disposal y catch silencioso", () => {
  test("not_applicable con recurso abierto -> UNDISPOSED_RESOURCE y no escribe", async () => {
    const r = await swrite("d/a.ts", "const s = open(f);", "not_applicable");
    assert.equal(r.body.code, "UNDISPOSED_RESOURCE"); assert.equal(exists("d/a.ts"), false);
  });
  test("not_applicable sin recurso se escribe", async () => { assert.equal((await swrite("d/b.ts", "const a = 1;", "not_applicable")).isError, false); });
  test("recurso abierto con patrón de desecho declarado se escribe", async () => {
    for (const d of ["dispose", "close", "finally", "autocloseable"]) assert.equal((await swrite(`d/c-${d}.ts`, "const s = open(f);", d)).isError, false, d);
  });
  test("catch vacío se rechaza; catch con cuerpo se acepta", async () => {
    assert.equal((await swrite("e/a.ts", "try { x(); } catch (e) {}")).body.code, "SILENT_CATCH");
    assert.equal((await swrite("e/b.ts", "try { x(); } catch (e) { log(e); }")).isError, false);
  });
  test("except con pass se rechaza aunque haya líneas en blanco antes del cuerpo", async () => {
    assert.equal((await swrite("e/c.py", "try:\n    x()\nexcept:\n\n    pass\n")).body.code, "SILENT_CATCH");
    assert.equal((await swrite("e/d.py", "try:\n    x()\nexcept:\n\n    log()\n")).isError, false);
  });
});

describe("znve_validate_contract: lista de librerías", () => {
  const contract = (code, banned) => call("znve_validate_contract", { contract_code: code, ...(banned !== undefined && { banned_libraries: banned }) });
  test("lista explícita reemplaza a la predeterminada", async () => {
    assert.equal((await contract("import foo from 'foo';", ["foo"])).body.status, "REJECTED");
    assert.equal((await contract("import _ from 'lodash';", ["foo"])).body.status, "APPROVED");
    assert.equal((await contract("import _ from 'lodash';")).body.status, "REJECTED");
    assert.equal((await contract("import _ from 'lodash';", [])).body.status, "REJECTED");
  });
  test("entradas vacías o solo espacios -> BAD_ARGUMENT", async () => {
    for (const b of [[""], ["  "], ["lodash", ""]]) assert.equal((await contract("x", b)).body.code, "BAD_ARGUMENT");
  });
});
