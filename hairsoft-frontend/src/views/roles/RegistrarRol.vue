<template>
  <div class="form-container">
    <div class="form-card">
      <div class="form-header">
        <h1>Registrar Rol</h1>
        <p>Ingresa los datos del nuevo rol</p>
      </div>

      <form @submit.prevent="guardarRol" class="form-grid">
        <!-- Nombre del rol -->
        <div class="input-group">
          <label>Nombre del Rol <span class="required">*</span></label>
          <input v-model="rol.nombre" type="text" placeholder="Ej: Administrador" required />
        </div>

        <!-- Descripción -->
        <div class="input-group">
          <label>Descripción</label>
          <textarea v-model="rol.descripcion" placeholder="Descripción del rol"></textarea>
        </div>

        <!-- Botones -->
        <div class="button-group">
          <button type="submit" class="save-btn">💾 Guardar</button>
          <button type="button" @click="cancelar" class="cancel-btn">❌ Cancelar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const rol = ref({ nombre: '', descripcion: '', estado: 'ACTIVO' })

const guardarRol = async () => {
  if (!rol.value.nombre.trim()) { 
    alert('El nombre del rol es obligatorio'); 
    return 
  }
  try {
    await axios.post(`${API_BASE}/usuarios/api/roles/crear/`, rol.value)
    alert('Rol creado con éxito')

    // 🔹 Redirigir a RegistrarUsuario con query para recargar roles
    router.push({ path: '/usuarios/crear', query: { reloadRoles: Date.now() } })

  } catch (err) {
    console.error(err)
    alert('No se pudo crear el rol')
  }
}

const cancelar = () => router.push('/roles')
</script>

<style scoped>
.form-card { background: rgba(23,23,23,0.8); border-radius:24px; padding:40px; max-width:600px; margin:auto; box-shadow:0 25px 50px rgba(0,0,0,0.5) }
.form-header { margin-bottom:30px }
.form-header h1 { font-size:1.8rem; margin-bottom:6px }
.form-header p { color:#aaa; font-size:0.9rem }
.form-grid { display:flex; flex-direction:column; gap:20px }
.input-group { display:flex; flex-direction:column }
.input-group label { font-weight:600; margin-bottom:6px }
.input-group input, .input-group textarea { padding:8px 12px; border-radius:6px; border:none; background:#f3f3f3; font-size:1rem }
textarea { resize:vertical; min-height:80px }
.button-group { display:flex; gap:12px; justify-content:flex-end }
.save-btn { background:#3b82f6; color:white; padding:8px 16px; border:none; border-radius:6px; cursor:pointer; font-weight:600 }
.cancel-btn { background:#ef4444; color:white; padding:8px 16px; border:none; border-radius:6px; cursor:pointer; font-weight:600 }
.required { color:#ef4444 }
</style>
