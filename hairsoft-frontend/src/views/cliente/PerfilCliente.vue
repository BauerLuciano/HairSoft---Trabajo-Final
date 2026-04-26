<template>
  <div class="perfil-container">
    <div class="header">
      <h1>Mis Datos</h1>
      <button @click="$router.push('/cliente/dashboard')" class="btn-volver">
        Volver
      </button>
    </div>

    <div v-if="cargando" class="loading">
      <div class="spinner"></div>
      <p>Cargando información...</p>
    </div>

    <div v-else class="perfil-card">
      <form @submit.prevent="guardarCambios" autocomplete="off">
        <h3 class="section-title">Datos Personales</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre</label>
            <input
              type="text"
              v-model="form.nombre"
              placeholder="Tu nombre"
              required
              :class="{ 'error': errores.nombre }"
              @blur="validarNombre"
            />
            <span v-if="errores.nombre" class="error-message">
              {{ errores.nombre }}
            </span>
          </div>

          <div class="form-group">
            <label>Apellido</label>
            <input
              type="text"
              v-model="form.apellido"
              placeholder="Tu apellido"
              required
              :class="{ 'error': errores.apellido }"
              @blur="validarApellido"
            />
            <span v-if="errores.apellido" class="error-message">
              {{ errores.apellido }}
            </span>
          </div>

          <div class="form-group">
            <label>DNI</label>
            <input
              type="text"
              v-model="form.dni"
              placeholder="Tu número de documento"
              required
              :class="{ 'error': errores.dni }"
              @input="validarDNI"
              @blur="validarDNI"
              maxlength="8"
            />
            <span v-if="errores.dni" class="error-message">
              {{ errores.dni }}
            </span>
          </div>

          <div class="form-group">
            <label>Correo Electrónico</label>
            <input
              type="email"
              v-model="form.correo"
              placeholder="nombre@ejemplo.com"
              required
              :class="{ 'error': errores.correo }"
              @input="validarCorreo"
              @blur="validarCorreo"
            />
            <span v-if="errores.correo" class="error-message">
              {{ errores.correo }}
            </span>
          </div>

          <div class="form-group" style="grid-column: 1 / -1">
            <label>Teléfono / Celular</label>
            <input
              type="tel"
              v-model="form.telefono"
              placeholder="Ej: 3758 123456"
              autocomplete="tel"
              :class="{ 'error': errores.telefono }"
              @input="validarTelefono"
              @blur="validarTelefono"
            />
            <span v-if="errores.telefono" class="error-message">
              {{ errores.telefono }}
            </span>
          </div>
        </div>

        <div class="divider"></div>

        <h3 class="section-title">Seguridad</h3>
        <p class="help-text">
          Completá estos campos solo si querés cambiar tu contraseña.
        </p>

        <div class="form-grid">
          <!-- Contraseña actual -->
          <div class="form-group password-group">
            <label>Contraseña Actual</label>
            <div class="input-wrapper">
              <input
                :type="showPassword.current ? 'text' : 'password'"
                v-model="form.currentPassword"
                placeholder="Escribí tu contraseña actual"
                autocomplete="new-password"
                :class="{ 'error': errores.currentPassword }"
              />
              <button
                type="button"
                class="toggle-password"
                @click="showPassword.current = !showPassword.current"
                tabindex="-1"
                aria-label="Mostrar contraseña"
              >
                <svg v-if="!showPassword.current" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <span v-if="isChangingPassword && !form.currentPassword" class="error-message">
              Requerido para cambiar la contraseña
            </span>
          </div>

          <!-- Nueva contraseña -->
          <div class="form-group password-group">
            <label>Nueva Contraseña</label>
            <div class="input-wrapper">
              <input
                :type="showPassword.new ? 'text' : 'password'"
                v-model="form.newPassword"
                placeholder="Mín 6 caracteres, 1 mayúscula, 1 número"
                autocomplete="new-password"
                :class="{ 'error': errores.newPassword }"
              />
              <button
                type="button"
                class="toggle-password"
                @click="showPassword.new = !showPassword.new"
                tabindex="-1"
                aria-label="Mostrar contraseña"
              >
                <svg v-if="!showPassword.new" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <!-- Requisitos dinámicos -->
            <div v-if="isChangingPassword" class="password-requirements">
              <ul class="requirement-list">
                <li :class="passwordValidations.minLength ? 'valid' : 'invalid'">
                  <svg v-if="passwordValidations.minLength" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  Al menos 6 caracteres
                </li>
                <li :class="passwordValidations.hasUpper ? 'valid' : 'invalid'">
                  <svg v-if="passwordValidations.hasUpper" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  Al menos 1 mayúscula
                </li>
                <li :class="passwordValidations.hasNumber ? 'valid' : 'invalid'">
                  <svg v-if="passwordValidations.hasNumber" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  Al menos 1 número
                </li>
              </ul>
            </div>
          </div>

          <!-- Confirmar nueva contraseña -->
          <div class="form-group password-group" style="grid-column: span 2">
            <label>Confirmar Nueva Contraseña</label>
            <div class="input-wrapper">
              <input
                :type="showPassword.confirm ? 'text' : 'password'"
                v-model="form.confirmNewPassword"
                placeholder="Repetí la nueva contraseña"
                autocomplete="new-password"
                :class="{ 'error': errores.confirmNewPassword }"
              />
              <button
                type="button"
                class="toggle-password"
                @click="showPassword.confirm = !showPassword.confirm"
                tabindex="-1"
                aria-label="Mostrar contraseña"
              >
                <svg v-if="!showPassword.confirm" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <span v-if="isChangingPassword && form.confirmNewPassword !== '' && !passwordsMatch" class="error-message">
              Las contraseñas no coinciden
            </span>
          </div>
        </div>

        <button type="submit" class="btn-guardar" :disabled="saveButtonDisabled">
          {{ guardando ? 'Guardando cambios...' : 'Actualizar Perfil' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/services/api'
import Swal from 'sweetalert2'

const isProduction = window.location.hostname.includes('vercel.app') || window.location.hostname.includes('railway.app')
const DOMAIN = isProduction ? 'https://web-production-ac47c.up.railway.app' : 'http://127.0.0.1:8000'

// ---------- ESTADOS ----------
const form = ref({
  nombre: '',
  apellido: '',
  correo: '',
  dni: '',
  telefono: '',
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: ''
})

const cargando = ref(true)
const guardando = ref(false)
const showPassword = reactive({ current: false, new: false, confirm: false })
const usuariosExistentes = ref([])

// Errores de validación
const errores = ref({
  nombre: '',
  apellido: '',
  dni: '',
  correo: '',
  telefono: '',
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: ''
})

// ---------- COMPUTADAS ----------
const isChangingPassword = computed(() => form.value.newPassword !== '' || form.value.confirmNewPassword !== '')

const passwordValidations = computed(() => {
  const pwd = form.value.newPassword
  return {
    minLength: pwd.length >= 6,
    hasUpper: /[A-Z]/.test(pwd),
    hasNumber: /[0-9]/.test(pwd)
  }
})

const allPasswordValid = computed(() => passwordValidations.value.minLength && passwordValidations.value.hasUpper && passwordValidations.value.hasNumber)
const passwordsMatch = computed(() => form.value.newPassword === form.value.confirmNewPassword)

const canSave = computed(() => {
  // Validar campos obligatorios no vacíos
  if (!form.value.nombre.trim() || !form.value.apellido.trim() || !form.value.dni.trim() || !form.value.correo.trim()) return false
  // Validar que no haya errores de formato / unicidad
  if (errores.value.nombre || errores.value.apellido || errores.value.dni || errores.value.correo) return false
  if (errores.value.telefono) return false

  // Si se está cambiando contraseña
  if (isChangingPassword.value) {
    if (!form.value.currentPassword) return false
    if (!allPasswordValid.value) return false
    if (!passwordsMatch.value) return false
  }
  return true
})

const saveButtonDisabled = computed(() => guardando.value || !canSave.value)

// ---------- CARGA DE DATOS ----------
const cargarUsuariosExistentes = async () => {
  try {
    const response = await api.get(`${DOMAIN}/api/usuarios/`)
    usuariosExistentes.value = response.data || []
  } catch (error) {
    console.error('Error cargando usuarios existentes:', error)
  }
}

const cargarDatos = async () => {
  try {
    const userId = localStorage.getItem('user_id')
    const response = await api.get(`${DOMAIN}/api/usuarios/${userId}/`)
    const data = response.data

    form.value.nombre = data.nombre || ''
    form.value.apellido = data.apellido || ''
    form.value.correo = data.correo || ''
    form.value.dni = data.dni !== 'No registrado' ? data.dni : ''

    const tel = data.telefono || ''
    form.value.telefono = (tel === 'No registrado' || tel.includes('@')) ? '' : tel
  } catch (error) {
    console.error('Error cargando perfil:', error)
    Swal.fire('Error de conexión', 'No pudimos cargar tus datos.', 'error')
  } finally {
    cargando.value = false
  }
}

// ---------- VALIDACIONES ----------
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

// Validación de DNI (formato + unicidad)
const validarDNI = () => {
  const dni = form.value.dni.trim()
  const userId = localStorage.getItem('user_id')

  if (!dni) {
    errores.value.dni = 'El DNI es obligatorio'
    return
  }
  if (!/^\d{7,8}$/.test(dni)) {
    errores.value.dni = 'DNI inválido (7-8 dígitos)'
    return
  }

  // Unicidad
  const existe = usuariosExistentes.value.some(u => u.id != userId && u.dni === dni)
  if (existe) {
    errores.value.dni = 'Este DNI ya está registrado por otro usuario'
  } else {
    errores.value.dni = ''
  }
}

// Validación de correo (formato + unicidad)
const validarCorreo = () => {
  const correo = form.value.correo.trim()
  const userId = localStorage.getItem('user_id')

  if (!correo) {
    errores.value.correo = 'El correo es obligatorio'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
    errores.value.correo = 'Correo electrónico inválido'
    return
  }

  // Unicidad
  const existe = usuariosExistentes.value.some(u => u.id != userId && u.correo?.toLowerCase() === correo.toLowerCase())
  if (existe) {
    errores.value.correo = 'Este correo ya está en uso por otro usuario'
  } else {
    errores.value.correo = ''
  }
}

const validarTelefono = () => {
  const tel = form.value.telefono.trim()
  if (!tel) {
    errores.value.telefono = ''
    return
  }
  // Formato simple: aceptar dígitos, espacios, guiones, +
  if (!/^\+?[\d\s\-]{7,20}$/.test(tel)) {
    errores.value.telefono = 'Formato de teléfono inválido'
  } else {
    errores.value.telefono = ''
  }
}

// ---------- GUARDAR ----------
const guardarCambios = async () => {
  // Forzar validación integral antes de enviar
  validarNombre()
  validarApellido()
  validarDNI()
  validarCorreo()
  validarTelefono()

  if (!canSave.value) {
    Swal.fire('Formulario incompleto', 'Por favor, corregí los errores antes de guardar.', 'error')
    return
  }

  guardando.value = true
  try {
    const userId = localStorage.getItem('user_id')
    const payload = {
      nombre: form.value.nombre.trim(),
      apellido: form.value.apellido.trim(),
      dni: form.value.dni.trim(),
      correo: form.value.correo.trim(),
      telefono: form.value.telefono.trim()
    }

    if (form.value.newPassword) {
      payload.contrasena_nueva = form.value.newPassword
      payload.contrasena_actual = form.value.currentPassword
    }

    await api.patch(`${DOMAIN}/api/usuarios/editar/${userId}/`, payload)

    Swal.fire({
      title: '¡Éxito!',
      text: 'Tus datos han sido actualizados.',
      icon: 'success',
      timer: 2000,
      showConfirmButton: false
    })

    // Limpiar contraseñas
    form.value.currentPassword = ''
    form.value.newPassword = ''
    form.value.confirmNewPassword = ''
  } catch (error) {
    console.error('Error guardando perfil:', error)
    let msg = 'Error del servidor al guardar los cambios.'
    if (error.response?.data) {
      if (error.response.data.correo) msg = 'Ese correo ya está en uso por otro usuario.'
      else if (error.response.data.dni) msg = 'Ese DNI ya está registrado en el sistema.'
      else if (error.response.data.error) msg = error.response.data.error
      else if (error.response.data.message) msg = error.response.data.message
    }
    Swal.fire('Error', msg, 'error')
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await cargarUsuariosExistentes()
  await cargarDatos()
})
</script>

<style scoped>
/* =============================================
   RESET DE AUTOFILL PARA MODO OSCURO
   ============================================= */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px var(--bg-primary, #1e1e2f) inset !important;
  -webkit-text-fill-color: var(--text-primary, #e1e1e1) !important;
  transition: background-color 5000s ease-in-out 0s;
  caret-color: var(--text-primary, #e1e1e1);
}

/* Ocultar el ojo nativo de Edge/Chrome */
input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear {
  display: none;
}
input[type="password"]::-webkit-credentials-auto-fill-button {
  visibility: hidden;
}

/* Estilo para inputs con error */
input.error {
  border-color: #f87171 !important;
  background: rgba(239, 68, 68, 0.05) !important;
}

/* Resto de estilos (idénticos a tu diseño premium) */
.perfil-container { max-width: 800px; margin: 2rem auto; padding: 0 1.5rem; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem; }
.header h1 { margin: 0; color: var(--text-primary); font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px; }
.btn-volver { background: transparent; border: 2px solid var(--border-color); color: var(--text-secondary); padding: 0.6rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-volver:hover { border-color: var(--text-primary); color: var(--text-primary); background-color: rgba(255,255,255,0.05); }
.perfil-card { background: var(--bg-secondary); padding: 3rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5); }
.section-title { color: var(--accent-color); margin: 0 0 1.2rem 0; font-size: 1.25rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.help-text { font-size: 0.9rem; color: var(--text-secondary); margin-top: -0.8rem; margin-bottom: 1.5rem; opacity: 0.8; }
.form-grid { display: grid; gap: 1.8rem; }
.form-group { display: flex; flex-direction: column; }
.form-group label { margin-bottom: 0.6rem; color: var(--text-secondary); font-weight: 600; font-size: 0.9rem; }
input { width: 100%; padding: 0.9rem 1.2rem; border-radius: 10px; border: 1px solid var(--border-color); background: var(--bg-primary); color: var(--text-primary); font-size: 1rem; transition: all 0.3s; }
input:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px rgba(var(--accent-color-rgb, 0,123,255), 0.2); }
input::placeholder { color: #6b7280; opacity: 0.8; }
.password-group .input-wrapper { position: relative; display: flex; align-items: center; }
.password-group .input-wrapper input { padding-right: 3rem; }
.toggle-password { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: transparent; border: none; padding: 4px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; justify-content: center; transition: color 0.2s; z-index: 2; }
.toggle-password:hover { color: var(--accent-color); }
.error-message { color: #f87171; font-size: 0.8rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.3rem; }
.password-requirements { margin-top: 0.8rem; background: rgba(255,255,255,0.03); border-radius: 8px; padding: 0.8rem 1rem; border: 1px solid rgba(255,255,255,0.05); }
.requirement-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.requirement-list li { font-size: 0.8rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem; }
.requirement-list li.valid { color: #34d399; }
.requirement-list li.invalid { color: #f87171; }
.divider { height: 1px; background: var(--border-color); margin: 3rem 0; opacity: 0.6; }
.btn-guardar { width: 100%; padding: 1.1rem; background: var(--accent-color); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 1.1rem; cursor: pointer; margin-top: 2.5rem; transition: all 0.3s; box-shadow: 0 4px 6px rgba(var(--accent-color-rgb, 0,123,255), 0.2); }
.btn-guardar:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(var(--accent-color-rgb, 0,123,255), 0.3); filter: brightness(1.05); }
.btn-guardar:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; filter: grayscale(0.3); }
.loading { text-align: center; padding: 5rem 0; color: var(--text-secondary); }
.spinner { border: 4px solid rgba(255,255,255,0.1); border-top-color: var(--accent-color); border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 1.5rem auto; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (min-width: 768px) { .form-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .perfil-card { padding: 1.5rem; } .header h1 { font-size: 1.8rem; } }
</style>