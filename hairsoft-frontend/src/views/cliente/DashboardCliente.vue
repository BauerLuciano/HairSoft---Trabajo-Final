<template>
  <div class="dashboard-cliente">
    <!-- Tarjeta de bienvenida -->
    <div class="welcome-card">
      <div class="welcome-content">
        <h1>¡Hola, <span class="nombre-destacado">{{ cliente.nombre || 'Cliente' }}</span>! 👋</h1>
        <p class="welcome-subtitle">Bienvenido a tu espacio personal en <span class="brand-highlight">HairSoft</span></p>
        <p class="welcome-message">Aquí puedes gestionar tus citas, ver tu historial y administrar tu perfil.</p>
      </div>
      
      <!-- Estadísticas REALES -->
      <div class="welcome-stats">
        <div class="stat-item">
          <div class="stat-number">{{ turnosProximos.length }}</div>
          <div class="stat-label">Próximos</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ turnosCompletados.length }}</div>
          <div class="stat-label">Completados</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ turnosCancelados.length }}</div>
          <div class="stat-label">Cancelados</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ turnosTotal }}</div>
          <div class="stat-label">Total</div>
        </div>
      </div>
      <div class="welcome-border"></div>
    </div>

    <!-- Sección de acciones principales -->
    <div class="section-header">
      <h2>Acciones Rápidas</h2>
      <p>Gestiona tus servicios de forma eficiente</p>
    </div>

    <div class="actions-grid">
      <div class="action-card primary" @click="irANuevoTurno">
        <div class="card-header">
          <div class="card-icon primary">📅</div>
          <div class="card-badge" v-if="tieneTurnosPendientes">¡Nuevo!</div>
        </div>
        <h3>Nuevo Turno</h3>
        <p>Reserva tu próxima cita ahora mismo</p>
        <div class="card-footer">
          <span class="card-cta">Reservar ahora →</span>
        </div>
        <div class="card-hover-effect"></div>
      </div>
      
      <div class="action-card secondary" @click="irAPerfil">
        <div class="card-header">
          <div class="card-icon secondary">👤</div>
        </div>
        <h3>Mis Datos</h3>
        <p>Actualiza tu información personal y preferencias</p>
        <div class="card-footer">
          <span class="card-cta">Editar perfil →</span>
        </div>
        <div class="card-hover-effect"></div>
      </div>

      <div class="action-card accent" @click="irAHistorial">
        <div class="card-header">
          <div class="card-icon accent">📜</div>
          <div class="card-badge" v-if="turnosRecientes > 0">{{ turnosRecientes }} nuevos</div>
        </div>
        <h3>Historial</h3>
        <p>Revisa tus turnos pasados y facturación</p>
        <div class="card-footer">
          <span class="card-cta">Ver historial →</span>
        </div>
        <div class="card-hover-effect"></div>
      </div>
    </div>

    <!-- SECCIÓN DE TURNOS PRÓXIMOS -->
    <div class="section-header" v-if="turnosProximos.length > 0">
      <div class="section-header-content">
        <div>
          <h2>Próximos Turnos</h2>
          <p>Tus próximas citas agendadas</p>
        </div>
        <button class="btn-refresh" @click="cargarTurnos" :disabled="cargando">
          <span v-if="cargando">⏳</span>
          <span v-else>↻ Actualizar</span>
        </button>
      </div>
    </div>

    <div class="turnos-container" v-if="turnosProximos.length > 0 && !cargando">
      <div class="turno-card" v-for="turno in turnosProximos" :key="turno.id">
        <div class="turno-fecha">
          <div class="turno-dia">{{ formatearDia(turno.fecha) }}</div>
          <div class="turno-mes">{{ formatearMes(turno.fecha) }}</div>
          <div class="turno-anio">{{ formatearAnio(turno.fecha) }}</div>
        </div>
        <div class="turno-info">
          <div class="turno-header">
            <h4>{{ getNombreServicios(turno.servicios) }}</h4>
            <span class="turno-precio" v-if="turno.monto_total > 0">${{ turno.monto_total }}</span>
          </div>
          <p class="turno-hora">⏰ {{ turno.hora }}</p>
          <p class="turno-estado" :class="getEstadoClass(turno.estado)">
            {{ formatearEstado(turno.estado) }}
          </p>
          <div class="turno-detalles">
            <p v-if="turno.peluquero_nombre">
              💇‍♀️ {{ turno.peluquero_nombre }} {{ turno.peluquero_apellido || '' }}
            </p>
            <p class="turno-pago" v-if="turno.tipo_pago && turno.tipo_pago !== 'PENDIENTE'">
              💳 {{ getTipoPagoTexto(turno.tipo_pago) }}
            </p>
            <p v-if="turno.monto_seña > 0" class="turno-sena">
              💰 Seña: ${{ turno.monto_seña }}
            </p>
          </div>
        </div>
        <div class="turno-acciones">
          <button 
            class="btn-turno btn-modificar" 
            @click="verDetalleTurno(turno)"
          >
            Ver Detalle
          </button>
          <button 
            class="btn-turno btn-cancelar" 
            @click="confirmarCancelacion(turno)"
            v-if="turno.estado === 'RESERVADO' || turno.estado === 'CONFIRMADO'"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>

    <!-- SECCIÓN DE TURNOS CANCELADOS -->
    <div class="section-header" v-if="turnosCancelados.length > 0">
      <h2>Turnos Cancelados</h2>
      <p>Historial de turnos cancelados</p>
    </div>

    <div class="turnos-container cancelados-container" v-if="turnosCancelados.length > 0 && !cargando">
      <div class="turno-card cancelado-card" v-for="turno in turnosCancelados" :key="turno.id">
        <div class="turno-fecha cancelado-fecha">
          <div class="turno-dia">{{ formatearDia(turno.fecha) }}</div>
          <div class="turno-mes">{{ formatearMes(turno.fecha) }}</div>
          <div class="turno-anio">{{ formatearAnio(turno.fecha) }}</div>
        </div>
        <div class="turno-info">
          <div class="turno-header">
            <h4 class="cancelado-text">{{ getNombreServicios(turno.servicios) }}</h4>
            <span class="turno-precio cancelado-text" v-if="turno.monto_total > 0">${{ turno.monto_total }}</span>
          </div>
          <p class="turno-hora cancelado-text">⏰ {{ turno.hora }}</p>
          <p class="turno-estado estado-cancelado">
            Cancelado
          </p>
          <div class="turno-detalles">
            <p class="cancelado-text" v-if="turno.peluquero_nombre">
              💇‍♀️ {{ turno.peluquero_nombre }} {{ turno.peluquero_apellido || '' }}
            </p>
          </div>
        </div>
        <div class="turno-acciones">
          <button 
            class="btn-turno btn-modificar" 
            @click="verDetalleTurno(turno)"
          >
            Ver Detalle
          </button>
        </div>
      </div>
    </div>

    <!-- SECCIÓN DE TURNOS COMPLETADOS -->
    <div class="section-header" v-if="turnosCompletados.length > 0">
      <h2>Historial Completado</h2>
      <p>Turnos finalizados anteriormente</p>
    </div>

    <div class="turnos-container completados-container" v-if="turnosCompletados.length > 0 && !cargando">
      <div class="turno-card completado-card" v-for="turno in turnosCompletados" :key="turno.id">
        <div class="turno-fecha completado-fecha">
          <div class="turno-dia">{{ formatearDia(turno.fecha) }}</div>
          <div class="turno-mes">{{ formatearMes(turno.fecha) }}</div>
          <div class="turno-anio">{{ formatearAnio(turno.fecha) }}</div>
        </div>
        <div class="turno-info">
          <div class="turno-header">
            <h4>{{ getNombreServicios(turno.servicios) }}</h4>
            <span class="turno-precio completado-text" v-if="turno.monto_total > 0">${{ turno.monto_total }}</span>
          </div>
          <p class="turno-hora completado-text">⏰ {{ turno.hora }}</p>
          <p class="turno-estado estado-completado">
            Completado
          </p>
          <div class="turno-detalles">
            <p class="completado-text" v-if="turno.peluquero_nombre">
              💇‍♀️ {{ turno.peluquero_nombre }} {{ turno.peluquero_apellido || '' }}
            </p>
            <p class="turno-pago completado-text" v-if="turno.tipo_pago && turno.tipo_pago !== 'PENDIENTE'">
              💳 {{ getTipoPagoTexto(turno.tipo_pago) }}
            </p>
          </div>
        </div>
        <div class="turno-acciones">
          <button 
            class="btn-turno btn-modificar" 
            @click="verDetalleTurno(turno)"
          >
            Ver Detalle
          </button>
        </div>
      </div>
    </div>

    <!-- Estados de carga -->
    <div class="loading-state" v-if="cargando && turnosProximos.length === 0 && turnosCompletados.length === 0 && turnosCancelados.length === 0">
      <div class="spinner"></div>
      <p>Cargando tus turnos...</p>
    </div>

    <div class="no-turnos" v-if="!cargando && turnosProximos.length === 0 && turnosCompletados.length === 0 && turnosCancelados.length === 0 && !error">
      <div class="no-turnos-icon">📅</div>
      <h3>No tienes turnos</h3>
      <p>¡Reserva tu primera cita ahora!</p>
      <button class="btn-primary" @click="irANuevoTurno">Reservar Turno</button>
    </div>

    <!-- Estado de error -->
    <div class="error-state" v-if="error">
      <div class="error-icon">⚠️</div>
      <h3>Error al cargar datos</h3>
      <p>{{ error }}</p>
      <button class="btn-primary" @click="cargarDatos">Reintentar</button>
    </div>

    <!-- Notificaciones -->
    <div class="notificaciones-container" v-if="notificaciones.length > 0">
      <div 
        class="notificacion-item" 
        :class="notif.type" 
        v-for="notif in notificaciones" 
        :key="notif.id"
      >
        <div class="notificacion-icon">{{ notif.icon }}</div>
        <div class="notificacion-content">
          <strong>{{ notif.titulo }}</strong>
          <p>{{ notif.mensaje }}</p>
        </div>
      </div>
    </div>

    <!-- Modal de cancelación -->
    <div v-if="showCancelModal" class="modal-overlay">
      <div class="modal-content">
        <button class="modal-close" @click="showCancelModal = false">×</button>
        <div class="modal-body">
          <h3>Cancelar Turno</h3>
          <p>¿Estás seguro de cancelar el turno del <strong>{{ formatearFechaCompleta(turnoACancelar?.fecha) }}</strong> a las <strong>{{ turnoACancelar?.hora }}</strong>?</p>
          <p class="modal-advertencia" v-if="turnoACancelar?.monto_seña > 0">
            ⚠️ Monto de seña: ${{ turnoACancelar?.monto_seña }}
          </p>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showCancelModal = false">
              Volver
            </button>
            <button class="btn-danger" @click="cancelarTurno">
              Sí, Cancelar Turno
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api'; // ← ¡MISMA INSTANCIA QUE HistorialTurnos.vue!

const router = useRouter();

// Estados reactivos
const cargando = ref(false);
const error = ref(null);
const cliente = ref({});
const todosTurnos = ref([]);
const showCancelModal = ref(false);
const turnoACancelar = ref(null);

// Computed properties (IGUAL QUE ANTES)
const turnosProximos = computed(() => {
  const ahora = new Date();
  return todosTurnos.value.filter(turno => {
    if (!turno.fecha) return false;
    
    const fechaTurno = new Date(turno.fecha);
    const [horas, minutos] = turno.hora.split(':').map(Number);
    fechaTurno.setHours(horas, minutos, 0, 0);
    
    return fechaTurno >= ahora && 
           turno.estado !== 'CANCELADO' && 
           turno.estado !== 'COMPLETADO';
  }).sort((a, b) => {
    const fechaA = new Date(a.fecha + 'T' + a.hora);
    const fechaB = new Date(b.fecha + 'T' + b.hora);
    return fechaA - fechaB;
  });
});

const turnosCompletados = computed(() => {
  return todosTurnos.value.filter(turno => 
    turno.estado === 'COMPLETADO'
  ).sort((a, b) => {
    const fechaA = new Date(a.fecha + 'T' + a.hora);
    const fechaB = new Date(b.fecha + 'T' + b.hora);
    return fechaB - fechaA;
  });
});

const turnosCancelados = computed(() => {
  return todosTurnos.value.filter(turno => 
    turno.estado === 'CANCELADO'
  ).sort((a, b) => {
    const fechaA = new Date(a.fecha + 'T' + a.hora);
    const fechaB = new Date(b.fecha + 'T' + b.hora);
    return fechaB - fechaA;
  });
});

const turnosTotal = computed(() => todosTurnos.value.length);
const tieneTurnosPendientes = computed(() => turnosProximos.value.length > 0);

const turnosRecientes = computed(() => {
  const unaSemanaAtras = new Date();
  unaSemanaAtras.setDate(unaSemanaAtras.getDate() - 7);
  
  return turnosCompletados.value.filter(turno => {
    const fechaTurno = new Date(turno.fecha + 'T' + turno.hora);
    return fechaTurno > unaSemanaAtras;
  }).length;
});

const notificaciones = computed(() => {
  const notifs = [];
  
  if (turnosProximos.value.length > 0) {
    const proximoTurno = turnosProximos.value[0];
    notifs.push({
      id: 1,
      type: 'info',
      icon: '📅',
      titulo: 'Próximo turno',
      mensaje: `Tienes un turno el ${formatearFechaCompleta(proximoTurno.fecha)} a las ${proximoTurno.hora}`
    });
  }
  
  const turnosConSena = turnosProximos.value.filter(t => t.tipo_pago === 'SENA_50' && t.monto_seña > 0);
  if (turnosConSena.length > 0) {
    notifs.push({
      id: 2,
      type: 'warning',
      icon: '💳',
      titulo: 'Señas pendientes',
      mensaje: `Tienes ${turnosConSena.length} turno(s) con seña del 50%`
    });
  }
  
  if (turnosCancelados.value.length > 0) {
    notifs.push({
      id: 3,
      type: 'warning',
      icon: '⚠️',
      titulo: 'Turnos cancelados',
      mensaje: `Tienes ${turnosCancelados.value.length} turno(s) cancelado(s)`
    });
  }
  
  return notifs;
});

// Funciones de formato
const formatearDia = (fecha) => {
  if (!fecha) return '--';
  const date = new Date(fecha);
  return date.getDate().toString().padStart(2, '0');
};

const formatearMes = (fecha) => {
  if (!fecha) return '---';
  const meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
  const date = new Date(fecha);
  return meses[date.getMonth()];
};

const formatearAnio = (fecha) => {
  if (!fecha) return '--';
  const date = new Date(fecha);
  return date.getFullYear().toString().slice(-2);
};

const formatearEstado = (estado) => {
  const estados = {
    'RESERVADO': 'Reservado',
    'CONFIRMADO': 'Confirmado',
    'COMPLETADO': 'Completado',
    'CANCELADO': 'Cancelado'
  };
  return estados[estado] || estado;
};

const getEstadoClass = (estado) => {
  const clases = {
    'RESERVADO': 'estado-reservado',
    'CONFIRMADO': 'estado-confirmado',
    'COMPLETADO': 'estado-completado',
    'CANCELADO': 'estado-cancelado'
  };
  return clases[estado] || 'estado-reservado';
};

const formatearFechaCompleta = (fecha) => {
  if (!fecha) return '';
  const date = new Date(fecha);
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
};

const getNombreServicios = (servicios) => {
  if (!servicios) return 'Servicio';
  
  if (typeof servicios === 'string') {
    return servicios || 'Servicio';
  }
  
  if (Array.isArray(servicios)) {
    if (servicios.length === 0) return 'Servicio';
    
    if (servicios.length === 1) {
      const servicio = servicios[0];
      if (typeof servicio === 'object' && servicio.nombre) {
        return servicio.nombre;
      }
      return servicio.toString();
    }
    
    const primerServicio = servicios[0];
    const nombrePrimero = typeof primerServicio === 'object' ? primerServicio.nombre : primerServicio.toString();
    return `${nombrePrimero} +${servicios.length - 1} más`;
  }
  
  return 'Servicio';
};

const getTipoPagoTexto = (tipoPago) => {
  const tipos = {
    'SENA_50': 'Seña 50%',
    'TOTAL': 'Pago Total',
    'PENDIENTE': 'Pendiente de Pago',
    'EFECTIVO': 'Efectivo',
    'TARJETA': 'Tarjeta',
    'TRANSFERENCIA': 'Transferencia'
  };
  return tipos[tipoPago] || tipoPago;
};

// 🚨🚨🚨 FUNCIÓN CORREGIDA - USANDO LA MISMA API INSTANCE 🚨🚨🚨
const cargarTurnos = async () => {
  cargando.value = true;
  error.value = null;
  
  try {
    // ¡USAR EXACTAMENTE LO MISMO QUE HistorialTurnos.vue!
    const response = await api.get('/turnos/mis-turnos/');
    
    if (!Array.isArray(response.data)) {
      throw new Error('Formato de datos inválido');
    }
    
    procesarTurnosRecibidos(response.data);
    
  } catch (err) {
    console.error('Error cargando turnos:', err);
    error.value = 'No se pudieron cargar los turnos. Intenta nuevamente.';
    todosTurnos.value = [];
  } finally {
    cargando.value = false;
  }
};

// FUNCIÓN PROCESAR TURNOS
const procesarTurnosRecibidos = (data) => {
  todosTurnos.value = data.map(turno => {
    let peluquero_nombre = '';
    let peluquero_apellido = '';
    
    if (turno.peluquero_nombre) {
      const nombres = turno.peluquero_nombre.split(' ');
      peluquero_nombre = nombres[0] || '';
      peluquero_apellido = nombres.slice(1).join(' ') || '';
    }
    
    let serviciosArray = [];
    if (Array.isArray(turno.servicios)) {
      serviciosArray = turno.servicios;
    } else if (typeof turno.servicios === 'string') {
      serviciosArray = turno.servicios.split(', ').map((nombre, idx) => ({
        id: idx + 1,
        nombre: nombre.trim(),
        precio: 0,
        duracion: 0
      }));
    }
    
    return {
      id: turno.id,
      fecha: turno.fecha,
      hora: turno.hora,
      estado: turno.estado || 'RESERVADO',
      tipo_pago: turno.tipo_pago || 'PENDIENTE',
      monto_seña: parseFloat(turno.monto_seña || 0),
      monto_total: parseFloat(turno.monto_total || 0),
      peluquero_nombre: peluquero_nombre,
      peluquero_apellido: peluquero_apellido,
      servicios: serviciosArray,
      duracion_total: turno.duracion || 0,
      canal: turno.canal || 'WEB',
      medio_pago: turno.medio_pago || 'EFECTIVO',
      puede_cancelar: turno.puede_cancelar || false
    };
  });
};

// Cargar datos del cliente
const cargarDatosCliente = () => {
  const userId = localStorage.getItem('user_id');
  const userNombre = localStorage.getItem('user_nombre');
  const userEmail = localStorage.getItem('user_email');
  const userTelefono = localStorage.getItem('user_telefono');
  const userRol = localStorage.getItem('user_rol');
  
  cliente.value = {
    id: userId,
    nombre: userNombre || 'Cliente',
    email: userEmail || '',
    telefono: userTelefono || '',
    rol: userRol || ''
  };
};

const cargarDatos = () => {
  cargarDatosCliente();
  cargarTurnos();
};

// Funciones de navegación
const irANuevoTurno = () => {
  router.push('/turnos/crear-web');
};

const irAPerfil = () => {
  router.push({ name: 'PerfilCliente' });
};

const irAHistorial = () => {
  router.push('/cliente/historial');
};

const verDetalleTurno = (turno) => {
  if (turno.id) {
    router.push(`/turnos/detalle/${turno.id}`);
  }
};

// Funciones de cancelación
const confirmarCancelacion = (turno) => {
  if (!turno.puede_cancelar) {
    alert('Este turno no puede ser cancelado.');
    return;
  }
  
  turnoACancelar.value = turno;
  showCancelModal.value = true;
};

const cancelarTurno = async () => {
  if (!turnoACancelar.value) return;
  
  try {
    cargando.value = true;
    showCancelModal.value = false;
    
    const response = await api.post(`/turnos/${turnoACancelar.value.id}/cancelar-con-reoferta/`);
    
    await cargarTurnos();
    alert(response.data.message || 'Turno cancelado exitosamente');
    
  } catch (err) {
    alert(err.response?.data?.message || 'No se pudo cancelar el turno.');
  } finally {
    cargando.value = false;
    turnoACancelar.value = null;
  }
};

// Lifecycle
onMounted(() => {
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }
  
  cargarDatos();
});
</script>

<style scoped>
/* ESTILOS COMPLETOS MANTENIENDO TU DISEÑO ORIGINAL */

.dashboard-cliente {
  padding: 2rem;
  max-width: 2000px;
  margin: auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* Tarjeta de bienvenida */
.welcome-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
  border-radius: 24px;
  padding: 2.5rem;
  margin-bottom: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
}

.welcome-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

.welcome-content {
  margin-bottom: 2rem;
}

.welcome-content h1 {
  margin: 0 0 1rem 0;
  font-size: 2.5rem;
  font-weight: 900;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nombre-destacado {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  animation: gradient 3s ease infinite;
  background-size: 200% 200%;
}

@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.welcome-subtitle {
  color: #94a3b8;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.brand-highlight {
  color: #0ea5e9;
  font-weight: 700;
}

.welcome-message {
  color: #64748b;
  font-size: 0.95rem;
}

/* Estadísticas */
.welcome-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1.5rem;
  background: rgba(15, 23, 42, 0.6);
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.stat-item {
  text-align: center;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(30, 41, 59, 0.3);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-item:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 10px 20px rgba(14, 165, 233, 0.1);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 900;
  margin-bottom: 0.25rem;
}

.stat-item:nth-child(1) .stat-number {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-item:nth-child(2) .stat-number {
  background: linear-gradient(135deg, #10b981, #059669);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-item:nth-child(3) .stat-number {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-item:nth-child(4) .stat-number {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Secciones */
.section-header {
  margin-bottom: 2rem;
}

.section-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header h2 {
  font-size: 1.8rem;
  font-weight: 900;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.section-header p {
  color: #94a3b8;
  font-size: 1rem;
}

/* Grid de acciones */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.action-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.action-card:hover {
  transform: translateY(-5px);
  border-color: #0ea5e9;
  box-shadow: 0 15px 30px rgba(14, 165, 233, 0.2);
}

.action-card.primary {
  border-top: 4px solid #0ea5e9;
}

.action-card.secondary {
  border-top: 4px solid #8b5cf6;
}

.action-card.accent {
  border-top: 4px solid #10b981;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-icon {
  font-size: 2.5rem;
}

.card-icon.primary {
  color: #0ea5e9;
}

.card-icon.secondary {
  color: #8b5cf6;
}

.card-icon.accent {
  color: #10b981;
}

.card-badge {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.action-card h3 {
  color: white;
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.75rem;
}

.action-card p {
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-cta {
  color: #0ea5e9;
  font-weight: 700;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.action-card:hover .card-cta {
  transform: translateX(5px);
}

.card-hover-effect {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: 0.5s;
}

.action-card:hover .card-hover-effect {
  left: 100%;
}

/* Tarjetas de turnos */
.turnos-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.turno-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: stretch;
  gap: 1.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  min-height: 180px;
  backdrop-filter: blur(10px);
}

.turno-card:hover {
  border-color: #0ea5e9;
  box-shadow: 0 15px 30px rgba(14, 165, 233, 0.2);
  transform: translateY(-2px);
}

/* Fecha */
.turno-fecha {
  text-align: center;
  min-width: 70px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 12px;
  padding: 0.5rem;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.turno-dia {
  font-size: 2rem;
  font-weight: 900;
  color: #0ea5e9;
  line-height: 1;
}

.turno-mes {
  font-size: 0.85rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  margin: 0.25rem 0;
}

.turno-anio {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

/* Información del turno */
.turno-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.turno-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.turno-header h4 {
  color: white;
  margin: 0;
  font-weight: 700;
  font-size: 1.1rem;
  flex: 1;
}

.turno-precio {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  white-space: nowrap;
}

.turno-hora {
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.turno-estado {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0;
  align-self: flex-start;
}

.estado-reservado {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.estado-confirmado {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.estado-completado {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.estado-cancelado {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
}

.turno-detalles {
  margin-top: auto;
}

.turno-detalles p {
  color: #94a3b8;
  font-size: 0.85rem;
  margin: 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.turno-pago {
  color: #8b5cf6 !important;
}

.turno-sena {
  color: #f59e0b !important;
  font-weight: 600;
}

/* Acciones del turno */
.turno-acciones {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 120px;
  justify-content: center;
}

.btn-turno {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  white-space: nowrap;
}

.btn-modificar {
  background: transparent;
  color: #0ea5e9;
  border: 1px solid #0ea5e9;
}

.btn-modificar:hover {
  background: rgba(14, 165, 233, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(14, 165, 233, 0.2);
}

.btn-cancelar {
  background: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.btn-cancelar:hover {
  background: rgba(239, 68, 68, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(239, 68, 68, 0.2);
}

/* Estilos para cancelados */
.cancelados-container .turno-card {
  border-color: rgba(239, 68, 68, 0.2);
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.7));
}

.cancelados-container .turno-card:hover {
  border-color: #ef4444;
}

.cancelados-container .turno-fecha {
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.1);
}

.cancelados-container .turno-dia,
.cancelados-container .turno-mes,
.cancelados-container .turno-anio {
  color: #ef4444;
  opacity: 0.7;
}

.cancelado-text {
  color: #9ca3af !important;
  text-decoration: line-through;
  opacity: 0.7;
}

/* Estilos para completados */
.completados-container .turno-card {
  border-color: rgba(59, 130, 246, 0.2);
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.7));
}

.completados-container .turno-card:hover {
  border-color: #3b82f6;
}

.completados-container .turno-fecha {
  background: rgba(59, 130, 246, 0.05);
  border-color: rgba(59, 130, 246, 0.1);
}

.completado-text {
  color: #6b7280 !important;
  opacity: 0.8;
}

/* Botón refresh */
.btn-refresh {
  background: rgba(30, 41, 59, 0.8);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  backdrop-filter: blur(10px);
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Estados sin datos */
.loading-state,
.no-turnos,
.error-state {
  text-align: center;
  padding: 3rem;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  margin: 2rem 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #0ea5e9;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-turnos {
  border-color: rgba(14, 165, 233, 0.3);
  border-style: dashed;
}

.error-state {
  border-color: rgba(239, 68, 68, 0.3);
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #ef4444;
}

.no-turnos-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #0ea5e9;
}

.loading-state p,
.no-turnos h3,
.error-state h3 {
  color: white;
  margin-bottom: 0.5rem;
}

.loading-state p,
.no-turnos p,
.error-state p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

/* Notificaciones */
.notificaciones-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 3rem;
}

.notificacion-item {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.notificacion-item.info {
  border-left: 4px solid #0ea5e9;
}

.notificacion-item.warning {
  border-left: 4px solid #f59e0b;
}

.notificacion-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.notificacion-content {
  flex: 1;
}

.notificacion-content strong {
  color: white;
  display: block;
  margin-bottom: 0.25rem;
}

.notificacion-content p {
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.88);
  backdrop-filter: blur(12px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeInModal 0.3s ease;
}

@keyframes fadeInModal {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  position: relative;
  animation: slideUp 0.3s ease;
  max-height: 85vh;
  max-width: 900px;
  width: 100%;
  overflow-y: auto;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(255, 255, 255, 0.1);
  padding: 2rem;
  backdrop-filter: blur(20px);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.modal-close:hover {
  color: white;
  background: rgba(239, 68, 68, 0.1);
}

.modal-body h3 {
  color: white;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 800;
}

.modal-body p {
  color: #94a3b8;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.modal-body strong {
  color: white;
}

.modal-advertencia {
  color: #f59e0b !important;
  background: rgba(245, 158, 11, 0.1);
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.3);
  font-weight: 600;
  margin-top: 1rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.modal-actions button {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(239, 68, 68, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-cliente {
    padding: 1rem;
  }
  
  .welcome-content h1 {
    font-size: 2rem;
  }
  
  .welcome-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    padding: 1rem;
  }
  
  .stat-number {
    font-size: 2rem;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .turnos-container {
    grid-template-columns: 1fr;
  }
  
  .turno-card {
    flex-direction: column;
    gap: 1rem;
    min-height: auto;
  }
  
  .turno-fecha {
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    min-height: auto;
    padding: 0.75rem;
  }
  
  .turno-dia,
  .turno-mes,
  .turno-anio {
    margin: 0;
  }
  
  .turno-acciones {
    flex-direction: row;
    width: 100%;
  }
  
  .btn-turno {
    flex: 1;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>