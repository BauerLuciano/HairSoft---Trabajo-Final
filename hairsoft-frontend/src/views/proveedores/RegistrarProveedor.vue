<template>
  <div class="form-card">
    <div class="form-header">
      <h1>Registrar Proveedor</h1>
      <p>Completa los datos obligatorios para el alta</p>
    </div>

    <form @submit.prevent="registrarProveedor" class="form-grid" autocomplete="off">
      
      <div class="input-group">
        <div class="label-row">
          <label>Razón Social / Nombre</label>
          <span class="badge-required">Requerido</span>
        </div>
        <input 
          v-model="proveedor.nombre" 
          type="text" 
          placeholder="Ej: Distribuidora Norte S.A." 
          @blur="validarNombre"
          :class="{ 'error': errores.nombre }"
        />
        <div v-if="errores.nombre" class="field-error">{{ errores.nombre }}</div>
      </div>

      <div class="input-group">
        <div class="label-row">
          <label>CUIT</label>
          <span class="badge-required">Requerido</span>
        </div>
        <input 
          v-model="proveedor.cuit"
          type="text"
          placeholder="20-12345678-9"
          @input="formatearCuitInput"
          @blur="validarCuit"
          :class="{ 'error': errores.cuit }"
          maxlength="13"
        />
        <div v-if="errores.cuit" class="field-error">{{ errores.cuit }}</div>
      </div>

      <div class="input-group">
        <div class="label-row">
          <label>Persona de Contacto</label>
          <span class="badge-required">Requerido</span>
        </div>
        <input 
          v-model="proveedor.contacto" 
          type="text" 
          placeholder="Ej: Juan Pérez" 
          @blur="validarContacto"
          :class="{ 'error': errores.contacto }"
        />
        <div v-if="errores.contacto" class="field-error">{{ errores.contacto }}</div>
      </div>

      <div class="input-group">
        <div class="label-row">
          <label>Teléfono / Celular</label>
          <span class="badge-required">Requerido</span>
        </div>
        <input 
          v-model="proveedor.telefono" 
          type="tel" 
          placeholder="+54 9 3755 558911" 
          @blur="validarTelefono"
          @input="formatearTelefono"
          :class="{ 'error': errores.telefono }"
        />
        <div v-if="errores.telefono" class="field-error">{{ errores.telefono }}</div>
      </div>

      <div class="input-group full-width">
        <div class="label-row">
          <label>Correo Electrónico</label>
          <span class="badge-required">Requerido</span>
        </div>
        <input 
          v-model="proveedor.email" 
          type="email" 
          placeholder="contacto@empresa.com"
          @blur="validarEmail"
          :class="{ 'error': errores.email }"
        />
        <div v-if="errores.email" class="field-error">{{ errores.email }}</div>
      </div>

      <div class="input-group full-width">
        <div class="label-row">
          <label>Dirección Física</label>
          <span class="badge-optional">Opcional</span>
        </div>
        <input 
          v-model="proveedor.direccion" 
          type="text" 
          placeholder="Calle 123, Ciudad, Provincia" 
        />
      </div>

      <div class="input-group full-width">
        <div class="label-row">
          <label>Categorías que provee</label>
          <span class="badge-required">Seleccione al menos una</span>
        </div>
        
        <div class="chips-wrapper">
          <div 
            v-for="categoria in categorias" 
            :key="categoria.id" 
            class="chip-item"
            :class="{ 'active': proveedor.categorias_seleccionadas.includes(categoria.id) }"
            @click="toggleCategoria(categoria.id)"
          >
            <span class="check-icon" v-if="proveedor.categorias_seleccionadas.includes(categoria.id)">✓</span>
            {{ categoria.nombre }}
          </div>
          
          <div v-if="categorias.length === 0" class="no-data">
            Cargando categorías... (o no hay ninguna creada)
          </div>
        </div>
        
        <div v-if="errores.categorias" class="field-error">{{ errores.categorias }}</div>
      </div>

      <div class="input-group full-width">
        <div class="label-row">
          <label>Notas / Productos Específicos</label>
          <span class="badge-optional">Opcional</span>
        </div>
        <textarea
          v-model="proveedor.productos_especificos"
          class="form-textarea"
          placeholder="Ej: Solo tinturas marca X, etc."
          rows="3"
        ></textarea>
      </div>

      <div class="full-width form-actions">
        <button type="button" @click="volver" class="btn btn-secondary">
          Cancelar
        </button>
        <button type="submit" :disabled="cargando" class="btn btn-primary">
          {{ cargando ? 'Guardando...' : 'Registrar Proveedor' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

const emit = defineEmits(['proveedor-registrado', 'cancelar'])
const API_BASE = 'http://127.0.0.1:8000'

const proveedor = reactive({
  nombre: '',
  cuit: '',
  contacto: '',
  telefono: '',
  email: '',
  direccion: '',
  categorias_seleccionadas: [], 
  productos_especificos: ''
})

const errores = reactive({
  nombre: '',
  cuit: '',
  contacto: '',
  telefono: '',
  email: '',
  categorias: ''
})

const categorias = ref([])
const cargando = ref(false)

// ==========================================
// 🛡️ VALIDACIONES Y FORMATOS
// ==========================================

const validarNombre = () => {
  errores.nombre = proveedor.nombre.trim() ? '' : 'El nombre es obligatorio'
}

const validarContacto = () => {
  errores.contacto = proveedor.contacto.trim() ? '' : 'El contacto es obligatorio'
}

// ✅ AUTO-FORMATO DE CUIT (XX-XXXXXXXX-X)
const formatearCuitInput = (event) => {
  let val = event.target.value.replace(/\D/g, '') // Solo números
  
  if (val.length > 2) val = val.substring(0, 2) + '-' + val.substring(2)
  if (val.length > 11) val = val.substring(0, 11) + '-' + val.substring(11)
  if (val.length > 13) val = val.substring(0, 13) // Limitar largo total

  proveedor.cuit = val
}

const validarCuit = () => {
  const val = proveedor.cuit
  const regexCuit = /^\d{2}-\d{8}-\d{1}$/
  
  if (!val) {
    errores.cuit = 'El CUIT es obligatorio'
  } else if (!regexCuit.test(val)) {
    errores.cuit = 'Formato inválido. Debe ser XX-XXXXXXXX-X'
  } else {
    errores.cuit = ''
  }
}

// ✅ AUTO-FORMATO TELÉFONO
const formatearTelefono = () => {
  let tel = proveedor.telefono.replace(/\D/g, '')
  if (tel.length === 0) { proveedor.telefono = ''; return }
  
  if (tel.startsWith('549')) proveedor.telefono = '+54 ' + tel.slice(2)
  else if (tel.startsWith('54')) proveedor.telefono = '+54 ' + tel.slice(2)
  else if (tel.startsWith('9')) proveedor.telefono = '+54 ' + tel
  else proveedor.telefono = '+54 9' + tel
}

const validarTelefono = () => {
  const val = proveedor.telefono.trim()
  if (!val) {
    errores.telefono = 'El teléfono es obligatorio'
    return
  }
  if (!/^\+54\s?9\d{10,11}$/.test(val.replace(/\s+/g, ''))) {
    errores.telefono = 'Formato: +54 9 3755 558911'
  } else {
    errores.telefono = ''
  }
}

const validarEmail = () => {
  const val = proveedor.email.trim()
  if (!val) {
    errores.email = 'El email es obligatorio'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
    errores.email = 'Correo electrónico inválido'
  } else {
    errores.email = ''
  }
}

const validarCategorias = () => {
  errores.categorias = proveedor.categorias_seleccionadas.length === 0 
    ? 'Seleccione al menos una categoría' 
    : ''
}

const toggleCategoria = (id) => {
  const index = proveedor.categorias_seleccionadas.indexOf(id)
  if (index === -1) proveedor.categorias_seleccionadas.push(id)
  else proveedor.categorias_seleccionadas.splice(index, 1)
  validarCategorias()
}

const hayErrores = () => {
  validarNombre()
  validarCuit()
  validarContacto()
  validarTelefono()
  validarEmail()
  validarCategorias()
  return Object.values(errores).some(msg => msg !== '')
}

// ==========================================
// 📡 API
// ==========================================

const cargarCategorias = async () => {
  try {
    // 🔥 TRUCO: Agregamos ?page_size=1000 para forzar que traiga todas si hay paginación
    const res = await axios.get(`${API_BASE}/api/categorias/productos/?page_size=1000`)
    
    // Detectar si viene paginado (objeto con .results) o lista directa (array)
    let lista = []
    if (res.data.results && Array.isArray(res.data.results)) {
      lista = res.data.results
    } else if (Array.isArray(res.data)) {
      lista = res.data
    } else {
      console.error("Formato de categorías desconocido:", res.data)
    }
    
    categorias.value = lista
    console.log(`✅ Categorías cargadas: ${lista.length}`)

  } catch (err) {
    console.error('Error cargando categorías', err)
    Swal.fire('Error', 'No se pudieron cargar las categorías', 'error')
  }
}

onMounted(() => {
  cargarCategorias()
})

const registrarProveedor = async () => {
  if (hayErrores()) {
    Swal.fire({
      icon: 'warning',
      title: 'Atención',
      text: 'Revisa los campos marcados en rojo.',
      background: '#1e293b',
      color: '#f1f5f9'
    })
    return
  }

  cargando.value = true
  try {
    const payload = {
      nombre: proveedor.nombre.trim(),
      cuit: proveedor.cuit.trim(),
      contacto: proveedor.contacto.trim(),
      telefono: proveedor.telefono.trim(),
      email: proveedor.email.trim(),
      direccion: proveedor.direccion.trim(),
      categorias: proveedor.categorias_seleccionadas,
      productos_especificos: proveedor.productos_especificos.trim()
    }

    const response = await axios.post(`${API_BASE}/api/proveedores/`, payload)
    
    await Swal.fire({
      icon: 'success',
      title: '¡Registrado!',
      text: 'Proveedor guardado exitosamente',
      background: '#1e293b',
      color: '#f1f5f9',
      timer: 1500,
      showConfirmButton: false
    })

    emit('proveedor-registrado', response.data)
    
  } catch (err) {
    console.error(err)
    let msg = 'Error al registrar.'
    if (err.response?.data?.cuit) msg = 'Ese CUIT ya está registrado.'
    
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: msg,
      background: '#1e293b',
      color: '#f1f5f9'
    })
  } finally {
    cargando.value = false
  }
}

const volver = () => emit('cancelar')
</script>

<style scoped>
/* =============================
   ESTILOS MODERNOS Y LIMPIOS
============================= */
.form-card {
  background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid #334155;
  border-radius: 16px;
  padding: 30px 40px;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  /* Eliminamos overflow y height fijo aquí para que crezca */
}

.form-header { text-align: center; margin-bottom: 30px; }
.form-header h1 { font-size: 2rem; color: #f1f5f9; margin: 0; }
.form-header p { color: #94a3b8; font-size: 0.95rem; margin-top: 5px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.input-group { display: flex; flex-direction: column; }
.input-group.full-width { grid-column: 1 / -1; }

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

label { color: #cbd5e1; font-weight: 600; font-size: 0.9rem; }

.badge-required {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.badge-optional {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

input, .form-textarea {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 12px 16px;
  color: #f1f5f9;
  font-size: 15px;
  transition: all 0.3s ease;
}

input:focus, .form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(15, 23, 42, 0.9);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
}

input.error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.field-error {
  color: #ef4444;
  font-size: 0.8rem;
  margin-top: 6px;
  font-weight: 500;
  animation: fadeIn 0.3s ease;
}


.chips-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
  border: 1px solid #334155;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.3);
    /* max-height: 250px; */
  /* overflow-y: auto; */
    height: auto;
  min-height: 50px;
}

/* Scrollbar personalizado para el wrapper */
.chips-wrapper::-webkit-scrollbar {
  width: 6px;
}
.chips-wrapper::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 3px;
}

.chip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(51, 65, 85, 0.4);
  border: 1px solid #475569;
  padding: 8px 16px;
  border-radius: 20px;
  color: #cbd5e1;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.chip-item:hover {
  background: rgba(51, 65, 85, 0.8);
  transform: translateY(-1px);
}

.chip-item.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-color: #3b82f6;
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  font-weight: 500;
}

.check-icon {
  font-weight: 800;
  font-size: 0.8rem;
}

.no-data {
  color: #64748b;
  font-style: italic;
  font-size: 0.9rem;
  padding: 10px;
}

/* BOTONES */
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #334155;
}

.btn {
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
}
.btn-primary:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
  transform: translateY(-2px);
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  background: transparent;
  color: #94a3b8;
  border: 1px solid #475569;
}
.btn-secondary:hover {
  background: #1e293b;
  color: #f1f5f9;
  border-color: #cbd5e1;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .form-card { padding: 20px; }
}
</style>