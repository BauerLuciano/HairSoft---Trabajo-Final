<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Productos Registrados</h1>
          <p>Gestión de productos del sistema</p>
        </div>
        <button @click="mostrarRegistrar = true" class="register-button">➕ Registrar Producto</button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre o código..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Categoría</label>
            <select v-model="filtros.categoria" class="filter-select">
              <option value="">Todas</option>
              <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
                {{ categoria.nombre }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Stock bajo</label>
            <select v-model="filtros.stockBajo" class="filter-select">
              <option value="">Todos</option>
              <option value="si">Solo stock bajo (≤ 10)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar filtros</button>
          </div>
        </div>
      </div>

      <!-- Tabla de productos -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Categoría</th>
              <th>Precio</th>
              <th>Stock</th>
              <th>Proveedores</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="producto in productosPaginados" :key="producto.id" 
                :class="{'stock-bajo-row': producto.stock_actual <= 10}">
              <td>{{ producto.codigo || '–' }}</td>
              <td>{{ producto.nombre || '–' }}</td>
              <td class="descripcion-cell">{{ producto.descripcion || 'Sin descripción' }}</td>
              <td>{{ getCategoriaNombre(producto) }}</td>
              <td>${{ producto.precio ? producto.precio.toLocaleString() : '0' }}</td>
              <td>
                <span :class="{
                  'stock-bajo': producto.stock_actual <= 10, 
                  'stock-critico': producto.stock_actual <= 5
                }">
                  {{ producto.stock_actual || 0 }}
                  <span v-if="producto.stock_actual <= 10" class="alerta-icon">⚠️</span>
                </span>
              </td>
              <td>
                <div class="proveedores-lista">
                  <div v-for="(proveedor, index) in getPrimerosProveedores(producto)" :key="proveedor.id" 
                       class="proveedor-item">
                    <span class="proveedor-nombre">{{ proveedor.nombre }}</span>
                  </div>
                  <div v-if="getProveedoresNombres(producto).length > 3" class="mas-proveedores">
                    +{{ getProveedoresNombres(producto).length - 3 }} más...
                  </div>
                  <div v-else-if="getProveedoresNombres(producto).length === 0" class="sin-proveedores">
                    Sin proveedor
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarProducto(producto)" class="action-button edit">✏️</button>
                  <button @click="eliminarProducto(producto)" class="action-button delete">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="productosPaginados.length === 0" class="no-results">
          <p v-if="productos.length === 0">No hay productos registrados</p>
          <p v-else>No se encontraron productos con los filtros aplicados</p>
        </div>
      </div>

      <!-- Mostrando cantidad -->
      <p class="usuarios-count">
        Mostrando {{ productosPaginados.length }} de {{ productosFiltrados.length }} productos
        <span v-if="productosStockBajo > 0" class="alerta-stock">
          ⚠️ {{ productosStockBajo }} productos con stock bajo
        </span>
      </p>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">← Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente →</button>
      </div>
    </div>

    <!-- Modal Registrar Producto -->
    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModal" title="Cerrar formulario">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        
        <RegistrarProducto 
          @producto-registrado="productoRegistrado"
          @cancelar="cerrarModal"
        />
      </div>
    </div>

    <!-- Modal Editar Producto -->
    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModalEditar" title="Cerrar formulario">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        <ModificarProducto 
          :producto-id="productoEditando?.id" 
          @producto-actualizado="productoActualizado"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import RegistrarProducto from './RegistrarProducto.vue'
import ModificarProducto from './ModificarProducto.vue'

const API_BASE = 'http://127.0.0.1:8000'

const productos = ref([])
const categorias = ref([])
const proveedores = ref([])
const filtros = ref({ 
  busqueda: '', 
  categoria: '', 
  stockBajo: '' 
})

const pagina = ref(1)
const itemsPorPagina = 8
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const productoEditando = ref(null)

// Cargar productos desde backend
const cargarProductos = async () => {
  try {
    console.log('🔄 Cargando productos...')
    const res = await axios.get(`${API_BASE}/usuarios/api/productos/`)
    console.log('✅ Productos cargados:', res.data)
    
    // Ordenar por ID (más reciente primero)
    productos.value = res.data.sort((a, b) => b.id - a.id)
  } catch (err) {
    console.error('❌ Error al cargar productos:', err)
    alert('No se pudo cargar la lista de productos')
  }
}

// Cargar categorías
const cargarCategorias = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/categorias/productos/`)
    categorias.value = res.data
  } catch (err) {
    console.error('Error al cargar categorías:', err)
  }
}

// Cargar proveedores
const cargarProveedores = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/proveedores/`)
    proveedores.value = res.data
  } catch (err) {
    console.error('Error al cargar proveedores:', err)
  }
}

// Helper para obtener nombre de categoría - CORREGIR
const getCategoriaNombre = (producto) => {
  if (producto.categoria_nombre) return producto.categoria_nombre
  if (producto.categoria) {
    const categoria = categorias.value.find(c => c.id === producto.categoria)
    return categoria ? categoria.nombre : '–'
  }
  return '–'
}

// Helper para obtener nombres de proveedores
const getProveedoresNombres = (producto) => {
  if (!producto.proveedores || !Array.isArray(producto.proveedores)) return []
  
  return producto.proveedores.map(provId => {
    const proveedor = proveedores.value.find(p => p.id === provId)
    return proveedor ? proveedor.nombre : null
  }).filter(Boolean)
}

// Helper para obtener primeros proveedores para mostrar en tabla
const getPrimerosProveedores = (producto) => {
  const proveedoresNombres = getProveedoresNombres(producto)
  if (!proveedoresNombres || proveedoresNombres.length === 0) return []
  
  // Convertir array de nombres a objetos con id y nombre
  return proveedoresNombres.slice(0, 3).map((nombre, index) => ({
    id: index,
    nombre: nombre,
    tipo: 'Prov'
  }))
}

onMounted(async () => {
  await cargarCategorias()
  await cargarProveedores()
  await cargarProductos()
})

// Filtrar productos
const productosFiltrados = computed(() => {
  const filtrados = productos.value.filter(p => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      (p.nombre?.toLowerCase().includes(busca) || 
       p.codigo?.toLowerCase().includes(busca))
    
    const matchCategoria = !filtros.value.categoria || p.categoria == filtros.value.categoria
    const matchStockBajo = !filtros.value.stockBajo || p.stock_actual <= 10
    
    return matchBusqueda && matchCategoria && matchStockBajo
  })
  
  return filtrados
})

// Contar productos con stock bajo
const productosStockBajo = computed(() => {
  return productosFiltrados.value.filter(p => p.stock_actual <= 10).length
})

// Paginación
const totalPaginas = computed(() => {
  return Math.max(1, Math.ceil(productosFiltrados.value.length / itemsPorPagina))
})

const productosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return productosFiltrados.value.slice(inicio, fin)
})

// Navegación paginación
const paginaAnterior = () => { 
  if (pagina.value > 1) pagina.value--
}

const paginaSiguiente = () => { 
  if (pagina.value < totalPaginas.value) pagina.value++
}

// Acciones sobre productos
const editarProducto = (producto) => {
  productoEditando.value = producto
  mostrarEditar.value = true
}

// Cuando se registra un nuevo producto
const productoRegistrado = async (nuevoProducto) => {
  console.log('🔄 Recargando productos después de registro...')
  await cargarProductos() // Recargar la lista completa
  cerrarModal()
  pagina.value = 1 // Ir a la primera página
}

// Cuando se actualiza el producto
const productoActualizado = async () => {
  await cargarProductos()
  cerrarModalEditar()
}

const eliminarProducto = async (producto) => {
  if (!confirm(`¿Está seguro de eliminar el producto "${producto.nombre}"?`)) return
  try {
    await axios.delete(`${API_BASE}/usuarios/api/productos/${producto.id}/`)
    await cargarProductos() // Recargar la lista
    alert('Producto eliminado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo eliminar el producto')
  }
}

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = { busqueda: '', categoria: '', stockBajo: '' }
  pagina.value = 1
}

// Cerrar modales
const cerrarModal = () => {
  mostrarRegistrar.value = false
}

const cerrarModalEditar = () => {
  mostrarEditar.value = false
  productoEditando.value = null
}

// Resetear página al cambiar filtros
watch(filtros, () => {
  pagina.value = 1
}, { deep: true })
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - PRODUCTOS
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

/* Estilos específicos de productos */
.descripcion-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-bajo {
  color: #f59e0b;
  font-weight: bold;
  background: rgba(245, 158, 11, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.stock-critico {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.stock-bajo-row {
  background: rgba(245, 158, 11, 0.05);
  border-left: 3px solid #f59e0b;
}

.alerta-icon {
  font-size: 12px;
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
  padding: 8px 14px;
  border: none;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
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

/* ESTADOS DE CARGA - CON VARIABLES */
.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
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

.alerta-stock {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  padding: 10px 18px;
  border-radius: 20px;
  font-weight: 800;
  letter-spacing: 0.8px;
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
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
}
</style>