========================================
COPIAS DE SEGURIDAD DE HAIRSOFT (PostgreSQL)
========================================

1. QUE SON LAS COPIAS DE SEGURIDAD DE HAIRSOFT
----------------------------------------------
Son archivos .backup que contienen una "foto" completa de la base de datos
PostgreSQL (structure y datos: usuarios, ventas, turnos, productos, etc.).
Se generan con la herramienta pg_dump de PostgreSQL. Permiten recuperar la
base de datos completa si algo sale mal (borrado accidental, error, fallo del
servidor, etc.).

2. IMPORTANTE: LOS ARCHIVOS .backup NO SON ARCHIVOS "CORRUPtos"
--------------------------------------------------------------
Los archivos .backup generados están en el formato CUSTOM de PostgreSQL
(se genera con la opcion -F c). Las letras y simbolos raros que puedas ver si
los abres con un editor de texto son NORMALES: es un formato binario
comprimido, NO es un archivo de texto ni un archivo danado. Nunca intentes
"repararlos" ni abrirlos/guardarlos con un editor de texto.

3. COMO VERIFICAR UN BACKUP (probar que esta sano)
--------------------------------------------------
Abre una terminal y ejecuta (el backup solo se LEE, no se modifica):

  pg_restore -l "D:\Facultad\Trabajo final\HairSoft\backups\nombre_del_backup.backup"

La opcion -l (list) lista el contenido del backup sin restaurarlo.
Si el comando termina mostrando la lista de tablas/objetos sin errores,
el backup es valido. Ejemplo de salida esperada (fragmento):

  ;
  ; Archive created at 2026-09-01 ...
  ; ...
  TABLE DATA public venta ...

4. COMO RESTAURAR UN BACKUP
---------------------------
Opcion A: restaurar en una base de datos vacia (recomendado para probar).

  1. Crear una base vacia (por ejemplo para probar):
     createdb -h localhost -p 5433 -U admin hairsoft_restaurada

  2. Restaurar el backup sobre esa base:
     pg_restore -h localhost -p 5433 -U admin -d hairsoft_restaurada --no-owner ^
       "D:\Facultad\Trabajo final\HairSoft\backups\nombre_del_backup.backup"

Opcion B: restaurar sobre la base existente de HairSoft.

  IMPORTANTE: pg_restore NO borra datos previos. Para restaurar limpio,
  primero debes BORRAR el contenido actual (eso es irrecuperable), por eso
  se trabaja SIEMPRE sobre una base recien creada en entornos reales:

  1. Crear una base vacia:  createdb -h localhost -p 5433 -U admin hairsoft_nueva
  2. Restaurar:             pg_restore -h localhost -p 5433 -U admin ^
                              -d hairsoft_nueva --no-owner --verbose ^
                              "D:\Facultad\Trabajo final\HairSoft\backups\nombre_del_backup.backup"
  3. Cambiar el acceso de HairSoft a la base restaurada (ajustar
     hairsoft/settings.py) o reemplazar la base original por la restaurada.

  Nota: el password se pide interactivamente evitando que quede en el
  historial. En Windows, con el simbolo "^" se corta la linea; tambien
  podes escribir todo en una sola linea sin "^".

5. ESTRUCTURA DE CARPETAS
-------------------------
Se crea una estructura dinámica: una carpeta por anio y por mes, y dentro
tres subcarpetas por tipo de backup:

  backups\
    README.txt                      este archivo
    backup.log                      registro de cada backup generado
    scripts\                        herramientas de automatizacion
    hairsoft_2026-09-01.backup      backup de prueba (se conserva)
    2026\
      Septiembre\
        Dias\       backups diarios de ese mes
        Semanas\    backups semanales de ese mes
        Mensual\    backup mensual de ese mes

La estructura se crea sola para cualquier mes y cualquier anio. La cantidad
de dias de cada mes se calcula segun el calendario real (se usa la fecha del
sistema), por lo que tambien funciona correctamente en anios bisiestos.

6. POLITICA DE RETENCION
------------------------
Las copias viejas se eliminan automaticamente al generar una nueva:

  - Backup diario  : se conservan los ultimos 30 dias
  - Backup semanal : se conservan los ultimos 3 meses (90 dias)
  - Backup mensual : se conservan los ultimos 12 meses (365 dias)

7. EJECUCION MANUAL DEL BACKUP
------------------------------
El script principal es backups\scripts\backup_hairsoft.ps1. Acepta el parametro
-Tipo con los valores Diario, Semanal o Mensual. Se puede ejecutar desde
PowerShell o desde Git Bash en Windows.

### Ejecución desde PowerShell

Abre una terminal en la carpeta raiz del proyecto y ejecuta:

Para backup diario:

```powershell
.\backups\scripts\backup_hairsoft.ps1 -Tipo Diario
```

Para backup semanal:

```powershell
.\backups\scripts\backup_hairsoft.ps1 -Tipo Semanal
```

Para backup mensual:

```powershell
.\backups\scripts\backup_hairsoft.ps1 -Tipo Mensual
```

### Ejecución desde Git Bash

Git Bash no ejecuta directamente un archivo .ps1 con la sintaxis .\archivo.ps1:
los scripts .ps1 son de PowerShell y Bash no los interpreta. Para generarlo
desde Git Bash hay que invocar PowerShell de forma explicita:

Para backup diario:

```bash
powershell -ExecutionPolicy Bypass -File "./backups/scripts/backup_hairsoft.ps1" -Tipo Diario
```

Para backup semanal:

```bash
powershell -ExecutionPolicy Bypass -File "./backups/scripts/backup_hairsoft.ps1" -Tipo Semanal
```

Para backup mensual:

```bash
powershell -ExecutionPolicy Bypass -File "./backups/scripts/backup_hairsoft.ps1" -Tipo Mensual
```

Simplificacion desde Windows: en lugar de escribir el comando manual, se puede
usar backups\scripts\ejecutar_backup.bat, que llama a PowerShell por vos
(solo agrega el tipo al final):

  .\backups\scripts\ejecutar_backup.bat Diario    (o Semanal, o Mensual)

8. FRECUENCIA DE GENERACION
---------------------------
Las tareas de Windows (Programador de tareas) que se instalan con
backups\scripts\instalar_tareas.ps1 generan:

  - Un backup diario: todos los dias a las 02:00
  - Un backup semanal: todos los domingos a las 03:00
  - Un backup mensual: el dia 1 de cada mes a las 04:00

Para generar un backup a mano (sin esperar la tarea):

  .\backups\scripts\ejecutar_backup.bat Diario    (o Semanal, o Mensual)

O directamente con PowerShell:

  powershell -File ".\backups\scripts\backup_hairsoft.ps1" -Tipo Diario

Los horarios se pueden cambiar en el Programador de tareas de Windows.

9. QUE HACER SI UN BACKUP FALLA
-------------------------------
Cada ejecucion deja un registro en backups\backup.log con la fecha, el tipo
y el resultado (OK, RETENCIÓN o ERROR). Si un backup falla:

  - Abrir backups\backup.log y buscar la linea ERROR mas reciente.
  - Verificar que PostgreSQL este corriendo (que el servicio postgresql
    este iniciado y escuchando en localhost:5433).
  - Verificar credenciales (usuario admin y password). El script usa la
    variable de entorno PGPASSWORD o el parametro -Password.
  - Verificar que pg_dump este instalado (suele estar en
    "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe").
  - Repetir la generacion con el lanzador manual. Si sigue fallando,
    contactar al administrador del sistema con el log a mano.

10. GIT: NO SUBIR LOS BACKUPS AL REPOSITORIO
-------------------------------------------
La carpeta backups/ esta excluida en el archivo .gitignore. Los backups
contienen datos de clientes, ventas y pagos y NUNCA deben subirse a Git.
La documentacion y los scripts de backup tampoco se versionan: git evita
toda la carpeta backups/.

11. MEDIO SEPARADO EN ENTORNOS REALES
-------------------------------------
En un entorno real, las copias de seguridad deben mantenerse en un medio
separado del sistema original (disco externo, servidor de respaldo, servicio
en la nube, etc.). Si el equipo falla, una copia guardada en el mismo disco
se pierde junto con el sistema. Este procedimiento esta pensado para
ejecutarse en el entorno local de desarrollo; para produccion, ademas, hay
que trasladar las copias a otro medio y guardar el password de PostgreSQL de
forma segura (variable de entorno, no en texto plano).