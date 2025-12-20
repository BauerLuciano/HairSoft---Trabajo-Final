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

      <div class="info-producto">
        <div class="info-item">
          <span class="label">Producto:</span>
          <span class="value">{{ datos.producto_nombre }}</span>
        </div>
        <div class="info-item">
          <span class="label">Solicitante:</span>
          <span class="value">HairSoft ({{ datos.proveedor_nombre }})</span>
        </div>
      </div>

      <form @submit.prevent="enviarCotizacion">
        
        <div class="form-group highlight-group">
          <label>Cantidad Disponible (u.)</label>
          <div class="input-wrapper">
            <input 
              v-model.number="form.cantidad" 
              type="number" 
              min="0"
              required 
              class="input-field input-destacado"
            >
            <span class="badge-solicitado">Solicitado: {{ datos.cantidad_requerida }}</span>
          </div>
          <small v-if="form.cantidad < datos.cantidad_requerida" class="aviso-stock">
            ⚠️ Estás ofertando menos de lo solicitado.
          </small>
        </div>

        <div class="form-group">
          <label>Precio Total Ofertado ($)</label>
          <input 
            v-model="form.precio_ofrecido" 
            type="number" step="0.01" min="0" required 
            placeholder="Ej: 15000.00"
            class="input-field"
          >
        </div>

        <div class="form-group">
          <label>Días hábiles entrega</label>
          <input 
            v-model="form.dias_entrega" 
            type="number" min="0" required 
            class="input-field"
          >
        </div>

        <div class="form-group">
          <label>Comentarios</label>
          <textarea 
            v-model="form.comentarios" 
            rows="2" 
            class="input-field"
          ></textarea>
        </div>

        <button type="submit" class="btn-enviar" :disabled="enviando">
          {{ enviando ? 'Enviando...' : 'Confirmar Presupuesto' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const token = route.params.token
// Ajustá si tu puerto es distinto
const API_URL = 'http://127.0.0.1:8000/usuarios/api/cotizacion-externa' 

const cargando = ref(true)
const error = ref(false)
const mensajeError = ref('')
const enviado = ref(false)
const enviando = ref(false)

const datos = ref({})
const form = ref({
  cantidad: '', // Ahora enviamos la cantidad real
  precio_ofrecido: '',
  dias_entrega: '',
  comentarios: ''
})

onMounted(async () => {
  try {
    const response = await axios.get(`${API_URL}/${token}/`)
    if (response.data.ya_respondido) {
      enviado.value = true
    } else {
      datos.value = response.data
      // Pre-cargamos el input con lo que pide el sistema
      form.value.cantidad = response.data.cantidad_requerida
    }
  } catch (e) {
    error.value = true
    mensajeError.value = 'Enlace inválido.'
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
    alert('Error al enviar.')
  } finally {
    enviando.value = false
  }
}
</script>

<style scoped>
/* Estilos Limpios */
.cotizacion-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: #f3f4f6; padding: 20px; font-family: sans-serif;
}
.card {
  background: white; padding: 30px; border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05); width: 100%; max-width: 480px;
}
.header { text-align: center; margin-bottom: 20px; }
.header h1 { font-size: 1.5rem; color: #111827; margin: 0; }
.subtitle { color: #6b7280; font-size: 0.9rem; }

.info-producto {
  background: #f9fafb; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #e5e7eb;
}
.info-item { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.95rem; }
.label { color: #6b7280; } .value { font-weight: 600; color: #374151; }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 5px; color: #374151; font-size: 0.9rem; }
.input-field {
  width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 1rem;
}
.highlight-group { background: #eff6ff; padding: 15px; border-radius: 8px; border: 1px dashed #3b82f6; }
.input-destacado { border-color: #3b82f6; font-weight: bold; text-align: center; font-size: 1.2rem; color: #2563eb; }
.badge-solicitado { display: block; text-align: center; font-size: 0.8rem; color: #6b7280; margin-top: 5px; }
.aviso-stock { color: #d97706; font-weight: 600; display: block; margin-top: 5px; font-size: 0.85rem; text-align: center;}

.btn-enviar {
  width: 100%; background: #2563eb; color: white; padding: 12px; border: none;
  border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 1rem;
}
.btn-enviar:hover { background: #1d4ed8; }
.btn-enviar:disabled { background: #9ca3af; }
</style>