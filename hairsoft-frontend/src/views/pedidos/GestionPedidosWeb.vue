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
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
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
                <span :class="['badge-estado', getEstadoClass(pedido.estado)]">{{ formatearEstadoPedido(pedido.estado, pedido.estado_display) }}</span>
                <div v-if="pedido.datos_entrega_interna" style="font-size: 0.75rem; color: #0ea5e9; margin-top: 6px; font-weight: 700; display: flex; align-items: center; gap: 4px;">
                  🛵 {{ pedido.datos_entrega_interna }}
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <div class="action-group action-group-main">
                    <button v-if="pedido.estado === 'PAGADO'" @click="cambiarEstado(pedido, 'EN_PREPARACION')" class="action-button preparar is-primary" title="Preparar pedido">
                      Preparar pedido
                    </button>

                    <template v-if="pedido.estado === 'EN_PREPARACION'">
                      <button v-if="pedido.tipo_entrega === 'RETIRO'" @click="cambiarEstado(pedido, 'LISTO_RETIRO')" class="action-button listo is-primary" title="Marcar como listo para retirar">
                        Listo para retirar
                      </button>
                      <button v-else @click="cambiarEstado(pedido, 'EN_CAMINO')" class="action-button enviar is-primary" title="Despachar pedido">
                        Despachar
                      </button>
                    </template>

                    <button v-if="['LISTO_RETIRO', 'EN_CAMINO'].includes(pedido.estado)" @click="cambiarEstado(pedido, 'ENTREGADO')" class="action-button complete is-primary" title="Marcar como entregado">
                      Marcar entregado
                    </button>

                    <button v-if="esAdmin && ['SOLICITA_CANCELACION', 'INCIDENCIA'].includes(pedido.estado)" @click="aprobarCancelacionCliente(pedido)" class="action-button refund is-primary" title="Aprobar cancelación">
                      Aprobar cancelación
                    </button>

                    <button v-if="esAdmin && pedido.estado === 'CANCELADO' && pedido.reembolso_estado === 'PENDIENTE' && pedido.mp_payment_id" @click="mostrarModalDevolucionManual(pedido, { modo: 'pendiente' })" class="action-button refund is-primary" title="Confirmar devolución manual">
                      Confirmar devolución
                    </button>

                    <button @click="verDetalle(pedido)" class="action-button detail" title="Ver detalle completo">
                      Ver detalle
                    </button>
                  </div>

                  <div v-if="(esAdmin && ['SOLICITA_CANCELACION', 'INCIDENCIA'].includes(pedido.estado)) || (esAdmin && ['PENDIENTE_PAGO','PAGADO','EN_PREPARACION'].includes(pedido.estado))" class="action-group action-group-admin">
                    <button v-if="esAdmin && ['SOLICITA_CANCELACION', 'INCIDENCIA'].includes(pedido.estado)" @click="rechazarSolicitud(pedido)" class="action-button enviar" title="Rechazar solicitud/incidencia">
                      Rechazar solicitud
                    </button>

                    <button v-if="esAdmin && ['PENDIENTE_PAGO','PAGADO','EN_PREPARACION'].includes(pedido.estado)" @click="cambiarEstado(pedido, 'CANCELADO')" class="action-button delete action-cancel" title="Cancelar pedido">
                      Cancelar
                    </button>
                  </div>
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
import { API_BASE_URL, getApiUrl } from '@/config/api'

const API_URL = `${API_BASE_URL}/api/web/pedidos/`;
const pedidos = ref([]);
const loading = ref(false);
const filtroActual = ref('ACTIVOS');
const paginaActual = ref(1);
const itemsPorPagina = 8;
const userRol = ref(localStorage.getItem('user_rol') || '');
const esAdmin = computed(() => userRol.value === 'ADMINISTRADOR');
const esRecepcionOAdmin = computed(() => ['ADMINISTRADOR', 'RECEPCIONISTA'].includes(userRol.value));

const repartidoresConocidos = computed(() => {
  const nombres = pedidos.value
    .map(p => (p.datos_entrega_interna || '').trim())
    .filter(n => n && n !== 'Aún no asignado' && n !== 'No aplica');
  return [...new Set(nombres)].sort((a, b) => a.localeCompare(b));
});

const filtrosEstados = [
  { key: 'TODOS', label: 'Todos' },
  { key: 'ACTIVOS', label: 'Pendientes' },
  { key: 'SOLICITA_CANCELACION', label: 'Solicitudes de cancelación' },
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

const cambiarEstado = async (pedido, nuevoEstado, skipModal = false, motivoAuto = '', obsAuto = '') => {
  let repartidor = '';
  let motivoCancelacion = motivoAuto;
  let obsCancelacion = obsAuto;
  
  // 🛵 CASO 1: DESPACHO MOTO
  if (nuevoEstado === 'EN_CAMINO' && pedido.tipo_entrega === 'MOTO') {
      const opciones = repartidoresConocidos.value
        .map(nombre => `<option value="${nombre}">${nombre}</option>`)
        .join('');

      const { value: nombre } = await Swal.fire({
          title: 'Despacho de Moto',
          html: `
            <div style="text-align:left; font-family:Inter,sans-serif;">
              <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:12px;">Seleccioná el repartidor que llevará el pedido.</p>
              <label style="color:#f8fafc; font-weight:700; display:block; margin-bottom:6px;">Repartidor</label>
              <select id="swal-repartidor" class="swal2-input" style="width:100%; margin:0 0 12px 0; background:#0f172a; color:white; border:1px solid #334155;">
                <option value="">Seleccionar repartidor...</option>
                ${opciones}
                <option value="__OTRO__">Otro repartidor...</option>
              </select>
              <input id="swal-repartidor-otro" class="swal2-input" style="display:none; width:100%; margin:0; background:#0f172a; color:white; border:1px solid #334155;" placeholder="Nombre del repartidor" />
            </div>
          `,
          didOpen: () => {
            const select = document.getElementById('swal-repartidor');
            const otro = document.getElementById('swal-repartidor-otro');
            select?.addEventListener('change', () => {
              const esOtro = select.value === '__OTRO__';
              otro.style.display = esOtro ? 'block' : 'none';
              if (esOtro) otro.focus();
            });
          },
          preConfirm: () => {
            const select = document.getElementById('swal-repartidor');
            const otro = document.getElementById('swal-repartidor-otro');
            const seleccionado = select?.value || '';
            const nombreFinal = seleccionado === '__OTRO__' ? (otro?.value || '').trim() : seleccionado;
            if (!nombreFinal) {
              Swal.showValidationMessage('Seleccioná o ingresá un repartidor');
              return false;
            }
            return nombreFinal;
          },
          showCancelButton: true,
          confirmButtonText: 'Confirmar Salida',
          confirmButtonColor: '#3b82f6',
          background: '#1e293b',
          color: '#fff'
      });
      if (nombre === undefined) return; 
      repartidor = nombre || 'Moto Mandado'; 
  }

  // 🚫 CASO 2: CANCELACIÓN ADMINISTRATIVA DIRECTA
  if (nuevoEstado === 'CANCELADO' && !skipModal) {
    if (!esAdmin.value) {
      await Swal.fire('Permiso requerido', 'Solo un administrador puede cancelar pedidos o procesar reembolsos.', 'warning');
      return;
    }

    if (['SOLICITA_CANCELACION', 'INCIDENCIA'].includes(pedido.estado)) {
      await Swal.fire({
        title: 'Usá la solicitud del cliente',
        text: 'Este pedido tiene una solicitud del cliente. Revisá el motivo original y usá "Aprobar cancelación" o "Rechazar solicitud".',
        icon: 'info',
        background: '#1e293b',
        color: '#fff'
      });
      return;
    }

    const motivosAdmin = [
      { value: '', label: 'Seleccioná un motivo' },
      { value: 'Falta de stock (error del sistema)', label: 'Falta de stock (error del sistema)' },
      { value: 'Pedido duplicado', label: 'Pedido duplicado' },
      { value: 'Solicitud del cliente', label: 'Solicitud del cliente' },
      { value: 'Problema con la entrega', label: 'Problema con la entrega' },
      { value: 'Problema con Mercado Pago', label: 'Problema con Mercado Pago' },
      { value: 'Otro motivo', label: 'Otro motivo' }
    ];

    const { value: formValues } = await Swal.fire({
      title: 'Cancelar pedido web',
      html: `
        <div style="text-align: left; font-family: 'Inter', sans-serif;">
          <div style="background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.45); border-radius: 12px; padding: 12px; margin-bottom: 14px;">
            <p style="margin:0; color:#fecaca; font-size:0.9rem; line-height:1.5;">
              <strong>Acción administrativa delicada.</strong> Se cancelará el pedido #${pedido.id}. El stock se devolverá automáticamente al inventario. Si hay pago con Mercado Pago, la devolución se realizará manualmente desde la cuenta de MP del administrador y luego deberá confirmarse en HairSoft.
            </p>
          </div>
          <label style="color: #f8fafc; font-weight: 700; display: block; margin-bottom: 5px;">Motivo <span style="color:#ef4444;">*</span></label>
          <select id="swal-motivo" class="swal2-input" style="width: 100%; margin: 0 0 15px 0; background: #0f172a; color: white; border: 1px solid #334155;">
            ${motivosAdmin.map(m => `<option value="${m.value}" ${m.value === '' ? 'disabled selected' : ''}>${m.label}</option>`).join('')}
          </select>
          <label style="color: #f8fafc; font-weight: 700; display: block; margin-bottom: 5px;">Observaciones adicionales <span id="swal-obs-req" style="font-weight:500; color:#94a3b8;">(opcional)</span></label>
          <textarea id="swal-obs" class="swal2-textarea" style="width: 100%; margin: 0 0 15px 0; background: #0f172a; color: white; border: 1px solid #334155; height: 80px;" placeholder="Podés agregar un detalle adicional"></textarea>
          <label style="color: #f8fafc; font-weight: 700; display: block; margin-bottom: 5px;">Para confirmar, escribí CANCELAR</label>
          <input id="swal-confirmacion" class="swal2-input" style="width: 100%; margin: 0; background: #0f172a; color: white; border: 1px solid #334155;" placeholder="CANCELAR" />
        </div>
      `,
      focusConfirm: false,
      showCancelButton: true,
      confirmButtonText: 'Confirmar cancelación',
      confirmButtonColor: '#ef4444',
      background: '#1e293b',
      color: '#fff',
      didOpen: () => {
        const motivoEl = document.getElementById('swal-motivo');
        const obsReq = document.getElementById('swal-obs-req');
        const obsEl = document.getElementById('swal-obs');
        const actualizar = () => {
          const esOtro = motivoEl?.value === 'Otro motivo';
          if (obsReq) {
            obsReq.textContent = esOtro ? '(obligatoria)' : '(opcional)';
            obsReq.style.color = esOtro ? '#ef4444' : '#94a3b8';
            obsReq.style.fontWeight = esOtro ? '700' : '500';
          }
          if (obsEl) obsEl.placeholder = esOtro ? 'Explicá el motivo de la cancelación' : 'Podés agregar un detalle adicional';
        };
        motivoEl?.addEventListener('change', actualizar);
        actualizar();
      },
      preConfirm: () => {
        const motivo = (document.getElementById('swal-motivo')?.value || '').trim();
        const obs = (document.getElementById('swal-obs')?.value || '').trim();
        const confirmacion = (document.getElementById('swal-confirmacion')?.value || '').trim().toUpperCase();
        if (!motivo) {
          Swal.showValidationMessage('Seleccioná un motivo de cancelación.');
          return false;
        }
        if (motivo === 'Otro motivo' && !obs) {
          Swal.showValidationMessage('Indicá una observación para explicar el motivo.');
          return false;
        }
        if (confirmacion !== 'CANCELAR') {
          Swal.showValidationMessage('Escribí CANCELAR para confirmar esta acción.');
          return false;
        }
        return { motivo, obs };
      }
    });

    if (!formValues) return;
    motivoCancelacion = formValues.motivo;
    obsCancelacion = formValues.obs;
  } else if (!skipModal) {
    const result = await Swal.fire({
      title: '¿Confirmar cambio?',
      text: `Pasar pedido #${pedido.id} al estado: ${nuevoEstado}`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#3b82f6',
      background: '#1e293b',
      color: '#fff'
    });
    if (!result.isConfirmed) return;
  }

  // Ejecutar petición
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}${pedido.id}/cambiar_estado/`, 
      { 
        estado: nuevoEstado, 
        repartidor: repartidor,
        motivo_cancelacion: motivoCancelacion,
        obs_cancelacion: obsCancelacion,
        devolver_stock: true,
      },
      { headers: { 'Authorization': `Token ${token}` } }
    );
    
    // 🔥 LÓGICA DE ALERTAS MEJORADA 🔥
    if (nuevoEstado === 'CANCELADO') {
      const reembolso = response.data.reembolso_estado;
      await cargarPedidos();
      const pedidoActualizado = pedidos.value.find(p => p.id === pedido.id) || { ...pedido, ...response.data, estado: 'CANCELADO' };
      if (reembolso === 'PENDIENTE' && pedidoActualizado.mp_payment_id) {
        await mostrarModalDevolucionManual(pedidoActualizado, { modo: 'postAprobacion' });
        return;
      } else if (reembolso === 'MANUAL') {
        Swal.fire({ title: 'Devolución confirmada', text: 'La devolución manual fue registrada correctamente.', icon: 'success', background: '#1e293b', color: '#fff' });
      } else {
        Swal.fire({ title: 'Pedido cancelado', text: `Stock devuelto: ${response.data.stock_devuelto ? 'Sí' : 'No / pendiente verificación'}`, icon: 'success', background: '#1e293b', color: '#fff' });
      }
    } else if (nuevoEstado === 'EN_CAMINO' && response.data.whatsapp_enviado) {
      Swal.fire({
        title: '🚚 Pedido en camino',
        html: 'El pedido fue despachado y se notificó al cliente <strong>vía WhatsApp</strong>.',
        icon: 'success',
        timer: 3000,
        showConfirmButton: false,
        background: '#1e293b', color: '#fff'
      });
    } else if (nuevoEstado === 'EN_CAMINO' && !response.data.whatsapp_enviado) {
      Swal.fire({
        title: '🚚 Pedido en camino',
        text: 'El pedido fue despachado pero no se pudo notificar al cliente (sin WhatsApp).',
        icon: 'warning',
        timer: 3000,
        showConfirmButton: false,
        background: '#1e293b', color: '#fff'
      });
    } else {
      Swal.fire({ title: '¡Éxito!', icon: 'success', timer: 1000, showConfirmButton: false });
    }
    
    cargarPedidos();
  } catch (e) {
    const errorMsg = e.response?.data?.error || 'No se pudo actualizar el pedido.';
    Swal.fire({ title: 'Error', text: errorMsg, icon: 'error', background: '#1e293b', color: '#fff' });
  }
};



const rechazarSolicitud = async (pedido) => {
  if (!esAdmin.value) return;
  const { value: motivo } = await Swal.fire({
    title: 'Rechazar solicitud/incidencia',
    input: 'textarea',
    inputLabel: 'Indicá el motivo del rechazo',
    inputPlaceholder: 'Ej: El pedido ya fue preparado / no corresponde...',
    showCancelButton: true,
    confirmButtonText: 'Rechazar',
    confirmButtonColor: '#f59e0b',
    background: '#1e293b',
    color: '#fff',
    inputValidator: (v) => !v?.trim() ? 'Debés indicar un motivo.' : undefined,
  });
  if (!motivo) return;
  try {
    const token = localStorage.getItem('token');
    await axios.post(`${API_URL}${pedido.id}/rechazar_cancelacion/`, { motivo }, { headers: { 'Authorization': `Token ${token}` } });
    Swal.fire({ title: 'Rechazada', icon: 'success', timer: 1200, showConfirmButton: false });
    cargarPedidos();
  } catch (e) {
    Swal.fire({ title: 'Error', text: e.response?.data?.error || 'No se pudo rechazar.', icon: 'error', background: '#1e293b', color: '#fff' });
  }
};

const copiarTexto = async (texto, label = 'Texto', btnId = null) => {
  const setBtnFeedback = (msg, ok = true) => {
    if (!btnId) return false;
    const btn = document.getElementById(btnId);
    if (!btn) return false;
    const prev = btn.textContent;
    btn.textContent = msg;
    btn.style.background = ok ? '#10b981' : '#ef4444';
    btn.disabled = true;
    setTimeout(() => {
      if (!document.getElementById(btnId)) return;
      btn.textContent = prev;
      btn.style.background = '#0ea5e9';
      btn.disabled = false;
    }, 1600);
    return true;
  };

  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(String(texto));
    } else {
      const ta = document.createElement('textarea');
      ta.value = String(texto);
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
    }
    if (!setBtnFeedback(`${label} copiado`, true)) {
      Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: `${label} copiado`, showConfirmButton: false, timer: 1600, background: '#1e293b', color: '#fff' });
    }
  } catch {
    if (!setBtnFeedback('No se pudo copiar', false)) {
      Swal.fire({ icon: 'error', title: 'No se pudo copiar', text: 'Copialo manualmente.', background: '#1e293b', color: '#fff' });
    }
  }
};

const mostrarModalDevolucionManual = async (pedido, { modo = 'postAprobacion' } = {}) => {
  if (!esAdmin.value) {
    await Swal.fire({ title: 'Permiso requerido', text: 'Solo un administrador puede confirmar devoluciones manuales.', icon: 'warning', background: '#1e293b', color: '#fff' });
    return;
  }

  const fmtARS = (n) => `$${Number(n || 0).toLocaleString('es-AR')}`;
  const pedidoCtx = { ...pedido };

  const obtenerPedidoActual = () => pedidos.value.find(p => p.id === pedidoCtx.id) || pedidoCtx;

  const renderHtml = (p) => {
    const estado = p.reembolso_estado || 'PENDIENTE';
    const yaConfirmado = estado === 'MANUAL';
    const puedeConfirmar = estado === 'PENDIENTE' && !!p.mp_payment_id;
    return `
      <div style="text-align:left; font-family:Inter,sans-serif;">
        <div style="background:rgba(15,23,42,0.65); border:1px solid #334155; border-radius:14px; padding:14px; margin-bottom:14px;">
          <p style="margin:0 0 8px; color:#cbd5e1;"><strong style="color:#f8fafc;">Pedido:</strong> #${p.id}</p>
          <p style="margin:0 0 8px; color:#cbd5e1;"><strong style="color:#f8fafc;">Cliente:</strong> ${escapeHtml(p.cliente_nombre || '-')}</p>
          <p style="margin:0 0 10px; color:#cbd5e1;"><strong style="color:#f8fafc;">Importe pagado:</strong> <span style="color:#10b981; font-size:1.35rem; font-weight:900;">${fmtARS(p.reembolso_monto || p.total)}</span></p>
          <div style="background:#0f172a; border:1px solid #0ea5e9; border-radius:12px; padding:12px;">
            <div style="color:#94a3b8; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.6px; font-weight:800; margin-bottom:6px;">ID de pago de Mercado Pago</div>
            <div id="mp-payment-id-display" style="color:#f8fafc; font-size:1.8rem; font-weight:900; letter-spacing:0.5px; word-break:break-all; line-height:1.2; margin-bottom:10px;">${escapeHtml(p.mp_payment_id || 'Sin ID de pago')}</div>
            <button type="button" id="btn-copiar-mp-id" ${p.mp_payment_id ? '' : 'disabled'} style="background:#0ea5e9; color:white; border:none; border-radius:10px; padding:10px 14px; font-weight:800; cursor:pointer; width:100%;">COPIAR ID DE PAGO</button>
          </div>
        </div>
        <div style="background:rgba(245,158,11,0.10); border:1px solid rgba(245,158,11,0.45); border-radius:12px; padding:12px; margin-bottom:14px; color:#fde68a; font-size:0.88rem; line-height:1.45;">
          <strong>Advertencia:</strong> antes de confirmar, verificá que Mercado Pago haya procesado efectivamente la devolución manual. Confirmá solo cuando la devolución ya esté realizada.
        </div>
        ${yaConfirmado ? `<div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.35); border-radius:12px; padding:12px; color:#86efac; font-weight:700;">Devolución manual ya confirmada.</div>` : ''}
        ${!p.mp_payment_id ? `<div style="background:rgba(148,163,184,0.1); border:1px solid rgba(148,163,184,0.35); border-radius:12px; padding:12px; color:#cbd5e1;">Este pedido no tiene ID de pago de Mercado Pago.</div>` : ''}
        ${!puedeConfirmar && !yaConfirmado ? `<div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.35); border-radius:12px; padding:12px; color:#fecaca; font-size:0.85rem;">Este pedido no tiene una devolución manual pendiente de confirmación.</div>` : ''}
      </div>
    `;
  };

  const abrir = async () => {
    const actual = obtenerPedidoActual();
    const estado = actual.reembolso_estado || 'PENDIENTE';
    const yaConfirmado = estado === 'MANUAL';
    const puedeConfirmar = esAdmin.value && estado === 'PENDIENTE' && !!actual.mp_payment_id;

    const resultado = await Swal.fire({
      title: modo === 'postAprobacion' ? 'Cancelación aprobada - Devolución manual' : 'Devolución manual en Mercado Pago',
      width: 720,
      html: renderHtml(actual),
      showCancelButton: true,
      showConfirmButton: puedeConfirmar,
      confirmButtonText: 'CONFIRMAR DEVOLUCIÓN REALIZADA',
      cancelButtonText: yaConfirmado ? 'Cerrar' : 'Más tarde',
      confirmButtonColor: '#10b981',
      cancelButtonColor: '#475569',
      background: '#1e293b',
      color: '#fff',
      allowOutsideClick: false,
      allowEscapeKey: yaConfirmado,
      customClass: { confirmButton: 'swal-confirmar-devolucion-btn' },
      didOpen: () => {
        const btn = document.getElementById('btn-copiar-mp-id');
        if (btn && actual.mp_payment_id) {
          btn.addEventListener('click', async (ev) => {
            ev.preventDefault();
            ev.stopPropagation();
            await copiarTexto(actual.mp_payment_id, 'ID de pago', 'btn-copiar-mp-id');
          });
        }
      },
      preConfirm: async () => {
        const pedidoActual = obtenerPedidoActual();
        if (!esAdmin.value) {
          Swal.showValidationMessage('Solo un administrador puede confirmar devoluciones manuales.');
          return false;
        }
        if (pedidoActual.reembolso_estado === 'MANUAL') {
          Swal.showValidationMessage('Esta devolución ya fue confirmada anteriormente.');
          return false;
        }
        if (pedidoActual.reembolso_estado !== 'PENDIENTE' || !pedidoActual.mp_payment_id) {
          Swal.showValidationMessage('El pedido no tiene una devolución manual pendiente de confirmación.');
          return false;
        }

        try {
          const token = localStorage.getItem('token');
          const res = await axios.post(`${API_URL}${pedidoActual.id}/confirmar_devolucion_manual/`, {}, { headers: { 'Authorization': `Token ${token}` } });
          return res.data;
        } catch (e) {
          const data = e.response?.data || {};
          const msg = data.error || 'No se pudo confirmar la devolución.';
          Swal.showValidationMessage(msg);
          // Si quedó confirmada por otra vía, refrescar para reflejar estado real.
          if (e.response?.status === 409 || data.reembolso_estado === 'MANUAL' || data.codigo === 'CAJA_CERRADA') {
            await cargarPedidos();
            const actualizado = obtenerPedidoActual();
            const yaConfirmado = actualizado.reembolso_estado === 'MANUAL';
            Swal.update({
              html: renderHtml(actualizado),
              showConfirmButton: !yaConfirmado && actualizado.reembolso_estado === 'PENDIENTE' && !!actualizado.mp_payment_id,
              cancelButtonText: yaConfirmado ? 'Cerrar' : 'Más tarde',
            });
            setTimeout(() => {
              const btn = document.getElementById('btn-copiar-mp-id');
              if (btn && actualizado.mp_payment_id) {
                btn.addEventListener('click', async (ev) => {
                  ev.preventDefault(); ev.stopPropagation();
                  await copiarTexto(actualizado.mp_payment_id, 'ID de pago', 'btn-copiar-mp-id');
                });
              }
            }, 0);
          }
          return false;
        }
      }
    });

    if (resultado.isConfirmed && resultado.value) {
      const data = resultado.value;
      await cargarPedidos();
      await Swal.fire({
        title: 'Devolución registrada',
        text: `Se registró la devolución MANUAL por ${fmtARS(data.reembolso_monto || actual.reembolso_monto || actual.total)} y el egreso en caja.`,
        icon: 'success',
        background: '#1e293b',
        color: '#fff'
      });
      return;
    }

    // "Más tarde" / cerrar: no navegar, solo dejar pendiente recuperable desde el listado.
    if (resultado.isDismissed && !yaConfirmado) {
      await cargarPedidos();
    }
  };

  await abrir();
};

// Aprobar cancelación solicitada por cliente (solo Administrador)
const aprobarCancelacionCliente = async (pedido) => {
  if (!esAdmin.value) {
    await Swal.fire('Permiso requerido', 'Solo un administrador puede aprobar cancelaciones y procesar reembolsos.', 'warning');
    return;
  }

  const infoMotivoSolicitud = extraerMotivoYObservacion(pedido.solicitud_cancelacion_motivo || pedido.incidencia_motivo || pedido.obs_cancelacion);
  const { value: form } = await Swal.fire({
    title: 'Aprobar cancelación',
    html: `
      <div style="text-align:left; font-family:Inter,sans-serif;">
        <div style="background: rgba(15,23,42,0.6); padding: 14px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 12px;">
          <p style="margin:0 0 6px 0; color:#f8fafc;"><strong>Cliente:</strong> ${escapeHtml(pedido.cliente_nombre || '-')}</p>
          <p style="margin:0 0 6px 0; color:#f8fafc;"><strong>Estado actual:</strong> ${escapeHtml(formatearEstadoPedido(pedido.estado, pedido.estado_display))}</p>
          <p style="margin:0 0 6px 0; color:#f8fafc;"><strong>Pago Mercado Pago:</strong> ${escapeHtml(pedido.mp_payment_id || 'No corresponde / sin Mercado Pago')}</p>
          <p style="margin:0; color:#10b981; font-size:1.1rem; font-weight:700;">Total: $${Number(pedido.total).toLocaleString('es-AR')}</p>
        </div>
        <p style="color:#cbd5e1; font-size:0.9rem; margin-bottom:8px;"><strong>Motivo:</strong> ${escapeHtml(infoMotivoSolicitud.motivo || 'Sin motivo')}</p>
        ${infoMotivoSolicitud.observacion ? `<p style="color:#94a3b8; font-size:0.85rem; margin:0 0 8px;"><strong style="color:#cbd5e1;">Observación adicional:</strong> ${escapeHtml(infoMotivoSolicitud.observacion)}</p>` : ''}
        <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.35); border-radius:10px; padding:10px; color:#bbf7d0; font-size:0.85rem; margin-bottom:10px;">
          Al aprobar, el stock se devolverá automáticamente al inventario.
        </div>
        ${pedido.mp_payment_id ? `<div style="background:rgba(14,165,233,0.08); border:1px solid rgba(14,165,233,0.35); border-radius:10px; padding:10px; color:#bae6fd; font-size:0.85rem;">La devolución se hará <strong>manualmente en Mercado Pago</strong>. Tras aprobar, se te mostrará el ID de pago para copiarlo y luego confirmar la devolución realizada.</div>` : ''}
        <label style="color:#f8fafc; font-weight:700; display:block; margin:10px 0 6px;">Observación del administrador (opcional)</label>
        <textarea id="swal-obs-aprob" class="swal2-textarea" style="width:100%; margin:0; background:#0f172a; color:white; border:1px solid #334155; height:80px;" placeholder="Podés agregar una observación interna"></textarea>
      </div>
    `,
    showCancelButton: true,
    confirmButtonColor: '#10b981',
    confirmButtonText: 'Aprobar cancelación',
    cancelButtonText: 'Volver',
    background: '#1e293b',
    color: '#fff',
    preConfirm: () => ({
      obs_cancelacion: (document.getElementById('swal-obs-aprob')?.value || '').trim(),
    })
  });

  if (!form) return;
  try {
    Swal.fire({ title: 'Procesando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
    const token = localStorage.getItem('token');
    const res = await axios.post(`${API_URL}${pedido.id}/aprobar_cancelacion/`, form, { headers: { 'Authorization': `Token ${token}` } });
    await cargarPedidos();
    const pedidoActualizado = pedidos.value.find(p => p.id === pedido.id) || { ...pedido, ...res.data, estado: 'CANCELADO' };

    if (pedidoActualizado.mp_payment_id && (res.data?.reembolso_estado === 'PENDIENTE' || pedidoActualizado.reembolso_estado === 'PENDIENTE')) {
      // Mantener la operación continua: abrir modal de devolución manual inmediatamente.
      await mostrarModalDevolucionManual(pedidoActualizado, { modo: 'postAprobacion' });
      return;
    }

    await Swal.fire({ title: 'Cancelación aprobada', text: `Reembolso: ${formatearReembolsoEstado(res.data?.reembolso_estado) || 'No corresponde devolución'}. Stock devuelto: ${res.data?.stock_devuelto ? 'Sí' : 'No / pendiente verificación'}`, icon: 'success', background: '#1e293b', color: '#fff' });
  } catch (e) {
    Swal.fire({ title: 'Error', text: e.response?.data?.error || 'No se pudo aprobar.', icon: 'error', background: '#1e293b', color: '#fff' });
  }
};

const ESTADO_HISTORIAL_LABELS = {
  PENDIENTE_PAGO: 'Esperando pago',
  PAGADO: 'Pagado',
  EN_PREPARACION: 'En preparación',
  LISTO_RETIRO: 'Listo para retirar',
  EN_CAMINO: 'En camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
  SOLICITA_CANCELACION: 'Solicitud de cancelación pendiente',
  INCIDENCIA: 'Incidencia'
};

const REEMBOLSO_LABELS = {
  PENDIENTE: 'Devolución pendiente',
  MANUAL: 'Devolución confirmada manualmente',
  NO_APLICA: 'No corresponde devolución',
  EXITOSO: 'Devolución realizada',
  FALLIDO: 'Devolución no realizada'
};

const escapeHtml = (value = '') => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#039;');

function extraerMotivoYObservacion(texto = '') {
  const raw = (texto || '').toString().trim();
  if (!raw) return { motivo: '', observacion: '', observacionAdmin: '' };
  const limpio = raw
    .replace(/^SOLICITUD DE CLIENTE:\s*/i, '')
    .replace(/^INCIDENCIA DE CLIENTE:\s*/i, '')
    .replace(/^INCIDENCIA REGISTRADA POR [^:]+:\s*/i, '')
    .replace(/^SOLICITUD REGISTRADA POR [^:]+:\s*/i, '')
    .replace(/^Cancelación directa del cliente:\s*/i, '')
    .trim();

  const adminMatch = limpio.match(/^(.*?)(?:\n+Observaci[oó]n del administrador\s*:\s*)([\s\S]*)$/i);
  let base = limpio;
  let observacionAdmin = '';
  if (adminMatch) {
    base = (adminMatch[1] || '').trim();
    observacionAdmin = (adminMatch[2] || '').trim();
  }

  const match = base.match(/^(.*?)(?:\n+Observaci[oó]n(?: adicional)?\s*:\s*)([\s\S]*)$/i);
  if (match) {
    return { motivo: (match[1] || '').trim(), observacion: (match[2] || '').trim(), observacionAdmin };
  }
  return { motivo: base, observacion: '', observacionAdmin };
}

const formatearEstadoHistorial = (estado) => {
  if (!estado || estado === '-') return '';
  return ESTADO_HISTORIAL_LABELS[estado] || String(estado).replace(/_/g, ' ');
};

const formatearEstadoPedido = (estado, display = '') => {
  const d = (display || '').toString().trim();
  if (d && !/^[A-Z_]+$/.test(d)) return d;
  return formatearEstadoHistorial(estado) || d || '-';
};

const formatearReembolsoEstado = (estado) => {
  if (!estado) return '';
  return REEMBOLSO_LABELS[estado] || String(estado).replace(/_/g, ' ');
};

const normalizarDetalleHistorial = (detalles) => {
  if (detalles === null || detalles === undefined) return '';
  if (typeof detalles === 'string') {
    const txt = detalles.trim();
    if (!txt || txt === '-' || /^-\s*→\s*-?$/.test(txt)) return '';
    if (txt === '[object Object]') return '';
    return txt;
  }
  if (Array.isArray(detalles)) {
    return detalles.map(normalizarDetalleHistorial).filter(Boolean).join(' · ');
  }
  if (typeof detalles === 'object') {
    const entries = Object.entries(detalles)
      .filter(([_, v]) => v !== null && v !== undefined && String(v).trim() !== '' && String(v) !== '[object Object]')
      .map(([k, v]) => {
        const label = k.replace(/_/g, ' ');
        const val = typeof v === 'object' ? normalizarDetalleHistorial(v) : String(v).trim();
        return val ? `${label}: ${val}` : '';
      })
      .filter(Boolean);
    return entries.join(' · ');
  }
  const txt = String(detalles).trim();
  return txt && txt !== '[object Object]' ? txt : '';
};

const etiquetaTransicion = (anterior, nuevo) => {
  const key = `${anterior}|${nuevo}`;
  const extras = {
    'PENDIENTE_PAGO|PAGADO': 'A preparar',
    'PAGADO|EN_PREPARACION': 'En preparación',
    'EN_PREPARACION|LISTO_RETIRO': 'Listo para retirar',
    'EN_PREPARACION|EN_CAMINO': 'Despachado',
    'LISTO_RETIRO|ENTREGADO': 'Entregado',
    'EN_CAMINO|ENTREGADO': 'Entregado'
  };
  const base = `${formatearEstadoHistorial(anterior)} → ${formatearEstadoHistorial(nuevo)}`;
  return extras[key] ? `${base} - ${extras[key]}` : base;
};

const descripcionHistorial = (item) => {
  const anterior = item.estado_anterior;
  const nuevo = item.estado_nuevo;
  const anteriorLabel = formatearEstadoHistorial(anterior);
  const nuevoLabel = formatearEstadoHistorial(nuevo);
  const accion = (item.accion || '').toString().toUpperCase();
  const detalle = normalizarDetalleHistorial(item.detalles);

  if (anteriorLabel && nuevoLabel && anteriorLabel !== nuevoLabel) {
    if (nuevo === 'CANCELADO' && accion.includes('APROB')) return `${anteriorLabel} → ${nuevoLabel} - Cancelación aprobada`;
    if (nuevo === 'CANCELADO') return `${anteriorLabel} → ${nuevoLabel}`;
    if (nuevo === 'SOLICITA_CANCELACION') return `${anteriorLabel} → ${nuevoLabel}`;
    if (nuevo === 'INCIDENCIA') return `${anteriorLabel} → ${nuevoLabel}`;
    return etiquetaTransicion(anterior, nuevo);
  }

  if (accion.includes('REEMBOLSO') || accion.includes('DEVOLUCION')) return 'Actualización de devolución';
  if (accion.includes('RECHAZ')) return 'Solicitud/incidencia rechazada';
  if (accion.includes('APROB')) return 'Cancelación aprobada';
  if (accion.includes('SOLICITUD')) return 'Solicitud de cancelación registrada';
  if (accion.includes('INCIDENCIA')) return 'Incidencia registrada';
  if (accion.includes('CANCEL')) return 'Pedido cancelado';
  if (nuevoLabel) return `Actualización: ${nuevoLabel}`;
  if (anteriorLabel) return `Actualización desde ${anteriorLabel}`;
  if (detalle) return 'Registro de seguimiento';
  return '';
};

const legibilizarTextoHistorial = (txt = '') => String(txt)
  .replace(/\bSOLICITA_CANCELACION\b/g, 'Solicitud de cancelación pendiente')
  .replace(/\bNO_APLICA\b/g, 'No corresponde devolución')
  .replace(/\bREEMBOLSO_PENDIENTE\b/g, 'Devolución pendiente')
  .replace(/\bREEMBOLSO_MANUAL\b/g, 'Devolución confirmada manualmente')
  .replace(/\bREEMBOLSO_EXITOSO\b/g, 'Devolución realizada')
  .replace(/\bREEMBOLSO_FALLIDO\b/g, 'Devolución no realizada')
  .replace(/\bPENDIENTE\b/g, 'Devolución pendiente')
  .replace(/\bMANUAL\b/g, 'Devolución confirmada manualmente')
  .replace(/\bEXITOSO\b/g, 'Devolución realizada')
  .replace(/\bFALLIDO\b/g, 'Devolución no realizada');

const detalleHistorial = (item) => {
  const detalle = normalizarDetalleHistorial(item.detalles);
  if (!detalle) return '';
  const anterior = formatearEstadoHistorial(item.estado_anterior);
  const nuevo = formatearEstadoHistorial(item.estado_nuevo);
  const transicionSimple = anterior && nuevo ? `${anterior} → ${nuevo}` : '';
  const legible = legibilizarTextoHistorial(detalle);
  if (legible === transicionSimple) return '';
  return legible;
};

const claveOperacionHistorial = (h) => {
  const accion = (h.raw?.accion || '').toString().toUpperCase();
  const nuevo = h.raw?.estado_nuevo || '';
  const titulo = h.titulo.toLowerCase();
  const fechaMin = h.fechaDate ? new Date(h.fechaDate).toISOString().slice(0, 16) : h.fecha;
  if (accion.includes('SOLICITUD') || titulo.includes('solicitud de cancelación')) return `solicitud|${h.usuario}|${fechaMin}`;
  if (accion.includes('INCIDENCIA') || titulo.includes('incidencia')) return `incidencia|${h.usuario}|${fechaMin}`;
  if (accion.includes('REEMBOLSO') || titulo.includes('reembolso')) return `reembolso|${h.usuario}|${fechaMin}|${h.detalle}`;
  return `${titulo}|${h.detalle}|${h.usuario}|${fechaMin}|${nuevo}`;
};

const construirHistorialHTML = (historial) => {
  const vistos = new Set();
  const items = (Array.isArray(historial) ? historial : [])
    .map((h) => {
      const titulo = descripcionHistorial(h);
      const detalle = detalleHistorial(h);
      const usuario = (h.usuario || 'Sistema').toString().trim() || 'Sistema';
      const fechaDate = h.fecha ? new Date(h.fecha) : null;
      const fecha = fechaDate && !Number.isNaN(fechaDate.getTime()) ? fechaDate.toLocaleString('es-AR') : '-';
      return { titulo, detalle, usuario, fecha, fechaDate, raw: h };
    })
    .filter((h) => h.titulo)
    .filter((h) => {
      const key = claveOperacionHistorial(h);
      if (vistos.has(key)) return false;
      vistos.add(key);
      return true;
    });

  const listaHTML = items.length ? items.map((h, idx) => `
        <div style="padding: 10px 0; ${idx < items.length - 1 ? 'border-bottom: 1px solid #334155;' : ''} font-size: 0.86rem;">
          <div style="color:#f8fafc; font-weight:700; line-height:1.35;">${escapeHtml(h.titulo)}</div>
          ${h.detalle ? `<div style="color:#cbd5e1; margin-top:3px; line-height:1.4;">${escapeHtml(h.detalle)}</div>` : ''}
          <div style="color:#94a3b8; margin-top:3px; font-size:0.8rem;">${escapeHtml(h.usuario)} · ${escapeHtml(h.fecha)}</div>
        </div>
      `).join('') : `<p style="margin:0; color:#94a3b8; font-size:0.86rem;">Todavía no hay cambios relevantes registrados.</p>`;

  return `
    <details style="background: rgba(15, 23, 42, 0.6); border-radius: 14px; border: 1px solid #334155; overflow:hidden;">
      <summary style="cursor:pointer; padding: 14px 16px; color:#38bdf8; font-weight:800; text-transform:uppercase; font-size:0.8rem; letter-spacing:0.5px; list-style:none; display:flex; align-items:center; justify-content:space-between; gap:10px;">
        <span>Historial de cambios</span>
        <span style="color:#94a3b8; font-size:0.72rem; font-weight:700; text-transform:none;">${items.length} registro${items.length === 1 ? '' : 's'}</span>
      </summary>
      <div style="padding: 0 16px 14px 16px; border-top:1px solid #334155;">
        ${listaHTML}
      </div>
    </details>
  `;
};

const verDetalle = async (p) => {
    let historial = [];
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}${p.id}/historial/`, { headers: { 'Authorization': `Token ${token}` } });
      historial = Array.isArray(res.data) ? res.data : [];
    } catch (e) {
      historial = [];
    }

    const fmtARS = (n) => `$${Number(n || 0).toLocaleString('es-AR')}`;
    const estadoLabel = formatearEstadoPedido(p.estado, p.estado_display);
    const estadoClase = getEstadoClass(p.estado);
    const estadoColorMap = {
      'estado-info': '#38bdf8',
      'estado-warning': '#fbbf24',
      'estado-success': '#34d399',
      'estado-completado': '#22c55e',
      'estado-cancelado': '#f87171',
      'estado-solicitud': '#fb923c',
      'estado-incidencia': '#fde047',
      'estado-secondary': '#94a3b8'
    };
    const estadoColor = estadoColorMap[estadoClase] || '#94a3b8';

    const dirEntrega = p.calle_entrega
      ? [p.calle_entrega, p.altura_entrega].filter(Boolean).join(' ') + (p.ciudad_entrega ? `, ${p.ciudad_entrega}` : '') + (p.provincia_entrega ? `, ${p.provincia_entrega}` : '')
      : (p.direccion_envio || '');
    const direccionTexto = p.tipo_entrega === 'RETIRO' ? 'Retiro en local' : (dirEntrega || 'Sin dirección informada');
    const choferTexto = p.tipo_entrega === 'RETIRO' ? 'No aplica' : (p.datos_entrega_interna || 'Aún no asignado');

    const itemsRows = (p.detalles || []).map((d, i) => `
      <tr>
        <td style="padding:8px 10px; border-bottom:1px solid #334155; color:#f8fafc; font-size:0.86rem;">${escapeHtml(d.nombre_producto || '-')}</td>
        <td style="padding:8px 10px; border-bottom:1px solid #334155; color:#cbd5e1; text-align:center; font-size:0.86rem; white-space:nowrap;">${Number(d.cantidad || 0)}</td>
        <td style="padding:8px 10px; border-bottom:1px solid #334155; color:#94a3b8; text-align:right; font-size:0.86rem; white-space:nowrap;">${fmtARS(d.precio_unitario)}</td>
        <td style="padding:8px 10px; border-bottom:1px solid #334155; color:#38bdf8; font-weight:700; text-align:right; font-size:0.86rem; white-space:nowrap;">${fmtARS(Number(d.cantidad || 0) * Number(d.precio_unitario || 0))}</td>
      </tr>
    `).join('');

    const historialHTML = construirHistorialHTML(historial);

    // extraerMotivoYObservacion definido a nivel de módulo

    const solicitudInfo = extraerMotivoYObservacion(p.solicitud_cancelacion_motivo);
    const incidenciaInfo = extraerMotivoYObservacion(p.incidencia_motivo);
    const motivoInfo = extraerMotivoYObservacion(p.motivo_cancelacion);
    const obsInfo = extraerMotivoYObservacion(p.obs_cancelacion);
    const tieneSolicitudCliente = !!(solicitudInfo.motivo || incidenciaInfo.motivo);
    const motivoCancelacion = solicitudInfo.motivo || incidenciaInfo.motivo || motivoInfo.motivo || obsInfo.motivo;
    let obsCancelacion = solicitudInfo.observacion || incidenciaInfo.observacion || motivoInfo.observacion || obsInfo.observacion || ((obsInfo.motivo && obsInfo.motivo !== motivoCancelacion && !obsInfo.observacionAdmin) ? obsInfo.motivo : '');
    let obsAdmin = obsInfo.observacionAdmin || solicitudInfo.observacionAdmin || incidenciaInfo.observacionAdmin || motivoInfo.observacionAdmin || '';
    // Cancelación directa administrativa: la observación almacenada es del administrador.
    if (!tieneSolicitudCliente && !obsAdmin && obsCancelacion) {
      obsAdmin = obsCancelacion;
      obsCancelacion = '';
    }
    const mostrarCancelBox = ['CANCELADO', 'SOLICITA_CANCELACION', 'INCIDENCIA'].includes(p.estado)
      || motivoCancelacion || obsCancelacion
      || (p.reembolso_estado && p.reembolso_estado !== 'NO_APLICA')
      || !!p.stock_devuelto;
    const cancelBorder = p.estado === 'INCIDENCIA' ? '#eab308' : (p.estado === 'SOLICITA_CANCELACION' ? '#fb923c' : '#ef4444');
    const cancelTitle = p.estado === 'INCIDENCIA' ? 'Incidencia' : (p.estado === 'SOLICITA_CANCELACION' ? 'Solicitud de cancelación' : 'Cancelación / Resolución');
    const reembolsoPendienteManual = p.estado === 'CANCELADO' && p.reembolso_estado === 'PENDIENTE' && !!p.mp_payment_id;
    const reembolsoManualConfirmado = p.reembolso_estado === 'MANUAL';
    const cancelBox = mostrarCancelBox ? `
      <div style="background: rgba(239, 68, 68, 0.06); border: 1px solid ${cancelBorder}; border-radius: 12px; padding: 12px 14px; margin-bottom: 14px;">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:8px;">
          <h4 style="color:${cancelBorder}; margin:0; text-transform:uppercase; font-size:0.78rem; font-weight:900; letter-spacing:0.4px;">${cancelTitle}</h4>
          <span style="color:#94a3b8; font-size:0.75rem;">${p.reembolso_estado ? `Reembolso: ${escapeHtml(formatearReembolsoEstado(p.reembolso_estado))}` : ''}</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px 14px; font-size:0.84rem;">
          <div style="color:#cbd5e1;"><strong style="color:#f8fafc;">Motivo:</strong> ${escapeHtml(motivoCancelacion || 'No especificado')}</div>
          <div style="color:#cbd5e1;"><strong style="color:#f8fafc;">Stock devuelto:</strong> ${p.stock_devuelto ? 'Sí' : 'No / pendiente verificación'}</div>
          <div style="grid-column:1 / -1; color:#cbd5e1;"><strong style="color:#f8fafc;">Observación del cliente:</strong> ${escapeHtml(obsCancelacion || 'Sin observación adicional')}</div>
          ${obsAdmin ? `<div style="grid-column:1 / -1; color:#cbd5e1;"><strong style="color:#f8fafc;">Observación del administrador:</strong> ${escapeHtml(obsAdmin)}</div>` : ''}
          ${p.reembolso_monto ? `<div style="color:#cbd5e1;"><strong style="color:#f8fafc;">Importe de devolución:</strong> <span style="color:#10b981; font-weight:700;">${fmtARS(p.reembolso_monto)}</span></div>` : ''}
          ${p.reembolso_fecha ? `<div style="color:#cbd5e1;"><strong style="color:#f8fafc;">Fecha de devolución:</strong> ${escapeHtml(new Date(p.reembolso_fecha).toLocaleString('es-AR'))}</div>` : ''}
          ${p.reembolso_error ? `<div style="grid-column:1 / -1; color:#fca5a5;"><strong style="color:#fecaca;">Observación de devolución:</strong> ${escapeHtml(p.reembolso_error)}</div>` : ''}
          ${(reembolsoPendienteManual || reembolsoManualConfirmado) ? `
            <div style="grid-column:1 / -1; background:#0f172a; border:1px solid ${reembolsoManualConfirmado ? 'rgba(16,185,129,0.45)' : 'rgba(14,165,233,0.45)'}; border-radius:10px; padding:10px;">
              <div style="color:#94a3b8; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.5px; font-weight:800; margin-bottom:4px;">ID de pago Mercado Pago</div>
              <div style="display:flex; gap:10px; align-items:center; justify-content:space-between; flex-wrap:wrap;">
                <div style="color:#f8fafc; font-size:1.15rem; font-weight:900; word-break:break-all;">${escapeHtml(p.mp_payment_id || '-')}</div>
                ${p.mp_payment_id ? `<button id="btn-copy-mp-detail" style="background:#0ea5e9; color:white; border:none; border-radius:8px; padding:8px 10px; font-weight:800; cursor:pointer;">COPIAR ID</button>` : ''}
              </div>
              <div style="margin-top:6px; color:${reembolsoManualConfirmado ? '#86efac' : '#fde68a'}; font-size:0.8rem; font-weight:700;">
                ${reembolsoManualConfirmado ? 'Devolución manual confirmada en HairSoft.' : 'Devolución pendiente: realizá el reembolso manual en MP y luego confirmalo en HairSoft.'}
              </div>
            </div>
          ` : ''}
        </div>
      </div>
    ` : '';

    Swal.fire({
        title: '',
        html: `
            <div style="text-align:left; font-size:0.92rem; color:#94a3b8; line-height:1.5; font-family:'Inter',sans-serif;">
                <div style="background:linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.75)); border:1px solid #334155; border-radius:14px; padding:14px 16px; margin-bottom:14px;">
                  <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px; flex-wrap:wrap;">
                    <div>
                      <div style="color:#94a3b8; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.7px; font-weight:800;">Detalle del pedido</div>
                      <div style="color:#f8fafc; font-size:1.3rem; font-weight:900; line-height:1.2; margin-top:2px;">Pedido #${p.id}</div>
                      <div style="color:#64748b; font-size:0.78rem; margin-top:4px;">${escapeHtml(formatearFecha(p.fecha_creacion))} ${escapeHtml(formatearHora(p.fecha_creacion))}</div>
                    </div>
                    <div style="text-align:right; display:flex; flex-direction:column; align-items:flex-end; gap:8px;">
                      <span style="display:inline-flex; align-items:center; padding:5px 10px; border-radius:999px; border:1px solid ${estadoColor}55; background:${estadoColor}1A; color:${estadoColor}; font-size:0.72rem; font-weight:800; text-transform:uppercase; letter-spacing:0.4px;">${escapeHtml(estadoLabel)}</span>
                      <div style="color:#10b981; font-size:1.35rem; font-weight:900; line-height:1;">${fmtARS(p.total)}</div>
                    </div>
                  </div>
                </div>

                ${cancelBox}

                <div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin-bottom:14px;">
                  <div style="background:rgba(15,23,42,0.55); padding:14px; border-radius:12px; border:1px solid #334155; min-width:0;">
                    <h4 style="color:#38bdf8; margin:0 0 10px 0; text-transform:uppercase; font-size:0.76rem; letter-spacing:0.5px; font-weight:800;">Cliente</h4>
                    <div style="font-size:0.84rem; color:#cbd5e1; margin-bottom:6px;"><strong style="color:#f8fafc;">Nombre:</strong> ${escapeHtml(p.cliente_nombre || '-')}</div>
                    <div style="font-size:0.84rem; color:#cbd5e1; word-break:break-word; margin-bottom:6px;"><strong style="color:#f8fafc;">Email:</strong> ${escapeHtml(p.cliente_email || '-')}</div>
                    <div style="font-size:0.8rem; color:#94a3b8;"><strong style="color:#cbd5e1;">Pago:</strong> ${p.mp_payment_id ? `MP ${escapeHtml(p.mp_payment_id)}` : 'Sin MP / no aplica'}</div>
                  </div>
                  <div style="background:rgba(15,23,42,0.55); padding:14px; border-radius:12px; border:1px solid #334155; min-width:0;">
                    <h4 style="color:#38bdf8; margin:0 0 10px 0; text-transform:uppercase; font-size:0.76rem; letter-spacing:0.5px; font-weight:800;">Logística</h4>
                    <div style="font-size:0.84rem; color:#cbd5e1; margin-bottom:6px;"><strong style="color:#f8fafc;">Forma:</strong> ${escapeHtml(p.tipo_entrega || '-')}</div>
                    <div style="font-size:0.84rem; color:#cbd5e1; margin-bottom:6px; word-break:break-word;"><strong style="color:#f8fafc;">Dirección:</strong> ${escapeHtml(direccionTexto)}</div>
                    <div style="font-size:0.84rem; color:#cbd5e1; margin-bottom:6px;"><strong style="color:#f8fafc;">Chofer:</strong> ${escapeHtml(choferTexto)}</div>
                    ${p.tiempo_estimado_minutos > 0 ? `<div style="font-size:0.8rem; color:#94a3b8; margin-bottom:6px;"><strong style="color:#cbd5e1;">Estimado:</strong> ~${escapeHtml(p.tiempo_estimado_minutos)} min</div>` : ''}
                    ${p.observaciones_entrega ? `<div style="font-size:0.8rem; color:#94a3b8; word-break:break-word;"><strong style="color:#cbd5e1;">Obs.:</strong> ${escapeHtml(p.observaciones_entrega)}</div>` : ''}
                  </div>
                </div>

                <div style="background:rgba(15,23,42,0.55); padding:14px; border-radius:12px; border:1px solid #334155; margin-bottom:14px;">
                  <h4 style="color:#38bdf8; margin:0 0 10px 0; text-transform:uppercase; font-size:0.76rem; letter-spacing:0.5px; font-weight:800;">Productos comprados</h4>
                  <div style="overflow:auto; border:1px solid #334155; border-radius:10px;">
                    <table style="width:100%; border-collapse:collapse; min-width:420px; background:rgba(15,23,42,0.35);">
                      <thead>
                        <tr style="background:rgba(51,65,85,0.35);">
                          <th style="text-align:left; padding:8px 10px; color:#94a3b8; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.4px; border-bottom:1px solid #334155;">Producto</th>
                          <th style="text-align:center; padding:8px 10px; color:#94a3b8; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.4px; border-bottom:1px solid #334155;">Cant.</th>
                          <th style="text-align:right; padding:8px 10px; color:#94a3b8; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.4px; border-bottom:1px solid #334155;">Unit.</th>
                          <th style="text-align:right; padding:8px 10px; color:#94a3b8; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.4px; border-bottom:1px solid #334155;">Subtotal</th>
                        </tr>
                      </thead>
                      <tbody>${itemsRows}</tbody>
                    </table>
                  </div>
                  <div style="margin-top:10px; display:flex; justify-content:flex-end;">
                    <div style="min-width:220px; background:#0f172a; border:1px solid #334155; border-radius:10px; padding:10px 12px;">
                      <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:#94a3b8; margin-bottom:4px;"><span>Subtotal</span><span style="color:#e2e8f0;">${fmtARS(Number(p.total) - Number(p.costo_envio || 0))}</span></div>
                      ${Number(p.costo_envio) > 0 ? `<div style="display:flex; justify-content:space-between; font-size:0.82rem; color:#94a3b8; margin-bottom:4px;"><span>Envío</span><span style="color:#38bdf8;">${fmtARS(p.costo_envio)}</span></div>` : ''}
                      <div style="display:flex; justify-content:space-between; font-size:0.95rem; color:#f8fafc; font-weight:800; border-top:1px solid #334155; padding-top:6px; margin-top:2px;"><span>Total</span><span style="color:#10b981;">${fmtARS(p.total)}</span></div>
                    </div>
                  </div>
                </div>

                ${historialHTML}
            </div>
        `,
        background: '#1e293b',
        color: '#fff',
        width: '760px',
        padding: '1rem 1rem 1.1rem',
        confirmButtonText: 'Cerrar',
        confirmButtonColor: '#0ea5e9',
        customClass: {
          popup: 'pedido-detalle-popup',
          htmlContainer: 'pedido-detalle-html'
        },
        didOpen: () => {
          const copyBtn = document.getElementById('btn-copy-mp-detail');
          if (copyBtn && p.mp_payment_id) {
            copyBtn.addEventListener('click', () => copiarTexto(p.mp_payment_id, 'ID de pago', 'btn-copy-mp-detail'));
          }
        }
    });
};

const pedidosFiltrados = computed(() => {
  if (filtroActual.value === 'TODOS') return pedidos.value;
  if (filtroActual.value === 'ACTIVOS') return pedidos.value.filter(p => !['ENTREGADO', 'CANCELADO'].includes(p.estado));
  return pedidos.value.filter(p => p.estado === filtroActual.value);
});

const totalPaginas = computed(() => Math.max(1, Math.ceil(pedidosFiltrados.value.length / itemsPorPagina)));
const pedidosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina;
  return pedidosFiltrados.value.slice(inicio, inicio + itemsPorPagina);
});

const paginaAnterior = () => { if (paginaActual.value > 1) paginaActual.value--; };
const paginaSiguiente = () => { if (paginaActual.value < totalPaginas.value) paginaActual.value++; };

const cambiarFiltro = (k) => { filtroActual.value = k; paginaActual.value = 1; };

const contarPorEstado = (k) => k === 'TODOS' ? pedidos.value.length : (k === 'ACTIVOS' ? pedidos.value.filter(p => !['ENTREGADO', 'CANCELADO'].includes(p.estado)).length : pedidos.value.filter(p => p.estado === k).length);

const getEstadoClass = (e) => {
  const mapa = { 
    'PAGADO': 'estado-info', 
    'EN_PREPARACION': 'estado-warning', 
    'LISTO_RETIRO': 'estado-success', 
    'EN_CAMINO': 'estado-success', 
    'ENTREGADO': 'estado-completado', 
    'CANCELADO': 'estado-cancelado',
    'SOLICITA_CANCELACION': 'estado-solicitud',
    'INCIDENCIA': 'estado-incidencia'
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
/* 🔥 NUEVO COLOR PARA SOLICITUD DE CANCELACIÓN */
.estado-solicitud { background: var(--bg-tertiary); color: #f97316; border-color: #f97316; box-shadow: 0 0 10px rgba(249, 115, 22, 0.2); }
.estado-incidencia { background: var(--bg-tertiary); color: #eab308; border-color: #eab308; box-shadow: 0 0 10px rgba(234, 179, 8, 0.2); }

/* ACCIONES */
.action-buttons {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
  min-width: 220px;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.action-group-main { width: 100%; }
.action-group-admin {
  width: 100%;
  padding-top: 6px;
  border-top: 1px dashed rgba(239, 68, 68, 0.25);
}

.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  transition: all 0.2s ease;
  background: var(--bg-tertiary);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.2px;
  white-space: nowrap;
}

.action-button svg { stroke: currentColor; }\n.action-button.is-primary { font-weight: 800; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }\n.action-button.action-cancel { margin-left: auto; }

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

/* 🔥 NUEVO BOTÓN DE REEMBOLSO */
.action-button.refund { border: 1px solid #10b981; color: #10b981; }
.action-button.refund:hover { background: #10b981; color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }


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

/* SWEETALERT DETALLE PEDIDO */
:deep(.pedido-detalle-popup) {
  border: 1px solid #334155;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
}
:deep(.pedido-detalle-html) {
  margin: 0 !important;
  padding: 0 !important;
  overflow-x: hidden;
}
:deep(.pedido-detalle-html details > summary::-webkit-details-marker) {
  display: none;
}
:deep(.pedido-detalle-html details[open] > summary span:last-child) {
  color: #38bdf8;
}
:deep(.swal-confirmar-devolucion-btn) {
  font-weight: 800 !important;
  letter-spacing: 0.3px;
  padding: 12px 18px !important;
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
  .action-buttons { min-width: 180px; gap: 6px; }\n  .action-group { gap: 6px; }\n  .action-button.action-cancel { margin-left: 0; }
  
  .pagination-container { flex-direction: column; gap: 15px; padding: 15px; }
  .pagination-button { width: 100%; justify-content: center; }
}

@media (max-width: 480px) {
  .list-card { padding: 18px; border-radius: 16px; }
  .header-content h1 { font-size: 1.4rem; }
  .users-table { display: block; overflow-x: auto; white-space: nowrap; }
  .badge-estado { font-size: 0.65rem; padding: 5px 10px; }
  .action-buttons { min-width: 100%; }\n  .action-group { width: 100%; }\n  .action-button { width: auto; height: auto; padding: 6px 10px; font-size: 0.72rem; }\n  .action-button.action-cancel { margin-left: 0; }
  .register-button { width: 100%; justify-content: center; }
  .filtros-estados { flex-direction: column; }
}
</style>