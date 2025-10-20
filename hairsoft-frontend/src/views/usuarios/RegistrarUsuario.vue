<template>
  <div class="user-form">
    <div class="form-card">
      <div class="form-header">
        <h1>Registrar Usuario</h1>
        <p>Completa los datos del usuario</p>
      </div>

      <form @submit.prevent="crearUsuario" class="form-grid">
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
  rol_id: ''
})

const usuarios = ref([])
const roles = ref([])
const errores = reactive({
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  correo: '',
  contrasena: ''
})

const cargarUsuarios = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    usuarios.value = res.data
  } catch (error) {
    console.error('Error al cargar usuarios:', error)
  }
}

const cargarRoles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    roles.value = res.data.filter(r => r.activo === true)
  } catch (error) {
    console.error('Error al cargar roles:', error)
  }
}

onMounted(async () => {
  await cargarUsuarios()
  await cargarRoles()
})

const validarFormulario = () => {
  console.log("🟢 Ejecutando validarFormulario()")
  return true
}

const crearUsuario = async () => {
  console.log("✅ crearUsuario ejecutado")

  if (!validarFormulario()) {
    alert('❌ Por favor corrige los errores en el formulario')
    return
  }

  // Buscar el rol seleccionado
  const rolNombre = roles.value.find(r => r.id == form.value.rol_id)?.nombre
  if (!rolNombre) {
    alert('❌ Por favor selecciona un rol válido')
    return
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
    await axios.post(`${API_BASE}/usuarios/api/usuarios/crear/`, payload)

    alert('✅ Usuario registrado con éxito')

    // Resetear formulario
    form.value = { nombre: '', apellido: '', dni: '', telefono: '', correo: '', contrasena: '', rol_id: '' }

    // Redirigir al listado de usuarios
    router.push({ name: 'ListadoUsuarios' })  // 🔹 Usamos el nombre de la ruta

  } catch (err) {
    console.error('❌ Error en crearUsuario:', err.response?.data || err)
    alert('Error al crear usuario:\n' + JSON.stringify(err.response?.data?.errors || err.response?.data || err))
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