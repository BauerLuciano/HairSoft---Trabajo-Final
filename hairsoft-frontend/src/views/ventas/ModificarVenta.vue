<template>
  <div class="venta-container">
    <h2>Modificar Venta #{{ ventaId }}</h2>

    <!-- Filtros de productos -->
    <div class="input-group">
      <input v-model="filtroNombre" placeholder="Buscar producto por nombre" class="input-modern"/>
      <select v-model="filtroCategoria" class="select-modern">
        <option value="">Todas las categorías</option>
        <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
      </select>
    </div>

    <!-- Lista de productos disponibles -->
    <div class="seccion-productos">
      <h3>Productos Disponibles</h3>
      <div v-if="productosDisponibles.length" class="productos-grid">
        <div v-for="producto in productosFiltrados" :key="producto.id" class="producto-item" :class="{'sin-stock': producto.stock === 0}">
          <div class="producto-info">
            <span class="producto-nombre">{{ producto.nombre }}</span>
            <span class="producto-detalles">
              <span class="producto-precio">${{ producto.precio }}</span>
              <span class="producto-stock" :class="{'stock-bajo': producto.stock > 0 && producto.stock <= 5, 'sin-stock-text': producto.stock === 0}">
                (Stock: {{ producto.stock }})
                <span v-if="producto.stock === 0" class="sin-stock-badge">SIN STOCK</span>
                <span v-else-if="producto.stock <= 5" class="stock-bajo-badge">STOCK BAJO</span>
              </span>
            </span>
          </div>
          <div class="producto-actions">
            <input 
              type="number" 
              min="1" 
              :max="producto.stock" 
              v-model.number="cantidadesTemp[producto.id]" 
              :disabled="producto.stock === 0"
              class="input-cantidad"
              :class="{'input-disabled': producto.stock === 0}"
            />
            <button 
              @click="agregarAlCarrito(producto)" 
              :disabled="producto.stock === 0 || cantidadesTemp[producto.id] > producto.stock || cantidadesTemp[producto.id] < 1"
              class="btn-agregar"
              :class="{'btn-disabled': producto.stock === 0 || cantidadesTemp[producto.id] > producto.stock || cantidadesTemp[producto.id] < 1}"
            >
              {{ producto.stock === 0 ? 'Sin Stock' : 'Agregar' }}
            </button>
          </div>
        </div>
      </div>
      <div v-else class="no-productos">
        <p>No hay productos disponibles</p>
        <button @click="recargarDatos" class="btn-reload">🔄 Recargar</button>
      </div>
    </div>

    <!-- Carrito - Productos en la venta -->
    <div class="resumen-container">
      <h3>Productos en la Venta</h3>
      <div v-if="carrito.length" class="carrito-list">
        <div v-for="(item, index) in carrito" :key="index" class="carrito-item">
          <div class="carrito-info">
            <span class="producto-nombre">{{ item.producto.nombre }}</span>
            <span class="carrito-detalles">
              ${{ item.producto.precio }} x {{ item.cantidad }} = ${{ item.subtotal }}
            </span>
          </div>
          <button @click="quitarDelCarrito(index)" class="btn-quitar">🗑️ Quitar</button>
        </div>
      </div>
      <div v-else class="carrito-vacio">
        <p>No hay productos en la venta</p>
      </div>
    </div>

    <!-- Método de pago -->
    <div class="pago-selector">
      <label for="medio_pago" class="label-modern">Medio de Pago</label>
      <select id="medio_pago" v-model.number="datosVenta.medio_pago" class="select-modern">
        <option :value="null" disabled>Seleccione método de pago</option>
        <option v-for="mp in metodosPago" :key="mp.id" :value="mp.id">
          {{ mp.nombre }}
        </option>
      </select>
      <div v-if="metodoPagoSeleccionado" class="info-pago">
        <small>Tipo: {{ metodoPagoSeleccionado.tipo }}</small>
      </div>
    </div>

    <!-- Total -->
    <div class="total-section">
      <h3 class="total-final">Total: ${{ total.toFixed(2) }}</h3>
    </div>

    <!-- Botones de acción -->
    <div class="action-buttons">
      <button 
        @click="actualizarVenta" 
        :disabled="carrito.length === 0 || !datosVenta.medio_pago || procesando" 
        class="btn-registrar-premium"
        :class="{'btn-processing': procesando}"
      >
        {{ procesando ? '🔄 Actualizando...' : '💾 Actualizar Venta' }}
      </button>
      <button @click="$emit('cancelar')" class="btn-cancelar">❌ Cancelar</button>
    </div>

    <!-- Mensajes de estado -->
    <div v-if="mensaje" :class="{'mensaje-error': error, 'mensaje-exito': !error}" class="mensaje">
      {{ mensaje }}
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
      debugMode: false,
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
    }
  },
  methods: {
    async cargarDatosVenta() {
      try {
        console.log(`📥 Cargando venta #${this.ventaId}...`);
        
        // ✅ Cargar datos adicionales primero
        await this.cargarDatosAdicionales();
        
        // ✅ Luego cargar la venta usando la nueva ruta /editar/
        const response = await axios.get(`${API_BASE_URL}/usuarios/api/ventas/${this.ventaId}/editar/`);
        const ventaData = response.data;
        
        console.log('📦 Datos de venta recibidos:', ventaData);
        
        // ✅ Cargar datos de la venta actual
        this.datosVenta.medio_pago = ventaData.medio_pago;
        console.log('💰 Medio pago actual:', this.datosVenta.medio_pago);
        
        // ✅ Cargar productos actuales en el carrito
        this.carrito = [];
        if (ventaData.detalles && ventaData.detalles.length > 0) {
          this.carrito = ventaData.detalles.map(detalle => {
            // Buscar el producto en los disponibles
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
        console.log('🛒 Carrito cargado:', this.carrito);
        
        // ✅ Inicializar cantidades temporales
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
        console.log('📥 Cargando datos adicionales...');
        
        // ✅ RUTAS EXACTAS según tu urls.py
        // Productos - usa ProductoListCreateAPIView
        const productosResponse = await axios.get(`${API_BASE_URL}/usuarios/api/productos/`);
        this.productosDisponibles = productosResponse.data || [];
        console.log('🛍️ Productos cargados:', this.productosDisponibles.length, this.productosDisponibles);
        
        // Métodos de pago - usa MetodoPagoListAPIView
        const metodosPagoResponse = await axios.get(`${API_BASE_URL}/usuarios/api/metodos-pago/`);
        this.metodosPago = metodosPagoResponse.data || [];
        console.log('💳 Métodos de pago cargados:', this.metodosPago.length, this.metodosPago);
        
        // Categorías - usa CategoriaProductoListAPIView
        const categoriasResponse = await axios.get(`${API_BASE_URL}/usuarios/api/categorias/productos/`);
        this.categorias = categoriasResponse.data || [];
        console.log('📂 Categorías cargadas:', this.categorias.length, this.categorias);
        
      } catch (error) {
        console.error('❌ Error cargando datos adicionales:', error);
        console.error('❌ Error details:', error.response?.data);
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
        Swal.fire({
          icon: 'error',
          title: 'Cantidad Inválida',
          text: 'La cantidad debe ser al menos 1',
          confirmButtonText: 'Entendido'
        });
        return;
      }
      
      if (cantidad > producto.stock) {
        Swal.fire({
          icon: 'error',
          title: 'Stock Insuficiente',
          text: `No hay suficiente stock. Solo quedan ${producto.stock} unidades.`,
          confirmButtonText: 'Entendido'
        });
        this.cantidadesTemp[producto.id] = producto.stock;
        return;
      }
      
      if (producto.stock === 0) {
        Swal.fire({
          icon: 'error',
          title: 'Sin Stock',
          text: 'Este producto no tiene stock disponible',
          confirmButtonText: 'Entendido'
        });
        return;
      }

      const productoExistente = this.carrito.find(item => item.producto.id === producto.id);
      const cantidadEnCarrito = productoExistente ? productoExistente.cantidad : 0;
      const stockDisponible = producto.stock - cantidadEnCarrito;
      
      if (cantidad > stockDisponible) {
        Swal.fire({
          icon: 'error',
          title: 'Stock Insuficiente',
          text: `No puedes agregar ${cantidad} unidades. Solo hay ${stockDisponible} disponibles.`,
          confirmButtonText: 'Entendido'
        });
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
      
      // Mensaje de éxito más elegante
      Swal.fire({
        icon: 'success',
        title: 'Producto Agregado',
        text: `${producto.nombre} agregado al carrito`,
        timer: 2000,
        showConfirmButton: false
      });
    },

    quitarDelCarrito(index) {
      const productoNombre = this.carrito[index].producto.nombre;
      this.carrito.splice(index, 1);
      
      Swal.fire({
        icon: 'success',
        title: 'Producto Removido',
        text: `${productoNombre} removido del carrito`,
        timer: 2000,
        showConfirmButton: false
      });
    },

    async actualizarVenta() {
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

      this.procesando = true;

      // Mostrar loading durante la actualización
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
        cliente: null
      };

      console.log("📦 Enviando datos para actualizar:", payload);

      try {
        const response = await axios.put(
          `${API_BASE_URL}/usuarios/api/ventas/${this.ventaId}/actualizar/`, 
          payload
        );
        
        if (response.data.status === 'ok') {
          Swal.close(); // Cerrar loading
          
          await Swal.fire({
            icon: 'success',
            title: 'Venta Actualizada',
            text: response.data.message,
            timer: 3000,
            showConfirmButton: false
          });
          
          // Esperar un momento antes de cerrar y refrescar
          setTimeout(() => {
            this.$emit('venta-actualizada');
          }, 1500);
        } else {
          Swal.close(); // Cerrar loading
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: response.data.error || 'Error desconocido',
            confirmButtonText: 'Entendido'
          });
        }
        
      } catch (error) {
        console.error('❌ Error actualizando venta:', error);
        Swal.close(); // Cerrar loading
        
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
      }, 5000);
    }
  },
  async mounted() {
    console.log('🚀 Componente ModificarVenta montado');
    await this.cargarDatosVenta();
  }
}
</script>

<style scoped>
.venta-container { 
  max-width: 800px; 
  margin: 0 auto; 
  padding: 25px; 
  background: #fff; 
  border-radius: 12px; 
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', sans-serif;
}

.seccion-productos {
  margin-bottom: 25px;
}

.seccion-productos h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 8px;
}

.input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.input-modern, .select-modern { 
  flex: 1;
  padding: 10px; 
  border-radius: 8px; 
  border: 1px solid #ddd; 
  transition: border-color 0.3s;
  font-size: 14px;
}

.input-modern:focus, .select-modern:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.productos-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.producto-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  background: #f8f9fa;
  transition: all 0.3s;
}

.producto-item:hover {
  background: #e9ecef;
}

.producto-item.sin-stock {
  background-color: #f8f9fa;
  opacity: 0.6;
  border-color: #dee2e6;
}

.producto-info {
  flex-grow: 1;
}

.producto-nombre {
  font-weight: bold;
  display: block;
  color: #2c3e50;
  margin-bottom: 4px;
}

.producto-detalles {
  display: flex;
  gap: 15px;
  align-items: center;
  font-size: 0.9em;
}

.producto-precio {
  color: #28a745;
  font-weight: bold;
}

.producto-stock {
  color: #6c757d;
}

.stock-bajo {
  color: #e67e22;
  font-weight: bold;
}

.sin-stock-text {
  color: #dc3545;
  font-weight: bold;
}

.stock-bajo-badge, .sin-stock-badge {
  font-size: 0.7em;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 5px;
}

.stock-bajo-badge {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.sin-stock-badge {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.producto-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-cantidad {
  width: 60px;
  text-align: center;
  padding: 6px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.input-cantidad.input-disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.btn-agregar { 
  background-color: #28a745; 
  color: white; 
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 12px;
  white-space: nowrap;
}

.btn-agregar:hover:not(.btn-disabled) {
  background-color: #218838;
}

.btn-agregar.btn-disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.resumen-container {
  padding: 20px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #fafafa;
  margin-bottom: 20px;
}

.resumen-container h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.carrito-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.carrito-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.carrito-info {
  flex-grow: 1;
}

.carrito-detalles {
  color: #6c757d;
  font-size: 0.9em;
}

.btn-quitar { 
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.9em;
  cursor: pointer;
}

.btn-quitar:hover {
  background-color: #c82333;
}

.carrito-vacio, .no-productos {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 20px;
}

.btn-reload {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.pago-selector {
  padding: 20px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.label-modern {
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
}

.info-pago {
  margin-top: 5px;
  color: #6c757d;
  font-size: 0.9em;
}

.total-section {
  text-align: right;
  margin: 20px 0;
  padding: 15px;
  background: #e7f3ff;
  border-radius: 8px;
}

.total-final {
  color: #007bff;
  margin: 0;
  font-size: 1.5em;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.btn-registrar-premium {
  flex: 1;
  background-color: #007bff;
  color: white;
  font-size: 1.1em;
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-registrar-premium:hover:not(:disabled):not(.btn-processing) {
  background-color: #0056b3;
}

.btn-registrar-premium:disabled,
.btn-registrar-premium.btn-processing {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-cancelar {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
}

.btn-cancelar:hover {
  background-color: #5a6268;
}

.mensaje {
  padding: 12px;
  border-radius: 6px;
  margin-top: 15px;
  text-align: center;
  font-weight: bold;
}

.mensaje-exito {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.mensaje-error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.debug-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
  border: 1px solid #dee2e6;
}

.debug-info h4 {
  margin-top: 0;
  color: #6c757d;
}

.btn-debug {
  background: #6c757d;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  margin-top: 10px;
}
</style>