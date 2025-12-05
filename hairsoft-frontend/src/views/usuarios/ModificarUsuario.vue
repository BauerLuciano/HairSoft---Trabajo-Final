<template>
  <div class="modern-form">
    <div class="form-header">
      <h1>Modificar Usuario</h1>
      <p class="subtitle">Edita los datos del usuario</p>
    </div>

    <form @submit.prevent="actualizarUsuario" class="form-content" autocomplete="off">
      
      <!-- Primera fila -->
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

      <!-- Segunda fila -->
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

      <!-- Correo -->
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
            :class="{ 'error': errores.correo }"
          />
        </div>
        <div v-if="errores.correo" class="field-error">
          <span class="error-dot"></span>
          {{ errores.correo }}
        </div>
      </div>

      <!-- Campos de contraseña (solo si se quiere cambiar) -->
      <div v-if="mostrarCambioContrasena" class="form-row">
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
              :class="{ 'error': errores.contrasena_actual }"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarContrasenaActual = !mostrarContrasenaActual"
            >
              {{ mostrarContrasenaActual ? '👁️' : '👁️‍🗨️' }}
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
              v-model="form.nueva_contrasena" 
              :type="mostrarNuevaContrasena ? 'text' : 'password'" 
              placeholder="Mínimo 6 caracteres"
              @blur="validarNuevaContrasena"
              :class="{ 'error': errores.nueva_contrasena }"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarNuevaContrasena = !mostrarNuevaContrasena"
            >
              {{ mostrarNuevaContrasena ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="errores.nueva_contrasena" class="field-error">
            <span class="error-dot"></span>
            {{ errores.nueva_contrasena }}
          </div>
        </div>
      </div>

      <!-- Botón para mostrar/ocultar cambio de contraseña -->
      <div class="full-width">
        <button 
          type="button" 
          class="toggle-password-change"
          @click="mostrarCambioContrasena = !mostrarCambioContrasena"
        >
          {{ mostrarCambioContrasena ? 'Ocultar cambio de contraseña' : 'Cambiar contraseña' }}
        </button>
      </div>

      <!-- Rol -->
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
          <div class="select-arrow">▼</div>
        </div>
        <div v-if="errores.rol_id" class="field-error">
          <span class="error-dot"></span>
          {{ errores.rol_id }}
        </div>
      </div>

      <!-- Botones -->
      <div class="form-row">
        <button type="submit" class="submit-button" :disabled="cargando">
          <span class="button-content">
            <span class="button-text">{{ cargando ? 'Actualizando...' : 'Actualizar Usuario' }}</span>
            <span class="button-icon">{{ cargando ? '⏳' : '✓' }}</span>
          </span>
        </button>
        
        <button type="button" @click="cancelar" class="cancel-button">
          <span class="button-content">
            <span class="button-text">Cancelar</span>
            <span class="button-icon">×</span>
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Props y emits
const props = defineProps({
  usuarioId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['usuario-actualizado', 'cancelar'])

// Estado
const cargando = ref(false)
const mostrarCambioContrasena = ref(false)
const mostrarContrasenaActual = ref(false)
const mostrarNuevaContrasena = ref(false)
const roles = ref([])
const usuariosExistentes = ref([])

// Formulario
const form = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena_actual: '',
  nueva_contrasena: '',
  rol_id: '',
  estado: 'ACTIVO'
})

// Errores
const errores = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena_actual: '',
  nueva_contrasena: '',
  rol_id: ''
})

// Cargar roles
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
    if (error.response?.status === 401) {
      Swal.fire({
        icon: 'error',
        title: 'Sesión expirada',
        text: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
        background: '#1e293b',
        color: '#f1f5f9'
      })
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron cargar los roles',
        background: '#1e293b',
        color: '#f1f5f9'
      })
    }
  }
}

// Cargar usuarios existentes para validar duplicados
const cargarUsuariosExistentes = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/usuarios/`)
    usuariosExistentes.value = res.data
  } catch (error) {
    console.error('Error cargando usuarios existentes:', error)
  }
}

// Formatear teléfono almacenado en el backend
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

// Cargar datos del usuario
const cargarUsuario = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/usuarios/`)
    const usuario = res.data.find(u => u.id == props.usuarioId)

    if (!usuario) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Usuario no encontrado',
        background: '#1e293b',
        color: '#f1f5f9'
      })
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
      nueva_contrasena: '',
      rol_id: usuario.rol_id || '',
      estado: usuario.estado || 'ACTIVO'
    }
  } catch (error) {
    console.error('Error al cargar usuario:', error)
    if (error.response?.status === 401) {
      Swal.fire({
        icon: 'error',
        title: 'Sesión expirada',
        text: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
        background: '#1e293b',
        color: '#f1f5f9'
      })
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar los datos del usuario',
        background: '#1e293b',
        color: '#f1f5f9'
      })
    }
  }
}

// Formateo y validaciones
const formatearDNI = () => {
  form.value.dni = form.value.dni.replace(/\D/g, '').slice(0, 8)
}

const formatearTelefono = () => {
  let tel = form.value.telefono.replace(/\D/g, '')
  
  if (tel.length === 0) {
    form.value.telefono = ''
    return
  }
  
  if (tel.startsWith('549')) {
    form.value.telefono = '+54 ' + tel.slice(2)
  } else if (tel.startsWith('54')) {
    form.value.telefono = '+54 ' + tel.slice(2)
  } else if (tel.startsWith('9')) {
    form.value.telefono = '+54 ' + tel
  } else {
    form.value.telefono = '+54 9' + tel
  }
  
  tel = form.value.telefono.replace(/\D/g, '')
  if (tel.length > 13) {
    tel = tel.slice(0, 13)
    const codigoPais = tel.slice(0, 2)
    const resto = tel.slice(2)
    form.value.telefono = `+${codigoPais} ${resto}`
  }
}

// Validar que no exista otro usuario con el mismo nombre y apellido
const validarNombreApellidoUnico = () => {
  const nombre = form.value.nombre.trim().toLowerCase()
  const apellido = form.value.apellido.trim().toLowerCase()
  
  if (!nombre || !apellido) return true
  
  const existeDuplicado = usuariosExistentes.value.some(usuario => {
    if (usuario.id == props.usuarioId) return false
    
    const usuarioNombre = usuario.nombre?.toLowerCase() || ''
    const usuarioApellido = usuario.apellido?.toLowerCase() || ''
    
    return usuarioNombre === nombre && usuarioApellido === apellido
  })
  
  return !existeDuplicado
}

// Validar que no exista otro usuario con el mismo DNI
const validarDNIUnico = () => {
  const dni = form.value.dni.trim()
  
  if (!dni) return true
  
  const existeDuplicado = usuariosExistentes.value.some(usuario => {
    if (usuario.id == props.usuarioId) return false
    return usuario.dni === dni
  })
  
  return !existeDuplicado
}

// Validar que no exista otro usuario con el mismo correo
const validarCorreoUnico = () => {
  const correo = form.value.correo.trim().toLowerCase()
  
  if (!correo) return true
  
  const existeDuplicado = usuariosExistentes.value.some(usuario => {
    if (usuario.id == props.usuarioId) return false
    const usuarioCorreo = usuario.correo?.toLowerCase() || ''
    return usuarioCorreo === correo
  })
  
  return !existeDuplicado
}

const validarNombre = () => {
  const val = form.value.nombre.trim()
  if (!val) {
    errores.value.nombre = 'El nombre es obligatorio'
  } else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val)) {
    errores.value.nombre = 'Solo letras (2-50 caracteres)'
  } else if (!validarNombreApellidoUnico()) {
    errores.value.nombre = 'Ya existe un usuario con este nombre y apellido'
  } else {
    errores.value.nombre = ''
  }
}

const validarApellido = () => {
  const val = form.value.apellido.trim()
  if (!val) {
    errores.value.apellido = 'El apellido es obligatorio'
  } else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val)) {
    errores.value.apellido = 'Solo letras (2-50 caracteres)'
  } else if (!validarNombreApellidoUnico()) {
    errores.value.apellido = 'Ya existe un usuario con este nombre y apellido'
  } else {
    errores.value.apellido = ''
  }
}

const validarDNI = () => {
  const val = form.value.dni.trim()
  if (!val) {
    errores.value.dni = 'El DNI es obligatorio'
  } else if (!/^\d{7,8}$/.test(val)) {
    errores.value.dni = 'DNI inválido (7-8 dígitos)'
  } else if (!validarDNIUnico()) {
    errores.value.dni = 'Ya existe un usuario con este DNI'
  } else {
    errores.value.dni = ''
  }
}

const validarTelefono = () => {
  const val = form.value.telefono.trim()
  if (!val) {
    errores.value.telefono = ''
    return
  }

  const limpio = val.replace(/\s+/g, '')
  
  if (!/^\+54\s?9\d{10}$/.test(limpio)) {
    errores.value.telefono = 'Formato: +54 9 3755 558911'
  } else {
    errores.value.telefono = ''
  }
}

const validarCorreo = () => {
  const val = form.value.correo.trim()
  if (!val) {
    errores.value.correo = 'El correo es obligatorio'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
    errores.value.correo = 'Correo electrónico inválido'
  } else if (!validarCorreoUnico()) {
    errores.value.correo = 'Ya existe un usuario con este correo'
  } else {
    errores.value.correo = ''
  }
}

const validarContrasenaActual = () => {
  if (!mostrarCambioContrasena.value) return
  
  const val = form.value.contrasena_actual
  if (!val) {
    errores.value.contrasena_actual = 'La contraseña actual es obligatoria para cambiar la contraseña'
  } else {
    errores.value.contrasena_actual = ''
  }
}

const validarNuevaContrasena = () => {
  if (!mostrarCambioContrasena.value) return
  
  const val = form.value.nueva_contrasena
  if (val && val.length < 6) {
    errores.value.nueva_contrasena = 'Mínimo 6 caracteres'
  } else if (val && !/(?=.*[A-Z])(?=.*\d)/.test(val)) {
    errores.value.nueva_contrasena = '1 mayúscula y 1 número'
  } else {
    errores.value.nueva_contrasena = ''
  }
}

const validarRol = () => {
  if (!form.value.rol_id) {
    errores.value.rol_id = 'Selecciona un rol'
  } else {
    errores.value.rol_id = ''
  }
}

const validarFormulario = () => {
  validarNombre()
  validarApellido()
  validarDNI()
  validarTelefono()
  validarCorreo()
  validarRol()
  
  if (mostrarCambioContrasena.value) {
    validarContrasenaActual()
    validarNuevaContrasena()
  }

  return !Object.values(errores.value).some(e => e !== '')
}

// Actualizar usuario
const actualizarUsuario = async () => {
  if (!validarFormulario()) {
    Swal.fire({
      icon: 'error',
      title: 'Formulario incompleto',
      text: 'Por favor, completa todos los campos requeridos correctamente',
      background: '#1e293b',
      color: '#f1f5f9'
    })
    return
  }

  // Validar administrador único
  try {
    const rolNombreSeleccionado = roles.value.find(r => r.id == form.value.rol_id)?.nombre?.toLowerCase()
    
    const usuariosRes = await axios.get(`${API_BASE}/api/usuarios/`)
    
    const hayOtroAdmin = usuariosRes.data.some(u => 
      u.rol_nombre?.toLowerCase() === 'administrador' && 
      u.id != props.usuarioId && 
      u.estado === 'ACTIVO'
    )

    if (rolNombreSeleccionado === 'administrador' && hayOtroAdmin) {
      Swal.fire({
        icon: 'warning',
        title: 'Administrador existente',
        text: 'Ya existe un administrador activo. No se puede asignar este rol.',
        background: '#1e293b',
        color: '#f1f5f9'
      })
      return
    }
  } catch (error) {
    console.error('Error validando administrador:', error)
  }

  cargando.value = true

  try {
    // Preparar teléfono para backend
    let telefonoParaBackend = null
    if (form.value.telefono.trim()) {
      let telLimpio = form.value.telefono.replace(/\s+/g, '').replace('+', '')
      
      if (!telLimpio.startsWith('549')) {
        if (telLimpio.startsWith('54')) {
          telLimpio = '549' + telLimpio.slice(2)
        } else if (telLimpio.startsWith('9')) {
          telLimpio = '54' + telLimpio
        } else {
          telLimpio = '549' + telLimpio
        }
      }
      
      if (telLimpio.length === 13) {
        telefonoParaBackend = '+' + telLimpio
      } else {
        errores.value.telefono = 'El teléfono debe tener 13 dígitos'
        throw new Error('Teléfono inválido')
      }
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

    // Solo incluir campos de contraseña si se está cambiando
    if (mostrarCambioContrasena.value && form.value.nueva_contrasena) {
      payload.contrasena_actual = form.value.contrasena_actual
      payload.nueva_contrasena = form.value.nueva_contrasena
    }

    console.log('Enviando actualización:', payload)

    const response = await axios.post(
      `${API_BASE}/api/usuarios/editar/${props.usuarioId}/`, 
      payload
    )

    Swal.fire({
      icon: 'success',
      title: 'Usuario actualizado',
      text: 'El usuario se ha actualizado exitosamente',
      background: '#1e293b',
      color: '#f1f5f9'
    })
    
    emit('usuario-actualizado', response.data)

  } catch (error) {
    console.error('Error:', error)
    let msg = 'Error al actualizar el usuario'
    
    if (error.response?.status === 401) {
      msg = 'No estás autenticado. Por favor, inicia sesión nuevamente.'
    } else if (error.response?.status === 403) {
      msg = 'No tienes permisos para realizar esta acción.'
    } else if (error.response?.data?.detail) {
      msg = error.response.data.detail
    } else if (error.response?.data?.message) {
      msg = error.response.data.message
    } else if (error.response?.data?.error) {
      msg = error.response.data.error
    } else if (typeof error.response?.data === 'object') {
      const erroresBackend = Object.values(error.response.data).flat().join(', ')
      if (erroresBackend) {
        msg = erroresBackend
      }
    } else if (error.message === 'Teléfono inválido') {
      msg = 'El teléfono debe tener el formato correcto: +54 9 3755 558911'
    }
    
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

const cancelar = () => {
  emit('cancelar')
}

onMounted(async () => {
  await cargarUsuariosExistentes()
  await cargarRoles()
  await cargarUsuario()
})
</script>

<style scoped>
/* MANTENEMOS LOS MISMOS ESTILOS QUE REGISTRAR USUARIO Y AÑADIMOS LO ESPECÍFICO */

/* Botón para cambiar contraseña */
.toggle-password-change {
  width: 100%;
  padding: 12px 24px;
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.toggle-password-change:hover {
  background: rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.5);
}

/* Botón cancelar */
.cancel-button {
  width: 100%;
  padding: 18px 32px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.cancel-button:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.2);
}

.cancel-button:active {
  transform: translateY(0);
}

/* Ajustes para los botones en fila */
.form-row:last-child {
  gap: 16px;
}

/* El resto de estilos son los mismos que registrar usuario */
.modern-form {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px;
  background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
  border-radius: 24px;
  border: 1px solid #334155;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.form-header h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #f1f5f9 0%, #0ea5e9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.subtitle {
  color: #94a3b8;
  font-size: 16px;
  margin: 0;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.input-field {
  position: relative;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.field-header label {
  color: #cbd5e1;
  font-weight: 600;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.required-badge {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.optional-badge {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.input-wrapper input,
.select-wrapper select {
  width: 100%;
  padding: 16px 52px 16px 20px;
  background: rgba(15, 23, 42, 0.7);
  border: 2px solid #334155;
  border-radius: 14px;
  color: #f1f5f9;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  box-sizing: border-box;
}

.input-wrapper input:focus,
.select-wrapper select:focus {
  outline: none;
  border-color: #0ea5e9;
  background: rgba(15, 23, 42, 0.9);
  box-shadow: 
    0 0 0 4px rgba(14, 165, 233, 0.2),
    0 4px 20px rgba(14, 165, 233, 0.15);
  transform: translateY(-1px);
}

.input-wrapper input.error,
.select-wrapper select.error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.07);
}

.password-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.2s;
  z-index: 2;
}

.password-toggle:hover {
  color: #0ea5e9;
  background: rgba(255, 255, 255, 0.05);
}

.select-wrapper {
  position: relative;
}

.select-wrapper select {
  appearance: none;
  cursor: pointer;
  padding-right: 52px;
}

.select-arrow {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 12px;
  pointer-events: none;
}

.field-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  color: #ef4444;
  font-size: 13px;
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

.error-dot {
  width: 6px;
  height: 6px;
  background: #ef4444;
  border-radius: 50%;
  flex-shrink: 0;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.submit-button {
  width: 100%;
  padding: 18px 32px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 
    0 12px 40px rgba(14, 165, 233, 0.4),
    0 4px 15px rgba(14, 165, 233, 0.3);
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.button-icon {
  font-size: 18px;
  transition: transform 0.3s;
}

.submit-button:hover:not(:disabled) .button-icon {
  transform: scale(1.1);
}

.full-width {
  grid-column: 1 / -1;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .form-header h1 {
    font-size: 28px;
  }
  
  .modern-form {
    padding: 24px;
  }
}
</style>