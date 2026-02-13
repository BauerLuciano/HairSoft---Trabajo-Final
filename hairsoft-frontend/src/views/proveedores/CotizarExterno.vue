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
        <h1>Solicitud de Presupuesto</h1>
        <p class="subtitle">HairSoft - Gestión de Stock</p>
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
              required 
              class="input-field input-destacado"
            >
          </div>
          <small v-if="form.cantidad < datos.cantidad_requerida" class="aviso-stock">
            ⚠️ Estás ofreciendo menos de lo solicitado (Lote: {{ datos.cantidad_requerida }}).
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

        <button type="submit" class="btn-enviar" :disabled="enviando">
          {{ enviando ? 'Procesando...' : 'Confirmar Presupuesto' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const token = route.params.token
const API_URL = 'http://127.0.0.1:8000/api/cotizacion-externa'
const cargando = ref(true)
const error = ref(false)
const mensajeError = ref('')
const enviado = ref(false)
const enviando = ref(false)

const datos = ref({}) // Empezamos vacío
const precioUnitario = ref(0)
const fechaSeleccionada = ref('')
const fechaMinima = new Date().toISOString().split('T')[0]

const form = ref({
  cantidad: 0,
  precio_ofrecido: 0,
  dias_entrega: 0,
  comentarios: ''
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
    // Usamos el puerto 8000 directamente para asegurar que vaya al backend
    const response = await axios.get(`${API_URL}/${token}/`)    
    console.log("📥 RESPUESTA DEL SERVER:", response.data)

    // Si lo que llega es un string (HTML), algo sigue mal en las rutas
    if (typeof response.data === 'string') {
        console.error("🚨 ERROR: Se recibió HTML en lugar de JSON. Revisar URLs de Django.")
        error.value = true
        return
    }

    if (response.data.ya_respondido) {
      enviado.value = true
    } else {
      datos.value = response.data
      // Precarga con fallback a 0 para evitar NaN
      form.value.cantidad = Number(response.data.cantidad_requerida) || 0
    }
  } catch (e) {
    console.error("❌ ERROR AXIOS:", e)
    error.value = true
  } finally {
    cargando.value = false
  }
})

const enviarCotizacion = async () => {
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
.cotizacion-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: #111827; padding: 20px; font-family: 'Inter', sans-serif;
}
.card {
  background: #ffffff; padding: 30px; border-radius: 20px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 500px;
}
.header h1 { font-size: 1.5rem; color: #111827; font-weight: 800; margin-bottom: 5px; }
.subtitle { color: #6b7280; font-size: 0.9rem; margin-bottom: 25px; display: block; }

/* ESTILO TABLA PRODUCTO */
.info-producto-box {
  background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 25px; overflow: hidden;
}
.info-header {
  background: #374151; color: white; padding: 10px 15px; display: flex; justify-content: space-between; font-size: 0.75rem; text-transform: uppercase; font-weight: 700;
}
.info-body {
  padding: 15px; display: flex; justify-content: space-between; align-items: center;
}
.product-name { font-weight: 700; color: #111827; }
.requested-qty { 
  background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 1.1rem;
}

.highlight-group { background: #f0f9ff; border: 2px solid #bae6fd; border-radius: 15px; padding: 20px; text-align: center; }
.input-destacado { font-size: 1.8rem !important; color: #0284c7 !important; text-align: center; font-weight: 900 !important; border-color: #0284c7 !important; }

.form-row { display: flex; gap: 15px; }
.half { flex: 1; }
.total-preview { 
  padding: 12px; background: #f3f4f6; border-radius: 10px; font-weight: 800; color: #111827; text-align: center; font-size: 1.1rem; border: 2px solid #e5e7eb;
}

.input-field {
  width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 10px; margin-top: 5px; font-size: 1rem;
}
.input-field:focus { outline: none; border-color: #2563eb; }
.aviso-stock { color: #9a3412; font-weight: 700; font-size: 0.8rem; margin-top: 10px; display: block; }

.btn-enviar {
  width: 100%; background: #2563eb; color: white; padding: 16px; border: none;
  border-radius: 12px; font-weight: 700; cursor: pointer; font-size: 1.1rem; margin-top: 10px;
}
.btn-enviar:hover { background: #1d4ed8; }
</style>