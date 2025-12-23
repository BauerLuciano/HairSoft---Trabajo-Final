<template>
  <div class="premium-layout">
    <div class="background-glow"></div>

    <div class="auth-card">
      <div class="card-header">
        <div class="icon-container">
          <div class="icon-bg"></div>
          <span class="icon">🔐</span>
        </div>
        <h1>Recuperar Cuenta</h1>
        <p>Ingresa tu correo electrónico y te enviaremos un enlace para restablecer tu contraseña.</p>
      </div>

      <form @submit.prevent="enviarSolicitud" autocomplete="off">
        <div class="input-group">
          <label for="email">Correo Electrónico</label>
          <div class="input-wrapper" :class="{ 'focused': focusedField === 'email' }">
            <input 
              id="email"
              v-model="email" 
              type="email" 
              placeholder="ejemplo@correo.com" 
              required
              :disabled="cargando"
              @focus="focusedField = 'email'"
              @blur="focusedField = ''"
            />
          </div>
        </div>

        <button type="submit" class="submit-btn" :disabled="cargando">
          <span v-if="cargando" class="spinner"></span>
          <span v-else>Enviar Enlace de Recuperación</span>
        </button>

        <div class="auth-footer">
          <router-link to="/login" class="back-link">
            <span>←</span> Volver al inicio de sesión
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

const email = ref('')
const cargando = ref(false)
const focusedField = ref('')
// Ajusta la URL base de tu API si es necesario
const API_BASE = 'http://127.0.0.1:8000'

const enviarSolicitud = async () => {
  if (!email.value) return

  cargando.value = true
  try {
    // Se envía la solicitud al backend
    await axios.post(`${API_BASE}/api/password-reset/solicitar/`, { 
      email: email.value 
    })

    // Mensaje de éxito genérico por seguridad
    Swal.fire({
      icon: 'success',
      title: '¡Enlace Enviado!',
      text: 'Si el correo existe en nuestra base de datos, recibirás un email con las instrucciones.',
      confirmButtonColor: '#0ea5e9',
      background: '#1e293b',
      color: '#f1f5f9'
    })
    
    email.value = '' // Limpiar campo

  } catch (error) {
    console.error(error)
    // Mensaje de error genérico
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Hubo un problema al procesar la solicitud.',
      background: '#1e293b',
      color: '#f1f5f9'
    })
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
/* --- LAYOUT & FONDO --- */
.premium-layout {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #0f172a; /* Color de fondo principal */
  position: relative;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 20px;
}

/* Efecto de luz de fondo */
.background-glow {
  position: absolute;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.15) 0%, transparent 70%);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  z-index: 0;
  animation: pulseGlow 8s infinite alternate;
}

@keyframes pulseGlow {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; }
}

/* --- TARJETA --- */
.auth-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 450px; /* Ancho máximo de la tarjeta */
  background: rgba(30, 41, 59, 0.7); /* Efecto Glassmorphism */
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  box-sizing: border-box; /* Importante para el padding */
}

/* --- HEADER --- */
.card-header { text-align: center; margin-bottom: 35px; }

.icon-container {
  position: relative; width: 80px; height: 80px; margin: 0 auto 20px;
  display: flex; justify-content: center; align-items: center;
}
.icon-bg {
  position: absolute; width: 100%; height: 100%;
  background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
  border-radius: 50%; opacity: 0.2;
  filter: blur(10px);
}
.icon { font-size: 40px; position: relative; z-index: 2; }

.card-header h1 {
  color: white; font-size: 26px; font-weight: 800; margin-bottom: 10px;
  letter-spacing: -0.5px;
}
.card-header p { color: #94a3b8; font-size: 15px; line-height: 1.5; }

/* --- INPUTS (CORREGIDO PARA ALINEACIÓN) --- */
.input-group {
  margin-bottom: 25px;
  width: 100%; /* Asegura que el grupo ocupe todo el ancho */
}

.input-group label {
  display: block;
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
  text-align: left;
}

.input-wrapper {
  position: relative;
  width: 100%; /* Asegura que el contenedor del input ocupe todo el ancho */
  background: rgba(15, 23, 42, 0.6);
  border: 2px solid #334155;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  box-sizing: border-box; /* Fundamental para que el padding no sume al ancho */
}

.input-wrapper.focused {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15);
  background: rgba(15, 23, 42, 0.9);
}


.input-wrapper input {
  flex-grow: 1; /* El input ocupa el espacio restante */
  width: 100%;
  padding: 16px;
  background: transparent;
  border: none;
  color: white;
  font-size: 16px;
  outline: none;
  box-sizing: border-box;
}

.input-wrapper input::placeholder {
  color: #64748b;
}

/* --- BOTÓN (CORREGIDO PARA ALINEACIÓN) --- */
.submit-btn {
  width: 100%; /* Asegura que el botón ocupe todo el ancho */
  padding: 16px; /* Padding consistente con el input */
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 12px; /* Mismo radio que el input */
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px -5px rgba(14, 165, 233, 0.4);
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box; /* Fundamental */
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -5px rgba(14, 165, 233, 0.5);
  filter: brightness(1.1);
}

.submit-btn:active { transform: translateY(0); }
.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; filter: grayscale(0.5); }

/* Spinner simple */
.spinner {
  width: 20px; height: 20px; border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* --- FOOTER --- */
.auth-footer { margin-top: 30px; text-align: center; }
.back-link {
  color: #94a3b8; text-decoration: none; font-weight: 600; font-size: 14px;
  display: inline-flex; align-items: center; gap: 6px;
  transition: all 0.2s;
}
.back-link span { transition: transform 0.2s; }
.back-link:hover { color: #0ea5e9; }
.back-link:hover span { transform: translateX(-4px); }
</style>