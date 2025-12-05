<template>
  <div class="public-register-page">
    <div class="form-card">
      <div class="form-header">
        <h1>Crear Cuenta</h1>
        <p>Únete a HairSoft y reserva tus turnos online</p>
      </div>

      <form @submit.prevent="crearUsuario" class="form-grid" autocomplete="off">
        <div class="input-group">
          <label>Nombre <span class="required">*</span></label>
          <input 
            v-model="form.nombre" 
            type="text" 
            placeholder="Tu nombre" 
            required 
            @blur="validarNombre"
            :class="{ 'campo-invalido': errores.nombre }"
          />
          <div class="error-message" v-if="errores.nombre">{{ errores.nombre }}</div>
        </div>

        <div class="input-group">
          <label>Apellido <span class="required">*</span></label>
          <input 
            v-model="form.apellido" 
            type="text" 
            placeholder="Tu apellido" 
            required 
            @blur="validarApellido"
            :class="{ 'campo-invalido': errores.apellido }"
          />
          <div class="error-message" v-if="errores.apellido">{{ errores.apellido }}</div>
        </div>

        <div class="input-group">
          <label>DNI <span class="required">*</span></label>
          <input 
            v-model="form.dni" 
            type="text" 
            placeholder="Tu DNI (sin puntos)" 
            required 
            @blur="validarDNI"
            maxlength="8"
            :class="{ 'campo-invalido': errores.dni }"
          />
          <div class="error-message" v-if="errores.dni">{{ errores.dni }}</div>
        </div>

        <div class="input-group">
          <label>Teléfono</label>
          <input 
            v-model="form.telefono" 
            type="text" 
            placeholder="Tu celular" 
            @blur="validarTelefono"
            maxlength="15"
            :class="{ 'campo-invalido': errores.telefono }"
          />
          <div class="error-message" v-if="errores.telefono">{{ errores.telefono }}</div>
        </div>

        <div class="input-group full-width">
          <label>Correo Electrónico <span class="required">*</span></label>
          <input 
            v-model="form.correo" 
            type="email" 
            placeholder="ejemplo@email.com" 
            required 
            autocomplete="off"
            @blur="validarCorreo"
            :class="{ 'campo-invalido': errores.correo }"
          />
          <div class="error-message" v-if="errores.correo">{{ errores.correo }}</div>
        </div>

        <div class="input-group">
          <label>Contraseña <span class="required">*</span></label>
          <input 
            v-model="form.contrasena" 
            type="password" 
            placeholder="Mínimo 6 caracteres" 
            required 
            autocomplete="new-password"
            @blur="validarContrasena"
            :class="{ 'campo-invalido': errores.contrasena }"
          />
          <div class="error-message" v-if="errores.contrasena">{{ errores.contrasena }}</div>
        </div>

        <div class="input-group">
          <label>Confirmar <span class="required">*</span></label>
          <input 
            v-model="form.confirmarContrasena" 
            type="password" 
            placeholder="Repite la contraseña" 
            required 
            autocomplete="new-password"
            @blur="validarConfirmarContrasena"
            :class="{ 'campo-invalido': errores.confirmarContrasena }"
          />
          <div class="error-message" v-if="errores.confirmarContrasena">{{ errores.confirmarContrasena }}</div>
        </div>

        <div class="full-width actions-row">
          <button type="submit" class="submit-btn" :disabled="cargando">
            <span v-if="cargando">Procesando...</span>
            <span v-else>Registrarme</span>
          </button>
        </div>

        <div class="full-width login-link">
          ¿Ya tienes cuenta? <router-link to="/login">Inicia Sesión aquí</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

const router = useRouter()
// Ajusta si es necesario
const API_BASE = 'http://127.0.0.1:8000'; 

const cargando = ref(false)
const idRolCliente = ref(null)

const form = ref({
  nombre: '', apellido: '', dni: '', telefono: '',
  correo: '', contrasena: '', confirmarContrasena: ''
})

const errores = ref({
  nombre: '', apellido: '', dni: '', telefono: '',
  correo: '', contrasena: '', confirmarContrasena: ''
})

// 🔹 Al montar, buscamos silenciosamente el ID del rol "Cliente"
onMounted(async () => {
  try {
    // Nota: Esta petición debe ser pública (AllowAny) en el backend, 
    // o deberás hardcodear el ID si no quieres exponer /roles/
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    const roles = res.data || []
    // Buscamos flexiblemente 'Cliente', 'cliente', 'CLIENTE'
    const rolEncontrado = roles.find(r => r.nombre.toLowerCase().includes('cliente'))
    
    if (rolEncontrado) {
      idRolCliente.value = rolEncontrado.id
    } else {
      console.error('⚠️ No se encontró el rol CLIENTE en la base de datos.')
      Swal.fire('Error de Configuración', 'No se pueden registrar clientes en este momento.', 'error')
    }
  } catch (error) {
    console.error('Error al cargar roles:', error)
  }
})

// ------------------------------
// VALIDACIONES (Idénticas a tu original)
// ------------------------------
const validarNombre = () => {
  const valor = form.value.nombre.trim()
  if (!valor) errores.value.nombre = "Requerido"
  else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(valor)) errores.value.nombre = "Solo letras (2-50 chars)"
  else errores.value.nombre = ""
}
const validarApellido = () => {
  const valor = form.value.apellido.trim()
  if (!valor) errores.value.apellido = "Requerido"
  else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(valor)) errores.value.apellido = "Solo letras (2-50 chars)"
  else errores.value.apellido = ""
}
const validarDNI = () => {
  const dni = form.value.dni.trim()
  if (!dni) errores.value.dni = "Requerido"
  else if (!/^\d{7,8}$/.test(dni)) errores.value.dni = "DNI inválido (7-8 números)"
  else errores.value.dni = ""
}
const validarTelefono = () => {
  const tel = form.value.telefono.trim()
  if (tel && !/^\+?[\d\s\-\(\)]{6,15}$/.test(tel)) errores.value.telefono = "Número inválido"
  else errores.value.telefono = ""
}
const validarCorreo = () => {
  const correo = form.value.correo.trim()
  if (!correo) errores.value.correo = "Requerido"
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) errores.value.correo = "Correo inválido"
  else errores.value.correo = ""
}
const validarContrasena = () => {
  const pass = form.value.contrasena
  if (!pass) errores.value.contrasena = "Requerida"
  else if (pass.length < 6) errores.value.contrasena = "Mínimo 6 caracteres"
  else if (!/(?=.*[A-Z])(?=.*\d)/.test(pass)) errores.value.contrasena = "Falta mayúscula y número"
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
  return !Object.values(errores.value).some(e => e)
}

// ----------------------------------
// CREAR USUARIO
// ----------------------------------
const crearUsuario = async () => {
  if (!validarFormulario()) return
  
  if (!idRolCliente.value) {
    Swal.fire('Error', 'Error interno: No se pudo asignar el rol de cliente.', 'error')
    return
  }

  cargando.value = true
  
  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      apellido: form.value.apellido.trim(),
      dni: form.value.dni.trim(),
      telefono: form.value.telefono.trim() || '',
      correo: form.value.correo.trim(),
      contrasena: form.value.contrasena,
      rol: idRolCliente.value, // ✅ ASIGNACIÓN AUTOMÁTICA
      estado: 'ACTIVO'
    }

    // Usamos el endpoint de crear usuario (Asegúrate que el backend permita esto sin token)
    await axios.post(`${API_BASE}/usuarios/api/usuarios/crear/`, payload)

    await Swal.fire({
      icon: 'success',
      title: '¡Bienvenido!',
      text: 'Tu cuenta ha sido creada exitosamente. Por favor inicia sesión.',
      confirmButtonText: 'Ir al Login',
      confirmButtonColor: '#0ea5e9'
    })

    router.push('/login')

  } catch (err) {
    console.error(err)
    let msg = 'No se pudo crear la cuenta.'
    if (err.response?.data?.error) msg = err.response.data.error
    else if (err.response?.data?.message) msg = err.response.data.message
    
    Swal.fire({
      icon: 'error',
      title: 'Error de Registro',
      text: msg,
      confirmButtonColor: '#ef4444'
    })
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
/* Reutilizamos variables pero con un fondo de página específico */
.public-register-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-primary); /* #0f172a según tu App.vue */
  padding: 20px;
}

/* Reutilizando tus estilos de form-card con ajustes */
.form-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 800px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #8b5cf6); /* Azul a Púrpura */
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 20px;
}

.form-header h1 {
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 5px;
}
.form-header p { color: var(--text-secondary); }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.input-group { display: flex; flex-direction: column; }
.full-width { grid-column: 1 / -1; }

label {
  font-size: 0.85rem;
  font-weight: bold;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
}

.required { color: #ef4444; }

input {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s;
}

input:focus {
  outline: none;
  border-color: #0ea5e9;
  background: rgba(255,255,255,0.1);
}

.campo-invalido { border-color: #ef4444 !important; }
.error-message { color: #ef4444; font-size: 0.8rem; margin-top: 5px; }

.submit-btn {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 16px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.2s;
  width: 100%;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(14,165,233,0.3); }
.submit-btn:disabled { opacity: 0.7; cursor: wait; }

.login-link {
  text-align: center;
  margin-top: 20px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.login-link a { color: #0ea5e9; text-decoration: none; font-weight: bold; }
.login-link a:hover { text-decoration: underline; }

@media (max-width: 600px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>