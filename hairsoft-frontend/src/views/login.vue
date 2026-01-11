<template>
  <div class="auth-page">
    <div class="auth-container">
      
      <div class="visual-panel">
        <div class="image-wrapper">
          <div class="gradient-overlay"></div>
          <div class="content-block">
            <h1>Los Últimos<br/>Serán Los Primeros</h1>
            <p>Tu estilo, nuestra pasión. Gestioná tus turnos y descubrí la mejor experiencia en gestión de peluquería.</p>
          </div>
        </div>
      </div>

      <div class="auth-panel">
        <div class="auth-wrapper">
          
          <div class="brand-header">
            <div class="brand-icon">
              <div class="icon-glow"></div>
              <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="32" cy="28" r="14" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                <path d="M 20 40 Q 20 42 22 42 L 42 42 Q 44 42 44 40" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/>
                <line x1="22" y1="42" x2="22" y2="50" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                <line x1="42" y1="42" x2="42" y2="50" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                <path d="M 32 18 L 33 21 L 36 21 L 34 23 L 35 26 L 32 24 L 29 26 L 30 23 L 28 21 L 31 21 Z" fill="currentColor"/>
              </svg>
            </div>
            <h1>HairSoft</h1>
            <p>Bienvenido de vuelta</p>
          </div>

          <form @submit.prevent="handleLogin" class="auth-form">
            
            <div class="input-field">
              <label>Correo Electrónico</label>
              <div class="input-wrap">
                <div class="icon">
                  <Mail :size="20" />
                </div>
                <input
                  v-model="credentials.username"
                  type="email"
                  placeholder="nombre@ejemplo.com"
                  required
                  :disabled="loading"
                  autocomplete="email"
                />
              </div>
            </div>

            <div class="input-field">
              <label>Contraseña</label>
              <div class="input-wrap">
                <div class="icon">
                  <Lock :size="20" />
                </div>
                <input
                  v-model="credentials.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Ingresá tu contraseña"
                  required
                  :disabled="loading"
                  autocomplete="current-password"
                />
                <button
                  type="button"
                  class="toggle-btn"
                  @click="showPassword = !showPassword"
                  :disabled="loading"
                  tabindex="-1"
                >
                  <EyeOff v-if="showPassword" :size="20" />
                  <Eye v-else :size="20" />
                </button>
              </div>
            </div>

            <div class="form-footer">
              <a href="#" @click.prevent="handleForgotPassword" class="link-secondary">
                ¿Olvidaste tu contraseña?
              </a>
            </div>

            <button 
              type="submit"
              class="btn-primary"
              :disabled="loading || !formValid"
            >
              <span class="btn-bg"></span>
              <span class="btn-content">
                <template v-if="!loading">
                  <span>Iniciar Sesión</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </template>
                <template v-else>
                  <span class="spinner"></span>
                  <span>Iniciando...</span>
                </template>
              </span>
            </button>

            <div class="divider">
              <span></span>
            </div>

            <div class="alt-actions">
              <p class="register-prompt">
                ¿No tenés cuenta? 
                <router-link to="/web/registro">Crear cuenta</router-link>
              </p>
              <router-link to="/web/home" class="link-home">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
                Volver al inicio
              </router-link>
            </div>
          </form>

          <div class="tagline">
            Los Últimos Serán Los Primeros
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';
import { Mail, Lock, Eye, EyeOff } from 'lucide-vue-next';

const router = useRouter();

// --- CONFIGURACIÓN HÍBRIDA (PRODUCCIÓN vs LOCAL) ---

const isProduction = window.location.hostname.includes('vercel.app');
const API_BASE = isProduction 
  ? 'https://web-production-ac47c.up.railway.app/usuarios' 
  : 'http://127.0.0.1:8000/usuarios';

console.log('🌐 Login conectado a:', API_BASE);

const credentials = ref({
  username: '',
  password: ''
});

const loading = ref(false);
const showPassword = ref(false);

const formValid = computed(() => {
  return credentials.value.username.trim() !== '' && 
         credentials.value.password.trim() !== '';
});

onMounted(() => {
  const savedEmail = localStorage.getItem('saved_email');
  if (savedEmail) {
    credentials.value.username = savedEmail;
  }
});

const handleLogin = async () => {
  if (!formValid.value) return;
  loading.value = true;
  
  try {
    // Usamos la URL dinámica que definimos arriba
    const response = await axios.post(`${API_BASE}/api/auth/login/`, credentials.value);
    
    if (response.data.status === 'ok') {
      localStorage.setItem('saved_email', credentials.value.username);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('user_rol', response.data.rol);
      localStorage.setItem('user_nombre', response.data.nombre || 'Usuario');
      localStorage.setItem('user_apellido', response.data.apellido || '');
      
      axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`;
      window.dispatchEvent(new Event('userChanged'));
      
      Swal.fire({
        title: '¡Bienvenido!',
        text: `Hola ${response.data.nombre || 'Usuario'}, has iniciado sesión exitosamente.`,
        icon: 'success',
        showConfirmButton: false,
        timer: 1500,
        background: '#1e293b',
        color: '#f1f5f9',
        iconColor: '#007bff'
      });

      setTimeout(() => {
        const rolUsuario = response.data.rol;
        if (rolUsuario === 'CLIENTE') {
          router.push('/cliente/dashboard');
        } else {
          router.push('/dashboard');
        }
      }, 1000);
    }
  } catch (error) {
    console.error("Error en login:", error);
    
    // Si no hay respuesta del servidor (error de red), avisamos que es conexión
    const errorMsg = error.response 
      ? (error.response.data?.message || 'Credenciales incorrectas.') 
      : 'No se pudo conectar con el servidor. Revisá tu conexión.';

    Swal.fire({
      title: 'Error de acceso',
      text: errorMsg,
      icon: 'error',
      confirmButtonColor: '#007bff',
      background: '#1e293b',
      color: '#f1f5f9'
    });
  } finally {
    loading.value = false;
  }
};

const handleForgotPassword = () => {
  Swal.fire({
    title: 'Recuperar contraseña',
    input: 'email',
    inputLabel: 'Ingresa tu correo electrónico',
    inputPlaceholder: 'tu@email.com',
    inputValue: credentials.value.username,
    showCancelButton: true,
    confirmButtonText: 'Enviar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#007bff',
    background: '#1e293b',
    color: '#f1f5f9'
  });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: 
    radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.08) 0%, transparent 50%),
    linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

.auth-page::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
  top: -300px;
  right: -300px;
  border-radius: 50%;
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(-100px, 100px) rotate(180deg); }
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 1300px;
  height: 1020px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 32px;
  overflow: hidden;
  box-shadow: 
    0 0 0 1px rgba(255, 255, 255, 0.1),
    0 50px 100px -20px rgba(0, 0, 0, 0.4),
    0 30px 60px -30px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
}

/* ==================== VISUAL PANEL ==================== */
.visual-panel {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  background-image: url('/Pelu_Login.jpg');
  background-size: cover;
  background-position: center;
  position: relative;
}

.gradient-overlay {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(
      180deg,
      rgba(15, 23, 42, 0.2) 0%,
      rgba(15, 23, 42, 0.6) 40%,
      rgba(15, 23, 42, 0.95) 100%
    );
  z-index: 1;
}

.content-block {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 64px;
  color: white;
  z-index: 2;
}

.floating-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 24px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px);
  border-radius: 100px;
  font-size: 0.8125rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 32px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.floating-badge svg {
  width: 16px;
  height: 16px;
  stroke: #fbbf24;
}

.content-block h1 {
  font-size: 3.75rem;
  font-weight: 900;
  line-height: 1.05;
  margin-bottom: 24px;
  letter-spacing: -0.06em;
  background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.content-block p {
  font-size: 1.125rem;
  line-height: 1.7;
  opacity: 0.9;
  max-width: 500px;
  font-weight: 400;
  margin-bottom: 36px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9375rem;
  font-weight: 500;
  opacity: 0.95;
}

.feature-item svg {
  width: 20px;
  height: 20px;
  stroke: #10b981;
  flex-shrink: 0;
}

/* ==================== AUTH PANEL ==================== */
.auth-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #ffffff;
  position: relative;
}

.auth-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%,
    rgba(99, 102, 241, 0.5) 50%,
    transparent 100%
  );
}

.auth-wrapper {
  width: 100%;
  max-width: 440px;
}

/* BRAND HEADER */
.brand-header {
  text-align: center;
  margin-bottom: 48px;
}

.brand-icon {
  width: 88px;
  height: 88px;
  background: linear-gradient(135deg, #1f42f0 0%, #129089 100%);
  border-radius: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 28px;
  position: relative;
  box-shadow: 
    0 20px 40px -12px rgba(99, 102, 241, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.icon-glow {
  position: absolute;
  inset: -8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 28px;
  opacity: 0.2;
  filter: blur(20px);
  z-index: -1;
}

.brand-icon svg {
  width: 48px;
  height: 48px;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

.brand-header h1 {
  font-size: 2.75rem;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 12px;
  letter-spacing: -0.05em;
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-header p {
  font-size: 1.0625rem;
  color: #64748b;
  font-weight: 600;
}

/* FORM */
.auth-form {
  width: 100%;
}

.input-field {
  margin-bottom: 26px;
}

.input-field label {
  display: block;
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12px;
  letter-spacing: -0.01em;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-wrap:hover {
  background: #ffffff;
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.05);
}

.input-wrap:focus-within {
  background: #ffffff;
  border-color: #6366f1;
  box-shadow: 
    0 0 0 4px rgba(99, 102, 241, 0.1),
    0 8px 20px -8px rgba(99, 102, 241, 0.2);
}

.icon {
  position: absolute;
  left: 20px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  pointer-events: none;
  z-index: 2;
  transition: color 0.3s;
}

.input-wrap:focus-within .icon {
  color: #6366f1;
}

.input-wrap input {
  width: 100%;
  height: 58px;
  padding: 0 20px 0 56px;
  border: none;
  background: transparent;
  font-size: 1.0rem;
  color: #0f172a;
  font-family: inherit;
  font-weight: 600;
  outline: none;
}

.input-wrap input::placeholder {
  color: #cbd5e1;
  font-weight: 400;
}

.toggle-btn {
  position: absolute;
  right: 14px;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 10px;
  display: flex;
  align-items: center;
  border-radius: 10px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  color: #6366f1;
  background: #f1f5f9;
}

/* FORM FOOTER */
.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 32px;
}

.link-secondary {
  font-size: 0.9375rem;
  color: #6366f1;
  text-decoration: none;
  font-weight: 700;
  transition: all 0.2s;
  position: relative;
}

.link-secondary::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: #6366f1;
  transition: width 0.3s;
}

.link-secondary:hover::after {
  width: 100%;
}

/* PRIMARY BUTTON */
.btn-primary {
  width: 100%;
  height: 58px;
  background: transparent;
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 1.0625rem;
  font-weight: 800;
  cursor: pointer;
  font-family: inherit;
  position: relative;
  overflow: hidden;
  letter-spacing: -0.01em;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #2f4ff3 0%, #1d8cbb 100%);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover:not(:disabled) .btn-bg {
  background: linear-gradient(135deg, #4f46e5 0%, #2b83fe 100%);
  box-shadow: 
    0 16px 32px -8px rgba(99, 102, 241, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 20px 40px -12px rgba(99, 241, 210, 0.6);
}

.btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 100%;

}

.btn-content svg {
  width: 20px;
  height: 20px;
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* DIVIDER */
.divider {
  display: flex;
  align-items: center;
  margin: 36px 0;
  position: relative;
}

.divider::before {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
}

.divider span {
  padding: 0 20px;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 600;
}

/* ALT ACTIONS */
.alt-actions {
  text-align: center;
}

.register-prompt {
  font-size: 0.9375rem;
  color: #64748b;
  margin-bottom: 18px;
  font-weight: 500;
}

.register-prompt a {
  color: #6366f1;
  font-weight: 800;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.2s;
}

.register-prompt a:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.link-home {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 700;
  padding: 10px 20px;
  border-radius: 10px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.link-home svg {
  width: 18px;
  height: 18px;
}

.link-home:hover {
  color: #6366f1;
  background: #f8fafc;
  border-color: #e2e8f0;
}

/* TAGLINE */
.tagline {
  text-align: center;
  margin-top: 44px;
  font-size: 0.8125rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 800;
}

/* RESPONSIVE */
@media (max-width: 1100px) {
  .auth-container {
    max-width: 1200px;
    height: 680px;
  }
  
  .content-block h1 {
    font-size: 3rem;
  }
}

@media (max-width: 900px) {
  .auth-page {
    padding: 20px;
  }
  
  .auth-container {
    flex-direction: column;
    height: auto;
    max-width: 600px;
  }
  
  .visual-panel {
    min-height: 360px;
    max-height: 360px;
  }
  
  .content-block {
    padding: 48px;
  }
  
  .content-block h1 {
    font-size: 2.5rem;
  }
  
  .content-block p {
    font-size: 1rem;
  }
  
  .auth-panel {
    padding: 48px 32px;
  }
}

@media (max-width: 600px) {
  .auth-page {
    padding: 0;
    align-items: flex-start;
  }
  
  .auth-container {
    border-radius: 0;
    min-height: 100vh;
  }
  
  .visual-panel {
    min-height: 280px;
    max-height: 280px;
  }
  
  .content-block {
    padding: 36px;
  }
  
  .content-block h1 {
    font-size: 2rem;
  }
  
  .floating-badge {
    padding: 8px 18px;
    font-size: 0.75rem;
  }
  
  .features {
    gap: 10px;
  }
  
  .feature-item {
    font-size: 0.875rem;
  }
  
  .brand-header {
    margin-bottom: 36px;
  }
  
  .brand-header h1 {
    font-size: 2.25rem;
  }
  
  .auth-panel {
    padding: 36px 24px;
  }
}
</style>