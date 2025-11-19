<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Título Principal -->
      <div class="brand-section">
        <h1 class="app-title">Los Últimos Serán Los Primeros</h1>
      </div>

      <!-- Acciones del Header -->
      <div class="header-actions">

        <!-- === NUEVO SWITCH SIMPLE SOL / LUNA === -->
        <label class="theme-switch-simple">
          <input 
            id="theme-input"
            type="checkbox"
            :checked="isDarkTheme"
            @change="toggleTheme"
          />
          <div class="simple-icon">
            <span v-if="!isDarkTheme" class="sol">☀️</span>
            <span v-else class="luna">🌙</span>
          </div>
        </label>
        <!-- ======================================== -->

        <!-- Perfil de Usuario -->
        <div class="user-profile">
          <div class="user-info">
            <span class="user-name">{{ usuario.nombre }}</span>
            <span class="user-role">{{ usuario.rol }}</span>
          </div>
          <div class="user-avatar">
            <img :src="usuarioImg" alt="Usuario" class="avatar-img" />
            <span class="online-indicator"></span>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import usuarioImg from '@/assets/usuario.png';

// Lógica de Usuario
const usuario = ref({ 
  nombre: 'Cargando...', 
  rol: 'Cargando...'
});

// Estado del tema
const isDarkTheme = ref(true);

// Cargar usuario actual
const cargarUsuarioActual = () => {
  const user_nombre = localStorage.getItem('user_nombre');
  const user_apellido = localStorage.getItem('user_apellido'); 
  const user_rol = localStorage.getItem('user_rol');
  
  if (user_nombre && user_apellido) {
    usuario.value.nombre = `${user_nombre} ${user_apellido}`;
    usuario.value.rol = formatearRol(user_rol);
  } else {
    usuario.value.nombre = "Iniciado";
    usuario.value.rol = "Iniciado";
  }
};

// Formatear rol
const formatearRol = (rol) => {
  const roles = {
    'ADMINISTRADOR': 'Administrador',
    'CLIENTE': 'Cliente', 
    'PELUQUERO': 'Peluquero',
    'RECEPCIONISTA': 'Recepcionista'
  };
  return roles[rol] || rol;
};

// Toggle tema
const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value;
  
  if (isDarkTheme.value) {
    document.documentElement.classList.remove('light-theme');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.add('light-theme');
    localStorage.setItem('theme', 'light');
  }
};

// Cargar tema guardado
const cargarTemaGuardado = () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    isDarkTheme.value = false;
    document.documentElement.classList.add('light-theme');
  } else {
    isDarkTheme.value = true;
    document.documentElement.classList.remove('light-theme');
  }
};

// Escuchar eventos
const configurarEventos = () => {
  window.addEventListener('usuarioLogueado', cargarUsuarioActual);
  window.addEventListener('storage', cargarUsuarioActual);
};

onMounted(() => {
  cargarUsuarioActual();
  cargarTemaGuardado();
  configurarEventos();
});
</script>

<style scoped>
/* Header Principal */
.app-header {
  position: sticky;
  top: 0;
  width: 100%;
  background: var(--bg-secondary);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  z-index: 1000;
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 100%;
  margin: 0 auto;
  padding: 16px 32px;
  height: 70px;
}

/* Título */
.brand-section {
  flex: 1;
}

.app-title {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
  letter-spacing: 0.3px;
}

/* Acciones del Header */
.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* ===================================================
   SWITCH SIMPLE
   ===================================================*/
.theme-switch-simple {
  cursor: pointer;
  font-size: 1.5rem;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-switch-simple input {
  display: none;
}

.simple-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform .3s ease;
}

.sol, .luna {
  font-size: 1.7rem;
}

.theme-switch-simple:hover .simple-icon {
  transform: scale(1.15);
}

/* ============================================
   PERFIL DE USUARIO
   ============================================ */

.user-profile {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 12px;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-profile:hover {
  background: var(--hover-bg);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1;
}

.user-role {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
  line-height: 1;
  opacity: 0.8;
}

.user-avatar {
  position: relative;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
}

.user-profile:hover .avatar-img {
  border-color: #3b82f6;
  transform: scale(1.05);
}

/* Indicador Online */
.online-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  background: #22c55e;
  border: 2px solid var(--bg-secondary);
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
  animation: pulse-online 2s infinite;
}

@keyframes pulse-online {
  0%, 100% {
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.1);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .app-title {
    font-size: 1.3rem;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 12px 20px;
    height: 65px;
  }

  .app-title {
    font-size: 1.1rem;
  }

  .user-info {
    display: none;
  }

  .user-profile {
    padding: 6px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 480px) {
  .app-title {
    font-size: 0.95rem;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
  }

  .header-actions {
    gap: 12px;
  }
}
</style>
