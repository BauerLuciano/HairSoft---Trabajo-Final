<template>
  <header class="app-header">
    <div class="header-content">
      <div class="brand-section">
        <div class="logo-icon">
          <i class="ri-scissors-cut-line"></i>
        </div>
        <div class="brand-info">
          <h1 class="app-title">HairSoft</h1>
          <span class="app-subtitle">Sistema de Gestión</span>
        </div>
      </div>

      <div class="header-actions">
        <!-- Botón de notificaciones -->
        <button class="action-btn notification-btn">
          <i class="ri-notification-3-line"></i>
          <span class="notification-badge">3</span>
        </button>

        <!-- Toggle de tema con animación -->
        <button @click="toggleTheme" class="action-btn theme-toggle">
          <div class="theme-icon-wrapper">
            <i class="ri-sun-line sun-icon" :class="{ active: isLightMode }"></i>
            <i class="ri-moon-line moon-icon" :class="{ active: !isLightMode }"></i>
          </div>
        </button>

        <!-- Perfil de usuario mejorado -->
        <div class="user-profile">
          <div class="user-info">
            <span class="user-name">{{ usuario.nombre }}</span>
            <span class="user-role">Administrador</span>
          </div>
          <div class="user-avatar">
            <img :src="usuarioImg" alt="Usuario" class="avatar-img" />
            <div class="status-indicator" :class="{ online: usuario.online }">
              <span class="status-pulse"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import usuarioImg from '@/assets/usuario.png';

// Lógica de Usuario
const usuario = ref({ nombre: '', online: true });
const cargarUsuarioActual = async () => {
    try {
        const response = await axios.get('/api/usuario_actual/');
        usuario.value.nombre = `${response.data.nombre} ${response.data.apellido}`;
    } catch (error) {
        usuario.value.nombre = 'Usuario Desconocido';
    }
};

// Lógica de Tema
const isLightMode = ref(false);

const toggleTheme = () => {
    isLightMode.value = !isLightMode.value;
    if (isLightMode.value) {
        document.documentElement.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
    } else {
        document.documentElement.classList.remove('light-mode');
        localStorage.setItem('theme', 'dark');
    }
};

onMounted(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        isLightMode.value = true;
        document.documentElement.classList.add('light-mode');
    }
    cargarUsuarioActual();
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
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 100%;
  margin: 0 auto;
  padding: 12px 32px;
  height: 70px;
}

/* Sección de Marca */
.brand-section {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--accent-color), #8b5cf6);
  border-radius: 14px;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
  transition: all 0.3s ease;
}

.logo-icon:hover {
  transform: translateY(-2px) rotate(5deg);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
}

.logo-icon i {
  font-size: 24px;
  color: #ffffff;
}

.brand-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.app-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1;
  letter-spacing: -0.5px;
}

.app-subtitle {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
  letter-spacing: 0.3px;
  opacity: 0.8;
}

/* Acciones del Header */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Botones de Acción */
.action-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
}

.action-btn:hover {
  background: var(--hover-bg);
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-btn i {
  font-size: 20px;
}

/* Notificaciones */
.notification-btn {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: linear-gradient(135deg, #ff6b6b, #ff4757);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(255, 71, 87, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* Toggle de Tema */
.theme-toggle {
  overflow: hidden;
}

.theme-icon-wrapper {
  position: relative;
  width: 20px;
  height: 20px;
}

.sun-icon,
.moon-icon {
  position: absolute;
  top: 0;
  left: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.sun-icon {
  opacity: 0;
  transform: rotate(-90deg) scale(0);
}

.sun-icon.active {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}

.moon-icon {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}

.moon-icon.active {
  opacity: 0;
  transform: rotate(90deg) scale(0);
}

/* Perfil de Usuario */
.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 6px 6px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-profile:hover {
  background: var(--hover-bg);
  border-color: var(--accent-color);
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1;
}

.user-role {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
  opacity: 0.8;
}

.user-avatar {
  position: relative;
  width: 44px;
  height: 44px;
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
  border-color: var(--accent-color);
  transform: scale(1.05);
}

.status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #6c757d;
  border-radius: 50%;
  border: 2px solid var(--bg-secondary);
  transition: all 0.3s ease;
}

.status-indicator.online {
  background: #00ff88;
  box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.3);
}

.status-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #00ff88;
  opacity: 0;
  animation: pulse-ring 2s infinite;
}

.status-indicator.online .status-pulse {
  opacity: 1;
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    padding: 12px 20px;
  }

  .brand-info {
    display: none;
  }

  .user-info {
    display: none;
  }

  .user-profile {
    padding: 6px;
  }

  .app-subtitle {
    display: none;
  }
}

@media (max-width: 480px) {
  .action-btn {
    width: 40px;
    height: 40px;
  }

  .logo-icon {
    width: 42px;
    height: 42px;
  }

  .logo-icon i {
    font-size: 20px;
  }

  .notification-btn {
    display: none;
  }
}
</style>