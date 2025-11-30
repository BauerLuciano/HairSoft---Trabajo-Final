# ================================
# usuarios/mercadopago_service.py
# ================================
import mercadopago
from django.conf import settings

class MercadoPagoService:
    def __init__(self):
        # Inicializar SDK con Access Token (producción de cuenta de prueba)
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO['ACCESS_TOKEN'])
        self.back_urls = settings.MERCADO_PAGO.get('BACK_URLS', {})
        self.statement_descriptor = "HAIRSOFT"

    def crear_preferencia_seña(self, turno_data):
        """
        Crea una preferencia de pago en Mercado Pago (sandbox o real)
        turno_data debe tener:
            - turno_id
            - monto_pago
            - cliente_nombre
            - cliente_correo
            - peluquero_nombre
            - es_pago_total (bool)
        """

        monto_pago = round(turno_data["monto_pago"], 2)
        titulo = (
            f"Reserva peluquería - {turno_data['peluquero_nombre']}"
            if not turno_data["es_pago_total"]
            else f"Pago completo turno - {turno_data['peluquero_nombre']}"
        )

        correo_cliente = turno_data.get("cliente_correo", "test_user_6205179917708892357@testuser.com")

        # URLs de redirección
        back_urls = {
            "success": self.back_urls.get("success", "http://localhost:5173/pago-exitoso"),
            "failure": self.back_urls.get("failure", "http://localhost:5173/pago-error"),
            "pending": self.back_urls.get("pending", "http://localhost:5173/pago-pendiente"),
        }

        payload = {
            "items": [
                {
                    "title": titulo,
                    "quantity": 1,
                    "unit_price": monto_pago,
                    "currency_id": "ARS",
                }
            ],
            "payer": {
                "name": turno_data["cliente_nombre"],
                "email": correo_cliente,
            },
            "back_urls": back_urls,
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
        }

        try:
            # Crear preferencia con SDK
            result = self.sdk.preference().create(payload)
            data = result["response"]
            print("🟦 Respuesta MP (SDK):", data)

            # Usar sandbox_init_point siempre para pruebas
            init_url = data.get("sandbox_init_point") or data.get("init_point")

            if "id" in data:
                return {
                    "success": True,
                    "init_point": init_url,
                    "preference_id": data["id"],
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Error desconocido al crear preferencia con SDK"),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

def devolver_pago(self, payment_id):
        """
        Realiza un reembolso total de un pago específico.
        Requiere el payment_id (no el preference_id).
        """
        try:
            # El endpoint de reembolso necesita un idempotency key para evitar duplicados (opcional pero recomendado)
            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {
                'X-Idempotency-Key': str(uuid.uuid4())
            }
            
            # Llamada a la API de reembolso
            refund_data = self.sdk.refund().create(payment_id, request_options)
            response = refund_data["response"]
            
            print(f"🔄 Respuesta Reembolso MP: {response}")
            
            if response.get("status") == "approved" or response.get("status") == "refunded":
                return {"success": True, "status": "refunded"}
            else:
                return {
                    "success": False, 
                    "error": response.get("message", "Error desconocido en reembolso")
                }
                
        except Exception as e:
            print(f"❌ Error en devolver_pago: {str(e)}")
            return {"success": False, "error": str(e)}