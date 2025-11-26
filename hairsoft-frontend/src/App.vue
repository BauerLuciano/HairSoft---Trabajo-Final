<template>
  <div class="app-layout">
    <Sidebar v-if="!route.meta.hideNavbar" /> 
    
    <div class="main-content-wrapper">
      <Header v-if="!route.meta.hideNavbar" /> 
      
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import Sidebar from './components/Sidebar.vue'; 
import Header from './components/Header.vue'; 

const route = useRoute();
// La lógica de tema se ejecuta en Header.vue
</script>

<style>
/* -------------------------------------- */
/* ESTILOS GLOBALES Y VARIABLES DE TEMA MODERNAS (Modo Oscuro por defecto) */
/* -------------------------------------- */

/* Variables de Tema Moderno y Minimalista */
:root {
  /* MODO OSCURO (Dark Mode - DEFAULT) */
  --bg-primary: #0f172a;        /* Fondo principal (Más claro que negro) */
  --bg-secondary: #1e293b;      /* Fondo de barras/tarjetas */
  --text-primary: #f8fafc;      /* Texto claro (Blanco suave) */
  --text-secondary: #cbd5e1;    /* Texto secundario (Gris claro) */
  --accent-color: #8b5cf6;      /* Púrpura vibrante (igual al header/sidebar) */
  --accent-shadow: rgba(139, 92, 246, 0.4); /* Sombra de acento */
  --shadow-color: rgba(0, 0, 0, 0.3); /* Sombra de elementos oscuros */
  --border-color: rgba(255, 255, 255, 0.1); /* Borde sutil */
  --hover-bg: rgba(255, 255, 255, 0.05); /* Fondo de hover sutil */
}

/* Variables para el MODO CLARO (Activado por la clase 'light-mode' en HTML) */
html.light-mode {
  --bg-primary: #f1f5f9;      /* Fondo principal (Blanco muy claro) */
  --bg-secondary: #ffffff;    /* Fondo de barras/tarjetas (Blanco puro) */
  --text-primary: #1e293b;    /* Texto oscuro */
  --text-secondary: #334155;  /* Texto secundario (Gris intermedio) */
  --accent-color: #8b5cf6;    /* Púrpura (consistente en ambos modos) */
  --accent-shadow: rgba(139, 92, 246, 0.4); 
  --shadow-color: rgba(0, 0, 0, 0.08); 
  --border-color: rgba(0, 0, 0, 0.1); 
  --hover-bg: rgba(0, 0, 0, 0.03); 
}

/* Estilos base del body/html */
* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden; /* IMPORTANTE: Evita el scroll del body */
  transition: all 0.4s ease;
}

body {
  background-color: var(--bg-primary); 
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* -------------------------------------- */
/* ESTRUCTURA DE LAYOUT (Header y Sidebar FIJOS) */
/* -------------------------------------- */

.app-layout {
  display: flex;
  height: 100vh; /* Altura completa de la ventana */
  overflow: hidden; /* Sin scroll en el layout principal */
}

/* El Sidebar ya tiene position: sticky en su propio componente */

.main-content-wrapper {
  flex: 1; /* Toma todo el espacio restante */
  display: flex;
  flex-direction: column;
  height: 100vh; /* Altura completa */
  overflow: hidden; /* Control de scroll interno */
}

/* El Header ya tiene position: sticky en su propio componente */

.page-content {
  flex: 1; /* Toma el espacio restante después del header */
  background-color: var(--bg-primary);
  overflow-y: auto; /* AQUÍ está el scroll - solo el contenido scrollea */
  overflow-x: hidden;
  transition: all 0.4s ease;
}

/* Scrollbar personalizado para el contenido */
.page-content::-webkit-scrollbar {
  width: 8px;
}

.page-content::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 10px;
}

.page-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
  transition: background 0.3s ease;
}

.page-content::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

/* Media Query para móvil (ocultar sidebar y expandir contenido) */
@media (max-width: 768px) {
  .sidebar {
    /* Se oculta o se colapsa en móvil */
    width: 0 !important;
    padding: 0 !important;
    border-right: none !important;
    overflow: hidden !important;
  }
  
  .main-content-wrapper {
    width: 100%; /* Asegura que el contenido ocupe todo el ancho */
  }
  
  .page-content {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 15px;
  }
}
</style>