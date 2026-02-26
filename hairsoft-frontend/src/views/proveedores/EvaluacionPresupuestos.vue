<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': generando }">
      
      <div class="list-header">
        <div class="header-content">
          <h1>📋 Evaluación de Presupuestos</h1>
          <p>Análisis y adjudicación de compras de stock</p>
        </div>
        <div class="header-buttons" style="display: flex; gap: 12px;">
          <button @click="cargarDatos" class="register-button" :disabled="cargando">
            <RefreshCw :size="18" :class="{ 'spin': cargando }" />
            Actualizar
          </button>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar Producto</label>
            <div class="search-wrapper">
              <Search :size="16" class="search-icon" />
              <input v-model="filtros.busqueda" placeholder="Ej: Shampoo..." class="filter-input" />
            </div>
          </div>

          <div class="filter-group">
            <label>Tipo de Compra</label>
            <select v-model="filtros.tipo" class="filter-input">
              <option value="">Todos</option>
              <option value="AUTOMATICA"> Automática</option>
              <option value="MANUAL"> Manual</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos</option>
              <option value="PENDIENTE"> Pendiente</option>
              <option value="COTIZADO"> Cotizado (Evaluar)</option>
              <option value="CERRADA"> Cerrada / Adjudicada</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              <Trash2 :size="16" />
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Stock Actual</th>
              <th>Cantidad</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Ofertas</th>
              <th>Recomendación</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="solicitud in solicitudesPaginadas" :key="solicitud.id" 
                :class="{'stock-bajo-row': solicitud.producto_stock <= 10, 'recomendada-row': tieneRecomendacion(solicitud)}">
              
              <td>
                <div class="producto-info">
                  <div class="prod-icon">
                    <Box :size="20" />
                  </div>
                  <div class="info-main">
                    <strong>{{ solicitud.producto_nombre }}</strong>
                    <span class="meta-date">{{ formatDate(solicitud.fecha_creacion) }}</span>
                  </div>
                </div>
              </td>

              <td>
                <span class="badge-estado" :class="getStockClass(solicitud.producto_stock)">
                  {{ solicitud.producto_stock }}
                </span>
              </td>

              <td>
                <strong>{{ solicitud.cantidad_requerida }} u.</strong>
              </td>

              <td>
                <span :class="['badge-tipo', solicitud.tipo_solicitud === 'MANUAL' ? 'tipo-manual' : 'tipo-auto']">
                  {{ solicitud.tipo_solicitud === 'MANUAL' ? ' Manual' : ' Automática' }}
                </span>
              </td>

              <td>
                <span :class="['badge-estado', getEstadoClass(solicitud.estado)]">
                  {{ solicitud.estado }}
                </span>
              </td>

              <td>
                <div class="ofertas-info">
                  <div class="ofertas-count">
                    <span class="total-ofertas">{{ solicitud.cotizaciones.length }} ofertas</span>
                    <span class="respondidas" v-if="ofertasRespondidas(solicitud) > 0">
                      {{ ofertasRespondidas(solicitud) }} respondidas
                    </span>
                  </div>
                  <div v-if="solicitud.estado === 'CERRADA'" class="ganador-info">
                    <Award :size="14" />
                    <span>Adjudicada</span>
                  </div>
                </div>
              </td>

              <td>
                <div class="recomendacion-cell" v-if="tieneRecomendacion(solicitud)">
                  <span class="recomendacion-indicator" :title="getRecomendacionTexto(solicitud)">
                    ⭐
                  </span>
                  <span class="recomendacion-breve">
                    Prioridad Alta
                  </span>
                </div>
                <span v-else class="sin-recomendacion">-</span>
              </td>

              <td>
                <div class="action-buttons">
                  <button 
                    @click="verDetalles(solicitud)"
                    class="action-button edit"
                    title="Ver detalles"
                  >
                    <Eye :size="14" />
                  </button>
                  
                  <button 
                    v-if="solicitud.estado !== 'CERRADA' && ofertasRespondidas(solicitud) > 0"
                    @click="mostrarModalAdjudicar(solicitud)"
                    class="action-button success"
                    title="Adjudicar compra / Aprobar presupuesto"
                  >
                    <CheckCircle :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="cargando" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando licitaciones y pedidos...</p>
        </div>

        <div v-else-if="solicitudesFiltradas.length === 0" class="no-results">
          <FileText class="no-results-icon" :size="48" />
          <p>No se encontraron solicitudes</p>
          <small>Intenta con otros términos de búsqueda</small>
        </div>
      </div>

      <div class="usuarios-count">
        <p>
          <FileText :size="16" />
          Mostrando {{ solicitudesPaginadas.length }} de {{ solicitudesFiltradas.length }} solicitudes
        </p>
        <div class="alertas-container">
          <span v-if="licitacionesPendientes > 0" class="alerta-stock">
            <Clock :size="14" />
            {{ licitacionesPendientes }} pendientes
          </span>
          <span v-if="licitacionesCerradas > 0" class="alerta-inactivo">
            <CheckCircle :size="14" />
            {{ licitacionesCerradas }} cerradas
          </span>
          <span v-if="licitacionesConRecomendacion > 0" class="alerta-recomendacion">
            <Award :size="14" />
            {{ licitacionesConRecomendacion }} prioritarias
          </span>
        </div>
      </div>

      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">
          <ChevronLeft :size="16" />
          Anterior
        </button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">
          Siguiente
          <ChevronRight :size="16" />
        </button>
      </div>

    </div>

    <div v-if="mostrarDetalles" class="modal-overlay" @click.self="cerrarModalDetalles">
      <div class="modal-content modal-detalles">
        <button class="modal-close" @click="cerrarModalDetalles" title="Cerrar detalles">
          <X :size="20" />
        </button>
        
        <div class="modal-header">
          <h2>{{ licitacionSeleccionada.tipo_solicitud === 'MANUAL' ? 'Presupuesto Manual' : 'Detalles de Licitación' }}</h2>
          <div class="modal-header-right">
            <span :class="['badge-estado', getEstadoClass(licitacionSeleccionada.estado)]">
              {{ licitacionSeleccionada.estado }}
            </span>
            <span v-if="tieneRecomendacion(licitacionSeleccionada)" class="recomendacion-badge-modal">
              ⭐ PRIORIDAD ALTA
            </span>
          </div>
        </div>

        <div class="detalles-container">
          <div class="detalle-producto">
            <div class="prod-icon large">
              <Box :size="24" />
            </div>
            <div class="info-detalle">
              <h3>{{ licitacionSeleccionada.producto_nombre }}</h3>
              <div class="meta-info">
                <span><strong>Cantidad requerida:</strong> {{ licitacionSeleccionada.cantidad_requerida }} unidades</span>
                <span><strong>Stock actual:</strong> {{ licitacionSeleccionada.producto_stock }} unidades</span>
                <span><strong>Fecha creación:</strong> {{ formatDate(licitacionSeleccionada.fecha_creacion) }} {{ formatHora(licitacionSeleccionada.fecha_creacion) }}</span>
                <span><strong>Días desde creación:</strong> {{ diasDesdeCreacion(licitacionSeleccionada) }} días</span>
              </div>
            </div>
          </div>

          <div class="recomendacion-detalle" v-if="tieneRecomendacion(licitacionSeleccionada)">
            <div class="recomendacion-header-detalle">
              <Award :size="18" />
              <h4>Análisis de Prioridad</h4>
            </div>
            <p class="recomendacion-texto">
              {{ getRecomendacionTexto(licitacionSeleccionada) }}
            </p>
            <div class="recomendacion-factores">
              <span class="factor" v-if="licitacionSeleccionada.producto_stock <= 10">
                ⚡ Stock crítico
              </span>
              <span class="factor" v-if="licitacionSeleccionada.cotizaciones.length >= 3">
                📈 Múltiples ofertas
              </span>
              <span class="factor" v-if="diasDesdeCreacion(licitacionSeleccionada) > 5">
                ⏰ Urgente por antigüedad
              </span>
            </div>
          </div>

          <div class="cotizaciones-section">
            <div class="cotizaciones-header">
              <h4>{{ licitacionSeleccionada.tipo_solicitud === 'MANUAL' ? 'Oferta Recibida' : 'Ofertas de Proveedores' }}</h4>
              <div class="cotizaciones-stats">
                <span class="stat-item">
                  <strong>Total:</strong> {{ licitacionSeleccionada.cotizaciones.length }}
                </span>
                <span class="stat-item">
                  <strong>Respondidas:</strong> {{ ofertasRespondidas(licitacionSeleccionada) }}
                </span>
                <span class="stat-item">
                  <strong>Mejor precio (Total):</strong> ${{ getMejorPrecio(licitacionSeleccionada)?.toLocaleString() || 'N/A' }}
                </span>
              </div>
            </div>
            
            <div class="table-responsive">
              <table class="users-table detail-table">
                <thead>
                  <tr>
                    <th>Proveedor</th>
                    <th>Estado</th>
                    <th>Cant. Oferta</th> 
                    <th>Precio Unitario</th>
                    <th>Precio Total</th>
                    <th>Tiempo Entrega</th>
                    <th v-if="licitacionSeleccionada.tipo_solicitud !== 'MANUAL'">Calificación</th>
                    <th v-if="licitacionSeleccionada.estado !== 'CERRADA'">Acción</th>
                    <th v-else>Resultado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="cotizacion in licitacionSeleccionada.cotizaciones" :key="cotizacion.id" 
                      :class="{ 
                        'ganadora-row': cotizacion.es_la_mejor,
                        'recomendada-oferta': esOfertaRecomendada(cotizacion, licitacionSeleccionada)
                      }">
                    
                    <td><span class="font-bold">{{ cotizacion.proveedor_nombre }}</span></td>
                    <td><span :class="['badge-sm', cotizacion.respondio ? 'bg-success' : 'bg-pending']">{{ cotizacion.respondio ? 'RESPONDIDO' : 'ESPERANDO' }}</span></td>
                    <td v-if="cotizacion.respondio"><span class="font-bold">{{ cotizacion.cantidad_ofertada || licitacionSeleccionada.cantidad_requerida }} u.</span></td>
                    <td v-else class="text-muted">-</td>
                    <td v-if="cotizacion.respondio">${{ calcularUnitario(cotizacion, licitacionSeleccionada).toLocaleString('es-AR', {minimumFractionDigits: 2}) }}</td>
                    <td v-else class="text-muted">-</td>
                    <td v-if="cotizacion.respondio" class="precio-cell">${{ cotizacion.precio_ofrecido.toLocaleString() }}</td>
                    <td v-else class="text-muted">-</td>
                    <td v-if="cotizacion.respondio">{{ cotizacion.dias_entrega }} días</td>
                    <td v-else class="text-muted">-</td>

                    <template v-if="licitacionSeleccionada.tipo_solicitud !== 'MANUAL'">
                      <td>
                        <div class="calificacion-estrella" v-if="cotizacion.respondio">
                          <span v-for="n in 5" :key="n" :class="['estrella', n <= calcularCalificacion(cotizacion, licitacionSeleccionada) ? 'activa' : '']">★</span>
                          <span class="puntaje">{{ calcularPuntaje(cotizacion, licitacionSeleccionada).toFixed(1) }}/10</span>
                        </div>
                        <span v-else class="text-muted">-</span>
                      </td>
                    </template>

                    <td>
                      <button v-if="cotizacion.respondio && licitacionSeleccionada.estado !== 'CERRADA'"
                        @click="generarOrden(licitacionSeleccionada, cotizacion.id)"
                        class="action-button primary-action"
                        :disabled="generando === licitacionSeleccionada.id"
                      >
                        <CheckCircle :size="14" />
                        <span>{{ licitacionSeleccionada.tipo_solicitud === 'MANUAL' ? 'Aprobar' : 'Adjudicar' }}</span>
                      </button>
                      <div v-if="cotizacion.es_la_mejor" class="winner-badge"><Award :size="14" /><span>CONFIRMADO</span></div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  RefreshCw, Search, Box, FileText, CheckCircle, Award, 
  Trash2, X, Eye, Clock, ChevronLeft, ChevronRight
} from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000';

const solicitudes = ref([])
const cargando = ref(true)
const generando = ref(null)
const filtros = ref({ 
  busqueda: '', 
  estado: '',
  tipo: '', // 👈 NUEVO FILTRO
  orden: 'fecha_desc'
})
const mostrarDetalles = ref(false)
const licitacionSeleccionada = ref({})

const pagina = ref(1)
const itemsPorPagina = 7

const cargarDatos = async () => {
  cargando.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_BASE}/api/evaluaciones-unificadas/`, {
      headers: { Authorization: `Token ${token}` }
    })
    const datos = Array.isArray(response.data) ? response.data : (response.data.results || [])
    solicitudes.value = datos.sort((a, b) => new Date(b.fecha_creacion) - new Date(a.fecha_creacion))
  } catch (error) {
    console.error("Error:", error)
  } finally {
    cargando.value = false
  }
}

const solicitudesFiltradas = computed(() => {
  let filtradas = solicitudes.value.filter(s => {
    const matchBusqueda = s.producto_nombre.toLowerCase().includes(filtros.value.busqueda.toLowerCase())
    const matchEstado = !filtros.value.estado || s.estado === filtros.value.estado
    const matchTipo = !filtros.value.tipo || s.tipo_solicitud === filtros.value.tipo // 👈 LÓGICA FILTRO TIPO
    return matchBusqueda && matchEstado && matchTipo
  })

  // Ordenamiento
  if (filtros.value.orden === 'fecha_desc') filtradas.sort((a, b) => new Date(b.fecha_creacion) - new Date(a.fecha_creacion))
  return filtradas
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(solicitudesFiltradas.value.length / itemsPorPagina)))
const solicitudesPaginadas = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return solicitudesFiltradas.value.slice(inicio, inicio + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

const tieneRecomendacion = (sol) => {
  if (sol.estado === 'CERRADA') return false
  if (sol.tipo_solicitud === 'MANUAL' && sol.estado === 'COTIZADO') return true
  return sol.producto_stock <= 10 || sol.cotizaciones.length >= 3 || diasDesdeCreacion(sol) > 5
}

const getRecomendacionTexto = (sol) => {
  if (sol.tipo_solicitud === 'MANUAL') return "Presupuesto manual recibido. Evaluar precios antes de confirmar."
  return "Se recomienda adjudicar pronto por bajo stock o antigüedad de la solicitud."
}

const getMejorPrecio = (sol) => {
  const ofertasValidas = sol.cotizaciones.filter(c => c.respondio && c.precio_ofrecido > 0)
  return ofertasValidas.length === 0 ? null : Math.min(...ofertasValidas.map(c => c.precio_ofrecido))
}

const esMejorPrecio = (cot, sol) => {
  if (sol.tipo_solicitud === 'MANUAL') return false
  const mejor = getMejorPrecio(sol)
  return cot.precio_ofrecido === mejor
}

const calcularUnitario = (cot, sol) => {
  const cant = cot.cantidad_ofertada || sol.cantidad_requerida
  return cant > 0 ? cot.precio_ofrecido / cant : 0
}

const calcularPuntaje = (cot, sol) => {
  const precios = sol.cotizaciones.filter(c => c.respondio).map(c => c.precio_ofrecido)
  const min = Math.min(...precios)
  const max = Math.max(...precios)
  if (min === max) return 5
  return (1 - ((cot.precio_ofrecido - min) / (max - min))) * 10
}

const calcularCalificacion = (cot, sol) => Math.round(calcularPuntaje(cot, sol) / 2)
const esOfertaRecomendada = (cot, sol) => cot.respondio && sol.tipo_solicitud !== 'MANUAL' && calcularPuntaje(cot, sol) >= 7.5

const diasDesdeCreacion = (sol) => Math.floor((new Date() - new Date(sol.fecha_creacion)) / (1000 * 60 * 60 * 24))
const licitacionesPendientes = computed(() => solicitudesFiltradas.value.filter(s => s.estado === 'PENDIENTE' || s.estado === 'COTIZADO').length)
const licitacionesCerradas = computed(() => solicitudesFiltradas.value.filter(s => s.estado === 'CERRADA').length)
const ofertasRespondidas = (sol) => sol.cotizaciones.filter(c => c.respondio).length

const generarOrden = async (sol, cotId) => {
  const esManual = sol.tipo_solicitud === 'MANUAL'
  const result = await Swal.fire({
    title: esManual ? '¿Aprobar Presupuesto?' : '¿Confirmar Adjudicación?',
    text: esManual ? 'El pedido pasará a estado Confirmado.' : 'Se generará la orden de compra.',
    icon: 'question', showCancelButton: true, confirmButtonColor: '#10b981'
  })
  if (!result.isConfirmed) return
  generando.value = sol.id
  try {
    const token = localStorage.getItem('token')
    const url = esManual ? `${API_BASE}/api/pedidos/${sol.pedido_real_id}/aprobar-manual/` : `${API_BASE}/api/solicitudes-presupuesto/${sol.id}/generar-orden/`
    await axios.post(url, { cotizacion_id: cotId }, { headers: { Authorization: `Token ${token}` } })
    Swal.fire('¡Éxito!', 'Procesado correctamente.', 'success')
    cargarDatos(); cerrarModalDetalles()
  } catch (e) {
    Swal.fire('Error', e.response?.data?.error || 'Error de servidor', 'error')
  } finally { generando.value = null }
}

const verDetalles = (sol) => { licitacionSeleccionada.value = sol; mostrarDetalles.value = true }
const cerrarModalDetalles = () => { mostrarDetalles.value = false; licitacionSeleccionada.value = {} }
const mostrarModalAdjudicar = (sol) => { licitacionSeleccionada.value = sol; mostrarDetalles.value = true }
const formatDate = (d) => new Date(d).toLocaleDateString('es-AR')
const formatHora = (d) => new Date(d).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })

const getEstadoClass = (est) => {
  if (est === 'PENDIENTE') return 'estado-warning'
  if (est === 'COTIZADO') return 'estado-info'
  if (est === 'CERRADA') return 'estado-success'
  return 'estado-secondary'
}

const getStockClass = (s) => s <= 5 ? 'estado-danger' : (s <= 10 ? 'estado-warning' : 'estado-success')
const limpiarFiltros = () => { filtros.value = { busqueda: '', estado: '', tipo: '', orden: 'fecha_desc' }; pagina.value = 1 }

onMounted(() => cargarDatos())
watch(filtros, () => { pagina.value = 1 }, { deep: true })
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - EVALUACIÓN PRESUPUESTOS
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

/* BADGES DE ESTADO */
.badge-estado {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.estado-warning {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.estado-info {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.estado-success {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.estado-danger {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
}

.estado-secondary {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  border: 2px solid var(--text-tertiary);
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* BADGES DE TIPO DE SOLICITUD (MANUAL VS AUTO) */
.badge-tipo {
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.tipo-auto {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.3);
}
.tipo-manual {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.badge-sm {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.bg-success { background: #d1fae5; color: #065f46; }
.bg-pending { background: #f3f4f6; color: #6b7280; }

/* HEADER */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 25px;
}

.header-content { flex: 1; }
.header-content h1 {
  margin: 0 0 10px 0;
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

.recomendacion-badge {
  font-weight: 700;
  color: #f59e0b;
  margin-right: 8px;
}

/* Botón registrar */
.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 8px;
}

.register-button::before {
  content: '';
  position: absolute;
  top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.register-button:hover::before { left: 100%; }
.register-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}
.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

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

.filter-input, .filter-select {
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.filter-input:focus, .filter-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

.search-wrapper { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--text-tertiary); }
.search-wrapper input { padding-left: 35px; }

.clear-filters-btn {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.clear-filters-btn:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* CONTADOR Y MENSAJES */
.usuarios-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0;
  padding: 18px;
  background: var(--hover-bg);
  border-radius: 12px;
  flex-wrap: wrap;
  gap: 15px;
  border: 1px solid var(--border-color);
}

.usuarios-count p {
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.5px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.alertas-container { display: flex; gap: 10px; flex-wrap: wrap; }
.alerta-stock { background: var(--bg-tertiary); color: #f59e0b; border: 2px solid #f59e0b; padding: 8px 16px; border-radius: 20px; font-weight: 700; letter-spacing: 0.5px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; }
.alerta-inactivo { background: var(--bg-tertiary); color: #10b981; border: 2px solid #10b981; padding: 8px 16px; border-radius: 20px; font-weight: 700; letter-spacing: 0.5px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; }
.alerta-recomendacion { background: var(--bg-tertiary); color: #8b5cf6; border: 2px solid #8b5cf6; padding: 8px 16px; border-radius: 20px; font-weight: 700; letter-spacing: 0.5px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; }

/* TABLA */
.table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow-md); border: 1px solid var(--border-color); }
.users-table th { background: var(--accent-color); color: white; padding: 18px 14px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px; }
.users-table tr { border-bottom: 1px solid var(--border-color); }
.users-table td { padding: 14px; vertical-align: middle; color: var(--text-secondary); font-weight: 500; }
.users-table td strong { color: var(--text-primary); font-weight: 800; letter-spacing: 0.3px; }
.users-table tr:hover { background: var(--hover-bg); transition: all 0.2s ease; }

.producto-info { display: flex; align-items: center; gap: 12px; }
.prod-icon { width: 40px; height: 40px; background: var(--bg-tertiary); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--accent-color); }
.prod-icon.large { width: 60px; height: 60px; }
.info-main { display: flex; flex-direction: column; }
.info-main strong { color: var(--text-primary); font-weight: 700; margin-bottom: 4px; }

.meta-date { font-size: 0.8rem; color: var(--text-tertiary); display: block; }
.meta-hora { font-size: 0.75rem; color: var(--text-tertiary); display: block; }
.meta-info { display: flex; flex-direction: column; gap: 4px; font-size: 0.9rem; }

.ofertas-info { display: flex; flex-direction: column; gap: 6px; }
.ofertas-count { display: flex; flex-direction: column; gap: 2px; }
.total-ofertas { font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }
.respondidas { font-size: 0.8rem; color: var(--text-tertiary); }
.ganador-info { display: flex; align-items: center; gap: 6px; color: #10b981; font-weight: 700; font-size: 0.8rem; }

/* Recomendaciones en tabla */
.recomendacion-cell { display: flex; align-items: center; gap: 8px; }
.recomendacion-indicator { color: #f59e0b; font-size: 1.2rem; cursor: help; }
.recomendacion-breve { font-size: 0.85rem; color: var(--text-primary); font-weight: 600; }
.sin-recomendacion { color: var(--text-tertiary); font-size: 0.85rem; }

.stock-bajo-row { background: rgba(245, 158, 11, 0.05); border-left: 3px solid #f59e0b; }
.recomendada-row { background: rgba(139, 92, 246, 0.05); border-left: 3px solid #8b5cf6; }

/* BOTONES DE ACCIÓN */
.action-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
.action-button { padding: 8px; border: none; border-radius: 10px; font-size: 0.8rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; width: 40px; height: 40px; }
.action-button.edit { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); }
.action-button.edit:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.action-button.success { background: var(--bg-tertiary); border: 1px solid #10b981; color: #10b981; }
.action-button.success:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4); border-color: #10b981; }

.primary-action { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 6px; border: 1px solid transparent; cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: all 0.2s; background: #3b82f6; color: white; width: auto; height: auto; }
.primary-action:hover { background: #2563eb; transform: translateY(-1px); }
.primary-action:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.winner-badge { display: flex; align-items: center; gap: 5px; color: #10b981; font-weight: 700; font-size: 0.85rem; }

/* ESTADOS DE CARGA */
.loading-state { text-align: center; padding: 80px; color: var(--text-secondary); }
.spinner { border: 4px solid var(--border-color); border-left: 4px solid var(--accent-color); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; }

.no-results { text-align: center; padding: 80px; color: var(--text-secondary); }
.no-results-icon { margin-bottom: 15px; opacity: 0.5; color: var(--text-tertiary); }
.no-results p { margin: 0 0 8px 0; font-size: 1.1em; color: var(--text-primary); }
.no-results small { font-size: 0.9em; color: var(--text-tertiary); }

/* PAGINACIÓN */
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 25px; }
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 800; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }
.pagination button:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.pagination button:disabled { background: var(--bg-tertiary); color: var(--text-tertiary); cursor: not-allowed; transform: none; border: 1px solid var(--border-color); opacity: 0.5; }
.pagination span { color: var(--text-primary); font-weight: 700; letter-spacing: 0.8px; font-size: 0.95rem; }

/* OVERLAY Y MODALES */
.overlay-activo { opacity: 0.3; filter: blur(5px); pointer-events: none; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.88); backdrop-filter: blur(12px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeInModal 0.3s ease; }
@keyframes fadeInModal { from { opacity: 0; } to { opacity: 1; } }
.modal-content { position: relative; animation: slideUp 0.3s ease; max-height: 85vh; max-width: 90vw; width: auto; overflow-y: auto; border-radius: 16px; background: var(--bg-secondary); box-shadow: var(--shadow-lg); border: 2px solid var(--border-color); padding: 0; margin: 20px; }
.modal-detalles { width: 90%; max-width: 1100px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }

.modal-close { position: absolute; top: 15px; right: 15px; background: var(--bg-tertiary); border: 2px solid var(--error-color); border-radius: 12px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--error-color); box-shadow: var(--shadow-md); transition: all 0.3s ease; z-index: 1001; }
.modal-close:hover { transform: scale(1.15) rotate(90deg); box-shadow: 0 6px 25px rgba(239, 68, 68, 0.6); background: var(--hover-bg); border-color: var(--error-color); }

.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 30px; border-bottom: 2px solid var(--border-color); background: var(--bg-primary); flex-wrap: wrap; gap: 15px; }
.modal-header h2 { margin: 0; color: var(--text-primary); font-weight: 800; font-size: 1.8rem; }
.modal-header-right { display: flex; gap: 10px; align-items: center; }

.recomendacion-badge-modal { background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(234, 179, 8, 0.1)); color: #f59e0b; padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; border: 1px solid #f59e0b; }

.detalles-container { padding: 30px; }
.detalle-producto { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; padding: 20px; background: var(--bg-primary); border-radius: 12px; border: 1px solid var(--border-color); }
.info-detalle h3 { margin: 0 0 10px 0; color: var(--text-primary); font-size: 1.4rem; font-weight: 700; }

.recomendacion-detalle { margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(234, 179, 8, 0.05)); border-radius: 12px; border-left: 4px solid #f59e0b; }
.recomendacion-texto { margin: 0 0 15px 0; color: var(--text-primary); font-size: 0.95rem; line-height: 1.5; }
.recomendacion-factores { display: flex; gap: 10px; flex-wrap: wrap; }
.recomendacion-factores .factor { padding: 6px 12px; background: var(--bg-tertiary); border-radius: 20px; font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }

.cotizaciones-section { margin-top: 30px; }
.cotizaciones-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }
.cotizaciones-header h4 { margin: 0; color: var(--text-primary); font-size: 1.2rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.cotizaciones-stats { display: flex; gap: 20px; font-size: 0.9rem; }
.cotizaciones-stats .stat-item { color: var(--text-secondary); }
.cotizaciones-stats .stat-item strong { color: var(--text-primary); }

.detail-table { width: 100%; font-size: 0.9rem; }
.detail-table th { background: var(--bg-tertiary); padding: 12px 10px; font-weight: 600; color: var(--text-secondary); }
.detail-table td { padding: 12px 10px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
.detail-table tr:last-child td { border-bottom: none; }

.ganadora-row { background: rgba(16, 185, 129, 0.05); }
.ganadora-row td:first-child { border-left: 3px solid #10b981; }
.recomendada-oferta { background: rgba(139, 92, 246, 0.05); }

.mejor-precio-badge { display: inline-block; margin-left: 8px; padding: 2px 6px; background: rgba(34, 197, 94, 0.1); color: #16a34a; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
.entrega-rapida-badge { display: inline-block; margin-left: 8px; padding: 2px 6px; background: rgba(59, 130, 246, 0.1); color: #3b82f6; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
.precio-cell { font-weight: 800; color: var(--text-primary); font-size: 1rem; }
.text-muted { color: var(--text-tertiary); }
.font-bold { font-weight: 700; }

.calificacion-estrella { display: flex; align-items: center; gap: 4px; }
.estrella { color: #d1d5db; font-size: 1rem; transition: all 0.2s; }
.estrella.activa { color: #f59e0b; }
.puntaje { margin-left: 8px; font-size: 0.8rem; color: var(--text-secondary); font-weight: 600; }

.modal-content::-webkit-scrollbar, .table-container::-webkit-scrollbar { width: 12px; height: 12px; }
.modal-content::-webkit-scrollbar-track, .table-container::-webkit-scrollbar-track { background: var(--bg-primary); border-radius: 6px; }
.modal-content::-webkit-scrollbar-thumb, .table-container::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 6px; border: 2px solid var(--bg-primary); }
.modal-content::-webkit-scrollbar-thumb:hover, .table-container::-webkit-scrollbar-thumb:hover { background: var(--accent-color); }

@media (max-width: 768px) {
  .list-card { padding: 25px; border-radius: 20px; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .header-content h1 { font-size: 1.6rem; }
  .filters-grid { grid-template-columns: 1fr; }
  .modal-content { max-width: 95vw; margin: 12px; border-radius: 12px; }
  .modal-detalles { width: 95%; }
  .users-table { font-size: 0.85rem; }
  .users-table th { font-size: 0.7rem; padding: 14px 10px; }
  .action-buttons { flex-direction: column; gap: 6px; }
  .usuarios-count { flex-direction: column; align-items: flex-start; gap: 10px; }
  .alertas-container { flex-direction: column; width: 100%; }
  .detalle-producto { flex-direction: column; text-align: center; }
  .modal-header { flex-direction: column; gap: 15px; align-items: flex-start; }
  .pagination { flex-direction: column; gap: 12px; }
  .cotizaciones-header { flex-direction: column; align-items: flex-start; }
  .cotizaciones-stats { flex-direction: column; gap: 8px; }
}
@media (max-width: 480px) {
  .list-card { padding: 18px; border-radius: 16px; }
  .header-content h1 { font-size: 1.4rem; }
  .users-table { display: block; overflow-x: auto; white-space: nowrap; }
  .filter-input, .filter-select { font-size: 0.9rem; }
  .badge-estado { font-size: 0.65rem; padding: 5px 10px; }
  .action-button { width: 36px; height: 36px; }
  .header-buttons { flex-direction: column; width: 100%; }
  .register-button { width: 100%; justify-content: center; }
  .modal-content { padding: 15px; }
  .detalles-container { padding: 15px; }
}
</style>