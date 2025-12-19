<template>
  <div class="list-container">
    <div class="list-card">
      
      <div class="list-header">
        <div class="header-content">
          <h1>AUDITORIA DEL SISTEMA</h1>
          <p>Trazabilidad completa de movimientos</p>
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
              </select>
          </div>
          <div class="filter-group">
            <button @click="limpiarFiltros" class="clear-filters-btn">Limpiar</button>
          </div>
        </div>
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
              <td><span class="badge-estado" :class="getClaseAccion(log.accion)">{{ log.accion }}</span></td>
              <td>
                <strong>{{ log.modelo_afectado }}</strong>
                <span style="font-size:0.8em; margin-left:5px;">#{{ log.objeto_id }}</span>
              </td>
              
              <td>
                <div class="browser-cell">
                    <div class="browser-main" :class="detectarNavegador(log.detalles).colorClass">
                        <i :class="detectarNavegador(log.detalles).icon" style="margin-right:5px;"></i>
                        <span>{{ detectarNavegador(log.detalles).name }}</span>
                    </div>
                    <div class="ip-sub">{{ log.ip_address || '-' }}</div>
                </div>
              </td>
              
              <td>
                <button @click="abrirDetalles(log)" class="action-button edit">Ver Ficha</button>
              </td>
            </tr>
            <tr v-if="logsPaginados.length === 0"><td colspan="6" style="text-align:center; padding:20px;">Sin registros.</td></tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente</button>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModal">&times;</button>
        
        <div class="modal-header-custom" :class="getClaseAccion(logSeleccionado?.accion)">
          <h2>Reporte #{{ logSeleccionado?.id }} - {{ logSeleccionado?.accion }}</h2>
          <p class="modal-subtitle">Objeto: {{ logSeleccionado?.modelo_afectado }} #{{ logSeleccionado?.objeto_id }}</p>
        </div>

        <div class="modal-body-custom">
          <div class="info-grid">
             <div class="info-item">
                 <span class="label">Responsable</span>
                 <span class="value">{{ logSeleccionado?.usuario_nombre || 'Sistema' }}</span>
             </div>
             <div class="info-item">
                 <span class="label">Conexión</span>
                 <span class="value" style="font-size: 0.9rem;">
                    <i :class="detectarNavegador(logSeleccionado?.detalles).icon" style="margin-right:5px"></i>
                    {{ infoDispositivo(logSeleccionado?.detalles) }}
                 </span>
                 <span class="sub-value">Desde IP: {{ logSeleccionado?.ip_address }}</span>
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
                Sin detalles adicionales.
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
import axios from '../../utils/axiosConfig' 

const logs = ref([])
const filtros = ref({ busqueda: '', accion: '' })
const pagina = ref(1)
const itemsPorPagina = 10
const mostrarModal = ref(false)
const logSeleccionado = ref(null)

const cargarAuditoria = async () => {
  try {
    const res = await axios.get('/usuarios/api/auditoria/') 
    logs.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

const parseDetalles = (detalles) => {
  if (!detalles) return {}
  let d = detalles
  if (typeof detalles === 'string') {
    try { d = JSON.parse(detalles) } catch (e) { return {} }
  }
  const visible = {}
  for (const key in d) {
      if (key !== '__meta__') visible[key] = d[key]
  }
  if (d.cambios) { 
      const adaptado = {}
      for (const [k, v] of Object.entries(d.cambios)) {
          adaptado[k] = { tipo: 'CAMBIO', anterior: v.anterior, nuevo: v.nuevo }
      }
      return adaptado
  }
  return visible
}

const isEmpty = (d) => Object.keys(parseDetalles(d)).length === 0

// NAVEGADOR
const getRawUA = (detalles) => {
    if (!detalles) return ''
    let d = detalles
    if (typeof detalles === 'string') try { d = JSON.parse(detalles) } catch (e) { return '' }
    return (d.__meta__ && d.__meta__.navegador) ? d.__meta__.navegador : ''
}

const detectBrowser = (ua) => {
    if (!ua) return { name: '-', icon: 'fas fa-minus', colorClass: '' }
    if (ua.includes('Edg')) return { name: 'Edge', icon: 'fab fa-edge', colorClass: 'text-edge' }
    if (ua.includes('OPR') || ua.includes('Opera')) return { name: 'Opera', icon: 'fab fa-opera', colorClass: 'text-opera' }
    if (ua.includes('Chrome')) return { name: 'Chrome', icon: 'fab fa-chrome', colorClass: 'text-chrome' }
    if (ua.includes('Firefox')) return { name: 'Firefox', icon: 'fab fa-firefox-browser', colorClass: 'text-firefox' }
    if (ua.includes('Safari')) return { name: 'Safari', icon: 'fab fa-safari', colorClass: 'text-safari' }
    return { name: 'Web', icon: 'fas fa-globe', colorClass: 'text-web' }
}

const detectOS = (ua) => {
    if (!ua) return ''
    if (ua.includes('Windows')) return 'Windows'
    if (ua.includes('Mac')) return 'macOS'
    if (ua.includes('Linux')) return 'Linux'
    if (ua.includes('Android')) return 'Android'
    if (ua.includes('iPhone') || ua.includes('iPad')) return 'iOS'
    return 'PC'
}

const detecting = (detalles) => detectBrowser(getRawUA(detalles))
const detectarNavegador = detecting 

const infoDispositivo = (detalles) => {
    const ua = getRawUA(detalles)
    if (!ua) return 'No registrado'
    const browser = detectBrowser(ua).name
    const os = detectOS(ua)
    return `${browser} en ${os}`
}

const formatValue = (val) => {
    if (val === null || val === undefined) return '-'
    if (val === true) return 'Sí'
    if (val === false) return 'No'
    return val
}

const formatearClave = (clave) => {
  if (!clave) return ''
  return clave.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatFecha = (f) => f ? new Date(f).toLocaleDateString('es-AR') : '-'
const formatHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : ''

const getClaseAccion = (accion) => {
  const map = { 'CREAR': 'estado-success', 'EDITAR': 'estado-info', 'ELIMINAR': 'estado-danger' }
  return map[accion] || 'estado-secondary'
}

const logsFiltrados = computed(() => {
  return logs.value.filter(log => {
    const term = filtros.value.busqueda.toLowerCase()
    const match = !term || 
        (log.usuario_nombre && log.usuario_nombre.toLowerCase().includes(term)) || 
        (log.modelo_afectado && log.modelo_afectado.toLowerCase().includes(term)) || 
        (log.ip_address && log.ip_address.includes(term))
    const matchAccion = !filtros.value.accion || log.accion === filtros.value.accion
    return match && matchAccion
  })
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(logsFiltrados.value.length / itemsPorPagina)))
const logsPaginados = computed(() => {
  const start = (pagina.value - 1) * itemsPorPagina
  return logsFiltrados.value.slice(start, start + itemsPorPagina)
})

const paginaAnterior = () => { if(pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if(pagina.value < totalPaginas.value) pagina.value++ }
const limpiarFiltros = () => { filtros.value = { busqueda: '', accion: '' }; pagina.value = 1 }
const abrirDetalles = (log) => { logSeleccionado.value = log; mostrarModal.value = true }
const cerrarModal = () => { mostrarModal.value = false; logSeleccionado.value = null }

watch(filtros, () => { pagina.value = 1 }, { deep: true })
onMounted(cargarAuditoria)
</script>

<style scoped>
/* ESTILOS GENERALES (Tu base) */
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-color); position: relative; overflow: hidden; }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header-content p { color: var(--text-secondary); margin-top: 8px; }
.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.3s; }
.register-button:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); }
.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; align-items: end; }
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; }
/* Input y Select (Buscador y Combo de Acción) */
.filter-input { 
  padding: 12px; 
  border-radius: 10px; 
  border: 2px solid var(--border-color); 
  
  /* 🔥 CAMBIO DE COLOR DE FONDO Y TEXTO */
  background-color: #1e293b; /* Gris oscuro elegante */
  color: #f1f5f9; /* Texto casi blanco */
  
  width: 100%; 
  box-sizing: border-box;
  outline: none; /* Quitamos el borde azul feo por defecto */
  transition: border-color 0.3s;
}

.filter-input:focus {
  border-color: #3b82f6; /* Borde azul al hacer clic */
}

/* 🔥 ESTO ES PARA LAS OPCIONES DESPLEGABLES */
.filter-input option {
  background-color: #1e293b;
  color: white;
  padding: 10px;
}
.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px; border-radius: 10px; cursor: pointer; font-weight: 700; }
.table-container { overflow-x: auto; border-radius: 16px; margin-bottom: 25px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); }
.users-table th { background: var(--accent-color); color: white; padding: 18px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; }
.users-table td { padding: 14px; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); }

/* ESTADOS */
.badge-estado { padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; }
.estado-success { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; }
.estado-info { background: rgba(14, 165, 233, 0.15); color: #0ea5e9; border: 1px solid #0ea5e9; }
.estado-danger { background: rgba(239, 68, 68, 0.15); color: var(--error-color); border: 1px solid var(--error-color); }
.estado-warning { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid #f59e0b; }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-tertiary); border: 1px solid var(--text-tertiary); }

.action-button { padding: 8px 16px; border-radius: 10px; font-weight: 800; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-tertiary); color: var(--text-primary); }
.action-button:hover { background: var(--hover-bg); }
.pagination { display: flex; justify-content: center; gap: 20px; align-items: center; }
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 800; }
.pagination button:disabled { opacity: 0.5; }

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
.sub-value { font-size: 0.8rem; color: var(--text-secondary); margin-top: 2px; }
.divider { border: 0; border-top: 1px solid var(--border-color); margin: 20px 0; opacity: 0.3; }
.section-title { color: var(--text-primary); font-size: 1.1rem; margin-bottom: 15px; font-weight: 700; border-left: 4px solid var(--accent-color); padding-left: 10px; }
.modal-footer-custom { padding: 20px; border-top: 1px solid var(--border-color); text-align: right; background: var(--bg-primary); border-radius: 0 0 16px 16px; }

/* TABLA PRO */
.diff-wrapper { border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: var(--bg-primary); }
.detail-table { width: 100%; border-collapse: collapse; }
.detail-table th { text-align: left; padding: 12px 15px; background: var(--bg-tertiary); color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; font-weight: 700; border-bottom: 1px solid var(--border-color); }
.detail-table td { padding: 10px 15px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
.field-col { color: var(--accent-color); font-weight: 600; font-size: 0.9rem; width: 30%; }
.value-col { font-family: monospace; font-size: 0.95rem; color: var(--text-primary); }
.row-changed { background: rgba(234, 179, 8, 0.15); }
.row-changed .field-col { color: #f59e0b; }
.changed-flag { background: #f59e0b; color: #000; font-size: 0.6rem; padding: 2px 5px; border-radius: 4px; margin-left: 8px; vertical-align: middle; }
.static-val { opacity: 0.6; } 
.change-container { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.val-old { color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 4px 8px; border-radius: 6px; text-decoration: line-through; opacity: 0.7; }
.arrow { color: var(--text-secondary); font-size: 0.8rem; }
.val-new { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.3); }
.no-data { padding: 20px; text-align: center; font-style: italic; color: var(--text-secondary); }

/* CELDA NAVEGADOR Y COLORES */
.browser-cell { display: flex; flex-direction: column; }
.browser-main { display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 0.9rem; color: var(--text-primary); }
.ip-sub { font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px; font-family: monospace; opacity: 0.7; }

/* COLORES NAVEGADOR */
.text-edge { color: #3b82f6; }
.text-chrome { color: #10b981; }
.text-firefox { color: #f97316; }
.text-opera { color: #ef4444; }
.text-safari { color: #0ea5e9; }
.text-web { color: #8b5cf6; }
</style>