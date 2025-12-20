<template>
  <div class="portal-proveedor">
    <div class="paper-container">
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando información del pedido...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="icon-error">🚫</div>
        <h2>Enlace no disponible</h2>
        <p>{{ error }}</p>
      </div>

      <div v-else class="pedido-content">
        <header class="header-pedido">
          <div class="brand">
            <h1>HairSoft <span class="badge">Portal Proveedores</span></h1>
          </div>
          <div class="meta-pedido">
            <p>Solicitud #{{ pedido.id }}</p>
            <p class="fecha">{{ formatearFecha(pedido.fecha_pedido) }}</p>
          </div>
        </header>

        <div v-if="pedido.estado !== 'ENVIADO'" class="banner-estado">
          <div class="icon-check">✅</div>
          <div>
            <h3>Pedido Confirmado</h3>
            <p>Ya hemos recibido tu respuesta para esta solicitud. ¡Muchas gracias!</p>
          </div>
        </div>

        <div v-else class="formulario-pedido">
          <div class="intro-text">
            <h2>Hola, {{ pedido.proveedor_nombre }} 👋</h2>
            <p>
              Por favor, confirmanos el stock y precio actual de los siguientes productos para preparar la orden de compra.
              Si no tenés stock, poné <strong>0</strong> en la cantidad.
            </p>
          </div>

          <div class="tabla-responsive">
            <table class="tabla-items">
              <thead>
                <tr>
                  <th class="col-prod">Producto</th>
                  <th class="col-num">Cantidad</th>
                  <th class="col-price">Precio Unit. ($)</th>
                  <th class="col-total">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="detalle in pedido.detalles" :key="detalle.id">
                  <td class="cell-prod">
                    <span class="nombre-prod">{{ detalle.producto_nombre }}</span>
                    <span class="codigo-prod">Cód: {{ detalle.producto_codigo || 'N/A' }}</span>
                  </td>
                  <td class="cell-input">
                    <input 
                      type="number" 
                      v-model.number="detalle.cantidad" 
                      min="0" 
                      class="input-modern input-qty"
                    >
                  </td>
                  <td class="cell-input">
                    <div class="input-group">
                      <span class="prefix">$</span>
                      <input 
                        type="number" 
                        v-model.number="detalle.precio_unitario" 
                        min="0" 
                        step="0.01" 
                        class="input-modern input-price"
                      >
                    </div>
                  </td>
                  <td class="cell-total">
                    ${{ (detalle.cantidad * detalle.precio_unitario).toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="3" class="text-right label-total">Total Estimado</td>
                  <td class="monto-total">${{ calcularTotal().toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div class="observaciones-box">
            <label>Comentarios adicionales (Opcional):</label>
            <textarea 
              v-model="comentarios" 
              placeholder="Ej: El envío sale mañana por la tarde..."
              rows="3"
            ></textarea>
          </div>

          <div class="actions-bar">
            <button class="btn-confirmar" @click="confirmarPedido" :disabled="enviando">
              <span v-if="!enviando">🚀 Confirmar Disponibilidad y Precios</span>
              <span v-else>Procesando...</span>
            </button>
          </div>
        </div>
      </div>
      
      <footer class="footer-portal">
        <p>Gestionado por <strong>HairSoft</strong> - Sistema de Gestión de Peluquerías</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';
import Swal from 'sweetalert2';

const route = useRoute();
const token = route.params.token;

const pedido = ref(null);
const loading = ref(true);
const error = ref(null);
const enviando = ref(false);
const comentarios = ref('');

// --- Carga Inicial ---
const cargarPedido = async () => {
  try {
    const res = await api.get(`/externo/pedido/${token}/`);
    pedido.value = res.data;
  } catch (err) {
    console.error(err);
    error.value = 'El pedido no existe o el enlace ya caducó.';
  } finally {
    loading.value = false;
  }
};

// --- Helpers ---
const formatearFecha = (fecha) => {
  if (!fecha) return '';
  return new Date(fecha).toLocaleDateString('es-AR', {
    day: 'numeric', month: 'long', year: 'numeric'
  });
};

const calcularTotal = () => {
  if (!pedido.value) return 0;
  return pedido.value.detalles.reduce((acc, item) => {
    return acc + ((item.cantidad || 0) * (item.precio_unitario || 0));
  }, 0);
};

// --- Acción Principal ---
const confirmarPedido = async () => {
  const totalItems = pedido.value.detalles.reduce((acc, item) => acc + item.cantidad, 0);
  
  if (totalItems === 0) {
    const result = await Swal.fire({
      title: '¿Confirmar con cantidad 0?',
      text: "Estás indicando que no tenés stock de NINGÚN producto.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, confirmar igual'
    });
    if (!result.isConfirmed) return;
  } else {
    const result = await Swal.fire({
      title: '¿Confirmar Pedido?',
      text: "Se actualizarán los precios y cantidades en el sistema de HairSoft.",
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#10b981',
      confirmButtonText: 'Sí, Confirmar'
    });
    if (!result.isConfirmed) return;
  }

  enviando.value = true;
  try {
    await api.post(`/externo/pedido/${token}/confirmar/`, {
      detalles: pedido.value.detalles,
      comentarios: comentarios.value 
    });

    await Swal.fire({
      title: '¡Excelente!',
      text: 'La confirmación se envió correctamente.',
      icon: 'success',
      confirmButtonColor: '#10b981'
    });
    
    cargarPedido();

  } catch (err) {
    Swal.fire('Error', 'Hubo un problema al guardar. Por favor, intentá de nuevo.', 'error');
  } finally {
    enviando.value = false;
  }
};

onMounted(() => {
  cargarPedido();
});
</script>

<style scoped>
/* --- DISEÑO PREMIUM REFINADO --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.portal-proveedor {
  background-color: #f3f4f6;
  min-height: 100vh;
  padding: 40px 20px;
  font-family: 'Inter', sans-serif;
  display: flex;
  justify-content: center;
}

.paper-container {
  background: white;
  width: 100%;
  max-width: 960px; /* Un poco más ancho para mejor respiro */
  border-radius: 16px;
  box-shadow: 0 10px 40px -10px rgba(0,0,0,0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Header */
.header-pedido {
  background: #1e293b;
  color: white;
  padding: 30px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-pedido h1 { margin: 0; font-size: 1.5rem; font-weight: 700; display: flex; align-items: center; gap: 15px; }
.badge { background: rgba(255,255,255,0.15); font-size: 0.8rem; padding: 4px 10px; border-radius: 20px; font-weight: 500; }
.meta-pedido { text-align: right; opacity: 0.9; font-size: 0.9rem; }
.meta-pedido .fecha { font-weight: 600; font-size: 1.1rem; }

/* Body */
.pedido-content { padding: 40px; flex: 1; }

.intro-text h2 { color: #111827; margin-top: 0; font-size: 1.8rem; margin-bottom: 0.5rem; }
.intro-text p { color: #4b5563; line-height: 1.6; max-width: 700px; margin-bottom: 40px; }

/* Tabla Estilizada */
.tabla-responsive { 
  overflow-x: auto; 
  margin-bottom: 40px; 
  border-radius: 8px; 
  border: 1px solid #e5e7eb; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.tabla-items { width: 100%; border-collapse: collapse; min-width: 700px; }

.tabla-items th {
  background: #f9fafb; 
  color: #6b7280; 
  font-weight: 600; 
  text-transform: uppercase;
  font-size: 0.75rem; 
  padding: 16px 24px; 
  text-align: left; 
  letter-spacing: 0.5px;
  border-bottom: 1px solid #e5e7eb;
}

.tabla-items td { padding: 16px 24px; border-top: 1px solid #e5e7eb; vertical-align: middle; }

/* Columnas & Alineación */
.col-prod { width: 40%; }
.col-num { width: 15%; text-align: center; }
.col-price { width: 25%; text-align: right; } /* Precio alineado a derecha */
.col-total { width: 20%; text-align: right; }

/* Celda Producto */
.cell-prod { display: flex; flex-direction: column; }
.nombre-prod { color: #111827; font-weight: 600; font-size: 1rem; margin-bottom: 4px; }
.codigo-prod { color: #9ca3af; font-size: 0.85rem; }

/* Celda Inputs */
.cell-input { vertical-align: middle; }

/* Inputs Modernos Refinados */
.input-modern {
  width: 100%; 
  padding: 10px 12px; 
  border: 1px solid #d1d5db; 
  border-radius: 6px;
  font-size: 1rem; 
  font-weight: 500; 
  color: #374151; 
  transition: all 0.2s; 
  background-color: #fff;
}
.input-modern:focus { 
  outline: none; 
  border-color: #3b82f6; 
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1); 
}

.input-qty { text-align: center; max-width: 80px; margin: 0 auto; display: block; }
.input-price { text-align: right; padding-left: 20px; } /* Espacio para el $ */

.input-group { position: relative; display: flex; align-items: center; justify-content: flex-end;}
.input-group .prefix { 
  position: absolute; 
  left: 10px; 
  color: #9ca3af; 
  pointer-events: none;
  font-weight: 500;
  z-index: 1; /* Asegura que el símbolo quede sobre el input */
}
/* Ajuste para que el texto no se monte sobre el símbolo $ */
.input-group input { padding-left: 24px; } 

.cell-total { text-align: right; font-weight: 700; color: #111827; font-size: 1.1rem; }

/* Footer Tabla */
tfoot td { background: #f8fafc; padding: 24px; border-top: 2px solid #e5e7eb; }
.label-total { font-size: 1.1rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
.monto-total { font-size: 1.6rem; color: #059669; font-weight: 800; text-align: right; }

/* Observaciones */
.observaciones-box { margin-bottom: 40px; background: #f9fafb; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; }
.observaciones-box label { display: block; font-weight: 600; color: #374151; margin-bottom: 10px; }
.observaciones-box textarea {
  width: 100%; padding: 12px; border: 1px solid #d1d5db; border-radius: 6px;
  font-family: inherit; resize: vertical; min-height: 100px; font-size: 0.95rem;
  background-color: white;
}
.observaciones-box textarea:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }


/* Botón Acción */
.actions-bar { display: flex; justify-content: flex-end; }
.btn-confirmar {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white; border: none; padding: 18px 48px; border-radius: 50px;
  font-size: 1.1rem; font-weight: 700; cursor: pointer;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}
.btn-confirmar:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5); }
.btn-confirmar:disabled { opacity: 0.6; cursor: not-allowed; filter: grayscale(0.5); }

/* Footer Page */
.footer-portal { text-align: center; padding: 30px; border-top: 1px solid #f3f4f6; color: #9ca3af; font-size: 0.9rem; background: #fdfdfd; }

/* Estados (Loading/Error/Success) */
.loading-state, .error-state { text-align: center; padding: 80px 20px; }
.spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3b82f6; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 24px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.banner-estado {
  background: #ecfdf5; border: 1px solid #10b981; border-radius: 12px;
  padding: 40px; display: flex; align-items: center; gap: 24px; margin-bottom: 20px;
}
.icon-check { font-size: 3.5rem; background: #10b981; color: white; width: 70px; height: 70px; border-radius: 50%; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }
.banner-estado h3 { color: #065f46; margin: 0 0 8px 0; font-size: 1.6rem; }
.banner-estado p { color: #047857; margin: 0; font-size: 1.1rem; }

@media (max-width: 640px) {
  .header-pedido { flex-direction: column; text-align: center; gap: 16px; padding: 24px; }
  .meta-pedido { text-align: center; }
  .pedido-content { padding: 24px; }
  .btn-confirmar { width: 100%; }
  .col-prod, .col-num, .col-price, .col-total { width: auto; } /* Reset width en móvil para que scrollee natural */
}
</style>