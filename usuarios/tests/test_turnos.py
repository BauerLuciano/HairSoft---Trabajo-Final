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
    from usuarios.models import Silla
    Silla.objects.create(nombre="Silla 1", orden=1)
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
    from usuarios.models import Silla
    Silla.objects.create(nombre="Silla 1", orden=1)
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
    assert res2.data.get('code') == 'CLIENTE_YA_TIENE_TURNO'
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
    assert res2.data.get('code') == 'SILLA_OCUPADA'
    assert "silla" in res2.data.get('message', '').lower()


# =============================================================================
# 🔥 CAPACIDAD REAL = min(peluqueros libres, sillas libres)
# Regla final: un turno SIEMPRE requiere 1 peluquero + 1 silla.
# Nunca crear un turno con silla=None.
# =============================================================================

def _crear_caja(admin):
    caja = Caja.objects.create(nombre="Caja Test")
    SesionCaja.objects.create(caja=caja, usuario_apertura=admin, saldo_inicial_efectivo=0)


@pytest.fixture
def _roles_turnos():
    from usuarios.models import Rol
    return {
        'peluquero': Rol.objects.create(nombre='Peluquero'),
        'cliente': Rol.objects.create(nombre='Cliente'),
        'admin': Rol.objects.create(nombre='Administrador'),
    }


@pytest.fixture
def _turno_payload():
    def _build(cliente, peluquero, servicio):
        return {
            "canal": "PRESENCIAL",
            "cliente_id": cliente.id,
            "peluquero_id": peluquero.id,
            "servicios_ids": [servicio.id],
            "fecha": "2026-07-20",
            "hora": "10:00",
            "tipo_pago": "TOTAL",
            "medio_pago": "EFECTIVO",
        }
    return _build


@pytest.mark.django_db
def test_capacidad_3_peluqueros_3_sillas_max_3_turnos(_roles_turnos, _turno_payload):
    from usuarios.models import Silla
    client = APIClient()
    [Silla.objects.create(nombre=f"Silla {i}", orden=i) for i in range(1, 4)]
    peluqueros = [UsuarioFactory(rol=_roles_turnos['peluquero']) for _ in range(3)]
    clientes = [UsuarioFactory(rol=_roles_turnos['cliente']) for _ in range(4)]
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol=_roles_turnos['admin'])
    client.force_authenticate(user=admin)
    _crear_caja(admin)

    url = '/api/turnos/crear/'
    for i in range(3):
        res = client.post(url, _turno_payload(clientes[i], peluqueros[i], servicio), format='json')
        assert res.status_code == 201, f"Turno {i+1} debería crearse: {res.data}"
        turno = Turno.objects.get(id=res.data['turno_id'])
        assert turno.silla_id is not None, "Todo turno creado debe tener silla asignada"

    assert Turno.objects.filter(fecha=date(2026, 7, 20), hora=time(10, 0)).count() == 3

    # 4to turno: no queda peluquero libre (peluquero[0] ya está ocupado)
    res = client.post(url, _turno_payload(clientes[3], peluqueros[0], servicio), format='json')
    assert res.status_code == 400
    assert Turno.objects.filter(fecha=date(2026, 7, 20), hora=time(10, 0)).count() == 3


@pytest.mark.django_db
def test_capacidad_3_peluqueros_2_sillas_max_2_turnos(_roles_turnos, _turno_payload):
    from usuarios.models import Silla
    client = APIClient()
    [Silla.objects.create(nombre=f"Silla {i}", orden=i) for i in range(1, 3)]  # 2 sillas
    peluqueros = [UsuarioFactory(rol=_roles_turnos['peluquero']) for _ in range(3)]  # 3 peluqueros
    clientes = [UsuarioFactory(rol=_roles_turnos['cliente']) for _ in range(3)]
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol=_roles_turnos['admin'])
    client.force_authenticate(user=admin)
    _crear_caja(admin)

    url = '/api/turnos/crear/'
    for i in range(2):
        res = client.post(url, _turno_payload(clientes[i], peluqueros[i], servicio), format='json')
        assert res.status_code == 201, f"Turno {i+1} debería crearse: {res.data}"
        assert Turno.objects.get(id=res.data['turno_id']).silla_id is not None

    # Tercer turno: peluquero libre pero NO hay silla libre → 400 y no se crea
    res = client.post(url, _turno_payload(clientes[2], peluqueros[2], servicio), format='json')
    assert res.status_code == 400, f"Debería rechazarse por falta de silla: {res.data}"
    assert Turno.objects.filter(fecha=date(2026, 7, 20), hora=time(10, 0)).count() == 2


@pytest.mark.django_db
def test_sin_silla_disponible_rechaza_y_no_crea(_roles_turnos, _turno_payload):
    from usuarios.models import Silla
    client = APIClient()
    Silla.objects.create(nombre="Silla 1", orden=1)  # 1 sola silla
    peluqueros = [UsuarioFactory(rol=_roles_turnos['peluquero']) for _ in range(2)]
    clientes = [UsuarioFactory(rol=_roles_turnos['cliente']) for _ in range(2)]
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol=_roles_turnos['admin'])
    client.force_authenticate(user=admin)
    _crear_caja(admin)

    url = '/api/turnos/crear/'
    res1 = client.post(url, _turno_payload(clientes[0], peluqueros[0], servicio), format='json')
    assert res1.status_code == 201
    assert Turno.objects.get(id=res1.data['turno_id']).silla_id is not None

    # Segundo turno: peluquero distinto libre, pero la única silla está ocupada
    res2 = client.post(url, _turno_payload(clientes[1], peluqueros[1], servicio), format='json')
    assert res2.status_code == 400
    assert res2.data.get('code') == 'SIN_SILLA_DISPONIBLE'
    assert "puestos" in res2.data.get('message', '').lower() or "local" in res2.data.get('message', '').lower()
    assert Turno.objects.filter(fecha=date(2026, 7, 20), hora=time(10, 0)).count() == 1


@pytest.mark.django_db
def test_sin_peluquero_disponible_rechaza_y_no_crea(_roles_turnos, _turno_payload):
    from usuarios.models import Silla
    client = APIClient()
    Silla.objects.create(nombre="Silla 1", orden=1)
    peluquero_a = UsuarioFactory(rol=_roles_turnos['peluquero'])
    clientes = [UsuarioFactory(rol=_roles_turnos['cliente']) for _ in range(2)]
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol=_roles_turnos['admin'])
    client.force_authenticate(user=admin)
    _crear_caja(admin)

    url = '/api/turnos/crear/'
    res1 = client.post(url, _turno_payload(clientes[0], peluquero_a, servicio), format='json')
    assert res1.status_code == 201

    # Segundo turno: mismo peluquero ocupado (aunque haya silla) → 400
    res2 = client.post(url, _turno_payload(clientes[1], peluquero_a, servicio), format='json')
    assert res2.status_code == 400
    assert res2.data.get('code') == 'PELUQUERO_OCUPADO'
    assert "ocupado" in res2.data.get('message', '').lower()
    assert Turno.objects.filter(fecha=date(2026, 7, 20), hora=time(10, 0)).count() == 1


@pytest.mark.django_db
def test_turno_cancelado_no_bloquea_silla_ni_peluquero(_roles_turnos, _turno_payload):
    from usuarios.models import Silla
    client = APIClient()
    sillas = [Silla.objects.create(nombre=f"Silla {i}", orden=i) for i in range(1, 3)]
    peluquero_b = UsuarioFactory(rol=_roles_turnos['peluquero'])
    cliente_a = UsuarioFactory(rol=_roles_turnos['cliente'])
    cliente_b = UsuarioFactory(rol=_roles_turnos['cliente'])
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol=_roles_turnos['admin'])
    client.force_authenticate(user=admin)
    _crear_caja(admin)

    # Antecedente CANCELADO en la misma silla 2 / peluquero_b (no debe bloquear)
    Turno.objects.create(
        fecha=date(2026, 7, 20), hora=time(10, 0),
        peluquero=peluquero_b, cliente=cliente_a,
        estado='CANCELADO', tipo_pago='TOTAL', silla=sillas[1],
    )

    url = '/api/turnos/crear/'
    res = client.post(url, _turno_payload(cliente_b, peluquero_b, servicio), format='json')
    assert res.status_code == 201, f"El turno cancelado no debería bloquear: {res.data}"
    assert Turno.objects.get(id=res.data['turno_id']).silla_id is not None


@pytest.mark.django_db
def test_todo_turno_nuevo_tiene_silla_asignada(_roles_turnos, _turno_payload):
    from usuarios.models import Silla
    client = APIClient()
    [Silla.objects.create(nombre=f"Silla {i}", orden=i) for i in range(1, 4)]
    peluqueros = [UsuarioFactory(rol=_roles_turnos['peluquero']) for _ in range(3)]
    clientes = [UsuarioFactory(rol=_roles_turnos['cliente']) for _ in range(3)]
    servicio = ServicioFactory(duracion=30)
    admin = UsuarioFactory(rol=_roles_turnos['admin'])
    client.force_authenticate(user=admin)
    _crear_caja(admin)

    url = '/api/turnos/crear/'
    for i in range(3):
        res = client.post(url, _turno_payload(clientes[i], peluqueros[i], servicio), format='json')
        assert res.status_code == 201
        turno = Turno.objects.get(id=res.data['turno_id'])
        assert turno.silla_id is not None
        assert turno.peluquero_id is not None