# usuarios/mercadopago_service.py
import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# CONFIGURACIÓN (AJUSTAR ESTO)
# ----------------------------------------------------------------------

BASE_URL = 'http://localhost:8000' 
NOTIFICATION_ENDPOINT = "/usuarios/api/mercadopago/webhook/"
NOTIFICATION_URL = f"{BASE_URL}{NOTIFICATION_ENDPOINT}" 

# ----------------------------------------------------------------------
# CLASE DE SERVICIO
# ----------------------------------------------------------------------

class MercadoPagoService:
    def __init__(self):
        # 🛑 CORRECCIÓN CRÍTICA 1: Aseguramos que el atributo exista en la instancia.
        # Leemos el token de settings al inicializar.
        mp_config = settings.MERCADO_PAGO
        self.access_token = mp_config.get('ACCESS_TOKEN') 
        
        if not self.access_token:
            logger.error("❌ MERCADO_PAGO ACCESS_TOKEN no configurado en settings.py.")
        
        # Leemos las URLs de retorno de settings (opcional, pero mejor centralizado)
        self.back_urls_config = settings.MERCADO_PAGO.get('BACK_URLS', {})


    def crear_preferencia_seña(self, turno_data):
        """
        Crea la preferencia para el pago de la SEÑA ONLINE (Redireccionamiento web).
        """
        
        # 🛑 CORRECCIÓN CRÍTICA 2: Leemos el token justo antes de usarlo para evitar errores de ámbito.
        access_token_actual = settings.MERCADO_PAGO.get('ACCESS_TOKEN')
        
        if not access_token_actual:
            return {"success": False, "error": "Token de Mercado Pago no configurado."}
            
        try:
            turno_id = turno_data.get('turno_id')
            
            # 🛑 CORRECCIÓN 3: USAR 'monto_pago' (Viene de la vista crear_turno)
            monto_pago = turno_data.get('monto_pago') 
            cliente_email = turno_data.get('cliente_correo', 'sin_email@temp.com')
            
            # La variable a validar ahora es monto_pago
            if not turno_id or not monto_pago or float(monto_pago) <= 0:
                # El error que viste en el frontend
                return {"success": False, "error": "Datos de pago inválidos (ID de turno o monto seña faltante/cero)."}

            monto_float = float(monto_pago)
            
            logger.info(f"🎯 Creando preferencia WEB - Turno: {turno_id} | Monto: {monto_float}")

            # URLs de retorno: Ajustadas para usar el ID de turno como external_reference
            back_urls = {
                "success": f"{BASE_URL}/turno/confirmacion/?status=success&external_reference={turno_id}",
                "failure": f"{BASE_URL}/turno/confirmacion/?status=failure&external_reference={turno_id}",
                "pending": f"{BASE_URL}/turno/confirmacion/?status=pending&external_reference={turno_id}",
            }
            
            preference_data = {
                "items": [
                    {
                        "title": f"Pago Turno #{turno_id}",
                        "quantity": 1,
                        "currency_id": "ARS",
                        "unit_price": monto_float
                    }
                ],
                "notification_url": NOTIFICATION_URL, 
                "back_urls": back_urls,
                #"auto_return": "approved",
                "external_reference": str(turno_id),
                "statement_descriptor": "BARBERIASEÑA",
                "payer": {
                    "email": cliente_email
                }
            }

            headers = {
                "Authorization": f"Bearer {access_token_actual}", # 🛑 Usando el token asegurado
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://api.mercadopago.com/checkout/preferences",
                headers=headers,
                json=preference_data,
                timeout=30
            )

            if response.status_code == 201:
                preference = response.json()
                logger.info(f"✅ Preferencia WEB creada: {preference.get('id')}")
                
                return {
                    "success": True,
                    "init_point": preference.get("init_point"), 
                    "sandbox_init_point": preference.get("sandbox_init_point"),
                    "preference_id": preference.get("id")
                }
            else:
                error_msg = response.text
                logger.error(f"❌ Error al crear preferencia MP (Status {response.status_code}): {error_msg}")
                return {
                    "success": False, 
                    "error": f"Error MP: {error_msg}"
                }
                
        except Exception as e:
            logger.error(f"💥 Excepción al crear preferencia MP: {str(e)}")
            return {
                "success": False, 
                "error": f"Excepción: {str(e)}"
            }

    # ... (El resto de la clase, como crear_preferencia_presencial, va aquí y DEBE usar access_token_actual = settings.MERCADO_PAGO.get('ACCESS_TOKEN') también)