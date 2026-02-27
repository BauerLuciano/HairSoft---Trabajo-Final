<template>
  <div class="registrar-categoria">
    <h1>{{ form.id ? 'Editar Categoría' : 'Registrar Categoría' }}</h1>

    <form @submit.prevent="guardarCategoria">
      <div>
        <label>Nombre:</label>
        <input v-model="form.nombre" type="text" />
        <span class="error">{{ errores.nombre }}</span>
      </div>

      <div>
        <label>Tipo:</label>
        <select v-model="form.tipo">
          <option value="">-- Seleccione --</option>
          <option value="Servicio">Servicio</option>
          <option value="Producto">Producto</option>
        </select>
        <span class="error">{{ errores.tipo }}</span>
      </div>

      <button type="submit">{{ form.id ? 'Actualizar' : 'Crear' }}</button>
      <button type="button" @click="resetForm">Cancelar</button>
    </form>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2' // ✅ NUEVO: Importamos SweetAlert

const API_BASE = 'http://127.0.0.1:8000'
const route = useRoute()
const router = useRouter()

const form = reactive({
  id: null,
  nombre: '',
  tipo: '' // 'Servicio' o 'Producto'
})

const errores = reactive({
  nombre: '',
  tipo: ''
})

// Si la ruta trae id, cargar categoría para editar
onMounted(async () => {
  const id = route.params.id
  if (id) {
    const tipo = route.query.tipo // pasamos ?tipo=Servicio o Producto
    if (!tipo) {
      Swal.fire('Error', 'Tipo de categoría requerido para editar', 'error')
      return router.push('/categorias')
    }
    form.id = id
    form.tipo = tipo

    try {
      const url = tipo === 'Servicio'
        ? `${API_BASE}/usuarios/api/categorias/servicios/`
        : `${API_BASE}/usuarios/api/categorias/productos/`
      const res = await axios.get(url)
      const cat = res.data.find(c => c.id == id)
      
      if (!cat) {
        Swal.fire('Error', 'Categoría no encontrada', 'error')
        return router.push('/categorias')
      }
      form.nombre = cat.nombre
    } catch (err) {
      console.error(err)
      Swal.fire('Error', 'Error cargando categoría', 'error')
    }
  }
})

const guardarCategoria = async () => {
  errores.nombre = form.nombre.trim() === '' ? 'El nombre es obligatorio' : ''
  errores.tipo = form.tipo === '' ? 'Debe seleccionar un tipo' : ''
  if (errores.nombre || errores.tipo) return

  const payload = { nombre: form.nombre }

  try {
    let url = ''
    if (form.id) {
      url = form.tipo === 'Servicio'
        ? `${API_BASE}/usuarios/api/categorias/servicios/editar/${form.id}/`
        : `${API_BASE}/usuarios/api/categorias/productos/editar/${form.id}/`
      await axios.post(url, payload)
      
      Swal.fire({
        icon: 'success',
        title: '¡Excelente!',
        text: 'Categoría actualizada con éxito'
      })
    } else {
      url = form.tipo === 'Servicio'
        ? `${API_BASE}/usuarios/api/categorias/servicios/crear/`
        : `${API_BASE}/usuarios/api/categorias/productos/crear/`
      await axios.post(url, payload)
      
      Swal.fire({
        icon: 'success',
        title: '¡Excelente!',
        text: 'Categoría creada con éxito'
      })
    }
    
    resetForm()
    router.push('/categorias')
    
  } catch (err) {
    console.error(err)
    
    // ✅ ATRAPAMOS EL MENSAJE DE PYTHON
    let mensajeError = 'Ocurrió un error al guardar la categoría.'

    if (err.response && err.response.data && err.response.data.message) {
      mensajeError = err.response.data.message
    }

    Swal.fire({
      icon: 'error',
      title: 'No se pudo guardar',
      text: mensajeError,
      confirmButtonColor: '#d33'
    })
  }
}

const resetForm = () => {
  form.id = null
  form.nombre = ''
  form.tipo = ''
  errores.nombre = ''
  errores.tipo = ''
}
</script>

<style scoped>
.error { color: red; font-size: 0.9em; }
</style>
