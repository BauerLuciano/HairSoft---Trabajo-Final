<template>
  <Navbar />
  <main class="app-content">
    <router-view />
  </main>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>

<style>
.app-content {
  margin-top: 60px;
  padding: 1rem;
}
</style>
