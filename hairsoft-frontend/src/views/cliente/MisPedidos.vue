<template>
  <div class="mis-pedidos-container">
    
    <div class="header-section">
      <button @click="$router.push('/cliente/dashboard')" class="btn-volver">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Volver
      </button>
      <h1>Mis Pedidos</h1>
    </div>

    <div v-if="cargando" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando historial...</p>
    </div>

    <div v-else-if="pedidos.length === 0" class="empty-state">
      <div class="empty-icon">📦</div>
      <h3>Aún no realizaste compras</h3>
      <p>Visitá nuestra tienda para ver los productos disponibles.</p>
      <button @click="$router.push('/web/productos')" class="btn-cta">Ir a la Tienda</button>
    </div>

    <div v-else class="content-wrapper">
      <div class="pedidos-list">
        <div v-for="pedido in pedidosPaginados" :key="pedido.id" class="pedido-card">
          
          <div class="pedido-header">
            <div class="meta-info">
              <span class="pedido-id">#{{ pedido.id }}</span>
              <span class="pedido-fecha">{{ formatearFecha(pedido.fecha_creacion) }}</span>
            </div>
            <span :class="['estado-badge', getClaseEstado(pedido.estado)]">
              {{ pedido.estado_display || pedido.estado }}
            </span>
          </div>

          <div class="pedido-body">
            <div class="items-preview">
              <div v-for="(detalle, index) in pedido.detalles.slice(0, 2)" :key="index" class="item-row">
                <span class="qty">{{ detalle.cantidad }}x</span>
                <span class="name">{{ detalle.nombre_producto }}</span>
              </div>
              <div v-if="pedido.detalles.length > 2" class="more-items">
                +{{ pedido.detalles.length - 2 }} productos más...
              </div>
            </div>
            
            <div class="total-section">
              <small>Total</small>
              <span class="total-monto">{{ formatearDinero(pedido.total) }}</span>
            </div>
          </div>

          <div class="pedido-footer">
            <div class="entrega-info">
              <span v-if="pedido.tipo_entrega === 'ENVIO'">🛵 Envío a domicilio</span>
              <span v-else>🏪 Retiro en local</span>
            </div>
            <button class="btn-ver" @click="verDetalle(pedido)">Ver Detalle</button>
          </div>

        </div>
      </div>

      <div v-if="totalPaginas > 1" class="paginacion">
        <button 
          @click="cambiarPagina(paginaActual - 1)" 
          :disabled="paginaActual === 1"
          class="btn-pag"
        >
          Anterior
        </button>
        
        <span class="pag-info">Página {{ paginaActual }} de {{ totalPaginas }}</span>
        
        <button 
          @click="cambiarPagina(paginaActual + 1)" 
          :disabled="paginaActual === totalPaginas"
          class="btn-pag"
        >
          Siguiente
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import Swal from 'sweetalert2';

const router = useRouter();
const pedidos = ref([]);
const cargando = ref(true);
const paginaActual = ref(1);
const itemsPorPagina = 10;

onMounted(async () => {
  try {
    const res = await api.get('/pedidos-web/');
    pedidos.value = Array.isArray(res.data) ? res.data : (res.data.results || []);
  } catch (e) {
    console.error(e);
  } finally {
    cargando.value = false;
  }
});

// Lógica de Paginación
const totalPaginas = computed(() => Math.ceil(pedidos.value.length / itemsPorPagina));

const pedidosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina;
  const fin = inicio + itemsPorPagina;
  return pedidos.value.slice(inicio, fin);
});

const cambiarPagina = (nuevaPagina) => {
  if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas.value) {
    paginaActual.value = nuevaPagina;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

// Utilidades
const formatearFecha = (f) => {
  if (!f) return '-';
  const fecha = new Date(f);
  return fecha.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
};

const formatearDinero = (monto) => {
  return Number(monto).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' });
};

const getClaseEstado = (e) => {
  const map = {
    'PENDIENTE': 'bg-yellow', 'PAGADO': 'bg-blue',
    'CONFIRMADO': 'bg-purple', 'ENTREGADO': 'bg-green',
    'CANCELADO': 'bg-red'
  };
  return map[e] || 'bg-gray';
};

const verDetalle = (p) => {
  // Calculamos subtotal de items para mostrar desglose si hay envío
  const costoEnvio = Number(p.costo_envio || 0);
  const subtotalItems = p.detalles.reduce((acc, d) => acc + (d.cantidad * d.precio_unitario), 0);

  // Construimos filas de la tabla
  const itemsHtml = p.detalles.map(d => `
    <tr>
      <td style="text-align: left;">
        <div style="font-weight: 600; color: inherit;">${d.nombre_producto}</div>
      </td>
      <td style="text-align: center;">${d.cantidad}</td>
      <td style="text-align: right;">${formatearDinero(d.precio_unitario)}</td>
      <td style="text-align: right; font-weight: 600;">${formatearDinero(d.cantidad * d.precio_unitario)}</td>
    </tr>
  `).join('');

  // Info de entrega y pago
  const infoEntrega = p.tipo_entrega === 'ENVIO' ? '🛵 Envío a domicilio' : '🏪 Retiro en local';
  const infoPago = p.medio_pago ? p.medio_pago.replace('_', ' ') : 'Mercado Pago';

  Swal.fire({
    title: `<div class="swal-header-title">Pedido #${p.id}</div>`,
    html: `
      <div class="detalle-container">
        <div class="detalle-meta">
          <span>📅 ${formatearFecha(p.fecha_creacion)}</span>
          <span class="badge-mini ${getClaseEstado(p.estado)}">${p.estado}</span>
        </div>

        <div class="table-responsive">
          <table class="detalle-table">
            <thead>
              <tr>
                <th style="text-align: left;">Producto</th>
                <th style="text-align: center;">Cant.</th>
                <th style="text-align: right;">Unit.</th>
                <th style="text-align: right;">Subtotal</th>
              </tr>
            </thead>
            <tbody>${itemsHtml}</tbody>
          </table>
        </div>

        <div class="detalle-totales">
          <div class="row">
          </div>
          ${costoEnvio > 0 ? `
          <div class="row">
            <span>Envío:</span>
            <span>${formatearDinero(costoEnvio)}</span>
          </div>` : ''}
          <div class="row total-final">
            <span>TOTAL:</span>
            <span>${formatearDinero(p.total)}</span>
          </div>
        </div>
      </div>
    `,
    width: '600px',
    showCloseButton: true,
    showConfirmButton: false,
    background: document.documentElement.classList.contains('light-theme') ? '#ffffff' : '#1e293b',
    color: document.documentElement.classList.contains('light-theme') ? '#0f172a' : '#f8fafc',
    customClass: {
      popup: 'detalle-popup-custom'
    }
  });
};
</script>

<style>
/* ============================================
   ESTILOS BASE (MODO OSCURO - DEFAULT)
   ============================================ */
.mis-pedidos-container {
  min-height: 100vh;
  background-color: #0f172a;
  color: #f8fafc;
  padding: 2rem;
  font-family: 'Segoe UI', sans-serif;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.header-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.header-section h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #fff;
}

.btn-volver {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: 0.3s;
}

.btn-volver:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

/* CARDS PEDIDOS (DARK) */
.pedidos-list { display: grid; gap: 1.5rem; }

.pedido-card {
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.pedido-card:hover {
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

.pedido-header {
  display: flex; justify-content: space-between; margin-bottom: 1rem;
  padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.pedido-id { font-weight: 800; color: #60a5fa; margin-right: 10px; }
.pedido-fecha { color: #94a3b8; font-size: 0.9rem; }

.estado-badge {
  padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
}

/* Colores Badges */
.bg-yellow { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.bg-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.bg-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.bg-red { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.bg-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; }

.pedido-body {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;
}

.item-row { font-size: 0.95rem; margin-bottom: 4px; color: #e2e8f0; }
.qty { font-weight: 700; color: #94a3b8; margin-right: 8px; }
.more-items { font-size: 0.85rem; color: #64748b; font-style: italic; }

.total-section { text-align: right; }
.total-section small { display: block; color: #94a3b8; }
.total-monto { font-size: 1.4rem; font-weight: 800; color: #fff; }

.pedido-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.entrega-info { font-size: 0.9rem; color: #cbd5e1; }

.btn-ver {
  background: transparent; border: 1px solid #3b82f6; color: #60a5fa;
  padding: 6px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: 0.2s;
}
.btn-ver:hover { background: rgba(59, 130, 246, 0.1); }

/* PAGINACIÓN (DARK) */
.paginacion { display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 2rem; }
.btn-pag {
  background: #1e293b; color: #fff; border: 1px solid rgba(255,255,255,0.1);
  padding: 8px 16px; border-radius: 8px; cursor: pointer;
}
.btn-pag:disabled { opacity: 0.5; cursor: not-allowed; }
.pag-info { color: #94a3b8; }

/* LOADING & EMPTY (DARK) */
.loading-state, .empty-state { text-align: center; padding: 4rem; color: #94a3b8; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.btn-cta {
  margin-top: 1rem; background: #3b82f6; color: white; border: none;
  padding: 10px 20px; border-radius: 8px; cursor: pointer;
}

/* =========================================
   ESTILOS DEL MODAL DE DETALLE (SWEETALERT)
   ========================================= */
.swal-header-title {
  font-size: 1.5rem; font-weight: 800; text-align: left; padding-bottom: 10px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2); margin-bottom: 15px;
}
.detalle-meta {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; font-size: 0.9rem; color: #94a3b8;
}
.badge-mini {
  padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
}
.table-responsive { width: 100%; overflow-x: auto; margin-bottom: 20px; }
.detalle-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.detalle-table th {
  color: #64748b; text-transform: uppercase; font-size: 0.75rem;
  padding: 8px; border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}
.detalle-table td {
  padding: 12px 8px; border-bottom: 1px solid rgba(148, 163, 184, 0.1); color: inherit;
}
.detalle-totales {
  border-top: 2px dashed rgba(148, 163, 184, 0.3); padding-top: 15px;
  margin-left: auto; width: 100%; max-width: 250px;
}
.detalle-totales .row {
  display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.95rem; color: #94a3b8;
}
.detalle-totales .total-final {
  font-size: 1.2rem; font-weight: 800; color: #3b82f6; margin-top: 10px;
  padding-top: 10px; border-top: 1px solid rgba(148, 163, 184, 0.2);
}
.detalle-footer-info { display: flex; gap: 10px; margin-top: 25px; flex-wrap: wrap; }
.info-tag {
  background: rgba(59, 130, 246, 0.1); color: #60a5fa; padding: 6px 12px;
  border-radius: 6px; font-size: 0.85rem; font-weight: 600;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* ============================================
   MODO CLARO (OVERRIDES)
   ============================================ */
html.light-theme .mis-pedidos-container {
  background-color: #f8fafc;
  color: #0f172a;
}

html.light-theme .header-section h1 { color: #0f172a; }
html.light-theme .header-section { border-bottom-color: rgba(0,0,0,0.1); }

/* Botones Light */
html.light-theme .btn-volver { color: #64748b; border-color: rgba(0,0,0,0.1); }
html.light-theme .btn-volver:hover { background: rgba(0,0,0,0.05); color: #0f172a; }

/* Cards Light */
html.light-theme .pedido-card {
  background: #e6fffb;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
html.light-theme .pedido-card:hover { box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
html.light-theme .pedido-header,
html.light-theme .pedido-footer { border-color: #f1f5f9; }
html.light-theme .pedido-fecha { color: #64748b; }
html.light-theme .item-row { color: #334155; }
html.light-theme .qty { color: #64748b; }
html.light-theme .total-monto { color: #0f172a; }
html.light-theme .entrega-info { color: #475569; }

/* Botón Ver Detalle Light */
html.light-theme .btn-ver { color: #2563eb; border-color: #2563eb; }
html.light-theme .btn-ver:hover { background: rgba(37, 99, 235, 0.05); }

/* Paginación Light */
html.light-theme .btn-pag { background: #ffffff; color: #334155; border-color: #e2e8f0; }
html.light-theme .pag-info { color: #475569; }

html.light-theme .empty-state, 
html.light-theme .loading-state { color: #64748b; }

/* Badges Light */
html.light-theme .bg-yellow { color: #d97706; background: rgba(251, 191, 36, 0.2); }
html.light-theme .bg-blue { color: #2563eb; background: rgba(59, 130, 246, 0.2); }
html.light-theme .bg-green { color: #16a34a; background: rgba(34, 197, 94, 0.2); }
html.light-theme .bg-red { color: #dc2626; background: rgba(239, 68, 68, 0.2); }
html.light-theme .bg-purple { color: #9333ea; background: rgba(168, 85, 247, 0.2); }

/* AJUSTES MODO CLARO PARA EL MODAL */
html.light-theme .swal-header-title { color: #1e293b; }
html.light-theme .detalle-table th { color: #64748b; }
html.light-theme .detalle-totales .row { color: #64748b; }
html.light-theme .detalle-totales .total-final { color: #2563eb; }
html.light-theme .info-tag { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
</style>