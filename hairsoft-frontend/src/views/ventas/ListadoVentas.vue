<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de ventas</h1>
          <p>Historial y administración de transacciones</p>
        </div>
        <button @click="mostrarRegistrar = true" class="register-button">
          <Plus :size="18" />
          Registrar Venta
        </button>
      </div>

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

          <div class="filter-group">
            <label>Método Pago</label>
            <select v-model="filtros.metodoPago" class="filter-input">
              <option value="">Todos</option>
              <option value="EFECTIVO">Efectivo</option>
              <option value="TARJETA">Tarjeta</option>
              <option value="TRANSFERENCIA">Transferencia</option>
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

      <div v-if="cargando" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Cargando ventas...</p>
      </div>

      <div v-else class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th style="width: 140px;">Fecha</th>
              <th>Cliente</th>
              <th>Usuario</th>
              <th style="width: 80px;">ID</th>
              <th>Total</th>
              <th>Método Pago</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th style="width: 60px; text-align: center;">PDF</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="venta in ventasPaginadas" :key="venta.id" 
                :class="{'venta-anulada-row': venta.anulada}">
              
              <td class="fecha-cell">
                <span class="fecha-dia">{{ formatFechaDia(venta.fecha) }}</span>
                <span class="fecha-hora">{{ formatFechaHora(venta.fecha) }}</span>
              </td>

              <td><strong>{{ venta.cliente_nombre || 'Venta Rápida' }}</strong></td>
              
              <td class="usuario-cell">{{ venta.usuario_nombre || '–' }}</td>
              
              <td class="id-cell">#{{ venta.id }}</td>
              
              <td class="total-cell">${{ formatPrecio(venta.total) }}</td>
              
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
                  {{ venta.anulada ? 'ANULADA' : 'ACTIVA' }}
                </span>
              </td>
              
              <td style="text-align: center;">
                <button 
                  @click="generarComprobantePDF(venta)" 
                  class="btn-pdf-icon"
                  :title="`Descargar comprobante #${venta.id}`"
                  :disabled="generandoPDF === venta.id || venta.anulada"
                >
                  <Loader v-if="generandoPDF === venta.id" :size="18" class="spin" />
                  <FileText v-else :size="18" />
                </button>
              </td>

              <td>
                <div class="action-buttons">
                  <button 
                    @click="editarVenta(venta)" 
                    class="action-button edit" 
                    :disabled="venta.anulada"
                    title="Editar"
                  >
                    <Edit3 :size="14" />
                  </button>
                  <button 
                    @click="anularVenta(venta)" 
                    class="action-button delete" 
                    :disabled="venta.anulada"
                    title="Anular"
                  >
                    <Trash2 :size="14" />
                  </button>
                  <button 
                    @click="verDetallesVenta(venta.id)" 
                    class="action-button detalle"
                    title="Ver Detalle"
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
          <button @click="cargarVentas" class="btn-reintentar">
            <RefreshCw :size="16" />
            Recargar
          </button>
        </div>
      </div>

      <div v-if="!cargando" class="list-footer">
        <div class="footer-left">
          <p class="count-text">
            Mostrando <strong>{{ ventasPaginadas.length }}</strong> de <strong>{{ ventasFiltradas.length }}</strong> ventas
          </p>
          
          <div class="alertas-container">
            <span v-if="ventasAnuladas > 0" class="alerta-bad">
              <AlertTriangle :size="14" />
              {{ ventasAnuladas }} anuladas
            </span>
            <span v-if="ventaRecienCreada" class="alerta-good">
              <CheckCircle :size="14" />
              Nueva venta (#{{ ventaRecienCreada }})
            </span>
          </div>
        </div>

        <div v-if="totalPaginas > 1" class="pagination">
          <button @click="paginaAnterior" :disabled="pagina === 1" class="page-btn">
            <ChevronLeft :size="18" />
          </button>
          <span class="page-info">Página {{ pagina }} de {{ totalPaginas }}</span>
          <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="page-btn">
            <ChevronRight :size="18" />
          </button>
        </div>
      </div>
    </div>

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
import axios from '@/utils/axiosConfig' 
import Swal from 'sweetalert2'
import RegistrarVenta from './RegistrarVenta.vue'
import ModificarVenta from './ModificarVenta.vue'
import { 
  Plus, Trash2, Edit3, Eye, FileText, Loader, Package, PackageX,
  ChevronLeft, ChevronRight, RefreshCw, AlertTriangle, CheckCircle
} from 'lucide-vue-next'

const router = useRouter()
const ventas = ref([])
const filtros = ref({ busqueda: '', fechaDesde: '', fechaHasta: '', metodoPago: '', tipo: '', estado: '' })
const pagina = ref(1)
const itemsPorPagina = 8
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const ventaEditando = ref(null)
const cargando = ref(false)
const generandoPDF = ref(null)
const ventaRecienCreada = ref(null)

const cargarVentas = async () => {
  cargando.value = true
  try {
    const res = await axios.get('/api/ventas/')
    const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
    if (data.length > 0) {
      ventas.value = data.sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
    } else {
      ventas.value = []
    }
  } catch (err) {
    console.error('❌ Error cargando ventas:', err)
  } finally {
    cargando.value = false
  }
}

onMounted(() => cargarVentas())

const ventasFiltradas = computed(() => {
  const busca = filtros.value.busqueda.toLowerCase()
  return ventas.value.filter(v => {
    const matchBusqueda = !busca || 
      (v.cliente_nombre?.toLowerCase() || '').includes(busca) || 
      (v.id || '').toString().includes(busca)
    
    const fecha = v.fecha ? new Date(v.fecha) : null
    const matchDesde = !filtros.value.fechaDesde || (fecha && fecha >= new Date(filtros.value.fechaDesde))
    const matchHasta = !filtros.value.fechaHasta || (fecha && fecha <= new Date(filtros.value.fechaHasta + 'T23:59:59'))
    const matchMetodo = !filtros.value.metodoPago || v.medio_pago_tipo === filtros.value.metodoPago
    const matchTipo = !filtros.value.tipo || v.tipo === filtros.value.tipo
    const matchEstado = !filtros.value.estado || 
        (filtros.value.estado === 'activa' && !v.anulada) || 
        (filtros.value.estado === 'anulada' && v.anulada)

    return matchBusqueda && matchDesde && matchHasta && matchMetodo && matchTipo && matchEstado
  })
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(ventasFiltradas.value.length / itemsPorPagina)))
const ventasPaginadas = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return ventasFiltradas.value.slice(inicio, inicio + itemsPorPagina)
})
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }
const ventasAnuladas = computed(() => ventasFiltradas.value.filter(v => v.anulada).length)

const editarVenta = (venta) => { if (venta.anulada) return; ventaEditando.value = venta; mostrarEditar.value = true }
const verDetallesVenta = (id) => router.push({ name: 'DetalleVenta', params: { id } })

const anularVenta = async (venta) => {
  const res = await Swal.fire({ title: '¿Anular venta?', text: "Esta acción no se puede deshacer", icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33', cancelButtonColor: '#3085d6', confirmButtonText: 'Sí, anular' })
  if (!res.isConfirmed) return
  
  try {
    await axios.post(`/api/ventas/${venta.id}/anular/`)
    await cargarVentas()
    Swal.fire('Anulada', 'La venta ha sido anulada.', 'success')
  } catch (err) { Swal.fire('Error', 'No se pudo anular', 'error') }
}

const generarComprobantePDF = (venta) => {
  generandoPDF.value = venta.id
  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
  setTimeout(() => {
      window.open(`${baseUrl}/api/ventas/${venta.id}/comprobante-pdf/`, '_blank')
      generandoPDF.value = null
  }, 500)
}

const cerrarModal = () => { mostrarRegistrar.value = false }
const cerrarModalEditar = () => { mostrarEditar.value = false; ventaEditando.value = null }
const procesarVentaRegistrada = async (venta) => { 
  await cargarVentas(); 
  ventaRecienCreada.value = venta.id 
  setTimeout(() => ventaRecienCreada.value = null, 5000) 
}
const ventaActualizada = async () => { await cargarVentas(); cerrarModalEditar() }
const limpiarFiltros = () => { filtros.value = { busqueda: '', fechaDesde: '', fechaHasta: '', metodoPago: '', tipo: '', estado: '' }; pagina.value = 1 }

// UTILS
const formatFechaDia = (f) => f ? new Date(f).toLocaleDateString('es-AR', {day: '2-digit', month: '2-digit', year: 'numeric'}) : '-'
const formatFechaHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : ''
const formatPrecio = (p) => p ? parseFloat(p).toLocaleString('es-AR', { minimumFractionDigits: 2 }) : '0.00'

const getClaseTipoPago = (t) => { if (t === 'EFECTIVO') return 'pago-efectivo'; if (t === 'TARJETA') return 'pago-tarjeta'; return 'pago-otro' }
const getClaseTipoVenta = (t) => t === 'TURNO' ? 'tipo-turno' : 'tipo-prod'
const getClaseEstadoVenta = (anulada) => anulada ? 'estado-anulada' : 'estado-activa'
</script>

<style scoped>
/* ESTILOS PREMIUM */
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1); border-radius: 24px 24px 0 0; }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; letter-spacing: 0.5px; }

.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; font-size: 0.95rem; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); display: flex; align-items: center; gap: 8px; }
.register-button:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); }

/* FILTROS */
.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; align-items: end; }
.filter-group { display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }
.filter-input { padding: 12px 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-weight: 500; font-size: 0.95rem; }
.filter-input:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); }
.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 18px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: 0.3s; text-transform: uppercase; font-size: 0.85rem; display: flex; align-items: center; gap: 6px; }
.clear-filters-btn:hover { background: var(--hover-bg); transform: translateY(-2px); }

/* TABLA */
.table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow-md); border: 1px solid var(--border-color); }
.users-table th { background: var(--accent-color); color: white; padding: 18px 14px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px; white-space: nowrap; }
.users-table tr { border-bottom: 1px solid var(--border-color); }
.users-table td { padding: 14px; vertical-align: middle; color: var(--text-secondary); font-weight: 500; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
.users-table tr:hover { background: var(--hover-bg); transition: 0.2s; }

/* CELDAS PERSONALIZADAS */
.fecha-cell { display: flex; flex-direction: column; }
.fecha-dia { font-weight: 700; color: var(--text-primary); }
.fecha-hora { font-size: 0.75rem; color: var(--text-tertiary); }

/* ✨ CORRECCIÓN DE COLOR PARA USUARIO E ID */
.usuario-cell { color: #e2e8f0; font-weight: 500; } /* Blanco suave / Gris claro */
.id-cell { font-family: monospace; color: #94a3b8; font-size: 0.85rem; font-weight: 600; } /* Gris medio legible */

.total-cell { font-size: 1rem; font-weight: 800; color: #10b981; }
.text-muted { color: var(--text-tertiary); font-size: 0.85rem; }

/* BADGES */
.badge-pago, .badge-tipo, .badge-estado { padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; border: 1px solid transparent; }
.pago-efectivo { background: rgba(16, 185, 129, 0.1); color: #10b981; border-color: #10b981; }
.pago-tarjeta { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border-color: #0ea5e9; }
.pago-otro { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; border-color: #8b5cf6; }
.tipo-turno { background: rgba(236, 72, 153, 0.1); color: #ec4899; border-color: #ec4899; }
.tipo-prod { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border-color: #f59e0b; }
.estado-activa { color: #10b981; background: rgba(16, 185, 129, 0.05); }
.estado-anulada { color: #ef4444; background: rgba(239, 68, 68, 0.05); text-decoration: line-through; }
.venta-anulada-row { opacity: 0.6; background: rgba(239, 68, 68, 0.02); }

/* BOTÓN PDF ICONO */
.btn-pdf-icon { background: transparent; border: 1px solid var(--border-color); color: var(--text-secondary); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; margin: 0 auto; }
.btn-pdf-icon:hover:not(:disabled) { background: #0ea5e9; color: white; border-color: #0ea5e9; transform: translateY(-2px); }
.btn-pdf-icon:disabled { opacity: 0.3; cursor: not-allowed; }
.spin { animation: spin 1s linear infinite; } @keyframes spin { to { transform: rotate(360deg); } }

/* ACCIONES */
.action-buttons { display: flex; gap: 6px; }
.action-button { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; border: 1px solid transparent; transition: 0.2s; background: var(--bg-tertiary); color: var(--text-secondary); }
.action-button:hover:not(:disabled) { transform: translateY(-2px); }
.action-button.edit:hover { color: #3b82f6; border-color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
.action-button.delete:hover { color: #ef4444; border-color: #ef4444; background: rgba(239, 68, 68, 0.1); }
.action-button.detalle:hover { color: #10b981; border-color: #10b981; background: rgba(16, 185, 129, 0.1); }
.action-button:disabled { opacity: 0.3; cursor: not-allowed; }

/* FOOTER */
.list-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 15px; background: var(--hover-bg); border-radius: 12px; flex-wrap: wrap; gap: 15px; }
.footer-left { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.count-text { color: var(--text-secondary); font-size: 0.9rem; margin: 0; }

.alertas-container { display: flex; gap: 10px; }
.alerta-bad, .alerta-good { padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: flex; align-items: center; gap: 6px; text-transform: uppercase; }
.alerta-bad { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; }
.alerta-good { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981; animation: fadeIn 0.5s ease; }

.pagination { display: flex; gap: 10px; align-items: center; }
.page-btn { background: var(--bg-tertiary); border: 1px solid var(--border-color); width: 36px; height: 36px; border-radius: 8px; cursor: pointer; color: var(--text-primary); display: flex; justify-content: center; align-items: center; transition: 0.2s; }
.page-btn:hover:not(:disabled) { background: var(--accent-color); color: white; border-color: var(--accent-color); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }

/* ESTADOS CARGA */
.loading-state { text-align: center; padding: 80px; color: var(--text-tertiary); font-weight: 600; }
.loading-spinner { width: 40px; height: 40px; border: 3px solid var(--border-color); border-top-color: var(--accent-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px; }
.no-results { text-align: center; padding: 60px; color: var(--text-tertiary); }
.btn-reintentar { margin-top: 15px; padding: 10px 20px; background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; color: var(--text-primary); display: flex; align-items: center; gap: 8px; justify-content: center; margin: 20px auto 0; font-weight: 700; transition: 0.3s; }
.btn-reintentar:hover { background: var(--hover-bg); transform: translateY(-2px); }

/* MODAL */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); z-index: 1000; display: flex; justify-content: center; align-items: center; }
.modal-content { background: var(--bg-secondary); padding: 0; border-radius: 16px; border: 1px solid var(--border-color); max-height: 90vh; overflow-y: auto; }

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-footer { flex-direction: column; align-items: flex-start; }
  .footer-left { flex-direction: column; align-items: flex-start; gap: 10px; }
  .pagination { width: 100%; justify-content: space-between; }
}
</style>