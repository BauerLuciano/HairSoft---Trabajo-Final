<template>
  <div class="servicio-container">
    <div class="header-section">
      <h2>
        <Scissors class="header-icon" />
        {{ form.id ? 'Editar Servicio' : 'Registrar Servicio' }}
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
            placeholder="Ej: Corte de Cabello, Coloración, Peinado..."
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
              min="0.01"
              required
              placeholder="0.00"
              class="input-modern with-prefix"
              @blur="validarPrecio"
              :class="{ 'campo-invalido': errores.precio }"
            />
          </div>
          <div class="mensaje-error" v-if="errores.precio">
            <span class="icono-error">!</span>
            {{ errores.precio }}
          </div>
          <div class="mensaje-ayuda">Precio del servicio al público</div>
        </div>

        <div class="input-group">
          <label class="input-label">
            <Clock :size="16" />
            Duración *
          </label>
          <div class="input-with-icon">
            <input
              v-model.number="form.duracion"
              type="number"
              min="1"
              required
              placeholder="20"
              class="input-modern with-suffix"
              @blur="validarDuracion"
            />
            <span class="input-suffix">min</span>
          </div>
          <div class="mensaje-error" v-if="errores.duracion">
            <span class="icono-error">!</span>
            {{ errores.duracion }}
          </div>
          <div class="mensaje-ayuda">Tiempo estimado</div>
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
          <div class="mensaje-ayuda">Porcentaje que gana el profesional (Ej: 50)</div>
        </div>
      </div>

      <div class="input-row">
        <div class="input-group full-width">
          <label class="input-label">
            <Layers :size="16" />
            Categoría
          </label>
          <select
            v-model.number="form.categoria"
            class="select-modern"
            :disabled="cargandoCategorias || categorias.length === 0"
          >
            <option value="">-- Seleccione una categoría --</option>
            <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
              {{ cat.nombre }}
            </option>
          </select>
          <div class="mensaje-ayuda" v-if="!form.categoria">
            Opcional: Asigne el servicio a una categoría específica
          </div>
          <div class="mensaje-ayuda" v-else-if="categoriaSeleccionada">
            Categoría seleccionada: <strong>{{ categoriaSeleccionada.nombre }}</strong>
          </div>
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

      <div class="input-row">
        <div class="input-group full-width">
          <label class="input-label">
            <MessageSquare :size="16" />
            Detalles del servicio
          </label>
          <textarea
            v-model="form.descripcion"
            rows="3"
            placeholder="Descripción detallada del servicio, procedimiento, materiales utilizados..."
            class="textarea-modern"
          ></textarea>
          <div class="contador-caracteres">
            {{ form.descripcion.length }}/500 caracteres
          </div>
        </div>
      </div>
    </div>

    <div class="card-modern summary-card" v-if="formularioCompleto">
      <div class="card-header">
        <div class="card-icon">
          <CheckCircle :size="20" />
        </div>
        <h3>Resumen del Servicio</h3>
      </div>

      <div class="summary-content">
        <div class="summary-item">
          <span class="summary-label"><Tag :size="14" /> Nombre:</span>
          <span class="summary-value">{{ form.nombre }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label"><DollarSign :size="14" /> Precio:</span>
          <span class="summary-value precio">${{ formatPrecio(form.precio) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label"><Clock :size="14" /> Duración:</span>
          <span class="summary-value duracion">{{ form.duracion }} minutos</span>
        </div>
        <div class="summary-item">
          <span class="summary-label"><Percent :size="14" /> Comisión:</span>
          <span class="summary-value">{{ form.porcentaje_comision || 0 }}%</span>
        </div>
        <div class="summary-item" v-if="categoriaSeleccionada">
          <span class="summary-label"><Layers :size="14" /> Categoría:</span>
          <span class="summary-value categoria">{{ categoriaSeleccionada.nombre }}</span>
        </div>
      </div>
    </div>

    <div class="action-buttons">
      <button @click="cancelar" class="btn-cancelar">
        <X :size="18" /> Cancelar
      </button>
      
      <button 
        @click="guardarServicio" 
        :disabled="!formularioValido || cargando" 
        class="btn-registrar-premium"
        :class="{'btn-processing': cargando}"
      >
        <span v-if="!cargando" class="btn-content">
          <CheckCircle2 :size="20" />
          {{ form.id ? 'Actualizar Servicio' : 'Registrar Servicio' }}
        </span>
        <span v-else class="btn-content">
          <Loader2 :size="20" class="btn-spinner" />
          Procesando...
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Scissors, ArrowLeft, ClipboardList, Tag, DollarSign, Clock,
  Layers, FileText, CheckCircle, CheckCircle2, Loader2, X,
  MessageSquare, Percent
} from 'lucide-vue-next'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const props = defineProps({
  servicioEditar: Object
})

const emit = defineEmits(['actualizar', 'cancelar'])

const form = reactive({
  id: null,
  nombre: '',
  precio: 0,
  porcentaje_comision: 0, // ✅ Campo nuevo inicializado
  duracion: 30,
  categoria: null,
  descripcion: ''
})

const errores = reactive({
  nombre: '',
  precio: '',
  duracion: ''
})

const categorias = reactive([])
const cargando = ref(false)
const cargandoCategorias = ref(false)

const formularioValido = computed(() => {
  return (
    form.nombre.trim() &&
    form.precio > 0 &&
    form.duracion >= 1 &&
    !errores.nombre &&
    !errores.precio &&
    !errores.duracion
  )
})

const formularioCompleto = computed(() => {
  return form.nombre.trim() && form.precio > 0 && form.duracion >= 1
})

const categoriaSeleccionada = computed(() => {
  return categorias.find(cat => cat.id === form.categoria)
})

const validarNombre = () => {
  const valor = form.nombre.trim()
  if (!valor) errores.nombre = "El nombre es obligatorio"
  else if (valor.length < 2) errores.nombre = "El nombre debe tener al menos 2 caracteres"
  else errores.nombre = ""
}

const validarPrecio = () => {
  if (!form.precio || form.precio <= 0) errores.precio = "El precio debe ser mayor a 0"
  else errores.precio = ""
}

const validarDuracion = () => {
  if (!form.duracion || form.duracion < 1) errores.duracion = "La duración debe ser al menos 1 minuto"
  else errores.duracion = ""
}

const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  return parseFloat(precio).toFixed(2)
}

const cargarCategorias = async () => {
  cargandoCategorias.value = true
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/categorias/servicios/`)
    categorias.length = 0
    categorias.push(...res.data)
  } catch (err) {
    console.error('Error cargando categorías:', err)
  } finally {
    cargandoCategorias.value = false
  }
}

watch(() => props.servicioEditar, (nuevo) => {
  if (nuevo) {
    form.id = nuevo.id
    form.nombre = nuevo.nombre
    form.precio = nuevo.precio
    form.porcentaje_comision = nuevo.porcentaje_comision || 0 // ✅ Cargar valor existente
    form.duracion = nuevo.duracion || 30
    form.categoria = nuevo.categoria?.id || null
    form.descripcion = nuevo.descripcion || ''
  }
}, { immediate: true })

watch(() => form.descripcion, (nuevo) => {
  if (nuevo.length > 500) form.descripcion = nuevo.substring(0, 500)
})

const guardarServicio = async () => {
  validarNombre(); validarPrecio(); validarDuracion();

  if (errores.nombre || errores.precio || errores.duracion) {
    Swal.fire({
      icon: 'warning', title: 'Formulario incompleto', text: 'Por favor corrige los errores.', confirmButtonColor: '#007bff'
    })
    return
  }

  cargando.value = true

  const payload = {
    nombre: form.nombre.trim(),
    precio: form.precio,
    porcentaje_comision: form.porcentaje_comision || 0, // ✅ Enviar al backend
    duracion: form.duracion,
    categoria: form.categoria || null,
    descripcion: form.descripcion.trim() || ''
  }

  try {
    if (form.id) {
      await axios.post(`${API_BASE}/usuarios/api/servicios/editar/${form.id}/`, payload)
      Swal.fire({ icon: 'success', title: 'Servicio actualizado', showConfirmButton: false, timer: 1500 })
    } else {
      await axios.post(`${API_BASE}/usuarios/api/servicios/crear/`, payload)
      Swal.fire({ icon: 'success', title: 'Servicio creado', showConfirmButton: false, timer: 1500 })
    }
    
    resetForm()
    emit('actualizar')
    setTimeout(() => router.push('/servicios'), 1500)

  } catch (err) {
    console.error('Error guardando servicio:', err)
    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo guardar el servicio.' })
  } finally {
    cargando.value = false
  }
}

const resetForm = () => {
  Object.assign(form, { id: null, nombre: '', precio: 0, porcentaje_comision: 0, duracion: 30, categoria: null, descripcion: '' })
  Object.assign(errores, { nombre: '', precio: '', duracion: '' })
}

const cancelar = () => router.push('/servicios')

onMounted(() => cargarCategorias())
</script>

<style scoped>
/* ESTILOS PERFECTAMENTE ALINEADOS (TUYOS ORIGINALES) */
.servicio-container { max-width: 1000px; margin: 0 auto; padding: 25px; background: #fff; border-radius: 16px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #f1f3f4; }
.header-section h2 { margin: 0; color: #1a1a1a; font-size: 1.8em; font-weight: 700; display: flex; align-items: center; gap: 12px; }
.header-icon { color: #007bff; }
.btn-back { background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s ease; display: flex; align-items: center; gap: 8px; }
.btn-back:hover { background: #5a6268; transform: translateY(-1px); }
.card-modern { background: #fff; border-radius: 16px; border: 2px solid #f1f3f4; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); transition: all 0.3s ease; }
.card-modern:hover { border-color: #007bff; box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15); }
.card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #f1f3f4; }
.card-icon { background: linear-gradient(135deg, #007bff, #0056b3); padding: 10px; border-radius: 10px; color: white; display: flex; align-items: center; justify-content: center; }
.card-header h3 { margin: 0; color: #1a1a1a; font-size: 1.3em; font-weight: 700; flex: 1; }
.input-row { display: flex; gap: 20px; margin-bottom: 20px; }
.input-row:last-child { margin-bottom: 0; }
.input-group { flex: 1; display: flex; flex-direction: column; }
.input-group.full-width { width: 100%; }
.input-label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 600; color: #2c3e50; font-size: 0.95em; }
.select-modern, .input-modern, .textarea-modern { width: 100%; padding: 12px 16px; border-radius: 10px; border: 2px solid #e1e5e9; background: #f8f9fa; font-size: 14px; transition: all 0.3s ease; color: #1a1a1a; box-sizing: border-box; }
.select-modern:focus, .input-modern:focus, .textarea-modern:focus { border-color: #007bff; background: #fff; box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1); outline: none; }
.input-with-icon { position: relative; width: 100%; }
.input-with-icon .input-prefix { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #6c757d; font-weight: 600; z-index: 1; }
.input-with-icon .input-suffix { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #6c757d; font-weight: 600; z-index: 1; }
.input-with-icon .input-modern.with-prefix { padding-left: 30px; }
.input-with-icon .input-modern.with-suffix { padding-right: 50px; }
.textarea-modern { min-height: 100px; resize: vertical; line-height: 1.5; }
.contador-caracteres { text-align: right; font-size: 0.8em; color: #6c757d; margin-top: 4px; }
.campo-invalido { border-color: #dc3545 !important; background: rgba(220, 53, 69, 0.05) !important; }
.campo-invalido:focus { box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1) !important; }
.mensaje-error { color: #dc3545; font-size: 0.85rem; margin-top: 6px; font-weight: 500; display: flex; align-items: center; gap: 4px; min-height: 20px; }
.icono-error { display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px; background: #dc3545; color: white; border-radius: 50%; font-size: 0.7rem; font-weight: bold; flex-shrink: 0; }
.mensaje-ayuda { color: #6c757d; font-size: 0.85em; margin-top: 8px; line-height: 1.4; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.summary-card { background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-color: #28a745; }
.summary-card:hover { border-color: #28a745; box-shadow: 0 6px 20px rgba(40, 167, 69, 0.15); }
.summary-content { background: white; padding: 20px; border-radius: 12px; border: 1px solid #dee2e6; }
.summary-item { display: flex; align-items: flex-start; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px dashed #dee2e6; }
.summary-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.summary-label { font-weight: 600; color: #495057; width: 140px; flex-shrink: 0; display: flex; align-items: center; gap: 6px; }
.summary-value { color: #1a1a1a; flex: 1; line-height: 1.5; }
.summary-value.precio { color: #28a745; font-weight: 700; font-size: 1.1em; }
.summary-value.duracion { color: #007bff; font-weight: 600; }
.summary-value.categoria { color: #6f42c1; font-weight: 600; }
.summary-value.descripcion { color: #6c757d; font-style: italic; line-height: 1.5; }
.action-buttons { display: flex; gap: 15px; margin-top: 30px; padding-top: 25px; border-top: 2px solid #f1f3f4; }
.btn-cancelar { flex: 1; background: #dc3545; color: white; border: none; padding: 16px 24px; border-radius: 12px; cursor: pointer; font-weight: 600; font-size: 1em; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; gap: 10px; box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2); }
.btn-cancelar:hover { background: #c82333; transform: translateY(-2px); box-shadow: 0 6px 18px rgba(220, 53, 69, 0.3); }
.btn-registrar-premium { flex: 2; background: linear-gradient(135deg, #007bff, #0056b3); color: white; font-size: 1.1em; padding: 18px; border: none; border-radius: 12px; cursor: pointer; transition: all 0.3s ease; font-weight: 600; box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3); position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; gap: 10px; }
.btn-registrar-premium:hover:not(:disabled):not(.btn-processing) { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4); background: linear-gradient(135deg, #0056b3, #004085); }
.btn-registrar-premium:disabled, .btn-registrar-premium.btn-processing { background: #6c757d; cursor: not-allowed; opacity: 0.7; transform: none; }
.btn-content { display: flex; align-items: center; justify-content: center; gap: 10px; }
.btn-spinner { animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@media (max-width: 768px) { .servicio-container { padding: 15px; } .header-section { flex-direction: column; gap: 15px; align-items: stretch; } .form-grid { grid-template-columns: 1fr; gap: 15px; } .input-row { flex-direction: column; gap: 15px; } .action-buttons { flex-direction: column; } .summary-item { flex-direction: column; gap: 5px; } .summary-label { width: 100%; } }
@media (max-width: 480px) { .card-modern { padding: 20px; } .btn-cancelar, .btn-registrar-premium { padding: 14px 20px; font-size: 0.95em; } .header-section h2 { font-size: 1.5em; } }
</style>