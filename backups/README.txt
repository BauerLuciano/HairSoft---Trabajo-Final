========================================
COPIAS DE SEGURIDAD DE HAIRSOFT
========================================

1. ¿QUÉ ES UN BACKUP?

---

Un backup es una copia de la base de datos PostgreSQL de HairSoft.
Se genera en formato CUSTOM (.backup) mediante pg_dump.

Los archivos .backup son binarios y no deben abrirse ni modificarse con
un editor de texto.

2. ESTRUCTURA DE CARPETAS

---

La carpeta de backups se organiza automáticamente por año, mes y tipo:

backups/
├── README.txt
├── backup.log
├── scripts/
│   ├── backup_hairsoft.ps1
│   ├── ejecutar_backup.bat
│   └── instalar_tareas.ps1
└── 2026/
    └── Septiembre/
        ├── Dias/
        │   └── hairsoft_2026-09-01.backup
        ├── Semanas/
        │   └── hairsoft_2026-09-01.backup
        └── Mensual/
            └── hairsoft_2026-09.backup

La estructura se genera automáticamente según la fecha del sistema, por
lo que funciona correctamente con meses de distinta duración y años
bisiestos.

3. RETENCIÓN

---

Diario   → 30 días
Semanal  → 90 días
Mensual  → 365 días

Las copias que superan estos períodos se eliminan automáticamente.

4. BACKUP MANUAL

---

El backup manual puede ejecutarse de tres formas: desde Git Bash, desde
PowerShell o mediante el archivo ejecutar_backup.bat.

Desde Git Bash, ubicado en la raíz del proyecto:

  powershell -ExecutionPolicy Bypass -File "./backups/scripts/backup_hairsoft.ps1" -Tipo Diario

  powershell -ExecutionPolicy Bypass -File "./backups/scripts/backup_hairsoft.ps1" -Tipo Semanal

  powershell -ExecutionPolicy Bypass -File "./backups/scripts/backup_hairsoft.ps1" -Tipo Mensual

Desde PowerShell, ubicado en la raíz del proyecto:

  .\backups\scripts\backup_hairsoft.ps1 -Tipo Diario

  .\backups\scripts\backup_hairsoft.ps1 -Tipo Semanal

  .\backups\scripts\backup_hairsoft.ps1 -Tipo Mensual

También se puede utilizar ejecutar_backup.bat desde CMD o directamente
desde el Explorador de Windows:

  backups\scripts\ejecutar_backup.bat Diario
  backups\scripts\ejecutar_backup.bat Semanal
  backups\scripts\ejecutar_backup.bat Mensual

La ejecución manual del backup no requiere iniciar la terminal como
Administrador.

5. AUTOMATIZACIÓN DE WINDOWS

---

El archivo instalar_tareas.ps1 registra tres tareas automáticas en el
Programador de tareas de Windows:

  Diario   → todos los días a las 02:00
  Semanal  → todos los domingos a las 03:00
  Mensual  → día 1 de cada mes a las 04:00

Para instalar las tareas automáticas:

1. Abrir Git Bash o PowerShell como Administrador.
2. Ubicarse en la raíz del proyecto.
3. Ejecutar el script correspondiente.

Desde Git Bash:

  powershell -ExecutionPolicy Bypass -File "./backups/scripts/instalar_tareas.ps1"

Desde PowerShell:

  .\backups\scripts\instalar_tareas.ps1

La instalación se realiza una sola vez. Una vez registradas las tareas,
Windows ejecutará los backups automáticamente según los horarios
establecidos.

6. VERIFICAR UN BACKUP

---

Para comprobar que un backup puede leerse correctamente:

  pg_restore -l "ruta\al\archivo.backup"

Si muestra el contenido sin errores, el backup es válido.

7. RESTAURAR UN BACKUP

---

Se recomienda restaurarlo primero en una base de datos nueva:

  createdb -h localhost -p 5433 -U admin hairsoft_restaurada

  pg_restore -h localhost -p 5433 -U admin -d hairsoft_restaurada --no-owner "ruta\al\archivo.backup"

8. SI UN BACKUP FALLA

---

Revisar:

* backups/backup.log
* que PostgreSQL esté funcionando
* que pg_dump esté instalado
* que los datos de conexión sean correctos

9. ALMACENAMIENTO

---

Las copias de seguridad deben conservarse también en una ubicación
separada del equipo o sistema principal, para reducir el riesgo de
perderlas ante una falla del equipo.

La ubicación separada puede ser, por ejemplo, otra unidad o disco,
un pendrive, un disco externo o cualquier otro medio de almacenamiento
adecuado.

Después de generar una copia, se debe trasladar o copiar a dicha
ubicación separada.