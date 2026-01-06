<template>
  <div class="dashboard-wrapper">
    
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">Dashboard - Reporte Comercial</h1>
        <p class="dashboard-subtitle">Análisis integral de ventas y servicios</p>
      </div>
      
      <div class="header-right">
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


        <button @click="generatePDF" class="pdf-btn" :disabled="loading">
          <i class="fas fa-file-pdf"></i>
          Exportar Reporte
        </button>
      </div>
    </header>

    <div v-if="customDateRange" class="custom-date-panel">
      <div class="custom-date-content">
        <div class="date-inputs">
          <div class="date-input-group">
            <label><i class="fas fa-calendar-day"></i> Fecha Desde</label>
            <input type="date" v-model="dateFrom" :max="dateTo || today" class="date-input-custom" />
          </div>
          <div class="date-input-group">
            <label><i class="fas fa-calendar-day"></i> Fecha Hasta</label>
            <input type="date" v-model="dateTo" :min="dateFrom" :max="today" class="date-input-custom" />
          </div>
          <button @click="applyCustomRange" class="apply-btn" :disabled="!dateFrom || !dateTo">
            <i class="fas fa-check"></i> Aplicar
          </button>
        </div>
        <div class="date-range-info" v-if="dateFrom && dateTo">
          <i class="fas fa-info-circle"></i> Mostrando datos desde <strong>{{ formatDateLong(dateFrom) }}</strong> hasta <strong>{{ formatDateLong(dateTo) }}</strong>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state-container">
      <div class="loader"></div>
      <p class="loading-text">Generando reporte...</p>
    </div>

    <div v-else-if="error" class="state-container error">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error de Conexión</h3>
        <p>{{ error }}</p>
        <button @click="fetchDashboardData" class="retry-btn"><i class="fas fa-redo"></i> Reintentar</button>
      </div>
    </div>

    <main v-else class="dashboard-content fade-in" ref="dashboardContent">

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
              <polyline points="0,18 20,15 40,10 60,12 80,6 100,4" fill="none" stroke="currentColor" stroke-width="2"/>
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
              <polyline points="0,20 20,16 40,18 60,13 80,10 100,8" fill="none" stroke="currentColor" stroke-width="2"/>
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
              <polyline points="0,14 20,12 40,9 60,11 80,5 100,3" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
        </div>
        </div>

      <div class="section-card chart-section">
        <div class="section-header">
          <h3><i class="fas fa-chart-line"></i> Evolución de Ingresos Diarios</h3>
          <div class="chart-info">
            <span class="chart-legend"><i class="fas fa-circle" style="color: #ef4444"></i> Ingresos por día</span>
          </div>
        </div>
        <div class="chart-body">
          <div v-if="dashboardData.ventasPorDia.length" class="trading-chart-container">
            <svg class="chart-grid" :viewBox="`0 0 ${chartWidth} ${chartHeight}`">
              <g v-for="i in 5" :key="`ref-${i}`">
                <line :x1="60" :y1="(chartHeight / 5) * i" :x2="chartWidth - 20" :y2="(chartHeight / 5) * i" stroke="#475569" stroke-width="1" stroke-dasharray="5,5" opacity="0.6"/>
                <text :x="10" :y="(chartHeight / 5) * i + 5" fill="#94a3b8" font-size="11" font-weight="600" font-family="system-ui">${{ formatNumberShort(Math.round((getMaxValue() / 5) * (5 - i))) }}</text>
              </g>
            </svg>
            <svg class="chart-svg" :viewBox="`0 0 ${chartWidth} ${chartHeight}`">
              <defs>
                <linearGradient id="areaGradientRed" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.35" />
                  <stop offset="100%" style="stop-color:#fca5a5;stop-opacity:0.05" />
                </linearGradient>
                <filter id="glowRed">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
              </defs>
              <path :d="getAreaPath()" fill="url(#areaGradientRed)" class="chart-area"/>
              <path :d="getLinePath()" fill="none" stroke="#ef4444" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="chart-line-red" filter="url(#glowRed)"/>
              <g v-for="(monto, i) in dashboardData.ventasPorDia" :key="`point-${i}`">
                <circle v-if="monto === Math.max(...dashboardData.ventasPorDia)" :cx="getXPosition(i)" :cy="getYPosition(monto)" r="9" fill="#dc2626" stroke="#ffffff" stroke-width="3" class="peak-point"/>
                <circle :cx="getXPosition(i)" :cy="getYPosition(monto)" r="6" fill="#0f172a" stroke="#ef4444" stroke-width="3" class="chart-point-red" @mouseenter="showTooltip(i, monto, $event)" @mouseleave="hideTooltip"/>
              </g>
            </svg>
            <div class="chart-labels">
              <span v-for="(label, i) in dashboardData.labelsDias" :key="`label-${i}`" class="day-label" :style="{ left: getXPositionPercent(i) + '%' }">{{ label }}</span>
            </div>
            <Transition name="tooltip">
              <div v-if="tooltip.visible" class="chart-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
                <div class="tooltip-header">{{ tooltip.date }}</div>
                <div class="tooltip-body"><div class="tooltip-value">${{ formatNumber(tooltip.value) }}</div></div>
              </div>
            </Transition>
          </div>
          <div v-else class="no-data">
            <i class="fas fa-chart-line"></i><p>No hay ventas registradas en este período</p>
          </div>
        </div>
      </div>

      <div class="section-card distribution-card">
        <div class="section-header">
          <h3><i class="fas fa-chart-pie"></i> Distribución de Actividad</h3>
        </div>
        <div class="distribution-body">
          <div class="distribution-chart-container">
            <svg width="240" height="240" viewBox="0 0 200 200">
              <defs>
                <linearGradient id="pieGradient1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" /><stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" /></linearGradient>
                <linearGradient id="pieGradient2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#10b981;stop-opacity:1" /><stop offset="100%" style="stop-color:#047857;stop-opacity:1" /></linearGradient>
              </defs>
              <circle cx="100" cy="100" r="85" fill="transparent" stroke="#334155" stroke-width="2" opacity="0.3"/>
              <path :d="getPiePath(0, getServicePercentage())" fill="url(#pieGradient2)" class="pie-sector"/>
              <path :d="getPiePath(getServicePercentage(), 100)" fill="url(#pieGradient1)" class="pie-sector"/>
              <circle cx="100" cy="100" r="45" fill="#1e293b"/>
              <text x="100" y="105" text-anchor="middle" fill="#f1f5f9" font-size="20" font-weight="800">{{ getTotalTransactions() }}</text>
            </svg>
          </div>
          <div class="distribution-legend">
            <div class="legend-item">
              <div class="legend-color service"></div>
              <div class="legend-content">
                <span class="legend-label">Servicios</span>
                <span class="legend-value">{{ dashboardData.serviciosRealizados }} turnos ({{ getServicePercentage().toFixed(1) }}%)</span>
              </div>
            </div>
            <div class="legend-item">
              <div class="legend-color product"></div>
              <div class="legend-content">
                <span class="legend-label">Productos</span>
                <span class="legend-value">{{ dashboardData.productosVendidos }} unidades ({{ getProductPercentage().toFixed(1) }}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="top-section">
        <h3 class="section-title"><i class="fas fa-trophy"></i> Análisis de Desempeño</h3>
        <div class="top-grid">
          <div class="section-card top-card">
            <div class="section-header"><h3><i class="fas fa-star"></i> Servicios Top</h3></div>
            <div class="list-body">
              <div class="list-item" v-for="(s, i) in dashboardData.serviciosTop" :key="i">
                <div class="rank" :class="getRankClass(i)">{{ i + 1 }}</div>
                <div class="item-content">
                  <div class="item-name">{{ s.nombre }}</div>
                  <div class="progress-bar"><div class="progress-fill service" :style="{ width: getPercentage(s.cantidad, dashboardData.serviciosTop) + '%' }"></div></div>
                </div>
                <div class="item-count">{{ s.cantidad }}</div>
              </div>
            </div>
          </div>
          <div class="section-card top-card">
            <div class="section-header"><h3><i class="fas fa-fire"></i> Productos Top</h3></div>
            <div class="list-body">
              <div class="list-item" v-for="(p, i) in dashboardData.productosTop" :key="i">
                <div class="rank" :class="getRankClass(i)">{{ i + 1 }}</div>
                <div class="item-content">
                  <div class="item-name">{{ p.nombre }}</div>
                  <div class="progress-bar"><div class="progress-fill product" :style="{ width: getPercentage(p.cantidad, dashboardData.productosTop) + '%' }"></div></div>
                </div>
                <div class="item-count">{{ p.cantidad }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>

    <div id="print-template" style="display: none;">
      <div class="pdf-page">
        
        <div class="pdf-header">
          <div class="pdf-brand-row">
            <div class="pdf-logo-box">
              <img :src="logoUrl" class="pdf-logo-img" alt="Logo" crossorigin="anonymous" />
            </div>
            <div class="pdf-brand-info">
              <h1 class="pdf-title">HAIRSOFT</h1>
              <h2 class="pdf-subtitle">Los Últimos Serán Los Primeros</h2>
              <div class="pdf-report-meta">
                <p><strong>REPORTE DE GESTIÓN</strong></p>
                <p class="pdf-period-badge">Período: {{ getPeriodDisplay }}</p>
                <p class="pdf-date">Emisión: {{ new Date().toLocaleDateString('es-AR') }}</p>
              </div>
            </div>
          </div>
          <div class="pdf-divider-line"></div>
        </div>

        <div class="pdf-summary-grid">
          <div class="pdf-kpi-box">
            <span class="pdf-kpi-label">Ingresos Totales</span>
            <span class="pdf-kpi-value text-green">${{ formatNumber(dashboardData.ingresosTotales) }}</span>
          </div>
          <div class="pdf-kpi-box">
            <span class="pdf-kpi-label">Turnos Realizados</span>
            <span class="pdf-kpi-value">{{ dashboardData.serviciosRealizados }}</span>
          </div>
          <div class="pdf-kpi-box">
            <span class="pdf-kpi-label">Productos Vendidos</span>
            <span class="pdf-kpi-value">{{ dashboardData.productosVendidos }}</span>
          </div>
          </div>

        <div class="pdf-chart-container">
          <h4 class="pdf-section-title">Tendencia de Ventas</h4>
          <svg class="pdf-chart-svg" :viewBox="`0 0 ${chartWidth} ${chartHeight + 40}`" width="100%" height="300">
             <defs>
              <linearGradient id="pdfGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.2" />
                <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
              </linearGradient>
            </defs>
            <g v-for="i in 5" :key="`pdf-line-${i}`">
              <line :x1="60" :y1="(chartHeight / 5) * i" :x2="chartWidth - 20" :y2="(chartHeight / 5) * i" stroke="#e2e8f0" stroke-width="1"/>
              <text :x="50" :y="(chartHeight / 5) * i + 5" text-anchor="end" fill="#64748b" font-size="12" font-family="Helvetica">
                ${{ formatNumberShort(Math.round((getMaxValue() / 5) * (5 - i))) }}
              </text>
            </g>
            <path :d="getAreaPath()" fill="url(#pdfGradient)" />
            <path :d="getLinePath()" fill="none" stroke="#dc2626" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <g v-for="(label, i) in dashboardData.labelsDias" :key="`pdf-lbl-${i}`">
              <text :x="getXPosition(i)" :y="chartHeight + 25" text-anchor="middle" fill="#475569" font-size="11" font-weight="bold" font-family="Helvetica">
                {{ label }}
              </text>
            </g>
          </svg>
        </div>

        <div class="pdf-tables-row">
          <div class="pdf-table-col">
            <h4 class="pdf-section-title">Top 5 Servicios</h4>
            <table class="pdf-table">
              <thead><tr><th width="15%">#</th><th>Servicio</th><th width="25%" class="text-right">Cant.</th></tr></thead>
              <tbody>
                <tr v-for="(s, i) in dashboardData.serviciosTop.slice(0, 5)" :key="i">
                  <td><span class="pdf-rank-circle">{{ i + 1 }}</span></td>
                  <td>{{ s.nombre }}</td>
                  <td class="text-right"><strong>{{ s.cantidad }}</strong></td>
                </tr>
                <tr v-if="dashboardData.serviciosTop.length === 0"><td colspan="3" class="text-center text-muted">Sin datos</td></tr>
              </tbody>
            </table>
          </div>
          <div class="pdf-table-col">
            <h4 class="pdf-section-title">Top 5 Productos</h4>
            <table class="pdf-table">
              <thead><tr><th width="15%">#</th><th>Producto</th><th width="25%" class="text-right">Unid.</th></tr></thead>
              <tbody>
                <tr v-for="(p, i) in dashboardData.productosTop.slice(0, 5)" :key="i">
                  <td><span class="pdf-rank-circle">{{ i + 1 }}</span></td>
                  <td>{{ p.nombre }}</td>
                  <td class="text-right"><strong>{{ p.cantidad }}</strong></td>
                </tr>
                <tr v-if="dashboardData.productosTop.length === 0"><td colspan="3" class="text-center text-muted">Sin datos</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="pdf-footer">
          <p>HairSoft - Sistema de Gestión Integral</p>
          <p class="small text-muted">Documento generado el {{ new Date().toLocaleString() }}</p>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axiosConfig'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

// LOGO: Usamos la ruta estática directa (Asume que está en /public/logo_barberia.jpg)
const logoUrl = '/logo_barberia.jpg'

const router = useRouter()
const selectedPeriod = ref('semana')
const loading = ref(true)
const error = ref(null)
const hoveredPoint = ref(null)
const dashboardContent = ref(null)

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
  clientesAtendidos: 0
})

const getPeriodDisplay = computed(() => {
  if (customDateRange.value && dateFrom.value && dateTo.value) {
    return `${formatDate(dateFrom.value)} al ${formatDate(dateTo.value)}`
  }
  const period = periods.find(p => p.value === selectedPeriod.value)
  return period ? period.label : 'Período'
})

const chartWidth = 900
const chartHeight = 320
const padding = 60

const tooltip = ref({ visible: false, x: 0, y: 0, value: 0, date: '', index: 0 })

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
  if (!customDateRange.value) fetchDashboardData()
}

const applyCustomRange = () => {
  if (dateFrom.value && dateTo.value) fetchDashboardData()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('es-AR', { day: '2-digit', month: 'short' })
}

const formatDateLong = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('es-AR', { day: '2-digit', month: 'long', year: 'numeric' })
}

const formatNumber = (num) => new Intl.NumberFormat('es-AR').format(num || 0)

const formatNumberShort = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const calculateAverageDaily = () => {
  if (!dashboardData.value.ventasPorDia.length) return 0
  const sum = dashboardData.value.ventasPorDia.reduce((a, b) => a + b, 0)
  return sum / dashboardData.value.ventasPorDia.length
}

const getMaxValue = () => Math.max(...dashboardData.value.ventasPorDia, 1)

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
    if (i === 0) path += `M ${x} ${y}`
    else {
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
  path += ` L ${lastX} ${chartHeight - padding} L ${firstX} ${chartHeight - padding} Z`
  return path
}

const getPiePath = (startPercent, endPercent) => {
  const startAngle = (startPercent / 100) * 360
  const endAngle = (endPercent / 100) * 360
  const cx = 100, cy = 100, r = 80
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

const getProductPercentage = () => 100 - getServicePercentage()

const getTotalTransactions = () => dashboardData.value.serviciosRealizados + dashboardData.value.productosVendidos

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

// --- GENERACIÓN PDF ---
const generatePDF = async () => {
  try {
    loading.value = true
    const printTemplate = document.getElementById('print-template')
    if (!printTemplate) throw new Error('Template no encontrado')

    // Mostrar para captura
    printTemplate.style.display = 'block'
    
    // IMPORTANTE: Damos un poco de tiempo para que la imagen del logo cargue si no está en cache
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const canvas = await html2canvas(printTemplate, {
      scale: 2,
      backgroundColor: '#ffffff',
      useCORS: true, // Esto ayuda a cargar la imagen si el servidor lo permite
      logging: false,
      allowTaint: true
    })
    
    printTemplate.style.display = 'none'
    
    const imgData = canvas.toDataURL('image/jpeg', 0.95)
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width
    
    pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight)
    pdf.save(`Reporte_HAIRSOFT_${selectedPeriod.value}.pdf`)
    
  } catch (err) {
    console.error('Error PDF:', err)
    alert('Error al generar el PDF.')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchDashboardData())
</script>

<style scoped>
/* ESTILOS DASHBOARD */
:root {
  --bg-dark: #0f172a;
  --bg-card: #1e293b;
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --accent: #3b82f6;
  --border: #334155;
  --positive: #10b981;
  --negative: #ef4444;
}

.dashboard-wrapper {
  background: linear-gradient(135deg, #0f172a 0%, #0f172a 100%);
  min-height: 100vh;
  color: #f1f5f9;
  padding: 2rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

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

.dashboard-subtitle { color: #94a3b8; margin: 0.5rem 0 0; font-size: 0.95rem; }
.header-right { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }

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
  font-size: 0.85rem;
}

.pdf-btn:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(239, 68, 68, 0.6); }

/* KPI CARDS */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
.kpi-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 18px;
  padding: 1.5rem;
  border: 1px solid #334155;
  transition: all 0.4s;
  position: relative;
  overflow: hidden;
}
.kpi-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5); border-color: currentColor; }
.income { color: #10b981; }
.service { color: #3b82f6; }
.product { color: #f97316; }

.kpi-header-card { display: flex; justify-content: space-between; margin-bottom: 1.5rem; }
.kpi-icon { width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; background: rgba(255,255,255,0.05); }
.kpi-data .label { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; display: block; }
.kpi-data .value { font-size: 2.5rem; font-weight: 900; color: white; display: block; margin: 5px 0; }
.kpi-data .subtitle { font-size: 0.85rem; color: #64748b; }
.kpi-sparkline { height: 40px; width: 100%; margin-top: 1rem; opacity: 0.4; }

/* SECTIONS */
.section-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 18px;
  border: 1px solid #334155;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 2rem;
}
.section-header { padding: 1.5rem 2rem; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
.section-header h3 { margin: 0; font-size: 1.3rem; font-weight: 800; display: flex; align-items: center; gap: 12px; color: #f1f5f9; }

/* CHART */
.trading-chart-container { position: relative; width: 100%; height: 380px; padding: 20px 0 60px 0; }
.chart-grid, .chart-svg { position: absolute; top: 20px; left: 0; width: 100%; height: calc(100% - 80px); }
.chart-labels { position: absolute; bottom: 0; left: 0; width: 100%; height: 60px; padding: 0 60px; }
.day-label { position: absolute; transform: translateX(-50%); font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }

/* DISTRIBUTION */
.distribution-body { padding: 2rem; display: flex; align-items: center; gap: 2rem; flex-wrap: wrap; justify-content: center; }
.distribution-legend { flex: 1; min-width: 250px; }
.legend-item { display: flex; align-items: center; gap: 1rem; padding: 1rem; margin-bottom: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 12px; }
.legend-color { width: 24px; height: 24px; border-radius: 6px; }
.legend-color.service { background: linear-gradient(135deg, #10b981, #047857); }
.legend-color.product { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.legend-label { display: block; font-weight: 700; color: #f1f5f9; }
.legend-value { color: #94a3b8; font-size: 0.9rem; }

/* TOP LISTS */
.top-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }
.list-item { display: flex; align-items: center; gap: 1rem; padding: 1.2rem 1.5rem; border-bottom: 1px solid #334155; }
.rank { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; background: #334155; color: #94a3b8; }
.rank.gold { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #78350f; }
.rank.silver { background: linear-gradient(135deg, #e5e7eb, #9ca3af); color: #374151; }
.rank.bronze { background: linear-gradient(135deg, #fb923c, #ea580c); color: #7c2d12; }
.item-content { flex: 1; }
.item-name { font-weight: 700; color: #f1f5f9; margin-bottom: 5px; }
.progress-bar { height: 6px; background: rgba(148, 163, 184, 0.15); border-radius: 10px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 10px; }
.progress-fill.service { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.progress-fill.product { background: linear-gradient(90deg, #f97316, #fb923c); }
.item-count { font-weight: 900; color: #f1f5f9; font-size: 1.1rem; }

/* DATE PICKER & LOADER */
.custom-date-panel { margin-bottom: 2rem; }
.custom-date-content { background: #1e293b; padding: 1.5rem; border-radius: 16px; border: 1px solid #334155; }
.date-inputs { display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap; }
.date-input-custom { background: #0f172a; border: 2px solid #334155; color: white; padding: 10px; border-radius: 8px; }
.apply-btn { background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
.state-container { height: 400px; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #94a3b8; }
.loader { border: 4px solid #334155; border-top: 4px solid #3b82f6; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* ========================================================================= */
/* ESTILOS PDF */
/* ========================================================================= */
#print-template {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #111;
  background: white;
  width: 210mm;
}

.pdf-page {
  padding: 15mm 15mm;
  background: white;
}

.pdf-header {
  margin-bottom: 25px;
}

.pdf-brand-row {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 25px;
  padding-bottom: 15px;
}

.pdf-logo-box {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  border: 3px solid #ef4444;
  padding: 3px;
  overflow: hidden;
  background: white;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pdf-logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.pdf-brand-info {
  flex: 1;
}

.pdf-title {
  font-size: 38px;
  font-weight: 900;
  margin: 0;
  color: #1f2937;
  letter-spacing: 2px;
  line-height: 1;
}

.pdf-subtitle {
  font-size: 14px;
  color: #ef4444;
  margin: 5px 0 15px 0;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.pdf-report-meta {
  display: flex;
  gap: 20px;
  align-items: center;
  font-size: 11px;
  color: #4b5563;
  border-left: 3px solid #e5e7eb;
  padding-left: 15px;
}

.pdf-period-badge {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 700;
  color: #111;
  border: 1px solid #d1d5db;
}

.pdf-divider-line {
  height: 2px;
  background: linear-gradient(90deg, #ef4444 0%, #fca5a5 100%);
  width: 100%;
  margin-top: 5px;
}

/* KPI Summary PDF - REAJUSTADO PARA 3 COLUMNAS */
.pdf-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3 columnas en vez de 4 */
  gap: 15px;
  margin-bottom: 30px;
}

.pdf-kpi-box {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}

.pdf-kpi-label {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
  margin-bottom: 5px;
}

.pdf-kpi-value {
  display: block;
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.text-green { color: #059669; }

/* Chart PDF */
.pdf-chart-container {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  background: #fdfdfd;
}

.pdf-section-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 800;
  color: #1e293b;
  border-bottom: 2px solid #ef4444;
  display: inline-block;
  padding-bottom: 5px;
}

/* Tables PDF */
.pdf-tables-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.pdf-table-col {
  flex: 1;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 15px;
}

.pdf-table {
  width: 100%;
  border-collapse: collapse;
}

.pdf-table th {
  text-align: left;
  font-size: 10px;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #cbd5e1;
  padding: 8px 5px;
}

.pdf-table td {
  font-size: 12px;
  padding: 10px 5px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.pdf-rank-circle {
  background: #f1f5f9;
  color: #64748b;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 10px;
  font-weight: bold;
}

.text-right { text-align: right; }
.text-center { text-align: center; }
.text-muted { color: #94a3b8; }

.pdf-footer {
  margin-top: 40px;
  text-align: center;
  border-top: 1px solid #e2e8f0;
  padding-top: 15px;
  color: #64748b;
  font-size: 11px;
}
</style>