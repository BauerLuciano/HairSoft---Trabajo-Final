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
        <!-- Perfil de usuario mejorado -->
        <div class="user-profile">
          <div class="user-info">
            <span class="user-name">{{ usuario.nombre }}</span>
            <span class="user-role">{{ usuario.rol }}</span>
          </div>
          <div class="user-avatar">
            <img :src="usuarioImg" alt="Usuario" class="avatar-img" />
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
const usuario = ref({ 
  nombre: 'Cargando...', 
  rol: 'Cargando...'
});

const cargarUsuarioActual = () => {
  const user_nombre = localStorage.getItem('user_nombre');
  const user_apellido = localStorage.getItem('user_apellido'); 
  const user_rol = localStorage.getItem('user_rol');
  
  if (user_nombre && user_apellido) {
    usuario.value.nombre = `${user_nombre} ${user_apellido}`;
    usuario.value.rol = formatearRol(user_rol);
  } else {
    usuario.value.nombre = "Invitado";
    usuario.value.rol = "Invitado";
  }
};

// Función para formatear el rol
const formatearRol = (rol) => {
  const roles = {
    'ADMINISTRADOR': 'Administrador',
    'CLIENTE': 'Cliente', 
    'PELUQUERO': 'Peluquero',
    'RECEPCIONISTA': 'Recepcionista'
  };
  return roles[rol] || rol;
};

// 🆕 ESCUCHAR EVENTOS PARA ACTUALIZAR AUTOMÁTICAMENTE
const configurarEventos = () => {
  // Escuchar evento personalizado del login
  window.addEventListener('usuarioLogueado', cargarUsuarioActual);
  
  // Escuchar cambios en localStorage desde otras pestañas
  window.addEventListener('storage', cargarUsuarioActual);
};

onMounted(() => {
  cargarUsuarioActual();
  configurarEventos();
});
</script>

<style scoped>
/* (MANTENÉ TODOS TUS ESTILOS ORIGINALES IGUAL) */
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

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
</style>