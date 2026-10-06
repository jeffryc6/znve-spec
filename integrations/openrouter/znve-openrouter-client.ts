// znve-openrouter-client.ts
// Cliente mínimo de OpenRouter para ZNVE. Requisitos: Node.js 18+ (fetch y AbortSignal.timeout nativos).
//
// - El prompt de sistema por defecto es system-prompt.md (generado por znve-auto desde master_spec.json).
// - Con `structured: true` exige la respuesta en el esquema de response-schema.json y la devuelve parseada.
// - Sin dependencias externas y sin logs: devuelve el artefacto y lanza errores explícitos.
// - Con ZNVE_OPENROUTER_USAGE=1 escribe en stderr los campos de uso de la respuesta (tokens y aciertos de caché):
//   es el instrumento de la prueba A/B. Sin la variable, no imprime nada.
// - response-schema.json debe permanecer estable: cambiarlo invalida la caché del prefijo.

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const HERE = fileURLToPath(new URL(".", import.meta.url));
const SYSTEM_PROMPT_FILE = `${HERE}system-prompt.md`;
const RESPONSE_SCHEMA_FILE = `${HERE}response-schema.json`;

const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
const DEFAULT_MODEL = "anthropic/claude-opus-5.5";
const DEFAULT_TIMEOUT_MS = 120_000;

export interface ZnveTaskOptions {
  prompt: string;
  /** Slug de OpenRouter. Por defecto: ZNVE_OPENROUTER_MODEL o anthropic/claude-opus-5.5. */
  model?: string;
  /** Prompt de sistema. Por defecto: system-prompt.md junto a este archivo. */
  systemPrompt?: string;
  /** Clave de OpenRouter. Por defecto: OPENROUTER_API_KEY. */
  apiKey?: string;
  /** true: exige el esquema znve_execution_envelope de response-schema.json. */
  structured?: boolean;
  timeoutMs?: number;
}

export async function executeZnveTask(options: ZnveTaskOptions & { structured: true }): Promise<Record<string, unknown>>;
export async function executeZnveTask(options: ZnveTaskOptions): Promise<string>;
export async function executeZnveTask({
  prompt,
  model = process.env.ZNVE_OPENROUTER_MODEL ?? DEFAULT_MODEL,
  systemPrompt,
  apiKey = process.env.OPENROUTER_API_KEY,
  structured = false,
  timeoutMs = DEFAULT_TIMEOUT_MS,
}: ZnveTaskOptions): Promise<string | Record<string, unknown>> {
  if (!apiKey) {
    throw new Error("[ZNVE_OR_CONFIG] Falta la clave: pasa apiKey o define OPENROUTER_API_KEY.");
  }

  const system = systemPrompt ?? (await readFile(SYSTEM_PROMPT_FILE, "utf-8"));
  const responseFormat = structured
    ? JSON.parse(await readFile(RESPONSE_SCHEMA_FILE, "utf-8"))
    : undefined;

  const response = await fetch(OPENROUTER_URL, {
    method: "POST",
    signal: AbortSignal.timeout(timeoutMs),
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "HTTP-Referer": "https://github.com/jeffryc6/znve-spec",
      "X-Title": "ZNVE-OpenRouter-Engine",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      // Baja temperatura para respuestas deterministas; los proveedores que no la admiten la ignoran.
      temperature: 0.1,
      top_p: 0.9,
      provider: {
        allow_fallbacks: true,
        data_collection: "deny", // Privacidad estricta
        // Con esquema, solo se enruta a proveedores que admiten response_format.
        require_parameters: structured,
      },
      ...(responseFormat && { response_format: responseFormat }),
      messages: [
        { role: "system", content: system },
        { role: "user", content: prompt },
      ],
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`[ZNVE_OR_ERROR] ${response.status}: ${errorBody}`);
  }

  const data = await response.json();
  const output: string | undefined = data.choices?.[0]?.message?.content;

  if (!output) {
    throw new Error("[ZNVE_OR_EMPTY] No se recibió contenido del proveedor.");
  }

  if (process.env.ZNVE_OPENROUTER_USAGE === "1") {
    process.stderr.write(`[ZNVE_OR_USAGE] ${JSON.stringify({ model: data.model ?? model, usage: data.usage ?? null })}\n`);
  }

  if (!structured) return output;
  try {
    return JSON.parse(output);
  } catch (err) {
    throw new Error(`[ZNVE_OR_SCHEMA] La respuesta no es JSON válido para znve_execution_envelope: ${(err as Error).message}`, {
      cause: err,
    });
  }
}
