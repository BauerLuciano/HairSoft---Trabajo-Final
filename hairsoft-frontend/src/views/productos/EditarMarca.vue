<template>
  <div class="pedido-container">
    <div class="header-section">
      <h2>
        <Edit3 class="header-icon" />
        Editar Marca
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
        <div class="mensaje-ayuda">El nombre debe ser único en el sistema</div>
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
    </div>

    <!-- Estado -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <ToggleLeft :size="20" />
        </div>
        <h3>Estado</h3>
      </div>

      <div class="radio-group-horizontal">
        <div class="radio-option" @click="marca.estado = 'activo'">
          <div class="radio-custom-large" :class="{ 'selected': marca.estado === 'activo' }">
            <div class="radio-check" v-if="marca.estado === 'activo'">
              <Check :size="16" />
            </div>
          </div>
          <div class="radio-content">
            <div class="radio-header">
              <span class="radio-title">Activo</span>
              <span class="radio-badge estado-success">Disponible</span>
            </div>
            <p class="radio-description">La marca estará disponible para asignar a productos</p>
          </div>
        </div>

        <div class="radio-option" @click="marca.estado = 'inactivo'">
          <div class="radio-custom-large" :class="{ 'selected': marca.estado === 'inactivo' }">
            <div class="radio-check" v-if="marca.estado === 'inactivo'">
              <Check :size="16" />
            </div>
          </div>
          <div class="radio-content">
            <div class="radio-header">
              <span class="radio-title">Inactivo</span>
              <span class="radio-badge estado-danger">Oculto</span>
            </div>
            <p class="radio-description">La marca no estará disponible temporalmente</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Botón Final -->
    <button 
      @click="actualizarMarca" 
      :disabled="!formularioValido || cargando" 
      class="btn-registrar-premium"
      :class="{'btn-processing': cargando}"
    >
      <span v-if="!cargando" class="btn-content">
        <Save :size="20" />
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
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Edit3, ArrowLeft, ClipboardList, Tag, 
  FileText, Save, Loader2, Check, 
  ToggleLeft, Package, Truck, AlertTriangle
} from 'lucide-vue-next'

const emit = defineEmits(['marca-actualizada', 'cancelar'])
const API_BASE = 'http://127.0.0.1:8000'

const props = defineProps({
  marca: {
    type: Object,
    required: true
  }
})

const marca = ref({
  nombre: '',
  descripcion: '',
  estado: 'activo',
  productos_count: 0,
  total_proveedores: 0,
  proveedores_nombres: []
})

// 📌 Errores por campo
const errores = ref({
  nombre: ''
})

const cargando = ref(false)
const nombreOriginal = ref('')

// Cargar datos de la marca
onMounted(() => {
  if (props.marca) {
    // Cargar todos los datos de la marca
    marca.value = {
      nombre: props.marca.nombre || '',
      descripcion: props.marca.descripcion || '',
      estado: props.marca.estado || 'activo',
      productos_count: props.marca.productos_count || 0,
      total_proveedores: props.marca.total_proveedores || 0,
      proveedores_nombres: props.marca.proveedores_nombres || []
    }
    nombreOriginal.value = props.marca.nombre || ''
    
    console.log('📥 Datos de marca cargados:', marca.value)
  }
})

// ------------------------------
// VALIDACIONES
// ------------------------------
const validarNombre = async () => {
  const valor = marca.value.nombre.trim()
  
  if (!valor) {
    errores.value.nombre = "El nombre es obligatorio"
    return
  }
  
  if (valor.length < 2) {
    errores.value.nombre = "El nombre debe tener al menos 2 caracteres"
    return
  }
  
  if (valor.length > 50) {
    errores.value.nombre = "El nombre no puede exceder los 50 caracteres"
    return
  }
  
  // Validar que no sea solo números
  if (/^\d+$/.test(valor)) {
    errores.value.nombre = 'El nombre no puede ser solo números'
    return
  }
  
  // Validar caracteres permitidos
  if (!/^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-&.]+$/.test(valor)) {
    errores.value.nombre = 'Solo se permiten letras, números, espacios y los caracteres: - & .'
    return
  }
  
  // Solo validar unicidad si cambió el nombre
  if (valor === nombreOriginal.value) {
    errores.value.nombre = ""
    return
  }
  
  // VALIDAR DUPLICADO
  try {
    const response = await axios.get(`${API_BASE}/api/marcas/`)
    const marcasExistentes = response.data
    
    const duplicado = marcasExistentes.find(m => 
      m.nombre.toLowerCase() === valor.toLowerCase() &&
      m.id !== props.marca.id // Excluir la marca actual
    )
    
    if (duplicado) {
      errores.value.nombre = `Ya existe una marca con el nombre "${valor}"`
      return
    }
  } catch (error) {
    console.error('Error validando:', error)
  }

  errores.value.nombre = ""
}

// Validar formulario completo
const validarFormulario = () => {
  validarNombre()
  return Object.values(errores.value).every(error => !error)
}

const formularioValido = computed(() => {
  return (
    marca.value.nombre.trim() &&
    Object.values(errores.value).every(error => !error)
  )
})

// Watch para validar nombre cuando cambia
watch(() => marca.value.nombre, validarNombre)

// ================================
// ACTUALIZAR MARCA
// ================================
const actualizarMarca = async () => {
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
      nombre: marca.value.nombre.trim(),
      descripcion: marca.value.descripcion.trim(),
      estado: marca.value.estado
    }

    console.log('📤 Enviando datos:', payload)
    console.log('URL:', `${API_BASE}/api/marcas/${props.marca.id}/`)

    const response = await axios.put(
      `${API_BASE}/api/marcas/${props.marca.id}/`, 
      payload
    )

    Swal.fire({
      icon: 'success',
      title: '✅ Marca actualizada',
      text: 'La marca se actualizó correctamente',
      confirmButtonColor: '#007bff',
      background: '#fff',
      color: '#1a1a1a',
      confirmButtonText: 'Continuar'
    }).then((result) => {
      if (result.isConfirmed) {
        emit("marca-actualizada", response.data)
      }
    })

  } catch (err) {
    console.error('Error:', err.response?.data || err)
    
    let mensaje = 'Error al guardar la marca'
    const data = err.response?.data
    
    if (data) {
      if (data.nombre) mensaje = data.nombre
      else if (data.non_field_errors) mensaje = data.non_field_errors
      else if (typeof data === 'string') mensaje = data
      else if (typeof data === 'object') {
        mensaje = Object.entries(data)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
          .join('\n')
      }
    }
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: mensaje,
      confirmButtonColor: '#007bff'
    })
  } finally {
    cargando.value = false
  }
}

const cancelar = () => emit("cancelar")
</script>

<style scoped>
/* ESTILOS EXACTAMENTE IGUALES A REGISTRARPRODUCTO.VUE */
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

/* Inputs y selects */
.input-group {
  margin-bottom: 20px;
  color: rgb(63, 63, 63);
}

.input-modern {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
}

.input-modern:focus {
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

/* Radio buttons estilo premium */
.radio-group-horizontal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.radio-option {
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: #fff;
}

.radio-option:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.radio-option.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.radio-custom-large {
  width: 24px;
  height: 24px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-top: 2px;
}

.radio-custom-large.selected {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.radio-check {
  display: flex;
  align-items: center;
  justify-content: center;
}

.radio-content {
  flex: 1;
}

.radio-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.radio-title {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 1.1em;
}

.radio-badge {
  font-size: 0.75em;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.estado-success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.estado-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.radio-description {
  color: #6c757d;
  font-size: 0.9em;
  line-height: 1.4;
  margin: 0;
}

/* Información de relaciones */
.relaciones-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.relacion-item {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  background: #f8f9fa;
}

.relacion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.relacion-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1a1a1a;
  font-size: 1em;
}

.relacion-valor {
  font-size: 1.5em;
  font-weight: 800;
  color: #007bff;
}

.relacion-valor.alta-cantidad {
  color: #28a745;
}

.relacion-advertencia {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid #ffc107;
  border-radius: 8px;
  color: #856404;
  font-size: 0.9em;
  margin-top: 8px;
}

.relacion-ok {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(40, 167, 69, 0.1);
  border: 1px solid #28a745;
  border-radius: 8px;
  color: #155724;
  font-size: 0.9em;
  margin-top: 8px;
}

/* Proveedores tags */
.proveedores-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.proveedor-tag {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
  border: 1px solid rgba(29, 78, 216, 0.2);
}

.mas-proveedores {
  color: #6c757d;
  font-size: 0.85em;
  font-style: italic;
  padding: 6px 12px;
}

/* Botón final premium */
.btn-registrar-premium {
  width: 100%;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  font-size: 1.1em;
  padding: 18px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 25px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-registrar-premium:hover:not(:disabled):not(.btn-processing) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
  background: linear-gradient(135deg, #20c997, #1e9e8a);
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
  
  .radio-group-horizontal {
    grid-template-columns: 1fr;
  }
  
  .radio-option {
    padding: 16px;
  }
  
  .relacion-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .radio-option {
    flex-direction: column;
    gap: 12px;
  }
  
  .radio-header {
    flex-direction: column;
    gap: 4px;
  }
  
  .proveedores-tags {
    flex-direction: column;
  }
  
  .proveedor-tag {
    width: 100%;
    text-align: center;
  }
}
</style>