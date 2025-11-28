<template>
  <div class="login-page">
    <div :class="['container', { 'visible': isVisible, 'shake': shake }]">
      <div class="logo-section">
        <div class="heading">HairSoft</div>
        <p class="sub-heading">Sistema de gestión para peluquerías</p>
      </div>
      
      <div class="form">
        <div class="input-wrapper">
          <Mail :size="20" class="input-icon" />
          <input
            v-model="credentials.username"
            required
            placeholder="Correo electrónico"
            type="email"
            class="input"
          />
        </div>
        
        <div class="input-wrapper">
          <Lock :size="20" class="input-icon" />
          <input
            v-model="credentials.password"
            required
            placeholder="Contraseña"
            :type="showPassword ? 'text' : 'password'"
            class="input input-password"
          />
          <button
            type="button"
            class="toggle-password"
            @click="showPassword = !showPassword"
          >
            <EyeOff v-if="showPassword" :size="20" />
            <Eye v-else :size="20" />
          </button>
        </div>

        <span class="forgot-password">
          <a href="#" @click.prevent>¿Olvidaste tu contraseña?</a>
        </span>
        
        <button 
          @click="handleLogin"
          class="login-button" 
          :disabled="loading"
        >
          <span v-if="!loading">Iniciar Sesión</span>
          <span v-else class="loader"></span>
        </button>
      </div>

      <div class="footer-text">
        Los Ultimos Serán Los Primeros
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';
import { Mail, Lock, Eye, EyeOff } from 'lucide-vue-next';

const router = useRouter();
// Asegúrate que este puerto sea el correcto (normalmente 8000 para Django)
const API_BASE = 'http://127.0.0.1:8000/usuarios';

const credentials = ref({
  username: '',
  password: ''
});

const loading = ref(false);
const showPassword = ref(false);
const isVisible = ref(false);
const shake = ref(false);

onMounted(() => {
  isVisible.value = true;
});

const handleLogin = async () => {
  loading.value = true;
  
  try {
    const response = await axios.post(`${API_BASE}/api/auth/login/`, credentials.value);
    
    if (response.data.status === 'ok') {
      // ✅ 1. GUARDAR TOKEN (¡CRUCIAL!)
      localStorage.setItem('token', response.data.token);
      
      // Guardar resto de la sesión
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('user_rol', response.data.rol);
      localStorage.setItem('user_nombre', response.data.nombre || 'Usuario');
      localStorage.setItem('user_apellido', response.data.apellido || '');
      
      // ✅ 2. Configurar headers globales para Axios
      // Esto ayuda a que otras peticiones simples ya tengan el token
      axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`;
      axios.defaults.headers.common['User-Id'] = response.data.user_id;
      axios.defaults.headers.common['User-Rol'] = response.data.rol;

      // Notificar a todos los componentes que el usuario cambió
      window.dispatchEvent(new Event('userChanged'));
      
      const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
          toast.addEventListener('mouseenter', Swal.stopTimer);
          toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
      });

      Toast.fire({
        icon: 'success',
        title: '¡Bienvenido a HairSoft!'
      });

      router.push('/dashboard');
    }
  } catch (error) {
    console.error(error);
    
    shake.value = true;
    setTimeout(() => {
      shake.value = false;
    }, 500);
    
    Swal.fire({
      icon: 'error',
      title: 'Acceso denegado',
      text: error.response?.data?.message || error.response?.data?.error || 'Credenciales incorrectas',
      confirmButtonColor: '#007bff'
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background-color: #0f172a;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.container {
  max-width: 480px;
  width: 100%;
  background: #F8F9FD;
  border-radius: 40px;
  padding: 45px 50px;
  border: 5px solid rgb(255, 255, 255);
  box-shadow: rgba(0, 123, 255, 0.3) 0px 30px 60px -20px;
  opacity: 0;
  transform: translateY(30px);
  transition: transform 0.3s ease;
}

.container.visible {
  animation: slideUp 0.6s ease forwards;
}

@keyframes slideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.container.shake {
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

.logo-section {
  text-align: center;
  margin-bottom: 35px;
  padding-bottom: 25px;
  border-bottom: 2px solid #e9ecef;
}

.heading {
  font-weight: 900;
  font-size: 36px;
  color: #007bff;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.sub-heading {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

.form {
  margin-top: 30px;
}

.input-wrapper {
  position: relative;
  margin-top: 18px;
}

.input-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
  transition: color 0.3s ease;
}

.input {
  width: 100%;
  background: white;
  border: none;
  padding: 15px 20px 15px 50px;
  border-radius: 20px;
  box-shadow: rgba(0, 123, 255, 0.15) 0px 10px 10px -5px;
  border: 2px solid transparent;
  font-size: 14px;
  font-family: inherit;
  color: #1a1a1a;
  transition: all 0.3s ease;
}

.input::placeholder {
  color: rgb(170, 170, 170);
}

.input:focus {
  outline: none;
  border: 2px solid #007bff;
  box-shadow: rgba(0, 123, 255, 0.25) 0px 10px 20px -5px;
}

.input:focus ~ .input-icon {
  color: #007bff;
}

.input-password {
  padding-right: 50px;
}

.input-password::-ms-reveal,
.input-password::-ms-clear {
  display: none;
}

.input-password::-webkit-contacts-auto-fill-button,
.input-password::-webkit-credentials-auto-fill-button {
  visibility: hidden;
  pointer-events: none;
  position: absolute;
  right: 0;
}

.toggle-password {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s ease;
}

.toggle-password:hover {
  color: #007bff;
}

.forgot-password {
  display: block;
  margin-top: 12px;
  margin-left: 10px;
}

.forgot-password a {
  font-size: 12px;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.forgot-password a:hover {
  color: #0056b3;
  text-decoration: underline;
}

.login-button {
  display: block;
  width: 100%;
  font-weight: bold;
  background: linear-gradient(45deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 15px;
  margin: 25px auto 20px;
  border-radius: 20px;
  box-shadow: rgba(0, 123, 255, 0.4) 0px 20px 10px -15px;
  border: none;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  font-size: 16px;
  font-family: inherit;
}

.login-button:hover:not(:disabled) {
  transform: scale(1.03);
  box-shadow: rgba(0, 123, 255, 0.5) 0px 23px 10px -20px;
}

.login-button:active:not(:disabled) {
  transform: scale(0.95);
  box-shadow: rgba(0, 123, 255, 0.4) 0px 15px 10px -10px;
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loader {
  width: 20px;
  height: 20px;
  border: 3px solid #fff;
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.footer-text {
  text-align: center;
  color: #64748b;
  font-size: 13px;
  margin-top: 30px;
  padding-top: 15px;
  border-top: 1px solid #d1d5db;
  font-weight: 400;
  letter-spacing: 0.3px;
  line-height: 1.6;
}

@media (max-width: 480px) {
  .container {
    padding: 35px 30px;
    max-width: 380px;
  }
  
  .heading {
    font-size: 32px;
  }
}
</style>