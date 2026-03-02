<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarModalAnular }">
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de ventas</h1>
          <p>Historial y administración de transacciones</p>
        </div>
        
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="irANotasCredito" class="register-button" style="background-color: #f59e0b; color: #fff;">
            <FileText :size="18" />
            Notas de Crédito
          </button>

          <button @click="generarReporteListado" class="register-button" style="background-color: #7c3aed;" :disabled="loadingPdf">
            <FileText :size="18" />
            {{ loadingPdf ? 'Generando...' : 'Exportar Listado' }}
          </button>

          <button @click="mostrarRegistrar = true" class="register-button">
            <Plus :size="18" />
            Registrar Venta
          </button>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Cliente, Usuario, ID de Venta" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Fecha desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Fecha hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Método Pago</label>
            <select v-model="filtros.metodoPago" class="filter-input select-dark">
              <option value="">Todos</option>
              <option value="EFECTIVO">Efectivo</option>
              <option value="TRANSFERENCIA">Transferencia</option>
              <option value="MERCADO_PAGO">Mercado Pago</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Tipo</label>
            <select v-model="filtros.tipo" class="filter-input select-dark">
              <option value="">Todos</option>
              <option value="PRODUCTO">Producto</option>
              <option value="TURNO">Turno</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input select-dark">
              <option value="">Todos</option>
              <option value="activa">Activa</option>
              <option value="anulada">Anulada</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              <Trash2 :size="16" />
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>

      <div v-if="cargando" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Cargando ventas...</p>
      </div>

      <div v-else class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th style="width: 80px;">ID</th> <th style="width: 140px;">Fecha</th>
              <th>Cliente</th>
              <th>Usuario</th>
              <th>Total</th>
              <th>Método Pago</th> 
              <th>Tipo</th>
              <th>Estado</th>
              <th style="width: 60px; text-align: center;">PDF</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="venta in ventasPaginadas" :key="venta.id" 
                :class="{'venta-anulada-row': venta.anulada}">
              
              <td><strong>#{{ venta.id }}</strong></td> <td class="fecha-cell">
                <span class="fecha-dia">{{ formatFechaDia(venta.fecha) }}</span>
                <span class="fecha-hora">{{ formatFechaHora(venta.fecha) }}</span>
              </td>

              <td><strong>{{ venta.cliente_nombre || 'Venta Rápida' }}</strong></td>
              
              <td class="usuario-cell">{{ venta.usuario_nombre || '–' }}</td>
              
              <td class="total-cell">${{ formatPrecio(venta.total) }}</td>
              
              <td>
                <span class="badge-pago" :class="getMedioPagoInfo(venta).clase">
                  <component :is="getMedioPagoInfo(venta).icono" :size="12" />
                  {{ venta.medio_pago_nombre || '–' }}
                </span>
              </td>

              <td>
                <span class="badge-tipo" :class="getClaseTipoVenta(venta.tipo)">
                  {{ venta.tipo || '–' }}
                </span>
              </td>
              <td>
                <span class="badge-estado" :class="getClaseEstadoVenta(venta.anulada)">
                  {{ venta.anulada ? 'ANULADA' : 'ACTIVA' }}
                </span>
              </td>
              
              <td style="text-align: center;">
                <button 
                  @click="generarComprobantePDF(venta)" 
                  class="btn-pdf-icon"
                  :title="`Descargar comprobante #${venta.id}`"
                  :disabled="generandoPDF === venta.id || venta.anulada"
                >
                  <Loader v-if="generandoPDF === venta.id" :size="18" class="spin" />
                  <FileText v-else :size="18" />
                </button>
              </td>

              <td>
                <div class="action-buttons">
                  <button 
                    @click="abrirModalAnular(venta)" 
                    class="action-button delete" 
                    :disabled="venta.anulada || venta.tipo === 'TURNO'"
                    :title="venta.tipo === 'TURNO' ? 'No se puede anular un turno completado' : 'Anular Venta'"
                  >
                    <Trash2 :size="14" />
                  </button>
                  <button 
                    @click="verDetallesVenta(venta.id)" 
                    class="action-button detalle"
                    title="Ver Detalle y Auditoría"
                  >
                    <Eye :size="14" />
                  </button>

                  <button 
                    v-if="venta.anulada" 
                    @click="verMotivoAnulacion(venta)" 
                    class="action-button anulada-info" 
                    title="Ver auditoría de anulación"
                  >
                    <Info :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="ventasPaginadas.length === 0 && !cargando" class="no-results">
          <PackageX class="no-results-icon" :size="48" />
          <p>No se encontraron ventas</p>
          <button @click="cargarVentas" class="btn-reintentar">
            <RefreshCw :size="16" />
            Recargar
          </button>
        </div>
      </div>

      <div v-if="!cargando" class="list-footer">
        <div class="footer-left">
          <p class="count-text">
            Mostrando <strong>{{ ventasPaginadas.length }}</strong> de <strong>{{ ventasFiltradas.length }}</strong> ventas
          </p>
          
          <div class="alertas-container">
            <span v-if="ventasAnuladas > 0" class="alerta-bad">
              <AlertTriangle :size="14" />
              {{ ventasAnuladas }} anuladas
            </span>
            <span v-if="ventaRecienCreada" class="alerta-good">
              <CheckCircle :size="14" />
              Nueva venta (#{{ ventaRecienCreada }})
            </span>
          </div>
        </div>

        <div v-if="totalPaginas > 1" class="pagination">
          <button @click="paginaAnterior" :disabled="pagina === 1" class="page-btn">
            <ChevronLeft :size="18" />
          </button>
          <span class="page-info">Página {{ pagina }} de {{ totalPaginas }}</span>
          <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="page-btn">
            <ChevronRight :size="18" />
          </button>
        </div>
      </div>
    </div>

    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <RegistrarVenta 
          @venta-registrada="procesarVentaRegistrada" 
          @venta-completada="cerrarModal"
          @cancelar="cerrarModal"
        />
      </div>
    </div>

    <div v-if="mostrarModalAnular" class="modal-overlay" @click.self="cerrarModalAnular">
      <div class="modal-content-anular">
        <h2>Anular Venta #{{ ventaAAnular?.id }}</h2>
        <p class="anular-warning">Atención: Esta acción devolverá el stock y generará una Nota de Crédito. <b>No se puede deshacer.</b></p>
        
        <div class="form-group">
          <label style="font-weight: bold; margin-bottom: 8px; display: block;">Motivo de la anulación:</label>
          <select v-model="motivoSeleccionado" class="filter-input select-dark w-full" style="margin-bottom: 12px;">
            <option value="Error en método de pago">Error en método de pago</option>
            <option value="Fondos insuficientes del cliente">Fondos insuficientes del cliente</option>
            <option value="Cliente se arrepintió de la compra">Cliente se arrepintió de la compra</option>
            <option value="Carga duplicada por error">Carga duplicada por error</option>
            <option value="Error al seleccionar los productos">Error al seleccionar los productos</option>
            <option value="Otro">Otro motivo (Especifique)</option>
          </select>
        </div>

        <div class="form-group" v-if="motivoSeleccionado === 'Otro'">
          <label style="font-size: 0.85rem; color: var(--text-secondary);">Especifique el motivo (Mín. 5 caracteres):</label>
          <textarea 
            v-model="motivoAnulacion" 
            rows="3" 
            placeholder="Escriba aquí la razón de la anulación..."
            class="filter-input w-full mt-2"
          ></textarea>
        </div>

        <div class="modal-actions-anular">
          <button @click="cerrarModalAnular" class="btn-cancelar">Cancelar</button>
          <button 
            @click="confirmarAnulacion" 
            class="btn-confirmar-anular"
            :disabled="!esMotivoValido || cargandoAnulacion"
          >
            <Loader v-if="cargandoAnulacion" :size="16" class="spin" style="margin-right: 5px;"/>
            {{ cargandoAnulacion ? 'Anulando...' : 'Confirmar Anulación' }}
          </button>
        </div>
      </div>
    </div>

    <div id="print-template" style="display: none;"></div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axiosConfig' 
import Swal from 'sweetalert2'
import RegistrarVenta from './RegistrarVenta.vue'
import { 
  Plus, Trash2, Eye, FileText, Loader, PackageX,
  ChevronLeft, ChevronRight, RefreshCw, AlertTriangle, CheckCircle,
  CreditCard, Banknote, Smartphone, ArrowRightLeft, HelpCircle, Info // 🔥 IMPORTADO INFO
} from 'lucide-vue-next'

const router = useRouter()
const ventas = ref([])
const filtros = ref({ busqueda: '', fechaDesde: '', fechaHasta: '', metodoPago: '', tipo: '', estado: '' })
const pagina = ref(1)
const itemsPorPagina = 8

// Estados UI
const mostrarRegistrar = ref(false)
const cargando = ref(false)
const generandoPDF = ref(null)
const ventaRecienCreada = ref(null)
const loadingPdf = ref(false)
const usuarioEmisor = ref('')

// Estados Anulación
const mostrarModalAnular = ref(false)
const ventaAAnular = ref(null)
const motivoSeleccionado = ref('Error en método de pago')
const motivoAnulacion = ref('')
const cargandoAnulacion = ref(false)

const empresaData = ref({
    razon_social: "", cuil_cuit: "", direccion: "", telefono: "", email: "" 
})

const irANotasCredito = () => {
  router.push('/notas-credito')
}

const cargarConfiguracionEmpresa = async () => {
    try {
        const res = await axios.get('/api/configuracion/');
        if (res.data) empresaData.value = res.data;
    } catch (e) { console.error("Error cargando config empresa", e); }
}

const obtenerUsuarioLogueado = () => {
  const n = localStorage.getItem('user_nombre');
  const a = localStorage.getItem('user_apellido');
  if(n || a) usuarioEmisor.value = `${n} ${a}`.trim();
  else usuarioEmisor.value = 'Administrador';
}

const cargarVentas = async () => {
  cargando.value = true
  try {
    const res = await axios.get('/api/ventas/')
    const data = Array.isArray(res.data) ? res.data : (res.data.results || [])
    if (data.length > 0) {
      ventas.value = data.sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
    } else {
      ventas.value = []
    }
  } catch (err) {
    console.error('❌ Error cargando ventas:', err)
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  obtenerUsuarioLogueado() 
  cargarVentas()
  cargarConfiguracionEmpresa()
})

const ventasFiltradas = computed(() => {
  const busca = filtros.value.busqueda.toLowerCase()
  return ventas.value.filter(v => {
    // 🔍 CORRECCIÓN: Ahora busca también por usuario_nombre
    const matchBusqueda = !busca || 
      (v.cliente_nombre?.toLowerCase() || '').includes(busca) || 
      (v.usuario_nombre?.toLowerCase() || '').includes(busca) || 
      (v.id || '').toString().includes(busca)
    
    const fecha = v.fecha ? new Date(v.fecha) : null
    const matchDesde = !filtros.value.fechaDesde || (fecha && fecha >= new Date(filtros.value.fechaDesde))
    const matchHasta = !filtros.value.fechaHasta || (fecha && fecha <= new Date(filtros.value.fechaHasta + 'T23:59:59'))
    const matchMetodo = !filtros.value.metodoPago || v.medio_pago_tipo === filtros.value.metodoPago
    const matchTipo = !filtros.value.tipo || v.tipo === filtros.value.tipo
    const matchEstado = !filtros.value.estado || 
        (filtros.value.estado === 'activa' && !v.anulada) || 
        (filtros.value.estado === 'anulada' && v.anulada)

    return matchBusqueda && matchDesde && matchHasta && matchMetodo && matchTipo && matchEstado
  })
})

const ventasAnuladas = computed(() => ventas.value.filter(v => v.anulada).length)
const totalPaginas = computed(() => Math.max(1, Math.ceil(ventasFiltradas.value.length / itemsPorPagina)))
const ventasPaginadas = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return ventasFiltradas.value.slice(inicio, inicio + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

const verDetallesVenta = (id) => router.push({ name: 'DetalleVenta', params: { id } })

// LÓGICA DE ANULACIÓN MEJORADA
const abrirModalAnular = (venta) => {
  ventaAAnular.value = venta;
  motivoSeleccionado.value = 'Error en método de pago';
  motivoAnulacion.value = '';
  mostrarModalAnular.value = true;
};

const cerrarModalAnular = () => {
  mostrarModalAnular.value = false;
  ventaAAnular.value = null;
  motivoAnulacion.value = '';
};

const esMotivoValido = computed(() => {
  if (motivoSeleccionado.value === 'Otro') {
    return motivoAnulacion.value.trim().length >= 5;
  }
  return true;
});

const confirmarAnulacion = async () => {
  if (!esMotivoValido.value) return;
  
  const motivoFinal = motivoSeleccionado.value === 'Otro' ? motivoAnulacion.value : motivoSeleccionado.value;
  
  cargandoAnulacion.value = true;
  try {
    const response = await axios.post(`/api/ventas/${ventaAAnular.value.id}/anular/`, {
      motivo: motivoFinal
    });
    
    Swal.fire({
        icon: 'success',
        title: 'Venta Anulada',
        text: response.data.message || 'La venta ha sido anulada y el stock restaurado.',
        confirmButtonColor: '#10b981'
    });
    
    cerrarModalAnular();
    await cargarVentas(); 
  } catch (error) {
    console.error("Error anulando venta:", error);
    Swal.fire({
        icon: 'error',
        title: 'Error al anular',
        text: error.response?.data?.error || 'Ocurrió un error inesperado.',
        confirmButtonColor: '#ef4444'
    });
  } finally {
    cargandoAnulacion.value = false;
  }
};


const generarComprobantePDF = (venta) => {
  generandoPDF.value = venta.id
  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
  const quienImprime = encodeURIComponent(usuarioEmisor.value || 'Caja Principal');
  setTimeout(() => {
      window.open(`${baseUrl}/api/ventas/${venta.id}/comprobante-pdf/?impreso_por=${quienImprime}`, '_blank')
      generandoPDF.value = null
  }, 500)
}

const generarReporteListado = async () => {
  loadingPdf.value = true;
  try {
    const params = new URLSearchParams();
    if (filtros.value.fechaDesde) params.append('fecha_desde', filtros.value.fechaDesde);
    if (filtros.value.fechaHasta) params.append('fecha_hasta', filtros.value.fechaHasta);
    if (filtros.value.metodoPago) params.append('metodo_pago', filtros.value.metodoPago);
    if (filtros.value.tipo) params.append('tipo', filtros.value.tipo);
    if (filtros.value.estado) params.append('estado', filtros.value.estado);
    
    if (usuarioEmisor.value) {
      params.append('impreso_por', usuarioEmisor.value);
    }

    const baseUrl = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
    const url = `${baseUrl}/ventas/exportar-listado-pdf/?${params.toString()}`;

    window.open(url, '_blank');
  } catch (error) {
    console.error('Error generando reporte:', error);
    Swal.fire('Error', 'No se pudo generar el reporte.', 'error');
  } finally {
    loadingPdf.value = false;
  }
};

const cerrarModal = () => { mostrarRegistrar.value = false }
const procesarVentaRegistrada = async (venta) => { 
  await cargarVentas(); 
  ventaRecienCreada.value = venta.id 
  setTimeout(() => ventaRecienCreada.value = null, 5000) 
}
const limpiarFiltros = () => { filtros.value = { busqueda: '', fechaDesde: '', fechaHasta: '', metodoPago: '', tipo: '', estado: '' }; pagina.value = 1 }

const formatFechaDia = (f) => f ? new Date(f).toLocaleDateString('es-AR', {day: '2-digit', month: '2-digit', year: 'numeric'}) : '-'
const formatFechaHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : ''
const formatPrecio = (p) => p ? parseFloat(p).toLocaleString('es-AR', { minimumFractionDigits: 2 }) : '0.00'

const getMedioPagoInfo = (venta) => {
    const tipo = (venta.medio_pago_tipo || '').toUpperCase()
    const nombre = (venta.medio_pago_nombre || '').toUpperCase()
    if (tipo === 'EFECTIVO' || nombre.includes('EFECTIVO')) return { clase: 'pago-efectivo', icono: Banknote }
    if (tipo === 'TARJETA' || nombre.includes('TARJETA')) return { clase: 'pago-tarjeta', icono: CreditCard }
    if (tipo === 'TRANSFERENCIA' || nombre.includes('TRANSF')) return { clase: 'pago-transferencia', icono: ArrowRightLeft }
    if (tipo === 'MERCADO_PAGO' || nombre.includes('MERCADO')) return { clase: 'pago-mp', icono: Smartphone }
    return { clase: 'pago-otro', icono: HelpCircle }
}

const getClaseTipoVenta = (t) => t === 'TURNO' ? 'tipo-turno' : 'tipo-prod'
const getClaseEstadoVenta = (anulada) => anulada ? 'estado-anulada' : 'estado-activa'

// 🔥 FUNCIÓN CORREGIDA: ALERTA DE ANULACIÓN LIMPIA Y ELEGANTE
const verMotivoAnulacion = async (venta) => {
  try {
    Swal.fire({ title: 'Cargando auditoría...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
    
    const token = localStorage.getItem('token');
    const response = await axios.get(`/api/ventas/${venta.id}/`, {
      headers: { Authorization: `Token ${token}` }
    });
    
    const detalleVenta = response.data;

    // Lista de productos limpia
    let itemsHTML = '<p style="color: #94a3b8; font-size: 0.85rem; text-align: center;">No hay productos registrados</p>';
    if (detalleVenta.detalles && detalleVenta.detalles.length > 0) {
      itemsHTML = detalleVenta.detalles.map(d => `
        <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #cbd5e1; padding: 10px 0; font-size: 0.95rem;">
          <span style="color: #334155; font-weight: 600;">${d.cantidad}x ${d.producto_nombre || d.producto.nombre || 'Producto'}</span>
          <span style="font-weight: 800; color: #64748b;">$${Number(d.subtotal || (d.precio_unitario * d.cantidad)).toLocaleString('es-AR')}</span>
        </div>
      `).join('');
    }

    // Formateo de fecha
    const fechaMostrar = detalleVenta.fecha_anulacion 
      ? new Date(detalleVenta.fecha_anulacion).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' }) 
      : 'Fecha no registrada';

    Swal.fire({
      title: `
        <div style="color: #ef4444; font-weight: 900; font-size: 1.5rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
          Venta Anulada #${venta.id}
        </div>`,
      html: `
        <div style="text-align: left; font-family: system-ui, -apple-system, sans-serif; margin-top: 15px;">
          
          <div style="border-left: 4px solid #ef4444; background-color: #fef2f2; border-radius: 0 8px 8px 0; padding: 16px; margin-bottom: 25px;">
            <p style="margin: 0 0 5px 0; font-size: 0.8rem; color: #991b1b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">📋 Motivo registrado:</p>
            <p style="margin: 0; font-size: 1.1rem; color: #7f1d1d; font-weight: 500; font-style: italic;">
              "${detalleVenta.motivo_anulacion || 'El sistema no registró un motivo.'}"
            </p>
          </div>

          <div style="margin-bottom: 20px;">
            <p style="margin: 0 0 8px 0; font-size: 0.8rem; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">📦 Mercadería reintegrada:</p>
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 5px 18px 15px;">
              ${itemsHTML}
              <div style="text-align: right; margin-top: 15px; font-size: 1.2rem; color: #0f172a;">
                Total cancelado: <strong style="color: #ef4444; font-weight: 900;">-$${Number(detalleVenta.total).toLocaleString('es-AR')}</strong>
              </div>
            </div>
          </div>

          <div style="text-align: center; margin-top: 25px;">
            <span style="background-color: #f1f5f9; padding: 6px 12px; border-radius: 20px; color: #64748b; font-size: 0.8rem; font-weight: 600;">
              🕒 Anulado el: ${fechaMostrar}
            </span>
          </div>
        </div>
      `,
      showConfirmButton: true,
      confirmButtonText: 'Cerrar',
      confirmButtonColor: '#0ea5e9',
      background: '#ffffff', // Forzamos fondo blanco para que no se rompa con themes oscuros
      width: '500px',
      customClass: {
        popup: 'swal2-border-radius' // Solo le damos bordes redondeados al contenedor
      }
    });

  } catch (error) {
    console.error("Error cargando detalle de anulación:", error);
    Swal.fire('Error', 'No se pudieron cargar los detalles de la anulación.', 'error');
  }
};
</script>

<style scoped>
.list-container { padding: 0; width: 100%; }
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); border-radius: 24px 24px 0 0; }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; flex-wrap: wrap; gap: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; letter-spacing: 0.5px; }

.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; font-size: 0.95rem; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); display: flex; align-items: center; gap: 8px; }
.register-button:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); }
.register-button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; align-items: end; }
.filter-group { display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }

.filter-input { padding: 12px 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-weight: 500; font-size: 0.95rem; }
.filter-input:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); }
.select-dark option { background-color: #1e293b; color: #f8fafc; font-weight: 500; }

.w-full { width: 100%; box-sizing: border-box; resize: vertical; }
.mt-2 { margin-top: 8px; }
.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 18px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: 0.3s; text-transform: uppercase; font-size: 0.85rem; display: flex; align-items: center; gap: 6px; }
.clear-filters-btn:hover { background: var(--hover-bg); transform: translateY(-2px); }

.table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow-md); border: 1px solid var(--border-color); }
.users-table th { background: var(--accent-color); color: white; padding: 18px 14px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px; white-space: nowrap; }
.users-table tr { border-bottom: 1px solid var(--border-color); }
.users-table td { padding: 14px; vertical-align: middle; color: var(--text-secondary); font-weight: 500; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
.users-table tr:hover { background: var(--hover-bg); transition: 0.2s; }

.fecha-cell { display: flex; flex-direction: column; }
.fecha-dia { font-weight: 700; color: var(--text-primary); }
.fecha-hora { font-size: 0.75rem; color: var(--text-tertiary); }
.usuario-cell { color: #e2e8f0; font-weight: 500; }
.total-cell { font-size: 1rem; font-weight: 800; color: #10b981; }

.badge-pago { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; border: 1px solid transparent; }
.pago-efectivo { background: rgba(16, 185, 129, 0.1); color: #10b981; border-color: rgba(16, 185, 129, 0.3); }
.pago-tarjeta { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; border-color: rgba(139, 92, 246, 0.3); }
.pago-transferencia { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border-color: rgba(245, 158, 11, 0.3); }
.pago-mp { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border-color: rgba(14, 165, 233, 0.3); }
.pago-otro { background: rgba(156, 163, 175, 0.1); color: #9ca3af; border-color: rgba(156, 163, 175, 0.3); }

.badge-tipo, .badge-estado { padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.tipo-turno { background: rgba(236, 72, 153, 0.1); color: #ec4899; border: 1px solid rgba(236, 72, 153, 0.3); }
.tipo-prod { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
.estado-activa { color: #10b981; background: rgba(16, 185, 129, 0.05); }
.estado-anulada { color: #ef4444; background: rgba(239, 68, 68, 0.05); text-decoration: line-through; }
.venta-anulada-row { opacity: 0.6; background: rgba(239, 68, 68, 0.02); }

.btn-pdf-icon { background: transparent; border: 1px solid var(--border-color); color: var(--text-secondary); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; margin: 0 auto; }
.btn-pdf-icon:hover:not(:disabled) { background: #0ea5e9; color: white; border-color: #0ea5e9; transform: translateY(-2px); }
.btn-pdf-icon:disabled { opacity: 0.3; cursor: not-allowed; }
.spin { animation: spin 1s linear infinite; } @keyframes spin { to { transform: rotate(360deg); } }

.action-buttons { display: flex; gap: 6px; }
.action-button { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; border: 1px solid transparent; transition: 0.2s; background: var(--bg-tertiary); color: var(--text-secondary); }
.action-button:hover:not(:disabled) { transform: translateY(-2px); }
.action-button.delete:hover:not(:disabled) { color: #ef4444; border-color: #ef4444; background: rgba(239, 68, 68, 0.1); }
.action-button.detalle:hover:not(:disabled) { color: #10b981; border-color: #10b981; background: rgba(16, 185, 129, 0.1); }

/* 🔥 ESTILO BOTÓN INFO ANULADA */
.action-button.anulada-info { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.5); color: #ef4444; }
.action-button.anulada-info:hover { background: #ef4444; color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3); }

.action-button:disabled { opacity: 0.3; cursor: not-allowed; background: transparent;}

.list-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 15px; background: var(--hover-bg); border-radius: 12px; flex-wrap: wrap; gap: 15px; }
.footer-left { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.count-text { color: var(--text-secondary); font-size: 0.9rem; margin: 0; }

.alertas-container { display: flex; gap: 10px; }
.alerta-bad, .alerta-good { padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: flex; align-items: center; gap: 6px; text-transform: uppercase; }
.alerta-bad { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; }
.alerta-good { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981; animation: fadeIn 0.5s ease; }

.pagination { display: flex; gap: 10px; align-items: center; }
.page-btn { background: var(--bg-tertiary); border: 1px solid var(--border-color); width: 36px; height: 36px; border-radius: 8px; cursor: pointer; color: var(--text-primary); display: flex; justify-content: center; align-items: center; transition: 0.2s; }
.page-btn:hover:not(:disabled) { background: var(--accent-color); color: white; border-color: var(--accent-color); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }

.loading-state { text-align: center; padding: 80px; color: var(--text-tertiary); font-weight: 600; }
.loading-spinner { width: 40px; height: 40px; border: 3px solid var(--border-color); border-top-color: var(--accent-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px; }
.no-results { text-align: center; padding: 60px; color: var(--text-tertiary); }
.btn-reintentar { margin-top: 15px; padding: 10px 20px; background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; color: var(--text-primary); display: flex; align-items: center; gap: 8px; justify-content: center; margin: 20px auto 0; font-weight: 700; transition: 0.3s; }
.btn-reintentar:hover { background: var(--hover-bg); transform: translateY(-2px); }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); z-index: 1000; display: flex; justify-content: center; align-items: center; }
.modal-content { background: var(--bg-secondary); padding: 0; border-radius: 16px; border: 1px solid var(--border-color); max-height: 90vh; overflow-y: auto; }

.modal-content-anular { background: var(--bg-secondary); padding: 30px; border-radius: 16px; border: 1px solid var(--border-color); width: 100%; max-width: 450px; text-align: left; }
.modal-content-anular h2 { margin-top: 0; color: var(--text-primary); font-size: 1.5rem; margin-bottom: 10px; }
.anular-warning { color: #ef4444; font-size: 0.9rem; margin-bottom: 20px; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 8px; border-left: 4px solid #ef4444; }
.modal-actions-anular { display: flex; justify-content: flex-end; gap: 10px; margin-top: 25px; }
.btn-cancelar { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-confirmar-anular { background: #ef4444; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; }
.btn-confirmar-anular:disabled { opacity: 0.5; cursor: not-allowed; }

/* FIX SWEETALERT PARA MODO OSCURO */
:deep(.swal-rounded-popup) { border-radius: 20px !important; background: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important; }
:deep(.swal2-border-radius) { border-radius: 16px !important;}

@media (max-width: 768px) {
  .list-footer { flex-direction: column; align-items: flex-start; }
  .footer-left { flex-direction: column; align-items: flex-start; gap: 10px; }
  .pagination { width: 100%; justify-content: space-between; }
}
</style>