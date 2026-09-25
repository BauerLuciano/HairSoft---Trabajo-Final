<template>
  <div class="list-container">
    <div class="list-card">

      <div class="list-header">
        <div class="header-content">
          <h1><i class="fas fa-shield-alt"></i> AUDITORÍA DEL SISTEMA</h1>
          <p>Trazabilidad integral: quién, cuándo, desde dónde, qué hizo y qué cambió</p>
        </div>
      </div>

      <!-- Módulos (filtro server-side, multi-selección) -->
      <div class="modules-chips-container">
        <button
          v-for="mod in modulosDisponibles"
          :key="mod.id"
          @click="toggleModulo(mod.id)"
          class="module-chip"
          :class="{ active: (mod.id === '' ? filtros.modulo.length === 0 : filtros.modulo.includes(mod.id)) }"
        >
          <i :class="mod.icon"></i> {{ mod.label }}
        </button>
      </div>

      <!-- Filtros (todos visibles, barra compacta con controles de formulario) -->
      <div class="filters-container">
        <div class="filters-row">

          <div class="filter-field filter-buscador">
            <i class="fas fa-search filter-field-icon"></i>
            <input v-model="filtros.busqueda" placeholder="Buscar auditoría..." class="filter-select"/>
          </div>

          <label class="filter-field filter-user" title="Quién realizó la acción">
            <span class="filter-field-label">Usuario</span>
            <select v-model="filtros.usuario" class="filter-select">
              <option value="">Todos</option>
              <option v-for="autor in autores" :key="autorKey(autor)" :value="autor">
                {{ autor.nombre }} — {{ autor.rol }}
              </option>
            </select>
          </label>

          <label class="filter-field filter-resultado" title="Resultado de la operación">
            <span class="filter-field-label">Resultado</span>
            <select v-model="filtros.resultado" class="filter-select">
              <option value="">Todos</option>
              <option value="EXITO">Éxito</option>
              <option value="ERROR">Error</option>
            </select>
          </label>

          <label class="filter-field filter-accion" title="Tipo de acción registrada">
            <span class="filter-field-label">Acción</span>
            <select v-model="filtros.accion" class="filter-select">
              <option value="">Cualquier acción</option>
              <option v-for="a in accionesDisponibles" :key="a" :value="a">{{ a.replace(/_/g, ' ') }}</option>
            </select>
          </label>

          <!-- El grupo Desde—Hasta es indivisible y hace wrap junto con Limpiar -->
          <div class="fechas-limpiar">
            <div class="fechas-group">
              <label class="filter-field">
                <span class="filter-field-label">Desde</span>
                <input type="date" v-model="filtros.fechaDesde" class="filter-select" :max="filtros.fechaHasta || undefined" />
              </label>
              <span class="fechas-separador" aria-hidden="true">—</span>
              <label class="filter-field">
                <span class="filter-field-label">Hasta</span>
                <input type="date" v-model="filtros.fechaHasta" class="filter-select" :min="filtros.fechaDesde || undefined" />
              </label>
            </div>

            <button @click="limpiarFiltros" class="clear-filters-btn filters-clear">
              <i class="fas fa-eraser"></i> Limpiar filtros
            </button>
          </div>

        </div>
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
                <div class="objeto-corto">
                  <div class="objeto-linea">
                    <strong class="objeto-modelo">{{ log.modelo_afectado || 'Sistema General' }}</strong>
                    <span v-if="log.objeto_id" class="objeto-id">#{{ log.objeto_id }}</span>
                  </div>
                  <span v-if="nombreCortoUtil(log)" class="objeto-nombre" :title="log.objeto_nombre">{{ log.objeto_nombre }}</span>
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
                <button @click="abrirDetalles(log)" class="action-button edit" title="Ver Ficha Detallada">
                  <i class="fas fa-eye"></i> Ver
                </button>
              </td>
            </tr>
            <tr v-if="!loading && logs.length === 0">
              <td colspan="7" style="text-align:center; padding:60px;">
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

        <div class="modal-header-custom" :class="modoOperacion ? 'resultado-exito' : claseResultado(detalle?.resultado)">
          <template v-if="modoOperacion">
            <div class="modal-title-row">
              <h2><i class="fas fa-link"></i> Operación <span class="muted">· {{ operacionTotal }} {{ operacionTotal === 1 ? 'evento' : 'eventos' }}</span></h2>
            </div>
            <p class="modal-subtitle">Eventos que componen esta operación</p>
          </template>
          <template v-else>
            <div class="modal-title-row">
              <h2>{{ (detalle?.accion || '').replace(/_/g, ' ') }} <span class="muted">· {{ getNombreModulo(detalle?.modulo_efectivo || detalle?.modulo) }}</span></h2>
              <span class="resultado-badge grande" :class="claseResultado(detalle?.resultado)">{{ detalle?.resultado || 'EXITO' }}</span>
            </div>
            <p class="modal-subtitle">Objeto: {{ detalle?.modelo_afectado || 'Sistema' }}
              <span v-if="detalle?.objeto_id"> · #{{ detalle?.objeto_id }}</span>
              <span v-if="detalle?.objeto_nombre"> · {{ detalle?.objeto_nombre }}</span>
            </p>
          </template>
        </div>

        <div class="modal-body-custom">
          <template v-if="modoOperacion">
            <!-- Índice compacto de la operación (dentro del mismo modal) -->
            <div v-if="operacionCargando" class="loading-overlay">
              <div class="spinner"></div>
              <p>Cargando eventos de la operación...</p>
            </div>
            <div v-else-if="operacionEventos.length === 0" class="no-data">
              <i class="fas fa-info-circle"></i> No se encontraron eventos para esta operación.
            </div>
            <div v-else class="op-index">
              <div v-for="(ev, i) in operacionEventos" :key="ev.id" class="op-index-row" @click="verDetalleOperacion(ev)" :title="'Ver detalle de ' + (ev.accion || '').replace(/_/g, ' ') + ' · ' + (ev.modelo_afectado || 'Sistema General') + (ev.objeto_id ? ' #' + ev.objeto_id : '')">
                <span class="op-index-num">{{ i + 1 }}</span>
                <span class="op-index-texto">
                  <span class="op-index-accion" :class="getClaseAccion(ev.accion)">{{ (ev.accion || '').replace(/_/g, ' ') }}</span>
                  <span class="op-index-modelo">{{ ev.modelo_afectado || 'Sistema General' }}<template v-if="ev.objeto_id"> #{{ ev.objeto_id }}</template></span>
                  <span class="op-index-fecha">{{ formatFecha(ev.fecha) }} {{ formatHora(ev.fecha) }}</span>
                </span>
                <i class="fas fa-chevron-right op-index-icon"></i>
              </div>
            </div>
          </template>
          <template v-else>
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
                <span class="sub-value" v-if="detalle?.usuario_email"><a :href="'mailto:' + detalle.usuario_email" class="mailto-link"><i class="fas fa-envelope"></i> {{ detalle.usuario_email }}</a></span>
                <span class="sub-value" v-if="detalle?.usuario_rol"><i class="fas fa-user-tag"></i> {{ detalle.usuario_rol }}</span>
              </template>
            </div>
            <!-- Cuándo -->
            <div class="info-item">
              <span class="label">Cuándo</span>
              <span class="value">{{ formatFechaHora(detalle?.fecha) }}</span>
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
              <span v-if="origenCompleto(detalle)" class="sub-value origen-resumen"><i class="fas fa-location-arrow"></i> {{ origenCompleto(detalle) }}</span>
            </div>
            <!-- Qué hizo -->
            <div class="info-item">
              <span class="label">Qué hizo</span>
              <span class="value" style="font-size: 0.95rem;">{{ detalle?.accion.replace(/_/g, ' ') }}</span>
              <span v-if="detalle?.descripcion && detalle.descripcion !== '-'" class="frase-hecho">{{ detalle.descripcion }}</span>
              <span v-if="detalle?.mensaje" class="sub-value motivo-error"><i class="fas fa-comment"></i> {{ detalle.mensaje }}</span>
            </div>
          </div>

          <hr class="divider">

          <h3 class="section-title">Sobre qué se actuó</h3>
          <div class="objeto-box">
            <div class="objeto-item"><span class="label">Modelo</span><span class="value">{{ detalle?.modelo_afectado || 'Sistema' }}</span></div>
            <div class="objeto-item"><span class="label">ID</span><span class="value mono">{{ detalle?.objeto_id || '—' }}</span></div>
            <div class="objeto-item" v-if="detalle?.objeto_nombre"><span class="label">Nombre</span><span class="value">{{ detalle.objeto_nombre }}</span></div>
          </div>

          <h3 class="section-title">{{ tituloDetalles }}</h3>
          <div class="diff-wrapper">
            <!-- EDITAR / modificación: tabla de cambios reales (Campo | ANTES | DESPUÉS) -->
            <table v-if="Object.keys(detallesCambios).length" class="detail-table cambio-table">
              <thead>
                <tr>
                  <th width="30%">Campo</th>
                  <th width="35%">Antes</th>
                  <th width="35%">Después</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(info, campo) in detallesCambios" :key="campo" class="row-changed">
                  <td class="field-col">{{ formatearClave(campo) }}</td>
                  <td class="value-col val-old-cell">{{ formatValue(info.anterior) }}</td>
                  <td class="value-col val-new-cell">{{ formatValue(info.nuevo) }}</td>
                </tr>
              </tbody>
            </table>
            <!-- CREAR / ELIMINAR / INGRESO_*: valores registrados (Campo | Contenido) -->
            <table v-if="Object.keys(detallesValores).length" class="detail-table">
              <thead>
                <tr>
                  <th width="35%">Campo</th>
                  <th width="65%">Contenido</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(info, campo) in detallesValores" :key="campo">
                  <td class="field-col">{{ formatearClave(campo) }}</td>
                  <td class="value-col">
                    <div v-if="info.tipo === 'VALOR'" class="static-val">{{ formatValue(info.valor) }}</div>
                    <div v-else class="legacy-val">{{ formatValue(info) }}</div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="!hayDetallesVisibles" class="no-data">
              <i class="fas fa-info-circle"></i> No hay datos registrados para este evento.
            </div>
          </div>

          <div v-if="Object.keys(contextoFuncional).length || Object.keys(contextoTecnico).length" class="contexto-box">
            <h3 v-if="Object.keys(contextoFuncional).length" class="section-title">Contexto</h3>
            <div v-if="Object.keys(contextoFuncional).length" class="contexto-grid">
              <div v-for="(valor, clave) in contextoFuncional" :key="clave" class="contexto-item">
                <span class="label">{{ formatearClave(clave) }}</span>
                <span class="value mono">{{ typeof valor === 'object' ? JSON.stringify(valor) : valor }}</span>
              </div>
            </div>
            <div v-if="mostrarContextoTecnico" class="contexto-grid">
              <div v-for="(valor, clave) in contextoTecnico" :key="clave" class="contexto-item">
                <span class="label">{{ formatearClave(clave) }}</span>
                <span class="value mono">{{ typeof valor === 'object' ? JSON.stringify(valor) : valor }}</span>
              </div>
            </div>
          </div>
          </template>
        </div>

        <div class="modal-footer-custom">
          <button v-if="!modoOperacion && !enOperacion && totalEventosOperacionDetalle > 1" @click="verOperacion(detalle.id_operacion, totalEventosOperacionDetalle)" class="footer-operacion">
            <i class="fas fa-link"></i> Ver operación
          </button>
          <button v-if="enOperacion && !modoOperacion" @click="volverAOperacion" class="footer-operacion">
            <i class="fas fa-chevron-left"></i> Volver a la operación
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
const pageSize = 8
const loading = ref(false)
const errorMsg = ref('')
const mostrarModal = ref(false)
const detalle = ref(null)
// Autores disponibles para el selector "Usuario" (vienen del backend: solo
// quienes realmente aparecen como autores de eventos de auditoría).
const autores = ref([])
// Sección colapsable de "Datos técnicos" dentro del modal de detalle.
const mostrarContextoTecnico = ref(false)
// Vista de operación dentro del mismo modal de detalle (sin segundos modales y
// sin tocar filtros, URL, página ni listado principal).
const modoOperacion = ref(false)
const enOperacion = ref(false)
const operacionEventos = ref([])
const operacionTotal = ref(0)
const operacionCargando = ref(false)

const filtros = ref({
  busqueda: '',
  modulo: [],          // multi-selección: [] = "Todos" (sin filtro de módulo)
  usuario: '',         // '' = Todos | objeto autor {id, nombre, rol, origen}
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
  'LOGIN', 'LOGIN_FALLIDO', 'LOGOUT', 'CAMBIO_PASSWORD',
  'CREAR', 'EDITAR', 'ELIMINAR', 'ANULAR_VENTA', 'CANCELAR',
  'APERTURA_CAJA', 'CIERRE_CAJA', 'INGRESO_VENTA', 'INGRESO_TURNO',
  'INGRESO_MANUAL', 'EGRESO_MANUAL', 'COBRO_RESTANTE', 'AJUSTE_STOCK',
  'CONSULTAR', 'EXPORTAR',
]

const totalPaginas = computed(() => Math.max(1, Math.ceil(count.value / pageSize)))

// Total de eventos del grupo de la operación (anotado en backend). Se ofrece
// "ver operación" solo cuando el grupo realmente tiene más de un evento (total > 1)
// y se muestra la cantidad TOTAL de eventos, no "relacionados" (total - 1).
const totalEventosOperacionDetalle = computed(() => Number(detalle.value?.total_eventos_operacion) || 0)

// Valor "vacío" = ausencia de dato (no debe mostrarse). 0, false, "No" y
// "No Aplica" son valores válidos del registro y se conservan.
const esValorVacio = (val) => {
  if (val === null || val === undefined) return true
  if (typeof val === 'string') {
    const t = val.trim()
    return t === '' || t === '-'
  }
  return false
}

// Detalles filtrados para la presentación: se ocultan los campos cuyo valor es
// un dato vacío (null, undefined, '', solo espacios, '-'). Además se ocultan
// los campos técnicos auto_now (fecha_actualizacion, fecha_modificacion):
// cambian en cada save() y generaban ruido tipo
// "Antes: 25/9/2026 12:59 → Ahora: 25/9/2026 12:59". Es solo presentación;
// los datos históricos quedan intactos en la DB.
const CAMPOS_AUTO_NOW = new Set(['fecha_actualizacion', 'fecha_modificacion'])

// Filas de cambio real (EDITAR): se muestran en la tabla de 3 columnas
// "Campo | ANTES | DESPUÉS". Los cambios nunca se filtran: son información real
// de una edición.
const detallesCambios = computed(() => {
  const d = detalle.value
  if (!d) return {}
  const visibles = {}
  for (const [clave, info] of Object.entries(parseDetalles(d.detalles))) {
    if (CAMPOS_AUTO_NOW.has(clave)) continue
    if (info && info.tipo === 'CAMBIO') visibles[clave] = info
  }
  return visibles
})

// Valores estáticos (CREAR, ELIMINAR, INGRESO_*, …): tabla de 2 columnas
// "Campo | Contenido". Se ocultan los vacíos, pero 0/false/"No" se conservan.
const detallesValores = computed(() => {
  const d = detalle.value
  if (!d) return {}
  const visibles = {}
  for (const [clave, info] of Object.entries(parseDetalles(d.detalles))) {
    if (CAMPOS_AUTO_NOW.has(clave)) continue
    if (info && info.tipo === 'CAMBIO') continue
    const valor = info && info.tipo === 'VALOR' ? info.valor : info
    if (!esValorVacio(valor)) visibles[clave] = info
  }
  return visibles
})

const hayDetallesVisibles = computed(() => Object.keys(detallesCambios.value).length + Object.keys(detallesValores.value).length > 0)

// Título de la sección de datos según la acción y el contenido real:
//  - hay campos CAMBIO            → "Cambios" (tabla de 3 columnas ANTES/DESPUÉS)
//  - ELIMINAR sin CAMBIO          → "Datos eliminados" (snapshot estático)
//  - resto (CREAR, INGRESO_*, …)  → "Datos registrados" (valores estáticos)
// Nunca se inventa un "antes" que no exista en los datos.
const tituloDetalles = computed(() => {
  const d = detalle.value
  if (!d) return 'Datos registrados'
  if (Object.keys(detallesCambios.value).length) return 'Cambios'
  if ((d.accion || '').toUpperCase() === 'ELIMINAR') return 'Datos eliminados'
  return 'Datos registrados'
})

// Claves de `contexto` internas/técnicas: no se muestran en la vista normal, se
// agrupan bajo la sección colapsable "Datos técnicos". La información NO se borra
// de la DB (solo cambia su presentación). La agrupación por id_operacion queda
// intacta: el dato sigue existiendo y el backend lo usa internamente como antes.
const CLAVES_CONTEXTO_TECNICAS = new Set([
  'operacion', 'pago_mixto', 'id_operacion', 'proceso', 'es_sistema', 'prueba',
])

// Contexto funcional visible normalmente: total, método de pago, montos, cliente,
// correo intentado, filtros, etc. — toda clave que no sea de las técnicas.
const contextoFuncional = computed(() => {
  const ctx = detalle.value?.contexto
  if (!ctx || typeof ctx !== 'object') return {}
  return Object.fromEntries(Object.entries(ctx).filter(([clave]) => !CLAVES_CONTEXTO_TECNICAS.has(clave)))
})

// Contexto técnico/debug agrupado en la sección colapsable "Datos técnicos".
const contextoTecnico = computed(() => {
  const ctx = detalle.value?.contexto
  if (!ctx || typeof ctx !== 'object') return {}
  return Object.fromEntries(Object.entries(ctx).filter(([clave]) => CLAVES_CONTEXTO_TECNICAS.has(clave)))
})

// Devuelve el nombre corto útil para la tabla (o '' si es una descripción larga).
// Las descripciones tipo str() de MovimientoCaja ("INGRESO | Venta de Productos | $26000.00 (Caja 220)")
// deben verse solo en Detalles, no en la fila.
const nombreCortoUtil = (log) => {
  const nombre = log?.objeto_nombre
  if (!nombre || nombre === '-') return ''
  if (nombre.includes('$')) return ''          // importes
  if (nombre.includes(' | ')) return ''        // descripciones separadas por pipe (movimiento/caja)
  if (/\d{2}\/\d{2}\/\d{4}/.test(nombre)) return ''  // fechas embebidas (dd/mm/yyyy)
  if (/\d{4}-\d{2}-\d{2}/.test(nombre)) return ''    // fechas embebidas (ISO)
  if (nombre.length > 45) return ''            // textos excesivamente largos
  return nombre
}

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

// Resumen legible del origen: "Edge en Windows (IP: 127.0.0.1)".
const origenCompleto = (log) => {
  if (!log) return ''
  const nav = getNombreNavegador(log.navegador_info)
  const so = log.sistema_operativo || ''
  const ip = log.ip_address || ''
  const base = []
  if (nav && nav !== 'Sistema' && nav !== '-') base.push(nav)
  if (so && so !== '-') base.push(so)
  let texto = base.join(' en ')
  if (ip && ip !== '-') texto = texto ? `${texto} (IP: ${ip})` : `IP: ${ip}`
  return texto
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
// Hora con segundos en la lista principal (distingue 12:59:14 / 12:59:16 / 12:59:19).
const formatHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : ''
const formatFechaHora = (f) => f ? new Date(f).toLocaleString('es-AR', { dateStyle: 'medium', timeStyle: 'short' }) : '-'

const truncar = (texto, n) => (texto && texto.length > n ? texto.slice(0, n) + '…' : texto)

// ---- Módulos: multi-selección ----
const toggleModulo = (modId) => {
  const f = filtros.value
  if (modId === '') {
    f.modulo = [] // Todos: deselecciona el resto
    return
  }
  const idx = f.modulo.indexOf(modId)
  if (idx >= 0) {
    f.modulo.splice(idx, 1) // click sobre un módulo seleccionado = quitarlo
  } else {
    f.modulo.push(modId) // seleccionar un módulo desactiva Todos
  }
}

// Clave estable para el <option> del selector de usuario: distingue cuentas con
// el mismo nombre (FK por id; snapshot por nombre+email).
const autorKey = (autor) => {
  if (!autor) return ''
  return autor.origen === 'usuario'
    ? `u${autor.id}`
    : `s${autor.nombre}|${autor.email || ''}`
}

const cargarAutores = async () => {
  try {
    const res = await api.get('/auditoria/autores/')
    autores.value = Array.isArray(res.data?.autores) ? res.data.autores : []
  } catch (err) {
    console.error('❌ Error cargando autores de auditoría:', err)
    autores.value = []
  }
}

const construirParams = () => {
  // URLSearchParams: axios lo serializa tal cual, permitiendo repetir el param
  // `modulo` (multi-selección) sin transformarlo en `modulo[]=...`.
  const params = new URLSearchParams()
  const f = filtros.value
  params.set('page', pagina.value)
  params.set('page_size', pageSize)
  for (const m of f.modulo) {
    params.append('modulo', m)
  }
  if (f.busqueda.trim()) params.set('search', f.busqueda.trim())
  if (f.usuario && typeof f.usuario === 'object') {
    if (f.usuario.origen === 'usuario') {
      // Usuario con FK: identificador estable (no mezcla nombres repetidos).
      params.set('usuario', f.usuario.id)
    } else {
      // Autor histórico sin FK (usuario eliminado): snapshot exacto.
      params.set('usuario_nombre_snapshot', f.usuario.nombre)
      params.set('usuario_email_snapshot', f.usuario.email || '')
    }
  }
  if (f.resultado) params.set('resultado', f.resultado)
  if (f.accion) params.set('accion', f.accion)
  if (f.idOperacion) params.set('id_operacion', f.idOperacion)
  if (f.fechaDesde) {
    params.set('fecha_desde', new Date(f.fechaDesde + 'T00:00:00').toISOString())
  }
  if (f.fechaHasta) {
    // Fin de día inclusive: 23:59:59.999 para no excluir eventos del último día.
    params.set('fecha_hasta', new Date(f.fechaHasta + 'T23:59:59.999').toISOString())
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

// Validación cruzada Desde/Hasta: si por alguna interacción el rango quedara
// inválido (Hasta < Desde), se corrige de forma segura. Permitido: Desde = Hasta.
watch(() => filtros.value.fechaDesde, (desde) => {
  const hasta = filtros.value.fechaHasta
  if (desde && hasta && hasta < desde) filtros.value.fechaHasta = desde
})
watch(() => filtros.value.fechaHasta, (hasta) => {
  const desde = filtros.value.fechaDesde
  if (hasta && desde && desde > hasta) filtros.value.fechaDesde = hasta
})

const limpiarFiltros = () => {
  filtros.value = {
    busqueda: '', modulo: [], usuario: '', resultado: '', accion: '',
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

const cerrarModal = () => {
  mostrarModal.value = false
  detalle.value = null
  // Cierra la vista de operación y limpia el índice (la X / Cerrar vuelve al listado).
  modoOperacion.value = false
  enOperacion.value = false
  operacionEventos.value = []
}

const verOperacion = async (idOperacion, total = 0) => {
  if (!idOperacion) return
  // El mismo modal pasa temporalmente a la vista compacta de la operación.
  // No se abren modales anidados ni se tocan filtros, URL, página ni listado principal.
  operacionTotal.value = total || 0
  operacionEventos.value = []
  operacionCargando.value = true
  modoOperacion.value = true
  enOperacion.value = true
  try {
    // Reutiliza el endpoint existente (filtro id_operacion ya soportado por la API,
    // sin agregar filtros nuevos ni generar auditorías CONSULTAR).
    const res = await api.get('/auditoria/', {
      params: { id_operacion: idOperacion, page: 1, page_size: 200 }
    })
    operacionEventos.value = Array.isArray(res.data.results) ? res.data.results : []
    // Count real del grupo para el encabezado "Operación · N eventos"
    operacionTotal.value = res.data.count || operacionTotal.value
  } catch (err) {
    operacionEventos.value = []
    console.error('❌ Error cargando eventos de la operación:', err)
  } finally {
    operacionCargando.value = false
  }
}

// Muestra el detalle de un evento dentro del mismo modal (reemplaza la vista
// de operación; usa el mismo mecanismo de detalle que el listado).
const verDetalleOperacion = async (ev) => {
  if (!ev) return
  modoOperacion.value = false
  detalle.value = ev
  try {
    const res = await api.get(`/auditoria/${ev.id}/`)
    if (res.data) detalle.value = res.data
  } catch (err) {
    console.warn('No se pudo refrescar el detalle, se muestra el dato de la fila:', err)
  }
}

// Vuelve al índice compacto de la operación (eventos ya en memoria, sin re-consultar).
const volverAOperacion = () => {
  modoOperacion.value = true
}

onMounted(() => {
  cargarAutores()
  cargarAuditoria()
})
</script>

<style scoped>
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1280px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-color); position: relative; overflow: hidden; margin: 0 auto; }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ac2e7, #0ac2e7, #0ac2e7); }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid var(--border-color); padding-bottom: 20px; }
.header-content h1 { font-size: 2rem; font-weight: 900; color: var(--text-primary); margin: 0; display: flex; align-items: center; gap: 10px; }
.header-content h1 i { color: #8b5cf6; }
.header-content p { color: var(--text-secondary); margin-top: 5px; font-size: 0.95rem; }

.modules-chips-container { display: flex; gap: 10px 14px; flex-wrap: wrap; margin-bottom: 25px; }
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

.objeto-corto { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.objeto-linea { display: flex; align-items: baseline; flex-wrap: wrap; }
.objeto-modelo { color: var(--text-primary); }
.objeto-id { font-size: 0.8em; margin-left: 5px; color: var(--accent-color); font-family: monospace; }
.objeto-nombre {
  font-size: 0.78em; opacity: 0.85; max-width: 200px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

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

/* Fila de filtros: barra compacta. Cada filtro es un campo con etiqueta a la
   izquierda ("Usuario [ Todos ▼ ]") y controles de formulario normales, todos
   a la misma altura; wrap de grupos completos sin scroll horizontal. */
.filters-row { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
/* min-width:0 en los controles evita que su tamaño intrínseco (p.ej. un
   <option> largo) sesgue la decisión de wrap: el layout queda gobernado por
   las flex-basis, no por el contenido. */
.filters-row input, .filters-row select { min-width: 0; }

/* Campo = etiqueta a la izquierda + control de formulario */
.filter-field { display: flex; align-items: center; gap: 6px; min-width: 0; }
.filter-field-label {
  font-size: 0.8rem; font-weight: 600; color: var(--text-secondary);
  white-space: nowrap; flex: 0 0 auto;
}
.filter-field-icon { font-size: 0.85rem; color: var(--text-tertiary); flex: 0 0 auto; }
.filter-field .filter-select { flex: 1 1 auto; }

/* Control de formulario normal (buscador, selects y fechas) */
.filters-row .filter-select {
  height: 38px;
  padding: 0 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.88rem;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s, background-color 0.2s;
}
.filters-row .filter-select:hover { border-color: var(--text-secondary); }
.filters-row .filter-select:focus { border-color: #8b5cf6; box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15); }
.filters-row .filter-select::placeholder { color: var(--text-tertiary); opacity: 0.85; }

/* Selects: flecha discreta propia (se oculta la nativa) */
.filters-row select.filter-select {
  appearance: none;
  -webkit-appearance: none;
  padding-right: 32px;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 12px;
  cursor: pointer;
}
.filters-row select.filter-select option,
.filters-row select.filter-select optgroup { background-color: #1e1e2e; color: #e0e0e0; }

/* Buscador: icono de lupa dentro del control, crece para aprovechar el resto */
.filter-buscador { flex: 3 1 210px; min-width: 145px; position: relative; }
.filter-buscador .filter-field-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; z-index: 1; }
.filter-buscador .filter-select { padding-left: 38px; }

/* Anchuras según contenido: Usuario y Acción más amplios (nombres+roles y
   acciones largas), Resultado compacto. */
.filter-user { flex: 1 1 185px; min-width: 158px; }
.filter-resultado { flex: 0 1 158px; min-width: 150px; }
.filter-accion { flex: 0 1 200px; min-width: 168px; }

/* Grupo Desde—Hasta: indivisible (nowrap interno). El flex-wrap del padre
   solo puede moverlos juntos a la línea siguiente, nunca separarlos.
   En escritorio ocupa ~390px (380–400); en anchos intermedios baja a 340px
   para que [Desde—Hasta][Limpiar] sigan en la misma línea. */
.fechas-group { display: flex; align-items: center; gap: 8px; flex: 0 1 390px; min-width: 376px; flex-wrap: nowrap; }
.fechas-group .filter-field { flex: 1 1 180px; min-width: 0; }
.fechas-group .filter-field .filter-field-label { flex: 0 0 auto; }
.fechas-group .filter-select { width: 100%; }
.fechas-separador { color: var(--text-tertiary); font-weight: 700; font-size: 1rem; padding: 0 2px; flex: 0 0 auto; }

/* Fechas + Limpiar son un bloque único que hace wrap junto: en desktop queda
   [Buscar][Usuario][Resultado][Acción] / [Desde—Hasta][Limpiar]. */
.fechas-limpiar { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; flex: 0 1 auto; min-width: 0; max-width: 100%; }
.fechas-limpiar > .clear-filters-btn { height: 38px; padding: 0 14px; white-space: nowrap; border-radius: 8px; flex: 0 0 auto; }

/* Botón colapsable de "Datos técnicos" dentro del modal de detalle */
.tecnicos-toggle {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--bg-tertiary); color: var(--text-secondary);
  border: 1px dashed var(--border-color); border-radius: 10px;
  padding: 8px 14px; cursor: pointer; font-weight: 700; font-size: 0.75rem;
  text-transform: uppercase; letter-spacing: 0.4px; transition: all 0.2s ease;
  margin-bottom: 12px;
}
.tecnicos-toggle:hover { color: var(--accent-color); border-color: var(--accent-color); background: var(--hover-bg); }
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
.sub-value.origen-resumen { font-style: italic; }
.mailto-link { color: var(--accent-color); text-decoration: none; font-weight: 700; }
.mailto-link:hover { text-decoration: underline; }
/* Texto descriptivo de la acción ("Claudio Sanchez modificó PedidoWeb #173.") */
.frase-hecho { font-size: 0.9rem; color: var(--text-primary); background: var(--bg-secondary); border-left: 3px solid var(--accent-color); padding: 8px 12px; border-radius: 6px; margin-top: 6px; font-weight: 600; line-height: 1.4; }

.divider { border: 0; border-top: 2px dashed var(--border-color); margin: 30px 0; opacity: 0.5; }
.section-title { color: var(--text-primary); font-size: 1.1rem; margin-bottom: 20px; font-weight: 800; border-left: 4px solid var(--accent-color); padding-left: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.modal-footer-custom { padding: 20px 30px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; align-items: center; background: var(--bg-primary); border-radius: 0 0 16px 16px; }
.footer-operacion { background: rgba(139, 92, 246, 0.1); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.4); padding: 10px 16px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: 0.2s; display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; }
.footer-operacion:hover { background: rgba(139, 92, 246, 0.2); }

/* Índice compacto de la operación (dentro del mismo modal de detalle) */
.op-index { display: flex; flex-direction: column; gap: 10px; }
.op-index-row { display: flex; align-items: center; gap: 14px; background: var(--bg-primary); border: 1px solid var(--border-color); padding: 14px 16px; border-radius: 12px; cursor: pointer; transition: border-color 0.2s, transform 0.2s; }
.op-index-row:hover { border-color: #8b5cf6; transform: translateY(-1px); }
.op-index-num { flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%; background: rgba(139, 92, 246, 0.12); color: #a78bfa; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.8rem; }
.op-index-texto { flex: 1; min-width: 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.op-index-accion { font-weight: 800; text-transform: uppercase; letter-spacing: 0.4px; font-size: 0.85rem; }
.op-index-modelo { font-weight: 600; color: var(--text-primary); font-size: 0.92rem; }
.op-index-fecha { color: var(--text-tertiary); font-size: 0.85rem; margin-left: auto; white-space: nowrap; }
.op-index-icon { color: var(--text-tertiary); flex-shrink: 0; }
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
.static-val { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 6px 10px; border-radius: 6px; display: inline-block; border: 1px solid rgba(16, 185, 129, 0.2); }
/* Tabla de cambios reales (EDITAR): columna ANTES / DESPUÉS */
.cambio-table .field-col { width: 30%; }
.cambio-table .val-old-cell { color: #ef4444; opacity: 0.85; }
.cambio-table .val-new-cell { color: #10b981; font-weight: 800; }
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

/* Resoluciones medias: el grupo de fechas se compacta un poco para seguir
   bajando completo a su propia fila junto con Limpiar (sin scroll horizontal
   ni separación de Desde—Hasta). */
@media (max-width: 1023.98px) {
  .fechas-group { flex: 0 1 340px; min-width: 325px; }
}

@media (max-width: 768px) {
  .info-grid { grid-template-columns: 1fr; }
  .list-card { padding: 20px; }
  /* Los chips hacen wrap natural, sin scroll horizontal */
  .modules-chips-container { flex-wrap: wrap; }
  .module-chip { white-space: nowrap; }
  .filters-row { gap: 10px; }
  .filter-field { gap: 5px; }
  .filter-field-label { font-size: 0.74rem; }
  .filters-row .filter-select { font-size: 0.85rem; }
  .modal-title-row { flex-direction: column; }
}

/* Pantalla extremadamente pequeña: excepción permitida — el grupo de fechas
   apila Desde y Hasta verticalmente (sigue siendo un bloque único, sin
   separarlos en filas distintas de la barra). */
@media (max-width: 420px) {
  .fechas-group { flex-wrap: wrap; min-width: 0; gap: 8px; flex: 1 1 100%; }
  .fechas-group .filter-field { flex: 1 1 100%; }
  .fechas-separador { display: none; }
}
</style>