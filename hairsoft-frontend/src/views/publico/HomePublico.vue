<template>
  <div class="home-publico">
    
    <!-- HERO SECTION -->
    <div class="hero-section">
      <div class="hero-background">
        <div class="hero-gradient"></div>
      </div>
      
      <div class="hero-content">  
        <h1 class="hero-title">
          <span class="title-main">Los Ultimos</span>
          <span class="title-accent">Serán Los Primeros</span>
        </h1>
        
        <p class="hero-description">
          Tu estilo, nuestra pasión. Reserva tu cita online en segundos y descubre la mejor experiencia de belleza.
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
        
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">12</span>
            <span class="stat-label">Años de Experiencia</span>
          </div>
        </div>
      </div>
    </div>

    <!-- FEATURES SECTION -->
    <div class="features-section">
      <div class="section-header">
        <h2 class="section-title">Descubre Nuestros Servicios</h2>
        <p class="section-subtitle">Todo lo que necesitas para lucir espectacular</p>
      </div>
      
      <div class="features-grid">
        
        <!-- Card Servicios -->
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
              Cortes modernos, coloración profesional y tratamientos capilares de primera calidad con productos premium.
            </p>
            
            <div class="card-features">
              <span class="feature-tag">Cortes</span>
              <span class="feature-tag">Coloración</span>
              <span class="feature-tag">Tratamientos</span>
            </div>
          </div>
          
          <div class="card-footer">
            <span class="link-text">
              Ver catálogo completo
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>
        </div>

        <!-- Card Productos -->
        <div class="feature-card clickable" @click="$router.push('/web/productos')">
          <div class="card-icon-wrapper">
            <div class="card-icon purple">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                <path d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          
          <div class="card-content">
            <h3 class="card-title">Productos Premium</h3>
            <p class="card-description">
              Las mejores marcas profesionales para el cuidado y mantenimiento de tu cabello en casa.
            </p>
            
            <div class="card-features">
              <span class="feature-tag">Shampoos</span>
              <span class="feature-tag">Tratamientos</span>
              <span class="feature-tag">Styling</span>
            </div>
          </div>
          
          <div class="card-footer">
            <span class="link-text">
              Explorar tienda
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>
        </div>

        <!-- Card Información -->
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
                  <p class="info-label">Dirección</p>
                  <p class="info-value">Avenida Libertador 600</p>
                  <p class="info-value-sub">San Vicente - Misiones</p>
                </div>
              </div>
              
              <div class="info-divider"></div>
              
              <div class="info-item">
                <svg class="info-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <div>
                  <p class="info-label">Horarios</p>
                  <p class="info-value horario">Lun - Sáb: 9:00 - 20:00</p>
                  <p class="info-value-sub">Domingos cerrado</p>
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
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';

const router = useRouter();

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
      background: '#1e293b',
      color: '#f8fafc'
    }).then((result) => {
      if (result.isConfirmed) {
        router.push('/login');
      } else {
        router.push('/web/servicios');
      }
    });
  }
};
</script>

<style scoped>
.home-publico {
  min-height: 100vh;
  background: #0f172a;
  color: #f8fafc;
  padding-bottom: 3rem;
}

/* ============================================
   HERO SECTION
   ============================================ */
.hero-section {
  position: relative;
  padding: 5rem 2rem;
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.hero-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #1e293b 100%);
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
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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
  color: #94a3b8;
  line-height: 1.8;
  max-width: 700px;
  margin: 0 auto 3rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 4rem;
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
}

.btn-cta:hover {
  opacity: 0.9;
}

.btn-cta svg {
  stroke: currentColor;
  flex-shrink: 0;
}

.btn-cta.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.btn-cta.secondary {
  background: rgba(31, 41, 55, 0.8);
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 3rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* ============================================
   FEATURES SECTION
   ============================================ */
.features-section {
  padding: 4rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-subtitle {
  font-size: 1.2rem;
  color: #94a3b8;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 20px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feature-card.clickable {
  cursor: pointer;
}

.feature-card.clickable:hover {
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.card-icon {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon.blue {
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.card-icon.purple {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.card-icon.green {
  background: linear-gradient(135deg, #059669, #10b981);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.card-icon svg {
  stroke: white;
}

.card-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #fff;
  letter-spacing: 0.3px;
}

.card-description {
  color: #94a3b8;
  line-height: 1.8;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.card-features {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 6px 14px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 20px;
  font-size: 0.85rem;
  color: #60a5fa;
  font-weight: 600;
}

.link-text {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #60a5fa;
  font-weight: 700;
  font-size: 1rem;
}

.link-text svg {
  stroke: currentColor;
}

.feature-card.clickable:hover .link-text {
  color: #3b82f6;
}

/* Card Info */
.feature-card.info:hover {
  border-color: rgba(16, 185, 129, 0.3);
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
  font-size: 0.8rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
  margin-bottom: 4px;
}

.info-value {
  font-size: 1rem;
  color: #e2e8f0;
  font-weight: 600;
  line-height: 1.6;
}

.info-value.horario {
  color: #10b981;
  font-weight: 700;
}

.info-value-sub {
  font-size: 0.9rem;
  color: #94a3b8;
  margin-top: 2px;
}

.info-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
}

.contact-badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.contact-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
  color: #10b981;
  font-size: 0.85rem;
  font-weight: 600;
}

.contact-badge:hover {
  background: rgba(16, 185, 129, 0.15);
}

.contact-badge svg {
  stroke: currentColor;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 4rem 1.5rem;
    min-height: 60vh;
  }

  .hero-title {
    font-size: 3rem;
  }

  .hero-description {
    font-size: 1.1rem;
  }

  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .btn-cta {
    width: 100%;
    justify-content: center;
  }

  .section-title {
    font-size: 2.2rem;
  }

  .features-section {
    padding: 3rem 1.5rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .btn-cta {
    padding: 14px 24px;
    font-size: 1rem;
  }

  .card-icon {
    width: 70px;
    height: 70px;
  }

  .card-title {
    font-size: 1.5rem;
  }
}
</style>