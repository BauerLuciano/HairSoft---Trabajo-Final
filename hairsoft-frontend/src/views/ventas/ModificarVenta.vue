<template>
  <div class="venta-page">
    <div class="venta-wrapper">
      <div class="page-header">
        <div class="header-content">
          <div class="header-title">
            <div class="title-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </div>
            <div>
              <h1>Modificar Venta #{{ ventaId }}</h1>
              <p class="venta-info-header">
                <span>📅 {{ formatFecha(ventaOriginal?.fecha) }}</span>
                <span :class="ventaOriginal?.anulada ? 'badge-anulada' : 'badge-activa'">
                  {{ ventaOriginal?.anulada ? '❌ ANULADA' : '✅ ACTIVA' }}
                </span>
                <span v-if="ventaOriginal">Total Original: ${{ formatPrecio(ventaOriginal.total) }}</span>
              </p>
            </div>
          </div>
          <button @click="$emit('cancelar')" class="btn-volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Cancelar
          </button>
        </div>
      </div>

      <div class="content-grid">
        <div class="productos-section">
          <div class="search-card">
            <div class="search-header">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <h2>Buscar Productos</h2>
            </div>
            <div class="search-grid">
              <div class="form-group">
                <label>Nombre o Código</label>
                <input
                  v-model="filtroNombre"
                  placeholder="Buscar producto..."
                  class="input-search"
                />
              </div>
              <div class="form-group">
                <label>Categoría</label>
                <select v-model="filtroCategoria" class="input-select">
                  <option value="">Todas las categorías</option>
                  <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                    {{ cat.nombre }}
                  </option>
                </select>
              </div>
              <button @click="limpiarFiltros" class="btn-reset">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="1 4 1 10 7 10"></polyline>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
                </svg>
                Limpiar
              </button>
            </div>
          </div>

          <div class="productos-card">
            <div class="productos-header">
              <div class="header-info">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <path d="M16 10a4 4 0 0 1-8 0"></path>
                </svg>
                <h2>Productos Disponibles</h2>
              </div>
              <span class="productos-count">{{ productosFiltrados.length }} productos</span>
            </div>

            <div class="productos-lista" v-if="productosFiltrados.length > 0">
              <div 
                v-for="producto in productosFiltrados" 
                :key="producto.id"
                class="producto-item"
                :class="{
                  'producto-seleccionado': productoEnCarrito(producto.id),
                  'producto-sin-stock': producto.stock === 0
                }"
              >
                <div class="producto-info">
                  <div class="producto-nombre-wrapper">
                    <h3 class="producto-nombre">{{ producto.nombre }}</h3>
                    <span class="producto-categoria">
                      {{ obtenerNombreCategoria(producto.categoria_id) }}
                    </span>
                  </div>
                  <div class="producto-detalles">
                    <div class="producto-precio">
                      <span class="precio-label">Precio</span>
                      <span class="precio-valor">${{ parseFloat(producto.precio).toFixed(2) }}</span>
                    </div>
                    <div class="producto-stock" :class="getStockClass(producto.stock)">
                      <span class="stock-label">Stock</span>
                      <span class="stock-valor">{{ producto.stock }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="producto-acciones">
                  <div class="cantidad-control">
                    <label>Cantidad</label>
                    <input 
                      type="number" 
                      min="1" 
                      :max="producto.stock" 
                      v-model.number="cantidadesTemp[producto.id]" 
                      :disabled="producto.stock === 0"
                      class="input-cantidad"
                    />
                  </div>
                  <button 
                    @click="agregarAlCarrito(producto)" 
                    :disabled="!puedeAgregarAlCarrito(producto)"
                    class="btn-agregar"
                    :class="{ 'btn-disabled': !puedeAgregarAlCarrito(producto) }"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    {{ obtenerTextoBoton(producto) }}
                  </button>
                </div>
              </div>
            </div>
            
            <div v-else class="productos-vacio">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <p>No se encontraron productos</p>
            </div>
          </div>
        </div>

        <div class="carrito-section">
          <div class="carrito-card">
            <div class="carrito-header">
              <div class="header-info">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="9" cy="21" r="1"></circle>
                  <circle cx="20" cy="21" r="1"></circle>
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                </svg>
                <h2>Carrito de Compra</h2>
              </div>
              <span class="carrito-badge">{{ carrito.length }}</span>
            </div>

            <div v-if="carrito.length === 0" class="carrito-vacio">
              <div class="vacio-icon">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="9" cy="21" r="1"></circle>
                  <circle cx="20" cy="21" r="1"></circle>
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                </svg>
              </div>
              <h3>Carrito vacío</h3>
              <p>Agrega productos para modificar la venta</p>
            </div>

            <div v-else class="carrito-contenido">
              <div class="carrito-items">
                <div v-for="(item, index) in carrito" :key="index" class="carrito-item">
                  <div class="item-info">
                    <h4>{{ item.producto.nombre }}</h4>
                    <div class="item-detalles">
                      <span class="item-cantidad">{{ item.cantidad }}x</span>
                      <span class="item-precio-unitario">${{ parseFloat(item.producto.precio).toFixed(2) }}</span>
                    </div>
                  </div>
                  <div class="item-acciones">
                    <div class="item-subtotal">${{ parseFloat(item.subtotal).toFixed(2) }}</div>
                    <button @click="quitarDelCarrito(index)" class="btn-quitar">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <button @click="vaciarCarrito" class="btn-vaciar">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                Vaciar Carrito
              </button>
            </div>
          </div>

          <div class="pago-card">
            <div class="pago-header">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                <line x1="1" y1="10" x2="23" y2="10"></line>
              </svg>
              <h2>Resumen de Pago</h2>
            </div>

            <div class="total-wrapper">
              <div class="total-info">
                <span class="total-label">Total a Pagar</span>
                <span class="total-valor">${{ total.toFixed(2) }}</span>
              </div>
            </div>

            <div class="form-group">
              <label>Método de Pago *</label>
              <select v-model.number="datosVenta.medio_pago" class="input-select">
                <option :value="null">Seleccionar método</option>
                <option 
                  v-for="mp in metodosPago" 
                  :key="mp.id" 
                  :value="mp.id"
                >
                  {{ mp.nombre }}
                </option>
              </select>
            </div>

            <div v-if="esMedioPagoConRecargo" class="datos-extra-pago slide-in">
              
              <div class="form-group" v-if="esTransferencia">
                <label>Billetera / Banco de Origen</label>
                <select v-model="datosVenta.entidad_pago" class="input-select">
                  <option value="" disabled selected>Seleccione entidad...</option>
                  <option value="UALA">Ualá</option>
                  <option value="BRUBANK">Brubank</option>
                  <option value="LEMON">Lemon Cash</option>
                  <option value="NARANJAX">Naranja X</option>
                  <option value="MODO">MODO</option>
                  <option value="SANTANDER">Santander</option>
                  <option value="GALICIA">Galicia</option>
                  <option value="BBVA">BBVA</option>
                  <option value="MACRO">Macro</option>
                  <option value="OTRO">Otro</option>
                </select>
              </div>

              <div class="form-group">
                <label>
                  {{ esMercadoPago ? 'ID Transacción Mercado Pago *' : 'Código de Comprobante *' }}
                </label>
                <input 
                  type="text" 
                  v-model="datosVenta.codigo_transaccion" 
                  class="input-search"
                  :placeholder="esMercadoPago ? 'Ej: #145025893768' : 'Ej: A123B456789'"
                  :maxlength="maxCodigoLength"
                />
                <small class="helper-text" style="color: #6b7280; font-size: 0.8rem; margin-top: 4px; display: block;">
                  {{ esMercadoPago ? 'Ingrese el ID de operación (Máx 14).' : 'Copie el código del comprobante bancario.' }}
                </small>
              </div>
            </div>

            <button 
              @click="validarYActualizarVenta" 
              :disabled="!formularioValido || procesando" 
              class="btn-confirmar"
              :class="{ 'btn-procesando': procesando }"
            >
              <template v-if="!procesando">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Actualizar Venta
              </template>
              <template v-else>
                <div class="spinner"></div>
                Procesando...
              </template>
            </button>
          </div>
        </div>
      </div>

      <transition name="toast">
        <div v-if="mensaje" class="toast-notification" :class="error ? 'error' : 'success'">
          <div class="toast-icon">
            <template v-if="!error">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </template>
            <template v-else>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
            </template>
          </div>
          <span>{{ mensaje }}</span>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2'

// URLs relativas usando la base de axiosConfig
const API_URL_PRODUCTOS = '/usuarios/api/productos/'
const API_URL_METODOS = '/usuarios/api/metodos-pago/'
const API_URL_CATEGORIAS = '/usuarios/api/categorias/productos/'
const API_URL_VENTAS = '/usuarios/api/ventas/'

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
      datosVenta: {
        medio_pago: null,
        entidad_pago: '',
        codigo_transaccion: ''
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

    // 🔥 HELPERS COMPUTADOS PARA LA LÓGICA DE PAGO
    metodoPagoSeleccionado() {
        if (!this.datosVenta.medio_pago) return null;
        return this.metodosPago.find(mp => mp.id === this.datosVenta.medio_pago);
    },
    esMercadoPago() {
        return this.metodoPagoSeleccionado?.tipo === 'MERCADOPAGO' || 
               this.metodoPagoSeleccionado?.nombre.toUpperCase().includes('MERCADO');
    },
    esTransferencia() {
        // 🔥 CORRECCIÓN: Si es Mercado Pago, NO es Transferencia
        if (this.esMercadoPago) return false;
        
        return this.metodoPagoSeleccionado?.tipo === 'TRANSFERENCIA' ||
               this.metodoPagoSeleccionado?.nombre.toUpperCase().includes('TRANSFERENCIA');
    },
    esMedioPagoConRecargo() {
        return this.esMercadoPago || this.esTransferencia;
    },
    maxCodigoLength() {
        return this.esMercadoPago ? 14 : 25;
    },
    
    formularioValido() {
      if (this.carrito.length === 0) return false;
      if (!this.datosVenta.medio_pago) return false;

      // Validación de código de transacción si aplica
      if (this.esMedioPagoConRecargo && !this.datosVenta.codigo_transaccion) {
         return false;
      }
      return true;
    },
    
    horasDesdeVenta() {
      if (!this.ventaOriginal?.fecha) return 0;
      return (new Date() - new Date(this.ventaOriginal.fecha)) / (1000 * 60 * 60);
    }
  },
  
  watch: {
    // 🔥 LIMPIAR CAMPOS AL CAMBIAR MEDIO DE PAGO
    'datosVenta.medio_pago'(newVal) {
        // Si estamos cargando la venta original, no limpiamos nada
        if (this.ventaOriginal && this.ventaOriginal.medio_pago === newVal) {
             this.datosVenta.entidad_pago = this.ventaOriginal.entidad_pago || '';
             this.datosVenta.codigo_transaccion = this.ventaOriginal.codigo_transaccion || '';
             return;
        }

        // Si cambia a Efectivo, limpiar todo
        if (!this.esMedioPagoConRecargo) {
            this.datosVenta.entidad_pago = '';
            this.datosVenta.codigo_transaccion = '';
        } else if (this.esMercadoPago) {
            // Si es MP, limpiar entidad (ya no se pide)
            this.datosVenta.entidad_pago = ''; 
        }
    }
  },
  
  methods: {
    obtenerNombreCategoria(categoriaId) {
      const categoria = this.categorias.find(c => c.id === categoriaId);
      return categoria ? categoria.nombre : 'Sin categoría';
    },
    
    productoEnCarrito(productoId) {
      return this.carrito.some(item => item.producto.id === productoId);
    },
    
    cantidadEnCarrito(productoId) {
      const item = this.carrito.find(item => item.producto.id === productoId);
      return item ? item.cantidad : 0;
    },
    
    puedeAgregarAlCarrito(producto) {
      if (producto.stock === 0) return false;
      const cantidad = this.cantidadesTemp[producto.id] || 1;
      return cantidad >= 1 && cantidad <= producto.stock;
    },
    
    obtenerTextoBoton(producto) {
      if (producto.stock === 0) return 'Sin Stock';
      if (this.productoEnCarrito(producto.id)) {
        return 'Añadir más';
      }
      return 'Agregar';
    },

    getStockClass(stock) {
      if (stock === 0) return 'stock-agotado';
      if (stock <= 5) return 'stock-bajo';
      return 'stock-disponible';
    },

    limpiarFiltros() {
      this.filtroNombre = '';
      this.filtroCategoria = '';
    },

    async cargarDatosVenta() {
      try {
        console.log(`📥 Cargando venta #${this.ventaId}...`);
        
        // Primero cargar datos maestros
        await this.cargarDatosAdicionales();
        
        // Usamos ?q=ID para traer el detalle completo (igual que en DetalleVenta)
        const response = await axios.get(`${API_URL_VENTAS}?q=${this.ventaId}`);
        const resultados = response.data.results || response.data;
        let ventaData = null;
        
        if (Array.isArray(resultados) && resultados.length > 0) {
            ventaData = resultados.find(v => v.id == this.ventaId) || resultados[0];
        } else {
             // Fallback directo
             const resDirecto = await axios.get(`${API_URL_VENTAS}${this.ventaId}/`);
             ventaData = resDirecto.data;
        }
        
        console.log('📦 Datos de venta recibidos:', ventaData);
        
        this.ventaOriginal = { ...ventaData };
        this.datosVenta.medio_pago = ventaData.medio_pago;

        // 🔥 PRE-CARGAR DATOS DE TRAZABILIDAD 🔥
        this.datosVenta.entidad_pago = ventaData.entidad_pago || '';
        this.datosVenta.codigo_transaccion = ventaData.codigo_transaccion || '';
        
        // Limpiar carrito antes de cargar
        this.carrito = [];
        
        // Cargar productos al carrito
        if (ventaData.detalles && ventaData.detalles.length > 0) {
          ventaData.detalles.forEach(detalle => {
            // Buscar el producto en la lista de productos disponibles
            const productoActual = this.productosDisponibles.find(p => p.id === detalle.producto);
            
            if (productoActual) {
              this.carrito.push({
                producto: {
                  id: productoActual.id,
                  nombre: productoActual.nombre,
                  precio: parseFloat(productoActual.precio),
                  stock: productoActual.stock,
                  categoria_id: productoActual.categoria_id
                },
                cantidad: detalle.cantidad,
                subtotal: detalle.cantidad * parseFloat(productoActual.precio)
              });
            } else {
              // Fallback si no está en la lista (ej: producto desactivado)
              this.carrito.push({
                producto: {
                  id: detalle.producto,
                  nombre: detalle.producto_nombre || `Producto #${detalle.producto}`,
                  precio: parseFloat(detalle.precio_unitario),
                  stock: 0,
                  categoria_id: null
                },
                cantidad: detalle.cantidad,
                subtotal: parseFloat(detalle.subtotal)
              });
            }
          });
        }
        
        // Inicializar cantidades temporales
        this.productosDisponibles.forEach(p => {
          if (!this.cantidadesTemp[p.id]) {
            this.cantidadesTemp[p.id] = 1;
          }
        });
        
        this.mostrarMensaje('✅ Datos de venta cargados correctamente');
        
      } catch (error) {
        console.error('❌ Error cargando datos de venta:', error);
        
        const msgError = error.response?.data?.error || error.message || 'Error desconocido';
        
        Swal.fire({
          icon: 'error',
          title: 'Error al Cargar',
          text: `No se pudieron cargar los datos: ${msgError}`,
          confirmButtonText: 'Entendido'
        });
      }
    },

    async cargarDatosAdicionales() {
      try {
        console.log('📥 Cargando productos, métodos de pago y categorías...');
        
        const [productosResponse, metodosPagoResponse, categoriasResponse] = await Promise.all([
          axios.get(API_URL_PRODUCTOS),
          axios.get(API_URL_METODOS),
          axios.get(API_URL_CATEGORIAS)
        ]);
        
        this.productosDisponibles = (productosResponse.data || []).map(prod => ({
          id: prod.id,
          nombre: prod.nombre,
          precio: parseFloat(prod.precio) || 0,
          stock: parseInt(prod.stock_actual) || 0,
          categoria_id: prod.categoria,
          estado: prod.estado
        }));
        
        // 🔥 FILTRO ANTI-TARJETAS 🔥
        if (Array.isArray(metodosPagoResponse.data)) {
            const permitidos = ['EFECTIVO', 'MERCADOPAGO', 'TRANSFERENCIA'];
            this.metodosPago = metodosPagoResponse.data.filter(mp => 
                mp.activo !== false && 
                (permitidos.includes(mp.tipo) || permitidos.includes(mp.nombre.toUpperCase())) &&
                !mp.nombre.toUpperCase().includes('TARJETA') 
            );
        } else {
            this.metodosPago = [];
        }
        
        this.categorias = categoriasResponse.data || [];
        
      } catch (error) {
        console.error('❌ Error cargando datos adicionales:', error);
        throw error;
      }
    },

    agregarAlCarrito(producto) {
      const cantidad = this.cantidadesTemp[producto.id] || 1;
      
      if (cantidad < 1) {
        this.mostrarMensaje('❌ La cantidad debe ser al menos 1', true);
        return;
      }
      
      if (producto.stock === 0) {
        this.mostrarMensaje('❌ Producto sin stock disponible', true);
        return;
      }

      const productoExistente = this.carrito.find(item => item.producto.id === producto.id);
      
      if (productoExistente) {
        const nuevaCantidadTotal = productoExistente.cantidad + cantidad;
        
        if (nuevaCantidadTotal > producto.stock) {
          this.mostrarMensaje(`❌ Stock insuficiente. Solo hay ${producto.stock} disponibles`, true);
          return;
        }
        
        productoExistente.cantidad = nuevaCantidadTotal;
        productoExistente.subtotal = productoExistente.cantidad * producto.precio;
        this.mostrarMensaje(`✅ Se agregaron ${cantidad} más de "${producto.nombre}"`);
      } else {
        if (cantidad > producto.stock) {
          this.mostrarMensaje(`❌ Stock insuficiente. Solo hay ${producto.stock} disponibles`, true);
          return;
        }
        
        this.carrito.push({
          producto: { ...producto },
          cantidad: cantidad,
          subtotal: cantidad * producto.precio
        });
        this.mostrarMensaje(`✅ "${producto.nombre}" agregado al carrito`);
      }
      
      this.cantidadesTemp[producto.id] = 1;
    },

    quitarDelCarrito(index) {
      const productoNombre = this.carrito[index].producto.nombre;
      this.carrito.splice(index, 1);
      this.mostrarMensaje(`🗑️ "${productoNombre}" removido del carrito`);
    },

    vaciarCarrito() {
      Swal.fire({
        title: '¿Vaciar carrito?',
        text: 'Se eliminarán todos los productos del carrito',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        confirmButtonText: 'Sí, vaciar',
      }).then((result) => {
        if (result.isConfirmed) {
          this.carrito = [];
          this.mostrarMensaje('Carrito vaciado', false);
        }
      });
    },

    async validarYActualizarVenta() {
      if (this.ventaOriginal?.anulada) {
        Swal.fire('Error', 'No se puede modificar una venta anulada', 'error');
        return;
      }

      if (this.carrito.length === 0) {
        Swal.fire('Atención', 'Debe agregar al menos un producto', 'warning');
        return;
      }
      
      if (!this.datosVenta.medio_pago) {
        Swal.fire('Atención', 'Debe seleccionar un método de pago', 'warning');
        return;
      }

      // Validación extra
      if (this.esMedioPagoConRecargo && !this.datosVenta.codigo_transaccion) {
          Swal.fire('Atención', 'Falta el código de transacción', 'warning');
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
      
      // Lógica entidad
      let entidadFinal = null;
      if (this.esMercadoPago) {
          entidadFinal = 'MERCADOPAGO';
      } else if (this.esTransferencia) {
          entidadFinal = this.datosVenta.entidad_pago;
      }
      
      const payload = { 
        total: parseFloat(this.total),
        tipo: 'PRODUCTO', 
        medio_pago: parseInt(this.datosVenta.medio_pago),
        detalles,
        cliente: null,
        motivo_modificacion: motivo,
        usuario_modificacion: 'usuario_actual',
        
        // 🔥 CAMPOS NUEVOS
        entidad_pago: entidadFinal,
        codigo_transaccion: this.esMedioPagoConRecargo ? this.datosVenta.codigo_transaccion : null
      };

      try {
        const response = await axios.put(
          `${API_URL_VENTAS}${this.ventaId}/actualizar/`, 
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
          throw new Error(response.data.error || 'Error en respuesta del servidor');
        }
        
      } catch (error) {
        console.error('❌ Error actualizando venta:', error);
        Swal.close();
        
        const errorMsg = error.response?.data?.error || error.message || 'Error al actualizar la venta';
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
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* LAYOUT PRINCIPAL */
.venta-page {
  min-height: 100vh;
  background: #0f172a;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.venta-wrapper {
  max-width: 100%;
  margin: 0;
  padding: 30px;
}

/* HEADER */
.page-header {
  background: linear-gradient(135deg, #1e293b, #334155);
  border-radius: 0;
  padding: 28px 32px;
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-bottom: 2px solid #06b6d4;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.venta-info-header {
  font-size: 14px;
  color: #94a3b8;
  margin: 4px 0 0 0;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.badge-activa {
  background: #d1fae5;
  color: #065f46;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.badge-anulada {
  background: #fee2e2;
  color: #991b1b;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.btn-volver {
  background: rgba(6, 182, 212, 0.1);
  border: 2px solid rgba(6, 182, 212, 0.3);
  color: #06b6d4;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-volver:hover {
  background: rgba(6, 182, 212, 0.2);
  border-color: #06b6d4;
  transform: translateY(-2px);
}

/* GRID DE CONTENIDO */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 30px;
}

/* SECCIÓN DE BÚSQUEDA */
.search-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 2px solid #e2e8f0;
}

.search-card:hover {
  border-color: #06b6d4;
}

.search-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  color: #06b6d4;
}

.search-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.search-grid {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 16px;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.input-search,
.input-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  color: #2d3748;
  background: #f7fafc;
  transition: all 0.3s ease;
}

.input-search:focus,
.input-select:focus {
  outline: none;
  border-color: #06b6d4;
  background: white;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.btn-reset {
  background: white;
  border: 2px solid #e2e8f0;
  color: #4a5568;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-reset:hover {
  background: #f7fafc;
  border-color: #06b6d4;
  color: #06b6d4;
}

/* LISTA DE PRODUCTOS */
.productos-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 2px solid #e2e8f0;
}

.productos-card:hover {
  border-color: #06b6d4;
}

.productos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #06b6d4;
}

.header-info h2 {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.productos-count {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
}

.productos-lista {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.productos-lista::-webkit-scrollbar {
  width: 6px;
}

.productos-lista::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 10px;
}

.productos-lista::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 10px;
}

.productos-lista::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.producto-item {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  transition: all 0.3s ease;
}

.producto-item:hover {
  border-color: #06b6d4;
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15);
  transform: translateY(-2px);
}

.producto-seleccionado {
  background: #ecfeff;
  border-color: #06b6d4;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.producto-sin-stock {
  opacity: 0.6;
  background: #fef2f2;
  border-color: #fca5a5;
}

.producto-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.producto-nombre-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.producto-nombre {
  font-size: 16px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.producto-categoria {
  display: inline-block;
  background: #ecfeff;
  color: #0891b2;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid #a5f3fc;
  width: fit-content;
}

.producto-detalles {
  display: flex;
  gap: 20px;
}

.producto-precio,
.producto-stock {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.precio-label,
.stock-label {
  font-size: 12px;
  color: #718096;
  font-weight: 600;
}

.precio-valor {
  font-size: 20px;
  font-weight: 700;
  color: #06b6d4;
}

.stock-valor {
  font-size: 16px;
  font-weight: 700;
}

.stock-disponible {
  color: #38a169;
}

.stock-bajo {
  color: #ed8936;
}

.stock-agotado {
  color: #e53e3e;
}

.producto-acciones {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-end;
  min-width: 140px;
}

.cantidad-control {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.cantidad-control label {
  font-size: 12px;
  font-weight: 600;
  color: #718096;
}

.input-cantidad {
  width: 100%;
  padding: 10px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  text-align: center;
  font-size: 16px;
  font-weight: 700;
  color: #2d3748;
  background: #f7fafc;
  transition: all 0.3s ease;
}

.input-cantidad:focus {
  outline: none;
  border-color: #06b6d4;
  background: white;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.btn-agregar {
  width: 100%;
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-agregar:hover:not(.btn-disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
}

.btn-agregar.btn-disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  opacity: 0.7;
}

.productos-vacio {
  text-align: center;
  padding: 60px 20px;
  color: #a0aec0;
}

.productos-vacio svg {
  margin-bottom: 16px;
  color: #cbd5e0;
}

.productos-vacio p {
  font-size: 16px;
  color: #718096;
}

/* CARRITO */
.carrito-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 2px solid #e2e8f0;
}

.carrito-card:hover {
  border-color: #06b6d4;
}

.carrito-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.carrito-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.carrito-badge {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.carrito-vacio {
  text-align: center;
  padding: 60px 20px;
}

.vacio-icon {
  color: #cbd5e0;
  margin-bottom: 20px;
}

.carrito-vacio h3 {
  font-size: 18px;
  color: #4a5568;
  margin: 0 0 8px 0;
}

.carrito-vacio p {
  font-size: 14px;
  color: #a0aec0;
  margin: 0;
}

.carrito-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
  margin-bottom: 16px;
}

.carrito-items::-webkit-scrollbar {
  width: 6px;
}

.carrito-items::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 10px;
}

.carrito-items::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 10px;
}

.carrito-items::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.carrito-item {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  transition: all 0.3s ease;
}

.carrito-item:hover {
  border-color: #06b6d4;
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.1);
}

.item-info {
  flex: 1;
}

.item-info h4 {
  font-size: 15px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 8px 0;
}

.item-detalles {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #718096;
}

.item-cantidad {
  font-weight: 700;
  color: #06b6d4;
}

.item-precio-unitario {
  color: #4a5568;
}

.item-acciones {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.item-subtotal {
  font-size: 16px;
  font-weight: 700;
  color: #06b6d4;
}

.btn-quitar {
  background: #fed7d7;
  border: none;
  color: #e53e3e;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-quitar:hover {
  background: #fc8181;
  color: white;
  transform: scale(1.1);
}

.btn-vaciar {
  width: 100%;
  background: white;
  border: 2px solid #e2e8f0;
  color: #718096;
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-vaciar:hover {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #dc2626;
}

/* PAGO Y RESUMEN */
.pago-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 2px solid #e2e8f0;
}

.pago-card:hover {
  border-color: #06b6d4;
}

.pago-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
  color: #06b6d4;
}

.pago-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.total-wrapper {
  background: linear-gradient(135deg, #ecfeff, #cffafe);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border: 2px solid #a5f3fc;
}

.total-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-label {
  font-size: 16px;
  font-weight: 600;
  color: #0e7490;
}

.total-valor {
  font-size: 32px;
  font-weight: 700;
  color: #0891b2;
}

.btn-confirmar {
  width: 100%;
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
  border: none;
  padding: 16px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.btn-confirmar:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
}

.btn-confirmar:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-confirmar.btn-procesando {
  background: #a0aec0;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* NOTIFICACIONES */
.toast-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  max-width: 400px;
  font-weight: 600;
  border-left: 4px solid;
}

.toast-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-notification.success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-left-color: #047857;
}

.toast-notification.success .toast-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.toast-notification.error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border-left-color: #b91c1c;
}

.toast-notification.error .toast-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* RESPONSIVE */
@media (max-width: 1400px) {
  .content-grid {
    grid-template-columns: 1fr 380px;
  }
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .carrito-section {
    order: -1;
  }
}

@media (max-width: 768px) {
  .venta-page {
    padding: 20px;
  }

  .page-header {
    padding: 20px;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-volver {
    width: 100%;
    justify-content: center;
  }

  .search-grid {
    grid-template-columns: 1fr;
  }

  .btn-reset {
    width: 100%;
  }

  .producto-item {
    flex-direction: column;
  }

  .producto-acciones {
    width: 100%;
    align-items: stretch;
  }
}
</style>