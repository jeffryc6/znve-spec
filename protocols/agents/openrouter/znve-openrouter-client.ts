// znve-openrouter-client.ts
// Requisitos de ejecución: Node.js 18+ (usa fetch nativo)

interface OpenRouterPayload {
  prompt: string;
  model?: string;
  systemPrompt: string;
  apiKey: string;
}

export async function executeZnveTask({
  prompt,
  model = "anthropic/claude-3.5-sonnet",
  systemPrompt,
  apiKey,
}: OpenRouterPayload): Promise<void> {
  const url = "https://openrouter.ai/api/v1/chat/completions";

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "HTTP-Referer": "https://github.com/jeffryc6/znve-spec",
      "X-Title": "ZNVE-OpenRouter-Engine",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: model,
      // Enrutamiento determinista: evitar caídas y fijar temperatura ultra-baja
      temperature: 0.1,
      top_p: 0.9,
      provider: {
        order: ["Anthropic", "DeepSeek", "Together"],
        allow_fallbacks: true,
        data_collection: "deny", // Privacidad estricta
      },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: prompt },
      ],
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`[ZNVE_OR_ERROR] ${response.status}: ${errorBody}`);
  }

  const data = await response.json();
  const output = data.choices?.[0]?.message?.content;

  if (!output) {
    throw new Error("[ZNVE_OR_EMPTY] No se recibió contenido del proveedor.");
  }

  // Entrega atómica del artefacto técnico
  process.stdout.write(output + "\n");
}