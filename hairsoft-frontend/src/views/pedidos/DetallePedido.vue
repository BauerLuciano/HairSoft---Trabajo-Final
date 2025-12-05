<template>
  <div class="list-container">
    <div class="list-card">
      <!-- Header con título y botones -->
      <div class="list-header">
        <div class="header-content">
          <h1>Detalle de Pedido</h1>
          <p>Información completa del pedido a proveedor #{{ pedidoId }}</p>
        </div>
        <div class="acciones-header">
          <button 
            v-if="pedido && pedido.estado === 'CONFIRMADO'" 
            @click="irARecibir" 
            class="register-button"
            :disabled="procesando"
          >
            <Truck :size="18" />
            {{ procesando ? 'Procesando...' : 'Recibir Mercadería' }}
          </button>
          <button 
            v-if="pedido && pedido.puede_cancelar" 
            @click="cancelarPedido" 
            class="action-button delete"
            :disabled="procesando"
          >
            <X :size="18" />
            Cancelar Pedido
          </button>
          <button @click="$router.push('/pedidos')" class="btn-volver">
            <ChevronLeft :size="18" />
            Volver a Pedidos
          </button>
        </div>
      </div>

      <!-- Estados de carga y error -->
      <div v-if="cargando" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Cargando detalle del pedido...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <AlertTriangle :size="48" />
        <p>{{ error }}</p>
        <button @click="obtenerPedido" class="btn-reintentar">
          <RefreshCw :size="16" />
          Reintentar
        </button>
        <button @click="$router.push('/pedidos')" class="btn-volver">
          <ChevronLeft :size="16" />
          Volver
        </button>
      </div>

      <!-- Contenido principal cuando hay datos -->
      <div v-else-if="pedido" class="detalle-contenido">
        <!-- Tarjeta de información principal -->
        <div class="detalle-card">
          <div class="detalle-header-card">
            <div class="titulo-pedido">
              <h2>Pedido #{{ pedido.id }}</h2>
              <span class="badge-estado" :class="getClaseEstado(pedido.estado)">
                {{ getEstadoTexto(pedido.estado) }}
              </span>
            </div>
            <div class="fecha-pedido">
              <Calendar :size="16" />
              {{ formatFecha(pedido.fecha_pedido) }}
            </div>
          </div>

          <!-- Información en grid -->
          <div class="grid-info">
            <div class="info-item">
              <label>Proveedor</label>
              <div class="info-value">
                <Truck :size="16" />
                <div>
                  <strong>{{ pedido.proveedor_nombre }}</strong>
                  <small v-if="pedido.proveedor_contacto" class="contacto-proveedor">
                    {{ pedido.proveedor_contacto }}
                  </small>
                </div>
              </div>
            </div>

            <div class="info-item">
              <label>Estado</label>
              <div class="info-value">
                <span class="badge-estado" :class="getClaseEstado(pedido.estado)">
                  {{ getEstadoTexto(pedido.estado) }}
                </span>
              </div>
            </div>

            <div class="info-item">
              <label>Creado por</label>
              <div class="info-value">
                <User :size="16" />
                {{ pedido.usuario_creador_nombre || 'Sistema' }}
              </div>
            </div>

            <div class="info-item">
              <label>Recepción Esperada</label>
              <div class="info-value">
                <CalendarCheck :size="16" />
                {{ pedido.fecha_esperada_recepcion ? formatFecha(pedido.fecha_esperada_recepcion) : 'Sin fecha definida' }}
              </div>
            </div>

            <div class="info-item">
              <label>Productos Solicitados</label>
              <div class="info-value">
                <Package :size="16" />
                {{ pedido.cantidad_productos || 0 }} productos
              </div>
            </div>

            <div class="info-item">
              <label>Total</label>
              <div class="info-value total-monto">
                <DollarSign :size="20" />
                ${{ formatPrecio(pedido.total_calculado || pedido.total || 0) }}
              </div>
            </div>
          </div>

          <!-- Tabla de productos -->
          <div class="tabla-detalle-container">
            <h3>
              <Package :size="20" />
              Detalle de Productos ({{ pedido.detalles?.length || 0 }})
            </h3>
            <div class="table-container">
              <table class="users-table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Código</th>
                    <th>Solicitado</th>
                    <th>Recibido</th>
                    <th>P. Unitario</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="detalle in pedido.detalles" :key="detalle.id">
                    <td>
                      <strong>{{ detalle.producto_nombre || 'Producto sin nombre' }}</strong>
                    </td>
                    <td>{{ detalle.producto_codigo || 'N/A' }}</td>
                    <td>
                      <span class="cantidad-solicitada">{{ detalle.cantidad }}</span>
                    </td>
                    <td>
                      <span :class="['cantidad-recibida', 
                                   { 'completo': detalle.cantidad_recibida === detalle.cantidad,
                                     'parcial': detalle.cantidad_recibida > 0 && detalle.cantidad_recibida < detalle.cantidad,
                                     'pendiente': !detalle.cantidad_recibida || detalle.cantidad_recibida === 0 }]">
                        {{ detalle.cantidad_recibida || 0 }}
                      </span>
                    </td>
                    <td>
                      <span v-if="detalle.precio_unitario" class="precio-unitario">
                        ${{ formatPrecio(detalle.precio_unitario) }}
                      </span>
                      <span v-else class="precio-pendiente">Pendiente</span>
                    </td>
                    <td><strong>${{ formatPrecio(detalle.subtotal || 0) }}</strong></td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="5" class="total-label">
                      <strong>TOTAL</strong>
                    </td>
                    <td class="total-final">
                      <strong>${{ formatPrecio(pedido.total_calculado || pedido.total || 0) }}</strong>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Observaciones -->
          <div v-if="pedido.observaciones" class="observaciones-container">
            <div class="observacion-header">
              <MessageSquare :size="18" />
              <h4>Observaciones</h4>
            </div>
            <div class="observacion-contenido">
              {{ pedido.observaciones }}
            </div>
          </div>

          <!-- Información adicional -->
          <div v-if="pedido.fecha_recepcion || pedido.estado === 'ENTREGADO'" class="info-extra">
            <div class="info-item-extra" v-if="pedido.fecha_recepcion">
              <label>Fecha de Recepción Real</label>
              <div class="info-value-extra">
                <CalendarCheck :size="16" />
                {{ formatFecha(pedido.fecha_recepcion) }}
              </div>
            </div>
            <div class="info-item-extra" v-if="pedido.estado === 'ENTREGADO'">
              <label>Estado de Stock</label>
              <div class="info-value-extra stock-actualizado">
                <CheckCircle :size="16" />
                Stock actualizado en sistema
              </div>
            </div>
          </div>
        </div>

        <!-- Botones de acción inferiores -->
        <div class="acciones-inferiores">
          <div class="acciones-izquierda">
            <button 
              v-if="pedido.estado === 'CONFIRMADO'" 
              @click="irARecibir" 
              class="action-button success"
              :disabled="procesando"
            >
              <Truck :size="16" />
              Recibir Mercadería
            </button>
            <button 
              v-if="pedido.puede_cancelar" 
              @click="cancelarPedido" 
              class="action-button delete"
              :disabled="procesando"
            >
              <X :size="16" />
              Cancelar Pedido
            </button>
            <button 
              v-if="pedido.estado === 'PENDIENTE'" 
              @click="editarPedido" 
              class="action-button edit"
              :disabled="procesando"
            >
              <Edit3 :size="16" />
              Editar Pedido
            </button>
          </div>
          <div class="acciones-derecha">
            <button @click="imprimir" class="action-button info">
              <Printer :size="16" />
              Imprimir
            </button>
            <button @click="$router.push('/pedidos')" class="btn-volver">
              <ChevronLeft :size="16" />
              Volver
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  ChevronLeft, RefreshCw, AlertTriangle, Calendar, CalendarCheck,
  User, Truck, DollarSign, Package, MessageSquare, CheckCircle,
  Edit3, X, Printer, Eye, PackageX, ArrowLeft, ArrowRight,
  Plus, Trash2, FileText, Loader
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const pedidoId = route.params.id
const pedido = ref(null)
const cargando = ref(true)
const error = ref(null)
const procesando = ref(false)

// Obtener datos del pedido
const obtenerPedido = async () => {
  cargando.value = true
  error.value = null
  
  try {
    console.log(`🔄 Cargando detalle del pedido #${pedidoId}...`)
    const token = localStorage.getItem('token')
    
    const response = await axios.get(`${API_BASE}/usuarios/api/pedidos/${pedidoId}/`, {
      headers: {
        'Authorization': `Token ${token}`
      }
    })
    
    if (response.data) {
      pedido.value = procesarPedido(response.data)
      console.log('✅ Detalle del pedido cargado:', pedido.value)
    } else {
      error.value = 'Pedido no encontrado'
      console.log('📭 No se encontró el pedido')
    }
  } catch (err) {
    console.error('❌ Error cargando detalle del pedido:', err.response || err)
    error.value = err.response?.data?.error || err.response?.data?.detail || err.message || 'Error al cargar el pedido'
    
    if (err.response?.status === 401) {
      Swal.fire({
        icon: 'error',
        title: 'Sesión expirada',
        text: 'Por favor, inicie sesión nuevamente.',
        confirmButtonText: 'Entendido'
      }).then(() => {
        router.push('/login')
      })
    }
  } finally {
    cargando.value = false
  }
}

// Procesar datos del pedido para añadir propiedades útiles
const procesarPedido = (pedidoData) => {
  // Calcular cantidad total de productos
  const cantidadProductos = pedidoData.detalles?.reduce((sum, detalle) => sum + (detalle.cantidad || 0), 0) || 0
  
  // Determinar si se puede cancelar
  const puedeCancelar = pedidoData.estado === 'PENDIENTE' || pedidoData.estado === 'CONFIRMADO'
  
  return {
    ...pedidoData,
    cantidad_productos: cantidadProductos,
    puede_cancelar: puedeCancelar
  }
}

// Funciones de utilidad (iguales a las del listado de pedidos)
const formatFecha = (fechaString) => {
  if (!fechaString) return '-'
  try {
    const fecha = new Date(fechaString)
    if (isNaN(fecha.getTime())) return 'Fecha inválida'
    
    return fecha.toLocaleDateString('es-AR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  } catch (e) {
    console.error("Error formateando fecha:", e)
    return 'Error fecha'
  }
}

const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  return parseFloat(precio).toFixed(2)
}

const getEstadoTexto = (estado) => {
  const estados = {
    'PENDIENTE': 'Pendiente',
    'CONFIRMADO': 'Confirmado',
    'ENTREGADO': 'Entregado',
    'CANCELADO': 'Cancelado',
    'PARCIAL': 'Parcialmente Recibido'
  }
  return estados[estado] || estado
}

const getClaseEstado = (estado) => {
  const clases = {
    'PENDIENTE': 'estado-warning',
    'CONFIRMADO': 'estado-info',
    'ENTREGADO': 'estado-success',
    'CANCELADO': 'estado-danger',
    'PARCIAL': 'estado-warning'
  }
  return clases[estado] || 'estado-secondary'
}

// Funciones de acción
const irARecibir = () => {
  if (!pedido.value || procesando.value) return
  
  // Verificar que el pedido puede ser recibido
  if (!['PENDIENTE', 'CONFIRMADO', 'PARCIAL'].includes(pedido.value.estado)) {
    Swal.fire({
      icon: 'warning',
      title: 'No recibible',
      text: 'Solo se pueden recibir pedidos en estado PENDIENTE, CONFIRMADO o PARCIAL',
      confirmButtonText: 'Entendido'
    })
    return
  }
  
  router.push({ name: 'RecibirPedido', params: { id: pedidoId } })
}

const cancelarPedido = async () => {
  if (!pedido.value || !pedido.value.puede_cancelar || procesando.value) return
  
  const result = await Swal.fire({
    title: '¿Cancelar Pedido?',
    html: `
      <div style="text-align: left;">
        <p><strong>Pedido #${pedido.value.id}</strong></p>
        <p><strong>Proveedor:</strong> ${pedido.value.proveedor_nombre}</p>
        <p><strong>Total:</strong> $${formatPrecio(pedido.value.total_calculado || pedido.value.total || 0)}</p>
        <p><strong>Productos:</strong> ${pedido.value.detalles?.length || 0} items</p>
        <hr style="margin: 15px 0;">
        <p style="color: #e53e3e; font-weight: bold;">
          ⚠️ Esta acción no se puede deshacer
        </p>
        <ul style="text-align: left; margin: 10px 0; padding-left: 20px;">
          <li>Marcará el pedido como CANCELADO</li>
          <li>No se podrá recibir mercadería</li>
          <li>Se notificará al proveedor</li>
        </ul>
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, cancelar pedido',
    cancelButtonText: 'Cancelar',
    reverseButtons: true,
    backdrop: true,
    allowOutsideClick: false
  })
  
  if (!result.isConfirmed) return
  
  procesando.value = true
  
  try {
    const token = localStorage.getItem('token')
    
    await axios.post(`${API_BASE}/usuarios/api/pedidos/${pedidoId}/cancelar/`, {}, {
      headers: {
        'Authorization': `Token ${token}`
      }
    })
    
    Swal.fire({
      icon: 'success',
      title: 'Pedido Cancelado',
      text: 'El pedido se ha cancelado exitosamente',
      timer: 3000,
      showConfirmButton: false
    })
    
    // Recargar datos del pedido
    await obtenerPedido()
    
  } catch (err) {
    console.error('❌ Error cancelando pedido:', err.response || err)
    
    let errorMessage = 'No se pudo cancelar el pedido'
    if (err.response?.data?.error) {
      errorMessage = err.response.data.error
    } else if (err.response?.status === 404) {
      errorMessage = 'Pedido no encontrado'
    } else if (err.response?.status === 400) {
      errorMessage = err.response.data.detail || 'No se puede cancelar el pedido en su estado actual'
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Error al Cancelar',
      text: errorMessage,
      confirmButtonText: 'Entendido'
    })
  } finally {
    procesando.value = false
  }
}

const editarPedido = () => {
  if (!pedido.value || pedido.value.estado !== 'PENDIENTE') {
    Swal.fire({
      icon: 'warning',
      title: 'No editable',
      text: 'Solo se pueden editar pedidos en estado PENDIENTE',
      confirmButtonText: 'Entendido'
    })
    return
  }
  
  router.push({ name: 'ModificarPedido', params: { id: pedidoId } })
}

const imprimir = () => {
  window.print()
}

onMounted(() => {
  obtenerPedido()
})
</script>

<style scoped>
/* Mismas variables CSS que el listado de pedidos/ventas */
.list-container {
  padding: 30px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* Tarjeta principal - IDÉNTICA al listado de pedidos */
.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1400px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
  border: 1px solid var(--border-color);
}

/* Borde superior azul acero - IDÉNTICO */
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* HEADER - IDÉNTICO */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 25px;
}

.header-content h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.header-content p {
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.5px;
}

.acciones-header {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

/* Botón Volver - estilo similar al register-button pero diferente color */
.btn-volver {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 14px 28px;
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

.btn-volver:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: #6b7280;
}

/* LOADING STATE - IDÉNTICO */
.loading-state {
  text-align: center;
  padding: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ERROR STATE - similar al no-results */
.error-state {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.error-state svg {
  margin-bottom: 0;
  opacity: 0.5;
  color: var(--error-color);
}

.error-state p {
  margin: 0;
  font-size: 1.1em;
  color: var(--text-primary);
}

/* Botón reintentar IDÉNTICO */
.btn-reintentar {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.btn-reintentar:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5);
}

/* DETALLE CONTENIDO */
.detalle-contenido {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Tarjeta de detalle */
.detalle-card {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 30px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  margin-bottom: 30px;
}

.detalle-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.titulo-pedido {
  display: flex;
  align-items: center;
  gap: 15px;
}

.titulo-pedido h2 {
  margin: 0;
  font-size: 1.8rem;
  color: var(--text-primary);
  font-weight: 800;
}

.fecha-pedido {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-weight: 600;
  background: var(--bg-tertiary);
  padding: 10px 18px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

/* GRID DE INFORMACIÓN */
.grid-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.info-item {
  background: var(--hover-bg);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.info-item:hover {
  background: var(--bg-tertiary);
  transform: translateY(-3px);
  box-shadow: var(--shadow-sm);
}

.info-item label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.info-value {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.info-value.total-monto {
  font-size: 1.5rem;
  color: #10b981;
}

.contacto-proveedor {
  display: block;
  font-size: 0.85rem;
  color: var(--text-tertiary);
  margin-top: 4px;
  font-weight: 500;
}

/* TABLA DETALLE */
.tabla-detalle-container h3 {
  font-size: 1.3rem;
  color: var(--text-primary);
  margin-bottom: 20px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 10px;
}

.tabla-detalle-container .table-container {
  margin-bottom: 0;
}

/* Estilos para cantidades */
.cantidad-solicitada {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 700;
}

.cantidad-recibida {
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 700;
}

.cantidad-recibida.completo {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.cantidad-recibida.parcial {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.cantidad-recibida.pendiente {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.precio-unitario {
  color: var(--text-primary);
  font-weight: 700;
}

.precio-pendiente {
  color: var(--text-tertiary);
  font-style: italic;
  font-size: 0.9rem;
}

.total-label {
  text-align: right;
  padding: 20px !important;
  font-size: 1.2rem;
  background: var(--bg-tertiary);
}

.total-final {
  font-size: 1.4rem;
  color: #10b981;
  padding: 20px !important;
  background: var(--bg-tertiary);
}

/* OBSERVACIONES */
.observaciones-container {
  margin-top: 30px;
  padding: 20px;
  background: var(--hover-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.observacion-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.observacion-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
  font-weight: 700;
}

.observacion-contenido {
  color: var(--text-secondary);
  line-height: 1.6;
  white-space: pre-line;
}

/* INFORMACIÓN EXTRA */
.info-extra {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 25px;
  padding-top: 25px;
  border-top: 2px solid var(--border-color);
}

.info-item-extra {
  background: var(--hover-bg);
  padding: 15px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.info-item-extra label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--text-tertiary);
  font-weight: 700;
  letter-spacing: 0.8px;
  margin-bottom: 6px;
}

.info-value-extra {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.stock-actualizado {
  color: #10b981;
}

/* ACCIONES INFERIORES */
.acciones-inferiores {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 25px;
  border-top: 2px solid var(--border-color);
  flex-wrap: wrap;
  gap: 15px;
}

.acciones-izquierda {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.acciones-derecha {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

/* BADGES DE ESTADO - IDÉNTICOS al listado de pedidos */
.badge-estado {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
}

.estado-warning {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.estado-info {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.estado-success {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.estado-danger {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
  opacity: 0.75;
}

.estado-secondary {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  border: 2px solid var(--text-tertiary);
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* BOTONES DE ACCIÓN - IDÉNTICOS al listado */
.action-button {
  padding: 12px 24px;
  height: 44px;
  font-size: 0.9rem;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  gap: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 120px;
}

.action-button.edit {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.action-button.edit:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-button.delete {
  background: var(--bg-tertiary);
  border: 1px solid var(--error-color);
  color: var(--error-color);
}
.action-button.delete:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  border-color: var(--error-color);
}

.action-button.success {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  border: 2px solid #059669;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}
.action-button.success:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.5);
  border-color: #047857;
}

.action-button.info {
  background: var(--bg-tertiary);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
}
.action-button.info:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
  border-color: var(--accent-color);
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* Botón Registrar (Recibir) - IDÉNTICO */
.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.register-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.register-button:hover::before {
  left: 100%;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* TABLA - IDÉNTICA */
.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

.users-table th {
  background: var(--accent-color);
  color: white;
  padding: 18px 14px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1.2px;
}

.users-table tr {
  border-bottom: 1px solid var(--border-color);
}

.users-table td {
  padding: 14px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-weight: 500;
}

.users-table td strong {
  color: var(--text-primary);
  font-weight: 800;
  letter-spacing: 0.3px;
}

.users-table tr:hover {
  background: var(--hover-bg);
  transition: all 0.2s ease;
}

.users-table tfoot tr {
  background: var(--bg-tertiary);
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-card {
    padding: 25px;
    border-radius: 20px;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-content h1 {
    font-size: 1.6rem;
  }
  
  .acciones-header {
    flex-direction: column;
    width: 100%;
  }
  
  .acciones-header button {
    width: 100%;
    justify-content: center;
  }
  
  .detalle-header-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .grid-info {
    grid-template-columns: 1fr;
  }
  
  .acciones-inferiores {
    flex-direction: column;
    align-items: stretch;
  }
  
  .acciones-izquierda, .acciones-derecha {
    flex-direction: column;
    width: 100%;
  }
  
  .acciones-izquierda button, .acciones-derecha button {
    width: 100%;
    justify-content: center;
  }
  
  .users-table {
    font-size: 0.85rem;
  }
  
  .users-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
  }
}

@media (max-width: 480px) {
  .list-card {
    padding: 18px;
    border-radius: 16px;
  }
  
  .header-content h1 {
    font-size: 1.4rem;
  }
  
  .detalle-card {
    padding: 18px;
  }
  
  .users-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .info-item {
    padding: 15px;
  }
  
  .info-value {
    font-size: 1rem;
  }
  
  .info-value.total-monto {
    font-size: 1.2rem;
  }
  
  .action-button {
    padding: 12px 16px;
    font-size: 0.85rem;
    min-width: 100px;
  }
}

/* ESTILOS PARA IMPRESIÓN */
@media print {
  .list-header, .acciones-inferiores, .btn-volver, .register-button, .action-button {
    display: none !important;
  }
  
  .list-container {
    padding: 0;
    background: white;
  }
  
  .list-card {
    box-shadow: none;
    border: none;
    padding: 0;
  }
  
  .list-card::before {
    display: none;
  }
  
  .detalle-card {
    box-shadow: none;
    border: 1px solid #ddd;
    margin: 0;
  }
  
  .users-table {
    box-shadow: none;
    border: 1px solid #ddd;
  }
  
  body {
    color: black !important;
    background: white !important;
  }
}
</style>