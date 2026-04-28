<template>
  <div class="modern-form">
    <div class="form-header">
      <h1>Modificar Usuario</h1>
      <p class="subtitle">Edita los datos del usuario</p>
    </div>

    <form @submit.prevent="actualizarUsuario" class="form-content" autocomplete="off">
      
      <div class="form-row">
        <div class="input-field">
          <div class="field-header">
            <label>Nombre</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper">
            <input 
              v-model="form.nombre" 
              type="text" 
              placeholder="Ingresa el nombre" 
              @blur="validarNombre"
              :class="{ 'error': errores.nombre }"
            />
          </div>
          <div v-if="errores.nombre" class="field-error">
            <span class="error-dot"></span>
            {{ errores.nombre }}
          </div>
        </div>

        <div class="input-field">
          <div class="field-header">
            <label>Apellido</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper">
            <input 
              v-model="form.apellido" 
              type="text" 
              placeholder="Ingresa el apellido" 
              @blur="validarApellido"
              :class="{ 'error': errores.apellido }"
            />
          </div>
          <div v-if="errores.apellido" class="field-error">
            <span class="error-dot"></span>
            {{ errores.apellido }}
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="input-field">
          <div class="field-header">
            <label>DNI</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper">
            <input 
              v-model="form.dni" 
              type="text" 
              placeholder="30236987"
              @blur="validarDNI"
              @input="formatearDNI"
              maxlength="8"
              :class="{ 'error': errores.dni }"
            />
          </div>
          <div v-if="errores.dni" class="field-error">
            <span class="error-dot"></span>
            {{ errores.dni }}
          </div>
        </div>

        <div class="input-field">
          <div class="field-header">
            <label>Teléfono</label>
            <span class="optional-badge">Opcional</span>
          </div>
          <div class="input-wrapper">
            <input 
              v-model="form.telefono" 
              type="tel" 
              placeholder="+54 3755399999"
              @blur="validarTelefono"
              @input="formatearTelefono"
              :class="{ 'error': errores.telefono }"
            />
          </div>
          <div v-if="errores.telefono" class="field-error">
            <span class="error-dot"></span>
            {{ errores.telefono }}
          </div>
        </div>
      </div>

      <div class="input-field full-width">
        <div class="field-header">
          <label>Correo Electrónico</label>
          <span class="required-badge">Requerido</span>
        </div>
        <div class="input-wrapper">
          <input 
            v-model="form.correo" 
            type="email" 
            placeholder="ejemplo@dominio.com" 
            @blur="validarCorreo"
            @input="validarCorreo"
            :class="{ 'error': errores.correo }"
          />
        </div>
        <div v-if="errores.correo" class="field-error">
          <span class="error-dot"></span>
          {{ errores.correo }}
        </div>
      </div>

      <div v-if="mostrarCambioContrasena" class="password-section">
        <div class="input-field">
          <div class="field-header">
            <label>Contraseña Actual</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper password-wrapper">
            <input 
              v-model="form.contrasena_actual" 
              :type="mostrarContrasenaActual ? 'text' : 'password'" 
              placeholder="Ingresa tu contraseña actual"
              @blur="validarContrasenaActual"
              @input="validarContrasenaActual"
              :class="{ 'error': errores.contrasena_actual }"
              autocomplete="new-password"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarContrasenaActual = !mostrarContrasenaActual"
              aria-label="Mostrar contraseña"
            >
              <svg v-if="!mostrarContrasenaActual" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <div v-if="errores.contrasena_actual" class="field-error">
            <span class="error-dot"></span>
            {{ errores.contrasena_actual }}
          </div>
        </div>

        <div class="input-field">
          <div class="field-header">
            <label>Nueva Contraseña</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper password-wrapper">
            <input 
              v-model="form.contrasena_nueva" 
              :type="mostrarNuevaContrasena ? 'text' : 'password'" 
              placeholder="Mín 6 caracteres, 1 mayúscula, 1 número"
              @blur="validarNuevaContrasena"
              @input="validarNuevaContrasena"
              :class="{ 'error': errores.contrasena_nueva }"
              autocomplete="new-password"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarNuevaContrasena = !mostrarNuevaContrasena"
              aria-label="Mostrar contraseña"
            >
              <svg v-if="!mostrarNuevaContrasena" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <div v-if="mostrarCambioContrasena" class="password-requirements">
            <ul class="requirement-list">
              <li :class="passwordRequisitos.minLength ? 'valid' : 'invalid'">
                <svg v-if="passwordRequisitos.minLength" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Al menos 6 caracteres
              </li>
              <li :class="passwordRequisitos.hasUpper ? 'valid' : 'invalid'">
                <svg v-if="passwordRequisitos.hasUpper" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Al menos 1 mayúscula
              </li>
              <li :class="passwordRequisitos.hasNumber ? 'valid' : 'invalid'">
                <svg v-if="passwordRequisitos.hasNumber" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Al menos 1 número
              </li>
            </ul>
          </div>
          <div v-if="errores.contrasena_nueva" class="field-error">
            <span class="error-dot"></span>
            {{ errores.contrasena_nueva }}
          </div>
        </div>

        <div class="input-field">
          <div class="field-header">
            <label>Repetir Nueva Contraseña</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper password-wrapper">
            <input 
              v-model="form.repetir_contrasena" 
              :type="mostrarRepetirContrasena ? 'text' : 'password'" 
              placeholder="Repetí la nueva contraseña"
              @blur="validarRepetirContrasena"
              @input="validarRepetirContrasena"
              :class="{ 'error': errores.repetir_contrasena }"
              autocomplete="new-password"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarRepetirContrasena = !mostrarRepetirContrasena"
              aria-label="Mostrar contraseña"
            >
              <svg v-if="!mostrarRepetirContrasena" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <div v-if="errores.repetir_contrasena" class="field-error">
            <span class="error-dot"></span>
            {{ errores.repetir_contrasena }}
          </div>
        </div>
      </div>

      <div class="full-width">
        <button 
          type="button" 
          class="toggle-password-change"
          @click="mostrarCambioContrasena = !mostrarCambioContrasena"
        >
          {{ mostrarCambioContrasena ? 'Ocultar cambio de contraseña' : 'Cambiar contraseña' }}
        </button>
      </div>

      <div class="input-field full-width">
        <div class="field-header">
          <label>Rol del Usuario</label>
          <span class="required-badge">Requerido</span>
        </div>
        <div class="select-wrapper">
          <select 
            v-model="form.rol_id" 
            @change="validarRol"
            :class="{ 'error': errores.rol_id }"
          >
            <option value="" disabled>Selecciona un rol</option>
            <option 
              v-for="rol in roles" 
              :key="rol.id" 
              :value="rol.id"
            >
              {{ rol.nombre }}
            </option>
          </select>
          <svg class="select-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
        <div v-if="errores.rol_id" class="field-error">
          <span class="error-dot"></span>
          {{ errores.rol_id }}
        </div>
      </div>

      <div class="form-row">
        <button type="submit" class="submit-button" :disabled="botonDeshabilitado" :class="{ 'opacity-50 cursor-not-allowed': botonDeshabilitado }">
          <span class="button-content">
            <span class="button-text">{{ cargando ? 'Actualizando...' : 'Actualizar Usuario' }}</span>
            <svg v-if="cargando" class="spinner-svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4 31.4" stroke-linecap="round" class="spin-animation"/>
            </svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </span>
        </button>
        
        <button type="button" @click="cancelar" class="cancel-button">
          <span class="button-content">
            <span class="button-text">Cancelar</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const props = defineProps({
  usuarioId: { type: [String, Number], required: true }
})
const emit = defineEmits(['usuario-actualizado', 'cancelar'])

const cargando = ref(false)
const mostrarCambioContrasena = ref(false)
const mostrarContrasenaActual = ref(false)
const mostrarNuevaContrasena = ref(false)
const mostrarRepetirContrasena = ref(false)
const roles = ref([])
const usuariosExistentes = ref([])

const form = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena_actual: '',
  contrasena_nueva: '',
  repetir_contrasena: '',
  rol_id: '',
  estado: 'ACTIVO'
})

const errores = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena_actual: '',
  contrasena_nueva: '',
  repetir_contrasena: '',
  rol_id: ''
})

const passwordRequisitos = computed(() => {
  const pwd = form.value.contrasena_nueva || ''
  return {
    minLength: pwd.length >= 6,
    hasUpper: /[A-Z]/.test(pwd),
    hasNumber: /[0-9]/.test(pwd)
  }
})

const formularioValido = computed(() => {
  if (errores.value.nombre || errores.value.apellido || errores.value.dni ||
      errores.value.correo || errores.value.rol_id) return false
  if (errores.value.telefono) return false

  if (mostrarCambioContrasena.value) {
    if (!form.value.contrasena_actual) return false
    if (!passwordRequisitos.value.minLength || !passwordRequisitos.value.hasUpper || !passwordRequisitos.value.hasNumber) return false
    if (errores.value.contrasena_actual || errores.value.contrasena_nueva || errores.value.repetir_contrasena) return false
    if (!form.value.repetir_contrasena) return false
  }
  return true
})

const botonDeshabilitado = computed(() => {
  return cargando.value || !formularioValido.value
})

// -------------------------------------------------------
// Carga de datos
// -------------------------------------------------------
const cargarRoles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/roles/`)
    if (Array.isArray(res.data)) {
      roles.value = res.data.filter(r => r.activo !== false)
    } else if (res.data && Array.isArray(res.data.data)) {
      roles.value = res.data.data.filter(r => r.activo !== false)
    } else if (res.data && res.data.results) {
      roles.value = res.data.results.filter(r => r.activo !== false)
    }
  } catch (error) {
    console.error('Error cargando roles:', error)
    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudieron cargar los roles', background: '#1e293b', color: '#f1f5f9' })
  }
}

// 🔥 ARREGLO 1: Cargar toda la base forzando límite
const cargarUsuariosExistentes = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/usuarios/?limit=1000`)
    if (Array.isArray(res.data)) {
      usuariosExistentes.value = res.data
    } else if (res.data && Array.isArray(res.data.results)) {
      usuariosExistentes.value = res.data.results
    } else if (res.data && Array.isArray(res.data.data)) {
      usuariosExistentes.value = res.data.data
    } else {
      usuariosExistentes.value = []
    }
  } catch (error) {
    console.error('Error cargando usuarios existentes:', error)
    usuariosExistentes.value = []
  }
}

const formatearTelefonoParaMostrar = (telefono) => {
  if (!telefono) return ''
  const telLimpio = telefono.replace(/\s+/g, '').replace('+', '')
  if (telLimpio.startsWith('549') && telLimpio.length === 13) {
    const codigoArea = telLimpio.substring(3, 7)
    const numero = telLimpio.substring(7)
    return `+54 9 ${codigoArea} ${numero}`
  }
  return telefono
}

const cargarUsuario = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/usuarios/`)
    const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
    const usuario = data.find(u => u.id == props.usuarioId)
    
    if (!usuario) {
      Swal.fire({ icon: 'error', title: 'Error', text: 'Usuario no encontrado', background: '#1e293b', color: '#f1f5f9' })
      emit('cancelar')
      return
    }
    form.value = {
      nombre: usuario.nombre || '',
      apellido: usuario.apellido || '',
      dni: usuario.dni || '',
      telefono: formatearTelefonoParaMostrar(usuario.telefono || ''),
      correo: usuario.correo || '',
      contrasena_actual: '',
      contrasena_nueva: '',
      repetir_contrasena: '',
      rol_id: usuario.rol_id || '',
      estado: usuario.estado || 'ACTIVO'
    }
  } catch (error) {
    console.error('Error al cargar usuario:', error)
    Swal.fire({ icon: 'error', title: 'Error', text: 'Error al cargar los datos del usuario', background: '#1e293b', color: '#f1f5f9' })
  }
}

// -------------------------------------------------------
// Formateo y validaciones
// -------------------------------------------------------
const formatearDNI = () => { 
  form.value.dni = form.value.dni.replace(/\D/g, '').slice(0, 8) 
  validarDNI()
}

const formatearTelefono = () => {
  let tel = form.value.telefono.replace(/\D/g, '')
  if (tel.length === 0) { form.value.telefono = ''; return }
  if (tel.startsWith('549')) form.value.telefono = '+54 ' + tel.slice(2)
  else if (tel.startsWith('54')) form.value.telefono = '+54 ' + tel.slice(2)
  else if (tel.startsWith('9')) form.value.telefono = '+54 ' + tel
  else form.value.telefono = '+54 9' + tel
  tel = form.value.telefono.replace(/\D/g, '')
  if (tel.length > 13) {
    tel = tel.slice(0, 13)
    form.value.telefono = `+${tel.slice(0,2)} ${tel.slice(2)}`
  }
  validarTelefono()
}

// Alerta genérica tipo Toast
const alertaDuplicado = (titulo, texto) => {
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'warning',
    title: titulo,
    text: texto,
    showConfirmButton: false,
    timer: 4000,
    timerProgressBar: true,
    background: '#1e293b',
    color: '#f1f5f9'
  })
}

// 🔥 ARREGLO 2: Validación exluyendo el ID propio (DNI y Correo)
const validarDNI = () => {
  const val = form.value.dni.trim()
  if (!val) {
    errores.value.dni = 'El DNI es obligatorio'
    return
  }
  if (!/^\d{7,8}$/.test(val)) {
    errores.value.dni = 'DNI inválido (7-8 dígitos)'
    return
  }
  
  if (usuariosExistentes.value && usuariosExistentes.value.length > 0) {
    const existe = usuariosExistentes.value.some(u => String(u.id) !== String(props.usuarioId) && String(u.dni) === String(val))
    if (existe) {
      errores.value.dni = 'Ya existe un usuario con este DNI'
      alertaDuplicado('DNI ya registrado', 'El DNI que ingresaste ya pertenece a otro usuario.')
      return
    }
  }
  errores.value.dni = ''
}

const validarCorreo = () => {
  const val = form.value.correo.trim().toLowerCase()
  if (!val) {
    errores.value.correo = 'El correo es obligatorio'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
    errores.value.correo = 'Correo electrónico inválido'
    return
  }

  if (usuariosExistentes.value && usuariosExistentes.value.length > 0) {
    const existe = usuariosExistentes.value.some(u => String(u.id) !== String(props.usuarioId) && u.correo?.toLowerCase() === val)
    if (existe) {
      errores.value.correo = 'Ya existe un usuario con este correo'
      alertaDuplicado('Correo ya registrado', 'Este correo ya está en uso. Por favor, usa otro.')
      return
    }
  }
  errores.value.correo = ''
}

const validarNombre = () => {
  const val = form.value.nombre.trim()
  if (!val) errores.value.nombre = 'El nombre es obligatorio'
  else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val)) errores.value.nombre = 'Solo letras (2-50 caracteres)'
  else errores.value.nombre = ''
}
const validarApellido = () => {
  const val = form.value.apellido.trim()
  if (!val) errores.value.apellido = 'El apellido es obligatorio'
  else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val)) errores.value.apellido = 'Solo letras (2-50 caracteres)'
  else errores.value.apellido = ''
}

const validarTelefono = () => {
  const val = form.value.telefono.trim()
  if (!val) { errores.value.telefono = ''; return }
  const limpio = val.replace(/\s+/g, '')
  if (!/^\+54\s?9\d{10}$/.test(limpio)) errores.value.telefono = 'Formato: +54 9 3755 558911'
  else errores.value.telefono = ''
}

const validarContrasenaActual = () => {
  if (!mostrarCambioContrasena.value) return
  errores.value.contrasena_actual = form.value.contrasena_actual ? '' : 'La contraseña actual es obligatoria'
}
const validarNuevaContrasena = () => {
  if (!mostrarCambioContrasena.value) return
  const val = form.value.contrasena_nueva
  if (!val) { errores.value.contrasena_nueva = ''; return }
  if (val.length < 6) errores.value.contrasena_nueva = 'Mínimo 6 caracteres'
  else if (!passwordRequisitos.value.hasUpper && !passwordRequisitos.value.hasNumber) errores.value.contrasena_nueva = 'Falta 1 mayúscula y 1 número'
  else if (!passwordRequisitos.value.hasUpper) errores.value.contrasena_nueva = 'Falta 1 mayúscula'
  else if (!passwordRequisitos.value.hasNumber) errores.value.contrasena_nueva = 'Falta 1 número'
  else errores.value.contrasena_nueva = ''
}
const validarRepetirContrasena = () => {
  if (!mostrarCambioContrasena.value) return
  const original = form.value.contrasena_nueva
  const repetir = form.value.repetir_contrasena
  if (!repetir) errores.value.repetir_contrasena = 'Debe repetir la nueva contraseña'
  else if (repetir !== original) errores.value.repetir_contrasena = 'Las contraseñas no coinciden'
  else errores.value.repetir_contrasena = ''
}
const validarRol = () => {
  errores.value.rol_id = form.value.rol_id ? '' : 'Selecciona un rol'
}

const validarFormulario = () => {
  validarNombre(); validarApellido(); validarDNI(); validarTelefono(); validarCorreo(); validarRol()
  if (mostrarCambioContrasena.value) {
    validarContrasenaActual(); validarNuevaContrasena(); validarRepetirContrasena()
  }
  return formularioValido.value
}

// -------------------------------------------------------
// Envío del formulario
// -------------------------------------------------------
const actualizarUsuario = async () => {
  if (!validarFormulario()) {
    Swal.fire({ icon: 'error', title: 'Formulario incompleto', text: 'Completá los campos requeridos correctamente', background: '#1e293b', color: '#f1f5f9' })
    return
  }

  try {
    const rolNombreSeleccionado = roles.value.find(r => r.id == form.value.rol_id)?.nombre?.toLowerCase()
    const hayOtroAdmin = usuariosExistentes.value.some(u => u.rol_nombre?.toLowerCase() === 'administrador' && u.id != props.usuarioId && u.estado === 'ACTIVO')
    if (rolNombreSeleccionado === 'administrador' && hayOtroAdmin) {
      Swal.fire({ icon: 'warning', title: 'Administrador existente', text: 'Ya existe un administrador activo.', background: '#1e293b', color: '#f1f5f9' })
      return
    }
  } catch (error) { console.error(error) }

  cargando.value = true
  try {
    let telefonoParaBackend = null
    if (form.value.telefono.trim()) {
      let telLimpio = form.value.telefono.replace(/\s+/g, '').replace('+', '')
      if (!telLimpio.startsWith('549')) {
        if (telLimpio.startsWith('54')) telLimpio = '549' + telLimpio.slice(2)
        else if (telLimpio.startsWith('9')) telLimpio = '54' + telLimpio
        else telLimpio = '549' + telLimpio
      }
      if (telLimpio.length === 13) telefonoParaBackend = '+' + telLimpio
      else throw new Error('Teléfono inválido')
    }

    const payload = {
      nombre: form.value.nombre.trim(),
      apellido: form.value.apellido.trim(),
      dni: form.value.dni.trim(),
      telefono: telefonoParaBackend,
      correo: form.value.correo.trim(),
      rol: form.value.rol_id,
      estado: form.value.estado
    }

    if (mostrarCambioContrasena.value && form.value.contrasena_nueva) {
      payload.contrasena_actual = form.value.contrasena_actual
      payload.contrasena_nueva = form.value.contrasena_nueva
    }

    const response = await axios.post(`${API_BASE}/api/usuarios/editar/${props.usuarioId}/`, payload)
    Swal.fire({ icon: 'success', title: 'Usuario actualizado', text: 'El usuario se ha actualizado exitosamente', background: '#1e293b', color: '#f1f5f9' })
    emit('usuario-actualizado', response.data)
  } catch (error) {
    console.error('Error:', error)
    
    // 🔥 ARREGLO 3: Red de seguridad para el 400
    if (error.response && error.response.status === 400) {
      const datosError = error.response.data
      let mostroAlerta = false
      
      if (datosError.dni) {
        errores.value.dni = 'Este DNI ya pertenece a otro usuario registrado.'
        mostroAlerta = true
      }
      if (datosError.correo) {
        errores.value.correo = 'Este correo electrónico ya está en uso. Elige otro.'
        mostroAlerta = true
      }

      if (mostroAlerta) {
        Swal.fire({
          icon: 'error',
          title: 'Datos duplicados',
          text: 'El DNI o Correo ingresado ya se encuentran registrados en otro usuario.',
          background: '#1e293b',
          color: '#f1f5f9'
        })
        cargando.value = false
        return
      }
    }

    let msg = 'Error al actualizar el usuario'
    if (error.response?.status === 401) msg = 'No estás autenticado. Por favor, inicia sesión nuevamente.'
    else if (error.response?.status === 403) msg = 'No tienes permisos para realizar esta acción.'
    else if (error.response?.data?.detail) msg = error.response.data.detail
    else if (error.response?.data?.message) msg = error.response.data.message
    else if (error.response?.data?.error) msg = error.response.data.error
    else if (typeof error.response?.data === 'object') {
      const erroresBackend = Object.values(error.response.data).flat().join(', ')
      if (erroresBackend) msg = erroresBackend
    } else if (error.message === 'Teléfono inválido') msg = 'El teléfono debe tener el formato correcto: +54 9 3755 558911'
    Swal.fire({ icon: 'error', title: 'Error', text: msg, background: '#1e293b', color: '#f1f5f9' })
  } finally { cargando.value = false }
}

const cancelar = () => emit('cancelar')

onMounted(async () => {
  await cargarUsuariosExistentes()
  await cargarRoles()
  await cargarUsuario()
})
</script>

<style scoped>
/* =============================================
   ESTILOS BASE (heredados de tu diseño)
   ============================================= */
.modern-form {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px;
  background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
  border-radius: 24px;
  border: 1px solid #334155;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
}
.form-header { text-align: center; margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); }
.form-header h1 { margin: 0 0 8px 0; font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #f1f5f9 0%, #0ea5e9 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; }
.subtitle { color: #94a3b8; font-size: 16px; margin: 0; }
.form-content { display: flex; flex-direction: column; gap: 24px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.input-field { position: relative; }
.field-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.field-header label { color: #cbd5e1; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
.required-badge { background: rgba(239,68,68,0.15); color: #ef4444; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.optional-badge { background: rgba(148,163,184,0.15); color: #94a3b8; padding: 4px 10px; border-radius: 20px; font-size: 11px; }

.input-wrapper { position: relative; width: 100%; }
.input-wrapper input, .select-wrapper select {
  width: 100%; padding: 16px 52px 16px 20px; background: rgba(15,23,42,0.7); border: 2px solid #334155; border-radius: 14px; color: #f1f5f9; font-size: 15px; font-weight: 500; transition: all 0.3s; backdrop-filter: blur(10px); box-sizing: border-box;
}
.input-wrapper input:focus, .select-wrapper select:focus {
  outline: none; border-color: #0ea5e9; background: rgba(15,23,42,0.9); box-shadow: 0 0 0 4px rgba(14,165,233,0.2), 0 4px 20px rgba(14,165,233,0.15);
}
.input-wrapper input.error, .select-wrapper select.error { border-color: #ef4444; background: rgba(239,68,68,0.07); }

/* Autofill fix Dark Mode */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px rgba(15,23,42,0.9) inset !important;
  -webkit-text-fill-color: #f1f5f9 !important;
  transition: background-color 5000s ease-in-out 0s;
}
/* Ocultar iconos nativos */
input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear { display: none; }
input[type="password"]::-webkit-credentials-auto-fill-button { visibility: hidden; }

.password-toggle {
  position: absolute; right: 16px; top: 50%; transform: translateY(-50%); background: transparent; border: none; color: #64748b; cursor: pointer; padding: 4px; border-radius: 8px; transition: color 0.2s; z-index: 2;
}
.password-toggle:hover { color: #0ea5e9; }

/* Sección de contraseñas */
.password-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 8px;
  margin-bottom: 8px;
}

/* Requisitos de contraseña */
.password-requirements { margin-top: 10px; background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.05); }
.requirement-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 6px; }
.requirement-list li { font-size: 13px; display: flex; align-items: center; gap: 8px; }
.requirement-list li.valid { color: #34d399; }
.requirement-list li.invalid { color: #f87171; }
.requirement-list li svg { flex-shrink: 0; }

.select-wrapper { position: relative; }
.select-wrapper select { appearance: none; cursor: pointer; padding-right: 52px; }
.select-arrow { position: absolute; right: 20px; top: 50%; transform: translateY(-50%); color: #64748b; pointer-events: none; }

.field-error { display: flex; align-items: center; gap: 8px; margin-top: 8px; color: #ef4444; font-size: 13px; font-weight: 500; animation: slideIn 0.3s ease; }
.error-dot { width: 6px; height: 6px; background: #ef4444; border-radius: 50%; }

@keyframes slideIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

.toggle-password-change { width: 100%; padding: 12px 24px; background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; margin-bottom: 16px; transition: all 0.3s; }
.toggle-password-change:hover { background: rgba(148,163,184,0.2); color: #cbd5e1; border-color: rgba(148,163,184,0.5); }

.submit-button, .cancel-button { width: 100%; padding: 18px 32px; border-radius: 14px; font-size: 16px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 12px; cursor: pointer; transition: all 0.3s; border: none; }
.submit-button { background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; }
.submit-button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(14,165,233,0.4), 0 4px 15px rgba(14,165,233,0.3); }
.submit-button:disabled { opacity: 0.5; cursor: not-allowed; }
.cancel-button { background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.cancel-button:hover { background: rgba(239,68,68,0.2); border-color: rgba(239,68,68,0.5); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(239,68,68,0.2); }

.spin-animation { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.full-width { grid-column: 1 / -1; }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; gap: 20px; }
  .form-header h1 { font-size: 28px; }
  .modern-form { padding: 24px; }
}
</style>