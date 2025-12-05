<template>
  <div class="page-background">
    <div class="main-card-container">
      <div class="venta-container">
        <!-- HEADER -->
        <div class="header-section">
          <div class="header-title">
            <h2>
              <span class="header-icon">💰</span>
              Registrar Venta de Productos
            </h2>
            <p class="header-subtitle">Agrega productos al carrito y completa la venta</p>
          </div>
          <div class="header-actions">
            <button @click="volverAlListado" class="btn-back">
              <span>←</span>
              Volver al Listado
            </button>
          </div>
        </div>

        <!-- CONTENIDO PRINCIPAL EN 2 COLUMNAS -->
        <div class="main-content">
          <!-- COLUMNA IZQUIERDA: PRODUCTOS -->
          <div class="left-column">
            <!-- FILTROS -->
            <div class="card">
              <div class="card-header">
                <div class="card-title">
                  <h3>Buscar Productos</h3>
                  <p class="card-subtitle">Filtra por nombre o categoría</p>
                </div>
              </div>
              
              <div class="filters-grid">
                <div class="filter-group">
                  <label class="filter-label">Nombre del Producto</label>
                  <div class="search-wrapper">
                    <input
                      v-model="filtroNombre"
                      placeholder="Escribe el nombre del producto..."
                      class="input-search"
                      @input="filtrarProductos"
                    />
                  </div>
                </div>
                <div class="filter-group">
                  <label class="filter-label">Categoría</label>
                  <select v-model="filtroCategoria" class="select-category">
                    <option value="">Todas las categorías</option>
                    <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                      {{ cat.nombre }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- LISTA DE PRODUCTOS -->
            <div class="card products-card">
              <div class="card-header">
                <div class="card-title">
                  <h3>Productos Disponibles</h3>
                  <p class="card-subtitle">
                    {{ productosFiltrados.length }} 
                    {{ productosFiltrados.length === 1 ? 'producto disponible' : 'productos disponibles' }}
                  </p>
                </div>
                <button @click="restablecerFiltros" class="btn-reset">
                  🔄 Restablecer
                </button>
              </div>

              <!-- TABLA DE PRODUCTOS -->
              <div class="table-container" v-if="productos.length">
                <div class="table-wrapper">
                  <table class="products-table">
                    <thead>
                      <tr>
                        <th class="col-check"></th>
                        <th class="col-name">Producto</th>
                        <th class="col-category">Categoría</th>
                        <th class="col-stock">Stock</th>
                        <th class="col-price">Precio</th>
                        <th class="col-quantity">Cantidad</th>
                        <th class="col-actions"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr 
                        v-for="producto in productosFiltrados" 
                        :key="producto.id"
                        :class="{
                          'row-selected': productoEnCarrito(producto.id),
                          'row-no-stock': producto.stock === 0
                        }"
                      >
                        <td class="col-check">
                          <div v-if="productoEnCarrito(producto.id)" class="selected-badge">
                            ✓
                          </div>
                        </td>
                        <td class="col-name">
                          <div class="product-info">
                            <span class="product-name">{{ producto.nombre }}</span>
                            <span class="product-id">ID: {{ producto.id }}</span>
                          </div>
                        </td>
                        <td class="col-category">
                          <span class="category-tag">
                            {{ obtenerNombreCategoria(producto.categoria_id) }}
                          </span>
                        </td>
                        <td class="col-stock">
                          <div class="stock-badge" :class="getStockClass(producto.stock)">
                            <span class="stock-value">{{ producto.stock }}</span>
                            <span v-if="producto.stock === 0" class="stock-label">SIN STOCK</span>
                            <span v-else-if="producto.stock <= 5" class="stock-label">BAJO</span>
                          </div>
                        </td>
                        <td class="col-price">
                          <span class="price">${{ producto.precio }}</span>
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
                            :class="{'btn-disabled': !puedeAgregarAlCarrito(producto)}"
                          >
                            {{ obtenerTextoBoton(producto) }}
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div v-else class="empty-state">
                <div class="empty-icon">📦</div>
                <div class="empty-content">
                  <h4>No hay productos disponibles</h4>
                  <p>Intenta ajustar los filtros de búsqueda</p>
                </div>
              </div>
            </div>
          </div>

          <!-- COLUMNA DERECHA: CARRITO -->
          <div class="right-column">
            <!-- CARRITO -->
            <div class="card cart-card" v-if="carrito.length > 0">
              <div class="card-header">
                <div class="card-title">
                  <h3>Carrito de Compras</h3>
                  <p class="card-subtitle">
                    {{ carrito.length }} 
                    {{ carrito.length === 1 ? 'producto agregado' : 'productos agregados' }}
                  </p>
                </div>
                <button @click="vaciarCarrito" class="btn-clear">
                  🗑️ Vaciar
                </button>
              </div>
              
              <!-- ITEMS DEL CARRITO -->
              <div class="cart-items">
                <div v-for="item in carrito" :key="item.producto.id" class="cart-item">
                  <div class="item-content">
                    <div class="item-header">
                      <span class="item-name">{{ item.producto.nombre }}</span>
                      <span class="item-price">${{ item.producto.precio }} c/u</span>
                    </div>
                    <div class="item-details">
                      <span class="detail">
                        <strong>Categoría:</strong> {{ obtenerNombreCategoria(item.producto.categoria_id) }}
                      </span>
                      <span class="detail">
                        <strong>Cantidad:</strong> {{ item.cantidad }}
                      </span>
                    </div>
                    <div class="item-subtotal">
                      <span>Subtotal:</span>
                      <strong>${{ item.subtotal }}</strong>
                    </div>
                  </div>
                  <button @click="quitarDelCarrito(item.producto.id)" class="btn-remove">
                    ✕
                  </button>
                </div>
              </div>
            </div>

            <!-- RESUMEN Y PAGO -->
            <div class="card summary-card" v-if="carrito.length > 0">
              <div class="card-header">
                <div class="card-title">
                  <h3>Completar Venta</h3>
                  <p class="card-subtitle">Selecciona el método de pago</p>
                </div>
              </div>
              
              <!-- RESUMEN -->
              <div class="summary-section">
                <div class="summary-row total-row">
                  <span>TOTAL A PAGAR:</span>
                  <span class="total-amount">${{ total.toFixed(2) }}</span>
                </div>
              </div>

              <!-- MÉTODO DE PAGO -->
              <div class="payment-section">
                <h4 class="payment-title">Método de Pago</h4>
                <div class="payment-options">
                  <div 
                    v-for="mp in metodosPago" 
                    :key="mp.id"
                    class="payment-option"
                    :class="{'payment-option-selected': datosVenta.medio_pago === mp.id}"
                    @click="datosVenta.medio_pago = mp.id"
                  >
                    <div class="payment-info">
                      <span class="payment-name">{{ mp.nombre }}</span>
                      <span class="payment-desc">{{ mp.descripcion }}</span>
                    </div>
                    <div class="payment-check" v-if="datosVenta.medio_pago === mp.id">
                      ✓
                    </div>
                  </div>
                </div>
              </div>

              <!-- BOTÓN DE CONFIRMACIÓN -->
              <button 
                @click="registrarVenta" 
                :disabled="!datosVenta.medio_pago || procesandoVenta" 
                class="btn-confirm"
                :class="{'btn-processing': procesandoVenta}"
              >
                <template v-if="!procesandoVenta">
                  <span class="btn-text">Confirmar Venta</span>
                  <span class="btn-total">${{ total.toFixed(2) }}</span>
                </template>
                <template v-else>
                  <span class="spinner">⏳</span>
                  <span>Procesando...</span>
                </template>
              </button>
            </div>

            <!-- CARRITO VACÍO -->
            <div class="card empty-cart-card" v-if="carrito.length === 0">
              <div class="empty-cart">
                <div class="empty-icon">🛒</div>
                <div class="empty-content">
                  <h4>Tu carrito está vacío</h4>
                  <p>Agrega productos desde la lista de la izquierda</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- NOTIFICACIONES -->
        <transition name="slide-up">
          <div v-if="mensaje" class="notification" :class="mensajeTipo">
            <div class="notification-content">
              <span class="notification-icon">
                <template v-if="mensajeTipo === 'success'">✅</template>
                <template v-else-if="mensajeTipo === 'error'">❌</template>
                <template v-else-if="mensajeTipo === 'warning'">⚠️</template>
                <template v-else>ℹ️</template>
              </span>
              <span class="notification-text">{{ mensaje }}</span>
            </div>
            <button @click="mensaje = ''" class="notification-close">✕</button>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Swal from 'sweetalert2';

const API_BASE_URL = 'http://localhost:8000'; 

export default {
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
                medio_pago: null
            },
            mensaje: '',
            mensajeTipo: 'success'
        }
    },
    computed: {
        productosFiltrados() {
            return this.productos.filter(p => {
                const nombreMatch = p.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase())
                const categoriaMatch = this.filtroCategoria ? p.categoria_id === parseInt(this.filtroCategoria) : true 
                return nombreMatch && categoriaMatch
            })
        },
        total() {
            return this.carrito.reduce((acc, item) => acc + item.subtotal, 0)
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
        
        stockDisponibleReal(producto) {
            const cantidadEnCarrito = this.cantidadEnCarrito(producto.id);
            return Math.max(0, producto.stock - cantidadEnCarrito);
        },
        
        puedeAgregarAlCarrito(producto) {
            if (producto.stock === 0) return false;
            
            const cantidad = this.cantidades[producto.id] || 1;
            const stockDisponible = this.stockDisponibleReal(producto);
            
            return cantidad >= 1 && cantidad <= stockDisponible;
        },
        
        obtenerTextoBoton(producto) {
            if (producto.stock === 0) return 'Sin Stock';
            
            const cantidadEnCarrito = this.cantidadEnCarrito(producto.id);
            if (cantidadEnCarrito > 0) {
                return `Agregar (${cantidadEnCarrito})`;
            }
            
            return 'Agregar';
        },

        getStockClass(stock) {
            if (stock === 0) return 'stock-critical';
            if (stock <= 5) return 'stock-low';
            return 'stock-normal';
        },

        validarCantidad(producto) {
          const cantidad = this.cantidades[producto.id] || 0;
          const stockDisponible = this.stockDisponibleReal(producto);
          
          if (cantidad > stockDisponible) {
            this.cantidades[producto.id] = stockDisponible;
            this.mostrarMensaje('Cantidad ajustada al stock disponible', 'info');
          }
        },

        filtrarProductos() {
            // Búsqueda en tiempo real
        },

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
                cancelButtonColor: '#6b7280',
                confirmButtonText: 'Sí, vaciar',
                cancelButtonText: 'Cancelar'
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
                const todosMetodos = Array.isArray(res.data) ? res.data : [];
                
                const metodosActivos = todosMetodos.filter(mp => mp.activo !== false);
                const metodosAgrupados = [];
                const tiposUsados = new Set();
                
                metodosActivos.forEach(mp => {
                    let tipoMostrar = '';
                    let idMostrar = mp.id;
                    
                    if (mp.nombre.toLowerCase().includes('efectivo')) {
                        tipoMostrar = 'Efectivo';
                    } 
                    else if (mp.nombre.toLowerCase().includes('crédito') || 
                             mp.nombre.toLowerCase().includes('debito') || 
                             mp.nombre.toLowerCase().includes('débito') || 
                             mp.nombre.toLowerCase().includes('tarjeta')) {
                        tipoMostrar = 'Tarjeta';
                    }
                    else if (mp.nombre.toLowerCase().includes('mercado') || 
                             mp.nombre.toLowerCase().includes('transferencia')) {
                        tipoMostrar = 'Transferencia';
                    }
                    
                    if (tipoMostrar && !tiposUsados.has(tipoMostrar)) {
                        tiposUsados.add(tipoMostrar);
                        metodosAgrupados.push({
                            id: idMostrar,
                            nombre: tipoMostrar,
                            tipo_original: mp.tipo,
                            descripcion: mp.descripcion || tipoMostrar,
                            requiere_confirmacion: mp.requiere_confirmacion || false
                        });
                    }
                });
                
                const tiposNecesarios = ['Efectivo', 'Tarjeta', 'Transferencia'];
                tiposNecesarios.forEach(tipo => {
                    if (!tiposUsados.has(tipo)) {
                        metodosAgrupados.push({
                            id: metodosAgrupados.length + 1,
                            nombre: tipo,
                            tipo_original: tipo.toUpperCase(),
                            descripcion: tipo,
                            requiere_confirmacion: tipo === 'Transferencia'
                        });
                    }
                });
                
                const orden = ['Efectivo', 'Tarjeta', 'Transferencia'];
                this.metodosPago = metodosAgrupados.sort((a, b) => 
                    orden.indexOf(a.nombre) - orden.indexOf(b.nombre)
                );
                
                if (this.metodosPago.length > 0) {
                    this.datosVenta.medio_pago = this.metodosPago[0].id;
                }
                
            } catch (err) { 
                console.error("❌ Error al cargar métodos de pago:", err);
                
                this.metodosPago = [
                    { id: 1, nombre: 'Efectivo', tipo_original: 'EFECTIVO', descripcion: 'Pago en efectivo', requiere_confirmacion: false },
                    { id: 2, nombre: 'Tarjeta', tipo_original: 'TARJETA', descripcion: 'Pago con tarjeta', requiere_confirmacion: true },
                    { id: 3, nombre: 'Transferencia', tipo_original: 'TRANSFERENCIA', descripcion: 'Transferencia bancaria o QR', requiere_confirmacion: true }
                ];
                
                this.datosVenta.medio_pago = 1;
            }
        },
        
        async cargarProductos() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/productos/`);
                const datosCrudos = Array.isArray(res.data) ? res.data : [];
                
                this.productos = datosCrudos.map(prod => ({
                    ...prod,
                    stock: prod.stock_actual
                }));

                this.inicializarCantidades();
            } catch (err) { 
                console.error("Error al cargar productos:", err);
                this.productos = [] 
            }
        },

        inicializarCantidades() {
            this.productos.forEach(p => { 
                p.stock = parseInt(p.stock) || 0;
                this.cantidades[p.id] = Math.min(1, p.stock);
            });
        },
        
        async cargarCategorias() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/categorias/productos/`)
                this.categorias = Array.isArray(res.data) ? res.data : []
            } catch (err) { 
                console.error("Error al cargar categorías:", err);
                this.categorias = [] 
            }
        },
        
        agregarAlCarrito(producto) {
            const cantidad = this.cantidades[producto.id];
            
            if (!this.validarStockDisponible(producto, cantidad)) {
                return;
            }

            const itemExistente = this.carrito.find(item => item.producto.id === producto.id);
            
            if (itemExistente) {
                itemExistente.cantidad += cantidad;
                itemExistente.subtotal = itemExistente.cantidad * producto.precio;
                this.mostrarMensaje(`${cantidad} unidad(es) agregadas a ${producto.nombre}`, 'success');
            } else {
                this.carrito.push({
                    producto: {
                        id: producto.id,
                        nombre: producto.nombre,
                        precio: parseFloat(producto.precio),
                        categoria_id: producto.categoria_id
                    },
                    cantidad,
                    subtotal: cantidad * producto.precio
                });
                this.mostrarMensaje(`${producto.nombre} agregado al carrito`, 'success');
            }
            
            this.actualizarStockVisual(producto.id, -cantidad);
            this.cantidades[producto.id] = 1;
        },
        
        validarStockDisponible(producto, cantidad) {
          if (cantidad < 1) {
            this.mostrarMensaje('La cantidad debe ser al menos 1', 'error');
            return false;
          }
          
          const stockDisponible = this.stockDisponibleReal(producto);
          
          if (cantidad > stockDisponible) {
            this.mostrarMensaje(`Stock insuficiente. Disponible: ${stockDisponible} unidades`, 'error');
            this.cantidades[producto.id] = stockDisponible;
            return false;
          }
          
          if (producto.stock === 0) {
            this.mostrarMensaje('Este producto no tiene stock disponible', 'error');
            return false;
          }
          
          return true;
        },
        
        actualizarStockVisual(productoId, cambio) {
            const producto = this.productos.find(p => p.id === productoId);
            if (producto) {
                producto.stock = Math.max(0, producto.stock + cambio);
                if (producto.stock === 0) {
                    this.cantidades[productoId] = 0;
                }
            }
        },
        
        quitarDelCarrito(productoId) {
            const itemIndex = this.carrito.findIndex(item => item.producto.id === productoId);
            if (itemIndex !== -1) {
                const item = this.carrito[itemIndex];
                const cantidadDevuelta = item.cantidad;
                const productoNombre = item.producto.nombre;
                
                this.actualizarStockVisual(productoId, cantidadDevuelta);
                this.carrito.splice(itemIndex, 1);

                this.mostrarMensaje(`${productoNombre} removido del carrito`, 'info');
            }
        },
        
        async registrarVenta() {
            console.log("🔄 Iniciando registro de venta...");
            
            if (!this.validarVenta()) return;

            this.procesandoVenta = true;

            Swal.fire({
                title: 'Registrando Venta...',
                text: 'Por favor espere',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            try {
                const payload = this.prepararPayloadVenta();
                console.log("📦 Payload enviado:", payload);

                const response = await axios.post(`${API_BASE_URL}/usuarios/api/ventas/registrar/`, payload);
                
                if (response.status === 201) {
                    console.log("✅ Venta registrada en backend");
                    await this.procesarVentaExitosa(response.data);
                }
            } catch (err) {
                console.error("❌ Error en registrarVenta:", err);
                await this.manejarErrorVenta(err);
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
                subtotal: parseFloat(item.subtotal)
            }));
            
            return { 
                total: parseFloat(this.total),
                tipo: 'PRODUCTO', 
                medio_pago: parseInt(this.datosVenta.medio_pago),
                detalles,
                cliente: null,
                usuario: 1
            };
        },

        async procesarVentaExitosa(ventaData) {
            console.log("🔄 procesarVentaExitosa iniciado:", ventaData);
            
            const totalConfirmado = parseFloat(ventaData.total);

            Swal.close();
            
            this.limpiarFormulario();
            await this.cargarProductos();
            
            this.$emit('venta-registrada', ventaData);
            
            const result = await Swal.fire({
                title: '¡Venta Registrada Exitosamente!',
                html: `
                    <div style="text-align: left; margin: 20px 0;">
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <strong>N° de Venta:</strong>
                                <span>#${ventaData.id}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <strong>Total:</strong>
                                <span style="color: #28a745; font-weight: bold;">$${totalConfirmado.toFixed(2)}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <strong>Método de Pago:</strong>
                                <span>${ventaData.medio_pago_nombre || 'Efectivo'}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Fecha:</strong>
                                <span>${new Date().toLocaleDateString('es-ES')}</span>
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
                cancelButtonText: '➡️ Continuar sin abrir',
                confirmButtonColor: '#28a745',
                cancelButtonColor: '#6c757d',
                reverseButtons: true,
                backdrop: true,
                allowOutsideClick: false
            });

            if (result.isConfirmed) {
                this.abrirComprobante(ventaData.id);
            } else {
                this.continuarSinAbrir();
            }
        },

        abrirComprobante(ventaId) {
            console.log("📄 Abriendo comprobante...");
            const pdfUrl = `${API_BASE_URL}/usuarios/api/ventas/${ventaId}/comprobante-pdf/`;
            window.open(pdfUrl, '_blank');
            
            this.$emit('venta-completada');
        },

        continuarSinAbrir() {
            console.log("➡️ Continuando sin comprobante...");
            this.$emit('venta-completada');
        },

        limpiarFormulario() {
            console.log("🧹 Limpiando formulario...");
            this.carrito = [];
            this.datosVenta.medio_pago = this.metodosPago[0]?.id || null;
            this.filtroNombre = '';
            this.filtroCategoria = '';
        },

        async manejarErrorVenta(err) {
            console.error("❌ Error completo:", err);
            
            Swal.close();
            
            let errorMessage = 'Error al registrar venta';
            
            if (err.response?.data) {
                if (err.response.status === 401) {
                    errorMessage = 'Debe iniciar sesión para registrar una venta.';
                } else {
                    errorMessage = JSON.stringify(err.response.data);
                }
            }
            
            Swal.fire({
                icon: 'error',
                title: 'Error al Registrar Venta',
                text: errorMessage,
                confirmButtonText: 'Entendido'
            });
            
            await this.cargarProductos();
        },

        mostrarMensaje(texto, tipo = 'info') {
            this.mensaje = texto;
            this.mensajeTipo = tipo;
            
            setTimeout(() => {
                this.mensaje = '';
            }, 4000);
        },

        volverAlListado() {
            if (this.carrito.length > 0) {
                Swal.fire({
                    title: '¿Salir sin completar la venta?',
                    text: 'Tienes productos en el carrito que se perderán',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#ef4444',
                    cancelButtonColor: '#6b7280',
                    confirmButtonText: 'Sí, salir',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.$emit('volver-al-listado');
                    }
                });
            } else {
                this.$emit('volver-al-listado');
            }
        }
    },
    
    mounted() {
        console.log("🚀 Componente RegistrarVenta.vue cargado");
        this.cargarProductos();
        this.cargarCategorias();
        this.cargarMetodosPago();
    }
}
</script>

<style scoped>
/* ============================================
   FONDO Y LAYOUT PRINCIPAL
   ============================================ */
.page-background {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.main-card-container {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 1800px;
  margin: 0 auto;
  padding: 30px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.venta-container {
  width: 100%;
  padding: 0;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ============================================
   HEADER
   ============================================ */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 25px 30px;
  background: linear-gradient(135deg, #1f2937, #374151);
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.header-title h2 {
  margin: 0 0 8px 0;
  color: white;
  font-size: 2em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: #60a5fa;
}

.header-subtitle {
  margin: 0;
  color: #cbd5e1;
  font-size: 1.1em;
}

.btn-back {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.25);
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1em;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-back:hover { 
  background: rgba(255, 255, 255, 0.25); 
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px); 
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

/* ============================================
   LAYOUT DE 2 COLUMNAS
   ============================================ */
.main-content {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 30px;
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* ============================================
   CARDS GENERALES
   ============================================ */
.card {
  background: #fff;
  border-radius: 18px;
  border: 1px solid #e5e7eb;
  padding: 30px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.card-title h3 {
  margin: 0 0 6px 0;
  color: #1f2937;
  font-size: 1.4em;
  font-weight: 700;
}

.card-subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.95em;
}

/* ============================================
   FILTROS
   ============================================ */
.filters-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 25px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filter-label {
  font-weight: 600;
  color: #374151;
  font-size: 1em;
  margin-left: 4px;
}

.search-wrapper {
  position: relative;
}

.input-search {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: #f9fafb;
  font-size: 1em;
  transition: all 0.3s ease;
  color: #1f2937;
  font-weight: 500;
}

.input-search:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
  outline: none;
}

.select-category {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: #f9fafb;
  font-size: 1em;
  transition: all 0.3s ease;
  color: #1f2937;
  font-weight: 500;
  cursor: pointer;
}

.select-category:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
  outline: none;
}

.btn-reset {
  background: #f3f4f6;
  color: #6b7280;
  border: 2px solid #e5e7eb;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9em;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-reset:hover {
  background: #e5e7eb;
  color: #374151;
}

/* ============================================
   TABLA DE PRODUCTOS
   ============================================ */
.table-container {
  margin-top: 15px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
}

.products-table thead {
  background: #f8fafc;
  border-bottom: 2px solid #e5e7eb;
}

.products-table th {
  padding: 18px 16px;
  text-align: left;
  color: #374151;
  font-weight: 600;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.products-table tbody tr {
  border-bottom: 1px solid #f1f3f4;
  transition: all 0.2s ease;
}

.products-table tbody tr:hover {
  background: #f8fafc;
}

.products-table tbody tr.row-selected {
  background: #f0fdf4;
  border-left: 4px solid #10b981;
}

.products-table tbody tr.row-no-stock {
  opacity: 0.7;
  background: #f9fafb;
}

.products-table td {
  padding: 16px 16px;
  vertical-align: middle;
}

/* Columnas específicas */
.col-check {
  width: 60px;
  text-align: center;
}

.selected-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #10b981;
  border-radius: 50%;
  color: white;
  font-weight: bold;
  font-size: 0.9em;
}

.col-name {
  min-width: 250px;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.05em;
}

.product-id {
  color: #6b7280;
  font-size: 0.85em;
  font-family: monospace;
}

.col-category {
  min-width: 150px;
}

.category-tag {
  background: #e7f3ff;
  color: #1d4ed8;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85em;
  font-weight: 500;
  border: 1px solid #b3d9ff;
  display: inline-block;
}

.col-stock {
  min-width: 120px;
}

.stock-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9em;
}

.stock-badge.stock-critical {
  background: #fee2e2;
  color: #dc2626;
}

.stock-badge.stock-low {
  background: #fef3c7;
  color: #d97706;
}

.stock-badge.stock-normal {
  background: #d1fae5;
  color: #059669;
}

.stock-value {
  font-size: 1.1em;
}

.stock-label {
  font-size: 0.8em;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.stock-critical .stock-label {
  background: #dc2626;
  color: white;
}

.stock-low .stock-label {
  background: #d97706;
  color: white;
}

.col-price {
  min-width: 120px;
}

.price {
  font-weight: 700;
  color: #059669;
  font-size: 1.1em;
}

.col-quantity {
  min-width: 140px;
}

.quantity-input {
  width: 100px;
  text-align: center;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  font-weight: 600;
  color: #1f2937;
  font-size: 1em;
}

.quantity-input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.quantity-input:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.col-actions {
  min-width: 150px;
  text-align: right;
}

.btn-add {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95em;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-add:hover:not(.btn-disabled) {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-add.btn-disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

/* ============================================
   CARRITO
   ============================================ */
.cart-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 10px;
}

.cart-items::-webkit-scrollbar {
  width: 6px;
}

.cart-items::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.cart-items::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  background: #f8fafc;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.cart-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.item-content {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.item-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1em;
  flex: 1;
}

.item-price {
  color: #059669;
  font-weight: 700;
  font-size: 1.05em;
  white-space: nowrap;
}

.item-details {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.detail {
  color: #6b7280;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-subtotal {
  text-align: left;
}

.item-subtotal span {
  display: block;
  font-size: 0.85em;
  color: #6b7280;
  margin-bottom: 4px;
}

.item-subtotal strong {
  font-weight: 700;
  color: #059669;
  font-size: 1.2em;
}

.btn-remove {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1.1em;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-remove:hover {
  background: #fecaca;
  transform: scale(1.1);
}

.btn-clear {
  background: #fee2e2;
  color: #dc2626;
  border: 2px solid #fecaca;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9em;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-clear:hover {
  background: #fecaca;
  color: #b91c1c;
}

/* ============================================
   RESUMEN
   ============================================ */
.summary-section {
  margin: 20px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 14px;
  border: 2px solid #e5e7eb;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  font-size: 1.3em;
  font-weight: 700;
  color: #1f2937;
}

.total-amount {
  color: #059669;
  font-size: 1.4em;
}

/* ============================================
   MÉTODOS DE PAGO
   ============================================ */
.payment-section {
  margin: 25px 0;
}

.payment-title {
  margin: 0 0 20px 0;
  color: #1f2937;
  font-size: 1.1em;
  font-weight: 600;
}

.payment-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.payment-option:hover {
  border-color: #93c5fd;
  background: #f0f9ff;
}

.payment-option-selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.payment-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.payment-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1em;
}

.payment-desc {
  color: #6b7280;
  font-size: 0.9em;
}

.payment-check {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #10b981;
  border-radius: 50%;
  color: white;
  font-weight: bold;
  font-size: 0.9em;
  flex-shrink: 0;
}

/* ============================================
   BOTÓN DE CONFIRMACIÓN
   ============================================ */
.btn-confirm {
  width: 100%;
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  padding: 20px;
  border: none;
  border-radius: 14px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.btn-confirm:hover:not(.btn-processing):not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(5, 150, 105, 0.3);
  background: linear-gradient(135deg, #047857, #065f46);
}

.btn-confirm:disabled,
.btn-confirm.btn-processing {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  opacity: 0.7;
}

.btn-text {
  flex: 1;
  text-align: center;
}

.btn-total {
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 1em;
}

.spinner {
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ============================================
   ESTADOS VACÍOS
   ============================================ */
.empty-state, .empty-cart {
  text-align: center;
  padding: 50px 20px;
  color: #6b7280;
}

.empty-icon {
  opacity: 0.5;
  margin-bottom: 20px;
  font-size: 3em;
  color: #9ca3af;
}

.empty-state h4, .empty-cart h4 {
  margin: 0 0 12px 0;
  font-size: 1.3em;
  color: #1f2937;
  font-weight: 600;
}

.empty-state p, .empty-cart p {
  margin: 0;
  font-size: 1em;
  color: #6b7280;
}

/* ============================================
   NOTIFICACIONES
   ============================================ */
.notification {
  position: fixed;
  bottom: 40px;
  right: 40px;
  min-width: 300px;
  max-width: 400px;
  background: white;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 9999;
  border-left: 6px solid;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.notification.success {
  border-left-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}

.notification.error {
  border-left-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
}

.notification.warning {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
}

.notification.info {
  border-left-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.notification-icon {
  font-size: 1.3em;
}

.notification-text {
  color: #1f2937;
  font-weight: 500;
}

.notification-close {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 1.1em;
  padding: 5px;
  transition: color 0.2s ease;
}

.notification-close:hover {
  color: #374151;
}

/* ============================================
   ANIMACIONES
   ============================================ */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1400px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .main-card-container {
    max-width: 1200px;
  }
}

@media (max-width: 1024px) {
  .page-background {
    padding: 15px;
  }
  
  .main-card-container {
    padding: 25px;
    border-radius: 20px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
    padding: 20px;
  }
  
  .header-title {
    text-align: center;
  }
  
  .btn-back {
    width: 100%;
    justify-content: center;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-card-container {
    padding: 20px;
    margin: 10px;
  }
  
  .card {
    padding: 25px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .table-wrapper {
    border-radius: 12px;
  }
  
  .products-table th,
  .products-table td {
    padding: 14px 12px;
  }
  
  .notification {
    left: 20px;
    right: 20px;
    bottom: 20px;
    min-width: auto;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .page-background {
    padding: 10px;
  }
  
  .main-card-container {
    padding: 15px;
    border-radius: 16px;
  }
  
  .card {
    padding: 20px;
  }
  
  .header-section h2 {
    font-size: 1.6em;
  }
  
  .btn-confirm {
    padding: 18px;
    font-size: 1em;
    flex-direction: column;
    gap: 10px;
  }
  
  .payment-option {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
}
</style>