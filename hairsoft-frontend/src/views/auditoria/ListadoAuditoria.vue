<template>
  <div class="list-container">
    <div class="list-card">
      
      <div class="list-header">
        <div class="header-content">
          <h1>Auditoría del Sistema</h1>
          <p>Registro detallado de actividad y seguridad</p>
        </div>
        <div class="header-buttons">
          <button @click="cargarAuditoria" class="register-button">
            Actualizar
          </button>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Usuario, Modelo..." class="filter-input"/>
          </div>
          <div class="filter-group">
            <label>Acción</label>
            <select v-model="filtros.accion" class="filter-input">
              <option value="">Todas</option>
              <option value="CREACION">Creación</option>
              <option value="MODIFICACION">Modificación</option>
              <option value="ELIMINACION">Eliminación</option>
            </select>
          </div>
          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              Limpiar
            </button>
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
              <th>IP / Nav</th>
              <th>Detalles</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logsPaginados" :key="log.id">
              <td>
                <div style="display: flex; flex-direction: column;">
                  <strong>{{ formatFecha(log.fecha) }}</strong>
                  <span style="font-size: 0.8em; opacity: 0.8;">{{ formatHora(log.fecha) }}</span>
                </div>
              </td>
              <td>
                <div style="font-weight: 600;">
                  {{ log.usuario_nombre ? log.usuario_nombre + ' ' + log.usuario_apellido : 'Sistema / Anónimo' }}
                </div>
              </td>
              <td>
                <span class="badge-estado" :class="getClaseAccion(log.accion)">
                  {{ log.accion }}
                </span>
              </td>
              <td>
                <strong>{{ log.modelo }}</strong>
              </td>
              <td>
                <div style="display: flex; flex-direction: column; font-size: 0.85rem;">
                  <span>{{ log.ip || '-' }}</span>
                  <span style="opacity: 0.7; font-size: 0.8em;">{{ simplificarNavegador(log.navegador) }}</span>
                </div>
              </td>
              <td>
                <button @click="abrirDetalles(log)" class="action-button edit">Ver</button>
              </td>
            </tr>
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
        <div class="modal-header-custom">
          <h2>Detalle de Auditoría</h2>
          <p class="modal-subtitle">Log #{{ logSeleccionado?.id }}</p>
        </div>

        <div class="modal-body-custom">
          <h3 class="section-title">Datos Registrados</h3>
          <div class="json-list">
            <div v-for="(valor, clave) in parseDetalles(logSeleccionado?.detalles)" :key="clave" class="json-item">
              <strong class="json-key">{{ formatearClave(clave) }}:</strong>
              <span class="json-value">{{ valor }}</span>
            </div>
            <div v-if="!logSeleccionado?.detalles" class="no-data-text">Sin detalles</div>
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
    logs.value = res.data
  } catch (err) {
    console.error(err)
  }
}

// Helpers
const parseDetalles = (detalles) => {
  if (!detalles) return {}
  // Priorizar la key 'datos' si existe (nuevo formato)
  const data = detalles.datos || detalles
  
  if (typeof data === 'string') {
    try { return JSON.parse(data) } catch (e) { return { 'Info': data } }
  }
  return data
}

const formatearClave = (clave) => {
  if (!clave) return ''
  return clave.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatFecha = (f) => f ? new Date(f).toLocaleDateString('es-AR') : '-'
const formatHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : ''

const simplificarNavegador = (ua) => {
  if (!ua) return '-'
  if (ua.includes('Edg') || ua.includes('Edge')) return 'Edge'
  if (ua.includes('Chrome')) return 'Chrome'
  if (ua.includes('Firefox')) return 'Firefox'
  return 'Web'
}

const getClaseAccion = (accion) => {
  if (accion === 'CREACION') return 'estado-success'
  if (accion === 'MODIFICACION') return 'estado-info'
  if (accion === 'ELIMINACION') return 'estado-danger'
  return 'estado-secondary'
}

// Filtros
const logsFiltrados = computed(() => {
  return logs.value.filter(log => {
    const term = filtros.value.busqueda.toLowerCase()
    const matchTexto = !term || 
      (log.usuario_nombre && log.usuario_nombre.toLowerCase().includes(term)) ||
      (log.modelo && log.modelo.toLowerCase().includes(term))
    const matchAccion = !filtros.value.accion || log.accion === filtros.value.accion
    return matchTexto && matchAccion
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

const abrirDetalles = (log) => {
  logSeleccionado.value = log
  mostrarModal.value = true
}
const cerrarModal = () => {
  mostrarModal.value = false
  logSeleccionado.value = null
}

watch(filtros, () => { pagina.value = 1 }, { deep: true })
onMounted(cargarAuditoria)
</script>

<style scoped>
/* ========================================
   🔥 TUS ESTILOS EXACTOS DE LISTADOPRODUCTOS.VUE
   ======================================== */

.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
  border: 1px solid var(--border-color);
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

.list-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 35px; flex-wrap: wrap; gap: 20px;
  border-bottom: 2px solid var(--border-color); padding-bottom: 25px;
}

.header-content h1 {
  margin: 0; font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase;
}

.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; letter-spacing: 0.5px; }

.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white; border: none; padding: 14px 28px; border-radius: 12px;
  font-weight: 800; cursor: pointer; transition: all 0.3s ease;
  text-transform: uppercase; letter-spacing: 1px; font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  display: flex; align-items: center; gap: 8px;
}
.register-button:hover {
  transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

.filters-container {
  margin-bottom: 30px; background: var(--hover-bg); padding: 24px;
  border-radius: 16px; border: 1px solid var(--border-color);
}

.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; align-items: end; }
.filter-group { display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }
.filter-input, .filter-select { padding: 12px 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); transition: all 0.3s ease; font-weight: 500; font-size: 0.95rem; }
.filter-input:focus, .filter-select:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); background: var(--bg-secondary); }

.clear-filters-btn {
  background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color);
  padding: 12px 18px; border-radius: 10px; cursor: pointer; font-weight: 700;
  transition: all 0.3s ease; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.8px;
  display: flex; align-items: center; gap: 6px; justify-content: center;
}
.clear-filters-btn:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }

.table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow-md); border: 1px solid var(--border-color); }
.users-table th { background: var(--accent-color); color: white; padding: 18px 14px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px; }
.users-table tr { border-bottom: 1px solid var(--border-color); }
.users-table td { padding: 14px; vertical-align: middle; color: var(--text-secondary); font-weight: 500; }
.users-table tr:hover { background: var(--hover-bg); transition: all 0.2s ease; }

/* Badges */
.badge-estado { padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; letter-spacing: 0.5px; }
.estado-success { background: var(--bg-tertiary); color: #10b981; border: 2px solid #10b981; }
.estado-info { background: var(--bg-tertiary); color: #0ea5e9; border: 2px solid #0ea5e9; }
.estado-danger { background: var(--bg-tertiary); color: var(--error-color); border: 2px solid var(--error-color); }
.estado-warning { background: var(--bg-tertiary); color: #f59e0b; border: 2px solid #f59e0b; }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-tertiary); border: 2px solid var(--text-tertiary); }

.action-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
.action-button { padding: 8px; border: none; border-radius: 10px; font-size: 0.8rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; width: 40px; height: 40px; }
.action-button.edit { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); }
.action-button.edit:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }

.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 25px; }
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 800; transition: all 0.3s ease; display: flex; gap: 8px; align-items: center; }
.pagination button:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-2px); }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination span { color: var(--text-primary); font-weight: 700; }

.no-results { text-align: center; padding: 80px; color: var(--text-secondary); }
.no-results-icon { margin-bottom: 15px; opacity: 0.5; color: var(--text-tertiary); }

/* --- ESTILOS DEL MODAL (ESTILO OSCURO) --- */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.88); backdrop-filter: blur(12px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-content { position: relative; background: var(--bg-secondary); border-radius: 16px; border: 2px solid var(--border-color); padding: 0; margin: 20px; width: 600px; max-width: 95vw; max-height: 85vh; overflow-y: auto; box-shadow: var(--shadow-lg); animation: slideUp 0.3s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }

.modal-close { position: absolute; top: 15px; right: 15px; background: var(--bg-tertiary); border: 2px solid var(--error-color); border-radius: 12px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--error-color); transition: all 0.3s ease; z-index: 10; }
.modal-close:hover { transform: scale(1.15) rotate(90deg); background: var(--hover-bg); }

.modal-header-custom { padding: 25px; border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.modal-header-custom h2 { margin: 0; font-size: 1.5rem; color: var(--text-primary); font-weight: 800; }
.modal-subtitle { margin: 5px 0 0; color: var(--text-secondary); font-size: 0.9rem; }

.modal-body-custom { padding: 25px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
.info-item { display: flex; flex-direction: column; }
.label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 4px; }
.value { font-size: 1rem; font-weight: 600; color: var(--text-primary); }

.divider { border: 0; border-top: 1px solid var(--border-color); margin: 20px 0; }
.section-title { font-size: 1.1rem; color: var(--text-primary); margin-bottom: 15px; }

.json-list { background: var(--hover-bg); border-radius: 12px; padding: 15px; border: 1px solid var(--border-color); }
.json-item { display: flex; flex-direction: column; padding: 8px 0; border-bottom: 1px solid var(--border-color); }
.json-item:last-child { border-bottom: none; }
.json-key { color: #0ea5e9; font-weight: 600; margin-bottom: 2px; }
.json-value { color: var(--text-primary); font-family: monospace; font-size: 0.9em; word-break: break-all; }
.no-data-text { color: var(--text-tertiary); font-style: italic; text-align: center; }

.modal-footer-custom { padding: 20px; border-top: 1px solid var(--border-color); background: var(--bg-primary); display: flex; justify-content: flex-end; }

/* SCROLLBAR */
.modal-content::-webkit-scrollbar, .table-container::-webkit-scrollbar { width: 8px; }
.modal-content::-webkit-scrollbar-thumb, .table-container::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }

@media (max-width: 768px) {
  .list-card { padding: 20px; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .info-grid { grid-template-columns: 1fr; }
}
</style>