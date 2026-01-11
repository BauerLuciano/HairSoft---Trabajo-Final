<template>
  <div class="premium-layout">
    <div class="background-glow"></div>

    <div class="auth-card">
      <div class="card-header">
        <div class="icon-container">
          <div class="icon-bg"></div>
          <span class="icon">🔑</span>
        </div>
        <h1>Nueva Contraseña</h1>
        <p>Creá una contraseña fuerte y segura.</p>
      </div>

      <form @submit.prevent="guardarPassword" autocomplete="off">
        
        <div class="input-group">
          <label>Nueva Contraseña</label>
          <div class="input-wrapper" :class="{ 'focused': focusedField === 'pass' }">
            <input 
              v-model="password" 
              :type="mostrarPass ? 'text' : 'password'" 
              placeholder="Mínimo 6 caracteres, 1 mayúscula, 1 número" 
              required
              @focus="focusedField = 'pass'"
              @blur="focusedField = ''"
            />
            <button type="button" class="eye-btn" @click="mostrarPass = !mostrarPass">
              {{ mostrarPass ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div class="input-group">
          <label>Confirmar Contraseña</label>
          <div class="input-wrapper" :class="{ 'focused': focusedField === 'confirm', 'error-border': errorMsg }">
            <input 
              v-model="confirmPassword" 
              :type="mostrarPass ? 'text' : 'password'" 
              placeholder="Repetí la contraseña" 
              required
              @focus="focusedField = 'confirm'"
              @blur="focusedField = ''"
            />
          </div>
          <div v-if="errorMsg" class="error-msg">⚠️ {{ errorMsg }}</div>
        </div>

        <button type="submit" class="submit-btn" :disabled="cargando || !esValido">
          <span v-if="cargando" class="spinner"></span>
          <span v-else>Actualizar Contraseña</span>
        </button>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()

const isProduction = window.location.hostname.includes('vercel.app');
const API_BASE = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://127.0.0.1:8000';

const password = ref('')
const confirmPassword = ref('')
const mostrarPass = ref(false)
const cargando = ref(false)
const focusedField = ref('')
const token = route.params.token 

// Validaciones
const esValido = computed(() => {
  // Regex: Al menos 6 caracteres, una mayúscula y un número
  const regexFuerte = /^(?=.*[A-Z])(?=.*\d).{6,}$/;
  return regexFuerte.test(password.value) && password.value === confirmPassword.value;
})

const errorMsg = computed(() => {
  if (confirmPassword.value && password.value !== confirmPassword.value) return "Las contraseñas no coinciden"
  
  if (password.value) {
      if (password.value.length < 6) return "Mínimo 6 caracteres"
      if (!/(?=.*[A-Z])/.test(password.value)) return "Falta al menos una mayúscula"
      if (!/(?=.*\d)/.test(password.value)) return "Falta al menos un número"
  }
  
  return ""
})

const guardarPassword = async () => {
  if (!esValido.value) return
  cargando.value = true
  try {
    await axios.post(`${API_BASE}/api/password-reset/confirmar/`, {
      token, nueva_password: password.value, confirmar_password: confirmPassword.value
    })
    Swal.fire({
      icon: 'success', title: '¡Perfecto!', text: 'Contraseña actualizada.',
      confirmButtonText: 'Iniciar Sesión', confirmButtonColor: '#0ea5e9',
      background: '#1e293b', color: '#f1f5f9'
    })
    router.push('/login')
  } catch (err) {
    Swal.fire({ icon: 'error', title: 'Error', text: 'El enlace expiró o es inválido.', background: '#1e293b', color: '#f1f5f9' })
    router.push('/recuperar-password')
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
/* --- LAYOUT & FONDO (Estilo Azul Original) --- */
.premium-layout {
  min-height: 100vh;
  display: flex; justify-content: center; align-items: center;
  background-color: #0f172a; /* Fondo oscuro principal */
  position: relative; overflow: hidden;
  font-family: 'Segoe UI', sans-serif;
  padding: 20px;
}

/* Glow Azul */
.background-glow {
    position: absolute;
    width: 600px; height: 600px;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    z-index: 0;
    background: radial-gradient(circle, rgba(14, 165, 233, 0.15) 0%, transparent 70%); /* Azul */
    animation: pulseGlow 8s infinite alternate;
}

@keyframes pulseGlow {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; }
}

/* --- TARJETA --- */
.auth-card {
  width: 100%; max-width: 450px; 
  z-index: 1;
  background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  box-sizing: border-box;
  animation: fadeInScale 0.6s ease-out;
}

@keyframes fadeInScale { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }

/* Headers */
.card-header { text-align: center; margin-bottom: 35px; }
.icon-container { position: relative; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; justify-content: center; align-items: center; }

/* Icon BG Azul */
.icon-bg {
  position: absolute; width: 100%; height: 100%;
  background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%); /* Azul */
  border-radius: 50%; opacity: 0.2;
  filter: blur(10px);
}
.icon { font-size: 40px; position: relative; z-index: 2; }
.card-header h1 { color: white; font-size: 26px; font-weight: 800; margin-bottom: 10px; }
.card-header p { color: #94a3b8; font-size: 15px; }

/* Inputs (Alineados y Azules) */
.input-group {
  margin-bottom: 25px;
  width: 100%;
}
.input-group label {
  display: block;
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.input-wrapper {
  position: relative;
  width: 100%;
  background: rgba(15, 23, 42, 0.6);
  border: 2px solid #334155;
  border-radius: 12px; /* Agregado borde redondeado aquí también */
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}
/* Focus Azul */
.input-wrapper.focused {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15);
  background: rgba(15, 23, 42, 0.9);
}
.input-wrapper.error-border { border-color: #ef4444; } /* Rojo solo para error */

.input-wrapper input {
  flex-grow: 1;
  width: 100%;
  padding: 16px;
  background: transparent;
  border: none;
  color: white;
  font-size: 16px;
  outline: none;
  box-sizing: border-box;
}

.eye-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding-right: 15px;
  transition: 0.2s;
  color: #64748b;
}
.eye-btn:hover { color: #0ea5e9; transform: scale(1.1); }

.error-msg { color: #ef4444; font-size: 13px; margin-top: 8px; font-weight: 600; display: flex; align-items: center; gap: 5px; animation: shake 0.4s ease-in-out; }
@keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }

/* Botón Azul Estándar */
.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); /* Gradiente Azul */
  color: white;
  border: none;
  border-radius: 12px;
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
  box-sizing: border-box;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -5px rgba(14, 165, 233, 0.5);
  filter: brightness(1.1);
}

.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; filter: grayscale(0.5); }

.spinner { width: 20px; height: 20px; border: 3px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>