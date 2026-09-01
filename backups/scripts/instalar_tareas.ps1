<#
.SYNOPSIS
Registra en el Programador de tareas de Windows los backups automáticos de HairSoft:

  - HairSoft_Backup_Diario : todos los días a las 02:00
  - HairSoft_Backup_Semanal: todos los domingos a las 03:00
  - HairSoft_Backup_Mensual: el día 1 de cada mes a las 04:00

.DESCRIPTION
Requiere ejecutarse como Administrador. Los horarios se pueden cambiar editando
los triggers de este archivo o directamente desde el Programador de tareas.

.EXAMPLE
.\instalar_tareas.ps1        # registra las tres tareas
.\instalar_tareas.ps1 -SoloDiario
#>

param(
    [switch]$SoloDiario,
    [switch]$SoloSemanal,
    [switch]$SoloMensual
)

$ErrorActionPreference = 'Stop'

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Este script debe ejecutarse como Administrador (botón derecho -> Ejecutar con PowerShell como administrador).'
}

$scriptBackup = Join-Path $PSScriptRoot 'backup_hairsoft.ps1'

function New-Tarea {
    param([string]$Nombre, [string]$Tipo, [string]$Argumento, [object]$Trigger)
    $accion = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptBackup`" $Argumento"
    Register-ScheduledTask -TaskName $Nombre -Action $accion -Trigger $Trigger -Description "Backup $Tipo de HairSoft (PostgreSQL)" -Force
    Write-Host "Tarea registrada: $Nombre (backup $Tipo)"
}

$registradas = $false

if ($SoloDiario -or -not ($SoloDiario -or $SoloSemanal -or $SoloMensual)) {
    New-Tarea -Nombre 'HairSoft_Backup_Diario' -Tipo 'Diario' -Argumento '-Tipo Diario' -Trigger (New-ScheduledTaskTrigger -Daily -At '02:00')
    $registradas = $true
}
if ($SoloSemanal -or -not ($SoloDiario -or $SoloSemanal -or $SoloMensual)) {
    $triggerSemanal = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '03:00'
    New-Tarea -Nombre 'HairSoft_Backup_Semanal' -Tipo 'Semanal' -Argumento '-Tipo Semanal' -Trigger $triggerSemanal
    $registradas = $true
}
if ($SoloMensual -or -not ($SoloDiario -or $SoloSemanal -or $SoloMensual)) {
    # Día 1 de cada mes a las 04:00. Se usa la API COM de Task Scheduler porque
    # New-ScheduledTaskTrigger -Monthly no está disponible en todos los Windows.
    $servicio = New-Object -ComObject Schedule.Service
    $servicio.Connect()
    $tarea = $servicio.NewTask(0)
    $tarea.Settings.Enabled = $true
    $tarea.Settings.StartWhenAvailable = $true
    $tarea.RegistrationInfo.Description = 'Backup Mensual de HairSoft (PostgreSQL)'
    $trigger = $tarea.Triggers.Create(4)  # 4 = TASK_TRIGGER_MONTHLY
    $trigger.StartBoundary = (Get-Date).ToString('yyyy-MM-dd') + 'T04:00:00'
    $trigger.DaysOfMonth = 1
    $trigger.MonthsOfYear = 0x0FFF         # los 12 meses
    $accion = $tarea.Actions.Create(0)     # 0 = TASK_ACTION_EXEC
    $accion.Path = 'powershell.exe'
    $accion.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptBackup`" -Tipo Mensual"
    $servicio.GetFolder('\').RegisterTaskDefinition('HairSoft_Backup_Mensual', $tarea, 6, $null, $null, $null) | Out-Null
    Write-Host 'Tarea registrada: HairSoft_Backup_Mensual (backup Mensual)'
    $registradas = $true
}

if ($registradas) {
    Write-Host ''
    Write-Host 'Backups automatizados. Para desinstalar:'
    Write-Host '  Unregister-ScheduledTask -TaskName HairSoft_Backup_Diario -Confirm:$false'
    Write-Host '  Unregister-ScheduledTask -TaskName HairSoft_Backup_Semanal -Confirm:$false'
    Write-Host '  Unregister-ScheduledTask -TaskName HairSoft_Backup_Mensual -Confirm:$false'
    Write-Host ''
    Write-Host 'O resumir en una línea:'
    Write-Host '  Get-ScheduledTask -TaskName "HairSoft_Backup_*" | Unregister-ScheduledTask -Confirm:$false'
}