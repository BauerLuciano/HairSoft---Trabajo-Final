<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Servicios</h1>
          <p>Gestión completa de servicios de la peluquería</p>
        </div>
        <button @click="irARegistrar" class="register-button">
          <span class="btn-text">➕ Registrar Servicio</span>
        </button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <div class="input-with-icon">
              <input 
                v-model="filtroBusqueda" 
                type="text" 
                placeholder="Nombre del servicio..." 
                class="filter-input" 
              />
              <span class="input-icon">🔍</span>
            </div>
          </div>
          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              🗑️ Limpiar filtros
            </button>
          </div>
        </div>
      </div>

      <!-- Tabla -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Precio</th>
              <th>Duración</th>
              <th>Categoría</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in serviciosPaginados" :key="s.id">
              <td>{{ s.nombre }}</td>
              <td>${{ s.precio }}</td>
              <td>{{ s.duracion || 20 }} min</td>
              <td>{{ s.categoria || '–' }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="editarServicio(s)" class="action-button edit">
                    ✏️ Editar
                  </button>
                  <button @click="eliminarServicio(s.id)" class="action-button delete">
                    🗑️ Eliminar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="serviciosPaginados.length === 0" class="no-results">
          <p>No se encontraron servicios con los filtros aplicados</p>
          <button @click="limpiarFiltros" class="clear-filters-btn">Limpiar filtros</button>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1" class="pagination-btn">
          ← Anterior
        </button>
        <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="pagination-btn">
          Siguiente →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

// Lista de servicios
const servicios = ref([])
const filtroBusqueda = ref('')

// Paginación
const pagina = ref(1)
const itemsPorPagina = 8

const cargarServicios = async () => {
  try {
    const params = new URLSearchParams()
    if (filtroBusqueda.value) params.append('q', filtroBusqueda.value)
    params.append('_', new Date().getTime())
    
    const res = await axios.get(`${API_BASE}/usuarios/api/servicios/`, { params })
    servicios.value = res.data
  } catch (err) {
    console.error('Error al cargar servicios:', err)
    alert('No se pudo cargar la lista de servicios')
  }
}

// Filtrado local
const serviciosFiltrados = computed(() => {
  let filtered = servicios.value
  if (filtroBusqueda.value) {
    const term = filtroBusqueda.value.toLowerCase()
    filtered = filtered.filter(s => s.nombre?.toLowerCase().includes(term))
  }
  return filtered
})

// Paginación
const totalPaginas = computed(() => Math.ceil(serviciosFiltrados.value.length / itemsPorPagina))
const serviciosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return serviciosFiltrados.value.slice(inicio, fin)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

const limpiarFiltros = () => {
  filtroBusqueda.value = ''
  pagina.value = 1
  cargarServicios()
}

// Acciones
const irARegistrar = () => router.push('/servicios/crear')
const editarServicio = (s) => router.push(`/servicios/modificar/${s.id}`)
const eliminarServicio = async (id) => {
  if (!confirm('¿Seguro que quieres eliminar este servicio?')) return
  try {
    await axios.post(`${API_BASE}/usuarios/api/servicios/eliminar/${id}/`)
    alert('Servicio eliminado con éxito')
    cargarServicios()
  } catch (err) {
    console.error(err)
    alert('No se pudo eliminar el servicio')
  }
}

// Montaje inicial
onMounted(() => cargarServicios())

watch(filtroBusqueda, () => { pagina.value = 1 })
</script>

<style scoped>
.list-card { padding: 40px; border-radius: 24px; background: #111; color: white; max-width: 1400px; margin: auto; }
.table-container { margin-top: 20px; overflow-x: auto; }
.users-table { width: 100%; border-collapse: collapse; }
.users-table th, .users-table td { padding: 10px; border-bottom: 1px solid #333; text-align: left; }
.action-buttons { display: flex; gap: 6px; }
.action-button { padding: 6px 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
.action-button.edit { background: #3b82f6; color: white; }
.action-button.delete { background: #ef4444; color: white; }
.register-button { padding: 10px 20px; background: #10b981; color: white; border-radius: 12px; cursor: pointer; }
.filters-container { margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
.filter-input { padding: 6px 12px; border-radius: 8px; border: none; width: 200px; }
.clear-filters-btn { background: #f59e0b; color: white; border-radius: 8px; padding: 6px 12px; cursor: pointer; }
.pagination { display: flex; justify-content: center; gap: 12px; margin-top: 20px; }
.pagination-btn { padding: 6px 12px; border-radius: 8px; border: none; cursor: pointer; background: #3b82f6; color: white; }
</style>
