import mercadopago
import uuid
from django.conf import settings

class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO['ACCESS_TOKEN'])
        self.config = settings.MERCADO_PAGO 
        self.statement_descriptor = "HAIRSOFT"

    def crear_preferencia_seña(self, turno_data):
        # 1. OBTENER EL TÚNEL (HTTPS)
        tunnel_url = getattr(settings, 'TUNNEL_URL', '')
        
        if not tunnel_url:
            base_url = "http://127.0.0.1:5173"
            # Si no hay túnel, fallback directo al frontend
            back_urls_dict = {
                "success": f"{base_url}/cliente/historial?pago_exitoso=true&turno_id={turno_data['turno_id']}",
                "failure": f"{base_url}/turnos/crear-web?pago_error=true",
                "pending": f"{base_url}/cliente/historial?pago_pendiente=true"
            }
        else:
            # SI HAY TÚNEL, USAMOS LAS RUTAS QUE TENÉS EN URLS.PY
            tunnel_url = tunnel_url.rstrip('/')
            
            # ✅ CORRECCIÓN ACÁ: Usamos /api/mercadopago/... para coincidir con tu urls.py
            back_urls_dict = {
                "success": f"{tunnel_url}/api/mercadopago/pago-exitoso/", 
                "failure": f"{tunnel_url}/api/mercadopago/pago-error/",
                "pending": f"{tunnel_url}/api/mercadopago/pago-pendiente/"
            }

        print(f"🔗 MP BACK_URLS: {back_urls_dict}")

        # 2. PREPARAR DATOS
        monto_pago = round(float(turno_data["monto_pago"]), 2)
        turno_id = str(turno_data['turno_id'])
        
        titulo = (
            f"Reserva peluquería - {turno_data['peluquero_nombre']}"
            if not turno_data.get("es_pago_total", False)
            else f"Pago completo turno - {turno_data['peluquero_nombre']}"
        )

        correo_cliente = turno_data.get("cliente_correo", "test_user_6205179917708892357@testuser.com")

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
                "email": correo_cliente,
            },
            "back_urls": back_urls_dict,
            
            # ✅ Auto-retorno activado (Funciona porque tunnel_url es HTTPS)
            "auto_return": "approved", 
            
            "notification_url": self.config.get('WEBHOOK_URL'),
            "external_reference": f"TURNO_{turno_id}",
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
        }

        try:
            result = self.sdk.preference().create(preference_data)
            response = result["response"]
            
            if result.get("status") == 201 or "id" in response:
                print("🟦 Respuesta MP (SDK): Preferencia Creada Exitosamente")
                link = response.get("sandbox_init_point") if settings.DEBUG else response.get("init_point")
                return {
                    "success": True,
                    "init_point": link,
                    "preference_id": response["id"],
                }
            else:
                error_msg = response.get("message") or "Error desconocido de MP"
                print(f"❌ Error de MP (Status {result.get('status')}): {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            print(f"💥 Excepción en MP Service: {str(e)}")
            return {"success": False, "error": str(e)}

    def devolver_pago(self, payment_id, amount=None):
        try:
            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {'X-Idempotency-Key': str(uuid.uuid4())}
            refund_data = {"amount": float(amount)} if amount else {}
            refund_result = self.sdk.refund().create(payment_id, refund_data, request_options)
            response = refund_result["response"]
            if response.get("status") in ["approved", "refunded"]:
                return {"success": True, "status": "refunded"}
            return {"success": False, "error": response.get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def crear_preferencia_compra_web(self, pedido, items_pedido):
        base_url = "http://127.0.0.1:5173"
        
        items_mp = []
        for detalle in items_pedido:
            items_mp.append({
                "title": str(detalle.producto.nombre), "quantity": int(detalle.cantidad),
                "currency_id": "ARS", "unit_price": float(detalle.precio_unitario) 
            })

        if pedido.costo_envio > 0:
            items_mp.append({"title": "Costo Envío", "quantity": 1, "currency_id": "ARS", "unit_price": float(pedido.costo_envio)})

        email_cliente = getattr(pedido.cliente, 'correo', None) or "test@testuser.com"

        back_urls_dict = {
            "success": f"{base_url}/cliente/pedidos?pago_exitoso=true&pedido_id={pedido.id}",
            "failure": f"{base_url}/carrito?pago_error=true",
            "pending": f"{base_url}/cliente/pedidos?pago_pendiente=true"
        }

        preference_data = {
            "items": items_mp,
            "payer": {"name": str(pedido.cliente.nombre), "email": email_cliente},
            "back_urls": back_urls_dict,
            "auto_return": "approved",
            "notification_url": self.config.get('WEBHOOK_URL'),
            "external_reference": f"PEDIDO_{pedido.id}",
            "binary_mode": True,
        }
        try:
            res = self.sdk.preference().create(preference_data)
            data = res["response"]
            return {"url_pago": data.get("sandbox_init_point") or data.get("init_point"), "preference_id": data["id"]}
        except Exception as e:
            raise e