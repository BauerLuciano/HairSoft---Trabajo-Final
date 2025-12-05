<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Marcas</h1>
          <p>Listado y administración de marcas del sistema</p>
        </div>
        <div class="header-buttons" style="display: flex; gap: 12px;">
          <button @click="mostrarRegistrar = true" class="register-button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Registrar Marca
          </button>
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
              <option value="activo">Activos</option>
              <option value="inactivo">Inactivos</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
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
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Productos</th>
              <th>Proveedores</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="marca in marcasPaginadas" :key="marca.id" 
                :class="{'sin-proveedores-row': marca.total_proveedores === 0}">
              <td><strong>{{ marca.nombre }}</strong></td>
              <td class="descripcion-cell">{{ marca.descripcion || 'Sin descripción' }}</td>
              <td>
                <span class="badge-estado estado-info">
                  {{ marca.productos_count || 0 }} producto{{ marca.productos_count !== 1 ? 's' : '' }}
                </span>
              </td>
              <td>
                <div class="proveedores-lista">
                  <div v-if="marca.proveedores_nombres && marca.proveedores_nombres.length > 0">
                    <div v-for="(proveedor, index) in getPrimerosProveedores(marca)" :key="proveedor.id || index" 
                         class="proveedor-item">
                      <span class="proveedor-nombre">{{ proveedor.nombre }}</span>
                    </div>
                    <div v-if="marca.proveedores_nombres.length > 3" class="mas-proveedores">
                      +{{ marca.proveedores_nombres.length - 3 }} más...
                    </div>
                  </div>
                  <div v-else class="sin-proveedores">
                    Sin proveedores
                  </div>
                </div>
              </td>
              <td>
                <span class="badge-estado" :class="getEstadoClass(marca.estado)">
                  {{ marca.estado === 'activo' ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarMarca(marca)" class="action-button edit" title="Editar marca">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                  <button @click="cambiarEstadoMarca(marca)" class="action-button" 
                          :class="marca.estado === 'activo' ? 'delete' : 'success'" 
                          :title="marca.estado === 'activo' ? 'Desactivar marca' : 'Activar marca'">
                    <svg v-if="marca.estado === 'activo'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"/>
                      <path d="M8 12l3 3 5-5"/>
                    </svg>
                    <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="marcasPaginadas.length === 0" class="no-results">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="no-results-icon">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          <p>No se encontraron marcas</p>
          <small>Intenta con otros términos de búsqueda</small>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Anterior
        </button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">
          Siguiente
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
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
        <EditarMarca 
          :marca="marcaEditando"
          @marca-actualizada="marcaActualizada"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import RegistrarMarca from './RegistrarMarca.vue'
import EditarMarca from './EditarMarca.vue'

const API_BASE = 'http://127.0.0.1:8000'

const marcas = ref([])
const filtros = ref({ busqueda: '', estado: '' })
const pagina = ref(1)
const itemsPorPagina = 8
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const marcaEditando = ref(null)

// Cargar marcas con productos y proveedores REALES
const cargarMarcas = async () => {
  try {
    // ✅ CORREGIDO: Rutas sin /usuarios/
    const [resMarcas, resProductos, resProveedores] = await Promise.all([
      axios.get(`${API_BASE}/api/marcas/`),
      axios.get(`${API_BASE}/api/productos/`),
      axios.get(`${API_BASE}/api/proveedores/`)
    ])
    
    const todasMarcas = resMarcas.data
    const todosProductos = resProductos.data
    const todosProveedores = resProveedores.data
    
    // 2. Crear mapa de productos por marca y proveedores por marca
    const productosPorMarca = {}
    const proveedoresPorMarca = {}
    
    // Inicializar estructuras
    todasMarcas.forEach(marca => {
      productosPorMarca[marca.id] = {
        count: 0,
        productos: []
      }
      proveedoresPorMarca[marca.id] = new Set()
    })
    
    // 3. Procesar TODOS los productos
    todosProductos.forEach(producto => {
      const marcaId = producto.marca
      
      if (marcaId && productosPorMarca[marcaId]) {
        productosPorMarca[marcaId].count++
        productosPorMarca[marcaId].productos.push(producto)
        
        if (producto.proveedores && Array.isArray(producto.proveedores)) {
          producto.proveedores.forEach(proveedorId => {
            const proveedor = todosProveedores.find(p => p.id === proveedorId)
            if (proveedor) {
              proveedoresPorMarca[marcaId].add(proveedor.nombre)
            }
          })
        }
        
        if (producto.proveedores_nombres && Array.isArray(producto.proveedores_nombres)) {
          producto.proveedores_nombres.forEach(nombre => {
            proveedoresPorMarca[marcaId].add(nombre)
          })
        }
      }
    })
    
    // 4. Procesar marcas con datos REALES
    marcas.value = todasMarcas.map(marca => {
      const productosInfo = productosPorMarca[marca.id] || { count: 0, productos: [] }
      const proveedoresDeEstaMarca = Array.from(proveedoresPorMarca[marca.id] || [])
      
      return {
        ...marca,
        productos_count: productosInfo.count,
        total_proveedores: proveedoresDeEstaMarca.length,
        proveedores_nombres: proveedoresDeEstaMarca,
        updated_at: marca.updated_at || marca.fecha_creacion
      }
    }).sort((a, b) => b.id - a.id)
    
  } catch (err) {
    console.error('❌ Error al cargar marcas:', err)
    alert('No se pudo cargar las marcas.')
  }
}

// Formatear fecha
const formatFecha = (fecha) => {
  if (!fecha) return '-'
  try {
    return new Date(fecha).toLocaleDateString('es-AR', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  } catch (error) {
    return fecha
  }
}

// Clase para estado
const getEstadoClass = (estado) => {
  const estadoLower = estado?.toLowerCase() || ''
  if (estadoLower === 'activo') return 'estado-success'
  if (estadoLower === 'inactivo') return 'estado-danger'
  return 'estado-secondary'
}

// Obtener primeros proveedores para mostrar
const getPrimerosProveedores = (marca) => {
  if (!marca.proveedores_nombres || !Array.isArray(marca.proveedores_nombres)) {
    return []
  }
  
  return marca.proveedores_nombres.slice(0, 3).map((nombre, index) => ({ 
    id: index, 
    nombre: nombre 
  }))
}

// Filtrado
const marcasFiltradas = computed(() => {
  return marcas.value.filter(m => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      m.nombre.toLowerCase().includes(busca) ||
      (m.descripcion && m.descripcion.toLowerCase().includes(busca))
    
    const matchEstado = !filtros.value.estado || m.estado === filtros.value.estado
    
    return matchBusqueda && matchEstado
  })
})

// Estadísticas
const marcasInactivas = computed(() => marcasFiltradas.value.filter(m => m.estado === 'inactivo').length)
const marcasSinProveedores = computed(() => marcasFiltradas.value.filter(m => !m.total_proveedores || m.total_proveedores === 0).length)

// Paginación
const totalPaginas = computed(() => Math.max(1, Math.ceil(marcasFiltradas.value.length / itemsPorPagina)))
const marcasPaginadas = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return marcasFiltradas.value.slice(inicio, inicio + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Cambiar estado de marca
const cambiarEstadoMarca = async (marca) => {
  const nuevoEstado = marca.estado === 'activo' ? 'inactivo' : 'activo'
  const accion = nuevoEstado === 'activo' ? 'activar' : 'desactivar'
  
  if (!confirm(`¿Está seguro de ${accion} la marca "${marca.nombre}"?`)) {
    return
  }

  try {
    // ✅ CORREGIDO: Ruta sin /usuarios/
    await axios.patch(`${API_BASE}/api/marcas/${marca.id}/cambiar_estado/`, { 
      estado: nuevoEstado 
    })
    
    await cargarMarcas()
    alert(`Marca ${accion}da correctamente`)
  } catch (err) {
    console.error('Error cambiando estado:', err)
    alert(`No se pudo ${accion} la marca`)
  }
}

// Editar marca
const editarMarca = (marca) => { 
  marcaEditando.value = marca
  mostrarEditar.value = true 
}

// Modales
const cerrarModal = () => { mostrarRegistrar.value = false }
const cerrarModalEditar = () => { 
  mostrarEditar.value = false
  marcaEditando.value = null 
}

// Eventos de los modales
const marcaRegistrada = async () => { 
  cerrarModal()
  await cargarMarcas()
  pagina.value = 1 
}

const marcaActualizada = async () => { 
  cerrarModalEditar()
  await cargarMarcas() 
}

// Limpiar filtros
const limpiarFiltros = () => { 
  filtros.value = { busqueda: '', estado: '' }
  pagina.value = 1 
}

// Watch para resetear página cuando cambian filtros
watch(filtros, () => { pagina.value = 1 }, { deep: true })

// Inicialización
onMounted(async () => { 
  await cargarMarcas()
})
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

.estado-info {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
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

.sin-proveedores-row {
  background: var(--hover-bg);
  opacity: 0.9;
}

.sin-proveedores-row:hover {
  background: var(--bg-tertiary);
}

/* Estilos específicos para marcas */
.descripcion-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.fecha-actualizacion {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  white-space: nowrap;
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