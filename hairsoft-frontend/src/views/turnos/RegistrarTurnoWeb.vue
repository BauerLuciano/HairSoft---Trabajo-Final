<template>
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
          <p><strong>Teléfono:</strong> {{ usuario.telefono || 'No registrado' }}</p>
          <p v-if="usuario.turnosCount > 0"><strong>Turnos reservados:</strong> {{ usuario.turnosCount }}</p>
        </div>
        <small class="info-pago">Tu información se enviará automáticamente al sistema.</small>
      </div>
    </div>

    <!-- Selección de Peluquero -->
    <div class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <UserCheck :size="20" />
        </div>
        <h3>Profesional</h3>
      </div>
      
      <div class="input-group">
        <select v-model="form.peluquero" @change="onPeluqueroSeleccionado" class="select-modern">
          <option value="">-- Seleccionar Profesional --</option>
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
                {{ servicio.duracion }}m
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

        <div class="calendar-footer">
          <Info :size="14" />
          Disponible: Hoy + 14 días (No Domingos)
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
            'hora-disponible-mejorada': estaHorarioDisponible(hora),
            'hora-ocupada-mejorada': !estaHorarioDisponible(hora)
          }"
        >
          <div 
            v-if="estaHorarioDisponible(hora)"
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

    <!-- Resumen del Turno -->
    <div v-if="form.hora" class="card-modern slide-in">
      <div class="card-header">
        <div class="card-icon">
          <Receipt :size="20" />
        </div>
        <h3>Resumen del Turno</h3>
      </div>

      <div class="resumen-grid">
        <div class="resumen-item" v-for="servicioId in form.servicios_ids" :key="servicioId">
          <div>
            <Scissors :size="16" /> {{ getServicioNombre(servicioId) }}
          </div>
          <span>${{ getServicioPrecio(servicioId) }}</span>
        </div>
        
        <div class="resumen-item subtotal" v-if="descuentoAplicado > 0">
          <div>
            <FileText :size="16" /> Subtotal
          </div>
          <span class="tachado">${{ calcularTotalOriginal() }}</span>
        </div>

        <div class="resumen-item descuento" v-if="descuentoAplicado > 0">
          <div>
            <Tag :size="16" /> Descuento ({{ descuentoAplicado }}%)
          </div>
          <span class="text-success">- ${{ calcularMontoDescuento() }}</span>
        </div>

        <div class="resumen-item total">
          <div>
            <Wallet :size="18" /> Total del servicio
          </div>
          <strong>${{ calcularTotalConDescuento() }}</strong>
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
            </div>
            <div class="beneficio-descuento">
              <span class="icono-descuento">🔥</span>
              <strong>¡Beneficio exclusivo!</strong> Si se libera, tendrás <strong>PRIORIDAD</strong>, <strong>15% de descuento</strong> y 1 hora para confirmar.
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
  apellido: '...', 
  dni: 'Cargando', 
  telefono: '', 
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
      for (let m = 0; m < 60; m += 20) { // ⏰ 20 EN 20 MINUTOS
        const horaStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
        
        // Si es hoy, filtrar horarios pasados
        if (esHoy) {
          if (h < horaActual) continue
          if (h === horaActual && m <= minutoActual) continue
        }
        
        horariosBase.push(horaStr)
      }
    }
  })
  return horariosBase
})

// Métodos
const cargarDatosIniciales = async () => {
  await Promise.all([
    cargarUsuarioLogueado(),
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

const cargarUsuarioLogueado = async () => {
  try {
    const storedUserId = localStorage.getItem('user_id')
    const token = localStorage.getItem('token')
    const config = token ? { headers: { 'Authorization': `Bearer ${token}` } } : {}
    
    if (storedUserId) {
      const res = await axios.get(`http://localhost:8000/usuarios/api/usuarios/${storedUserId}/`, config)
      usuario.value = res.data
      usuario.value.id = parseInt(storedUserId)
      try {
        const statsRes = await axios.get(`http://localhost:8000/usuarios/api/turnos/cliente/${usuario.value.id}/estadisticas/`, config)
        usuario.value.turnosCount = statsRes.data.total_turnos || 0
      } catch { usuario.value.turnosCount = 0 }
    } else {
      usuario.value = { 
        nombre: 'Invitado', 
        apellido: '', 
        dni: 'No identificado', 
        telefono: 'No registrado', 
        turnosCount: 0, 
        id: null 
      }
    }
  } catch (err) {
    console.error("Error usuario:", err)
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
    let url = "http://localhost:8000/usuarios/api/turnos/?estado__in=RESERVADO,CONFIRMADO"
    if (fecha) url += `&fecha=${fecha}`
    const res = await axios.get(url)
    turnosOcupados.value = res.data.results || res.data
  } catch (err) { turnosOcupados.value = [] }
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
  
  const isInRange = diffDays >= 0 && diffDays <= 14
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

const estaHorarioDisponible = (horario) => {
  if (!form.value.fecha || !form.value.peluquero) return true
  const turnoOcupado = turnosOcupados.value.find(turno => {
    return turno.peluquero_id == form.value.peluquero && 
           turno.fecha === form.value.fecha && 
           turno.hora === horario
  })
  return !turnoOcupado
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

  try {
    const token = localStorage.getItem('token')
    const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {}

    const res = await axios.post("http://localhost:8000/usuarios/api/turnos/crear/", payload, config)
    const data = res.data
    cargando.value = false

    if (data.status === 'ok') {
      if (data.procesar_pago && data.mp_data?.init_point) {
        Swal.fire({ 
          icon: 'success', 
          title: 'Reserva Iniciada', 
          text: 'Redirigiendo a Mercado Pago...', 
          timer: 2000, 
          showConfirmButton: false 
        }).then(() => { 
          window.open(data.mp_data.init_point, '_blank')
          router.push('/turnos')
        })
      } else {
        Swal.fire({ 
          icon: 'success', 
          title: '¡Turno Reservado!', 
          text: 'Te esperamos.', 
          timer: 2000, 
          showConfirmButton: false 
        }).then(() => { 
          router.push('/turnos')
        })
      }
    } else {
      Swal.fire('Error', data.message || "No se pudo reservar.", 'error')
    }
  } catch (err) {
    cargando.value = false
    if (err.response && err.response.status === 401) {
      Swal.fire('Sesión Expirada', 'Inicia sesión.', 'error')
    } else {
      Swal.fire('Error', err.response?.data?.message || 'Error de conexión', 'error')
    }
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

/* ... (todos los estilos anteriores se mantienen igual) ... */

/* NUEVOS ESTILOS PARA HORARIOS MEJORADOS */
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

.btn-avisar-liberado-mejorada {
  width: 100%;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.9em;
  margin-top: 8px;
}

.btn-avisar-liberado-mejorada:hover:not(:disabled) {
  background: linear-gradient(135deg, #0984e3, #074a8f);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(116, 185, 255, 0.4);
}

.btn-avisar-liberado-mejorada:disabled {
  background: linear-gradient(135deg, #00b894, #00a085);
  cursor: not-allowed;
}

/* Responsive para horarios */
@media (max-width: 768px) {
  .grid-horarios-mejorado {
    grid-template-columns: 1fr;
  }
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

.cupon-alerta {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
}

.cupon-alerta .card-header {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.cupon-alerta .card-icon {
  background: rgba(255, 255, 255, 0.2);
}

.cupon-alerta h3 {
  color: white;
}

.cupon-alerta p {
  margin: 0;
  padding: 10px 0 0 0;
  color: rgba(255, 255, 255, 0.9);
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

/* Cliente Info */
.cliente-info-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 2px solid #e9ecef;
}

.cliente-datos p {
  margin: 8px 0;
  color: #1a1a1a;
}

.info-pago {
  display: block;
  margin-top: 10px;
  color: #6c757d;
  font-size: 0.9em;
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

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
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
  margin-top: 15px;
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

.servicio-categoria {
  font-size: 0.75em;
  background: #f1f3f4;
  color: #6c757d;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
  align-self: flex-start;
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

.grid-horarios {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.btn-hora {
  padding: 12px;
  text-align: center;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: white;
  font-weight: 600;
  color: #1a1a1a;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-hora:hover:not(:disabled) {
  border-color: #007bff;
  color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.hora-selected {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-color: #007bff;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.hora-ocupada {
  background: #fee2e2;
  color: #dc3545;
  border-color: #fca5a5;
  text-decoration: line-through;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Interés en horarios */
.interes-horarios {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border-radius: 12px;
  padding: 15px;
  border: 2px solid #ffc107;
}

.interes-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  color: #856404;
}

.interes-info p {
  margin: 0;
  font-size: 0.9em;
}

.btn-interes {
  width: 100%;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.9em;
  margin-top: 8px;
}

.btn-interes:hover:not(:disabled) {
  background: linear-gradient(135deg, #0984e3, #074a8f);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(116, 185, 255, 0.4);
}

.btn-interes:disabled {
  background: linear-gradient(135deg, #00b894, #00a085);
  cursor: not-allowed;
}

/* Resumen */
.resumen-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  color: #1a1a1a;
  border-bottom: 1px solid #e9ecef;
}

.resumen-item:last-child {
  border-bottom: none;
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

.resumen-item.subtotal .tachado {
  text-decoration: line-through;
  color: #9ca3af;
  font-size: 0.9rem;
}

.resumen-item.descuento {
  color: #10b981;
  font-weight: 700;
  background: rgba(16, 185, 129, 0.1);
  padding: 8px 12px;
  border-radius: 8px;
  margin: 5px 0;
}

.monto-final-pago {
  color: #28a745;
  font-weight: 800;
  font-size: 1.3em;
}

.resumen-final {
  background: linear-gradient(135deg, #f8fff9, #f0f9ff);
  border-color: #28a745;
}

.resumen-detalles {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 20px;
}

/* Pago */
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

.radio-content small {
  color: #6c757d;
  font-size: 0.8em;
}

.radio-active .radio-content span {
  color: #007bff;
}

.medio-pago-box {
  border: 2px solid #e1e5e9;
  padding: 20px;
  border-radius: 12px;
  background: #f8f9fa;
}

.medio-pago-content {
  display: flex;
  color: grey;
  align-items: center;
  gap: 12px;
  font-size: 1.1em;
  font-weight: 600;
}

.medio-icon {
  font-size: 1.5em;
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

.btn-confirmar-premium:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, #0056b3, #004085);
}

.btn-confirmar-premium:disabled {
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

.info-pago-final {
  margin-top: 15px;
  text-align: center;
  color: #6c757d;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
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
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  background: linear-gradient(135deg, #4facfe, #00f2fe);
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
  cursor: pointer;
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

.info-interes-card {
  margin-bottom: 25px;
}

.info-details {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 20px;
}

.info-details p {
  margin: 8px 0;
  color: #1a1a1a;
}

.beneficio-descuento {
  padding: 15px;
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border-radius: 12px;
  text-align: center;
  border: 2px solid #ffd700;
  font-weight: 600;
}

.icono-descuento {
  font-size: 1.2em;
  margin-right: 5px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-confirmar-interes {
  padding: 15px 25px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.1em;
  flex: 1;
}

.btn-confirmar-interes:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
}

.btn-confirmar-interes:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancelar-interes {
  padding: 15px 25px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.1em;
  flex: 1;
}

.btn-cancelar-interes:hover {
  background: #5a6268;
  transform: translateY(-2px);
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

.slide-enter-active {
  transition: all 0.3s ease;
}
.slide-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-enter-from,
.slide-leave-to {
  transform: translateY(-10px);
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
  
  .grid-servicios {
    grid-template-columns: 1fr;
  }
  
  .calendar-grid {
    gap: 4px;
  }
  
  .day-btn {
    font-size: 0.85em;
  }
  
  .grid-horarios {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
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
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>