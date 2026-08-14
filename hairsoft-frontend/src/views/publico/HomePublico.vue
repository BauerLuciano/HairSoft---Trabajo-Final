<template>
  <div class="home-publico">
    <!-- ============ HERO ============ -->
    <section class="hero" :style="heroStyle">
      <div class="hero-overlay"></div>
      <div class="hero-glow"></div>

      <div class="hero-content">
        <span class="hero-badge reveal">
          <MapPin :size="14" />
          {{ ciudad }}
        </span>

        <h1 class="hero-title reveal">
          <span class="title-main">{{ tituloPartes.main }}</span>
          <span v-if="tituloPartes.accent" class="title-accent">{{ tituloPartes.accent }}</span>
        </h1>

        <p class="hero-description reveal">
          Reservá turnos o realizá pedidos de productos de forma rápida y online.
        </p>

        <div class="hero-actions reveal">
          <button @click="intentarReservar" class="btn-cta primary">
            <CalendarPlus :size="20" />
            <span>Reservar Turno</span>
          </button>
          <router-link to="/web/productos" class="btn-cta ghost">
            <ShoppingBag :size="20" />
            <span>Ver Productos</span>
          </router-link>
          <router-link to="/web/servicios" class="btn-cta ghost">
            <Scissors :size="20" />
            <span>Ver Servicios</span>
          </router-link>
        </div>

        <div class="hero-cards">
          <div class="hero-card reveal">
            <div class="hero-card-icon"><MapPin :size="20" /></div>
            <div class="hero-card-info">
              <span class="hero-card-label">Dirección</span>
              <strong class="hero-card-value">{{ direccionCorta }}</strong>
            </div>
          </div>

          <div class="hero-card reveal">
            <div class="hero-card-icon"><Phone :size="20" /></div>
            <div class="hero-card-info">
              <span class="hero-card-label">Teléfono</span>
              <strong class="hero-card-value">{{ configLocal.telefono }}</strong>
            </div>
          </div>

          <div class="hero-card reveal">
            <div class="hero-card-icon"><Clock :size="20" /></div>
            <div class="hero-card-info">
              <span class="hero-card-label">Hoy</span>
              <strong class="hero-card-value">{{ horarioDeHoy }}</strong>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ HORARIOS ============ -->
    <section class="section horarios-section">
      <div class="section-header reveal">
        <span class="section-eyebrow">Atención</span>
        <h2 class="section-title">Horarios de Atención</h2>
        <p class="section-subtitle">Te esperamos toda la semana</p>
      </div>

      <div class="horarios-grid">
        <div
          v-for="h in horariosOrdenados"
          :key="h.dia_semana"
          class="horario-dia reveal"
          :class="{ cerrado: !h.trabaja, hoy: esHoy(h) }"
        >
          <span class="dia-nombre">{{ h.dia_nombre }}</span>
          <span v-if="h.trabaja" class="dia-horario">{{ formatearHorario(h) }}</span>
          <span v-else class="dia-horario cerrado-text">Cerrado</span>
        </div>
      </div>
    </section>

    <!-- ============ CÓMO FUNCIONA ============ -->
    <section class="section como-funciona">
      <div class="section-header reveal">
        <span class="section-eyebrow">Sencillo</span>
        <h2 class="section-title">¿Cómo funciona?</h2>
        <p class="section-subtitle">Reservá tu turno en menos de un minuto</p>
      </div>

      <div class="pasos-grid">
        <div class="paso reveal">
          <div class="paso-numero">01</div>
          <div class="paso-icono"><Scissors :size="32" /></div>
          <h3>Elegí tu servicio</h3>
          <p>Explorá nuestro catálogo de cortes, coloraciones y tratamientos.</p>
        </div>

        <div class="paso reveal">
          <div class="paso-numero">02</div>
          <div class="paso-icono"><CalendarCheck :size="32" /></div>
          <h3>Reservá tu turno</h3>
          <p>Elegí día, hora y peluquero. Al reservar online, el pago se realiza por Mercado Pago.</p>
        </div>

        <div class="paso reveal">
          <div class="paso-numero">03</div>
          <div class="paso-icono"><Sparkles :size="32" /></div>
          <h3>Pagá</h3>
          <p>Aboná una seña del 50 % o el total online. Si elegís seña, el resto se abona en el local.</p>
        </div>
      </div>

      <!-- PAGO DE TURNOS ONLINE -->
      <div class="pago-online reveal">
        <div class="pago-header">
          <div class="pago-header-icon"><CreditCard :size="22" /></div>
          <h3>Reservá tu turno online</h3>
        </div>

        <p class="pago-desc">
          Los turnos reservados online se abonan mediante <strong>Mercado Pago</strong>.
          Podés elegir entre pagar una seña del <strong>50&nbsp;%</strong> o el total del turno.
        </p>

        <div class="pago-opciones">
          <div class="pago-opcion destacada">
            <span class="pago-badge"><strong>50&nbsp;%</strong><span class="pago-badge-label">Seña</span></span>
            <p>Pagás online la mitad del valor como seña. El resto lo abonás en la peluquería, en efectivo o con Mercado Pago.</p>
          </div>

          <div class="pago-opcion">
            <span class="pago-badge"><strong>100&nbsp;%</strong><span class="pago-badge-label">Pago total</span></span>
            <p>Abonás el valor completo del turno online con Mercado Pago. Sin pagos pendientes en el local.</p>
          </div>
        </div>

        <div class="pago-presencial">
          <div class="pago-presencial-icon"><Wallet :size="18" /></div>
          <div>
            <h4>Turnos presenciales</h4>
            <p>Si reservás tu turno directamente en la peluquería, abonás en el local: efectivo o Mercado Pago.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ SERVICIOS DESTACADOS ============ -->
    <section class="section servicios-destacados">
      <div class="section-header reveal">
        <span class="section-eyebrow">Profesional</span>
        <h2 class="section-title">Servicios Destacados</h2>
        <p class="section-subtitle">Los favoritos de nuestros clientes</p>
      </div>

      <div v-if="cargandoServicios" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="servicios-grid">
        <div v-for="s in serviciosDestacados" :key="s.id" class="servicio-card reveal">
          <span class="servicio-categoria">{{ s.categoria_nombre }}</span>
          <h3 class="servicio-nombre">{{ s.nombre }}</h3>
          <div class="servicio-meta">
            <Clock :size="15" />
            <span>{{ s.duracion || 30 }} min</span>
          </div>
          <div class="servicio-footer">
            <div class="servicio-precio">
              <span class="precio-moneda">$</span>
              <span class="precio-valor">{{ formatPrice(s.precio) }}</span>
            </div>
            <router-link to="/web/servicios" class="btn-detalle">Ver más</router-link>
          </div>
        </div>
      </div>

      <div class="ver-mas reveal">
        <router-link to="/web/servicios" class="btn-outline">
          Ver todos los servicios
          <ChevronRight :size="18" />
        </router-link>
      </div>
    </section>

    <!-- ============ PRODUCTOS DESTACADOS ============ -->
    <section class="section productos-destacados">
      <div class="section-header reveal">
        <span class="section-eyebrow">Tienda</span>
        <h2 class="section-title">Productos Destacados</h2>
        <p class="section-subtitle">Cuidado y estilo de las mejores marcas</p>
      </div>

      <div v-if="cargandoProductos" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="productos-grid">
        <div v-for="p in productosDestacados" :key="p.id" class="producto-card reveal">
          <div class="producto-img">
            <img :src="getImageUrl(p.imagen)" :alt="p.nombre" loading="lazy" />
          </div>
          <div class="producto-info">
            <span class="producto-marca">{{ p.marca_nombre }}</span>
            <h3 class="producto-nombre">{{ p.nombre }}</h3>
            <div class="producto-footer">
              <div class="producto-precio">
                <span class="precio-moneda">$</span>
                <span class="precio-valor">{{ formatPrice(p.precio) }}</span>
              </div>
              <button
                class="btn-agregar"
                :disabled="p.stock_actual <= 0"
                @click="agregarAlCarrito(p)"
              >
                <ShoppingBag :size="16" />
                {{ p.stock_actual > 0 ? 'Agregar' : 'Sin stock' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="ver-mas reveal">
        <router-link to="/web/productos" class="btn-outline">
          Ver la tienda completa
          <ChevronRight :size="18" />
        </router-link>
      </div>
    </section>

    <!-- ============ FOOTER ============ -->
    <footer class="footer">
      <div class="footer-grid">
        <div class="footer-col">
          <h4>Contacto</h4>
          <ul>
            <li><MapPin :size="16" /> {{ configLocal.direccion }}</li>
            <li><Phone :size="16" /> {{ configLocal.telefono }}</li>
            <li><Mail :size="16" /> {{ configLocal.email }}</li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Accesos</h4>
          <ul>
            <li><router-link to="/web/home">Inicio</router-link></li>
            <li><router-link to="/web/servicios">Servicios</router-link></li>
            <li><router-link to="/web/productos">Productos</router-link></li>
          </ul>
        </div>
      </div>

    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/utils/axiosConfig';
import {
  MapPin, Phone, Clock, Scissors, CalendarPlus, CalendarCheck,
  Sparkles, ShoppingBag, ChevronRight, Mail, CreditCard, Wallet
} from 'lucide-vue-next';
import { useCartStore } from '@/stores/cart';
import { requireAuth, sesionValida } from '@/utils/authPrompt';

const router = useRouter();
const cartStore = useCartStore();

const MEDIA_BASE = window.location.hostname.includes('vercel.app')
  ? 'https://web-production-ac47c.up.railway.app'
  : 'http://127.0.0.1:8000';

const getImageUrl = (img) => {
  if (!img) return null;
  if (img.startsWith('http')) return img;
  return `${MEDIA_BASE}${img}`;
};

const configLocal = ref({
  razon_social: 'HairSoft Salón',
  direccion: 'Avenida Libertador 600, San Vicente - Misiones',
  telefono: '3755-72716',
  email: 'contacto@hairsoft.com',
  logo: null,
  imagen_portada: null,
  horarios: []
});

const servicios = ref([]);
const productos = ref([]);
const cargandoServicios = ref(true);
const cargandoProductos = ref(true);

const anio = new Date().getFullYear();

const heroStyle = computed(() => {
  const portada = configLocal.value.imagen_portada ? getImageUrl(configLocal.value.imagen_portada) : null;
  return portada ? { '--hero-img': `url('${portada}')` } : { '--hero-img': 'none' };
});

const tituloPartes = computed(() => {
  const nombreCompleto = configLocal.value.razon_social || '';
  const palabras = nombreCompleto.split(' ');

  if (palabras.length <= 2) {
    return { main: nombreCompleto, accent: '' };
  }

  const mitad = Math.floor(palabras.length / 2);
  return {
    main: palabras.slice(0, mitad).join(' '),
    accent: palabras.slice(mitad).join(' ')
  };
});

const ciudad = computed(() => {
  const partes = (configLocal.value.direccion || '').split(',');
  return partes.length > 1 ? partes[partes.length - 1].trim() : 'San Vicente - Misiones';
});

const direccionCorta = computed(() => {
  const primera = (configLocal.value.direccion || '').split(',')[0];
  return primera && primera !== 'Cargando ubicación...' ? primera : 'Consultá nuestros horarios';
});

const horariosOrdenados = computed(() => {
  return [...(configLocal.value.horarios || [])].sort((a, b) => a.dia_semana - b.dia_semana);
});

const diaSemanaHoy = () => (new Date().getDay() + 6) % 7;

const esHoy = (h) => h.dia_semana === diaSemanaHoy();

const formatearHora = (hora) => (hora ? String(hora).slice(0, 5) : '');

const formatearHorario = (h) => {
  if (!h.trabaja) return 'Cerrado';
  const partes = [];
  if (h.hora_apertura_manana && h.hora_cierre_manana) {
    partes.push(`${formatearHora(h.hora_apertura_manana)}–${formatearHora(h.hora_cierre_manana)}`);
  }
  if (h.hora_apertura_tarde && h.hora_cierre_tarde) {
    partes.push(`${formatearHora(h.hora_apertura_tarde)}–${formatearHora(h.hora_cierre_tarde)}`);
  }
  return partes.length ? partes.join(' / ') : 'Consultar';
};

const horarioDeHoy = computed(() => {
  const hoy = horariosOrdenados.value.find((h) => h.dia_semana === diaSemanaHoy());
  if (!hoy) return 'Consultar';
  if (!hoy.trabaja) return 'Cerrado hoy';
  return formatearHorario(hoy);
});

const serviciosDestacados = computed(() => servicios.value.slice(0, 6));

const productosDestacados = computed(() => productos.value.slice(0, 6));

const formatPrice = (value) => {
  const num = Number(value);
  return isNaN(num) ? '0' : Math.round(num).toLocaleString('es-AR');
};

const cargarDatosConfiguracion = async () => {
  try {
    const res = await axios.get('/api/web/configuracion/');
    configLocal.value = { ...configLocal.value, ...res.data };
  } catch (error) {
    console.error('No se pudo cargar la configuración de la peluquería', error);
  }
};

const cargarServicios = async () => {
  cargandoServicios.value = true;
  try {
    const res = await axios.get('/api/servicios/');
    const datos = Array.isArray(res.data) ? res.data : (res.data.results || []);
    servicios.value = datos.filter((s) => s && (s.estado === 'ACTIVO' || !s.estado));
  } catch (error) {
    console.error('Error al cargar servicios', error);
  } finally {
    cargandoServicios.value = false;
  }
};

const cargarProductos = async () => {
  cargandoProductos.value = true;
  try {
    const res = await axios.get('/api/catalogo/');
    productos.value = Array.isArray(res.data) ? res.data : (res.data.results || []);
  } catch (error) {
    console.error('Error al cargar productos', error);
  } finally {
    cargandoProductos.value = false;
  }
};

const agregarAlCarrito = (producto) => {
  if (producto && producto.stock_actual > 0) {
    cartStore.agregarProducto(producto);
  }
};

const intentarReservar = async () => {
  const token = localStorage.getItem('token');

  if (!token) {
    requireAuth({ action: 'booking', redirect: '/turnos/crear-web' });
    return;
  }

  const valida = await sesionValida(axios);
  if (valida === false) {
    requireAuth({ action: 'booking', redirect: '/turnos/crear-web' });
    return;
  }

  router.push('/turnos/crear-web');
};

let observer = null;

const setupReveal = async () => {
  await nextTick();
  if (observer) observer.disconnect();

  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
};

onMounted(async () => {
  await Promise.all([
    cargarDatosConfiguracion(),
    cargarServicios(),
    cargarProductos()
  ]);
  setupReveal();
});

onUnmounted(() => {
  if (observer) observer.disconnect();
});
</script>

<style scoped>
/* ============================================
   HOME PÚBLICO — BARBERÍA PREMIUM (AZUL / CELESTE)
   Adaptado a modo oscuro y modo claro (themes.css)
   ============================================ */
.home-publico {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding-bottom: 0;
  transition: background 0.3s, color 0.3s;
}

/* Acentos azul / celeste (funcionan en ambos temas) */
.home-publico {
  --azul: #3b82f6;
  --azul-oscuro: #1e40af;
  --celeste: #38bdf8;
  --azul-claro: #bae6fd;
  --gradiente-azul: linear-gradient(135deg, #38bdf8 0%, #3b82f6 45%, #1e40af 100%);
}

.reveal {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1), transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--reveal-delay, 0s);
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ============================================
   HERO — fondo visual (portada configurada)
   ============================================ */
.hero {
  --overlay: linear-gradient(180deg, rgba(15, 23, 42, 0.45) 0%, rgba(15, 23, 42, 0.62) 55%, rgba(15, 23, 42, 0.82) 100%);
  position: relative;
  min-height: 92vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6.5rem 2rem 4rem;
  background-image: var(--overlay), var(--hero-img);
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  overflow: hidden;
}

/* Modo claro: overlay más liviano para que el logo se vea brillante */
html.light-theme .hero {
  --overlay: linear-gradient(180deg, rgba(15, 23, 42, 0.3) 0%, rgba(15, 23, 42, 0.45) 55%, rgba(15, 23, 42, 0.68) 100%);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 20% 20%, rgba(56, 189, 248, 0.14) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 90%, rgba(37, 99, 235, 0.16) 0%, transparent 50%);
  pointer-events: none;
}

.hero-glow {
  position: absolute;
  bottom: -120px;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  height: 260px;
  background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.22) 0%, transparent 70%);
  filter: blur(30px);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 900px;
  text-align: center;
  color: #f1f5f9;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 20px;
  border-radius: 50px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.4);
  color: var(--azul-claro);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 1.2rem;
  backdrop-filter: blur(8px);
}

.hero-title {
  font-size: 4.2rem;
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: -2px;
  margin-bottom: 1.2rem;
  text-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
}

.title-main {
  display: block;
  color: #ffffff;
}

.title-accent {
  display: block;
  background: var(--gradiente-azul);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-top: 0.4rem;
}

.hero-description {
  font-size: 1.2rem;
  color: rgba(241, 245, 249, 0.85);
  line-height: 1.8;
  max-width: 620px;
  margin: 0 auto 2rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2.5rem;
}

.btn-cta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 34px;
  font-size: 1.05rem;
  font-weight: 800;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  letter-spacing: 0.3px;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-cta.primary {
  background: var(--gradiente-azul);
  color: #ffffff;
  box-shadow: 0 10px 30px rgba(37, 99, 235, 0.35);
}

.btn-cta.primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 40px rgba(37, 99, 235, 0.5);
}

.btn-cta.ghost {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
}

.btn-cta.ghost:hover {
  background: rgba(255, 255, 255, 0.16);
  border-color: rgba(255, 255, 255, 0.45);
  transform: translateY(-3px);
}

.hero-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.2rem;
  max-width: 860px;
  margin: 0 auto;
}

.hero-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: rgba(15, 16, 20, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  text-align: left;
  backdrop-filter: blur(14px);
  transition: all 0.3s ease;
}

html.light-theme .hero-card {
  background: rgba(255, 255, 255, 0.78);
  border-color: rgba(255, 255, 255, 0.55);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}

.hero-card:hover {
  border-color: rgba(56, 189, 248, 0.5);
  transform: translateY(-4px);
}

.hero-card-icon {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: var(--celeste);
  display: flex;
  align-items: center;
  justify-content: center;
}

html.light-theme .hero-card-icon {
  background: rgba(37, 99, 235, 0.12);
  border-color: rgba(37, 99, 235, 0.3);
  color: var(--azul);
}

.hero-card-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.hero-card-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: rgba(241, 245, 249, 0.55);
}

html.light-theme .hero-card-label {
  color: #475569;
}

.hero-card-value {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f1f5f9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

html.light-theme .hero-card-value {
  color: #0f172a;
}

/* ============================================
   SECCIONES GENÉRICAS
   ============================================ */
.section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3.25rem 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 2.2rem;
}

.section-eyebrow {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--accent-color);
  margin-bottom: 0.6rem;
}

.section-title {
  font-size: 2.6rem;
  font-weight: 900;
  letter-spacing: -1px;
  color: var(--text-primary);
  margin-bottom: 0.4rem;
}

.section-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

/* ============================================
   HORARIOS
   ============================================ */
.horarios-section {
  padding-top: 2rem;
}

.horarios-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
}

.horario-dia {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.horario-dia:hover {
  transform: translateY(-3px);
  border-color: rgba(37, 99, 235, 0.4);
}

.horario-dia.cerrado {
  opacity: 0.55;
}

.horario-dia.hoy {
  background: var(--accent-light);
  border-color: var(--accent-color);
  box-shadow: 0 0 0 1px var(--accent-color), 0 8px 24px rgba(37, 99, 235, 0.15);
}

.dia-nombre {
  font-size: 0.85rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

.horario-dia.hoy .dia-nombre {
  color: var(--accent-color);
}

.dia-horario {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  line-height: 1.4;
}

.cerrado-text {
  color: var(--error-color);
}

/* ============================================
   CÓMO FUNCIONA
   ============================================ */
.como-funciona {
  position: relative;
}

.pasos-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.paso {
  position: relative;
  text-align: center;
  padding: 3rem 2rem 2.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.paso:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(37, 99, 235, 0.45);
}

.paso-numero {
  position: absolute;
  top: 18px;
  left: 22px;
  font-size: 0.95rem;
  font-weight: 900;
  letter-spacing: 1px;
  color: var(--accent-color);
  opacity: 0.8;
}

.paso-icono {
  width: 72px;
  height: 72px;
  margin: 0 auto 1.5rem;
  border-radius: 50%;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: var(--celeste);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(37, 99, 235, 0.12);
}

.paso h3 {
  font-size: 1.35rem;
  font-weight: 800;
  margin-bottom: 0.8rem;
  color: var(--text-primary);
}

.paso p {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 0.95rem;
}

/* ============================================
   PAGO DE TURNOS ONLINE (Mercado Pago)
   ============================================ */
.pago-online {
  margin: 2rem auto 0;
  max-width: 900px;
  padding: 2rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  box-shadow: var(--shadow-md);
}

.pago-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0.8rem;
}

.pago-header-icon {
  flex-shrink: 0;
  width: 46px;
  height: 46px;
  border-radius: 13px;
  background: rgba(56, 189, 248, 0.14);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: var(--celeste);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pago-header h3 {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.pago-desc {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 1.4rem;
}

.pago-desc strong {
  color: var(--accent-color);
  font-weight: 800;
}

.pago-opciones {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.pago-opcion {
  padding: 1.3rem 1.4rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.pago-opcion.destacada {
  border-color: rgba(37, 99, 235, 0.45);
  background: var(--accent-light);
}

.pago-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.6rem;
}

.pago-badge strong {
  font-size: 1.7rem;
  font-weight: 900;
  line-height: 1;
  background: var(--gradiente-azul);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.pago-badge-label {
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.pago-opcion p {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.55;
  color: var(--text-secondary);
}

.pago-presencial {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 1.3rem;
  padding: 1.1rem 1.3rem;
  background: var(--bg-primary);
  border: 1px dashed var(--border-hover);
  border-radius: 12px;
}

.pago-presencial-icon {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--accent-color);
}

.pago-presencial h4 {
  margin: 0 0 0.25rem;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-primary);
}

.pago-presencial p {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.5;
  color: var(--text-secondary);
}

/* ============================================
   SERVICIOS DESTACADOS
   ============================================ */
.servicios-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.servicio-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 2rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.servicio-card:hover {
  transform: translateY(-5px);
  border-color: rgba(37, 99, 235, 0.45);
  box-shadow: var(--shadow-lg);
}

.servicio-categoria {
  align-self: flex-start;
  padding: 6px 14px;
  border-radius: 50px;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: var(--accent-color);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.servicio-nombre {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.3;
}

.servicio-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
}

.servicio-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 1.2rem;
  border-top: 1px solid var(--border-color);
}

.servicio-precio {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.precio-moneda {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--accent-color);
}

.precio-valor {
  font-size: 1.7rem;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1;
}

.btn-detalle {
  display: inline-flex;
  align-items: center;
  padding: 9px 18px;
  border-radius: 10px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: var(--accent-color);
  font-size: 0.85rem;
  font-weight: 800;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-detalle:hover {
  background: var(--gradiente-azul);
  color: #ffffff;
  border-color: transparent;
}

/* ============================================
   PRODUCTOS DESTACADOS
   ============================================ */
.productos-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.producto-card {
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.producto-card:hover {
  transform: translateY(-5px);
  border-color: rgba(37, 99, 235, 0.45);
  box-shadow: var(--shadow-lg);
}

.producto-img {
  position: relative;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  background: var(--bg-primary);
}

.producto-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.producto-card:hover .producto-img img {
  transform: scale(1.07);
}

.btn-agregar {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 16px;
  border: none;
  border-radius: 10px;
  background: var(--gradiente-azul);
  color: #ffffff;
  font-size: 0.82rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(37, 99, 235, 0.3);
}

.btn-agregar:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.4);
}

.btn-agregar:disabled {
  background: rgba(107, 114, 128, 0.6);
  color: rgba(255, 255, 255, 0.7);
  cursor: not-allowed;
  box-shadow: none;
}

.producto-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 6px;
  padding: 1.2rem 1.4rem 1.4rem;
}

.producto-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.producto-marca {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--accent-color);
}

.producto-nombre {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.7em;
}

.producto-precio {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.producto-precio .precio-valor {
  font-size: 1.3rem;
}

/* ============================================
   BOTONES GENÉRICOS + LOADING
   ============================================ */
.ver-mas {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border-radius: 14px;
  border: 2px solid var(--border-hover);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 800;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
  transform: translateY(-2px);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 3rem 0;
}

.spinner {
  width: 44px;
  height: 44px;
  border: 3px solid var(--border-color);
  border-radius: 50%;
  border-top-color: var(--accent-color);
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================
   BANNER CTA
   ============================================ */
.cta-banner {
  position: relative;
  margin: 1.5rem 2rem 0;
  border-radius: 26px;
  overflow: hidden;
  background:
    radial-gradient(ellipse at 15% 30%, rgba(56, 189, 248, 0.22) 0%, transparent 55%),
    radial-gradient(ellipse at 85% 80%, rgba(37, 99, 235, 0.25) 0%, transparent 50%),
    linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid rgba(56, 189, 248, 0.3);
}

html.light-theme .cta-banner {
  background:
    radial-gradient(ellipse at 15% 30%, rgba(255, 255, 255, 0.18) 0%, transparent 55%),
    radial-gradient(ellipse at 85% 80%, rgba(14, 165, 233, 0.35) 0%, transparent 50%),
    var(--gradient-accent);
  border-color: transparent;
}

.cta-content {
  text-align: center;
  padding: 3.5rem 2rem;
}

.cta-content h2 {
  font-size: 2.4rem;
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 0.8rem;
  letter-spacing: -1px;
}

.cta-content p {
  color: rgba(241, 245, 249, 0.75);
  font-size: 1.1rem;
  max-width: 560px;
  margin: 0 auto 2.2rem;
  line-height: 1.6;
}

/* ============================================
   FOOTER
   ============================================ */
.footer {
  margin-top: 3rem;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.footer-grid {
  max-width: 1000px;
  margin: 0 auto;
  padding: 3rem 2rem 2rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 360px));
  justify-content: center;
  gap: 2.5rem;
}

.footer-col h4 {
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent-color);
  margin-bottom: 1.2rem;
}

.footer-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-col ul li {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.footer-col ul li svg {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--accent-color);
}

.footer-col ul li a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.25s ease;
}

.footer-col ul li a:hover {
  color: var(--accent-color);
}

.footer-bottom {
  border-top: 1px solid var(--border-color);
  text-align: center;
  padding: 1.4rem 2rem;
  font-size: 0.82rem;
  color: var(--text-tertiary);
}

.footer-bottom p {
  margin: 0;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .horarios-grid { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: 768px) {
  .hero { min-height: 82vh; padding: 5.5rem 1.5rem 3rem; }
  .hero-title { font-size: 3rem; }
  .hero-cards { grid-template-columns: 1fr; max-width: 420px; }

  .section { padding: 2.75rem 1.2rem; }
  .section-title { font-size: 2.1rem; }

  .horarios-grid { grid-template-columns: repeat(2, 1fr); }
  .pasos-grid { grid-template-columns: 1fr; }
  .servicios-grid { grid-template-columns: repeat(2, 1fr); }
  .productos-grid { grid-template-columns: repeat(2, 1fr); }

  .pago-online { padding: 1.8rem; }
  .pago-opciones { grid-template-columns: 1fr; }

  .cta-banner { margin: 1.5rem 1rem 0; }
  .cta-content h2 { font-size: 1.9rem; }

  .footer-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 480px) {
  .hero-title { font-size: 2.3rem; }
  .hero-description { font-size: 1.05rem; }
  .hero-actions { flex-direction: column; align-items: center; }
  .btn-cta { width: 100%; justify-content: center; }

  .horarios-grid { grid-template-columns: 1fr; }
  .servicios-grid { grid-template-columns: 1fr; }
  .productos-grid { grid-template-columns: 1fr; }

  .footer-grid { grid-template-columns: 1fr; }
}
</style>
