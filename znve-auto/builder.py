#!/usr/bin/env python3
"""
ZNVE Artifact Compiler (solo biblioteca estándar de Python).

Genera las directivas de Claude, Gemini, Copilot, Cursor, DeepSeek, Ollama, OpenRouter y
Antigravity, el manual protocols/COMMANDS.md y el paquete znve.zip a partir de una sola
fuente de verdad: master_spec.json.

Uso:
    python znve-auto/builder.py            # genera o sincroniza los artefactos
    python znve-auto/builder.py --verify   # sale con código 1 si hay drift
    python znve-auto/builder.py --diff     # muestra el diff de cada archivo desfasado
"""

from __future__ import annotations

import argparse
import difflib
import html
import io
import json
import re
import sys
import zipfile
from pathlib import Path

AUTO_DIR = Path(__file__).resolve().parent
REPO_ROOT = AUTO_DIR.parent
SPEC_PATH = AUTO_DIR / "master_spec.json"
TEMPLATES_DIR = AUTO_DIR / "templates"

# {{clave}} inserta un bloque del contexto; {{> archivo.tmpl}} incluye otra plantilla.
PLACEHOLDER = re.compile(r"\{\{\s*(>?)\s*([\w.\-]+)\s*\}\}")
MAX_INCLUDE_DEPTH = 5

# Fecha fija para que znve.zip sea reproducible byte a byte.
ZIP_DATE = (1980, 1, 1, 0, 0, 0)

# Bloque gestionado dentro de un archivo escrito a mano. Los marcadores pueden ir en un
# comentario de Python (#), de línea (//), dentro de un bloque /** ... */ ( * ) o en un
# comentario HTML/Markdown (<!-- ... -->).
# Un archivo puede tener varios bloques con nombre: '>>> znve:generated:<nombre>'.
_MARK = r"^[ \t]*(?:#|//|\*|<!--)[ \t]*"


def region_pattern(name: str = "") -> re.Pattern:
    tag = re.escape("znve:generated" + (f":{name}" if name else "")) + r"(?![:\w])"
    return re.compile(_MARK + ">>> " + tag + r"[^\n]*\n(.*?)" + _MARK + "<<< " + tag, re.S | re.M)


class SpecError(Exception):
    """La especificación o una plantilla no permiten generar los artefactos."""


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def load_spec(path: Path = SPEC_PATH) -> dict:
    if not path.exists():
        raise SpecError(f"No se encontró la especificación maestra en {path}")
    spec = json.loads(path.read_text(encoding="utf-8"))
    ids = [c["id"] for c in spec["commands"]]
    for section in spec["sections"]:
        for cid in section["commands"]:
            if cid not in ids:
                raise SpecError(f"La sección '{section['title_es']}' referencia un comando inexistente: {cid}")
    return spec


def command_map(spec: dict) -> dict:
    return {c["id"]: c for c in spec["commands"]}


# ---------------------------------------------------------------------------
# Bloques reutilizables (cada uno es texto listo para insertar en una plantilla)
# ---------------------------------------------------------------------------

def cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def help_block(spec: dict) -> str:
    lines = [f"🛠️ CATÁLOGO DE COMANDOS ZNVE v{spec['version']}:"]
    for c in spec["commands"]:
        lines.append(f"• {c['name']:<19}: {c['summary_es']}")
    lines += [
        "",
        "📋 REGLA POR DEFECTO (SIN COMANDO):",
        "Toda respuesta técnica se estructura en 4 bloques:",
        default_format_short(spec) + ".",
        "",
        spec["invocation"]["usage_es"],
    ]
    return "\n".join(lines)


def default_format_short(spec: dict) -> str:
    blocks = spec["default_format"]["blocks"]
    return " -> ".join(f"[{i}] {b['short_es']}" for i, b in enumerate(blocks, 1))


def default_format_md(spec: dict) -> str:
    blocks = spec["default_format"]["blocks"]
    return "\n".join(f"{i}. `{b['label_es']}` — {b['desc_es']}" for i, b in enumerate(blocks, 1))


def default_format_plain(spec: dict) -> str:
    blocks = spec["default_format"]["blocks"]
    return "\n".join(f"{b['label_es']} ({b['desc_es'].rstrip('.')})" for b in blocks)


def default_format_en(spec: dict) -> str:
    blocks = spec["default_format"]["blocks"]
    return "\n".join(f"{i}. `{b['label_en']}`: {b['desc_en']}" for i, b in enumerate(blocks, 1))


def guardrails_md(spec: dict) -> str:
    return "\n".join(
        f"{i}. **{g['title_es']}.** {g['text_es']}" for i, g in enumerate(spec["guardrails"], 1)
    )


def guardrails_caps(spec: dict) -> str:
    return "\n".join(
        f"{i}. {g['title_es'].upper()}: {g['text_es']}" for i, g in enumerate(spec["guardrails"], 1)
    )


def guardrails_en(spec: dict) -> str:
    return "\n".join(f"{i}. {g['text_en']}" for i, g in enumerate(spec["guardrails"], 1))


def scenario_table_md(spec: dict) -> str:
    rows = ["| Escenario | Comando | Propósito |", "|---|---|---|"]
    rows += [f"| {s['label_es']} | {s['flow']} | {s['purpose_es']} |" for s in spec["scenarios"]]
    return "\n".join(rows)


def modes_list_md(spec: dict) -> str:
    return "\n".join(f"{s['id']}. **{s['mode_es']}** — {s['flow']}" for s in spec["scenarios"] if s["id"])


def invocation_md(spec: dict) -> str:
    return "\n".join(f"- {form}" for form in spec["invocation"]["forms_es"])


def contract_rules_md(spec: dict, indent: str = "") -> str:
    rules = spec["contract_rules"]
    out = [f"{indent}- **Stack por plataforma (`--platform`):**"]
    out += [
        f"{indent}  - **{s['platform']}** (`{s['flag']}`): {s['stack']} · persistencia: {s['persistence']}."
        for s in rules["stack"]
    ]
    out.append(f"{indent}- **Excepciones al Anti-Bloat Fence:** {rules['exception_rule_es']}")
    out.append(f"{indent}- **Lista de chequeo de solidez:**")
    out += [
        f"{indent}  {i}. **{c['title_es']}:** {c['desc_es']}" for i, c in enumerate(rules["checklist"], 1)
    ]
    out.append(
        f"{indent}- **Criterio de parada:** al cumplirse los 4 puntos, emite "
        f"\"{rules['stop_criterion']}\" y detén la generación."
    )
    out.append(f"{indent}- **Modo `--delta` (In-Flight):**")
    out += [f"{indent}  {i}. {step}" for i, step in enumerate(rules["delta_steps_es"], 1)]
    return "\n".join(out)


def command_heading(c: dict) -> str:
    return f"`{c['name']}` — {c['title_es']}"


def outputs_numbered_md(c: dict, indent: str = "  ") -> str:
    return "\n".join(
        f"{indent}{i}. `{o['label_es']}` — {o['desc_es']}" for i, o in enumerate(c["outputs"], 1)
    )


def phases_md(c: dict, indent: str = "  ") -> str:
    return "\n".join(
        f"{indent}{i}. **{p['label_es']}:** {p['desc_es']}" for i, p in enumerate(c["phases"], 1)
    )


def command_full_md(spec: dict, c: dict) -> str:
    """Bloque de un comando en estilo skill (Claude, Antigravity)."""
    lines = [f"### {command_heading(c)}"]
    if c["syntax"] != c["name"]:
        lines.append(f"- **Sintaxis:** `{c['syntax']}`")
    lines.append(f"- **Activación:** {c['activation_es']}")
    lines.append(f"- **Directiva:** {c['directive_es']}")
    if c["id"] == "help":
        lines.append("- **Salida:** imprime exactamente este bloque, sin texto adicional:")
        lines += ["", "```text", help_block(spec), "```"]
    elif c.get("phases"):
        lines.append("- **Fases:**")
        lines.append(phases_md(c))
    else:
        lines.append("- **Salida:**")
        lines.append(outputs_numbered_md(c))
    if c["id"] == "contract":
        lines.append(contract_rules_md(spec))
    return "\n".join(lines)


def commands_full_md(spec: dict) -> str:
    cmds = command_map(spec)
    parts = []
    for section in spec["sections"]:
        block = [f"## {section['title_es']}", ""]
        block.append("\n\n".join(command_full_md(spec, cmds[cid]) for cid in section["commands"]))
        parts.append("\n".join(block))
    return "\n\n---\n\n".join(parts)


def command_compact(c: dict, lang: str) -> str:
    """Una línea por comando para directivas compactas (Copilot, DeepSeek, Ollama...)."""
    aliases = [a for a in c["aliases"] if a.startswith("/znve-")]
    if lang == "en":
        names = " or ".join(f"`{n}`" for n in [c["name"], *aliases])
        text = c["directive_en"]
        if c.get("phases"):
            text += " Phases: " + " -> ".join(p["short_en"] for p in c["phases"]) + "."
        elif c["outputs"]:
            text += " Output: " + "; ".join(f"{i}) {o['label_en']}" for i, o in enumerate(c["outputs"], 1)) + "."
        extra = c.get("compact_extra_en")
    else:
        names = " o ".join(f"`{n}`" for n in [c["name"], *aliases])
        text = cap(c["directive_es"])
        if c["read_only"] and "solo lectura" not in text.lower():
            text = "SOLO LECTURA. " + text
        if c.get("phases"):
            text += " Fases: " + " -> ".join(p["short_es"] for p in c["phases"]) + "."
        elif c["outputs"]:
            text += " Salida: " + "; ".join(f"{i}) {o['label_es']}" for i, o in enumerate(c["outputs"], 1)) + "."
        extra = c.get("compact_extra_es")
    if extra:
        text += " " + extra
    return f"- {names}: {text}"


def commands_compact(spec: dict, lang: str = "es", heading: str = "###") -> str:
    cmds = command_map(spec)
    key = "caps_en" if lang == "en" else "caps_es"
    parts = []
    for section in spec["sections"]:
        title = f"{heading} {section[key]}" if heading else section[key]
        lines = [title] + [command_compact(cmds[cid], lang) for cid in section["commands"]]
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def chameleon_table_md(spec: dict) -> str:
    rows = ["| Plataforma | Prioridades ZNVE | Antipatrones prohibidos |", "|---|---|---|"]
    rows += [
        f"| **{p['name']}** | {p['priorities']} | {p['antipatterns']} |" for p in spec["chameleon"]["platforms"]
    ]
    return "\n".join(rows)


def chameleon_verification_md(spec: dict) -> str:
    return "\n".join(
        f"- **{p['name'].split(' (')[0]}:** {p['verification']}"
        for p in spec["chameleon"]["platforms"]
        if p["verification"]
    )


def chameleon_bullets(spec: dict, bold: bool = True) -> str:
    fmt = "- **{name}:** Prioriza {pri} Prohibido: {anti}" if bold else "- {name}: Prioriza {pri} Prohibido: {anti}"
    return "\n".join(
        fmt.format(name=p["name"], pri=p["priorities"], anti=p["antipatterns"])
        for p in spec["chameleon"]["platforms"]
    )


def quick_reference_table_md(spec: dict) -> str:
    rows = ["| Comando / Herramienta | Tipo | Modos o fase |", "|---|---|---|"]
    for c in spec["commands"]:
        modes = "Modo " + ", ".join(str(m) for m in c["modes"]) if c["modes"] else "Todos"
        rows.append(f"| `{c['name']}` | Comando de barra | {modes} |")
    for t in spec["mcp"]["tools"]:
        rows.append(f"| `{t['name']}` | Herramienta MCP | {t['phase']} |")
    return "\n".join(rows)


def commands_manual_md(spec: dict) -> str:
    parts = []
    for i, c in enumerate(spec["commands"], 1):
        lines = [f"### {i}. {command_heading(c)}", ""]
        lines.append(f"- **Sintaxis:** `{c['syntax']}`")
        lines.append(f"- **Cuándo se usa:** {cap(c['activation_es'])}")
        lines.append(f"- **Restricción:** {cap(c['directive_es'])}")
        lines.append(f"- **Entornos recomendados:** {c['environments_es']}")
        if c["id"] == "help":
            lines.append("- **Salida:** el catálogo de comandos:")
            lines += ["", "```text", help_block(spec), "```", ""]
        elif c.get("phases"):
            lines.append("- **Fases:**")
            lines.append(phases_md(c))
        else:
            lines.append("- **Formato de entrega:**")
            lines.append(outputs_numbered_md(c))
        if c["id"] == "contract":
            lines.append(contract_rules_md(spec))
        lines += ["- **Ejemplo:**", "", "```text", c["example_es"], "```"]
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def mcp_tools_md(spec: dict) -> str:
    parts = []
    for i, t in enumerate(spec["mcp"]["tools"], 1):
        lines = [f"### {i}. `{t['name']}`", ""]
        lines.append(f"- **Fase:** {t['phase']}")
        lines.append(f"- **Qué hace:** {t['summary_es']}")
        lines.append("- **Parámetros:**")
        for p in t["params"]:
            req = "obligatorio" if p["required"] else "opcional"
            lines.append(f"  - `{p['name']}` ({p['type']}, {req}): {p['desc_es']}")
        lines.append(f"- **Comportamiento:** {t['behavior_es']}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def mcp_tools_list_md(spec: dict) -> str:
    return "\n".join(f"- `{t['name']}`: {t['summary_es']}" for t in spec["mcp"]["tools"])


def integrations_md(spec: dict) -> str:
    parts = []
    for i, integ in enumerate(spec["integrations"], 1):
        lines = [f"### {i}. {integ['name']}", ""]
        for step in integ["steps_es"]:
            if isinstance(step, str):
                lines.append(f"- {step}")
                continue
            code = spec["mcp"]["config_example"] if step["code"] == "@mcp.config_example" else step["code"]
            lines += ["", f"```{step['lang']}", code, "```", ""]
        parts.append("\n".join(lines).rstrip())
    return "\n\n".join(parts)


def workflows_md(spec: dict) -> str:
    parts = []
    for wf in spec["workflows"]:
        steps = [f"{i}. {actor:<8} --> {text}" for i, (actor, text) in enumerate(wf["steps"], 1)]
        parts.append("\n".join([f"### {wf['title_es']}", "", "```text", *steps, "```"]))
    return "\n\n".join(parts)


def py_string(text: str) -> str:
    """Literal Python legible para un bloque de texto; repr() si el texto rompería las triples comillas."""
    if '"""' in text or "\\" in text:
        return repr(text)
    return f'"""\n{text}\n""".strip()'


def antigravity_py_constants(spec: dict) -> str:
    instruction = "\n".join([
        f"Eres el Agente Principal de Arquitectura, Ingeniería Forense y Ejecución Quirúrgica bajo el estándar ZNVE v{spec['version']}.",
        f"Axioma 1: \"{spec['axioms'][0]['es']}\"",
        f"Axioma 2: \"{spec['axioms'][1]['es']}\"",
        "Tu objetivo es garantizar contratos deterministas inmutables, cero dependencias parásitas, "
        "mínima huella de ejecución (CPU/RAM/I/O) y cero ruido operativo.",
        "",
        "🛑 REGLAS DE GOBERNANZA INVIOLABLES:",
        guardrails_caps(spec),
        "",
        "🎛️ PROTOCOLO DE COMANDOS SEGÚN ESCENARIO:",
        "",
        commands_compact(spec, "es", ""),
        "",
        "📋 ESTRUCTURA DE RESPUESTA POR DEFECTO (EN AUSENCIA DE COMANDO):",
        default_format_plain(spec),
    ])
    modes = "\n".join(s["mode_es"] for s in spec["scenarios"] if s["id"])
    return "\n".join([
        f"ZNVE_NAME = {spec['name']!r}",
        f"ZNVE_VERSION = {spec['version']!r}",
        f"ZNVE_SYSTEM_INSTRUCTION = {py_string(instruction)}",
        f"ZNVE_HELP_CATALOG = {py_string(help_block(spec))}",
        f"ZNVE_MODES = {py_string(modes)}",
        f"ZNVE_DEFAULT_FORMAT_SHORT = {default_format_short(spec)!r}",
    ])


def mcp_ts_tool_docs(spec: dict) -> str:
    """Descripciones de las herramientas y sus parámetros para el servidor MCP (tools/list)."""
    docs = {
        t["name"]: {
            "description": f"{t['summary_es']} {t['behavior_es']}",
            "params": {p["name"]: p["desc_es"] for p in t["params"]},
        }
        for t in spec["mcp"]["tools"]
    }
    body = json.dumps(docs, ensure_ascii=False, indent=2)
    return f"const TOOL_DOCS: Record<string, {{ description: string; params: Record<string, string> }}> = {body};"


def readme_commands_md(spec: dict) -> str:
    rows = [
        "| Command / Comando | Mode / Modo | Purpose | Propósito |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for c in spec["commands"]:
        modes = ", ".join(str(m) for m in c["modes"]) if c["modes"] else "—"
        rows.append(f"| `{c['syntax']}` | {modes} | {c['summary_en']} | {c['summary_es']} |")
    return "\n".join(rows)


def spec_commands_md(spec: dict) -> str:
    lines = []
    for c in spec["commands"]:
        modes = "todos" if not c["modes"] else "modo " + ", ".join(str(m) for m in c["modes"])
        ro = " Solo lectura." if c["read_only"] else ""
        lines.append(f"* `{c['syntax']}` ({modes}): {c['summary_es']}{ro}")
    return "\n".join(lines)


def index_commands_html(spec: dict) -> str:
    """Catálogo en los dos idiomas de la web; el CSS muestra el del <html lang> activo."""
    width = max(len(c["name"]) for c in spec["commands"])
    blocks = []
    for lang in ("es", "en"):
        body = "\n".join(
            f"{html.escape(c['name']):<{width}}  --&gt; {html.escape(c[f'summary_{lang}'])}" for c in spec["commands"]
        )
        blocks.append(f'        <pre class="commands" data-l="{lang}" lang="{lang}">\n{body}</pre>')
    return "\n".join(blocks)


def build_context(spec: dict) -> dict:
    notice = "Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano."
    return {
        "name": spec["name"],
        "title": spec["title"],
        "version": spec["version"],
        "author": spec["author"],
        "license": spec["license"],
        "source": spec["source"],
        "axiom_1_es": spec["axioms"][0]["es"],
        "axiom_2_es": spec["axioms"][1]["es"],
        "axiom_1_en": spec["axioms"][0]["en"],
        "axiom_2_en": spec["axioms"][1]["en"],
        "generated_md": f"<!-- {notice} -->",
        "generated_hash": f"# {notice}",
        "generated_plain": notice,
        "help_block": help_block(spec),
        "guardrails_md": guardrails_md(spec),
        "guardrails_caps": guardrails_caps(spec),
        "guardrails_en": guardrails_en(spec),
        "scenario_table_md": scenario_table_md(spec),
        "modes_list_md": modes_list_md(spec),
        "invocation_md": invocation_md(spec),
        "invocation_fallback": spec["invocation"]["fallback_es"],
        "stop_criterion": spec["contract_rules"]["stop_criterion"],
        "commands_full_md": commands_full_md(spec),
        "commands_compact_md": commands_compact(spec, "es", "###"),
        "commands_compact_h4": commands_compact(spec, "es", "####"),
        "commands_compact_plain": commands_compact(spec, "es", ""),
        "commands_compact_en": commands_compact(spec, "en", "###"),
        "commands_manual_md": commands_manual_md(spec),
        "quick_reference_table_md": quick_reference_table_md(spec),
        "mcp_tools_md": mcp_tools_md(spec),
        "mcp_tools_list_md": mcp_tools_list_md(spec),
        "integrations_md": integrations_md(spec),
        "workflows_md": workflows_md(spec),
        "chameleon_intro": spec["chameleon"]["intro_es"],
        "chameleon_table_md": chameleon_table_md(spec),
        "chameleon_verification_md": chameleon_verification_md(spec),
        "chameleon_bullets_md": chameleon_bullets(spec, bold=True),
        "chameleon_plain": chameleon_bullets(spec, bold=False),
        "default_format_md": default_format_md(spec),
        "default_format_plain": default_format_plain(spec),
        "default_format_en": default_format_en(spec),
        "default_format_short": default_format_short(spec),
        "default_format_note": spec["default_format"]["conceptual_note_es"],
        "antigravity_py_constants": antigravity_py_constants(spec),
        "mcp_ts_help_fallback": "const HELP_FALLBACK =\n  " + json.dumps(
            f"[ZNVE_HELP_FALLBACK] protocols/COMMANDS.md no disponible. Comandos ZNVE v{spec['version']}: "
            + ", ".join(c["name"] for c in spec["commands"]) + ".",
            ensure_ascii=False,
        ) + ";",
        "mcp_ts_tool_docs": mcp_ts_tool_docs(spec),
        "readme_commands_md": readme_commands_md(spec),
        "spec_commands_md": spec_commands_md(spec),
        "index_commands_html": index_commands_html(spec),
        "mcp_ts_header": "\n".join([
            f" * Framework: Zero-Noise Vibe Engineering (ZNVE) v{spec['version']}",
            f" * Axioma 1: \"{spec['axioms'][0]['es']}\"",
            f" * Axioma 2: \"{spec['axioms'][1]['es']}\"",
        ]),
    }


# ---------------------------------------------------------------------------
# Plantillas
# ---------------------------------------------------------------------------

def render(text: str, ctx: dict, source: str, depth: int = 0) -> str:
    if depth > MAX_INCLUDE_DEPTH:
        raise SpecError(f"Demasiados niveles de inclusión en {source}")

    def substitute(match: re.Match) -> str:
        include, key = match.group(1), match.group(2)
        if include:
            partial = TEMPLATES_DIR / key
            if not partial.exists():
                raise SpecError(f"{source}: la plantilla incluida '{key}' no existe")
            return render(partial.read_text(encoding="utf-8"), ctx, key, depth + 1).rstrip("\n")
        if key not in ctx:
            raise SpecError(f"{source}: marcador desconocido '{{{{{key}}}}}'")
        return ctx[key]

    return PLACEHOLDER.sub(substitute, text)


def normalize(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    return "\n".join(lines).strip("\n") + "\n"


def apply_region(rel: str, block: str, name: str = "", base: str | None = None) -> str:
    """Sustituye un bloque gestionado de un archivo escrito a mano y conserva el resto."""
    text = base if base is not None else current_text(REPO_ROOT / rel)
    if text is None:
        raise SpecError(f"{rel}: el archivo no existe")
    match = region_pattern(name).search(text)
    if not match:
        tag = "znve:generated" + (f":{name}" if name else "")
        raise SpecError(f"{rel}: faltan los marcadores '>>> {tag}' / '<<< {tag}'")
    return normalize(text[:match.start(1)] + block.strip("\n") + "\n" + text[match.end(1):])


def render_targets(spec: dict) -> dict:
    """Devuelve {ruta relativa: contenido} de todos los artefactos de texto."""
    ctx = build_context(spec)
    outputs = {}
    for target in spec["targets"]:
        tmpl_path = TEMPLATES_DIR / target["template"]
        if not tmpl_path.exists():
            raise SpecError(f"Falta la plantilla {tmpl_path.relative_to(REPO_ROOT)}")
        outputs[target["output"]] = normalize(render(tmpl_path.read_text(encoding="utf-8"), ctx, target["template"]))
    for region in spec.get("regions", []):
        if region["block"] not in ctx:
            raise SpecError(f"{region['output']}: bloque desconocido '{region['block']}'")
        rel = region["output"]
        outputs[rel] = apply_region(rel, ctx[region["block"]], region.get("name", ""), outputs.get(rel))
    for mirror in spec.get("mirrors", []):
        source = outputs.get(mirror["source"]) or current_text(REPO_ROOT / mirror["source"])
        if source is None:
            raise SpecError(f"{mirror['output']}: no existe el original {mirror['source']}")
        outputs[mirror["output"]] = source
    return outputs


def bundle_ignored(rel: str) -> bool:
    """Cachés y archivos ocultos (__pycache__, .DS_Store, .git...) nunca entran en un paquete."""
    return any(part == "__pycache__" or part.startswith(".") or part.endswith(".pyc") for part in rel.split("/"))


def bundle_members(bundle: dict, rendered: dict) -> dict:
    """Archivos del paquete: los generados dentro de la carpeta más los que existan a mano en disco."""
    prefix = f"{bundle['root']}/{bundle['folder']}/"
    members = {}
    folder = REPO_ROOT / bundle["root"] / bundle["folder"]
    if folder.exists():
        for path in folder.rglob("*"):
            if path.is_file() and not bundle_ignored(path.relative_to(folder).as_posix()):
                rel = path.relative_to(REPO_ROOT).as_posix()
                members[rel[len(bundle["root"]) + 1:]] = path.read_bytes()
    for rel, content in rendered.items():
        if rel.startswith(prefix):
            members[rel[len(bundle["root"]) + 1:]] = content.encode("utf-8")
    return dict(sorted(members.items()))


def build_zip(members: dict) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, data in members.items():
            info = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    return buffer.getvalue()


def read_zip_members(path: Path) -> dict | None:
    if not path.exists():
        return None
    with zipfile.ZipFile(path) as zf:
        return {name: zf.read(name) for name in sorted(zf.namelist())}


# ---------------------------------------------------------------------------
# Construcción y verificación
# ---------------------------------------------------------------------------

def current_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return normalize(path.read_text(encoding="utf-8"))


def build(spec: dict, verify_only: bool = False, show_diff: bool = False) -> list[str]:
    """Genera los artefactos (o solo los compara). Devuelve las rutas desfasadas o actualizadas."""
    rendered = render_targets(spec)
    changed = []

    for rel, expected in rendered.items():
        path = REPO_ROOT / rel
        actual = current_text(path)
        if actual == expected:
            continue
        changed.append(rel)
        if show_diff:
            diff = difflib.unified_diff(
                (actual or "").splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile=f"{rel} (actual)",
                tofile=f"{rel} (esperado)",
            )
            sys.stdout.writelines(diff)
        if not verify_only:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(expected)

    for bundle in spec.get("bundles", []):
        members = bundle_members(bundle, rendered)
        path = REPO_ROOT / bundle["output"]
        if read_zip_members(path) == members:
            continue
        changed.append(bundle["output"])
        if not verify_only:
            path.write_bytes(build_zip(members))

    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compila los artefactos ZNVE desde master_spec.json.")
    parser.add_argument("--verify", action="store_true", help="solo compara; sale con 1 si hay drift")
    parser.add_argument("--diff", action="store_true", help="muestra el diff de cada archivo desfasado")
    args = parser.parse_args(argv)

    try:
        spec = load_spec()
        changed = build(spec, verify_only=args.verify, show_diff=args.diff)
    except (SpecError, KeyError, json.JSONDecodeError) as err:
        print(f"[error] {err}", file=sys.stderr)
        return 2

    total = sum(len(spec.get(kind, [])) for kind in ("targets", "regions", "mirrors", "bundles"))
    if args.verify:
        if changed:
            print(f"[drift] {len(changed)} de {total} artefactos no coinciden con master_spec.json (v{spec['version']}):")
            for rel in changed:
                print(f"    - {rel}")
            print("Ejecuta: python znve-auto/builder.py")
            return 1
        print(f"[ok] {total} artefactos sincronizados con master_spec.json (v{spec['version']}).")
        return 0

    for rel in changed:
        print(f"[actualizado] {rel}")
    print(f"[ok] {len(changed)} actualizados, {total - len(changed)} sin cambios (v{spec['version']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
