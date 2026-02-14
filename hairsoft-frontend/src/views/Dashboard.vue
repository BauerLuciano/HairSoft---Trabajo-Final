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
      <div class="kpi-grid">
        <div class="kpi-card income">
          <div class="kpi-header-card"><div class="kpi-icon"><i class="fas fa-dollar-sign"></i></div></div>
          <div class="kpi-data">
            <span class="label">Ingresos Totales</span>
            <span class="value">${{ formatNumber(dashboardData.ingresosTotales) }}</span>
            <span class="subtitle">Facturación bruta</span>
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
        <h3 class="section-title"><i class="fas fa-trophy"></i> Desempeño Comercial</h3>
        <div class="top-grid">
          <div class="section-card top-card">
            <div class="section-header"><h3><i class="fas fa-star"></i> Servicios Top</h3></div>
            <div class="list-body">
              <div class="list-item" v-for="(s, i) in dashboardData.serviciosTop" :key="i">
                <div class="rank">{{ i + 1 }}</div>
                <div class="item-content"><div class="item-name">{{ s.nombre }}</div></div>
                <div class="item-count">{{ s.cantidad }}</div>
              </div>
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
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px;">
        <div style="padding: 25px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; background: #f8fafc;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Ingresos Totales</span>
          <p style="margin: 10px 0 0; font-size: 22px; font-weight: 900; color: #10b981;">$ {{ formatNumber(dashboardData.ingresosTotales) }}</p>
        </div>
        <div style="padding: 25px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Ticket Promedio</span>
          <p style="margin: 10px 0 0; font-size: 22px; font-weight: 900; color: #0ea5e9;">$ {{ formatNumber(ticketPromedio) }}</p>
        </div>
        <div style="padding: 25px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Operaciones</span>
          <p style="margin: 10px 0 0; font-size: 24px; font-weight: 900; color: #0f172a;">{{ getTotalTransactions() }}</p>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
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
  ingresosTotales: 0, serviciosRealizados: 0, productosVendidos: 0,
  ventasPorDia: [], labelsDias: [], serviciosTop: [], productosTop: [],
  usuario_emisor: '', empresa: null
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

// ✅ CONVERSOR MEJORADO CON LOGS Y MANEJO DE ERRORES
const convertToBase64 = async (url) => {
  if (!url) {
    console.warn('convertToBase64: URL vacía')
    return null
  }
  try {
    console.log('🟡 convertToBase64 - URL original:', url)
    // Construir URL absoluta si es relativa
    let finalURL = url
    if (!url.startsWith('http')) {
      const base = axios.defaults.baseURL.replace(/\/$/, '')
      const path = url.startsWith('/') ? url : `/${url}`
      finalURL = base + path
    }
    console.log('🟡 convertToBase64 - URL final:', finalURL)

    const response = await axios.get(finalURL, { 
      responseType: 'blob',
      // Asegurar token por si acaso (aunque el interceptor ya lo hace)
      headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
    })
    
    console.log('🟢 convertToBase64 - Blob recibido, tipo:', response.data.type, 'tamaño:', response.data.size)

    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        console.log('🟢 convertToBase64 - Base64 generado (primeros 50):', reader.result.substring(0, 50))
        resolve(reader.result)
      }
      reader.onerror = (error) => {
        console.error('🔴 convertToBase64 - Error leyendo blob:', error)
        reject(error)
      }
      reader.readAsDataURL(response.data)
    })
  } catch (e) {
    console.error('🔴 convertToBase64 - Error en Axios:', e)
    if (e.response) {
      console.error('Status:', e.response.status)
      console.error('Data:', e.response.data)
    }
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
    
    // Hacer ambas peticiones en paralelo
    const [dashboardRes, configRes] = await Promise.all([
      axios.get('/api/dashboard/', { params }),
      axios.get('/api/configuracion/')
    ])
    
    let data = dashboardRes.data
    // Sobrescribir empresa con la de configuración (que tiene el logo)
    data.empresa = configRes.data
    
    console.log('🟢 fetchDashboardData - datos empresa (con logo):', data.empresa)

    // Convertir el logo a Base64
    if (data.empresa && data.empresa.logo) {
        logoBase64.value = await convertToBase64(data.empresa.logo)
        console.log('🟢 fetchDashboardData - logoBase64 asignado:', logoBase64.value ? 'OK' : 'VACÍO')
    } else {
        console.warn('fetchDashboardData - No hay logo en empresa')
    }
    
    dashboardData.value = data
  } catch (err) {
    console.error('🔴 fetchDashboardData - Error:', err)
    error.value = "Error al conectar con el servidor."
  } finally {
    loading.value = false
  }
}

// LÓGICA DE GRÁFICOS (SIN MODIFICAR)
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

// NAVEGACIÓN
const selectPeriod = (p) => { customDateRange.value = false; selectedPeriod.value = p; fetchDashboardData() }
const toggleCustomRange = () => { customDateRange.value = !customDateRange.value; if (!customDateRange.value) fetchDashboardData() }
const applyCustomRange = () => { if (dateFrom.value && dateTo.value) fetchDashboardData() }

const showTooltip = (i, v, e) => {
  const rect = e.target.getBoundingClientRect(), container = e.target.closest('.trading-chart-container').getBoundingClientRect()
  tooltip.value = { visible: true, x: rect.left - container.left, y: rect.top - container.top - 90, value: v, date: dashboardData.value.labelsDias[i] }
}
const hideTooltip = () => tooltip.value.visible = false

// ✅ GENERACIÓN DE PDF CORREGIDA Y MEJORADA
const generatePDF = async () => {
  loading.value = true
  console.log('🟡 generatePDF - Iniciando...')

  try {
    // 1. Asegurar que el logo esté cargado
    if (dashboardData.value.empresa?.logo && !logoBase64.value) {
      console.log('🟡 generatePDF - Logo no cargado, forzando carga...')
      logoBase64.value = await convertToBase64(dashboardData.value.empresa.logo)
    }

    console.log('🟡 generatePDF - logoBase64 después de carga:', logoBase64.value ? 'OK' : 'VACÍO')

    // 2. Esperar a que Vue actualice el DOM
    await nextTick()

    // 3. Mostrar el template oculto
    const el = document.getElementById('print-template')
    if (!el) {
      throw new Error('No se encontró el elemento #print-template')
    }
    el.style.display = 'block'
    console.log('🟡 generatePDF - Template mostrado')

    // 4. Dar tiempo para que la imagen se renderice (especialmente si es Base64)
    await new Promise(r => setTimeout(r, 500))

    // 5. Verificar que el img tenga el src
    const imgElement = el.querySelector('img')
    console.log('🟡 generatePDF - src del img en template:', imgElement ? (imgElement.src ? imgElement.src.substring(0, 50) + '...' : 'src vacío') : 'no img')

    // 6. Generar canvas con opciones mejoradas
    console.log('🟡 generatePDF - Generando canvas...')
    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: true, // Activamos logging para ver problemas en consola
      allowTaint: false,
      foreignObjectRendering: false,
      onclone: (clonedDoc, element) => {
        // Podemos verificar que el logo esté en el clon
        const clonedImg = element.querySelector('img')
        console.log('🟡 html2canvas onclone - img src:', clonedImg ? clonedImg.src.substring(0,50) : 'no img')
      }
    })
    console.log('🟢 generatePDF - Canvas generado')

    // 7. Ocultar el template
    el.style.display = 'none'

    // 8. Crear PDF y agregar imagen
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgData = canvas.toDataURL('image/jpeg', 0.95)
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const imgProps = pdf.getImageProperties(imgData)
    const imgHeight = (imgProps.height * pdfWidth) / imgProps.width

    pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, imgHeight)
    pdf.save(`Balance_Operativo.pdf`)
    console.log('🟢 generatePDF - PDF guardado')
  } catch (err) {
    console.error('🔴 generatePDF - Error:', err)
    // Podrías mostrar una notificación al usuario
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

/* KPI Summary PDF */
.pdf-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
}

.no-data i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
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

.pie-sector {
  transition: opacity 0.3s;
}

.pie-sector:hover {
  opacity: 0.8;
}

/* ============ MODO CLARO (AGREGAR AL FINAL DEL <style>) ============ */

/* Wrapper principal */
:root.light-theme .dashboard-wrapper {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  color: #0f172a;
}

/* Header */
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

:root.light-theme .dashboard-subtitle {
  color: #64748b;
}

:root.light-theme .period-selector {
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid #cbd5e1;
}

:root.light-theme .period-selector button {
  color: #475569;
}

:root.light-theme .period-selector button.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

/* KPI Cards */
:root.light-theme .kpi-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

:root.light-theme .kpi-card:hover {
  box-shadow: 0 8px 24px rgba(100, 116, 139, 0.15);
}

:root.light-theme .kpi-icon {
  background: rgba(0, 0, 0, 0.03);
}

:root.light-theme .kpi-data .label {
  color: #64748b;
}

:root.light-theme .kpi-data .value {
  color: #0f172a;
}

:root.light-theme .kpi-data .subtitle {
  color: #94a3b8;
}

/* Sections */
:root.light-theme .section-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

:root.light-theme .section-header {
  border-bottom: 1px solid #e2e8f0;
}

:root.light-theme .section-header h3 {
  color: #0f172a;
}

:root.light-theme .chart-body {
  background: rgba(248, 250, 252, 0.3);
}

/* Chart labels y grid */
:root.light-theme .day-label {
  color: #475569;
}

:root.light-theme .chart-tooltip {
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid #cbd5e1;
  box-shadow: 0 8px 24px rgba(100, 116, 139, 0.15);
}

:root.light-theme .tooltip-header {
  color: #64748b;
}

/* Distribution */
:root.light-theme .legend-item {
  background: rgba(248, 250, 252, 0.8);
}

:root.light-theme .legend-label {
  color: #0f172a;
}

:root.light-theme .legend-value {
  color: #64748b;
}

/* Top Lists */
:root.light-theme .list-item {
  border-bottom: 1px solid #e2e8f0;
}

:root.light-theme .list-item:hover {
  background: rgba(248, 250, 252, 0.8);
}

:root.light-theme .rank {
  background: #e2e8f0;
  color: #64748b;
}

:root.light-theme .item-name {
  color: #0f172a;
}

:root.light-theme .progress-bar {
  background: rgba(203, 213, 225, 0.3);
}

:root.light-theme .item-count {
  color: #0f172a;
}

/* Date picker */
:root.light-theme .custom-date-content {
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

:root.light-theme .date-input-group label {
  color: #475569;
}

:root.light-theme .date-input-custom {
  background: #f8fafc;
  border: 2px solid #cbd5e1;
  color: #0f172a;
}

:root.light-theme .date-input-custom:focus {
  border-color: #3b82f6;
  background: #ffffff;
}

:root.light-theme .date-range-info {
  background: rgba(248, 250, 252, 0.95);
  color: #64748b;
}

:root.light-theme .date-range-info strong {
  color: #0f172a;
}

/* Loader */
:root.light-theme .state-container {
  color: #64748b;
}

:root.light-theme .loader {
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
}

:root.light-theme .loading-text {
  color: #475569;
}

:root.light-theme .error-content h3 {
  color: #0f172a;
}

/* Section title */
:root.light-theme .section-title {
  color: #0f172a;
}

:root.light-theme .chart-legend {
  color: #64748b;
}

:root.light-theme .no-data {
  color: #94a3b8;
}

/* Chart info */
:root.light-theme .chart-info {
  color: #64748b;
}
</style>