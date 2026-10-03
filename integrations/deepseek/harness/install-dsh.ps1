# ==============================================================================
# ZNVE v2.3.0 - Instalador GLOBAL para DeepSeek Harness (DSH)
#
# Instala la directiva ZNVE como instrucciones globales de DSH, para que aplique
# en toda sesion y en cualquier proyecto:
#
#     $DSH_HOME/AGENTS.md      ($DSH_HOME por defecto: ~/.dsh)
#
# El contenido sale de AGENTS.md, junto a este script.
#
# Uso (compatible con Windows PowerShell 5.1 y PowerShell 7+):
#     powershell -NoProfile -ExecutionPolicy Bypass -File install-dsh.ps1            # instala
#     powershell -NoProfile -ExecutionPolicy Bypass -File install-dsh.ps1 -DryRun    # solo muestra que haria
#     powershell -NoProfile -ExecutionPolicy Bypass -File install-dsh.ps1 -Uninstall # restaura o elimina
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
$Marker = 'Zero-Noise Vibe Engineering (ZNVE) v2.3.0'
# El presupuesto de render de DSH es 65536 bytes para toda la cadena de AGENTS.md.
# Un global por encima de esto compite con los proyectos y puede ser descartado.
$BudgetWarnBytes = 30000


function Resolve-DshHome {
    param([string]$Explicit)
    if ($Explicit) { return $Explicit }
    if ($env:DSH_HOME) { return $env:DSH_HOME }
    return (Join-Path $env:USERPROFILE '.dsh')
}


function Get-Backups {
    param([string]$Target)
    $dir = Split-Path -Parent $Target
    $leaf = Split-Path -Leaf $Target
    if (-not (Test-Path -LiteralPath $dir)) { return @() }
    return @(Get-ChildItem -LiteralPath $dir -Filter "$leaf.bak-*" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending)
}


function Show-Plan {
    param([string]$Target, [string]$Action)
    Write-Host ''
    Write-Host "  ZNVE v2.3.0 -> DeepSeek Harness" -ForegroundColor Cyan
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
    Show-Plan -Target $target -Action 'desinstalar'

    if (-not (Test-Path -LiteralPath $target)) {
        Write-Host '  [i] No hay instalacion global de ZNVE. Nada que hacer.' -ForegroundColor Yellow
        exit 0
    }

    $backups = Get-Backups -Target $target
    if ($DryRun) {
        if ($backups.Count -gt 0) {
            Write-Host "  [dry-run] Restauraria la copia mas reciente: $($backups[0].Name)" -ForegroundColor Yellow
        } else {
            Write-Host '  [dry-run] Eliminaria el archivo global (sin copia previa que restaurar).' -ForegroundColor Yellow
        }
        exit 0
    }

    if ($backups.Count -gt 0) {
        Copy-Item -LiteralPath $backups[0].FullName -Destination $target -Force
        Write-Host "  [ok] Restaurada la copia previa: $($backups[0].Name)" -ForegroundColor Green
    } else {
        Remove-Item -LiteralPath $target -Force
        Write-Host '  [ok] Archivo global eliminado (no habia copia previa).' -ForegroundColor Green
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

$home_ = Resolve-DshHome -Explicit $DshHome
$target = Join-Path $home_ 'AGENTS.md'
Show-Plan -Target $target -Action 'instalar'

$content = Get-Content -LiteralPath $Source -Raw -Encoding UTF8

# Verificacion de contenido: la directiva debe declarar su version.
if ($content -notmatch [regex]::Escape($Marker)) {
    Write-Host "  [!] $Source no contiene la marca de version esperada:" -ForegroundColor Red
    Write-Host "      '$Marker'"
    exit 2
}

$bytes = (Get-Item -LiteralPath $Source).Length
if ($bytes -gt $BudgetWarnBytes) {
    Write-Host "  [!] AVISO: la directiva pesa $bytes bytes." -ForegroundColor Yellow
    Write-Host '      DSH conserva primero los archivos mas especificos: un global grande'
    Write-Host '      puede ser descartado cuando un AGENTS.md de proyecto compite con el.'
    Write-Host '      Conviene mantenerlo conciso y delegar los detalles al proyecto.'
}

# Idempotencia: si ya es identico, no se toca nada.
if (Test-Path -LiteralPath $target) {
    $current = Get-Content -LiteralPath $target -Raw -Encoding UTF8
    if ($current -eq $content) {
        Write-Host '  [i] El global ya esta actualizado e identico. No se escribe nada.' -ForegroundColor Green
        Write-Host ''
        exit 0
    }
}

if ($DryRun) {
    if (Test-Path -LiteralPath $target) {
        Write-Host '  [dry-run] El destino existe y difiere: se guardaria copia y se sobrescribiria.' -ForegroundColor Yellow
    } else {
        Write-Host '  [dry-run] El destino no existe: se crearia.' -ForegroundColor Yellow
    }
    Write-Host ''
    exit 0
}

# 1. Crear el directorio global si falta.
if (-not (Test-Path -LiteralPath $home_)) {
    New-Item -ItemType Directory -Force -Path $home_ | Out-Null
    Write-Host "  [ok] Directorio global creado: $home_"
}

# 2. Copia de seguridad antes de sobrescribir (nunca se pierde el contenido previo).
if (Test-Path -LiteralPath $target) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backup = "$target.bak-$stamp"
    Copy-Item -LiteralPath $target -Destination $backup -Force
    Write-Host "  [ok] Copia de seguridad: $(Split-Path -Leaf $backup)"
}

# 3. Escribir sin BOM, con saltos de linea LF (el repo es LF; DSH lee UTF-8).
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$normalized = ($content -replace "`r`n", "`n")
[System.IO.File]::WriteAllText($target, $normalized, $utf8NoBom)
Write-Host "  [ok] Directiva instalada en: $target"

# 4. Verificar releyendo.
$verify = Get-Content -LiteralPath $target -Raw -Encoding UTF8
if ($verify -notmatch [regex]::Escape($Marker)) {
    Write-Host '  [!] La verificacion fallo: el archivo escrito no contiene la marca de version.' -ForegroundColor Red
    exit 1
}
Write-Host "  [ok] Verificado: $((Get-Item -LiteralPath $target).Length) bytes, marca de version presente." -ForegroundColor Green

Write-Host ''
Write-Host '  Siguiente paso: abre una sesion NUEVA de DSH y escribe /znve-help.' -ForegroundColor Cyan
Write-Host '  Debe responder con el catalogo de los 10 comandos.'
Write-Host ''
Write-Host '  Recuerda: esto es guia, no barrera. Para invariantes duros usa el sandbox' -ForegroundColor DarkGray
Write-Host '  de archivos, la puerta de aprobacion y los checks de CI.' -ForegroundColor DarkGray
Write-Host ''
exit 0
