<template>
  <div class="dashboard-wrapper">
    
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">Dashboard - Reporte Comercial</h1>
        <p class="dashboard-subtitle">Análisis integral de ventas y caja</p>
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
          <i class="fas fa-file-invoice-dollar"></i>
          Exportar Balance
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
      <p class="loading-text">Generando balance de gestión...</p>
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
      
      <div v-if="!dashboardData.cajaAbierta && dashboardData.pendientesInfo && dashboardData.pendientesInfo.cantidad > 0" class="alerta-huerfanos" style="margin-bottom: 2rem;">
        <i class="fas fa-exclamation-circle" style="font-size: 2rem;"></i>
        <div class="alerta-content">
          <strong>Caja Cerrada - Cobros Web Pendientes</strong>
          <p>
            {{ dashboardData.pendientesInfo.cantidad === 1 ? 'Ingresó 1 pago' : `Ingresaron ${dashboardData.pendientesInfo.cantidad} pagos` }} 
            por Mercado Pago mientras la caja estaba inactiva.
            <strong>(Total: ${{ formatNumber(dashboardData.pendientesInfo.total_dinero) }})</strong>
            <span style="font-size: 0.85rem; opacity: 0.9;">Inicie un turno en "Caja Diaria" para asimilar estos ingresos al balance de hoy.</span>
          </p>
        </div>
      </div>

      <div v-if="!dashboardData.cajaAbierta && (!dashboardData.pendientesInfo || dashboardData.pendientesInfo.cantidad === 0)" class="alerta-huerfanos" style="margin-bottom: 2rem; border-color: #ef4444; background: rgba(239, 68, 68, 0.1);">
        <i class="fas fa-lock" style="font-size: 2rem; color: #ef4444;"></i>
        <div class="alerta-content">
          <strong style="color: #b91c1c;">La Caja Diaria está Cerrada</strong>
          <p style="color: #7f1d1d;">
            Actualmente no hay ninguna sesión de caja activa. No olvides iniciar el turno de caja antes de comenzar a registrar cobros presenciales.
          </p>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card income">
          <div class="kpi-header-card"><div class="kpi-icon"><i class="fas fa-dollar-sign"></i></div></div>
          <div class="kpi-data">
            <span class="label">Ingresos Totales</span>
            <span class="value">${{ formatNumber(dashboardData.ingresosTotales) }}</span>
            <span class="subtitle">Facturación bruta</span>
          </div>
        </div>
        <div class="kpi-card expense">
          <div class="kpi-header-card"><div class="kpi-icon"><i class="fas fa-arrow-down"></i></div></div>
          <div class="kpi-data">
            <span class="label">Egresos Totales</span>
            <span class="value">${{ formatNumber(dashboardData.egresosTotales) }}</span>
            <span class="subtitle">Gastos y pagos a proveedores</span>
          </div>
        </div>
        <div class="kpi-card service">
          <div class="kpi-header-card"><div class="kpi-icon"><i class="fas fa-cut"></i></div></div>
          <div class="kpi-data">
            <span class="label">Servicios Realizados</span>
            <span class="value">{{ dashboardData.serviciosRealizados }}</span>
            <span class="subtitle">Turnos atendidos</span>
          </div>
        </div>
        <div class="kpi-card product">
          <div class="kpi-header-card"><div class="kpi-icon"><i class="fas fa-shopping-bag"></i></div></div>
          <div class="kpi-data">
            <span class="label">Productos Vendidos</span>
            <span class="value">{{ dashboardData.productosVendidos }}</span>
            <span class="subtitle">Unidades vendidas</span>
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
          <div v-if="dashboardData.ventasPorDia && dashboardData.ventasPorDia.length" class="trading-chart-container">
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
              <span v-for="(label, i) in dashboardData.labelsDias" :key="`label-${i}`" class="day-label" :style="{ left: getXPositionPercent(i) + '%' }" v-if="shouldShowLabel(i)">
                {{ label }}
              </span>
            </div>
            <Transition name="tooltip">
              <div v-if="tooltip.visible" class="chart-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
                <div class="tooltip-header">{{ tooltip.date }}</div>
                <div class="tooltip-body"><div class="tooltip-value">${{ formatNumber(tooltip.value) }}</div></div>
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <div class="top-section">
        <h3 class="section-title" style="margin-bottom: 1.5rem;"><i class="fas fa-trophy"></i> Desempeño y Medios de Pago</h3>
        
        <div class="top-grid">
          
          <div class="section-card top-card">
            <div class="section-header"><h3><i class="fas fa-star"></i> Servicios Top</h3></div>
            <div class="list-body">
              <div class="list-item" v-for="(s, i) in dashboardData.serviciosTop" :key="i">
                <div class="rank">{{ i + 1 }}</div>
                <div class="item-content"><div class="item-name">{{ s.nombre }}</div></div>
                <div class="item-count">{{ s.cantidad }}</div>
              </div>
              <div v-if="!dashboardData.serviciosTop.length" class="empty-state">Sin servicios en este período</div>
            </div>
          </div>
          
          <div class="section-card top-card">
            <div class="section-header"><h3><i class="fas fa-fire"></i> Productos Top</h3></div>
            <div class="list-body">
              <div class="list-item" v-for="(p, i) in dashboardData.productosTop" :key="i">
                <div class="rank">{{ i + 1 }}</div>
                <div class="item-content"><div class="item-name">{{ p.nombre }}</div></div>
                <div class="item-count">{{ p.cantidad }}</div>
              </div>
              <div v-if="!dashboardData.productosTop.length" class="empty-state">Sin productos vendidos</div>
            </div>
          </div>

          <div class="section-card top-card">
            <div class="section-header"><h3><i class="fas fa-wallet"></i> Ingresos por Medio</h3></div>
            <div class="list-body medios-pago-body">
              
              <div v-for="(medio, index) in dashboardData.ingresosPorMedio" :key="index" class="medio-item">
                <div class="medio-info">
                  <div class="medio-dot" :style="{ backgroundColor: getMedioColor(index) }"></div>
                  <span class="medio-name">{{ medio.medio }}</span>
                </div>
                <div class="medio-amount">${{ formatNumber(medio.total) }}</div>
                <div class="medio-progress-bg">
                  <div class="medio-progress-fill" :style="{ width: getPorcentajeMedio(medio.total) + '%', backgroundColor: getMedioColor(index) }"></div>
                </div>
              </div>

              <div v-if="!dashboardData.ingresosPorMedio || !dashboardData.ingresosPorMedio.length" class="empty-state">
                No hay cobros registrados
              </div>
              
            </div>
          </div>

        </div>
      </div>
    </main>

    <div id="print-template" style="display: none; width: 850px; min-height: 1100px; background: white; color: #1e293b; padding: 60px; font-family: Arial, sans-serif; position: relative;">
      
      <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #0f172a; padding-bottom: 25px; margin-bottom: 40px;">
        
        <div style="display: flex; align-items: center; gap: 20px;">
          <div style="width: 100px; height: 100px; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; background: #f8fafc;">
            <img v-if="logoBase64" :src="logoBase64" style="width: 100%; height: 100%; object-fit: contain;" />
            <div v-else style="font-weight: bold; color: #0f172a;">LOGO</div>
          </div>
          <div style="text-align: left; line-height: 1.6;">
            <h1 style="margin: 0; font-size: 24px; color: #0f172a; text-transform: uppercase; font-weight: 900;">{{ dashboardData.empresa?.razon_social || 'GESTIÓN' }}</h1>
            <p style="margin: 0; font-size: 12px; color: #334155; font-weight: bold;">CUIT: {{ dashboardData.empresa?.cuil_cuit || '-' }}</p>
            <p style="margin: 0; font-size: 11px; color: #64748b;">DIRECCIÓN: {{ dashboardData.empresa?.direccion || '-' }}</p>
            <p style="margin: 0; font-size: 11px; color: #64748b;">TELÉFONO: {{ dashboardData.empresa?.telefono || '-' }}</p>
            <p style="margin: 0; font-size: 11px; color: #64748b;">EMAIL: {{ dashboardData.empresa?.email || '-' }}</p>
          </div>
        </div>

        <div style="text-align: right;">
          <div style="background: #0f172a; color: white; padding: 10px 15px; font-size: 12px; font-weight: 800; border-radius: 4px; margin-bottom: 12px;">BALANCE DE RENDIMIENTO</div>
          <p style="margin: 0; font-size: 11px; color: #64748b; text-transform: uppercase;">Emitido por:</p>
          <p style="margin: 2px 0 10px; font-size: 13px; font-weight: bold; color: #0f172a;">{{ dashboardData.usuario_emisor || 'ADMINISTRADOR' }}</p>
          <p style="margin: 0; font-size: 11px; color: #64748b;">PERÍODO: <strong>{{ getPeriodDisplay }}</strong></p>
        </div>
      </div>

      <h3 style="font-size: 14px; text-transform: uppercase; border-left: 5px solid #0ea5e9; padding-left: 10px; margin-bottom: 20px; color: #0f172a;">1. Resultados del Período</h3>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 40px;">
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; background: #f8fafc;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Ingresos</span>
          <p style="margin: 10px 0 0; font-size: 20px; font-weight: 900; color: #10b981;">$ {{ formatNumber(dashboardData.ingresosTotales) }}</p>
        </div>
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; background: #fffcfc;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Egresos</span>
          <p style="margin: 10px 0 0; font-size: 20px; font-weight: 900; color: #ef4444;">$ {{ formatNumber(dashboardData.egresosTotales) }}</p>
        </div>
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Ticket Promedio</span>
          <p style="margin: 10px 0 0; font-size: 20px; font-weight: 900; color: #0ea5e9;">$ {{ formatNumber(ticketPromedio) }}</p>
        </div>
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Operaciones</span>
          <p style="margin: 10px 0 0; font-size: 20px; font-weight: 900; color: #0f172a;">{{ getTotalTransactions() }}</p>
        </div>
      </div>

      <h3 style="font-size: 14px; text-transform: uppercase; border-left: 5px solid #0ea5e9; padding-left: 10px; margin-bottom: 20px; color: #0f172a;">2. Análisis Detallado</h3>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px;">
        
        <div>
          <h4 style="font-size: 12px; color: #475569; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Top Servicios</h4>
          <table style="width: 100%; border-collapse: collapse;">
            <tr v-for="s in dashboardData.serviciosTop.slice(0, 5)" :key="s.nombre" style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 10px 0; font-size: 12px;">{{ s.nombre }}</td>
              <td style="padding: 10px 0; font-size: 12px; text-align: right; font-weight: bold;">{{ s.cantidad }} uds.</td>
            </tr>
          </table>
        </div>
        
        <div>
          <h4 style="font-size: 12px; color: #475569; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Top Productos</h4>
          <table style="width: 100%; border-collapse: collapse;">
            <tr v-for="p in dashboardData.productosTop.slice(0, 5)" :key="p.nombre" style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 10px 0; font-size: 12px;">{{ p.nombre }}</td>
              <td style="padding: 10px 0; font-size: 12px; text-align: right; font-weight: bold;">{{ p.cantidad }} uds.</td>
            </tr>
          </table>
        </div>

        <div>
          <h4 style="font-size: 12px; color: #475569; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Ingresos por Medio</h4>
          <table style="width: 100%; border-collapse: collapse;">
            <tr v-for="(m, index) in dashboardData.ingresosPorMedio" :key="m.medio" style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 10px 0; font-size: 12px;">
                <span :style="{ color: getMedioColor(index), fontWeight: 'bold', marginRight: '5px' }">●</span>
                {{ m.medio }}
              </td>
              <td style="padding: 10px 0; font-size: 12px; text-align: right; font-weight: bold;">${{ formatNumber(m.total) }}</td>
            </tr>
          </table>
        </div>

      </div>

      <div style="position: absolute; bottom: 50px; right: 60px; text-align: right;">
        <p style="margin: 0; font-size: 11px; color: #94a3b8; font-weight: bold;">Página 1 de 1</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import axios from '@/utils/axiosConfig'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const logoBase64 = ref(null) 
const selectedPeriod = ref('semana')
const loading = ref(true)
const error = ref(null)
const customDateRange = ref(false)
const dateFrom = ref('')
const dateTo = ref('')
const tooltip = ref({ visible: false, x: 0, y: 0, value: 0, date: '', index: 0 })

const dashboardData = ref({
  ingresosTotales: 0, egresosTotales: 0, serviciosRealizados: 0, productosVendidos: 0,
  ventasPorDia: [], labelsDias: [], serviciosTop: [], productosTop: [],
  ingresosPorMedio: [], // 🔥 ARRAY NUEVO
  usuario_emisor: '', empresa: null, cajaAbierta: true, pendientesInfo: { cantidad: 0, total_dinero: 0 }
})

const ticketPromedio = computed(() => {
  const t = (dashboardData.value.serviciosRealizados || 0) + (dashboardData.value.productosVendidos || 0)
  return t > 0 ? (dashboardData.value.ingresosTotales / t) : 0
})

const getTotalTransactions = () => (dashboardData.value.serviciosRealizados || 0) + (dashboardData.value.productosVendidos || 0)

const getLocalToday = () => {
  const d = new Date()
  const offset = d.getTimezoneOffset()
  return new Date(d.getTime() - (offset*60*1000)).toISOString().split('T')[0]
}
const today = getLocalToday()

const periods = [
  { value: 'hoy', label: 'Hoy', icon: 'fas fa-clock' },
  { value: 'semana', label: '7 Días', icon: 'fas fa-calendar-week' },
  { value: 'mes', label: 'Este Mes', icon: 'fas fa-calendar-alt' },
]

const getPeriodDisplay = computed(() => {
  if (customDateRange.value && dateFrom.value && dateTo.value) return `${formatDate(dateFrom.value)} al ${formatDate(dateTo.value)}`
  const p = periods.find(p => p.value === selectedPeriod.value)
  return p ? p.label : 'Período'
})

// 🔥 COLORES PARA LOS MEDIOS DE PAGO
const medioColors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];
const getMedioColor = (index) => medioColors[index % medioColors.length];

const getPorcentajeMedio = (monto) => {
  if (!dashboardData.value.ingresosTotales) return 0;
  return (monto / dashboardData.value.ingresosTotales) * 100;
}

const convertToBase64 = async (url) => {
  if (!url) return null
  try {
    let finalURL = url
    if (!url.startsWith('http')) {
      const base = axios.defaults.baseURL.replace(/\/$/, '')
      const path = url.startsWith('/') ? url : `/${url}`
      finalURL = base + path
    }

    const response = await axios.get(finalURL, { 
      responseType: 'blob',
      headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
    })
    
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result)
      reader.onerror = (error) => reject(error)
      reader.readAsDataURL(response.data)
    })
  } catch (e) {
    return null
  }
}

const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    let params = customDateRange.value && dateFrom.value && dateTo.value 
      ? { date_from: dateFrom.value, date_to: dateTo.value }
      : { period: selectedPeriod.value }
    
    const [dashboardRes, configRes] = await Promise.all([
      axios.get('/api/dashboard/', { params }),
      axios.get('/api/configuracion/')
    ])
    
    let data = dashboardRes.data
    data.empresa = configRes.data
    
    if (data.empresa && data.empresa.logo) {
        logoBase64.value = await convertToBase64(data.empresa.logo)
    } 
    
    dashboardData.value = data
  } catch (err) {
    error.value = "Error al conectar con el servidor."
  } finally {
    loading.value = false
  }
}

const chartWidth = 900; const chartHeight = 320; const padding = 60;
const formatNumber = (num) => new Intl.NumberFormat('es-AR').format(num || 0)
const formatNumberShort = (num) => num >= 1000 ? (num / 1000).toFixed(1) + 'K' : num
const formatDate = (d) => d ? d.split('-').reverse().join('/') : '-'
const formatDateLong = (d) => d ? new Date(d).toLocaleDateString('es-AR', { day: '2-digit', month: 'long', year: 'numeric' }) : '-'

const getMaxValue = () => {
  const v = dashboardData.value.ventasPorDia;
  return (v && v.length) ? Math.max(...v, 100) : 100;
}
const getXPosition = (i) => padding + (i / ((dashboardData.value.ventasPorDia?.length - 1) || 1)) * (chartWidth - padding * 2)
const getYPosition = (v) => chartHeight - padding - ((v / getMaxValue()) * (chartHeight - padding * 2))
const getXPositionPercent = (i) => (getXPosition(i) / chartWidth) * 100

const getLinePath = () => {
  const v = dashboardData.value.ventasPorDia;
  if (!v || !v.length) return '';
  return v.reduce((p, val, i) => i === 0 ? `M ${getXPosition(i)} ${getYPosition(val)}` : `${p} L ${getXPosition(i)} ${getYPosition(val)}`, '')
}
const getAreaPath = () => {
  const v = dashboardData.value.ventasPorDia;
  if (!v || !v.length) return '';
  return `${getLinePath()} L ${getXPosition(v.length-1)} ${chartHeight-padding} L ${getXPosition(0)} ${chartHeight-padding} Z`
}
const shouldShowLabel = (i) => (dashboardData.value.labelsDias?.length || 0) <= 7 || i % 2 === 0

const selectPeriod = (p) => { customDateRange.value = false; selectedPeriod.value = p; fetchDashboardData() }
const toggleCustomRange = () => { customDateRange.value = !customDateRange.value; if (!customDateRange.value) fetchDashboardData() }
const applyCustomRange = () => { if (dateFrom.value && dateTo.value) fetchDashboardData() }

const showTooltip = (i, v, e) => {
  const rect = e.target.getBoundingClientRect(), container = e.target.closest('.trading-chart-container').getBoundingClientRect()
  tooltip.value = { visible: true, x: rect.left - container.left, y: rect.top - container.top - 90, value: v, date: dashboardData.value.labelsDias[i] }
}
const hideTooltip = () => tooltip.value.visible = false

const generatePDF = async () => {
  loading.value = true
  try {
    if (dashboardData.value.empresa?.logo && !logoBase64.value) {
      logoBase64.value = await convertToBase64(dashboardData.value.empresa.logo)
    }

    await nextTick()
    const el = document.getElementById('print-template')
    if (!el) throw new Error('No se encontró el elemento #print-template')
    
    el.style.display = 'block'
    await new Promise(r => setTimeout(r, 500))

    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      allowTaint: false,
      foreignObjectRendering: false,
    })

    el.style.display = 'none'

    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgData = canvas.toDataURL('image/jpeg', 0.95)
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const imgProps = pdf.getImageProperties(imgData)
    const imgHeight = (imgProps.height * pdfWidth) / imgProps.width

    pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, imgHeight)
    pdf.save(`Balance_Operativo.pdf`)
  } catch (err) {
    console.error('🔴 generatePDF - Error:', err)
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

/* ALERTA HUERFANOS Y CAJA CERRADA */
.alerta-huerfanos { background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; border-radius: 16px; padding: 20px 25px; display: flex; gap: 20px; text-align: left; align-items: flex-start; }
.alerta-huerfanos i { color: #f59e0b; margin-top: 2px; }
.alerta-content strong { display: block; color: #b45309; font-size: 1.2rem; margin-bottom: 5px; text-transform: uppercase;}
.alerta-content p { margin: 0; color: #92400e; font-size: 1rem; line-height: 1.5; }

/* KPI CARDS */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
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
.expense { color: #ef4444; }
.service { color: #3b82f6; }
.product { color: #f97316; }

.kpi-header-card { display: flex; justify-content: space-between; margin-bottom: 1.5rem; }
.kpi-icon { width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; background: rgba(255,255,255,0.05); }
.kpi-data .label { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; display: block; }
.kpi-data .value { font-size: 2.5rem; font-weight: 900; color: white; display: block; margin: 5px 0; }
.kpi-data .subtitle { font-size: 0.85rem; color: #64748b; }

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
.chart-labels { 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  width: 100%; 
  height: 60px; 
  padding: 0 60px;
}
.day-label { 
  position: absolute; 
  transform: translateX(-50%); 
  font-size: 0.8rem; 
  color: #94a3b8; 
  font-weight: 700; 
  text-transform: uppercase;
  white-space: nowrap;
}

.chart-tooltip {
  position: absolute;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 12px;
  pointer-events: none;
  z-index: 1000;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
}

.tooltip-header {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 6px;
  font-weight: 600;
}

.tooltip-value {
  font-size: 1.4rem;
  font-weight: 900;
  color: #ef4444;
}

.tooltip-enter-active, .tooltip-leave-active {
  transition: opacity 0.2s;
}

.tooltip-enter-from, .tooltip-leave-to {
  opacity: 0;
}

/* TOP LISTS */
.top-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
.list-item { display: flex; align-items: center; gap: 1rem; padding: 1.2rem 1.5rem; border-bottom: 1px solid #334155; }
.rank { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; background: #334155; color: #94a3b8; }
.item-content { flex: 1; }
.item-name { font-weight: 700; color: #f1f5f9; margin-bottom: 5px; }
.item-count { font-weight: 900; color: #f1f5f9; font-size: 1.1rem; }
.empty-state { padding: 2rem; text-align: center; color: #64748b; font-style: italic; }

/* BARRAS MEDIO DE PAGO */
.medios-pago-body { padding: 1rem 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
.medio-item { display: flex; flex-direction: column; gap: 8px; }
.medio-info { display: flex; align-items: center; gap: 10px; }
.medio-dot { width: 12px; height: 12px; border-radius: 50%; }
.medio-name { font-weight: 600; color: #e2e8f0; font-size: 0.95rem; }
.medio-amount { text-align: right; font-weight: 800; font-size: 1.1rem; color: #f8fafc; margin-top: -20px; }
.medio-progress-bg { width: 100%; height: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 4px; overflow: hidden; }
.medio-progress-fill { height: 100%; border-radius: 4px; transition: width 1s ease-in-out; }

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
.fade-in {
  animation: fadeIn 0.5s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chart-line-red {
  animation: drawLine 1.5s ease-out;
}

@keyframes drawLine {
  from { stroke-dasharray: 2000; stroke-dashoffset: 2000; }
  to { stroke-dasharray: 2000; stroke-dashoffset: 0; }
}

.chart-point-red {
  transition: all 0.2s;
}

.chart-point-red:hover {
  r: 8;
  filter: drop-shadow(0 0 8px #ef4444);
}


/* ============ MODO CLARO ============ */
:root.light-theme .dashboard-wrapper {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  color: #0f172a;
}
:root.light-theme .dashboard-header {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(203, 213, 225, 0.5);
  box-shadow: 0 2px 16px rgba(100, 116, 139, 0.08);
}
:root.light-theme .dashboard-title {
  background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
:root.light-theme .dashboard-subtitle { color: #64748b; }
:root.light-theme .period-selector { background: rgba(248, 250, 252, 0.95); border: 1px solid #cbd5e1; }
:root.light-theme .period-selector button { color: #475569; }
:root.light-theme .period-selector button.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white;
}
:root.light-theme .kpi-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0;
}
:root.light-theme .kpi-icon { background: rgba(0, 0, 0, 0.03); }
:root.light-theme .kpi-data .label { color: #64748b; }
:root.light-theme .kpi-data .value { color: #0f172a; }
:root.light-theme .kpi-data .subtitle { color: #94a3b8; }
:root.light-theme .section-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0;
}
:root.light-theme .section-header { border-bottom: 1px solid #e2e8f0; }
:root.light-theme .section-header h3 { color: #0f172a; }
:root.light-theme .day-label { color: #475569; }
:root.light-theme .chart-tooltip { background: rgba(255, 255, 255, 0.98); border: 1px solid #cbd5e1; }
:root.light-theme .tooltip-header { color: #64748b; }
:root.light-theme .list-item { border-bottom: 1px solid #e2e8f0; }
:root.light-theme .rank { background: #e2e8f0; color: #64748b; }
:root.light-theme .item-name { color: #0f172a; }
:root.light-theme .item-count { color: #0f172a; }
:root.light-theme .custom-date-content { background: #ffffff; border: 1px solid #e2e8f0; }
:root.light-theme .date-input-group label { color: #475569; }
:root.light-theme .date-input-custom { background: #f8fafc; border: 2px solid #cbd5e1; color: #0f172a; }
:root.light-theme .date-range-info { background: rgba(248, 250, 252, 0.95); color: #64748b; }
:root.light-theme .medio-name { color: #0f172a; }
:root.light-theme .medio-amount { color: #0f172a; }
:root.light-theme .medio-progress-bg { background: #e2e8f0; }
</style>