<template>
  <Transition name="cart-slide">
    <div v-if="cartStore.isCartOpen" class="cart-overlay" @click="cartStore.toggleCart">
      <div class="cart-container" @click.stop>
        
        <div class="cart-header">
          <div class="header-main">
            <div class="title-group">
              <div class="icon-circle">
                <ShoppingCart :size="20" />
              </div>
              <div>
                <h2>Tu Pedido</h2>
                <div class="item-count">
                  <span class="count-pill">
                    {{ cartStore.items.length }} {{ cartStore.items.length === 1 ? 'producto' : 'productos' }}
                  </span>
                  <span class="dot-separator">•</span>
                  <span class="units-text">
                    {{ cartStore.cantidadTotal }} {{ cartStore.cantidadTotal === 1 ? 'unidad' : 'unidades' }}
                  </span>
                </div>
              </div>
            </div>
            <button class="close-pill" @click="cartStore.toggleCart">
              Cerrar <X :size="18" />
            </button>
          </div>

          <div class="shipping-incentive">
            <p v-if="cartStore.precioTotal < 15000">
              Estás a <strong>${{ (15000 - cartStore.precioTotal).toLocaleString() }}</strong> del envío gratis
            </p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: Math.min((cartStore.precioTotal / 15000) * 100, 100) + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="cart-scroll-area">
          <div v-if="cartStore.items.length === 0" class="empty-basket">
            <div class="empty-illustration">
              <div class="blob"></div>
              <ShoppingCart :size="80" stroke-width="1" />
            </div>
            <h3>Tu carrito está vacío</h3>
            <p>Parece que todavía no sumaste nada. ¡Nuestros productos te esperan!</p>
            <button class="btn-explore" @click="cartStore.toggleCart">
              Explorar Catálogo
            </button>
          </div>

          <div v-else class="items-grid">
            <TransitionGroup name="list">
              <div v-for="item in cartStore.items" :key="item.id" class="product-row">
                <div class="product-img-box">
                  <img :src="getImageUrl(item.imagen)" :alt="item.nombre" />
                </div>
                
                <div class="product-details">
                  <div class="product-top">
                    <h4>{{ item.nombre }}</h4>
                    <button class="delete-icon" @click="cartStore.removerProducto(item.id)">
                      <Trash2 :size="18" />
                    </button>
                  </div>
                  
                  <div class="product-bottom">
                    <div class="stepper">
                      <button @click="cartStore.actualizarCantidad(item.id, item.cantidad - 1)" :disabled="item.cantidad <= 1">-</button>
                      <span class="qty">{{ item.cantidad }}</span>
                      <button @click="cartStore.actualizarCantidad(item.id, item.cantidad + 1)" :disabled="item.cantidad >= item.stock_max">+</button>
                    </div>
                    <div class="subtotal-price">
                      ${{ Number(item.precio * item.cantidad).toLocaleString() }}
                    </div>
                  </div>
                </div>
              </div>
            </TransitionGroup>
          </div>
        </div>

        <div v-if="cartStore.items.length > 0" class="cart-checkout-footer">
          <div class="summary-card">
            <div class="summary-line">
              <span>Subtotal</span>
              <span>${{ Number(cartStore.precioTotal).toLocaleString() }}</span>
            </div>
            <div class="summary-line total-highlight">
              <span>Total final</span>
              <span class="total-amount">${{ Number(cartStore.precioTotal).toLocaleString() }}</span>
            </div>
          </div>
          
          <button class="main-checkout-btn" @click="irAlCheckout">
            <span>Iniciar Compra</span>
            <div class="btn-icon">
              <ArrowRight :size="20" />
            </div>
          </button>

          <p class="secure-info">
            <ShieldCheck :size="12" /> Transacción protegida por Mercado Pago
          </p>
        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useCartStore } from '@/stores/cart';
import { useRouter } from 'vue-router';
import { X, ShoppingCart, Trash2, ArrowRight, ShieldCheck, CheckCircle } from 'lucide-vue-next';

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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.cart-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  justify-content: flex-end;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.cart-container {
  width: 100%;
  max-width: 520px; /* Ancho ideal para PC */
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  box-shadow: -20px 0 60px rgba(0, 0, 0, 0.2);
}

/* HEADER */
.cart-header {
  padding: 35px 30px 20px;
  background: white;
  border-bottom: 1px solid #f1f5f9;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-circle {
  width: 48px; height: 48px;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
}

.title-group h2 {
  margin: 0; font-size: 1.5rem; font-weight: 800; color: #0f172a;
}

.item-count {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.count-pill {
  font-size: 0.8rem;
  color: #1e40af;
  font-weight: 700;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 6px;
}

.units-text {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.dot-separator { color: #cbd5e1; }

.close-pill {
  background: #f8fafc; border: 1px solid #e2e8f0;
  padding: 10px 18px; border-radius: 50px;
  font-size: 0.85rem; font-weight: 700; color: #64748b;
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; transition: 0.3s;
}
.close-pill:hover { background: #0f172a; color: #fff; border-color: #0f172a; }

/* BARRA DE PROGRESO */
.shipping-incentive {
  background: #f8fafc; border-radius: 16px; padding: 15px;
}
.shipping-incentive p {
  margin: 0 0 10px; font-size: 0.85rem; color: #475569; font-weight: 500;
}
.success-text { color: #059669 !important; font-weight: 700; display: flex; align-items: center; gap: 6px; }

.progress-bar {
  height: 8px; background: #e2e8f0; border-radius: 10px; overflow: hidden;
}
.progress-fill {
  height: 100%; background: linear-gradient(to right, #1e40af, #3b82f6);
  transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ÁREA DE PRODUCTOS */
.cart-scroll-area {
  flex: 1; overflow-y: auto; padding: 30px;
}

.items-grid { display: flex; flex-direction: column; gap: 15px; }

.product-row {
  display: flex; gap: 18px; padding: 18px;
  background: #fff; border: 1px solid #f1f5f9;
  border-radius: 24px; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.product-row:hover { border-color: #3b82f6; transform: translateX(-5px); box-shadow: 10px 10px 30px rgba(15, 23, 42, 0.05); }

.product-img-box {
  width: 95px; height: 95px; border-radius: 18px;
  background: #f8fafc; border: 1px solid #f1f5f9;
  display: flex; align-items: center; justify-content: center; overflow: hidden;
  flex-shrink: 0;
}
.product-img-box img { width: 85%; height: 85%; object-fit: contain; }

.product-details { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }

.product-top { display: flex; justify-content: space-between; align-items: flex-start; }
.product-top h4 { margin: 0; font-size: 1.05rem; font-weight: 700; color: #1e293b; line-height: 1.4; }

.delete-icon {
  background: transparent; border: none; color: #cbd5e1;
  cursor: pointer; transition: 0.2s; padding: 5px;
}
.delete-icon:hover { color: #ef4444; }

.product-bottom { display: flex; justify-content: space-between; align-items: center; }

.stepper {
  display: flex; align-items: center; background: #f1f5f9;
  border-radius: 12px; padding: 5px;
}
.stepper button {
  width: 30px; height: 30px; border: none; background: white;
  border-radius: 10px; cursor: pointer; font-weight: 800; font-size: 1.1rem;
  color: #1e3a8a; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: 0.2s;
}
.stepper button:disabled { opacity: 0.3; cursor: not-allowed; }
.qty { width: 38px; text-align: center; font-weight: 800; color: #0f172a; }

.subtotal-price { font-weight: 800; font-size: 1.2rem; color: #1e40af; }

/* EMPTY STATE */
.empty-basket {
  height: 80%; display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center;
}
.empty-illustration { position: relative; margin-bottom: 35px; color: #dbeafe; }
.blob {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 150px; height: 150px; background: #eff6ff; border-radius: 50%; z-index: -1;
}

.btn-explore {
  margin-top: 30px; padding: 16px 35px; background: #0f172a;
  color: white; border: none; border-radius: 16px;
  font-weight: 700; cursor: pointer; transition: 0.3s;
}

/* FOOTER */
.cart-checkout-footer {
  padding: 35px 30px; background: white;
  border-top: 1px solid #f1f5f9;
}

.summary-card {
  background: #f8fafc; border-radius: 20px; padding: 25px; margin-bottom: 25px;
  border: 1px solid #f1f5f9;
}
.summary-line {
  display: flex; justify-content: space-between; margin-bottom: 12px;
  color: #64748b; font-weight: 600;
}
.total-highlight {
  margin-top: 15px; padding-top: 15px; border-top: 2px dashed #cbd5e1;
  color: #0f172a;
}
.total-amount { font-size: 1.8rem; font-weight: 900; color: #1e40af; }

.main-checkout-btn {
  width: 100%; height: 70px; border: none; border-radius: 20px;
  background: linear-gradient(135deg, #1e40af 0%, #0f172a 100%);
  color: white; font-size: 1.15rem; font-weight: 800;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 30px; cursor: pointer; transition: 0.4s;
  box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
}
.main-checkout-btn:hover { transform: translateY(-3px); box-shadow: 0 15px 40px rgba(30, 58, 138, 0.4); }

.btn-icon {
  width: 38px; height: 38px; background: rgba(255,255,255,0.15);
  border-radius: 12px; display: flex; align-items: center; justify-content: center;
}

.secure-info {
  text-align: center; font-size: 0.75rem; color: #94a3b8; margin-top: 20px;
  display: flex; align-items: center; justify-content: center; gap: 6px; font-weight: 500;
}

/* ANIMACIONES */
.cart-slide-enter-active, .cart-slide-leave-active { transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
.cart-slide-enter-from, .cart-slide-leave-to { opacity: 0; }
.cart-slide-enter-from .cart-container { transform: translateX(100%); }
.cart-slide-leave-to .cart-container { transform: translateX(100%); }

.list-enter-active, .list-leave-active { transition: all 0.4s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: scale(0.9); }

@media (max-width: 640px) {
  .cart-container { max-width: 100%; }
  .main-checkout-btn { height: 60px; padding: 0 20px; }
}
</style>