<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Turnos</h1>
          <p>Gestión completa de turnos de la peluquería</p>
        </div>
        <button @click="irARegistrar" class="register-button">
          <span class="btn-text">➕ Registrar Turno</span>
        </button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar Cliente</label>
            <input 
              v-model="filtros.busqueda" 
              type="text" 
              placeholder="Nombre o apellido del cliente..." 
              class="filter-input" 
            />
          </div>
          <div class="filter-group">
            <label>Peluquero</label>
            <select v-model="filtros.peluquero" class="filter-select">
              <option value="">Todos</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                {{ p.nombre }} {{ p.apellido }}
              </option>
            </select>
          </div>
          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-select">
              <option value="">Todos</option>
              <option v-for="estado in estadosDisponibles" :key="estado" :value="estado">
                {{ formatearEstado(estado) }}
              </option>
            </select>
          </div>
          <div class="filter-group">
            <label>Canal</label>
            <select v-model="filtros.canal" class="filter-select">
              <option value="">Todos</option>
              <option value="WEB">Web</option>
              <option value="PRESENCIAL">Presencial</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input"/>
          </div>
          <div class="filter-group">
            <label>Hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input"/>
          </div>
          <div class="filter-group">
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar</button>
          </div>
        </div>
      </div>

      <!-- Resumen de Estados -->
      <div class="estados-summary">
        <div class="summary-item" :class="getEstadoClass('RESERVADO')">
          Reservados: {{ contarTurnosPorEstado('RESERVADO') }}
        </div>
        <div class="summary-item" :class="getEstadoClass('CONFIRMADO')">
          Confirmados: {{ contarTurnosPorEstado('CONFIRMADO') }}
        </div>
        <div class="summary-item" :class="getEstadoClass('COMPLETADO')">
          Completados: {{ contarTurnosPorEstado('COMPLETADO') }}
        </div>
        <div class="summary-item" :class="getEstadoClass('CANCELADO')">
          Cancelados: {{ contarTurnosPorEstado('CANCELADO') }}
        </div>
      </div>

      <!-- Tabla -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Hora</th>
              <th>Cliente</th>
              <th>Peluquero</th>
              <th>Servicios</th>
              <th>Estado</th>
              <th>Canal</th>
              <th>Pago</th>
              <th>Duración</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in turnosFiltradosPaginados" :key="t.id">
              <td class="fecha-turno">{{ formatFecha(t.fecha) }}</td>
              <td class="hora-turno">{{ formatHora(t.hora) }}</td>
              <td>{{ t.cliente_nombre }} {{ t.cliente_apellido }}</td>
              <td>{{ t.peluquero_nombre }} {{ t.peluquero_apellido }}</td>
              <td class="servicios">{{ t.servicios_nombres }}</td>
              <td>
                <span class="status-badge" :class="t.estado.toLowerCase()">
                  {{ formatearEstado(t.estado) }}
                </span>
              </td>
              <td>
                <span class="canal-badge" :class="t.canal.toLowerCase()">
                  {{ t.canal === 'WEB' ? '🌐 Web' : '🏪 Presencial' }}
                </span>
              </td>
              <td class="pago-info">
                <span v-if="t.tipo_pago === 'SENA_50'">Seña 50%</span>
                <span v-else-if="t.tipo_pago === 'TOTAL'">Total</span>
                <span v-else class="pago-pendiente">Pendiente</span>
              </td>
              <td class="duracion">{{ t.duracion_total }} min</td>
              <td class="actions">
                <button 
                  v-if="t.puede_modificar"
                  @click="modificarTurno(t.id)"
                  class="action-button edit"
                  title="Modificar turno"
                >
                  ✏️
                </button>
                <button 
                  v-if="t.puede_cancelar"
                  @click="cancelarTurno(t)"
                  class="action-button cancel"
                  title="Cancelar turno"
                >
                  ❌
                </button>
                <button 
                  v-if="t.puede_completar"
                  @click="completarTurno(t.id)"
                  class="action-button complete"
                  title="Marcar como completado"
                >
                  ✅
                </button>
                <span v-if="!t.puede_modificar && !t.puede_cancelar && !t.puede_completar" class="sin-acciones">
                  -
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="turnosFiltradosPaginados.length === 0" class="no-results">
          <p>No se encontraron turnos con los filtros aplicados</p>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">← Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente →</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const turnos = ref([])
const peluqueros = ref([])
const pagina = ref(1)
const itemsPorPagina = 8

// Estados desde el nuevo modelo
const estadosDisponibles = ref(['RESERVADO', 'CONFIRMADO', 'COMPLETADO', 'CANCELADO'])

const filtros = ref({
  busqueda: '',
  peluquero: '',
  estado: '',
  canal: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Cargar turnos desde backend
const cargarTurnos = async () => {
  try {
    const params = new URLSearchParams()
    if (filtros.value.peluquero) params.append('peluquero', filtros.value.peluquero)
    if (filtros.value.estado) params.append('estado', filtros.value.estado)
    if (filtros.value.canal) params.append('canal', filtros.value.canal)
    if (filtros.value.fechaDesde) params.append('fecha_desde', filtros.value.fechaDesde)
    if (filtros.value.fechaHasta) params.append('fecha_hasta', filtros.value.fechaHasta)

    const res = await fetch(`http://localhost:8000/usuarios/api/turnos/?${params.toString()}`)
    const data = await res.json()

    // Transformar datos con la nueva estructura
    turnos.value = data.map(t => {
      const fechaHoraTurno = new Date(`${t.fecha}T${t.hora}`)
      const ahora = new Date()
      const tresHorasAntes = new Date(fechaHoraTurno.getTime() - (3 * 60 * 60 * 1000))
      
      // Calcular permisos según casos de uso
      const puedeModificar = (t.estado === 'RESERVADO' || t.estado === 'CONFIRMADO') && ahora < tresHorasAntes
      const puedeCancelar = puedeModificar // Misma regla que modificar
      const puedeCompletar = t.estado === 'CONFIRMADO' && ahora >= fechaHoraTurno

      return {
        id: t.id,
        fecha: t.fecha,
        hora: t.hora,
        estado: t.estado,
        canal: t.canal || 'PRESENCIAL',
        tipo_pago: t.tipo_pago || 'PENDIENTE',
        monto_seña: t.monto_seña || 0,
        monto_total: t.monto_total || 0,
        cliente_nombre: t.cliente_nombre || t.cliente?.nombre || '',
        cliente_apellido: t.cliente_apellido || t.cliente?.apellido || '',
        peluquero_nombre: t.peluquero_nombre || t.peluquero?.nombre || '',
        peluquero_apellido: t.peluquero_apellido || t.peluquero?.apellido || '',
        servicios_nombres: Array.isArray(t.servicios) ? 
          t.servicios.map(s => typeof s === 'string' ? s : s.nombre).join(', ') : '',
        duracion_total: t.duracion_total || t.servicios?.reduce((sum, s) => sum + (s.duracion || 20), 0) || 0,
        // Permisos calculados
        puede_modificar: puedeModificar,
        puede_cancelar: puedeCancelar,
        puede_completar: puedeCompletar,
        // Para cálculos
        fecha_hora: fechaHoraTurno
      }
    })

  } catch (err) {
    console.error('Error al cargar turnos:', err)
    turnos.value = []
  }
}

// Resto de funciones se mantienen similares pero adaptadas...
const formatearEstado = (estado) => {
  const estados = {
    'RESERVADO': 'Reservado',
    'CONFIRMADO': 'Confirmado', 
    'COMPLETADO': 'Completado',
    'CANCELADO': 'Cancelado'
  }
  return estados[estado] || estado
}

const contarTurnosPorEstado = (estado) => {
  return turnos.value.filter(t => t.estado === estado).length
}

const getEstadoClass = (estado) => {
  return estado.toLowerCase()
}

// Filtros computados
const turnosFiltrados = computed(() => {
  return turnos.value.filter(turno => {
    // Filtro por búsqueda (nombre/apellido cliente)
    if (filtros.value.busqueda) {
      const busqueda = filtros.value.busqueda.toLowerCase()
      const nombreCompleto = `${turno.cliente_nombre} ${turno.cliente_apellido}`.toLowerCase()
      if (!nombreCompleto.includes(busqueda)) return false
    }
    return true
  })
})

const turnosFiltradosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return turnosFiltrados.value.slice(inicio, fin)
})

const totalPaginas = computed(() => Math.ceil(turnosFiltrados.value.length / itemsPorPagina))

// Funciones de paginación
const paginaAnterior = () => { if(pagina.value>1) pagina.value-- }
const paginaSiguiente = () => { if(pagina.value<totalPaginas.value) pagina.value++ }

const formatFecha = fechaString => {
  if (!fechaString) return '–'
  const fecha = new Date(fechaString)
  return isNaN(fecha.getTime()) ? '–' : fecha.toLocaleDateString('es-ES')
}

const formatHora = horaString => {
  if (!horaString) return '–'
  return horaString.slice(0,5)
}

const limpiarFiltros = () => {
  filtros.value = { 
    busqueda:'', 
    peluquero:'', 
    estado:'', 
    canal:'', 
    fechaDesde:'', 
    fechaHasta:'' 
  }
  pagina.value = 1
  cargarTurnos()
}

const irARegistrar = () => router.push('/turnos/crear-presencial')

// Funciones de acciones
const modificarTurno = (id) => {
  console.log('Modificar turno:', id)
  // router.push(`/turnos/modificar/${id}`)
}

const cancelarTurno = async (turno) => {
  const mensaje = turno.canal === 'WEB' ? 
    '¿Cancelar turno web? Se devolverá la seña si hay +3 horas.' :
    '¿Cancelar turno presencial? Se devolverá el pago si hay +3 horas.'
  
  if (confirm(mensaje)) {
    try {
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/cancelar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (res.ok) {
        await cargarTurnos() // Recargar lista
        alert('Turno cancelado exitosamente')
      } else {
        alert('Error al cancelar el turno')
      }
    } catch (err) {
      console.error('Error:', err)
      alert('Error al cancelar el turno')
    }
  }
}

const completarTurno = async (id) => {
  if (confirm('¿Marcar turno como completado?')) {
    try {
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${id}/completar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (res.ok) {
        await cargarTurnos()
        alert('Turno marcado como completado')
      }
    } catch (err) {
      console.error('Error:', err)
    }
  }
}

// Cargar peluqueros
const cargarPeluqueros = async () => {
  try {
    const res = await fetch('http://localhost:8000/usuarios/api/peluqueros/')
    peluqueros.value = await res.json()
  } catch (err) {
    console.error('Error al cargar peluqueros:', err)
  }
}

onMounted(() => {
  cargarTurnos()
  cargarPeluqueros()
})

watch(filtros, () => {
  pagina.value = 1
  cargarTurnos()
}, { deep: true })
</script>


<style scoped>
/* Mantener todos los estilos base del componente original */

/* Estilos específicos para turnos */
.servicios {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-services {
  color: #9ca3af;
  font-style: italic;
}

.duracion {
  font-weight: 600;
  color: #e5e7eb;
  text-align: center;
}

.fecha-turno, .hora-turno {
  font-weight: 600;
  color: #ffffff;
}

/* Badges de estado específicos */
.status-badge.pendiente {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.status-badge.confirmado {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.status-badge.cancelado {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.status-badge.completado {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

/* Botón de confirmar */
.action-button.confirm {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.action-button.confirm:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* Resumen de estados */
.estados-summary {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.summary-item {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

.summary-item.pendiente {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.summary-item.confirmado {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.summary-item.cancelado {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Modo claro - mantener adaptaciones */
body.light-mode .fecha-turno,
body.light-mode .hora-turno,
body.light-mode .duracion {
  color: #000000;
}

body.light-mode .no-services {
  color: #666666;
}

/* Estilos para badges de canal */
.canal-badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

.canal-badge.web {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid #3b82f6;
}

.canal-badge.presencial {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid #10b981;
}

/* Info de pago */
.pago-info {
  font-size: 0.9rem;
}

.pago-pendiente {
  color: #f59e0b;
  font-style: italic;
}

.sin-acciones {
  color: #9ca3af;
  font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
  .estados-summary {
    flex-direction: column;
    gap: 5px;
  }
  
  .servicios {
    max-width: 150px;
  }
}
</style>