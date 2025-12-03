<template>
  <div class="pedido-container">
    <div class="header-section">
      <h2>
        <Package class="header-icon" />
        Registrar Nuevo Producto
      </h2>
      <button @click="cancelar" class="btn-back">
        <ArrowLeft :size="18" />
        Volver al Listado
      </button>
    </div>

    <!-- Información Básica -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <ClipboardList :size="20" />
        </div>
        <h3>Información Básica</h3>
      </div>

      <div class="input-group">
        <label>
          <Tag :size="16" />
          Nombre del Producto *
        </label>
        <input
          v-model="producto.nombre"
          type="text"
          required
          placeholder="Ingrese el nombre del producto"
          class="input-modern"
          @blur="validarNombre"
          :class="{ 'campo-invalido': errores.nombre }"
        />
        <div class="mensaje-error" v-if="errores.nombre">{{ errores.nombre }}</div>
      </div>

      <div class="form-grid">
        <div class="input-group">
          <label>
            <Award :size="16" />
            Marca *
          </label>
          <select
            v-model.number="producto.marca"
            required
            class="select-modern"
            :disabled="cargandoMarcas || marcas.length === 0"
            @blur="validarMarca"
            :class="{ 'campo-invalido': errores.marca }"
          >
            <option value="">Seleccione una marca</option>
            <option v-for="marca in marcas" :key="marca.id" :value="marca.id">
              {{ marca.nombre }}
            </option>
          </select>
          <div class="mensaje-error" v-if="errores.marca">{{ errores.marca }}</div>
        </div>

        <div class="input-group">
          <label>
            <Layers :size="16" />
            Categoría *
          </label>
          <select
            v-model.number="producto.categoria"
            required
            class="select-modern"
            :disabled="cargandoCategorias || categoriasProductos.length === 0"
            @blur="validarCategoria"
            :class="{ 'campo-invalido': errores.categoria }"
          >
            <option value="">Seleccione una categoría</option>
            <option v-for="categoria in categoriasProductos" :key="categoria.id" :value="categoria.id">
              {{ categoria.nombre }}
            </option>
          </select>
          <div class="mensaje-error" v-if="errores.categoria">{{ errores.categoria }}</div>
        </div>
      </div>

      <div class="input-group">
        <label>
          <Barcode :size="16" />
          Código del Producto *
        </label>
        <input
          v-model="producto.codigo"
          type="text"
          required
          readonly
          class="input-modern readonly"
        />
        <div class="mensaje-ayuda">Código generado automáticamente según la categoría</div>
      </div>

      <div class="input-group">
        <label>
          <FileText :size="16" />
          Descripción (Opcional)
        </label>
        <textarea
          v-model="producto.descripcion"
          rows="3"
          placeholder="Descripción del producto..."
          class="textarea-modern"
        ></textarea>
      </div>
    </div>

    <!-- Precio y Stock -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <DollarSign :size="20" />
        </div>
        <h3>Precio y Stock</h3>
      </div>

      <div class="form-grid">
        <div class="input-group">
          <label>
            <DollarSign :size="16" />
            Precio de Venta *
          </label>
          <input
            v-model.number="producto.precio"
            type="number"
            step="0.01"
            min="0.01"
            required
            placeholder="0.00"
            class="input-modern"
            @blur="validarPrecio"
            :class="{ 'campo-invalido': errores.precio }"
          />
          <div class="mensaje-error" v-if="errores.precio">{{ errores.precio }}</div>
        </div>

        <div class="input-group">
          <label>
            <Package :size="16" />
            Stock Inicial *
          </label>
          <input
            v-model.number="producto.stock_actual"
            type="number"
            min="0"
            required
            placeholder="0"
            class="input-modern"
            @blur="validarStock"
            :class="{ 'campo-invalido': errores.stock }"
          />
          <div class="mensaje-error" v-if="errores.stock">{{ errores.stock }}</div>
        </div>
      </div>
    </div>

    <!-- Proveedores -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <Truck :size="20" />
        </div>
        <h3>Proveedores</h3>
        <span v-if="proveedoresActivos.length > 0" class="badge-count">
          {{ proveedoresActivos.length }}
        </span>
      </div>

      <div class="input-group">
        <div class="proveedores-grid">
          <div 
            v-for="proveedor in proveedoresActivos" 
            :key="proveedor.id" 
            class="proveedor-item"
            :class="{ 'selected': producto.proveedores_seleccionados.includes(proveedor.id) }"
            @click="toggleProveedor(proveedor.id)"
          >
            <div class="proveedor-seleccion">
              <div class="proveedor-checkbox" :class="{ 'checked': producto.proveedores_seleccionados.includes(proveedor.id) }">
                <Check v-if="producto.proveedores_seleccionados.includes(proveedor.id)" :size="14" />
              </div>
            </div>
            
            <div class="proveedor-info">
              <div class="proveedor-header">
                <span class="proveedor-nombre">{{ proveedor.nombre }}</span>
                <span class="proveedor-estado">
                  <BadgeCheck :size="14" />
                  Activo
                </span>
              </div>
              <div class="proveedor-details">
                <span class="proveedor-contacto">
                  <User :size="12" />
                  {{ proveedor.contacto || 'Sin contacto' }}
                </span>
                <span class="proveedor-telefono">
                  <Phone :size="12" />
                  {{ proveedor.telefono || 'Sin teléfono' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="mensaje-error" v-if="errores.proveedores">
          <span class="icono-error">!</span>
          {{ errores.proveedores }}
        </div>
        <div class="mensaje-ayuda" v-else-if="producto.proveedores_seleccionados.length > 0">
          ✅ {{ producto.proveedores_seleccionados.length }} proveedor(es) seleccionado(s)
        </div>
        <div class="mensaje-ayuda" v-else>
          Seleccione al menos un proveedor
        </div>
      </div>
    </div>

    <!-- Botón Final -->
    <button 
      @click="registrarProducto" 
      :disabled="!formularioValido || cargando" 
      class="btn-registrar-premium"
      :class="{'btn-processing': cargando}"
    >
      <span v-if="!cargando" class="btn-content">
        <CheckCircle2 :size="20" />
        Registrar Producto
      </span>
      <span v-else class="btn-content">
        <Loader2 :size="20" class="btn-spinner" />
        Procesando...
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Package, ArrowLeft, ClipboardList, Tag, Award, Layers, 
  Barcode, FileText, DollarSign, Truck, User, Phone, 
  Check, BadgeCheck, CheckCircle2, Loader2
} from 'lucide-vue-next'

const emit = defineEmits(['producto-registrado', 'cancelar'])
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

// 📌 Errores por campo
const errores = ref({
  nombre: '',
  marca: '',
  categoria: '',
  precio: '',
  stock: '',
  proveedores: ''
})

const categorias = ref([])
const proveedores = ref([])
const marcas = ref([])

const cargando = ref(false)
const cargandoCategorias = ref(false)
const cargandoProveedores = ref(false)
const cargandoMarcas = ref(false)

// ------------------------------
// VALIDACIONES POR CAMPO (SOLO EN BLUR)
// ------------------------------
const validarNombre = () => {
  const valor = producto.value.nombre.trim()
  if (!valor) {
    errores.value.nombre = "El nombre es obligatorio"
  } else if (valor.length < 2) {
    errores.value.nombre = "El nombre debe tener al menos 2 caracteres"
  } else if (valor.length > 100) {
    errores.value.nombre = "El nombre no puede exceder los 100 caracteres"
  } else {
    errores.value.nombre = ""
  }
}

const validarMarca = () => {
  if (!producto.value.marca) {
    errores.value.marca = "Seleccione una marca"
  } else {
    errores.value.marca = ""
  }
}

const validarCategoria = () => {
  if (!producto.value.categoria) {
    errores.value.categoria = "Seleccione una categoría"
  } else {
    errores.value.categoria = ""
  }
}

const validarPrecio = () => {
  const precio = producto.value.precio
  if (!precio || precio <= 0) {
    errores.value.precio = "El precio debe ser mayor a 0"
  } else if (precio > 1000000) {
    errores.value.precio = "El precio no puede exceder 1,000,000"
  } else {
    errores.value.precio = ""
  }
}

const validarStock = () => {
  const stock = producto.value.stock_actual
  if (stock === null || stock === undefined || stock < 0) {
    errores.value.stock = "El stock no puede ser negativo"
  } else if (stock > 1000000) {
    errores.value.stock = "El stock no puede exceder 1,000,000"
  } else {
    errores.value.stock = ""
  }
}

const validarProveedores = () => {
  if (producto.value.proveedores_seleccionados.length === 0 && proveedoresActivos.value.length > 0) {
    errores.value.proveedores = "Seleccione al menos un proveedor"
  } else {
    errores.value.proveedores = ""
  }
}

const formularioValido = computed(() => {
  return (
    producto.value.nombre.trim() &&
    producto.value.precio > 0 &&
    producto.value.stock_actual >= 0 &&
    producto.value.categoria &&
    producto.value.marca &&
    producto.value.codigo &&
    producto.value.proveedores_seleccionados.length > 0 &&
    Object.values(errores.value).every(error => !error)
  )
})

const categoriasProductos = computed(() => categorias.value)
const proveedoresActivos = computed(() =>
  proveedores.value.filter(p => p.estado === 'ACTIVO' || p.activo)
)

// Toggle proveedor
const toggleProveedor = (proveedorId) => {
  const index = producto.value.proveedores_seleccionados.indexOf(proveedorId)
  if (index > -1) {
    producto.value.proveedores_seleccionados.splice(index, 1)
  } else {
    producto.value.proveedores_seleccionados.push(proveedorId)
  }
  validarProveedores()
}

// ================================
// GENERAR CÓDIGO AUTOMÁTICO
// ================================
const generarCodigo = async (categoriaId) => {
  if (!categoriaId) {
    producto.value.codigo = ''
    return
  }

  try {
    const categoria = categorias.value.find(c => c.id === categoriaId)
    if (!categoria) return

    const abreviatura = categoria.nombre.slice(0, 3).toUpperCase()
    
    const res = await axios.get(`${API_BASE}/usuarios/api/productos/`)
    const todosLosProductos = res.data

    let maxNum = 0
    todosLosProductos.forEach(p => {
      if (p.codigo && p.codigo.startsWith(abreviatura + '-')) {
        const partes = p.codigo.split('-')
        if (partes.length === 2) {
          const num = parseInt(partes[1])
          if (!isNaN(num) && num > maxNum) {
            maxNum = num
          }
        }
      }
    })

    const nuevoNumero = maxNum + 1
    producto.value.codigo = `${abreviatura}-${nuevoNumero.toString().padStart(3, '0')}`

  } catch (err) {
    console.error('Error generando código:', err)
    const categoria = categorias.value.find(c => c.id === categoriaId)
    if (categoria) {
      const abreviatura = categoria.nombre.slice(0, 3).toUpperCase()
      producto.value.codigo = `${abreviatura}-001`
    }
  }
}

// ================================
// CARGA DE DATOS
// ================================
const cargarMarcas = async () => {
  cargandoMarcas.value = true
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/marcas/`)
    marcas.value = res.data
  } catch (err) {
    console.error("Error cargando marcas:", err)
  } finally {
    cargandoMarcas.value = false
  }
}

const cargarCategorias = async () => {
  cargandoCategorias.value = true
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/categorias/productos/`)
    categorias.value = res.data
  } catch (err) {
    console.error('Error cargando categorías:', err)
  } finally {
    cargandoCategorias.value = false
  }
}

const cargarProveedores = async () => {
  cargandoProveedores.value = true
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/proveedores/`)
    proveedores.value = res.data
  } catch (err) {
    console.error('Error cargando proveedores:', err)
  } finally {
    cargandoProveedores.value = false
  }
}

const cargarDatos = async () => {
  await Promise.all([cargarMarcas(), cargarCategorias(), cargarProveedores()])
}

// ================================
// WATCHER
// ================================
watch(() => producto.value.categoria, (newVal) => {
  if (newVal) {
    generarCodigo(Number(newVal))
    validarCategoria()
  }
})

// ================================
// VALIDAR FORMULARIO COMPLETO
// ================================
const validarFormulario = () => {
  validarNombre()
  validarMarca()
  validarCategoria()
  validarPrecio()
  validarStock()
  validarProveedores()

  // Verificar si hay algún error
  return Object.values(errores.value).every(error => !error)
}

// ================================
// REGISTRAR PRODUCTO
// ================================
const registrarProducto = async () => {
  if (!validarFormulario()) {
    Swal.fire({
      icon: 'error',
      title: 'Formulario inválido',
      text: 'Por favor corrige los errores en el formulario',
      confirmButtonColor: '#007bff',
      background: '#fff',
      color: '#1a1a1a'
    })
    return
  }

  cargando.value = true
  try {
    const payload = {
      nombre: producto.value.nombre.trim(),
      codigo: producto.value.codigo,
      descripcion: producto.value.descripcion.trim(),
      precio: producto.value.precio,
      stock: producto.value.stock_actual,
      categoria: Number(producto.value.categoria),
      marca: Number(producto.value.marca),
      proveedores: producto.value.proveedores_seleccionados
    }

    const res = await axios.post(`${API_BASE}/usuarios/api/productos/`, payload)

    Swal.fire({
      icon: 'success',
      title: 'Producto registrado',
      text: 'El producto se creó correctamente',
      confirmButtonColor: '#007bff',
      background: '#fff',
      color: '#1a1a1a'
    })
    
    emit("producto-registrado", res.data)
    resetForm()

  } catch (err) {
    console.error('❌ Error en registrarProducto:', err.response?.data || err)
    
    let errorMessage = 'Ocurrió un error inesperado.'
    if (err.response?.data) {
      if (typeof err.response.data === 'string') {
        errorMessage = err.response.data
      } else if (err.response.data.message) {
        errorMessage = err.response.data.message
      } else if (err.response.data.error) {
        errorMessage = err.response.data.error
      } else if (typeof err.response.data === 'object') {
        errorMessage = Object.values(err.response.data).flat().join(', ')
      }
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Error al registrar producto',
      text: errorMessage,
      confirmButtonColor: '#007bff',
      background: '#fff',
      color: '#1a1a1a'
    })
  } finally {
    cargando.value = false
  }
}

const resetForm = () => {
  producto.value = {
    nombre: "",
    codigo: "",
    descripcion: "",
    precio: 0,
    stock_actual: 0,
    categoria: "",
    marca: "",
    proveedores_seleccionados: []
  }

  errores.value = {
    nombre: '',
    marca: '',
    categoria: '',
    precio: '',
    stock: '',
    proveedores: ''
  }
}

const cancelar = () => emit("cancelar")

onMounted(() => cargarDatos())
</script>

<style scoped>
/* ESTILOS EXACTAMENTE IGUALES A REGISTRARPEDIDO.VUE */
.pedido-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 25px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.header-section h2 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: #007bff;
}

.btn-back {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-back:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Cards modernas */
.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #007bff;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f1f3f4;
}

.card-icon {
  background: linear-gradient(135deg, #007bff, #0056b3);
  padding: 10px;
  border-radius: 10px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
}

.badge-count {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 600;
}

/* Inputs y selects */
.input-group {
  margin-bottom: 20px;
  color: rgb(63, 63, 63);
}

.select-modern, .input-modern {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
}

.select-modern:focus, .input-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

/* Campos inválidos */
.campo-invalido {
  border-color: #dc3545 !important;
  background: rgba(220, 53, 69, 0.05) !important;
}

.campo-invalido:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1) !important;
}

.readonly {
  background-color: #e9ecef !important;
  cursor: not-allowed !important;
  color: #6c757d;
}

/* Mensajes de error */
.mensaje-error {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 6px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  min-height: 20px;
}

.icono-error {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: #dc3545;
  color: white;
  border-radius: 50%;
  font-size: 0.7rem;
  font-weight: bold;
}

/* Mensajes de ayuda */
.mensaje-ayuda {
  color: #6c757d;
  font-size: 0.85em;
  margin-top: 8px;
  display: block;
}

/* Textarea */
.textarea-modern {
  width: 100%;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
  resize: vertical;
  min-height: 80px;
}

.textarea-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

/* Grid para formularios */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* Proveedores como productos */
.proveedores-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 15px;
}

.proveedor-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.proveedor-item:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.proveedor-item.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.proveedor-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
  flex-shrink: 0;
}

.proveedor-checkbox.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.proveedor-info {
  flex: 1;
}

.proveedor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.proveedor-nombre {
  font-weight: 600;
  color: #1a1a1a;
  flex: 1;
  margin-right: 10px;
}

.proveedor-estado {
  color: #28a745;
  font-weight: 600;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 4px;
}

.proveedor-details {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.proveedor-contacto, .proveedor-telefono {
  font-size: 0.85em;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #e9ecef;
}

/* Botón final premium */
.btn-registrar-premium {
  width: 100%;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  font-size: 1.1em;
  padding: 18px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 25px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-registrar-premium:hover:not(:disabled):not(.btn-processing) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, #0056b3, #004085);
}

.btn-registrar-premium:disabled,
.btn-registrar-premium.btn-processing {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .pedido-container {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .proveedor-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .proveedor-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>