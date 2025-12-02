<template>
  <div class="turno-container">
    <div class="header-section">
      <h2>
        <Calendar class="header-icon" />
        Nuevo Turno
      </h2>
      <button @click="volverAlListado" class="btn-back">
        <ArrowLeft :size="18" />
        Volver al Listado
      </button>
    </div>

    <!-- Selección de Cliente -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <Users :size="20" />
        </div>
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
            <Plus :size="18" />
            Nuevo Cliente
          </button>
        </div>

        <ul v-if="clientesSugeridos.length && !form.cliente" class="lista-sugerencias">
          <li v-for="c in clientesSugeridos" :key="c.id" @click="seleccionarCliente(c)" class="item-sugerencia">
            <div class="avatar-mini">
              <User :size="14" />
            </div>
            <div class="sugerencia-info">
              <strong>{{ getNombreCompletoCliente(c) }}</strong>
              <small>
                <IdCard :size="12" />
                DNI: {{ c.dni || '---' }}
              </small>
            </div>
          </li>
        </ul>
        
        <div v-if="errorCliente" class="msg-error">
          <AlertCircle :size="14" />
          {{ errorCliente }}
        </div>
      </div>
    </div>

    <!-- Categorías -->
    <div v-if="form.cliente" class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <FolderOpen :size="20" />
        </div>
        <h3>Categoría de Servicio</h3>
        <span v-if="categoriasSeleccionadas.length" class="badge-count">
          {{ categoriasSeleccionadas.length }}
        </span>
      </div>
      
      <div class="grid-chips">
        <button 
          v-for="categoria in categorias" 
          :key="categoria.id"
          class="chip-modern"
          :class="{ 'chip-active': categoriasSeleccionadas.includes(categoria.id) }"
          @click="toggleCategoria(categoria.id)"
        >
          <Tag :size="14" />
          {{ categoria.nombre }}
        </button>
      </div>
    </div>

    <!-- Servicios -->
    <div v-if="categoriasSeleccionadas.length > 0" class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <Scissors :size="20" />
        </div>
        <h3>Servicios</h3>
        <span v-if="form.servicios_ids.length" class="badge-count">
          {{ form.servicios_ids.length }}
        </span>
      </div>
      
      <div v-if="serviciosFiltrados.length === 0" class="no-resultados">
        <Inbox class="no-resultados-icon" :size="48" />
        <p>No hay servicios disponibles</p>
        <small>Selecciona una categoría para ver los servicios</small>
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
              <span class="servicio-precio">
                <DollarSign :size="14" />
                ${{ servicio.precio }}
              </span>
              <span class="servicio-duracion">
                <Clock :size="14" />
                {{ servicio.duracion }}m
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profesional -->
    <div v-if="form.servicios_ids.length > 0" class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <UserCheck :size="20" />
        </div>
        <h3>Profesional</h3>
      </div>
      
      <div class="input-group">
        <select v-model="form.peluquero" @change="alCambiarPeluquero" class="select-modern">
          <option value="">-- Seleccionar Profesional --</option>
          <option v-for="p in peluqueros" :key="p.id" :value="p.id">
            {{ p.nombre }} {{ p.apellido || '' }}
          </option>
        </select>
      </div>
    </div>

    <!-- Calendario -->
    <div v-if="form.peluquero" class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <CalendarDays :size="20" />
        </div>
        <h3>Seleccionar Fecha</h3>
      </div>
      
      <div class="calendar-wrapper">
        <div class="calendar-header">
          <button @click="cambiarMes(-1)" class="btn-nav-cal">
            <ChevronLeft :size="20" />
          </button>
          <span class="mes-titulo">{{ nombreMesActual }} {{ currentYear }}</span>
          <button @click="cambiarMes(1)" class="btn-nav-cal">
            <ChevronRight :size="20" />
          </button>
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

        <div class="calendar-footer">
          <Info :size="14" />
          Disponible: Hoy + 7 días (No Domingos)
        </div>
      </div>
    </div>

    <!-- Horarios - VERSIÓN CORREGIDA -->
    <div v-if="form.fecha" class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <Clock :size="20" />
        </div>
        <h3>Horarios Disponibles</h3>
      </div>
      
      <div v-if="cargandoHorarios" class="loading-spinner">
        <Loader2 class="spinner-icon" :size="32" />
        <p>Buscando horarios disponibles...</p>
      </div>
      
      <div v-else-if="horariosGenerados.length === 0" class="no-resultados">
        <Clock class="no-resultados-icon" :size="48" />
        <p>No hay horarios disponibles</p>
        <small>Intenta seleccionar otro día</small>
      </div>
      
      <div v-else class="grid-horarios-mejorado">
        <div
          v-for="hora in horariosGenerados"
          :key="hora"
          class="hora-card-mejorada"
          :class="{
            'hora-selected-mejorada': form.hora === hora,
            'hora-disponible-mejorada': esHorarioDisponible(hora),
            'hora-ocupada-mejorada': !esHorarioDisponible(hora)
          }"
        >
          <div 
            v-if="esHorarioDisponible(hora)"
            class="hora-content-mejorada"
            @click="seleccionarHora(hora)"
          >
            <div class="hora-info-mejorada">
              <Clock :size="16" class="hora-icon-mejorada" />
              <span class="hora-texto-mejorada">{{ hora }}</span>
            </div>
            <div class="hora-estado-mejorada disponible">
              <CheckCircle2 :size="14" />
              <span>Disponible</span>
            </div>
          </div>
          
          <div v-else class="hora-content-mejorada ocupada">
            <div class="hora-info-mejorada">
              <Clock :size="16" class="hora-icon-mejorada" />
              <span class="hora-texto-mejorada">{{ hora }}</span>
            </div>
            <div class="hora-estado-mejorada ocupado">
              <Bell :size="14" class="campanita-icon" />
              <span>Ocupado</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Resumen y Pago -->
    <div v-if="form.hora" class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <Receipt :size="20" />
        </div>
        <h3>Resumen del Turno</h3>
      </div>

      <div class="resumen-grid">
        <div class="resumen-item">
          <div>
            <Scissors :size="16" /> Total de Servicios:
          </div>
          <strong>{{ form.servicios_ids.length }}</strong>
        </div>
        <div class="resumen-item total">
          <div>
            <Wallet :size="18" /> Total a Pagar:
          </div>
          <strong>${{ calcularTotal() }}</strong>
        </div>
      </div>

      <div class="pago-section">
        <label class="label-modern">
          <CreditCard :size="16" />
          Tipo de Pago
        </label>
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
          <label class="label-modern">
            <Banknote :size="16" />
            Método de Pago
          </label>
          <select v-model="form.medio_pago" class="select-modern">
            <option value="EFECTIVO">💵 Efectivo</option>
            <option value="TARJETA">💳 Tarjeta</option>
            <option value="TRANSFERENCIA">📱 Transferencia</option>
          </select>
        </div>
        
        <div v-if="form.medio_pago !== 'EFECTIVO'" class="input-group">
          <label class="label-modern">
            <FileText :size="16" />
            Nro. Comprobante
          </label>
          <input 
            type="text" 
            v-model="form.comprobante_id" 
            class="input-modern"
            placeholder="Ingrese número de comprobante"
          />
        </div>
      </div>
    </div>

    <!-- Botón Final -->
    <button 
      v-if="form.hora"
      @click="crearTurno" 
      class="btn-confirmar-premium"
      :class="{'btn-processing': procesando}"
      :disabled="procesando"
    >
      <span v-if="!procesando" class="btn-content">
        <CheckCircle2 :size="20" />
        Confirmar Reserva - ${{ calcularTotal() }}
      </span>
      <span v-else class="btn-content">
        <Loader2 :size="20" class="btn-spinner" />
        Procesando...
      </span>
    </button>

    <!-- Toast Message -->
    <transition name="fade">
      <div v-if="mensaje" class="toast-message" :class="mensajeTipo">
        <component :is="mensajeTipo === 'success' ? CheckCircle : AlertCircle" :size="18" />
        {{ mensaje }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Calendar, ArrowLeft, Users, Search, X, Plus, User, IdCard,
  AlertCircle, FolderOpen, Tag, Scissors, Check, DollarSign,
  Clock, UserCheck, CalendarDays, ChevronLeft, ChevronRight,
  Info, Loader2, Receipt, Wallet, CreditCard, Bell, CheckCircle2,
  Banknote, FileText, CheckCircle, Inbox
} from 'lucide-vue-next'

const router = useRouter()
const API_URL = "http://localhost:8000/usuarios/api"

// Estados
const form = ref({
  canal: 'PRESENCIAL',
  cliente: null,
  clienteNombre: "",
  peluquero: "",
  servicios_ids: [],
  tipo_pago: "SENA_50",
  medio_pago: "EFECTIVO",
  comprobante_id: "",
  fecha: "",
  hora: ""
})

const categorias = ref([])
const servicios = ref([])
const peluqueros = ref([])
const busquedaCliente = ref("")
const clientesSugeridos = ref([])
const categoriasSeleccionadas = ref([])
const horariosGenerados = ref([])
const turnosOcupadosDelDia = ref([]) // CAMBIADO: ahora almacenará turnos completos
const currentDate = ref(new Date())
const errorCliente = ref("")
const mensaje = ref("")
const mensajeTipo = ref("success")
const procesando = ref(false)
const cargandoHorarios = ref(false)

const horarioApertura = 9
const horarioCierre = 20
const intervaloMinutos = 20

// Computed
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

// Métodos
const cargarDatosIniciales = async () => {
  try {
    const [resCat, resServ, resPel] = await Promise.all([
      fetch(`${API_URL}/categorias/servicios/`),
      fetch(`${API_URL}/servicios/`),
      fetch(`${API_URL}/peluqueros/`)
    ])
    categorias.value = await resCat.json()
    servicios.value = await resServ.json()
    peluqueros.value = await resPel.json()
  } catch (error) {
    console.error("Error API", error)
    mensaje.value = "Error al cargar datos iniciales"
    mensajeTipo.value = "error"
  }
}

const actualizarBusquedaCliente = async (e) => {
  busquedaCliente.value = e.target.value
  if (busquedaCliente.value.length < 2) {
    clientesSugeridos.value = []
    return
  }
  try {
    const res = await fetch(`${API_URL}/clientes/?q=${busquedaCliente.value}`)
    const data = await res.json()
    clientesSugeridos.value = data.results || data || []
    errorCliente.value = clientesSugeridos.value.length === 0 ? "No se encontraron clientes" : ""
  } catch (e) {
    errorCliente.value = "Error de conexión"
  }
}

const seleccionarCliente = (c) => {
  form.value.cliente = c.id
  const nombre = c.nombre || c.first_name || ''
  const apellido = c.apellido || c.last_name || ''
  form.value.clienteNombre = `${nombre} ${apellido}`.trim()
  clientesSugeridos.value = []
  busquedaCliente.value = ""
  errorCliente.value = ""
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
  router.push('/usuarios/crear')
}

const getNombreCompletoCliente = (c) => {
  return `${c.nombre || c.first_name || ''} ${c.apellido || c.last_name || ''}`.trim()
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

const alCambiarPeluquero = () => {
  resetFechas()
}

const resetFechas = () => {
  form.value.fecha = ""
  form.value.hora = ""
  horariosGenerados.value = []
  turnosOcupadosDelDia.value = []
}

const cambiarMes = (dir) => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(currentDate.value.getMonth() + dir)
  currentDate.value = newDate
}

const esHoy = (day) => {
  const today = new Date()
  return day === today.getDate() && 
         currentMonth.value === today.getMonth() && 
         currentYear.value === today.getFullYear()
}

const esDiaSeleccionado = (day) => {
  if (!form.value.fecha) return false
  const [y, m, d] = form.value.fecha.split('-').map(Number)
  return day === d && (currentMonth.value + 1) === m && currentYear.value === y
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

const seleccionarDiaCalendario = (day) => {
  if (!esDiaSeleccionable(day)) return
  
  const mesStr = String(currentMonth.value + 1).padStart(2, '0')
  const diaStr = String(day).padStart(2, '0')
  form.value.fecha = `${currentYear.value}-${mesStr}-${diaStr}`
  
  cargarHorariosParaFecha(form.value.fecha)
}

// 🎯 CORREGIDO: Ahora sí filtra por peluquero específico
const cargarHorariosParaFecha = async (fecha) => {
  form.value.hora = ""
  cargandoHorarios.value = true
  turnosOcupadosDelDia.value = [] // Limpiar antes de cargar
  
  try {
    // URL corregida: solo turnos del peluquero seleccionado en la fecha seleccionada
    const url = `${API_URL}/turnos/?fecha=${fecha}&peluquero_id=${form.value.peluquero}&estado__in=RESERVADO,CONFIRMADO`
    const res = await fetch(url)
    const data = await res.json()
    
    // Guardamos los turnos completos para poder filtrar por peluquero
    turnosOcupadosDelDia.value = data.results || data || []
    
  } catch (e) {
    console.error("Error cargando turnos ocupados:", e)
    turnosOcupadosDelDia.value = []
  }
  
  generarGrillaHorarios(fecha)
  cargandoHorarios.value = false
}

const generarGrillaHorarios = (fechaStr) => {
  const horarios = []
  const [year, month, day] = fechaStr.split('-').map(Number)
  const fechaSeleccionada = new Date(year, month - 1, day)
  const esHoy = new Date().toDateString() === fechaSeleccionada.toDateString()
  const ahora = new Date()

  for (let h = horarioApertura; h < horarioCierre; h++) {
    for (let m = 0; m < 60; m += intervaloMinutos) {
      const horaStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
      if (esHoy) {
        const fechaHoraLoop = new Date()
        fechaHoraLoop.setHours(h, m, 0, 0)
        if (fechaHoraLoop <= ahora) continue
      }
      horarios.push(horaStr)
    }
  }
  horariosGenerados.value = horarios
}

// 🎯 CORREGIDO: Ahora sí verifica si el horario está ocupado por ESTE peluquero
const esHorarioDisponible = (hora) => {
  if (!form.value.fecha || !form.value.peluquero) return true
  
  // Buscar turnos ocupados para este peluquero específico en esta fecha y hora
  const turnoOcupado = turnosOcupadosDelDia.value.find(turno => {
    // Verificar que el turno sea del mismo peluquero
    const mismoPeluquero = turno.peluquero_id == form.value.peluquero
    
    // Verificar que sea la misma fecha (formato puede variar)
    const mismaFecha = turno.fecha === form.value.fecha || 
                      turno.fecha === form.value.fecha.replace(/-/g, '/')
    
    // Verificar que sea la misma hora
    const mismaHora = turno.hora === hora
    
    return mismoPeluquero && mismaFecha && mismaHora
  })
  
  return !turnoOcupado
}

const seleccionarHora = (hora) => {
  if (esHorarioDisponible(hora)) {
    form.value.hora = hora
  }
}

const calcularTotal = () => {
  return form.value.servicios_ids.reduce((total, id) => {
    const s = servicios.value.find(x => x.id === id)
    return total + (s ? parseFloat(s.precio) : 0)
  }, 0)
}

const calcularSena = () => {
  return calcularTotal() / 2
}

const crearTurno = async () => {
  procesando.value = true
  mensaje.value = ""
  
  const duracion = form.value.servicios_ids.reduce((acc, id) => {
    const s = servicios.value.find(x => x.id === id)
    return acc + (s ? parseInt(s.duracion) : 0)
  }, 0)

  const payload = {
    ...form.value,
    monto_total: calcularTotal(),
    monto_seña: form.value.tipo_pago === 'SENA_50' ? calcularSena() : 0,
    duracion_total: duracion
  }

  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_URL}/turnos/crear/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token ? `Token ${token}` : ''
      },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (res.ok && data.status === 'ok') {
      mensaje.value = "¡Turno Reservado con Éxito!"
      mensajeTipo.value = "success"
      setTimeout(() => router.push('/turnos'), 2000)
    } else {
      mensaje.value = data.message || "Error al crear turno"
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
.turno-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 25px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.header-section h2 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: #007bff;
}

.btn-back {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-back:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Cards */
.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #007bff;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15);
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
  background: linear-gradient(135deg, #007bff, #0056b3);
  padding: 10px;
  border-radius: 10px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
}

.badge-count {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 600;
}

/* Inputs */
.input-group {
  margin-bottom: 20px;
}

.label-modern {
  display: block;
  font-weight: 700;
  color: #334155;
  margin-bottom: 10px;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.row-search {
  display: flex;
  gap: 10px;
}

.search-wrapper {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.input-modern {
  width: 100%;
  padding: 12px 16px 12px 42px;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
}

.input-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.cliente-activo {
  background: #e7f3ff !important;
  border-color: #007bff !important;
  color: #0056b3 !important;
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
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-icon-clean:hover {
  background: #fee;
}

.btn-nuevo {
  background: #0f172a;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn-nuevo:hover {
  background: #1e293b;
  transform: translateY(-1px);
}

.select-modern {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
  cursor: pointer;
}

.select-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

/* Sugerencias */
.lista-sugerencias {
  position: absolute;
  background: white;
  border: 2px solid #e1e5e9;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  list-style: none;
  padding: 8px;
}

.item-sugerencia {
  padding: 12px;
  display: flex;
  gap: 12px;
  align-items: center;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.item-sugerencia:hover {
  background: #f8f9fa;
}

.avatar-mini {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.sugerencia-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sugerencia-info strong {
  color: #1a1a1a;
  font-size: 0.95em;
}

.sugerencia-info small {
  color: #6c757d;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 4px;
}

.msg-error {
  color: #dc3545;
  font-size: 0.85em;
  margin-top: 8px;
  padding: 8px 12px;
  background: #fee;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Chips de Categorías */
.grid-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip-modern {
  background: #fff;
  border: 2px solid #e1e5e9;
  padding: 10px 18px;
  border-radius: 50px;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9em;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chip-modern:hover {
  border-color: #007bff;
  color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
}

.chip-active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-color: #007bff;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

/* Servicios */
.grid-servicios {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.card-servicio {
  background: #fff;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.card-servicio:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.15);
}

.servicio-active {
  border-color: #007bff;
  background: #e7f3ff;
}

.servicio-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s;
}

.servicio-active .servicio-check {
  opacity: 1;
}

.servicio-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.servicio-nombre {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 1em;
  line-height: 1.3;
  padding-right: 30px;
}

.servicio-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.servicio-precio {
  color: #28a745;
  font-weight: 700;
  font-size: 1.1em;
  display: flex;
  align-items: center;
  gap: 4px;
}

.servicio-duracion {
  color: #6c757d;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Calendario */
.calendar-wrapper {
  background: linear-gradient(135deg, #f8f9fa, #f1f3f4);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid #e1e5e9;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.mes-titulo {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 1.1em;
  text-transform: capitalize;
}

.btn-nav-cal {
  background: transparent;
  border: none;
  color: #6c757d;
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-nav-cal:hover {
  background: #f8f9fa;
  color: #007bff;
}

.calendar-days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-size: 0.8em;
  font-weight: 700;
  color: #6c757d;
  margin-bottom: 12px;
  padding: 0 4px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.day-btn {
  aspect-ratio: 1;
  border-radius: 10px;
  border: 2px solid transparent;
  background: white;
  color: #1a1a1a;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  font-size: 0.95em;
}

.day-btn:hover:not(:disabled) {
  border-color: #007bff;
  background: #e7f3ff;
  transform: scale(1.05);
}

.day-selected {
  background: linear-gradient(135deg, #007bff, #0056b3) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
  border: none !important;
}

.day-disabled {
  background: #f1f3f4;
  color: #3b3b3b;
  cursor: not-allowed;
  opacity: 0.5;
}

.day-today {
  border-color: #ffc107;
  font-weight: 700;
}

.badge-today {
  position: absolute;
  bottom: 2px;
  font-size: 0.5em;
  font-weight: 800;
  color: #ffc107;
  letter-spacing: 0.5px;
}

.day-selected .badge-today {
  color: rgba(255, 255, 255, 0.8);
}

.calendar-footer {
  margin-top: 16px;
  text-align: center;
  color: #6c757d;
  font-size: 0.85em;
  padding: 10px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* Horarios */
.loading-spinner {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.spinner-icon {
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
  color: #007bff;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.grid-horarios-mejorado {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.hora-card-mejorada {
  border-radius: 12px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.hora-content-mejorada {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hora-disponible-mejorada .hora-content-mejorada {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border: 2px solid #28a745;
}

.hora-disponible-mejorada .hora-content-mejorada:hover {
  background: linear-gradient(135deg, #c3e6cb, #b1dfbb);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.hora-selected-mejorada .hora-content-mejorada {
  background: linear-gradient(135deg, #28a745, #20c997);
  border-color: #1e7e34;
}

.hora-ocupada-mejorada .hora-content-mejorada {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border: 2px solid #ffc107;
  cursor: default;
}

.hora-info-mejorada {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hora-icon-mejorada {
  flex-shrink: 0;
}

.hora-texto-mejorada {
  font-size: 1.3em;
  font-weight: 700;
  color: #155724;
}

.hora-ocupada-mejorada .hora-texto-mejorada {
  color: #856404;
}

.hora-selected-mejorada .hora-texto-mejorada {
  color: white;
}

.hora-estado-mejorada {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85em;
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 6px;
  align-self: flex-start;
}

.hora-estado-mejorada.disponible {
  background: rgba(40, 167, 69, 0.15);
  color: #155724;
}

.hora-estado-mejorada.ocupado {
  background: rgba(255, 193, 7, 0.15);
  color: #856404;
}

.hora-selected-mejorada .hora-estado-mejorada {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.campanita-icon {
  color: #ffc107;
  animation: ring 2s infinite;
}

@keyframes ring {
  0%, 100% { transform: rotate(0deg); }
  10%, 30%, 50%, 70%, 90% { transform: rotate(-10deg); }
  20%, 40%, 60%, 80% { transform: rotate(10deg); }
}

/* Resumen y Pago */
.resumen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  color: #1a1a1a;
}

.resumen-item span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6c757d;
}

.resumen-item strong {
  color: #1a1a1a;
  font-size: 1.1em;
}

.resumen-item.total {
  border-top: 2px solid #dee2e6;
  margin-top: 10px;
  padding-top: 15px;
  font-size: 1.2em;
  font-weight: 700;
}

.pago-section {
  margin-bottom: 20px;
}

.pago-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-top: 10px;
}

.radio-box {
  border: 2px solid #e1e5e9;
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s ease;
  background: white;
}

.radio-box:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.radio-active {
  border-color: #007bff;
  background: #e7f3ff;
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
  color: #6c757d;
  font-size: 0.9em;
}

.radio-content strong {
  color: #1a1a1a;
  font-size: 1.3em;
}

.radio-active .radio-content span {
  color: #007bff;
}

.pago-detalles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

/* Botón Final */
.btn-confirmar-premium {
  width: 100%;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  font-size: 1.1em;
  padding: 18px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 25px;
  font-weight: 700;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.btn-confirmar-premium:hover:not(:disabled):not(.btn-processing) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, #0056b3, #004085);
}

.btn-confirmar-premium:disabled,
.btn-confirmar-premium.btn-processing {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-spinner {
  animation: spin 1s linear infinite;
}

/* Toast */
.toast-message {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 16px 24px;
  border-radius: 12px;
  font-weight: 600;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 400px;
}

.toast-message.success {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.toast-message.error {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

/* Estados Vacíos */
.no-resultados {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.no-resultados-icon {
  margin-bottom: 15px;
  opacity: 0.5;
  color: #6c757d;
}

.no-resultados p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: #1a1a1a;
  font-weight: 600;
}

.no-resultados small {
  font-size: 0.9em;
  color: #6c757d;
}

/* Animaciones */
.slide-in {
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .turno-container {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-section h2 {
    font-size: 1.5em;
  }
  
  .row-search {
    flex-direction: column;
  }
  
  .grid-servicios {
    grid-template-columns: 1fr;
  }
  
  .calendar-grid {
    gap: 4px;
  }
  
  .day-btn {
    font-size: 0.85em;
  }
  
  .grid-horarios-mejorado {
    grid-template-columns: 1fr;
  }
  
  .pago-options {
    grid-template-columns: 1fr;
  }
  
  .pago-detalles {
    grid-template-columns: 1fr;
  }
  
  .toast-message {
    right: 15px;
    left: 15px;
    bottom: 15px;
  }
}
</style>