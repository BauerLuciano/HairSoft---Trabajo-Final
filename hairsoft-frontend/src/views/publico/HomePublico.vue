<template>
  <div class="home-publico">
    
    <div class="hero-section">
      
      <div class="hero-content fade-in">  
        <h1 class="hero-title">
          <span class="title-main">{{ tituloPartes.main }}</span>
          <span class="title-accent">{{ tituloPartes.accent }}</span>
        </h1>
        
        <p class="hero-description">
          Reservá turnos o realizá pedidos de productos de forma rápida y online.
        </p>

        <div class="hero-actions">
          <button @click="intentarReservar" class="btn-cta primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span>Reservar Ahora</span>
          </button>
        </div>
      </div>
    </div>


    <div class="features-section fade-in">
      <div class="section-header">
        <h2 class="section-title">Todo lo que necesitás</h2>
        <p class="section-subtitle">Servicios profesionales y productos de alta gama</p>
      </div>
      
      <div class="features-grid">
        
        <div class="feature-card clickable" @click="$router.push('/web/servicios')">
          <div class="card-icon-wrapper">
            <div class="card-icon blue">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                <path d="M7 21h10M12 17v4M8 3h8l-1 8H9L8 3zM6 11c0 4.418 2.686 8 6 8s6-3.582 6-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="card-content">
            <h3 class="card-title">Nuestros Servicios</h3>
            <p class="card-description">
              Cortes modernos, coloración profesional y tratamientos capilares de primera calidad.
            </p>
            <div class="card-features">
              <span class="feature-tag">Cortes</span>
              <span class="feature-tag">Coloración</span>
              <span class="feature-tag">Barbería</span>
            </div>
          </div>
          <div class="card-footer">
            <span class="link-text">
              Ver catálogo de servicios
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>
        </div>

        <div class="feature-card clickable" @click="$router.push('/web/productos')">
          <div class="card-icon-wrapper">
            <div class="card-icon purple">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                <path d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="card-content">
            <h3 class="card-title">Productos</h3>
            <p class="card-description">
              Las mejores marcas para el cuidado de tu cabello
            </p>
            <div class="card-features">
              <span class="feature-tag">Shampoos</span>
              <span class="feature-tag">Tratamientos</span>
              <span class="feature-tag">Styling</span>
            </div>
          </div>
          <div class="card-footer">
            <span class="link-text">
              Explorar tienda web
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>
        </div>

        <div class="feature-card info">
          <div class="card-icon-wrapper">
            <div class="card-icon green">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          
          <div class="card-content">
            <h3 class="card-title">Visítanos</h3>
            
            <div class="info-section">
              <div class="info-item">
                <svg class="info-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke="currentColor" stroke-width="2"/>
                  <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
                </svg>
                <div>
                  <p class="info-label">Ciudad:</p>
                  <p class="info-value">{{"San Vicente - Misiones"}}</p>
                  <p class="info-label">Dirección</p>
                  <p class="info-value">{{ configLocal.direccion.split(',')[0] || 'Cargando...' }}</p>
                  <p class="info-value-sub" v-if="configLocal.direccion.includes(',')">
                    {{ configLocal.direccion.split(',')[1].trim() }}
                  </p>
                </div>
              </div>
              
              <div class="info-divider"></div>
              
              <div class="info-item">
                <svg class="info-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <div>
                  <p class="info-label">Contacto</p>
                  <p class="info-value horario">{{ configLocal.telefono }}</p>
                  <p class="info-value-sub">{{ configLocal.email }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/utils/axiosConfig';
import Swal from 'sweetalert2';

const router = useRouter();

// Estado con los datos por defecto hasta que cargue la API
const configLocal = ref({
  razon_social: 'HairSoft Salón',
  direccion: 'Cargando ubicación...',
  telefono: 'Cargando...',
  email: 'Cargando...'
});

// Obtener datos del backend público
const cargarDatosConfiguracion = async () => {
  try {
    const res = await axios.get('/api/web/configuracion/');
    configLocal.value = res.data;
  } catch (error) {
    console.error("No se pudo cargar la configuración de la peluquería", error);
  }
};

// Computada inteligente: Corta el nombre de la peluquería en 2 líneas para que quede lindo
const tituloPartes = computed(() => {
  const nombreCompleto = configLocal.value.razon_social || '';
  const palabras = nombreCompleto.split(' ');
  
  if (palabras.length <= 2) {
    return { main: nombreCompleto, accent: '' };
  }
  
  // Dividimos a la mitad (Ej: "Los Últimos" / "Serán Los Primeros")
  const mitad = Math.floor(palabras.length / 2);
  return {
    main: palabras.slice(0, mitad).join(' '),
    accent: palabras.slice(mitad).join(' ')
  };
});

const intentarReservar = () => {
  const token = localStorage.getItem('token');
  const rol = localStorage.getItem('user_rol');

  if (token && rol === 'CLIENTE') {
    router.push('/turnos/crear-web');
  } else if (token && rol !== 'CLIENTE') {
    router.push('/dashboard');
  } else {
    Swal.fire({
      title: 'Inicia Sesión',
      text: 'Para reservar un turno, necesitas ingresar a tu cuenta o registrarte.',
      icon: 'info',
      showCancelButton: true,
      confirmButtonText: 'Ir al Login',
      cancelButtonText: 'Ver Servicios primero',
      confirmButtonColor: '#3b82f6',
      cancelButtonColor: '#6b7280',
      background: 'var(--bg-primary)',
      color: 'var(--text-primary)'
    }).then((result) => {
      if (result.isConfirmed) {
        router.push('/login');
      } else {
        router.push('/web/servicios');
      }
    });
  }
};

onMounted(() => {
  cargarDatosConfiguracion();
});
</script>

<style scoped>
/* AHORA USAMOS LAS VARIABLES GLOBALES DE TU PROYECTO */
.home-publico {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding-bottom: 3rem;
  transition: background 0.3s, color 0.3s;
}

/* ============================================
   HERO SECTION
   ============================================ */
.hero-section {
  position: relative;
  padding: 5rem 2rem;
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-background {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 900px;
  text-align: center;
}

.hero-title {
  font-size: 4.5rem;
  font-weight: 900;
  margin-bottom: 1.5rem;
  line-height: 1.1;
  letter-spacing: -2px;
}

.title-main {
  display: block;
  color: var(--text-primary);
}

.title-accent {
  display: block;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-top: 0.5rem;
}

.hero-description {
  font-size: 1.25rem;
  color: var(--text-secondary);
  line-height: 1.8;
  max-width: 700px;
  margin: 0 auto 3rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-cta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  font-size: 1.1rem;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  letter-spacing: 0.3px;
  transition: all 0.3s ease;
}

.btn-cta.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
}

.btn-cta.primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.4);
}

.btn-cta svg {
  stroke: currentColor;
  flex-shrink: 0;
}

/* ============================================
   VIDEO SECTION
   ============================================ */
.video-showcase {
  max-width: 1000px;
  margin: 40px auto 80px;
  padding: 0 20px;
  text-align: center;
}

.video-container {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  line-height: 0; 
}

.institutional-video {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: cover;
  display: block;
}

.video-text {
  margin-top: 25px;
}

.video-text h2 {
  font-size: 2rem;
  color: var(--text-primary);
  font-weight: 800;
  margin-bottom: 10px;
}

.video-text p {
  color: var(--text-secondary);
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
}

/* ============================================
   FEATURES SECTION
   ============================================ */
.features-section {
  padding: 0 2rem 5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.section-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

.feature-card.clickable {
  cursor: pointer;
}

.feature-card.clickable:hover {
  border-color: #3b82f6;
  box-shadow: var(--shadow-md);
  transform: translateY(-5px);
}

.card-icon-wrapper {
  display: inline-block;
}

.card-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon.blue { background: linear-gradient(135deg, #1e40af, #3b82f6); box-shadow: 0 0 20px rgba(59, 130, 246, 0.2); }
.card-icon.purple { background: linear-gradient(135deg, #7c3aed, #a78bfa); box-shadow: 0 0 20px rgba(139, 92, 246, 0.2); }
.card-icon.green { background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }

.card-icon svg {
  stroke: white;
}

.card-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.card-description {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.card-features {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 6px 14px;
  background: var(--hover-bg);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 0.8rem;
  color: #3b82f6;
  font-weight: 600;
}

.link-text {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #60a5fa;
  font-weight: 700;
  font-size: 0.95rem;
  transition: color 0.3s ease;
}

.feature-card.clickable:hover .link-text {
  color: #3b82f6;
}

/* Card Info (Visítanos) */
.feature-card.info:hover {
  border-color: #10b981;
  box-shadow: var(--shadow-md);
  transform: translateY(-5px);
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-item {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.info-icon {
  stroke: #10b981;
  flex-shrink: 0;
  margin-top: 2px;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 700;
  margin-bottom: 4px;
}

.info-value {
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.4;
}

.info-value.horario {
  color: #10b981;
}

.info-value-sub {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.info-divider {
  height: 1px;
  background: var(--border-color);
}

.fade-in { animation: fadeIn 0.8s ease-out forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .hero-section {
    padding: 4rem 1.5rem;
    min-height: 50vh;
  }

  .hero-title { font-size: 3rem; }
  .hero-description { font-size: 1.1rem; }
  
  .video-showcase { margin: 20px auto 60px; }
  .video-text h2 { font-size: 1.5rem; }

  .section-title { font-size: 2rem; }
}

@media (max-width: 480px) {
  .hero-title { font-size: 2.2rem; }
  .feature-card { padding: 1.5rem; }
  .card-icon { width: 60px; height: 60px; }
  .card-title { font-size: 1.3rem; }
}
</style>