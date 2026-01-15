import pytest
from rest_framework import status
from rest_framework.test import APIClient
from usuarios.factories import UsuarioFactory, ProductoFactory, MetodoPagoFactory

@pytest.mark.django_db
def test_venta_descuenta_stock_correctamente():
    client = APIClient()
    admin = UsuarioFactory(rol__nombre='Administrador')
    client.force_authenticate(user=admin)
    
    producto = ProductoFactory(nombre="Shampoo Test", stock_actual=10, precio=1000)
    metodo = MetodoPagoFactory(nombre="Efectivo")
    
    # ✅ URL CORREGIDA: Apuntamos a tu función personalizada
    url = '/api/ventas/registrar/' 
    
    data = {
        "medio_pago": metodo.id,
        "detalles": [
            {
                "producto": producto.id,
                "cantidad": 3,
                "precio_unitario": 1000
            }
        ]
    }
    
    response = client.post(url, data, format='json')
    
    assert response.status_code == 201
    producto.refresh_from_db()
    assert producto.stock_actual == 7

@pytest.mark.django_db
def test_error_venta_stock_insuficiente():
    client = APIClient()
    admin = UsuarioFactory(rol__nombre='Administrador')
    client.force_authenticate(user=admin)
    
    producto = ProductoFactory(nombre="Shampoo Escaso", stock_actual=5, precio=1000)
    metodo = MetodoPagoFactory(nombre="Efectivo")
    
    # ✅ URL CORREGIDA: Apuntamos a tu función personalizada
    url = '/api/ventas/registrar/' 
    
    data = {
        "medio_pago": metodo.id,
        "detalles": [
            {
                "producto": producto.id,
                "cantidad": 10, # Más de lo que hay (5)
                "precio_unitario": 1000
            }
        ]
    }
    
    response = client.post(url, data, format='json')
    
    # Ahora sí, tu función devuelve {"error": "Stock insuficiente..."}
    assert response.status_code == 400
    assert "Stock insuficiente" in response.data['error']
    
    # Verificamos que no se descontó nada
    producto.refresh_from_db()
    assert producto.stock_actual == 5 
    print(f"\n✅ El sistema bloqueó la venta correctamente: {response.data['error']}")

@pytest.mark.django_db
def test_anular_venta_restaura_stock():
    client = APIClient()
    admin = UsuarioFactory(rol__nombre='Administrador')
    client.force_authenticate(user=admin)
    
    # 1. Vendemos 3 productos (Stock inicial 10 -> queda en 7)
    producto = ProductoFactory(stock_actual=10)
    metodo = MetodoPagoFactory()
    url_vender = '/api/ventas/registrar/'
    data = {
        "medio_pago": metodo.id,
        "detalles": [{"producto": producto.id, "cantidad": 3, "precio_unitario": 100}]
    }
    res_v = client.post(url_vender, data, format='json')
    venta_id = res_v.data['id']

    # 2. Anulamos la venta
    url_anular = f'/api/ventas/{venta_id}/anular/'
    response = client.post(url_anular) # Tu view usa POST para anular

    # 3. Verificación: El stock debe volver a 10
    assert response.status_code == 200
    producto.refresh_from_db()
    assert producto.stock_actual == 10
    print(f"\n✅ Venta anulada. Stock restaurado a: {producto.stock_actual}")