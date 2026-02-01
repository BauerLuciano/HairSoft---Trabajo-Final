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
import { useRouter, useRoute } from 'vue-router' // ✅ AGREGADO useRoute
import axios from 'axios'
import Swal from 'sweetalert2'
import api from '@/services/api'
import {
  Calendar, CalendarPlus, CalendarX, Clock, History,
  ChevronLeft, ChevronRight, User, XCircle, AlertCircle,
  Eye, MessageSquare
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute() // ✅ AGREGADO

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

const estadoTexto = (estado) => {
  const map = {
    'RESERVADO': 'Reservado',
    'CONFIRMADO': 'Confirmado',
    'CANCELADO': 'Cancelado',
    'COMPLETADO': 'Completado'
  }
  return map[estado] || estado
}

const claseEstado = (estado) => {
  const map = {
    'RESERVADO': 'reservado',
    'CONFIRMADO': 'confirmado',
    'CANCELADO': 'cancelado',
    'COMPLETADO': 'completado'
  }
  return map[estado] || 'default'
}

const cancelarTurno = async (turno) => {
  const result = await Swal.fire({
    title: '¿Cancelar Turno?',
    html: `
      <div style="text-align: left; margin: 1rem 0;">
        <p><strong>Fecha:</strong> ${formatFecha(turno.fecha)} - ${turno.hora}hs</p>
        <p><strong>Servicio:</strong> ${turno.servicios}</p>
        <p style="color: #f59e0b; margin-top: 1rem;">
          <small>Si pagaste seña, te contactaremos para el reembolso.</small>
        </p>
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#6b7280',
    confirmButtonText: 'Sí, cancelar turno',
    cancelButtonText: 'Mantener turno'
  })

  if (result.isConfirmed) {
    try {
      Swal.showLoading()
      const response = await api.post(`/turnos/cancelar-propio/${turno.id}/`)
      
      Swal.fire({
        icon: 'success',
        title: 'Turno cancelado',
        text: response.data.message,
        confirmButtonColor: '#0ea5e9'
      })
      cargarMisTurnos()
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.error || 'No se pudo cancelar el turno',
        confirmButtonColor: '#0ea5e9'
      })
    }
  }
}

const verDetalles = (turno) => {
  Swal.fire({
    title: 'Detalles del Turno',
    html: `
      <div style="text-align: left;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
          <div style="width: 10px; height: 10px; border-radius: 50%; background: #10b981;"></div>
          <strong style="color: #10b981;">COMPLETADO</strong>
        </div>
        
        <p><strong>📅 Fecha:</strong> ${formatFecha(turno.fecha)} - ${turno.hora}hs</p>
        <p><strong>✂️ Servicio:</strong> ${turno.servicios}</p>
        <p><strong>👨‍💼 Peluquero:</strong> ${turno.peluquero_nombre || 'No asignado'}</p>
        <p><strong>⏱ Duración:</strong> ${turno.duracion || 30} minutos</p>
        <p><strong>💰 Total:</strong> $${turno.monto_total || '0'}</p>
        
        ${turno.notas ? `<p style="margin-top: 1rem; padding: 10px; background: rgba(14, 165, 233, 0.1); border-radius: 8px;">
          <strong>📝 Notas:</strong> ${turno.notas}
        </p>` : ''}
      </div>
    `,
    confirmButtonColor: '#0ea5e9'
  })
}

// ✅ FUNCIÓN NUEVA PARA LA ALERTA DE FELICIDADES
const mostrarAlertaFelicidades = async (turnoId) => {
  try {
    // 🛑 ACÁ ESTABA EL ERROR: Faltaba el "/api" al principio
    const res = await api.get(`/api/turnos/${turnoId}/`);
    const t = res.data;
    
    Swal.fire({
      title: '¡Felicidades! 🎉',
      html: `
        <div style="text-align: left; background: #f0f9ff; padding: 1.2rem; border-radius: 12px; border: 1px solid #bae6fd;">
          <p style="font-size: 1.1rem; margin-bottom: 1rem;">Tu reserva ha sido confirmada con éxito.</p>
          <p>📅 <b>Día:</b> ${formatFecha(t.fecha)}</p>
          <p>⏰ <b>Hora:</b> ${t.hora} hs</p>
          <p>💇‍♂️ <b>Profesional:</b> ${t.peluquero_nombre}</p>
          <p>💰 <b>Monto:</b> $${t.monto_total}</p>
          <p style="margin-top: 1rem; font-size: 0.9rem; color: #0369a1;">¡Te esperamos!</p>
        </div>
      `,
      icon: 'success',
      confirmButtonText: 'Genial',
      confirmButtonColor: '#0ea5e9'
    });
    
    // Limpiamos los parámetros de la URL para que no vuelva a saltar al recargar
    router.replace({ query: {} });
  } catch (e) { 
    console.error("Error al obtener datos del turno:", e); 
    // Fallback por si falla la API, para que no quede undefined
    Swal.fire({
        title: '¡Turno Confirmado!',
        text: 'Tu pago se procesó correctamente y el turno ya figura en tu historial.',
        icon: 'success',
        confirmButtonColor: '#0ea5e9'
    });
  }
}

onMounted(async () => {
  await cargarMisTurnos()
  
  const query = route.query;
  if (query.pago_exitoso === 'true') {
    if (query.tipo === 'pedido') {
      // ✅ ALERTA PARA COMPRA DE PRODUCTOS
      Swal.fire({
        title: '¡Compra Exitosa! 🛍️',
        text: `Tu pedido #${query.pedido_id || query.id} ha sido procesado.`,
        icon: 'success',
        confirmButtonColor: '#0ea5e9'
      });
    } else {
      // ✅ ALERTA PARA TURNOS (CORREGIDO)
      mostrarAlertaFelicidades(query.turno_id); 
    }
    
    // Limpiar URL para que no salga el cartel al recargar
    router.replace({ query: {} }); 
  }
})

// Computed: turnos filtrados
const turnosFiltrados = computed(() => {
  const hoy = new Date().toISOString().split('T')[0]
  
  let filtrados = []
  
  if (tabActiva.value === 'proximos') {
    filtrados = turnos.value.filter(t => 
      t.fecha >= hoy && 
      ['RESERVADO', 'CONFIRMADO'].includes(t.estado)
    )
    // Ordenar por fecha y hora más cercana
    filtrados.sort((a, b) => {
      const fechaA = new Date(a.fecha + 'T' + a.hora)
      const fechaB = new Date(b.fecha + 'T' + b.hora)
      return fechaA - fechaB
    })
  } else {
    filtrados = turnos.value.filter(t => 
      t.fecha < hoy || 
      ['CANCELADO', 'COMPLETADO'].includes(t.estado)
    )
    // Ordenar por fecha más reciente primero
    filtrados.sort((a, b) => {
      const fechaA = new Date(a.fecha + 'T' + a.hora)
      const fechaB = new Date(b.fecha + 'T' + b.hora)
      return fechaB - fechaA
    })
  }
  
  // Paginación solo para historial
  if (tabActiva.value === 'historial') {
    const inicio = (pagina.value - 1) * itemsPorPagina
    return filtrados.slice(inicio, inicio + itemsPorPagina)
  }
  
  return filtrados
})

// Computed: contadores
const contadorProximos = computed(() => {
  const hoy = new Date().toISOString().split('T')[0]
  return turnos.value.filter(t => 
    t.fecha >= hoy && 
    ['RESERVADO', 'CONFIRMADO'].includes(t.estado)
  ).length
})

const contadorHistorial = computed(() => {
  const hoy = new Date().toISOString().split('T')[0]
  return turnos.value.filter(t => 
    t.fecha < hoy || 
    ['CANCELADO', 'COMPLETADO'].includes(t.estado)
  ).length
})

// Computed: próxima fecha
const proximoEnDias = computed(() => {
  const hoy = new Date().toISOString().split('T')[0]
  const proximos = turnos.value.filter(t => 
    t.fecha >= hoy && 
    ['RESERVADO', 'CONFIRMADO'].includes(t.estado)
  )
  
  if (proximos.length === 0) return 0
  
  const fechaProximo = new Date(proximos[0].fecha)
  const hoyDate = new Date(hoy)
  const diferencia = Math.ceil((fechaProximo - hoyDate) / (1000 * 60 * 60 * 24))
  
  return Math.max(0, diferencia)
})

// Computed: paginación para historial
const totalPaginas = computed(() => {
  if (tabActiva.value !== 'historial') return 1
  
  const hoy = new Date().toISOString().split('T')[0]
  const historial = turnos.value.filter(t => 
    t.fecha < hoy || 
    ['CANCELADO', 'COMPLETADO'].includes(t.estado)
  )
  
  return Math.max(1, Math.ceil(historial.length / itemsPorPagina))
})

const paginasVisibles = computed(() => {
  const total = totalPaginas.value
  const current = pagina.value
  const pages = []
  
  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
      pages.push('...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...')
      for (let i = total - 3; i <= total; i++) pages.push(i)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }
  
  return pages
})

// FIXED: Indicador de tabs que se mueve correctamente
const indicatorStyle = computed(() => {
  if (!tabProximos.value || !tabHistorial.value) {
    return {
      transform: `translateX(${tabActiva.value === 'proximos' ? '0%' : '100%'})`,
      width: '50%'
    }
  }
  const position = tabActiva.value === 'proximos' ? 0 : 100
  return {
    transform: `translateX(${position}%)`,
    width: '50%'
  }
})

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