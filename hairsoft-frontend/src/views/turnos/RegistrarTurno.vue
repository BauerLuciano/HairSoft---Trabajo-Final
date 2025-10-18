<template>
  <div class="form-container">
    <div class="form-card">
      <h1 class="form-title">Registrar Turno</h1>
      <p class="form-subtitle">Completa los datos del turno</p>

      <form @submit.prevent="crearTurno" class="form-grid">

        <!-- Cliente -->
        <div class="input-group full-width cliente-wrapper">
          <input 
            type="text" 
            v-model="form.clienteNombre" 
            @input="buscarCliente" 
            class="input-field" 
            placeholder="Cliente (*)"
          />
          <span class="input-icon lupa" @click="buscarCliente()">🔍</span>
          <button type="button" class="btn-agregar-cliente" @click="irRegistroUsuario()">⋯</button>

          <ul v-if="clientesSugeridos.length" class="sugerencias-list">
            <li v-for="c in clientesSugeridos" :key="c.id" @click="seleccionarCliente(c)">
              {{ c.nombre }} {{ c.apellido }} - {{ c.dni }}
            </li>
          </ul>
        </div>

        <!-- Fecha -->
        <div class="input-group">
          <label>Fecha del turno</label>
          <input 
            type="date" 
            v-model="form.fecha" 
            :min="fechaMin" 
            :max="fechaMax" 
            class="input-field"
            @change="actualizarHorasDisponibles"
            required
          />
        </div>

        <!-- Peluquero -->
        <div class="input-group">
          <label>Peluquero</label>
          <select v-model="form.peluquero" class="input-field" @change="actualizarHorasDisponibles" required>
            <option value="">Seleccione peluquero</option>
            <option v-for="p in peluqueros" :key="p.id" :value="p.id">{{ p.nombre }} {{ p.apellido }}</option>
          </select>
        </div>

        <!-- Servicio -->
        <div class="input-group">
          <label>Servicio</label>
          <select v-model="form.servicio" class="input-field" @change="actualizarHorasDisponibles" required>
            <option value="">Seleccione servicio</option>
            <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
          </select>
        </div>

        <!-- Hora -->
        <div class="input-group full-width">
          <label>Hora del turno (*)</label>

          <div class="time-grid">
            <div 
              v-for="h in horariosBase" 
              :key="h" 
              class="time-slot"
              :class="{ 
                selected: form.hora === h,
                disabled: horasDisponibles.length && !horasDisponibles.includes(h)
              }"
              @click="seleccionarHorario(h)"
            >
              <span class="hora-principal">{{ h }}</span>
              <span class="hora-badge" v-if="horasDisponibles.length">
                {{ horasDisponibles.includes(h) ? 'Libre' : 'Ocupado' }}
              </span>
            </div>
          </div>

          <div v-if="form.hora" class="hora-resumen">
            <strong>{{ form.hora }}</strong> → <strong>{{ calcularHoraFin() }}</strong>
            <span v-if="form.servicio">({{ duracionServicio() }} min)</span>
          </div>
        </div>

        <!-- Botón Guardar -->
        <div class="input-group full-width">
          <button type="submit" class="submit-button" :disabled="!form.hora">Guardar</button>
        </div>

      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        cliente: null,
        clienteNombre: '',
        fecha: '',
        hora: '',
        peluquero: '',
        servicio: ''
      },
      clientesSugeridos: [],
      peluqueros: [],
      servicios: [],
      fechaMin: '',
      fechaMax: '',
      horasDisponibles: [],
      horariosBase: []
    };
  },
  mounted() {
    this.calcularFechas();
    this.cargarServicios();
    this.cargarPeluqueros();
    this.generarHorariosBase();
  },
  methods: {
    calcularFechas() {
      const hoy = new Date();
      const max = new Date();
      max.setDate(hoy.getDate() + 7);
      this.fechaMin = hoy.toISOString().split('T')[0];
      this.fechaMax = max.toISOString().split('T')[0];
    },

    generarHorariosBase() {
      const horarios = [];
      for (let hora = 8; hora < 20; hora++) {
        for (let minuto = 0; minuto < 60; minuto += 20) {
          const h = hora.toString().padStart(2, '0');
          const m = minuto.toString().padStart(2, '0');
          horarios.push(`${h}:${m}`);
        }
      }
      this.horariosBase = horarios;
    },

    async cargarServicios() {
      const res = await fetch('http://localhost:8000/usuarios/api/servicios/');
      this.servicios = await res.json();
    },

    async cargarPeluqueros() {
      const res = await fetch('http://localhost:8000/usuarios/api/peluqueros/');
      this.peluqueros = await res.json();
    },

    async buscarCliente() {
      if (!this.form.clienteNombre) {
        this.clientesSugeridos = [];
        return;
      }
      const res = await fetch(`http://localhost:8000/usuarios/api/clientes/?q=${this.form.clienteNombre}`);
      const data = await res.json();
      this.clientesSugeridos = data.results;
    },

    seleccionarCliente(c) {
      this.form.cliente = c.id;
      this.form.clienteNombre = `${c.nombre} ${c.apellido}`;
      this.clientesSugeridos = [];
    },

    seleccionarHorario(h) {
      if (this.horasDisponibles.length && !this.horasDisponibles.includes(h)) {
        return;
      }
      this.form.hora = h;
    },

    calcularHoraFin() {
      if (!this.form.hora || !this.form.servicio) return '--:--';
      const servicio = this.servicios.find(s => s.id === this.form.servicio);
      const duracion = servicio?.duracion || 20;
      const [hh, mm] = this.form.hora.split(':').map(Number);
      const totalMin = hh * 60 + mm + duracion;
      const horaFin = Math.floor(totalMin / 60);
      const minFin = totalMin % 60;
      return `${horaFin.toString().padStart(2, '0')}:${minFin.toString().padStart(2, '0')}`;
    },

    duracionServicio() {
      if (!this.form.servicio) return 20;
      const servicio = this.servicios.find(s => s.id === this.form.servicio);
      return servicio?.duracion || 20;
    },

    async actualizarHorasDisponibles() {
      if (!this.form.fecha || !this.form.peluquero || !this.form.servicio) {
        this.horasDisponibles = [];
        return;
      }

      const servicioSel = this.servicios.find(s => s.id === this.form.servicio);
      const duracion = servicioSel?.duracion || 20;

      const res = await fetch(`http://localhost:8000/usuarios/api/turnos/?fecha=${this.form.fecha}&peluquero=${this.form.peluquero}`);
      const turnos = await res.json();

      const inicio = 8 * 60;
      const fin = 20 * 60;
      const horarios = [];

      for (let min = inicio; min <= fin - duracion; min += 20) {
        const hh = Math.floor(min / 60).toString().padStart(2, '0');
        const mm = (min % 60).toString().padStart(2, '0');
        const horaStr = `${hh}:${mm}`;

        const conflict = turnos.some(t => {
          if (!t.hora) return false;
          const [th, tm] = t.hora.split(':').map(Number);
          const tInicio = th * 60 + tm;
          const tFin = tInicio + (t.servicio_duracion || 20);
          return (min < tFin && (min + duracion) > tInicio);
        });

        if (!conflict) horarios.push(horaStr);
      }

      this.horasDisponibles = horarios;
      if (!horarios.includes(this.form.hora)) this.form.hora = '';
    },

    async crearTurno() {
      // Validar todos los campos
      if (!this.form.fecha || !this.form.hora || !this.form.cliente || !this.form.peluquero || !this.form.servicio) {
        alert('Por favor, complete todos los campos antes de registrar el turno.');
        return;
      }

      // Combinar fecha y hora
      const fecha_hora = `${this.form.fecha} ${this.form.hora}`;

      const data = {
        cliente: this.form.cliente,
        peluquero: this.form.peluquero,
        servicio: this.form.servicio,   // <-- usa [this.form.servicio] si es ManyToMany
        fecha_hora: fecha_hora
      };

      try {
        const res = await fetch('http://localhost:8000/usuarios/api/turnos/crear/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });

        if (res.ok) {
          alert('Turno registrado con éxito');
          this.form = { cliente: null, clienteNombre: '', fecha: '', hora: '', peluquero: '', servicio: '' };
          this.horasDisponibles = [];
        } else {
          const errorData = await res.json();
          alert('Error al registrar turno: ' + JSON.stringify(errorData));
        }
      } catch (err) {
        alert('Error al conectar con el servidor: ' + err.message);
      }
    },

    irRegistroUsuario() {
      window.location.href = '/usuarios/crear/';
    }
  },
  watch: {
    'form.fecha': 'actualizarHorasDisponibles',
    'form.peluquero': 'actualizarHorasDisponibles',
    'form.servicio': 'actualizarHorasDisponibles'
  }
};
</script>



<style scoped>
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

.time-grid::-webkit-scrollbar {
  width: 8px;
}

.time-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.time-grid::-webkit-scrollbar-thumb {
  background: #667eea;
  border-radius: 10px;
}

.time-slot {
  padding: 12px 10px;
  border: 2px solid #e0e0e0;
  background: rgb(92, 92, 92);
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
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.time-slot.selected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.time-slot.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: #f9f9f9;
}

.time-slot.disabled:hover {
  transform: none;
  box-shadow: none;
  border-color: #e0e0e0;
}

.hora-principal {
  font-weight: 700;
  font-size: 16px;
}

.hora-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  background: #e8f5e9;
  color: #2e7d32;
}

.time-slot.disabled .hora-badge {
  background: #ffebee;
  color: #c62828;
}

.time-slot.selected .hora-badge {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.hora-resumen {
  margin-top: 15px;
  padding: 15px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 10px;
  text-align: center;
  font-size: 18px;
  color: #333;
}

.hora-resumen strong {
  color: #667eea;
  font-weight: 700;
}

.hora-resumen span {
  font-size: 14px;
  color: #666;
  margin-left: 8px;
}

@media (max-width: 768px) {
  .time-grid {
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
    gap: 8px;
  }
  
  .time-slot {
    padding: 10px 8px;
  }
  
  .hora-principal {
    font-size: 14px;
  }
  
  .hora-badge {
    font-size: 9px;
  }
}

.text-muted {
  color: #999;
  font-style: italic;
  display: block;
  padding: 20px;
  text-align: center;
}
</style>