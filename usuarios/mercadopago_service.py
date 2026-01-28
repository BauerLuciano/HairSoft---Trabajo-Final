import mercadopago
import uuid
from django.conf import settings

class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO['ACCESS_TOKEN'])
        self.config = settings.MERCADO_PAGO 
        self.statement_descriptor = "HAIRSOFT"

    def crear_preferencia_seña(self, turno_data):
        monto_pago = round(float(turno_data["monto_pago"]), 2)
        titulo = (
            f"Reserva peluquería - {turno_data['peluquero_nombre']}"
            if not turno_data.get("es_pago_total", False)
            else f"Pago completo turno - {turno_data['peluquero_nombre']}"
        )

        correo_cliente = turno_data.get("cliente_correo", "test_user_6205179917708892357@testuser.com")

        # Estructura forzada para evitar el error 400 de MP
        back_urls_dict = {
            "success": self.config['BACK_URLS']['success'],
            "failure": self.config['BACK_URLS']['failure'],
            "pending": self.config['BACK_URLS']['pending']
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
                "name": str(turno_data["cliente_nombre"]),
                "email": correo_cliente,
            },
            "back_urls": back_urls_dict,
            "auto_return": "approved",
            "notification_url": self.config['WEBHOOK_URL'],
            "external_reference": str(turno_data['turno_id']), # Solo ID para tu vista
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
        }

        try:
            result = self.sdk.preference().create(payload)
            data = result["response"]
            print("🟦 Respuesta MP (SDK):", data)

            init_url = data.get("sandbox_init_point") or data.get("init_point")

            if "id" in data:
                return {
                    "success": True,
                    "init_point": init_url,
                    "preference_id": data["id"],
                }
            else:
                print(f"❌ Error de MP: {data}")
                return {"success": False, "error": data.get("message")}
        except Exception as e:
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
        items_mp = []
        for detalle in items_pedido:
            items_mp.append({
                "title": str(detalle.producto.nombre), "quantity": int(detalle.cantidad),
                "currency_id": "ARS", "unit_price": float(detalle.precio_unitario) 
            })

        if pedido.costo_envio > 0:
            items_mp.append({"title": "Costo Envío", "quantity": 1, "currency_id": "ARS", "unit_price": float(pedido.costo_envio)})

        email_cliente = getattr(pedido.cliente, 'correo', None) or "test@testuser.com"

        preference_data = {
            "items": items_mp,
            "payer": {"name": str(pedido.cliente.nombre), "email": email_cliente},
            "back_urls": self.config['BACK_URLS'],
            "auto_return": "approved",
            "notification_url": self.config['WEBHOOK_URL'],
            "external_reference": f"PEDIDO_{pedido.id}",
            "binary_mode": True,
        }
        try:
            res = self.sdk.preference().create(preference_data)
            data = res["response"]
            return {"url_pago": data.get("sandbox_init_point") or data.get("init_point"), "preference_id": data["id"]}
        except Exception as e:
            raise e