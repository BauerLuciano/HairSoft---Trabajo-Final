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
          <div class="client-limit-container">
            <router-view />
          </div>
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
import CartSidebar from '@/components/CartSidebar.vue';

const route = useRoute();

const esLayoutAdmin = computed(() => {
  return !route.meta.hideNavbar && (!route.meta.layout || route.meta.layout === 'admin');
});

const esLayoutCliente = computed(() => {
  return !route.meta.hideNavbar && route.meta.layout === 'client';
});

// Tus estilos originales, no los toco
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
   =============================================================================
*/

:root {
  --bg-primary: #0f172a;        
  --bg-secondary: #1e293b;      
  --text-primary: #f8fafc;      
  --text-secondary: #cbd5e1;    
  --accent-color: #8b5cf6;
}

/* 1. RESET MAESTRO */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%; 
  overflow: hidden; /* 🔒 Mantenemos el bloqueo de scroll en body */
  background-color: var(--bg-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* 2. CONTENEDOR PRINCIPAL */
.app-layout {
  display: flex;
  width: 100%;
  height: 100vh; 
  overflow: hidden;
}

/* 3. WRAPPER DE CONTENIDO */
.main-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  position: relative;
}

/* 4. ÁREA DE SCROLL (BASE / ADMIN) - ESTA NO LA TOCAMOS */
.page-content {
  flex: 5; /* Mantenemos tu flex 5 para no romper tablas */
  background-color: var(--bg-primary);
  overflow-y: auto; 
  overflow-x: hidden;
  padding: 20px;
  position: relative;
  scroll-behavior: smooth;
}

/* =========================================
   AJUSTES ESPECÍFICOS POR LAYOUT
   ========================================= */

/* --- Layout Cliente (Corregido) --- */
.client-wrapper {
  background-color: var(--bg-primary);
}

/* Hereda de .page-content pero le quitamos el padding directo y el margin
   para que el scrollbar quede pegado a la derecha de la pantalla */
.client-content {
  width: 100%;
  margin: 0; 
  padding: 0; 
}

/* Nuevo contenedor interno para centrar el contenido del cliente
   sin afectar el ancho de la barra de desplazamiento */
.client-limit-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100%; /* Para asegurar que ocupe el alto */
}

/* --- Layout Público (Corregido) --- */
.public-page {
  flex: 1; /* ✅ ESTO FALTABA: Obliga al div a llenar el espacio restante */
  width: 100%;
  height: 100%;
  overflow-y: auto; /* Scroll propio */
  background: var(--bg-primary);
  display: flex;       /* Opcional: Ayuda a centrar login si se requiere */
  flex-direction: column;
}

/* --- Scrollbars (Tu estilo original) --- */
.page-content::-webkit-scrollbar,
.public-page::-webkit-scrollbar,
.client-content::-webkit-scrollbar {
  width: 8px;
}
.page-content::-webkit-scrollbar-track,
.public-page::-webkit-scrollbar-track,
.client-content::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}
.page-content::-webkit-scrollbar-thumb,
.public-page::-webkit-scrollbar-thumb,
.client-content::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}
.page-content::-webkit-scrollbar-thumb:hover,
.public-page::-webkit-scrollbar-thumb:hover,
.client-content::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

/* Media Query Móvil */
@media (max-width: 768px) {
  .page-content, 
  .client-limit-container {
    padding: 15px;
  }
}
</style>