<template>
  <Navbar />
  <main class="app-content">
    <router-view />
  </main>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { onMounted } from 'vue'

// Aplicar tema guardado al cargar la app
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'light') {
    document.body.classList.add('light-mode')
  }
})
</script>

<style>
/* Estilos base del body - FONDO OSCURO POR DEFECTO */
body {
  margin: 0;
  padding: 0;
  transition: background-color 0.4s ease, color 0.4s ease;
  background: #0a0a0a !important;
  color: #ffffff !important;
  min-height: 100vh;
}

/*.app-content {
  margin-top: 60px;
  padding: 1rem;
  transition: all 0.4s ease;
  min-height: calc(100vh - 80px);
} */

/* MODO CLARO - FONDO BLANCO EN TODO */
body.light-mode {
  background: #ffffff !important;
  color: #1a1a1a !important;
}

body.light-mode .app-content {
  background: #ffffff !important;
}

/* Asegurar que todos los contenedores tengan fondo blanco en modo claro */
body.light-mode * {
  transition: background-color 0.4s ease, color 0.4s ease, border-color 0.4s ease;
}
</style>