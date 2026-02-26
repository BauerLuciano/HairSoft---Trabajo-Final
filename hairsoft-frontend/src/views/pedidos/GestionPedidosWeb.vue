<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Pedidos Web</h1>
          <p>Administrar compras online de clientes</p>
        </div>
        <button class="register-button" @click="cargarPedidos" :disabled="loading">
          <svg :class="{ 'spin': loading }" width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>

      <div class="filters-container">
        <div class="filtros-estados">
          <button 
            v-for="est in filtrosEstados" 
            :key="est.key" 
            @click="cambiarFiltro(est.key)" 
            :class="['btn-filtro', { active: filtroActual === est.key }]"
          >
            {{ est.label }}
            <span class="badge" v-if="contarPorEstado(est.key) > 0">{{ contarPorEstado(est.key) }}</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="no-results">
        <svg class="spin no-results-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
        <p>Cargando pedidos...</p>
      </div>
      <div v-else-if="pedidosFiltrados.length === 0" class="no-results">
        <svg class="no-results-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
        <p>No hay pedidos en este estado.</p>
        <small style="color: var(--text-tertiary); font-size: 0.9rem;">Prueba seleccionando otro filtro.</small>
      </div>

      <div v-else class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Fecha y Hora</th>
              <th>Cliente</th>
              <th>Entrega</th>
              <th>Items</th>
              <th>Total</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pedido in pedidosPaginados" :key="pedido.id">
              <td class="col-id">#{{ pedido.id }}</td>
              <td>
                <div class="fecha-col">
                  <strong>{{ formatearFecha(pedido.fecha_creacion) }}</strong>
                  <span class="hora">{{ formatearHora(pedido.fecha_creacion) }}hs</span>
                </div>
              </td>
              <td>
                <div class="cliente-info">
                  <strong>{{ pedido.cliente_nombre }}</strong>
                  <small>{{ pedido.cliente_email }}</small>
                </div>
              </td>
              <td>
                <div class="entrega-badge" :class="pedido.tipo_entrega === 'RETIRO' ? 'retiro' : 'envio'">
                  <svg v-if="pedido.tipo_entrega === 'RETIRO'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
                  {{ pedido.tipo_entrega }}
                </div>
              </td>
              <td>
                <span style="font-weight: 700; color: var(--text-primary);">{{ pedido.detalles?.length || 0 }}</span> 
                <span style="color: var(--text-secondary); font-size: 0.85rem;"> prod.</span>
              </td>
              <td>
                <div class="precio-total-container">
                  <span class="precio-total">${{ Number(pedido.total).toLocaleString('es-AR') }}</span>
                </div>
              </td>
              <td>
                <span :class="['badge-estado', getEstadoClass(pedido.estado)]">{{ pedido.estado_display }}</span>
                <div v-if="pedido.datos_entrega_interna" style="font-size: 0.75rem; color: #0ea5e9; margin-top: 6px; font-weight: 700; display: flex; align-items: center; gap: 4px;">
                  🛵 {{ pedido.datos_entrega_interna }}
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button v-if="pedido.estado === 'PAGADO'" @click="cambiarEstado(pedido, 'EN_PREPARACION')" class="action-button preparar" title="Preparar pedido">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                  </button>
                  
                  <template v-if="pedido.estado === 'EN_PREPARACION'">
                    <button v-if="pedido.tipo_entrega === 'RETIRO'" @click="cambiarEstado(pedido, 'LISTO_RETIRO')" class="action-button listo" title="Listo para retirar">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
                    </button>
                    <button v-else @click="cambiarEstado(pedido, 'EN_CAMINO')" class="action-button enviar" title="Despachar">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                    </button>
                  </template>

                  <button v-if="['LISTO_RETIRO', 'EN_CAMINO'].includes(pedido.estado)" @click="cambiarEstado(pedido, 'ENTREGADO')" class="action-button complete" title="Marcar Entregado">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                  </button>
                  
                  <button @click="verDetalle(pedido)" class="action-button detail" title="Ver detalle completo">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                    </svg>
                  </button>

                  <button v-if="!['ENTREGADO', 'CANCELADO'].includes(pedido.estado)" @click="cambiarEstado(pedido, 'CANCELADO')" class="action-button delete" title="Cancelar pedido">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="totalPaginas > 1" class="pagination-container">
          <button @click="paginaAnterior" :disabled="paginaActual === 1" class="pagination-button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            Anterior
          </button>
          
          <div class="pagination-info">
            <span class="pagination-numbers">Página <strong>{{ paginaActual }}</strong> de <strong>{{ totalPaginas }}</strong></span>
            <span class="pagination-total">{{ pedidosFiltrados.length }} pedidos en total</span>
          </div>

          <button @click="paginaSiguiente" :disabled="paginaActual === totalPaginas" class="pagination-button">
            Siguiente
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios'; 
import Swal from 'sweetalert2';

const API_URL = 'http://127.0.0.1:8000/api/web/pedidos/';
const pedidos = ref([]);
const loading = ref(false);
const filtroActual = ref('ACTIVOS');
const paginaActual = ref(1);
const itemsPorPagina = 8;

const filtrosEstados = [
  { key: 'TODOS', label: 'Todos' },
  { key: 'ACTIVOS', label: 'Pendientes' },
  { key: 'ENTREGADO', label: 'Entregados' },
  { key: 'CANCELADO', label: 'Cancelados' },
];

const cargarPedidos = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(API_URL, { headers: { 'Authorization': `Token ${token}` } });
    pedidos.value = Array.isArray(response.data) ? response.data : (response.data.results || []);
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const cambiarEstado = async (pedido, nuevoEstado) => {
  let repartidor = '';
  
  // 🛵 DESPACHO MOTO: Si es MOTO y va a EN_CAMINO, pedimos nombre
  if (nuevoEstado === 'EN_CAMINO' && pedido.tipo_entrega === 'MOTO') {
      const { value: nombre } = await Swal.fire({
          title: 'Despacho de Moto',
          text: '¿Quién es el repartidor que lleva este pedido?',
          input: 'text',
          inputPlaceholder: 'Ej: Juan Motos / Carlos Cadete',
          showCancelButton: true,
          confirmButtonText: 'Confirmar Salida',
          confirmButtonColor: '#3b82f6',
          background: '#1e293b',
          color: '#fff'
      });
      
      if (nombre === undefined) return; // Canceló el modal
      repartidor = nombre || 'Moto Mandado'; 
  }

  const result = await Swal.fire({
    title: '¿Confirmar cambio?',
    text: `Pasar pedido #${pedido.id} al estado: ${nuevoEstado}`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#3b82f6',
    background: '#1e293b',
    color: '#fff'
  });

  if (result.isConfirmed) {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}${pedido.id}/cambiar_estado/`, 
        { estado: nuevoEstado, repartidor: repartidor },
        { headers: { 'Authorization': `Token ${token}` } }
      );
      Swal.fire({ title: '¡Éxito!', icon: 'success', timer: 1000, showConfirmButton: false });
      cargarPedidos();
    } catch (e) {
      Swal.fire('Error', 'No se pudo actualizar el estado.', 'error');
    }
  }
};

const verDetalle = (p) => {
    const itemsHTML = p.detalles.map(d => `
        <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #334155; font-size: 0.95rem;">
            <span style="color:#f8fafc; font-weight: 500;">${d.nombre_producto}</span>
            <span style="font-weight:700; color:#38bdf8;">${d.cantidad} x $${Number(d.precio_unitario).toLocaleString('es-AR')}</span>
        </div>
    `).join('');

    Swal.fire({
        title: `<span style="font-weight: 800; color: #e2e8f0;">Detalle Pedido #${p.id}</span>`,
        html: `
            <div style="text-align: left; font-size: 0.95rem; color: #94a3b8; line-height: 1.6; font-family: 'Inter', sans-serif;">
                
                <div style="background: rgba(15, 23, 42, 0.6); padding: 18px; border-radius: 14px; margin-bottom: 15px; border: 1px solid #334155;">
                    <h4 style="color: #38bdf8; margin: 0 0 12px 0; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                      Datos del Cliente
                    </h4>
                    <p style="margin: 4px 0;"><strong style="color:#f8fafc;">Nombre:</strong> ${p.cliente_nombre}</p>
                    <p style="margin: 4px 0;"><strong style="color:#f8fafc;">Email:</strong> ${p.cliente_email}</p>
                </div>

                <div style="background: rgba(15, 23, 42, 0.6); padding: 18px; border-radius: 14px; margin-bottom: 15px; border: 1px solid #334155;">
                    <h4 style="color: #38bdf8; margin: 0 0 12px 0; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
                      Logística y Entrega
                    </h4>
                    <p style="margin: 4px 0;"><strong style="color:#f8fafc;">Método:</strong> ${p.tipo_entrega}</p>
                    <p style="margin: 4px 0;"><strong style="color:#f8fafc;">Dirección:</strong> ${p.direccion_envio || 'Retiro en Local'}</p>
                    <p style="margin: 4px 0;"><strong style="color:#f8fafc;">Repartidor/Chofer:</strong> 
                        <span style="color: #10b981; font-weight: 800; background: rgba(16, 185, 129, 0.1); padding: 2px 8px; border-radius: 6px;">${p.datos_entrega_interna || 'Aún no asignado'}</span>
                    </p>
                </div>

                <div style="background: rgba(15, 23, 42, 0.6); padding: 18px; border-radius: 14px; margin-bottom: 15px; border: 1px solid #334155;">
                    <h4 style="color: #38bdf8; margin: 0 0 12px 0; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                      Productos Comprados
                    </h4>
                    ${itemsHTML}
                    <div style="margin-top:15px; text-align:right; font-size:1.2rem; background: #0f172a; padding: 10px; border-radius: 8px;">
                        <span style="color:#94a3b8; font-size: 0.9rem; text-transform: uppercase; font-weight: 700; margin-right: 10px;">Total Pagado:</span> 
                        <strong style="color:#10b981;"> $${Number(p.total).toLocaleString('es-AR')}</strong>
                    </div>
                </div>
            </div>
        `,
        background: '#1e293b',
        color: '#fff',
        width: '600px',
        confirmButtonText: 'Cerrar Detalles',
        confirmButtonColor: '#0ea5e9'
    });
};

// Computed y formateadores
const pedidosFiltrados = computed(() => {
  if (filtroActual.value === 'TODOS') return pedidos.value;
  if (filtroActual.value === 'ACTIVOS') return pedidos.value.filter(p => !['ENTREGADO', 'CANCELADO'].includes(p.estado));
  return pedidos.value.filter(p => p.estado === filtroActual.value);
});

// 🔥 FUNCIONES DE PAGINACIÓN
const totalPaginas = computed(() => Math.max(1, Math.ceil(pedidosFiltrados.value.length / itemsPorPagina)));
const pedidosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina;
  return pedidosFiltrados.value.slice(inicio, inicio + itemsPorPagina);
});

const paginaAnterior = () => {
  if (paginaActual.value > 1) paginaActual.value--;
};
const paginaSiguiente = () => {
  if (paginaActual.value < totalPaginas.value) paginaActual.value++;
};

const cambiarFiltro = (k) => { 
  filtroActual.value = k; 
  paginaActual.value = 1; // Reseteamos página al cambiar de filtro
};

const contarPorEstado = (k) => k === 'TODOS' ? pedidos.value.length : (k === 'ACTIVOS' ? pedidos.value.filter(p => !['ENTREGADO', 'CANCELADO'].includes(p.estado)).length : pedidos.value.filter(p => p.estado === k).length);

const getEstadoClass = (e) => {
  const mapa = { 
    'PENDIENTE_PAGO': 'estado-secondary', 
    'PAGADO': 'estado-info', 
    'EN_PREPARACION': 'estado-warning', 
    'LISTO_RETIRO': 'estado-success', 
    'EN_CAMINO': 'estado-success', 
    'ENTREGADO': 'estado-completado', 
    'CANCELADO': 'estado-cancelado' 
  };
  return mapa[e] || 'estado-secondary';
};

const formatearFecha = (f) => new Date(f).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
const formatearHora = (f) => new Date(f).toLocaleTimeString('es-AR', {hour:'2-digit', minute:'2-digit'});

onMounted(cargarPedidos);
</script>

<style scoped>
/* ========================================
   ESTILO PROFESIONAL PEDIDOS WEB (UI PREMIUM)
   ======================================== */

.list-container {
  padding: 32px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}

.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.4s ease;
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* HEADER */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 25px;
}

.header-content h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.header-content p {
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 8px;
  letter-spacing: 0.5px;
}

.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.register-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
}

.register-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 🔥 FILTROS TIPO TABS PREMIUM */
.filters-container {
  margin-bottom: 30px;
  background: var(--bg-primary);
  padding: 8px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
  display: inline-block;
}

.filtros-estados {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-filtro {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 12px 24px;
  border-radius: 14px;
  cursor: pointer;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.btn-filtro:hover:not(.active) {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.btn-filtro.active {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid var(--border-color);
}

.badge {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.btn-filtro.active .badge {
  background: #0ea5e9;
  color: white;
  border-color: #0ea5e9;
}

/* TABLA */
.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

.users-table th {
  background: var(--accent-color);
  color: white;
  padding: 18px 14px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1px;
  white-space: nowrap;
}

.users-table tr {
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s ease;
}

.users-table td {
  padding: 16px 14px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.users-table td strong {
  color: var(--text-primary);
  font-weight: 800;
  letter-spacing: 0.3px;
}

.users-table tr:hover {
  background: var(--hover-bg);
}

/* COLUMNAS ESPECÍFICAS */
.col-id {
  color: #0ea5e9;
  font-weight: 900;
  font-size: 1.1rem;
}

.fecha-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hora {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  font-weight: 600;
}

.cliente-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cliente-info small {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

/* ENTREGA */
.entrega-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  margin-bottom: 4px;
  white-space: nowrap;
}

.entrega-badge.retiro {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.entrega-badge.envio {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

/* PRECIO */
.precio-total-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.precio-total {
  font-weight: 900;
  font-size: 1.15rem;
  color: #10b981;
  letter-spacing: 0.5px;
}

/* ESTADOS */
.badge-estado {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
  white-space: nowrap;
  border: 2px solid transparent;
}

.estado-warning { background: var(--bg-tertiary); color: #f59e0b; border-color: #f59e0b; box-shadow: 0 0 10px rgba(245, 158, 11, 0.2); }
.estado-info { background: var(--bg-tertiary); color: #0ea5e9; border-color: #0ea5e9; box-shadow: 0 0 10px rgba(14, 165, 233, 0.2); }
.estado-success { background: var(--bg-tertiary); color: #10b981; border-color: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-tertiary); border-color: var(--text-tertiary); }
.estado-completado { background: #0ea5e9; color: white; border-color: #0ea5e9; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3); }
.estado-cancelado { background: var(--bg-tertiary); color: var(--error-color); border-color: var(--error-color); opacity: 0.8; text-decoration: line-through; }

/* ACCIONES */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-button {
  padding: 8px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  transition: all 0.2s ease;
  background: var(--bg-tertiary);
}

.action-button svg { stroke: currentColor; }

.action-button.preparar { border: 1px solid #0ea5e9; color: #0ea5e9; }
.action-button.preparar:hover { background: #0ea5e9; color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3); }

.action-button.listo { border: 1px solid #8b5cf6; color: #8b5cf6; }
.action-button.listo:hover { background: #8b5cf6; color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(139, 92, 246, 0.3); }

.action-button.enviar { border: 1px solid #f59e0b; color: #f59e0b; }
.action-button.enviar:hover { background: #f59e0b; color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3); }

.action-button.complete { border: 1px solid #10b981; color: #10b981; }
.action-button.complete:hover { background: #10b981; color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }

.action-button.detail { background: var(--hover-bg); border: 1px solid var(--border-color) !important; color: var(--text-secondary) !important; }
.action-button.detail:hover { background: var(--text-secondary); color: var(--bg-primary) !important; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); }

.action-button.delete { border: 1px solid var(--error-color); color: var(--error-color); }
.action-button.delete:hover { background: var(--error-color); color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3); }


/* 🔥 PAGINACIÓN MEJORADA */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background: var(--bg-primary);
  border-radius: 16px;
  margin-top: 25px;
  border: 1px solid var(--border-color);
  gap: 20px;
  flex-wrap: wrap;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}

.pagination-button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.pagination-button:hover:not(:disabled) {
  background: var(--hover-bg);
  border-color: var(--accent-color);
  color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.pagination-button:disabled {
  background: transparent;
  color: var(--text-tertiary);
  border-color: transparent;
  cursor: not-allowed;
  opacity: 0.5;
}

.pagination-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.pagination-numbers {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 500;
  letter-spacing: 0.5px;
}

.pagination-numbers strong {
  color: var(--text-primary);
  font-weight: 900;
  font-size: 1.1rem;
}

.pagination-total {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* EMPTY STATE */
.no-results {
  text-align: center;
  padding: 80px 20px;
  background: var(--bg-primary);
  border-radius: 16px;
  border: 1px dashed var(--border-color);
  margin-top: 20px;
}

.no-results-icon {
  margin-bottom: 20px;
  color: var(--text-tertiary);
  opacity: 0.5;
}

.no-results p {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-container { padding: 15px; }
  .list-card { padding: 25px; border-radius: 20px; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .header-content h1 { font-size: 1.6rem; }
  .filters-container { width: 100%; border-radius: 16px; padding: 5px; }
  .btn-filtro { flex: 1; justify-content: center; padding: 10px; font-size: 0.8rem; }
  
  .users-table { font-size: 0.85rem; }
  .users-table th { font-size: 0.7rem; padding: 14px 10px; }
  .action-buttons { flex-direction: row; gap: 6px; }
  
  .pagination-container { flex-direction: column; gap: 15px; padding: 15px; }
  .pagination-button { width: 100%; justify-content: center; }
}

@media (max-width: 480px) {
  .list-card { padding: 18px; border-radius: 16px; }
  .header-content h1 { font-size: 1.4rem; }
  .users-table { display: block; overflow-x: auto; white-space: nowrap; }
  .badge-estado { font-size: 0.65rem; padding: 5px 10px; }
  .action-button { width: 36px; height: 36px; }
  .register-button { width: 100%; justify-content: center; }
  .filtros-estados { flex-direction: column; }
}
</style>