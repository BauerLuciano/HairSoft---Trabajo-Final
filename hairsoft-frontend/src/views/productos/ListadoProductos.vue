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
              <td>{{ getCategoriaNombre(producto.categoria) }}</td>
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
                <span v-if="getProveedoresNombres(producto).length > 0">
                  {{ getProveedoresNombres(producto).join(', ') }}
                </span>
                <span v-else class="sin-proveedor">Sin proveedor</span>
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
          ⚠️ {{ productosStockBajo }} productos con stock bajo (≤ 10)
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

// Helper para obtener nombre de categoría
const getCategoriaNombre = (categoriaId) => {
  if (!categoriaId) return '–'
  const categoria = categorias.value.find(c => c.id === categoriaId)
  return categoria ? categoria.nombre : '–'
}

// Helper para obtener nombres de proveedores
const getProveedoresNombres = (producto) => {
  if (!producto.proveedores || !Array.isArray(producto.proveedores)) return []
  
  return producto.proveedores.map(provId => {
    const proveedor = proveedores.value.find(p => p.id === provId)
    return proveedor ? proveedor.nombre : null
  }).filter(Boolean)
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
.list-container {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.list-card {
  background: rgba(23, 23, 23, 0.8);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1800px;
  margin: 0 auto;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5),
              0 0 0 1px rgba(255,255,255,0.05) inset;
  position: relative;
  overflow: hidden;
  transition: opacity 0.3s ease, filter 0.3s ease;
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #6b7280, #9ca3af, #6b7280);
  border-radius: 24px 24px 0 0;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-content h1 {
  color: white;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.header-content p {
  color: #9ca3af;
  margin: 5px 0 0 0;
  font-size: 1rem;
}

.register-button {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

.filters-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  color: #e5e7eb;
  font-weight: 500;
  font-size: 0.9rem;
}

.filter-input, .filter-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 10px 12px;
  color: white;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.filter-input:focus, .filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-input::placeholder {
  color: #9ca3af;
}

.clear-filters-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.clear-filters-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
}

.table-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.02);
}

.users-table th {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(30, 58, 138, 0.2));
  color: #e5e7eb;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.users-table td {
  padding: 14px 12px;
  color: #d1d5db;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.9rem;
}

.users-table tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

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

.sin-proveedor {
  color: #6b7280;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-button.edit {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.action-button.delete {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.action-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.no-results {
  text-align: center;
  padding: 40px;
  color: #9ca3af;
  font-style: italic;
}

.usuarios-count {
  color: #9ca3af;
  text-align: center;
  margin: 20px 0;
  font-size: 0.9rem;
}

.alerta-stock {
  color: #f59e0b;
  font-weight: bold;
  margin-left: 15px;
  background: rgba(245, 158, 11, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.pagination button {
  background: rgba(255, 255, 255, 0.1);
  color: #e5e7eb;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination button:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  color: #d1d5db;
  font-weight: 500;
}

.overlay-activo {
  opacity: 0.4;
  filter: blur(3px);
  pointer-events: none;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  position: relative;
  animation: slideUp 0.3s ease;
  max-height: 85vh;
  max-width: 70vw;
  overflow-y: auto;
  border-radius: 16px;
  background: rgba(23, 23, 23, 0.98);
  box-shadow: 0 20px 40px rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 0;
  margin: 20px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-close {
  position: absolute;
  top: 8px;
  right: 8px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  border-radius: 10px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 100;
  box-shadow: 0 3px 8px rgba(239, 68, 68, 0.4);
  overflow: hidden;
}

.modal-close::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.modal-close:hover {
  transform: scale(1.15) rotate(90deg);
  box-shadow: 0 5px 15px rgba(239, 68, 68, 0.6);
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

.modal-close:hover::before {
  left: 100%;
}

.modal-close:active {
  transform: scale(0.9) rotate(90deg);
}

.modal-close svg {
  width: 14px;
  height: 14px;
  transition: transform 0.3s ease;
}

.modal-close:hover svg {
  transform: scale(1.2);
}

@keyframes subtlePulse {
  0%, 100% {
    box-shadow: 0 3px 8px rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 3px 12px rgba(239, 68, 68, 0.6);
  }
}

.modal-close {
  animation: subtlePulse 3s infinite;
}

.modal-content ::v-deep .form-container {
  margin: 0;
  padding: 20px;
  border-radius: 16px;
}

@media (max-width: 1400px) {
  .modal-content {
    max-width: 85vw;
  }
}

@media (max-width: 768px) {
  .modal-content {
    max-width: 95vw;
    margin: 10px;
  }
  
  .list-card {
    padding: 20px;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .list-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .users-table {
    font-size: 0.8rem;
  }
  
  .users-table th,
  .users-table td {
    padding: 8px 6px;
  }
}
</style>