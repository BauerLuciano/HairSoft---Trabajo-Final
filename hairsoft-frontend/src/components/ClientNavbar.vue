<template>
  <nav class="client-nav">
    <div class="nav-content">
      <!-- Logo con efecto similar al sidebar -->
      <div class="logo-section">
        <div class="logo-wrapper">
          <router-link :to="homeLink" class="logo-link">
            <div class="logo-container">
              <span class="logo-icon">✂️</span>
            </div>
            <div class="brand-info">
              <span class="brand-name">HairSoft</span>
              <span class="brand-subtitle" v-if="usuarioLogueado">CLIENTE</span>
            </div>
          </router-link>
        </div>
      </div>
      
      <!-- Navegación principal - con efectos del sidebar -->
      <div class="nav-links-section">
        <div class="links-container">
          <router-link :to="homeLink" class="nav-link">
            <div class="link-content">
              <div class="link-icon">🏠</div>
              <span class="link-text">Inicio</span>
            </div>
            <div class="link-indicator"></div>
          </router-link>
          
          <router-link to="/web/servicios" class="nav-link">
            <div class="link-content">
              <div class="link-icon">✂️</div>
              <span class="link-text">Servicios</span>
            </div>
            <div class="link-indicator"></div>
          </router-link>
          
          <router-link to="/web/productos" class="nav-link">
            <div class="link-content">
              <div class="link-icon">🛒</div>
              <span class="link-text">Productos</span>
            </div>
            <div class="link-indicator"></div>
          </router-link>
          
          <router-link v-if="usuarioLogueado" to="/cliente/historial" class="nav-link">
            <div class="link-content">
              <div class="link-icon">📅</div>
              <span class="link-text">Mis Turnos</span>
            </div>
            <div class="link-indicator"></div>
          </router-link>
        </div>
      </div>
      
      <!-- Acciones de usuario - MEJORADO con efectos del header -->
      <div class="user-actions-section">
        <div v-if="usuarioLogueado" class="user-profile-wrapper" ref="profileRef">
          <div class="user-profile" @click="toggleDropdown" :class="{ 'active': dropdownOpen }">
            <div class="user-info">
              <span class="user-name">Hola, {{ usuarioNombre }}</span>
              <span class="user-role">Cliente</span>
            </div>
            <div class="user-avatar">
              <div class="avatar-circle">
                <span class="avatar-initials">{{ avatarInitial }}</span>
              </div>
              <span class="online-indicator"></span>
            </div>
            <span class="dropdown-arrow">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>

          <!-- Dropdown MEJORADO con efectos del header -->
          <transition name="dropdown">
            <div v-if="dropdownOpen" class="profile-dropdown">
              <div class="dropdown-header">
                <div class="dropdown-avatar">
                  <div class="avatar-circle-large">
                    {{ avatarInitial }}
                  </div>
                </div>
                <div class="dropdown-user-info">
                  <span class="dropdown-greeting">Hola,</span>
                  <span class="dropdown-username">{{ usuarioNombre }}</span>
                  <span class="dropdown-role">Cliente</span>
                </div>
              </div>
                            
              <div class="dropdown-divider"></div>
              
              <button @click="confirmLogout" class="dropdown-item logout">
                <svg class="item-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>Cerrar Sesión</span>
              </button>
            </div>
          </transition>
        </div>

        <div v-else class="auth-buttons">
          <router-link to="/login" class="auth-btn login-btn">
            <div class="btn-icon">🔑</div>
            <span>Ingresar</span>
          </router-link>
          <router-link to="/web/registro" class="auth-btn register-btn">
            <div class="btn-icon">📝</div>
            <span>Crear Cuenta</span>
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';

const router = useRouter();
const usuarioLogueado = ref(false);
const usuarioNombre = ref('');
const usuarioApellido = ref('');
const dropdownOpen = ref(false);
const profileRef = ref(null);

// Propiedades computadas
const homeLink = computed(() => {
  return usuarioLogueado.value ? '/cliente/dashboard' : '/web/home';
});

const avatarInitial = computed(() => {
  if (usuarioNombre.value) {
    const inicialNombre = usuarioNombre.value.charAt(0).toUpperCase();
    const inicialApellido = usuarioApellido.value ? usuarioApellido.value.charAt(0).toUpperCase() : '';
    return inicialNombre + inicialApellido;
  }
  return 'C';
});

onMounted(() => {
  const token = localStorage.getItem('token');
  const rol = localStorage.getItem('user_rol');
  
  if (token && rol === 'CLIENTE') {
    usuarioLogueado.value = true;
    usuarioNombre.value = localStorage.getItem('user_nombre') || 'Cliente';
    usuarioApellido.value = localStorage.getItem('user_apellido') || '';
  }
  
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Cerrar dropdown al hacer click fuera
const handleClickOutside = (event) => {
  if (profileRef.value && !profileRef.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
};

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

const confirmLogout = () => {
  dropdownOpen.value = false;
  
  Swal.fire({
    title: '¿Cerrar sesión?',
    text: "¿Estás seguro que deseas salir de tu cuenta?",
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, salir',
    cancelButtonText: 'Cancelar',
    background: '#0f172a',
    color: '#fff',
    customClass: {
      popup: 'sweet-popup',
      title: 'sweet-title',
      confirmButton: 'sweet-confirm',
      cancelButton: 'sweet-cancel'
    }
  }).then((result) => {
    if (result.isConfirmed) {
      logout();
    }
  });
};

const logout = () => {
  localStorage.clear();
  
  const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 2000,
    timerProgressBar: true,
    background: '#0f172a',
    color: '#fff',
    iconColor: '#3b82f6'
  });
  
  Toast.fire({
    icon: 'success',
    title: 'Sesión cerrada correctamente'
  }).then(() => {
    window.location.href = '/web/home';
  });
};
</script>

<style scoped>
/* NAVBAR PRINCIPAL - Mismo estilo que sidebar */
.client-nav {
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
  height: 70px;
  display: flex;
  align-items: center;
}

.client-nav::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 32px;
  right: 32px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
}

.nav-content {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  gap: 30px;
}

/* Logo Section - Igual que sidebar */
.logo-section {
  flex-shrink: 0;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-container {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #3b82f6;
  box-shadow: 
    0 0 20px rgba(59, 130, 246, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.3),
    inset 0 0 0 1px rgba(255, 255, 255, 0.1);
  position: relative;
  transition: all 0.3s ease;
}

.logo-container::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
  z-index: -1;
  opacity: 0.3;
  filter: blur(4px);
}

.logo-container:hover {
  transform: scale(1.05);
  box-shadow: 
    0 0 25px rgba(59, 130, 246, 0.5),
    0 6px 16px rgba(0, 0, 0, 0.4);
}

.logo-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 1.6rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 0.65rem;
  font-weight: 700;
  color: #60a5fa;
  letter-spacing: 2px;
  text-transform: uppercase;
  opacity: 0.9;
}

/* Navegación principal - con efectos del sidebar */
.nav-links-section {
  flex: 1;
  display: flex;
  justify-content: center;
}

.links-container {
  display: flex;
  gap: 2px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 12px;
  padding: 4px;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  text-decoration: none;
  padding: 10px 20px;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  min-width: 120px;
  justify-content: center;
}

.nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #3b82f6;
  transform: scaleY(0);
  transition: transform 0.3s ease;
  border-radius: 0 2px 2px 0;
}

.link-content {
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 2;
}

.link-icon {
  font-size: 1.1rem;
  transition: all 0.3s ease;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.link-text {
  font-size: 0.95rem;
  font-weight: 600;
  color: #d1d5db;
  letter-spacing: 0.3px;
  transition: all 0.3s ease;
}

.link-indicator {
  width: 0;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  background: #60a5fa;
  border-radius: 0 4px 4px 0;
  transition: width 0.3s ease;
  z-index: 1;
}

/* Hover y Active States */
.nav-link:hover {
  background: rgba(31, 41, 55, 0.8);
  transform: translateY(-2px);
}

.nav-link:hover::before {
  transform: scaleY(1);
}

.nav-link:hover .link-icon {
  transform: scale(1.1);
}

.nav-link:hover .link-text {
  color: #fff;
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  box-shadow: 
    0 4px 16px rgba(59, 130, 246, 0.4),
    0 2px 8px rgba(0, 0, 0, 0.2);
}

.nav-link.router-link-active::before {
  transform: scaleY(1);
  background: #60a5fa;
}

.nav-link.router-link-active .link-icon {
  color: #ffffff;
  transform: scale(1.1);
}

.nav-link.router-link-active .link-text {
  color: #ffffff;
  font-weight: 600;
}

/* ============================================
   USER PROFILE SECTION - ESTILO HEADER
   ============================================ */
.user-actions-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-profile-wrapper {
  position: relative;
}

/* Perfil de usuario - Estilo Header */
.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
  position: relative;
}

.user-profile::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #3b82f6;
  transform: scaleY(0);
  transition: transform 0.3s ease;
  border-radius: 0 2px 2px 0;
}

.user-profile:hover,
.user-profile.active {
  background: rgba(31, 41, 55, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.user-profile:hover::before,
.user-profile.active::before {
  transform: scaleY(0.6);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
}

.user-name {
  font-size: 1.05rem;
  font-weight: 600;
  color: #d1d5db;
  letter-spacing: 0.3px;
}

.user-role {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
}

/* Avatar - Estilo Header */
.user-avatar {
  position: relative;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
}

.avatar-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #3b82f6;
  box-shadow: 
    0 0 20px rgba(59, 130, 246, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.3),
    inset 0 0 0 1px rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.avatar-circle::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
  z-index: -1;
  opacity: 0.3;
  filter: blur(4px);
}

.user-profile:hover .avatar-circle {
  transform: scale(1.05);
}

.avatar-initials {
  color: white;
  font-weight: bold;
  font-size: 1.05rem;
  z-index: 1;
}

.online-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 11px;
  height: 11px;
  background: #22c55e;
  border: 2.5px solid #111827;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
}

.dropdown-arrow {
  display: flex;
  align-items: center;
  color: #9ca3af;
  margin-left: 2px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-profile.active .dropdown-arrow {
  transform: rotate(180deg);
  color: #60a5fa;
}

/* ============================================
   DROPDOWN MENU - ESTILO HEADER MEJORADO
   ============================================ */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  min-width: 280px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.3);
  padding: 12px;
  z-index: 1001;
  transform-origin: top right;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  position: relative;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
  margin-bottom: 8px;
}

.dropdown-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 16px;
  right: 16px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
}

.dropdown-avatar {
  flex-shrink: 0;
}

.avatar-circle-large {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.4rem;
  border: 3px solid #3b82f6;
  box-shadow: 
    0 0 20px rgba(59, 130, 246, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.3);
  position: relative;
}

.avatar-circle-large::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
  z-index: -1;
  opacity: 0.3;
  filter: blur(4px);
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.dropdown-greeting {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 600;
  letter-spacing: 2.5px;
  text-transform: uppercase;
}

.dropdown-username {
  font-weight: 800;
  font-size: 1.1rem;
  letter-spacing: 0.3px;
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dropdown-role {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
  letter-spacing: 0.2px;
}

.dropdown-divider {
  height: 1px;
  background: rgba(59, 130, 246, 0.1);
  margin: 8px 0;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 16px;
  border: none;
  background: transparent;
  color: #d1d5db;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  position: relative;
  text-decoration: none;
}

.dropdown-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #3b82f6;
  transform: scaleY(0);
  transition: transform 0.2s ease;
  border-radius: 0 2px 2px 0;
}

.dropdown-item:hover::before {
  transform: scaleY(1);
}

.dropdown-item:hover {
  background: rgba(31, 41, 55, 0.8);
  transform: translateX(3px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.item-icon {
  flex-shrink: 0;
  transition: transform 0.2s ease;
  font-size: 1.1rem;
}

.dropdown-item:hover .item-icon {
  transform: scale(1.1);
}

.dropdown-item.logout {
  color: #ef4444;
  margin-top: 4px;
}

.dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* Animación de entrada */
.dropdown-enter-active {
  animation: dropdown-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-leave-active {
  animation: dropdown-out 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes dropdown-in {
  0% {
    opacity: 0;
    transform: translateY(-15px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes dropdown-out {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-10px) scale(0.97);
  }
}

/* Auth Buttons (No logueado) */
.auth-buttons {
  display: flex;
  gap: 12px;
}

.auth-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.login-btn {
  color: #d1d5db;
  border: 1px solid rgba(59, 130, 246, 0.3);
  background: rgba(30, 41, 59, 0.5);
}

.login-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #fff;
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-2px);
}

.register-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.register-btn:hover {
  background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.btn-icon {
  font-size: 1rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .nav-content {
    padding: 0 20px;
    gap: 20px;
  }
  
  .links-container {
    gap: 1px;
  }
  
  .nav-link {
    padding: 10px 15px;
    min-width: 100px;
  }
  
  .link-text {
    font-size: 0.9rem;
  }
}

@media (max-width: 768px) {
  .client-nav {
    height: 60px;
  }
  
  .nav-content {
    padding: 0 15px;
  }
  
  .brand-name {
    font-size: 1.3rem;
  }
  
  .logo-container {
    width: 40px;
    height: 40px;
  }
  
  .logo-icon {
    font-size: 1.2rem;
  }
  
  .links-container {
    display: none; /* Ocultar links en móvil */
  }
  
  .user-info {
    display: none;
  }
  
  .user-profile {
    gap: 10px;
    padding: 6px 10px;
  }
  
  .user-avatar {
    width: 38px;
    height: 38px;
  }
  
  .auth-btn span {
    display: none;
  }
  
  .auth-btn {
    padding: 10px;
  }
  
  .profile-dropdown {
    min-width: 260px;
    right: -8px;
  }
}

@media (max-width: 480px) {
  .brand-name {
    display: none;
  }
  
  .logo-link {
    gap: 0;
  }
  
  .profile-dropdown {
    min-width: 240px;
  }
}
</style>