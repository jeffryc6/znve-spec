<p align="right">
  <a href="https://translate.google.com/translate?sl=es&tl=en&u=https://github.com/jeffryc6/znve-spec/blob/main/protocols/agents/claude/skills/GUIA_CREAR_SKILL.md">
    <img src="https://img.shields.io/badge/Translate_to-English-blue?style=flat-square&logo=googletranslate" alt="Translate to English">
  </a>
</p>

# 🧩 Guía rápida: cómo crear una Skill de Claude

Esta guía explica, sin tecnicismos, qué necesita una *skill* para funcionar, cómo hacerla bien y cómo instalarla. Si prefieres que Claude la haga por ti, salta a **[Pídele a Claude que la cree](#-pídele-a-claude-que-la-cree)**.

---

## 🤔 ¿Qué es una skill?

Una skill es un **manual de instrucciones que Claude consulta solo cuando lo necesita**. Por ejemplo: "cómo redactamos los informes en mi empresa" o "cómo trabajar con la metodología ZNVE".

Funciona en tres niveles:

1. **Nombre y descripción:** Claude los ve siempre y con ellos decide si la skill sirve para lo que le pides.
2. **El archivo `SKILL.md`:** Claude lo lee completo cuando decide usar la skill.
3. **Archivos extra** (opcionales): Claude los abre solo si el `SKILL.md` le indica que los necesita.

Por eso la **descripción** es lo más importante: si no explica bien cuándo usar la skill, Claude nunca la abrirá.

---

## ✅ Requisitos obligatorios

Si falta uno de estos puntos, la skill no se podrá subir o no funcionará.

| # | Requisito | Ejemplo correcto |
|---|---|---|
| 1 | Una **carpeta** con el nombre de la skill | `informe-mensual/` |
| 2 | Dentro, un archivo llamado **exactamente** `SKILL.md` (en mayúsculas) | `informe-mensual/SKILL.md` |
| 3 | **Solo un** `SKILL.md` por skill (los demás archivos se llaman distinto) | `references/ejemplos.md` |
| 4 | El `SKILL.md` empieza con una **cabecera** entre dos líneas `---` | Ver plantilla abajo |
| 5 | Campo `name`: minúsculas, números y guiones; máximo 64 caracteres; sin espacios ni tildes | `informe-mensual` ✅ · `Informe Mensual` ❌ |
| 6 | Campo `description`: qué hace **y cuándo usarla**; máximo 1024 caracteres; sin los símbolos `<` ni `>` | Ver plantilla abajo |
| 7 | En la cabecera solo se permiten: `name`, `description`, `license`, `allowed-tools`, `metadata` y `compatibility` | `version` o `author` van **dentro** de `metadata` |
| 8 | Archivos guardados en **UTF-8** (no "ANSI") | Si ves `Ã©` o `??` en vez de `é` o emojis, la codificación está mal |
| 9 | Para subirla: un **.zip que contenga la carpeta** (no los archivos sueltos) | `informe-mensual.zip` → `informe-mensual/SKILL.md` |

### Estructura de carpetas

```text
informe-mensual/            ← carpeta de la skill (mismo nombre que "name")
├── SKILL.md                ← obligatorio: cabecera + instrucciones
├── references/             ← opcional: documentos de consulta
│   └── ejemplos.md
├── scripts/                ← opcional: programas que Claude puede ejecutar
└── assets/                 ← opcional: plantillas, logos, fuentes
```

### Plantilla mínima de `SKILL.md`

```markdown
---
name: informe-mensual
description: Redacta el informe mensual de ventas con el formato de la empresa (resumen, tabla por región y próximos pasos). Úsala siempre que el usuario pida un informe mensual, un resumen de ventas del mes o un reporte para dirección, aunque no diga la palabra "informe".
metadata:
  version: 1.0.0
  author: tu-usuario
---

# Informe mensual de ventas

## Cuándo aplicar
Cuando haya que resumir las ventas de un mes para dirección.

## Pasos
1. Pide los datos del mes si el usuario no los adjuntó.
2. Calcula el total y la variación frente al mes anterior.
3. Redacta con la estructura de abajo.

## Formato de salida
# Informe de [mes]
## Resumen (3 líneas como máximo)
## Tabla por región
## Próximos pasos
```

---

## 💡 Recomendaciones

**Sobre la descripción**
- Di **qué hace** y **cuándo usarla**, con las frases que diría un usuario real ("hazme el informe del mes", "resumen de ventas").
- Sé un poco insistente ("Úsala siempre que…"). Claude tiende a no usar una skill si no está seguro de que encaja.

**Sobre las instrucciones**
- Escribe como si le explicaras la tarea a un compañero nuevo: pasos claros y en orden.
- **Explica el porqué** de cada regla. "No uses tablas porque el informe se lee en el móvil" funciona mejor que "NUNCA uses tablas".
- Incluye **un ejemplo** del resultado esperado.
- Mantén el `SKILL.md` por debajo de unas **500 líneas**. Lo que sea detalle o consulta, muévelo a `references/` e indica en el `SKILL.md` cuándo leerlo.

**Sobre el contenido**
- **Nunca** pongas contraseñas, claves de API ni datos personales dentro de una skill.
- Una skill = una tarea o tema. Si hace demasiadas cosas distintas, divídela en varias.
- Guarda siempre en UTF-8 (en el Bloc de notas: *Guardar como → Codificación: UTF-8*).

---

## 🪜 Pasos a seguir

1. **Define el objetivo.** Responde en una frase: ¿qué hará la skill y cuándo debe activarse?
2. **Crea la carpeta** con un nombre en minúsculas y guiones (por ejemplo, `informe-mensual`).
3. **Escribe el `SKILL.md`** partiendo de la plantilla de arriba.
4. **Revisa la lista de requisitos** (tabla ✅). Presta atención a la cabecera y a la codificación UTF-8.
5. **Comprime la carpeta en .zip.** En Windows: clic derecho sobre la carpeta → *Enviar a* → *Carpeta comprimida*.
6. **Instálala:**
   - **claude.ai / app de escritorio:** *Settings → Capabilities → Skills → Upload skill* y elige el .zip. La opción de ejecución de código debe estar activada.
   - **Claude Code:** copia la carpeta (sin comprimir) a `~/.claude/skills/` para todos tus proyectos, o a `.claude/skills/` dentro de un proyecto concreto.
7. **Pruébala** con 2 o 3 peticiones reales, escritas como las harías normalmente. Comprueba que Claude la usa y que el resultado es el esperado.
8. **Mejórala.** Si Claude no la activa, mejora la descripción. Si la activa pero el resultado no es bueno, mejora las instrucciones o añade un ejemplo. Vuelve a subirla.

### ⚠️ Errores frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| "Unexpected key" al subir | `version` o `author` en la cabecera | Muévelos dentro de `metadata:` |
| Tildes raras o `??` en lugar de emojis | Archivo guardado en ANSI | Vuelve a guardarlo en UTF-8 |
| "SKILL.md not found" | El .zip tiene los archivos sueltos o el nombre en minúsculas | Comprime la **carpeta** y usa `SKILL.md` en mayúsculas |
| Claude nunca usa la skill | Descripción vaga ("ayuda con informes") | Añade qué hace, cuándo y ejemplos de frases del usuario |
| "Found N SKILL.md files" | Hay otro `SKILL.md` dentro de la carpeta | Cambia el nombre de los demás (por ejemplo, `references/notas.md`) |

---

## 🤖 Pídele a Claude que la cree

Copia el siguiente texto en una conversación con Claude, completa lo que está entre corchetes y adjunta cualquier documento de apoyo (manuales, ejemplos, plantillas):

```text
Quiero que crees una Skill de Claude siguiendo la guía GUIA_CREAR_SKILL.md
del repositorio jeffryc6/znve-spec.

- Qué debe hacer: [describe la tarea en 1-2 frases]
- Cuándo debe activarse: [frases que yo diría para pedirla]
- Formato del resultado: [cómo debe verse la respuesta final]
- Material de apoyo: [adjunto / no hay]

Entrégame la carpeta lista para subir en un .zip.
```

### 📌 Nota para Claude

> Si un usuario te comparte esta guía o te pide crear una skill, **créala tú mismo** siguiendo este documento:
>
> 1. Si falta información esencial (qué hace, cuándo activarse, formato del resultado), haz como máximo 3 preguntas breves. Si no, propón valores razonables y continúa.
> 2. Genera la carpeta `<name>/` con un `SKILL.md` que cumpla **todos** los requisitos de la tabla ✅. Usa `metadata` para versión y autor, UTF-8 y una descripción que diga qué hace y cuándo usarla.
> 3. Pasa a `references/` el material largo y referencia cada archivo desde el `SKILL.md` indicando cuándo leerlo.
> 4. Valida la cabecera (claves permitidas, longitud de `name` y `description`, sin `<` ni `>`) y que solo haya un `SKILL.md`.
> 5. Comprime la carpeta en un `.zip` (con la carpeta dentro) y entrégaselo al usuario con las instrucciones de instalación del paso 6.
> 6. Explica en lenguaje sencillo qué hace la skill, cómo probarla y cómo pedir mejoras.
