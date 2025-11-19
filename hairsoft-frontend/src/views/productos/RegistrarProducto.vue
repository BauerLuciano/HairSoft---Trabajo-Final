<template>
  <div class="form-container">
    <h2>Registrar Nuevo Producto</h2>
    
    <form @submit.prevent="registrarProducto" class="product-form">
      <div class="form-grid">
        <!-- Información Básica - REORDENADO -->
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

          <!-- CATEGORÍA PRIMERO -->
          <div class="form-group">
            <label for="categoria_id">Categoría *</label>
            <select
              id="categoria_id"
              v-model="producto.categoria"
              required
              class="form-select"
              :disabled="cargandoCategorias || categoriasProductos.length === 0"
              @change="generarCodigoAutomatico"
            >
              <option value="">Seleccione una categoría</option>
              <option v-for="categoria in categoriasProductos" :key="categoria.id" :value="categoria.id">
                {{ categoria.nombre }}
              </option>
            </select>
            <small class="form-help">Al seleccionar categoría se genera código automático</small>
            
            <div v-if="cargandoCategorias" class="loading-message">
              <div class="spinner"></div>
              Cargando categorías...
            </div>
            <div v-else-if="categoriasProductos.length === 0" class="no-data-message error">
              ❌ No hay categorías disponibles
            </div>
          </div>

          <!-- CÓDIGO AUTOMÁTICO - SOLO LECTURA -->
          <div class="form-group">
            <label for="codigo">Código del Producto *</label>
            <input
              id="codigo"
              v-model="producto.codigo"
              type="text"
              required
              readonly
              placeholder="Se generará automáticamente al elegir categoría"
              class="form-input readonly"
              style="background-color: #f9fafb; cursor: not-allowed;"
            />
            <small class="form-help">Código generado automáticamente</small>
          </div>

          <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea
              id="descripcion"
              v-model="producto.descripcion"
              rows="3"
              placeholder="Descripción del producto (opcional)..."
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
              v-model.number="producto.precio"
              type="number"
              step="0.01"
              min="0.01"
              required
              placeholder="0.00"
              class="form-input"
              @input="validarPrecio"
            />
            <small class="form-help error" v-if="precioInvalido">El precio debe ser mayor a 0</small>
          </div>

          <div class="form-group">
            <label for="stock_actual">Stock Inicial *</label>
            <input
              id="stock_actual"
              v-model.number="producto.stock_actual"
              type="number"
              min="0"
              required
              placeholder="0"
              class="form-input"
              @input="validarStock"
            />
            <small class="form-help">Alerta automática cuando el stock sea ≤ 10 unidades</small>
            <small class="form-help error" v-if="stockInvalido">El stock no puede ser negativo</small>
          </div>

          <!-- Proveedores movidos aquí -->
          <div class="form-group">
            <label>Proveedores Disponibles</label>
            
            <div v-if="cargandoProveedores" class="loading-message">
              <div class="spinner"></div>
              Cargando proveedores...
            </div>
            
            <div v-else-if="proveedoresActivos.length > 0" class="checkbox-group-enhanced">
              <div class="checkbox-item" v-for="proveedor in proveedoresActivos" :key="proveedor.id">
                <input 
                  type="checkbox" 
                  :id="`proveedor-${proveedor.id}`"
                  :value="proveedor.id" 
                  v-model="producto.proveedores_seleccionados"
                  class="enhanced-checkbox"
                />
                <label :for="`proveedor-${proveedor.id}`" class="enhanced-checkbox-label">
                  <span class="checkmark"></span>
                  <span class="proveedor-info">
                    <strong>{{ proveedor.nombre }}</strong>
                    <span class="proveedor-contacto">{{ proveedor.contacto || 'Sin contacto' }}</span>
                  </span>
                </label>
              </div>
            </div>
            
            <div v-else class="no-data-message">
              No hay proveedores disponibles
            </div>
            <small class="form-help">Puede seleccionar múltiples proveedores</small>
          </div>
        </div>
      </div>

      <!-- Botones -->
      <div class="form-actions">
        <button type="button" @click="cancelar" class="btn btn-secondary">
          Cancelar
        </button>
        <button type="submit" :disabled="cargando || !formularioValido" class="btn btn-primary">
          {{ cargando ? 'Registrando...' : 'Registrar Producto' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

const emit = defineEmits(['producto-registrado', 'cancelar'])

const API_BASE = 'http://127.0.0.1:8000'

const producto = ref({
  nombre: '',
  codigo: '',
  descripcion: '',
  precio: 0,
  stock_actual: 0,
  categoria: '',
  proveedores_seleccionados: []
})

const categorias = ref([])
const proveedores = ref([])
const cargando = ref(false)
const cargandoCategorias = ref(false)
const cargandoProveedores = ref(false)
const precioInvalido = ref(false)
const stockInvalido = ref(false)

// Computed para validar formulario completo
const formularioValido = computed(() => {
  return producto.value.nombre.trim() && 
         producto.value.precio > 0 &&
         producto.value.stock_actual >= 0 &&
         producto.value.categoria &&
         producto.value.codigo
})

// Filtrar solo categorías de productos
const categoriasProductos = computed(() => {
  return categorias.value
})

// Filtrar proveedores activos
const proveedoresActivos = computed(() => {
  return proveedores.value.filter(p => p.estado === 'ACTIVO' || p.activo)
})

// Generar código automático cuando se selecciona categoría
const generarCodigoAutomatico = async () => {
  if (!producto.value.categoria) return
  
  try {
    const categoriaSeleccionada = categorias.value.find(c => c.id == producto.value.categoria)
    if (!categoriaSeleccionada) return

    // Obtener el último código de esta categoría
    const response = await axios.get(`${API_BASE}/usuarios/api/productos/?categoria=${producto.value.categoria}`)
    const productosMismaCategoria = response.data
    
    let nuevoNumero = 1
    if (productosMismaCategoria.length > 0) {
      // Buscar el número más alto
      const numeros = productosMismaCategoria
        .map(p => {
          if (p.codigo && p.codigo.startsWith(categoriaSeleccionada.nombre.substring(0, 3).toUpperCase())) {
            const partes = p.codigo.split('-')
            if (partes.length === 2) {
              return parseInt(partes[1]) || 0
            }
          }
          return 0
        })
        .filter(n => n > 0)
      
      nuevoNumero = numeros.length > 0 ? Math.max(...numeros) + 1 : 1
    }

    const abreviatura = categoriaSeleccionada.nombre.substring(0, 3).toUpperCase()
    producto.value.codigo = `${abreviatura}-${nuevoNumero.toString().padStart(3, '0')}`
    
  } catch (error) {
    console.error('Error generando código:', error)
    // Si falla, generar código local
    const categoriaSeleccionada = categorias.value.find(c => c.id == producto.value.categoria)
    if (categoriaSeleccionada) {
      const abreviatura = categoriaSeleccionada.nombre.substring(0, 3).toUpperCase()
      producto.value.codigo = `${abreviatura}-001`
    }
  }
}

// Validaciones en tiempo real
const validarPrecio = () => {
  precioInvalido.value = producto.value.precio <= 0
}

const validarStock = () => {
  stockInvalido.value = producto.value.stock_actual < 0
}

// Cargar categorías
const cargarCategorias = async () => {
  cargandoCategorias.value = true
  try {
    const response = await axios.get(`${API_BASE}/usuarios/api/categorias/productos/`)
    categorias.value = response.data
  } catch (err) {
    console.error('Error cargando categorías:', err)
    try {
      const altResponse = await axios.get(`${API_BASE}/usuarios/api/categorias/`)
      categorias.value = altResponse.data
    } catch (altErr) {
      console.error('También falló endpoint alternativo:', altErr)
    }
  } finally {
    cargandoCategorias.value = false
  }
}

// Cargar proveedores
const cargarProveedores = async () => {
  cargandoProveedores.value = true
  try {
    const response = await axios.get(`${API_BASE}/usuarios/api/proveedores/`)
    proveedores.value = response.data
  } catch (err) {
    console.error('Error al cargar proveedores:', err)
  } finally {
    cargandoProveedores.value = false
  }
}

// Cargar todos los datos
const cargarDatos = async () => {
  await Promise.all([
    cargarCategorias(),
    cargarProveedores()
  ])
}

const registrarProducto = async () => {
  if (!formularioValido.value) {
    alert('❌ Complete todos los campos obligatorios correctamente')
    return
  }
  
  cargando.value = true
  try {
    const payload = {
      nombre: producto.value.nombre.trim(),
      codigo: producto.value.codigo,
      descripcion: producto.value.descripcion.trim() || '',
      precio: parseFloat(producto.value.precio),
      stock: parseInt(producto.value.stock_actual),
      categoria: parseInt(producto.value.categoria),
      proveedores: producto.value.proveedores_seleccionados.map(p => parseInt(p))
    }

    console.log('📤 Enviando producto:', payload)
    
    const response = await axios.post(`${API_BASE}/usuarios/api/productos/`, payload)
    
    console.log('✅ Producto registrado con éxito:', response.data)
    alert('✅ Producto registrado con éxito')
    resetForm()
    emit('producto-registrado', response.data)
    
  } catch (err) {
    console.error('❌ Error al registrar producto:', err)
    if (err.response?.status === 400) {
      const errors = err.response.data
      let mensajeError = '❌ Error en los datos:\n'
      if (typeof errors === 'object') {
        Object.entries(errors).forEach(([campo, errores]) => {
          mensajeError += `• ${campo}: ${Array.isArray(errores) ? errores.join(', ') : errores}\n`
        })
      } else {
        mensajeError += JSON.stringify(errors, null, 2)
      }
      alert(mensajeError)
    } else {
      alert('❌ Error al registrar el producto: ' + (err.response?.data?.message || err.message))
    }
  } finally {
    cargando.value = false
  }
}

const resetForm = () => {
  producto.value = {
    nombre: '',
    codigo: '',
    descripcion: '',
    precio: 0,
    stock_actual: 0,
    categoria: '',
    proveedores_seleccionados: []
  }
  precioInvalido.value = false
  stockInvalido.value = false
}

const cancelar = () => {
  emit('cancelar')
}

onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
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
  appearance: none; /* Remover estilo por defecto */
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

/* Mejorar visibilidad de campos inválidos */
.form-input:invalid {
  border-color: #dc2626;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

/* CHECKBOXES MEJORADOS - MUY VISIBLES */
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

/* Estados de carga y mensajes */
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

/* Form Actions */
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

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

/* Responsive */
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