import pytest
from unittest.mock import patch
from datetime import datetime, date, time, timedelta, timezone as dt_timezone
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from usuarios.factories import UsuarioFactory, ServicioFactory
from usuarios.models import Turno
from usuarios.turno_service import TurnoService
import pytz

ARG_TZ = pytz.timezone('America/Argentina/Buenos_Aires')

# 2026-09-06 15:00 UTC = 2026-09-06 12:00 hs Argentina
NOW_ARG = datetime(2026, 9, 6, 12, 0, 0)
NOW_UTC = datetime(2026, 9, 6, 15, 0, 0, tzinfo=dt_timezone.utc)


def _hoy():
    return NOW_ARG.date()


def _crear_turno(peluquero, fecha, hora=time(10, 0), estado='RESERVADO'):
    turno = Turno.objects.create(
        fecha=fecha,
        hora=hora,
        peluquero=peluquero,
        estado=estado,
        tipo_pago='TOTAL',
        monto_total=2000,
    )
    return turno


def _token_cliente(user):
    return Token.objects.create(user=user).key


@pytest.fixture
def _fix_base():
    from usuarios.models import Silla
    Silla.objects.create(nombre="Silla 1", orden=1)
    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    admin = UsuarioFactory(rol__nombre='Administrador')
    servicio = ServicioFactory(duracion=30)
    return {'peluquero': peluquero, 'admin': admin, 'servicio': servicio}


# =============================================================================
# MODIFICAR turno pasados (backend) - sin bypass por rol
# =============================================================================

@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_modificar_turno_de_ayer_rechazado_admin(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() - timedelta(days=1))
    client = APIClient()
    url = f'/api/turnos/{turno.id}/modificar/'
    res = client.post(
        url,
        data={'fecha': str(turno.fecha), 'hora': str(turno.hora)},
        format='json',
        HTTP_AUTHORIZATION=f"Token {_token_cliente(_fix_base['admin'])}",
    )
    assert res.status_code == 400
    assert 'fecha ya pasó' in res.json().get('error', '')
    turno.refresh_from_db()
    assert turno.estado == 'RESERVADO'


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_modificar_turno_de_hace_varios_dias_rechazado_admin(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() - timedelta(days=4))
    client = APIClient()
    res = client.post(
        f'/api/turnos/{turno.id}/modificar/',
        data={'fecha': str(turno.fecha), 'hora': str(turno.hora)},
        format='json',
        HTTP_AUTHORIZATION=f"Token {_token_cliente(_fix_base['admin'])}",
    )
    assert res.status_code == 400
    assert 'fecha ya pasó' in res.json().get('error', '')


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_modificar_turno_pasado_rechazado_peluquero(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() - timedelta(days=1))
    client = APIClient()
    res = client.post(
        f'/api/turnos/{turno.id}/modificar/',
        data={'fecha': str(turno.fecha), 'hora': str(turno.hora)},
        format='json',
        HTTP_AUTHORIZATION=f"Token {_token_cliente(_fix_base['peluquero'])}",
    )
    assert res.status_code == 400
    assert 'fecha ya pasó' in res.json().get('error', '')


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_modificar_turno_de_hoy_con_hora_pasada_permitido(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy(), hora=time(8, 0))
    client = APIClient()
    res = client.post(
        f'/api/turnos/{turno.id}/modificar/',
        data={'fecha': str(turno.fecha), 'hora': str(turno.hora)},
        format='json',
        HTTP_AUTHORIZATION=f"Token {_token_cliente(_fix_base['admin'])}",
    )
    assert res.status_code == 200
    assert res.json().get('status') == 'ok'


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_modificar_turno_futuro_permitido(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() + timedelta(days=1))
    client = APIClient()
    res = client.post(
        f'/api/turnos/{turno.id}/modificar/',
        data={'fecha': str(turno.fecha), 'hora': str(turno.hora)},
        format='json',
        HTTP_AUTHORIZATION=f"Token {_token_cliente(_fix_base['admin'])}",
    )
    assert res.status_code == 200
    assert res.json().get('status') == 'ok'


# =============================================================================
# CANCELAR turnos pasados (backend) - la protección se mantiene
# =============================================================================

@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_cancelar_turno_de_ayer_rechazado(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() - timedelta(days=1))
    success, message = TurnoService.procesar_cancelacion_automatica(
        turno.id, usuario_cancelacion=_fix_base['admin'], motivo='test'
    )
    assert success is False
    assert 'fecha ya pasó' in message
    turno.refresh_from_db()
    assert turno.estado == 'RESERVADO'


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_cancelar_turno_de_hace_varios_dias_rechazado(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() - timedelta(days=4))
    success, message = TurnoService.procesar_cancelacion_automatica(
        turno.id, usuario_cancelacion=_fix_base['admin'], motivo='test'
    )
    assert success is False
    assert 'fecha ya pasó' in message


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_cancelar_turno_de_hoy_con_hora_pasada_permitido(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy(), hora=time(8, 0))
    success, message = TurnoService.procesar_cancelacion_automatica(
        turno.id, usuario_cancelacion=_fix_base['admin'], motivo='test'
    )
    assert success is True
    turno.refresh_from_db()
    assert turno.estado == 'CANCELADO'


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_cancelar_turno_futuro_permitido(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() + timedelta(days=1))
    success, message = TurnoService.procesar_cancelacion_automatica(
        turno.id, usuario_cancelacion=_fix_base['admin'], motivo='test'
    )
    assert success is True
    turno.refresh_from_db()
    assert turno.estado == 'CANCELADO'


# =============================================================================
# COMPLETAR turnos pasados - debe seguir funcionando
# =============================================================================

@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_completar_turno_pasado_reservado_permitido(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() - timedelta(days=1))
    client = APIClient()
    client.force_authenticate(user=_fix_base['admin'])
    res = client.post(f'/api/turnos/{turno.id}/cambiar-estado/COMPLETADO/')
    assert res.status_code == 200
    assert res.json().get('status') == 'ok'
    turno.refresh_from_db()
    assert turno.estado == 'COMPLETADO'


@pytest.mark.django_db
@patch.object(timezone, 'now', return_value=NOW_UTC)
def test_turno_pasado_reservado_no_cambia_solo(_mock, _fix_base):
    turno = _crear_turno(_fix_base['peluquero'], _hoy() - timedelta(days=2))
    turno.refresh_from_db()
    assert turno.estado == 'RESERVADO'
    assert Turno.objects.filter(id=turno.id, estado='RESERVADO').exists()