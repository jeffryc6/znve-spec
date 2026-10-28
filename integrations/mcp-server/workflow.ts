/** ZNVE 2.5 workflow. One engine for every host; no model-owned success flags. */
import { createHash, randomUUID } from "node:crypto";
import * as fs from "node:fs/promises";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

type Obj = Record<string, any>;
type Schema = Record<string, any>;
export interface WorkflowIO {
  root: string;
  resolve: (file: string, write?: boolean) => Promise<string>;
  validateContent?: (content: string) => void;
}
export class WorkflowError extends Error {
  constructor(readonly code: string, message: string) { super(message); }
}
const error = (code: string, message: string): never => { throw new WorkflowError(code, message); };
const hash = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");
const idPattern = /^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}$/;
const MAX_FILE = 1024 * 1024;

/** Deliberately small JSON Schema subset, rejected rather than guessed on bad data. */
export function validate(value: unknown, schema: Schema, at = "$"): void {
  if (schema.enum && !schema.enum.includes(value)) error("BAD_ARGUMENT", `${at}: enum inválido`);
  if (schema.type === "object") {
    if (!value || typeof value !== "object" || Array.isArray(value)) error("BAD_ARGUMENT", `${at}: objeto requerido`);
    const obj = value as Obj;
    for (const key of schema.required ?? []) if (!Object.hasOwn(obj, key)) error("BAD_ARGUMENT", `${at}.${key}: requerido`);
    for (const [key, item] of Object.entries(obj)) {
      if (!schema.properties || !Object.hasOwn(schema.properties, key)) {
        if (schema.additionalProperties === false) error("BAD_ARGUMENT", `${at}.${key}: campo desconocido`);
      } else validate(item, schema.properties[key], `${at}.${key}`);
    }
  } else if (schema.type === "array") {
    if (!Array.isArray(value)) error("BAD_ARGUMENT", `${at}: array requerido`);
    const items = value as unknown[];
    if (items.length < (schema.minItems ?? 0) || items.length > (schema.maxItems ?? Infinity)) error("BAD_ARGUMENT", `${at}: tamaño inválido`);
    if (schema.uniqueItems && new Set(items.map(x => JSON.stringify(x))).size !== items.length) error("BAD_ARGUMENT", `${at}: duplicados`);
    items.forEach((v, i) => validate(v, schema.items, `${at}[${i}]`));
  } else if (schema.type === "string") {
    if (typeof value !== "string") error("BAD_ARGUMENT", `${at}: string requerido`);
    const text = value as string;
    if (text.trim().length < (schema.minLength ?? 0) || text.length > (schema.maxLength ?? Infinity) || (schema.pattern && !new RegExp(schema.pattern).test(text))) error("BAD_ARGUMENT", `${at}: texto inválido`);
  } else if (schema.type === "integer") {
    if (!Number.isInteger(value) || (value as number) < (schema.minimum ?? -Infinity) || (value as number) > (schema.maximum ?? Infinity)) error("BAD_ARGUMENT", `${at}: entero inválido`);
  } else if (schema.type === "boolean" && typeof value !== "boolean") error("BAD_ARGUMENT", `${at}: boolean requerido`);
}

export class Workflow {
  private schemas = new Map<string, Schema>();
  private state: string;
  constructor(private io: WorkflowIO) { this.state = path.join(io.root, ".znve", "state"); }

  private async schema(name: string): Promise<Schema> {
    if (!this.schemas.has(name)) {
      const here = path.dirname(fileURLToPath(import.meta.url));
      const candidates = [path.resolve(here, "../../schemas", name + ".schema.json"), path.resolve(here, "../../../schemas", name + ".schema.json")];
      for (const candidate of candidates) {
        try { this.schemas.set(name, JSON.parse(await fs.readFile(candidate, "utf8"))); break; }
        catch (e: any) { if (e.code !== "ENOENT") throw e; }
      }
    }
    return this.schemas.get(name) ?? error("IO_ERROR", `Falta esquema ${name}`);
  }

  private async digest(file: string): Promise<string> {
    const target = await this.io.resolve(file);
    try {
      const stat = await fs.stat(target);
      if (!stat.isFile() || stat.size > MAX_FILE) error("BAD_ARGUMENT", "Solo archivos regulares de hasta 1 MiB");
      return hash(await fs.readFile(target));
    } catch (e: any) { if (e.code === "ENOENT") return "missing"; throw e; }
  }

  private async snapshot(spec: Obj): Promise<Record<string, string>> {
    const snapshot: Record<string, string> = Object.create(null);
    for (const file of [...spec.required_files, ...spec.allowed_files].sort()) snapshot[file] = await this.digest(file);
    return snapshot;
  }

  private async spec(file: string): Promise<{ spec: Obj; fingerprint: string }> {
    const target = await this.io.resolve(file);
    const stat = await fs.stat(target);
    if (!stat.isFile() || stat.size > MAX_FILE) error("BAD_ARGUMENT", "Spec inválida o demasiado grande");
    const raw = await fs.readFile(target, "utf8");
    let spec: Obj;
    try { spec = JSON.parse(raw); } catch { return error("BAD_ARGUMENT", "Spec no es JSON válido"); }
    validate(spec, await this.schema("specification"));
    const ids = (items: Obj[]) => items.map(x => x.id);
    for (const items of [spec.criteria, spec.checks, spec.assumptions]) {
      if (new Set(ids(items)).size !== items.length) error("BAD_ARGUMENT", "IDs duplicados");
    }
    const checks = new Set(ids(spec.checks));
    for (const criterion of spec.criteria) if (!checks.has(criterion.check_id)) error("BAD_ARGUMENT", `Check ausente para ${criterion.id}`);
    const criteria = new Map<string, Obj>(spec.criteria.map((criterion: Obj): [string, Obj] => [criterion.id as string, criterion]));
    const ensureReferences = (items: Obj[] | undefined, field: string, known: Set<string>) => {
      for (const item of items ?? []) for (const id of item[field] ?? []) if (!known.has(id)) error("BAD_ARGUMENT", `${field} desconocido para ${item.id ?? item.from}`);
    };
    ensureReferences(spec.invariants, "check_ids", checks);
    ensureReferences(spec.observable_outcomes, "criterion_ids", new Set(criteria.keys()));
    ensureReferences(spec.state_transitions, "criterion_ids", new Set(criteria.keys()));
    for (const outcome of spec.observable_outcomes ?? []) for (const id of outcome.criterion_ids as string[]) if (!criteria.get(id)?.required) error("BAD_ARGUMENT", `Resultado observable requiere criterio obligatorio: ${id}`);
    for (const [name, items] of Object.entries({ invariants: spec.invariants ?? [], observable_outcomes: spec.observable_outcomes ?? [], decision_records: spec.decision_records ?? [] })) {
      const values = ids(items as Obj[]);
      if (new Set(values).size !== values.length) error("BAD_ARGUMENT", `IDs duplicados en ${name}`);
    }
    const risk = spec.risk_budget;
    const evidenceRank: Record<string, number> = { local: 0, component_real: 1, production_like: 2 };
    if (risk?.impact === "high") {
      if (!spec.human_intent || !(spec.observable_outcomes?.length) || !(spec.invariants?.length) || !(spec.decision_records?.length)) error("BAD_ARGUMENT", "Riesgo alto requiere intención, resultado observable, invariante y decisión");
      if (evidenceRank[risk.minimum_evidence] < evidenceRank.component_real) error("BAD_ARGUMENT", "Riesgo alto requiere evidencia component_real o production_like");
      for (const invariant of spec.invariants) for (const checkId of invariant.check_ids) {
        const kind = spec.checks.find((check: Obj) => check.id === checkId).evidence_kind;
        if (!kind || evidenceRank[kind] < evidenceRank[risk.minimum_evidence]) error("BAD_ARGUMENT", `Invariante ${invariant.id} requiere evidencia suficiente`);
      }
    }
    if (risk?.uncertainty === "high" && !spec.assumptions.some((assumption: Obj) => assumption.material)) error("BAD_ARGUMENT", "Incertidumbre alta requiere un supuesto material");
    const seen = new Set<string>();
    for (const file of [...spec.required_files, ...spec.allowed_files]) {
      if (path.isAbsolute(file) || file.includes("\\") || file.split("/").some((x: string) => !x || x === "." || x === ".." || x.includes(":"))) error("BAD_ARGUMENT", "Usa rutas relativas canónicas con /");
      const resolved = await this.io.resolve(file, spec.allowed_files.includes(file));
      if ((process.platform === "win32" ? resolved.toLowerCase() === target.toLowerCase() : resolved === target)) error("BAD_ARGUMENT", "La spec debe estar fuera de sus archivos declarados");
      const key = process.platform === "win32" ? resolved.toLowerCase() : resolved;
      if (seen.has(key)) error("BAD_ARGUMENT", "Archivo duplicado o alias entre entradas y cambios");
      seen.add(key);
    }
    if (!spec.criteria.some((c: Obj) => c.required)) error("BAD_ARGUMENT", "La spec requiere al menos un criterio obligatorio");
    return { spec, fingerprint: hash(raw) };
  }

  private approved(fingerprint: string): boolean {
    return (process.env.ZNVE_APPROVED_SPECS ?? "").split(",").map(x => x.trim()).includes(fingerprint);
  }

  private runners(): Record<string, string> {
    try {
      const value = JSON.parse(process.env.ZNVE_RUNNERS ?? "{}");
      if (!value || Array.isArray(value) || typeof value !== "object" || Object.values(value).some(x => typeof x !== "string" || !path.isAbsolute(x))) throw new Error("invalid");
      return value;
    } catch { return error("BAD_ARGUMENT", "ZNVE_RUNNERS debe mapear nombres a ejecutables absolutos"); }
  }

  /** Internal storage rejects links, including an existing .znve junction. */
  private async stateDirectory(): Promise<void> {
    const realRoot = await fs.realpath(this.io.root);
    for (const dir of [path.join(this.io.root, ".znve"), this.state]) {
      await fs.mkdir(dir, { recursive: true });
      const stat = await fs.lstat(dir);
      const real = await fs.realpath(dir);
      const rel = path.relative(realRoot, real);
      if (!stat.isDirectory() || stat.isSymbolicLink() || rel.startsWith("..") || path.isAbsolute(rel)) error("OUTSIDE_WORKSPACE", "Estado no puede usar enlaces");
    }
  }

  private async load(kind: string, id: string): Promise<Obj> {
    if (!idPattern.test(id)) error("BAD_ARGUMENT", "ID inválido");
    await this.stateDirectory();
    const file = path.join(this.state, `${kind}-${id}.json`);
    const st = await fs.lstat(file);
    if (!st.isFile() || st.isSymbolicLink() || st.size > MAX_FILE) error("BAD_ARGUMENT", "Registro inválido");
    return JSON.parse(await fs.readFile(file, "utf8"));
  }

  private async save(kind: string, id: string, value: Obj): Promise<void> {
    const file = path.join(this.state, `${kind}-${id}.json`);
    await fs.writeFile(file, JSON.stringify(value) + "\n", { flag: "wx", mode: 0o600 });
  }

  private async locked<T>(fn: () => Promise<T>): Promise<T> {
    await this.stateDirectory();
    const lock = path.join(this.state, ".lock");
    try { await fs.mkdir(lock); } catch (e: any) { if (e.code === "EEXIST") error("BUSY", "Otra operación controla el estado; un lock huérfano requiere revisión humana"); throw e; }
    try { return await fn(); } finally { await fs.rmdir(lock); }
  }

  private async stale(record: Obj, file: string): Promise<boolean> {
    const current = await this.spec(file);
    return record.spec_hash !== current.fingerprint || JSON.stringify(record.files) !== JSON.stringify(await this.snapshot(current.spec));
  }

  private async execute(check: Obj, spec: Obj): Promise<Obj> {
    const executable = this.runners()[check.runner];
    if (!executable) error("EXECUTION_DISABLED", "Runner no autorizado por el host");
    const st = await fs.stat(executable);
    if (!st.isFile()) error("BAD_ARGUMENT", "Runner no es archivo regular");
    // No shell, no inherited API keys, no raw stdout/stderr in the model or state.
    const env: NodeJS.ProcessEnv = {};
    for (const key of ["PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "TMPDIR", "LANG", "TZ"]) if (process.env[key]) env[key] = process.env[key];
    return new Promise((resolve, reject) => {
      const child = spawn(executable, check.argv, { cwd: this.io.root, env, shell: false, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
      let bytes = 0, timedOut = false, overflow = false;
      const output = createHash("sha256");
      const consume = (tag: string, data: Buffer) => {
        bytes += data.length;
        if (bytes > 65536) { overflow = true; child.kill(); }
        else output.update(tag).update(data);
      };
      child.stdout.on("data", data => consume("out", data));
      child.stderr.on("data", data => consume("err", data));
      const timer = setTimeout(() => { timedOut = true; child.kill(); }, check.timeout_ms);
      child.on("error", e => { clearTimeout(timer); reject(e); });
      child.on("close", code => {
        clearTimeout(timer);
        resolve({ state: code === 0 && !timedOut && !overflow ? "passed" : "failed", exit_code: code, timed_out: timedOut, output_limited: overflow, output_bytes: bytes, output_digest: output.digest("hex"), runner: check.runner, argv_digest: hash(JSON.stringify(check.argv)) });
      });
    });
  }

  async dispatch(operation: string, payload: Obj): Promise<Obj> {
    const requestSchema = await this.schema("workflow");
    const schema = requestSchema.$defs?.[operation];
    if (!schema) error("BAD_ARGUMENT", "Operación desconocida");
    validate(payload, schema);
    if (operation === "stall_detect") {
      const tail = payload.events.slice(-payload.window);
      const stalled = tail.length === payload.window && new Set(tail.map((x: Obj) => x.action)).size === 1 && tail.every((x: Obj) => !x.new_evidence);
      return { status: "SUCCESS", stalled, recommendation: stalled ? "Revisar hipótesis y recursos disponibles; no repetir automáticamente" : "Sin repetición exacta detectada; no demuestra progreso semántico" };
    }
    const { spec, fingerprint } = await this.spec(payload.spec_path);
    if (operation === "spec_validate") return { status: "SUCCESS", structurally_valid: true, spec_hash: fingerprint, host_approved: this.approved(fingerprint), semantic_validation: "not_proven" };
    if (operation === "preflight") {
      const files = await this.snapshot(spec);
      const missing = spec.required_files.filter((f: string) => files[f] === "missing");
      const runners = this.runners();
      const unavailable: string[] = [];
      for (const check of spec.checks) {
        const executable = runners[check.runner];
        if (!executable || !(await fs.stat(executable).then(s => s.isFile(), () => false))) unavailable.push(check.runner);
      }
      return { status: "SUCCESS", ready: missing.length === 0 && unavailable.length === 0 && this.approved(fingerprint), spec_hash: fingerprint, base_hashes: Object.fromEntries(spec.allowed_files.map((file: string) => [file, files[file]])), missing_files: missing, unavailable_runners: [...new Set(unavailable)], host_approved: this.approved(fingerprint), limits: "Comandos y red requieren permisos del host; este motor no es un sandbox" };
    }
    return this.locked(async () => {
      if (operation === "verify") {
        if (!this.approved(fingerprint)) error("SPEC_NOT_APPROVED", "El hash de spec no está aprobado en el host");
        const check = spec.checks.find((c: Obj) => c.id === payload.check_id);
        if (!check) error("BAD_ARGUMENT", "Check inexistente");
        const before = await this.snapshot(spec);
        if (spec.required_files.some((f: string) => before[f] === "missing")) error("NOT_FOUND", "Faltan entradas requeridas");
        const result = await this.execute(check, spec);
        const after = await this.snapshot(spec);
        const currentSpec = await this.spec(payload.spec_path);
        const record = { id: randomUUID(), spec_id: spec.id, spec_hash: fingerprint, check_id: check.id, files: before, created_at: new Date().toISOString(), validity: JSON.stringify(before) === JSON.stringify(after) && currentSpec.fingerprint === fingerprint ? "current" : "stale", ...result };
        validate(record, await this.schema("evidence"));
        await this.save("evidence", record.id, record);
        return { status: "SUCCESS", evidence: record };
      }
      if (operation === "gate") {
        const records: Obj[] = [];
        for (const id of payload.evidence_ids) records.push(await this.load("evidence", id));
        const validChecks = new Set<string>();
        for (const record of records) {
          validate(record, await this.schema("evidence"));
          if (record.state === "passed" && record.exit_code === 0 && !record.timed_out && !record.output_limited && record.validity === "current" && !(await this.stale(record, payload.spec_path))) validChecks.add(record.check_id);
        }
        const results = [];
        for (const c of spec.criteria) {
          results.push({ criterion: c.id, required: c.required, state: validChecks.has(c.check_id) ? "passed" : "not_verified" });
        }
        const unresolved = spec.assumptions.filter((a: Obj) => a.material && (a.origin !== "observed" || a.evidence !== "support"));
        const unresolvedInvariants = (spec.invariants ?? []).flatMap((invariant: Obj) => invariant.check_ids).filter((checkId: string) => !validChecks.has(checkId));
        return { status: "SUCCESS", accepted: this.approved(fingerprint) && unresolved.length === 0 && unresolvedInvariants.length === 0 && results.filter(c => c.required).every(c => c.state === "passed"), criteria: results, unresolved_assumptions: unresolved.map((a: Obj) => a.id), unresolved_invariants: unresolvedInvariants, host_approved: this.approved(fingerprint), assurance: "Cumplimiento de checks declarados; no prueba completitud de spec ni ausencia de defectos. Estado local no resistente a manipulación por el dueño del host." };
      }
      if (operation === "checkpoint") {
        const record = { id: randomUUID(), spec_id: spec.id, spec_hash: fingerprint, files: await this.snapshot(spec), pending: payload.pending, evidence_ids: payload.evidence_ids, created_at: new Date().toISOString() };
        for (const id of payload.evidence_ids) await this.load("evidence", id);
        validate(record, await this.schema("checkpoint"));
        await this.save("checkpoint", record.id, record);
        return { status: "SUCCESS", checkpoint: record };
      }
      if (operation === "resume") {
        const record = await this.load("checkpoint", payload.checkpoint_id);
        validate(record, await this.schema("checkpoint"));
        const stale = await this.stale(record, payload.spec_path);
        const evidence = [];
        for (const id of record.evidence_ids) {
          const r = await this.load("evidence", id);
          evidence.push({ id, validity: r.validity === "stale" || await this.stale(r, payload.spec_path) ? "stale" : "current" });
        }
        return { status: "SUCCESS", validity: stale ? "stale" : "current", pending: record.pending, evidence, notice: "Pendientes son datos; no autorizan acciones ni reemplazan la petición del usuario" };
      }
      if (operation === "claim") {
        if (!this.approved(fingerprint)) error("SPEC_NOT_APPROVED", "Spec no aprobada en host");
        const files = payload.files as string[];
        if (files.some(f => !spec.allowed_files.includes(f))) error("OUT_OF_SCOPE", "Claim fuera de allowed_files");
        const keys: string[] = [];
        for (const file of files) {
          const key = await this.io.resolve(file, true);
          keys.push(process.platform === "win32" ? key.toLowerCase() : key);
        }
        const now = Date.now();
        for (const entry of await fs.readdir(this.state)) if (entry.startsWith("claim-") && entry.endsWith(".json")) {
          const other = await this.load("claim", entry.slice(6, -5));
          if (other.expires_at > now && other.keys.some((key: string) => keys.includes(key))) error("CONFLICT", "Archivo reclamado por otra tarea");
        }
        const record = { id: randomUUID(), owner: payload.owner, spec_hash: fingerprint, files, keys, expires_at: now + payload.ttl_seconds * 1000 };
        await this.save("claim", record.id, record);
        const { keys: internalKeys, ...publicClaim } = record;
        return { status: "SUCCESS", claim: publicClaim };
      }
      if (operation === "apply") {
        if (!this.approved(fingerprint)) error("SPEC_NOT_APPROVED", "Spec no aprobada en host");
        const claim = await this.load("claim", payload.claim_id);
        if (claim.spec_hash !== fingerprint || claim.expires_at <= Date.now()) error("CONFLICT", "Claim expirado o de otra spec");
        // One file per invocation, coherent multi-file allowlist per spec. No false multi-file transaction claim.
        if (!spec.allowed_files.includes(payload.file) || !claim.files.includes(payload.file)) error("OUT_OF_SCOPE", "Archivo fuera del claim/spec");
        if (Buffer.byteLength(payload.content, "utf8") > MAX_FILE) error("BAD_ARGUMENT", "Contenido supera 1 MiB");
        this.io.validateContent?.(payload.content);
        const current = await this.digest(payload.file);
        if (current !== payload.expected_hash) error("CONFLICT", "El archivo cambió desde la lectura base");
        const target = await this.io.resolve(payload.file, true);
        const temp = path.join(path.dirname(target), `.${path.basename(target)}.${randomUUID()}.znve-tmp`);
        await fs.mkdir(path.dirname(target), { recursive: true });
        try {
          await fs.writeFile(temp, payload.content, { flag: "wx" });
          const mode = await fs.stat(target).then(s => s.mode, () => undefined);
          if (mode !== undefined) await fs.chmod(temp, mode);
          if (await this.digest(payload.file) !== current) error("CONFLICT", "Conflicto antes de escritura");
          if (current === "missing") await fs.link(temp, target);
          else await fs.rename(temp, target);
        } finally { await fs.rm(temp, { force: true }); }
        return { status: "SUCCESS", file: payload.file, hash: hash(payload.content), verification: "required", concurrency: "Cooperativa; procesos externos pueden competir fuera del lock" };
      }
      return error("BAD_ARGUMENT", "Operación sin manejador");
    });
  }
}
