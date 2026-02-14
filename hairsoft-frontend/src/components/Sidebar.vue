<template>
  <nav class="sidebar">
    <div class="sidebar-header">
      <div class="logo-wrapper">
        <div class="logo-container">
          <img :src="empresa.logo || logoEstatico" alt="HairSoft Logo" class="logo" />
        </div>
      </div>
    </div>

    <div class="nav-section">
      <span class="section-title">MENÚ PRINCIPAL</span>
      
      <ul class="nav-links">
        <li v-if="userRol !== 'PELUQUERO'">
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

      <template v-for="(section, key) in filteredMenu" :key="key">
        <div v-if="section.items.length > 0" class="acordeon-section">
          <div class="acordeon-header" @click="toggleSection(key)">
            <div class="acordeon-header-content">
              <div class="acordeon-icon-wrapper">
                <i :class="[section.icon, 'acordeon-icon']"></i>
              </div>
              <span class="acordeon-title">{{ section.title }}</span>
            </div>
            <i 
              class="ri-arrow-down-s-line acordeon-arrow"
              :class="{ 'rotated': openSection === key }"
            ></i>
          </div>
          <div class="acordeon-content" :class="{ 'open': openSection === key }">
            <ul class="nav-links acordeon-items">
              <li v-for="item in section.items" :key="item.path">
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
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from '@/utils/axiosConfig';
import logoEstatico from '@/assets/logo.jpg';

const openSection = ref('comercial'); 
const userRol = localStorage.getItem('user_rol'); 

const empresa = ref({
  razon_social: '',
  logo: null
});

const cargarBranding = async () => {
  try {
    const res = await axios.get('/api/configuracion/');
    const data = res.data;
    
    // ✅ CORRECCIÓN: Si la URL es relativa (/media/...), le agregamos el dominio del backend
    if (data.logo && !data.logo.startsWith('http')) {
        const API_BASE = 'http://127.0.0.1:8000'; // Ajustá esto a tu puerto de Django
        data.logo = `${API_BASE}${data.logo}`;
    }
    
    empresa.value = data;
  } catch (e) {
    console.error("No se pudo cargar el logo dinámico");
  }
};

const menuData = {
  comercial: {
    title: 'Gestión Comercial',
    icon: 'ri-store-2-line',
    items: [
      { name: 'Ventas', path: '/ventas', icon: 'ri-bar-chart-2-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] },
      { name: 'Pedidos Web', path: '/pedidos-web-admin', icon: 'ri-global-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] }, 
      { name: 'Turnos', path: '/turnos', icon: 'ri-calendar-event-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA', 'PELUQUERO'] },
      { name: 'Servicios', path: '/servicios', icon: 'ri-scissors-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] },
    ]
  },
  inventario: {
    title: 'Inventario',
    icon: 'ri-archive-line',
    items: [
      { name: 'Productos', path: '/productos', icon: 'ri-shopping-bag-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] },
      { name: 'Catálogo Visual', path: '/catalogo', icon: 'ri-layout-grid-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] }, 
      { name: 'Pedidos Prov.', path: '/pedidos', icon: 'ri-shopping-cart-2-line', roles: ['ADMINISTRADOR'] }, 
      { name: 'Proveedores', path: '/proveedores', icon: 'ri-truck-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] },
      { name: 'Categorías', path: '/categorias', icon: 'ri-list-settings-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] },
      { name: 'Marcas', path: '/productos/marcas', icon: 'ri-price-tag-2-line', roles: ['ADMINISTRADOR', 'RECEPCIONISTA'] },
      { name: 'Licitaciones', path: '/proveedores/evaluacion', icon: 'ri-file-list-3-line', roles: ['ADMINISTRADOR'] }, 
    ]
  },
  admin: {
    title: 'Administración',
    icon: 'ri-settings-3-line',
    items: [
      { name: 'Usuarios', path: '/usuarios', icon: 'ri-team-line', roles: ['ADMINISTRADOR'] },
      { name: 'Roles', path: '/roles', icon: 'ri-shield-user-line', roles: ['ADMINISTRADOR'] },
      { name: 'Liquidación Sueldos', path: '/admin/liquidacion', icon: 'ri-money-dollar-circle-line', roles: ['ADMINISTRADOR'] }, 
      { name: 'Auditoría', path: '/auditoria', icon: 'ri-file-history-line', roles: ['ADMINISTRADOR'] },
      { name: 'Ajustes Local', path: '/configuracion', icon: 'ri-settings-4-line', roles: ['ADMINISTRADOR'] },
    ]
  }
};

const filteredMenu = computed(() => {
  const filtered = {};
  for (const key in menuData) {
    const section = menuData[key];
    const items = section.items.filter(item => item.roles.includes(userRol));
    if (items.length > 0) {
      filtered[key] = { ...section, items };
    }
  }
  return filtered;
});

const toggleSection = (section) => {
  openSection.value = openSection.value === section ? null : section;
};

onMounted(cargarBranding);
</script>

<style scoped>
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
  border-radius: 10%;
  overflow: hidden;
  border: 3px solid #949494;
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

.nav-links {
  list-style: none;
  margin: 0 0 8px 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

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
  color: #adadad;
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
  color: #a0a4ab;
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