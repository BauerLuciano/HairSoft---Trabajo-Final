<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Título Principal -->
      <div class="brand-section">
        <h1 class="app-title">Los Últimos Serán Los Primeros</h1>
      </div>

      <!-- Acciones del Header -->
      <div class="header-actions">

        <!-- NUEVO SWITCH MODERNO DE TEMA -->
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

        <!-- Perfil de Usuario con Dropdown -->
        <div class="user-profile-wrapper" ref="profileRef">
          <div class="user-profile" @click="toggleDropdown" :class="{ 'active': showDropdown }">
            <div class="user-info">
              <span class="user-name">{{ userName }}</span>
              <span class="user-role">{{ formattedRole }}</span>
            </div>
            <div class="user-avatar">
              <div class="avatar-circle">
                {{ userInitials }}
              </div>
              <span class="online-indicator"></span>
            </div>
            <span class="dropdown-arrow">▼</span>
          </div>

          <!-- Menú Desplegable -->
          <transition name="fade">
            <div v-if="showDropdown" class="profile-dropdown">
              <div class="dropdown-header">
                <span class="dropdown-greeting">Hola,</span>
                <span class="dropdown-username">{{ userName }}</span>
              </div>
              
              <div class="dropdown-divider"></div>
              
              <button @click="handleLogout" class="dropdown-item logout">
                <span class="icon">🚪</span>
                Cerrar Sesión
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
  // Cerrar dropdown
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
  }).then((result) => {
    if (result.isConfirmed) {
      // 1. Limpiar LocalStorage (Auth)
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_rol');
      localStorage.removeItem('user_nombre');
      localStorage.removeItem('user_apellido');
      
      // Nota: No borramos 'theme' para mantener la preferencia del usuario

      // 2. Notificar Logout (opcional, para limpiar estados globales)
      window.dispatchEvent(new Event('userLoggedOut'));

      // 3. Redirigir al Login
      router.push('/login');

      // 4. Toast de despedida
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

.brand-section { flex: 1; }

.app-title {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* ============================================
   NUEVO SWITCH MODERNO DE TEMA
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

/* Efecto de switch deslizante */
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
   PERFIL Y DROPDOWN (MANTENIDO)
   ============================================ */

.user-profile-wrapper {
  position: relative;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.user-profile:hover, .user-profile.active {
  background: var(--hover-bg);
  border-color: var(--border-color);
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
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.user-avatar {
  position: relative;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.avatar-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1rem;
  border: 2px solid var(--border-color);
}

.online-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  background: #22c55e;
  border: 2px solid var(--bg-secondary);
  border-radius: 50%;
}

.dropdown-arrow {
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-left: 4px;
  transition: transform 0.3s ease;
}

.user-profile.active .dropdown-arrow {
  transform: rotate(180deg);
}

/* Estilos del Menú Desplegable */
.profile-dropdown {
  position: absolute;
  top: 120%;
  right: 0;
  width: 220px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  padding: 8px;
  z-index: 1001;
  transform-origin: top right;
}

.dropdown-header {
  padding: 12px 16px;
}

.dropdown-greeting {
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.dropdown-username {
  display: block;
  font-weight: 700;
  color: var(--text-primary);
  font-size: 1rem;
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
  margin: 8px 0;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.95rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: var(--hover-bg);
}

.dropdown-item.logout {
  color: #ef4444;
}

.dropdown-item.logout:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* Animación de entrada */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 768px) {
  .user-info { display: none; }
  .header-content { padding: 12px 16px; }
  
  /* Ajuste del switch en móvil */
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
}

@media (max-width: 480px) {
  .header-actions {
    gap: 12px;
  }
  
  .app-title {
    font-size: 1.2rem;
  }
}
</style>