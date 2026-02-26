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

        <div v-if="pedido.estado !== 'ENVIADO' && pedido.estado !== 'PENDIENTE'" class="banner-estado">
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
              Por favor, revisá lo que te solicitamos. Podés modificar la cantidad si tenés menos stock, 
              pero <strong>no podés superar la cantidad solicitada</strong>.
            </p>
          </div>

          <div class="tabla-responsive">
            <table class="tabla-items">
              <thead>
                <tr>
                  <th class="col-prod">Producto</th>
                  <th class="col-num text-center">Solicitado</th>
                  <th class="col-num text-center">Tu Stock</th>
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
                  
                  <td class="cell-display text-center">
                    <span class="badge-solicitado">{{ detalle.cantidad_original }} u.</span>
                  </td>

                  <td class="cell-input">
                    <input 
                      type="number" 
                      v-model.number="detalle.cantidad" 
                      min="0" 
                      :max="detalle.cantidad_original"
                      class="input-modern input-qty"
                      :class="{ 'input-error': detalle.cantidad > detalle.cantidad_original }"
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
                    ${{ (detalle.cantidad * (detalle.precio_unitario || 0)).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="4" class="text-right label-total">Total Estimado</td>
                  <td class="monto-total">${{ calcularTotal().toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div class="delivery-box">
            <label class="label-importante">📅 ¿Cuándo estimás que podrías entregar este pedido?</label>
            <input 
              type="date" 
              v-model="fechaEntrega" 
              class="input-modern date-picker" 
              :min="new Date().toISOString().split('T')[0]"
              required
            >
            <p class="help-text">Seleccioná una fecha tentativa de llegada al local.</p>
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
              <span v-if="!enviando">Confirmar Disponibilidad y Precios</span>
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
import axios from 'axios';
import Swal from 'sweetalert2';

const route = useRoute();
const token = route.params.token;
const API_URL = 'http://127.0.0.1:8000/api'; 

const pedido = ref(null);
const loading = ref(true);
const error = ref(null);
const enviando = ref(false);
const comentarios = ref('');
const fechaEntrega = ref('');

const cargarPedido = async () => {
  try {
    const res = await axios.get(`${API_URL}/externo/pedido/${token}/`);
    pedido.value = res.data;
    if (pedido.value.detalles) {
      pedido.value.detalles.forEach(d => { d.cantidad_original = d.cantidad; });
    }
  } catch (err) {
    error.value = 'El pedido no existe o el enlace ya caducó.';
  } finally {
    loading.value = false;
  }
};

const formatearFecha = (fecha) => {
  if (!fecha) return '';
  return new Date(fecha).toLocaleDateString('es-AR', { day: 'numeric', month: 'long', year: 'numeric' });
};

const calcularTotal = () => {
  if (!pedido.value) return 0;
  return pedido.value.detalles.reduce((acc, item) => acc + ((item.cantidad || 0) * (item.precio_unitario || 0)), 0);
};

const confirmarPedido = async () => {
  if (!fechaEntrega.value) {
    Swal.fire('Atención', 'Por favor, seleccioná una fecha estimada de entrega.', 'warning');
    return;
  }

  const excedidos = pedido.value.detalles.filter(d => d.cantidad > d.cantidad_original);
  if (excedidos.length > 0) {
    Swal.fire({ title: 'Cantidades Excedidas', text: 'No podés enviar más de lo solicitado.', icon: 'error' });
    return;
  }

  const result = await Swal.fire({
    title: '¿Confirmar Envío?',
    text: "Se notificará al local con tus precios y fecha de entrega.",
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Sí, Confirmar'
  });

  if (!result.isConfirmed) return;

  enviando.value = true;
  try {
    await axios.post(`${API_URL}/externo/pedido/${token}/confirmar/`, {
      detalles: pedido.value.detalles,
      comentarios: comentarios.value,
      fecha_entrega: fechaEntrega.value 
    });

    await Swal.fire({ title: '¡Éxito!', text: 'Respuesta enviada correctamente.', icon: 'success' });
    cargarPedido();
  } catch (err) {
    Swal.fire('Error', 'No se pudo guardar la respuesta.', 'error');
  } finally {
    enviando.value = false;
  }
};

onMounted(() => { cargarPedido(); });
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800&display=swap');

/* ─── LAYOUT ────────────────────────────────────────── */
.portal-proveedor {
  background-color: #f3f4f6;
  min-height: 100vh;
  padding: 48px 20px;
  font-family: 'Inter', sans-serif;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  color: #1f2937;
}

.paper-container {
  background: #ffffff;
  width: 100%;
  max-width: 1024px;
  border-radius: 20px;
  box-shadow:
    0 0 0 1px rgba(0,0,0,0.06),
    0 4px 6px -2px rgba(0,0,0,0.05),
    0 24px 48px -12px rgba(0,0,0,0.14);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ─── HEADER ────────────────────────────────────────── */
.header-pedido {
  background: #111827;
  padding: 26px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  border-bottom: 3px solid #10b981;
}

.header-pedido h1 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: #f9fafb;
  letter-spacing: -0.4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge {
  background: #10b981;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 4px 11px;
  border-radius: 99px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.meta-pedido { text-align: right; line-height: 1.4; }
.meta-pedido p { margin: 0; font-size: 0.88rem; color: #6b7280; font-weight: 500; }
.meta-pedido p:first-child { color: #f9fafb; font-weight: 700; font-size: 0.97rem; margin-bottom: 2px; }
.fecha { color: #4b5563 !important; font-size: 0.82rem !important; }

/* ─── BODY ──────────────────────────────────────────── */
.pedido-content { flex: 1; display: flex; flex-direction: column; }

.formulario-pedido { padding: 40px; flex: 1; }

.intro-text {
  margin-bottom: 36px;
  padding-bottom: 28px;
  border-bottom: 1px solid #e5e7eb;
}

.intro-text h2 {
  color: #111827;
  font-weight: 800;
  font-size: 1.65rem;
  margin: 0 0 10px;
  letter-spacing: -0.5px;
}

.intro-text p {
  color: #4b5563;
  font-size: 0.97rem;
  font-weight: 400;
  margin: 0;
  line-height: 1.65;
}

.intro-text strong { color: #111827; font-weight: 700; }

/* ─── TABLA ─────────────────────────────────────────── */
.tabla-responsive {
  overflow-x: auto;
  margin-bottom: 28px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.tabla-items {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.tabla-items thead {
  background: #f9fafb;
}

.tabla-items th {
  color: #6b7280;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  padding: 13px 20px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.tabla-items tbody tr {
  transition: background 0.12s ease;
}

.tabla-items tbody tr:hover {
  background: #f9fafb;
}

.tabla-items td {
  padding: 15px 20px;
  border-top: 1px solid #f3f4f6;
  color: #1f2937;
  font-weight: 400;
  vertical-align: middle;
}

.nombre-prod {
  display: block;
  color: #111827;
  font-weight: 600;
  font-size: 0.97rem;
  margin-bottom: 3px;
}

.codigo-prod {
  display: block;
  color: #9ca3af;
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* Badge solicitado */
.badge-solicitado {
  display: inline-flex;
  align-items: center;
  background: #f3f4f6;
  color: #374151;
  padding: 5px 13px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.88rem;
  border: 1px solid #e5e7eb;
}

/* ─── INPUTS ────────────────────────────────────────── */
.input-modern {
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid #d1d5db;
  border-radius: 8px;
  background: #fff;
  color: #111827;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.95rem;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
  -moz-appearance: textfield;
}

.input-modern::-webkit-outer-spin-button,
.input-modern::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }

.input-modern:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.input-modern.input-error {
  border-color: #ef4444 !important;
  background: #fef2f2;
  box-shadow: 0 0 0 3px rgba(239,68,68,0.1);
}

.input-qty {
  text-align: center;
  max-width: 90px;
  color: #059669;
  border-color: #6ee7b7;
  background: #f0fdf4;
  font-weight: 700;
}

.input-qty:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16,185,129,0.12);
}

.input-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.prefix {
  color: #9ca3af;
  font-weight: 600;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.input-price { max-width: 120px; }

/* Totales */
.text-right { text-align: right; }
.text-center { text-align: center; }

.cell-total {
  font-weight: 700;
  color: #111827;
  font-size: 0.97rem;
  white-space: nowrap;
}

.tabla-items tfoot tr { background: #f9fafb; }

.tabla-items tfoot td {
  padding-top: 16px;
  padding-bottom: 16px;
  border-top: 2px solid #e5e7eb;
}

.label-total {
  color: #6b7280;
  font-weight: 600;
  font-size: 0.9rem;
  text-align: right;
  padding-right: 20px;
}

.monto-total {
  color: #059669;
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  white-space: nowrap;
}

/* ─── DELIVERY BOX ──────────────────────────────────── */
.delivery-box {
  margin-bottom: 20px;
  background: #eff6ff;
  padding: 22px 26px;
  border-radius: 12px;
  border: 1.5px solid #bfdbfe;
}

.label-importante {
  display: block;
  font-weight: 700;
  color: #1d4ed8;
  margin-bottom: 12px;
  font-size: 0.95rem;
}

.date-picker {
  max-width: 240px;
  border-color: #93c5fd;
  color: #1e40af;
  background: #fff;
  font-weight: 600;
}

.date-picker:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.12);
}

.help-text {
  color: #3b82f6;
  font-size: 0.8rem;
  font-weight: 500;
  margin: 8px 0 0;
}

/* ─── OBSERVACIONES ─────────────────────────────────── */
.observaciones-box {
  margin-bottom: 36px;
  background: #fafafa;
  padding: 22px 26px;
  border-radius: 12px;
  border: 1.5px solid #e5e7eb;
}

.observaciones-box label {
  display: block;
  color: #374151;
  font-weight: 600;
  font-size: 0.88rem;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.observaciones-box textarea {
  width: 100%;
  padding: 10px 13px;
  border: 1.5px solid #d1d5db;
  border-radius: 8px;
  color: #111827;
  background: #fff;
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  font-weight: 400;
  resize: vertical;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
  line-height: 1.6;
}

.observaciones-box textarea::placeholder { color: #9ca3af; }

.observaciones-box textarea:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.12);
}

/* ─── BOTÓN ─────────────────────────────────────────── */
.actions-bar {
  display: flex;
  justify-content: flex-end;
}

.btn-confirmar {
  background: #059669;
  color: #fff;
  padding: 15px 40px;
  border: none;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: -0.1px;
  box-shadow: 0 4px 0 #047857, 0 8px 24px rgba(5,150,105,0.28);
  transition: background 0.15s, transform 0.12s, box-shadow 0.12s, opacity 0.15s;
}

.btn-confirmar:hover:not(:disabled) {
  background: #047857;
  transform: translateY(-2px);
  box-shadow: 0 6px 0 #065f46, 0 14px 32px rgba(5,150,105,0.32);
}

.btn-confirmar:active:not(:disabled) {
  transform: translateY(2px);
  box-shadow: 0 1px 0 #047857;
}

.btn-confirmar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ─── BANNER CONFIRMADO ─────────────────────────────── */
.banner-estado {
  margin: 36px 40px;
  background: #ecfdf5;
  border: 1.5px solid #6ee7b7;
  border-radius: 14px;
  padding: 26px 30px;
  display: flex;
  align-items: center;
  gap: 18px;
  color: #064e3b;
}

.banner-estado h3 {
  margin: 0 0 4px;
  font-size: 1.05rem;
  font-weight: 800;
  color: #065f46;
}

.banner-estado p {
  margin: 0;
  font-size: 0.93rem;
  color: #047857;
}

.icon-check { font-size: 1.75rem; flex-shrink: 0; }

/* ─── LOADING / ERROR ───────────────────────────────── */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 80px 40px;
  color: #6b7280;
  font-size: 0.97rem;
}

.error-state h2 {
  color: #111827;
  font-weight: 800;
  margin: 0;
  font-size: 1.3rem;
}

.icon-error { font-size: 2.5rem; }

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e5e7eb;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ─── FOOTER ────────────────────────────────────────── */
.footer-portal {
  padding: 18px 40px;
  color: #9ca3af;
  font-size: 0.8rem;
  font-weight: 500;
  border-top: 1px solid #f3f4f6;
  text-align: center;
}

.footer-portal strong { color: #6b7280; font-weight: 600; }

/* ─── RESPONSIVE ────────────────────────────────────── */
@media (max-width: 640px) {
  .portal-proveedor { padding: 0; background: #fff; }
  .paper-container { border-radius: 0; box-shadow: none; }
  .header-pedido { padding: 20px 20px; flex-direction: column; align-items: flex-start; gap: 10px; }
  .meta-pedido { text-align: left; }
  .formulario-pedido { padding: 20px; }
  .banner-estado { margin: 20px; }
  .actions-bar { justify-content: stretch; }
  .btn-confirmar { width: 100%; text-align: center; }
}
</style>