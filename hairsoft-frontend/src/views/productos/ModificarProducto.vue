<template>
  <div class="form-container">
    <h2>Modificar Producto</h2>
    <form @submit.prevent="modificarProducto" class="product-form">
      <div class="form-grid">

        <!-- Información Básica -->
        <div class="form-section">
          <h3>Información Básica</h3>

          <!-- Nombre -->
          <div class="form-group">
            <label for="nombre">Nombre del Producto *</label>
            <input id="nombre" v-model="producto.nombre" type="text" required placeholder="Ingrese el nombre del producto" class="form-input"/>
          </div>

          <!-- Marca -->
          <div class="form-group">
            <label for="marca">Marca *</label>
            <select id="marca" v-model.number="producto.marca" required class="form-select" :disabled="cargandoMarcas || marcas.length === 0">
              <option value="">Seleccione una marca</option>
              <option v-for="marca in marcas" :key="marca.id" :value="marca.id">{{ marca.nombre }}</option>
            </select>
          </div>

          <!-- Categoría -->
          <div class="form-group">
            <label for="categoria_id">Categoría *</label>
            <select id="categoria_id" v-model.number="producto.categoria" required class="form-select" :disabled="cargandoCategorias || categoriasProductos.length === 0">
              <option value="">Seleccione una categoría</option>
              <option v-for="categoria in categoriasProductos" :key="categoria.id" :value="categoria.id">{{ categoria.nombre }}</option>
            </select>
          </div>

          <!-- Código autogenerado (solo lectura) -->
          <div class="form-group">
            <label for="codigo">Código del Producto *</label>
            <input id="codigo" v-model="producto.codigo" type="text" required readonly class="form-input readonly"/>
          </div>

          <!-- Descripción -->
          <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea id="descripcion" v-model="producto.descripcion" rows="3" placeholder="Descripción del producto (opcional)..." class="form-textarea"></textarea>
          </div>
        </div>

        <!-- Precio, Stock y Proveedores -->
        <div class="form-section">
          <h3>Precio y Stock</h3>
          <div class="form-group">
            <label for="precio">Precio de Venta *</label>
            <input id="precio" v-model.number="producto.precio" type="number" step="0.01" min="0.01" required placeholder="0.00" class="form-input"/>
          </div>

          <div class="form-group">
            <label for="stock_actual">Stock Actual *</label>
            <input id="stock_actual" v-model.number="producto.stock_actual" type="number" min="0" required placeholder="0" class="form-input"/>
          </div>

          <!-- Proveedores -->
          <div class="form-group">
            <label>Proveedores *</label>
            <div class="checkbox-group-enhanced">
              <div v-if="cargandoProveedores" class="loading-message">
                <div class="spinner"></div>
                <span>Cargando proveedores...</span>
              </div>
              
              <div v-else-if="proveedoresActivos.length === 0" class="no-data-message error">
                ❌ No hay proveedores activos registrados.
              </div>
              
              <div v-else class="checkbox-list">
                <div v-for="proveedor in proveedoresActivos" :key="proveedor.id" class="checkbox-item">
                  <input 
                    :id="'proveedor_' + proveedor.id" 
                    v-model="producto.proveedores_seleccionados" 
                    :value="proveedor.id" 
                    type="checkbox" 
                    class="enhanced-checkbox"
                  >
                  <label :for="'proveedor_' + proveedor.id" class="enhanced-checkbox-label">
                    <div class="checkmark"></div>
                    <div class="proveedor-info">
                      <strong>{{ proveedor.nombre }}</strong>
                      <span class="proveedor-contacto">
                        {{ proveedor.contacto || 'Sin contacto' }} | {{ proveedor.telefono || 'Sin teléfono' }}
                      </span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
            <span class="form-help" :class="{ 'error': producto.proveedores_seleccionados.length === 0 && proveedoresActivos.length > 0 }">
              {{ producto.proveedores_seleccionados.length === 0 && proveedoresActivos.length > 0 ? '❌ Seleccione al menos un proveedor' : 'Seleccione uno o más proveedores que venden este producto' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Botones -->
      <div class="form-actions">
        <button type="button" @click="cancelar" class="btn btn-secondary">Cancelar</button>
        <button type="submit" :disabled="cargando || !formularioValido" class="btn btn-primary">{{ cargando ? 'Actualizando...' : 'Actualizar Producto' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

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
  stock_actual: 0,
  categoria: '',
  marca: '',
  proveedores_seleccionados: []
})

const categorias = ref([])
const proveedores = ref([])
const marcas = ref([])

const cargando = ref(false)
const cargandoCategorias = ref(false)
const cargandoProveedores = ref(false)
const cargandoMarcas = ref(false)

const formularioValido = computed(() =>
  producto.value.nombre.trim() &&
  producto.value.precio > 0 &&
  producto.value.stock_actual >= 0 &&
  producto.value.categoria &&
  producto.value.marca &&
  producto.value.codigo &&
  producto.value.proveedores_seleccionados.length > 0
)

const categoriasProductos = computed(() => categorias.value)
// ✅ CORREGIDO: Asegurar que proveedores.value sea un array
const proveedoresActivos = computed(() => {
  if (!Array.isArray(proveedores.value)) {
    console.warn('proveedores.value no es un array:', proveedores.value)
    return []
  }
  return proveedores.value.filter(p => 
    p.estado === 'ACTIVO' || p.activo === true || p.activo === 'true'
  )
})

// ================================
// CARGAR DATOS DEL PRODUCTO
// ================================
const cargarProducto = async () => {
  try {
    console.log(`Cargando producto ID: ${props.productoId}`)
    const response = await axios.get(`${API_BASE}/api/productos/${props.productoId}/`)
    const productoData = response.data
    
    console.log('Producto data recibida:', productoData)
    
    // Asegurar que proveedores_seleccionados sea un array
    let proveedoresSeleccionados = []
    if (Array.isArray(productoData.proveedores)) {
      proveedoresSeleccionados = productoData.proveedores
    } else if (productoData.proveedores_ids) {
      proveedoresSeleccionados = productoData.proveedores_ids
    }
    
    // Mapear los datos del producto al formato del formulario
    producto.value = {
      nombre: productoData.nombre || '',
      codigo: productoData.codigo || '',
      descripcion: productoData.descripcion || '',
      precio: parseFloat(productoData.precio) || 0,
      stock_actual: productoData.stock_actual || 0,
      categoria: productoData.categoria || productoData.categoria_id || productoData.categoria?.id || '',
      marca: productoData.marca || productoData.marca_id || productoData.marca?.id || '',
      proveedores_seleccionados: proveedoresSeleccionados
    }
    
    console.log('Producto mapeado:', producto.value)
  } catch (err) {
    console.error('Error al cargar producto:', err)
    alert('❌ Error al cargar los datos del producto')
  }
}

// ================================
// CARGAR DATOS ADICIONALES
// ================================
const cargarMarcas = async () => {
  cargandoMarcas.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/marcas/`)
    marcas.value = res.data || []
    console.log('Marcas cargadas:', marcas.value)
  } catch (err) {
    console.error("Error cargando marcas:", err)
    marcas.value = []
  } finally {
    cargandoMarcas.value = false
  }
}

const cargarCategorias = async () => {
  cargandoCategorias.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/categorias/productos/`)
    categorias.value = res.data || []
    console.log('Categorías cargadas:', categorias.value)
  } catch (err) {
    console.error('Error cargando categorías:', err)
    categorias.value = []
  } finally {
    cargandoCategorias.value = false
  }
}

const cargarProveedores = async () => {
  cargandoProveedores.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/proveedores/`)
    // ✅ Asegurar que sea un array
    proveedores.value = Array.isArray(res.data) ? res.data : []
    console.log('Proveedores cargados:', proveedores.value)
  } catch (err) {
    console.error('Error cargando proveedores:', err)
    proveedores.value = []
  } finally {
    cargandoProveedores.value = false
  }
}

const cargarDatos = async () => {
  await Promise.all([
    cargarMarcas(), 
    cargarCategorias(), 
    cargarProveedores()
  ])
}

// ================================
// MODIFICAR PRODUCTO
// ================================
const modificarProducto = async () => {
  if (!formularioValido.value) {
    if (producto.value.proveedores_seleccionados.length === 0) {
      alert("❌ Debe seleccionar al menos un proveedor para el producto.")
    } else {
      alert("❌ Complete todos los campos obligatorios.")
    }
    return
  }

  cargando.value = true
  try {
    // ✅ CORREGIDO: Usar 'stock' en lugar de 'stock_actual' porque el serializer lo espera así
    const payload = {
      nombre: producto.value.nombre.trim(),
      codigo: producto.value.codigo.toString().trim(),
      descripcion: producto.value.descripcion.trim(),
      precio: String(producto.value.precio),
      stock: Number(producto.value.stock_actual), // ⚠️ CAMBIÉ: stock_actual → stock
      categoria: Number(producto.value.categoria),
      marca: Number(producto.value.marca),
      proveedores: producto.value.proveedores_seleccionados.map(id => Number(id))
    }

    console.log('Enviando payload para modificar:', payload)
    
    const res = await axios.put(`${API_BASE}/api/productos/${props.productoId}/`, payload)

    alert("✅ Producto actualizado correctamente")
    emit("producto-actualizado", res.data)

  } catch (err) {
    console.error('Error al actualizar producto:', err.response?.data || err)
    
    let mensajeError = "❌ Error al actualizar el producto"
    if (err.response?.data) {
      // Mostrar errores específicos del backend
      if (typeof err.response.data === 'string') {
        mensajeError = err.response.data
      } else if (err.response.data.precio) {
        mensajeError = `Error en precio: ${err.response.data.precio}`
      } else if (err.response.data.nombre) {
        mensajeError = `Error en nombre: ${err.response.data.nombre}`
      } else if (err.response.data.stock) {
        mensajeError = `Error en stock: ${err.response.data.stock}`
      } else {
        mensajeError = JSON.stringify(err.response.data)
      }
    }
    
    alert(mensajeError)
  } finally {
    cargando.value = false
  }
}

// ================================
// CANCELAR
// ================================
const cancelar = () => {
  emit("cancelar")
}

// ================================
// WATCHERS Y MOUNTED
// ================================
onMounted(async () => {
  console.log('Componente ModificarProducto montado')
  await cargarDatos()
  await cargarProducto()
})

watch(() => props.productoId, () => {
  if (props.productoId) {
    console.log('productoId cambiado:', props.productoId)
    cargarProducto()
  }
}, { immediate: true })
</script>

<style scoped>
/* LOS MISMOS ESTILOS QUE REGISTRAR PRODUCTO */
.form-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-container h2 {
  color: #1f2937;
  margin-bottom: 20px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.form-section {
  background: #f8fafc;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.form-section h3 {
  color: #374151;
  margin-bottom: 15px;
  font-size: 1.1rem;
  font-weight: 600;
  border-bottom: 2px solid #3b82f6;
  padding-bottom: 8px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
  background: white;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-help {
  color: #6b7280;
  font-size: 0.75rem;
  margin-top: 4px;
  display: block;
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'><path fill='%23333' d='M2 0L0 2h4zm0 5L0 3h4z'/></svg>");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 12px;
  padding-right: 40px;
}

.readonly {
  background-color: #f9fafb !important;
  cursor: not-allowed !important;
  color: #6b7280;
}

.form-help.error {
  color: #dc2626;
  font-weight: 500;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.checkbox-group-enhanced {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 15px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
}

.enhanced-checkbox {
  display: none;
}

.enhanced-checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.3s ease;
  width: 100%;
  background: white;
}

.enhanced-checkbox-label:hover {
  border-color: #3b82f6;
  background: #f0f7ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.enhanced-checkbox:checked + .enhanced-checkbox-label {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkmark {
  width: 22px;
  height: 22px;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.enhanced-checkbox:checked + .enhanced-checkbox-label .checkmark {
  background: #3b82f6;
  border-color: #3b82f6;
}

.enhanced-checkbox:checked + .enhanced-checkbox-label .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.proveedor-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.proveedor-info strong {
  color: #1f2937;
  font-size: 14px;
}

.proveedor-contacto {
  color: #6b7280;
  font-size: 12px;
}

.loading-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  color: #6b7280;
  font-size: 0.875rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data-message {
  text-align: center;
  padding: 15px;
  color: #6b7280;
  font-style: italic;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px dashed #d1d5db;
}

.no-data-message.error {
  color: #dc2626;
  background: #fef2f2;
  border-color: #fecaca;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .form-container {
    padding: 15px;
    margin: 10px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>