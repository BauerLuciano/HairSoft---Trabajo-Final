import pytest
from unittest.mock import patch
from datetime import datetime, date, time
from django.utils import timezone
from rest_framework.test import APIClient
from usuarios.factories import UsuarioFactory, ServicioFactory
from usuarios.models import Caja, SesionCaja, Turno, ConfiguracionSistema
import pytz

@pytest.mark.django_db
def test_no_permitir_turnos_solapados():
    client = APIClient()

    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    cliente = UsuarioFactory(rol__nombre='Cliente')
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol__nombre='Administrador')
    client.force_authenticate(user=admin)

    caja = Caja.objects.create(nombre="Caja Test")
    SesionCaja.objects.create(caja=caja, usuario_apertura=admin, saldo_inicial_efectivo=0)

    url = '/api/turnos/crear/'
    data = {
        "canal": "PRESENCIAL",
        "cliente_id": cliente.id,
        "peluquero_id": peluquero.id,
        "servicios_ids": [servicio.id],
        "fecha": "2026-05-11",
        "hora": "10:00",
        "tipo_pago": "TOTAL",
        "medio_pago": "EFECTIVO"
    }

    res1 = client.post(url, data, format='json')
    assert res1.status_code == 201, f"Error creando primer turno: {res1.data}"

    data_solapada = data.copy()
    data_solapada["hora"] = "10:15"
    res2 = client.post(url, data_solapada, format='json')

    assert res2.status_code == 400
    assert "Horario ocupado" in res2.data['message']


@pytest.mark.django_db
def test_cancelar_turno_segun_margen():
    config = ConfiguracionSistema.get_solo()
    config.margen_horas_cancelacion = 3
    config.save()

    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    servicio = ServicioFactory(duracion=30)

    turno = Turno.objects.create(
        fecha=date(2026, 6, 8),
        hora=time(10, 0),
        peluquero=peluquero,
        estado='RESERVADO',
        tipo_pago='TOTAL',
        monto_seña=1000,
        monto_total=2000,
    )
    turno.servicios.set([servicio])

    mock_1h_antes = datetime(2026, 6, 8, 12, 0, 0, tzinfo=pytz.utc)
    with patch.object(timezone, 'now', return_value=mock_1h_antes):
        puede, reembolso, msg = turno.puede_ser_cancelado()
        assert puede == True
        assert reembolso == False
        assert "Fuera de término" in msg

    mock_25h_antes = datetime(2026, 6, 7, 12, 0, 0, tzinfo=pytz.utc)
    with patch.object(timezone, 'now', return_value=mock_25h_antes):
        puede, reembolso, msg = turno.puede_ser_cancelado()
        assert puede == True
        assert reembolso == True
        assert "Reembolso habilitado" in msg

@pytest.mark.django_db
def test_calcular_comision_peluquero():
    peluquero = UsuarioFactory(rol__nombre='Peluquero')

    srv_a = ServicioFactory(precio=1000, duracion=30, porcentaje_comision=10)
    srv_b = ServicioFactory(precio=500, duracion=30, porcentaje_comision=20)
    srv_c = ServicioFactory(precio=800, duracion=30, porcentaje_comision=0)

    turno = Turno.objects.create(
        fecha=date(2026, 6, 10),
        hora=time(10, 0),
        peluquero=peluquero,
        estado='RESERVADO',
        tipo_pago='TOTAL',
        monto_total=2000,
    )

    # Caso 1: un servicio con 10%
    turno.servicios.set([srv_a])
    assert turno.calcular_comision_peluquero() == 100.0

    # Caso 2: un servicio con 0%
    turno.servicios.set([srv_c])
    assert turno.calcular_comision_peluquero() == 0.0

    # Caso 3: múltiples servicios (10% de 1000 + 20% de 500 = 200)
    turno.servicios.set([srv_a, srv_b])
    assert turno.calcular_comision_peluquero() == 200.0

@pytest.mark.django_db
def test_asignar_silla_disponible():
    from usuarios.turno_service import TurnoService
    from usuarios.models import Silla

    silla1 = Silla.objects.create(nombre="Silla 1", orden=1)
    silla2 = Silla.objects.create(nombre="Silla 2", orden=2)
    silla3 = Silla.objects.create(nombre="Silla 3", orden=3)

    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    servicio = ServicioFactory(duracion=30)

    # Caso 1: todas ocupadas → None
    for s in [silla1, silla2, silla3]:
        t = Turno.objects.create(
            fecha=date(2026, 6, 10), hora=time(10, 0),
            peluquero=peluquero, estado='RESERVADO',
            tipo_pago='TOTAL', silla=s
        )
        t.servicios.set([servicio])

    assert TurnoService._asignar_silla_disponible(date(2026, 6, 10), time(10, 0)) is None

    # Caso 2: silla3 libre → debe devolver silla3 (primera libre por orden)
    silla3_turno = Turno.objects.get(silla=silla3)
    silla3_turno.estado = 'CANCELADO'
    silla3_turno.save()

    silla_asignada = TurnoService._asignar_silla_disponible(date(2026, 6, 10), time(10, 0))
    assert silla_asignada is not None
    assert silla_asignada.id == silla3.id

@pytest.mark.django_db
def test_turno_presencial_sin_caja():
    client = APIClient()

    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    cliente = UsuarioFactory(rol__nombre='Cliente')
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol__nombre='Administrador')
    client.force_authenticate(user=admin)

    # NO se crea Caja ni SesionCaja

    url = '/api/turnos/crear/'
    data = {
        "canal": "PRESENCIAL",
        "cliente_id": cliente.id,
        "peluquero_id": peluquero.id,
        "servicios_ids": [servicio.id],
        "fecha": "2026-05-11",
        "hora": "10:00",
        "tipo_pago": "TOTAL",
        "medio_pago": "EFECTIVO"
    }

    res = client.post(url, data, format='json')
    assert res.status_code == 400
    assert "Debe abrir una caja" in res.data['error']

@pytest.mark.django_db
def test_turno_cliente_duplicado_misma_fecha_hora():
    client = APIClient()

    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    cliente = UsuarioFactory(rol__nombre='Cliente')
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol__nombre='Administrador')
    client.force_authenticate(user=admin)

    caja = Caja.objects.create(nombre="Caja Test")
    SesionCaja.objects.create(caja=caja, usuario_apertura=admin, saldo_inicial_efectivo=0)

    url = '/api/turnos/crear/'
    data = {
        "canal": "PRESENCIAL",
        "cliente_id": cliente.id,
        "peluquero_id": peluquero.id,
        "servicios_ids": [servicio.id],
        "fecha": "2026-05-11",
        "hora": "10:00",
        "tipo_pago": "TOTAL",
        "medio_pago": "EFECTIVO"
    }

    # Primer turno → debe crear
    res1 = client.post(url, data, format='json')
    assert res1.status_code == 201

    # Segundo turno mismo cliente/misma fecha/hora → debe rechazar
    res2 = client.post(url, data, format='json')
    assert res2.status_code == 400
    assert "Ya tienes un turno reservado" in str(res2.data.get('message', ''))

@pytest.mark.django_db
def test_turno_silla_manual_ocupada():
    from usuarios.models import Silla, Rol

    client = APIClient()

    silla1 = Silla.objects.create(nombre="Silla 1", orden=1)
    silla2 = Silla.objects.create(nombre="Silla 2", orden=2)

    rol_peluquero = Rol.objects.create(nombre='Peluquero')
    rol_cliente = Rol.objects.create(nombre='Cliente')
    rol_admin = Rol.objects.create(nombre='Administrador')

    peluquero_a = UsuarioFactory(rol=rol_peluquero)
    peluquero_b = UsuarioFactory(rol=rol_peluquero)
    cliente = UsuarioFactory(rol=rol_cliente)
    cliente2 = UsuarioFactory(rol=rol_cliente)
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol=rol_admin)
    client.force_authenticate(user=admin)

    caja = Caja.objects.create(nombre="Caja Test")
    SesionCaja.objects.create(caja=caja, usuario_apertura=admin, saldo_inicial_efectivo=0)

    url = '/api/turnos/crear/'

    data1 = {
        "canal": "PRESENCIAL",
        "cliente_id": cliente.id,
        "peluquero_id": peluquero_a.id,
        "servicios_ids": [servicio.id],
        "fecha": "2026-05-11",
        "hora": "10:00",
        "silla_id": silla1.id,
        "tipo_pago": "TOTAL",
        "medio_pago": "EFECTIVO"
    }
    res1 = client.post(url, data1, format='json')
    assert res1.status_code == 201

    data2 = {
        "canal": "PRESENCIAL",
        "cliente_id": cliente2.id,
        "peluquero_id": peluquero_b.id,
        "servicios_ids": [servicio.id],
        "fecha": "2026-05-11",
        "hora": "10:00",
        "silla_id": silla1.id,
        "tipo_pago": "TOTAL",
        "medio_pago": "EFECTIVO"
    }
    res2 = client.post(url, data2, format='json')
    assert res2.status_code == 400
    assert "silla" in res2.data.get('message', '').lower()