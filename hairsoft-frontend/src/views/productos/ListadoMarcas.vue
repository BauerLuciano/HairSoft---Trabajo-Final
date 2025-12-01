<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Marcas</h1>
          <p>Administración y control de marcas del sistema</p>
        </div>
        <div class="header-buttons">
          <button @click="mostrarRegistrar = true" class="register-button">
            <Plus :size="18" />
            Registrar Marca
          </button>
          <router-link to="/productos" class="register-button secondary">
            <ArrowLeft :size="18" />
            Volver a Productos
          </router-link>
        </div>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre de marca..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos</option>
              <option value="ACTIVO">Activos</option>
              <option value="INACTIVO">Inactivos</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Productos</label>
            <select v-model="filtros.productos" class="filter-input">
              <option value="">Todos</option>
              <option value="con">Con productos</option>
              <option value="sin">Sin productos</option>
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

      <!-- Tabla de marcas -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Productos asociados</th>
              <th>Proveedores asociados</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="marca in marcasPaginados" :key="marca.id">
              <td><strong>#{{ marca.id }}</strong></td>
              <td>
                <div class="marca-info">
                  <strong>{{ marca.nombre || '–' }}</strong>
                </div>
              </td>
              <td>
                <span class="badge-estado" :class="getProductosClass(marca.productos_count)">
                  {{ marca.productos_count || 0 }} productos
                </span>
              </td>
              <td>
                <div class="proveedores-lista">
                  <div v-if="marca.proveedores_nombres && marca.proveedores_nombres.length > 0">
                    <div v-for="(proveedor, index) in marca.proveedores_nombres.slice(0, 3)" :key="index" 
                         class="proveedor-item">
                      <span class="proveedor-nombre">{{ proveedor }}</span>
                    </div>
                    <div v-if="marca.proveedores_nombres.length > 3" class="mas-proveedores">
                      +{{ marca.proveedores_nombres.length - 3 }} más...
                    </div>
                  </div>
                  <div v-else class="sin-proveedores">
                    Sin proveedor
                  </div>
                </div>
              </td>
              <td>
                <span class="badge-estado" :class="getEstadoClass(marca.estado)">
                  {{ marca.estado === 'ACTIVO' ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarMarca(marca)" class="action-button edit" title="Editar marca">
                    <Edit3 :size="14" />
                  </button>
                  <button @click="cambiarEstadoMarca(marca)" class="action-button" 
                          :class="marca.estado === 'ACTIVO' ? 'delete' : 'success'" 
                          :title="marca.estado === 'ACTIVO' ? 'Desactivar marca' : 'Activar marca'">
                    <Power :size="14" v-if="marca.estado === 'ACTIVO'" />
                    <CheckCircle :size="14" v-else />
                  </button>
                  <button @click="eliminarMarca(marca)" class="action-button delete" title="Eliminar marca">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="marcasPaginados.length === 0" class="no-results">
          <PackageX class="no-results-icon" :size="48" />
          <p>No se encontraron marcas</p>
          <small>Intenta con otros términos de búsqueda</small>
        </div>
      </div>

      <!-- Mostrando cantidad -->
      <div class="usuarios-count">
        <p>
          <Package :size="16" />
          Mostrando {{ marcasPaginados.length }} de {{ marcasFiltradas.length }} marcas
        </p>
        <div class="alertas-container">
          <span v-if="marcasInactivas > 0" class="alerta-inactivo">
            <PowerOff :size="14" />
            {{ marcasInactivas }} inactivas
          </span>
          <span v-if="marcasSinProductos > 0" class="alerta-stock">
            <PackageX :size="14" />
            {{ marcasSinProductos }} sin productos
          </span>
        </div>
      </div>

      <!-- Paginación -->
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

    <!-- Modal Registrar Marca -->
    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <RegistrarMarca 
          @marca-registrada="marcaRegistrada"
          @cancelar="cerrarModal"
        />
      </div>
    </div>

    <!-- Modal Editar Marca -->
    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModalEditar" title="Cerrar formulario">
          <X :size="20" />
        </button>
        <ModificarMarca 
          :marca-id="marcaEditando?.id" 
          @marca-actualizada="marcaActualizada"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import RegistrarMarca from './RegistrarMarca.vue'
import ModificarMarca from './ModificarMarca.vue'
import { 
  Package, PackageX, Plus, Edit3, Power, CheckCircle, PowerOff,
  ChevronLeft, ChevronRight, Trash2, ArrowLeft, X
} from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000'

export default {
  name: "ListadoMarcas",
  components: {
    RegistrarMarca,
    ModificarMarca,
    Package, PackageX, Plus, Edit3, Power, CheckCircle, PowerOff,
    ChevronLeft, ChevronRight, Trash2, ArrowLeft, X
  },
  setup() {
    const router = useRouter()
    const marcas = ref([])
    const filtros = ref({ 
      busqueda: '', 
      estado: '', 
      productos: '' 
    })

    const pagina = ref(1)
    const itemsPorPagina = 8
    const mostrarRegistrar = ref(false)
    const mostrarEditar = ref(false)
    const marcaEditando = ref(null)

    const cargarMarcas = async () => {
      try {
        const res = await axios.get(`${API_BASE}/usuarios/api/marcas/`)
        marcas.value = res.data.sort((a, b) => b.id - a.id)
        console.log('Marcas cargadas:', marcas.value)
        
        // DEBUG: Ver estructura de datos
        marcas.value.forEach((marca, index) => {
          console.log(`Marca ${index + 1}:`, {
            id: marca.id,
            nombre: marca.nombre,
            proveedores_nombres: marca.proveedores_nombres,
            proveedores_count: marca.proveedores_count,
            productos_count: marca.productos_count
          })
        })
      } catch (err) {
        console.error('❌ Error al cargar marcas:', err)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo cargar la lista de marcas',
          confirmButtonColor: '#0ea5e9'
        })
      }
    }

    const getEstadoClass = (estado) => {
      if (estado === 'ACTIVO') return 'estado-success'
      if (estado === 'INACTIVO') return 'estado-danger'
      return 'estado-secondary'
    }

    const getProductosClass = (cantidad) => {
      if (cantidad === 0) return 'estado-danger'
      if (cantidad <= 3) return 'estado-warning'
      return 'estado-success'
    }

    onMounted(async () => {
      await cargarMarcas()
    })

    const marcasFiltradas = computed(() => {
      return marcas.value.filter(m => {
        const busca = filtros.value.busqueda.toLowerCase()
        const matchBusqueda = !busca || (m.nombre?.toLowerCase().includes(busca))
        
        const matchEstado = !filtros.value.estado || m.estado === filtros.value.estado
        
        const matchProductos = !filtros.value.productos || 
          (filtros.value.productos === 'con' && m.productos_count > 0) ||
          (filtros.value.productos === 'sin' && (!m.productos_count || m.productos_count === 0))

        return matchBusqueda && matchEstado && matchProductos
      })
    })

    const marcasInactivas = computed(() => 
      marcasFiltradas.value.filter(m => m.estado === 'INACTIVO').length
    )

    const marcasSinProductos = computed(() => 
      marcasFiltradas.value.filter(m => !m.productos_count || m.productos_count === 0).length
    )

    const totalPaginas = computed(() => 
      Math.max(1, Math.ceil(marcasFiltradas.value.length / itemsPorPagina))
    )

    const marcasPaginados = computed(() => {
      const inicio = (pagina.value - 1) * itemsPorPagina
      return marcasFiltradas.value.slice(inicio, inicio + itemsPorPagina)
    })

    const paginaAnterior = () => { 
      if (pagina.value > 1) pagina.value-- 
    }

    const paginaSiguiente = () => { 
      if (pagina.value < totalPaginas.value) pagina.value++ 
    }

    const editarMarca = (marca) => { 
      marcaEditando.value = marca; 
      mostrarEditar.value = true 
    }

    const marcaRegistrada = async () => { 
      await cargarMarcas(); 
      cerrarModal(); 
      pagina.value = 1 
    }

    const marcaActualizada = async () => { 
      await cargarMarcas(); 
      cerrarModalEditar() 
    }

    const cambiarEstadoMarca = async (marca) => {
      const nuevoEstado = marca.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'
      const accion = nuevoEstado === 'ACTIVO' ? 'activar' : 'desactivar'
      
      const result = await Swal.fire({
        title: `¿${accion.charAt(0).toUpperCase() + accion.slice(1)} marca?`,
        text: `¿Está seguro de ${accion} la marca "${marca.nombre}"?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#0ea5e9',
        cancelButtonColor: '#6b7280',
        confirmButtonText: `Sí, ${accion}`,
        cancelButtonText: 'Cancelar'
      })
      
      if (!result.isConfirmed) return
      
      try {
        const res = await axios.post(`${API_BASE}/usuarios/api/marcas/cambiar-estado/${marca.id}/`)
        
        if (res.data.status === 'ok') {
          // Actualizar el estado localmente
          marca.estado = nuevoEstado
          
          Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: res.data.message,
            confirmButtonColor: '#0ea5e9'
          })
        }
      } catch (err) { 
        console.error(err)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: `No se pudo ${accion} la marca`,
          confirmButtonColor: '#0ea5e9'
        })
      }
    }

    const eliminarMarca = async (marca) => {
      const result = await Swal.fire({
        title: '¿Eliminar marca?',
        text: `¿Está seguro de eliminar la marca "${marca.nombre}"?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#0ea5e9',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      })
      
      if (!result.isConfirmed) return

      try {
        await axios.delete(`${API_BASE}/usuarios/api/marcas/eliminar/${marca.id}/`)
        marcas.value = marcas.value.filter(m => m.id !== marca.id)
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Marca eliminada correctamente',
          confirmButtonColor: '#0ea5e9'
        })
      } catch (error) {
        console.error("Error al eliminar marca:", error)
        const errorMsg = error.response?.data?.error || "No se pudo eliminar la marca"
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: errorMsg,
          confirmButtonColor: '#0ea5e9'
        })
      }
    }

    const limpiarFiltros = () => { 
      filtros.value = { busqueda: '', estado: '', productos: '' }
      pagina.value = 1 
    }

    const cerrarModal = () => { mostrarRegistrar.value = false }
    const cerrarModalEditar = () => { mostrarEditar.value = false; marcaEditando.value = null }

    const navegarAProductos = () => {
      router.push('/productos')
    }

    watch(filtros, () => { pagina.value = 1 }, { deep: true })

    return {
      marcas,
      filtros,
      pagina,
      itemsPorPagina,
      mostrarRegistrar,
      mostrarEditar,
      marcaEditando,
      marcasFiltradas,
      marcasPaginados,
      marcasInactivas,
      marcasSinProductos,
      totalPaginas,
      cargarMarcas,
      getEstadoClass,
      getProductosClass,
      editarMarca,
      cambiarEstadoMarca,
      eliminarMarca,
      paginaAnterior,
      paginaSiguiente,
      limpiarFiltros,
      marcaRegistrada,
      marcaActualizada,
      cerrarModal,
      cerrarModalEditar,
      navegarAProductos
    }
  }
}
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - MARCAS
   ======================================== */

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
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
  white-space: nowrap;
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

.header-buttons {
  display: flex;
  gap: 12px;
}

/* Botón registrar */
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
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.register-button.secondary {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  box-shadow: 0 6px 20px rgba(107, 114, 128, 0.35);
}

.register-button.secondary:hover {
  background: linear-gradient(135deg, #4b5563, #374151);
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

.filter-input, .filter-select {
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.filter-input:focus, .filter-select:focus {
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
  display: flex;
  align-items: center;
  gap: 6px;
}

.clear-filters-btn:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
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

/* Información de la marca */
.marca-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ESTILOS PARA LA LISTA DE PROVEEDORES EN LA TABLA */
.proveedores-lista {
  max-width: 250px;
}

.proveedor-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid var(--border-color);
}

.proveedor-item:last-child {
  border-bottom: none;
}

.proveedor-nombre {
  color: var(--text-primary);
  font-size: 0.85rem;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.mas-proveedores {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-style: italic;
  text-align: center;
  padding: 4px 0;
  background: var(--hover-bg);
  border-radius: 4px;
  margin-top: 4px;
}

.sin-proveedores {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-style: italic;
  text-align: center;
  padding: 8px 0;
}

/* BOTONES DE ACCIÓN - CON VARIABLES */
.action-buttons { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
}

.action-button {
  padding: 8px;
  border: none;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  width: 40px;
  height: 40px;
}

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
  display: flex;
  align-items: center;
  gap: 8px;
}

.alertas-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.alerta-stock {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.alerta-inactivo {
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

/* ESTADOS DE CARGA - CON VARIABLES */
.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
}

.no-results-icon {
  margin-bottom: 15px;
  opacity: 0.5;
  color: var(--text-tertiary);
}

.no-results p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: var(--text-primary);
}

.no-results small {
  font-size: 0.9em;
  color: var(--text-tertiary);
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
  display: flex;
  align-items: center;
  gap: 8px;
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
  animation: slideUp 0.3s ease;
  max-height: 85vh;
  max-width: 90vw;
  width: auto;
  overflow-y: auto;
  border-radius: 16px;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--border-color);
  padding: 0;
  margin: 20px;
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
  width: 12px;
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
    gap: 10px;
  }
  
  .alertas-container {
    flex-direction: column;
    width: 100%;
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
  
  .filter-input, .filter-select {
    font-size: 0.9rem;
  }
  
  .badge-estado {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
  
  .action-button {
    width: 36px;
    height: 36px;
  }
  
  .header-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .register-button {
    width: 100%;
    justify-content: center;
  }
}
</style>