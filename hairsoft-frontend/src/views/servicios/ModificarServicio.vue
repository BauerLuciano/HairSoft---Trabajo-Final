<template>
  <div class="servicio-container">
    
    <div v-if="cargandoDatos" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando información del servicio...</p>
    </div>

    <div v-else>
      <div class="header-section">
        <h2>
          <Scissors class="header-icon" />
          Editar Servicio
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
          <h3>Información del Servicio</h3>
        </div>

        <div class="input-row">
          <div class="input-group full-width">
            <label class="input-label">
              <Tag :size="16" />
              Nombre del Servicio *
            </label>
            <input
              v-model="form.nombre"
              type="text"
              required
              placeholder="Ej: Corte de Cabello..."
              class="input-modern"
              @blur="validarNombre"
              :class="{ 'campo-invalido': errores.nombre }"
            />
            <div class="mensaje-error" v-if="errores.nombre">
              <span class="icono-error">!</span>
              {{ errores.nombre }}
            </div>
          </div>
        </div>

        <div class="form-grid">
          <div class="input-group">
            <label class="input-label">
              <DollarSign :size="16" />
              Precio *
            </label>
            <div class="input-with-icon">
              <span class="input-prefix">$</span>
              <input
                v-model.number="form.precio"
                type="number"
                step="0.01"
                required
                class="input-modern with-prefix"
                @blur="validarPrecio"
                :class="{ 'campo-invalido': errores.precio }"
              />
            </div>
            <div class="mensaje-error" v-if="errores.precio">
              <span class="icono-error">!</span>
              {{ errores.precio }}
            </div>
          </div>

          <div class="input-group">
            <label class="input-label">
              <Clock :size="16" />
              Duración (min) *
            </label>
            <div class="input-with-icon">
              <input
                v-model.number="form.duracion"
                type="number"
                min="1"
                required
                class="input-modern with-suffix"
                @blur="validarDuracion"
              />
              <span class="input-suffix">min</span>
            </div>
            <div class="mensaje-error" v-if="errores.duracion">
              {{ errores.duracion }}
            </div>
          </div>
          
          <div class="input-group">
            <label class="input-label">
              <Percent :size="16" />
              Comisión Peluquero
            </label>
            <div class="input-with-icon">
              <input
                v-model.number="form.porcentaje_comision"
                type="number"
                min="0"
                max="100"
                step="0.01"
                placeholder="0"
                class="input-modern with-suffix"
              />
              <span class="input-suffix">%</span>
            </div>
          </div>
        </div>

        <div class="input-row">
          <div class="input-group full-width">
            <label class="input-label">
              <Layers :size="16" />
              Categoría
            </label>
            <select v-model="form.categoria" class="select-modern">
              <option :value="null">-- Seleccione una categoría --</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                {{ cat.nombre }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="card-modern">
        <div class="card-header">
          <div class="card-icon">
            <FileText :size="20" />
          </div>
          <h3>Descripción (Opcional)</h3>
        </div>
        <div class="input-group full-width">
          <textarea
            v-model="form.descripcion"
            rows="3"
            placeholder="Detalles del servicio..."
            class="textarea-modern"
          ></textarea>
          <div class="contador-caracteres">{{ form.descripcion.length }}/500</div>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="cancelar" class="btn-cancelar">
          <X :size="18" /> Cancelar
        </button>
        
        <button 
          @click="actualizarServicio" 
          :disabled="!formularioValido || cargandoGuardado" 
          class="btn-registrar-premium"
        >
          <span v-if="!cargandoGuardado" class="btn-content">
            <CheckCircle2 :size="20" /> Guardar Cambios
          </span>
          <span v-else class="btn-content">
            <Loader2 :size="20" class="btn-spinner" /> Guardando...
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Scissors, ArrowLeft, ClipboardList, Tag, DollarSign, Clock,
  Layers, FileText, CheckCircle2, Loader2, X,
  Percent
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const servicioId = route.params.id
const API_BASE = 'http://127.0.0.1:8000'

const form = reactive({
  nombre: '',
  precio: 0,
  porcentaje_comision: 0,
  duracion: 30,
  categoria: null,
  descripcion: ''
})

const errores = reactive({ nombre: '', precio: '', duracion: '' })
const categorias = ref([])
const cargandoDatos = ref(true)
const cargandoGuardado = ref(false)

const formularioValido = computed(() => {
  return form.nombre && form.precio > 0 && form.duracion > 0 && !errores.nombre && !errores.precio
})

const validarNombre = () => {
  if (!form.nombre.trim()) errores.nombre = "El nombre es obligatorio"
  else errores.nombre = ""
}
const validarPrecio = () => {
  if (form.precio <= 0) errores.precio = "Precio inválido"
  else errores.precio = ""
}
const validarDuracion = () => {
  if (form.duracion < 1) errores.duracion = "Duración inválida"
  else errores.duracion = ""
}

const cargarDatosIniciales = async () => {
  cargandoDatos.value = true
  try {
    // ✅ CORRECCIÓN: URLs actualizadas sin "/usuarios/"
    const [resCat, resServ] = await Promise.all([
      axios.get(`${API_BASE}/api/categorias/servicios/`),
      axios.get(`${API_BASE}/api/servicios/${servicioId}/`)
    ])
    
    categorias.value = resCat.data
    const s = resServ.data
    
    console.log('Datos del servicio cargados:', s) // Para debug
    
    form.nombre = s.nombre
    form.precio = s.precio
    form.porcentaje_comision = s.porcentaje_comision || 0
    form.duracion = s.duracion
    form.categoria = s.categoria
    form.descripcion = s.descripcion || ''

  } catch (err) {
    console.error('Error cargando datos:', err.response || err)
    Swal.fire({
      icon: 'error', 
      title: 'Error', 
      text: 'No se pudo cargar el servicio.',
      confirmButtonColor: '#007bff'
    })
    router.push('/servicios')
  } finally {
    cargandoDatos.value = false
  }
}

const actualizarServicio = async () => {
  validarNombre(); validarPrecio(); validarDuracion();
  
  if (errores.nombre || errores.precio) {
    Swal.fire({
      icon: 'warning',
      title: 'Formulario incompleto',
      text: 'Por favor corrige los errores antes de continuar.',
      confirmButtonColor: '#007bff'
    })
    return
  }

  cargandoGuardado.value = true
  
  const payload = {
    nombre: form.nombre.trim(),
    precio: form.precio,
    porcentaje_comision: form.porcentaje_comision || 0,
    duracion: form.duracion,
    categoria: form.categoria || null,
    descripcion: form.descripcion.trim() || ''
  }

  try {
    // ✅ CORRECCIÓN: URL actualizada y usando POST (no PUT)
    await axios.post(`${API_BASE}/api/servicios/editar/${servicioId}/`, payload)
    
    Swal.fire({
      icon: 'success', 
      title: '¡Actualizado!',
      text: 'Servicio modificado con éxito',
      showConfirmButton: false, 
      timer: 1500,
      confirmButtonColor: '#007bff'
    })
    
    setTimeout(() => router.push('/servicios'), 1500)
  } catch (err) {
    console.error('Error actualizando servicio:', err.response?.data || err)
    Swal.fire({
      icon: 'error', 
      title: 'Error', 
      text: err.response?.data?.message || 'No se pudo guardar los cambios',
      confirmButtonColor: '#007bff'
    })
  } finally {
    cargandoGuardado.value = false
  }
}

const cancelar = () => router.push('/servicios')

onMounted(() => cargarDatosIniciales())

// Limitar descripción a 500 caracteres
watch(() => form.descripcion, (nuevo) => {
  if (nuevo.length > 500) form.descripcion = nuevo.substring(0, 500)
})
</script>

<style scoped>
.servicio-container { max-width: 1000px; margin: 0 auto; padding: 25px; background: #fff; border-radius: 16px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); font-family: 'Segoe UI', sans-serif; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #f1f3f4; }
.header-section h2 { margin: 0; color: #1a1a1a; font-size: 1.8em; font-weight: 700; display: flex; align-items: center; gap: 12px; }
.header-icon { color: #007bff; }
.btn-back { background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 8px; transition: 0.3s; }
.btn-back:hover { background: #5a6268; transform: translateY(-1px); }
.card-modern { background: #fff; border-radius: 16px; border: 2px solid #f1f3f4; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); }
.card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #f1f3f4; }
.card-icon { background: linear-gradient(135deg, #007bff, #0056b3); padding: 10px; border-radius: 10px; color: white; display: flex; align-items: center; justify-content: center; }
.card-header h3 { margin: 0; font-size: 1.3em; font-weight: 700; color: #1a1a1a; }
.input-row { display: flex; gap: 20px; margin-bottom: 20px; }
.input-group { flex: 1; display: flex; flex-direction: column; }
.full-width { width: 100%; }
.input-label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: #2c3e50; font-size: 0.95em; }
.input-modern, .select-modern, .textarea-modern { width: 100%; padding: 12px 16px; border-radius: 10px; border: 2px solid #e1e5e9; background: #f8f9fa; font-size: 14px; transition: 0.3s; color: #1a1a1a; box-sizing: border-box; }
.input-modern:focus, .select-modern:focus, .textarea-modern:focus { border-color: #007bff; background: #fff; box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1); outline: none; }
.input-with-icon { position: relative; width: 100%; }
.input-prefix { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #6c757d; font-weight: 600; }
.input-suffix { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #6c757d; font-weight: 600; }
.with-prefix { padding-left: 30px; }
.with-suffix { padding-right: 50px; }
.campo-invalido { border-color: #dc3545 !important; background: rgba(220, 53, 69, 0.05) !important; }
.mensaje-error { color: #dc3545; font-size: 0.85rem; margin-top: 6px; font-weight: 500; display: flex; align-items: center; gap: 4px; }
.icono-error { width: 16px; height: 16px; background: #dc3545; color: white; border-radius: 50%; font-size: 0.7rem; font-weight: bold; display: flex; justify-content: center; align-items: center; }
.mensaje-ayuda { color: #6c757d; font-size: 0.85em; margin-top: 8px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.contador-caracteres { text-align: right; font-size: 0.8em; color: #6c757d; margin-top: 4px; }
.action-buttons { display: flex; gap: 15px; margin-top: 30px; padding-top: 25px; border-top: 2px solid #f1f3f4; }
.btn-cancelar { flex: 1; background: #dc3545; color: white; border: none; padding: 16px; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 10px; transition: 0.3s; }
.btn-cancelar:hover { background: #c82333; transform: translateY(-2px); }
.btn-registrar-premium { flex: 2; background: linear-gradient(135deg, #007bff, #0056b3); color: white; border: none; padding: 16px; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 10px; transition: 0.3s; }
.btn-registrar-premium:hover:not(:disabled) { background: linear-gradient(135deg, #0056b3, #004085); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4); }
.btn-registrar-premium:disabled { background: #6c757d; opacity: 0.7; cursor: not-allowed; }
.btn-content { display: flex; align-items: center; gap: 10px; }
.btn-spinner { animation: spin 1s linear infinite; }
.loading-state { text-align: center; padding: 50px; color: #666; font-size: 1.2em; }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #007bff; border-radius: 50%; margin: 0 auto 20px; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } .action-buttons { flex-direction: column; } }
</style>