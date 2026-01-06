<template>
  <nav class="client-nav">
    <div class="nav-content">
      
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
      
      <div class="nav-links-section">
        <div class="links-container">
          <button @click="irAInicio" :class="['nav-link', { active: !rutaActual || rutaActual === 'resumen' }]">
            <span class="link-text">Inicio</span>
            <div class="link-indicator"></div>
          </button>
          
          <router-link to="/web/servicios" class="nav-link">
            <span class="link-text">Servicios</span>
            <div class="link-indicator"></div>
          </router-link>
          
          <router-link :to="{ name: 'ProductosPublico' }" class="nav-link">
            <span class="link-text">Productos</span>
            <div class="link-indicator"></div>
          </router-link>
          
          <!-- ✅ MIS TURNOS (Solo visible si está logueado) -->
          <router-link 
            v-if="usuarioLogueado" 
            :to="{ name: 'HistorialTurnos' }" 
            class="nav-link"
          >
            <span class="link-text">Mis Turnos</span>
            <div class="link-indicator"></div>
          </router-link>
          
          <!-- MIS PEDIDOS -->
          <button 
            v-if="usuarioLogueado" 
            @click="irAPedidos" 
            :class="['nav-link', { active: rutaActual === 'pedidos' }]"
          >
            <span class="link-text">Mis Pedidos</span>
            <div class="link-indicator"></div>
          </button>
        </div>
      </div>
      
      <div class="user-actions-section">
        <div v-if="usuarioLogueado" class="user-profile-wrapper" ref="profileRef">
          
          <div class="user-profile" @click="toggleDropdown" :class="{ 'active': dropdownOpen }">
            <div class="user-info">
              <span class="user-name">{{ usuarioNombre }}</span>
              <span class="user-role">Cliente</span>
            </div>
            <div class="user-avatar">
              <div class="avatar-circle">
                <span class="avatar-initials">{{ avatarInitial }}</span>
              </div>
              <span class="online-indicator"></span>
            </div>
            <span class="dropdown-arrow">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6L8 10L12 6"/></svg>
            </span>
          </div>

          <transition name="dropdown">
            <div v-if="dropdownOpen" class="profile-dropdown">
              <div class="dropdown-header">
                <div class="dropdown-avatar">
                  <div class="avatar-circle-large">{{ avatarInitial }}</div>
                </div>
                <div class="dropdown-user-info">
                  <span class="dropdown-greeting">HOLA,</span>
                  <span class="dropdown-username">{{ usuarioNombre }}</span>
                </div>
              </div>
              
              <div class="dropdown-divider"></div>
              
              <ul class="dropdown-list">
                <button @click="confirmLogout" class="dropdown-item logout">
                  <svg class="item-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>Cerrar Sesión</span>
                </button>
              </ul>
            </div>
          </transition>
        </div>

        <div v-else class="auth-buttons">
          <router-link to="/login" class="auth-btn login-btn">Ingresar</router-link>
          <router-link to="/web/registro" class="auth-btn register-btn">Registrarse</router-link>
        </div>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import Swal from 'sweetalert2';

const router = useRouter();
const route = useRoute();

const usuarioLogueado = ref(false);
const usuarioNombre = ref('');
const usuarioApellido = ref('');
const dropdownOpen = ref(false);
const profileRef = ref(null);

const rutaActual = computed(() => route.query.ver);
const avatarInitial = computed(() => usuarioNombre.value ? usuarioNombre.value.charAt(0).toUpperCase() : 'C');

// Link inteligente para el logo
const homeLink = computed(() => {
  return usuarioLogueado.value 
    ? { name: 'DashboardCliente', query: { ver: 'resumen' } } 
    : '/web/home';
});

const checkAuth = () => {
  const token = localStorage.getItem('token');
  const rol = localStorage.getItem('user_rol');
  if (token && rol === 'CLIENTE') {
    usuarioLogueado.value = true;
    usuarioNombre.value = localStorage.getItem('user_nombre') || 'Cliente';
    usuarioApellido.value = localStorage.getItem('user_apellido') || '';
  } else {
    usuarioLogueado.value = false;
  }
};

const toggleDropdown = () => dropdownOpen.value = !dropdownOpen.value;
const handleClickOutside = (e) => {
  if (profileRef.value && !profileRef.value.contains(e.target)) dropdownOpen.value = false;
};

// --- NAVEGACIÓN ---

const irAInicio = () => {
  dropdownOpen.value = false;
  if (usuarioLogueado.value) {
    // Si es cliente, vamos al Dashboard (Resumen)
    router.push({ name: 'DashboardCliente', query: { ver: 'resumen' } });
  } else {
    // Si es público, al Home
    router.push('/web/home');
  }
};

const irAPedidos = () => {
  dropdownOpen.value = false;
  router.push({ name: 'DashboardCliente', query: { ver: 'pedidos' } });
};

const confirmLogout = () => {
  dropdownOpen.value = false;
  Swal.fire({
    title: '¿Cerrar sesión?',
    text: '¿Estás seguro de que deseas salir?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#6b7280',
    confirmButtonText: 'Sí, cerrar sesión',
    cancelButtonText: 'Cancelar',
    background: '#0f172a',
    color: '#fff',
    customClass: {
      popup: 'swal-popup-dark',
      confirmButton: 'swal-confirm-btn',
      cancelButton: 'swal-cancel-btn'
    }
  }).then((result) => {
    if (result.isConfirmed) {
      logout();
    }
  });
};

const logout = () => {
  localStorage.clear();
  Swal.fire({
    title: 'Sesión cerrada',
    text: 'Has cerrado sesión exitosamente',
    icon: 'success',
    timer: 1500,
    showConfirmButton: false,
    background: '#0f172a',
    color: '#fff'
  }).then(() => {
    window.location.href = '/web/home';
  });
};

onMounted(() => {
  checkAuth();
  document.addEventListener('click', handleClickOutside);
});
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
/* ============================================
   NAVBAR PRINCIPAL
   ============================================ */
.client-nav {
  background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 75px;
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}

/* ============================================
   LOGO
   ============================================ */
.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: transform 0.3s ease;
  padding: 8px 12px;
  border-radius: 12px;
  position: relative;
}

.logo-wrapper::before {
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

.logo-link {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
}

.logo-container {
  width: 46px;
  height: 46px;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  border: 3px solid #3b82f6;
  box-shadow: 
    0 0 20px rgba(59, 130, 246, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  position: relative;
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

.logo-wrapper:hover .logo-container {
  transform: scale(1.05) rotate(5deg);
}

.brand-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-name {
  font-size: 1.35rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
  text-transform: uppercase;
  text-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
}

.brand-subtitle {
  color: #60a5fa;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2.5px;
  text-transform: uppercase;
}

/* ============================================
   NAVEGACIÓN
   ============================================ */
.nav-links-section {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 0 20px;
}

.links-container {
  display: flex;
  gap: 6px;
  background: rgba(30, 41, 59, 0.5);
  padding: 6px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  background: transparent;
  border: none;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.3px;
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
  transition: transform 0.2s ease;
  border-radius: 0 2px 2px 0;
}

.nav-link:hover {
  color: #fff;
  background: rgba(31, 41, 55, 0.8);
}

.nav-link:hover::before {
  transform: scaleY(0.6);
}

.nav-link.router-link-active,
.nav-link.active {
  background: linear-gradient(135deg, rgba(30, 64, 175, 0.4), rgba(59, 130, 246, 0.2));
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.nav-link.active::before,
.nav-link.router-link-active::before {
  transform: scaleY(1);
}

.link-icon {
  stroke: currentColor;
  flex-shrink: 0;
}

.link-indicator {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #3b82f6;
  transition: width 0.3s ease;
  border-radius: 2px;
}

.nav-link.active .link-indicator,
.nav-link.router-link-active .link-indicator {
  width: 50%;
}

/* ============================================
   PERFIL DE USUARIO
   ============================================ */
.user-profile-wrapper {
  position: relative;
}

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
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.user-name {
  color: #d1d5db;
  font-weight: 600;
  font-size: 1.05rem;
  letter-spacing: 0.3px;
}

.user-role {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.2px;
}

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
  background: linear-gradient(135deg, #4f46e5 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.05rem;
  border: 3px solid rgba(139, 92, 246, 0.5);
  box-shadow: 
    0 0 20px rgba(139, 92, 246, 0.4),
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
  background: linear-gradient(45deg, #8b5cf6, #a78bfa);
  z-index: -1;
  opacity: 0.3;
  filter: blur(4px);
}

.user-profile:hover .avatar-circle {
  transform: scale(1.05);
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

.dropdown-arrow svg {
  stroke: currentColor;
}

/* ============================================
   DROPDOWN MEJORADO
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
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
  margin-bottom: 8px;
  position: relative;
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
  background: linear-gradient(135deg, #4f46e5 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.4rem;
  border: 3px solid rgba(139, 92, 246, 0.5);
  box-shadow: 
    0 0 20px rgba(139, 92, 246, 0.4),
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
  background: linear-gradient(45deg, #8b5cf6, #a78bfa);
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

.dropdown-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 16px;
  color: #d1d5db;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
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
  stroke: currentColor;
}

.dropdown-item:hover .item-icon {
  transform: scale(1.1);
}

.dropdown-item.logout {
  color: #ef4444;
  margin-top: 4px;
}

.dropdown-item.logout::before {
  background: #ef4444;
}

.dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* ============================================
   BOTONES DE AUTENTICACIÓN
   ============================================ */
.auth-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.auth-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.3s ease;
  letter-spacing: 0.3px;
  border: 1px solid transparent;
}

.auth-btn svg {
  stroke: currentColor;
  flex-shrink: 0;
}

.login-btn {
  color: #d1d5db;
  border-color: rgba(255, 255, 255, 0.1);
  background: transparent;
}

.login-btn:hover {
  background: rgba(31, 41, 55, 0.8);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.register-btn {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  position: relative;
  overflow: hidden;
}

.register-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.register-btn:hover::before {
  opacity: 1;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

/* ============================================
   ANIMACIONES
   ============================================ */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-15px) scale(0.95);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.97);
}

/* ============================================
   SWEETALERT2 CUSTOM
   ============================================ */
:deep(.swal-popup-dark) {
  border: 1px solid rgba(59, 130, 246, 0.2) !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
}

:deep(.swal-confirm-btn) {
  background: linear-gradient(135deg, #ef4444, #dc2626) !important;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
}

:deep(.swal-confirm-btn:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
}

:deep(.swal-cancel-btn) {
  background: rgba(107, 114, 128, 0.2) !important;
  color: #9ca3af !important;
  border: 1px solid rgba(107, 114, 128, 0.3) !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
}

:deep(.swal-cancel-btn:hover) {
  background: rgba(107, 114, 128, 0.3) !important;
  color: #fff !important;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .nav-links-section {
    display: none;
  }
}

@media (max-width: 768px) {
  .nav-content {
    padding: 0 20px;
  }
  
  .user-info {
    display: none;
  }
  
  .profile-dropdown {
    min-width: 260px;
    right: -8px;
  }

  .auth-btn span {
    display: none;
  }

  .auth-btn {
    padding: 10px 14px;
  }
}

@media (max-width: 480px) {
  .client-nav {
    height: 68px;
  }
  
  .nav-content {
    padding: 0 16px;
  }
  
  .brand-name {
    font-size: 1.2rem;
  }
  
  .logo-container {
    width: 38px;
    height: 38px;
    font-size: 1.1rem;
  }
  
  .user-avatar {
    width: 38px;
    height: 38px;
  }
  
  .profile-dropdown {
    min-width: 240px;
  }
}
</style>