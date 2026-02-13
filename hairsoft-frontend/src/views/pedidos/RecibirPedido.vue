<template>
  <div class="recepcion-container">
    <div class="recepcion-card">
      <div class="recepcion-header">
        <h1>📦 Recepción de Pedido #{{ pedidoId }}</h1>
        <p>Confirmar ingreso de mercadería y actualización de stock/precios</p>
      </div>

      <div v-if="cargando" class="loading-state">
        <p>🔄 Cargando detalles del pedido...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>❌ {{ error }}</p>
        <button @click="volverAlListado" class="btn-volver">← Volver al listado</button>
      </div>

      <div v-else-if="pedido" class="recepcion-form">
        <div class="pedido-info">
          <div class="info-grid">
            <div class="info-item">
              <label>Proveedor:</label>
              <div class="info-value proveedor-resaltado">
                <strong>{{ pedido.proveedor_nombre }}</strong>
              </div>
            </div>
            <div class="info-item destacada">
              <label>Recepción Esperada:</label>
              <div class="info-value">
                <span v-if="pedido.fecha_esperada_recepcion" style="color: white; font-weight: 700;">
                  {{ formatFechaSimple(pedido.fecha_esperada_recepcion) }}
                </span>
                <span v-else class="texto-pendiente-blanco">Pendiente de confirmación</span>
              </div>
            </div>
            <div class="info-item">
              <label>Total de la Orden:</label>
              <strong class="total-monto">${{ formatPrecio(pedido.total) }}</strong>
            </div>
          </div>
        </div>

        <div class="productos-section">
          <h3>Items de la Orden</h3>
          <div class="table-container">
            <table class="users-table">
              <thead>
                <tr>
                  <th>Producto / Código</th>
                  <th class="text-center">Cant. Ofrecida</th> <th class="text-center">Estado Entrega</th> <th class="text-right">Precio Unit.</th>
                  <th class="text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="detalle in pedido.detalles" :key="detalle.id">
                  <td>
                    <div class="prod-info">
                      <strong>{{ detalle.producto_nombre }}</strong>
                      <small>{{ detalle.producto_codigo }}</small>
                    </div>
                  </td>
                  <td class="text-center">
                    <span class="qty-badge buy">{{ detalle.cantidad }} u.</span>
                  </td>
                  <td class="text-center">
                    <span :class="`badge-estado estado-${getEstadoClass(pedido.estado)}`">
                      {{ getEstadoTexto(pedido.estado) }}
                    </span>
                  </td>
                  <td class="text-right">${{ formatPrecio(detalle.precio_unitario) }}</td>
                  <td class="text-right"><strong>${{ formatPrecio(detalle.subtotal) }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="action-buttons">
          <button @click="volverAlListado" class="btn-cancelar">
            ← Cancelar
          </button>
          <button 
            @click="confirmarRecepcion" 
            :disabled="procesando || pedido.estado === 'ENTREGADO'"
            class="btn-confirmar"
          >
            {{ procesando ? '🔄 Procesando...' : '✅ Confirmar Recepción Completa' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const pedidoId = ref(null)
const pedido = ref(null)
const cargando = ref(true)
const error = ref(null)
const procesando = ref(false)

onMounted(() => {
  pedidoId.value = route.params.id
  cargarPedido()
})

const cargarPedido = async () => {
  try {
    cargando.value = true
    const token = localStorage.getItem('token')
    // 🏁 URL SIN /usuarios/ para que funcione directo en la API
    const response = await axios.get(`${API_BASE}/api/pedidos/${pedidoId.value}/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
    pedido.value = response.data
  } catch (err) {
    error.value = 'No se pudo cargar el pedido.'
    console.error(err)
  } finally {
    cargando.value = false
  }
}

const confirmarRecepcion = async () => {
  const result = await Swal.fire({
    title: '¿Confirmar Recepción Completa?',
    text: "Se sumará el stock al inventario y los precios se actualizarán si subieron.",
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#059669',
    confirmButtonText: 'Sí, recibir todo',
    cancelButtonText: 'Cancelar'
  })

  if (!result.isConfirmed) return

  try {
    procesando.value = true
    const token = localStorage.getItem('token')
    
    // Llamada a tu función recibir_pedido del back (sin prefijo usuarios)
    await axios.post(`${API_BASE}/api/pedidos/${pedidoId.value}/recibir/`, {}, {
      headers: { 'Authorization': `Token ${token}` }
    })

    Swal.fire('¡Recibido!', 'El stock se actualizó y el pedido está ENTREGADO.', 'success')
    router.push('/pedidos')
  } catch (err) {
    Swal.fire('Error', 'No se pudo procesar la recepción.', 'error')
  } finally {
    procesando.value = false
  }
}

const volverAlListado = () => router.push('/pedidos')

// Formateadores y Mapeos de Estado OFICIALES
const formatPrecio = (p) => parseFloat(p || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })
const formatFechaSimple = (f) => new Date(f + 'T00:00:00').toLocaleDateString('es-AR')

const getEstadoTexto = (e) => ({
  'PENDIENTE': 'Pendiente',
  'ENVIADO': 'Enviado a Proveedor',
  'CONFIRMADO': 'Confirmado por Proveedor',
  'ENTREGADO': 'Recibido en Local',
  'CANCELADO': 'Cancelado'
}[e] || e)

const getEstadoClass = (e) => ({
  'PENDIENTE': 'warning',
  'ENVIADO': 'info',
  'CONFIRMADO': 'info',
  'ENTREGADO': 'success',
  'CANCELADO': 'danger'
}[e] || 'secondary')
</script>

<style scoped>
/* Estilos para Recepción Esperada */
.texto-pendiente-blanco {
  color: #ffffff !important;
  font-weight: 700;
}

.destacada {
  background: #1e293b; 
  border-radius: 12px;
  padding: 15px !important;
  border: 1px solid #334155;
}

.proveedor-resaltado {
  color: #0ea5e9;
  font-size: 1.2rem;
}

.recepcion-container { padding: 30px; max-width: 1200px; margin: 0 auto; }
.recepcion-card { background: var(--bg-secondary); border-radius: 24px; padding: 40px; border: 1px solid var(--border-color); position: relative; overflow: hidden; }
.recepcion-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: #059669; border-radius: 24px 24px 0 0; }

.recepcion-header { margin-bottom: 30px; border-bottom: 2px solid var(--border-color); padding-bottom: 20px; }
.recepcion-header h1 { font-size: 2rem; color: var(--text-primary); font-weight: 900; text-transform: uppercase; }

.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
.info-item label { display: block; font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 5px; font-weight: 700; }

.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; }
.users-table th { background: var(--accent-color); color: white; padding: 15px; text-align: left; font-size: 0.8rem; text-transform: uppercase; }
.users-table td { padding: 15px; border-bottom: 1px solid var(--border-color); color: var(--text-primary); }

.qty-badge { padding: 4px 10px; border-radius: 6px; font-weight: 700; background: rgba(14, 165, 233, 0.1); color: #0ea5e9; }
.total-monto { color: #10b981; font-size: 1.4rem; }

.action-buttons { display: flex; justify-content: space-between; margin-top: 30px; }
.btn-confirmar { background: linear-gradient(135deg, #059669, #047857); color: white; border: none; padding: 15px 30px; border-radius: 12px; font-weight: 800; cursor: pointer; text-transform: uppercase; }
.btn-cancelar { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 15px 30px; border-radius: 12px; cursor: pointer; text-transform: uppercase; }

.badge-estado { padding: 5px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
.estado-warning { background: #fef3c7; color: #d97706; }
.estado-info { background: #e0f2fe; color: #0284c7; }
.estado-success { background: #dcfce7; color: #166534; }
.estado-danger { background: #fee2e2; color: #dc2626; }

.prod-info { display: flex; flex-direction: column; }
.prod-info small { color: var(--text-tertiary); }
.text-center { text-align: center; }
.text-right { text-align: right; }
</style>