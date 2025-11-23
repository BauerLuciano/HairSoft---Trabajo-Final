<template>
  <!-- Tu template permanece exactamente igual -->
  <div class="pedido-container">
    <div class="header-section">
      <h2>
        <span class="header-icon">💰</span>
        Registrar Venta de Productos
      </h2>
    </div>

    <!-- Filtros de productos -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">🔍</div>
        <h3>Filtros de Búsqueda</h3>
      </div>
      <div class="input-group">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input v-model="filtroNombre" placeholder="Buscar producto por nombre" class="input-modern"/>
        </div>
        <select v-model="filtroCategoria" class="select-modern">
          <option value="">Todas las categorías</option>
          <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
        </select>
      </div>
    </div>

    <!-- Lista de productos -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">📦</div>
        <h3>Productos Disponibles</h3>
        <div class="badge-count" v-if="productosFiltrados.length > 0">
          {{ productosFiltrados.length }} {{ productosFiltrados.length === 1 ? 'producto' : 'productos' }}
        </div>
      </div>

      <div v-if="productos.length" class="productos-grid">
        <div v-for="producto in productosFiltrados" :key="producto.id" class="producto-item" :class="{'sin-stock': producto.stock === 0}">
          <div class="producto-info">
            <div class="producto-header">
              <span class="producto-nombre">{{ producto.nombre }}</span>
              <span class="producto-precio">${{ producto.precio }}</span>
            </div>
            <div class="producto-details">
              <span class="producto-codigo">
                <span>ID:</span>
                <strong>{{ producto.id }}</strong>
              </span>
              <span class="producto-categoria">
                <span>Categoría:</span>
                <strong>{{ obtenerNombreCategoria(producto.categoria_id) }}</strong>
              </span>
              <span class="producto-stock" :class="{
                'stock-critico': producto.stock === 0, 
                'stock-bajo': producto.stock > 0 && producto.stock <= 5,
                'stock-medio': producto.stock > 5 && producto.stock <= 15,
                'stock-alto': producto.stock > 15
              }">
                <span>Stock:</span>
                <strong>{{ producto.stock }}</strong>
                <span v-if="producto.stock === 0" class="sin-stock-badge">SIN STOCK</span>
                <span v-else-if="producto.stock <= 5" class="stock-bajo-badge">BAJO</span>
                
                <span v-if="productoEnCarrito(producto.id)" class="stock-carrito-info">
                  (En carrito: {{ cantidadEnCarrito(producto.id) }})
                </span>
              </span>
            </div>
          </div>
          <div class="producto-actions">
            <div class="control-group">
              <label for="cantidad">
                <span>Cantidad:</span>
              </label>
              <input 
                id="cantidad"
                type="number" 
                min="1" 
                :max="stockDisponibleReal(producto)" 
                v-model.number="cantidades[producto.id]" 
                :disabled="producto.stock === 0"
                class="input-cantidad"
                :class="{'input-disabled': producto.stock === 0}"
                @change="validarCantidad(producto)"
              />
            </div>
            <button 
              @click="agregarAlCarrito(producto)" 
              :disabled="!puedeAgregarAlCarrito(producto)"
              class="btn-agregar-masivo"
              :class="{'btn-disabled': !puedeAgregarAlCarrito(producto)}"
            >
              {{ obtenerTextoBoton(producto) }}
            </button>
          </div>
        </div>
      </div>
      <div v-else class="no-resultados">
        <div class="no-resultados-icon">📦</div>
        <p>No hay productos disponibles</p>
        <small>Intenta ajustar los filtros de búsqueda</small>
      </div>
    </div>

    <!-- Carrito Mejorado -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">🛒</div>
        <h3>Carrito de Compras</h3>
        <div class="badge-count" v-if="carrito.length > 0">
          {{ carrito.length }} {{ carrito.length === 1 ? 'producto' : 'productos' }}
        </div>
      </div>
      
      <div v-if="carrito.length" class="detalles-list">
        <div v-for="item in carrito" :key="item.producto.id" class="detalle-item">
          <div class="detalle-info">
            <div class="detalle-header">
              <span class="detalle-nombre">{{ item.producto.nombre }}</span>
              <span class="detalle-categoria">
                <span>Categoría:</span>
                <strong>{{ obtenerNombreCategoria(item.producto.categoria_id) }}</strong>
              </span>
            </div>
            <div class="detalle-details">
              <span class="detalle-codigo">
                <span>ID:</span>
                <strong>{{ item.producto.id }}</strong>
              </span>
              <span class="detalle-precio">
                <span>Precio:</span>
                <strong>${{ item.producto.precio }}</strong>
              </span>
            </div>
          </div>
          <div class="detalle-controls">
            <div class="control-group">
              <label for="cantidad-carrito">
                <span>Cantidad:</span>
              </label>
              <span class="input-cantidad">{{ item.cantidad }}</span>
            </div>
            <div class="detalle-subtotal">
              <div class="subtotal-label">
                <span>Subtotal:</span>
              </div>
              <div class="subtotal-value">${{ item.subtotal }}</div>
            </div>
            <button @click="quitarDelCarrito(item.producto.id)" class="btn-eliminar" title="Quitar del carrito">
              <span class="trash-icon">🗑️</span>
            </button>
          </div>
        </div>
        
        <!-- Resumen del carrito -->
        <div class="resumen-pedido">
          <div class="resumen-grid">
            <div class="resumen-item total">
              <span>
                <span>Total a Pagar:</span>
              </span>
              <span>${{ total.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-resultados">
        <div class="no-resultados-icon">🛒</div>
        <p>Tu carrito está vacío</p>
        <small>Agrega productos desde la lista arriba</small>
      </div>
    </div>

    <!-- Selector de pago -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">💳</div>
        <h3>Información de Pago</h3>
      </div>
      <div class="input-group">
        <label for="medio_pago" class="info-label">Medio de Pago</label>
        <select id="medio_pago" v-model.number="datosVenta.medio_pago" class="select-modern">
          <option :value="null" disabled>Seleccione método de pago</option>
          <option v-for="mp in metodosPago" :key="mp.id" :value="mp.id">
            {{ mp.nombre }}
          </option>
        </select>
      </div>
    </div>

    <button 
        @click="registrarVenta" 
        :disabled="carrito.length === 0 || !datosVenta.medio_pago || procesandoVenta" 
        class="btn-registrar-premium"
        :class="{'btn-processing': procesandoVenta}"
    >
      <span v-if="!procesandoVenta" class="btn-content">
        <span class="btn-icon">💳</span>
        Registrar Venta - ${{ total.toFixed(2) }}
      </span>
      <span v-else class="btn-content">
        <span class="btn-spinner">⏳</span>
        Procesando...
      </span>
    </button>
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
            debug: true
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
        },
        metodoPagoSeleccionado() {
            if (!this.datosVenta.medio_pago) return null;
            return this.metodosPago.find(mp => mp.id === this.datosVenta.medio_pago);
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
                return `Agregar (+${cantidadEnCarrito})`;
            }
            
            return 'Agregar';
        },

        validarCantidad(producto) {
          const cantidad = this.cantidades[producto.id] || 0;
          const stockDisponible = this.stockDisponibleReal(producto);
          
          if (cantidad > stockDisponible) {
            this.cantidades[producto.id] = stockDisponible;
            this.$nextTick(() => {
              Swal.fire({
                icon: 'warning',
                title: 'Cantidad Ajustada',
                text: `Stock disponible: ${stockDisponible} unidades`,
                timer: 3000,
                showConfirmButton: false
              })
            });
          }
        },

        async cargarMetodosPago() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/metodos-pago/`); 
                this.metodosPago = Array.isArray(res.data) ? res.data : [];
                
                if (this.metodosPago.length > 0) {
                    const efectivo = this.metodosPago.find(mp => mp.nombre === 'Efectivo') || this.metodosPago[0];
                    this.datosVenta.medio_pago = efectivo.id;
                }
            } catch (err) { 
                console.error("❌ Error al cargar métodos de pago:", err);
                this.metodosPago = [];
            }
        },
        
        // En RegistrarVenta.vue -> methods:

        async cargarProductos() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/productos/`);
                const datosCrudos = Array.isArray(res.data) ? res.data : [];
                
                // 🚨 LA CORRECCIÓN MÁGICA ESTÁ ACÁ ABAJO:
                // Mapeamos 'stock_actual' (Backend) a 'stock' (Frontend)
                this.productos = datosCrudos.map(prod => ({
                    ...prod,
                    stock: prod.stock_actual // <--- ESTO SOLUCIONA EL PROBLEMA
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
            }
            
            this.actualizarStockVisual(producto.id, -cantidad);
            this.cantidades[producto.id] = 1;

            // Mensaje de éxito al agregar producto
            Swal.fire({
                icon: 'success',
                title: 'Producto Agregado',
                text: `${producto.nombre} agregado al carrito`,
                timer: 2000,
                showConfirmButton: false
            });
        },
        
        validarStockDisponible(producto, cantidad) {
          if (cantidad < 1) {
            Swal.fire({
              icon: 'error',
              title: 'Error',
              text: 'La cantidad debe ser al menos 1',
              confirmButtonText: 'Entendido'
            })
            return false;
          }
          
          const stockDisponible = this.stockDisponibleReal(producto);
          
          if (cantidad > stockDisponible) {
            Swal.fire({
              icon: 'error',
              title: 'Stock Insuficiente',
              text: `Solo quedan ${stockDisponible} unidades disponibles`,
              confirmButtonText: 'Entendido'
            })
            this.cantidades[producto.id] = stockDisponible;
            return false;
          }
          
          if (producto.stock === 0) {
            Swal.fire({
              icon: 'error',
              title: 'Sin Stock',
              text: 'Este producto no tiene stock disponible',
              confirmButtonText: 'Entendido'
            })
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

                // Mensaje al quitar producto
                Swal.fire({
                    icon: 'info',
                    title: 'Producto Removido',
                    text: `${productoNombre} removido del carrito`,
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        },
        
        async registrarVenta() {
            console.log("🔄 Iniciando registro de venta...");
            
            if (!this.validarVenta()) return;

            this.procesandoVenta = true;

            // Mostrar loading durante el registro
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
            Swal.fire({
              icon: 'warning',
              title: 'Carrito Vacío',
              text: 'Debe agregar productos al carrito',
              confirmButtonText: 'Entendido'
            })
            return false;
          }
          if (!this.datosVenta.medio_pago) {
            Swal.fire({
              icon: 'warning',
              title: 'Método de Pago',
              text: 'Debe seleccionar un medio de pago',
              confirmButtonText: 'Entendido'
            })
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
            
            // 1. Guardamos el total REAL que viene del backend antes de limpiar nada
            const totalConfirmado = parseFloat(ventaData.total); // <--- CLAVE

            // Cerrar loading
            Swal.close();
            
            // 2. Limpiamos el formulario (esto pone this.total en 0)
            this.limpiarFormulario();
            await this.cargarProductos();
            
            // Emitir para actualizar listado
            this.$emit('venta-registrada', ventaData);
            
            // 3. Mostrar Modal usando 'totalConfirmado' en vez de 'this.total'
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
            
            // ✅ EMITIR PARA CERRAR REGISTRO Y MOSTRAR LISTADO
            this.$emit('venta-completada');
        },

        continuarSinAbrir() {
            console.log("➡️ Continuando sin comprobante...");
            
            // ✅ EMITIR PARA CERRAR REGISTRO Y MOSTRAR LISTADO
            this.$emit('venta-completada');
        },

        limpiarFormulario() {
            console.log("🧹 Limpiando formulario...");
            this.carrito = [];
            this.datosVenta.medio_pago = null;
            this.total = 0;
            this.filtroNombre = '';
            this.filtroCategoria = '';
        },

        async manejarErrorVenta(err) {
            console.error("❌ Error completo:", err);
            
            // Cerrar loading
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
/* Estilos base mejorados */
.pedido-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 25px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.header-section h2 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: #007bff;
}

.btn-back {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-back:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Cards modernas */
.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #a6a6a6;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #007bff;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15);
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
  background: linear-gradient(135deg, #007bff, #0056b3);
  padding: 10px;
  border-radius: 10px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
}

.badge-count {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 600;
}

/* Inputs y selects */
.input-group {
  margin-bottom: 20px;
}

.select-modern, .input-modern {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
}

.select-modern:focus, .input-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

/* Info del proveedor */
.proveedor-info {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #dee2e6;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-value {
  color: #1a1a1a;
  font-weight: 500;
  padding-left: 22px;
}

/* Filtros */
.filtros-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1a1a1a;
  margin-bottom: 15px;
}

/* Categorías */
.categorias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.categoria-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.categoria-item:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.categoria-item.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.categoria-checkbox {
  flex-shrink: 0;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
}

.checkmark.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.categoria-info {
  flex: 1;
}

.categoria-nombre {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 4px;
}

.productos-count {
  font-size: 0.8em;
  color: #6c757d;
  background: #f8f9fa;
  padding: 3px 8px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.filtro-actions {
  display: flex;
  gap: 10px;
}

.btn-outline {
  background: transparent;
  border: 2px solid #007bff;
  color: #007bff;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-outline:hover {
  background: #007bff;
  color: white;
  transform: translateY(-1px);
}

/* Búsqueda */
.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.search-box {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-box .input-modern {
  padding-left: 40px;
}

.stats-badge {
  background: linear-gradient(135deg, #6c757d, #5a6268);
  color: white;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 600;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Productos */
.productos-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.producto-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.producto-item:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.producto-item.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.producto-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
  flex-shrink: 0;
}

.producto-checkbox.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.producto-info {
  flex: 1;
}

.producto-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.producto-nombre {
  font-weight: 600;
  color: #1a1a1a;
  flex: 1;
  margin-right: 10px;
}

.producto-precio {
  color: #28a745;
  font-weight: 700;
  font-size: 1.1em;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 2px;
}

.producto-details {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.producto-codigo, .producto-stock, .producto-categoria {
  font-size: 0.85em;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.producto-codigo {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #e9ecef;
}

.producto-categoria {
  background: #e7f3ff;
  color: #0056b3;
  border: 1px solid #b3d9ff;
}

.stock-critico {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.stock-bajo {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.stock-medio {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.stock-alto {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.agregar-section {
  margin-top: 20px;
  text-align: center;
}

.btn-agregar-masivo {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1em;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-agregar-masivo:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
}

.btn-agregar-masivo.btn-disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
}

/* Detalles del pedido */
.detalles-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detalle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.detalle-item:hover {
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.detalle-info {
  flex: 1;
}

.detalle-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.detalle-nombre {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 1.1em;
}

.detalle-categoria {
  background: #e7f3ff;
  color: #0056b3;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8em;
  font-weight: 500;
  border: 1px solid #b3d9ff;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.detalle-details {
  display: flex;
  gap: 15px;
  align-items: center;
}

.detalle-codigo, .detalle-precio {
  font-size: 0.9em;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 4px;
}

.detalle-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: center;
}

.control-group label {
  font-size: 0.8em;
  color: #6c757d;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-cantidad, .input-precio {
  width: 80px;
  text-align: center;
  padding: 8px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  background: #fff;
  font-weight: 600;
  color: #1a1a1a;
}

.input-cantidad:focus, .input-precio:focus {
  border-color: #007bff;
  outline: none;
}

.input-cantidad.input-disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
  opacity: 0.6;
}

.detalle-subtotal {
  text-align: center;
  min-width: 100px;
}

.subtotal-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 0.8em;
  color: #6c757d;
  margin-bottom: 4px;
}

.subtotal-value {
  font-weight: 700;
  color: #28a745;
  font-size: 1.1em;
}

.btn-eliminar {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-eliminar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

/* Resumen */
.resumen-pedido {
  margin-top: 25px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  border: 2px solid #e9ecef;
}

.resumen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  color: #1a1a1a;
  font-size: 1em;
}

.resumen-item span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.resumen-item.total {
  border-top: 2px solid #dee2e6;
  margin-top: 10px;
  padding-top: 15px;
  font-size: 1.2em;
  font-weight: 700;
}

/* Textarea */
.textarea-modern {
  width: 100%;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
  resize: vertical;
  min-height: 80px;
}

.textarea-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.textarea-footer small {
  color: #6c757d;
  font-size: 0.8em;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Estados vacíos */
.no-resultados, .seleccion-categoria {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.no-resultados-icon, .seleccion-icon {
  margin-bottom: 15px;
  opacity: 0.5;
  color: #6c757d;
}

.no-resultados p, .seleccion-categoria p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: #1a1a1a;
}

.no-resultados small, .seleccion-categoria small {
  font-size: 0.9em;
  color: #6c757d;
}

/* Botón final premium */
.btn-registrar-premium {
  width: 100%;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  font-size: 1.1em;
  padding: 18px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 25px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-registrar-premium:hover:not(:disabled):not(.btn-processing) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, #0056b3, #004085);
}

.btn-registrar-premium:disabled,
.btn-registrar-premium.btn-processing {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .pedido-container {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .search-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .detalle-item {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .detalle-controls {
    justify-content: space-between;
    flex-wrap: wrap;
  }
  
  .categorias-grid {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .producto-item {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .producto-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>