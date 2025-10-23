<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Roles</h1>
          <p>Gestión completa de los roles del sistema</p>
        </div>
        <button @click="irARegistrar" class="register-button">
          <span class="btn-text">➕ Registrar Rol</span>
        </button>
      </div>

      <!-- Filtros -->
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
              <span class="input-icon">🔍</span>
            </div>
          </div>
          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar Filtros</button>
          </div>
        </div>
      </div>

      <!-- Tabla de Roles -->
      <div class="table-container">
        <table class="users-table">
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
            <tr v-for="rol in rolesPaginados" :key="rol.id" class="table-row">
              <td>{{ rol.nombre || '–' }}</td>
              <td>{{ rol.descripcion || '–' }}</td>
              <td>
                <span v-if="rol.permisos && rol.permisos.length">
                  {{ rol.permisos.map(p => p.nombre).join(', ') }}
                </span>
                <span v-else>–</span>
              </td>
              <td>
                <span :class="['status-badge', getStatusClass(rol.activo)]">
                  {{ getStatusDisplayName(rol.activo) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarRol(rol)" class="action-button edit">✏️ Editar</button>
                  <button @click="eliminarRol(rol)" class="action-button delete">🗑️ Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="rolesPaginados.length === 0" class="no-results">
          <p>No se encontraron roles con los filtros aplicados</p>
          <button @click="limpiarFiltros" class="clear-filters-btn">Limpiar filtros</button>
        </div>
      </div>

      <!-- Información de resultados -->
      <div class="results-info">
        <p>Mostrando {{ rolesPaginados.length }} de {{ rolesFiltrados.length }} roles</p>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1" class="pagination-btn">← Anterior</button>
        <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="pagination-btn">Siguiente →</button>
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

const roles = ref([])
const filtros = ref({ busqueda: '' })
const pagina = ref(1)
const itemsPorPagina = 8

// Cargar roles desde backend
const cargarRoles = async () => {
  try {
    const params = new URLSearchParams()
    if (filtros.value.busqueda) params.append('q', filtros.value.busqueda)
    params.append('_', new Date().getTime())
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`, { params })
    roles.value = res.data
  } catch (err) {
    console.error(err)
    alert('No se pudieron cargar los roles')
  }
}

// Filtrado
const rolesFiltrados = computed(() => {
  if (!filtros.value.busqueda) return roles.value
  const term = filtros.value.busqueda.toLowerCase()
  return roles.value.filter(r => r.nombre?.toLowerCase().includes(term))
})

// Paginación
const totalPaginas = computed(() => Math.ceil(rolesFiltrados.value.length / itemsPorPagina))
const rolesPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return rolesFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Acciones
const irARegistrar = () => router.push({ path: '/roles/crear', query: { reload: new Date().getTime() } })
const editarRol = (rol) => router.push(`/roles/modificar/${rol.id}`)
const eliminarRol = async (rol) => {
  if (!confirm(`¿Eliminar el rol ${rol.nombre}?`)) return
  try {
    await axios.post(`${API_BASE}/usuarios/api/roles/eliminar/${rol.id}/`)
    roles.value = roles.value.filter(r => r.id !== rol.id)
    alert('Rol eliminado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo eliminar el rol')
  }
}

// Limpiar filtros
const limpiarFiltros = () => { filtros.value = { busqueda: '' }; pagina.value = 1 }

// Mostrar estado correctamente
const getStatusDisplayName = (estado) => (estado ? 'Activo' : 'Inactivo')
const getStatusClass = (estado) => (estado ? 'activo' : 'inactivo')

// Watchers
watch(filtros, () => { pagina.value = 1; cargarRoles() }, { deep: true })
watch(() => route.query.reload, () => { cargarRoles() })

onMounted(() => { cargarRoles() })
</script>

<style scoped>
.list-card { background: rgba(23,23,23,0.8); border-radius:24px; padding:40px; max-width:1200px; margin:auto; box-shadow:0 25px 50px rgba(0,0,0,0.5) }
.list-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px }
.filters-grid { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px }
.filter-group { display:flex; flex-direction:column }
.filter-input, .filter-select { padding:6px 10px; border-radius:6px; border:none }
.action-buttons { display:flex; gap:6px }
.action-button { padding:6px 12px; border:none; border-radius:6px; cursor:pointer; font-weight:600; display:flex; align-items:center; gap:4px }
.action-button.edit { background:#3b82f6; color:white }
.action-button.delete { background:#ef4444; color:white }
.status-badge { padding:2px 8px; border-radius:6px; font-size:0.8rem; color:white }
.status-badge.activo { background:green }
.table-container table { width:100%; border-collapse:collapse }
.table-container th, td { padding:10px; text-align:left; border-bottom:1px solid #ccc }
</style>
