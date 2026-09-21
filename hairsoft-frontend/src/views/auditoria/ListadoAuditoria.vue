<template>
  <div class="list-container">
    <div class="list-card">

      <div class="list-header">
        <div class="header-content">
          <h1><i class="fas fa-shield-alt"></i> AUDITORÍA DEL SISTEMA</h1>
          <p>Trazabilidad integral: quién, cuándo, desde dónde, qué hizo y qué cambió</p>
        </div>
      </div>

      <!-- Módulos (filtro server-side) -->
      <div class="modules-chips-container">
        <button
          v-for="mod in modulosDisponibles"
          :key="mod.id"
          @click="filtros.modulo = mod.id"
          class="module-chip"
          :class="{ active: mod.id === filtros.modulo }"
        >
          <i :class="mod.icon"></i> {{ mod.label }}
        </button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group" style="grid-column: span 2;">
            <label>Buscador</label>
            <div class="search-wrapper">
              <i class="fas fa-search search-icon"></i>
              <input v-model="filtros.busqueda" placeholder="Usuario, email, modelo, #ID, IP, endpoint, mensaje..." class="filter-input search-input"/>
            </div>
          </div>

          <div class="filter-group">
            <label>Responsable</label>
            <input v-model="filtros.usuario" type="text" placeholder="Nombre o email..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Resultado</label>
            <select v-model="filtros.resultado" class="filter-input">
              <option value="">Todos</option>
              <option value="EXITO">Éxito</option>
              <option value="ERROR">Error</option>
              <option value="SISTEMA">Sistema (automático)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Acción</label>
            <select v-model="filtros.accion" class="filter-input">
              <option value="">Cualquier acción</option>
              <option v-for="a in accionesDisponibles" :key="a" :value="a">{{ a.replace(/_/g, ' ') }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input" />
          </div>
          <div class="filter-group">
            <label>Hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input" />
          </div>

          <div class="filter-group" style="display: flex; align-items: flex-end;">
            <button @click="limpiarFiltros" class="clear-filters-btn" style="width: 100%; height: 42px;">
              <i class="fas fa-eraser"></i> Limpiar
            </button>
          </div>
        </div>
      </div>

      <div v-if="filtros.idOperacion" class="operacion-active">
        <i class="fas fa-link"></i>
        Mostrando todos los eventos de la operación
        <code>#{{ filtros.idOperacion.slice(0, 8) }}</code>
        <button @click="filtros.idOperacion = ''" class="quitar-operacion" title="Quitar filtro de operación">&times;</button>
      </div>

      <div v-if="errorMsg" class="error-banner">
        <i class="fas fa-exclamation-triangle"></i> {{ errorMsg }}
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
              <th>Quién</th>
              <th>Módulo / Acción</th>
              <th>Resultado</th>
              <th>Sobre qué</th>
              <th>Desde dónde</th>
              <th style="text-align: center;">Operación</th>
              <th style="text-align: center;">Detalle</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>
                <div style="display:flex; flex-direction:column;">
                  <strong>{{ formatFecha(log.fecha) }}</strong>
                  <span style="font-size:0.8em; opacity:0.7;">{{ formatHora(log.fecha) }}</span>
                </div>
              </td>
              <td>
                <template v-if="esSistema(log)">
                  <span class="badge-sistema"><i class="fas fa-robot"></i> SISTEMA</span>
                  <div style="font-size:0.72em; opacity:0.8;">proceso automático</div>
                </template>
                <template v-else>
                  <div style="font-weight:600; color: var(--text-primary);">{{ log.usuario_nombre || 'Anónimo' }}</div>
                  <div style="font-size:0.75em; opacity:0.8; color: var(--text-tertiary);">
                    {{ log.usuario_email || 'sin email' }}<span v-if="log.usuario_rol"> · {{ log.usuario_rol }}</span>
                  </div>
                </template>
              </td>
              <td>
                <div style="display:flex; flex-direction:column; gap: 6px; align-items: flex-start;">
                  <span class="badge-modulo">
                    <i :class="getIconoModulo(log.modulo_efectivo || log.modulo)"></i> {{ getNombreModulo(log.modulo_efectivo || log.modulo) }}
                  </span>
                  <span class="badge-estado" :class="getClaseAccion(log.accion)">{{ log.accion.replace(/_/g, ' ') }}</span>
                  <span v-if="log.descripcion && log.descripcion !== '-'" class="desc-corta" :title="log.descripcion">{{ log.descripcion }}</span>
                </div>
              </td>
              <td>
                <span class="resultado-badge" :class="claseResultado(log.resultado)">
                  {{ log.resultado || 'EXITO' }}
                </span>
                <div v-if="log.resultado === 'ERROR' && log.mensaje" class="motivo-error" :title="log.mensaje">
                  <i class="fas fa-info-circle"></i> {{ truncar(log.mensaje, 40) }}
                </div>
              </td>
              <td>
                <strong style="color: var(--text-primary);">{{ log.modelo_afectado || 'Sistema General' }}</strong>
                <span v-if="log.objeto_id" style="font-size:0.8em; margin-left:5px; color: var(--accent-color); font-family: monospace;">#{{ log.objeto_id }}</span>
                <div v-if="log.objeto_nombre" style="font-size:0.78em; opacity:0.85;">{{ log.objeto_nombre }}</div>
                <div v-if="log.campos_modificados && log.campos_modificados.length" class="campos-afectados">
                  <span v-for="c in log.campos_modificados.slice(0, 5)" :key="c" class="campo-chip">{{ c }}</span>
                  <span v-if="log.campos_modificados.length > 5" class="campo-chip">+{{ log.campos_modificados.length - 5 }}</span>
                </div>
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
                <button
                  v-if="log.id_operacion"
                  @click="verOperacion(log.id_operacion)"
                  class="operation-chip"
                  :title="`Ver todos los eventos con id_operacion ${log.id_operacion}`"
                >
                  <i class="fas fa-link"></i>
                </button>
                <span v-else style="opacity:0.3;">—</span>
              </td>
              <td style="text-align: center;">
                <button @click="abrirDetalles(log)" class="action-button edit" title="Ver Ficha Detallada">
                  <i class="fas fa-eye"></i> Ver
                </button>
              </td>
            </tr>
            <tr v-if="!loading && logs.length === 0">
              <td colspan="8" style="text-align:center; padding:60px;">
                <i class="fas fa-search" style="font-size:3rem; opacity:0.2; margin-bottom:15px; display:block;"></i>
                <h3 style="color: var(--text-secondary); margin: 0;">No se encontraron registros</h3>
                <p style="color: var(--text-tertiary); font-size: 0.9rem;">Probá ajustando los filtros de búsqueda.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación server-side -->
      <div v-if="count > 0" class="pagination">
        <button @click="irPagina(pagina - 1)" :disabled="pagina <= 1"><i class="fas fa-chevron-left"></i> Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }} · {{ count }} registros</span>
        <button @click="irPagina(pagina + 1)" :disabled="pagina >= totalPaginas">Siguiente <i class="fas fa-chevron-right"></i></button>
      </div>
    </div>

    <!-- ================= MODAL DE DETALLE ================= -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModal">&times;</button>

        <div class="modal-header-custom" :class="claseResultado(detalle?.resultado)">
          <div class="modal-title-row">
            <h2>{{ (detalle?.accion || '').replace(/_/g, ' ') }} <span class="muted">· {{ getNombreModulo(detalle?.modulo_efectivo || detalle?.modulo) }}</span></h2>
            <span class="resultado-badge grande" :class="claseResultado(detalle?.resultado)">{{ detalle?.resultado || 'EXITO' }}</span>
          </div>
          <p class="modal-subtitle">Objeto: {{ detalle?.modelo_afectado || 'Sistema' }}
            <span v-if="detalle?.objeto_id"> · #{{ detalle?.objeto_id }}</span>
            <span v-if="detalle?.objeto_nombre"> · {{ detalle?.objeto_nombre }}</span>
          </p>
        </div>

        <div class="modal-body-custom">
          <div class="info-grid">
            <!-- Quién -->
            <div class="info-item">
              <span class="label">Quién</span>
              <template v-if="esSistema(detalle)">
                <span class="value badge-sistema"><i class="fas fa-robot"></i> SISTEMA</span>
                <span class="sub-value">proceso automático</span>
              </template>
              <template v-else>
                <span class="value">{{ detalle?.usuario_nombre || 'Anónimo' }}</span>
                <span class="sub-value" v-if="detalle?.usuario_email"><i class="fas fa-envelope"></i> {{ detalle.usuario_email }}</span>
                <span class="sub-value" v-if="detalle?.usuario_rol"><i class="fas fa-user-tag"></i> {{ detalle.usuario_rol }}</span>
              </template>
            </div>
            <!-- Cuándo -->
            <div class="info-item">
              <span class="label">Cuándo</span>
              <span class="value">{{ formatFechaHora(detalle?.fecha) }}</span>
              <span class="sub-value" v-if="detalle?.endpoint"><i class="fas fa-route"></i> {{ detalle.endpoint }} <span v-if="detalle?.metodo_http">({{ detalle.metodo_http }})</span></span>
            </div>
            <!-- Desde dónde -->
            <div class="info-item">
              <span class="label">Desde dónde</span>
              <span class="value" style="font-size: 0.95rem;">
                <i :class="getIconoNavegador(detalle?.navegador_info)" style="margin-right:5px"></i>
                {{ getNombreNavegador(detalle?.navegador_info) }}
              </span>
              <span class="sub-value" v-if="detalle?.sistema_operativo"><i class="fas fa-desktop"></i> {{ detalle.sistema_operativo }}</span>
              <span class="sub-value"><i class="fas fa-network-wired"></i> IP: {{ detalle?.ip_address || 'No registrada' }}</span>
              <span v-if="detalle?.dispositivo_info" class="sub-value">{{ detalle.dispositivo_info }}</span>
            </div>
            <!-- Qué hizo -->
            <div class="info-item">
              <span class="label">Qué hizo</span>
              <span class="value" style="font-size: 0.95rem;">{{ detalle?.accion.replace(/_/g, ' ') }}</span>
              <span v-if="detalle?.descripcion && detalle.descripcion !== '-'" class="sub-value">{{ detalle.descripcion }}</span>
              <span v-if="detalle?.mensaje" class="sub-value motivo-error"><i class="fas fa-comment"></i> {{ detalle.mensaje }}</span>
            </div>
          </div>

          <hr class="divider">

          <h3 class="section-title">Sobre qué se actuó</h3>
          <div class="objeto-box">
            <div class="objeto-item"><span class="label">Modelo</span><span class="value">{{ detalle?.modelo_afectado || 'Sistema' }}</span></div>
            <div class="objeto-item"><span class="label">ID</span><span class="value mono">{{ detalle?.objeto_id || '—' }}</span></div>
            <div class="objeto-item" v-if="detalle?.objeto_nombre"><span class="label">Nombre</span><span class="value">{{ detalle.objeto_nombre }}</span></div>
            <div class="objeto-item" v-if="detalle?.id_operacion">
              <span class="label">Operación</span>
              <span class="value mono">
                <code>{{ detalle.id_operacion.slice(0, 8) }}</code>
                <button @click="verOperacion(detalle.id_operacion)" class="operation-chip inline" title="Ver todos los eventos de esta operación">
                  <i class="fas fa-link"></i> ver operación
                </button>
              </span>
            </div>
          </div>

          <h3 class="section-title">Cambios (ANTES / DESPUÉS)</h3>
          <div class="diff-wrapper">
            <table class="detail-table">
              <thead>
                <tr>
                  <th width="35%">Campo</th>
                  <th width="65%">Contenido</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(info, campo) in parseDetalles(detalle?.detalles)"
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
                    <div v-else-if="info.tipo === 'VALOR'" class="static-val">{{ formatValue(info.valor) }}</div>
                    <div v-else class="legacy-val">{{ formatValue(info) }}</div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="isEmpty(detalle?.detalles) && (!detalle.antes || Object.keys(detalle.antes).length === 0)" class="no-data">
              <i class="fas fa-info-circle"></i> No hay cambios de campos registrados para este movimiento.
            </div>
          </div>

          <div v-if="detalle?.contexto && Object.keys(detalle.contexto).length" class="contexto-box">
            <h3 class="section-title">Contexto</h3>
            <div class="contexto-grid">
              <div v-for="(valor, clave) in detalle.contexto" :key="clave" class="contexto-item">
                <span class="label">{{ formatearClave(clave) }}</span>
                <span class="value mono">{{ typeof valor === 'object' ? JSON.stringify(valor) : valor }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer-custom">
          <button v-if="detalle?.id_operacion" @click="verOperacion(detalle.id_operacion)" class="footer-operacion">
            <i class="fas fa-link"></i> Ver toda la operación
          </button>
          <button @click="cerrarModal" class="clear-filters-btn" style="width: auto; margin-left: auto;"><i class="fas fa-check"></i> Entendido</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import api from '@/services/api'

const logs = ref([])
const count = ref(0)
const pagina = ref(1)
const pageSize = 25
const loading = ref(false)
const errorMsg = ref('')
const mostrarModal = ref(false)
const detalle = ref(null)

const filtros = ref({
  busqueda: '',
  modulo: '',
  usuario: '',
  resultado: '',
  accion: '',
  fechaDesde: '',
  fechaHasta: '',
  idOperacion: ''
})

const modulosDisponibles = [
  { id: '', label: 'Todos', icon: 'fas fa-layer-group' },
  { id: 'AUTENTICACION', label: 'Accesos', icon: 'fas fa-user-shield' },
  { id: 'USUARIOS', label: 'Usuarios', icon: 'fas fa-users' },
  { id: 'SERVICIOS', label: 'Servicios', icon: 'fas fa-cut' },
  { id: 'INVENTARIO', label: 'Inventario', icon: 'fas fa-boxes' },
  { id: 'PROVEEDORES', label: 'Proveedores', icon: 'fas fa-truck' },
  { id: 'PRECIOS', label: 'Precios', icon: 'fas fa-tags' },
  { id: 'TURNOS', label: 'Turnos', icon: 'fas fa-calendar-check' },
  { id: 'VENTAS', label: 'Ventas', icon: 'fas fa-cash-register' },
  { id: 'PEDIDOS_WEB', label: 'Pedidos Web', icon: 'fas fa-shopping-cart' },
  { id: 'PAGOS', label: 'Pagos', icon: 'fas fa-credit-card' },
  { id: 'CAJA', label: 'Caja', icon: 'fas fa-box-open' },
  { id: 'CONFIGURACION', label: 'Configuración', icon: 'fas fa-cog' },
  { id: 'SEGURIDAD', label: 'Seguridad', icon: 'fas fa-shield-halved' },
  { id: 'SISTEMA', label: 'Sistema', icon: 'fas fa-server' },
]

const accionesDisponibles = [
  'LOGIN', 'LOGIN_GOOGLE', 'LOGIN_FALLIDO', 'LOGOUT', 'CAMBIO_PASSWORD',
  'CREAR', 'EDITAR', 'ELIMINAR', 'ANULAR_VENTA', 'CANCELAR',
  'APERTURA_CAJA', 'CIERRE_CAJA', 'INGRESO_VENTA', 'INGRESO_TURNO',
  'INGRESO_MANUAL', 'EGRESO_MANUAL', 'COBRO_RESTANTE', 'AJUSTE_STOCK',
  'CONSULTAR', 'EXPORTAR',
]

const totalPaginas = computed(() => Math.max(1, Math.ceil(count.value / pageSize)))

const esSistema = (log) => {
  if (!log) return false
  return log.resultado === 'SISTEMA' || String(log.usuario_nombre).toUpperCase() === 'SISTEMA'
}

const claseResultado = (r) => {
  if (!r || r === 'EXITO') return 'resultado-exito'
  if (r === 'ERROR') return 'resultado-error'
  if (r === 'SISTEMA') return 'resultado-sistema'
  return 'resultado-exito'
}

const getNombreModulo = (modId) => {
  const mod = modulosDisponibles.find(m => m.id === modId)
  return mod ? mod.label : (modId || 'Sistema General')
}

const getIconoModulo = (modId) => {
  const mod = modulosDisponibles.find(m => m.id === modId)
  return mod ? mod.icon : 'fas fa-server'
}

const getClaseAccion = (accion) => {
  if (!accion) return 'estado-secondary'
  const a = accion.toUpperCase()
  if (a.includes('CREAR') || a.includes('INGRESO') || a.includes('APERTURA') || a.includes('LOGIN')) return 'estado-success'
  if (a.includes('EDITAR')) return 'estado-info'
  if (a.includes('ELIMINAR') || a.includes('ANULAR') || a.includes('CIERRE') || a.includes('EGRESO') || a.includes('LOGOUT') || a.includes('FALLIDO')) return 'estado-danger'
  if (a.includes('AJUSTE') || a.includes('CANCELAR')) return 'estado-warning'
  return 'estado-secondary'
}

const getIconoNavegador = (navegadorInfo) => {
  if (!navegadorInfo) return 'fas fa-globe'
  const navLower = navegadorInfo.toLowerCase()
  if (navLower.includes('edge')) return 'fab fa-edge'
  if (navLower.includes('opera') || navLower.includes('opr')) return 'fab fa-opera'
  if (navLower.includes('brave')) return 'fab fa-brave'
  if (navLower.includes('chrome')) return 'fab fa-chrome'
  if (navLower.includes('firefox')) return 'fab fa-firefox-browser'
  if (navLower.includes('safari')) return 'fab fa-safari'
  return 'fas fa-globe'
}

const getColorNavegador = (navegadorInfo) => {
  if (!navegadorInfo) return ''
  const navLower = navegadorInfo.toLowerCase()
  if (navLower.includes('edge')) return 'text-edge'
  if (navLower.includes('opera') || navLower.includes('opr')) return 'text-opera'
  if (navLower.includes('brave')) return 'text-brave'
  if (navLower.includes('chrome')) return 'text-chrome'
  if (navLower.includes('firefox')) return 'text-firefox'
  if (navLower.includes('safari')) return 'text-safari'
  return 'text-web'
}

const getNombreNavegador = (navegadorInfo) => {
  if (!navegadorInfo || navegadorInfo === '-') return 'Sistema'
  const navLower = navegadorInfo.toLowerCase()
  if (navLower.includes('edg/') || navLower.includes('edge')) return 'Edge'
  if (navLower.includes('brave')) return 'Brave'
  if (navLower.includes('opr/') || navLower.includes('opera')) return 'Opera'
  if (navLower.includes('firefox')) return 'Firefox'
  if (navLower.includes('chrome')) return 'Chrome'
  if (navLower.includes('safari')) return 'Safari'
  return navegadorInfo
}

const parseDetalles = (detalles) => {
  if (!detalles) return {}
  let d = detalles
  if (typeof detalles === 'string') {
    try { d = JSON.parse(detalles) } catch (e) { return {} }
  }
  const adaptado = {}
  if (d.anterior !== undefined && d.nuevo !== undefined) {
    return { Modificación: { tipo: 'CAMBIO', anterior: d.anterior, nuevo: d.nuevo } }
  }
  if (d.cambios) {
    for (const [k, v] of Object.entries(d.cambios)) {
      adaptado[k] = { tipo: 'CAMBIO', anterior: v.anterior, nuevo: v.nuevo }
    }
  }
  for (const [key, value] of Object.entries(d)) {
    if (key === 'cambios' || key === '__meta__') continue
    if (value && typeof value === 'object' && value.anterior !== undefined && value.nuevo !== undefined) {
      adaptado[key] = { tipo: 'CAMBIO', anterior: value.anterior, nuevo: value.nuevo }
    }
    else if (value && typeof value === 'object' && value.tipo === 'CAMBIO') {
      adaptado[key] = value
    }
    else if (value && typeof value === 'object' && value.tipo === 'VALOR') {
      adaptado[key] = value
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
  if (typeof val === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(val)) {
    const d = new Date(val)
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString('es-AR') + ' ' + d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) + ' hs'
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
const formatFechaHora = (f) => f ? new Date(f).toLocaleString('es-AR', { dateStyle: 'medium', timeStyle: 'short' }) : '-'

const truncar = (texto, n) => (texto && texto.length > n ? texto.slice(0, n) + '…' : texto)

const construirParams = () => {
  const params = { page: pagina.value, page_size: pageSize }
  const f = filtros.value
  if (f.modulo) params.modulo = f.modulo
  if (f.busqueda.trim()) params.search = f.busqueda.trim()
  if (f.usuario.trim()) params.usuario_nombre = f.usuario.trim()
  if (f.resultado) params.resultado = f.resultado
  if (f.accion) params.accion = f.accion
  if (f.idOperacion) params.id_operacion = f.idOperacion
  if (f.fechaDesde) {
    params.fecha_desde = new Date(f.fechaDesde + 'T00:00:00').toISOString()
  }
  if (f.fechaHasta) {
    params.fecha_hasta = new Date(f.fechaHasta + 'T23:59:59').toISOString()
  }
  return params
}

const cargarAuditoria = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await api.get('/auditoria/', { params: construirParams() })
    logs.value = Array.isArray(res.data.results) ? res.data.results : []
    count.value = res.data.count || 0
  } catch (err) {
    errorMsg.value = err?.response?.status === 403
      ? 'No tenés permiso para ver la auditoría.'
      : err?.response?.status === 401
        ? 'Sesión expirada. Volvé a iniciar sesión.'
        : 'Error al cargar la auditoría: ' + (err?.message || 'desconocido')
    console.error('❌ Error cargando auditoría:', err)
  } finally {
    loading.value = false
  }
}

const irPagina = (n) => {
  if (n < 1 || (count.value > 0 && n > totalPaginas.value)) return
  pagina.value = n
  cargarAuditoria()
}

// Debounce suave para que escribir en el buscador no dispare requests por tecla
let timer = null
watch(filtros, () => {
  pagina.value = 1
  clearTimeout(timer)
  timer = setTimeout(cargarAuditoria, 350)
}, { deep: true })

const limpiarFiltros = () => {
  filtros.value = {
    busqueda: '', modulo: '', usuario: '', resultado: '', accion: '',
    fechaDesde: '', fechaHasta: '', idOperacion: ''
  }
  pagina.value = 1
  cargarAuditoria()
}

const abrirDetalles = async (log) => {
  detalle.value = log
  mostrarModal.value = true
  try {
    const res = await api.get(`/auditoria/${log.id}/`)
    if (res.data) detalle.value = res.data
  } catch (err) {
    console.warn('No se pudo refrescar el detalle, se muestra el dato de la fila:', err)
  }
}

const cerrarModal = () => { mostrarModal.value = false; detalle.value = null }

const verOperacion = (idOperacion) => {
  if (!idOperacion) return
  filtros.value.idOperacion = idOperacion
  filtros.value.modulo = ''
  filtros.value.busqueda = ''
  filtros.value.usuario = ''
  filtros.value.resultado = ''
  filtros.value.accion = ''
  filtros.value.fechaDesde = ''
  filtros.value.fechaHasta = ''
  pagina.value = 1
  cerrarModal()
  cargarAuditoria()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(cargarAuditoria)
</script>

<style scoped>
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-color); position: relative; overflow: hidden; margin: 0 auto; }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ac2e7, #0ac2e7, #0ac2e7); }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid var(--border-color); padding-bottom: 20px; }
.header-content h1 { font-size: 2rem; font-weight: 900; color: var(--text-primary); margin: 0; display: flex; align-items: center; gap: 10px; }
.header-content h1 i { color: #8b5cf6; }
.header-content p { color: var(--text-secondary); margin-top: 5px; font-size: 0.95rem; }

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
.module-chip:hover { background: var(--hover-bg); color: var(--text-primary); transform: translateY(-1px); }
.module-chip.active { background: var(--accent-color); color: white; border-color: var(--accent-color); box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2); }

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

.estado-success { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.estado-info { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.2); }
.estado-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
.estado-warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-tertiary); border: 1px solid var(--border-color); }

/* Resultado */
.resultado-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.resultado-badge.grande { font-size: 0.8rem; padding: 6px 14px; }
.resultado-exito { background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.resultado-error { background: rgba(239, 68, 68, 0.12); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.resultado-sistema { background: rgba(139, 92, 246, 0.12); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.35); }

.motivo-error { font-size: 0.72rem; color: #ef4444; margin-top: 4px; display: flex; align-items: center; gap: 4px; max-width: 180px; }
.motivo-error i { flex-shrink: 0; }

.badge-sistema {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(139, 92, 246, 0.12); color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.35);
  padding: 4px 10px; border-radius: 6px;
  font-size: 0.72rem; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;
}

.desc-corta {
  font-size: 0.72rem; color: var(--text-tertiary);
  max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.campos-afectados { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }
.campo-chip {
  font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
  background: rgba(245, 158, 11, 0.1); color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.25);
  padding: 2px 6px; border-radius: 4px; letter-spacing: 0.3px;
}

.operation-chip {
  background: var(--bg-tertiary); color: var(--text-secondary);
  border: 1px solid var(--border-color); border-radius: 8px;
  padding: 7px 10px; cursor: pointer; transition: 0.2s;
  display: inline-flex; align-items: center; gap: 6px; font-weight: 700; font-size: 0.75rem;
}
.operation-chip:hover { color: #8b5cf6; border-color: #8b5cf6; background: rgba(139, 92, 246, 0.08); transform: translateY(-1px); }
.operation-chip.inline { padding: 4px 8px; }

.operacion-active {
  display: flex; align-items: center; gap: 8px;
  background: rgba(139, 92, 246, 0.1); border: 1px dashed rgba(139, 92, 246, 0.5);
  color: #a78bfa; border-radius: 10px; padding: 10px 16px;
  font-size: 0.85rem; font-weight: 600; margin-bottom: 15px;
}
.operacion-active code { background: rgba(139, 92, 246, 0.2); padding: 2px 8px; border-radius: 5px; font-family: monospace; }
.quitar-operacion { background: transparent; border: none; color: #a78bfa; font-size: 1.2rem; cursor: pointer; margin-left: auto; }
.quitar-operacion:hover { color: #ef4444; }

.error-banner {
  background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444; padding: 12px 18px; border-radius: 10px;
  font-weight: 600; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;
}

.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 20px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; align-items: end; }
.filter-group label { font-weight: 700; margin-bottom: 8px; display: block; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; }
.filter-input { padding: 10px 14px; border-radius: 10px; border: 2px solid var(--border-color); background-color: var(--bg-primary); color: var(--text-primary); width: 100%; box-sizing: border-box; outline: none; transition: border-color 0.3s; font-size: 0.9rem; }
.filter-input:focus { border-color: #8b5cf6; }
.filter-input option, .filter-input optgroup { background-color: #1e1e2e; color: #e0e0e0; }
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

.browser-cell { display: flex; flex-direction: column; gap: 4px; }
.browser-main { display: flex; align-items: center; gap: 6px; font-weight: 700; font-size: 0.85rem; color: var(--text-primary); }
.ip-sub { font-size: 0.75rem; color: var(--text-secondary); font-family: monospace; opacity: 0.9; }
.os-sub { font-size: 0.65rem; color: #8b5cf6; background: rgba(139, 92, 246, 0.1); padding: 2px 6px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; width: fit-content; text-transform: uppercase; font-weight: 800; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeIn 0.2s ease; }
.modal-content { background: var(--bg-secondary); width: 880px; max-width: 95vw; border-radius: 16px; border: 1px solid var(--border-color); position: relative; max-height: 92vh; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
.modal-close { position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,0.2); border: none; font-size: 1.5rem; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; z-index: 10; }
.modal-close:hover { background: #ef4444; transform: rotate(90deg); }

.modal-header-custom { padding: 30px; border-bottom: 1px solid var(--border-color); background: var(--bg-primary); border-radius: 16px 16px 0 0; position: relative; overflow: hidden; }
.modal-title-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; }
.modal-header-custom h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; font-weight: 900; position: relative; z-index: 2; text-transform: uppercase; letter-spacing: 0.5px; }
.modal-header-custom h2 .muted { color: var(--text-tertiary); font-weight: 700; text-transform: none; }
.modal-subtitle { color: var(--text-secondary); margin-top: 8px; font-size: 0.95rem; font-weight: 600; position: relative; z-index: 2; }

.modal-header-custom.resultado-exito::before { content:''; position:absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(16,185,129,0.1), transparent); }
.modal-header-custom.resultado-error::before { content:''; position:absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(239,68,68,0.1), transparent); }
.modal-header-custom.resultado-sistema::before { content:''; position:absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(135deg, rgba(139,92,246,0.12), transparent); }

.modal-body-custom { padding: 30px; overflow-y: auto; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
.info-item { background: var(--bg-primary); border: 1px solid var(--border-color); padding: 20px; border-radius: 12px; display: flex; flex-direction: column; gap: 5px; }
.label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 800; letter-spacing: 0.5px; }
.value { font-size: 1.1rem; color: var(--text-primary); font-weight: 700; }
.value.mono { font-family: 'Courier New', Courier, monospace; }
.sub-value { font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px; display: flex; align-items: center; gap: 6px; }

.divider { border: 0; border-top: 2px dashed var(--border-color); margin: 30px 0; opacity: 0.5; }
.section-title { color: var(--text-primary); font-size: 1.1rem; margin-bottom: 20px; font-weight: 800; border-left: 4px solid var(--accent-color); padding-left: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.modal-footer-custom { padding: 20px 30px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; align-items: center; background: var(--bg-primary); border-radius: 0 0 16px 16px; }
.footer-operacion { background: rgba(139, 92, 246, 0.1); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.4); padding: 10px 16px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: 0.2s; display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; }
.footer-operacion:hover { background: rgba(139, 92, 246, 0.2); }

.objeto-box {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px;
  background: var(--bg-primary); border: 1px solid var(--border-color);
  padding: 20px; border-radius: 12px; margin-bottom: 30px;
}
.objeto-item { display: flex; flex-direction: column; gap: 4px; }
.objeto-item .value { font-size: 0.95rem; }

.diff-wrapper { border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: var(--bg-primary); }
.detail-table { width: 100%; border-collapse: collapse; }
.detail-table th { text-align: left; padding: 15px 20px; background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; font-weight: 800; border-bottom: 2px solid var(--border-color); }
.detail-table td { padding: 15px 20px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
.field-col { color: var(--text-primary); font-weight: 700; font-size: 0.95rem; width: 35%; }
.value-col { font-family: 'Courier New', Courier, monospace; font-size: 0.95rem; color: var(--text-secondary); font-weight: 600; }
.row-changed { background: rgba(245, 158, 11, 0.05); }
.row-changed .field-col { color: #f59e0b; }
.changed-flag { background: #f59e0b; color: white; font-size: 0.6rem; padding: 3px 6px; border-radius: 4px; margin-left: 10px; vertical-align: middle; font-weight: 800; }

.static-val { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 6px 10px; border-radius: 6px; display: inline-block; border: 1px solid rgba(16, 185, 129, 0.2); }
.change-container { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.val-old { color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 6px 10px; border-radius: 6px; text-decoration: line-through; opacity: 0.8; border: 1px solid rgba(239, 68, 68, 0.2);}
.arrow { color: var(--text-tertiary); font-size: 1.2rem; }
.val-new { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 6px 10px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.4); }
.no-data { padding: 30px; text-align: center; color: var(--text-tertiary); font-size: 0.95rem; }

.contexto-box { margin-top: 30px; }
.contexto-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.contexto-item { background: var(--bg-primary); border: 1px solid var(--border-color); padding: 12px 14px; border-radius: 10px; display: flex; flex-direction: column; gap: 4px; }
.contexto-item .value { font-size: 0.85rem; word-break: break-word; }

.text-edge { color: #3b82f6; }
.text-chrome { color: #10b981; }
.text-brave { color: #fb542b; }
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
  .modal-title-row { flex-direction: column; }
}
</style>