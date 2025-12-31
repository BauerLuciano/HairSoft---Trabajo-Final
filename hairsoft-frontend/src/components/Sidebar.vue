<template>
  <nav class="sidebar">
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

    <div class="nav-section">
      <span class="section-title">MENÚ PRINCIPAL</span>
      
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

const openSection = ref('comercial'); 

const menuSections = {
  comercial: [
    { name: 'Ventas', path: '/ventas', icon: 'ri-bar-chart-2-line' },
    { name: 'Turnos', path: '/turnos', icon: 'ri-calendar-event-line' },
    { name: 'Servicios', path: '/servicios', icon: 'ri-scissors-line' },
  ],
  inventario: [
    { name: 'Productos', path: '/productos', icon: 'ri-shopping-bag-line' },
    { name: 'Catálogo Visual', path: '/catalogo', icon: 'ri-layout-grid-line' }, 
    { name: 'Pedidos', path: '/pedidos', icon: 'ri-shopping-cart-2-line' },
    { name: 'Proveedores', path: '/proveedores', icon: 'ri-truck-line' },
    { name: 'Categorías', path: '/categorias', icon: 'ri-list-settings-line' },
    { name: 'Marcas', path: '/productos/marcas', icon: 'ri-price-tag-2-line' },
    { name: 'Licitaciones', path: '/proveedores/evaluacion', icon: 'ri-file-list-3-line' },
  ],
  admin: [
    { name: 'Usuarios', path: '/usuarios', icon: 'ri-team-line' },
    { name: 'Roles', path: '/roles', icon: 'ri-shield-user-line' },
    { name: 'Liquidación Sueldos', path: '/admin/liquidacion', icon: 'ri-money-dollar-circle-line' }, // 💰 Agregado
    { name: 'Auditoría', path: '/auditoria', icon: 'ri-file-history-line' },
  ]
};

const toggleSection = (section) => {
  openSection.value = openSection.value === section ? null : section;
};
</script>

<style scoped>
/* Sidebar Principal */
.sidebar {
  width: 290px;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  border-right: 1px solid rgba(59, 130, 246, 0.15);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
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
  background: rgba(17, 24, 39, 0.5);
  border-radius: 10px;
  margin: 8px 0;
}

.sidebar::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #374151, #1f2937);
  border-radius: 10px;
  transition: background 0.3s ease;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #4b5563, #374151);
}

/* Header del Sidebar */
.sidebar-header {
  padding: 32px 20px 28px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  position: relative;
}

.sidebar-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20px;
  right: 20px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
}

.logo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.logo-container {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  overflow: hidden;
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

.logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.brand-info {
  text-align: center;
}

.brand-name {
  font-size: 1.9rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  display: block;
  text-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
}

/* Sección de Navegación */
.nav-section {
  flex: 1;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-title {
  font-size: 0.7rem;
  font-weight: 800;
  color: #6b7280;
  letter-spacing: 2px;
  text-transform: uppercase;
  padding: 0 12px;
  margin-bottom: 12px;
  position: relative;
  display: inline-block;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 12px;
  width: 30px;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, transparent);
  border-radius: 2px;
}

/* Lista de Links */
.nav-links {
  list-style: none;
  margin: 0 0 8px 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Link Individual */
.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-decoration: none;
  padding: 13px 16px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
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
  gap: 14px;
  flex: 1;
  z-index: 2;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.icon {
  font-size: 1.35rem;
  color: #d1d5db;
  transition: all 0.3s ease;
}

.link-text {
  font-size: 1.02rem;
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

/* Hover State */
.nav-link:hover {
  background: rgba(31, 41, 55, 0.8);
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.nav-link:hover::before {
  transform: scaleY(1);
}

.nav-link:hover .icon-wrapper {
  background: rgba(59, 130, 246, 0.2);
  transform: scale(1.05);
}

.nav-link:hover .icon {
  color: #fff;
  transform: scale(1.1);
}

.nav-link:hover .link-text {
  color: #fff;
}

/* Active State */
.nav-link.router-link-active {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  box-shadow: 
    0 4px 16px rgba(59, 130, 246, 0.4),
    0 2px 8px rgba(0, 0, 0, 0.2);
  transform: translateX(4px);
}

.nav-link.router-link-active::before {
  transform: scaleY(1);
  background: #60a5fa;
}

.nav-link.router-link-active .icon-wrapper {
  background: rgba(255, 255, 255, 0.15);
}

.nav-link.router-link-active .icon {
  color: #ffffff;
  transform: scale(1.1);
}

.nav-link.router-link-active .link-text {
  color: #ffffff;
  font-weight: 600;
}

/* Acordeón */
.acordeon-section {
  margin-bottom: 6px;
}

.acordeon-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(59, 130, 246, 0.1);
  position: relative;
  user-select: none;
}

.acordeon-header::before {
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

.acordeon-header:hover {
  background: rgba(31, 41, 55, 0.8);
  border-color: rgba(59, 130, 246, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.acordeon-header:hover::before {
  transform: scaleY(0.6);
}

.acordeon-header-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.acordeon-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  border-radius: 8px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.acordeon-header:hover .acordeon-icon-wrapper {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.acordeon-icon {
  font-size: 1.2rem;
  color: #ffffff;
}

.acordeon-title {
  font-size: 1.02rem;
  font-weight: 600;
  color: #d1d5db;
  letter-spacing: 0.3px;
  transition: color 0.3s ease;
}

.acordeon-header:hover .acordeon-title {
  color: #fff;
}

.acordeon-arrow {
  font-size: 1.2rem;
  color: #9ca3af;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.7;
}

.acordeon-header:hover .acordeon-arrow {
  opacity: 1;
  color: #60a5fa;
}

.acordeon-arrow.rotated {
  transform: rotate(180deg);
  color: #60a5fa;
}

/* Contenido del Acordeón */
.acordeon-content {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  padding-top: 0;
  padding-left: 18px;
  border-left: 2px solid rgba(59, 130, 246, 0.2);
  margin-left: 24px;
}

.acordeon-content.open {
  max-height: 600px;
  opacity: 1;
  padding-top: 8px;
  padding-bottom: 4px;
}

.acordeon-items {
  margin: 0;
  padding: 0;
}

.acordeon-item {
  font-size: 0.94rem;
}

.acordeon-item .icon-wrapper {
  width: 28px;
  height: 28px;
}

.acordeon-item .icon {
  font-size: 1.15rem;
}

.acordeon-item .link-text {
  font-size: 0.94rem;
  font-weight: 500;
}

.acordeon-item:hover .link-text {
  font-weight: 600;
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar {
    width: 270px;
  }
}

@media (max-height: 800px) {
  .sidebar-header {
    padding: 24px 20px 20px;
  }
  
  .logo-container {
    width: 75px;
    height: 75px;
  }
  
  .brand-name {
    font-size: 1.6rem;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -290px;
    width: 290px;
    z-index: 1001;
  }

  .sidebar.active {
    left: 0;
  }
}
</style>