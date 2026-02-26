<template>
  <div class="list-container">
    <div class="list-card">
      
      <div class="list-header">
        <div class="header-content">
          <h1>AUDITORIA DEL SISTEMA</h1>
          <p>Trazabilidad completa de movimientos unificada</p>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Usuario, Modelo, IP..." class="filter-input"/>
          </div>
          <div class="filter-group">
            <label>Acción</label>
            <select v-model="filtros.accion" class="filter-input">
              <option value="">Todas</option>
              <option value="CREAR">Creación</option>
              <option value="EDITAR">Edición</option>
              <option value="ELIMINAR">Eliminación</option>
              <option value="ANULAR_VENTA">Anulación Venta</option>
              <option value="AJUSTE_STOCK">Ajuste de Stock</option>
            </select>
          </div>
          <div class="filter-group">
            <button @click="limpiarFiltros" class="clear-filters-btn">Limpiar</button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p>Cargando auditoría...</p>
      </div>

      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Modelo</th>
              <th>Dispositivo</th>
              <th>Detalles</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logsPaginados" :key="log.id">
              <td>
                <div style="display:flex; flex-direction:column;">
                  <strong>{{ formatFecha(log.fecha) }}</strong>
                  <span style="font-size:0.8em; opacity:0.7;">{{ formatHora(log.fecha) }}</span>
                </div>
              </td>
              <td>
                <div style="font-weight:600;">{{ log.usuario_nombre || 'Sistema' }}</div>
                <div style="font-size:0.75em; opacity:0.8;">{{ log.usuario_rol }}</div>
              </td>
              <td><span class="badge-estado" :class="getClaseAccion(log.accion)">{{ log.accion.replace('_', ' ') }}</span></td>
              <td>
                <strong>{{ log.modelo_afectado }}</strong>
                <span style="font-size:0.8em; margin-left:5px;">#{{ log.objeto_id }}</span>
              </td>
              
              <td>
                <div class="browser-cell">
                  <div class="browser-main" :class="getColorNavegador(log.navegador_info)">
                    <i :class="getIconoNavegador(log.navegador_info)" style="margin-right:5px;"></i>
                    <span>{{ getNombreNavegador(log.navegador_info) }}</span>
                  </div>
                  <div class="ip-sub">{{ log.ip_address || 'Sin IP' }}</div>
                  <div v-if="log.sistema_operativo" class="os-sub">
                    <i class="fas fa-desktop"></i> {{ log.sistema_operativo }}
                  </div>
                </div>
              </td>
              
              <td>
                <button @click="abrirDetalles(log)" class="action-button edit">Ver Ficha</button>
              </td>
            </tr>
            <tr v-if="!loading && logsPaginados.length === 0">
              <td colspan="6" style="text-align:center; padding:20px;">
                <i class="fas fa-inbox" style="font-size:2rem; opacity:0.3; margin-bottom:10px; display:block;"></i>
                No hay registros de auditoría.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="logsPaginados.length > 0" class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente</button>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModal">&times;</button>
        
        <div class="modal-header-custom" :class="getClaseAccion(logSeleccionado?.accion)">
          <h2>Reporte #{{ logSeleccionado?.id }} - {{ logSeleccionado?.accion.replace('_', ' ') }}</h2>
          <p class="modal-subtitle">Objeto: {{ logSeleccionado?.modelo_afectado }} #{{ logSeleccionado?.objeto_id }}</p>
        </div>

        <div class="modal-body-custom">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">Responsable</span>
              <span class="value">{{ logSeleccionado?.usuario_nombre || 'Sistema' }}</span>
              <span v-if="logSeleccionado?.usuario_email" class="sub-value">
                {{ logSeleccionado?.usuario_email }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">Conexión</span>
              <span class="value" style="font-size: 0.9rem;">
                <i :class="getIconoNavegador(logSeleccionado?.navegador_info)" style="margin-right:5px"></i>
                {{ getNombreNavegador(logSeleccionado?.navegador_info) }}
                <span v-if="logSeleccionado?.navegador_info && logSeleccionado.navegador_info.includes(' ')">
                  ({{ logSeleccionado.navegador_info.split(' ').slice(1).join(' ') }})
                </span>
              </span>
              <span class="sub-value">
                <i class="fas fa-network-wired"></i> IP: {{ logSeleccionado?.ip_address || 'No registrada' }}
                <span v-if="logSeleccionado?.sistema_operativo" style="margin-left:10px;">
                  <i class="fas fa-desktop"></i> {{ logSeleccionado?.sistema_operativo }}
                </span>
              </span>
            </div>
          </div>

          <hr class="divider">

          <h3 class="section-title">Datos del Registro</h3>
          
          <div class="diff-wrapper">
            <table class="detail-table">
              <thead>
                <tr>
                  <th width="35%">Campo</th>
                  <th width="65%">Contenido</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(info, campo) in parseDetalles(logSeleccionado?.detalles)" 
                    :key="campo" 
                    :class="{ 'row-changed': info.tipo === 'CAMBIO' }">
                  
                  <td class="field-col">
                    {{ formatearClave(campo) }}
                    <span v-if="info.tipo === 'CAMBIO'" class="changed-flag">MODIFICADO</span>
                  </td>
                  
                  <td class="value-col">
                    <div v-if="info.tipo === 'CAMBIO'" class="change-container">
                      <div class="val-old"><small>Antes:</small> {{ formatValue(info.anterior) }}</div>
                      <div class="arrow">➜</div>
                      <div class="val-new"><small>Ahora:</small> {{ formatValue(info.nuevo) }}</div>
                    </div>
                    <div v-else-if="info.tipo === 'VALOR'" class="static-val">
                      {{ formatValue(info.valor) }}
                    </div>
                    <div v-else class="legacy-val">{{ formatValue(info) }}</div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="isEmpty(logSeleccionado?.detalles)" class="no-data">
              <i class="fas fa-info-circle"></i> Sin detalles adicionales.
            </div>
          </div>
        </div>
        
        <div class="modal-footer-custom">
          <button @click="cerrarModal" class="clear-filters-btn" style="width: auto;">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api/auditoria/';

const logs = ref([])
const filtros = ref({ busqueda: '', accion: '' })
const pagina = ref(1)
const itemsPorPagina = 10
const mostrarModal = ref(false)
const logSeleccionado = ref(null)
const loading = ref(false)

const getIconoNavegador = (navegadorInfo) => {
  if (!navegadorInfo) return 'fas fa-globe';
  const navLower = navegadorInfo.toLowerCase();
  if (navLower.includes('edge')) return 'fab fa-edge';
  if (navLower.includes('opera') || navLower.includes('opr')) return 'fab fa-opera';
  if (navLower.includes('chrome')) return 'fab fa-chrome';
  if (navLower.includes('firefox')) return 'fab fa-firefox-browser';
  if (navLower.includes('safari')) return 'fab fa-safari';
  return 'fas fa-globe';
}

const getColorNavegador = (navegadorInfo) => {
  if (!navegadorInfo) return '';
  const navLower = navegadorInfo.toLowerCase();
  if (navLower.includes('edge')) return 'text-edge';
  if (navLower.includes('opera') || navLower.includes('opr')) return 'text-opera';
  if (navLower.includes('chrome')) return 'text-chrome';
  if (navLower.includes('firefox')) return 'text-firefox';
  if (navLower.includes('safari')) return 'text-safari';
  return 'text-web';
}

const getNombreNavegador = (navegadorInfo) => {
  if (!navegadorInfo) return '-';
  const navLower = navegadorInfo.toLowerCase();
  if (navLower.includes('edge')) return 'Edge';
  if (navLower.includes('opera') || navLower.includes('opr')) return 'Opera';
  if (navLower.includes('chrome')) return 'Chrome';
  if (navLower.includes('firefox')) return 'Firefox';
  if (navLower.includes('safari')) return 'Safari';
  return navegadorInfo.split(' ')[0] || 'Navegador';
}

// 🔥 PARSEO INTELIGENTE DEFINITIVO (SALVA LAS PAPAS DEL FORMATO VIEJO)
const parseDetalles = (detalles) => {
  if (!detalles) return {}
  let d = detalles
  if (typeof detalles === 'string') {
    try { d = JSON.parse(detalles) } catch (e) { return {} }
  }
  
  const adaptado = {}

  // 🚨 CASO 1: El JSON entero es UN SOLO CAMBIO suelto (el viejo formato que me pasaste)
  // Ej: {"tipo":"CAMBIO", "nuevo":"Juanitardo", "anterior":"Juanito"}
  if (d.anterior !== undefined && d.nuevo !== undefined) {
      return {
        "Modificación": { tipo: 'CAMBIO', anterior: d.anterior, nuevo: d.nuevo }
      }
  }
  
  // 🚨 CASO 2: Es el formato nuevo ordenado (Tiene la caja "cambios")
  if (d.cambios) {
    for (const [k, v] of Object.entries(d.cambios)) {
      adaptado[k] = { tipo: 'CAMBIO', anterior: v.anterior, nuevo: v.nuevo }
    }
  }

  // 🚨 CASO 3: Recorremos todo lo demás (valores sueltos o cambios anidados)
  for (const [key, value] of Object.entries(d)) {
    if (key === 'cambios' || key === '__meta__') continue;

    // Si detecta un objeto anidado que tiene anterior y nuevo
    if (value && typeof value === 'object' && value.anterior !== undefined && value.nuevo !== undefined) {
      adaptado[key] = { tipo: 'CAMBIO', anterior: value.anterior, nuevo: value.nuevo }
    } 
    // Si viene directo con el tipo seteado
    else if (value && typeof value === 'object' && value.tipo === 'CAMBIO') {
       adaptado[key] = value; 
    }
    // Si es un valor suelto normal (ej: motivo_anulacion, monto_devuelto, etc.)
    else {
      adaptado[key] = { tipo: 'VALOR', valor: value }
    }
  }
  
  return adaptado
}

const isEmpty = (d) => Object.keys(parseDetalles(d)).length === 0

const formatValue = (val) => {
  if (val === null || val === undefined) return '-'
  if (val === true) return 'Sí'
  if (val === false) return 'No'
  if (Array.isArray(val)) return val.join(' | ')
  if (typeof val === 'object') return JSON.stringify(val)
  return val
}

const formatearClave = (clave) => {
  if (!clave) return ''
  return clave.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
}

const formatFecha = (f) => (f ? new Date(f).toLocaleDateString('es-AR') : '-')
const formatHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : ''

const getClaseAccion = (accion) => {
  const map = {
    CREAR: 'estado-success',
    EDITAR: 'estado-info',
    ELIMINAR: 'estado-danger',
    ANULAR_VENTA: 'estado-danger', 
    AJUSTE_STOCK: 'estado-warning' 
  }
  return map[accion] || 'estado-secondary'
}

const cargarAuditoria = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', ...(token && { 'Authorization': `Token ${token}` }) };
    const res = await axios.get(API_URL, { headers });
    
    let datos = [];
    if (Array.isArray(res.data)) datos = res.data;
    else if (res.data && Array.isArray(res.data.results)) datos = res.data.results;
    else if (res.data && Array.isArray(res.data.data)) datos = res.data.data;
    
    logs.value = datos;
  } catch (err) {
    console.error('❌ Error cargando auditoría:', err);
  } finally {
    loading.value = false;
  }
}

const logsFiltrados = computed(() => {
  return logs.value.filter((log) => {
    const term = filtros.value.busqueda.toLowerCase()
    const match = !term ||
      (log.usuario_nombre && log.usuario_nombre.toLowerCase().includes(term)) ||
      (log.modelo_afectado && log.modelo_afectado.toLowerCase().includes(term))
    const matchAccion = !filtros.value.accion || log.accion === filtros.value.accion
    return match && matchAccion
  })
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(logsFiltrados.value.length / itemsPorPagina)))
const logsPaginados = computed(() => {
  const start = (pagina.value - 1) * itemsPorPagina
  return logsFiltrados.value.slice(start, start + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }
const limpiarFiltros = () => { filtros.value = { busqueda: '', accion: '' }; pagina.value = 1 }
const abrirDetalles = (log) => { logSeleccionado.value = log; mostrarModal.value = true }
const cerrarModal = () => { mostrarModal.value = false; logSeleccionado.value = null }

watch(filtros, () => { pagina.value = 1 }, { deep: true })
onMounted(() => { cargarAuditoria() })
</script>

<style scoped>
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-color); position: relative; overflow: hidden; }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header-content p { color: var(--text-secondary); margin-top: 8px; }
.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; align-items: end; }
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; }
.filter-input { padding: 12px; border-radius: 10px; border: 2px solid var(--border-color); background-color: #1e293b; color: #f1f5f9; width: 100%; box-sizing: border-box; outline: none; transition: border-color 0.3s; }
.filter-input:focus { border-color: #3b82f6; }
.filter-input option { background-color: #1e293b; color: white; padding: 10px; }
.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px; border-radius: 10px; cursor: pointer; font-weight: 700; }
.table-container { overflow-x: auto; border-radius: 16px; margin-bottom: 25px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); }
.users-table th { background: var(--accent-color); color: white; padding: 18px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; }
.users-table td { padding: 14px; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); }

/* ESTADOS */
.badge-estado { padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; }
.estado-success { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; }
.estado-info { background: rgba(14, 165, 233, 0.15); color: #0ea5e9; border: 1px solid #0ea5e9; }
.estado-danger { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid #ef4444; }
.estado-warning { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid #f59e0b; }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-tertiary); border: 1px solid var(--text-tertiary); }

.action-button { padding: 8px 16px; border-radius: 10px; font-weight: 800; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-tertiary); color: var(--text-primary); }
.action-button:hover { background: var(--hover-bg); }
.pagination { display: flex; justify-content: center; gap: 20px; align-items: center; }
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 800; }
.pagination button:disabled { opacity: 0.5; }

.loading-overlay { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; color: var(--text-secondary); }
.spinner { border: 4px solid rgba(255, 255, 255, 0.1); border-left-color: #0ea5e9; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* CELDA NAVEGADOR */
.browser-cell { display: flex; flex-direction: column; gap: 4px; }
.browser-main { display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 0.9rem; color: var(--text-primary); }
.ip-sub { font-size: 0.75rem; color: var(--text-secondary); font-family: monospace; opacity: 0.8; }
.os-sub { font-size: 0.7rem; color: #8b5cf6; background: rgba(139, 92, 246, 0.1); padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; width: fit-content; }

/* MODAL */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: var(--bg-secondary); width: 850px; max-width: 95vw; border-radius: 16px; border: 1px solid var(--border-color); position: relative; max-height: 90vh; display: flex; flex-direction: column; }
.modal-close { position: absolute; top: 15px; right: 15px; background: transparent; border: none; font-size: 1.5rem; color: var(--text-secondary); cursor: pointer; }
.modal-header-custom { padding: 25px; border-bottom: 1px solid var(--border-color); background: var(--bg-primary); border-radius: 16px 16px 0 0; }
.modal-header-custom h2 { margin: 0; color: var(--text-primary); }
.modal-subtitle { color: var(--text-secondary); margin-top: 5px; font-size: 0.9rem; }
.modal-body-custom { padding: 25px; overflow-y: auto; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.info-item { background: var(--hover-bg); padding: 15px; border-radius: 10px; display: flex; flex-direction: column; }
.label { font-size: 0.7rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; }
.value { font-size: 1rem; color: var(--text-primary); font-weight: 600; }
.sub-value { font-size: 0.8rem; color: var(--text-secondary); margin-top: 2px; display: flex; align-items: center; gap: 5px; }
.divider { border: 0; border-top: 1px solid var(--border-color); margin: 20px 0; opacity: 0.3; }
.section-title { color: var(--text-primary); font-size: 1.1rem; margin-bottom: 15px; font-weight: 700; border-left: 4px solid var(--accent-color); padding-left: 10px; }
.modal-footer-custom { padding: 20px; border-top: 1px solid var(--border-color); text-align: right; background: var(--bg-primary); border-radius: 0 0 16px 16px; }

/* TABLA DETALLES */
.diff-wrapper { border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: var(--bg-primary); }
.detail-table { width: 100%; border-collapse: collapse; }
.detail-table th { text-align: left; padding: 12px 15px; background: var(--bg-tertiary); color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; font-weight: 700; border-bottom: 1px solid var(--border-color); }
.detail-table td { padding: 10px 15px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
.field-col { color: var(--accent-color); font-weight: 600; font-size: 0.9rem; width: 30%; }
.value-col { font-family: monospace; font-size: 0.95rem; color: var(--text-primary); }
.row-changed { background: rgba(234, 179, 8, 0.15); }
.row-changed .field-col { color: #f59e0b; }
.changed-flag { background: #f59e0b; color: #000; font-size: 0.6rem; padding: 2px 5px; border-radius: 4px; margin-left: 8px; vertical-align: middle; }

/* 🔥 ESTILOS PARA LA DATA DE AUDITORIA */
.static-val { font-weight: 600; color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 6px; display: inline-block;} 
.change-container { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.val-old { color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 4px 8px; border-radius: 6px; text-decoration: line-through; opacity: 0.7; }
.arrow { color: var(--text-secondary); font-size: 0.8rem; }
.val-new { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.3); }
.no-data { padding: 20px; text-align: center; font-style: italic; color: var(--text-secondary); }

/* COLORES NAVEGADOR */
.text-edge { color: #3b82f6; }
.text-chrome { color: #10b981; }
.text-firefox { color: #f97316; }
.text-opera { color: #ef4444; }
.text-safari { color: #0ea5e9; }
.text-web { color: #8b5cf6; }
</style>