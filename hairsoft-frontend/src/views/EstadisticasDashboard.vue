<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">Reportes Estratégicos</h1>
        <p class="dashboard-subtitle">Análisis financiero y rendimiento del local</p>
      </div>
      <div class="header-right">
        <div class="period-selector">
          <button v-for="opt in periodOptions" :key="opt.value" :class="{ active: filtros.periodo === opt.value }" @click="setPeriod(opt.value)">
            <i :class="opt.icon"></i> {{ opt.label }}
          </button>
        </div>
        <div v-if="filtros.periodo === 'custom'" class="custom-date-panel">
          <input type="date" v-model="filtros.fecha_inicio" class="date-input-custom" />
          <span class="date-separator">→</span>
          <input type="date" v-model="filtros.fecha_fin" class="date-input-custom" />
        </div>
        <button class="apply-btn" @click="cargarEstadisticas" :disabled="loading || isGeneratingPDF">
          <i class="ri-refresh-line" :class="{ 'rotating': loading }"></i> {{ loading ? 'Analizando...' : 'Analizar' }}
        </button>
        
        <button class="pdf-btn" @click="generatePDF" :disabled="loading || isGeneratingPDF || !stats">
          <i class="ri-file-download-line" :class="{ 'rotating': isGeneratingPDF }"></i> 
          {{ isGeneratingPDF ? 'Exportando...' : 'Exportar Reporte' }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="state-container">
      <div class="loader"></div>
      <p>Procesando datos...</p>
    </div>

    <div v-else-if="error" class="alerta-huerfanos">
      <i class="ri-error-warning-line"></i>
      <div class="alerta-content">
        <strong>Error de conexión</strong>
        <p>{{ error }}</p>
        <button @click="cargarEstadisticas" style="margin-top: 10px; background: transparent; border: 1px solid #ef4444; color: #ef4444; padding: 5px 10px; border-radius: 6px; cursor: pointer;">Reintentar</button>
      </div>
    </div>

    <div v-else-if="stats" class="fade-in" id="dashboard-content">
      
      <div class="kpi-grid">
        <div class="kpi-card income-card">
          <div class="kpi-icon"><i class="ri-money-dollar-circle-line"></i></div>
          <div class="kpi-info">
            <span class="kpi-label">Facturación Total Bruta</span>
            <span class="kpi-value">{{ formatCurrency(stats.kpis.ingreso_total) }}</span>
            <span class="kpi-subtext">Ticket Promedio: <strong>{{ formatCurrency(stats.kpis.ticket_promedio) }}</strong></span>
          </div>
        </div>

        <div class="kpi-card turnos-card">
          <div class="kpi-icon"><i class="ri-user-heart-line"></i></div>
          <div class="kpi-info">
            <span class="kpi-label">Retención de Clientes</span>
            <span class="kpi-value">{{ stats.kpis.fidelidad.tasa }}% <small class="text-sm">Vuelven</small></span>
            <span class="kpi-subtext">Nuevos: <strong>{{ stats.kpis.fidelidad.nuevos }}</strong> | Recurrentes: <strong>{{ stats.kpis.fidelidad.recurrentes }}</strong></span>
          </div>
        </div>

        <div class="kpi-card stars-card">
          <div class="kpi-icon"><i class="ri-star-smile-line"></i></div>
          <div class="kpi-info" style="width: 100%;">
            <span class="kpi-label">Los Más Elegidos</span>
            
            <div class="favorite-item">
              <span class="favorite-title">
                <span class="fav-label"><i class="ri-scissors-cut-line service-icon"></i> Servicio:</span> 
                <strong class="fav-name">{{ stats.kpis.servicio_estrella.nombre }}</strong>
              </span>
              <span class="favorite-details" v-if="stats.kpis.servicio_estrella.nombre !== 'Ninguno'">
                {{ stats.kpis.servicio_estrella.cantidad }} realizados &bull; <span class="income">{{ formatCurrency(stats.kpis.servicio_estrella.ingreso) }}</span>
              </span>
            </div>

            <div class="favorite-item">
              <span class="favorite-title">
                <span class="fav-label"><i class="ri-shopping-bag-line product-icon"></i> Producto:</span> 
                <strong class="fav-name">{{ stats.kpis.producto_estrella.nombre }}</strong>
              </span>
              <span class="favorite-details" v-if="stats.kpis.producto_estrella.nombre !== 'Ninguno'">
                {{ stats.kpis.producto_estrella.cantidad }} vendidos &bull; <span class="income">{{ formatCurrency(stats.kpis.producto_estrella.ingreso) }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="section-card chart-card">
          <div class="section-header"><h3>💸 Origen de Ingresos (Reservas)</h3></div>
          <div class="chart-layout">
            <div class="chart-box">
              <canvas ref="turnosChartCanvas" :style="{ opacity: (ingresosTurnos > 0 || ingresosSenas > 0) ? 1 : 0 }"></canvas>
              <div class="chart-empty-message" v-if="ingresosTurnos === 0 && ingresosSenas === 0">Sin datos en estas fechas.</div>
            </div>
            <div class="chart-summary" v-if="ingresosTurnos > 0 || ingresosSenas > 0">
              <div class="summary-item">
                <span class="summary-dot" style="background-color: #10b981;"></span>
                <div class="summary-info">
                  <span class="summary-label">Turnos Completados</span>
                  <span class="summary-value">{{ formatCurrency(ingresosTurnos) }}</span>
                </div>
              </div>
              <div class="summary-item mt-3">
                <span class="summary-dot" style="background-color: #f59e0b;"></span>
                <div class="summary-info">
                  <span class="summary-label">Señas Retenidas</span>
                  <span class="summary-value">{{ formatCurrency(ingresosSenas) }}</span>
                </div>
              </div>
              <div class="summary-item total mt-4">
                <div class="summary-info">
                  <span class="summary-label">TOTAL ORIGEN</span>
                  <span class="summary-value">{{ formatCurrency(ingresosTurnos + ingresosSenas) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="section-card chart-card">
          <div class="section-header"><h3>💳 Distribución por Medio de Pago</h3></div>
          <div class="chart-layout">
            <div class="chart-box">
              <canvas ref="pagosChartCanvas" :style="{ opacity: stats.graficos.medios_pago.length > 0 ? 1 : 0 }"></canvas>
              <div class="chart-empty-message" v-if="stats.graficos.medios_pago.length === 0">No hay pagos registrados.</div>
            </div>
            
            <div class="chart-summary" v-if="stats.graficos.medios_pago.length > 0">
              <div class="summary-item" v-for="(item, idx) in stats.graficos.medios_pago" :key="idx" :class="{ 'mt-3': idx > 0 }">
                <span class="summary-dot" style="background-color: #3b82f6;"></span>
                <div class="summary-info">
                  <span class="summary-label">{{ item.medio }}</span>
                  <span class="summary-value">{{ formatCurrency(item.total) }}</span>
                </div>
              </div>
              
              <div class="summary-item total mt-4">
                <div class="summary-info">
                  <span class="summary-label">TOTAL PAGOS</span>
                  <span class="summary-value">{{ formatCurrency(stats.graficos.medios_pago.reduce((a, c) => a + c.total, 0)) }}</span>
                </div>
              </div>
            </div>
            
          </div>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h3>🛡️ Ingresos por Cancelaciones (Señas Retenidas)</h3>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Servicio</th>
                <th class="text-right">Monto Retenido</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in stats.tablas.penalizaciones" :key="idx">
                <td>{{ item.fecha }}</td>
                <td class="item-name">{{ item.cliente }}</td>
                <td>{{ item.servicio }}</td>
                <td class="text-right item-count income">+ {{ formatCurrency(item.monto_retenido) }}</td>
              </tr>
              <tr v-if="!stats.tablas.penalizaciones.length">
                <td colspan="4" class="empty-state">No hubo cancelaciones con retención de seña en este período.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h3>📦 Top 5: Stock Estancado (Capital Inmovilizado)</h3>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Marca</th>
                <th class="text-center">Stock Actual</th>
                <th class="text-right">Capital Parado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in stats.tablas.stock_estancado" :key="idx">
                <td class="item-name">{{ item.producto }}</td>
                <td>{{ item.marca }}</td>
                <td class="text-center"><span class="badge-neutral">{{ item.stock }}</span></td>
                <td class="text-right expense">{{ formatCurrency(item.capital) }}</td>
              </tr>
              <tr v-if="!stats.tablas.stock_estancado.length">
                <td colspan="4" class="empty-state">Excelente rotación. Todos los productos se movieron.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div id="print-template" style="display: none; width: 850px; min-height: 1100px; background: white; color: #1e293b; padding: 60px; font-family: Arial, sans-serif; position: relative;">
      
      <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #0f172a; padding-bottom: 25px; margin-bottom: 40px;">
        <div style="display: flex; align-items: center; gap: 20px;">
          <div style="width: 100px; height: 100px; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; background: #f8fafc;">
            <img v-if="logoBase64" :src="logoBase64" style="width: 100%; height: 100%; object-fit: contain;" />
            <div v-else style="font-weight: bold; color: #0f172a;">LOGO</div>
          </div>
          <div style="text-align: left; line-height: 1.6;">
            <h1 style="margin: 0; font-size: 24px; color: #0f172a; text-transform: uppercase; font-weight: 900;">{{ empresaData?.razon_social || 'GESTIÓN' }}</h1>
            <p style="margin: 0; font-size: 12px; color: #334155; font-weight: bold;">CUIT: {{ empresaData?.cuil_cuit || '-' }}</p>
            <p style="margin: 0; font-size: 11px; color: #64748b;">DIRECCIÓN: {{ empresaData?.direccion || '-' }}</p>
            <p style="margin: 0; font-size: 11px; color: #64748b;">TELÉFONO: {{ empresaData?.telefono || '-' }}</p>
            <p style="margin: 0; font-size: 11px; color: #64748b;">EMAIL: {{ empresaData?.email || '-' }}</p>
          </div>
        </div>

        <div style="text-align: right;">
          <div style="background: #0f172a; color: white; padding: 10px 15px; font-size: 12px; font-weight: 800; border-radius: 4px; margin-bottom: 12px;">REPORTE ADMINISTRATIVO</div>
          <p style="margin: 0; font-size: 11px; color: #64748b; text-transform: uppercase;">Emitido por:</p>
          <p style="margin: 2px 0 10px; font-size: 13px; font-weight: bold; color: #0f172a;">{{ usuarioEmisor || 'Administrador' }}</p>
          <p style="margin: 0; font-size: 11px; color: #64748b;">PERÍODO: <strong>{{ getPeriodDisplay }}</strong></p>
          <p style="margin: 4px 0 0; font-size: 11px; color: #64748b;">FECHA DE EMISIÓN: <strong>{{ getFechaEmision() }}</strong></p>
        </div>
      </div>

      <h3 style="font-size: 14px; text-transform: uppercase; border-left: 5px solid #0ea5e9; padding-left: 10px; margin-bottom: 20px; color: #0f172a;">1. Indicadores Clave</h3>
      <div v-if="stats" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 40px;">
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; background: #f8fafc;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Facturación Bruta</span>
          <p style="margin: 10px 0 0; font-size: 18px; font-weight: 900; color: #10b981;">{{ formatCurrency(stats.kpis.ingreso_total) }}</p>
          <p style="margin: 5px 0 0; font-size: 10px; color: #64748b;">Ticket Prom: {{ formatCurrency(stats.kpis.ticket_promedio) }}</p>
        </div>
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; background: #f8fafc;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Retención Clientes</span>
          <p style="margin: 10px 0 0; font-size: 18px; font-weight: 900; color: #0ea5e9;">{{ stats.kpis.fidelidad.tasa }}%</p>
          <p style="margin: 5px 0 0; font-size: 10px; color: #64748b;">Recurrentes: {{ stats.kpis.fidelidad.recurrentes }} | Nuevos: {{ stats.kpis.fidelidad.nuevos }}</p>
        </div>
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; background: #f8fafc;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Servicio Estrella</span>
          <p style="margin: 10px 0 0; font-size: 14px; font-weight: 900; color: #3b82f6;">{{ stats.kpis.servicio_estrella.nombre }}</p>
          <p style="margin: 5px 0 0; font-size: 10px; color: #64748b;">{{ stats.kpis.servicio_estrella.cantidad }} usos | {{ formatCurrency(stats.kpis.servicio_estrella.ingreso) }}</p>
        </div>
        <div style="padding: 20px 15px; border: 1px solid #e2e8f0; border-radius: 12px; text-align: center; background: #f8fafc;">
          <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 800;">Producto Estrella</span>
          <p style="margin: 10px 0 0; font-size: 14px; font-weight: 900; color: #f97316;">{{ stats.kpis.producto_estrella.nombre }}</p>
          <p style="margin: 5px 0 0; font-size: 10px; color: #64748b;">{{ stats.kpis.producto_estrella.cantidad }} vent. | {{ formatCurrency(stats.kpis.producto_estrella.ingreso) }}</p>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px;">
        <div>
          <h3 style="font-size: 14px; text-transform: uppercase; border-left: 5px solid #f59e0b; padding-left: 10px; margin-bottom: 15px; color: #0f172a;">2. Origen de Ingresos</h3>
          <img id="pdf-chart-torta" style="width: 100%; max-height: 250px; object-fit: contain; margin-bottom: 10px;" />
          <div v-if="stats" style="font-size: 11px; color: #334155; line-height: 1.5;">
            <strong>Turnos Completados:</strong> {{ formatCurrency(ingresosTurnos) }}<br>
            <strong>Señas Retenidas:</strong> {{ formatCurrency(ingresosSenas) }}<br>
            <strong style="color: #0f172a; display: block; margin-top: 5px; font-size: 12px;">TOTAL ORIGEN: {{ formatCurrency(ingresosTurnos + ingresosSenas) }}</strong>
          </div>
        </div>
        <div>
          <h3 style="font-size: 14px; text-transform: uppercase; border-left: 5px solid #3b82f6; padding-left: 10px; margin-bottom: 15px; color: #0f172a;">3. Medios de Pago</h3>
          <img id="pdf-chart-barras" style="width: 100%; max-height: 250px; object-fit: contain; margin-bottom: 10px;" />
          <div v-if="stats" style="font-size: 11px; color: #334155; line-height: 1.5;">
            <span v-for="item in stats.graficos.medios_pago" :key="item.medio">
              <strong>{{ item.medio }}:</strong> {{ formatCurrency(item.total) }}<br>
            </span>
            <strong style="color: #0f172a; display: block; margin-top: 5px; font-size: 12px;">TOTAL PAGOS: {{ formatCurrency(stats.graficos.medios_pago.reduce((a,c) => a + c.total, 0)) }}</strong>
          </div>
        </div>
      </div>

      <div v-if="stats">
        <h3 style="font-size: 14px; text-transform: uppercase; border-left: 5px solid #ef4444; padding-left: 10px; margin-bottom: 20px; color: #0f172a;">4. Stock Estancado (Top 5)</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
          <thead>
            <tr style="background: #0f172a; color: white;">
              <th style="padding: 10px; text-align: left; font-size: 10px;">PRODUCTO</th>
              <th style="padding: 10px; text-align: left; font-size: 10px;">MARCA</th>
              <th style="padding: 10px; text-align: center; font-size: 10px;">STOCK</th>
              <th style="padding: 10px; text-align: right; font-size: 10px;">CAPITAL PARADO</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in stats.tablas.stock_estancado" :key="idx" style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px; font-size: 11px;">{{ item.producto }}</td>
              <td style="padding: 10px; font-size: 11px;">{{ item.marca }}</td>
              <td style="padding: 10px; text-align: center; font-size: 11px; font-weight: bold;">{{ item.stock }}</td>
              <td style="padding: 10px; text-align: right; font-size: 11px; color: #ef4444; font-weight: bold;">{{ formatCurrency(item.capital) }}</td>
            </tr>
            <tr v-if="!stats.tablas.stock_estancado.length">
              <td colspan="4" style="padding: 20px; text-align: center; font-size: 11px; color: #64748b; font-style: italic;">Excelente rotación. Todos los productos se movieron.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="stats">
        <h3 style="font-size: 14px; text-transform: uppercase; border-left: 5px solid #10b981; padding-left: 10px; margin-bottom: 20px; color: #0f172a;">5. Señas Retenidas (Cancelaciones)</h3>
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="background: #0f172a; color: white;">
              <th style="padding: 10px; text-align: left; font-size: 10px;">FECHA</th>
              <th style="padding: 10px; text-align: left; font-size: 10px;">CLIENTE</th>
              <th style="padding: 10px; text-align: left; font-size: 10px;">SERVICIO</th>
              <th style="padding: 10px; text-align: right; font-size: 10px;">MONTO</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in stats.tablas.penalizaciones" :key="idx" style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px; font-size: 11px;">{{ item.fecha }}</td>
              <td style="padding: 10px; font-size: 11px;">{{ item.cliente }}</td>
              <td style="padding: 10px; font-size: 11px;">{{ item.servicio }}</td>
              <td style="padding: 10px; text-align: right; font-size: 11px; color: #10b981; font-weight: bold;">+ {{ formatCurrency(item.monto_retenido) }}</td>
            </tr>
            <tr v-if="!stats.tablas.penalizaciones.length">
              <td colspan="4" style="padding: 20px; text-align: center; font-size: 11px; color: #64748b; font-style: italic;">No hubo cancelaciones con retención de seña en este período.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import axios from '@/utils/axiosConfig'; 
import Chart from 'chart.js/auto';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const filtros = ref({ fecha_inicio: '', fecha_fin: '', periodo: 'month' });
const stats = ref(null);
const loading = ref(false);
const error = ref(null);
const isGeneratingPDF = ref(false);

const turnosChartCanvas = ref(null);
const pagosChartCanvas = ref(null);
let turnosChartInstance = null;
let pagosChartInstance = null;

const logoBase64 = ref(null);
const empresaData = ref(null);
const usuarioEmisor = ref(null);

const periodOptions = [
  { value: 'today', label: 'Hoy', icon: 'ri-calendar-today-line' },
  { value: 'week', label: 'Esta semana', icon: 'ri-calendar-week-line' },
  { value: 'month', label: 'Este mes', icon: 'ri-calendar-month-line' },
  { value: 'custom', label: 'Personalizado', icon: 'ri-settings-4-line' }
];

// 🔥 VARIABLES COMPUTADAS PARA EXTRAER INGRESOS
const ingresosTurnos = computed(() => {
  if (!stats.value || !stats.value.graficos.turnos_ingresos) return 0;
  const turnoObj = stats.value.graficos.turnos_ingresos.find(i => i.label === 'Turnos Completados');
  return turnoObj ? turnoObj.total : 0;
});

const ingresosSenas = computed(() => {
  if (!stats.value || !stats.value.graficos.turnos_ingresos) return 0;
  const senaObj = stats.value.graficos.turnos_ingresos.find(i => i.label === 'Señas Retenidas');
  return senaObj ? senaObj.total : 0;
});

const formatCurrency = (v) => {
  if (!v || isNaN(v)) return '$ 0,00';
  return `$ ${parseFloat(v).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

const getFechaEmision = () => {
  const d = new Date();
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' }) + ' ' + d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
};

const getPeriodDisplay = computed(() => {
  if (filtros.value.periodo === 'custom' && filtros.value.fecha_inicio && filtros.value.fecha_fin) {
    const f1 = filtros.value.fecha_inicio.split('-').reverse().join('/');
    const f2 = filtros.value.fecha_fin.split('-').reverse().join('/');
    return `${f1} al ${f2}`;
  }
  const p = periodOptions.find(opt => opt.value === filtros.value.periodo);
  return p ? p.label : 'Período';
});

const setPeriod = (period) => {
  filtros.value.periodo = period;
  if (period !== 'custom') aplicarPeriodoRapido();
};

const aplicarPeriodoRapido = () => {
  const hoy = new Date();
  const fin = hoy.toISOString().split('T')[0];
  let inicio = '';

  switch (filtros.value.periodo) {
    case 'today': inicio = fin; break;
    case 'week':
      const semana = new Date(hoy);
      semana.setDate(hoy.getDate() - 7);
      inicio = semana.toISOString().split('T')[0];
      break;
    case 'month':
      const mes = new Date(hoy);
      mes.setMonth(hoy.getMonth() - 1);
      inicio = mes.toISOString().split('T')[0];
      break;
    default: return;
  }
  filtros.value.fecha_inicio = inicio;
  filtros.value.fecha_fin = fin;
  cargarEstadisticas();
};

const convertToBase64 = async (url) => {
  if (!url) return null;
  try {
    let finalURL = url;
    if (!url.startsWith('http')) {
      const base = axios.defaults.baseURL ? axios.defaults.baseURL.replace(/\/$/, '') : '';
      const path = url.startsWith('/') ? url : `/${url}`;
      finalURL = base + path;
    }
    const response = await axios.get(finalURL, { 
      responseType: 'blob',
      headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
    });
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(response.data);
    });
  } catch (e) {
    return null;
  }
};

const renderCharts = async () => {
  await nextTick();
  if (!stats.value) return;

  if (turnosChartInstance) turnosChartInstance.destroy();
  if (pagosChartInstance) pagosChartInstance.destroy();

  const style = getComputedStyle(document.documentElement);
  const textColor = style.getPropertyValue('--text-tertiary').trim() || '#94a3b8';
  const gridColor = style.getPropertyValue('--border-color').trim() || '#334155';

  if (turnosChartCanvas.value && (ingresosTurnos.value > 0 || ingresosSenas.value > 0)) {
    turnosChartInstance = new Chart(turnosChartCanvas.value, {
      type: 'doughnut',
      data: {
        labels: stats.value.graficos.turnos_ingresos.map(i => i.label),
        datasets: [{
          data: stats.value.graficos.turnos_ingresos.map(i => i.total),
          backgroundColor: stats.value.graficos.turnos_ingresos.map(i => i.color),
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        animation: { duration: 0 }, 
        plugins: { 
          legend: { display: false }, 
          tooltip: { callbacks: { label: (context) => ' ' + formatCurrency(context.raw || 0) } }
        },
        cutout: '75%'
      }
    });
  }

  if (pagosChartCanvas.value && stats.value.graficos.medios_pago.length > 0) {
    const labels = stats.value.graficos.medios_pago.map(m => m.medio);
    const data = stats.value.graficos.medios_pago.map(m => m.total);

    pagosChartInstance = new Chart(pagosChartCanvas.value, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Monto Ingresado', data: data, backgroundColor: '#3b82f6', borderRadius: 4, barPercentage: 0.5
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        animation: { duration: 0 }, 
        plugins: { 
          legend: { display: false },
          tooltip: { callbacks: { label: (context) => ' ' + formatCurrency(context.raw || 0) } }
        },
        scales: {
          y: { 
            beginAtZero: true, 
            ticks: { 
              color: textColor,
              font: { size: 18, weight: '600' } 
            }, 
            grid: { color: gridColor, drawBorder: false } 
          },
          x: { 
            ticks: { 
              color: textColor,
              font: { size: 18, weight: 'bold' } 
            }, 
            grid: { display: false } 
          }
        }
      }
    });
  }
};

const cargarEstadisticas = async () => {
  loading.value = true; 
  error.value = null;
  
  try {
    const [resStats, resConfig] = await Promise.all([
      axios.get('/api/estadisticas/', { params: { fecha_inicio: filtros.value.fecha_inicio, fecha_fin: filtros.value.fecha_fin } }),
      axios.get('/api/configuracion/')
    ]);
    
    stats.value = resStats.data;
    empresaData.value = resConfig.data;
    usuarioEmisor.value = resStats.data.usuario_emisor || 'Administrador';
    
    if (empresaData.value && empresaData.value.logo && !logoBase64.value) {
      logoBase64.value = await convertToBase64(empresaData.value.logo);
    }

  } catch (e) {
    console.error(e);
    error.value = e.response?.data?.error || 'Error de conexión con el servidor. Revisá la red o recargá la página.';
  } finally {
    loading.value = false; 
  }

  await nextTick(); 

  if (stats.value && !error.value) {
    renderCharts();
  }
};

const generatePDF = async () => {
  isGeneratingPDF.value = true;
  
  try {
    if (turnosChartInstance) {
      document.getElementById('pdf-chart-torta').src = turnosChartInstance.toBase64Image();
    }
    if (pagosChartInstance) {
      document.getElementById('pdf-chart-barras').src = pagosChartInstance.toBase64Image();
    }

    const el = document.getElementById('print-template');
    if (!el) throw new Error('No se encontró el template del PDF');

    el.style.display = 'block';
    el.style.position = 'absolute';
    el.style.top = '-9999px';
    el.style.left = '-9999px';

    await new Promise(r => setTimeout(r, 500));

    const canvas = await html2canvas(el, {
      scale: 5,
      useCORS: true,
      backgroundColor: '#ffffff',
    });

    el.style.display = 'none';
    el.style.position = 'relative';
    el.style.top = '0';
    el.style.left = '0';

    const pdf = new jsPDF('p', 'mm', 'a4');
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    
    const imgData = canvas.toDataURL('image/jpeg', 0.95);
    const imgProps = pdf.getImageProperties(imgData);
    const totalImgHeight = (imgProps.height * pdfWidth) / imgProps.width;

    let heightLeft = totalImgHeight;
    let position = 0;
    let pageNumber = 1;
    const pageHeight = pdfHeight - 10; 
    const totalPages = Math.ceil(totalImgHeight / pageHeight) || 1;

    pdf.addImage(imgData, 'JPEG', 0, position, pdfWidth, totalImgHeight);
    heightLeft -= pageHeight;
    pdf.setFontSize(8);
    pdf.setTextColor(100, 116, 139);
    pdf.text(`Reporte Administrativo - Página ${pageNumber} de ${totalPages}`, pdfWidth - 65, pdfHeight - 5);

    while (heightLeft > 0) {
      position = heightLeft - totalImgHeight; 
      pdf.addPage();
      pageNumber++;
      pdf.addImage(imgData, 'JPEG', 0, position, pdfWidth, totalImgHeight);
      heightLeft -= pageHeight;
      
      pdf.setFontSize(8);
      pdf.setTextColor(100, 116, 139);
      pdf.text(`Reporte Administrativo - Página ${pageNumber} de ${totalPages}`, pdfWidth - 65, pdfHeight - 5);
    }

    pdf.save(`Reporte_Estrategico_${filtros.value.fecha_inicio}_al_${filtros.value.fecha_fin}.pdf`);
    
  } catch (err) {
    console.error('Error generando PDF:', err);
  } finally {
    isGeneratingPDF.value = false;
  }
};

onMounted(() => aplicarPeriodoRapido());
</script>

<style scoped>
.dashboard-wrapper {
  background: var(--bg-primary);
  min-height: 100vh;
  color: var(--text-primary);
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
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
}
.dashboard-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--accent-color);
}
.dashboard-subtitle {
  color: var(--text-secondary);
  margin: 0.2rem 0 0;
  font-size: 0.9rem;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.period-selector {
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 4px;
  display: flex;
  gap: 4px;
  border: 1px solid var(--border-color);
}
.period-selector button {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: 0.2s;
}
.period-selector button.active {
  background: var(--accent-color);
  color: white;
}

.custom-date-panel {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-primary);
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}
.date-separator { color: var(--text-secondary); }
.date-input-custom {
  background: transparent;
  border: none;
  color: var(--text-primary);
  outline: none;
}

.apply-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.apply-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.apply-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.pdf-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: 0.2s;
}
.pdf-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(239,68,68,0.3); }
.pdf-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.rotating { animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.kpi-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.2rem;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: 0.2s;
}
.kpi-icon {
  font-size: 2rem;
  padding: 0.8rem;
  border-radius: 8px;
  background: var(--hover-bg);
  flex-shrink: 0;
}
.income-card .kpi-icon  { color: #10b981; }
.turnos-card .kpi-icon  { color: #3b82f6; }
.stars-card .kpi-icon   { color: #f59e0b; }

.kpi-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.kpi-label {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.kpi-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0.1rem 0;
}
.kpi-subtext {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.favorite-item {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}
.favorite-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.favorite-title {
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.fav-label {
  color: var(--text-secondary) !important;
  display: flex;
  align-items: center;
  gap: 4px;
}
.fav-name {
  color: #ffffff !important;
  font-weight: 700;
}
.favorite-details {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-left: 24px;
}
.service-icon { color: #3b82f6; font-size: 1.1rem; }
.product-icon { color: #f97316; font-size: 1.1rem; }

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}
.chart-card {
  display: flex;
  flex-direction: column;
  margin-bottom: 0 !important;
}

.chart-layout {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 1rem;
}

.chart-layout .chart-box {
  width: 50%;
  height: 220px;
  flex-shrink: 0;
  padding: 0;
  position: relative;
}

.chart-box canvas { transition: opacity 0.3s ease; }

.chart-empty-message {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  color: var(--text-tertiary);
  font-style: italic;
  font-size: 1rem;
}

.chart-summary {
  width: 45%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.summary-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}
.summary-info {
  display: flex;
  flex-direction: column;
}
.summary-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
}
.summary-value {
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 900;
}
.summary-item.total {
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
}
.summary-item.total .summary-label {
  color: var(--accent-color);
  font-size: 1rem;
  font-weight: 800;
}
.summary-item.total .summary-value {
  font-size: 2rem;
}
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }

.section-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 1.5rem;
}
.section-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}
.section-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.table-container { overflow-x: auto; }
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.data-table th {
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.8rem;
  text-transform: uppercase;
  padding: 1rem 1.5rem;
  letter-spacing: 0.5px;
}
.data-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}
.data-table tr:hover td { background: var(--hover-bg); }
.item-name { font-weight: 600; }
.income  { color: #10b981; }
.expense { color: #ef4444; }
.text-center { text-align: center; }
.text-right  { text-align: right; }

.badge-neutral {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  border: 1px solid var(--border-color);
}
.empty-state {
  padding: 2rem !important;
  text-align: center;
  color: var(--text-tertiary);
  font-style: italic;
}

.state-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: var(--text-secondary);
}
.loader {
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--accent-color);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.alerta-huerfanos {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 12px;
  padding: 1.2rem 1.5rem;
  color: #ef4444;
}
.alerta-content strong { display: block; margin-bottom: 4px; }
.alerta-content p { margin: 0; font-size: 0.9rem; color: var(--text-secondary); }

.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

/* RESPONSIVE */
@media (max-width: 900px) {
  .chart-layout {
    flex-direction: column;
  }
  .chart-layout .chart-box {
    width: 100%;
    margin-bottom: 1rem;
  }
  .chart-summary {
    width: 100%;
    border-top: 1px solid var(--border-color);
    padding-top: 1.5rem;
  }
}
</style>