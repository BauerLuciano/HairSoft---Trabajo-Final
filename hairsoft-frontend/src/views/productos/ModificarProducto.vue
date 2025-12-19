<template>
  <div class="form-container">
    <h2>Modificar Producto</h2>
    <form @submit.prevent="modificarProducto" class="product-form">
      <div class="form-grid">

        <div class="form-section">
          <h3>Información Básica</h3>

          <div class="form-group">
            <label for="nombre">Nombre del Producto *</label>
            <input id="nombre" v-model="producto.nombre" type="text" required placeholder="Ingrese el nombre del producto" class="form-input"/>
          </div>

          <div class="form-group">
            <label for="marca">Marca *</label>
            <select id="marca" v-model.number="producto.marca" required class="form-select" :disabled="cargandoMarcas || marcas.length === 0">
              <option value="">Seleccione una marca</option>
              <option v-for="marca in marcas" :key="marca.id" :value="marca.id">{{ marca.nombre }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="categoria_id">Categoría *</label>
            <select id="categoria_id" v-model.number="producto.categoria" required class="form-select" :disabled="cargandoCategorias || categoriasProductos.length === 0">
              <option value="">Seleccione una categoría</option>
              <option v-for="categoria in categoriasProductos" :key="categoria.id" :value="categoria.id">{{ categoria.nombre }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="codigo">Código del Producto *</label>
            <input id="codigo" v-model="producto.codigo" type="text" required readonly class="form-input readonly"/>
          </div>

          <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea id="descripcion" v-model="producto.descripcion" rows="3" placeholder="Descripción del producto (opcional)..." class="form-textarea"></textarea>
          </div>
        </div>

        <div class="form-section">
          <h3>Configuración de Inventario</h3>
          
          <div class="form-group">
            <label for="precio">Precio de Venta *</label>
            <input id="precio" v-model.number="producto.precio" type="number" step="0.01" min="0.01" required placeholder="0.00" class="form-input"/>
          </div>

          <div class="form-grid-3">
            
            <div class="form-group">
              <label for="stock_actual">Stock Actual *</label>
              <input 
                id="stock_actual" 
                v-model.number="producto.stock_actual" 
                type="number" min="0" required 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="stock_minimo" title="Avisar cuando baje de esta cantidad">Stock Mínimo 🚩</label>
              <input 
                id="stock_minimo" 
                v-model.number="producto.stock_minimo" 
                type="number" min="1" required 
                class="form-input warning-border"
              />
            </div>

            <div class="form-group">
              <label for="lote_reposicion" title="Cantidad sugerida a comprar">Lote Reposición 📦</label>
              <input 
                id="lote_reposicion" 
                v-model.number="producto.lote_reposicion" 
                type="number" min="1" required 
                class="form-input info-border"
              />
            </div>

          </div>

          <div class="form-group mt-3">
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
                        {{ proveedor.contacto || 'Sin contacto' }}
                      </span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
            <span class="form-help" :class="{ 'error': producto.proveedores_seleccionados.length === 0 && proveedoresActivos.length > 0 }">
              {{ producto.proveedores_seleccionados.length === 0 ? '❌ Seleccione al menos un proveedor' : 'Proveedores seleccionados' }}
            </span>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" @click="cancelar" class="btn btn-secondary">Cancelar</button>
        <button type="submit" :disabled="cargando || !formularioValido" class="btn btn-primary">{{ cargando ? 'Guardando...' : 'Guardar Cambios' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from '@/utils/axiosConfig'

const props = defineProps({
  productoId: { type: [String, Number], required: true }
})

const emit = defineEmits(['producto-actualizado', 'cancelar'])

const producto = ref({
  nombre: '',
  codigo: '',
  descripcion: '',
  precio: 0,
  stock_actual: 0,
  stock_minimo: 5,      // 🚩 Alerta
  lote_reposicion: 1,   // 📦 Compra
  categoria: '',
  marca: '',
  proveedores_seleccionados: []
})

const categorias = ref([])
const proveedores = ref([])
const marcas = ref([])
const cargando = ref(false)
const cargandoMarcas = ref(false)
const cargandoCategorias = ref(false)
const cargandoProveedores = ref(false)

// Validación
const formularioValido = computed(() =>
  producto.value.nombre.trim() &&
  producto.value.precio > 0 &&
  producto.value.stock_actual >= 0 &&
  producto.value.stock_minimo > 0 &&
  producto.value.lote_reposicion > 0 && // ✅ Validamos lote
  producto.value.categoria &&
  producto.value.marca &&
  producto.value.codigo &&
  producto.value.proveedores_seleccionados.length > 0
)

const categoriasProductos = computed(() => categorias.value)

const proveedoresActivos = computed(() => {
  if (!Array.isArray(proveedores.value)) return []
  return proveedores.value.filter(p => p.estado === 'ACTIVO' || p.activo === true)
})

// ================================
// CARGAR DATOS PRODUCTO
// ================================
const cargarProducto = async () => {
  try {
    const response = await axios.get(`/usuarios/api/productos/${props.productoId}/`)
    const data = response.data
    
    // Mapeo de proveedores (pueden venir como objetos o IDs)
    let proveedoresSeleccionados = []
    if (Array.isArray(data.proveedores)) {
      // Si son objetos, extraemos IDs, si son IDs los dejamos
      proveedoresSeleccionados = typeof data.proveedores[0] === 'object' 
        ? data.proveedores.map(p => p.id) 
        : data.proveedores
    } else if (data.proveedores_ids) {
      proveedoresSeleccionados = data.proveedores_ids
    }
    
    producto.value = {
      nombre: data.nombre || '',
      codigo: data.codigo || '',
      descripcion: data.descripcion || '',
      precio: parseFloat(data.precio) || 0,
      stock_actual: data.stock_actual || 0,
      stock_minimo: data.stock_minimo || 5,      // ✅ Cargar valor
      lote_reposicion: data.lote_reposicion || 1,// ✅ Cargar valor
      categoria: data.categoria?.id || data.categoria || '',
      marca: data.marca?.id || data.marca || '',
      proveedores_seleccionados: proveedoresSeleccionados
    }
  } catch (err) {
    console.error('Error cargando producto:', err)
    alert('❌ Error al cargar los datos del producto')
  }
}

// ================================
// CARGAR AUXILIARES
// ================================
const cargarAuxiliares = async () => {
  cargandoMarcas.value = true; cargandoCategorias.value = true; cargandoProveedores.value = true
  try {
    const [resM, resC, resP] = await Promise.all([
      axios.get('/usuarios/api/marcas/'),
      axios.get('/usuarios/api/categorias/productos/'),
      axios.get('/usuarios/api/proveedores/')
    ])
    marcas.value = resM.data || []
    categorias.value = resC.data || []
    proveedores.value = resP.data || []
  } catch (err) { console.error(err) } 
  finally {
    cargandoMarcas.value = false; cargandoCategorias.value = false; cargandoProveedores.value = false
  }
}

// ================================
// GUARDAR CAMBIOS
// ================================
const modificarProducto = async () => {
  if (!formularioValido.value) {
    alert("❌ Revise los datos. Stocks y precios deben ser válidos.")
    return
  }

  cargando.value = true
  try {
    const payload = {
      nombre: producto.value.nombre.trim(),
      codigo: producto.value.codigo.toString().trim(),
      descripcion: producto.value.descripcion.trim(),
      precio: String(producto.value.precio),
      stock_actual: Number(producto.value.stock_actual),
      stock_minimo: Number(producto.value.stock_minimo),       // ✅
      lote_reposicion: Number(producto.value.lote_reposicion), // ✅
      categoria: Number(producto.value.categoria),
      marca: Number(producto.value.marca),
      proveedores: producto.value.proveedores_seleccionados.map(id => Number(id))
    }

    const res = await axios.put(`/usuarios/api/productos/${props.productoId}/`, payload)

    alert("✅ Producto actualizado correctamente")
    emit("producto-actualizado", res.data)

  } catch (err) {
    console.error('Error update:', err)
    let msg = "Error al actualizar"
    if (err.response?.data?.detail) msg = err.response.data.detail
    alert(msg)
  } finally {
    cargando.value = false
  }
}

const cancelar = () => emit("cancelar")

onMounted(async () => {
  await cargarAuxiliares()
  if (props.productoId) await cargarProducto()
})

watch(() => props.productoId, (newId) => { if(newId) cargarProducto() })
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