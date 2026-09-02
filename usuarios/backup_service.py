import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings

# =========================================================================
# Servicio de copias de seguridad
# -------------------------------------------------------------------------
# Expone funciones puras para listar, generar, verificar y descargar las
# copias que produce backups/scripts/backup_hairsoft.ps1 (formato CUSTOM).
# No modifica el script: lo invoca tal cual, igual que la tarea programada.
# =========================================================================

TIPOS_VALIDOS = {'Diario': 'Dias', 'Semanal': 'Semanas', 'Mensual': 'Mensual'}
MESES_ESPANOL = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
RETENCION_DIAS = {'Diario': 30, 'Semanal': 90, 'Mensual': 365}

BACKUP_DIR = Path(settings.BASE_DIR) / 'backups'
BACKUP_SCRIPT = BACKUP_DIR / 'scripts' / 'backup_hairsoft.ps1'
LOG_FILE = BACKUP_DIR / 'backup.log'


def _parsear_fecha(nombre):
    """Extrae la fecha de un nombre de copia (hairsoft_YYYY-MM-DD.backup o
    hairsoft_YYYY-MM.backup para las mensuales)."""
    if not nombre.startswith('hairsoft_'):
        return None
    base = nombre[len('hairsoft_'):].rsplit('.', 1)[0]
    for fmt in ('%Y-%m-%d', '%Y-%m'):
        try:
            return datetime.strptime(base, fmt)
        except ValueError:
            continue
    return None


def _serializar_archivo(archivo, tipo):
    """Fecha/hora REAL de generación tomada de la metadata del archivo
    (st_mtime) en hora local de Windows. No se aplica ninguna conversión de
    zona horaria para no alterar la hora local."""
    st = archivo.stat()
    return {
        'nombre': archivo.name,
        'ruta': archivo.relative_to(BACKUP_DIR).as_posix(),
        'tipo': tipo,
        'fecha': datetime.fromtimestamp(st.st_mtime).isoformat(),
        'tamano_bytes': st.st_size,
    }


def listar_backups():
    """Devuelve todas las copias organizadas bajo backups\Año\Mes\{...},
    excluyendo archivos fuera de la estructura de retención."""
    backups = []
    for archivo in BACKUP_DIR.rglob('hairsoft_*.backup'):
        if not archivo.is_file():
            continue
        carpeta = archivo.parent.name
        tipo = next((t for t, c in TIPOS_VALIDOS.items() if c == carpeta), None)
        if tipo is None:
            continue
        if _parsear_fecha(archivo.name) is None:
            continue
        backups.append(_serializar_archivo(archivo, tipo))
    backups.sort(key=lambda b: (b['fecha'] or ''), reverse=True)
    return backups


def resumen_backups(backups):
    """Resumen para las tarjetas de la UI: último backup y cantidad por tipo."""
    por_tipo = {}
    for b in backups:
        por_tipo.setdefault(b['tipo'], []).append(b)

    ultimos = {}
    for tipo in TIPOS_VALIDOS:
        lista = por_tipo.get(tipo, [])
        ultimos[tipo] = {
            'nombre': lista[0]['nombre'] if lista else None,
            'fecha': lista[0]['fecha'] if lista else None,
            'cantidad': len(lista),
            'retencion_dias': RETENCION_DIAS[tipo],
        }

    return {
        'total_copias': len(backups),
        'tamano_total_bytes': sum(b['tamano_bytes'] for b in backups),
        'ultimos': ultimos,
    }


def generar_backup(tipo):
    """Dispare backup_hairsoft.ps1 para un tipo y devuelve el resultado."""
    if tipo not in TIPOS_VALIDOS:
        raise ValueError("Tipo inválido. Use 'Diario', 'Semanal' o 'Mensual'.")
    if not BACKUP_SCRIPT.is_file():
        raise RuntimeError(f'No se encontró el script de backup: {BACKUP_SCRIPT}')

    cmd = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
           '-File', str(BACKUP_SCRIPT), '-Tipo', tipo]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=180)

    salida = (proc.stderr.strip() or proc.stdout.strip()) or 'El script no devolvió salida.'
    resultado = {
        'ok': proc.returncode == 0,
        'tipo': tipo,
        'returncode': proc.returncode,
        'salida': _acotar(salida),
        'archivo': None,
    }
    if proc.returncode == 0:
        resultado['archivo'] = _backup_recien_generado(tipo)
    else:
        resultado['error'] = _acotar(salida)
    return resultado


def _backup_recien_generado(tipo):
    hoy = datetime.now()
    if tipo == 'Mensual':
        nombre = hoy.strftime('hairsoft_%Y-%m.backup')
    else:
        nombre = hoy.strftime('hairsoft_%Y-%m-%d.backup')
    carpeta = BACKUP_DIR / str(hoy.year) / MESES_ESPANOL[hoy.month - 1] / TIPOS_VALIDOS[tipo]
    archivo = carpeta / nombre
    if archivo.is_file():
        return _serializar_archivo(archivo, tipo)
    return None


def verificar_backup(ruta):
    """Verifica una copia con pg_restore -l (lee el listado TOC)."""
    archivo = resolver_ruta_backup(ruta)
    pg_restore = _localizar_pg_tool('pg_restore.exe')
    if pg_restore is None:
        raise RuntimeError('No se encontró pg_restore. Instalá PostgreSQL o agregá sus binarios al PATH.')

    proc = subprocess.run([str(pg_restore), '-l', str(archivo)],
                          capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=120)
    if proc.returncode == 0:
        entradas = len([l for l in proc.stdout.splitlines() if l.strip()])
        return {
            'ok': True,
            'archivo': archivo.name,
            'entradas': entradas,
            'detalle': 'Backup válido: el listado TOC se lee correctamente.',
        }
    error = proc.stderr.strip() or proc.stdout.strip()
    return {
        'ok': False,
        'archivo': archivo.name,
        'error': _acotar(error),
        'detalle': 'No se pudo verificar el backup: posible archivo corrupto o no compatible.',
    }


def leer_log(lineas_max=25):
    """Últimas líneas de backup.log, tal como las escribe backup_hairsoft.ps1."""
    if not LOG_FILE.is_file():
        return []
    try:
        contenido = LOG_FILE.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return []
    contenido = contenido.replace('\ufeff', '')
    return contenido.splitlines()[-lineas_max:]


def resolver_ruta_backup(ruta):
    """Valida que ruta apunte a un .backup dentro de backups/ y lo devuelve."""
    try:
        destino = (BACKUP_DIR / ruta).resolve()
        raiz = BACKUP_DIR.resolve()
    except (OSError, ValueError):
        raise ValueError('Ruta de backup no válida.')
    try:
        dentro = os.path.commonpath([str(destino), str(raiz)]) == str(raiz)
    except ValueError:
        dentro = False
    if not dentro:
        raise ValueError('Ruta fuera del directorio de backups.')
    if destino.suffix != '.backup' or not destino.name.startswith('hairsoft_'):
        raise ValueError('Nombre de archivo de backup no válido.')
    if not destino.is_file():
        raise ValueError('Archivo de backup no encontrado.')
    return destino


def _localizar_pg_tool(nombre):
    encontrado = shutil.which(nombre)
    if encontrado:
        return Path(encontrado)
    base = Path(r'C:\Program Files\PostgreSQL')
    if base.is_dir():
        candidatos = sorted(base.glob(f'*/bin/{nombre}'),
                            key=lambda p: p.parent.parent.name, reverse=True)
        if candidatos:
            return candidatos[0]
    return None


def _acotar(texto, max_chars=500):
    if not texto:
        return ''
    return texto if len(texto) <= max_chars else texto[:max_chars] + '…'