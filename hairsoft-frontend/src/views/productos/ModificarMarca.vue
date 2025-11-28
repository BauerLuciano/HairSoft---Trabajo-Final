<template>
  <div class="form-container">
    <h2>Modificar Marca</h2>
    <form @submit.prevent="actualizarMarca" class="form">
      <div class="form-group">
        <label>Nombre de la Marca *</label>
        <input v-model="formData.nombre" type="text" required class="form-input"/>
      </div>
      
      <div class="form-buttons">
        <button type="submit" class="submit-button" :disabled="cargando">
          <CheckCircle :size="16" v-if="!cargando" />
          {{ cargando ? 'Actualizando...' : 'Actualizar Marca' }}
        </button>
        <button type="button" @click="$emit('cancelar')" class="cancel-button">
          Cancelar
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { CheckCircle } from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000'

export default {
  name: 'ModificarMarca',
  props: {
    marcaId: {
      type: Number,
      required: true
    }
  },
  emits: ['marca-actualizada', 'cancelar'],
  setup(props, { emit }) {
    const formData = ref({
      nombre: ''
    })
    const cargando = ref(false)

    const cargarMarca = async () => {
      try {
        const res = await axios.get(`${API_BASE}/usuarios/api/marcas/${props.marcaId}/`)
        formData.value = res.data
      } catch (error) {
        console.error('Error al cargar marca:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo cargar la información de la marca',
          confirmButtonColor: '#0ea5e9'
        })
      }
    }

    const actualizarMarca = async () => {
      cargando.value = true
      
      try {
        await axios.put(`${API_BASE}/usuarios/api/marcas/${props.marcaId}/`, formData.value)
        
        Swal.fire({
          icon: 'success',
          title: '¡Éxito!',
          text: 'Marca actualizada correctamente',
          confirmButtonColor: '#0ea5e9'
        })
        
        emit('marca-actualizada')
      } catch (error) {
        console.error('Error al actualizar marca:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.error || 'No se pudo actualizar la marca',
          confirmButtonColor: '#0ea5e9'
        })
      } finally {
        cargando.value = false
      }
    }

    onMounted(() => {
      cargarMarca()
    })

    return {
      formData,
      cargando,
      actualizarMarca
    }
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
