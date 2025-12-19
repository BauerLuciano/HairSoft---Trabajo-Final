<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Título Principal -->
      <div class="brand-section">
        <h1 class="app-title">Los Ultimos Serán los primeros</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Acciones del Header -->
      <div class="header-actions">

        <!-- SWITCH MODERNO DE TEMA (sin cambios) -->
        <label class="theme-switch-modern" title="Cambiar tema">
          <input 
            type="checkbox"
            :checked="isDarkTheme"
            @change="toggleTheme"
          />
          <div class="switch-background">
            <!-- Icono Sol -->
            <svg
              height="0"
              width="100"
              viewBox="0 0 24 24"
              data-name="Layer 1"
              id="Layer_1"
              xmlns="http://www.w3.org/2000/svg"
              class="sun-icon"
            >
              <path
                d="M12,17c-2.76,0-5-2.24-5-5s2.24-5,5-5,5,2.24,5,5-2.24,5-5,5ZM13,0h-2V5h2V0Zm0,19h-2v5h2v-5ZM5,11H0v2H5v-2Zm19,0h-5v2h5v-2Zm-2.81-6.78l-1.41-1.41-3.54,3.54,1.41,1.41,3.54-3.54ZM7.76,17.66l-1.41-1.41-3.54,3.54,1.41,1.41,3.54-3.54Zm0-11.31l-3.54-3.54-1.41,1.41,3.54,3.54,1.41-1.41Zm13.44,13.44l-3.54-3.54-1.41,1.41,3.54,3.54,1.41-1.41Z"
              ></path>
            </svg>
            
            <!-- Icono Luna -->
            <svg
              height="512"
              width="512"
              viewBox="0 0 24 24"
              data-name="Layer 1"
              id="Layer_1"
              xmlns="http://www.w3.org/2000/svg"
              class="moon-icon"
            >
              <path
                d="M12.009,24A12.067,12.067,0,0,1,.075,10.725,12.121,12.121,0,0,1,10.1.152a13,13,0,0,1,5.03.206,2.5,2.5,0,0,1,1.8,1.8,2.47,2.47,0,0,1-.7,2.425c-4.559,4.168-4.165,10.645.807,14.412h0a2.5,2.5,0,0,1-.7,4.319A13.875,13.875,0,0,1,12.009,24Zm.074-22a10.776,10.776,0,0,0-1.675.127,10.1,10.1,0,0,0-8.344,8.8A9.928,9.928,0,0,0,4.581,18.7a10.473,10.473,0,0,0,11.093,2.734.5.5,0,0,0,.138-.856h0C9.883,16.1,9.417,8.087,14.865,3.124a.459.459,0,0,0,.127-.465.491.491,0,0,0-.356-.362A10.68,10.68,0,0,0,12.083,2ZM20.5,12a1,1,0,0,1-.97-.757l-.358-1.43L17.74,9.428a1,1,0,0,1,.035-1.94l1.4-.325.351-1.406a1,1,0,0,1,1.94,0l.355,1.418,1.418.355a1,1,0,0,1,0,1.94l-1.418.355-.355,1.418A1,1,0,0,1,20.5,12ZM16,14a1,1,0,0,0,2,0A1,1,0,0,0,16,14Zm6,4a1,1,0,0,0,2,0A1,1,0,0,0,22,18Z"
              ></path>
            </svg>
          </div>
        </label>

        <!-- Perfil de Usuario con Dropdown Mejorado -->
        <div class="user-profile-wrapper" ref="profileRef">
          <div class="user-profile" @click="toggleDropdown" :class="{ 'active': showDropdown }">
            <div class="user-info">
              <span class="user-name">{{ userName }}</span>
              <span class="user-role">{{ formattedRole }}</span>
            </div>
            <div class="user-avatar">
              <div class="avatar-circle">
                <span class="avatar-initials">{{ userInitials }}</span>
              </div>
              <span class="online-indicator"></span>
            </div>
            <span class="dropdown-arrow">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>

          <!-- Menú Desplegable Mejorado -->
          <transition name="dropdown">
            <div v-if="showDropdown" class="profile-dropdown">
              <div class="dropdown-header">
                <div class="dropdown-avatar">
                  <div class="avatar-circle-large">
                    {{ userInitials }}
                  </div>
                </div>
                <div class="dropdown-user-info">
                  <span class="dropdown-greeting">Hola,</span>
                  <span class="dropdown-username">{{ userName }}</span>
                  <span class="dropdown-role">{{ formattedRole }}</span>
                </div>
              </div>
              
              <div class="dropdown-divider"></div>
              
              <button @click="handleLogout" class="dropdown-item logout">
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

      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';
import api from '../services/api';

const router = useRouter();
const isDarkTheme = ref(true);
const showDropdown = ref(false);
const profileRef = ref(null);

// Datos del usuario
const userData = ref({
  id: null,
  rol: null,
  nombre: null,
  apellido: null
});

// Computed
const userInitials = computed(() => {
  const nombre = userData.value.nombre;
  const apellido = userData.value.apellido;
  if (!nombre) return '??';
  const inicialNombre = nombre.charAt(0).toUpperCase();
  const inicialApellido = apellido ? apellido.charAt(0).toUpperCase() : '';
  return inicialNombre + inicialApellido;
});

const userName = computed(() => {
  const nombre = userData.value.nombre;
  const apellido = userData.value.apellido;
  if (!nombre) return 'Usuario';
  return `${nombre} ${apellido || ''}`.trim();
});

const formattedRole = computed(() => {
  const roles = {
    'ADMINISTRADOR': 'Administrador',
    'CLIENTE': 'Cliente', 
    'PELUQUERO': 'Peluquero',
    'RECEPCIONISTA': 'Recepcionista'
  };
  return roles[userData.value.rol] || userData.value.rol || 'Usuario';
});

// Funciones de Carga
const loadCurrentUser = () => {
  userData.value = {
    id: localStorage.getItem('user_id'),
    rol: localStorage.getItem('user_rol'),
    nombre: localStorage.getItem('user_nombre'),
    apellido: localStorage.getItem('user_apellido')
  };
};

// Toggle Dropdown
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

// Cerrar dropdown al hacer click fuera
const handleClickOutside = (event) => {
  if (profileRef.value && !profileRef.value.contains(event.target)) {
    showDropdown.value = false;
  }
};

// Función de Cerrar Sesión
const handleLogout = () => {
  showDropdown.value = false;

  Swal.fire({
    title: '¿Cerrar sesión?',
    text: "¿Estás seguro que deseas salir?",
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, salir',
    cancelButtonText: 'Cancelar',
    background: isDarkTheme.value ? '#1e293b' : '#fff',
    color: isDarkTheme.value ? '#fff' : '#000'
  }).then(async (result) => {
      if (result.isConfirmed) {
        
        // 🔥 CORRECCIÓN AQUÍ: Quitamos el '/api' que sobraba
        try {
          console.log("Intentando notificar logout...");
          // SOLO 'auth/logout/' (sin /api/ al principio porque Axios ya lo pone)
          await api.post('auth/logout/'); 
          console.log("Logout notificado con éxito");
        } catch (error) {
          console.error("❌ Error al avisar al backend:", error);
        }

      // LIMPIEZA LOCAL
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_rol');
      localStorage.removeItem('user_nombre');
      localStorage.removeItem('user_apellido');
      localStorage.removeItem('token'); 
      
      window.dispatchEvent(new Event('userLoggedOut'));
      router.push('/login');

      const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: true
      });
      Toast.fire({
        icon: 'success',
        title: 'Sesión cerrada correctamente'
      });
    }
  });
};

// Event Listeners
const handleStorageChange = (event) => {
  if (['user_id', 'user_rol', 'user_nombre', 'user_apellido'].includes(event.key)) {
    loadCurrentUser();
  }
};

const handleUserChange = () => loadCurrentUser();

// Tema
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

onMounted(() => {
  loadCurrentUser();
  loadSavedTheme();
  window.addEventListener('storage', handleStorageChange);
  window.addEventListener('userChanged', handleUserChange);
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange);
  window.removeEventListener('userChanged', handleUserChange);
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
/* Header Principal - Colores del Sidebar */
.app-header {
  position: sticky;
  top: 0;
  width: 100%;
  background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 32px;
  right: 32px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 100%;
  margin: 0 auto;
  padding: 18px 36px;
  height: 75px;
}

.brand-section {
  flex: 1;
  position: relative;
}

.app-title {
  font-size: 1.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin: 0;
  line-height: 1.2;
  text-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
}

.title-underline {
  position: absolute;
  bottom: -6px;
  left: 0;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, transparent);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.brand-section:hover .title-underline {
  width: 100px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

/* ============================================
   SWITCH MODERNO DE TEMA (sin cambios)
   ============================================ */

.theme-switch-modern {
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
}

.theme-switch-modern input {
  display: none;
}

.switch-background {
  position: relative;
  width: 70px;
  height: 34px;
  background: var(--bg-tertiary);
  border-radius: 50px;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
}

.theme-switch-modern:hover .switch-background {
  border-color: var(--accent-color);
  transform: scale(1.05);
}

.theme-switch-modern input:checked + .switch-background {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
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
   PERFIL Y DROPDOWN - Estilo Sidebar
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

/* Menú Desplegable - Estilo Sidebar */
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

/* Responsive */
@media (max-width: 768px) {
  .user-info {
    display: none;
  }
  
  .header-content {
    padding: 14px 20px;
    height: 68px;
  }
  
  .app-title {
    font-size: 1.5rem;
  }
  
  .header-actions {
    gap: 16px;
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
  }
}

@media (max-width: 480px) {
  .header-actions {
    gap: 12px;
  }
  
  .app-title {
    font-size: 1.2rem;
  }
  
  .header-content {
    padding: 12px 16px;
  }
  
  .user-profile {
    padding: 6px 10px;
  }
  
  .user-avatar {
    width: 38px;
    height: 38px;
  }
  
  .profile-dropdown {
    min-width: 240px;
    right: -8px;
  }
}
</style>