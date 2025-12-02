<template>
  <div class="pedido-container">
    <div class="card-clean">
      
      <div class="header-section">
        <div class="header-icon-bg">✂️</div>
        <div>
          <h2>Nuevo Turno</h2>
          <p class="subtitle">Reserva presencial rápida</p>
        </div>
      </div>

      <div class="form-content">
        
        <div class="input-group">
          <label class="label-modern">Cliente</label>
          <div class="row-search">
            <div class="search-wrapper">
              <span class="icon-lupa">🔍</span>
              <input
                type="text"
                :value="form.cliente ? form.clienteNombre : busquedaCliente"
                @input="actualizarBusquedaCliente"
                :placeholder="form.cliente ? '' : 'Buscar por nombre o DNI...'"
                :class="['input-glass', { 'cliente-activo': form.cliente }]"
                :readonly="form.cliente !== null"
              />
              <button v-if="form.cliente" @click="limpiarCliente" class="btn-icon-clean" title="Quitar">✕</button>
            </div>
            
            <button @click="irARegistrarCliente" class="btn-nuevo-glass">
              + Nuevo
            </button>
          </div>

          <ul v-if="clientesSugeridos.length && !form.cliente" class="lista-sugerencias">
            <li v-for="c in clientesSugeridos" :key="c.id" @click="seleccionarCliente(c)" class="item-sugerencia">
              <div class="avatar-mini">{{ getInicial(c) }}</div>
              <div class="info-sugerencia">
                <strong>{{ getNombreCompletoCliente(c) }}</strong>
                <small>DNI: {{ c.dni || '---' }}</small>
              </div>
            </li>
          </ul>
          <div v-if="errorCliente" class="msg-error">{{ errorCliente }}</div>
        </div>

        <transition name="slide-in">
          <div v-if="form.cliente" class="input-group">
            <label class="label-modern">Categoría</label>
            <div class="grid-chips">
              <button 
                v-for="categoria in categorias" 
                :key="categoria.id"
                class="chip-glass"
                :class="{ 'chip-active': categoriasSeleccionadas.includes(categoria.id) }"
                @click="toggleCategoria(categoria.id)"
              >
                {{ categoria.nombre }}
              </button>
            </div>
          </div>
        </transition>

        <transition name="slide-in">
          <div v-if="categoriasSeleccionadas.length > 0" class="input-group">
            <label class="label-modern">Servicios Disponibles</label>
            
            <div v-if="serviciosFiltrados.length === 0" class="texto-vacio">No hay servicios en esta categoría.</div>
            
            <div class="grid-servicios">
              <div 
                v-for="servicio in serviciosFiltrados" 
                :key="servicio.id"
                class="card-servicio-mini"
                :class="{ 'servicio-active': form.servicios_ids.includes(servicio.id) }"
                @click="toggleServicio(servicio)"
              >
                <div class="serv-header">
                  <span class="serv-nombre">{{ servicio.nombre }}</span>
                  <div class="checkbox-circle">
                    <span v-if="form.servicios_ids.includes(servicio.id)">✓</span>
                  </div>
                </div>
                <div class="serv-footer">
                  <span class="serv-precio">${{ servicio.precio }}</span>
                  <span class="serv-duracion">⏱ {{ servicio.duracion }} min</span>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <transition name="slide-in">
          <div v-if="form.servicios_ids.length > 0" class="input-group">
            <label class="label-modern">Profesional</label>
            <select v-model="form.peluquero" @change="alCambiarPeluquero" class="input-glass select-arrow">
              <option value="">-- Seleccionar Profesional --</option>
              <option v-for="p in peluqueros" :key="p.id" :value="p.id">
                {{ p.nombre }} {{ p.apellido || '' }}
              </option>
            </select>
          </div>
        </transition>

        <transition name="slide-in">
          <div v-if="form.peluquero" class="input-group">
            <div class="calendar-wrapper-sky">
              <div class="calendar-header-sky">
                <button @click="cambiarMes(-1)" class="btn-nav-sky">‹</button>
                <h3 class="mes-titulo-sky">{{ nombreMesActual }} {{ currentYear }}</h3>
                <button @click="cambiarMes(1)" class="btn-nav-sky">›</button>
              </div>

              <div class="weekdays-grid-sky">
                <div v-for="d in ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb']" :key="d" class="weekday-sky">
                  {{ d }}
                </div>
              </div>

              <div class="days-grid-sky">
                <div v-for="i in startingDayOfWeek" :key="'empty-'+i" class="day-empty"></div>
                
                <button 
                  v-for="day in daysInMonth" 
                  :key="day"
                  class="day-btn-sky"
                  :class="{
                    'is-today': esHoy(day),
                    'is-selected': esDiaSeleccionado(day),
                    'is-disabled': !esDiaSeleccionable(day)
                  }"
                  :disabled="!esDiaSeleccionable(day)"
                  @click="seleccionarDiaCalendario(day)"
                >
                  <span v-if="esHoy(day)" class="dot-today"></span>
                  <span class="day-number">{{ day }}</span>
                  <span v-if="esHoy(day)" class="text-today">HOY</span>
                </button>
              </div>

              <div class="calendar-legend-sky">
                <div class="legend-item"><span class="dot selected"></span> Seleccionado</div>
                <div class="legend-item"><span class="dot available"></span> Disponible</div>
              </div>
            </div>
          </div>
        </transition>

        <transition name="slide-in">
          <div v-if="form.fecha" class="input-group">
            <label class="label-modern">Horarios Disponibles</label>
            
            <div v-if="cargandoHorarios" class="loading-spinner">Buscando disponibilidad...</div>
            
            <div v-else class="grid-horarios-compacto">
              <button 
                v-for="hora in horariosGenerados" 
                :key="hora"
                class="btn-hora-pill"
                :class="{ 
                  'hora-selected': form.hora === hora,
                  'hora-ocupada': esHorarioOcupado(hora)
                }"
                :disabled="esHorarioOcupado(hora)"
                @click="seleccionarHora(hora)"
              >
                {{ hora }}
              </button>
            </div>
            
            <div v-if="!cargandoHorarios && horariosGenerados.length === 0" class="texto-vacio">
              No hay horarios disponibles para esta fecha.
            </div>
          </div>
        </transition>

        <transition name="slide-in">
          <div v-if="form.hora" class="resumen-card">
            <div class="resumen-header">
              <span>Total a Pagar</span>
              <span class="precio-grande">${{ calcularTotal() }}</span>
            </div>
            
            <div class="pago-options">
              <label class="radio-box" :class="{ 'radio-active': form.tipo_pago === 'SENA_50' }">
                <input type="radio" v-model="form.tipo_pago" value="SENA_50" class="hidden-radio"> 
                <span>Seña 50%</span>
                <strong>${{ calcularSena() }}</strong>
              </label>
              <label class="radio-box" :class="{ 'radio-active': form.tipo_pago === 'TOTAL' }">
                <input type="radio" v-model="form.tipo_pago" value="TOTAL" class="hidden-radio"> 
                <span>Total</span>
                <strong>${{ calcularTotal() }}</strong>
              </label>
            </div>

            <div class="row-pago-extra">
               <select v-model="form.medio_pago" class="input-glass small">
                 <option value="EFECTIVO">💵 Efectivo</option>
                 <option value="TARJETA">💳 Tarjeta</option>
                 <option value="TRANSFERENCIA">📱 Transferencia</option>
               </select>
               
               <input 
                 v-if="form.medio_pago !== 'EFECTIVO'"
                 type="text" 
                 v-model="form.comprobante_id" 
                 class="input-glass small"
                 placeholder="Nro. Operación / Comprobante"
               >
            </div>

            <button 
              @click="crearTurno" 
              class="btn-confirmar-gradiente"
              :disabled="procesando"
            >
              {{ procesando ? 'Procesando...' : 'CONFIRMAR RESERVA ✨' }}
            </button>
          </div>
        </transition>

        <transition name="fade">
          <div v-if="mensaje" class="toast-message" :class="mensajeTipo">
            {{ mensaje }}
          </div>
        </transition>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // Estado del formulario
      form: {
        canal: 'PRESENCIAL',
        cliente: null,        // ID del cliente
        clienteNombre: "",    // Nombre para mostrar
        peluquero: "",
        servicios_ids: [],
        tipo_pago: "SENA_50",
        medio_pago: "EFECTIVO",
        comprobante_id: "",
        fecha: "",
        hora: ""
      },
      // Datos API
      categorias: [],
      servicios: [],
      peluqueros: [],
      
      // UI
      busquedaCliente: "",
      clientesSugeridos: [],
      categoriasSeleccionadas: [],
      horariosGenerados: [],
      horariosOcupadosDelDia: [],
      
      // Calendario Lógica
      currentDate: new Date(), 
      
      // Feedback
      errorCliente: "",
      mensaje: "",
      mensajeTipo: "success",
      procesando: false,
      cargandoHorarios: false,
      
      // Configuración
      horarioApertura: 9,
      horarioCierre: 20,
      intervaloMinutos: 20
    };
  },
  computed: {
    serviciosFiltrados() {
      if (this.categoriasSeleccionadas.length === 0) return [];
      const nombresCats = this.categorias
        .filter(c => this.categoriasSeleccionadas.includes(c.id))
        .map(c => c.nombre);
      return this.servicios.filter(s => nombresCats.includes(s.categoria));
    },
    // Computadas para el Calendario
    currentYear() { return this.currentDate.getFullYear(); },
    currentMonth() { return this.currentDate.getMonth(); },
    nombreMesActual() {
      const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
      return meses[this.currentMonth];
    },
    daysInMonth() {
      return new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
    },
    startingDayOfWeek() {
      return new Date(this.currentYear, this.currentMonth, 1).getDay();
    }
  },
  methods: {
    // --- Carga Inicial ---
    async mountedCalls() {
      const API_URL = "http://localhost:8000/usuarios/api";
      try {
        const [resCat, resServ, resPel] = await Promise.all([
          fetch(`${API_URL}/categorias/servicios/`),
          fetch(`${API_URL}/servicios/`),
          fetch(`${API_URL}/peluqueros/`)
        ]);
        this.categorias = await resCat.json();
        this.servicios = await resServ.json();
        this.peluqueros = await resPel.json();
      } catch (error) {
        console.error("Error cargando datos", error);
        this.mensaje = "Error de conexión con el servidor";
        this.mensajeTipo = "error";
      }
    },

    // --- Lógica de Cliente (CORREGIDA) ---
    async actualizarBusquedaCliente(e) {
      this.busquedaCliente = e.target.value;
      
      // Si el usuario borra lo que escribió, reseteamos el cliente seleccionado
      if (this.form.cliente && this.busquedaCliente !== this.form.clienteNombre) {
         this.limpiarCliente(); 
      }

      if (this.busquedaCliente.length < 2) {
        this.clientesSugeridos = [];
        return;
      }
      try {
        const res = await fetch(`http://localhost:8000/usuarios/api/clientes/?q=${this.busquedaCliente}`);
        const data = await res.json();
        this.clientesSugeridos = data.results || data || [];
        this.errorCliente = this.clientesSugeridos.length === 0 ? "No encontrado" : "";
      } catch (e) {
        this.errorCliente = "Error buscando cliente";
      }
    },
    
    seleccionarCliente(c) {
      // 1. Validamos que venga un ID
      if (!c.id) {
        this.errorCliente = "Error: El cliente seleccionado no tiene ID válido.";
        return;
      }

      // 2. Asignamos ID y Nombre
      this.form.cliente = c.id;
      const nombre = c.nombre || c.first_name || '';
      const apellido = c.apellido || c.last_name || '';
      this.form.clienteNombre = `${nombre} ${apellido}`.trim();
      
      // 3. Limpiamos sugerencias
      this.clientesSugeridos = [];
      this.busquedaCliente = ""; 
      this.errorCliente = "";
      
      console.log("Cliente seleccionado ID:", this.form.cliente); // Debug para consola
    },

    limpiarCliente() {
      this.form.cliente = null;
      this.form.clienteNombre = "";
      this.busquedaCliente = "";
      // Resetear pasos posteriores para evitar inconsistencias
      this.categoriasSeleccionadas = [];
      this.form.servicios_ids = [];
      this.form.peluquero = "";
      this.resetFechas();
    },

    irARegistrarCliente() {
      // CORRECCIÓN DEL ROUTER: Usamos la ruta definida en tu index.js
      this.$router.push('/usuarios/crear'); 
    },

    getInicial(c) {
       const n = c.nombre || c.first_name || 'C';
       return n.charAt(0).toUpperCase();
    },
    getNombreCompletoCliente(c) {
        return `${c.nombre || c.first_name || ''} ${c.apellido || c.last_name || ''}`;
    },

    // --- Servicios y Categorías ---
    toggleCategoria(id) {
      if (this.categoriasSeleccionadas.includes(id)) {
        this.categoriasSeleccionadas = this.categoriasSeleccionadas.filter(c => c !== id);
      } else {
        this.categoriasSeleccionadas.push(id);
      }
      // Al cambiar categorías, limpiamos selección posterior
      this.form.servicios_ids = []; 
      this.form.peluquero = "";
      this.resetFechas();
    },
    toggleServicio(servicio) {
      if (this.form.servicios_ids.includes(servicio.id)) {
        this.form.servicios_ids = this.form.servicios_ids.filter(id => id !== servicio.id);
      } else {
        this.form.servicios_ids.push(servicio.id);
      }
      // Al cambiar servicios, reiniciamos peluquero y fecha
      this.form.peluquero = "";
      this.resetFechas();
    },

    // --- Profesionales ---
    alCambiarPeluquero() {
      this.resetFechas();
    },
    resetFechas() {
      this.form.fecha = "";
      this.form.hora = "";
      this.horariosGenerados = [];
    },

    // --- Lógica del Calendario (Estilo React/Sky) ---
    cambiarMes(dir) {
      const newDate = new Date(this.currentDate);
      newDate.setMonth(this.currentDate.getMonth() + dir);
      this.currentDate = newDate;
    },
    esHoy(day) {
      const today = new Date();
      return day === today.getDate() && 
             this.currentMonth === today.getMonth() && 
             this.currentYear === today.getFullYear();
    },
    esDiaSeleccionado(day) {
      if (!this.form.fecha) return false;
      // Ojo con el timezone, usamos split para comparar strings YYYY-MM-DD
      const [y, m, d] = this.form.fecha.split('-').map(Number);
      return day === d && (this.currentMonth + 1) === m && this.currentYear === y;
    },
    esDiaSeleccionable(day) {
      const date = new Date(this.currentYear, this.currentMonth, day);
      const today = new Date();
      today.setHours(0,0,0,0);
      
      const diffTime = date - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      // Regla: Hoy + prox 7 dias
      const isInRange = diffDays >= 0 && diffDays <= 7;
      // Regla: No domingos (0)
      const isSunday = date.getDay() === 0;
      
      return isInRange && !isSunday;
    },
    seleccionarDiaCalendario(day) {
      if (!this.esDiaSeleccionable(day)) return;
      
      const mesStr = String(this.currentMonth + 1).padStart(2, '0');
      const diaStr = String(day).padStart(2, '0');
      this.form.fecha = `${this.currentYear}-${mesStr}-${diaStr}`;
      
      this.cargarHorariosParaFecha(this.form.fecha);
    },

    // --- Lógica de Horarios ---
    async cargarHorariosParaFecha(fecha) {
      this.form.hora = "";
      this.cargandoHorarios = true;
      try {
        const res = await fetch(`http://localhost:8000/usuarios/api/turnos/ocupados/?fecha=${fecha}&peluquero_id=${this.form.peluquero}`);
        const data = await res.json();
        this.horariosOcupadosDelDia = data.horarios_ocupados || []; 
      } catch (e) {
        console.error("Error API Horarios", e);
        this.horariosOcupadosDelDia = [];
      }
      this.generarGrillaHorarios(fecha);
      this.cargandoHorarios = false;
    },
    generarGrillaHorarios(fechaStr) {
      const horarios = [];
      const [year, month, day] = fechaStr.split('-').map(Number);
      const fechaSeleccionada = new Date(year, month - 1, day);
      const esHoy = new Date().toDateString() === fechaSeleccionada.toDateString();
      const ahora = new Date();

      for (let h = this.horarioApertura; h < this.horarioCierre; h++) {
        for (let m = 0; m < 60; m += this.intervaloMinutos) {
          const horaStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
          
          // Si es hoy, filtrar horarios pasados
          if (esHoy) {
            const fechaHoraLoop = new Date();
            fechaHoraLoop.setHours(h, m, 0, 0);
            if (fechaHoraLoop <= ahora) continue;
          }
          horarios.push(horaStr);
        }
      }
      this.horariosGenerados = horarios;
    },
    esHorarioOcupado(hora) {
      return this.horariosOcupadosDelDia.includes(hora);
    },
    seleccionarHora(hora) {
      this.form.hora = hora;
    },

    // --- Cálculos y Envío ---
    calcularTotal() {
      return this.form.servicios_ids.reduce((total, id) => {
        const s = this.servicios.find(x => x.id === id);
        return total + (s ? parseFloat(s.precio) : 0);
      }, 0);
    },
    calcularSena() {
      return this.calcularTotal() / 2;
    },
    
    async crearTurno() {
      // VALIDACIÓN FINAL MANUAL
      if (!this.form.cliente) {
        this.mensaje = "❌ Error: Falta seleccionar el cliente.";
        this.mensajeTipo = "error";
        return;
      }
      if (!this.form.hora) {
        this.mensaje = "❌ Error: Falta seleccionar un horario.";
        this.mensajeTipo = "error";
        return;
      }

      this.procesando = true;
      this.mensaje = "";

      // Calcular duración total
      const duracion = this.form.servicios_ids.reduce((acc, id) => {
         const s = this.servicios.find(x => x.id === id);
         return acc + (s ? parseInt(s.duracion) : 0);
      }, 0);

      const payload = {
        ...this.form, // Incluye cliente, peluquero, fecha, hora, tipo_pago
        monto_total: this.calcularTotal(),
        monto_seña: this.form.tipo_pago === 'SENA_50' ? this.calcularSena() : 0,
        duracion_total: duracion
      };

      try {
        const token = localStorage.getItem('token');
        const res = await fetch("http://localhost:8000/usuarios/api/turnos/crear/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": token ? `Token ${token}` : ''
          },
          body: JSON.stringify(payload)
        });
        
        const data = await res.json();

        if (res.ok && data.status === 'ok') {
          this.mensaje = "✅ ¡Turno registrado exitosamente!";
          this.mensajeTipo = "success";
          setTimeout(() => this.$router.push('/turnos'), 2000);
        } else {
          this.mensaje = `❌ ${data.message || "Error al crear turno"}`;
          this.mensajeTipo = "error";
        }
      } catch (e) {
        this.mensaje = "❌ Error de conexión con el servidor";
        this.mensajeTipo = "error";
        console.error(e);
      } finally {
        this.procesando = false;
      }
    }
  },
  mounted() {
    this.mountedCalls();
  }
};
</script>

<style scoped>
/* ESTILOS BASE */
.pedido-container {
  font-family: 'Inter', 'Segoe UI', sans-serif;
  color: #1e293b;
  background-color: #f1f5f9;
  min-height: 100vh;
  padding: 20px;
  display: flex;
  justify-content: center;
}

.card-clean {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
  padding: 30px;
  width: 100%;
  max-width: 800px;
}

/* HEADER */
.header-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
}
.header-icon-bg {
  width: 48px; height: 48px;
  background: #0ea5e9; /* Sky blue */
  color: white;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem;
}
.header-section h2 { margin: 0; font-weight: 800; font-size: 1.6rem; color: #0f172a; }
.subtitle { margin: 0; color: #64748b; font-size: 0.9rem; }

/* LABELS & INPUTS */
.label-modern {
  display: block; font-weight: 700; color: #334155; margin-bottom: 8px; font-size: 0.95rem;
}
.input-group { margin-bottom: 25px; position: relative; }

.row-search { display: flex; gap: 10px; }
.search-wrapper { position: relative; flex: 1; }
.icon-lupa { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); opacity: 0.5; }
.input-glass {
  width: 100%; padding: 12px 12px 12px 38px;
  border: 2px solid #e2e8f0; border-radius: 10px;
  font-size: 1rem; transition: all 0.2s; background: #f8fafc;
}
.input-glass:focus { border-color: #0ea5e9; background: white; outline: none; }
.input-glass.cliente-activo { 
  background-color: #f0f9ff; border-color: #0ea5e9; color: #0369a1; font-weight: 600; 
}
.input-glass.small { padding: 10px; font-size: 0.9rem; width: 100%; box-sizing: border-box; }

.btn-icon-clean {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: none; border: none; color: #ef4444; font-weight: bold; cursor: pointer;
}
.btn-nuevo-glass {
  background: #0f172a; color: white; border: none; padding: 0 20px;
  border-radius: 10px; font-weight: 600; cursor: pointer; transition: 0.2s;
}
.btn-nuevo-glass:hover { background: #334155; }

/* LISTA SUGERENCIAS */
.lista-sugerencias {
  position: absolute; top: 100%; left: 0; width: 100%;
  background: white; border: 1px solid #e2e8f0; border-radius: 10px;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
  z-index: 50; max-height: 250px; overflow-y: auto; margin-top: 5px; list-style: none; padding: 0;
}
.item-sugerencia {
  padding: 12px; display: flex; gap: 12px; align-items: center; cursor: pointer; border-bottom: 1px solid #f1f5f9;
}
.item-sugerencia:hover { background: #f8fafc; }
.avatar-mini {
  width: 35px; height: 35px; background: #e0f2fe; color: #0ea5e9;
  border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;
}
.info-sugerencia { display: flex; flex-direction: column; }
.info-sugerencia small { color: #64748b; }

/* CHIPS CATEGORIAS */
.grid-chips { display: flex; flex-wrap: wrap; gap: 10px; }
.chip-glass {
  background: white; border: 1px solid #cbd5e1; padding: 8px 16px;
  border-radius: 50px; color: #475569; cursor: pointer; transition: 0.2s; font-weight: 500;
}
.chip-glass:hover { border-color: #0ea5e9; color: #0ea5e9; }
.chip-active { background: #0ea5e9; color: white; border-color: #0ea5e9; box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2); }

/* GRID SERVICIOS (Horizontal) */
.grid-servicios {
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); 
  gap: 12px;
}
.card-servicio-mini {
  background: white; border: 2px solid #e2e8f0; border-radius: 12px;
  padding: 15px; cursor: pointer; transition: all 0.2s;
  display: flex; flex-direction: column; justify-content: space-between;
  min-height: 100px;
}
.card-servicio-mini:hover { border-color: #0ea5e9; transform: translateY(-2px); }
.servicio-active { border-color: #0ea5e9; background: #f0f9ff; }
.serv-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.serv-nombre { font-weight: 700; font-size: 0.95rem; color: #0f172a; line-height: 1.3; }
.checkbox-circle { 
  width: 20px; height: 20px; border: 2px solid #cbd5e1; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.servicio-active .checkbox-circle { background: #0ea5e9; border-color: #0ea5e9; color: white; font-size: 0.7rem; }
.serv-footer { display: flex; flex-direction: column; gap: 2px; }
.serv-precio { font-weight: 800; color: #059669; font-size: 1rem; }
.serv-duracion { font-size: 0.75rem; color: #64748b; }

/* CALENDARIO ESTILO SKY REACT */
.calendar-wrapper-sky {
  background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20px; border: 1px solid #e2e8f0; padding: 25px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.calendar-header-sky {
  display: flex; justify-content: space-between; align-items: center;
  background: white; padding: 15px; border-radius: 12px; margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.mes-titulo-sky { margin: 0; font-weight: 800; color: #0f172a; font-size: 1.1rem; text-transform: capitalize; }
.btn-nav-sky {
  background: transparent; border: none; font-size: 1.5rem; color: #64748b;
  cursor: pointer; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  transition: 0.2s;
}
.btn-nav-sky:hover { background: #f1f5f9; color: #0ea5e9; transform: scale(1.1); }

.weekdays-grid-sky {
  display: grid; grid-template-columns: repeat(7, 1fr); margin-bottom: 10px;
}
.weekday-sky { text-align: center; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }

.days-grid-sky {
  display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px;
}
.day-btn-sky {
  aspect-ratio: 1;
  background: white; border: 1px solid #e2e8f0; border-radius: 12px;
  color: #334155; display: flex; flex-direction: column; align-items: center; justify-content: center;
  cursor: pointer; position: relative; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.day-btn-sky:hover:not(:disabled) { border-color: #0ea5e9; transform: translateY(-2px); }
.day-number { font-size: 1rem; font-weight: 600; }

/* Estados del día */
.is-selected { 
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); 
  color: white; border: none; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.4); 
}
.is-today { border-color: #0ea5e9; color: #0284c7; }
.is-selected .text-today { color: #e0f2fe; }
.is-selected .dot-today { background: white; }
.is-disabled { background: #f1f5f9; color: #cbd5e1; cursor: not-allowed; border-color: transparent; box-shadow: none; }

.dot-today { width: 6px; height: 6px; background: #0ea5e9; border-radius: 50%; position: absolute; top: 6px; right: 6px; }
.text-today { font-size: 0.6rem; font-weight: 800; margin-top: 2px; }

.calendar-legend-sky {
  margin-top: 20px; display: flex; justify-content: center; gap: 20px; font-size: 0.8rem; color: #64748b;
}
.legend-item { display: flex; align-items: center; gap: 6px; }
.dot { width: 10px; height: 10px; border-radius: 4px; }
.dot.selected { background: #0ea5e9; }
.dot.available { border: 1px solid #cbd5e1; background: white; }

/* GRILLA HORARIOS */
.grid-horarios-compacto { display: flex; flex-wrap: wrap; gap: 8px; }
.btn-hora-pill {
  padding: 8px 16px; border: 1px solid #cbd5e1; background: white; border-radius: 8px;
  font-weight: 600; color: #334155; cursor: pointer; transition: 0.2s; min-width: 70px;
}
.btn-hora-pill:hover:not(:disabled) { border-color: #0ea5e9; color: #0ea5e9; }
.hora-selected { background: #0ea5e9; color: white; border-color: #0ea5e9; }
.hora-ocupada { background: #fee2e2; color: #ef4444; text-decoration: line-through; cursor: not-allowed; border-color: #fca5a5; }

/* RESUMEN */
.resumen-card { margin-top: 30px; background: white; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 25px; }
.resumen-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.precio-grande { font-size: 2rem; font-weight: 800; color: #0f172a; }

.pago-options { display: flex; gap: 15px; margin-bottom: 20px; }
.radio-box {
  flex: 1; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px;
  cursor: pointer; text-align: center; transition: 0.2s;
}
.radio-box:hover { border-color: #94a3b8; }
.radio-active { border-color: #0ea5e9; background: #f0f9ff; color: #0369a1; }
.hidden-radio { display: none; }
.radio-box strong { display: block; font-size: 1.2rem; margin-top: 5px; }

.row-pago-extra { display: flex; gap: 10px; margin-bottom: 25px; }

.btn-confirmar-gradiente {
  width: 100%; padding: 18px; border: none; border-radius: 12px;
  background: linear-gradient(135deg, #0ea5e9, #2563eb);
  color: white; font-weight: 800; font-size: 1.1rem; cursor: pointer;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); text-transform: uppercase; letter-spacing: 1px;
}
.btn-confirmar-gradiente:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5); }
.btn-confirmar-gradiente:disabled { background: #cbd5e1; cursor: not-allowed; box-shadow: none; transform: none; }

/* MENSAJES */
.msg-error { color: #ef4444; font-size: 0.85rem; margin-top: 5px; font-weight: 600; }
.texto-vacio { font-style: italic; color: #94a3b8; margin-top: 10px; }
.toast-message { margin-top: 20px; padding: 15px; border-radius: 8px; text-align: center; font-weight: 700; }
.toast-message.success { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.toast-message.error { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

/* ANIMACIONES */
.slide-in-enter-active { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.fade-enter-active { transition: opacity 0.5s; }
.fade-enter-from { opacity: 0; }
</style>