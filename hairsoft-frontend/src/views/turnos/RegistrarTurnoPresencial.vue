<template>
  <div class="page-background">
    <div class="main-card-container">
      <div class="turno-container">
        <div v-if="cargandoDatos" class="loading-state">
          <Loader2 class="spinner-icon" :size="48" />
          <p>Cargando datos iniciales...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <AlertCircle class="error-icon" :size="48" />
          <h3>Error</h3>
          <p>{{ error }}</p>
        </div>

        <div v-else class="form-content">
          <div class="header-section">
            <h2>
              <Calendar class="header-icon" />
              Registrar Turno (Presencial)
            </h2>
            <button @click="volverAlListado" class="btn-back">
              <ArrowLeft :size="18" />
              Volver
            </button>
          </div>

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
                    :value="form.cliente ? form.clienteNombre : busquedaCliente"
                    @input="actualizarBusquedaCliente"
                    :placeholder="form.cliente ? '' : 'Buscar por nombre o DNI...'"
                    :class="['input-modern', { 'cliente-activo': form.cliente }]"
                    :readonly="form.cliente !== null"
                  />
                  <button v-if="form.cliente" @click="limpiarCliente" class="btn-icon-clean">
                    <X :size="16" />
                  </button>
                </div>
                
                <button @click="irARegistrarCliente" class="btn-nuevo">
                  <Plus :size="18" /> Nuevo
                </button>
              </div>

              <ul v-if="clientesSugeridos.length && !form.cliente" class="lista-sugerencias">
                <li v-for="c in clientesSugeridos" :key="c.id" @click="seleccionarCliente(c)" class="item-sugerencia">
                  <div class="avatar-mini"><User :size="14" /></div>
                  <div class="sugerencia-info">
                    <strong>{{ getNombreCompletoCliente(c) }}</strong>
                    <small> - DNI: {{ c.dni || '---' }}</small>
                  </div>
                </li>
              </ul>
              
              <div v-if="errorCliente" class="msg-error">
                <AlertCircle :size="14" /> {{ errorCliente }}
              </div>
            </div>
          </div>

          <div v-if="form.cliente" class="card-modern slide-in">
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
                  'profesional-selected': form.peluquero === p.id,
                  'profesional-disabled': p.id === form.cliente
                }"
                @click="p.id !== form.cliente ? seleccionarPeluquero(p.id) : null"
              >
                <div class="profesional-avatar">
                  <User :size="24" />
                </div>
                <div class="profesional-info">
                  <div class="profesional-nombre">{{ p.nombre }} {{ p.apellido || '' }}</div>
                  <div v-if="p.id === form.cliente" class="profesional-badge-cliente">Es el cliente</div>
                  <div v-else-if="form.peluquero === p.id" class="profesional-badge-selected">✓ Seleccionado</div>
                </div>
              </div>
            </div>
            
            <div v-if="form.peluquero === form.cliente && form.cliente" class="msg-error mt-2">
              <AlertCircle :size="14" /> No puedes seleccionar al mismo profesional como cliente.
            </div>
          </div>

          <div v-if="form.peluquero && form.peluquero !== form.cliente" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);"><Armchair :size="20" /></div>
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
          <div v-if="form.peluquero && form.peluquero !== form.cliente" class="card-modern slide-in">
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
                  'hora-disponible': esHorarioDisponibleCompleto(hora),
                  'hora-ocupada': !esHorarioDisponibleCompleto(hora)
                }"
                @click="esHorarioDisponibleCompleto(hora) ? seleccionarHora(hora) : null"
              >
                <div class="hora-icono">
                  <Clock v-if="esHorarioDisponibleCompleto(hora)" :size="16" />
                  <X v-else :size="18" />
                </div>
                <span class="hora-texto">{{ hora }}</span>
                <span v-if="!esHorarioDisponibleCompleto(hora)" class="etiqueta-ocupado">OCUPADO</span>
              </div>
            </div>
          </div>
          <div v-if="form.hora" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><Receipt :size="20" /></div>
              <h3>Confirmación y Pago</h3>
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
                    <span>Pago Total</span>
                    <strong>${{ calcularTotal() }}</strong>
                  </div>
                </label>
              </div>
            </div>

            <div class="pago-detalles">
              <div class="input-group">
                <label class="label-modern">Medio de Pago</label>
                <select v-model="form.medio_pago" class="select-modern">
                  <option value="EFECTIVO">💵 Efectivo</option>
                  <option value="MERCADO_PAGO">🔵 Mercado Pago (QR/Link)</option>
                  <option value="TRANSFERENCIA">🏦 Transferencia</option>
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
              @click="crearTurno" 
              class="btn-confirmar-premium"
              :disabled="procesando"
            >
              <span v-if="!procesando">Confirmar Reserva</span>
              <span v-else>Procesando...</span>
            </button>
          </div>

          <transition name="fade">
            <div v-if="mensaje" class="toast-message" :class="mensajeTipo">
              <component :is="mensajeTipo === 'success' ? CheckCircle : AlertCircle" :size="18" />
              {{ mensaje }}
            </div>
          </transition>

          <transition name="fade">
            <div v-if="mostrarModalRegistro" class="modal-overlay">
              <div class="modal-container">
                <div class="modal-header">
                  <h3>📝 Registrar Nuevo Cliente</h3>
                  <button @click="cerrarModalRegistro" class="modal-close-btn">
                    <X :size="20" />
                  </button>
                </div>
                
                <div class="modal-body">
                  <div class="form-grid">
                    <div class="input-group">
                      <label class="label-modern">Nombre *</label>
                      <input type="text" v-model="formNuevoCliente.nombre" class="input-modern" placeholder="Ej: Juan" :class="{ 'input-error': erroresCliente.nombre }" />
                      <div v-if="erroresCliente.nombre" class="msg-error small">{{ erroresCliente.nombre }}</div>
                    </div>
                    <div class="input-group">
                      <label class="label-modern">Apellido *</label>
                      <input type="text" v-model="formNuevoCliente.apellido" class="input-modern" placeholder="Ej: Pérez" :class="{ 'input-error': erroresCliente.apellido }" />
                      <div v-if="erroresCliente.apellido" class="msg-error small">{{ erroresCliente.apellido }}</div>
                    </div>
                    <div class="input-group">
                      <label class="label-modern">DNI *</label>
                      <input type="text" v-model="formNuevoCliente.dni" class="input-modern" placeholder="Ej: 12345678" :class="{ 'input-error': erroresCliente.dni }" />
                      <div v-if="erroresCliente.dni" class="msg-error small">{{ erroresCliente.dni }}</div>
                    </div>
                    <div class="input-group">
                      <label class="label-modern">Teléfono</label>
                      <input type="text" v-model="formNuevoCliente.telefono" class="input-modern" placeholder="Ej: +541123456789" />
                    </div>
                    <div class="input-group">
                      <label class="label-modern">Email *</label>
                      <input type="email" v-model="formNuevoCliente.correo" class="input-modern" placeholder="Ej: cliente@email.com" :class="{ 'input-error': erroresCliente.correo }" />
                      <div v-if="erroresCliente.correo" class="msg-error small">{{ erroresCliente.correo }}</div>
                    </div>
                    <div class="input-group">
                      <label class="label-modern">Contraseña *</label>
                      <input type="password" v-model="formNuevoCliente.contrasena" class="input-modern" placeholder="Mínimo 6 caracteres" :class="{ 'input-error': erroresCliente.contrasena }" />
                      <div v-if="erroresCliente.contrasena" class="msg-error small">{{ erroresCliente.contrasena }}</div>
                    </div>
                  </div>
                  
                  <div v-if="errorCrearCliente" class="msg-error mt-3">
                    <AlertCircle :size="14" /> {{ errorCrearCliente }}
                  </div>
                </div>
                
                <div class="modal-footer">
                  <button @click="cerrarModalRegistro" class="btn-secondary">Cancelar</button>
                  <button @click="crearClienteDesdeTurno" class="btn-primary" :disabled="creandoCliente">
                    <span v-if="!creandoCliente">Registrar Cliente</span>
                    <span v-else>Registrando...</span>
                  </button>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue' 
import { useRouter } from 'vue-router'
import { 
  Calendar, ArrowLeft, Users, Search, X, Plus, User, IdCard,
  AlertCircle, FolderOpen, Tag, Scissors, Check, Clock, UserCheck, 
  CalendarDays, ChevronLeft, ChevronRight, Info, Loader2, Receipt, 
  CheckCircle2, Bell, Banknote, FileText, Inbox, CheckCircle, CreditCard, Wallet,
  Armchair, ChevronDown // 🔥 IMPORTANTE: Iconos nuevos
} from 'lucide-vue-next'
import Swal from 'sweetalert2'

const router = useRouter()
const API_URL = "http://localhost:8000/api"

// 🔥 FUNCIÓN PARA OBTENER HEADERS CON TOKEN
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    "Content-Type": "application/json",
    "Authorization": token ? `Token ${token}` : ''
  }
}

const form = ref({
  canal: 'PRESENCIAL',
  cliente: null,
  clienteNombre: "",
  peluquero: "",
  silla: null, // 🔥 NUEVO CAMPO
  servicios_ids: [],
  tipo_pago: "SENA_50",
  medio_pago: "EFECTIVO",
  entidad_pago: "", 
  codigo_transaccion: "", 
  fecha: "",
  hora: ""
})

const categorias = ref([])
const servicios = ref([])
const peluqueros = ref([])
const sillas = ref([]) // 🔥 LISTA DE SILLAS
const busquedaCliente = ref("")
const clientesSugeridos = ref([])
const categoriasSeleccionadas = ref([])
const slotsOcupadosReales = ref([]) // 🔥 Ahora guarda TODOS los minutos ocupados
const currentDate = ref(new Date())
const errorCliente = ref("")
const mensaje = ref("")
const mensajeTipo = ref("success")
const procesando = ref(false)
const cargandoHorarios = ref(false)
const errorValidacion = ref(false)
const cargandoDatos = ref(true) // 🔥 NUEVO: estado de carga

const intervaloMinutos = 20
const STORAGE_KEY = 'turno_presencial_context'

// 🔥 OBSERVADOR: Recalcular disponibilidad cuando cambian los servicios
watch(() => form.value.servicios_ids, () => {
  if (form.value.fecha && form.value.peluquero && form.value.hora) {
    if (!esHorarioDisponibleCompleto(form.value.hora)) {
      form.value.hora = ""
    }
  }
}, { deep: true })

// 🔥 Observador para limpiar campos con valor correcto
watch(() => form.value.medio_pago, (newVal) => {
  if (newVal === 'EFECTIVO') {
    form.value.entidad_pago = ""
    form.value.codigo_transaccion = ""
    errorValidacion.value = false
  }
  if (newVal === 'MERCADO_PAGO') {
    form.value.entidad_pago = "" 
  }
})

// 🔥 PROPIEDAD COMPUTADA PARA EL LARGO DEL CÓDIGO
const maxCodigoLength = computed(() => {
  return form.value.medio_pago === 'MERCADO_PAGO' ? 14 : 25
})

const serviciosFiltrados = computed(() => {
  if (categoriasSeleccionadas.value.length === 0) return []
  return servicios.value.filter(s => {
    if (!s.categoria) return false
    const catId = typeof s.categoria === 'object' ? s.categoria.id : s.categoria
    return categoriasSeleccionadas.value.includes(catId)
  })
})

// 🔥 FILTRAR SILLAS ACTIVAS
const sillasActivas = computed(() => {
  return sillas.value.filter(s => s.activa)
})

const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())
const nombreMesActual = computed(() => {
  const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
  return meses[currentMonth.value]
})
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
      for (let m = 0; m < 60; m += intervaloMinutos) {
        const horaStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
        horariosBase.push(horaStr)
      }
    }
    horariosBase.push(`${String(b.fin).padStart(2, '0')}:00`)
  })

  return horariosBase
})

// 🔥 CORREGIDO: cargarHorariosOcupados - Ahora guarda TODOS los minutos ocupados
const cargarHorariosOcupados = async (fecha) => {
  if (!form.value.peluquero || form.value.peluquero === form.value.cliente) return
  
  form.value.hora = ""
  cargandoHorarios.value = true
  slotsOcupadosReales.value = [] 
  
  try {
    // 🔥 Agregar la silla seleccionada a la query si existe
    let url = `${API_URL}/turnos/?fecha=${fecha}&peluquero=${form.value.peluquero}&estado__in=RESERVADO,CONFIRMADO`
    
    // Si eligió silla manual, quizás quieras filtrar o validar algo extra acá,
    // pero por ahora traemos los turnos del peluquero para evitar solapamiento humano.
    // La validación de silla ocupada la hará el backend al guardar.
    
    const res = await fetch(url, {
      headers: getAuthHeaders()
    })
    
    if (!res.ok) throw new Error(`Error API: ${res.status}`)
    
    const turnos = await res.json()
    const resultados = Array.isArray(turnos) ? turnos : (turnos.results || [])
    
    const ocupadosSet = new Set()
    
    resultados.forEach(turno => {
      if (['CANCELADO', 'DISPONIBLE'].includes(turno.estado)) return
      if (turno.fecha !== fecha) return

      const [h, m] = turno.hora.split(':').map(Number)
      const inicioMin = h * 60 + m
      
      let duracion = turno.duracion_total || 0
      if (!duracion && turno.servicios) {
        if (Array.isArray(turno.servicios) && typeof turno.servicios[0] === 'object') {
          duracion = turno.servicios.reduce((acc, s) => acc + (s.duracion || 20), 0)
        } else {
          duracion = 20 
        }
      }
      if (!duracion) duracion = 20
      
      const finMin = inicioMin + duracion
      
      // 🔥 GUARDAR TODOS LOS MINUTOS OCUPADOS (no solo slots de 20 min)
      for (let i = inicioMin; i < finMin; i++) {
        const hh = Math.floor(i / 60).toString().padStart(2, '0')
        const mm = (i % 60).toString().padStart(2, '0')
        ocupadosSet.add(`${hh}:${mm}`)
      }
    })
    
    slotsOcupadosReales.value = Array.from(ocupadosSet)

  } catch (e) {
    console.error("❌ Error cargando horarios:", e)
  } finally {
    cargandoHorarios.value = false
  }
}

// 🔥 FUNCIÓN PARA UI: Verifica solo el slot inicial
const esHorarioDisponibleUI = (hora) => {
  if (!form.value.fecha || !form.value.peluquero) return true
  
  const [h, m] = hora.split(':').map(Number)
  const horaString = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
  
  // Verificar si el slot inicial está ocupado
  if (slotsOcupadosReales.value.some(slot => 
      slot.startsWith(horaString.substring(0, 5)))) return false

  const hoy = new Date()
  const hoyFormateado = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
  
  if (form.value.fecha === hoyFormateado) {
    if (h < hoy.getHours()) return false
    if (h === hoy.getHours() && m < hoy.getMinutes()) return false
  }
  return true
}

// 🔥 NUEVA FUNCIÓN: Verifica disponibilidad COMPLETA considerando duración
const esHorarioDisponibleCompleto = (horaSeleccionada) => {
  if (!form.value.fecha || !form.value.peluquero) return false
  
  // Calcular duración total de los servicios seleccionados
  const duracionTotal = form.value.servicios_ids.reduce((acc, id) => {
    const s = servicios.value.find(x => x.id === id)
    return acc + (s ? parseInt(s.duracion) : 0)
  }, 0)
  
  // Si no hay servicios seleccionados, duración mínima
  if (duracionTotal === 0) return esHorarioDisponibleUI(horaSeleccionada)
  
  // Convertir hora seleccionada a minutos
  const [h, m] = horaSeleccionada.split(':').map(Number)
  const inicioMinutos = h * 60 + m
  const finMinutos = inicioMinutos + duracionTotal
  
  // Verificar minuto por minuto si hay solapamiento
  for (let i = inicioMinutos; i < finMinutos; i++) {
    const horaSlot = Math.floor(i / 60).toString().padStart(2, '0')
    const minutoSlot = (i % 60).toString().padStart(2, '0')
    const slotActual = `${horaSlot}:${minutoSlot}`
    
    // Si este minuto está ocupado por otro turno, no está disponible
    if (slotsOcupadosReales.value.some(slot => 
        slot.startsWith(slotActual.substring(0, 5)))) {
      return false
    }
  }
  
  // También verificar que no sea una hora pasada si es hoy
  const hoy = new Date()
  const hoyFormateado = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
  if (form.value.fecha === hoyFormateado) {
    if (inicioMinutos < (hoy.getHours() * 60 + hoy.getMinutes())) {
      return false
    }
  }
  
  return true
}

const guardarContexto = () => {
  const contexto = {
    categoriasSeleccionadas: categoriasSeleccionadas.value,
    serviciosSeleccionados: form.value.servicios_ids,
    peluquero: form.value.peluquero,
    silla_id: form.value.silla, // 🔥 GUARDAMOS SILLA
    tipo_pago: form.value.tipo_pago,
    medio_pago: form.value.medio_pago,
    entidad_pago: form.value.entidad_pago,
    codigo_transaccion: form.value.codigo_transaccion,
    fecha: form.value.fecha,
    hora: form.value.hora,
    timestamp: Date.now()
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(contexto))
}

const cargarContexto = () => {
  const contextoStr = sessionStorage.getItem(STORAGE_KEY)
  if (contextoStr) {
    try {
      const contexto = JSON.parse(contextoStr)
      if (contexto.tipo_pago) form.value.tipo_pago = contexto.tipo_pago
      if (contexto.medio_pago) form.value.medio_pago = contexto.medio_pago
      if (contexto.entidad_pago) form.value.entidad_pago = contexto.entidad_pago
      if (contexto.codigo_transaccion) form.value.codigo_transaccion = contexto.codigo_transaccion
      
      if (contexto.peluquero && form.value.cliente !== contexto.peluquero) {
        form.value.peluquero = contexto.peluquero
      }
      if (contexto.silla) form.value.silla = contexto.silla // 🔥 RECUPERAMOS SILLA
      if (contexto.fecha) form.value.fecha = contexto.fecha
      if (contexto.hora) form.value.hora = contexto.hora
      if (contexto.serviciosSeleccionados && contexto.serviciosSeleccionados.length > 0) {
        form.value.servicios_ids = contexto.serviciosSeleccionados
      }
      if (contexto.categoriasSeleccionadas && contexto.categoriasSeleccionadas.length > 0) {
        categoriasSeleccionadas.value = contexto.categoriasSeleccionadas
      }
      if (form.value.fecha && form.value.peluquero && form.value.peluquero !== form.value.cliente) {
        cargarHorariosOcupados(form.value.fecha)
      }
    } catch (e) { console.error(e) }
  }
}

const limpiarContexto = () => sessionStorage.removeItem(STORAGE_KEY)

// 🔥 CORREGIDO: cargarDatosIniciales con headers de autenticación
const cargarDatosIniciales = async () => {
  try {
    cargandoDatos.value = true
    
    const headers = getAuthHeaders()

    const [catRes, servRes, pelRes, sillasRes] = await Promise.all([
      fetch(`${API_URL}/categorias/servicios/`, { headers }),
      fetch(`${API_URL}/servicios/`, { headers }),
      fetch(`${API_URL}/peluqueros/`, { headers }),
      fetch(`${API_URL}/sillas/`, { headers }) // 🔥 CARGAMOS SILLAS
    ])
    
    // Verificar respuestas
    if (!catRes.ok) throw new Error(`Error categorías: ${catRes.status}`)
    if (!servRes.ok) throw new Error(`Error servicios: ${servRes.status}`)
    if (!pelRes.ok) throw new Error(`Error peluqueros: ${pelRes.status}`)
    // No cortamos si fallan las sillas, solo logueamos
    if (sillasRes.ok) sillas.value = await sillasRes.json()
    
    categorias.value = await catRes.json()
    servicios.value = await servRes.json()
    peluqueros.value = await pelRes.json()

    console.log("✅ Datos cargados correctamente")
    console.log("- Categorías:", categorias.value.length)
    console.log("- Servicios:", servicios.value.length)
    console.log("- Peluqueros:", peluqueros.value.length)
    console.log("- Sillas:", sillas.value.length)

  } catch (error) {
    console.error("❌ Error en cargarDatosIniciales:", error)
    
    // Mostrar error específico
    if (error.message.includes('401')) {
      mensaje.value = "Error de autenticación. Por favor, vuelve a iniciar sesión."
      mensajeTipo.value = "error"
      setTimeout(() => {
        localStorage.removeItem('token')
        router.push('/login')
      }, 2000)
    } else {
      mensaje.value = "Error cargando datos del servidor: " + error.message
      mensajeTipo.value = "error"
    }
  } finally {
    cargandoDatos.value = false
  }
}

const actualizarBusquedaCliente = async (e) => {
  busquedaCliente.value = e.target.value
  if (busquedaCliente.value.length < 1) {
    clientesSugeridos.value = []
    return
  }
  try {
    const res = await fetch(`${API_URL}/clientes/?q=${busquedaCliente.value}`, {
      headers: getAuthHeaders()
    })
    const data = await res.json()
    clientesSugeridos.value = data.results || data || []
    errorCliente.value = clientesSugeridos.value.length === 0 ? "No se encontraron clientes" : ""
  } catch (e) { 
    errorCliente.value = "Error al buscar clientes" 
    console.error("Error buscando clientes:", e)
  }
}

const seleccionarCliente = (c) => {
  if (!c || !c.id) return
  form.value.cliente = parseInt(c.id)
  const nombre = c.nombre || c.first_name || ''
  const apellido = c.apellido || c.last_name || ''
  form.value.clienteNombre = `${nombre} ${apellido}`.trim()
  clientesSugeridos.value = []
  busquedaCliente.value = ""
  if (form.value.peluquero === c.id) {
    form.value.peluquero = ""
    resetFechas()
  }
  if (form.value.fecha && form.value.peluquero) cargarHorariosOcupados(form.value.fecha)
}

const limpiarCliente = () => {
  form.value.cliente = null
  form.value.clienteNombre = ""
  busquedaCliente.value = ""
  categoriasSeleccionadas.value = []
  form.value.servicios_ids = []
  form.value.peluquero = ""
  resetFechas()
}

const irARegistrarCliente = () => {
  guardarContexto()
  router.push('/usuarios/crear?returnTo=turnos')
}

const getNombreCompletoCliente = (c) => `${c.nombre || ''} ${c.apellido || ''}`.trim()

const toggleCategoria = (id) => {
  const index = categoriasSeleccionadas.value.indexOf(id)
  if (index > -1) categoriasSeleccionadas.value.splice(index, 1)
  else categoriasSeleccionadas.value.push(id)
  form.value.servicios_ids = []
  form.value.peluquero = ""
}

const toggleServicio = (servicio) => {
  const index = form.value.servicios_ids.indexOf(servicio.id)
  if (index > -1) form.value.servicios_ids.splice(index, 1)
  else form.value.servicios_ids.push(servicio.id)
  form.value.peluquero = ""
  resetFechas()
}

const seleccionarPeluquero = (id) => {
  form.value.peluquero = id
  resetFechas()
}

const resetFechas = () => {
  form.value.fecha = ""
  form.value.hora = ""
  slotsOcupadosReales.value = []
}

const cambiarMes = (dir) => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(currentDate.value.getMonth() + dir)
  currentDate.value = newDate
}

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

// 🔥 CORREGIDO: seleccionarHora usa la verificación COMPLETA
const seleccionarHora = (hora) => {
  if (esHorarioDisponibleCompleto(hora)) form.value.hora = hora
}

const calcularTotal = () => {
  return form.value.servicios_ids.reduce((total, id) => {
    const s = servicios.value.find(x => x.id === id)
    return total + (s ? parseFloat(s.precio) : 0)
  }, 0).toFixed(2)
}

const calcularSena = () => (calcularTotal() / 2).toFixed(2)

// 🔥 CORRECCIÓN COMPLETA: Función crearTurno
const crearTurno = async () => {
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
  
  errorValidacion.value = false
  procesando.value = true
  
  const duracion = form.value.servicios_ids.reduce((acc, id) => {
    const s = servicios.value.find(x => x.id === id)
    return acc + (s ? parseInt(s.duracion) : 0)
  }, 0)

  const totalCalculado = parseFloat(calcularTotal())
  const esPagoSena = form.value.tipo_pago.includes('SENA')

  // Lógica para determinar entidad_pago
  let entidadFinal = null;
  if (form.value.medio_pago === 'MERCADO_PAGO') {
    entidadFinal = 'MERCADO_PAGO';
  } else if (form.value.medio_pago === 'TRANSFERENCIA') {
    entidadFinal = form.value.entidad_pago;
  }

  const payload = {
    peluquero_id: form.value.peluquero,
    cliente_id: form.value.cliente,
    servicios_ids: form.value.servicios_ids,
    fecha: form.value.fecha,
    hora: form.value.hora,
    canal: 'PRESENCIAL',
    silla: form.value.silla, // 🔥 ENVIAMOS SILLA
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
    const res = await fetch(`${API_URL}/turnos/crear/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })
    
    const data = await res.json()
    
    if (res.ok && (data.status === 'ok' || res.status === 201)) {
      await Swal.fire({
        icon: 'success',
        title: '¡Turno Reservado!',
        text: 'El turno se ha creado exitosamente',
        confirmButtonText: 'Aceptar',
        timer: 2000,
        timerProgressBar: true
      })
      
      limpiarContexto()
      router.push('/turnos')
    } else {
      let errorMsg = "Error al crear turno"
      if (data.message) errorMsg = data.message
      if (data.errors) {
        errorMsg = Object.entries(data.errors)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
          .join('; ')
      }
      await Swal.fire({
        icon: 'error',
        title: 'Error',
        text: errorMsg,
        confirmButtonText: 'Entendido'
      })
    }
  } catch (e) {
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: e.message,
      confirmButtonText: 'Entendido'
    })
    console.error('Error completo:', e)
  } finally {
    procesando.value = false
  }
}

const volverAlListado = () => {
  limpiarContexto()
  router.push('/turnos')
}

// No necesitas estas variables si no las usas
const mostrarModalRegistro = ref(false)
const creandoCliente = ref(false)
const errorCrearCliente = ref("")
const formNuevoCliente = ref({ nombre: "", apellido: "", dni: "", telefono: "", correo: "", contrasena: "" })
const erroresCliente = ref({ nombre: "", apellido: "", dni: "", correo: "", contrasena: "" })

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const nuevoClienteId = urlParams.get('nuevo_cliente_id')
  const nuevoClienteNombre = urlParams.get('nuevo_cliente_nombre')
  
  if (nuevoClienteId && nuevoClienteNombre) {
    seleccionarCliente({
      id: parseInt(nuevoClienteId),
      nombre: decodeURIComponent(nuevoClienteNombre.split('+')[0]),
      apellido: decodeURIComponent(nuevoClienteNombre.split('+')[1] || '')
    })
    cargarContexto()
    window.history.replaceState({}, '', window.location.pathname)
  }
  
  // Verificar token antes de cargar
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  
  cargarDatosIniciales()
})

onBeforeUnmount(() => {
  if (!window.location.pathname.includes('/usuarios/crear')) {
    limpiarContexto()
  }
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

/* 🔥 PROFESIONALES - CARDS EN VEZ DE SELECT */
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

/* 🔥 ESTILOS PARA EL SELECTOR DE SILLA (NUEVO) */
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
  padding-right: 40px; /* Espacio para el icono */
}

.form-control-select:focus {
  border-color: #8b5cf6; /* Morado para diferenciar */
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

/* 🔥 HORARIOS MEJORADOS */
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

.hora-card:hover:not(.hora-ocupada) {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.hora-icono {
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hora-ocupada .hora-icono {
  color: #dc2626;
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

.hora-selected .hora-texto,
.hora-selected .hora-icono { 
  color: white; 
}

/* 🔥 HORARIOS OCUPADOS - ESTILO MEJORADO */
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

.hora-ocupada:hover {
  border-color: #f87171;
  transform: none;
  box-shadow: none;
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

.btn-icon-clean { 
  position: absolute; 
  right: 12px; 
  top: 50%; 
  transform: translateY(-50%); 
  background: none; 
  border: none; 
  color: #dc3545; 
  cursor: pointer; 
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-icon-clean:hover {
  background: #fee2e2;
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
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #1f2937, #374151);
  border-radius: 16px 16px 0 0;
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4em;
  font-weight: 600;
}

.modal-close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.input-error {
  border-color: #dc3545 !important;
  background: #fff5f5 !important;
}

.msg-error.small {
  font-size: 0.85em;
  padding: 8px 12px;
  margin-top: 5px;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #f9fafb;
  border-radius: 0 0 16px 16px;
}

.btn-secondary {
  background: #6b7280;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.lista-sugerencias {
  position: absolute;
  background: white;
  border: 2px solid #e5e7eb;
  width: 100%;
  max-height: 250px;
  overflow-y: auto;
  z-index: 100;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  margin-top: 5px;
  list-style: none;
  padding: 8px 0;
}

.item-sugerencia { 
  padding: 12px 16px; 
  color: #4b5563; 
  display: flex; 
  gap: 12px; 
  align-items: center; 
  cursor: pointer; 
  border-radius: 8px; 
  transition: all 0.2s;
  margin: 0 8px;
}

.item-sugerencia:hover { 
  background: #f3f4f6; 
}

.avatar-mini { 
  width: 36px; 
  height: 36px; 
  background: #e0f2fe; 
  color: #3b82f6; 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  flex-shrink: 0;
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

.mt-3 {
  margin-top: 16px;
}

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
  background: rgb(72, 255, 130);
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
  background: #747474; 
  color: #ffffff; 
  cursor: not-allowed; 
  opacity: 0.6;
}

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