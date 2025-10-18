<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Usuarios Registrados</h1>
          <p>Gestión completa de usuarios del sistema</p>
        </div>
        <button @click="irARegistrar" class="register-button">
          <span class="btn-text">➕ Registrar Usuario</span>
        </button>
      </div>

      <!-- Filtros Mejorados -->
      <div class="filters-container">
        <div class="filters-grid">
          <!-- Búsqueda general -->
          <div class="filter-group">
            <label>Buscar</label>
            <div class="input-with-icon">
              <input 
                v-model="filtros.busqueda" 
                type="text" 
                placeholder="Nombre o DNI..." 
                class="filter-input" 
              />
              <span class="input-icon">🔍</span>
            </div>
          </div>

          <!-- Filtro por rol -->
          <div class="filter-group">
            <label>Rol</label>
            <select v-model="filtros.rol" class="filter-select">
              <option value="">Todos los roles</option>
              <option value="ADMIN">Administrador</option>
              <option value="REC">Recepcionista</option>
              <option value="PEL">Peluquero</option>
              <option value="CLI">Cliente</option>
            </select>
          </div>

          <!-- Filtro por fecha desde -->
          <div class="filter-group">
            <label>Fecha desde</label>
            <input 
              v-model="filtros.fechaDesde" 
              type="date" 
              class="filter-input" 
            />
          </div>

          <!-- Filtro por fecha hasta -->
          <div class="filter-group">
            <label>Fecha hasta</label>
            <input 
              v-model="filtros.fechaHasta" 
              type="date" 
              class="filter-input" 
            />
          </div>

          <!-- Botón limpiar filtros DEBAJO de las fechas -->
          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              🗑️ Limpiar Filtros
            </button>
          </div>
        </div>
      </div>

      <!-- Tabla Mejorada -->
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
            <tr v-for="usuario in usuariosPaginados" :key="usuario.id" class="table-row">
              <td class="user-name">{{ usuario.nombre || '–' }}</td>
              <td>{{ usuario.apellido || '–' }}</td>
              <td class="user-dni">{{ usuario.dni || '–' }}</td>
              <td class="user-phone">{{ usuario.telefono || 'No registrado' }}</td>
              <td class="user-email">{{ usuario.correo || '–' }}</td>
              <td>
                <span class="role-badge" :class="getRoleClass(usuario.rol)">
                  {{ getRoleDisplayName(usuario.rol) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="getStatusClass(usuario.estado)">
                  {{ getStatusDisplayName(usuario.estado) }}
                </span>
              </td>
              <td class="fecha-registro">
                {{ formatFecha(usuario.fecha_creacion || usuario.created_at || usuario.fecha_registro) }}
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarUsuario(usuario)" class="action-button edit">
                    <span class="btn-icon">✏️</span>
                    Editar
                  </button>
                  <button @click="eliminarUsuario(usuario)" class="action-button delete">
                    <span class="btn-icon">🗑️</span>
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Mensaje cuando no hay resultados -->
        <div v-if="usuariosPaginados.length === 0" class="no-results">
          <p>No se encontraron usuarios con los filtros aplicados</p>
          <button @click="limpiarFiltros" class="clear-filters-btn">
            Limpiar filtros
          </button>
        </div>
      </div>

      <!-- Información de resultados DEBAJO de la tabla -->
      <div class="results-info">
        <p>Mostrando {{ usuariosPaginados.length }} de {{ usuariosFiltrados.length }} usuarios</p>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1" class="pagination-btn">
          <span class="btn-icon">←</span> Anterior
        </button>
        <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="pagination-btn">
          Siguiente <span class="btn-icon">→</span>
        </button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const API_BASE = 'http://127.0.0.1:8000'

// Lista de usuarios
const usuarios = ref([])

// Filtros
const filtros = ref({
  busqueda: '',
  rol: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Paginación
const pagina = ref(1)
const itemsPorPagina = 8

// Cargar usuarios desde el backend
const cargarUsuarios = async () => {
  try {
    const params = new URLSearchParams()
    if (filtros.value.busqueda) params.append('q', filtros.value.busqueda)
    if (filtros.value.rol) params.append('rol', filtros.value.rol)

    // Evitar caching
    params.append('_', new Date().getTime())

    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`, { params })
    usuarios.value = res.data
    console.log('Usuarios cargados:', usuarios.value)
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
    alert('No se pudo cargar la lista de usuarios')
  }
}

// Recargar cuando cambie la ruta
watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/usuarios') cargarUsuarios()
  },
  { immediate: true }
)

// Recargar cuando cambian los filtros
watch(
  filtros,
  () => {
    pagina.value = 1
    cargarUsuarios()
  },
  { deep: true }
)

// Filtrado por fecha
const filtrarPorFecha = (usuario) => {
  if (!filtros.value.fechaDesde && !filtros.value.fechaHasta) return true
  if (!usuario.fecha_creacion) return true

  const fechaUsuario = new Date(usuario.fecha_creacion)

  if (filtros.value.fechaDesde) {
    const desde = new Date(filtros.value.fechaDesde)
    if (fechaUsuario < desde) return false
  }

  if (filtros.value.fechaHasta) {
    const hasta = new Date(filtros.value.fechaHasta)
    hasta.setDate(hasta.getDate() + 1)
    if (fechaUsuario >= hasta) return false
  }

  return true
}

// Usuarios filtrados
const usuariosFiltrados = computed(() => {
  let filtered = usuarios.value

  // Filtro por búsqueda (nombre o DNI)
  if (filtros.value.busqueda) {
    const term = filtros.value.busqueda.toLowerCase()
    filtered = filtered.filter(u =>
      (u.nombre?.toLowerCase().includes(term)) ||
      (u.dni?.toLowerCase().includes(term))
    )
  }

  // Filtro por rol
  if (filtros.value.rol) {
    filtered = filtered.filter(u => (u.rol?.toUpperCase() || '') === filtros.value.rol)
  }

  // Filtro por fecha
  filtered = filtered.filter(filtrarPorFecha)

  console.log('Usuarios filtrados:', filtered)
  return filtered
})

// Paginación
const totalPaginas = computed(() => Math.ceil(usuariosFiltrados.value.length / itemsPorPagina))
const usuariosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  const paginados = usuariosFiltrados.value.slice(inicio, fin)
  console.log('Usuarios paginados:', paginados)
  return paginados
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Funciones auxiliares
const getRoleDisplayName = (rol) => {
  const roles = { 'ADMIN': 'Administrador', 'REC': 'Recepcionista', 'PEL': 'Peluquero', 'CLI': 'Cliente' }
  return roles[rol?.toUpperCase()] || rol || 'Sin rol'
}

// **Esta función faltaba**
const getRoleClass = (rol) => {
  switch ((rol || '').toUpperCase()) {
    case 'ADMIN': return 'role-admin'
    case 'REC':   return 'role-rec'
    case 'PEL':   return 'role-pel'
    case 'CLI':   return 'role-cli'
    default:      return ''
  }
}

const getStatusDisplayName = (estado) => {
  const estados = { 'ACTIVO': 'Activo', 'INACTIVO': 'Inactivo' }
  return estados[estado?.toUpperCase()] || 'Activo'
}

const getStatusClass = (estado) => (estado?.toLowerCase() === 'activo' ? 'activo' : 'inactivo')

// Acciones
const irARegistrar = () => router.push('/usuarios/crear')
const editarUsuario = (usuario) => router.push(`/usuarios/modificar/${usuario.id}`)
const eliminarUsuario = async (usuario) => {
  if (!confirm(`¿Desactivar al usuario ${usuario.nombre}?`)) return
  try {
    await axios.post(`${API_BASE}/usuarios/api/usuarios/eliminar/${usuario.id}/`)
    usuarios.value = usuarios.value.map(u => u.id === usuario.id ? { ...u, estado: 'INACTIVO' } : u)
    alert('Usuario desactivado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo desactivar el usuario')
  }
}

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = { busqueda: '', rol: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1
}

// Mostrar fecha bonita
const formatFecha = (fecha) => {
  if (!fecha) return '–'
  const d = new Date(fecha)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString()
}

// Montaje inicial
onMounted(() => {
  cargarUsuarios()
})

</script>

<style scoped>
/* Tarjeta principal */
.list-card {
  background: rgba(23, 23, 23, 0.8);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5),
              0 0 0 1px rgba(255,255,255,0.05) inset;
  position: relative;
  overflow: hidden;
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #6b7280, #9ca3af, #6b7280);
  border-radius: 24px 24px 0 0;
}

/* Botones específicos de esta tabla */
.action-buttons { display: flex; gap: 6px; flex-wrap: wrap; }
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
</style>