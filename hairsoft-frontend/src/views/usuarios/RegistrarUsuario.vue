<template>
  <div class="modern-form">
    <!-- 🎯 NOTA DE CONTEXTO CUANDO VENIMOS DE TURNOS -->
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
      
      <!-- Primera fila -->
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

      <!-- Segunda fila -->
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
            <span class="optional-badge">Opcional</span>
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

      <!-- Correo -->
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
            @blur="validarCorreo"
            :class="{ 'error': errores.correo }"
          />
        </div>
        <div v-if="errores.correo" class="field-error">
          <span class="error-dot"></span>
          {{ errores.correo }}
        </div>
      </div>

      <!-- Contraseñas -->
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

      <!-- 🔥 CAMBIO IMPORTANTE: Si venimos de turnos, el rol ES FIJO = CLIENTE -->
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

      <!-- Botón -->
      <button type="submit" class="submit-button" :disabled="cargando">
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
import { ref, onMounted, watch } from 'vue'
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
const idRolCliente = ref(null) // 🎯 PARA GUARDAR EL ID DEL ROL CLIENTE

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
  // Solo detectar de dónde venimos, NO redirigir automáticamente
  vieneDeTurnos.value = route.query.returnTo === 'turnos'
  
  console.log("📌 Contexto:", vieneDeTurnos.value ? 'Desde Turnos Presenciales' : 'Registro Normal')
  
  await cargarUsuariosExistentes()
  await cargarRoles()
  
  // 🎯 IMPORTANTE: Buscar el rol CLIENTE si venimos de turnos
  if (vieneDeTurnos.value && !idRolCliente.value) {
    const rolCliente = roles.value.find(r => r.nombre.toLowerCase().includes('cliente'))
    if (rolCliente) {
      idRolCliente.value = rolCliente.id
      // 🟢 FORZAR EL ROL CLIENTE EN EL FORMULARIO
      form.value.rol_id = idRolCliente.value
    }
  }  
})

// Cargar roles
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
    
    console.log("📋 Roles cargados:", roles.value.length)
  } catch (error) {
    console.error('Error cargando roles:', error)
    if (error.response?.status === 401) {
      Swal.fire({
        icon: 'error',
        title: 'Sesión expirada',
        text: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
        background: '#1e293b',
        color: '#f1f5f9'
      })
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron cargar los roles',
        background: '#1e293b',
        color: '#f1f5f9'
      })
    }
  }
}

// Cargar usuarios existentes para validar duplicados
const cargarUsuariosExistentes = async () => {
  try {
    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    const res = await axios.get(`${API_BASE}/api/usuarios/`)
    usuariosExistentes.value = res.data
  } catch (error) {
    console.error('Error cargando usuarios existentes:', error)
  }
}

// Formateo y validaciones
const formatearDNI = () => {
  form.value.dni = form.value.dni.replace(/\D/g, '').slice(0, 8)
}

const formatearTelefono = () => {
  let tel = form.value.telefono.replace(/\D/g, '')
  
  if (tel.length === 0) {
    form.value.telefono = ''
    return
  }
  
  if (tel.startsWith('549')) {
    form.value.telefono = '+54 ' + tel.slice(2)
  } else if (tel.startsWith('54')) {
    form.value.telefono = '+54 ' + tel.slice(2)
  } else if (tel.startsWith('9')) {
    form.value.telefono = '+54 ' + tel
  } else {
    form.value.telefono = '+54 9' + tel
  }
  
  tel = form.value.telefono.replace(/\D/g, '')
  if (tel.length > 13) {
    tel = tel.slice(0, 13)
    const codigoPais = tel.slice(0, 2)
    const resto = tel.slice(2)
    form.value.telefono = `+${codigoPais} ${resto}`
  }
}

// Validar que no exista otro usuario con el mismo nombre y apellido
const validarNombreApellidoUnico = () => {
  const nombre = form.value.nombre.trim().toLowerCase()
  const apellido = form.value.apellido.trim().toLowerCase()
  
  if (!nombre || !apellido) return true
  
  const existeDuplicado = usuariosExistentes.value.some(usuario => {
    const usuarioNombre = usuario.nombre?.toLowerCase() || ''
    const usuarioApellido = usuario.apellido?.toLowerCase() || ''
    
    return usuarioNombre === nombre && usuarioApellido === apellido
  })
  
  return !existeDuplicado
}

// Validar que no exista otro usuario con el mismo DNI
const validarDNIUnico = () => {
  const dni = form.value.dni.trim()
  
  if (!dni) return true
  
  const existeDuplicado = usuariosExistentes.value.some(usuario => {
    return usuario.dni === dni
  })
  
  return !existeDuplicado
}

// Validar que no exista otro usuario con el mismo correo
const validarCorreoUnico = () => {
  const correo = form.value.correo.trim().toLowerCase()
  
  if (!correo) return true
  
  const existeDuplicado = usuariosExistentes.value.some(usuario => {
    const usuarioCorreo = usuario.correo?.toLowerCase() || ''
    return usuarioCorreo === correo
  })
  
  return !existeDuplicado
}

const validarNombre = () => {
  const val = form.value.nombre.trim()
  if (!val) {
    errores.value.nombre = 'El nombre es obligatorio'
  } else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val)) {
    errores.value.nombre = 'Solo letras (2-50 caracteres)'
  } else if (!validarNombreApellidoUnico()) {
    errores.value.nombre = 'Ya existe un usuario con este nombre y apellido'
  } else {
    errores.value.nombre = ''
  }
}

const validarApellido = () => {
  const val = form.value.apellido.trim()
  if (!val) {
    errores.value.apellido = 'El apellido es obligatorio'
  } else if (!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,50}$/.test(val)) {
    errores.value.apellido = 'Solo letras (2-50 caracteres)'
  } else if (!validarNombreApellidoUnico()) {
    errores.value.apellido = 'Ya existe un usuario con este nombre y apellido'
  } else {
    errores.value.apellido = ''
  }
}

const validarDNI = () => {
  const val = form.value.dni.trim()
  if (!val) {
    errores.value.dni = 'El DNI es obligatorio'
  } else if (!/^\d{7,8}$/.test(val)) {
    errores.value.dni = 'DNI inválido (7-8 dígitos)'
  } else if (!validarDNIUnico()) {
    errores.value.dni = 'Ya existe un usuario con este DNI'
  } else {
    errores.value.dni = ''
  }
}

const validarTelefono = () => {
  const val = form.value.telefono.trim()
  if (!val) {
    errores.value.telefono = ''
    return
  }

  const limpio = val.replace(/\s+/g, '')
  
  if (!/^\+54\s?9\d{10}$/.test(limpio)) {
    errores.value.telefono = 'Formato: +54 9 3755 558911'
  } else {
    errores.value.telefono = ''
  }
}

const validarCorreo = () => {
  const val = form.value.correo.trim()
  if (!val) {
    errores.value.correo = 'El correo es obligatorio'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
    errores.value.correo = 'Correo electrónico inválido'
  } else if (!validarCorreoUnico()) {
    errores.value.correo = 'Ya existe un usuario con este correo'
  } else {
    errores.value.correo = ''
  }
}

const validarContrasena = () => {
  const val = form.value.contrasena
  if (!val) {
    errores.value.contrasena = 'La contraseña es obligatoria'
  } else if (val.length < 6) {
    errores.value.contrasena = 'Mínimo 6 caracteres'
  } else if (!/(?=.*[A-Z])(?=.*\d)/.test(val)) {
    errores.value.contrasena = '1 mayúscula y 1 número'
  } else {
    errores.value.contrasena = ''
  }
  
  if (form.value.confirmarContrasena) {
    validarConfirmarContrasena()
  }
}

const validarConfirmarContrasena = () => {
  const val = form.value.confirmarContrasena
  if (!val) {
    errores.value.confirmarContrasena = 'Confirma la contraseña'
  } else if (val !== form.value.contrasena) {
    errores.value.confirmarContrasena = 'Las contraseñas no coinciden'
  } else {
    errores.value.confirmarContrasena = ''
  }
}

const validarRol = () => {
  if (!form.value.rol_id) {
    errores.value.rol_id = 'Selecciona un rol'
  } else {
    errores.value.rol_id = ''
  }
}

const validarFormulario = () => {
  validarNombre()
  validarApellido()
  validarDNI()
  validarTelefono()
  validarCorreo()
  validarContrasena()
  validarConfirmarContrasena()
  
  // Solo validar rol si NO venimos de turnos
  if (!vieneDeTurnos.value) {
    validarRol()
  }

  return !Object.values(errores.value).some(e => e !== '')
}

const crearUsuario = async () => {
  // Validar formulario primero
  if (!validarFormulario()) {
    Swal.fire({
      icon: 'error',
      title: 'Formulario incompleto',
      text: 'Por favor, completa todos los campos requeridos correctamente',
      background: '#1e293b',
      color: '#f1f5f9'
    })
    return
  }

  // 🔥 VALIDAR ADMINISTRADOR ÚNICO (solo para registros normales)
  if (!vieneDeTurnos.value) {
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
      const rolNombreSeleccionado = roles.value.find(r => r.id == form.value.rol_id)?.nombre?.toLowerCase()
      
      const usuariosRes = await axios.get(`${API_BASE}/api/usuarios/`)
      
      const hayOtroAdmin = usuariosRes.data.some(u => 
        u.rol_nombre?.toLowerCase() === 'administrador' && 
        u.estado === 'ACTIVO'
      )

      if (rolNombreSeleccionado === 'administrador' && hayOtroAdmin) {
        Swal.fire({
          icon: 'warning',
          title: 'Administrador existente',
          text: 'Ya existe un administrador activo. No se puede crear otro.',
          background: '#1e293b',
          color: '#f1f5f9'
        })
        return
      }
    } catch (error) {
      console.error('Error validando administrador:', error)
    }
  }

  cargando.value = true

  try {
    // Preparar el teléfono para el backend
    let telefonoParaBackend = null
    if (form.value.telefono.trim()) {
      let telLimpio = form.value.telefono.replace(/\s+/g, '').replace('+', '')
      
      if (!telLimpio.startsWith('549')) {
        if (telLimpio.startsWith('54')) {
          telLimpio = '549' + telLimpio.slice(2)
        } else if (telLimpio.startsWith('9')) {
          telLimpio = '54' + telLimpio
        } else {
          telLimpio = '549' + telLimpio
        }
      }
      
      if (telLimpio.length === 13) {
        telefonoParaBackend = '+' + telLimpio
      } else {
        errores.value.telefono = 'El teléfono debe tener 13 dígitos'
        throw new Error('Teléfono inválido')
      }
    }

    // 🎯 SI VENIMOS DE TURNOS, EL ROL ES FIJO = CLIENTE
    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    
    // Buscar el rol CLIENTE si venimos de turnos
    if (vieneDeTurnos.value && !idRolCliente.value) {
      const rolCliente = roles.value.find(r => r.nombre.toLowerCase().includes('cliente'))
      if (rolCliente) {
        idRolCliente.value = rolCliente.id
      } else {
        // Si no encuentra el rol CLIENTE, buscar alternativas
        console.warn('No se encontró rol CLIENTE, buscando alternativas...')
        const rolAlternativo = roles.value.find(r => 
          r.nombre.toLowerCase().includes('cliente') || 
          r.nombre.toLowerCase().includes('usuario')
        )
        if (rolAlternativo) {
          idRolCliente.value = rolAlternativo.id
        } else {
          throw new Error('No se encontró el rol CLIENTE en el sistema')
        }
      }
    }

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

    console.log('📤 Enviando al backend:', payload)

    const response = await axios.post(`${API_BASE}/api/usuarios/crear/`, payload)
    const nuevoUsuarioId = response.data.id

    console.log("✅ CLIENTE CREADO - ID:", nuevoUsuarioId)

    // 🎯 AQUÍ ESTÁ LA CLAVE CORREGIDA - DIFERENCIAR ENTRE VENIR DE TURNOS O NO
    if (vieneDeTurnos.value) {
      console.log("🔥 VENIMOS DE TURNOS - REDIRIGIENDO A TURNOS...")
      
      // Mostrar mensaje de éxito rápido
      await Swal.fire({
        icon: 'success',
        title: '¡Cliente Registrado!',
        text: 'Volviendo a turnos con el cliente seleccionado...',
        showConfirmButton: false,
        timer: 800,
        timerProgressBar: true,
        background: '#1e293b',
        color: '#f1f5f9'
      })
      
      // 🟢 CODIFICAR LOS NOMBRES PARA LA URL (usar + en lugar de %20 para espacios)
      const nombreCodificado = encodeURIComponent(form.value.nombre.trim())
      const apellidoCodificado = encodeURIComponent(form.value.apellido.trim())
      const nombreCompleto = `${nombreCodificado}+${apellidoCodificado}`
      
      console.log("📍 Redirigiendo a turnos con:", {
        id: nuevoUsuarioId,
        nombre: nombreCompleto
      })
      
      // 🟢 REDIRIGIR CON LOS PARÁMETROS CORRECTOS
      router.push({
        path: '/turnos/crear-presencial',
        query: {
          nuevo_cliente_id: nuevoUsuarioId,
          nuevo_cliente_nombre: nombreCompleto
        }
      })
      
    } else {
      // 🔥 CASO 2: REGISTRO NORMAL (NO desde turnos)
      Swal.fire({
        icon: 'success',
        title: 'Usuario creado',
        text: 'El usuario se ha registrado exitosamente',
        background: '#1e293b',
        color: '#f1f5f9'
      }).then(() => {
        // Limpiar formulario
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
        
        // Limpiar errores
        Object.keys(errores.value).forEach(key => {
          errores.value[key] = ''
        })
        
        // Resetear estados de contraseñas
        mostrarContrasena.value = false
        mostrarConfirmarContrasena.value = false
        
        // Recargar usuarios existentes
        cargarUsuariosExistentes()
      })
    }

  } catch (error) {
    console.error('❌ Error creando usuario:', error)
    
    let msg = 'Error al crear el usuario'
    
    if (error.response?.data?.error) {
      msg = error.response.data.error
    } else if (error.response?.data?.message) {
      msg = error.response.data.message
    } else if (error.message) {
      msg = error.message
    }
    
    // Manejar errores específicos de duplicados
    if (msg.toLowerCase().includes('dni') || msg.toLowerCase().includes('duplicado')) {
      errores.value.dni = 'Ya existe un usuario con este DNI'
    }
    
    if (msg.toLowerCase().includes('correo') || msg.toLowerCase().includes('email')) {
      errores.value.correo = 'Ya existe un usuario con este correo'
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: msg,
      background: '#1e293b',
      color: '#f1f5f9'
    })
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