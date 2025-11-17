<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Título Principal -->
      <div class="brand-section">
        <h1 class="app-title">Los Últimos Serán Los Primeros</h1>
      </div>

      <!-- Acciones del Header -->
      <div class="header-actions">
        <!-- Switch Tema Oscuro/Claro -->
        <label class="theme-switch">
          <input 
            id="theme-input" 
            type="checkbox" 
            :checked="isDarkTheme"
            @change="toggleTheme"
          />
          <div class="slider round">
            <div class="sun-moon">
              <svg id="moon-dot-1" class="moon-dot" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="moon-dot-2" class="moon-dot" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="moon-dot-3" class="moon-dot" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="light-ray-1" class="light-ray" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="light-ray-2" class="light-ray" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="light-ray-3" class="light-ray" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="cloud-1" class="cloud-dark" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="cloud-2" class="cloud-dark" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="cloud-3" class="cloud-dark" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="cloud-4" class="cloud-light" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="cloud-5" class="cloud-light" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
              <svg id="cloud-6" class="cloud-light" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="50"></circle>
              </svg>
            </div>
            <div class="stars">
              <svg id="star-1" class="star" viewBox="0 0 20 20">
                <path d="M 0 10 C 10 10,10 10 ,0 10 C 10 10 , 10 10 , 10 20 C 10 10 , 10 10 , 20 10 C 10 10 , 10 10 , 10 0 C 10 10,10 10 ,0 10 Z"></path>
              </svg>
              <svg id="star-2" class="star" viewBox="0 0 20 20">
                <path d="M 0 10 C 10 10,10 10 ,0 10 C 10 10 , 10 10 , 10 20 C 10 10 , 10 10 , 20 10 C 10 10 , 10 10 , 10 0 C 10 10,10 10 ,0 10 Z"></path>
              </svg>
              <svg id="star-3" class="star" viewBox="0 0 20 20">
                <path d="M 0 10 C 10 10,10 10 ,0 10 C 10 10 , 10 10 , 10 20 C 10 10 , 10 10 , 20 10 C 10 10 , 10 10 , 10 0 C 10 10,10 10 ,0 10 Z"></path>
              </svg>
              <svg id="star-4" class="star" viewBox="0 0 20 20">
                <path d="M 0 10 C 10 10,10 10 ,0 10 C 10 10 , 10 10 , 10 20 C 10 10 , 10 10 , 20 10 C 10 10 , 10 10 , 10 0 C 10 10,10 10 ,0 10 Z"></path>
              </svg>
            </div>
          </div>
        </label>

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
    usuario.value.nombre = "Invitado";
    usuario.value.rol = "Invitado";
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

/* ============================================
   THEME SWITCH (Sol/Luna animado)
   ============================================ */

.theme-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
  cursor: pointer;
}

.theme-switch #theme-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #2196f3;
  transition: 0.4s;
  z-index: 0;
  overflow: hidden;
}

.sun-moon {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: yellow;
  transition: 0.4s;
}

#theme-input:checked + .slider {
  background-color: #0f172a;
}

#theme-input:focus + .slider {
  box-shadow: 0 0 1px #2196f3;
}

#theme-input:checked + .slider .sun-moon {
  transform: translateX(26px);
  background-color: white;
  animation: rotate-center 0.6s ease-in-out both;
}

.moon-dot {
  opacity: 0;
  transition: 0.4s;
  fill: gray;
}

#theme-input:checked + .slider .sun-moon .moon-dot {
  opacity: 1;
}

.slider.round {
  border-radius: 34px;
}

.slider.round .sun-moon {
  border-radius: 50%;
}

#moon-dot-1 {
  left: 10px;
  top: 3px;
  position: absolute;
  width: 6px;
  height: 6px;
  z-index: 4;
}

#moon-dot-2 {
  left: 2px;
  top: 10px;
  position: absolute;
  width: 10px;
  height: 10px;
  z-index: 4;
}

#moon-dot-3 {
  left: 16px;
  top: 18px;
  position: absolute;
  width: 3px;
  height: 3px;
  z-index: 4;
}

#light-ray-1 {
  left: -8px;
  top: -8px;
  position: absolute;
  width: 43px;
  height: 43px;
  z-index: -1;
  fill: white;
  opacity: 10%;
}

#light-ray-2 {
  left: -50%;
  top: -50%;
  position: absolute;
  width: 55px;
  height: 55px;
  z-index: -1;
  fill: white;
  opacity: 10%;
}

#light-ray-3 {
  left: -18px;
  top: -18px;
  position: absolute;
  width: 60px;
  height: 60px;
  z-index: -1;
  fill: white;
  opacity: 10%;
}

.cloud-light {
  position: absolute;
  fill: #eee;
  animation-name: cloud-move;
  animation-duration: 6s;
  animation-iteration-count: infinite;
}

.cloud-dark {
  position: absolute;
  fill: #ccc;
  animation-name: cloud-move;
  animation-duration: 6s;
  animation-iteration-count: infinite;
  animation-delay: 1s;
}

#cloud-1 {
  left: 30px;
  top: 15px;
  width: 40px;
}

#cloud-2 {
  left: 44px;
  top: 10px;
  width: 20px;
}

#cloud-3 {
  left: 18px;
  top: 24px;
  width: 30px;
}

#cloud-4 {
  left: 36px;
  top: 18px;
  width: 40px;
}

#cloud-5 {
  left: 48px;
  top: 14px;
  width: 20px;
}

#cloud-6 {
  left: 22px;
  top: 26px;
  width: 30px;
}

@keyframes cloud-move {
  0% {
    transform: translateX(0px);
  }
  40% {
    transform: translateX(4px);
  }
  80% {
    transform: translateX(-4px);
  }
  100% {
    transform: translateX(0px);
  }
}

.stars {
  transform: translateY(-32px);
  opacity: 0;
  transition: 0.4s;
}

.star {
  fill: white;
  position: absolute;
  transition: 0.4s;
  animation-name: star-twinkle;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}

#theme-input:checked + .slider .stars {
  transform: translateY(0);
  opacity: 1;
}

#star-1 {
  width: 20px;
  top: 2px;
  left: 3px;
  animation-delay: 0.3s;
}

#star-2 {
  width: 6px;
  top: 16px;
  left: 3px;
}

#star-3 {
  width: 12px;
  top: 20px;
  left: 10px;
  animation-delay: 0.6s;
}

#star-4 {
  width: 18px;
  top: 0px;
  left: 18px;
  animation-delay: 1.3s;
}

@keyframes star-twinkle {
  0% {
    transform: scale(1);
  }
  40% {
    transform: scale(1.2);
  }
  80% {
    transform: scale(0.8);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes rotate-center {
  0% {
    transform: translateX(26px) rotate(0);
  }
  100% {
    transform: translateX(26px) rotate(360deg);
  }
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

  .theme-switch {
    width: 50px;
    height: 28px;
  }

  .sun-moon {
    height: 22px;
    width: 22px;
  }

  #theme-input:checked + .slider .sun-moon {
    transform: translateX(22px);
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