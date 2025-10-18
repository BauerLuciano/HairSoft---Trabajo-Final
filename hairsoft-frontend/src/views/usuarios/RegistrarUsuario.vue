<template>
  <div class="user-form">
    <div class="form-card">
      <div class="form-header">
        <h1>Registrar Usuario</h1>
        <p>Completa los datos del usuario</p>
      </div>

      <form @submit.prevent="crearUsuario" class="form">
        <div class="form-grid">
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
            <div class="input-decoration"></div>
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
            <div class="input-decoration"></div>
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
            <div class="input-decoration"></div>
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
            <div class="input-decoration"></div>
          </div>

          <!-- Correo -->
          <div class="input-group">
            <label>Correo <span class="required">*</span></label>
            <input 
              v-model="form.correo" 
              type="email" 
              placeholder="Ingrese el correo electrónico" 
              required 
              @input="validarCorreo"
              @blur="mostrarErrorCorreo"
            />
            <div class="error-message" v-if="errores.correo">{{ errores.correo }}</div>
            <div class="input-decoration"></div>
          </div>

          <!-- Contraseña -->
          <div class="input-group">
            <label>Contraseña <span class="required">*</span></label>
            <input 
              v-model="form.contrasena" 
              type="password" 
              placeholder="Ingrese la contraseña" 
              required 
              @input="validarContrasena"
              @blur="mostrarErrorContrasena"
            />
            <div class="error-message" v-if="errores.contrasena">{{ errores.contrasena }}</div>
            <div class="input-decoration"></div>
          </div>

          <!-- Rol -->
          <div class="input-group">
            <label>Rol <span class="required">*</span></label>
            <select v-model="form.rol" required>
              <option value="">Seleccionar rol</option>
              <option value="ADMIN">Administrador</option>
              <option value="RECEPCIONISTA">Recepcionista</option>
              <option value="PELUQUERO">Peluquero</option>
              <option value="CLIENTE">Cliente</option>
            </select>
            <div class="select-arrow">▼</div>
          </div>

          <div class="full-width">
            <button type="submit" class="submit-btn">
              <span class="btn-text">Guardar Usuario</span>
              <span class="btn-icon">→</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const form = ref({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena: '',
  rol: ''
})

const usuarios = ref([])
const errores = reactive({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena: ''
})

// Expresiones regulares para validación
const regexSoloLetras = /^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$/
const regexSoloNumeros = /^\d+$/
const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const regexAlfanumerico = /^[A-Za-z0-9]+$/

// ... todas las funciones de validación y mostrar errores quedan igual ...

// Validación general antes de enviar
const validarFormulario = () => {
  let valido = true
  
  Object.keys(errores).forEach(key => { errores[key] = '' })
  
  if (!regexSoloLetras.test(form.value.nombre)) {
    errores.nombre = 'El nombre es requerido y solo puede contener letras'
    valido = false
  }
  
  if (!regexSoloLetras.test(form.value.apellido)) {
    errores.apellido = 'El apellido es requerido y solo puede contener letras'
    valido = false
  }
  
  if (!regexSoloNumeros.test(form.value.dni) || form.value.dni.length !== 8) {
    errores.dni = 'El DNI es requerido y debe tener 8 dígitos'
    valido = false
  }
  
  if (form.value.telefono && (!regexSoloNumeros.test(form.value.telefono) || form.value.telefono.length < 8)) {
    errores.telefono = 'El teléfono debe contener solo números y tener al menos 8 dígitos'
    valido = false
  }
  
  if (!regexEmail.test(form.value.correo)) {
    errores.correo = 'Ingrese un correo electrónico válido'
    valido = false
  }
  
  if (!regexAlfanumerico.test(form.value.contrasena) || form.value.contrasena.length < 6) {
    errores.contrasena = 'La contraseña debe tener al menos 6 caracteres alfanuméricos'
    valido = false
  }
  
  return valido
}

onMounted(async () => {
  await cargarUsuarios()
})

const cargarUsuarios = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    usuarios.value = res.data
  } catch (error) {
    console.error('Error al cargar usuarios:', error)
  }
}

// === Mapeo de roles ===
const rolMap = {
  ADMIN: 'ADMINISTRADOR',
  REC: 'RECEPCIONISTA',
  PEL: 'PELUQUERO',
  CLI: 'CLIENTE'
}

const crearUsuario = async () => {
  if (!validarFormulario()) {
    alert('❌ Por favor corrige los errores en el formulario')
    return
  }

  // Verificar que no haya más de un administrador
  if (form.value.rol === 'ADMIN') {
    await cargarUsuarios()
    
    const administradoresExistentes = usuarios.value.filter(usuario => {
      const rol = usuario.rol ? usuario.rol.toString().toUpperCase() : ''
      return rol === 'ADMIN' || rol === 'ADMINISTRADOR'
    })

    if (administradoresExistentes.length > 0) {
      alert(`❌ Ya existen ${administradoresExistentes.length} administrador(es) en el sistema. No se puede crear otro.`)
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
      rol: rolMap[form.value.rol] || form.value.rol, // ⚡ corrección clave
      estado: 'ACTIVO'
    }

    console.log('📤 Enviando datos:', payload)

    await axios.post(`${API_BASE}/usuarios/api/usuarios/crear/`, payload)
    alert('✅ Usuario registrado con éxito')
    
    window.location.href = '/usuarios'
    
  } catch (err) {
    console.error('❌ Error completo:', err)
    console.error('📊 Status:', err.response?.status)
    console.error('📝 Data de error:', JSON.stringify(err.response?.data, null, 2))
    
    if (err.response?.status === 400) {
      const errors = err.response.data
      if (errors.correo) {
        alert('❌ El correo ya está registrado.')
      } else if (errors.dni) {
        alert('❌ El DNI ya está registrado.')
      } else {
        let errorMsg = '❌ Errores:\n'
        Object.entries(errors).forEach(([campo, mensajes]) => {
          errorMsg += `• ${campo}: ${Array.isArray(mensajes) ? mensajes.join(', ') : mensajes}\n`
        })
        alert(errorMsg)
      }
    } else {
      alert('❌ Error: ' + (err.response?.data?.message || err.message))
    }
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