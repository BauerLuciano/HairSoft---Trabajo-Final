<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Roles</h1>
          <p>Gestión completa de los roles del sistema</p>
        </div>
        <div class="header-buttons" style="display: flex; gap: 12px;">
          <button @click="irARegistrar" class="register-button">
            <Plus :size="18" />
            Registrar Rol
          </button>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          
          <div class="filter-group">
            <label>Buscar Rol</label>
            <div class="input-with-icon">
              <input
                v-model="filtros.busqueda"
                type="text"
                placeholder="Nombre del rol..."
                class="filter-input"
              />
              <Search class="input-icon" :size="16" />
            </div>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="todos">Todos</option>
              <option value="activos">Activos</option>
              <option value="inactivos">Inactivos</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              <Trash2 :size="16" />
              Limpiar
            </button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="roles-table">
          <thead>
            <tr>
              <th>Nombre del Rol</th>
              <th>Descripción</th>
              <th>Permisos</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rol in rolesPaginados" :key="rol.id" :class="{ 'row-inactive': !rol.activo }">
              <td><strong>{{ rol.nombre || '–' }}</strong></td>
              <td class="descripcion-cell">{{ rol.descripcion || 'Sin descripción' }}</td>
              <td>
                <div class="permisos-lista">
                  <div v-if="esCliente(rol.nombre)" class="badge-cliente">
                    <User :size="12" style="margin-right: 4px"/> Cliente Web
                  </div>
                  
                  <template v-else-if="getPermisosCount(rol) > 0">
                    <div v-for="(permiso, index) in getPrimerosPermisos(rol)" :key="index" 
                         class="permiso-item">
                      <span class="permiso-nombre">{{ permiso.nombre }}</span>
                    </div>
                    <div v-if="getPermisosCount(rol) > 3" class="mas-permisos">
                      +{{ getPermisosCount(rol) - 3 }} más...
                    </div>
                  </template>
                  
                  <div v-else class="sin-permisos">
                    Sin permisos asignados
                  </div>
                </div>
              </td>
              <td>
                <span class="badge-estado" :class="getEstadoClass(rol.activo)">
                  {{ getStatusDisplayName(rol.activo) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarRol(rol)" class="action-button edit" title="Editar rol">
                    <Edit3 :size="14" />
                  </button>
                  
                  <button 
                    @click="cambiarEstadoRol(rol)" 
                    class="action-button" 
                    :class="rol.activo ? 'delete' : 'success'" 
                    :title="rol.activo ? 'Desactivar rol' : 'Activar rol'"
                  >
                    <Power :size="14" v-if="rol.activo" />
                    <CheckCircle :size="14" v-else />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="rolesPaginados.length === 0" class="no-results">
          <Shield class="no-results-icon" :size="48" />
          <p>No se encontraron roles con los filtros aplicados</p>
          <small>Intenta con otros términos de búsqueda</small>
        </div>
      </div>

      <div class="roles-count">
        <p>
          <Shield :size="16" />
          Mostrando {{ rolesPaginados.length }} de {{ rolesFiltrados.length }} roles
        </p>
        <div class="alertas-container">
          <span v-if="rolesInactivos > 0" class="alerta-inactivo">
            <PowerOff :size="14" />
            {{ rolesInactivos }} roles inactivos
          </span>
        </div>
      </div>

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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/utils/axiosConfig' // Usamos tu config para mantener sesión
import Swal from 'sweetalert2'
import { 
  Shield, Plus, Edit3, Power, CheckCircle, PowerOff,
  ChevronLeft, ChevronRight, Trash2, Search, User
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const API_BASE = 'http://127.0.0.1:8000'

const roles = ref([])
const filtros = ref({ busqueda: '', estado: 'todos' })
const pagina = ref(1)
const itemsPorPagina = 8

// Cargar roles desde backend
const cargarRoles = async () => {
  try {
    const params = new URLSearchParams()
    if (filtros.value.busqueda) params.append('q', filtros.value.busqueda)
    params.append('_', new Date().getTime())
    
    // URL Correcta
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`, { params })
    roles.value = res.data
  } catch (err) {
    console.error('❌ Error al cargar roles:', err)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar la lista de roles',
      confirmButtonColor: '#0ea5e9'
    })
  }
}

// Helpers para permisos
const getPermisosCount = (rol) => {
  return rol.permisos && Array.isArray(rol.permisos) ? rol.permisos.length : 0
}

const getPrimerosPermisos = (rol) => {
  if (!rol.permisos || !Array.isArray(rol.permisos)) return []
  return rol.permisos.slice(0, 3)
}

const esCliente = (nombre) => {
  return nombre && nombre.toLowerCase().includes('cliente')
}

// Filtrado
const rolesFiltrados = computed(() => {
  let resultado = roles.value

  // 1. Filtro por Búsqueda
  if (filtros.value.busqueda) {
    const term = filtros.value.busqueda.toLowerCase()
    resultado = resultado.filter(r => r.nombre?.toLowerCase().includes(term))
  }

  // 2. Filtro por Estado
  if (filtros.value.estado === 'activos') {
    resultado = resultado.filter(r => r.activo)
  } else if (filtros.value.estado === 'inactivos') {
    resultado = resultado.filter(r => !r.activo)
  }

  return resultado
})

// Contadores
const rolesInactivos = computed(() => rolesFiltrados.value.filter(r => !r.activo).length)

// Paginación
const totalPaginas = computed(() => Math.max(1, Math.ceil(rolesFiltrados.value.length / itemsPorPagina)))
const rolesPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return rolesFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Acciones
const irARegistrar = () => router.push({ path: '/roles/crear', query: { reload: new Date().getTime() } })
const editarRol = (rol) => router.push(`/roles/modificar/${rol.id}`)

// 🔥 LÓGICA DE ACTIVAR/DESACTIVAR CORREGIDA
const cambiarEstadoRol = async (rol) => {
  const nuevoEstado = !rol.activo
  const accion = nuevoEstado ? 'activar' : 'desactivar'
  
  const result = await Swal.fire({
    title: `¿${accion.charAt(0).toUpperCase() + accion.slice(1)} rol?`,
    text: `¿Está seguro de ${accion} el rol "${rol.nombre}"?`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: nuevoEstado ? '#10b981' : '#ef4444', 
    cancelButtonColor: '#6b7280',
    confirmButtonText: `Sí, ${accion}`,
    cancelButtonText: 'Cancelar'
  })
  
  if (!result.isConfirmed) return
  
  try {
    // ✅ URL ARREGLADA: Faltaba '/usuarios' al principio
    await axios.patch(`${API_BASE}/usuarios/api/roles/${rol.id}/`, {
      activo: nuevoEstado
    })
    
    // Actualizamos localmente para feedback instantáneo
    rol.activo = nuevoEstado
    
    Swal.fire({
      icon: 'success',
      title: '¡Éxito!',
      text: `Rol ${accion}do correctamente`,
      confirmButtonColor: '#0ea5e9',
      timer: 1500,
      showConfirmButton: false
    })
  } catch (err) { 
    console.error(err)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: `No se pudo ${accion} el rol.`,
      confirmButtonColor: '#0ea5e9'
    })
    // Recargamos por si acaso hubo desincronización
    await cargarRoles()
  }
}

// Limpiar filtros
const limpiarFiltros = () => { 
  filtros.value = { busqueda: '', estado: 'todos' }
  pagina.value = 1 
}

const getStatusDisplayName = (estado) => (estado ? 'Activo' : 'Inactivo')
const getEstadoClass = (estado) => estado ? 'estado-success' : 'estado-danger'

watch(filtros, () => { pagina.value = 1 }, { deep: true })
watch(() => route.query.reload, () => { cargarRoles() })

onMounted(() => { cargarRoles() })
</script>

<style scoped>
/* ========================================
   🔥 TUS ESTILOS ORIGINALES (INTACTOS)
   ======================================== */

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

.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* Efecto visual para filas inactivas */
.row-inactive {
  opacity: 0.6;
  background-color: rgba(255, 255, 255, 0.02);
}

.badge-cliente {
  display: inline-flex;
  align-items: center;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid #3b82f6;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

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

.filters-container {
  margin-bottom: 30px;
  background: var(--hover-bg);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-input {
  padding: 12px 14px 12px 40px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: var(--text-tertiary);
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
  display: flex;
  align-items: center;
  gap: 6px;
}

.clear-filters-btn:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
}

.roles-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

.roles-table th {
  background: var(--accent-color);
  color: white;
  padding: 18px 14px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1.2px;
}

.roles-table tr {
  border-bottom: 1px solid var(--border-color);
}

.roles-table td {
  padding: 14px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-weight: 500;
}

.roles-table td strong {
  color: var(--text-primary);
  font-weight: 800;
  letter-spacing: 0.3px;
}

.roles-table tr:hover {
  background: var(--hover-bg);
  transition: all 0.2s ease;
}

.descripcion-cell {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.permisos-lista {
  max-width: 300px;
}

.permiso-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid var(--border-color);
}

.permiso-item:last-child {
  border-bottom: none;
}

.permiso-nombre {
  color: var(--text-primary);
  font-size: 0.85rem;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.mas-permisos {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-style: italic;
  text-align: center;
  padding: 4px 0;
  background: var(--hover-bg);
  border-radius: 4px;
  margin-top: 4px;
}

.sin-permisos {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-style: italic;
  text-align: center;
  padding: 8px 0;
}

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

.roles-count {
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

.roles-count p {
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

.table-container::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.table-container::-webkit-scrollbar-track {
  background: var(--bg-primary);
  border-radius: 6px;
}

.table-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 6px;
  border: 2px solid var(--bg-primary);
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

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
  
  .roles-table {
    font-size: 0.85rem;
  }
  
  .roles-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 6px;
  }
  
  .roles-count {
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
  
  .roles-table {
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
  
  .permisos-lista {
    max-width: 200px;
  }
}
</style>