<template>
  <div class="dashboard-cliente">
    
    <div class="welcome-header">
      <div class="welcome-text">
        <h1>Hola, <span class="text-highlight">{{ cliente.nombre }}</span></h1>
        <p v-if="vistaActual === 'resumen'">Panel de control personal</p>
        <p v-else>Historial de Compras</p>
      </div>
    </div>

    <div v-if="vistaActual === 'resumen'" class="view-content fade-in">
      
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
            <span class="stat-num">{{ pedidos.length }}</span>
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

        <div class="action-card" @click="cambiarVista('pedidos')">
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

    <div v-if="vistaActual === 'pedidos'" class="view-content fade-in">
      <div class="pedidos-toolbar">
        <button class="btn-refresh" @click="cargarDatos">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>Actualizar Lista</span>
        </button>
        <button class="btn-primary-small" @click="irAProductos">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Nuevo Pedido</span>
        </button>
      </div>

      <div class="pedidos-list" v-if="pedidos.length > 0">
        <div v-for="pedido in pedidosPaginados" :key="pedido.id" class="pedido-card">
          <div class="pedido-header">
            <div class="pedido-meta">
              <span class="pedido-id">Pedido #{{ pedido.id }}</span>
              <span class="pedido-date">{{ formatearFecha(pedido.fecha_creacion) }}</span>
            </div>
            <span :class="['pedido-status', getEstadoPedidoClass(pedido.estado)]">
              {{ pedido.estado_display }}
            </span>
          </div>
          
          <div class="pedido-body">
            <div class="pedido-items">
              <div v-for="d in pedido.detalles" :key="d.id" class="pedido-item">
                <span class="item-qty">{{ d.cantidad }}x</span>
                <span class="item-name">{{ d.nombre_producto }}</span>
              </div>
            </div>
            <div class="pedido-delivery">
              <div class="delivery-badge">
                <span class="delivery-icon">{{ pedido.tipo_entrega === 'RETIRO' ? '🏪' : '🛵' }}</span>
                <span class="delivery-text">
                  {{ pedido.tipo_entrega === 'RETIRO' ? 'Retiro en Local' : 'Envío a Domicilio' }}
                </span>
              </div>
            </div>
          </div>

          <div class="pedido-footer">
            <div class="pedido-total">
              <span class="total-label">Total:</span>
              <span class="total-amount">${{ Number(pedido.total).toLocaleString() }}</span>
            </div>
            <button class="btn-detail" @click="verDetallePedido(pedido)">
              <span>Ver Detalle</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/services/api';
import Swal from 'sweetalert2';

const router = useRouter();
const route = useRoute();

const todosTurnos = ref([]);
const pedidos = ref([]);
const vistaActual = ref('resumen');
const cliente = ref({ nombre: localStorage.getItem('user_nombre') || 'Cliente' });

// ✅ FUNCIÓN QUE TRAE DATA REAL DEL SERVER PARA EVITAR EL "UNDEFINED"
const manejarExitoPago = async (tipo, id) => {
  if (tipo === 'pedido') {
    await Swal.fire('¡Compra Exitosa!', `Pedido #${id} procesado.`, 'success');
    vistaActual.value = 'pedidos';
  } else {
    try {
      // 1. Pedimos al server los datos reales del turno recién pagado
      const res = await api.get(`/turnos/${id}/`); 
      const t = res.data;

      // 2. Mostramos cartel con info real: fecha, hora, peluquero_nombre
      await Swal.fire({
        title: '¡Felicidades! 🎉',
        html: `
          <div style="text-align: left; background: #f0f9ff; padding: 1.2rem; border-radius: 12px; border: 1px solid #bae6fd;">
            <p style="margin-bottom: 10px; font-weight: 600;">Tu reserva ha sido confirmada con éxito.</p>
            <p>📅 <b>Día:</b> ${t.fecha}</p>
            <p>⏰ <b>Hora:</b> ${t.hora} hs</p>
            <p>💇‍♂️ <b>Profesional:</b> ${t.peluquero_nombre}</p>
            <p>💰 <b>Monto:</b> $${t.monto_seña || t.monto_total}</p>
          </div>`,
        icon: 'success',
        confirmButtonText: 'Genial',
        confirmButtonColor: '#0ea5e9'
      });
    } catch (e) {
      await Swal.fire('¡Felicidades!', 'Tu turno fue confirmado.', 'success');
    }
    vistaActual.value = 'resumen';
  }
  
  await cargarDatos();
  // Limpiamos parámetros de URL para no repetir el cartel
  router.replace({ query: { ver: vistaActual.value } });
};

const cargarDatos = async () => {
  try {
    const [resT, resP] = await Promise.all([api.get('/turnos/mis-turnos/'), api.get('/pedidos-web/')]);
    todosTurnos.value = resT.data;
    pedidos.value = Array.isArray(resP.data) ? resP.data : (resP.data.results || []);
  } catch (e) { console.error("Error cargando datos"); }
};

onMounted(async () => {
  // 🛡️ SEGURIDAD: SI NO HAY TOKEN, AL LOGIN (EVITA VISTA PÚBLICA)
  if (!localStorage.getItem('token')) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }

  await cargarDatos();

  // 🛍️ DETECCIÓN DE PAGO EXITOSO DESDE MERCADO PAGO
  const { pago_exitoso, pedido_id, turno_id } = route.query;
  if (pago_exitoso === 'true') {
    // Esperar un momento para que los datos se carguen
    setTimeout(async () => {
      if (pedido_id) await manejarExitoPago('pedido', pedido_id);
      else if (turno_id) await manejarExitoPago('turno', turno_id);
    }, 500);
  }
});

// Paginación y otros métodos... (Mantenelos igual)
const paginaActual = ref(1);
const turnosProximos = computed(() => todosTurnos.value.filter(t => t.estado !== 'CANCELADO'));
const pedidosPaginados = computed(() => pedidos.value.slice((paginaActual.value - 1) * 8, paginaActual.value * 8));
const cambiarVista = (v) => { vistaActual.value = v; router.push({ query: { ver: v } }); };
const irAPagina = (p) => paginaActual.value = p;
const irANuevoTurno = () => router.push({ name: 'RegistrarTurnoWeb' });
const irAProductos = () => router.push({ name: 'ProductosPublico' });
const irAPerfil = () => router.push({ name: 'PerfilCliente' });
const irAHistorial = () => router.push('/cliente/historial');
const formatearDia = (f) => f ? f.split('-')[2] : '-';
const formatearMes = (f) => f ? new Date(f).toLocaleDateString('es-ES', { month: 'short' }).toUpperCase() : '-';
const getNombreServicios = (s) => Array.isArray(s) ? s[0]?.nombre : s;
const getEstadoClass = (e) => e === 'CONFIRMADO' ? 'status-confirmed' : 'status-reserved';
const getEstadoPedidoClass = (e) => 'status-paid';
const verDetallePedido = (p) => Swal.fire(`Pedido #${p.id}`, `Total: $${p.total}`, 'info');
</script>

<style scoped>
/* ============================================
   VARIABLES Y BASE - MODO OSCURO
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
   MODO CLARO
   ============================================ */
:root.light-theme .dashboard-cliente {
  background: #f8fafc;
  color: #0f172a;
}

/* ============================================
   HEADER
   ============================================ */
.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  position: relative;
}

.welcome-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
}

:root.light-theme .welcome-header {
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

:root.light-theme .welcome-header::after {
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
}

.welcome-text h1 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #fff;
}

:root.light-theme .welcome-text h1 {
  color: #0f172a;
}

.text-highlight {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-text p {
  margin: 0.5rem 0 0 0;
  color: #94a3b8;
  font-size: 1rem;
  font-weight: 500;
}

:root.light-theme .welcome-text p {
  color: #64748b;
}

/* ============================================
   ESTADÍSTICAS
   ============================================ */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.stat-card {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 1.8rem;
  display: flex;
  align-items: center;
  gap: 1.2rem;
  border: 1px solid rgba(59, 130, 246, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

:root.light-theme .stat-card {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border: 1px solid rgba(203, 213, 225, 0.4);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

:root.light-theme .stat-card:hover {
  box-shadow: 0 8px 25px rgba(100, 116, 139, 0.2);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
}

.stat-icon-wrapper.blue {
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.stat-icon-wrapper.purple {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.stat-icon-wrapper::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 14px;
  background: inherit;
  z-index: -1;
  opacity: 0.3;
  filter: blur(8px);
}

.stat-svg {
  stroke: white;
  stroke-width: 2;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

.stat-num {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  letter-spacing: -1px;
}

:root.light-theme .stat-num {
  color: #0f172a;
}

.stat-label {
  font-size: 0.85rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

:root.light-theme .stat-label {
  color: #64748b;
}

/* ============================================
   ACCIONES RÁPIDAS
   ============================================ */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.action-card {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  padding: 2rem;
  border-radius: 16px;
  cursor: pointer;
  border: 1px solid rgba(59, 130, 246, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

:root.light-theme .action-card {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border: 1px solid rgba(203, 213, 225, 0.4);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-card:hover {
  transform: translateY(-8px);
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}

:root.light-theme .action-card:hover {
  box-shadow: 0 12px 30px rgba(100, 116, 139, 0.2);
}

.action-card:hover::before {
  opacity: 1;
}

.action-card.highlight {
  border: 1px solid rgba(59, 130, 246, 0.3);
  background: linear-gradient(145deg, rgba(59, 130, 246, 0.1), rgba(30, 41, 59, 0.8));
}

:root.light-theme .action-card.highlight {
  background: linear-gradient(145deg, rgba(59, 130, 246, 0.08), rgba(248, 250, 252, 0.95));
}

.action-icon {
  width: 60px;
  height: 60px;
  background: rgba(59, 130, 246, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.2rem;
}

:root.light-theme .action-icon {
  background: rgba(59, 130, 246, 0.1);
}

.action-icon svg {
  stroke: #60a5fa;
}

:root.light-theme .action-icon svg {
  stroke: #3b82f6;
}

.action-card h3 {
  margin: 0 0 8px 0;
  color: #fff;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.3px;
}

:root.light-theme .action-card h3 {
  color: #0f172a;
}

.action-card p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.5;
}

:root.light-theme .action-card p {
  color: #64748b;
}

.action-arrow {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  font-size: 1.5rem;
  color: #3b82f6;
  transition: transform 0.3s ease;
}

.action-card:hover .action-arrow {
  transform: translateX(5px);
}

/* ============================================
   SECCIÓN DE TURNOS
   ============================================ */
.section-box {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

:root.light-theme .section-box {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border: 1px solid rgba(203, 213, 225, 0.4);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

:root.light-theme .section-header {
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.section-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.3px;
}

:root.light-theme .section-header h3 {
  color: #0f172a;
}

.btn-link {
  background: transparent;
  border: none;
  color: #60a5fa;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  padding: 6px 12px;
  border-radius: 6px;
}

:root.light-theme .btn-link {
  color: #3b82f6;
}

.btn-link:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

:root.light-theme .btn-link:hover {
  background: rgba(59, 130, 246, 0.08);
}

.mini-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mini-item {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255,255,255,0.03);
  padding: 15px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.05);
  transition: all 0.2s ease;
}

:root.light-theme .mini-item {
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.05);
}

.mini-item:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateX(5px);
}

:root.light-theme .mini-item:hover {
  background: rgba(0,0,0,0.04);
}

.date-badge {
  text-align: center;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  padding: 10px 15px;
  border-radius: 12px;
  min-width: 70px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.date-badge .day {
  display: block;
  font-weight: 800;
  font-size: 1.5rem;
  line-height: 1;
  color: white;
}

.date-badge .month {
  display: block;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.8);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 4px;
}

.turno-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.turno-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.turno-hora {
  font-weight: 700;
  color: #60a5fa;
  font-size: 1rem;
}

:root.light-theme .turno-hora {
  color: #3b82f6;
}

.turno-servicio {
  font-weight: 600;
  color: #e2e8f0;
  font-size: 0.95rem;
}

:root.light-theme .turno-servicio {
  color: #1e293b;
}

.turno-estado {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  width: fit-content;
}

.status-reserved {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

:root.light-theme .status-reserved {
  background: rgba(251, 191, 36, 0.15);
  color: #d97706;
}

.status-confirmed {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

:root.light-theme .status-confirmed {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
}

.empty-message {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.empty-message svg {
  stroke: #475569;
  margin-bottom: 1rem;
}

:root.light-theme .empty-message svg {
  stroke: #94a3b8;
}

.empty-message p {
  margin: 0;
  font-size: 0.95rem;
}

/* ============================================
   PEDIDOS
   ============================================ */
.pedidos-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.btn-refresh {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: #94a3b8;
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

:root.light-theme .btn-refresh {
  border: 1px solid rgba(0,0,0,0.15);
  color: #64748b;
}

.btn-refresh:hover {
  background: rgba(31, 41, 55, 0.8);
  border-color: #3b82f6;
  color: #fff;
}

:root.light-theme .btn-refresh:hover {
  background: rgba(248, 250, 252, 0.95);
  color: #0f172a;
}

.btn-refresh svg {
  stroke: currentColor;
}

.btn-primary-small {
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  font-size: 0.9rem;
}

.btn-primary-small:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.btn-primary-small svg {
  stroke: currentColor;
}

.pedidos-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.pedido-card {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 1.8rem;
  border: 1px solid rgba(59, 130, 246, 0.1);
  transition: all 0.3s ease;
}

:root.light-theme .pedido-card {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border: 1px solid rgba(203, 213, 225, 0.4);
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.08);
}

.pedido-card:hover {
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

:root.light-theme .pedido-card:hover {
  box-shadow: 0 8px 25px rgba(100, 116, 139, 0.2);
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

:root.light-theme .pedido-header {
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.pedido-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pedido-id {
  color: #60a5fa;
  font-weight: 800;
  font-size: 1.05rem;
  letter-spacing: 0.3px;
}

:root.light-theme .pedido-id {
  color: #3b82f6;
}

.pedido-date {
  color: #94a3b8;
  font-size: 0.85rem;
}

:root.light-theme .pedido-date {
  color: #64748b;
}

.pedido-status {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-pending { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }
.status-paid { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.status-preparing { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.status-ready { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }
.status-shipping { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }
.status-delivered { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.status-cancelled { background: rgba(239, 68, 68, 0.2); color: #f87171; }

:root.light-theme .status-pending { background: rgba(148, 163, 184, 0.15); color: #64748b; }
:root.light-theme .status-paid { background: rgba(59, 130, 246, 0.15); color: #2563eb; }
:root.light-theme .status-preparing { background: rgba(251, 191, 36, 0.15); color: #d97706; }
:root.light-theme .status-ready { background: rgba(139, 92, 246, 0.15); color: #7c3aed; }
:root.light-theme .status-shipping { background: rgba(139, 92, 246, 0.15); color: #7c3aed; }
:root.light-theme .status-delivered { background: rgba(34, 197, 94, 0.15); color: #16a34a; }
:root.light-theme .status-cancelled { background: rgba(239, 68, 68, 0.15); color: #dc2626; }

.pedido-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.2rem;
}

.pedido-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.pedido-item {
  font-size: 0.95rem;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
}

:root.light-theme .pedido-item {
  color: #1e293b;
}

.item-qty {
  font-weight: 700;
  color: #60a5fa;
}

:root.light-theme .item-qty {
  color: #3b82f6;
}

.item-name {
  color: #cbd5e1;
}

:root.light-theme .item-name {
  color: #334155;
}

.pedido-delivery {
  flex-shrink: 0;
}

.delivery-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
  font-size: 0.85rem;
  color: #94a3b8;
  border: 1px solid rgba(255,255,255,0.05);
}

:root.light-theme .delivery-badge {
  background: rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.05);
  color: #64748b;
}

.delivery-icon {
  font-size: 1.2rem;
}

.pedido-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

:root.light-theme .pedido-footer {
  border-top: 1px solid rgba(0,0,0,0.05);
}

.pedido-total {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.total-label {
  font-size: 0.8rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

:root.light-theme .total-label {
  color: #64748b;
}

.total-amount {
  font-weight: 800;
  font-size: 1.4rem;
  color: #fff;
  letter-spacing: -0.5px;
}

:root.light-theme .total-amount {
  color: #0f172a;
}

.btn-detail {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: #e2e8f0;
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

:root.light-theme .btn-detail {
  border: 1px solid rgba(0,0,0,0.15);
  color: #1e293b;
}

.btn-detail:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: #3b82f6;
  color: #fff;
}

:root.light-theme .btn-detail:hover {
  background: rgba(59, 130, 246, 0.08);
  color: #0f172a;
}

.btn-detail svg {
  stroke: currentColor;
}

/* ============================================
   PAGINACIÓN
   ============================================ */
.pagination-container {
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
}

:root.light-theme .pagination-container {
  border-top: 1px solid rgba(203, 213, 225, 0.4);
}

.pagination-info {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

:root.light-theme .pagination-info {
  color: #64748b;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #cbd5e1;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

:root.light-theme .pagination-btn {
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #334155;
}

.pagination-btn:not(:disabled):hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #fff;
  transform: translateY(-2px);
}

:root.light-theme .pagination-btn:not(:disabled):hover {
  background: rgba(59, 130, 246, 0.08);
  color: #0f172a;
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-btn svg {
  stroke: currentColor;
  flex-shrink: 0;
}

.pagination-numbers {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-number {
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #cbd5e1;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

:root.light-theme .pagination-number {
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #334155;
}

.pagination-number:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  transform: translateY(-2px);
}

:root.light-theme .pagination-number:hover {
  background: rgba(59, 130, 246, 0.08);
  color: #3b82f6;
}

.pagination-number.active {
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.pagination-number.active::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 10px;
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
  z-index: -1;
  opacity: 0.3;
  filter: blur(4px);
}

.pagination-ellipsis {
  color: #64748b;
  font-weight: 700;
  padding: 0 8px;
  user-select: none;
}

/* ============================================
   ESTADO VACÍO
   ============================================ */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 16px;
  border: 1px dashed rgba(59, 130, 246, 0.2);
}

:root.light-theme .empty-state {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border: 1px dashed rgba(203, 213, 225, 0.4);
}

.empty-icon {
  margin-bottom: 1.5rem;
}

.empty-icon svg {
  stroke: #475569;
}

:root.light-theme .empty-icon svg {
  stroke: #94a3b8;
}

.empty-state h3 {
  margin: 0 0 0.8rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #e2e8f0;
}

:root.light-theme .empty-state h3 {
  color: #0f172a;
}

.empty-state p {
  margin: 0 0 2rem 0;
  color: #94a3b8;
  font-size: 1rem;
}

:root.light-theme .empty-state p {
  color: #64748b;
}

.btn-cta {
  padding: 12px 28px;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.btn-cta:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.btn-cta svg {
  stroke: currentColor;
}

/* ============================================
   ANIMACIONES
   ============================================ */
.fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-cliente {
    padding: 1.5rem;
  }

  .welcome-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .pedidos-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .btn-refresh,
  .btn-primary-small {
    width: 100%;
    justify-content: center;
  }

  .pedido-body {
    flex-direction: column;
    gap: 15px;
  }

  .pedido-footer {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .btn-detail {
    width: 100%;
    justify-content: center;
  }

  /* Paginación responsive */
  .pagination-controls {
    gap: 8px;
  }

  .pagination-btn span {
    display: none;
  }

  .pagination-btn {
    padding: 10px;
    min-width: 40px;
    justify-content: center;
  }

  .pagination-number {
    min-width: 36px;
    height: 36px;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .dashboard-cliente {
    padding: 1rem;
  }

  .welcome-text h1 {
    font-size: 1.8rem;
  }

  .section-box {
    padding: 1.5rem;
  }
}

/* ============================================
   SWEETALERT2 CUSTOM STYLES
   ============================================ */
:deep(.swal-popup-dark) {
  border: 1px solid rgba(59, 130, 246, 0.2) !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
}

:deep(.swal-popup-light) {
  border: 1px solid rgba(203, 213, 225, 0.4) !important;
  box-shadow: 0 20px 40px rgba(100, 116, 139, 0.2) !important;
}

:deep(.swal-title-dark) {
  color: #60a5fa !important;
  font-weight: 800 !important;
}

:deep(.swal-title-light) {
  color: #3b82f6 !important;
  font-weight: 800 !important;
}

:deep(.swal-button-dark) {
  background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
}

:deep(.swal-button-light) {
  background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2) !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
}

:deep(.swal-button-dark:hover),
:deep(.swal-button-light:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
}
</style>