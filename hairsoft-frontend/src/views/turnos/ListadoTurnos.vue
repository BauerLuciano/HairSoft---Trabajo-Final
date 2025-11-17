<template>
  <div class="turnos-container">
    <div class="list-card">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>
            <Calendar class="header-icon" />
            Lista de Turnos
          </h1>
          <p>Gestión y administración de turnos de la barbería</p>
        </div>
        <button @click="irARegistrar" class="register-button">
          <Plus :size="18" />
          Registrar Turno
        </button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar Cliente</label>
            <input 
              v-model="filtros.busqueda" 
              placeholder="Nombre o apellido..." 
              class="filter-input standard-height"
            />
          </div>

          <div class="filter-group">
            <label>Peluquero</label>
            <select v-model="filtros.peluquero" class="filter-input standard-height">
              <option value="">Todos</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                {{ p.nombre }} {{ p.apellido }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input standard-height">
              <option value="">Todos</option>
              <option v-for="estado in estadosDisponibles" :key="estado" :value="estado">
                {{ formatearEstado(estado) }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Canal</label>
            <select v-model="filtros.canal" class="filter-input standard-height">
              <option value="">Todos</option>
              <option value="WEB">Web</option>
              <option value="PRESENCIAL">Presencial</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Fecha desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input standard-height"/>
          </div>

          <div class="filter-group">
            <label>Fecha hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input standard-height"/>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn standard-height">
              <Trash2 :size="16" />
              Limpiar
            </button>
          </div>
        </div>
      </div>

      <!-- Tabla de Turnos -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Fecha - turno</th>
              <th>Hora - turno</th>
              <th>Cliente</th>
              <th>Peluquero</th>
              <th>Servicios</th>
              <th>Estado</th>
              <th>Pago</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="turno in turnosFiltradosPaginados" :key="turno.id">
              <td><strong>{{ formatFecha(turno.fecha) }}</strong></td>
              <td><strong>{{ formatHora(turno.hora) }}</strong></td>
              <td>
                <div class="cliente-info">
                  <strong>{{ turno.cliente_nombre }} {{ turno.cliente_apellido }}</strong>
                  <div class="info-adicional">
                    <span class="canal-badge" :class="turno.canal.toLowerCase()">
                      {{ turno.canal === 'WEB' ? '🌐 Web' : '🏪 Presencial' }}
                    </span>
                  </div>
                </div>
              </td>
              <td>{{ turno.peluquero_nombre }}</td>
              <td class="servicios-columna">
                <div class="servicios-compactos">
                  <div 
                    v-for="(servicio, index) in getServiciosLista(turno.servicios).slice(0, 2)" 
                    :key="index"
                    class="servicio-item"
                  >
                    <span class="servicio-nombre">• {{ servicio }}</span>
                  </div>
                  <div v-if="getServiciosLista(turno.servicios).length > 2" class="mas-servicios">
                    +{{ getServiciosLista(turno.servicios).length - 2 }} más
                  </div>
                </div>
                <div class="duracion-total">{{ turno.duracion_total }} min</div>
              </td>
              <td>
                <span class="badge-estado" :class="getEstadoClass(turno.estado)">
                  {{ formatearEstado(turno.estado) }}
                </span>
              </td>
              <td>
                <span class="badge-estado" :class="getPagoClass(turno.tipo_pago)">
                  {{ getPagoTexto(turno.tipo_pago) }}
                </span>
                <div v-if="turno.tipo_pago === 'SENA_50'" class="monto-info">
                  ${{ turno.monto_seña }} / ${{ turno.monto_total }}
                </div>
              </td>
              <td>
                <div class="action-buttons-compact">
                  <!-- Botón Editar -->
                  <button 
                    v-if="turno.puede_modificar"
                    @click="modificarTurno(turno.id)"
                    class="btn-action-icon edit"
                    title="Modificar turno"
                  >
                    <Edit3 :size="16" />
                  </button>

                  <!-- Botón Señar -->
                  <button 
                    v-if="turno.estado === 'RESERVADO' && turno.tipo_pago === 'PENDIENTE'"
                    @click="procesarSena(turno)"
                    class="btn-action-icon sena"
                    title="Procesar seña"
                  >
                    <DollarSign :size="16" />
                  </button>

                  <!-- Botón Cancelar -->
                  <button 
                    v-if="turno.puede_cancelar"
                    @click="cancelarTurno(turno)"
                    class="btn-action-icon delete"
                    title="Cancelar turno"
                  >
                    <Trash2 :size="16" />
                  </button>

                  <!-- Botón Completar -->
                  <button 
                    v-if="turno.puede_completar"
                    @click="completarTurno(turno.id)"
                    class="btn-action-icon complete"
                    title="Marcar como completado"
                  >
                    <Check :size="16" />
                  </button>

                  <span 
                    v-if="!turno.puede_modificar && !turno.puede_cancelar && !turno.puede_completar && !(turno.estado === 'RESERVADO' && turno.tipo_pago === 'PENDIENTE')" 
                    class="sin-acciones"
                  >
                    -
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="turnosFiltradosPaginados.length === 0" class="no-results">
          <SearchX class="no-resultados-icon" :size="48" />
          <p>No se encontraron turnos</p>
          <small>Intenta con otros términos de búsqueda</small>
          <button @click="limpiarFiltros" class="btn-reintentar">
            <Trash2 :size="16" />
            Limpiar Filtros
          </button>
        </div>
      </div>

      <!-- Resumen y paginación -->
      <div class="usuarios-count">
        <div class="resumen-info">
          <span>
            <Calendar :size="16" />
            Mostrando {{ turnosFiltradosPaginados.length }} de {{ turnosFiltrados.length }} turnos
          </span>
        </div>
        
        <div class="pagination">
          <button @click="paginaAnterior" :disabled="pagina === 1" class="btn-pagination">
            <ChevronLeft :size="16" />
            Anterior
          </button>
          <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
          <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="btn-pagination">
            Siguiente
            <ChevronRight :size="16" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Calendar, Plus, Trash2, Edit3, Check, 
  SearchX, ChevronLeft, ChevronRight, DollarSign
} from 'lucide-vue-next'
import Swal from 'sweetalert2'

const router = useRouter()
const turnos = ref([])
const peluqueros = ref([])
const pagina = ref(1)
const itemsPorPagina = 10

const estadosDisponibles = ref(['RESERVADO', 'CONFIRMADO', 'COMPLETADO', 'CANCELADO'])

const filtros = ref({
  busqueda: '',
  peluquero: '',
  estado: '',
  canal: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Cargar peluqueros
const cargarPeluqueros = async () => {
  try {
    const res = await fetch('http://localhost:8000/usuarios/api/peluqueros/')
    peluqueros.value = await res.json()
  } catch (err) {
    console.error('Error al cargar peluqueros:', err)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Error al cargar los peluqueros',
      confirmButtonText: 'Entendido'
    })
  }
}

// Cargar turnos
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

    // Ordenar turnos: activos primero, cancelados al final
    const turnosOrdenados = data
      .map(t => ({
        id: t.id,
        fecha: t.fecha,
        hora: t.hora,
        estado: t.estado,
        canal: t.canal || 'PRESENCIAL',
        tipo_pago: t.tipo_pago || 'PENDIENTE',
        monto_seña: t.monto_seña || 0,
        monto_total: t.monto_total || 0,
        cliente_nombre: t.cliente_nombre || '',
        cliente_apellido: t.cliente_apellido || '',
        peluquero_nombre: t.peluquero_nombre || '',
        servicios: Array.isArray(t.servicios) ? t.servicios : [],
        duracion_total: t.duracion_total || 0,
        puede_modificar: (t.estado === 'RESERVADO' || t.estado === 'CONFIRMADO') && t.puede_modificar,
        puede_cancelar: (t.estado === 'RESERVADO' || t.estado === 'CONFIRMADO') && t.puede_cancelar,
        puede_completar: (t.estado === 'CONFIRMADO'),
        puede_senar: t.estado === 'RESERVADO' && t.tipo_pago === 'PENDIENTE'
      }))
      .sort((a, b) => {
        // Cancelados van al final
        if (a.estado === 'CANCELADO' && b.estado !== 'CANCELADO') return 1
        if (b.estado === 'CANCELADO' && a.estado !== 'CANCELADO') return -1
        
        // Ordenar por fecha y hora (más recientes primero)
        const fechaA = new Date(`${a.fecha}T${a.hora}`)
        const fechaB = new Date(`${b.fecha}T${b.hora}`)
        return fechaB - fechaA
      })

    turnos.value = turnosOrdenados

  } catch (err) {
    console.error('Error al cargar turnos:', err)
    turnos.value = []
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Error al cargar los turnos',
      confirmButtonText: 'Entendido'
    })
  }
}

// Cargar todo
const cargarTodo = async () => {
  try {
    await cargarPeluqueros()
    await cargarTurnos()
  } catch (error) {
    console.error('Error cargando datos:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Error al cargar los datos iniciales',
      confirmButtonText: 'Entendido'
    })
  }
}

// Filtros
const turnosFiltrados = computed(() => {
  let resultados = [...turnos.value]

  if (filtros.value.busqueda) {
    const busqueda = filtros.value.busqueda.toLowerCase()
    resultados = resultados.filter(turno => {
      const nombreCompleto = `${turno.cliente_nombre} ${turno.cliente_apellido}`.toLowerCase()
      return nombreCompleto.includes(busqueda)
    })
  }

  if (filtros.value.estado) {
    resultados = resultados.filter(turno => turno.estado === filtros.value.estado)
  }

  if (filtros.value.canal) {
    resultados = resultados.filter(turno => turno.canal === filtros.value.canal)
  }

  if (filtros.value.fechaDesde) {
    resultados = resultados.filter(turno => turno.fecha >= filtros.value.fechaDesde)
  }

  if (filtros.value.fechaHasta) {
    resultados = resultados.filter(turno => turno.fecha <= filtros.value.fechaHasta)
  }

  return resultados
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

// Formateadores
const formatFecha = fechaString => {
  if (!fechaString) return '–'
  try {
    const [year, month, day] = fechaString.split('-')
    return `${day}/${month}/${year}`
  } catch (e) {
    console.error('Error formateando fecha:', fechaString, e)
    return '–'
  }
}

const formatHora = horaString => {
  if (!horaString) return '–'
  return horaString.slice(0,5)
}

const getServiciosLista = (servicios) => {
  if (!Array.isArray(servicios)) return []
  return servicios.map(s => typeof s === 'string' ? s : s.nombre)
}

const formatearEstado = (estado) => {
  const estados = {
    'RESERVADO': 'Reservado',
    'CONFIRMADO': 'Confirmado', 
    'COMPLETADO': 'Completado',
    'CANCELADO': 'Cancelado'
  }
  return estados[estado] || estado
}

const getEstadoClass = (estado) => {
  const clases = {
    'RESERVADO': 'estado-warning',
    'CONFIRMADO': 'estado-info',
    'COMPLETADO': 'estado-success',
    'CANCELADO': 'estado-danger'
  }
  return clases[estado] || 'estado-secondary'
}

const getPagoClass = (tipoPago) => {
  if (tipoPago === 'SENA_50') return 'estado-info'
  if (tipoPago === 'TOTAL') return 'estado-success'
  return 'estado-warning'
}

const getPagoTexto = (tipoPago) => {
  if (tipoPago === 'SENA_50') return 'Seña 50%'
  if (tipoPago === 'TOTAL') return 'Total'
  return 'Pendiente'
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

const modificarTurno = (turnoId) => {
  router.push(`/turnos/modificar/${turnoId}`)
}

// ✅ NUEVA FUNCIÓN: Completar pago (seña restante)
const completarPago = async (turno) => {
  const montoRestante = turno.monto_total - turno.monto_seña
  
  const result = await Swal.fire({
    title: 'Completar Pago',
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Servicios:</strong> ${getServiciosLista(turno.servicios).join(', ')}</p>
        <p><strong>Monto total:</strong> $${turno.monto_total}</p>
        <p><strong>Seña pagada:</strong> $${turno.monto_seña}</p>
        <p><strong>Restante a pagar:</strong> $${montoRestante}</p>
      </div>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Confirmar Pago',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33'
  })

  if (result.isConfirmed) {
    try {
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/completar-pago/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tipo_pago: 'TOTAL'
        })
      })
      
      const data = await res.json()
      
      if (res.ok && data.status === 'ok') {
        await cargarTurnos()
        Swal.fire({
          icon: 'success',
          title: 'Pago Completado',
          text: data.message,
          confirmButtonText: 'Entendido'
        })
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: data.message || 'Error al completar el pago',
          confirmButtonText: 'Entendido'
        })
      }
    } catch (err) {
      Swal.fire({
        icon: 'error',
        title: 'Error de Conexión',
        text: 'No se pudo conectar con el servidor',
        confirmButtonText: 'Entendido'
      })
    }
  }
}

// ✅ FUNCIÓN: Procesar seña inicial
const procesarSena = async (turno) => {
  const montoSena = turno.monto_total * 0.5
  
  const result = await Swal.fire({
    title: 'Procesar Seña',
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Servicios:</strong> ${getServiciosLista(turno.servicios).join(', ')}</p>
        <p><strong>Monto total:</strong> $${turno.monto_total}</p>
        <p><strong>Seña (50%):</strong> $${montoSena}</p>
      </div>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Procesar Seña',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#f59e0b',
    cancelButtonColor: '#d33'
  })

  if (result.isConfirmed) {
    try {
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/procesar-sena/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tipo_pago: 'SENA_50'
        })
      })
      
      const data = await res.json()
      
      if (res.ok && data.status === 'ok') {
        await cargarTurnos()
        Swal.fire({
          icon: 'success',
          title: 'Seña Procesada',
          text: data.message,
          confirmButtonText: 'Entendido'
        })
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: data.message || 'Error al procesar la seña',
          confirmButtonText: 'Entendido'
        })
      }
    } catch (err) {
      Swal.fire({
        icon: 'error',
        title: 'Error de Conexión',
        text: 'No se pudo conectar con el servidor',
        confirmButtonText: 'Entendido'
      })
    }
  }
}

const cancelarTurno = async (turno) => {
  const result = await Swal.fire({
    title: 'Cancelar Turno',
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Fecha:</strong> ${formatFecha(turno.fecha)} ${formatHora(turno.hora)}</p>
        <p><strong>Servicios:</strong> ${getServiciosLista(turno.servicios).join(', ')}</p>
        ${turno.monto_seña > 0 ? `<p style="color: #f59e0b;"><strong>Seña pagada:</strong> $${turno.monto_seña}</p>` : ''}
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Sí, Cancelar',
    cancelButtonText: 'No, Mantener',
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6'
  })

  if (result.isConfirmed) {
    try {
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/cancelar/`, {
        method: 'POST'
      })
      
      const data = await res.json()
      
      if (res.ok && data.status === 'ok') {
        await cargarTurnos()
        Swal.fire({
          icon: 'success',
          title: 'Turno Cancelado',
          text: data.message,
          confirmButtonText: 'Entendido'
        })
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: data.message || 'Error al cancelar el turno',
          confirmButtonText: 'Entendido'
        })
      }
    } catch (err) {
      Swal.fire({
        icon: 'error',
        title: 'Error de Conexión',
        text: 'No se pudo conectar con el servidor',
        confirmButtonText: 'Entendido'
      })
    }
  }
}

const completarTurno = async (id) => {
  const result = await Swal.fire({
    title: 'Completar Turno',
    text: '¿Marcar este turno como completado?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Sí, Completar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#10b981',
    cancelButtonColor: '#6b7280'
  })

  if (result.isConfirmed) {
    try {
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${id}/completar/`, {
        method: 'POST'
      })
      
      const data = await res.json()
      
      if (res.ok && data.status === 'ok') {
        await cargarTurnos()
        Swal.fire({
          icon: 'success',
          title: 'Turno Completado',
          text: data.message,
          confirmButtonText: 'Entendido'
        })
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: data.message || 'Error al completar el turno',
          confirmButtonText: 'Entendido'
        })
      }
    } catch (err) {
      Swal.fire({
        icon: 'error',
        title: 'Error de Conexión',
        text: 'No se pudo conectar con el servidor',
        confirmButtonText: 'Entendido'
      })
    }
  }
}

onMounted(() => {
  cargarTodo()
})

// Watchers
watch(() => filtros.value.peluquero, () => {
  pagina.value = 1
  cargarTurnos()
})

watch(() => [
  filtros.value.busqueda,
  filtros.value.estado, 
  filtros.value.canal,
  filtros.value.fechaDesde,
  filtros.value.fechaHasta
], () => {
  pagina.value = 1
})
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - COMPACTO
   ======================================== */

/* Tarjeta principal - Fondo oscuro elegante */
.list-card {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  color: #e5e5e5;
  border-radius: 24px;
  padding: 30px;
  width: 100%;
  max-width: 1600px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6),
              0 0 0 1px rgba(100, 100, 100, 0.15) inset;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
}

/* Borde superior azul acero */
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
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.estado-info {
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.estado-success {
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.estado-danger {
  background: linear-gradient(135deg, #3d3d3d, #2a2a2a);
  color: #ef4444;
  border: 2px solid #ef4444;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
  opacity: 0.75;
}

.estado-secondary {
  background: linear-gradient(135deg, #2d3748, #1a202c);
  color: #9ca3af;
  border: 2px solid #9ca3af;
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* HEADER - Diseño masculino */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
  border-bottom: 2px solid rgba(14, 165, 233, 0.25);
  padding-bottom: 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 1.8rem;
  background: linear-gradient(135deg, #ffffff, #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.header-content p {
  color: #9ca3af;
  font-weight: 500;
  margin-top: 5px;
  letter-spacing: 0.5px;
  font-size: 0.9rem;
}

.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
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
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.register-button:hover::before {
  left: 100%;
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

/* FILTROS - Estilo industrial */
.filters-container {
  margin-bottom: 25px;
  background: rgba(0, 0, 0, 0.4);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid rgba(100, 100, 100, 0.2);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-weight: 700;
  margin-bottom: 8px;
  color: #9ca3af;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 1px;
}

.filter-input {
  padding: 10px 12px;
  border: 2px solid #374151;
  border-radius: 8px;
  background: #1a1a1a;
  color: #e5e5e5;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.85rem;
}

.filter-input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
  background: #252525;
}

.clear-filters-btn {
  background: linear-gradient(135deg, #4b5563, #374151);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.clear-filters-btn:hover {
  background: linear-gradient(135deg, #374151, #1f2937);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(75, 85, 99, 0.4);
}

.standard-height {
  height: 40px !important;
  min-height: 40px;
  box-sizing: border-box;
}

.filter-input.standard-height {
  padding: 10px 12px;
}

.clear-filters-btn.standard-height {
  padding: 10px 15px;
}

/* TABLA - Diseño profesional COMPACTO */
.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  border-radius: 12px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(100, 100, 100, 0.2);
  font-size: 0.85rem;
}

.users-table th {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  padding: 14px 10px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
  white-space: nowrap;
}

.users-table td {
  padding: 12px 10px;
  border-bottom: 1px solid rgba(100, 100, 100, 0.12);
  vertical-align: middle;
  color: #d1d1d1;
  font-weight: 500;
}

.users-table td strong {
  color: #ffffff;
  font-weight: 800;
  letter-spacing: 0.3px;
}

.users-table tr:hover {
  background: rgba(14, 165, 233, 0.08);
  transition: all 0.2s ease;
}

/* Información del cliente compacta */
.cliente-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-adicional {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.canal-badge, .pago-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
}

.canal-badge.web {
  background: rgba(14, 165, 233, 0.15);
  color: #0ea5e9;
  border: 1px solid #0ea5e9;
}

.canal-badge.presencial {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
  border: 1px solid #8b5cf6;
}

.pago-sena {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid #f59e0b;
}

.pago-total {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.pago-pendiente {
  background: rgba(107, 114, 128, 0.15);
  color: #9ca3af;
  border: 1px solid #9ca3af;
}

.monto-info {
  font-size: 0.7rem;
  color: #9ca3af;
  margin-top: 4px;
}

/* Servicios compactos */
.servicios-compactos {
  max-width: 180px;
}

.servicio-item {
  padding: 2px 0;
}

.servicio-nombre {
  color: #e5e5e5;
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.mas-servicios {
  color: #9ca3af;
  font-size: 0.75rem;
  font-style: italic;
  padding: 4px 0;
  background: rgba(156, 163, 175, 0.1);
  border-radius: 4px;
  text-align: center;
  margin-top: 4px;
}

.duracion-total {
  color: #0ea5e9;
  font-weight: 700;
  font-size: 0.8rem;
  margin-top: 4px;
  text-align: center;
  background: rgba(14, 165, 233, 0.1);
  padding: 3px 8px;
  border-radius: 8px;
  display: inline-block;
}

/* BOTONES DE ACCIÓN COMPACTOS */
.action-buttons-compact {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-action-icon {
  padding: 8px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  width: 36px;
  height: 36px;
}

.btn-action-icon.edit {
  background: linear-gradient(135deg, #64748b, #475569);
  border: 1px solid rgba(100, 116, 139, 0.4);
  color: white;
}

.btn-action-icon.edit:hover {
  background: linear-gradient(135deg, #475569, #334155);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.5);
}

.btn-action-icon.sena {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border: 1px solid rgba(245, 158, 11, 0.6);
  color: white;
}

.btn-action-icon.sena:hover {
  background: linear-gradient(135deg, #d97706, #b45309);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.5);
}

.btn-action-icon.delete {
  background: linear-gradient(135deg, #3d3d3d, #2a2a2a);
  border: 1px solid rgba(239, 68, 68, 0.6);
  color: #ef4444;
}

.btn-action-icon.delete:hover {
  background: linear-gradient(135deg, #2a2a2a, #1a1a1a);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
  border-color: #ef4444;
}

.btn-action-icon.complete {
  background: linear-gradient(135deg, #059669, #047857);
  border: 1px solid rgba(5, 150, 105, 0.6);
  color: white;
}

.btn-action-icon.complete:hover {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4);
  border-color: #059669;
}

.sin-acciones {
  color: #6b7280;
  font-size: 0.8rem;
  font-style: italic;
}

/* ESTADOS DE CARGA Y NO RESULTADOS */
.no-results {
  text-align: center;
  padding: 60px;
  color: #9ca3af;
}

.btn-reintentar {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 15px;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 15px auto 0;
}

.btn-reintentar:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.5);
}

/* CONTADOR Y PAGINACIÓN */
.usuarios-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  padding: 15px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 10px;
  flex-wrap: wrap;
  gap: 12px;
  border: 1px solid rgba(100, 100, 100, 0.2);
}

.resumen-info {
  color: #9ca3af;
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* PAGINACIÓN */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.pagination button {
  background: linear-gradient(135deg, #475569, #334155);
  color: white;
  border: 1px solid rgba(71, 85, 105, 0.5);
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination button:hover:not(:disabled) {
  background: linear-gradient(135deg, #334155, #1e293b);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(71, 85, 105, 0.5);
}

.pagination button:disabled {
  background: #2d2d2d;
  color: #6b7280;
  cursor: not-allowed;
  transform: none;
  border: 1px solid rgba(107, 114, 128, 0.3);
  opacity: 0.5;
}

.pagination-info {
  color: #e5e5e5;
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 0.85rem;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-card {
    padding: 20px;
    border-radius: 16px;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-content h1 {
    font-size: 1.4rem;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .users-table {
    font-size: 0.8rem;
  }
  
  .users-table th {
    font-size: 0.7rem;
    padding: 12px 8px;
  }
  
  .usuarios-count {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .pagination {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .list-card {
    padding: 15px;
    border-radius: 12px;
  }
  
  .header-content h1 {
    font-size: 1.2rem;
  }
  
  .users-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
    font-size: 0.75rem;
  }
  
  .filter-input {
    font-size: 0.8rem;
  }
  
  .badge-estado {
    font-size: 0.6rem;
    padding: 4px 8px;
  }
  
  .action-buttons-compact {
    flex-direction: column;
    gap: 4px;
  }
  
  .btn-action-icon {
    width: 32px;
    height: 32px;
    padding: 6px;
  }
}
</style>