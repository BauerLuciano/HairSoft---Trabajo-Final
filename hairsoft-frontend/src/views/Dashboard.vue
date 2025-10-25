<template>
  <div :class="['dashboard-container', { 'light-mode': isLightModeReactive }]">

    <div class="header">
      <div class="header-content">
        
        <div class="title-section">
          <h1 class="main-title">
            <span class="scissors-icon">✂️</span>
            PANEL DE GESTIÓN AVANZADA
          </h1>
          <p class="subtitle">Análisis Estratégico de **Los Últimos Serán Los Primeros**</p>
        </div>
        
        <div class="period-buttons">
          <button
            v-for="period in ['hoy', 'semana', 'mes']"
            :key="period"
            @click="selectedPeriod = period"
            :class="['period-btn', { active: selectedPeriod === period }]"
          >
            {{ period === 'hoy' ? 'HOY' : period === 'semana' ? 'SEMANA' : 'MES' }}
          </button>
        </div>
      </div>
    </div>

    <div class="container">
      
      <section class="section-kpis">
        <h2 class="section-title">Resultados Clave del Período</h2>
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon kpi-icon-gold"><span>💰</span></div>
              <div class="kpi-trend">
                <span>📈</span>
                <span class="trend-value">{{ currentKpis.crecimientoVentas }}%</span>
              </div>
            </div>
            <p class="kpi-label">Ingresos Totales</p>
            <p class="kpi-value">${{ (currentKpis.ventasDia / 1000).toFixed(1) }}K</p>
            <p class="kpi-meta">Meta mensual: $150K</p>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon kpi-icon-silver"><span>✂️</span></div>
              <div class="kpi-badge">⚡</div>
            </div>
            <p class="kpi-label">Servicios Realizados</p>
            <p class="kpi-value">{{ currentKpis.serviciosRealizados }}</p>
            <p class="kpi-meta">Ticket promedio: ${{ currentKpis.ticketPromedio }}</p>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon kpi-icon-new"><span>👤</span></div>
              <div class="kpi-badge">🏆</div>
            </div>
            <p class="kpi-label">Clientes Nuevos</p>
            <p class="kpi-value">{{ currentKpis.clientesNuevos }}</p>
            <p class="kpi-meta">Total registrados: {{ currentKpis.usuarios }}</p>
          </div>

          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon kpi-icon-product"><span>🛍️</span></div>
              <div class="kpi-badge">⭐</div>
            </div>
            <p class="kpi-label">Productos Vendidos</p>
            <p class="kpi-value">{{ currentKpis.productosVendidos }}</p>
            <p class="kpi-meta">Stock bajo: {{ stockProductos.length }} items</p>
          </div>
        </div>
      </section>

      <div v-if="stockProductos.length > 0" class="alert-box alert-warning">
        <div class="alert-content">
          <div class="alert-icon"><span>⚠️</span></div>
          <div class="alert-body">
            <h3 class="alert-title">
              Alerta de Stock Crítico
              <span class="alert-badge">{{ stockProductos.length }} productos</span>
            </h3>
            <div class="stock-grid">
              <div v-for="(item, idx) in stockProductos" :key="idx" class="stock-item">
                <div class="stock-header">
                  <p class="stock-name">{{ item.producto }}</p>
                  <span class="stock-icon">📦</span>
                </div>
                <div class="stock-info">
                  <span class="stock-category">{{ item.categoria }}</span>
                  <span class="stock-quantity">Stock: {{ item.stock }}</span>
                </div>
                <div class="stock-minimum">
                  Mínimo: {{ item.minimo }} uds.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <section class="section-charts">
        <h2 class="section-title">Rendimiento Detallado</h2>
        <div class="charts-grid">
          
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">
                <div class="chart-icon chart-icon-gold"><span>✂️</span></div>
                Servicios Destacados
              </h3>
            </div>
            <div class="servicios-list">
              <div v-for="(servicio, idx) in serviciosMasSolicitados" :key="idx" class="servicio-item">
                <div class="servicio-header">
                  <p class="servicio-name">{{ servicio.nombre }}</p>
                  <span :class="['servicio-trend', servicio.tendencia >= 0 ? 'trend-up' : 'trend-down']">
                    {{ servicio.tendencia >= 0 ? '↑' : '↓' }} {{ Math.abs(servicio.tendencia) }}%
                  </span>
                </div>
                <div class="servicio-stats">
                  <span class="servicio-quantity">{{ servicio.cantidad }}</span>
                  <span class="servicio-revenue">${{ (servicio.ingresos / 1000).toFixed(0) }}K</span>
                </div>
              </div>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">
                <div class="chart-icon chart-icon-silver"><span>🏆</span></div>
                Top Peluqueros
              </h3>
            </div>
            <div class="peluqueros-list">
              <div v-for="(peluquero, idx) in rendimientoPeluqueros" :key="idx" class="peluquero-item">
                <div class="peluquero-info">
                  <div class="peluquero-rank">{{ idx + 1 }}</div>
                  <div class="peluquero-details">
                    <p class="peluquero-name">{{ peluquero.nombre }}</p>
                    <p class="peluquero-services">{{ peluquero.servicios }} servicios</p>
                  </div>
                </div>
                <div class="peluquero-revenue">
                  <p class="revenue-amount">${{ (peluquero.ingresos / 1000).toFixed(0) }}K</p>
                  <p class="revenue-label">INGRESOS</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section-products">
        <div class="chart-card large-card">
          <div class="chart-header">
            <h3 class="chart-title">
              <div class="chart-icon chart-icon-product"><span>📦</span></div>
              Productos Más Vendidos
            </h3>
          </div>
          <div class="products-grid">
            <div v-for="(producto, idx) in productosTopVentas" :key="idx" class="product-card">
              <div class="product-rank">{{ idx + 1 }}</div>
              <p class="product-name">{{ producto.nombre }}</p>
              <p class="product-units">{{ producto.ventas }} unidades</p>
              <p class="product-revenue">${{ (producto.ingresos / 1000).toFixed(1) }}K</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';

export default {
  name: 'Dashboard',
  setup() {
    const isLightModeReactive = ref(document.body.classList.contains('light-mode'));

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                isLightModeReactive.value = document.body.classList.contains('light-mode');
            }
        });
    });

    onMounted(() => {
        observer.observe(document.body, { attributes: true });
    });
    
    const selectedPeriod = ref('semana');
    const kpis = {
        hoy: { usuarios: 247, ventasDia: 8500, crecimientoVentas: 12.5, serviciosRealizados: 156, clientesNuevos: 23, ticketPromedio: 2850, productosVendidos: 45 },
        semana: { usuarios: 247, ventasDia: 52000, crecimientoVentas: 18.2, serviciosRealizados: 890, clientesNuevos: 67, ticketPromedio: 3100, productosVendidos: 234 },
        mes: { usuarios: 247, ventasDia: 125000, crecimientoVentas: 15.8, serviciosRealizados: 3240, clientesNuevos: 234, ticketPromedio: 2950, productosVendidos: 892 }
    };
    const serviciosMasSolicitados = [
        { nombre: 'Corte + Barba', cantidad: 145, ingresos: 435000, tendencia: 12 },
        { nombre: 'Coloración', cantidad: 98, ingresos: 588000, tendencia: 8 },
        { nombre: 'Tratamiento', cantidad: 87, ingresos: 348000, tendencia: -3 },
        { nombre: 'Peinado', cantidad: 56, ingresos: 336000, tendencia: 15 },
        { nombre: 'Alisado', cantidad: 42, ingresos: 378000, tendencia: 5 }
    ];
    const rendimientoPeluqueros = [
        { nombre: 'Ana Martínez', servicios: 45, ingresos: 135000 },
        { nombre: 'Carlos Ruiz', servicios: 38, ingresos: 114000 },
        { nombre: 'Diego López', servicios: 42, ingresos: 126000 },
        { nombre: 'María Sánchez', servicios: 36, ingresos: 108000 },
        { nombre: 'Laura Gómez', servicios: 40, ingresos: 120000 }
    ];
    const stockProductos = [
        { producto: 'Shampoo Kerastase', stock: 3, minimo: 10, categoria: 'Cuidado' },
        { producto: 'Tinte Loreal 6.3', stock: 2, minimo: 8, categoria: 'Color' },
        { producto: 'Cera Modeladora', stock: 4, minimo: 12, categoria: 'Styling' }
    ];
    const productosTopVentas = [
        { nombre: 'Shampoo Kerastase', ventas: 45, ingresos: 112500 },
        { nombre: 'Cera American Crew', ventas: 38, ingresos: 45600 },
        { nombre: 'Acondicionador Pantene', ventas: 32, ingresos: 48000 },
        { nombre: 'Tinte Loreal', ventas: 28, ingresos: 50400 },
        { nombre: 'Spray Fijador', ventas: 25, ingresos: 22500 }
    ];

    const currentKpis = computed(() => kpis[selectedPeriod.value]);

    return {
      selectedPeriod,
      currentKpis,
      serviciosMasSolicitados,
      rendimientoPeluqueros,
      stockProductos,
      productosTopVentas,
      isLightModeReactive 
    };
  }
}
</script>

<style scoped>
/*
 * 🌑 ESTILO PRINCIPAL (DARK MODE) OPTIMIZADO CON MEJOR CONTRASTE 🌑
 */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* --- PALETA DE COLORES (DARK MODE SOFISTICADO) --- */
:root {
    --color-bg-primary: #0A0E27; /* Fondo azul oscuro profundo */
    --color-bg-secondary: #1A1F3A; /* Fondo de tarjetas (azul oscuro con mejor contraste) */
    --color-bg-tertiary: #252B47; /* Fondo de listas/botones (azul intermedio más claro) */
    --color-text-light: #FFFFFF; /* Texto principal (blanco puro) */
    --color-text-muted: #A8B2D1; /* Texto secundario (azul grisáceo claro) */
    --color-accent-gold: #FFD700; /* Dorado brillante */
    --color-accent-gold-dark: #D4AF37; 
    --color-border: #3D4563; /* Borde visible azul grisáceo */
    --color-border-light: #505875; /* Borde más claro para elementos internos */
    --color-alert: #FF9800; 
    --color-alert-bg: #2A1F0F; /* Fondo de alerta oscuro y diferenciado */
}

/* Light Mode */
.dashboard-container.light-mode {
    --color-bg-primary: #F5F7FA;
    --color-bg-secondary: #FFFFFF;
    --color-bg-tertiary: #F0F3F7; 
    --color-text-light: #2C3E50;
    --color-text-muted: #7F8C8D;
    --color-accent-gold: #D4AF37;
    --color-accent-gold-dark: #A0802C;
    --color-border: #E0E6EE;
    --color-border-light: #F0F3F7;
    --color-alert: #E67E22;
    --color-alert-bg: #FFF8E1; 
}

/* --- BASE --- */
* { margin: 0; padding: 0; box-sizing: border-box; }

.dashboard-container {
  min-height: 100vh;
  background: var(--color-bg-primary); 
  font-family: 'Inter', sans-serif;
  color: var(--color-text-light); 
  transition: background 0.3s ease; 
}

.container { max-width: 1280px; margin: 0 auto; padding: 2.5rem 2rem; }

/* --- HEADER --- */
.header {
  background: var(--color-bg-secondary);
  border-bottom: 2px solid var(--color-accent-gold);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); 
}
.header-content {
  max-width: 1280px; margin: 0 auto; padding: 1.5rem 2rem; display: flex;
  align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 2rem;
}
.title-section { display: flex; flex-direction: column; }
.main-title {
  font-size: 2rem; font-weight: 800; color: var(--color-text-light); letter-spacing: 0.04em;
  display: flex; align-items: center; gap: 0.75rem; text-transform: uppercase;
}
.scissors-icon { font-size: 1.8rem; color: var(--color-accent-gold); }
.subtitle { color: var(--color-accent-gold); font-size: 0.9rem; margin-top: 0.4rem; font-weight: 500; letter-spacing: 0.1em; }
.period-buttons { display: flex; gap: 0.5rem; }
.period-btn {
  padding: 0.6rem 1.2rem; border-radius: 0.4rem; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; cursor: pointer; transition: all 0.2s ease-in-out;
  border: 1px solid var(--color-border);
  background: var(--color-bg-tertiary);
  color: var(--color-text-light);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.period-btn.active {
  background: linear-gradient(to right, var(--color-accent-gold), var(--color-accent-gold-dark));
  color: #FFFFFF; border-color: var(--color-accent-gold-dark); box-shadow: 0 5px 12px rgba(255, 215, 0, 0.3);
}
.period-btn:hover:not(.active) {
  background: var(--color-border); border-color: var(--color-accent-gold); color: var(--color-text-light);
}

/* --- SECCIONES Y GRID --- */
.section-title { 
    font-size: 1.5rem; font-weight: 700; color: var(--color-accent-gold); margin-bottom: 1.5rem;
    padding-bottom: 0.5rem; border-bottom: 1px solid var(--color-border);
}

.kpi-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;
}

.charts-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;
}
.products-grid {
    display: flex; gap: 1rem; flex-wrap: wrap; justify-content: space-between;
}

/* --- KPI CARD & CHART CARD (¡CLAVE DEL CONTRASTE!) --- */
.kpi-card, .chart-card {
  background: var(--color-bg-secondary);
  border-radius: 0.8rem; padding: 1.5rem;
  border: 2px solid var(--color-border); 
  box-shadow: 0 4px 15px rgba(61, 69, 99, 0.5), 0 0 20px rgba(255, 215, 0, 0.05); 
  transition: all 0.2s ease-in-out;
}

.kpi-card:hover, .chart-card:hover { 
    border-color: var(--color-accent-gold); 
    transform: translateY(-3px); 
    box-shadow: 0 8px 25px rgba(61, 69, 99, 0.7), 0 0 30px rgba(255, 215, 0, 0.2); 
}

.kpi-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }

.kpi-icon { padding: 0.7rem; border-radius: 50%; box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1); font-size: 1.4rem; color: #FFFFFF; }
.kpi-icon-gold { background: var(--color-accent-gold); }
.kpi-icon-silver { background: #95A5A6; }
.kpi-icon-new { background: #2ECC71; }
.kpi-icon-product { background: #3498DB; }

.kpi-label { color: var(--color-text-muted); font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-value { font-size: 2.8rem; font-weight: 800; color: var(--color-text-light); margin-top: 0.4rem; }
.kpi-meta { font-size: 0.75rem; color: var(--color-text-muted); margin-top: 0.4rem; font-weight: 400; }
.kpi-trend { color: #2ECC71; font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; gap: 0.2rem; }
.trend-value { margin-left: 0.2rem; }

/* --- ALERT BOX --- */
.alert-box {
  background: var(--color-alert-bg); 
  border-left: 5px solid var(--color-alert);
  border-radius: 0.8rem; padding: 1.5rem; margin-bottom: 3rem;
  box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4); 
  border: 1px solid var(--color-alert);
}
.alert-content { display: flex; gap: 1.5rem; }
.alert-icon { 
    background: var(--color-alert); 
    color: var(--color-bg-primary); 
    padding: 0.8rem; border-radius: 50%; font-size: 1.2rem; align-self: flex-start; 
}
.alert-title { 
    color: var(--color-alert); 
    font-weight: 700; font-size: 1.15rem; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.04em; 
}

.stock-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;
}
.stock-item {
  background: var(--color-bg-tertiary); 
  border-radius: 0.5rem; padding: 1rem;
  border: 1.5px solid var(--color-border-light);
  transition: all 0.2s ease-in-out;
  box-shadow: 0 2px 6px rgba(255, 152, 0, 0.2);
}
.stock-item:hover {
    background: color-mix(in srgb, var(--color-bg-tertiary), white 8%); 
    border-color: var(--color-alert);
    box-shadow: 0 4px 10px rgba(255, 152, 0, 0.3);
}
.stock-header { display: flex; justify-content: space-between; align-items: center; }
.stock-name { font-weight: 700; color: var(--color-text-light); font-size: 0.9rem; }
.stock-quantity { font-weight: 600; color: #FF6B6B; }

/* --- CHART CARD & LISTS --- */
.chart-header { margin-bottom: 1rem; }
.chart-title { font-size: 1.1rem; font-weight: 700; color: var(--color-text-light); text-transform: uppercase; letter-spacing: 0.02em; display: flex; align-items: center; gap: 0.5rem; }
.chart-icon { padding: 0.5rem; border-radius: 0.3rem; font-size: 1.2rem; color: #FFFFFF; }
.chart-icon-gold { background: var(--color-accent-gold); }
.chart-icon-silver { background: #95A5A6; }
.chart-icon-product { background: #3498DB; }

.servicios-list, .peluqueros-list { display: flex; flex-direction: column; gap: 0.6rem; }

.servicio-item, .peluquero-item, .product-card {
  background: var(--color-bg-tertiary);
  border-radius: 0.5rem; padding: 1rem;
  border: 1.5px solid var(--color-border-light);
  transition: all 0.2s ease-in-out;
  box-shadow: 0 2px 8px rgba(61, 69, 99, 0.3);
}

.servicio-item:hover, .peluquero-item:hover, .product-card:hover { 
    border-color: var(--color-accent-gold); 
    background: color-mix(in srgb, var(--color-bg-tertiary), white 8%); 
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.2);
}

.servicio-header, .peluquero-info { display: flex; justify-content: space-between; align-items: center; }
.servicio-stats { display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 0.5rem; }

.servicio-name, .peluquero-name { font-weight: 600; color: var(--color-text-light); }
.servicio-revenue, .revenue-amount { color: var(--color-accent-gold); font-weight: 700; }
.trend-up { color: #2ECC71; }
.trend-down { color: #E74C3C; }

.peluquero-rank { background: var(--color-accent-gold); color: #FFFFFF; padding: 0.4rem 0.6rem; border-radius: 0.3rem; font-weight: 700; font-size: 0.9rem; }
.peluquero-info { align-items: flex-start; gap: 1rem; }
.peluquero-details { flex-grow: 1; }
.peluquero-services { color: var(--color-text-muted); font-size: 0.75rem; }

.product-card {
  width: calc(20% - 10px); 
  min-width: 150px;
  background: var(--color-bg-tertiary);
  border-radius: 0.6rem; padding: 1rem;
  border: 1.5px solid var(--color-border-light);
  box-shadow: 0 2px 8px rgba(61, 69, 99, 0.3);
  transition: all 0.2s ease-in-out;
  text-align: center;
}

/* --- LIGHT MODE ADJUSTMENTS --- */
.dashboard-container.light-mode .header {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-bottom-color: var(--color-accent-gold);
}

.dashboard-container.light-mode .period-btn {
  background: var(--color-bg-secondary);
  color: var(--color-text-light);
  border-color: var(--color-border);
}

.dashboard-container.light-mode .kpi-card,
.dashboard-container.light-mode .chart-card {
  background: var(--color-bg-secondary);
  box-shadow: 0 6px 15px rgba(44, 62, 80, 0.06);
}

.dashboard-container.light-mode .servicio-item,
.dashboard-container.light-mode .peluquero-item,
.dashboard-container.light-mode .product-card {
  background: var(--color-bg-tertiary);
}

.dashboard-container.light-mode .alert-box {
    box-shadow: 0 4px 15px rgba(230, 126, 34, 0.2);
    background: var(--color-alert-bg); 
    border-left: 5px solid var(--color-alert);
}
.dashboard-container.light-mode .stock-item {
    background: var(--color-bg-tertiary); 
    border: 1px solid var(--color-border);
}

/* --- Responsive --- */
@media (max-width: 1024px) {
  .charts-grid { grid-template-columns: 1fr; }
  .products-grid { justify-content: space-around; }
  .product-card { width: calc(33% - 15px); }
}

@media (max-width: 768px) {
  .header-content { flex-direction: column; align-items: flex-start; padding: 1rem; }
  .main-title { font-size: 1.8rem; }
  .kpi-grid { grid-template-columns: 1fr; }
  .container { padding: 1.5rem 1rem; }
  .product-card { width: calc(50% - 10px); }
  .alert-content { flex-direction: column; gap: 0.75rem; }
}
</style>