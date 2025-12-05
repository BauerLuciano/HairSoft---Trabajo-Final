<template>
  <div class="perfil-container">
    <div class="header">
      <h1>Mis Datos 👤</h1>
      <button @click="$router.push('/cliente/dashboard')" class="btn-volver">Volver</button>
    </div>

    <div v-if="cargando" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else class="perfil-card">
      <form @submit.prevent="guardarCambios">
        <div class="form-group">
          <label>Nombre Completo</label>
          <input type="text" :value="`${usuario.nombre} ${usuario.apellido}`" disabled class="input-disabled">
        </div>

        <div class="form-group">
          <label>Correo Electrónico</label>
          <input type="email" v-model="usuario.correo" disabled class="input-disabled">
        </div>

        <div class="form-group">
          <label>Teléfono / Celular</label>
          <input type="text" v-model="form.telefono" placeholder="Tu número de contacto">
        </div>

        <div class="divider"></div>
        <h3>Seguridad</h3>

        <div class="form-group">
          <label>Contraseña Actual (Requerida solo si vas a cambiarla)</label>
          <input type="password" v-model="form.currentPassword" placeholder="Tu contraseña actual">
        </div>

        <div class="form-group">
          <label>Nueva Contraseña</label>
          <input type="password" v-model="form.newPassword" placeholder="Nueva contraseña">
        </div>

        <button type="submit" class="btn-guardar" :disabled="guardando">
          {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import Swal from 'sweetalert2';

const usuario = ref({});
const form = ref({
  telefono: '',
  currentPassword: '',
  newPassword: ''
});
const cargando = ref(true);
const guardando = ref(false);

const cargarDatos = async () => {
  try {
    const userId = localStorage.getItem('user_id');
    // Asegúrate de que este endpoint exista y sea accesible
    const response = await api.get(`/usuarios/${userId}/`); 
    usuario.value = response.data;
    form.value.telefono = response.data.telefono;
  } catch (error) {
    console.error(error);
    Swal.fire('Error', 'No pudimos cargar tus datos', 'error');
  } finally {
    cargando.value = false;
  }
};

const guardarCambios = async () => {
  // Validación simple
  if (form.value.newPassword && !form.value.currentPassword) {
    Swal.fire('Atención', 'Debes ingresar tu contraseña actual para cambiarla.', 'warning');
    return;
  }

  guardando.value = true;
  try {
    const userId = localStorage.getItem('user_id');
    const payload = {
      telefono: form.value.telefono
    };

    // Solo enviamos contraseñas si el usuario escribió algo
    if (form.value.newPassword) {
      payload.contrasena_nueva = form.value.newPassword;
      payload.contrasena_actual = form.value.currentPassword;
    }

    // Usamos PATCH contra la vista que acabamos de arreglar
    await api.patch(`/usuarios/editar/${userId}/`, payload);

    Swal.fire('Éxito', 'Tus datos han sido actualizados', 'success');
    
    // Limpiar campos de password
    form.value.currentPassword = '';
    form.value.newPassword = '';
    
  } catch (error) {
    console.error(error);
    const msg = error.response?.data?.message || 'No se pudieron guardar los cambios';
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
.perfil-container { max-width: 600px; margin: 2rem auto; padding: 0 1rem; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.perfil-card { background: var(--bg-secondary); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color); }
.form-group { margin-bottom: 1.5rem; }
.divider { height: 1px; background: var(--border-color); margin: 2rem 0 1rem; }
h3 { color: var(--accent-color); margin-bottom: 1rem; font-size: 1.1rem; }
label { display: block; margin-bottom: 0.5rem; color: var(--text-secondary); }
input { 
  width: 100%; padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border-color); 
  background: var(--bg-primary); color: var(--text-primary);
}
.input-disabled { opacity: 0.7; cursor: not-allowed; background: rgba(0,0,0,0.2); }
.btn-guardar {
  width: 100%; padding: 1rem; background: var(--accent-color); color: white; border: none; 
  border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 1rem;
}
.btn-volver { background: transparent; border: 1px solid var(--text-secondary); color: var(--text-primary); padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;}
.loading { text-align: center; padding: 2rem; }
.spinner { /* Reutiliza tu estilo de spinner */ border: 3px solid rgba(255,255,255,0.1); border-top-color: var(--accent-color); border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>