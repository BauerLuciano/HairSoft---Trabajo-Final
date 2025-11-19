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
            @input="validarNombre"
            @blur="mostrarErrorNombre"
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
            @input="validarApellido"
            @blur="mostrarErrorApellido"
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
            @input="validarDNI"
            @blur="mostrarErrorDNI"
            maxlength="8"
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
            @input="validarTelefono"
            @blur="mostrarErrorTelefono"
            maxlength="15"
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
            @input="validarCorreo"
            @blur="mostrarErrorCorreo"
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
            @input="validarContrasena"
            @blur="mostrarErrorContrasena"
          />
          <div class="error-message" v-if="errores.contrasena">{{ errores.contrasena }}</div>
        </div>

        <!-- Rol -->
        <div class="input-group">
          <label>Rol <span class="required">*</span></label>
          <select v-model="form.rol_id" required>
            <option value="">Seleccionar rol</option>
            <option v-for="rol in roles" :key="rol.id" :value="rol.id">
              {{ rol.nombre }}
            </option>
          </select>
          <div class="select-arrow">▼</div>
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
  rol_id: ''
})

// 📌 Roles y usuarios existentes
const roles = ref([])
const usuarios = ref([])

// 🔹 Cargar usuarios existentes (sólo para checks internos, dejalo si lo usás)
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
// VALIDACIONES POR CAMPO (AGREGADAS SIN BORRAR NINGUNA LÍNEA DEL TEMPLATE)
// ------------------------------
const validarNombre = () => {
  if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}$/.test(form.value.nombre)) {
    errores.value.nombre = "El nombre solo puede contener letras y tener 2-50 caracteres"
  } else {
    errores.value.nombre = ""
  }
}

const mostrarErrorNombre = () => {
  if (!form.value.nombre) errores.value.nombre = "El nombre es obligatorio"
}

const validarApellido = () => {
  if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}$/.test(form.value.apellido)) {
    errores.value.apellido = "El apellido solo puede contener letras y tener 2-50 caracteres"
  } else {
    errores.value.apellido = ""
  }
}

const mostrarErrorApellido = () => {
  if (!form.value.apellido) errores.value.apellido = "El apellido es obligatorio"
}

const validarDNI = () => {
  // aceptamos 7-9 números (pero el input tiene maxlength=8 según template; mantenemos chequeo 7-10 por flexibilidad)
  if (!/^\d{7,10}$/.test(form.value.dni)) {
    errores.value.dni = "DNI inválido (solo números, 7-10 dígitos)"
  } else {
    errores.value.dni = ""
  }
}

const mostrarErrorDNI = () => {
  if (!form.value.dni) errores.value.dni = "El DNI es obligatorio"
}

const validarTelefono = () => {
  if (form.value.telefono && !/^\+?\d{6,15}$/.test(form.value.telefono)) {
    errores.value.telefono = "Número inválido (solo números y opcional +, 6-15 dígitos)"
  } else {
    errores.value.telefono = ""
  }
}

const mostrarErrorTelefono = () => {
  if (form.value.telefono && !/^\+?\d{6,15}$/.test(form.value.telefono)) {
    errores.value.telefono = "Teléfono inválido"
  }
}

const validarCorreo = () => {
  if (!/\S+@\S+\.\S+/.test(form.value.correo)) {
    errores.value.correo = "Correo inválido"
  } else {
    errores.value.correo = ""
  }
}

const mostrarErrorCorreo = () => {
  if (!form.value.correo) errores.value.correo = "El correo es obligatorio"
}

const validarContrasena = () => {
  if (!form.value.contrasena || form.value.contrasena.length < 6) {
    errores.value.contrasena = "Debe tener al menos 6 caracteres"
  } else {
    errores.value.contrasena = ""
  }
}

const mostrarErrorContrasena = () => {
  if (!form.value.contrasena) errores.value.contrasena = "La contraseña es obligatoria"
}

// ----------------------------------
// VALIDACIÓN DE FORMULARIO (USADA ANTES DE ENVIAR)
// ----------------------------------
const validarFormulario = () => {
  console.log("🟢 Ejecutando validarFormulario()")

  // reset
  errores.value = {
    nombre: '',
    apellido: '',
    dni: '',
    telefono: '',
    correo: '',
    contrasena: '',
    rol_id: ''
  }

  let valido = true

  // reutilizamos las validaciones por campo para llenar errores
  validarNombre()
  validarApellido()
  validarDNI()
  validarTelefono()
  validarCorreo()
  validarContrasena()

  if (!form.value.rol_id) {
    errores.value.rol_id = 'Selecciona un rol.'
    valido = false
  }

  // si algún mensaje quedó, marcar inválido
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
      text: 'Por favor corrige los errores en el formulario'
    })
    return
  }

  const rolSeleccionado = roles.value.find(r => r.id == form.value.rol_id)
  if (!rolSeleccionado) {
    Swal.fire({
      icon: 'error',
      title: 'Rol no válido',
      text: 'Por favor selecciona un rol válido'
    })
    return
  }

  // 🔹 Verificar si ya existe un administrador activo
  if (rolSeleccionado.nombre?.toLowerCase() === 'administrador') {
    const hayAdminActivo = usuarios.value.some(u => u.rol_nombre?.toLowerCase() === 'administrador' && u.estado === 'ACTIVO')
    if (hayAdminActivo) {
      Swal.fire({
        icon: 'warning',
        title: 'Administrador existente',
        text: 'Ya existe un usuario Administrador activo. No se puede crear otro.'
      })
      return
    }
  }

  try {
    const payload = {
      nombre: form.value.nombre,
      apellido: form.value.apellido,
      dni: form.value.dni,
      telefono: form.value.telefono || '',
      correo: form.value.correo,
      contrasena: form.value.contrasena,
      rol: form.value.rol_id,
      estado: 'ACTIVO'
    }

    console.log("📤 Enviando datos al backend:", payload)
    const res = await axios.post(`${API_BASE}/usuarios/api/usuarios/crear/`, payload)

    Swal.fire({
      icon: 'success',
      title: 'Usuario registrado',
      text: 'El usuario se creó correctamente'
    })

    // Limpiar formulario
    resetForm()

    // Emitir evento para que el padre refresque la lista y cierre modal
    emit('usuario-registrado', res.data)

  } catch (err) {
    console.error('❌ Error en crearUsuario:', err.response?.data || err)
    Swal.fire({
      icon: 'error',
      title: 'Error al crear usuario',
      text: err.response?.data?.message || JSON.stringify(err.response?.data) || 'Ocurrió un error inesperado.'
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
    rol_id: ''
  }

  errores.value = {
    nombre: '',
    apellido: '',
    dni: '',
    telefono: '',
    correo: '',
    contrasena: '',
    rol_id: ''
  }
}
</script>



<style scoped>
/* =============================
   ESTILOS EXCLUSIVOS DEL FORMULARIO
============================= */
.user-form { display: flex; justify-content: center; align-items: center; }

.form-card {
  background: rgba(23, 23, 23, 0.8);
  border: 2px solid #374151;
  border-radius: 20px;
  padding: 50px;
  max-width: 950px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05) inset;
  backdrop-filter: blur(10px);
  position: relative;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #6b7280, #9ca3af, #6b7280);
  border-radius: 20px 20px 0 0;
}

.form-header { text-align: center; margin-bottom: 50px; }
.form-header h1 { font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 12px; }
.form-header p { color: #d1d5db; font-size: 1.1rem; font-weight: 500; }

/* efectos exclusivos de botones, flechas y decoraciones */
.input-decoration, .select-arrow, .submit-btn, .btn-icon {}

/* Responsive exclusivo del formulario */
@media (max-width: 768px) {
  .form-card { padding: 35px 25px; }
  .form-grid { grid-template-columns: 1fr; }
  .form-header h1 { font-size: 2rem; }
  .form-header p { font-size: 1rem; }
}

@media (max-width: 480px) {
  .form-card { padding: 25px 20px; border-radius: 16px; }
  .form-header { margin-bottom: 35px; }
  .form-header h1 { font-size: 1.8rem; }
}
</style>