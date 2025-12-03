<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Turnos</h1>
          <p>Gestión y administración de turnos</p>
        </div>
        <button @click="irARegistrar" class="register-button">
          <Plus :size="18" />
          Registrar Turno
        </button>
      </div>

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
              <th>Hora</th>
              <th>Cliente</th>
              <th>Peluquero</th>
              <th>Servicios</th>
              <th>Duración</th>
              <th>Estado</th>
              <th>Precio Total</th>
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
                    <span class="canal-badge" :class="(turno.canal || '').toLowerCase()">
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
                  <div v-for="(servicio, index) in getServiciosLista(turno.servicios).slice(0, 2)" :key="index" class="servicio-item">
                    <span class="servicio-nombre">• {{ servicio }}</span>
                  </div>
                  <div v-if="getServiciosLista(turno.servicios).length > 2" class="mas-servicios">
                    +{{ getServiciosLista(turno.servicios).length - 2 }} más
                  </div>
                </div>
              </td>
              
              <td>
                <div style="display: flex; align-items: center; gap: 5px; color: #64748b; font-weight: 600;">
                  <Clock :size="16" />
                  {{ turno.duracion_total || 0 }} min
                </div>
              </td>

              <td>
                <span class="badge-estado" :class="getEstadoClass(turno.estado, turno.tipo_pago)">
                  {{ getEstadoTexto(turno.estado, turno.tipo_pago) }}
                </span>
              </td>
              <td>
                <div class="precio-total-container">
                  <span class="precio-total">
                    ${{ formatPrecio(turno.monto_total) }}
                  </span>
                  <div v-if="turno.tipo_pago === 'SENA_50'" class="detalle-pago-mini">
                    <small>Seña: ${{ formatPrecio(turno.monto_seña || calcularPrecioTotal(turno) * 0.5) }}</small>
                    <br>
                    <small>Falta: ${{ formatPrecio(calcularPrecioTotal(turno) - (turno.monto_seña || calcularPrecioTotal(turno) * 0.5)) }}</small>
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <!-- BOTÓN VER DETALLE - SIEMPRE VISIBLE -->
                  <button @click="verDetalleTurno(turno)" class="action-button view" title="Ver Detalle">
                    <Eye :size="14"/>
                  </button>
                  
                  <!-- BOTÓN EDITAR - CORREGIDO: Visible cuando no esté COMPLETADO ni CANCELADO -->
                  <button v-if="turno.estado !== 'COMPLETADO' && turno.estado !== 'CANCELADO'" 
                          @click="modificarTurno(turno.id)" 
                          class="action-button edit" 
                          title="Editar">
                    <Edit3 :size="14"/>
                  </button>
                  
                  <button v-if="turno.estado === 'RESERVADO' && turno.tipo_pago === 'SENA_50'" 
                          @click="confirmarPagoTotal(turno)" 
                          class="action-button pagar" 
                          title="Confirmar Pago Total">
                    <CreditCard :size="14"/>
                  </button>
                  
                  <button v-if="turno.estado === 'CONFIRMADO'" 
                          @click="completarTurno(turno)" 
                          class="action-button complete" 
                          title="Marcar como Completado">
                    <Check :size="14"/>
                  </button>
                  
                  <button v-if="turno.estado === 'RESERVADO' || turno.estado === 'CONFIRMADO'" 
                          @click="cancelarTurno(turno)" 
                          class="action-button delete" 
                          title="Cancelar Turno">
                    <Trash2 :size="14"/>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="turnosFiltradosPaginados.length === 0" class="no-results">
          <SearchX class="no-results-icon" :size="48" />
          <p>No se encontraron turnos</p>
          <button @click="limpiarFiltros" class="btn-reintentar">Limpiar Filtros</button>
        </div>
      </div>

      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1"><ChevronLeft :size="16"/> Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas || 1 }}</span>
        <button @click="paginaSiguiente" :disabled="pagina >= totalPaginas">Siguiente <ChevronRight :size="16"/></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Plus, Trash2, Edit3, Check, SearchX, ChevronLeft, 
  ChevronRight, Eye, CreditCard, Clock
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

const formatFecha = s => {
    if(!s) return '-';
    try { const [y,m,d] = s.split('-'); return `${d}/${m}/${y}`; } catch(e) { return s; }
}

const formatHora = s => (s && s.length >= 5) ? s.slice(0,5) : '-'

const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  return parseFloat(precio).toFixed(2)
}

const getServiciosLista = s => {
  if (!s) return []
  if (Array.isArray(s)) {
    return s.map(x => {
      if (typeof x === 'string') return x
      if (typeof x === 'object' && x.nombre) return x.nombre
      return String(x)
    })
  }
  return []
}

const formatearEstado = e => ({
  'RESERVADO':'Reservado',
  'CONFIRMADO':'Confirmado',
  'COMPLETADO':'Completado',
  'CANCELADO':'Cancelado'
}[e] || e)

const getEstadoTexto = (estado, tipoPago) => {
  if (estado === 'RESERVADO') {
    return tipoPago === 'SENA_50' ? 'Reservado (Con Seña)' : 'Reservado (Pagado Total)'
  }
  if (estado === 'CONFIRMADO') return 'Confirmado'
  if (estado === 'COMPLETADO') return 'Completado'
  if (estado === 'CANCELADO') return 'Cancelado'
  return estado
}

const getEstadoClass = (estado, tipoPago) => {
  if (estado === 'RESERVADO') {
    return tipoPago === 'SENA_50' ? 'estado-warning' : 'estado-success'
  }
  if (estado === 'CONFIRMADO') return 'estado-success'
  if (estado === 'COMPLETADO') return 'estado-completado'
  if (estado === 'CANCELADO') return 'estado-cancelado'
  return 'estado-secondary'
}

const calcularPrecioTotal = (turno) => {
  if (turno.monto_total && turno.monto_total > 0) return turno.monto_total
  if (turno.servicios && Array.isArray(turno.servicios)) {
    return turno.servicios.reduce((total, servicio) => total + (servicio.precio || 0), 0)
  }
  return 0
}

const verDetalleTurno = async (turno) => {
  try {
    const precioTotal = calcularPrecioTotal(turno)
    const serviciosList = getServiciosLista(turno.servicios)
    
    let serviciosDetallados = []
    if (turno.servicios && Array.isArray(turno.servicios)) {
      serviciosDetallados = turno.servicios.map(s => {
        if (typeof s === 'object') {
          return { nombre: s.nombre || 'Servicio', precio: s.precio || 0 }
        }
        return { nombre: s, precio: 0 }
      })
    }
    
    const clienteNombre = turno.cliente_nombre || ''
    const clienteApellido = turno.cliente_apellido || ''
    const peluqueroNombre = turno.peluquero_nombre || ''
    const montoSeña = turno.monto_seña || (turno.tipo_pago === 'SENA_50' ? precioTotal * 0.5 : 0)
    const saldoPendiente = precioTotal - montoSeña
    
    let html = `
      <div class="detalle-turno" style="text-align: left; max-width: 600px;">
        <div class="detalle-header">
          <h3 style="margin-top: 0; color: #0ea5e9; border-bottom: 2px solid #0ea5e9; padding-bottom: 10px;">
            Detalle del Turno #${turno.id}
          </h3>
        </div>
        
        <div class="detalle-info-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px;">
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Cliente:</strong><br>
            <span style="color: #1e293b;">${clienteNombre} ${clienteApellido}</span>
          </div>
          
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Peluquero:</strong><br>
            <span style="color: #1e293b;">${peluqueroNombre}</span>
          </div>
          
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Fecha:</strong><br>
            <span style="color: #1e293b;">${formatFecha(turno.fecha)}</span>
          </div>
          
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Hora:</strong><br>
            <span style="color: #1e293b;">${formatHora(turno.hora)}</span>
          </div>
          
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Duración:</strong><br>
            <span style="color: #1e293b;">${turno.duracion_total || 0} min</span>
          </div>
          
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Estado:</strong><br>
            <span style="color: #1e293b; font-weight: 600;">${getEstadoTexto(turno.estado, turno.tipo_pago)}</span>
          </div>
          
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Canal:</strong><br>
            <span style="color: #1e293b;">${turno.canal === 'WEB' ? '🌐 Web' : '🏪 Presencial'}</span>
          </div>
          
          <div class="info-item" style="padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <strong style="color: #475569;">Tipo de Pago:</strong><br>
            <span style="color: #1e293b;">${turno.tipo_pago === 'SENA_50' ? 'Con Seña 50%' : 'Total'}</span>
          </div>
        </div>
        
        <div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
          <h4 style="margin-top: 0; color: #475569; margin-bottom: 10px;">Servicios</h4>
          <ul style="margin: 0; padding-left: 20px;">
    `
    
    if (serviciosDetallados.length > 0) {
      serviciosDetallados.forEach(servicio => {
        html += `<li style="margin-bottom: 5px; color: #1e293b;">
                  <strong>${servicio.nombre}</strong> - $${servicio.precio.toFixed(2)}
                </li>`
      })
    } else if (serviciosList.length > 0) {
      serviciosList.forEach(servicio => {
        html += `<li style="margin-bottom: 5px; color: #1e293b;">
                  <strong>${servicio}</strong>
                </li>`
      })
    } else {
      html += `<li style="color: #94a3b8;">No hay servicios registrados</li>`
    }
    
    html += `
          </ul>
        </div>
        
        <div style="padding: 15px; background: #0f766e; color: white; border-radius: 8px; margin-bottom: 20px;">
          <h4 style="margin-top: 0; margin-bottom: 10px; color: white;">Resumen Financiero</h4>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
            <div>
              <strong>Precio Total:</strong><br>
              <span style="font-size: 18px; font-weight: bold;">$${precioTotal.toFixed(2)}</span>
            </div>
    `
    
    if (turno.tipo_pago === 'SENA_50') {
      html += `
            <div>
              <strong>Seña Pagada:</strong><br>
              <span style="font-size: 18px; font-weight: bold;">$${montoSeña.toFixed(2)}</span>
            </div>
            <div>
              <strong>Saldo Pendiente:</strong><br>
              <span style="font-size: 18px; font-weight: bold;">$${saldoPendiente.toFixed(2)}</span>
            </div>
      `
    }
    
    html += `
          </div>
        </div>
      </div>
    `
    
    await Swal.fire({
      title: `Turno #${turno.id}`,
      html: html,
      width: 650,
      showCloseButton: true,
      showConfirmButton: true,
      confirmButtonText: 'Cerrar',
      confirmButtonColor: '#0ea5e9'
    })
    
  } catch (error) {
    console.error('Error al mostrar detalle:', error)
    Swal.fire('Error', 'No se pudo cargar el detalle del turno', 'error')
  }
}

const cargarPeluqueros = async () => {
    try {
        const res = await fetch('http://localhost:8000/usuarios/api/peluqueros/', {
            headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
        })
        peluqueros.value = await res.json()
    } catch(e) {
        console.error('Error cargando peluqueros:', e)
    }
}

const cargarTurnos = async () => {
    try {
        const token = localStorage.getItem('token')
        const p = new URLSearchParams()
        if(filtros.value.peluquero) p.append('peluquero', filtros.value.peluquero)
        if(filtros.value.estado) p.append('estado', filtros.value.estado)
        if(filtros.value.canal) p.append('canal', filtros.value.canal)
        if(filtros.value.fechaDesde) p.append('fecha_desde', filtros.value.fechaDesde)
        if(filtros.value.fechaHasta) p.append('fecha_hasta', filtros.value.fechaHasta)

        const res = await fetch(`http://localhost:8000/usuarios/api/turnos/?${p.toString()}`, {
            headers: { 'Authorization': `Token ${token}` }
        })
        const data = await res.json()
        
        const turnosOrdenados = data.sort((a, b) => {
          const fechaA = new Date(`${a.fecha}T${a.hora}`)
          const fechaB = new Date(`${b.fecha}T${b.hora}`)
          return fechaB - fechaA
        })
        
        turnos.value = turnosOrdenados.map(t => ({
            ...t,
            servicios: Array.isArray(t.servicios) ? t.servicios : [],
            canal: t.canal || 'PRESENCIAL',
            monto_seña: parseFloat(t.monto_seña || 0),
            monto_total: parseFloat(t.monto_total || 0),
        }))
    } catch(e) {
        console.error(e)
        Swal.fire('Error', 'No se pudieron cargar los turnos', 'error')
    }
}

const confirmarPagoTotal = async (turno) => {
  try {
    const precioTotal = calcularPrecioTotal(turno)
    const señaPagada = turno.monto_seña || 0
    const saldoPendiente = precioTotal - señaPagada
    
    const confirm = await Swal.fire({
      title: 'Confirmar Pago Total',
      html: `
        <div style="text-align: left;">
          <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
          <p><strong>Precio Total:</strong> $${precioTotal.toFixed(2)}</p>
          <p><strong>Seña Pagada:</strong> $${señaPagada.toFixed(2)}</p>
          <p><strong>Saldo a Pagar:</strong> $${saldoPendiente.toFixed(2)}</p>
          <p>¿Confirmar que se ha realizado el pago completo del saldo pendiente?</p>
        </div>
      `,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Confirmar Pago Total',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#10b981'
    })

    if (confirm.isConfirmed) {
      Swal.fire({ title: 'Procesando...', didOpen: () => Swal.showLoading() })
      
      const response = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/cambiar-estado/CONFIRMADO/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tipo_pago: 'TOTAL',
          monto_total: precioTotal
        })
      })

      const data = await response.json()

      if (response.ok && data.status === 'ok') {
        await cargarTurnos()
        Swal.fire('¡Pago confirmado!', 'El turno ahora está CONFIRMADO (pagado total).', 'success')
      } else {
        Swal.fire('Error', data.message || 'No se pudo confirmar el pago', 'error')
      }
    }
  } catch (error) {
    console.error('Error confirmando pago:', error)
    Swal.fire('Error', 'No se pudo procesar el pago', 'error')
  }
}

const completarTurno = async (turno) => {
  try {
    const confirm = await Swal.fire({
      title: '¿Completar turno?',
      html: `
        <div style="text-align: left;">
          <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
          <p><strong>Fecha:</strong> ${formatFecha(turno.fecha)}</p>
          <p><strong>Hora:</strong> ${formatHora(turno.hora)}</p>
          <p>¿Marcar este turno como COMPLETADO?</p>
        </div>
      `,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: '✅ Completar',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#10b981'
    })

    if (confirm.isConfirmed) {
      Swal.fire({ title: 'Procesando...', didOpen: () => Swal.showLoading() })

      const response = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/cambiar-estado/COMPLETADO/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (response.ok && data.status === 'ok') {
        await cargarTurnos()
        Swal.fire('¡Completado!', 'Turno marcado como COMPLETADO.', 'success')
      } else {
        Swal.fire('Error', data.message || 'No se pudo completar', 'error')
      }
    }
  } catch (error) {
    console.error('Error completando turno:', error)
    Swal.fire('Error', 'Error de conexión', 'error')
  }
}

const cancelarTurno = async (turno) => {
  try {
    const confirm = await Swal.fire({
      title: '¿Cancelar turno?',
      html: `
        <div style="text-align: left;">
          <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
          <p><strong>Fecha:</strong> ${formatFecha(turno.fecha)}</p>
          <p><strong>Hora:</strong> ${formatHora(turno.hora)}</p>
          <p><strong>Estado Actual:</strong> ${getEstadoTexto(turno.estado, turno.tipo_pago)}</p>
          <p>¿Estás seguro de cancelar este turno?</p>
        </div>
      `,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, cancelar',
      cancelButtonText: 'No',
      confirmButtonColor: '#ef4444'
    })

    if (confirm.isConfirmed) {
      Swal.fire({ title: 'Procesando...', didOpen: () => Swal.showLoading() })
      
      const response = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/cambiar-estado/CANCELADO/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (response.ok && data.status === 'ok') {
        await cargarTurnos()
        Swal.fire('¡Cancelado!', 'Turno cancelado.', 'success')
      } else {
        Swal.fire('Error', data.message || 'No se pudo cancelar', 'error')
      }
    }
  } catch(e) { 
    console.error("Error:", e);
    Swal.fire('Error', 'Error de conexión', 'error'); 
  }
}

const irARegistrar = () => router.push('/turnos/crear-presencial')
const modificarTurno = (id) => router.push(`/turnos/modificar/${id}`)

const limpiarFiltros = () => {
    filtros.value = { busqueda:'', peluquero:'', estado:'', canal:'', fechaDesde:'', fechaHasta:'' }
    pagina.value = 1
    cargarTurnos()
}

const turnosFiltrados = computed(() => {
    let res = turnos.value
    if (filtros.value.busqueda) {
        const b = filtros.value.busqueda.toLowerCase()
        res = res.filter(t => {
          const nombreCompleto = `${t.cliente_nombre || ''} ${t.cliente_apellido || ''}`.toLowerCase()
          return nombreCompleto.includes(b)
        })
    }
    return res
})

const turnosFiltradosPaginados = computed(() => {
    const inicio = (pagina.value - 1) * itemsPorPagina
    return turnosFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

const totalPaginas = computed(() => Math.ceil(turnosFiltrados.value.length / itemsPorPagina))
const paginaAnterior = () => { if(pagina.value>1) pagina.value-- }
const paginaSiguiente = () => { if(pagina.value<totalPaginas.value) pagina.value++ }

onMounted(() => { cargarPeluqueros(); cargarTurnos(); })

watch(() => [
    filtros.value.peluquero, 
    filtros.value.estado, 
    filtros.value.canal, 
    filtros.value.fechaDesde, 
    filtros.value.fechaHasta
], () => { 
    pagina.value = 1; 
    cargarTurnos(); 
})
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

.precio-total {
  font-weight: 900;
  font-size: 1.1rem;
  color: var(--text-primary);
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #0ea5e9, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detalle-pago-mini {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 600;
  background: rgba(245, 158, 11, 0.1);
  padding: 3px 8px;
  border-radius: 6px;
  border: 1px solid rgba(245, 158, 11, 0.2);
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

/* ✅ BOTONES DE ACCIÓN - IGUAL QUE PRODUCTOS */
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

/* VER DETALLE (azul) */
.action-button.view {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.action-button.view:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* EDITAR (gris) */
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

/* SEÑAR (ámbar) */
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

/* PAGAR TOTAL (verde) */
.action-button.pagar {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}

.action-button.pagar:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  border-color: #10b981;
}

/* COMPLETAR (verde fuerte) */
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

/* CANCELAR (rojo) */
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
  
  .precio-total-container {
    min-width: auto;
    padding: 8px;
  }
  
  .precio-total {
    font-size: 0.95rem;
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
  
  .precio-total-container {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}
</style>