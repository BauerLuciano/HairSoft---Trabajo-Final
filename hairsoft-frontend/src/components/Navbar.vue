<template>
  <nav class="navbar">
    <!-- Logo / Nombre -->
    <div class="navbar-left">
      <div class="logo-container">
        <img :src="logo" alt="HairSoft Logo" class="logo" />
        <div class="logo-glow"></div>
      </div>
      <span class="brand-name">HairSoft</span>
    </div>

    <!-- Módulos / Menú -->
    <ul class="nav-links">
      <li v-for="modulo in modulos" :key="modulo.name">
        <router-link :to="modulo.path" class="nav-link">
          {{ modulo.name }}
        </router-link>
      </li>
    </ul>

    <!-- Usuario y Tema -->
    <div class="navbar-right">
      <!-- Switch de tema -->
      <div class="theme-toggle">
        <label class="switch" for="themeSwitch">
          <input 
            id="themeSwitch" 
            type="checkbox" 
            class="circle" 
            v-model="isLightMode"
            @change="toggleTheme"
          />
          <svg
            viewBox="0 0 384 512"
            xmlns="http://www.w3.org/2000/svg"
            class="moon svg"
          >
            <path
              d="M223.5 32C100 32 0 132.3 0 256S100 480 223.5 480c60.6 0 115.5-24.2 155.8-63.4c5-4.9 6.3-12.5 3.1-18.7s-10.1-9.7-17-8.5c-9.8 1.7-19.8 2.6-30.1 2.6c-96.9 0-175.5-78.8-175.5-176c0-65.8 36-123.1 89.3-153.3c6.1-3.5 9.2-10.5 7.7-17.3s-7.3-11.9-14.3-12.5c-6.3-.5-12.6-.8-19-.8z"
            ></path>
          </svg>
          <div class="sun svg">
            <span class="dot"></span>
          </div>
        </label>
      </div>

      <!-- Usuario -->
      <div class="user-info">
        <div class="user-avatar-container">
          <img :src="usuarioImg" alt="Usuario" class="user-img" />
          <span class="user-status" :class="{ online: usuario.online }"></span>
        </div>
        <span class="user-name">{{ usuario.nombre }}</span>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import logo from '@/assets/logo.jpg';
import usuarioImg from '@/assets/usuario.png';

const router = useRouter();

const modulos = [
  { name: 'Usuarios', path: '/usuarios' },
  { name: 'Turnos', path: '/turnos' },
  { name: 'Servicios', path: '/servicios' },
  { name: 'Productos', path: '/productos' },
  { name: 'Ventas', path: '/ventas' },
  { name: 'Proveedores', path: '/proveedores' },
  { name: 'Categorías', path: '/categorias' },
  { name: 'Roles', path: '/roles' }
];

const usuario = ref({
  nombre: 'Juan Pérez',
  online: true
});

// Tema - FALSE = oscuro (default), TRUE = claro
const isLightMode = ref(false);

const toggleTheme = () => {
  if (isLightMode.value) {
    // Modo claro activado
    document.body.classList.add('light-mode');
    localStorage.setItem('theme', 'light');
  } else {
    // Modo oscuro activado
    document.body.classList.remove('light-mode');
    localStorage.setItem('theme', 'dark');
  }
};

// Cargar tema guardado al montar
onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    isLightMode.value = true;
    document.body.classList.add('light-mode');
  }
});
</script>


<style scoped>
/* Navbar principal - SIEMPRE OSCURO (no cambia con el tema) */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0rem 3rem;
  background: linear-gradient(135deg, rgba(10, 10, 15, 0.95) 0%, rgba(20, 20, 30, 0.95) 100%);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 2px solid rgba(0, 153, 255, 0.2);
  color: #ffffff;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8), 0 0 80px rgba(0, 153, 255, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  flex-wrap: wrap;
  height: 80px;
}

.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(0, 153, 255, 0.05) 50%, 
    transparent 100%);
  pointer-events: none;
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

/* Logo y nombre */
.navbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 2;
}

.logo-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  width: 60px;
  flex-shrink: 0;
}

.logo {
  max-height: 100%;
  max-width: 100%;
  border-radius: 14px;
  object-fit: cover;
  box-shadow: 0 4px 20px rgba(0, 153, 255, 0.5);
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
  border: 2px solid rgba(0, 153, 255, 0.3);
}

.logo-container:hover .logo {
  transform: scale(1.05) rotate(5deg);
  box-shadow: 0 6px 28px rgba(0, 153, 255, 0.7);
}

.logo-glow {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 14px;
  background: radial-gradient(circle, rgba(0, 153, 255, 0.4) 0%, transparent 70%);
  filter: blur(10px);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.brand-name {
  font-size: 1.9rem;
  font-weight: 900;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 50%, #7b2cbf 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
  text-shadow: 0 0 30px rgba(0, 153, 255, 0.5);
  position: relative;
}

/* Módulos / links */
.nav-links {
  display: flex;
  list-style: none;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
  z-index: 2;
}

.nav-links li {
  position: relative;
}

.nav-link {
  display: block;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
  padding: 10px 20px;
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  letter-spacing: 0.3px;
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 153, 255, 0.2) 0%, rgba(123, 44, 191, 0.2) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 14px;
}

.nav-link:hover::before {
  opacity: 1;
}

.nav-link:hover {
  color: #00d4ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 153, 255, 0.3);
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, rgba(0, 153, 255, 0.25) 0%, rgba(123, 44, 191, 0.25) 100%);
  color: #00d4ff;
  box-shadow: 0 0 20px rgba(0, 153, 255, 0.4);
}

/* Usuario y tema */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  z-index: 2;
}

/* ESTILOS DEL SWITCH DE TEMA */
.theme-toggle {
  display: flex;
  align-items: center;
}

.switch {
  --transition: 300ms;
  --transition500: 500ms;
  --color-dark: #0c0f14;
  --color-darkGray: #21262e;
  --color-gray: #52555a;
  --color-offwhite: #cecece;
  --shadow-color: var(--color-dark);
  position: relative;
  display: flex;
  align-items: center;
  width: 60px;
  height: fit-content;
  background-color: var(--color-dark);
  border-radius: 30px;
  padding: 4px;
  transition: var(--transition500);
  user-select: none;
  cursor: pointer;
  overflow: hidden;
}

.switch .svg {
  transition: var(--transition);
  position: absolute;
  left: 5px;
}

.switch .moon {
  width: 18px;
  fill: var(--color-gray);
  opacity: 1;
}

.switch .sun {
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  border-radius: 50%;
  left: calc(100% - 21.5px);
  top: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  scale: 0.8;
  opacity: 0;
}

.switch .sun .dot {
  position: relative;
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-dark);
  background: white;
  z-index: 1;
  box-shadow: 11px 0px 0px var(--shadow-color),
    10.3px 0px 0px var(--shadow-color), -11px 0px 0px var(--shadow-color),
    -10.3px 0px 0px var(--shadow-color), 0px -11px 0px var(--shadow-color),
    0px -10.3px 0px var(--shadow-color), 0px 11px 0px var(--shadow-color),
    0px 10.3px 0px var(--shadow-color), 8px 8px 0px var(--shadow-color),
    7.3px 7.3px 0px var(--shadow-color), 8px -8px 0px var(--shadow-color),
    7.3px -7.3px 0px var(--shadow-color), -8px -8px 0px var(--shadow-color),
    -7.3px -7.3px 0px var(--shadow-color), -8px 8px 0px var(--shadow-color),
    -7.3px 7.3px 0px var(--shadow-color);
}

.switch .sun .dot::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: white;
  border: 2px solid var(--color-dark);
}

.switch .circle {
  appearance: none;
  position: relative;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  left: 0;
  background-color: var(--color-darkGray);
  border: 1px solid var(--color-darkGray);
  transition: var(--transition500);
  box-shadow: 1px 1px 20px 3px var(--color-darkGray);
  cursor: pointer;
}

.switch:has(.circle:checked) {
  background: var(--color-offwhite);
}

.switch .circle:hover {
  margin-left: 3px;
}

.switch .circle:checked:hover {
  margin-left: -3px;
}

.switch .circle:checked {
  left: calc(100% - 24px);
  background: white;
  border-color: white;
  box-shadow: 1px 1px 30px 12px white;
}

.switch:has(.circle:checked) > .sun {
  opacity: 1;
}

.switch:has(.circle:checked) > .moon {
  opacity: 0;
}

/* Usuario */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 153, 255, 0.3);
  box-shadow: 0 4px 16px rgba(0, 153, 255, 0.2);
}

.user-avatar-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-img {
  height: 42px;
  width: 42px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 2px 12px rgba(0, 153, 255, 0.4);
  border: 2px solid rgba(0, 153, 255, 0.5);
  transition: all 0.3s ease;
}

.user-info:hover .user-img {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 153, 255, 0.6);
}

.user-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: #6c757d;
  border: 2px solid rgba(10, 10, 15, 0.95);
  transition: all 0.3s ease;
}

.user-status.online {
  background-color: #00ff88;
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.6);
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { box-shadow: 0 0 8px rgba(0, 255, 136, 0.4); }
  50% { box-shadow: 0 0 16px rgba(0, 255, 136, 0.8); }
}

.user-name {
  font-weight: 700;
  font-size: 15px;
  color: #ffffff;
  letter-spacing: 0.3px;
}

/* Responsive */
@media (max-width: 968px) {
  .navbar {
    padding: 1rem 1.5rem;
  }

  .brand-name {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0.75rem 1rem;
  }

  .user-name {
    display: none;
  }

  .brand-name {
    font-size: 1.3rem;
  }
}
</style>