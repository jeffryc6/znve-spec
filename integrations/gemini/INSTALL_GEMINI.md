<!-- Archivo generado por znve-auto/builder.py desde znve-auto/master_spec.json. No lo edites a mano. -->

# ZNVE v2.3.0: skill para Gemini

La skill sigue el formato abierto Agent Skills: una carpeta con `SKILL.md` en la raíz (frontmatter `name` y `description`) y recursos opcionales. La misma carpeta sirve para la app de Gemini (web y Mac) y para Gemini CLI.

```text
integrations/gemini/skills/znve/
├── SKILL.md                      <-- instrucciones y catálogo de comandos
└── references/
    └── chameleon-layer.md        <-- prioridades y antipatrones por plataforma
```

Referencias: [Skills en la app de Gemini](https://support.google.com/gemini/answer/17094296?hl=en&co=GENIE.Platform%3DDesktop) · [Agent Skills en Gemini CLI](https://geminicli.com/docs/cli/skills/)

---

## 1. App de Gemini (gemini.google.com y app de Mac)

Requisitos de Google: cuenta personal de Google, mayor de 18 años y la **actividad de Keep** (Keep Activity) activada.

1. Abre **Settings → Skills** en [gemini.google.com](https://gemini.google.com).
2. Pulsa **Upload** y selecciona la **carpeta** `integrations/gemini/skills/znve/` completa. Subir solo `SKILL.md` también funciona, pero sin la Capa Camaleónica.
3. Comprueba que la skill `znve` aparece activada en la página de Skills.
4. Abre un chat nuevo y prueba: `znve-help`.

Notas:

- Antes de subir la carpeta, borra archivos binarios ocultos (`.DS_Store`, `__pycache__`, `*.pyc`). Gemini solo acepta archivos de texto plano y un máximo de 100 MB.
- Las skills con archivos subidos no se pueden editar desde la app móvil ni desde la app de Mac. Para actualizar a una versión nueva de ZNVE, borra la skill en la página de Skills y vuelve a subir la carpeta.

---

## 2. Gemini CLI

### Opción A: instalar desde el repositorio

```bash
gemini skills install https://github.com/jeffryc6/znve-spec.git --path integrations/gemini/skills/znve
```

Añade `--scope workspace` para instalarla solo en el proyecto actual.

### Opción B: enlazar la copia local (se actualiza con `git pull`)

Dentro de una sesión de `gemini`:

```text
/skills link ./integrations/gemini/skills/znve --scope user
/skills reload
```

### Opción C: copiar la carpeta

| Alcance | Destino |
|---|---|
| Usuario (todos los proyectos) | `~/.gemini/skills/znve/` |
| Proyecto | `.gemini/skills/znve/` en la raíz del repositorio |

Si dos ubicaciones definen `znve`, gana la de mayor precedencia: proyecto > usuario > extensiones > integradas.

### Verificación

```bash
gemini skills list
```

Dentro de la sesión, `/skills list` debe mostrar `znve` como activa. Para pausarla sin desinstalarla, usa `/skills disable znve` y `/skills enable znve`.

---

## 3. Cómo invocar los comandos

| Entorno | Forma recomendada | Ejemplo |
|---|---|---|
| App de Gemini | Con o sin barra | `/znve-contract Diseña el DTO de usuario` |
| Gemini CLI | **Sin** barra inicial (la CLI reserva `/` para sus comandos) | `znve-contract Diseña el DTO de usuario` |

`znve-help`, `znve help` y `/znve-help` (en la app) devuelven el catálogo completo:

```text
🛠️ CATÁLOGO DE COMANDOS ZNVE v2.3.0:
• /znve-help         : Manual operativo e índice de comandos.
• /znve-contract     : Diseño de interfaces inmutables, DTOs y Anti-Bloat Fence.
• /znve-execute      : Implementación atómica en TARGET_FILE con desecho de recursos.
• /znve-triage       : Diagnóstico y contención de radio de impacto ante caídas.
• /znve-hotfix       : Parche quirúrgico atómico con test de regresión obligatorio.
• /znve-upgrade      : Migración de dependencias mediante Adaptador desacoplado.
• /znve-forensic     : Ingesta en solo lectura, matriz I/O y efectos secundarios.
• /znve-harness      : Suite Golden Master de caja negra sobre código intacto.
• /znve-legacy-rescue: Orquestación integral en 5 fases para código legacy.
• /znve-audit        : Hardening de hilos, memoria, descriptores y seguridad.

📋 REGLA POR DEFECTO (SIN COMANDO):
Toda respuesta técnica se estructura en 4 bloques:
[1] Blueprint y Contrato -> [2] Racional -> [3] Tarea Atómica -> [4] Verificación.

💡 USO: /znve <comando> <petición>   (ej.: /znve contract Diseña el DTO de usuario)
```

---

## 4. Solución de problemas

| Síntoma | Causa probable y solución |
|---|---|
| Gemini CLI responde `Unknown command` | El mensaje empezaba por `/`. Escribe `znve-help` sin barra. |
| Gemini responde sin el formato ZNVE | La skill está desactivada o no se activó. Revisa **Settings → Skills** (app) o `/skills list` (CLI), o nombra la skill: "usa la skill znve". |
| La subida falla en la app | Hay un archivo binario oculto o el nombre de la skill no está en minúsculas con guiones. No edites `SKILL.md`: regenéralo con `python znve-auto/builder.py`. |
| Una versión antigua sigue respondiendo | Hay otra copia de `znve` con más precedencia. Revisa `.gemini/skills/` y `.agents/skills/` del proyecto. |

---

## 5. Rendimiento y caché

Cada fase es una sesión. Las fases de diseño (`contract`, `forensic`, `triage`, `audit`) usan el modelo o nivel de razonamiento más alto disponible; las de ejecución (`execute`, `hotfix`, `harness`), el más rápido que cumpla el contrato. La configuración se elige al abrir la sesión. Solo cambia dentro de ella si el host lo permite sin reescribir el prefijo; si no, cambiar de modelo, de nivel de razonamiento, de herramientas o de esquema de salida invalida la caché. Al cerrar una fase verificada, recomienda el corte de sesión del perfil activo.

**Perfil activo: Gemini (app y CLI).**
- **Prefijo fijo:** skill `znve` y `~/.gemini/GEMINI.md`.
- **Invalida la caché:** editar `GEMINI.md` o la skill con la sesión abierta; activar o desactivar skills o extensiones; cambiar de modelo; compactar el historial a mitad de fase.
- **Corte de sesión:** `/clear` en la CLI o chat nuevo en la app, al cerrar cada fase.
- **Configuración por fase:** elige el modelo al abrir la sesión y no lo cambies dentro de ella.
- **Medición:** `usage_metadata.cached_content_token_count`.

Cifras de referencia, prácticas de sesión y protocolo de medición: `protocols/PROMPT_GUIDE.md`, sección «Rendimiento y caché».
