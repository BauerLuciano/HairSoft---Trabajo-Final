<template>
  <div class="pedido-container">
    <div class="header-section">
      <h2>
        <Shield class="header-icon" />
        Modificar Rol
      </h2>
      <button @click="cancelar" class="btn-back">
        <ArrowLeft :size="18" />
        Volver
      </button>
    </div>

    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon"><UserCog :size="20" /></div>
        <h3>Información del Rol</h3>
      </div>
      <div class="input-group">
        <label>Nombre del Rol *</label>
        <input 
          v-model="rol.nombre" type="text" class="input-modern"
          @blur="validarNombre" :class="{ 'campo-invalido': errores.nombre }"
        />
        <div class="mensaje-error" v-if="errores.nombre">{{ errores.nombre }}</div>
      </div>
      <div class="input-group">
        <label>Descripción</label>
        <textarea v-model="rol.descripcion" rows="2" class="textarea-modern"></textarea>
      </div>
    </div>

    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon"><Lock :size="20" /></div>
        <h3>Permisos Asignados</h3>
        <span class="badge-count">{{ rol.permisos.length }}</span>
      </div>

      <div v-if="permisosDisponibles.length > 0" class="permisos-grid">
        <div 
          v-for="permiso in permisosDisponibles" 
          :key="permiso.id" 
          class="producto-item"
          :class="{ 'selected': rol.permisos.includes(permiso.id) }"
          @click="togglePermiso(permiso.id)"
        >
          <div class="producto-seleccion">
            <div class="producto-checkbox" :class="{ 'checked': rol.permisos.includes(permiso.id) }">
              <Check v-if="rol.permisos.includes(permiso.id)" :size="14" />
            </div>
          </div>
          <div class="producto-info">
            <span class="producto-nombre">{{ permiso.nombre }}</span>
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
        Actualizar Rol
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
import { Shield, ArrowLeft, UserCog, Lock, Check, CheckCircle2, Loader2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'
const rolId = route.params.id

const rol = reactive({ nombre: '', descripcion: '', permisos: [], activo: true })
const errores = reactive({ nombre: '' })
const permisosDisponibles = ref([])
const cargando = ref(false)

onMounted(async () => {
  if (!rolId) return router.push('/roles')
  await cargarPermisos()
  await cargarRol()
})

const cargarPermisos = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/permisos/`)
    permisosDisponibles.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const cargarRol = async () => {
  try {
    // 🔥 URL CORRECTA (ya arreglada en urls.py)
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/${rolId}/`)
    
    rol.nombre = res.data.nombre
    rol.descripcion = res.data.descripcion
    rol.activo = res.data.activo
    rol.permisos = res.data.permisos || []
    
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'No se pudo cargar el rol', 'error')
    router.push('/roles')
  }
}

const togglePermiso = (id) => {
  const i = rol.permisos.indexOf(id)
  if (i === -1) rol.permisos.push(id)
  else rol.permisos.splice(i, 1)
}

const validarNombre = () => {
  errores.nombre = rol.nombre.trim() ? '' : 'El nombre es obligatorio'
}

const guardarCambios = async () => {
  validarNombre()
  if (errores.nombre) return

  cargando.value = true
  try {
    // 🔥 Usamos PUT para actualizar
    await axios.put(`${API_BASE}/usuarios/api/roles/${rolId}/`, rol)
    
    await Swal.fire({
      icon: 'success',
      title: '¡Rol Actualizado!',
      text: 'Los cambios se guardaron correctamente',
      timer: 1500,
      showConfirmButton: false,
      confirmButtonColor: '#0ea5e9'
    })
    router.push('/roles')
  } catch (err) {
    const msg = err.response?.data?.message || 'Error al guardar cambios'
    if (msg.includes('existe')) errores.nombre = msg
    else Swal.fire('Error', msg, 'error')
  } finally {
    cargando.value = false
  }
}

const cancelar = () => router.push('/roles')
</script>

<style scoped>
/* MISMOS ESTILOS QUE PEDISTE, NO LOS TOCO */
.pedido-container { max-width: 800px; margin: 0 auto; padding: 25px; background: #fff; border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); font-family: 'Segoe UI', sans-serif; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px solid #f1f3f4; padding-bottom: 20px; }
.header-section h2 { margin: 0; color: #1a1a1a; font-size: 1.8em; font-weight: 700; display: flex; align-items: center; gap: 12px; }
.header-icon { color: #007bff; }
.btn-back { background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; display: flex; gap: 8px; align-items: center; }
.card-modern { background: #fff; border-radius: 16px; border: 2px solid #f1f3f4; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
.card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #f1f3f4; }
.card-icon { background: linear-gradient(135deg, #007bff, #0056b3); padding: 10px; border-radius: 10px; color: white; display: flex; }
.card-header h3 { margin: 0; font-size: 1.3em; font-weight: 700; color: #1a1a1a; }
.badge-count { background: #28a745; color: white; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.9em; margin-left: auto; }
.input-group { margin-bottom: 20px; }
.input-group label { display: block; font-weight: 600; margin-bottom: 8px; color: #495057; }
.input-modern, .textarea-modern { width: 100%; padding: 12px 16px; border-radius: 10px; border: 2px solid #e1e5e9; background: #f8f9fa; font-size: 14px; transition: 0.3s; }
.input-modern:focus, .textarea-modern:focus { border-color: #007bff; background: #fff; outline: none; }
.campo-invalido { border-color: #dc3545 !important; background: rgba(220,53,69,0.05) !important; }
.mensaje-error { color: #dc3545; font-size: 0.85rem; margin-top: 6px; }
.permisos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
.producto-item { display: flex; align-items: flex-start; gap: 12px; padding: 16px; border: 2px solid #e9ecef; border-radius: 12px; cursor: pointer; transition: 0.3s; background: #fff; }
.producto-item:hover { border-color: #007bff; transform: translateY(-2px); }
.producto-item.selected { border-color: #007bff; background: #e7f3ff; }
.producto-checkbox { width: 20px; height: 20px; border: 2px solid #dee2e6; border-radius: 6px; display: flex; align-items: center; justify-content: center; transition: 0.3s; color: transparent; flex-shrink: 0; margin-top: 2px; }
.producto-checkbox.checked { background: #007bff; border-color: #007bff; color: white; }
.producto-nombre { font-weight: 600; color: #1a1a1a; font-size: 0.95em; }
.btn-registrar-premium { width: 100%; background: linear-gradient(135deg, #007bff, #0056b3); color: white; font-size: 1.1em; padding: 18px; border: none; border-radius: 12px; cursor: pointer; transition: 0.3s; margin-top: 10px; font-weight: 600; box-shadow: 0 4px 15px rgba(0,123,255,0.3); }
.btn-registrar-premium:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,123,255,0.4); }
.btn-registrar-premium:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-content { display: flex; align-items: center; justify-content: center; gap: 10px; }
.btn-spinner { animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>