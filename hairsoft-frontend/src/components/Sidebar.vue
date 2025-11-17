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
        </div>
      </div>
    </div>

    <!-- Navegación Principal -->
    <div class="nav-section">
      <span class="section-title">MENÚ PRINCIPAL</span>
      
      <!-- Dashboard - Siempre visible -->
      <ul class="nav-links">
        <li>
          <router-link to="/dashboard" class="nav-link">
            <div class="link-content">
              <div class="icon-wrapper">
                <i class="icon ri-dashboard-line"></i>
              </div>
              <span class="link-text">Dashboard</span>
            </div>
            <div class="link-indicator"></div>
          </router-link>
        </li>
      </ul>

      <!-- Acordeón: Gestión Comercial -->
      <div class="acordeon-section">
        <div class="acordeon-header" @click="toggleSection('comercial')">
          <div class="acordeon-header-content">
            <div class="acordeon-icon-wrapper">
              <i class="ri-store-2-line acordeon-icon"></i>
            </div>
            <span class="acordeon-title">Gestión Comercial</span>
          </div>
          <i 
            class="ri-arrow-down-s-line acordeon-arrow"
            :class="{ 'rotated': openSection === 'comercial' }"
          ></i>
        </div>
        <div class="acordeon-content" :class="{ 'open': openSection === 'comercial' }">
          <ul class="nav-links acordeon-items">
            <li v-for="item in menuSections.comercial" :key="item.path">
              <router-link :to="item.path" class="nav-link acordeon-item">
                <div class="link-content">
                  <div class="icon-wrapper">
                    <i :class="['icon', item.icon]"></i>
                  </div>
                  <span class="link-text">{{ item.name }}</span>
                </div>
                <div class="link-indicator"></div>
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- Acordeón: Inventario -->
      <div class="acordeon-section">
        <div class="acordeon-header" @click="toggleSection('inventario')">
          <div class="acordeon-header-content">
            <div class="acordeon-icon-wrapper">
              <i class="ri-archive-line acordeon-icon"></i>
            </div>
            <span class="acordeon-title">Inventario</span>
          </div>
          <i 
            class="ri-arrow-down-s-line acordeon-arrow"
            :class="{ 'rotated': openSection === 'inventario' }"
          ></i>
        </div>
        <div class="acordeon-content" :class="{ 'open': openSection === 'inventario' }">
          <ul class="nav-links acordeon-items">
            <li v-for="item in menuSections.inventario" :key="item.path">
              <router-link :to="item.path" class="nav-link acordeon-item">
                <div class="link-content">
                  <div class="icon-wrapper">
                    <i :class="['icon', item.icon]"></i>
                  </div>
                  <span class="link-text">{{ item.name }}</span>
                </div>
                <div class="link-indicator"></div>
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- Acordeón: Administración -->
      <div class="acordeon-section">
        <div class="acordeon-header" @click="toggleSection('admin')">
          <div class="acordeon-header-content">
            <div class="acordeon-icon-wrapper">
              <i class="ri-settings-3-line acordeon-icon"></i>
            </div>
            <span class="acordeon-title">Administración</span>
          </div>
          <i 
            class="ri-arrow-down-s-line acordeon-arrow"
            :class="{ 'rotated': openSection === 'admin' }"
          ></i>
        </div>
        <div class="acordeon-content" :class="{ 'open': openSection === 'admin' }">
          <ul class="nav-links acordeon-items">
            <li v-for="item in menuSections.admin" :key="item.path">
              <router-link :to="item.path" class="nav-link acordeon-item">
                <div class="link-content">
                  <div class="icon-wrapper">
                    <i :class="['icon', item.icon]"></i>
                  </div>
                  <span class="link-text">{{ item.name }}</span>
                </div>
                <div class="link-indicator"></div>
              </router-link>
            </li>
          </ul>
        </div>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import logo from '@/assets/logo.jpg';

const openSection = ref('comercial'); // Por defecto, abre Gestión Comercial

const menuSections = {
  comercial: [
    { name: 'Ventas', path: '/ventas', icon: 'ri-bar-chart-2-line' },
    { name: 'Turnos', path: '/turnos', icon: 'ri-calendar-event-line' },
    { name: 'Servicios', path: '/servicios', icon: 'ri-scissors-line' },
  ],
  inventario: [
    { name: 'Productos', path: '/productos', icon: 'ri-shopping-bag-line' },
    { name: 'Pedidos', path: '/pedidos', icon: 'ri-shopping-cart-2-line' },
    { name: 'Proveedores', path: '/proveedores', icon: 'ri-truck-line' },
    { name: 'Categorías', path: '/categorias', icon: 'ri-list-settings-line' },
  ],
  admin: [
    { name: 'Usuarios', path: '/usuarios', icon: 'ri-team-line' },
    { name: 'Roles', path: '/roles', icon: 'ri-shield-user-line' },
  ]
};

const toggleSection = (section) => {
  openSection.value = openSection.value === section ? null : section;
};
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
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.logo-container {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.25);
  transition: box-shadow 0.3s ease;
}

.logo-container:hover {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.35);
}

.logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 3px solid #3b82f6;
}

.brand-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: 0.5px;
  text-align: center;
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
  margin: 0 0 12px 0;
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
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
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
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
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

/* ========== ESTILOS DEL ACORDEÓN ========== */

.acordeon-section {
  margin-bottom: 8px;
}

/* Header del Acordeón */
.acordeon-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.acordeon-header:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateX(2px);
}

.acordeon-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.acordeon-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 8px;
  flex-shrink: 0;
}

.acordeon-icon {
  font-size: 1rem;
  color: #ffffff;
}

.acordeon-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.acordeon-arrow {
  font-size: 1.2rem;
  color: var(--text-secondary);
  transition: transform 0.3s ease;
}

.acordeon-arrow.rotated {
  transform: rotate(180deg);
}

/* Contenido del Acordeón */
.acordeon-content {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding-top: 0;
}

.acordeon-content.open {
  max-height: 500px; /* Ajusta según necesites */
  opacity: 1;
  padding-top: 4px;
}

/* Items dentro del acordeón */
.acordeon-items {
  margin: 0;
  padding-left: 12px;
}

.acordeon-item {
  /* Hereda estilos de .nav-link */
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