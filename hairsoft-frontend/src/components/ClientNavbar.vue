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
          <button 
            @click="irAInicio" 
            :class="['nav-link', { active: isActiveLink('inicio') }]"
          >
            <span class="link-text">Inicio</span>
            <div class="link-indicator"></div>
          </button>
          
          <router-link 
            to="/web/servicios" 
            :class="['nav-link', { active: isActiveLink('servicios') }]"
          >
            <span class="link-text">Servicios</span>
            <div class="link-indicator"></div>
          </router-link>
          
          <router-link 
            :to="{ name: 'ProductosPublico' }" 
            :class="['nav-link', { active: isActiveLink('productos') }]"
          >
            <span class="link-text">Productos</span>
            <div class="link-indicator"></div>
          </router-link>

          <router-link 
            v-if="cartStore.cantidadTotal > 0"
            to="/checkout" 
            :class="['nav-link', { active: isActiveLink('checkout') }]"
            title="Ver mi carrito"
          >
            <div style="position: relative; display: flex; align-items: center;">
              <ShoppingBag :size="20" />
              <span class="cart-badge">{{ cartStore.cantidadTotal }}</span>
            </div>
            <span class="link-text" style="margin-left: 6px;">Carrito</span>
            <div class="link-indicator"></div>
          </router-link>
          
          <router-link 
            v-if="usuarioLogueado" 
            :to="{ name: 'HistorialTurnos' }" 
            :class="['nav-link', { active: isActiveLink('turnos') }]"
          >
            <span class="link-text">Mis Turnos</span>
            <div class="link-indicator"></div>
          </router-link>
          
          <button 
            v-if="usuarioLogueado" 
            @click="irAPedidos" 
            :class="['nav-link', { active: isActiveLink('pedidos') }]"
          >
            <span class="link-text">Mis Pedidos</span>
            <div class="link-indicator"></div>
          </button>
        </div>
      </div>
      
      <div class="user-actions-section">
        
        <label class="theme-switch-modern" title="Cambiar tema">
          <input 
            type="checkbox"
            :checked="isDarkTheme"
            @change="toggleTheme"
          />
          <div class="switch-background">
            <svg
              height="0"
              width="100"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
              class="sun-icon"
            >
              <path d="M12,17c-2.76,0-5-2.24-5-5s2.24-5,5-5,5,2.24,5,5-2.24,5-5,5ZM13,0h-2V5h2V0Zm0,19h-2v5h2v-5ZM5,11H0v2H5v-2Zm19,0h-5v2h5v-2Zm-2.81-6.78l-1.41-1.41-3.54,3.54,1.41,1.41,3.54-3.54ZM7.76,17.66l-1.41-1.41-3.54,3.54,1.41,1.41,3.54-3.54Zm0-11.31l-3.54-3.54-1.41,1.41,3.54,3.54,1.41-1.41Zm13.44,13.44l-3.54-3.54-1.41,1.41,3.54,3.54,1.41-1.41Z"></path>
            </svg>
            <svg
              height="512"
              width="512"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
              class="moon-icon"
            >
              <path d="M12.009,24A12.067,12.067,0,0,1,.075,10.725,12.121,12.121,0,0,1,10.1.152a13,13,0,0,1,5.03.206,2.5,2.5,0,0,1,1.8,1.8,2.47,2.47,0,0,1-.7,2.425c-4.559,4.168-4.165,10.645.807,14.412h0a2.5,2.5,0,0,1-.7,4.319A13.875,13.875,0,0,1,12.009,24Zm.074-22a10.776,10.776,0,0,0-1.675.127,10.1,10.1,0,0,0-8.344,8.8A9.928,9.928,0,0,0,4.581,18.7a10.473,10.473,0,0,0,11.093,2.734.5.5,0,0,0,.138-.856h0C9.883,16.1,9.417,8.087,14.865,3.124a.459.459,0,0,0,.127-.465.491.491,0,0,0-.356-.362A10.68,10.68,0,0,0,12.083,2ZM20.5,12a1,1,0,0,1-.97-.757l-.358-1.43L17.74,9.428a1,1,0,0,1,.035-1.94l1.4-.325.351-1.406a1,1,0,0,1,1.94,0l.355,1.418,1.418.355a1,1,0,0,1,0,1.94l-1.418.355-.355,1.418A1,1,0,0,1,20.5,12ZM16,14a1,1,0,0,0,2,0A1,1,0,0,0,16,14Zm6,4a1,1,0,0,0,2,0A1,1,0,0,0,22,18Z"></path>
            </svg>
          </div>
        </label>

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
import { ShoppingBag } from 'lucide-vue-next';

// IMPORTAMOS TU STORE DE PINIA (cart.js)
import { useCartStore } from '@/stores/cart';

const router = useRouter();
const route = useRoute();

// INICIALIZAMOS EL STORE
const cartStore = useCartStore();

const usuarioLogueado = ref(false);
const usuarioNombre = ref('');
const usuarioApellido = ref('');
const dropdownOpen = ref(false);
const profileRef = ref(null);
const isDarkTheme = ref(true);

// Calculamos inicial
const avatarInitial = computed(() => usuarioNombre.value ? usuarioNombre.value.charAt(0).toUpperCase() : 'C');

// Link inteligente para el logo
const homeLink = computed(() => {
  return usuarioLogueado.value 
    ? { name: 'DashboardCliente', query: { ver: 'resumen' } } 
    : '/web/home';
});

// Función para detectar link activo
const isActiveLink = (linkName) => {
  const currentPath = route.path;
  const currentQuery = route.query.ver;
  
  switch(linkName) {
    case 'inicio':
      if (usuarioLogueado.value) {
        return (currentPath.includes('dashboard') || currentPath.includes('cliente')) && 
               (!currentQuery || currentQuery === 'resumen');
      } else {
        return currentPath === '/web/home' || currentPath === '/';
      }
    case 'servicios': return currentPath.includes('/web/servicios');
    case 'productos': 
      return currentPath.includes('/web/productos') || 
             currentPath.includes('/productos') ||
             route.name === 'ProductosPublico';
    
    // ✅ CASO CHECKOUT
    case 'checkout': return currentPath.includes('/checkout');
      
    case 'turnos': 
      return currentPath.includes('/historial') || 
             currentPath.includes('/turnos') ||
             route.name === 'HistorialTurnos';
    case 'pedidos':
      return route.name === 'MisPedidos' || currentPath.includes('mis-pedidos');
  }
};

// Check Auth
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

// --- TEMA ---
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

const loadSavedTheme = () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    isDarkTheme.value = false;
    document.documentElement.classList.add('light-theme');
  } else {
    isDarkTheme.value = true;
    document.documentElement.classList.remove('light-theme');
  }
};

// --- NAVEGACIÓN ---
const irAInicio = () => {
  dropdownOpen.value = false;
  if (usuarioLogueado.value) {
    router.push({ name: 'DashboardCliente', query: { ver: 'resumen' } });
  } else {
    router.push('/web/home');
  }
};

const irAPedidos = () => {
  dropdownOpen.value = false;
  router.push({ name: 'MisPedidos' });
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
    background: isDarkTheme.value ? '#0f172a' : '#fff',
    color: isDarkTheme.value ? '#fff' : '#000',
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
  cartStore.limpiarCarrito(); // Limpiamos el carrito al salir usando la acción del store
  Swal.fire({
    title: 'Sesión cerrada',
    text: 'Has cerrado sesión exitosamente',
    icon: 'success',
    timer: 1500,
    showConfirmButton: false,
    background: isDarkTheme.value ? '#0f172a' : '#fff',
    color: isDarkTheme.value ? '#fff' : '#000'
  }).then(() => {
    window.location.href = '/web/home';
  });
};

onMounted(() => {
  checkAuth();
  loadSavedTheme();
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('userChanged', checkAuth);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('userChanged', checkAuth);
});
</script>

<style scoped>
/* ============================================
   NAVBAR PRINCIPAL - MODO OSCURO
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
   MODO CLARO - NAVBAR
   ============================================ */
:root.light-theme .client-nav {
  background: rgba(255, 255, 255, 0.95); /* Fondo blanco casi sólido */
  backdrop-filter: blur(10px); /* Efecto vidrio */
  border-bottom: 1px solid rgba(226, 232, 240, 0.8); /* Borde gris muy suave */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); /* Sombra sutil y elegante */
}

:root.light-theme .client-nav::after {
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent); /* Línea decorativa sutil */
}

/* LOGO MODO CLARO */
:root.light-theme .brand-name {
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%); /* Texto oscuro con gradiente */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: none; /* Quitamos sombra para limpieza */
}

:root.light-theme .brand-subtitle {
  color: #2563eb; /* Azul corporativo */
}

/* LINKS DE NAVEGACIÓN MODO CLARO */
:root.light-theme .links-container {
  background: #f1f5f9; /* Fondo gris muy claro para el contenedor de links */
  border: 1px solid #e2e8f0;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
}

:root.light-theme .nav-link {
  color: #64748b; /* Gris medio para texto */
}

:root.light-theme .nav-link:hover {
  color: #1e293b; /* Texto oscuro al hover */
  background: #ffffff; /* Fondo blanco al hover */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* Sombrita al hover */
}

/* LINK ACTIVO MODO CLARO */
:root.light-theme .nav-link.active {
  background: #ffffff;
  color: #2563eb; /* Azul activo */
  border-color: #bfdbfe; /* Borde azul muy claro */
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
}

/* PERFIL Y ACCIONES MODO CLARO */
:root.light-theme .switch-background {
  background: #e2e8f0;
  border-color: #cbd5e1;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}

:root.light-theme .user-profile:hover,
:root.light-theme .user-profile.active {
  background: #f8fafc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0; /* Borde sutil al hover */
}

:root.light-theme .user-name {
  color: #1e293b;
  font-weight: 700;
}

:root.light-theme .user-role {
  color: #64748b;
}

/* DROPDOWN MODO CLARO */
:root.light-theme .profile-dropdown {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 
    0 10px 15px -3px rgba(0, 0, 0, 0.1), 
    0 4px 6px -2px rgba(0, 0, 0, 0.05); /* Sombra elevada */
}

:root.light-theme .dropdown-header {
  border-bottom: 1px solid #f1f5f9;
  background-color: #f8fafc; /* Cabecera del dropdown ligeramente gris */
}

:root.light-theme .dropdown-username {
  background: none;
  -webkit-text-fill-color: initial;
  color: #1e293b;
}

:root.light-theme .dropdown-item {
  color: #475569;
}

:root.light-theme .dropdown-item:hover {
  background: #f1f5f9;
  color: #1e293b;
  box-shadow: none; /* Quitamos sombra interna para limpieza */
}

/* BOTONES AUTH MODO CLARO */
:root.light-theme .login-btn {
  color: #475569;
  border: 1px solid #cbd5e1;
}

:root.light-theme .login-btn:hover {
  background: #f1f5f9;
  color: #1e293b;
  border-color: #94a3b8;
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

:root.light-theme .brand-name {
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 8px rgba(100, 116, 139, 0.15);
}

.brand-subtitle {
  color: #60a5fa;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2.5px;
  text-transform: uppercase;
}

:root.light-theme .brand-subtitle {
  color: #3b82f6;
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

:root.light-theme .links-container {
  background: rgba(248, 250, 252, 0.9);
  border-color: rgba(203, 213, 225, 0.4);
  box-shadow: inset 0 2px 4px rgba(100, 116, 139, 0.05);
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

:root.light-theme .nav-link {
  color: #475569;
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

:root.light-theme .nav-link:hover {
  color: #0f172a;
  background: rgba(248, 250, 252, 0.95);
}

.nav-link:hover::before {
  transform: scaleY(0.6);
}

/* 🎯 ESTADO ACTIVO CORREGIDO */
.nav-link.active {
  background: linear-gradient(135deg, rgba(30, 64, 175, 0.4), rgba(59, 130, 246, 0.2));
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

:root.light-theme .nav-link.active {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(96, 165, 250, 0.05));
  color: #1e40af;
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.nav-link.active::before {
  transform: scaleY(1);
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

.nav-link.active .link-indicator {
  width: 50%;
}

/* CART BADGE */
.cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #ef4444;
  color: white;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 50px;
  border: 2px solid #1e293b;
  min-width: 14px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
}

:root.light-theme .cart-badge {
  border-color: #ffffff;
}

/* ============================================
   SWITCH DE TEMA
   ============================================ */
.theme-switch-modern {
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  margin-right: 12px;
}

.theme-switch-modern input {
  display: none;
}

.switch-background {
  position: relative;
  width: 70px;
  height: 34px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 50px;
  border: 2px solid rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
}

:root.light-theme .switch-background {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.theme-switch-modern:hover .switch-background {
  border-color: #3b82f6;
  transform: scale(1.05);
}

.theme-switch-modern input:checked + .switch-background {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
}

:root.light-theme .theme-switch-modern input:checked + .switch-background {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.sun-icon,
.moon-icon {
  width: 18px;
  height: 18px;
  transition: all 0.3s ease;
  z-index: 2;
}

.sun-icon {
  fill: #f59e0b;
  opacity: 1;
}

.moon-icon {
  fill: #94a3b8;
  opacity: 0.7;
}

.theme-switch-modern input:checked + .switch-background .sun-icon {
  opacity: 0.7;
  fill: #94a3b8;
}

.theme-switch-modern input:checked + .switch-background .moon-icon {
  opacity: 1;
  fill: #e2e8f0;
}

:root.light-theme .theme-switch-modern input:checked + .switch-background .moon-icon {
  fill: #1e293b;
}

.switch-background::before {
  content: '';
  position: absolute;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  left: 4px;
  top: 50%;
  transform: translateY(-50%);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.theme-switch-modern input:checked + .switch-background::before {
  left: calc(100% - 30px);
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  box-shadow: 0 2px 8px rgba(148, 163, 184, 0.3);
}

/* ============================================
   PERFIL DE USUARIO
   ============================================ */
.user-profile-wrapper {
  position: relative;
}

.user-actions-section {
  display: flex;
  align-items: center;
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

:root.light-theme .user-profile:hover,
:root.light-theme .user-profile.active {
  background: rgba(248, 250, 252, 0.95);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.12);
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

:root.light-theme .user-name {
  color: #0f172a;
}

.user-role {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.2px;
}

:root.light-theme .user-role {
  color: #64748b;
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

:root.light-theme .online-indicator {
  border-color: #ffffff;
}

.dropdown-arrow {
  display: flex;
  align-items: center;
  color: #9ca3af;
  margin-left: 2px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:root.light-theme .dropdown-arrow {
  color: #64748b;
}

.user-profile.active .dropdown-arrow {
  transform: rotate(180deg);
  color: #60a5fa;
}

:root.light-theme .user-profile.active .dropdown-arrow {
  color: #3b82f6;
}

/* ============================================
   DROPDOWN
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

:root.light-theme .profile-dropdown {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid rgba(203, 213, 225, 0.5);
  box-shadow: 
    0 20px 40px rgba(100, 116, 139, 0.15),
    0 4px 12px rgba(100, 116, 139, 0.08);
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

:root.light-theme .dropdown-header {
  border-bottom: 1px solid rgba(203, 213, 225, 0.4);
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

:root.light-theme .dropdown-header::after {
  background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
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

:root.light-theme .dropdown-greeting {
  color: #64748b;
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

:root.light-theme .dropdown-username {
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dropdown-divider {
  height: 1px;
  background: rgba(59, 130, 246, 0.1);
  margin: 8px 0;
}

:root.light-theme .dropdown-divider {
  background: rgba(203, 213, 225, 0.4);
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

:root.light-theme .dropdown-item {
  color: #1e293b;
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

:root.light-theme .dropdown-item:hover {
  background: rgba(248, 250, 252, 0.95);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.1);
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

:root.light-theme .dropdown-item.logout {
  color: #dc2626;
}

.dropdown-item.logout::before {
  background: #ef4444;
}

:root.light-theme .dropdown-item.logout::before {
  background: #dc2626;
}

.dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.1);
}

:root.light-theme .dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.08);
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

.login-btn {
  color: #d1d5db;
  border-color: rgba(255, 255, 255, 0.1);
  background: transparent;
}

:root.light-theme .login-btn {
  color: #475569;
  border-color: rgba(100, 116, 139, 0.2);
}

.login-btn:hover {
  background: rgba(31, 41, 55, 0.8);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

:root.light-theme .login-btn:hover {
  background: rgba(248, 250, 252, 0.95);
  color: #0f172a;
  border-color: rgba(100, 116, 139, 0.3);
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
  
  .theme-switch-modern .switch-background {
    width: 60px;
    height: 30px;
  }
  
  .sun-icon,
  .moon-icon {
    width: 16px;
    height: 16px;
  }
  
  .switch-background::before {
    width: 22px;
    height: 22px;
  }
  
  .theme-switch-modern input:checked + .switch-background::before {
    left: calc(100% - 26px);
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