<template>
  <div class="cotizacion-container">
    
    <div v-if="cargando" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando solicitud...</p>
    </div>

    <div v-else-if="error" class="card error-card">
      <div class="icon">❌</div>
      <h2>Enlace inválido o expirado</h2>
      <p>{{ mensajeError }}</p>
    </div>

    <div v-else-if="enviado" class="card success-card">
      <div class="icon">✅</div>
      <h2>¡Cotización Enviada!</h2>
      <p>Gracias. Hemos registrado tu respuesta.</p>
    </div>

    <div v-else class="card form-card">
      <div class="header">
        <h1>HairSoft <span class="badge">Solicitud de Presupuesto</span></h1>
        <p class="subtitle">Gestión de Stock</p>
      </div>

      <div class="info-producto-box">
        <div class="info-header">
          <span>Producto</span>
          <span>Solicitado</span>
        </div>
        <div class="info-body">
          <span class="product-name">{{ datos.producto_nombre }}</span>
          <span class="requested-qty">{{ datos.cantidad_requerida }} <small>u.</small></span>
        </div>
      </div>

      <form @submit.prevent="enviarCotizacion">
        
        <div class="form-group highlight-group">
          <label>Su Oferta (Cantidad disponible)</label>
          <div class="input-wrapper">
            <input 
              v-model.number="form.cantidad" 
              type="number" 
              min="1"
              :max="datos.cantidad_requerida"
              required 
              class="input-field input-destacado"
              :class="{ 'input-error': esCantidadInvalida }"
            >
          </div>
          
          <small v-if="form.cantidad < datos.cantidad_requerida && form.cantidad > 0" class="aviso-stock">
            ⚠️ Estás ofreciendo menos de lo solicitado (Lote: {{ datos.cantidad_requerida }}).
          </small>
          
          <small v-if="esCantidadInvalida" class="error-msg">
            ❌ No puedes ofrecer más de lo solicitado (Máx: {{ datos.cantidad_requerida }}).
          </small>
        </div>

        <div class="form-row">
          <div class="form-group half">
            <label>Precio Unitario ($)</label>
            <input 
              v-model="precioUnitario" 
              type="number" step="0.01" min="0" required 
              placeholder="0.00"
              class="input-field"
            >
          </div>
          <div class="form-group half">
            <label>Total de la Oferta</label>
            <div class="total-preview">$ {{ (form.cantidad * precioUnitario).toFixed(2) }}</div>
          </div>
        </div>

        <div class="form-group">
          <label>Fecha Estimada de Entrega</label>
          <input 
            v-model="fechaSeleccionada" 
            type="date" 
            :min="fechaMinima"
            required 
            class="input-field"
          >
          <small class="info-calculo" v-if="form.dias_entrega > 0">
            Días hábiles para la entrega: <strong>{{ form.dias_entrega }}</strong>
          </small>
        </div>

        <div class="form-group">
          <label>Comentarios adicionales</label>
          <textarea 
            v-model="form.comentarios" 
            rows="2" 
            placeholder="Ej: Stock garantizado..."
            class="input-field"
          ></textarea>
        </div>

        <button type="submit" class="btn-enviar" :disabled="enviando || esCantidadInvalida">
          {{ enviando ? 'Procesando...' : 'Confirmar Presupuesto' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue' // Agregamos computed
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const token = route.params.token
// OJO: Asegúrate que esta URL sea accesible desde internet si el proveedor está fuera de tu red local
const API_URL = 'http://127.0.0.1:8000/api/cotizacion-externa' 
const cargando = ref(true)
const error = ref(false)
const mensajeError = ref('')
const enviado = ref(false)
const enviando = ref(false)

const datos = ref({}) 
const precioUnitario = ref(0)
const fechaSeleccionada = ref('')
const fechaMinima = new Date().toISOString().split('T')[0]

const form = ref({
  cantidad: 0,
  precio_ofrecido: 0,
  dias_entrega: 0,
  comentarios: ''
})

// CAMBIO 4: Propiedad computada para validar la cantidad fácilmente
const esCantidadInvalida = computed(() => {
  // Si no hay datos cargados, no es inválido todavía
  if (!datos.value.cantidad_requerida) return false;
  // Es inválido si lo que escribe el usuario es mayor a lo requerido
  return form.value.cantidad > datos.value.cantidad_requerida;
})

// Cálculo de total dinámico
watch([precioUnitario, () => form.value.cantidad], () => {
  const q = Number(form.value.cantidad) || 0
  const p = Number(precioUnitario.value) || 0
  form.value.precio_ofrecido = (q * p).toFixed(2)
})

// Cálculo de días desde calendario
watch(fechaSeleccionada, (val) => {
  if (val) {
    const hoy = new Date(); hoy.setHours(0,0,0,0)
    const entrega = new Date(val)
    const diff = Math.ceil((entrega - hoy) / (1000 * 60 * 60 * 24))
    form.value.dias_entrega = diff >= 0 ? diff : 0
  }
})

onMounted(async () => {
  try {
    const response = await axios.get(`${API_URL}/${token}/`)    
    console.log("📥 RESPUESTA DEL SERVER:", response.data)

    if (typeof response.data === 'string') {
        console.error("🚨 ERROR: Se recibió HTML en lugar de JSON. Revisar URLs de Django.")
        error.value = true
        return
    }

    if (response.data.ya_respondido) {
      enviado.value = true
    } else {
      datos.value = response.data
      // Precarga con lo requerido (luego ellos pueden bajarlo si quieren)
      form.value.cantidad = Number(response.data.cantidad_requerida) || 0
    }
  } catch (e) {
    console.error("❌ ERROR AXIOS:", e)
    error.value = true
    mensajeError.value = 'No se pudo cargar la información.'
  } finally {
    cargando.value = false
  }
})

const enviarCotizacion = async () => {
  // Doble chequeo antes de enviar por si hackearon el HTML
  if (esCantidadInvalida.value) {
    alert("La cantidad no puede superar lo solicitado.");
    return;
  }

  enviando.value = true
  try {
    await axios.post(`${API_URL}/${token}/`, form.value)
    enviado.value = true
  } catch (e) {
    alert('Error al enviar presupuesto.')
  } finally {
    enviando.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800&display=swap');

/* ─── LAYOUT ────────────────────────────────────────── */
.cotizacion-container {
  background-color: #f3f4f6;
  min-height: 100vh;
  padding: 48px 20px;
  font-family: 'Inter', sans-serif;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  color: #1f2937;
}

/* ─── CARD ──────────────────────────────────────────── */
.card {
  background: #ffffff;
  width: 100%;
  max-width: 520px;
  border-radius: 20px;
  box-shadow:
    0 0 0 1px rgba(0,0,0,0.06),
    0 4px 6px -2px rgba(0,0,0,0.05),
    0 24px 48px -12px rgba(0,0,0,0.14);
  overflow: hidden;
}

/* ─── HEADER ────────────────────────────────────────── */
.header {
  background: #111827;
  padding: 24px 30px;
  border-bottom: 3px solid #10b981;
}

.header h1 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 800;
  color: #f9fafb;
  letter-spacing: -0.4px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
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

.subtitle {
  color: #6b7280;
  font-size: 0.82rem;
  font-weight: 500;
  margin: 0;
  display: block;
}

/* ─── ESTADOS ───────────────────────────────────────── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 0.97rem;
}

.error-card,
.success-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 50px 30px;
  gap: 10px;
}

.error-card h2,
.success-card h2 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 800;
  color: #111827;
}

.error-card p,
.success-card p {
  color: #6b7280;
  margin: 0;
  font-size: 0.95rem;
}

.icon { font-size: 2.5rem; }

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e5e7eb;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ─── FORM CARD ─────────────────────────────────────── */
.form-card form {
  padding: 0 28px 28px;
}

/* ─── INFO PRODUCTO ─────────────────────────────────── */
.info-producto-box {
  margin: 24px 28px 0;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.info-header {
  background: #374151;
  color: #e5e7eb;
  padding: 9px 16px;
  display: flex;
  justify-content: space-between;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.info-body {
  background: #f9fafb;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-name {
  font-weight: 600;
  color: #111827;
  font-size: 0.97rem;
}

.requested-qty {
  background: #ecfdf5;
  color: #059669;
  padding: 5px 13px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 1rem;
  border: 1px solid #6ee7b7;
}

/* ─── FORM GROUPS ───────────────────────────────────── */
.form-group {
  margin-top: 20px;
}

.form-group label {
  display: block;
  font-size: 0.78rem;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 7px;
}

.form-row {
  display: flex;
  gap: 14px;
  margin-top: 20px;
}

.half { flex: 1; }

/* ─── HIGHLIGHT GROUP ───────────────────────────────── */
.highlight-group {
  background: #eff6ff;
  border: 1.5px solid #bfdbfe;
  border-radius: 12px;
  padding: 18px;
  text-align: center;
  margin-top: 20px;
}

.highlight-group label {
  color: #1d4ed8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ─── INPUTS ────────────────────────────────────────── */
.input-field {
  width: 100%;
  padding: 10px 12px;
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

.input-field::-webkit-outer-spin-button,
.input-field::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }

.input-field:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.input-field.input-error {
  border-color: #ef4444 !important;
  background: #fef2f2;
  box-shadow: 0 0 0 3px rgba(239,68,68,0.1);
}

.input-destacado {
  font-size: 1.8rem !important;
  font-weight: 800 !important;
  color: #1d4ed8 !important;
  text-align: center;
  border-color: #93c5fd !important;
  background: #fff !important;
}

.input-destacado:focus {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

.input-field[type="date"] {
  color: #1e40af;
  border-color: #93c5fd;
  background: #fff;
}

textarea.input-field {
  resize: vertical;
  font-weight: 400;
  line-height: 1.6;
}

textarea.input-field::placeholder { color: #9ca3af; }

/* ─── TOTAL PREVIEW ─────────────────────────────────── */
.total-preview {
  padding: 10px 12px;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-weight: 800;
  color: #059669;
  font-size: 1.1rem;
  text-align: center;
  margin-top: 0;
}

/* ─── AVISOS ────────────────────────────────────────── */
.aviso-stock {
  display: block;
  margin-top: 8px;
  color: #92400e;
  font-weight: 600;
  font-size: 0.78rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 6px;
  padding: 6px 10px;
}

.error-msg {
  display: block;
  margin-top: 8px;
  color: #991b1b;
  font-weight: 600;
  font-size: 0.78rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 6px 10px;
}

.info-calculo {
  display: block;
  margin-top: 6px;
  color: #3b82f6;
  font-size: 0.8rem;
  font-weight: 500;
}

/* ─── BOTÓN ─────────────────────────────────────────── */
.btn-enviar {
  width: 100%;
  background: #059669;
  color: #fff;
  padding: 15px;
  border: none;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 24px;
  letter-spacing: -0.1px;
  box-shadow: 0 4px 0 #047857, 0 8px 24px rgba(5,150,105,0.28);
  transition: background 0.15s, transform 0.12s, box-shadow 0.12s, opacity 0.15s;
}

.btn-enviar:hover:not(:disabled) {
  background: #047857;
  transform: translateY(-2px);
  box-shadow: 0 6px 0 #065f46, 0 14px 32px rgba(5,150,105,0.32);
}

.btn-enviar:active:not(:disabled) {
  transform: translateY(2px);
  box-shadow: 0 1px 0 #047857;
}

.btn-enviar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* ─── RESPONSIVE ────────────────────────────────────── */
@media (max-width: 540px) {
  .cotizacion-container { padding: 0; background: #fff; }
  .card { border-radius: 0; box-shadow: none; max-width: 100%; }
  .form-row { flex-direction: column; gap: 0; }
  .info-producto-box { margin: 20px 20px 0; }
  .form-card form { padding: 0 20px 24px; }
  .header { padding: 20px; }
}
</style>