<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Proveedores</h1>
          <p>Gestión de proveedores del sistema</p>
        </div>
        <div class="header-buttons">
          <button @click="mostrarRegistrar = true" class="register-button">
            <Plus :size="18" />
            Registrar Proveedor
          </button>
          <button @click="irAGestionPrecios" class="register-button secondary">
            <DollarSign :size="18" />
            Lista de Precios
          </button>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre, CUIT o teléfono..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Categoría</label>
            <select v-model="filtros.categoria" class="filter-input">
              <option value="">Todas las categorías</option>
              <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
                {{ categoria.nombre }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos</option>
              <option value="ACTIVO">Activo</option>
              <option value="INACTIVO">Inactivo</option>
            </select>
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
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              <Trash2 :size="16" />
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="proveedores-table">
          <thead>
            <tr>
              <th style="width: 50px;">#</th>
              <th>CUIT</th>
              <th>Nombre / Email</th>
              <th>Contacto</th>
              <th>Teléfono</th>
              <th>Categorías</th>
              <th class="text-center">Estado</th>
              <th class="text-center">Registro</th>
              <th class="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="proveedor in proveedoresPaginados" :key="proveedor.id">
              
              <td><span class="id-badge">#{{ proveedor.id }}</span></td>
              
              <td class="font-mono">{{ proveedor.cuit || '–' }}</td>
              
              <td>
                <div class="info-vertical">
                  <strong>{{ proveedor.nombre || '–' }}</strong>
                  <small class="text-muted">{{ proveedor.email }}</small>
                </div>
              </td>
              
              <td>{{ proveedor.contacto || '–' }}</td>
              
              <td>{{ proveedor.telefono || '–' }}</td>
              
              <td>
                <div v-if="proveedor.categorias_nombres && proveedor.categorias_nombres.length > 0" class="categorias-container">
                  <span v-for="(categoria, index) in getPrimerasCategorias(proveedor.categorias_nombres)" :key="index" 
                        class="categoria-badge">
                    {{ categoria }}
                  </span>
                  <div v-if="proveedor.categorias_nombres.length > 2" class="mas-categorias">
                    +{{ proveedor.categorias_nombres.length - 2 }}
                  </div>
                </div>
                <span v-else class="sin-categoria">–</span>
              </td>
              
              <td class="text-center">
                <span class="badge-estado" :class="getEstadoClass(proveedor.estado)">
                  {{ proveedor.estado === 'ACTIVO' ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              
              <td class="text-center">
                <div class="fecha-box">
                  <span class="fecha-dia">{{ formatFecha(proveedor.fecha_creacion).dia }}</span>
                  <span class="fecha-hora">{{ formatFecha(proveedor.fecha_creacion).hora }}</span>
                </div>
              </td>
              
              <td>
                <div class="action-buttons justify-end">
                  <button @click="editarProveedor(proveedor)" class="action-button edit" title="Editar proveedor">
                    <Edit3 :size="14" />
                  </button>
                  <button @click="verPreciosProveedor(proveedor)" class="action-button prices" title="Ver precios">
                    <DollarSign :size="14" />
                  </button>
                  <button @click="cambiarEstadoProveedor(proveedor)" class="action-button" 
                          :class="proveedor.estado === 'ACTIVO' ? 'delete' : 'success'" 
                          :title="proveedor.estado === 'ACTIVO' ? 'Desactivar proveedor' : 'Activar proveedor'">
                    <Power :size="14" v-if="proveedor.estado === 'ACTIVO'" />
                    <CheckCircle :size="14" v-else />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="proveedoresPaginados.length === 0" class="no-results">
          <Truck class="no-results-icon" :size="48" />
          <p>No se encontraron proveedores</p>
          <small>Intenta con otros términos de búsqueda</small>
        </div>
      </div>

      <div class="proveedores-count">
        <p>
          <Truck :size="16" />
          Mostrando {{ proveedoresPaginados.length }} de {{ proveedoresFiltrados.length }} proveedores
        </p>
        <div class="alertas-container">
          <span v-if="proveedoresInactivos > 0" class="alerta-inactivo">
            <PowerOff :size="14" />
            {{ proveedoresInactivos }} proveedores inactivos
          </span>
        </div>
      </div>

      <div class="pagination">
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

    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <RegistrarProveedor 
          @proveedor-registrado="proveedorRegistrado"
          @cancelar="cerrarModal"
        />
      </div>
    </div>

    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModalEditar" title="Cerrar formulario">
          <X :size="20" />
        </button>
        <ModificarProveedor 
          :proveedor-id="proveedorEditando?.id" 
          @proveedor-actualizado="proveedorActualizado"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import RegistrarProveedor from './RegistrarProveedor.vue'
import ModificarProveedor from './ModificarProveedor.vue'
import { 
  Truck, Plus, Edit3, Power, CheckCircle, PowerOff, DollarSign,
  ChevronLeft, ChevronRight, Trash2, X
} from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000'
const router = useRouter()

const proveedores = ref([])
const categorias = ref([])
const filtros = ref({ 
  busqueda: '', 
  categoria: '',
  estado: '', 
  fechaDesde: '', 
  fechaHasta: '' 
})

const pagina = ref(1)
const itemsPorPagina = 8
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const proveedorEditando = ref(null)

const cargarProveedores = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/proveedores/`)
    proveedores.value = res.data.sort((a, b) => {
      const fechaA = new Date(a.fecha_creacion || 0)
      const fechaB = new Date(b.fecha_creacion || 0)
      return fechaB - fechaA
    })
  } catch (err) {
    console.error('❌ Error al cargar proveedores:', err)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar la lista de proveedores',
      confirmButtonColor: '#0ea5e9'
    })
  }
}

const cargarCategorias = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/categorias/productos/`) 
    categorias.value = res.data.filter(c => c.activo)
  } catch (err) {
    console.error('Error al cargar categorías:', err)
  }
}

onMounted(async () => {
  await cargarProveedores()
  await cargarCategorias()
})

const irAGestionPrecios = () => router.push('/proveedores/listas-precios')
const verPreciosProveedor = (proveedor) => router.push(`/proveedores/listas-precios?proveedor_id=${proveedor.id}`)

const getPrimerasCategorias = (categorias) => {
  if (!categorias || categorias.length === 0) return []
  return categorias.slice(0, 2)
}

const getEstadoClass = (estado) => estado === 'ACTIVO' ? 'estado-success' : 'estado-danger'

// ✅ NUEVO FORMATO DE FECHA
const formatFecha = (fechaString) => {
  if (!fechaString) return { dia: '–', hora: '' }
  const fecha = new Date(fechaString)
  return {
    dia: fecha.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: '2-digit' }),
    hora: fecha.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
  }
}

const filtrarPorFecha = (proveedor) => {
  const fecha = proveedor.fecha_creacion ? new Date(proveedor.fecha_creacion) : null
  if (!fecha) return true
  if (filtros.value.fechaDesde && fecha < new Date(filtros.value.fechaDesde)) return false
  if (filtros.value.fechaHasta) {
    const hasta = new Date(filtros.value.fechaHasta)
    hasta.setDate(hasta.getDate() + 1)
    if (fecha >= hasta) return false
  }
  return true
}

const proveedoresFiltrados = computed(() => {
  const filtrados = proveedores.value.filter(p => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      (p.nombre?.toLowerCase().includes(busca) || 
       p.cuit?.includes(busca) ||  // Agregada búsqueda por CUIT
       p.telefono?.toLowerCase().includes(busca));
       
    const matchCategoria = !filtros.value.categoria || (p.categorias && p.categorias.includes(Number(filtros.value.categoria)));
    const matchEstado = !filtros.value.estado || p.estado === filtros.value.estado;
    const matchFecha = filtrarPorFecha(p);
    
    return matchBusqueda && matchCategoria && matchEstado && matchFecha
  })
  
  return filtrados.sort((a, b) => {
    if (a.estado === b.estado) return 0
    return a.estado === 'ACTIVO' ? -1 : 1
  })
})

const proveedoresInactivos = computed(() => proveedoresFiltrados.value.filter(p => p.estado === 'INACTIVO').length)
const totalPaginas = computed(() => Math.max(1, Math.ceil(proveedoresFiltrados.value.length / itemsPorPagina)))

const proveedoresPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return proveedoresFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

const editarProveedor = (proveedor) => {
  proveedorEditando.value = proveedor
  mostrarEditar.value = true
}

const cambiarEstadoProveedor = async (proveedor) => {
  const nuevoEstado = proveedor.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'
  const accion = nuevoEstado === 'ACTIVO' ? 'activar' : 'desactivar'
  
  const result = await Swal.fire({
    title: `¿${accion.charAt(0).toUpperCase() + accion.slice(1)} proveedor?`,
    text: `¿Está seguro de ${accion} el proveedor "${proveedor.nombre}"?`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#0ea5e9',
    cancelButtonColor: '#6b7280',
    confirmButtonText: `Sí, ${accion}`,
    cancelButtonText: 'Cancelar'
  })
  
  if (!result.isConfirmed) return
  
  try {
    await axios.patch(`${API_BASE}/api/proveedores/${proveedor.id}/`, {
      estado: nuevoEstado
    })
    await cargarProveedores()
    Swal.fire({
      icon: 'success',
      title: '¡Éxito!',
      text: `Proveedor ${accion}do correctamente`,
      confirmButtonColor: '#0ea5e9'
    })
  } catch (err) { 
    console.error(err)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: `No se pudo ${accion} el proveedor`,
      confirmButtonColor: '#0ea5e9'
    })
  }
}

const proveedorActualizado = async () => { await cargarProveedores(); cerrarModalEditar() }
const proveedorRegistrado = async () => { await cargarProveedores(); cerrarModal(); pagina.value = 1 }
const limpiarFiltros = () => { filtros.value = { busqueda: '', categoria: '', estado: '', fechaDesde: '', fechaHasta: '' }; pagina.value = 1 }
const cerrarModal = () => { mostrarRegistrar.value = false }
const cerrarModalEditar = () => { mostrarEditar.value = false; proveedorEditando.value = null }

watch(filtros, () => { pagina.value = 1 }, { deep: true })
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - PROVEEDORES
   ======================================== */

.list-container { padding: 32px; max-width: 1600px; margin: 0 auto; min-height: 100vh; font-family: 'Inter', sans-serif; }
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); border-radius: 24px 24px 0 0; }

/* HEADER */
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; flex-wrap: wrap; gap: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; letter-spacing: 0.5px; }

/* Botones */
.header-buttons { display: flex; gap: 12px; align-items: center; }
.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; font-size: 0.95rem; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); position: relative; overflow: hidden; display: flex; align-items: center; gap: 8px; }
.register-button.secondary { background: linear-gradient(135deg, #059669, #047857); box-shadow: 0 6px 20px rgba(5, 150, 105, 0.35); }
.register-button:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); background: linear-gradient(135deg, #0284c7, #0369a1); }
.register-button.secondary:hover { box-shadow: 0 10px 30px rgba(5, 150, 105, 0.5); background: linear-gradient(135deg, #047857, #065f46); }

/* FILTROS */
.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; align-items: end; }
.filter-group { display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }
.filter-input { padding: 12px 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); transition: all 0.3s ease; font-weight: 500; font-size: 0.95rem; height: 44px; box-sizing: border-box; width: 100%; }
.filter-input:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); background: var(--bg-secondary); }
.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 18px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: all 0.3s ease; text-transform: uppercase; font-size: 0.85rem; height: 44px; display: flex; align-items: center; gap: 6px; width: 100%; justify-content: center; }
.clear-filters-btn:hover { background: var(--hover-bg); transform: translateY(-2px); }

/* TABLA - ESTILO SOLICITADO */
.table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; border: 1px solid var(--border-color); }
.proveedores-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); min-width: 1200px; }
.proveedores-table th { background: var(--accent-color); color: white; padding: 18px 14px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px; white-space: nowrap; }
.proveedores-table tr { border-bottom: 1px solid var(--border-color); }
.proveedores-table td { padding: 14px; vertical-align: middle; color: var(--text-secondary); font-weight: 500; white-space: nowrap; }
.proveedores-table tr:hover { background: var(--hover-bg); }

/* Elementos de la tabla */
.info-vertical { display: flex; flex-direction: column; }
.text-muted { color: #8f9ea4 !important; }
.id-badge { background: var(--bg-tertiary); color: var(--text-tertiary); padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
.font-mono { font-family: monospace; font-size: 0.95rem; letter-spacing: 0.5px; color: var(--text-primary); }

/* Fecha Vertical */
.fecha-box { display: flex; flex-direction: column; align-items: center; }
.fecha-dia { font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }
.fecha-hora { font-size: 0.8rem; color: var(--text-tertiary); }

/* Badges y Categorías */
.badge-estado { padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; white-space: nowrap; }
.estado-success { background: var(--bg-tertiary); color: #10b981; border: 2px solid #10b981; }
.estado-danger { background: var(--bg-tertiary); color: var(--error-color); border: 2px solid var(--error-color); }

.categorias-container { display: flex; flex-direction: column; gap: 6px; max-width: 200px; }
.categoria-badge { background: var(--bg-tertiary); color: #0ea5e9; border: 2px solid #0ea5e9; padding: 4px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; text-align: center; }
.mas-categorias { color: var(--text-tertiary); font-size: 0.75rem; font-style: italic; text-align: center; background: var(--hover-bg); border-radius: 8px; padding: 2px; }
.sin-categoria { color: var(--text-tertiary); font-style: italic; }

/* Utilidades */
.text-center { text-align: center; }
.text-right { text-align: right; }
.justify-end { justify-content: flex-end; }

/* Botones de acción */
.action-buttons { display: flex; gap: 6px; flex-wrap: nowrap; }
.action-button { padding: 8px; border: none; border-radius: 10px; width: 40px; height: 40px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; }
.action-button.edit { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); }
.action-button.edit:hover { background: var(--hover-bg); transform: translateY(-2px); }
.action-button.prices { background: var(--bg-tertiary); border: 1px solid #059669; color: #059669; }
.action-button.prices:hover { background: var(--hover-bg); transform: translateY(-2px); }
.action-button.delete { background: var(--bg-tertiary); border: 1px solid var(--error-color); color: var(--error-color); }
.action-button.delete:hover { background: var(--hover-bg); transform: translateY(-2px); }
.action-button.success { background: var(--bg-tertiary); border: 1px solid #10b981; color: #10b981; }
.action-button.success:hover { background: var(--hover-bg); transform: translateY(-2px); }

/* Paginación y Contadores */
.proveedores-count { display: flex; justify-content: space-between; align-items: center; margin: 25px 0; padding: 18px; background: var(--hover-bg); border-radius: 12px; border: 1px solid var(--border-color); }
.proveedores-count p { color: var(--text-secondary); font-weight: 600; margin: 0; display: flex; align-items: center; gap: 8px; }
.alerta-inactivo { background: var(--bg-tertiary); color: #ef4444; border: 2px solid #ef4444; padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 25px; }
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 800; display: flex; align-items: center; gap: 8px; }
.pagination button:hover:not(:disabled) { background: var(--hover-bg); }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination span { color: var(--text-primary); font-weight: 700; }

/* Loading State */
.no-results { text-align: center; padding: 80px; color: var(--text-secondary); }
.no-results-icon { margin-bottom: 15px; opacity: 0.5; color: var(--text-tertiary); }
.no-results p { font-size: 1.1em; color: var(--text-primary); }
.animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Modales */
.overlay-activo { opacity: 0.3; filter: blur(5px); pointer-events: none; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.88); backdrop-filter: blur(12px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeInModal 0.3s ease; }
@keyframes fadeInModal { from { opacity: 0; } to { opacity: 1; } }
.modal-content { position: relative; animation: slideUp 0.3s ease; max-height: 85vh; width: auto; overflow-y: auto; border-radius: 16px; background: var(--bg-secondary); box-shadow: var(--shadow-lg); border: 2px solid var(--border-color); padding: 0; margin: 20px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
.modal-close { position: absolute; top: 15px; right: 15px; background: var(--bg-tertiary); border: 2px solid var(--error-color); border-radius: 12px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--error-color); z-index: 1001; transition: all 0.3s ease; }
.modal-close:hover { transform: scale(1.15) rotate(90deg); background: var(--hover-bg); }

@media (max-width: 768px) {
  .list-header, .proveedores-count { flex-direction: column; gap: 20px; align-items: flex-start; }
  .header-buttons, .alertas-container { width: 100%; flex-direction: column; }
  .register-button { width: 100%; justify-content: center; }
  .filters-grid { grid-template-columns: 1fr; }
}
</style>