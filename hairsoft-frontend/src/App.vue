<template>
  <div class="app-layout">
    <template v-if="esLayoutAdmin">
      <Sidebar />
      <div class="main-content-wrapper">
        <Header />
        <main class="page-content">
          <router-view />
        </main>
      </div>
    </template>

    <template v-else-if="esLayoutCliente">
      <div class="main-content-wrapper client-wrapper">
        <ClientNavbar />
        <main class="page-content client-content">
          <router-view />
        </main>
      </div>
    </template>

    <template v-else>
      <div class="public-page">
        <router-view />
      </div>
    </template>

    <CartSidebar />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './components/Sidebar.vue';
import Header from './components/Header.vue';
import ClientNavbar from './components/ClientNavbar.vue';
import CartSidebar from '@/components/CartSidebar.vue'; // <--- IMPORTACIÓN NUEVA

const route = useRoute();

// Lógica de decisión de layout basada en meta-tags del router
const esLayoutAdmin = computed(() => {
  return !route.meta.hideNavbar && (!route.meta.layout || route.meta.layout === 'admin');
});

const esLayoutCliente = computed(() => {
  return !route.meta.hideNavbar && route.meta.layout === 'client';
});

// Cargar estilos globales dinámicamente
onMounted(() => {
  import('./styles/reset.css');
  import('./styles/base.css');
  import('./styles/formularios.css');
  import('./styles/modos.css');
  import('./styles/themes.css');
});
</script>

<style>
/* =============================================================================
   ESTILOS ESTRUCTURALES MAESTROS
   Estos estilos controlan el layout y evitan el doble scroll.
   =============================================================================
*/

/* Variables Globales (Por defecto Dark Mode) */
:root {
  --bg-primary: #0f172a;        
  --bg-secondary: #1e293b;      
  --text-primary: #f8fafc;      
  --text-secondary: #cbd5e1;    
  --accent-color: #8b5cf6;
}

/* 1. RESET MAESTRO: Bloqueamos el scroll del navegador */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%; /* Ocupa exactamente el alto de la ventana */
  overflow: hidden; /* 🔒 CLAVE: Prohíbe scroll en el body */
  background-color: var(--bg-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* 2. CONTENEDOR PRINCIPAL */
.app-layout {
  display: flex;
  width: 100%;
  height: 100vh; /* Fuerza altura de viewport */
  overflow: hidden; /* Asegura que nada desborde aquí */
}

/* 3. WRAPPER DE CONTENIDO (Derecha del sidebar o Pantalla completa cliente) */
.main-content-wrapper {
  flex: 1; /* Toma todo el espacio disponible */
  display: flex;
  flex-direction: column; /* Apila Header arriba y Contenido abajo */
  height: 100%; /* ✅ CLAVE: Hereda la altura, no la fuerza */
  overflow: hidden; /* Evita scroll en el wrapper */
  position: relative;
}

/* 4. ÁREA DE SCROLL (Donde va el router-view) */
.page-content {
  flex: 1; /* Ocupa el espacio restante debajo del header */
  background-color: var(--bg-primary);
  overflow-y: auto; /* ✅ ÚNICO LUGAR CON SCROLL VERTICAL */
  overflow-x: hidden; /* Evita scroll horizontal */
  padding: 20px;
  position: relative;
  scroll-behavior: smooth;
}

/* =========================================
   AJUSTES ESPECÍFICOS POR LAYOUT
   ========================================= */

/* Layout Cliente */
.client-wrapper {
  background-color: var(--bg-primary);
}

.client-content {
  width: 100%;
  max-width: 1200px; /* Centrado bonito en monitores grandes */
  margin: 0 auto;
  padding: 20px;
}

/* Layout Público (Login, Registro, Landing) */
/* Este sí puede scrollear completo porque no tiene header fijo */
.public-page {
  width: 100%;
  height: 100%;
  overflow-y: auto; 
  background: var(--bg-primary);
}

/* Estilo de la barra de desplazamiento (Scrollbar) */
.page-content::-webkit-scrollbar,
.public-page::-webkit-scrollbar {
  width: 8px;
}
.page-content::-webkit-scrollbar-track,
.public-page::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}
.page-content::-webkit-scrollbar-thumb,
.public-page::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}
.page-content::-webkit-scrollbar-thumb:hover,
.public-page::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}
/* Layout Cliente - Corrección completa */
.client-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: var(--bg-primary);
}

.client-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

/* Sobrescribe cualquier min-height problemático */
.client-content > * {
  min-height: 0 !important;
}

/* Scrollbar específico para cliente */
.client-content::-webkit-scrollbar {
  width: 8px;
}
.client-content::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}
.client-content::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}
/* Media Query Móvil */
@media (max-width: 768px) {
  .page-content, 
  .client-content {
    padding: 15px; /* Menos padding en celular */
  }
}
</style>