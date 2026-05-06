<template>
  <div class="dashboard-cliente">
    
    <div class="welcome-header">
      <div class="welcome-text">
        <h1>Hola, <span class="text-highlight">{{ cliente.nombre }}</span></h1>
        <p>Bienvenido a tu panel de control personal en HairSoft</p>
      </div>
    </div>

    <div class="view-content fade-in">
      
      <div class="stats-grid">
        <div class="stat-card" @click="irAHistorial">
          <div class="stat-icon-wrapper blue">
            <Calendar class="stat-svg" :size="28" />
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ turnosProximos.length }}</span>
            <span class="stat-label">Turnos Activos</span>
          </div>
        </div>
        
        <div class="stat-card" @click="irAMisPedidos">
          <div class="stat-icon-wrapper purple">
            <ShoppingBag class="stat-svg" :size="28" />
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ cantidadPedidos }}</span>
            <span class="stat-label">Pedidos Totales</span>
          </div>
        </div>
      </div>

      <div class="actions-grid">
        <div class="action-card main-action" @click="irANuevoTurno">
          <div class="action-icon">
            <CalendarPlus :size="32" />
          </div>
          <div class="action-text">
            <h3>Nuevo Turno</h3>
            <p>Agenda tu próxima visita hoy</p>
          </div>
          <span class="action-arrow">→</span>
        </div>
        
        <div class="action-card secondary-action" @click="irAProductos">
          <div class="action-icon">
            <ShoppingCart :size="32" />
          </div>
          <div class="action-text">
            <h3>Ir a la Tienda</h3>
            <p>Productos profesionales</p>
          </div>
          <span class="action-arrow">→</span>
        </div>

        <div class="action-card secondary-action" @click="irAMisPedidos">
          <div class="action-icon">
            <Package :size="32" />
          </div>
          <div class="action-text">
            <h3>Mis Compras</h3>
            <p>Seguimiento de pedidos</p>
          </div>
          <span class="action-arrow">→</span>
        </div>

        <div class="action-card data-action" @click="irAPerfil">
          <div class="action-icon">
            <UserCircle :size="32" />
          </div>
          <div class="action-text">
            <h3>Mis Datos</h3>
            <p>Gestionar mi información</p>
          </div>
          <span class="action-arrow">→</span>
        </div>
      </div>

      <div class="section-box appointments-section">
        <div class="section-header">
          <div class="header-title">
            <Clock :size="20" class="icon-blue" />
            <h3>Tus Próximas Citas</h3>
          </div>
          <button class="btn-ver-todos" @click="irAHistorial">
            Ver historial completo <ChevronRight :size="16" />
          </button>
        </div>
        
        <div v-if="turnosProximos.length > 0" class="appointments-list">
          <div v-for="t in turnosProximos.slice(0, 4)" :key="t.id" class="appointment-item">
            <div class="apt-date">
              <span class="day">{{ formatearDia(t.fecha) }}</span>
              <span class="month">{{ formatearMes(t.fecha) }}</span>
            </div>
            
            <div class="apt-main-info">
              <div class="apt-services">
                {{ getNombreServicios(t.servicios) }}
              </div>
              <div class="apt-meta">
                <span class="apt-time"><Clock :size="14" /> {{ t.hora.substring(0, 5) }} hs</span>
                <span class="apt-barber"><User :size="14" /> {{ t.peluquero_nombre }}</span>
              </div>
            </div>

            <div class="apt-status-box">
              <span :class="['status-badge', getEstadoClass(t.estado)]">
                {{ formatearEstado(t.estado) }}
              </span>
              <button class="btn-quick-action" @click="irAHistorial" title="Gestionar turno">
                <Settings :size="16" />
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state-modern">
          <div class="empty-icon-circle">
            <CalendarX :size="40" />
          </div>
          <h4>No tenés turnos programados</h4>
          <p>¿Es hora de un nuevo corte? ¡Reservá tu lugar!</p>
          <button class="btn-schedule-first" @click="irANuevoTurno">
            Agendar mi primer turno
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/services/api';
import Swal from 'sweetalert2';
import { 
  Calendar, CalendarPlus, CalendarX, Clock, ShoppingBag, 
  ShoppingCart, User, ChevronRight, Settings, Package, UserCircle 
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();

const todosTurnos = ref([]);
const cantidadPedidos = ref(0);
const cliente = ref({ nombre: localStorage.getItem('user_nombre') || 'Cliente' });

const cargarDatos = async () => {
  try {
    const [resT, resP] = await Promise.all([
      api.get('/turnos/mis-turnos/'), 
      api.get('/pedidos-web/')
    ]);
    todosTurnos.value = resT.data;
    const lista = Array.isArray(resP.data) ? resP.data : (resP.data.results || []);
    cantidadPedidos.value = lista.length;
  } catch (e) { 
    console.error("Error al cargar los datos"); 
  }
};

onMounted(async () => {
  if (!localStorage.getItem('token')) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }
  await cargarDatos();
});

const turnosProximos = computed(() => {
  const hoy = new Date().toISOString().split('T')[0];
  return todosTurnos.value
    .filter(t => t.estado !== 'CANCELADO' && t.fecha >= hoy)
    .sort((a, b) => new Date(a.fecha + 'T' + a.hora) - new Date(b.fecha + 'T' + b.hora));
});

// Navegación
const irANuevoTurno = () => router.push({ name: 'RegistrarTurnoWeb' });
const irAProductos = () => router.push({ name: 'ProductosPublico' });
const irAPerfil = () => router.push({ name: 'PerfilCliente' });
const irAHistorial = () => router.push('/cliente/historial');
const irAMisPedidos = () => router.push({ name: 'MisPedidos' });

// Formateadores
const formatearDia = (f) => f ? f.split('-')[2] : '-';
const formatearMes = (f) => {
  if (!f) return '-';
  const meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
  const mesIndex = parseInt(f.split('-')[1]) - 1;
  return meses[mesIndex];
};

const getNombreServicios = (s) => {
  if (Array.isArray(s)) return s.map(serv => serv.nombre).join(', ');
  return s || 'Servicio General';
};

const getEstadoClass = (e) => {
  if (e === 'CONFIRMADO' || e === 'COMPLETADO') return 'status-confirmed';
  return 'status-reserved';
};

const formatearEstado = (e) => e === 'CONFIRMADO' ? 'Confirmado' : 'Reservado';
</script>

<style scoped>
/* ============================================
   ESTILOS PREMIUM - DASHBOARD CLIENTE
   ============================================ */

.dashboard-cliente {
  min-height: 100vh;
  background: #0f172a;
  color: #f8fafc;
  padding: 2.5rem;
  font-family: 'Inter', sans-serif;
}

.text-highlight {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* HEADER CON PERFIL */
.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #1e293b;
}

.welcome-text h1 { font-size: 2.5rem; font-weight: 800; margin: 0; }
.welcome-text p { color: #64748b; margin-top: 5px; }

.user-profile-summary {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 8px 15px;
  background: #1e293b;
  border-radius: 50px;
  border: 1px solid #334155;
  cursor: pointer;
  transition: 0.3s;
}

.user-profile-summary:hover {
  border-color: #3b82f6;
  background: #243147;
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.profile-name { font-weight: 700; font-size: 0.95rem; color: #f1f5f9; }
.profile-role { font-size: 0.75rem; color: #3b82f6; font-weight: 600; text-transform: uppercase; }

.profile-avatar {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white;
}

/* STATS */
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
.stat-card {
  background: #1e293b;
  padding: 1.5rem; border-radius: 20px;
  display: flex; align-items: center; gap: 1.5rem;
  border: 1px solid #334155;
  cursor: pointer; transition: 0.3s;
}
.stat-card:hover { transform: translateY(-3px); border-color: #3b82f6; }

.stat-icon-wrapper {
  width: 55px; height: 55px; border-radius: 15px;
  display: flex; align-items: center; justify-content: center;
}
.stat-icon-wrapper.blue { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.stat-icon-wrapper.purple { background: rgba(167, 139, 250, 0.1); color: #a78bfa; }

.stat-num { font-size: 1.8rem; font-weight: 800; display: block; }
.stat-label { font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase; }

/* ACTIONS GRID - CORREGIDA */
.actions-grid { 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 1.2rem; 
  margin-bottom: 3rem; 
}

.action-card {
  background: #1e293b;
  padding: 1.5rem; border-radius: 20px;
  display: flex; flex-direction: column; gap: 12px;
  border: 1px solid #334155; cursor: pointer; transition: 0.3s;
  position: relative;
}

.action-card:hover { 
  background: #243147; 
  border-color: #3b82f6; 
  transform: translateY(-5px);
}

.action-card.main-action { 
  background: linear-gradient(145deg, #1e3a8a, #1e293b); 
  border-color: #3b82f6;
}

.action-icon { color: #3b82f6; }
.action-text h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #f1f5f9; }
.action-text p { margin: 4px 0 0; color: #64748b; font-size: 0.8rem; }
.action-arrow { position: absolute; bottom: 1.2rem; right: 1.2rem; opacity: 0.3; font-size: 1.2rem; }

/* SECCIÓN TURNOS */
.appointments-section {
  background: #1e293b;
  border-radius: 24px;
  border: 1px solid #334155;
  padding: 2rem;
}

.section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 2rem;
}

.header-title { display: flex; align-items: center; gap: 10px; }
.icon-blue { color: #3b82f6; }

.btn-ver-todos {
  background: transparent; border: none; color: #3b82f6;
  font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 5px;
}

.appointments-list { display: flex; flex-direction: column; gap: 1rem; }

.appointment-item {
  display: flex; align-items: center;
  background: #0f172a;
  padding: 1.2rem; border-radius: 18px;
  border: 1px solid #334155;
  transition: 0.2s;
}

.appointment-item:hover { border-color: #3b82f6; }

.apt-date {
  background: #1e293b;
  min-width: 65px; padding: 10px;
  border-radius: 14px; text-align: center;
  margin-right: 1.5rem;
  border: 1px solid #334155;
}

.apt-date .day { display: block; font-size: 1.4rem; font-weight: 800; color: #3b82f6; }
.apt-date .month { font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; }

.apt-main-info { flex-grow: 1; }
.apt-services { font-weight: 700; font-size: 1.05rem; color: #f1f5f9; margin-bottom: 4px; }
.apt-meta { display: flex; gap: 15px; font-size: 0.85rem; color: #64748b; }
.apt-meta span { display: flex; align-items: center; gap: 5px; }

.apt-status-box { display: flex; align-items: center; gap: 15px; }

.status-badge {
  padding: 6px 12px; border-radius: 10px;
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
}
.status-reserved { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.status-confirmed { background: rgba(16, 185, 129, 0.1); color: #10b981; }

.btn-quick-action {
  background: #1e293b; border: none; color: #64748b;
  width: 35px; height: 35px; border-radius: 10px;
  cursor: pointer; transition: 0.2s;
}
.btn-quick-action:hover { color: #f1f5f9; background: #334155; }

/* EMPTY STATE */
.empty-state-modern {
  text-align: center; padding: 3rem 0;
}
.empty-icon-circle {
  width: 80px; height: 80px; background: #0f172a;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.5rem; color: #334155;
}
.empty-state-modern h4 { font-size: 1.25rem; margin: 0; }
.empty-state-modern p { color: #64748b; margin: 10px 0 1.5rem; }

.btn-schedule-first {
  background: #3b82f6; color: white; border: none;
  padding: 12px 24px; border-radius: 12px;
  font-weight: 700; cursor: pointer; transition: 0.3s;
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .stats-grid, .actions-grid { grid-template-columns: 1fr; }
  .welcome-header { flex-direction: column; align-items: flex-start; gap: 20px; }
  .user-profile-summary { align-self: flex-end; }
  .dashboard-cliente { padding: 1.5rem; }
}

/* MODO CLARO OVERRIDES */
html.light-theme .dashboard-cliente { background: #f8fafc; color: #0f172a; }
html.light-theme .stat-card,
html.light-theme .action-card,
html.light-theme .appointments-section,
html.light-theme .appointment-item,
html.light-theme .apt-date,
html.light-theme .user-profile-summary { 
  background: white; border-color: #e2e8f0; 
}
html.light-theme .appointment-item { background: #f1f5f9; }
html.light-theme .profile-name { color: #0f172a; }
html.light-theme .stat-num,
html.light-theme .action-text h3,
html.light-theme .apt-services { color: #0f172a; }
</style>