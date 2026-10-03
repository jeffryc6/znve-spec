# ZNVE para DeepSeek Harness (DSH)

Integración **global** de Zero-Noise Vibe Engineering (ZNVE) v2.3.0 en DeepSeek Harness. Una vez instalada, ZNVE aplica a **toda sesión de DSH, en cualquier proyecto**, sin configuración por repositorio.

## Qué problema resuelve

DSH ya soporta instrucciones persistentes mediante una cadena de archivos `AGENTS.md`. Este directorio empaqueta la directiva ZNVE en el formato que DSH carga como **contexto duradero global**, en lugar de obligarte a pegar el prompt en cada conversación.

| Archivo | Para qué sirve |
|---|---|
| `AGENTS.md` | **La directiva.** Es el archivo que se instala como global de DSH. Autocontenido y deliberadamente conciso. |
| `DSH_PROTOCOL.md` | Cómo se mapea ZNVE a los mecanismos reales de DSH, y qué se puede y qué no se puede garantizar. |
| `install-dsh.ps1` | Instalador idempotente con copia de seguridad y dry-run. |
| `../directive.md` | Directiva existente para **la app web o la API** de DeepSeek (rol `system`). No sirve para DSH: aquí el mecanismo es la cadena `AGENTS.md`. |

## Instalación

### Opción A — instalador (recomendado)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File protocols\agents\deepseek\install-dsh.ps1
```

Primero, sin escribir nada:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File protocols\agents\deepseek\install-dsh.ps1 -DryRun
```

> El script es compatible con Windows PowerShell 5.1 y con PowerShell 7+. En Windows el binario se llama
> `powershell.exe`; `pwsh.exe` solo existe si instalaste PowerShell 7 aparte. No requiere administrador.

### Opción B — manual

Copia `AGENTS.md` a la ruta global de DSH:

```powershell
Copy-Item integrations/deepseek/harness/AGENTS.md "$env:USERPROFILE\.dsh\AGENTS.md"
```

La ruta global es fija en la versión actual de DSH: `$DSH_HOME/AGENTS.md`, donde `$DSH_HOME` es `~/.dsh` salvo que lo cambies. **No existe una segunda ruta oficial** para instrucciones globales.

### Opción C — solo este repositorio

Sin efecto global: deja `AGENTS.md` en la raíz del proyecto y DSH lo cargará con prioridad sobre el global. Útil para proyectos donde no quieras ZNVE fuera de contexto.

## Verificación

Abre una **sesión nueva** de DSH y pide:

```text
/znve-help
```

Debes recibir el catálogo de los 10 comandos. Si no aparece, revisa `DSH_PROTOCOL.md` § Diagnóstico.

## Desinstalación

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File protocols\agents\deepseek\install-dsh.ps1 -Uninstall
```

Restaura la copia de seguridad más reciente si existe; si no, elimina el archivo global.

## Aviso importante

`AGENTS.md` es **guía, no barrera**. DSH lo inyecta como contexto de rol usuario y su propio texto dice que las reglas "pueden ser relevantes" y deben usarse "como guía cuando apliquen". No sustituye al sandbox de archivos, a la puerta de aprobación ni a los checks de CI. Los detalles están en `DSH_PROTOCOL.md` § Límites.

## Referencias

- [Alcance y precedencia de `AGENTS.md` en DSH](https://raw.githubusercontent.com/sandbaseai/deepseek-harness-handbook/main/docs/en/agent-patterns/agents-md-scope.md) — documento de referencia sobre la cadena de carga, el presupuesto de render y por qué "cargado" no significa "obligado".
- [Discusión upstream #3285](https://github.com/deepseek-ai/deepseek-harness/discussions/3285) — propuesta para separar la ruta global de las instrucciones de proyecto; **no implementada** a la fecha de verificación.
