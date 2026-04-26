<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Turnos</h1>
          <p>Gestión y administración de turnos</p>
        </div>
        <button v-if="esAdminORecep" @click="irARegistrar" class="register-button"><Plus :size="18" /> Registrar Turno</button>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label for="busqueda">Buscar</label>
            <input v-model="filtros.busqueda" id="busqueda" type="text" class="filter-input" 
                   placeholder="Cliente, Transacción..." @keyup.enter="cargarTurnos">
          </div>
          <div class="filter-group" v-if="esAdminORecep">
            <label for="peluquero">Profesional</label>
            <select v-model="filtros.peluquero" id="peluquero" class="filter-select" @change="cargarTurnos">
              <option value="">Todos</option>
              <option v-for="pel in listaPeluqueros" :key="pel.id" :value="pel.id">
                {{ pel.nombre }} {{ pel.apellido }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label for="estado">Estado</label>
            <select v-model="filtros.estado" id="estado" class="filter-select" @change="cargarTurnos">
              <option value="">Todos</option>
              <option value="RESERVADO">Reservado</option>
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
            <label for="medioPago">Método Pago</label>
            <select v-model="filtros.medioPago" id="medioPago" class="filter-select" @change="cargarTurnos">
              <option value="">Todos</option>
              <option value="EFECTIVO">Efectivo</option>
              <option value="MERCADO_PAGO">Mercado Pago</option>
            </select>
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
              <th style="width: 60px;">ID</th>
              <th>Fecha/Hora</th>
              <th>Cliente</th>
              <th>Estado</th> 
              <th>Pago / Transacción</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="turno in turnosFiltradosPaginados" :key="turno.id">
              <td>
                <span class="badge-id">#{{ turno.id }}</span>
              </td>
              <td>
                <strong>{{ formatFecha(turno.fecha) }}</strong><br>
                <small>{{ formatHora(turno.hora) }}hs</small><br>
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
                    {{ turno.descuento_aplicado }}% Fidelización
                  </span>
                </div>
                
                <div v-if="turno.estado === 'CANCELADO'">
                  <div v-if="turno.reembolso_estado === 'NO_APLICA' && esTurnoPorCanje(turno)" style="margin-top: 5px;">
                    <span class="badge-reembolso-no-aplica">
                      <i class="bi bi-arrow-left-right me-1"></i>
                      Canje - No aplica reembolso
                    </span>
                  </div>
                  
                  <div v-else-if="turno.reembolso_estado === 'NO_APLICA'" style="margin-top: 5px;">
                    <span class="badge-reembolso-no-aplica">
                      <i class="bi bi-clock me-1"></i>
                      Sin reembolso (cancelación tardía)
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
                  <span class="payment-status-badge" :class="getPaymentBadgeClass(turno)">
                    <template v-if="(parseFloat(turno.monto_total) || 0) > (parseFloat(turno.monto_seña) || 0)">
                      ⚠️ FALTA COBRAR: ${{ formatPrecio((parseFloat(turno.monto_total) || 0) - (parseFloat(turno.monto_seña) || 0)) }}
                    </template>
                    <template v-else>
                      ✅ PAGADO TOTAL
                    </template>
                  </span>

                  <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 6px; font-weight: 500;">
                    Seña: ${{ formatPrecio(turno.monto_seña || 0) }} ({{ getMedioPagoTexto(turno.medio_pago, turno.entidad_pago) }})
                  </div>

                  <div style="font-size: 0.85rem; color: #94a3b8; opacity: 0.8;">
                    Total Turno: ${{ formatPrecio(turno.monto_total || 0) }}
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  
                  <button @click="verDetalleTurno(turno)" class="action-button view" title="Ver Detalle">
                    <Eye :size="14"/>
                  </button>
                  
                  <button v-if="esAdminORecep && puedeEditarTurno(turno)" 
                          @click="editarTurno(turno)" 
                          class="action-button edit" 
                          title="Editar Turno">
                    <Edit :size="14"/>
                  </button>
                  
                  <button v-if="esAdminORecep && turno.estado === 'CANCELADO' && turno.reembolso_estado === 'PENDIENTE'" 
                          @click="gestionarReembolsoManual(turno)" 
                          class="action-button reembolso" 
                          title="Marcar como Dinero Devuelto">
                    <ArrowRightLeft :size="14"/>
                  </button>
                  
                  <button v-if="esAdminORecep && esEstadoActivo(turno.estado) && (parseFloat(turno.monto_total) || 0) > (parseFloat(turno.monto_seña) || 0)" 
                          @click="confirmarPagoTotal(turno)" 
                          class="action-button pagar" 
                          title="Cobrar Restante">
                    <CreditCard :size="14"/>
                  </button>
                  
                  <button v-if="esAdminORecep && mostrarBotonCompletar(turno)" 
                          @click="completarTurno(turno)" 
                          class="action-button complete" 
                          title="Finalizar Atención">
                    <Check :size="14"/>
                  </button>
                  
                  <button v-if="esAdminORecep && puedeCancelarTurno(turno)" 
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
const listaPeluqueros = ref([]) 
const pagina = ref(1)
const itemsPorPagina = 7
const loading = ref(false)
const filtros = ref({ 
  busqueda: '', 
  peluquero: '', 
  estado: '', 
  canal: '', 
  fechaDesde: '', 
  fechaHasta: '' ,
  medioPago: ''
})

const userRol = computed(() => {
  return (localStorage.getItem('user_rol') || '').toUpperCase()
})

const esAdminORecep = computed(() => {
  return ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'SUPERUSER'].includes(userRol.value)
})

const irARegistrar = () => {
  router.push('/turnos/crear-presencial')
}

const editarTurno = (turno) => {
  router.push(`/turnos/modificar/${turno.id}`)
}

const puedeEditarTurno = (turno) => {
  if (turno.estado !== 'RESERVADO') return false;
  return ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'PELUQUERO', 'PEL'].includes(userRol.value);
};

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
  if (!precio && precio !== 0) return '0.00'
  const numero = parseFloat(precio)
  if (isNaN(numero)) return '0.00'
  return numero.toLocaleString('es-AR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const getEntidadPagoTexto = (entidad) => {
  if (!entidad) return ''
  const mapaEntidades = {
    'MERCADO_PAGO': 'Mercado Pago', 'MERCADOPAGO': 'Mercado Pago', 'UALA': 'Ualá',
    'CUENTADNI': 'Cuenta DNI', 'BRUBANK': 'Brubank', 'LEMON': 'Lemon Cash',
    'NARANJAX': 'Naranja X', 'MODO': 'MODO', 'SANTANDER': 'Santander Río',
    'GALICIA': 'Galicia', 'BBVA': 'BBVA', 'MACRO': 'Macro', 'OTRO': 'Otro'
  }
  return mapaEntidades[entidad] || entidad
}

const getMedioPagoTexto = (medioPago, entidadPago = null) => {
  if (!medioPago || medioPago === 'PENDIENTE') return 'Pendiente'
  if (medioPago === 'TRANSFERENCIA' && entidadPago) {
    return getEntidadPagoTexto(entidadPago)
  }
  const map = {
    'MERCADO_PAGO': 'Mercado Pago',
    'EFECTIVO': 'Efectivo',
  }
  return map[medioPago] || medioPago
}

const calcularFaltaPagar = (turno) => {
  if (turno.tipo_pago === 'TOTAL') return 0;
  const total = parseFloat(turno.monto_total) || 0
  const senia = parseFloat(turno.monto_seña) || 0
  return Math.max(0, total - senia)
}

const calcularMontoReembolso = (turno) => {
  if (turno.estado !== 'CANCELADO' || turno.reembolso_estado !== 'PENDIENTE') return 0
  
  if (turno.tipo_pago === 'TOTAL' || turno.medio_pago_restante) {
    return parseFloat(turno.monto_total) || 0
  }
  
  return parseFloat(turno.monto_seña) || parseFloat(turno.monto_total) || 0
}

const esTurnoPorCanje = (turno) => {
  if (turno.estado === 'CANCELADO') {
    if (turno.motivo_cancelacion && 
        (turno.motivo_cancelacion.includes('Turno por canje') ||
         turno.motivo_cancelacion.includes('Canjeado') ||
         turno.motivo_cancelacion.includes('Reoferta'))) {
      return true;
    }
    if (turno.obs_cancelacion && 
        (turno.obs_cancelacion.includes('Canjeado') || 
         turno.obs_cancelacion.includes('Reoferta') ||
         turno.obs_cancelacion.includes('Origen: Turno Viejo'))) {
      return true;
    }
  } else {
    if (turno.obs_cancelacion && turno.obs_cancelacion.includes('Turno obtenido por canje')) {
      return true;
    }
  }
  return false;
}

const esTurnoConDescuento = (turno) => {
  return turno.obs_cancelacion && 
         (turno.obs_cancelacion.includes('15%') || 
          turno.obs_cancelacion.includes('Descuento'))
}

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
  if (turno.duracion_total) return `${turno.duracion_total} min`
  if (turno.servicios && turno.servicios.length > 0) {
    const duracion = turno.servicios.reduce((total, servicio) => {
      return total + (servicio.duracion || 0)
    }, 0)
    return `${duracion} min`
  }
  return '30 min'
}

const esEstadoActivo = (estado) => estado === 'RESERVADO';

const getEstadoTexto = (estado, tipoPago) => {
  if (estado === 'RESERVADO') return 'Reservado';
  return estado;
};

const getEstadoClass = (estado, tipoPago) => {
  if (estado === 'RESERVADO') {
    return tipoPago === 'TOTAL' ? 'estado-success' : 'estado-warning';
  } else if (estado === 'COMPLETADO') {
    return 'estado-completado';
  } else if (estado === 'CANCELADO') {
    return 'estado-cancelado';
  }
  return 'estado-secondary';
};

const getMedioPagoClass = (medioPago) => {
  if (!medioPago) return 'otro'
  const medio = medioPago.toLowerCase()
  if (medio.includes('mercado')) return 'mp'
  if (medio.includes('efectivo')) return 'efectivo'
  if (medio.includes('pendiente')) return 'pendiente'
  return 'otro'
}

// 🔥 INDICADORES DE PAGO
const getPaymentBadgeData = (turno) => {
  const total = parseFloat(turno.monto_total) || 0
  const sena = parseFloat(turno.monto_seña) || 0
  
  if (sena >= total) {
    return { class: 'badge-pagado-total', text: 'Pagado Total' }
  } else if (sena > 0) {
    const diff = total - sena
    return { class: 'badge-saldo-pendiente', text: `Saldo: $${formatPrecio(diff)}` }
  } else {
    return { class: 'badge-a-pagar', text: `A Pagar: $${formatPrecio(total)}` }
  }
}

const getPaymentBadgeClass = (turno) => getPaymentBadgeData(turno).class
const getPaymentBadgeText = (turno) => getPaymentBadgeData(turno).text

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
    
    const response = await axios.get(`/api/turnos/?${params.toString()}`)
    turnos.value = response.data || []
    
    turnos.value.sort((a, b) => {
      const dateA = new Date(`${a.fecha}T${a.hora}`)
      const dateB = new Date(`${b.fecha}T${b.hora}`)
      return dateB - dateA
    })
    
  } catch (error) {
    console.error('❌ Error cargando turnos:', error)
    Swal.fire('Error', 'No se pudieron cargar los turnos.', 'error')
  } finally {
    loading.value = false
  }
}

const cancelarTurno = async (turno) => {
  try {
    let margenConfig = 3; 
    try {
        const resConfig = await axios.get('/api/configuracion/');
        if (resConfig.data && resConfig.data.margen_horas_cancelacion) {
            margenConfig = resConfig.data.margen_horas_cancelacion;
        }
    } catch (e) { console.error("Error al obtener margen de cancelación:", e) }

    const ahora = new Date();
    const fechaTurno = new Date(`${turno.fecha}T${turno.hora}`);
    const horasFaltantes = (fechaTurno - ahora) / (1000 * 60 * 60);
    const hayReembolso = horasFaltantes >= margenConfig && (parseFloat(turno.monto_seña) > 0 || parseFloat(turno.monto_total) > 0);
    
    // Calculamos el monto solo para mostrárselo como aviso
    let montoTotal = 0;
    if (turno.tipo_pago === 'TOTAL' || turno.medio_pago_restante) {
      montoTotal = parseFloat(turno.monto_total) || 0;
    } else {
      montoTotal = parseFloat(turno.monto_seña) || parseFloat(turno.monto_total) || 0;
    }

    const { value: formValues } = await Swal.fire({
      title: '',
      width: '480px',
      html: `
        <div style="font-family: 'Inter', -apple-system, sans-serif; text-align: left;">
          
          <div style="text-align: center; margin-bottom: 20px;">
            <div style="background: #fee2e2; color: #ef4444; width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; font-size: 2rem;">
              <i class="bi bi-calendar-x"></i>
            </div>
            <h2 style="margin: 0; font-size: 1.4rem; font-weight: 800; color: #1e293b;">Cancelar Turno</h2>
            <p style="margin: 5px 0 0 0; color: #64748b; font-size: 0.95rem;">Estás a punto de anular la reserva de <b>${turno.cliente_nombre}</b>.</p>
          </div>

          ${hayReembolso ? `
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 15px; margin-bottom: 20px; display: flex; gap: 15px; align-items: flex-start; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
              <span style="font-size: 1.5rem;">✅</span>
              <div>
                <strong style="color: #166534; font-size: 0.95rem; display: block; margin-bottom: 4px;">Reembolso a favor del cliente</strong>
                <span style="color: #15803d; font-size: 0.85rem; line-height: 1.4; display: block;">
                  Se generará un <b>reembolso pendiente de $${formatPrecio(montoTotal)}</b> porque cancela con ${Math.floor(horasFaltantes)}hs de anticipación. Luego podrás gestionarlo desde la tabla.
                </span>
              </div>
            </div>
          ` : `
            <div style="background: #fffbeb; border: 1px solid #fef3c7; border-radius: 12px; padding: 15px; margin-bottom: 20px; display: flex; gap: 15px; align-items: flex-start; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
              <span style="font-size: 1.5rem;">⚠️</span>
              <div>
                <strong style="color: #92400e; font-size: 0.95rem; display: block; margin-bottom: 4px;">Sin Reembolso</strong>
                <span style="color: #b45309; font-size: 0.85rem; line-height: 1.4; display: block;">
                  Cancelación con ${Math.floor(horasFaltantes)}hs de anticipación (Mínimo requerido: ${margenConfig}hs). El dinero no se devuelve.
                </span>
              </div>
            </div>
          `}

          <div style="background: #f8fafc; padding: 20px; border-radius: 14px; border: 1px solid #e2e8f0;">
            <label style="display:block; margin-bottom:8px; font-weight: 700; color: #334155; font-size: 0.9rem;">Motivo de cancelación:</label>
            <select id="motivoCancelacion" class="swal2-input" style="width: 100%; margin: 0 0 15px 0; height: 45px; font-size: 0.95rem; border-radius: 10px; border: 1px solid #cbd5e1; color: #0f172a; background: white;">
              <option value="" disabled selected>Seleccioná un motivo...</option>
              <option value="MOTIVOS_PERSONALES">Motivos personales</option>
              <option value="PROBLEMAS_SALUD">Problema de salud</option>
              <option value="ERROR_RESERVA">Error al reservar</option>
              <option value="CAMBIO_PLANES">Cambio de planes</option>
              <option value="OTRO">Otro</option>
            </select>
            
            <label style="display:block; margin-bottom:8px; font-weight: 700; color: #334155; font-size: 0.9rem;">Observaciones internas:</label>
            <textarea id="observacionesCancelacion" class="swal2-textarea" style="width: 100%; margin: 0; height: 80px; font-size: 0.95rem; padding: 12px; border-radius: 10px; border: 1px solid #cbd5e1; color: #0f172a; background: white;" placeholder="Escribí un detalle (opcional)..."></textarea>
          </div>

        </div>
      `,
      showCancelButton: true,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#64748b',
      confirmButtonText: 'Confirmar Cancelación',
      cancelButtonText: 'Volver',
      didOpen: () => {
        const confirmBtn = Swal.getConfirmButton();
        const cancelBtn = Swal.getCancelButton();
        confirmBtn.style.borderRadius = '10px';
        confirmBtn.style.fontWeight = '700';
        confirmBtn.style.padding = '12px 24px';
        cancelBtn.style.borderRadius = '10px';
        cancelBtn.style.fontWeight = '700';
        cancelBtn.style.padding = '12px 24px';
      },
      preConfirm: () => {
        const motivoSelect = document.getElementById('motivoCancelacion');
        const observacionesTextarea = document.getElementById('observacionesCancelacion');
        
        if (!motivoSelect.value) {
          Swal.showValidationMessage('Por favor seleccioná un motivo');
          return false;
        }
        
        return {
          motivo_cancelacion: motivoSelect.options[motivoSelect.selectedIndex].text,
          motivo_cancelacion_codigo: motivoSelect.value,
          obs_cancelacion: observacionesTextarea.value.trim() || ''
        }
      }
    });

    if (formValues) {
      loading.value = true;
      try {
        Swal.fire({ title: 'Procesando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
        
        const response = await axios.post(`/api/turnos/${turno.id}/cancelar/`, formValues);
        
        if (response.data.status === 'ok') {
          await Swal.fire({ 
            icon: 'success', 
            title: 'Turno cancelado', 
            text: response.data.message || 'El turno ha sido cancelado exitosamente.',
            confirmButtonColor: '#0ea5e9'
          });
        } else {
          await Swal.fire('Error', response.data.error || 'Error desconocido', 'error');
        }
        await cargarTurnos();
      } catch (error) {
        Swal.fire('Error', error.response?.data?.error || 'Error de conexión', 'error');
      } finally {
        loading.value = false;
      }
    }
  } catch (error) {
    console.error('Error en cancelarTurno:', error);
    loading.value = false;
  }
}

const confirmarPagoTotal = async (turno) => {
  const total = parseFloat(turno.monto_total) || 0;
  const pagado = parseFloat(turno.monto_seña) || 0;
  const falta = total - pagado;
  
  const selectEntidadHtml = `
    <div id="entidadContainer" style="display: none; margin-top: 15px; text-align: left;">
      <label style="display: block; font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 5px;">Billetera / Banco de Origen *</label>
      <select id="entidad_pago" class="swal2-input" style="width: 100%; margin: 0; height: 42px; font-size: 0.9rem;">
        <option value="" disabled selected>Seleccione entidad...</option>
        <option value="UALA">Ualá</option>
        <option value="BRUBANK">Brubank</option>
        <option value="LEMON">Lemon Cash</option>
        <option value="NARANJAX">Naranja X</option>
        <option value="MODO">MODO</option>
        <option value="SANTANDER">Santander</option>
        <option value="GALICIA">Galicia</option>
        <option value="BBVA">BBVA</option>
        <option value="MACRO">Macro</option>
        <option value="OTRO">Otro</option>
      </select>
    </div>
  `;

  const { isConfirmed, value: formValues } = await Swal.fire({
    title: 'Cobrar Restante',
    html: `
      <div style="background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Monto a cobrar</p>
        <p style="margin: 5px 0 0 0; color: #10b981; font-size: 1.8rem; font-weight: 800;">$${formatPrecio(falta)}</p>
      </div>

      <div style="text-align: left;">
        <label style="display: block; font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 5px;">Medio de Pago</label>
        <select id="medio_pago" class="swal2-input" style="width: 100%; margin: 0; height: 42px; font-size: 0.9rem;">
          <option value="EFECTIVO" selected>💵 Efectivo</option>
          <option value="MERCADO_PAGO">🔵 Mercado Pago</option>
        </select>

        ${selectEntidadHtml}

        <div id="transaccionContainer" style="display: none; margin-top: 15px;">
          <label style="display: block; font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 5px;">N° de Comprobante *</label>
          <input id="nro_transaccion" type="text" class="swal2-input" style="width: 100%; margin: 0; height: 42px; font-size: 0.9rem;" placeholder="">
        </div>
      </div>
    `,
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Registrar Pago',
    cancelButtonText: 'Cancelar',
    didOpen: () => {
      const medioSelect = document.getElementById('medio_pago');
      const tranContainer = document.getElementById('transaccionContainer');
      const entContainer = document.getElementById('entidadContainer');
      const inputTransaccion = document.getElementById('nro_transaccion');

      medioSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        inputTransaccion.value = ''; 
        
        if (val === 'EFECTIVO') {
          tranContainer.style.display = 'none';
          entContainer.style.display = 'none';
        } else {
          tranContainer.style.display = 'block';
          if (val === 'TRANSFERENCIA') {
            entContainer.style.display = 'block';
            inputTransaccion.placeholder = "Ej: A1B2C3D4 (Máx 18)";
            inputTransaccion.maxLength = 18;
          } else if (val === 'MERCADO_PAGO') {
            entContainer.style.display = 'none';
            inputTransaccion.placeholder = "Ej: 1234567890 (Máx 14)";
            inputTransaccion.maxLength = 14;
          }
        }
      });

      inputTransaccion.addEventListener('input', (e) => {
        if (medioSelect.value === 'MERCADO_PAGO') {
          e.target.value = e.target.value.replace(/\D/g, '');
        } else if (medioSelect.value === 'TRANSFERENCIA') {
          e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
        }
      });
    },
    preConfirm: () => {
      const medio_pago = document.getElementById('medio_pago').value;
      const entidad_pago = document.getElementById('entidad_pago').value;
      const nro_transaccion = document.getElementById('nro_transaccion').value.trim();

      if (medio_pago === 'MERCADO_PAGO') {
        if (!nro_transaccion) {
          Swal.showValidationMessage('El número de comprobante de Mercado Pago es obligatorio.');
          return false;
        }
        if (!/^\d{1,14}$/.test(nro_transaccion)) {
          Swal.showValidationMessage('Mercado Pago admite solo números (hasta 14 dígitos).');
          return false;
        }
      }

      if (medio_pago === 'TRANSFERENCIA') {
        if (!entidad_pago) {
          Swal.showValidationMessage('Debe seleccionar la billetera o banco de origen.');
          return false;
        }
        if (!nro_transaccion) {
          Swal.showValidationMessage('El número de transferencia es obligatorio.');
          return false;
        }
        if (!/^[a-zA-Z0-9]{1,18}$/.test(nro_transaccion)) {
          Swal.showValidationMessage('El comprobante debe ser alfanumérico (hasta 18 caracteres).');
          return false;
        }
      }

      return {
        tipo_pago: 'TOTAL',
        medio_pago: medio_pago,
        entidad_pago: medio_pago === 'TRANSFERENCIA' ? entidad_pago : (medio_pago === 'MERCADO_PAGO' ? 'MERCADO_PAGO' : null),
        nro_transaccion: medio_pago !== 'EFECTIVO' ? nro_transaccion : null
      };
    }
  });

  if (isConfirmed && formValues) {
    try {
      Swal.fire({ title: 'Registrando pago...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
      
      await axios.post(`/api/turnos/${turno.id}/actualizar-pago/`, formValues);
      
      await cargarTurnos();
      Swal.fire('¡Pago registrado!', 'El saldo restante se cobró exitosamente.', 'success');
    } catch (error) { 
      console.error(error);
      Swal.fire('Error', 'No se pudo registrar el pago.', 'error');
    }
  }
}

const gestionarReembolsoManual = async (turno) => {
  const montoTotal = calcularMontoReembolso(turno);
  
  // 1. Detectar si hay pago Online (Mercado Pago)
  const idMP = turno.mp_payment_id || turno.codigo_transaccion;
  const esPagoOnline = idMP && !['EFECTIVO', 'PRESENCIAL', 'None', null, ''].includes(idMP);

  // 2. Lógica de Preferencia e Inteligencia de sugerencia
  let valorEfe = 0;
  let valorMP = 0;
  let prefeTexto = "No especificada";
  let prefeIcono = "❓";
  let prefeColor = "#94a3b8"; // Gris por defecto
  let prefeBg = "#f8fafc";
  const obs = turno.obs_cancelacion || "";

  if (obs.includes("PREFIERE DEVOLUCIÓN EN:")) {
    // Si el cliente especificó desde su app, respetamos su decisión
    if (obs.includes("Efectivo")) {
      valorEfe = montoTotal;
      prefeTexto = "Efectivo en el local";
      prefeIcono = "💵";
      prefeColor = "#15803d";
      prefeBg = "#f0fdf4";
    } else {
      valorMP = montoTotal;
      prefeTexto = "Mercado Pago";
      prefeIcono = "📱";
      prefeColor = "#1d4ed8";
      prefeBg = "#eff6ff";
    }
  } else {
    // 💡 SUGERENCIA AUTOMÁTICA: Si no especificó, sugerimos según cómo entró la plata
    if (esPagoOnline) {
      valorMP = montoTotal;
      prefeTexto = "Mercado Pago";
      prefeIcono = "💳";
      prefeColor = "#1d4ed8";
      prefeBg = "#eff6ff";
    } else {
      valorEfe = montoTotal;
      prefeTexto = "Efectivo";
      prefeIcono = "💵";
      prefeColor = "#15803d";
      prefeBg = "#f0fdf4";
    }
  }

  const formatear = (n) => n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  await Swal.fire({
    title: '',
    width: '520px',
    background: '#ffffff',
    showCancelButton: true,
    confirmButtonText: 'Confirmar Devolución',
    confirmButtonColor: '#0ea5e9',
    cancelButtonText: 'Cerrar',
    html: `
      <div style="font-family: 'Inter', -apple-system, sans-serif; text-align: left; padding: 5px;">
        
        <div style="text-align: center; margin-bottom: 25px;">
          <div style="display: inline-block; padding: 8px 16px; background: #f0f9ff; border-radius: 30px; color: #0ea5e9; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">
            Gestión de Reintegro
          </div>
          <h2 style="margin: 0; font-size: 2.8rem; font-weight: 900; color: #0f172a; letter-spacing: -1.5px;">$${formatear(montoTotal)}</h2>
          <p style="margin: 5px 0 0 0; color: #64748b; font-size: 1rem; font-weight: 500;">Total a devolver a <b>${turno.cliente_nombre}</b></p>
        </div>

        <div style="margin-bottom: 25px;">
           <div style="background: ${prefeBg}; border: 1px solid ${prefeColor}33; padding: 15px; border-radius: 16px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);">
              <div>
                <span style="display: block; font-size: 0.65rem; text-transform: uppercase; color: ${prefeColor}; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 2px;">Método recomendado</span>
                <span style="font-size: 1.05rem; color: ${prefeColor}; font-weight: 700;">${prefeIcono} ${prefeTexto}</span>
              </div>
           </div>

           ${esPagoOnline ? `
           <div style="background: #0f172a; padding: 18px; border-radius: 16px; margin-top: 12px; position: relative; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
              <span style="display: block; font-size: 0.7rem; text-transform: uppercase; color: #94a3b8; font-weight: 800; margin-bottom: 8px; letter-spacing: 0.5px;">ID de Transacción Mercado Pago</span>
              <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; color: #38bdf8; font-weight: 800; letter-spacing: 1px;">${idMP}</span>
              </div>
           </div>
           ` : `
           `}
        </div>

        <div style="background: #ffffff; border: 2px solid #f1f5f9; padding: 20px; border-radius: 20px;">
          <h4 style="margin: 0 0 18px 0; font-size: 0.85rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">Confirmar Montos de Salida</h4>
          
          <div style="display: flex; flex-direction: column; gap: 15px;">
            <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; background: #f0fdf4; color: #16a34a; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem;">💵</div>
                <span style="font-weight: 700; color: #1e293b; font-size: 1rem;">Efectivo</span>
              </div>
              <div style="position: relative; width: 180px;">
                <span style="position: absolute; left: 14px; top: 12px; font-weight: 800; color: #94a3b8; font-size: 1.1rem;">$</span>
                <input id="val_efe" type="text" class="swal2-input" 
                       style="width: 100%; margin: 0; height: 50px; padding-left: 28px; font-size: 1.3rem; font-weight: 800; border-radius: 12px; border: 2px solid #e2e8f0; text-align: right; color: #0f172a;" 
                       value="${valorEfe > 0 ? formatear(valorEfe) : '0'}">
              </div>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; padding-top: 5px;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; background: #eff6ff; color: #2563eb; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem;">📱</div>
                <span style="font-weight: 700; color: #1e293b; font-size: 1rem;">Mercado Pago</span>
              </div>
              <div style="position: relative; width: 180px;">
                <span style="position: absolute; left: 14px; top: 12px; font-weight: 800; color: #94a3b8; font-size: 1.1rem;">$</span>
                <input id="val_mp" type="text" class="swal2-input" 
                       style="width: 100%; margin: 0; height: 50px; padding-left: 28px; font-size: 1.3rem; font-weight: 800; border-radius: 12px; border: 2px solid #e2e8f0; text-align: right; color: #0f172a;" 
                       value="${valorMP > 0 ? formatear(valorMP) : '0'}">
              </div>
            </div>
          </div>
        </div>

        <div id="val_status" style="margin-top: 20px; padding: 15px; border-radius: 14px; text-align: center; font-weight: 800; font-size: 0.95rem; transition: all 0.3s;"></div>
      </div>
    `,
    didOpen: () => {
      const inEfe = document.getElementById('val_efe');
      const inMP = document.getElementById('val_mp');
      const status = document.getElementById('val_status');
      const confirmBtn = Swal.getConfirmButton();

      confirmBtn.style.width = '100%';
      confirmBtn.style.height = '55px';
      confirmBtn.style.borderRadius = '14px';
      confirmBtn.style.fontSize = '1.1rem';
      confirmBtn.style.fontWeight = '800';
      confirmBtn.style.marginTop = '15px';
      confirmBtn.style.boxShadow = '0 10px 15px -3px rgba(14, 165, 233, 0.3)';

      const parse = (v) => parseFloat(v.replace(/\./g, '').replace(',', '.')) || 0;
      const mask = (i) => {
        let l = i.value.replace(/[^0-9,]/g, '');
        let p = l.split(',');
        if (p.length > 2) p = [p[0], p.slice(1).join('')];
        if (p[1]) p[1] = p[1].substring(0, 2);
        p[0] = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        i.value = p.join(',');
      };

      const validate = () => {
        const total = parse(inEfe.value) + parse(inMP.value);
        const diff = Math.abs(total - montoTotal);
        if (diff <= 0.01) {
          status.style.background = '#dcfce7'; status.style.color = '#15803d'; status.style.border = '1px solid #bbf7d0';
          status.innerHTML = '¡Listo! Los montos coinciden perfectamente';
          confirmBtn.disabled = false;
          confirmBtn.style.background = 'linear-gradient(135deg, #0ea5e9, #2563eb)';
        } else {
          status.style.background = '#fef2f2'; status.style.color = '#dc2626'; status.style.border = '1px solid #fecaca';
          status.innerHTML = `⚠️ Falta asignar $${formatear(Math.max(0, montoTotal - total))}`;
          confirmBtn.disabled = true;
          confirmBtn.style.background = '#cbd5e1';
          confirmBtn.style.boxShadow = 'none';
        }
      };

      inEfe.addEventListener('input', () => { mask(inEfe); validate(); });
      inMP.addEventListener('input', () => { mask(inMP); validate(); });
      inEfe.addEventListener('focus', () => inEfe.select());
      inMP.addEventListener('focus', () => inMP.select());
      validate();
    },
    preConfirm: () => {
      const vEfe = parseFloat(document.getElementById('val_efe').value.replace(/\./g, '').replace(',', '.')) || 0;
      const vMP = parseFloat(document.getElementById('val_mp').value.replace(/\./g, '').replace(',', '.')) || 0;
      return {
        monto_efectivo: vEfe,
        monto_mp: vMP,
        reembolso_api_mp: vMP > 0 && esPagoOnline
      };
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        Swal.fire({ 
          title: 'Procesando Reintegro', 
          html: '<div class="spinner-border text-info" role="status"></div><p style="margin-top:15px">Esto puede tomar unos segundos...</p>', 
          showConfirmButton: false,
          allowOutsideClick: false
        });
        const resp = await axios.post(`/api/turnos/${turno.id}/completar-reembolso-manual/`, result.value);
        await cargarTurnos();
        Swal.fire({
          icon: 'success',
          title: '¡Operación Exitosa!',
          text: resp.data.message,
          timer: 3000,
          showConfirmButton: false
        });
      } catch (e) {
        Swal.fire('Atención', e.response?.data?.error || 'No se pudo completar el reintegro.', 'error');
      }
    }
  });
};

const verDetalleTurno = async (turno) => {
  try {
    const response = await axios.get(`/api/turnos/${turno.id}/`);
    
    if (response.data && response.data.error) throw new Error(`Error: ${response.data.error}`);
    if (!response.data || !response.data.id) throw new Error('Error de datos');

    const turnoDetalle = response.data;

    let serviciosHTML = '';
    let totalDuracion = 0;
    let totalPrecio = 0;

    if (turnoDetalle.servicios && turnoDetalle.servicios.length > 0) {
      serviciosHTML = turnoDetalle.servicios.map(s => {
        // Vamos sumando para el total
        totalDuracion += (s.duracion || 0);
        totalPrecio += (parseFloat(s.precio) || 0);

        return `
        <tr style="border-bottom: 1px solid #f1f5f9;">
          <td style="padding: 12px; font-weight: 500; color: #1e293b; font-size: 0.95rem;">${s.nombre || 'Sin nombre'}</td>
          <td style="padding: 12px; text-align: right; color: #64748b; font-size: 0.9rem;">${s.duracion || 0}m</td>
          <td style="padding: 12px; text-align: right; font-weight: 700; color: #0f172a;">$${formatPrecio(s.precio || 0)}</td>
        </tr>
      `}).join('');

      // 🔥 AGREGAMOS LA FILA DE TOTAL AL FINAL DE LA TABLA
      if (turnoDetalle.servicios.length > 1) {
        serviciosHTML += `
          <tr style="background-color: #f8fafc; border-top: 2px solid #e2e8f0;">
            <td style="padding: 12px; font-weight: 800; color: #0f172a; font-size: 1rem;">TOTAL SERVICIOS</td>
            <td style="padding: 12px; text-align: right; color: #475569; font-weight: 700; font-size: 0.95rem;">${totalDuracion}m</td>
            <td style="padding: 12px; text-align: right; font-weight: 900; color: #0ea5e9; font-size: 1.1rem;">$${formatPrecio(totalPrecio)}</td>
          </tr>
        `;
      }
    } else {
      serviciosHTML = `<tr><td colspan="3" style="padding: 15px; text-align: center; color: #94a3b8;">Sin servicios detallados</td></tr>`;
    }

    const faltaPagar = calcularFaltaPagar(turnoDetalle);
    const montoAbonado = turnoDetalle.tipo_pago === 'TOTAL' ? turnoDetalle.monto_total : turnoDetalle.monto_seña;

    const medioPago = turnoDetalle.medio_pago || '';
    const entidadPago = turnoDetalle.entidad_pago || null;
    const transactionId = turnoDetalle.codigo_transaccion || turnoDetalle.mp_payment_id;

    Swal.fire({
      title: `<div style="display: flex; align-items: center; gap: 10px; color: #0f172a;">
                <span style="background: #0ea5e9; color: white; padding: 6px 14px; border-radius: 40px; font-size: 0.9rem; font-weight: 600;">Turno #${turnoDetalle.id}</span>
              </div>`,
      width: '800px',
      background: '#ffffff',
      showConfirmButton: false,
      showCloseButton: true,
      html: `
        <div style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: left;">

          <div style="display: flex; gap: 12px; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #f1f5f9;">
            <span class="badge-estado ${getEstadoClass(turnoDetalle.estado, turnoDetalle.tipo_pago)}" style="padding: 8px 16px; border-radius: 30px; font-weight: 700; font-size: 0.9rem;">
              ${getEstadoTexto(turnoDetalle.estado, turnoDetalle.tipo_pago)}
            </span>
            <span class="canal-badge ${(turnoDetalle.canal || 'PRESENCIAL').toLowerCase()}" style="padding: 8px 16px; border-radius: 30px; font-weight: 600; font-size: 0.9rem;">
              ${turnoDetalle.canal || 'PRESENCIAL'}
            </span>
          </div>

          ${turnoDetalle.estado === 'CANCELADO' ? `
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 16px; padding: 20px; margin-bottom: 25px; display: flex; flex-direction: column; gap: 10px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">🚫</span>
                <div>
                  <h4 style="margin: 0; color: #991b1b; font-size: 0.9rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Motivo de Cancelación</h4>
                  <span style="color: #7f1d1d; font-size: 1.2rem; font-weight: 800;">${turnoDetalle.motivo_cancelacion || 'No especificado'}</span>
                </div>
              </div>
              ${turnoDetalle.obs_cancelacion ? `
                <div style="background: white; border-radius: 10px; padding: 12px; color: #991b1b; font-size: 0.95rem; font-style: italic; border: 1px dashed #fca5a5;">
                  " ${turnoDetalle.obs_cancelacion} "
                </div>
              ` : ''}
            </div>
          ` : ''}

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;">
            <div style="background: #f8fafc; padding: 18px; border-radius: 16px; border: 1px solid #e2e8f0;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                <span style="font-size: 1.5rem;">👤</span>
                <span style="font-weight: 700; color: #334155;">Cliente</span>
              </div>
              <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a;">${turnoDetalle.cliente_nombre || 'Cliente'} ${turnoDetalle.cliente_apellido || ''}</div>
            </div>
            <div style="background: #f8fafc; padding: 18px; border-radius: 16px; border: 1px solid #e2e8f0;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                <span style="font-size: 1.5rem;">✂️</span>
                <span style="font-weight: 700; color: #334155;">Profesional</span>
              </div>
              <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a;">${turnoDetalle.peluquero_nombre || 'Profesional'}</div>
            </div>
          </div>

          <div style="margin-bottom: 25px;">
            <h4 style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 15px; letter-spacing: 0.5px;">
              <span style="font-size: 1.2rem;">📋</span> Detalle de Servicios
            </h4>
            <div style="border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden;">
              <table style="width: 100%; border-collapse: collapse;">
                <thead style="background: #f1f5f9;">
                  <tr>
                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #334155;">Servicio</th>
                    <th style="padding: 12px; text-align: right; font-weight: 600; color: #334155;">Duración</th>
                    <th style="padding: 12px; text-align: right; font-weight: 600; color: #334155;">Precio</th>
                  </tr>
                </thead>
                <tbody>
                  ${serviciosHTML}
                </tbody>
              </table>
            </div>
          </div>

          <div style="background: ${turnoDetalle.silla_nombre ? '#f0fdf4' : '#fef2f2'}; padding: 16px; border-radius: 16px; border: 1px solid ${turnoDetalle.silla_nombre ? '#bbf7d0' : '#fecaca'}; display: flex; align-items: center; gap: 15px; margin-bottom: 25px;">
            <span style="font-size: 2rem;">🪑</span>
            <div>
              <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: ${turnoDetalle.silla_nombre ? '#16a34a' : '#dc2626'};">Puesto de trabajo</span>
              <div style="font-size: 1.3rem; font-weight: 800; color: ${turnoDetalle.silla_nombre ? '#14532d' : '#7f1d1d'};">${turnoDetalle.silla_nombre || 'Pendiente de asignación'}</div>
            </div>
          </div>

          <div style="background: linear-gradient(145deg, #1e293b, #0f172a); padding: 24px; border-radius: 20px; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
              <h4 style="margin:0; font-size: 1rem; font-weight: 600; color: #94a3b8; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.4rem;">💰</span> Resumen de pago
              </h4>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
              <div>
                <span style="font-size: 0.8rem; color: #94a3b8;">Abonado</span>
                <div style="font-size: 2rem; font-weight: 800; color: #4ade80;">$${formatPrecio(montoAbonado || 0)}</div>
              </div>
              <div>
                <span style="font-size: 0.8rem; color: #94a3b8;">Pendiente</span>
                <div style="font-size: 2rem; font-weight: 800; color: ${faltaPagar > 0 ? '#fbbf24' : '#ffffff'};">$${formatPrecio(faltaPagar > 0 ? faltaPagar : 0)}</div>
              </div>
            </div>

            <div style="background: #0f172a; border-radius: 14px; padding: 16px; border: 1px solid #334155; margin-top: 10px;">
              
              <div style="margin-bottom: ${turnoDetalle.medio_pago_restante ? '12px' : '0'}; border-bottom: ${turnoDetalle.medio_pago_restante ? '1px solid #334155' : 'none'}; padding-bottom: ${turnoDetalle.medio_pago_restante ? '12px' : '0'};">
                <span style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 6px;">${turnoDetalle.medio_pago_restante ? '1er Pago (Seña)' : 'Pago Único / Seña'}</span>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                  <span style="font-size: 0.9rem; font-weight: 600; color: #e2e8f0; display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 1.2rem;">🏦</span> ${getMedioPagoTexto(medioPago, entidadPago)}
                  </span>
                  <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 700; background: #1e293b; padding: 4px 12px; border-radius: 40px; color: #a5f3fc; letter-spacing: 0.5px; margin-left: auto;">
                    ${transactionId || 'Sin Comprobante'}
                  </span>
                </div>
              </div>

              ${turnoDetalle.medio_pago_restante ? `
                <div style="margin-top: 12px;">
                  <span style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 6px;">2do Pago (Restante)</span>
                  <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="font-size: 0.9rem; font-weight: 600; color: #e2e8f0; display: flex; align-items: center; gap: 6px;">
                      <span style="font-size: 1.2rem;">🏦</span> ${getMedioPagoTexto(turnoDetalle.medio_pago_restante, turnoDetalle.entidad_pago_restante)}
                    </span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 700; background: #1e293b; padding: 4px 12px; border-radius: 40px; color: #a5f3fc; letter-spacing: 0.5px; margin-left: auto;">
                      ${turnoDetalle.codigo_transaccion_restante || 'Sin Comprobante'}
                    </span>
                  </div>
                </div>
              ` : ''}
              
            </div>
          </div>
        </div>
      `
    });
  } catch (error) {
    Swal.fire('Error', 'No se pudo cargar el detalle del turno.', 'error');
  }
};

// 🔥 FLUJO COMPLETAR MEJORADO – COBRO DE SALDO PENDIENTE
const completarTurno = async (turno) => {
  const total = parseFloat(turno.monto_total) || 0;
  const sena = parseFloat(turno.monto_seña) || 0;
  const diff = total - sena;

  if (diff > 0) {
    // --- CASE: HAY SALDO PENDIENTE → MODAL DE COBRO ---
    const { isConfirmed, value: formValues } = await Swal.fire({
      title: 'Saldo Pendiente',
      html: `
        <div style="text-align: left;">
          <div style="background: #f8fafc; padding: 15px; border-radius: 12px; margin-bottom: 20px;">
            <p><strong>Total del Turno:</strong> $${formatPrecio(total)}</p>
            <p><strong>Ya Pagado (Seña):</strong> $${formatPrecio(sena)}</p>
            <p style="font-size: 1.2rem; font-weight: 700; color: #f59e0b;"><strong>Saldo a Cobrar:</strong> $${formatPrecio(diff)}</p>
          </div>
          <label for="metodo_pago_saldo" style="display: block; font-weight: 600; margin-bottom: 8px; color: #1e293b;">
            Método de Pago para el Saldo
          </label>
          <select id="metodo_pago_saldo" class="swal2-input" style="width: 100%;">
            <option value="EFECTIVO">💵 Efectivo</option>
            <option value="MERCADO_PAGO">🔵 Mercado Pago</option>
            <option value="TRANSFERENCIA">🏦 Transferencia</option>
          </select>
        </div>
      `,
      showCancelButton: true,
      confirmButtonColor: '#10b981',
      confirmButtonText: 'Cobrar y Completar',
      cancelButtonText: 'Cancelar',
      preConfirm: () => {
        const metodo = document.getElementById('metodo_pago_saldo').value;
        if (!metodo) {
          Swal.showValidationMessage('Seleccione un método de pago');
          return false;
        }
        return { metodo_pago_saldo: metodo };
      }
    });

    if (isConfirmed && formValues) {
      try {
        await axios.post(`/api/turnos/${turno.id}/cambiar-estado/COMPLETADO/`, formValues);
        await cargarTurnos();
        Swal.fire('¡Turno completado!', 'El saldo pendiente fue cobrado.', 'success');
      } catch (error) {
        Swal.fire('Error', 'No se pudo completar el turno.', 'error');
      }
    }
  } else {
    // --- CASE: SIN SALDO PENDIENTE → CONFIRMACIÓN SIMPLE ---
    const { isConfirmed } = await Swal.fire({
      title: '¿Completar turno?',
      text: 'Marcar como completado.',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#10b981',
      confirmButtonText: 'Sí, completar'
    });

    if (isConfirmed) {
      try {
        await axios.post(`/api/turnos/${turno.id}/cambiar-estado/COMPLETADO/`);
        await cargarTurnos();
        Swal.fire('¡Turno completado!', '', 'success');
      } catch (error) {
        Swal.fire('Error', 'No se pudo completar el turno.', 'error');
      }
    }
  }
};

const limpiarFiltros = () => {
  filtros.value = { busqueda: '', peluquero: '', estado: '', canal: '', fechaDesde: '', fechaHasta: '', medioPago: '' }
  pagina.value = 1
  cargarTurnos()
}

const turnosFiltrados = computed(() => {
  let filtrados = turnos.value
  
  if (filtros.value.busqueda) {
    const busqueda = filtros.value.busqueda.toLowerCase().trim()
    
    filtrados = filtrados.filter(turno => {
      // 1. Buscamos por Nombres (con || '' para evitar undefined)
      // Nota: busco peluquero.apellido dentro del objeto peluquero ya que no está aplanado en el serializer
      const strCliente = `${turno.cliente_nombre || ''} ${turno.cliente_apellido || ''}`.toLowerCase()
      const strPeluquero = `${turno.peluquero_nombre || ''} ${turno.peluquero?.apellido || ''}`.toLowerCase()
      
      const matchNombres = strCliente.includes(busqueda) || strPeluquero.includes(busqueda)
      
      // 2. Buscamos por IDs (Turno, MercadoPago y Transacciones manuales)
      const matchId = turno.id ? String(turno.id).includes(busqueda) : false
      const matchMp = turno.mp_payment_id ? String(turno.mp_payment_id).includes(busqueda) : false
      const matchNroTrans = turno.nro_transaccion ? String(turno.nro_transaccion).includes(busqueda) : false
      const matchCodTrans = turno.codigo_transaccion ? String(turno.codigo_transaccion).toLowerCase().includes(busqueda) : false
      const matchCodRest = turno.codigo_transaccion_restante ? String(turno.codigo_transaccion_restante).toLowerCase().includes(busqueda) : false

      // Si encuentra coincidencia en ALGUNO de todos estos campos, lo muestra
      return matchNombres || matchId || matchMp || matchNroTrans || matchCodTrans || matchCodRest
    })
  }

  // Filtros fijos
  if (filtros.value.estado) filtrados = filtrados.filter(turno => turno.estado === filtros.value.estado)
  if (filtros.value.canal) filtrados = filtrados.filter(turno => turno.canal === filtros.value.canal)
  if (filtros.value.fechaDesde) filtrados = filtrados.filter(turno => turno.fecha >= filtros.value.fechaDesde)
  if (filtros.value.fechaHasta) filtrados = filtrados.filter(turno => turno.fecha <= filtros.value.fechaHasta)
  
  if (filtros.value.medioPago) {
    filtrados = filtrados.filter(turno => {
      const mp1 = (turno.medio_pago || '').toUpperCase()
      const mp2 = (turno.medio_pago_restante || '').toUpperCase()
      
      if (filtros.value.medioPago === 'MERCADO_PAGO') {
        return mp1.includes('MERCADO') || mp2.includes('MERCADO')
      } else if (filtros.value.medioPago === 'EFECTIVO') {
        return mp1.includes('EFECTIVO') || mp2.includes('EFECTIVO')
      } else if (filtros.value.medioPago === 'TRANSFERENCIA') {
        return mp1.includes('TRANSF') || mp2.includes('TRANSF')
      }
      return true
    })
  }
  
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
  return ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'PELUQUERO', 'PEL'].includes(userRol.value)
}

const puedeCancelarTurno = (turno) => {
  if (['COMPLETADO', 'CANCELADO'].includes(turno.estado)) return false
  return ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'PELUQUERO', 'PEL'].includes(userRol.value)
}

onMounted(async () => { 
  cargarTurnos() 
  if (esAdminORecep.value) {
    try {
      const res = await axios.get('/api/peluqueros/')
      listaPeluqueros.value = res.data || []
    } catch(e) { console.error('Error cargando peluqueros para el filtro', e) }
  }
})

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

/* 🔥 ESTILO PARA LA ETIQUETA DEL ID 🔥 */
.badge-id {
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  padding: 4px 8px;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  font-size: 0.8rem;
  border: 1px solid var(--border-color);
  display: inline-block;
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

.badge-reembolso-no-aplica {
  display: inline-flex;
  align-items: center;
  background: #2d817f; 
  color: #f8fafc; 
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #475569;
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

/* ESTILOS PARA EL NUEVO INDICADOR DE ESTADO DE PAGO */
.payment-status-badge {
  display: block;
  width: fit-content;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  white-space: nowrap;
}

.badge-pagado-total {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid #10b981;
}

.badge-saldo-pendiente {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid #f59e0b;
}

.badge-a-pagar {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
  border: 1px solid #ef4444;
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
  grid-template-columns: repeat(4, 1fr);
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
  padding: 0 18px; /* Ajustado el padding vertical porque le damos height fijo */
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.8px;
  display: flex;
  align-items: center;
  justify-content: center; 
  height: 42px; 
  width: 100%;
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

.action-button.edit { background: var(--bg-tertiary); border: 1px solid #0ea5e9; color: #0ea5e9; }
.action-button.edit:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4); border-color: #0ea5e9; }

.action-button.view { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); }
.action-button.view:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }

.action-button.reembolso { background: var(--bg-tertiary); border: 1px solid #f59e0b; color: #f59e0b; }
.action-button.reembolso:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4); border-color: #f59e0b; }

.action-button.pagar { background: var(--bg-tertiary); border: 1px solid #10b981; color: #10b981; }
.action-button.pagar:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4); border-color: #10b981; }

.action-button.complete { background: var(--bg-tertiary); border: 1px solid #10b981; color: #10b981; }
.action-button.complete:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4); border-color: #10b981; }

.action-button.delete { background: var(--bg-tertiary); border: 1px solid var(--error-color); color: var(--error-color); }
.action-button.delete:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4); border-color: var(--error-color); }

/* ESTADOS DE CARGA */
.no-results { text-align: center; padding: 80px; color: var(--text-secondary); }
.no-results-icon { margin-bottom: 15px; opacity: 0.5; color: var(--text-tertiary); }
.no-results p { margin: 0 0 8px 0; font-size: 1.1em; color: var(--text-primary); }

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
.btn-reintentar:hover { background: linear-gradient(135deg, #0284c7, #0369a1); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5); }

/* PAGINACIÓN */
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 25px; }
.pagination button {
  background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 800; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; font-size: 0.85rem; display: flex; align-items: center; gap: 8px;
}
.pagination button:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.pagination button:disabled { background: var(--bg-tertiary); color: var(--text-tertiary); cursor: not-allowed; transform: none; border: 1px solid var(--border-color); opacity: 0.5; }
.pagination span { color: var(--text-primary); font-weight: 700; letter-spacing: 0.8px; font-size: 0.95rem; }

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-card { padding: 25px; border-radius: 20px; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .header-content h1 { font-size: 1.6rem; }
@media (max-width: 1024px) {
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 600px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
}
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