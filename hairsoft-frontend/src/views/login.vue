<template>
  <div class="login-page">
    <div :class="['login-card', { 'visible': isVisible, 'shake': shake }]">
      <!-- Logo Section -->
      <div class="logo-container">
        <div class="logo-circle">
          <div class="logo-inner">
            <svg viewBox="0 0 64 64" class="logo-svg" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Cabeza -->
              <circle cx="32" cy="28" r="14" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <!-- Cuerpo -->
              <path d="M 20 40 Q 20 42 22 42 L 42 42 Q 44 42 44 40" stroke="white" stroke-width="3" stroke-linecap="round" fill="none"/>
              <line x1="22" y1="42" x2="22" y2="50" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <line x1="42" y1="42" x2="42" y2="50" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <!-- Estrella decorativa -->
              <path d="M 32 18 L 33 21 L 36 21 L 34 23 L 35 26 L 32 24 L 29 26 L 30 23 L 28 21 L 31 21 Z" fill="white"/>
            </svg>
          </div>
        </div>
        <h1 class="logo-title">HairSoft</h1>
        <p class="logo-subtitle">Sistema de gestión para peluquerías</p>
      </div>
      
      <!-- Form Section -->
      <div class="form-section">
        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Email Input -->
          <div class="input-group">
            <div class="input-wrapper">
              <Mail class="input-icon" :size="20" />
              <input
                v-model="credentials.username"
                required
                placeholder="Correo electrónico"
                type="email"
                class="form-input"
                :disabled="loading"
              />
            </div>
          </div>
          
          <!-- Password Input -->
          <div class="input-group">
            <div class="input-wrapper">
              <Lock class="input-icon" :size="20" />
              <input
                v-model="credentials.password"
                required
                placeholder="Contraseña"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                :disabled="loading"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                :disabled="loading"
              >
                <EyeOff v-if="showPassword" :size="20" />
                <Eye v-else :size="20" />
              </button>
            </div>
          </div>

          <!-- Forgot Password -->
          <div class="forgot-password">
            <a href="#" @click.prevent="handleForgotPassword" class="forgot-link">
              ¿Olvidaste tu contraseña?
            </a>
          </div>
          
          <!-- Login Button -->
          <button 
            type="submit"
            class="submit-button"
            :class="{ 'loading': loading }"
            :disabled="loading || !formValid"
          >
            <span v-if="!loading" class="button-content">
              <span class="button-text">Iniciar Sesión</span>
              <svg class="button-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </span>
            <div v-else class="button-loader">
              <div class="spinner"></div>
              <span>Iniciando...</span>
            </div>
          </button>
          
          <!-- Back Link -->
          <div class="back-link-container">
            <router-link to="/web/home" class="back-link">
              <svg class="back-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              <span>Volver al sitio web</span>
            </router-link>
          </div>

          <!-- Register Link -->
          <div class="register-link-container">
            <span class="register-text">¿No tienes cuenta? </span>
            <router-link to="/web/registro" class="register-link">
              Regístrate aquí
            </router-link>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="footer-section">
        <div class="footer-content">
          <p class="footer-text">Los Ultimos Serán Los Primeros</p>
          <div class="footer-divider"></div>
          <div class="footer-meta">
          </div>
        </div>
      </div>
    </div>
    
    <!-- Background Elements -->
    <div class="bg-blur-1"></div>
    <div class="bg-blur-2"></div>
    <div class="bg-blur-3"></div>
    <div class="bg-grid"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';
import { Mail, Lock, Eye, EyeOff } from 'lucide-vue-next';

const router = useRouter();
const API_BASE = 'http://127.0.0.1:8000/usuarios';

// Reactive state
const credentials = ref({
  username: '',
  password: ''
});

const loading = ref(false);
const showPassword = ref(false);
const isVisible = ref(false);
const shake = ref(false);

// Computed property for form validation
const formValid = computed(() => {
  return credentials.value.username.trim() !== '' && 
         credentials.value.password.trim() !== '';
});

onMounted(() => {
  // Check for saved credentials
  const savedEmail = localStorage.getItem('saved_email');
  if (savedEmail) {
    credentials.value.username = savedEmail;
  }
  
  // Trigger entrance animation
  setTimeout(() => {
    isVisible.value = true;
  }, 100);
});

const handleLogin = async () => {
  if (!formValid.value) return;
  
  loading.value = true;
  
  try {
    const response = await axios.post(`${API_BASE}/api/auth/login/`, credentials.value);
    
    if (response.data.status === 'ok') {
      // Save credentials (optional)
      localStorage.setItem('saved_email', credentials.value.username);
      
      // Save authentication data
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('user_rol', response.data.rol);
      localStorage.setItem('user_nombre', response.data.nombre || 'Usuario');
      localStorage.setItem('user_apellido', response.data.apellido || '');
      
      // Configure axios defaults
      axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`;
      axios.defaults.headers.common['User-Id'] = response.data.user_id;
      axios.defaults.headers.common['User-Rol'] = response.data.rol;

      // Notify other components
      window.dispatchEvent(new Event('userChanged'));
      
      // Success notification
      Swal.fire({
        title: '¡Bienvenido!',
        text: `Hola ${response.data.nombre || 'Usuario'}, has iniciado sesión exitosamente.`,
        icon: 'success',
        showConfirmButton: false,
        timer: 2000,
        background: '#1e293b',
        color: '#f1f5f9',
        iconColor: '#007bff'
      });

      // Redirect based on role
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
    console.error('Login error:', error);
    
    // Shake animation for error
    shake.value = true;
    setTimeout(() => {
      shake.value = false;
    }, 500);
    
    // Error notification
    Swal.fire({
      title: 'Error de autenticación',
      text: error.response?.data?.message || 
            error.response?.data?.error || 
            'Credenciales incorrectas. Por favor, verifica tu información.',
      icon: 'error',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#007bff',
      background: '#1e293b',
      color: '#f1f5f9',
      iconColor: '#ef4444'
    });
  } finally {
    loading.value = false;
  }
};

const handleForgotPassword = () => {
  Swal.fire({
    title: 'Recuperar contraseña',
    html: `
      <p>Ingresa tu correo electrónico y te enviaremos un enlace para restablecer tu contraseña.</p>
      <input type="email" id="recovery-email" class="swal2-input" placeholder="Correo electrónico" value="${credentials.value.username}">
    `,
    showCancelButton: true,
    confirmButtonText: 'Enviar enlace',
    confirmButtonColor: '#007bff',
    cancelButtonText: 'Cancelar',
    background: '#1e293b',
    color: '#f1f5f9',
    preConfirm: () => {
      const email = Swal.getPopup().querySelector('#recovery-email').value;
      if (!email) {
        Swal.showValidationMessage('Por favor ingresa tu correo electrónico');
      } else if (!/^\S+@\S+\.\S+$/.test(email)) {
        Swal.showValidationMessage('Por favor ingresa un correo válido');
      }
      return { email: email };
    }
  }).then((result) => {
    if (result.isConfirmed) {
      // Here you would typically make an API call
      Swal.fire({
        title: '¡Enlace enviado!',
        text: 'Revisa tu correo electrónico para restablecer tu contraseña.',
        icon: 'success',
        confirmButtonColor: '#007bff',
        background: '#1e293b',
        color: '#f1f5f9',
        iconColor: '#007bff'
      });
    }
  });
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* Background Effects */
.bg-blur-1, .bg-blur-2, .bg-blur-3 {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.2;
  z-index: 0;
  animation: float 20s ease-in-out infinite;
}

.bg-blur-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #007bff, transparent);
  top: -200px;
  right: -200px;
  animation-delay: 0s;
}

.bg-blur-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #0056b3, transparent);
  bottom: -250px;
  left: -250px;
  animation-delay: 7s;
}

.bg-blur-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #00d4ff, transparent);
  top: 40%;
  right: 20%;
  animation-delay: 14s;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(0, 123, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 123, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  z-index: 0;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

/* Login Card */
.login-card {
  max-width: 520px;
  width: 100%;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 32px;
  padding: 50px 48px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
  opacity: 0;
  transform: translateY(30px) scale(0.95);
  transition: all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 1;
  position: relative;
}

.login-card.visible {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.login-card.shake {
  animation: shakeError 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97);
}

@keyframes shakeError {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-8px); }
  20%, 40%, 60%, 80% { transform: translateX(8px); }
}

/* Logo Section */
.logo-container {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 2px solid rgba(0, 123, 255, 0.08);
}

.logo-circle {
  width: 92px;
  height: 92px;
  background: linear-gradient(135deg, #007bff 0%, #00b4ff 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 
    0 12px 28px rgba(0, 123, 255, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
}

.logo-circle::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: translateX(-100%);
  animation: shine 3s ease-in-out infinite;
}

@keyframes shine {
  0% { transform: translateX(-100%); }
  50%, 100% { transform: translateX(100%); }
}

.logo-circle:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 
    0 16px 32px rgba(0, 123, 255, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.logo-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-svg {
  width: 50px;
  height: 50px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.logo-title {
  font-weight: 800;
  font-size: 38px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.logo-subtitle {
  color: #64748b;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.2px;
}

/* Form Section */
.form-section {
  margin-bottom: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  position: relative;
  width: 100%;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 20px;
  color: #94a3b8;
  pointer-events: none;
  transition: all 0.3s ease;
  z-index: 2;
}

.form-input {
  width: 100%;
  background: white;
  border: 2px solid #e2e8f0;
  padding: 20px 60px 20px 54px;
  border-radius: 14px;
  font-size: 16px;
  font-family: inherit;
  color: #1e293b;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  box-sizing: border-box;
  height: 60px;
}

.form-input::placeholder {
  color: #cbd5e1;
}

.form-input:focus {
  outline: none;
  border-color: #007bff;
  background: #f8faff;
  box-shadow: 
    0 0 0 4px rgba(0, 123, 255, 0.08),
    0 4px 12px rgba(0, 123, 255, 0.15);
  transform: translateY(-1px);
}

.form-input:focus ~ .input-icon,
.input-wrapper:focus-within .input-icon {
  color: #007bff;
  transform: scale(1.1);
}

.form-input:disabled {
  background: #f8fafc;
  cursor: not-allowed;
  opacity: 0.6;
}

.password-toggle {
  position: absolute;
  right: 18px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  border-radius: 10px;
}

.password-toggle:hover:not(:disabled) {
  color: #007bff;
  background: rgba(0, 123, 255, 0.08);
  transform: scale(1.1);
}

.password-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Forgot Password */
.forgot-password {
  text-align: right;
  margin-top: -8px;
}

.forgot-link {
  font-size: 14px;
  color: #007bff;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  padding: 6px 12px;
  border-radius: 8px;
  display: inline-block;
}

.forgot-link:hover {
  color: #0056b3;
  background: rgba(0, 123, 255, 0.06);
  text-decoration: none;
  transform: translateX(-2px);
}

/* Submit Button */
.submit-button {
  width: 100%;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 20px 24px;
  margin-top: 12px;
  border-radius: 14px;
  border: none;
  font-size: 17px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 
    0 8px 16px rgba(0, 123, 255, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.submit-button:hover:not(:disabled)::before {
  transform: translateX(100%);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 
    0 12px 24px rgba(0, 123, 255, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.submit-button:active:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 
    0 4px 12px rgba(0, 123, 255, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.button-text {
  letter-spacing: 0.5px;
}

.button-arrow {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.submit-button:hover:not(:disabled) .button-arrow {
  transform: translateX(4px);
}

.button-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Back Link */
.back-link-container {
  text-align: center;
  margin-top: 20px;
}

.back-link {
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 10px 18px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.back-link:hover {
  color: #007bff;
  background: rgba(0, 123, 255, 0.06);
  text-decoration: none;
  transform: translateX(-2px);
}

.back-arrow {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.back-link:hover .back-arrow {
  transform: translateX(-4px);
}

/* Register Link */
.register-link-container {
  text-align: center;
  margin-top: 16px;
  padding: 14px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.04), rgba(0, 180, 255, 0.04));
  border: 1px solid rgba(0, 123, 255, 0.1);
  transition: all 0.3s ease;
}

.register-link-container:hover {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.06), rgba(0, 180, 255, 0.06));
  border-color: rgba(0, 123, 255, 0.15);
}

.register-text {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.2px;
}

.register-link {
  color: #007bff;
  font-weight: 700;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  padding: 2px 6px;
  border-radius: 6px;
  letter-spacing: 0.2px;
}

.register-link:hover {
  color: #0056b3;
  background: rgba(0, 123, 255, 0.1);
  text-decoration: none;
}

/* Footer Section */
.footer-section {
  margin-top: 32px;
  padding-top: 28px;
  border-top: 2px solid rgba(0, 123, 255, 0.1);
}

.footer-content {
  text-align: center;
  position: relative;
}

.footer-icon {
  font-size: 24px;
  margin-bottom: 12px;
  display: inline-block;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { 
    transform: scale(1);
    opacity: 1;
  }
  50% { 
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.footer-text {
  color: #64748b;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.footer-divider {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #007bff, transparent);
  margin: 12px auto;
  border-radius: 2px;
}

.footer-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 500;
}

.footer-version,
.footer-year {
  color: #94a3b8;
  letter-spacing: 0.5px;
}

.footer-dot {
  color: #007bff;
  font-weight: 700;
  font-size: 16px;
}

/* Responsive Design */
@media (max-width: 600px) {
  .login-card {
    max-width: 450px;
    padding: 40px 32px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 36px 28px;
    max-width: 380px;
  }
  
  .logo-circle {
    width: 80px;
    height: 80px;
  }
  
  .logo-svg {
    width: 42px;
    height: 42px;
  }
  
  .logo-title {
    font-size: 32px;
  }
  
  .form-input {
    padding: 18px 54px 18px 48px;
    font-size: 15px;
    height: 56px;
  }
  
  .submit-button {
    height: 56px;
    font-size: 16px;
  }
  
  .input-icon {
    left: 16px;
  }
  
  .password-toggle {
    right: 16px;
  }
}

@media (max-width: 350px) {
  .login-card {
    padding: 28px 20px;
  }
  
  .logo-title {
    font-size: 28px;
  }
  
  .logo-subtitle {
    font-size: 13px;
  }
}
</style>