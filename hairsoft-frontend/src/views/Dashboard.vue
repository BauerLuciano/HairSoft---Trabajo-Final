<template>
  <div class="dashboard-wrapper">
    
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">Dashboard - Reporte Comercial</h1>
        <p class="dashboard-subtitle">Análisis integral de ventas y servicios</p>
      </div>
      
      <div class="header-right">
        <!-- Selector de período predefinido -->
        <div class="period-selector">
          <button 
            v-for="p in periods" 
            :key="p.value"
            :class="{ active: selectedPeriod === p.value && !customDateRange }"
            @click="selectPeriod(p.value)"
          >
            <i :class="p.icon"></i>
            {{ p.label }}
          </button>
          <button 
            :class="{ active: customDateRange }"
            @click="toggleCustomRange"
          >
            <i class="fas fa-calendar-alt"></i>
            Personalizado
          </button>
        </div>

        <!-- Indicador del período activo -->
        <div class="period-display">
          <i class="fas fa-calendar-check"></i>
          <span>{{ getPeriodDisplay }}</span>
        </div>

        <!-- Botón de generar PDF -->
        <button @click="generatePDF" class="pdf-btn" :disabled="loading">
          <i class="fas fa-file-pdf"></i>
          Exportar Reporte Completo
        </button>
      </div>
    </header>

    <!-- Panel de fechas personalizadas -->
    <Transition name="slide-down">
      <div v-if="customDateRange" class="custom-date-panel">
        <div class="date-inputs">
          <div class="date-input-group">
            <label>
              <i class="fas fa-calendar-day"></i>
              Fecha Desde
            </label>
            <input 
              type="date" 
              v-model="dateFrom" 
              :max="dateTo || today"
            />
          </div>
          <div class="date-input-group">
            <label>
              <i class="fas fa-calendar-day"></i>
              Fecha Hasta
            </label>
            <input 
              type="date" 
              v-model="dateTo" 
              :min="dateFrom"
              :max="today"
            />
          </div>
          <button @click="applyCustomRange" class="apply-btn">
            <i class="fas fa-check"></i>
            Aplicar
          </button>
        </div>
        <div class="date-range-info" v-if="dateFrom && dateTo">
          <i class="fas fa-info-circle"></i>
          Mostrando datos desde <strong>{{ formatDate(dateFrom) }}</strong> hasta <strong>{{ formatDate(dateTo) }}</strong>
        </div>
      </div>
    </Transition>

    <div v-if="loading" class="state-container">
      <div class="loader"></div>
      <p class="loading-text">Generando reporte...</p>
    </div>

    <div v-else-if="error" class="state-container error">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error de Conexión</h3>
        <p>{{ error }}</p>
        <button @click="fetchDashboardData" class="retry-btn">
          <i class="fas fa-redo"></i>
          Reintentar
        </button>
      </div>
    </div>

    <main v-else class="dashboard-content fade-in" ref="dashboardContent">
      
      <!-- 📊 RESÚMEN DEL PERÍODO -->
      <div class="period-summary-card">
        <div class="summary-header">
          <h3><i class="fas fa-chart-bar"></i> Resumen del Período</h3>
          <div class="period-tag">
            <i class="fas fa-clock"></i>
            {{ getPeriodDisplay }}
          </div>
        </div>
        <div class="summary-stats">
          <div class="summary-stat">
            <div class="stat-label">Días Analizados</div>
            <div class="stat-value">{{ dashboardData.ventasPorDia.length }}</div>
          </div>
          <div class="summary-stat">
            <div class="stat-label">Venta Promedio/Día</div>
            <div class="stat-value">${{ formatNumber(calculateAverageDaily()) }}</div>
          </div>
          <div class="summary-stat">
            <div class="stat-label">Día Pico</div>
            <div class="stat-value">{{ getPeakDay() }}</div>
          </div>
          <div class="summary-stat">
            <div class="stat-label">Total Transacciones</div>
            <div class="stat-value">{{ dashboardData.productosVendidos + dashboardData.serviciosRealizados }}</div>
          </div>
        </div>
      </div>

      <!-- 💎 KPI CARDS -->
      <div class="kpi-grid">
        
        <div class="kpi-card income">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-dollar-sign"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Ingresos Totales</span>
            <span class="value">${{ formatNumber(dashboardData.ingresosTotales) }}</span>
            <span class="subtitle">Facturación del período</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline
                points="0,18 20,15 40,10 60,12 80,6 100,4"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              />
            </svg>
          </div>
        </div>

        <div class="kpi-card service">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-cut"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Servicios Completados</span>
            <span class="value">{{ dashboardData.serviciosRealizados }}</span>
            <span class="subtitle">Turnos atendidos</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline
                points="0,20 20,16 40,18 60,13 80,10 100,8"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              />
            </svg>
          </div>
        </div>

        <div class="kpi-card product">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-shopping-bag"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Productos Vendidos</span>
            <span class="value">{{ dashboardData.productosVendidos }}</span>
            <span class="subtitle">Unidades despachadas</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline
                points="0,14 20,12 40,9 60,11 80,5 100,3"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              />
            </svg>
          </div>
        </div>

        <div class="kpi-card clients">
          <div class="kpi-header-card">
            <div class="kpi-icon"><i class="fas fa-users"></i></div>
          </div>
          <div class="kpi-data">
            <span class="label">Clientes Atendidos</span>
            <span class="value">{{ dashboardData.clientesAtendidos || calcularClientes() }}</span>
            <span class="subtitle">Personas atendidas</span>
          </div>
          <div class="kpi-sparkline">
            <svg viewBox="0 0 100 24" preserveAspectRatio="none">
              <polyline
                points="0,16 20,14 40,12 60,15 80,10 100,8"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              />
            </svg>
          </div>
        </div>

      </div>

      <!-- 🔥 SECCIÓN DE GRÁFICOS -->
      <div class="charts-grid">
        
        <!-- GRÁFICO PRINCIPAL -->
        <div class="section-card chart-section main-chart">
          <div class="section-header">
            <h3>
              <i class="fas fa-chart-line"></i> 
              Evolución de Ingresos Diarios
            </h3>
            <div class="chart-info">
              <span class="chart-legend">
                <i class="fas fa-circle" style="color: #3b82f6"></i>
                Ingresos por día
              </span>
            </div>
          </div>
          <div class="chart-body">
            <div v-if="dashboardData.ventasPorDia.length" class="trading-chart-container">
              
              <!-- Grid mejorado -->
              <svg class="chart-grid" :viewBox="`0 0 ${chartWidth} ${chartHeight}`">
                <!-- Líneas horizontales de referencia -->
                <g v-for="i in 5" :key="`ref-${i}`">
                  <line 
                    :x1="60" :y1="(chartHeight / 5) * i"
                    :x2="chartWidth - 20" :y2="(chartHeight / 5) * i"
                    stroke="#334155" stroke-width="1" stroke-dasharray="5,5" opacity="0.4"/>
                  <!-- Labels de valores -->
                  <text 
                    :x="10" 
                    :y="(chartHeight / 5) * i + 5"
                    fill="#64748b"
                    font-size="11"
                    font-weight="600"
                    font-family="system-ui, -apple-system, sans-serif"
                  >
                    ${{ formatNumberShort(Math.round((getMaxValue() / 5) * (5 - i))) }}
                  </text>
                </g>
              </svg>

              <!-- Gráfico SVG -->
              <svg class="chart-svg" :viewBox="`0 0 ${chartWidth} ${chartHeight}`">
                <defs>
                  <!-- Gradiente del área -->
                  <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.5" />
                    <stop offset="50%" style="stop-color:#3b82f6;stop-opacity:0.2" />
                    <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0" />
                  </linearGradient>
                  
                  <!-- Glow para la línea -->
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>

                  <!-- Gradiente de línea -->
                  <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#3b82f6" />
                    <stop offset="50%" style="stop-color:#60a5fa" />
                    <stop offset="100%" style="stop-color:#3b82f6" />
                  </linearGradient>
                </defs>

                <!-- Área rellena -->
                <path 
                  :d="getAreaPath()" 
                  fill="url(#areaGradient)" 
                  class="chart-area"
                />

                <!-- Sombra de la línea -->
                <path 
                  :d="getLinePath()" 
                  fill="none" 
                  stroke="#3b82f6" 
                  stroke-width="5" 
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  opacity="0.15"
                  filter="blur(8px)"
                />

                <!-- Línea principal -->
                <path 
                  :d="getLinePath()" 
                  fill="none" 
                  stroke="url(#lineGradient)" 
                  stroke-width="3" 
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="chart-line"
                  filter="url(#glow)"
                />

                <!-- Línea de promedio -->
                <line 
                  :x1="padding" 
                  :y1="getYPosition(calculateAverageDaily())"
                  :x2="chartWidth - padding" 
                  :y2="getYPosition(calculateAverageDaily())"
                  stroke="#10b981"
                  stroke-width="2"
                  stroke-dasharray="8,4"
                  opacity="0.6"
                />

                <!-- Puntos interactivos -->
                <g v-for="(monto, i) in dashboardData.ventasPorDia" :key="`point-${i}`">
                  <!-- Punto especial para el día pico -->
                  <circle 
                    v-if="monto === Math.max(...dashboardData.ventasPorDia)"
                    :cx="getXPosition(i)" 
                    :cy="getYPosition(monto)"
                    r="8"
                    fill="#ef4444"
                    stroke="#ffffff"
                    stroke-width="2"
                    class="peak-point"
                  />
                  
                  <!-- Glow exterior -->
                  <circle 
                    :cx="getXPosition(i)" 
                    :cy="getYPosition(monto)"
                    r="12"
                    fill="#3b82f6"
                    opacity="0.12"
                    class="point-glow"
                    :class="{ active: hoveredPoint === i }"
                  />
                  <!-- Círculo principal -->
                  <circle 
                    :cx="getXPosition(i)" 
                    :cy="getYPosition(monto)"
                    r="6"
                    fill="#0f172a"
                    stroke="#3b82f6"
                    stroke-width="2.5"
                    class="chart-point"
                    :class="{ active: hoveredPoint === i }"
                    @mouseenter="showTooltip(i, monto, $event)"
                    @mouseleave="hideTooltip"
                  />
                  <!-- Centro brillante -->
                  <circle 
                    :cx="getXPosition(i)" 
                    :cy="getYPosition(monto)"
                    r="2"
                    fill="#60a5fa"
                    class="point-center"
                    :class="{ active: hoveredPoint === i }"
                  />
                </g>
              </svg>

              <!-- Labels de días -->
              <div class="chart-labels">
                <span 
                  v-for="(label, i) in dashboardData.labelsDias" 
                  :key="`label-${i}`"
                  class="day-label"
                  :class="{ active: hoveredPoint === i, peak: dashboardData.ventasPorDia[i] === Math.max(...dashboardData.ventasPorDia) }"
                  :style="{ left: getXPositionPercent(i) + '%' }"
                >
                  {{ label }}
                  <span v-if="dashboardData.ventasPorDia[i] === Math.max(...dashboardData.ventasPorDia)" class="peak-badge">
                    <i class="fas fa-fire"></i>
                  </span>
                </span>
              </div>

              <!-- Tooltip -->
              <Transition name="tooltip">
                <div 
                  v-if="tooltip.visible" 
                  class="chart-tooltip"
                  :style="{ 
                    left: tooltip.x + 'px', 
                    top: tooltip.y + 'px' 
                  }"
                >
                  <div class="tooltip-header">
                    <i class="fas fa-calendar-day"></i>
                    {{ tooltip.date }}
                    <span v-if="tooltip.value === Math.max(...dashboardData.ventasPorDia)" class="tooltip-badge">
                      <i class="fas fa-crown"></i> DÍA PICO
                    </span>
                  </div>
                  <div class="tooltip-body">
                    <div class="tooltip-value">${{ formatNumber(tooltip.value) }}</div>
                    <div class="tooltip-label">Ingresos del día</div>
                    <div class="tooltip-comparison" :class="getComparisonClass(tooltip.value)">
                      <i :class="getComparisonIcon(tooltip.value)"></i>
                      {{ getComparisonText(tooltip.value) }}
                    </div>
                  </div>
                </div>
              </Transition>
            </div>

            <div v-else class="no-data">
              <i class="fas fa-chart-line"></i>
              <p>No hay ventas registradas en este período</p>
            </div>
          </div>
        </div>

        <!-- GRÁFICO DE DISTRIBUCIÓN -->
        <div class="section-card distribution-card">
          <div class="section-header">
            <h3><i class="fas fa-chart-pie"></i> Distribución por Tipo</h3>
          </div>
          <div class="distribution-body">
            <div class="distribution-chart">
              <svg width="200" height="200" viewBox="0 0 200 200">
                <defs>
                  <linearGradient id="pieGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" />
                  </linearGradient>
                  <linearGradient id="pieGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#047857;stop-opacity:1" />
                  </linearGradient>
                </defs>
                
                <circle cx="100" cy="100" r="80" fill="transparent" stroke="#334155" stroke-width="2"/>
                
                <!-- Sector Servicios -->
                <path 
                  :d="getPiePath(0, getServicePercentage())" 
                  fill="url(#pieGradient2)"
                  class="pie-sector"
                />
                
                <!-- Sector Productos -->
                <path 
                  :d="getPiePath(getServicePercentage(), 100)" 
                  fill="url(#pieGradient1)"
                  class="pie-sector"
                />
                
                <circle cx="100" cy="100" r="40" fill="#1e293b"/>
                
                <text x="100" y="95" text-anchor="middle" fill="#f1f5f9" font-size="18" font-weight="700">
                  {{ getTotalTransactions() }}
                </text>
                <text x="100" y="115" text-anchor="middle" fill="#94a3b8" font-size="12">
                  Total
                </text>
              </svg>
            </div>
            <div class="distribution-legend">
              <div class="legend-item">
                <div class="legend-color service"></div>
                <div class="legend-content">
                  <span class="legend-label">Servicios</span>
                  <span class="legend-value">{{ dashboardData.serviciosRealizados }} ({{ getServicePercentage().toFixed(1) }}%)</span>
                </div>
              </div>
              <div class="legend-item">
                <div class="legend-color product"></div>
                <div class="legend-content">
                  <span class="legend-label">Productos</span>
                  <span class="legend-value">{{ dashboardData.productosVendidos }} ({{ getProductPercentage().toFixed(1) }}%)</span>
                </div>
              </div>
              <div class="distribution-insight">
                <i class="fas fa-lightbulb"></i>
                <span v-if="getServicePercentage() > getProductPercentage()">
                  Los servicios generan más actividad que los productos
                </span>
                <span v-else>
                  Los productos son la principal fuente de actividad
                </span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- 📊 SECCIÓN DE TOP LISTAS -->
      <div class="top-section">
        <h3 class="section-title"><i class="fas fa-trophy"></i> Análisis de Desempeño</h3>
        <p class="section-subtitle">Top performers del período seleccionado</p>
        
        <div class="top-grid">
          
          <div class="section-card top-card">
            <div class="section-header">
              <h3><i class="fas fa-star"></i> Servicios Más Solicitados</h3>
              <span class="total-count">Total: {{ getTotalServices() }}</span>
            </div>
            <div class="list-body">
              <div class="list-item" v-for="(s, i) in dashboardData.serviciosTop" :key="i">
                <div class="rank" :class="getRankClass(i)">
                  <i v-if="i === 0" class="fas fa-crown"></i>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <div class="item-content">
                  <div class="item-header">
                    <div class="item-name">{{ s.nombre }}</div>
                    <div class="item-percentage">{{ getItemPercentage(s.cantidad, dashboardData.serviciosTop) }}%</div>
                  </div>
                  <div class="item-progress">
                    <div class="progress-bar">
                      <div 
                        class="progress-fill service" 
                        :style="{ width: getPercentage(s.cantidad, dashboardData.serviciosTop) + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
                <div class="item-count">{{ s.cantidad }} turnos</div>
              </div>
              <div v-if="!dashboardData.serviciosTop.length" class="no-data-text">
                <i class="fas fa-inbox"></i>
                Sin servicios registrados
              </div>
            </div>
          </div>

          <div class="section-card top-card">
            <div class="section-header">
              <h3><i class="fas fa-fire"></i> Productos Más Vendidos</h3>
              <span class="total-count">Total: {{ dashboardData.productosVendidos }} unidades</span>
            </div>
            <div class="list-body">
              <div class="list-item" v-for="(p, i) in dashboardData.productosTop" :key="i">
                <div class="rank" :class="getRankClass(i)">
                  <i v-if="i === 0" class="fas fa-crown"></i>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <div class="item-content">
                  <div class="item-header">
                    <div class="item-name">{{ p.nombre }}</div>
                    <div class="item-percentage">{{ getItemPercentage(p.cantidad, dashboardData.productosTop) }}%</div>
                  </div>
                  <div class="item-progress">
                    <div class="progress-bar">
                      <div 
                        class="progress-fill product" 
                        :style="{ width: getPercentage(p.cantidad, dashboardData.productosTop) + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
                <div class="item-count">{{ p.cantidad }} u.</div>
              </div>
              <div v-if="!dashboardData.productosTop.length" class="no-data-text">
                <i class="fas fa-inbox"></i>
                Sin productos vendidos
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- 📈 ESTADÍSTICAS ADICIONALES -->
      <div class="stats-grid">
        
        <div class="section-card stat-card">
          <div class="section-header">
            <h3><i class="fas fa-box-open"></i> Estado de Inventario</h3>
          </div>
          <div class="stat-body">
            <div class="stat-item">
              <div class="stat-label">Productos en stock bajo</div>
              <div class="stat-value" :class="{ 'warning': dashboardData.stockBajoCount > 0 }">
                {{ dashboardData.stockBajoCount }}
              </div>
            </div>
            <button 
              v-if="dashboardData.stockBajoCount > 0" 
              @click="irAInventario" 
              class="action-btn full-width"
            >
              <i class="fas fa-boxes"></i>
              Revisar Inventario Crítico
            </button>
          </div>
        </div>


        <div class="section-card stat-card insights-card">
          <div class="section-header">
            <h3><i class="fas fa-lightbulb"></i> Información del período</h3>
          </div>
          <div class="insights-body">
            <div class="insight-item" v-if="dashboardData.serviciosTop.length > 0">
              <i class="fas fa-medal"></i>
              <div class="insight-content">
                <strong>Servicio estrella:</strong> {{ dashboardData.serviciosTop[0]?.nombre }}
              </div>
            </div>
            <div class="insight-item" v-if="dashboardData.productosTop.length > 0">
              <i class="fas fa-shopping-bag"></i>
              <div class="insight-content">
                <strong>Producto top:</strong> {{ dashboardData.productosTop[0]?.nombre }}
              </div>
            </div>
            <div class="insight-item">
              <i class="fas fa-chart-line"></i>
              <div class="insight-content">
                <strong>Mejor día:</strong> {{ getPeakDay() }} (${{ formatNumber(Math.max(...dashboardData.ventasPorDia)) }})
              </div>
            </div>
          </div>
        </div>

      </div>

    </main>

  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axiosConfig'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const router = useRouter()
const selectedPeriod = ref('semana')
const loading = ref(true)
const error = ref(null)
const hoveredPoint = ref(null)
const dashboardContent = ref(null)

// Fechas personalizadas
const customDateRange = ref(false)
const dateFrom = ref('')
const dateTo = ref('')
const today = new Date().toISOString().split('T')[0]

const periods = [
  { value: 'hoy', label: 'Hoy', icon: 'fas fa-clock' },
  { value: 'semana', label: '7 Días', icon: 'fas fa-calendar-week' },
  { value: 'mes', label: 'Este Mes', icon: 'fas fa-calendar-alt' },
]

const dashboardData = ref({
  ingresosTotales: 0,
  serviciosRealizados: 0,
  productosVendidos: 0,
  stockBajoCount: 0,
  ventasPorDia: [],
  labelsDias: [],
  serviciosTop: [],
  productosTop: [],
  clientesAtendidos: 0,
  inventarioTotal: 0,
  valorInventario: 0
})

// Computed properties
const getPeriodDisplay = computed(() => {
  if (customDateRange.value && dateFrom.value && dateTo.value) {
    return `${formatDate(dateFrom.value)} al ${formatDate(dateTo.value)}`
  }
  const period = periods.find(p => p.value === selectedPeriod.value)
  return period ? period.label : 'Período'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

// Dimensiones del gráfico
const chartWidth = 900
const chartHeight = 320
const padding = 60

const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  value: 0,
  date: '',
  index: 0
})

const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    const params = customDateRange.value && dateFrom.value && dateTo.value
      ? { date_from: dateFrom.value, date_to: dateTo.value }
      : { period: selectedPeriod.value }
    
    const res = await axios.get('/usuarios/api/dashboard/', { params })
    dashboardData.value = { ...dashboardData.value, ...res.data }
  } catch (err) {
    console.error(err)
    error.value = "Error al conectar con el servidor."
  } finally {
    loading.value = false
  }
}

const selectPeriod = (period) => {
  customDateRange.value = false
  selectedPeriod.value = period
  fetchDashboardData()
}

const toggleCustomRange = () => {
  customDateRange.value = !customDateRange.value
  if (!customDateRange.value) {
    fetchDashboardData()
  }
}

const applyCustomRange = () => {
  if (dateFrom.value && dateTo.value) {
    fetchDashboardData()
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'short'
  })
}

const formatNumber = (num) => new Intl.NumberFormat('es-AR').format(num || 0)

const formatNumberShort = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

// Métricas calculadas
const calculateAverageDaily = () => {
  if (!dashboardData.value.ventasPorDia.length) return 0
  const sum = dashboardData.value.ventasPorDia.reduce((a, b) => a + b, 0)
  return sum / dashboardData.value.ventasPorDia.length
}

const calculateAverageTicket = () => {
  const totalTransactions = dashboardData.value.productosVendidos + dashboardData.value.serviciosRealizados
  if (totalTransactions === 0) return 0
  return dashboardData.value.ingresosTotales / totalTransactions
}

const calculateProductsPerSale = () => {
  if (dashboardData.value.serviciosRealizados === 0) return 0
  return dashboardData.value.productosVendidos / dashboardData.value.serviciosRealizados
}

const calculateServicesPerClient = () => {
  if (dashboardData.value.clientesAtendidos === 0) return 0
  return dashboardData.value.serviciosRealizados / dashboardData.value.clientesAtendidos
}

const calculateMargin = () => {
  // Estimación simple del margen (50% como base)
  return 50
}

const calculateGrowth = () => {
  // Simulación de crecimiento vs período anterior
  return Math.random() * 20 - 5 // Entre -5% y +15%
}

const getPeakDay = () => {
  if (!dashboardData.value.ventasPorDia.length) return '--'
  const maxValue = Math.max(...dashboardData.value.ventasPorDia)
  const index = dashboardData.value.ventasPorDia.indexOf(maxValue)
  return dashboardData.value.labelsDias[index] || '--'
}

const getMaxValue = () => {
  return Math.max(...dashboardData.value.ventasPorDia, 1)
}

// Métodos del gráfico
const getXPosition = (index) => {
  const count = dashboardData.value.ventasPorDia.length
  if (count <= 1) return chartWidth / 2
  return padding + (index / (count - 1)) * (chartWidth - padding * 2)
}

const getXPositionPercent = (index) => {
  const count = dashboardData.value.ventasPorDia.length
  if (count <= 1) return 50
  return (padding / chartWidth * 100) + (index / (count - 1)) * ((chartWidth - padding * 2) / chartWidth * 100)
}

const getYPosition = (value) => {
  const max = getMaxValue()
  const normalized = value / max
  return chartHeight - padding - (normalized * (chartHeight - padding * 2))
}

const getLinePath = () => {
  if (!dashboardData.value.ventasPorDia.length) return ''
  
  let path = ''
  dashboardData.value.ventasPorDia.forEach((value, i) => {
    const x = getXPosition(i)
    const y = getYPosition(value)
    
    if (i === 0) {
      path += `M ${x} ${y}`
    } else {
      const prevX = getXPosition(i - 1)
      const prevY = getYPosition(dashboardData.value.ventasPorDia[i - 1])
      const cpX = (prevX + x) / 2
      
      path += ` Q ${cpX} ${prevY}, ${x} ${y}`
    }
  })
  
  return path
}

const getAreaPath = () => {
  if (!dashboardData.value.ventasPorDia.length) return ''
  
  let path = getLinePath()
  
  const lastX = getXPosition(dashboardData.value.ventasPorDia.length - 1)
  const firstX = getXPosition(0)
  
  path += ` L ${lastX} ${chartHeight - padding}`
  path += ` L ${firstX} ${chartHeight - padding}`
  path += ' Z'
  
  return path
}

const getPiePath = (startPercent, endPercent) => {
  const startAngle = (startPercent / 100) * 360
  const endAngle = (endPercent / 100) * 360
  
  const cx = 100
  const cy = 100
  const r = 80
  
  const startRad = (startAngle - 90) * Math.PI / 180
  const endRad = (endAngle - 90) * Math.PI / 180
  
  const x1 = cx + r * Math.cos(startRad)
  const y1 = cy + r * Math.sin(startRad)
  const x2 = cx + r * Math.cos(endRad)
  const y2 = cy + r * Math.sin(endRad)
  
  const largeArc = endAngle - startAngle > 180 ? 1 : 0
  
  return `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`
}

const getServicePercentage = () => {
  const total = dashboardData.value.serviciosRealizados + dashboardData.value.productosVendidos
  if (total === 0) return 50
  return (dashboardData.value.serviciosRealizados / total) * 100
}

const getProductPercentage = () => {
  return 100 - getServicePercentage()
}

const getTotalServices = () => {
  return dashboardData.value.serviciosTop.reduce((sum, item) => sum + item.cantidad, 0)
}

const getTotalTransactions = () => {
  return dashboardData.value.serviciosRealizados + dashboardData.value.productosVendidos
}

const showTooltip = (index, value, event) => {
  hoveredPoint.value = index
  const rect = event.target.getBoundingClientRect()
  const container = event.target.closest('.trading-chart-container').getBoundingClientRect()
  
  tooltip.value = {
    visible: true,
    x: rect.left - container.left,
    y: rect.top - container.top - 90,
    value: value,
    date: dashboardData.value.labelsDias[index],
    index: index
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
  hoveredPoint.value = null
}

const getComparisonClass = (value) => {
  const avg = calculateAverageDaily()
  if (value > avg * 1.2) return 'positive'
  if (value < avg * 0.8) return 'negative'
  return 'neutral'
}

const getComparisonIcon = (value) => {
  const avg = calculateAverageDaily()
  if (value > avg * 1.2) return 'fas fa-arrow-up'
  if (value < avg * 0.8) return 'fas fa-arrow-down'
  return 'fas fa-equals'
}

const getComparisonText = (value) => {
  const avg = calculateAverageDaily()
  const diff = ((value - avg) / avg) * 100
  if (value > avg * 1.2) return `${diff.toFixed(1)}% sobre el promedio`
  if (value < avg * 0.8) return `${Math.abs(diff).toFixed(1)}% bajo el promedio`
  return 'En línea con el promedio'
}

const getTrendClass = (type) => {
  // Simulación de tendencias
  const trends = {
    income: Math.random() > 0.3 ? 'positive' : 'negative',
    service: Math.random() > 0.4 ? 'positive' : 'negative',
    product: Math.random() > 0.5 ? 'positive' : 'negative'
  }
  return trends[type] || 'positive'
}

const getTrendIcon = (type) => {
  const trendClass = getTrendClass(type)
  return trendClass === 'positive' ? 'fas fa-arrow-up' : 'fas fa-arrow-down'
}

const getTrendPercentage = (type) => {
  // Simulación de porcentajes
  const percentages = {
    income: (Math.random() * 15 + 5).toFixed(1),
    service: (Math.random() * 12 + 3).toFixed(1),
    product: (Math.random() * 18 + 8).toFixed(1)
  }
  return percentages[type] || '0.0'
}

const getRankClass = (index) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

const getPercentage = (value, array) => {
  const max = Math.max(...array.map(item => item.cantidad))
  return max > 0 ? (value / max) * 100 : 0
}

const getItemPercentage = (value, array) => {
  const total = array.reduce((sum, item) => sum + item.cantidad, 0)
  return total > 0 ? ((value / total) * 100).toFixed(1) : '0.0'
}

const getMarginClass = () => {
  const margin = calculateMargin()
  if (margin > 60) return 'positive'
  if (margin < 40) return 'negative'
  return 'neutral'
}

const calcularClientes = () => {
  return Math.round((dashboardData.value.serviciosRealizados + dashboardData.value.productosVendidos) / 2)
}

const irAInventario = () => {
  router.push({ path: '/productos', query: { filtro: 'stock_bajo' } })
}

const printReport = () => {
  window.print()
}

// Generar PDF mejorado
const generatePDF = async () => {
  try {
    loading.value = true
    
    const element = dashboardContent.value
    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#0f172a',
      logging: false,
      useCORS: true
    })
    
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    const imgWidth = 210
    const pageHeight = 297
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    
    let heightLeft = imgHeight
    let position = 10
    
    // Agregar título y metadata
    pdf.setFillColor(15, 23, 42)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.setTextColor(255, 255, 255)
    pdf.setFontSize(20)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Reporte Comercial', 105, 20, { align: 'center' })
    
    pdf.setFontSize(12)
    pdf.setFont('helvetica', 'normal')
    pdf.text(`Período: ${getPeriodDisplay.value}`, 105, 30, { align: 'center' })
    pdf.text(`Generado: ${currentDate.value}`, 105, 35, { align: 'center' })
    
    // Agregar imagen del dashboard
    pdf.addImage(imgData, 'PNG', 0, 45, imgWidth, imgHeight)
    
    // Agregar página si es necesario
    heightLeft -= pageHeight - 55
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }
    
    pdf.save(`reporte-${selectedPeriod.value}-${Date.now()}.pdf`)
    
  } catch (err) {
    console.error('Error generando PDF:', err)
    alert('Error al generar el PDF')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchDashboardData())
</script>

<style scoped>
:root {
  --bg-dark: #0f172a;
  --bg-card: #1e293b;
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --accent: #3b82f6;
  --border: #334155;
  --positive: #10b981;
  --negative: #ef4444;
  --warning: #f59e0b;
}

.dashboard-wrapper {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  min-height: 100vh;
  color: #f1f5f9;
  padding: 2rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* HEADER MEJORADO */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dashboard-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard-subtitle {
  color: #94a3b8;
  margin: 0.5rem 0 0;
  font-size: 0.95rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.period-display {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #60a5fa;
  display: flex;
  align-items: center;
  gap: 8px;
}

.period-selector {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 12px;
  padding: 6px;
  border: 1px solid #334155;
  display: flex;
  gap: 4px;
}

.period-selector button {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.period-selector button.active {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.period-selector button:hover:not(.active) {
  background: rgba(59, 130, 246, 0.1);
  color: white;
}

.pdf-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
}

.pdf-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.6);
}

.pdf-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* RESUMEN DEL PERÍODO */
.period-summary-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 18px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid #334155;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.summary-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #f1f5f9;
  display: flex;
  align-items: center;
  gap: 10px;
}

.period-tag {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #60a5fa;
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.summary-stat {
  text-align: center;
}

.stat-label {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 900;
  color: #f1f5f9;
  line-height: 1;
}

/* KPI CARDS MEJORADAS */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 18px;
  padding: 1.5rem;
  border: 1px solid #334155;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
  background: linear-gradient(90deg, currentColor, transparent);
  opacity: 0;
  transition: opacity 0.4s;
}

.kpi-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  border-color: currentColor;
}

.kpi-card:hover::before {
  opacity: 1;
}

.income { color: #10b981; }
.service { color: #3b82f6; }
.product { color: #f97316; }
.clients { color: #8b5cf6; }

.kpi-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.kpi-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  transition: all 0.4s;
  position: relative;
  overflow: hidden;
}

.kpi-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  background: currentColor;
  opacity: 0.1;
}

.kpi-card:hover .kpi-icon {
  transform: scale(1.1) rotate(5deg);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-trend.positive {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.kpi-trend.negative {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.kpi-data {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.kpi-data .label {
  font-size: 0.9rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 700;
}

.kpi-data .value {
  font-size: 2.5rem;
  font-weight: 900;
  color: white;
  line-height: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.kpi-data .subtitle {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.kpi-sparkline {
  height: 40px;
  width: 100%;
  margin-top: 1rem;
  opacity: 0.4;
  transition: opacity 0.3s;
}

.kpi-card:hover .kpi-sparkline {
  opacity: 0.8;
}

/* GRID DE GRÁFICOS */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.main-chart {
  grid-column: 1;
}

.distribution-card {
  grid-column: 2;
}

@media (max-width: 1200px) {
  .main-chart,
  .distribution-card {
    grid-column: 1;
  }
}

/* SECCIÓN DE GRÁFICO PRINCIPAL */
.chart-section {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 18px;
  border: 1px solid #334155;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.section-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #334155;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #f1f5f9;
}

.chart-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chart-legend {
  font-size: 0.85rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.chart-body {
  padding: 2rem;
  background: linear-gradient(to bottom, rgba(59, 130, 246, 0.03), transparent);
}

.trading-chart-container {
  position: relative;
  width: 100%;
  height: 380px;
  padding: 20px 0 60px 0;
}

.chart-grid,
.chart-svg {
  position: absolute;
  top: 20px;
  left: 0;
  width: 100%;
  height: calc(100% - 80px);
}

.chart-grid {
  pointer-events: none;
}

.chart-area {
  opacity: 0;
  animation: fadeInArea 1.5s ease-out 0.3s forwards;
}

.chart-line {
  stroke-dasharray: 3000;
  stroke-dashoffset: 3000;
  animation: drawLine 2s ease-out forwards;
}

.peak-point {
  animation: pulse 2s infinite;
  filter: drop-shadow(0 0 8px #ef4444);
}

@keyframes pulse {
  0%, 100% {
    r: 8;
  }
  50% {
    r: 10;
  }
}

.chart-labels {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  display: flex;
  padding: 0 60px;
}

.day-label {
  position: absolute;
  transform: translateX(-50%);
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.day-label.active {
  color: #60a5fa;
  transform: translateX(-50%) scale(1.15);
}

.day-label.peak {
  color: #ef4444;
}

.peak-badge {
  font-size: 0.7rem;
  background: rgba(239, 68, 68, 0.2);
  padding: 2px 6px;
  border-radius: 10px;
  color: #fca5a5;
}

/* GRÁFICO DE DISTRIBUCIÓN */
.distribution-body {
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.distribution-chart {
  flex-shrink: 0;
}

.pie-sector {
  transition: transform 0.3s;
}

.pie-sector:hover {
  transform: scale(1.05);
  transform-origin: center;
}

.distribution-legend {
  flex: 1;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s;
}

.legend-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(5px);
}

.legend-color {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  flex-shrink: 0;
}

.legend-color.service {
  background: linear-gradient(135deg, #10b981, #047857);
}

.legend-color.product {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.legend-content {
  flex: 1;
}

.legend-label {
  display: block;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 4px;
}

.legend-value {
  display: block;
  font-size: 0.9rem;
  color: #94a3b8;
  font-weight: 600;
}

.distribution-insight {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #60a5fa;
  font-weight: 600;
}

/* SECCIÓN TOP */
.top-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-subtitle {
  color: #94a3b8;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.top-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.top-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.top-card .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-count {
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 20px;
}

.list-body {
  padding: 0;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #334155;
  transition: all 0.3s;
}

.list-item:hover {
  background: rgba(59, 130, 246, 0.05);
  padding-left: 2rem;
}

.list-item:last-child {
  border-bottom: none;
}

.rank {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 900;
  background: #334155;
  color: #94a3b8;
  flex-shrink: 0;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.rank::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.1;
}

.rank.gold::before { background: #fbbf24; }
.rank.silver::before { background: #e5e7eb; }
.rank.bronze::before { background: #fb923c; }

.list-item:hover .rank {
  transform: scale(1.15) rotate(5deg);
}

.rank.gold {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #78350f;
  box-shadow: 0 6px 20px rgba(251, 191, 36, 0.4);
}

.rank.silver {
  background: linear-gradient(135deg, #e5e7eb 0%, #9ca3af 100%);
  color: #374151;
  box-shadow: 0 6px 20px rgba(156, 163, 175, 0.3);
}

.rank.bronze {
  background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%);
  color: #7c2d12;
  box-shadow: 0 6px 20px rgba(251, 146, 60, 0.3);
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-name {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-percentage {
  font-size: 0.85rem;
  font-weight: 800;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.item-progress {
  width: 100%;
}

.progress-bar {
  height: 8px;
  background: rgba(148, 163, 184, 0.15);
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fillBar 2s ease-out;
}

.progress-fill.service {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.progress-fill.product {
  background: linear-gradient(90deg, #f97316 0%, #fb923c 100%);
}

.item-count {
  font-weight: 900;
  color: #f1f5f9;
  font-size: 1.1rem;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 12px;
  min-width: 80px;
  text-align: center;
}

/* ESTADÍSTICAS ADICIONALES */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.stat-body {
  padding: 1.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 0.9rem;
  color: #94a3b8;
  font-weight: 600;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 800;
  color: #f1f5f9;
}

.stat-value.positive {
  color: #10b981;
}

.stat-value.negative {
  color: #ef4444;
}

.stat-value.warning {
  color: #f59e0b;
  animation: pulseWarning 2s infinite;
}

@keyframes pulseWarning {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.insights-card .stat-body {
  padding: 1.5rem;
}

.insight-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  margin-bottom: 1rem;
  transition: all 0.3s;
}

.insight-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(5px);
}

.insight-item:last-child {
  margin-bottom: 0;
}

.insight-item i {
  color: #3b82f6;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
  font-size: 0.9rem;
  color: #94a3b8;
  line-height: 1.5;
}

.insight-content strong {
  color: #f1f5f9;
  font-weight: 700;
}

.insight-content .positive {
  color: #10b981;
  font-weight: 800;
}

.insight-content .negative {
  color: #ef4444;
  font-weight: 800;
}

/* BOTONES */
.action-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  width: 100%;
  margin-top: 1rem;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.6);
}

.action-btn.full-width {
  width: 100%;
}

/* FOOTER */
.report-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #334155;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-info {
  color: #64748b;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-actions {
  display: flex;
  gap: 1rem;
}

.footer-btn {
  background: transparent;
  border: 1px solid #334155;
  color: #94a3b8;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.footer-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  border-color: #3b82f6;
}

.footer-btn.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
}

.footer-btn.primary:hover {
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

/* TOOLTIP MEJORADO */
.chart-tooltip {
  position: absolute;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 2px solid #3b82f6;
  border-radius: 16px;
  padding: 0;
  pointer-events: none;
  z-index: 1000;
  min-width: 200px;
  box-shadow: 0 20px 50px rgba(59, 130, 246, 0.5);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.tooltip-enter-active,
.tooltip-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}

.tooltip-header {
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.2);
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  color: #60a5fa;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.tooltip-badge {
  margin-left: auto;
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tooltip-body {
  padding: 16px;
  text-align: center;
}

.tooltip-value {
  font-size: 2rem;
  font-weight: 900;
  color: #60a5fa;
  line-height: 1;
  margin-bottom: 8px;
  text-shadow: 0 2px 8px rgba(59, 130, 246, 0.5);
}

.tooltip-label {
  font-size: 0.8rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 12px;
  font-weight: 600;
}

.tooltip-comparison {
  font-size: 0.8rem;
  padding: 8px 12px;
  border-radius: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tooltip-comparison.positive {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.tooltip-comparison.negative {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.tooltip-comparison.neutral {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

/* ESTADOS */
.state-container {
  height: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}

.loader {
  width: 60px;
  height: 60px;
  border: 5px solid #334155;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s infinite linear;
  position: relative;
}

.loader::after {
  content: '';
  position: absolute;
  inset: -8px;
  border: 5px solid transparent;
  border-top-color: #60a5fa;
  border-radius: 50%;
  animation: spin 2s infinite linear reverse;
  opacity: 0.5;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: #94a3b8;
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 1.1rem;
  text-align: center;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  text-align: center;
  padding: 3rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 20px;
  border: 2px solid rgba(239, 68, 68, 0.2);
}

.error-content i {
  font-size: 5rem;
  color: #ef4444;
  animation: pulse 2s infinite;
}

.error-content h3 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: #f1f5f9;
}

.error-content p {
  margin: 0;
  color: #fca5a5;
  max-width: 400px;
  line-height: 1.6;
}

.retry-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-size: 0.9rem;
}

.retry-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.6);
}

.fade-in {
  animation: fadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fillBar {
  from {
    width: 0;
  }
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .period-selector {
    flex: 1;
    max-width: 400px;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-wrapper {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
  }
  
  .header-right {
    flex-direction: column;
    gap: 1rem;
  }
  
  .period-selector {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .period-selector button {
    flex: 1;
    min-width: 90px;
  }
  
  .pdf-btn {
    width: 100%;
    justify-content: center;
  }
  
  .date-inputs {
    flex-direction: column;
  }
  
  .date-input-group {
    width: 100%;
  }
  
  .apply-btn {
    width: 100%;
    justify-content: center;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .top-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .distribution-body {
    flex-direction: column;
    text-align: center;
  }
  
  .footer-content {
    flex-direction: column;
    text-align: center;
  }
  
  .footer-actions {
    width: 100%;
    justify-content: center;
  }
  
  .trading-chart-container {
    height: 300px;
  }
  
  .chart-labels {
    padding: 0 40px;
  }
  
  .day-label {
    font-size: 0.75rem;
  }
}

@media print {
  .dashboard-wrapper {
    background: white !important;
    color: black !important;
    padding: 0 !important;
  }
  
  .dashboard-header,
  .period-selector,
  .pdf-btn,
  .report-footer,
  .action-btn {
    display: none !important;
  }
  
  .section-card {
    break-inside: avoid;
    border: 1px solid #ddd !important;
    box-shadow: none !important;
  }
}
</style>