<#
.SYNOPSIS
Genera una copia de seguridad de la base de datos PostgreSQL de HairSoft y aplica
la política de retención.

.DESCRIPTION
Crea la estructura backups\<Año>\<Mes>\{Dias,Semanas,Mensual} de forma dinámica
para cualquier mes y año, ejecuta pg_dump en formato CUSTOM (-F c) con extensión
.backup y elimina las copias que superan la retención:

  - Diario  : conserva 30 días
  - Semanal : conserva 3 meses (90 días)
  - Mensual : conserva 12 meses (365 días)

.PARAMETER Tipo
Tipo de backup a generar: Diario, Semanal o Mensual. Insensible a mayúsculas.

.PARAMETER BaseDeDatos
Nombre de la base de datos. Por defecto: hairsoft_db

.PARAMETER Usuario
Usuario de PostgreSQL. Por defecto: admin

.PARAMETER HostName
Host de PostgreSQL. Por defecto: localhost

.PARAMETER Puerto
Puerto de PostgreSQL. Por defecto: 5433

.PARAMETER Password
Contraseña de PostgreSQL. Si se define la variable de entorno PGPASSWORD se
usa esa; si no, se usa el valor por defecto (admin, igual que settings.py).

.EXAMPLE
.\backup_hairsoft.ps1 -Tipo Diario
.\backup_hairsoft.ps1 -Tipo Semanal
.\backup_hairsoft.ps1 -Tipo Mensual
#>

param(
    [ValidateSet('Diario', 'Semanal', 'Mensual')]
    [string]$Tipo = 'Diario',
    [string]$BaseDeDatos = 'hairsoft_db',
    [string]$Usuario = 'admin',
    [string]$HostName = 'localhost',
    [int]$Puerto = 5433,
    [string]$Password = 'admin'
)

$ErrorActionPreference = 'Stop'

$retencionDias = @{ Diario = 30; Semanal = 90; Mensual = 365 }
$mesesEspanol = @('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre')

$carpetaTipo = switch ($Tipo) {
    'Diario'  { 'Dias' }
    'Semanal' { 'Semanas' }
    'Mensual' { 'Mensual' }
}

# Raíz: backups\ (la carpeta padre de scripts\)
$raiz = Split-Path -Parent $PSScriptRoot
$log = Join-Path $raiz 'backup.log'

function Get-PgDumpPath {
    $cmd = Get-Command pg_dump -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $encontrado = Get-ChildItem 'C:\Program Files\PostgreSQL' -Filter 'pg_dump.exe' -Recurse -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($encontrado) { return $encontrado.FullName }
    throw 'No se encontró pg_dump. Instalá PostgreSQL o agregá sus binarios al PATH.'
}

function Get-FechaDeNombre {
    param([string]$NombreBase)
    # hairsoft_2026-09-15  -> fecha completa
    if ($NombreBase -match 'hairsoft_(\d{4})-(\d{2})-(\d{2})$') {
        return [datetime]::new([int]$Matches[1], [int]$Matches[2], [int]$Matches[3])
    }
    # hairsoft_2026-09  -> primer día del mes
    if ($NombreBase -match 'hairsoft_(\d{4})-(\d{2})$') {
        return [datetime]::new([int]$Matches[1], [int]$Matches[2], 1)
    }
    return $null
}

# Dispara una copia de seguridad. Lleva registro en backup.log.
try {
    $fecha = Get-Date
    $anio = $fecha.ToString('yyyy')
    $mes = $mesesEspanol[$fecha.Month - 1]

    $carpetaDestino = Join-Path $raiz (Join-Path $anio (Join-Path $mes $carpetaTipo))
    New-Item -ItemType Directory -Path $carpetaDestino -Force | Out-Null

    if ($Tipo -eq 'Mensual') {
        $nombreCopia = 'hairsoft_{0}-{1}.backup' -f $anio, $fecha.ToString('MM')
    }
    else {
        $nombreCopia = 'hairsoft_{0}.backup' -f $fecha.ToString('yyyy-MM-dd')
    }

    $rutaCopia = Join-Path $carpetaDestino $nombreCopia

    if ($env:PGPASSWORD) { $Password = $env:PGPASSWORD }
    $env:PGPASSWORD = $Password

    $pgDump = Get-PgDumpPath

    Write-Host "Generando backup [$Tipo] -> $rutaCopia"
    & $pgDump -h $HostName -p $Puerto -U $Usuario -d $BaseDeDatos -F c -b -f $rutaCopia
    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump falló con código de salida $LASTEXITCODE"
    }

    $tamano = (Get-Item $rutaCopia).Length
    Write-Host "Backup [$Tipo] generado correctamente ($tamano bytes)."
    Add-Content -Path $log -Encoding UTF8 -Value ("{0:yyyy-MM-dd HH:mm:ss} - [{1}] OK - {2} ({3} bytes)" -f $fecha, $Tipo, $nombreCopia, $tamano)

    # --- Política de retención: elimina copias viejas de la misma categoría ---
    $diasRetencion = $retencionDias[$Tipo]
    $corte = $fecha.Date.AddDays(-$diasRetencion)

    foreach ($archivo in Get-ChildItem -Path $carpetaDestino -Filter 'hairsoft_*.backup' -File) {
        if ($archivo.Name -eq $nombreCopia) { continue }
        $fechaCopia = Get-FechaDeNombre -NombreBase $archivo.BaseName
        if ($null -ne $fechaCopia -and $fechaCopia -lt $corte) {
            Remove-Item -LiteralPath $archivo.FullName -Force
            Add-Content -Path $log -Encoding UTF8 -Value ("{0:yyyy-MM-dd HH:mm:ss} - [{1}] RETENCIÓN - se eliminó {2}" -f $fecha, $Tipo, $archivo.Name)
            Write-Host "Retención: se eliminó la copia vieja $($archivo.Name)"
        }
    }

    Write-Host 'Proceso finalizado.'
}
catch {
    Add-Content -Path $log -Encoding UTF8 -Value ("{0:yyyy-MM-dd HH:mm:ss} - [{1}] ERROR - {2}" -f (Get-Date), $Tipo, $_.Exception.Message)
    Write-Error $_.Exception.Message
    exit 1
}