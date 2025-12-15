<template>
  <div class="pedido-container">
    <div class="header-section">
      <h2>
        <Award class="header-icon" />
        Modificar Marca
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
        <h3>Información de la Marca</h3>
      </div>

      <div class="input-group">
        <label>
          <Tag :size="16" />
          Nombre de la Marca *
        </label>
        <input
          v-model="marca.nombre"
          type="text"
          required
          placeholder="Ej: Loreal, Pantene..."
          class="input-modern"
          @blur="validarNombre"
          :class="{ 'campo-invalido': errores.nombre }"
        />
        <div class="mensaje-error" v-if="errores.nombre">{{ errores.nombre }}</div>
      </div>

      <div class="input-group">
        <label>
          <FileText :size="16" />
          Descripción (Opcional)
        </label>
        <textarea
          v-model="marca.descripcion"
          rows="3"
          placeholder="Breve descripción de la marca..."
          class="textarea-modern"
        ></textarea>
      </div>

      <div class="input-group">
        <label>
          <ToggleLeft :size="16" />
          Proveedores Asociados
        </label>
        
        <div class="chips-wrapper">
          <div 
            v-for="prov in proveedoresDisponibles" 
            :key="prov.id" 
            class="chip-item"
            :class="{ 'active': marca.proveedores.includes(prov.id) }"
            @click="toggleProveedor(prov.id)"
          >
            <Check v-if="marca.proveedores.includes(prov.id)" :size="14" class="check-icon" />
            {{ prov.nombre }}
          </div>
          
          <div v-if="proveedoresDisponibles.length === 0" class="no-data">
            <Loader2 class="btn-spinner" :size="16" /> Cargando proveedores...
          </div>
        </div>
      </div>

      <div class="input-group">
        <label>Estado</label>
        <div class="radio-group-horizontal">
          <div 
            class="radio-option"
            :class="{ 'selected': marca.estado === 'activo' }"
            @click="marca.estado = 'activo'"
          >
            <div class="radio-custom-large" :class="{ 'selected': marca.estado === 'activo' }">
              <Check v-if="marca.estado === 'activo'" :size="14" />
            </div>
            <div class="radio-content">
              <div class="radio-header">
                <div class="radio-title">Activo</div>
                <span class="radio-badge estado-success">VISIBLE</span>
              </div>
            </div>
          </div>

          <div 
            class="radio-option"
            :class="{ 'selected': marca.estado === 'inactivo' }"
            @click="marca.estado = 'inactivo'"
          >
            <div class="radio-custom-large" :class="{ 'selected': marca.estado === 'inactivo' }">
              <Check v-if="marca.estado === 'inactivo'" :size="14" />
            </div>
            <div class="radio-content">
              <div class="radio-header">
                <div class="radio-title">Inactivo</div>
                <span class="radio-badge estado-danger">OCULTO</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <button 
      @click="guardarCambios" 
      :disabled="cargando" 
      class="btn-registrar-premium"
      :class="{'btn-processing': cargando}"
    >
      <span v-if="!cargando" class="btn-content">
        <CheckCircle2 :size="20" />
        Guardar Cambios
      </span>
      <span v-else class="btn-content">
        <Loader2 :size="20" class="btn-spinner" />
        Guardando...
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Award, ArrowLeft, ClipboardList, Tag, 
  FileText, CheckCircle2, Loader2, 
  Check, ToggleLeft
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

// OBTENER ID DIRECTAMENTE DE LA RUTA
const marcaId = route.params.id

const marca = reactive({
  nombre: '',
  descripcion: '',
  estado: 'activo',
  proveedores: [] // Array de IDs
})

const errores = ref({ nombre: '' })
const proveedoresDisponibles = ref([])
const cargando = ref(false)

// 1. Cargar datos al iniciar
onMounted(async () => {
  if (!marcaId) {
    Swal.fire('Error', 'ID de marca no válido', 'error')
    router.push('/productos/marcas')
    return
  }
  await Promise.all([cargarProveedores(), cargarMarca()])
})

const cargarProveedores = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/proveedores/?estado=ACTIVO`)
    proveedoresDisponibles.value = res.data.results || res.data
  } catch (err) {
    console.error('Error proveedores:', err)
  }
}

const cargarMarca = async () => {
  try {
    // URL CORRECTA: Sin "/editar/" al final, coincide con tu urls.py
    const res = await axios.get(`${API_BASE}/api/marcas/${marcaId}/`)
    
    marca.nombre = res.data.nombre
    marca.descripcion = res.data.descripcion
    marca.estado = res.data.estado
    // El backend ahora devuelve los IDs en 'proveedores'
    marca.proveedores = res.data.proveedores || []
    
  } catch (err) {
    console.error('Error cargando marca:', err)
    Swal.fire('Error', 'No se pudo cargar la marca', 'error')
    router.push('/productos/marcas')
  }
}

const toggleProveedor = (id) => {
  const index = marca.proveedores.indexOf(id)
  if (index === -1) marca.proveedores.push(id)
  else marca.proveedores.splice(index, 1)
}

const validarNombre = () => {
  errores.value.nombre = marca.nombre.trim() ? '' : 'El nombre es obligatorio'
}

const guardarCambios = async () => {
  validarNombre()
  if (errores.value.nombre) return

  cargando.value = true
  try {
    const payload = {
      nombre: marca.nombre.trim(),
      descripcion: marca.descripcion.trim(),
      estado: marca.estado,
      proveedores: marca.proveedores
    }

    await axios.put(`${API_BASE}/api/marcas/${marcaId}/`, payload)
    
    await Swal.fire({
      icon: 'success',
      title: '¡Actualizado!',
      text: 'Marca modificada correctamente',
      timer: 1500,
      showConfirmButton: false,
      background: '#fff',
      color: '#1a1a1a'
    })
    
    router.push('/productos/marcas')

  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'No se pudo guardar los cambios', 'error')
  } finally {
    cargando.value = false
  }
}

const cancelar = () => router.push('/productos/marcas')
</script>

<style scoped>
/* ESTILOS EXACTAMENTE IGUALES A REGISTRARMARCA.VUE */
.pedido-container { max-width: 1000px; margin: 0 auto; padding: 25px; background: #fff; border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); font-family: 'Segoe UI', sans-serif; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #f1f3f4; }
.header-section h2 { margin: 0; color: #1a1a1a; font-size: 1.8em; font-weight: 700; display: flex; align-items: center; gap: 12px; }
.header-icon { color: #007bff; }
.btn-back { background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 8px; transition: 0.3s; }
.btn-back:hover { background: #5a6268; }

.card-modern { background: #fff; border-radius: 16px; border: 2px solid #f1f3f4; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
.card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #f1f3f4; }
.card-icon { background: linear-gradient(135deg, #007bff, #0056b3); padding: 10px; border-radius: 10px; color: white; display: flex; }
.card-header h3 { margin: 0; color: #1a1a1a; font-size: 1.3em; font-weight: 700; }

.input-group { margin-bottom: 20px; }
.input-group label { display: flex; align-items: center; gap: 8px; font-weight: 600; margin-bottom: 8px; color: #495057; }
.input-modern, .textarea-modern { width: 100%; padding: 12px 16px; border-radius: 10px; border: 2px solid #e1e5e9; background: #f8f9fa; font-size: 14px; color: #1a1a1a; transition: 0.3s; }
.input-modern:focus, .textarea-modern:focus { border-color: #007bff; background: #fff; box-shadow: 0 0 0 3px rgba(0,123,255,0.1); outline: none; }
.campo-invalido { border-color: #dc3545 !important; background: rgba(220,53,69,0.05) !important; }
.mensaje-error { color: #dc3545; font-size: 0.85rem; margin-top: 6px; }

/* CHIPS PROVEEDORES */
.chips-wrapper { display: flex; flex-wrap: wrap; gap: 10px; padding: 15px; border: 2px solid #e1e5e9; border-radius: 12px; background: #f8f9fa; min-height: 60px; }
.chip-item { display: flex; align-items: center; gap: 8px; background: #fff; border: 1px solid #ced4da; padding: 8px 16px; border-radius: 50px; color: #495057; font-size: 0.9rem; cursor: pointer; transition: 0.2s; user-select: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.chip-item:hover { transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-color: #adb5bd; }
.chip-item.active { background: linear-gradient(135deg, #007bff, #0056b3); border-color: #0056b3; color: white; box-shadow: 0 4px 10px rgba(0,123,255,0.3); }
.check-icon { font-weight: bold; }
.no-data { color: #6c757d; font-style: italic; font-size: 0.9rem; display: flex; align-items: center; gap: 8px; }

/* Radio Buttons */
.radio-group-horizontal { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.radio-option { border: 2px solid #e9ecef; border-radius: 12px; padding: 15px; cursor: pointer; display: flex; gap: 12px; align-items: center; background: #fff; transition: 0.3s; }
.radio-option:hover { border-color: #007bff; transform: translateY(-2px); }
.radio-option.selected { border-color: #007bff; background: #e7f3ff; }
.radio-custom-large { width: 24px; height: 24px; border: 2px solid #dee2e6; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: 0.3s; }
.radio-custom-large.selected { background: #007bff; border-color: #007bff; color: white; }
.radio-header { display: flex; justify-content: space-between; width: 100%; align-items: center; }
.radio-title { font-weight: 600; color: #1a1a1a; }
.radio-badge { font-size: 0.7em; padding: 4px 8px; border-radius: 12px; font-weight: 700; }
.estado-success { background: rgba(16,185,129,0.1); color: #10b981; }
.estado-danger { background: rgba(239,68,68,0.1); color: #ef4444; }

/* Botón */
.btn-registrar-premium { width: 100%; background: linear-gradient(135deg, #007bff, #0056b3); color: white; font-size: 1.1em; padding: 16px; border: none; border-radius: 12px; cursor: pointer; transition: 0.3s; margin-top: 20px; font-weight: 600; box-shadow: 0 4px 15px rgba(0,123,255,0.3); }
.btn-registrar-premium:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,123,255,0.4); }
.btn-registrar-premium:disabled { background: #6c757d; cursor: not-allowed; opacity: 0.7; }
.btn-content { display: flex; align-items: center; justify-content: center; gap: 10px; }
.btn-spinner { animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 768px) {
  .pedido-container { padding: 15px; }
  .header-section { flex-direction: column; gap: 15px; align-items: stretch; }
  .radio-group-horizontal { grid-template-columns: 1fr; }
}
</style>