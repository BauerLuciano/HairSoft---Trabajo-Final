<template>
  <div class="pedido-container">
    <div class="card-modern">
      <div class="header-section">
        <h2>Reservar Turno Online</h2>
        <p class="subtitle">Reserva tu turno desde casa, con pago de seña o total</p>
      </div>

      <div class="form-content">
        <div class="input-group cliente-section">
          <label class="section-label">👤 Tus Datos</label>
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

        <div class="input-group">
          <label class="section-label">👨‍💼 Elegir Peluquero</label>
          <select v-model="form.peluquero" @change="onPeluqueroSeleccionado" class="select-modern-rounded">
            <option value="">Selecciona tu peluquero preferido</option>
            <option v-for="p in peluqueros" :key="p.id" :value="p.id">
              {{ p.nombre }} {{ p.apellido }}
            </option>
          </select>
        </div>

        <div v-if="form.peluquero" class="input-group">
          <label class="section-label">📁 Seleccionar Categorías</label>
          <div class="categorias-container-horizontal">
            <div class="categorias-grid-horizontal">
              <div 
                v-for="categoria in categorias" 
                :key="categoria.id"
                class="categoria-card-horizontal"
                :class="{ selected: categoriasSeleccionadas.includes(categoria.id) }"
                @click="toggleCategoria(categoria.id)"
              >
                <div class="categoria-checkbox-horizontal">
                  <span class="checkmark-horizontal" :class="{ checked: categoriasSeleccionadas.includes(categoria.id) }">
                    ✓
                  </span>
                </div>
                <div class="categoria-content-horizontal">
                  <span class="categoria-nombre-horizontal">{{ categoria.nombre }}</span>
                  <span class="categoria-desc-horizontal">{{ categoria.descripcion || 'Servicios de calidad' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="categoriasSeleccionadas.length === 0" class="no-selection">
            <span>📝</span>
            <p>Selecciona al menos una categoría para ver los servicios</p>
          </div>
        </div>

        <transition name="scale-fade">
          <div v-if="categoriasSeleccionadas.length > 0" class="input-group">
            <label class="section-label">
              ✂️ Servicios Disponibles
              <span class="selected-categories">({{ categoriasSeleccionadasNombres }})</span>
            </label>
            
            <div class="busqueda-servicios">
              <input
                type="text"
                v-model="busquedaServicio"
                placeholder="Buscar servicio..."
                class="input-busqueda"
              />
            </div>
            
            <div class="servicios-grid-horizontal" v-if="serviciosFiltrados.length > 0">
              <div 
                v-for="servicio in serviciosFiltrados" 
                :key="servicio.id"
                class="servicio-item-horizontal"
                :class="{ selected: form.servicios_ids.includes(servicio.id) }"
                @click="toggleServicio(servicio)"
              >
                <div class="servicio-checkbox">
                  <span class="checkmark" :class="{ checked: form.servicios_ids.includes(servicio.id) }">
                    ✓
                  </span>
                </div>
                <div class="servicio-info">
                  <span class="servicio-nombre">{{ servicio.nombre }}</span>
                  <div class="servicio-details">
                    <span class="servicio-precio">${{ servicio.precio }}</span>
                    <span class="servicio-duracion">{{ servicio.duracion }}min</span>
                  </div>
                  <span class="servicio-categoria">{{ getCategoriaNombre(servicio.categoria) }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="no-servicios">
              <p v-if="busquedaServicio">No se encontraron servicios con "{{ busquedaServicio }}"</p>
              <p v-else>No hay servicios en las categorías seleccionadas</p>
            </div>
          </div>
        </transition>

        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0" class="resumen-pedido">
            <h3 class="section-label">💰 Resumen de Costos</h3>
            <div class="resumen-grid">
              <div class="resumen-item" v-for="servicioId in form.servicios_ids" :key="servicioId">
                <span>{{ getServicioNombre(servicioId) }}</span>
                <span>${{ getServicioPrecio(servicioId) }}</span>
              </div>
              <div class="resumen-item total">
                <span>Total del servicio</span>
                <span><strong>${{ calcularTotal() }}</strong></span>
              </div>
            </div>
          </div>
        </transition>

        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0" class="input-group">
            <label class="section-label">📅 Seleccionar Fecha</label>
            
            <div class="calendar-container-horizontal">
              <div class="calendar-grid-horizontal">
                <div 
                  v-for="dateInfo in fechasDisponibles" 
                  :key="dateInfo.fullDate"
                  class="date-card-horizontal"
                  :class="{ 
                    selected: form.fecha === dateInfo.fullDate,
                    today: dateInfo.isToday 
                  }"
                  @click="seleccionarFecha(dateInfo)"
                >
                  <div v-if="dateInfo.isToday" class="today-badge">Hoy</div>
                  <div class="date-content">
                    <span class="day-name">{{ dateInfo.dayName }}</span>
                    <span class="day-number">{{ dateInfo.dayNum }}</span>
                    <span class="month-name">{{ dateInfo.month }}</span>
                  </div>
                  <div class="shine-effect"></div>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <transition name="scale-fade">
          <div v-if="form.fecha" class="input-group">
            <label class="section-label">⏰ Seleccionar Horario</label>
            
            <div class="time-picker-trigger" @click="abrirModalHora">
              <div class="time-display">
                <span class="time-icon">⏰</span>
                <span class="time-text">{{ form.hora || 'Seleccionar hora' }}</span>
                <span class="time-arrow">▼</span>
              </div>
            </div>
          </div>
        </transition>

        <transition name="scale-fade">
          <div v-if="form.fecha && form.hora" class="input-group">
            <label class="section-label">💳 Seleccione Opción de Pago</label>
            
            <div class="pago-container-horizontal">
              <div class="pago-options-horizontal">
                <div 
                  class="pago-option-horizontal"
                  :class="{ selected: form.tipo_pago === 'SENA_50' }"
                  @click="form.tipo_pago = 'SENA_50'"
                >
                  <div class="pago-content-horizontal">
                    <span class="pago-nombre-horizontal">Seña (50%)</span>
                    <span class="pago-monto-horizontal">${{ calcularSena() }}</span>
                    <span class="pago-desc-horizontal">Resto: ${{ (calcularTotal() * 0.5).toFixed(2) }} en el local</span>
                  </div>
                </div>

                <div 
                  class="pago-option-horizontal"
                  :class="{ selected: form.tipo_pago === 'TOTAL' }"
                  @click="form.tipo_pago = 'TOTAL'"
                >
                  <div class="pago-content-horizontal">
                    <span class="pago-nombre-horizontal">Pago Total (100%)</span>
                    <span class="pago-monto-horizontal">${{ calcularTotal() }}</span>
                    <span class="pago-desc-horizontal">Pago completo online</span>
                  </div>
                </div>
              </div>

              <transition name="slide-fade">
                <div v-if="form.tipo_pago" class="medio-pago-section-horizontal">
                  <label class="section-label">🔗 Medio de Pago</label>
                  <div class="medio-pago-options-horizontal">
                    <div class="medio-pago-btn-horizontal active">
                      <span class="medio-icon-horizontal">💳</span>
                      <span class="medio-text-horizontal">Mercado Pago</span>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </transition>

        <transition name="scale-fade">
          <div v-if="formularioValido" class="card-modern resumen-final">
            <h3 class="section-label">✅ Confirmar y Pagar</h3>
            <div class="resumen-final-detalles">
              <div class="resumen-grid">
                <div class="resumen-item">
                  <span>Fecha:</span>
                  <span>{{ formatoFechaLegible(form.fecha) }} a las {{ form.hora }}</span>
                </div>
                <div class="resumen-item">
                  <span>Peluquero:</span>
                  <span>{{ getPeluqueroNombre() }}</span>
                </div>
                <div class="resumen-item">
                  <span>Servicios:</span>
                  <span>{{ getServiciosNombres() }}</span>
                </div>
                <div class="resumen-item total">
                  <span>Total a pagar ahora:</span>
                  <span class="monto-final-pago">${{ montoAPagarAhora() }}</span>
                </div>
              </div>
            </div>
            
            <button
              @click="reservarTurno" 
              class="btn-registrar-premium"
              :disabled="cargando"
            >
              <span class="btn-content">
                {{ cargando ? '🔄 Procesando...' : `💳 Pagar $${montoAPagarAhora()} con Mercado Pago` }}
              </span>
            </button>
            
            <p class="info-pago-final">
              Tu turno quedará <strong>confirmado</strong> tras el pago exitoso.
            </p>
          </div>
        </transition>

        <transition name="bounce">
          <div v-if="mensajeInteres" class="mensaje-premium" :class="{ error: mensajeInteres.includes('Error') }">
            <span class="mensaje-icon">{{ mensajeInteres.includes('Error') ? '❌' : '✅' }}</span>
            <span class="mensaje-text">{{ mensajeInteres }}</span>
          </div>
        </transition>

        <transition name="bounce">
          <div v-if="mensaje" class="mensaje-premium" :class="{ error: mensaje.includes('Error') }">
            <span class="mensaje-icon">{{ mensaje.includes('Error') ? '❌' : '✅' }}</span>
            <span class="mensaje-text">{{ mensaje }}</span>
          </div>
        </transition>

        <div v-if="cargando" class="loading-overlay">
          <div class="loading-content">
            <span class="loading-spinner">🔄</span>
            <p>Iniciando proceso de pago. No cierres esta ventana...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL DE HORARIOS -->
    <div v-if="mostrarModalHora" class="modal-overlay" @click="cerrarModalHora">
      <div class="modal-content modal-horario-grande" @click.stop>
        <div class="modal-header">
          <h3>⏰ Seleccionar Horario</h3>
          <button class="modal-close-btn" @click="cerrarModalHora">×</button>
        </div>
        <div class="modal-body">
          
          <!-- GRID DE HORARIOS - ESTILOS IGUAL AL PRESENCIAL -->
          <div class="quick-time-grid-modal-mejorado">
            
            <!-- CADA HORARIO -->
            <div 
              v-for="hora in horariosDisponibles" 
              :key="hora"
              class="quick-time-option-modal-mejorado"
              :class="{ 
                selected: form.hora === hora,
                disabled: !estaHorarioDisponible(hora)
              }"
            >
              
              <!-- SI ESTÁ DISPONIBLE -->
              <div 
                v-if="estaHorarioDisponible(hora)"
                class="hora-content-disponible"
                @click="seleccionarHoraRapida(hora)"
              >
                <div class="hora-icon">✅</div>
                <div class="hora-texto">
                  <span class="hora-hora">{{ hora }}</span>
                  <span class="hora-estado">Disponible</span>
                </div>
              </div>
              
              <!-- SI ESTÁ OCUPADO -->
              <div 
                v-else
                class="hora-content-ocupado"
              >
                <div class="hora-icon">❌</div>
                <div class="hora-texto">
                  <span class="hora-hora">{{ hora }}</span>
                  <span class="hora-estado">Ocupado</span>
                </div>
                
                <!-- BOTÓN "AVÍSAME" - SIEMPRE VISIBLE -->
                <div class="horario-ocupado-actions-mejorado">
                  <button 
                    @click.stop="registrarInteresHorario(hora)"
                    class="btn-avisar-liberado-mejorado"
                    :disabled="estaInteresRegistrado(hora)"
                  >
                    {{ estaInteresRegistrado(hora) ? '✅ En lista' : '🔔 Avísame' }}
                  </button>
                </div>
              </div>
              
            </div>
          </div>
          
          <!-- INFORMACIÓN ADICIONAL -->
          <div class="info-avisos-horarios">
            <p><strong>💡 ¿El horario está ocupado?</strong></p>
            <p>Tocá "Avísame" y te notificaremos si alguien cancela.</p>
            <p>Tendrás <strong>15% descuento</strong>.</p>
          </div>
          
        </div>
      </div>
    </div>

    <!-- Modal de Confirmación de Interés -->
    <div v-if="mostrarModalInteres" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>🔔 Confirmar Interés</h3>
          <button class="modal-close-btn" @click="cancelarRegistroInteres">×</button>
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
              <strong>¡Beneficio exclusivo!</strong> Si se libera, tendrás <strong>PRIORIDAD</strong> (primer registrado = primer avisado), <strong>15% de descuento</strong> 
              y 1 hora para confirmar el turno.
            </div>
          </div>
          <div class="modal-actions">
            <button 
              @click="confirmarRegistroInteres" 
              class="btn-confirmar-interes"
              :disabled="registrandoInteres"
            >
              {{ registrandoInteres ? 'Registrando...' : '✅ Sí, avisarme' }}
            </button>
            <button @click="cancelarRegistroInteres" class="btn-cancelar-interes">❌ Cancelar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Swal from 'sweetalert2'; // ✅ Importamos Swal

export default {
  data() {
    return {
      form: {
        peluquero: null, 
        servicios_ids: [],
        hora: "",
        fecha: "",
        tipo_pago: null,
        medio_pago: "MERCADO_PAGO",
        canal: "WEB"
      },
      usuario: { 
        id: null, 
        nombre: 'Cargando', 
        apellido: '...', 
        dni: 'Cargando', 
        telefono: '',
        turnosCount: 0 
      }, 
      peluqueros: [],
      servicios: [],
      categorias: [],
      turnosOcupados: [],
      mensaje: "", // Ya no lo usaremos visualmente, pero lo dejo por compatibilidad
      cargando: false,
      categoriasSeleccionadas: [],
      busquedaServicio: "",
      interesesRegistrados: [],
      mostrarModalInteres: false,
      horarioSeleccionadoInteres: null,
      registrandoInteres: false,
      mensajeInteres: "",
      mostrarModalHora: false
    };
  },
  computed: {
    formularioValido() {
      return this.form.peluquero && 
             this.form.servicios_ids.length > 0 &&
             this.form.fecha && 
             this.form.hora &&
             this.form.tipo_pago;
    },
    
    fechasDisponibles() {
      const dates = [];
      const today = new Date();
      for (let i = 0; i < 14; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        if (date.getDay() !== 0) {
          dates.push(this.formatDate(date));
          if (dates.length === 7) break;
        }
      }
      return dates;
    },

    serviciosFiltrados() {
      let filtrados = this.servicios;
      if (this.categoriasSeleccionadas.length > 0) {
        filtrados = filtrados.filter(servicio => {
          const categoriaSeleccionada = this.categorias.find(cat => 
            cat.id === this.categoriasSeleccionadas[0]
          );
          return servicio.categoria === categoriaSeleccionada.nombre;
        });
      }
      if (this.busquedaServicio) {
        const termino = this.busquedaServicio.toLowerCase();
        filtrados = filtrados.filter(s => s.nombre.toLowerCase().includes(termino));
      }
      return filtrados;
    },

    categoriasSeleccionadasNombres() {
      return this.categoriasSeleccionadas.map(catId => {
        const categoria = this.categorias.find(c => c.id === catId);
        return categoria ? categoria.nombre : '';
      }).join(', ');
    },
    
    horariosDisponibles() {
      const horariosBase = [];
      const bloques = [{ inicio: 8, fin: 12 }, { inicio: 15, fin: 20 }];
      const ahora = new Date();
      const horaActual = ahora.getHours();
      const minutoActual = ahora.getMinutes();
      
      const hoy = new Date();
      const hoyFormateado = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`;
      const esHoy = this.form.fecha === hoyFormateado;

      bloques.forEach(b => {
        for (let h = b.inicio; h < b.fin; h++) {
          for (let m = 0; m < 60; m += 30) {
            const horaStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
            if (esHoy) {
              if (h < horaActual || (h === horaActual && m <= minutoActual)) continue;
            }
            horariosBase.push(horaStr);
          }
        }
      });
      return horariosBase;
    }
  },
  methods: {
    async cargarDatosIniciales() {
      await Promise.all([
        this.cargarUsuarioLogueado(),
        this.cargarPeluqueros(),
        this.cargarServicios(),
        this.cargarCategorias(),
        this.cargarTurnosOcupados()
      ]);
      // Cargar intereses DESPUÉS de tener el usuario asegurado
      await this.cargarInteresesUsuario();
    },

    async cargarUsuarioLogueado() {
          try {
            const storedUserId = localStorage.getItem('user_id') || sessionStorage.getItem('user_id');
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            const config = token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
            
            if (storedUserId) {
                const res = await axios.get(`http://localhost:8000/usuarios/api/usuarios/${storedUserId}/`, config); 
                this.usuario = res.data; 
                this.usuario.id = parseInt(storedUserId);
                try {
                  const statsRes = await axios.get(`http://localhost:8000/usuarios/api/turnos/cliente/${this.usuario.id}/estadisticas/`, config);
                  this.usuario.turnosCount = statsRes.data.total_turnos || 0;
                } catch (statsErr) {
                  this.usuario.turnosCount = 0;
                }
            } else {
                this.usuario = { nombre: 'Invitado', apellido: '', dni: 'No identificado', telefono: 'No registrado', turnosCount: 0, id: null };
            }
          } catch (err) {
            console.error("Error usuario:", err);
            const storedUserId = localStorage.getItem('user_id');
            this.usuario = { 
              nombre: localStorage.getItem('user_nombre') || 'Invitado', 
              apellido: '', 
              dni: 'No disponible', 
              id: storedUserId ? parseInt(storedUserId) : null
            };
          }
    },
    
    async cargarPeluqueros() {
      try {
        const res = await axios.get("http://localhost:8000/usuarios/api/peluqueros/");
        this.peluqueros = res.data.map(p => ({ ...p, apellido: p.apellido || '' }));
      } catch (err) { this.peluqueros = []; }
    },

    async cargarServicios() {
      try {
        const res = await axios.get("http://localhost:8000/usuarios/api/servicios/");
        this.servicios = res.data;
      } catch (err) { console.error(err); }
    },

    async cargarCategorias() {
      try {
        const res = await axios.get("http://localhost:8000/usuarios/api/categorias/servicios/");
        this.categorias = res.data;
      } catch (err) { console.error(err); }
    },

    async cargarTurnosOcupados(fecha = null) {
      try {
        let url = "http://localhost:8000/usuarios/api/turnos/?estado__in=RESERVADO,CONFIRMADO";
        if (fecha) url += `&fecha=${fecha}`;
        const res = await axios.get(url);
        this.turnosOcupados = res.data.results || res.data;
      } catch (err) { this.turnosOcupados = []; }
    },

    async cargarInteresesUsuario() {
      try {
        if (this.usuario.id) {
          // Asegúrate de que la URL coincida con tu urls.py (singular o plural)
          const res = await axios.get(`http://localhost:8000/usuarios/api/turnos/mis-intereses/`, {
             headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
          });
          this.interesesRegistrados = res.data;
        }
      } catch (err) { console.error("Error intereses:", err); }
    },
    
    montoAPagarAhora() {
      const total = parseFloat(this.calcularTotal());
      if (this.form.tipo_pago === 'TOTAL') return total.toFixed(2);
      if (this.form.tipo_pago === 'SENA_50') return (total * 0.5).toFixed(2);
      return '0.00';
    },

    toggleCategoria(categoriaId) {
      const index = this.categoriasSeleccionadas.indexOf(categoriaId);
      if (index === -1) this.categoriasSeleccionadas.push(categoriaId);
      else this.categoriasSeleccionadas.splice(index, 1);
    },

    toggleServicio(servicio) {
      const index = this.form.servicios_ids.indexOf(servicio.id);
      if (index === -1) this.form.servicios_ids.push(servicio.id);
      else this.form.servicios_ids.splice(index, 1);
    },

    getServicioNombre(id) { return this.servicios.find(x => x.id === id)?.nombre || ''; },
    getServiciosNombres() { return this.form.servicios_ids.map(id => this.getServicioNombre(id)).join(', '); },
    getServicioPrecio(id) { return this.servicios.find(x => x.id === id)?.precio || 0; },
    getCategoriaNombre(categoria) { return categoria || 'General'; },

    calcularTotal() {
      return this.form.servicios_ids.reduce((total, id) => total + parseFloat(this.getServicioPrecio(id) || 0), 0).toFixed(2);
    },
    calcularSena() { return (this.calcularTotal() * 0.5).toFixed(2); },

    formatDate(date) {
      const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
      const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
      const today = new Date();
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const fullDate = `${year}-${month}-${day}`;
      const isToday = date.toDateString() === today.toDateString();
      
      return {
        dayName: days[date.getDay()],
        dayNum: date.getDate(),
        month: months[date.getMonth()],
        fullDate: fullDate,
        isToday: isToday,
        dateObj: date
      };
    },

    formatoFechaLegible(fechaStr) {
      if(!fechaStr) return '';
      const [year, month, day] = fechaStr.split('-');
      const fecha = new Date(year, month - 1, day);
      return fecha.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
    },

    onPeluqueroSeleccionado() {
      this.limpiarSelecciones();
      this.cargarTurnosOcupados(this.form.fecha);
    },

    seleccionarFecha(dateInfo) {
      this.form.fecha = dateInfo.fullDate;
      this.form.hora = "";
      this.form.tipo_pago = null;
      this.cargarTurnosOcupados(dateInfo.fullDate);
    },

    estaHorarioDisponible(horario) {
      if (!this.form.fecha || !this.form.peluquero) return true;
      const peluqueroSeleccionado = this.peluqueros.find(p => p.id == this.form.peluquero);
      if (!peluqueroSeleccionado) return true;

      const turnoOcupado = this.turnosOcupados.find(turno => {
        const mismoPeluquero = turno.peluquero_id == this.form.peluquero; // ID vs ID es más seguro
        return mismoPeluquero && turno.fecha === this.form.fecha && turno.hora === horario;
      });
      return !turnoOcupado;
    },

    estaInteresRegistrado(horario) {
      return this.interesesRegistrados.some(interes => 
        interes.fecha_deseada === this.form.fecha &&
        interes.hora_deseada === horario &&
        interes.peluquero_id == this.form.peluquero
      );
    },

    getPeluqueroNombre() {
      const p = this.peluqueros.find(p => p.id == this.form.peluquero); 
      return p ? `${p.nombre} ${p.apellido}` : '';
    },

    limpiarSelecciones() {
      this.form.fecha = null;
      this.form.hora = "";
      this.form.servicios_ids = [];
      this.form.tipo_pago = null;
      this.categoriasSeleccionadas = [];
    },

    abrirModalHora() { this.mostrarModalHora = true; },
    cerrarModalHora() { this.mostrarModalHora = false; },

    seleccionarHoraRapida(hora) {
      if (this.estaHorarioDisponible(hora)) {
        this.form.hora = hora;
        this.form.tipo_pago = null;
        this.cerrarModalHora();
      }
    },

    registrarInteresHorario(horario) {
      if (this.estaHorarioDisponible(horario)) {
        Swal.fire('Atención', 'Este horario está disponible, puedes reservarlo directamente.', 'info');
        return;
      }
      this.horarioSeleccionadoInteres = horario;
      this.mostrarModalInteres = true;
    },

    cancelarRegistroInteres() {
      this.mostrarModalInteres = false;
      this.horarioSeleccionadoInteres = null;
    },

    async confirmarRegistroInteres() {
        if (!this.usuario.id) { 
            Swal.fire('Error', 'Debes iniciar sesión para registrarte.', 'error');
            return; 
        }

        this.registrandoInteres = true;

        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {};

            const payload = {
                cliente_id: this.usuario.id,
                servicio_id: this.form.servicios_ids[0],
                peluquero_id: this.form.peluquero,
                fecha_deseada: this.form.fecha,
                hora_deseada: this.horarioSeleccionadoInteres
            };

            const res = await axios.post(
                "http://localhost:8000/usuarios/api/turnos/registrar-interes/",
                payload, 
                config
            );
            
            // ✅ EXITO: SWAL + REFRESCO
            if (res.data.success) {
                this.mostrarModalInteres = false;
                await this.cargarInteresesUsuario(); // <--- ESTO ACTUALIZA EL BOTÓN "YA REGISTRADO"
                
                Swal.fire({
                    icon: 'success',
                    title: '¡Listo!',
                    text: 'Te avisaremos por WhatsApp si el turno se libera.',
                    timer: 3000,
                    showConfirmButton: false
                });
            } else {
                Swal.fire('Atención', res.data.error || "Ya estás registrado.", 'warning');
            }
        } catch (err) {
            Swal.fire('Error', err.response?.data?.error || "Error al conectar.", 'error');
        } finally {
            this.registrandoInteres = false;
        }
    },
    
    async reservarTurno() {
      if (!this.formularioValido) {
        Swal.fire('Faltan datos', 'Completa todos los campos y selecciona el pago.', 'warning');
        return;
      }

      this.cargando = true;
      const payload = {
        peluquero_id: this.form.peluquero, 
        servicios_ids: this.form.servicios_ids,
        fecha: this.form.fecha,
        hora: this.form.hora,
        canal: 'WEB',
        tipo_pago: this.form.tipo_pago,
        medio_pago: this.form.medio_pago
      };

      try {
        const token = localStorage.getItem('token');
        const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {};

        const res = await axios.post("http://localhost:8000/usuarios/api/turnos/crear/", payload, config);
        const data = res.data;
        this.cargando = false;

        if (data.status === 'ok') {
          if (data.procesar_pago && data.mp_data?.init_point) {
            
            // ✅ ÉXITO CON PAGO: SWAL CON CONFIRMACIÓN
            Swal.fire({
                icon: 'success',
                title: 'Reserva Iniciada',
                text: 'Te redirigiremos a Mercado Pago para completar el pago.',
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                window.open(data.mp_data.init_point, '_blank');
                this.$router.push('/turnos');
            });

          } else {
            // ✅ ÉXITO SIN PAGO (LOCAL): SWAL SIMPLE
            Swal.fire({
                icon: 'success',
                title: '¡Turno Reservado!',
                text: 'Te esperamos en el local.',
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                this.$router.push('/turnos');
            });
          }
        } else {
          Swal.fire('Error', data.message || "No se pudo reservar.", 'error');
        }
      } catch (err) {
        this.cargando = false;
        if (err.response && err.response.status === 401) {
            Swal.fire('Sesión Expirada', 'Por favor inicia sesión nuevamente.', 'error');
        } else {
            Swal.fire('Error', err.response?.data?.message || 'Error de conexión', 'error');
        }
      }
    },

    iniciarPagoMercadoPago(initPointUrl) {
      if (initPointUrl) window.open(initPointUrl, '_blank');
    }
  },

  mounted() {
    this.cargarDatosIniciales();
  }
};
</script>

<style scoped>
/* ESTILOS BASE */
.pedido-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 25px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.header-section h2 {
  margin: 0 0 8px 0;
  color: #1a1a1a;
  font-size: 1.8em;
  font-weight: 700;
}

.subtitle {
  color: #6c757d;
  font-size: 1.1em;
  margin: 0;
}

.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.input-group {
  margin-bottom: 25px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1a1a1a;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 1.1em;
}

.cliente-section {
  margin-left: 0;
}

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

.select-modern-rounded {
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 16px;
  transition: all 0.3s ease;
  color: #1a1a1a;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'><path fill='%23666' d='M2 0L0 2h4zm0 5L0 3h4z'/></svg>");
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 12px;
}

.select-modern-rounded:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

/* CATEGORÍAS HORIZONTALES */
.categorias-container-horizontal {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.categorias-grid-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 20px;
  overflow-x: auto;
}

.categoria-card-horizontal {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
  min-width: 200px;
  flex-shrink: 0;
}

.categoria-card-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.categoria-card-horizontal.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.checkmark-horizontal {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
  font-size: 12px;
  font-weight: bold;
}

.checkmark-horizontal.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.categoria-nombre-horizontal {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 4px;
}

.categoria-desc-horizontal {
  font-size: 0.8em;
  color: #6c757d;
}

.no-selection {
  text-align: center;
  padding: 30px 20px;
  color: #6c757d;
  border: 2px dashed #e9ecef;
  border-radius: 12px;
  margin-top: 10px;
}

.no-selection span {
  font-size: 2em;
  margin-bottom: 10px;
  display: block;
}

/* SERVICIOS */
.busqueda-servicios {
  margin-bottom: 15px;
}

.input-busqueda {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
}

.input-busqueda:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.servicios-grid-horizontal {
  display: flex;
  overflow-x: auto;
  gap: 12px;
  padding: 10px 5px;
  margin-bottom: 15px;
}

.servicio-item-horizontal {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
  min-width: 280px;
  flex-shrink: 0;
}

.servicio-item-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.servicio-item-horizontal.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
  font-size: 12px;
  font-weight: bold;
}

.checkmark.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.servicio-nombre {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 6px;
}

.servicio-details {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.servicio-precio {
  color: #28a745;
  font-weight: 700;
}

.servicio-duracion {
  color: #6c757d;
  font-size: 0.9em;
}

.servicio-categoria {
  font-size: 0.75em;
  background: #f1f3f4;
  color: #6c757d;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

.selected-categories {
  color: #007bff;
  font-weight: 500;
  font-size: 0.9em;
  margin-left: 8px;
}

/* CALENDARIO */
.calendar-container-horizontal {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.calendar-grid-horizontal {
  display: flex;
  overflow-x: auto;
  padding: 20px;
  gap: 12px;
}

.date-card-horizontal {
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  padding: 20px 15px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 3px solid transparent;
  min-width: 120px;
  flex-shrink: 0;
  overflow: hidden;
}

.date-card-horizontal:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(79, 172, 254, 0.3);
}

.date-card-horizontal.selected {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: #4facfe;
  box-shadow: 0 25px 50px rgba(79, 172, 254, 0.5);
  transform: scale(1.05);
}

.today-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: linear-gradient(135deg, #24948c 0%, #e08618 100%);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 10px;
}

.date-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.day-name {
  font-size: 0.8rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.date-card-horizontal.selected .day-name {
  color: rgba(255, 255, 255, 0.9);
}

.day-number {
  font-size: 2rem;
  font-weight: 900;
  color: #1e293b;
}

.date-card-horizontal.selected .day-number {
  color: white;
}

.month-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}

.date-card-horizontal.selected .month-name {
  color: rgba(255, 255, 255, 0.85);
}

/* SELECTOR DE HORA */
.time-picker-trigger {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.time-picker-trigger:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.15);
}

.time-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #1a1a1a;
  font-weight: 600;
}

.time-icon {
  font-size: 1.2em;
}

.time-text {
  flex: 1;
  text-align: center;
  font-size: 1.1em;
}

.time-arrow {
  color: #6c757d;
  transition: transform 0.3s ease;
}

/* MODAL */
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

.modal-horario-grande {
  max-width: 800px !important;
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

/* GRID DE HORARIOS MEJORADO - ESTILOS IGUAL AL PRESENCIAL */
.quick-time-grid-modal-mejorado {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px;
}

.quick-time-option-modal-mejorado {
  border-radius: 12px;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

/* HORARIOS DISPONIBLES */
.hora-content-disponible {
  padding: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border: 2px solid #28a745;
  transition: all 0.3s ease;
}

.hora-content-disponible:hover {
  background: linear-gradient(135deg, #c3e6cb, #b1dfbb);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.quick-time-option-modal-mejorado.selected .hora-content-disponible {
  background: linear-gradient(135deg, #28a745, #20c997);
  border-color: #1e7e34;
}

.quick-time-option-modal-mejorado.selected .hora-hora,
.quick-time-option-modal-mejorado.selected .hora-estado {
  color: white;
}

/* HORARIOS OCUPADOS */
.hora-content-ocupado {
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border: 2px solid #ffc107;
}

.hora-icon {
  font-size: 1.5em;
  flex-shrink: 0;
}

.hora-texto {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hora-hora {
  font-size: 1.3em;
  font-weight: 700;
  color: #155724;
}

.hora-content-ocupado .hora-hora {
  color: #856404;
}

.hora-estado {
  font-size: 0.85em;
  color: #155724;
  opacity: 0.8;
}

.hora-content-ocupado .hora-estado {
  color: #856404;
}

/* BOTÓN "AVÍSAME SI SE LIBERA" */
.horario-ocupado-actions-mejorado {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ffc107;
  width: 100%;
}

.btn-avisar-liberado-mejorado {
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
}

.btn-avisar-liberado-mejorado:hover:not(:disabled) {
  background: linear-gradient(135deg, #0984e3, #074a8f);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(116, 185, 255, 0.4);
}

.btn-avisar-liberado-mejorado:disabled {
  background: linear-gradient(135deg, #00b894, #00a085);
  cursor: not-allowed;
}

/* INFO AVISOS */
.info-avisos-horarios {
  margin-top: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border-radius: 10px;
  border: 1px solid #90caf9;
  text-align: center;
}

.info-avisos-horarios p {
  margin: 5px 0;
  color: #1565c0;
  font-size: 0.9em;
}

/* MODAL DE INTERÉS */
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

/* PAGO */
.pago-container-horizontal {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  padding: 25px;
}

.pago-options-horizontal {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.pago-option-horizontal {
  flex: 1;
  padding: 25px 20px;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.pago-option-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
}

.pago-option-horizontal.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.pago-nombre-horizontal {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 1.2em;
  display: block;
  margin-bottom: 8px;
}

.pago-monto-horizontal {
  color: #28a745;
  font-weight: 800;
  font-size: 1.4em;
  display: block;
  margin-bottom: 8px;
}

.pago-desc-horizontal {
  color: #6c757d;
  font-size: 0.9em;
}

.medio-pago-section-horizontal {
  margin-top: 25px;
  padding-top: 25px;
  border-top: 2px solid #f1f3f4;
}

.medio-pago-btn-horizontal {
  padding: 25px 20px;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.medio-pago-btn-horizontal.active {
  border-color: #007bff;
  background: #e7f3ff;
}

.medio-icon-horizontal {
  font-size: 2.5em;
}

.medio-text-horizontal {
  font-weight: 700;
  color: #1a1a1a;
}

/* RESUMEN */
.resumen-pedido {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  border: 2px solid #e9ecef;
}

.resumen-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  color: #1a1a1a;
}

.resumen-item.total {
  border-top: 2px solid #dee2e6;
  margin-top: 10px;
  padding-top: 12px;
  font-size: 1.2em;
  font-weight: 700;
}

.resumen-final {
  background: linear-gradient(135deg, #f8fff9, #f0f9ff);
  border-color: #28a745;
}

.monto-final-pago {
  color: #28a745;
  font-weight: 800;
  font-size: 1.3em;
}

.btn-registrar-premium {
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
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.btn-registrar-premium:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
}

.btn-registrar-premium:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
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
}

/* MENSAJES */
.mensaje-premium {
  margin-top: 20px;
  padding: 15px 20px;
  border-radius: 10px;
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mensaje-premium.error {
  background: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

.mensaje-icon {
  font-size: 1.2em;
}

/* LOADING */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.loading-content {
  background: white;
  padding: 30px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.loading-spinner {
  font-size: 2em;
  display: block;
  margin-bottom: 15px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ANIMACIONES */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.scale-fade-enter-active {
  transition: all 0.3s ease;
}
.scale-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.scale-fade-enter-from,
.scale-fade-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

.bounce-enter-active {
  animation: bounce-in 0.5s;
}
.bounce-leave-active {
  animation: bounce-in 0.5s reverse;
}

/* ESTILO PARA EL BOTÓN "YA REGISTRADO" */
.btn-avisar-nuevo:disabled {
  background: linear-gradient(135deg, #2ecc71, #27ae60) !important; /* Verde éxito */
  color: white !important;
  opacity: 0.9;
  cursor: default;
  box-shadow: none;
  transform: none;
  border: 1px solid #2ecc71;
}

/* Ajuste visual para que se note que es un estado final */
.btn-avisar-nuevo:disabled::before {
  content: ""; 
}

@keyframes bounce-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .pedido-container {
    padding: 15px;
  }
  
  .calendar-grid-horizontal,
  .servicios-grid-horizontal,
  .categorias-grid-horizontal {
    flex-direction: column;
  }
  
  .servicio-item-horizontal,
  .categoria-card-horizontal {
    min-width: auto;
  }
  
  .pago-options-horizontal,
  .modal-actions {
    flex-direction: column;
  }
  
  .quick-time-grid-modal-mejorado {
    grid-template-columns: 1fr;
  }
  
  .modal-horario-grande {
    margin: 10px;
    max-height: 95vh;
  }
}
</style>