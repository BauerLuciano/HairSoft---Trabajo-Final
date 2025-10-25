<template>
  <div class="form-card">
    <div class="form-header">
      <h1>Registrar Proveedor</h1>
      <p>Completa los datos del proveedor</p>
    </div>

    <form @submit.prevent="registrarProveedor" class="form-grid" autocomplete="off">
      <!-- Nombre -->
      <div class="input-group">
        <label>Nombre del Proveedor <span class="required">*</span></label>
        <input 
          v-model="proveedor.nombre" 
          type="text" 
          placeholder="Ingrese el nombre del proveedor" 
          required 
        />
      </div>

      <!-- Contacto -->
      <div class="input-group">
        <label>Persona de Contacto</label>
        <input 
          v-model="proveedor.contacto" 
          type="text" 
          placeholder="Nombre del contacto principal" 
        />
      </div>

      <!-- Teléfono -->
      <div class="input-group">
        <label>Teléfono <span class="required">*</span></label>
        <input 
          v-model="proveedor.telefono" 
          type="tel" 
          placeholder="Número de teléfono" 
          required 
        />
      </div>

      <!-- Email -->
      <div class="input-group">
        <label>Email</label>
        <input 
          v-model="proveedor.email" 
          type="email" 
          placeholder="correo@proveedor.com" 
        />
      </div>

      <!-- Dirección -->
      <div class="input-group">
        <label>Dirección</label>
        <input 
          v-model="proveedor.direccion" 
          type="text" 
          placeholder="Dirección del proveedor" 
        />
      </div>

      <!-- Categorías que Ofrece -->
      <div class="input-group full-width">
        <label>Categorías que Ofrece</label>
        <div class="categorias-grid">
          <label v-for="categoria in categorias" :key="categoria.id" class="checkbox-label">
            <input 
              type="checkbox" 
              :value="categoria.id" 
              v-model="proveedor.categorias_seleccionadas"
              class="checkbox-input"
            />
            <span class="checkbox-custom"></span>
            {{ categoria.nombre }}
          </label>
        </div>
      </div>

      <!-- Productos Específicos -->
      <div class="input-group full-width">
        <label>Productos Específicos (Opcional)</label>
        <textarea 
          v-model="proveedor.productos_especificos" 
          rows="3" 
          placeholder="Lista de productos específicos que ofrece..."
          class="form-textarea"
        ></textarea>
      </div>

      <!-- Botones -->
      <div class="full-width form-actions">
        <button type="button" @click="volver" class="btn btn-secondary">
          ← Volver
        </button>
        <button type="submit" :disabled="cargando" class="btn btn-primary">
          {{ cargando ? 'Registrando...' : 'Guardar Proveedor' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['proveedor-registrado', 'cancelar'])

const API_BASE = 'http://127.0.0.1:8000'

const proveedor = reactive({
  nombre: '',
  contacto: '',
  telefono: '',
  email: '',
  direccion: '',
  categorias_seleccionadas: [],
  productos_especificos: ''
})

const categorias = ref([])
const cargando = ref(false)

// Cargar categorías de tipo PRODUCTO
// Cargar categorías de productos
const cargarCategorias = async () => {
  try {
    // USAR ESTE ENDPOINT - el que existe en tus URLs
    const res = await axios.get(`${API_BASE}/usuarios/api/categorias/productos/`)
    categorias.value = res.data
  } catch (err) {
    console.error('Error al cargar categorías:', err)
    // Si falla, dejamos el array vacío en lugar de hardcodear
    categorias.value = []
    alert('No se pudieron cargar las categorías. Intente nuevamente.')
  }
}

const registrarProveedor = async () => {
  if (!validarProveedor()) return
  
  cargando.value = true
  try {
    const payload = {
      nombre: proveedor.nombre.trim(),
      contacto: proveedor.contacto.trim(),
      telefono: proveedor.telefono.trim(),
      email: proveedor.email.trim(),
      direccion: proveedor.direccion.trim(),
      categorias: proveedor.categorias_seleccionadas,
      productos_especificos: proveedor.productos_especificos.trim()
    }

    const response = await axios.post(`${API_BASE}/usuarios/api/proveedores/`, payload)
    alert('✅ Proveedor registrado con éxito')
    
    resetForm()
    emit('proveedor-registrado', response.data)
    
  } catch (err) {
    console.error('Error al registrar proveedor:', err)
    if (err.response?.status === 400 && err.response?.data?.nombre) {
      alert('❌ Error: Ya existe un proveedor con ese nombre')
    } else {
      alert('❌ Error al registrar el proveedor: ' + (err.response?.data?.message || err.message))
    }
  } finally {
    cargando.value = false
  }
}

const validarProveedor = () => {
  if (!proveedor.nombre.trim()) {
    alert('❌ El nombre del proveedor es obligatorio')
    return false
  }
  if (!proveedor.telefono.trim()) {
    alert('❌ El teléfono es obligatorio')
    return false
  }
  return true
}

const resetForm = () => {
  proveedor.nombre = ''
  proveedor.contacto = ''
  proveedor.telefono = ''
  proveedor.email = ''
  proveedor.direccion = ''
  proveedor.categorias_seleccionadas = []
  proveedor.productos_especificos = ''
}

const volver = () => {
  emit('cancelar')
}

onMounted(() => {
  cargarCategorias()
})
</script>

<style scoped>
/* =============================
   ESTILOS DIRECTOS DEL FORMULARIO
============================= */
.form-card {
  background: rgba(23, 23, 23, 0.8);
  border: 2px solid #374151;
  border-radius: 20px;
  padding: 50px;
  width: 100%;
  max-width: 950px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05) inset;
  backdrop-filter: blur(10px);
  position: relative;
  margin: 0 auto;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #6b7280, #9ca3af, #6b7280);
  border-radius: 20px 20px 0 0;
}

.form-header { 
  text-align: center; 
  margin-bottom: 50px; 
}

.form-header h1 { 
  font-size: 2.5rem; 
  font-weight: 800; 
  color: #ffffff; 
  margin-bottom: 12px; 
}

.form-header p { 
  color: #d1d5db; 
  font-size: 1.1rem; 
  font-weight: 500; 
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group.full-width {
  grid-column: 1 / -1;
}

label {
  color: #d1d5db;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.required {
  color: #ef4444;
}

input, .form-textarea {
  background: rgba(17, 24, 39, 0.8);
  border: 1px solid #4b5563;
  border-radius: 8px;
  padding: 12px 16px;
  color: white;
  font-size: 14px;
  transition: all 0.3s ease;
}

input:focus, .form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

/* Checkboxes para categorías */
.categorias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.checkbox-label:hover {
  background: rgba(255, 255, 255, 0.1);
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #4b5563;
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-input:checked + .checkbox-custom {
  background: #3b82f6;
  border-color: #3b82f6;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  color: white;
  font-size: 12px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Botones */
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 25px;
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
  font-size: 0.95rem;
}

.btn-primary {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
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

/* Responsive */
@media (max-width: 768px) {
  .form-card { 
    padding: 35px 25px; 
    margin: 20px;
  }
  
  .form-grid { 
    grid-template-columns: 1fr; 
  }
  
  .form-header h1 { 
    font-size: 2rem; 
  }
  
  .form-header p { 
    font-size: 1rem; 
  }
  
  .categorias-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .form-card { 
    padding: 25px 20px; 
    border-radius: 16px; 
    margin: 10px;
  }
  
  .form-header { 
    margin-bottom: 35px; 
  }
  
  .form-header h1 { 
    font-size: 1.8rem; 
  }
}
</style>