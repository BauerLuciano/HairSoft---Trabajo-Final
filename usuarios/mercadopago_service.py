import mercadopago
import uuid
from django.conf import settings

class MercadoPagoService:
    def __init__(self):
        # Iniciamos el SDK con el Token de tus settings
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO['ACCESS_TOKEN'])
        self.config = settings.MERCADO_PAGO 
        self.statement_descriptor = "HAIRSOFT"

    def crear_preferencia_seña(self, turno_data):
        """
        CREA PAGO PARA SEÑA DE TURNOS
        """
        tunnel_url = getattr(settings, 'TUNNEL_URL', '').rstrip('/')
        
        # Para que MP acepte auto_return, la URL debe ser la del túnel (HTTPS)
        if tunnel_url:
            base_url = tunnel_url
        else:
            base_url = "http://127.0.0.1:8000"

        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/pago-exitoso/", 
            "failure": f"{base_url}/api/mercadopago/pago-error/",
            "pending": f"{base_url}/api/mercadopago/pago-pendiente/"
        }

        monto_pago = round(float(turno_data["monto_pago"]), 2)
        turno_id = str(turno_data['turno_id'])
        titulo = f"Seña Turno - {turno_data['peluquero_nombre']}"

        preference_data = {
            "items": [
                {
                    "title": titulo,
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": monto_pago,
                }
            ],
            "payer": {
                "name": str(turno_data["cliente_nombre"]),
                "email": turno_data.get("cliente_correo", "test_user_6205179917708892357@testuser.com"),
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
            return {
                "success": True, 
                "init_point": res.get("sandbox_init_point") if settings.DEBUG else res.get("init_point"), 
                "preference_id": res["id"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def crear_preferencia_compra_web(self, pedido, items_pedido):
        """
        CREA PAGO PARA CARRITO DE PRODUCTOS
        """
        tunnel_url = getattr(settings, 'TUNNEL_URL', '').rstrip('/')
        
        # MP exige que si hay auto_return, las back_urls sean HTTPS válidas
        if tunnel_url:
            base_url = tunnel_url
        else:
            base_url = "http://127.0.0.1:8000"

        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/pago-exitoso/", 
            "failure": f"{base_url}/api/mercadopago/pago-error/",
            "pending": f"{base_url}/api/mercadopago/pago-pendiente/"
        }

        # Cargamos los productos al formato de MP
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
                "email": getattr(pedido.cliente, 'correo', "test@testuser.com")
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
                    "url_pago": data.get("sandbox_init_point") if settings.DEBUG else data.get("init_point"), 
                    "preference_id": data["id"]
                }
            else:
                raise Exception(f"MP Error: {data.get('message', 'Error desconocido')}")
        except Exception as e:
            print(f"💥 Error en crear_preferencia_compra_web: {e}")
            raise e

    def devolver_pago(self, payment_id, amount=None):
        """
        REEMBOLSOS
        """
        try:
            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {'X-Idempotency-Key': str(uuid.uuid4())}
            refund_data = {"amount": float(amount)} if amount else {}
            refund_result = self.sdk.refund().create(payment_id, refund_data, request_options)
            if refund_result["response"].get("status") in ["approved", "refunded"]:
                return {"success": True, "status": "refunded"}
            return {"success": False, "error": refund_result["response"].get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}