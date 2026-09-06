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
                    <template v-if="turno.saldo_pendiente > 0">
                      ⚠️ FALTA COBRAR: ${{ formatPrecio(turno.saldo_pendiente) }}
                    </template>
                    <template v-else>
                      ✅ PAGADO TOTAL
                    </template>
                  </span>

                  <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 6px; font-weight: 500;">
                    <div>
                      {{ etiquetaMedioPagoCompacta(turno.medio_pago, turno.entidad_pago, turno.codigo_transaccion) }} · ${{ formatPrecio(turno.tipo_pago === 'SENA_50' ? (turno.monto_seña || 0) : (turno.monto_total || 0)) }}
                    </div>
                    <div v-if="desgloseMedioPagoCompacto(turno.medio_pago, turno.entidad_pago, turno.codigo_transaccion)" style="font-size: 0.8rem; opacity: 0.75; margin-top: 2px;">
                      {{ desgloseMedioPagoCompacto(turno.medio_pago, turno.entidad_pago, turno.codigo_transaccion) }}
                    </div>
                  </div>
                  <div style="font-size: 0.85rem; color: #94a3b8; opacity: 0.8;">
                    Total Turno: ${{ formatPrecio(turno.monto_total || 0) }}
                  </div>
                  <span v-if="turno.estado === 'CANCELADO' && turno.reembolso_estado === 'PENDIENTE' && turno.reembolso_alias" class="badge-alias-informado">@ Alias informado</span>
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
                  
                  <button v-if="esAdminORecep && esEstadoActivo(turno.estado) && turno.saldo_pendiente > 0" 
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

  <PagoQrModal
    v-if="qrSaldoAbierto"
    :init-point="qrSaldoInit"
    :monto="qrSaldoMonto"
    monto-label="Saldo pendiente a cobrar"
    :estado="qrSaldoEstado"
    boton-cancelar="Cancelar"
    boton-continuar="Listo"
    status-ok-sub="Cobro registrado"
    @cancelar="cerrarQrSaldo"
    @continuar="cerrarQrSaldo"
  />
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
import PagoQrModal from '@/components/PagoQrModal.vue'

const router = useRouter()

const qrSaldoAbierto = ref(false)
const qrSaldoInit = ref('')
const qrSaldoMonto = ref(0)
const qrSaldoEstado = ref('pending')
let pollIdSaldo = null

const abrirQrSaldo = async (turno, falta) => {
  try {
    const resp = await axios.post(`/api/turnos/${turno.id}/pagar-saldo/`, { metodo: 'MERCADO_PAGO' });
    const { init_point } = resp.data;
    let aprobado = false;

    qrSaldoInit.value = init_point;
    qrSaldoMonto.value = falta;
    qrSaldoEstado.value = 'pending';
    qrSaldoAbierto.value = true;

    if (pollIdSaldo) clearInterval(pollIdSaldo);
    pollIdSaldo = setInterval(async () => {
      try {
        const check = await axios.get(`/api/turnos/${turno.id}/`);
        if (check.data.medio_pago_restante === 'MERCADO_PAGO' || check.data.mp_payment_id_saldo) {
          aprobado = true;
          clearInterval(pollIdSaldo);
          pollIdSaldo = null;
          qrSaldoEstado.value = 'confirmed';
          setTimeout(() => {
            qrSaldoAbierto.value = false;
            Swal.fire('Pago registrado', `Cobro de $${formatPrecio(falta)} por QR Mercado Pago aprobado.`, 'success');
            cargarTurnos();
          }, 1200);
        }
      } catch (e) {}
    }, 1500);

    setTimeout(() => {
      if (!aprobado) {
        clearInterval(pollIdSaldo);
        pollIdSaldo = null;
        qrSaldoAbierto.value = false;
      }
    }, 900000);
  } catch (error) {
    Swal.fire('Error', error.response?.data?.error || 'No se pudo generar el pago.', 'error');
  }
};

const cerrarQrSaldo = () => {
  if (pollIdSaldo) {
    clearInterval(pollIdSaldo);
    pollIdSaldo = null;
  }
  qrSaldoAbierto.value = false;
};

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

const fechaHoyArgentina = () => {
  const hoy = new Date()
  const partes = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Argentina/Buenos_Aires',
    year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(hoy)
  const mapa = {}
  for (const p of partes) mapa[p.type] = p.value
  return `${mapa.year}-${mapa.month}-${mapa.day}`
}

const esTurnoPasado = (fecha) => {
  if (!fecha) return false
  return String(fecha) < fechaHoyArgentina()
}

const puedeEditarTurno = (turno) => {
  if (turno.estado !== 'RESERVADO') return false;
  if (esTurnoPasado(turno.fecha)) return false;
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

const labelMedioPago = (medioPago) => {
  if (!medioPago || medioPago === 'PENDIENTE') return 'Pendiente'
  const map = {
    'MERCADO_PAGO': 'Mercado Pago',
    'EFECTIVO': 'Efectivo',
    'MIXTO': 'Mixto',
  }
  return map[medioPago] || medioPago
}

const getSubtipoMP = (entidad) => {
  const e = String(entidad || '').toUpperCase()
  if (e === 'MERCADOPAGO_ALIAS') return 'Alias'
  if (e === 'MERCADOPAGO_QR') return 'QR'
  return null
}

const esCodigoMixto = (codigoTransaccion, entidadPago = null) => {
  if (String(entidadPago || '').toUpperCase() === 'MIXTO') return true
  const codigo = String(codigoTransaccion || '').trim()
  if (!codigo) return false
  const partes = codigo.split('|')
  if (partes.length < 2) return false
  return partes.every(p => /^[A-Z_]+:\d+(\.\d+)?$/.test(p))
}

const parsePartePago = (parte) => {
  const idx = String(parte).indexOf(':')
  const medio = idx > -1 ? String(parte).slice(0, idx) : String(parte)
  const monto = idx > -1 ? parseFloat(String(parte).slice(idx + 1)) : 0
  let etiqueta = labelMedioPago(medio)
  const subtipo = getSubtipoMP(medio)
  if (subtipo && etiqueta === 'Mercado Pago') etiqueta += ` (${subtipo})`
  return { medio, etiqueta, monto: isNaN(monto) ? 0 : monto }
}

const formatearMedioPagoTurno = (medioPago, entidadPago = null, codigoTransaccion = null) => {
  const codigo = String(codigoTransaccion || '').trim()
  if (esCodigoMixto(codigoTransaccion, entidadPago) && codigo.includes('|')) {
    const detalle = codigo.split('|').map(parsePartePago)
    return 'Mixto: ' + detalle.map(p => `${p.etiqueta} $${formatPrecio(p.monto)}`).join(' + ')
  }
  let etiqueta = labelMedioPago(medioPago)
  if (etiqueta === 'Mercado Pago') {
    const subtipo = getSubtipoMP(entidadPago)
    if (subtipo) etiqueta += ` (${subtipo})`
  }
  return etiqueta
}

const desglosarMedioPagoTurno = (medioPago, entidadPago = null, codigoTransaccion = null) => {
  const codigo = String(codigoTransaccion || '').trim()
  if (esCodigoMixto(codigoTransaccion, entidadPago) && codigo.includes('|')) {
    return { mixto: true, partes: codigo.split('|').map(parsePartePago) }
  }
  return { mixto: false, etiqueta: formatearMedioPagoTurno(medioPago, entidadPago, codigoTransaccion) }
}

const etiquetaMedioPagoCompacta = (medioPago, entidadPago = null, codigoTransaccion = null) => {
  const codigo = String(codigoTransaccion || '').trim()
  if (esCodigoMixto(codigoTransaccion, entidadPago) && codigo.includes('|')) return 'Mixto'
  return formatearMedioPagoTurno(medioPago, entidadPago, codigoTransaccion)
}

const desgloseMedioPagoCompacto = (medioPago, entidadPago = null, codigoTransaccion = null) => {
  const codigo = String(codigoTransaccion || '').trim()
  if (!(esCodigoMixto(codigoTransaccion, entidadPago) && codigo.includes('|'))) return ''
  return codigo.split('|').map((parte) => {
    const { medio, monto } = parsePartePago(parte)
    const base = String(medio).startsWith('MERCADOPAGO') ? 'MP' : labelMedioPago(medio)
    const subtipo = getSubtipoMP(medio)
    return `${base}${subtipo === 'QR' ? ' (QR)' : ''} $${formatPrecio(monto)}`
  }).join(' · ')
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

// Un ID real de Mercado Pago SOLO proviene de mp_payment_id o mp_payment_id_saldo.
// Nunca de codigo_transaccion ni de comprobantes manuales de Alias.
const esIdMPReal = (turno) => {
  const paymentId = String(turno.mp_payment_id || turno.mp_payment_id_saldo || '').trim()
  if (!paymentId || paymentId === 'None') return false
  const entidad = String(turno.entidad_pago || '').toUpperCase()
  // Presencial Alias puro: el cajero guardó el comprobante manual en mp_payment_id → NO es un ID real
  if (entidad === 'MERCADOPAGO') return false
  const desglose = desglosarMedioPagoTurno(turno.medio_pago, turno.entidad_pago, turno.codigo_transaccion)
  if (desglose.mixto) {
    const parteMP = desglose.partes.find((p) => String(p.medio).startsWith('MERCADOPAGO'))
    if (!parteMP) return false
    return getSubtipoMP(parteMP.medio) === 'QR'
  }
  return true
}

const esOrigenAlias = (turno) => {
  if (String(turno.entidad_pago || '').toUpperCase() === 'MERCADOPAGO') return true
  const desglose = desglosarMedioPagoTurno(turno.medio_pago, turno.entidad_pago, turno.codigo_transaccion)
  if (desglose.mixto) {
    return desglose.partes.some((p) => getSubtipoMP(p.medio) === 'Alias')
  }
  return false
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
        const raw = resConfig.data && resConfig.data.margen_horas_cancelacion;
        if (typeof raw === 'number') {
            margenConfig = raw;
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

    // Clientes interesados (Avisame) para este horario: aviso visual informativo
    let cantidadInteresados = 0;
    try {
      const resInt = await axios.get(`/api/turnos/${turno.id}/interesados/`);
      cantidadInteresados = parseInt(resInt.data?.cantidad, 10) || 0;
    } catch (err) {
      console.error('Error al consultar clientes interesados del turno', err);
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

          ${cantidadInteresados > 0 ? `
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 14px 15px; margin-bottom: 18px; display: flex; gap: 12px; align-items: flex-start; text-align: left;">
              <span style="font-size: 1.3rem; line-height: 1; margin-top: 1px;">ℹ️</span>
              <span style="color: #1e3a8a; font-size: 0.88rem; line-height: 1.45; font-weight: 500;">
                Este turno está vinculado a <b>${cantidadInteresados}</b> ${cantidadInteresados === 1 ? 'cliente interesado' : 'clientes interesados'}. Al cancelarlo, se notificará a los clientes interesados sobre la disponibilidad del horario.
              </span>
            </div>
          ` : ''}

          ${hayReembolso ? `
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 15px; margin-bottom: 20px; display: flex; gap: 15px; align-items: flex-start; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
              <span style="font-size: 1.5rem;">✅</span>
              <div>
                <strong style="color: #166534; font-size: 0.95rem; display: block; margin-bottom: 4px;">Reembolso a favor del cliente</strong>
                <span style="color: #15803d; font-size: 0.85rem; line-height: 1.4; display: block;">
                  Se generará un <b>reembolso pendiente de $${formatPrecio(montoTotal)}</b> porque cancela con ${Math.floor(horasFaltantes)}hs de anticipación.
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

  const { isConfirmed, value: metodo } = await Swal.fire({
    title: 'Cobrar Restante',
    html: `
      <div style="background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Monto a cobrar</p>
        <p style="margin: 5px 0 0 0; color: #10b981; font-size: 1.8rem; font-weight: 800;">$${formatPrecio(falta)}</p>
      </div>
      <div style="text-align: left;">
        <label style="display: block; font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 5px;">Medio de Pago</label>
        <select id="medio_pago" class="swal2-input" style="width: 100%; margin: 0; height: 42px; font-size: 0.9rem;">
          <option value="EFECTIVO" selected>Efectivo</option>
          <option value="MERCADO_PAGO">Mercado Pago</option>
        </select>
      </div>
    `,
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Continuar',
    cancelButtonText: 'Cancelar',
    preConfirm: () => {
      return document.getElementById('medio_pago').value;
    }
  });

  if (!isConfirmed || !metodo) return;

  if (metodo === 'EFECTIVO') {
    try {
      await axios.post(`/api/turnos/${turno.id}/pagar-saldo/`, { metodo: 'EFECTIVO' });
      await cargarTurnos();
      Swal.fire('Pago registrado', `Cobro de $${formatPrecio(falta)} en efectivo registrado.`, 'success');
    } catch (error) {
      Swal.fire('Error', error.response?.data?.error || 'No se pudo registrar el pago.', 'error');
    }
    return;
  }

  // MERCADO_PAGO: elegir entre QR o Alias
  const { isConfirmed: subConfirmed, value: subMetodo } = await Swal.fire({
    title: 'Cobrar con Mercado Pago',
    html: `
      <div style="background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Monto a cobrar</p>
        <p style="margin: 5px 0 0 0; color: #10b981; font-size: 1.8rem; font-weight: 800;">$${formatPrecio(falta)}</p>
      </div>
      <div style="text-align: left;">
        <label style="display: block; font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 8px;">Elegí cómo cobrar:</label>
        <label style="display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: #f0f9ff; border: 2px solid #bae6fd; border-radius: 10px; margin-bottom: 8px; cursor: pointer;">
          <input type="radio" name="sub_mp" value="QR" checked style="width: 18px; height: 18px; accent-color: #0ea5e9;">
          <div>
            <span style="font-weight: 600; color: #0f172a; font-size: 0.95rem;">Código QR</span>
            <span style="display: block; font-size: 0.75rem; color: #64748b;">Cliente escanea con la app de MP o cámara — pago automático</span>
          </div>
        </label>
        <label style="display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: #fefce8; border: 2px solid #fde68a; border-radius: 10px; cursor: pointer;">
          <input type="radio" name="sub_mp" value="ALIAS" style="width: 18px; height: 18px; accent-color: #eab308;">
          <div>
            <span style="font-weight: 600; color: #0f172a; font-size: 0.95rem;">Transferencia por Alias</span>
            <span style="display: block; font-size: 0.75rem; color: #64748b;">Cliente transfiere por alias y admin confirma manualmente</span>
          </div>
        </label>
      </div>
    `,
    showCancelButton: true,
    confirmButtonColor: '#0ea5e9',
    confirmButtonText: 'Continuar',
    cancelButtonText: 'Cancelar',
    preConfirm: () => {
      const sel = document.querySelector('input[name="sub_mp"]:checked');
      return sel ? sel.value : null;
    }
  });

  if (!subConfirmed || !subMetodo) return;

  if (subMetodo === 'QR') {
    await abrirQrSaldo(turno, falta);
  } else {
    // Alias: mostrar alias y botón para marcar como pagado
    try {
      const aliasResp = await axios.get('/api/configuracion-local/');
      const alias = aliasResp.data?.mp_alias || 'No configurado';

      const { isConfirmed: aliasConfirmed } = await Swal.fire({
        title: 'Transferencia por Alias',
        html: `
          <div style="text-align: center;">
            <div style="background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 16px;">
              <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Monto a cobrar</p>
              <p style="margin: 5px 0 0 0; color: #10b981; font-size: 1.8rem; font-weight: 800;">$${formatPrecio(falta)}</p>
            </div>
            <p style="color: #334155; font-size: 0.95rem; margin: 0 0 4px;">Pedile al cliente que transfiera al alias:</p>
            <div style="background: #0f172a; color: #a5f3fc; font-size: 1.3rem; font-weight: 800; padding: 12px 20px; border-radius: 10px; letter-spacing: 1px; font-family: monospace; display: inline-block; margin: 8px 0 16px;">
              ${alias}
            </div>
          </div>
        `,
        showCancelButton: true,
        confirmButtonColor: '#10b981',
        confirmButtonText: 'Ya me transfirió',
        cancelButtonText: 'Cancelar',
        cancelButtonColor: '#94a3b8',
        allowOutsideClick: false
      });

      if (aliasConfirmed) {
        await axios.post(`/api/turnos/${turno.id}/pagar-saldo/`, { metodo: 'ALIAS' });
        await cargarTurnos();
        Swal.fire('Pago registrado', `Cobro de $${formatPrecio(falta)} por alias MP registrado.`, 'success');
      }
    } catch (error) {
      Swal.fire('Error', error.response?.data?.error || 'No se pudo registrar el pago.', 'error');
    }
  }
}

const gestionarReembolsoManual = async (turno) => {
  const montoTotal = calcularMontoReembolso(turno);

  // 1. ID REAL de Mercado Pago: solo desde mp_payment_id / mp_payment_id_saldo.
  //    Nunca codigo_transaccion ni comprobantes manuales de Alias.
  const paymentIdReal = String(turno.mp_payment_id || turno.mp_payment_id_saldo || '').trim();
  const hasIdReal = esIdMPReal(turno) && paymentIdReal && paymentIdReal !== 'None';
  const esAliasOrigen = esOrigenAlias(turno);

  const desglose = desglosarMedioPagoTurno(turno.medio_pago, turno.entidad_pago, turno.codigo_transaccion);
  const partesMixto = desglose.mixto ? desglose.partes : null;

  // Íconos SVG (los mismos que usa la app: lucide)
  const icEfectivo = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>`;
  const icMP = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg>`;
  const icDesglose = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>`;
  const icRotate = `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>`;
  const icAt = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/></svg>`;
  const icCheck = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>`;
  const icAlert = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>`;
  const icX = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>`;
  const icTrash = `<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>`;
  

  // 2. Lógica de Preferencia e Inteligencia de sugerencia (SOLO sugiere/precarga, no restringe)
  let valorEfe = 0;
  let valorMP = 0;
  let prefeTexto = "No especificada";
  let prefeIcono = "";
  let prefeColor = "#94a3b8"; // Gris por defecto
  const obs = turno.obs_cancelacion || "";

  if (obs.includes("PREFIERE DEVOLUCIÓN EN:")) {
    // Si el cliente especificó desde su app, respetamos su decisión
    if (obs.includes("Efectivo")) {
      valorEfe = montoTotal;
      prefeTexto = "Efectivo en el local";
      prefeIcono = icEfectivo;
      prefeColor = "#15803d";
    } else {
      valorMP = montoTotal;
      prefeTexto = "Mercado Pago";
      prefeIcono = icMP;
      prefeColor = "#1d4ed8";
    }
  } else if (partesMixto) {
    // Prefill = desglose original (editable, no es una restricción)
    const parteEfe = partesMixto.find(p => String(p.medio) === 'EFECTIVO');
    const parteMP = partesMixto.find(p => String(p.medio).startsWith('MERCADOPAGO'));
    valorEfe = parteEfe ? parteEfe.monto : 0;
    valorMP = parteMP ? parteMP.monto : 0;
    if (Math.abs((valorEfe + valorMP) - montoTotal) > 0.01) {
      valorEfe = Math.max(0, montoTotal - valorMP);
    }
    prefeTexto = "Según desglose original";
    prefeIcono = icDesglose;
    prefeColor = "#475569";
  } else if (hasIdReal) {
    valorMP = montoTotal;
    prefeTexto = "Mercado Pago";
    prefeIcono = icMP;
    prefeColor = "#1d4ed8";
  } else if (String(turno.medio_pago || '').toUpperCase() === 'MERCADO_PAGO' || esAliasOrigen) {
    valorMP = montoTotal;
    prefeTexto = "Mercado Pago (manual - transferencia)";
    prefeIcono = icMP;
    prefeColor = "#1d4ed8";
  } else {
    valorEfe = montoTotal;
    prefeTexto = "Efectivo";
    prefeIcono = icEfectivo;
    prefeColor = "#15803d";
  }

  const formatear = (n) => n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  // 3. Pago original (secundario) y ayuda contextual (nunca el string crudo del desglose como ID)
  let panelOrigenHTML = '';
  let panelAyudaHTML = '';

  if (partesMixto) {
    panelOrigenHTML = `
    <div style="background: #ffffff; border: 1px solid #eef2f7; border-radius: 12px; padding: 13px 15px;">
      <div style="font-size: 0.66rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Pago original · desglose</div>
      ${partesMixto.map((p) => `
      <div style="display: flex; align-items: center; gap: 9px; padding: 6px 0;">
        <span style="width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: ${String(p.medio).startsWith('MERCADOPAGO') ? '#dbeafe' : '#d1fae5'}; color: ${String(p.medio).startsWith('MERCADOPAGO') ? '#1d4ed8' : '#15803d'};">${String(p.medio).startsWith('MERCADOPAGO') ? icMP : icEfectivo}</span>
        <span style="font-size: 0.82rem; color: #334155; font-weight: 600; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${p.etiqueta}</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #0f172a; font-weight: 700;">$${formatear(p.monto)}</span>
      </div>`).join('')}
      ${hasIdReal ? `
      <div style="display: flex; align-items: center; gap: 9px; margin-top: 6px; padding-top: 6px; border-top: 1px dashed #e2e8f0;">
        <span style="width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #dbeafe; color: #1d4ed8;">${icMP}</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #0f172a; font-weight: 700; letter-spacing: 0.3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${paymentIdReal}</span>
      </div>` : ''}
    </div>`;
  } else if (hasIdReal && paymentIdReal) {
    panelOrigenHTML = `
    <div style="background: #ffffff; border: 1px solid #eef2f7; border-radius: 12px; padding: 14px 15px;">
      <div style="font-size: 0.66rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Pago original</div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #dbeafe; color: #1d4ed8;">${icMP}</span>
        <div style="min-width: 0;">
          <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; color: #0f172a; font-weight: 700; letter-spacing: 0.3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${paymentIdReal}</div>
          <div style="font-size: 0.66rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 3px;">Mercado Pago</div>
        </div>
      </div>
      <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 10px; line-height: 1.45;">Buscá este ID en Mercado Pago para hacer la devolución manual.</div>
    </div>`;
  } else if (esAliasOrigen && !partesMixto) {
    panelOrigenHTML = `
    <div style="background: #ffffff; border: 1px solid #eef2f7; border-radius: 12px; padding: 14px 15px;">
      <div style="font-size: 0.66rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Pago original</div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #dbeafe; color: #1d4ed8;">${icAt}</span>
        <span style="font-size: 0.86rem; color: #334155; font-weight: 600; line-height: 1.45;">Se devuelve mediante transferencia manual a un Alias.</span>
      </div>
    </div>`;
  } else {
    panelOrigenHTML = `
    <div style="background: #ffffff; border: 1px solid #eef2f7; border-radius: 12px; padding: 14px 15px;">
      <div style="font-size: 0.66rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Pago original</div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #d1fae5; color: #15803d;">${icEfectivo}</span>
        <span style="font-size: 0.86rem; color: #334155; font-weight: 600;">El pago original fue en efectivo.</span>
      </div>
    </div>`;
  }

  await Swal.fire({
    title: '',
    width: '720px',
    background: '#ffffff',
    showCancelButton: true,
    confirmButtonText: 'Confirmar Devolución',
    confirmButtonColor: '#0ea5e9',
    cancelButtonText: 'Cerrar',
    html: `
      <div style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: left;">

        <div style="display: flex; align-items: flex-start; gap: 16px; padding: 4px 2px 0;">
          <span style="width: 54px; height: 54px; border-radius: 17px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(160deg, #dbeafe, #bfdbfe); color: #1d4ed8; box-shadow: inset 0 0 0 1px rgba(29, 78, 216, 0.08);">${icRotate}</span>
          <div style="flex: 1; min-width: 0; padding-top: 1px;">
            <div style="font-size: 0.68rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.4px;">Gestión de Reintegro</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; line-height: 1.15; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${turno.cliente_nombre || 'Cliente'} ${turno.cliente_apellido || ''}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">Devolución sobre el turno #${turno.id}</div>
          </div>
          <div style="text-align: right; flex-shrink: 0; padding-top: 2px;">
            <div style="font-size: 0.66rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.1px; margin-bottom: 4px;">A devolver</div>
            <div style="font-size: 2rem; font-weight: 800; color: #0f172a; letter-spacing: -1px; line-height: 1;">$${formatear(montoTotal)}</div>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 10px; background: #f8fafc; border: 1px solid #eef2f7; border-radius: 12px; padding: 10px 14px; margin-top: 18px;">
          <span style="width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #ffffff; color: ${prefeColor}; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);">${prefeIcono ? prefeIcono : icDesglose}</span>
          <span style="font-size: 0.68rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px;">Sugerido</span>
          <span style="font-size: 0.92rem; font-weight: 700; color: #334155; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${prefeTexto}</span>
          <span style="flex: 1; height: 1px; background: #eef2f7;"></span>
          <span style="font-size: 0.7rem; color: #cbd5e1; font-weight: 700; white-space: nowrap;">Podés cambiarlo</span>
        </div>

        <div style="display: flex; align-items: center; gap: 10px; margin: 20px 0 12px;">
          <span style="width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #e0f2fe; color: #0284c7;">${icDesglose}</span>
          <span style="font-size: 0.76rem; font-weight: 800; color: #334155; text-transform: uppercase; letter-spacing: 0.8px;">Método de devolución</span>
          <span style="flex: 1; height: 1px; background: #eef2f7;"></span>
          <span id="mixto_hint" style="font-size: 0.7rem; font-weight: 600; color: #94a3b8;">Podés dividir el total</span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
          <div id="opt_efe" style="border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 14px; background: #ffffff; transition: border-color 0.2s, background 0.2s;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="width: 38px; height: 38px; border-radius: 11px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #d1fae5; color: #15803d;">${icEfectivo}</span>
              <div style="flex: 1; min-width: 0;">
                <div style="font-size: 0.92rem; font-weight: 800; color: #0f172a;">Efectivo</div>
                <div id="sub_efe" style="font-size: 0.7rem; color: #94a3b8; margin-top: 1px;">Devolución en el local</div>
              </div>
              <span id="dot_efe" style="width: 22px; height: 22px; border-radius: 50%; border: 2px solid #e2e8f0; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; color: #ffffff; transition: all 0.2s;"></span>
              <button id="del_efe" type="button" title="Limpiar importe de Efectivo" style="width: 26px; height: 26px; border-radius: 8px; border: 1px solid #fecaca; background: #fef2f2; color: #ef4444; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; padding: 0; margin-left: 1px; box-shadow: none;">${icTrash}</button>
            </div>
            <div id="wrap_efe" style="display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 11px; margin-top: 12px; transition: border-color 0.2s;">
              <span style="font-size: 1rem; font-weight: 700; color: #94a3b8; padding-left: 11px; line-height: 1;">$</span>
              <input id="val_efe" type="text" class="swal2-input"
                     style="flex: 1; min-width: 0; margin: 0; height: 44px; border: 0; background: transparent; font-size: 1.05rem; font-weight: 800; text-align: right; padding: 0 12px; color: #0f172a; box-sizing: border-box;"
                     value="${valorEfe > 0 ? formatear(valorEfe) : '0'}">
            </div>
          </div>

          <div id="opt_mp" style="border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 14px; background: #ffffff; transition: border-color 0.2s, background 0.2s;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="width: 38px; height: 38px; border-radius: 11px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #dbeafe; color: #1d4ed8;">${icMP}</span>
              <div style="flex: 1; min-width: 0;">
                <div style="font-size: 0.92rem; font-weight: 800; color: #0f172a;">Mercado Pago</div>
                <div id="sub_mp" style="font-size: 0.7rem; color: #94a3b8; margin-top: 1px;">Transferencia manual</div>
              </div>
              <span id="dot_mp" style="width: 22px; height: 22px; border-radius: 50%; border: 2px solid #e2e8f0; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; color: #ffffff; transition: all 0.2s;"></span>
              <button id="del_mp" type="button" title="Limpiar importe de Mercado Pago" style="width: 26px; height: 26px; border-radius: 8px; border: 1px solid #fecaca; background: #fef2f2; color: #ef4444; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; padding: 0; margin-left: 1px; box-shadow: none;">${icTrash}</button>
            </div>
            <div id="wrap_mp" style="display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 11px; margin-top: 12px; transition: border-color 0.2s;">
              <span style="font-size: 1rem; font-weight: 700; color: #94a3b8; padding-left: 11px; line-height: 1;">$</span>
              <input id="val_mp" type="text" class="swal2-input"
                     style="flex: 1; min-width: 0; margin: 0; height: 44px; border: 0; background: transparent; font-size: 1.05rem; font-weight: 800; text-align: right; padding: 0 12px; color: #0f172a; box-sizing: border-box;"
                     value="${valorMP > 0 ? formatear(valorMP) : '0'}">
            </div>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px;">
          <div style="background: #f8fafc; border: 1px solid #eef2f7; border-radius: 14px; padding: 12px 14px;">
            <div style="font-size: 0.62rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.9px;">Total a devolver</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 800; color: #0f172a; margin-top: 4px;">$${formatear(montoTotal)}</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #eef2f7; border-radius: 14px; padding: 12px 14px;">
            <div style="font-size: 0.62rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.9px;">Asignado</div>
            <div id="res_asignado" style="font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 800; color: #0ea5e9; margin-top: 4px;">$${formatear(Math.round((valorEfe + valorMP) * 100) / 100)}</div>
          </div>
          <div id="res_falta_card" style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 14px; padding: 12px 14px; transition: background 0.2s, border-color 0.2s;">
            <div id="res_falta_lbl" style="font-size: 0.62rem; font-weight: 800; color: #b45309; text-transform: uppercase; letter-spacing: 0.9px;">Falta por asignar</div>
            <div id="res_falta" style="font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 800; color: #b45309; margin-top: 4px;">$${formatear(Math.max(0, Math.round((montoTotal - valorEfe - valorMP) * 100) / 100))}</div>
          </div>
        </div>

        <div id="mp_manual_fields" style="display: none; margin-top: 12px; border: 1px solid #bfdbfe; background: #f0f7ff; border-radius: 12px; padding: 13px 14px;">
          <div style="display: flex; align-items: center; gap: 9px;">
            <span style="width: 28px; height: 28px; border-radius: 9px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #dbeafe; color: #1d4ed8;"><span style="display: flex;">${icAt}</span></span>
            <span style="font-size: 0.8rem; font-weight: 800; color: #1e3a8a;">Alias para devolución</span>
            <span style="font-size: 0.62rem; color: #dc2626; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-left: auto;">Requerido</span>
          </div>
          <input id="reembolso_alias" type="text" class="swal2-input"
                 style="width: 100%; margin: 9px 0 0; height: 44px; border-radius: 11px; font-size: 0.95rem; padding: 0 12px; border: 1px solid #dbeafe; background: #ffffff; box-sizing: border-box; transition: border-color 0.2s;"
                 placeholder="ej: peluqueria.alias"
                 value="${String(turno.reembolso_alias || '').trim()}">
          <div style="font-size: 0.7rem; color: #64748b; margin-top: 6px;">Alias del cliente al que se transferirá el reembolso. Si fue informado al cancelar, ya está precargado y podés editarlo.</div>
        </div>

        <div style="display: grid; grid-template-columns: ${panelAyudaHTML ? '1fr 1fr' : '1fr'}; gap: 12px; margin-top: 14px;">
          ${panelOrigenHTML}
          ${panelAyudaHTML}
        </div>

        <div id="val_status" style="display: flex; align-items: center; justify-content: center; gap: 8px; border-radius: 14px; padding: 12px 14px; font-size: 0.88rem; font-weight: 600; min-height: 46px; transition: all 0.25s; border: 1px solid transparent; margin-top: 14px;"></div>
      </div>
    `,
didOpen: () => {
      const inEfe = document.getElementById('val_efe');
      const inMP = document.getElementById('val_mp');
      const status = document.getElementById('val_status');
      const confirmBtn = Swal.getConfirmButton();
      const cancelBtn = Swal.getCancelButton();
      const optEfe = document.getElementById('opt_efe');
      const optMP = document.getElementById('opt_mp');
      const dotEfe = document.getElementById('dot_efe');
      const dotMP = document.getElementById('dot_mp');
      const wrapEfe = document.getElementById('wrap_efe');
      const wrapMP = document.getElementById('wrap_mp');

      confirmBtn.style.width = '100%';
      confirmBtn.style.height = '55px';
      confirmBtn.style.borderRadius = '14px';
      confirmBtn.style.fontSize = '1.1rem';
      confirmBtn.style.fontWeight = '800';
      confirmBtn.style.marginTop = '16px';
      confirmBtn.style.boxShadow = '0 10px 15px -3px rgba(14, 165, 233, 0.3)';

      if (cancelBtn) {
        cancelBtn.style.width = '100%';
        cancelBtn.style.height = '55px';
        cancelBtn.style.borderRadius = '14px';
        cancelBtn.style.fontSize = '1.02rem';
        cancelBtn.style.fontWeight = '700';
        cancelBtn.style.background = '#ffffff';
        cancelBtn.style.color = '#64748b';
        cancelBtn.style.border = '1.5px solid #e2e8f0';
        cancelBtn.style.marginTop = '10px';
        cancelBtn.style.boxShadow = 'none';
      }

      const parse = (v) => parseFloat(v.replace(/\./g, '').replace(',', '.')) || 0;
      const mask = (i) => {
        let l = i.value.replace(/[^0-9,]/g, '');
        let p = l.split(',');
        if (p.length > 2) p = [p[0], p.slice(1).join('')];
        if (p[1]) p[1] = p[1].substring(0, 2);
        p[0] = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        i.value = p.join(',');
      };

      const manualFields = document.getElementById('mp_manual_fields');

      const pintarSeleccion = () => {
        const vE = parse(inEfe.value);
        const vM = parse(inMP.value);
        const onE = vE > 0;
        const onM = vM > 0;
        if (optEfe) {
          optEfe.style.borderColor = onE ? '#059669' : '#e2e8f0';
          optEfe.style.background = onE ? '#f0fdf9' : '#ffffff';
        }
        if (optMP) {
          optMP.style.borderColor = onM ? '#2563eb' : '#e2e8f0';
          optMP.style.background = onM ? '#eff6ff' : '#ffffff';
        }
        if (dotEfe) {
          dotEfe.style.borderColor = onE ? '#059669' : '#e2e8f0';
          dotEfe.style.background = onE ? '#059669' : '#ffffff';
          dotEfe.innerHTML = onE ? `<span style="display: flex;">${icCheck}</span>` : '';
        }
        if (dotMP) {
          dotMP.style.borderColor = onM ? '#2563eb' : '#e2e8f0';
          dotMP.style.background = onM ? '#2563eb' : '#ffffff';
          dotMP.innerHTML = onM ? `<span style="display: flex;">${icCheck}</span>` : '';
        }
      };

      const pintar = () => {
        const vMP = parse(inMP.value);
        if (manualFields) {
          manualFields.style.display = (!hasIdReal && vMP > 0) ? 'block' : 'none';
        }
      };

      const pintarResumen = () => {
        const asignado = parse(inEfe.value) + parse(inMP.value);
        const diff = Math.round((asignado - montoTotal) * 100) / 100;
        const resAsignado = document.getElementById('res_asignado');
        const resFalta = document.getElementById('res_falta');
        const resFaltaCard = document.getElementById('res_falta_card');
        const resFaltaLbl = document.getElementById('res_falta_lbl');
        if (resAsignado) resAsignado.textContent = `$${formatear(asignado)}`;
        if (resFalta && resFaltaCard && resFaltaLbl) {
          let estado, valor, colorTexto, fondo, borde;
          if (Math.abs(diff) <= 0.01) {
            estado = 'Importe correcto';
            valor = formatear(0);
            colorTexto = '#047857'; fondo = '#ecfdf5'; borde = '#a7f3d0';
          } else if (diff > 0) {
            estado = 'Excedente';
            valor = formatear(diff);
            colorTexto = '#dc2626'; fondo = '#fef2f2'; borde = '#fecaca';
          } else {
            estado = 'Falta por asignar';
            valor = formatear(Math.abs(diff));
            colorTexto = '#b45309'; fondo = '#fffbeb'; borde = '#fde68a';
          }
          resFaltaLbl.textContent = estado;
          resFaltaLbl.style.color = colorTexto;
          resFalta.textContent = `$${valor}`;
          resFalta.style.color = colorTexto;
          resFaltaCard.style.background = fondo;
          resFaltaCard.style.borderColor = borde;
        }
      };

      const validate = () => {
        pintarSeleccion();
        pintarResumen();
        const vMP = parse(inMP.value);
        const total = parse(inEfe.value) + vMP;
        const diff = total - montoTotal;
        const alias = document.getElementById('reembolso_alias')?.value.trim() || '';
        const faltaAlias = vMP > 0 && !hasIdReal && !alias;
        const mixtoHint = document.getElementById('mixto_hint');
        const esMixto = parse(inEfe.value) > 0 && vMP > 0;
        if (mixtoHint) {
          mixtoHint.textContent = esMixto ? 'Devolución mixta: Efectivo + Mercado Pago' : 'Podés dividir el total';
          mixtoHint.style.color = esMixto ? '#7c3aed' : '#94a3b8';
          mixtoHint.style.fontWeight = esMixto ? '700' : '600';
        }
        if (Math.abs(diff) <= 0.01 && !faltaAlias) {
          status.style.background = '#ecfdf5'; status.style.color = '#047857'; status.style.border = '1px solid #a7f3d0';
          status.innerHTML = `<span style="display: flex;">${icCheck}</span> Los montos coinciden con el total a devolver`;
          confirmBtn.disabled = false;
          confirmBtn.style.background = 'linear-gradient(135deg, #0ea5e9, #2563eb)';
          confirmBtn.style.boxShadow = '0 10px 15px -3px rgba(14, 165, 233, 0.3)';
        } else if (faltaAlias) {
          status.style.background = '#fffbeb'; status.style.color = '#b45309'; status.style.border = '1px solid #fde68a';
          status.innerHTML = `<span style="display: flex;">${icAlert}</span> Debes completar el Alias del cliente para devolver por Mercado Pago`;
          confirmBtn.disabled = true;
          confirmBtn.style.background = '#cbd5e1';
          confirmBtn.style.boxShadow = 'none';
        } else if (diff > 0) {
          status.style.background = '#fef2f2'; status.style.color = '#dc2626'; status.style.border = '1px solid #fecaca';
          status.innerHTML = `<span style="display: flex;">${icX}</span> El monto supera el total a devolver en $${formatear(diff)}`;
          confirmBtn.disabled = true;
          confirmBtn.style.background = '#cbd5e1';
          confirmBtn.style.boxShadow = 'none';
        } else {
          status.style.background = '#fef2f2'; status.style.color = '#dc2626'; status.style.border = '1px solid #fecaca';
          status.innerHTML = `<span style="display: flex;">${icX}</span> Falta asignar $${formatear(Math.abs(diff))} del total`;
          confirmBtn.disabled = true;
          confirmBtn.style.background = '#cbd5e1';
          confirmBtn.style.boxShadow = 'none';
        }
      };

      const focusWrap = (wrap, on) => {
        if (!wrap) return;
        wrap.style.borderColor = on ? '#38bdf8' : '#e2e8f0';
      };

      inEfe.addEventListener('input', () => { mask(inEfe); validate(); });
      inMP.addEventListener('input', () => { mask(inMP); pintar(); validate(); });
      inEfe.addEventListener('focus', () => { inEfe.select(); focusWrap(wrapEfe, true); });
      inEfe.addEventListener('blur', () => focusWrap(wrapEfe, false));
      inMP.addEventListener('focus', () => { inMP.select(); focusWrap(wrapMP, true); });
      inMP.addEventListener('blur', () => focusWrap(wrapMP, false));

      const inAlias = document.getElementById('reembolso_alias');
      if (inAlias) {
        inAlias.addEventListener('input', validate);
        inAlias.addEventListener('focus', () => { inAlias.style.borderColor = '#38bdf8'; });
        inAlias.addEventListener('blur', () => { inAlias.style.borderColor = '#dbeafe'; });
      }

      const delEfe = document.getElementById('del_efe');
      const delMP = document.getElementById('del_mp');

      if (delEfe) delEfe.addEventListener('click', () => {
        if (parse(inEfe.value) <= 0) return;
        inEfe.value = '0';
        pintar();
        validate();
      });

      if (delMP) delMP.addEventListener('click', () => {
        if (parse(inMP.value) <= 0) return;
        inMP.value = '0';
        pintar();
        validate();
      });

      pintar();
      validate();
    },
    preConfirm: () => {
      const vEfe = parseFloat(document.getElementById('val_efe').value.replace(/\./g, '').replace(',', '.')) || 0;
      const vMP = parseFloat(document.getElementById('val_mp').value.replace(/\./g, '').replace(',', '.')) || 0;
      const data = {
        monto_efectivo: vEfe,
        monto_mp: vMP
      };
      if (vMP > 0) {
        const alias = document.getElementById('reembolso_alias')?.value.trim() || '';
        if (alias) data.reembolso_alias = alias;
      }
      return data;
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
      serviciosHTML = turnoDetalle.servicios.map((s, idx) => {
        // Vamos sumando para el total
        totalDuracion += (s.duracion || 0);
        totalPrecio += (parseFloat(s.precio) || 0);

        return `
        <tr style="${idx % 2 === 1 ? 'background: #fcfdfe;' : ''}">
          <td style="padding: 11px 16px; border-bottom: 1px solid #f1f5f9; font-weight: 600; color: #1e293b; font-size: 0.9rem;">${s.nombre || 'Sin nombre'}</td>
          <td style="padding: 11px 16px; border-bottom: 1px solid #f1f5f9; text-align: right;">
            <span style="display: inline-block; background: #f1f5f9; color: #475569; border-radius: 8px; padding: 3px 10px; font-size: 0.74rem; font-weight: 700;">${s.duracion || 0} min</span>
          </td>
          <td style="padding: 11px 16px; border-bottom: 1px solid #f1f5f9; text-align: right; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #0f172a; font-size: 0.9rem;">$${formatPrecio(s.precio || 0)}</td>
        </tr>
      `}).join('');

      if (turnoDetalle.servicios.length > 1) {
        serviciosHTML += `
          <tr style="background: #f8fafc;">
            <td style="padding: 13px 16px; border-top: 1px solid #e2e8f0; font-weight: 800; color: #334155; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.9px;">Total de servicios</td>
            <td style="padding: 13px 16px; border-top: 1px solid #e2e8f0; text-align: right; color: #475569; font-weight: 700; font-size: 0.82rem;">${totalDuracion}m</td>
            <td style="padding: 13px 16px; border-top: 1px solid #e2e8f0; text-align: right; font-family: 'JetBrains Mono', monospace; font-weight: 900; color: #0f172a; font-size: 1.05rem;">$${formatPrecio(totalPrecio)}</td>
          </tr>
        `;
      }
    } else {
      serviciosHTML = `<tr><td colspan="3" style="padding: 16px; text-align: center; color: #94a3b8; font-size: 0.9rem;">Sin servicios detallados</td></tr>`;
    }

    const faltaPagar = calcularFaltaPagar(turnoDetalle);
    const montoAbonado = turnoDetalle.tipo_pago === 'TOTAL' ? turnoDetalle.monto_total : turnoDetalle.monto_seña;

    const medioPago = turnoDetalle.medio_pago || '';
    const entidadPago = turnoDetalle.entidad_pago || null;
    const transactionId = turnoDetalle.codigo_transaccion || turnoDetalle.mp_payment_id;

    const detallePago = desglosarMedioPagoTurno(medioPago, entidadPago, turnoDetalle.codigo_transaccion);
    const comprobantePago = detallePago.mixto
      ? (turnoDetalle.mp_payment_id || 'Sin Comprobante')
      : (transactionId || 'Sin Comprobante');

    const totalTurno = parseFloat(turnoDetalle.monto_total) || 0;
    const totalAbonado = parseFloat(montoAbonado) || 0;
    const paidPct = totalTurno > 0 ? Math.min(100, Math.max(0, Math.round((totalAbonado / totalTurno) * 100))) : 0;
    const reembEstado = String(turnoDetalle.reembolso_estado || '').toUpperCase();
    const reembCompletado = turnoDetalle.estado === 'CANCELADO' && reembEstado === 'COMPLETADO';
    const reembPendiente = turnoDetalle.estado === 'CANCELADO' && reembEstado === 'PENDIENTE';

    // Íconos SVG (los mismos que usa la app: lucide)
    const icUser = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;
    const icScissors = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><path d="M8.12 8.12 12 12"/><path d="M20 4 8.12 15.88"/><circle cx="6" cy="18" r="3"/><path d="M14.8 14.8 20 20"/></svg>`;
    const icArmchair = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 9V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v3"/><path d="M3 16a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-4 0v2H7v-2a2 2 0 0 0-4 0Z"/><path d="M5 18v2"/><path d="M19 18v2"/></svg>`;
    const icList = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg>`;
    const icCredit = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>`;
    const icEfectivo = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>`;
    const icMP = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg>`;
    const icX = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>`;
    const icDesglose = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>`;
    const icCalendar = `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/></svg>`;
    const icCheck = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>`;
    const icWallet = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>`;

    const medioUpper = String(medioPago).toUpperCase();
    const singleIcon = medioUpper.includes('MERCADO') ? icMP : (medioUpper.includes('EFECTIVO') ? icEfectivo : icWallet);
    const singleTint = medioUpper.includes('MERCADO') ? '#dbeafe' : (medioUpper.includes('EFECTIVO') ? '#d1fae5' : '#fef3c7');
    const singleAccent = medioUpper.includes('MERCADO') ? '#1d4ed8' : (medioUpper.includes('EFECTIVO') ? '#15803d' : '#b45309');

    const restUpper = String(turnoDetalle.medio_pago_restante || '').toUpperCase();
    const restIcon = restUpper.includes('MERCADO') ? icMP : (restUpper.includes('EFECTIVO') ? icEfectivo : icWallet);
    const restTint = restUpper.includes('MERCADO') ? '#dbeafe' : (restUpper.includes('EFECTIVO') ? '#d1fae5' : '#fef3c7');
    const restAccent = restUpper.includes('MERCADO') ? '#1d4ed8' : (restUpper.includes('EFECTIVO') ? '#15803d' : '#b45309');

    const detalleMedioPagoHTML = detallePago.mixto
      ? `<div style="display: flex; flex-direction: column; gap: 7px;">
          ${detallePago.partes.map(p => `
            <div style="display: flex; align-items: center; gap: 10px; font-size: 0.9rem; font-weight: 600; color: #334155;">
              <span style="width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: ${String(p.medio).startsWith('MERCADOPAGO') ? '#dbeafe' : '#d1fae5'}; color: ${String(p.medio).startsWith('MERCADOPAGO') ? '#1d4ed8' : '#15803d'};">${String(p.medio).startsWith('MERCADOPAGO') ? icMP : icEfectivo}</span>
              ${p.etiqueta}
              <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #0f172a; margin-left: auto;">$${formatPrecio(p.monto)}</span>
            </div>`).join('')}
        </div>`
      : `<span style="font-size: 0.92rem; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 10px;">
          <span style="width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: ${singleTint}; color: ${singleAccent};">${singleIcon}</span>
          <span style="overflow: hidden; text-overflow: ellipsis;">${detallePago.etiqueta}</span>
        </span>`;

    const chipResumenMedio = (p) => {
      const esMP = String(p.medio).startsWith('MERCADOPAGO');
      const tint = esMP ? '#dbeafe' : '#d1fae5';
      const accent = esMP ? '#1d4ed8' : '#15803d';
      const icon = esMP ? icMP : icEfectivo;
      return `<span style="display: inline-flex; align-items: center; gap: 8px; background: ${tint}; color: ${accent}; border-radius: 9px; padding: 6px 11px; font-size: 0.82rem; font-weight: 700;"><span style="width: 22px; height: 22px; border-radius: 7px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #ffffff;">${icon}</span>${p.etiqueta || labelMedioPago(p.medio)}</span>`;
    };

    const medioPagoResumenHTML = detallePago.mixto
      ? `<div style="display: flex; align-items: center; gap: 9px; flex-wrap: wrap;">
          <span style="display: inline-flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; border-radius: 9px; padding: 5px 10px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.6px;">Mixto</span>
          ${detallePago.partes.map(chipResumenMedio).join('<span style="color: #cbd5e1; font-weight: 800;">+</span>')}
        </div>`
      : `<span style="display: inline-flex; align-items: center; gap: 8px; background: ${singleTint}; color: ${singleAccent}; border-radius: 9px; padding: 6px 11px; font-size: 0.82rem; font-weight: 700;"><span style="width: 22px; height: 22px; border-radius: 7px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #ffffff;">${singleIcon}</span>${detallePago.etiqueta || 'Sin especificar'}</span>`;

    Swal.fire({
      title: '',
      width: '800px',
      background: '#ffffff',
      showConfirmButton: false,
      showCloseButton: true,
      html: `
        <div style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: left;">

          <div style="display: flex; align-items: flex-start; gap: 16px;">
            <span style="width: 56px; height: 56px; border-radius: 17px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(160deg, #e0f2fe, #bae6fd); color: #0369a1; box-shadow: inset 0 0 0 1px rgba(3, 105, 161, 0.08);">${icCalendar}</span>
            <div style="flex: 1; min-width: 0; padding-top: 1px;">
              <div style="font-size: 0.68rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.4px;">Detalle del Turno</div>
              <div style="font-size: 1.65rem; font-weight: 800; color: #0f172a; letter-spacing: -0.6px; line-height: 1.15; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${turnoDetalle.cliente_nombre || 'Cliente'} ${turnoDetalle.cliente_apellido || ''}</div>
              <div style="font-size: 0.82rem; color: #64748b; margin-top: 3px;">Turno #${turnoDetalle.id} · ${turnoDetalle.canal || 'PRESENCIAL'}</div>
            </div>
          </div>

          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px;">
            <span class="badge-estado ${getEstadoClass(turnoDetalle.estado, turnoDetalle.tipo_pago)}" style="padding: 7px 16px; border-radius: 30px; font-weight: 800; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px;">
              ${getEstadoTexto(turnoDetalle.estado, turnoDetalle.tipo_pago)}
            </span>
            <span class="canal-badge ${(turnoDetalle.canal || 'PRESENCIAL').toLowerCase()}" style="padding: 7px 16px; border-radius: 30px; font-weight: 700; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.5px;">
              ${turnoDetalle.canal || 'PRESENCIAL'}
            </span>
            <span style="padding: 7px 16px; border-radius: 30px; font-weight: 700; font-size: 0.76rem; background: #f1f5f9; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">
              ${turnoDetalle.tipo_pago === 'TOTAL' ? 'Pago Total' : turnoDetalle.tipo_pago === 'SEÑA' ? 'Con seña' : (turnoDetalle.tipo_pago || 'Pago')}
            </span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px;">
            <div style="background: #f8fafc; border: 1px solid #eef2f7; border-radius: 14px; padding: 13px 15px;">
              <div style="display: flex; align-items: center; gap: 9px;">
                <span style="width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #e0f2fe; color: #0284c7;">${icUser}</span>
                <span style="font-size: 0.62rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.9px;">Cliente</span>
              </div>
              <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-top: 9px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${turnoDetalle.cliente_nombre || 'Cliente'} ${turnoDetalle.cliente_apellido || ''}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #eef2f7; border-radius: 14px; padding: 13px 15px;">
              <div style="display: flex; align-items: center; gap: 9px;">
                <span style="width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #ede9fe; color: #7c3aed;">${icScissors}</span>
                <span style="font-size: 0.62rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.9px;">Profesional</span>
              </div>
              <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-top: 9px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${turnoDetalle.peluquero_nombre || 'Profesional'}</div>
            </div>
            <div style="background: ${turnoDetalle.silla_nombre ? '#f0fdf9' : '#f8fafc'}; border: 1px solid ${turnoDetalle.silla_nombre ? '#a7f3d0' : '#eef2f7'}; border-radius: 14px; padding: 13px 15px;">
              <div style="display: flex; align-items: center; gap: 9px;">
                <span style="width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: ${turnoDetalle.silla_nombre ? '#d1fae5' : '#f1f5f9'}; color: ${turnoDetalle.silla_nombre ? '#059669' : '#64748b'};">${icArmchair}</span>
                <span style="font-size: 0.62rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.9px;">Puesto</span>
              </div>
              <div style="font-size: 0.95rem; font-weight: 700; color: ${turnoDetalle.silla_nombre ? '#14532d' : '#64748b'}; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${turnoDetalle.silla_nombre || 'Pendiente de asignación'}</div>
              <div style="font-size: 0.66rem; font-weight: 800; color: ${turnoDetalle.silla_nombre ? '#059669' : '#64748b'}; text-transform: uppercase; letter-spacing: 0.7px; margin-top: 4px;">${turnoDetalle.silla_nombre ? 'Asignado' : 'Sin asignar'}</div>
            </div>
          </div>

          <div style="margin-top: 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #e0f2fe; color: #0284c7;">${icList}</span>
              <span style="font-size: 0.78rem; font-weight: 800; color: #334155; text-transform: uppercase; letter-spacing: 0.8px;">Detalle de servicios</span>
              <span style="flex: 1; height: 1px; background: #eef2f7;"></span>
              <span style="font-size: 0.72rem; font-weight: 800; color: #64748b; background: #f1f5f9; padding: 4px 11px; border-radius: 20px;">${(turnoDetalle.servicios && turnoDetalle.servicios.length) ? `${turnoDetalle.servicios.length} servicio${turnoDetalle.servicios.length > 1 ? 's' : ''}` : 'Sin servicios'}</span>
            </div>
            <div style="border: 1px solid #eef2f7; border-radius: 16px; overflow: hidden; margin-top: 12px;">
              <table style="width: 100%; border-collapse: collapse;">
                <thead style="background: #f8fafc;">
                  <tr>
                    <th style="padding: 11px 16px; text-align: left; font-weight: 700; font-size: 0.66rem; letter-spacing: 0.9px; text-transform: uppercase; color: #94a3b8; border-bottom: 1px solid #eef2f7;">Servicio</th>
                    <th style="padding: 11px 16px; text-align: right; font-weight: 700; font-size: 0.66rem; letter-spacing: 0.9px; text-transform: uppercase; color: #94a3b8; border-bottom: 1px solid #eef2f7;">Duración</th>
                    <th style="padding: 11px 16px; text-align: right; font-weight: 700; font-size: 0.66rem; letter-spacing: 0.9px; text-transform: uppercase; color: #94a3b8; border-bottom: 1px solid #eef2f7;">Precio</th>
                  </tr>
                </thead>
                <tbody>
                  ${serviciosHTML}
                </tbody>
              </table>
            </div>
          </div>

          <div style="margin-top: 22px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #e0f2fe; color: #0284c7;">${icCredit}</span>
              <span style="font-size: 0.78rem; font-weight: 800; color: #334155; text-transform: uppercase; letter-spacing: 0.8px;">Resumen de pago</span>
              <span style="flex: 1; height: 1px; background: #eef2f7;"></span>
              <span style="font-size: 0.72rem; font-weight: 800; color: ${faltaPagar > 0 ? '#b45309' : '#047857'}; background: ${faltaPagar > 0 ? '#fffbeb' : '#ecfdf5'}; padding: 4px 12px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.4px;">${faltaPagar > 0 ? 'Pendiente' : 'Pagado'}</span>
            </div>

            <div style="background: linear-gradient(150deg, #f8fafc, #eff6ff); border: 1px solid #e2e8f0; border-radius: 20px; padding: 22px; margin-top: 12px;">

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                  <div style="font-size: 0.68rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.1px; margin-bottom: 6px;">Abonado</div>
                  <div style="font-size: 2.1rem; font-weight: 800; color: #059669; letter-spacing: -0.8px; line-height: 1; font-family: 'JetBrains Mono', monospace;">$${formatPrecio(totalAbonado)}</div>
                </div>
                <div style="padding-left: 20px; border-left: 1px solid #e2e8f0;">
                  <div style="font-size: 0.68rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.1px; margin-bottom: 6px;">Pendiente</div>
                  <div style="font-size: 2.1rem; font-weight: 800; color: ${faltaPagar > 0 ? '#d97706' : '#94a3b8'}; letter-spacing: -0.8px; line-height: 1; font-family: 'JetBrains Mono', monospace;">$${formatPrecio(faltaPagar > 0 ? faltaPagar : 0)}</div>
                </div>
              </div>

              <div style="height: 8px; background: #eef2f7; border-radius: 20px; margin-top: 18px; overflow: hidden;">
                <div style="width: ${paidPct}%; height: 100%; border-radius: 20px; background: linear-gradient(90deg, #10b981, #059669);"></div>
              </div>
              <div style="display: flex; justify-content: space-between; margin-top: 6px;">
                <span style="font-size: 0.68rem; font-weight: 700; color: #94a3b8;">${paidPct}% abonado</span>
                <span style="font-size: 0.68rem; font-weight: 700; color: #94a3b8;">Total: $${formatPrecio(totalTurno)}</span>
              </div>
<div style="border-top: 1px solid #e2e8f0; margin-top: 18px; padding-top: 16px; display: flex; flex-direction: column; gap: 16px;">

                <div>
                  <div style="font-size: 0.68rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 9px;">${turnoDetalle.medio_pago_restante ? '1er Pago · Seña' : 'Pago registrado'}</div>
                  <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    ${detalleMedioPagoHTML}
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; color: #475569; background: #ffffff; border: 1px solid #e2e8f0; padding: 4px 11px; border-radius: 9px; letter-spacing: 0.4px; margin-left: auto;">${comprobantePago}</span>
                  </div>
                </div>

                ${turnoDetalle.medio_pago_restante ? `
                  <div>
                    <div style="font-size: 0.68rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 9px;">2do Pago · Restante</div>
                    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                      <span style="font-size: 0.92rem; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 10px;">
                        <span style="width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: ${restTint}; color: ${restAccent};">${restIcon}</span>
                        ${formatearMedioPagoTurno(turnoDetalle.medio_pago_restante, turnoDetalle.entidad_pago_restante, turnoDetalle.codigo_transaccion_restante)}
                      </span>
                      <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; color: #475569; background: #ffffff; border: 1px solid #e2e8f0; padding: 4px 11px; border-radius: 9px; letter-spacing: 0.4px; margin-left: auto;">
                        ${turnoDetalle.mp_payment_id_saldo || turnoDetalle.codigo_transaccion_restante || 'Sin Comprobante'}
                      </span>
                    </div>
                  </div>
                ` : ''}
              </div>
            </div>
          </div>

          ${turnoDetalle.estado === 'CANCELADO' ? `
            <div style="margin-top: 22px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span style="width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #fee2e2; color: #dc2626;">${icX}</span>
                <span style="font-size: 0.78rem; font-weight: 800; color: #334155; text-transform: uppercase; letter-spacing: 0.8px;">Cancelación y reintegro</span>
                <span style="flex: 1; height: 1px; background: #eef2f7;"></span>
                <span style="font-size: 0.72rem; font-weight: 800; color: ${reembCompletado ? '#047857' : '#b45309'}; background: ${reembCompletado ? '#ecfdf5' : '#fffbeb'}; padding: 4px 12px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.4px;">${reembCompletado ? 'Reembolso completado' : 'Reintegro pendiente'}</span>
              </div>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px;">
                <div style="background: #fff7f6; border: 1px solid #fecaca; border-radius: 14px; padding: 15px 16px;">
                  <div style="font-size: 0.66rem; font-weight: 800; color: #dc2626; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Motivo de cancelación</div>
                  <div style="font-size: 1rem; font-weight: 800; color: #7f1d1d; line-height: 1.3;">${turnoDetalle.motivo_cancelacion || 'No especificado'}</div>
                  ${turnoDetalle.obs_cancelacion ? `
                    <div style="background: #ffffff; border: 1px dashed #fca5a5; border-radius: 10px; padding: 9px 12px; margin-top: 10px; color: #991b1b; font-size: 0.84rem; font-style: italic;">
                      ${String(turnoDetalle.obs_cancelacion || '').replace('Mercado Pago / Transferencia', 'Mercado Pago')}
                    </div>
                  ` : ''}
                </div>

                ${reembCompletado ? `
                  <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 14px; padding: 15px 16px;">
                    <div style="font-size: 0.66rem; font-weight: 800; color: #059669; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Reembolso completado</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #166534; margin-top: 2px;">Transferencia MP manual</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 10px;">
                      <span style="width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #d1fae5; color: #15803d;">${icCheck}</span>
                      <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; color: #047857; background: #ffffff; border: 1px solid #a7f3d0; padding: 4px 11px; border-radius: 9px;">${turnoDetalle.reembolso_alias || 'Alias'}</span>
                    </div>
                  </div>
                ` : reembPendiente ? `
                  <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 14px; padding: 15px 16px;">
                    <div style="font-size: 0.66rem; font-weight: 800; color: #b45309; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Reintegro pendiente</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #92400e; margin-top: 2px;">Aún no se registró la devolución.</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 10px;">
                      <span style="width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; background: #fef3c7; color: #b45309;">${icCredit}</span>
                      <span style="font-size: 0.78rem; font-weight: 600; color: #78350f; line-height: 1.4;">Usá la opción “Devolver” del turno para registrar el reintegro.</span>
                    </div>
                  </div>
                ` : `
                  <div style="background: #f8fafc; border: 1px solid #eef2f7; border-radius: 14px; padding: 15px 16px;">
                    <div style="font-size: 0.66rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Reintegro</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #475569; margin-top: 2px;">Sin movimiento de reintegro registrado.</div>
                  </div>
                `}
              </div>
            </div>
          ` : ''}
        </div>
      `
    });
  } catch (error) {
    Swal.fire('Error', 'No se pudo cargar el detalle del turno.', 'error');
  }
};

// 🔥 FLUJO COMPLETAR MEJORADO – COBRO DE SALDO PENDIENTE
const completarTurno = async (turno) => {
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
  if (turno.saldo_pendiente > 0) return false
  return ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC', 'PELUQUERO', 'PEL'].includes(userRol.value)
}

const puedeCancelarTurno = (turno) => {
  if (['COMPLETADO', 'CANCELADO'].includes(turno.estado)) return false
  if (esTurnoPasado(turno.fecha)) return false
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

/* BADGE AZUL PARA REEMBOLSO PENDIENTE (saldo a favor) */
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

/* BADGE AZUL PARA ALIAS INFORMADO EN REINTEGRO PENDIENTE.
   Usa fondo traslúcido que funciona en modo claro y oscuro. */
.badge-alias-informado {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  width: fit-content;
  margin-top: 6px;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: #0284c7;
  background: rgba(14, 165, 233, 0.10);
  border: 1px solid rgba(14, 165, 233, 0.35);
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