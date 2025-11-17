<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Usuarios Registrados</h1>
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
            <label>Rol</label>
            <select v-model="filtros.rol" class="filter-input">
              <option value="">Todos</option>
              <option v-for="rol in roles" :key="rol.id" :value="rol.id">
                {{ rol.nombre }}
              </option>
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
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE
   ======================================== */

/* Tarjeta principal - Fondo oscuro elegante */
.list-card {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  color: #e5e5e5;
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6),
              0 0 0 1px rgba(100, 100, 100, 0.15) inset;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
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

/* BADGES DE ESTADO */
.badge-estado {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
}

.estado-warning {
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.estado-info {
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.estado-success {
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.estado-danger {
  background: linear-gradient(135deg, #3d3d3d, #2a2a2a);
  color: #ef4444;
  border: 2px solid #ef4444;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
  opacity: 0.75;
}

.estado-secondary {
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #9ca3af;
  border: 2px solid #9ca3af;
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* HEADER - Diseño masculino */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 2px solid rgba(14, 165, 233, 0.25);
  padding-bottom: 25px;
}

.header-content h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, #ffffff, #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.header-content p {
  color: #9ca3af;
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.5px;
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

/* FILTROS - Estilo industrial */
.filters-container {
  margin-bottom: 30px;
  background: rgba(0, 0, 0, 0.4);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(100, 100, 100, 0.2);
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
  color: #9ca3af;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}

.filter-input {
  padding: 12px 14px;
  border: 2px solid #374151;
  border-radius: 10px;
  background: #1a1a1a;
  color: #e5e5e5;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.filter-input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15);
  background: #252525;
}

.clear-filters-btn {
  background: linear-gradient(135deg, #4b5563, #374151);
  color: white;
  border: none;
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
  background: linear-gradient(135deg, #374151, #1f2937);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(75, 85, 99, 0.4);
}

/* TABLA - Diseño profesional */
.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: #1a1a1a;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(100, 100, 100, 0.2);
}

.users-table th {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  padding: 18px 14px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1.2px;
}

.users-table td {
  padding: 14px;
  border-bottom: 1px solid rgba(100, 100, 100, 0.12);
  vertical-align: middle;
  color: #d1d1d1;
  font-weight: 500;
}

.users-table td strong {
  color: #ffffff;
  font-weight: 800;
  letter-spacing: 0.3px;
}

.users-table tr:hover {
  background: rgba(14, 165, 233, 0.08);
  transition: all 0.2s ease;
}

/* BOTONES DE ACCIÓN */
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
  background: linear-gradient(135deg, #64748b, #475569);
  border: 1px solid rgba(100, 116, 139, 0.4);
}

.action-button.edit:hover {
  background: linear-gradient(135deg, #475569, #334155);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(100, 116, 139, 0.5);
}

.action-button.delete {
  background: linear-gradient(135deg, #3d3d3d, #2a2a2a);
  border: 1px solid rgba(239, 68, 68, 0.6);
  color: #ef4444;
}

.action-button.delete:hover {
  background: linear-gradient(135deg, #2a2a2a, #1a1a1a);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  border-color: #ef4444;
}

/* CONTADOR Y MENSAJES */
.usuarios-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0;
  padding: 18px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  flex-wrap: wrap;
  gap: 15px;
  border: 1px solid rgba(100, 100, 100, 0.2);
}

.usuarios-count p {
  color: #9ca3af;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* PAGINACIÓN */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
}

.pagination button {
  background: linear-gradient(135deg, #475569, #334155);
  color: white;
  border: 1px solid rgba(71, 85, 105, 0.5);
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
  gap: 6px;
}

.pagination button:hover:not(:disabled) {
  background: linear-gradient(135deg, #334155, #1e293b);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(71, 85, 105, 0.5);
}

.pagination button:disabled {
  background: #2d2d2d;
  color: #6b7280;
  cursor: not-allowed;
  transform: none;
  border: 1px solid rgba(107, 114, 128, 0.3);
  opacity: 0.5;
}

.pagination span {
  color: #e5e5e5;
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 0.95rem;
}

/* ESTADOS VACÍOS */
.no-results {
  text-align: center;
  padding: 80px;
  color: #9ca3af;
}

.no-results-icon {
  margin-bottom: 15px;
  opacity: 0.5;
  color: #9ca3af;
}

.no-results p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: #e5e5e5;
}

.no-results small {
  font-size: 0.9em;
  color: #9ca3af;
}

/* OVERLAY Y MODALES */
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
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7),
              0 0 0 1px rgba(14, 165, 233, 0.3);
  border: 2px solid rgba(14, 165, 233, 0.2);
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
  background: linear-gradient(135deg, #2d3748, #1a202c);
  border: 2px solid rgba(239, 68, 68, 0.6);
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #ef4444;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
  z-index: 1001;
  font-weight: 900;
  font-size: 1.2rem;
}

.modal-close:hover {
  transform: scale(1.15) rotate(90deg);
  box-shadow: 0 6px 25px rgba(239, 68, 68, 0.6);
  background: linear-gradient(135deg, #1a202c, #0f0f0f);
  border-color: #ef4444;
}

/* SCROLLBAR PERSONALIZADO */
.modal-content::-webkit-scrollbar,
.table-container::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.modal-content::-webkit-scrollbar-track,
.table-container::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 6px;
}

.modal-content::-webkit-scrollbar-thumb,
.table-container::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #475569, #334155);
  border-radius: 6px;
  border: 2px solid #1a1a1a;
}

.modal-content::-webkit-scrollbar-thumb:hover,
.table-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
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
  
  .filter-input {
    font-size: 0.9rem;
  }
  
  .badge-estado {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
}
</style>