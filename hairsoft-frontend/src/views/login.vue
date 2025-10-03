<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-container">
        <!-- Logo de tijera, reemplaza URL si querés -->
        <img src="https://i.gifer.com/37Eo.gif" alt="HairSoft Logo" class="logo">
      </div>

      <h1 class="login-title">HairSoft</h1>
      <p class="login-subtitle">Ingresa a tu cuenta!</p>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="input-group">
          <input type="text" v-model="username" required class="input-field" placeholder="Usuario">
        </div>

        <div class="input-group">
          <input type="password" v-model="password" required class="input-field" placeholder="Contraseña">
        </div>

        <a href="#" class="forgot-password">¿Olvidaste tu contraseña?</a>

        <button type="submit" class="login-button">Iniciar Sesión</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    handleLogin() {
      console.log('Login:', this.username, this.password)
      // Aquí va tu lógica de login
    },
    handleGoogleLogin() {
      console.log('Google login')
      // Aquí va tu lógica de login con Google
    }
  }
}
</script>

<!-- Asegúrate de que la ruta apunta a src/styles/login.css -->
<style src="../styles/login.css"></style>
