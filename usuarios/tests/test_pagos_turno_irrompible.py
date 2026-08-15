import uuid
import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from usuarios.factories import UsuarioFactory, ServicioFactory
from usuarios.models import Caja, SesionCaja, Turno, MovimientoCaja, PagoTemporal


def _setup_base():
    admin = UsuarioFactory(rol__nombre='Administrador')
    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    cliente = UsuarioFactory(rol__nombre='Cliente')
    servicio = ServicioFactory(precio=2000.00, duracion=30)
    caja = Caja.objects.create(nombre=f"Caja Test {uuid.uuid4().hex[:8]}")
    sesion = SesionCaja.objects.create(caja=caja, usuario_apertura=admin, saldo_inicial_efectivo=0)
    return {'admin': admin, 'peluquero': peluquero, 'cliente': cliente, 'servicio': servicio, 'sesion': sesion}


def _payload_base(base, **overrides):
    data = {
        "canal": "PRESENCIAL",
        "cliente_id": base['cliente'].id,
        "peluquero_id": base['peluquero'].id,
        "servicios_ids": [base['servicio'].id],
        "fecha": "2026-05-11",
        "hora": "10:00",
        "tipo_pago": "SENA_50",
        "medio_pago": "EFECTIVO",
    }
    data.update(overrides)
    return data


def _crear_turno(base, **overrides):
    client = APIClient()
    client.force_authenticate(user=base['admin'])
    return client.post('/api/turnos/crear/', _payload_base(base, **overrides), format='json')


def _crear_turno_db(base, **campos):
    turno = Turno.objects.create(
        cliente=base['cliente'],
        peluquero=base['peluquero'],
        fecha='2026-05-11',
        hora='10:00',
        canal='PRESENCIAL',
        estado='RESERVADO',
        tipo_pago=campos.pop('tipo_pago', 'SENA_50'),
        medio_pago=campos.pop('medio_pago', 'EFECTIVO'),
        monto_seña=campos.pop('monto_seña', Decimal('500')),
        monto_total=campos.pop('monto_total', Decimal('1000')),
        **campos,
    )
    turno.servicios.set([base['servicio']])
    return turno


# ============================================================
# 1. SEÑA + QR aprobado = IRROMPIBLE
# ============================================================
@pytest.mark.django_db
def test_sena_qr_aprobado_es_irrompible():
    base = _setup_base()
    pago = PagoTemporal.objects.create(monto=Decimal('1000'), mp_payment_id='pay_mp_001', pagado=True, usado=False)

    res = _crear_turno(base, tipo_pago='SENA_50', medio_pago='MERCADO_PAGO', pago_uuid=str(pago.uid))
    assert res.status_code == 201, res.data

    turno = Turno.objects.get(id=res.data['turno_id'])
    assert turno.medio_pago == 'MERCADO_PAGO'
    assert turno.tipo_pago == 'SENA_50'
    assert turno.mp_payment_id == 'pay_mp_001'
    assert float(turno.monto_seña) == 1000.0
    assert float(turno.calcular_saldo_pendiente()) == 1000.0
    pago.refresh_from_db()
    assert pago.usado is True

    # Un solo movimiento de caja por la seña (MP)
    movs = MovimientoCaja.objects.filter(turno_relacionado=turno, concepto='TURNO_PRESENCIAL')
    assert movs.count() == 1
    assert movs.first().metodo_pago == 'MERCADO_PAGO'

    # Admin no puede cambiar SEÑA <-> TOTAL
    token = Token.objects.create(user=base['admin'])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    res = client.post(f'/api/turnos/{turno.id}/modificar/', {'tipo_pago': 'TOTAL'}, format='json')
    assert res.status_code == 409, res.content

    # Admin no puede cambiar el medio principal
    res = client.post(f'/api/turnos/{turno.id}/modificar/', {'medio_pago': 'EFECTIVO'}, format='json')
    assert res.status_code == 409, res.content

    # actualizar-pago tampoco cambia tipo ni sobre-escribe mp_payment_id
    client2 = APIClient()
    client2.force_authenticate(user=base['admin'])
    res = client2.post(f'/api/turnos/{turno.id}/actualizar-pago/', {'tipo_pago': 'TOTAL'}, format='json')
    assert res.status_code == 409, res.content

    res = client2.post(f'/api/turnos/{turno.id}/actualizar-pago/', {'nro_transaccion': 'hack'}, format='json')
    assert res.status_code == 409, res.content

    turno.refresh_from_db()
    assert turno.mp_payment_id == 'pay_mp_001'
    assert turno.tipo_pago == 'SENA_50'


# ============================================================
# 2. TOTAL + QR aprobado: no se puede cambiar a otro medio
# ============================================================
@pytest.mark.django_db
def test_total_qr_aprobado_bloquea_cambio_medio():
    base = _setup_base()
    pago = PagoTemporal.objects.create(monto=Decimal('2000'), mp_payment_id='pay_mp_002', pagado=True, usado=False)

    res = _crear_turno(base, tipo_pago='TOTAL', medio_pago='MERCADO_PAGO', pago_uuid=str(pago.uid))
    assert res.status_code == 201, res.data

    turno = Turno.objects.get(id=res.data['turno_id'])
    assert turno.tipo_pago == 'TOTAL'
    assert turno.medio_pago == 'MERCADO_PAGO'
    assert float(turno.calcular_saldo_pendiente()) == 0.0

    client = APIClient()
    client.force_authenticate(user=base['admin'])
    res = client.post(f'/api/turnos/{turno.id}/actualizar-pago/', {'medio_pago': 'EFECTIVO'}, format='json')
    assert res.status_code == 409, res.content

    token = Token.objects.create(user=base['admin'])
    client2 = APIClient()
    client2.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    res = client2.post(f'/api/turnos/{turno.id}/modificar/', {'tipo_pago': 'SENA_50'}, format='json')
    assert res.status_code == 409, res.content


# ============================================================
# 3. Cobrar restante (EFECTIVO) sobre seña MP: no pisa principal
# ============================================================
@pytest.mark.django_db
def test_cobrar_restante_efectivo_no_pisa_principal_mp():
    base = _setup_base()
    pago = PagoTemporal.objects.create(monto=Decimal('1000'), mp_payment_id='pay_mp_003', pagado=True, usado=False)
    res = _crear_turno(base, tipo_pago='SENA_50', medio_pago='MERCADO_PAGO', pago_uuid=str(pago.uid))
    turno = Turno.objects.get(id=res.data['turno_id'])

    client = APIClient()
    client.force_authenticate(user=base['admin'])
    res = client.post(f'/api/turnos/{turno.id}/pagar-saldo/', {'metodo': 'EFECTIVO'}, format='json')
    assert res.status_code == 200, res.content

    turno.refresh_from_db()
    assert turno.medio_pago == 'MERCADO_PAGO'            # principal intacto
    assert turno.mp_payment_id == 'pay_mp_003'           # mp_payment_id intacto
    assert turno.medio_pago_restante == 'EFECTIVO'
    assert turno.tipo_pago == 'TOTAL'
    assert float(turno.monto_seña) == 2000.0
    assert float(turno.calcular_saldo_pendiente()) == 0.0

    movs = MovimientoCaja.objects.filter(turno_relacionado=turno)
    assert movs.filter(concepto='TURNO_PRESENCIAL').count() == 1
    assert movs.filter(concepto='COBRO_RESTANTE', metodo_pago='EFECTIVO', monto=1000).count() == 1


# ============================================================
# 4. Pago mixto (QR + efectivo) = misma filosofía del POS
# ============================================================
@pytest.mark.django_db
def test_pago_mixto_qr_mas_efectivo():
    base = _setup_base()
    pago = PagoTemporal.objects.create(monto=Decimal('800'), mp_payment_id='pay_mp_004', pagado=True, usado=False)

    res = _crear_turno(
        base,
        tipo_pago='SENA_50',
        medio_pago='MIXTO',
        pago_mixto=True,
        monto_mp=800,
        monto_efectivo=200,
        pago_uuid=str(pago.uid),
    )
    assert res.status_code == 201, res.data

    turno = Turno.objects.get(id=res.data['turno_id'])
    assert turno.medio_pago == 'MERCADO_PAGO'
    assert turno.entidad_pago == 'MIXTO'
    assert turno.codigo_transaccion == 'MERCADOPAGO_QR:800.00|EFECTIVO:200.00'
    assert float(turno.monto_seña) == 1000.0  # mixto cubre la seña íntegra
    pago.refresh_from_db()
    assert pago.usado is True

    # Un movimiento de caja por medio
    movs = MovimientoCaja.objects.filter(turno_relacionado=turno, concepto='TURNO_PRESENCIAL')
    assert movs.filter(metodo_pago='EFECTIVO', monto=200).count() == 1
    assert movs.filter(metodo_pago='MERCADO_PAGO', monto=800).count() == 1


@pytest.mark.django_db
def test_pago_mixto_suma_invalida():
    base = _setup_base()
    pago = PagoTemporal.objects.create(monto=Decimal('800'), mp_payment_id='pay_mp_005', pagado=True, usado=False)
    res = _crear_turno(
        base,
        pago_mixto=True,
        monto_mp=800,
        monto_efectivo=100,  # 900 != 1000 (seña)
        pago_uuid=str(pago.uid),
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_pago_mixto_sin_qr_aprobado_ni_comprobante():
    base = _setup_base()
    res = _crear_turno(
        base,
        pago_mixto=True,
        monto_mp=800,
        monto_efectivo=200,
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_pago_mixto_por_alias_sin_qr():
    base = _setup_base()
    # Mixto cuyo restante se cobró por ALIAS (confirmado por el cajero, sin QR ni mp_payment_id)
    res = _crear_turno(
        base,
        tipo_pago='SENA_50',
        medio_pago='MIXTO',
        pago_mixto=True,
        monto_mp=800,
        monto_efectivo=200,
        entidad_pago='MERCADOPAGO_ALIAS',
    )
    assert res.status_code == 201, res.data

    turno = Turno.objects.get(id=res.data['turno_id'])
    assert turno.medio_pago == 'MERCADO_PAGO'
    assert turno.entidad_pago == 'MIXTO'
    assert turno.codigo_transaccion == 'MERCADOPAGO_ALIAS:800.00|EFECTIVO:200.00'
    assert turno.mp_payment_id is None  # alias no usa comprobante de Mercado Pago
    assert float(turno.monto_seña) == 1000.0

    # Un movimiento de caja por medio (misma filosofía del POS)
    movs = MovimientoCaja.objects.filter(turno_relacionado=turno, concepto='TURNO_PRESENCIAL')
    assert movs.filter(metodo_pago='EFECTIVO', monto=200).count() == 1
    assert movs.filter(metodo_pago='MERCADO_PAGO', monto=800).count() == 1


# ============================================================
# 5. PagoTemporal usado / no pagado no se puede reutilizar
# ============================================================
@pytest.mark.django_db
def test_pago_temporal_reuso_bloqueado():
    base = _setup_base()
    pago = PagoTemporal.objects.create(monto=Decimal('1000'), mp_payment_id='pay_mp_006', pagado=True, usado=True)
    res = _crear_turno(base, pago_uuid=str(pago.uid))
    assert res.status_code == 400
    assert 'utilizado' in res.data['error']

    pago2 = PagoTemporal.objects.create(monto=Decimal('1000'), mp_payment_id='pay_mp_007', pagado=False, usado=False)
    res2 = _crear_turno(base, pago_uuid=str(pago2.uid))
    assert res2.status_code == 400


# ============================================================
# 6. No forzar TOTAL al cobrar el restante (regresión)
# ============================================================
@pytest.mark.django_db
def test_actualizar_pago_no_duplica_caja_al_cobrar_restante():
    base = _setup_base()
    turno = _crear_turno_db(base, tipo_pago='SENA_50', medio_pago='EFECTIVO', monto_seña=Decimal('500'), monto_total=Decimal('1000'))

    client = APIClient()
    client.force_authenticate(user=base['admin'])

    # 1er cobro del restante
    res = client.post(f'/api/turnos/{turno.id}/actualizar-pago/', {'medio_pago': 'EFECTIVO'}, format='json')
    assert res.status_code == 200, res.content
    turno.refresh_from_db()
    assert turno.medio_pago_restante == 'EFECTIVO'
    assert float(turno.monto_seña) == 1000.0
    assert turno.tipo_pago == 'TOTAL'
    assert turno.medio_pago == 'EFECTIVO'  # principal intacto

    # 2do request idéntico: turno ya saldado -> no duplica movimiento
    res2 = client.post(f'/api/turnos/{turno.id}/actualizar-pago/', {'medio_pago': 'EFECTIVO'}, format='json')
    assert res2.status_code == 200
    assert MovimientoCaja.objects.filter(turno_relacionado=turno, concepto='COBRO_RESTANTE').count() == 1


@pytest.mark.django_db
def test_total_efectivo_bloquea_cambio_de_medio():
    base = _setup_base()
    turno = _crear_turno_db(base, tipo_pago='TOTAL', medio_pago='EFECTIVO', monto_seña=Decimal('1000'), monto_total=Decimal('1000'))

    client = APIClient()
    client.force_authenticate(user=base['admin'])
    res = client.post(f'/api/turnos/{turno.id}/actualizar-pago/', {'medio_pago': 'MERCADO_PAGO'}, format='json')
    assert res.status_code == 409, res.content


# ============================================================
# 7. No se regenera QR para un turno con pago MP aprobado
# ============================================================
@pytest.mark.django_db
def test_no_re_generar_qr_para_turno_mp_aprobado():
    base = _setup_base()
    pago = PagoTemporal.objects.create(monto=Decimal('1000'), mp_payment_id='pay_mp_008', pagado=True, usado=False)
    res = _crear_turno(base, pago_uuid=str(pago.uid))
    turno = Turno.objects.get(id=res.data['turno_id'])

    client = APIClient()
    res = client.post('/api/mercadopago/crear-preferencia-sena/', {'turno_id': turno.id, 'monto_sena': 1000}, format='json')
    assert res.status_code == 409, res.content
