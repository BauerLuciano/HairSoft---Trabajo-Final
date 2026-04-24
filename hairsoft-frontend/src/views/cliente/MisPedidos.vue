<template>
  <div class="mis-pedidos-container">
    
    <div class="header-section">
      <div class="header-titles">
        <button @click="$router.push('/cliente/dashboard')" class="btn-volver">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        <div>
          <h1>Mis Pedidos</h1>
          <p class="subtitle">Historial de compras y seguimientos</p>
        </div>
      </div>
    </div>

    <div v-if="cargando" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando tu historial...</p>
    </div>

    <div v-else-if="pedidos.length === 0" class="empty-state">
      <div class="empty-icon-container">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
      </div>
      <h3>Aún no realizaste compras</h3>
      <p>Visitá nuestra tienda para ver los increíbles productos que tenemos para vos.</p>
      <button @click="$router.push('/web/productos')" class="btn-cta">Ir a la Tienda</button>
    </div>

    <div v-else class="content-wrapper">
      <div class="pedidos-list">
        <div v-for="pedido in pedidosPaginados" :key="pedido.id" class="pedido-card">
          
          <div class="pedido-header">
            <div class="meta-info">
              <div class="icon-box">📦</div>
              <div>
                <span class="pedido-id">Pedido #{{ pedido.id }}</span>
                <span class="pedido-fecha">{{ formatearFecha(pedido.fecha_creacion) }}</span>
              </div>
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
              <small>Total pagado</small>
              <span class="total-monto">{{ formatearDinero(pedido.total) }}</span>
            </div>
          </div>

          <div class="pedido-footer">
            <div class="entrega-info">
              <svg v-if="pedido.tipo_entrega === 'ENVIO' || pedido.tipo_entrega === 'MOTO' || pedido.tipo_entrega === 'CORREO'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
              <span>{{ pedido.tipo_entrega === 'RETIRO' ? 'Retiro en local' : 'Envío a domicilio' }}</span>
            </div>
            
            <div class="action-buttons-group">
              <button 
                v-if="puedeSolicitarCancelacion(pedido.estado)" 
                class="btn-cancelar" 
                @click="solicitarCancelacion(pedido)"
                title="Solicitar cancelación de esta compra">
                Cancelar
              </button>
              <button class="btn-ver" @click="verDetalle(pedido)">
                <span>Ver Detalle</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </button>
            </div>
          </div>

        </div>
      </div>

      <div v-if="totalPaginas > 1" class="paginacion">
        <button @click="cambiarPagina(paginaActual - 1)" :disabled="paginaActual === 1" class="btn-pag">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
          Anterior
        </button>
        
        <span class="pag-info">Página <strong>{{ paginaActual }}</strong> de {{ totalPaginas }}</span>
        
        <button @click="cambiarPagina(paginaActual + 1)" :disabled="paginaActual === totalPaginas" class="btn-pag">
          Siguiente
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </button>
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
const pedidos = ref([]);
const cargando = ref(true);
const paginaActual = ref(1);
const itemsPorPagina = 8;

const descargarComprobantePedidoWeb = async (pedidoId) => {
  try {
    Swal.fire({
      title: 'Generando comprobante...',
      text: 'Por favor espera un momento.',
      allowOutsideClick: false,
      didOpen: () => { Swal.showLoading() }
    });

    const response = await api.get(`/web/pedidos/${pedidoId}/comprobante-pdf/`, {
      responseType: 'blob' 
    });
    
    const fileURL = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const fileLink = document.createElement('a');
    fileLink.href = fileURL;
    fileLink.setAttribute('download', `Comprobante_Compra_${pedidoId}.pdf`);
    document.body.appendChild(fileLink);
    fileLink.click();
    
    fileLink.remove();
    window.URL.revokeObjectURL(fileURL);
    Swal.close();
  } catch (error) {
    console.error("Error PDF:", error);
    Swal.fire('Error', 'No se pudo descargar el PDF.', 'error');
  }
};

onMounted(async () => {
  await cargarPedidos();

  if (route.query.pago_exitoso === 'true' && route.query.pedido_id) {
    const pId = route.query.pedido_id;
    
    const result = await Swal.fire({
      title: '¡Compra Exitosa! 🎉',
      text: 'Tu pedido ha sido registrado y pagado correctamente.',
      icon: 'success',
      showCancelButton: true,
      confirmButtonColor: '#10b981',
      cancelButtonColor: '#64748b',
      confirmButtonText: '📄 Descargar Comprobante',
      cancelButtonText: 'Cerrar'
    });

    if (result.isConfirmed) {
      await descargarComprobantePedidoWeb(pId);
    }
    
    router.replace({ query: {} });
  }
});

const cargarPedidos = async () => {
  cargando.value = true;
  try {
    const res = await api.get('/web/pedidos/'); 
    pedidos.value = Array.isArray(res.data) ? res.data : (res.data.results || []);
  } catch (e) {
    console.error("❌ Error cargando pedidos:", e);
    Swal.fire({ title: 'Error', text: 'No se pudieron cargar tus pedidos.', icon: 'error' });
  } finally {
    cargando.value = false;
  }
};

// LOGICA DE CANCELACIÓN
const puedeSolicitarCancelacion = (estado) => {
  return ['PENDIENTE_PAGO', 'PAGADO', 'EN_PREPARACION'].includes(estado);
};

const solicitarCancelacion = async (pedido) => {
  const { value: motivo } = await Swal.fire({
    title: 'Solicitar Cancelación',
    text: 'Contanos brevemente por qué querés cancelar la compra:',
    input: 'text',
    inputPlaceholder: 'Ej: Me equivoqué de producto...',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#64748b',
    confirmButtonText: 'Enviar Solicitud',
    cancelButtonText: 'Cerrar',
    background: document.documentElement.classList.contains('light-theme') ? '#fff' : '#1e293b',
    color: document.documentElement.classList.contains('light-theme') ? '#0f172a' : '#fff',
    inputValidator: (value) => {
      if (!value) return 'Por favor, dejanos un motivo para procesar tu solicitud.';
    }
  });

  if (motivo) {
    try {
      Swal.fire({ title: 'Enviando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
      await api.post(`/web/pedidos/${pedido.id}/solicitar_cancelacion/`, { motivo: motivo });
      Swal.fire('¡Enviado!', 'Tu solicitud fue enviada. Te notificaremos pronto.', 'success');
      await cargarPedidos(); 
    } catch (error) {
      console.error(error);
      Swal.fire('Error', 'No se pudo enviar la solicitud.', 'error');
    }
  }
};

// Paginación
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

const formatearFecha = (f) => {
  if (!f) return '-';
  const fecha = new Date(f);
  return fecha.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const formatearDinero = (monto) => {
  return Number(monto).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' });
};

const getClaseEstado = (e) => {
  const map = {
    'PENDIENTE_PAGO': 'bg-yellow',
    'PAGADO': 'bg-blue',
    'EN_PREPARACION': 'bg-purple', 
    'LISTO_RETIRO': 'bg-teal',
    'EN_CAMINO': 'bg-teal',
    'ENTREGADO': 'bg-green',
    'CANCELADO': 'bg-red',
    'SOLICITA_CANCELACION': 'bg-orange'
  };
  return map[e] || 'bg-gray';
};

// 💎 DETALLE MEJORADO (RECIBO DIGITAL)
const verDetalle = async (p) => {
  const itemsHtml = p.detalles.map(d => `
    <div class="receipt-item">
      <div class="item-info">
        <span class="item-qty">${d.cantidad}x</span>
        <span class="item-name">${d.nombre_producto || 'Producto'}</span>
      </div>
      <span class="item-subtotal">${formatearDinero(d.cantidad * d.precio_unitario)}</span>
    </div>
  `).join('');

  // Lógica para mostrar la transacción de Mercado Pago
  const mpHTML = p.mp_payment_id ? `
    <div class="receipt-mp-box">
      <div class="mp-logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>
      </div>
      <div class="mp-info">
        <span class="mp-title">Abonado vía Mercado Pago</span>
        <span class="mp-id">Ref: ${p.mp_payment_id}</span>
      </div>
    </div>
  ` : '';

  // Alerta si el pedido está cancelado o solicitando cancelación
  const isCanceledOrRequested = p.estado === 'CANCELADO' || p.estado === 'SOLICITA_CANCELACION';
  const cancelHTML = isCanceledOrRequested ? `
    <div class="receipt-alert">
      <div class="alert-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        ${p.estado === 'CANCELADO' ? 'Pedido Anulado' : 'Cancelación en Revisión'}
      </div>
      <div class="alert-msg"><strong>Motivo:</strong> ${p.motivo_cancelacion || 'Solicitud de cliente'}</div>
      <div class="alert-obs">${p.obs_cancelacion ? `"${p.obs_cancelacion}"` : ''}</div>
    </div>
  ` : '';

  const result = await Swal.fire({
    html: `
      <div class="receipt-wrapper">
        <div class="receipt-header">
          <div class="receipt-icon">🛍️</div>
          <h2>Pedido #${p.id}</h2>
          <p class="receipt-date">${formatearFecha(p.fecha_creacion)}</p>
          <span class="estado-badge ${getClaseEstado(p.estado)}">${p.estado_display || p.estado}</span>
        </div>

        ${cancelHTML}

        <div class="receipt-section">
          <h3 class="section-title">Detalle de Productos</h3>
          <div class="items-list">
            ${itemsHtml}
          </div>
        </div>

        <div class="receipt-section">
          <h3 class="section-title">Logística</h3>
          <div class="logistics-info">
            <p><strong>Entrega:</strong> ${p.tipo_entrega}</p>
            ${p.direccion_envio ? `<p><strong>Destino:</strong> ${p.direccion_envio}</p>` : ''}
            ${p.datos_entrega_interna ? `<p><strong>Repartidor:</strong> ${p.datos_entrega_interna}</p>` : ''}
          </div>
        </div>

        ${mpHTML}

        <div class="receipt-totals">
          ${Number(p.costo_envio) > 0 ? `
          <div class="totals-row">
            <span>Costo de Envío</span>
            <span>${formatearDinero(p.costo_envio)}</span>
          </div>` : ''}
          <div class="totals-row grand-total">
            <span>TOTAL</span>
            <span>${formatearDinero(p.total)}</span>
          </div>
        </div>
      </div>
    `,
    showCloseButton: true,
    showCancelButton: true,
    showConfirmButton: true,
    confirmButtonText: '📄 Descargar PDF',
    cancelButtonText: 'Cerrar',

    // 🔥 ACÁ ESTÁ LA MAGIA PARA SACAR EL MARCO BLANCO
    background: document.documentElement.classList.contains('light-theme') ? '#ffffff' : '#1e293b',
    color: document.documentElement.classList.contains('light-theme') ? '#0f172a' : '#f8fafc',
    
    customClass: {
      popup: 'swal-receipt-popup',
      confirmButton: 'swal-btn-confirm',
      cancelButton: 'swal-btn-cancel'
    }
  });

  if (result.isConfirmed) {
    await descargarComprobantePedidoWeb(p.id);
  }
};
</script>

<style>
/* ============================================
   ESTILOS GENERALES Y LAYOUT
   ============================================ */
.mis-pedidos-container {
  min-height: 100vh;
  background-color: #0f172a;
  color: #f8fafc;
  padding: 2rem;
  font-family: 'Inter', system-ui, sans-serif;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.header-section {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.header-titles {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.header-titles h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 4px 0 0 0;
  color: #94a3b8;
  font-size: 0.95rem;
}

.btn-volver {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f8fafc;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-volver:hover {
  background: #3b82f6;
  border-color: #3b82f6;
  transform: translateY(-2px);
}

/* ============================================
   TARJETAS DE PEDIDOS (MODERNAS)
   ============================================ */
.pedidos-list { 
  display: grid; 
  gap: 1.5rem; 
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
}

.pedido-card {
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
  position: relative;
  overflow: hidden;
}

.pedido-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.pedido-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
}

.pedido-card:hover::before {
  opacity: 1;
}

.pedido-header {
  display: flex; 
  justify-content: space-between; 
  align-items: flex-start;
  margin-bottom: 1.2rem;
  padding-bottom: 1.2rem; 
  border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-box {
  background: rgba(59, 130, 246, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.pedido-id { 
  display: block;
  font-weight: 800; 
  color: #f8fafc; 
  font-size: 1.1rem;
}

.pedido-fecha { 
  display: block;
  color: #94a3b8; 
  font-size: 0.85rem; 
  margin-top: 2px;
}

/* BADGES DE ESTADO (MÁS VIVOS) */
.estado-badge {
  padding: 6px 12px; 
  border-radius: 8px; 
  font-size: 0.75rem; 
  font-weight: 800; 
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.bg-yellow { background: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.3); }
.bg-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
.bg-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
.bg-teal { background: rgba(20, 184, 166, 0.15); color: #2dd4bf; border: 1px solid rgba(20, 184, 166, 0.3); }
.bg-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
.bg-red { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
.bg-orange { background: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); }
.bg-gray { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3); }

/* CUERPO DE LA TARJETA */
.pedido-body {
  flex-grow: 1;
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 1.5rem;
}

.item-row { 
  font-size: 0.95rem; 
  margin-bottom: 6px; 
  color: #e2e8f0; 
  display: flex;
  gap: 8px;
}
.qty { font-weight: 800; color: #3b82f6; }
.more-items { font-size: 0.85rem; color: #64748b; font-style: italic; margin-top: 8px; }

.total-section { text-align: right; }
.total-section small { display: block; color: #94a3b8; font-weight: 500; text-transform: uppercase; font-size: 0.7rem;}
.total-monto { font-size: 1.5rem; font-weight: 900; color: #10b981; letter-spacing: -0.5px;}

/* FOOTER DE LA TARJETA */
.pedido-footer {
  display: flex; 
  justify-content: space-between; 
  align-items: center;
  padding-top: 1.2rem; 
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.entrega-info { 
  font-size: 0.85rem; 
  color: #cbd5e1; 
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-buttons-group {
  display: flex;
  gap: 8px;
}

.btn-ver {
  background: #3b82f6; 
  border: none; 
  color: #fff;
  padding: 8px 16px; 
  border-radius: 10px; 
  cursor: pointer; 
  font-weight: 600; 
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-ver:hover { background: #2563eb; transform: scale(1.02); }

.btn-cancelar {
  background: transparent;
  border: 1px solid #ef4444;
  color: #f87171;
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}
.btn-cancelar:hover { background: rgba(239, 68, 68, 0.1); }

/* ============================================
   MODAL SWEETALERT: TICKET PREMIUM
   ============================================ */
.swal-receipt-popup {
  padding: 0 !important;
  border-radius: 24px !important;
  overflow: hidden;
}

.receipt-wrapper {
  background: transparent; /* 🔥 CORREGIDO: Esto saca el marco de fondo */
  color: inherit; /* 🔥 CORREGIDO: Hereda el color que le da Swal */
  text-align: left;
  font-family: 'Inter', sans-serif;
}

.receipt-header {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.5));
  padding: 30px 20px;
  text-align: center;
  border-bottom: 1px dashed rgba(255,255,255,0.1);
}

.receipt-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.receipt-header h2 {
  margin: 0 0 5px 0;
  font-size: 1.5rem;
  font-weight: 900;
  color: inherit;
}

.receipt-date {
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0 0 15px 0;
}

.receipt-section {
  padding: 20px;
  border-bottom: 1px dashed rgba(255,255,255,0.1);
}

.section-title {
  color: #38bdf8;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 15px 0;
  font-weight: 800;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.receipt-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
}

.item-info { display: flex; gap: 10px; }
.item-qty { font-weight: 800; color: #60a5fa; }
.item-name { color: inherit; font-weight: 500; }
.item-subtotal { font-weight: 700; color: inherit; }

.logistics-info p {
  margin: 6px 0;
  color: #cbd5e1;
  font-size: 0.95rem;
}
.logistics-info strong { color: inherit; }

/* 🌟 CAJA MERCADO PAGO */
.receipt-mp-box {
  margin: 20px;
  background: rgba(14, 165, 233, 0.1);
  border: 1px solid rgba(14, 165, 233, 0.3);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}
.mp-logo {
  background: #0ea5e9;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.mp-info { display: flex; flex-direction: column; }
.mp-title { font-weight: 700; color: #38bdf8; font-size: 0.9rem; }
.mp-id { color: #bae6fd; font-size: 0.8rem; font-family: monospace; margin-top: 2px;}

/* CAJA DE ALERTA (CANCELACIÓN) */
.receipt-alert {
  margin: 20px 20px 0 20px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-left: 4px solid #ef4444;
  border-radius: 8px;
  padding: 15px;
}
.alert-title { display: flex; align-items: center; gap: 8px; color: #f87171; font-weight: 800; margin-bottom: 5px; }
.alert-msg { color: #fca5a5; font-size: 0.9rem; }
.alert-obs { margin-top: 5px; font-style: italic; color: #cbd5e1; font-size: 0.85rem; }

/* TOTALES */
.receipt-totals {
  padding: 20px;
  background: rgba(0,0,0,0.1);
}
.totals-row {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 0.95rem;
  margin-bottom: 8px;
}
.grand-total {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.1);
  font-size: 1.4rem;
  font-weight: 900;
  color: #10b981;
}

/* BOTONES SWAL */
.swal-btn-confirm { background: #10b981 !important; color: white !important; border-radius: 10px !important; font-weight: 700 !important; }
.swal-btn-cancel { background: #475569 !important; color: white !important; border-radius: 10px !important; font-weight: 700 !important; }

/* ============================================
   ESTADOS VACÍOS Y PAGINACIÓN
   ============================================ */
.empty-state { text-align: center; padding: 4rem; color: #94a3b8; }
.empty-icon-container {
  width: 100px; height: 100px; margin: 0 auto 1.5rem;
  background: rgba(59, 130, 246, 0.1); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #3b82f6;
}
.btn-cta {
  margin-top: 1.5rem; background: #3b82f6; color: white; border: none;
  padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 700;
  transition: all 0.2s ease;
}
.btn-cta:hover { background: #2563eb; transform: translateY(-2px); }

.paginacion { display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 3rem; }
.btn-pag {
  background: #1e293b; color: #fff; border: 1px solid rgba(255,255,255,0.1);
  padding: 10px 16px; border-radius: 10px; cursor: pointer; font-weight: 600;
  display: flex; align-items: center; gap: 6px; transition: 0.2s;
}
.btn-pag:hover:not(:disabled) { background: #3b82f6; border-color: #3b82f6; transform: translateY(-2px); }
.btn-pag:disabled { opacity: 0.4; cursor: not-allowed; }
.pag-info { color: #94a3b8; }
.pag-info strong { color: #f8fafc; }

/* ============================================
   MODO CLARO (OVERRIDES PROFESIONALES)
   ============================================ */
html.light-theme .mis-pedidos-container { background-color: #f8fafc; color: #0f172a; }
html.light-theme .header-titles h1 { color: #0f172a; }
html.light-theme .subtitle { color: #64748b; }
html.light-theme .btn-volver { background: #fff; border-color: #e2e8f0; color: #0f172a; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
html.light-theme .btn-volver:hover { background: #3b82f6; color: white; border-color: #3b82f6; }

/* Cards Light */
html.light-theme .pedido-card { background: #ffffff; border-color: #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
html.light-theme .pedido-card:hover { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); border-color: #cbd5e1; }
html.light-theme .pedido-header, html.light-theme .pedido-footer { border-color: #f1f5f9; }
html.light-theme .pedido-id { color: #0f172a; }
html.light-theme .pedido-fecha { color: #64748b; }
html.light-theme .icon-box { background: #eff6ff; color: #3b82f6; }
html.light-theme .item-row { color: #334155; }
html.light-theme .qty { color: #2563eb; }
html.light-theme .total-monto { color: #059669; }
html.light-theme .entrega-info { color: #475569; }

/* SweetAlert Receipt Light */
html.light-theme .receipt-header { background: #f8fafc; border-bottom-color: #e2e8f0; }
html.light-theme .receipt-date { color: #64748b; }
html.light-theme .receipt-section { border-bottom-color: #e2e8f0; }
html.light-theme .section-title { color: #0284c7; }
html.light-theme .item-qty { color: #2563eb; }
html.light-theme .logistics-info p { color: #475569; }

/* 🌟 MP BOX LIGHT (SOLUCIÓN AL CONTRASTE) */
html.light-theme .receipt-mp-box { background: #eff6ff; border-color: #bfdbfe; }
html.light-theme .mp-title { color: #0369a1; }
html.light-theme .mp-id { color: #3b82f6; font-weight: 600; }

html.light-theme .receipt-alert { background: #fef2f2; border-color: #fecaca; }
html.light-theme .alert-title { color: #dc2626; }
html.light-theme .alert-msg { color: #991b1b; }
html.light-theme .alert-obs { color: #7f1d1d; }

html.light-theme .receipt-totals { background: #f8fafc; border-top: 1px solid #e2e8f0; }
html.light-theme .totals-row { color: #475569; }
html.light-theme .grand-total { color: #059669; border-top-color: #e2e8f0; }

/* Paginación Light */
html.light-theme .btn-pag { background: #ffffff; color: #334155; border-color: #e2e8f0; }
html.light-theme .pag-info { color: #475569; }
html.light-theme .pag-info strong { color: #0f172a; }
html.light-theme .empty-icon-container { background: #eff6ff; color: #2563eb; }
</style>