<template>
  <div class="pedido-container">
    <div class="card-modern">

      <!-- =============================== -->
      <!-- 1) CLIENTE -->
      <!-- =============================== -->
      <div class="header-section">
        <h2>Registrar Turno Presencial</h2>
        <p class="subtitle">Sistema de reservas en local</p>
      </div>

      <div class="form-content">

        <!-- CLIENTE -->
        <div class="input-group cliente-section">
          <label class="section-label">Buscar Cliente:</label>
          <div class="search-box-improved">
            <span class="search-icon">🔍</span>
            <input
              type="text"
              v-model="form.clienteNombre"
              @input="buscarCliente"
              placeholder="Nombre, apellido o DNI..."
              class="input-modern-improved"
            />
          </div>

          <transition name="slide-fade">
            <ul v-if="clientesSugeridos.length" class="sugerencias-list-improved">
              <li 
                v-for="c in clientesSugeridos" 
                :key="c.id" 
                @click="seleccionarCliente(c)"
                class="sugerencia-item-improved"
              >
                <span class="cliente-avatar">{{ c.nombre.charAt(0) }}</span>
                <div class="cliente-info">
                  <span class="cliente-nombre">{{ c.nombre }} {{ c.apellido }}</span>
                  <span class="cliente-dni">DNI: {{ c.dni }}</span>
                </div>
              </li>
            </ul>
          </transition>
        </div>

        <!-- =============================== -->
        <!-- 2) PELUQUERO -->
        <!-- =============================== -->
        <div class="input-group">
          <label class="section-label">Peluquero:</label>
          <select 
            v-model="form.peluquero" 
            @change="limpiarFechaHora" 
            class="select-modern-rounded"
          >
            <option value="">Seleccione un peluquero</option>
            <option v-for="p in peluqueros" :key="p.id" :value="p.id">
              {{ p.nombre }} {{ p.apellido }}
            </option>
          </select>
        </div>

        <!-- =============================== -->
        <!-- 3) CATEGORÍAS -->
        <!-- =============================== -->
        <div class="input-group">
          <label class="section-label">Seleccionar Categorías</label>
          
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
                  <span 
                    class="checkmark-horizontal" 
                    :class="{ checked: categoriasSeleccionadas.includes(categoria.id) }"
                  >
                    ✓
                  </span>
                </div>
                <div class="categoria-content-horizontal">
                  <span class="categoria-nombre-horizontal">{{ categoria.nombre }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- =============================== -->
        <!-- 4) SERVICIOS POR CATEGORÍA -->
        <!-- =============================== -->
        <transition name="scale-fade">
          <div v-if="categoriasSeleccionadas.length > 0" class="input-group">

            <label class="section-label">
              Servicios Disponibles
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
                  <span 
                    class="checkmark" 
                    :class="{ checked: form.servicios_ids.includes(servicio.id) }"
                  >
                    ✓
                  </span>
                </div>
                <div class="servicio-info">
                  <span class="servicio-nombre">{{ servicio.nombre }}</span>
                  <div class="servicio-details">
                    <span class="servicio-precio">${{ servicio.precio }}</span>
                    <span class="servicio-duracion">{{ servicio.duracion }}min</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </transition>

        <!-- =============================== -->
        <!-- 5) RESUMEN -->
        <!-- =============================== -->
        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0" class="resumen-pedido">
            <div class="resumen-grid">
              <div class="resumen-item total">
                <span>Total</span>
                <span>${{ calcularTotal() }}</span>
              </div>
            </div>
          </div>
        </transition>

        <!-- =============================== -->
        <!-- 6) FECHA -->
        <!-- =============================== -->
        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0 && form.peluquero" class="input-group">
            <label class="section-label">Seleccionar Fecha</label>

            <div class="calendar-container-horizontal">
              <div class="calendar-grid-horizontal">

                <div 
                  v-for="dateInfo in fechasDisponibles" 
                  :key="dateInfo.fullDate"
                  class="date-card-horizontal"
                  :class="{ selected: form.fecha === dateInfo.fullDate, today: dateInfo.isToday }"
                  @click="seleccionarFecha(dateInfo)"
                >
                  <div v-if="dateInfo.isToday" class="today-badge">Hoy</div>
                  <div class="date-content">
                    <span class="day-name">{{ dateInfo.dayName }}</span>
                    <span class="day-number">{{ dateInfo.dayNum }}</span>
                    <span class="month-name">{{ dateInfo.month }}</span>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </transition>

        <!-- =============================== -->
        <!-- 7) HORA -->
        <!-- =============================== -->
        <transition name="scale-fade">
          <div v-if="form.fecha" class="input-group">
            <label class="section-label">Seleccionar Horario</label>

            <div class="time-picker-trigger" @click="abrirModalHora">
              <div class="time-display">
                <span class="time-icon">⏰</span>
                <span class="time-text">{{ form.hora || 'Seleccionar hora' }}</span>
                <span class="time-arrow">▼</span>
              </div>
            </div>

          </div>
        </transition>

        <!-- =============================== -->
        <!-- 8) FORMA DE PAGO -->
        <!-- =============================== -->
        <transition name="scale-fade">
          <div v-if="form.hora" class="input-group">

            <label class="section-label">
              <span class="label-icon">💳</span> Forma de Pago
            </label>

            <div class="pago-container-horizontal">
              <div class="pago-options-horizontal">

                <label 
                  class="pago-option-horizontal" 
                  :class="{ selected: form.tipo_pago === 'SENA_50' }"
                >
                  <input type="radio" v-model="form.tipo_pago" value="SENA_50" />
                  <div class="pago-content-horizontal">
                    <span class="pago-nombre-horizontal">Seña 50%</span>
                    <span class="pago-monto-horizontal">${{ calcularSena() }}</span>
                  </div>
                </label>

                <label 
                  class="pago-option-horizontal" 
                  :class="{ selected: form.tipo_pago === 'TOTAL' }"
                >
                  <input type="radio" v-model="form.tipo_pago" value="TOTAL" />
                  <div class="pago-content-horizontal">
                    <span class="pago-nombre-horizontal">Pago Total</span>
                    <span class="pago-monto-horizontal">${{ calcularTotal() }}</span>
                  </div>
                </label>

              </div>

              <!-- ======================= -->
              <!-- 9) MEDIO DE PAGO -->
              <!-- ======================= -->
              <transition name="slide-fade">
                <div v-if="form.tipo_pago" class="medio-pago-section-horizontal">

                  <label class="section-label">Medio de Pago</label>

                  <div class="medio-pago-options-horizontal">
                    <button 
                      class="medio-pago-btn-horizontal" 
                      :class="{ active: form.medio_pago === 'EFECTIVO' }"
                      @click="form.medio_pago = 'EFECTIVO'"
                    >
                      💵 Efectivo
                    </button>

                    <button 
                      class="medio-pago-btn-horizontal" 
                      :class="{ active: form.medio_pago === 'TARJETA' }"
                      @click="form.medio_pago = 'TARJETA'"
                    >
                      💳 Tarjeta
                    </button>

                    <button 
                      class="medio-pago-btn-horizontal" 
                      :class="{ active: form.medio_pago === 'TRANSFERENCIA' }"
                      @click="form.medio_pago = 'TRANSFERENCIA'"
                    >
                      📱 Transferencia
                    </button>
                  </div>

                  <transition name="scale-fade">
                    <div v-if="form.medio_pago !== 'EFECTIVO'" class="input-comprobante">
                      <label class="section-label small">🧾 Nro. Operación (Opcional)</label>
                      <div class="search-box-improved">
                        <span class="search-icon">#</span>
                        <input
                          type="text"
                          v-model="form.comprobante_id"
                          placeholder="Ej: 1234567890"
                          class="input-modern-improved"
                        />
                      </div>
                    </div>
                  </transition>

                </div>
              </transition>

            </div>
          </div>
        </transition>

        <!-- BOTÓN -->
        <button 
          @click="crearTurno" 
          class="btn-registrar-premium"
          :disabled="!formularioValido"
        >
          <span class="btn-content"><span>✨</span> {{ textoBoton }}</span>
        </button>

        <transition name="bounce">
          <div v-if="mensaje" class="mensaje-premium" :class="{ error: mensaje.includes('❌') }">
            <span class="mensaje-icon">{{ mensaje.includes('❌') ? '❌' : '✅' }}</span>
            <span class="mensaje-text">{{ mensaje }}</span>
          </div>
        </transition>

      </div>
    </div>

    <!-- MODAL HORARIO -->
    <div v-if="mostrarModalHora" class="modal-overlay" @click="cerrarModalHora">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🕐 Seleccionar Horario</h3>
          <button class="modal-close-btn" @click="cerrarModalHora">×</button>
        </div>

        <div class="modal-body">
          <div class="quick-times-modal">
            <h4>🕐 Horarios Disponibles</h4>

            <div class="quick-time-grid-modal">
              <div 
                v-for="hora in horariosDisponibles" 
                :key="hora" 
                class="quick-time-option-modal"
                :class="{ selected: form.hora === hora, disabled: !estaHorarioDisponible(hora) }"
                @click="estaHorarioDisponible(hora) ? seleccionarHoraRapida(hora) : null"
              >
                {{ hora }}
                <span 
                  v-if="!estaHorarioDisponible(hora)" 
                  class="occupied-badge"
                >
                  OCUPADO
                </span>
              </div>

            </div>
          </div>
        </div>

      </div>
    </div>

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
        comprobante_id: "", // <--- NUEVO CAMPO
        hora: "",
        fecha: ""
      },
      clientesSugeridos: [],
      peluqueros: [],
      servicios: [],
      serviciosFiltradosPorCategoria: [],
      categorias: [],
      turnosOcupados: [],
      mensaje: "",
      horariosDisponibles: [],
      categoriasSeleccionadas: [],
      busquedaServicio: "",
      mostrarModalHora: false
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
      return `Confirmar Reserva ($${monto})`;
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
      let filtrados = this.serviciosFiltradosPorCategoria;
      if (this.busquedaServicio) {
        const termino = this.busquedaServicio.toLowerCase();
        filtrados = filtrados.filter(s => s.nombre.toLowerCase().includes(termino));
      }
      return filtrados;
    },
    categoriasSeleccionadasNombres() {
      return this.categoriasSeleccionadas.map(catId => {
        const cat = this.categorias.find(c => c.id === catId);
        return cat ? cat.nombre : '';
      }).join(', ');
    }
  },
  methods: {
    seleccionarCliente(cliente) {
      this.form.cliente = cliente.id;
      this.form.clienteNombre = `${cliente.nombre} ${cliente.apellido}`;
      this.clientesSugeridos = [];
    },
    toggleCategoria(categoriaId) {
      const index = this.categoriasSeleccionadas.indexOf(categoriaId);
      if (index === -1) this.categoriasSeleccionadas.push(categoriaId);
      else this.categoriasSeleccionadas.splice(index, 1);
      this.cargarServiciosPorCategorias();
    },
    formatDate(date) {
      const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
      const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const today = new Date();
      return {
        dayName: days[date.getDay()],
        dayNum: date.getDate(),
        month: months[date.getMonth()],
        fullDate: `${year}-${month}-${day}`,
        isToday: date.toDateString() === today.toDateString()
      };
    },
    formatoFechaLegible(fechaStr) {
      if(!fechaStr) return '';
      const [year, month, day] = fechaStr.split('-');
      const fecha = new Date(year, month - 1, day);
      return fecha.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
    },
    async buscarCliente() {
      const termino = this.form.clienteNombre.trim();
      if (!termino) {
        this.clientesSugeridos = [];
        this.form.cliente = null;
        return;
      }
      try {
        const res = await fetch(`http://localhost:8000/usuarios/api/clientes/?q=${encodeURIComponent(termino)}`);
        const data = await res.json();
        this.clientesSugeridos = data.results || [];
      } catch (err) { this.clientesSugeridos = []; }
    },
    async cargarServicios() {
      try {
        const res = await fetch("http://localhost:8000/usuarios/api/servicios/");
        this.servicios = await res.json();
        this.serviciosFiltradosPorCategoria = [...this.servicios];
      } catch (err) {}
    },
    async cargarCategorias() {
      try {
        const res = await fetch("http://localhost:8000/usuarios/api/categorias/servicios/");
        this.categorias = await res.json();
      } catch (err) {}
    },
    async cargarPeluqueros() {
      try {
        const res = await fetch("http://localhost:8000/usuarios/api/peluqueros/");
        this.peluqueros = await res.json();
      } catch (err) {}
    },
    async cargarTurnosOcupados() {
      try {
        const res = await fetch("http://localhost:8000/usuarios/api/turnos/");
        this.turnosOcupados = await res.json();
      } catch (err) {}
    },
    cargarServiciosPorCategorias() {
      if (this.categoriasSeleccionadas.length === 0) {
        this.serviciosFiltradosPorCategoria = [...this.servicios];
      } else {
        const nombres = this.categoriasSeleccionadas.map(id => this.categorias.find(c => c.id === id)?.nombre);
        this.serviciosFiltradosPorCategoria = this.servicios.filter(s => nombres.includes(s.categoria));
      }
      this.form.servicios_ids = [];
    },
    toggleServicio(servicio) {
      const index = this.form.servicios_ids.indexOf(servicio.id);
      if (index === -1) this.form.servicios_ids.push(servicio.id);
      else this.form.servicios_ids.splice(index, 1);
    },
    getServicioNombre(id) { return this.servicios.find(s => s.id === id)?.nombre || ''; },
    getServicioPrecio(id) { return this.servicios.find(s => s.id === id)?.precio || 0; },
    getCategoriaNombre(cat) { return cat || 'General'; },
    calcularTotal() { return this.form.servicios_ids.reduce((t, id) => t + parseFloat(this.getServicioPrecio(id)), 0); },
    calcularSena() { return this.calcularTotal() * 0.5; },
    seleccionarFecha(info) {
      this.form.fecha = info.fullDate;
      this.form.hora = "";
      this.generarHorarios();
    },
    generarHorarios() {
      const h = [];
      for(let i=8; i<12; i++) for(let m=0; m<60; m+=20) h.push(`${String(i).padStart(2,'0')}:${String(m).padStart(2,'0')}`);
      for(let i=15; i<20; i++) for(let m=0; m<60; m+=20) h.push(`${String(i).padStart(2,'0')}:${String(m).padStart(2,'0')}`);
      this.horariosDisponibles = h;
    },
    estaHorarioDisponible(hora) {
      if(!this.form.fecha || !this.form.peluquero) return false;
      return !this.turnosOcupados.find(t => t.fecha === this.form.fecha && t.hora === hora && t.peluquero_id == this.form.peluquero && t.estado !== 'CANCELADO');
    },
    limpiarFechaHora() { this.form.fecha = ""; this.form.hora = ""; },
    seleccionarHoraRapida(h) { this.form.hora = h; this.cerrarModalHora(); },
    abrirModalHora() { this.mostrarModalHora = true; },
    cerrarModalHora() { this.mostrarModalHora = false; },

    async crearTurno() {
      if (!this.formularioValido) return;
      
      const payload = {
        cliente_id: this.form.cliente,
        peluquero_id: this.form.peluquero,
        servicios_ids: this.form.servicios_ids,
        fecha: this.form.fecha,
        hora: this.form.hora,
        canal: 'PRESENCIAL',
        tipo_pago: this.form.tipo_pago,
        medio_pago: this.form.medio_pago,
        // ✅ AQUÍ ENVIAMOS EL CAMPO CLAVE
        mp_payment_id: (this.form.medio_pago !== 'EFECTIVO') ? this.form.comprobante_id : null,
        monto_total: this.calcularTotal(),
        monto_seña: this.form.tipo_pago === 'SENA_50' ? this.calcularSena() : 0
      };

      try {
        this.mensaje = "🔄 Registrando...";
        const token = localStorage.getItem('token');
        const headers = { 
          "Content-Type": "application/json",
          "Authorization": token ? `Token ${token}` : ''
        };

        const res = await fetch("http://localhost:8000/usuarios/api/turnos/crear/", {
          method: "POST",
          headers: headers,
          body: JSON.stringify(payload),
        });
        
        const data = await res.json();
        
        if (res.ok && data.status === 'ok') {
          this.mensaje = "✅ ¡Turno registrado!";
          setTimeout(() => { this.$router.push('/turnos'); }, 1500);
        } else {
          this.mensaje = data.message || "Error";
        }
      } catch (err) {
        this.mensaje = "Error de conexión";
      }
    },
    
    limpiarFormulario() {
      this.form = { canal: 'PRESENCIAL', cliente: null, peluquero: "", servicios_ids: [], tipo_pago: "SENA_50", medio_pago: "EFECTIVO", comprobante_id: "", hora: "", fecha: "" };
    }
  },
  mounted() {
    this.cargarServicios();
    this.cargarCategorias();
    this.cargarPeluqueros();
    this.cargarTurnosOcupados();
  }
};
</script>

<style scoped>
/* ESTILOS NUEVOS PARA HORARIOS OCUPADOS */

/* Estilo para opciones deshabilitadas en selects */
.time-select-modal option:disabled {
  background-color: #f8d7da;
  color: #721c24;
  opacity: 0.6;
}

/* Estilo mejorado para horarios ocupados en el grid */
.quick-time-option-modal.occupied {
  background: #f8d7da !important;
  color: #721c24 !important;
  border-color: #f5c6cb !important;
  cursor: not-allowed !important;
  opacity: 0.7;
}

.quick-time-option-modal.disabled {
  background: #f8f9fa !important;
  color: #6c757d !important;
  border-color: #e9ecef !important;
  cursor: not-allowed !important;
  opacity: 0.6;
}

.occupied-badge {
  display: block;
  font-size: 0.7em;
  background: #dc3545;
  color: white;
  padding: 2px 6px;
  border-radius: 8px;
  margin-top: 5px;
  font-weight: bold;
}

.ocupados-info {
  margin-top: 15px;
  padding: 12px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  color: #856404;
  font-size: 0.9em;
}

.ocupados-info p {
  margin: 0;
}

/* Mejorar el estilo del botón deshabilitado */
.confirm-time-btn-modal:disabled {
  background: #6c757d !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Efecto hover solo para horarios disponibles */
.quick-time-option-modal:not(.disabled):not(.occupied):hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

/* CORRECCIÓN: Campo cliente ligeramente a la derecha */
.cliente-section {
  margin-left: 10px;
}

/* NUEVO ESTILO: Categorías en disposición horizontal */
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

.categoria-checkbox-horizontal {
  flex-shrink: 0;
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

.categoria-content-horizontal {
  flex: 1;
}

.categoria-nombre-horizontal {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 4px;
  font-size: 1em;
}

.categoria-desc-horizontal {
  font-size: 0.8em;
  color: #6c757d;
}

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
  display: flex;
  align-items: center;
  gap: 12px;
}

.subtitle {
  color: #6c757d;
  font-size: 1.1em;
  margin: 0;
}

.header-icon {
  color: #007bff;
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

.card-modern:hover {
  border-color: #007bff;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15);
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

.search-box-improved {
  position: relative;
  margin-bottom: 8px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 2;
}

.input-modern-improved {
  width: 100%;
  padding: 16px 16px 16px 48px;
  border-radius: 12px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 16px;
  transition: all 0.3s ease;
  color: #1a1a1a;
}

.input-modern-improved:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.sugerencias-list-improved {
  position: absolute;
  width: 100%;
  background: white;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  margin-top: 8px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
}

.sugerencia-item-improved {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f1f3f4;
}

.sugerencia-item-improved:hover {
  background: #f8f9fa;
}

.sugerencia-item-improved:last-child {
  border-bottom: none;
}

.cliente-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1em;
  flex-shrink: 0;
}

.cliente-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.cliente-nombre {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 1em;
}

.cliente-dni {
  font-size: 0.85em;
  color: #6c757d;
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
  scrollbar-width: thin;
  scrollbar-color: #007bff #f1f3f4;
}

.servicios-grid-horizontal::-webkit-scrollbar {
  height: 6px;
}

.servicios-grid-horizontal::-webkit-scrollbar-track {
  background: #f1f3f4;
  border-radius: 3px;
}

.servicios-grid-horizontal::-webkit-scrollbar-thumb {
  background: #007bff;
  border-radius: 3px;
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

.servicio-checkbox {
  flex-shrink: 0;
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

.servicio-info {
  flex: 1;
}

.servicio-nombre {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 6px;
  font-size: 1em;
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
  font-size: 1em;
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

.no-servicios {
  text-align: center;
  padding: 30px 20px;
  color: #6c757d;
}

.no-servicios span {
  font-size: 2em;
  margin-bottom: 10px;
  display: block;
}

.no-servicios p {
  margin: 0;
  font-size: 1.1em;
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

.no-selection p {
  margin: 0;
  font-size: 1em;
}

.selected-categories {
  color: #007bff;
  font-weight: 500;
  font-size: 0.9em;
  margin-left: 8px;
}

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
  scrollbar-width: thin;
  scrollbar-color: #007bff #f1f3f4;
}

.calendar-grid-horizontal::-webkit-scrollbar {
  height: 6px;
}

.calendar-grid-horizontal::-webkit-scrollbar-track {
  background: #f1f3f4;
  border-radius: 3px;
}

.calendar-grid-horizontal::-webkit-scrollbar-thumb {
  background: #007bff;
  border-radius: 3px;
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
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.date-card-horizontal.selected {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: #4facfe;
  box-shadow: 0 25px 50px rgba(79, 172, 254, 0.5);
  transform: scale(1.05);
}

.date-card-horizontal.today {
  border-color: #ffd700;
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
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
}

.date-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  position: relative;
  z-index: 1;
}

.day-name {
  font-size: 0.8rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: color 0.3s;
}

.date-card-horizontal.selected .day-name {
  color: rgba(255, 255, 255, 0.9);
}

.day-number {
  font-size: 2rem;
  font-weight: 900;
  color: #1e293b;
  line-height: 1;
  transition: color 0.3s;
}

.date-card-horizontal.selected .day-number {
  color: white;
}

.month-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: color 0.3s;
}

.date-card-horizontal.selected .month-name {
  color: rgba(255, 255, 255, 0.85);
}

.shine-effect {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 30%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 70%
  );
  transform: translateX(-100%);
  transition: transform 0.6s;
}

.date-card-horizontal:hover .shine-effect {
  transform: translateX(100%);
}

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

.time-picker-trigger:hover .time-arrow {
  transform: rotate(180deg);
}

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

.time-selector-modal-content {
  text-align: center;
}

.time-inputs-modal {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.input-group-modal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.input-label-modal {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.time-select-modal {
  width: 120px;
  height: 90px;
  font-size: 2.5rem;
  font-weight: 900;
  color: #1e293b;
  background: white;
  border: 3px solid #e1e5e9;
  border-radius: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  appearance: none;
  outline: none;
}

.time-select-modal:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 15px 40px rgba(79, 172, 254, 0.3);
  border-color: #4facfe;
}

.time-select-modal:focus {
  border-color: #4facfe;
  box-shadow: 0 15px 40px rgba(79, 172, 254, 0.4);
}

.separator-modal {
  font-size: 3rem;
  font-weight: 900;
  color: #4facfe;
  margin: 0 15px;
  animation: blink 2s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.selected-time-display-modal {
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 25px;
  animation: slideUp 0.4s ease-out;
}

.display-content-modal {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.info-pago {
  color: grey
}
.display-icon-modal {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(79, 172, 254, 0.3);
  flex-shrink: 0;
  color: white;
  font-weight: bold;
  font-size: 1.2em;
}

.display-text-modal {
  flex: 1;
  text-align: left;
}

.display-label-modal {
  font-size: 1rem;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.display-time-modal {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1e293b;
}

.confirm-time-btn-modal {
  width: 100%;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 18px;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 20px rgba(79, 172, 254, 0.4);
}

.confirm-time-btn-modal:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 15px 40px rgba(79, 172, 254, 0.5);
}

.confirm-time-btn-modal:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.time-error-modal {
  margin-top: 15px;
  padding: 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  text-align: center;
  font-size: 1em;
}

.quick-times-modal {
  margin-top: 25px;
}

.quick-times-modal h4 {
  margin: 0 0 20px 0;
  color: #1a1a1a;
  font-size: 1.2em;
  font-weight: 600;
}

.quick-time-grid-modal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
  gap: 12px;
}

.quick-time-option-modal {
  padding: 15px 10px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  color: #1a1a1a;
  text-align: center;
  font-size: 1em;
}

.quick-time-option-modal:hover:not(.disabled):not(.occupied) {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.quick-time-option-modal.selected {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.quick-time-option-modal.disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

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
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 25px 20px;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
  text-align: center;
}

.pago-option-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.1);
}

.pago-option-horizontal.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.pago-content-horizontal {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.pago-nombre-horizontal {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 1.2em;
}

.pago-monto-horizontal {
  color: #28a745;
  font-weight: 800;
  font-size: 1.4em;
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

.medio-pago-options-horizontal {
  display: flex;
  gap: 15px;
}

.medio-pago-btn-horizontal {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 25px 20px;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.medio-pago-btn-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.1);
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
  font-size: 1.1em;
}

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
  align-items: center;
  padding: 8px 0;
  color: #1a1a1a;
  font-size: 1em;
}

.resumen-item.total {
  border-top: 2px solid #dee2e6;
  margin-top: 10px;
  padding-top: 12px;
  font-size: 1.2em;
  font-weight: 700;
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
  background: linear-gradient(135deg, #0056b3, #004085);
}

.btn-registrar-premium:disabled {
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
@keyframes bounce-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@media (max-width: 768px) {
  .pedido-container {
    padding: 15px;
  }
  
  .calendar-grid-horizontal {
    padding: 15px;
  }
  
  .servicios-grid-horizontal {
    flex-direction: column;
    overflow-x: visible;
  }
  
  .servicio-item-horizontal {
    min-width: auto;
  }
  
  .categorias-grid-horizontal {
    flex-direction: column;
  }
  
  .categoria-card-horizontal {
    min-width: auto;
  }
  
  .pago-options-horizontal {
    flex-direction: column;
  }
  
  .medio-pago-options-horizontal {
    flex-direction: column;
  }
  
  .quick-time-grid-modal {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .time-inputs-modal {
    flex-direction: column;
    gap: 20px;
  }
  
  .separator-modal {
    margin: 0;
  }
  
  .modal-content {
    margin: 10px;
    max-height: 95vh;
  }
  
  .cliente-section {
    margin-left: 0;
  }
}
</style>