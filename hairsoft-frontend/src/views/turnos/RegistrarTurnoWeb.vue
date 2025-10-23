<template>
  <div class="form-container">
    <div class="form-card turnos-card">
      <h1 class="form-title">Reservar Turno Online</h1>
      <p class="form-subtitle">Reserva tu turno desde casa, con pago de seña o total.</p>

      <div class="cliente-info">
        <div class="info-card">
          <h3>Tus Datos</h3>
          <p><strong>Cliente:</strong> {{ usuario.nombre }} {{ usuario.apellido }}</p> 
          <p><strong>DNI:</strong> {{ usuario.dni || 'Cargando...' }}</p>
          <p><strong>Teléfono:</strong> {{ usuario.telefono || 'No registrado' }}</p>
          <small class="info-pago">Tu información se enviará automáticamente al sistema.</small>
        </div>
      </div>

      <div class="input-group">
        <label for="peluquero">Elegir Peluquero</label>
        <select v-model="form.peluquero" id="peluquero" required @change="limpiarSelecciones">
          <option :value="null">Selecciona tu peluquero preferido</option>
          <option v-for="p in peluqueros" :key="p.id" :value="p.id">
            {{ p.nombre }} {{ p.apellido }}
          </option>
        </select>
      </div>
      
      <div v-if="form.peluquero" class="input-group">
        <label for="servicios">Servicios que necesitas</label>
        <div class="servicios-grid">
          <div 
            v-for="servicio in servicios" 
            :key="servicio.id"
            class="servicio-checkbox"
            :class="{ selected: form.servicios_ids.includes(servicio.id) }"
            @click="toggleServicio(servicio)"
          >
            <div class="servicio-info">
              <span class="servicio-nombre">{{ servicio.nombre }}</span>
              <span class="servicio-precio">${{ servicio.precio }}</span>
              <span class="servicio-duracion">{{ servicio.duracion }}min</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="form.servicios_ids.length > 0" class="resumen-servicios">
        <h3>Resumen de Costos</h3>
        <div class="total-section">
          <div class="monto-total">
            <strong>Total del servicio: ${{ calcularTotal() }}</strong>
          </div>
        </div>

        <div class="opciones-pago">
            <h4>Seleccione Opción de Pago con Mercado Pago:</h4>
            <label class="radio-option">
                <input type="radio" v-model="form.tipo_pago" value="SENA_50" required> 
                Pagar **Seña (50%)**: <strong class="monto-sena">${{ calcularSena() }}</strong>
                <small> (El resto ${{ (calcularTotal() * 0.5).toFixed(2) }} lo pagas en el local)</small>
            </label>
            <label class="radio-option">
                <input type="radio" v-model="form.tipo_pago" value="TOTAL" required> 
                Pagar **Total (100%)**: <strong class="monto-total-pago">${{ calcularTotal() }}</strong>
            </label>
        </div>
      </div>

      <div v-if="form.peluquero && form.servicios_ids.length > 0" class="input-group">
        <label>Selecciona el día</label>
        <div class="calendario">
           <div class="calendario-header">
             <button @click="mesAnterior" class="btn-calendario">&lt;</button>
             <span class="mes-actual">{{ mesActualTexto }}</span>
             <button @click="mesSiguiente" class="btn-calendario">&gt;</button>
           </div>
           <div class="dias-semana">
             <div v-for="dia in ['Lun','Mar','Mie','Jue','Vie','Sab']" :key="dia" class="dia-header">{{ dia }}</div>
           </div>
           <div class="dias-mes">
             <div 
               v-for="dia in diasDelMes" 
               :key="dia.fecha"
               class="dia-calendario"
               :class="{
                 'disabled': !dia.disponible || dia.pasado,
                 'selected': fechaSeleccionada === dia.fecha,
                 'hoy': dia.hoy
               }"
               @click="seleccionarDia(dia)"
             >
               <span class="numero-dia">{{ dia.numero }}</span>
               <span v-if="!dia.disponible && !dia.pasado" class="indicador-ocupado">●</span>
             </div>
           </div>
         </div>
      </div>

      <div v-if="fechaSeleccionada" class="input-group">
        <label>Elegi el horario</label>
        <div class="horarios-grid">
          <button
            v-for="horario in horariosDisponibles"
            :key="horario.hora"
            type="button"
            class="horario-btn"
            :class="{ 
              selected: form.hora === horario.hora,
              disabled: !horario.disponible
            }"
            @click="form.hora = horario.hora"
            :disabled="!horario.disponible"
          >
            <span class="hora">{{ horario.hora }}</span>
            <span v-if="!horario.disponible" class="estado">Ocupado</span>
            <span v-else class="estado disponible">Disponible</span>
          </button>
        </div>
      </div>

      <div v-if="formularioValido" class="input-group full-width">
        <div class="resumen-final">
          <h3>Confirmar y Pagar</h3>
          <p><strong>Fecha:</strong> {{ formatoFechaLegible(fechaSeleccionada) }} a las {{ form.hora }}</p>
          <p><strong>Peluquero:</strong> {{ getPeluqueroNombre() }}</p>
          <p><strong>Total a pagar ahora:</strong> <strong class="monto-final-pago">${{ montoAPagarAhora() }}</strong></p>
        </div>
        <button
          @click="reservarTurno" 
          type="button" 
          class="btn-pagar"
          :disabled="cargando"
        >
          {{ cargando ? 'Procesando Pago...' : `Pagar $${montoAPagarAhora()} con Mercado Pago` }}
        </button>
        <p class="info-pago">
          Tu turno quedará <strong>confirmado</strong> tras el pago.
        </p>
      </div>

      <p v-if="mensaje" class="mensaje" :class="{ error: mensaje.includes('Error') }">
        {{ mensaje }}
      </p>

      <div v-if="cargando" class="loading">
        <p>Iniciando proceso de pago. No cierres esta ventana...</p>
      </div>
      
    </div>
  </div>
</template>

<script>
import axios from 'axios'; 

export default {
  data() {
    return {
      // 🚨 Restauramos la convención a 'peluquero'
      form: {
        peluquero: null, 
        servicios_ids: [],
        hora: "",
        fecha: "",
        tipo_pago: null,
      },
      // Simulación de usuario logueado (debe ser cargado por cargarUsuarioLogueado)
      usuario: { id: null, nombre: 'Cargando', apellido: '...', dni: 'Cargando', telefono: '' }, 
      
      peluqueros: [],
      servicios: [],
      fechaSeleccionada: null,
      mesActual: new Date(),
      horariosDisponibles: [],
      turnosOcupados: [],
      mensaje: "",
      cargando: false
    };
  },
  computed: {
    formularioValido() {
      // 🚨 Usamos 'form.peluquero'
      return this.form.peluquero && 
             this.form.servicios_ids.length > 0 &&
             this.fechaSeleccionada && 
             this.form.hora &&
             this.form.tipo_pago;
    },
    diasDelMes() {
        // Lógica del calendario se mantiene
        const year = this.mesActual.getFullYear();
        const month = this.mesActual.getMonth();
        const primerDia = new Date(year, month, 1);
        const ultimoDia = new Date(year, month + 1, 0);
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);
        
        const dias = [];
        
        const primerDiaSemana = primerDia.getDay() === 0 ? 6 : primerDia.getDay() - 1;
        for (let i = primerDiaSemana; i > 0; i--) {
            const fecha = new Date(year, month, -i + 1);
            dias.push({
                numero: fecha.getDate(),
                fecha: this.formatoFecha(fecha),
                disponible: false,
                pasado: true
            });
        }
        
        for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
            const fecha = new Date(year, month, dia);
            const fechaStr = this.formatoFecha(fecha);
            const disponible = this.estaDiaDisponible(fecha);
            const pasado = fecha < hoy;
            const hoyDia = this.esMismoDia(fecha, hoy);
            
            dias.push({
                numero: dia,
                fecha: fechaStr,
                disponible,
                pasado,
                hoy: hoyDia
            });
        }
        
        return dias;
    },
    mesActualTexto() {
      return this.mesActual.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
    }
  },
  methods: {
    async cargarDatosIniciales() {
      await Promise.all([
        this.cargarUsuarioLogueado(),
        this.cargarPeluqueros(),
        this.cargarServicios(),
        this.cargarTurnosOcupados()
      ]);
    },

    async cargarUsuarioLogueado() {
       try {
         // Intenta obtener los datos del usuario logueado. Si Django usa sesiones, esta URL debe funcionar
         const res = await axios.get("http://localhost:8000/usuarios/api/me/"); 
         this.usuario = res.data; 
       } catch (err) {
         console.error("Error al cargar usuario logueado. Asegúrate de estar autenticado.", err);
       }
    },
    
    async cargarPeluqueros() {
      try {
        const res = await axios.get("http://localhost:8000/usuarios/api/peluqueros/");
        // El problema aquí no es el método, sino la inconsistencia de variables. 
        this.peluqueros = res.data;
      } catch (err) {
        console.error("❌ Error al cargar peluqueros (Verifica la URL en Django):", err.response ? err.response.data : err.message);
        this.mensaje = "Error al cargar la lista de peluqueros. Revisa la consola.";
        this.peluqueros = [];
      }
    },

    async cargarServicios() {
      try {
        const res = await axios.get("http://localhost:8000/usuarios/api/servicios/");
        this.servicios = res.data;
      } catch (err) {
        console.error("Error al cargar servicios:", err);
      }
    },

    async cargarTurnosOcupados() {
      try {
        const res = await axios.get("http://localhost:8000/usuarios/api/turnos/?estado__in=RESERVADO,CONFIRMADO");
        this.turnosOcupados = res.data.results || res.data;
      } catch (err) {
        console.error("Error al cargar turnos:", err);
      }
    },
    
    montoAPagarAhora() {
        const total = parseFloat(this.calcularTotal());
        if (this.form.tipo_pago === 'TOTAL') {
            return total.toFixed(2);
        }
        if (this.form.tipo_pago === 'SENA_50') {
            return (total * 0.5).toFixed(2);
        }
        return '0.00';
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
        }, 0).toFixed(2);
    },

    calcularSena() {
        return (this.calcularTotal() * 0.5).toFixed(2);
    },
    
    mesAnterior() {
      this.mesActual = new Date(this.mesActual.getFullYear(), this.mesActual.getMonth() - 1, 1);
      this.limpiarFechaHora();
    },

    mesSiguiente() {
      this.mesActual = new Date(this.mesActual.getFullYear(), this.mesActual.getMonth() + 1, 1);
      this.limpiarFechaHora();
    },

    seleccionarDia(dia) {
      if (!dia.disponible || dia.pasado) return;
      this.fechaSeleccionada = dia.fecha;
      this.form.hora = "";
      this.generarHorariosDisponibles();
    },

    formatoFecha(fecha) {
      const anio = fecha.getFullYear();
      const mes = String(fecha.getMonth() + 1).padStart(2, '0');
      const dia = String(fecha.getDate()).padStart(2, '0');
      return `${anio}-${mes}-${dia}`;
    },

    formatoFechaLegible(fechaStr) {
      const fecha = new Date(fechaStr + 'T00:00:00');
      return fecha.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
    },

    esMismoDia(fecha1, fecha2) {
      return fecha1.toDateString() === fecha2.toDateString();
    },

    estaDiaDisponible(fecha) {
      if (fecha.getDay() === 0 || fecha.getDay() === 6) return false; 
      
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      const fechaComparar = new Date(fecha);
      fechaComparar.setHours(0, 0, 0, 0);
      
      return fechaComparar >= hoy;
    },

    generarHorariosDisponibles() {
      const horariosBase = [];
      const bloques = [
        { inicio: 8, fin: 12 },
        { inicio: 15, fin: 20 }
      ];

      bloques.forEach(bloque => {
        for (let h = bloque.inicio; h < bloque.fin; h++) {
          for (let m = 0; m < 60; m += 30) {
            const hora = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
            const disponible = this.estaHorarioDisponible(hora);
            horariosBase.push({ hora, disponible });
          }
        }
      });

      this.horariosDisponibles = horariosBase;
    },

    estaHorarioDisponible(horario) {
      // 🚨 Usamos 'form.peluquero'
      if (!this.fechaSeleccionada || !this.form.peluquero) return false;

      const turnoOcupado = this.turnosOcupados.find(t => 
        t.fecha === this.fechaSeleccionada && 
        t.hora === horario && 
        t.peluquero == this.form.peluquero
      );
      
      return !turnoOcupado;
    },

    getPeluqueroNombre() {
      // 🚨 Usamos 'form.peluquero'
      const peluquero = this.peluqueros.find(p => p.id == this.form.peluquero); 
      return peluquero ? `${peluquero.nombre} ${peluquero.apellido}` : '';
    },

    limpiarSelecciones() {
      this.fechaSeleccionada = null;
      this.form.hora = "";
      this.form.servicios_ids = [];
      this.form.tipo_pago = null;
    },

    limpiarFechaHora() {
      this.fechaSeleccionada = null;
      this.form.hora = "";
    },

    async reservarTurno() {
      if (!this.formularioValido) {
        this.mensaje = "Error: Completa todos los campos y selecciona una opción de pago.";
        return;
      }

      this.cargando = true;
      this.mensaje = "Reservando turno y generando link de pago con Mercado Pago...";

      const payload = {
        // 🚨 CRUCIAL: Renombramos 'peluquero' a 'peluquero_id' en el payload para el backend.
        peluquero_id: this.form.peluquero, 
        servicios_ids: this.form.servicios_ids,
        fecha: this.fechaSeleccionada,
        hora: this.form.hora,
        canal: 'WEB',
        tipo_pago: this.form.tipo_pago, // SENA_50 o TOTAL
      };

      try {
        const res = await axios.post("http://localhost:8000/usuarios/api/turnos/crear/", payload);

        const data = res.data;
        this.cargando = false;
        this.mensaje = "";

        if (data.status === 'ok' && data.procesar_pago && data.mp_data && data.mp_data.init_point) {
            this.mensaje = "Turno pre-reservado. Redirigiendo a Mercado Pago para abonar...";
            this.iniciarPagoMercadoPago(data.mp_data.init_point);
        } else {
            this.mensaje = `Error: ${data.message || "Error al reservar el turno."}`;
        }
      } catch (err) {
        console.error("Error de red/servidor:", err);
        this.cargando = false;
        
        const errorMsg = err.response?.data?.message || err.message || "Error de conexión con el servidor.";
        this.mensaje = `Error de reserva: ${errorMsg}`;
      }
    },

    iniciarPagoMercadoPago(initPointUrl) {
      window.location.href = initPointUrl; 
    }
  },

  mounted() {
    this.cargarDatosIniciales();
  }
};
</script>

<style scoped>
/* Estilos necesarios para las opciones de pago y presentación */
.opciones-pago {
    border: 1px solid #ccc;
    padding: 15px;
    border-radius: 6px;
    margin-bottom: 20px;
}
.opciones-pago h4 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #34495e;
}
.radio-option {
    display: block;
    padding: 10px;
    margin-bottom: 8px;
    border: 1px solid #eee;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}
.radio-option:hover {
    background-color: #f7f7f7;
}
.radio-option input[type="radio"] {
    margin-right: 10px;
}
.monto-sena {
    color: #e67e22; 
    font-weight: bold;
}
.monto-total-pago {
    color: #27ae60; 
    font-weight: bold;
}
.cliente-info {
    margin-bottom: 20px;
    padding: 15px;
    background-color: #f0f8ff;
    border-left: 5px solid #007bff;
    border-radius: 4px;
}
.cliente-info h3 {
    margin-top: 0;
    color: #007bff;
}
.btn-pagar {
    background-color: #009ee3; 
    color: white;
    padding: 12px 20px;
    border: none;
    border-radius: 4px;
    font-size: 1.1em;
    cursor: pointer;
    transition: background-color 0.3s;
}
.btn-pagar:hover:not(:disabled) {
    background-color: #007bb5;
}
.btn-pagar:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

/* Estilos de la grilla de servicios y calendario (mantener tu estilo si es más complejo) */
.servicios-grid, .horarios-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
}
.servicio-checkbox {
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}
.servicio-checkbox.selected {
    border-color: #007bff;
    background-color: #e6f0ff;
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}
.servicio-precio {
    font-weight: bold;
    color: green;
}
.calendario {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
}
.dias-semana, .dias-mes {
    display: grid;
    grid-template-columns: repeat(6, 1fr); 
    gap: 5px;
}
.dia-header {
    font-weight: bold;
    text-align: center;
    padding: 5px 0;
}
.dia-calendario {
    text-align: center;
    padding: 10px 5px;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.2s;
}
.dia-calendario.disabled, .dia-calendario.pasado {
    cursor: not-allowed;
    color: #ccc;
    background-color: #fafafa;
}
.dia-calendario.selected {
    background-color: #007bff;
    color: white;
    font-weight: bold;
}
</style>