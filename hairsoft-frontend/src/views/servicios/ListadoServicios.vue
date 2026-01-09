  <template>
    <div class="list-container">
      <div class="list-card">
        
        <div class="list-header">
          <div class="header-content">
            <h1>Gestión de servicios</h1>
            <p>Administra el catálogo de servicios de la peluquería</p>
          </div>
          <button @click="irARegistrar" class="register-button">
            <Plus :size="18" />
            Registrar Servicio
          </button>
        </div>

        <div class="filters-container">
          <div class="filters-grid">
            
            <div class="filter-group">
              <label>Buscar</label>
              <div class="input-with-icon">
                <Search :size="16" class="input-icon" />
                <input 
                  v-model="filtroBusqueda" 
                  type="text" 
                  placeholder="Nombre del servicio..." 
                  class="filter-input" 
                />
              </div>
            </div>

            <div class="filter-group">
              <label>Categoría</label>
              <select v-model="filtroCategoria" class="filter-input">
                <option value="">Todas las categorías</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.nombre">
                  {{ cat.nombre }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>Estado</label>
              <select v-model="filtroEstado" class="filter-input">
                <option value="todos">Todos</option>
                <option value="activos">Solo Activos</option>
                <option value="inactivos">Solo Inactivos</option>
              </select>
            </div>

            <div class="filter-group">
              <label>&nbsp;</label>
              <button @click="limpiarFiltros" class="clear-filters-btn">
                <Trash2 :size="14" /> Limpiar
              </button>
            </div>
          </div>
        </div>

        <div class="table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Precio</th>
                <th>Duración</th>
                <th>Comisión</th> <th>Categoría</th>
                <th>Estado</th> <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in serviciosPaginados" :key="s.id" :class="{ 'row-inactive': !s.activo }">
                <td>
                  <strong :class="{ 'text-crossed': !s.activo }">{{ s.nombre }}</strong>
                </td>
                <td class="price-cell">${{ Number(s.precio).toLocaleString() }}</td>
                <td>
                  <span class="duration-badge">
                    <Clock :size="12" /> {{ s.duracion || 20 }} min
                  </span>
                </td>
                <td>
                  <span class="duration-badge" style="color: #6f42c1; background: rgba(111, 66, 193, 0.1);">
                    {{ s.porcentaje_comision || 0 }}%
                  </span>
                </td>
                <td>
                  <span class="category-badge">{{ s.categoria_nombre || s.categoria || 'General' }}</span>
                </td>
                
                <td>
                  <span :class="['status-badge', s.activo ? 'status-active' : 'status-inactive']">
                    {{ s.activo ? 'ACTIVO' : 'INACTIVO' }}
                  </span>
                </td>

                <td>
                  <div class="action-buttons">
                    <button @click="verDetalle(s)" class="action-button info" title="Ver Detalle">
                      <Eye :size="16" />
                    </button>
                    
                    <button @click="editarServicio(s)" class="action-button edit" title="Editar">
                      <Edit3 :size="16" />
                    </button>
                    
                    <button 
                      @click="cambiarEstado(s)" 
                      class="action-button"
                      :class="s.activo ? 'delete' : 'activate'"
                      :title="s.activo ? 'Desactivar Servicio' : 'Reactivar Servicio'"
                    >
                      <Trash2 v-if="s.activo" :size="16" />
                      <RefreshCw v-else :size="16" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="serviciosPaginados.length === 0" class="no-results">
            <div class="icon-box">
              <SearchX :size="48" />
            </div>
            <p>No se encontraron servicios</p>
            <button @click="limpiarFiltros" class="btn-link">Limpiar filtros</button>
          </div>
        </div>

        <div class="pagination" v-if="totalPaginas > 1">
          <button @click="paginaAnterior" :disabled="pagina === 1" class="pagination-btn">
            <ChevronLeft :size="18" />
          </button>
          <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
          <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="pagination-btn">
            <ChevronRight :size="18" />
          </button>
        </div>
      </div>

      <div v-if="mostrarModalDetalle" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>{{ servicioSeleccionado?.nombre }}</h3>
            <button class="close-btn" @click="cerrarModal">
              <X :size="20" />
            </button>
          </div>
          
          <div class="modal-body">
            <div class="detail-grid">
              <div class="detail-item">
                <span class="label">Precio</span>
                <span class="value price">${{ Number(servicioSeleccionado?.precio).toLocaleString() }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Duración</span>
                <span class="value">{{ servicioSeleccionado?.duracion }} min</span>
              </div>
              <div class="detail-item">
                <span class="label">Comisión</span>
                <span class="value">{{ servicioSeleccionado?.porcentaje_comision || 0 }}%</span>
              </div>
              <div class="detail-item">
                <span class="label">Estado</span>
                <span :class="['value', servicioSeleccionado?.activo ? 'text-green' : 'text-red']">
                  {{ servicioSeleccionado?.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </div>
            </div>
            
            <div class="description-section">
              <span class="label">Descripción</span>
              <div class="description-box">
                {{ servicioSeleccionado?.descripcion || 'Sin descripción detallada.' }}
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="editarServicio(servicioSeleccionado)" class="btn-editar-modal">
              <Edit3 :size="16" /> Editar
            </button>
            <button @click="cerrarModal" class="btn-cerrar-modal">Cerrar</button>
          </div>
        </div>
      </div>

    </div>
  </template>

  <script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from '@/utils/axiosConfig'
  import Swal from 'sweetalert2'
  import { 
    Plus, Search, Trash2, Eye, Edit3, Clock, ChevronLeft, ChevronRight, X, SearchX, RefreshCw
  } from 'lucide-vue-next'

  const router = useRouter()

  const servicios = ref([])
  const categorias = ref([])
  const filtroBusqueda = ref('')
  const filtroCategoria = ref('')
  const filtroEstado = ref('todos')

  const mostrarModalDetalle = ref(false)
  const servicioSeleccionado = ref(null)

  const pagina = ref(1)
  const itemsPorPagina = 8

  const cargarDatos = async () => {
    try {
      const [resServicios, resCategorias] = await Promise.all([
        axios.get('/usuarios/api/servicios/'),
        axios.get('/usuarios/api/categorias/servicios/')
      ])
      servicios.value = resServicios.data
      categorias.value = resCategorias.data
    } catch (err) {
      console.error('Error:', err)
      Swal.fire('Error', 'No se pudieron cargar los datos', 'error')
    }
  }

  const serviciosFiltrados = computed(() => {
    return servicios.value.filter(s => {
      const matchNombre = !filtroBusqueda.value || 
        s.nombre.toLowerCase().includes(filtroBusqueda.value.toLowerCase())
      
      const catNombre = s.categoria_nombre || s.categoria || ''
      const matchCategoria = !filtroCategoria.value || 
        catNombre === filtroCategoria.value

      let matchEstado = true
      if (filtroEstado.value === 'activos') matchEstado = s.activo === true
      if (filtroEstado.value === 'inactivos') matchEstado = s.activo === false

      return matchNombre && matchCategoria && matchEstado
    })
  })

  const totalPaginas = computed(() => Math.ceil(serviciosFiltrados.value.length / itemsPorPagina))
  const serviciosPaginados = computed(() => {
    const inicio = (pagina.value - 1) * itemsPorPagina
    return serviciosFiltrados.value.slice(inicio, inicio + itemsPorPagina)
  })

  const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
  const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

  const limpiarFiltros = () => {
    filtroBusqueda.value = ''
    filtroCategoria.value = ''
    filtroEstado.value = 'activos'
    pagina.value = 1
  }

  const irARegistrar = () => router.push('/servicios/crear')
  const editarServicio = (s) => router.push(`/servicios/modificar/${s.id}`)

  const cambiarEstado = async (servicio) => {
    const accion = servicio.activo ? 'desactivar' : 'activar'
    const colorBtn = servicio.activo ? '#ef4444' : '#10b981'
    
    const result = await Swal.fire({
      title: `¿${accion.charAt(0).toUpperCase() + accion.slice(1)} servicio?`,
      text: servicio.activo 
        ? "Dejará de aparecer en las opciones de turnos." 
        : "Volverá a estar disponible para turnos.",
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: colorBtn,
      cancelButtonColor: '#334155',
      confirmButtonText: `Sí, ${accion}`,
      cancelButtonText: 'Cancelar',
      background: '#1e293b',
      color: '#fff'
    })

    if (result.isConfirmed) {
      try {
        await axios.post(`/usuarios/api/servicios/${servicio.id}/cambiar-estado/`)
        servicio.activo = !servicio.activo
        Swal.fire({
          title: '¡Listo!',
          text: `El servicio ha sido ${servicio.activo ? 'activado' : 'desactivado'}.`,
          icon: 'success',
          timer: 1500,
          showConfirmButton: false,
          background: '#1e293b',
          color: '#fff'
        })
      } catch (err) {
        console.error(err)
        Swal.fire({ title: 'Error', text: 'No se pudo cambiar el estado.', icon: 'error' })
      }
    }
  }

  const verDetalle = (servicio) => {
    servicioSeleccionado.value = servicio
    mostrarModalDetalle.value = true
  }
  const cerrarModal = () => {
    mostrarModalDetalle.value = false
    servicioSeleccionado.value = null
  }

  onMounted(() => cargarDatos())
  watch([filtroBusqueda, filtroCategoria, filtroEstado], () => { pagina.value = 1 })
  </script>

  <style scoped>
  /* ESTILOS EXACTOS TUYOS (SIN CAMBIOS) */
  .list-container { padding: 30px; max-width: 1400px; margin: 0 auto; font-family: 'Segoe UI', sans-serif; }
  .list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; border: 1px solid var(--border-color); }
  .list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1); }
  .list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
  .header-content h1 { margin: 0; font-size: 2.2rem; font-weight: 900; letter-spacing: 1px; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .header-content p { color: var(--text-secondary); margin-top: 5px; font-weight: 500; }
  .register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 700; cursor: pointer; transition: 0.3s; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3); }
  .register-button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5); }
  .filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); }
  .filters-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 0.5fr; gap: 20px; align-items: end; }
  .filter-group label { display: block; font-weight: 700; margin-bottom: 8px; color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; }
  .input-with-icon { position: relative; }
  .input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); }
  .filter-input { width: 100%; padding: 12px 14px 12px 42px; border-radius: 10px; background: var(--bg-primary); border: 2px solid var(--border-color); color: var(--text-primary); transition: 0.3s; box-sizing: border-box; }
  select.filter-input { padding-left: 14px; background-color: #1e293b; }
  .filter-input:focus { border-color: #0ea5e9; box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1); outline: none; }
  .clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px; border-radius: 10px; cursor: pointer; width: 100%; font-weight: 600; display: flex; justify-content: center; gap: 6px; align-items: center; transition: 0.3s; }
  .clear-filters-btn:hover { background: var(--hover-bg); color: #ef4444; border-color: #ef4444; }
  .table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; }
  .users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; border: 1px solid var(--border-color); }
  .users-table th { background: var(--accent-color); color: white; padding: 18px; text-align: left; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
  .users-table td { padding: 16px 18px; color: var(--text-secondary); border-bottom: 1px solid var(--border-color); }
  .users-table tr:hover { background: var(--hover-bg); transition: 0.2s; }
  .row-inactive { background: rgba(255, 255, 255, 0.02); opacity: 0.7; }
  .text-crossed { text-decoration: line-through; color: var(--text-tertiary); }
  .price-cell { color: #10b981; font-weight: 800; font-size: 1rem; }
  .duration-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(14, 165, 233, 0.1); color: #0ea5e9; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
  .category-badge { background: var(--bg-tertiary); border: 1px solid var(--border-color); padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
  .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; }
  .status-active { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981; }
  .status-inactive { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; }
  .action-buttons { display: flex; gap: 8px; }
  .action-button { width: 36px; height: 36px; border-radius: 8px; border: 1px solid transparent; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; background: var(--bg-tertiary); color: var(--text-secondary); }
  .action-button:hover { transform: translateY(-2px); }
  .action-button.info:hover { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border-color: #0ea5e9; }
  .action-button.edit:hover { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border-color: #f59e0b; }
  .action-button.delete:hover { background: rgba(239, 68, 68, 0.1); color: #ef4444; border-color: #ef4444; }
  .action-button.activate { color: #10b981; border-color: #10b981; }
  .action-button.activate:hover { background: rgba(16, 185, 129, 0.1); color: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }
  .no-results { text-align: center; padding: 60px; color: var(--text-tertiary); }
  .icon-box { margin-bottom: 10px; opacity: 0.5; }
  .btn-link { background: none; border: none; color: #0ea5e9; cursor: pointer; text-decoration: underline; font-weight: 600; margin-top: 10px; }
  .pagination { display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 30px; }
  .pagination-btn { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; }
  .pagination-btn:hover:not(:disabled) { background: #0ea5e9; color: white; border-color: #0ea5e9; }
  .pagination-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .pagination-info { font-weight: 700; color: var(--text-secondary); }
  .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); z-index: 2000; display: flex; justify-content: center; align-items: center; }
  .modal-content { background: #1e293b; color: #f1f5f9; width: 90%; max-width: 500px; border-radius: 20px; border: 1px solid #334155; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
  .modal-header { padding: 20px 30px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
  .modal-header h3 { margin: 0; font-size: 1.5rem; color: white; }
  .close-btn { background: none; border: none; color: #94a3b8; cursor: pointer; transition: 0.2s; }
  .close-btn:hover { color: white; transform: rotate(90deg); }
  .modal-body { padding: 30px; }
  .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
  .detail-item { display: flex; flex-direction: column; gap: 5px; }
  .detail-item .label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; }
  .detail-item .value { font-size: 1.1rem; font-weight: 600; color: white; }
  .value.price { color: #4ade80; }
  .text-green { color: #4ade80; }
  .text-red { color: #ef4444; }
  .description-section .label { display: block; font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; }
  .description-box { background: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #334155; color: #cbd5e1; line-height: 1.6; font-size: 0.95rem; }
  .modal-footer { padding: 20px 30px; border-top: 1px solid #334155; background: #0f172a; border-radius: 0 0 20px 20px; display: flex; justify-content: flex-end; gap: 15px; }
  .btn-editar-modal { background: #0ea5e9; color: white; border: none; padding: 10px 20px; border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
  .btn-cerrar-modal { background: transparent; border: 1px solid #475569; color: #cbd5e1; padding: 10px 20px; border-radius: 10px; font-weight: 600; cursor: pointer; }
  .btn-cerrar-modal:hover { background: rgba(255,255,255,0.05); color: white; }
  @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  @media (max-width: 768px) { .filters-grid { grid-template-columns: 1fr; } .list-card { padding: 20px; } }
  </style>