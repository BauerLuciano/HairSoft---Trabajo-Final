<template>
  <div class="page-background">
    <div class="main-card-container">
      <div class="turno-container">
        
        <!-- HEADER -->
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

        <div>
          <transition name="slide">
            <div v-if="descuentoAplicado > 0" class="promo-banner">
              <div class="promo-content">
                <div class="promo-icon-wrapper">
                  <Gift :size="24" />
                </div>
                <div class="promo-text">
                  <h4 class="m-0">¡Descuento Activado!</h4>
                  <p class="m-0">
                    Tenés un <strong>{{ descuentoAplicado }}% OFF</strong> bonificado en este turno.
                  </p>
                </div>
              </div>
              
              <div class="promo-code-section">
                <div class="code-pill">
                  <Tag :size="14" />
                  <span class="code-text">{{ cuponCodigo }}</span>
                </div>
                <small v-if="fechaVencimientoCupon" class="expiry-text">
                  Vence: {{ fechaVencimientoCupon }}
                </small>
              </div>
            </div>
          </transition>

          <!-- MENSAJE DE ERROR DE CUPÓN -->
          <transition name="fade">
            <div v-if="mensajeErrorCupon" class="card-modern cupon-error">
              <div class="card-header">
                <div class="card-icon" style="background: #ef4444; color: white;">
                  <AlertCircle :size="20" />
                </div>
                <h3>❌ Error en Cupón</h3>
              </div>
              <p>{{ mensajeErrorCupon }}</p>
              <button @click="mensajeErrorCupon = ''" class="btn-cerrar-error">
                <X :size="16" /> Cerrar
              </button>
            </div>
          </transition>

          <!-- DATOS DEL CLIENTE -->
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
                <p><strong>DNI:</strong> {{ usuario.dni || 'No registrado' }}</p>
                <p><strong>Teléfono:</strong> {{ usuario.telefono || 'No registrado' }}</p>
                <p v-if="usuario.turnosCount > 0"><strong>Turnos reservados:</strong> {{ usuario.turnosCount }}</p>
              </div>
            </div>
          </div>

          <!-- CATEGORÍAS DE SERVICIO -->
          <div class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon">
                <FolderOpen :size="20" />
              </div>
              <h3>Categoría de Servicio</h3>
              <span v-if="categoriasSeleccionadas.length" class="badge-count">
                {{ categoriasSeleccionadas.length }}
              </span>
            </div>
            
            <div v-if="categorias.length === 0" class="loading-spinner">
              <Loader2 class="spinner-icon" :size="24" />
              <p>Cargando categorías...</p>
            </div>
            
            <div v-else class="grid-chips">
              <button 
                type="button"
                v-for="categoria in categorias" 
                :key="categoria.id"
                class="chip-modern"
                :class="{ 'chip-active': categoriasSeleccionadas.includes(String(categoria.id)) }"
                @click="toggleCategoria(categoria.id)"
              >
                <Tag :size="14" />
                {{ categoria.nombre }}
              </button>
            </div>
            
            <p v-if="categoriasSeleccionadas.length > 0" class="hint-text">
              ✅ Has seleccionado {{ categoriasSeleccionadas.length }} categoría(s)
            </p>
          </div>

          <!-- SERVICIOS -->
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
                  @input="filtrarServicios"
                />
              </div>
            </div>
            
            <div v-if="servicios.length === 0" class="loading-spinner">
              <Loader2 class="spinner-icon" :size="24" />
              <p>Cargando servicios...</p>
            </div>
            
            <div v-else-if="serviciosFiltrados.length === 0" class="no-resultados">
              <Inbox class="no-resultados-icon" :size="48" />
              <p v-if="busquedaServicio">No se encontraron servicios con "{{ busquedaServicio }}"</p>
              <p v-else>No hay servicios en las categorías seleccionadas</p>
              <small>Intenta seleccionar otras categorías</small>
            </div>
            
            <div v-else class="grid-servicios">
              <div 
                v-for="servicio in serviciosFiltrados" 
                :key="servicio.id"
                class="card-servicio"
                :class="{ 'servicio-active': estaServicioSeleccionado(servicio) }"
                @click="toggleServicio(servicio)"
              >
                <div class="servicio-check">
                  <Check v-if="estaServicioSeleccionado(servicio)" :size="16" />
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
            
            <div v-if="form.servicios_ids.length > 0" class="servicios-seleccionados">
              <h4>📋 Servicios seleccionados ({{ form.servicios_ids.length }})</h4>
              <div class="servicios-lista">
                <span v-for="servicioId in form.servicios_ids" :key="servicioId" class="servicio-tag">
                  {{ getServicioNombre(servicioId) }}
                  <button @click="eliminarServicio(servicioId)" class="btn-eliminar-servicio">
                    <X :size="12" />
                  </button>
                </span>
              </div>
              <p class="total-parcial">
                Total parcial: <strong>${{ calcularTotal() }}</strong>
                <span v-if="descuentoAplicado > 0" class="descuento-indicador">
                  (-{{ descuentoAplicado }}% descuento aplicado)
                </span>
              </p>
            </div>
          </div>

          <!-- PELUQUERO -->
          <div v-if="form.servicios_ids.length > 0" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon">
                <UserCheck :size="20" />
              </div>
              <h3>Elegir Peluquero</h3>
            </div>
            
            <div v-if="peluqueros.length === 0" class="loading-spinner">
              <Loader2 class="spinner-icon" :size="24" />
              <p>Cargando peluqueros...</p>
            </div>
            
            <div v-else class="grid-peluqueros">
              <div 
                v-for="p in peluqueros" 
                :key="p.id"
                class="card-peluquero"
                :class="{ 'peluquero-active': form.peluquero === p.id }"
                @click="seleccionarPeluquero(p.id)"
              >
                <div class="peluquero-avatar">
                  {{ getInicialesPeluquero(p) }}
                </div>
                
                <div class="peluquero-info">
                  <span class="peluquero-nombre">{{ getNombreCompletoPeluquero(p) }}</span>
                  <span class="peluquero-experiencia">Peluquero profesional</span>
                </div>
                
                <div v-if="form.peluquero === p.id" class="peluquero-selected">
                  <CheckCircle :size="20" />
                </div>
              </div>
            </div>
            
            <p v-if="form.peluquero" class="hint-text">
              ✅ Peluquero seleccionado: <strong>{{ getPeluqueroNombre() }}</strong>
            </p>
          </div>

          <!-- FECHA -->
          <div v-if="form.peluquero" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon">
                <CalendarDays :size="20" />
              </div>
              <h3>Seleccionar Fecha</h3>
              <span v-if="form.fecha" class="badge-count">
                {{ formatoFechaLegible(form.fecha) }}
              </span>
            </div>
            
            <div class="calendar-wrapper">
              <div class="calendar-header">
                <button type="button" @click="cambiarMes(-1)" class="btn-nav-cal">
                  <ChevronLeft :size="20" />
                </button>
                <span class="mes-titulo">{{ nombreMesActual }} {{ currentYear }}</span>
                <button type="button" @click="cambiarMes(1)" class="btn-nav-cal">
                  <ChevronRight :size="20" />
                </button>
              </div>

              <div class="calendar-days-header">
                <span v-for="d in ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb']" :key="d">{{ d }}</span>
              </div>

              <div class="calendar-grid">
                <div v-for="i in startingDayOfWeek" :key="'empty-'+i" class="day-empty"></div>
                
                <button 
                  type="button"
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

          <!-- HORARIOS -->
          <div v-if="form.fecha" class="card-modern slide-in">
            <div class="card-header">
              <div class="card-icon">
                <Clock :size="20" />
              </div>
              <h3>Horarios Disponibles</h3>
              <span v-if="form.hora" class="badge-count">
                {{ form.hora }}
              </span>
            </div>
            
            <div v-if="cargandoHorarios" class="loading-spinner">
              <Loader2 class="spinner-icon" :size="32" />
              <p>Buscando horarios disponibles...</p>
            </div>
            
            <div v-else class="grid-horarios-mejorado">
              <!-- HORARIOS DISPONIBLES -->
              <div
                v-for="hora in horariosDisponibles"
                :key="hora"
                class="hora-card-mejorada"
                :class="{
                  'hora-selected-mejorada': form.hora === hora,
                  'hora-disponible-mejorada': true
                }"
                @click="seleccionarHora(hora)"
              >
                <div class="hora-content-mejorada">
                  <div class="hora-info-mejorada">
                    <Clock :size="16" class="hora-icon-mejorada" />
                    <span class="hora-texto-mejorada">{{ hora }}</span>
                  </div>
                  <div class="hora-estado-mejorada disponible">
                    <span>Disponible</span>
                  </div>
                </div>
              </div>

              <!-- HORARIOS OCUPADOS -->
              <div
                v-for="hora in horariosOcupadosParaMostrar"
                :key="'ocupado-'+hora"
                class="hora-card-mejorada hora-ocupada-mejorada"
              >
                <div class="hora-content-mejorada ocupada">
                  <div class="hora-info-mejorada">
                    <Clock :size="16" class="hora-icon-mejorada" />
                    <span class="hora-texto-mejorada">{{ hora }}</span>
                    <span class="hora-duracion-badge-ocupado">Ocupado</span>
                  </div>
                  
                  <button 
                    type="button"
                    class="btn-avisar-liberado-mejorada"
                    :disabled="estaInteresRegistrado(hora)"
                    @click.stop="registrarInteresHorario(hora)"
                  >
                    <Bell :size="14" />
                    {{ estaInteresRegistrado(hora) ? 'En lista' : 'Avísame' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- POLÍTICA DE RESERVA -->
          <div v-if="form.hora" class="politica-seccion-card slide-in">
            <div class="politica-header">
              <Info :size="18" class="politica-icon" />
              <span>Política de Reserva y Reembolso</span>
            </div>
            <div class="politica-contenido">
              <p class="politica-texto-principal">
                {{ configSist.politica_senia }}
              </p>

              <div class="politica-reglas">
                <div class="regla-item positive">
                  <CheckCircle :size="16" />
                  <span>
                    <strong>Aviso con más de {{ configSist.margen_horas_cancelacion }} horas:</strong> 
                    Devolución total del dinero abonado.
                  </span>
                </div>
                
                <div class="regla-item negative">
                  <AlertCircle :size="16" />
                  <span>
                    <strong>Aviso con menos de {{ configSist.margen_horas_cancelacion }} horas:</strong> 
                    Sin reembolso. Se aplica penalidad por cancelación tardía.
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- OPCIONES DE PAGO -->
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

          <!-- RESUMEN FINAL Y CONFIRMACIÓN -->
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
              
              <!-- 🔥 SECCIÓN DE DESCUENTO EN RESUMEN -->
              <div v-if="descuentoAplicado > 0" class="resumen-item descuento-resumen">
                <span><Gift :size="14" /> Descuento aplicado:</span>
                <span class="descuento-positivo">- {{ descuentoAplicado }}%</span>
              </div>
              
              <div class="resumen-item total">
                <span><Wallet :size="16" /> Total a pagar ahora:</span>
                <span class="monto-final-pago">${{ montoAPagarAhora() }}</span>
              </div>
            </div>
            
            <button
              type="button"
              @click="crearPagoMercadoPago" 
              class="btn-confirmar-premium"
              :disabled="cargandoMercadoPago"
            >
              <span class="btn-content">
                <CreditCard :size="20" />
                {{ cargandoMercadoPago ? '🔄 Creando pago...' : `Pagar $${montoAPagarAhora()} con Mercado Pago` }}
              </span>
            </button>
            
            <p class="info-pago-final">
              <CheckCircle2 :size="14" />
              Serás redirigido a Mercado Pago para completar el pago.
            </p>
          </div>
        </div>

        <!-- MODAL DE INTERÉS -->
        <div v-if="mostrarModalInteres" class="modal-overlay">
          <div class="modal-content">
            <div class="modal-header">
              <h3>🔔 Confirmar Interés</h3>
              <button class="modal-close-btn" @click="cancelarRegistroInteres"><X :size="20" /></button>
            </div>
            <div class="modal-body">
              <div class="info-interes-card">
                <p><strong>📅 Fecha:</strong> {{ formatoFechaLegible(form.fecha) }}</p>
                <p><strong>⏰ Horario:</strong> {{ horarioSeleccionadoInteres }}</p>
                <p><strong>👨‍💼 Peluquero:</strong> {{ getPeluqueroNombre() }}</p>
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

        <!-- TOAST DE MENSAJES -->
        <transition name="fade">
          <div v-if="mensaje" class="toast-message" :class="mensajeTipo">{{ mensaje }}</div>
        </transition>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import Swal from 'sweetalert2'
import { 
  Calendar, ArrowLeft, User, UserCheck, FolderOpen, Tag, 
  Scissors, Check, DollarSign, Clock, CalendarDays, 
  ChevronLeft, ChevronRight, Loader2, 
  CheckCircle2, Bell, Banknote, Inbox, CheckCircle, CreditCard, Wallet,
  Gift, Search, X, AlertCircle, Info
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const cuponCodigo = ref(null)
const descuentoAplicado = ref(0)
const mensajePromo = ref("")
const fechaVencimientoCupon = ref("")
const mensajeErrorCupon = ref("")
const mostrarDescuento = computed(() => {
  const totalOriginal = calcularTotalOriginal()
  if (descuentoAplicado.value > 0 && totalOriginal > 0) {
    const ahorro = totalOriginal * (descuentoAplicado.value / 100)
    return {
      porcentaje: descuentoAplicado.value,
      totalOriginal: totalOriginal,
      ahorro: ahorro,
      totalConDescuento: totalOriginal - ahorro
    }
  }
  return null
})

// CONFIGURACIÓN DEL SISTEMA
const configSist = ref({
  margen_horas_cancelacion: 3,
  politica_senia: 'Cargando política de reserva...'
})

// FORMULARIO
const form = ref({
  peluquero: "", 
  servicios_ids: [], 
  hora: "", 
  fecha: "",
  tipo_pago: "SENA_50", 
  medio_pago: "MERCADO_PAGO", 
  canal: "WEB", 
  cliente: null,
  cup_codigo: null  // 🔥 NUEVO: Campo para cupón
})

// DATOS
const usuario = ref({ 
  id: null, 
  nombre: '', 
  apellido: '', 
  dni: '', 
  telefono: '', 
  turnosCount: 0, 
  isAuthenticated: false 
})
const peluqueros = ref([])
const servicios = ref([])
const categorias = ref([])
const slotsOcupadosReales = ref([])
const categoriasSeleccionadas = ref([])
const busquedaServicio = ref("")
const cargandoMercadoPago = ref(false)
const cargandoHorarios = ref(false)
const cargandoDatos = ref(true)
const mostrarModalInteres = ref(false)
const horarioSeleccionadoInteres = ref(null)
const registrandoInteres = ref(false)
const currentDate = ref(new Date())
const DIAS_RANGO = 7
const horariosInteres = ref([])
const mensaje = ref("")
const mensajeTipo = ref("")

// 🔥 NUEVA FUNCIÓN: VALIDAR CUPÓN CON BACKEND
const validarCuponBackend = async (codigo) => {
  if (!codigo) return
  
  try {
    console.log(`🎟️ Validando cupón: ${codigo}`)
    
    const response = await api.get(`/api/promociones/validar/${codigo}/`)
    
    if (response.data.valido) {
      // Aplicar descuento
      descuentoAplicado.value = response.data.descuento
      mensajePromo.value = response.data.mensaje
      fechaVencimientoCupon.value = response.data.valido_hasta || ""
      
      // Mostrar mensaje de éxito
      Swal.fire({
        title: '¡Cupón Aplicado!',
        text: response.data.mensaje,
        icon: 'success',
        timer: 3000,
        showConfirmButton: false
      })
      
      // Guardar código en el form para enviar al backend
      form.value.cup_codigo = codigo
      
      return true
    } else {
      // Mostrar error
      mensajeErrorCupon.value = response.data.mensaje
      descuentoAplicado.value = 0
      cuponCodigo.value = null
      form.value.cup_codigo = null
      
      Swal.fire({
        title: 'Cupón Inválido',
        text: response.data.mensaje,
        icon: 'error',
        confirmButtonText: 'Entendido'
      })
      
      return false
    }
  } catch (error) {
    console.error('Error validando cupón:', error)
    
    mensajeErrorCupon.value = 'Error al validar el cupón. Intenta nuevamente.'
    descuentoAplicado.value = 0
    cuponCodigo.value = null
    form.value.cup_codigo = null
    
    Swal.fire({
      title: 'Error',
      text: 'No se pudo validar el cupón. Intenta nuevamente.',
      icon: 'error',
      confirmButtonText: 'Entendido'
    })
    
    return false
  }
}

// 🔥 CORREGIR: onMounted para validar cupón automáticamente
onMounted(async () => {
  await cargarDatosIniciales()
  
  // Verificar si hay cupón en la URL
  if (route.query.cup) {
    cuponCodigo.value = route.query.cup
    console.log(`🔍 Cupón detectado en URL: ${route.query.cup}`)
    
    // Validar automáticamente el cupón
    await validarCuponBackend(route.query.cup)
  }
})

// WATCHERS
watch(() => form.value.servicios_ids, () => {
  if (form.value.fecha && form.value.peluquero && form.value.hora) {
    if (!esHorarioDisponibleCompleto(form.value.hora)) {
      form.value.hora = ""
    }
  }
}, { deep: true })

watch([() => form.value.fecha, () => form.value.peluquero], ([nuevaFecha, nuevoPeluquero]) => {
  if (nuevaFecha && nuevoPeluquero) cargarTurnosOcupados(nuevaFecha)
})

// FUNCIONES AUXILIARES
const getListaServicios = () => {
  try {
    if (Array.isArray(servicios.value)) return servicios.value
    if (servicios.value?.results) return servicios.value.results
    return []
  } catch (error) { 
    return [] 
  }
}

const serviciosFiltrados = computed(() => {
  try {
    let lista = getListaServicios()
    if (categoriasSeleccionadas.value.length > 0) {
      lista = lista.filter(s => {
        if (!s || !s.categoria) return false
        let catId = (typeof s.categoria === 'object' && s.categoria !== null) 
                    ? String(s.categoria.id || s.categoria) 
                    : String(s.categoria)
        return categoriasSeleccionadas.value.includes(catId)
      })
    }
    if (busquedaServicio.value.trim()) {
      const term = busquedaServicio.value.toLowerCase().trim()
      lista = lista.filter(s => s && s.nombre && s.nombre.toLowerCase().includes(term))
    }
    return lista
  } catch (error) { 
    return [] 
  }
})

const toggleCategoria = (id) => {
  const cid = String(id)
  const index = categoriasSeleccionadas.value.indexOf(cid)
  if (index > -1) categoriasSeleccionadas.value.splice(index, 1)
  else categoriasSeleccionadas.value.push(cid)
}

const toggleServicio = (servicio) => {
  if (!servicio || !servicio.id) return
  const id = String(servicio.id)
  const index = form.value.servicios_ids.indexOf(id)
  if (index > -1) form.value.servicios_ids.splice(index, 1)
  else form.value.servicios_ids.push(id)
  if (form.value.hora) form.value.hora = ""
}

const estaServicioSeleccionado = (servicio) => servicio?.id && form.value.servicios_ids.includes(String(servicio.id))

const eliminarServicio = (servicioId) => {
  form.value.servicios_ids = form.value.servicios_ids.filter(id => id !== String(servicioId))
  if (form.value.hora) form.value.hora = ""
}

const formularioValido = computed(() => 
  form.value.peluquero && 
  form.value.servicios_ids.length > 0 && 
  form.value.fecha && 
  form.value.hora
)

const calcularTotalOriginal = () => {
  try {
    const lista = getListaServicios()
    return form.value.servicios_ids.reduce((acc, id) => {
      const s = lista.find(x => String(x.id) === String(id))
      return acc + (parseFloat(s?.precio) || 0)
    }, 0)
  } catch (error) { 
    return 0 
  }
}

const calcularTotal = () => calcularTotalOriginal().toFixed(2)

const calcularTotalConDescuento = () => {
  const total = calcularTotalOriginal()
  const descuento = total * (descuentoAplicado.value / 100)
  return (total - descuento).toFixed(2)
}

const calcularDuracionTotalServicios = () => {
  const lista = getListaServicios()
  return form.value.servicios_ids.reduce((total, id) => {
    const s = lista.find(x => String(x.id) === String(id))
    return total + parseInt(s?.duracion || s?.duracion_minutos || 20)
  }, 0)
}

const calcularSena = () => {
  const totalConDescuento = parseFloat(calcularTotalConDescuento())
  return (totalConDescuento * 0.5).toFixed(2)
}

const montoAPagarAhora = () => {
  return (form.value.tipo_pago === 'SENA_50' ? calcularSena() : calcularTotalConDescuento())
}

const getServicioNombre = (id) => getListaServicios().find(s => String(s.id) === String(id))?.nombre || 'Servicio'

const getPeluqueroNombre = () => {
  const lista = Array.isArray(peluqueros.value) ? peluqueros.value : (peluqueros.value?.results || [])
  const p = lista.find(x => String(x.id) === String(form.value.peluquero))
  return p ? `${p.nombre || ''} ${p.apellido || ''}`.trim() : ''
}

const getServiciosNombres = () => form.value.servicios_ids.map(id => getServicioNombre(id)).join(', ')

const getNombreCompletoPeluquero = (p) => p ? `${p.nombre || ''} ${p.apellido || ''}`.trim() : ''

const getInicialesPeluquero = (p) => (p?.nombre || 'P').charAt(0).toUpperCase()

const formatoFechaLegible = (f) => f ? new Date(f + 'T12:00:00').toLocaleDateString('es-ES', { 
  weekday: 'long', 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric' 
}) : ''

const getCategoriaNombre = (cat) => (typeof cat === 'object' && cat !== null) ? (cat.nombre || 'General') : 'General'

const nombreMesActual = computed(() => currentDate.value.toLocaleString('es-ES', { month: 'long' }).toUpperCase())

const currentYear = computed(() => currentDate.value.getFullYear())

const startingDayOfWeek = computed(() => new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1).getDay())

const daysInMonth = computed(() => new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 0).getDate())

const esHoy = (day) => {
  const hoy = new Date()
  return day === hoy.getDate() && 
         currentDate.value.getMonth() === hoy.getMonth() && 
         currentYear.value === hoy.getFullYear()
}

const esDiaSeleccionado = (day) => form.value.fecha && 
  day === new Date(form.value.fecha + 'T12:00:00').getDate() && 
  currentDate.value.getMonth() === new Date(form.value.fecha + 'T12:00:00').getMonth()

const esDiaSeleccionable = (day) => {
  const target = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day)
  target.setHours(0,0,0,0)
  const hoy = new Date()
  hoy.setHours(0,0,0,0)
  
  if (target < hoy || target.getDay() === 0) return false
  
  let tempDate = new Date(hoy)
  let count = 0
  while (tempDate <= target) { 
    if (tempDate.getDay() !== 0) count++
    tempDate.setDate(tempDate.getDate() + 1)
  }
  
  return count <= DIAS_RANGO
}

const seleccionarDiaCalendario = (day) => {
  const month = String(currentDate.value.getMonth() + 1).padStart(2, '0')
  form.value.fecha = `${currentYear.value}-${month}-${String(day).padStart(2, '0')}`
  form.value.hora = ""
}

const cambiarMes = (delta) => { 
  const n = new Date(currentDate.value)
  n.setMonth(n.getMonth() + delta)
  currentDate.value = n
}

const esHorarioDisponibleUI = (h) => {
  if (!form.value.fecha || !form.value.peluquero) return true
  
  const [hS, mS] = h.substring(0,5).split(':').map(Number)
  const horaString = `${hS.toString().padStart(2, '0')}:${mS.toString().padStart(2, '0')}`
  
  if (slotsOcupadosReales.value.some(slot => 
      slot.startsWith(horaString.substring(0, 5)))) return false
  
  const hoy = new Date()
  const hoyF = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
  
  if (form.value.fecha === hoyF) {
    return (hS * 60 + mS) > (hoy.getHours() * 60 + hoy.getMinutes() + 30)
  }
  
  return true
}

const esHorarioDisponibleCompleto = (horaSeleccionada) => {
  if (!form.value.fecha || !form.value.peluquero) return false
  
  const duracionTotal = calcularDuracionTotalServicios()
  
  if (duracionTotal === 0) return esHorarioDisponibleUI(horaSeleccionada)
  
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
    if (inicioMinutos < (hoy.getHours() * 60 + hoy.getMinutes() + 30)) {
      return false
    }
  }
  
  return true
}

const horariosDisponibles = computed(() => 
  ['08:00','08:20','08:40','09:00','09:20','09:40','10:00','10:20','10:40',
   '11:00','11:20','11:40','15:00','15:20','15:40','16:00','16:20','16:40',
   '17:00','17:20','17:40','18:00','18:20','18:40','19:00','19:20','19:40','20:00']
  .filter(h => esHorarioDisponibleCompleto(h))
)

const horariosOcupadosParaMostrar = computed(() => 
  ['08:00','08:20','08:40','09:00','09:20','09:40','10:00','10:20','10:40',
   '11:00','11:20','11:40','15:00','15:20','15:40','16:00','16:20','16:40',
   '17:00','17:20','17:40','18:00','18:20','18:40','19:00','19:20','19:40','20:00']
  .filter(h => !esHorarioDisponibleCompleto(h))
)

const seleccionarPeluquero = (id) => { 
  form.value.peluquero = id
  form.value.hora = ""
  slotsOcupadosReales.value = []
}

const seleccionarHora = (h) => { 
  if (esHorarioDisponibleCompleto(h)) form.value.hora = h
}

const cargarDatosIniciales = async () => {
  cargandoDatos.value = true
  try {
    const userId = localStorage.getItem('user_id')
    if (!userId) return router.push('/login')
    
    const [resU, p, s, c, resConfig] = await Promise.all([
      api.get(`/api/usuarios/${userId}/`),
      api.get('/api/peluqueros/'),
      api.get('/api/servicios/'),
      api.get('/api/categorias/servicios/'),
      api.get('/api/configuracion/')
    ])
    
    usuario.value = { ...resU.data, isAuthenticated: true }
    form.value.cliente = userId
    peluqueros.value = p.data?.results || p.data
    servicios.value = s.data?.results || s.data
    categorias.value = c.data?.results || c.data
    
    if (resConfig.data) {
      configSist.value = resConfig.data
    }
    
  } catch (error) {
    console.error('Error cargando datos iniciales:', error)
    Swal.fire({
      title: 'Error',
      text: 'No se pudieron cargar los datos. Intenta recargar la página.',
      icon: 'error'
    })
  } finally {
    cargandoDatos.value = false
  }
}

const cargarTurnosOcupados = async (f) => {
  if (!form.value.peluquero || !f) return
  cargandoHorarios.value = true
  
  try {
    const res = await api.get(`/api/turnos/?fecha=${f}&peluquero=${form.value.peluquero}`)
    const turnosData = res.data?.results || res.data
    const ocupadosSet = new Set()
    
    turnosData.forEach(turno => {
      if (turno.estado === 'CANCELADO' || turno.estado === 'DISPONIBLE') return
      if (turno.fecha !== f) return
      if (!turno.hora) return
      
      const [h, m] = turno.hora.split(':').map(Number)
      let dur = turno.duracion_total || 0
      
      if (!dur && turno.servicios) {
        if (Array.isArray(turno.servicios)) {
          dur = turno.servicios.reduce((acc, s) => acc + (s.duracion || 20), 0)
        } else {
          dur = 20
        }
      }
      
      if (!dur) dur = 20
      
      const inicioMin = h * 60 + m
      const finMin = inicioMin + dur
      
      for (let i = inicioMin; i < finMin; i++) {
        ocupadosSet.add(`${Math.floor(i/60).toString().padStart(2,'0')}:${(i%60).toString().padStart(2,'0')}`)
      }
    })
    
    slotsOcupadosReales.value = Array.from(ocupadosSet)
    
  } catch (error) {
    console.error('Error cargando turnos ocupados:', error)
  } finally {
    cargandoHorarios.value = false
  }
}

// 🔥 CORREGIR: crearPagoMercadoPago para incluir cupón
const crearPagoMercadoPago = async () => {
  if (!formularioValido.value) {
    Swal.fire({
      title: 'Formulario Incompleto',
      text: 'Por favor completa todos los campos requeridos.',
      icon: 'warning'
    })
    return
  }
  
  cargandoMercadoPago.value = true
  
  try {
    const payload = {
      peluquero_id: parseInt(form.value.peluquero),
      cliente_id: parseInt(usuario.value.id),
      servicios_ids: form.value.servicios_ids.map(id => parseInt(id)),
      fecha: form.value.fecha,
      hora: form.value.hora,
      canal: 'WEB',
      tipo_pago: form.value.tipo_pago,
      medio_pago: 'MERCADO_PAGO',
      monto_total: parseFloat(calcularTotalConDescuento()),
      cup_codigo: form.value.cup_codigo,  // 🔥 ENVIAR CUPÓN AL BACKEND
      duracion_total: calcularDuracionTotalServicios()
    }
    
    console.log('📤 Enviando payload con cupón:', payload.cup_codigo)
    
    const res = await api.post('/api/turnos/crear/', payload)
    
    if (res.data.status === 'ok') {
      // 🔥 MOSTRAR INFORMACIÓN DE DESCUENTO APLICADO
      if (res.data.descuento && res.data.descuento.aplicado) {
        Swal.fire({
          title: '¡Descuento Aplicado!',
          html: `✅ Se aplicó un ${res.data.descuento.porcentaje}% de descuento<br>
                 <strong>Total a pagar: $${res.data.descuento.monto_final.toFixed(2)}</strong>`,
          icon: 'success',
          timer: 4000,
          showConfirmButton: false
        })
      }
      
      const mpUrl = res.data?.mp_data?.init_point
      if (mpUrl) {
        // Redirigir a Mercado Pago
        window.location.href = mpUrl
      } else {
        Swal.fire({
          title: 'Turno Creado',
          text: 'Tu turno fue reservado exitosamente.',
          icon: 'success'
        }).then(() => {
          router.push('/cliente/historial')
        })
      }
    } else {
      throw new Error(res.data.message || 'Error al crear el turno')
    }
    
  } catch (error) {
    console.error('Error creando turno:', error)
    
    let errorMsg = 'Error al crear el turno.'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    }
    
    Swal.fire({
      title: 'Error',
      text: errorMsg,
      icon: 'error',
      confirmButtonText: 'Entendido'
    })
    
  } finally {
    cargandoMercadoPago.value = false
  }
}

const registrarInteresHorario = (h) => {
  horarioSeleccionadoInteres.value = h
  mostrarModalInteres.value = true
}

const cancelarRegistroInteres = () => {
  mostrarModalInteres.value = false
}

const estaInteresRegistrado = (h) => 
  horariosInteres.value.some(hi => hi.hora === h && hi.fecha === form.value.fecha)

const confirmarRegistroInteres = async () => {
  registrandoInteres.value = true
  
  try {
    await api.post('/api/turnos/registrar-interes/', {
      fecha: form.value.fecha,
      hora: horarioSeleccionadoInteres.value,
      peluquero_id: form.value.peluquero,
      cliente_id: usuario.value.id,
      servicios_ids: form.value.servicios_ids,
      interes_notificacion: true
    })
    
    Swal.fire({
      title: '¡Interés registrado!',
      text: 'Te avisaremos si este horario se libera.',
      icon: 'success',
      timer: 3000,
      showConfirmButton: false
    })
    
    mostrarModalInteres.value = false
    
  } catch (error) {
    Swal.fire({
      title: 'Error',
      text: 'No se pudo registrar tu interés. Intenta nuevamente.',
      icon: 'error'
    })
  } finally {
    registrandoInteres.value = false
  }
}

const filtrarServicios = () => {
  nextTick()
}

const volverAlListado = () => router.push('/cliente/historial')

// 🔥 NUEVA FUNCIÓN: Validar cupón manualmente
const validarCuponManual = async () => {
  if (!cuponCodigo.value) {
    Swal.fire({
      title: 'Código Vacío',
      text: 'Por favor ingresa un código de cupón.',
      icon: 'warning'
    })
    return
  }
  
  await validarCuponBackend(cuponCodigo.value)
}

// Exportar funciones para usar en template
defineExpose({
  form,
  usuario,
  serviciosFiltrados,
  toggleServicio,
  estaServicioSeleccionado,
  eliminarServicio,
  crearPagoMercadoPago,
  validarCuponManual
})
</script>

<style scoped>
/* ============================================
   NUEVOS ESTILOS: POLÍTICA DE SEÑAS (PEDIDO PROFE)
   ============================================ */
.politica-seccion-card {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 25px;
}

.politica-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  color: #1e293b;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.85rem;
}

.politica-icon {
  color: #3b82f6;
}

.politica-contenido {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.politica-texto-principal {
  color: #4b5563;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
}

.politica-margen-badge {
  background: #eff6ff;
  color: #1d4ed8;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.88rem;
  border: 1px solid #dbeafe;
}

.politica-margen-badge strong {
  color: #1e3a8a;
}

/* ============================================
   ESTILOS ORIGINALES (MANTENIDOS AL 100%)
   ============================================ */
.alerta-mercado-pago {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 3px solid #2196f3;
  animation: pulse-alerta 2s infinite;
  margin-bottom: 30px;
}

@keyframes pulse-alerta {
  0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.4); }
  70% { box-shadow: 0 0 0 15px rgba(33, 150, 243, 0); }
  100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
}

.alerta-contenido {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 20px 0;
}

.alerta-icono-grande {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #2196f3, #0d47a1);
  border-radius: 50%;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
}

.alerta-mensaje {
  flex: 1;
}

.alerta-mensaje h4 {
  margin: 0 0 15px 0;
  color: #1565c0;
  font-size: 1.4em;
  font-weight: 700;
}

.alerta-mensaje p {
  margin: 0 0 20px 0;
  color: #37474f;
  font-size: 1.1em;
  line-height: 1.5;
}

.detalles-turno {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(33, 150, 243, 0.2);
}


.slide-enter-active,
.slide-leave-active {
  transition: all 0.4s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.detalle-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  color: #455a64;
}

.detalle-item svg {
  color: #2196f3;
  flex-shrink: 0;
}

.detalle-item strong {
  color: #1565c0;
  margin-right: 5px;
}

.alerta-acciones {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 25px;
  padding-top: 25px;
  border-top: 2px solid rgba(33, 150, 243, 0.2);
}

.btn-ver-turnos {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #2196f3, #0d47a1);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.btn-ver-turnos:hover {
  background: linear-gradient(135deg, #0d47a1, #08306b);
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(33, 150, 243, 0.4);
}

.btn-nueva-reserva {
  width: 100%;
  padding: 18px;
  background: white;
  color: #2196f3;
  border: 2px solid #2196f3;
  border-radius: 12px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.btn-nueva-reserva:hover {
  background: #e3f2fd;
  transform: translateY(-2px);
}

.nota-pago {
  text-align: center;
  color: #546e7a;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 0;
}

.nota-pago svg {
  color: #ff9800;
}

.grid-peluqueros {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.card-peluquero {
  border: 2px solid #e9ecef;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  background: white;
}

.card-peluquero:hover {
  border-color: #667eea;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.15);
}

.peluquero-active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
}

.peluquero-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
}

.peluquero-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.peluquero-nombre {
  font-weight: 700;
  color: #333;
  font-size: 18px;
  display: block;
}

.peluquero-experiencia {
  font-size: 14px;
  color: #666;
  background: #f8f9fa;
  padding: 4px 10px;
  border-radius: 20px;
  align-self: flex-start;
}

.peluquero-selected {
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
  flex-shrink: 0;
}

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

.cliente-info-card {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  padding: 25px;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  position: relative;
}

.cliente-datos {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  row-gap: 16px;
}

.cliente-datos p {
  margin: 0;
  color: #4b5563;
  font-size: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.5;
}

.cliente-datos strong {
  color: #1f2937;
  font-weight: 700;
  min-width: 120px;
  display: inline-block;
  flex-shrink: 0;
}

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

.grid-horarios-mejorado {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  width: 100%;
}

.hora-card-mejorada {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 10px;
  cursor: pointer;
  text-align: center;
  font-weight: 600;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  width: 100%;
  transition: all 0.3s ease;
}

.hora-card-mejorada:hover:not(.hora-ocupada-mejorada) {
  border-color: #3b82f6;
  transform: translateY(-2px);
}

.hora-selected-mejorada {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 0 0 2px #3b82f6;
}

.hora-ocupada-mejorada {
  background: #fef2f2;
  border-color: #fee2e2;
  cursor: not-allowed;
  opacity: 0.8;
  color: #dc2626;
}

.hora-content-mejorada {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
}

.hora-info-mejorada {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.hora-icon-mejorada {
  color: #6b7280;
  flex-shrink: 0;
}

.hora-texto-mejorada {
  font-weight: 700;
  font-size: 1.15rem;
  color: #1f2937;
  white-space: nowrap;
}

.hora-duracion-badge-ocupado {
  background: #fef2f2;
  color: #dc2626;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  white-space: nowrap;
}

.hora-estado-mejorada {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.85rem;
  padding: 6px 10px;
  border-radius: 8px;
  width: fit-content;
  max-width: 100%;
}

.hint-text {
  margin-top: 12px;
  padding: 10px 15px;
  background: #f0f9ff;
  border-radius: 8px;
  color: #0369a1;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.servicios-seleccionados {
  margin-top: 25px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.servicios-seleccionados h4 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 1rem;
}

.servicios-lista {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.servicio-tag {
  background: #e0f2fe;
  color: #0369a1;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-eliminar-servicio {
  background: none;
  border: none;
  color: #0369a1;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-eliminar-servicio:hover {
  background: #bae6fd;
}

.total-parcial {
  margin: 0;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
  color: #1f2937;
  font-size: 1rem;
  text-align: right;
}

.total-parcial strong {
  color: #059669;
  font-size: 1.2rem;
}

.calendar-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px;
  background: #fef3c7;
  border-radius: 8px;
  color: #92400e;
  font-size: 0.9rem;
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
  justify-content: center; gap: 6px;
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
  100% { transform: rotate(360deg); }
}

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

.politica-reglas {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 15px 0;
}

.regla-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  padding: 8px 12px;
  border-radius: 8px;
}

.regla-item.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #065f46;
}

.regla-item.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #991b1b;
}

.politica-texto-principal {
  color: #1e293b;
  font-weight: 500;
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

/* 🎟️ Banner de Promoción Moderno */
.promo-banner {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); /* Verde fresco */
  border: 1px solid #10b981;
  border-left: 6px solid #059669; /* Borde grueso a la izquierda */
  border-radius: 10px;
  padding: 16px;
  margin: 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
  flex-wrap: wrap;
  gap: 15px;
}

/* Parte Izquierda: Icono y Texto */
.promo-content {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1; /* Ocupa el espacio disponible */
}

.promo-icon-wrapper {
  background-color: #059669;
  color: white;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 6px rgba(5, 150, 105, 0.3);
}

.promo-text h4 {
  font-size: 1.1rem;
  font-weight: 800;
  color: #065f46;
  margin-bottom: 4px;
}

.promo-text p {
  font-size: 0.95rem;
  color: #374151;
  line-height: 1.3;
  margin: 0;
}

/* Parte Derecha: Código del Cupón */
.promo-code-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end; /* Alinear a la derecha */
  justify-content: center;
}

.code-pill {
  background-color: #ffffff;
  color: #059669;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  border: 2px dashed #34d399; /* Borde punteado estilo cupón */
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.expiry-text {
  margin-top: 5px;
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

/* Animación de entrada */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); /* Rebote suave */
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

/* Responsive para celulares */
@media (max-width: 576px) {
  .promo-banner {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .promo-code-section {
    width: 100%;
    align-items: flex-start; /* En celu alineamos a la izquierda */
    border-top: 1px solid #a7f3d0;
    padding-top: 10px;
    margin-top: 5px;
  }
  
  .code-pill {
    width: 100%;
    justify-content: center;
  }
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
  color: rgb(49, 49, 49);
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

.cupon-alerta-mejorado {
  background-color: #ffffff; /* Fondo blanco explícito */
  border-left: 5px solid #10b981; /* Borde verde a la izquierda para destacar */
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 0; /* El padding lo manejan los hijos */
  margin-top: 20px;
  margin-bottom: 20px;
  overflow: hidden;
  color: #374151; /* Texto gris oscuro (casi negro) para que SE VEA */
}

.cupon-alerta-mejorado .card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #065f46; /* Verde oscuro para el título */
  flex-grow: 1;
}

.badge-descuento {
  background: #10b981;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.cupon-alerta .card-header h3 {
  color: #1f2937 !important;
}

.cupon-alerta p {
  color: #1f2937 !important;
  font-weight: 600;
}

.cupon-alerta strong {
  color: #000000 !important;
  font-weight: 700;
}
.descuento-indicador {
  color: #10b981;
  font-weight: bold;
  margin-left: 10px;
}

.descuento-positivo {
  color: #10b981;
  font-weight: bold;
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

@media (max-width: 1024px) {
  .grid-servicios { grid-template-columns: repeat(2, 1fr); }
  .grid-peluqueros { grid-template-columns: 1fr; }
  .grid-horarios-mejorado { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
  .cliente-datos { grid-template-columns: 1fr; gap: 16px; }
  .cliente-datos p { flex-direction: column; align-items: flex-start; }
  .cliente-datos strong { min-width: auto; margin-bottom: 4px; }
}

@media (max-width: 768px) {
  .page-background { padding: 15px 10px; }
  .main-card-container { padding: 20px; }
  .header-section { flex-direction: column; gap: 15px; padding: 20px; }
  .header-section h2 { font-size: 1.5em; }
  .btn-back { width: 100%; justify-content: center; }
  .card-modern { padding: 18px; }
  .alerta-contenido { flex-direction: column; text-align: center; }
  .grid-servicios { grid-template-columns: 1fr; }
  .grid-horarios-mejorado { grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .hora-card-mejorada { min-height: 95px; padding: 12px 8px; }
  .hora-texto-mejorada { font-size: 1.05rem; }
  .pago-options { grid-template-columns: 1fr; }
  .cliente-datos { grid-template-columns: 1fr; gap: 14px; }
  .cliente-datos p { flex-direction: column; align-items: flex-start; }
  .cliente-datos strong { min-width: auto; margin-bottom: 4px; }
  .calendar-wrapper { padding: 14px; }
  .mes-titulo { font-size: 1em; }
  .calendar-days-header { font-size: 0.75em; }
  .day-btn { font-size: 0.85rem; }
}

@media (max-width: 480px) {
  .page-background { padding: 10px 8px; }
  .main-card-container { padding: 15px; }
  .header-section { padding: 15px; }
  .header-section h2 { font-size: 1.3em; }
  .card-modern { padding: 15px; }
  .card-icon { width: 40px; height: 40px; }
  .card-header h3 { font-size: 1.05em; }
  .grid-horarios-mejorado { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .hora-card-mejorada { padding: 12px 8px; min-height: 90px; }
  .hora-texto-mejorada { font-size: 1rem; }
  .hora-estado-mejorada { font-size: 0.75rem; padding: 4px 8px; }
  .cliente-datos { grid-template-columns: 1fr; gap: 12px; }
  .cliente-datos p { flex-direction: column; align-items: flex-start; gap: 4px; }
  .cliente-datos strong { min-width: auto; }
  .calendar-wrapper { padding: 12px; }
  .calendar-header { margin-bottom: 12px; }
  .btn-nav-cal { width: 36px; height: 36px; min-width: 36px; }
  .mes-titulo { font-size: 0.95em; }
  .calendar-days-header { font-size: 0.7em; gap: 2px; }
  .calendar-grid { gap: 4px; }
  .day-btn { font-size: 0.8rem; border-radius: 6px; }
  .badge-today { font-size: 0.45em; bottom: 1px; }
  .peluquero-avatar { width: 50px; height: 50px; min-width: 50px; font-size: 20px; }
  .peluquero-nombre { font-size: 15px; }
  .toast-message { left: 10px; right: 10px; bottom: 10px; min-width: auto; font-size: 0.9rem; }
  .modal-content { width: 95%; padding: 20px; }
  .modal-actions { flex-direction: column; }
}

@media (max-width: 360px) {
  .page-background { padding: 8px 5px; }
  .main-card-container { padding: 12px; }
  .header-section { padding: 12px; }
  .header-section h2 { font-size: 1.2em; }
  .card-modern { padding: 12px; }
  .grid-horarios-mejorado { grid-template-columns: repeat(2, 1fr); gap: 6px; }
  .hora-card-mejorada { min-height: 85px; padding: 10px 6px; }
  .hora-texto-mejorada { font-size: 0.95rem; }
  .hora-estado-mejorada { font-size: 0.7rem; padding: 3px 6px; }
  .cliente-datos { grid-template-columns: 1fr; gap: 10px; }
  .cliente-datos p { font-size: 0.95rem; }
  .calendar-wrapper { padding: 10px; }
  .mes-titulo { font-size: 0.9em; }
  .btn-nav-cal { width: 32px; height: 32px; min-width: 32px; }
  .calendar-days-header { font-size: 0.65em; }
  .calendar-grid { gap: 3px; }
  .day-btn { font-size: 0.75rem; min-height: 32px; }
  .badge-today { display: none; }
  .peluquero-avatar { width: 45px; height: 45px; min-width: 45px; font-size: 18px; }
}
</style>