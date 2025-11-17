<template>
  <div :class="['dashboard-container', { 'light-mode': isLightModeReactive }]">

    <div class="header">
      <div class="header-content">
        
        <div class="title-section">
          <h1 class="main-title">
            <span class="scissors-icon">✂️</span>
            PANEL DE GESTIÓN AVANZADA
          </h1>
          <p class="subtitle">Análisis Estratégico en Tiempo Real</p>
        </div>
        
        <div class="period-buttons">
          <button
            v-for="period in periodOptions"
            :key="period.value"
            @click="changePeriod(period.value)"
            :class="['period-btn', { active: selectedPeriod === period.value }]"
            :disabled="loading"
          >
            {{ period.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="container">
      
      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">Cargando datos del dashboard...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <h3 class="error-title">Error al cargar datos</h3>
        <p class="error-message">{{ error }}</p>
        <button @click="fetchDashboardData" class="btn-retry">Reintentar</button>
      </div>

      <!-- Main Content -->
      <div v-else>
        <section class="section-kpis">
          <h2 class="section-title">Resultados Clave del Período</h2>
          <div class="kpi-grid">
            <div class="kpi-card">
              <div class="kpi-header">
                <div class="kpi-icon kpi-icon-gold"><span>💰</span></div>
                <div class="kpi-trend" :class="getTrendClass(dashboardData.ventasTrend)">
                  <span>{{ dashboardData.ventasTrend >= 0 ? '📈' : '📉' }}</span>
                  <span class="trend-value">{{ Math.abs(dashboardData.ventasTrend) }}%</span>
                </div>
              </div>
              <p class="kpi-label">Ingresos Totales</p>
              <p class="kpi-value">${{ formatCurrency(dashboardData.ingresosTotales) }}</p>
              <p class="kpi-meta">Meta: ${{ formatCurrency(dashboardData.metaMensual) }}</p>
            </div>

            <div class="kpi-card">
              <div class="kpi-header">
                <div class="kpi-icon kpi-icon-silver"><span>✂️</span></div>
                <div class="kpi-badge">⚡</div>
              </div>
              <p class="kpi-label">Servicios Realizados</p>
              <p class="kpi-value">{{ dashboardData.serviciosRealizados }}</p>
              <p class="kpi-meta">Ticket: ${{ formatCurrency(dashboardData.ticketPromedio) }}</p>
            </div>

            <div class="kpi-card">
              <div class="kpi-header">
                <div class="kpi-icon kpi-icon-new"><span>👤</span></div>
                <div class="kpi-badge">🏆</div>
              </div>
              <p class="kpi-label">Clientes Nuevos</p>
              <p class="kpi-value">{{ dashboardData.clientesNuevos }}</p>
              <p class="kpi-meta">Total: {{ dashboardData.totalClientes }}</p>
            </div>

            <div class="kpi-card">
              <div class="kpi-header">
                <div class="kpi-icon kpi-icon-product"><span>🛍️</span></div>
                <div class="kpi-badge">⭐</div>
              </div>
              <p class="kpi-label">Productos Vendidos</p>
              <p class="kpi-value">{{ dashboardData.productosVendidos }}</p>
              <p class="kpi-meta">Stock bajo: {{ dashboardData.stockBajoCount }} items</p>
            </div>
          </div>
        </section>

        <!-- Stock Alert -->
        <div v-if="dashboardData.stockBajo && dashboardData.stockBajo.length > 0" class="alert-box alert-warning">
          <div class="alert-content">
            <div class="alert-icon"><span>⚠️</span></div>
            <div class="alert-body">
              <h3 class="alert-title">
                Alerta de Stock Crítico
                <span class="alert-badge">{{ dashboardData.stockBajo.length }} productos</span>
              </h3>
              <div class="stock-grid">
                <div v-for="(item, idx) in dashboardData.stockBajo" :key="idx" class="stock-item">
                  <div class="stock-header">
                    <p class="stock-name">{{ item.nombre }}</p>
                    <span class="stock-icon">📦</span>
                  </div>
                  <div class="stock-info">
                    <span class="stock-category">{{ item.categoria }}</span>
                    <span class="stock-quantity">Stock: {{ item.stock_actual }}</span>
                  </div>
                  <div class="stock-minimum">
                    Mínimo: {{ item.stock_minimo }} uds.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Section -->
        <section class="section-charts">
          <h2 class="section-title">Rendimiento Detallado</h2>
          <div class="charts-grid">
            
            <!-- Servicios Destacados -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title">
                  <div class="chart-icon chart-icon-gold"><span>✂️</span></div>
                  Servicios Destacados
                </h3>
              </div>
              <div class="servicios-list">
                <div v-for="(servicio, idx) in dashboardData.serviciosTop" :key="idx" class="servicio-item">
                  <div class="servicio-header">
                    <p class="servicio-name">{{ servicio.nombre }}</p>
                    <span :class="['servicio-trend', servicio.tendencia >= 0 ? 'trend-up' : 'trend-down']">
                      {{ servicio.tendencia >= 0 ? '↑' : '↓' }} {{ Math.abs(servicio.tendencia) }}%
                    </span>
                  </div>
                  <div class="servicio-stats">
                    <span class="servicio-quantity">{{ servicio.cantidad }} servicios</span>
                    <span class="servicio-revenue">${{ formatCurrency(servicio.ingresos) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Top Peluqueros -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title">
                  <div class="chart-icon chart-icon-silver"><span>🏆</span></div>
                  Top Peluqueros
                </h3>
              </div>
              <div class="peluqueros-list">
                <div v-for="(peluquero, idx) in dashboardData.topPeluqueros" :key="idx" class="peluquero-item">
                  <div class="peluquero-info">
                    <div class="peluquero-rank">{{ idx + 1 }}</div>
                    <div class="peluquero-details">
                      <p class="peluquero-name">{{ peluquero.nombre }}</p>
                      <p class="peluquero-services">{{ peluquero.servicios_completados }} servicios</p>
                    </div>
                  </div>
                  <div class="peluquero-revenue">
                    <p class="revenue-amount">${{ formatCurrency(peluquero.ingresos_generados) }}</p>
                    <p class="revenue-label">INGRESOS</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Productos Más Vendidos -->
        <section class="section-products">
          <div class="chart-card large-card">
            <div class="chart-header">
              <h3 class="chart-title">
                <div class="chart-icon chart-icon-product"><span>📦</span></div>
                Productos Más Vendidos
              </h3>
            </div>
            <div class="products-grid">
              <div v-for="(producto, idx) in dashboardData.productosTop" :key="idx" class="product-card">
                <div class="product-rank">{{ idx + 1 }}</div>
                <p class="product-name">{{ producto.nombre }}</p>
                <p class="product-units">{{ producto.unidades_vendidas }} unidades</p>
                <p class="product-revenue">${{ formatCurrency(producto.ingresos) }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Estadísticas Simples -->
        <section class="section-analytics">
          <h2 class="section-title">Análisis Visual</h2>
          <div class="analytics-grid">
            
            <!-- Ventas por Día -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title">
                  <div class="chart-icon chart-icon-gold"><span>📊</span></div>
                  Ventas por Día (Últimos 7 días)
                </h3>
              </div>
              <div class="simple-chart">
                <div v-for="(venta, idx) in dashboardData.ventasPorDia" :key="idx" 
                     class="bar-container">
                  <div class="bar-label">{{ dashboardData.labelsDias[idx] }}</div>
                  <div class="bar-track">
                    <div class="bar-fill" 
                         :style="{ height: getBarHeight(venta, dashboardData.ventasPorDia) + '%' }">
                      <span class="bar-value">${{ formatCurrency(venta) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Distribución de Servicios -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title">
                  <div class="chart-icon chart-icon-silver"><span>🥧</span></div>
                  Distribución de Servicios
                </h3>
              </div>
              <div class="pie-chart-simple">
                <div v-for="(servicio, idx) in dashboardData.serviciosDistribucion" :key="idx" 
                     class="pie-item">
                  <div class="pie-color" :style="{ backgroundColor: getPieColor(idx) }"></div>
                  <span class="pie-label">{{ servicio.servicio }}</span>
                  <span class="pie-value">{{ servicio.cantidad }}%</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';

export default {
  name: 'Dashboard',
  setup() {
    // Estado reactivo
    const isLightModeReactive = ref(document.body.classList.contains('light-mode'));
    const selectedPeriod = ref('semana');
    const loading = ref(true);
    const error = ref(null);
    const dashboardData = ref({
      ingresosTotales: 0,
      serviciosRealizados: 0,
      clientesNuevos: 0,
      productosVendidos: 0,
      ticketPromedio: 0,
      ventasTrend: 0,
      metaMensual: 150000,
      totalClientes: 0,
      stockBajoCount: 0,
      stockBajo: [],
      serviciosTop: [],
      topPeluqueros: [],
      productosTop: [],
      ventasPorDia: [],
      serviciosDistribucion: [],
      labelsDias: []
    });

    // Opciones de período
    const periodOptions = [
      { value: 'hoy', label: 'HOY' },
      { value: 'semana', label: 'SEMANA' },
      { value: 'mes', label: 'MES' }
    ];

    // Observador para light mode
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          isLightModeReactive.value = document.body.classList.contains('light-mode');
        }
      });
    });

    // Formatear currency
    const formatCurrency = (amount) => {
      if (!amount && amount !== 0) return '0';
      if (amount >= 1000) {
        return (amount / 1000).toFixed(1) + 'K';
      }
      return amount.toString();
    };

    // Obtener clase de tendencia
    const getTrendClass = (trend) => {
      return trend >= 0 ? 'trend-up' : 'trend-down';
    };

    // Calcular altura de barras para el gráfico
    const getBarHeight = (value, dataArray) => {
      if (!dataArray || dataArray.length === 0) return 0;
      const maxValue = Math.max(...dataArray);
      return maxValue > 0 ? (value / maxValue) * 100 : 0;
    };

    // Colores para el gráfico de torta
    const getPieColor = (index) => {
      const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
      return colors[index % colors.length];
    };

    // Fetch datos del dashboard - CORREGIDO
    const fetchDashboardData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        console.log(`🔄 Fetching dashboard data for period: ${selectedPeriod.value}`);
        
        const response = await fetch(`http://localhost:8000/usuarios/api/dashboard/?period=${selectedPeriod.value}`, {
          mode: 'cors',
          credentials: 'omit'
        });
        
        console.log(`📊 Response status: ${response.status}`);
        
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Dashboard data received successfully', data);
        
        // ✅ ASIGNAR DIRECTAMENTE los datos de la API
        dashboardData.value = data;
        
      } catch (err) {
        console.error('❌ Error fetching dashboard data:', err);
        error.value = `Error de conexión: ${err.message}`;
        
        // ❌ ELIMINADO: No usar datos de ejemplo
        // El dashboard mostrará el estado de error
        
      } finally {
        // ✅ CLAVE: Desactivar loading siempre
        loading.value = false;
      }
    };
    
    // Cambiar período
    const changePeriod = (period) => {
      selectedPeriod.value = period;
      fetchDashboardData();
    };

    // Watchers
    watch(selectedPeriod, fetchDashboardData);

    // Lifecycle
    onMounted(() => {
      observer.observe(document.body, { attributes: true });
      fetchDashboardData();
    });

    return {
      isLightModeReactive,
      selectedPeriod,
      periodOptions,
      loading,
      error,
      dashboardData,
      changePeriod,
      formatCurrency,
      getTrendClass,
      getBarHeight,
      getPieColor,
      fetchDashboardData
    };
  }
}
</script>

<style scoped>
/* ========================================
   🔥 DASHBOARD BARBERÍA ELEGANTE
   ======================================== */

/* CONTENEDOR PRINCIPAL */
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
  color: #e5e5e5;
  padding: 0;
}

/* HEADER */
.header {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  border-bottom: 4px solid #0ea5e9;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 30px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.title-section {
  flex: 1;
  min-width: 250px;
}

.main-title {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, #ffffff, #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 15px;
}

.scissors-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 10px rgba(14, 165, 233, 0.5));
}

.subtitle {
  color: #9ca3af;
  font-weight: 500;
  margin: 8px 0 0 0;
  letter-spacing: 0.8px;
  font-size: 0.95rem;
}

.period-buttons {
  display: flex;
  gap: 12px;
  background: rgba(0, 0, 0, 0.4);
  padding: 8px;
  border-radius: 16px;
  border: 1px solid rgba(100, 100, 100, 0.2);
}

.period-btn {
  background: transparent;
  color: #9ca3af;
  border: 2px solid transparent;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.period-btn:hover:not(:disabled) {
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.1);
}

.period-btn.active {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border-color: #0ea5e9;
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
}

.period-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* CONTAINER */
.container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 40px;
}

/* LOADING STATE */
.loading-container {
  text-align: center;
  padding: 100px 40px;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  margin: 0 auto 30px;
  border: 4px solid rgba(14, 165, 233, 0.2);
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #9ca3af;
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* ERROR STATE */
.error-container {
  text-align: center;
  padding: 100px 40px;
  background: rgba(239, 68, 68, 0.05);
  border-radius: 24px;
  border: 2px solid rgba(239, 68, 68, 0.3);
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 20px rgba(239, 68, 68, 0.5));
}

.error-title {
  color: #ef4444;
  font-size: 1.8rem;
  font-weight: 900;
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.error-message {
  color: #9ca3af;
  font-size: 1.1rem;
  margin-bottom: 30px;
}

.btn-retry {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.btn-retry:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(239, 68, 68, 0.6);
}

/* SECTIONS */
.section-title {
  font-size: 1.6rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 25px;
  background: linear-gradient(135deg, #ffffff, #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.section-kpis {
  margin-bottom: 40px;
}

/* KPI CARDS */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
}

.kpi-card {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6),
              0 0 0 1px rgba(100, 100, 100, 0.15) inset;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7);
}

.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 50px rgba(14, 165, 233, 0.3);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.kpi-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
}

.kpi-icon-gold {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.2));
  border: 2px solid rgba(245, 158, 11, 0.4);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}

.kpi-icon-silver {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(2, 132, 199, 0.2));
  border: 2px solid rgba(14, 165, 233, 0.4);
  box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);
}

.kpi-icon-new {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.2));
  border: 2px solid rgba(16, 185, 129, 0.4);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
}

.kpi-icon-product {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(124, 58, 237, 0.2));
  border: 2px solid rgba(139, 92, 246, 0.4);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 800;
  font-size: 0.8rem;
}

.trend-up {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.trend-down {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.kpi-badge {
  font-size: 1.4rem;
}

.kpi-label {
  color: #9ca3af;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
}

.kpi-value {
  font-size: 2.4rem;
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.kpi-meta {
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 600;
}

/* ALERT BOX */
.alert-box {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(245, 158, 11, 0.3);
}

.alert-warning::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.alert-content {
  display: flex;
  gap: 20px;
}

.alert-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.alert-body {
  flex: 1;
}

.alert-title {
  font-size: 1.3rem;
  font-weight: 900;
  color: #f59e0b;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.alert-badge {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.stock-item {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 12px;
  padding: 15px;
  transition: all 0.3s ease;
}

.stock-item:hover {
  border-color: #f59e0b;
  transform: translateX(5px);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.stock-name {
  font-weight: 800;
  color: #ffffff;
  font-size: 0.95rem;
}

.stock-icon {
  font-size: 1.2rem;
}

.stock-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.stock-category {
  color: #9ca3af;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stock-quantity {
  color: #ef4444;
  font-weight: 700;
  font-size: 0.85rem;
}

.stock-minimum {
  color: #6b7280;
  font-size: 0.8rem;
}

/* CHARTS SECTION */
.section-charts {
  margin-bottom: 40px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
}

.chart-card {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6),
              0 0 0 1px rgba(100, 100, 100, 0.15) inset;
  position: relative;
  overflow: hidden;
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7);
}

.large-card {
  grid-column: 1 / -1;
}

.chart-header {
  margin-bottom: 25px;
}

.chart-title {
  font-size: 1.2rem;
  font-weight: 900;
  color: #ffffff;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}

.chart-icon-gold {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.2));
  border: 2px solid rgba(245, 158, 11, 0.4);
}

.chart-icon-silver {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(2, 132, 199, 0.2));
  border: 2px solid rgba(14, 165, 233, 0.4);
}

.chart-icon-product {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(124, 58, 237, 0.2));
  border: 2px solid rgba(139, 92, 246, 0.4);
}

/* SERVICIOS LIST */
.servicios-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.servicio-item {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(100, 100, 100, 0.2);
  border-radius: 12px;
  padding: 18px;
  transition: all 0.3s ease;
}

.servicio-item:hover {
  border-color: #0ea5e9;
  transform: translateX(5px);
  background: rgba(14, 165, 233, 0.05);
}

.servicio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.servicio-name {
  font-weight: 800;
  color: #ffffff;
  font-size: 1rem;
}

.servicio-trend {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
}

.servicio-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.servicio-quantity {
  color: #9ca3af;
  font-size: 0.85rem;
}

.servicio-revenue {
  color: #10b981;
  font-weight: 800;
  font-size: 1.1rem;
}

/* PELUQUEROS LIST */
.peluqueros-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.peluquero-item {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(100, 100, 100, 0.2);
  border-radius: 12px;
  padding: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.peluquero-item:hover {
  border-color: #0ea5e9;
  transform: translateX(5px);
  background: rgba(14, 165, 233, 0.05);
}

.peluquero-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.peluquero-rank {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.2rem;
  color: white;
}

.peluquero-name {
  font-weight: 800;
  color: #ffffff;
  font-size: 1rem;
  margin-bottom: 4px;
}

.peluquero-services {
  color: #9ca3af;
  font-size: 0.85rem;
}

.peluquero-revenue {
  text-align: right;
}

.revenue-amount {
  color: #10b981;
  font-weight: 900;
  font-size: 1.3rem;
  margin-bottom: 4px;
}

.revenue-label {
  color: #6b7280;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 1px;
}

/* PRODUCTS SECTION */
.section-products {
  margin-bottom: 40px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.product-card {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(100, 100, 100, 0.2);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  position: relative;
  transition: all 0.3s ease;
}

.product-card:hover {
  border-color: #8b5cf6;
  transform: translateY(-5px);
  background: rgba(139, 92, 246, 0.05);
}

.product-rank {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 0.9rem;
  color: white;
}

.product-name {
  font-weight: 800;
  color: #ffffff;
  font-size: 1rem;
  margin-bottom: 10px;
}

.product-units {
  color: #9ca3af;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.product-revenue {
  color: #8b5cf6;
  font-weight: 900;
  font-size: 1.2rem;
}

/* ANALYTICS SECTION */
.section-analytics {
  margin-bottom: 40px;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 25px;
}

/* SIMPLE CHART - Bar Chart */
.simple-chart {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 250px;
  padding: 20px 10px;
}

.bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
}

.bar-track {
  flex: 1;
  width: 100%;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 8px;
  position: relative;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #0ea5e9, #0284c7);
  border-radius: 8px 8px 0 0;
  position: relative;
  transition: height 0.5s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  box-shadow: 0 -4px 15px rgba(14, 165, 233, 0.4);
}

.bar-value {
  color: white;
  font-size: 0.7rem;
  font-weight: 800;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
}

/* PIE CHART SIMPLE */
.pie-chart-simple {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 10px;
}

.pie-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.pie-item:hover {
  background: rgba(0, 0, 0, 0.6);
  transform: translateX(5px);
}

.pie-color {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  flex-shrink: 0;
  box-shadow: 0 0 10px currentColor;
}

.pie-label {
  flex: 1;
  color: #e5e5e5;
  font-weight: 700;
  font-size: 0.9rem;
}

.pie-value {
  color: #0ea5e9;
  font-weight: 900;
  font-size: 1.1rem;
}

/* RESPONSIVE */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 20px;
  }
  
  .header-content {
    padding: 20px;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .main-title {
    font-size: 1.6rem;
  }
  
  .period-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .period-btn {
    flex: 1;
    padding: 10px;
    font-size: 0.75rem;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .stock-grid {
    grid-template-columns: 1fr;
  }
  
  .alert-content {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }
  
  .header-content {
    padding: 15px;
  }
  
  .main-title {
    font-size: 1.3rem;
  }
  
  .kpi-card {
    padding: 20px;
  }
  
  .kpi-value {
    font-size: 2rem;
  }
  
  .chart-card {
    padding: 20px;
  }
  
  .simple-chart {
    height: 200px;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
}

/* LIGHT MODE SUPPORT (opcional) */
.light-mode .dashboard-container {
  background: linear-gradient(145deg, #f3f4f6, #e5e7eb);
  color: #1f2937;
}

.light-mode .kpi-card,
.light-mode .chart-card,
.light-mode .alert-box {
  background: linear-gradient(145deg, #ffffff, #f9fafb);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.light-mode .header {
  background: linear-gradient(145deg, #ffffff, #f9fafb);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}
</style>