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
            >
          </div>

          <div class="form-group">
            <label>Apellido</label>
            <input 
              type="text" 
              v-model="form.apellido" 
              placeholder="Tu apellido"
              required
            >
          </div>

          <div class="form-group">
            <label>DNI</label>
            <input 
              type="text" 
              v-model="form.dni" 
              placeholder="Tu número de documento"
              required
            >
          </div>

          <div class="form-group">
            <label>Correo Electrónico</label>
            <input 
              type="email" 
              v-model="form.correo" 
              placeholder="nombre@ejemplo.com"
              required
            >
          </div>

          <div class="form-group" style="grid-column: 1 / -1;">
            <label>Teléfono / Celular</label>
            <input 
              type="tel" 
              v-model="form.telefono" 
              placeholder="Ej: 3758 123456"
              autocomplete="tel"
              required
            >
          </div>
        </div>

        <div class="divider"></div>

        <h3 class="section-title">Seguridad</h3>
        <p class="help-text">Completá estos campos solo si querés cambiar tu contraseña.</p>

        <div class="form-grid">
          <div class="form-group">
            <label>Contraseña Actual</label>
            <input 
              type="password" 
              v-model="form.currentPassword" 
              placeholder="Escribí tu contraseña actual"
              autocomplete="new-password"
            >
          </div>

          <div class="form-group">
            <label>Nueva Contraseña</label>
            <input 
              type="password" 
              v-model="form.newPassword" 
              placeholder="Mínimo 8 caracteres"
              autocomplete="new-password"
            >
          </div>
        </div>

        <button type="submit" class="btn-guardar" :disabled="guardando">
          {{ guardando ? 'Guardando cambios...' : 'Guardar Cambios' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import Swal from 'sweetalert2';

const isProduction = window.location.hostname.includes('vercel.app') || window.location.hostname.includes('railway.app');
const DOMAIN = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://127.0.0.1:8000';

// Todo unificado en el estado del formulario
const form = ref({
  nombre: '',
  apellido: '',
  correo: '',
  dni: '',
  telefono: '',
  currentPassword: '',
  newPassword: ''
});

const cargando = ref(true);
const guardando = ref(false);

const cargarDatos = async () => {
  try {
    const userId = localStorage.getItem('user_id');
    const GET_URL = `${DOMAIN}/api/usuarios/${userId}/`;
    const response = await api.get(GET_URL);
    const data = response.data;

    // Asignamos todo al form para que sea editable
    form.value.nombre = data.nombre || '';
    form.value.apellido = data.apellido || '';
    form.value.correo = data.correo || '';
    form.value.dni = data.dni !== 'No registrado' ? data.dni : '';

    const tel = data.telefono || '';
    form.value.telefono = (tel === 'No registrado' || tel.includes('@')) ? '' : tel;

  } catch (error) {
    console.error("❌ Error cargando perfil:", error);
    Swal.fire('Error de conexión', 'No pudimos cargar tus datos.', 'error');
  } finally {
    cargando.value = false;
  }
};

const guardarCambios = async () => {
  if (form.value.newPassword && !form.value.currentPassword) {
    Swal.fire('Atención', 'Debés ingresar tu contraseña actual para poder cambiarla.', 'warning');
    return;
  }

  guardando.value = true;
  try {
    const userId = localStorage.getItem('user_id');
    const PATCH_URL = `${DOMAIN}/api/usuarios/editar/${userId}/`;
    
    // Enviamos TODOS los campos editables
    const payload = {
      nombre: form.value.nombre,
      apellido: form.value.apellido,
      dni: form.value.dni,
      correo: form.value.correo,
      telefono: form.value.telefono
    };

    if (form.value.newPassword) {
      payload.contrasena_nueva = form.value.newPassword;
      payload.contrasena_actual = form.value.currentPassword;
    }

    await api.patch(PATCH_URL, payload);

    Swal.fire({
      title: '¡Éxito!',
      text: 'Tus datos han sido actualizados.',
      icon: 'success',
      timer: 2000,
      showConfirmButton: false
    });
    
    // Limpiamos las contraseñas post-guardado
    form.value.currentPassword = '';
    form.value.newPassword = '';
    
  } catch (error) {
    console.error("❌ Error guardando perfil:", error);
    
    // Si meten un correo o DNI que ya existe, el backend te lo va a rechazar. Acá lo atajamos:
    let msg = 'Error del servidor al guardar los cambios.';
    if (error.response?.data) {
       if (error.response.data.correo) msg = 'Ese correo ya está en uso por otro usuario.';
       else if (error.response.data.dni) msg = 'Ese DNI ya está registrado en el sistema.';
       else if (error.response.data.error) msg = error.response.data.error;
       else if (error.response.data.message) msg = error.response.data.message;
    }

    Swal.fire('Error', msg, 'error');
  } finally {
    guardando.value = false;
  }
};

onMounted(() => {
  cargarDatos();
});
</script>

<style scoped>
/* CONTENEDOR PRINCIPAL */
.perfil-container { 
  max-width: 800px; 
  margin: 2rem auto; 
  padding: 0 1.5rem; 
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* HEADER */
.header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 2.5rem; 
}

.header h1 { 
  margin: 0; 
  color: var(--text-primary); 
  font-size: 2.2rem; 
  font-weight: 700;
  letter-spacing: -0.5px;
}

.btn-volver { 
  background: transparent; 
  border: 2px solid var(--border-color); 
  color: var(--text-secondary); 
  padding: 0.6rem 1.5rem; 
  border-radius: 8px; 
  font-weight: 600; 
  cursor: pointer; 
  transition: all 0.2s ease-in-out; 
}

.btn-volver:hover { 
  border-color: var(--text-primary); 
  color: var(--text-primary); 
  background-color: rgba(0, 0, 0, 0.02);
}

/* TARJETA DE PERFIL */
.perfil-card { 
  background: var(--bg-secondary); 
  padding: 3rem; 
  border-radius: 16px; 
  border: 1px solid rgba(0, 0, 0, 0.05); /* Borde sutil */
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1); /* Sombra elegante */
}

.section-title { 
  color: var(--accent-color); 
  margin: 0 0 1.2rem 0; 
  font-size: 1.25rem; 
  font-weight: 600; 
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.help-text { 
  font-size: 0.9rem; 
  color: var(--text-secondary); 
  margin-top: -0.8rem; 
  margin-bottom: 1.5rem; 
  opacity: 0.8;
}

/* FORMULARIO */
.form-grid { 
  display: grid; 
  gap: 1.8rem; 
}

.form-group { 
  display: flex; 
  flex-direction: column; 
}

.form-group label { 
  margin-bottom: 0.6rem; 
  color: var(--text-secondary); 
  font-weight: 600; 
  font-size: 0.9rem; 
}

input { 
  width: 100%; 
  padding: 0.9rem 1.2rem; 
  border-radius: 10px; 
  border: 1px solid var(--border-color); 
  background: var(--bg-primary); 
  color: var(--text-primary); 
  font-size: 1rem; 
  transition: all 0.3s ease; 
}

input:focus { 
  outline: none; 
  border-color: var(--accent-color); 
  box-shadow: 0 0 0 4px rgba(var(--accent-color-rgb, 0, 123, 255), 0.15); 
  background: #ffffff; /* Brillo extra al hacer foco */
}

input::placeholder {
  color: #a0aec0;
}

.divider { 
  height: 1px; 
  background: var(--border-color); 
  margin: 3rem 0; 
  opacity: 0.6; 
}

/* BOTÓN GUARDAR */
.btn-guardar { 
  width: 100%; 
  padding: 1.1rem; 
  background: var(--accent-color); 
  color: white; 
  border: none; 
  border-radius: 10px; 
  font-weight: 600; 
  font-size: 1.1rem; 
  cursor: pointer; 
  margin-top: 2.5rem; 
  transition: all 0.3s ease; 
  box-shadow: 0 4px 6px rgba(var(--accent-color-rgb, 0, 123, 255), 0.2);
}

.btn-guardar:hover:not(:disabled) { 
  transform: translateY(-2px); 
  box-shadow: 0 6px 12px rgba(var(--accent-color-rgb, 0, 123, 255), 0.3);
  filter: brightness(1.05);
}

.btn-guardar:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(var(--accent-color-rgb, 0, 123, 255), 0.2);
}

.btn-guardar:disabled { 
  opacity: 0.65; 
  cursor: not-allowed; 
  box-shadow: none;
}

/* ESTADO DE CARGA */
.loading { 
  text-align: center; 
  padding: 5rem 0; 
  color: var(--text-secondary); 
}

.spinner { 
  border: 4px solid rgba(0, 0, 0, 0.05); 
  border-top-color: var(--accent-color); 
  border-radius: 50%; 
  width: 50px; 
  height: 50px; 
  animation: spin 1s linear infinite; 
  margin: 0 auto 1.5rem auto; 
}

@keyframes spin { 
  to { transform: rotate(360deg); } 
}

/* RESPONSIVE */
@media (min-width: 768px) { 
  .form-grid { 
    grid-template-columns: repeat(2, 1fr); 
  }
}

@media (max-width: 480px) {
  .perfil-card {
    padding: 1.5rem;
  }
  .header h1 {
    font-size: 1.8rem;
  }
}
</style>