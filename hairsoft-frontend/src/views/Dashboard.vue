<template>
  <div class="dashboard-wrapper">
    <!-- Header Premium -->
    <header class="dashboard-header">
      <div class="header-container">
        <div class="header-left">
          <h1 class="dashboard-title">
            <span class="title-icon">📊</span>
            Dashboard
          </h1>
          <div class="period-selector">
            <select v-model="selectedPeriod" @change="fetchDashboardData" class="period-select">
              <option value="hoy">Hoy</option>
              <option value="semana">Esta semana</option>
              <option value="mes">Este mes</option>
            </select>
          </div>
        </div>
        <div class="header-right">
          <div class="last-update">
            <span class="update-icon">🕐</span>
            {{ lastUpdate }}
          </div>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">Cargando datos del dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3 class="error-title">Error al cargar datos</h3>
      <p class="error-message">{{ error }}</p>
      <button @click="fetchDashboardData" class="retry-btn">
        <span>🔄</span>
        Reintentar
      </button>
    </div>

    <!-- Main Content -->
    <main v-else class="dashboard-content">
      
      <!-- KPI Cards -->
      <section class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon-wrapper green">
              <span class="kpi-icon">💰</span>
            </div>
            <div class="kpi-trend" :class="dashboardData.ventasTrend >= 0 ? 'positive' : 'negative'">
              <span class="trend-arrow">{{ dashboardData.ventasTrend >= 0 ? '↗' : '↘' }}</span>
              <span class="trend-value">{{ Math.abs(dashboardData.ventasTrend) }}%</span>
            </div>
          </div>
          <div class="kpi-body">
            <h3 class="kpi-value">${{ formatNumber(dashboardData.ingresosTotales) }}</h3>
            <p class="kpi-label">Ingresos Totales</p>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon-wrapper blue">
              <span class="kpi-icon">✂️</span>
            </div>
            <div class="kpi-badge">⚡ Hot</div>
          </div>
          <div class="kpi-body">
            <h3 class="kpi-value">{{ dashboardData.serviciosRealizados }}</h3>
            <p class="kpi-label">Servicios Realizados</p>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon-wrapper purple">
              <span class="kpi-icon">👥</span>
            </div>
            <div class="kpi-badge">✨ New</div>
          </div>
          <div class="kpi-body">
            <h3 class="kpi-value">{{ dashboardData.clientesNuevos }}</h3>
            <p class="kpi-label">Clientes Nuevos</p>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon-wrapper orange">
              <span class="kpi-icon">🎫</span>
            </div>
            <div class="kpi-trend positive">
              <span class="trend-arrow">↗</span>
              <span class="trend-value">0%</span>
            </div>
          </div>
          <div class="kpi-body">
            <h3 class="kpi-value">${{ formatNumber(dashboardData.ticketPromedio) }}</h3>
            <p class="kpi-label">Ticket Promedio</p>
          </div>
        </div>
      </section>

      <!-- Content Grid -->
      <div class="content-layout">
        
        <!-- Left Column -->
        <div class="content-left">
          
          <!-- Servicios Populares Card -->
          <div class="info-card">
            <div class="card-header">
              <div class="card-title-group">
                <span class="card-icon">🔥</span>
                <h3 class="card-title">Servicios Más Solicitados</h3>
              </div>
              <span class="card-badge">Top 5</span>
            </div>
            <div class="card-body">
              <div class="service-list">
                <div 
                  v-for="(servicio, index) in dashboardData.serviciosTop" 
                  :key="servicio.nombre"
                  class="service-row"
                >
                  <div class="service-rank">{{ index + 1 }}</div>
                  <div class="service-details">
                    <span class="service-name">{{ servicio.nombre }}</span>
                    <span class="service-meta">{{ servicio.cantidad }} servicios</span>
                  </div>
                  <div class="service-amount">${{ formatNumber(servicio.ingresos) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Stats Card -->
          <div class="info-card">
            <div class="card-header">
              <div class="card-title-group">
                <span class="card-icon">📦</span>
                <h3 class="card-title">Resumen de Ventas</h3>
              </div>
            </div>
            <div class="card-body">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-icon">📊</div>
                  <div class="stat-info">
                    <span class="stat-value">{{ dashboardData.productosVendidos }}</span>
                    <span class="stat-label">Productos Vendidos</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon">👤</div>
                  <div class="stat-info">
                    <span class="stat-value">{{ dashboardData.totalClientes }}</span>
                    <span class="stat-label">Total Clientes</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon">🎯</div>
                  <div class="stat-info">
                    <span class="stat-value">${{ formatNumber(dashboardData.metaMensual) }}</span>
                    <span class="stat-label">Meta Mensual</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="content-right">
          
          <!-- Chart Card -->
          <div class="info-card chart-card">
            <div class="card-header">
              <div class="card-title-group">
                <span class="card-icon">📈</span>
                <h3 class="card-title">Ventas de la Semana</h3>
              </div>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <div 
                  v-for="(venta, index) in dashboardData.ventasPorDia" 
                  :key="index"
                  class="chart-column"
                >
                  <div 
                    class="chart-bar" 
                    :style="{ height: getBarHeight(venta) + '%' }"
                    :data-value="'$' + formatNumber(venta)"
                  >
                    <div class="bar-tooltip">${{ formatNumber(venta) }}</div>
                  </div>
                  <div class="chart-label">{{ dashboardData.labelsDias[index] }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Alert Card -->
          <div v-if="dashboardData.stockBajoCount > 0" class="info-card alert-card">
            <div class="card-header">
              <div class="card-title-group">
                <span class="card-icon">⚠️</span>
                <h3 class="card-title">Alertas de Inventario</h3>
              </div>
              <span class="alert-count">{{ dashboardData.stockBajoCount }}</span>
            </div>
            <div class="card-body">
              <div class="alert-content">
                <div class="alert-icon-large">📦</div>
                <p class="alert-text">
                  <strong>{{ dashboardData.stockBajoCount }} productos</strong> tienen stock bajo
                </p>
                <button class="alert-action-btn">Ver Productos</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'ModernDashboard',
  setup() {
    const selectedPeriod = ref('semana')
    const loading = ref(true)
    const error = ref(null)
    const dashboardData = ref({})
    const lastUpdate = ref('')

    const defaultData = {
      ingresosTotales: 0,
      serviciosRealizados: 0,
      clientesNuevos: 0,
      productosVendidos: 0,
      ticketPromedio: 0,
      ventasTrend: 0,
      metaMensual: 0,
      totalClientes: 0,
      stockBajoCount: 0,
      stockBajo: [],
      serviciosTop: [],
      topPeluqueros: [],
      productosTop: [],
      ventasPorDia: [],
      serviciosDistribucion: [],
      labelsDias: []
    }

    const fetchDashboardData = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await fetch(
          `http://localhost:8000/usuarios/api/dashboard/?period=${selectedPeriod.value}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        )
        
        if (!response.ok) {
          throw new Error(`HTTP Error: ${response.status}`)
        }

        const data = await response.json()
        dashboardData.value = { ...defaultData, ...data }
        lastUpdate.value = new Date().toLocaleTimeString('es-ES', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
        
      } catch (err) {
        error.value = `Error de conexión: ${err.message}`
        dashboardData.value = defaultData
      } finally {
        loading.value = false
      }
    }

    const formatNumber = (num) => {
      if (!num && num !== 0) return '0'
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k'
      }
      return num.toLocaleString('es-ES')
    }

    const getBarHeight = (value) => {
      const maxValue = Math.max(...dashboardData.value.ventasPorDia)
      return maxValue > 0 ? (value / maxValue) * 100 : 0
    }

    onMounted(() => {
      fetchDashboardData()
    })

    return {
      selectedPeriod,
      loading,
      error,
      dashboardData,
      lastUpdate,
      fetchDashboardData,
      formatNumber,
      getBarHeight
    }
  }
}
</script>

<style scoped>
.dashboard-wrapper {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* ========== HEADER ========== */
.dashboard-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 24px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.dashboard-title {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
}

.period-selector {
  position: relative;
}

.period-select {
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  color: var(--text-primary);
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.period-select:hover {
  border-color: var(--accent-color);
}

.period-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.last-update {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.update-icon {
  font-size: 16px;
}

/* ========== LOADING & ERROR ========== */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 20px;
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: 500;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.error-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.error-message {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.retry-btn {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* ========== MAIN CONTENT ========== */
.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
}

/* ========== KPI CARDS ========== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.kpi-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-color);
  box-shadow: var(--shadow-lg);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.kpi-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.kpi-icon-wrapper.green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.kpi-icon-wrapper.blue {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.kpi-icon-wrapper.purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.kpi-icon-wrapper.orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
}

.kpi-trend.positive {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color);
}

.kpi-trend.negative {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error-color);
}

.kpi-badge {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  background: var(--accent-light);
  color: var(--accent-color);
}

.kpi-body {
  margin-top: 12px;
}

.kpi-value {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -1px;
}

.kpi-label {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  margin: 0;
}

/* ========== CONTENT LAYOUT ========== */
.content-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.content-left,
.content-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ========== INFO CARDS ========== */
.info-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.info-card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-md);
}

.alert-card {
  border-color: var(--warning-color);
}

.card-header {
  padding: 20px 24px;
  border-bottom: 2px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-icon {
  font-size: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.card-badge {
  padding: 6px 12px;
  background: var(--accent-light);
  color: var(--accent-color);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
}

.alert-count {
  background: var(--warning-color);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.card-body {
  padding: 24px;
}

/* ========== SERVICE LIST ========== */
.service-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.service-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.service-row:hover {
  border-color: var(--accent-color);
  transform: translateX(4px);
}

.service-rank {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-hover));
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  flex-shrink: 0;
}

.service-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.service-name {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 15px;
}

.service-meta {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.service-amount {
  font-size: 18px;
  font-weight: 800;
  color: var(--accent-color);
}

/* ========== STATS GRID ========== */
.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  border-color: var(--accent-color);
  transform: scale(1.02);
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
}

/* ========== CHART ========== */
.chart-card {
  min-height: 400px;
}

.chart-container {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  height: 280px;
  padding: 20px 0;
}

.chart-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.chart-bar {
  width: 100%;
  background: linear-gradient(to top, var(--accent-color), var(--accent-hover));
  border-radius: 8px 8px 0 0;
  min-height: 40px;
  position: relative;
  transition: all 0.3s ease;
  cursor: pointer;
}

.chart-bar:hover {
  transform: scaleY(1.05);
  box-shadow: 0 -4px 12px rgba(59, 130, 246, 0.3);
}

.bar-tooltip {
  position: absolute;
  top: -32px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-secondary);
  border: 2px solid var(--accent-color);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.chart-bar:hover .bar-tooltip {
  opacity: 1;
}

.chart-label {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}

/* ========== ALERT CONTENT ========== */
.alert-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
  padding: 20px;
}

.alert-icon-large {
  font-size: 48px;
}

.alert-text {
  color: var(--text-secondary);
  font-size: 15px;
  margin: 0;
}

.alert-action-btn {
  background: var(--warning-color);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alert-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* ========== RESPONSIVE ========== */
@media (max-width: 1200px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    padding: 20px;
  }
  
  .header-container {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .dashboard-content {
    padding: 20px;
  }
  
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .kpi-value {
    font-size: 28px;
  }
}

@media (max-width: 480px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-title {
    font-size: 24px;
  }
  
  .chart-container {
    height: 200px;
  }
}
</style>