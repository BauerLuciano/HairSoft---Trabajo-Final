<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <!-- Header -->
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

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre, teléfono o producto..." class="filter-input"/>
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

      <!-- Tabla de proveedores -->
      <div class="table-container">
        <table class="proveedores-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Contacto</th>
              <th>Teléfono</th>
              <th>Email</th>
              <th>Dirección</th>
              <th>Productos</th>
              <th>Categorías</th>
              <th>Estado</th>
              <th>Fecha Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="proveedor in proveedoresPaginados" :key="proveedor.id">
              <td><strong>{{ proveedor.nombre || '–' }}</strong></td>
              <td>{{ proveedor.contacto || '–' }}</td>
              <td>{{ proveedor.telefono || 'No registrado' }}</td>
              <td>{{ proveedor.email || '–' }}</td>
              <td class="direccion-cell">{{ proveedor.direccion || '–' }}</td>
              <td>
                <div class="productos-lista">
                  <div v-for="(producto, index) in getPrimerosProductos(proveedor.productos)" :key="index" 
                       class="producto-item">
                    <span class="producto-nombre">{{ producto }}</span>
                  </div>
                  <div v-if="proveedor.productos && proveedor.productos.length > 3" class="mas-productos">
                    +{{ proveedor.productos.length - 3 }} más...
                  </div>
                  <div v-else-if="!proveedor.productos || proveedor.productos.length === 0" class="sin-productos">
                    Sin productos
                  </div>
                </div>
              </td>
              <td>
                <div v-if="proveedor.categorias_nombres && proveedor.categorias_nombres.length > 0" class="categorias-container">
                  <span v-for="(categoria, index) in getPrimerasCategorias(proveedor.categorias_nombres)" :key="index" 
                        class="categoria-badge">
                    {{ categoria }}
                  </span>
                  <div v-if="proveedor.categorias_nombres.length > 2" class="mas-categorias">
                    +{{ proveedor.categorias_nombres.length - 2 }} más
                  </div>
                </div>
                <span v-else class="sin-categoria">–</span>
              </td>
              <td>
                <span class="badge-estado" :class="getEstadoClass(proveedor.estado)">
                  {{ proveedor.estado === 'ACTIVO' ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td>{{ formatFecha(proveedor.fecha_creacion) }}</td>
              <td>
                <div class="action-buttons">
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

      <!-- Mostrando cantidad -->
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

    <!-- Modal Registrar Proveedor -->
    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <RegistrarProveedor 
          @proveedor-registrado="proveedorRegistrado"
          @cancelar="cerrarModal"
        />
      </div>
    </div>

    <!-- Modal Editar Proveedor -->
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
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

// Cargar proveedores desde backend
const cargarProveedores = async () => {
  try {
    // ✅ CORREGIDO: Ruta sin /usuarios/
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

// Cargar categorías de tipo PRODUCTO
const cargarCategorias = async () => {
  try {
    // ✅ CORREGIDO: Ruta sin /usuarios/
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

// Método para ir a gestión de precios general
const irAGestionPrecios = () => {
  router.push('/proveedores/listas-precios')
}

// Método para ver precios de un proveedor específico
const verPreciosProveedor = (proveedor) => {
  router.push(`/proveedores/listas-precios?proveedor_id=${proveedor.id}`)
}

// Método para obtener primeros productos
const getPrimerosProductos = (productos) => {
  if (!productos || productos.length === 0) return []
  return productos.slice(0, 3)
}

// Método para obtener primeras categorías
const getPrimerasCategorias = (categorias) => {
  if (!categorias || categorias.length === 0) return []
  return categorias.slice(0, 2)
}

// Clase para el estado
const getEstadoClass = (estado) => {
  return estado === 'ACTIVO' ? 'estado-success' : 'estado-danger'
}

// Filtros por fecha
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

// Filtrar proveedores
const proveedoresFiltrados = computed(() => {
  const filtrados = proveedores.value.filter(p => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      (p.nombre?.toLowerCase().includes(busca) || 
       p.telefono?.toLowerCase().includes(busca) ||
       p.productos_que_ofrece?.toLowerCase().includes(busca));
       
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

// Contadores
const proveedoresInactivos = computed(() => proveedoresFiltrados.value.filter(p => p.estado === 'INACTIVO').length)

// Paginación
const totalPaginas = computed(() => Math.max(1, Math.ceil(proveedoresFiltrados.value.length / itemsPorPagina)))

const proveedoresPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return proveedoresFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

// Navegación paginación
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Acciones sobre proveedores
const editarProveedor = (proveedor) => {
  proveedorEditando.value = proveedor
  mostrarEditar.value = true
}

// Cambiar estado del proveedor
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
    // ✅ CORREGIDO: Ruta sin /usuarios/
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

// Cuando se actualiza el proveedor
const proveedorActualizado = async () => {
  await cargarProveedores()
  cerrarModalEditar()
}

const proveedorRegistrado = async () => {
  await cargarProveedores()
  cerrarModal()
  pagina.value = 1
}

// Limpiar filtros
const limpiarFiltros = () => { 
  filtros.value = { busqueda: '', categoria: '', estado: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1 
}

// Formato de fecha
const formatFecha = (fecha) => fecha ? new Date(fecha).toLocaleString() : '–'

// Cerrar modales
const cerrarModal = () => { mostrarRegistrar.value = false }

const cerrarModalEditar = () => {
  mostrarEditar.value = false
  proveedorEditando.value = null
}

// Resetear página al cambiar filtros
watch(filtros, () => {
  pagina.value = 1
}, { deep: true })
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - PROVEEDORES
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

/* Botones del header */
.header-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

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
}

.register-button.secondary {
  background: linear-gradient(135deg, #059669, #047857);
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.35);
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

.register-button.secondary:hover {
  box-shadow: 0 10px 30px rgba(5, 150, 105, 0.5);
  background: linear-gradient(135deg, #047857, #065f46);
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
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
  height: 44px;
  box-sizing: border-box;
  width: 100%;
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
  height: 44px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
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

.proveedores-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  table-layout: auto;
  min-width: 1400px;
}

.proveedores-table th {
  background: var(--accent-color);
  color: white;
  padding: 18px 14px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1.2px;
  white-space: nowrap;
}

.proveedores-table tr {
  border-bottom: 1px solid var(--border-color);
}

.proveedores-table td {
  padding: 14px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.proveedores-table td strong {
  color: var(--text-primary);
  font-weight: 800;
  letter-spacing: 0.3px;
}

.proveedores-table tr:hover {
  background: var(--hover-bg);
  transition: all 0.2s ease;
}

/* Estilos específicos de proveedores */
.direccion-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ESTILOS PARA LA LISTA DE PRODUCTOS EN LA TABLA */
.productos-lista {
  max-width: 250px;
}

.producto-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid var(--border-color);
}

.producto-item:last-child {
  border-bottom: none;
}

.producto-nombre {
  color: var(--text-primary);
  font-size: 0.85rem;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.mas-productos {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-style: italic;
  text-align: center;
  padding: 4px 0;
  background: var(--hover-bg);
  border-radius: 4px;
  margin-top: 4px;
}

.sin-productos {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-style: italic;
  text-align: center;
  padding: 8px 0;
}

/* ESTILOS CORREGIDOS PARA CATEGORÍAS */
.categorias-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 200px;
  min-width: 150px;
}

.categoria-badge {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  padding: 6px 10px;
  border-radius: 16px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: block;
  letter-spacing: 0.3px;
  white-space: normal;
  word-break: break-word;
  text-align: center;
  line-height: 1.3;
  box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
  width: 100%;
  box-sizing: border-box;
}

.mas-categorias {
  color: var(--text-tertiary);
  font-size: 0.75rem;
  font-style: italic;
  text-align: center;
  padding: 4px 8px;
  background: var(--hover-bg);
  border-radius: 8px;
  margin-top: 2px;
}

.sin-categoria {
  color: var(--text-tertiary);
  font-style: italic;
  text-align: center;
}

/* BOTONES DE ACCIÓN - UNO AL LADO DEL OTRO */
.action-buttons { 
  display: flex; 
  gap: 6px; 
  flex-wrap: nowrap;
  justify-content: center;
  align-items: center;
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
  min-width: 40px;
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

.action-button.prices {
  background: var(--bg-tertiary);
  border: 1px solid #059669;
  color: #059669;
}

.action-button.prices:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(5, 150, 105, 0.4);
  border-color: #059669;
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
.proveedores-count {
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

.proveedores-count p {
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
  
  .header-buttons {
    flex-direction: column;
    width: 100%;
    gap: 8px;
  }
  
  .register-button {
    width: 100%;
    justify-content: center;
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
  
  .proveedores-table {
    font-size: 0.85rem;
    min-width: 1200px;
  }
  
  .proveedores-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
  }
  
  .action-buttons {
    flex-direction: row;
    gap: 4px;
  }
  
  .action-button {
    width: 36px;
    height: 36px;
    min-width: 36px;
  }
  
  .categorias-container {
    max-width: 150px;
    min-width: 120px;
  }
  
  .categoria-badge {
    font-size: 0.7rem;
    padding: 4px 8px;
  }
  
  .proveedores-count {
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
  
  .proveedores-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
    min-width: 1100px;
  }
  
  .filter-input {
    font-size: 0.9rem;
  }
  
  .badge-estado {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
  
  .action-button {
    width: 32px;
    height: 32px;
    min-width: 32px;
  }
  
  .categorias-container {
    max-width: 120px;
    min-width: 100px;
  }
  
  .categoria-badge {
    font-size: 0.65rem;
    padding: 3px 6px;
  }
}
</style>