<template>
  <div class="pedido-container">
    <div class="header-section">
      <h2>
        <Award class="header-icon" />
        Registrar Nueva Marca
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
            v-for="prov in proveedores" 
            :key="prov.id" 
            class="chip-item"
            :class="{ 'active': marca.proveedores.includes(prov.id) }"
            @click="toggleProveedor(prov.id)"
          >
            <Check v-if="marca.proveedores.includes(prov.id)" :size="14" class="check-icon" />
            {{ prov.nombre }}
          </div>
          
          <div v-if="proveedores.length === 0" class="no-data">
            <Loader2 class="btn-spinner" :size="16" /> Cargando proveedores...
          </div>
        </div>
      </div>
    </div>

    <button 
      @click="guardarMarca" 
      :disabled="cargando" 
      class="btn-registrar-premium"
      :class="{'btn-processing': cargando}"
    >
      <span v-if="!cargando" class="btn-content">
        <CheckCircle2 :size="20" />
        Registrar Marca
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
import { useRouter } from 'vue-router' // Importamos router para redireccionar si se usa como pagina
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Award, ArrowLeft, ClipboardList, Tag, 
  FileText, CheckCircle2, Loader2, 
  Check, ToggleLeft
} from 'lucide-vue-next'

// Definimos emits para cuando se usa como modal
const emit = defineEmits(['marca-registrada', 'cancelar'])

const isProduction = window.location.hostname.includes('vercel.app');
const API_BASE = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://127.0.0.1:8000';

const marca = reactive({
  nombre: '',
  descripcion: '',
  proveedores: []
})

const errores = reactive({ nombre: '' })
const proveedores = ref([])
const cargando = ref(false)

// Cargar proveedores al iniciar
const cargarProveedores = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/proveedores/?estado=ACTIVO`)
    if (Array.isArray(res.data)) {
      proveedores.value = res.data
    } else if (res.data.results) {
      proveedores.value = res.data.results
    } else {
      proveedores.value = []
    }
  } catch (err) {
    console.error('Error cargando proveedores', err)
  }
}

onMounted(() => {
  cargarProveedores()
})

const toggleProveedor = (id) => {
  const index = marca.proveedores.indexOf(id)
  if (index === -1) marca.proveedores.push(id)
  else marca.proveedores.splice(index, 1)
}

const validarNombre = () => {
  errores.nombre = marca.nombre.trim() ? '' : 'El nombre es obligatorio'
}

const guardarMarca = async () => {
  validarNombre()
  if (errores.nombre) return

  cargando.value = true
  try {
    // 🔥 ENVÍO CORRECTO: Nombre, Descripción y lista de IDs de proveedores
    await axios.post(`${API_BASE}/api/marcas/crear/`, {
      nombre: marca.nombre.trim(),
      descripcion: marca.descripcion.trim(),
      proveedores: marca.proveedores
    })
    
    await Swal.fire({
      icon: 'success',
      title: '¡Éxito!',
      text: 'Marca registrada correctamente',
      timer: 1500,
      showConfirmButton: false,
      background: '#fff',
      color: '#1a1a1a'
    })
    
    // Emitir evento para cerrar modal y recargar lista
    emit('marca-registrada')

  } catch (err) {
    console.error(err)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: err.response?.data?.message || 'Error al guardar la marca',
      confirmButtonColor: '#007bff'
    })
  } finally {
    cargando.value = false
  }
}

const cancelar = () => {
  emit('cancelar')
}
</script>

<style scoped>
/* ========================================
   🔥 TUS ESTILOS EXACTOS (Copiados de ModificarMarca)
   ======================================== */

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
}
</style>