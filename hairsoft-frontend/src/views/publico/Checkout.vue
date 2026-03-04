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

              <label class="delivery-card" :class="{ active: tipoEntrega === 'MOTO', 'is-loading': cargandoCosto }">
                  <input type="radio" v-model="tipoEntrega" value="MOTO" hidden :disabled="cargandoCosto">
                  <div class="card-icon">🛵</div>
                  <div class="card-content">
                    <span class="card-title">Moto Mandado</span>
                    <span class="card-desc">Solo válido para San Vicente.</span>
                  </div>
                  <div class="card-price loading-price" v-if="cargandoCosto">
                    <i class="ri-loader-4-line animate-spin"></i>
                  </div>
                  <div class="card-price" v-else>${{ costoMotoMandado.toLocaleString('es-AR') }}</div>
                </label>
            </div>
          </section>

          <transition name="fade">
            <section class="checkout-section" v-if="tipoEntrega !== 'RETIRO'">
              <h2 class="section-title"><span class="step-number">2</span> Datos del Envío</h2>
              <div class="form-grid">
                <div class="form-group full-width">
                  <label>Dirección Completa <span class="required">*</span></label>
                  <input v-model="direccion" type="text" placeholder="Calle, número, piso, depto..." class="modern-input">
                </div>
                <div class="form-group full-width">
                  <label>Observaciones / Referencias</label>
                  <textarea v-model="referencia" placeholder="Ej: Portón negro, timbre roto, dejar en recepción..." class="modern-textarea"></textarea>
                </div>
              </div>
            </section>
          </transition>

        </div>

        <div class="summary-column">
          <div class="summary-card">
            <h3>Resumen del Pedido</h3>
            
            <div v-if="cartStore.items.length === 0" class="empty-cart-msg">
              <i class="ri-shopping-cart-line"></i>
              <p>Tu carrito está vacío.</p>
            </div>

            <div v-else class="summary-items-list">
              <div v-for="item in cartStore.items" :key="item.id" class="summary-item">
                <div class="item-info">
                  <span class="item-qty">{{ item.cantidad }}x</span>
                  <span class="item-name">{{ item.nombre }}</span>
                </div>
                <span class="item-price">${{ (item.precio * item.cantidad).toLocaleString('es-AR') }}</span>
              </div>
            </div>
            
            <div class="divider"></div>
            
            <div class="summary-totals">
              <div class="total-row">
                <span>Subtotal</span>
                <span>${{ cartStore.precioTotal.toLocaleString('es-AR') }}</span>
              </div>
              <div class="total-row shipping">
                <span>Envío</span>
                <span v-if="cargandoCosto && tipoEntrega === 'MOTO'" class="shipping-loading">Calculando...</span>
                <span v-else class="shipping-cost">{{ costoEnvio > 0 ? `$${costoEnvio.toLocaleString('es-AR')}` : 'Gratis' }}</span>
              </div>
              <div class="total-row final">
                <span>Total a Pagar</span>
                <span>${{ totalFinal.toLocaleString('es-AR') }}</span>
              </div>
            </div>

            <button class="btn-checkout-action" @click="procesarPedido" :disabled="procesando || cartStore.items.length === 0 || cargandoCosto">
              <span v-if="!procesando"><i class="ri-secure-payment-line" style="margin-right: 8px;"></i> Pagar con Mercado Pago</span>
              <span v-else><i class="ri-loader-4-line animate-spin" style="margin-right: 8px;"></i> Procesando...</span>
            </button>

            <div class="security-badge">
              <i class="ri-lock-2-line"></i> Pago 100% seguro
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useCartStore } from '@/stores/cart';
import api from '@/services/api';
import Swal from 'sweetalert2';

const cartStore = useCartStore();
const tipoEntrega = ref('RETIRO');
const direccion = ref('');
const referencia = ref('');
const procesando = ref(false);

// Variables para el costo dinámico
const costoMotoMandado = ref(1500); 
const cargandoCosto = ref(true);

onMounted(async () => {
  try {
    // Apuntamos a la misma URL donde guardaste los datos recién
    const response = await api.get('/api/configuracion/');
    if (response.data && response.data.costo_envio_moto !== undefined) {
      costoMotoMandado.value = parseFloat(response.data.costo_envio_moto);
    }
  } catch (error) {
    console.error("No se pudo obtener el costo de envío, usando valor por defecto", error);
  } finally {
    cargandoCosto.value = false;
  }
});

const costoEnvio = computed(() => {
  if (tipoEntrega.value === 'MOTO') return costoMotoMandado.value;
  return 0;
});

const totalFinal = computed(() => cartStore.precioTotal + costoEnvio.value);

const procesarPedido = async () => {
  if (cartStore.items.length === 0) return;
  
  if (tipoEntrega.value !== 'RETIRO' && !direccion.value.trim()) {
    Swal.fire({ 
      title: 'Faltan datos', 
      text: "Por favor ingresa una dirección completa para el envío.", 
      icon: 'warning', 
      confirmButtonColor: '#0ea5e9'
    });
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
      icon: 'error',
      confirmButtonColor: '#ef4444'
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
  color: #0f172a;
}

.checkout-container {
  max-width: 1100px;
  margin: 0 auto;
}

/* ========================================
   📋 HEADER
   ======================================== */
.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #0f172a;
  margin-bottom: 8px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.page-header p {
  font-size: 1.1rem;
  color: #64748b;
}

/* ========================================
   📐 GRID LAYOUT
   ======================================== */
.checkout-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 30px;
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
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #f1f5f9;
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.35rem;
  color: #1e293b;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
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
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
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
  padding: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f8fafc;
  position: relative;
}

.delivery-card:not(.is-loading):hover {
  border-color: #cbd5e1;
  background: white;
}

.delivery-card.active {
  border-color: #0ea5e9;
  background: #f0f9ff;
}

.delivery-card.is-loading {
  opacity: 0.7;
  cursor: wait;
}

.card-icon {
  font-size: 2.5rem;
  line-height: 1;
  filter: grayscale(1);
  opacity: 0.5;
  transition: all 0.2s ease;
}

.delivery-card.active .card-icon {
  filter: grayscale(0);
  opacity: 1;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 1.1rem;
}

.card-desc {
  font-size: 0.9rem;
  color: #64748b;
}

.card-price {
  font-weight: 700;
  color: #0f172a;
  font-size: 1.15rem;
  padding: 6px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.card-price.free {
  color: #059669;
  background: #ecfdf5;
  border-color: #a7f3d0;
}

.card-price.loading-price {
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ========================================
   📝 FORMULARIOS
   ======================================== */
.form-grid {
  display: grid;
  gap: 16px;
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
  color: #475569;
  font-weight: 600;
  font-size: 0.9rem;
}

.required {
  color: #ef4444;
}

.modern-input,
.modern-textarea {
  width: 100%;
  padding: 14px 16px;
  border: 1.5px solid #cbd5e1;
  border-radius: 10px;
  background-color: white;
  font-size: 1rem;
  color: #1e293b;
  transition: all 0.2s ease;
}

.modern-input:focus,
.modern-textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
}

.modern-textarea {
  resize: vertical;
  min-height: 90px;
}

/* ========================================
   💳 SUMMARY CARD
   ======================================== */
.summary-column {
  position: relative;
}

.summary-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
  position: sticky;
  top: 24px;
}

.summary-card h3 {
  font-size: 1.35rem;
  color: #1e293b;
  margin-bottom: 24px;
  font-weight: 700;
}

.empty-cart-msg {
  text-align: center;
  padding: 20px 0;
  color: #94a3b8;
}

.empty-cart-msg i {
  font-size: 2.5rem;
  margin-bottom: 10px;
  display: block;
}

.summary-items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 350px;
  overflow-y: auto;
  padding-right: 5px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-qty {
  background: #e0f2fe;
  color: #0284c7;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
}

.item-name {
  color: #334155;
  font-weight: 500;
  font-size: 0.95rem;
}

.item-price {
  color: #0f172a;
  font-weight: 700;
  font-size: 1rem;
}

.divider {
  height: 1px;
  background: #e2e8f0;
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
  align-items: center;
  font-size: 1rem;
  color: #475569;
}

.total-row.shipping .shipping-cost {
  font-weight: 600;
  color: #0ea5e9;
}

.total-row.shipping .shipping-loading {
  font-style: italic;
  color: #94a3b8;
}

.total-row.final {
  padding-top: 16px;
  border-top: 2px dashed #e2e8f0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

/* ========================================
   🔘 BOTÓN DE CHECKOUT
   ======================================== */
.btn-checkout-action {
  width: 100%;
  margin-top: 24px;
  padding: 16px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1.05rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-checkout-action:hover:not(:disabled) {
  background: #0284c7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-checkout-action:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

/* ========================================
   🔒 SECURITY BADGE
   ======================================== */
.security-badge {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
}

/* ========================================
   🌀 ANIMACIONES
   ======================================== */
.animate-spin {
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>