<template>
  <div class="turnos-container">
    <div class="turnos-header">
      <div class="header-content">
        <h1>Mis Turnos</h1>
        <p class="subtitulo">Gestiona y revisa todos tus turnos programados</p>
      </div>
      <button @click="$router.push('/turnos/crear-web')" class="btn-nuevo-turno">
        <CalendarPlus :size="18" />
        Nuevo Turno
      </button>
    </div>

    <div class="tabs-container">
      <div class="tabs-wrapper">
        <button 
          ref="tabProximos"
          :class="['tab', { active: tabActiva === 'proximos' }]" 
          @click="tabActiva = 'proximos'"
        >
          <Clock :size="16" />
          Próximos
          <span v-if="contadorProximos > 0" class="tab-badge">
            {{ contadorProximos }}
          </span>
        </button>
        <button 
          ref="tabHistorial"
          :class="['tab', { active: tabActiva === 'historial' }]" 
          @click="tabActiva = 'historial'"
        >
          <History :size="16" />
          Historial
          <span v-if="contadorHistorial > 0" class="tab-badge">
            {{ contadorHistorial }}
          </span>
        </button>
      </div>
      <div class="tabs-indicator" :style="indicatorStyle"></div>
    </div>

    <div v-if="cargando" class="loading-state">
      <div class="spinner-container">
        <div class="spinner"></div>
        <p>Cargando tus turnos...</p>
      </div>
    </div>

    <div v-else-if="turnosFiltrados.length === 0" class="sin-turnos">
      <div class="sin-turnos-content">
        <CalendarX :size="64" />
        <h3>No tienes turnos {{ tabActiva === 'proximos' ? 'programados' : 'en el historial' }}</h3>
        <p v-if="tabActiva === 'proximos'">
          ¡Programa tu primer turno y disfruta de nuestros servicios!
        </p>
        <p v-else>
          Tu historial de turnos aparecerá aquí una vez que completes tu primer servicio.
        </p>
        <button v-if="tabActiva === 'proximos'" @click="$router.push('/turnos/crear-web')" class="btn-programar">
          <CalendarPlus :size="18" />
          Programar mi primer turno
        </button>
      </div>
    </div>

    <div v-else class="turnos-grid">
      <div v-for="turno in turnosFiltrados" :key="turno.id" class="turno-card">
        <div class="turno-borde" :class="claseEstado(turno.estado)"></div>
        
        <div class="turno-content">
          <div class="turno-header">
            <div class="turno-fecha">
              <Calendar :size="14" />
              <span class="fecha-texto">{{ formatFecha(turno.fecha) }}</span>
              <span class="fecha-hora">{{ turno.hora }}hs</span>
            </div>
            <div class="turno-estado">
              <span :class="['estado-badge', claseEstado(turno.estado)]">
                {{ estadoTexto(turno.estado) }}
              </span>
            </div>
          </div>

          <div class="turno-info">
            <h3 class="turno-titulo">{{ turno.servicios }}</h3>
            
            <div class="turno-detalles">
              <div class="detalle-item">
                <User :size="14" />
                <span class="detalle-label">Peluquero:</span>
                <span class="detalle-valor">{{ turno.peluquero_nombre || 'No asignado' }}</span>
              </div>
              
              <div class="detalle-item">
                <Clock :size="14" />
                <span class="detalle-label">Duración:</span>
                <span class="detalle-valor">{{ turno.duracion || 30 }} minutos</span>
              </div>
            </div>
          </div>

          <div class="turno-footer">
            <div class="turno-precio">
              <div class="precio-total">
                <span class="precio-simbolo">$</span>
                <span class="precio-valor">{{ turno.monto_total || '0' }}</span>
              </div>
              <span class="precio-texto">Total del servicio</span>
            </div>
            
            <!-- 🔥 BADGE DE FIDELIZACIÓN - 15% DESCUENTO -->
            <div v-if="turno.descuento_aplicado && turno.descuento_aplicado > 0" class="descuento-fidelizacion">
              <i class="bi bi-gift me-1"></i>
              <span>Con 15% OFF (fidelización)</span>
            </div>
            
            <div class="turno-acciones">
              <button 
                v-if="turno.puede_cancelar && turno.estado !== 'CANCELADO'" 
                @click="cancelarTurno(turno)" 
                class="btn-cancelar"
              >
                <XCircle :size="16" />
                Cancelar
              </button>
              
              <div 
                v-else-if="tabActiva === 'proximos' && turno.estado !== 'CANCELADO'" 
                class="no-cancelable"
              >
                <AlertCircle :size="14" />
                <small>No cancelable (menos de 3 horas)</small>
              </div>
              
              <button 
                v-if="turno.estado === 'COMPLETADO'" 
                @click="verDetalles(turno)" 
                class="btn-detalles"
              >
                <Eye :size="16" />
                Ver detalles
              </button>
            </div>
          </div>

          <div v-if="turno.notas" class="turno-notas">
            <MessageSquare :size="14" />
            <span>{{ turno.notas }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!cargando && tabActiva === 'historial' && totalPaginas > 1" class="paginacion-turnos">
      <div class="paginacion-info">
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
      </div>
      
      <div class="paginacion-controles">
        <button 
          @click="paginaAnterior" 
          :disabled="pagina === 1" 
          class="btn-pagina prev"
        >
          <ChevronLeft :size="16" />
        </button>
        
        <div class="paginacion-numeros">
          <button
            v-for="num in paginasVisibles"
            :key="num"
            :class="{ active: num === pagina, dots: num === '...' }"
            @click="num !== '...' && cambiarPagina(num)"
            :disabled="num === '...'"
          >
            {{ num }}
          </button>
        </div>
        
        <button 
          @click="paginaSiguiente" 
          :disabled="pagina === totalPaginas" 
          class="btn-pagina next"
        >
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <div v-if="!cargando && turnosFiltrados.length > 0" class="turnos-estadisticas">
      <div class="estadistica-item">
        <Calendar :size="18" />
        <div class="estadistica-info">
          <span class="estadistica-valor">{{ turnosFiltrados.length }}</span>
          <span class="estadistica-label">
            {{ tabActiva === 'proximos' ? 'turnos programados' : 'turnos en historial' }}
          </span>
        </div>
      </div>
      
      <div v-if="tabActiva === 'proximos'" class="estadistica-item">
        <Clock :size="18" />
        <div class="estadistica-info">
          <span class="estadistica-valor">{{ proximoEnDias }} días</span>
          <span class="estadistica-label">para tu próximo turno</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import api from '@/services/api'
import {
  Calendar, CalendarPlus, CalendarX, Clock, History,
  ChevronLeft, ChevronRight, User, XCircle, AlertCircle,
  Eye, MessageSquare
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute() 

const turnos = ref([])
const cargando = ref(true)
const tabActiva = ref('proximos')
const pagina = ref(1)
const itemsPorPagina = 6
const tabProximos = ref(null)
const tabHistorial = ref(null)

const cargarMisTurnos = async () => {
  try {
    const response = await api.get('/turnos/mis-turnos/')
    turnos.value = response.data
  } catch (error) {
    console.error('Error cargando turnos:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No pudimos cargar tus turnos',
      confirmButtonColor: '#0ea5e9'
    })
  } finally {
    cargando.value = false
  }
}

const formatFecha = (f) => {
  if (!f) return ''
  const [y, m, d] = f.split('-')
  return `${d}/${m}/${y}`
}

const formatPrecio = (p) => parseFloat(p).toLocaleString('es-AR', { minimumFractionDigits: 2 })

// 🔥 ESTADOS ACTUALIZADOS (Chau Confirmado)
const estadoTexto = (estado) => {
  const map = { 'RESERVADO': 'Reservado', 'CANCELADO': 'Cancelado', 'COMPLETADO': 'Completado' }
  return map[estado] || estado
}

const claseEstado = (estado) => {
  const map = { 'RESERVADO': 'reservado', 'CANCELADO': 'cancelado', 'COMPLETADO': 'completado' }
  return map[estado] || 'default'
}

// 💳 MEDIOS DE PAGO PARA EL DETALLE
const getMedioPagoTexto = (medio, entidad = null) => {
  if (medio === 'TRANSFERENCIA' && entidad) return entidad
  const map = { 'MERCADO_PAGO': 'Mercado Pago', 'EFECTIVO': 'Efectivo', 'TRANSFERENCIA': 'Transferencia' }
  return map[medio] || medio
}

const cancelarTurno = async (turno) => {
  let margenConfig = 3;
  try {
    const resConfig = await api.get('/api/configuracion/');
    if (resConfig.data && resConfig.data.margen_horas_cancelacion) {
      margenConfig = resConfig.data.margen_horas_cancelacion;
    }
  } catch (error) { console.error(error) }

  const ahora = new Date();
  const fechaTurno = new Date(`${turno.fecha}T${turno.hora}`);
  const horasFaltantes = (fechaTurno - ahora) / (1000 * 60 * 60);
  const hayReembolso = horasFaltantes >= margenConfig;

  const { value: formValues } = await Swal.fire({
    title: '¿Cancelar Turno?',
    html: `
      <div style="text-align: left; font-family: sans-serif;">
        <div style="background: ${hayReembolso ? '#f0fdf4' : '#fffbeb'}; padding: 12px; border-radius: 10px; margin-bottom: 15px; border: 1px solid ${hayReembolso ? '#bbf7d0' : '#fef3c7'}; display: flex; align-items: center; gap: 10px;">
          <div style="font-size: 1.2rem;">${hayReembolso ? '✅' : '⚠️'}</div>
          <div>
            <div style="font-weight: 700; color: ${hayReembolso ? '#166534' : '#92400e'}; font-size: 0.9rem;">${hayReembolso ? 'Reembolso disponible' : 'Sin reembolso'}</div>
            <div style="color: ${hayReembolso ? '#16a34a' : '#b45309'}; font-size: 0.8rem;">Anticipación: ${Math.floor(horasFaltantes)}hs (Mínimo requerido: ${margenConfig}hs).</div>
          </div>
        </div>
        <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; border: 1px solid #e2e8f0;">
          <label style="display:block; margin-bottom:5px; font-weight:bold;">Motivo:</label>
          <select id="motivo" class="swal2-input" style="width: 100%; margin: 0 0 15px 0;">
            <option value="PERSONAL">Motivos personales</option>
            <option value="SALUD">Problema de salud</option>
            <option value="ERROR">Error al reservar</option>
            <option value="HORARIO">Cambio de planes</option>
          </select>
          <label style="display:block; margin-bottom:5px; font-weight:bold;">Observaciones:</label>
          <textarea id="obs" class="swal2-textarea" style="width: 100%; margin: 0; height: 80px;" placeholder="Opcional..."></textarea>
        </div>
      </div>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    confirmButtonText: 'Confirmar Cancelación',
    preConfirm: () => ({ motivo: document.getElementById('motivo').value, observaciones: document.getElementById('obs').value })
  });

  if (formValues) {
    try {
      const response = await api.post(`/turnos/cancelar-propio/${turno.id}/`, formValues);
      await Swal.fire({ icon: response.data.reembolso_ok ? 'success' : 'warning', title: 'Turno Cancelado', text: response.data.message });
      cargarMisTurnos();
    } catch (error) { Swal.fire('Error', 'No se pudo cancelar el turno.', 'error') }
  }
}

// 🔥 VERSIÓN UNIFICADA (ESTILO ADMIN) PARA EL CLIENTE
const verDetalles = async (turno) => {
  try {
    // 1. Buscamos los datos completos del turno a la API
    const response = await api.get(`/api/turnos/${turno.id}/`);
    const t = response.data;

    // 2. Armamos la tablita de servicios
    let serviciosHTML = '';
    if (t.servicios && t.servicios.length > 0) {
      serviciosHTML = t.servicios.map(s => `
        <tr style="border-bottom: 1px solid #f1f5f9;">
          <td style="padding: 12px; font-weight: 500; color: #1e293b; font-size: 0.95rem;">${s.nombre}</td>
          <td style="padding: 12px; text-align: right; color: #64748b; font-size: 0.9rem;">${s.duracion}m</td>
          <td style="padding: 12px; text-align: right; font-weight: 700; color: #0f172a;">$${formatPrecio(s.precio)}</td>
        </tr>
      `).join('');
    } else {
      serviciosHTML = `<tr><td colspan="3" style="padding: 15px; text-align: center; color: #94a3b8;">Sin servicios detallados</td></tr>`;
    }

    // 3. Cálculos de dinero (usando la lógica que corregimos hoy)
    const faltaPagar = t.tipo_pago === 'TOTAL' ? 0 : (parseFloat(t.monto_total) - parseFloat(t.monto_seña));
    const montoAbonado = t.tipo_pago === 'TOTAL' ? t.monto_total : t.monto_seña;

    // 4. Identificamos los comprobantes
    const transactionId1 = t.codigo_transaccion || t.mp_payment_id || 'EFECTIVO';

    Swal.fire({
      title: `<div style="display: flex; align-items: center; justify-content: center; gap: 10px; color: #0f172a;">
                <span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px;">Detalle de tu Turno</span>
              </div>`,
      width: '700px',
      background: '#ffffff',
      showConfirmButton: false,
      showCloseButton: true,
      html: `
        <div style="font-family: 'Inter', sans-serif; text-align: left;">

          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #f1f5f9;">
            <span class="estado-badge ${claseEstado(t.estado)}" style="padding: 8px 16px; border-radius: 30px; font-weight: 700; font-size: 0.9rem;">
              ${estadoTexto(t.estado)}
            </span>
            <div style="font-weight: 600; color: #64748b;">
              📅 ${formatFecha(t.fecha)} - ${t.hora}hs
            </div>
          </div>

          ${t.estado === 'CANCELADO' ? `
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 15px; margin-bottom: 20px;">
              <div style="color: #991b1b; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">Motivo de Cancelación</div>
              <div style="color: #7f1d1d; font-size: 1.1rem; font-weight: 600;">${t.motivo_cancelacion || 'No especificado'}</div>
              ${t.obs_cancelacion ? `<div style="color: #b91c1c; font-size: 0.9rem; margin-top: 5px; font-style: italic;">"${t.obs_cancelacion}"</div>` : ''}
            </div>
          ` : ''}

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;">
            <div style="background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;">
              <div style="font-weight: 700; color: #475569; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 5px;">Profesional</div>
              <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">${t.peluquero_nombre}</div>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;">
              <div style="font-weight: 700; color: #475569; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 5px;">Duración Total</div>
              <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">${t.duracion_total || t.duracion || 30} min</div>
            </div>
          </div>

          <div style="margin-bottom: 25px;">
            <h4 style="font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 10px;">Servicios Contratados</h4>
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
              <table style="width: 100%; border-collapse: collapse;">
                <thead style="background: #f1f5f9;">
                  <tr>
                    <th style="padding: 10px; text-align: left; font-size: 0.8rem;">Servicio</th>
                    <th style="padding: 10px; text-align: right; font-size: 0.8rem;">Tiempo</th>
                    <th style="padding: 10px; text-align: right; font-size: 0.8rem;">Precio</th>
                  </tr>
                </thead>
                <tbody>
                  ${serviciosHTML}
                </tbody>
              </table>
            </div>
          </div>

          <div style="background: linear-gradient(145deg, #1e293b, #0f172a); padding: 20px; border-radius: 16px; color: white;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
              <h4 style="margin:0; font-size: 0.9rem; font-weight: 600; color: #94a3b8;">Resumen Económico</h4>
              <span style="color: #4ade80; font-weight: 800; font-size: 1.2rem;">Total: $${formatPrecio(t.monto_total)}</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px; border-bottom: 1px solid #334155; padding-bottom: 15px;">
              <div>
                <span style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Has Abonado</span>
                <div style="font-size: 1.4rem; font-weight: 700; color: #4ade80;">$${formatPrecio(montoAbonado)}</div>
              </div>
              <div>
                <span style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Saldo Pendiente</span>
                <div style="font-size: 1.4rem; font-weight: 700; color: ${faltaPagar > 0 ? '#fbbf24' : '#ffffff'};">$${formatPrecio(faltaPagar)}</div>
              </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 10px;">
              <div>
                <span style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">${t.medio_pago_restante ? 'Primer Pago (Seña)' : 'Detalle de Pago'}</span>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                  <span style="font-size: 0.85rem;">💳 ${getMedioPagoTexto(t.medio_pago, t.entidad_pago)}</span>
                  <span style="font-family: monospace; font-size: 0.85rem; color: #a5f3fc;">Ref: ${transactionId1}</span>
                </div>
              </div>

              ${t.medio_pago_restante ? `
                <div style="border-top: 1px dashed #334155; pt: 8px; margin-top: 5px;">
                  <span style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Segundo Pago (Saldo en Local)</span>
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span style="font-size: 0.85rem;">💵 ${getMedioPagoTexto(t.medio_pago_restante, t.entidad_pago_restante)}</span>
                    <span style="font-family: monospace; font-size: 0.85rem; color: #a5f3fc;">Ref: ${t.codigo_transaccion_restante || 'PRESENCIAL'}</span>
                  </div>
                </div>
              ` : ''}
            </div>
          </div>

          ${t.notas ? `
            <div style="margin-top: 20px; padding: 12px; background: #fffbeb; border-radius: 10px; border-left: 4px solid #f59e0b; color: #92400e; font-size: 0.9rem;">
              <strong>Nota del Peluquero:</strong> ${t.notas}
            </div>
          ` : ''}

        </div>
      `
    });
  } catch (error) {
    console.error(error);
    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo cargar el detalle del turno.', confirmButtonColor: '#0ea5e9' });
  }
};

const mostrarAlertaFelicidades = async (turnoId) => {
  try {
    const res = await api.get(`/api/turnos/${turnoId}/`);
    const t = res.data;
    Swal.fire({
      title: '¡Felicidades! 🎉',
      html: `<div style="text-align: left; background: #f0f9ff; padding: 1.2rem; border-radius: 12px; border: 1px solid #bae6fd;">
          <p style="font-size: 1.1rem; margin-bottom: 1rem;">Tu reserva ha sido confirmada con éxito.</p>
          <p>📅 <b>Día:</b> ${formatFecha(t.fecha)}</p><p>⏰ <b>Hora:</b> ${t.hora} hs</p><p>💇‍♂️ <b>Profesional:</b> ${t.peluquero_nombre}</p><p>💰 <b>Monto:</b> $${t.monto_total}</p>
        </div>`,
      icon: 'success', confirmButtonColor: '#0ea5e9'
    });
    router.replace({ query: {} });
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  await cargarMisTurnos()
  const query = route.query;
  if (query.pago_exitoso === 'true') {
    if (query.tipo !== 'pedido') mostrarAlertaFelicidades(query.turno_id); 
    router.replace({ query: {} }); 
  }
})

const turnosFiltrados = computed(() => {
  const hoy = new Date().toISOString().split('T')[0]
  let filtrados = tabActiva.value === 'proximos' 
    ? turnos.value.filter(t => t.fecha >= hoy && t.estado === 'RESERVADO').sort((a, b) => new Date(a.fecha + 'T' + a.hora) - new Date(b.fecha + 'T' + b.hora))
    : turnos.value.filter(t => t.fecha < hoy || ['CANCELADO', 'COMPLETADO'].includes(t.estado)).sort((a, b) => new Date(b.fecha + 'T' + b.hora) - new Date(a.fecha + 'T' + a.hora))
  
  if (tabActiva.value === 'historial') {
    const inicio = (pagina.value - 1) * itemsPorPagina
    return filtrados.slice(inicio, inicio + itemsPorPagina)
  }
  return filtrados
})

const contadorProximos = computed(() => turnos.value.filter(t => t.fecha >= new Date().toISOString().split('T')[0] && t.estado === 'RESERVADO').length)
const contadorHistorial = computed(() => turnos.value.filter(t => t.fecha < new Date().toISOString().split('T')[0] || ['CANCELADO', 'COMPLETADO'].includes(t.estado)).length)
const proximoEnDias = computed(() => {
  const proximos = turnos.value.filter(t => t.fecha >= new Date().toISOString().split('T')[0] && t.estado === 'RESERVADO')
  if (proximos.length === 0) return 0
  return Math.max(0, Math.ceil((new Date(proximos[0].fecha) - new Date()) / (1000 * 60 * 60 * 24)))
})

const totalPaginas = computed(() => tabActiva.value !== 'historial' ? 1 : Math.max(1, Math.ceil(turnos.value.filter(t => t.fecha < new Date().toISOString().split('T')[0] || ['CANCELADO', 'COMPLETADO'].includes(t.estado)).length / itemsPorPagina)))
const paginasVisibles = computed(() => {
  const total = totalPaginas.value, current = pagina.value, pages = []
  if (total <= 5) for (let i = 1; i <= total; i++) pages.push(i)
  else if (current <= 3) { for (let i = 1; i <= 4; i++) pages.push(i); pages.push('...', total) }
  else if (current >= total - 2) { pages.push(1, '...'); for (let i = total - 3; i <= total; i++) pages.push(i) }
  else { pages.push(1, '...', current - 1, current, current + 1, '...', total) }
  return pages
})

const indicatorStyle = computed(() => ({ transform: `translateX(${tabActiva.value === 'proximos' ? '0' : '100'}%)`, width: '50%' }))
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }
const cambiarPagina = (num) => { if (num !== '...') pagina.value = num }
watch(tabActiva, () => { pagina.value = 1 })
</script>

<style scoped>
/* ========================================
   📅 MIS TURNOS - DISEÑO ESPECTACULAR
   ======================================== */

.turnos-container {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

/* HEADER */
.turnos-header {
  background: var(--bg-secondary);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.turnos-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
}

.header-content {
  flex: 1;
  min-width: 300px;
}

.header-content h1 {
  margin: 0;
  font-size: 2.8rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.subtitulo {
  color: var(--text-secondary);
  font-size: 1.1rem;
  max-width: 600px;
  line-height: 1.5;
}

.btn-nuevo-turno {
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
  gap: 10px;
  white-space: nowrap;
}

.btn-nuevo-turno::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-nuevo-turno:hover::before {
  left: 100%;
}

.btn-nuevo-turno:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

/* TABS MEJORADAS - ARREGLADO */
.tabs-container {
  background: rgb(27, 48, 101);
  border-radius: 16px;
  padding: 10px;
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.tabs-wrapper {
  display: flex;
  position: relative;
  z-index: 1;
}

.tab {
  flex: 1;
  background: none;
  border: none;
  padding: 16px 24px;
  color: var(--text-secondary);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  border-radius: 12px;
  z-index: 2;
}

.tab:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
}

.tab.active {
  color: white;
}

.tabs-indicator {
  position: absolute;
  top: 10px;
  left: 10px;
  width: calc(50% - 10px);
  height: calc(100% - 20px);
  border-radius: 12px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
  z-index: 1;
}

.tab-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  min-width: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tab.active .tab-badge {
  background: rgba(255, 255, 255, 0.3);
}

/* LOADING STATE */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  background: var(--bg-secondary);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.spinner-container {
  text-align: center;
  color: var(--text-secondary);
}

.spinner {
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top: 3px solid #0ea5e9;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* SIN TURNOS */
.sin-turnos {
  text-align: center;
  padding: 80px 20px;
  background: var(--bg-secondary);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  margin: 40px 0;
}

.sin-turnos svg {
  color: var(--text-tertiary);
  margin-bottom: 25px;
  opacity: 0.5;
}

.sin-turnos h3 {
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: 1.8rem;
  font-weight: 800;
}

.sin-turnos p {
  color: var(--text-secondary);
  margin-bottom: 30px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  font-size: 1.1rem;
  line-height: 1.5;
}

.btn-programar {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-programar:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

/* GRID DE TURNOS */
.turnos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.turno-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  position: relative;
  display: flex;
}

.turno-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  border-color: #0ea5e9;
}

/* BORDE DE ESTADO */
.turno-borde {
  width: 6px;
  min-height: 100%;
}

.turno-borde.reservado {
  background: linear-gradient(to bottom, #f59e0b, #fbbf24);
}

.turno-borde.confirmado {
  background: linear-gradient(to bottom, #10b981, #34d399);
}

.turno-borde.cancelado {
  background: linear-gradient(to bottom, #ef4444, #f87171);
}

.turno-borde.completado {
  background: linear-gradient(to bottom, #0ea5e9, #60a5fa);
}

/* CONTENIDO DEL TURNO */
.turno-content {
  padding: 24px;
  flex: 1;
}

/* HEADER DEL TURNO */
.turno-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.turno-fecha {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-weight: 700;
}

.fecha-texto {
  font-size: 1rem;
}

.fecha-hora {
  background: var(--bg-primary);
  color: var(--text-secondary);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid var(--border-color);
}

.estado-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.estado-badge.reservado {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.estado-badge.confirmado {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.estado-badge.cancelado {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
}

.estado-badge.completado {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  border: 1px solid rgba(14, 165, 233, 0.3);
}

/* INFO DEL TURNO */
.turno-info {
  margin-bottom: 20px;
}

.turno-titulo {
  margin: 0 0 15px 0;
  font-size: 1.3rem;
  color: var(--text-primary);
  font-weight: 800;
  line-height: 1.3;
}

.turno-detalles {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detalle-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.detalle-item svg {
  color: var(--text-tertiary);
  opacity: 0.7;
  flex-shrink: 0;
}

.detalle-label {
  font-weight: 600;
  min-width: 80px;
}

.detalle-valor {
  color: var(--text-primary);
  font-weight: 500;
  flex: 1;
}

/* FOOTER DEL TURNO */
.turno-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: 15px;
}

.turno-precio {
  display: flex;
  flex-direction: column;
}

.precio-total {
  display: flex;
  align-items: baseline;
  gap: 2px;
  margin-bottom: 4px;
}

.precio-simbolo {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.precio-valor {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1;
}

.precio-texto {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-weight: 500;
}

.turno-acciones {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-cancelar {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-cancelar:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.no-cancelable {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-style: italic;
}

.no-cancelable svg {
  color: #f59e0b;
}

.btn-detalles {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  border: 1px solid rgba(14, 165, 233, 0.3);
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-detalles:hover {
  background: rgba(14, 165, 233, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}

/* NOTAS DEL TURNO */
.turno-notas {
  margin-top: 15px;
  padding: 12px;
  background: rgba(14, 165, 233, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(14, 165, 233, 0.1);
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.turno-notas svg {
  color: #0ea5e9;
  flex-shrink: 0;
  margin-top: 2px;
}

/* PAGINACIÓN */
.paginacion-turnos {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  margin: 40px 0;
  flex-wrap: wrap;
  gap: 20px;
}

.descuento-fidelizacion {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  font-weight: 600;
}

.paginacion-info {
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.95rem;
}

.paginacion-controles {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-pagina {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-pagina:hover:not(:disabled) {
  background: var(--hover-bg);
  border-color: #0ea5e9;
  color: #0ea5e9;
  transform: translateY(-2px);
}

.btn-pagina:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.paginacion-numeros {
  display: flex;
  gap: 6px;
}

.paginacion-numeros button {
  min-width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.paginacion-numeros button:hover:not(:disabled) {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.paginacion-numeros button.active {
  background: #0ea5e9;
  color: white;
  border-color: #0ea5e9;
}

.paginacion-numeros button.dots {
  background: none;
  border: none;
  cursor: default;
  color: var(--text-tertiary);
  min-width: 30px;
}

.paginacion-numeros button.dots:hover {
  background: none;
}

/* ESTADÍSTICAS */
.turnos-estadisticas {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.estadistica-item {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 15px;
}

.estadistica-item svg {
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.1);
  padding: 12px;
  border-radius: 12px;
}

.estadistica-info {
  display: flex;
  flex-direction: column;
}

.estadistica-valor {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.estadistica-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .turnos-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .turnos-container {
    padding: 20px 15px;
  }
  
  .turnos-header {
    padding: 30px 25px;
    flex-direction: column;
    text-align: center;
    gap: 25px;
  }
  
  .header-content {
    min-width: auto;
  }
  
  .header-content h1 {
    font-size: 2.2rem;
  }
  
  .turnos-grid {
    grid-template-columns: 1fr;
  }
  
  .turno-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }
  
  .turno-acciones {
    justify-content: flex-start;
  }
  
  .paginacion-turnos {
    flex-direction: column;
    text-align: center;
    gap: 25px;
  }
  
  .paginacion-info {
    text-align: center;
    width: 100%;
  }
}

@media (max-width: 480px) {
  .header-content h1 {
    font-size: 1.8rem;
  }
  
  .subtitulo {
    font-size: 1rem;
  }
  
  .btn-nuevo-turno {
    width: 100%;
    justify-content: center;
  }
  
  .tab {
    padding: 14px 16px;
    font-size: 0.9rem;
  }
  
  .detalle-item {
    flex-wrap: wrap;
  }
  
  .detalle-label {
    min-width: 70px;
  }
  
  .precio-valor {
    font-size: 1.5rem;
  }
  
  .turnos-estadisticas {
    grid-template-columns: 1fr;
  }
}
</style>