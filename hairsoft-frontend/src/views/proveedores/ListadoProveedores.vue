<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <div class="list-header">
        <div class="header-content">
          <h1>Proveedores Registrados</h1>
          <p>Gestión de proveedores del sistema</p>
        </div>
        <div class="header-actions">
          <button @click="mostrarRegistrar = true" class="register-button">➕ Registrar Proveedor</button>
          <button @click="irAGestionPrecios" class="prices-button">💰 Lista de Precios</button>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre, teléfono o producto..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Categoría</label>
            <select v-model="filtros.categoria" class="filter-select">
              <option value="">Todas las categorías</option>
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
            <label>Fecha desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Fecha hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar filtros</button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="users-table">
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
                <td>{{ proveedor.nombre || '–' }}</td>
                <td>{{ proveedor.contacto || '–' }}</td>
                <td>{{ proveedor.telefono || 'No registrado' }}</td>
                <td>{{ proveedor.email || '–' }}</td>
                <td class="direccion-cell">{{ proveedor.direccion || '–' }}</td>
                <td class="productos-cell">
                  <ul v-if="proveedor.productos && proveedor.productos.length > 0" class="productos-list">
                    <li v-for="producto in proveedor.productos" :key="producto">{{ producto }}</li>
                  </ul>
                  <span v-else>–</span>
                </td>
                <td>
                  <span v-if="proveedor.categorias_nombres && proveedor.categorias_nombres.length > 0" class="categoria-badge">
                    {{ proveedor.categorias_nombres.join(', ') }}
                  </span>
                  <span v-else class="sin-categoria">–</span>
                </td>
                <td><span :class="proveedor.estado.toLowerCase()">{{ proveedor.estado }}</span></td>
                <td>{{ formatFecha(proveedor.fecha_creacion) }}</td>
                <td>
                  <div class="action-buttons">
                    <button @click="editarProveedor(proveedor)" class="action-button edit">✏️</button>
                    <button @click="verPreciosProveedor(proveedor)" class="action-button prices">💰</button>
                    <button @click="eliminarProveedor(proveedor)" class="action-button delete">🗑️</button>
                  </div>
                </td>
              </tr>
            </tbody>
        </table>

        <div v-if="proveedoresPaginados.length === 0" class="no-results">
          <p>No se encontraron proveedores</p>
        </div>
      </div>

      <p class="usuarios-count">
        Mostrando {{ proveedoresPaginados.length }} de {{ proveedoresFiltrados.length }} proveedores
      </p>

      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">← Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente →</button>
      </div>
    </div>

    <div v-if="mostrarRegistrar" class="form-overlay">
      <RegistrarProveedor 
        @proveedor-registrado="refrescarProveedores"
        @cancelar="cerrarModal"
      />
    </div>

    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
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
import RegistrarProveedor from './RegistrarProveedor.vue'
import ModificarProveedor from './ModificarProveedor.vue'

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
    const res = await axios.get(`${API_BASE}/usuarios/api/proveedores/`)
    proveedores.value = res.data.sort((a, b) => {
      const fechaA = new Date(a.fecha_creacion || 0)
      const fechaB = new Date(b.fecha_creacion || 0)
      return fechaB - fechaA
    })
  } catch (err) {
    console.error('Error al cargar proveedores:', err)
    alert('No se pudo cargar la lista de proveedores')
  }
}

// Cargar categorías de tipo PRODUCTO
const cargarCategorias = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/categorias/productos/`) 
    categorias.value = res.data.filter(c => c.activo)
  } catch (err) {
    console.error('Error al cargar categorías:', err)
  }
}

onMounted(async () => {
  await cargarProveedores()
  await cargarCategorias()
})

// ✅ NUEVO: Método para ir a gestión de precios general
const irAGestionPrecios = () => {
  router.push('/proveedores/listas-precios')
}

// Método para ver precios de un proveedor específico
const verPreciosProveedor = (proveedor) => {
  router.push(`/proveedores/listas-precios?proveedor_id=${proveedor.id}`)
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

// Paginación
const totalPaginas = computed(() => {
  return Math.max(1, Math.ceil(proveedoresFiltrados.value.length / itemsPorPagina))
})

const proveedoresPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return proveedoresFiltrados.value.slice(inicio, fin)
})

// Navegación paginación
const paginaAnterior = () => { 
  if (pagina.value > 1) pagina.value--
}

const paginaSiguiente = () => { 
  if (pagina.value < totalPaginas.value) pagina.value++
}

// Acciones sobre proveedores
const editarProveedor = (proveedor) => {
  proveedorEditando.value = proveedor
  mostrarEditar.value = true
}

// Cuando se actualiza el proveedor
const proveedorActualizado = async () => {
  await cargarProveedores()
  cerrarModalEditar()
}

const eliminarProveedor = async (proveedor) => {
  if (!confirm(`¿Desactivar al proveedor ${proveedor.nombre}?`)) return
  try {
    await axios.delete(`${API_BASE}/usuarios/api/proveedores/${proveedor.id}/`) 
    proveedor.estado = 'INACTIVO'
    
    await nextTick()
    alert('Proveedor desactivado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo desactivar el proveedor')
  }
}

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = { busqueda: '', categoria: '', estado: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1
}

// Formato de fecha
const formatFecha = (fecha) => fecha ? new Date(fecha).toLocaleString() : '–'

// Cerrar modales
const cerrarModal = () => mostrarRegistrar.value = false

const cerrarModalEditar = () => {
  mostrarEditar.value = false
  proveedorEditando.value = null
}

// Refrescar proveedores 
const refrescarProveedores = async (nuevoProveedor = null) => {
  if (nuevoProveedor) {
    await cargarProveedores()
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
/* Contenedor principal con margen para el navbar */
.list-container {
  margin-left: 250px;
  padding: 20px;
  min-height: 100vh;
  transition: margin-left 0.3s ease, padding 0.3s ease;
}

/* Ajustes responsive para el margen y padding */
@media (max-width: 968px) {
  .list-container {
    margin-left: 200px;
  }
}

@media (max-width: 768px) {
  .list-container {
    margin-left: 80px;
    padding: 10px;
  }
}

/* Tarjeta principal */
.list-card {
  background: rgba(23, 23, 23, 0.8);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1800px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05) inset;
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

/* ✅ NUEVO: Contenedor para los botones del header */
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* ✅ NUEVO: Botón de lista de precios */
.prices-button {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.prices-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
  background: linear-gradient(135deg, #059669, #047857);
}

/* Botón registrar proveedor (ajustado para estar junto al nuevo botón) */
.register-button {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
}

/* Celdas específicas para proveedores */
.direccion-cell {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.productos-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.productos-cell ul li {
  line-height: 1.4;
}

.productos-list {
  margin: 0;
  padding-left: 18px;
  list-style-type: disc;
}

/* Estilos para badges de categorías */
.categoria-badge {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.sin-categoria {
  color: #6b7280;
  font-style: italic;
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

.action-button.prices {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.action-button.delete {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

/* Estados */
.activo, .inactivo {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.activo {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.inactivo {
  color: #6b7280;
  background: rgba(107, 114, 128, 0.1);
}

/* Efecto de oscurecimiento */
.overlay-activo {
  opacity: 0.4;
  filter: blur(3px);
  pointer-events: none;
}

/* OVERLAY NUEVO - SIN MODAL */
.form-overlay {
  position: fixed;
  top: 0;
  left: 250px;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(5px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  animation: fadeIn 0.3s ease;
}

/* Responsive para overlay */
@media (max-width: 968px) {
  .form-overlay {
    left: 200px;
  }
}

@media (max-width: 768px) {
  .form-overlay {
    left: 80px;
    padding: 20px;
  }
}

/* Modal overlay existente */
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

/* Animaciones */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Contenedor del formulario para editar */
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

/* Botón de cerrar modal */
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
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  z-index: 100;
  box-shadow: 0 3px 8px rgba(239,68,68,0.4);
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
  box-shadow: 0 5px 15px rgba(239,68,68,0.6);
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

/* Responsive para los botones del header */
@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    width: 100%;
    gap: 8px;
  }
  
  .register-button,
  .prices-button {
    width: 100%;
    justify-content: center;
  }
}

/* Responsive modal */
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