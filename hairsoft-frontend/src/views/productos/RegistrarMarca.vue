<template>
  <div class="user-form">
    <div class="form-card">
      <div class="form-header">
        <h1>Registrar Marca</h1>
        <p>Completa los datos de la nueva marca</p>
      </div>

      <form @submit.prevent="crearMarca" class="form-grid" autocomplete="off">
        <!-- Nombre de la Marca -->
        <div class="input-group">
          <label>Nombre <span class="required">*</span></label>
          <input 
            v-model="form.nombre" 
            type="text" 
            placeholder="Ingrese el nombre de la marca" 
            required 
            @input="validarNombre"
            @blur="mostrarErrorNombre"
          />
          <div class="error-message" v-if="errores.nombre">{{ errores.nombre }}</div>
        </div>

        <div class="full-width">
          <button type="submit" class="submit-btn">
            <span class="btn-text">Guardar Marca</span>
            <span class="btn-icon">→</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const emit = defineEmits(['marca-registrada'])

const form = ref({
  nombre: ''
})

const errores = ref({
  nombre: ''
})

// Validaciones
const validarNombre = () => {
  if (!form.value.nombre || form.value.nombre.length < 2) {
    errores.value.nombre = "El nombre debe tener al menos 2 caracteres"
  } else {
    errores.value.nombre = ""
  }
}

const mostrarErrorNombre = () => {
  if (!form.value.nombre) errores.value.nombre = "El nombre es obligatorio"
}

// Validar formulario completo
const validarFormulario = () => {
  validarNombre()
  return !errores.value.nombre
}

// Crear marca
const crearMarca = async () => {
  if (!validarFormulario()) {
    Swal.fire({
      icon: 'error',
      title: 'Formulario inválido',
      text: 'Por favor corrige los errores'
    })
    return
  }

  try {
    const res = await axios.post(`${API_BASE}/usuarios/api/marcas/crear/`, form.value)

    Swal.fire({
      icon: 'success',
      title: 'Marca registrada',
      text: 'La marca se creó correctamente'
    })

    form.value.nombre = ''
    emit('marca-registrada', res.data)

  } catch (err) {
    console.error(err)
    Swal.fire({
      icon: 'error',
      title: 'Error al crear marca',
      text: err.response?.data?.message || 'Ocurrió un error inesperado.'
    })
  }
}
</script>

<style scoped>
.user-form { display: flex; justify-content: center; align-items: center; }
.form-card {
  background: rgba(23,23,23,0.8);
  border: 2px solid #374151;
  border-radius: 20px;
  padding: 50px;
  max-width: 500px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05) inset;
  backdrop-filter: blur(10px);
}
.form-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #6b7280, #9ca3af, #6b7280);
  border-radius: 20px 20px 0 0;
}
.form-header { text-align: center; margin-bottom: 30px; }
.form-header h1 { color: #fff; margin-bottom: 10px; }
.form-header p { color: #d1d5db; }
.input-group { margin-bottom: 20px; }
.error-message { color: #f87171; font-size: 0.9rem; margin-top: 5px; }
.submit-btn { width: 100%; padding: 10px; background: #4f46e5; color: white; border: none; border-radius: 10px; cursor: pointer; font-size: 1rem; display: flex; justify-content: center; align-items: center; }
.submit-btn .btn-icon { margin-left: 8px; }
</style>
