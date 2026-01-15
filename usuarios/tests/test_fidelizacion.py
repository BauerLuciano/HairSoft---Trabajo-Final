import pytest
from rest_framework.test import APIClient
from usuarios.models import PromocionReactivacion
from django.utils import timezone
from datetime import timedelta
from usuarios.factories import UsuarioFactory

@pytest.mark.django_db
def test_validar_cupon_fidelizacion():
    client = APIClient()
    cliente = UsuarioFactory(rol__nombre='Cliente')
    
    # 1. Creamos una promo manual para el cliente
    promo = PromocionReactivacion.objects.create(
        cliente=cliente,
        codigo="VOLVE2026",
        descuento_porcentaje=15,
        fecha_vencimiento=timezone.now() + timedelta(days=10),
        estado='ACTIVA'
    )
    
    # 2. Validamos el cupón por la API
    url = f'/api/promociones/validar/VOLVE2026/'
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.data['valido'] == True
    assert float(response.data['descuento']) == 15.0
    print(f"\n✅ Cupón {promo.codigo} validado correctamente.")