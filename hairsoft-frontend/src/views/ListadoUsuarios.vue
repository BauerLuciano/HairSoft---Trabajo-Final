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
            placeholder="Buscar por nombre o email..."
            v-model="searchTerm"
          />
        </div>
        
        <div class="filter-wrapper">
          <svg class="filter-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
          </svg>
          <select 
            class="input-field filter-select"
            v-model="filterRole"
          >
            <option value="todos">Todos los roles</option>
            <option value="Admin">Admin</option>
            <option value="Moderador">Moderador</option>
            <option value="Usuario">Usuario</option>
          </select>
        </div>

        <button class="submit-button btn-nuevo" @click="irCrearUsuario">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <line x1="19" y1="8" x2="19" y2="14"></line>
            <line x1="22" y1="11" x2="16" y2="11"></line>
          </svg>
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
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usuario in usuariosFiltrados" :key="usuario.id">
              <td>{{ usuario.id }}</td>
              <td>{{ usuario.nombre }}</td>
              <td>{{ usuario.email }}</td>
              <td>
                <span :class="['badge', `badge-${usuario.rol.toLowerCase()}`]">
                  {{ usuario.rol }}
                </span>
              </td>
              <td>
                <span :class="['estado', usuario.estado.toLowerCase()]">
                  {{ usuario.estado }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="btn-action editar"
                    @click="handleEditar(usuario.id)"
                    title="Editar"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button 
                    class="btn-action eliminar"
                    @click="handleEliminar(usuario.id)"
                    title="Eliminar"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="usuariosFiltrados.length === 0" class="no-results">
          <p>No se encontraron usuarios</p>
        </div>
      </div>

      <!-- Footer con info -->
      <div class="table-footer">
        <p>Mostrando {{ usuariosFiltrados.length }} de {{ usuarios.length }} usuarios</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router'; // Si usás Vue Router

const router = useRouter();

// Estado reactivo
const searchTerm = ref('');
const filterRole = ref('todos');

// Datos de ejemplo
const usuarios = ref([
  { id: 1, nombre: 'Juan Pérez', email: 'juan@example.com', rol: 'Admin', estado: 'Activo' },
  { id: 2, nombre: 'María García', email: 'maria@example.com', rol: 'Usuario', estado: 'Activo' },
  { id: 3, nombre: 'Carlos López', email: 'carlos@example.com', rol: 'Moderador', estado: 'Inactivo' },
  { id: 4, nombre: 'Ana Martínez', email: 'ana@example.com', rol: 'Usuario', estado: 'Activo' },
  { id: 5, nombre: 'Pedro Sánchez', email: 'pedro@example.com', rol: 'Admin', estado: 'Activo' },
]);

// Computed para filtrado
const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(u => {
    const matchSearch = u.nombre.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
                        u.email.toLowerCase().includes(searchTerm.value.toLowerCase());
    const matchRole = filterRole.value === 'todos' || u.rol === filterRole.value;
    return matchSearch && matchRole;
  });
});

// Métodos
const irCrearUsuario = () => {
  router.push('/usuarios/crear'); // Ajustá la ruta según tu app
};

const handleEditar = (id) => {
  router.push(`/usuarios/editar/${id}`); // O usá un modal
};

const handleEliminar = (id) => {
  if (confirm('¿Estás seguro de eliminar este usuario?')) {
    usuarios.value = usuarios.value.filter(u => u.id !== id);
  }
};
</script>

<style scoped>
/* === BASE STYLES (colores de tu formulario.css) === */
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
  max-width: 500px;
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

.usuarios-card {
  max-width: 1200px;
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-title {
  font-size: 32px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
  letter-spacing: -1px;
}

.input-field {
  width: 100%;
  padding: 15px 18px;
  font-size: 15px;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-weight: 500;
  outline: none;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-field:focus {
  border-color: rgba(0, 153, 255, 0.6);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 153, 255, 0.2),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.submit-button {
  width: auto;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #0099ff 0%, #8a2be2 100%);
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 153, 255, 0.4),
              inset 0 1px 0 rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  letter-spacing: 0.5px;
}

.submit-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.submit-button:hover::before {
  left: 100%;
}

.submit-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 48px rgba(0, 153, 255, 0.6),
              0 0 60px rgba(138, 43, 226, 0.4);
}

.submit-button:active {
  transform: translateY(-1px);
}

/* === ESTILOS ESPECÍFICOS DE LISTADO === */
.actions-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
  align-items: center;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.search-input {
  padding-left: 48px;
}

.filter-wrapper {
  position: relative;
  min-width: 180px;
}

.filter-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.filter-select {
  padding-left: 48px;
  cursor: pointer;
}

.btn-nuevo {
  white-space: nowrap;
}

/* === TABLA === */
.table-wrapper {
  overflow-x: auto;
  border-radius: 16px;
  background: rgba(10, 10, 10, 0.4);
}

.usuarios-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(10px);
}

.usuarios-table th,
.usuarios-table td {
  padding: 16px;
  text-align: left;
  color: #ffffff;
  font-size: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.usuarios-table th {
  background: rgba(0, 0, 0, 0.4);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.8);
}

.usuarios-table tbody tr {
  transition: all 0.3s ease;
}

.usuarios-table tbody tr:hover {
  background: rgba(0, 153, 255, 0.08);
  transform: scale(1.01);
}

.usuarios-table tbody tr:last-child td {
  border-bottom: none;
}

/* === BADGES Y ESTADOS === */
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.badge-admin {
  background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
  color: white;
}

.badge-moderador {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
}

.badge-usuario {
  background: linear-gradient(135deg, #a8e6cf, #56ab91);
  color: #1a1a1a;
}

.estado {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.estado.activo {
  background: rgba(46, 213, 115, 0.2);
  color: #2ed573;
  border: 1px solid #2ed573;
}

.estado.inactivo {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
  border: 1px solid #ff4757;
}

/* === BOTONES DE ACCIÓN === */
.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 8px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action.editar {
  background: linear-gradient(135deg, #0099ff, #00d4ff);
  color: white;
}

.btn-action.editar:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 20px rgba(0, 153, 255, 0.4);
}

.btn-action.eliminar {
  background: linear-gradient(135deg, #ff4757, #ff6348);
  color: white;
}

.btn-action.eliminar:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 20px rgba(255, 71, 87, 0.4);
}

/* === NO RESULTS === */
.no-results {
  padding: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
}

/* === FOOTER === */
.table-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .form-card {
    padding: 25px;
  }

  .form-title {
    font-size: 24px;
  }

  .actions-bar {
    flex-direction: column;
  }

  .search-wrapper,
  .filter-wrapper {
    width: 100%;
  }

  .usuarios-table {
    font-size: 13px;
  }

  .usuarios-table th,
  .usuarios-table td {
    padding: 10px 8px;
  }

  .badge,
  .estado {
    font-size: 11px;
    padding: 3px 8px;
  }
}
</style>