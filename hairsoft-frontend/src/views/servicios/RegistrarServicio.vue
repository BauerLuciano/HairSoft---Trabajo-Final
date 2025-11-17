<template>
  <div class="registrar-servicio">
    <h1>{{ form.id ? 'Editar Servicio' : 'Registrar Servicio' }}</h1>

    <form @submit.prevent="guardarServicio">
      <div>
        <label>Nombre:</label>
        <input v-model="form.nombre" type="text">
        <span class="error">{{ errores.nombre }}</span>
      </div>

      <div>
        <label>Precio:</label>
        <input v-model.number="form.precio" type="number" min="0">
        <span class="error">{{ errores.precio }}</span>
      </div>

      <div>
        <label>Duración (min):</label>
        <input v-model.number="form.duracion" type="number" min="1">
      </div>

      <div>
        <label>Categoría:</label>
        <select v-model="form.categoria">
          <option value="">-- Seleccione --</option>
          <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
            {{ cat.nombre }}
          </option>
        </select>
      </div>

      <button type="submit">{{ form.id ? 'Actualizar' : 'Crear' }}</button>
      <button type="button" @click="resetForm">Cancelar</button>
    </form>
  </div>
</template>

<script setup>
import { reactive, watch, onMounted} from 'vue'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

const props = defineProps({
  servicioEditar: Object
})

const emit = defineEmits(['actualizar'])

const form = reactive({
  id: null,
  nombre: '',
  precio: 0,
  duracion: 20,
  categoria: null
})

const errores = reactive({
  nombre: '',
  precio: ''
})

const categorias = reactive([])

// Cargar categorías al montar
onMounted(async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/categorias/servicios/`)
    categorias.push(...res.data)
  } catch (err) {
    console.error('Error cargando categorías:', err)
  }
})

// Llenar formulario si se pasa un servicio para editar
watch(() => props.servicioEditar, (nuevo) => {
  if (nuevo) {
    form.id = nuevo.id
    form.nombre = nuevo.nombre
    form.precio = nuevo.precio
    form.duracion = nuevo.duracion || 20
    form.categoria = nuevo.categoria?.id || null
  }
})

const guardarServicio = async () => {
  errores.nombre = form.nombre.trim() === '' ? 'El nombre es obligatorio' : ''
  errores.precio = form.precio <= 0 ? 'El precio debe ser mayor que cero' : ''
  if (errores.nombre || errores.precio) return

  const payload = {
    nombre: form.nombre,
    precio: form.precio,
    duracion: form.duracion,
    categoria: form.categoria
  }

  try {
    if (form.id) {
      await axios.post(`${API_BASE}/usuarios/api/servicios/editar/${form.id}/`, payload)
      alert('✅ Servicio actualizado')
    } else {
      await axios.post(`${API_BASE}/usuarios/api/servicios/crear/`, payload)
      alert('✅ Servicio creado')
    }
    resetForm()
    emit('actualizar') // actualizar listado en componente padre
  } catch (err) {
    console.error('Error guardando servicio:', err)
    alert('❌ Ocurrió un error al guardar el servicio')
  }
}

const resetForm = () => {
  form.id = null
  form.nombre = ''
  form.precio = 0
  form.duracion = 20
  form.categoria = null
  errores.nombre = ''
  errores.precio = ''
}
</script>

<style scoped>
.error {
  color: red;
  font-size: 0.9em;
}
</style>
