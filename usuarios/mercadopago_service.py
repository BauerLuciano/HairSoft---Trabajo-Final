import mercadopago
import uuid
from django.conf import settings

class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO['ACCESS_TOKEN'])
        self.config = settings.MERCADO_PAGO 
        self.statement_descriptor = "HAIRSOFT"

    def crear_preferencia_seña(self, turno_data):
        """
        CREA PAGO PARA SEÑA DE TURNOS - 100% MODO SANDBOX
        """
        base_url = "https://brandi-palmar-pickily.ngrok-free.dev"

        # 🔥 FIX DEFINITIVO: Usamos la URL de ngrok (HTTPS) para engañar a MP.
        # Esto va a golpear la ruta que agregaste en urls.py y la función en views.py,
        # la cual te va a redirigir automáticamente a Vue.
        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/retorno/", 
            "failure": f"{base_url}/api/mercadopago/retorno/",
            "pending": f"{base_url}/api/mercadopago/retorno/"
        }

        monto = turno_data.get("monto_pago") or turno_data.get("monto_seña")
        monto_pago = round(float(monto), 2) if monto else 0.1
        turno_id = str(turno_data.get('turno_id', uuid.uuid4()))
        
        email_comprador_prueba = "test_user_1860959446082982366@testuser.com"
        
        preference_data = {
            "items": [
                {
                    "title": f"Seña Turno - {turno_data.get('peluquero_nombre', 'Servicio')}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": monto_pago,
                }
            ],
            "payer": {
                "name": str(turno_data.get("cliente_nombre", "Cliente")),
                "email": email_comprador_prueba, 
            },
            "back_urls": back_urls_dict,
            "auto_return": "approved", # 🔥 MP lo va a aceptar porque back_urls tiene HTTPS
            "external_reference": f"TURNO_{turno_id}",
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
            "notification_url": f"{base_url}/api/mercadopago/webhook/"
        }

        try:
            result = self.sdk.preference().create(preference_data)
            res = result["response"]
            
            if result.get("status") not in [200, 201]:
                print(f"🔥 ERROR REAL DE MERCADO PAGO 🔥: {res}")
                return {"success": False, "error": res.get("message", "Error al crear preferencia en MP")}
            
            return {
                "success": True, 
                "init_point": res.get("sandbox_init_point"), 
                "preference_id": res["id"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def crear_preferencia_temporal(self, monto, uid_str):
        base_url = "https://brandi-palmar-pickily.ngrok-free.dev"
        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/retorno/",
            "failure": f"{base_url}/api/mercadopago/retorno/",
            "pending": f"{base_url}/api/mercadopago/retorno/"
        }
        monto_pago = round(float(monto), 2) if monto else 0.1
        email_comprador_prueba = "test_user_1860959446082982366@testuser.com"

        preference_data = {
            "items": [
                {
                    "title": "Pago Turno Presencial",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": monto_pago,
                }
            ],
            "payer": {"email": email_comprador_prueba},
            "back_urls": back_urls_dict,
            "auto_return": "approved",
            "external_reference": f"TEMP_{uid_str}",
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
            "notification_url": f"{base_url}/api/mercadopago/webhook/"
        }
        try:
            result = self.sdk.preference().create(preference_data)
            res = result["response"]
            if result.get("status") not in [200, 201]:
                return {"success": False, "error": res.get("message", "Error al crear preferencia")}
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
        base_url = "https://brandi-palmar-pickily.ngrok-free.dev"

        # 🔥 FIX: Aplicar el mismo puente de ngrok acá
        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/retorno/", 
            "failure": f"{base_url}/api/mercadopago/retorno/",
            "pending": f"{base_url}/api/mercadopago/retorno/"
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

        email_comprador_prueba = "test_user_1860959446082982366@testuser.com"

        preference_data = {
            "items": items_mp,
            "payer": {
                "name": str(pedido.cliente.nombre), 
                "email": email_comprador_prueba 
            },
            "back_urls": back_urls_dict,
            "auto_return": "approved",
            "external_reference": f"PEDIDO_{pedido.id}",
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
            "notification_url": f"{base_url}/api/mercadopago/webhook/"
        }

        try:
            result = self.sdk.preference().create(preference_data)
            res = result["response"]
            
            if result.get("status") not in [200, 201]:
                print(f"🔥 ERROR REAL DE MERCADO PAGO 🔥: {res}")
                return {"success": False, "error": res.get("message", "Error al crear preferencia en MP")}

            return {
                "url_pago": res.get("sandbox_init_point"), 
                "preference_id": res["id"]
            }
        except Exception as e:
            raise e

    def crear_preferencia_saldo(self, turno, monto_saldo):
        """
        CREA PAGO PARA SALDO PENDIENTE DE TURNO
        """
        base_url = "https://brandi-palmar-pickily.ngrok-free.dev"

        back_urls_dict = {
            "success": f"{base_url}/api/mercadopago/retorno/",
            "failure": f"{base_url}/api/mercadopago/retorno/",
            "pending": f"{base_url}/api/mercadopago/retorno/"
        }

        nombre_cliente = turno.cliente.nombre if turno.cliente else "Cliente"
        servicios_nombres = ", ".join(s.nombre for s in turno.servicios.all())

        email_comprador_prueba = "test_user_1860959446082982366@testuser.com"

        preference_data = {
            "items": [
                {
                    "title": f"Saldo Turno - {servicios_nombres or 'Servicio'}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": round(float(monto_saldo), 2),
                }
            ],
            "payer": {
                "name": nombre_cliente,
                "email": email_comprador_prueba,
            },
            "back_urls": back_urls_dict,
            "auto_return": "approved",
            "external_reference": f"TURNO_SALDO_{turno.id}",
            "binary_mode": True,
            "statement_descriptor": self.statement_descriptor,
            "notification_url": f"{base_url}/api/mercadopago/webhook/"
        }

        try:
            result = self.sdk.preference().create(preference_data)
            res = result["response"]

            if result.get("status") not in [200, 201]:
                print(f"🔥 ERROR MP SALDO: {res}")
                return {"success": False, "error": res.get("message", "Error al crear preferencia en MP")}

            return {
                "success": True,
                "init_point": res.get("sandbox_init_point"),
                "preference_id": res["id"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reembolsar_pago(self, payment_id):
        """
        Reembolsa un pago aprobado usando el SDK oficial de Mercado Pago.
        """
        respuesta = self.sdk.refund().create(payment_id)
        
        if respuesta.get("status") in [200, 201]:
            return respuesta.get("response")
        else:
            mensaje_error = respuesta.get("response", {}).get("message", "Error desconocido de MP")
            raise Exception(f"Fallo al reembolsar en MP: {mensaje_error}")