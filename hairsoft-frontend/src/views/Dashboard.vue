<template>
  <div class="dashboard-container">
    <div class="header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo-icon-wrapper">
            <div class="logo-icon-blur"></div>
            <div class="logo-icon">
              <span class="scissors-icon">✂️</span>
            </div>
          </div>
          <div class="title-section">
            <h1 class="main-title">
              <span>𝕷𝖔𝖘 Ú𝖑</span>
              <svg viewBox="0 0 100 140" class="caduceus-svg">
                <defs>
                  <linearGradient id="caduceus-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#D4AF37;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#B8941F;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <rect x="48" y="15" width="4" height="120" fill="url(#caduceus-gradient)" />
                <circle cx="50" cy="12" r="5" fill="url(#caduceus-gradient)" />
                <path d="M 30,25 Q 35,30 40,35 Q 45,40 50,45 Q 55,50 50,55 Q 45,60 40,65 Q 35,70 30,75" fill="none" stroke="url(#caduceus-gradient)" stroke-width="3.5" stroke-linecap="round"/>
                <circle cx="30" cy="25" r="4" fill="url(#caduceus-gradient)" />
                <circle cx="29" cy="24" r="1" fill="#000" />
                <path d="M 70,25 Q 65,30 60,35 Q 55,40 50,45 Q 45,50 50,55 Q 55,60 60,65 Q 65,70 70,75" fill="none" stroke="url(#caduceus-gradient)" stroke-width="3.5" stroke-linecap="round"/>
                <circle cx="70" cy="25" r="4" fill="url(#caduceus-gradient)" />
                <circle cx="71" cy="24" r="1" fill="#000" />
                <path d="M 50,15 Q 30,8 15,12 Q 10,13 12,18 Q 14,22 20,20 Q 30,17 40,20 Q 45,21 50,20" fill="url(#caduceus-gradient)" stroke="url(#caduceus-gradient)" stroke-width="1"/>
                <path d="M 45,18 Q 35,15 25,16 Q 20,17 21,20 Q 22,23 27,22 Q 35,20 42,22" fill="url(#caduceus-gradient)" opacity="0.8"/>
                <path d="M 40,20 Q 32,18 26,19 Q 23,20 24,22 Q 25,24 29,23 Q 35,22 39,24" fill="url(#caduceus-gradient)" opacity="0.6"/>
                <path d="M 50,15 Q 70,8 85,12 Q 90,13 88,18 Q 86,22 80,20 Q 70,17 60,20 Q 55,21 50,20" fill="url(#caduceus-gradient)" stroke="url(#caduceus-gradient)" stroke-width="1"/>
                <path d="M 55,18 Q 65,15 75,16 Q 80,17 79,20 Q 78,23 73,22 Q 65,20 58,22" fill="url(#caduceus-gradient)" opacity="0.8"/>
                <path d="M 60,20 Q 68,18 74,19 Q 77,20 76,22 Q 75,24 71,23 Q 65,22 61,24" fill="url(#caduceus-gradient)" opacity="0.6"/>
              </svg>
              <span>𝖎𝖒𝖔𝖘 𝕾𝖊𝖗á𝖓 𝖑𝖔𝖘 𝕻𝖗𝖎𝖒𝖊𝖗𝖔𝖘</span>
            </h1>
            <p class="subtitle">PANEL DE CONTROL PROFESIONAL</p>
          </div>
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
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon kpi-icon-gold">
              <span>💰</span>
            </div>
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
            <div class="kpi-icon kpi-icon-gray">
              <span>✂️</span>
            </div>
            <div class="kpi-badge">⚡</div>
          </div>
          <p class="kpi-label">Servicios</p>
          <p class="kpi-value">{{ currentKpis.serviciosRealizados }}</p>
          <p class="kpi-meta">Ticket promedio: ${{ currentKpis.ticketPromedio }}</p>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon kpi-icon-silver">
              <span>👤</span>
            </div>
            <div class="kpi-badge">🏆</div>
          </div>
          <p class="kpi-label">Clientes Nuevos</p>
          <p class="kpi-value">{{ currentKpis.clientesNuevos }}</p>
          <p class="kpi-meta">Total registrados: {{ currentKpis.usuarios }}</p>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon kpi-icon-dark">
              <span>🛍️</span>
            </div>
            <div class="kpi-badge">⭐</div>
          </div>
          <p class="kpi-label">Productos Vendidos</p>
          <p class="kpi-value">{{ currentKpis.productosVendidos }}</p>
          <p class="kpi-meta">Stock en alerta</p>
        </div>
      </div>

      <div v-if="stockProductos.length > 0" class="alert-box">
        <div class="alert-content">
          <div class="alert-icon">
            <span>⚠️</span>
          </div>
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
                  Mínimo requerido: {{ item.minimo }} unidades
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <h2 class="chart-title">
              <div class="chart-icon chart-icon-gold">
                <span>✂️</span>
              </div>
              Servicios Destacados
            </h2>
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
                <span class="servicio-quantity">Cantidad: {{ servicio.cantidad }}</span>
                <span class="servicio-revenue">${{ (servicio.ingresos / 1000).toFixed(0) }}K</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h2 class="chart-title">
              <div class="chart-icon chart-icon-silver">
                <span>🏆</span>
              </div>
              Top Peluqueros
            </h2>
          </div>
          <div class="peluqueros-list">
            <div v-for="(peluquero, idx) in rendimientoPeluqueros" :key="idx" class="peluquero-item">
              <div class="peluquero-info">
                <div class="peluquero-rank">{{ idx + 1 }}</div>
                <div class="peluquero-details">
                  <p class="peluquero-name">{{ peluquero.nombre }}</p>
                  <p class="peluquero-services">{{ peluquero.servicios }} servicios realizados</p>
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

      <div class="chart-card">
        <div class="chart-header">
          <h2 class="chart-title">
            <div class="chart-icon chart-icon-dark">
              <span>📦</span>
            </div>
            Productos Más Vendidos
          </h2>
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
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      selectedPeriod: 'semana',
      kpis: {
        hoy: {
          usuarios: 247,
          ventasDia: 8500,
          crecimientoVentas: 12.5,
          serviciosRealizados: 156,
          clientesNuevos: 23,
          ticketPromedio: 2850,
          productosVendidos: 45
        },
        semana: {
          usuarios: 247,
          ventasDia: 52000,
          crecimientoVentas: 18.2,
          serviciosRealizados: 890,
          clientesNuevos: 67,
          ticketPromedio: 3100,
          productosVendidos: 234
        },
        mes: {
          usuarios: 247,
          ventasDia: 125000,
          crecimientoVentas: 15.8,
          serviciosRealizados: 3240,
          clientesNuevos: 234,
          ticketPromedio: 2950,
          productosVendidos: 892
        }
      },
      serviciosMasSolicitados: [
        { nombre: 'Corte + Barba', cantidad: 145, ingresos: 435000, tendencia: 12 },
        { nombre: 'Coloración', cantidad: 98, ingresos: 588000, tendencia: 8 },
        { nombre: 'Tratamiento', cantidad: 87, ingresos: 348000, tendencia: -3 },
        { nombre: 'Peinado', cantidad: 56, ingresos: 336000, tendencia: 15 },
        { nombre: 'Alisado', cantidad: 42, ingresos: 378000, tendencia: 5 }
      ],
      rendimientoPeluqueros: [
        { nombre: 'Ana Martínez', servicios: 45, ingresos: 135000 },
        { nombre: 'Carlos Ruiz', servicios: 38, ingresos: 114000 },
        { nombre: 'Diego López', servicios: 42, ingresos: 126000 },
        { nombre: 'María Sánchez', servicios: 36, ingresos: 108000 },
        { nombre: 'Laura Gómez', servicios: 40, ingresos: 120000 }
      ],
      stockProductos: [
        { producto: 'Shampoo Kerastase', stock: 3, minimo: 10, categoria: 'Cuidado' },
        { producto: 'Tinte Loreal 6.3', stock: 2, minimo: 8, categoria: 'Color' },
        { producto: 'Cera Modeladora', stock: 4, minimo: 12, categoria: 'Styling' }
      ],
      productosTopVentas: [
        { nombre: 'Shampoo Kerastase', ventas: 45, ingresos: 112500 },
        { nombre: 'Cera American Crew', ventas: 38, ingresos: 45600 },
        { nombre: 'Acondicionador Pantene', ventas: 32, ingresos: 48000 },
        { nombre: 'Tinte Loreal', ventas: 28, ingresos: 50400 },
        { nombre: 'Spray Fijador', ventas: 25, ingresos: 22500 }
      ]
    }
  },
  computed: {
    currentKpis() {
      return this.kpis[this.selectedPeriod]
    }
  }
}
</script>

<style scoped>
/* Base Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Dashboard Container */
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(to bottom right, #09090b, #000000, #18181b);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header */
.header {
  background: #000;
  border-bottom: 2px solid #D4AF37;
  box-shadow: 0 20px 50px rgba(212, 175, 55, 0.2);
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 2rem;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo-icon-wrapper {
  position: relative;
}

.logo-icon-blur {
  position: absolute;
  inset: 0;
  background: #D4AF37;
  border-radius: 1rem;
  filter: blur(20px);
  opacity: 0.5;
}

.logo-icon {
  position: relative;
  background: linear-gradient(to bottom right, #D4AF37, #B8941F);
  padding: 1rem;
  border-radius: 1rem;
  box-shadow: 0 25px 50px rgba(212, 175, 55, 0.3);
  border: 2px solid #D4AF37;
}

.scissors-icon {
  font-size: 2.5rem;
  display: block;
}

.main-title {
  font-size: 3rem;
  font-weight: 900;
  /* Utilizando una fuente serif con carácter */
  font-family: 'Times New Roman', Times, serif; 
  color: #D4AF37;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.8), 0 0 20px rgba(212,175,55,0.3);
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.caduceus-svg {
  height: 4rem;
  margin: 0 0.25rem;
  filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.8)) drop-shadow(0 0 20px rgba(212,175,55,0.3));
}

.subtitle {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-weight: 500;
  letter-spacing: 0.1em;
}

.period-buttons {
  display: flex;
  gap: 0.75rem;
}

.period-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid #3f3f46;
  background: #18181b;
  color: #9ca3af;
}

.period-btn.active {
  background: linear-gradient(to right, #D4AF37, #B8941F);
  color: #000;
  border-color: #D4AF37;
  box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
}

.period-btn:hover:not(.active) {
  background: #27272a;
  border-color: #52525b;
}

/* Container */
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: linear-gradient(to bottom right, #18181b, #000);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 2px solid #27272a;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  transition: all 0.3s;
}

.kpi-card:hover {
  border-color: rgba(212, 175, 55, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 25px 50px rgba(212, 175, 55, 0.2);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.kpi-icon {
  padding: 0.75rem;
  border-radius: 0.75rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  font-size: 1.5rem;
}

.kpi-icon-gold {
  background: linear-gradient(to bottom right, #D4AF37, #B8941F);
  border: 1px solid #D4AF37;
}

.kpi-icon-gray {
  background: linear-gradient(to bottom right, #52525b, #27272a);
  border: 1px solid #71717a;
}

.kpi-icon-silver {
  background: linear-gradient(to bottom right, #71717a, #52525b);
  border: 1px solid #9ca3af;
}

.kpi-icon-dark {
  background: linear-gradient(to bottom right, #52525b, #3f3f46);
  border: 1px solid #71717a;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #10b981; /* Verde para crecimiento */
  font-weight: 700;
  font-size: 0.875rem;
}

.kpi-trend span:first-child {
  font-size: 1.2rem;
}

.trend-value {
  font-size: 0.875rem;
}

.kpi-badge {
  font-size: 1.25rem;
  color: #D4AF37;
}

.kpi-label {
  color: #71717a;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.kpi-value {
  font-size: 3rem;
  font-weight: 900;
  color: #fff;
  margin-top: 0.5rem;
}

.kpi-meta {
  font-size: 0.75rem;
  color: #52525b;
  margin-top: 0.5rem;
  font-weight: 500;
}

/* Alert Box */
.alert-box {
  background: linear-gradient(to right, #450a0a, #000);
  border-left: 4px solid #dc2626;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(220, 38, 38, 0.5);
}

.alert-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.alert-icon {
  background: #7f1d1d;
  padding: 0.75rem;
  border-radius: 0.75rem;
  border: 2px solid #991b1b;
  font-size: 1.5rem;
}

.alert-body {
  flex: 1;
}

.alert-title {
  color: #f87171;
  font-weight: 900;
  font-size: 1.125rem;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.alert-badge {
  background: #dc2626;
  color: #fff;
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 700;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.stock-item {
  background: #09090b;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 2px solid rgba(127, 29, 29, 0.5);
  transition: all 0.3s;
}

.stock-item:hover {
  border-color: rgba(220, 38, 38, 0.5);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stock-name {
  font-weight: 700;
  color: #fff;
  font-size: 0.875rem;
}

.stock-icon {
  font-size: 1.25rem;
}

.stock-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
}

.stock-category {
  color: #71717a;
  font-weight: 500;
}

.stock-quantity {
  font-weight: 700;
  color: #f87171; /* Rojo para el stock bajo */
}

.stock-minimum {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #52525b;
  font-weight: 500;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: linear-gradient(to bottom right, #18181b, #000);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 2px solid #27272a;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 900;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.chart-icon {
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1.25rem;
}

.chart-icon-gold {
  background: linear-gradient(to bottom right, #D4AF37, #B8941F);
  border: 1px solid #D4AF37;
}

.chart-icon-silver {
  background: linear-gradient(to bottom right, #71717a, #52525b);
  border: 1px solid #9ca3af;
}

.chart-icon-dark {
  background: linear-gradient(to bottom right, #3f3f46, #18181b);
  border: 1px solid #52525b;
}

/* Servicios List */
.servicios-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.servicio-item {
  background: #09090b;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 2px solid #27272a;
  transition: all 0.3s;
}

.servicio-item:hover {
  border-color: rgba(212, 175, 55, 0.5);
}

.servicio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.servicio-name {
  font-weight: 700;
  color: #fff;
}

.servicio-trend {
  font-size: 0.875rem;
  font-weight: 900;
}

.trend-up {
  color: #10b981; /* Verde */
}

.trend-down {
  color: #f87171; /* Rojo */
}

.servicio-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.servicio-quantity {
  color: #9ca3af;
}

.servicio-revenue {
  color: #D4AF37;
  font-weight: 700;
}

/* Peluqueros List */
.peluqueros-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.peluquero-item {
  background: #09090b;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 2px solid #27272a;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s;
}

.peluquero-item:hover {
  border-color: rgba(212, 175, 55, 0.5);
}

.peluquero-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.peluquero-rank {
  background: linear-gradient(to bottom right, #D4AF37, #B8941F);
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 900;
  color: #000;
  box-shadow: 0 5px 15px rgba(212, 175, 55, 0.5);
}

.peluquero-details {
  display: flex;
  flex-direction: column;
}

.peluquero-name {
  font-weight: 700;
  color: #fff;
  font-size: 1rem;
}

.peluquero-services {
  color: #71717a;
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 0.25rem;
}

.peluquero-revenue {
  text-align: right;
}

.revenue-amount {
  font-size: 1.5rem;
  font-weight: 900;
  color: #D4AF37;
}

.revenue-label {
  font-size: 0.65rem;
  color: #52525b;
  font-weight: 700;
  text-transform: uppercase;
  margin-top: 0.25rem;
}

/* Productos Top Ventas Grid */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.product-card {
  background: linear-gradient(to bottom, #09090b, #000);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 2px solid #27272a;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  text-align: center;
  position: relative;
  transition: all 0.3s;
}

.product-card:hover {
  border-color: #52525b;
  transform: translateY(-2px);
}

.product-rank {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  background: #D4AF37;
  color: #000;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 900;
  font-size: 0.75rem;
  box-shadow: 0 5px 10px rgba(212, 175, 55, 0.5);
}

.product-name {
  font-weight: 700;
  color: #fff;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-units {
  color: #71717a;
  font-size: 0.75rem;
  margin: 0.5rem 0;
}

.product-revenue {
  font-size: 1.25rem;
  font-weight: 900;
  color: #D4AF37;
}

/* Media Queries for Responsiveness */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .main-title {
    font-size: 2rem;
  }

  .caduceus-svg {
    height: 3rem;
  }

  .kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 600px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .stock-grid {
    grid-template-columns: 1fr;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
</style>