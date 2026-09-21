<template>
  <div class="auth-page" :class="{ 'con-imagen': imagenLoginActiva }" :style="pageStyle">

    <!-- ==================== PANEL VISUAL (identidad: imagen_login) ==================== -->
    <aside class="visual-panel" :class="{ 'sin-imagen': !imagenLoginActiva }">
      <template v-if="imagenLoginActiva">
        <div class="visual-bg" :style="visualBgStyle" aria-hidden="true"></div>
        <div class="visual-figure">
          <img :src="configWeb.imagen_login" class="visual-img" alt="Imagen del local" />
        </div>
        <!-- Degradado inferior sutil: mejora el contraste del texto sobre zonas claras de la imagen -->
        <div class="visual-scrim" aria-hidden="true"></div>
      </template>
      <div class="visual-overlay"></div>

      <div class="visual-content">
        <div class="visual-message">
          <h1 class="visual-title">{{ razonSocial }}</h1>
          <p class="visual-sub">Tu peluquería, todo en un solo lugar</p>
        </div>
      </div>
    </aside>

    <!-- ==================== PANEL DEL FORMULARIO ==================== -->
    <main class="auth-panel">
      <div class="auth-wrapper">

        <header class="auth-heading">
          <h1 class="auth-title">Bienvenido!</h1>
          <p class="auth-sub">Ingresá tu email y contraseña para continuar.</p>
        </header>

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
              <router-link :to="{ path: '/web/registro', query: route.query.redirect ? { redirect: route.query.redirect } : {} }">Crear cuenta</router-link>
            </p>
            <router-link to="/web/home" class="link-home">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              Volver al inicio
            </router-link>
          </div>
        </form>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';
import { Mail, Lock, Eye, EyeOff } from 'lucide-vue-next';
import { GoogleLogin } from 'vue3-google-login'; // Importamos el componente de Google

const router = useRouter();
const route = useRoute();

const isProduction = window.location.hostname.includes('vercel.app');
const DOMAIN = isProduction ? 'https://web-production-ac47c.up.railway.app' : 'http://127.0.0.1:8000';
const API_URL = `${DOMAIN}/api/auth/login/`;
// Configuración pública (endpoint sin autenticación) — branding + imagen del Login
const WEB_CONFIG_URL = `${DOMAIN}/api/web/configuracion/`;

const credentials = ref({
  username: '',
  password: ''
});

const loading = ref(false);
const showPassword = ref(false);

// ---------------- Configuración pública (Ajustes del Local -> Logo y Marca Visual) ----------------
const configWeb = ref({
  razon_social: 'HairSoft',
  imagen_login: null,
  mostrar_imagen_login: true,
});

const mostrarLoginImagen = computed(() => configWeb.value.mostrar_imagen_login !== false);
const imagenLoginActiva = computed(() => mostrarLoginImagen.value && !!configWeb.value.imagen_login);
const razonSocial = computed(() => (configWeb.value.razon_social || '').trim() || 'HairSoft');

const visualBgStyle = computed(() =>
  imagenLoginActiva.value ? { backgroundImage: `url('${configWeb.value.imagen_login}')` } : {}
);

const pageStyle = computed(() =>
  imagenLoginActiva.value ? { '--login-img': `url('${configWeb.value.imagen_login}')` } : {}
);

const cargarConfigWeb = async () => {
  try {
    const { data } = await axios.get(WEB_CONFIG_URL);
    configWeb.value = { ...configWeb.value, ...data };
  } catch (e) {
    console.error('No se pudo cargar la configuración del Login', e);
  }
};

const formValid = computed(() => credentials.value.username.trim() !== '' && credentials.value.password.trim() !== '');

onMounted(() => {
  cargarConfigWeb();

  const savedEmail = localStorage.getItem('saved_email');
  if (savedEmail) credentials.value.username = savedEmail;
  
  const query = route.query;
  if (query.post_payment === 'true') {
    setTimeout(() => {
      Swal.fire({ title: '¡Pago Confirmado! ✅', text: 'Tu pago fue procesado exitosamente.', icon: 'success', timer: 3000 });
    }, 500);
    localStorage.setItem('pending_payment', JSON.stringify({ type: query.type, id: query.id, timestamp: new Date().getTime() }));
  }
});

// 🟢 LA MAGIA DE GOOGLE ESTÁ ACÁ
const handleGoogleLogin = async (response) => {
  loading.value = true;
  try {
    const googleToken = response.credential;
    
    // Le mandamos el token al Backend
    const res = await axios.post(`${DOMAIN}/api/auth/google/`, { token: googleToken });

    if (res.status === 200 || res.status === 201) {
      // ✅ ESCENARIO A: EL CORREO YA EXISTÍA EN LA BD -> Lo dejamos pasar
      const data = res.data;
      
      // 🔥 ACÁ ESTÁN LAS VARIABLES CORREGIDAS PARA QUE COINCIDAN CON DJANGO 🔥
      localStorage.setItem('token', data.token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('user_rol', data.rol);
      localStorage.setItem('user_nombre', data.nombre);
      localStorage.setItem('user_apellido', data.apellido || '');
      localStorage.setItem('login_fresh', 'true');
      
      Swal.fire({ title: '¡Bienvenido!', text: `Hola ${data.nombre}`, icon: 'success', timer: 1500 });
      
      setTimeout(() => {
        if (data.rol === 'CLIENTE') router.push('/cliente/dashboard');
        else router.push('/dashboard');
      }, 1000);

    } else if (res.status === 202) {
      // 🟡 ESCENARIO B: ES UN USUARIO NUEVO -> A pedir DNI y Clave
      const datosGoogle = res.data.datos_google;
      
      // Guardamos en memoria los datos que nos regaló Google para no hacérselos tipear de nuevo
      sessionStorage.setItem('google_draft', JSON.stringify(datosGoogle));
      
      Swal.fire({
        title: '¡Casi listo!',
        text: 'Vemos que es tu primera vez. Necesitamos un par de datos más para crear tu cuenta.',
        icon: 'info',
        confirmButtonText: 'Completar Perfil',
        background: '#1e293b',
        color: '#f1f5f9',
        confirmButtonColor: '#6366f1'
      }).then(() => {
        // Lo mandamos al registro, pero con una banderita en la URL
        router.push('/web/registro?google=true');
      });
    }

  } catch (error) {
    console.error("❌ Error en Google Login:", error);
    Swal.fire({
      title: 'Error',
      text: 'No se pudo iniciar sesión con Google.',
      icon: 'error',
      background: '#1e293b', color: '#f1f5f9'
    });
  } finally {
    loading.value = false;
  }
};

// LOGIN TRADICIONAL
const handleLogin = async () => {
  if (!formValid.value) return;
  loading.value = true;
  
  try {
    const response = await axios.post(API_URL, credentials.value);
    const data = response.data || response; 

    if (typeof data === 'string' && data.startsWith('<!DOCTYPE')) throw new Error('Ruta API incorrecta');

    if (data.status === 'ok') {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('user_rol', data.rol);
      localStorage.setItem('user_nombre', data.nombre);
      localStorage.setItem('user_apellido', data.apellido || '');
      localStorage.setItem('login_fresh', 'true');
      
      Swal.fire({ title: '¡Bienvenido!', text: `Hola ${data.nombre}`, icon: 'success', timer: 1500 });

      setTimeout(() => {
        const query = route.query;
        const redirectUrl = query.redirect;
        if (redirectUrl && redirectUrl.startsWith('/')) {
          router.push(redirectUrl);
          return;
        }
        if (query.force_whatsapp === 'true' || query.from_whatsapp === 'true') {
             const pendingOffer = sessionStorage.getItem('pending_offer');
             if (pendingOffer) {
                const { turno_id, token } = JSON.parse(pendingOffer);
                sessionStorage.removeItem('pending_offer');
                router.push(`/aceptar-oferta/${turno_id}/${token}`);
                return;
             }
        }
        if (data.rol === 'CLIENTE') router.push('/cliente/dashboard');
        else router.push('/dashboard');
      }, 1000);

    } else {
        Swal.fire('Error', data.message || 'Error desconocido', 'warning');
    }

  } catch (error) {
    let mensaje = 'No se pudo conectar con el servidor.';
    if (error.response?.data?.error) mensaje = error.response.data.error;
    else if (error.response?.data?.message) mensaje = error.response.data.message;

    Swal.fire({ title: 'Error de acceso', text: mensaje, icon: 'error', confirmButtonColor: '#007bff', background: '#1e293b', color: '#f1f5f9' });
  } finally {
    loading.value = false;
  }
};

const handleForgotPassword = async () => {
  const { value: email } = await Swal.fire({
    title: 'Recuperar contraseña',
    input: 'email',
    inputLabel: 'Ingresá tu correo electrónico',
    inputValue: credentials.value.username,
    showCancelButton: true,
    confirmButtonText: 'Enviar enlace',
    cancelButtonText: 'Cancelar',
    inputValidator: (value) => { if (!value) return '¡Necesitás ingresar un correo!'; }
  });

  if (email) {
    try {
      Swal.fire({ title: 'Enviando...', text: 'Por favor, esperá un momento.', allowOutsideClick: false, didOpen: () => { Swal.showLoading(); } });
      await axios.post(`${DOMAIN}/api/password-reset/solicitar/`, { email: email });
      Swal.fire({ title: '¡Correo enviado!', text: 'Recibirás un enlace para restablecer tu contraseña.', icon: 'success', confirmButtonColor: '#007bff' });
    } catch (error) {
      Swal.fire({ title: 'Error', text: 'Hubo un problema al intentar enviar el correo.', icon: 'error', confirmButtonColor: '#007bff' });
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ==================== LAYOUT FULL-VIEWPORT ==================== */
.auth-page {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr);
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #0b1120;
  color: #0f172a;
  overflow: hidden;
}

/* ==================== PANEL VISUAL ==================== */
.visual-panel {
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(150deg, #1e1b4b 0%, #1f42f0 52%, #129089 100%);
}

.visual-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: blur(16px) saturate(1.1);
  transform: scale(1.2);
}

/* Overlay que equilibra legibilidad sin apagar la fotografía */
.visual-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  background:
    linear-gradient(100deg, rgba(11, 17, 32, 0.38) 0%, rgba(11, 17, 32, 0.06) 45%, rgba(11, 17, 32, 0.42) 100%),
    radial-gradient(130% 90% at 50% 110%, rgba(11, 17, 32, 0.36) 0%, transparent 58%);
}

/* Capa de la imagen original: respeta proporción y composición (contain) */
.visual-figure {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(14px, 2vw, 28px);
}

.visual-img {
  max-width: 96%;
  max-height: 92%;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 32px 64px -22px rgba(0, 0, 0, 0.6), 0 14px 32px -12px rgba(0, 0, 0, 0.4);
  animation: fadeUp 0.6s ease both;
}

/* Degradado inferior que integra el texto con la imagen sin taparla */
.visual-scrim {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 60%;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(11, 17, 32, 0) 0%, rgba(11, 17, 32, 0.3) 55%, rgba(11, 17, 32, 0.55) 100%);
}

/* Fallback visual de marca cuando no hay imagen o está desactivada */
.visual-panel.sin-imagen {
  background:
    radial-gradient(1100px 560px at 18% -4%, rgba(99, 102, 241, 0.38) 0%, transparent 60%),
    radial-gradient(900px 520px at 100% 108%, rgba(18, 144, 137, 0.42) 0%, transparent 55%),
    linear-gradient(150deg, #1e1b4b 0%, #1f42f0 52%, #129089 100%);
}

.visual-panel.sin-imagen .visual-overlay {
  background: linear-gradient(180deg, rgba(11, 17, 32, 0.18) 0%, rgba(11, 17, 32, 0.5) 100%);
}

.visual-panel.sin-imagen::before,
.visual-panel.sin-imagen::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.45;
  z-index: 0;
}

.visual-panel.sin-imagen::before {
  width: 460px;
  height: 460px;
  background: #6366f1;
  top: -150px;
  right: -130px;
}

.visual-panel.sin-imagen::after {
  width: 400px;
  height: 400px;
  background: #14b8a6;
  bottom: -140px;
  left: -150px;
}

/* Contenido del panel visual */
.visual-content {
  position: relative;
  z-index: 3;
  height: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  padding: clamp(30px, 4.5vw, 60px);
  color: #fff;
}

.visual-brand {
  display: flex;
  align-items: center;
  gap: 13px;
  animation: fadeUp 0.55s ease both;
}

.visual-icon {
  width: 46px;
  height: 46px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.16);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 24px -10px rgba(0, 0, 0, 0.4);
}

.visual-icon svg {
  width: 26px;
  height: 26px;
}

.visual-message {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 560px;
  animation: fadeUp 0.55s ease 0.08s both;
}

.visual-title {
  font-size: clamp(2.5rem, 4.7vw, 4.3rem);
  font-weight: 800;
  line-height: 1.04;
  letter-spacing: -0.035em;
  color: #fff;
  text-shadow: 0 2px 30px rgba(11, 17, 32, 0.55), 0 1px 4px rgba(11, 17, 32, 0.5);
}

.visual-sub {
  margin-top: 20px;
  font-size: clamp(1rem, 1.35vw, 1.16rem);
  line-height: 1.65;
  opacity: 0.88;
  max-width: 470px;
  text-shadow: 0 1px 20px rgba(11, 17, 32, 0.6), 0 1px 2px rgba(11, 17, 32, 0.45);
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== PANEL DEL FORMULARIO ==================== */
.auth-panel {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(34px, 5vw, 76px);
  min-height: 100vh;
  min-height: 100dvh;
  overflow-y: auto;
  background:
    radial-gradient(900px 600px at 100% -5%, rgba(99, 102, 241, 0.09) 0%, transparent 55%),
    linear-gradient(180deg, #fbfcfe 0%, #f1f4f9 100%);
}

.auth-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #1f42f0, #129089, transparent);
  z-index: 1;
}

.auth-wrapper {
  width: 100%;
  max-width: 440px;
  animation: fadeUp 0.5s ease both;
}

/* Encabezado del formulario */
.auth-heading {
  margin-bottom: 34px;
}

.auth-title {
  font-size: clamp(1.65rem, 2.5vw, 2.05rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #0f172a;
  line-height: 1.15;
}

.auth-sub {
  margin-top: 10px;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #64748b;
}

/* FORM */
.auth-form {
  width: 100%;
}

.input-field {
  margin-bottom: 20px;
}

.input-field label {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  letter-spacing: -0.01em;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  transition: border-color 0.25s ease, background 0.25s ease, box-shadow 0.25s ease;
}

.input-wrap:hover {
  background: #fff;
  border-color: #cbd5e1;
}

.input-wrap:focus-within {
  background: #fff;
  border-color: #4f46e5;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.12), 0 8px 24px -12px rgba(79, 70, 229, 0.35);
}

.icon {
  position: absolute;
  left: 18px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  pointer-events: none;
  z-index: 2;
  transition: color 0.25s ease, transform 0.25s ease;
}

.input-wrap:focus-within .icon {
  color: #4f46e5;
  transform: scale(1.08);
}

.input-wrap input {
  width: 100%;
  height: 56px;
  padding: 0 18px 0 52px;
  border: none;
  background: transparent;
  font-size: 0.95rem;
  color: #0f172a;
  font-family: inherit;
  font-weight: 600;
  outline: none;
}

.input-wrap input::placeholder {
  color: #b6c0d0;
  font-weight: 400;
}

.toggle-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  border-radius: 9px;
  transition: color 0.2s ease, background 0.2s ease, transform 0.15s ease;
}

.toggle-btn:hover {
  color: #4f46e5;
  background: #eef2ff;
}

.toggle-btn:active {
  transform: scale(0.92);
}

/* FORM FOOTER */
.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 26px;
}

.link-secondary {
  font-size: 0.9rem;
  color: #4f46e5;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.link-secondary:hover {
  color: #4338ca;
}

/* PRIMARY BUTTON */
.btn-primary {
  width: 100%;
  height: 56px;
  background: transparent;
  color: #fff;
  border: none;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  font-family: inherit;
  position: relative;
  overflow: hidden;
  letter-spacing: -0.01em;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s ease, filter 0.25s ease;
}

.btn-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #4f46e5 0%, #1d8cbb 100%);
  transition: opacity 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 18px 36px -12px rgba(79, 70, 229, 0.5);
  filter: brightness(1.04);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 10px 24px -12px rgba(79, 70, 229, 0.4);
}

.btn-primary:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.28);
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
}

.btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 100%;
}

.btn-content svg {
  width: 18px;
  height: 18px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
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
  margin: 26px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e6eaf1;
}

.divider span {
  padding: 0 16px;
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 600;
}

/* ALT ACTIONS */
.alt-actions {
  text-align: center;
}

.register-prompt {
  font-size: 0.92rem;
  color: #64748b;
  margin-bottom: 16px;
  font-weight: 500;
}

.register-prompt a {
  color: #4f46e5;
  font-weight: 700;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.2s ease;
}

.register-prompt a:hover {
  color: #4338ca;
  text-decoration: underline;
}

.link-home {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 9px 16px;
  border-radius: 10px;
  transition: color 0.2s ease, background 0.2s ease, border-color 0.2s ease;
  border: 1px solid transparent;
}

.link-home svg {
  width: 16px;
  height: 16px;
}

.link-home:hover {
  color: #4f46e5;
  background: #f8fafc;
  border-color: #e6eaf1;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1100px) {
  .auth-page { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
  .visual-title { font-size: clamp(2.1rem, 3.9vw, 3.1rem); }
  .auth-panel { padding: 40px 32px; }
}

@media (max-width: 860px) {
  .auth-page {
    display: block;
    overflow: auto;
  }

  .visual-panel { display: none; }

  .auth-panel {
    min-height: 100vh;
    min-height: 100dvh;
    padding: 36px 20px;
    background: linear-gradient(180deg, #fbfcfe 0%, #f1f4f9 100%);
  }

  /* Si hay imagen de Login, se usa como fondo secundario difuminado */
  .auth-page.con-imagen .auth-panel {
    background:
      linear-gradient(rgba(11, 17, 32, 0.76), rgba(11, 17, 32, 0.86)),
      var(--login-img, none) center/cover no-repeat;
  }

  .auth-wrapper {
    max-width: 408px;
    margin: 0 auto;
  }

  .auth-page.con-imagen .auth-wrapper {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 22px;
    padding: 32px 24px;
    box-shadow: 0 30px 60px -20px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(14px);
  }
}

@media (max-width: 600px) {
  .auth-panel { padding: 26px 16px; }
  .auth-heading { margin-bottom: 30px; }
  .auth-title { font-size: 1.7rem; }
  .auth-sub { font-size: 0.9rem; }
  .input-field { margin-bottom: 18px; }
  .input-wrap input { height: 54px; font-size: 0.92rem; }
  .btn-primary { height: 54px; font-size: 0.96rem; border-radius: 12px; }
  .form-footer { margin-bottom: 24px; }
  .divider { margin: 24px 0; }
  .auth-page.con-imagen .auth-wrapper { padding: 28px 20px; }
}

@media (max-width: 380px) {
  .auth-panel { padding: 20px 14px; }
  .auth-title { font-size: 1.55rem; }
  .input-wrap input { height: 52px; font-size: 0.9rem; padding: 0 14px 0 48px; }
  .icon { left: 15px; }
  .btn-primary { height: 52px; font-size: 0.94rem; }
}
</style>