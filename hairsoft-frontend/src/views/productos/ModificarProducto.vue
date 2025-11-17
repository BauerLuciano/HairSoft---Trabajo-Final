<template>
  <div class="form-container">
    <h2>Modificar Producto</h2>
    
    <form @submit.prevent="modificarProducto" class="product-form">
      <div class="form-grid">
        <!-- Información Básica -->
        <div class="form-section">
          <h3>Información Básica</h3>
          
          <div class="form-group">
            <label for="nombre">Nombre del Producto *</label>
            <input
              id="nombre"
              v-model="producto.nombre"
              type="text"
              required
              placeholder="Ingrese el nombre del producto"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="codigo">Código del Producto</label>
            <input
              id="codigo"
              v-model="producto.codigo"
              type="text"
              placeholder="Código único"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea
              id="descripcion"
              v-model="producto.descripcion"
              rows="3"
              placeholder="Descripción del producto..."
              class="form-textarea"
            ></textarea>
          </div>
        </div>

        <!-- Precio y Stock -->
        <div class="form-section">
          <h3>Precio y Stock</h3>
          
          <div class="form-group">
            <label for="precio">Precio de Venta *</label>
            <input
              id="precio"
              v-model="producto.precio"
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="0.00"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="costo">Costo de Compra</label>
            <input
              id="costo"
              v-model="producto.costo"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="stock_actual">Stock Actual *</label>
            <input
              id="stock_actual"
              v-model="producto.stock_actual"
              type="number"
              min="0"
              required
              placeholder="0"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="stock_minimo">Stock Mínimo</label>
            <input
              id="stock_minimo"
              v-model="producto.stock_minimo"
              type="number"
              min="0"
              placeholder="0"
              class="form-input"
            />
          </div>
        </div>

        <!-- Categoría y Proveedor -->
        <div class="form-section">
          <h3>Categorización</h3>
          
          <div class="form-group">
            <label for="categoria_id">Categoría *</label>
            <select
              id="categoria_id"
              v-model="producto.categoria_id"
              required
              class="form-select"
            >
              <option value="">Seleccione una categoría</option>
              <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
                {{ categoria.nombre }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="proveedor_id">Proveedor</label>
            <select
              id="proveedor_id"
              v-model="producto.proveedor_id"
              class="form-select"
            >
              <option value="">Seleccione un proveedor</option>
              <option v-for="proveedor in proveedores" :key="proveedor.id" :value="proveedor.id">
                {{ proveedor.nombre }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="estado">Estado *</label>
            <select
              id="estado"
              v-model="producto.estado"
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
          {{ cargando ? 'Actualizando...' : 'Actualizar Producto' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

// ✅ Ya no es necesario importar defineProps o defineEmits
const props = defineProps({
  productoId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['producto-actualizado', 'cancelar'])

const API_BASE = 'http://127.0.0.1:8000'

const producto = ref({
  nombre: '',
  codigo: '',
  descripcion: '',
  precio: 0,
  costo: 0,
  stock_actual: 0,
  stock_minimo: 0,
  categoria_id: '',
  proveedor_id: '',
  estado: 'ACTIVO'
})

const categorias = ref([])
const proveedores = ref([])
const cargando = ref(false)

// ================================
// Cargar datos del producto
// ================================
const cargarProducto = async () => {
  try {
    const response = await axios.get(`${API_BASE}/productos/api/productos/${props.productoId}/`)
    producto.value = response.data
  } catch (err) {
    console.error('Error al cargar producto:', err)
    alert('Error al cargar los datos del producto')
  }
}

// ================================
// Cargar categorías y proveedores
// ================================
const cargarDatos = async () => {
  try {
    const [catRes, provRes] = await Promise.all([
      axios.get(`${API_BASE}/productos/api/categorias/`),
      axios.get(`${API_BASE}/proveedores/api/proveedores/`)
    ])

    categorias.value = catRes.data.filter(c => c.activo)
    proveedores.value = provRes.data.filter(p => p.estado === 'ACTIVO')
  } catch (err) {
    console.error('Error al cargar datos:', err)
    alert('Error al cargar categorías o proveedores')
  }
}

// ================================
// Modificar producto
// ================================
const modificarProducto = async () => {
  if (!validarProducto()) return

  cargando.value = true
  try {
    await axios.put(`${API_BASE}/productos/api/productos/${props.productoId}/`, producto.value)
    alert('Producto actualizado con éxito')
    emit('producto-actualizado')
  } catch (err) {
    console.error('Error al actualizar producto:', err)
    alert('Error al actualizar el producto: ' + (err.response?.data?.message || err.message))
  } finally {
    cargando.value = false
  }
}

// ================================
// Validaciones
// ================================
const validarProducto = () => {
  if (!producto.value.nombre.trim()) {
    alert('El nombre del producto es obligatorio')
    return false
  }
  if (producto.value.precio < 0) {
    alert('El precio no puede ser negativo')
    return false
  }
  if (producto.value.stock_actual < 0) {
    alert('El stock no puede ser negativo')
    return false
  }
  if (producto.value.stock_minimo < 0) {
    alert('El stock mínimo no puede ser negativo')
    return false
  }
  return true
}

// ================================
// Cancelar acción
// ================================
const cancelar = () => {
  emit('cancelar')
}

// ================================
// Ciclo de vida y watchers
// ================================
onMounted(async () => {
  await Promise.all([cargarProducto(), cargarDatos()])
})

watch(() => props.productoId, () => {
  if (props.productoId) cargarProducto()
})
</script>

<style scoped>
/* Los estilos son los mismos que en RegistrarProducto.vue */
.form-container {
  background: rgba(23, 23, 23, 0.95);
  border-radius: 16px;
  padding: 30px;
  max-width: 900px;
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