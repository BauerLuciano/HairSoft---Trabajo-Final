<template>
  <div class="modern-form">
    <div class="form-header">
      <h1>Crear Cuenta</h1>
      <p class="subtitle">Únete a HairSoft y reserva tus turnos online</p>
    </div>

    <form @submit.prevent="crearUsuario" class="form-content" autocomplete="off">
      
      <input type="text" style="display:none" />
      <input type="password" style="display:none" />

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
              placeholder="Ingresa tu nombre" 
              @blur="validarNombre"
              :class="{ 'error': errores.nombre }"
              autocomplete="off"
              name="new_user_name_hs"
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
              placeholder="Ingresa tu apellido" 
              @blur="validarApellido"
              :class="{ 'error': errores.apellido }"
              autocomplete="off"
              name="new_user_lastname_hs"
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
              placeholder="Tu DNI (sin puntos)" 
              @blur="validarDNI"
              @input="formatearDNI"
              maxlength="8"
              :class="{ 'error': errores.dni }"
              autocomplete="off"
              name="new_user_dni_hs"
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
              placeholder="+54 9 3755..." 
              @blur="validarTelefono"
              @input="formatearTelefono"
              :class="{ 'error': errores.telefono }"
              autocomplete="off"
              name="new_user_phone_hs"
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
            placeholder="ejemplo@email.com" 
            @blur="validarCorreo"
            :class="{ 'error': errores.correo }"
            autocomplete="off" 
            name="new_user_email_random_id" 
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
              @blur="validarContrasena"
              :class="{ 'error': errores.contrasena }"
              autocomplete="new-password"
              name="new_password_field"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarContrasena = !mostrarContrasena"
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
            <label>Confirmar</label>
            <span class="required-badge">Requerido</span>
          </div>
          <div class="input-wrapper password-wrapper">
            <input 
              v-model="form.confirmarContrasena" 
              :type="mostrarConfirmarContrasena ? 'text' : 'password'" 
              placeholder="Repite la contraseña" 
              @blur="validarConfirmarContrasena"
              :class="{ 'error': errores.confirmarContrasena }"
              autocomplete="new-password"
              name="confirm_password_field"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="mostrarConfirmarContrasena = !mostrarConfirmarContrasena"
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

      <button type="submit" class="submit-button" :disabled="cargando">
        <span class="button-content">
          <span class="button-text">{{ cargando ? 'Registrando...' : 'Crear Cuenta' }}</span>
          <span class="button-icon">{{ cargando ? '⏳' : '→' }}</span>
        </span>
      </button>

      <div class="login-link">
        ¿Ya tienes cuenta? <router-link to="/login">Inicia Sesión aquí</router-link>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

const router = useRouter()
// Ajustá si tu puerto es diferente
const API_BASE = 'http://127.0.0.1:8000' 

const cargando = ref(false)
const mostrarContrasena = ref(false)
const mostrarConfirmarContrasena = ref(false)
const idRolCliente = ref(null)
const usuariosExistentes = ref([])

const form = ref({
  nombre: '', apellido: '', dni: '', telefono: '',
  correo: '', contrasena: '', confirmarContrasena: ''
})

const errores = ref({
  nombre: '', apellido: '', dni: '', telefono: '',
  correo: '', contrasena: '', confirmarContrasena: ''
})

// --- CARGA INICIAL ---
onMounted(async () => {
  await cargarUsuariosExistentes()
  await obtenerRolCliente()
})

const cargarUsuariosExistentes = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`) 
    usuariosExistentes.value = res.data
  } catch (error) {
    console.warn('No se pudo cargar lista de usuarios (posiblemente requiere auth)', error)
  }
}

const obtenerRolCliente = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    const rol = res.data.find(r => r.nombre.toLowerCase().includes('cliente'))
    if (rol) {
      idRolCliente.value = rol.id
    } else {
      Swal.fire('Error', 'No se encontró el rol CLIENTE en el sistema.', 'error')
    }
  } catch (error) {
    console.error('Error cargando roles:', error)
  }
}

// --- VALIDACIONES ---
const formatearDNI = () => { form.value.dni = form.value.dni.replace(/\D/g, '').slice(0, 8) }

const formatearTelefono = () => {
  let tel = form.value.telefono.replace(/\D/g, '')
  if (tel.length === 0) { form.value.telefono = ''; return }
  
  if (tel.startsWith('549')) form.value.telefono = '+54 ' + tel.slice(2)
  else if (tel.startsWith('54')) form.value.telefono = '+54 ' + tel.slice(2)
  else if (tel.startsWith('9')) form.value.telefono = '+54 ' + tel
  else form.value.telefono = '+54 9' + tel

  tel = form.value.telefono.replace(/\D/g, '')
  if (tel.length > 13) {
    const codigo = tel.slice(0, 2); const resto = tel.slice(2, 13)
    form.value.telefono = `+${codigo} ${resto}`
  }
}

const validarUnico = (campo, valor) => {
  if (!usuariosExistentes.value.length) return true 
  return !usuariosExistentes.value.some(u => u[campo] === valor)
}

const validarNombre = () => {
  const v = form.value.nombre.trim()
  if (!v) errores.value.nombre = "Requerido"
  else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(v)) errores.value.nombre = "Solo letras"
  else errores.value.nombre = ""
}

const validarApellido = () => {
  const v = form.value.apellido.trim()
  if (!v) errores.value.apellido = "Requerido"
  else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(v)) errores.value.apellido = "Solo letras"
  else errores.value.apellido = ""
}

const validarDNI = () => {
  const v = form.value.dni.trim()
  if (!v) errores.value.dni = "Requerido"
  else if (!/^\d{7,8}$/.test(v)) errores.value.dni = "DNI inválido"
  else if (!validarUnico('dni', v)) errores.value.dni = "Ya registrado"
  else errores.value.dni = ""
}

const validarTelefono = () => {
  const v = form.value.telefono.trim()
  if (v && !/^\+54\s?9\d{10}$/.test(v.replace(/\s+/g, ''))) errores.value.telefono = "Formato inválido"
  else errores.value.telefono = ""
}

const validarCorreo = () => {
  const v = form.value.correo.trim()
  if (!v) errores.value.correo = "Requerido"
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) errores.value.correo = "Correo inválido"
  else if (!validarUnico('correo', v)) errores.value.correo = "Correo ya registrado"
  else errores.value.correo = ""
}

const validarContrasena = () => {
  const v = form.value.contrasena
  if (!v) errores.value.contrasena = "Requerida"
  else if (v.length < 6) errores.value.contrasena = "Mínimo 6 caracteres"
  else if (!/(?=.*[A-Z])(?=.*\d)/.test(v)) errores.value.contrasena = "Falta mayúscula y número"
  else errores.value.contrasena = ""
  if (form.value.confirmarContrasena) validarConfirmarContrasena()
}

const validarConfirmarContrasena = () => {
  if (form.value.confirmarContrasena !== form.value.contrasena) errores.value.confirmarContrasena = "No coinciden"
  else errores.value.confirmarContrasena = ""
}

const validarFormulario = () => {
  validarNombre(); validarApellido(); validarDNI(); validarTelefono(); 
  validarCorreo(); validarContrasena(); validarConfirmarContrasena();
  return !Object.values(errores.value).some(e => e !== "")
}

const crearUsuario = async () => {
  if (!validarFormulario()) return
  if (!idRolCliente.value) {
    Swal.fire('Error', 'No se pudo asignar el rol de cliente.', 'error')
    return
  }

  cargando.value = true
  try {
    let tel = null
    if (form.value.telefono) {
      let limpio = form.value.telefono.replace(/\s+/g, '').replace('+', '')
      if (limpio.length === 13) tel = '+' + limpio
    }

    const payload = {
      nombre: form.value.nombre.trim(),
      apellido: form.value.apellido.trim(),
      dni: form.value.dni.trim(),
      telefono: tel,
      correo: form.value.correo.trim(),
      contrasena: form.value.contrasena,
      rol: idRolCliente.value,
      estado: 'ACTIVO'
    }

    await axios.post(`${API_BASE}/usuarios/api/usuarios/crear/`, payload)

    await Swal.fire({
      icon: 'success',
      title: '¡Bienvenido!',
      text: 'Tu cuenta fue creada. Por favor inicia sesión.',
      confirmButtonText: 'Ir al Login',
      confirmButtonColor: '#0ea5e9',
      background: '#1e293b', color: '#f1f5f9'
    })

    router.push('/login')

  } catch (err) {
    console.error(err)
    let msg = err.response?.data?.error || err.response?.data?.message || 'Error al registrarse'
    if (msg.includes('dni')) errores.value.dni = "DNI ya registrado"
    if (msg.includes('correo')) errores.value.correo = "Correo ya registrado"

    Swal.fire({ 
      icon: 'error', title: 'Error', text: msg,
      background: '#1e293b', color: '#f1f5f9'
    })
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
/* ESTILOS PREMIUM OSCUROS (Idénticos a RegistrarUsuario) */
.modern-form {
  max-width: 900px; margin: 0 auto; padding: 40px;
  background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
  border-radius: 24px; border: 1px solid #334155;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.form-header { text-align: center; margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
.form-header h1 { margin: 0 0 8px 0; font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #f1f5f9 0%, #0ea5e9 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; }
.subtitle { color: #94a3b8; font-size: 16px; margin: 0; }

.form-content { display: flex; flex-direction: column; gap: 24px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.input-field { position: relative; }
.full-width { grid-column: 1 / -1; }

.field-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.field-header label { color: #cbd5e1; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
.required-badge { background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }
.optional-badge { background: rgba(148, 163, 184, 0.15); color: #94a3b8; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }

.input-wrapper { position: relative; width: 100%; }
.input-wrapper input { width: 100%; padding: 16px 20px; background: rgba(15, 23, 42, 0.7); border: 2px solid #334155; border-radius: 14px; color: #f1f5f9; font-size: 15px; font-weight: 500; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); backdrop-filter: blur(10px); box-sizing: border-box; }
.input-wrapper input:focus { outline: none; border-color: #0ea5e9; background: rgba(15, 23, 42, 0.9); box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.2), 0 4px 20px rgba(14, 165, 233, 0.15); transform: translateY(-1px); }
.input-wrapper input.error { border-color: #ef4444; background: rgba(239, 68, 68, 0.07); }
.input-wrapper input.error:focus { box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.2); }

.password-toggle { position: absolute; right: 16px; top: 50%; transform: translateY(-50%); background: transparent; border: none; color: #64748b; font-size: 20px; cursor: pointer; padding: 4px; transition: 0.2s; }
.password-toggle:hover { color: #0ea5e9; }

.field-error { display: flex; align-items: center; gap: 8px; margin-top: 8px; color: #ef4444; font-size: 13px; font-weight: 500; animation: slideIn 0.3s ease; }
.error-dot { width: 6px; height: 6px; background: #ef4444; border-radius: 50%; flex-shrink: 0; }

.submit-button { width: 100%; padding: 18px 32px; background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; border: none; border-radius: 14px; font-size: 16px; font-weight: 700; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); margin-top: 10px; position: relative; overflow: hidden; }
.submit-button::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent); transition: left 0.6s; }
.submit-button:hover:not(:disabled)::before { left: 100%; }
.submit-button:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(14, 165, 233, 0.4), 0 4px 15px rgba(14, 165, 233, 0.3); background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); }
.submit-button:disabled { opacity: 0.5; cursor: not-allowed; }

.button-content { display: flex; align-items: center; justify-content: center; gap: 12px; }
.button-icon { font-size: 18px; transition: transform 0.3s; }
.submit-button:hover:not(:disabled) .button-icon { transform: translateX(4px); }

.login-link { text-align: center; margin-top: 25px; color: #94a3b8; font-size: 0.95rem; }
.login-link a { color: #0ea5e9; text-decoration: none; font-weight: 700; transition: 0.2s; }
.login-link a:hover { color: #38bdf8; text-decoration: underline; }

@keyframes slideIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 900px) { .modern-form { padding: 32px; border-radius: 20px; margin: 16px; } }
@media (max-width: 768px) { .form-row { grid-template-columns: 1fr; gap: 20px; } .form-header h1 { font-size: 28px; } }
</style>