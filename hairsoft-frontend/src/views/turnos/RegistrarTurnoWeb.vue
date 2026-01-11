<template>
  <div class="page-background">
    <div class="main-card-container">
      <div class="turno-container">
        
        <!-- HEADER PRINCIPAL -->
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

        <!-- MENSAJE CUANDO SE REDIRIGE A MERCADO PAGO -->
        <div v-if="redirigiendoMercadoPago" class="card-modern alerta-mercado-pago">
          <div class="card-header">
            <div class="card-icon">
              <CheckCircle :size="20" />
            </div>
            <h3> ¡Reserva Creada con Éxito!</h3>
          </div>
          
          <div class="alerta-contenido">
            <div class="alerta-icono-grande">
              <CreditCard :size="48" />
            </div>
            
            <div class="alerta-mensaje">
              <h4>Redirigiendo a Mercado Pago...</h4>
              <p>Tu turno ha sido reservado exitosamente. Por favor, <strong>completa el pago en la nueva pestaña</strong> que se abrirá automáticamente.</p>
              
              <div class="detalles-turno">
                <div class="detalle-item">
                  <CalendarDays :size="16" />
                  <span><strong>Fecha:</strong> {{ formatoFechaLegible(form.fecha) }} a las {{ form.hora }}</span>
                </div>
                <div class="detalle-item">
                  <UserCheck :size="16" />
                  <span><strong>Peluquero:</strong> {{ getPeluqueroNombre() }}</span>
                </div>
                <div class="detalle-item">
                  <Wallet :size="16" />
                  <span><strong>Monto a pagar:</strong> ${{ montoAPagarAhora() }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="alerta-acciones">
            <button @click="irAlListado" class="btn-ver-turnos">
              <span class="btn-content">
                <Calendar :size="18" />
                Ver mis turnos
              </span>
            </button>
            
            <button @click="nuevaReserva" class="btn-nueva-reserva">
              <span class="btn-content">
                <CalendarDays :size="18" />
                Hacer otra reserva
              </span>
            </button>
            
            <p class="nota-pago">
              <Info :size="14" />
              <strong>Nota:</strong> Si la pestaña de Mercado Pago no se abrió, revisa tu navegador 
            </p>
          </div>
        </div>

        <!-- FORMARIO NORMAL (se oculta cuando se redirige) -->
        <div v-if="!redirigiendoMercadoPago">
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

          <!-- 1. DATOS DEL USUARIO -->
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

          <!-- 2. CATEGORÍAS -->
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
                :class="{ 'chip-active': categoriasSeleccionadas.includes(categoria.id) }"
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

          <!-- 3. SERVICIOS (visible si hay categorías seleccionadas) -->
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
              </p>
            </div>
          </div>

          <!-- 4. PELUQUERO (visible si hay servicios seleccionados) -->
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

          <!-- 5. FECHA (visible si hay peluquero seleccionado) -->
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
            
            <div class="calendar-footer">
              <Info :size="16" />
              <span>Rango de reserva: Hoy hasta {{ getFechaMaximaReserva() }} (7 días hábiles)</span>
            </div>
          </div>

          <!-- 6. HORARIOS (visible si hay fecha seleccionada) -->
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
            
            <div v-else-if="horariosDisponibles.length === 0" class="no-resultados">
              <Clock class="no-resultados-icon" :size="48" />
              <p>No hay horarios disponibles para {{ formatoFechaLegible(form.fecha) }}</p>
              <small>Intenta seleccionar otra fecha</small>
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
            
            <p v-if="form.hora" class="hint-text">
              ✅ Horario seleccionado: <strong>{{ form.hora }}</strong>
            </p>
          </div>

          <!-- 7. OPCIONES DE PAGO (visible si hay hora seleccionada) -->
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

          <!-- 8. RESUMEN Y CONFIRMACIÓN -->
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
            
            <!-- BOTÓN QUE LLAMA A MERCADO PAGO -->
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

          <!-- Modal de interés en horarios ocupados -->
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
                    <p>15% de descuento y 1 hora para confirmar.</p>
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
        </div>

        <!-- Toast de mensajes -->
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import Swal from 'sweetalert2'
import { 
  Calendar, ArrowLeft, User, UserCheck, FolderOpen, Tag, 
  Scissors, Check, DollarSign, Clock, CalendarDays, 
  ChevronLeft, ChevronRight, Loader2, Receipt, 
  CheckCircle2, Bell, Banknote, FileText, Inbox, CheckCircle, CreditCard, Wallet,
  Gift, Search, X, AlertCircle, Info
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

// ==========================================
// ESTADO REACTIVO - CORREGIDO
// ==========================================
const form = ref({
  peluquero: "",
  servicios_ids: [],
  hora: "",
  fecha: "",
  tipo_pago: "SENA_50", 
  medio_pago: "MERCADO_PAGO", 
  canal: "WEB",
  cliente: null
})

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

// Estados de carga
const cargandoMercadoPago = ref(false)
const cargandoHorarios = ref(false)
const cargandoDatos = ref(true)
const cargandoServicios = ref(false)

const mostrarModalInteres = ref(false)
const horarioSeleccionadoInteres = ref(null)
const registrandoInteres = ref(false)
const redirigiendoMercadoPago = ref(false) 
const currentDate = ref(new Date())

const intervaloMinutos = 20
const DIAS_RANGO = 7 
const cuponCodigo = ref(null)
const descuentoAplicado = ref(0)
const mensajePromo = ref("")
const horariosInteres = ref([])
const mensaje = ref("")
const mensajeTipo = ref("")

// ==========================================
// 🛡️ LÓGICA DE SELECCIÓN Y FILTROS - CORREGIDO
// ==========================================

// Helper seguro para obtener lista plana
const getListaServicios = () => {
  try {
    if (Array.isArray(servicios.value)) return servicios.value;
    if (servicios.value && Array.isArray(servicios.value.results)) return servicios.value.results;
    if (servicios.value && servicios.value.data && Array.isArray(servicios.value.data)) return servicios.value.data;
    return [];
  } catch (error) {
    console.error('Error en getListaServicios:', error);
    return [];
  }
}

const serviciosFiltrados = computed(() => {
  try {
    let lista = getListaServicios();
    
    // Filtro Categoría
    if (categoriasSeleccionadas.value.length > 0) {
      lista = lista.filter(s => {
        if (!s || !s.categoria) return false;
        
        let catId;
        if (typeof s.categoria === 'object' && s.categoria !== null) {
          catId = String(s.categoria.id || s.categoria);
        } else {
          catId = String(s.categoria);
        }
        
        return categoriasSeleccionadas.value.includes(catId);
      });
    }
    
    // Filtro Búsqueda
    if (busquedaServicio.value.trim()) {
      const term = busquedaServicio.value.toLowerCase().trim();
      lista = lista.filter(s => 
        s && s.nombre && typeof s.nombre === 'string' && s.nombre.toLowerCase().includes(term)
      );
    }
    
    return lista;
  } catch (error) {
    console.error('Error en serviciosFiltrados:', error);
    return [];
  }
});

const toggleCategoria = (id) => {
  try {
    const cid = String(id);
    const index = categoriasSeleccionadas.value.indexOf(cid);
    if (index > -1) {
      categoriasSeleccionadas.value.splice(index, 1);
    } else {
      categoriasSeleccionadas.value.push(cid);
    }
  } catch (error) {
    console.error('Error en toggleCategoria:', error);
  }
}

const toggleServicio = (servicio) => {
  try {
    if (!servicio || !servicio.id) {
      console.error('Servicio inválido en toggleServicio:', servicio);
      return;
    }
    
    const id = String(servicio.id);
    const index = form.value.servicios_ids.indexOf(id);
    
    if (index > -1) {
      // Remover servicio
      form.value.servicios_ids.splice(index, 1);
    } else {
      // Agregar servicio
      form.value.servicios_ids.push(id);
    }
    
    // Resetear horarios si cambian los servicios
    if (form.value.hora) {
      form.value.hora = "";
    }
    
    // Recargar turnos ocupados si hay fecha y peluquero
    if (form.value.fecha && form.value.peluquero) {
      cargarTurnosOcupados(form.value.fecha);
    }
    
    // Forzar actualización de la vista
    nextTick();
  } catch (error) {
    console.error('Error en toggleServicio:', error);
    Swal.fire({
      title: 'Error',
      text: 'No se pudo agregar el servicio. Intenta nuevamente.',
      icon: 'error'
    });
  }
}

const estaServicioSeleccionado = (servicio) => {
  try {
    if (!servicio || !servicio.id) return false;
    return form.value.servicios_ids.includes(String(servicio.id));
  } catch {
    return false;
  }
}

const eliminarServicio = (servicioId) => {
  try {
    const idStr = String(servicioId);
    form.value.servicios_ids = form.value.servicios_ids.filter(id => id !== idStr);
    
    if (form.value.hora) form.value.hora = "";
    if (form.value.fecha && form.value.peluquero) {
      cargarTurnosOcupados(form.value.fecha);
    }
  } catch (error) {
    console.error('Error en eliminarServicio:', error);
  }
}

const formularioValido = computed(() => {
  return (
    form.value.peluquero && 
    form.value.servicios_ids.length > 0 && 
    form.value.fecha && 
    form.value.hora
  );
})

// ==========================================
// 🛡️ CÁLCULOS - MEJORADO CON MANEJO DE ERRORES
// ==========================================

const calcularTotalOriginal = () => {
  try {
    const lista = getListaServicios();
    return form.value.servicios_ids.reduce((acc, id) => {
      const s = lista.find(x => String(x.id) === String(id));
      if (!s) return acc;
      const precio = parseFloat(s.precio) || 0;
      return acc + precio;
    }, 0);
  } catch (error) {
    console.error('Error en calcularTotalOriginal:', error);
    return 0;
  }
}

// ✅ CORRECCIÓN: Esta función NO existe en el template, se usa calcularTotal() 
const calcularTotal = () => {
  return calcularTotalOriginal().toFixed(2);
}

const calcularTotalConDescuento = () => {
  try {
    const total = calcularTotalOriginal();
    const descuento = descuentoAplicado.value || 0;
    const totalConDescuento = total * (1 - descuento / 100);
    return totalConDescuento.toFixed(2);
  } catch (error) {
    console.error('Error en calcularTotalConDescuento:', error);
    return "0.00";
  }
}

const calcularDuracionTotalServicios = () => {
  try {
    const lista = getListaServicios();
    return form.value.servicios_ids.reduce((total, id) => {
      const s = lista.find(x => String(x.id) === String(id));
      if (!s) return total;
      
      // Manejar diferentes nombres de propiedad
      const duracion = s.duracion || s.duracion_minutos || 20;
      return total + parseInt(duracion) || 0;
    }, 0);
  } catch (error) {
    console.error('Error en calcularDuracionTotalServicios:', error);
    return 0;
  }
}

// ✅ CORRECCIÓN: Función para calcular la seña (50%)
const calcularSena = () => {
  const total = parseFloat(calcularTotalConDescuento());
  return (total * 0.5).toFixed(2);
}

// ✅ CORRECCIÓN: Función para calcular monto a pagar ahora
const montoAPagarAhora = () => {
  const total = parseFloat(calcularTotalConDescuento());
  if (form.value.tipo_pago === 'SENA_50') {
    return (total * 0.5).toFixed(2);
  } else {
    return total.toFixed(2);
  }
}

// ==========================================
// API CALLS & HELPERS - MEJORADO
// ==========================================

const getPeluqueroNombre = () => {
  try {
    const lista = Array.isArray(peluqueros.value) 
      ? peluqueros.value 
      : (peluqueros.value?.results || []);
    
    if (!form.value.peluquero || lista.length === 0) return '';
    
    const p = lista.find(x => String(x.id) === String(form.value.peluquero));
    if (!p) return '';
    
    return `${p.nombre || ''} ${p.apellido || ''}`.trim() || p?.username || 'Peluquero';
  } catch {
    return '';
  }
}

// ✅ CORRECCIÓN: Esta función NO existe, se usa en el template
const getServicioNombre = (servicioId) => {
  try {
    const lista = getListaServicios();
    const s = lista.find(s => String(s.id) === String(servicioId));
    return s ? s.nombre : 'Servicio no encontrado';
  } catch (error) {
    console.error('Error en getServicioNombre:', error);
    return 'Servicio no encontrado';
  }
}

const getServiciosNombres = () => {
  try {
    const lista = getListaServicios();
    return form.value.servicios_ids
      .map(id => {
        const s = lista.find(s => String(s.id) === String(id));
        return s?.nombre || '';
      })
      .filter(n => n)
      .join(', ');
  } catch {
    return '';
  }
}

const getNombreCompletoPeluquero = (p) => {
  try {
    if (!p) return '';
    return `${p.nombre || ''} ${p.apellido || ''}`.trim();
  } catch {
    return '';
  }
}

const getInicialesPeluquero = (p) => {
  try {
    return (p?.nombre || 'P').charAt(0).toUpperCase();
  } catch {
    return 'P';
  }
}

const formatoFechaLegible = (f) => {
  try {
    if (!f) return '';
    const date = new Date(f);
    if (isNaN(date.getTime())) return f;
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return f;
  }
}

const getCategoriaNombre = (cat) => {
  try {
    const lista = Array.isArray(categorias.value) 
      ? categorias.value 
      : (categorias.value?.results || []);
    
    if (typeof cat === 'object' && cat !== null) {
      return cat.nombre || 'General';
    }
    
    const c = lista.find(x => String(x.id) === String(cat));
    return c ? c.nombre : 'General';
  } catch {
    return 'General';
  }
}

// ✅ CORRECCIÓN: Función para seleccionar peluquero
const seleccionarPeluquero = (peluqueroId) => {
  form.value.peluquero = peluqueroId;
  onPeluqueroSeleccionado();
}

const onPeluqueroSeleccionado = () => {
  form.value.fecha = "";
  form.value.hora = "";
  slotsOcupadosReales.value = [];
}

// ✅ CORRECCIÓN: Funciones para el calendario
const nombreMesActual = computed(() => {
  const meses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];
  return meses[currentDate.value.getMonth()];
});

const currentYear = computed(() => {
  return currentDate.value.getFullYear();
});

const startingDayOfWeek = computed(() => {
  const firstDay = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1);
  return firstDay.getDay(); // 0 = Domingo, 1 = Lunes, etc.
});

const daysInMonth = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  return new Date(year, month + 1, 0).getDate();
});

const esHoy = (day) => {
  const hoy = new Date();
  const selectedDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day);
  return hoy.toDateString() === selectedDate.toDateString();
};

const esDiaSeleccionado = (day) => {
  if (!form.value.fecha) return false;
  const selectedDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day);
  const fechaForm = new Date(form.value.fecha);
  return selectedDate.toDateString() === fechaForm.toDateString();
};

const esDiaSeleccionable = (day) => {
  const selectedDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day);
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  
  // No permitir días pasados
  if (selectedDate < hoy) return false;
  
  // Limitar a 7 días en el futuro
  const maxDate = new Date();
  maxDate.setDate(hoy.getDate() + DIAS_RANGO);
  return selectedDate <= maxDate;
};

const seleccionarDiaCalendario = (day) => {
  const year = currentDate.value.getFullYear();
  const month = String(currentDate.value.getMonth() + 1).padStart(2, '0');
  const dayStr = String(day).padStart(2, '0');
  form.value.fecha = `${year}-${month}-${dayStr}`;
};

const cambiarMes = (delta) => {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(newDate.getMonth() + delta);
  currentDate.value = newDate;
};

// ✅ CORRECCIÓN: Función para obtener fecha máxima de reserva
const getFechaMaximaReserva = () => {
  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + DIAS_RANGO);
  return maxDate.toLocaleDateString('es-ES');
};

// ✅ CORRECCIÓN: Función para filtrar servicios (usada en el template)
const filtrarServicios = () => {
  // Esta función se llama desde el input, pero ya tenemos serviciosFiltrados computed
  // Solo necesitamos actualizar la búsqueda
  nextTick();
};

// ✅ CORRECCIÓN: Función para obtener horarios ocupados para mostrar
const horariosOcupadosParaMostrar = computed(() => {
  const horariosBase = [
    '08:00','08:20','08:40','09:00','09:20','09:40',
    '10:00','10:20','10:40','11:00','11:20','11:40',
    '15:00','15:20','15:40','16:00','16:20','16:40',
    '17:00','17:20','17:40','18:00','18:20','18:40',
    '19:00','19:20','19:40','20:00'
  ];
  
  return horariosBase.filter(h => !esHorarioDisponible(h));
});

// ✅ CORRECCIÓN: Función para verificar si ya se registró interés
const estaInteresRegistrado = (hora) => {
  return horariosInteres.value.some(h => h.hora === hora && h.fecha === form.value.fecha);
};

// ✅ CORRECCIÓN: Función para registrar interés en horario
const registrarInteresHorario = (hora) => {
  horarioSeleccionadoInteres.value = hora;
  mostrarModalInteres.value = true;
};

// ✅ CORRECCIÓN: Función para cancelar registro de interés
const cancelarRegistroInteres = () => {
  mostrarModalInteres.value = false;
  horarioSeleccionadoInteres.value = null;
};

const cargarDatosIniciales = async () => {
  cargandoDatos.value = true;
  
  try {
    // Verificar si hay usuario autenticado
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('user_id');
    
    if (!token || !userId) {
      usuario.value.isAuthenticated = false;
      // Redirigir a login si no está autenticado
      Swal.fire({
        title: 'Sesión requerida',
        text: 'Debes iniciar sesión para agendar un turno',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ir a login',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          router.push('/login');
        } else {
          router.back();
        }
      });
      return;
    }
    
    usuario.value.isAuthenticated = true;
    
    // Cargar datos del usuario
    if (userId) {
      const resU = await api.get(`/usuarios/${userId}/`);
      usuario.value = { ...resU.data, isAuthenticated: true };
      form.value.cliente = userId;
    }
    
    // Cargar peluqueros, servicios y categorías en paralelo
    const [p, s, c] = await Promise.all([
      api.get('/peluqueros/').catch(e => {
        console.error('Error cargando peluqueros:', e);
        return { data: [] };
      }),
      api.get('/servicios/').catch(e => {
        console.error('Error cargando servicios:', e);
        return { data: [] };
      }),
      api.get('/categorias/servicios/').catch(e => {
        console.error('Error cargando categorías:', e);
        return { data: [] };
      })
    ]);
    
    // Normalización de datos
    peluqueros.value = Array.isArray(p.data) ? p.data : (p.data?.results || []);
    servicios.value = Array.isArray(s.data) ? s.data : (s.data?.results || []);
    categorias.value = Array.isArray(c.data) ? c.data : (c.data?.results || []);
    
    console.log('Datos cargados:', {
      peluqueros: peluqueros.value.length,
      servicios: servicios.value.length,
      categorias: categorias.value.length
    });
    
  } catch (error) {
    console.error('Error en carga inicial:', error);
    Swal.fire({
      title: 'Error',
      text: 'No se pudieron cargar los datos. Por favor, recarga la página.',
      icon: 'error',
      confirmButtonText: 'Recargar'
    }).then(() => {
      window.location.reload();
    });
  } finally {
    cargandoDatos.value = false;
  }
}

const cargarTurnosOcupados = async (fecha) => {
  if (!form.value.peluquero) return;
  
  cargandoHorarios.value = true;
  try {
    const res = await api.get(
      `/turnos/?fecha=${fecha}&peluquero=${form.value.peluquero}&estado__in=RESERVADO,CONFIRMADO`
    );
    
    const turnos = Array.isArray(res.data) ? res.data : (res.data?.results || []);
    const ocupadosSet = new Set();
    
    turnos.forEach(turno => {
      if (!turno.hora) return;
      const [h, m] = turno.hora.split(':').map(Number);
      const inicioMin = h * 60 + m;
      const dur = turno.duracion_total || 20;
      
      for (let i = inicioMin; i < inicioMin + dur; i += 20) {
        ocupadosSet.add(
          `${Math.floor(i / 60).toString().padStart(2, '0')}:${(i % 60).toString().padStart(2, '0')}`
        );
      }
    });
    
    slotsOcupadosReales.value = Array.from(ocupadosSet);
  } catch (error) {
    console.error('Error cargando turnos ocupados:', error);
    slotsOcupadosReales.value = [];
  } finally {
    cargandoHorarios.value = false;
  }
}

// ==========================================
// MERCADO PAGO - MEJORADO
// ==========================================

const crearPagoMercadoPago = async () => {
  if (!formularioValido.value) {
    Swal.fire({
      title: 'Formulario incompleto',
      text: 'Por favor, completa todos los campos requeridos',
      icon: 'warning'
    });
    return;
  }
  
  // Verificar autenticación
  if (!usuario.value.isAuthenticated) {
    Swal.fire({
      title: 'Sesión requerida',
      text: 'Debes iniciar sesión para continuar',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Ir a login',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        router.push('/login');
      }
    });
    return;
  }
  
  cargandoMercadoPago.value = true;
  
  try {
    const total = parseFloat(calcularTotalConDescuento());
    const payload = {
      peluquero_id: form.value.peluquero,
      cliente_id: usuario.value.id,
      servicios_ids: form.value.servicios_ids,
      fecha: form.value.fecha,
      hora: form.value.hora,
      canal: 'WEB',
      tipo_pago: form.value.tipo_pago,
      medio_pago: 'MERCADO_PAGO',
      monto_total: total,
      monto_seña: form.value.tipo_pago === 'SENA_50' ? (total * 0.5).toFixed(2) : 0,
      duracion_total: calcularDuracionTotalServicios(),
      cup_codigo: cuponCodigo.value
    };
    
    console.log('Enviando payload a MercadoPago:', payload);
    
    const res = await api.post('/turnos/crear/', payload);
    
    if (res.data && (res.data.mp_data?.init_point || res.data.init_point)) {
      const mpUrl = res.data.mp_data?.init_point || res.data.init_point;
      redirigiendoMercadoPago.value = true;
      
      // Pequeño delay para mostrar feedback al usuario
      setTimeout(() => {
        window.location.href = mpUrl;
      }, 500);
    } else {
      throw new Error('No se recibió URL de pago');
    }
    
  } catch (error) {
    console.error('Error en MercadoPago:', error);
    
    let errorMessage = 'Error al crear el turno. Por favor, intenta nuevamente.';
    
    if (error.response) {
      if (error.response.status === 400) {
        errorMessage = error.response.data?.message || 'Datos inválidos. Verifica la información.';
      } else if (error.response.status === 401) {
        errorMessage = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        router.push('/login');
      }
    }
    
    Swal.fire({
      title: 'Error',
      text: errorMessage,
      icon: 'error',
      confirmButtonText: 'Entendido'
    });
  } finally {
    cargandoMercadoPago.value = false;
  }
}

// ==========================================
// DISPONIBILIDAD HORARIA - MEJORADO
// ==========================================

const esHorarioDisponible = (h) => {
  try {
    if (!form.value.fecha || !form.value.peluquero) return true;
    
    // Verificar si está ocupado
    if (slotsOcupadosReales.value.includes(h.substring(0, 5))) return false;
    
    // Validación de horario pasado para "hoy"
    const hoy = new Date();
    const hoyF = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`;
    
    if (form.value.fecha === hoyF) {
      const [hS, mS] = h.substring(0, 5).split(':').map(Number);
      const ahora = hoy.getHours() * 60 + hoy.getMinutes();
      const horarioSeleccionado = hS * 60 + mS;
      
      // Agregar margen de 30 minutos para el futuro
      return horarioSeleccionado > (ahora + 30);
    }
    
    return true;
  } catch {
    return false;
  }
}

const horariosDisponibles = computed(() => {
  const horariosBase = [
    '08:00','08:20','08:40','09:00','09:20','09:40',
    '10:00','10:20','10:40','11:00','11:20','11:40',
    '15:00','15:20','15:40','16:00','16:20','16:40',
    '17:00','17:20','17:40','18:00','18:20','18:40',
    '19:00','19:20','19:40','20:00'
  ];
  
  return horariosBase.filter(h => esHorarioDisponible(h));
});

const seleccionarHora = (h) => {
  if (esHorarioDisponible(h)) {
    form.value.hora = h;
  }
}

// ==========================================
// INTERÉS Y CUPONES - MEJORADO
// ==========================================

const confirmarRegistroInteres = async () => {
  if (!form.value.peluquero || !form.value.fecha || !horarioSeleccionadoInteres.value) {
    Swal.fire({
      title: 'Error',
      text: 'Faltan datos para registrar el interés',
      icon: 'error'
    });
    return;
  }
  
  registrandoInteres.value = true;
  
  try {
    await api.post('/turnos/registrar-interes/', {
      fecha: form.value.fecha,
      hora: horarioSeleccionadoInteres.value,
      peluquero_id: form.value.peluquero,
      cliente_id: usuario.value.id,
      servicios_ids: form.value.servicios_ids,
      interes_notificacion: true
    });
    
    Swal.fire({
      title: '¡Interés registrado!',
      text: 'Te notificaremos cuando se libere este horario.',
      icon: 'success',
      timer: 3000
    });
    
    mostrarModalInteres.value = false;
    horarioSeleccionadoInteres.value = null;
  } catch (error) {
    console.error('Error registrando interés:', error);
    Swal.fire({
      title: 'Error',
      text: 'No se pudo registrar tu interés. Intenta nuevamente.',
      icon: 'error'
    });
  } finally {
    registrandoInteres.value = false;
  }
}

// ==========================================
// FUNCIONES DE NAVEGACIÓN - CORREGIDAS
// ==========================================

const volverAlListado = () => {
  router.back();
};

const irAlListado = () => {
  router.push('/cliente/historial');
};

const nuevaReserva = () => {
  window.location.reload();
};

const volverAtras = () => {
  router.back();
};

const irAServicios = () => {
  router.push('/servicios');
};

// ==========================================
// LIFECYCLE & WATCHERS
// ==========================================

onMounted(() => {
  console.log('Componente RegistrarTurnoWeb montado');
  cargarDatosIniciales();
});

watch(() => form.value.fecha, (newFecha) => {
  if (newFecha && form.value.peluquero) {
    cargarTurnosOcupados(newFecha);
  }
});

watch(() => form.value.peluquero, (newPeluquero) => {
  if (newPeluquero && form.value.fecha) {
    cargarTurnosOcupados(form.value.fecha);
  }
});

// ==========================================
// EXPORTAR FUNCIONES
// ==========================================

defineExpose({
  form,
  usuario,
  serviciosFiltrados,
  toggleServicio,
  estaServicioSeleccionado,
  eliminarServicio,
  crearPagoMercadoPago,
  volverAtras,
  irAServicios
});
</script>

<style scoped>
/* ============================================
   ESTILOS MEJORADOS RESPONSIVE - MOBILE FIRST
   Optimizado para verse perfecto en celulares
   ============================================ */

/* ============================================
   BASE Y VARIABLES
   ============================================ */
:root {
  --primary: #3b82f6;
  --primary-dark: #1d4ed8;
  --success: #10b981;
  --warning: #f59e0b;
  --error: #dc2626;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
}

/* ============================================
   CONTENEDOR PRINCIPAL - MOBILE FIRST
   ============================================ */
.page-background {
  min-height: 100vh;
  padding: var(--spacing-md);
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.main-card-container {
  background: white;
  border-radius: var(--spacing-md);
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: var(--spacing-md);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--gray-200);
}

.turno-container {
  width: 100%;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* ============================================
   HEADER - OPTIMIZADO MOBILE
   ============================================ */
.header-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, #1f2937, #374151);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

.header-section h2 {
  margin: 0;
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  line-height: 1.3;
}

.header-icon { 
  color: #60a5fa;
  flex-shrink: 0;
}

.btn-back {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  backdrop-filter: blur(10px);
  width: 100%;
}

.btn-back:hover, .btn-back:active { 
  background: rgba(255, 255, 255, 0.2); 
  border-color: rgba(255, 255, 255, 0.3);
  transform: scale(0.98);
}

/* ============================================
   CARDS - MOBILE OPTIMIZED
   ============================================ */
.card-modern {
  background: #fff;
  border-radius: var(--radius-md);
  border: 1px solid var(--gray-200);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.card-modern:active {
  transform: scale(0.99);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--gray-100);
  flex-wrap: wrap;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border-radius: var(--radius-md);
  color: white;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
}

.card-header h3 {
  margin: 0;
  color: var(--gray-800);
  font-size: 1.1rem;
  font-weight: 700;
  flex: 1;
  min-width: 0;
}

.badge-count {
  background: var(--success);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
  white-space: nowrap;
}

/* ============================================
   ALERTA MERCADO PAGO - MOBILE
   ============================================ */
.alerta-mercado-pago {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 2px solid #2196f3;
  animation: pulse-alerta 2s infinite;
  margin-bottom: var(--spacing-lg);
}

@keyframes pulse-alerta {
  0%, 100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(33, 150, 243, 0); }
}

.alerta-contenido {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;
  text-align: center;
}

.alerta-icono-grande {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #2196f3, #0d47a1);
  border-radius: 50%;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 6px 20px rgba(33, 150, 243, 0.3);
}

.alerta-mensaje {
  width: 100%;
}

.alerta-mensaje h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: #1565c0;
  font-size: 1.2rem;
  font-weight: 700;
}

.alerta-mensaje p {
  margin: 0 0 var(--spacing-md) 0;
  color: #37474f;
  font-size: 0.95rem;
  line-height: 1.5;
}

.detalles-turno {
  background: rgba(255, 255, 255, 0.9);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  border: 1px solid rgba(33, 150, 243, 0.2);
}

.detalle-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) 0;
  color: #455a64;
  font-size: 0.9rem;
}

.detalle-item svg {
  color: #2196f3;
  flex-shrink: 0;
  margin-top: 2px;
}

.detalle-item strong {
  color: #1565c0;
  margin-right: 4px;
}

.alerta-acciones {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 2px solid rgba(33, 150, 243, 0.2);
}

.btn-ver-turnos,
.btn-nueva-reserva {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.btn-ver-turnos {
  background: linear-gradient(135deg, #2196f3, #0d47a1);
  color: white;
}

.btn-ver-turnos:active {
  background: linear-gradient(135deg, #0d47a1, #08306b);
  transform: scale(0.98);
}

.btn-nueva-reserva {
  background: white;
  color: #2196f3;
  border: 2px solid #2196f3;
}

.btn-nueva-reserva:active {
  background: #e3f2fd;
  transform: scale(0.98);
}

.nota-pago {
  text-align: center;
  color: #546e7a;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  background: var(--gray-100);
  border-radius: var(--radius-sm);
  margin: 0;
}

/* ============================================
   CUPÓN ALERTA
   ============================================ */
.cupon-alerta {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 2px solid var(--warning);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
}

/* ============================================
   DATOS DEL CLIENTE
   ============================================ */
.cliente-info-card {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 2px solid var(--gray-200);
}

.cliente-datos {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.cliente-datos p {
  margin: 0;
  color: var(--gray-600);
  font-size: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--spacing-xs);
  background: white;
  border-radius: var(--radius-sm);
}

.cliente-datos strong {
  color: var(--gray-800);
  font-weight: 700;
  display: block;
}

/* ============================================
   INPUTS Y SELECTS
   ============================================ */
.input-modern, .select-modern {
  width: 100%;
  padding: var(--spacing-sm);
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-md);
  background: var(--gray-50);
  font-size: 1rem;
  transition: all 0.3s ease;
  color: var(--gray-800);
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.input-modern:focus, .select-modern:focus {
  border-color: var(--primary);
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.select-modern {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--spacing-sm) center;
  background-size: 20px;
  padding-right: 40px;
  cursor: pointer;
}

/* ============================================
   BÚSQUEDA SERVICIOS
   ============================================ */
.busqueda-servicios {
  margin-bottom: var(--spacing-md);
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: var(--spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  color: var(--gray-600);
  pointer-events: none;
}

.busqueda-servicios .input-modern {
  padding-left: 40px;
}

/* ============================================
   CHIPS - CATEGORÍAS
   ============================================ */
.grid-chips { 
  display: flex; 
  flex-wrap: wrap; 
  gap: var(--spacing-xs); 
}

.chip-modern {
  background: #fff; 
  border: 2px solid var(--gray-200); 
  padding: var(--spacing-sm) var(--spacing-md); 
  border-radius: 50px;
  color: var(--gray-600); 
  cursor: pointer; 
  font-weight: 600; 
  display: flex; 
  align-items: center; 
  gap: var(--spacing-xs);
  transition: all 0.3s ease;
  font-size: 0.9rem;
  white-space: nowrap;
}

.chip-modern:active { 
  transform: scale(0.95);
}

.chip-active { 
  background: linear-gradient(135deg, var(--primary), var(--primary-dark)); 
  color: white; 
  border-color: var(--primary); 
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

/* ============================================
   SERVICIOS - GRID MOBILE
   ============================================ */
.grid-servicios { 
  display: grid; 
  grid-template-columns: 1fr;
  gap: var(--spacing-sm); 
  margin-top: var(--spacing-md);
}

.card-servicio { 
  background: #fff; 
  border: 2px solid var(--gray-200); 
  border-radius: var(--radius-md); 
  padding: var(--spacing-md); 
  cursor: pointer; 
  position: relative; 
  transition: all 0.3s ease;
}

.card-servicio:active { 
  transform: scale(0.98);
}

.servicio-active { 
  border-color: var(--success); 
  background: #f0fdf4; 
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.servicio-check { 
  position: absolute; 
  top: var(--spacing-sm); 
  right: var(--spacing-sm); 
  width: 24px;
  height: 24px;
  background: var(--success);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.servicio-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding-right: 30px;
}

.servicio-nombre { 
  font-weight: 700; 
  color: var(--gray-800); 
  display: block;
  font-size: 1rem;
  line-height: 1.3;
}

.servicio-details { 
  display: flex; 
  justify-content: space-between; 
  align-items: center;
  color: var(--gray-600); 
  font-size: 0.9rem;
  gap: var(--spacing-sm);
}

.servicio-precio { 
  color: #059669; 
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

.servicio-duracion {
  color: var(--gray-600);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.servicio-categoria {
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px var(--spacing-sm);
  border-radius: 12px;
  font-size: 0.8rem;
  align-self: flex-start;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* ============================================
   NO RESULTADOS
   ============================================ */
.no-resultados {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
  color: var(--gray-600);
}

.no-resultados-icon {
  opacity: 0.4;
  margin-bottom: var(--spacing-md);
  color: var(--gray-300);
}

.no-resultados p {
  margin: var(--spacing-xs) 0;
  font-size: 1rem;
}

.no-resultados small {
  font-size: 0.85rem;
  color: var(--gray-600);
}

/* ============================================
   PELUQUEROS - MOBILE OPTIMIZED
   ============================================ */
.grid-peluqueros {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.card-peluquero {
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  position: relative;
  background: white;
}

.card-peluquero:active {
  transform: scale(0.98);
}

.peluquero-active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.peluquero-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.peluquero-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.peluquero-nombre {
  font-weight: 700;
  color: #333;
  font-size: 1rem;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.peluquero-experiencia {
  font-size: 0.8rem;
  color: #666;
  background: var(--gray-100);
  padding: 2px var(--spacing-xs);
  border-radius: 12px;
  align-self: flex-start;
  white-space: nowrap;
}

.peluquero-selected {
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
  flex-shrink: 0;
}

/* ============================================
   CALENDARIO - MOBILE OPTIMIZED
   ============================================ */
.calendar-wrapper { 
  background: var(--gray-50); 
  border-radius: var(--radius-md); 
  padding: var(--spacing-md); 
  border: 2px solid var(--gray-200); 
}

.calendar-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: var(--spacing-md); 
  gap: var(--spacing-sm);
}

.mes-titulo { 
  font-weight: 700; 
  font-size: 1rem; 
  color: var(--gray-800);
  text-align: center;
  flex: 1;
}

.btn-nav-cal { 
  background: white; 
  border: 1px solid var(--gray-200); 
  border-radius: var(--radius-sm); 
  width: 36px; 
  height: 36px; 
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-nav-cal:active { 
  background: var(--gray-100); 
  transform: scale(0.95);
}

.calendar-days-header { 
  display: grid; 
  grid-template-columns: repeat(7, 1fr); 
  text-align: center; 
  font-weight: 700; 
  color: var(--gray-600); 
  margin-bottom: var(--spacing-sm); 
  font-size: 0.75rem; 
  gap: 2px;
}

.calendar-grid { 
  display: grid; 
  grid-template-columns: repeat(7, 1fr); 
  gap: 4px; 
}

.day-empty {
  aspect-ratio: 1;
}

.day-btn {
  aspect-ratio: 1; 
  border-radius: var(--radius-sm); 
  border: 2px solid transparent; 
  background: rgb(72, 255, 130); 
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  position: relative;
  transition: all 0.2s;
  color: var(--gray-800);
  min-height: 36px;
}

.day-btn:active:not(:disabled) { 
  transform: scale(0.95);
}

.day-selected { 
  background: var(--primary) !important; 
  color: white !important; 
  border-color: var(--primary) !important;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.day-today { 
  border-color: var(--warning); 
  background: #fef3c7;
  font-weight: 700;
}

.badge-today { 
  position: absolute; 
  bottom: 2px; 
  font-size: 0.5rem; 
  color: #d97706; 
  font-weight: 800; 
}

.day-disabled { 
  background: #d1d5db; 
  color: #ffffff; 
  cursor: not-allowed; 
  opacity: 0.6;
}

.calendar-footer { 
  text-align: center; 
  margin-top: var(--spacing-md); 
  font-size: 0.8rem; 
  color: var(--gray-600); 
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  background: #fef3c7;
  border-radius: var(--radius-sm);
  line-height: 1.4;
}

/* ============================================
   HORARIOS - MOBILE OPTIMIZED
   ============================================ */
.grid-horarios-mejorado {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-xs);
}

.hora-card-mejorada {
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
  cursor: pointer;
  text-align: center;
  font-weight: 600;
  background: white;
  transition: all 0.3s ease;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hora-card-mejorada:active:not(.hora-ocupada-mejorada) {
  transform: scale(0.95);
}

.hora-selected-mejorada {
  border-color: var(--primary);
  background: #eff6ff;
  box-shadow: 0 0 0 2px var(--primary);
}

.hora-ocupada-mejorada {
  background: #fef2f2;
  border-color: #fee2e2;
  cursor: not-allowed;
  opacity: 0.8;
}

.hora-content-mejorada {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  align-items: center;
}

.hora-info-mejorada {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.hora-icon-mejorada {
  color: var(--gray-600);
}

.hora-texto-mejorada {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--gray-800);
}

.hora-duracion-badge-ocupado {
  background: #fef2f2;
  color: var(--error);
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 0.7rem;
  white-space: nowrap;
}

.hora-estado-mejorada {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 6px;
}

.hora-estado-mejorada.disponible {
  background: #f0fdf4;
  color: #059669;
}

.btn-avisar-liberado-mejorada {
  width: 100%;
  margin-top: var(--spacing-xs);
  padding: 6px;
  background: linear-gradient(135deg, var(--warning), #d97706);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.btn-avisar-liberado-mejorada:active:not(:disabled) {
  background: linear-gradient(135deg, #d97706, #b45309);
  transform: scale(0.95);
}

.btn-avisar-liberado-mejorada:disabled {
  background: var(--gray-300);
  cursor: not-allowed;
  opacity: 0.7;
}

/* ============================================
   HINT TEXT
   ============================================ */
.hint-text {
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: #f0f9ff;
  border-radius: var(--radius-sm);
  color: #0369a1;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

/* ============================================
   SERVICIOS SELECCIONADOS
   ============================================ */
.servicios-seleccionados {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--gray-50);
  border-radius: var(--radius-md);
  border: 1px solid var(--gray-200);
}

.servicios-seleccionados h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--gray-800);
  font-size: 0.95rem;
}

.servicios-lista {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.servicio-tag {
  background: #e0f2fe;
  color: #0369a1;
  padding: 6px var(--spacing-sm);
  border-radius: 16px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
}

.servicio-tag span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  flex-shrink: 0;
}

.btn-eliminar-servicio:active {
  background: #bae6fd;
}

.total-parcial {
  margin: 0;
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--gray-200);
  color: var(--gray-800);
  font-size: 0.9rem;
  text-align: right;
}

.total-parcial strong {
  color: #059669;
  font-size: 1.1rem;
}

/* ============================================
   PAGO
   ============================================ */
.pago-section {
  margin-bottom: var(--spacing-md);
}

.label-modern {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--gray-800);
  font-size: 0.95rem;
}

.pago-options {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.radio-box {
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  cursor: pointer;
  color: var(--gray-800);
  text-align: center;
  transition: all 0.3s ease;
}

.radio-box:active {
  transform: scale(0.98);
}

.radio-active {
  border-color: var(--primary);
  background: #eff6ff;
}

.hidden-radio {
  display: none;
}

.radio-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.radio-content span {
  font-weight: 600;
  font-size: 0.95rem;
}

.radio-content strong {
  font-size: 1.2rem;
  color: #059669;
}

.radio-content small {
  color: var(--gray-600);
  font-size: 0.8rem;
}

.medio-pago-box {
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  background: white;
}

.medio-pago-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  justify-content: center;
}

.medio-icon {
  font-size: 1.5rem;
}

.medio-text {
  font-weight: 600;
  color: var(--gray-800);
}

/* ============================================
   RESUMEN FINAL
   ============================================ */
.resumen-final {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border: 2px solid var(--gray-200);
}

.resumen-detalles {
  background: white;
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--gray-200);
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--gray-200);
  color: var(--gray-800);
  font-size: 0.9rem;
  gap: var(--spacing-sm);
}

.resumen-item span:first-child {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  flex-shrink: 0;
}

.resumen-item span:last-child {
  text-align: right;
  word-break: break-word;
}

.resumen-item:last-child {
  border-bottom: none;
}

.resumen-item.total {
  border-top: 2px solid var(--gray-200);
  padding-top: var(--spacing-md);
  margin-top: var(--spacing-sm);
  font-size: 1rem;
  font-weight: 700;
}

.monto-final-pago {
  font-size: 1.3rem;
  color: #059669;
  font-weight: 700;
}

.btn-confirmar-premium {
  width: 100%;
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  padding: var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  position: relative;
  overflow: hidden;
  min-height: 52px;
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

.btn-confirmar-premium:active:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: scale(0.98);
}

.btn-confirmar-premium:active::before {
  left: 100%;
}

.btn-confirmar-premium:disabled {
  background: var(--gray-300);
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.info-pago-final {
  text-align: center;
  color: var(--gray-600);
  margin-top: var(--spacing-md);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  line-height: 1.4;
  padding: 0 var(--spacing-sm);
}

/* ============================================
   LOADING
   ============================================ */
.loading-spinner {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
  color: var(--gray-600);
}

.spinner-icon {
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
  color: var(--primary);
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

/* ============================================
   MODAL - MOBILE OPTIMIZED
   ============================================ */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-md);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
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
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--gray-200);
}

.modal-header h3 {
  margin: 0;
  color: var(--gray-800);
  font-size: 1.2rem;
}

.modal-close-btn {
  background: var(--gray-100);
  border: 1px solid var(--gray-300);
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.modal-close-btn:active {
  background: var(--gray-200);
  transform: scale(0.95);
}

.info-interes-card {
  background: var(--gray-50);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.info-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
  font-size: 0.9rem;
}

.info-details p {
  margin: 0;
  color: var(--gray-800);
  padding: 6px 0;
}

.beneficio-descuento {
  background: linear-gradient(135deg, #6db0f8, #667ffb);
  border-radius: var(--radius-sm);
  padding: var(--spacing-sm);
  text-align: center;
  font-size: 0.85rem;
  color: white;
}

.beneficio-descuento strong {
  display: block;
  margin-bottom: 4px;
  font-size: 0.95rem;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.btn-confirmar-interes,
.btn-cancelar-interes {
  width: 100%;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-confirmar-interes {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  border: none;
}

.btn-confirmar-interes:active:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: scale(0.98);
}

.btn-confirmar-interes:disabled {
  background: var(--gray-300);
  cursor: not-allowed;
}

.btn-cancelar-interes {
  background: var(--gray-100);
  color: var(--gray-600);
  border: 1px solid var(--gray-300);
}

.btn-cancelar-interes:active {
  background: var(--gray-200);
  transform: scale(0.98);
}

/* ============================================
   TOAST
   ============================================ */
.toast-message {
  position: fixed;
  bottom: var(--spacing-md);
  left: var(--spacing-md);
  right: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  z-index: 9999;
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(10px);
  animation: slideInUp 0.3s ease;
}

@keyframes slideInUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.toast-message.success {
  background: rgba(16, 185, 129, 0.95);
  color: white;
  border-left: 4px solid #059669;
}

.toast-message.error {
  background: rgba(239, 68, 68, 0.95);
  color: white;
  border-left: 4px solid var(--error);
}

/* ============================================
   ANIMACIONES
   ============================================ */
.slide-enter-active, .slide-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.slide-enter-from, .slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-in {
  animation: slideInRight 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideInRight {
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* ============================================
   TABLETS (768px - 1024px)
   ============================================ */
@media (min-width: 768px) {
  .main-card-container {
    padding: var(--spacing-xl);
    max-width: 800px;
    border-radius: var(--radius-xl);
  }

  .header-section {
    flex-direction: row;
    align-items: center;
    padding: var(--spacing-lg);
  }

  .header-section h2 {
    font-size: 1.5rem;
  }

  .btn-back {
    width: auto;
  }

  .alerta-contenido {
    flex-direction: row;
    text-align: left;
    gap: var(--spacing-lg);
  }

  .alerta-icono-grande {
    width: 70px;
    height: 70px;
  }

  .card-icon {
    width: 44px;
    height: 44px;
  }

  .card-header h3 {
    font-size: 1.2rem;
  }

  .cliente-datos {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }

  .cliente-datos p {
    flex-direction: row;
    align-items: center;
  }

  .cliente-datos strong {
    min-width: 120px;
  }

  .grid-servicios {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }

  .grid-peluqueros {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }

  .peluquero-avatar {
    width: 55px;
    height: 55px;
    font-size: 22px;
  }

  .calendar-grid {
    gap: 6px;
  }

  .day-btn {
    font-size: 0.9rem;
    min-height: 40px;
  }

  .grid-horarios-mejorado {
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-sm);
  }

  .pago-options {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }

  .resumen-item {
    font-size: 0.95rem;
  }

  .toast-message {
    left: auto;
    right: var(--spacing-lg);
    min-width: 350px;
  }

  .modal-content {
    padding: var(--spacing-xl);
  }
}

/* ============================================
   DESKTOP (1024px+)
   ============================================ */
@media (min-width: 1024px) {
  .page-background {
    padding: var(--spacing-xl);
  }

  .main-card-container {
    max-width: 1200px;
    padding: 40px;
  }

  .header-section h2 {
    font-size: 1.8rem;
  }

  .alerta-icono-grande {
    width: 80px;
    height: 80px;
  }

  .card-modern:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
  }

  .card-icon {
    width: 48px;
    height: 48px;
  }

  .card-header h3 {
    font-size: 1.3rem;
  }

  .chip-modern:hover {
    border-color: var(--primary);
    color: var(--primary);
    transform: translateY(-2px);
  }

  .grid-servicios {
    grid-template-columns: repeat(3, 1fr);
  }

  .card-servicio:hover {
    border-color: var(--primary);
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
  }

  .grid-peluqueros {
    grid-template-columns: repeat(2, 1fr);
  }

  .card-peluquero:hover {
    border-color: #667eea;
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
  }

  .peluquero-avatar {
    width: 60px;
    height: 60px;
    font-size: 24px;
  }

  .calendar-grid {
    gap: 10px;
  }

  .day-btn {
    font-size: 1rem;
    min-height: 44px;
  }

  .day-btn:hover:not(:disabled) {
    border-color: var(--primary);
    transform: translateY(-1px);
  }

  .grid-horarios-mejorado {
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-md);
  }

  .hora-card-mejorada:hover:not(.hora-ocupada-mejorada) {
    border-color: var(--primary);
    transform: translateY(-2px);
  }

  .btn-confirmar-premium:hover:not(:disabled) {
    background: linear-gradient(135deg, #047857, #065f46);
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(5, 150, 105, 0.4);
  }

  .btn-confirmar-premium:hover::before {
    left: 100%;
  }

  .radio-box:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
  }

  .modal-content {
    max-width: 550px;
  }

  .modal-actions {
    flex-direction: row;
  }
}

/* ============================================
   LANDSCAPE MOBILE
   ============================================ */
@media (max-width: 767px) and (orientation: landscape) {
  .modal-content {
    max-height: 80vh;
  }

  .calendar-grid {
    gap: 3px;
  }

  .day-btn {
    min-height: 32px;
    font-size: 0.8rem;
  }
}

/* ============================================
   ACCESIBILIDAD
   ============================================ */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* ============================================
   DARK MODE SUPPORT (opcional)
   ============================================ */
@media (prefers-color-scheme: dark) {
  /* Aquí puedes agregar estilos dark mode si lo deseas */
}

/* ============================================
   UTILIDADES
   ============================================ */
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-left { text-align: left; }
.mt-1 { margin-top: var(--spacing-xs); }
.mt-2 { margin-top: var(--spacing-sm); }
.mt-3 { margin-top: var(--spacing-md); }
.mb-1 { margin-bottom: var(--spacing-xs); }
.mb-2 { margin-bottom: var(--spacing-sm); }
.mb-3 { margin-bottom: var(--spacing-md); }
.p-1 { padding: var(--spacing-xs); }
.p-2 { padding: var(--spacing-sm); }
.p-3 { padding: var(--spacing-md); }

/* ============================================
   FIX PARA OVERFLOW EN MOBILE
   ============================================ */
* {
  -webkit-tap-highlight-color: transparent;
}

html {
  overflow-x: hidden;
}

body {
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Prevenir zoom en inputs en iOS */
@media screen and (max-width: 767px) {
  input[type="text"],
  input[type="number"],
  input[type="email"],
  input[type="tel"],
  select,
  textarea {
    font-size: 16px !important;
  }
}
</style>