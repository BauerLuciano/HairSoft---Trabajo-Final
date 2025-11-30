<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarModalDetalle }">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de Pedidos</h1>
          <p>Administra y realiza seguimiento de todos los pedidos a proveedores</p>
        </div>
        <button @click="mostrarRegistrarPedido" class="register-button">
          ➕ Nuevo Pedido
        </button>
      </div>

      <!-- Filtros CORREGIDOS -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>ID del Pedido</label>
            <input v-model="filtros.id" type="text" placeholder="Ej: 123" class="filter-input standard-height" @input="aplicarFiltros">
          </div>
          
          <div class="filter-group">
            <label>Proveedor</label>
            <select v-model="filtros.proveedor_id" class="filter-input standard-height" @change="aplicarFiltros">
              <option value="">Todos los proveedores</option>
              <option v-for="proveedor in proveedores" :key="proveedor.id" :value="proveedor.id">
                {{ proveedor.nombre }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input standard-height" @change="aplicarFiltros">
              <option value="">Todos los estados</option>
              <option v-for="estado in estadosPedido" :key="estado.valor" :value="estado.valor">
                {{ estado.texto }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Fecha Desde</label>
            <input v-model="filtros.fecha_desde" type="date" class="filter-input standard-height" @change="aplicarFiltros">
          </div>

          <div class="filter-group">
            <label>Fecha Hasta</label>
            <input v-model="filtros.fecha_hasta" type="date" class="filter-input standard-height" @change="aplicarFiltros">
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn standard-height">🗑️ Limpiar filtros</button>
          </div>
        </div>
      </div>

      <!-- Estado de carga -->
      <div v-if="cargando" class="loading-state">
        <p>🔄 Cargando pedidos...</p>
      </div>

      <!-- Tabla de pedidos MEJORADA -->
      <div v-else class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Proveedor</th>
              <th>Fecha Pedido</th>
              <th>Estado</th>
              <th>Productos</th>
              <th>Total</th>
              <th>Creado por</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pedido in pedidosPaginados" :key="pedido.id">
              <td><strong>#{{ pedido.id }}</strong></td>
              <td>
                <div>
                  <strong>{{ pedido.proveedor_nombre }}</strong>
                  <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 4px;">
                    {{ pedido.proveedor_contacto || 'Sin contacto' }}
                  </div>
                </div>
              </td>
              <td>{{ formatFecha(pedido.fecha_pedido) }}</td>
              <td>
                <span :class="`badge-estado estado-${getEstadoClass(pedido.estado)}`">
                  {{ getEstadoTexto(pedido.estado) }}
                </span>
              </td>
              <td>
                <div class="productos-lista">
                  <div v-for="(producto, index) in getPrimerosProductos(pedido.detalles)" :key="producto.id" 
                       class="producto-item">
                    <span class="producto-nombre">{{ producto.producto_nombre }}</span>
                    <span class="producto-cantidad">x{{ producto.cantidad }}</span>
                  </div>
                  <div v-if="pedido.detalles && pedido.detalles.length > 3" class="mas-productos">
                    +{{ pedido.detalles.length - 3 }} más...
                  </div>
                  <div v-else-if="!pedido.detalles || pedido.detalles.length === 0" class="sin-productos">
                    Sin productos
                  </div>
                </div>
              </td>
              <td><strong>${{ formatPrecio(pedido.total || pedido.total_calculado || 0) }}</strong></td>
              <td>{{ pedido.usuario_creador_nombre || 'Sistema' }}</td>
              <td class="action-buttons">
                <!-- Ojo para ver detalle -->
                <button @click="verDetalle(pedido)" class="action-button view" title="Ver detalle completo">
                  👁️
                </button>
                
                <!-- Lápiz para editar -->
                <button 
                  v-if="pedido.estado === 'PENDIENTE'" 
                  @click="editarPedido(pedido)" 
                  class="action-button edit" 
                  title="Editar pedido">
                  ✏️
                </button>
                
                <!-- Tacho para cancelar -->
                <button 
                  v-if="pedido.puede_cancelar" 
                  @click="cancelarPedido(pedido)" 
                  class="action-button delete" 
                  title="Cancelar pedido">
                  🗑️
                </button>
                
                <!-- Check para recibir - MEJORADO -->
                <button 
                  v-if="puedeRecibirPedido(pedido.estado)" 
                  @click="recibirPedido(pedido)" 
                  class="action-button receive" 
                  title="Recibir pedido"
                  :disabled="recibiendoPedido === pedido.id"
                >
                  {{ recibiendoPedido === pedido.id ? '⏳' : '✅' }}
                  {{ recibiendoPedido === pedido.id ? 'Procesando...' : 'Recibir' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="pedidosPaginados.length === 0 && !cargando" class="no-results">
          <p>📭 No se encontraron pedidos</p>
          <button @click="cargarDatosIniciales" class="btn-reintentar">🔄 Reintentar</button>
        </div>
      </div>

      <!-- Mostrando cantidad -->
      <div v-if="!cargando" class="usuarios-count">
        <p>📊 Mostrando {{ pedidosPaginados.length }} de {{ pedidosFiltrados.length }} pedidos</p>
      </div>

      <!-- Paginación -->
      <div v-if="!cargando && pedidosFiltrados.length > 0" class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">← Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente →</button>
      </div>
    </div>

    <!-- Modal de Detalle MEJORADO -->
    <div v-if="mostrarModalDetalle && pedidoSeleccionado" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button @click="cerrarModal" class="modal-close" title="Cerrar detalle">✖️</button>
        
        <div style="padding: 30px;">
          <div class="list-header" style="border-bottom: 2px solid rgba(14, 165, 233, 0.25); padding-bottom: 20px; margin-bottom: 25px;">
            <div class="header-content">
              <h1>Detalle del Pedido #{{ pedidoSeleccionado.id }}</h1>
              <p>Información completa del pedido y productos solicitados</p>
            </div>
          </div>

          <div class="pedido-detalle">
            <!-- Información del pedido -->
            <div class="info-section" style="margin-bottom: 30px;">
              <h4 style="color: #0ea5e9; margin-bottom: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Información General</h4>
              <div class="info-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div class="info-item" style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 10px; border: 1px solid rgba(100, 100, 100, 0.2);">
                  <label style="color: #000000; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px;">Proveedor:</label>
                  <div style="color: #ffffff; font-weight: 800; margin-top: 5px;">{{ pedidoSeleccionado.proveedor_nombre }}</div>
                </div>
                <div class="info-item" style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 10px; border: 1px solid rgba(100, 100, 100, 0.2);">
                  <label style="color: #000000; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px;">Estado:</label>
                  <div style="margin-top: 5px;">
                    <span :class="`badge-estado estado-${getEstadoClass(pedidoSeleccionado.estado)}`">
                      {{ getEstadoTexto(pedidoSeleccionado.estado) }}
                    </span>
                  </div>
                </div>
                <div class="info-item" style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 10px; border: 1px solid rgba(100, 100, 100, 0.2);">
                  <label style="color: #000000; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px;">Fecha Pedido:</label>
                  <div style="color: #ffffff; font-weight: 800; margin-top: 5px;">{{ formatFecha(pedidoSeleccionado.fecha_pedido) }}</div>
                </div>
                <div class="info-item" style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 10px; border: 1px solid rgba(100, 100, 100, 0.2);">
                  <label style="color: #000000; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px;">Total:</label>
                  <div style="color: #ffffff; font-weight: 900; font-size: 1.2rem; margin-top: 5px;">${{ formatPrecio(pedidoSeleccionado.total || pedidoSeleccionado.total_calculado || 0) }}</div>
                </div>
              </div>
            </div>

            <!-- Productos del pedido MEJORADO -->
            <div class="productos-section" v-if="pedidoSeleccionado.detalles && pedidoSeleccionado.detalles.length > 0">
              <h4 style="color: #0ea5e9; margin-bottom: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">
                Productos Solicitados ({{ pedidoSeleccionado.detalles.length }})
              </h4>
              <div class="productos-list-detalle" style="display: grid; gap: 12px;">
                <div v-for="detalle in pedidoSeleccionado.detalles" :key="detalle.id" 
                     class="producto-detalle-item">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                      <strong style="color: #000000; font-size: 1rem; display: block; margin-bottom: 4px;">
                        {{ detalle.producto_nombre || 'Producto sin nombre' }}
                      </strong>
                      <div style="display: flex; gap: 15px; font-size: 0.85rem;">
                        <span style="color: #9ca3af;" v-if="detalle.producto_codigo">
                          <strong>Código:</strong> {{ detalle.producto_codigo }}
                        </span>
                        <span style="color: #0ea5e9;">
                          <strong>Cantidad:</strong> {{ detalle.cantidad || 0 }}
                        </span>
                      </div>
                    </div>
                    <div style="text-align: right; min-width: 120px;">
                      <div style="color: #9ca3af; font-size: 0.8rem; margin-bottom: 5px;">Precio Unitario</div>
                      <strong style="color: #0ea5e9; font-size: 1.1rem;">${{ formatPrecio(detalle.precio_unitario || 0) }}</strong>
                    </div>
                  </div>
                  <div style="border-top: 1px solid rgba(100, 100, 100, 0.3); margin-top: 10px; padding-top: 10px; text-align: right;">
                    <strong style="color: #10b981; font-size: 1.1rem;">Subtotal: ${{ formatPrecio(detalle.subtotal || 0) }}</strong>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-productos" style="text-align: center; padding: 40px; color: #9ca3af;">
              <p style="font-size: 1.2rem;">📦</p>
              <p>No hay productos en este pedido</p>
            </div>
          </div>

          <div style="border-top: 2px solid rgba(14, 165, 233, 0.25); padding-top: 25px; margin-top: 30px; text-align: center;">
            <button @click="cerrarModal" class="clear-filters-btn" style="min-width: 120px;">
              ✖️ Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

// Estados
const pedidos = ref([])
const proveedores = ref([])
const cargando = ref(false)
const mostrarModalDetalle = ref(false)
const pedidoSeleccionado = ref(null)
const recibiendoPedido = ref(null) // ✅ NUEVO: Control de estado de recepción

// Estados del pedido
const estadosPedido = ref([
  { valor: 'PENDIENTE', texto: 'Pendiente' },
  { valor: 'CONFIRMADO', texto: 'Confirmado' },
  { valor: 'ENTREGADO', texto: 'Entregado' },
  { valor: 'CANCELADO', texto: 'Cancelado' }
])

// Filtros y paginación
const filtros = ref({
  id: '',
  proveedor_id: '',
  estado: '',
  fecha_desde: '',
  fecha_hasta: ''
})

const pagina = ref(1)
const itemsPorPagina = 8

// Cargar datos iniciales
const cargarDatosIniciales = async () => {
  try {
    cargando.value = true
    
    // Cargar proveedores para el filtro
    const proveedoresResponse = await axios.get(`${API_BASE}/usuarios/api/proveedores/`)
    proveedores.value = proveedoresResponse.data.filter(p => p.estado === 'ACTIVO')
    
    // Cargar pedidos
    await buscarPedidos()
    
  } catch (error) {
    console.error('Error cargando datos:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Error al cargar los datos iniciales',
      confirmButtonText: 'Entendido'
    })
  } finally {
    cargando.value = false
  }
}

// Buscar pedidos con filtros
const buscarPedidos = async () => {
  try {
    cargando.value = true
    
    // ✅ CORRECCIÓN: Agregar token
    const token = localStorage.getItem('token');
    
    // ✅ SOLO ENVIAR PARÁMETROS QUE TIENEN VALOR
    const params = new URLSearchParams()
    
    if (filtros.value.id) params.append('id', filtros.value.id)
    if (filtros.value.proveedor_id) params.append('proveedor_id', filtros.value.proveedor_id)
    if (filtros.value.estado) params.append('estado', filtros.value.estado)
    if (filtros.value.fecha_desde) params.append('fecha_desde', filtros.value.fecha_desde)
    if (filtros.value.fecha_hasta) params.append('fecha_hasta', filtros.value.fecha_hasta)
    
    console.log('🔍 Parámetros enviados:', params.toString())
    
    const response = await axios.get(`${API_BASE}/usuarios/api/pedidos/buscar/?${params}`, {
      headers: {
        'Authorization': `Token ${token}`
      }
    })
    
    // ✅ PROCESAR PEDIDOS PARA AGREGAR PROPIEDADES DINÁMICAS
    pedidos.value = procesarPedidos(response.data)
    console.log('✅ Pedidos cargados:', pedidos.value.length)
    
  } catch (error) {
    console.error('❌ Error buscando pedidos:', error)
    console.error('📄 Respuesta del error:', error.response?.data)
    
    // ✅ CORRECCIÓN: Manejo de error 401
    if (error.response?.status === 401) {
      Swal.fire({
        icon: 'error',
        title: 'Sesión expirada',
        text: 'Por favor, inicie sesión nuevamente.',
        confirmButtonText: 'Entendido'
      }).then(() => {
        router.push('/login');
      });
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al cargar pedidos: ' + (error.response?.data?.error || error.message),
        confirmButtonText: 'Entendido'
      });
    }
  } finally {
    cargando.value = false
  }
}

// ✅ NUEVA FUNCIÓN: Procesar pedidos para agregar propiedades dinámicas
const procesarPedidos = (pedidosData) => {
  return pedidosData.map(pedido => ({
    ...pedido,
    puede_recibir: puedeRecibirPedido(pedido.estado),
    puede_cancelar: pedido.estado === 'PENDIENTE' || pedido.estado === 'CONFIRMADO'
  }))
}

// ✅ NUEVA FUNCIÓN: Verificar si un pedido puede ser recibido
const puedeRecibirPedido = (estado) => {
  return estado === 'PENDIENTE' || estado === 'CONFIRMADO'
}

// Aplicar filtros automáticamente
const aplicarFiltros = () => {
  pagina.value = 1 // Resetear a primera página
  buscarPedidos()
}

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = {
    id: '',
    proveedor_id: '',
    estado: '',
    fecha_desde: '',
    fecha_hasta: ''
  }
  buscarPedidos()
}

// NUEVA FUNCIÓN: Obtener primeros productos para mostrar en tabla
const getPrimerosProductos = (detalles) => {
  if (!detalles || detalles.length === 0) return []
  return detalles.slice(0, 3) // Mostrar solo los primeros 3 productos
}

// Navegación
const mostrarRegistrarPedido = () => {
  router.push('/pedidos/crear')
}

const editarPedido = (pedido) => {
  if (pedido.estado === 'PENDIENTE') {
    router.push(`/pedidos/modificar/${pedido.id}`)
  } else {
    Swal.fire({
      icon: 'warning',
      title: 'No editable',
      text: 'Solo se pueden editar pedidos en estado PENDIENTE',
      confirmButtonText: 'Entendido'
    })
  }
}

// Operaciones de estado
const cancelarPedido = async (pedido) => {
  const result = await Swal.fire({
    title: '¿Cancelar Pedido?',
    html: `
      <div style="text-align: left;">
        <p><strong>Pedido #${pedido.id}</strong></p>
        <p><strong>Proveedor:</strong> ${pedido.proveedor_nombre}</p>
        <p><strong>Total:</strong> $${pedido.total || pedido.total_calculado || 0}</p>
        <hr style="margin: 15px 0;">
        <p style="color: #e53e3e; font-weight: bold;">
          ⚠️ Esta acción no se puede deshacer
        </p>
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, cancelar pedido',
    cancelButtonText: 'Cancelar',
    reverseButtons: true
  })
  
  if (!result.isConfirmed) return
  
  try {
    cargando.value = true
    await axios.post(`${API_BASE}/usuarios/api/pedidos/${pedido.id}/cancelar/`)
    
    Swal.fire({
      icon: 'success',
      title: 'Pedido Cancelado',
      text: 'El pedido se ha cancelado exitosamente',
      timer: 2000,
      showConfirmButton: false
    })
    
    await buscarPedidos()
  } catch (error) {
    console.error('Error cancelando pedido:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Error al cancelar el pedido',
      confirmButtonText: 'Entendido'
    })
  } finally {
    cargando.value = false
  }
}

const recibirPedido = async (pedido) => {
  console.log('🔄 Iniciando proceso de recepción para pedido:', pedido.id);
  
  if (recibiendoPedido.value) return;
  
  // Verificar si el pedido puede ser recibido
  if (!puedeRecibirPedido(pedido.estado)) {
    Swal.fire({
      icon: 'warning',
      title: 'No recibible',
      text: 'Solo se pueden recibir pedidos en estado PENDIENTE o CONFIRMADO',
      confirmButtonText: 'Entendido'
    });
    return;
  }
  
  // Confirmación antes de proceder
  const result = await Swal.fire({
    title: '¿Recibir Pedido?',
    html: `
      <div style="text-align: left;">
        <p><strong>Pedido #${pedido.id}</strong></p>
        <p><strong>Proveedor:</strong> ${pedido.proveedor_nombre}</p>
        <p><strong>Total:</strong> $${formatPrecio(pedido.total || pedido.total_calculado || 0)}</p>
        <p><strong>Productos:</strong> ${pedido.detalles?.length || 0} items</p>
        <hr style="margin: 15px 0;">
        <p style="color: #059669; font-weight: bold;">
          ✅ Serás redirigido a la pantalla de recepción para confirmar cantidades
        </p>
      </div>
    `,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#059669',
    cancelButtonColor: '#6b7280',
    confirmButtonText: 'Sí, recibir pedido',
    cancelButtonText: 'Cancelar',
    reverseButtons: true
  });
  
  if (!result.isConfirmed) return;
  
  console.log('✅ Confirmado, redirigiendo a recepción...');
  
  try {
    recibiendoPedido.value = pedido.id;
    
    // ✅ CORRECCIÓN: Agregar token de autenticación
    const token = localStorage.getItem('token');
    
    // Verificar que el endpoint de recepción existe
    const testResponse = await axios.get(`${API_BASE}/usuarios/api/pedidos/${pedido.id}/`, {
      headers: {
        'Authorization': `Token ${token}`
      }
    });
    console.log('📦 Pedido verificado:', testResponse.data);
    
    // Redirigir a la pantalla de recepción
    router.push(`/pedidos/recibir/${pedido.id}`);
    
  } catch (error) {
    console.error('❌ Error verificando pedido:', error);
    
    // ✅ CORRECCIÓN: Manejo de error 401 específico
    if (error.response?.status === 401) {
      Swal.fire({
        icon: 'error',
        title: 'No autorizado',
        text: 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.',
        confirmButtonText: 'Entendido'
      }).then(() => {
        // Redirigir al login o recargar la página
        router.push('/login');
      });
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo acceder al pedido. Verifique que existe.',
        confirmButtonText: 'Entendido'
      });
    }
  } finally {
    // Resetear después de un breve delay para permitir la navegación
    setTimeout(() => {
      recibiendoPedido.value = null;
    }, 1000);
  }
};

// Modal de detalle - VERSIÓN MEJORADA
const verDetalle = async (pedido) => {
  try {
    console.log('🔍 Cargando detalles del pedido:', pedido.id)
    
    // ✅ CORRECCIÓN: Agregar token
    const token = localStorage.getItem('token');
    
    // Intentar cargar detalles completos del pedido
    const response = await axios.get(`${API_BASE}/usuarios/api/pedidos/${pedido.id}/`, {
      headers: {
        'Authorization': `Token ${token}`
      }
    })
    pedidoSeleccionado.value = response.data
    
    console.log('📦 Respuesta completa del pedido:', response.data)
    console.log('🔍 Detalles del pedido cargados:', response.data.detalles)
    
    // ✅ VERIFICACIÓN CRÍTICA: Si no hay detalles en la respuesta, usar los del listado
    if (!pedidoSeleccionado.value.detalles || pedidoSeleccionado.value.detalles.length === 0) {
      console.log('⚠️ No hay detalles en la respuesta, usando detalles del listado')
      if (pedido.detalles && pedido.detalles.length > 0) {
        pedidoSeleccionado.value.detalles = pedido.detalles
        console.log('✅ Detalles del listado asignados:', pedidoSeleccionado.value.detalles)
      } else {
        console.log('❌ No hay detalles disponibles en ningún lugar')
      }
    } else {
      console.log('✅ Detalles cargados correctamente desde la API')
    }
    
    mostrarModalDetalle.value = true
    
  } catch (error) {
    console.error('❌ Error cargando detalle del pedido:', error)
    console.error('🔍 Detalles del error:', error.response?.data)
    
    // ✅ CORRECCIÓN: Manejo de error 401
    if (error.response?.status === 401) {
      Swal.fire({
        icon: 'error',
        title: 'No autorizado',
        text: 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.',
        confirmButtonText: 'Entendido'
      });
      return;
    }
    
    // Si falla, mostrar al menos los datos básicos con los detalles que ya tenemos
    pedidoSeleccionado.value = { ...pedido }
    
    // ✅ Asegurar que tenemos los detalles del listado
    if (!pedidoSeleccionado.value.detalles && pedido.detalles) {
      pedidoSeleccionado.value.detalles = pedido.detalles
    }
    
    console.log('🔄 Usando datos locales del pedido:', pedidoSeleccionado.value)
    mostrarModalDetalle.value = true
  }
}

const cerrarModal = () => {
  mostrarModalDetalle.value = false
  pedidoSeleccionado.value = null
}

// Utilidades
const formatFecha = (fechaString) => {
  if (!fechaString) return '-'
  try {
    const fecha = new Date(fechaString)
    return fecha.toLocaleDateString('es-AR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return fechaString
  }
}

const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  return parseFloat(precio).toFixed(2)
}

const getEstadoClass = (estado) => {
  const clases = {
    'PENDIENTE': 'warning',
    'CONFIRMADO': 'info',
    'ENTREGADO': 'success',
    'CANCELADO': 'danger'
  }
  return clases[estado] || 'secondary'
}

const getEstadoTexto = (estado) => {
  const textos = {
    'PENDIENTE': 'Pendiente',
    'CONFIRMADO': 'Confirmado',
    'ENTREGADO': 'Entregado',
    'CANCELADO': 'Cancelado'
  }
  return textos[estado] || estado
}

// Filtrado y paginación
const pedidosFiltrados = computed(() => {
  return pedidos.value
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(pedidosFiltrados.value.length / itemsPorPagina)))

const pedidosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return pedidosFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

const paginaAnterior = () => { 
  if (pagina.value > 1) pagina.value-- 
}

const paginaSiguiente = () => { 
  if (pagina.value < totalPaginas.value) pagina.value++ 
}

// Ciclo de vida
onMounted(() => {
  cargarDatosIniciales()
})
</script>

<style scoped>

/* Tarjeta principal - CON VARIABLES */
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
  transition: all 0.4s ease;
  border: 1px solid var(--border-color);
}

/* Borde superior azul acero */
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* BADGES DE ESTADO - CON VARIABLES */
.badge-estado {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
}

.estado-warning {
  background: var(--bg-tertiary);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.estado-info {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.estado-success {
  background: var(--bg-tertiary);
  color: #ffffff;
  border: 2px solid #1f4f3f;
  box-shadow: 0 0 12px rgb(255, 255, 255);
}

.estado-danger {
  background: var(--bg-tertiary);
  color: var(--error-color);
  border: 2px solid var(--error-color);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
  text-decoration: line-through;
  opacity: 0.75;
}

.estado-secondary {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  border: 2px solid var(--text-tertiary);
  box-shadow: 0 0 8px rgba(156, 163, 175, 0.2);
}

/* HEADER - CON VARIABLES */
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

/* Botón registrar */
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

/* FILTROS - CON VARIABLES */
.filters-container {
  margin-bottom: 30px;
  background: var(--hover-bg);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 18px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}

.filter-input {
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.filter-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

.clear-filters-btn {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.8px;
}

.clear-filters-btn:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* ESTADOS DE CARGA - CON VARIABLES */
.loading-state {
  text-align: center;
  padding: 80px;
  font-size: 1.3em;
  color: var(--text-secondary);
  font-weight: 600;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
}

.btn-reintentar {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 20px;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.btn-reintentar::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-reintentar:hover::before {
  left: 100%;
}

.btn-reintentar:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5);
}

/* TABLA - CON VARIABLES */
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

/* ESTILOS ESPECÍFICOS DE PEDIDOS */
.productos-lista {
  max-width: 250px;
}

.producto-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid var(--border-color);
}

.producto-item:last-child {
  border-bottom: none;
}

.producto-nombre {
  color: var(--text-primary);
  font-size: 0.85rem;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.producto-cantidad {
  color: #0ea5e9;
  font-weight: 700;
  font-size: 0.8rem;
  background: rgba(14, 165, 233, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  min-width: 30px;
  text-align: center;
}

.mas-productos {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-style: italic;
  text-align: center;
  padding: 4px 0;
  background: var(--hover-bg);
  border-radius: 4px;
  margin-top: 4px;
}

.sin-productos {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-style: italic;
  text-align: center;
  padding: 8px 0;
}

/* BOTONES DE ACCIÓN - CON VARIABLES */
.action-buttons { 
  display: flex; 
  gap: 8px; 
  flex-wrap: wrap; 
}

.action-button {
  padding: 8px 14px;
  border: none;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.action-button.view {
  background: var(--bg-tertiary);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
}

.action-button.view:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
  border-color: var(--accent-color);
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

/* ✅ ESTILO MEJORADO PARA BOTÓN RECIBIR */
.action-button.receive {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  border: 2px solid #059669;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.action-button.receive:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857, #065f46);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.5);
  border-color: #047857;
}

.action-button.receive:active {
  transform: translateY(0);
}

.action-button.receive:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* Altura estándar para inputs */
.standard-height {
  height: 44px !important;
  min-height: 44px;
  box-sizing: border-box;
}

.filter-input.standard-height {
  padding: 12px 14px;
}

.clear-filters-btn.standard-height {
  padding: 12px 18px;
}

/* CONTADOR Y MENSAJES - CON VARIABLES */
.usuarios-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0;
  padding: 18px;
  background: var(--hover-bg);
  border-radius: 12px;
  flex-wrap: wrap;
  gap: 15px;
  border: 1px solid var(--border-color);
}

.usuarios-count p {
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.5px;
  margin: 0;
}

/* PAGINACIÓN - CON VARIABLES */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
}

.pagination button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
}

.pagination button:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.pagination button:disabled {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  transform: none;
  border: 1px solid var(--border-color);
  opacity: 0.5;
}

.pagination span {
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 0.95rem;
}

/* OVERLAY Y MODALES - CON VARIABLES */
.overlay-activo {
  opacity: 0.3;
  filter: blur(5px);
  pointer-events: none;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.88);
  backdrop-filter: blur(12px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeInModal 0.3s ease;
}

@keyframes fadeInModal {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  position: relative;
  animation: slideUp 0.3s ease;
  max-height: 85vh;
  max-width: 90vw;
  width: auto;
  overflow-y: auto;
  border-radius: 16px;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--border-color);
  padding: 0;
  margin: 20px;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: var(--bg-tertiary);
  border: 2px solid var(--error-color);
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--error-color);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  z-index: 1001;
  font-weight: 900;
  font-size: 1.2rem;
}

.modal-close:hover {
  transform: scale(1.15) rotate(90deg);
  box-shadow: 0 6px 25px rgba(239, 68, 68, 0.6);
  background: var(--hover-bg);
  border-color: var(--error-color);
}

/* ESTILOS PARA EL MODAL DE DETALLE */
.producto-detalle-item {
  background: var(--hover-bg);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.producto-detalle-item:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-color);
}

/* SCROLLBAR PERSONALIZADO - CON VARIABLES */
.modal-content::-webkit-scrollbar,
.table-container::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.modal-content::-webkit-scrollbar-track,
.table-container::-webkit-scrollbar-track {
  background: var(--bg-primary);
  border-radius: 6px;
}

.modal-content::-webkit-scrollbar-thumb,
.table-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 6px;
  border: 2px solid var(--bg-primary);
}

.modal-content::-webkit-scrollbar-thumb:hover,
.table-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
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
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    max-width: 95vw;
    margin: 12px;
    border-radius: 12px;
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
  
  .usuarios-count {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
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
  
  .filter-input {
    font-size: 0.9rem;
  }
  
  .badge-estado {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
}
</style>