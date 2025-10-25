<template>
  <nav class="sidebar">
    <!-- Header del Sidebar -->
    <div class="sidebar-header">
      <div class="logo-wrapper">
        <div class="logo-container">
          <img :src="logo" alt="HairSoft Logo" class="logo" />
        </div>
        <div class="brand-info">
          <span class="brand-name">HairSoft</span>
          <span class="brand-tagline">Pro Studio</span>
        </div>
      </div>
    </div>

    <!-- Navegación Principal -->
    <div class="nav-section">
      <span class="section-title">MENÚ PRINCIPAL</span>
      <ul class="nav-links">
        <li v-for="modulo in modulosConIcono" :key="modulo.name">
          <router-link :to="modulo.path" class="nav-link">
            <div class="link-content">
              <div class="icon-wrapper">
                <i :class="['icon', modulo.icon]"></i>
              </div>
              <span class="link-text">{{ modulo.name }}</span>
            </div>
            <div class="link-indicator"></div>
          </router-link>
        </li>
      </ul>
    </div>

    <!-- Footer del Sidebar (opcional) -->
    <div class="sidebar-footer">
      <div class="footer-card">
        <div class="footer-icon">
          <i class="ri-lightbulb-flash-line"></i>
        </div>
        <div class="footer-content">
          <p class="footer-title">¿Necesitás ayuda?</p>
          <p class="footer-text">Consultá nuestra guía</p>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import logo from '@/assets/logo.jpg';

const modulosConIcono = [
  { name: 'Dashboard', path: '/dashboard', icon: 'ri-dashboard-line' },
  { name: 'Usuarios', path: '/usuarios', icon: 'ri-team-line' },
  { name: 'Turnos', path: '/turnos', icon: 'ri-calendar-event-line' },
  { name: 'Servicios', path: '/servicios', icon: 'ri-scissors-line' },
  { name: 'Productos', path: '/productos', icon: 'ri-shopping-bag-line' },
  { name: 'Ventas', path: '/ventas', icon: 'ri-bar-chart-2-line' },
  { name: 'Proveedores', path: '/proveedores', icon: 'ri-truck-line' },
  { name: 'Categorías', path: '/categorias', icon: 'ri-list-settings-line' },
  { name: 'Roles', path: '/roles', icon: 'ri-shield-user-line' },
];
</script>

<style scoped>
/* Sidebar Principal */
.sidebar {
  width: 280px;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.08);
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  overflow-x: hidden;
}

/* Scrollbar personalizado */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Header del Sidebar */
.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-container {
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
  transition: all 0.3s ease;
}

.logo-container:hover {
  transform: translateY(-2px) rotate(5deg);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
}

.logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 2px solid var(--accent-color);
}

.brand-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-name {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -0.5px;
}

.brand-tagline {
  font-size: 0.75rem;
  color: var(--accent-color);
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}

/* Sección de Navegación */
.nav-section {
  flex: 1;
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 1.2px;
  text-transform: uppercase;
  padding: 0 12px;
  margin-bottom: 8px;
  opacity: 0.7;
}

/* Lista de Links */
.nav-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-links li {
  position: relative;
}

/* Link Individual */
.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-decoration: none;
  padding: 12px 12px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.link-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  z-index: 2;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: var(--bg-primary);
  border-radius: 10px;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.icon {
  font-size: 1.2rem;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.link-text {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.link-indicator {
  width: 0;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  background: var(--accent-color);
  border-radius: 0 4px 4px 0;
  transition: width 0.3s ease;
  z-index: 1;
}

/* Hover State */
.nav-link:hover {
  background: var(--hover-bg);
  transform: translateX(4px);
}

.nav-link:hover .icon-wrapper {
  background: linear-gradient(135deg, var(--accent-color), #8b5cf6);
  border-color: transparent;
  transform: scale(1.05);
}

.nav-link:hover .icon {
  color: #ffffff;
  transform: scale(1.1);
}

.nav-link:hover .link-text {
  color: var(--text-primary);
  font-weight: 600;
}

.nav-link:hover .link-indicator {
  width: 4px;
}

/* Active State (Router Link Activo) */
.nav-link.router-link-active {
  background: linear-gradient(135deg, var(--accent-color), #8b5cf6);
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3);
  transform: translateX(4px);
}

.nav-link.router-link-active .icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-link.router-link-active .icon {
  color: #ffffff;
  transform: scale(1.1);
}

.nav-link.router-link-active .link-text {
  color: #ffffff;
  font-weight: 700;
}

.nav-link.router-link-active .link-indicator {
  width: 4px;
  background: #ffffff;
}

/* Footer del Sidebar */
.sidebar-footer {
  padding: 16px 20px 24px;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
}

.footer-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.footer-card:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.08));
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
}

.footer-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--accent-color);
  border-radius: 8px;
  flex-shrink: 0;
}

.footer-icon i {
  font-size: 16px;
  color: #ffffff;
}

.footer-content {
  flex: 1;
}

.footer-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 2px 0;
  line-height: 1.2;
}

.footer-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.3;
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar {
    width: 260px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -280px;
    width: 280px;
    z-index: 1001;
  }

  .sidebar.active {
    left: 0;
  }
}
</style>