<template>
  <div class="recepcion-container">
    <div class="recepcion-card">
      <div class="recepcion-header">
        <h1>📦 Recepción de Pedido #{{ pedidoId }}</h1>
        <p>Confirmar recepción completa de productos y actualizar stock</p>
      </div>

      <!-- Estado de carga -->
      <div v-if="cargando" class="loading-state">
        <p>🔄 Cargando detalles del pedido...</p>
      </div>

      <!-- Error al cargar -->
      <div v-else-if="error" class="error-state">
        <p>❌ {{ error }}</p>
        <button @click="volverAlListado" class="btn-volver">← Volver al listado</button>
      </div>

      <!-- Formulario de recepción -->
      <div v-else-if="pedido" class="recepcion-form">
        <!-- Información del pedido -->
        <div class="pedido-info">
          <div class="info-grid">
            <div class="info-item">
              <label>Proveedor:</label>
              <strong>{{ pedido.proveedor_nombre }}</strong>
            </div>
            <div class="info-item">
              <label>Estado:</label>
              <span :class="`badge-estado estado-${getEstadoClass(pedido.estado)}`">
                {{ getEstadoTexto(pedido.estado) }}
              </span>
            </div>
            <div class="info-item">
              <label>Fecha Pedido:</label>
              <span>{{ formatFecha(pedido.fecha_pedido) }}</span>
            </div>
            <div class="info-item">
              <label>Total:</label>
              <strong>${{ formatPrecio(pedido.total || pedido.total_calculado || 0) }}</strong>
            </div>
          </div>
        </div>

        <!-- Productos a recibir - SOLO LECTURA -->
        <div class="productos-section">
          <h3>Productos a Recibir</h3>
          <div class="productos-list">
            <div v-for="detalle in pedido.detalles" :key="detalle.id" class="producto-item">
              <div class="producto-info">
                <h4>{{ detalle.producto_nombre }}</h4>
                <div class="producto-details">
                  <span>Código: {{ detalle.producto_codigo || 'N/A' }}</span>
                  <span>Stock actual: {{ detalle.producto_stock_actual || 0 }}</span>
                </div>
              </div>
              
              <div class="cantidades-container">
                <div class="cantidad-info">
                  <label>Cantidad Solicitada:</label>
                  <span class="cantidad-solicitada">{{ detalle.cantidad }}</span>
                </div>
                
                <div class="cantidad-info">
                  <label>Será recibido:</label>
                  <span class="cantidad-recibida">{{ detalle.cantidad }}</span>
                  <small style="color: #059669; font-weight: 600;">✓ Cantidad confirmada</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="action-buttons">
          <button @click="volverAlListado" class="btn-cancelar">
            ← Cancelar
          </button>
          <button 
            @click="confirmarRecepcion" 
            :disabled="procesando"
            class="btn-confirmar"
          >
            {{ procesando ? '🔄 Procesando...' : '✅ Confirmar Recepción Completa' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

// Estados
const pedidoId = ref(null)
const pedido = ref(null)
const cargando = ref(false)
const error = ref(null)
const procesando = ref(false)

// Computed - SIEMPRE puede confirmar (no hay validación de cantidades)
const puedeConfirmar = computed(() => {
  return pedido.value && pedido.value.detalles && pedido.value.detalles.length > 0
})

// Ciclo de vida
onMounted(() => {
  pedidoId.value = route.params.id
  cargarPedido()
})

// Métodos
const cargarPedido = async () => {
  try {
    cargando.value = true
    error.value = null
    
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('No hay token de autenticación')
    }

    console.log('🔍 Cargando pedido:', pedidoId.value)

    const response = await axios.get(`${API_BASE}/usuarios/api/pedidos/${pedidoId.value}/`, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    })

    console.log('✅ Pedido cargado:', response.data)
    pedido.value = response.data

  } catch (err) {
    console.error('❌ Error cargando pedido:', err)
    
    if (err.response?.status === 401) {
      error.value = 'No autorizado. Su sesión ha expirado.'
      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else if (err.response?.status === 404) {
      error.value = 'Pedido no encontrado'
    } else {
      error.value = 'Error al cargar el pedido: ' + (err.response?.data?.detail || err.message)
    }
  } finally {
    cargando.value = false
  }
}

const confirmarRecepcion = async () => {
  const result = await Swal.fire({
    title: '¿Confirmar Recepción Completa?',
    html: `
      <div style="text-align: left;">
        <p>Se recibirán <strong>TODAS</strong> las cantidades solicitadas:</p>
        <ul style="margin: 10px 0; padding-left: 20px;">
          ${pedido.value.detalles.map(d => 
            `<li><strong>${d.cantidad} x</strong> ${d.producto_nombre}</li>`
          ).join('')}
        </ul>
        <p>El stock se actualizará y el pedido se marcará como <strong>ENTREGADO</strong></p>
      </div>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#059669',
    cancelButtonColor: '#6b7280',
    confirmButtonText: 'Sí, confirmar recepción completa',
    cancelButtonText: 'Cancelar',
    reverseButtons: true
  })

  if (!result.isConfirmed) return

  try {
    procesando.value = true

    const token = localStorage.getItem('token')
    
    // ✅ ESTO ES LO QUE TENÉS QUE MANDAR:
    const datosRecepcion = {
      detalles_recepcion: pedido.value.detalles.map(detalle => ({
        id: detalle.id,
        cantidad_recibida: detalle.cantidad  // Usar la cantidad ORIGINAL
      }))
    }

    console.log('📤 Enviando recepción:', datosRecepcion)

    const response = await axios.post(
      `${API_BASE}/usuarios/api/pedidos/${pedidoId.value}/recibir/`,
      datosRecepcion,
      {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    console.log('✅ Recepción confirmada:', response.data)

    Swal.fire({
      icon: 'success',
      title: '¡Recepción Exitosa!',
      html: `
        <div style="text-align: left;">
          <p>✅ Pedido marcado como <strong>ENTREGADO</strong></p>
          <p>✅ Stock actualizado correctamente</p>
          <p>Será redirigido al listado de pedidos...</p>
        </div>
      `,
      timer: 3000,
      showConfirmButton: false
    })

    setTimeout(() => router.push('/pedidos'), 3000)

  } catch (err) {
    console.error('❌ Error confirmando recepción:', err)
    
    let mensajeError = 'Error al confirmar la recepción'
    
    if (err.response?.status === 401) {
      mensajeError = 'No autorizado. Su sesión ha expirado.'
    } else if (err.response?.data) {
      mensajeError = JSON.stringify(err.response.data)
    }

    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: mensajeError,
      confirmButtonText: 'Entendido'
    })
  } finally {
    procesando.value = false
  }
}

const volverAlListado = () => {
  router.push('/pedidos')
}

// Utilidades
const formatFecha = (fechaString) => {
  if (!fechaString) return '-'
  try {
    const fecha = new Date(fechaString)
    return fecha.toLocaleDateString('es-AR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch (error) {
    return fechaString
  }
}

const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  return parseFloat(precio).toFixed(2)
}

const getEstadoClass = (estado) => {
  const clases = {
    'PENDIENTE': 'warning',
    'CONFIRMADO': 'info',
    'ENTREGADO': 'success',
    'CANCELADO': 'danger'
  }
  return clases[estado] || 'secondary'
}

const getEstadoTexto = (estado) => {
  const textos = {
    'PENDIENTE': 'Pendiente',
    'CONFIRMADO': 'Confirmado',
    'ENTREGADO': 'Entregado',
    'CANCELADO': 'Cancelado'
  }
  return textos[estado] || estado
}
</script>

<style scoped>
.recepcion-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.recepcion-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.recepcion-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #059669, #047857, #065f46, #047857, #059669);
  border-radius: 24px 24px 0 0;
}

.recepcion-header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 20px;
}

.recepcion-header h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #059669);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
}

.recepcion-header p {
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.5px;
}

/* Estados */
.loading-state, .error-state {
  text-align: center;
  padding: 60px;
  font-size: 1.2em;
}

.error-state {
  color: var(--error-color);
}

/* Información del pedido */
.pedido-info {
  background: var(--hover-bg);
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}

/* Productos */
.productos-section {
  margin-bottom: 30px;
}

.productos-section h3 {
  color: var(--text-primary);
  margin-bottom: 20px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.productos-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.producto-item {
  background: var(--bg-primary);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.producto-info {
  flex: 1;
}

.producto-info h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-weight: 700;
}

.producto-details {
  display: flex;
  gap: 15px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.cantidades-container {
  display: flex;
  gap: 30px;
  align-items: center;
}

.cantidad-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 120px;
}

.cantidad-info label {
  font-weight: 700;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
}

.cantidad-solicitada, .cantidad-recibida {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.cantidad-recibida {
  color: #059669;
}

/* Botones */
.action-buttons {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 30px;
}

.btn-cancelar, .btn-confirmar, .btn-volver {
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-cancelar {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-cancelar:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
}

.btn-confirmar {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.35);
}

.btn-confirmar:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(5, 150, 105, 0.5);
}

.btn-confirmar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.btn-volver {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  margin: 0 auto;
}

/* Badges */
.badge-estado {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
}

.estado-warning {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
}

.estado-info {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
}

.estado-success {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
}

.estado-danger {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
}

/* Responsive */
@media (max-width: 768px) {
  .recepcion-container {
    padding: 15px;
  }
  
  .recepcion-card {
    padding: 25px;
    border-radius: 20px;
  }
  
  .producto-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .cantidades-container {
    width: 100%;
    justify-content: space-between;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .recepcion-card {
    padding: 20px;
    border-radius: 16px;
  }
  
  .recepcion-header h1 {
    font-size: 1.6rem;
  }
  
  .cantidades-container {
    flex-direction: column;
    gap: 15px;
    width: 100%;
  }
  
  .cantidad-info {
    min-width: auto;
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
  }
}
</style>