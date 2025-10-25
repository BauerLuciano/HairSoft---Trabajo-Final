<template>
  <div class="form-container">
    <h2>Registrar Nuevo Producto</h2>
    
    <form @submit.prevent="registrarProducto" class="product-form">
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
              placeholder="Código único (opcional)"
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
            <label for="stock_actual">Stock Inicial *</label>
            <input
              id="stock_actual"
              v-model="producto.stock_actual"
              type="number"
              min="0"
              required
              placeholder="0"
              class="form-input"
            />
            <small class="form-help">Alerta automática cuando el stock sea ≤ 10 unidades</small>
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
              <option v-for="categoria in categoriasProductos" :key="categoria.id" :value="categoria.id">
                {{ categoria.nombre }}
              </option>
            </select>
            <small class="form-help">Categorías específicas para productos</small>
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
            <small class="form-help">Múltiples proveedores pueden vender el mismo producto</small>
          </div>
        </div>
      </div>

      <!-- Botones -->
      <div class="form-actions">
        <button type="button" @click="cancelar" class="btn btn-secondary">
          Cancelar
        </button>
        <button type="submit" :disabled="cargando" class="btn btn-primary">
          {{ cargando ? 'Registrando...' : 'Registrar Producto' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const emit = defineEmits(['producto-registrado', 'cancelar'])

const API_BASE = 'http://127.0.0.1:8000'

const producto = ref({
  nombre: '',
  codigo: '',
  descripcion: '',
  precio: 0,
  stock_actual: 0,
  categoria_id: '',
  proveedor_id: ''
})

const categorias = ref([])
const proveedores = ref([])
const cargando = ref(false)

// Filtrar solo categorías de productos
const categoriasProductos = computed(() => {
  return categorias.value.filter(c => c.tipo === 'PRODUCTO' && c.activo)
})

// Cargar categorías y proveedores
const cargarDatos = async () => {
  try {
    const [catRes, provRes] = await Promise.all([
      axios.get(`${API_BASE}/categorias/api/categorias/`),
      axios.get(`${API_BASE}/proveedores/api/proveedores/`)
    ])
    
    categorias.value = catRes.data
    proveedores.value = provRes.data.filter(p => p.estado === 'ACTIVO')
  } catch (err) {
    console.error('Error al cargar datos:', err)
    alert('Error al cargar categorías o proveedores')
  }
}

const registrarProducto = async () => {
  if (!validarProducto()) return
  
  cargando.value = true
  try {
    const response = await axios.post(`${API_BASE}/productos/api/productos/`, producto.value)
    alert('Producto registrado con éxito')
    emit('producto-registrado', response.data)
  } catch (err) {
    console.error('Error al registrar producto:', err)
    alert('Error al registrar el producto: ' + (err.response?.data?.message || err.message))
  } finally {
    cargando.value = false
  }
}

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
  return true
}

const cancelar = () => {
  emit('cancelar')
}

onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
/* Mantener los mismos estilos que antes, solo agregar */
.form-help {
  color: #9ca3af;
  font-size: 0.8rem;
  margin-top: 4px;
  display: block;
}
</style>