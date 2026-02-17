<template>
  <div class="page-background">
    <div class="main-card-container">
      <div class="turno-container">
        <div class="header-section">
          <h2>
            <Calendar class="header-icon" />
            Modificar Turno
          </h2>
          <button @click="volverAlListado" class="btn-back">
            <ArrowLeft :size="18" />
            Volver
          </button>
        </div>

        <div v-if="cargando" class="loading-state">
          <Loader2 class="spinner-icon" :size="48" />
          <p>Cargando datos del turno...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <AlertCircle class="error-icon" :size="48" />
          <h3>Error</h3>
          <p>{{ error }}</p>
          <button @click="volverAlListado" class="btn-cancelar-premium">
            ← Volver al listado
          </button>
        </div>

        <div v-else class="form-content">
          <!-- Cliente -->
          <div class="card-modern">
            <div class="card-header">
              <div class="card-icon"><Users :size="20" /></div>
              <h3>Cliente</h3>
            </div>
            
            <div class="input-group">
              <div class="row-search">
                <div class="search-wrapper">
                  <Search class="search-icon" :size="18" />
                  <input
                    type="text"
                    :value="form.clienteNombre"
                    readonly
                    placeholder="Cliente del turno"
                    class="input-modern cliente-activo"
                  />
                </div>
                
                <button @click="abrirModalCambiarCliente" class="btn-nuevo">
                  <Edit3 :size="18" /> Cambiar
                </button>
              </div>
            </div>
          </div>

          <!-- Categorías -->
          <div class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><FolderOpen :size="20" /></div>
              <h3>Categoría</h3>
            </div>
            <div class="grid-chips">
              <button 
                v-for="categoria in categorias" 
                :key="categoria.id"
                class="chip-modern"
                :class="{ 'chip-active': categoriasSeleccionadas.includes(categoria.id) }"
                @click="toggleCategoria(categoria.id)"
              >
                <Tag :size="14" /> {{ categoria.nombre }}
              </button>
            </div>
          </div>

          <!-- Servicios -->
          <div v-if="categoriasSeleccionadas.length > 0" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><Scissors :size="20" /></div>
              <h3>Servicios</h3>
            </div>
            
            <div v-if="serviciosFiltrados.length === 0" class="no-resultados">
              <Inbox class="no-resultados-icon" :size="48" />
              <p>No hay servicios en esta categoría</p>
            </div>
            
            <div v-else class="grid-servicios">
              <div 
                v-for="servicio in serviciosFiltrados" 
                :key="servicio.id"
                class="card-servicio"
                :class="{ 'servicio-active': form.servicios_ids.includes(servicio.id) }"
                @click="toggleServicio(servicio)"
              >
                <div class="servicio-check">
                  <Check v-if="form.servicios_ids.includes(servicio.id)" :size="16" />
                </div>
                <div class="servicio-content">
                  <span class="servicio-nombre">{{ servicio.nombre }}</span>
                  <div class="servicio-details">
                    <span class="servicio-precio">${{ servicio.precio }}</span>
                    <span class="servicio-duracion">{{ servicio.duracion }}m</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Profesional (cards) -->
          <div v-if="form.servicios_ids.length > 0" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><UserCheck :size="20" /></div>
              <h3>Profesional</h3>
            </div>
            
            <div class="profesionales-grid">
              <div 
                v-for="p in peluqueros" 
                :key="p.id"
                class="profesional-card"
                :class="{ 
                  'profesional-selected': Number(form.peluquero) === Number(p.id),
                  'profesional-disabled': Number(p.id) === Number(form.cliente)
                }"
                @click="Number(p.id) !== Number(form.cliente) ? seleccionarPeluquero(p.id) : null"
              >
                <div class="profesional-avatar">
                  <User :size="24" />
                </div>
                <div class="profesional-info">
                  <div class="profesional-nombre">{{ p.nombre }} {{ p.apellido || '' }}</div>
                  <div v-if="Number(p.id) === Number(form.cliente)" class="profesional-badge-cliente">Es el cliente</div>
                  <div v-else-if="Number(form.peluquero) === Number(p.id)" class="profesional-badge-selected">✓ Seleccionado</div>
                </div>
              </div>
            </div>
            
            <div v-if="Number(form.peluquero) === Number(form.cliente) && form.cliente" class="msg-error mt-2">
              <AlertCircle :size="14" /> No puedes seleccionar al mismo profesional como cliente.
            </div>
          </div>

          <!-- Silla -->
          <div v-if="form.peluquero && Number(form.peluquero) !== Number(form.cliente)" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);">
                <Armchair :size="20" />
              </div>
              <h3>Puesto de Trabajo</h3>
            </div>
            
            <div class="input-group">
              <div class="custom-select-wrapper">
                <select v-model="form.silla" class="form-control-select">
                  <option :value="null">✨ Asignación Automática (Recomendado)</option>
                  <option v-for="silla in sillasActivas" :key="silla.id" :value="silla.id">
                    🪑 {{ silla.nombre }}
                  </option>
                </select>
                <ChevronDown class="select-icon" :size="18" />
              </div>
              <small style="color: #6b7280; font-size: 0.85rem; margin-top: 8px; display: block; padding-left: 5px;">
                <Info :size="14" style="vertical-align: middle; margin-right: 4px;" />
                Si eliges automático, el sistema buscará la primera silla libre.
              </small>
            </div>
          </div>

          <!-- Calendario -->
          <div v-if="form.peluquero && Number(form.peluquero) !== Number(form.cliente)" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><CalendarDays :size="20" /></div>
              <h3>Fecha</h3>
            </div>
            
            <div class="calendar-wrapper">
              <div class="calendar-header">
                <button @click="cambiarMes(-1)" class="btn-nav-cal"><ChevronLeft :size="20" /></button>
                <span class="mes-titulo">{{ nombreMesActual }} {{ currentYear }}</span>
                <button @click="cambiarMes(1)" class="btn-nav-cal"><ChevronRight :size="20" /></button>
              </div>

              <div class="calendar-days-header">
                <span v-for="d in ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb']" :key="d">{{ d }}</span>
              </div>

              <div class="calendar-grid">
                <div v-for="i in startingDayOfWeek" :key="'empty-'+i" class="day-empty"></div>
                <button 
                  v-for="day in daysInMonth" 
                  :key="day"
                  class="day-btn"
                  :class="{
                    'day-today': esHoy(day),
                    'day-selected': esDiaSeleccionado(day),
                    'day-disabled': !esDiaSeleccionable(day)
                  }"
                  :disabled="!esDiaSeleccionable(day)"
                  @click="seleccionarDiaCalendario(day)"
                >
                  {{ day }}
                  <span v-if="esHoy(day)" class="badge-today">HOY</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Horarios -->
          <div v-if="form.fecha" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><Clock :size="20" /></div>
              <h3>Horarios Disponibles</h3>
            </div>
            
            <div v-if="cargandoHorarios" class="loading-spinner">
              <Loader2 class="spinner-icon" :size="32" />
              <p>Calculando disponibilidad...</p>
            </div>
            
            <div v-else-if="horariosGenerados.length === 0" class="no-resultados">
              <Clock class="no-resultados-icon" :size="48" />
              <p>Local Cerrado en esta fecha</p>
            </div>
            
            <div v-else class="grid-horarios">
              <div
                v-for="hora in horariosGenerados"
                :key="hora"
                class="hora-card"
                :class="{
                  'hora-selected': form.hora === hora,
                  'hora-actual': esHorarioDelTurnoActual(hora),
                  'hora-ocupada': !esHorarioDisponibleCompleto(hora) && !esHorarioDelTurnoActual(hora)
                }"
                @click="esHorarioDisponibleCompleto(hora) ? seleccionarHora(hora) : null"
              >
                <span class="hora-texto">{{ hora }}</span>
                <span v-if="esHorarioDelTurnoActual(hora)" class="etiqueta-actual">ACTUAL</span>
                <span v-else-if="!esHorarioDisponibleCompleto(hora)" class="etiqueta-ocupado">OCUPADO</span>
              </div>
            </div>
          </div>

          <!-- Confirmación y Pago -->
          <div v-if="form.hora" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><Receipt :size="20" /></div>
              <h3>Confirmación</h3>
            </div>

            <div class="resumen-grid">
              <div class="resumen-item total">
                <span>Total a Pagar:</span>
                <strong>${{ calcularTotal() }}</strong>
              </div>
            </div>

            <div class="pago-section">
              <div class="pago-options">
                <label class="radio-box" :class="{ 'radio-active': form.tipo_pago === 'SENA_50' }">
                  <input type="radio" v-model="form.tipo_pago" value="SENA_50" class="hidden-radio">
                  <div class="radio-content">
                    <span>Seña 50%</span>
                    <strong>${{ calcularSena() }}</strong>
                  </div>
                </label>
                <label class="radio-box" :class="{ 'radio-active': form.tipo_pago === 'TOTAL' }">
                  <input type="radio" v-model="form.tipo_pago" value="TOTAL" class="hidden-radio">
                  <div class="radio-content">
                    <span>Total</span>
                    <strong>${{ calcularTotal() }}</strong>
                  </div>
                </label>
              </div>
            </div>

            <div class="pago-detalles">
              <div class="input-group">
                <label class="label-modern">Método de Pago</label>
                <select v-model="form.medio_pago" class="select-modern">
                  <option value="EFECTIVO">💵 Efectivo</option>
                  <option value="MERCADO_PAGO">🔵 Mercado Pago</option>
                  <option value="TRANSFERENCIA">🏦 Transferencia Bancaria</option>
                </select>
              </div>
              
              <div v-if="form.medio_pago !== 'EFECTIVO'" class="datos-transferencia-container slide-in">
                
                <div class="input-group" v-if="form.medio_pago === 'TRANSFERENCIA'">
                  <label class="label-modern">Billetera / Banco de Origen</label>
                  <select v-model="form.entidad_pago" class="select-modern">
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

                <div class="input-group">
                  <label class="label-modern">
                    {{ form.medio_pago === 'MERCADO_PAGO' ? 'ID Transacción Mercado Pago *' : 'Código de Comprobante *' }}
                  </label>
                  
                  <input 
                    type="text" 
                    v-model="form.codigo_transaccion" 
                    class="input-modern" 
                    :placeholder="form.medio_pago === 'MERCADO_PAGO' ? 'Ej: #145025893768' : 'Ej: A123B456789'"
                    :maxlength="maxCodigoLength"
                    :class="{ 'input-error': errorValidacion && !form.codigo_transaccion }"
                  />
                  
                  <small class="helper-text">
                    <Info :size="12" /> 
                    {{ form.medio_pago === 'MERCADO_PAGO' ? 'ID de operación MP (Ej: #123...). Máx 14.' : 'Código del comprobante bancario. Máx 25.' }}
                  </small>
                  <div v-if="errorValidacion && !form.codigo_transaccion" class="msg-error small">
                    El código es obligatorio.
                  </div>
                </div>
              </div>
            </div>

            <button 
              @click="modificarTurno" 
              class="btn-confirmar-premium"
              :disabled="procesando || !formularioValido"
            >
              <span v-if="!procesando">Actualizar Turno</span>
              <span v-else>Actualizando...</span>
            </button>
          </div>

          <transition name="fade">
            <div v-if="mensaje" class="toast-message" :class="mensajeTipo">
              <component :is="mensajeTipo === 'success' ? CheckCircle : AlertCircle" :size="18" />
              {{ mensaje }}
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal para cambiar cliente (MEJORADO) -->
  <div v-if="mostrarModalCliente" class="modal-overlay" @click="cerrarModalCliente">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>🔄 Cambiar Cliente</h3>
        <button class="modal-close-btn" @click="cerrarModalCliente">×</button>
      </div>
      <div class="modal-body">
        <div class="input-group">
          <div class="search-wrapper">
            <Search class="search-icon" :size="18" />
            <input
              type="text"
              v-model="busquedaClienteModal"
              @input="actualizarBusquedaClienteModal"
              placeholder="Buscar por nombre o DNI..."
              class="input-modern"
            />
          </div>
          
          <ul v-if="clientesSugeridosModal.length" class="lista-sugerencias-modal">
            <li v-for="c in clientesSugeridosModal" :key="c.id" @click="seleccionarClienteModal(c)" class="item-sugerencia-modal">
              <div class="avatar-mini"><User :size="14" /></div>
              <div class="sugerencia-info">
                <!-- CORREGIDO: manejar tanto nombre/apellido como first_name/last_name -->
                <strong>{{ getNombreCompletoCliente(c) }}</strong>
                <small>DNI: {{ c.dni || '---' }}</small>
              </div>
            </li>
          </ul>
          
          <div v-if="errorClienteModal" class="msg-error mt-2">
            <AlertCircle :size="14" /> {{ errorClienteModal }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Calendar, ArrowLeft, Users, Search, Edit3, Tag, Scissors, 
  Check, Clock, UserCheck, CalendarDays, ChevronLeft, ChevronRight, 
  Info, Loader2, Receipt, AlertCircle, CheckCircle, User, 
  FolderOpen, Inbox, Armchair, ChevronDown
} from 'lucide-vue-next'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const turnoId = route.params.id
const API_URL = "http://localhost:8000/api"

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    "Content-Type": "application/json",
    "Authorization": token ? `Token ${token}` : ''
  }
}

// Estados
const cargando = ref(true)
const procesando = ref(false)
const error = ref(null)
const mensaje = ref("")
const mensajeTipo = ref("success")
const cargandoHorarios = ref(false)
const errorValidacion = ref(false)

// Datos maestros
const categorias = ref([])
const servicios = ref([])
const peluqueros = ref([])
const sillas = ref([])
const categoriasSeleccionadas = ref([])
const slotsOcupadosReales = ref([])      // minutos ocupados por OTROS turnos
const slotsTurnoActual = ref(new Set())   // minutos del turno actual (para marcarlo)
const turnoOriginal = ref(null)           // guardar datos originales para comparar
const currentDate = ref(new Date())       // mes mostrado en el calendario

// Modal Cliente
const mostrarModalCliente = ref(false)
const busquedaClienteModal = ref("")
const clientesSugeridosModal = ref([])
const errorClienteModal = ref("")

// Formulario
const form = ref({
  canal: 'PRESENCIAL',
  cliente: null,
  clienteNombre: "",
  peluquero: "",
  silla: null,
  servicios_ids: [],
  tipo_pago: "SENA_50",
  medio_pago: "EFECTIVO",
  entidad_pago: "",
  codigo_transaccion: "",
  fecha: "",
  hora: ""
})

// Observadores
watch(() => form.value.medio_pago, (newVal) => {
  if (cargando.value) return 
  if (newVal === 'EFECTIVO') {
    form.value.entidad_pago = ""
    form.value.codigo_transaccion = ""
    errorValidacion.value = false
  } else if (newVal === 'MERCADO_PAGO') {
    form.value.entidad_pago = "" 
  }
})

// 🔥 IMPORTANTE: ya no borramos la hora al cambiar servicios, solo verificamos disponibilidad
watch(() => form.value.servicios_ids, () => {
  // No hacemos nada aquí, la disponibilidad se evalúa en el template y en formularioValido
}, { deep: true })

// Propiedades computadas
const maxCodigoLength = computed(() => form.value.medio_pago === 'MERCADO_PAGO' ? 14 : 25)

const serviciosFiltrados = computed(() => {
  if (categoriasSeleccionadas.value.length === 0) return []
  return servicios.value.filter(s => {
    if (!s.categoria) return false
    const catId = typeof s.categoria === 'object' ? s.categoria.id : s.categoria
    return categoriasSeleccionadas.value.includes(Number(catId))
  })
})

const sillasActivas = computed(() => sillas.value.filter(s => s.activa))

// 🔥 Validación mejorada: incluye disponibilidad de la hora
const formularioValido = computed(() => {
  const base = form.value.cliente && form.value.peluquero && 
               form.value.servicios_ids.length > 0 && form.value.fecha && 
               form.value.hora && form.value.tipo_pago && form.value.medio_pago
  if (!base) return false
  // Verificar que la hora sea válida (disponible)
  if (!esHorarioDisponibleCompleto(form.value.hora)) return false
  if (form.value.medio_pago !== 'EFECTIVO' && !form.value.codigo_transaccion) return false
  return true
})

// Calendario
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())
const nombreMesActual = computed(() => 
  ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'][currentMonth.value]
)
const daysInMonth = computed(() => new Date(currentYear.value, currentMonth.value + 1, 0).getDate())
const startingDayOfWeek = computed(() => new Date(currentYear.value, currentMonth.value, 1).getDay())

const horariosGenerados = computed(() => {
  const horariosBase = []
  const bloques = [
    { inicio: 8, fin: 12 }, 
    { inicio: 15, fin: 20 }
  ]

  bloques.forEach(b => {
    for (let h = b.inicio; h < b.fin; h++) {
      for (let m = 0; m < 60; m += 20) {
        const horaStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
        horariosBase.push(horaStr)
      }
    }
    horariosBase.push(`${String(b.fin).padStart(2, '0')}:00`)
  })

  return horariosBase
})

// Funciones Calendario
const esHoy = (day) => {
  const today = new Date()
  return day === today.getDate() && currentMonth.value === today.getMonth() && currentYear.value === today.getFullYear()
}

const esDiaSeleccionable = (day) => {
  const date = new Date(currentYear.value, currentMonth.value, day)
  const today = new Date()
  today.setHours(0,0,0,0)
  const diffTime = date - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return (diffDays >= 0 && diffDays <= 8) && date.getDay() !== 0
}

const esDiaSeleccionado = (day) => {
  if (!form.value.fecha) return false
  const [y, m, d] = form.value.fecha.split('-').map(Number)
  return day === d && (currentMonth.value + 1) === m && currentYear.value === y
}

const seleccionarDiaCalendario = (day) => {
  if (!esDiaSeleccionable(day)) return
  const mesStr = String(currentMonth.value + 1).padStart(2, '0')
  const diaStr = String(day).padStart(2, '0')
  form.value.fecha = `${currentYear.value}-${mesStr}-${diaStr}`
  cargarHorariosOcupados(form.value.fecha)
}

const cambiarMes = (dir) => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(currentDate.value.getMonth() + dir)
  currentDate.value = newDate
}

// Carga de horarios ocupados
const cargarHorariosOcupados = async (fecha) => {
  if (!form.value.peluquero) return
  
  // Guardar la hora actual antes de resetear (si es necesario)
  const horaPrevia = form.value.hora
  
  cargandoHorarios.value = true
  slotsOcupadosReales.value = []
  slotsTurnoActual.value.clear()
  
  try {
    const res = await fetch(
      `${API_URL}/turnos/?fecha=${fecha}&peluquero_id=${form.value.peluquero}&estado__in=RESERVADO,CONFIRMADO`, 
      { headers: getAuthHeaders() }
    )
    
    if (!res.ok) throw new Error(`Error horarios: ${res.status}`)
    
    const turnos = await res.json()
    const resultados = Array.isArray(turnos) ? turnos : (turnos.results || [])
    const ocupadosSet = new Set()
    
    resultados.forEach(t => {
      const [h, m] = t.hora.split(':').map(Number)
      let dur = t.duracion_total || 0
      if (!dur && t.servicios) {
        dur = t.servicios.reduce((acc, s) => acc + (s.duracion || 20), 0)
      }
      if (!dur) dur = 20
      
      const inicioMinutos = h * 60 + m
      const finMinutos = inicioMinutos + dur
      
      if (t.id === parseInt(turnoId)) {
        // Guardar minutos del turno actual (para marcarlo)
        for (let i = inicioMinutos; i < finMinutos; i++) {
          const horaSlot = Math.floor(i / 60).toString().padStart(2, '0')
          const minutoSlot = (i % 60).toString().padStart(2, '0')
          slotsTurnoActual.value.add(`${horaSlot}:${minutoSlot}`)
        }
      } else {
        // Otros turnos: marcar como ocupados
        for (let i = inicioMinutos; i < finMinutos; i++) {
          const horaSlot = Math.floor(i / 60).toString().padStart(2, '0')
          const minutoSlot = (i % 60).toString().padStart(2, '0')
          ocupadosSet.add(`${horaSlot}:${minutoSlot}`)
        }
      }
    })
    
    slotsOcupadosReales.value = Array.from(ocupadosSet)
    
    // Restaurar la hora previa si sigue siendo válida
    if (horaPrevia && esHorarioDisponibleCompleto(horaPrevia)) {
      form.value.hora = horaPrevia
    } else if (turnoOriginal.value?.fecha === fecha && turnoOriginal.value?.hora) {
      // Si es la fecha original y no se restauró antes, asignar la hora original
      form.value.hora = turnoOriginal.value.hora
    } else {
      form.value.hora = ""
    }
    
  } catch (e) { 
    console.error("Error en cargarHorariosOcupados:", e) 
  } finally { 
    cargandoHorarios.value = false 
  }
}

// Funciones de disponibilidad
const esHorarioDelTurnoActual = (hora) => {
  if (!turnoOriginal.value) return false
  if (form.value.fecha !== turnoOriginal.value.fecha) return false
  if (Number(form.value.peluquero) !== Number(turnoOriginal.value.peluquero_id)) return false
  
  const [h, m] = hora.split(':').map(Number)
  const horaString = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
  
  return slotsTurnoActual.value.has(horaString)
}

const esHorarioDisponibleCompleto = (horaSeleccionada) => {
  if (!form.value.fecha || !form.value.peluquero) return false
  
  if (esHorarioDelTurnoActual(horaSeleccionada)) return true
  
  const duracionTotal = form.value.servicios_ids.reduce((acc, id) => {
    const s = servicios.value.find(x => Number(x.id) === Number(id))
    return acc + (s ? parseInt(s.duracion) : 0)
  }, 0)
  
  if (duracionTotal === 0) return false
  
  const [h, m] = horaSeleccionada.split(':').map(Number)
  const inicioMinutos = h * 60 + m
  const finMinutos = inicioMinutos + duracionTotal
  
  for (let i = inicioMinutos; i < finMinutos; i++) {
    const horaSlot = Math.floor(i / 60).toString().padStart(2, '0')
    const minutoSlot = (i % 60).toString().padStart(2, '0')
    const slotActual = `${horaSlot}:${minutoSlot}`
    
    if (slotsOcupadosReales.value.some(slot => 
        slot.startsWith(slotActual.substring(0, 5)))) {
      return false
    }
  }
  
  const hoy = new Date()
  const hoyFormateado = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
  if (form.value.fecha === hoyFormateado) {
    if (inicioMinutos < (hoy.getHours() * 60 + hoy.getMinutes())) {
      return false
    }
  }
  
  return true
}

const seleccionarHora = (hora) => { 
  if (esHorarioDisponibleCompleto(hora)) form.value.hora = hora 
}

// Funciones del formulario (CORREGIDAS: ya no resetean peluquero ni fechas)
const toggleCategoria = (id) => {
  const idx = categoriasSeleccionadas.value.indexOf(Number(id))
  if (idx > -1) categoriasSeleccionadas.value.splice(idx, 1)
  else categoriasSeleccionadas.value.push(Number(id))
  form.value.servicios_ids = []
  // Ya no se resetea el peluquero ni la fecha
}

const toggleServicio = (s) => {
  const idx = form.value.servicios_ids.indexOf(Number(s.id))
  if (idx > -1) form.value.servicios_ids.splice(idx, 1)
  else form.value.servicios_ids.push(Number(s.id))
  // Ya no se resetea nada
}

const seleccionarPeluquero = (id) => {
  form.value.peluquero = Number(id)
  resetFechas()
}

const resetFechas = () => {
  form.value.fecha = ""
  form.value.hora = ""
  slotsOcupadosReales.value = []
}

// Cálculos de total
const calcularTotal = () => form.value.servicios_ids.reduce((acc, id) => {
  const s = servicios.value.find(x => Number(x.id) === Number(id))
  return acc + (s ? parseFloat(s.precio) : 0)
}, 0).toFixed(2)

const calcularSena = () => (calcularTotal() / 2).toFixed(2)

// Navegación
const volverAlListado = () => router.push('/turnos')

// Carga de datos iniciales
const cargarDatosTurno = async () => {
  try {
    cargando.value = true
    
    const headers = getAuthHeaders()

    // 1. Cargar maestros
    const [catRes, servRes, pelRes, sillasRes] = await Promise.all([
      fetch(`${API_URL}/categorias/servicios/`, { headers }),
      fetch(`${API_URL}/servicios/`, { headers }),
      fetch(`${API_URL}/peluqueros/`, { headers }),
      fetch(`${API_URL}/sillas/`, { headers })
    ])
    
    if (!catRes.ok) throw new Error(`Error categorías: ${catRes.status}`)
    if (!servRes.ok) throw new Error(`Error servicios: ${servRes.status}`)
    if (!pelRes.ok) throw new Error(`Error peluqueros: ${pelRes.status}`)
    if (!sillasRes.ok) console.warn("No se pudieron cargar las sillas")
    
    categorias.value = await catRes.json()
    servicios.value = await servRes.json()
    peluqueros.value = await pelRes.json()
    if (sillasRes.ok) sillas.value = await sillasRes.json()

    // 2. Cargar turno
    const turnoRes = await fetch(`${API_URL}/turnos/${turnoId}/`, { headers })
    if (!turnoRes.ok) {
      if (turnoRes.status === 401 || turnoRes.status === 403) {
        localStorage.removeItem('token')
        router.push('/login')
        return
      }
      throw new Error(`Error cargando turno: ${turnoRes.status}`)
    }
    
    const turno = await turnoRes.json()
    console.log("Turno cargado:", turno)

    // Guardar datos originales
    turnoOriginal.value = {
      fecha: turno.fecha,
      peluquero_id: Number(turno.peluquero_id || turno.peluquero?.id),
      hora: turno.hora,
      duracion_total: turno.duracion_total || turno.servicios?.reduce((acc, s) => acc + (s.duracion || 20), 0) || 20
    }

    // 3. Asignar valores al formulario
    form.value.cliente = Number(turno.cliente_id || turno.cliente?.id)
    
    if (turno.cliente) {
      form.value.clienteNombre = `${turno.cliente.nombre || turno.cliente.first_name || ''} ${turno.cliente.apellido || turno.cliente.last_name || ''}`.trim()
    } else {
      form.value.clienteNombre = `${turno.cliente_nombre || ''} ${turno.cliente_apellido || ''}`.trim()
    }

    form.value.peluquero = Number(turno.peluquero_id || turno.peluquero?.id)
    form.value.silla = turno.silla_id ? Number(turno.silla_id) : (turno.silla?.id ? Number(turno.silla.id) : null)
    form.value.servicios_ids = (turno.servicios || []).map(s => Number(s.id))

    // Auto-seleccionar categorías
    const catsParaActivar = new Set()
    turno.servicios?.forEach(s => {
      if (s.categoria) {
        catsParaActivar.add(Number(s.categoria))
      } else {
        const servicioCat = servicios.value.find(srv => Number(srv.id) === Number(s.id))
        if (servicioCat && servicioCat.categoria) {
          const catId = typeof servicioCat.categoria === 'object' ? Number(servicioCat.categoria.id) : Number(servicioCat.categoria)
          if (catId) catsParaActivar.add(catId)
        }
      }
    })
    categoriasSeleccionadas.value = Array.from(catsParaActivar)

    // Fecha y hora
    form.value.fecha = turno.fecha
    form.value.hora = turno.hora

    // Pago
    form.value.tipo_pago = turno.tipo_pago || "SENA_50"
    form.value.medio_pago = turno.medio_pago || "EFECTIVO"
    form.value.entidad_pago = turno.entidad_pago || ""
    form.value.codigo_transaccion = turno.codigo_transaccion || ""

    // 4. Posicionar calendario
    if (form.value.fecha) {
      const [year, month] = form.value.fecha.split('-').map(Number)
      currentDate.value = new Date(year, month - 1, 1)
    }

    // 5. Cargar horarios ocupados
    if (form.value.fecha && form.value.peluquero) {
      await cargarHorariosOcupados(form.value.fecha)
    }

    await nextTick()

  } catch (err) {
    error.value = "Error al cargar datos: " + err.message
    console.error("Error en cargarDatosTurno:", err)
  } finally {
    cargando.value = false
  }
}

// Modificar turno
const modificarTurno = async () => {
  if (form.value.medio_pago !== 'EFECTIVO' && !form.value.codigo_transaccion) {
    errorValidacion.value = true
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Falta el código de transacción',
      confirmButtonText: 'Entendido'
    })
    return
  }
  
  procesando.value = true
  
  let entidadFinal = null
  if (form.value.medio_pago === 'MERCADO_PAGO') entidadFinal = 'MERCADO_PAGO'
  else if (form.value.medio_pago === 'TRANSFERENCIA') entidadFinal = form.value.entidad_pago

  const duracion = form.value.servicios_ids.reduce((acc, id) => {
    const s = servicios.value.find(x => Number(x.id) === Number(id))
    return acc + (s ? parseInt(s.duracion) : 0)
  }, 0)

  const totalCalculado = parseFloat(calcularTotal())
  const esPagoSena = form.value.tipo_pago.includes('SENA')

  const payload = {
    peluquero_id: Number(form.value.peluquero),
    servicios_ids: form.value.servicios_ids.map(id => Number(id)),
    fecha: form.value.fecha,
    hora: form.value.hora,
    silla: form.value.silla ? Number(form.value.silla) : null,
    tipo_pago: esPagoSena ? 'SENA_50' : 'TOTAL',
    medio_pago: form.value.medio_pago,
    monto_total: totalCalculado,
    monto_seña: esPagoSena ? parseFloat(calcularSena()) : totalCalculado,
    duracion_total: duracion,
    entidad_pago: entidadFinal,
    mp_payment_id: form.value.medio_pago === 'MERCADO_PAGO' ? form.value.codigo_transaccion : null,
    codigo_transaccion: form.value.medio_pago === 'TRANSFERENCIA' ? form.value.codigo_transaccion : null
  }

  try {
    const res = await fetch(`${API_URL}/turnos/${turnoId}/modificar/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })
    
    const data = await res.json()
    
    if (res.ok && data.status === 'ok') {
      await Swal.fire({ 
        icon: 'success', 
        title: 'Turno Actualizado', 
        text: 'Los cambios se guardaron correctamente',
        confirmButtonText: 'Aceptar' 
      })
      router.push('/turnos')
    } else {
      let errorMsg = data.message || data.error || "Error al actualizar"
      if (data.errors) {
        errorMsg = Object.entries(data.errors)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
          .join('; ')
      }
      throw new Error(errorMsg)
    }
  } catch (e) {
    Swal.fire({ 
      icon: 'error', 
      title: 'Error', 
      text: e.message,
      confirmButtonText: 'Entendido'
    })
  } finally {
    procesando.value = false
  }
}

// Modal Cliente
const abrirModalCambiarCliente = () => { 
  mostrarModalCliente.value = true; 
  busquedaClienteModal.value = ""; 
  clientesSugeridosModal.value = [] 
}
const cerrarModalCliente = () => mostrarModalCliente.value = false

const actualizarBusquedaClienteModal = async () => {
  if (busquedaClienteModal.value.length < 1) return
  try {
    const res = await fetch(
      `${API_URL}/clientes/?q=${busquedaClienteModal.value}`, 
      { headers: getAuthHeaders() }
    )
    if (!res.ok) throw new Error(`Error clientes: ${res.status}`)
    const data = await res.json()
    clientesSugeridosModal.value = data.results || data || []
  } catch (e) {
    console.error("Error buscando clientes:", e)
    errorClienteModal.value = "Error al buscar clientes"
  }
}

const seleccionarClienteModal = (c) => {
  form.value.cliente = Number(c.id)
  const nombre = c.nombre || c.first_name || ''
  const apellido = c.apellido || c.last_name || ''
  form.value.clienteNombre = `${nombre} ${apellido}`.trim()
  if (Number(form.value.peluquero) === Number(c.id)) {
    form.value.peluquero = ""
    resetFechas()
  }
  cerrarModalCliente()
}

const getNombreCompletoCliente = (c) => {
  const nombre = c.nombre || c.first_name || ''
  const apellido = c.apellido || c.last_name || ''
  return `${nombre} ${apellido}`.trim()
}

onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  cargarDatosTurno()
})
</script>

<style scoped>
/* ============================================
   FONDO DE PÁGINA Y CONTENEDOR PRINCIPAL
   ============================================ */
.page-background {
  min-height: 100vh;
  padding: 30px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.main-card-container {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.turno-container {
  width: 100%;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #1f2937, #374151);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.header-section h2 {
  margin: 0;
  color: white;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header-icon { 
  color: #60a5fa; 
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.btn-back {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
}

.btn-back:hover { 
  background: rgba(255, 255, 255, 0.2); 
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px); 
}

/* Cards Modernas */
.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #3b82f6;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f1f3f4;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 12px;
  color: white;
  box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
}

.card-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
  letter-spacing: -0.5px;
}

/* PROFESIONALES - CARDS */
.profesionales-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 10px;
}

.profesional-card {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 14px;
}

.profesional-card:hover:not(.profesional-disabled) {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.15);
}

.profesional-selected {
  border-color: #10b981 !important;
  background: #f0fdf4;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.profesional-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f9fafb;
}

.profesional-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #dbeafe, #93c5fd);
  color: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profesional-selected .profesional-avatar {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #10b981;
}

.profesional-info {
  flex: 1;
}

.profesional-nombre {
  font-weight: 700;
  color: #1f2937;
  font-size: 1.05rem;
  margin-bottom: 4px;
}

.profesional-badge-cliente {
  font-size: 0.8rem;
  color: #dc2626;
  font-weight: 600;
  background: #fee2e2;
  padding: 3px 10px;
  border-radius: 6px;
  display: inline-block;
}

.profesional-badge-selected {
  font-size: 0.8rem;
  color: #10b981;
  font-weight: 600;
  background: #d1fae5;
  padding: 3px 10px;
  border-radius: 6px;
  display: inline-block;
}

/* SELECTOR DE SILLA */
.custom-select-wrapper {
  position: relative;
  width: 100%;
}

.form-control-select {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 1rem;
  color: #1f2937;
  appearance: none;
  cursor: pointer;
  transition: all 0.3s ease;
  padding-right: 40px;
}

.form-control-select:focus {
  border-color: #8b5cf6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
  outline: none;
}

.select-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
}

/* HORARIOS */
.grid-horarios {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.hora-card {
  background: #fff;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  padding: 14px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.hora-card:hover:not(.hora-ocupada):not(.hora-actual) {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.hora-texto {
  font-weight: 700;
  color: #1f2937;
  font-size: 1.1em;
  display: block;
}

.hora-selected {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border-color: #3b82f6;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.hora-selected .hora-texto { 
  color: white; 
}

.hora-ocupada {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  border: 2px solid #f87171;
  cursor: not-allowed;
  opacity: 0.85;
}

.hora-ocupada .hora-texto {
  text-decoration: line-through;
  color: #dc2626;
  font-weight: 700;
}

.etiqueta-ocupado {
  display: block;
  font-size: 0.65em;
  color: white;
  font-weight: 800;
  background: #dc2626;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* HORARIO ACTUAL (turno que se está modificando) - MÁS NOTORIO */
.hora-actual {
  border: 3px solid #2563eb !important;
  background: #bfdbfe !important;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3);
  transform: scale(1.02);
  cursor: pointer;
}

.hora-actual .hora-texto {
  color: #1e3a8a !important;
  font-weight: 800 !important;
  text-decoration: none !important;
}

.etiqueta-actual {
  display: block;
  font-size: 0.7em;
  color: white;
  font-weight: 700;
  margin-top: 4px;
  background: #2563eb;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

/* Inputs y Selects */
.input-modern, .select-modern {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 15px;
  transition: all 0.3s ease;
  color: #1f2937;
}

.input-modern:focus, .select-modern:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.row-search { 
  display: flex; 
  gap: 12px; 
  margin-bottom: 15px;
}

.search-wrapper { 
  flex: 1; 
  position: relative; 
}

.search-icon { 
  position: absolute; 
  left: 16px; 
  top: 50%; 
  transform: translateY(-50%); 
  color: #6b7280; 
}

.input-modern { 
  padding-left: 46px; 
  width: 100%;
}

.cliente-activo {
  background: #e0f2fe !important;
  border-color: #0ea5e9 !important;
  font-weight: 600;
}

.btn-nuevo { 
  background: linear-gradient(135deg, #0f172a, #1e293b); 
  color: white; 
  border: none; 
  padding: 0 24px; 
  border-radius: 10px; 
  font-weight: 600; 
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-nuevo:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(15, 23, 42, 0.3);
}

/* Sugerencias - MODAL MEJORADO */
.lista-sugerencias-modal {
  position: absolute;
  background: white;
  border: 2px solid #e5e7eb;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  margin-top: 8px;
  list-style: none;
  padding: 12px 0;
}

.item-sugerencia-modal { 
  padding: 14px 18px; 
  color: #1f2937; 
  display: flex; 
  gap: 14px; 
  align-items: center; 
  cursor: pointer; 
  border-radius: 8px; 
  transition: all 0.2s;
  margin: 4px 10px;
  border: 1px solid transparent;
}

.item-sugerencia-modal:hover { 
  background: #eef2ff; 
  border-color: #3b82f6;
  transform: translateX(4px);
}

.item-sugerencia-modal .sugerencia-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-sugerencia-modal strong {
  font-size: 1.05rem;
  color: #111827;
}

.item-sugerencia-modal small {
  color: #6b7280;
  font-size: 0.9rem;
}

.avatar-mini { 
  width: 40px; 
  height: 40px; 
  background: #dbeafe; 
  color: #2563eb; 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  flex-shrink: 0;
  font-weight: bold;
}

.msg-error {
  color: #dc3545;
  background: #fee2e2;
  padding: 10px 14px;
  border-radius: 8px;
  margin-top: 10px;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mt-2 {
  margin-top: 12px;
}

/* Chips */
.grid-chips { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 12px; 
}

.chip-modern {
  background: #fff; 
  border: 2px solid #e5e7eb; 
  padding: 12px 20px; 
  border-radius: 50px;
  color: #6b7280; 
  cursor: pointer; 
  font-weight: 600; 
  display: flex; 
  align-items: center; 
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.chip-modern:hover { 
  border-color: #3b82f6; 
  color: #3b82f6; 
  transform: translateY(-2px);
}

.chip-active { 
  background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
  color: white; 
  border-color: #3b82f6; 
  box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
}

/* Servicios */
.grid-servicios { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); 
  gap: 16px; 
  margin-top: 20px;
}

.card-servicio { 
  background: #fff; 
  border: 2px solid #e5e7eb; 
  border-radius: 12px; 
  padding: 20px; 
  cursor: pointer; 
  position: relative; 
  transition: all 0.3s ease;
}

.card-servicio:hover { 
  border-color: #3b82f6; 
  transform: translateY(-3px); 
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
}

.servicio-active { 
  border-color: #10b981; 
  background: #f0fdf4; 
}

.servicio-check { 
  position: absolute; 
  top: 12px; 
  right: 12px; 
  width: 24px;
  height: 24px;
  background: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.servicio-nombre { 
  font-weight: 700; 
  color: #1f2937; 
  display: block; 
  margin-bottom: 8px; 
  font-size: 1.05rem;
}

.servicio-details { 
  display: flex; 
  justify-content: space-between; 
  color: #6b7280; 
  font-size: 0.95em; 
}

.servicio-precio { 
  color: #059669; 
  font-weight: 700; 
}

.servicio-duracion {
  color: #6b7280;
  font-weight: 500;
}

/* Calendario - DÍAS DISPONIBLES EN VERDE */
.calendar-wrapper { 
  background: #f8fafc; 
  border-radius: 16px; 
  padding: 24px; 
  border: 2px solid #e5e7eb; 
}

.calendar-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 20px; 
}

.mes-titulo { 
  font-weight: 700; 
  font-size: 1.2em; 
  color: #1f2937;
}

.btn-nav-cal { 
  background: white; 
  border: 1px solid #e5e7eb; 
  border-radius: 8px; 
  width: 40px; 
  height: 40px; 
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  transition: all 0.2s;
}

.btn-nav-cal:hover { 
  background: #f3f4f6; 
  border-color: #d1d5db;
}

.calendar-days-header { 
  display: grid; 
  grid-template-columns: repeat(7, 1fr); 
  text-align: center; 
  font-weight: 700; 
  color: #6b7280; 
  margin-bottom: 15px; 
  font-size: 0.95em; 
}

.calendar-grid { 
  display: grid; 
  grid-template-columns: repeat(7, 1fr); 
  gap: 10px; 
}

.day-btn {
  aspect-ratio: 1; 
  border-radius: 10px; 
  border: 2px solid transparent; 
  background: rgb(72, 255, 130); /* Verde como en registro */
  font-weight: 600;
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  position: relative;
  transition: all 0.2s;
  color: #1f2937;
}

.day-btn:hover:not(:disabled) { 
  border-color: #3b82f6; 
  transform: translateY(-1px);
}

.day-selected { 
  background: #3b82f6 !important; 
  color: white !important; 
  border-color: #3b82f6 !important;
}

.day-today { 
  border-color: #f59e0b; 
  background: #fef3c7;
}

.badge-today { 
  position: absolute; 
  bottom: 4px; 
  font-size: 0.6em; 
  color: #d97706; 
  font-weight: 800; 
}

.day-disabled { 
  background: #e5e7eb !important; 
  color: #9ca3af !important; 
  cursor: not-allowed; 
  opacity: 0.6;
}

/* Resumen y Pago */
.resumen-grid { 
  display: flex; 
  flex-direction: column; 
  gap: 12px; 
  margin-bottom: 25px; 
}

.resumen-item { 
  display: flex; 
  justify-content: space-between; 
  padding: 12px 0; 
  border-bottom: 1px solid #e5e7eb; 
  color: #1f2937;
}

.resumen-item.total { 
  font-size: 1.3em; 
  font-weight: 700; 
  border-top: 2px solid #e5e7eb; 
  margin-top: 15px; 
  padding-top: 15px;
  border-bottom: none; 
}

.pago-section {
  margin-bottom: 25px;
}

.pago-options { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 20px; 
  margin-bottom: 25px; 
}

.radio-box {
  border: 2px solid #e5e7eb; 
  padding: 20px; 
  border-radius: 12px; 
  cursor: pointer; 
  color: #1f2937; 
  text-align: center; 
  transition: all 0.3s ease;
}

.radio-box:hover { 
  border-color: #3b82f6; 
  transform: translateY(-2px);
}

.radio-active { 
  border-color: #3b82f6; 
  background: #eff6ff; 
}

.hidden-radio { 
  display: none; 
}

.radio-content { 
  display: flex; 
  flex-direction: column; 
  gap: 8px; 
}

.radio-content span { 
  font-weight: 600; 
  font-size: 1.1rem;
}

.radio-content strong { 
  font-size: 1.3rem; 
  color: #059669; 
}

.pago-detalles { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 20px; 
  margin-bottom: 25px; 
}

.input-group {
  margin-bottom: 15px;
}

.label-modern {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
  color: #1f2937;
  font-size: 1rem;
}

.btn-confirmar-premium {
  width: 100%; 
  background: linear-gradient(135deg, #059669, #047857); 
  color: white; 
  padding: 18px; 
  border: none;
  border-radius: 12px; 
  font-size: 1.1em; 
  font-weight: 700; 
  cursor: pointer; 
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.btn-confirmar-premium:hover:not(:disabled) { 
  transform: translateY(-3px); 
  box-shadow: 0 10px 25px rgba(5, 150, 105, 0.4);
  background: linear-gradient(135deg, #047857, #065f46);
}

.btn-confirmar-premium:disabled { 
  background: #9ca3af; 
  cursor: not-allowed; 
  transform: none; 
  opacity: 0.7;
}

.btn-cancelar-premium {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-cancelar-premium:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Loader y Empty States */
.loading-state, .error-state {
  text-align: center; 
  padding: 50px 20px; 
  color: #6b7280;
}

.loading-state .spinner-icon {
  animation: spin 1s linear infinite; 
  margin-bottom: 15px; 
  color: #3b82f6; 
}

.error-state .error-icon {
  color: #dc3545;
  margin-bottom: 15px;
}

.loading-spinner, .no-resultados { 
  text-align: center; 
  padding: 50px 20px; 
  color: #6b7280; 
}

.spinner-icon { 
  animation: spin 1s linear infinite; 
  margin-bottom: 15px; 
  color: #3b82f6; 
}

@keyframes spin { 
  100% { 
    transform: rotate(360deg); 
  } 
}

.no-resultados-icon {
  opacity: 0.4;
  margin-bottom: 15px;
  color: #9ca3af;
}

/* Toast */
.toast-message {
  position: fixed; 
  bottom: 30px; 
  right: 30px; 
  padding: 18px 24px; 
  border-radius: 12px; 
  font-weight: 600;
  display: flex; 
  align-items: center; 
  gap: 12px; 
  z-index: 9999; 
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  min-width: 300px;
  backdrop-filter: blur(10px);
}

.toast-message.success { 
  background: rgba(16, 185, 129, 0.95); 
  color: white; 
  border-left: 4px solid #059669;
}

.toast-message.error { 
  background: rgba(239, 68, 68, 0.95); 
  color: white; 
  border-left: 4px solid #dc2626;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-radius: 20px 20px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4em;
  font-weight: 700;
}

.modal-close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 1.8em;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 30px;
  position: relative;
}

/* Animaciones */
.fade-enter-active, .fade-leave-active { 
  transition: opacity 0.5s ease; 
}

.fade-enter-from, .fade-leave-to { 
  opacity: 0; 
}

.slide-in {
  animation: slideInRight 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .main-card-container {
    padding: 30px;
    margin: 20px;
  }
  
  .pago-detalles {
    grid-template-columns: 1fr;
  }
  
  .grid-servicios {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .profesionales-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-background {
    padding: 20px 15px;
  }
  
  .main-card-container {
    padding: 25px;
    border-radius: 20px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
    padding: 20px;
  }
  
  .btn-back {
    width: 100%;
    justify-content: center;
  }
  
  .grid-servicios,
  .profesionales-grid {
    grid-template-columns: 1fr;
  }
  
  .grid-horarios {
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  }
  
  .pago-options {
    grid-template-columns: 1fr;
  }
  
  .row-search {
    flex-direction: column;
  }
  
  .btn-nuevo {
    width: 100%;
    justify-content: center;
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .page-background {
    padding: 15px 10px;
  }
  
  .main-card-container {
    padding: 20px;
    border-radius: 16px;
  }
  
  .card-modern {
    padding: 20px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-icon {
    width: 40px;
    height: 40px;
  }
  
  .grid-horarios {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 8px;
  }
  
  .toast-message {
    left: 15px;
    right: 15px;
    bottom: 15px;
    min-width: auto;
  }
}
</style>