<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Usuarios</h1>
          <p>Gestión de usuarios del sistema</p>
        </div>
        <button @click="mostrarRegistrar = true" class="register-button">
          <UserPlus :size="18" />
          Registrar Usuario
        </button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre o DNI..." class="filter-input"/>
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
            <label>Rol</label>
            <select v-model="filtros.rol" class="filter-input">
              <option value="">Todos</option>
              <option v-for="rol in roles" :key="rol.id" :value="rol.id">
                {{ rol.nombre }}
              </option>
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

      <!-- Tabla de usuarios -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Apellido</th>
              <th>DNI</th>
              <th>Teléfono</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Fecha Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usuario in usuariosPaginados" :key="usuario.id">
              <td><strong>{{ usuario.nombre || '–' }}</strong></td>
              <td>{{ usuario.apellido || '–' }}</td>
              <td>{{ usuario.dni || '–' }}</td>
              <td>{{ usuario.telefono || 'No registrado' }}</td>
              <td>{{ usuario.correo || '–' }}</td>
              <td>
                <span class="badge-estado estado-info">
                  {{ usuario.rol_nombre || 'Sin rol' }}
                </span>
              </td>
              <td>
                <span class="badge-estado" :class="getEstadoClass(usuario.estado)">
                  {{ usuario.estado }}
                </span>
              </td>
              <td>{{ formatFecha(usuario.fecha_creacion) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="editarUsuario(usuario)" class="action-button edit" title="Editar usuario">
                    <Edit3 :size="14" />
                  </button>
                  <button @click="eliminarUsuario(usuario)" class="action-button delete" title="Desactivar usuario">
                    <UserX :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="usuariosPaginados.length === 0" class="no-results">
          <SearchX class="no-results-icon" :size="48" />
          <p>No se encontraron usuarios</p>
          <small>Intenta con otros términos de búsqueda</small>
        </div>
      </div>

      <!-- Mostrando cantidad -->
      <div class="usuarios-count">
        <p>
          <Users :size="16" />
          Mostrando {{ usuariosPaginados.length }} de {{ usuariosFiltrados.length }} usuarios
        </p>
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

    <!-- Modal Registrar Usuario -->
    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModal" title="Cerrar formulario">
          <X :size="20" />
        </button>
        
        <RegistrarUsuario @usuario-registrado="refrescarUsuarios"/>
      </div>
    </div>

    <!-- Modal Editar Usuario -->
    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
        <ModificarUsuario 
          :usuario-id="usuarioEditando?.id" 
          @usuario-actualizado="usuarioActualizado"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import RegistrarUsuario from './RegistrarUsuario.vue'
import ModificarUsuario from './ModificarUsuario.vue'
import { 
  Users, UserPlus, Filter, List, Hash, Edit3, UserX, SearchX,
  ChevronLeft, ChevronRight, Trash2, X
} from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000'

const usuarios = ref([])
const roles = ref([])
const filtros = ref({ busqueda: '', rol: '', fechaDesde: '', fechaHasta: '' })

const pagina = ref(1)
const itemsPorPagina = 7
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const usuarioEditando = ref(null)
const hayAdminActivo = ref(false)

// Cargar usuarios desde backend
const cargarUsuarios = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    usuarios.value = res.data.sort((a, b) => {
      const fechaA = new Date(a.fecha_creacion || 0)
      const fechaB = new Date(b.fecha_creacion || 0)
      return fechaB - fechaA
    })
    
    hayAdminActivo.value = usuarios.value.some(
      u => u.rol_nombre?.toLowerCase() === 'administrador' && u.estado === 'ACTIVO'
    )
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
    alert('No se pudo cargar la lista de usuarios')
  }
}

// Cargar roles
const cargarRoles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    roles.value = res.data.filter(r => r.activo || r.nombre.toLowerCase() === 'administrador')
  } catch (err) {
    console.error('Error al cargar roles:', err)
  }
}

onMounted(async () => {
  await cargarUsuarios()
  await cargarRoles()
})

// Filtros por fecha
const filtrarPorFecha = (usuario) => {
  const fecha = usuario.fecha_creacion ? new Date(usuario.fecha_creacion) : null
  if (!fecha) return true
  if (filtros.value.fechaDesde && fecha < new Date(filtros.value.fechaDesde)) return false
  if (filtros.value.fechaHasta) {
    const hasta = new Date(filtros.value.fechaHasta)
    hasta.setDate(hasta.getDate() + 1)
    if (fecha >= hasta) return false
  }
  return true
}

// Filtrar usuarios
const usuariosFiltrados = computed(() => {
  const filtrados = usuarios.value.filter(u => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      (u.nombre?.toLowerCase().includes(busca) || 
       u.apellido?.toLowerCase().includes(busca) ||
       u.dni?.toLowerCase().includes(busca))
    const matchRol = !filtros.value.rol || (u.rol_id && u.rol_id == filtros.value.rol)
    const matchFecha = filtrarPorFecha(u)
    return matchBusqueda && matchRol && matchFecha
  })
  
  return filtrados.sort((a, b) => {
    if (a.estado === b.estado) return 0
    return a.estado === 'ACTIVO' ? -1 : 1
  })
})

// Paginación
const totalPaginas = computed(() => {
  return Math.max(1, Math.ceil(usuariosFiltrados.value.length / itemsPorPagina))
})

const usuariosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return usuariosFiltrados.value.slice(inicio, fin)
})

// Navegación paginación
const paginaAnterior = () => { 
  if (pagina.value > 1) pagina.value--
}

const paginaSiguiente = () => { 
  if (pagina.value < totalPaginas.value) pagina.value++
}

// Acciones sobre usuarios
const editarUsuario = (usuario) => {
  usuarioEditando.value = usuario
  mostrarEditar.value = true
}

const usuarioActualizado = async () => {
  await cargarUsuarios()
  cerrarModalEditar()
}

const eliminarUsuario = async (usuario) => {
  if (!confirm(`¿Desactivar al usuario ${usuario.nombre}?`)) return
  try {
    await axios.post(`${API_BASE}/usuarios/api/usuarios/eliminar/${usuario.id}/`)
    usuario.estado = 'INACTIVO'
    await nextTick()
    alert('Usuario desactivado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo desactivar el usuario')
  }
}

// Clases para estados
const getEstadoClass = (estado) => {
  const estadoLower = estado?.toLowerCase() || ''
  if (estadoLower === 'activo') return 'estado-success'
  if (estadoLower === 'inactivo') return 'estado-danger'
  return 'estado-secondary'
}

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = { busqueda: '', rol: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1
}

// Formato de fecha
const formatFecha = (fecha) => fecha ? new Date(fecha).toLocaleString() : '–'

// Cerrar modales
const cerrarModal = () => mostrarRegistrar.value = false

const cerrarModalEditar = () => {
  mostrarEditar.value = false
  usuarioEditando.value = null
}

// Refrescar usuarios 
const refrescarUsuarios = async (nuevoUsuario = null) => {
  if (nuevoUsuario) {
    await cargarUsuarios()
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
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - USUARIOS
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
}
</style>