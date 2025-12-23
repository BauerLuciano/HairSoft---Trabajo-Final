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
          placeholder="Ej: Shampoo Keratina 500ml"
          class="input-modern"
          @blur="validarNombre"
          :class="{ 'campo-invalido': errores.nombre }"
        />
        <div class="mensaje-feedback error" v-if="errores.nombre">{{ errores.nombre }}</div>
        <div class="mensaje-feedback" v-else>&nbsp;</div>
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
          <div class="mensaje-feedback error" v-if="errores.marca">{{ errores.marca }}</div>
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
          <div class="mensaje-feedback error" v-if="errores.categoria">{{ errores.categoria }}</div>
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
        <div class="mensaje-feedback info">Generado autom. según categoría</div>
      </div>

      <div class="input-group">
        <label>
          <FileText :size="16" />
          Descripción (Opcional)
        </label>
        <textarea
          v-model="producto.descripcion"
          rows="3"
          placeholder="Detalles adicionales del producto..."
          class="textarea-modern"
        ></textarea>
      </div>

      <div class="input-group" style="margin-top: 20px;">
        <label>
          <Camera :size="16" />
          Imagen del Producto (Opcional)
        </label>
        
        <div class="image-upload-wrapper">
          <input 
            type="file" 
            ref="fileInput"
            @change="seleccionarImagen" 
            accept="image/*"
            style="display: none"
          >
          
          <div class="image-preview-container" @click="$refs.fileInput.click()">
            <div v-if="imagenPreview" class="preview-active">
              <img :src="imagenPreview" alt="Vista previa" class="img-preview">
              <button @click.stop="quitarImagen" class="btn-remove-img" title="Quitar imagen">
                <X :size="16" />
              </button>
            </div>
            <div v-else class="upload-placeholder">
              <UploadCloud :size="32" class="upload-icon" />
              <span>Hacé clic para subir una imagen</span>
              <small>JPG, PNG o WEBP</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <DollarSign :size="20" />
        </div>
        <h3>Configuración de Inventario</h3>
      </div>

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
        <div class="mensaje-feedback error" v-if="errores.precio">{{ errores.precio }}</div>
      </div>

      <div class="form-grid-3">
        
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
          <div class="mensaje-feedback error" v-if="errores.stock">{{ errores.stock }}</div>
          <div class="mensaje-feedback" v-else>&nbsp;</div>
        </div>

        <div class="input-group">
          <label title="Avisar cuando baje de esta cantidad">
            <AlertTriangle :size="16" class="icon-warning" />
            Stock Mínimo *
          </label>
          <input
            v-model.number="producto.stock_minimo"
            type="number"
            min="1"
            required
            placeholder="Ej: 5"
            class="input-modern warning-border"
            @blur="validarStockMinimo"
            :class="{ 'campo-invalido': errores.stock_minimo }"
          />
          <div class="mensaje-feedback error" v-if="errores.stock_minimo">{{ errores.stock_minimo }}</div>
          <div class="mensaje-feedback" v-else>&nbsp;</div>
        </div>

        <div class="input-group">
          <label title="Cantidad sugerida a comprar">
            <Truck :size="16" class="icon-info" />
            Lote Reposición *
          </label>
          <input
            v-model.number="producto.lote_reposicion"
            type="number"
            min="1"
            required
            placeholder="Ej: 12"
            class="input-modern info-border"
          />
          <div class="mensaje-feedback info">Sugerido para compra</div>
        </div>

      </div>
    </div>

    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <Truck :size="20" />
        </div>
        <h3>Proveedores (Opcional)</h3>
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
              </div>
              <div class="proveedor-details">
                <span class="proveedor-contacto">
                  {{ proveedor.contacto || 'Sin contacto' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="mensaje-feedback error" v-if="errores.proveedores">
          {{ errores.proveedores }}
        </div>
        <div class="mensaje-feedback info" v-else-if="producto.proveedores_seleccionados.length > 0">
          ✅ {{ producto.proveedores_seleccionados.length }} proveedor(es) seleccionado(s)
        </div>
        <div class="mensaje-feedback info" v-else>
          Seleccione al menos un proveedor (opcional)
        </div>
      </div>
    </div>

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
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2'
import { 
  Package, ArrowLeft, ClipboardList, Tag, Award, Layers, 
  Barcode, FileText, DollarSign, Truck, User, Phone, 
  Check, BadgeCheck, CheckCircle2, Loader2, AlertTriangle,
  Camera, UploadCloud, X 
} from 'lucide-vue-next'

const emit = defineEmits(['producto-registrado', 'cancelar'])

const producto = ref({
  nombre: '',
  codigo: '',
  descripcion: '',
  precio: 0,
  stock_actual: 0,
  stock_minimo: 5,
  lote_reposicion: 1,
  categoria: '',
  marca: '',
  proveedores_seleccionados: []
})

const imagenArchivo = ref(null)
const imagenPreview = ref(null)
const fileInput = ref(null)

const errores = ref({
  nombre: '', marca: '', categoria: '', precio: '', stock: '', stock_minimo: '', proveedores: ''
})

const categorias = ref([])
const proveedores = ref([])
const marcas = ref([])

const cargando = ref(false)
const cargandoCategorias = ref(false)
const cargandoProveedores = ref(false)
const cargandoMarcas = ref(false)

const seleccionarImagen = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) { 
      Swal.fire('Error', 'La imagen es muy pesada (Máx 5MB)', 'warning')
      return
    }
    imagenArchivo.value = file
    imagenPreview.value = URL.createObjectURL(file)
  }
}

const quitarImagen = () => {
  imagenArchivo.value = null
  imagenPreview.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const validarNombre = async () => {
  const valor = producto.value.nombre.trim()
  if (!valor) { errores.value.nombre = "El nombre es obligatorio"; return }
  if (valor.length < 2) { errores.value.nombre = "Mínimo 2 caracteres"; return }
  
  if (producto.value.marca) {
    try {
      const response = await axios.get(`/usuarios/api/productos/?nombre=${valor}&marca=${producto.value.marca}`)
      const data = Array.isArray(response.data) ? response.data : (response.data.results || [])
      if (data.length > 0) {
        errores.value.nombre = `Ya existe "${valor}" para esta marca`
        return
      }
    } catch (e) {}
  }
  errores.value.nombre = ""
}

const validarMarca = () => errores.value.marca = !producto.value.marca ? "Seleccione una marca" : ""
const validarCategoria = () => errores.value.categoria = !producto.value.categoria ? "Seleccione una categoría" : ""
const validarPrecio = () => errores.value.precio = (!producto.value.precio || producto.value.precio <= 0) ? "Mayor a 0" : ""
const validarStock = () => errores.value.stock = (producto.value.stock_actual < 0) ? "No negativo" : ""
const validarStockMinimo = () => errores.value.stock_minimo = (producto.value.stock_minimo < 1) ? "Mínimo 1" : ""

const formularioValido = computed(() => {
  return (
    producto.value.nombre.trim() &&
    producto.value.precio > 0 &&
    producto.value.stock_actual >= 0 &&
    producto.value.stock_minimo > 0 &&
    producto.value.lote_reposicion > 0 &&
    producto.value.categoria &&
    producto.value.marca &&
    Object.values(errores.value).every(error => !error)
  )
})

const categoriasProductos = computed(() => categorias.value)
const proveedoresActivos = computed(() => proveedores.value.filter(p => p.estado === 'ACTIVO' || p.activo))

const toggleProveedor = (id) => {
  const idx = producto.value.proveedores_seleccionados.indexOf(id)
  if (idx > -1) producto.value.proveedores_seleccionados.splice(idx, 1)
  else producto.value.proveedores_seleccionados.push(id)
}

const generarCodigo = async (catId) => {
  if (!catId) { producto.value.codigo = ''; return }
  try {
    const cat = categorias.value.find(c => c.id === catId)
    if (!cat) return
    const abr = cat.nombre.slice(0, 3).toUpperCase()
    const res = await axios.get(`/usuarios/api/productos/`)
    const prods = Array.isArray(res.data) ? res.data : (res.data.results || [])
    
    let max = 0
    prods.forEach(p => {
      if (p.codigo?.startsWith(abr + '-')) {
        const n = parseInt(p.codigo.split('-')[1])
        if (!isNaN(n) && n > max) max = n
      }
    })
    producto.value.codigo = `${abr}-${String(max + 1).padStart(3, '0')}`
  } catch (e) { console.error(e) }
}

const cargarDatos = async () => {
  cargandoCategorias.value = true; cargandoMarcas.value = true; cargandoProveedores.value = true
  try {
    const [resM, resC, resP] = await Promise.all([
      axios.get('/usuarios/api/marcas/'),
      axios.get('/usuarios/api/categorias/productos/'),
      axios.get('/usuarios/api/proveedores/')
    ])
    marcas.value = Array.isArray(resM.data) ? resM.data : []
    categorias.value = Array.isArray(resC.data) ? resC.data : []
    proveedores.value = Array.isArray(resP.data) ? resP.data : []
  } catch (e) { console.error(e) }
  finally {
    cargandoCategorias.value = false; cargandoMarcas.value = false; cargandoProveedores.value = false
  }
}

watch(() => producto.value.categoria, (v) => { if(v) generarCodigo(Number(v)) })
watch(() => producto.value.marca, () => { if(producto.value.nombre) setTimeout(validarNombre, 300) })

const registrarProducto = async () => {
  if (!formularioValido.value) {
    Swal.fire({ icon: 'error', title: 'Error', text: 'Revise los campos requeridos' })
    return
  }

  cargando.value = true
  try {
    const formData = new FormData()
    
    formData.append('nombre', producto.value.nombre.trim())
    formData.append('codigo', producto.value.codigo)
    formData.append('descripcion', producto.value.descripcion || '')
    formData.append('precio', producto.value.precio)
    formData.append('stock_actual', producto.value.stock_actual)
    formData.append('stock_minimo', producto.value.stock_minimo)
    formData.append('lote_reposicion', producto.value.lote_reposicion)
    formData.append('categoria', Number(producto.value.categoria))
    formData.append('marca', Number(producto.value.marca))
    
    producto.value.proveedores_seleccionados.forEach(id => {
      formData.append('proveedores', id)
    })

    if (imagenArchivo.value) {
      formData.append('imagen', imagenArchivo.value)
    }

    const config = { headers: { 'Content-Type': 'multipart/form-data' } }

    const res = await axios.post(`/usuarios/api/productos/`, formData, config)

    Swal.fire({
      icon: 'success',
      title: 'Producto Registrado',
      text: `Creado con código ${res.data.codigo}`,
      confirmButtonColor: '#007bff'
    }).then(() => {
      emit("producto-registrado", res.data)
      resetForm()
    })

  } catch (err) {
    console.error(err)
    Swal.fire({ icon: 'error', title: 'Error al guardar', text: err.response?.data?.detail || 'Intente nuevamente' })
  } finally {
    cargando.value = false
  }
}

const resetForm = () => {
  producto.value = {
    nombre: "", codigo: "", descripcion: "", precio: 0,
    stock_actual: 0, stock_minimo: 5, lote_reposicion: 1,
    categoria: "", marca: "", proveedores_seleccionados: []
  }
  quitarImagen()
}

const cancelar = () => emit("cancelar")
onMounted(() => cargarDatos())
</script>

<style scoped>
/* ESTILOS EXACTOS + CORRECCIONES */
.pedido-container { max-width: 1000px; margin: 0 auto; padding: 25px; background: #fff; border-radius: 16px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #f1f3f4; }
.header-section h2 { margin: 0; color: #1a1a1a; font-size: 1.8em; font-weight: 700; display: flex; align-items: center; gap: 12px; }
.header-icon { color: #007bff; }
.btn-back { background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s ease; display: flex; align-items: center; gap: 8px; }
.btn-back:hover { background: #5a6268; transform: translateY(-1px); }
.card-modern { background: #fff; border-radius: 16px; border: 2px solid #f1f3f4; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); transition: all 0.3s ease; }
.card-modern:hover { border-color: #007bff; box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15); }
.card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #f1f3f4; }
.card-icon { background: linear-gradient(135deg, #007bff, #0056b3); padding: 10px; border-radius: 10px; color: white; display: flex; align-items: center; justify-content: center; }
.card-header h3 { margin: 0; color: #1a1a1a; font-size: 1.3em; font-weight: 700; flex: 1; }
.badge-count { background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.9em; font-weight: 600; }
.input-group { margin-bottom: 20px; color: rgb(63, 63, 63); }
.select-modern, .input-modern { width: 100%; padding: 12px 16px; border-radius: 10px; border: 2px solid #e1e5e9; background: #f8f9fa; font-size: 14px; transition: all 0.3s ease; color: #1a1a1a; box-sizing: border-box; }
.select-modern:focus, .input-modern:focus { border-color: #007bff; background: #fff; box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1); outline: none; }
.campo-invalido { border-color: #dc3545 !important; background: rgba(220, 53, 69, 0.05) !important; }
.campo-invalido:focus { box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1) !important; }
.readonly { background-color: #e9ecef !important; cursor: not-allowed !important; color: #6c757d; }

/* FIX ALINEACIÓN MENSAJES */
.mensaje-feedback { font-size: 0.85rem; margin-top: 6px; font-weight: 500; display: flex; align-items: center; gap: 4px; min-height: 20px; }
.mensaje-feedback.error { color: #dc3545; }
.mensaje-feedback.info { color: #6c757d; font-size: 0.8em; }

.textarea-modern { width: 100%; padding: 15px; border: 2px solid #e9ecef; border-radius: 10px; background: #f8f9fa; font-size: 14px; transition: all 0.3s ease; color: #1a1a1a; resize: vertical; min-height: 80px; box-sizing: border-box; }
.textarea-modern:focus { border-color: #007bff; background: #fff; box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1); outline: none; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.form-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }

/* FIX PROVEEDORES HORIZONTAL (GRID INTELIGENTE) */
.proveedores-grid { 
  display: grid; 
  /* Esto asegura que se pongan uno al lado del otro si caben, mínimo 240px cada uno */
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
  gap: 15px; 
  margin-bottom: 15px;
  width: 100%;
}

.proveedor-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border: 2px solid #e9ecef; border-radius: 12px; cursor: pointer; transition: all 0.3s ease; background: #fff; }
.proveedor-item:hover { border-color: #007bff; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1); }
.proveedor-item.selected { border-color: #007bff; background: #e7f3ff; }
.proveedor-checkbox { width: 20px; height: 20px; border: 2px solid #dee2e6; border-radius: 6px; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; color: transparent; flex-shrink: 0; }
.proveedor-checkbox.checked { background: #007bff; border-color: #007bff; color: white; }
.proveedor-info { flex: 1; overflow: hidden; }
.proveedor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.proveedor-nombre { font-weight: 600; color: #1a1a1a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.proveedor-details { font-size: 0.85em; color: #6c757d; }
.proveedor-contacto { font-weight: 500; }

.btn-registrar-premium { width: 100%; background: linear-gradient(135deg, #007bff, #0056b3); color: white; font-size: 1.1em; padding: 18px; border: none; border-radius: 12px; cursor: pointer; transition: all 0.3s ease; margin-top: 25px; font-weight: 600; box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3); position: relative; overflow: hidden; }
.btn-registrar-premium:hover:not(:disabled):not(.btn-processing) { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4); background: linear-gradient(135deg, #0056b3, #004085); }
.btn-registrar-premium:disabled, .btn-registrar-premium.btn-processing { background: #6c757d; cursor: not-allowed; opacity: 0.7; transform: none; }
.btn-content { display: flex; align-items: center; justify-content: center; gap: 10px; }
.btn-spinner { animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* ESTILOS IMAGEN */
.image-upload-wrapper { width: 100%; }
.image-preview-container { width: 100%; height: 180px; border: 2px dashed #e1e5e9; border-radius: 12px; background-color: #f8f9fa; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s ease; overflow: hidden; position: relative; }
.image-preview-container:hover { border-color: #007bff; background-color: #e7f3ff; }
.preview-active { width: 100%; height: 100%; position: relative; }
.img-preview { width: 100%; height: 100%; object-fit: contain; background: white; }
.btn-remove-img { position: absolute; top: 10px; right: 10px; background: rgba(220, 53, 69, 0.9); color: white; border: none; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; }
.btn-remove-img:hover { transform: scale(1.1); background: #dc3545; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; color: #6c757d; }
.upload-icon { color: #007bff; margin-bottom: 5px; }

@media (max-width: 768px) {
  .pedido-container { padding: 15px; }
  .header-section { flexDirection: column; gap: 15px; alignItems: stretch; }
  .form-grid, .form-grid-3 { grid-template-columns: 1fr; gap: 15px; }
  .proveedores-grid { grid-template-columns: 1fr; } /* En móvil se apilan */
}
</style>