<template>
  <div class="dashboard-wrapper">
    <!-- Header Premium -->
    <header class="dashboard-header">
      <div class="header-container">
        <div class="header-left">
          <div class="header-icon-wrapper">
            <span class="header-icon">📊</span>
          </div>
          <div class="header-info">
            <h1 class="dashboard-title">Dashboard</h1>
            <p class="dashboard-subtitle">Análisis en tiempo real</p>
          </div>
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
            <span class="update-time">{{ lastUpdate }}</span>
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
        <!-- Ingresos Totales -->
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

        <!-- Servicios Realizados -->
        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon-wrapper blue">
              <span class="kpi-icon">✂️</span>
            </div>
            <div class="kpi-badge hot">⚡ Hot</div>
          </div>
          <div class="kpi-body">
            <h3 class="kpi-value">{{ formatNumber(dashboardData.serviciosRealizados) }}</h3>
            <p class="kpi-label">Servicios Realizados</p>
          </div>
        </div>

        <!-- Clientes Nuevos -->
        <div class="kpi-card">
          <div class="kpi-header">
            <div class="kpi-icon-wrapper accent">
              <span class="kpi-icon">👥</span>
            </div>
            <div class="kpi-badge new">✨ New</div>
          </div>
          <div class="kpi-body">
            <h3 class="kpi-value">{{ formatNumber(dashboardData.clientesNuevos) }}</h3>
            <p class="kpi-label">Clientes Nuevos</p>
          </div>
        </div>

        <!-- Ticket Promedio -->
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
                <div class="card-icon-wrapper">
                  <span class="card-icon">🔥</span>
                </div>
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
                <div class="card-icon-wrapper">
                  <span class="card-icon">📦</span>
                </div>
                <h3 class="card-title">Resumen de Ventas</h3>
              </div>
            </div>
            <div class="card-body">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-icon">📊</div>
                  <div class="stat-info">
                    <span class="stat-value">{{ formatNumber(dashboardData.productosVendidos) }}</span>
                    <span class="stat-label">Productos Vendidos</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon">👤</div>
                  <div class="stat-info">
                    <span class="stat-value">{{ formatNumber(dashboardData.totalClientes) }}</span>
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
                <div class="card-icon-wrapper">
                  <span class="card-icon">📈</span>
                </div>
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
                <div class="card-icon-wrapper alert">
                  <span class="card-icon">⚠️</span>
                </div>
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
        
        const now = new Date()
        lastUpdate.value = now.toLocaleTimeString('es-ES', { 
          hour: '2-digit', 
          minute: '2-digit',
          second: '2-digit'
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
/* ========== VARIABLES BASE ========== */
.dashboard-wrapper {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* ========== HEADER PREMIUM ========== */
.dashboard-header {
  background: var(--bg-secondary);
  border-bottom: 3px solid var(--border-color);
  padding: 24px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-md);
}

.dashboard-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1);
}

.header-container {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.header-icon-wrapper {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  border: 2px solid var(--border-color);
}

.header-icon {
  font-size: 28px;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.dashboard-title {
  font-size: 28px;
  font-weight: 900;
  margin: 0;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.dashboard-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  margin: 4px 0 0 0;
  letter-spacing: 0.5px;
}

.period-selector {
  position: relative;
}

.period-select {
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  color: var(--text-primary);
  padding: 12px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.period-select:hover {
  border-color: var(--accent-color);
  background: var(--hover-bg);
}

.period-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
}

.last-update {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-tertiary);
  padding: 10px 18px;
  border-radius: 12px;
  border: 2px solid var(--border-color);
}

.update-icon {
  font-size: 18px;
}

.update-time {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-family: 'Courier New', monospace;
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
  width: 60px;
  height: 60px;
  border: 5px solid var(--border-color);
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 24px;
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.error-icon {
  font-size: 72px;
  margin-bottom: 20px;
}

.error-title {
  font-size: 28px;
  font-weight: 900;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.error-message {
  color: var(--text-secondary);
  margin-bottom: 28px;
  font-weight: 500;
  font-size: 15px;
}

.retry-btn {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
}

.retry-btn:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
}

/* ========== MAIN CONTENT ========== */
.dashboard-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 32px;
}

/* ========== KPI CARDS ========== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.kpi-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 20px;
  padding: 28px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1);
  border-radius: 20px 20px 0 0;
}

.kpi-card:hover {
  transform: translateY(-6px);
  border-color: var(--accent-color);
  box-shadow: var(--shadow-lg);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.kpi-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  border: 2px solid var(--border-color);
}

.kpi-icon-wrapper.green {
  background: linear-gradient(135deg, #10b981, #059669);
}

.kpi-icon-wrapper.blue {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
}

.kpi-icon-wrapper.accent {
  background: linear-gradient(135deg, #0ea5e9, #0369a1);
}

.kpi-icon-wrapper.orange {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border: 2px solid;
}

.kpi-trend.positive {
  background: var(--bg-tertiary);
  color: #10b981;
  border-color: #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.kpi-trend.negative {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border-color: var(--error-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
}

.kpi-badge {
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  border: 2px solid;
}

.kpi-badge.hot {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border-color: #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.kpi-badge.new {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border-color: #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.kpi-body {
  margin-top: 16px;
}

.kpi-value {
  font-size: 42px;
  font-weight: 900;
  color: var(--text-primary);
  margin: 0 0 10px 0;
  letter-spacing: -1.5px;
}

.kpi-label {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
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
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
}

.info-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1);
  border-radius: 20px 20px 0 0;
}

.info-card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-md);
}

.alert-card {
  border-color: var(--warning-color);
}

.alert-card::before {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.card-header {
  padding: 24px 28px;
  border-bottom: 2px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--hover-bg);
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.card-icon-wrapper {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-color);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.card-icon-wrapper.alert {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.card-icon {
  font-size: 22px;
}

.card-title {
  font-size: 18px;
  font-weight: 900;
  color: var(--text-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.card-badge {
  padding: 8px 16px;
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.alert-count {
  background: var(--warning-color);
  color: white;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.card-body {
  padding: 28px;
}

/* ========== SERVICE LIST ========== */
.service-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.service-row {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.service-row:hover {
  border-color: var(--accent-color);
  transform: translateX(6px);
  box-shadow: var(--shadow-sm);
}

.service-rank {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 15px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
  border: 2px solid var(--border-color);
}

.service-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.service-name {
  font-weight: 800;
  color: var(--text-primary);
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.service-meta {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.3px;
}

.service-amount {
  font-size: 20px;
  font-weight: 900;
  color: #0ea5e9;
  letter-spacing: -0.5px;
}

/* ========== STATS GRID ========== */
.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  border-color: var(--accent-color);
  transform: scale(1.03);
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-value {
  font-size: 26px;
  font-weight: 900;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* ========== CHART ========== */
.chart-card {
  min-height: 450px;
}

.chart-container {
  display: flex;
  align-items: flex-end;
  gap: 18px;
  height: 300px;
  padding: 24px 0;
}

.chart-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.chart-bar {
  width: 100%;
  background: linear-gradient(to top, #0ea5e9, #0284c7);
  border-radius: 10px 10px 0 0;
  min-height: 50px;
  position: relative;
  transition: all 0.4s ease;
  cursor: pointer;
  border: 2px solid var(--border-color);
  border-bottom: none;
  box-shadow: 0 -4px 12px rgba(14, 165, 233, 0.3);
}

.chart-bar:hover {
  transform: scaleY(1.08);
  box-shadow: 0 -8px 20px rgba(14, 165, 233, 0.5);
  background: linear-gradient(to top, #0284c7, #0369a1);
}

.bar-tooltip {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-secondary);
  border: 2px solid #0ea5e9;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 800;
  color: var(--text-primary);
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  box-shadow: var(--shadow-md);
  letter-spacing: 0.5px;
}

.chart-bar:hover .bar-tooltip {
  opacity: 1;
}

.chart-label {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 700;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ========== ALERT CONTENT ========== */
.alert-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 20px;
  padding: 24px;
}

.alert-icon-large {
  font-size: 56px;
}

.alert-text {
  color: var(--text-secondary);
  font-size: 15px;
  margin: 0;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.alert-text strong {
  color: var(--text-primary);
  font-weight: 800;
}

.alert-action-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35);
}

.alert-action-btn:hover {
  background: linear-gradient(135deg, #d97706, #b45309);
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(245, 158, 11, 0.5);
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
  
  .header-left {
    flex-wrap: wrap;
  }
  
  .dashboard-content {
    padding: 20px;
  }
  
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .kpi-value {
    font-size: 32px;
  }
  
  .chart-container {
    height: 220px;
  }
}

@media (max-width: 480px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-title {
    font-size: 22px;
  }
  
  .header-icon-wrapper {
    width: 48px;
    height: 48px;
  }
  
  .header-icon {
    font-size: 24px;
  }
  
  .chart-container {
    height: 180px;
  }
}
</style>