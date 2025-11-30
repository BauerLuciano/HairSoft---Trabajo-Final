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
      <p>Gracias por responder. Su propuesta ha sido registrada en nuestro sistema.</p>
      <button @click="cerrarPestana" class="btn-secondary">Cerrar pestaña</button>
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
          <span class="label">Cantidad Requerida:</span>
          <span class="value highlight">{{ datos.cantidad_requerida }} u.</span>
        </div>
        <div class="info-item">
          <span class="label">Proveedor:</span>
          <span class="value">{{ datos.proveedor_nombre }}</span>
        </div>
      </div>

      <form @submit.prevent="enviarCotizacion">
        <div class="form-group">
          <label>Precio Total Ofertado ($)</label>
          <input 
            v-model="form.precio_ofrecido" 
            type="number" 
            step="0.01" 
            min="0"
            required 
            placeholder="Ej: 15000.00"
            class="input-field"
          >
          <small>Incluir impuestos si corresponde.</small>
        </div>

        <div class="form-group">
          <label>Días hábiles para entrega</label>
          <input 
            v-model="form.dias_entrega" 
            type="number" 
            min="0"
            required 
            placeholder="Ej: 3"
            class="input-field"
          >
        </div>

        <div class="form-group">
          <label>Comentarios / Observaciones</label>
          <textarea 
            v-model="form.comentarios" 
            placeholder="Ej: Incluye envío gratis..."
            rows="3"
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
const API_URL = 'http://127.0.0.1:8000/usuarios/api/cotizacion-externa' 

// Estados
const cargando = ref(true)
const error = ref(false)
const mensajeError = ref('')
const enviado = ref(false)
const enviando = ref(false)

// Datos
const datos = ref({})
const form = ref({
  precio_ofrecido: '',
  dias_entrega: '',
  comentarios: ''
})

// Cargar datos al entrar
onMounted(async () => {
  try {
    const response = await axios.get(`${API_URL}/${token}/`)
    
    // Si ya respondió, la API nos avisa
    if (response.data.ya_respondido) {
      enviado.value = true
    } else {
      datos.value = response.data
    }
  } catch (e) {
    error.value = true
    mensajeError.value = e.response?.data?.error || 'No pudimos cargar la solicitud.'
  } finally {
    cargando.value = false
  }
})

// Enviar formulario
const enviarCotizacion = async () => {
  enviando.value = true
  try {
    await axios.post(`${API_URL}/${token}/`, form.value)
    enviado.value = true
  } catch (e) {
    alert('Error al enviar: ' + (e.response?.data?.error || 'Intente nuevamente'))
  } finally {
    enviando.value = false
  }
}

const cerrarPestana = () => {
  window.close()
}
</script>

<style scoped>
/* Diseño limpio y profesional centrado */
.cotizacion-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f3f4f6; /* Gris muy suave */
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 480px;
  text-align: center;
}

.header h1 {
  color: #111827;
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 25px;
}

.info-producto {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  text-align: left;
  border: 1px solid #e5e7eb;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.info-item:last-child { margin-bottom: 0; }

.label { color: #6b7280; }
.value { font-weight: 600; color: #111827; }
.highlight { color: #10b981; }

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: #374151;
}

.input-field {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input-field:focus {
  border-color: #10b981;
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.btn-enviar {
  width: 100%;
  background: #10b981;
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-enviar:hover { background: #059669; }
.btn-enviar:disabled { background: #9ca3af; cursor: not-allowed; }

/* Estados de Error y Éxito */
.icon { font-size: 3rem; margin-bottom: 15px; }
.success-card h2 { color: #10b981; margin-bottom: 10px; }
.error-card h2 { color: #ef4444; margin-bottom: 10px; }
.btn-secondary {
  margin-top: 20px;
  padding: 10px 20px;
  background: #e5e7eb;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* Spinner de carga */
.loading-state {
  text-align: center;
  color: #6b7280;
}
.spinner {
  border: 4px solid #e5e7eb;
  border-top: 4px solid #10b981;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>