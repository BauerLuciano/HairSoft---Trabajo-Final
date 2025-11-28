<template>
  <div class="list-container">
    <div class="list-card">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>
            Gestión de turnos
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
              class="filter-input"
            />
          </div>

          <div class="filter-group">
            <label>Fecha desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Fecha hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Peluquero</label>
            <select v-model="filtros.peluquero" class="filter-input">
              <option value="">Todos</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                {{ p.nombre }} {{ p.apellido }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos</option>
              <option v-for="estado in estadosDisponibles" :key="estado" :value="estado">
                {{ formatearEstado(estado) }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Canal</label>
            <select v-model="filtros.canal" class="filter-input">
              <option value="">Todos</option>
              <option value="WEB">Web</option>
              <option value="PRESENCIAL">Presencial</option>
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
                    <span v-if="turno.oferta_activa" class="badge-reoferta">
                      🔥 Reoferta Activa
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
                <div v-if="turno.oferta_activa" class="info-reoferta">
                  <small>Oferta expira: {{ formatHora(turno.fecha_expiracion_oferta) }}</small>
                </div>
              </td>
              <td>
                <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 6px;">
                  <span class="badge-estado" :class="getPagoClass(turno.tipo_pago)">
                    {{ getPagoTexto(turno.tipo_pago) }}
                  </span>
                  <div v-if="turno.tipo_pago === 'SENA_50'" class="monto-info">
                    ${{ turno.monto_seña }} / ${{ turno.monto_total }}
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <!-- Botón Editar -->
                  <button 
                    v-if="turno.puede_modificar"
                    @click="modificarTurno(turno.id)"
                    class="action-button edit"
                    title="Modificar turno"
                  >
                    <Edit3 :size="14" />
                  </button>

                  <!-- Botón Señar -->
                  <button 
                    v-if="turno.estado === 'RESERVADO' && turno.tipo_pago === 'PENDIENTE'"
                    @click="procesarSena(turno)"
                    class="action-button sena"
                    title="Procesar seña"
                  >
                    <DollarSign :size="14" />
                  </button>

                  <!-- Botón Cancelar CON REOFERTA -->
                  <button 
                    v-if="turno.puede_cancelar"
                    @click="cancelarTurnoConReoferta(turno)"
                    class="action-button delete"
                    title="Cancelar turno"
                  >
                    <Trash2 :size="14" />
                  </button>

                  <!-- Botón Completar -->
                  <button 
                    v-if="turno.puede_completar"
                    @click="completarTurno(turno.id)"
                    class="action-button complete"
                    title="Marcar como completado"
                  >
                    <Check :size="14" />
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
          <SearchX class="no-results-icon" :size="48" />
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
        <p>
          <Calendar :size="16" />
          Mostrando {{ turnosFiltradosPaginados.length }} de {{ turnosFiltrados.length }} turnos
        </p>
        <div class="alertas-container">
          <span v-if="turnosConReoferta > 0" class="alerta-reoferta">
            🔥 {{ turnosConReoferta }} con reoferta activa
          </span>
        </div>
      </div>

      <!-- Paginación -->
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

const estadosDisponibles = ref(['RESERVADO', 'CONFIRMADO', 'COMPLETADO', 'CANCELADO', 'DISPONIBLE'])

const filtros = ref({
  busqueda: '',
  peluquero: '',
  estado: '',
  canal: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Computed para turnos con reoferta
const turnosConReoferta = computed(() => {
  return turnos.value.filter(t => t.oferta_activa).length
})

// Cargar peluqueros
const cargarPeluqueros = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('http://localhost:8000/usuarios/api/peluqueros/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
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
    const token = localStorage.getItem('token')
    const params = new URLSearchParams()
    if (filtros.value.peluquero) params.append('peluquero', filtros.value.peluquero)
    if (filtros.value.estado) params.append('estado', filtros.value.estado)
    if (filtros.value.canal) params.append('canal', filtros.value.canal)
    if (filtros.value.fechaDesde) params.append('fecha_desde', filtros.value.fechaDesde)
    if (filtros.value.fechaHasta) params.append('fecha_hasta', filtros.value.fechaHasta)

    const res = await fetch(`http://localhost:8000/usuarios/api/turnos/?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
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
        puede_senar: t.estado === 'RESERVADO' && t.tipo_pago === 'PENDIENTE',
        // Campos para reoferta
        oferta_activa: t.oferta_activa || false,
        fecha_expiracion_oferta: t.fecha_expiracion_oferta || null
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
  if (typeof horaString === 'string') {
    return horaString.slice(0,5)
  }
  return '–'
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
    'CANCELADO': 'Cancelado',
    'DISPONIBLE': 'Disponible'
  }
  return estados[estado] || estado
}

const getEstadoClass = (estado) => {
  const clases = {
    'RESERVADO': 'estado-warning',
    'CONFIRMADO': 'estado-info',
    'COMPLETADO': 'estado-success',
    'CANCELADO': 'estado-danger',
    'DISPONIBLE': 'estado-secondary'
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

// ✅ NUEVA FUNCIÓN: Cancelar con reoferta
const cancelarTurnoConReoferta = async (turno) => {
  const result = await Swal.fire({
    title: 'Cancelar Turno',
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Fecha:</strong> ${formatFecha(turno.fecha)} ${formatHora(turno.hora)}</p>
        <p><strong>Servicios:</strong> ${getServiciosLista(turno.servicios).join(', ')}</p>
        ${turno.monto_seña > 0 ? `<p style="color: #f59e0b;"><strong>Seña pagada:</strong> $${turno.monto_seña}</p>` : ''}
        <p style="color: #0ea5e9; margin-top: 10px;">
          <strong>🔥 RECOFERTA AUTOMÁTICA:</strong> Se enviarán ofertas a clientes interesados.
        </p>
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Sí, Cancelar y Reofertar',
    cancelButtonText: 'No, Mantener',
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6'
  })

  if (result.isConfirmed) {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/cancelar-con-reoferta/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })
      
      const data = await res.json()
      
      if (res.ok && data.status === 'ok') {
        await cargarTurnos()
        
        if (data.reoferta_iniciada) {
          Swal.fire({
            icon: 'success',
            title: 'Turno Cancelado',
            html: `
              <div style="text-align: left;">
                <p>${data.message}</p>
                <p style="color: #059669; margin-top: 10px;">
                  <strong>✅ Reoferta masiva iniciada:</strong> Se están enviando ofertas a clientes interesados.
                </p>
              </div>
            `,
            confirmButtonText: 'Entendido'
          })
        } else {
          Swal.fire({
            icon: 'success',
            title: 'Turno Cancelado',
            text: data.message,
            confirmButtonText: 'Entendido'
          })
        }
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: data.error || 'Error al cancelar el turno',
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

// Funciones existentes (procesarSena, completarPago, completarTurno) se mantienen igual...
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
      const token = localStorage.getItem('token')
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/procesar-sena/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
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
      const token = localStorage.getItem('token')
      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${id}/completar/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
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
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - TURNOS
   ======================================== */

/* Tarjeta principal - CON VARIABLES */
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

/* Borde superior azul acero */
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* BADGES DE ESTADO - CON VARIABLES */
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
  text-decoration: line-through;
  opacity: 0.75;
}

.estado-secondary {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  border: 2px solid var(--text-tertiary);
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* HEADER - CON VARIABLES */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 25px;
}

.header-content h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-content p {
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.5px;
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
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

/* FILTROS - CON VARIABLES */
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

.filter-group {
  display: flex;
  flex-direction: column;
}

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

/* TABLA - CON VARIABLES */
.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

.users-table th {
  background: var(--accent-color);
  color: white;
  padding: 18px 14px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1.2px;
  white-space: nowrap;
}

.users-table tr {
  border-bottom: 1px solid var(--border-color);
}

.users-table td {
  padding: 14px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-weight: 500;
}

.users-table td strong {
  color: var(--text-primary);
  font-weight: 800;
  letter-spacing: 0.3px;
}

.users-table tr:hover {
  background: var(--hover-bg);
  transition: all 0.2s ease;
}

/* Información del cliente */
.cliente-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-adicional {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.canal-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.7rem;
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

.badge-reoferta {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.monto-info {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 6px;
  font-weight: 700;
  letter-spacing: 0.3px;
  background: var(--bg-tertiary);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  display: inline-block;
}

/* Servicios */
.servicios-compactos {
  max-width: 200px;
}

.servicio-item {
  padding: 3px 0;
}

.servicio-nombre {
  color: var(--text-primary);
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.mas-servicios {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-style: italic;
  padding: 4px 0;
  background: var(--hover-bg);
  border-radius: 4px;
  text-align: center;
  margin-top: 4px;
}

.duracion-total {
  color: #0ea5e9;
  font-weight: 700;
  font-size: 0.85rem;
  margin-top: 6px;
  text-align: center;
  background: rgba(14, 165, 233, 0.1);
  padding: 4px 10px;
  border-radius: 8px;
  display: inline-block;
}

.info-reoferta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 600;
}

/* BOTONES DE ACCIÓN - CON VARIABLES */
.action-buttons { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
}

.action-button {
  padding: 8px;
  border: none;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  width: 40px;
  height: 40px;
}

.action-button.edit {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.action-button.edit:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-button.sena {
  background: var(--bg-tertiary);
  border: 1px solid #f59e0b;
  color: #f59e0b;
}

.action-button.sena:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
  border-color: #f59e0b;
}

.action-button.delete {
  background: var(--bg-tertiary);
  border: 1px solid var(--error-color);
  color: var(--error-color);
}

.action-button.delete:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  border-color: var(--error-color);
}

.action-button.complete {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}

.action-button.complete:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  border-color: #10b981;
}

.sin-acciones {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-style: italic;
}

/* CONTADOR Y MENSAJES - CON VARIABLES */
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

.alertas-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.alerta-reoferta {
  background: var(--bg-tertiary);
  color: #ff6b6b;
  border: 2px solid #ff6b6b;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ESTADOS DE CARGA - CON VARIABLES */
.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
}

.no-results-icon {
  margin-bottom: 15px;
  opacity: 0.5;
  color: var(--text-tertiary);
}

.no-results p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: var(--text-primary);
}

.no-results small {
  font-size: 0.9em;
  color: var(--text-tertiary);
}

.btn-reintentar {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 20px;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 20px auto 0;
}

.btn-reintentar:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5);
}

/* PAGINACIÓN - CON VARIABLES */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
}

.pagination button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination button:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.pagination button:disabled {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  transform: none;
  border: 1px solid var(--border-color);
  opacity: 0.5;
}

.pagination span {
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 0.95rem;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-card {
    padding: 25px;
    border-radius: 20px;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-content h1 {
    font-size: 1.6rem;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .users-table {
    font-size: 0.85rem;
  }
  
  .users-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 6px;
  }
  
  .usuarios-count {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .alertas-container {
    flex-direction: column;
    width: 100%;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .list-card {
    padding: 18px;
    border-radius: 16px;
  }
  
  .header-content h1 {
    font-size: 1.4rem;
  }
  
  .users-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .filter-input, .filter-select {
    font-size: 0.9rem;
  }
  
  .badge-estado {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
  
  .action-button {
    width: 36px;
    height: 36px;
  }
}
</style>