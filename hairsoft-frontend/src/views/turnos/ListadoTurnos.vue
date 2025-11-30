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
                <span class="badge-estado" :class="getEstadoClass(turno.estado)">
                  {{ formatearEstado(turno.estado) }}
                </span>
              </td>
              <td>
                <div class="pago-container">
                  <span class="badge-pago" :class="getPagoClass(turno.tipo_pago)">
                    {{ getPagoTexto(turno.tipo_pago) }}
                  </span>
                  <div v-if="turno.tipo_pago === 'SENA_50'" class="monto-detalle">
                    <span class="monto-seña">${{ formatPrecio(turno.monto_seña) }}</span>
                    <span class="monto-total">/ ${{ formatPrecio(turno.monto_total) }}</span>
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button v-if="turno.puede_modificar" @click="modificarTurno(turno.id)" class="action-button edit" title="Editar"><Edit3 :size="14"/></button>
                  <button v-if="turno.puede_senar" @click="procesarSena(turno)" class="action-button sena" title="Señar"><DollarSign :size="14"/></button>
                  <button v-if="turno.puede_cancelar" @click="cancelarTurnoConReoferta(turno)" class="action-button delete" title="Cancelar"><Trash2 :size="14"/></button>
                  <button v-if="turno.puede_completar" @click="completarTurno(turno.id)" class="action-button complete" title="Completar"><Check :size="14"/></button>
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
import { Calendar, Plus, Trash2, Edit3, Check, SearchX, ChevronLeft, ChevronRight, DollarSign } from 'lucide-vue-next'
import Swal from 'sweetalert2'

const router = useRouter()
const turnos = ref([])
const peluqueros = ref([])
const pagina = ref(1)
const itemsPorPagina = 10

// ✅ LISTA LIMPIA: SIN 'DISPONIBLE'
const estadosDisponibles = ref(['RESERVADO', 'CONFIRMADO', 'COMPLETADO', 'CANCELADO'])

const filtros = ref({
  busqueda: '',
  peluquero: '',
  estado: '',
  canal: '',
  fechaDesde: '',
  fechaHasta: ''
})

// --- FUNCIONES AUXILIARES ---
const formatFecha = s => {
    if(!s) return '-';
    try { const [y,m,d] = s.split('-'); return `${d}/${m}/${y}`; } catch(e) { return s; }
}
const formatHora = s => (s && s.length >= 5) ? s.slice(0,5) : '-'
const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  return parseFloat(precio).toFixed(2)
}
const getServiciosLista = s => Array.isArray(s) ? s.map(x => typeof x === 'string' ? x : x.nombre) : []
const formatearEstado = e => ({'RESERVADO':'Reservado','CONFIRMADO':'Confirmado','COMPLETADO':'Completado','CANCELADO':'Cancelado'}[e] || e)
const getEstadoClass = e => ({'RESERVADO':'estado-warning','CONFIRMADO':'estado-info','COMPLETADO':'estado-success','CANCELADO':'estado-danger'}[e] || 'estado-secondary')
const getPagoClass = t => (t === 'SENA_50' ? 'pago-sena' : (t === 'TOTAL' ? 'pago-total' : 'pago-pendiente'))
const getPagoTexto = t => (t === 'SENA_50' ? 'Seña 50%' : (t === 'TOTAL' ? 'Total' : 'Pendiente'))

// --- CARGA DE DATOS ---
const cargarPeluqueros = async () => {
    try {
        const res = await fetch('http://localhost:8000/usuarios/api/peluqueros/', {
            headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
        })
        peluqueros.value = await res.json()
    } catch(e) {}
}

const cargarTurnos = async () => {
    try {
        const token = localStorage.getItem('token')
        const p = new URLSearchParams()
        // Enviamos filtros al backend
        if(filtros.value.peluquero) p.append('peluquero', filtros.value.peluquero)
        if(filtros.value.estado) p.append('estado', filtros.value.estado)
        if(filtros.value.canal) p.append('canal', filtros.value.canal)
        if(filtros.value.fechaDesde) p.append('fecha_desde', filtros.value.fechaDesde)
        if(filtros.value.fechaHasta) p.append('fecha_hasta', filtros.value.fechaHasta)

        const res = await fetch(`http://localhost:8000/usuarios/api/turnos/?${p.toString()}`, {
            headers: { 'Authorization': `Token ${token}` }
        })
        const data = await res.json()
        
        // ✅ CORRECCIÓN: ORDENAR POR FECHA MÁS RECIENTE PRIMERO
        const turnosOrdenados = data.sort((a, b) => {
          const fechaA = new Date(`${a.fecha}T${a.hora}`)
          const fechaB = new Date(`${b.fecha}T${b.hora}`)
          return fechaB - fechaA // Orden descendente (más reciente primero)
        })
        
        // Procesamos datos
        turnos.value = turnosOrdenados.map(t => ({
            ...t,
            puede_senar: t.estado === 'RESERVADO' && t.tipo_pago === 'PENDIENTE',
            servicios: Array.isArray(t.servicios) ? t.servicios : [],
            canal: t.canal || 'PRESENCIAL'
        }))
    } catch(e) {
        console.error(e)
        Swal.fire('Error', 'No se pudieron cargar los turnos', 'error')
    }
}

const cancelarTurnoConReoferta = async (turno) => {
    try {
        // PASO 1: Consultar al Backend
        console.log(`🔍 Consultando interesados para turno ${turno.id}...`);
        
        const resInteresados = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/interesados/`, {
            headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
        });

        let cantidadInteresados = 0;

        if (resInteresados.ok) {
            const dataInteresados = await resInteresados.json();
            console.log("✅ Respuesta Backend:", dataInteresados);
            
            // Forzamos conversión a número para evitar problemas de tipos
            cantidadInteresados = parseInt(dataInteresados.cantidad);
            
            // Si parseInt devuelve NaN (por error), lo volvemos 0
            if (isNaN(cantidadInteresados)) cantidadInteresados = 0;
            
        } else {
            console.error("❌ Error al consultar interesados. Status:", resInteresados.status);
            // No detenemos el flujo, asumimos 0 pero logueamos el error
        }

        console.log(`📊 Cantidad final detectada: ${cantidadInteresados}`);

        // PASO 2: Calcular reembolso
        const fechaTurno = new Date(`${turno.fecha}T${turno.hora}`);
        const ahora = new Date();
        const diffHoras = (fechaTurno - ahora) / (1000 * 60 * 60);
        const correspondeReembolso = diffHoras >= 3;
        
        // PASO 3: Armar HTML
        let html = `<div style="text-align:left; font-size: 0.95rem;">
            <p><strong>Cliente:</strong> ${turno.cliente_nombre}</p>
            <p><strong>Fecha:</strong> ${formatFecha(turno.fecha)} ${formatHora(turno.hora)}</p>
            <hr style="margin: 10px 0; border-color: #eee;">`;

        // Info de Reembolso
        if(turno.monto_seña > 0) {
            html += correspondeReembolso 
                ? `<div style="background:#d1fae5;padding:8px;border-radius:6px;color:#065f46;margin-bottom:8px;display:flex;align-items:center;gap:5px;">
                     <span>💰</span> <strong>Se intentará reembolso automático</strong>
                   </div>`
                : `<div style="background:#fee2e2;padding:8px;border-radius:6px;color:#991b1b;margin-bottom:8px;display:flex;align-items:center;gap:5px;">
                     <span>⚠️</span> <strong>Sin reembolso (< 3hs)</strong>
                   </div>`;
        }

        // Info de Interesados (¡LÓGICA CORREGIDA!)
        if (cantidadInteresados > 0) {
            html += `<div style="background:#eff6ff;padding:10px;border-radius:6px;color:#1e40af;border:1px solid #bfdbfe;">
                        <h3 style="margin:0 0 5px 0;font-size:1rem;">🚀 ¡Reoferta Activa!</h3>
                        <p style="margin:0;">Hay <strong>${cantidadInteresados} personas</strong> en lista de espera.</p>
                        <small>Se les enviará una notificación automática ahora mismo.</small>
                     </div>`;
        } else {
            html += `<div style="color:#6b7280;font-style:italic;margin-top:5px;">
                        ℹ️ No hay interesados en lista de espera. El turno quedará disponible.
                     </div>`;
        }
        html += `</div>`;

        // PASO 4: Mostrar Alerta
        const confirm = await Swal.fire({
            title: cantidadInteresados > 0 ? '¿Cancelar y Reofertar?' : '¿Cancelar Turno?',
            html: html,
            icon: cantidadInteresados > 0 ? 'info' : 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sí, Confirmar',
            cancelButtonText: 'Volver',
            confirmButtonColor: '#d33',
            reverseButtons: true
        });

        // PASO 5: Ejecutar Cancelación
        if(confirm.isConfirmed) {
            Swal.fire({ title: 'Procesando...', didOpen: () => Swal.showLoading() });
            
            const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turno.id}/cancelar-con-reoferta/`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Token ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await res.json();
            
            if(res.ok && data.status === 'ok') {
                await cargarTurnos();
                
                let msgFinal = data.message || 'Turno cancelado con éxito';
                // Usamos el dato que devuelve el backend en la cancelación para confirmar
                if (data.reoferta_iniciada) {
                    msgFinal = `✅ Turno cancelado.<br>🚀 Se notificó a ${data.interesados} interesados.`;
                }

                Swal.fire({
                    title: '¡Listo!',
                    html: msgFinal,
                    icon: 'success'
                });

            } else {
                Swal.fire('Error', data.error || 'No se pudo cancelar', 'error');
            }
        }

    } catch(e) { 
        console.error("💥 Error en cancelarTurnoConReoferta:", e);
        Swal.fire('Error', 'Fallo de conexión al verificar interesados', 'error'); 
    }
}

const irARegistrar = () => router.push('/turnos/crear-presencial')
const modificarTurno = (id) => router.push(`/turnos/modificar/${id}`)
const procesarSena = async (turno) => { /* Lógica igual */ }
const completarTurno = async (id) => { /* Lógica igual */ }

const limpiarFiltros = () => {
    filtros.value = { busqueda:'', peluquero:'', estado:'', canal:'', fechaDesde:'', fechaHasta:'' }
    cargarTurnos()
}

// ✅ FILTRO CLIENTE-SIDE SOLO PARA BUSQUEDA TEXTUAL
// El resto de filtros (canal, estado) YA los hizo el backend
const turnosFiltrados = computed(() => {
    let res = turnos.value
    if (filtros.value.busqueda) {
        const b = filtros.value.busqueda.toLowerCase()
        res = res.filter(t => `${t.cliente_nombre} ${t.cliente_apellido}`.toLowerCase().includes(b))
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

// Al cambiar filtros, recargamos desde backend
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

/* ✅ CORRECCIÓN: ESTILOS PARA BADGES DE PAGO */
.badge-pago {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
  white-space: nowrap;
  border: 2px solid;
}

.pago-sena {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border-color: #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.3);
}

.pago-total {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-color: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.3);
}

.pago-pendiente {
  background: rgba(156, 163, 175, 0.15);
  color: #6b7280;
  border-color: #6b7280;
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* ✅ CORRECCIÓN: CONTENEDOR DE PAGO MEJORADO */
.pago-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  min-width: 100px;
}

.monto-detalle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.monto-seña {
  color: #f59e0b;
  font-weight: 700;
}

.monto-total {
  color: var(--text-tertiary);
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
  
  .pago-container {
    min-width: auto;
    align-items: flex-start;
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
  
  .badge-estado, .badge-pago {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
  
  .action-button {
    width: 36px;
    height: 36px;
  }
}
</style>