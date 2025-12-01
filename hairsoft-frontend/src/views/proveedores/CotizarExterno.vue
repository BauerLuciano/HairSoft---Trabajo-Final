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
      <button @click="redirigirInicio" class="btn-secondary">
        Volver al inicio
      </button>
    </div>

    <div v-else-if="enviado" class="card success-card">
      <div class="icon">✅</div>
      <h2>¡Cotización Enviada!</h2>
      <p>Gracias por responder. Su propuesta ha sido registrada en nuestro sistema.</p>
      
      <div class="acciones-container">
        <button @click="intentarCerrar" class="btn-primary">
          Cerrar pestaña
        </button>
        <button @click="redirigirInicio" class="btn-secondary">
          Volver al inicio
        </button>
      </div>
      
      <div v-if="mostrarAdvertenciaCierre" class="advertencia">
        <p>⚠️ Si la pestaña no se cierra automáticamente, por favor ciérrela manualmente.</p>
      </div>
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
const mostrarAdvertenciaCierre = ref(false)

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

// Intentar cerrar la pestaña
const intentarCerrar = () => {
  // Intentamos cerrar la ventana
  if (window.opener || window.history.length <= 1) {
    window.close()
  } else {
    // Si no se puede cerrar, mostramos advertencia
    mostrarAdvertenciaCierre.value = true
    // También intentamos redirigir a una página en blanco y luego cerrar
    setTimeout(() => {
      window.location.href = 'about:blank'
      setTimeout(() => window.close(), 100)
    }, 2000)
  }
}

// Redirigir a página principal
const redirigirInicio = () => {
  window.location.href = 'https://www.google.com' // Cambia por tu URL
}
</script>

<style scoped>
.cotizacion-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header h1 {
  color: #111827;
  font-size: 1.8rem;
  margin-bottom: 5px;
  font-weight: 700;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 25px;
  font-size: 1rem;
}

.info-producto {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 30px;
  text-align: left;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 1rem;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-item:last-child { 
  margin-bottom: 0; 
  border-bottom: none;
}

.label { 
  color: #64748b; 
  font-weight: 500;
}
.value { 
  font-weight: 600; 
  color: #1e293b; 
}
.highlight { 
  color: #10b981; 
  font-size: 1.1rem;
}

.form-group {
  margin-bottom: 25px;
  text-align: left;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
  color: #374151;
  font-size: 0.95rem;
}

.input-field {
  width: 100%;
  padding: 14px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.input-field:focus {
  border-color: #10b981;
  background: white;
  outline: none;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
  transform: translateY(-2px);
}

.btn-enviar {
  width: 100%;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 16px;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-enviar:hover { 
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}
.btn-enviar:active { 
  transform: translateY(0);
}
.btn-enviar:disabled { 
  background: #9ca3af; 
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Estados de Error y Éxito */
.icon { 
  font-size: 4rem; 
  margin-bottom: 20px;
  animation: bounce 0.6s;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
  40% {transform: translateY(-10px);}
  60% {transform: translateY(-5px);}
}

.success-card h2 { 
  color: #10b981; 
  margin-bottom: 15px;
  font-size: 1.8rem;
}
.error-card h2 { 
  color: #ef4444; 
  margin-bottom: 15px;
  font-size: 1.8rem;
}

.acciones-container {
  display: flex;
  gap: 15px;
  margin-top: 25px;
  flex-direction: column;
}

.btn-primary {
  padding: 14px 20px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.btn-secondary {
  padding: 14px 20px;
  background: #f1f5f9;
  color: #475569;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e2e8f0;
  transform: translateY(-2px);
}

.advertencia {
  margin-top: 20px;
  padding: 15px;
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 12px;
  color: #92400e;
}

.advertencia p {
  margin: 0;
  font-size: 0.9rem;
}

/* Spinner de carga */
.loading-state {
  text-align: center;
  color: white;
  background: rgba(255,255,255,0.1);
  padding: 40px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.spinner {
  border: 4px solid rgba(255,255,255,0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin { 
  0% { transform: rotate(0deg); } 
  100% { transform: rotate(360deg); } 
}
</style>