<template>
  <div class="modern-form">
    <div v-if="vieneDeTurnos" class="turno-notice">
      <div class="notice-icon">📋</div>
      <div class="notice-content">
        <h3>Registro para Turno Presencial</h3>
        <p>Completa los datos del cliente para continuar con la reserva del turno</p>
      </div>
    </div>

    <div class="form-header">
      <h1>{{ vieneDeTurnos ? 'Registrar Nuevo Cliente' : 'Registrar Nuevo Usuario' }}</h1>
      <p class="subtitle">{{ vieneDeTurnos ? 'Completa los datos del cliente para el turno' : 'Completa todos los campos requeridos' }}</p>
    </div>

    <form @submit.prevent="crearUsuario" class="form-content" autocomplete="off">
      
      <div style="opacity: 0; position: absolute; z-index: -1; height: 0; overflow: hidden;">
        <input type="email" name="fake_email_catcher" id="fake_email_catcher" autocomplete="username">
        <input type="password" name="fake_password_catcher" id="fake_password_catcher" autocomplete="current-password">
      </div>

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
            <span class="required-badge">Requerido</span>
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
            autocomplete="off"
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

      <div class="form-row">
        <div class="input-field">
          <div class="field-header">
            <label>Contraseña</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper password-wrapper">
            <input 
              v-model="form.contrasena" 
              :type="mostrarContrasena ? 'text' : 'password'" 
              placeholder="Mínimo 6 caracteres"
              autocomplete="new-password"
              @blur="validarContrasena"
              :class="{ 'error': errores.contrasena }"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarContrasena = !mostrarContrasena"
              :aria-label="mostrarContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            >
              {{ mostrarContrasena ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="errores.contrasena" class="field-error">
            <span class="error-dot"></span>
            {{ errores.contrasena }}
          </div>
        </div>

        <div class="input-field">
          <div class="field-header">
            <label>Confirmar Contraseña</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper password-wrapper">
            <input 
              v-model="form.confirmarContrasena" 
              :type="mostrarConfirmarContrasena ? 'text' : 'password'" 
              placeholder="Repite la contraseña" 
              autocomplete="new-password"
              @blur="validarConfirmarContrasena"
              :class="{ 'error': errores.confirmarContrasena }"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarConfirmarContrasena = !mostrarConfirmarContrasena"
              :aria-label="mostrarConfirmarContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            >
              {{ mostrarConfirmarContrasena ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="errores.confirmarContrasena" class="field-error">
            <span class="error-dot"></span>
            {{ errores.confirmarContrasena }}
          </div>
        </div>
      </div>

      <div v-if="!vieneDeTurnos" class="input-field full-width">
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
            <option value="" disabled selected>Selecciona un rol</option>
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

      <button type="submit" class="submit-button" :disabled="botonDeshabilitado" :class="{ 'opacity-50 cursor-not-allowed': botonDeshabilitado }">
        <span class="button-content">
          <span class="button-text">{{ 
            cargando 
              ? (vieneDeTurnos ? 'Registrando cliente...' : 'Creando usuario...') 
              : (vieneDeTurnos ? 'Registrar Cliente y Volver a Turnos' : 'Crear Usuario')
          }}</span>
          <span class="button-icon">{{ cargando ? '⏳' : (vieneDeTurnos ? '📋' : '→') }}</span>
        </span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Estado
const cargando = ref(false)
const mostrarContrasena = ref(false)
const mostrarConfirmarContrasena = ref(false)
const roles = ref([])
const usuariosExistentes = ref([])
const vieneDeTurnos = ref(false)
const idRolCliente = ref(null)

// Formulario
const form = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena: '',
  confirmarContrasena: '',
  rol_id: ''
})

// Errores
const errores = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena: '',
  confirmarContrasena: '',
  rol_id: ''
})

onMounted(async () => {
  vieneDeTurnos.value = route.query.returnTo === 'turnos'
  console.log("📌 Contexto:", vieneDeTurnos.value ? 'Desde Turnos Presenciales' : 'Registro Normal')
  
  // Cargamos roles y la lista de usuarios para la validación en tiempo real
  await cargarRoles()
  await cargarUsuariosExistentes()
  
  if (vieneDeTurnos.value && !idRolCliente.value) {
    const rolCliente = roles.value.find(r => r.nombre.toLowerCase().includes('cliente'))
    if (rolCliente) {
      idRolCliente.value = rolCliente.id
      form.value.rol_id = idRolCliente.value
    }
  }  
})

// Cargar Roles
const cargarRoles = async () => {
  try {
    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
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
  }
}

// 🔥 ARREGLO CLAVE 1: Extraer bien el array bancando paginación de Django y forzando límite alto
const cargarUsuariosExistentes = async () => {
  try {
    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    // Le metemos un limite alto para que traiga todos a la vista de una vez
    const res = await axios.get(`${API_BASE}/api/usuarios/?limit=1000`)
    
    if (Array.isArray(res.data)) {
      usuariosExistentes.value = res.data
    } else if (res.data && Array.isArray(res.data.results)) {
      usuariosExistentes.value = res.data.results
    } else if (res.data && Array.isArray(res.data.data)) {
      usuariosExistentes.value = res.data.data
    } else {
      usuariosExistentes.value = [] // Fallback seguro
    }
    console.log(`✅ Usuarios cargados para validación: ${usuariosExistentes.value.length}`)
  } catch (error) {
    console.error('Error cargando usuarios existentes:', error)
    usuariosExistentes.value = []
  }
}

// ==========================================
// FORMATEOS EN TIEMPO REAL
// ==========================================
const formatearDNI = () => {
  form.value.dni = form.value.dni.replace(/\D/g, '').slice(0, 8)
  validarDNI() // Validamos mientras tipea
}

const formatearTelefono = () => {
  let tel = form.value.telefono.replace(/\D/g, '')
  if (!tel) { form.value.telefono = ''; validarTelefono(); return }
  
  if (tel.startsWith('549') || tel.startsWith('54')) {
    form.value.telefono = '+54 ' + tel.slice(2)
  } else if (tel.startsWith('9')) {
    form.value.telefono = '+54 ' + tel
  } else {
    form.value.telefono = '+54 9' + tel
  }
  
  tel = form.value.telefono.replace(/\D/g, '')
  if (tel.length > 13) {
    form.value.telefono = `+${tel.slice(0, 2)} ${tel.slice(2, 13)}`
  }
  validarTelefono()
}

// ==========================================
// VALIDACIONES INDIVIDUALES
// ==========================================
const validarNombre = () => {
  const val = form.value.nombre.trim()
  errores.value.nombre = !val ? 'El nombre es obligatorio' : (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val) ? 'Solo letras (2-50 caracteres)' : '')
}

const validarApellido = () => {
  const val = form.value.apellido.trim()
  errores.value.apellido = !val ? 'El apellido es obligatorio' : (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val) ? 'Solo letras (2-50 caracteres)' : '')
}

const validarTelefono = () => {
  const val = form.value.telefono.trim()
  const limpio = val.replace(/\s+/g, '')
  errores.value.telefono = !val ? 'El teléfono es obligatorio' : (!/^\+54\s?9\d{10}$/.test(limpio) ? 'Formato: +54 9 3755 558911' : '')
}

const validarContrasena = () => {
  const val = form.value.contrasena
  errores.value.contrasena = !val ? 'La contraseña es obligatoria' : (val.length < 6 ? 'Mínimo 6 caracteres' : (!/(?=.*[A-Z])(?=.*\d)/.test(val) ? '1 mayúscula y 1 número' : ''))
  if (form.value.confirmarContrasena) validarConfirmarContrasena()
}

const validarConfirmarContrasena = () => {
  const val = form.value.confirmarContrasena
  errores.value.confirmarContrasena = !val ? 'Confirma la contraseña' : (val !== form.value.contrasena ? 'Las contraseñas no coinciden' : '')
}

const validarRol = () => { errores.value.rol_id = !form.value.rol_id ? 'Selecciona un rol' : '' }

// ==========================================
// 🚨 VALIDACIONES DE DUPLICADOS EN TIEMPO REAL
// ==========================================
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
  
  // Chequeo contra el array descargado
  if (usuariosExistentes.value && usuariosExistentes.value.length > 0) {
    const existe = usuariosExistentes.value.some(u => String(u.dni) === String(val))
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

  // Chequeo contra el array descargado
  if (usuariosExistentes.value && usuariosExistentes.value.length > 0) {
    const existe = usuariosExistentes.value.some(u => u.correo && u.correo.toLowerCase() === val)
    if (existe) {
      errores.value.correo = 'Ya existe un usuario con este correo'
      alertaDuplicado('Correo ya registrado', 'Este correo ya está en uso. Por favor, usa otro.')
      return
    }
  }

  errores.value.correo = ''
}

// Alerta genérica tipo Toast para no ser tan invasivos pero sí claros
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

const forzarValidacionCompleta = () => {
  validarNombre(); validarApellido(); validarDNI(); validarTelefono(); 
  validarCorreo(); validarContrasena(); validarConfirmarContrasena();
  if (!vieneDeTurnos.value) validarRol()
}

// ==========================================
// 🔒 COMPUTADA PARA DESHABILITAR EL BOTÓN
// ==========================================
// Retorna TRUE si hay algún error o si los campos requeridos están vacíos
const botonDeshabilitado = computed(() => {
  // 1. Hay algún mensaje de error visible?
  const hayErrores = Object.values(errores.value).some(e => e !== '')
  
  // 2. Faltan campos requeridos por llenar?
  const camposVacios = !form.value.nombre || !form.value.apellido || !form.value.dni || 
                       !form.value.telefono || !form.value.correo || !form.value.contrasena || 
                       !form.value.confirmarContrasena || (!vieneDeTurnos.value && !form.value.rol_id)
                       
  return hayErrores || camposVacios || cargando.value
})

// ==========================================
// ENVÍO AL BACKEND
// ==========================================
const crearUsuario = async () => {
  forzarValidacionCompleta()
  
  if (botonDeshabilitado.value) {
    Swal.fire({ icon: 'error', title: 'Formulario incompleto', text: 'Revisa los errores en rojo', background: '#1e293b', color: '#f1f5f9' })
    return
  }

  // Validar administrador único
  if (!vieneDeTurnos.value) {
    const rolNombreSeleccionado = roles.value.find(r => r.id == form.value.rol_id)?.nombre?.toLowerCase()
    const hayOtroAdmin = usuariosExistentes.value.some(u => u.rol_nombre?.toLowerCase() === 'administrador' && u.estado === 'ACTIVO')

    if (rolNombreSeleccionado === 'administrador' && hayOtroAdmin) {
      Swal.fire({ icon: 'warning', title: 'Administrador existente', text: 'Ya existe un administrador activo. No se puede crear otro.', background: '#1e293b', color: '#f1f5f9' })
      return
    }
  }

  cargando.value = true

  try {
    let telefonoParaBackend = '+' + form.value.telefono.replace(/\s+/g, '').replace('+', '')
    
    const payload = {
      nombre: form.value.nombre.trim(),
      apellido: form.value.apellido.trim(),
      dni: form.value.dni.trim(),
      telefono: telefonoParaBackend,
      correo: form.value.correo.trim(),
      contrasena: form.value.contrasena,
      rol: vieneDeTurnos.value ? idRolCliente.value : form.value.rol_id,
      estado: 'ACTIVO'
    }

    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    const response = await axios.post(`${API_BASE}/api/usuarios/crear/`, payload)
    
    if (vieneDeTurnos.value) {
      const nombreCompleto = encodeURIComponent(payload.nombre) + '+' + encodeURIComponent(payload.apellido)
      await Swal.fire({ icon: 'success', title: '¡Cliente Registrado!', text: 'Volviendo a turnos...', showConfirmButton: false, timer: 1000, background: '#1e293b', color: '#f1f5f9' })
      router.push(`/turnos/crear-presencial?nuevo_cliente_id=${response.data.id}&nuevo_cliente_nombre=${nombreCompleto}`).then(() => window.location.reload())
    } else {
      await Swal.fire({ icon: 'success', title: 'Usuario creado', showConfirmButton: false, timer: 1000, background: '#1e293b', color: '#f1f5f9' })
      router.push('/usuarios').then(() => window.location.reload())
    }

  } catch (error) {
    console.error('❌ Error creando usuario:', error)
    
    // 🔥 ARREGLO CLAVE 2: Red de seguridad en caso de que el backend mande un 400
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
          text: 'El DNI o Correo ingresado ya se encuentran registrados.',
          background: '#1e293b',
          color: '#f1f5f9'
        })
        cargando.value = false
        return
      }
    }
    
    const msg = error.response?.data?.error || error.response?.data?.message || 'Error al guardar el usuario.'
    Swal.fire({ icon: 'error', title: 'Error', text: msg, background: '#1e293b', color: '#f1f5f9' })
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
/* ESTILOS MODERNOS CON TUS COLORES */

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

/* 🎯 NOTA DE CONTEXTO PARA TURNOS */
.turno-notice {
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  animation: slideIn 0.5s ease;
}

.notice-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.notice-content h3 {
  margin: 0 0 8px 0;
  color: #f1f5f9;
  font-size: 18px;
}

.notice-content p {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* HEADER ESTILIZADO */
.form-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.9;
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

/* CONTENIDO DEL FORM */
.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* FILAS DEL FORM */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* CAMPOS INDIVIDUALES */
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

/* INPUTS ESTILIZADOS */
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
  border-radius: 14px; /* BORDES REDONDEADOS EN TODOS LADOS */
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

.input-wrapper input.error:focus {
  box-shadow: 
    0 0 0 4px rgba(239, 68, 68, 0.2),
    0 4px 20px rgba(239, 68, 68, 0.1);
}

/* ICONOS EN INPUTS */
.input-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 18px;
  pointer-events: none;
}

/* PASSWORD WRAPPER */
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

.password-toggle:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.3);
}

/* SELECT ESTILIZADO */
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

/* ERRORES */
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

/* BOTÓN MODERNO */
.submit-button {
  width: 100%;
  padding: 18px 32px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 14px; /* BORDES REDONDEADOS */
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-top: 10px;
  position: relative;
  overflow: hidden;
}

.submit-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s;
}

.submit-button:hover:not(:disabled)::before {
  left: 100%;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 
    0 12px 40px rgba(14, 165, 233, 0.4),
    0 4px 15px rgba(14, 165, 233, 0.3);
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
}

.submit-button:active:not(:disabled) {
  transform: translateY(-1px);
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
  transform: translateX(4px);
}

/* FULL WIDTH */
.full-width {
  grid-column: 1 / -1;
}

/* RESPONSIVE */
@media (max-width: 900px) {
  .modern-form {
    padding: 32px;
    border-radius: 20px;
    margin: 16px;
  }
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
  
  .turno-notice {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .modern-form {
    padding: 20px;
    border-radius: 16px;
  }
  
  .form-header h1 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .input-wrapper input,
  .select-wrapper select {
    padding: 14px 48px 14px 16px;
    font-size: 14px;
  }
  
  .submit-button {
    padding: 16px 24px;
    font-size: 15px;
  }
}

/* EFECTO DE GLOW EN FOCUS */
@keyframes glow {
  0%, 100% {
    box-shadow: 
      0 0 0 4px rgba(14, 165, 233, 0.2),
      0 4px 20px rgba(14, 165, 233, 0.15);
  }
  50% {
    box-shadow: 
      0 0 0 4px rgba(14, 165, 233, 0.3),
      0 4px 25px rgba(14, 165, 233, 0.25);
  }
}

.input-wrapper input:focus,
.select-wrapper select:focus {
  animation: glow 2s infinite;
}
</style>