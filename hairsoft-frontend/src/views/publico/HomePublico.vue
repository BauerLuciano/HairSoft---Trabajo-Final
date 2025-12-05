<template>
  <div class="home-publico">
    <div class="hero-section">
      <div class="hero-content">
        <h1>HairSoft <span class="accent">Style</span></h1>
        <p>Tu estilo, nuestra pasión. Reserva tu cita online en segundos.</p>
        <button @click="intentarReservar" class="btn-cta">📅 Reservar Ahora</button>
      </div>
    </div>

    <div class="features-grid">
      <div class="feature-card" @click="$router.push('/web/servicios')">
        <div class="icon">✂️</div>
        <h3>Nuestros Servicios</h3>
        <p>Cortes, coloración y tratamientos de primera calidad.</p>
        <span class="link-text">Ver catálogo →</span>
      </div>

      <div class="feature-card" @click="$router.push('/web/productos')">
        <div class="icon">🛍️</div>
        <h3>Productos</h3>
        <p>Las mejores marcas para el cuidado de tu cabello.</p>
        <span class="link-text">Explorar tienda →</span>
      </div>

      <div class="feature-card info">
        <div class="icon">📍</div>
        <h3>Visítanos</h3>
        <p>Avenida Libertador 600</p>
        <p>San Vicente - Misiones</p>
        <p class="horario">Lun - Sáb: 9:00 - 20:00</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';

const router = useRouter();

// LÓGICA CENTRAL: ¿Qué pasa cuando le dan a "Reservar"?
const intentarReservar = () => {
  const token = localStorage.getItem('token');
  const rol = localStorage.getItem('user_rol');

  if (token && rol === 'CLIENTE') {
    // 1. Si ya es cliente y está logueado -> Al formulario directo
    router.push('/turnos/crear-web');
  } else if (token && rol !== 'CLIENTE') {
    // 2. Si es admin/empleado -> A su dashboard (no deberían reservar por acá)
    router.push('/dashboard');
  } else {
    // 3. Si es PÚBLICO (No logueado) -> Al Login con mensaje
    Swal.fire({
      title: 'Inicia Sesión',
      text: 'Para reservar un turno, necesitas ingresar a tu cuenta o registrarte.',
      icon: 'info',
      showCancelButton: true,
      confirmButtonText: 'Ir al Login',
      cancelButtonText: 'Ver Servicios primero'
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
  padding-bottom: 4rem;
}

/* Hero Section Moderno */
.hero-section {
  background: linear-gradient(135deg, var(--bg-secondary) 0%, #1e293b 100%);
  color: var(--text-primary);
  padding: 4rem 2rem;
  text-align: center;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 3rem;
  border-radius: 0 0 20px 20px;
}

.hero-content h1 {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  font-weight: 800;
}

.hero-content .accent {
  color: var(--accent-color);
}

.hero-content p {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.btn-cta {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 50px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 15px var(--accent-shadow);
}

.btn-cta:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px var(--accent-shadow);
}

/* Grid de Opciones */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.feature-card {
  background: var(--bg-secondary);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.feature-card:hover {
  transform: translateY(-5px);
  border-color: var(--accent-color);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.feature-card.info {
  cursor: default; /* La tarjeta de info no es clickeable */
}
.feature-card.info:hover {
  transform: none;
  border-color: var(--border-color);
  box-shadow: none;
}

.icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.link-text {
  margin-top: auto;
  color: var(--accent-color);
  font-weight: bold;
  font-size: 0.9rem;
}

.horario {
  font-weight: bold;
  color: #10b981; /* Verde para horario */
}
</style>