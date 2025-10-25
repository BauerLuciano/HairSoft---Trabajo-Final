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
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-select">
              <option value="">Todos</option>
              <option value="ACTIVO">Activo</option>
              <option value="INACTIVO">Inactivo</option>
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
              <th>Proveedor</th>
              <th>Estado</th>
              <th>Fecha Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="producto in productosPaginados" :key="producto.id" :class="{'stock-bajo-row': producto.stock_actual <= 10}">
              <td>{{ producto.codigo || '–' }}</td>
              <td>{{ producto.nombre || '–' }}</td>
              <td class="descripcion-cell">{{ producto.descripcion || 'Sin descripción' }}</td>
              <td>{{ producto.categoria_nombre || '–' }}</td>
              <td>${{ producto.precio ? producto.precio.toLocaleString() : '0' }}</td>
              <td>
                <span :class="{'stock-bajo': producto.stock_actual <= 10, 'stock-critico': producto.stock_actual <= 5}">
                  {{ producto.stock_actual || 0 }}
                  <span v-if="producto.stock_actual <= 10" class="alerta-icon">⚠️</span>
                </span>
              </td>
              <td>{{ producto.proveedor_nombre || 'Sin proveedor' }}</td>
              <td><span :class="producto.estado.toLowerCase()">{{ producto.estado }}</span></td>
              <td>{{ formatFecha(producto.fecha_creacion) }}</td>
              <td>
                <button @click="editarProducto(producto)" class="action-button edit">✏️</button>
                <button @click="eliminarProducto(producto)" class="action-button delete">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="productosPaginados.length === 0" class="no-results">
          <p>No se encontraron productos</p>
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
        
        <RegistrarProducto @producto-registrado="refrescarProductos"/>
      </div>
    </div>

    <!-- Modal Editar Producto -->
    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
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
  estado: '', 
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
    const res = await axios.get(`${API_BASE}/productos/api/productos/`)
    // Ordenar por fecha (más reciente primero)
    productos.value = res.data.sort((a, b) => {
      const fechaA = new Date(a.fecha_creacion || 0)
      const fechaB = new Date(b.fecha_creacion || 0)
      return fechaB - fechaA
    })
  } catch (err) {
    console.error('Error al cargar productos:', err)
    alert('No se pudo cargar la lista de productos')
  }
}

// Cargar categorías de PRODUCTOS (no de servicios)
const cargarCategorias = async () => {
  try {
    const res = await axios.get(`${API_BASE}/categorias/api/categorias/`)
    // Filtrar solo categorías de productos
    categorias.value = res.data.filter(c => c.tipo === 'PRODUCTO' && c.activo)
  } catch (err) {
    console.error('Error al cargar categorías:', err)
  }
}

// Cargar proveedores
const cargarProveedores = async () => {
  try {
    const res = await axios.get(`${API_BASE}/proveedores/api/proveedores/`)
    proveedores.value = res.data.filter(p => p.estado === 'ACTIVO')
  } catch (err) {
    console.error('Error al cargar proveedores:', err)
  }
}

onMounted(async () => {
  await cargarProductos()
  await cargarCategorias()
  await cargarProveedores()
})

// Filtrar productos
const productosFiltrados = computed(() => {
  const filtrados = productos.value.filter(p => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      (p.nombre?.toLowerCase().includes(busca) || 
       p.codigo?.toLowerCase().includes(busca))
    const matchCategoria = !filtros.value.categoria || (p.categoria_id && p.categoria_id == filtros.value.categoria)
    const matchEstado = !filtros.value.estado || p.estado === filtros.value.estado
    const matchStockBajo = !filtros.value.stockBajo || p.stock_actual <= 10
    
    return matchBusqueda && matchCategoria && matchEstado && matchStockBajo
  })
  
  // Ordenar por estado: ACTIVOS primero, INACTIVOS al final
  return filtrados.sort((a, b) => {
    if (a.estado === b.estado) return 0
    return a.estado === 'ACTIVO' ? -1 : 1
  })
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

// Cuando se actualiza el producto
const productoActualizado = async () => {
  await cargarProductos()
  cerrarModalEditar()
}

const eliminarProducto = async (producto) => {
  if (!confirm(`¿Desactivar el producto ${producto.nombre}?`)) return
  try {
    await axios.post(`${API_BASE}/productos/api/productos/eliminar/${producto.id}/`)
    producto.estado = 'INACTIVO'
    
    await nextTick()
    alert('Producto desactivado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo desactivar el producto')
  }
}

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = { busqueda: '', categoria: '', estado: '', stockBajo: '' }
  pagina.value = 1
}

// Formato de fecha
const formatFecha = (fecha) => fecha ? new Date(fecha).toLocaleString() : '–'

// Cerrar modales
const cerrarModal = () => mostrarRegistrar.value = false

const cerrarModalEditar = () => {
  mostrarEditar.value = false
  productoEditando.value = null
}

// Refrescar productos 
const refrescarProductos = async (nuevoProducto = null) => {
  if (nuevoProducto) {
    await cargarProductos()
    pagina.value = 1
    await nextTick()
  }
  mostrarRegistrar.value = false
}

// Resetear página al cambiar filtros
watch(filtros, () => {
  pagina.value = 1
}, { deep: true })
</script>

<style scoped>
/* Tarjeta principal */
.list-card {
  background: rgba(23, 23, 23, 0.8);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1800px;
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

/* Celdas específicas para productos */
.descripcion-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Indicadores de stock */
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

.alerta-stock {
  color: #f59e0b;
  font-weight: bold;
  margin-left: 15px;
  background: rgba(245, 158, 11, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

/* Botones de acción */
.action-buttons { 
  display: flex; 
  gap: 6px; 
  flex-wrap: wrap; 
}

.action-button {
  padding: 6px 12px;
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

/* Estados */
.activo {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.inactivo {
  color: #6b7280;
  background: rgba(107, 114, 128, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
}

/* Efecto de oscurecimiento elegante cuando se abre el modal */
.overlay-activo {
  opacity: 0.4;
  filter: blur(3px);
  pointer-events: none;
}

/* Modal overlay - fondo oscuro semitransparente */
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

/* Contenedor del formulario */
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

/* Botón de cerrar */
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

/* Efecto de pulso sutil en el botón */
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

/* Asegurar que el formulario interno se adapte */
.modal-content ::v-deep .form-container {
  margin: 0;
  padding: 20px;
  border-radius: 16px;
}

/* Responsive */
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
}
</style>