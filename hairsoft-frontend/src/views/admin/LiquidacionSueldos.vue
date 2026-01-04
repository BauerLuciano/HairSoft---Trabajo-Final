<template>
  <div class="list-container">
    <div class="list-card">
      
      <!-- HEADER -->
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Sueldos</h1>
          <p>Liquidación de comisiones y registro de pagos</p>
        </div>
        
        <div class="header-buttons" style="display: flex; gap: 12px;">
          <button 
            @click="cambiarTab('calcular')" 
            class="register-button"
            :class="{ 'btn-activo': tabActiva === 'calcular' }"
            style="min-width: 160px;"
          >
            <Calculator :size="18" />
            Calcular Pendientes
          </button>
          <button 
            @click="cambiarTab('historial')" 
            class="register-button"
            :class="{ 'btn-activo': tabActiva === 'historial' }"
            style="background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-secondary);"
          >
            <History :size="18" />
            Historial
          </button>
        </div>
      </div>

      <!-- VISTA CALCULAR -->
      <div v-if="tabActiva === 'calcular'" class="animate-fade">
        
        <!-- FILTROS AUTOMÁTICOS -->
        <div class="filters-container">
          <div class="filters-grid">
            <div class="filter-group">
              <label>Desde</label>
              <input type="date" v-model="fechaInicio" class="filter-input" @change="obtenerReporte" />
            </div>
            <div class="filter-group">
              <label>Hasta</label>
              <input type="date" v-model="fechaFin" class="filter-input" @change="obtenerReporte" />
            </div>
            
            <div class="filter-group" style="grid-column: span 2;">
              <label>Profesional</label>
              <select v-model="filtroPeluquero" class="filter-input" @change="obtenerReporte">
                <option :value="null">Todos los Profesionales</option>
                <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                  {{ p.nombre }} {{ p.apellido }}
                </option>
              </select>
            </div>
          </div>
          
          <div v-if="cargando" style="margin-top: 15px; color: var(--accent-color); font-size: 0.9rem; display: flex; align-items: center; gap: 8px; font-weight: 600;">
             <span class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></span> Calculando comisiones...
          </div>
        </div>

        <!-- STATS CARDS -->
        <div v-if="reporte.length > 0" class="usuarios-count" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; background: transparent; border: none; padding: 0;">
          <div class="stat-card total-pagar">
            <div class="stat-icon"><DollarSign :size="24" /></div>
            <div class="stat-info">
              <span>A Pagar</span>
              <h3>$ {{ formatPrecio(totalGeneralPagar) }}</h3>
            </div>
          </div>
          <div class="stat-card total-ventas">
            <div class="stat-icon"><Store :size="24" /></div>
            <div class="stat-info">
              <span>Caja Total</span>
              <h3>$ {{ formatPrecio(totalVentasGeneradas) }}</h3>
            </div>
          </div>
          <div class="stat-card total-turnos">
            <div class="stat-icon"><Scissors :size="24" /></div>
            <div class="stat-info">
              <span>Turnos</span>
              <h3>{{ totalTurnos }}</h3>
            </div>
          </div>
        </div>

        <!-- TABLA REPORTE -->
        <div class="table-container" v-if="reporte.length > 0">
          <table class="users-table">
            <thead>
              <tr>
                <th style="width: 50px"></th>
                <th>Empleado</th>
                <th class="text-center">Turnos</th>
                <th class="text-end">Generado</th>
                <th class="text-end">Total a Pagar</th>
                <th class="text-center" style="width: 100px;">Acción</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="item in reportePaginado" :key="item.id">
                <tr :class="expandedRows.includes(item.id) ? 'hover-row expanded' : 'hover-row'">
                  <td @click="toggleExpand(item.id)" style="cursor: pointer; text-align: center;">
                    <component :is="expandedRows.includes(item.id) ? ChevronUp : ChevronDown" :size="18" style="opacity: 0.7;" />
                  </td>
                  <td>
                    <div style="display: flex; align-items: center; gap: 10px;">
                      <div class="employee-avatar">{{ item.nombre.charAt(0) }}</div>
                      <div>
                        <strong>{{ item.nombre }}</strong><br/>
                        <span style="font-size: 0.75rem; opacity: 0.7;">{{ item.rol }}</span>
                      </div>
                    </div>
                  </td>
                  <td class="text-center">
                    <span class="badge-estado estado-info">{{ item.cantidad_turnos }}</span>
                  </td>
                  <td class="text-end" style="opacity: 0.8;">$ {{ formatPrecio(calcularGenerado(item)) }}</td>
                  <td class="text-end">
                    <span class="monto-total">$ {{ formatPrecio(item.total_a_pagar) }}</span>
                  </td>
                  <td class="text-center">
                    <div class="action-buttons" style="justify-content: center;">
                      <button @click="registrarPago(item)" class="action-button success" title="Registrar Pago">
                        <CheckCircle :size="16" />
                      </button>
                    </div>
                  </td>
                </tr>
                
                <!-- DETALLE EXPANDIDO -->
                <tr v-if="expandedRows.includes(item.id)" class="row-detail">
                  <td colspan="6" style="padding: 0;">
                    <div class="detail-wrapper">
                      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px; color: var(--text-primary);">
                        <FileText :size="16" /> 
                        <span style="font-weight: 700; text-transform: uppercase; font-size: 0.8rem;">Detalle de Turnos</span>
                      </div>
                      <div class="table-container" style="box-shadow: none; border: 1px solid var(--border-color);">
                        <table class="users-table" style="font-size: 0.85rem;">
                          <thead>
                            <tr>
                              <th style="background: var(--bg-tertiary); color: var(--text-secondary);">Fecha</th>
                              <th style="background: var(--bg-tertiary); color: var(--text-secondary);">Cliente</th>
                              <th style="background: var(--bg-tertiary); color: var(--text-secondary);">Servicios</th>
                              <th class="text-end" style="background: var(--bg-tertiary); color: var(--text-secondary);">Cobrado</th>
                              <th class="text-end" style="background: var(--bg-tertiary); color: var(--text-secondary);">Comisión</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(t, idx) in item.detalles" :key="idx">
                              <td>
                                <div style="display: flex; flex-direction: column;">
                                  <span style="font-weight: 600;">{{ t.fecha }}</span>
                                  <span style="font-size: 0.75rem; opacity: 0.7;">{{ t.hora }}</span>
                                </div>
                              </td>
                              <td><strong>{{ t.cliente }}</strong></td>
                              <td>
                                <div style="display: flex; flex-direction: column; gap: 4px;">
                                  <div v-for="(serv, i) in t.servicios.split(' + ')" :key="i" style="display: flex; align-items: center;">
                                    <div style="width: 4px; height: 4px; background: #0ea5e9; border-radius: 50%; margin-right: 6px;"></div>
                                    <span v-if="serv.includes('(')">
                                      {{ serv.split('(')[0] }} 
                                      <span style="color: #10b981; font-weight: 800; font-size: 0.8rem;">
                                        ({{ serv.split('(')[1] }}
                                      </span>
                                    </span>
                                    <span v-else>{{ serv }}</span>
                                  </div>
                                </div>
                              </td>
                              <td class="text-end" style="opacity: 0.8;">$ {{ formatPrecio(t.total_cobrado) }}</td>
                              <td class="text-end">
                                <span style="color: #10b981; font-weight: 700;">$ {{ formatPrecio(t.comision) }}</span>
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
        
        <div class="pagination" v-if="totalPaginasReporte > 1">
          <button @click="paginaReporte--" :disabled="paginaReporte === 1"><ChevronLeft :size="16" /> Anterior</button>
          <span>Página {{ paginaReporte }} de {{ totalPaginasReporte }}</span>
          <button @click="paginaReporte++" :disabled="paginaReporte === totalPaginasReporte">Siguiente <ChevronRight :size="16" /></button>
        </div>

        <div v-if="reporte.length > 0" style="margin-top: 20px; display: flex; justify-content: flex-end;">
           <button @click="descargarPDF" class="clear-filters-btn" :disabled="descargandoPDF">
             <span v-if="descargandoPDF" class="spinner-small"></span>
             <span v-else style="display: flex; align-items: center; gap: 6px;">
                <FileText :size="16" /> Descargar Reporte PDF
             </span>
           </button>
        </div>
        
        <div v-else-if="!cargando" class="no-results">
           <Search class="no-results-icon" :size="48" />
           <p>Listo para calcular</p>
           <small>Seleccioná un rango de fechas para ver las comisiones.</small>
        </div>
      </div>

      <!-- VISTA HISTORIAL -->
      <div v-if="tabActiva === 'historial'" class="animate-fade">
        <div class="filters-container">
            <div class="filters-grid" style="grid-template-columns: 1fr;">
                <div class="filter-group">
                  <label>Filtrar Historial por Profesional</label>
                  <select v-model="filtroPeluqueroHistorial" class="filter-input" @change="cargarHistorial">
                      <option :value="null">Ver Todos</option>
                      <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                      {{ p.nombre }} {{ p.apellido }}
                      </option>
                  </select>
                </div>
            </div>
        </div>

        <div class="table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>Fecha Pago</th>
                <th>Empleado</th>
                <th>Período Liquidado</th>
                <th class="text-end">Total Pagado</th>
                <th class="text-center">Comprobante</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pago in historialPaginado" :key="pago.id">
                <td>
                  <div style="display: flex; align-items: center; gap: 6px; font-weight: 600;">
                    <CalendarCheck :size="16" style="color: #10b981;" /> {{ formatDate(pago.fecha_pago) }}
                  </div>
                </td>
                <td><strong>{{ pago.empleado_nombre }} {{ pago.empleado_apellido }}</strong></td>
                <td>
                  <span class="badge-estado estado-secondary">
                    {{ formatDate(pago.fecha_inicio_periodo) }} al {{ formatDate(pago.fecha_fin_periodo) }}
                  </span>
                </td>
                <td class="text-end">
                  <span class="monto-total" style="font-size: 0.95rem;">$ {{ formatPrecio(pago.total_pagado) }}</span>
                </td>
                <td class="text-center">
                  <!-- BOTÓN CORREGIDO CON TÍTULO DETALLADO -->
                  <div class="action-buttons" style="justify-content: center;">
                    <button 
                      class="action-button edit" 
                      :title="`Pago de $${formatPrecio(pago.total_pagado)} a ${pago.empleado_nombre} ${pago.empleado_apellido}`" 
                      @click="imprimirComprobante(pago)"
                      style="width: auto; padding: 8px 12px; gap: 6px;"
                    >
                      <Printer :size="16" />
                      <span class="btn-text">Ver Comprobante</span>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="historial.length === 0">
                 <td colspan="5" class="no-results" style="padding: 40px;">
                    <p>No hay pagos registrados aún</p>
                 </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination" v-if="totalPaginasHistorial > 1">
          <button @click="paginaHistorial--" :disabled="paginaHistorial === 1">
            <ChevronLeft :size="16" /> Anterior
          </button>
          <span>Página {{ paginaHistorial }} de {{ totalPaginasHistorial }}</span>
          <button @click="paginaHistorial++" :disabled="paginaHistorial === totalPaginasHistorial">
            Siguiente <ChevronRight :size="16" /></button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from '@/utils/axiosConfig';
import Swal from 'sweetalert2';
import { 
  Calculator, History, Search, DollarSign, Store, Scissors, 
  ChevronDown, ChevronUp, CheckCircle, FileText, CalendarCheck, 
  Printer, ChevronLeft, ChevronRight 
} from 'lucide-vue-next';

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

// --- CORRECCIÓN DE FECHA MEJORADA ---
// Formatea fechas ISO o strings simples para evitar 'Invalid Date'
const formatDate = (f) => {
  if (!f) return '-';
  try {
    const datePart = typeof f === 'string' && f.includes('T') ? f.split('T')[0] : f;
    
    // Parseo manual YYYY-MM-DD para evitar problemas de zona horaria
    if (typeof datePart === 'string' && datePart.includes('-')) {
        const parts = datePart.split('-');
        // Aseguramos que tenemos año, mes y día
        if (parts.length === 3) {
            return `${parts[2]}/${parts[1]}/${parts[0]}`;
        }
    }
    
    // Fallback: intento estándar
    const d = new Date(f);
    return isNaN(d) ? '-' : d.toLocaleDateString('es-AR');
  } catch (e) {
    return f;
  }
};

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
  else if (tab === 'calcular' && fechaInicio.value && fechaFin.value) obtenerReporte();
};

const cargarPeluqueros = async () => {
    try {
        const res = await axios.get(`${API_URL}/peluqueros/`);
        peluqueros.value = res.data;
    } catch (e) { console.error("Error cargando peluqueros", e); }
};

const obtenerReporte = async () => {
  // Búsqueda automática: si faltan fechas no hacemos nada, si están, buscamos.
  if (!fechaInicio.value || !fechaFin.value) return;
  
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
  } catch (e) { Swal.fire('Error', 'Error al calcular', 'error'); } 
  finally { cargando.value = false; }
};

const registrarPago = async (empleado) => {
  if (empleado.total_a_pagar <= 0) return Swal.fire('Atención', 'El monto a pagar es 0', 'warning');

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
      };
      await axios.post(`${API_URL}/liquidaciones/registrar/`, payload);
      Swal.fire({ title: '¡Pago Registrado!', icon: 'success', timer: 1500, showConfirmButton: false });
      
      reporte.value = reporte.value.filter(e => e.id !== empleado.id);
    } catch (e) { 
      console.error(e);
      Swal.fire('Error', 'No se pudo registrar. Verifique que no esté ya pagado.', 'error'); 
    }
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
        const res = await axios.get(`${API_URL}/reporte-liquidacion/pdf/`, { 
            params, 
            responseType: 'blob' 
        });
        
        const blob = new Blob([res.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = nombreArchivo;
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => { document.body.removeChild(link); window.URL.revokeObjectURL(url); }, 100);
    } catch (e) { 
        console.error(e);
        Swal.fire('Error', 'Error al generar el PDF', 'error'); 
    }
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
  // Carga inicial
  obtenerReporte();
});
</script>

<style scoped>
/* ========================================
   🔥 ESTILO UNIFICADO (Idéntico a Productos)
   ======================================== */

:root {
  --bg-primary: #1e293b;
  --bg-secondary: #0f172a;
  --bg-tertiary: #1e293b; 
  --hover-bg: #334155;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-tertiary: #64748b;
  --accent-color: #0ea5e9;
  --accent-light: rgba(14, 165, 233, 0.2);
  --success-color: #10b981;
  --error-color: #ef4444;
  --border-color: #334155;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

.list-container {
  padding: 32px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}

/* Tarjeta principal */
.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1);
  border-radius: 24px 24px 0 0;
}

/* HEADER */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 25px;
}

.header-content h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.header-content p {
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.5px;
}

/* Botones Principales */
.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4);
}

.register-button:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-activo { background: #0284c7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2); }

/* FILTROS */
.filters-container {
  margin-bottom: 30px;
  background: var(--hover-bg);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 18px;
  align-items: end;
}

.filter-group { display: flex; flex-direction: column; }

.filter-group label {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}

.filter-input {
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-weight: 500;
  font-size: 0.95rem;
  height: 48px;
  box-sizing: border-box;
}

.filter-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

/* CARDS DE ESTADISTICAS */
.stat-card {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  width: 50px; height: 50px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: white;
}

.total-pagar .stat-icon { background: linear-gradient(135deg, #10b981, #059669); }
.total-ventas .stat-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }
.total-turnos .stat-icon { background: linear-gradient(135deg, #0ea5e9, #0284c7); }

.stat-info span { font-size: 0.8rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; }
.stat-info h3 { margin: 0; font-size: 1.5rem; color: var(--text-primary); font-weight: 800; }

/* TABLA */
.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
}

.users-table th {
  background: var(--accent-color);
  color: white;
  padding: 16px 12px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
  white-space: nowrap;
}

.users-table td {
  padding: 14px 12px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--border-color);
}

.hover-row:hover { background: var(--hover-bg); transition: 0.2s; }
.expanded { background: rgba(14, 165, 233, 0.05); border-left: 4px solid var(--accent-color); }

/* UTILIDADES TABLA */
.text-center { text-align: center; }
.text-end { text-align: right; }

.employee-avatar {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800;
}

.badge-estado {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
}
.estado-info { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border: 1px solid #0ea5e9; }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-secondary); border: 1px solid var(--border-color); }

.monto-total { color: #0ea5e9; font-weight: 800; font-size: 1.1rem; }

/* ACCIONES */
.action-button {
  padding: 8px; border: none; border-radius: 10px;
  cursor: pointer; width: 36px; height: 36px;
  display: inline-flex; align-items: center; justify-content: center;
  transition: all 0.3s;
}
.action-button.success { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981; }
.action-button.success:hover { background: #10b981; color: white; transform: translateY(-2px); }
.action-button.edit { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); }
.action-button.edit:hover { background: var(--hover-bg); border-color: var(--accent-color); }

/* DETALLE EXPANDIDO */
.row-detail td { padding: 0; background: #0b1120; }
.detail-wrapper { padding: 24px; border-left: 4px solid var(--accent-color); }
.spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* PAGINACIÓN */
.pagination { display: flex; justify-content: center; gap: 15px; align-items: center; margin-top: 25px; }
.pagination button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  display: flex; align-items: center; gap: 8px;
}
.pagination button:hover:not(:disabled) { background: var(--hover-bg); border-color: var(--accent-color); color: var(--accent-color); }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }

.clear-filters-btn {
  background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color);
  padding: 12px 20px; border-radius: 10px; cursor: pointer; font-weight: 700;
  transition: all 0.3s;
}
.clear-filters-btn:hover:not(:disabled) { border-color: var(--accent-color); color: var(--accent-color); background: var(--hover-bg); }

.no-results { text-align: center; padding: 60px; color: var(--text-secondary); }
.no-results-icon { opacity: 0.3; margin-bottom: 15px; color: var(--text-tertiary); }

.btn-text {
  display: inline-block;
  margin-left: 6px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Ocultar texto en móviles si quieres ahorrar espacio */
@media (max-width: 768px) {
  .btn-text { display: none; }
}

/* RESPONSIVE */
@media (max-width: 1024px) { .filters-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 768px) {
  .list-card { padding: 20px; }
  .filters-grid, .stats-grid { grid-template-columns: 1fr; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .header-buttons { width: 100%; flex-direction: column; }
  .register-button { justify-content: center; }
}
</style>