<template>
  <div class="form-container">
    <div class="form-card turnos-card">
      <h1 class="form-title">🏪 Registrar Turno Presencial</h1>
      <p class="form-subtitle">Para clientes que reservan en el local</p>

      <!-- CLIENTE -->
      <div class="input-group">
        <label for="cliente">Buscar Cliente</label>
        <input
          type="text"
          id="cliente"
          v-model="form.clienteNombre"
          @input="buscarCliente"
          placeholder="Nombre, apellido o DNI del cliente"
          autocomplete="off"
        />
        <ul v-if="clientesSugeridos.length" class="sugerencias-list">
          <li 
            v-for="c in clientesSugeridos" 
            :key="c.id" 
            @click="seleccionarCliente(c)"
            class="sugerencia-item"
          >
            {{ c.nombre }} {{ c.apellido }} — DNI: {{ c.dni }}
          </li>
        </ul>
      </div>

      <!-- PELUQUERO -->
      <div class="input-group">
        <label for="peluquero">Peluquero</label>
        <select v-model="form.peluquero" id="peluquero" required @change="limpiarFechaHora">
          <option value="">Seleccione un peluquero</option>
          <option v-for="p in peluqueros" :key="p.id" :value="p.id">
            {{ p.nombre }} {{ p.apellido }}
          </option>
        </select>
      </div>

      <!-- SERVICIOS (MÚLTIPLES) -->
      <div class="input-group">
        <label for="servicios">Servicios</label>
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

      <!-- RESUMEN DE SERVICIOS -->
      <div v-if="form.servicios_ids.length > 0" class="resumen-servicios">
        <h3>📊 Resumen de Servicios</h3>
        <div class="servicios-seleccionados">
          <div 
            v-for="servicioId in form.servicios_ids" 
            :key="servicioId"
            class="servicio-seleccionado"
          >
            {{ getServicioNombre(servicioId) }} - ${{ getServicioPrecio(servicioId) }}
          </div>
        </div>
        <div class="total-section">
          <strong>Total: ${{ calcularTotal() }}</strong>
        </div>
      </div>

      <!-- SELECTOR DE FECHA (solo si hay servicios y peluquero) -->
      <div v-if="form.servicios_ids.length > 0 && form.peluquero" class="input-group">
        <label>📅 Seleccionar Fecha</label>
        <div class="time-grid">
          <button
            v-for="(fecha, index) in proximosDias"
            :key="index"
            type="button"
            class="time-slot"
            :class="{ 
              selected: fechaSeleccionada && fechaSeleccionada.toDateString() === fecha.toDateString(),
              disabled: !estaDisponible(fecha)
            }"
            @click="seleccionarFecha(fecha)"
            :disabled="!estaDisponible(fecha)"
          >
            <span class="hora-principal">{{ diasSemana[fecha.getDay()] }}</span>
            <span class="hora-badge">{{ fecha.getDate() }}/{{ fecha.getMonth() + 1 }}</span>
            <span v-if="!estaDisponible(fecha)" class="no-disponible">No disponible</span>
          </button>
        </div>
      </div>

      <!-- SELECTOR DE HORARIO (solo si hay fecha seleccionada) -->
      <div v-if="fechaSeleccionada" class="input-group">
        <label>🕒 Seleccionar Horario</label>
        <div class="time-grid">
          <button
            v-for="h in horariosDisponibles"
            :key="h"
            type="button"
            class="time-slot"
            :class="{ 
              selected: form.hora === h,
              disabled: !estaHorarioDisponible(h)
            }"
            @click="form.hora = h"
            :disabled="!estaHorarioDisponible(h)"
          >
            {{ h }}
            <span v-if="!estaHorarioDisponible(h)" class="no-disponible">Ocupado</span>
          </button>
        </div>
      </div>

      <!-- TIPO DE PAGO Y MEDIO DE PAGO (solo si hay hora seleccionada) -->
      <div v-if="form.hora" class="input-group">
        <label>💰 Forma de Pago</label>
        
        <!-- Primero: Tipo de Pago -->
        <div class="pago-options">
          <label class="pago-option">
            <input 
              type="radio" 
              v-model="form.tipo_pago" 
              value="SENA_50" 
            />
            <span class="pago-label">
              Seña 50% - ${{ calcularSena() }}
              <small>El cliente paga la seña ahora</small>
            </span>
          </label>
          <label class="pago-option">
            <input 
              type="radio" 
              v-model="form.tipo_pago" 
              value="TOTAL" 
            />
            <span class="pago-label">
              Pago Total - ${{ calcularTotal() }}
              <small>El cliente paga todo ahora</small>
            </span>
          </label>
        </div>

        <!-- Luego: Medio de Pago -->
        <div v-if="form.tipo_pago" class="medio-pago-section">
          <label class="section-label">💳 Medio de Pago</label>
          <div class="medio-pago-options">
            <label class="medio-pago-option">
              <input 
                type="radio" 
                v-model="form.medio_pago" 
                value="EFECTIVO" 
              />
              <span class="medio-pago-label">
                💵 Efectivo
                <small>Pago en el local</small>
              </span>
            </label>
            <label class="medio-pago-option">
              <input 
                type="radio" 
                v-model="form.medio_pago" 
                value="MERCADO_PAGO" 
              />
              <span class="medio-pago-label">
                📱 Mercado Pago
                <small>Pago online</small>
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- BOTÓN -->
      <div class="input-group full-width">
        <button 
          @click="crearTurno" 
          type="button" 
          class="btn-registrar"
          :disabled="!formularioValido"
        >
          {{ textoBoton }}
        </button>
      </div>

      <p v-if="mensaje" class="mensaje" :class="{ error: mensaje.includes('❌') }">
        {{ mensaje }}
      </p>
    </div>

    <!-- INSTRUCCIONES PARA PAGO CON QR FIJO -->
    <div v-if="mostrarInstruccionesMP" class="instrucciones-qr">
      <h3>📱 Pago con Mercado Pago</h3>
      
      <div class="pasos-pago">
        <div class="paso">
          <span class="numero">1</span>
          <span>Cliente escanea el <strong>QR fijo del mostrador</strong></span>
        </div>
        <div class="paso">
          <span class="numero">2</span>
          <span>Ingresa monto: <strong>${{ montoAPagar }}</strong></span>
        </div>
        <div class="paso">
          <span class="numero">3</span>
          <span>Completa el pago en la app de MP</span>
        </div>
        <div class="paso">
          <span class="numero">4</span>
          <span>Muestra el comprobante al usuario (Adm. o Recep.)</span>
        </div>
      </div>

      <div class="info-pago">
        <p><strong>Cliente:</strong> {{ turnoActual.cliente_nombre }}</p>
        <p><strong>Concepto:</strong> {{ turnoActual.tipo_pago === 'SENA_50' ? 'Seña 50%' : 'Pago completo' }}</p>
        <p><strong>Monto a pagar:</strong> ${{ montoAPagar }}</p>
      </div>

      <div class="acciones">
        <button @click="marcarComoPagado" class="btn-confirmar">
          ✅ Marcar como Pagado
        </button>
        <button @click="cerrarInstrucciones" class="btn-cerrar">
          Cerrar
        </button>
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
      
      // ✅ NUEVAS VARIABLES PARA INSTRUCCIONES
      mostrarInstruccionesMP: false,
      turnoActual: null,
      montoAPagar: 0
    };
  },
  computed: {
    formularioValido() {
      return this.form.cliente && 
             this.form.peluquero && 
             this.form.servicios_ids.length > 0 &&
             this.fechaSeleccionada && 
             this.form.hora &&
             this.form.tipo_pago &&
             this.form.medio_pago;
    },
    textoBoton() {
      const monto = this.form.tipo_pago === 'SENA_50' ? this.calcularSena() : this.calcularTotal();
      const medio = this.form.medio_pago === 'EFECTIVO' ? 'Efectivo' : 'Mercado Pago';
      
      if (this.form.tipo_pago === 'SENA_50') {
        return `💰 Seña 50% - $${monto} (${medio})`;
      } else {
        return `💵 Pago Total - $${monto} (${medio})`;
      }
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
      
      while (contador < 14) {
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
    
    generarHorarios() {
      const horarios = [];
      const bloques = [
        { inicio: 8, fin: 12 },
        { inicio: 15, fin: 20 }
      ];
      
      bloques.forEach(bloque => {
        for (let h = bloque.inicio; h < bloque.fin; h++) {
          for (let m = 0; m < 60; m += 30) {
            const hora = `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
            horarios.push(hora);
          }
        }
      });
      this.horariosDisponibles = horarios;
    },
    
    seleccionarFecha(fecha) {
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
      if (!this.fechaSeleccionada || !this.form.peluquero) return false;
      
      const fechaStr = this.formatoFecha(this.fechaSeleccionada);
      const turnoOcupado = this.turnosOcupados.find(t => 
        t.fecha === fechaStr && 
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

    // ✅ MOSTRAR INSTRUCCIONES PARA PAGO CON QR FIJO
    mostrarInstruccionesPago(turnoData) {
      this.turnoActual = turnoData;
      this.montoAPagar = turnoData.monto_seña || turnoData.monto_total;
      this.mostrarInstruccionesMP = true;
      this.mensaje = "✅ Turno creado. Cliente debe escanear QR fijo del mostrador.";
    },

    // ✅ CERRAR INSTRUCCIONES
    cerrarInstrucciones() {
      this.mostrarInstruccionesMP = false;
      this.turnoActual = null;
      this.mensaje = "✅ Turno registrado. El cliente puede pagar cuando quiera.";
    },

    // ✅ MARCAR COMO PAGADO (cuando cliente muestra comprobante)
    async marcarComoPagado() {
      try {
        this.mensaje = "🔄 Marcando como pagado...";
        
        // Aquí podrías llamar a un endpoint para actualizar el estado del turno
        // Por ahora solo cerramos las instrucciones
        this.mostrarInstruccionesMP = false;
        this.mensaje = "✅ Pago confirmado. Turno activado.";
        this.limpiarFormulario();
        
      } catch (err) {
        console.error("Error marcando como pagado:", err);
        this.mensaje = "❌ Error al confirmar pago.";
      }
    },
    
    // ✅ CREAR TURNO
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

      console.log("📤 Enviando datos al backend:", payload);

      try {
        this.mensaje = "🔄 Creando turno...";
        
        const res = await fetch("http://localhost:8000/usuarios/api/turnos/crear/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        
        const data = await res.json();
        console.log("📥 Respuesta del backend:", data);
        
        if (res.ok && data.status === 'ok') {
          if (this.form.medio_pago === 'MERCADO_PAGO') {
            // ✅ SI USA MP, MOSTRAR INSTRUCCIONES PARA QR FIJO
            console.log("🎯 Mostrando instrucciones para QR fijo");
            this.mostrarInstruccionesPago(data);
          } else {
            // ✅ SI ES EFECTIVO, CONFIRMAR DIRECTAMENTE
            this.mensaje = "✅ Turno registrado correctamente.";
            this.limpiarFormulario();
          }
        } else {
          this.mensaje = data.message || "❌ Error al registrar el turno.";
          console.error("Error del backend:", data);
        }
      } catch (err) {
        console.error("💥 Error de conexión:", err);
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
      
      setTimeout(() => {
        if (this.mensaje.includes('✅')) {
          this.mensaje = "";
        }
      }, 5000);
    }
  },
  
  mounted() {
    this.cargarServicios();
    this.cargarPeluqueros();
    this.cargarTurnosOcupados();
    this.generarProximosDias();
    this.generarHorarios();
  }
};
</script>

<style scoped>
/* ESTILOS PARA INSTRUCCIONES QR FIJO */
.instrucciones-qr {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 2rem;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  border: 2px solid #667eea;
}

.instrucciones-qr h3 {
  margin: 0 0 1.5rem 0;
  color: #333;
  text-align: center;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 1rem;
}

.pasos-pago {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.paso {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.numero {
  background: #007bff;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
  flex-shrink: 0;
}

.info-pago {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f8f9fa;
}

.info-pago p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.acciones {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-confirmar {
  padding: 0.75rem 1.5rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.btn-confirmar:hover {
  background: #1e7e34;
  transform: translateY(-1px);
}

.btn-cerrar {
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cerrar:hover {
  background: #545b62;
  transform: translateY(-1px);
}

/* ESTILOS EXISTENTES DEL FORMULARIO */
.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
}

.time-slot {
  padding: 12px 10px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 6px;
  user-select: none;
}

.time-slot:hover:not(.disabled) { 
  border-color: #667eea; 
  transform: translateY(-2px); 
  box-shadow: 0 4px 12px rgba(102,126,234,0.2); 
}

.time-slot.selected { 
  background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); 
  color: white; 
  border-color: #667eea; 
  box-shadow: 0 6px 16px rgba(102,126,234,0.4); 
}

.time-slot.disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
  opacity: 0.6;
}

.hora-principal { font-weight:700; font-size:16px; }
.hora-badge { font-size:10px; font-weight:600; padding:3px 8px; border-radius:10px; background:#e8f5e9; color:#2e7d32; }

.servicios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.servicio-checkbox {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.servicio-checkbox:hover {
  border-color: #667eea;
  transform: translateY(-1px);
}

.servicio-checkbox.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.servicio-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.servicio-nombre {
  font-weight: 600;
  color: #333;
}

.servicio-precio {
  color: #667eea;
  font-weight: 600;
}

.servicio-duracion {
  font-size: 0.8em;
  color: #666;
}

.resumen-servicios {
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.servicios-seleccionados {
  margin-bottom: 10px;
}

.servicio-seleccionado {
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
  color: #333;
}

.total-section {
  border-top: 2px solid #667eea;
  padding-top: 10px;
  font-size: 1.1em;
}

.pago-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pago-option {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  background: white;
  transition: all 0.3s ease;
}

.pago-option:hover {
  border-color: #667eea;
  transform: translateY(-1px);
}

.pago-option input[type="radio"]:checked + .pago-label {
  color: #667eea;
  font-weight: bold;
}

.pago-label {
  display: flex;
  flex-direction: column;
  color: #333;
}

.pago-label small {
  color: #666;
  font-size: 0.8em;
}

.no-disponible {
  color: #ef4444;
  font-size: 0.8em;
  margin-top: 4px;
  font-weight: 500;
}

.mensaje {
  padding: 12px;
  border-radius: 8px;
  margin: 15px 0;
  text-align: center;
  font-weight: 500;
}

.mensaje:not(.error) {
  background: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.mensaje.error {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

.medio-pago-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.section-label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  color: #333;
  font-size: 1em;
}

.medio-pago-options {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.medio-pago-option {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 150px;
  background: white;
}

.medio-pago-option:hover {
  border-color: #667eea;
  transform: translateY(-1px);
}

.medio-pago-option input[type="radio"]:checked + .medio-pago-label {
  color: #667eea;
  font-weight: bold;
}

.medio-pago-option input[type="radio"]:checked {
  border-color: #667eea;
}

.medio-pago-label {
  display: flex;
  flex-direction: column;
  margin-left: 8px;
  color: #333;
}

.medio-pago-label small {
  color: #666;
  font-size: 0.8em;
  margin-top: 2px;
}

input[type="radio"] {
  accent-color: #667eea;
}

.btn-registrar:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.btn-registrar:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
</style>