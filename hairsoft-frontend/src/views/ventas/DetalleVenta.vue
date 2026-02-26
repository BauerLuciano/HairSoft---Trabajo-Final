<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Detalle de Venta</h1>
          <p>Información completa y auditoría de la venta #{{ ventaId }}</p>
        </div>
        <div class="acciones-header">
          <button 
            @click="generarComprobantePDF" 
            class="register-button"
            :disabled="generandoPDF"
          >
            <FileText :size="18" v-if="!generandoPDF" />
            <Loader :size="18" v-else />
            {{ generandoPDF ? 'Generando...' : 'Comprobante PDF' }}
          </button>
          <button @click="$router.push('/ventas')" class="btn-volver">
            <ChevronLeft :size="18" />
            Volver a Ventas
          </button>
        </div>
      </div>

      <div v-if="cargando" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Cargando detalle de venta...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <AlertTriangle :size="48" />
        <p>{{ error }}</p>
        <button @click="obtenerVenta" class="btn-reintentar">
          <RefreshCw :size="16" />
          Reintentar
        </button>
      </div>

      <div v-else-if="venta" class="detalle-contenido">
        <div class="detalle-card">
          <div class="detalle-header-card">
            <div class="titulo-venta">
              <h2>Venta #{{ venta.id }}</h2>
              <span class="badge-estado" :class="getClaseEstadoVenta(venta.anulada)">
                {{ venta.anulada ? '❌ ANULADA' : '✅ COMPLETADA' }}
              </span>
            </div>
            <div class="fecha-venta">
              <Calendar :size="16" />
              {{ formatearFecha(venta.fecha) }}
            </div>
          </div>

          <div class="grid-info">
            <div class="info-item">
              <label>Cliente</label>
              <div class="info-value">
                <User :size="16" />
                {{ venta.cliente_nombre || 'Venta Rápida' }}
              </div>
            </div>

            <div class="info-item">
              <label>Atendido por</label>
              <div class="info-value">
                <UserCheck :size="16" />
                {{ venta.usuario_nombre || 'Sistema' }}
              </div>
            </div>

            <div class="info-item">
              <label>Tipo de Venta</label>
              <div class="info-value">
                <span class="badge-tipo" :class="getClaseTipoVenta(venta.tipo)">
                  {{ venta.tipo || 'PRODUCTO' }}
                </span>
              </div>
            </div>

            <div class="info-item">
              <label>Total Venta</label>
              <div class="info-value total-monto">
                <DollarSign :size="20" />
                {{ formatPrecio(venta.total) }}
              </div>
            </div>
          </div>

          <div class="auditoria-pago-container">
            <h3><Info :size="18" style="margin-right: 8px; display: inline-block; vertical-align: text-bottom;"/>Detalles de Transacción</h3>
            <div class="grid-auditoria">
                
                <div class="dato-auditoria">
                    <span class="label-auditoria">Medio de Pago:</span>
                    <span class="badge-pago" :class="getClaseTipoPago(venta)">
                        {{ getNombrePago(venta) }}
                    </span>
                </div>

                <div class="dato-auditoria" v-if="venta.entidad_pago">
                    <span class="label-auditoria">Entidad / Billetera:</span>
                    <strong class="valor-auditoria">{{ venta.entidad_pago }}</strong>
                </div>

                <div class="dato-auditoria full-width" v-if="venta.codigo_transaccion">
                    <span class="label-auditoria">Ref. / ID Transacción:</span>
                    <div class="code-wrapper">
                        <code class="codigo-referencia">{{ venta.codigo_transaccion }}</code>
                    </div>
                </div>

                <div class="dato-auditoria full-width" v-if="venta.mp_payment_id">
                    <span class="label-auditoria">MercadoPago ID:</span>
                    <div class="code-wrapper">
                        <code class="codigo-referencia mp">
                            <img src="https://logotipoz.com/wp-content/uploads/2021/10/versiones-logo-mercadopago.png" alt="MP" class="mp-mini-logo" style="height: 12px; margin-right: 5px;">
                            {{ venta.mp_payment_id }}
                        </code>
                    </div>
                </div>
            </div>
          </div>

          <div class="tabla-detalle-container">
            <h3>Productos/Servicios</h3>
            <div class="table-container">
              <table class="users-table">
                <thead>
                  <tr>
                    <th>Ítem</th>
                    <th>Tipo</th>
                    <th>Cantidad</th>
                    <th>P. Unitario</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="detalle in venta.detalles" :key="detalle.id">
                    <td>
                      <strong>{{ detalle.producto_nombre || detalle.servicio_nombre || 'N/A' }}</strong>
                      <small v-if="detalle.turno" class="turno-info">
                        (Turno #{{ detalle.turno }})
                      </small>
                    </td>
                    <td>
                      <span v-if="detalle.producto_nombre" class="badge-tipo producto">Producto</span>
                      <span v-else class="badge-tipo turno">Servicio</span>
                    </td>
                    <td>{{ detalle.cantidad }}</td>
                    <td>${{ formatPrecio(detalle.precio_unitario) }}</td>
                    <td><strong>${{ formatPrecio(detalle.subtotal) }}</strong></td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="4" class="total-label">
                      <strong>TOTAL FINAL</strong>
                    </td>
                    <td class="total-final">
                      <strong>${{ formatPrecio(venta.total) }}</strong>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <div v-if="venta.notas || venta.anulada" class="notas-container">
            <div v-if="venta.notas" class="nota">
              <MessageSquare :size="16" />
              <div>
                <strong>Notas:</strong> {{ venta.notas }}
              </div>
            </div>
            <div v-if="venta.anulada" class="nota anulada">
              <AlertTriangle :size="16" />
              <div>
                <strong>Esta venta fue anulada</strong>
                <small>No genera ingresos y el stock fue restaurado</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2'
import { 
  FileText, Loader, ChevronLeft, RefreshCw, AlertTriangle,
  Calendar, User, UserCheck, DollarSign, MessageSquare, Trash2, Info
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const ventaId = route.params.id
const venta = ref(null)
const cargando = ref(true)
const error = ref(null)
const generandoPDF = ref(false)

const obtenerVenta = async () => {
  cargando.value = true
  error.value = null
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/ventas/?q=${ventaId}`)
    const resultados = res.data.results || res.data;
    
    if (Array.isArray(resultados) && resultados.length > 0) {
      const ventaEncontrada = resultados.find(v => v.id == ventaId) || resultados[0];
      venta.value = ventaEncontrada
    } else {
      const resDirecto = await axios.get(`${API_BASE}/usuarios/api/ventas/${ventaId}/`);
      if (resDirecto.data) venta.value = resDirecto.data;
      else throw new Error('Venta no encontrada');
    }
  } catch (err) {
    console.error('❌ Error cargando detalle:', err)
    error.value = 'No se pudo cargar la venta. Verifique que exista.'
  } finally {
    cargando.value = false
  }
}

const formatearFecha = (fecha) => {
  if (!fecha) return '–'
  return new Date(fecha).toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const formatPrecio = (p) => parseFloat(p || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })

// 🔥 LÓGICA CORREGIDA: PRIORIZA IDs SOBRE NOMBRE
const getNombrePago = (v) => {
    // 1. Si hay ID de MP, es Mercado Pago sí o sí.
    if (v.mp_payment_id) return 'Mercado Pago';
    
    // 2. Si hay código de transacción, es digital (Transferencia o Tarjeta), nunca Efectivo.
    if (v.codigo_transaccion) {
        const tipoOriginal = (v.medio_pago_tipo || '').toUpperCase();
        // Si el tipo decía 'EFECTIVO' pero hay código, lo corregimos a Transferencia
        if (!tipoOriginal || tipoOriginal === 'EFECTIVO') return 'Transferencia';
    }

    // 3. Si no hay conflicto de IDs, usamos el nombre si existe
    if (v.medio_pago_nombre) return v.medio_pago_nombre;
    
    // 4. Fallback al mapeo estándar
    const tipo = (v.medio_pago_tipo || '').toUpperCase();
    const map = {
        'MERCADO_PAGO': 'Mercado Pago',
        'MERCADOPAGO': 'Mercado Pago',
        'TRANSFERENCIA': 'Transferencia',
        'TARJETA': 'Tarjeta',
        'EFECTIVO': 'Efectivo',
        'MIXTO': 'Mixto'
    };
    return map[tipo] || 'Otro';
}

// 🔥 COLOR DEL BADGE CORREGIDO: También mira la venta completa
const getClaseTipoPago = (v) => {
  if (!v) return 'default';
  
  // Inferencia por IDs para el color
  if (v.mp_payment_id) return 'pago-mp';
  if (v.codigo_transaccion) return 'transferencia'; // Asumimos color transferencia para refs bancarias

  // Inferencia normal por tipo
  const tipo = (v.medio_pago_tipo || '').toUpperCase();
  const tipos = { 
      'EFECTIVO': 'efectivo', 
      'TARJETA': 'tarjeta', 
      'TRANSFERENCIA': 'transferencia', 
      'MERCADO_PAGO': 'pago-mp', 
      'MERCADOPAGO': 'pago-mp' 
  }
  return tipos[tipo] || 'default'
}

const getClaseTipoVenta = (tipo) => tipo === 'TURNO' ? 'turno' : 'producto'
const getClaseEstadoVenta = (anulada) => anulada ? 'estado-anulada' : 'estado-activa'

const generarComprobantePDF = async () => {
  if (generandoPDF.value || !venta.value) return
  generandoPDF.value = true
  try {
    const url = `${API_BASE}/usuarios/api/ventas/${venta.value.id}/comprobante-pdf/`
    window.open(url, '_blank')
  } catch (e) {
    Swal.fire('Error', 'No se pudo generar el PDF', 'error')
  } finally {
    generandoPDF.value = false
  }
}

const anularVenta = async () => {
  if (!venta.value || venta.value.anulada) return
  const result = await Swal.fire({
    title: '¿Anular Venta?',
    text: "Esto devolverá el stock y anulará el ingreso.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    confirmButtonText: 'Sí, anular'
  })
  
  if (!result.isConfirmed) return
  
  try {
    cargando.value = true
    await axios.post(`${API_BASE}/usuarios/api/ventas/${venta.value.id}/anular/`)
    venta.value.anulada = true
    Swal.fire('Venta Anulada', 'La operación fue exitosa', 'success')
  } catch (err) {
    Swal.fire('Error', 'No se pudo anular la venta', 'error')
  } finally {
    cargando.value = false
  }
}

onMounted(() => { obtenerVenta() })
</script>

<style scoped>
/* VARIABLES (Fallback si faltan en themes.css) */
:root {
    --bg-tertiary: #f1f5f9;
    --border-color: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
}

/* CONTAINER */
.list-container {
  padding: 30px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  background: var(--bg-primary);
}

.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1400px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
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

.acciones-header {
  display: flex;
  gap: 15px;
  align-items: center;
}

/* DATOS PRINCIPALES */
.detalle-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.titulo-venta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.titulo-venta h2 {
  margin: 0;
  font-size: 1.8rem;
  color: var(--text-primary);
  font-weight: 800;
}

.fecha-venta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-weight: 600;
  background: var(--bg-tertiary);
  padding: 10px 18px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.grid-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.info-item {
  background: var(--hover-bg);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.info-item label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.info-value.total-monto {
  font-size: 1.5rem;
  color: #10b981;
}

/* SECCION AUDITORIA - INTEGRADA AL TEMA */
.auditoria-pago-container {
    background: var(--bg-tertiary); /* Usa variable, no blanco fijo */
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 30px;
}

.auditoria-pago-container h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 14px;
    color: var(--text-secondary);
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
}

.grid-auditoria {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
}

.dato-auditoria {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.dato-auditoria.full-width {
    grid-column: 1 / -1;
}

.label-auditoria {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 600;
    text-transform: uppercase;
}

.valor-auditoria {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1.05rem;
}

.code-wrapper {
    display: flex;
    align-items: center;
}

.codigo-referencia {
    font-family: 'Courier New', monospace;
    background: var(--bg-primary);
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    display: inline-flex;
    align-items: center;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.codigo-referencia.mp {
    border-color: #0ea5e9;
    color: #0ea5e9;
    background: rgba(14, 165, 233, 0.05);
}

/* TABLAS Y BADGES */
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
}

.users-table td {
  padding: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
}

.total-final {
  font-size: 1.4rem;
  color: #10b981;
  padding: 20px !important;
}

.badge-pago {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.badge-pago.pago-mp {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  border: 1px solid #0ea5e9;
}

.badge-pago.transferencia {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
  border: 1px solid #8b5cf6;
}

.badge-pago.efectivo {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid #10b981;
}

.badge-pago.tarjeta {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid #f59e0b;
}

.badge-tipo {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}
.badge-tipo.producto { background: var(--bg-tertiary); color: #f59e0b; border: 2px solid #f59e0b; }
.badge-tipo.turno { background: var(--bg-tertiary); color: #ec4899; border: 2px solid #ec4899; }

.badge-estado {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}
.badge-estado.estado-activa { background: var(--bg-tertiary); color: var(--success-color); border: 2px solid var(--success-color); }
.badge-estado.estado-anulada { background: var(--bg-tertiary); color: var(--error-color); border: 2px solid var(--error-color); opacity: 0.75; text-decoration: line-through; }

/* BOTONES */
.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-volver {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-volver:hover {
  background: var(--hover-bg);
}

.action-button.delete {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* NOTAS */
.notas-container {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid var(--border-color);
}
.nota {
  display: flex; gap: 12px; padding: 16px; background: var(--bg-tertiary); border-radius: 12px; margin-bottom: 12px; border: 1px solid var(--border-color);
}
.nota.anulada { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--error-color); }

/* LOADING & ERROR */
.loading-state, .error-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}
.loading-spinner {
  width: 40px; height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* RESPONSIVE */
@media (max-width: 768px) {
  .header-content h1 { font-size: 1.5rem; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .acciones-header { width: 100%; flex-direction: column; }
  .acciones-header button { width: 100%; justify-content: center; }
  .users-table { font-size: 0.85rem; }
}
</style>