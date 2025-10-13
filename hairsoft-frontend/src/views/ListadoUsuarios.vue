<template>
  <div class="form-container">
    <div class="form-card usuarios-card">
      <h1 class="form-title">Listado de Usuarios</h1>

      <!-- Barra de acciones -->
      <div class="actions-bar">
        <div class="search-wrapper">
          <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            type="text"
            class="input-field search-input"
            placeholder="Buscar por nombre o correo..."
            v-model="searchTerm"
          />
        </div>

        <div class="filter-wrapper">
          <svg class="filter-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
          </svg>
          <select class="input-field filter-select" v-model="filterRole">
            <option value="todos">Todos los roles</option>
            <option value="ADMIN">Administrador</option>
            <option value="REC">Recepcionista</option>
            <option value="PEL">Peluquero</option>
            <option value="CLI">Cliente</option>
          </select>
        </div>

        <button class="submit-button btn-nuevo" @click="irCrearUsuario">
          Nuevo Usuario
        </button>
      </div>

      <!-- Tabla de usuarios -->
      <div class="table-wrapper">
        <table class="usuarios-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usuario in usuariosFiltrados" :key="usuario.id">
              <td>{{ usuario.id }}</td>
              <td>{{ usuario.nombre }} {{ usuario.apellido }}</td>
              <td>{{ usuario.correo || usuario.email || '-' }}</td>
              <td>
                <span :class="['badge', `badge-${(usuario.rol || '').toLowerCase()}`]">
                  {{ usuario.rol }}
                </span>
              </td>
              <td>
                <span :class="['estado', (usuario.estado || '').toLowerCase()]">
                  {{ usuario.estado || '—' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-action editar" @click="handleEditar(usuario.id)">✏️</button>
                  <button class="btn-action eliminar" @click="handleEliminar(usuario.id)">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="usuariosFiltrados.length === 0" class="no-results">
          <p>No se encontraron usuarios</p>
        </div>
      </div>

      <div class="table-footer">
        <p>Mostrando {{ usuariosFiltrados.length }} de {{ usuarios.length }} usuarios</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const usuarios = ref([]);
const searchTerm = ref('');
const filterRole = ref('todos');

const API_BASE = 'http://127.0.0.1:8000'; // si cambiás el puerto, actualizá acá

// Traer usuarios desde backend (res.data es un array según tu API)
const fetchUsuarios = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`, {
      params: {
        q: searchTerm.value || undefined,
        rol: filterRole.value === 'todos' ? undefined : filterRole.value
      }
    });
    // Respuesta: array directo
    usuarios.value = Array.isArray(res.data) ? res.data : (res.data.usuarios || res.data.results || []);
  } catch (err) {
    console.error('Error al traer usuarios:', err);
    // No queremos romper la app: dejamos usuarios como está
  }
};

// computed: filtra por búsqueda y rol
const usuariosFiltrados = computed(() => {
  const q = (searchTerm.value || '').toLowerCase().trim();
  return usuarios.value.filter(u => {
    const nombreCompleto = `${u.nombre || ''} ${u.apellido || ''}`.toLowerCase();
    const correo = (u.correo || u.email || '').toString().toLowerCase();
    const matchQ = !q || nombreCompleto.includes(q) || correo.includes(q);
    const matchRol = filterRole.value === 'todos' || (u.rol || '') === filterRole.value;
    return matchQ && matchRol;
  });
});

const irCrearUsuario = () => router.push('/usuarios/crear');
const handleEditar = (id) => router.push(`/usuarios/editar/${id}`);
const handleEliminar = async (id) => {
  if (!confirm('¿Estás seguro de eliminar este usuario?')) return;
  try {
    await axios.delete(`${API_BASE}/usuarios/api/usuarios/${id}/`);
    usuarios.value = usuarios.value.filter(u => u.id !== id);
  } catch (err) {
    console.error('Error al eliminar:', err);
    alert('No se pudo eliminar el usuario.');
  }
};

onMounted(fetchUsuarios);
watch([searchTerm, filterRole], () => {
  // llamamos sin spamear demasiado: pequeña debounce simple opcional
  fetchUsuarios();
});
</script>

<style scoped>
/* ==== RESTAURADO: estilos completos (tu CSS original adaptado) ==== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.form-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  background: #0a0a0a;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  position: relative;
  overflow: hidden;
}

.form-container::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 153, 255, 0.15) 0%, transparent 70%);
  top: -200px;
  left: -200px;
  animation: float 20s ease-in-out infinite;
}

.form-container::after {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(138, 43, 226, 0.15) 0%, transparent 70%);
  bottom: -150px;
  right: -150px;
  animation: float 15s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

.form-card {
  background: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
  padding: 48px;
  width: 100%;
  max-width: 1200px;
  position: relative;
  overflow: hidden;
  z-index: 10;
  animation: cardFadeIn 0.8s ease;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent,
    #0099ff 20%,
    #00ff88 40%,
    #ff0080 60%,
    #8a2be2 80%,
    transparent
  );
  animation: borderGlow 4s linear infinite;
}

@keyframes borderGlow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes cardFadeIn {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-title {
  font-size: 32px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
  letter-spacing: -1px;
}

.input-field {
  width: 100%;
  padding: 12px 14px;
  font-size: 14px;
  border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  background: rgba(255,255,255,0.03);
  color: #fff;
  outline: none;
}

.actions-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.search-wrapper { flex: 1; min-width: 220px; position: relative; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: rgba(255,255,255,0.45); pointer-events: none; }
.search-input { padding-left: 42px; }

.filter-wrapper { min-width: 180px; position: relative; }
.filter-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: rgba(255,255,255,0.45); pointer-events: none; }
.filter-select { padding-left: 42px; }

.submit-button {
  padding: 12px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg,#0099ff 0%,#8a2be2 100%);
  color: #fff;
  border: none;
  cursor: pointer;
}

/* tabla */
.table-wrapper { overflow-x: auto; border-radius: 12px; background: rgba(10,10,10,0.35); padding: 8px; }
.usuarios-table { width: 100%; border-collapse: collapse; min-width: 800px; }
.usuarios-table th, .usuarios-table td { padding: 12px 14px; text-align: left; color: #fff; border-bottom: 1px solid rgba(255,255,255,0.04); }
.usuarios-table th { background: rgba(0,0,0,0.35); text-transform: uppercase; font-size: 12px; letter-spacing: 0.6px; }
.usuarios-table tbody tr:hover { background: rgba(0,153,255,0.04); transform: translateY(-1px); }

/* badges y estados */
.badge { display:inline-block; padding: 4px 10px; border-radius: 12px; font-weight:700; font-size: 13px; }
.badge-admin { background: linear-gradient(135deg,#ff6b6b,#ee5a6f); color:#fff; }
.badge-rec { background: linear-gradient(135deg,#ffd166,#f6a609); color:#1a1a1a; }
.badge-pel { background: linear-gradient(135deg,#4ecdc4,#44a08d); color:#fff; }
.badge-cli { background: linear-gradient(135deg,#a8e6cf,#56ab91); color:#1a1a1a; }

.estado { display:inline-block; padding: 4px 10px; border-radius: 12px; font-weight:700; font-size: 13px; }
.estado.pending { background: rgba(255,193,7,0.12); color:#ffc107; border:1px solid rgba(255,193,7,0.18); }
.estado.activo { background: rgba(40,199,111,0.12); color:#28c76f; border:1px solid rgba(40,199,111,0.18); }
.estado.inactivo { background: rgba(255,71,87,0.12); color:#ff4757; border:1px solid rgba(255,71,87,0.18); }

.action-buttons { display:flex; gap:8px; }
.btn-action { padding:8px; border-radius:8px; border:none; cursor:pointer; }
.btn-action.editar { background: linear-gradient(135deg,#0099ff,#00d4ff); color:#fff; }
.btn-action.eliminar { background: linear-gradient(135deg,#ff4757,#ff6348); color:#fff; }

.no-results { padding: 24px; text-align:center; color: rgba(255,255,255,0.6); }

.table-footer { margin-top:16px; text-align:center; color: rgba(255,255,255,0.6); }

/* responsive */
@media (max-width: 768px) {
  .form-card { padding: 22px; }
  .usuarios-table { font-size: 13px; min-width: 600px; }
  .search-wrapper, .filter-wrapper { width: 100%; }
}
</style>
