<template>
  <div class="venta-page">
    <div class="venta-wrapper">
      <div class="page-header">
        <div class="header-content">
          <div class="header-title">
            <div class="title-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
            </div>
            <div>
              <h1>Nueva Venta</h1>
              <p>Registra una venta de productos</p>
            </div>
          </div>
          <button @click="volverAlListado" class="btn-volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Volver al Listado
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
                  @input="filtrarProductos"
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
              <button @click="restablecerFiltros" class="btn-reset">
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
                      {{ obtenerNombreCategoria(producto.categoria) }}
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
                      :max="stockDisponibleReal(producto)" 
                      v-model.number="cantidades[producto.id]" 
                      :disabled="producto.stock === 0"
                      class="input-cantidad"
                      @change="validarCantidad(producto)"
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
              <p>Agrega productos para comenzar</p>
            </div>

            <div v-else class="carrito-contenido">
              <div class="carrito-items">
                <div v-for="item in carrito" :key="item.producto.id" class="carrito-item">
                  <div class="item-info">
                    <h4>{{ item.producto.nombre }}</h4>
                    <div class="item-detalles">
                      <span class="item-cantidad">{{ item.cantidad }}x</span>
                      <span class="item-precio-unitario">${{ parseFloat(item.producto.precio).toFixed(2) }}</span>
                    </div>
                  </div>
                  <div class="item-acciones">
                    <div class="item-subtotal">${{ parseFloat(item.subtotal).toFixed(2) }}</div>
                    <button @click="quitarDelCarrito(item.producto.id)" class="btn-quitar">
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

          <div class="pago-card" v-if="carrito.length > 0">
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
              <select v-model="datosVenta.medio_pago" class="input-select">
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
              @click="registrarVenta" 
              :disabled="!formularioValido || procesandoVenta || carrito.length === 0" 
              class="btn-confirmar"
              :class="{ 'btn-procesando': procesandoVenta }"
            >
              <template v-if="!procesandoVenta">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Confirmar Venta
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
        <div v-if="mensaje" class="toast-notification" :class="mensajeTipo">
          <div class="toast-icon">
            <template v-if="mensajeTipo === 'success'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </template>
            <template v-else-if="mensajeTipo === 'error'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
            </template>
            <template v-else>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
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
import Swal from 'sweetalert2';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default {
    name: 'RegistrarVenta',
    
    inject: ['router'] || [],
    
    data() {
        return {
            productos: [],
            categorias: [],
            metodosPago: [],
            filtroNombre: '',
            filtroCategoria: '',
            cantidades: {},
            carrito: [],
            procesandoVenta: false,
            datosVenta: {
                medio_pago: null,
                entidad_pago: '',
                codigo_transaccion: '',
                usuario: 1 
            },
            mensaje: '',
            mensajeTipo: 'success'
        }
    },
    
    computed: {
        productosFiltrados() {
            return this.productos.filter(p => {
                const nombreMatch = p.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase())
                const categoriaMatch = this.filtroCategoria ? p.categoria === parseInt(this.filtroCategoria) : true 
                return nombreMatch && categoriaMatch && p.estado === 'ACTIVO' 
            })
        },
        total() {
            return this.carrito.reduce((acc, item) => acc + item.subtotal, 0)
        },
        
        // 🔥 HELPERS COMPUTADOS PARA LA LÓGICA DE PAGO
        metodoPagoSeleccionado() {
            if (!this.datosVenta.medio_pago) return null;
            return this.metodosPago.find(mp => mp.id === this.datosVenta.medio_pago);
        },
        esMercadoPago() {
            return this.metodoPagoSeleccionado?.tipo === 'MERCADOPAGO';
        },
        esTransferencia() {
            return this.metodoPagoSeleccionado?.tipo === 'TRANSFERENCIA';
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
        }
    },
    
    watch: {
        // Limpiar campos si cambian de medio de pago
        'datosVenta.medio_pago'(newVal) {
            this.datosVenta.entidad_pago = '';
            this.datosVenta.codigo_transaccion = '';
        }
    },
    
    methods: {
        navegarAListado() {
            console.log("🚀 Iniciando navegación al listado de ventas");
            if (this.$route.path === '/ventas') {
                window.location.reload();
                return;
            }
            this.$router.push('/ventas').catch(err => {
                console.error("Router err", err);
                window.location.href = '/ventas';
            });
        },

        volverAlListado() {
            if (this.carrito.length > 0) {
                Swal.fire({
                    title: '¿Salir sin completar la venta?',
                    text: 'Se perderán los productos agregados al carrito',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, salir',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.navegarAListado();
                    }
                });
            } else {
                this.navegarAListado();
            }
        },

        async procesarVentaExitosa(ventaData) {
            Swal.close();
            this.limpiarFormulario();
            await this.cargarProductos(); 

            const totalConfirmado = parseFloat(ventaData.total);
            
            const result = await Swal.fire({
                title: '¡Venta Registrada Exitosamente!',
                html: `
                    <div style="text-align: left; margin: 20px 0;">
                        <div style="background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 4px solid #059669; color: #1f2937;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <strong>N° de Venta:</strong>
                                <span>#${ventaData.id}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <strong>Total:</strong>
                                <span style="color: #059669; font-weight: bold;">$${totalConfirmado.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                    <p style="text-align: center; margin: 20px 0 10px 0; color: #6c757d;">
                        ¿Desea abrir el comprobante de venta?
                    </p>
                `,
                icon: 'success',
                showCancelButton: true,
                confirmButtonText: '📄 Sí, abrir comprobante',
                cancelButtonText: '➡️ Continuar (ir a Listado)',
                confirmButtonColor: '#3b82f6',
                cancelButtonColor: '#6c757d',
                reverseButtons: true,
                backdrop: true,
                allowOutsideClick: false
            });

            if (result.isConfirmed) {
                this.abrirComprobante(ventaData.id);
                setTimeout(() => {
                    this.navegarAListado();
                }, 500);
            } else {
                this.navegarAListado();
            }
        },

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
        
        stockDisponibleReal(producto) {
            const cantidadEnCarrito = this.cantidadEnCarrito(producto.id);
            return Math.max(0, producto.stock - cantidadEnCarrito);
        },
        
        puedeAgregarAlCarrito(producto) {
            if (producto.stock === 0) return false;
            const cantidad = this.cantidades[producto.id] || 1;
            const stockDisponible = producto.stock;
            const cantidadEnCarrito = this.cantidadEnCarrito(producto.id);
            return cantidad >= 1 && (cantidad + cantidadEnCarrito) <= stockDisponible;
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

        validarCantidad(producto) {
            let cantidad = this.cantidades[producto.id] || 0;
            const stockTotal = producto.stock;
            const cantidadEnCarrito = this.cantidadEnCarrito(producto.id);
            
            if (cantidad < 1) {
                this.cantidades[producto.id] = 1;
            } else if (cantidad + cantidadEnCarrito > stockTotal) {
                cantidad = stockTotal - cantidadEnCarrito;
                this.cantidades[producto.id] = Math.max(1, cantidad);
                this.mostrarMensaje('Cantidad ajustada para no exceder el stock total', 'warning');
            }
        },
        
        filtrarProductos() {}, 
        restablecerFiltros() {
            this.filtroNombre = '';
            this.filtroCategoria = '';
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
                    this.carrito.forEach(item => {
                        this.actualizarStockVisual(item.producto.id, item.cantidad);
                    });
                    this.carrito = [];
                    this.mostrarMensaje('Carrito vaciado', 'info');
                }
            });
        },

        async cargarMetodosPago() {
            try {
                // 1. Cargar desde API para obtener los IDs reales
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/metodos-pago/`); 
                if (Array.isArray(res.data)) {
                    // 🔥 AQUÍ ESTÁ EL ARREGLO:
                    // Filtramos explícitamente para QUE NO PASE LA TARJETA
                    // Solo aceptamos Efectivo, MP o Transferencia.
                    const permitidos = ['EFECTIVO', 'MERCADOPAGO', 'TRANSFERENCIA'];
                    
                    this.metodosPago = res.data.filter(mp => 
                        mp.activo !== false && 
                        (permitidos.includes(mp.tipo) || permitidos.includes(mp.nombre.toUpperCase())) &&
                        !mp.nombre.toUpperCase().includes('TARJETA') 
                    );
                }
                
                // 2. Seleccionar EFECTIVO por defecto si existe
                if (this.metodosPago.length > 0) {
                    const efectivo = this.metodosPago.find(m => m.tipo === 'EFECTIVO');
                    this.datosVenta.medio_pago = efectivo ? efectivo.id : this.metodosPago[0].id;
                }
            } catch (err) { 
                console.error("❌ Error al cargar métodos de pago:", err);
            }
        },
        
        async cargarProductos() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/productos/`);
                this.productos = (Array.isArray(res.data) ? res.data : []).map(prod => ({
                    ...prod,
                    stock: parseInt(prod.stock_actual) || 0, 
                    precio: parseFloat(prod.precio) || 0,
                }));
                this.productos.forEach(p => { 
                    this.cantidades[p.id] = Math.min(1, p.stock);
                });
            } catch (err) { 
                console.error("Error al cargar productos:", err);
            }
        },

        async cargarCategorias() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/categorias/productos/`)
                this.categorias = Array.isArray(res.data) ? res.data : []
            } catch (err) { 
                console.error("Error al cargar categorías:", err);
            }
        },
        
        agregarAlCarrito(producto) {
            const cantidadAAgregar = this.cantidades[producto.id];
            
            if ((cantidadAAgregar + this.cantidadEnCarrito(producto.id)) > producto.stock) {
                 this.mostrarMensaje(`No puedes agregar ${cantidadAAgregar}. Stock máximo excedido.`, 'error');
                 return;
            }

            const itemIndex = this.carrito.findIndex(item => item.producto.id === producto.id);
            
            if (itemIndex !== -1) {
                const itemExistente = this.carrito[itemIndex];
                itemExistente.cantidad += cantidadAAgregar;
                itemExistente.subtotal = itemExistente.cantidad * itemExistente.producto.precio;
                this.mostrarMensaje(`Se añadió(eron) ${cantidadAAgregar} unidad(es) de ${producto.nombre}.`, 'success');
            } else {
                this.carrito.push({
                    producto: {
                        id: producto.id,
                        nombre: producto.nombre,
                        precio: producto.precio,
                        categoria: producto.categoria
                    },
                    cantidad: cantidadAAgregar,
                    subtotal: cantidadAAgregar * producto.precio
                });
                this.mostrarMensaje(`${producto.nombre} agregado al carrito`, 'success');
            }
            
            this.productos.find(p => p.id === producto.id).stock -= cantidadAAgregar;
            this.cantidades[producto.id] = 1;
        },
        
        actualizarStockVisual(productoId, cambio) {
            const producto = this.productos.find(p => p.id === productoId);
            if (producto) {
                producto.stock = Math.min(producto.stock_actual, producto.stock + cambio);
                if (producto.stock === 0) {
                    this.cantidades[productoId] = 0;
                }
            }
        },
        
        quitarDelCarrito(productoId) {
            const itemIndex = this.carrito.findIndex(item => item.producto.id === productoId);
            if (itemIndex !== -1) {
                const item = this.carrito[itemIndex];
                this.actualizarStockVisual(productoId, item.cantidad);
                this.carrito.splice(itemIndex, 1);
                this.mostrarMensaje(`${item.producto.nombre} removido del carrito`, 'info');
            }
        },
        
        async registrarVenta() {
            if (!this.validarVenta()) return;

            this.procesandoVenta = true;
            
            Swal.fire({
                title: 'Registrando Venta...',
                text: 'Por favor espere',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });

            try {
                const payload = this.prepararPayloadVenta();
                const response = await axios.post(`${API_BASE_URL}/usuarios/api/ventas/registrar/`, payload);
                
                if (response.status === 201) {
                    await this.procesarVentaExitosa(response.data); 
                } else {
                      throw new Error(`Respuesta inesperada del servidor: ${response.status}`);
                }
            } catch (err) {
                this.manejarErrorVenta(err);
            } finally {
                this.procesandoVenta = false;
            }
        },

        validarVenta() {
          if (this.carrito.length === 0) {
            this.mostrarMensaje('Debe agregar productos al carrito', 'warning');
            return false;
          }
          if (!this.datosVenta.medio_pago) {
            this.mostrarMensaje('Debe seleccionar un método de pago', 'warning');
            return false;
          }
          // Validación extra de código
          if (this.esMedioPagoConRecargo && !this.datosVenta.codigo_transaccion) {
             this.mostrarMensaje('Falta el código de transacción', 'warning');
             return false;
          }
          return true;
        },

        prepararPayloadVenta() {
            const detalles = this.carrito.map(item => ({
                producto: item.producto.id,
                cantidad: item.cantidad,
                precio_unitario: parseFloat(item.producto.precio),
                subtotal: parseFloat(item.subtotal),
                servicio: null,
                turno: null 
            }));
            
            // Lógica entidad (Si es MP, la entidad es MERCADOPAGO)
            let entidadFinal = null;
            if (this.esMercadoPago) {
                entidadFinal = 'MERCADOPAGO';
            } else if (this.esTransferencia) {
                entidadFinal = this.datosVenta.entidad_pago;
            }

            return { 
                total: parseFloat(this.total),
                tipo: 'PRODUCTO', 
                
                // MANDAMOS EL ID REAL QUE VIENE DE LA API
                medio_pago: parseInt(this.datosVenta.medio_pago),
                
                detalles,
                cliente: null,
                usuario: this.datosVenta.usuario,
                
                // Nuevos campos
                entidad_pago: entidadFinal,
                codigo_transaccion: this.esMedioPagoConRecargo ? this.datosVenta.codigo_transaccion : null
            };
        },

        abrirComprobante(ventaId) {
            const pdfUrl = `${API_BASE_URL}/usuarios/api/ventas/${ventaId}/comprobante-pdf/`;
            window.open(pdfUrl, '_blank');
        },

        manejarErrorVenta(err) {
            Swal.close();
            let errorMessage = 'Error desconocido al registrar venta.';
            if (err.response) {
                if (err.response.status === 401) {
                    errorMessage = 'Permiso denegado. Debe iniciar sesión.';
                } else if (err.response.data) {
                    errorMessage = JSON.stringify(err.response.data);
                }
            }
            
            Swal.fire({
                icon: 'error',
                title: 'Error al Registrar Venta',
                text: errorMessage,
                confirmButtonColor: '#ef4444'
            });
            this.cargarProductos();
        },

        mostrarMensaje(texto, tipo = 'info') {
            this.mensaje = texto;
            this.mensajeTipo = tipo;
            setTimeout(() => { this.mensaje = ''; }, 4000);
        },

        limpiarFormulario() {
            this.carrito = [];
            // Volver a seleccionar el por defecto
            if (this.metodosPago.length > 0) {
                const efectivo = this.metodosPago.find(m => m.tipo === 'EFECTIVO');
                this.datosVenta.medio_pago = efectivo ? efectivo.id : this.metodosPago[0].id;
            }
            this.datosVenta.codigo_transaccion = '';
            this.datosVenta.entidad_pago = '';
            this.filtroNombre = '';
            this.filtroCategoria = '';
        }
    },
    
    mounted() {
        this.cargarProductos();
        this.cargarCategorias();
        this.cargarMetodosPago();
    }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* ============================================
   LAYOUT PRINCIPAL
   ============================================ */
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

/* ============================================
   HEADER
   ============================================ */
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

.header-title p {
  font-size: 14px;
  color: #94a3b8;
  margin: 4px 0 0 0;
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

/* ============================================
   GRID DE CONTENIDO
   ============================================ */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 30px;
}

/* ============================================
   SECCIÓN DE BÚSQUEDA
   ============================================ */
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

/* ============================================
   LISTA DE PRODUCTOS
   ============================================ */
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

/* ============================================
   CARRITO
   ============================================ */
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
  color: #e2e8f0;
  margin-bottom: 20px;
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

/* ============================================
   PAGO Y RESUMEN
   ============================================ */
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

/* ============================================
   NOTIFICACIONES
   ============================================ */
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

.toast-notification.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-left-color: #b45309;
}

.toast-notification.warning .toast-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.toast-notification.info {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
  border-left-color: #0e7490;
}

.toast-notification.info .toast-icon {
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

/* ============================================
   RESPONSIVE
   ============================================ */
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