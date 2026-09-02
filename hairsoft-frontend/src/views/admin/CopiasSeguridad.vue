<template>
  <div class="list-container">
    <div class="list-card">

      <div class="list-header">
        <div class="header-content">
          <h1><i class="fas fa-database"></i> COPIA DE SEGURIDAD</h1>
          <p>Respaldo automático de la base de datos PostgreSQL con política de retención</p>
        </div>
        <div class="header-actions">
          <button class="btn-help" @click="mostrarAyuda" title="Cómo funciona la automatización de backups">
            <i class="fas fa-circle-question"></i> Ayuda
          </button>
          <button class="btn-refresh" @click="cargarTodo" :disabled="loading">
            <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i> Actualizar
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p>Cargando copias de seguridad...</p>
      </div>

      <template v-else>
        <div class="summary-grid">
          <div v-for="info in tiposInfo" :key="info.tipo" class="summary-card">
            <div class="summary-head">
              <span class="badge-tipo" :class="badgeClase(info.tipo)">{{ info.tipo }}</span>
              <span class="summary-count"><span class="dot">·</span> {{ contarCopias(info.tipo) }}</span>
            </div>

            <div class="summary-info">
              <div class="summary-label"><i class="fas fa-clock"></i> Último backup</div>
              <template v-if="ultimoDe(info.tipo)">
                <div class="summary-fecha-val">{{ formatFechaLarga(ultimoDe(info.tipo).fecha) }}</div>
                <div class="summary-nombre" :title="ultimoDe(info.tipo).nombre">{{ ultimoDe(info.tipo).nombre }}</div>
              </template>
              <div v-else class="sin-backup"><i class="fas fa-hourglass-half"></i> Sin copias aún</div>
            </div>

            <div class="summary-retencion">
              <i class="fas fa-shield-halved"></i> Retención: {{ info.retencion }} días
            </div>

            <button class="gen-btn" :class="'gen-' + info.tipo.toLowerCase()"
                    :disabled="generando === info.tipo" @click="confirmarGeneracion(info.tipo)">
              <i v-if="generando === info.tipo" class="fas fa-spinner fa-spin"></i>
              <i v-else :class="info.icono"></i>
              Generar {{ info.tipo }}
            </button>
          </div>
        </div>

        <div class="filters-container">
          <div class="filters-grid">
            <div class="filter-group" style="grid-column: span 2;">
              <label>Buscar</label>
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input v-model="filtros.busqueda" class="filter-input search-input"
                       placeholder="Buscar por nombre de archivo..." />
              </div>
            </div>

            <div class="filter-group">
              <label>Tipo</label>
              <select v-model="filtros.tipo" class="filter-input">
                <option value="">Todos</option>
                <option v-for="t in tipos" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>

            <div class="filter-group">
              <label>Desde</label>
              <input type="date" v-model="filtros.fechaDesde" class="filter-input"
                     :max="filtros.fechaHasta || hoy" />
            </div>

            <div class="filter-group">
              <label>Hasta</label>
              <input type="date" v-model="filtros.fechaHasta" class="filter-input"
                     :min="filtros.fechaDesde || undefined" :max="hoy" />
            </div>

            <div class="filter-group" style="display: flex; align-items: flex-end;">
              <button @click="limpiarFiltros" class="clear-filters-btn" style="width: 100%; height: 42px;">
                <i class="fas fa-eraser"></i> Limpiar
              </button>
            </div>
          </div>
        </div>

        <div class="section-heading">
          <h2><i class="fas fa-file-archive"></i> Copias existentes</h2>
          <span v-if="resumen" class="total-copias">
            {{ hayFiltros ? backupsFiltrados.length + ' de ' + backups.length : backups.length + ' total' }}
            · {{ formatTamano(tamanoFiltrado) }}
          </span>
        </div>

        <div class="table-container">
          <div class="table-scroll">
            <table class="users-table">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Fecha</th>
                  <th>Archivo</th>
                  <th>Tamaño</th>
                  <th style="text-align: center;">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in backupsPaginados" :key="b.ruta">
                  <td>
                    <span class="badge-tipo" :class="badgeClase(b.tipo)">{{ b.tipo }}</span>
                  </td>
                  <td>
                    <div class="fecha-cell">
                      <strong>{{ formatFecha(b.fecha) }}</strong>
                      <span class="hora-cell">{{ formatHora(b.fecha) }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="nombre-copia" :title="b.nombre">{{ b.nombre }}</span>
                  </td>
                  <td>{{ formatTamano(b.tamano_bytes) }}</td>
                  <td style="text-align: center;">
                    <div class="row-actions">
                      <button class="action-button verify" :disabled="verificando === b.ruta"
                              @click="verificar(b)">
                        <i v-if="verificando === b.ruta" class="fas fa-spinner fa-spin"></i>
                        <i v-else class="fas fa-search-check"></i> Verificar
                      </button>
                      <button class="action-button download" :disabled="descargando === b.ruta"
                              @click="descargar(b)">
                        <i v-if="descargando === b.ruta" class="fas fa-spinner fa-spin"></i>
                        <i v-else class="fas fa-download"></i> Descargar
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!loading && backups.length === 0">
                  <td colspan="5" style="text-align:center; padding:60px;">
                    <i class="fas fa-database" style="font-size:3rem; opacity:0.2; margin-bottom:15px; display:block;"></i>
                    <h3 style="color: var(--text-secondary); margin: 0;">No hay copias de seguridad aún</h3>
                    <p style="color: var(--text-tertiary); font-size: 0.9rem;">
                      Generá la primera copia con los botones de arriba o esperá la tarea programada.
                    </p>
                  </td>
                </tr>
                <tr v-else-if="backupsFiltrados.length === 0">
                  <td colspan="5" style="text-align:center; padding:60px;">
                    <i class="fas fa-filter" style="font-size:3rem; opacity:0.2; margin-bottom:15px; display:block;"></i>
                    <h3 style="color: var(--text-secondary); margin: 0;">No se encontraron copias</h3>
                    <p style="color: var(--text-tertiary); font-size: 0.9rem;">
                      Probá ajustando o limpiando los filtros de búsqueda.
                    </p>
                    <button @click="limpiarFiltros" class="clear-filters-btn"
                            style="margin-top: 15px; padding: 10px 20px; width: auto;">
                      <i class="fas fa-eraser"></i> Limpiar filtros
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="mostrarPaginacion" class="pagination">
          <div class="pagination-pages">
            <button @click="paginaAnterior" :disabled="pagina === 1">
              <i class="fas fa-chevron-left"></i> Anterior
            </button>
            <span>Página {{ pagina }} de {{ totalPaginas }}</span>
            <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">
              Siguiente <i class="fas fa-chevron-right"></i>
            </button>
          </div>
          <div class="pagination-limit">
            <label for="porPagina">Ver por página</label>
            <select id="porPagina" v-model="itemsPorPagina" class="filter-input limit-select">
              <option v-for="n in opcionesPorPagina" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
        </div>

        <div class="logs-heading">
          <button class="logs-toggle" @click="mostrarLogs = !mostrarLogs">
            <i class="fas" :class="mostrarLogs ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            {{ mostrarLogs ? 'Ocultar logs' : 'Mostrar logs' }}
            <span class="logs-count">{{ registros.length }} registros</span>
          </button>
        </div>

        <div v-if="mostrarLogs" class="log-container">
          <div v-for="(linea, idx) in registrosInvertidos" :key="idx" :class="['log-line', claseLog(linea)]">
            <i class="fas" :class="iconoLog(linea)"></i>
            <span>{{ linea }}</span>
          </div>
          <div v-if="registros.length === 0" class="no-log">
            <i class="fas fa-info-circle"></i> Todavía no hay registros en backup.log
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import Swal from 'sweetalert2'
import backupService from '@/services/backupService'

const loading = ref(false)
const backups = ref([])
const resumen = ref(null)
const registros = ref([])
const generando = ref('')
const verificando = ref('')
const descargando = ref('')
const mostrarLogs = ref(false)

const filtros = ref({ busqueda: '', tipo: '', fechaDesde: '', fechaHasta: '' })
const pagina = ref(1)
const itemsPorPagina = ref(15)
const opcionesPorPagina = [5, 10, 15, 25]

const tipos = ['Diario', 'Semanal', 'Mensual']
const tiposInfo = [
  { tipo: 'Diario', retencion: 30, icono: 'fas fa-calendar-day' },
  { tipo: 'Semanal', retencion: 90, icono: 'fas fa-calendar-week' },
  { tipo: 'Mensual', retencion: 365, icono: 'fas fa-calendar-alt' }
]

const badgeClase = (tipo) => ({
  Diario: 'tipo-diario',
  Semanal: 'tipo-semanal',
  Mensual: 'tipo-mensual'
}[tipo] || '')

const hoy = computed(() => {
  const d = new Date()
  const mes = String(d.getMonth() + 1).padStart(2, '0')
  const dia = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mes}-${dia}`
})

const hayFiltros = computed(() =>
  !!(filtros.value.busqueda || filtros.value.tipo || filtros.value.fechaDesde || filtros.value.fechaHasta)
)

const ultimoDe = (tipo) => resumen.value?.ultimos?.[tipo] || null

const contarCopias = (tipo) => {
  const c = ultimoDe(tipo)?.cantidad || 0
  return `${c} ${c === 1 ? 'copia' : 'copias'}`
}

const formatTamano = (bytes) => {
  if (!bytes && bytes !== 0) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

const formatFecha = (f) => {
  if (!f) return '-'
  const d = new Date(f)
  return isNaN(d.getTime()) ? f : d.toLocaleDateString('es-AR')
}

const formatHora = (f) => {
  if (!f) return ''
  const d = new Date(f)
  if (isNaN(d.getTime())) return ''
  const h = d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
  return h === '00:00' ? '' : h
}

const formatFechaLarga = (f) => {
  if (!f) return '-'
  const d = new Date(f)
  return isNaN(d.getTime()) ? f : d.toLocaleDateString('es-AR', { day: 'numeric', month: 'long', year: 'numeric' })
}

const backupsFiltrados = computed(() => {
  const term = filtros.value.busqueda.trim().toLowerCase()
  const desde = filtros.value.fechaDesde ? new Date(filtros.value.fechaDesde + 'T00:00:00') : null
  const hasta = filtros.value.fechaHasta ? new Date(filtros.value.fechaHasta + 'T23:59:59') : null

  return backups.value
    .filter((b) => {
      if (term && !b.nombre.toLowerCase().includes(term)) return false
      if (filtros.value.tipo && b.tipo !== filtros.value.tipo) return false
      const f = new Date(b.fecha)
      if (desde && f < desde) return false
      if (hasta && f > hasta) return false
      return true
    })
    .sort((a, b) => (b.fecha || '').localeCompare(a.fecha || ''))
})

const tamanoFiltrado = computed(() =>
  backupsFiltrados.value.reduce((acc, b) => acc + b.tamano_bytes, 0)
)

const totalPaginas = computed(() => Math.max(1, Math.ceil(backupsFiltrados.value.length / itemsPorPagina.value)))
const backupsPaginados = computed(() => {
  const start = (pagina.value - 1) * itemsPorPagina.value
  return backupsFiltrados.value.slice(start, start + itemsPorPagina.value)
})
const mostrarPaginacion = computed(() => backupsFiltrados.value.length > itemsPorPagina.value)

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

const registrosInvertidos = computed(() => [...registros.value].reverse())

const claseLog = (linea) => {
  if (linea.includes('ERROR')) return 'log-error'
  if (linea.includes('OK')) return 'log-ok'
  if (linea.includes('RETENCIÓN') || linea.includes('RETENCION')) return 'log-warning'
  return 'log-neutral'
}

const iconoLog = (linea) => {
  if (linea.includes('ERROR')) return 'fa-circle-xmark'
  if (linea.includes('OK')) return 'fa-circle-check'
  if (linea.includes('RETENCIÓN') || linea.includes('RETENCION')) return 'fa-trash'
  return 'fa-circle-info'
}

const mostrarAyuda = () => {
  Swal.fire({
    title: 'Automatización de backups',
    html: `
      <div class="ayuda-backups">
        <p class="ayuda-intro">
          <i class="fas fa-robot"></i>
          <span>Los backups se generan automáticamente mediante el <strong>Programador de tareas de Windows</strong>.</span>
        </p>
        <div class="ayuda-horarios">
          <div class="ayuda-fila">
            <span class="ayuda-badge ayuda-diario">Diario</span>
            <span>todos los días a las <strong>02:00</strong>.</span>
          </div>
          <div class="ayuda-fila">
            <span class="ayuda-badge ayuda-semanal">Semanal</span>
            <span>todos los domingos a las <strong>03:00</strong>.</span>
          </div>
          <div class="ayuda-fila">
            <span class="ayuda-badge ayuda-mensual">Mensual</span>
            <span>el día 1 de cada mes a las <strong>04:00</strong>.</span>
          </div>
        </div>
        <p class="ayuda-manual">
          <i class="fas fa-hand-pointer"></i>
          <span>También podés generar un backup manualmente con los botones <strong>Generar Diario</strong>, <strong>Generar Semanal</strong> y <strong>Generar Mensual</strong>.</span>
        </p>
      </div>`,
    confirmButtonText: 'Entendido',
    confirmButtonColor: '#8b5cf6',
    width: '500px',
    padding: '1.6rem',
    customClass: {
      popup: 'ayuda-swal-popup'
    }
  })
}

watch(filtros, () => { pagina.value = 1 }, { deep: true })
watch(itemsPorPagina, () => { pagina.value = 1 })

watch(() => filtros.value.fechaDesde, (v) => {
  if (v && filtros.value.fechaHasta && v > filtros.value.fechaHasta) {
    filtros.value.fechaHasta = v
  }
})
watch(() => filtros.value.fechaHasta, (v) => {
  if (v && filtros.value.fechaDesde && v < filtros.value.fechaDesde) {
    filtros.value.fechaDesde = v
  }
})

const cargarListado = async () => {
  const res = await backupService.listar()
  backups.value = res.data?.backups || []
  resumen.value = res.data || null
}

const cargarLog = async () => {
  try {
    const res = await backupService.leerLog()
    registros.value = res.data?.registros || []
  } catch (err) {
    console.error('Error cargando log:', err)
  }
}

const cargarTodo = async () => {
  loading.value = true
  try {
    await Promise.all([cargarListado(), cargarLog()])
  } catch (err) {
    Swal.fire('Error', err.response?.data?.error || 'No se pudieron cargar las copias de seguridad.', 'error')
  } finally {
    loading.value = false
  }
}

const limpiarFiltros = () => {
  filtros.value = { busqueda: '', tipo: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1
}

const confirmarGeneracion = async (tipo) => {
  const result = await Swal.fire({
    title: `Generar backup ${tipo}`,
    html: `Se ejecutará <code>backup_hairsoft.ps1 -Tipo ${tipo}</code>.<br>
           Se aplicará la política de retención (backups viejos pueden eliminarse).`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Sí, generar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#0ea5e9'
  })
  if (!result.isConfirmed) return

  generando.value = tipo
  try {
    const res = await backupService.generar(tipo)
    const archivo = res.data?.archivo
    if (res.data?.ok && archivo) {
      await Swal.fire('Backup generado', `${archivo.nombre} creado correctamente.`, 'success')
    } else {
      await Swal.fire('Atención', res.data?.error || res.data?.salida || 'El backup terminó con errores.', 'warning')
    }
    await cargarListado()
    await cargarLog()
  } catch (err) {
    Swal.fire('Error', err.response?.data?.error || 'No se pudo generar el backup.', 'error')
  } finally {
    generando.value = ''
  }
}

const verificar = async (b) => {
  verificando.value = b.ruta
  try {
    const res = await backupService.verificar(b.ruta)
    if (res.data?.ok) {
      await Swal.fire(
        'Backup válido',
        `${b.nombre}<br><br>El listado TOC se lee correctamente: <strong>${res.data.entradas}</strong> entradas.`,
        'success'
      )
    } else {
      await Swal.fire(
        'Backup no válido',
        `${b.nombre}<br><br><small style="font-family:monospace;">${res.data?.error || res.data?.detalle || 'No se pudo verificar.'}</small>`,
        'error'
      )
    }
  } catch (err) {
    Swal.fire('Error', err.response?.data?.error || 'No se pudo verificar el backup.', 'error')
  } finally {
    verificando.value = ''
  }
}

const descargar = async (b) => {
  descargando.value = b.ruta
  try {
    const res = await backupService.descargar(b.ruta)
    const blobUrl = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = b.nombre
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(blobUrl)
  } catch (err) {
    Swal.fire('Error', err.response?.data?.error || 'No se pudo descargar el backup.', 'error')
  } finally {
    descargando.value = ''
  }
}

onMounted(cargarTodo)
</script>

<style scoped>
.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
  margin: 0 auto;
}
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #8b5cf6);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}
.header-content h1 {
  font-size: 2rem;
  font-weight: 900;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.header-content h1 i { color: #8b5cf6; }
.header-content p { color: var(--text-secondary); margin-top: 5px; font-size: 0.95rem; }

.btn-refresh {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: 0.2s;
  text-transform: uppercase;
  font-size: 0.8rem;
}
.btn-refresh:hover:not(:disabled) { background: var(--hover-bg); border-color: var(--text-secondary); }
.btn-refresh:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-help {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: 0.2s;
  text-transform: uppercase;
  font-size: 0.8rem;
}
.btn-help i { color: #8b5cf6; }
.btn-help:hover { background: var(--hover-bg); border-color: var(--text-secondary); }

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

/* ── Tarjetas de resumen ─────────────────────────────── */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}
.summary-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.summary-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.summary-count {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-secondary);
}
.summary-count .dot { color: var(--text-tertiary); margin-right: 2px; }

.summary-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-height: 58px;
  justify-content: center;
}
.summary-label {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  gap: 6px;
}
.summary-fecha-val {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-primary);
  text-transform: capitalize;
}
.summary-nombre {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sin-backup { color: var(--text-tertiary); font-size: 0.9rem; font-weight: 600; }

.summary-retencion {
  font-size: 0.8rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px dashed var(--border-color);
  padding-top: 12px;
}
.summary-retencion i { color: var(--accent-color); }

.gen-btn {
  padding: 10px 14px;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  transition: 0.2s;
  font-size: 0.82rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.gen-btn:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-1px); }
.gen-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.gen-btn.gen-diario:hover:not(:disabled) { border-color: #0ea5e9; color: #0ea5e9; }
.gen-btn.gen-semanal:hover:not(:disabled) { border-color: #f59e0b; color: #f59e0b; }
.gen-btn.gen-mensual:hover:not(:disabled) { border-color: #10b981; color: #10b981; }

/* ── Filtros ─────────────────────────────────────────── */
.filters-container {
  background: var(--hover-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
}
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  align-items: end;
}
.filter-group label {
  font-weight: 700;
  margin-bottom: 8px;
  display: block;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
}
.filter-input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  width: 100%;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.3s;
  font-size: 0.9rem;
}
.filter-input:focus { border-color: #8b5cf6; }
.filter-input option, .filter-input optgroup { background-color: var(--bg-primary); color: var(--text-primary); }

.search-wrapper { position: relative; }
.search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); }
.search-input { padding-left: 40px; }

.clear-filters-btn {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-transform: uppercase;
  font-size: 0.8rem;
}
.clear-filters-btn:hover { background: var(--hover-bg); border-color: var(--text-secondary); }

/* ── Encabezados de sección ──────────────────────────── */
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0 15px;
  border-left: 4px solid var(--accent-color);
  padding-left: 12px;
}
.section-heading h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-heading h2 i { color: var(--accent-color); }
.total-copias { font-size: 0.85rem; color: var(--text-secondary); font-weight: 700; }

/* ── Tabla ───────────────────────────────────────────── */
.badge-tipo {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
}
.tipo-diario { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.25); }
.tipo-semanal { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); }
.tipo-mensual { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25); }

.table-container {
  border-radius: 16px;
  margin-bottom: 10px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}
.table-scroll {
  max-height: 480px;
  overflow-y: auto;
}
.users-table { width: 100%; border-collapse: separate; border-spacing: 0; background: var(--bg-primary); }
.users-table th {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  padding: 15px;
  text-align: left;
  font-weight: 800;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 1;
}
.users-table td {
  padding: 12px 15px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  vertical-align: middle;
}
.users-table tr:hover { background: var(--hover-bg); }
.fecha-cell { display: flex; flex-direction: column; }
.fecha-cell strong { color: var(--text-primary); }
.hora-cell { font-size: 0.75rem; color: var(--text-tertiary); }
.nombre-copia {
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-family: monospace;
  display: block;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-actions { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
.action-button {
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  transition: 0.2s;
  font-size: 0.8rem;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.action-button:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-2px); }
.action-button:disabled { opacity: 0.6; cursor: not-allowed; }
.action-button.verify:hover:not(:disabled) { border-color: #10b981; color: #10b981; }
.action-button.download:hover:not(:disabled) { border-color: #0ea5e9; color: #0ea5e9; }

/* ── Paginación ──────────────────────────────────────── */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
  margin: 15px 0 20px;
}
.pagination-pages {
  display: flex;
  gap: 15px;
  align-items: center;
}
.pagination-pages button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.pagination-pages button:hover:not(:disabled) { background: var(--hover-bg); border-color: var(--text-secondary); }
.pagination-pages button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination-pages span { font-weight: 700; color: var(--text-secondary); font-size: 0.9rem; }
.pagination-limit { display: flex; align-items: center; gap: 10px; }
.pagination-limit label { font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; }
.limit-select { width: 80px; padding: 8px 10px; }

/* ── Logs colapsables ────────────────────────────────── */
.logs-heading {
  display: flex;
  justify-content: flex-start;
  margin: 25px 0 10px;
}
.logs-toggle {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 800;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.logs-toggle:hover { background: var(--hover-bg); border-color: var(--text-secondary); }
.logs-toggle .logs-count {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-tertiary);
  background: var(--hover-bg);
  padding: 2px 8px;
  border-radius: 20px;
}

.log-container {
  display: flex;
  flex-direction: column;
  gap: 5px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 15px;
  max-height: 260px;
  overflow-y: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.8rem;
}
.log-line { display: flex; align-items: center; gap: 8px; padding: 3px 6px; border-radius: 5px; }
.log-line i { font-size: 0.8rem; flex-shrink: 0; }
.log-ok { color: #10b981; }
.log-error { color: #ef4444; background: rgba(239, 68, 68, 0.06); }
.log-warning { color: #f59e0b; }
.log-neutral { color: var(--text-tertiary); }
.no-log { color: var(--text-tertiary); padding: 10px; display: flex; align-items: center; gap: 8px; }

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-secondary);
}
.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left-color: #8b5cf6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .list-card { padding: 20px; }
  .summary-grid { grid-template-columns: 1fr; }
  .filters-grid { grid-template-columns: 1fr; }
  .section-heading { flex-direction: column; align-items: flex-start; gap: 6px; }
  .pagination { flex-direction: column; align-items: stretch; }
  .pagination-pages { justify-content: center; }
  .pagination-limit { justify-content: center; }
  .row-actions { flex-direction: column; align-items: center; }
}
</style>

<style>
/* Estilos del modal de ayuda (SweetAlert2 renderiza el HTML fuera del componente,
   por eso van en un bloque no-scoped para que las clases sí apliquen). */
.ayuda-backups {
  display: flex;
  flex-direction: column;
  gap: 14px;
  text-align: left;
  color: var(--text-secondary);
  font-size: 0.94rem;
  line-height: 1.55;
}

.ayuda-intro {
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: var(--hover-bg);
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--accent-color);
  border-radius: 10px;
  padding: 12px 14px;
}
.ayuda-intro i { color: var(--accent-color); margin-top: 4px; }
.ayuda-intro strong { color: var(--text-primary); }

.ayuda-horarios {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 14px;
}
.ayuda-fila {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ayuda-fila strong { color: var(--text-primary); }
.ayuda-badge {
  min-width: 76px;
  text-align: center;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.ayuda-diario { color: #0ea5e9; background: rgba(14, 165, 233, 0.12); border: 1px solid rgba(14, 165, 233, 0.3); }
.ayuda-semanal { color: #f59e0b; background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3); }
.ayuda-mensual { color: #10b981; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); }

.ayuda-manual {
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 0.88rem;
  color: var(--text-tertiary);
}
.ayuda-manual i { color: var(--accent-color); margin-top: 4px; }
.ayuda-manual strong { color: var(--text-secondary); }

/* SweetAlert2 pinta el popup de blanco por defecto; en modo oscuro (default)
   eso choca con las variables oscuras del contenido. Solo se adapta este
   modal en oscuro; el modo claro queda exactamente igual (popup blanco). */
:root:not(.light-theme) .ayuda-swal-popup {
  background: var(--bg-secondary);
}
:root:not(.light-theme) .ayuda-swal-popup .swal2-title {
  color: var(--text-primary);
}
:root:not(.light-theme) .ayuda-swal-popup .swal2-html-container {
  color: var(--text-secondary);
}
</style>