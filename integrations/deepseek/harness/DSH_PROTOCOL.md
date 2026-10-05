# Protocolo ZNVE ↔ DeepSeek Harness (DSH)

Documento técnico de la integración. Explica **cómo carga DSH las instrucciones**, **qué parte de ZNVE se puede garantizar y cuál no**, y **cómo diagnosticar** cuando una regla no se aplica.

Verificado contra la documentación de alcance de `AGENTS.md` de DeepSeek Harness (revisión de contenido 2, verificada 2026-08-27, upstream `b150a55`, versión `0.1.1-rc.2`).

---

## 1. La cadena de carga

DSH carga una cadena acotada de archivos compatibles con `AGENTS.md` en cada sesión. El orden, de menor a mayor **especificidad**:

```text
[Instrucciones de sistema y developer]
        ↓
[Petición directa del usuario]        ← máxima autoridad de rol usuario
        ↓
$DSH_HOME/AGENTS.md                   ← GLOBAL (aquí se instala ZNVE)
        ↓
<proyecto>/AGENTS.md, CLAUDE.md        ← base del proyecto
        ↓
<proyecto>/AGENTS.local.md, *.local.md ← overlay local (fuera de control de versiones)
        ↓
<subdir>/AGENTS.md                     ← anidado (descubrimiento por herramienta)
        ↓
Skill cargada explícitamente
```

Dos dimensiones distintas que conviene no confundir:

- **Autoridad:** las instrucciones de workspace **no** anulan las de sistema, developer ni la petición directa del usuario.
- **Especificidad:** dentro de la cadena, lo más específico gana sobre lo más amplio.

Valores por defecto relevantes:

| Parámetro | Valor |
|---|---|
| Base del proyecto | `AGENTS.md`, `CLAUDE.md` |
| Overlays locales | `AGENTS.local.md`, `CLAUDE.local.md` |
| Marcador de raíz | `.git` |
| Presupuesto de render | 65.536 bytes |
| Tope por archivo | 1 MiB |

Si no existe el marcador de raíz, el cwd de la sesión pasa a ser la raíz del proyecto. Dentro de un mismo directorio, dos archivos con contenido idéntico tras recortar espacios colapsan en el primero; `AGENTS.md` y `CLAUDE.md` con contenido distinto cargan ambos.

## 2. Descubrimiento anidado: lo dispara la herramienta, no el shell

Los archivos anidados **no** se cargan de forma anticipada. Tras un `read`, `write` o `edit` de primera parte que toque una ruta más profunda, DSH inspecciona los ámbitos alcanzados y encola un aviso de adición, reemplazo o eliminación.

**`cd` en shell no dispara este descubrimiento.** Cada llamada de shell tiene su propio estado, y analizar sintaxis arbitraria de shell no es la frontera de observación del sistema de archivos. Para que un ámbito anidado se vuelva visible hay que hacer una acción de sistema de archivos estructurada bajo esa ruta.

**No hay watcher de archivos.** Las ediciones externas se ven tras un toque estructurado, una reconciliación al reanudar la sesión, o una restauración del baseline tras una compactación.

Esto tiene una consecuencia práctica para ZNVE: el `AGENTS.md` que vive en `integrations/deepseek/harness/` **no** se carga por estar en el repo. Solo se carga si la sesión arranca bajo ese directorio o si una operación estructurada llega hasta él.

## 3. Qué puede y qué no puede garantizar ZNVE en DSH

DSH distingue cuatro afirmaciones que se confunden con facilidad:

| Afirmación | Quién la prueba |
|---|---|
| **descubierto** | la ruta esperada aparece en el baseline |
| **visible al modelo** | la petición derivada contiene el mensaje, dentro del presupuesto |
| **seguido** | la acción propuesta coincide con la regla en ese turno |
| **obligado** | una frontera **no basada en el modelo** rechaza la acción prohibida |

`AGENTS.md` **puede** establecer las dos primeras. **Influye** en la tercera. **No puede** establecer la cuarta por sí solo.

Traducido a ZNVE: los cinco pilares, los ocho guardrails y el flujo de comandos funcionan por instrucción (probabilístico). La contención —"no escribas fuera del repositorio", "solo estos comandos", "no expongas este secreto"— **no**.

### Mapeo: dónde vive cada garantía de ZNVE

| Requisito ZNVE | Dueño real de la obligación |
|---|---|
| "No escribas fuera del repositorio" | Política de sandbox de archivos de DSH |
| "No hagas push sin aprobación" | Puerta de aprobación + protección de rama |
| "Solo estos comandos" | Lista blanca de herramientas y validador de argumentos |
| "Los tests deben pasar antes del merge" | Checks de estado requeridos en CI |
| "Nunca expongas este secreto" | Aislamiento de credenciales, redacción y política de salida |
| "No borres datos de producción" | Credenciales de mínimo privilegio y autorización en servidor |
| Contrato primero, Anti-Bloat, hilo principal, proyecciones, cero ruido, cero relleno | `AGENTS.md` (instrucción) |

Mantén también la regla en prosa: ayuda a que el modelo elija el camino seguro. Pero no la conviertas en la última frontera.

### El `TARGET_FILE` único

ZNVE exige un único archivo objetivo por tarea atómica. En DSH esto es **una instrucción, no un confinamiento**: la herramienta de escritura no sabe nada del contrato aprobado y no hay estado entre "aprobar contrato" y "escribir". Si necesitas que sea real, el control es la política de sandbox, no la prosa.

### Solo lectura

Los comandos `/znve-help`, `/znve-triage`, `/znve-forensic` y `/znve-audit` son de solo lectura por diseño. En DSH eso se expresa como directiva; **no** desactiva ninguna herramienta de escritura. Un `read-only` de verdad se consigue con el modo de solo lectura del propio DSH.

## 4. Presupuesto: por qué el global puede desaparecer

El renderizador **conserva primero los archivos más específicos**. Cuando la cadena completa excede `maxBytes` (65.536 por defecto), descarta archivos completos empezando por los más amplios, y emite un aviso visible de presupuesto.

Consecuencia directa: **una regla global puede desaparecer bajo presión de presupuesto mientras una regla profunda de proyecto se mantiene.** Por eso `AGENTS.md` en este directorio es deliberadamente conciso: si el global engorda, compite con los proyectos y pierde.

Un archivo mayor que `maxSourceBytes` (1 MiB) se **ignora**, no se lee en parte. Una instrucción debería ser mucho más pequeña.

## 5. La colisión de `$DSH_HOME`

Cuando el workspace de la sesión **es** `$DSH_HOME`, `$DSH_HOME/AGENTS.md` tiene dos significados posibles a la vez:

1. el archivo global fijo;
2. el candidato por defecto en la raíz del proyecto.

No existe una segunda ruta oficial para instrucciones solo-globales (la [#3285](https://github.com/deepseek-ai/deepseek-harness/discussions/3285) lo propone, sin implementar). Por tanto **un solo archivo no puede contener políticas globales y de proyecto separadas**.

Recomendaciones mientras siga así:

1. Trata `$DSH_HOME/AGENTS.md` como global, no como política de un repositorio de configuración.
2. Mantén la guía específica de cada proyecto en su propio repositorio versionado.
3. **No uses enlaces simbólicos** para forzar los dos significados: los enlaces en el componente final se siguen y pueden cruzar la frontera de confianza del repositorio.
4. Si un workspace es `$DSH_HOME`, revisa las etiquetas de origen del baseline antes de actuar.

## 6. Diagnóstico

Clasifica el fallo antes de reescribir la regla.

```text
Acción inesperada
├── ¿La regla es visible en la petición actual?
│   ├── NO  → problema de ámbito, descubrimiento, refresco o presupuesto
│   └── SÍ  → ¿hay autoridad superior en conflicto?
│             ├── SÍ → resuelve el conflicto (sistema/developer/usuario)
│             └── NO → ¿es una invariante de seguridad?
│                      ├── SÍ → añade obligación determinista
│                      └── NO → haz la regla concreta y comprueba cumplimiento
```

**La regla es visible pero no se sigue**

- Busca una instrucción en conflicto de sistema, developer o usuario.
- Sustituye objetivos vagos por acción observable, frontera y condición de parada.
- Separa hechos del repositorio de flujo obligatorio: la prosa larga compite por atención.
- Pon la regla en el directorio más estrecho que aplique, no repetida en global y local.
- Declara qué hacer cuando la regla no se puede cumplir; si no, el modelo improvisa.
- Si violarla causa daño, deja de ajustar el prompt y añade una puerta de política o autorización.

**La regla nunca aparece**

- Confirma el cwd de la sesión y el marcador de raíz más cercano.
- Confirma el nombre y las mayúsculas del archivo candidato.
- Comprueba que `maxBytes` es positivo y que el archivo cabe en `maxSourceBytes`.
- Busca un aviso de presupuesto que omitiera un archivo amplio.
- Para archivos anidados, haz un toque estructurado de fs bajo ese directorio (un `cd` no basta).
- Confirma que existe un proveedor `ctx.fs` en la composición; sin él, la carga es un no-op.

**La regla aparece dos veces**

- Comprueba si el cwd o la raíz del proyecto es igual a `$DSH_HOME` (colisión de §5).
- Comprueba si `AGENTS.md` y `CLAUDE.md` son distintos y no duplicados tras recortar espacios.
- Inspecciona las rutas de origen mostradas antes de borrar nada.

**Una edición parece obsoleta**

- No esperes a un watcher: no existe.
- Haz una lectura estructurada acotada bajo el ámbito relevante, o reanuda la sesión.
- Busca `Updated instructions from:` o `Instructions removed:` en el siguiente evento de contexto.
- Para probar precedencia o descubrimiento nuevos, **abre una sesión nueva**; el historial previo sigue siendo duradero.

## 7. Puerta de aceptación

Marca cada punto en una sesión nueva antes de dar la integración por buena:

- [ ] Una sesión nueva de cualquier proyecto muestra la etiqueta de origen global.
- [ ] `/znve-help` responde con el catálogo de los 10 comandos.
- [ ] La petición directa del usuario sigue siendo autoritativa sobre la prosa del workspace.
- [ ] Un `AGENTS.md` de proyecto con reglas propias tiene prioridad sobre el global.
- [ ] Ningún secreto, token ni URL privada está presente en el baseline renderizado.
- [ ] Si el workspace es `$DSH_HOME`, se revisó la colisión de §5.
- [ ] Toda invariante destructiva, de seguridad o de salida de red tiene dueño determinista fuera de la prosa.
- [ ] El cumplimiento se probó con una tarea adversarial pequeña, no con una sola lectura del archivo.

## 8. Fuentes

- [Alcance y precedencia de `AGENTS.md` en DSH](https://raw.githubusercontent.com/sandbaseai/deepseek-harness-handbook/main/docs/en/agent-patterns/agents-md-scope.md)
- [Discusión upstream #3285 — la ruta global frente a las instrucciones de proyecto](https://github.com/deepseek-ai/deepseek-harness/discussions/3285)
- [Discusión #4731 — por qué `AGENTS.md` puede no parecer obligar al modelo](https://github.com/deepseek-ai/deepseek-harness/discussions/4731)
