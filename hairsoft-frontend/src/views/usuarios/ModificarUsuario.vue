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

          <!-- Rol dinámico -->
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
            <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
            <button type="submit" class="submit-btn">
              <span class="btn-text">Actualizar Usuario</span>
              <span class="btn-icon">→</span>
            </button>
            <button type="button" @click="cancelar" class="cancel-btn">
              Cancelar
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import axios from 'axios'

// 🔹 DEFINIR PROPS Y EMITS
const props = defineProps({
  usuarioId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['usuario-actualizado', 'cancelar'])

const API_BASE = 'http://127.0.0.1:8000'

const roles = ref([])
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
const errorMessage = ref('')

// ✅ Cargar roles desde el backend
const cargarRoles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    roles.value = res.data.filter(r => r.activo === true)
  } catch (error) {
    console.error('Error al cargar roles:', error)
  }
}

// ✅ Cargar datos del usuario - MODIFICADO (usa props)
const cargarUsuario = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    const usuario = res.data.find(u => u.id == props.usuarioId) // 🔹 USA PROPS

    if (!usuario) {
      errorMessage.value = 'Usuario no encontrado'
      emit('cancelar') // 🔹 EMITIR EN LUGAR DE ROUTER
      return
    }

    form.value = {
      nombre: usuario.nombre || '',
      apellido: usuario.apellido || '',
      dni: usuario.dni || '',
      telefono: usuario.telefono || '',
      correo: usuario.correo || '',
      contrasena_actual: '',
      nueva_contrasena: '',
      rol_id: usuario.rol_id || '',
      estado: usuario.estado || 'ACTIVO'
    }
  } catch (error) {
    console.error('Error al cargar usuario:', error)
    errorMessage.value = 'Error al cargar los datos del usuario'
  }
}

// ✅ Validación simple (mantener igual)
const validarFormulario = () => {
  if (!form.value.nombre || !form.value.apellido || !form.value.dni || !form.value.correo || !form.value.rol_id) {
    errorMessage.value = 'Complete todos los campos obligatorios'
    return false
  }
  return true
}

// ✅ Actualizar usuario - MODIFICADO
const actualizarUsuario = async () => {
  if (!validarFormulario()) return

  try {
    // 🔹 Validación de administrador único
    const rolNombreSeleccionado = roles.value.find(r => r.id == form.value.rol_id)?.nombre?.toLowerCase()
    const usuariosRes = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    const hayOtroAdmin = usuariosRes.data.some(u => u.rol_nombre?.toLowerCase() === 'administrador' && u.id != props.usuarioId && u.estado === 'ACTIVO')

    if (rolNombreSeleccionado === 'administrador' && hayOtroAdmin) {
      errorMessage.value = 'Ya existe un administrador activo. No se puede asignar este rol.'
      return
    }

    const payload = {
      nombre: form.value.nombre,
      apellido: form.value.apellido,
      dni: form.value.dni,
      telefono: form.value.telefono || '',
      correo: form.value.correo,
      rol: form.value.rol_id,
      estado: form.value.estado,
      contrasena: form.value.nueva_contrasena || ''
    }

    if (form.value.nueva_contrasena && form.value.contrasena_actual) {
      payload.contrasena_actual = form.value.contrasena_actual
    }

    await axios.post(`${API_BASE}/usuarios/api/usuarios/editar/${props.usuarioId}/`, payload) // 🔹 USA PROPS
    alert('✅ Usuario actualizado con éxito')
    emit('usuario-actualizado') // 🔹 EMITIR EN LUGAR DE ROUTER
  } catch (err) {
    console.error('Error al actualizar usuario:', err)
    errorMessage.value = 'Error al actualizar el usuario'
  }
}

// 🔹 Cancelar edición
const cancelar = () => {
  emit('cancelar')
}

onMounted(async () => {
  await cargarRoles()
  await cargarUsuario()
})
</script>

<style scoped>
/* MANTENER TODOS TUS ESTILOS ACTUALES (los que ya tienen en el style) */
.cancel-btn {
  width: 100%;
  padding: 18px 32px;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 10px;
}

.cancel-btn:hover {
  background: #4b5563;
}
</style>