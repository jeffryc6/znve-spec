// Bloque gestionado de install-codex.mjs en config.toml (node:test, cero dependencias).
//
// Solo funciones puras: no compila, no arranca el servidor ni toca ~/.codex.
//
// Uso: npm test

import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { hasForeignTable, removeBlock, renderBlock, tomlString, upsertBlock } from "../install-codex.mjs";

const NAME = "znve-engine";
const block = (workspace = "/w") => renderBlock(NAME, { command: "/usr/bin/node", server: "/s/znve-mcp-server.js", workspace });
const USER_CONFIG = 'model = "gpt-5"\n\n[mcp_servers.context7]\ncommand = "npx"\nargs = ["-y", "@upstash/context7-mcp"]\n';

describe("install-codex: config.toml", () => {
  test("tomlString escapa comillas, barras invertidas y saltos de línea", () => {
    assert.equal(tomlString('C:\\a "b"\nc'), '"C:\\\\a \\"b\\"\\nc"');
  });

  test("el bloque declara command, args y ZNVE_WORKSPACE en sus tablas", () => {
    const text = block();
    assert.match(text, /^\[mcp_servers\.znve-engine\]\ncommand = "\/usr\/bin\/node"\nargs = \["\/s\/znve-mcp-server\.js"\]/m);
    assert.match(text, /^\[mcp_servers\.znve-engine\.env\]\nZNVE_WORKSPACE = "\/w"$/m);
  });

  test("en un config vacío el resultado es solo el bloque", () => {
    assert.equal(upsertBlock("", NAME, block()), `${block()}\n`);
  });

  test("se añade al final y conserva el resto del archivo byte a byte", () => {
    const out = upsertBlock(USER_CONFIG, NAME, block());
    assert.ok(out.startsWith(USER_CONFIG.trimEnd() + "\n\n"));
    assert.ok(out.endsWith(`${block()}\n`));
  });

  test("reinstalar sustituye el bloque en su sitio, sin duplicarlo", () => {
    const once = upsertBlock(USER_CONFIG, NAME, block("/w1"));
    const twice = upsertBlock(once + '\n[profiles.fast]\nmodel = "x"\n', NAME, block("/w2"));
    assert.equal(twice.match(/\[mcp_servers\.znve-engine\]/g).length, 1);
    assert.match(twice, /ZNVE_WORKSPACE = "\/w2"/);
    assert.ok(twice.indexOf("[mcp_servers.znve-engine]") < twice.indexOf("[profiles.fast]"));
  });

  test("también reconoce el bloque con finales de línea CRLF", () => {
    const crlf = upsertBlock(USER_CONFIG, NAME, block("/w1")).replace(/\n/g, "\r\n");
    const out = upsertBlock(crlf, NAME, block("/w2"));
    assert.equal(out.match(/\[mcp_servers\.znve-engine\]/g).length, 1);
  });

  test("una tabla del servidor escrita a mano fuera del bloque detiene la instalación", () => {
    for (const header of ["[mcp_servers.znve-engine]", '[mcp_servers."znve-engine"]', "[ mcp_servers . znve-engine . env ]"]) {
      const text = `${USER_CONFIG}\n${header}\ncommand = "node"\n`;
      assert.ok(hasForeignTable(text, NAME), header);
      assert.throws(() => upsertBlock(text, NAME, block()), /fuera del bloque gestionado/);
    }
  });

  test("otro servidor con prefijo parecido no cuenta como tabla ajena", () => {
    assert.equal(hasForeignTable(`${USER_CONFIG}\n[mcp_servers.znve-engine-dev]\ncommand = "x"\n`, NAME), false);
  });

  test("desinstalar retira solo el bloque", () => {
    const installed = upsertBlock(USER_CONFIG, NAME, block());
    assert.equal(removeBlock(installed, NAME).trimEnd(), USER_CONFIG.trimEnd());
    assert.equal(removeBlock(USER_CONFIG, NAME), USER_CONFIG);
  });
});
