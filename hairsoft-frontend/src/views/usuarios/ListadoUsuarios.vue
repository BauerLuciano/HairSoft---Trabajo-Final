<template>
  <div class="list-container">
    <div class="list-card">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Usuarios Registrados</h1>
          <p>Gestión de usuarios del sistema</p>
        </div>
        <button @click="irARegistrar" class="register-button">➕ Registrar Usuario</button>
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
            <select v-model="filtros.rol" class="filter-select">
              <option value="">Todos</option>
              <option v-for="rol in roles" :key="rol.id" :value="rol.id">{{ rol.nombre }}</option>
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

      <!-- Tabla -->
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
              <td>{{ usuario.nombre || '–' }}</td>
              <td>{{ usuario.apellido || '–' }}</td>
              <td>{{ usuario.dni || '–' }}</td>
              <td>{{ usuario.telefono || 'No registrado' }}</td>
              <td>{{ usuario.correo || '–' }}</td>
              <td><span class="role-badge">{{ usuario.rol_nombre || 'Sin rol' }}</span></td>
              <td><span :class="usuario.estado.toLowerCase()">{{ usuario.estado }}</span></td>
              <td>{{ formatFecha(usuario.fecha_creacion) }}</td>
              <td>
                <button @click="editarUsuario(usuario)">✏️</button>
                <button @click="eliminarUsuario(usuario)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="usuariosPaginados.length === 0" class="no-results">
          <p>No se encontraron usuarios</p>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">← Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente →</button>
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

const usuarios = ref([])
const roles = ref([])
const filtros = ref({ busqueda: '', rol: '', fechaDesde: '', fechaHasta: '' })

const pagina = ref(1)
const itemsPorPagina = 8

const cargarUsuarios = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    usuarios.value = res.data
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
    alert('No se pudo cargar la lista de usuarios')
  }
}

const cargarRoles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    roles.value = res.data.filter(r => r.activo)
  } catch (err) {
    console.error('Error al cargar roles:', err)
  }
}

onMounted(async () => {
  await cargarUsuarios()
  await cargarRoles()
})

// Filtros
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

const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(u => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || u.nombre.toLowerCase().includes(busca) || u.dni.toLowerCase().includes(busca)
    const matchRol = !filtros.value.rol || (u.rol && u.rol.id == filtros.value.rol)
    const matchFecha = filtrarPorFecha(u)
    return matchBusqueda && matchRol && matchFecha
  })
})

const totalPaginas = computed(() => Math.ceil(usuariosFiltrados.value.length / itemsPorPagina))
const usuariosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return usuariosFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

// Paginación
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Acciones
const irARegistrar = () => router.push('/usuarios/crear')
const editarUsuario = (usuario) => router.push(`/usuarios/modificar/${usuario.id}`)
const eliminarUsuario = async (usuario) => {
  if (!confirm(`¿Desactivar al usuario ${usuario.nombre}?`)) return
  try {
    await axios.post(`${API_BASE}/usuarios/api/usuarios/eliminar/${usuario.id}/`)
    usuario.estado = 'INACTIVO'
    alert('Usuario desactivado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo desactivar el usuario')
  }
}

const limpiarFiltros = () => {
  filtros.value = { busqueda: '', rol: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1
}

const formatFecha = (fecha) => fecha ? new Date(fecha).toLocaleString() : '–'

// Recargar página si cambian los filtros
watch(filtros, () => pagina.value = 1, { deep: true })
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