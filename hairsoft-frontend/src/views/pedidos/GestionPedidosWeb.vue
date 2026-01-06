<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Pedidos Web</h1>
          <p>Administrar compras online de clientes</p>
        </div>
        <button class="register-button" @click="cargarPedidos">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Actualizar
        </button>
      </div>

      <!-- FILTROS DE ESTADOS -->
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

      <!-- LOADING -->
      <div v-if="loading" class="no-results">
        <p>Cargando pedidos...</p>
      </div>

      <!-- EMPTY STATE -->
      <div v-else-if="pedidosFiltrados.length === 0" class="no-results">
        <svg class="no-results-icon" width="48" height="48" viewBox="0 0 24 24" fill="none">
          <path d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p>No hay pedidos en estado <strong>{{ getLabelFiltro() }}</strong></p>
      </div>

      <!-- TABLA -->
      <div v-else class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Fecha</th>
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
                  <span class="hora">{{ formatearHora(pedido.fecha_creacion) }}</span>
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
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path v-if="pedido.tipo_entrega === 'RETIRO'" d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path v-else d="M1 3h15v13H1zM16 8h4l3 3v5h-7V8zM5.5 21a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM18.5 21a2.5 2.5 0 100-5 2.5 2.5 0 000 5z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  {{ pedido.tipo_entrega === 'RETIRO' ? 'Retiro' : 'Envío' }}
                </div>
                <div class="direccion-tooltip" v-if="pedido.tipo_entrega !== 'RETIRO'">
                  {{ pedido.direccion_envio }}
                </div>
              </td>
              
              <td>
                <div class="items-compactos">
                  <div v-for="d in pedido.detalles.slice(0, 2)" :key="d.id" class="item-row">
                    <span class="item-qty">{{ d.cantidad }}x</span>
                    <span class="item-name">{{ d.nombre_producto }}</span>
                  </div>
                  <div v-if="pedido.detalles.length > 2" class="mas-items">
                    +{{ pedido.detalles.length - 2 }} más
                  </div>
                </div>
              </td>
              
              <td>
                <div class="precio-total-container">
                  <span class="precio-total">${{ Number(pedido.total).toLocaleString() }}</span>
                </div>
              </td>
              
              <td>
                <span :class="['badge-estado', getEstadoClass(pedido.estado)]">
                  {{ pedido.estado_display }}
                </span>
              </td>
              
              <td>
                <div class="action-buttons">
                  <button 
                    v-if="pedido.estado === 'PAGADO'"
                    @click="cambiarEstado(pedido, 'EN_PREPARACION')"
                    class="action-button preparar"
                    title="Comenzar a preparar"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>

                  <template v-if="pedido.estado === 'EN_PREPARACION'">
                    <button 
                      v-if="pedido.tipo_entrega === 'RETIRO'"
                      @click="cambiarEstado(pedido, 'LISTO_RETIRO')"
                      class="action-button listo"
                      title="Marcar listo para retirar"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" stroke="currentColor" stroke-width="2"/>
                        <polyline points="7.5 4.21 12 6.81 16.5 4.21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        <polyline points="7.5 19.79 7.5 14.6 3 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        <polyline points="21 12 16.5 14.6 16.5 19.79" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        <line x1="12" y1="22.08" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      </svg>
                    </button>
                    
                    <button 
                      v-else
                      @click="cambiarEstado(pedido, 'EN_CAMINO')"
                      class="action-button enviar"
                      title="Despachar pedido"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                  </template>

                  <button 
                    v-if="['LISTO_RETIRO', 'EN_CAMINO'].includes(pedido.estado)"
                    @click="cambiarEstado(pedido, 'ENTREGADO')"
                    class="action-button complete"
                    title="Finalizar entrega"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <polyline points="20 6 9 17 4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>

                  <button 
                    v-if="!['ENTREGADO', 'CANCELADO'].includes(pedido.estado)"
                    @click="cambiarEstado(pedido, 'CANCELADO')"
                    class="action-button delete"
                    title="Cancelar y devolver stock"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- PAGINACIÓN -->
        <div v-if="totalPaginas > 1" class="pagination-container">
          <button 
            @click="irAPagina(paginaActual - 1)"
            :disabled="paginaActual === 1"
            class="pagination-button"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <polyline points="15 18 9 12 15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Anterior
          </button>

          <div class="pagination-info">
            <span class="pagination-numbers">
              Página <strong>{{ paginaActual }}</strong> de <strong>{{ totalPaginas }}</strong>
            </span>
            <span class="pagination-total">
              ({{ pedidosFiltrados.length }} pedidos totales)
            </span>
          </div>

          <button 
            @click="irAPagina(paginaActual + 1)"
            :disabled="paginaActual === totalPaginas"
            class="pagination-button"
          >
            Siguiente
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';
import Swal from 'sweetalert2';

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
    const response = await api.get('/pedidos-web/');
    let datos = Array.isArray(response.data) ? response.data : (response.data.results || []);
    
    // ✅ CORRECCIÓN: Confiamos en el backend. 
    // El serializer nuevo ya manda "Juan Perez" en el campo 'cliente_nombre'.
    pedidos.value = datos; 

  } catch (error) {
    console.error(error);
    Swal.fire({
      title: 'Error',
      text: 'No se pudieron cargar los pedidos',
      icon: 'error',
      confirmButtonColor: '#3b82f6'
    });
  } finally {
    loading.value = false;
  }
};

const pedidosFiltrados = computed(() => {
  if (filtroActual.value === 'TODOS') return pedidos.value;
  if (filtroActual.value === 'ACTIVOS') {
    return pedidos.value.filter(p => !['ENTREGADO', 'CANCELADO'].includes(p.estado));
  }
  return pedidos.value.filter(p => p.estado === filtroActual.value);
});

const totalPaginas = computed(() => {
  return Math.ceil(pedidosFiltrados.value.length / itemsPorPagina);
});

const pedidosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina;
  const fin = inicio + itemsPorPagina;
  return pedidosFiltrados.value.slice(inicio, fin);
});

const cambiarFiltro = (nuevoFiltro) => {
  filtroActual.value = nuevoFiltro;
  paginaActual.value = 1;
};

const irAPagina = (numeroPagina) => {
  if (numeroPagina >= 1 && numeroPagina <= totalPaginas.value) {
    paginaActual.value = numeroPagina;
    document.querySelector('.table-container')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

const contarPorEstado = (key) => {
  if (key === 'TODOS') return pedidos.value.length;
  if (key === 'ACTIVOS') return pedidos.value.filter(p => !['ENTREGADO', 'CANCELADO'].includes(p.estado)).length;
  return pedidos.value.filter(p => p.estado === key).length;
};

const getLabelFiltro = () => filtrosEstados.find(f => f.key === filtroActual.value)?.label;

const cambiarEstado = async (pedido, nuevoEstado) => {
  let titulo = '¿Avanzar estado?';
  let texto = `El pedido pasará a: ${nuevoEstado}`;
  let confirmColor = '#3b82f6';

  if (nuevoEstado === 'CANCELADO') {
    titulo = '¿Cancelar Pedido?';
    texto = 'Se devolverá el stock de los productos automáticamente.';
    confirmColor = '#ef4444';
  } else if (nuevoEstado === 'ENTREGADO') {
    titulo = '¿Confirmar Entrega?';
    texto = 'El pedido se marcará como finalizado.';
    confirmColor = '#10b981';
  }

  const result = await Swal.fire({
    title: titulo,
    text: texto,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: confirmColor,
    cancelButtonColor: '#6b7280',
    confirmButtonText: 'Sí, confirmar',
    background: '#1e293b',
    color: '#f8fafc'
  });

  if (result.isConfirmed) {
    try {
      await api.post(`/pedidos-web/${pedido.id}/cambiar_estado/`, { estado: nuevoEstado });
      
      Swal.fire({
        title: '¡Actualizado!',
        icon: 'success',
        timer: 1500,
        showConfirmButton: false,
        background: '#1e293b',
        color: '#f8fafc'
      });
      
      cargarPedidos();
    } catch (error) {
      Swal.fire({
        title: 'Error',
        text: 'No se pudo actualizar el estado',
        icon: 'error',
        confirmButtonColor: '#3b82f6',
        background: '#1e293b',
        color: '#f8fafc'
      });
    }
  }
};

const formatearFecha = (f) => new Date(f).toLocaleDateString('es-AR');
const formatearHora = (f) => new Date(f).toLocaleTimeString('es-AR', {hour:'2-digit', minute:'2-digit'});

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

// --- AGREGADO: Ver Detalle (que faltaba en tu script anterior) ---
const verDetalle = (pedido) => {
    let itemsHTML = pedido.detalles.map(d => 
        `<div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
           <span>${d.nombre_producto}</span>
           <strong>x${d.cantidad}</strong>
         </div>`
    ).join('');

    Swal.fire({
        title: `Pedido #${pedido.id}`,
        html: `
            <div style="text-align: left; color: #cbd5e1;">
                <p><strong>Cliente:</strong> ${pedido.cliente_nombre}</p>
                <p><strong>Email:</strong> ${pedido.cliente_email}</p>
                <p><strong>Entrega:</strong> ${pedido.tipo_entrega === 'RETIRO' ? 'Retiro en Local' : 'Envío: ' + pedido.direccion_envio}</p>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">
                ${itemsHTML}
                <div style="margin-top: 15px; text-align: right; font-size: 1.2rem; color: #fff;">
                    Total: <span style="color: #4ade80;">$${Number(pedido.total).toLocaleString()}</span>
                </div>
            </div>
        `,
        background: '#1e293b',
        color: '#fff',
        confirmButtonColor: '#3b82f6'
    });
};

onMounted(cargarPedidos);
</script>

<style scoped>
/* ========================================
   ESTILO PROFESIONAL PEDIDOS WEB
   ======================================== */

.list-container {
  padding: 0;
  width: 100%;
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
}

.register-button:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  opacity: 0.9;
}

.register-button svg {
  stroke: currentColor;
}

/* FILTROS */
.filters-container {
  margin-bottom: 30px;
  background: var(--hover-bg);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.filtros-estados {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-filtro {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 10px 18px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.8px;
}

.btn-filtro:hover {
  background: var(--hover-bg);
}

.btn-filtro.active {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.badge {
  background: rgba(255,255,255,0.2);
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 800;
}

.btn-filtro:not(.active) .badge {
  background: var(--bg-primary);
  color: var(--text-primary);
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
  letter-spacing: 1.2px;
  white-space: nowrap;
}

.users-table tr {
  border-bottom: 1px solid var(--border-color);
}

.users-table td {
  padding: 14px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-weight: 500;
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
  font-weight: 800;
  font-size: 1rem;
}

.fecha-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hora {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.cliente-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cliente-info small {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

/* ENTREGA */
.entrega-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.entrega-badge.retiro {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.entrega-badge.envio {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid #f59e0b;
}

.entrega-badge svg {
  stroke: currentColor;
}

.direccion-tooltip {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ITEMS */
.items-compactos {
  max-width: 200px;
}

.item-row {
  display: flex;
  gap: 6px;
  padding: 3px 0;
  font-size: 0.85rem;
}

.item-qty {
  color: #0ea5e9;
  font-weight: 800;
}

.item-name {
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mas-items {
  color: var(--text-tertiary);
  font-size: 0.75rem;
  font-style: italic;
  padding: 4px 0;
  background: var(--hover-bg);
  border-radius: 4px;
  text-align: center;
  margin-top: 4px;
}

/* PRECIO */
.precio-total-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.precio-total {
  font-weight: 900;
  font-size: 1.2rem;
  background: linear-gradient(135deg, #0ea5e9, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

/* ESTADOS */
.badge-estado {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.estado-warning {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
}

.estado-info {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
}

.estado-success {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
}

.estado-secondary {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  border: 2px solid var(--text-tertiary);
}

.estado-completado {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
}

.estado-cancelado {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  opacity: 0.8;
}

/* ACCIONES */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-button {
  padding: 8px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.action-button svg {
  stroke: currentColor;
}

.action-button.preparar {
  background: var(--bg-tertiary);
  border: 1px solid #0ea5e9;
  color: #0ea5e9;
}

.action-button.preparar:hover {
  background: var(--hover-bg);
  opacity: 0.9;
}

.action-button.listo {
  background: var(--bg-tertiary);
  border: 1px solid #8b5cf6;
  color: #8b5cf6;
}

.action-button.listo:hover {
  background: var(--hover-bg);
  opacity: 0.9;
}

.action-button.enviar {
  background: var(--bg-tertiary);
  border: 1px solid #8b5cf6;
  color: #8b5cf6;
}

.action-button.enviar:hover {
  background: var(--hover-bg);
  opacity: 0.9;
}

.action-button.complete {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}

.action-button.complete:hover {
  background: var(--hover-bg);
  opacity: 0.9;
}

.action-button.delete {
  background: var(--bg-tertiary);
  border: 1px solid var(--error-color);
  color: var(--error-color);
}

.action-button.delete:hover {
  background: var(--hover-bg);
  opacity: 0.9;
}

/* PAGINACIÓN */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 20px;
  background: var(--hover-bg);
  border-radius: 16px;
  margin-top: 25px;
  border: 1px solid var(--border-color);
  gap: 20px;
  flex-wrap: wrap;
}

.pagination-button {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 12px 24px;
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
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
}

.pagination-button:disabled {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  opacity: 0.5;
}

.pagination-button svg {
  stroke: currentColor;
}

.pagination-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.pagination-numbers {
  font-size: 1.1rem;
  color: var(--text-primary);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.pagination-numbers strong {
  color: var(--accent-color);
  font-weight: 900;
  font-size: 1.3rem;
}

.pagination-total {
  font-size: 0.85rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

/* EMPTY STATE */
.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
}

.no-results-icon {
  margin-bottom: 15px;
  opacity: 0.5;
  stroke: var(--text-tertiary);
}

.no-results p {
  margin: 0;
  font-size: 1.1em;
  color: var(--text-primary);
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-card {
    padding: 25px;
    border-radius: 20px;
  }

  .list-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-content h1 {
    font-size: 1.6rem;
  }

  .users-table {
    font-size: 0.85rem;
  }

  .users-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 6px;
  }

  .pagination-container {
    flex-direction: column;
    gap: 15px;
  }

  .pagination-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .list-card {
    padding: 18px;
    border-radius: 16px;
  }

  .header-content h1 {
    font-size: 1.4rem;
  }

  .users-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }

  .badge-estado {
    font-size: 0.65rem;
    padding: 5px 10px;
  }

  .action-button {
    width: 36px;
    height: 36px;
  }

  .pagination-numbers {
    font-size: 0.95rem;
  }

  .pagination-numbers strong {
    font-size: 1.1rem;
  }
}
</style>