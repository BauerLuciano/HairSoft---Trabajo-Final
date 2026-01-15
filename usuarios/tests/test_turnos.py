import pytest
from rest_framework.test import APIClient
from usuarios.factories import UsuarioFactory, ServicioFactory

@pytest.mark.django_db
def test_no_permitir_turnos_solapados():
    client = APIClient()

    # 1. SETUP: Creamos los personajes
    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    cliente = UsuarioFactory(rol__nombre='Cliente')
    servicio = ServicioFactory(duracion=30) # 30 min de duración
    
    admin = UsuarioFactory(rol__nombre='Administrador')
    client.force_authenticate(user=admin)

    url = '/api/turnos/crear/' 
    
    # 2. DATA: Usamos los nombres exactos que pide tu vista
    data = {
        "canal": "PRESENCIAL",
        "cliente_id": cliente.id,
        "peluquero_id": peluquero.id, # Antes decia 'peluquero'
        "servicios_ids": [servicio.id], # Antes decia 'servicios'
        "fecha": "2026-05-10",
        "hora": "10:00",
        "tipo_pago": "TOTAL",
        "medio_pago": "EFECTIVO"
    }

    # 3. EJECUCIÓN: Creamos el primer turno
    res1 = client.post(url, data, format='json')
    
    if res1.status_code != 201:
        print(f"\n🛑 ERROR EN TURNOS (POST 1): {res1.data}")
        
    assert res1.status_code == 201
    print("\n✅ Primer turno creado con éxito.")

    # 4. SOLAPAMIENTO: Intentamos crear otro en el mismo rango (10:00 a 10:30)
    # Mandamos un turno a las 10:15 (Debería chocar con el de las 10:00)
    data_solapada = data.copy()
    data_solapada["hora"] = "10:15"
    
    res2 = client.post(url, data_solapada, format='json')
    
    # Debería dar 400 porque tu lógica de "Colisión" es robusta
    assert res2.status_code == 400
    assert "Horario ocupado" in res2.data['message']
    print(f"✅ El sistema rechazó el solapamiento correctamente: {res2.data['message']}")