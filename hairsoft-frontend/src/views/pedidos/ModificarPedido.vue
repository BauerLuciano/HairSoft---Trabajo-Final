<template>
  <div class="container">
    <div class="header">
      <h2>Modificar Pedido #{{ pedidoId }}</h2>
      <button @click="volverAlListado" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i> Volver al Listado
      </button>
    </div>

    <div v-if="cargandoDatos" class="loading-full">
      <div class="spinner"></div>
      <span>Cargando datos del pedido...</span>
    </div>

    <div v-else-if="!puedeModificar" class="error-card">
      <i class="fas fa-exclamation-triangle"></i>
      <h3>No se puede modificar el pedido</h3>
      <p>El pedido #{{ pedidoId }} no está en estado PENDIENTE o no existe.</p>
      <button @click="volverAlListado" class="btn btn-primary">
        Volver al Listado
      </button>
    </div>

    <div v-else class="form-container">
      <form @submit.prevent="actualizarPedido" class="pedido-form">
        <!-- Información del Proveedor -->
        <div class="form-section">
          <h3>Información del Proveedor</h3>
          
          <div class="form-group">
            <label for="proveedor">Proveedor *</label>
            <select
              id="proveedor"
              v-model="pedido.proveedor"
              required
              class="form-select"
              :disabled="cargandoProveedores"
            >
              <option value="">Seleccione un proveedor</option>
              <option 
                v-for="proveedor in proveedoresActivos" 
                :key="proveedor.id" 
                :value="proveedor.id"
              >
                {{ proveedor.nombre }} - {{ proveedor.contacto || 'Sin contacto' }}
              </option>
            </select>
          </div>

          <div v-if="proveedorSeleccionado" class="proveedor-info-card">
            <h4>Información del Proveedor</h4>
            <div class="info-grid">
              <div class="info-item">
                <label>Contacto:</label>
                <span>{{ proveedorSeleccionado.contacto || 'No especificado' }}</span>
              </div>
              <div class="info-item">
                <label>Teléfono:</label>
                <span>{{ proveedorSeleccionado.telefono || 'No especificado' }}</span>
              </div>
              <div class="info-item">
                <label>Email:</label>
                <span>{{ proveedorSeleccionado.email || 'No especificado' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Productos del Pedido -->
        <div class="form-section">
          <h3>Productos del Pedido</h3>
          
          <div class="productos-header">
            <div class="search-producto">
              <input
                v-model="busquedaProducto"
                type="text"
                placeholder="Buscar producto para agregar..."
                class="form-input"
                @input="filtrarProductos"
              />
            </div>
            <button type="button" @click="agregarProducto" class="btn btn-primary">
              <i class="fas fa-plus"></i> Agregar Producto
            </button>
          </div>

          <!-- Productos disponibles para agregar -->
          <div v-if="busquedaProducto && productosDisponibles.length > 0" class="productos-disponibles">
            <h5>Productos Disponibles</h5>
            <div class="productos-grid">
              <div 
                v-for="producto in productosDisponibles" 
                :key="producto.id"
                class="producto-card"
                @click="seleccionarProducto(producto)"
              >
                <div class="producto-info">
                  <strong>{{ producto.nombre }}</strong>
                  <small>Código: {{ producto.codigo || 'N/A' }}</small>
                  <span class="producto-stock">Stock: {{ producto.stock_actual }}</span>
                  <span class="producto-precio">${{ producto.precio }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Productos en el pedido -->
          <div v-if="pedido.detalles.length > 0" class="productos-agregados">
            <h5>Productos en el Pedido ({{ pedido.detalles.length }})</h5>
            <div class="detalles-list">
              <div 
                v-for="(detalle, index) in pedido.detalles" 
                :key="detalle.id || index"
                class="detalle-item"
              >
                <div class="detalle-info">
                  <strong>{{ detalle.producto_nombre }}</strong>
                  <small>Código: {{ detalle.producto_codigo || 'N/A' }}</small>
                  <span class="stock-info">Stock actual: {{ detalle.producto_stock_actual }}</span>
                  
                  <!-- Indicador si es producto original o nuevo -->
                  <span v-if="!detalle.id" class="nuevo-producto-badge">
                    <i class="fas fa-plus"></i> Nuevo
                  </span>
                </div>
                
                <div class="detalle-controls">
                  <div class="cantidad-control">
                    <label>Cantidad:</label>
                    <input
                      v-model.number="detalle.cantidad"
                      type="number"
                      min="1"
                      class="form-input small"
                      @change="actualizarSubtotal(detalle)"
                    />
                  </div>
                  
                  <div class="precio-control">
                    <label>Precio Unitario:</label>
                    <input
                      v-model.number="detalle.precio_unitario"
                      type="number"
                      step="0.01"
                      min="0"
                      class="form-input small"
                      @change="actualizarSubtotal(detalle)"
                    />
                  </div>
                  
                  <div class="subtotal">
                    <strong>Subtotal: ${{ detalle.subtotal }}</strong>
                  </div>
                  
                  <button 
                    type="button" 
                    @click="eliminarProducto(index)" 
                    class="btn-icon btn-danger"
                    title="Eliminar producto"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Resumen del pedido -->
            <div class="resumen-pedido">
              <div class="resumen-item">
                <span>Cantidad de productos:</span>
                <strong>{{ pedido.detalles.length }}</strong>
              </div>
              <div class="resumen-item">
                <span>Total del pedido:</span>
                <strong class="total">${{ totalPedido }}</strong>
              </div>
              <div class="resumen-item" v-if="pedidoOriginal">
                <span>Total original:</span>
                <strong :class="{'text-danger': totalPedido !== pedidoOriginal.total}">
                  ${{ pedidoOriginal.total }}
                </strong>
              </div>
            </div>
          </div>

          <div v-else class="no-productos">
            <i class="fas fa-box-open"></i>
            <p>No hay productos en el pedido</p>
            <small>Agregue productos usando la búsqueda</small>
          </div>
        </div>

        <!-- Información Adicional -->
        <div class="form-section">
          <h3>Información Adicional</h3>
          
          <div class="form-group">
            <label for="fecha_esperada">Fecha Esperada de Recepción</label>
            <input
              id="fecha_esperada"
              v-model="pedido.fecha_esperada_recepcion"
              type="date"
              class="form-input"
              :min="fechaMinima"
            />
          </div>

          <div class="form-group">
            <label for="observaciones">Observaciones</label>
            <textarea
              id="observaciones"
              v-model="pedido.observaciones"
              rows="3"
              placeholder="Observaciones adicionales sobre el pedido..."
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
              @click="resetearCambios" 
              class="btn btn-outline"
              :disabled="!hayCambios"
            >
              <i class="fas fa-undo"></i> Deshacer Cambios
            </button>
            <button 
              type="submit" 
              :disabled="!puedeActualizar || cargando" 
              class="btn btn-primary"
            >
              <span v-if="cargando">
                <i class="fas fa-spinner fa-spin"></i> Actualizando...
              </span>
              <span v-else>
                <i class="fas fa-save"></i> Actualizar Pedido
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
  proveedor: '',
  fecha_esperada_recepcion: '',
  observaciones: '',
  detalles: []
})

const pedidoOriginal = ref(null)
const proveedores = ref([])
const productos = ref([])
const cargando = ref(false)
const cargandoDatos = ref(true)
const cargandoProveedores = ref(false)
const busquedaProducto = ref('')

// Computed
const proveedoresActivos = computed(() => {
  return proveedores.value.filter(p => p.estado === 'ACTIVO')
})

const proveedorSeleccionado = computed(() => {
  return proveedores.value.find(p => p.id === pedido.value.proveedor)
})

const productosDisponibles = computed(() => {
  if (!busquedaProducto.value) return []
  
  const busqueda = busquedaProducto.value.toLowerCase()
  return productos.value.filter(producto => 
    !pedido.value.detalles.some(d => d.producto === producto.id) &&
    (producto.nombre.toLowerCase().includes(busqueda) || 
     (producto.codigo && producto.codigo.toLowerCase().includes(busqueda)))
  )
})

const totalPedido = computed(() => {
  return pedido.value.detalles.reduce((total, detalle) => total + detalle.subtotal, 0)
})

const puedeModificar = computed(() => {
  return pedidoOriginal.value && pedidoOriginal.value.estado === 'PENDIENTE'
})

const puedeActualizar = computed(() => {
  return pedido.value.proveedor && 
         pedido.value.detalles.length > 0 && 
         pedido.value.detalles.every(d => d.cantidad > 0 && d.precio_unitario > 0)
})

const hayCambios = computed(() => {
  if (!pedidoOriginal.value) return false
  
  return JSON.stringify(pedido.value) !== JSON.stringify(pedidoOriginal.value)
})

const fechaMinima = computed(() => {
  const hoy = new Date()
  return hoy.toISOString().split('T')[0]
})

// Métodos
const cargarDatos = async () => {
  try {
    cargandoDatos.value = true
    
    // Cargar datos del formulario
    const datosResponse = await axios.get(`${API_BASE}/usuarios/api/pedidos/datos-crear/`)
    proveedores.value = datosResponse.data.proveedores
    productos.value = datosResponse.data.productos
    
    // Cargar pedido existente
    const pedidoResponse = await axios.get(`${API_BASE}/usuarios/api/pedidos/${pedidoId}/`)
    pedidoOriginal.value = { ...pedidoResponse.data }
    
    // Preparar datos para edición
    pedido.value = {
      proveedor: pedidoResponse.data.proveedor,
      fecha_esperada_recepcion: pedidoResponse.data.fecha_esperada_recepcion || '',
      observaciones: pedidoResponse.data.observaciones || '',
      detalles: pedidoResponse.data.detalles.map(detalle => ({
        id: detalle.id,
        producto: detalle.producto,
        producto_nombre: detalle.producto_nombre,
        producto_codigo: detalle.producto_codigo,
        producto_stock_actual: detalle.producto_stock_actual,
        cantidad: detalle.cantidad,
        precio_unitario: parseFloat(detalle.precio_unitario),
        subtotal: parseFloat(detalle.subtotal)
      }))
    }
    
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

const seleccionarProducto = (producto) => {
  const yaAgregado = pedido.value.detalles.some(d => d.producto === producto.id)
  if (yaAgregado) {
    alert('Este producto ya está en el pedido')
    return
  }

  pedido.value.detalles.push({
    producto: producto.id,
    producto_nombre: producto.nombre,
    producto_codigo: producto.codigo,
    producto_stock_actual: producto.stock_actual,
    cantidad: 1,
    precio_unitario: producto.precio,
    subtotal: producto.precio
  })

  busquedaProducto.value = ''
}

const agregarProducto = () => {
  if (!busquedaProducto.value) {
    alert('Ingrese un término de búsqueda para agregar productos')
    return
  }
}

const eliminarProducto = (index) => {
  pedido.value.detalles.splice(index, 1)
}

const actualizarSubtotal = (detalle) => {
  detalle.subtotal = detalle.cantidad * detalle.precio_unitario
}

const resetearCambios = () => {
  if (!pedidoOriginal.value) return
  
  if (confirm('¿Estás seguro de deshacer todos los cambios?')) {
    pedido.value = { ...pedidoOriginal.value }
  }
}

const actualizarPedido = async () => {
  if (!puedeActualizar.value) {
    alert('Complete todos los campos obligatorios y verifique los productos')
    return
  }

  if (!confirm('¿Estás seguro de actualizar el pedido?')) {
    return
  }

  try {
    cargando.value = true
    
    const payload = {
      proveedor: pedido.value.proveedor,
      fecha_esperada_recepcion: pedido.value.fecha_esperada_recepcion || null,
      observaciones: pedido.value.observaciones || '',
      detalles: pedido.value.detalles.map(detalle => ({
        producto: detalle.producto,
        cantidad: detalle.cantidad,
        precio_unitario: detalle.precio_unitario
      }))
    }

    await axios.put(`${API_BASE}/usuarios/api/pedidos/${pedidoId}/`, payload)
    
    alert('✅ Pedido actualizado exitosamente')
    router.push('/pedidos')
    
  } catch (error) {
    console.error('Error actualizando pedido:', error)
    
    if (error.response?.status === 400) {
      const errors = error.response.data
      let errorMessage = 'Errores en el formulario:\n'
      
      Object.entries(errors).forEach(([field, messages]) => {
        errorMessage += `• ${field}: ${messages.join(', ')}\n`
      })
      
      alert(errorMessage)
    } else {
      alert('Error al actualizar el pedido: ' + (error.response?.data?.error || error.message))
    }
  } finally {
    cargando.value = false
  }
}

const volverAlListado = () => {
  router.push('/pedidos')
}

const filtrarProductos = () => {
  // La búsqueda se maneja en el computed
}

// Ciclo de vida
onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
.loading-full {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #6b7280;
}

.error-card {
  text-align: center;
  padding: 60px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
}

.error-card i {
  font-size: 3rem;
  margin-bottom: 20px;
}

.nuevo-producto-badge {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 4px;
  display: inline-block;
}

.text-danger {
  color: #dc2626;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

/* Reutiliza los mismos estilos del RegistrarPedido */
</style>