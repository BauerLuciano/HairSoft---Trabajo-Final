<template>
  <div class="form-container">
    <h2>Registrar Nueva Marca</h2>
    <form @submit.prevent="registrarMarca" class="form">
      <div class="form-group">
        <label>Nombre de la Marca *</label>
        <input 
          v-model="formData.nombre" 
          type="text" 
          required 
          class="form-input" 
          placeholder="Ej: Loreal, Pantene..." 
          :disabled="cargando"
        />
        <small class="form-help">El nombre debe ser único</small>
      </div>
      
      <div class="form-buttons">
        <button type="submit" class="submit-button" :disabled="cargando || !formData.nombre.trim()">
          <CheckCircle :size="16" v-if="!cargando" />
          {{ cargando ? 'Registrando...' : 'Registrar Marca' }}
        </button>
        <button type="button" @click="$emit('cancelar')" class="cancel-button" :disabled="cargando">
          Cancelar
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { CheckCircle } from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000'
const emit = defineEmits(['marca-registrada', 'cancelar'])

const formData = ref({
  nombre: ''
})

const cargando = ref(false)

const registrarMarca = async () => {
  // Validación básica
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
    // IMPORTANTE: Enviar solo el campo 'nombre' según tu modelo
    const response = await axios.post(`${API_BASE}/usuarios/api/marcas/crear/`, {
      nombre: formData.value.nombre.trim()
    })
    
    if (response.data.id) {
      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: 'Marca registrada correctamente',
        confirmButtonColor: '#0ea5e9'
      })
      
      // Limpiar formulario
      formData.value = { nombre: '' }
      
      emit('marca-registrada')
    } else {
      throw new Error('No se recibió ID de la marca')
    }
  } catch (error) {
    console.error('Error al registrar marca:', error)
    
    let mensajeError = 'No se pudo registrar la marca'
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