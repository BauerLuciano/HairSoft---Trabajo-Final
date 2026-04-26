<template>
  <div class="premium-layout">
    <div class="background-glow"></div>

    <div class="auth-card">
      <div class="card-header">
        <div class="icon-container">
          <div class="icon-bg"></div>
          <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
          </span>
        </div>
        <h1>Nueva Contraseña</h1>
        <p>Creá una credencial de acceso segura.</p>
      </div>

      <form @submit.prevent="guardarPassword" autocomplete="off">
        
        <div class="input-group">
          <label>Nueva Contraseña</label>
          <div class="input-wrapper" :class="{ 'focused': focusedField === 'pass', 'error-border': errorPassword }">
            <input 
              v-model="password" 
              :type="mostrarPass ? 'text' : 'password'" 
              placeholder="Ej: Secreta123" 
              required
              @focus="focusedField = 'pass'"
              @blur="focusedField = ''"
            />
            <button type="button" class="eye-btn" @click="mostrarPass = !mostrarPass" title="Alternar visibilidad">
              <svg v-if="!mostrarPass" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
              </svg>
            </button>
          </div>
          <div v-if="errorPassword" class="error-msg">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            {{ errorPassword }}
          </div>
          <div v-else class="helper-text">Mínimo 6 caracteres, 1 mayúscula y 1 número.</div>
        </div>

        <div class="input-group">
          <label>Confirmar Contraseña</label>
          <div class="input-wrapper" :class="{ 'focused': focusedField === 'confirm', 'error-border': errorConfirmacion }">
            <input 
              v-model="confirmPassword" 
              :type="mostrarPass ? 'text' : 'password'" 
              placeholder="Repetí tu nueva contraseña" 
              required
              @focus="focusedField = 'confirm'"
              @blur="focusedField = ''"
            />
          </div>
          <div v-if="errorConfirmacion" class="error-msg">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            {{ errorConfirmacion }}
          </div>
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

// Validaciones separadas para una mejor UX
const errorPassword = computed(() => {
  if (!password.value) return "" // No mostrar error si está vacío
  if (password.value.length < 6) return "Debe tener al menos 6 caracteres"
  if (!/(?=.*[A-Z])/.test(password.value)) return "Debe incluir al menos una letra mayúscula"
  if (!/(?=.*\d)/.test(password.value)) return "Debe incluir al menos un número"
  return ""
})

const errorConfirmacion = computed(() => {
  if (!confirmPassword.value) return "" // No mostrar error si está vacío
  if (password.value !== confirmPassword.value) return "Las contraseñas no coinciden"
  return ""
})

const esValido = computed(() => {
  return password.value.length >= 6 && 
         /(?=.*[A-Z])/.test(password.value) && 
         /(?=.*\d)/.test(password.value) && 
         password.value === confirmPassword.value;
})

const guardarPassword = async () => {
  if (!esValido.value) return
  cargando.value = true
  try {
    await axios.post(`${API_BASE}/api/password-reset/confirmar/`, {
      token, nueva_password: password.value, confirmar_password: confirmPassword.value
    })
    Swal.fire({
      icon: 'success', title: '¡Perfecto!', text: 'Contraseña actualizada correctamente.',
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
/* --- LAYOUT & FONDO --- */
.premium-layout {
  min-height: 100vh;
  display: flex; justify-content: center; align-items: center;
  background-color: #0f172a;
  position: relative; overflow: hidden;
  font-family: 'Segoe UI', system-ui, sans-serif;
  padding: 20px;
}

.background-glow {
    position: absolute;
    width: 600px; height: 600px;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    z-index: 0;
    background: radial-gradient(circle, rgba(14, 165, 233, 0.15) 0%, transparent 70%);
    animation: pulseGlow 8s infinite alternate;
}

@keyframes pulseGlow {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; }
}

/* --- TARJETA --- */
.auth-card {
  width: 100%; max-width: 420px; 
  z-index: 1;
  background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 40px 35px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  box-sizing: border-box;
  animation: fadeInScale 0.5s ease-out;
}

@keyframes fadeInScale { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }

/* Headers */
.card-header { text-align: center; margin-bottom: 30px; }
.icon-container { position: relative; width: 64px; height: 64px; margin: 0 auto 16px; display: flex; justify-content: center; align-items: center; }
.icon-bg {
  position: absolute; width: 100%; height: 100%;
  background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
  border-radius: 50%; opacity: 0.2;
  filter: blur(8px);
}
.icon { position: relative; z-index: 2; display: flex; }
.card-header h1 { color: #f8fafc; font-size: 24px; font-weight: 700; margin: 0 0 8px 0; letter-spacing: -0.5px; }
.card-header p { color: #94a3b8; font-size: 14px; margin: 0; }

/* Inputs */
.input-group { margin-bottom: 22px; width: 100%; }
.input-group label {
  display: block; color: #cbd5e1; font-size: 12px; font-weight: 600;
  margin-bottom: 8px; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;
}
.input-wrapper {
  position: relative; width: 100%;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #334155;
  border-radius: 10px;
  transition: all 0.2s ease;
  display: flex; align-items: center; box-sizing: border-box;
}

.input-wrapper.focused { border-color: #0ea5e9; box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15); background: rgba(15, 23, 42, 0.8); }
.input-wrapper.error-border { border-color: #ef4444; }

.input-wrapper input {
  flex-grow: 1; width: 100%; padding: 14px 16px;
  background: transparent; border: none; color: white;
  font-size: 15px; outline: none; box-sizing: border-box;
}
.input-wrapper input::placeholder { color: #475569; }

.eye-btn {
  background: none; border: none; cursor: pointer;
  padding: 0 16px; display: flex; align-items: center; justify-content: center;
  color: #64748b; transition: color 0.2s;
}
.eye-btn:hover { color: #cbd5e1; }

.helper-text { color: #64748b; font-size: 12px; margin-top: 6px; }
.error-msg { 
  color: #ef4444; font-size: 13px; margin-top: 6px; 
  display: flex; align-items: center; animation: shake 0.4s ease-in-out; 
}
@keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-4px); } 75% { transform: translateX(4px); } }

/* Botón */
.submit-btn {
  width: 100%; padding: 15px; margin-top: 10px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white; border: none; border-radius: 10px;
  font-size: 15px; font-weight: 600; cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px 0 rgba(14, 165, 233, 0.39);
  display: flex; justify-content: center; align-items: center;
}

.submit-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4); }
.submit-btn:active:not(:disabled) { transform: translateY(1px); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; filter: grayscale(0.3); box-shadow: none; }

/* --- OCULTAR EL OJITO NATIVO DEL NAVEGADOR --- */
input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear {
  display: none;
}
input[type="password"]::-webkit-reveal {
  display: none;
}

.spinner { width: 18px; height: 18px; border: 2.5px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>