# ZNVE 2.5.0 — entrega local

Spec-Driven Agent Engineering conserva axiomas y comandos anteriores. MCP 2.1.0 añade una herramienta sin romper las seis legacy.

- Motor TypeScript único; Python de Antigravity se retira con error explícito.
- Comandos spec, verify, checkpoint y resume; schemas generados de la fuente única.
- Aprobación por hash del host, runners explícitos y evidencia sin salida cruda.
- Gate, vigencia de snapshots, claims y escrituras optimistas.
- Copilot conserva .github/copilot-instructions.md; Grok se menciona sin carpeta propia.

## Migración y límites

La carpeta original no se modifica. Adopta esta copia explícitamente; no se actualizan instalaciones globales. Reconfigura Antigravity al MCP común. OpenRouter añade verification_report obligatorio; adapta sus consumidores. Las seis herramientas legacy mantienen payloads y códigos.

La evidencia local se registra en VALIDATION.md después de ejecutarse. SDKs/hosts externos sin smoke test real permanecen NO INTEGRADOS. No se afirma ahorro de tokens ni eliminación universal del drift. No se publica ni instala globalmente esta entrega.
