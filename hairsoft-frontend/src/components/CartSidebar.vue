<template>
  <Transition name="slide-fade">
    <div v-if="cartStore.isCartOpen" class="cart-backdrop" @click="cartStore.toggleCart">
      <div class="cart-panel" @click.stop>
        
        <div class="cart-header">
          <div class="header-title">
            <h2>Mi Carrito</h2>
            <span class="badge-count">{{ cartStore.cantidadTotal }}</span>
          </div>
          <button class="btn-close" @click="cartStore.toggleCart">
            <X :size="24" />
          </button>
        </div>

        <div class="cart-body">
          <div v-if="cartStore.items.length === 0" class="cart-empty">
            <div class="empty-state-icon">
              <ShoppingCart :size="64" stroke-width="1.5" />
            </div>
            <h3>Tu carrito está vacío</h3>
            <p>¡Explorá nuestros productos y encontrá lo que buscás!</p>
            <button class="btn-seguir" @click="cartStore.toggleCart">
              Ir al Catálogo
            </button>
          </div>

          <div v-else class="cart-items-list">
            <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
              <div class="item-image-wrapper">
                <img :src="getImageUrl(item.imagen)" :alt="item.nombre" />
              </div>
              
              <div class="item-content">
                <div class="item-info">
                  <h4>{{ item.nombre }}</h4>
                  <button class="btn-remove-text" @click="cartStore.removerProducto(item.id)">
                    Eliminar
                  </button>
                </div>
                
                <div class="item-actions">
                  <div class="quantity-control">
                    <button 
                      @click="cartStore.actualizarCantidad(item.id, item.cantidad - 1)" 
                      class="qty-btn"
                    >-</button>
                    <span class="qty-value">{{ item.cantidad }}</span>
                    <button 
                      @click="cartStore.actualizarCantidad(item.id, item.cantidad + 1)" 
                      class="qty-btn"
                      :disabled="item.cantidad >= item.stock_max"
                    >+</button>
                  </div>
                  <div class="item-price">
                    ${{ Number(item.precio * item.cantidad).toLocaleString() }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="cartStore.items.length > 0" class="cart-footer">
          <div class="summary-row">
            <span>Subtotal</span>
            <span class="amount">${{ Number(cartStore.precioTotal).toLocaleString() }}</span>
          </div>
          
          <button class="btn-checkout" @click="irAlCheckout">
            Iniciar Compra
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </button>
        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useCartStore } from '@/stores/cart';
import { useRouter } from 'vue-router';
import { X, ShoppingCart, Trash2 } from 'lucide-vue-next';

const cartStore = useCartStore();
const router = useRouter();

const getImageUrl = (img) => {
  if (!img) return '/placeholder.png';
  if (img.startsWith('http')) return img;
  return `http://127.0.0.1:8000${img}`;
};

const irAlCheckout = () => {
  cartStore.toggleCart();
  router.push('/checkout');
};
</script>

<style scoped>
.cart-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(15, 23, 42, 0.6); /* Fondo oscuro semitransparente */
  backdrop-filter: blur(4px); /* Efecto blur moderno */
  z-index: 9999;
  display: flex;
  justify-content: flex-end;
}

.cart-panel {
  width: 100%;
  max-width: 450px; /* Un poco más ancho */
  height: 100%;
  background: white;
  display: flex;
  flex-direction: column;
  box-shadow: -10px 0 30px rgba(0,0,0,0.15);
}

/* HEADER */
.cart-header {
  padding: 25px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
}

.badge-count {
  background: #0ea5e9;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  padding: 2px 10px;
  border-radius: 20px;
}

.btn-close {
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #e2e8f0;
  color: #0f172a;
}

/* BODY */
.cart-body {
  flex: 1;
  overflow-y: auto;
  padding: 25px;
  background-color: #fff;
}

/* Empty State */
.cart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #64748b;
}

.empty-state-icon {
  background: #f0f9ff;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0ea5e9;
  margin-bottom: 20px;
}

.cart-empty h3 {
  color: #0f172a;
  font-size: 1.25rem;
  margin-bottom: 8px;
}

.btn-seguir {
  margin-top: 25px;
  padding: 12px 24px;
  background: #0f172a;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-seguir:hover {
  background: #1e293b;
}

/* Items List */
.cart-items-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cart-item {
  display: flex;
  gap: 16px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}

.item-image-wrapper {
  width: 90px;
  height: 90px;
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.item-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.item-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.item-info h4 {
  margin: 0;
  font-size: 1rem;
  color: #0f172a;
  font-weight: 600;
  line-height: 1.4;
  margin-right: 10px;
}

.btn-remove-text {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.quantity-control {
  display: flex;
  align-items: center;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.qty-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #0f172a;
  transition: background 0.2s;
}

.qty-btn:hover:not(:disabled) {
  background: #f1f5f9;
}

.qty-btn:disabled {
  color: #cbd5e1;
  cursor: not-allowed;
}

.qty-value {
  width: 32px;
  text-align: center;
  color: black;
  font-size: 0.95rem;
  font-weight: 600;
  border-left: 1px solid #f1f5f9;
  border-right: 1px solid #f1f5f9;
}

.item-price {
  font-weight: 700;
  font-size: 1.1rem;
  color: #0f172a;
}

/* FOOTER */
.cart-footer {
  padding: 30px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 1.2rem;
  color: #0f172a;
  font-weight: 700;
}

.amount {
  font-size: 1.5rem;
  color: #0ea5e9;
}

.btn-checkout {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-checkout:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4);
}

/* ANIMACIONES */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: opacity 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active .cart-panel {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-fade-leave-active .cart-panel {
  transition: transform 0.3s ease-in;
}

.slide-fade-enter-from .cart-panel,
.slide-fade-leave-to .cart-panel {
  transform: translateX(100%);
}
</style>