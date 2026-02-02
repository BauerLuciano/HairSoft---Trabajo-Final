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
            </div>
          </section>

          <section class="checkout-section" v-if="tipoEntrega !== 'RETIRO'">
            <h2 class="section-title"><span class="step-number">2</span> Datos del Envío</h2>
            <div class="form-grid">
              <div class="form-group full-width">
                <label>Dirección Completa</label>
                <input v-model="direccion" type="text" placeholder="Calle, número, piso, depto..." class="modern-input">
              </div>
              <div class="form-group full-width">
                <label>Observaciones / Referencias</label>
                <textarea v-model="referencia" placeholder="Ej: Portón negro, timbre roto, dejar en recepción..." class="modern-textarea"></textarea>
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
import api from '@/services/api';
import Swal from 'sweetalert2';

const cartStore = useCartStore();
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

const procesarPedido = async () => {
  if (cartStore.items.length === 0) return;
  
  if (tipoEntrega.value !== 'RETIRO' && !direccion.value.trim()) {
    Swal.fire({ title: 'Atención', text: "Por favor ingresa una dirección para el envío.", icon: 'warning', background: '#fff', color: '#000' });
    return;
  }

  procesando.value = true;

  try {
    const direccionFinal = tipoEntrega.value === 'RETIRO' 
      ? 'Retiro en Local' 
      : `${direccion.value.trim()} | Obs: ${referencia.value.trim() || 'Sin observaciones'}`;

    const payload = {
      tipo_entrega: tipoEntrega.value,
      costo_envio: costoEnvio.value,
      direccion_envio: direccionFinal,
      detalles: cartStore.items.map(item => ({ producto: item.id, cantidad: item.cantidad }))
    };

    const response = await api.post('/web/pedidos/', payload);

    if (response.data.url_pago) {
        cartStore.limpiarCarrito(); 
        window.location.href = response.data.url_pago;
    } else {
        throw new Error("No se recibió el link de pago.");
    }

  } catch (error) {
    console.error("Error checkout:", error);
    Swal.fire({ 
      title: 'Error', 
      text: error.response?.data?.message || "No se pudo procesar la compra. Reintente en unos minutos.", 
      icon: 'error' 
    });
  } finally {
    procesando.value = false;
  }
};
</script>

<style scoped>
/* ========================================
   🎨 VARIABLES Y BASE
   ======================================== */
.checkout-page {
  background: linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
  padding: 50px 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
}

.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* ========================================
   📋 HEADER
   ======================================== */
.page-header {
  margin-bottom: 50px;
  text-align: center;
}

.page-header h1 {
  font-size: 2.75rem;
  color: #0f172a;
  margin-bottom: 12px;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  font-size: 1.125rem;
  color: #64748b;
  font-weight: 400;
  letter-spacing: 0.01em;
}

/* ========================================
   📐 GRID LAYOUT
   ======================================== */
.checkout-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 40px;
  align-items: start;
}

@media (max-width: 968px) {
  .checkout-grid {
    grid-template-columns: 1fr;
  }
}

/* ========================================
   📦 SECCIONES
   ======================================== */
.checkout-section {
  background: white;
  padding: 35px;
  border-radius: 20px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.checkout-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 20px 25px -5px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 1.5rem;
  color: #0f172a;
  margin-bottom: 28px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.step-number {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

/* ========================================
   🚚 DELIVERY CARDS
   ======================================== */
.delivery-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.delivery-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 22px;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  background: #fafafa;
}

.delivery-card:hover {
  border-color: #cbd5e1;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.delivery-card.active {
  border-color: #0ea5e9;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  box-shadow: 0 8px 16px rgba(14, 165, 233, 0.15);
  transform: translateX(0);
}

.delivery-card.active::before {
  content: '✓';
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: #0ea5e9;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
}

.card-icon {
  font-size: 2.5rem;
  line-height: 1;
  filter: grayscale(0.3);
  transition: filter 0.2s ease;
}

.delivery-card.active .card-icon {
  filter: grayscale(0);
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 1.1rem;
  letter-spacing: -0.01em;
}

.card-desc {
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 400;
}

.card-price {
  font-weight: 700;
  color: #0f172a;
  font-size: 1.25rem;
  padding: 8px 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.card-price.free {
  color: #059669;
  background: #ecfdf5;
  border-color: #a7f3d0;
}

/* ========================================
   📝 FORMULARIOS
   ======================================== */
.form-grid {
  display: grid;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  color: #334155;
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: 0.01em;
}

.modern-input,
.modern-textarea {
  width: 100%;
  padding: 15px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background-color: #fafafa;
  font-size: 1rem;
  color: #0f172a;
  font-family: inherit;
  transition: all 0.2s ease;
}

.modern-input:hover,
.modern-textarea:hover {
  border-color: #cbd5e1;
  background-color: white;
}

.modern-input:focus,
.modern-textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  background-color: white;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}

.modern-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

/* ========================================
   💳 SUMMARY CARD
   ======================================== */
.summary-column {
  position: relative;
}

.summary-card {
  background: white;
  padding: 35px;
  border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 20px 25px -5px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  position: sticky;
  top: 30px;
}

.summary-card h3 {
  font-size: 1.5rem;
  color: #0f172a;
  margin-bottom: 24px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.summary-items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background: #f8fafc;
  border-radius: 10px;
  transition: background 0.2s ease;
}

.summary-item:hover {
  background: #f1f5f9;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-qty {
  background: #0ea5e9;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.9rem;
}

.item-name {
  color: #334155;
  font-weight: 500;
  font-size: 1rem;
}

.item-price {
  color: #0f172a;
  font-weight: 700;
  font-size: 1.05rem;
}

.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #e2e8f0, transparent);
  margin: 24px 0;
}

.summary-totals {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.05rem;
  color: #475569;
  font-weight: 500;
}

.total-row.shipping {
  color: #64748b;
}

.total-row.final {
  padding-top: 16px;
  border-top: 2px solid #e2e8f0;
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
}

.total-row.final span:last-child {
  color: #0ea5e9;
}

/* ========================================
   🔘 BOTÓN DE CHECKOUT
   ======================================== */
.btn-checkout-action {
  width: 100%;
  margin-top: 28px;
  padding: 18px 24px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 16px rgba(14, 165, 233, 0.25);
  letter-spacing: 0.02em;
}

.btn-checkout-action:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.35);
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
}

.btn-checkout-action:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-checkout-action:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  box-shadow: none;
}

/* ========================================
   🔒 SECURITY BADGE
   ======================================== */
.security-badge {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #64748b;
  font-size: 0.9rem;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  font-weight: 500;
}

.security-badge svg {
  opacity: 0.7;
}

/* ========================================
   📱 RESPONSIVE
   ======================================== */
@media (max-width: 968px) {
  .page-header h1 {
    font-size: 2rem;
  }

  .checkout-section {
    padding: 25px;
  }

  .summary-card {
    position: static;
    margin-top: 20px;
  }

  .delivery-card {
    padding: 18px;
  }

  .card-icon {
    font-size: 2rem;
  }
}

@media (max-width: 640px) {
  .checkout-page {
    padding: 30px 15px;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .section-title {
    font-size: 1.25rem;
  }

  .delivery-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .card-price {
    align-self: flex-end;
  }
}
</style>