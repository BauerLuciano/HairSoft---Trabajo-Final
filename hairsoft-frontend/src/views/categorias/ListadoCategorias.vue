<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Categorías</h1>
          <p>Gestión completa de categorías de servicios y productos</p>
        </div>
        <button @click="abrirModalCrear" class="register-button">
          <span class="btn-text">➕ Registrar Categoría</span>
        </button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" type="text" placeholder="Nombre..." class="filter-input" />
          </div>
          <div class="filter-group">
            <label>Tipo</label>
            <select v-model="filtros.tipo" class="filter-select">
              <option value="">Todos</option>
              <option value="Servicio">Servicio</option>
              <option value="Producto">Producto</option>
            </select>
          </div>
          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar Filtros</button>
          </div>
        </div>
      </div>

      <!-- Tabla -->
      <div class="table-container">
        <table class="categories-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Tipo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in categoriasPaginadas" :key="cat.id">
              <td>{{ cat.nombre }}</td>
              <td>{{ cat.descripcion }}</td>
              <td>{{ cat.tipo }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="abrirModalEditar(cat)" class="action-button edit">✏️ Editar</button>
                  <button @click="eliminarCategoria(cat)" class="action-button delete">🗑️ Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="categoriasPaginadas.length === 0" class="no-results">
          <p>No se encontraron categorías</p>
          <button @click="limpiarFiltros" class="clear-filters-btn">Limpiar filtros</button>
        </div>
      </div>

      <!-- Información de resultados -->
      <div class="results-info">
        <p>Mostrando {{ categoriasPaginadas.length }} de {{ categoriasFiltradas.length }} categorías</p>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1" class="pagination-btn">← Anterior</button>
        <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="pagination-btn">Siguiente →</button>
      </div>
    </div>

    <!-- Modal de creación/edición -->
    <div v-if="modalVisible" class="modal-backdrop">
      <div class="modal-card">
        <h2>{{ form.id ? 'Editar Categoría' : 'Registrar Categoría' }}</h2>
        <form @submit.prevent="guardarCategoria">
          <div>
            <label>Nombre:</label>
            <input v-model="form.nombre" type="text" />
            <span class="error">{{ errores.nombre }}</span>
          </div>
          <div>
            <label>Descripción:</label>
            <input v-model="form.descripcion" type="text" />
          </div>
          <div>
            <label>Tipo:</label>
            <select v-model="form.tipo">
              <option value="">-- Seleccione --</option>
              <option value="Servicio">Servicio</option>
              <option value="Producto">Producto</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="submit">{{ form.id ? 'Actualizar' : 'Crear' }}</button>
            <button type="button" @click="cerrarModal">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

// Datos
const categorias = ref([])

// Filtros
const filtros = ref({ busqueda: '', tipo: '' })

// Paginación
const pagina = ref(1)
const itemsPorPagina = 8

// Modal y formulario
const modalVisible = ref(false)
const form = reactive({ id: null, nombre: '', descripcion: '', tipo: '' })
const errores = reactive({ nombre: '' })

// Cargar categorías
const cargarCategorias = async () => {
  try {
    const resServicios = await axios.get(`${API_BASE}/usuarios/api/categorias/servicios/`)
    const resProductos = await axios.get(`${API_BASE}/usuarios/api/categorias/productos/`)
    categorias.value = [
      ...resServicios.data.map(c => ({ ...c, tipo: 'Servicio' })),
      ...resProductos.data.map(c => ({ ...c, tipo: 'Producto' }))
    ]
  } catch (err) {
    console.error(err)
    alert('No se pudieron cargar las categorías')
  }
}

// Filtros computados
const categoriasFiltradas = computed(() => {
  let filtered = categorias.value
  if (filtros.value.busqueda) {
    const term = filtros.value.busqueda.toLowerCase()
    filtered = filtered.filter(c => c.nombre.toLowerCase().includes(term))
  }
  if (filtros.value.tipo) filtered = filtered.filter(c => c.tipo === filtros.value.tipo)
  return filtered
})

// Paginación computada
const totalPaginas = computed(() => Math.ceil(categoriasFiltradas.value.length / itemsPorPagina))
const categoriasPaginadas = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return categoriasFiltradas.value.slice(inicio, inicio + itemsPorPagina)
})

// Paginación
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// Acciones modal
const abrirModalCrear = () => {
  form.id = null
  form.nombre = ''
  form.descripcion = ''
  form.tipo = ''
  errores.nombre = ''
  modalVisible.value = true
}

const abrirModalEditar = (cat) => {
  form.id = cat.id
  form.nombre = cat.nombre
  form.descripcion = cat.descripcion
  form.tipo = cat.tipo
  errores.nombre = ''
  modalVisible.value = true
}

const cerrarModal = () => { modalVisible.value = false }

// Guardar categoría
const guardarCategoria = async () => {
  errores.nombre = form.nombre.trim() === '' ? 'El nombre es obligatorio' : ''
  if (errores.nombre) return

  try {
    let url = ''
    if (form.tipo === 'Servicio') {
      url = form.id
        ? `${API_BASE}/usuarios/api/categorias/servicios/editar/${form.id}/`
        : `${API_BASE}/usuarios/api/categorias/servicios/crear/`
    } else {
      url = form.id
        ? `${API_BASE}/usuarios/api/categorias/productos/editar/${form.id}/`
        : `${API_BASE}/usuarios/api/categorias/productos/crear/`
    }
    await axios.post(url, { nombre: form.nombre, descripcion: form.descripcion })
    alert(`✅ Categoría ${form.id ? 'actualizada' : 'creada'}`)
    cerrarModal()
    cargarCategorias()
  } catch (err) {
    console.error(err)
    alert('❌ Error al guardar la categoría')
  }
}

// Eliminar
const eliminarCategoria = async (cat) => {
  if (!confirm(`¿Eliminar categoría "${cat.nombre}"?`)) return
  try {
    const url = cat.tipo === 'Servicio'
      ? `${API_BASE}/usuarios/api/categorias/servicios/eliminar/${cat.id}/`
      : `${API_BASE}/usuarios/api/categorias/productos/eliminar/${cat.id}/`
    await axios.post(url)
    categorias.value = categorias.value.filter(c => c.id !== cat.id)
    alert('Categoría eliminada')
  } catch (err) {
    console.error(err)
    alert('No se pudo eliminar la categoría')
  }
}

// Limpiar filtros
const limpiarFiltros = () => { filtros.value = { busqueda: '', tipo: '' }; pagina.value = 1 }

onMounted(() => cargarCategorias())
watch(filtros, () => { pagina.value = 1 }, { deep: true })
</script>

<style scoped>
.list-card { 
  background: rgba(23,23,23,0.8); border-radius: 24px; padding: 40px; 
  max-width: 1200px; margin: auto; box-shadow: 0 25px 50px rgba(0,0,0,0.5);
}
.action-buttons { display: flex; gap: 6px; }
.action-button { padding: 6px 12px; border: none; border-radius: 8px; cursor: pointer; }
.action-button.edit { background: linear-gradient(135deg,#3b82f6,#1d4ed8); color: white; }
.action-button.delete { background: linear-gradient(135deg,#ef4444,#dc2626); color: white; }

/* Modal */
.modal-backdrop { position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:999; }
.modal-card { background:#171717; padding:30px; border-radius:16px; max-width:400px; width:100%; }
.modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:15px; }
.error { color:red; font-size:0.9em; }
</style>
