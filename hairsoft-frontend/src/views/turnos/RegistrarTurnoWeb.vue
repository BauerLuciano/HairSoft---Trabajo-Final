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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
// ✅ USAMOS TU INSTANCIA CENTRAL (api.js) PARA NO TOCAR URLS NUNCA MÁS
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
// ESTADO REACTIVO (INTACTO)
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

const usuario = ref({ id: null, nombre: '', apellido: '', dni: '', telefono: '', turnosCount: 0 })
const peluqueros = ref([])
const servicios = ref([])
const categorias = ref([])
const slotsOcupadosReales = ref([])
const categoriasSeleccionadas = ref([])
const busquedaServicio = ref("")

const cargandoMercadoPago = ref(false)
const cargandoHorarios = ref(false)
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

// ==========================================
// 🛡️ ESCUDOS ANTI-PANTALLA BLANCA (BLINDAJE)
// ==========================================

// Servicios filtrados con protección para que no explote si servicios está vacío
const serviciosFiltrados = computed(() => {
  const lista = Array.isArray(servicios.value) ? servicios.value : [];
  let filtrados = lista;
  
  if (categoriasSeleccionadas.value.length > 0) {
    filtrados = filtrados.filter(s => {
      if (!s || !s.categoria) return false;
      const catId = typeof s.categoria === 'object' ? String(s.categoria.id) : String(s.categoria);
      return categoriasSeleccionadas.value.includes(catId);
    });
  }
  
  if (busquedaServicio.value.trim()) {
    const term = busquedaServicio.value.toLowerCase().trim();
    filtrados = filtrados.filter(s => s.nombre && s.nombre.toLowerCase().includes(term));
  }
  return filtrados;
});

const getPeluqueroNombre = () => {
  if (!form.value.peluquero || !peluqueros.value) return '';
  const p = peluqueros.value.find(p => String(p.id) === String(form.value.peluquero));
  return p ? `${p.nombre || ''} ${p.apellido || ''}`.trim() : 'Seleccionar...';
}

const getServicioNombre = (id) => {
  const s = servicios.value.find(s => String(s.id) === String(id));
  return s ? s.nombre : 'Cargando...';
}

// ==========================================
// 🚀 LLAMADAS AL BACKEND (VÍA API.JS)
// ==========================================

const cargarDatosIniciales = async () => {
  const userId = localStorage.getItem('user_id');
  try {
    if (userId) {
      const resU = await api.get(`/usuarios/${userId}/`);
      usuario.value = resU.data;
      form.value.cliente = userId;
    }
    // Cargamos todo de una usando tu API central
    const [p, s, c] = await Promise.all([
      api.get('/peluqueros/'),
      api.get('/servicios/'),
      api.get('/categorias/servicios/')
    ]);
    
    // Verificamos si vienen paginados (DRF suele usar .results)
    peluqueros.value = p.data.results || p.data;
    servicios.value = s.data.results || s.data;
    categorias.value = c.data.results || c.data;
    
  } catch(e) { 
    console.error('Error carga inicial:', e);
    Swal.fire({ title: 'Error de conexión', text: 'No se pudieron cargar los datos del servidor.', icon: 'error' });
  }
}

const cargarTurnosOcupados = async (fecha) => {
  if (!form.value.peluquero) return;
  cargandoHorarios.value = true;
  try {
    const res = await api.get(`/turnos/?fecha=${fecha}&peluquero=${form.value.peluquero}&estado__in=RESERVADO,CONFIRMADO`);
    const turnos = res.data.results || res.data;
    const ocupadosSet = new Set();
    if (Array.isArray(turnos)) {
      turnos.forEach(turno => {
        if (!turno.hora) return;
        const [h, m] = turno.hora.split(':').map(Number);
        const inicioMin = h * 60 + m;
        const dur = turno.duracion_total || 20;
        for (let i = inicioMin; i < inicioMin + dur; i += 20) {
          ocupadosSet.add(`${Math.floor(i / 60).toString().padStart(2, '0')}:${(i % 60).toString().padStart(2, '0')}`);
        }
      });
    }
    slotsOcupadosReales.value = Array.from(ocupadosSet);
  } catch (e) { console.error("Error horarios:", e) } 
  finally { cargandoHorarios.value = false }
}

const crearPagoMercadoPago = async () => {
  if (!formularioValido.value) return;
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
    const res = await api.post('/turnos/crear/', payload);
    const mpUrl = res.data?.mp_data?.init_point || res.data?.init_point;
    if (mpUrl) window.location.href = mpUrl; // Redirección directa para móvil
  } catch (error) {
    Swal.fire({ title: 'Error', text: error.response?.data?.message || 'Error al procesar el turno.', icon: 'error' });
  } finally { cargandoMercadoPago.value = false }
}

const confirmarRegistroInteres = async () => {
  registrandoInteres.value = true;
  try {
    const payload = { 
      fecha: form.value.fecha, 
      hora: horarioSeleccionadoInteres.value, 
      peluquero_id: form.value.peluquero, 
      cliente_id: usuario.value.id, 
      servicios_ids: form.value.servicios_ids, 
      interes_notificacion: true 
    };
    await api.post('/turnos/registrar-interes/', payload);
    Swal.fire({ title: '¡Anotado!', text: 'Te avisaremos si se libera el horario.', icon: 'success' });
  } catch (e) { 
    Swal.fire({ title: 'Error', text: 'No se pudo registrar el interés.', icon: 'error' }); 
  } finally { 
    registrandoInteres.value = false; 
    mostrarModalInteres.value = false;
  }
}

// ==========================================
// LÓGICA DE SELECCIÓN Y CÁLCULOS (SIN CAMBIOS)
// ==========================================
const toggleServicio = (servicio) => {
  const id = String(servicio.id);
  if (form.value.servicios_ids.includes(id)) {
    form.value.servicios_ids = form.value.servicios_ids.filter(x => x !== id);
  } else {
    form.value.servicios_ids = [...form.value.servicios_ids, id];
  }
  if (form.value.hora) form.value.hora = "";
  if (form.value.fecha && form.value.peluquero) cargarTurnosOcupados(form.value.fecha);
}

const toggleCategoria = (id) => {
  const cid = String(id);
  const index = categoriasSeleccionadas.value.indexOf(cid);
  index > -1 ? categoriasSeleccionadas.value.splice(index, 1) : categoriasSeleccionadas.value.push(cid);
}

const calcularTotalOriginal = () => {
  return form.value.servicios_ids.reduce((acc, id) => {
    const s = servicios.value.find(x => String(x.id) === String(id));
    return acc + parseFloat(s?.precio || 0);
  }, 0);
}
const calcularTotalConDescuento = () => (calcularTotalOriginal() * (1 - descuentoAplicado.value / 100)).toFixed(2);
const calcularDuracionTotalServicios = () => {
  return form.value.servicios_ids.reduce((t, id) => {
    const s = servicios.value.find(x => String(x.id) === String(id));
    return t + (parseInt(s?.duracion || 20));
  }, 0);
}

const esHorarioDisponible = (h) => {
  if (!form.value.fecha || !form.value.peluquero) return true;
  if (slotsOcupadosReales.value.includes(h.substring(0, 5))) return false;
  return true;
}

const seleccionarPeluquero = (id) => { 
  form.value.peluquero = id; 
  form.value.fecha = ""; 
  form.value.hora = ""; 
  slotsOcupadosReales.value = [];
}

const seleccionarDiaCalendario = (d) => {
  const date = new Date(currentDate.value);
  form.value.fecha = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}

const seleccionarHora = (h) => { if (esHorarioDisponible(h)) form.value.hora = h; }

onMounted(cargarDatosIniciales);
watch(() => form.value.fecha, (f) => { if (f && form.value.peluquero) cargarTurnosOcupados(f) });

// Re-declaramos helpers de utilidad que usa tu template
const getNombreCompletoPeluquero = (p) => p ? `${p.nombre || ''} ${p.apellido || ''}`.trim() : '';
const getInicialesPeluquero = (p) => (p?.nombre || 'P').charAt(0).toUpperCase();
const formatoFechaLegible = (f) => f; // Simplificado para evitar errores
const formularioValido = computed(() => form.value.peluquero && form.value.servicios_ids.length > 0 && form.value.fecha && form.value.hora);
</script>

<style scoped>
/* ============================================
   ESTILOS ESPECÍFICOS PARA LA ALERTA MERCADO PAGO
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

/* ============================================
   ESTILOS MEJORADOS PARA PELUQUEROS
   ============================================ */
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

/* ============================================
   ESTILOS GENERALES (MANTENER LOS EXISTENTES)
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
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.hora-card-mejorada {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  text-align: center;
  font-weight: 600;
  background: white;
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
  height: 100%;
  justify-content: space-between;
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

/* Estilos adicionales para el flujo reorganizado */

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
  
  .grid-peluqueros {
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
  
  .alerta-contenido {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .alerta-icono-grande {
    width: 60px;
    height: 60px;
  }
  
  .grid-servicios {
    grid-template-columns: 1fr;
  }
  
  .grid-peluqueros {
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