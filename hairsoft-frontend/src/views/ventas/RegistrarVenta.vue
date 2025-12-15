<template>
  <div class="page-background">
    <div class="main-card-container">
      <div class="venta-container">
        <div class="header-section">
          <h2>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="header-icon"><path d="M21 12H3M21 12V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v7"></path><path d="M12 14v8M9 20h6"></path></svg>
            Registrar Venta (Productos)
          </h2>
          <button @click="volverAlListado" class="btn-back">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
            Volver
          </button>
        </div>

        <div class="main-content">
          <div class="left-column">
            
            <div class="card-modern">
              <div class="card-header">
                <div class="card-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </div>
                <h3>Buscar Productos</h3>
              </div>
              
              <div class="filters-grid">
                <div class="input-group">
                  <label class="label-modern">Nombre/Código</label>
                  <input
                    v-model="filtroNombre"
                    placeholder="Escribe el nombre o código..."
                    class="input-modern"
                    @input="filtrarProductos"
                  />
                </div>
                <div class="input-group">
                  <label class="label-modern">Categoría</label>
                  <select v-model="filtroCategoria" class="select-modern">
                    <option value="">Todas</option>
                    <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                      {{ cat.nombre }}
                    </option>
                  </select>
                </div>
                <button @click="restablecerFiltros" class="clear-filters-btn">
                    🔄 Restablecer
                </button>
              </div>
            </div>

            <div class="card-modern products-card">
              <div class="card-header">
                <div class="card-icon">
                   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                </div>
                <h3>Lista de Productos</h3>
                <p class="card-subtitle-right">
                  {{ productosFiltrados.length }} disponibles
                </p>
              </div>

              <div class="table-container" v-if="productosFiltrados.length > 0">
                <div class="table-wrapper">
                  <table class="products-table">
                    <thead>
                      <tr>
                        <th class="col-name-prod">Producto</th>
                        <th class="col-category">Categoría</th>
                        <th class="col-price">Precio</th>
                        <th class="col-stock">Stock</th>
                        <th class="col-quantity">Cant.</th>
                        <th class="col-actions"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr 
                        v-for="producto in productosFiltrados" 
                        :key="producto.id"
                        :class="{'row-selected': productoEnCarrito(producto.id), 'row-no-stock': producto.stock === 0}"
                      >
                        <td class="col-name-prod">
                          <div class="product-info">
                            <span class="product-name">{{ producto.nombre }}</span>
                            <span class="product-id" v-if="productoEnCarrito(producto.id)">✓ En Carrito</span>
                          </div>
                        </td>
                        <td class="col-category">
                          <span class="category-tag">
                            {{ obtenerNombreCategoria(producto.categoria) }}
                          </span>
                        </td>
                        <td class="col-price">
                          <span class="price">${{ parseFloat(producto.precio).toFixed(2) }}</span>
                        </td>
                        <td class="col-stock">
                          <div class="stock-badge" :class="getStockClass(producto.stock)">
                            {{ producto.stock }}
                          </div>
                        </td>
                        <td class="col-quantity">
                          <input 
                            type="number" 
                            min="1" 
                            :max="stockDisponibleReal(producto)" 
                            v-model.number="cantidades[producto.id]" 
                            :disabled="producto.stock === 0"
                            class="quantity-input"
                            @change="validarCantidad(producto)"
                          />
                        </td>
                        <td class="col-actions">
                          <button 
                            @click="agregarAlCarrito(producto)" 
                            :disabled="!puedeAgregarAlCarrito(producto)"
                            class="btn-add"
                          >
                            {{ obtenerTextoBoton(producto) }}
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div v-else class="no-resultados">
                <p>No hay productos activos o con stock disponible.</p>
              </div>
            </div>
          </div>

          <div class="right-column">
            
            <div class="card-modern cart-card">
              <div class="card-header">
                <div class="card-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
                </div>
                <h3>Carrito ({{ carrito.length }})</h3>
              </div>
              
              <div v-if="carrito.length === 0" class="empty-cart">
                <div class="empty-icon">🛒</div>
                <p>Agrega productos</p>
              </div>

              <div v-else>
                <div class="cart-items">
                  <div v-for="item in carrito" :key="item.producto.id" class="cart-item">
                    <div class="item-content">
                      <div class="item-header">
                        <span class="item-name">{{ item.producto.nombre }}</span>
                        <span class="item-price">${{ parseFloat(item.producto.precio).toFixed(2) }}</span>
                      </div>
                      <div class="item-details">
                        <span class="detail">Cant.: <strong>{{ item.cantidad }}</strong></span>
                        <span class="detail">Subtotal: <strong>${{ parseFloat(item.subtotal).toFixed(2) }}</strong></span>
                      </div>
                    </div>
                    <button @click="quitarDelCarrito(item.producto.id)" class="btn-remove">✕</button>
                  </div>
                </div>

                <button @click="vaciarCarrito" class="btn-secondary-full">🗑️ Vaciar Carrito</button>
              </div>
            </div>

            <div class="card-modern summary-card" v-if="carrito.length > 0">
              <div class="card-header">
                <div class="card-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-4"></path><path d="M6 10h12M12 15h1"></path><path d="M17 17h5M17 14v4"></path></svg>
                </div>
                <h3>Total y Pago</h3>
              </div>
              
              <div class="resumen-grid">
                <div class="resumen-item total">
                  <span>TOTAL A PAGAR:</span>
                  <strong class="total-amount">${{ total.toFixed(2) }}</strong>
                </div>
              </div>

              <div class="input-group">
                <label class="label-modern">Método de Pago *</label>
                <select v-model="datosVenta.medio_pago" class="select-modern">
                  <option :value="null">-- Seleccionar --</option>
                  <option 
                    v-for="mp in metodosPago" 
                    :key="mp.id" 
                    :value="mp.id"
                  >
                    {{ mp.nombre }}
                  </option>
                </select>
              </div>

              <button 
                @click="registrarVenta" 
                :disabled="!datosVenta.medio_pago || procesandoVenta || carrito.length === 0" 
                class="btn-confirmar-premium"
              >
                <template v-if="!procesandoVenta">
                  Confirmar Venta (${{ total.toFixed(2) }})
                </template>
                <template v-else>
                  <span class="spinner">⏳</span>
                  <span>Procesando...</span>
                </template>
              </button>
            </div>
          </div>
        </div>

        <transition name="fade">
          <div v-if="mensaje" class="toast-message" :class="mensajeTipo">
            <span class="notification-icon">
                <template v-if="mensajeTipo === 'success'">✅</template>
                <template v-else-if="mensajeTipo === 'error'">❌</template>
                <template v-else-if="mensajeTipo === 'warning'">⚠️</template>
            </span>
            {{ mensaje }}
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default {
    name: 'RegistrarVenta',
    
    // ✅ AGREGAR ESTO para inyectar el router
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
                usuario: 1 
            },
            mensaje: '',
            mensajeTipo: 'success'
        }
    },
    
    // ✅ AGREGAR computed para el router si es necesario
    computed: {
        // ... tus computed actuales ...
        productosFiltrados() {
            return this.productos.filter(p => {
                const nombreMatch = p.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase())
                const categoriaMatch = this.filtroCategoria ? p.categoria === parseInt(this.filtroCategoria) : true 
                return nombreMatch && categoriaMatch && p.estado === 'ACTIVO' 
            })
        },
        total() {
            return this.carrito.reduce((acc, item) => acc + item.subtotal, 0)
        }
    },
    
    methods: {
        navegarAListado() {
            console.log("🚀 Iniciando navegación al listado de ventas");
            
            // PRIMERO: Verificar si ya estamos en /ventas
            if (this.$route.path === '/ventas') {
                console.log("⚠️ Ya estamos en /ventas, recargando...");
                window.location.reload();
                return;
            }
            
            // SEGUNDO: Intentar navegación Vue Router
            this.$router.push('/ventas')
                .then(() => {
                    console.log("✅ Vue Router: Navegación exitosa");
                    
                    // Si después de 500ms aún no cambió, forzar recarga
                    setTimeout(() => {
                        if (this.$route.path !== '/ventas') {
                            console.log("⏰ Timeout: Forzando navegación directa");
                            window.location.href = '/ventas';
                        }
                    }, 500);
                })
                .catch((error) => {
                    console.error("❌ Vue Router error:", error);
                    console.log("🔄 Usando navegación directa como fallback");
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
            
            // 🔥 FLUJO DE COMPROBANTE REQUERIDO
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
                // Esperar un momento y luego navegar
                setTimeout(() => {
                    this.navegarAListado();
                }, 500);
            } else {
                // Redirigir inmediatamente cuando se hace clic en "Continuar"
                this.navegarAListado();
            }
        },

        // ... TUS OTROS MÉTODOS SIN CAMBIOS ...
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
            if (stock === 0) return 'stock-critical';
            if (stock <= 5) return 'stock-low';
            return 'stock-normal';
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
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/metodos-pago/`); 
                this.metodosPago = Array.isArray(res.data) ? res.data.filter(mp => mp.activo !== false) : [];
                if (this.metodosPago.length > 0) {
                    this.datosVenta.medio_pago = this.metodosPago[0].id;
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
            
            return { 
                total: parseFloat(this.total),
                tipo: 'PRODUCTO', 
                medio_pago: parseInt(this.datosVenta.medio_pago),
                detalles,
                cliente: null,
                usuario: this.datosVenta.usuario 
            };
        },

        abrirComprobante(ventaId) {
            console.log("📄 Abriendo comprobante...");
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
            this.datosVenta.medio_pago = this.metodosPago[0]?.id || null;
            this.filtroNombre = '';
            this.filtroCategoria = '';
        }
    },
    
    mounted() {
        console.log("Componente montado. Router disponible:", this.$router);
        console.log("Router inyectado:", this.router);
        
        this.cargarProductos();
        this.cargarCategorias();
        this.cargarMetodosPago();
    }
}
</script>

<style scoped>
/* ========================================================
   🔥 ESTILOS DE TURNOS PRESENCIALES (Copia limpia)
   ======================================================== */
.page-background {
  min-height: 100vh;
  padding: 30px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.main-card-container {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.venta-container {
  width: 100%;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* --- HEADER --- */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #1f2937, #374151);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.header-section h2 {
  margin: 0;
  color: white;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header-icon { 
  color: #60a5fa; 
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.btn-back {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
}

.btn-back:hover { 
  background: rgba(255, 255, 255, 0.2); 
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px); 
}

/* --- LAYOUT DE 2 COLUMNAS (ADAPTACIÓN) --- */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr; 
  gap: 30px;
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* --- CARDS MODERNAS (Estilo Turnos) --- */
.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 25px;
  margin-bottom: 0px; 
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #3b82f6;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f1f3f4;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 12px;
  color: white;
  box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
}

.card-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
}

.card-subtitle-right {
  margin: 0;
  color: #6b7280;
  font-size: 0.9em;
}

/* --- FORM Y FILTROS --- */
.input-group {
    margin-bottom: 15px;
}

.label-modern {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1f2937;
  font-size: 1rem;
}

.input-modern, .select-modern {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 15px;
  transition: all 0.3s ease;
  color: #1f2937;
}

.input-modern:focus, .select-modern:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.filters-grid { 
    display: grid; 
    grid-template-columns: 1fr 1fr auto; 
    gap: 15px;
    align-items: end;
}

.clear-filters-btn {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  height: 48px;
}
.clear-filters-btn:hover { background: #e5e7eb; }

/* --- TABLA (Estilo de Listado) --- */
.table-container {
  margin-top: 15px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.table-wrapper {
  overflow-x: auto;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.products-table th {
  padding: 16px 14px;
  text-align: left;
  background: #f8fafc;
  color: #374151;
  font-weight: 600;
  font-size: 0.85em;
  text-transform: uppercase;
}

.products-table td {
  padding: 14px;
  border-bottom: 1px solid #f1f3f4;
  vertical-align: middle;
}

.products-table tbody tr:hover { background: #f8fafc; }
.row-selected { background: #f0fdf4 !important; border-left: 4px solid #10b981; }
.row-no-stock { opacity: 0.7; background: #f9fafb; }

.product-name { font-weight: 600; color: #1f2937; }
.product-id { color: #6b7280; font-size: 0.8em; display: block; }
.category-tag { background: #e7f3ff; color: #1d4ed8; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }

.stock-badge { padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 0.9em; min-width: 60px; text-align: center;}
.stock-critical { background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }
.stock-low { background: #fef3c7; color: #d97706; border: 1px solid #fcd34d; }
.stock-normal { background: #d1fae5; color: #059669; border: 1px solid #6ee7b7; }

.quantity-input { width: 60px; text-align: center; padding: 8px; border: 1px solid #e5e7eb; border-radius: 6px; }
.btn-add { background: #3b82f6; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: 600; transition: all 0.3s ease; }
.btn-add:hover:not(.btn-disabled) { background: #2563eb; }
.btn-add.btn-disabled { background: #9ca3af; cursor: not-allowed; }


/* --- CARRITO / DERECHA --- */
.cart-items { display: flex; flex-direction: column; gap: 10px; max-height: 400px; overflow-y: auto; padding-right: 10px; }
.cart-item { padding: 15px; background: #f8fafc; border-radius: 12px; border: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
.item-name { font-weight: 600; color: #1f2937; }
.item-details { color: #6b7280; font-size: 0.9em; }
.item-details strong { color: #1f2937; }
.btn-remove { background: #fee2e2; color: #dc2626; border: none; width: 30px; height: 30px; border-radius: 6px; }
.btn-secondary-full { background: #f3f4f6; color: #dc2626; border: 1px solid #e5e7eb; padding: 12px; border-radius: 10px; font-weight: 600; width: 100%; margin-top: 15px; }

/* --- RESUMEN Y PAGO --- */
.resumen-grid { margin: 20px 0 10px 0; }
.resumen-item.total { padding: 12px 0; font-size: 1.3em; font-weight: 700; border-top: 2px solid #f1f3f4; margin-top: 10px; padding-top: 10px; }
.total-amount { color: #059669; font-size: 1.4em; }

/* Botón Final (Estilo Confirmar Turno) */
.btn-confirmar-premium {
  width: 100%; 
  background: linear-gradient(135deg, #059669, #047857); 
  color: white; 
  padding: 18px; 
  border: none;
  border-radius: 12px; 
  font-size: 1.1em; 
  font-weight: 700; 
  cursor: pointer; 
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.btn-confirmar-premium:hover:not(:disabled) { 
  transform: translateY(-3px); 
  box-shadow: 0 10px 25px rgba(5, 150, 105, 0.4);
}

.btn-confirmar-premium:disabled { 
  background: #9ca3af; 
  cursor: not-allowed; 
  opacity: 0.7;
}

.spinner { animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- ESTADOS VACÍOS --- */
.empty-cart, .no-resultados { text-align: center; padding: 30px 20px; color: #6b7280; }
.empty-icon { opacity: 0.5; margin-bottom: 15px; font-size: 2em; color: #9ca3af; }
.empty-cart p, .no-resultados p { margin: 0; font-size: 0.95em; color: #6b7280; }
.empty-cart h4, .no-resultados h4 { margin: 0 0 8px 0; font-size: 1.2em; color: #1f2937; font-weight: 600; }

/* --- NOTIFICACIONES --- */
.toast-message { position: fixed; bottom: 30px; right: 30px; padding: 15px 20px; border-radius: 10px; font-weight: 600; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
.toast-message.success { background: #d1fae5; color: #059669; }
.toast-message.error { background: #fee2e2; color: #dc2626; }
.toast-message.warning { background: #fef3c7; color: #d97706; }

/* --- RESPONSIVE --- */
@media (max-width: 1200px) {
  .main-content { grid-template-columns: 1fr; }
  .main-card-container { max-width: 900px; }
  .right-column { min-width: 100%; }
}

@media (max-width: 768px) {
  .main-card-container { padding: 25px; border-radius: 20px; }
  .header-section { flex-direction: column; align-items: stretch; gap: 15px; padding: 20px; }
  .btn-back { width: 100%; justify-content: center; }
  .card-modern { padding: 20px; }
  .filters-grid { grid-template-columns: 1fr 1fr; }
  .filters-grid .clear-filters-btn { grid-column: span 2; height: auto; }
  .products-table { min-width: 600px; }
  .total-amount { font-size: 1.3em; }
}
</style>