<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Detalle de Venta</h1>
          <p>Información completa de la venta #{{ ventaId }}</p>
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
        <button @click="$router.push('/ventas')" class="btn-volver">
          <ChevronLeft :size="16" />
          Volver
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
              <label>Método de Pago</label>
              <div class="info-value">
                <span class="badge-pago" :class="getClaseTipoPago(venta.medio_pago_tipo)">
                  {{ venta.medio_pago_nombre || 'Efectivo' }}
                </span>
                
                <small v-if="venta.entidad_pago" class="extra-pago-info">
                   ({{ venta.entidad_pago }})
                </small>
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

            <div v-if="venta.codigo_transaccion" class="info-item">
              <label>Transacción ID</label>
              <div class="info-value transaccion-id">
                {{ venta.codigo_transaccion }}
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

        <div class="acciones-detalle">
          <button 
            @click="anularVenta" 
            class="action-button delete"
            :disabled="venta.anulada"
            :title="venta.anulada ? 'Venta ya anulada' : 'Anular esta venta'"
          >
            <Trash2 :size="16" />
            Anular Venta
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/utils/axiosConfig' // 🔥 CORREGIDO: Usar instancia configurada con Token
import Swal from 'sweetalert2'
import { 
  FileText, Loader, ChevronLeft, RefreshCw, AlertTriangle,
  Calendar, User, UserCheck, DollarSign, MessageSquare,
  Trash2, Edit3, Printer, Eye, Package, PackageX,
  CheckCircle, X, ArrowLeft, ArrowRight, Plus, Trash2 as TrashIcon
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
// Usamos URL relativa porque axiosConfig ya tiene la BASE_URL si está bien configurado, 
// o usamos la variable local si axiosConfig no la tiene.
// Para asegurar, mantenemos la variable pero usada con la instancia importada.
const API_BASE = 'http://127.0.0.1:8000'

const ventaId = route.params.id
const venta = ref(null)
const cargando = ref(true)
const error = ref(null)
const generandoPDF = ref(false)

// Obtener datos de la venta
const obtenerVenta = async () => {
  cargando.value = true
  error.value = null
  
  try {
    console.log(`🔄 Cargando detalle de venta #${ventaId}...`)
    
    // 🔥 TRUCO: Usamos el endpoint de búsqueda (?q=ID) en lugar del detalle directo.
    // Esto fuerza al backend a usar el Serializer de Listado (que sabemos que trae los detalles completos)
    // en lugar del Serializer de Detalle (que a veces viene vacío o con IDs).
    const res = await axios.get(`${API_BASE}/usuarios/api/ventas/?q=${ventaId}`)
    
    // Manejar respuesta paginada o lista directa
    const resultados = res.data.results || res.data;
    
    if (Array.isArray(resultados) && resultados.length > 0) {
      // Buscamos la venta exacta por si la búsqueda trajo coincidencias parciales
      const ventaEncontrada = resultados.find(v => v.id == ventaId) || resultados[0];
      venta.value = ventaEncontrada
      console.log('✅ Detalle de venta cargado (vía listado):', venta.value)
    } else {
      // Fallback: Si no funciona la búsqueda, intentamos ID directo
      console.warn('⚠️ No encontrada en listado, intentando ID directo...');
      const resDirecto = await axios.get(`${API_BASE}/usuarios/api/ventas/${ventaId}/`);
      if (resDirecto.data) {
          venta.value = resDirecto.data;
      } else {
          throw new Error('Venta no encontrada');
      }
    }
  } catch (err) {
    console.error('❌ Error cargando detalle de venta:', err.response || err)
    error.value = err.response?.data?.message || err.message || 'Error al cargar la venta'
    
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error.value,
      confirmButtonText: 'Entendido'
    })
  } finally {
    cargando.value = false
  }
}

// Funciones de utilidad
const formatearFecha = (fecha) => {
  if (!fecha) return '–'
  try {
    const dateObj = new Date(fecha)
    if (isNaN(dateObj.getTime())) return 'Fecha inválida'
    return dateObj.toLocaleString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  } catch (e) {
    console.error("Error formateando fecha:", e)
    return 'Error fecha'
  }
}

const formatPrecio = (precio) => {
  if (precio === undefined || precio === null) return '0.00'
  return parseFloat(precio).toFixed(2)
}

const getClaseTipoPago = (tipoPago) => {
  if (!tipoPago) return 'default'
  const tipos = {
    'EFECTIVO': 'efectivo',
    'TARJETA': 'tarjeta',
    'TRANSFERENCIA': 'transferencia',
    'MERCADOPAGO': 'transferencia' // MP usa estilo similar a transferencia o propio
  }
  return tipos[tipoPago] || 'default'
}

const getClaseTipoVenta = (tipo) => {
  const tipos = {
    'PRODUCTO': 'producto',
    'TURNO': 'turno',
    'MIXTO': 'mixto'
  }
  return tipos[tipo] || 'default'
}

const getClaseEstadoVenta = (anulada) => {
  return anulada ? 'estado-anulada' : 'estado-activa'
}

// Funciones de acción
const generarComprobantePDF = async () => {
  if (generandoPDF.value || !venta.value) return
  
  generandoPDF.value = true
  console.log(`📄 Generando comprobante PDF para venta #${venta.value.id}`)
  
  try {
    Swal.fire({
      title: 'Generando PDF...',
      text: 'Por favor espere',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    const url = `${API_BASE}/usuarios/api/ventas/${venta.value.id}/comprobante-pdf/`
    window.open(url, '_blank')
    
    Swal.close()
    Swal.fire({
      icon: 'success',
      title: 'PDF Generado',
      text: `Comprobante para venta #${venta.value.id} generado correctamente`,
      timer: 2000,
      showConfirmButton: false
    })
    
  } catch (error) {
    console.error('❌ Error generando PDF:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo generar el comprobante PDF',
      confirmButtonText: 'Entendido'
    })
  } finally {
    generandoPDF.value = false
  }
}

const anularVenta = async () => {
  if (!venta.value || venta.value.anulada) return
  
  const result = await Swal.fire({
    title: '¿Anular Venta?',
    html: `
      <div style="text-align: left;">
        <p><strong>Venta #${venta.value.id}</strong></p>
        <p><strong>Cliente:</strong> ${venta.value.cliente_nombre || 'Venta Rápida'}</p>
        <p><strong>Total:</strong> $${venta.value.total}</p>
        <p><strong>Fecha:</strong> ${formatearFecha(venta.value.fecha)}</p>
        <hr style="margin: 15px 0;">
        <p style="color: #e53e3e; font-weight: bold;">
          ⚠️ Esta acción no se puede deshacer
        </p>
        <ul style="text-align: left; margin: 10px 0; padding-left: 20px;">
          <li>Marcará la venta como ANULADA</li>
          <li>Devolverá el stock de los productos</li>
        </ul>
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, anular venta',
    cancelButtonText: 'Cancelar',
    reverseButtons: true,
    backdrop: true,
    allowOutsideClick: false
  })
  
  if (!result.isConfirmed) return
  
  try {
    cargando.value = true
    console.log(`🔄 Anulando venta #${venta.value.id}...`)
    
    Swal.fire({
      title: 'Anulando Venta...',
      text: 'Por favor espere',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    const response = await axios.post(`${API_BASE}/usuarios/api/ventas/${venta.value.id}/anular/`)
    
    if (response.status === 200) {
      venta.value.anulada = true
      
      Swal.fire({
        icon: 'success',
        title: 'Venta Anulada',
        text: `Venta #${venta.value.id} anulada correctamente. Stock actualizado.`,
        timer: 3000,
        showConfirmButton: false
      })
      
      console.log(`✅ Venta #${venta.value.id} anulada exitosamente`)
    }
  } catch (err) {
    console.error('❌ Error anulando venta:', err.response || err)
    
    let errorMessage = 'No se pudo anular la venta'
    if (err.response?.data?.error) {
      errorMessage = err.response.data.error
    } else if (err.response?.status === 404) {
      errorMessage = 'Venta no encontrada'
    }
    
    Swal.fire({
      icon: 'error',
      title: 'Error al Anular',
      text: errorMessage,
      confirmButtonText: 'Entendido'
    })
  } finally {
    cargando.value = false
  }
}

const editarVenta = () => {
  if (!venta.value || venta.value.anulada) {
    Swal.fire({
      icon: 'warning',
      title: 'Venta Anulada',
      text: 'No se puede editar una venta anulada',
      confirmButtonText: 'Entendido'
    })
    return
  }
  router.push({ name: 'ModificarVenta', params: { id: venta.value.id } })
}

const imprimir = () => {
  window.print()
}

onMounted(() => {
  obtenerVenta()
})
</script>

<style scoped>
/* Mismas variables CSS que el listado */
.list-container {
  padding: 30px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* Tarjeta principal - IDÉNTICA al listado */
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
  transition: all 0.4s ease;
  border: 1px solid var(--border-color);
}

/* Borde superior azul acero - IDÉNTICO */
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* HEADER - IDÉNTICO */
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

/* Botón Volver - estilo similar al register-button pero diferente color */
.btn-volver {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-volver:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: #6b7280;
}

/* LOADING STATE - IDÉNTICO */
.loading-state {
  text-align: center;
  padding: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ERROR STATE - similar al no-results */
.error-state {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.error-state svg {
  margin-bottom: 0;
  opacity: 0.5;
  color: var(--error-color);
}

.error-state p {
  margin: 0;
  font-size: 1.1em;
  color: var(--text-primary);
}

/* Botón reintentar IDÉNTICO */
.btn-reintentar {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.btn-reintentar:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5);
}

/* DETALLE CONTENIDO */
.detalle-contenido {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Tarjeta de detalle */
.detalle-card {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 30px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  margin-bottom: 30px;
}

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

/* GRID DE INFORMACIÓN */
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

.info-item:hover {
  background: var(--bg-tertiary);
  transform: translateY(-3px);
  box-shadow: var(--shadow-sm);
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

/* TABLA DETALLE */
.tabla-detalle-container h3 {
  font-size: 1.3rem;
  color: var(--text-primary);
  margin-bottom: 20px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 10px;
}

.tabla-detalle-container .table-container {
  margin-bottom: 0;
}

.turno-info {
  display: block;
  font-size: 0.8rem;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.total-label {
  text-align: right;
  padding: 20px !important;
  font-size: 1.2rem;
}

.total-final {
  font-size: 1.4rem;
  color: #10b981;
  padding: 20px !important;
}

/* NOTAS */
.notas-container {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid var(--border-color);
}

.nota {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid var(--border-color);
}

.nota.anulada {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--error-color);
}

.nota.anulada small {
  display: block;
  font-size: 0.85rem;
  opacity: 0.9;
  margin-top: 4px;
}

/* ACCIONES DETALLE */
.acciones-detalle {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding-top: 25px;
  border-top: 2px solid var(--border-color);
}

.acciones-detalle .action-button {
  padding: 14px 28px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 800;
}

/* BADGES - IDÉNTICOS al listado */
.badge-estado, .badge-pago, .badge-tipo {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
}

.badge-estado.estado-activa {
  background: var(--bg-tertiary);
  color: var(--success-color);
  border: 2px solid var(--success-color);
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.badge-estado.estado-anulada {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
  opacity: 0.75;
}

.badge-pago.efectivo {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
}

.badge-pago.tarjeta {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 8px rgba(14, 165, 233, 0.2);
}

.badge-pago.transferencia {
  background: var(--bg-tertiary);
  color: #8b5cf6;
  border: 2px solid #8b5cf6;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.2);
}

.badge-tipo.producto {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.2);
}

.badge-tipo.turno {
  background: var(--bg-tertiary);
  color: #ec4899;
  border: 2px solid #ec4899;
  box-shadow: 0 0 8px rgba(236, 72, 153, 0.2);
}

.badge-tipo.mixto {
  background: var(--bg-tertiary);
  color: #8b5cf6;
  border: 2px solid #8b5cf6;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.2);
}

/* BOTONES DE ACCIÓN - IDÉNTICOS al listado */
.action-button {
  padding: 12px 16px;
  width: auto;
  height: 44px;
  font-size: 0.9rem;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  gap: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.action-button.edit {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
.action-button.edit:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-button.delete {
  background: var(--bg-tertiary);
  border: 1px solid var(--error-color);
  color: var(--error-color);
}
.action-button.delete:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  border-color: var(--error-color);
}

.action-button.success {
  background: var(--bg-tertiary);
  border: 1px solid #10b981;
  color: #10b981;
}
.action-button.success:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  border-color: #10b981;
}

/* Botón Registrar (PDF) - IDÉNTICO */
.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.register-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.register-button:hover::before {
  left: 100%;
}

.register-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* TABLA - IDÉNTICA */
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
  transition: all 0.2s ease;
}

.users-table tfoot tr {
  background: var(--bg-tertiary);
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
  
  .acciones-header {
    flex-direction: column;
    width: 100%;
  }
  
  .acciones-header button {
    width: 100%;
    justify-content: center;
  }
  
  .grid-info {
    grid-template-columns: 1fr;
  }
  
  .detalle-header-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .acciones-detalle {
    flex-direction: column;
  }
  
  .acciones-detalle .action-button {
    width: 100%;
    justify-content: center;
  }
  
  .users-table {
    font-size: 0.85rem;
  }
  
  .users-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
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
  
  .detalle-card {
    padding: 18px;
  }
  
  .users-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .info-item {
    padding: 15px;
  }
  
  .info-value {
    font-size: 1rem;
  }
  
  .info-value.total-monto {
    font-size: 1.2rem;
  }
}

/* ESTILOS PARA IMPRESIÓN */
@media print {
  .list-header, .acciones-detalle, .btn-volver, .register-button {
    display: none !important;
  }
  
  .list-container {
    padding: 0;
    background: white;
  }
  
  .list-card {
    box-shadow: none;
    border: none;
    padding: 0;
  }
  
  .list-card::before {
    display: none;
  }
  
  .detalle-card {
    box-shadow: none;
    border: 1px solid #ddd;
    margin: 0;
  }
  
  .users-table {
    box-shadow: none;
    border: 1px solid #ddd;
  }
  
  .info-item {
    break-inside: avoid;
  }
  
  body {
    color: black !important;
    background: white !important;
  }
}
</style>