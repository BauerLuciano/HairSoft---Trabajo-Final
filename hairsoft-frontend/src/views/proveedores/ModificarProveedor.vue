<template>
  <div class="form-card">
    <div class="form-header">
      <h1>Modificar Proveedor</h1>
      <p>Actualiza los datos del proveedor</p>
    </div>

    <form @submit.prevent="modificarProveedor" class="form-grid" autocomplete="off">
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

      <!-- CUIT -->
      <div class="input-group">
        <label>CUIT</label>
        <input 
          v-model="proveedor.cuit"
          type="text"
          placeholder="Ingrese el CUIT del proveedor"
          @input="filtrarCuit"
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

      <!-- Productos que ofrece (Opcional) -->
      <div class="input-group full-width">
        <label>Productos que ofrece (Opcional)</label>
        <div class="productos-grid">
          <label v-for="producto in productos" :key="producto.id" class="checkbox-label">
            <input 
              type="checkbox" 
              :value="producto.id" 
              v-model="proveedor.productos_seleccionados"
              class="checkbox-input"
            />
            <span class="checkbox-custom"></span>
            {{ producto.nombre }}
          </label>
        </div>
      </div>

      <!-- Productos específicos (solo si hay productos seleccionados) -->
      <div class="input-group full-width" v-if="proveedor.productos_seleccionados.length > 0">
        <label>Productos específicos (opcional)</label>
        <textarea
          v-model="proveedor.productos_especificos"
          placeholder="Ejemplo: tinturas, shampoos, máquinas, tijeras..."
          rows="3"
        ></textarea>
      </div>

      <!-- Estado -->
      <div class="input-group full-width">
        <label>Estado *</label>
        <select v-model="proveedor.estado" required>
          <option value="ACTIVO">Activo</option>
          <option value="INACTIVO">Inactivo</option>
        </select>
      </div>

      <!-- Botones -->
      <div class="full-width form-actions">
        <button type="button" @click="volver" class="btn btn-secondary">
          ← Volver
        </button>
        <button type="submit" :disabled="cargando" class="btn btn-primary">
          {{ cargando ? 'Actualizando...' : 'Actualizar Proveedor' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

const props = defineProps({
  proveedorId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['proveedor-actualizado', 'cancelar'])
const API_BASE = 'http://127.0.0.1:8000'

const proveedor = reactive({
  nombre: '',
  cuit: '',
  contacto: '',
  telefono: '',
  email: '',
  direccion: '',
  categorias_seleccionadas: [], 
  productos_seleccionados: [],   
  productos_especificos: '',
  estado: 'ACTIVO'
})

const categorias = ref([])
const productos = ref([])
const cargando = ref(false)

// 1. Cargar las listas maestras (Categorías y Productos)
const cargarListas = async () => {
  try {
    const [resCats, resProds] = await Promise.all([
      axios.get(`${API_BASE}/api/categorias/productos/`),
      axios.get(`${API_BASE}/api/productos/`)
    ])
    categorias.value = resCats.data
    productos.value = resProds.data
  } catch (err) {
    console.error('Error cargando listas:', err)
  }
}

// 2. Cargar los datos del proveedor y MAPEARLOS
const cargarProveedor = async () => {
  if (!props.proveedorId) return
  cargando.value = true
  
  try {
    const res = await axios.get(`${API_BASE}/api/proveedores/${props.proveedorId}/`)
    const data = res.data

    // Mapeo campo por campo para asegurar la carga
    proveedor.nombre = data.nombre || ''
    proveedor.cuit = data.cuit || ''
    proveedor.contacto = data.contacto || ''
    proveedor.telefono = data.telefono || ''
    proveedor.email = data.email || ''
    proveedor.direccion = data.direccion || ''
    proveedor.productos_especificos = data.productos_especificos || ''
    proveedor.estado = data.estado || 'ACTIVO'

    // El Serializer ahora manda IDs, así que Vue los vincula con los checkboxes
    proveedor.categorias_seleccionadas = data.categorias || []
    proveedor.productos_seleccionados = data.productos || []

    console.log("✅ Datos del proveedor cargados:", proveedor)
  } catch (err) {
    console.error('Error al cargar proveedor:', err)
    Swal.fire('Error', 'No se pudo obtener la información del proveedor', 'error')
  } finally {
    cargando.value = false
  }
}

const modificarProveedor = async () => {
  if (!proveedor.nombre || !proveedor.telefono) {
    return Swal.fire('Atención', 'Nombre y Teléfono son obligatorios', 'warning')
  }

  cargando.value = true
  try {
    const payload = {
      nombre: proveedor.nombre,
      cuit: proveedor.cuit,
      contacto: proveedor.contacto,
      telefono: proveedor.telefono,
      email: proveedor.email,
      direccion: proveedor.direccion,
      categorias: proveedor.categorias_seleccionadas,
      productos: proveedor.productos_seleccionados,
      productos_especificos: proveedor.productos_especificos,
      estado: proveedor.estado
    }

    await axios.put(`${API_BASE}/api/proveedores/${props.proveedorId}/`, payload)
    
    Swal.fire({
      icon: 'success',
      title: '¡Actualizado!',
      text: 'Proveedor modificado correctamente',
      timer: 1500,
      showConfirmButton: false
    })
    
    emit('proveedor-actualizado')
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'No se pudo actualizar el proveedor', 'error')
  } finally {
    cargando.value = false
  }
}

const filtrarCuit = (event) => {
  event.target.value = event.target.value.replace(/[^0-9-]/g, '')
  proveedor.cuit = event.target.value
}

const volver = () => emit('cancelar')

onMounted(async () => {
  // Primero las listas, después el proveedor
  await cargarListas()
  await cargarProveedor()
})

watch(() => props.proveedorId, async (newVal) => {
  if (newVal) await cargarProveedor()
})
</script>

<style scoped>
/* =============================
   ESTILOS DEL FORMULARIO
============================= */
.form-card {
  background: rgba(23, 23, 23, 0.8);
  border: 2px solid #374151;
  border-radius: 20px;
  padding: 30px 50px;
  width: 100%;
  max-width: 950px;
  max-height: 90vh;
  overflow-y: auto;
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

input, select, textarea {
  background: rgba(17, 24, 39, 0.8);
  border: 1px solid #4b5563;
  border-radius: 8px;
  padding: 12px 16px;
  color: white;
  font-size: 14px;
  transition: all 0.3s ease;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

/* Checkboxes para categorías y productos */
.categorias-grid,
.productos-grid {
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
  margin-top: 20px;
  padding-top: 15px;
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
  
  .categorias-grid,
  .productos-grid {
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
