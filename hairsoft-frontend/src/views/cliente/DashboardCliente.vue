<template>
  <div class="dashboard-cliente">
    
    <div class="welcome-header">
      <div class="welcome-text">
        <h1>Hola, <span class="text-highlight">{{ cliente.nombre }}</span></h1>
        <p>Panel de control personal</p>
      </div>
    </div>

    <div class="view-content fade-in">
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon-wrapper blue">
            <svg class="stat-svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ turnosProximos.length }}</span>
            <span class="stat-label">Turnos Próximos</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon-wrapper purple">
            <svg class="stat-svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ cantidadPedidos }}</span>
            <span class="stat-label">Pedidos Totales</span>
          </div>
        </div>
      </div>

      <div class="actions-grid">
        <div class="action-card" @click="irANuevoTurno">
          <div class="action-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <h3>Nuevo Turno</h3>
          <p>Agenda tu próxima visita</p>
          <span class="action-arrow">→</span>
        </div>
        
        <div class="action-card highlight" @click="irAProductos">
          <div class="action-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <circle cx="9" cy="21" r="1" stroke="currentColor" stroke-width="2"/>
              <circle cx="20" cy="21" r="1" stroke="currentColor" stroke-width="2"/>
              <path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>Ir a la Tienda</h3>
          <p>Comprar productos</p>
          <span class="action-arrow">→</span>
        </div>

        <div class="action-card" @click="irAMisPedidos">
          <div class="action-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4H6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3 6h18M16 10a4 4 0 01-8 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>Mis Pedidos</h3>
          <p>Ver historial de compras</p>
          <span class="action-arrow">→</span>
        </div>
        
        <div class="action-card" @click="irAPerfil">
          <div class="action-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <h3>Mis Datos</h3>
          <p>Gestionar perfil</p>
          <span class="action-arrow">→</span>
        </div>
      </div>

      <div class="section-box">
        <div class="section-header">
          <h3>Próximos Turnos</h3>
          <button class="btn-link" @click="irAHistorial">Ver todos →</button>
        </div>
        
        <div v-if="turnosProximos.length > 0" class="mini-list">
          <div v-for="t in turnosProximos.slice(0,3)" :key="t.id" class="mini-item">
            <div class="date-badge">
              <span class="day">{{ formatearDia(t.fecha) }}</span>
              <small class="month">{{ formatearMes(t.fecha) }}</small>
            </div>
            <div class="turno-info">
              <div class="turno-title">
                <span class="turno-hora">{{ t.hora }}hs</span>
                <span class="turno-servicio">{{ getNombreServicios(t.servicios) }}</span>
              </div>
              <span :class="['turno-estado', getEstadoClass(t.estado)]">
                {{ formatearEstado(t.estado) }}
              </span>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-message">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
            <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <p>No tienes turnos próximos</p>
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

const router = useRouter();
const route = useRoute();

const todosTurnos = ref([]);
const cantidadPedidos = ref(0);
const cliente = ref({ nombre: localStorage.getItem('user_nombre') || 'Cliente' });

// Manejo de pagos (Turnos y Pedidos)
const manejarExitoPago = async (tipo, id) => {
  if (tipo === 'pedido') {
    await Swal.fire('¡Compra Exitosa! 🛍️', `Tu pedido #${id} se procesó correctamente.`, 'success');
    router.push({ name: 'MisPedidos' });
  } else {
    try {
      const res = await api.get(`/api/turnos/${id}/`); 
      const t = res.data;
      await Swal.fire({
        title: '¡Felicidades! 🎉',
        html: `
          <div style="text-align: left; background: #f0f9ff; padding: 1.2rem; border-radius: 12px; border: 1px solid #bae6fd;">
            <p style="margin-bottom: 10px; font-weight: 600;">Tu reserva ha sido confirmada con éxito.</p>
            <p>📅 <b>Día:</b> ${t.fecha}</p>
            <p>⏰ <b>Hora:</b> ${t.hora} hs</p>
            <p>💇‍♂️ <b>Profesional:</b> ${t.peluquero_nombre}</p>
          </div>`,
        icon: 'success',
        confirmButtonText: 'Genial',
        confirmButtonColor: '#0ea5e9'
      });
    } catch (e) {
      await Swal.fire('¡Felicidades!', 'Tu turno fue confirmado.', 'success');
    }
  }
  router.replace({ query: {} });
  cargarDatos();
};

const cargarDatos = async () => {
  try {
    const [resT, resP] = await Promise.all([api.get('/turnos/mis-turnos/'), api.get('/pedidos-web/')]);
    todosTurnos.value = resT.data;
    const lista = Array.isArray(resP.data) ? resP.data : (resP.data.results || []);
    cantidadPedidos.value = lista.length;
  } catch (e) { console.error("Error cargando datos"); }
};

onMounted(async () => {
  if (!localStorage.getItem('token')) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }

  await cargarDatos();

  const { pago_exitoso, pedido_id, turno_id } = route.query;
  if (pago_exitoso === 'true') {
    setTimeout(async () => {
      if (pedido_id) await manejarExitoPago('pedido', pedido_id);
      else if (turno_id) await manejarExitoPago('turno', turno_id);
    }, 500);
  }
});

const turnosProximos = computed(() => todosTurnos.value.filter(t => t.estado !== 'CANCELADO'));

// NAVEGACIÓN
const irANuevoTurno = () => router.push({ name: 'RegistrarTurnoWeb' });
const irAProductos = () => router.push({ name: 'ProductosPublico' });
const irAPerfil = () => router.push({ name: 'PerfilCliente' });
const irAHistorial = () => router.push('/cliente/historial');
const irAMisPedidos = () => router.push({ name: 'MisPedidos' });

// FORMATOS
const formatearDia = (f) => f ? f.split('-')[2] : '-';
const formatearMes = (f) => f ? new Date(f).toLocaleDateString('es-ES', { month: 'short' }).toUpperCase() : '-';
const getNombreServicios = (s) => Array.isArray(s) ? s[0]?.nombre : s;
const getEstadoClass = (e) => e === 'CONFIRMADO' ? 'status-confirmed' : 'status-reserved';
const formatearEstado = (e) => e === 'CONFIRMADO' ? 'Confirmado' : 'Reservado';
</script>

<style>
/* ============================================
   VARIABLES Y BASE - MODO OSCURO (DEFAULT)
   ============================================ */
.dashboard-cliente {
  min-height: 100vh;
  background: #0f172a;
  color: #f8fafc;
  padding: 2.5rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* ============================================
   MODO CLARO (OVERRIDES)
   ============================================ */
/* Usamos html.light-theme para máxima especificidad */
html.light-theme .dashboard-cliente {
  background: #f8fafc !important;
  color: #0f172a !important;
}

html.light-theme .welcome-text h1 {
  color: #0f172a !important;
}

html.light-theme .welcome-text p {
  color: #64748b !important;
}

html.light-theme .welcome-header {
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

html.light-theme .welcome-header::after {
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
}

/* STAT CARDS CLARO */
html.light-theme .stat-card {
  background: linear-gradient(145deg, #d5eaf6, #f8fafc);
  border: 1px solid rgba(203, 213, 225, 0.4);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

html.light-theme .stat-card:hover {
  box-shadow: 0 8px 25px rgba(100, 116, 139, 0.2);
}

html.light-theme .stat-num {
  color: #0f172a;
}

html.light-theme .stat-label {
  color: #64748b;
}

/* ACTION CARDS CLARO */
html.light-theme .action-card {
  background: linear-gradient(145deg, #dcefff, #f8fafc);
  border: 1px solid rgba(203, 213, 225, 0.4);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

html.light-theme .action-card:hover {
  box-shadow: 0 12px 30px rgba(100, 116, 139, 0.2);
}

html.light-theme .action-card.highlight {
  background: linear-gradient(145deg, rgba(59, 130, 246, 0.08), rgba(248, 250, 252, 0.95));
}

html.light-theme .action-icon {
  background: rgba(59, 130, 246, 0.1);
}

html.light-theme .action-icon svg {
  stroke: #3b82f6;
}

html.light-theme .action-card h3 {
  color: #0f172a;
}

html.light-theme .action-card p {
  color: #64748b;
}

/* SECCIÓN CLARO */
html.light-theme .section-box {
  background: linear-gradient(145deg, #e5e5e5, #f8fafc);
  border: 1px solid rgba(203, 213, 225, 0.4);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

html.light-theme .section-header {
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

html.light-theme .section-header h3 {
  color: #0f172a;
}

html.light-theme .btn-link {
  color: #ffffff;
}

html.light-theme .btn-link:hover {
  background: rgba(59, 130, 246, 0.08);
}

html.light-theme .mini-item {
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.05);
}

html.light-theme .mini-item:hover {
  background: rgba(0,0,0,0.04);
}

html.light-theme .turno-hora {
  color: #3b82f6;
}

html.light-theme .turno-servicio {
  color: #1e293b;
}

html.light-theme .status-reserved {
  background: rgba(251, 191, 36, 0.15);
  color: #d97706;
}

html.light-theme .status-confirmed {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
}

html.light-theme .empty-message svg {
  stroke: #94a3b8;
}

html.light-theme .empty-message p {
  color: #64748b;
}

/* ============================================
   ESTILOS BASE (MODO OSCURO)
   ============================================ */
/* HEADER */
.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  position: relative;
}
.welcome-text h1 { margin: 0; font-size: 2.2rem; font-weight: 800; color: #fff; }
.text-highlight {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.welcome-text p { margin: 0.5rem 0 0 0; color: #94a3b8; }

/* STATS */
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 2.5rem; }
.stat-card {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 1.8rem;
  display: flex; align-items: center; gap: 1.2rem;
  border: 1px solid rgba(59, 130, 246, 0.1);
}
.stat-icon-wrapper { width: 60px; height: 60px; border-radius: 14px; display: flex; align-items: center; justify-content: center; }
.stat-icon-wrapper.blue { background: linear-gradient(135deg, #1e40af, #3b82f6); box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
.stat-icon-wrapper.purple { background: linear-gradient(135deg, #7c3aed, #a78bfa); box-shadow: 0 0 20px rgba(139, 92, 246, 0.3); }
.stat-svg { stroke: white; stroke-width: 2; }
.stat-info { display: flex; flex-direction: column; }
.stat-num { font-size: 2rem; font-weight: 800; color: #fff; }
.stat-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; }

/* ACTIONS */
.actions-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2.5rem; }
.action-card {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  padding: 2rem; border-radius: 16px; cursor: pointer;
  border: 1px solid rgba(59, 130, 246, 0.1); transition: 0.3s; position: relative;
}
.action-card:hover { transform: translateY(-8px); border-color: rgba(59, 130, 246, 0.4); box-shadow: 0 12px 30px rgba(0,0,0,0.4); }
.action-card.highlight { background: linear-gradient(145deg, rgba(59,130,246,0.1), rgba(30,41,59,0.8)); border-color: rgba(59,130,246,0.3); }
.action-icon { width: 60px; height: 60px; background: rgba(59,130,246,0.15); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.2rem; }
.action-icon svg { stroke: #60a5fa; }
.action-card h3 { margin: 0 0 8px; color: #fff; font-size: 1.15rem; font-weight: 700; }
.action-card p { margin: 0; color: #94a3b8; font-size: 0.9rem; }
.action-arrow { position: absolute; bottom: 1.5rem; right: 1.5rem; font-size: 1.5rem; color: #3b82f6; transition: 0.3s; }
.action-card:hover .action-arrow { transform: translateX(5px); }

/* SECCIÓN TURNOS */
.section-box { background: linear-gradient(145deg, #1e293b, #0f172a); border-radius: 16px; padding: 2rem; border: 1px solid rgba(59, 130, 246, 0.1); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 1rem; }
.section-header h3 { margin: 0; font-size: 1.3rem; font-weight: 700; color: #fff; }
.btn-link { background: transparent; border: none; color: #60a5fa; font-weight: 600; cursor: pointer; }
.mini-list { display: flex; flex-direction: column; gap: 12px; }
.mini-item { display: flex; align-items: center; gap: 15px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
.date-badge { text-align: center; background: linear-gradient(135deg, #1e40af, #3b82f6); padding: 10px 15px; border-radius: 12px; min-width: 70px; }
.date-badge .day { display: block; font-weight: 800; font-size: 1.5rem; line-height: 1; color: white; }
.date-badge .month { font-size: 0.75rem; color: rgba(255,255,255,0.8); text-transform: uppercase; }
.turno-info { display: flex; flex-direction: column; gap: 6px; }
.turno-hora { font-weight: 700; color: #60a5fa; font-size: 1rem; margin-right: 10px; }
.turno-servicio { font-weight: 600; color: #e2e8f0; }
.turno-estado { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; width: fit-content; }
.status-reserved { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.status-confirmed { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.empty-message { text-align: center; padding: 3rem; color: #64748b; }
.empty-message svg { stroke: #475569; margin-bottom: 1rem; }

/* ANIMACIONES */
.fade-in { animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* RESPONSIVE */
@media (max-width: 768px) {
  .stats-grid, .actions-grid { grid-template-columns: 1fr; }
  .dashboard-cliente { padding: 1.5rem; }
}
</style>