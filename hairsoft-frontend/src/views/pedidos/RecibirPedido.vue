<template>
  <div class="container">
    <div class="header">
      <h2>Registrar Recepción de Pedido #{{ pedidoId }}</h2>
      <button @click="volverAlListado" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i> Volver al Listado
      </button>
    </div>

    <div v-if="cargandoDatos" class="loading-full">
      <div class="spinner"></div>
      <span>Cargando datos del pedido...</span>
    </div>

    <div v-else-if="!puedeRecibir" class="error-card">
      <i class="fas fa-exclamation-triangle"></i>
      <h3>No se puede recibir el pedido</h3>
      <p>El pedido #{{ pedidoId }} no está en estado PENDIENTE o PARCIAL, o no existe.</p>
      <button @click="volverAlListado" class="btn btn-primary">
        Volver al Listado
      </button>
    </div>

    <div v-else class="form-container">
      <!-- Información del Pedido -->
      <div class="info-card">
        <h3>Información del Pedido</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>Proveedor:</label>
            <span>{{ pedido.proveedor_nombre }}</span>
          </div>
          <div class="info-item">
            <label>Fecha del Pedido:</label>
            <span>{{ formatFecha(pedido.fecha_pedido) }}</span>
          </div>
          <div class="info-item">
            <label>Estado Actual:</label>
            <span :class="`badge badge-${getEstadoClass(pedido.estado)}`">
              {{ getEstadoTexto(pedido.estado) }}
            </span>
          </div>
          <div class="info-item">
            <label>Total del Pedido:</label>
            <span class="price">${{ pedido.total_calculado }}</span>
          </div>
        </div>
      </div>

      <!-- Formulario de Recepción -->
      <form @submit.prevent="registrarRecepcion" class="recepcion-form">
        <div class="form-section">
          <h3>Registrar Cantidades Recibidas</h3>
          <p class="form-help">
            Ingrese las cantidades efectivamente recibidas de cada producto. 
            El stock se actualizará automáticamente.
          </p>

          <div class="productos-recepcion">
            <div 
              v-for="(detalle, index) in pedido.detalles" 
              :key="detalle.id"
              class="producto-recepcion-item"
              :class="{'completo': detalle.cantidad_recibida === detalle.cantidad, 'parcial': detalle.cantidad_recibida > 0 && detalle.cantidad_recibida < detalle.cantidad}"
            >
              <div class="producto-info">
                <div class="producto-header">
                  <strong>{{ detalle.producto_nombre }}</strong>
                  <span class="producto-codigo">Código: {{ detalle.producto_codigo || 'N/A' }}</span>
                </div>
                <div class="producto-stock">
                  Stock actual: <strong>{{ detalle.producto_stock_actual }}</strong>
                </div>
              </div>

              <div class="recepcion-controls">
                <div class="cantidad-info">
                  <div class="cantidad-item">
                    <label>Solicitado:</label>
                    <span class="cantidad-solicitada">{{ detalle.cantidad }}</span>
                  </div>
                  <div class="cantidad-item">
                    <label>Ya Recibido:</label>
                    <span class="cantidad-recibida">{{ detalle.cantidad_recibida }}</span>
                  </div>
                  <div class="cantidad-item">
                    <label>Pendiente:</label>
                    <span class="cantidad-pendiente">{{ detalle.cantidad - detalle.cantidad_recibida }}</span>
                  </div>
                </div>

                <div class="recepcion-input">
                  <label for="`cantidad-${index}`">Cantidad Recibida *</label>
                  <input
                    :id="`cantidad-${index}`"
                    v-model.number="detalle.cantidad_recibida_nueva"
                    type="number"
                    :min="0"
                    :max="detalle.cantidad - detalle.cantidad_recibida"
                    class="form-input"
                    required
                    @change="validarCantidad(detalle)"
                  />
                  <small class="form-help">
                    Máximo: {{ detalle.cantidad - detalle.cantidad_recibida }} unidades
                  </small>
                </div>

                <div class="recepcion-resultado">
                  <div class="resultado-item">
                    <span>Nuevo stock:</span>
                    <strong :class="{'stock-aumento': detalle.cantidad_recibida_nueva > 0}">
                      {{ detalle.producto_stock_actual + detalle.cantidad_recibida_nueva }}
                    </strong>
                  </div>
                  <div class="resultado-item" v-if="detalle.cantidad_recibida_nueva > 0">
                    <span>Incremento:</span>
                    <span class="incremento">+{{ detalle.cantidad_recibida_nueva }}</span>
                  </div>
                </div>
              </div>

              <!-- Barra de progreso -->
              <div class="progreso-recepcion">
                <div class="progreso-labels">
                  <span>Progreso de recepción:</span>
                  <span>{{ calcularPorcentaje(detalle) }}%</span>
                </div>
                <div class="progreso-bar">
                  <div 
                    class="progreso-fill"
                    :style="{ width: `${calcularPorcentaje(detalle)}%` }"
                    :class="{'completo': calcularPorcentaje(detalle) === 100}"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Resumen de la recepción -->
          <div class="resumen-recepcion">
            <h4>Resumen de la Recepción</h4>
            <div class="resumen-grid">
              <div class="resumen-item">
                <span>Productos en el pedido:</span>
                <strong>{{ pedido.detalles.length }}</strong>
              </div>
              <div class="resumen-item">
                <span>Productos completos:</span>
                <strong class="text-success">{{ productosCompletos }}</strong>
              </div>
              <div class="resumen-item">
                <span>Productos parciales:</span>
                <strong class="text-warning">{{ productosParciales }}</strong>
              </div>
              <div class="resumen-item">
                <span>Productos pendientes:</span>
                <strong class="text-danger">{{ productosPendientes }}</strong>
              </div>
              <div class="resumen-item total">
                <span>Total recibido en esta entrega:</span>
                <strong class="total-recibido">{{ totalUnidadesRecibidas }} unidades</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Observaciones -->
        <div class="form-section">
          <h3>Observaciones de la Recepción</h3>
          <div class="form-group">
            <label for="observaciones">Observaciones (Opcional)</label>
            <textarea
              id="observaciones"
              v-model="observaciones"
              rows="3"
              placeholder="Observaciones sobre la recepción, estado de los productos, etc."
              class="form-textarea"
            ></textarea>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="form-actions">
          <button type="button" @click="volverAlListado" class="btn btn-secondary">
            Cancelar
          </button>
          <div class="action-buttons">
            <button 
              type="button" 
              @click="marcarTodoComoRecibido" 
              class="btn btn-outline"
              :disabled="todoRecibido"
            >
              <i class="fas fa-check-double"></i> Marcar Todo como Recibido
            </button>
            <button 
              type="submit" 
              :disabled="!puedeRegistrarRecepcion || cargando" 
              class="btn btn-success"
            >
              <span v-if="cargando">
                <i class="fas fa-spinner fa-spin"></i> Procesando...
              </span>
              <span v-else>
                <i class="fas fa-check-circle"></i> Registrar Recepción
              </span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const API_BASE = 'http://127.0.0.1:8000'

const pedidoId = route.params.id

// Estados
const pedido = ref({
  proveedor_nombre: '',
  fecha_pedido: '',
  estado: '',
  total_calculado: 0,
  detalles: []
})

const observaciones = ref('')
const cargando = ref(false)
const cargandoDatos = ref(true)

// Computed
const puedeRecibir = computed(() => {
  return pedido.value.estado && ['PENDIENTE', 'PARCIAL'].includes(pedido.value.estado)
})

const productosCompletos = computed(() => {
  return pedido.value.detalles.filter(d => 
    d.cantidad_recibida_nueva === (d.cantidad - d.cantidad_recibida)
  ).length
})

const productosParciales = computed(() => {
  return pedido.value.detalles.filter(d => 
    d.cantidad_recibida_nueva > 0 && 
    d.cantidad_recibida_nueva < (d.cantidad - d.cantidad_recibida)
  ).length
})

const productosPendientes = computed(() => {
  return pedido.value.detalles.filter(d => d.cantidad_recibida_nueva === 0).length
})

const totalUnidadesRecibidas = computed(() => {
  return pedido.value.detalles.reduce((total, detalle) => total + detalle.cantidad_recibida_nueva, 0)
})

const todoRecibido = computed(() => {
  return pedido.value.detalles.every(d => 
    d.cantidad_recibida_nueva === (d.cantidad - d.cantidad_recibida)
  )
})

const puedeRegistrarRecepcion = computed(() => {
  return totalUnidadesRecibidas.value > 0 && 
         pedido.value.detalles.every(d => 
           d.cantidad_recibida_nueva >= 0 && 
           d.cantidad_recibida_nueva <= (d.cantidad - d.cantidad_recibida)
         )
})

// Métodos
const cargarDatos = async () => {
  try {
    cargandoDatos.value = true
    
    // Cargar pedido existente
    const response = await axios.get(`${API_BASE}/usuarios/api/pedidos/${pedidoId}/`)
    pedido.value = { ...response.data }
    
    // Preparar datos para recepción
    pedido.value.detalles = pedido.value.detalles.map(detalle => ({
      ...detalle,
      cantidad_recibida_nueva: 0 // Inicializar en 0 para la nueva recepción
    }))
    
  } catch (error) {
    console.error('Error cargando datos:', error)
    if (error.response?.status === 404) {
      alert('Pedido no encontrado')
    } else {
      alert('Error al cargar los datos del pedido')
    }
    volverAlListado()
  } finally {
    cargandoDatos.value = false
  }
}

const validarCantidad = (detalle) => {
  const maximo = detalle.cantidad - detalle.cantidad_recibida
  if (detalle.cantidad_recibida_nueva > maximo) {
    detalle.cantidad_recibida_nueva = maximo
    alert(`La cantidad no puede superar las ${maximo} unidades pendientes`)
  }
  
  if (detalle.cantidad_recibida_nueva < 0) {
    detalle.cantidad_recibida_nueva = 0
  }
}

const marcarTodoComoRecibido = () => {
  if (confirm('¿Marcar todas las cantidades pendientes como recibidas?')) {
    pedido.value.detalles.forEach(detalle => {
      detalle.cantidad_recibida_nueva = detalle.cantidad - detalle.cantidad_recibida
    })
  }
}

const calcularPorcentaje = (detalle) => {
  const totalRecibido = detalle.cantidad_recibida + detalle.cantidad_recibida_nueva
  return Math.round((totalRecibido / detalle.cantidad) * 100)
}

const registrarRecepcion = async () => {
  if (!puedeRegistrarRecepcion.value) {
    alert('Ingrese al menos una cantidad recibida válida')
    return
  }

  if (!confirm('¿Confirmar la recepción de los productos? El stock se actualizará automáticamente.')) {
    return
  }

  try {
    cargando.value = true
    
    const payload = {
      detalles_recepcion: pedido.value.detalles.map(detalle => ({
        id: detalle.id,
        cantidad_recibida: detalle.cantidad_recibida_nueva
      }))
    }

    const response = await axios.post(
      `${API_BASE}/usuarios/api/pedidos/${pedidoId}/recibir/`, 
      payload
    )
    
    const nuevoEstado = response.data.estado
    let mensaje = `✅ Recepción registrada exitosamente. `
    
    if (nuevoEstado === 'RECIBIDO') {
      mensaje += 'El pedido ha sido COMPLETADO.'
    } else if (nuevoEstado === 'PARCIAL') {
      mensaje += 'El pedido queda como RECEPCIÓN PARCIAL.'
    }
    
    alert(mensaje)
    router.push('/pedidos')
    
  } catch (error) {
    console.error('Error registrando recepción:', error)
    
    if (error.response?.status === 400) {
      const errors = error.response.data
      let errorMessage = 'Errores en la recepción:\n'
      
      Object.entries(errors).forEach(([field, messages]) => {
        errorMessage += `• ${field}: ${messages.join(', ')}\n`
      })
      
      alert(errorMessage)
    } else {
      alert('Error al registrar la recepción: ' + (error.response?.data?.error || error.message))
    }
  } finally {
    cargando.value = false
  }
}

const volverAlListado = () => {
  router.push('/pedidos')
}

const formatFecha = (fechaString) => {
  if (!fechaString) return '-'
  const fecha = new Date(fechaString)
  return fecha.toLocaleDateString('es-AR')
}

const getEstadoClass = (estado) => {
  const clases = {
    'PENDIENTE': 'warning',
    'RECIBIDO': 'success',
    'CANCELADO': 'danger',
    'PARCIAL': 'info'
  }
  return clases[estado] || 'secondary'
}

const getEstadoTexto = (estado) => {
  const textos = {
    'PENDIENTE': 'Pendiente',
    'RECIBIDO': 'Recibido',
    'CANCELADO': 'Cancelado',
    'PARCIAL': 'Parcial'
  }
  return textos[estado] || estado
}
</script>

<style scoped>
.info-card {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
}

.info-card h3 {
  color: #0369a1;
  margin-bottom: 15px;
}

.producto-recepcion-item {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.producto-recepcion-item.completo {
  border-color: #10b981;
  background: #f0fdf4;
}

.producto-recepcion-item.parcial {
  border-color: #f59e0b;
  background: #fffbeb;
}

.producto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.producto-codigo {
  color: #6b7280;
  font-size: 0.875rem;
}

.producto-stock {
  color: #374151;
  font-size: 0.875rem;
}

.recepcion-controls {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 30px;
  align-items: start;
  margin: 15px 0;
}

.cantidad-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cantidad-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f3f4f6;
}

.cantidad-item:last-child {
  border-bottom: none;
}

.cantidad-solicitada {
  font-weight: 600;
  color: #374151;
}

.cantidad-recibida {
  font-weight: 600;
  color: #10b981;
}

.cantidad-pendiente {
  font-weight: 600;
  color: #f59e0b;
}

.recepcion-input {
  min-width: 150px;
}

.recepcion-resultado {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 140px;
}

.resultado-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.stock-aumento {
  color: #10b981;
  font-weight: 600;
}

.incremento {
  color: #10b981;
  font-weight: 600;
}

.progreso-recepcion {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.progreso-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.875rem;
  color: #6b7280;
}

.progreso-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progreso-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progreso-fill.completo {
  background: #10b981;
}

.resumen-recepcion {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.resumen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.resumen-item.total {
  border-top: 2px solid #e5e7eb;
  border-bottom: none;
  font-size: 1.1rem;
  margin-top: 10px;
  padding-top: 15px;
}

.total-recibido {
  color: #10b981;
  font-weight: 600;
}

.text-success { color: #10b981; }
.text-warning { color: #f59e0b; }
.text-danger { color: #ef4444; }

.btn-success {
  background: #10b981;
  border-color: #10b981;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
  border-color: #059669;
}

/* Responsive */
@media (max-width: 768px) {
  .recepcion-controls {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .resumen-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 10px;
  }
}
</style>