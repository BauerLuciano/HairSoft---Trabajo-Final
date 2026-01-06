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
      
      <!-- ESTADÍSTICAS -->
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

      <!-- ACCIONES RÁPIDAS -->
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

      <!-- PRÓXIMOS TURNOS -->
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

      <!-- PAGINACIÓN -->
      <div v-if="pedidos.length > 0 && totalPaginas > 1" class="pagination-container">
        <div class="pagination-info">
          Mostrando {{ (paginaActual - 1) * pedidosPorPagina + 1 }} - 
          {{ Math.min(paginaActual * pedidosPorPagina, pedidos.length) }} 
          de {{ pedidos.length }} pedidos
        </div>
        
        <div class="pagination-controls">
          <button 
            @click="paginaAnterior" 
            :disabled="paginaActual === 1"
            class="pagination-btn prev"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <polyline points="15 18 9 12 15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Anterior</span>
          </button>
          
          <div class="pagination-numbers">
            <button 
              v-if="paginasVisibles[0] > 1"
              @click="irAPagina(1)"
              class="pagination-number"
            >
              1
            </button>
            
            <span v-if="paginasVisibles[0] > 2" class="pagination-ellipsis">...</span>
            
            <button 
              v-for="pagina in paginasVisibles" 
              :key="pagina"
              @click="irAPagina(pagina)"
              :class="['pagination-number', { active: pagina === paginaActual }]"
            >
              {{ pagina }}
            </button>
            
            <span v-if="paginasVisibles[paginasVisibles.length - 1] < totalPaginas - 1" class="pagination-ellipsis">...</span>
            
            <button 
              v-if="paginasVisibles[paginasVisibles.length - 1] < totalPaginas"
              @click="irAPagina(totalPaginas)"
              class="pagination-number"
            >
              {{ totalPaginas }}
            </button>
          </div>
          
          <button 
            @click="paginaSiguiente" 
            :disabled="paginaActual === totalPaginas"
            class="pagination-btn next"
          >
            <span>Siguiente</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="empty-state" v-else-if="pedidos.length === 0">
        <div class="empty-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
            <path d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>Aún no tienes pedidos</h3>
        <p>Visita nuestra tienda para realizar tu primera compra.</p>
        <button class="btn-cta" @click="irAProductos">
          <span>Ir al Catálogo</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
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

const cliente = ref({});
const todosTurnos = ref([]);
const pedidos = ref([]);
const cargando = ref(false);
const vistaActual = ref('resumen');

// Paginación
const paginaActual = ref(1);
const pedidosPorPagina = 8;

// --- WATCHERS ---
watch(() => route.query.ver, (val) => {
  vistaActual.value = val === 'pedidos' ? 'pedidos' : 'resumen';
}, { immediate: true });

// --- COMPUTED ---
const turnosProximos = computed(() => {
  const ahora = new Date();
  return todosTurnos.value.filter(t => {
    if(!t.fecha) return false;
    const f = new Date(t.fecha + 'T' + t.hora);
    return f >= ahora && t.estado !== 'CANCELADO' && t.estado !== 'COMPLETADO';
  }).sort((a,b) => new Date(a.fecha) - new Date(b.fecha));
});

// Paginación de pedidos
const totalPaginas = computed(() => Math.ceil(pedidos.value.length / pedidosPorPagina));

const pedidosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * pedidosPorPagina;
  const fin = inicio + pedidosPorPagina;
  return pedidos.value.slice(inicio, fin);
});

const paginasVisibles = computed(() => {
  const paginas = [];
  const maxVisible = 5;
  let inicio = Math.max(1, paginaActual.value - Math.floor(maxVisible / 2));
  let fin = Math.min(totalPaginas.value, inicio + maxVisible - 1);
  
  if (fin - inicio < maxVisible - 1) {
    inicio = Math.max(1, fin - maxVisible + 1);
  }
  
  for (let i = inicio; i <= fin; i++) {
    paginas.push(i);
  }
  
  return paginas;
});

// --- HELPERS ---
const formatearDia = (f) => f ? new Date(f).getDate() : '-';
const formatearMes = (f) => f ? new Date(f).toLocaleDateString('es-ES', { month: 'short' }).toUpperCase() : '-';
const formatearFecha = (f) => new Date(f).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric', hour:'2-digit', minute:'2-digit' });
const formatearEstado = (e) => ({ 'RESERVADO': 'Reservado', 'CONFIRMADO': 'Confirmado' }[e] || e);
const getNombreServicios = (s) => Array.isArray(s) ? (s[0]?.nombre || 'Servicio') + (s.length > 1 ? '...' : '') : s;

const getEstadoClass = (estado) => {
  const mapa = {
    'RESERVADO': 'status-reserved',
    'CONFIRMADO': 'status-confirmed'
  };
  return mapa[estado] || 'status-default';
};

const getEstadoPedidoClass = (estado) => {
  const mapa = {
    'PENDIENTE_PAGO': 'status-pending',
    'PAGADO': 'status-paid',
    'EN_PREPARACION': 'status-preparing',
    'LISTO_RETIRO': 'status-ready',
    'EN_CAMINO': 'status-shipping',
    'ENTREGADO': 'status-delivered',
    'CANCELADO': 'status-cancelled'
  };
  return mapa[estado] || 'status-default';
};

// --- ACTIONS ---
const cambiarVista = (vista) => {
  router.push({ query: { ...route.query, ver: vista } });
  vistaActual.value = vista;
  // Resetear paginación al cambiar a vista de pedidos
  if (vista === 'pedidos') {
    paginaActual.value = 1;
  }
};

const cargarDatos = async () => {
  cargando.value = true;
  try {
    cliente.value = { nombre: localStorage.getItem('user_nombre') || 'Cliente' };
    const resTurnos = await api.get('/turnos/mis-turnos/');
    if (Array.isArray(resTurnos.data)) todosTurnos.value = resTurnos.data;
    const resPedidos = await api.get('/pedidos-web/');
    pedidos.value = Array.isArray(resPedidos.data) ? resPedidos.data : (resPedidos.data.results || []);
  } catch (e) {
    console.error(e);
  } finally {
    cargando.value = false;
  }
};

const irANuevoTurno = () => router.push({ name: 'RegistrarTurnoWeb' });
const irAProductos = () => router.push({ name: 'ProductosPublico' });
const irAPerfil = () => router.push({ name: 'PerfilCliente' });
const irAHistorial = () => router.push('/cliente/historial');

// Funciones de paginación
const irAPagina = (pagina) => {
  if (pagina >= 1 && pagina <= totalPaginas.value) {
    paginaActual.value = pagina;
    // Scroll suave al inicio de la lista
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const paginaAnterior = () => {
  if (paginaActual.value > 1) {
    irAPagina(paginaActual.value - 1);
  }
};

const paginaSiguiente = () => {
  if (paginaActual.value < totalPaginas.value) {
    irAPagina(paginaActual.value + 1);
  }
};

const verDetallePedido = (pedido) => {
  // Construir HTML para mejor presentación
  let itemsHTML = pedido.detalles.map(d => 
    `<div style="text-align: left; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">
      <strong style="color: #60a5fa;">${d.cantidad}x</strong> ${d.nombre_producto}
    </div>`
  ).join('');

  Swal.fire({
    title: `Pedido #${pedido.id}`,
    html: `
      <div style="text-align: left; margin-top: 1rem;">
        <div style="margin-bottom: 1rem; padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
          <small style="color: #94a3b8;">Fecha</small><br>
          <strong style="color: #e2e8f0;">${formatearFecha(pedido.fecha_creacion)}</strong>
        </div>
        
        <div style="margin-bottom: 1rem;">
          <h4 style="color: #60a5fa; margin-bottom: 0.5rem;">Items del Pedido:</h4>
          ${itemsHTML}
        </div>

        <div style="display: flex; justify-content: space-between; padding: 15px; background: rgba(59, 130, 246, 0.1); border-radius: 8px; margin-top: 1rem;">
          <div>
            <small style="color: #94a3b8;">Tipo de Entrega</small><br>
            <strong style="color: #e2e8f0;">${pedido.tipo_entrega === 'RETIRO' ? '🏪 Retiro en Local' : '🛵 Envío a Domicilio'}</strong>
          </div>
          <div style="text-align: right;">
            <small style="color: #94a3b8;">Total</small><br>
            <strong style="color: #22c55e; font-size: 1.3rem;">$${Number(pedido.total).toLocaleString()}</strong>
          </div>
        </div>
      </div>
    `,
    icon: 'info',
    confirmButtonText: 'Cerrar',
    confirmButtonColor: '#3b82f6',
    background: '#1e293b',
    color: '#f8fafc',
    customClass: {
      popup: 'swal-popup-dark',
      title: 'swal-title-dark',
      confirmButton: 'swal-button-dark'
    }
  });
};

onMounted(cargarDatos);
</script>

<style scoped>
/* ============================================
   VARIABLES Y BASE
   ============================================ */
.dashboard-cliente {
  min-height: 100vh;
  background: #0f172a;
  color: #f8fafc;
  padding: 2.5rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
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

.welcome-text h1 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #fff;
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

.stat-label {
  font-size: 0.85rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
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

.action-card:hover::before {
  opacity: 1;
}

.action-card.highlight {
  border: 1px solid rgba(59, 130, 246, 0.3);
  background: linear-gradient(145deg, rgba(59, 130, 246, 0.1), rgba(30, 41, 59, 0.8));
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

.action-icon svg {
  stroke: #60a5fa;
}

.action-card h3 {
  margin: 0 0 8px 0;
  color: #fff;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.action-card p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.5;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.section-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.3px;
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

.btn-link:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
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

.mini-item:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateX(5px);
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

.turno-servicio {
  font-weight: 600;
  color: #e2e8f0;
  font-size: 0.95rem;
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

.status-confirmed {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
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

.btn-refresh:hover {
  background: rgba(31, 41, 55, 0.8);
  border-color: #3b82f6;
  color: #fff;
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

.pedido-card:hover {
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
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

.pedido-date {
  color: #94a3b8;
  font-size: 0.85rem;
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

.item-qty {
  font-weight: 700;
  color: #60a5fa;
}

.item-name {
  color: #cbd5e1;
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

.total-amount {
  font-weight: 800;
  font-size: 1.4rem;
  color: #fff;
  letter-spacing: -0.5px;
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

.btn-detail:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: #3b82f6;
  color: #fff;
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

.pagination-info {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
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

.pagination-btn:not(:disabled):hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #fff;
  transform: translateY(-2px);
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

.pagination-number:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  transform: translateY(-2px);
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

.empty-icon {
  margin-bottom: 1.5rem;
}

.empty-icon svg {
  stroke: #475569;
}

.empty-state h3 {
  margin: 0 0 0.8rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #e2e8f0;
}

.empty-state p {
  margin: 0 0 2rem 0;
  color: #94a3b8;
  font-size: 1rem;
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

:deep(.swal-title-dark) {
  color: #60a5fa !important;
  font-weight: 800 !important;
}

:deep(.swal-button-dark) {
  background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
}

:deep(.swal-button-dark:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
}
</style>