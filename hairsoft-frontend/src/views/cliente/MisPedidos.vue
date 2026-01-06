<template>
  <div class="mis-pedidos-container">
    <h2>Mis Compras</h2>

    <div v-if="loading" class="loading">Cargando pedidos...</div>

    <div v-else-if="pedidos.length === 0" class="empty-state">
      <p>Aún no has realizado compras.</p>
      <router-link to="/productos" class="btn-comprar">Ir al Catálogo</router-link>
    </div>

    <div v-else class="pedidos-list">
      <div v-for="pedido in pedidos" :key="pedido.id" class="pedido-card">
        
        <div class="pedido-header">
          <div class="info-principal">
            <span class="pedido-id">Pedido #{{ pedido.id }}</span>
            <span class="pedido-fecha">{{ formatearFecha(pedido.fecha_creacion) }}</span>
          </div>
          <div :class="['estado-badge', getColorEstado(pedido.estado)]">
            {{ pedido.estado_display }}
          </div>
        </div>

        <div class="pedido-entrega">
          <div class="tipo-entrega">
            <span v-if="pedido.tipo_entrega === 'RETIRO'">🏪 Retiro en Local</span>
            <span v-else>🛵 Envío a Domicilio</span>
          </div>
          <div class="direccion" v-if="pedido.direccion_envio">
            {{ pedido.direccion_envio }}
          </div>
        </div>

        <div class="pedido-productos">
          <div v-for="detalle in pedido.detalles" :key="detalle.id" class="producto-row">
            <span>{{ detalle.cantidad }}x {{ detalle.nombre_producto }}</span>
            <span>${{ Number(detalle.precio_unitario).toLocaleString() }}</span>
          </div>
        </div>

        <div class="pedido-footer">
          <span class="label">Total Pagado:</span>
          <span class="total">${{ Number(pedido.total).toLocaleString() }}</span>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const pedidos = ref([]);
const loading = ref(true);

const cargarPedidos = async () => {
  try {
    const response = await api.get('/pedidos-web/');
    pedidos.value = response.data;
  } catch (error) {
    console.error("Error cargando pedidos", error);
  } finally {
    loading.value = false;
  }
};

const formatearFecha = (fecha) => {
  return new Date(fecha).toLocaleDateString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};

const getColorEstado = (estado) => {
  const mapa = {
    'PENDIENTE_PAGO': 'bg-gray',
    'PAGADO': 'bg-blue',
    'EN_PREPARACION': 'bg-yellow',
    'LISTO_RETIRO': 'bg-purple',
    'EN_CAMINO': 'bg-purple',
    'ENTREGADO': 'bg-green',
    'CANCELADO': 'bg-red'
  };
  return mapa[estado] || 'bg-gray';
};

onMounted(cargarPedidos);
</script>

<style scoped>
.mis-pedidos-container { max-width: 800px; margin: 0 auto; padding: 20px; }
h2 { color: #1e293b; margin-bottom: 20px; font-size: 1.8rem; }

.pedido-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
  margin-bottom: 20px;
  padding: 20px;
  transition: transform 0.2s;
}
.pedido-card:hover { transform: translateY(-2px); box-shadow: 0 8px 12px rgba(0,0,0,0.08); }

.pedido-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
.pedido-id { font-weight: 800; color: #0ea5e9; font-size: 1.1rem; margin-right: 10px; }
.pedido-fecha { color: #64748b; font-size: 0.9rem; }

.estado-badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: white; }
.bg-gray { background: #94a3b8; }
.bg-blue { background: #3b82f6; } /* Pagado */
.bg-yellow { background: #f59e0b; } /* Preparación */
.bg-purple { background: #8b5cf6; } /* Listo/En camino */
.bg-green { background: #10b981; } /* Entregado */
.bg-red { background: #ef4444; } /* Cancelado */

.pedido-entrega { background: #f8fafc; padding: 10px; border-radius: 8px; margin-bottom: 15px; font-size: 0.9rem; color: #334155; }
.tipo-entrega { font-weight: 600; margin-bottom: 4px; }

.pedido-productos { margin-bottom: 15px; }
.producto-row { display: flex; justify-content: space-between; margin-bottom: 5px; color: #475569; font-size: 0.95rem; }

.pedido-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 10px; border-top: 2px dashed #e2e8f0; }
.label { font-weight: 600; color: #334155; }
.total { font-weight: 800; font-size: 1.2rem; color: #0f172a; }

.empty-state { text-align: center; padding: 40px; color: #64748b; }
.btn-comprar { display: inline-block; margin-top: 10px; background: #0ea5e9; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; }
</style>