import mercadopago
import uuid
from django.conf import settings

class MercadoPagoService:
    def __init__(self):
        # Inicializar SDK con Access Token
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO['ACCESS_TOKEN'])
        self.back_urls = settings.MERCADO_PAGO.get('BACK_URLS', {})
        self.statement_descriptor = "HAIRSOFT"

    # ======================================================
    # LÓGICA DE TURNOS (INTACTA)
    # ======================================================
    def crear_preferencia_seña(self, turno_data):
        """
        Crea una preferencia de pago en Mercado Pago para señas de turnos.
        """
        monto_pago = round(turno_data["monto_pago"], 2)
        titulo = (
            f"Reserva peluquería - {turno_data['peluquero_nombre']}"
            if not turno_data["es_pago_total"]
            else f"Pago completo turno - {turno_data['peluquero_nombre']}"
        )

        # Aquí usamos el correo que viene del diccionario del turno
        correo_cliente = turno_data.get("cliente_correo", "test_user_6205179917708892357@testuser.com")

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
                return {
                    "success": False,
                    "error": data.get("message", "Error desconocido al crear preferencia con SDK"),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def devolver_pago(self, payment_id, amount=None):
        """
        Realiza un reembolso total o PARCIAL de un pago.
        """
        try:
            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {
                'X-Idempotency-Key': str(uuid.uuid4())
            }
            
            refund_data = {}
            if amount:
                refund_data = {"amount": float(amount)}

            refund_result = self.sdk.refund().create(payment_id, refund_data, request_options)
            response = refund_result["response"]
            
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

    # ======================================================
    # LÓGICA DE COMPRA DE PRODUCTOS (CORREGIDA)
    # ======================================================
    def crear_preferencia_compra_web(self, pedido, items_pedido):
        """
        Genera la preferencia de pago para un Pedido Web.
        """
        # 1. Armamos la lista de items para MercadoPago
        items_mp = []
        for detalle in items_pedido:
            items_mp.append({
                # Forzamos string y float para evitar errores de serialización
                "title": str(detalle.producto.nombre), 
                "quantity": int(detalle.cantidad),
                "currency_id": "ARS",
                "unit_price": float(detalle.precio_unitario) 
            })

        # 2. Si hay costo de envío, lo agregamos como un item más
        if pedido.costo_envio > 0:
            items_mp.append({
                "title": f"Costo de Envío ({pedido.get_tipo_entrega_display()})",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(pedido.costo_envio)
            })

        # Obtenemos email de forma segura
        email_cliente = getattr(pedido.cliente, 'correo', None) or getattr(pedido.cliente, 'email', None) or "test_user_123456@testuser.com"

        # 3. Configuración de la preferencia
        preference_data = {
            "items": items_mp,
            "payer": {
                "name": str(pedido.cliente.nombre),
                "surname": str(pedido.cliente.apellido),
                "email": email_cliente, 
            },
            "back_urls": {
                # Usamos 127.0.0.1 para evitar problemas de CORS/DNS con localhost en algunos navegadores
                "success": "http://127.0.0.1:5173/compra-exitosa",
                "failure": "http://127.0.0.1:5173/compra-fallida",
                "pending": "http://127.0.0.1:5173/compra-pendiente"
            },
            # "auto_return": "approved", # COMENTADO: Causa error 400 'invalid_auto_return' si back_urls no son HTTPS o válidas
            "external_reference": str(pedido.id),
            "statement_descriptor": "HairSoft Tienda",
        }

        try:
            print(f"📤 Enviando preferencia a MP: {preference_data}") # DEBUG
            preference_result = self.sdk.preference().create(preference_data)
            
            # Verificación de respuesta
            if preference_result.get("status") not in [200, 201]:
                error_msg = preference_result.get("response", {}).get("message", "Error desconocido de MP")
                print(f"❌ Error respuesta MP: {preference_result}")
                raise Exception(f"MercadoPago Error: {error_msg}")

            preference_response = preference_result["response"]
            
            # Verificación de ID
            if "id" not in preference_response:
                 print(f"❌ Respuesta MP sin ID: {preference_response}")
                 raise Exception("MercadoPago no devolvió un ID de preferencia válido.")

            # Obtenemos el link correcto (Sandbox o Producción según configuración)
            init_url = preference_response.get("sandbox_init_point") or preference_response.get("init_point")

            return {
                "url_pago": init_url,
                "preference_id": preference_response["id"]
            }
        except Exception as e:
            print(f"❌ Error creando preferencia de compra web: {e}")
            raise e