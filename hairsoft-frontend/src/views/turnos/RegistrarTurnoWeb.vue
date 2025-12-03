<template>
  <!-- FONDO DEGRADADO -->
  <div class="page-background">
    <!-- TARJETA BLANCA QUE ENVUELVE TODO -->
    <div class="main-card-container">
      <div class="turno-container">
        <div class="header-section">
          <h2>
            <Calendar class="header-icon" />
            Reservar Turno Online
          </h2>
          <button @click="volverAlListado" class="btn-back">
            <ArrowLeft :size="18" />
            Volver al Listado
          </button>
        </div>

        <!-- Alerta de Descuento -->
        <transition name="slide">
          <div v-if="descuentoAplicado > 0" class="card-modern cupon-alerta">
            <div class="card-header">
              <div class="card-icon">
                <Gift :size="20" />
              </div>
              <h3>🎉 ¡Descuento Activado!</h3>
            </div>
            <p>Tenés un <strong>{{ descuentoAplicado }}% OFF</strong> por reactivación. {{ mensajePromo }}</p>
          </div>
        </transition>

        <!-- Datos del Usuario -->
        <div class="card-modern">
          <div class="card-header">
            <div class="card-icon">
              <User :size="20" />
            </div>
            <h3>Tus Datos</h3>
          </div>
          
          <div class="cliente-info-card">
            <div class="cliente-datos">
              <p><strong>Cliente:</strong> {{ usuario.nombre }} {{ usuario.apellido }}</p>
              <p><strong>DNI:</strong> {{ usuario.dni || 'Cargando...' }}</p>
              <p><strong>Teléfono:</strong> {{ usuario.telefono || 'Cargando...' }}</p>
              <p v-if="usuario.turnosCount > 0"><strong>Turnos reservados:</strong> {{ usuario.turnosCount }}</p>
            </div>
          </div>
        </div>

        <!-- Selección de Peluquero -->
        <div class="card-modern slide-in">
          <div class="card-header">
            <div class="card-icon">
              <UserCheck :size="20" />
            </div>
            <h3>Elegir Peluquero</h3>
          </div>
          
          <div class="input-group">
            <select v-model="form.peluquero" @change="onPeluqueroSeleccionado" class="select-modern">
              <option value="">-- Seleccionar peluquero! --</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                {{ p.nombre }} {{ p.apellido }}
              </option>
            </select>
          </div>
        </div>

        <!-- Categorías -->
        <div v-if="form.peluquero" class="card-modern slide-in">
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
          
          <div class="busqueda-servicios">
            <div class="search-wrapper">
              <Search class="search-icon" :size="18" />
              <input
                type="text"
                v-model="busquedaServicio"
                placeholder="Buscar servicio..."
                class="input-modern"
              />
            </div>
          </div>
          
          <div v-if="serviciosFiltrados.length === 0" class="no-resultados">
            <Inbox class="no-resultados-icon" :size="48" />
            <p v-if="busquedaServicio">No se encontraron servicios con "{{ busquedaServicio }}"</p>
            <p v-else>No hay servicios en las categorías seleccionadas</p>
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
                    {{ servicio.duracion || servicio.duracion_minutos || 60 }}m
                  </span>
                </div>
                <span class="servicio-categoria">{{ getCategoriaNombre(servicio.categoria) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Calendario -->
        <div v-if="form.servicios_ids.length > 0" class="card-modern slide-in">
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
          </div>
        </div>

        <!-- Horarios -->
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
          
          <div v-else-if="horariosDisponibles.length === 0" class="no-resultados">
            <Clock class="no-resultados-icon" :size="48" />
            <p>No hay horarios disponibles</p>
            <small>Intenta seleccionar otro día</small>
          </div>
          
          <div v-else class="grid-horarios-mejorado">
            <div
              v-for="hora in horariosDisponibles"
              :key="hora"
              class="hora-card-mejorada"
              :class="{
                'hora-selected-mejorada': form.hora === hora,
                'hora-disponible-mejorada': true,
                'hora-ocupada-mejorada': false
              }"
            >
              <div 
                class="hora-content-mejorada"
                @click="seleccionarHora(hora)"
              >
                <div class="hora-info-mejorada">
                  <Clock :size="16" class="hora-icon-mejorada" />
                  <span class="hora-texto-mejorada">{{ hora }}</span>
                </div>
                <div class="hora-estado-mejorada disponible">
                  <span>Disponible</span>
                </div>
              </div>
            </div>

            <!-- Horarios ocupados -->
            <div
              v-for="hora in horariosOcupadosParaMostrar"
              :key="'ocupado-'+hora"
              class="hora-card-mejorada hora-ocupada-mejorada"
            >
              <div class="hora-content-mejorada ocupada">
                <div class="hora-info-mejorada">
                  <Clock :size="16" class="hora-icon-mejorada" />
                  <span class="hora-texto-mejorada">{{ hora }}</span>
                  <span class="hora-duracion-badge-ocupado">
                    Ocupado
                  </span>
                </div>

                <button 
                  class="btn-avisar-liberado-mejorada"
                  :disabled="estaInteresRegistrado(hora)"
                  @click="registrarInteresHorario(hora)"
                >
                  <Bell :size="14" />
                  {{ estaInteresRegistrado(hora) ? '✅ En lista' : 'Avísame' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Opciones de Pago -->
        <div v-if="form.hora" class="card-modern slide-in">
          <div class="card-header">
            <div class="card-icon">
              <CreditCard :size="20" />
            </div>
            <h3>Opciones de Pago</h3>
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
                  <small>Resto: ${{ (calcularTotalConDescuento() * 0.5).toFixed(2) }} en el local</small>
                </div>
              </label>
              <label class="radio-box" :class="{ 'radio-active': form.tipo_pago === 'TOTAL' }">
                <input type="radio" v-model="form.tipo_pago" value="TOTAL" class="hidden-radio">
                <div class="radio-content">
                  <span>Pago Total (100%)</span>
                  <strong>${{ calcularTotalConDescuento() }}</strong>
                  <small>Pago completo online</small>
                </div>
              </label>
            </div>
          </div>

          <div v-if="form.tipo_pago" class="pago-detalles">
            <div class="input-group">
              <label class="label-modern">
                <Banknote :size="16" />
                Medio de Pago
              </label>
              <div class="medio-pago-box">
                <div class="medio-pago-content">
                  <span class="medio-icon">💳</span>
                  <span class="medio-text">Mercado Pago</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Confirmación Final -->
        <div v-if="formularioValido" class="card-modern slide-in resumen-final">
          <div class="card-header">
            <div class="card-icon">
              <CheckCircle2 :size="20" />
            </div>
            <h3>Confirmar Reserva</h3>
          </div>

          <div class="resumen-detalles">
            <div class="resumen-item">
              <span><CalendarDays :size="14" /> Fecha:</span>
              <span>{{ formatoFechaLegible(form.fecha) }} a las {{ form.hora }}</span>
            </div>
            <div class="resumen-item">
              <span><UserCheck :size="14" /> Profesional:</span>
              <span>{{ getPeluqueroNombre() }}</span>
            </div>
            <div class="resumen-item">
              <span><Scissors :size="14" /> Servicios:</span>
              <span>{{ getServiciosNombres() }}</span>
            </div>
            <div class="resumen-item">
              <span><Clock :size="14" /> Duración total:</span>
              <span>{{ calcularDuracionTotalServicios() }} minutos</span>
            </div>
            
            <div class="resumen-item total">
              <span><Wallet :size="16" /> Total a pagar ahora:</span>
              <span class="monto-final-pago">${{ montoAPagarAhora() }}</span>
            </div>
          </div>
          
          <button
            @click="reservarTurno" 
            class="btn-confirmar-premium"
            :disabled="cargando"
          >
            <span class="btn-content">
              <CreditCard :size="20" />
              {{ cargando ? '🔄 Procesando...' : `Pagar $${montoAPagarAhora()} con Mercado Pago` }}
            </span>
          </button>
          
          <p class="info-pago-final">
            <CheckCircle2 :size="14" />
            Tu turno quedará <strong>confirmado</strong> tras el pago exitoso.
          </p>
        </div>

        <!-- Modal de Interés -->
        <div v-if="mostrarModalInteres" class="modal-overlay">
          <div class="modal-content">
            <div class="modal-header">
              <h3>🔔 Confirmar Interés</h3>
              <button class="modal-close-btn" @click="cancelarRegistroInteres">
                <X :size="20" />
              </button>
            </div>
            <div class="modal-body">
              <div class="info-interes-card">
                <div class="info-details">
                  <p><strong>📅 Fecha:</strong> {{ formatoFechaLegible(form.fecha) }}</p>
                  <p><strong>⏰ Horario:</strong> {{ horarioSeleccionadoInteres }}</p>
                  <p><strong>👨‍💼 Peluquero:</strong> {{ getPeluqueroNombre() }}</p>
                  <p><strong>✂️ Servicios:</strong> {{ getServiciosNombres() }}</p>
                  <p><strong>⏱️ Duración:</strong> {{ calcularDuracionTotalServicios() }} minutos</p>
                </div>
                <div class="beneficio-descuento">
                  <strong>¡Beneficio exclusivo!</strong> 
                  <p>   </p>
                  <strong>15% de descuento</strong> y 1 hora para confirmar.
                </div>
              </div>
              <div class="modal-actions">
                <button @click="confirmarRegistroInteres" class="btn-confirmar-interes" :disabled="registrandoInteres">
                  {{ registrandoInteres ? 'Registrando...' : '✅ Sí, avisarme' }}
                </button>
                <button @click="cancelarRegistroInteres" class="btn-cancelar-interes">❌ Cancelar</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Toast Message -->
        <transition name="fade">
          <div v-if="mensaje" class="toast-message" :class="mensajeTipo">
            <component :is="mensajeTipo === 'success' ? CheckCircle : AlertCircle" :size="18" />
            {{ mensaje }}
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Calendar, ArrowLeft, User, UserCheck, FolderOpen, Tag, 
  Scissors, Check, DollarSign, Clock, CalendarDays, 
  ChevronLeft, ChevronRight, Info, Loader2, Receipt, 
  Wallet, CreditCard, Banknote, CheckCircle2, CheckCircle, 
  Inbox, Search, Gift, Bell, X, FileText, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const API_URL = "http://localhost:8000/usuarios/api"
// Estados
const form = ref({
  peluquero: null,
  servicios_ids: [],
  hora: "",
  fecha: "",
  tipo_pago: null,
  medio_pago: "MERCADO_PAGO",
  canal: "WEB"
})

const usuario = ref({ 
  id: null, 
  nombre: 'Cargando', 
  apellido: '', 
  dni: 'Cargando...', 
  telefono: 'Cargando...', 
  turnosCount: 0 
})

const peluqueros = ref([])
const servicios = ref([])
const categorias = ref([])
const turnosOcupados = ref([])
const categoriasSeleccionadas = ref([])
const busquedaServicio = ref("")
const interesesRegistrados = ref([])
const cargando = ref(false)
const cargandoHorarios = ref(false)
const mostrarModalInteres = ref(false)
const horarioSeleccionadoInteres = ref(null)
const registrandoInteres = ref(false)
const currentDate = ref(new Date())
const mensaje = ref("")
const mensajeTipo = ref("success")

// Cupón de descuento
const cuponCodigo = ref(null)
const descuentoAplicado = ref(0)
const mensajePromo = ref("")

// Computed
const formularioValido = computed(() => {
  return form.value.peluquero && 
         form.value.servicios_ids.length > 0 &&
         form.value.fecha && 
         form.value.hora &&
         form.value.tipo_pago
})

const serviciosFiltrados = computed(() => {
  let filtrados = servicios.value
  if (categoriasSeleccionadas.value.length > 0) {
    const nombresCats = categorias.value
      .filter(c => categoriasSeleccionadas.value.includes(c.id))
      .map(c => c.nombre)
    filtrados = filtrados.filter(s => nombresCats.includes(s.categoria))
  }
  if (busquedaServicio.value) {
    const termino = busquedaServicio.value.toLowerCase()
    filtrados = filtrados.filter(s => s.nombre.toLowerCase().includes(termino))
  }
  return filtrados
})

// Computed para calendario
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

// 🎯 HORARIOS DE 20 EN 20 MINUTOS EXACTAMENTE
const horariosGenerados = computed(() => {
  const horariosBase = []
  const bloques = [
    { inicio: 8, fin: 12 },    // Mañana: 8:00 a 12:00
    { inicio: 15, fin: 20 }    // Tarde: 15:00 a 20:00
  ]

  const ahora = new Date()
  const horaActual = ahora.getHours()
  const minutoActual = ahora.getMinutes()

  const hoy = new Date()
  const hoyFormateado = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
  const esHoy = form.value.fecha === hoyFormateado

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

    // ✨ Agregar el horario exacto de cierre: fin:00 (ej: 12:00 o 20:00)
    const cierreStr = `${String(b.fin).padStart(2, '0')}:00`
    horariosBase.push(cierreStr)
  })

  return horariosBase
})

// 🔥 NUEVAS FUNCIONES PARA BLOQUEAR POR DURACIÓN

// 1. Calcular duración total de los servicios seleccionados
const calcularDuracionTotalServicios = () => {
  return form.value.servicios_ids.reduce((total, id) => {
    const servicio = servicios.value.find(s => s.id === id)
    return total + (servicio?.duracion || servicio?.duracion_minutos || 60) // 60 min por defecto
  }, 0)
}

// 2. Obtener duración de un servicio específico
const getServicioDuracion = (id) => {
  const servicio = servicios.value.find(s => s.id === id)
  return servicio?.duracion || servicio?.duracion_minutos || 60
}

// 3. Convertir "HH:MM" a minutos totales del día
const horaAMinutos = (horaStr) => {
  if (!horaStr) return 0
  const [horas, minutos] = horaStr.split(':').map(Number)
  return horas * 60 + minutos
}

// 4. Calcular duración de un turno existente
const calcularDuracionTurno = (turno) => {
  // Si el turno tiene información de servicios, sumar sus duraciones
  if (turno.servicios && turno.servicios.length > 0) {
    return turno.servicios.reduce((total, servicioId) => {
      const servicio = servicios.value.find(s => s.id === servicioId)
      return total + (servicio?.duracion || servicio?.duracion_minutos || 60)
    }, 0)
  }
  
  // Si no, usar duración por defecto
  return turno.duracion_minutos || 60
}

// 5. Función principal corregida que verifica rangos de tiempo
const estaHorarioDisponible = (horario) => {
  if (!form.value.fecha || !form.value.peluquero) return true
  
  const duracionTurnoSolicitado = calcularDuracionTotalServicios()
  const horarioInicioMinutos = horaAMinutos(horario)
  const horarioFinMinutos = horarioInicioMinutos + duracionTurnoSolicitado
  
  // Verificar que el turno no se pase del horario de cierre (20:00)
  const cierreMinutos = 20 * 60 // 20:00 = 1200 minutos
  if (horarioFinMinutos > cierreMinutos) {
    return false
  }
  
  // Verificar si algún turno ocupado se solapa con nuestro horario deseado
  const turnoOcupado = turnosOcupados.value.find(turno => {
    // Solo verificar turnos del mismo peluquero y fecha
    if (turno.peluquero_id != form.value.peluquero || turno.fecha !== form.value.fecha) {
      return false
    }
    
    // Calcular duración del turno ocupado
    const duracionOcupado = calcularDuracionTurno(turno)
    const turnoInicioMinutos = horaAMinutos(turno.hora)
    const turnoFinMinutos = turnoInicioMinutos + duracionOcupado
    
    // Verificar solapamiento
    const solapa = 
      // Caso 1: Nuestro turno comienza durante el turno ocupado
      (horarioInicioMinutos >= turnoInicioMinutos && horarioInicioMinutos < turnoFinMinutos) ||
      // Caso 2: Nuestro turno termina durante el turno ocupado
      (horarioFinMinutos > turnoInicioMinutos && horarioFinMinutos <= turnoFinMinutos) ||
      // Caso 3: Nuestro turno contiene completamente al turno ocupado
      (horarioInicioMinutos <= turnoInicioMinutos && horarioFinMinutos >= turnoFinMinutos)
    
    return solapa
  })
  
  return !turnoOcupado
}

// 6. Horarios disponibles que caben con la duración del servicio
const horariosDisponibles = computed(() => {
  return horariosGenerados.value.filter(horario => {
    return estaHorarioDisponible(horario)
  })
})

// 7. Horarios ocupados para mostrar en la interfaz
const horariosOcupadosParaMostrar = computed(() => {
  return horariosGenerados.value.filter(horario => {
    return !estaHorarioDisponible(horario)
  })
})

// Métodos
const cargarDatosIniciales = async () => {
  await Promise.all([
    cargarUsuarioLogueado(), // ARREGLADO para traer todos los datos
    cargarPeluqueros(),
    cargarServicios(),
    cargarCategorias(),
    cargarTurnosOcupados()
  ])
  await validarCuponURL()
  await cargarInteresesUsuario()
}

const validarCuponURL = async () => {
  let codigo = route.query.cup
  
  if (!codigo) {
    const urlParams = new URLSearchParams(window.location.search)
    codigo = urlParams.get('cup')
  }

  if (!codigo) return

  try {
    const res = await axios.get(`http://localhost:8000/usuarios/api/promociones/validar/${codigo}/`)
    
    if (res.data.valido) {
      cuponCodigo.value = codigo
      descuentoAplicado.value = parseFloat(res.data.descuento)
      mensajePromo.value = res.data.mensaje
      
      Swal.fire({
        title: '¡Descuento Activado! 🎉',
        text: res.data.mensaje,
        icon: 'success',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 4000
      })
    }
  } catch (e) {
    console.error("Error validando cupón:", e)
  }
}

// En RegistrarTurnoWeb.vue

const cargarUsuarioLogueado = async () => {
  try {
    const storedUserId = localStorage.getItem('user_id')
    const token = localStorage.getItem('token')
    
    // Configuración segura de headers
    const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {}
    
    if (storedUserId) {
      console.log("🔍 Buscando datos del usuario ID:", storedUserId)
      
      // 1. Llamada al backend (ahora devuelve DNI y Telefono seguro)
      const res = await axios.get(`${API_URL}/usuarios/${storedUserId}/`, config)
      const data = res.data
      
      console.log("✅ Datos recibidos:", data) // Mirá la consola para ver si llegan

      // 2. Asignación directa (sin lógica rara)
      usuario.value = {
        id: data.id,
        nombre: data.nombre || 'Cliente',
        apellido: data.apellido || '',
        dni: data.dni || 'No registrado',
        telefono: data.telefono || 'No registrado',
        turnosCount: 0
      }
      
      // 3. Cargar estadísticas (Opcional, si falla no rompe nada)
      try {
        const statsRes = await axios.get(`${API_URL}/turnos/cliente/${storedUserId}/estadisticas/`, config)
        usuario.value.turnosCount = statsRes.data.total_turnos || 0
      } catch (e) {
        console.warn("No se pudieron cargar estadísticas (no es crítico)")
      }

    } else {
      usuario.value = { 
        nombre: 'Invitado', apellido: '', dni: '---', telefono: '---', turnosCount: 0, id: null 
      }
    }
  } catch (err) {
    console.error("❌ Error cargando usuario:", err)
    // Mostramos error en la interfaz para que no quede "Cargando"
    usuario.value = { 
      nombre: 'Error al cargar', 
      apellido: '', 
      dni: 'Error de conexión', 
      telefono: 'Intente recargar', 
      turnosCount: 0, 
      id: null 
    }
  }
}

const cargarPeluqueros = async () => {
  try {
    const res = await axios.get("http://localhost:8000/usuarios/api/peluqueros/")
    peluqueros.value = res.data.map(p => ({ ...p, apellido: p.apellido || '' }))
  } catch (err) { peluqueros.value = [] }
}

const cargarServicios = async () => {
  try {
    const res = await axios.get("http://localhost:8000/usuarios/api/servicios/")
    servicios.value = res.data
  } catch (err) { console.error(err) }
}

const cargarCategorias = async () => {
  try {
    const res = await axios.get("http://localhost:8000/usuarios/api/categorias/servicios/")
    categorias.value = res.data
  } catch (err) { console.error(err) }
}

const cargarTurnosOcupados = async (fecha = null) => {
  try {
    let url = "http://localhost:8000/usuarios/api/turnos/?estado__in=RESERVADO,CONFIRMADO&expand=servicios"
    if (fecha) url += `&fecha=${fecha}`
    
    const res = await axios.get(url)
    turnosOcupados.value = res.data.results || res.data
    
    // Si los turnos vienen sin servicios, cargar servicios por separado
    if (turnosOcupados.value.length > 0 && !turnosOcupados.value[0].servicios) {
      // Intentar obtener servicios de otra manera
      for (const turno of turnosOcupados.value) {
        try {
          const turnoDetalle = await axios.get(`http://localhost:8000/usuarios/api/turnos/${turno.id}/`)
          turno.servicios = turnoDetalle.data.servicios_ids || []
        } catch { turno.servicios = [] }
      }
    }
  } catch (err) { 
    console.error("Error cargando turnos ocupados:", err)
    turnosOcupados.value = [] 
  }
}

const cargarInteresesUsuario = async () => {
  try {
    if (usuario.value.id) {
      const res = await axios.get(`http://localhost:8000/usuarios/api/turnos/mis-intereses/`, {
        headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
      })
      interesesRegistrados.value = res.data
    }
  } catch (err) { console.error("Error intereses:", err) }
}

// Cálculos con descuento
const calcularTotalOriginal = () => {
  return form.value.servicios_ids.reduce((total, id) => 
    total + parseFloat(getServicioPrecio(id) || 0), 0
  ).toFixed(2)
}

const calcularMontoDescuento = () => {
  const total = parseFloat(calcularTotalOriginal())
  if (descuentoAplicado.value > 0) {
    return (total * (descuentoAplicado.value / 100)).toFixed(2)
  }
  return '0.00'
}

const calcularTotalConDescuento = () => {
  const total = parseFloat(calcularTotalOriginal())
  if (descuentoAplicado.value > 0) {
    return (total * (1 - descuentoAplicado.value / 100)).toFixed(2)
  }
  return total.toFixed(2)
}

const calcularSena = () => {
  const totalConDesc = parseFloat(calcularTotalConDescuento())
  return (totalConDesc * 0.5).toFixed(2)
}

const montoAPagarAhora = () => {
  const total = parseFloat(calcularTotalConDescuento())
  if (form.value.tipo_pago === 'TOTAL') return total.toFixed(2)
  if (form.value.tipo_pago === 'SENA_50') return (total * 0.5).toFixed(2)
  return '0.00'
}

// Métodos de UI
const toggleCategoria = (categoriaId) => {
  const index = categoriasSeleccionadas.value.indexOf(categoriaId)
  if (index === -1) categoriasSeleccionadas.value.push(categoriaId)
  else categoriasSeleccionadas.value.splice(index, 1)
}

const toggleServicio = (servicio) => {
  const index = form.value.servicios_ids.indexOf(servicio.id)
  if (index === -1) form.value.servicios_ids.push(servicio.id)
  else form.value.servicios_ids.splice(index, 1)
}

const getServicioNombre = (id) => servicios.value.find(x => x.id === id)?.nombre || ''
const getServiciosNombres = () => form.value.servicios_ids.map(id => getServicioNombre(id)).join(', ')
const getServicioPrecio = (id) => servicios.value.find(x => x.id === id)?.precio || 0
const getCategoriaNombre = (categoria) => categoria || 'General'

const formatoFechaLegible = (fechaStr) => {
  if (!fechaStr) return ''
  const [year, month, day] = fechaStr.split('-')
  const fecha = new Date(year, month - 1, day)
  return fecha.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
}

const onPeluqueroSeleccionado = () => {
  form.value.fecha = ""
  form.value.hora = ""
  form.value.tipo_pago = null
  cargarTurnosOcupados(form.value.fecha)
}

// Calendario
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
  
  cargarTurnosOcupados(form.value.fecha)
}

const seleccionarHora = (hora) => {
  form.value.hora = hora
}

const estaInteresRegistrado = (horario) => {
  return interesesRegistrados.value.some(interes => 
    interes.fecha_deseada === form.value.fecha &&
    interes.hora_deseada === horario &&
    interes.peluquero_id == form.value.peluquero
  )
}

const getPeluqueroNombre = () => {
  const p = peluqueros.value.find(p => p.id == form.value.peluquero)
  return p ? `${p.nombre} ${p.apellido}` : ''
}

const registrarInteresHorario = (horario) => {
  if (estaHorarioDisponible(horario)) { 
    Swal.fire('Atención', 'Este horario está disponible.', 'info')
    return 
  }
  horarioSeleccionadoInteres.value = horario
  mostrarModalInteres.value = true
}

const cancelarRegistroInteres = () => { 
  mostrarModalInteres.value = false
  horarioSeleccionadoInteres.value = null
}

const confirmarRegistroInteres = async () => {
  if (!usuario.value.id) { 
    Swal.fire('Error', 'Debes iniciar sesión.', 'error')
    return 
  }
  registrandoInteres.value = true
  try {
    const token = localStorage.getItem('token')
    const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {}
    const payload = { 
      cliente_id: usuario.value.id, 
      servicio_id: form.value.servicios_ids[0], 
      peluquero_id: form.value.peluquero, 
      fecha_deseada: form.value.fecha, 
      hora_deseada: horarioSeleccionadoInteres.value 
    }
    const res = await axios.post("http://localhost:8000/usuarios/api/turnos/registrar-interes/", payload, config)
    if (res.data.success) {
      mostrarModalInteres.value = false
      await cargarInteresesUsuario()
      Swal.fire({ 
        icon: 'success', 
        title: '¡Listo!', 
        text: 'Te avisaremos por WhatsApp.', 
        timer: 3000, 
        showConfirmButton: false 
      })
    } else {
      Swal.fire('Atención', res.data.error || "Ya registrado.", 'warning')
    }
  } catch (err) { 
    Swal.fire('Error', err.response?.data?.error || "Error al conectar.", 'error')
  } finally { 
    registrandoInteres.value = false 
  }
}

const reservarTurno = async () => {
  // 1. Validación
  if (!formularioValido.value) { 
    Swal.fire('Faltan datos', 'Completa todos los campos.', 'warning')
    return 
  }

  cargando.value = true
  
  const payload = {
    peluquero_id: form.value.peluquero,
    servicios_ids: form.value.servicios_ids,
    fecha: form.value.fecha,
    hora: form.value.hora,
    canal: 'WEB',
    tipo_pago: form.value.tipo_pago,
    medio_pago: form.value.medio_pago,
    cup_codigo: cuponCodigo.value
  }

  console.log("🚀 Enviando reserva:", payload)

  try {
    const token = localStorage.getItem('token')
    const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {}

    const res = await axios.post("http://localhost:8000/usuarios/api/turnos/crear/", payload, config)
    const data = res.data
    
    cargando.value = false

    if (data.status === 'ok') {
      
      // CASO A: PAGO CON MERCADO PAGO
      if (data.procesar_pago === true && data.mp_data && data.mp_data.init_point) {
        
        // Mostramos alerta de éxito. El clic en "Pagar Ahora" abre la pestaña nueva.
        // Esto evita que Chrome bloquee la ventana emergente.
        Swal.fire({ 
          icon: 'success', 
          title: '¡Reserva Creada!', 
          text: 'Haz clic para completar el pago en Mercado Pago.', 
          confirmButtonText: 'PAGAR AHORA',
          allowOutsideClick: false,
          allowEscapeKey: false
        }).then((result) => {
          if (result.isConfirmed) {
            // 1. Abrir MP en NUEVA PESTAÑA
            window.open(data.mp_data.init_point, '_blank')
            
            // 2. En TU sistema, ir al listado (así no tienes que volver atrás)
            router.push('/turnos')
          }
        })
      
      } 
      // CASO B: SIN PAGO (Efectivo o error de link)
      else {
        if (form.value.medio_pago === 'MERCADO_PAGO') {
            Swal.fire('Atención', 'Reserva creada pero no se generó el link de pago. Revisa tus turnos.', 'warning').then(() => router.push('/turnos'))
        } else {
            Swal.fire({ 
              icon: 'success', 
              title: '¡Turno Reservado!', 
              text: 'Te esperamos en el local.', 
              timer: 2000, 
              showConfirmButton: false 
            }).then(() => { 
              router.push('/turnos')
            })
        }
      }

    } else {
      Swal.fire('Error', data.message || "No se pudo reservar.", 'error')
    }

  } catch (err) {
    cargando.value = false
    console.error(err)
    const msg = err.response?.data?.message || 'Error de conexión'
    Swal.fire('Error', msg, 'error')
  }
}

const volverAlListado = () => {
  router.push('/turnos')
}

onMounted(() => {
  cargarDatosIniciales()
  setTimeout(() => {
    validarCuponURL()
  }, 500)
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



/* ============================================
   TURNO CONTAINER (tu estructura original)
   ============================================ */
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

.badge-count {
  background: #10b981;
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* Cupón alerta */
.cupon-alerta {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 2px solid #f59e0b;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}

.cupon-alerta .card-header {
  border-bottom-color: rgba(245, 158, 11, 0.3);
}

/* Datos del cliente */
.cliente-info-card {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  padding: 25px;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  position: relative;
}

.cliente-datos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.cliente-datos p {
  margin: 0;
  color: #4b5563;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cliente-datos strong {
  color: #1f2937;
  font-weight: 700;
  min-width: 140px;
  display: inline-block;
}

/* Inputs y Selects */
.input-modern, .select-modern {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
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

.select-modern {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 20px;
  padding-right: 50px;
  cursor: pointer;
}

/* Busqueda servicios */
.busqueda-servicios {
  margin-bottom: 24px;
}

.search-wrapper {
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
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); 
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

.servicio-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.servicio-nombre { 
  font-weight: 700; 
  color: #1f2937; 
  display: block;
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

.servicio-categoria {
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  align-self: flex-start;
}

/* No resultados */
.no-resultados {
  text-align: center;
  padding: 50px 20px;
  color: #6b7280;
}

.no-resultados-icon {
  opacity: 0.4;
  margin-bottom: 15px;
  color: #9ca3af;
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

/* Horarios */
.grid-horarios-mejorado {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.hora-card-mejorada {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.hora-selected-mejorada {
  box-shadow: 0 0 0 4px #3b82f6;
  transform: scale(1.05);
}

.hora-content-mejorada {
  padding: 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.hora-content-mejorada:hover:not(.ocupada) {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.hora-info-mejorada {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.hora-icon-mejorada {
  color: #6b7280;
}

.hora-texto-mejorada {
  font-weight: 600;
  font-size: 1.1rem;
  color: #1f2937;
}

.hora-duracion-badge-ocupado {
  background: #fef2f2;
  color: #dc2626;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  margin-left: auto;
}

.hora-estado-mejorada {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  padding: 6px 12px;
  border-radius: 8px;
}

.hora-estado-mejorada.disponible {
  background: #f0fdf4;
  color: #059669;
}

.btn-avisar-liberado-mejorada {
  width: 100%;
  margin-top: 12px;
  padding: 8px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-avisar-liberado-mejorada:hover:not(:disabled) {
  background: linear-gradient(135deg, #d97706, #b45309);
  transform: translateY(-2px);
}

.btn-avisar-liberado-mejorada:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.7;
}

.ocupada {
  opacity: 0.8;
  cursor: not-allowed;
}

/* Loading */
.loading-spinner {
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

/* Pago */
.pago-section {
  margin-bottom: 25px;
}

.label-modern {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1f2937;
  font-size: 1rem;
}

.pago-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.radio-box {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
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

.radio-content small {
  color: #6b7280;
  font-size: 0.85rem;
}

.pago-detalles {
  margin-bottom: 25px;
}

.medio-pago-box {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  background: white;
}

.medio-pago-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.medio-icon {
  font-size: 1.5rem;
}

.medio-text {
  font-weight: 600;
  color: #1f2937;
}

/* Resumen final */
.resumen-final {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border: 2px solid #e2e8f0;
}

.resumen-detalles {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  border: 1px solid #e5e7eb;
}

.resumen-detalles .resumen-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.resumen-detalles .resumen-item:last-child {
  border-bottom: none;
}

.resumen-detalles .resumen-item.total {
  border-top: 2px solid #e5e7eb;
  padding-top: 15px;
  margin-top: 10px;
  font-size: 1.2rem;
  font-weight: 700;
}

.monto-final-pago {
  font-size: 1.4rem;
  color: #059669;
  font-weight: 700;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  position: relative;
  overflow: hidden;
}

.btn-confirmar-premium::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s;
}

.btn-confirmar-premium:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(5, 150, 105, 0.4);
}

.btn-confirmar-premium:hover::before {
  left: 100%;
}

.btn-confirmar-premium:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  opacity: 0.7;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-pago-final {
  text-align: center;
  color: #6b7280;
  margin-top: 16px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 24px;
  padding: 32px;
  max-width: 550px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.1);
  animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3rem;
}

.modal-close-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close-btn:hover {
  background: #e5e7eb;
}

.info-interes-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.info-details {
  display: flex;
  color: #1f2937;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.beneficio-descuento {
  background: linear-gradient(135deg, #6db0f8, #667ffb);
  border: 1px solid #ffffff;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  font-size: 0.9rem;
  color: white;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-confirmar-interes {
  flex: 1;
  padding: 14px;
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-confirmar-interes:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: translateY(-2px);
}

.btn-confirmar-interes:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-cancelar-interes {
  flex: 1;
  padding: 14px;
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancelar-interes:hover {
  background: #e5e7eb;
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
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  min-width: 300px;
  backdrop-filter: blur(10px);
  animation: slideInRight 0.3s ease;
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

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Animaciones */
.slide-enter-active, .slide-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.slide-enter-from, .slide-leave-to {
  transform: translateY(-30px);
  opacity: 0;
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

/* Responsive */
@media (max-width: 1024px) {
  .main-card-container {
    padding: 30px;
    margin: 20px;
  }
  
  .grid-servicios {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .grid-horarios-mejorado {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
  
  .grid-horarios-mejorado {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .pago-options {
    grid-template-columns: 1fr;
  }
  
  .cliente-datos {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    padding: 24px;
    width: 95%;
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
  
  .grid-horarios-mejorado {
    grid-template-columns: 1fr;
  }
  
  .toast-message {
    left: 15px;
    right: 15px;
    bottom: 15px;
    min-width: auto;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>