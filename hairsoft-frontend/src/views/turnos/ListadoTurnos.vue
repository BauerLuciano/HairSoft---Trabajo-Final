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
            <input v-model="filtros.busqueda" placeholder="Nombre o apellido..." class="filter-input"/>
          </div>
          <div class="filter-group">
            <label>Desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input"/>
          </div>
          <div class="filter-group">
            <label>Hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input"/>
          </div>

          <div v-if="userRol !== 'PELUQUERO'" class="filter-group">
            <label>Peluquero</label>
            <select v-model="filtros.peluquero" class="filter-input">
              <option value="">Todos</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">{{ p.nombre }} {{ p.apellido }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos</option>
              <option value="RESERVADO">Reservado</option>
              <option value="CONFIRMADO">Confirmado</option>
              <option value="COMPLETADO">Completado</option>
              <option value="CANCELADO">Cancelado</option>
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
              <Trash2 :size="16" /> Limpiar
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
              <th>Precio / Pago</th>
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
                    <span v-if="turno.oferta_activa" class="badge-reoferta">🔥 Reoferta</span>
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
                  <Clock :size="16" /> {{ turno.duracion_total || 0 }} min
                </div>
              </td>

              <td>
                <span class="badge-estado" :class="getEstadoClass(turno.estado, turno.tipo_pago)">
                  {{ getEstadoTexto(turno.estado, turno.tipo_pago) }}
                </span>
              </td>
              
              <td>
                <div class="precio-total-container">
                  <span class="precio-total">${{ formatPrecio(turno.monto_total) }}</span>
                  
                  <div class="medio-pago-wrapper">
                     <div v-if="turno.medio_pago && turno.medio_pago !== 'PENDIENTE'" 
                          class="medio-pago-badge" 
                          :class="getClaseMedioPago(turno.medio_pago)">
                        <component :is="getIconoMedioPago(turno.medio_pago)" :size="12" />
                        <span>{{ getMedioPagoLabel(turno.medio_pago) }}</span>
                     </div>
                     <div v-else-if="!turno.medio_pago" style="font-size: 10px; color: red;">
                        (Sin dato pago)
                     </div>
                  </div>

                  <div class="detalle-financiero">
                    <div v-if="esEstadoActivo(turno.estado) && turno.tipo_pago === 'SENA_50'" class="saldo-pendiente">
                      <small>✅ Seña: ${{ formatPrecio(turno.monto_seña) }}</small>
                      <small class="falta">⚠️ Resta: ${{ formatPrecio(turno.monto_total - (turno.monto_seña || 0)) }}</small>
                    </div>

                    <div v-else-if="(esEstadoActivo(turno.estado) && turno.tipo_pago === 'TOTAL') || turno.estado === 'COMPLETADO'" class="saldo-ok">
                      <small>✅ Pagado Total</small>
                    </div>

                    <div v-else-if="turno.estado === 'CANCELADO' && turno.monto_seña > 0">
                      <div v-if="turno.reembolsado" class="saldo-favor">
                        <small>💰 A favor del cliente: ${{ formatPrecio(turno.monto_seña) }}</small>
                      </div>
                      <div v-else class="saldo-pendiente">
                        <small v-if="turno.canal === 'PRESENCIAL'" style="color: #f59e0b; font-weight: bold;">⚠️ Devolución Pendiente</small>
                        <small v-else style="color: #ef4444; font-weight: bold;">🔒 Retenido (Penalidad)</small>
                      </div>
                    </div>
                  </div>
                </div>
              </td>

              <td>
                <div class="action-buttons">
                  <button @click="verDetalleTurno(turno)" class="action-button view" title="Ver Detalle">
                    <Eye :size="14"/>
                  </button>
                  
                  <button v-if="turno.puede_modificar" @click="modificarTurno(turno.id)" class="action-button edit" title="Editar">
                    <Edit3 :size="14"/>
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
import axios from '../../utils/axiosConfig'
import { 
  Plus, Trash2, Edit3, Check, SearchX, ChevronLeft, ChevronRight, 
  Eye, CreditCard, Clock, Banknote, Smartphone, HelpCircle, ArrowRightLeft 
} from 'lucide-vue-next'
import Swal from 'sweetalert2'

const router = useRouter()
const turnos = ref([])
const peluqueros = ref([])
const pagina = ref(1)
const itemsPorPagina = 7
const filtros = ref({ busqueda: '', peluquero: '', estado: '', canal: '', fechaDesde: '', fechaHasta: '' })

// 🛡️ REGLA ORO: Obtenemos el rol del localStorage
const userRol = localStorage.getItem('user_rol'); 

const esEstadoActivo = (estado) => ['RESERVADO', 'CONFIRMADO'].includes(estado);

const formatFecha = s => { if(!s) return '-'; try { const [y,m,d] = s.split('-'); return `${d}/${m}/${y}`; } catch(e) { return s; } }
const formatHora = s => (s && s.length >= 5) ? s.slice(0,5) : '-'
const formatPrecio = (p) => (!p ? '0.00' : parseFloat(p).toFixed(2))

const getServiciosLista = s => {
  if (!s) return []
  if (Array.isArray(s)) return s.map(x => (typeof x === 'object' && x.nombre) ? x.nombre : String(x))
  return []
}

const getMedioPagoLabel = (mp) => {
  if (!mp) return 'Pendiente'
  const m = mp.toUpperCase()
  if (m.includes('EFECTIVO')) return 'Efectivo'
  if (m.includes('MERCADO') || m.includes('MP')) return 'Mercado Pago (Web)'
  if (m.includes('TARJETA') || m.includes('CREDITO') || m.includes('DEBITO')) return 'Tarjeta'
  if (m.includes('TRANSF')) return 'Transferencia'
  return mp
}

const getClaseMedioPago = (mp) => {
    if (!mp) return 'otro'
    const m = mp.toUpperCase()
    if (m.includes('MERCADO')) return 'mp'
    if (m.includes('EFECTIVO')) return 'efectivo'
    if (m.includes('TARJETA') || m.includes('CREDITO') || m.includes('DEBITO')) return 'tarjeta'
    if (m.includes('TRANSF')) return 'transferencia'
    return 'otro'
}

const getIconoMedioPago = (mp) => {
    if (!mp) return HelpCircle
    const m = mp.toUpperCase()
    if (m.includes('MERCADO')) return Smartphone
    if (m.includes('EFECTIVO')) return Banknote
    if (m.includes('TARJETA') || m.includes('CREDITO') || m.includes('DEBITO')) return CreditCard
    if (m.includes('TRANSF')) return ArrowRightLeft
    return HelpCircle
}

const getEstadoTexto = (estado, tipoPago) => {
  if (estado === 'RESERVADO') return tipoPago === 'TOTAL' ? 'Reservado (Pagado)' : 'Reservado (Seña)'
  if (estado === 'CONFIRMADO') return 'Confirmado'
  if (estado === 'COMPLETADO') return 'Completado'
  if (estado === 'CANCELADO') return 'Cancelado'
  return estado
}

const getEstadoClass = (estado, tipoPago) => {
  if (estado === 'RESERVADO' || estado === 'CONFIRMADO') return tipoPago === 'TOTAL' ? 'estado-success' : 'estado-warning'
  if (estado === 'COMPLETADO') return 'estado-completado'
  if (estado === 'CANCELADO') return 'estado-cancelado'
  return 'estado-secondary'
}

const calcularPrecioTotal = (t) => {
  if (t.monto_total > 0) return t.monto_total
  if (t.servicios && Array.isArray(t.servicios)) return t.servicios.reduce((a, b) => a + (b.precio || 0), 0)
  return 0
}

const verDetalleTurno = async (turno) => {
    const precioTotal = calcularPrecioTotal(turno)
    const montoSeña = turno.monto_seña || 0
    const saldo = precioTotal - montoSeña
    const cliente = `${turno.cliente_nombre} ${turno.cliente_apellido}`
    
    let html = `
      <div style="text-align: left; color: #333; font-family: sans-serif;">
        <div style="border-bottom: 2px solid #3b82f6; padding-bottom: 10px; margin-bottom: 15px;">
           <h3 style="margin: 0; color: #3b82f6;">Ficha de Turno #${turno.id}</h3>
           <small style="color: #666;">${formatFecha(turno.fecha)} - ${formatHora(turno.hora)}</small>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
           <div><strong>Cliente:</strong><br>${cliente}</div>
           <div><strong>Peluquero:</strong><br>${turno.peluquero_nombre}</div>
           <div><strong>Estado:</strong><br>${getEstadoTexto(turno.estado, turno.tipo_pago)}</div>
           <div><strong>Canal:</strong><br>${turno.canal}</div>
           <div><strong>Medio Pago:</strong><br>${getMedioPagoLabel(turno.medio_pago)}</div>
        </div>
        <div style="background: #f3f4f6; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
           <strong>Servicios:</strong>
           <ul style="margin: 5px 0; padding-left: 20px;">
             ${getServiciosLista(turno.servicios).map(s => `<li>${s}</li>`).join('')}
           </ul>
        </div>
        <div style="text-align: right; font-size: 1.1em;">
           <p style="margin: 5px 0;">Total: <strong>$${formatPrecio(precioTotal)}</strong></p>
           ${turno.tipo_pago === 'SENA_50' ? `<p style="margin: 5px 0; color: #f59e0b;">Falta abonar: <strong>$${formatPrecio(saldo)}</strong></p>` : '<p style="color: #10b981; margin: 5px 0;">✅ Pagado Total</p>'}
        </div>
      </div>`
    await Swal.fire({ html: html, showCloseButton: true, confirmButtonText: 'Cerrar', confirmButtonColor: '#3b82f6' })
}

const cargarPeluqueros = async () => { 
  if (userRol !== 'PELUQUERO') {
    try { const res = await axios.get('/api/peluqueros/'); peluqueros.value = res.data; } catch(e){} 
  }
}

const cargarTurnos = async () => {
    try {
        const p = new URLSearchParams(filtros.value)
        const res = await axios.get(`/api/turnos/?${p.toString()}`);
        const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
        turnos.value = data.sort((a, b) => new Date(`${b.fecha}T${b.hora}`) - new Date(`${a.fecha}T${a.hora}`))
    } catch(e) { console.error(e) }
}

const confirmarPagoTotal = async (turno) => {
  const precio = calcularPrecioTotal(turno)
  const falta = precio - (turno.monto_seña || 0)
  const { isConfirmed } = await Swal.fire({ 
      title: 'Cobrar Restante', text: `Monto a abonar: $${falta}`, icon: 'info', showCancelButton: true, confirmButtonText: 'Cobrar y Guardar', confirmButtonColor: '#10b981', cancelButtonColor: '#6b7280'
  })
  if (isConfirmed) {
      await axios.post(`/api/turnos/${turno.id}/actualizar-pago/`, { tipo_pago: 'TOTAL', monto_total: precio });
      cargarTurnos()
      Swal.fire({ title: '¡Cobrado!', icon: 'success', timer: 1500, showConfirmButton: false })
  }
}

// ✅ LIBERADO: Completado forzoso para Gestión
const completarTurno = async (turno) => {
  const { isConfirmed } = await Swal.fire({ 
      title: 'Finalizar Turno', 
      text: `¿Marcar el turno de ${turno.cliente_nombre} como COMPLETADO?`, 
      icon: 'warning', 
      showCancelButton: true, 
      confirmButtonText: 'Sí, completar', 
      confirmButtonColor: '#10b981', 
      cancelButtonColor: '#d33'
  })
  if (isConfirmed) {
      try {
        await axios.post(`/api/turnos/${turno.id}/cambiar-estado/COMPLETADO/`);
        cargarTurnos()
        Swal.fire({ title: '¡Hecho!', text: 'Atención finalizada correctamente.', icon: 'success', timer: 1500, showConfirmButton: false })
      } catch (e) {
        Swal.fire({ title: 'Error', text: 'No se pudo cambiar el estado. Revisa si falta cobrar.', icon: 'error' });
      }
  }
}

const cancelarTurno = async (turno) => {
  const { isConfirmed } = await Swal.fire({ 
      title: 'Cancelar Turno', text: '¿Estás seguro que deseas cancelar?', icon: 'error', showCancelButton: true, confirmButtonText: 'Sí, cancelar', confirmButtonColor: '#ef4444', cancelButtonColor: '#6b7280'
  })
  if (isConfirmed) {
      await axios.post(`/api/turnos/${turno.id}/cambiar-estado/CANCELADO/`);
      cargarTurnos()
      Swal.fire({ title: 'Cancelado', icon: 'success', timer: 1500, showConfirmButton: false })
  }
}

const irARegistrar = () => router.push('/turnos/crear-presencial')
const modificarTurno = (id) => router.push(`/turnos/modificar/${id}`)
const limpiarFiltros = () => { filtros.value = { busqueda:'', peluquero:'', estado:'', canal:'', fechaDesde:'', fechaHasta:'' }; cargarTurnos() }

const turnosFiltradosPaginados = computed(() => {
    let res = turnos.value
    if (filtros.value.busqueda) res = res.filter(t => (t.cliente_nombre+t.cliente_apellido).toLowerCase().includes(filtros.value.busqueda.toLowerCase()))
    const inicio = (pagina.value - 1) * itemsPorPagina
    return res.slice(inicio, inicio + itemsPorPagina)
})
const totalPaginas = computed(() => Math.ceil(turnos.value.length / itemsPorPagina))
const paginaAnterior = () => { if(pagina.value>1) pagina.value-- }
const paginaSiguiente = () => { if(pagina.value<totalPaginas.value) pagina.value++ }

const mostrarBotonCompletar = (turno) => {
    if (['COMPLETADO', 'CANCELADO'].includes(turno.estado)) return false;
    // Si es ADMIN o RECEPCIONISTA, puede completar CUALQUIERA activo
    if (['ADMINISTRADOR', 'RECEPCIONISTA'].includes(userRol)) return true;
    return turno.puede_completar;
}

const puedeCancelarTurno = (turno) => {
    if (['COMPLETADO', 'CANCELADO'].includes(turno.estado)) return false;
    const esPersonalGestion = ['ADMINISTRADOR', 'RECEPCIONISTA', 'ADMIN'].includes(userRol?.toUpperCase());
    return turno.puede_cancelar || esPersonalGestion;
}

onMounted(() => { cargarPeluqueros(); cargarTurnos(); })
watch(filtros.value, () => cargarTurnos())
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

.estado-completado {
  background: var(--bg-tertiary);
  color: #0ea5e9; /* Azul completado */
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
.action-button.view:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }

.action-button.edit {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.action-button.edit:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }

.action-button.pagar {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}
.action-button.pagar:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4); border-color: #10b981; }

.action-button.complete {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}
.action-button.complete:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4); border-color: #10b981; }

.action-button.delete {
  background: var(--bg-tertiary);
  border: 1px solid var(--error-color);
  color: var(--error-color);
}
.action-button.delete:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4); border-color: var(--error-color); }

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
.btn-reintentar:hover { background: linear-gradient(135deg, #0284c7, #0369a1); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5); }

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
.pagination button:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.pagination button:disabled { background: var(--bg-tertiary); color: var(--text-tertiary); cursor: not-allowed; transform: none; border: 1px solid var(--border-color); opacity: 0.5; }
.pagination span { color: var(--text-primary); font-weight: 700; letter-spacing: 0.8px; font-size: 0.95rem; }

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

/* ✅ ESTILOS FINANCIEROS INTELIGENTES (ADD-ON) */
.detalle-financiero { display: flex; flex-direction: column; gap: 2px; margin-top: 4px; }
.saldo-pendiente small { display: block; font-size: 0.75rem; color: var(--text-secondary); }
.saldo-pendiente .falta { color: #f59e0b; font-weight: 700; }
.saldo-ok small { color: #10b981; font-weight: 700; font-size: 0.75rem; background: rgba(16, 185, 129, 0.1); padding: 2px 6px; border-radius: 4px; }
.saldo-favor small { color: #3b82f6; font-weight: 700; font-size: 0.75rem; background: rgba(59, 130, 246, 0.1); padding: 2px 6px; border-radius: 4px; }

/* 🔥 ESTILOS PARA MEDIO DE PAGO */
.medio-pago-wrapper { margin-top: 2px; margin-bottom: 4px; }
.medio-pago-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.68rem; font-weight: 800; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.medio-pago-badge.mp { background: rgba(14, 165, 233, 0.12); color: #0ea5e9; border: 1px solid rgba(14, 165, 233, 0.25); }
.medio-pago-badge.efectivo { background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25); }
/* Estilos nuevos para completar la colección */
.medio-pago-badge.tarjeta {
  background: rgba(139, 92, 246, 0.12); /* Violeta */
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.25);
}

.medio-pago-badge.transferencia {
  background: rgba(245, 158, 11, 0.12); /* Naranja */
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.25);
}
.medio-pago-badge.otro { background: rgba(156, 163, 175, 0.12); color: #6b7280; border: 1px solid rgba(156, 163, 175, 0.25); }
</style>