<template>
  <div class="checkout-page">
    <div class="checkout-container">
      
      <div class="page-header">
        <h1>Finalizar Compra</h1>
        <p>Completá los datos para recibir tus productos.</p>
      </div>

      <div class="checkout-grid">
        
        <div class="form-column">
          
          <section class="checkout-section">
            <h2 class="section-title"><span class="step-number">1</span> Método de Entrega</h2>
            <div class="delivery-cards">
              <label class="delivery-card" :class="{ active: tipoEntrega === 'RETIRO' }">
                <input type="radio" v-model="tipoEntrega" value="RETIRO" hidden>
                <div class="card-icon">🏪</div>
                <div class="card-content">
                  <span class="card-title">Retiro en el Local</span>
                  <span class="card-desc">Pasás a buscarlo por la peluquería.</span>
                </div>
                <div class="card-price free">Gratis</div>
              </label>

              <label class="delivery-card" :class="{ active: tipoEntrega === 'MOTO' }">
                <input type="radio" v-model="tipoEntrega" value="MOTO" hidden>
                <div class="card-icon">🛵</div>
                <div class="card-content">
                  <span class="card-title">Moto Mandado</span>
                  <span class="card-desc">Solo válido para San Vicente.</span>
                </div>
                <div class="card-price">$1.500</div>
              </label>

              <label class="delivery-card" :class="{ active: tipoEntrega === 'CORREO' }">
                <input type="radio" v-model="tipoEntrega" value="CORREO" hidden>
                <div class="card-icon">📦</div>
                <div class="card-content">
                  <span class="card-title">Correo Argentino</span>
                  <span class="card-desc">Envío a todo el país.</span>
                </div>
                <div class="card-price">$8.000</div>
              </label>
            </div>
          </section>

          <section class="checkout-section" v-if="tipoEntrega !== 'RETIRO'">
            <h2 class="section-title"><span class="step-number">2</span> Datos del Envío</h2>
            <div class="form-grid">
              <div class="form-group full-width">
                <label>Dirección Completa</label>
                <input v-model="direccion" type="text" placeholder="Calle, número, piso..." class="modern-input">
              </div>
              <div class="form-group full-width">
                <label>Referencia</label>
                <textarea v-model="referencia" placeholder="Portón negro, dejar en recepción..." class="modern-textarea"></textarea>
              </div>
            </div>
          </section>

        </div>

        <div class="summary-column">
          <div class="summary-card">
            <h3>Resumen del Pedido</h3>
            <div class="summary-items-list">
              <div v-for="item in cartStore.items" :key="item.id" class="summary-item">
                <div class="item-info">
                  <span class="item-qty">{{ item.cantidad }}x</span>
                  <span class="item-name">{{ item.nombre }}</span>
                </div>
                <span class="item-price">${{ (item.precio * item.cantidad).toLocaleString() }}</span>
              </div>
            </div>
            <div class="divider"></div>
            <div class="summary-totals">
              <div class="total-row"><span>Subtotal</span><span>${{ cartStore.precioTotal.toLocaleString() }}</span></div>
              <div class="total-row shipping"><span>Envío</span><span>{{ costoEnvio > 0 ? `$${costoEnvio.toLocaleString()}` : 'Gratis' }}</span></div>
              <div class="total-row final"><span>Total</span><span>${{ totalFinal.toLocaleString() }}</span></div>
            </div>

            <button class="btn-checkout-action" @click="procesarPedido" :disabled="procesando || cartStore.items.length === 0">
              <span v-if="!procesando">Pagar con Mercado Pago</span>
              <span v-else>Procesando...</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useCartStore } from '@/stores/cart';
import api from '@/services/api'; // ✅ Usamos tu conexión inteligente
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';

const cartStore = useCartStore();
const router = useRouter();

const tipoEntrega = ref('RETIRO');
const direccion = ref('');
const referencia = ref('');
const procesando = ref(false);

const costoEnvio = computed(() => {
  if (tipoEntrega.value === 'MOTO') return 1500;
  if (tipoEntrega.value === 'CORREO') return 8000;
  return 0;
});

const totalFinal = computed(() => cartStore.precioTotal + costoEnvio.value);

// Checkout.vue -> Función procesarPedido corregida

const procesarPedido = async () => {
  if (cartStore.items.length === 0) return;
  
  if (tipoEntrega.value !== 'RETIRO' && !direccion.value.trim()) {
    Swal.fire({ title: 'Atención', text: "Por favor ingresa una dirección de envío.", icon: 'warning' });
    return;
  }

  procesando.value = true;

  try {
    const payload = {
      tipo_entrega: tipoEntrega.value,
      costo_envio: costoEnvio.value,
      direccion_envio: tipoEntrega.value !== 'RETIRO' ? `${direccion.value} (${referencia.value})` : 'Retiro en local',
      detalles: cartStore.items.map(item => ({ producto: item.id, cantidad: item.cantidad }))
    };

    // 1. Creamos el pedido en el Back (Nace como PENDIENTE_PAGO)
    const response = await api.post('/pedidos-web/', payload);

    if (response.data.url_pago) {
        // 2. Limpiamos el carrito (ya está guardado en la DB del Back)
        cartStore.limpiarCarrito(); 
        
        // 3. REDIRECCIÓN DIRECTA A MERCADO PAGO
        // El Back se encargará de mandarnos al listado de pedidos al volver
        window.location.href = response.data.url_pago;
    } else {
        throw new Error("No se recibió el link de pago.");
    }

  } catch (error) {
    console.error("Error checkout:", error);
    Swal.fire({ 
      title: 'Error', 
      text: error.response?.data?.message || "No se pudo procesar la compra.", 
      icon: 'error' 
    });
  } finally {
    procesando.value = false;
  }
};
</script>

<style scoped>
.checkout-page {
  background-color: #f8fafc;
  min-height: 100vh;
  padding: 40px 20px;
  font-family: 'Segoe UI', sans-serif;
}

.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #1e293b;
  margin-bottom: 10px;
  font-weight: 800;
}

.page-header p {
  color: #64748b;
  font-size: 1.1rem;
}

.checkout-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr; /* Columna izquierda más ancha */
  gap: 40px;
  align-items: start;
}

/* Columna de Formularios */
.form-column {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.checkout-section {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.section-title {
  font-size: 1.4rem;
  color: #0f172a;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-number {
  background: #0ea5e9;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
}

/* Tarjetas de Envío */
.delivery-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.delivery-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.delivery-card:hover {
  border-color: #cbd5e1;
  background-color: #f8fafc;
}

.delivery-card.active {
  border-color: #0ea5e9;
  background-color: #f0f9ff;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}

.card-icon {
  font-size: 1.8rem;
  background: white;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 1.05rem;
}

.card-desc {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 4px;
}

.card-price {
  font-weight: 700;
  font-size: 1.1rem;
  color: #0f172a;
}

.card-price.free {
  color: #10b981;
}

/* Inputs */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #334155;
  font-size: 0.95rem;
}

.modern-input, .modern-textarea {
  width: 100%;
  padding: 14px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 1rem;
  color: #1e293b;
  transition: border-color 0.2s;
  background-color: #f8fafc;
}

.modern-input:focus, .modern-textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.modern-textarea {
  resize: vertical;
  min-height: 100px;
}

/* Resumen (Columna Derecha) */
.summary-column {
  position: sticky;
  top: 20px;
}

.summary-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.summary-card h3 {
  margin: 0 0 20px 0;
  font-size: 1.3rem;
  color: #0f172a;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 15px;
}

.summary-items-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
  padding-right: 5px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-size: 0.95rem;
}

.item-info {
  display: flex;
  gap: 8px;
  color: #334155;
}

.item-qty {
  font-weight: 700;
  color: #0ea5e9;
}

.item-price {
  font-weight: 600;
  color: #1e293b;
}

.divider {
  height: 1px;
  background-color: #e2e8f0;
  margin: 20px 0;
}

.summary-totals {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: 1rem;
}

.total-row.shipping {
  color: #10b981;
}

.total-row.final {
  margin-top: 10px;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
}

/* Botón de Pago */
.btn-checkout-action {
  width: 100%;
  margin-top: 25px;
  padding: 18px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-checkout-action:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(14, 165, 233, 0.4);
}

.btn-checkout-action:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.security-badge {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.85rem;
}

/* Responsive */
@media (max-width: 900px) {
  .checkout-grid {
    grid-template-columns: 1fr;
  }
  .summary-column {
    order: -1; /* Muestra el resumen primero en móviles */
    position: static;
  }
}
</style>