<template>
  <div class="list-container">
    <div class="list-card">
      
      <div class="list-header">
        <div class="header-content">
          <div>
            <h1>GESTIÓN DE SUELDOS</h1>
            <p>Liquidación de comisiones y registro de pagos</p>
          </div>
        </div>
      </div>

      <div class="tabs-container">
        <button 
          class="tab-btn" 
          :class="{ active: tabActiva === 'calcular' }" 
          @click="cambiarTab('calcular')"
        >
          <i class="ri-calculator-line"></i> 
          <span>Calcular Pendientes</span>
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: tabActiva === 'historial' }" 
          @click="cambiarTab('historial')"
        >
          <i class="ri-history-line"></i> 
          <span>Historial de Pagos</span>
        </button>
      </div>

      <div v-if="tabActiva === 'calcular'" class="animate-fade">
        
        <div class="filters-container">
          <div class="filters-grid">
            <div class="filter-group">
              <label><i class="ri-calendar-line"></i> Desde</label>
              <input type="date" v-model="fechaInicio" class="filter-input" />
            </div>
            <div class="filter-group">
              <label><i class="ri-calendar-check-line"></i> Hasta</label>
              <input type="date" v-model="fechaFin" class="filter-input" />
            </div>
            
            <div class="filter-group">
              <label><i class="ri-user-search-line"></i> Filtrar Profesional</label>
              <div class="select-wrapper">
                <select v-model="filtroPeluquero" class="filter-input custom-select">
                  <option :value="null">Todos los Profesionales</option>
                  <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                    {{ p.nombre }} {{ p.apellido }}
                  </option>
                </select>
                <i class="ri-arrow-down-s-line select-arrow"></i>
              </div>
            </div>

            <div class="filter-group filter-button-group">
              <button @click="obtenerReporte" class="search-button" :disabled="cargando">
                <span v-if="cargando" class="spinner"></span>
                <span v-else><i class="ri-search-line"></i> Calcular</span>
              </button>
            </div>
          </div>
        </div>

        <div v-if="reporte.length > 0" class="stats-grid">
          <div class="stat-card total-pagar">
            <div class="stat-icon"><i class="ri-hand-coin-line"></i></div>
            <div class="stat-info">
              <span>Total Comisiones a Pagar</span>
              <h3>$ {{ formatPrecio(totalGeneralPagar) }}</h3>
            </div>
          </div>
          
          <div class="stat-card total-ventas">
            <div class="stat-icon"><i class="ri-store-2-line"></i></div>
            <div class="stat-info">
              <span>Total Generado (Caja)</span>
              <h3>$ {{ formatPrecio(totalVentasGeneradas) }}</h3>
            </div>
          </div>

          <div class="stat-card total-turnos">
            <div class="stat-icon"><i class="ri-scissors-cut-line"></i></div>
            <div class="stat-info">
              <span>Turnos a Liquidar</span>
              <h3>{{ totalTurnos }}</h3>
            </div>
          </div>
        </div>

        <div class="table-container" v-if="reporte.length > 0">
          <div class="table-wrapper">
            <table class="users-table">
              <thead>
                <tr>
                  <th style="width: 50px"></th>
                  <th>Empleado</th>
                  <th class="text-center"><i class="ri-time-line"></i> Turnos</th>
                  <th class="text-end text-muted"><i class="ri-store-line"></i> Generado</th>
                  <th class="text-end"><i class="ri-money-dollar-circle-line"></i> Total a Pagar</th>
                  <th class="text-center">Acción</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="item in reportePaginado" :key="item.id">
                  <tr class="row-parent" :class="{ expanded: expandedRows.includes(item.id) }">
                    <td class="expand-cell" @click="toggleExpand(item.id)">
                      <div class="expand-button">
                        <i :class="expandedRows.includes(item.id) ? 'ri-arrow-up-s-line' : 'ri-arrow-down-s-line'"></i>
                      </div>
                    </td>
                    <td>
                      <div class="employee-info">
                        <div class="employee-avatar">{{ item.nombre.charAt(0) }}</div>
                        <div>
                          <strong class="employee-name">{{ item.nombre }}</strong>
                          <small class="employee-role">{{ item.rol }}</small>
                        </div>
                      </div>
                    </td>
                    <td class="text-center">
                      <span class="badge-turnos">{{ item.cantidad_turnos }}</span>
                    </td>
                    <td class="text-end">
                      <span class="monto-generado">$ {{ formatPrecio(calcularGenerado(item)) }}</span>
                    </td>
                    <td class="text-end">
                      <span class="monto-total">$ {{ formatPrecio(item.total_a_pagar) }}</span>
                    </td>
                    <td class="text-center">
                      <button 
                        @click="registrarPago(item)" 
                        class="btn-pagar"
                        title="Confirmar Pago"
                      >
                        <i class="ri-check-double-line"></i>
                        <span>Pagar</span>
                      </button>
                    </td>
                  </tr>
                  
                  <tr v-if="expandedRows.includes(item.id)" class="row-detail">
                    <td colspan="6">
                      <div class="detail-wrapper">
                        <h4 class="detail-title"><i class="ri-file-list-3-line"></i> Detalle de Turnos Pendientes</h4>
                        <div class="detail-scroll">
                          <table class="detail-table">
                            <thead>
                              <tr>
                                <th><i class="ri-calendar-2-line"></i> Fecha</th>
                                <th><i class="ri-user-line"></i> Cliente</th>
                                <th><i class="ri-scissors-cut-line"></i> Servicios</th>
                                <th class="text-end">Cobrado</th>
                                <th class="text-end"><i class="ri-money-dollar-circle-line"></i> Comisión</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="(t, idx) in item.detalles" :key="idx" class="detail-row">
                                <td>
                                  <div class="detail-date">
                                    <span class="date-day">{{ t.fecha }}</span>
                                    <span class="date-time">{{ t.hora }}</span>
                                  </div>
                                </td>
                                <td><strong>{{ t.cliente }}</strong></td>
                                <td>
                                  <div class="services-vertical">
                                    <div v-for="(serv, i) in t.servicios.split(' + ')" :key="i" class="service-item">
                                      <i class="ri-checkbox-blank-circle-fill" style="font-size: 6px; vertical-align: middle; margin-right: 4px; color: #0ea5e9;"></i>
                                      {{ serv }}
                                    </div>
                                  </div>
                                </td>
                                <td class="text-end text-muted">$ {{ formatPrecio(t.total_cobrado) }}</td>
                                <td class="text-end">
                                  <span class="detail-amount">$ {{ formatPrecio(t.comision) }}</span>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          
          <div class="pagination-container" v-if="totalPaginasReporte > 1">
            <button @click="paginaReporte--" :disabled="paginaReporte === 1" class="pagination-btn">
              <i class="ri-arrow-left-s-line"></i> Anterior
            </button>
            <span class="pagination-info">Página {{ paginaReporte }} de {{ totalPaginasReporte }}</span>
            <button @click="paginaReporte++" :disabled="paginaReporte === totalPaginasReporte" class="pagination-btn">
              Siguiente <i class="ri-arrow-right-s-line"></i>
            </button>
          </div>
          
          <div class="download-section">
            <button @click="descargarPDF" class="btn-download" :disabled="descargandoPDF">
              <span v-if="descargandoPDF" class="spinner-small"></span>
              <span v-else><i class="ri-file-pdf-line"></i> Descargar Reporte PDF</span>
            </button>
          </div>

        </div>
        
        <div v-else-if="!cargando" class="empty-state">
           <i class="ri-search-line empty-icon"></i>
           <h3>Listo para calcular</h3>
           <p>Seleccioná un rango de fechas para ver las comisiones.</p>
        </div>
      </div>

      <div v-if="tabActiva === 'historial'" class="animate-fade">
        
        <div class="filters-container">
            <div class="filters-grid" style="grid-template-columns: 1fr;">
                <div class="filter-group">
                  <label><i class="ri-user-search-line"></i> Filtrar Historial por Profesional</label>
                  <div class="select-wrapper">
                    <select v-model="filtroPeluqueroHistorial" class="filter-input custom-select" @change="cargarHistorial">
                        <option :value="null">Ver Todos</option>
                        <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                        {{ p.nombre }} {{ p.apellido }}
                        </option>
                    </select>
                    <i class="ri-arrow-down-s-line select-arrow"></i>
                  </div>
                </div>
            </div>
        </div>

        <div class="table-container">
          <div class="table-wrapper">
            <table class="users-table historial-table">
              <thead>
                <tr>
                  <th><i class="ri-calendar-check-line"></i> Fecha Pago</th>
                  <th><i class="ri-user-line"></i> Empleado</th>
                  <th><i class="ri-calendar-2-line"></i> Período</th>
                  <th class="text-end"><i class="ri-money-dollar-circle-line"></i> Pagado</th>
                  <th class="text-center">PDF</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pago in historialPaginado" :key="pago.id" class="historial-row">
                  <td>
                    <div class="historial-date">
                      <i class="ri-calendar-check-fill"></i>
                      {{ formatDate(pago.fecha_pago) }}
                    </div>
                  </td>
                  <td>
                    <div class="employee-info-simple">
                      <strong>{{ pago.empleado_nombre }} {{ pago.empleado_apellido }}</strong>
                    </div>
                  </td>
                  <td>
                    <span class="period-badge">
                      {{ formatDate(pago.fecha_inicio_periodo) }} → {{ formatDate(pago.fecha_fin_periodo) }}
                    </span>
                  </td>
                  <td class="text-end">
                    <span class="historial-amount">$ {{ formatPrecio(pago.total_pagado) }}</span>
                  </td>
                  <td class="text-center">
                    <button class="btn-print" title="Reimprimir PDF" @click="imprimirComprobante(pago)">
                      <i class="ri-printer-line"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="historial.length === 0">
                  <td colspan="5">
                    <div class="empty-state-inline">
                      <i class="ri-inbox-line"></i>
                      <span>No hay pagos registrados aún</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="pagination-container" v-if="totalPaginasHistorial > 1">
          <button @click="paginaHistorial--" :disabled="paginaHistorial === 1" class="pagination-btn">
            <i class="ri-arrow-left-s-line"></i> Anterior
          </button>
          <span class="pagination-info">Página {{ paginaHistorial }} de {{ totalPaginasHistorial }}</span>
          <button @click="paginaHistorial++" :disabled="paginaHistorial === totalPaginasHistorial" class="pagination-btn">
            Siguiente <i class="ri-arrow-right-s-line"></i>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from '@/utils/axiosConfig';
import Swal from 'sweetalert2';

const API_URL = "http://localhost:8000/api";

const tabActiva = ref('calcular');
const fechaInicio = ref("");
const fechaFin = ref("");
const reporte = ref([]);
const historial = ref([]);
const peluqueros = ref([]);
const filtroPeluquero = ref(null);
const filtroPeluqueroHistorial = ref(null);

const cargando = ref(false);
const descargandoPDF = ref(false);
const expandedRows = ref([]);
const itemsPorPagina = 8;
const paginaReporte = ref(1);
const paginaHistorial = ref(1);

const formatPrecio = (v) => parseFloat(v || 0).toLocaleString("es-AR", { minimumFractionDigits: 2 });
const formatDate = (f) => f ? new Date(f).toLocaleDateString('es-AR') : '-';

const totalGeneralPagar = computed(() => reporte.value.reduce((acc, item) => acc + item.total_a_pagar, 0));
const totalTurnos = computed(() => reporte.value.reduce((acc, item) => acc + item.cantidad_turnos, 0));
const totalVentasGeneradas = computed(() => {
  return reporte.value.reduce((acc, item) => {
    return acc + item.detalles.reduce((t, turno) => t + (turno.total_cobrado || 0), 0);
  }, 0);
});

const reportePaginado = computed(() => {
  const inicio = (paginaReporte.value - 1) * itemsPorPagina;
  return reporte.value.slice(inicio, inicio + itemsPorPagina);
});
const totalPaginasReporte = computed(() => Math.ceil(reporte.value.length / itemsPorPagina));

const historialPaginado = computed(() => {
  const inicio = (paginaHistorial.value - 1) * itemsPorPagina;
  return historial.value.slice(inicio, inicio + itemsPorPagina);
});
const totalPaginasHistorial = computed(() => Math.ceil(historial.value.length / itemsPorPagina));

const toggleExpand = (id) => {
  if (expandedRows.value.includes(id)) expandedRows.value = expandedRows.value.filter(i => i !== id);
  else expandedRows.value.push(id);
};

const calcularGenerado = (item) => {
  return item.detalles.reduce((acc, t) => acc + (t.total_cobrado || 0), 0);
};

const cambiarTab = async (tab) => {
  tabActiva.value = tab;
  paginaReporte.value = 1;
  paginaHistorial.value = 1;
  expandedRows.value = [];
  if (tab === 'historial') await cargarHistorial();
};

const cargarPeluqueros = async () => {
    try {
        const res = await axios.get(`${API_URL}/peluqueros/`);
        peluqueros.value = res.data;
    } catch (e) { console.error("Error cargando peluqueros", e); }
};

const obtenerReporte = async () => {
  if (!fechaInicio.value || !fechaFin.value) return Swal.fire('Atención', 'Seleccioná las fechas primero', 'warning');
  cargando.value = true;
  expandedRows.value = [];
  paginaReporte.value = 1;
  try {
    const res = await axios.get(`${API_URL}/reporte-liquidacion/`, { 
        params: { 
            fecha_inicio: fechaInicio.value, 
            fecha_fin: fechaFin.value,
            peluquero_id: filtroPeluquero.value 
        } 
    });
    reporte.value = res.data;
    if (reporte.value.length === 0) Swal.fire('Sin Datos', 'No hay nada pendiente para liquidar', 'info');
  } catch (e) { Swal.fire('Error', 'Error al calcular', 'error'); } 
  finally { cargando.value = false; }
};

const registrarPago = async (empleado) => {
  const result = await Swal.fire({
    title: `Pagar $${formatPrecio(empleado.total_a_pagar)}`,
    text: `Confirmar pago a ${empleado.nombre}.`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Sí, Pagar',
    confirmButtonColor: '#10b981',
    background: '#1e293b', color: '#fff'
  });

  if (result.isConfirmed) {
    try {
      const payload = {
        empleado_id: empleado.id,
        fecha_inicio: fechaInicio.value,
        fecha_fin: fechaFin.value,
        monto_comisiones: empleado.comision_ganada,
        monto_sueldo_fijo: 0,
        total_pagado: empleado.total_a_pagar
      };
      await axios.post(`${API_URL}/liquidaciones/registrar/`, payload);
      Swal.fire({ title: '¡Pago Registrado!', icon: 'success', timer: 1500, showConfirmButton: false });
      reporte.value = reporte.value.filter(e => e.id !== empleado.id);
    } catch (e) { Swal.fire('Error', 'No se pudo registrar', 'error'); }
  }
};

const cargarHistorial = async () => {
  try {
    const res = await axios.get(`${API_URL}/liquidaciones/historial/`, {
        params: { empleado_id: filtroPeluqueroHistorial.value }
    });
    historial.value = res.data;
  } catch (e) { console.error(e); }
};

const descargarPDF = async () => {
    await manejarDescargaPDF({ 
        fecha_inicio: fechaInicio.value, 
        fecha_fin: fechaFin.value,
        peluquero_id: filtroPeluquero.value 
    }, `Reporte_${fechaInicio.value}.pdf`);
};

const imprimirComprobante = async (pago) => {
    await manejarDescargaPDF({ 
        fecha_inicio: pago.fecha_inicio_periodo, 
        fecha_fin: pago.fecha_fin_periodo,
        peluquero_id: pago.empleado 
    }, `Comprobante_${pago.fecha_pago}.pdf`);
};

const manejarDescargaPDF = async (params, nombreArchivo) => {
    descargandoPDF.value = true;
    try {
        const res = await axios.get(`${API_URL}/reporte-liquidacion/pdf/`, { params, responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
        const link = document.createElement('a');
        link.href = url;
        link.download = nombreArchivo;
        document.body.appendChild(link);
        link.click();
        setTimeout(() => { document.body.removeChild(link); window.URL.revokeObjectURL(url); }, 100);
    } catch (e) { Swal.fire('Error', 'Error al generar PDF', 'error'); }
    finally { descargandoPDF.value = false; }
}

onMounted(async () => {
  await cargarPeluqueros();
  const today = new Date();
  const diff = today.getDate() - today.getDay() + (today.getDay() === 0 ? -6 : 1);
  const monday = new Date(today.setDate(diff));
  const saturday = new Date(today.setDate(monday.getDate() + 5));
  fechaInicio.value = monday.toISOString().split('T')[0];
  fechaFin.value = saturday.toISOString().split('T')[0];
});
</script>

<style scoped>
/* ==================== VARIABLES Y BASE ==================== */
.list-container { padding: 24px; max-width: 1400px; margin: 0 auto; min-height: 100vh; }
.list-card { background: var(--bg-secondary); border-radius: 24px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); border: 1px solid var(--border-color); position: relative; overflow: hidden; }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9); background-size: 200% 100%; }
@keyframes gradientShift { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
.stat-card { background: var(--bg-primary); padding: 20px; border-radius: 16px; border: 1px solid var(--border-color); display: flex; align-items: center; gap: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.stat-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; }
.stat-info span { font-size: 0.85rem; color: var(--text-secondary); display: block; margin-bottom: 5px; }
.stat-info h3 { margin: 0; font-size: 1.4rem; color: var(--text-primary); font-weight: 800; }
.total-pagar .stat-icon { background: linear-gradient(135deg, #10b981, #059669); }
.total-ventas .stat-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }
.total-turnos .stat-icon { background: linear-gradient(135deg, #0ea5e9, #0284c7); }

.list-header { border-bottom: 2px solid var(--border-color); padding-bottom: 24px; margin-bottom: 32px; }
.header-content { display: flex; align-items: center; gap: 20px; }
.list-header h1 { font-size: 2rem; color: var(--text-primary); font-weight: 800; margin: 0; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.list-header p { color: var(--text-secondary); margin: 5px 0 0 0; font-weight: 500; }

.tabs-container { display: flex; gap: 12px; margin-bottom: 32px; background: var(--hover-bg); padding: 8px; border-radius: 16px; border: 1px solid var(--border-color); }
.tab-btn { flex: 1; background: transparent; border: none; padding: 14px; font-size: 1rem; font-weight: 700; color: var(--text-secondary); cursor: pointer; border-radius: 12px; display: flex; align-items: center; justify-content: center; gap: 10px; transition: 0.3s; }
.tab-btn.active { background: var(--bg-primary); color: #0ea5e9; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.tab-btn:hover:not(.active) { color: var(--text-primary); }

.filters-container { background: var(--bg-primary); padding: 24px; border-radius: 16px; margin-bottom: 30px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: 1fr 1fr 1.5fr 1fr; gap: 20px; align-items: end; }
.filter-group label { display: block; font-weight: 700; color: var(--text-secondary); margin-bottom: 8px; font-size: 0.9rem; }
.filter-input { width: 100%; padding: 12px; border-radius: 10px; border: 2px solid var(--border-color); background: var(--bg-secondary); color: var(--text-primary); outline: none; transition: 0.2s; }
.filter-input:focus { border-color: #0ea5e9; box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2); background: var(--bg-primary); }

/* SELECT STYLES */
.select-wrapper { position: relative; }
.custom-select { appearance: none; cursor: pointer; }
.select-arrow { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: var(--text-secondary); pointer-events: none; font-size: 1.2rem; }

.search-button { background: #0ea5e9; color: white; padding: 12px; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; width: 100%; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
.search-button:hover:not(:disabled) { background: #0284c7; transform: translateY(-2px); }

.table-container { border-radius: 16px; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
.table-wrapper { overflow-x: auto; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); }
.users-table th { background: #1e293b; color: white; padding: 16px; text-align: left; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; }
.users-table td { padding: 16px; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); vertical-align: middle; }
.row-parent { transition: 0.2s; }
.row-parent:hover { background: var(--hover-bg); }
.row-parent.expanded { background: var(--hover-bg); border-left: 4px solid #0ea5e9; }

.expand-button { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: rgba(14,165,233,0.1); color: #0ea5e9; border-radius: 8px; cursor: pointer; transition: 0.2s; }
.expand-button:hover { background: #0ea5e9; color: white; }
.employee-info { display: flex; align-items: center; gap: 12px; }
.employee-avatar { width: 40px; height: 40px; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.employee-name { display: block; color: var(--text-primary); font-size: 1rem; }
.employee-role { font-size: 0.8rem; color: var(--text-muted); }
.badge-turnos { background: var(--bg-secondary); padding: 5px 10px; border-radius: 6px; font-weight: 700; border: 1px solid var(--border-color); }
.monto-comision { color: #10b981; font-weight: 700; }
.monto-generado { color: var(--text-muted); }
.monto-total { color: #0ea5e9; font-weight: 800; font-size: 1.1rem; }
.btn-pagar { background: #10b981; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: 0.2s; }
.btn-pagar:hover { background: #059669; transform: translateY(-2px); }

.row-detail td { padding: 0; background: var(--bg-secondary); }
.detail-wrapper { padding: 20px; }
.detail-title { margin: 0 0 15px 0; color: var(--text-primary); font-size: 1rem; display: flex; align-items: center; gap: 8px; }
.detail-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color); }
.detail-table th { background: var(--hover-bg); color: var(--text-secondary); padding: 10px 15px; font-size: 0.8rem; }
.detail-table td { padding: 10px 15px; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
.detail-amount { color: #10b981; font-weight: 700; }
.services-tag { font-size: 0.85rem; color: var(--text-primary); }
.services-vertical { display: flex; flex-direction: column; gap: 4px; }
.service-item { font-size: 0.85rem; color: var(--text-primary); line-height: 1.3; }

.pagination-container { display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 20px; padding: 10px; }
.pagination-btn { background: var(--bg-primary); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 8px; cursor: pointer; color: var(--text-primary); display: flex; align-items: center; gap: 5px; transition: 0.2s; }
.pagination-btn:hover:not(:disabled) { border-color: #0ea5e9; color: #0ea5e9; }
.pagination-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.download-section { margin-top: 20px; display: flex; justify-content: flex-end; }
.btn-download { background: var(--bg-primary); border: 2px solid #0ea5e9; color: #0ea5e9; padding: 12px 24px; border-radius: 10px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
.btn-download:hover { background: #0ea5e9; color: white; }

.historial-date { display: flex; align-items: center; gap: 8px; font-weight: 600; }
.period-badge { background: var(--hover-bg); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; border: 1px solid var(--border-color); }
.btn-print { background: var(--bg-secondary); border: 1px solid var(--border-color); width: 36px; height: 36px; border-radius: 8px; cursor: pointer; color: var(--text-secondary); display: inline-flex; align-items: center; justify-content: center; transition: 0.2s; }
.btn-print:hover { border-color: #0ea5e9; color: #0ea5e9; }

.text-center { text-align: center; }
.text-end { text-align: right; }
.text-muted { color: var(--text-muted); }
.empty-state { text-align: center; padding: 60px; color: var(--text-muted); }
.empty-icon { font-size: 4rem; opacity: 0.3; margin-bottom: 15px; display: block; }
.animate-fade { animation: fade 0.3s ease; }
@keyframes fade { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.spinner { width: 18px; height: 18px; border: 3px solid rgba(255, 255, 255, 0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
.spinner-small { width: 14px; height: 14px; border: 2px solid rgba(255, 255, 255, 0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .filters-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 768px) {
  .list-card { padding: 24px; }
  .header-content { flex-direction: column; text-align: center; }
  .list-header h1 { font-size: 1.8rem; }
  .filters-grid { grid-template-columns: 1fr; }
  .tabs-container { flex-direction: column; }
  .employee-avatar { width: 40px; height: 40px; font-size: 1.1rem; }
  .pagination-container { flex-direction: column; gap: 12px; }
  .pagination-btn { width: 100%; justify-content: center; }
}
</style>