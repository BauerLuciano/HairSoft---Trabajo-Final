import os
import time
from datetime import datetime

import pytest
from rest_framework.test import APIClient

from usuarios import backup_service
from usuarios.backup_service import TIPOS_VALIDOS, listar_backups, resumen_backups
from usuarios.factories import UsuarioFactory


@pytest.fixture
def dir_backups(tmp_path, monkeypatch):
    """Crea una estructura backups/<Año>/<Mes>/<carpeta> y apunta BACKUP_DIR ahí."""
    monkeypatch.setattr(backup_service, 'BACKUP_DIR', tmp_path)
    return tmp_path


def _crear_backup(dir_backups, tipo, nombre, mtime_local):
    """Crea un .backup ficticio (solo metadata, no es un dump real)."""
    carpeta = TIPOS_VALIDOS[tipo]
    destino = dir_backups / '2026' / 'Septiembre' / carpeta
    destino.mkdir(parents=True, exist_ok=True)
    archivo = destino / nombre
    archivo.write_bytes(b'fake-backup-data')
    mtime = time.mktime(mtime_local.timetuple())
    os.utime(archivo, (mtime, mtime))
    return archivo


@pytest.mark.django_db
def test_listar_backups_usa_fecha_hora_real(dir_backups):
    """La fecha/hora sale de la metadata del archivo, no del nombre."""
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 20, 20, 43))
    _crear_backup(dir_backups, 'Semanal', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 20, 43, 5))
    _crear_backup(dir_backups, 'Mensual', 'hairsoft_2026-09.backup', datetime(2026, 9, 1, 19, 29, 22))

    backups = listar_backups()

    assert len(backups) == 3
    por_tipo = {b['tipo']: b for b in backups}
    assert por_tipo['Diario']['fecha'] == '2026-09-01T20:20:43'
    assert por_tipo['Semanal']['fecha'] == '2026-09-01T20:43:05'
    assert por_tipo['Mensual']['fecha'] == '2026-09-01T19:29:22'


@pytest.mark.django_db
def test_listar_backups_no_muestra_medianoche(dir_backups):
    """Regresión: antes todos aparecían como T00:00:00 (12:00 a. m.)."""
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 2, 0, 7))
    _crear_backup(dir_backups, 'Mensual', 'hairsoft_2026-09.backup', datetime(2026, 9, 1, 4, 0, 0))

    backups = listar_backups()
    assert all(b['fecha'] and not b['fecha'].endswith('T00:00:00') for b in backups)
    assert {b['tipo']: b['fecha'] for b in backups}['Diario'] == '2026-09-01T02:00:07'


@pytest.mark.django_db
def test_fecha_es_hora_local_sin_conversion_de_zona(dir_backups):
    """fromtimestamp devuelve datetime naive (hora local de Windows),
    sin sufijo Z ni +HH:MM que el frontend interpretaría como otra zona."""
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 2, 0, 0))

    backups = listar_backups()
    fecha = backups[0]['fecha']
    assert fecha == '2026-09-01T02:00:00'
    assert 'Z' not in fecha and '+' not in fecha
    # El objeto original es naive (local), sin timezone offset
    d = [b for b in backups][0]
    st = (dir_backups / '2026' / 'Septiembre' / 'Dias' / 'hairsoft_2026-09-01.backup').stat()
    f_dt = datetime.fromtimestamp(st.st_mtime)
    assert f_dt.tzinfo is None


@pytest.mark.django_db
def test_orden_descendente_por_fecha_hora_real(dir_backups):
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-03.backup', datetime(2026, 9, 3, 2, 0, 0))
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 22, 15, 0))
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-02.backup', datetime(2026, 9, 2, 2, 0, 0))

    backups = listar_backups()
    fechas = [b['fecha'] for b in backups]
    assert fechas == sorted(fechas, reverse=True)
    assert backups[0]['nombre'] == 'hairsoft_2026-09-03.backup'


@pytest.mark.django_db
def test_excluye_archivos_con_nombre_invalido(dir_backups):
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 20, 20, 43))
    (dir_backups / '2026' / 'Septiembre' / 'Dias' / 'otro_archivo.backup').write_bytes(b'x')
    (dir_backups / '2026' / 'Septiembre' / 'Dias' / 'hairsoft_2026.backup').write_bytes(b'x')

    assert len(listar_backups()) == 1


@pytest.mark.django_db
def test_resumen_usa_el_ultimo_backup_real_por_tipo(dir_backups):
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 2, 0, 0))
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-02.backup', datetime(2026, 9, 2, 2, 0, 5))
    _crear_backup(dir_backups, 'Mensual', 'hairsoft_2026-09.backup', datetime(2026, 9, 1, 4, 0, 0))

    backups = listar_backups()
    resumen = resumen_backups(backups)

    assert resumen['total_copias'] == 3
    assert resumen['ultimos']['Diario']['fecha'] == '2026-09-02T02:00:05'
    assert resumen['ultimos']['Diario']['cantidad'] == 2
    assert resumen['ultimos']['Mensual']['fecha'] == '2026-09-01T04:00:00'
    assert isinstance(resumen['tamano_total_bytes'], int) and resumen['tamano_total_bytes'] > 0


@pytest.mark.django_db
def test_api_listado_backups_devuelve_fecha_hora_real(dir_backups):
    _crear_backup(dir_backups, 'Diario', 'hairsoft_2026-09-01.backup', datetime(2026, 9, 1, 20, 20, 43))
    admin = UsuarioFactory(rol__nombre='Administrador')
    client = APIClient()
    client.force_authenticate(user=admin)

    res = client.get('/api/backups/')
    assert res.status_code == 200
    assert res.data['backups'][0]['fecha'] == '2026-09-01T20:20:43'
    assert res.data['ultimos']['Diario']['fecha'] == '2026-09-01T20:20:43'


@pytest.mark.django_db
def test_api_listado_backups_deniega_a_no_admin():
    cliente = UsuarioFactory(rol__nombre='Cliente')
    client = APIClient()
    client.force_authenticate(user=cliente)

    res = client.get('/api/backups/')
    assert res.status_code == 403


@pytest.mark.django_db
def test_api_listado_backups_requiere_autenticacion():
    client = APIClient()
    res = client.get('/api/backups/')
    assert res.status_code in (401, 403)