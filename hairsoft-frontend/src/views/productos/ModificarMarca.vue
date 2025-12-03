<template>
  <div class="form-container">
    <h2>Modificar Marca</h2>
    <form @submit.prevent="actualizarMarca" class="form">
      <div class="form-group">
        <label>Nombre de la Marca *</label>
        <input 
          v-model="formData.nombre" 
          type="text" 
          required 
          class="form-input" 
          placeholder="Nombre de la marca"
          :disabled="cargando"
        />
        <small class="form-help">ID: {{ props.marcaId }}</small>
      </div>
      
      <div class="form-buttons">
        <button type="submit" class="submit-button" :disabled="cargando || !formData.nombre.trim()">
          <CheckCircle :size="16" v-if="!cargando" />
          {{ cargando ? 'Actualizando...' : 'Actualizar Marca' }}
        </button>
        <button type="button" @click="$emit('cancelar')" class="cancel-button" :disabled="cargando">
          Cancelar
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { CheckCircle } from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000'
const props = defineProps({
  marcaId: {
    type: Number,
    required: true
  }
})
const emit = defineEmits(['marca-actualizada', 'cancelar'])

const formData = ref({
  nombre: ''
})

const cargando = ref(false)

const cargarMarca = async () => {
  cargando.value = true
  try {
    // Obtener todas las marcas y filtrar por ID
    const response = await axios.get(`${API_BASE}/usuarios/api/marcas/`)
    const marcas = response.data
    const marcaEncontrada = marcas.find(m => m.id === props.marcaId)
    
    if (marcaEncontrada) {
      formData.value = {
        nombre: marcaEncontrada.nombre || ''
      }
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo cargar la información de la marca',
        confirmButtonColor: '#0ea5e9'
      })
    }
  } catch (error) {
    console.error('Error al cargar marca:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar la información de la marca',
      confirmButtonColor: '#0ea5e9'
    })
  } finally {
    cargando.value = false
  }
}

const actualizarMarca = async () => {
  if (!formData.value.nombre.trim()) {
    Swal.fire({
      icon: 'warning',
      title: 'Campo requerido',
      text: 'El nombre de la marca es obligatorio',
      confirmButtonColor: '#0ea5e9'
    })
    return
  }
  
  cargando.value = true
  
  try {
    // Como no hay endpoint PUT/PATCH específico, usamos el mismo que crear pero con lógica diferente
    // O necesitarías crear un endpoint específico para editar marcas
    await axios.put(`${API_BASE}/usuarios/api/marcas/${props.marcaId}/`, {
      nombre: formData.value.nombre.trim()
    })
    
    Swal.fire({
      icon: 'success',
      title: '¡Éxito!',
      text: 'Marca actualizada correctamente',
      confirmButtonColor: '#0ea5e9'
    })
    
    emit('marca-actualizada')
  } catch (error) {
    console.error('Error al actualizar marca:', error)
    
    let mensajeError = 'No se pudo actualizar la marca'
    if (error.response?.data?.message) {
      mensajeError = error.response.data.message
    } else if (error.response?.data?.error) {
      mensajeError = error.response.data.error
    } else if (error.message) {
      mensajeError = error.message
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: mensajeError,
      confirmButtonColor: '#0ea5e9'
    })
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  cargarMarca()
})
</script>

<style scoped>
.form-container {
  padding: 40px;
  max-width: 500px;
  width: 100%;
}

h2 {
  margin: 0 0 30px 0;
  color: var(--text-primary);
  font-size: 1.8rem;
  font-weight: 800;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}

.form-input {
  padding: 14px 16px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-weight: 500;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

.form-help {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.form-buttons {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.submit-button {
  flex: 1;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 16px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.cancel-button {
  flex: 1;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  padding: 16px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
}

.cancel-button:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: var(--error-color);
  color: var(--error-color);
}

.cancel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>