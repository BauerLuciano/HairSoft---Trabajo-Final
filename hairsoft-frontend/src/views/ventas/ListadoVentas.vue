<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de ventas</h1>
          <p>Gestión de ventas del sistema</p>
        </div>
        <button @click="mostrarRegistrar = true" class="register-button">
          <Plus :size="18" />
          Registrar Venta
        </button>
      </div>

      <!-- Filtros Mejorados -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Cliente, Usuario o ID..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Fecha desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Fecha hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input"/>
          </div>

          <!-- NUEVOS FILTROS -->
          <div class="filter-group">
            <label>Método Pago</label>
            <select v-model="filtros.metodoPago" class="filter-input">
              <option value="">Todos</option>
              <option value="EFECTIVO">Efectivo</option>
              <option value="TARJETA">Tarjeta</option>
              <option value="TRANSFERENCIA">Transferencia</option>
              <option value="MERCADO_PAGO">Mercado Pago</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Tipo</label>
            <select v-model="filtros.tipo" class="filter-input">
              <option value="">Todos</option>
              <option value="PRODUCTO">Producto</option>
              <option value="TURNO">Turno</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos</option>
              <option value="activa">Activa</option>
              <option value="anulada">Anulada</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              <Trash2 :size="16" />
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>

      <!-- Estados de carga -->
      <div v-if="cargando" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Cargando ventas...</p>
      </div>

      <!-- Tabla de ventas -->
      <div v-else class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Cliente</th>
              <th>Usuario</th>
              <th>Fecha</th>
              <th>Total</th>
              <th>Método Pago</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Comprobante</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="venta in ventasPaginadas" :key="venta.id" 
                :class="{'venta-anulada-row': venta.anulada}">
              <td><strong>#{{ venta.id }}</strong></td>
              <td>{{ venta.cliente_nombre || 'Venta Rápida' }}</td>
              <td>{{ venta.usuario_nombre || '–' }}</td>
              <td>{{ formatFecha(venta.fecha) }}</td>
              <td><strong>${{ formatPrecio(venta.total) }}</strong></td>
              <td>
                <span class="badge-pago" :class="getClaseTipoPago(venta.medio_pago_tipo)">
                  {{ venta.medio_pago_nombre || '–' }}
                </span>
              </td>
              <td>
                <span class="badge-tipo" :class="getClaseTipoVenta(venta.tipo)">
                  {{ venta.tipo || '–' }}
                </span>
              </td>
              <td>
                <span class="badge-estado" :class="getClaseEstadoVenta(venta.anulada)">
                  {{ venta.anulada ? '❌ ANULADA' : '✅ ACTIVA' }}
                </span>
              </td>
              <td>
                <button 
                  @click="generarComprobantePDF(venta)" 
                  class="btn-comprobante"
                  :title="`Descargar comprobante PDF venta #${venta.id}`"
                  :disabled="generandoPDF === venta.id || venta.anulada"
                >
                  <FileText :size="14" v-if="generandoPDF !== venta.id" />
                  <Loader :size="14" v-else />
                  {{ generandoPDF === venta.id ? 'Generando...' : 'PDF' }}
                </button>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="editarVenta(venta)" 
                    class="action-button edit" 
                    :disabled="venta.anulada"
                    :title="venta.anulada ? 'No se puede editar venta anulada' : 'Editar venta'"
                  >
                    <Edit3 :size="14" />
                  </button>
                  <button 
                    @click="anularVenta(venta)" 
                    class="action-button delete" 
                    :disabled="venta.anulada"
                    :title="venta.anulada ? 'Venta ya anulada' : 'Anular venta'"
                  >
                    <Trash2 :size="14" />
                  </button>
                  <button 
                    @click="verDetallesVenta(venta)" 
                    class="action-button info"
                    title="Ver detalles de venta"
                  >
                    <Eye :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="ventasPaginadas.length === 0 && !cargando" class="no-results">
          <PackageX class="no-results-icon" :size="48" />
          <p>No se encontraron ventas</p>
          <small>Intenta con otros términos de búsqueda</small>
          <button @click="cargarVentas" class="btn-reintentar">
            <RefreshCw :size="16" />
            Reintentar
          </button>
        </div>
      </div>

      <!-- Contador y mensajes -->
      <div v-if="!cargando" class="usuarios-count">
        <p>
          <Package :size="16" />
          Mostrando {{ ventasPaginadas.length }} de {{ ventasFiltradas.length }} ventas
        </p>
        <div class="alertas-container">
          <span v-if="ventasAnuladas > 0" class="alerta-anulada">
            <AlertTriangle :size="14" />
            {{ ventasAnuladas }} anuladas
          </span>
          <span v-if="ventaRecienCreada" class="venta-reciente">
            <CheckCircle :size="14" />
            Venta #{{ ventaRecienCreada }} registrada
          </span>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="!cargando && ventasFiltradas.length > 0" class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">
          <ChevronLeft :size="16" />
          Anterior
        </button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">
          Siguiente
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- Modales -->
    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <RegistrarVenta 
          @venta-registrada="procesarVentaRegistrada" 
          @venta-completada="cerrarModal"
          @cancelar="cerrarModal"
        />
      </div>
    </div>

    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
        <ModificarVenta 
          :venta-id="ventaEditando?.id" 
          @venta-actualizada="ventaActualizada"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import RegistrarVenta from './RegistrarVenta.vue'
import ModificarVenta from './ModificarVenta.vue'
import { 
  Plus, Trash2, Edit3, Eye, FileText, Loader, Package, PackageX,
  ChevronLeft, ChevronRight, X, AlertTriangle, CheckCircle, RefreshCw
} from 'lucide-vue-next'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const ventas = ref([])
const filtros = ref({ 
  busqueda: '', 
  fechaDesde: '', 
  fechaHasta: '',
  metodoPago: '',
  tipo: '',
  estado: ''
})
const pagina = ref(1)
const itemsPorPagina = 8
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const ventaEditando = ref(null)
const cargando = ref(false)
const ventaRecienCreada = ref(null)
const generandoPDF = ref(null)

// Cargar ventas del backend
const cargarVentas = async () => {
  cargando.value = true
  try {
    console.log('🔄 Cargando ventas desde:', `${API_BASE}/usuarios/api/ventas/`)
    const res = await axios.get(`${API_BASE}/usuarios/api/ventas/`)
    
    if (res.data && Array.isArray(res.data) && res.data.length > 0) {
      // Ordenar por fecha descendente
      ventas.value = res.data.sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
      console.log('✅ Ventas cargadas:', ventas.value.length)
    } else {
      console.log('📭 No hay ventas registradas')
      ventas.value = []
    }
  } catch (err) {
    console.error('❌ Error cargando ventas:', err.response || err)
    Swal.fire({
      icon: 'error',
      title: 'Error al Cargar Ventas',
      text: err.response?.data?.message || err.message,
      confirmButtonText: 'Entendido'
    })
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  cargarVentas()
})

// Computed properties
const ventasFiltradas = computed(() => {
  const busca = filtros.value.busqueda.toLowerCase()
  return ventas.value.filter(v => {
    // Filtro de búsqueda
    const matchBusqueda = !busca || 
      (v.cliente_nombre?.toLowerCase().includes(busca) || 
       v.usuario_nombre?.toLowerCase().includes(busca) ||
       v.medio_pago_nombre?.toLowerCase().includes(busca) ||
       v.id.toString().includes(busca))
    
    // Filtro de fecha
    const fecha = v.fecha ? new Date(v.fecha) : null
    const matchFechaDesde = !filtros.value.fechaDesde || (fecha && fecha >= new Date(filtros.value.fechaDesde))
    const matchFechaHasta = !filtros.value.fechaHasta || (fecha && fecha <= new Date(filtros.value.fechaHasta + 'T23:59:59'))
    
    // Nuevos filtros
    const matchMetodoPago = !filtros.value.metodoPago || v.medio_pago_tipo === filtros.value.metodoPago
    const matchTipo = !filtros.value.tipo || v.tipo?.toLowerCase() === filtros.value.tipo.toLowerCase()
    const matchEstado = !filtros.value.estado || 
      (filtros.value.estado === 'activa' && !v.anulada) ||
      (filtros.value.estado === 'anulada' && v.anulada)
    
    return matchBusqueda && matchFechaDesde && matchFechaHasta && matchMetodoPago && matchTipo && matchEstado
  })
})

const ventasAnuladas = computed(() => ventasFiltradas.value.filter(v => v.anulada).length)
const totalPaginas = computed(() => Math.max(1, Math.ceil(ventasFiltradas.value.length / itemsPorPagina)))
const ventasPaginadas = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return ventasFiltradas.value.slice(inicio, inicio + itemsPorPagina)
})

// Funciones de paginación
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Funciones de ventas
const editarVenta = (venta) => {
  if (venta.anulada) {
    Swal.fire({
      icon: 'warning',
      title: 'Venta Anulada',
      text: 'No se puede editar una venta anulada',
      confirmButtonText: 'Entendido'
    })
    return
  }
  ventaEditando.value = venta
  mostrarEditar.value = true
}

const verDetallesVenta = (venta) => {
  Swal.fire({
    title: `Detalles Venta #${venta.id}`,
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${venta.cliente_nombre || 'Venta Rápida'}</p>
        <p><strong>Usuario:</strong> ${venta.usuario_nombre || '–'}</p>
        <p><strong>Fecha:</strong> ${formatFecha(venta.fecha)}</p>
        <p><strong>Total:</strong> $${formatPrecio(venta.total)}</p>
        <p><strong>Método Pago:</strong> ${venta.medio_pago_nombre || '–'}</p>
        <p><strong>Tipo:</strong> ${venta.tipo || '–'}</p>
        <p><strong>Estado:</strong> ${venta.anulada ? '❌ ANULADA' : '✅ ACTIVA'}</p>
      </div>
    `,
    icon: 'info',
    confirmButtonText: 'Cerrar'
  })
}

const generarComprobantePDF = async (venta) => {
  if (generandoPDF.value === venta.id || venta.anulada) return
  
  generandoPDF.value = venta.id
  console.log(`📄 Generando comprobante PDF para venta #${venta.id}`)
  
  try {
    Swal.fire({
      title: 'Generando PDF...',
      text: 'Por favor espere',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    const url = `${API_BASE}/usuarios/api/ventas/${venta.id}/comprobante-pdf/`
    window.open(url, '_blank')
    
    Swal.close()
    Swal.fire({
      icon: 'success',
      title: 'PDF Generado',
      text: `Comprobante para venta #${venta.id} generado correctamente`,
      timer: 2000,
      showConfirmButton: false
    })
    
  } catch (error) {
    console.error('❌ Error generando PDF:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo generar el comprobante PDF',
      confirmButtonText: 'Entendido'
    })
  } finally {
    generandoPDF.value = null
  }
}

const anularVenta = async (venta) => {
  if (venta.anulada) {
    Swal.fire({
      icon: 'warning',
      title: 'Venta Ya Anulada',
      text: 'Esta venta ya está anulada',
      confirmButtonText: 'Entendido'
    })
    return
  }
  
  const result = await Swal.fire({
    title: '¿Anular Venta?',
    html: `
      <div style="text-align: left;">
        <p><strong>Venta #${venta.id}</strong></p>
        <p><strong>Cliente:</strong> ${venta.cliente_nombre || 'Venta Rápida'}</p>
        <p><strong>Total:</strong> $${venta.total}</p>
        <p><strong>Fecha:</strong> ${formatFecha(venta.fecha)}</p>
        <hr style="margin: 15px 0;">
        <p style="color: #e53e3e; font-weight: bold;">
          ⚠️ Esta acción no se puede deshacer
        </p>
        <ul style="text-align: left; margin: 10px 0; padding-left: 20px;">
          <li>Marcará la venta como ANULADA</li>
          <li>Devolverá el stock de los productos</li>
        </ul>
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, anular venta',
    cancelButtonText: 'Cancelar',
    reverseButtons: true,
    backdrop: true,
    allowOutsideClick: false
  })
  
  if (!result.isConfirmed) return
  
  try {
    cargando.value = true
    console.log(`🔄 Anulando venta #${venta.id}...`)
    
    Swal.fire({
      title: 'Anulando Venta...',
      text: 'Por favor espere',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    const response = await axios.post(`${API_BASE}/usuarios/api/ventas/${venta.id}/anular/`)
    
    if (response.status === 200) {
      const ventaIndex = ventas.value.findIndex(v => v.id === venta.id)
      if (ventaIndex !== -1) {
        ventas.value[ventaIndex].anulada = true
      }
      
      await cargarVentas()
      
      Swal.fire({
        icon: 'success',
        title: 'Venta Anulada',
        text: `Venta #${venta.id} anulada correctamente. Stock actualizado.`,
        timer: 3000,
        showConfirmButton: false
      })
      
      console.log(`✅ Venta #${venta.id} anulada exitosamente`)
    }
  } catch (err) {
    console.error('❌ Error anulando venta:', err.response || err)
    
    let errorMessage = 'No se pudo anular la venta'
    if (err.response?.data?.error) {
      errorMessage = err.response.data.error
    } else if (err.response?.status === 404) {
      errorMessage = 'Venta no encontrada'
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Error al Anular',
      text: errorMessage,
      confirmButtonText: 'Entendido'
    })
  } finally {
    cargando.value = false
  }
}

// Funciones de modal
const cerrarModal = () => { mostrarRegistrar.value = false }
const cerrarModalEditar = () => { mostrarEditar.value = false; ventaEditando.value = null }

const procesarVentaRegistrada = async (ventaData) => {
  console.log('🎯 EVENTO RECIBIDO - Venta registrada:', ventaData)
  
  if (ventaData && ventaData.id) {
    const nuevaVenta = {
      ...ventaData,
      cliente_nombre: 'Venta Rápida',
      usuario_nombre: 'Sistema', 
      medio_pago_nombre: 'Efectivo',
      tipo: 'PRODUCTO',
      anulada: false,
      fecha: ventaData.fecha || new Date().toISOString()
    }
    
    ventas.value.unshift(nuevaVenta)
    
    ventaRecienCreada.value = ventaData.id
    setTimeout(() => {
      ventaRecienCreada.value = null
    }, 5000)
    
    console.log('✅ Venta agregada al listado - Modal sigue abierto')
  }
}

const ventaActualizada = async () => {
  await cargarVentas()
  cerrarModalEditar()
  Swal.fire({
    icon: 'success',
    title: 'Venta Actualizada',
    text: 'La venta se ha actualizado correctamente',
    timer: 2000,
    showConfirmButton: false
  })
}

const limpiarFiltros = () => {
  filtros.value = { 
    busqueda: '', 
    fechaDesde: '', 
    fechaHasta: '',
    metodoPago: '',
    tipo: '',
    estado: ''
  }
  pagina.value = 1
}

// Funciones de utilidad
const formatFecha = (fecha) => {
  if (!fecha) return '–'
  try {
    const dateObj = new Date(fecha)
    if (isNaN(dateObj.getTime())) return 'Fecha inválida'
    return dateObj.toLocaleString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
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

const getClaseTipoPago = (tipoPago) => {
  const tipos = {
    'EFECTIVO': 'efectivo',
    'TARJETA': 'tarjeta',
    'TRANSFERENCIA': 'transferencia',
    'MERCADO_PAGO': 'mercadopago'
  }
  return tipos[tipoPago] || 'default'
}

const getClaseTipoVenta = (tipo) => {
  const tipos = {
    'PRODUCTO': 'producto',
    'TURNO': 'turno',
    'MIXTO': 'mixto'
  }
  return tipos[tipo] || 'default'
}

const getClaseEstadoVenta = (anulada) => {
  return anulada ? 'estado-anulada' : 'estado-activa'
}
</script>

<style scoped>

/* Tarjeta principal - CON VARIABLES */
.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
  border: 1px solid var(--border-color);
}

/* Borde superior azul acero */
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* BADGES DE ESTADO - CON VARIABLES */
.badge-estado {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
}

.estado-activa {
  background: var(--bg-tertiary);
  color: var(--success-color);
  border: 2px solid var(--success-color);
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.estado-anulada {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
  opacity: 0.75;
}

/* HEADER - CON VARIABLES */
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

/* BOTONES DE ACCIÓN - tamaño similar a Registrar Producto */
.action-button {
  padding: 12px 16px;           /* espacio interno más amplio */
  width: auto;                  /* ancho automático según contenido */
  height: 44px;                 /* altura parecida al register-button */
  font-size: 0.9rem;            /* texto más visible */
  border-radius: 12px;          /* bordes redondeados */
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

/* Editar */
.action-button.edit {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.action-button.edit:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* Eliminar */
.action-button.delete {
  background: var(--bg-tertiary);
  border: 1px solid var(--error-color);
  color: var(--error-color);
}
.action-button.delete:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  border-color: var(--error-color);
}

/* Éxito */
.action-button.success {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}
.action-button.success:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  border-color: #10b981;
}
/* Botón Detalle de venta */
.action-button.detalle {
  background: var(--bg-tertiary); /* mismo fondo que los demás */
  border: 1px solid #0ea5e9;     /* borde azul, como info */
  color: #0ea5e9;                 /* texto azul */
}

.action-button.detalle:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
  border-color: #0ea5e9;
}

/* BOTÓN DE COMPROBANTE PDF MEJORADO */
.btn-comprobante {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 800;
  transition: all 0.3s ease;
  min-width: 80px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
}

.btn-comprobante:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

.btn-comprobante:disabled {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  opacity: 0.5;
  border: 1px solid var(--border-color);
}

/* NUEVOS BADGES PARA TIPOS DE VENTA */
.badge-tipo.mixto {
  background: var(--bg-tertiary);
  color: #8b5cf6;
  border: 2px solid #8b5cf6;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.2);
}

/* ESTILO PARA FILA DE VENTA ANULADA */
.venta-anulada-row {
  background: rgba(239, 68, 68, 0.05);
  opacity: 0.7;
}

.venta-anulada-row:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* ALERTAS MEJORADAS */
.alerta-anulada {
  background: var(--bg-tertiary);
  color: #ef4444;
  border: 2px solid #ef4444;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.venta-reciente {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: fadeIn 0.5s ease;
}

/* LOADING STATE MEJORADO */
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

/* NO RESULTS MEJORADO */
.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.no-results-icon {
  margin-bottom: 0;
  opacity: 0.5;
  color: var(--text-tertiary);
}

.no-results p {
  margin: 0;
  font-size: 1.1em;
  color: var(--text-primary);
}

.no-results small {
  font-size: 0.9em;
  color: var(--text-tertiary);
}

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


/* Botones azules pueden quedar igual */
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

.register-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

/* FILTROS - CON VARIABLES */
.filters-container {
  margin-bottom: 30px;
  background: var(--hover-bg);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 18px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}

.filter-input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
  box-sizing: border-box; /* importante para que width funcione correctamente */
}

.filter-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

.clear-filters-btn {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.8px;
}

.clear-filters-btn:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* ESTADOS DE CARGA - CON VARIABLES */
.loading-state {
  text-align: center;
  padding: 80px;
  font-size: 1.3em;
  color: var(--text-secondary);
  font-weight: 600;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
}

/* Botón reintentar igual */
.btn-reintentar {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 20px;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.btn-reintentar::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-reintentar:hover::before {
  left: 100%;
}

.btn-reintentar:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5);
}

/* TABLA - CON VARIABLES */
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

/* BOTONES DE ACCIÓN - tamaño similar a Registrar Producto */
.action-buttons { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
}

.action-button {
  padding: 12px 16px;
  width: auto;
  height: 44px;
  font-size: 0.9rem;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  gap: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Editar */
.action-button.edit {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.action-button.edit:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* Eliminar */
.action-button.delete {
  background: var(--bg-tertiary);
  border: 1px solid var(--error-color);
  color: var(--error-color);
}
.action-button.delete:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  border-color: var(--error-color);
}

/* Éxito */
.action-button.success {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}
.action-button.success:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  border-color: #10b981;
}

/* Detalle de venta */
.action-button.detalle {
  background: var(--bg-tertiary);
  border: 1px solid #0ea5e9;
  color: #0ea5e9;
}
.action-button.detalle:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
  border-color: #0ea5e9;
}
/* BOTÓN DE COMPROBANTE PDF - CON VARIABLES */
.btn-comprobante {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 800;
  transition: all 0.3s ease;
  min-width: 90px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-comprobante:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.btn-comprobante:disabled {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  opacity: 0.5;
  border: 1px solid var(--border-color);
}

/* BADGES - CON VARIABLES */
.badge-pago, .badge-tipo, .badge-anulada {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.8px;
}

.badge-pago.efectivo {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
}

.badge-pago.tarjeta {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 8px rgba(14, 165, 233, 0.2);
}

.badge-pago.transferencia {
  background: var(--bg-tertiary);
  color: #8b5cf6;
  border: 2px solid #8b5cf6;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.2);
}

.badge-pago.mercadopago {
  background: var(--bg-tertiary);
  color: #00b2ff;
  border: 2px solid #00b2ff;
  box-shadow: 0 0 8px rgba(0, 178, 255, 0.2);
}

.badge-pago.default {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.badge-tipo.producto {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.2);
}

.badge-tipo.turno {
  background: var(--bg-tertiary);
  color: #ec4899;
  border: 2px solid #ec4899;
  box-shadow: 0 0 8px rgba(236, 72, 153, 0.2);
}

.badge-tipo.default {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.badge-anulada.anulada {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.2);
}

.badge-anulada:not(.anulada) {
  background: var(--bg-tertiary);
  color: var(--success-color);
  border: 2px solid var(--success-color);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
}

/* CONTADOR Y MENSAJES - CON VARIABLES */
.usuarios-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0;
  padding: 18px;
  background: var(--hover-bg);
  border-radius: 12px;
  flex-wrap: wrap;
  gap: 15px;
  border: 1px solid var(--border-color);
}

.usuarios-count p {
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.5px;
  margin: 0;
}

.venta-reciente {
  background: var(--bg-tertiary);
  color: var(--success-color);
  border: 2px solid var(--success-color);
  padding: 10px 18px;
  border-radius: 20px;
  margin-top: 0;
  animation: fadeIn 0.5s ease;
  font-weight: 800;
  letter-spacing: 0.8px;
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* PAGINACIÓN - CON VARIABLES */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
}

.pagination button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
}

.pagination button:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.pagination button:disabled {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  transform: none;
  border: 1px solid var(--border-color);
  opacity: 0.5;
}

.pagination span {
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 0.95rem;
}

/* OVERLAY Y MODALES - CON VARIABLES */
.overlay-activo {
  opacity: 0.3;
  filter: blur(5px);
  pointer-events: none;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.88);
  backdrop-filter: blur(12px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeInModal 0.3s ease;
}

@keyframes fadeInModal {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  position: relative;
  max-height: 88vh;
  max-width: 100vw;
  width: auto;
  overflow-y: auto;
  border-radius: 16px;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--border-color);
  padding: 0px;
  margin: 90px;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: var(--bg-tertiary);
  border: 2px solid var(--error-color);
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--error-color);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  z-index: 1001;
  font-weight: 900;
  font-size: 1.2rem;
}

.modal-close:hover {
  transform: scale(1.15) rotate(90deg);
  box-shadow: 0 6px 25px rgba(239, 68, 68, 0.6);
  background: var(--hover-bg);
  border-color: var(--error-color);
}

/* SCROLLBAR PERSONALIZADO - CON VARIABLES */
.modal-content::-webkit-scrollbar,
.table-container::-webkit-scrollbar {
  width: 2px;
  height: 12px;
}

.modal-content::-webkit-scrollbar-track,
.table-container::-webkit-scrollbar-track {
  background: var(--bg-primary);
  border-radius: 6px;
}

.modal-content::-webkit-scrollbar-thumb,
.table-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 6px;
  border: 2px solid var(--bg-primary);
}

.modal-content::-webkit-scrollbar-thumb:hover,
.table-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

/* RESPONSIVE (igual) */
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
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    max-width: 95vw;
    margin: 12px;
    border-radius: 12px;
  }
  
  .users-table {
    font-size: 0.85rem;
  }
  
  .users-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 6px;
  }
  
  .usuarios-count {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
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
  
  .users-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .btn-comprobante {
    min-width: 70px;
    padding: 8px 12px;
    font-size: 0.7rem;
  }
  
  .filter-input {
    font-size: 0.9rem;
  }
  
  .badge-pago, .badge-tipo, .badge-estado, .badge-anulada {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
}
</style>