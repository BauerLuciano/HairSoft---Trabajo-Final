<template>
  <div class="user-form">
    <div class="form-card">
      <div class="form-header">
        <h1>Modificar Usuario</h1>
        <p>Edita los datos del usuario</p>
      </div>

      <form @submit.prevent="actualizarUsuario" class="form">
        <div class="form-grid">
          <!-- Nombre -->
          <div class="input-group">
            <label>Nombre <span class="required">*</span></label>
            <input v-model="form.nombre" type="text" placeholder="Ingrese el nombre" required />
          </div>

          <!-- Apellido -->
          <div class="input-group">
            <label>Apellido <span class="required">*</span></label>
            <input v-model="form.apellido" type="text" placeholder="Ingrese el apellido" required />
          </div>

          <!-- DNI -->
          <div class="input-group">
            <label>DNI <span class="required">*</span></label>
            <input v-model="form.dni" type="text" placeholder="Ingrese el DNI" required maxlength="8" />
          </div>

          <!-- Teléfono -->
          <div class="input-group">
            <label>Teléfono</label>
            <input v-model="form.telefono" type="text" placeholder="Ingrese el teléfono" maxlength="15" />
          </div>

          <!-- Correo -->
          <div class="input-group">
            <label>Correo <span class="required">*</span></label>
            <input v-model="form.correo" type="email" placeholder="Ingrese el correo electrónico" required />
          </div>

          <!-- Contraseña actual -->
          <div class="input-group">
            <label>Contraseña actual</label>
            <input v-model="form.contrasena_actual" type="password" placeholder="Ingrese la contraseña actual (solo si cambia contraseña)" />
          </div>

          <!-- Nueva contraseña -->
          <div class="input-group">
            <label>Nueva Contraseña</label>
            <input v-model="form.nueva_contrasena" type="password" placeholder="Ingrese nueva contraseña (opcional)" />
          </div>

          <!-- Rol -->
          <div class="input-group">
            <label>Rol <span class="required">*</span></label>
            <select v-model="form.rol" required>
              <option value="">Seleccionar rol</option>
              <option value="ADMINISTRADOR">Administrador</option>
              <option value="RECEPCIONISTA">Recepcionista</option>
              <option value="PELUQUERO">Peluquero</option>
              <option value="CLIENTE">Cliente</option>
            </select>
            <div class="select-arrow">▼</div>
          </div>

          <div class="full-width">
            <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
            <button type="submit" class="submit-btn">
              <span class="btn-text">Actualizar Usuario</span>
              <span class="btn-icon">→</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const API_BASE = 'http://127.0.0.1:8000'

const usuarioId = ref(route.params.id)
const form = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena_actual: '',
  nueva_contrasena: '',
  rol: '',
  estado: 'ACTIVO'
})
const errorMessage = ref('')

// Cargar datos del usuario
const cargarUsuario = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    const todosLosUsuarios = res.data
    const usuario = todosLosUsuarios.find(u => u.id == usuarioId.value)
    if (!usuario) {
      errorMessage.value = 'Usuario no encontrado'
      router.push('/usuarios')
      return
    }

    // Mapear roles
    const rolMap = { 'ADMIN': 'ADMINISTRADOR', 'REC': 'RECEPCIONISTA', 'PEL': 'PELUQUERO', 'CLI': 'CLIENTE' }
    const rolFinal = usuario.rol ? rolMap[usuario.rol.toUpperCase()] || 'CLIENTE' : 'CLIENTE'

    form.value.nombre = usuario.nombre || ''
    form.value.apellido = usuario.apellido || ''
    form.value.dni = usuario.dni || ''
    form.value.telefono = usuario.telefono || ''
    form.value.correo = usuario.correo || ''
    form.value.contrasena_actual = ''
    form.value.nueva_contrasena = ''
    form.value.rol = rolFinal
    form.value.estado = usuario.estado || 'ACTIVO'
  } catch (error) {
    errorMessage.value = 'Error al cargar los datos del usuario'
    console.error(error)
  }
}

// Verificar si ya existe un administrador
const checkExistingAdmin = async () => {
  if (form.value.rol !== 'ADMINISTRADOR') return true
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    const usuarios = res.data
    const adminExists = usuarios.some(u => u.rol === 'ADMIN' && u.id !== parseInt(usuarioId.value))
    return !adminExists
  } catch (err) {
    errorMessage.value = 'Error al verificar administradores'
    console.error(err)
    return false
  }
}

// Validar formulario
const validarFormulario = () => {
  if (!form.value.nombre || !form.value.apellido || !form.value.dni || !form.value.correo || !form.value.rol) {
    errorMessage.value = 'Complete todos los campos obligatorios'
    return false
  }
  if (form.value.dni.length !== 8) {
    errorMessage.value = 'El DNI debe tener 8 dígitos'
    return false
  }
  if (form.value.nueva_contrasena && !form.value.contrasena_actual) {
    errorMessage.value = 'Para cambiar la contraseña, debe ingresar la contraseña actual'
    return false
  }
  return true
}

// Actualizar usuario
const actualizarUsuario = async () => {
  if (!validarFormulario()) return

  const canAssignAdmin = await checkExistingAdmin()
  if (!canAssignAdmin) {
    errorMessage.value = 'Solo puede existir un administrador. Por favor, elija otro rol.'
    return
  }

  try {
    const payload = {
      nombre: form.value.nombre,
      apellido: form.value.apellido,
      dni: form.value.dni,
      telefono: form.value.telefono || '',
      correo: form.value.correo,
      rol: form.value.rol,
      estado: form.value.estado || 'ACTIVO',
      contrasena: form.value.nueva_contrasena || '' // siempre se envía
    }

    if (form.value.nueva_contrasena && form.value.contrasena_actual) {
      payload.contrasena_actual = form.value.contrasena_actual
    }

    await axios.post(`${API_BASE}/usuarios/api/usuarios/editar/${usuarioId.value}/`, payload)
    alert('Usuario actualizado con éxito')
    router.push('/usuarios')
  } catch (err) {
    if (err.response?.status === 400) {
      const errors = err.response.data.errors || err.response.data
      let msg = 'Error en los datos: '
      if (errors.rol) msg += `Rol - ${errors.rol.join(' ')} `
      if (errors.contrasena) msg += `Contraseña - ${errors.contrasena.join(' ')} `
      if (errors.contrasena_actual) msg += `Contraseña actual - ${errors.contrasena_actual.join(' ')} `
      if (errors.dni) msg += `DNI - ${errors.dni.join(' ')} `
      if (errors.correo) msg += `Correo - ${errors.correo.join(' ')} `
      errorMessage.value = msg
    } else {
      errorMessage.value = 'No se pudo actualizar el usuario'
    }
    console.error(err)
  }
}

onMounted(() => cargarUsuario())
</script>


<style scoped>
.user-form {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40px 20px;
  background: transparent;
}

.form-card {
  background: rgba(23, 23, 23, 0.8);
  border: 2px solid #374151;
  border-radius: 20px;
  padding: 50px;
  width: 100%;
  max-width: 950px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #6b7280, #9ca3af, #6b7280);
  border-radius: 20px 20px 0 0;
}

.form-header {
  text-align: center;
  margin-bottom: 50px;
}

.form-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 12px;
}

.form-header p {
  color: #d1d5db;
  font-size: 1.1rem;
  font-weight: 500;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28px;
}

.input-group {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.full-width {
  grid-column: 1 / -1;
}

label {
  color: #f3f4f6;
  font-weight: 600;
  font-size: 0.95rem;
  margin-left: 5px;
}

.required {
  color: #ef4444;
  font-weight: 700;
}

input, select {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #4b5563 !important;
  border-radius: 20px !important;
  background: rgba(255, 255, 255, 0.05) !important;
  color: #ffffff !important;
  font-size: 1rem;
  font-weight: 500;
  font-family: inherit;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

input::placeholder {
  color: #9ca3af !important;
  font-weight: 400;
}

input:focus, select:focus {
  outline: none !important;
  border-color: #6b7280 !important;
  background: rgba(255, 255, 255, 0.08) !important;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.2) !important;
  transform: translateY(-2px);
}

.input-decoration {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #9ca3af;
  border-radius: 0 0 20px 20px;
  transition: width 0.3s ease;
}

input:focus ~ .input-decoration {
  width: 90%;
}

select {
  appearance: none;
  cursor: pointer;
  padding-right: 50px;
  border-radius: 20px !important;
}

.select-arrow {
  position: absolute;
  right: 20px;
  bottom: 16px;
  color: #9ca3af;
  pointer-events: none;
  transition: transform 0.3s ease;
  font-size: 0.8rem;
}

select:focus ~ .select-arrow {
  transform: rotate(180deg);
  color: #d1d5db;
}

select option {
  background: #1f2937 !important;
  color: #ffffff !important;
  padding: 12px;
}

.error-message {
  color: #ef4444;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  margin-bottom: 15px;
}

.submit-btn {
  width: 100%;
  padding: 18px 32px;
  background: #374151;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
  margin-top: 10px;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.5s;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn:hover {
  transform: translateY(-3px);
  background: #4b5563;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
}

.submit-btn:active {
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.submit-btn:hover .btn-icon {
  transform: translateX(4px);
}

/* ======== MODO CLARO ======== */
body.light-mode .user-form {
  background: transparent;
}

body.light-mode .form-card {
  background: #ffffff;
  border: 2px solid #000000;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(0, 0, 0, 0.05) inset;
}

body.light-mode .form-card::before {
  background: linear-gradient(90deg, #000000, #333333, #000000);
}

body.light-mode .form-header h1 {
  color: #000000;
}

body.light-mode .form-header p {
  color: #666666;
}

body.light-mode label {
  color: #000000;
}

body.light-mode input,
body.light-mode select {
  background: #ffffff !important;
  border: 2px solid #d1d5db !important;
  color: #000000 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
}

body.light-mode input::placeholder {
  color: #9ca3af !important;
}

body.light-mode input:focus,
body.light-mode select:focus {
  border-color: #000000 !important;
  background: #ffffff !important;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1) !important;
}

body.light-mode .input-decoration {
  background: #000000;
}

body.light-mode select option {
  background: #ffffff !important;
  color: #000000 !important;
}

body.light-mode .select-arrow {
  color: #666666;
}

body.light-mode .submit-btn {
  background: #000000;
  color: #ffffff;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

body.light-mode .submit-btn:hover {
  background: #333333;
}

body.light-mode .error-message {
  color: #dc2626;
}

/* Responsive */
@media (max-width: 768px) {
  .form-card {
    padding: 35px 25px;
    margin: 20px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 22px;
  }
  
  .form-header h1 {
    font-size: 2rem;
  }
  
  .form-header p {
    font-size: 1rem;
  }
  
  input, select {
    padding: 14px 18px !important;
  }
}

@media (max-width: 480px) {
  .user-form {
    padding: 20px 15px;
  }
  
  .form-card {
    padding: 25px 20px;
    border-radius: 16px;
  }
  
  .form-header {
    margin-bottom: 35px;
  }
  
  .form-header h1 {
    font-size: 1.8rem;
  }
}
</style>