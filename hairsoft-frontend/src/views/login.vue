<template>
  <div style="padding: 20px;">
    <h1>HairSoft Login</h1>
    <div v-if="mensajeError" style="color: red;">{{ mensajeError }}</div>
    <input v-model="username" placeholder="Email" style="display: block; margin: 10px 0; padding: 5px;">
    <input v-model="password" type="password" placeholder="Password" style="display: block; margin: 10px 0; padding: 5px;">
    <button @click="handleLogin" style="padding: 10px 20px;">Login</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      mensajeError: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        console.log("🔐 Intentando login...");
        const response = await fetch("http://localhost:8000/usuarios/api/auth/login/", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          }),
          credentials: 'include'
        });
        
        const data = await response.json();
        console.log("📦 Respuesta:", data);
        
        if (data.status === 'ok') {
          localStorage.setItem('user_id', data.user_id);
          localStorage.setItem('user_rol', data.rol);
          console.log("✅ Login exitoso! Rol: " + data.rol);
          
          // 🆕 OBTENER DATOS COMPLETOS DEL USUARIO
          try {
            const userResponse = await fetch(`http://localhost:8000/usuarios/api/usuarios/${data.user_id}/`);
            const userData = await userResponse.json();
            
            localStorage.setItem('user_nombre', userData.nombre);
            localStorage.setItem('user_apellido', userData.apellido);
            
            console.log("✅ Datos usuario guardados:", userData);
          } catch (userError) {
            console.error("❌ Error obteniendo datos usuario:", userError);
            // 🆕 TEMPORAL: Usar email como nombre si falla
            const userEmail = this.username;
            const userName = userEmail.split('@')[0];
            localStorage.setItem('user_nombre', userName);
            localStorage.setItem('user_apellido', '');
          }
          
          // 🆕 DISPARAR EVENTO PARA ACTUALIZAR HEADER
          window.dispatchEvent(new Event('usuarioLogueado'));
          
          // 🚨 REDIRECCIÓN SEGÚN ROL
          const rol = data.rol;
          if (rol === 'CLIENTE') {
            console.log("🎯 Redirigiendo a crear turno web...");
            this.$router.push('/turnos/crear-web');
          } else if (rol === 'ADMINISTRADOR') {
            console.log("🎯 Redirigiendo a usuarios...");
            this.$router.push('/usuarios');
          } else if (rol === 'PELUQUERO') {
            console.log("🎯 Redirigiendo a turnos...");
            this.$router.push('/turnos');
          } else {
            console.log("❌ Rol desconocido:", rol);
            this.mensajeError = "Rol no reconocido: " + rol;
          }
          
        } else {
          this.mensajeError = data.message || "Error en login";
        }
      } catch (error) {
        console.error("💥 Error:", error);
        this.mensajeError = "Error de conexión";
      }
    }
  }
}
</script>

<style src="../styles/login.css"></style>

<style>
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