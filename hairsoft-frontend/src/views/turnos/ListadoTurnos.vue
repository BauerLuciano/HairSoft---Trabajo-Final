<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Turnos</h1>
          <p>Gestión y administración de turnos</p>
        </div>
        <button @click="irARegistrar" class="register-button"><Plus :size="18" /> Registrar Turno</button>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label for="busqueda">Buscar</label>
            <input v-model="filtros.busqueda" id="busqueda" type="text" class="filter-input" 
                   placeholder="Cliente, Peluquero..." @keyup.enter="cargarTurnos">
          </div>
          <div class="filter-group">
            <label for="estado">Estado</label>
            <select v-model="filtros.estado" id="estado" class="filter-select" @change="cargarTurnos">
              <option value="">Todos</option>
              <option value="RESERVADO">Reservado</option>
              <option value="CONFIRMADO">Confirmado</option>
              <option value="COMPLETADO">Completado</option>
              <option value="CANCELADO">Cancelado</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="canal">Canal</label>
            <select v-model="filtros.canal" id="canal" class="filter-select" @change="cargarTurnos">
              <option value="">Todos</option>
              <option value="WEB">Web</option>
              <option value="PRESENCIAL">Presencial</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="fechaDesde">Desde</label>
            <input v-model="filtros.fechaDesde" id="fechaDesde" type="date" class="filter-input" @change="cargarTurnos">
          </div>
          <div class="filter-group">
            <label for="fechaHasta">Hasta</label>
            <input v-model="filtros.fechaHasta" id="fechaHasta" type="date" class="filter-input" @change="cargarTurnos">
          </div>
          <div class="filter-group">
            <button @click="limpiarFiltros" class="clear-filters-btn"><Trash2 :size="14"/> Limpiar</button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Fecha/Hora</th>
              <th>Cliente</th>
              <th>Estado / Motivo</th>
              <th>Pago / Transacción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="turno in turnosFiltradosPaginados" :key="turno.id">
              <td>
                <strong>{{ formatFecha(turno.fecha) }}</strong><br>
                <small>{{ formatHora(turno.hora) }}hs</small><br>
                <small class="text-muted">{{ getDuracion(turno) }}</small>
              </td>
              <td>
                <strong>{{ turno.cliente_nombre }} {{ turno.cliente_apellido }}</strong><br>
                <span class="canal-badge" :class="(turno.canal || 'PRESENCIAL').toLowerCase()">
                  {{ turno.canal || 'PRESENCIAL' }}
                </span>
              </td>
              <td>
                <span class="badge-estado" :class="getEstadoClass(turno.estado, turno.tipo_pago)">
                  {{ getEstadoTexto(turno.estado, turno.tipo_pago) }}
                </span>
                
                <div v-if="turno.info_descuento" style="margin-top: 5px;">
                  <span class="badge-fidelizacion">
                    <i class="fas fa-gift me-1"></i>
                    {{ turno.info_descuento.texto }}
                  </span>
                </div>
                
                <div v-else-if="turno.descuento_aplicado && turno.descuento_aplicado > 0" style="margin-top: 5px;">
                  <span class="badge-fidelizacion">
                    <i class="bi bi-gift me-1"></i>
                    15% Fidelización
                  </span>
                </div>
                
                <div v-if="turno.estado === 'CANCELADO'">
                  <div v-if="turno.motivo_cancelacion" style="margin-top: 5px;">
                    <span class="badge-motivo-cancelacion">
                      <i class="bi bi-x-circle me-1"></i>
                      {{ turno.motivo_cancelacion }}
                    </span>
                  </div>
                  
                  <div v-if="turno.reembolso_estado === 'NO_APLICA'" style="margin-top: 5px;">
                    <span class="badge-reembolso-no-aplica">
                      <i class="bi bi-arrow-left-right me-1"></i>
                      Canje - No aplica reembolso
                    </span>
                  </div>
                  
                  <div v-if="turno.reembolso_estado === 'PENDIENTE'" style="margin-top: 5px;">
                    <span class="badge-reembolso-pendiente">
                      <i class="bi bi-cash-coin me-1"></i>
                      DEVOLVER ${{ formatPrecio(calcularMontoReembolso(turno)) }}
                    </span>
                  </div>
                  
                  <div v-if="turno.reembolso_estado === 'COMPLETADO'" style="margin-top: 5px;">
                    <span class="badge-reembolso-completado">
                      <i class="bi bi-check-circle me-1"></i>
                      Reembolsado
                    </span>
                  </div>
                </div>
                
                <div v-if="turno.estado !== 'CANCELADO' && esTurnoPorCanje(turno)" style="margin-top: 5px;">
                  <span class="badge-tipo-canje">
                    <i class="bi bi-arrow-repeat me-1"></i>
                    Turno por Canje
                  </span>
                </div>
              </td>
              <td>
                <div class="pago-info">
                  <div class="medio-pago-wrapper">
                    <span class="medio-pago-badge" :class="getMedioPagoClass(turno.medio_pago)">
                      {{ getMedioPagoTexto(turno.medio_pago) }}
                    </span>
                    
                    <span v-if="esTurnoPorCanje(turno) && turno.nro_transaccion" 
                          class="badge-clonado">
                      <i class="bi bi-link-45deg me-1"></i>
                      ID Clonado
                    </span>
                  </div>
                  
                  <div v-if="turno.tipo_pago === 'SENA_50'" class="detalle-pago">
                    <div class="text-senia">Seña: ${{ formatPrecio(turno.monto_seña) }}</div>
                    <div class="text-falta">Falta: ${{ formatPrecio(calcularFaltaPagar(turno)) }}</div>
                  </div>
                  <div v-else-if="turno.tipo_pago === 'TOTAL'" class="detalle-pago">
                    <span class="text-pagado">Pagado total: ${{ formatPrecio(turno.monto_total) }}</span>
                  </div>
                  
                  <div v-if="(turno.info_descuento) || (turno.descuento_aplicado && turno.descuento_aplicado > 0)" class="descuento-info">
                    <span class="badge-descuento-fidelizacion">
                      <i class="bi bi-percent me-1"></i>
                      15% OFF aplicado
                    </span>
                  </div>
                  
                  <div v-if="turno.codigo_transaccion || turno.mp_payment_id || turno.nro_transaccion" 
                       class="transaccion-info-mejorado">
                    <div class="transaccion-header">
                      <i class="bi bi-credit-card"></i>
                      <span>COMPROBANTE</span>
                    </div>
                    <div class="transaccion-codigo">
                      {{ turno.codigo_transaccion || turno.mp_payment_id || turno.nro_transaccion }}
                    </div>
                  </div>

                  <div v-if="turno.entidad_pago" class="entidad-pago-info-mejorado">
                    <div class="entidad-header">
                      <i class="bi bi-building"></i>
                      <span>ENTIDAD</span>
                    </div>
                    <div class="entidad-nombre">
                      {{ getEntidadPagoTexto(turno.entidad_pago) }}
                    </div>
                  </div>

                  <div v-if="esTurnoConDescuento(turno)" class="descuento-info">
                    <span class="badge-descuento">
                      <i class="bi bi-percent me-1"></i>
                      15% OFF aplicado
                    </span>
                  </div>

                  <div v-if="esTurnoPorCanje(turno) && extraerSaldoAFavor(turno) > 0" class="saldo-favor-info">
                    <span class="badge-saldo-favor">
                      <i class="bi bi-wallet2 me-1"></i>
                      Saldo a favor: ${{ formatPrecio(extraerSaldoAFavor(turno)) }}
                    </span>
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button v-if="puedeEditarTurno(turno)" 
                          @click="editarTurno(turno)" 
                          class="action-button edit" 
                          title="Editar Turno">
                    <Edit :size="14"/>
                  </button>
                  
                  <button @click="verDetalleTurno(turno)" class="action-button view" title="Ver Detalle">
                    <Eye :size="14"/>
                  </button>
                  
                  <button v-if="turno.estado === 'CANCELADO' && turno.reembolso_estado === 'PENDIENTE'" 
                          @click="gestionarReembolsoManual(turno)" 
                          class="action-button reembolso" 
                          title="Marcar como Dinero Devuelto">
                    <ArrowRightLeft :size="14"/>
                  </button>
                  
                  <button v-if="esEstadoActivo(turno.estado) && turno.tipo_pago === 'SENA_50'" 
                          @click="confirmarPagoTotal(turno)" 
                          class="action-button pagar" 
                          title="Cobrar Restante">
                    <CreditCard :size="14"/>
                  </button>
                  
                  <button v-if="mostrarBotonCompletar(turno)" 
                          @click="completarTurno(turno)" 
                          class="action-button complete" 
                          title="Finalizar Atención">
                    <Check :size="14"/>
                  </button>
                  
                  <button v-if="puedeCancelarTurno(turno)" 
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
          <div class="no-results-icon">
            <Eye :size="48" />
          </div>
          <p>No se encontraron turnos</p>
          <button @click="limpiarFiltros" class="btn-reintentar">
            <Plus :size="16" /> Limpiar filtros
          </button>
        </div>
      </div>

      <div v-if="totalPaginas > 1" class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">
          <ArrowLeft :size="14"/> Anterior
        </button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">
          Siguiente <ArrowRight :size="14"/>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../../utils/axiosConfig'
import { 
  Plus, Trash2, Eye, CreditCard, ArrowRightLeft, Check, 
  ArrowLeft, ArrowRight, Edit
} from 'lucide-vue-next'
import Swal from 'sweetalert2'

const router = useRouter()
const turnos = ref([])
const pagina = ref(1)
const itemsPorPagina = 7
const loading = ref(false)
const filtros = ref({ 
  busqueda: '', 
  peluquero: '', 
  estado: '', 
  canal: '', 
  fechaDesde: '', 
  fechaHasta: '' 
})

// Obtener rol del usuario desde localStorage
const userRol = computed(() => {
  return localStorage.getItem('user_rol') || ''
})

// NAVEGACIÓN
const irARegistrar = () => {
  router.push('/turnos/crear-presencial')
}

// 🔥 FUNCIÓN: Editar turno
const editarTurno = (turno) => {
  // Navegar a la página de edición del turno
  router.push(`/turnos/modificar/${turno.id}`)
}

// 🔥 FUNCIÓN: Verificar si se puede editar el turno
const puedeEditarTurno = (turno) => {
  // Solo se puede editar turnos en estado RESERVADO o CONFIRMADO
  if (!['RESERVADO', 'CONFIRMADO'].includes(turno.estado)) {
    return false
  }
  
  // Verificar permisos del usuario
  const rol = userRol.value.toUpperCase()
  const rolesPermitidos = ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'PELUQUERO', 'PEL']
  
  return rolesPermitidos.includes(rol)
}

// FUNCIONES DE FORMATO
const formatFecha = (fechaStr) => {
  if (!fechaStr) return '-'
  const [year, month, day] = fechaStr.split('-')
  return `${day}/${month}/${year}`
}

const formatHora = (horaStr) => {
  if (!horaStr) return '-'
  return horaStr.slice(0, 5)
}

// FORMATO DE PRECIO CORREGIDO: 2 decimales siempre
const formatPrecio = (precio) => {
  if (!precio && precio !== 0) return '0.00'
  const numero = parseFloat(precio)
  if (isNaN(numero)) return '0.00'
  return numero.toLocaleString('es-AR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// FUNCIÓN: Formatear texto de entidad de pago
const getEntidadPagoTexto = (entidad) => {
  if (!entidad) return ''
  
  const mapaEntidades = {
    'MERCADO_PAGO': 'Mercado Pago',
    'MERCADOPAGO': 'Mercado Pago',
    'UALA': 'Ualá',
    'CUENTADNI': 'Cuenta DNI',
    'BRUBANK': 'Brubank',
    'LEMON': 'Lemon Cash',
    'NARANJAX': 'Naranja X',
    'MODO': 'MODO',
    'SANTANDER': 'Santander Río',
    'GALICIA': 'Galicia',
    'BBVA': 'BBVA',
    'MACRO': 'Macro',
    'OTRO': 'Otro'
  }
  
  return mapaEntidades[entidad] || entidad
}

// FUNCIONES DE CÁLCULO
const calcularFaltaPagar = (turno) => {
  const total = parseFloat(turno.monto_total) || 0
  const senia = parseFloat(turno.monto_seña) || 0
  return total - senia
}

// Lógica de reembolso SOLO para cancelados con PENDIENTE
const calcularMontoReembolso = (turno) => {
  if (turno.estado !== 'CANCELADO' || turno.reembolso_estado !== 'PENDIENTE') {
    return 0
  }
  
  if (turno.tipo_pago === 'SENA_50') {
    return turno.monto_seña || 0
  }
  return turno.monto_total || 0
}

// DETECTAR SI EL TURNO ES POR CANJE
const esTurnoPorCanje = (turno) => {
  return turno.obs_cancelacion && 
         (turno.obs_cancelacion.includes('Canjeado') || 
          turno.obs_cancelacion.includes('Reoferta') ||
          turno.obs_cancelacion.includes('Origen: Turno Viejo'))
}

// DETECTAR SI EL TURNO TIENE DESCUENTO DE CANJE
const esTurnoConDescuento = (turno) => {
  return turno.obs_cancelacion && 
         (turno.obs_cancelacion.includes('15%') || 
          turno.obs_cancelacion.includes('Descuento'))
}

// EXTRAER SALDO A FAVOR DE LA OBSERVACIÓN (Canje)
const extraerSaldoAFavor = (turno) => {
  if (!turno.obs_cancelacion) return 0
  
  const obs = turno.obs_cancelacion.toLowerCase()
  const patron1 = /saldo\s*favor[:\s]*\$?\s*([\d,\.]+)/i
  const patron2 = /saldo\s*a\s*favor[:\s]*\$?\s*([\d,\.]+)/i
  
  let match = obs.match(patron1) || obs.match(patron2)
  
  if (match && match[1]) {
    const monto = parseFloat(match[1].replace(',', '.'))
    return isNaN(monto) ? 0 : monto
  }
  
  return 0
}

const getDuracion = (turno) => {
  if (turno.duracion_total) {
    return `${turno.duracion_total} min`
  }
  
  if (turno.servicios && turno.servicios.length > 0) {
    const duracion = turno.servicios.reduce((total, servicio) => {
      return total + (servicio.duracion || 0)
    }, 0)
    return `${duracion} min`
  }
  
  return '30 min'
}

// FUNCIONES DE ESTADO Y CLASES
const esEstadoActivo = (estado) => {
  return ['RESERVADO', 'CONFIRMADO'].includes(estado)
}

const getEstadoTexto = (estado, tipoPago) => {
  if (estado === 'RESERVADO') return 'Reservado'
  if (estado === 'CONFIRMADO') return 'Confirmado'
  return estado
}

const getEstadoClass = (estado, tipoPago) => {
  if (estado === 'RESERVADO' || estado === 'CONFIRMADO') {
    return tipoPago === 'TOTAL' ? 'estado-success' : 'estado-warning'
  } else if (estado === 'COMPLETADO') {
    return 'estado-completado'
  } else if (estado === 'CANCELADO') {
    return 'estado-cancelado'
  }
  return 'estado-secondary'
}

const getMedioPagoClass = (medioPago) => {
  if (!medioPago) return 'otro'
  const medio = medioPago.toLowerCase()
  if (medio.includes('mercado')) return 'mp'
  if (medio.includes('efectivo')) return 'efectivo'
  if (medio.includes('tarjeta')) return 'tarjeta'
  if (medio.includes('transferencia')) return 'transferencia'
  if (medio.includes('pendiente')) return 'pendiente'
  return 'otro'
}

const getMedioPagoTexto = (medioPago) => {
  if (!medioPago || medioPago === 'PENDIENTE') return 'Pendiente'
  const map = {
    'MERCADO_PAGO': 'Mercado Pago',
    'EFECTIVO': 'Efectivo',
    'TRANSFERENCIA': 'Transferencia',
    'TARJETA': 'Tarjeta'
  }
  return map[medioPago] || medioPago
}

// CARGA DE TURNOS CON FILTRO PARA INCLUIR CANCELADOS Y DEBUG
const cargarTurnos = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    
    if (filtros.value.busqueda) params.append('q', filtros.value.busqueda)
    if (filtros.value.estado) params.append('estado', filtros.value.estado)
    if (filtros.value.canal) params.append('canal', filtros.value.canal)
    if (filtros.value.fechaDesde) params.append('fecha_desde', filtros.value.fechaDesde)
    if (filtros.value.fechaHasta) params.append('fecha_hasta', filtros.value.fechaHasta)
    if (filtros.value.peluquero) params.append('peluquero_id', filtros.value.peluquero)
    
    params.append('incluir_cancelados', 'true')
    
    console.log('🔍 Cargando turnos con parámetros:', params.toString())
    
    const response = await axios.get(`/api/turnos/?${params.toString()}`)
    turnos.value = response.data || []
    
    if (turnos.value.length > 0) {
      console.log('✅ Primer turno recibido para debug:', {
        id: turnos.value[0].id,
        medio_pago: turnos.value[0].medio_pago,
        codigo_transaccion: turnos.value[0].codigo_transaccion,
        entidad_pago: turnos.value[0].entidad_pago,
        mp_payment_id: turnos.value[0].mp_payment_id,
        nro_transaccion: turnos.value[0].nro_transaccion
      })
    }
    
    turnos.value.sort((a, b) => {
      const dateA = new Date(`${a.fecha}T${a.hora}`)
      const dateB = new Date(`${b.fecha}T${b.hora}`)
      return dateB - dateA
    })
    
  } catch (error) {
    console.error('❌ Error cargando turnos:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudieron cargar los turnos. Por favor, intenta nuevamente.'
    })
  } finally {
    loading.value = false
  }
}

// CANCELACIÓN DE TURNO
const cancelarTurno = async (turno) => {
  try {
    let margenReembolso = 3; 
    try {
        const resConfig = await axios.get('/api/configuracion/');
        if (resConfig.data && resConfig.data.margen_horas_cancelacion) {
            margenReembolso = resConfig.data.margen_horas_cancelacion;
        }
    } catch (e) {
        console.error("Error obteniendo margen dinámico, usando 3 por defecto:", e);
    }

    const ahora = new Date()
    const fechaTurno = new Date(`${turno.fecha}T${turno.hora}`)
    const horasFaltantes = (fechaTurno - ahora) / (1000 * 60 * 60)
    
    const hayReembolso = horasFaltantes >= margenReembolso
    
    let mensajeReembolso = ''
    let iconoReembolso = ''
    
    if (hayReembolso) {
      mensajeReembolso = `El cliente recibirá reembolso (cancelación con más de ${margenReembolso} horas de anticipación).`
      iconoReembolso = 'success'
    } else {
      mensajeReembolso = `No habrá reembolso (faltan menos de ${margenReembolso} horas para el turno).`
      iconoReembolso = 'warning'
    }

    const { value: formValues } = await Swal.fire({
      title: `<div style="text-align: center; margin-bottom: 10px;">
                <span style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">Cancelar Turno</span>
              </div>`,
      html: `
        <div style="text-align: left; max-width: 520px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
          
          <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); border: 1px solid #e5e7eb;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 4px;">
                  ${turno.cliente_nombre} ${turno.cliente_apellido}
                </div>
                <div style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #6b7280;">
                  <span style="display: inline-flex; align-items: center; gap: 4px;">
                    <i class="bi bi-calendar3" style="font-size: 0.9rem;"></i>
                    ${formatFecha(turno.fecha)}
                  </span>
                  <span style="display: inline-flex; align-items: center; gap: 4px;">
                    <i class="bi bi-clock" style="font-size: 0.9rem;"></i>
                    ${formatHora(turno.hora)}hs
                  </span>
                </div>
              </div>
              <div style="font-size: 1.3rem; font-weight: 800; color: #0f172a; background: linear-gradient(135deg, #f8fafc, #e2e8f0); padding: 8px 12px; border-radius: 8px;">
                $${formatPrecio(turno.monto_total)}
              </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.9rem; color: #4b5563; background: #f9fafb; padding: 8px 12px; border-radius: 6px; margin-top: 8px;">
              <i class="bi bi-person-badge" style="color: #6366f1;"></i>
              <span>${turno.peluquero_nombre || 'Peluquero no asignado'}</span>
            </div>
          </div>

          <div style="background: ${hayReembolso ? '#f0fdf4' : '#fffbeb'}; 
                      padding: 16px; border-radius: 10px; margin-bottom: 24px; 
                      border-left: 4px solid ${hayReembolso ? '#10b981' : '#f59e0b'};">
            <div style="display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px;">
              <div style="background: ${hayReembolso ? '#d1fae5' : '#fef3c7'}; 
                          width: 32px; height: 32px; border-radius: 50%; 
                          display: flex; align-items: center; justify-content: center; 
                          flex-shrink: 0;">
                <i class="bi bi-${hayReembolso ? 'check-circle' : 'exclamation-triangle'}" 
                   style="color: ${hayReembolso ? '#059669' : '#d97706'}; font-size: 1rem;"></i>
              </div>
              <div style="flex: 1;">
                <div style="font-weight: 700; color: ${hayReembolso ? '#065f46' : '#92400e'}; margin-bottom: 6px; font-size: 1rem;">
                  ${hayReembolso ? '✅ Reembolso aplicable' : '⚠️ Sin reembolso'}
                </div>
                <div style="color: ${hayReembolso ? '#047857' : '#b45309'}; font-size: 0.9rem; line-height: 1.4;">
                  ${mensajeReembolso}
                </div>
                ${turno.monto_seña > 0 ? `
                  <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid ${hayReembolso ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                      <span style="font-weight: 600; color: ${hayReembolso ? '#065f46' : '#92400e'};">Monto a devolver:</span>
                      <span style="font-weight: 800; color: ${hayReembolso ? '#059669' : '#d97706'}; font-size: 1.1rem;">
                        $${formatPrecio(hayReembolso ? turno.monto_seña : 0)}
                      </span>
                    </div>
                  </div>
                ` : ''}
              </div>
            </div>
          </div>

          <div style="margin-bottom: 24px;">
            <div style="margin-bottom: 16px;">
              <label for="motivoCancelacion" style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 0.95rem;">
                <i class="bi bi-flag" style="margin-right: 6px; color: #6366f1;"></i>
                Motivo de cancelación *
              </label>
              <select id="motivoCancelacion" 
                      style="width: 100%; padding: 12px 14px; border-radius: 8px; border: 2px solid #d1d5db; 
                             background: white; color: #111827; font-size: 0.95rem; outline: none; cursor: pointer;">
                <option value="" disabled selected>Selecciona un motivo...</option>
                <option value="MOTIVOS_PERSONALES">Motivos personales</option>
                <option value="PROBLEMAS_SALUD">Problemas de salud</option>
                <option value="ERROR_RESERVA">Error al reservar</option>
                <option value="CAMBIO_PLANES">Cambio de planes</option>
                <option value="NO_PRESENTO">No se presentó</option>
                <option value="EMERGENCIA">Emergencia familiar</option>
                <option value="CANJE_AUTOMATICO">Canje Automático</option>
                <option value="OTRO">Otro motivo</option>
              </select>
            </div>

            <div>
              <label for="observacionesCancelacion" style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 0.95rem;">
                <i class="bi bi-chat-left-text" style="margin-right: 6px; color: #6366f1;"></i>
                Observaciones adicionales (Opcional)
              </label>
              <textarea id="observacionesCancelacion" rows="3" style="width: 100%; padding: 12px 14px; border-radius: 8px; border: 2px solid #d1d5db;"></textarea>
            </div>
          </div>

          <div style="background: #eff6ff; padding: 14px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #dbeafe;">
            <div style="display: flex; align-items: flex-start; gap: 10px;">
              <div style="background: #3b82f6; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <i class="bi bi-info-lg" style="color: white; font-size: 0.9rem;"></i>
              </div>
              <div>
                <div style="font-weight: 600; color: #1e40af; margin-bottom: 4px; font-size: 0.95rem;">Proceso automático</div>
                <div style="color: #3b82f6; font-size: 0.85rem; line-height: 1.4;">
                  El sistema evaluará si hay clientes en lista de espera y les ofrecerá el turno con 15% de descuento.
                </div>
              </div>
            </div>
          </div>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: 'Confirmar cancelación',
      cancelButtonText: 'Volver atrás',
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#f3f4f6',
      preConfirm: () => {
        const motivoSelect = document.getElementById('motivoCancelacion')
        const observacionesTextarea = document.getElementById('observacionesCancelacion')
        
        if (!motivoSelect.value) {
          Swal.showValidationMessage('Por favor, selecciona un motivo de cancelación')
          return false
        }
        
        const motivoTexto = motivoSelect.options[motivoSelect.selectedIndex].text
        
        return {
          motivo_cancelacion: motivoTexto,
          motivo_cancelacion_codigo: motivoSelect.value,
          obs_cancelacion: observacionesTextarea.value.trim() || ''
        }
      }
    })

    if (formValues) {
      loading.value = true
      
      Swal.fire({
        title: 'Procesando cancelación',
        text: 'Evaluando reembolso y actualizando sistema...',
        showConfirmButton: false,
        allowOutsideClick: false
      })

      try {
        const response = await axios.post(`/api/turnos/${turno.id}/cancelar/`, formValues)
        Swal.close()

        if (response.data.status === 'ok') {
          await Swal.fire({
            icon: iconoReembolso,
            title: 'Turno cancelado',
            text: response.data.message,
            confirmButtonColor: '#10b981'
          })
        } else {
          await Swal.fire('Error', response.data.error || 'Error desconocido', 'error')
        }
        await cargarTurnos()
      } catch (error) {
        console.error('Error cancelando turno:', error)
        Swal.fire('Error', 'Error de conexión', 'error')
      } finally {
        loading.value = false
      }
    }
  } catch (error) {
    console.error('Error en cancelarTurno:', error)
    loading.value = false
  }
}

// PAGO TOTAL
const confirmarPagoTotal = async (turno) => {
  const falta = calcularFaltaPagar(turno)
  
  const { value: nroTransaccion } = await Swal.fire({
    title: 'Cobrar Restante',
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Falta cobrar:</strong> <span style="color: #f59e0b; font-weight: bold;">$${formatPrecio(falta)}</span></p>
        <br>
        <label for="nro_transaccion">N° transacción (opcional):</label>
        <input id="nro_transaccion" class="swal2-input" placeholder="Ej: MP-123456789">
      </div>
    `,
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Registrar Pago',
    preConfirm: () => document.getElementById('nro_transaccion').value || ''
  })

  if (nroTransaccion !== undefined) {
    try {
      await axios.post(`/api/turnos/${turno.id}/actualizar-pago/`, {
        tipo_pago: 'TOTAL',
        medio_pago: turno.medio_pago || 'EFECTIVO',
        nro_transaccion: nroTransaccion || ''
      })
      await cargarTurnos()
      Swal.fire('¡Pago registrado!', '', 'success')
    } catch (error) {
      Swal.fire('Error', 'No se pudo registrar el pago.', 'error')
    }
  }
}

// REEMBOLSO MANUAL
const gestionarReembolsoManual = async (turno) => {
  const monto = calcularMontoReembolso(turno)
  
  const { isConfirmed } = await Swal.fire({
    title: 'Confirmar devolución',
    html: `Devolver <span style="color:#f59e0b; font-weight:bold;">$${formatPrecio(monto)}</span> a ${turno.cliente_nombre}`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#f59e0b',
    confirmButtonText: 'Sí, devuelto'
  })

  if (isConfirmed) {
    try {
      await axios.post(`/api/turnos/${turno.id}/completar-reembolso-manual/`)
      await cargarTurnos()
      Swal.fire('¡Reembolso completado!', '', 'success')
    } catch (error) {
      Swal.fire('Error', 'No se pudo completar el reembolso.', 'error')
    }
  }
}

// VER DETALLE
const verDetalleTurno = async (turno) => {
  console.log('=== DEBUG TURNO DETALLE ===');
  console.log('ID:', turno.id);
  console.log('Canal:', turno.canal);
  console.log('codigo_transaccion:', turno.codigo_transaccion);
  console.log('entidad_pago:', turno.entidad_pago);
  console.log('mp_payment_id:', turno.mp_payment_id);
  console.log('nro_transaccion:', turno.nro_transaccion);
  console.log('==========================');
  
  const duracionTotal = turno.duracion_total || 30
  
  let serviciosHTML = ''
  let totalServicios = 0
  
  if (turno.servicios && turno.servicios.length > 0) {
    serviciosHTML = turno.servicios.map(s => {
      totalServicios += parseFloat(s.precio || 0)
      return `<tr><td>${s.nombre}</td><td align="right">${s.duracion}m</td><td align="right">$${formatPrecio(s.precio)}</td></tr>`
    }).join('')
  }
  
  const esCanje = esTurnoPorCanje(turno)
  const tieneDescuento = esTurnoConDescuento(turno)
  
  let montoSaldoAFavor = 0
  let esSaldoAFavor = false
  
  if (esCanje) {
    montoSaldoAFavor = extraerSaldoAFavor(turno)
    esSaldoAFavor = montoSaldoAFavor > 0
  } else {
    const faltaPagar = calcularFaltaPagar(turno)
    esSaldoAFavor = faltaPagar < 0
    montoSaldoAFavor = Math.abs(faltaPagar)
  }
  
  const faltaPagar = calcularFaltaPagar(turno)
  
  let pagoInfoHTML = ''
  
  if (esSaldoAFavor && esCanje) {
    pagoInfoHTML = `
      <div style="background: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 2px solid #10b981; border-left: 5px solid #059669;">
        <div style="font-size: 0.85rem; color: #065f46; margin-bottom: 6px; font-weight: 700; display: flex; align-items: center; gap: 8px;">
          <i class="bi bi-cash-coin" style="font-size: 1rem;"></i>
          SALDO A DEVOLVER AL CLIENTE
        </div>
        <div style="font-size: 1.6rem; font-weight: 900; color: #059669; margin: 10px 0;">
          $${formatPrecio(montoSaldoAFavor)}
        </div>
        <div style="font-size: 0.75rem; color: #0ea5e9; margin-top: 8px; padding: 6px 10px; background: #f0f9ff; border-radius: 6px; border-left: 3px solid #0ea5e9;">
          <i class="bi bi-info-circle" style="margin-right: 5px;"></i>
          Saldo generado por canje automático
        </div>
      </div>
    `
  } else if (esSaldoAFavor) {
    pagoInfoHTML = `
      <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 2px solid #10b981;">
        <div style="font-size: 0.8rem; color: #059669; margin-bottom: 4px; font-weight: bold;">
          <i class="bi bi-wallet2"></i> SALDO A FAVOR
        </div>
        <div style="font-size: 1.4rem; font-weight: 900; color: #059669;">
          $${formatPrecio(montoSaldoAFavor)}
        </div>
      </div>
    `
  } else {
    pagoInfoHTML = `
      <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 4px;">
          ${faltaPagar > 0 ? 'Falta pagar' : 'Pagado completo'}
        </div>
        <div style="font-size: 1.2rem; font-weight: 900; color: ${faltaPagar > 0 ? '#f59e0b' : '#10b981'};">$${formatPrecio(Math.abs(faltaPagar))}</div>
      </div>
    `
  }

  let transaccionInfoHTML = ''
  
  if (turno.codigo_transaccion) {
    transaccionInfoHTML = `<div><strong><i class="bi bi-credit-card"></i> Cód. Transacción:</strong> ${turno.codigo_transaccion}</div>`
  } else if (turno.mp_payment_id) {
    transaccionInfoHTML = `<div><strong><i class="bi bi-cash"></i> MP Payment ID:</strong> ${turno.mp_payment_id}</div>`
  } else if (turno.nro_transaccion) {
    transaccionInfoHTML = `<div><strong><i class="bi bi-fingerprint"></i> ID Transacción:</strong> ${turno.nro_transaccion}</div>`
  }

  Swal.fire({
    title: `<div style="display: flex; align-items: center; gap: 12px; color: #0ea5e9;">
              <i class="bi bi-calendar2-week" style="font-size: 1.5rem;"></i>
              <span>Turno #${turno.id}</span>
            </div>`,
    html: `
      <div style="text-align: left; max-width: 700px; font-family: 'Segoe UI', sans-serif;">
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e2e8f0;">
          <div>
            <span class="badge-estado ${getEstadoClass(turno.estado, turno.tipo_pago)}">
              ${getEstadoTexto(turno.estado, turno.tipo_pago)}
            </span>
            <span class="canal-badge ${(turno.canal || 'PRESENCIAL').toLowerCase()}" style="margin-left: 8px;">
              ${turno.canal || 'PRESENCIAL'}
            </span>
            ${esCanje ? `
              <span style="margin-left: 8px; background: #fef3c7; color: #d97706; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                <i class="bi bi-arrow-repeat"></i> CANJE
              </span>
            ` : ''}
          </div>
          <div style="font-size: 1.2rem; font-weight: 900; color: #0f172a;">
            $${formatPrecio(turno.monto_total)}
            ${tieneDescuento ? '<span style="font-size: 0.8rem; color: #0ea5e9; margin-left: 5px;">(15% OFF)</span>' : ''}
          </div>
        </div>
        
        ${esCanje ? `
          <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); padding: 15px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #f59e0b;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
              <i class="bi bi-info-circle-fill" style="color: #d97706; font-size: 1.2rem;"></i>
              <strong style="color: #92400e;">Información de Canje</strong>
            </div>
            <div style="color: #92400e; font-size: 0.9rem; line-height: 1.4;">
              ${turno.obs_cancelacion || 'Turno generado por sistema de canje automático.'}
            </div>
          </div>
        ` : ''}
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
          <div style="background: #f8fafc; padding: 15px; border-radius: 10px;">
            <h4 style="color: #0ea5e9; margin-bottom: 10px;"><i class="bi bi-person"></i> Cliente</h4>
            <p><strong>${turno.cliente_nombre} ${turno.cliente_apellido}</strong></p>
          </div>
          <div style="background: #f8fafc; padding: 15px; border-radius: 10px;">
            <h4 style="color: #10b981; margin-bottom: 10px;"><i class="bi bi-scissors"></i> Peluquero</h4>
            <p><strong>${turno.peluquero_nombre || 'No asignado'}</strong></p>
          </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #0ea5e9;">
          <h4 style="color: #0369a1; margin-bottom: 15px;"><i class="bi bi-cash-stack"></i> Información de Pago</h4>
          
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; text-align: center;">
            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
              <div style="font-size: 0.8rem; color: #64748b;">Total</div>
              <div style="font-size: 1.2rem; font-weight: 900;">$${formatPrecio(turno.monto_total)}</div>
            </div>
            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
              <div style="font-size: 0.8rem; color: #64748b;">Pagado/Seña</div>
              <div style="font-size: 1.2rem; font-weight: 900; color: #10b981;">$${formatPrecio(turno.monto_seña)}</div>
            </div>
            ${pagoInfoHTML}
          </div>
          
          <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-size: 0.9rem;">
            <div><strong><i class="bi bi-credit-card"></i> Medio:</strong> ${getMedioPagoTexto(turno.medio_pago)}</div>
            ${turno.entidad_pago ? `<div><strong><i class="bi bi-building"></i> Entidad:</strong> ${getEntidadPagoTexto(turno.entidad_pago)}</div>` : ''}
            ${transaccionInfoHTML}
            ${turno.estado === 'CANCELADO' && turno.reembolso_estado === 'NO_APLICA' ? `
              <div style="margin-top: 8px;">
                <span style="background: #f3f4f6; color: #6b7280; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                  <i class="bi bi-arrow-left-right"></i> Reembolso: No aplica (Canje)
                </span>
              </div>
            ` : ''}
          </div>
        </div>

        ${serviciosHTML ? `
          <div style="background: #f8fafc; padding: 20px; border-radius: 12px;">
            <h4 style="color: #7c3aed; margin-bottom: 10px;">Servicios</h4>
            <table style="width: 100%; border-collapse: collapse;">
              ${serviciosHTML}
            </table>
          </div>
        ` : ''}
      </div>
    `,
    showCloseButton: true,
    showConfirmButton: false,
    width: '750px'
  })
}

// COMPLETAR TURNO
const completarTurno = async (turno) => {
  const { isConfirmed } = await Swal.fire({
    title: '¿Completar turno?',
    text: 'Marcar como completado.',
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Sí, completar'
  })

  if (isConfirmed) {
    try {
      await axios.post(`/api/turnos/${turno.id}/cambiar-estado/COMPLETADO/`)
      await cargarTurnos()
      Swal.fire('¡Turno completado!', '', 'success')
    } catch (error) {
      Swal.fire('Error', 'No se pudo completar el turno.', 'error')
    }
  }
}

// FILTROS Y PAGINACIÓN
const limpiarFiltros = () => {
  filtros.value = { busqueda: '', peluquero: '', estado: '', canal: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1
  cargarTurnos()
}

const turnosFiltrados = computed(() => {
  let filtrados = turnos.value
  if (filtros.value.busqueda) {
    const busqueda = filtros.value.busqueda.toLowerCase()
    filtrados = filtrados.filter(turno => 
      `${turno.cliente_nombre} ${turno.cliente_apellido}`.toLowerCase().includes(busqueda) ||
      `${turno.peluquero_nombre} ${turno.peluquero_apellido}`.toLowerCase().includes(busqueda)
    )
  }
  if (filtros.value.estado) filtrados = filtrados.filter(turno => turno.estado === filtros.value.estado)
  if (filtros.value.canal) filtrados = filtrados.filter(turno => turno.canal === filtros.value.canal)
  if (filtros.value.fechaDesde) filtrados = filtrados.filter(turno => turno.fecha >= filtros.value.fechaDesde)
  if (filtros.value.fechaHasta) filtrados = filtrados.filter(turno => turno.fecha <= filtros.value.fechaHasta)
  return filtrados
})

const totalPaginas = computed(() => Math.ceil(turnosFiltrados.value.length / itemsPorPagina))
const turnosFiltradosPaginados = computed(() => {
  const start = (pagina.value - 1) * itemsPorPagina
  return turnosFiltrados.value.slice(start, start + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// PERMISOS
const mostrarBotonCompletar = (turno) => {
  if (['COMPLETADO', 'CANCELADO'].includes(turno.estado)) return false
  const rol = userRol.value.toUpperCase()
  return ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'PELUQUERO', 'PEL'].includes(rol)
}

const puedeCancelarTurno = (turno) => {
  if (['COMPLETADO', 'CANCELADO'].includes(turno.estado)) return false
  const rol = userRol.value.toUpperCase()
  return ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'PELUQUERO', 'PEL'].includes(rol)
}

// CARGA INICIAL
onMounted(() => { cargarTurnos() })
watch(filtros, () => { pagina.value = 1 }, { deep: true })
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

.estado-success {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.estado-completado {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.estado-cancelado {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
  opacity: 0.8;
}

.estado-secondary {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  border: 2px solid var(--text-tertiary);
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* BADGE ROJO PARA MOTIVO DE CANCELACIÓN */
.badge-motivo-cancelacion {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 2px 6px rgba(220, 53, 69, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* BADGE GRIS PARA REEMBOLSO NO APLICABLE */
.badge-reembolso-no-aplica {
  display: inline-flex;
  align-items: center;
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #d1d5db;
}

.badge-fidelizacion {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.badge-descuento-fidelizacion {
    color: #ffffff; /* 🔥 Letra BLANCA */
    background-color: #198754; /* 🔥 Fondo Verde Fuerte (Bootstrap Success) */
    font-size: 0.75rem;
    padding: 2px 8px; /* Un poquito más de padding a los costados */
    border-radius: 4px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    margin-top: 4px;
    box-shadow: 0 2px 4px rgba(25, 135, 84, 0.2); /* Sombrita suave */
}

/* BADGE ORO PARA TIPO DE CANJE */
.badge-tipo-canje {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #f59e0b;
}

/* BADGE VERDE PARA DESCUENTO APLICADO */
.badge-descuento {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #065f46;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid #10b981;
  margin-top: 4px;
}

/* BADGE AZUL PARA TRAZABILIDAD CLONADA */
.badge-clonado {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid #3b82f6;
  margin-left: 6px;
}

/* BADGE NARANJA PARA REEMBOLSO PENDIENTE */
.badge-reembolso-pendiente {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 2px 6px rgba(245, 158, 11, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: pulse 2s infinite;
}

/* BADGE VERDE PARA REEMBOLSO COMPLETADO */
.badge-reembolso-completado {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* BADGE AZUL PARA SALDO A FAVOR */
.badge-saldo-favor {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
  color: #0369a1;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid #0ea5e9;
  margin-top: 4px;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* ESTILOS ESPECÍFICOS PARA TRANSACCIONES Y ENTIDADES */
.transaccion-info-mejorado {
  margin-top: 6px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-radius: 10px;
  padding: 8px;
  border: 1px solid #e2e8f0;
}

.transaccion-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.transaccion-header i {
  color: #3b82f6;
}

.transaccion-codigo {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  font-weight: 700;
  color: #1e293b;
  background: white;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entidad-pago-info-mejorado {
  margin-top: 6px;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-radius: 10px;
  padding: 8px;
  border: 1px solid #bbf7d0;
}

.entidad-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  color: #065f46;
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.entidad-header i {
  color: #10b981;
}

.entidad-nombre {
  font-size: 0.85rem;
  font-weight: 700;
  color: #064e3b;
  background: white;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #86efac;
}

/* Información de pago */
.pago-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detalle-pago {
  font-size: 0.75rem;
}

.text-senia {
  color: #10b981;
  font-weight: 600;
}

.text-falta {
  color: #f59e0b;
  font-weight: 700;
}

.text-pagado {
  color: #10b981;
  font-weight: 700;
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

/* HEADER */
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

/* TABLA */
.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
  min-height: 300px;
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

/* Badge de Fidelización (Violeta Fachero) */
.badge-fidelizacion {
    background-color: #6f42c1; /* Violeta Bootstrap */
    color: white;
    font-size: 0.75rem; /* Letra chiquita pero legible */
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(111, 66, 193, 0.2);
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    gap: 4px; /* Espacio entre ícono y texto */
    animation: fadeIn 0.5s ease-in;
}

/* Badge de Descuento (Verde Éxito) */
.badge-descuento-fidelizacion {
    color: #198754; /* Verde oscuro */
    background-color: #d1e7dd; /* Verde clarito fondo */
    font-size: 0.75rem;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    margin-top: 4px;
}

/* Animación suave para que aparezcan lindos */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Ajustes para la columna de pago */
.pago-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
}

.text-pagado {
    font-weight: 600;
    color: #0d6efd; /* Azul standard */
}

/* Información del cliente */
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

/* Badge para medio de pago */
.medio-pago-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.medio-pago-badge.mp {
  background: rgba(14, 165, 233, 0.12);
  color: #0ea5e9;
  border: 1px solid rgba(14, 165, 233, 0.25);
}

.medio-pago-badge.efectivo {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.medio-pago-badge.tarjeta {
  background: rgba(139, 92, 246, 0.12);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.25);
}

.medio-pago-badge.transferencia {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.medio-pago-badge.pendiente {
  background: rgba(156, 163, 175, 0.12);
  color: #6b7280;
  border: 1px solid rgba(156, 163, 175, 0.25);
}

.medio-pago-badge.otro {
  background: rgba(156, 163, 175, 0.12);
  color: #6b7280;
  border: 1px solid rgba(156, 163, 175, 0.25);
}

/* 🔥 BOTONES DE ACCIÓN CON LAPICITO INCLUIDO */
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

/* Botón Editar (lapicito) */
.action-button.edit {
  background: var(--bg-tertiary);
  border: 1px solid #0ea5e9;
  color: #0ea5e9;
}
.action-button.edit:hover { 
  background: var(--hover-bg); 
  transform: translateY(-2px); 
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4); 
  border-color: #0ea5e9; 
}

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

.action-button.reembolso {
  background: var(--bg-tertiary);
  border: 1px solid #f59e0b;
  color: #f59e0b;
}
.action-button.reembolso:hover { 
  background: var(--hover-bg); 
  transform: translateY(-2px); 
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4); 
  border-color: #f59e0b; 
}

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

/* ESTADOS DE CARGA */
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

/* PAGINACIÓN */
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
  .list-card { padding: 25px; border-radius: 20px; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .header-content h1 { font-size: 1.6rem; }
  .filters-grid { grid-template-columns: 1fr; }
  .users-table { font-size: 0.85rem; }
  .users-table th { font-size: 0.7rem; padding: 14px 10px; }
  .action-buttons { flex-direction: column; gap: 6px; }
  .pagination { flex-direction: column; gap: 12px; }
}

@media (max-width: 480px) {
  .list-card { padding: 18px; border-radius: 16px; }
  .header-content h1 { font-size: 1.4rem; }
  .users-table { display: block; overflow-x: auto; white-space: nowrap; }
  .filter-input, .filter-select { font-size: 0.9rem; }
  .badge-estado { font-size: 0.65rem; padding: 5px 10px; }
  .action-button { width: 36px; height: 36px; }
}
</style>