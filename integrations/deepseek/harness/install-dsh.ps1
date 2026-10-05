# ==============================================================================
# ZNVE - Instalador GLOBAL para DeepSeek Harness (DSH)
#
# Instala la directiva ZNVE como instrucciones globales de DSH, para que aplique
# en toda sesion y en cualquier proyecto:
#
#     $DSH_HOME/AGENTS.md      ($DSH_HOME por defecto: ~/.dsh)
#
# El contenido sale de AGENTS.md, junto a este script, y se instala como un BLOQUE
# entre marcadores (<!-- znve:start --> ... <!-- znve:end -->): lo que ya tengas en
# tu AGENTS.md global se conserva, y la desinstalacion retira solo ese bloque.
#
# Uso (compatible con Windows PowerShell 5.1 y PowerShell 7+):
#     powershell -NoProfile -ExecutionPolicy Bypass -File install-dsh.ps1            # instala
#     powershell -NoProfile -ExecutionPolicy Bypass -File install-dsh.ps1 -DryRun    # solo muestra que haria
#     powershell -NoProfile -ExecutionPolicy Bypass -File install-dsh.ps1 -Uninstall # retira el bloque
#
# No requiere el SDK de DSH ni permisos de administrador.
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Uninstall,
    # Ruta del global. Por defecto respeta $DSH_HOME y cae a ~/.dsh.
    [string]$DshHome
)

$ErrorActionPreference = 'Stop'

$SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Source = Join-Path $SkillDir 'AGENTS.md'
# La marca identifica una directiva ZNVE de cualquier version; la version la lleva AGENTS.md.
$MarkerPattern = 'Zero-Noise Vibe Engineering \(ZNVE\) v(\d+\.\d+\.\d+)'
$BlockStart = '<!-- znve:start -->'
$BlockEnd = '<!-- znve:end -->'
# El presupuesto de render de DSH es 65536 bytes para toda la cadena de AGENTS.md.
# Un global por encima de esto compite con los proyectos y puede ser descartado.
$BudgetWarnBytes = 30000


function Resolve-DshHome {
    param([string]$Explicit)
    if ($Explicit) { return $Explicit }
    if ($env:DSH_HOME) { return $env:DSH_HOME }
    return (Join-Path $env:USERPROFILE '.dsh')
}


function Read-Lf {
    param([string]$Path)
    return ((Get-Content -LiteralPath $Path -Raw -Encoding UTF8) -replace "`r`n", "`n")
}


function Write-Lf {
    # Sin BOM y con saltos LF: el repo es LF y DSH lee UTF-8.
    param([string]$Path, [string]$Text)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $utf8NoBom)
}


function Get-BlockMatch {
    param([string]$Text)
    $pattern = [regex]::Escape($BlockStart) + '.*?' + [regex]::Escape($BlockEnd)
    return [regex]::Match($Text, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
}


function Test-LegacyInstall {
    # Una instalacion anterior (v2.3.x) sustituia el archivo entero, sin marcadores.
    param([string]$Text)
    return (($Text -match $MarkerPattern) -and (-not (Get-BlockMatch -Text $Text).Success))
}


function Get-Backups {
    # Los nombres llevan la fecha (yyyyMMdd-HHmmss): ordenar por nombre es ordenar por antiguedad.
    # LastWriteTime no sirve: Copy-Item conserva la fecha del original.
    param([string]$Target)
    $dir = Split-Path -Parent $Target
    $leaf = Split-Path -Leaf $Target
    if (-not (Test-Path -LiteralPath $dir)) { return @() }
    return @(Get-ChildItem -LiteralPath $dir -Filter "$leaf.bak-*" -File -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending)
}


function Backup-File {
    param([string]$Target)
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backup = "$Target.bak-$stamp"
    Copy-Item -LiteralPath $Target -Destination $backup -Force
    Write-Host "  [ok] Copia de seguridad: $(Split-Path -Leaf $backup)"
}


function Show-Plan {
    param([string]$Target, [string]$Action, [string]$Version)
    Write-Host ''
    Write-Host "  ZNVE$(if ($Version) { " v$Version" }) -> DeepSeek Harness" -ForegroundColor Cyan
    Write-Host "  Accion   : $Action"
    Write-Host "  Origen   : $Source"
    Write-Host "  Destino  : $Target"
    Write-Host ''
}


# ------------------------------------------------------------------------------
# Desinstalacion
# ------------------------------------------------------------------------------
if ($Uninstall) {
    $home_ = Resolve-DshHome -Explicit $DshHome
    $target = Join-Path $home_ 'AGENTS.md'
    Show-Plan -Target $target -Action 'desinstalar' -Version ''

    if (-not (Test-Path -LiteralPath $target)) {
        Write-Host '  [i] No hay instalacion global de ZNVE. Nada que hacer.' -ForegroundColor Yellow
        exit 0
    }

    $current = Read-Lf -Path $target
    $block = Get-BlockMatch -Text $current

    if ($block.Success) {
        $rest = ($current.Remove($block.Index, $block.Length)) -replace "`n{3,}", "`n`n"
        $rest = $rest.Trim("`n")
        if ($DryRun) {
            if ($rest.Trim().Length -eq 0) {
                Write-Host '  [dry-run] Retiraria el bloque de ZNVE y eliminaria el archivo, que quedaria vacio.' -ForegroundColor Yellow
            } else {
                Write-Host '  [dry-run] Retiraria el bloque de ZNVE y conservaria el resto del archivo.' -ForegroundColor Yellow
            }
            exit 0
        }
        Backup-File -Target $target
        if ($rest.Trim().Length -eq 0) {
            Remove-Item -LiteralPath $target -Force
            Write-Host '  [ok] Bloque de ZNVE retirado; el archivo global quedaba vacio y se elimino.' -ForegroundColor Green
        } else {
            Write-Lf -Path $target -Text ($rest + "`n")
            Write-Host '  [ok] Bloque de ZNVE retirado; el resto del archivo global se conserva.' -ForegroundColor Green
        }
    } elseif (Test-LegacyInstall -Text $current) {
        # Instalacion anterior de archivo entero: se restaura la copia previa mas reciente
        # que no sea de ZNVE; si no la hay, el archivo era solo de ZNVE y se elimina.
        $previous = $null
        foreach ($b in (Get-Backups -Target $target)) {
            if ((Read-Lf -Path $b.FullName) -notmatch $MarkerPattern) { $previous = $b; break }
        }
        if ($DryRun) {
            if ($previous) {
                Write-Host "  [dry-run] Restauraria la copia previa: $($previous.Name)" -ForegroundColor Yellow
            } else {
                Write-Host '  [dry-run] Eliminaria el archivo global (sin copia previa que restaurar).' -ForegroundColor Yellow
            }
            exit 0
        }
        if ($previous) {
            Copy-Item -LiteralPath $previous.FullName -Destination $target -Force
            Write-Host "  [ok] Restaurada la copia previa: $($previous.Name)" -ForegroundColor Green
        } else {
            Remove-Item -LiteralPath $target -Force
            Write-Host '  [ok] Archivo global eliminado (era una instalacion de ZNVE sin copia previa).' -ForegroundColor Green
        }
    } else {
        Write-Host '  [i] El AGENTS.md global no contiene la directiva de ZNVE. No se toca.' -ForegroundColor Yellow
        exit 0
    }

    Write-Host '  [*] Abre una sesion nueva de DSH para que el cambio surta efecto.'
    Write-Host ''
    exit 0
}


# ------------------------------------------------------------------------------
# Instalacion
# ------------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $Source)) {
    Write-Host "  [!] Falta $Source" -ForegroundColor Red
    Write-Host '      Es el archivo que se instala; no se puede continuar.'
    exit 2
}

$content = Read-Lf -Path $Source

# Verificacion de contenido: la directiva debe declarar su version.
$found = [regex]::Match($content, $MarkerPattern)
if (-not $found.Success) {
    Write-Host "  [!] $Source no declara su version de ZNVE:" -ForegroundColor Red
    Write-Host '      se esperaba "Zero-Noise Vibe Engineering (ZNVE) vX.Y.Z".'
    exit 2
}
$version = $found.Groups[1].Value

$home_ = Resolve-DshHome -Explicit $DshHome
$target = Join-Path $home_ 'AGENTS.md'
Show-Plan -Target $target -Action 'instalar' -Version $version

$bytes = [System.Text.Encoding]::UTF8.GetByteCount($content)
if ($bytes -gt $BudgetWarnBytes) {
    Write-Host "  [!] AVISO: la directiva pesa $bytes bytes." -ForegroundColor Yellow
    Write-Host '      DSH conserva primero los archivos mas especificos: un global grande'
    Write-Host '      puede ser descartado cuando un AGENTS.md de proyecto compite con el.'
    Write-Host '      Conviene mantenerlo conciso y delegar los detalles al proyecto.'
}

$block = "$BlockStart`n$($content.Trim("`n"))`n$BlockEnd"

# Texto final segun el estado del destino.
$exists = Test-Path -LiteralPath $target
if (-not $exists) {
    $plan = 'crear'
    $final = "$block`n"
} else {
    $current = Read-Lf -Path $target
    $existing = Get-BlockMatch -Text $current
    if ($existing.Success) {
        $plan = 'actualizar el bloque de ZNVE y conservar el resto'
        $final = $current.Remove($existing.Index, $existing.Length).Insert($existing.Index, $block)
    } elseif (Test-LegacyInstall -Text $current) {
        $plan = 'migrar la instalacion anterior (archivo entero) a un bloque'
        $final = "$block`n"
    } else {
        $plan = 'anadir el bloque de ZNVE al final y conservar tu contenido'
        $final = $current.TrimEnd("`n") + "`n`n$block`n"
    }
}

# Idempotencia: si ya es identico, no se toca nada.
if ($exists -and ($current -eq $final)) {
    Write-Host '  [i] El global ya esta actualizado e identico. No se escribe nada.' -ForegroundColor Green
    Write-Host ''
    exit 0
}

if ($DryRun) {
    Write-Host "  [dry-run] Se haria: $plan." -ForegroundColor Yellow
    Write-Host ''
    exit 0
}

# 1. Crear el directorio global si falta.
if (-not (Test-Path -LiteralPath $home_)) {
    New-Item -ItemType Directory -Force -Path $home_ | Out-Null
    Write-Host "  [ok] Directorio global creado: $home_"
}

# 2. Copia de seguridad antes de modificar (nunca se pierde el contenido previo).
if ($exists) { Backup-File -Target $target }

# 3. Escribir.
Write-Lf -Path $target -Text $final
Write-Host "  [ok] Directiva instalada en: $target"

# 4. Verificar releyendo.
$verify = Read-Lf -Path $target
if (-not (Get-BlockMatch -Text $verify).Success -or ($verify -notmatch $MarkerPattern)) {
    Write-Host '  [!] La verificacion fallo: el archivo escrito no contiene el bloque de ZNVE.' -ForegroundColor Red
    exit 1
}
Write-Host "  [ok] Verificado: $((Get-Item -LiteralPath $target).Length) bytes, bloque de ZNVE v$version presente." -ForegroundColor Green

Write-Host ''
Write-Host '  Siguiente paso: abre una sesion NUEVA de DSH y escribe /znve-help.' -ForegroundColor Cyan
Write-Host '  Debe responder con el catalogo de los 10 comandos.'
Write-Host ''
Write-Host '  Recuerda: esto es guia, no barrera. Para invariantes duros usa el sandbox' -ForegroundColor DarkGray
Write-Host '  de archivos, la puerta de aprobacion y los checks de CI.' -ForegroundColor DarkGray
Write-Host ''
exit 0
