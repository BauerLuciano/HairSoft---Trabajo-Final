import mercadopago
import uuid
from django.conf import settings

class MercadoPagoService:
    def __init__(self):
        # Iniciamos el SDK con el Token que esté en settings (Debe ser el TEST-...)
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO['ACCESS_TOKEN'])
        self.config = settings.MERCADO_PAGO 
        self.statement_descriptor = "HAIRSOFT"

    def crear_preferencia_seña(self, turno_data):
        """
        CREA PAGO PARA SEÑA DE TURNOS - 100% MODO SANDBOX
        """
        tunnel_url = getattr(settings, 'TUNNEL_URL', '').rstrip('/')
        base_url = tunnel_url if tunnel_url else "http://127.0.0.1:8000"

        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/pago-exitoso/", 
            "failure": f"{base_url}/api/mercadopago/pago-error/",
            "pending": f"{base_url}/api/mercadopago/pago-pendiente/"
        }

        monto_pago = round(float(turno_data["monto_pago"]), 2)
        turno_id = str(turno_data['turno_id'])
        
        # ✅ Email del comprador de prueba OBLIGATORIO para evitar el error de "partes de prueba"
        # Usamos el mail del comprador que creaste en el panel de MP
        email_comprador_prueba = "test_user_8104669143652787055@testuser.com"

        preference_data = {
            "items": [
                {
                    "title": f"Seña Turno - {turno_data['peluquero_nombre']}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": monto_pago,
                }
            ],
            "payer": {
                "name": str(turno_data["cliente_nombre"]),
                "email": email_comprador_prueba, 
            },
            "back_urls": back_urls_dict,
            "auto_return": "approved", 
            "external_reference": f"TURNO_{turno_id}",
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
        }

        if tunnel_url and "localhost" not in tunnel_url:
            preference_data["notification_url"] = f"{tunnel_url}/mercadopago/webhook/"

        try:
            result = self.sdk.preference().create(preference_data)
            res = result["response"]
            
            # ✅ Devolvemos SIEMPRE el sandbox_init_point para tokens TEST-
            return {
                "success": True, 
                "init_point": res.get("sandbox_init_point"), 
                "preference_id": res["id"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def crear_preferencia_compra_web(self, pedido, items_pedido):
        """
        CREA PAGO PARA CARRITO - 100% MODO SANDBOX
        """
        tunnel_url = getattr(settings, 'TUNNEL_URL', '').rstrip('/')
        base_url = tunnel_url if tunnel_url else "http://127.0.0.1:8000"

        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/pago-exitoso/", 
            "failure": f"{base_url}/api/mercadopago/pago-error/",
            "pending": f"{base_url}/api/mercadopago/pago-pendiente/"
        }

        items_mp = []
        for detalle in items_pedido:
            items_mp.append({
                "title": str(detalle.producto.nombre),
                "quantity": int(detalle.cantidad),
                "currency_id": "ARS",
                "unit_price": float(detalle.precio_unitario) 
            })

        if pedido.costo_envio > 0:
            items_mp.append({
                "title": "Costo Envío", 
                "quantity": 1, 
                "currency_id": "ARS", 
                "unit_price": float(pedido.costo_envio)
            })

        preference_data = {
            "items": items_mp,
            "payer": {
                "name": str(pedido.cliente.nombre), 
                "email": "test_user_8104669143652787055@testuser.com" # ✅ Email de prueba OBLIGATORIO
            },
            "back_urls": back_urls_dict,
            "auto_return": "approved",
            "external_reference": f"PEDIDO_{pedido.id}",
            "binary_mode": True,
        }

        if tunnel_url and "localhost" not in tunnel_url:
            preference_data["notification_url"] = f"{tunnel_url}/mercadopago/webhook/"

        try:
            res_sdk = self.sdk.preference().create(preference_data)
            data = res_sdk["response"]
            if res_sdk["status"] in [200, 201]:
                return {
                    "url_pago": data.get("sandbox_init_point"), 
                    "preference_id": data["id"]
                }
            else:
                raise Exception(f"MP Error: {data.get('message', 'Error desconocido')}")
        except Exception as e:
            raise e

    def devolver_pago(self, payment_id, amount=None):
        """
        REEMBOLSOS POSTA - Ajustado para Sandbox
        """
        try:
            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {'X-Idempotency-Key': str(uuid.uuid4())}
            
            # ✅ TRUCO: En Sandbox, para reembolso total mandamos el diccionario vacío {}.
            # Esto evita conflictos con el monto y credenciales.
            refund_data = {} 
            
            result = self.sdk.refund().create(payment_id, refund_data, request_options)
            
            print(f"DEBUG MP STATUS: {result['status']}")

            if result["status"] in [200, 201]:
                return {
                    "success": True, 
                    "status": "refunded",
                    "refund_id": result["response"].get("id")
                }
            
            error_detail = result["response"].get("message", "Error desconocido")
            return {"success": False, "error": f"MP Status {result['status']}: {error_detail}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}