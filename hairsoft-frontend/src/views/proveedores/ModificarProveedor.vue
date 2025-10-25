<template>
  <div class="form-container">
    <h2>Modificar Proveedor</h2>
    
    <form @submit.prevent="modificarProveedor" class="proveedor-form">
      <div class="form-grid">
        <!-- Información Básica -->
        <div class="form-section">
          <h3>Información Básica</h3>
          
          <div class="form-group">
            <label for="nombre">Nombre del Proveedor *</label>
            <input
              id="nombre"
              v-model="proveedor.nombre"
              type="text"
              required
              placeholder="Ingrese el nombre del proveedor"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="contacto">Persona de Contacto</label>
            <input
              id="contacto"
              v-model="proveedor.contacto"
              type="text"
              placeholder="Nombre del contacto principal"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="productos_que_ofrece">Productos que Ofrece *</label>
            <textarea
              id="productos_que_ofrece"
              v-model="proveedor.productos_que_ofrece"
              rows="3"
              required
              placeholder="Lista de productos que provee"
              class="form-textarea"
            ></textarea>
          </div>
        </div>

        <!-- Contacto -->
        <div class="form-section">
          <h3>Información de Contacto</h3>
          
          <div class="form-group">
            <label for="telefono">Teléfono *</label>
            <input
              id="telefono"
              v-model="proveedor.telefono"
              type="tel"
              required
              placeholder="Número de teléfono"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="proveedor.email"
              type="email"
              placeholder="correo@proveedor.com"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="direccion">Dirección</label>
            <textarea
              id="direccion"
              v-model="proveedor.direccion"
              rows="2"
              placeholder="Dirección completa del proveedor"
              class="form-textarea"
            ></textarea>
          </div>

          <div class="form-group">
            <label for="estado">Estado *</label>
            <select
              id="estado"
              v-model="proveedor.estado"
              required
              class="form-select"
            >
              <option value="ACTIVO">Activo</option>
              <option value="INACTIVO">Inactivo</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Botones -->
      <div class="form-actions">
        <button type="button" @click="cancelar" class="btn btn-secondary">
          Cancelar
        </button>
        <button type="submit" :disabled="cargando" class="btn btn-primary">
          {{ cargando ? 'Actualizando...' : 'Actualizar Proveedor' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  proveedorId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['proveedor-actualizado', 'cancelar'])

const API_BASE = 'http://127.0.0.1:8000'

const proveedor = ref({
  nombre: '',
  contacto: '',
  telefono: '',
  email: '',
  direccion: '',
  productos_que_ofrece: '',
  estado: 'ACTIVO'
})

const cargando = ref(false)

// Cargar datos del proveedor
const cargarProveedor = async () => {
  try {
    const response = await axios.get(`${API_BASE}/usuarios/api/proveedores/${props.proveedorId}/`)
    proveedor.value = response.data
  } catch (err) {
    console.error('Error al cargar proveedor:', err)
    alert('Error al cargar los datos del proveedor')
  }
}

const modificarProveedor = async () => {
  if (!validarProveedor()) return
  
  cargando.value = true
  try {
    await axios.put(`${API_BASE}/proveedores/api/proveedores/${props.proveedorId}/`, proveedor.value)
    alert('Proveedor actualizado con éxito')
    emit('proveedor-actualizado')
  } catch (err) {
    console.error('Error al actualizar proveedor:', err)
    if (err.response?.status === 400 && err.response?.data?.nombre) {
      alert('Error: Ya existe un proveedor con ese nombre')
    } else {
      alert('Error al actualizar el proveedor: ' + (err.response?.data?.message || err.message))
    }
  } finally {
    cargando.value = false
  }
}

const validarProveedor = () => {
  if (!proveedor.value.nombre.trim()) {
    alert('El nombre del proveedor es obligatorio')
    return false
  }
  if (!proveedor.value.telefono.trim()) {
    alert('El teléfono es obligatorio')
    return false
  }
  if (!proveedor.value.productos_que_ofrece.trim()) {
    alert('Los productos que ofrece son obligatorios')
    return false
  }
  return true
}

const cancelar = () => {
  emit('cancelar')
}

onMounted(() => {
  cargarProveedor()
})

// Recargar proveedor cuando cambie el ID
watch(() => props.proveedorId, () => {
  if (props.proveedorId) {
    cargarProveedor()
  }
})
</script>

<style scoped>
.form-container {
  background: rgba(23, 23, 23, 0.95);
  border-radius: 16px;
  padding: 30px;
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: white;
  margin-bottom: 30px;
  text-align: center;
  font-size: 1.8rem;
}

h3 {
  color: #9ca3af;
  margin-bottom: 20px;
  font-size: 1.2rem;
  border-bottom: 1px solid #374151;
  padding-bottom: 8px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.form-section {
  background: rgba(31, 41, 55, 0.3);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #d1d5db;
  font-weight: 500;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #4b5563;
  border-radius: 8px;
  background: rgba(17, 24, 39, 0.8);
  color: white;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #374151;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: white;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #4b5563, #374151);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .form-container {
    padding: 20px;
  }
}
</style>