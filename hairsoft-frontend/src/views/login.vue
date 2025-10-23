<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-container">
        <img src="https://i.gifer.com/37Eo.gif" alt="HairSoft Logo" class="logo">
      </div>

      <h1 class="login-title">HairSoft</h1>
      <p class="login-subtitle">Ingresa a tu cuenta!</p>

      <div v-if="mensajeError" class="error-message">
        {{ mensajeError }}
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="input-group">
          <input type="text" v-model.trim="username" required class="input-field" placeholder="Correo electrónico">
        </div>

        <div class="input-group">
          <input type="password" v-model="password" required class="input-field" placeholder="Contraseña">
        </div>

        <router-link to="/recuperar-password" class="forgot-password">¿Olvidaste tu contraseña?</router-link>

        <button type="submit" class="login-button">Iniciar Sesión</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'Login',
    data() {
        return {
            username: '', // Correo/Usuario
            password: '', // Contraseña
            mensajeError: ''
        }
    },
    methods: {
        async handleLogin() {
            this.mensajeError = '';
            
            if (!this.username || !this.password) {
                this.mensajeError = "Por favor, ingresa tu correo y contraseña.";
                return;
            }

            try {
                const response = await axios.post("http://localhost:8000/usuarios/api/auth/login/", {
                    username: this.username,
                    password: this.password
                });

                const data = response.data;

                if (data.status === 'ok') {
                    // 1. Guardar datos en LocalStorage
                    localStorage.setItem('user_id', data.user_id);
                    localStorage.setItem('user_rol', data.rol);
                    
                    // 2. 🛑 CORRECCIÓN CLAVE: Redirección con rutas existentes
                    const rol = data.rol;
                    
                    if (rol === 'CLIENTE') {
                        // Ruta real del cliente (crear turno web)
                        this.$router.push('/turnos/crear-web'); 
                        
                    } else if (rol === 'ADMINISTRADOR') {
                        // Ruta real de administración (Listado de Usuarios)
                        this.$router.push('/usuarios'); 
                        
                    } else if (rol === 'PELUQUERO') {
                        // Ruta real de Peluquero (Listado de Turnos)
                        this.$router.push('/turnos');
                        
                    } else {
                        // Rol desconocido o SIN_ROL
                        this.$router.push('/login'); 
                    }
                    
                    // Si usas Vuex/Pinia, aquí llamarías a cargarUsuarioLogueado()
                } else {
                    this.mensajeError = data.message || "Error al iniciar sesión.";
                }
            } catch (error) {
                console.error("Error de login:", error.response);
                
                // Manejo de errores 401 Unauthorized
                if (error.response && error.response.status === 401) {
                    this.mensajeError = "Credenciales incorrectas. Vuelve a intentarlo.";
                } else {
                    this.mensajeError = "Error de conexión o problema en el servidor.";
                }
            }
        }
    }
}
</script>

<style src="../styles/login.css"></style>

<style>
/* Estilo simple para el mensaje de error */
.error-message {
    color: #cc0000;
    background-color: #ffe0e0;
    border: 1px solid #cc0000;
    padding: 10px;
    margin-bottom: 15px;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
}
</style>