<template>
  <div class="user-form">
    <div class="form-card">
      <div class="form-header">
        <h1>Registrar Usuario</h1>
        <p>Completa los datos del usuario</p>
      </div>

      <form @submit.prevent="crearUsuario" class="form-grid" autocomplete="off">
        <!-- Nombre -->
        <div class="input-group">
          <label>Nombre <span class="required">*</span></label>
          <input 
            v-model="form.nombre" 
            type="text" 
            placeholder="Ingrese el nombre" 
            required 
            @blur="validarNombre"
            :class="{ 'campo-invalido': errores.nombre }"
          />
          <div class="error-message" v-if="errores.nombre">{{ errores.nombre }}</div>
        </div>

        <!-- Apellido -->
        <div class="input-group">
          <label>Apellido <span class="required">*</span></label>
          <input 
            v-model="form.apellido" 
            type="text" 
            placeholder="Ingrese el apellido" 
            required 
            @blur="validarApellido"
            :class="{ 'campo-invalido': errores.apellido }"
          />
          <div class="error-message" v-if="errores.apellido">{{ errores.apellido }}</div>
        </div>

        <!-- DNI -->
        <div class="input-group">
          <label>DNI <span class="required">*</span></label>
          <input 
            v-model="form.dni" 
            type="text" 
            placeholder="Ingrese el DNI" 
            required 
            @blur="validarDNI"
            maxlength="8"
            :class="{ 'campo-invalido': errores.dni }"
          />
          <div class="error-message" v-if="errores.dni">{{ errores.dni }}</div>
        </div>

        <!-- Teléfono -->
        <div class="input-group">
          <label>Teléfono</label>
          <input 
            v-model="form.telefono" 
            type="text" 
            placeholder="Ingrese el teléfono" 
            @blur="validarTelefono"
            maxlength="15"
            :class="{ 'campo-invalido': errores.telefono }"
          />
          <div class="error-message" v-if="errores.telefono">{{ errores.telefono }}</div>
        </div>

        <!-- Correo -->
        <div class="input-group">
          <label>Correo <span class="required">*</span></label>
          <input 
            v-model="form.correo" 
            type="email" 
            placeholder="Ingrese el correo electrónico" 
            required 
            autocomplete="off"
            @blur="validarCorreo"
            :class="{ 'campo-invalido': errores.correo }"
          />
          <div class="error-message" v-if="errores.correo">{{ errores.correo }}</div>
        </div>

        <!-- Contraseña -->
        <div class="input-group">
          <label>Contraseña <span class="required">*</span></label>
          <input 
            v-model="form.contrasena" 
            type="password" 
            placeholder="Ingrese la contraseña" 
            required 
            autocomplete="new-password"
            @blur="validarContrasena"
            :class="{ 'campo-invalido': errores.contrasena }"
          />
          <div class="error-message" v-if="errores.contrasena">{{ errores.contrasena }}</div>
        </div>

        <!-- Confirmar Contraseña -->
        <div class="input-group">
          <label>Confirmar Contraseña <span class="required">*</span></label>
          <input 
            v-model="form.confirmarContrasena" 
            type="password" 
            placeholder="Confirme la contraseña" 
            required 
            autocomplete="new-password"
            @blur="validarConfirmarContrasena"
            :class="{ 'campo-invalido': errores.confirmarContrasena }"
          />
          <div class="error-message" v-if="errores.confirmarContrasena">{{ errores.confirmarContrasena }}</div>
        </div>

        <!-- Rol -->
        <div class="input-group">
          <label>Rol <span class="required">*</span></label>
          <select 
            v-model="form.rol_id" 
            required 
            @blur="validarRol"
            :class="{ 'campo-invalido': errores.rol_id }"
          >
            <option value="">Seleccionar rol</option>
            <option v-for="rol in roles" :key="rol.id" :value="rol.id">
              {{ rol.nombre }}
            </option>
          </select>
          <div class="select-arrow">▼</div>
          <div class="error-message" v-if="errores.rol_id">{{ errores.rol_id }}</div>
        </div>

        <div class="full-width">
          <button type="submit" class="submit-btn">
            <span class="btn-text">Guardar Usuario</span>
            <span class="btn-icon">→</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

// 📌 API
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// 📌 Props y eventos
const emit = defineEmits(['usuario-registrado'])

// 📌 Formulario
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

// 📌 Errores por campo
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

// 📌 Roles y usuarios existentes
const roles = ref([])
const usuarios = ref([])

// 🔹 Cargar usuarios existentes
const cargarUsuarios = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    usuarios.value = res.data
  } catch (error) {
    console.error('Error al cargar usuarios:', error)
  }
}

// 🔹 Cargar roles activos
const cargarRoles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    roles.value = (res.data || []).filter(r => r.activo === true || r.activo === undefined)
  } catch (error) {
    console.error('Error al cargar roles:', error)
  }
}

onMounted(async () => {
  await cargarUsuarios()
  await cargarRoles()
})

// ------------------------------
// VALIDACIONES POR CAMPO (SOLO EN BLUR)
// ------------------------------
const validarNombre = () => {
  const valor = form.value.nombre.trim()
  if (!valor) {
    errores.value.nombre = "El nombre es obligatorio"
  } else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(valor)) {
    errores.value.nombre = "El nombre solo puede contener letras y tener 2-50 caracteres"
  } else {
    errores.value.nombre = ""
  }
}

const validarApellido = () => {
  const valor = form.value.apellido.trim()
  if (!valor) {
    errores.value.apellido = "El apellido es obligatorio"
  } else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(valor)) {
    errores.value.apellido = "El apellido solo puede contener letras y tener 2-50 caracteres"
  } else {
    errores.value.apellido = ""
  }
}

const validarDNI = () => {
  const dni = form.value.dni.trim()
  if (!dni) {
    errores.value.dni = "El DNI es obligatorio"
  } else if (!/^\d{7,8}$/.test(dni)) {
    errores.value.dni = "DNI inválido (solo números, 7-8 dígitos)"
  } else {
    errores.value.dni = ""
  }
}

const validarTelefono = () => {
  const telefono = form.value.telefono.trim()
  if (telefono && !/^\+?[\d\s\-\(\)]{6,15}$/.test(telefono)) {
    errores.value.telefono = "Número inválido (solo números y caracteres especiales, 6-15 dígitos)"
  } else {
    errores.value.telefono = ""
  }
}

const validarCorreo = () => {
  const correo = form.value.correo.trim()
  if (!correo) {
    errores.value.correo = "El correo es obligatorio"
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
    errores.value.correo = "Correo inválido"
  } else {
    errores.value.correo = ""
  }
}

const validarContrasena = () => {
  const contrasena = form.value.contrasena
  if (!contrasena) {
    errores.value.contrasena = "La contraseña es obligatoria"
  } else if (contrasena.length < 6) {
    errores.value.contrasena = "Debe tener al menos 6 caracteres"
  } else if (!/(?=.*[A-Z])(?=.*\d)/.test(contrasena)) {
    errores.value.contrasena = "Debe contener al menos una mayúscula y un número"
  } else {
    errores.value.contrasena = ""
  }
  
  // Si hay confirmación, validar que coincidan
  if (form.value.confirmarContrasena) {
    validarConfirmarContrasena()
  }
}

const validarConfirmarContrasena = () => {
  const confirmacion = form.value.confirmarContrasena
  if (!confirmacion) {
    errores.value.confirmarContrasena = "Confirmar contraseña es obligatorio"
  } else if (confirmacion !== form.value.contrasena) {
    errores.value.confirmarContrasena = "Las contraseñas no coinciden"
  } else {
    errores.value.confirmarContrasena = ""
  }
}

const validarRol = () => {
  if (!form.value.rol_id) {
    errores.value.rol_id = 'Selecciona un rol'
  } else {
    errores.value.rol_id = ''
  }
}

// ----------------------------------
// VALIDACIÓN DE FORMULARIO COMPLETO
// ----------------------------------
const validarFormulario = () => {
  console.log("🟢 Ejecutando validarFormulario()")

  // Validar todos los campos antes de enviar
  validarNombre()
  validarApellido()
  validarDNI()
  validarTelefono()
  validarCorreo()
  validarContrasena()
  validarConfirmarContrasena()
  validarRol()

  // Verificar si hay algún error
  let valido = true
  Object.keys(errores.value).forEach(k => {
    if (errores.value[k]) valido = false
  })

  return valido
}

// ----------------------------------
// CREAR USUARIO
// ----------------------------------
const crearUsuario = async () => {
  console.log("✅ crearUsuario ejecutado")

  if (!validarFormulario()) {
    Swal.fire({
      icon: 'error',
      title: 'Formulario inválido',
      text: 'Por favor corrige los errores en el formulario',
      confirmButtonColor: '#0ea5e9',
      background: '#1e293b',
      color: '#f1f5f9'
    })
    return
  }

  const rolSeleccionado = roles.value.find(r => r.id == form.value.rol_id)
  if (!rolSeleccionado) {
    Swal.fire({
      icon: 'error',
      title: 'Rol no válido',
      text: 'Por favor selecciona un rol válido',
      confirmButtonColor: '#0ea5e9',
      background: '#1e293b',
      color: '#f1f5f9'
    })
    return
  }

  // 🔹 Verificar si ya existe un administrador activo
  if (rolSeleccionado.nombre?.toLowerCase() === 'administrador') {
    const hayAdminActivo = usuarios.value.some(u => 
      u.rol_nombre?.toLowerCase() === 'administrador' && u.estado === 'ACTIVO'
    )
    if (hayAdminActivo) {
      Swal.fire({
        icon: 'warning',
        title: 'Administrador existente',
        text: 'Ya existe un usuario Administrador activo. No se puede crear otro.',
        confirmButtonColor: '#0ea5e9',
        background: '#1e293b',
        color: '#f1f5f9'
      })
      return
    }
  }

  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      apellido: form.value.apellido.trim(),
      dni: form.value.dni.trim(),
      telefono: form.value.telefono.trim() || '',
      correo: form.value.correo.trim(),
      contrasena: form.value.contrasena,
      rol: form.value.rol_id,
      estado: 'ACTIVO'
    }

    console.log("📤 Enviando datos al backend:", payload)
    const res = await axios.post(`${API_BASE}/usuarios/api/usuarios/crear/`, payload)

    Swal.fire({
      icon: 'success',
      title: 'Usuario registrado',
      text: 'El usuario se creó correctamente',
      confirmButtonColor: '#0ea5e9',
      background: '#1e293b',
      color: '#f1f5f9'
    })

    // Limpiar formulario
    resetForm()

    // Emitir evento para que el padre refresque la lista y cierre modal
    emit('usuario-registrado', res.data)

  } catch (err) {
    console.error('❌ Error en crearUsuario:', err.response?.data || err)
    
    let errorMessage = 'Ocurrió un error inesperado.'
    if (err.response?.data) {
      if (typeof err.response.data === 'string') {
        errorMessage = err.response.data
      } else if (err.response.data.message) {
        errorMessage = err.response.data.message
      } else if (err.response.data.error) {
        errorMessage = err.response.data.error
      } else if (typeof err.response.data === 'object') {
        errorMessage = Object.values(err.response.data).flat().join(', ')
      }
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Error al crear usuario',
      text: errorMessage,
      confirmButtonColor: '#0ea5e9',
      background: '#1e293b',
      color: '#f1f5f9'
    })
  }
}

// ------------------------------
// RESET
// ------------------------------
const resetForm = () => {
  form.value = {
    nombre: '',
    apellido: '',
    dni: '',
    telefono: '',
    correo: '',
    contrasena: '',
    confirmarContrasena: '',
    rol_id: ''
  }

  errores.value = {
    nombre: '',
    apellido: '',
    dni: '',
    telefono: '',
    correo: '',
    contrasena: '',
    confirmarContrasena: '',
    rol_id: ''
  }
}
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - FORMULARIO USUARIO
   ======================================== */

:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;
  --accent-color: #0ea5e9;
  --accent-light: rgba(14, 165, 233, 0.1);
  --border-color: #334155;
  --hover-bg: #2d3748;
  --error-color: #ef4444;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
}


/* Tarjeta del formulario */
.form-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 900px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
  border: 1px solid var(--border-color);
}

/* Borde superior azul acero */
.form-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* Header del formulario */
.form-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 25px;
  border-bottom: 2px solid var(--border-color);
}

.form-header h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.form-header p {
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.5px;
  font-size: 1rem;
}

/* Grid del formulario */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 25px;
}

.full-width {
  grid-column: 1 / -1;
}

/* Grupos de entrada */
.input-group {
  display: flex;
  flex-direction: column;
  position: relative;
}

.input-group label {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.required {
  color: var(--error-color);
  font-size: 1.2rem;
}

/* Campos de entrada */
.input-group input,
.input-group select {
  padding: 14px 16px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
  width: 100%;
}

.input-group input:focus,
.input-group select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

.input-group input::placeholder {
  color: var(--text-tertiary);
}

/* Estilos específicos para select */
.input-group select {
  appearance: none;
  cursor: pointer;
  padding-right: 40px;
}

.select-arrow {
  position: absolute;
  right: 16px;
  bottom: 16px;
  pointer-events: none;
  color: var(--text-tertiary);
  font-size: 0.8rem;
  transform: translateY(-50%);
}

/* Campos inválidos */
.campo-invalido {
  border-color: var(--error-color) !important;
  background: rgba(239, 68, 68, 0.05) !important;
}

.campo-invalido:focus {
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.2) !important;
}

/* Mensajes de error */
.error-message {
  color: var(--error-color);
  font-size: 0.8rem;
  margin-top: 6px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  min-height: 20px;
}

/* Botón de submit */
.submit-btn {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 18px 32px;
  border-radius: 12px;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-size: 1rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  margin-top: 10px;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

.btn-text {
  font-size: 1rem;
  font-weight: 900;
}

.btn-icon {
  font-size: 1.2rem;
  font-weight: 900;
  transition: transform 0.3s ease;
}

.submit-btn:hover .btn-icon {
  transform: translateX(5px);
}

/* Responsive */
@media (max-width: 768px) {
  .form-card {
    padding: 25px;
    border-radius: 20px;
    margin: 15px;
  }
  
  .form-header h1 {
    font-size: 1.8rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .submit-btn {
    padding: 16px 24px;
    font-size: 0.95rem;
  }
}

@media (max-width: 480px) {
  .form-card {
    padding: 20px;
    border-radius: 16px;
  }
  
  .form-header h1 {
    font-size: 1.5rem;
  }
  
  .form-header p {
    font-size: 0.9rem;
  }
  
  .input-group input,
  .input-group select {
    padding: 12px 14px;
    font-size: 0.9rem;
  }
  
  .submit-btn {
    padding: 14px 20px;
    font-size: 0.9rem;
  }
}

/* Estados de validación visual */
.input-group input:valid:not(:focus):not(:placeholder-shown):not(.campo-invalido),
.input-group select:valid:not(:focus):not(.campo-invalido) {
  border-color: var(--success-color);
  background: rgba(16, 185, 129, 0.05);
}
</style>