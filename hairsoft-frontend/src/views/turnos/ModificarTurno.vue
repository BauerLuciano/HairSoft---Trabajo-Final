<template>
  <!-- FONDO DEGRADADO -->
  <div class="page-background">
    <!-- TARJETA BLANCA QUE ENVUELVE TODO -->
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
          <!-- ==================== -->
          <!-- CLIENTE (SOLO LECTURA) -->
          <!-- ==================== -->
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

          <!-- ==================== -->
          <!-- CATEGORÍA -->
          <!-- ==================== -->
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

          <!-- ==================== -->
          <!-- SERVICIOS -->
          <!-- ==================== -->
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

          <!-- ==================== -->
          <!-- PROFESIONAL -->
          <!-- ==================== -->
          <div v-if="form.servicios_ids.length > 0" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon"><UserCheck :size="20" /></div>
              <h3>Profesional</h3>
            </div>
            <select v-model="form.peluquero" @change="alCambiarPeluquero" class="select-modern">
              <option value="">-- Seleccionar --</option>
              <option 
                v-for="p in peluqueros" 
                :key="p.id" 
                :value="p.id"
                :disabled="p.id === form.cliente"
              >
                {{ p.nombre }} {{ p.apellido || '' }} {{ p.id === form.cliente ? '(Es el cliente)' : '' }}
              </option>
            </select>
            <div v-if="form.peluquero === form.cliente && form.cliente" class="msg-error mt-2">
              <AlertCircle :size="14" /> No puedes seleccionar al mismo profesional como cliente.
            </div>
          </div>

          <!-- ==================== -->
          <!-- FECHA -->
          <!-- ==================== -->
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

          <!-- ==================== -->
          <!-- HORARIOS DISPONIBLES -->
          <!-- ==================== -->
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
                  'hora-disponible': esHorarioDisponible(hora),
                  'hora-ocupada': !esHorarioDisponible(hora)
                }"
                @click="esHorarioDisponible(hora) ? seleccionarHora(hora) : null"
              >
                <span class="hora-texto">{{ hora }}</span>
                <span v-if="!esHorarioDisponible(hora)" class="etiqueta-ocupado">OCUPADO</span>
              </div>
            </div>
          </div>

          <!-- ==================== -->
          <!-- CONFIRMACIÓN -->
          <!-- ==================== -->
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
                  <option value="TARJETA">💳 Tarjeta</option>
                  <option value="TRANSFERENCIA">📱 Transferencia / MP</option>
                </select>
              </div>
              
              <div v-if="form.medio_pago !== 'EFECTIVO'" class="input-group">
                <label class="label-modern">Nro. Comprobante (Opcional)</label>
                <input type="text" v-model="form.comprobante_id" class="input-modern" placeholder="Ej: 12345678" />
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

  <!-- MODAL CAMBIAR CLIENTE -->
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
          
          <ul v-if="clientesSugeridosModal.length" class="lista-sugerencias">
            <li v-for="c in clientesSugeridosModal" :key="c.id" @click="seleccionarClienteModal(c)" class="item-sugerencia">
              <div class="avatar-mini"><User :size="14" /></div>
              <div class="sugerencia-info">
                <strong>{{ getNombreCompletoCliente(c) }}</strong>
                <small>  - DNI: {{ c.dni || '---' }}</small>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Calendar, ArrowLeft, Users, Search, Edit3, Tag, Scissors, 
  Check, Clock, UserCheck, CalendarDays, ChevronLeft, ChevronRight, 
  Info, Loader2, Receipt, AlertCircle, CheckCircle, User, 
  Plus, FolderOpen, Inbox, X
} from 'lucide-vue-next'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const turnoId = route.params.id

// ✅ CORREGIDO: Ruta sin /usuarios/
const API_URL = "http://localhost:8000/api"

// Estados de carga
const cargando = ref(true)
const procesando = ref(false)
const error = ref(null)
const mensaje = ref("")
const mensajeTipo = ref("success")
const cargandoHorarios = ref(false)

// Datos del turno
const turnoData = ref({})

// Modal cambiar cliente
const mostrarModalCliente = ref(false)
const busquedaClienteModal = ref("")
const clientesSugeridosModal = ref([])
const errorClienteModal = ref("")

// Datos de formulario
const form = ref({
  canal: 'PRESENCIAL',
  cliente: null,
  clienteNombre: "",
  clienteDni: "",
  peluquero: "",
  servicios_ids: [],
  tipo_pago: "SENA_50",
  medio_pago: "EFECTIVO",
  comprobante_id: "",
  fecha: "",
  hora: ""
})

// Datos maestros
const categorias = ref([])
const servicios = ref([])
const peluqueros = ref([])
const categoriasSeleccionadas = ref([])
const slotsOcupadosReales = ref([])
const currentDate = ref(new Date())

// Computed properties (EXACTAMENTE IGUAL AL REGISTRAR)
const serviciosFiltrados = computed(() => {
  if (categoriasSeleccionadas.value.length === 0) return []
  const nombresCats = categorias.value
    .filter(c => categoriasSeleccionadas.value.includes(c.id))
    .map(c => c.nombre)
  return servicios.value.filter(s => nombresCats.includes(s.categoria))
})

const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())
const nombreMesActual = computed(() => {
  const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
  return meses[currentMonth.value]
})
const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
})
const startingDayOfWeek = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 1).getDay()
})

const horariosGenerados = computed(() => {
  const horariosBase = []
  const bloques = [
    { inicio: 8, fin: 12 }, 
    { inicio: 15, fin: 20 }
  ]
  const ahora = new Date()
  const horaActual = ahora.getHours()
  const minutoActual = ahora.getMinutes()
  const hoy = new Date()
  const hoyFormateado = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
  
  const fechaForm = form.value.fecha
  const esHoy = fechaForm === hoyFormateado

  bloques.forEach(b => {
    for (let h = b.inicio; h < b.fin; h++) {
      for (let m = 0; m < 60; m += 20) {
        const horaStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
        if (esHoy) {
          if (h < horaActual) continue
          if (h === horaActual && m <= minutoActual) continue
        }
        horariosBase.push(horaStr)
      }
    }
    const cierreH = b.fin
    const cierreStr = `${String(cierreH).padStart(2, '0')}:00`
    let agregarCierre = true
    if (esHoy) {
       if (cierreH < horaActual) agregarCierre = false
       if (cierreH === horaActual && 0 <= minutoActual) agregarCierre = false
    }
    if (agregarCierre) horariosBase.push(cierreStr)
  })

  return horariosBase
})

const formularioValido = computed(() => {
  return (
    form.value.cliente &&
    form.value.peluquero &&
    form.value.servicios_ids.length > 0 &&
    form.value.fecha &&
    form.value.hora &&
    form.value.tipo_pago &&
    form.value.medio_pago
  )
})

// Métodos de calendario (EXACTAMENTE IGUAL AL REGISTRAR)
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
  const isInRange = diffDays >= 0 && diffDays <= 7
  const isSunday = date.getDay() === 0
  return isInRange && !isSunday
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

// Métodos de datos (AJUSTADOS PARA MODIFICAR)
const cargarDatosTurno = async () => {
  try {
    cargando.value = true
    
    // ✅ CORREGIDO: Rutas sin /usuarios/
    const [turnoRes, catRes, servRes, pelRes] = await Promise.all([
      fetch(`${API_URL}/turnos/${turnoId}/`),
      fetch(`${API_URL}/categorias/servicios/`),
      fetch(`${API_URL}/servicios/`),
      fetch(`${API_URL}/peluqueros/`)
    ])

    // Verificar si el turno existe
    if (!turnoRes.ok) {
      throw new Error("Turno no encontrado")
    }
    
    const turno = await turnoRes.json()
    categorias.value = await catRes.json()
    servicios.value = await servRes.json()
    peluqueros.value = await pelRes.json()
    
    console.log("📦 Turno cargado:", turno)
    turnoData.value = turno
    
    // Asignar datos del turno al formulario
    form.value.cliente = turno.cliente_id
    form.value.clienteNombre = `${turno.cliente_nombre} ${turno.cliente_apellido}`.trim()
    form.value.clienteDni = turno.cliente_dni || ""
    
    form.value.peluquero = turno.peluquero_id
    
    // Servicios y categorías
    form.value.servicios_ids = turno.servicios.map(s => s.id)
    
    // Obtener categorías de los servicios
    const categoriasDelTurno = new Set()
    turno.servicios.forEach(servicio => {
      const serv = servicios.value.find(s => s.id === servicio.id)
      if (serv) {
        const categoria = categorias.value.find(c => c.nombre === serv.categoria)
        if (categoria) categoriasDelTurno.add(categoria.id)
      }
    })
    categoriasSeleccionadas.value = Array.from(categoriasDelTurno)
    
    // Fecha y hora
    form.value.fecha = turno.fecha
    form.value.hora = turno.hora
    
    // Pago
    form.value.tipo_pago = turno.tipo_pago
    form.value.medio_pago = turno.medio_pago || "EFECTIVO"
    
    // Si hay fecha, cargar horarios ocupados
    if (form.value.fecha && form.value.peluquero) {
      await cargarHorariosOcupados(form.value.fecha)
    }
    
  } catch (err) {
    console.error("❌ Error cargando turno:", err)
    error.value = "No se pudo cargar el turno. Verifica que exista."
    
    // Mostrar error con SweetAlert
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar el turno. Verifica que exista.',
      confirmButtonText: 'Volver al listado'
    }).then(() => {
      router.push('/turnos')
    })
  } finally {
    cargando.value = false
  }
}

const cargarDatosIniciales = async () => {
  await cargarDatosTurno()
}

const alCambiarPeluquero = () => {
  resetFechas()
}

const resetFechas = () => {
  form.value.fecha = ""
  form.value.hora = ""
  slotsOcupadosReales.value = []
}

const cargarHorariosOcupados = async (fecha) => {
  form.value.hora = ""
  cargandoHorarios.value = true
  slotsOcupadosReales.value = [] 
  
  try {
    // ✅ CORREGIDO: Ruta sin /usuarios/
    const url = `${API_URL}/turnos/?fecha=${fecha}&peluquero_id=${form.value.peluquero}&estado__in=RESERVADO,CONFIRMADO`
    const res = await fetch(url)
    const turnos = await res.json()
    
    const ocupadosSet = new Set()
    
    turnos.forEach(turno => {
      if (turno.id === parseInt(turnoId)) return // Excluir el turno actual
        
      const [h, m] = turno.hora.split(':').map(Number)
      const inicioMin = h * 60 + m
      
      let duracion = turno.duracion_total || 0
      if (!duracion && turno.servicios) {
          duracion = turno.servicios.reduce((acc, s) => acc + (s.duracion || 20), 0)
      }
      if (!duracion) duracion = 20
      
      const finMin = inicioMin + duracion
      
      for (let i = inicioMin; i < finMin; i += 20) {
          const hh = Math.floor(i / 60).toString().padStart(2, '0')
          const mm = (i % 60).toString().padStart(2, '0')
          ocupadosSet.add(`${hh}:${mm}`)
      }
    })
    
    slotsOcupadosReales.value = Array.from(ocupadosSet)
  } catch (e) {
    console.error("Error cargando turnos:", e)
  } finally {
    cargandoHorarios.value = false
  }
}

const esHorarioDisponible = (hora) => {
  if (!form.value.fecha || !form.value.peluquero) return true
  const horaSimple = hora.substring(0, 5)
  return !slotsOcupadosReales.value.includes(horaSimple)
}

const seleccionarHora = (hora) => {
  if (esHorarioDisponible(hora)) {
    form.value.hora = hora
  }
}

const toggleCategoria = (id) => {
  const index = categoriasSeleccionadas.value.indexOf(id)
  if (index > -1) {
    categoriasSeleccionadas.value.splice(index, 1)
  } else {
    categoriasSeleccionadas.value.push(id)
  }
  form.value.servicios_ids = []
  form.value.peluquero = ""
}

const toggleServicio = (servicio) => {
  const index = form.value.servicios_ids.indexOf(servicio.id)
  if (index > -1) {
    form.value.servicios_ids.splice(index, 1)
  } else {
    form.value.servicios_ids.push(servicio.id)
  }
  form.value.peluquero = ""
  resetFechas()
}

const calcularTotal = () => {
  return form.value.servicios_ids.reduce((total, id) => {
    const s = servicios.value.find(x => x.id === id)
    return total + (s ? parseFloat(s.precio) : 0)
  }, 0).toFixed(2)
}

const calcularSena = () => {
  return (calcularTotal() / 2).toFixed(2)
}

// Métodos para cambiar cliente
const abrirModalCambiarCliente = () => {
  mostrarModalCliente.value = true
  busquedaClienteModal.value = ""
  clientesSugeridosModal.value = []
  errorClienteModal.value = ""
}

const cerrarModalCliente = () => {
  mostrarModalCliente.value = false
}

const actualizarBusquedaClienteModal = async () => {
  if (busquedaClienteModal.value.length < 1) {
    clientesSugeridosModal.value = []
    return
  }
  try {
    // ✅ CORREGIDO: Ruta sin /usuarios/
    const res = await fetch(`${API_URL}/clientes/?q=${busquedaClienteModal.value}`)
    const data = await res.json()
    clientesSugeridosModal.value = data.results || data || []
    errorClienteModal.value = clientesSugeridosModal.value.length === 0 ? "No se encontraron clientes" : ""
  } catch (e) {
    errorClienteModal.value = "Error de conexión"
  }
}

const getNombreCompletoCliente = (c) => {
  return `${c.nombre || c.first_name || ''} ${c.apellido || c.last_name || ''}`.trim()
}

const seleccionarClienteModal = (c) => {
  form.value.cliente = c.id
  form.value.clienteNombre = getNombreCompletoCliente(c)
  form.value.clienteDni = c.dni || ""
  cerrarModalCliente()
  
  if (form.value.peluquero === c.id) {
      form.value.peluquero = ""
      resetFechas()
  }
}

// Método principal para modificar
const modificarTurno = async () => {
  procesando.value = true
  mensaje.value = ""
  
  const duracion = form.value.servicios_ids.reduce((acc, id) => {
    const s = servicios.value.find(x => x.id === id)
    return acc + (s ? parseInt(s.duracion) : 0)
  }, 0)

  const payload = {
    peluquero_id: form.value.peluquero,
    cliente_id: form.value.cliente,
    servicios_ids: form.value.servicios_ids,
    fecha: form.value.fecha,
    hora: form.value.hora,
    canal: 'PRESENCIAL',
    tipo_pago: form.value.tipo_pago,
    medio_pago: form.value.medio_pago,
    monto_total: parseFloat(calcularTotal()),
    monto_seña: form.value.tipo_pago === 'SENA_50' ? parseFloat(calcularSena()) : 0,
    duracion_total: duracion,
    mp_payment_id: form.value.medio_pago !== 'EFECTIVO' ? form.value.comprobante_id : null
  }

  try {
    const token = localStorage.getItem('token')
    // ✅ CORREGIDO: Ruta sin /usuarios/
    const res = await fetch(`${API_URL}/turnos/${turnoId}/modificar/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token ? `Token ${token}` : ''
      },
      body: JSON.stringify(payload)
    })
    
    const data = await res.json()
    
    if (res.ok && data.status === 'ok') {
      mensaje.value = "¡Turno Actualizado con Éxito!"
      mensajeTipo.value = "success"
      await Swal.fire({
        icon: 'success',
        title: 'Turno Actualizado',
        text: 'El turno se actualizó correctamente',
        confirmButtonText: 'Aceptar'
      })
      router.push('/turnos')
    } else {
      mensaje.value = data.message || "Error al actualizar turno"
      mensajeTipo.value = "error"
    }
  } catch (e) {
    mensaje.value = "Error de conexión con el servidor"
    mensajeTipo.value = "error"
  } finally {
    procesando.value = false
  }
}

const volverAlListado = () => {
  router.push('/turnos')
}

onMounted(() => {
  cargarDatosIniciales()
})
</script>

<style scoped>
/* ============================================
   ESTILOS EXACTAMENTE IGUALES AL REGISTRAR
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

/* Grilla de Horarios */
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
  padding: 16px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hora-card:hover {
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
  background: #fee2e2;
  border-color: #fca5a5;
  cursor: not-allowed;
  opacity: 0.7;
}

.hora-ocupada .hora-texto {
  text-decoration: line-through;
  color: #dc3545;
}

.etiqueta-ocupado {
  display: block;
  font-size: 0.7em;
  color: #dc3545;
  font-weight: 700;
  margin-top: 4px;
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

/* Sugerencias */
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

/* Calendario */
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

.calendar-footer { 
  text-align: center; 
  margin-top: 20px; 
  font-size: 0.9em; 
  color: #6b7280; 
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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

.label-modern {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
  color: #1f2937;
  font-size: 1rem;
}

/* Botón Final */
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

.fade-enter-active, .fade-leave-active { 
  transition: opacity 0.5s ease; 
}

.fade-enter-from, .fade-leave-to { 
  opacity: 0; 
}

/* Animaciones */
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

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 100%;
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
}

/* Botón Cancelar para estado de error */
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
  
  .grid-servicios {
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