<template>
  <div class="venta-container">
    <!-- Header -->
    <div class="venta-header">
      <div class="header-content">
        <div class="titulo-section">
          <h2>Modificar Venta #{{ ventaId }}</h2>
          <div class="venta-info">
            <span class="info-item">📅 {{ formatFecha(ventaOriginal?.fecha) }}</span>
            <span :class="ventaOriginal?.anulada ? 'estado-badge anulada' : 'estado-badge activa'">
              {{ ventaOriginal?.anulada ? '❌ ANULADA' : '✅ ACTIVA' }}
            </span>
            <span class="info-item" v-if="ventaOriginal">
              Total Original: ${{ formatPrecio(ventaOriginal.total) }}
            </span>
          </div>
        </div>
        <button @click="$emit('cancelar')" class="btn-cerrar" title="Cerrar">
          <span>×</span>
        </button>
      </div>
    </div>

    <!-- Layout -->
    <div class="layout">
      
      <!-- Columna productos -->
      <div class="columna-productos">
        <div class="seccion-busqueda">
          <div class="busqueda-header">
            <h3>📦 Productos Disponibles</h3>
            <div class="contador">
              {{ productosFiltrados.length }} productos
            </div>
          </div>
          <div class="filtros">
            <div class="search-container">
              <input 
                v-model="filtroNombre" 
                placeholder="Buscar por nombre..." 
                class="input-busqueda"
              />
              <span class="search-icon">🔍</span>
            </div>
            <select v-model="filtroCategoria" class="select-categoria">
              <option value="">Todas las categorías</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                {{ cat.nombre }}
              </option>
            </select>
          </div>
        </div>

        <!-- Grid -->
        <div class="productos-grid">
          <div 
            v-for="producto in productosFiltrados" 
            :key="producto.id" 
            class="producto-card"
            :class="{
              'sin-stock': producto.stock === 0,
              'stock-bajo': producto.stock > 0 && producto.stock <= 5
            }"
          >
            <div class="producto-content">
              <div class="producto-header">
                <span class="nombre-producto">{{ producto.nombre }}</span>
                <span class="precio-producto">${{ producto.precio }}</span>
              </div>
              
              <div class="stock-section">
                <div class="stock-visual">
                  <div class="stock-bar">
                    <div 
                      class="stock-fill" 
                      :class="getStockClass(producto.stock)"
                      :style="{ width: getStockWidth(producto.stock) }"
                    ></div>
                  </div>
                  <span class="stock-text" :class="getStockTextClass(producto.stock)">
                    {{ producto.stock }} unidades
                  </span>
                </div>
                <span v-if="producto.stock === 0" class="badge-stock cero">SIN STOCK</span>
                <span v-else-if="producto.stock <= 5" class="badge-stock bajo">STOCK BAJO</span>
              </div>

              <div class="actions-section">
                <div class="cantidad-controls">
                  <button 
                    @click="decrementarCantidad(producto.id)"
                    :disabled="cantidadesTemp[producto.id] <= 1"
                    class="btn-cantidad"
                  >−</button>
                  
                  <input 
                    type="number" 
                    min="1" 
                    :max="producto.stock" 
                    v-model.number="cantidadesTemp[producto.id]" 
                    :disabled="producto.stock === 0"
                    class="input-cantidad"
                  />
                  
                  <button 
                    @click="incrementarCantidad(producto.id)"
                    :disabled="cantidadesTemp[producto.id] >= producto.stock"
                    class="btn-cantidad"
                  >+</button>
                </div>
                
                <button 
                  @click="agregarAlCarrito(producto)" 
                  :disabled="producto.stock === 0 || cantidadesTemp[producto.id] > producto.stock || cantidadesTemp[producto.id] < 1"
                  class="btn-agregar"
                  :class="getAgregarBtnClass(producto.stock)"
                >
                  <span class="btn-icon">
                    {{ producto.stock === 0 ? '⛔' : producto.stock <= 5 ? '⚠️' : '➕' }}
                  </span>
                  <span class="btn-text">
                    {{ producto.stock === 0 ? 'Sin Stock' : 'Agregar' }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="productosDisponibles.length === 0" class="estado-vacio">
          <div class="empty-state">
            <span class="empty-icon">📦</span>
            <h4>No hay productos disponibles</h4>
            <p>No se encontraron productos en el sistema</p>
            <button @click="recargarDatos" class="btn-recargar">
              🔄 Recargar Productos
            </button>
          </div>
        </div>
      </div>

      <!-- Columna resumen -->
      <div class="columna-resumen">
        
        <!-- Carrito -->
        <div class="resumen-card">
          <div class="resumen-header">
            <h3>🛒 Carrito de Venta</h3>
            <div class="carrito-stats">
              <span class="items-count">{{ carrito.length }} items</span>
              <span class="items-total">${{ total.toFixed(2) }}</span>
            </div>
          </div>
          
          <div v-if="carrito.length" class="carrito-lista">
            <div 
              v-for="(item, index) in carrito" 
              :key="index" 
              class="carrito-item"
              @mouseenter="hoverItem = index"
              @mouseleave="hoverItem = null"
            >
              <div class="item-content">
                <div class="item-info">
                  <span class="item-nombre">{{ item.producto.nombre }}</span>
                  <span class="item-detalles">
                    ${{ item.producto.precio }} × {{ item.cantidad }} unidades
                  </span>
                </div>
                <div class="item-subtotal">
                  ${{ item.subtotal }}
                </div>
              </div>
              <button 
                @click="quitarDelCarrito(index)" 
                class="btn-quitar"
                :class="{ 'hovered': hoverItem === index }"
              >
                <span class="quitar-icon">🗑️</span>
              </button>
            </div>
          </div>
          
          <div v-else class="carrito-vacio">
            <div class="empty-cart">
              <span class="cart-icon">🛒</span>
              <p>El carrito está vacío</p>
              <small>Agregá productos desde la lista</small>
            </div>
          </div>
        </div>

        <!-- MÉTODO DE PAGO -->
        <div class="pago-card">
          <h3>💳 Método de Pago</h3>
          <div class="pago-selector">
            <select 
              v-model.number="datosVenta.medio_pago" 
              class="select-pago"
              :class="{ 'selected': datosVenta.medio_pago }"
            >
              <option :value="null" disabled>Selecciona un método de pago</option>
              <option v-for="mp in metodosPago" :key="mp.id" :value="mp.id">
                {{ formatMetodoPago(mp) }}
              </option>
            </select>
            
            <div v-if="metodoPagoSeleccionado" class="pago-info">
              <div class="pago-details">
                <span class="pago-tipo">{{ metodoPagoSeleccionado.tipo }}</span>
                <span class="pago-desc">{{ getPagoDescription(metodoPagoSeleccionado.tipo) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Totales -->
        <div class="totales-card">
          <div class="totales-header">
            <h4>Resumen de Totales</h4>
          </div>
          <div class="total-comparison">
            <div class="total-line original">
              <span>Total Original:</span>
              <span class="amount" v-if="ventaOriginal">
                ${{ formatPrecio(ventaOriginal.total) }}
              </span>
            </div>
            
            <div class="total-line nuevo">
              <span>Nuevo Total:</span>
              <span class="amount final">${{ total.toFixed(2) }}</span>
            </div>
            
            <div 
              class="total-line diferencia"
              :class="getDiferenciaClass()"
              v-if="ventaOriginal"
            >
              <span>Diferencia:</span>
              <span class="amount">
                {{ getDiferenciaSymbol() }}${{ Math.abs(total - ventaOriginal.total).toFixed(2) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="acciones-card">
          <button 
            @click="validarYActualizarVenta" 
            :disabled="carrito.length === 0 || !datosVenta.medio_pago || procesando" 
            class="btn-primary"
            :class="{
              'disabled': carrito.length === 0 || !datosVenta.medio_pago,
              'processing': procesando,
              'ready': carrito.length > 0 && datosVenta.medio_pago
            }"
          >
            <span class="btn-icon" v-if="!procesando">💾</span>
            <span class="btn-icon processing" v-else>⏳</span>
            <span class="btn-text">
              {{ procesando ? 'Actualizando...' : 'Actualizar Venta' }}
            </span>
          </button>
          
          <button @click="$emit('cancelar')" class="btn-secondary">
            <span class="btn-icon">❌</span>
            <span class="btn-text">Cancelar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Mensaje flotante -->
    <div 
      v-if="mensaje" 
      :class="['notificacion', error ? 'error' : 'success']"
      @click="mensaje = ''"
    >
      <span class="notificacion-icon">
        {{ error ? '⚠️' : '✅' }}
      </span>
      <span class="notificacion-text">{{ mensaje }}</span>
      <button class="notificacion-close">×</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Swal from 'sweetalert2'

const API_BASE_URL = 'http://localhost:8000'

export default {
  name: 'ModificarVenta',
  props: {
    ventaId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      productosDisponibles: [],
      categorias: [],
      metodosPago: [],
      carrito: [],
      filtroNombre: '',
      filtroCategoria: '',
      cantidadesTemp: {},
      procesando: false,
      mensaje: '',
      error: false,
      ventaOriginal: null,
      hoverItem: null,
      datosVenta: {
        medio_pago: null
      }
    }
  },
  computed: {
    productosFiltrados() {
      let productos = this.productosDisponibles;
      
      if (this.filtroNombre) {
        productos = productos.filter(p => 
          p.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase())
        );
      }
      
      if (this.filtroCategoria) {
        productos = productos.filter(p => 
          p.categoria_id === parseInt(this.filtroCategoria)
        );
      }
      
      return productos;
    },
    total() {
      return this.carrito.reduce((acc, item) => acc + item.subtotal, 0);
    },
    metodoPagoSeleccionado() {
      if (!this.datosVenta.medio_pago) return null;
      return this.metodosPago.find(mp => mp.id === this.datosVenta.medio_pago);
    },
    horasDesdeVenta() {
      if (!this.ventaOriginal?.fecha) return 0;
      return (new Date() - new Date(this.ventaOriginal.fecha)) / (1000 * 60 * 60);
    }
  },
  methods: {
    // Métodos para métodos de pago
    formatMetodoPago(mp) {
      // Formatea el nombre para mostrar mejor
      const nombres = {
        'EFECTIVO': '💰 Efectivo',
        'TARJETA': '💳 Tarjeta',
        'TRANSFERENCIA': '📲 Transferencia'
      };
      return nombres[mp.nombre] || mp.nombre;
    },
    
    getPagoDescription(tipo) {
      const descripciones = {
        'EFECTIVO': 'Pago en efectivo',
        'TARJETA': 'Tarjeta crédito/débito', 
        'TRANSFERENCIA': 'QR MP, alias, etc.'
      };
      return descripciones[tipo] || tipo;
    },

    // Métodos visuales para stock
    getStockClass(stock) {
      if (stock === 0) return 'sin-stock-fill';
      if (stock <= 5) return 'bajo-stock-fill';
      return 'normal-stock-fill';
    },
    
    getStockWidth(stock) {
      const max = 20; // Stock máximo para visualización
      return Math.min((stock / max) * 100, 100) + '%';
    },
    
    getStockTextClass(stock) {
      if (stock === 0) return 'text-sin-stock';
      if (stock <= 5) return 'text-bajo-stock';
      return 'text-normal-stock';
    },
    
    getAgregarBtnClass(stock) {
      if (stock === 0) return 'btn-sin-stock';
      if (stock <= 5) return 'btn-bajo-stock';
      return 'btn-normal-stock';
    },
    
    getDiferenciaClass() {
      if (!this.ventaOriginal) return '';
      return this.total > this.ventaOriginal.total ? 'positiva' : 'negativa';
    },
    
    getDiferenciaSymbol() {
      if (!this.ventaOriginal) return '';
      return this.total > this.ventaOriginal.total ? '+' : '−';
    },

    // Métodos existentes
    incrementarCantidad(productoId) {
      if (this.cantidadesTemp[productoId] < this.productosDisponibles.find(p => p.id === productoId).stock) {
        this.cantidadesTemp[productoId]++;
      }
    },
    
    decrementarCantidad(productoId) {
      if (this.cantidadesTemp[productoId] > 1) {
        this.cantidadesTemp[productoId]--;
      }
    },

    async cargarDatosVenta() {
      try {
        console.log(`📥 Cargando venta #${this.ventaId}...`);
        
        await this.cargarDatosAdicionales();
        
        const response = await axios.get(`${API_BASE_URL}/usuarios/api/ventas/${this.ventaId}/editar/`);
        const ventaData = response.data;
        
        console.log('📦 Datos de venta recibidos:', ventaData);
        
        this.ventaOriginal = { ...ventaData };
        this.datosVenta.medio_pago = ventaData.medio_pago;
        
        this.carrito = [];
        if (ventaData.detalles && ventaData.detalles.length > 0) {
          this.carrito = ventaData.detalles.map(detalle => {
            const productoActual = this.productosDisponibles.find(p => p.id === detalle.producto) || {
              id: detalle.producto,
              nombre: detalle.producto_nombre || 'Producto',
              precio: parseFloat(detalle.precio_unitario),
              stock: 0,
              categoria_id: null
            };
            
            return {
              producto: productoActual,
              cantidad: detalle.cantidad,
              subtotal: parseFloat(detalle.subtotal)
            };
          });
        }
        
        this.productosDisponibles.forEach(p => {
          this.cantidadesTemp[p.id] = 1;
        });
        
        this.mostrarMensaje('✅ Datos de venta cargados correctamente');
        
      } catch (error) {
        console.error('❌ Error cargando datos de venta:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error al Cargar',
          text: 'No se pudieron cargar los datos de la venta',
          confirmButtonText: 'Entendido'
        });
      }
    },

    async cargarDatosAdicionales() {
      try {
        const productosResponse = await axios.get(`${API_BASE_URL}/usuarios/api/productos/`);
        this.productosDisponibles = productosResponse.data || [];
        
        const metodosPagoResponse = await axios.get(`${API_BASE_URL}/usuarios/api/metodos-pago/`);
        this.metodosPago = metodosPagoResponse.data || [];
        console.log('💳 Métodos de pago cargados:', this.metodosPago);
        
        const categoriasResponse = await axios.get(`${API_BASE_URL}/usuarios/api/categorias/productos/`);
        this.categorias = categoriasResponse.data || [];
        
      } catch (error) {
        console.error('❌ Error cargando datos adicionales:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error al Cargar',
          text: 'No se pudieron cargar los productos y categorías',
          confirmButtonText: 'Entendido'
        });
      }
    },

    agregarAlCarrito(producto) {
      const cantidad = this.cantidadesTemp[producto.id] || 1;
      
      if (cantidad < 1) {
        this.mostrarMensaje('❌ La cantidad debe ser al menos 1', true);
        return;
      }
      
      if (cantidad > producto.stock) {
        this.mostrarMensaje(`❌ Stock insuficiente. Solo ${producto.stock} disponibles`, true);
        this.cantidadesTemp[producto.id] = producto.stock;
        return;
      }
      
      if (producto.stock === 0) {
        this.mostrarMensaje('❌ Producto sin stock disponible', true);
        return;
      }

      const productoExistente = this.carrito.find(item => item.producto.id === producto.id);
      const cantidadEnCarrito = productoExistente ? productoExistente.cantidad : 0;
      const stockDisponible = producto.stock - cantidadEnCarrito;
      
      if (cantidad > stockDisponible) {
        this.mostrarMensaje(`❌ Solo puedes agregar ${stockDisponible} unidades más`, true);
        this.cantidadesTemp[producto.id] = stockDisponible;
        return;
      }
      
      if (productoExistente) {
        productoExistente.cantidad += cantidad;
        productoExistente.subtotal = productoExistente.cantidad * producto.precio;
      } else {
        this.carrito.push({
          producto: { ...producto },
          cantidad: cantidad,
          subtotal: cantidad * producto.precio
        });
      }
      
      this.cantidadesTemp[producto.id] = 1;
      this.mostrarMensaje(`✅ "${producto.nombre}" agregado al carrito`);
    },

    quitarDelCarrito(index) {
      const productoNombre = this.carrito[index].producto.nombre;
      this.carrito.splice(index, 1);
      this.mostrarMensaje(`🗑️ "${productoNombre}" removido del carrito`);
    },

    async validarYActualizarVenta() {
      if (this.ventaOriginal?.anulada) {
        Swal.fire({
          icon: 'error',
          title: 'Venta Anulada',
          text: 'No se puede modificar una venta anulada',
          confirmButtonText: 'Entendido'
        });
        return;
      }

      if (this.carrito.length === 0) {
        Swal.fire({
          icon: 'error',
          title: 'Carrito Vacío',
          text: 'Debe agregar al menos un producto',
          confirmButtonText: 'Entendido'
        });
        return;
      }
      
      if (!this.datosVenta.medio_pago) {
        Swal.fire({
          icon: 'error',
          title: 'Método de Pago',
          text: 'Debe seleccionar un método de pago',
          confirmButtonText: 'Entendido'
        });
        return;
      }

      if (this.horasDesdeVenta > 24) {
        const result = await Swal.fire({
          title: 'Venta Antigua',
          html: `Esta venta tiene <strong>${Math.floor(this.horasDesdeVenta)} horas</strong>.<br>¿Seguro de modificarla?`,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Sí, modificar',
          cancelButtonText: 'Cancelar'
        });
        
        if (!result.isConfirmed) return;
      }

      const { value: motivo } = await Swal.fire({
        title: 'Motivo de modificación',
        input: 'select',
        inputOptions: {
          'ERROR_PRECIO': 'Error en precio',
          'CAMBIO_PRODUCTOS': 'Cambio en productos',
          'ERROR_CLIENTE': 'Error en cliente/datos',
          'CAMBIO_METODO_PAGO': 'Cambio método de pago',
          'AGREGAR_PRODUCTOS': 'Agregar productos',
          'OTRO': 'Otro motivo'
        },
        inputPlaceholder: 'Selecciona el motivo',
        showCancelButton: true,
        inputValidator: (value) => {
          if (!value) return 'Debes seleccionar un motivo';
        }
      });

      if (!motivo) return;

      const confirmResult = await Swal.fire({
        title: '¿Confirmar modificación?',
        html: `Venta #${this.ventaId}<br><strong>Total: $${this.total.toFixed(2)}</strong>`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, modificar',
        cancelButtonText: 'Cancelar'
      });

      if (confirmResult.isConfirmed) {
        await this.actualizarVenta(motivo);
      }
    },

    async actualizarVenta(motivo) {
      this.procesando = true;

      Swal.fire({
        title: 'Actualizando Venta...',
        text: 'Por favor espere',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        }
      });

      const detalles = this.carrito.map(item => ({
        producto: item.producto.id,
        cantidad: item.cantidad,
        precio_unitario: parseFloat(item.producto.precio),
        subtotal: parseFloat(item.subtotal)
      }));
      
      const payload = { 
        total: parseFloat(this.total),
        tipo: 'PRODUCTO', 
        medio_pago: parseInt(this.datosVenta.medio_pago),
        detalles,
        cliente: null,
        motivo_modificacion: motivo,
        usuario_modificacion: 'usuario_actual'
      };

      try {
        const response = await axios.put(
          `${API_BASE_URL}/usuarios/api/ventas/${this.ventaId}/actualizar/`, 
          payload
        );
        
        if (response.data.status === 'ok') {
          Swal.close();
          
          await Swal.fire({
            icon: 'success',
            title: 'Venta Actualizada',
            text: `Venta #${this.ventaId} modificada correctamente`,
            timer: 3000,
            showConfirmButton: false
          });
          
          setTimeout(() => {
            this.$emit('venta-actualizada');
          }, 1500);
        } else {
          Swal.close();
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: response.data.error || 'Error desconocido',
            confirmButtonText: 'Entendido'
          });
        }
        
      } catch (error) {
        console.error('❌ Error actualizando venta:', error);
        Swal.close();
        
        const errorMsg = error.response?.data?.error || error.response?.data?.message || 'Error al actualizar la venta';
        Swal.fire({
          icon: 'error',
          title: 'Error al Actualizar',
          text: errorMsg,
          confirmButtonText: 'Entendido'
        });
      } finally {
        this.procesando = false;
      }
    },

    async recargarDatos() {
      await this.cargarDatosVenta();
    },

    mostrarMensaje(mensaje, esError = false) {
      this.mensaje = mensaje;
      this.error = esError;
      setTimeout(() => {
        this.mensaje = '';
      }, 4000);
    },

    formatFecha(fecha) {
      if (!fecha) return '–';
      try {
        const dateObj = new Date(fecha);
        if (isNaN(dateObj.getTime())) return 'Fecha inválida';
        return dateObj.toLocaleString('es-AR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        });
      } catch (e) {
        return 'Error fecha';
      }
    },

    formatPrecio(precio) {
      if (!precio) return '0.00';
      return parseFloat(precio).toFixed(2);
    }
  },
  async mounted() {
    console.log('🚀 Componente ModificarVenta montado');
    await this.cargarDatosVenta();
  }
}
</script>

<style scoped>
/* CONTENEDOR PRINCIPAL */
.venta-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 70vh;
}

/* HEADER */
.venta-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #dee2e6;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.titulo-section h2 {
  margin: 0 0 6px 0;
  color: #495057;
  font-size: 1.4rem;
  font-weight: 500;
}

.venta-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.info-item {
  color: #6c757d;
  font-size: 0.85rem;
}

.estado-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.estado-badge.activa {
  background: #d4edda;
  color: #155724;
}

.estado-badge.anulada {
  background: #f5c6cb;
  color: #721c24;
}

.btn-cerrar {
  background: #e9ecef;
  color: #6c757d;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.1rem;
  transition: background 0.2s;
}

.btn-cerrar:hover {
  background: #dee2e6;
}

/* LAYOUT */
.layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 16px;
}

/* COLUMNA PRODUCTOS */
.columna-productos {
  background: #ffffff;
  border-radius: 4px;
  padding: 16px;
  border: 1px solid #dee2e6;
}

.seccion-busqueda {
  margin-bottom: 16px;
}

.busqueda-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.busqueda-header h3 {
  margin: 0;
  color: #495057;
  font-size: 1.1rem;
  font-weight: 500;
}

.contador {
  background: #e9ecef;
  color: #6c757d;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
}

.filtros {
  display: flex;
  gap: 12px;
}

.search-container {
  flex: 1;
  position: relative;
}

.input-busqueda {
  width: 100%;
  padding: 10px 14px 10px 36px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.85rem;
  transition: border 0.2s;
}

.input-busqueda:focus {
  border-color: #80bdff;
  outline: none;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #adb5bd;
}

.select-categoria {
  padding: 10px 14px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  min-width: 180px;
  font-size: 0.85rem;
  transition: border 0.2s;
}

.select-categoria:focus {
  border-color: #80bdff;
  outline: none;
}

/* GRID PRODUCTOS */
.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
}

.producto-card {
  background: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 16px;
  transition: box-shadow 0.2s;
}

.producto-card:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.producto-card.sin-stock {
  opacity: 0.7;
}

.producto-card.stock-bajo {
  border-left: 2px solid #ffc107;
}

.producto-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.producto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nombre-producto {
  font-weight: 500;
  color: #495057;
  font-size: 0.95rem;
}

.precio-producto {
  font-weight: 500;
  color: #28a745;
  font-size: 1rem;
}

.stock-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stock-visual {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stock-bar {
  flex: 1;
  height: 5px;
  background: #e9ecef;
  border-radius: 2.5px;
  overflow: hidden;
}

.stock-fill {
  height: 100%;
  transition: width 0.2s;
}

.sin-stock-fill {
  background: #dc3545;
}

.bajo-stock-fill {
  background: #ffc107;
}

.normal-stock-fill {
  background: #28a745;
}

.stock-text {
  font-size: 0.75rem;
  font-weight: 400;
}

.text-sin-stock { color: #dc3545; }
.text-bajo-stock { color: #ffc107; }
.text-normal-stock { color: #28a745; }

.badge-stock {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.badge-stock.bajo {
  background: #fff3cd;
  color: #856404;
}

.badge-stock.cero {
  background: #f8d7da;
  color: #721c24;
}

.actions-section {
  display: flex;
  gap: 8px;
  align-items: center;
}

.cantidad-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #e9ecef;
  border-radius: 4px;
  padding: 3px;
}

.btn-cantidad {
  width: 28px;
  height: 28px;
  border: none;
  background: #ffffff;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  color: #495057;
  transition: background 0.2s;
}

.btn-cantidad:hover:not(:disabled) {
  background: #dee2e6;
}

.btn-cantidad:disabled {
  opacity: 0.5;
}

.input-cantidad {
  width: 45px;
  text-align: center;
  padding: 5px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.input-cantidad:focus {
  border-color: #80bdff;
  outline: none;
}

.input-cantidad:disabled {
  background: #e9ecef;
  color: #adb5bd;
}

.btn-agregar {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.85rem;
  transition: opacity 0.2s;
}

.btn-agregar:hover:not(.btn-sin-stock) {
  opacity: 0.85;
}

.btn-sin-stock {
  background: #adb5bd;
  color: #ffffff;
  cursor: not-allowed;
}

.btn-bajo-stock {
  background: #ffc107;
  color: #212529;
}

.btn-normal-stock {
  background: #28a745;
  color: #ffffff;
}

.btn-icon {
  font-size: 0.9rem;
}

.btn-text {
  font-weight: 500;
}

.estado-vacio {
  text-align: center;
  padding: 30px 16px;
}

.empty-state {
  max-width: 250px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  opacity: 0.4;
}

.empty-state h4 {
  color: #495057;
  margin-bottom: 6px;
  font-size: 1.1rem;
}

.empty-state p {
  color: #6c757d;
  margin-bottom: 16px;
  font-size: 0.85rem;
}

.btn-recargar {
  background: #007bff;
  color: #ffffff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-recargar:hover {
  background: #0069d9;
}

/* COLUMNA RESUMEN */
.columna-resumen {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.resumen-card,
.pago-card,
.totales-card,
.acciones-card {
  background: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 16px;
}

/* CARRITO */
.resumen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.resumen-header h3 {
  margin: 0;
  color: #495057;
  font-size: 1.1rem;
  font-weight: 500;
}

.carrito-stats {
  display: flex;
  gap: 8px;
}

.items-count {
  background: #e9ecef;
  color: #6c757d;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
}

.items-total {
  background: #d4edda;
  color: #155724;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
}

.carrito-lista {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.carrito-item {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.carrito-item:hover {
  background: #e9ecef;
}

.item-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-info {
  flex: 1;
}

.item-nombre {
  font-weight: 400;
  color: #495057;
  display: block;
  font-size: 0.85rem;
}

.item-detalles {
  color: #6c757d;
  font-size: 0.75rem;
}

.item-subtotal {
  font-weight: 500;
  color: #28a745;
  font-size: 0.85rem;
}

.btn-quitar {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  opacity: 0.6;
  transition: opacity 0.2s, background 0.2s;
}

.btn-quitar:hover, .btn-quitar.hovered {
  opacity: 1;
  background: #f5c6cb;
}

.quitar-icon {
  font-size: 0.9rem;
}

.carrito-vacio {
  text-align: center;
  padding: 24px 12px;
  color: #6c757d;
}

.cart-icon {
  font-size: 2rem;
  margin-bottom: 8px;
  opacity: 0.4;
}

.carrito-vacio p {
  margin: 0 0 4px 0;
  font-size: 0.95rem;
}

.carrito-vacio small {
  font-size: 0.75rem;
}

/* PAGO */
.pago-card h3 {
  margin: 0 0 12px 0;
  color: #495057;
  font-size: 1.1rem;
  font-weight: 500;
}

.pago-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.select-pago {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.85rem;
  transition: border 0.2s;
}

.select-pago:focus {
  border-color: #80bdff;
  outline: none;
}

.select-pago.selected {
  border-color: #28a745;
}

.pago-info {
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.pago-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pago-tipo {
  font-weight: 500;
  color: #007bff;
  font-size: 0.85rem;
}

.pago-desc {
  color: #6c757d;
  font-size: 0.75rem;
}

/* TOTALES */
.totales-card {
  background: #f8f9fa;
  color: #495057;
}

.totales-header {
  margin-bottom: 12px;
}

.totales-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
}

.total-comparison {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.total-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.total-line:not(:last-child) {
  border-bottom: 1px solid #dee2e6;
}

.total-line.original {
  opacity: 0.8;
}

.total-line.nuevo {
  font-size: 1rem;
  font-weight: 500;
}

.total-line.diferencia {
  padding: 6px 10px;
  border-radius: 4px;
  font-weight: 500;
}

.total-line.diferencia.positiva {
  background: #d4edda;
  color: #155724;
}

.total-line.diferencia.negativa {
  background: #f5c6cb;
  color: #721c24;
}

.amount {
  font-weight: 500;
}

.amount.final {
  font-size: 1.1rem;
}

/* ACCIONES */
.acciones-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-primary {
  padding: 10px 14px;
  background: #28a745;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-primary:hover:not(.disabled):not(.processing) {
  background: #218838;
}

.btn-primary.disabled, .btn-primary.processing {
  background: #adb5bd;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 14px;
  background: #e9ecef;
  color: #495057;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-secondary:hover {
  background: #dee2e6;
}

/* NOTIFICACIÓN */
.notificacion {
  position: fixed;
  top: 16px;
  right: 16px;
  padding: 10px 14px;
  border-radius: 4px;
  font-weight: 400;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.notificacion.success {
  background: #d4edda;
  color: #155724;
}

.notificacion.error {
  background: #f5c6cb;
  color: #721c24;
}

.notificacion:hover {
  opacity: 0.9;
}

.notificacion-icon {
  font-size: 0.9rem;
}

.notificacion-text {
  flex: 1;
  font-size: 0.85rem;
}

.notificacion-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 1rem;
  cursor: pointer;
}

/* RESPONSIVE */
@media (max-width: 1200px) {
  .layout {
    grid-template-columns: 1fr;
  }
  
  .columna-resumen {
    order: -1;
  }
}

@media (max-width: 768px) {
  .venta-container {
    padding: 12px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .venta-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .productos-grid {
    grid-template-columns: 1fr;
  }
  
  .filtros {
    flex-direction: column;
  }
  
  .search-container,
  .select-categoria {
    width: 100%;
  }
}
</style>