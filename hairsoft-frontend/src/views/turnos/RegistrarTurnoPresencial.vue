<template>
  <div class="form-container">
    <div class="form-card turnos-card">
      <!-- HEADER CON GRADIENTE -->
      <div class="card-header">
        <div class="header-content">
          <div class="icon-wrapper">
            <span class="icon-emoji">💇‍♂️</span>
          </div>
          <div class="header-text">
            <h1 class="form-title">Registrar Turno Presencial</h1>
            <p class="form-subtitle">Sistema de reservas en local</p>
          </div>
        </div>
        <div class="header-decoration"></div>
      </div>

      <div class="form-content">
        <!-- CLIENTE CON BÚSQUEDA AVANZADA -->
        <div class="input-group enhanced">
          <label for="cliente" class="label-modern">
            <span class="label-icon">👤</span>
            <span>Buscar Cliente</span>
          </label>
          <div class="search-wrapper">
            <input
              type="text"
              id="cliente"
              v-model="form.clienteNombre"
              @input="buscarCliente"
              placeholder="Nombre, apellido o DNI..."
              autocomplete="off"
              class="input-modern"
            />
            <div class="search-icon">🔍</div>
          </div>
          <transition name="slide-fade">
            <ul v-if="clientesSugeridos.length" class="sugerencias-list">
              <li 
                v-for="c in clientesSugeridos" 
                :key="c.id" 
                @click="seleccionarCliente(c)"
                class="sugerencia-item"
              >
                <span class="cliente-avatar">{{ c.nombre.charAt(0) }}</span>
                <div class="cliente-info">
                  <span class="cliente-nombre">{{ c.nombre }} {{ c.apellido }}</span>
                  <span class="cliente-dni">DNI: {{ c.dni }}</span>
                </div>
                <span class="select-arrow">→</span>
              </li>
            </ul>
          </transition>
        </div>

        <!-- PELUQUERO CON ESTILO -->
        <div class="input-group enhanced">
          <label for="peluquero" class="label-modern">
            <span class="label-icon">✂️</span>
            <span>Peluquero</span>
          </label>
          <div class="select-wrapper">
            <select v-model="form.peluquero" id="peluquero" required @change="limpiarFechaHora" class="select-modern">
              <option value="">Seleccione un peluquero</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                {{ p.nombre }} {{ p.apellido }}
              </option>
            </select>
            <div class="select-arrow-icon">▼</div>
          </div>
        </div>

        <!-- SERVICIOS CON CARDS PREMIUM -->
        <div class="input-group enhanced">
          <label class="label-modern">
            <span class="label-icon">💅</span>
            <span>Servicios Disponibles</span>
          </label>
          <div class="servicios-grid-premium">
            <div 
              v-for="servicio in servicios" 
              :key="servicio.id"
              class="servicio-card"
              :class="{ selected: form.servicios_ids.includes(servicio.id) }"
              @click="toggleServicio(servicio)"
            >
              <div class="servicio-check">
                <span v-if="form.servicios_ids.includes(servicio.id)" class="check-icon">✓</span>
              </div>
              <div class="servicio-content">
                <span class="servicio-nombre">{{ servicio.nombre }}</span>
                <div class="servicio-meta">
                  <span class="servicio-precio">${{ servicio.precio }}</span>
                  <span class="servicio-duracion">⏱ {{ servicio.duracion }}min</span>
                </div>
              </div>
              <div class="card-glow"></div>
            </div>
          </div>
        </div>

        <!-- RESUMEN FLOTANTE -->
        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0" class="resumen-flotante">
            <div class="resumen-header">
              <span class="resumen-icon">📊</span>
              <h3>Resumen de Servicios</h3>
            </div>
            <div class="servicios-seleccionados">
              <div 
                v-for="servicioId in form.servicios_ids" 
                :key="servicioId"
                class="servicio-seleccionado"
              >
                <span class="servicio-dot"></span>
                <span class="servicio-text">{{ getServicioNombre(servicioId) }}</span>
                <span class="servicio-price">${{ getServicioPrecio(servicioId) }}</span>
              </div>
            </div>
            <div class="total-section">
              <span>Total</span>
              <span class="total-amount">${{ calcularTotal() }}</span>
            </div>
          </div>
        </transition>

        <!-- CALENDARIO MODERNO MEJORADO -->
        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0 && form.peluquero" class="input-group enhanced">
            <label class="label-modern">
              <span class="label-icon">📅</span>
              <span>Seleccionar Fecha</span>
            </label>
            <div class="calendario-wrapper">
              <div class="date-input-wrapper">
                <input 
                  type="date" 
                  v-model="form.fecha"
                  :min="fechaMinima"
                  :max="fechaMaxima"
                  @change="validarFechaSeleccionada"
                  class="date-input-modern"
                />
                <div class="date-icon">📅</div>
              </div>
              <div class="dias-rapidos">
                <button 
                  v-for="dia in diasRapidos" 
                  :key="dia.label"
                  @click="seleccionarDiaRapido(dia)"
                  class="dia-rapido-btn"
                  :class="{ active: dia.fecha === form.fecha }"
                >
                  {{ dia.label }}
                </button>
              </div>
            </div>
          </div>
        </transition>

        <!-- SELECTOR DE HORA TIPO RELOJ MEJORADO -->
        <transition name="scale-fade">
          <div v-if="form.fecha" class="input-group enhanced">
            <label class="label-modern">
              <span class="label-icon">🕐</span>
              <span>Seleccionar Horario</span>
            </label>
            <div class="horarios-wrapper">
              <div class="time-selector-modern">
                <div class="time-display" @click="toggleTimeSelector">
                  <span class="selected-time">{{ form.hora || 'Seleccionar hora' }}</span>
                  <span class="time-arrow">▼</span>
                </div>
                <transition name="slide-fade">
                  <div v-if="showTimeSelector" class="time-selector-dropdown">
                    <div class="time-sections">
                      <div class="time-section" v-for="(bloque, idx) in bloquesHorarios" :key="idx">
                        <div class="time-section-title">{{ bloque.titulo }}</div>
                        <div class="time-options">
                          <button
                            v-for="h in bloque.horarios"
                            :key="h"
                            type="button"
                            class="time-option"
                            :class="{ 
                              selected: form.hora === h,
                              disabled: !estaHorarioDisponible(h)
                            }"
                            @click="seleccionarHora(h)"
                            :disabled="!estaHorarioDisponible(h)"
                          >
                            <span class="time-text">{{ h }}</span>
                            <span v-if="!estaHorarioDisponible(h)" class="time-badge">Ocupado</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </transition>
              </div>
            </div>
          </div>
        </transition>

        <!-- FORMA DE PAGO PREMIUM -->
        <transition name="scale-fade">
          <div v-if="form.hora" class="input-group enhanced">
            <label class="label-modern">
              <span class="label-icon">💳</span>
              <span>Forma de Pago</span>
            </label>
            
            <div class="pago-cards">
              <label class="pago-card" :class="{ active: form.tipo_pago === 'SENA_50' }">
                <input type="radio" v-model="form.tipo_pago" value="SENA_50" />
                <div class="pago-card-content">
                  <div class="pago-icon">💰</div>
                  <div class="pago-details">
                    <span class="pago-title">Seña 50%</span>
                    <span class="pago-amount">${{ calcularSena() }}</span>
                    <span class="pago-desc">Cliente paga seña ahora</span>
                  </div>
                  <div class="check-circle">
                    <span v-if="form.tipo_pago === 'SENA_50'">✓</span>
                  </div>
                </div>
              </label>

              <label class="pago-card" :class="{ active: form.tipo_pago === 'TOTAL' }">
                <input type="radio" v-model="form.tipo_pago" value="TOTAL" />
                <div class="pago-card-content">
                  <div class="pago-icon">💵</div>
                  <div class="pago-details">
                    <span class="pago-title">Pago Total</span>
                    <span class="pago-amount">${{ calcularTotal() }}</span>
                    <span class="pago-desc">Cliente paga todo ahora</span>
                  </div>
                  <div class="check-circle">
                    <span v-if="form.tipo_pago === 'TOTAL'">✓</span>
                  </div>
                </div>
              </label>
            </div>

            <!-- MEDIO DE PAGO -->
            <transition name="slide-fade">
              <div v-if="form.tipo_pago" class="medio-pago-wrapper">
                <label class="section-label">Medio de Pago</label>
                <div class="medio-cards">
                  <label class="medio-card" :class="{ active: form.medio_pago === 'EFECTIVO' }">
                    <input type="radio" v-model="form.medio_pago" value="EFECTIVO" />
                    <div class="medio-icon">💵</div>
                    <div class="medio-text">
                      <span class="medio-title">Efectivo</span>
                      <span class="medio-desc">Pago en local</span>
                    </div>
                  </label>

                  <label class="medio-card" :class="{ active: form.medio_pago === 'MERCADO_PAGO' }">
                    <input type="radio" v-model="form.medio_pago" value="MERCADO_PAGO" />
                    <div class="medio-icon">📱</div>
                    <div class="medio-text">
                      <span class="medio-title">Mercado Pago</span>
                      <span class="medio-desc">Pago online</span>
                    </div>
                  </label>
                </div>
              </div>
            </transition>
          </div>
        </transition>

        <!-- BOTÓN PRINCIPAL CON ANIMACIÓN -->
        <div class="button-wrapper">
          <button 
            @click="crearTurno" 
            type="button" 
            class="btn-registrar-premium"
            :disabled="!formularioValido"
          >
            <span class="btn-icon">✨</span>
            <span class="btn-text">{{ textoBoton }}</span>
            <div class="btn-shine"></div>
          </button>
        </div>

        <!-- MENSAJE CON ANIMACIÓN -->
        <transition name="bounce">
          <div v-if="mensaje" class="mensaje-premium" :class="{ error: mensaje.includes('❌') }">
            <span class="mensaje-icon">{{ mensaje.includes('❌') ? '❌' : '✅' }}</span>
            <span class="mensaje-text">{{ mensaje }}</span>
          </div>
        </transition>
      </div>
    </div>

    <!-- MODAL DE INSTRUCCIONES QR MEJORADO -->
    <transition name="modal-fade">
      <div v-if="mostrarInstruccionesMP" class="modal-overlay" @click.self="cerrarInstrucciones">
        <div class="modal-qr">
          <div class="modal-header">
            <h3>📱 Pago con Mercado Pago</h3>
            <button @click="cerrarInstrucciones" class="btn-close">✕</button>
          </div>

          <div class="pasos-pago">
            <div class="paso" v-for="(paso, idx) in pasosPago" :key="idx">
              <div class="paso-numero">{{ idx + 1 }}</div>
              <div class="paso-content">
                <span class="paso-text">{{ paso }}</span>
              </div>
            </div>
          </div>

          <div class="info-pago">
            <div class="info-row">
              <span class="info-label">Cliente:</span>
              <span class="info-value">{{ turnoActual?.cliente_nombre }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Concepto:</span>
              <span class="info-value">{{ turnoActual?.tipo_pago === 'SENA_50' ? 'Seña 50%' : 'Pago completo' }}</span>
            </div>
            <div class="info-row total">
              <span class="info-label">Monto a pagar:</span>
              <span class="info-value">${{ montoAPagar }}</span>
            </div>
          </div>

          <div class="modal-actions">
            <button @click="marcarComoPagado" class="btn-modal-confirm">
              <span>✅</span> Marcar como Pagado
            </button>
            <button @click="cerrarInstrucciones" class="btn-modal-cancel">
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        canal: 'PRESENCIAL',
        cliente: null,
        clienteNombre: "",
        peluquero: "",
        servicios_ids: [],
        tipo_pago: "SENA_50",
        medio_pago: "EFECTIVO",
        hora: "",
        fecha: ""
      },
      clientesSugeridos: [],
      peluqueros: [],
      servicios: [],
      turnosOcupados: [],
      mensaje: "",
      fechaSeleccionada: null,
      proximosDias: [],
      horariosDisponibles: [],
      diasSemana: ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'],
      mostrarInstruccionesMP: false,
      turnoActual: null,
      montoAPagar: 0,
      pasosPago: [
        'Cliente escanea el QR fijo del mostrador',
        'Ingresa el monto exacto mostrado',
        'Completa el pago en la app de Mercado Pago',
        'Muestra el comprobante al personal'
      ],
      showTimeSelector: false,
      fechaMinima: '',
      fechaMaxima: ''
    };
  },
  computed: {
    formularioValido() {
      return this.form.cliente && 
             this.form.peluquero && 
             this.form.servicios_ids.length > 0 &&
             this.form.fecha && 
             this.form.hora &&
             this.form.tipo_pago &&
             this.form.medio_pago;
    },
    textoBoton() {
      const monto = this.form.tipo_pago === 'SENA_50' ? this.calcularSena() : this.calcularTotal();
      const medio = this.form.medio_pago === 'EFECTIVO' ? 'Efectivo' : 'Mercado Pago';
      
      if (this.form.tipo_pago === 'SENA_50') {
        return `Registrar Seña - $${monto} (${medio})`;
      } else {
        return `Registrar Pago Total - $${monto} (${medio})`;
      }
    },
    bloquesHorarios() {
      const manana = [];
      const tarde = [];
      
      // Mañana: 08:00 a 12:00
      for (let h = 8; h < 12; h++) {
        for (let m = 0; m < 60; m += 20) {
          manana.push(`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`);
        }
      }
      
      // Tarde: 15:00 a 20:00
      for (let h = 15; h < 20; h++) {
        for (let m = 0; m < 60; m += 20) {
          tarde.push(`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`);
        }
      }
      
      this.horariosDisponibles = [...manana, ...tarde];
      
      return [
        { titulo: '🌅 Mañana', horarios: manana },
        { titulo: '🌆 Tarde', horarios: tarde }
      ];
    },
    diasRapidos() {
      const hoy = new Date();
      const dias = [];
      
      for (let i = 0; i < 7; i++) {
        const fecha = new Date(hoy);
        fecha.setDate(hoy.getDate() + i);
        
        // Saltar domingos (0 es domingo)
        if (fecha.getDay() === 0) continue;
        
        let label = '';
        if (i === 0) label = 'Hoy';
        else if (i === 1) label = 'Mañana';
        else label = this.diasSemana[fecha.getDay()];
        
        dias.push({
          label,
          fecha: this.formatoFecha(fecha)
        });
      }
      
      return dias;
    }
  },
  methods: {
    async buscarCliente() {
      const termino = this.form.clienteNombre.trim();
      if (!termino) {
        this.clientesSugeridos = [];
        this.form.cliente = null;
        return;
      }
      try {
        const res = await fetch(`http://localhost:8000/usuarios/api/clientes/?q=${encodeURIComponent(termino)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        this.clientesSugeridos = Array.isArray(data.results) ? data.results : [];
      } catch (err) {
        console.error('Error al buscar clientes:', err);
        this.clientesSugeridos = [];
      }
    },
    
    seleccionarCliente(cliente) {
      this.form.cliente = cliente.id;
      this.form.clienteNombre = `${cliente.nombre} ${cliente.apellido}`;
      this.clientesSugeridos = [];
    },
    
    async cargarServicios() {
      try {
        const res = await fetch("http://localhost:8000/usuarios/api/servicios/");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        this.servicios = data || [];
      } catch (err) {
        console.error("Error al cargar servicios:", err);
      }
    },
    
    async cargarPeluqueros() {
      try {
        const res = await fetch("http://localhost:8000/usuarios/api/peluqueros/");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        this.peluqueros = data || [];
      } catch (err) {
        console.error("Error al cargar peluqueros:", err);
        this.peluqueros = [];
      }
    },
    
    async cargarTurnosOcupados() {
      try {
        const res = await fetch("http://localhost:8000/usuarios/api/turnos/");
        if (res.ok) {
          const data = await res.json();
          this.turnosOcupados = data;
        }
      } catch (err) {
        console.error("Error al cargar turnos ocupados:", err);
      }
    },
    
    toggleServicio(servicio) {
      const index = this.form.servicios_ids.indexOf(servicio.id);
      if (index === -1) {
        this.form.servicios_ids.push(servicio.id);
      } else {
        this.form.servicios_ids.splice(index, 1);
      }
    },
    
    getServicioNombre(servicioId) {
      const servicio = this.servicios.find(s => s.id === servicioId);
      return servicio ? servicio.nombre : '';
    },
    
    getServicioPrecio(servicioId) {
      const servicio = this.servicios.find(s => s.id === servicioId);
      return servicio ? servicio.precio : 0;
    },
    
    calcularTotal() {
      return this.form.servicios_ids.reduce((total, servicioId) => {
        return total + parseFloat(this.getServicioPrecio(servicioId) || 0);
      }, 0);
    },
    
    calcularSena() {
      return this.calcularTotal() * 0.5;
    },
    
    generarProximosDias() {
      const dias = [];
      const hoy = new Date();
      let contador = 0;
      let offset = 0;
      
      while (contador < 7) {
        const fecha = new Date(hoy);
        fecha.setDate(hoy.getDate() + offset);
        
        if (fecha.getDay() !== 0) {
          dias.push(fecha);
          contador++;
        }
        offset++;
      }
      this.proximosDias = dias;
    },
    
    seleccionarFecha(fecha) {
      if (!this.estaDisponible(fecha)) return;
      this.fechaSeleccionada = fecha;
      this.form.hora = "";
      this.form.fecha = this.formatoFecha(fecha);
    },
    
    formatoFecha(fecha) {
      const anio = fecha.getFullYear();
      const mes = String(fecha.getMonth() + 1).padStart(2,'0');
      const dia = String(fecha.getDate()).padStart(2,'0');
      return `${anio}-${mes}-${dia}`;
    },
    
    estaDisponible(fecha) {
      if (fecha.getDay() === 0) return false;
      
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      const fechaComparar = new Date(fecha);
      fechaComparar.setHours(0, 0, 0, 0);
      
      return fechaComparar >= hoy;
    },
    
    estaHorarioDisponible(horario) {
      if (!this.form.fecha || !this.form.peluquero) return false;
      
      const turnoOcupado = this.turnosOcupados.find(t => 
        t.fecha === this.form.fecha && 
        t.hora === horario && 
        t.peluquero_id == this.form.peluquero &&
        t.estado !== 'CANCELADO'
      );
      
      return !turnoOcupado;
    },

    limpiarFechaHora() {
      this.fechaSeleccionada = null;
      this.form.hora = "";
      this.form.fecha = "";
    },

    mostrarInstruccionesPago(turnoData) {
      this.turnoActual = turnoData;
      this.montoAPagar = turnoData.monto_seña || turnoData.monto_total;
      this.mostrarInstruccionesMP = true;
      this.mensaje = "✅ Turno creado. Cliente debe escanear QR fijo del mostrador.";
    },

    cerrarInstrucciones() {
      this.mostrarInstruccionesMP = false;
      this.turnoActual = null;
      this.mensaje = "✅ Turno registrado. El cliente puede pagar cuando quiera.";
    },

    async marcarComoPagado() {
      try {
        this.mensaje = "🔄 Marcando como pagado...";
        this.mostrarInstruccionesMP = false;
        this.mensaje = "✅ Pago confirmado. Turno activado.";
        this.limpiarFormulario();
      } catch (err) {
        console.error("Error marcando como pagado:", err);
        this.mensaje = "❌ Error al confirmar pago.";
      }
    },
    
    async crearTurno() {
      if (!this.formularioValido) {
        this.mensaje = "❌ Completa todos los campos obligatorios.";
        return;
      }

      const payload = {
        cliente_id: this.form.cliente,
        peluquero_id: this.form.peluquero,
        servicios_ids: this.form.servicios_ids,
        fecha: this.form.fecha,
        hora: this.form.hora,
        canal: 'PRESENCIAL',
        tipo_pago: this.form.tipo_pago,
        medio_pago: this.form.medio_pago,
        monto_total: this.calcularTotal(),
        monto_seña: this.form.tipo_pago === 'SENA_50' ? this.calcularSena() : 0
      };

      try {
        this.mensaje = "🔄 Creando turno...";
        
        const res = await fetch("http://localhost:8000/usuarios/api/turnos/crear/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        
        const data = await res.json();
        
        if (res.ok && data.status === 'ok') {
          if (this.form.medio_pago === 'MERCADO_PAGO') {
            this.mostrarInstruccionesPago(data);
          } else {
            this.mensaje = "✅ Turno registrado correctamente.";
            this.limpiarFormulario();
          }
        } else {
          this.mensaje = data.message || "❌ Error al registrar el turno.";
        }
      } catch (err) {
        console.error("Error:", err);
        this.mensaje = "❌ No se pudo conectar con el servidor.";
      }
    },
    
    limpiarFormulario() {
      this.form = {
        canal: 'PRESENCIAL',
        cliente: null,
        clienteNombre: "",
        peluquero: "",
        servicios_ids: [],
        tipo_pago: "SENA_50",
        medio_pago: "EFECTIVO",
        hora: "",
        fecha: ""
      };
      this.fechaSeleccionada = null;
      this.clientesSugeridos = [];
      this.showTimeSelector = false;
      
      setTimeout(() => {
        if (this.mensaje.includes('✅')) {
          this.mensaje = "";
        }
      }, 5000);
    },
    
    esHoy(fecha) {
      const hoy = new Date();
      return fecha.toDateString() === hoy.toDateString();
    },
    
    getMesNombre(mes) {
      const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
      return meses[mes];
    },
    
    // Nuevos métodos para el selector de fecha y hora mejorado
    calcularFechasLimite() {
      const hoy = new Date();
      this.fechaMinima = this.formatoFecha(hoy);
      
      const maxFecha = new Date(hoy);
      maxFecha.setDate(hoy.getDate() + 6); // 7 días incluyendo hoy
      this.fechaMaxima = this.formatoFecha(maxFecha);
    },
    
    validarFechaSeleccionada() {
      if (this.form.fecha) {
        const fecha = new Date(this.form.fecha);
        if (fecha.getDay() === 0) { // Domingo
          this.mensaje = "❌ Los domingos no hay atención";
          this.form.fecha = "";
          return;
        }
        this.form.hora = ""; // Resetear hora al cambiar fecha
      }
    },
    
    seleccionarDiaRapido(dia) {
      this.form.fecha = dia.fecha;
      this.form.hora = ""; // Resetear hora
    },
    
    toggleTimeSelector() {
      this.showTimeSelector = !this.showTimeSelector;
    },
    
    seleccionarHora(hora) {
      this.form.hora = hora;
      this.showTimeSelector = false;
    }
  },
  
  mounted() {
    this.cargarServicios();
    this.cargarPeluqueros();
    this.cargarTurnosOcupados();
    this.generarProximosDias();
    this.calcularFechasLimite();
  }
};
</script>

<style scoped>
/* ============================================ */
/* 🎨 DISEÑO ULTRA PREMIUM - HAIRSOFT */
/* ============================================ */

.form-container {
  min-height: 100%;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.form-card {
  width: 100%;
  max-width: 1200px;
  background: var(--bg-secondary);
  border-radius: 32px;
  overflow: hidden;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px var(--border-color);
  animation: cardSlideUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes cardSlideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* HEADER CON GRADIENTE */
.card-header {
  position: relative;
  padding: 40px;
  background: linear-gradient(135deg, var(--accent-color) 0%, #7c3aed 100%);
  overflow: hidden;
}

.card-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

.header-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, 
    transparent 0%,
    rgba(255,255,255,0.5) 50%,
    transparent 100%
  );
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.header-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-wrapper {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.icon-emoji {
  font-size: 2.5rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.header-text {
  flex: 1;
}

.form-title {
  margin: 0;
  color: white;
  font-size: 2.5rem;
  font-weight: 800;
  letter-spacing: -1px;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
}

.form-subtitle {
  margin: 8px 0 0 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  font-weight: 500;
}

/* CONTENIDO DEL FORMULARIO */
.form-content {
  padding: 50px;
}

/* GRUPOS DE INPUT MEJORADOS */
.input-group {
  margin-bottom: 35px;
}

.input-group.enhanced {
  animation: fadeInUp 0.5s ease-out backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.label-modern {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.label-icon {
  font-size: 1.3rem;
  filter: drop-shadow(0 2px 4px rgba(139, 92, 246, 0.3));
}

/* BÚSQUEDA DE CLIENTE */
.search-wrapper {
  position: relative;
}

.input-modern {
  width: 100%;
  padding: 18px 55px 18px 20px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.input-modern:focus {
  border-color: var(--accent-color);
  box-shadow: 
    0 0 0 4px rgba(139, 92, 246, 0.1),
    0 8px 24px rgba(139, 92, 246, 0.2);
  transform: translateY(-2px);
}

.search-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  opacity: 0.5;
  pointer-events: none;
}

/* SUGERENCIAS DE CLIENTE */
.sugerencias-list {
  list-style: none;
  margin: 10px 0 0 0;
  padding: 0;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-height: 300px;
  overflow-y: auto;
}

.sugerencia-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid var(--border-color);
}

.sugerencia-item:last-child {
  border-bottom: none;
}

.sugerencia-item:hover {
  background: var(--hover-bg);
  padding-left: 25px;
}

.cliente-avatar {
  width: 45px;
  height: 45px;
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.2rem;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.cliente-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cliente-nombre {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1rem;
}

.cliente-dni {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.select-arrow {
  color: var(--accent-color);
  font-size: 1.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sugerencia-item:hover .select-arrow {
  opacity: 1;
}

/* SELECT MODERNO */
.select-wrapper {
  position: relative;
}

.select-modern {
  width: 100%;
  padding: 18px 50px 18px 20px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
  outline: none;
  cursor: pointer;
  appearance: none;
}

.select-modern:focus {
  border-color: var(--accent-color);
  box-shadow: 
    0 0 0 4px rgba(139, 92, 246, 0.1),
    0 8px 24px rgba(139, 92, 246, 0.2);
}

.select-arrow-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  pointer-events: none;
  transition: transform 0.3s ease;
}

.select-modern:focus + .select-arrow-icon {
  transform: translateY(-50%) rotate(180deg);
  color: var(--accent-color);
}

/* SERVICIOS GRID PREMIUM */
.servicios-grid-premium {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.servicio-card {
  position: relative;
  padding: 24px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.servicio-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.servicio-card:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: var(--accent-color);
  box-shadow: 0 20px 60px rgba(139, 92, 246, 0.3);
}

.servicio-card.selected {
  border-color: var(--accent-color);
  box-shadow: 0 20px 60px rgba(139, 92, 246, 0.4);
}

.servicio-card.selected::before {
  opacity: 0.1;
}

.card-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.6s ease;
  pointer-events: none;
}

.servicio-card:hover .card-glow {
  transform: translate(-50%, -50%) scale(1);
}

.servicio-check {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 32px;
  height: 32px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 1;
}

.servicio-card.selected .servicio-check {
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  border-color: var(--accent-color);
  transform: scale(1.1);
}

.check-icon {
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
}

.servicio-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.servicio-nombre {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.servicio-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.servicio-precio {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--accent-color);
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.servicio-duracion {
  font-size: 0.9rem;
  color: var(--text-secondary);
  padding: 6px 12px;
  background: var(--bg-secondary);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

/* RESUMEN FLOTANTE */
.resumen-flotante {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.05));
  border: 2px solid var(--accent-color);
  border-radius: 24px;
  padding: 30px;
  margin: 35px 0;
  box-shadow: 
    0 20px 60px rgba(139, 92, 246, 0.2),
    inset 0 0 60px rgba(139, 92, 246, 0.05);
  position: relative;
  overflow: hidden;
}

.resumen-flotante::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.resumen-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.resumen-icon {
  font-size: 1.8rem;
}

.resumen-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
}

.servicios-seleccionados {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.servicio-seleccionado {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.servicio-seleccionado:last-child {
  border-bottom: none;
}

.servicio-dot {
  width: 8px;
  height: 8px;
  background: var(--accent-color);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--accent-color);
}

.servicio-text {
  flex: 1;
  color: var(--text-primary);
  font-weight: 600;
}

.servicio-price {
  color: var(--accent-color);
  font-weight: 700;
  font-size: 1.1rem;
}

.total-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0 0 0;
  border-top: 2px solid var(--accent-color);
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-primary);
  position: relative;
  z-index: 1;
}

.total-amount {
  font-size: 1.8rem;
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* CALENDARIO MODERNO MEJORADO */
.calendario-wrapper {
  background: var(--bg-primary);
  border-radius: 20px;
  padding: 25px;
  border: 2px solid var(--border-color);
}

.date-input-wrapper {
  position: relative;
  margin-bottom: 20px;
}

.date-input-modern {
  width: 100%;
  padding: 18px 55px 18px 20px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  cursor: pointer;
}

.date-input-modern:focus {
  border-color: var(--accent-color);
  box-shadow: 
    0 0 0 4px rgba(139, 92, 246, 0.1),
    0 8px 24px rgba(139, 92, 246, 0.2);
  transform: translateY(-2px);
}

.date-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  opacity: 0.5;
  pointer-events: none;
}

.dias-rapidos {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.dia-rapido-btn {
  padding: 12px 20px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 100px;
  text-align: center;
}

.dia-rapido-btn:hover {
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
}

.dia-rapido-btn.active {
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  border-color: var(--accent-color);
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

/* SELECTOR DE HORA MEJORADO */
.horarios-wrapper {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.time-selector-modern {
  position: relative;
}

.time-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.time-display:hover {
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
}

.selected-time {
  color: var(--text-primary);
  font-weight: 600;
}

.time-arrow {
  color: var(--text-secondary);
  transition: transform 0.3s ease;
}

.time-selector-modern.open .time-arrow {
  transform: rotate(180deg);
}

.time-selector-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  margin-top: 8px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.time-sections {
  padding: 20px;
}

.time-section {
  margin-bottom: 25px;
}

.time-section:last-child {
  margin-bottom: 0;
}

.time-section-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.time-option {
  position: relative;
  padding: 14px 12px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.time-option:hover:not(.disabled) {
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
}

.time-option.selected {
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.time-option.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(1);
}

.time-text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.time-option.selected .time-text {
  color: white;
}

.time-badge {
  font-size: 0.7rem;
  color: #ef4444;
  font-weight: 600;
}

/* CARDS DE PAGO */
.pago-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.pago-card {
  position: relative;
  cursor: pointer;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s ease;
}

.pago-card input[type="radio"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.pago-card-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.pago-card-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.1), transparent);
  transition: left 0.6s ease;
}

.pago-card:hover .pago-card-content::before {
  left: 100%;
}

.pago-card:hover .pago-card-content {
  transform: translateY(-4px);
  border-color: var(--accent-color);
  box-shadow: 0 15px 40px rgba(139, 92, 246, 0.2);
}

.pago-card.active .pago-card-content {
  border-color: var(--accent-color);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.05));
  box-shadow: 0 15px 40px rgba(139, 92, 246, 0.3);
}

.pago-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.pago-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pago-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.pago-amount {
  font-size: 1.6rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.pago-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.check-circle {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.pago-card.active .check-circle {
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  border-color: var(--accent-color);
  color: white;
  transform: scale(1.2);
}

/* MEDIOS DE PAGO */
.medio-pago-wrapper {
  margin-top: 25px;
  padding-top: 25px;
  border-top: 1px solid var(--border-color);
}

.section-label {
  display: block;
  margin-bottom: 15px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.medio-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.medio-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.medio-card input[type="radio"] {
  position: absolute;
  opacity: 0;
}

.medio-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 0;
  background: var(--accent-color);
  transition: height 0.3s ease;
}

.medio-card:hover {
  border-color: var(--accent-color);
  transform: translateX(4px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.2);
}

.medio-card:hover::before {
  height: 100%;
}

.medio-card.active {
  border-color: var(--accent-color);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.05));
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}

.medio-card.active::before {
  height: 100%;
}

.medio-icon {
  font-size: 2rem;
}

.medio-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.medio-title {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 1rem;
}

.medio-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* BOTÓN PRINCIPAL PREMIUM */
.button-wrapper {
  margin: 40px 0 20px 0;
}

.btn-registrar-premium {
  position: relative;
  width: 100%;
  padding: 22px 40px;
  background: linear-gradient(135deg, var(--accent-color) 0%, #7c3aed 100%);
  color: white;
  border: none;
  border-radius: 18px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 0 15px 40px rgba(139, 92, 246, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.btn-registrar-premium::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.btn-registrar-premium:hover::before {
  left: 100%;
}

.btn-registrar-premium:hover:not(:disabled) {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 20px 60px rgba(139, 92, 246, 0.6);
}

.btn-registrar-premium:active:not(:disabled) {
  transform: translateY(-2px) scale(1.01);
}

.btn-registrar-premium:disabled {
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: not-allowed;
  box-shadow: none;
  border: 2px solid var(--border-color);
}

.btn-icon {
  font-size: 1.5rem;
}

.btn-text {
  position: relative;
  z-index: 1;
}

.btn-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  animation: shine 3s infinite;
  pointer-events: none;
}

@keyframes shine {
  0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1); opacity: 0; }
}

/* MENSAJE PREMIUM */
.mensaje-premium {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px 30px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 1rem;
  margin-top: 20px;
  animation: messageSlide 0.5s ease-out;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mensaje-premium:not(.error) {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.1));
  border: 2px solid #10b981;
  color: #10b981;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
}

.mensaje-premium.error {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.1));
  border: 2px solid #ef4444;
  color: #ef4444;
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.2);
}

.mensaje-icon {
  font-size: 1.5rem;
}

/* MODAL QR MEJORADO */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-qr {
  background: var(--bg-secondary);
  border-radius: 28px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.5);
  border: 2px solid var(--border-color);
  animation: modalZoomIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalZoomIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30px;
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  color: white;
  border-radius: 28px 28px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 800;
}

.btn-close {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.pasos-pago {
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.paso {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 16px;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
}

.paso:hover {
  border-color: var(--accent-color);
  transform: translateX(8px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.2);
}

.paso-numero {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  flex-shrink: 0;
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.paso-content {
  flex: 1;
  display: flex;
  align-items: center;
}

.paso-text {
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.6;
  font-weight: 600;
}

.info-pago {
  margin: 0 30px 30px 30px;
  padding: 25px;
  background: var(--bg-primary);
  border-radius: 16px;
  border-left: 4px solid var(--accent-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row.total {
  padding-top: 20px;
  margin-top: 10px;
  border-top: 2px solid var(--accent-color);
  border-bottom: none;
}

.info-label {
  color: var(--text-secondary);
  font-weight: 600;
}

.info-value {
  color: var(--text-primary);
  font-weight: 700;
  font-size: 1.1rem;
}

.info-row.total .info-value {
  font-size: 1.6rem;
  background: linear-gradient(135deg, var(--accent-color), #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.modal-actions {
  display: flex;
  gap: 15px;
  padding: 0 30px 30px 30px;
}

.btn-modal-confirm {
  flex: 1;
  padding: 16px 24px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
}

.btn-modal-confirm:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(16, 185, 129, 0.4);
}

.btn-modal-cancel {
  padding: 16px 24px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  border-radius: 14px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-modal-cancel:hover {
  border-color: var(--accent-color);
  background: var(--hover-bg);
  transform: translateY(-2px);
}

/* TRANSICIONES Y ANIMACIONES */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.scale-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.scale-fade-leave-active {
  transition: all 0.2s ease-in;
}

.scale-fade-enter-from {
  transform: scale(0.95);
  opacity: 0;
}

.scale-fade-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

.bounce-enter-active {
  animation: bounceIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.bounce-leave-active {
  animation: bounceOut 0.3s ease-in;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(-20px);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  100% {
    transform: scale(1) translateY(0);
  }
}

@keyframes bounceOut {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0.3) translateY(-20px);
    opacity: 0;
  }
}

.modal-fade-enter-active {
  transition: all 0.3s ease-out;
}

.modal-fade-leave-active {
  transition: all 0.2s ease-in;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-qr {
  transform: scale(0.9);
}

.modal-fade-leave-to .modal-qr {
  transform: scale(0.9);
}

/* RESPONSIVE DESIGN */
@media (max-width: 1024px) {
  .servicios-grid-premium {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
  
  .time-options {
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  }
}

@media (max-width: 768px) {
  .form-content {
    padding: 30px 25px;
  }
  
  .card-header {
    padding: 30px 25px;
  }
  
  .form-title {
    font-size: 2rem;
  }
  
  .icon-wrapper {
    width: 60px;
    height: 60px;
  }
  
  .icon-emoji {
    font-size: 2rem;
  }
  
  .servicios-grid-premium {
    grid-template-columns: 1fr;
  }
  
  .pago-cards {
    grid-template-columns: 1fr;
  }
  
  .medio-cards {
    grid-template-columns: 1fr;
  }
  
  .time-options {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .dias-rapidos {
    flex-direction: column;
  }
  
  .dia-rapido-btn {
    min-width: auto;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .btn-modal-confirm,
  .btn-modal-cancel {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .form-content {
    padding: 20px 15px;
  }
  
  .card-header {
    padding: 25px 15px;
  }
  
  .form-title {
    font-size: 1.6rem;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .time-options {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .btn-registrar-premium {
    font-size: 1rem;
    padding: 18px 30px;
  }
}

/* SCROLLBAR PERSONALIZADO PARA MODAL */
.modal-qr::-webkit-scrollbar {
  width: 8px;
}

.modal-qr::-webkit-scrollbar-track {
  background: var(--bg-primary);
  border-radius: 10px;
}

.modal-qr::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
  transition: background 0.3s ease;
}

.modal-qr::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

/* SCROLLBAR PARA SUGERENCIAS */
.sugerencias-list::-webkit-scrollbar {
  width: 6px;
}

.sugerencias-list::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 10px;
}

.sugerencias-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
}

.sugerencias-list::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

/* ANIMACIÓN DE CARGA PARA LOS INPUTS */
.input-modern:focus,
.select-modern:focus,
.date-input-modern:focus {
  animation: inputPulse 0.6s ease-out;
}

@keyframes inputPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(139, 92, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
  }
}

/* EFECTO HOVER PARA ELEMENTOS INTERACTIVOS */
.servicio-card,
.dia-rapido-btn,
.time-option,
.pago-card,
.medio-card {
  will-change: transform;
}

/* OPTIMIZACIÓN DE RENDIMIENTO */
* {
  -webkit-tap-highlight-color: transparent;
}

button,
.servicio-card,
.dia-rapido-btn,
.time-option,
.pago-card,
.medio-card,
.sugerencia-item {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
}

/* ACCESIBILIDAD */
.input-modern:focus-visible,
.select-modern:focus-visible,
.date-input-modern:focus-visible,
.btn-registrar-premium:focus-visible {
  outline: 3px solid var(--accent-color);
  outline-offset: 3px;
}

/* MODO CLARO - AJUSTES ESPECÍFICOS */
html.light-mode .card-glow {
  background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
}

html.light-mode .resumen-flotante::before {
  background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%);
}

html.light-mode .btn-shine {
  background: radial-gradient(circle, rgba(255,255,255,0.5) 0%, transparent 70%);
}
</style>