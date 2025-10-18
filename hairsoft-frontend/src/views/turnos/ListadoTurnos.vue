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
            <label>Buscar</label>
            <input 
              v-model="filtros.busqueda" 
              type="text" 
              placeholder="Cliente, DNI o Servicio..." 
              class="filter-input" 
            />
          </div>
          <div class="filter-group">
            <label>Peluquero</label>
            <select v-model="filtros.peluquero" class="filter-select">
              <option value="">Todos</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">{{ p.nombre }} {{ p.apellido }}</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-select">
              <option value="">Todos</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="CONFIRMADO">Confirmado</option>
              <option value="CANCELADO">Cancelado</option>
              <option value="COMPLETADO">Completado</option>
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
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar filtros</button>
          </div>
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
              <th>Teléfono</th>
              <th>Peluquero</th>
              <th>Servicios</th>
              <th>Estado</th>
              <th>Duración</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in turnosFiltradosPaginados" :key="t.id">
              <td>{{ formatFecha(t.fecha) }}</td>
              <td>{{ formatHora(t.hora) }}</td>
              <td>{{ t.cliente.nombre }} {{ t.cliente.apellido }}</td>
              <td>{{ t.cliente.telefono || 'No registrado' }}</td>
              <td>{{ t.peluquero.nombre }} {{ t.peluquero.apellido }}</td>
              <td>{{ t.servicios.map(s => s.nombre).join(', ') }}</td>
              <td>{{ t.estado }}</td>
              <td>{{ calcularDuracion(t.servicios) }} min</td>
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
const filtros = ref({
  busqueda: '',
  peluquero: '',
  estado: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Cargar turnos desde backend
const cargarTurnos = async () => {
  try {
    const params = new URLSearchParams()
    if (filtros.value.peluquero) params.append('peluquero', filtros.value.peluquero)
    if (filtros.value.estado) params.append('estado', filtros.value.estado)
    if (filtros.value.fechaDesde) params.append('fecha_desde', filtros.value.fechaDesde)
    if (filtros.value.fechaHasta) params.append('fecha_hasta', filtros.value.fechaHasta)

    const res = await fetch(`http://localhost:8000/usuarios/api/turnos/?${params.toString()}`)
    const data = await res.json()

    // Transformar datos a estructura esperada
    turnos.value = data.map(t => ({
      id: t.id,
      fecha: t.fecha,
      hora: t.hora,
      estado: t.estado,
      cliente: {
        nombre: t.cliente.split(' ')[0] || '',
        apellido: t.cliente.split(' ')[1] || '',
        telefono: t.cliente_telefono || ''
      },
      peluquero: {
        nombre: t.peluquero.split(' ')[0] || '',
        apellido: t.peluquero.split(' ')[1] || ''
      },
      servicios: t.servicios.map(s => ({ nombre: s }))
    }))
  } catch (err) {
    console.error('Error al cargar turnos:', err)
    turnos.value = []
  }
}

// Cargar peluqueros para filtro
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

// Formateo
const formatFecha = fechaString => {
  if (!fechaString) return '–'
  const fecha = new Date(fechaString)
  return isNaN(fecha.getTime()) ? '–' : fecha.toLocaleDateString('es-ES')
}

const formatHora = horaString => {
  if (!horaString) return '–'
  return horaString.slice(0,5)
}

const calcularDuracion = servicios => servicios.reduce((sum, s) => sum + (s.duracion || 20), 0)

// Paginación
const totalPaginas = computed(() => Math.ceil(turnos.value.length / itemsPorPagina))
const turnosFiltradosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return turnos.value.slice(inicio, fin)
})
const paginaAnterior = () => { if(pagina.value>1) pagina.value-- }
const paginaSiguiente = () => { if(pagina.value<totalPaginas.value) pagina.value++ }

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = { busqueda:'', peluquero:'', estado:'', fechaDesde:'', fechaHasta:'' }
  pagina.value = 1
  cargarTurnos()
}

// Ir a registrar turno
const irARegistrar = () => router.push('/turnos/crear')
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