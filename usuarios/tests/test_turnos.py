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