<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Detalle de Pedido</h1>
          <p>Gestión de Orden de Compra #{{ pedidoId }}</p>
        </div>
        <div class="acciones-header">
          <button 
            v-if="pedido && ['CONFIRMADO', 'ENVIADO'].includes(pedido.estado)" 
            @click="irARecibir" 
            class="register-button"
          >
            <Truck :size="18" /> Recibir Mercadería
          </button>
          <button 
            v-if="pedido && pedido.puede_cancelar" 
            @click="cancelarPedido" 
            class="action-button delete"
          >
            <X :size="18" /> Cancelar
          </button>
          <button @click="$router.push('/pedidos')" class="btn-volver">
            <ChevronLeft :size="18" /> Volver
          </button>
        </div>
      </div>

      <div v-if="cargando" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Buscando datos...</p>
      </div>

      <div v-else-if="pedido" class="detalle-contenido">
        <div class="detalle-card">
          <div class="detalle-header-card">
            <div class="titulo-pedido">
              <h2>Pedido #{{ pedido.id }}</h2>
            </div>
            <div class="fecha-pedido">
              <Calendar :size="16" /> Creado el {{ formatFecha(pedido.fecha_pedido) }}
            </div>
          </div>

          <div class="grid-info">
            <div class="info-item">
              <label>Proveedor</label>
              <div class="info-value proveedor-resaltado">
                <Truck :size="20" />
                <strong>{{ pedido.proveedor_nombre }}</strong>
              </div>
            </div>
            <div class="info-item">
              <label>Responsable</label>
              <div class="info-value">{{ pedido.usuario_creador_nombre || 'Claudio' }}</div>
            </div>
            <div class="info-item">
              <label>Total de la Operación</label>
              <div class="info-value total-monto">${{ formatPrecio(pedido.total) }}</div>
            </div>
          </div>

          <div class="tabla-detalle-container">
            <h3><Package :size="20" /> Items de la Orden</h3>
            <div class="table-container">
              <table class="users-table">
                <thead>
                  <tr>
                    <th>Producto / Código</th>
                    <th class="text-center">Cant. Ofrecida</th> 
                    <th class="text-center">Estado Entrega</th>
                    <th class="text-right">Precio Unit.</th>
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
                      <span class="badge-estado" :class="getClaseEstado(pedido.estado)">
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

          <div v-if="pedido.observaciones" class="observaciones-container">
            <div class="observacion-header"><MessageSquare :size="18" /> <h4>Notas y Plazos</h4></div>
            <div class="observacion-contenido">{{ pedido.observaciones }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ChevronLeft, Truck, Calendar, CalendarCheck, Package, MessageSquare, X } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const pedidoId = route.params.id
const pedido = ref(null)
const cargando = ref(true)

const obtenerPedido = async () => {
  cargando.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_BASE}/api/pedidos/${pedidoId}/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
    pedido.value = response.data
  } catch (err) {
    console.error("Error cargando detalle:", err)
  } finally {
    cargando.value = false
  }
}

const formatFecha = (f) => f ? new Date(f).toLocaleString('es-AR') : '-'
const formatFechaSimple = (f) => f ? new Date(f + 'T00:00:00').toLocaleDateString('es-AR') : '-'
const formatPrecio = (p) => parseFloat(p || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })

// ✅ Mapeo de estados según la clase Pedido de Django
const getEstadoTexto = (e) => {
  const estados = {
    'PENDIENTE': 'Pendiente',
    'ENVIADO': 'Enviado a Proveedor',
    'CONFIRMADO': 'Confirmado por Proveedor',
    'ENTREGADO': 'Recibido en Local',
    'CANCELADO': 'Cancelado'
  }
  return estados[e] || e
}

const getClaseEstado = (e) => ({ 
  'PENDIENTE': 'estado-warning', 
  'ENVIADO': 'estado-info', 
  'CONFIRMADO': 'estado-info', 
  'ENTREGADO': 'estado-success', 
  'CANCELADO': 'estado-danger' 
}[e] || 'estado-secondary')

const irARecibir = () => router.push({ name: 'RecibirPedido', params: { id: pedidoId } })

const cancelarPedido = async () => {
  // Lógica de cancelación
}

onMounted(obtenerPedido)
</script>

<style scoped>
/* No se tocan tus estilos originales, solo se mantienen las clases requeridas */

.texto-pendiente-blanco {
  color: #ffffff !important;
  font-weight: 700;
}

.proveedor-resaltado {
  color: var(--accent-color);
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.destacada {
  background: #1e293b; 
  border-radius: 8px;
  padding: 10px !important;
  border: 1px solid var(--accent-color);
}

.destacada label {
  color: #94a3b8;
}

.destacada .info-value {
  color: #ffffff;
}

/* Base de estilos del componente (sin cambios) */
.list-container { padding: 30px; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; background: var(--bg-primary); }
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1400px; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; transition: all 0.4s ease; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); border-radius: 24px 24px 0 0; }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; }
.acciones-header { display: flex; gap: 15px; align-items: center; }
.btn-volver { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; display: flex; align-items: center; gap: 8px; }
.btn-volver:hover { background: var(--hover-bg); transform: translateY(-2px); }
.loading-state { text-align: center; padding: 80px; display: flex; flex-direction: column; align-items: center; gap: 16px; }
.loading-spinner { width: 40px; height: 40px; border: 3px solid var(--border-color); border-top-color: var(--accent-color); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.detalle-contenido { animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.detalle-card { background: var(--bg-primary); border-radius: 16px; padding: 30px; border: 1px solid var(--border-color); box-shadow: var(--shadow-md); margin-bottom: 30px; }
.detalle-header-card { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid var(--border-color); }
.titulo-pedido { display: flex; align-items: center; gap: 15px; }
.titulo-pedido h2 { margin: 0; font-size: 1.8rem; color: var(--text-primary); font-weight: 800; }
.fecha-pedido { display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-weight: 600; background: var(--bg-tertiary); padding: 10px 18px; border-radius: 12px; border: 1px solid var(--border-color); }
.grid-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
.info-item { background: var(--hover-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--border-color); transition: all 0.3s ease; }
.info-item label { display: block; font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; margin-bottom: 8px; }
.info-value { display: flex; align-items: flex-start; gap: 10px; font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.info-value.total-monto { font-size: 1.5rem; color: #10b981; }
.tabla-detalle-container h3 { font-size: 1.3rem; color: var(--text-primary); margin-bottom: 20px; font-weight: 800; display: flex; align-items: center; gap: 10px; }
.qty-badge { padding: 4px 10px; border-radius: 6px; font-weight: 700; }
.qty-badge.buy { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; }
.text-right { text-align: right; }
.prod-info { display: flex; flex-direction: column; }
.prod-info small { color: var(--text-tertiary); }
.observaciones-container { margin-top: 30px; padding: 20px; background: var(--hover-bg); border-radius: 12px; border: 1px solid var(--border-color); }
.observacion-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.observacion-header h4 { margin: 0; font-size: 1.1rem; color: var(--text-primary); font-weight: 700; }
.observacion-contenido { color: var(--text-secondary); line-height: 1.6; white-space: pre-line; }
.badge-estado { padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; border: 2px solid transparent; }
.estado-warning { background: var(--bg-tertiary); color: #f59e0b; border-color: #f59e0b; }
.estado-info { background: var(--bg-tertiary); color: #0ea5e9; border-color: #0ea5e9; }
.estado-success { background: var(--bg-tertiary); color: #10b981; border-color: #10b981; }
.estado-danger { background: var(--bg-tertiary); color: var(--error-color); border-color: var(--error-color); opacity: 0.75; }
.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); text-transform: uppercase; }
.action-button.delete { background: var(--bg-tertiary); border: 1px solid var(--error-color); color: var(--error-color); padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 8px; text-transform: uppercase; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; border: 1px solid var(--border-color); }
.users-table th { background: var(--accent-color); color: white; padding: 18px 14px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; }
.users-table td { padding: 14px; vertical-align: middle; color: var(--text-secondary); border-bottom: 1px solid var(--border-color); }
</style>