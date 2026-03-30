<template>
  <div class="list-container">
    <div class="list-card">
      
      <div class="list-header">
        <div class="header-content">
          <h1><i class="fas fa-shield-alt"></i> AUDITORÍA DEL SISTEMA</h1>
          <p>Trazabilidad completa de movimientos unificada</p>
        </div>
      </div>

      <div class="modules-chips-container">
        <button 
          v-for="mod in modulosDisponibles" 
          :key="mod.id" 
          @click="filtros.modulo = mod.id; pagina = 1"
          class="module-chip"
          :class="{ 'active': mod.id === filtros.modulo }"
        >
          <i :class="mod.icon"></i> {{ mod.label }}
        </button>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group" style="grid-column: span 2;">
            <label>Buscador Inteligente</label>
            <div class="search-wrapper">
              <i class="fas fa-search search-icon"></i>
              <input v-model="filtros.busqueda" placeholder="Buscar por IP, Acción, Usuario o Detalle..." class="filter-input search-input"/>
            </div>
          </div>
          
          <div class="filter-group">
            <label>Usuario Responsable</label>
            <select v-model="filtros.usuario" class="filter-input">
              <option value="">Todos los usuarios</option>
              <option v-for="usr in usuariosUnicos" :key="usr" :value="usr">
                {{ usr }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Tipo de Acción</label>
            <select v-model="filtros.tipo_accion" class="filter-input">
              <option value="">Cualquier movimiento</option>
              <option value="CREACION">Creaciones / Altas</option>
              <option value="EDICION">Ediciones / Modificaciones</option>
              <option value="ELIMINACION">Eliminaciones / Anulaciones</option>
              <option value="ACCESO">Accesos (Login / Logout)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Fecha Desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input" />
          </div>
          <div class="filter-group">
            <label>Fecha Hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input" />
          </div>

          <div class="filter-group" style="display: flex; align-items: flex-end;">
            <button @click="limpiarFiltros" class="clear-filters-btn" style="width: 100%; height: 42px;">
              <i class="fas fa-eraser"></i> Limpiar
            </button>
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
              <th>Módulo / Acción</th>
              <th>Registro Afectado</th>
              <th>Conexión / Origen</th>
              <th style="text-align: center;">Detalles</th>
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
                <div style="font-weight:600; color: var(--text-primary);">{{ log.usuario_nombre || 'Sistema' }}</div>
                <div style="font-size:0.75em; opacity:0.8; color: var(--text-tertiary);">{{ log.usuario_rol }}</div>
              </td>
              <td>
                <div style="display:flex; flex-direction:column; gap: 6px; align-items: flex-start;">
                  <span class="badge-modulo">
                    <i :class="getIconoModulo(determinarModulo(log))"></i> {{ getNombreModulo(determinarModulo(log)) }}
                  </span>
                  <span class="badge-estado" :class="getClaseAccion(log.accion)">{{ log.accion.replace(/_/g, ' ') }}</span>
                </div>
              </td>
              <td>
                <strong style="color: var(--text-primary);">{{ log.modelo_afectado || 'Sistema General' }}</strong>
                <span v-if="log.objeto_id" style="font-size:0.8em; margin-left:5px; color: var(--accent-color); font-family: monospace;">#{{ log.objeto_id }}</span>
              </td>
              
              <td>
                <div class="browser-cell">
                  <div class="browser-main" :class="getColorNavegador(log.navegador_info)">
                    <i :class="getIconoNavegador(log.navegador_info)" style="margin-right:5px;"></i>
                    <span>{{ getNombreNavegador(log.navegador_info) }}</span>
                  </div>
                  <div class="ip-sub"><i class="fas fa-network-wired" style="font-size: 0.8em; margin-right: 3px;"></i> {{ log.ip_address || 'Sin IP' }}</div>
                  <div v-if="log.sistema_operativo" class="os-sub">
                    <i class="fas fa-desktop"></i> {{ log.sistema_operativo }}
                  </div>
                </div>
              </td>
              
              <td style="text-align: center;">
                <button @click="abrirDetalles(log)" class="action-button edit" title="Ver Ficha Detallada">
                  <i class="fas fa-eye"></i> Ver
                </button>
              </td>
            </tr>
            <tr v-if="!loading && logsPaginados.length === 0">
              <td colspan="6" style="text-align:center; padding:60px;">
                <i class="fas fa-search" style="font-size:3rem; opacity:0.2; margin-bottom:15px; display:block;"></i>
                <h3 style="color: var(--text-secondary); margin: 0;">No se encontraron registros</h3>
                <p style="color: var(--text-tertiary); font-size: 0.9rem;">Probá ajustando los filtros de búsqueda.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="logsPaginados.length > 0" class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1"><i class="fas fa-chevron-left"></i> Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente <i class="fas fa-chevron-right"></i></button>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModal">&times;</button>
        
        <div class="modal-header-custom" :class="getClaseAccion(logSeleccionado?.accion)">
          <h2>Reporte #{{ logSeleccionado?.id }} - {{ logSeleccionado?.accion.replace(/_/g, ' ') }}</h2>
          <p class="modal-subtitle">Objeto: {{ logSeleccionado?.modelo_afectado || 'Sistema' }} <span v-if="logSeleccionado?.objeto_id">#{{ logSeleccionado?.objeto_id }}</span></p>
        </div>

        <div class="modal-body-custom">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">Responsable</span>
              <span class="value">{{ logSeleccionado?.usuario_nombre || 'Sistema' }}</span>
              <span v-if="logSeleccionado?.usuario_email" class="sub-value">
                <i class="fas fa-envelope"></i> {{ logSeleccionado?.usuario_email }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">Conexión y Origen</span>
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
              <i class="fas fa-info-circle"></i> No hay detalles adicionales registrados para este movimiento.
            </div>
          </div>
        </div>
        
        <div class="modal-footer-custom">
          <button @click="cerrarModal" class="clear-filters-btn" style="width: auto;"><i class="fas fa-check"></i> Entendido</button>
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
const filtros = ref({ 
  busqueda: '', 
  modulo: '', 
  usuario: '', 
  tipo_accion: '', 
  fechaDesde: '', 
  fechaHasta: '' 
})
const pagina = ref(1)
const itemsPorPagina = 10
const mostrarModal = ref(false)
const logSeleccionado = ref(null)
const loading = ref(false)

const modulosDisponibles = [
  { id: '', label: 'Todos', icon: 'fas fa-layer-group' },
  { id: 'AUTENTICACION', label: 'Accesos', icon: 'fas fa-user-shield' },
  { id: 'VENTAS', label: 'Facturación', icon: 'fas fa-cash-register' },
  { id: 'TURNOS', label: 'Turnos', icon: 'fas fa-calendar-check' },
  { id: 'CAJA', label: 'Caja', icon: 'fas fa-box-open' },
  { id: 'INVENTARIO', label: 'Inventario', icon: 'fas fa-boxes' },
  { id: 'USUARIOS', label: 'Usuarios', icon: 'fas fa-users' }
]

const determinarModulo = (log) => {
  if (!log) return 'OTROS';
  const modelo = (log.modelo_afectado || '').toLowerCase();
  const accion = (log.accion || '').toLowerCase();

  if (accion.includes('login') || accion.includes('logout') || modelo.includes('sesion') && !modelo.includes('caja')) return 'AUTENTICACION';
  if (modelo.includes('venta') || modelo.includes('nota') || accion.includes('anular_venta')) return 'VENTAS';
  if (modelo.includes('turno') || modelo.includes('servicio')) return 'TURNOS';
  if (modelo.includes('caja') || modelo.includes('movimiento') || accion.includes('caja') || accion.includes('ingreso') || accion.includes('egreso')) return 'CAJA';
  if (modelo.includes('producto') || modelo.includes('stock') || modelo.includes('categoria') || accion.includes('ajuste')) return 'INVENTARIO';
  if (modelo.includes('usuario') || modelo.includes('cliente') || modelo.includes('peluquero')) return 'USUARIOS';

  return 'OTROS';
}

const getNombreModulo = (modId) => {
  const mod = modulosDisponibles.find(m => m.id === modId);
  return mod ? mod.label : 'Sistema General';
}

const getIconoModulo = (modId) => {
  const mod = modulosDisponibles.find(m => m.id === modId);
  return mod ? mod.icon : 'fas fa-server';
}

const usuariosUnicos = computed(() => {
  const users = logs.value.map(l => l.usuario_nombre || 'Sistema').filter(u => u);
  return [...new Set(users)].sort();
});

const getTipoAccionGeneral = (accion) => {
  const a = (accion || '').toUpperCase();
  if (a.includes('CREAR') || a.includes('INGRESO') || a.includes('APERTURA')) return 'CREACION';
  if (a.includes('EDITAR') || a.includes('ACTUALIZAR') || a.includes('AJUSTE')) return 'EDICION';
  if (a.includes('ELIMINAR') || a.includes('ANULAR') || a.includes('CIERRE') || a.includes('EGRESO')) return 'ELIMINACION';
  if (a.includes('LOGIN') || a.includes('LOGOUT') || a.includes('ACCESO')) return 'ACCESO';
  return 'OTRO';
};

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
  if (!navegadorInfo || navegadorInfo === 'Desconocido' || navegadorInfo === 'Sistema' || navegadorInfo === '-') {
    return 'Sistema';
  }
  const navLower = navegadorInfo.toLowerCase();
  if (navLower.includes('edge') || navLower.includes('edg')) return 'Edge';
  if (navLower.includes('brave')) return 'Brave';
  if (navLower.includes('opera') || navLower.includes('opr')) return 'Opera';
  if (navLower.includes('firefox')) return 'Firefox';
  if (navLower.includes('chrome')) return 'Chrome';
  if (navLower.includes('safari')) return 'Safari';
  return navegadorInfo.split(' ')[0] || 'Navegador';
}

const parseDetalles = (detalles) => {
  if (!detalles) return {}
  let d = detalles
  if (typeof detalles === 'string') {
    try { d = JSON.parse(detalles) } catch (e) { return {} }
  }
  const adaptado = {}
  if (d.anterior !== undefined && d.nuevo !== undefined) {
      return { "Modificación": { tipo: 'CAMBIO', anterior: d.anterior, nuevo: d.nuevo } }
  }
  if (d.cambios) {
    for (const [k, v] of Object.entries(d.cambios)) {
      adaptado[k] = { tipo: 'CAMBIO', anterior: v.anterior, nuevo: v.nuevo }
    }
  }
  for (const [key, value] of Object.entries(d)) {
    if (key === 'cambios' || key === '__meta__') continue;
    if (value && typeof value === 'object' && value.anterior !== undefined && value.nuevo !== undefined) {
      adaptado[key] = { tipo: 'CAMBIO', anterior: value.anterior, nuevo: value.nuevo }
    } 
    else if (value && typeof value === 'object' && value.tipo === 'CAMBIO') {
       adaptado[key] = value; 
    }
    else if (value && typeof value === 'object' && value.tipo === 'VALOR') {
      adaptado[key] = value;
    }
    else {
      adaptado[key] = { tipo: 'VALOR', valor: value }
    }
  }
  return adaptado
}

const isEmpty = (d) => Object.keys(parseDetalles(d)).length === 0

const formatValue = (val) => {
  if (val === null || val === undefined || val === '') return '-'
  if (val === true) return 'Sí'
  if (val === false) return 'No'
  if (Array.isArray(val)) return val.join(' | ')
  if (typeof val === 'string' && val.includes('T') && val.includes('-') && val.length > 15) {
    const d = new Date(val);
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString('es-AR') + ' ' + d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) + ' hs';
    }
  }
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
  if (!accion) return 'estado-secondary';
  const a = accion.toUpperCase();
  if (a.includes('CREAR') || a.includes('INGRESO') || a.includes('APERTURA') || a.includes('LOGIN')) return 'estado-success';
  if (a.includes('EDITAR')) return 'estado-info';
  if (a.includes('ELIMINAR') || a.includes('ANULAR') || a.includes('CIERRE') || a.includes('EGRESO') || a.includes('LOGOUT')) return 'estado-danger';
  if (a.includes('AJUSTE')) return 'estado-warning';
  return 'estado-secondary';
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
    const term = filtros.value.busqueda.toLowerCase();
    const matchBusqueda = !term ||
      (log.usuario_nombre && log.usuario_nombre.toLowerCase().includes(term)) ||
      (log.modelo_afectado && log.modelo_afectado.toLowerCase().includes(term)) ||
      (log.accion && log.accion.toLowerCase().includes(term)) ||
      (log.ip_address && log.ip_address.toLowerCase().includes(term)) ||
      (log.detalles && typeof log.detalles === 'string' && log.detalles.toLowerCase().includes(term));

    const mod = determinarModulo(log);
    const matchModulo = !filtros.value.modulo || mod === filtros.value.modulo;

    const usr = log.usuario_nombre || 'Sistema';
    const matchUsuario = !filtros.value.usuario || usr === filtros.value.usuario;

    const tipoAccion = getTipoAccionGeneral(log.accion);
    const matchTipoAccion = !filtros.value.tipo_accion || tipoAccion === filtros.value.tipo_accion;

    let matchFechas = true;
    if (filtros.value.fechaDesde || filtros.value.fechaHasta) {
        const fechaLog = new Date(log.fecha).getTime();
        if (filtros.value.fechaDesde) {
            const dDesde = new Date(filtros.value.fechaDesde + 'T00:00:00').getTime();
            if (fechaLog < dDesde) matchFechas = false;
        }
        if (filtros.value.fechaHasta) {
            const dHasta = new Date(filtros.value.fechaHasta + 'T23:59:59').getTime();
            if (fechaLog > dHasta) matchFechas = false;
        }
    }

    return matchBusqueda && matchModulo && matchUsuario && matchTipoAccion && matchFechas;
  })
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(logsFiltrados.value.length / itemsPorPagina)))
const logsPaginados = computed(() => {
  const start = (pagina.value - 1) * itemsPorPagina
  return logsFiltrados.value.slice(start, start + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

const limpiarFiltros = () => { 
  filtros.value = { busqueda: '', modulo: '', usuario: '', tipo_accion: '', fechaDesde: '', fechaHasta: '' }; 
  pagina.value = 1 
}

const abrirDetalles = (log) => { logSeleccionado.value = log; mostrarModal.value = true }
const cerrarModal = () => { mostrarModal.value = false; logSeleccionado.value = null }

watch(filtros, () => { pagina.value = 1 }, { deep: true })
onMounted(() => { cargarAuditoria() })
</script>

<style scoped>
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-color); position: relative; overflow: hidden; margin: 0 auto; }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ac2e7, #0ac2e7, #0ac2e7); }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid var(--border-color); padding-bottom: 20px; }
.header-content h1 { font-size: 2rem; font-weight: 900; color: var(--text-primary); margin: 0; display: flex; align-items: center; gap: 10px; }
.header-content h1 i { color: #8b5cf6; }
.header-content p { color: var(--text-secondary); margin-top: 5px; font-size: 0.95rem; }

/* 🔥 ESTILOS SUTILES PARA LOS CHIPS 🔥 */
.modules-chips-container { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 25px; }
.module-chip { 
  padding: 8px 16px; 
  border-radius: 20px; 
  border: 1px solid var(--border-color); 
  background: var(--bg-tertiary); 
  color: var(--text-secondary); 
  font-weight: 600; 
  font-size: 0.85rem; 
  cursor: pointer; 
  transition: all 0.2s ease; 
  display: flex; 
  align-items: center; 
  gap: 8px; 
}
.module-chip:hover { 
  background: var(--hover-bg); 
  color: var(--text-primary); 
  transform: translateY(-1px); 
}
.module-chip.active { 
  background: var(--accent-color); 
  color: white; 
  border-color: var(--accent-color); 
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2); 
}

/* 🔥 BADGES DE TABLA LIMPIOS Y PROFESIONALES 🔥 */
.badge-modulo { 
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary); 
  font-size: 0.75rem; 
  font-weight: 600; 
  text-transform: uppercase; 
  letter-spacing: 0.5px; 
}

.badge-modulo i { font-size: 0.85rem; opacity: 0.8; }

.badge-estado { 
  padding: 4px 10px; 
  border-radius: 6px; 
  font-size: 0.65rem; 
  font-weight: 800; 
  text-transform: uppercase; 
  display: inline-block; 
  letter-spacing: 0.5px; 
}

/* Los colores se usan SÓLO para la acción (verde=crear, azul=editar, rojo=borrar) */
.estado-success { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.estado-info { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.2); }
.estado-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
.estado-warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-tertiary); border: 1px solid var(--border-color); }

/* CONTENEDOR DE FILTROS */
.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 20px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; align-items: end; }
.filter-group label { font-weight: 700; margin-bottom: 8px; display: block; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; }
.filter-input { padding: 10px 14px; border-radius: 10px; border: 2px solid var(--border-color); background-color: var(--bg-primary); color: var(--text-primary); width: 100%; box-sizing: border-box; outline: none; transition: border-color 0.3s; font-size: 0.9rem; }
.filter-input:focus { border-color: #8b5cf6; }
.search-wrapper { position: relative; }
.search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); }
.search-input { padding-left: 40px; }

.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 10px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: 0.3s; display: flex; align-items: center; justify-content: center; gap: 8px; text-transform: uppercase; font-size: 0.8rem; }
.clear-filters-btn:hover { background: var(--hover-bg); border-color: var(--text-secondary); }

.table-container { overflow-x: auto; border-radius: 16px; margin-bottom: 25px; border: 1px solid var(--border-color); }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); }
.users-table th { background: var(--bg-secondary); color: var(--text-secondary); padding: 15px; text-align: left; font-weight: 800; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; border-bottom: 2px solid var(--border-color); }
.users-table td { padding: 12px 15px; border-bottom: 1px solid var(--border-color); color: var(--text-secondary); vertical-align: middle;}
.users-table tr:hover { background: var(--hover-bg); }

.action-button { padding: 8px 12px; border-radius: 8px; font-weight: 700; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-tertiary); color: var(--text-primary); transition: 0.2s; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 6px; }
.action-button:hover { background: var(--hover-bg); transform: translateY(-2px); }

.pagination { display: flex; justify-content: center; gap: 20px; align-items: center; margin-top: 20px;}
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 10px 20px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: 0.2s; display: flex; align-items: center; gap: 8px; }
.pagination button:hover:not(:disabled) { background: var(--hover-bg); border-color: var(--text-secondary); }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination span { font-weight: 700; color: var(--text-secondary); font-size: 0.9rem; }

.loading-overlay { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px; color: var(--text-secondary); }
.spinner { border: 4px solid rgba(255, 255, 255, 0.1); border-left-color: #8b5cf6; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* CELDA NAVEGADOR */
.browser-cell { display: flex; flex-direction: column; gap: 4px; }
.browser-main { display: flex; align-items: center; gap: 6px; font-weight: 700; font-size: 0.85rem; color: var(--text-primary); }
.ip-sub { font-size: 0.75rem; color: var(--text-secondary); font-family: monospace; opacity: 0.9; }
.os-sub { font-size: 0.65rem; color: #8b5cf6; background: rgba(139, 92, 246, 0.1); padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; width: fit-content; text-transform: uppercase; font-weight: 800; }

/* MODAL */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeIn 0.2s ease; }
.modal-content { background: var(--bg-secondary); width: 850px; max-width: 95vw; border-radius: 16px; border: 1px solid var(--border-color); position: relative; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
.modal-close { position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,0.2); border: none; font-size: 1.5rem; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; z-index: 10; }
.modal-close:hover { background: #ef4444; transform: rotate(90deg); }

.modal-header-custom { padding: 30px; border-bottom: 1px solid var(--border-color); background: var(--bg-primary); border-radius: 16px 16px 0 0; position: relative; overflow: hidden; }
.modal-header-custom h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; font-weight: 900; position: relative; z-index: 2; }
.modal-subtitle { color: var(--text-secondary); margin-top: 8px; font-size: 0.95rem; font-weight: 600; position: relative; z-index: 2; }

.modal-header-custom.estado-success::before { content:''; position:absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(16,185,129,0.1), transparent); }
.modal-header-custom.estado-info::before { content:''; position:absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(14,165,233,0.1), transparent); }
.modal-header-custom.estado-danger::before { content:''; position:absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(239,68,68,0.1), transparent); }
.modal-header-custom.estado-warning::before { content:''; position:absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(245,158,11,0.1), transparent); }

.modal-body-custom { padding: 30px; overflow-y: auto; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
.info-item { background: var(--bg-primary); border: 1px solid var(--border-color); padding: 20px; border-radius: 12px; display: flex; flex-direction: column; gap: 5px; }
.label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 800; letter-spacing: 0.5px; }
.value { font-size: 1.1rem; color: var(--text-primary); font-weight: 700; }
.sub-value { font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px; display: flex; align-items: center; gap: 6px; }

.divider { border: 0; border-top: 2px dashed var(--border-color); margin: 30px 0; opacity: 0.5; }
.section-title { color: var(--text-primary); font-size: 1.1rem; margin-bottom: 20px; font-weight: 800; border-left: 4px solid var(--accent-color); padding-left: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.modal-footer-custom { padding: 20px 30px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; background: var(--bg-primary); border-radius: 0 0 16px 16px; }

/* TABLA DETALLES MODAL */
.diff-wrapper { border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: var(--bg-primary); }
.detail-table { width: 100%; border-collapse: collapse; }
.detail-table th { text-align: left; padding: 15px 20px; background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; font-weight: 800; border-bottom: 2px solid var(--border-color); }
.detail-table td { padding: 15px 20px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
.field-col { color: var(--text-primary); font-weight: 700; font-size: 0.95rem; width: 35%; }
.value-col { font-family: 'Courier New', Courier, monospace; font-size: 0.95rem; color: var(--text-secondary); font-weight: 600; }
.row-changed { background: rgba(245, 158, 11, 0.05); }
.row-changed .field-col { color: #f59e0b; }
.changed-flag { background: #f59e0b; color: white; font-size: 0.6rem; padding: 3px 6px; border-radius: 4px; margin-left: 10px; vertical-align: middle; font-weight: 800; }

.static-val { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 6px 10px; border-radius: 6px; display: inline-block; border: 1px solid rgba(16, 185, 129, 0.2);} 
.change-container { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.val-old { color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 6px 10px; border-radius: 6px; text-decoration: line-through; opacity: 0.8; border: 1px solid rgba(239, 68, 68, 0.2);}
.arrow { color: var(--text-tertiary); font-size: 1.2rem; }
.val-new { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 6px 10px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.4); }
.no-data { padding: 30px; text-align: center; color: var(--text-tertiary); font-size: 0.95rem; }

/* COLORES NAVEGADOR */
.text-edge { color: #3b82f6; }
.text-chrome { color: #10b981; }
.text-firefox { color: #f97316; }
.text-opera { color: #ef4444; }
.text-safari { color: #0ea5e9; }
.text-web { color: #8b5cf6; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .info-grid { grid-template-columns: 1fr; }
  .filters-grid { grid-template-columns: 1fr; }
  .list-card { padding: 20px; }
  .change-container { flex-direction: column; align-items: flex-start; gap: 5px; }
  .arrow { transform: rotate(90deg); margin-left: 15px; }
  .modules-chips-container { overflow-x: auto; flex-wrap: nowrap; padding-bottom: 10px; }
  .module-chip { white-space: nowrap; }
}
</style>