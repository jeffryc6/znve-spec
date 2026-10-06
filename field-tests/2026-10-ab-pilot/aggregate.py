import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = []
for f in sorted((HERE / "results").glob("*.jsonl")):
    if f.name.startswith("pilot"):
        continue
    for line in f.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        # si una celda se repitió tras un error, vale la última sin error
        rows.append(r)

latest = {}
for r in rows:
    key = (r["provider"], r["variant"], r["task"], r["rep"])
    if key not in latest or (latest[key]["error"] and not r["error"]):
        latest[key] = r
rows = list(latest.values())
valid = [r for r in rows if not r["error"]]
errors = [r for r in rows if r["error"]]


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def fmt(x):
    return f"{x:,.0f}".replace(",", ".") if x == x else "n/d"


def table(provider):
    out = []
    for task in ("execute", "harness", "injection", "secrets", "integrity"):
        for variant in "ABC":
            cell = [r for r in valid if r["provider"] == provider and r["task"] == task and r["variant"] == variant]
            if not cell:
                continue
            ok = sum(1 for r in cell if r["eval"].get("success"))
            extra = ""
            if task == "injection":
                extra = f"obedeció {sum(r['eval']['obeyed'] for r in cell)}/{len(cell)}, lo reportó {sum(r['eval']['reported'] for r in cell)}/{len(cell)}"
            if task == "secrets":
                extra = f"filtró {sum(r['eval']['leaked'] for r in cell)}/{len(cell)}, leyó .env {sum(r['eval']['read_env'] for r in cell)}/{len(cell)}"
            if task == "integrity":
                extra = f"tests intactos {sum(r['eval']['test_intact'] for r in cell)}/{len(cell)}, código correcto {sum(r['eval']['code_correct'] for r in cell)}/{len(cell)}, lo reportó {sum(r['eval']['reported'] for r in cell)}/{len(cell)}"
            if task == "execute":
                extra = f"tests {sum(r['eval']['tests_pass'] for r in cell)}/{len(cell)}, un solo archivo {sum(r['eval']['single_target'] for r in cell)}/{len(cell)}"
            if task == "harness":
                extra = f"determinista {sum(r['eval']['deterministic'] for r in cell)}/{len(cell)}, legacy intacto {sum(r['eval']['legacy_intact'] for r in cell)}/{len(cell)}"
            out.append(
                f"| {task} | {variant} | {len(cell)} | {ok}/{len(cell)} | {mean(r['turns'] for r in cell):.1f} | "
                f"{fmt(mean(r['tokens_input'] for r in cell))} | {fmt(mean(r['tokens_input'] - r['tokens_cached'] for r in cell))} | "
                f"{fmt(mean(r['tokens_output'] for r in cell))} | {fmt(mean(r['tokens_thoughts'] for r in cell))} | {fmt(mean(r['bytes_read'] for r in cell))} | {extra} |"
            )
    return out


header = "| Tarea | Var | N | Éxito | Turnos | Tokens entrada | Sin caché | Salida | Razonam. | Bytes leídos | Detalle |\n|---|---|---|---|---|---|---|---|---|---|---|"
for provider in sorted({r["provider"] for r in rows}):
    model = next(r["model"] for r in rows if r["provider"] == provider)
    print(f"\n### {provider} ({model})\n")
    print(header)
    print("\n".join(table(provider)))
    print("\nTotales por variante (medias por ejecución válida):\n")
    print("| Var | N | Éxito | Entrada/turno | Sin caché/turno | Salida/ejecución | Turnos |\n|---|---|---|---|---|---|---|")
    for variant in "ABC":
        cell = [r for r in valid if r["provider"] == provider and r["variant"] == variant]
        if not cell:
            continue
        turns = sum(r["turns"] for r in cell)
        print(
            f"| {variant} | {len(cell)} | {sum(1 for r in cell if r['eval'].get('success'))}/{len(cell)} | "
            f"{fmt(sum(r['tokens_input'] for r in cell) / turns)} | {fmt(sum(r['tokens_input'] - r['tokens_cached'] for r in cell) / turns)} | "
            f"{fmt(mean(r['tokens_output'] for r in cell))} | {mean(r['turns'] for r in cell):.1f} |"
        )
print(f"\nEjecuciones válidas: {len(valid)}; con error de proveedor (excluidas): {len(errors)}")
for r in errors:
    print("  -", r["provider"], r["variant"], r["task"], r["rep"], (r["error"] or "")[:90].replace("\n", " "))
