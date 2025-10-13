<template>
  <nav class="navbar">
    <!-- Logo / Nombre -->
    <div class="navbar-left">
      <div class="logo-container">
        <img src="@/assets/logo.jpg" alt="HairSoft Logo" class="logo" />
        <div class="logo-glow"></div>
      </div>
      <span class="brand-name">HairSoft</span>
    </div>

    <!-- Módulos / Menú -->
    <ul :class="['nav-links', { 'open': menuOpen }]">
      <li v-for="modulo in modulos" :key="modulo.name">
        <router-link :to="modulo.path" class="nav-link">
          {{ modulo.name }}
        </router-link>
      </li>
    </ul>

    <!-- Usuario -->
    <div class="navbar-right">
      <div class="user-info">
        <div class="user-avatar-container">
          <img src="@/assets/usuario.png" alt="Usuario" class="user-img" />
          <span class="user-status" :class="{ online: usuario.online }"></span>
        </div>
        <span class="user-name">{{ usuario.nombre }}</span>
      </div>
      <button class="menu-toggle" @click="menuOpen = !menuOpen">
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const menuOpen = ref(false);
const router = useRouter();

const modulos = [
  { name: 'Usuarios', path: '/usuarios' },
  { name: 'Turnos', path: '/turnos' },
  { name: 'Servicios', path: '/servicios' },
  { name: 'Productos', path: '/productos' },
  { name: 'Ventas', path: '/ventas' },
  { name: 'Proveedores', path: '/proveedores' }
];

const usuario = ref({
  nombre: 'Juan Pérez',
  online: true
});
</script>

<style scoped>
/* Navbar principal - Elegante y moderna */
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
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  height: 80px; /* altura fija */
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
  height: 60px;  /* altura deseada del logo */
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

/* Usuario */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  z-index: 2;
}

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

/* Toggle menú mobile */
.menu-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: rgba(0, 153, 255, 0.1);
  border: 1px solid rgba(0, 153, 255, 0.3);
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-toggle:hover {
  background: rgba(0, 153, 255, 0.2);
  transform: scale(1.05);
}

.hamburger-line {
  width: 24px;
  height: 2px;
  background: #ffffff;
  border-radius: 2px;
  transition: all 0.3s ease;
}

/* Responsive */
@media (max-width: 968px) {
  .navbar {
    padding: 1rem 1.5rem;
  }

  .nav-links {
    display: none;
    flex-direction: column;
    width: 100%;
    margin-top: 1rem;
    background: rgba(15, 15, 20, 0.98);
    backdrop-filter: blur(20px);
    padding: 1.5rem;
    border-radius: 16px;
    gap: 0.5rem;
    border: 1px solid rgba(0, 153, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  }

  .nav-links.open {
    display: flex;
    animation: slideDown 0.3s ease;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .menu-toggle {
    display: flex;
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
