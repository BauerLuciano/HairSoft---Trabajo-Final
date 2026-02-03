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

      <!-- Filtros -->
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
                
                <!-- ✅ BADGE ROJO ELEGANTE PARA MOTIVO DE CANCELACIÓN -->
                <div v-if="turno.estado === 'CANCELADO' && turno.motivo_cancelacion" style="margin-top: 5px;">
                  <span class="badge-motivo-cancelacion">
                    <i class="bi bi-x-circle me-1"></i>
                    {{ turno.motivo_cancelacion }}
                  </span>
                </div>
                
                <!-- ✅ BADGE NARANJA PARA REEMBOLSO PENDIENTE (Efectivo/Transferencia) -->
                <div v-if="turno.reembolso_estado === 'PENDIENTE'" style="margin-top: 5px;">
                  <span class="badge-reembolso-pendiente">
                    <i class="bi bi-cash-coin me-1"></i>
                    DEVOLVER ${{ formatPrecio(calcularMontoReembolso(turno)) }}
                  </span>
                </div>
                
                <!-- ✅ BADGE VERDE PARA REEMBOLSO COMPLETADO -->
                <div v-if="turno.reembolso_estado === 'COMPLETADO'" style="margin-top: 5px;">
                  <span class="badge-reembolso-completado">
                    <i class="bi bi-check-circle me-1"></i>
                    Reembolsado
                  </span>
                </div>
              </td>
              <td>
                <!-- ✅ COLUMNA DE PAGO Y TRANSACCIÓN -->
                <div class="pago-info">
                  <div class="medio-pago-wrapper">
                    <span class="medio-pago-badge" :class="getMedioPagoClass(turno.medio_pago)">
                      {{ getMedioPagoTexto(turno.medio_pago) }}
                    </span>
                  </div>
                  
                  <div v-if="turno.tipo_pago === 'SENA_50'" class="detalle-pago">
                    <div class="text-senia">Seña: ${{ formatPrecio(turno.monto_seña) }}</div>
                    <div class="text-falta">Falta: ${{ formatPrecio(calcularFaltaPagar(turno)) }}</div>
                  </div>
                  <div v-else-if="turno.tipo_pago === 'TOTAL'" class="detalle-pago">
                    <span class="text-pagado">Pagado total</span>
                  </div>
                  
                  <!-- ✅ MOSTRAR ID DE TRANSACCIÓN (Transferencia, MercadoPago, etc.) -->
                  <div v-if="turno.nro_transaccion || turno.mp_payment_id" class="transaccion-info">
                    <small style="color: #6b7280; font-size: 0.7rem;">
                      <strong>ID Transacción:</strong><br>
                      {{ turno.nro_transaccion || turno.mp_payment_id }}
                    </small>
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <!-- Botón Ver Detalle -->
                  <button @click="verDetalleTurno(turno)" class="action-button view" title="Ver Detalle">
                    <Eye :size="14"/>
                  </button>
                  
                  <!-- ✅ Botón para marcar reembolso manual como completado -->
                  <button v-if="turno.reembolso_estado === 'PENDIENTE'" 
                          @click="gestionarReembolsoManual(turno)" 
                          class="action-button reembolso" 
                          title="Marcar como Dinero Devuelto">
                    <ArrowRightLeft :size="14"/>
                  </button>
                  
                  <!-- ✅ Botón para cobrar restante (de seña a total) -->
                  <button v-if="esEstadoActivo(turno.estado) && turno.tipo_pago === 'SENA_50'" 
                          @click="confirmarPagoTotal(turno)" 
                          class="action-button pagar" 
                          title="Cobrar Restante">
                    <CreditCard :size="14"/>
                  </button>
                  
                  <!-- ✅ Botón para completar turno -->
                  <button v-if="mostrarBotonCompletar(turno)" 
                          @click="completarTurno(turno)" 
                          class="action-button complete" 
                          title="Finalizar Atención">
                    <Check :size="14"/>
                  </button>
                  
                  <!-- ✅ Botón para cancelar turno (con el modal unificado) -->
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
        
        <!-- Mensaje cuando no hay resultados -->
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

      <!-- Paginación -->
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
  ArrowLeft, ArrowRight
} from 'lucide-vue-next'
import Swal from 'sweetalert2'

const router = useRouter()
const turnos = ref([])
const pagina = ref(1)
const itemsPorPagina = 10
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

// ✅ NAVEGACIÓN
const irARegistrar = () => {
  router.push('/turnos/crear-presencial')
}

// ✅ FUNCIONES DE FORMATO
const formatFecha = (fechaStr) => {
  if (!fechaStr) return '-'
  const [year, month, day] = fechaStr.split('-')
  return `${day}/${month}/${year}`
}

const formatHora = (horaStr) => {
  if (!horaStr) return '-'
  return horaStr.slice(0, 5)
}

const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  return parseFloat(precio).toFixed(2)
}

// ✅ FUNCIONES DE CÁLCULO
const calcularFaltaPagar = (turno) => {
  const total = parseFloat(turno.monto_total) || 0
  const senia = parseFloat(turno.monto_seña) || 0
  return total - senia
}

const calcularMontoReembolso = (turno) => {
  if (turno.tipo_pago === 'SENA_50') {
    return turno.monto_seña || 0
  }
  return turno.monto_total || 0
}

const getDuracion = (turno) => {
  if (turno.duracion_total) {
    return `${turno.duracion_total} min`
  }
  
  // Calcular duración sumando servicios
  if (turno.servicios && turno.servicios.length > 0) {
    const duracion = turno.servicios.reduce((total, servicio) => {
      return total + (servicio.duracion || 0)
    }, 0)
    return `${duracion} min`
  }
  
  return '30 min' // Default
}

// ✅ FUNCIONES DE ESTADO Y CLASES
const esEstadoActivo = (estado) => {
  return ['RESERVADO', 'CONFIRMADO'].includes(estado)
}

const getEstadoTexto = (estado, tipoPago) => {
  if (estado === 'RESERVADO') {
    return tipoPago === 'TOTAL' ? 'Pagado' : 'Señado'
  }
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

// ✅ CARGA DE TURNOS
const cargarTurnos = async () => {
  try {
    loading.value = true
    
    // Construir parámetros de filtro
    const params = new URLSearchParams()
    
    // Solo agregar filtros si tienen valor
    if (filtros.value.busqueda) params.append('q', filtros.value.busqueda)
    if (filtros.value.estado) params.append('estado', filtros.value.estado)
    if (filtros.value.canal) params.append('canal', filtros.value.canal)
    if (filtros.value.fechaDesde) params.append('fecha_desde', filtros.value.fechaDesde)
    if (filtros.value.fechaHasta) params.append('fecha_hasta', filtros.value.fechaHasta)
    if (filtros.value.peluquero) params.append('peluquero_id', filtros.value.peluquero)
    
    const response = await axios.get(`/api/turnos/?${params.toString()}`)
    
    // El endpoint devuelve un array directamente
    turnos.value = response.data || []
    
    // Ordenar por fecha y hora (más reciente primero)
    turnos.value.sort((a, b) => {
      const dateA = new Date(`${a.fecha}T${a.hora}`)
      const dateB = new Date(`${b.fecha}T${b.hora}`)
      return dateB - dateA
    })
    
  } catch (error) {
    console.error('Error cargando turnos:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudieron cargar los turnos. Por favor, intenta nuevamente.'
    })
  } finally {
    loading.value = false
  }
}

// ✅ CANCELACIÓN DE TURNO - MODERNIZADO Y ESTILIZADO
const cancelarTurno = async (turno) => {
  try {
    // ✅ PASO NUEVO: Traer el margen real de la base de datos antes de calcular nada
    // No borramos nada, solo hacemos que el margen deje de ser un 3 "de mentira"
    let margenReembolso = 3; 
    try {
        const resConfig = await axios.get('/api/configuracion/');
        if (resConfig.data && resConfig.data.margen_horas_cancelacion) {
            margenReembolso = resConfig.data.margen_horas_cancelacion;
        }
    } catch (e) {
        console.error("Error obteniendo margen dinámico, usando 3 por defecto:", e);
    }

    // 1. Calcular tiempo hasta el turno para determinar reembolso
    const ahora = new Date()
    const fechaTurno = new Date(`${turno.fecha}T${turno.hora}`)
    const horasFaltantes = (fechaTurno - ahora) / (1000 * 60 * 60)
    
    // ✅ Ahora 'hayReembolso' se calcula con el margen real (3, 4, o el que pongas)
    const hayReembolso = horasFaltantes >= margenReembolso
    
    // Determinar mensaje de reembolso
    let mensajeReembolso = ''
    let iconoReembolso = ''
    let colorReembolso = ''
    
    if (hayReembolso) {
      mensajeReembolso = `El cliente recibirá reembolso (cancelación con más de ${margenReembolso} horas de anticipación).`
      iconoReembolso = 'success'
      colorReembolso = '#10b981'
    } else {
      mensajeReembolso = `No habrá reembolso (faltan menos de ${margenReembolso} horas para el turno).`
      iconoReembolso = 'warning'
      colorReembolso = '#f59e0b'
    }

    // 2. Modal moderno y profesional (TODO TU HTML Y DISEÑO ESTÁ ACÁ INTACTO)
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
                             background: white; color: #111827; font-size: 0.95rem; transition: all 0.2s;
                             outline: none; cursor: pointer; appearance: none; background-image: url('data:image/svg+xml;charset=UTF-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path fill="none" stroke="%236b7280" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m2 5 6 6 6-6"/></svg>'); background-repeat: no-repeat; background-position: right 14px center; background-size: 14px;">
                <option value="" disabled selected style="color: #9ca3af;">Selecciona un motivo...</option>
                <option value="MOTIVOS_PERSONALES">Motivos personales</option>
                <option value="PROBLEMAS_SALUD">Problemas de salud</option>
                <option value="ERROR_RESERVA">Error al reservar</option>
                <option value="CAMBIO_PLANES">Cambio de planes</option>
                <option value="NO_PRESENTO">No se presentó</option>
                <option value="EMERGENCIA">Emergencia familiar</option>
                <option value="OTRO">Otro motivo</option>
              </select>
            </div>

            <div>
              <label for="observacionesCancelacion" style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 0.95rem;">
                <i class="bi bi-chat-left-text" style="margin-right: 6px; color: #6366f1;"></i>
                Observaciones adicionales
                <span style="font-weight: 400; color: #9ca3af; font-size: 0.85rem; margin-left: 4px;">(Opcional)</span>
              </label>
              <textarea id="observacionesCancelacion" 
                        placeholder="Detalles adicionales, notas internas, comentarios..."
                        rows="3"
                        style="width: 100%; padding: 12px 14px; border-radius: 8px; border: 2px solid #d1d5db; 
                               background: white; color: #111827; font-size: 0.95rem; resize: vertical;
                               outline: none; transition: all 0.2s; font-family: inherit;">
              </textarea>
            </div>
          </div>

          <div style="background: #eff6ff; padding: 14px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #dbeafe;">
            <div style="display: flex; align-items: flex-start; gap: 10px;">
              <div style="background: #3b82f6; width: 24px; height: 24px; border-radius: 50%; 
                          display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <i class="bi bi-info-lg" style="color: white; font-size: 0.9rem;"></i>
              </div>
              <div>
                <div style="font-weight: 600; color: #1e40af; margin-bottom: 4px; font-size: 0.95rem;">
                  Proceso automático de cancelación
                </div>
                <div style="color: #3b82f6; font-size: 0.85rem; line-height: 1.4;">
                  El sistema evaluará automáticamente si hay clientes en lista de espera para este horario y les ofrecerá el turno liberado.
                </div>
              </div>
            </div>
          </div>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: `<div style="display: flex; align-items: center; justify-content: center; gap: 8px; font-weight: 600;">
                            <i class="bi bi-x-circle-fill" style="font-size: 1rem;"></i>
                            Confirmar cancelación
                          </div>`,
      cancelButtonText: `<div style="display: flex; align-items: center; justify-content: center; gap: 8px; font-weight: 600; color: #6b7280;">
                           <i class="bi bi-arrow-left" style="font-size: 1rem;"></i>
                           Volver atrás
                         </div>`,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#f3f4f6',
      reverseButtons: true,
      focusConfirm: false,
      allowOutsideClick: false,
      allowEscapeKey: false,
      showCloseButton: true,
      closeButtonHtml: '<i class="bi bi-x-lg" style="font-size: 1.2rem;"></i>',
      customClass: {
        popup: 'swal2-popup-custom',
        title: 'swal2-title-custom',
        confirmButton: 'swal2-confirm-custom',
        cancelButton: 'swal2-cancel-custom',
        closeButton: 'swal2-close-custom'
      },
      didOpen: () => {
        const motivoSelect = document.getElementById('motivoCancelacion')
        const observacionesTextarea = document.getElementById('observacionesCancelacion')
        
        if (motivoSelect) {
          motivoSelect.addEventListener('focus', function() {
            this.style.borderColor = '#6366f1'
            this.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)'
          })
          motivoSelect.addEventListener('blur', function() {
            this.style.borderColor = '#d1d5db'
            this.style.boxShadow = 'none'
          })
        }
        
        if (observacionesTextarea) {
          observacionesTextarea.addEventListener('focus', function() {
            this.style.borderColor = '#6366f1'
            this.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)'
          })
          observacionesTextarea.addEventListener('blur', function() {
            this.style.borderColor = '#d1d5db'
            this.style.boxShadow = 'none'
          })
        }
      },
      preConfirm: () => {
        const motivoSelect = document.getElementById('motivoCancelacion')
        const observacionesTextarea = document.getElementById('observacionesCancelacion')
        
        if (!motivoSelect.value) {
          Swal.showValidationMessage(`
            <div style="display: flex; align-items: center; gap: 8px; color: #dc2626; font-size: 0.9rem;">
              <i class="bi bi-exclamation-triangle-fill"></i>
              Por favor, selecciona un motivo de cancelación
            </div>
          `)
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

    // 3. Procesamiento de la cancelación
    if (formValues) {
      loading.value = true
      
      Swal.fire({
        title: `<div style="display: flex; flex-direction: column; align-items: center; gap: 16px;">
                  <div class="spinner" style="width: 50px; height: 50px; border: 3px solid #f3f4f6; border-top-color: #ef4444; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                  <div style="text-align: center;">
                    <div style="font-weight: 600; color: #1f2937; font-size: 1.1rem; margin-bottom: 4px;">Procesando cancelación</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Evaluando reembolso y actualizando sistema...</div>
                  </div>
                </div>`,
        html: `<style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>`,
        showConfirmButton: false,
        allowOutsideClick: false,
        allowEscapeKey: false,
        showCloseButton: false
      })

      try {
        const response = await axios.post(`/api/turnos/${turno.id}/cancelar/`, formValues)
        Swal.close()

        if (response.data.status === 'ok') {
          await Swal.fire({
            icon: iconoReembolso,
            title: `<div style="display: flex; flex-direction: column; align-items: center; gap: 12px;">
                      <span style="font-size: 1.4rem; font-weight: 700; color: #1f2937;">Turno cancelado</span>
                    </div>`,
            html: `
              <div style="text-align: center; max-width: 400px; margin: 0 auto;">
                <div style="color: #4b5563; font-size: 0.95rem; margin-bottom: 20px; line-height: 1.5;">
                  ${response.data.message}
                </div>
                
                ${turno.medio_pago === 'EFECTIVO' && hayReembolso ? `
                  <div style="background: #fffbeb; border-radius: 10px; padding: 16px; margin-top: 16px; border: 1px solid #fcd34d;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                      <div style="background: #f59e0b; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <i class="bi bi-cash-coin" style="color: white; font-size: 1rem;"></i>
                      </div>
                      <div style="font-weight: 700; color: #92400e; text-align: left; flex: 1;">
                        Acción requerida
                      </div>
                    </div>
                    <div style="text-align: left; color: #b45309; font-size: 0.9rem; line-height: 1.4;">
                      Se debe devolver <strong style="color: #d97706; font-size: 1.05rem;">$${formatPrecio(turno.monto_seña)}</strong> al cliente en efectivo.
                    </div>
                  </div>
                ` : ''}
              </div>
            `,
            showConfirmButton: true,
            confirmButtonText: `<div style="display: flex; align-items: center; justify-content: center; gap: 8px; font-weight: 600;">
                                  <i class="bi bi-check-lg"></i>
                                  Entendido
                                </div>`,
            confirmButtonColor: hayReembolso ? '#10b981' : '#3b82f6'
          })
        } else {
          await Swal.fire({
            icon: 'error',
            title: '<span style="color: #dc2626; font-weight: 700;">Error</span>',
            html: `<div style="text-align: center; color: #6b7280;">${response.data.error || 'Error desconocido'}</div>`,
            confirmButtonText: 'Reintentar',
            confirmButtonColor: '#dc2626'
          })
        }
        await cargarTurnos()
      } catch (error) {
        console.error('Error cancelando turno:', error)
        Swal.fire({
          icon: 'error',
          title: '<span style="color: #dc2626; font-weight: 700;">Error de conexión</span>',
          html: `<div style="text-align: left; background: #fef2f2; padding: 12px; border-radius: 8px; color: #991b1b; font-size: 0.85rem;">
                    <strong>Detalle técnico:</strong><br>
                    ${error.response?.data?.error || error.message || 'Error de servidor'}
                  </div>`,
          confirmButtonColor: '#6b7280'
        })
      } finally {
        loading.value = false
      }
    }
  } catch (error) {
    console.error('Error en cancelarTurno:', error)
    loading.value = false
  }
}

// ✅ PAGO TOTAL (COBRAR RESTO DE SEÑA)
const confirmarPagoTotal = async (turno) => {
  const falta = calcularFaltaPagar(turno)
  
  const { value: nroTransaccion } = await Swal.fire({
    title: 'Cobrar Restante',
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Monto total:</strong> $${formatPrecio(turno.monto_total)}</p>
        <p><strong>Seña pagada:</strong> $${formatPrecio(turno.monto_seña)}</p>
        <p><strong>Falta cobrar:</strong> <span style="color: #f59e0b; font-weight: bold;">$${formatPrecio(falta)}</span></p>
        <br>
        <label for="nro_transaccion" style="display: block; margin-bottom: 8px; font-weight: bold;">N° de transacción (opcional):</label>
        <input id="nro_transaccion" class="swal2-input" placeholder="Ej: MP-123456789 o Transferencia-001">
      </div>
    `,
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Registrar Pago',
    cancelButtonText: 'Cancelar',
    preConfirm: () => {
      const input = document.getElementById('nro_transaccion')
      return input.value || ''
    }
  })

  if (nroTransaccion !== undefined) {
    try {
      await axios.post(`/api/turnos/${turno.id}/actualizar-pago/`, {
        tipo_pago: 'TOTAL',
        medio_pago: turno.medio_pago || 'EFECTIVO',
        nro_transaccion: nroTransaccion || ''
      })
      
      await cargarTurnos()
      
      Swal.fire({
        icon: 'success',
        title: '¡Pago registrado!',
        text: 'El pago total ha sido registrado correctamente.',
        showConfirmButton: true
      })
      
    } catch (error) {
      console.error('Error registrando pago:', error)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo registrar el pago. Intenta nuevamente.'
      })
    }
  }
}

// ✅ GESTIÓN DE REEMBOLSO MANUAL
const gestionarReembolsoManual = async (turno) => {
  const monto = calcularMontoReembolso(turno)
  
  const { isConfirmed } = await Swal.fire({
    title: 'Confirmar devolución de dinero',
    html: `
      <div style="text-align: left;">
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Monto a devolver:</strong> <span style="color: #f59e0b; font-weight: bold;">$${formatPrecio(monto)}</span></p>
        <p><strong>Medio de pago original:</strong> ${getMedioPagoTexto(turno.medio_pago)}</p>
        <br>
        <p style="color: #6b7280; font-size: 0.9rem;">
          <i class="bi bi-info-circle"></i> Esta acción marcará el reembolso como "COMPLETADO" en el sistema.
        </p>
      </div>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#f59e0b',
    confirmButtonText: 'Sí, dinero devuelto',
    cancelButtonText: 'Cancelar'
  })

  if (isConfirmed) {
    try {
      await axios.post(`/api/turnos/${turno.id}/completar-reembolso-manual/`)
      await cargarTurnos()
      
      Swal.fire({
        icon: 'success',
        title: '¡Reembolso completado!',
        text: 'El reembolso ha sido marcado como completado.',
        showConfirmButton: true
      })
      
    } catch (error) {
      console.error('Error completando reembolso:', error)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo marcar el reembolso como completado.'
      })
    }
  }
}

// ✅ FUNCIÓN MEJORADA PARA VER DETALLE DEL TURNO (CORREGIDA)
const verDetalleTurno = async (turno) => {
  // Calcular duración total
  const duracionTotal = turno.duracion_total || 
    (turno.servicios ? turno.servicios.reduce((total, s) => total + (s.duracion || 0), 0) : 30)
  
  // Calcular servicios
  let serviciosHTML = ''
  let serviciosLista = []
  let totalServicios = 0
  
  if (turno.servicios && turno.servicios.length > 0) {
    serviciosLista = turno.servicios.map(s => {
      totalServicios += parseFloat(s.precio || 0)
      return {
        nombre: s.nombre,
        precio: parseFloat(s.precio || 0),
        duracion: s.duracion || 30
      }
    })
    
    serviciosHTML = serviciosLista.map(s => 
      `<tr>
        <td>${s.nombre}</td>
        <td style="text-align: right;">${s.duracion} min</td>
        <td style="text-align: right;">$${formatPrecio(s.precio)}</td>
      </tr>`
    ).join('')
  }
  
  // Determinar estado de reembolso
  let reembolsoHTML = ''
  if (turno.reembolso_estado && turno.reembolso_estado !== 'NO_APLICA') {
    const reembolsoClases = {
      'PENDIENTE': 'warning',
      'COMPLETADO': 'success',
      'NO_APLICA': 'secondary'
    }
    
    const reembolsoIconos = {
      'PENDIENTE': '⏳',
      'COMPLETADO': '✅',
      'NO_APLICA': '➖'
    }
    
    reembolsoHTML = `
      <div style="background: #f8fafc; padding: 15px; border-radius: 10px; margin-top: 15px;">
        <h4 style="color: #0ea5e9; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
          <i class="bi bi-arrow-left-right"></i> Estado de Reembolso
        </h4>
        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
          <div>
            <strong>Estado:</strong> 
            <span style="background: ${turno.reembolso_estado === 'PENDIENTE' ? '#fef3c7' : '#d1fae5'}; 
                          color: ${turno.reembolso_estado === 'PENDIENTE' ? '#d97706' : '#059669'}; 
                          padding: 4px 10px; border-radius: 20px; margin-left: 8px; font-size: 0.8rem;">
              ${reembolsoIconos[turno.reembolso_estado] || '📝'} ${turno.reembolso_estado}
            </span>
          </div>
          ${turno.reembolsado ? '<div><strong>Reembolsado:</strong> Sí</div>' : ''}
          ${turno.mp_refund_id ? `<div><strong>ID Reembolso MP:</strong> ${turno.mp_refund_id}</div>` : ''}
        </div>
      </div>
    `
  }
  
  // Información de pago detallada
  const faltaPagar = calcularFaltaPagar(turno)
  const seniaPagada = turno.monto_seña > 0
  
  // Formatear fechas de creación y modificación
  const formatDateSafe = (dateString) => {
    if (!dateString) return 'Fecha no disponible'
    const date = new Date(dateString)
    return isNaN(date.getTime()) ? 'Fecha inválida' : date.toLocaleDateString('es-AR') + ' ' + date.toLocaleTimeString('es-AR', {hour: '2-digit', minute:'2-digit'})
  }

  Swal.fire({
    title: `<div style="display: flex; align-items: center; gap: 12px; color: #0ea5e9;">
              <i class="bi bi-calendar2-week" style="font-size: 1.5rem;"></i>
              <span>Turno #${turno.id} - ${formatFecha(turno.fecha)} ${formatHora(turno.hora)}hs</span>
            </div>`,
    html: `
      <div style="text-align: left; max-width: 700px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        
        <!-- 🔥 ENCABEZADO CON ESTADO -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e2e8f0;">
          <div>
            <span class="badge-estado ${getEstadoClass(turno.estado, turno.tipo_pago)}" style="font-size: 0.9rem;">
              ${getEstadoTexto(turno.estado, turno.tipo_pago)}
            </span>
            <span class="canal-badge ${(turno.canal || 'PRESENCIAL').toLowerCase()}" style="margin-left: 8px;">
              ${turno.canal || 'PRESENCIAL'}
            </span>
          </div>
          <div style="font-size: 1.2rem; font-weight: 900; color: #0f172a;">
            $${formatPrecio(turno.monto_total)}
          </div>
        </div>
        
        <!-- 📋 INFORMACIÓN BÁSICA EN 2 COLUMNAS -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
          <div style="background: #f8fafc; padding: 15px; border-radius: 10px;">
            <h4 style="color: #0ea5e9; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
              <i class="bi bi-person"></i> Cliente
            </h4>
            <p style="margin: 5px 0; font-size: 0.95rem;">
              <strong>Nombre:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}
            </p>
            ${turno.cliente_dni ? `<p style="margin: 5px 0; font-size: 0.95rem;"><strong>DNI:</strong> ${turno.cliente_dni}</p>` : ''}
          </div>
          
          <div style="background: #f8fafc; padding: 15px; border-radius: 10px;">
            <h4 style="color: #10b981; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
              <i class="bi bi-scissors"></i> Peluquero
            </h4>
            <p style="margin: 5px 0; font-size: 0.95rem;">
              <strong>Nombre:</strong> ${turno.peluquero_nombre || 'No asignado'} ${turno.peluquero_apellido || ''}
            </p>
            <p style="margin: 5px 0; font-size: 0.95rem;">
              <strong>Duración:</strong> ${duracionTotal} minutos
            </p>
          </div>
        </div>
        
        <!-- 💰 INFORMACIÓN DE PAGO -->
        <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #0ea5e9;">
          <h4 style="color: #0369a1; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
            <i class="bi bi-cash-stack"></i> Información de Pago
          </h4>
          
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; text-align: center;">
            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
              <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 4px;">Total</div>
              <div style="font-size: 1.2rem; font-weight: 900; color: #0f172a;">$${formatPrecio(turno.monto_total)}</div>
            </div>
            
            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
              <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 4px;">Seña</div>
              <div style="font-size: 1.2rem; font-weight: 900; color: #10b981;">$${formatPrecio(turno.monto_seña)}</div>
            </div>
            
            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
              <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 4px;">Falta</div>
              <div style="font-size: 1.2rem; font-weight: 900; color: ${faltaPagar > 0 ? '#f59e0b' : '#10b981'};">$${formatPrecio(faltaPagar)}</div>
            </div>
          </div>
          
          <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
              <div>
                <strong>Tipo de pago:</strong> 
                <span style="background: ${turno.tipo_pago === 'TOTAL' ? '#d1fae5' : '#fef3c7'}; 
                              color: ${turno.tipo_pago === 'TOTAL' ? '#059669' : '#d97706'}; 
                              padding: 2px 8px; border-radius: 4px; margin-left: 6px;">
                  ${turno.tipo_pago === 'SENA_50' ? 'Seña 50%' : 'Pago Total'}
                </span>
              </div>
              <div>
                <strong>Medio:</strong> 
                <span class="medio-pago-badge ${getMedioPagoClass(turno.medio_pago)}" style="margin-left: 6px;">
                  ${getMedioPagoTexto(turno.medio_pago)}
                </span>
              </div>
            </div>
            
            ${turno.nro_transaccion ? `
              <div style="margin-top: 10px; font-size: 0.85rem;">
                <strong>N° Transacción:</strong> 
                <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">
                  ${turno.nro_transaccion}
                </code>
              </div>
            ` : ''}
            
            ${turno.mp_payment_id ? `
              <div style="margin-top: 10px; font-size: 0.85rem;">
                <strong>MP Payment ID:</strong> 
                <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; margin-left: 6px; font-size: 0.8rem;">
                  ${turno.mp_payment_id}
                </code>
              </div>
            ` : ''}
          </div>
        </div>
        
        <!-- ✂️ SERVICIOS -->
        ${serviciosHTML ? `
          <div style="background: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
            <h4 style="color: #7c3aed; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
              <i class="bi bi-list-check"></i> Servicios (${serviciosLista.length})
            </h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid #e2e8f0;">
                  <th style="text-align: left; padding: 8px 0; color: #64748b;">Servicio</th>
                  <th style="text-align: right; padding: 8px 0; color: #64748b;">Duración</th>
                  <th style="text-align: right; padding: 8px 0; color: #64748b;">Precio</th>
                </tr>
              </thead>
              <tbody>
                ${serviciosHTML}
                <tr style="border-top: 2px solid #e2e8f0; font-weight: bold;">
                  <td style="padding: 10px 0; color: #0f172a;">Total</td>
                  <td style="text-align: right; padding: 10px 0; color: #64748b;">${duracionTotal} min</td>
                  <td style="text-align: right; padding: 10px 0; color: #0f172a;">$${formatPrecio(totalServicios)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        ` : ''}
        
        <!-- 📝 INFORMACIÓN ADICIONAL -->
        <div style="background: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
          <h4 style="color: #475569; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
            <i class="bi bi-info-circle"></i> Información Adicional
          </h4>
          ${turno.motivo_cancelacion ? `
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0;">
              <div style="font-size: 0.8rem; color: #64748b;">Motivo de cancelación</div>
              <div style="color: #dc2626; font-weight: 600; background: #fee2e2; padding: 8px 12px; border-radius: 6px; margin-top: 4px; border-left: 3px solid #dc2626;">
                ${turno.motivo_cancelacion}
              </div>
            </div>
          ` : ''}
          
          ${turno.obs_cancelacion ? `
            <div style="margin-top: 10px;">
              <div style="font-size: 0.8rem; color: #64748b;">Observaciones</div>
              <div style="color: #475569; background: #f1f5f9; padding: 8px 12px; border-radius: 6px; margin-top: 4px; font-size: 0.9rem;">
                ${turno.obs_cancelacion}
              </div>
            </div>
          ` : ''}
        </div>
        
        <!-- 🔄 REEMBOLSO -->
        ${reembolsoHTML}
        
      </div>
    `,
    showCloseButton: true,
    showConfirmButton: false,
    width: '750px',
    padding: '0',
    customClass: {
      popup: 'swal2-popup-custom',
      title: 'swal2-title-custom'
    }
  })
}

// ✅ COMPLETAR TURNO
const completarTurno = async (turno) => {
  const { isConfirmed } = await Swal.fire({
    title: '¿Completar turno?',
    html: `
      <div style="text-align: left;">
        <p>Marcar este turno como <strong>COMPLETADO</strong>.</p>
        <p><strong>Cliente:</strong> ${turno.cliente_nombre} ${turno.cliente_apellido}</p>
        <p><strong>Total:</strong> $${formatPrecio(turno.monto_total)}</p>
      </div>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Sí, completar',
    cancelButtonText: 'Cancelar'
  })

  if (isConfirmed) {
    try {
      await axios.post(`/api/turnos/${turno.id}/cambiar-estado/COMPLETADO/`)
      await cargarTurnos()
      
      Swal.fire({
        icon: 'success',
        title: '¡Turno completado!',
        text: 'El turno ha sido marcado como COMPLETADO.',
        showConfirmButton: true
      })
      
    } catch (error) {
      console.error('Error completando turno:', error)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo completar el turno.'
      })
    }
  }
}

// ✅ FILTROS Y PAGINACIÓN
const limpiarFiltros = () => {
  filtros.value = {
    busqueda: '',
    peluquero: '',
    estado: '',
    canal: '',
    fechaDesde: '',
    fechaHasta: ''
  }
  pagina.value = 1
  cargarTurnos()
}

const turnosFiltrados = computed(() => {
  let filtrados = turnos.value
  
  // Filtro por búsqueda (cliente o peluquero)
  if (filtros.value.busqueda) {
    const busqueda = filtros.value.busqueda.toLowerCase()
    filtrados = filtrados.filter(turno => {
      const cliente = `${turno.cliente_nombre || ''} ${turno.cliente_apellido || ''}`.toLowerCase()
      const peluquero = `${turno.peluquero_nombre || ''} ${turno.peluquero_apellido || ''}`.toLowerCase()
      return cliente.includes(busqueda) || peluquero.includes(busqueda)
    })
  }
  
  // Filtro por estado
  if (filtros.value.estado) {
    filtrados = filtrados.filter(turno => turno.estado === filtros.value.estado)
  }
  
  // Filtro por canal
  if (filtros.value.canal) {
    filtrados = filtrados.filter(turno => turno.canal === filtros.value.canal)
  }
  
  // Filtro por fecha desde
  if (filtros.value.fechaDesde) {
    filtrados = filtrados.filter(turno => turno.fecha >= filtros.value.fechaDesde)
  }
  
  // Filtro por fecha hasta
  if (filtros.value.fechaHasta) {
    filtrados = filtrados.filter(turno => turno.fecha <= filtros.value.fechaHasta)
  }
  
  return filtrados
})

const totalPaginas = computed(() => {
  return Math.ceil(turnosFiltrados.value.length / itemsPorPagina)
})

const turnosFiltradosPaginados = computed(() => {
  const start = (pagina.value - 1) * itemsPorPagina
  const end = start + itemsPorPagina
  return turnosFiltrados.value.slice(start, end)
})

const paginaAnterior = () => {
  if (pagina.value > 1) pagina.value--
}

const paginaSiguiente = () => {
  if (pagina.value < totalPaginas.value) pagina.value++
}

// ✅ LÓGICA DE PERMISOS PARA BOTONES
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

// ✅ CARGA INICIAL Y WATCHERS
onMounted(() => {
  cargarTurnos()
})

watch(filtros, () => {
  pagina.value = 1
  // El cargarTurnos se llama automáticamente con los @change en los inputs
}, { deep: true })
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - TURNOS (MODO OSCURO POR DEFECTO)
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

/* ✅ BADGE ROJO ELEGANTE PARA MOTIVO DE CANCELACIÓN */
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

/* ✅ ESTILOS PARA LOS MODALES PROFESIONALES */
:deep(.swal2-popup-custom) {
  border-radius: 20px !important;
  border: 2px solid #0ea5e9 !important;
  overflow: hidden !important;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}

:deep(.swal2-title-custom) {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
  padding: 20px 24px 10px 24px !important;
  margin: 0 !important;
  font-size: 1.4rem !important;
  font-weight: 900 !important;
}

:deep(.swal2-close) {
  color: #64748b !important;
  transition: color 0.3s ease !important;
  font-size: 1.8rem !important;
}

:deep(.swal2-close:hover) {
  color: #ef4444 !important;
}

:deep(.swal2-html-container) {
  padding: 0 24px 24px 24px !important;
  margin: 0 !important;
  max-height: 70vh !important;
  overflow-y: auto !important;
}

:deep(.swal2-select) {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
  transition: all 0.3s ease !important;
}

:deep(.swal2-select:focus) {
  border-color: #0ea5e9 !important;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2) !important;
  outline: none !important;
}

:deep(.swal2-textarea) {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
  transition: all 0.3s ease !important;
}

:deep(.swal2-textarea:focus) {
  border-color: #0ea5e9 !important;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2) !important;
  outline: none !important;
}

/* ✅ ESTILOS PARA SCROLLBAR EN MODALES */
:deep(.swal2-html-container)::-webkit-scrollbar {
  width: 8px;
}

:deep(.swal2-html-container)::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

:deep(.swal2-html-container)::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

:deep(.swal2-html-container)::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* ✅ ANIMACIÓN PARA BOTONES DE CONFIRMACIÓN */
:deep(.swal2-confirm) {
  transition: all 0.3s ease !important;
  font-weight: 700 !important;
  letter-spacing: 0.5px !important;
}

:deep(.swal2-confirm:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
}

/* ✅ BADGE NARANJA PARA REEMBOLSO PENDIENTE */
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

/* ✅ BADGE VERDE PARA REEMBOLSO COMPLETADO */
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

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
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

.transaccion-info {
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px dashed #e2e8f0;
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

/* Badge para motivo de cancelación (rojo elegante) */
.badge-motivo-cancelacion {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #dc2626;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border-left: 3px solid #dc2626;
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.1);
}

/* Badge para reembolso pendiente (naranja llamativo) */
.badge-reembolso-pendiente {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #d97706;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border-left: 3px solid #f59e0b;
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
  animation: pulse 2s infinite;
}

/* Badge para reembolso completado (verde profesional) */
.badge-reembolso-completado {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #059669;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border-left: 3px solid #10b981;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
}

/* Animación para badge pendiente */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.8; }
  100% { opacity: 1; }
}

/* Estilos para información de pago */
.text-senia {
  font-size: 0.8rem;
  color: #059669;
  font-weight: 500;
}

.text-falta {
  font-size: 0.8rem;
  color: #f59e0b;
  font-weight: 600;
}

.text-pagado {
  font-size: 0.8rem;
  color: #3b82f6;
  font-weight: 500;
}

/* Badge de medio de pago */
.medio-pago-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.medio-pago-badge.efectivo { background: #d1fae5; color: #065f46; }
.medio-pago-badge.mp { background: #93c5fd; color: #1e40af; }
.medio-pago-badge.tarjeta { background: #e9d5ff; color: #7c3aed; }
.medio-pago-badge.transferencia { background: #fecaca; color: #b91c1c; }
.medio-pago-badge.pendiente { background: #f3f4f6; color: #6b7280; }
.medio-pago-badge.otro { background: #fde68a; color: #92400e; }

/* ✅ BOTONES DE ACCIÓN */
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

/* 🔥 ESTILOS PARA MEDIO DE PAGO */
.medio-pago-wrapper { 
  margin-bottom: 4px; 
}

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

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-card { padding: 25px; border-radius: 20px; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .header-content h1 { font-size: 1.6rem; }
  .filters-grid { grid-template-columns: 1fr; }
  .users-table { font-size: 0.85rem; }
  .users-table th { font-size: 0.7rem; padding: 14px 10px; }
  .action-buttons { flex-direction: column; gap: 6px; }
  .precio-total-container { min-width: auto; padding: 8px; }
  .precio-total { font-size: 0.95rem; }
  .pagination { flex-direction: column; gap: 12px; }
}

@media (max-width: 480px) {
  .list-card { padding: 18px; border-radius: 16px; }
  .header-content h1 { font-size: 1.4rem; }
  .users-table { display: block; overflow-x: auto; white-space: nowrap; }
  .filter-input, .filter-select { font-size: 0.9rem; }
  .badge-estado { font-size: 0.65rem; padding: 5px 10px; }
  .action-button { width: 36px; height: 36px; }
  .precio-total-container { flex-direction: row; justify-content: space-between; align-items: center; }
}
</style>