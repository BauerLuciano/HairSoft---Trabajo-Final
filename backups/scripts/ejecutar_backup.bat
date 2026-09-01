@echo off
rem Genera un backup de HairSoft. Uso: ejecutar_backup.bat [Diario|Semanal|Mensual]
setlocal
set TIPO=%~1
if "%TIPO%"=="" set TIPO=Diario
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0backup_hairsoft.ps1" -Tipo %TIPO%
if errorlevel 1 (
    echo Backup %TIPO% FALLIDO. Revisar backups\backup.log
) else (
    echo Backup %TIPO% generado correctamente.
)
endlocal