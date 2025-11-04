<template>
  <div class="venta-container">
    <h2>Registrar Venta de Productos</h2>

    <!-- Filtros de productos -->
    <div class="input-group">
      <input v-model="filtroNombre" placeholder="Buscar producto por nombre" class="input-modern"/>
      <select v-model="filtroCategoria" class="select-modern">
        <option value="">Todas las categorías</option>
        <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
      </select>
    </div>

    <!-- Lista de productos -->
    <div v-if="productos.length" class="productos-grid">
      <div v-for="producto in productosFiltrados" :key="producto.id" class="producto-item" :class="{'sin-stock': producto.stock === 0}">
        <div class="producto-info">
          <span class="producto-nombre">{{ producto.nombre }}</span>
          <span class="producto-stock" :class="{
            'stock-bajo': producto.stock > 0 && producto.stock <= 5, 
            'sin-stock-text': producto.stock === 0
          }">
            (Stock: {{ producto.stock }})
            <span v-if="producto.stock === 0" class="sin-stock-badge">SIN STOCK</span>
            <span v-else-if="producto.stock <= 5" class="stock-bajo-badge">STOCK BAJO</span>
            
            <span v-if="productoEnCarrito(producto.id)" class="stock-carrito-info">
              (En carrito: {{ cantidadEnCarrito(producto.id) }})
            </span>
          </span>
        </div>
        <div class="producto-actions">
          <span class="producto-precio">${{ producto.precio }}</span>
          <input 
            type="number" 
            min="1" 
            :max="stockDisponibleReal(producto)" 
            v-model.number="cantidades[producto.id]" 
            :disabled="producto.stock === 0"
            class="input-cantidad"
            :class="{'input-disabled': producto.stock === 0}"
            @change="validarCantidad(producto)"
          />
          <button 
            @click="agregarAlCarrito(producto)" 
            :disabled="!puedeAgregarAlCarrito(producto)"
            class="btn-agregar"
            :class="{'btn-disabled': !puedeAgregarAlCarrito(producto)}"
          >
            {{ obtenerTextoBoton(producto) }}
          </button>
        </div>
      </div>
    </div>
    <div v-else class="no-productos">No hay productos disponibles</div>

    <!-- Carrito Mejorado -->
    <div class="resumen-container">
      <div class="carrito-header">
        <div class="carrito-title">
          <span class="carrito-icon">🛒</span>
          <h3>Carrito de Compras</h3>
        </div>
        <div class="carrito-badge" v-if="carrito.length > 0">
          {{ carrito.length }} {{ carrito.length === 1 ? 'producto' : 'productos' }}
        </div>
      </div>
      
      <div v-if="carrito.length" class="carrito-list">
        <div v-for="item in carrito" :key="item.producto.id" class="carrito-item">
          <div class="carrito-producto-info">
            <span class="carrito-producto-nombre">{{ item.producto.nombre }}</span>
            <div class="carrito-detalles">
              <span class="carrito-precio-unitario">${{ item.producto.precio }} c/u</span>
              <span class="carrito-cantidad">x {{ item.cantidad }}</span>
            </div>
          </div>
          <div class="carrito-actions">
            <span class="carrito-subtotal">${{ item.subtotal }}</span>
            <button @click="quitarDelCarrito(item.producto.id)" class="btn-quitar" title="Quitar del carrito">
              <span class="trash-icon">🗑️</span>
            </button>
          </div>
        </div>
        
        <!-- Resumen del carrito -->
        <div class="carrito-resumen">
          <div class="resumen-item">
            <span>Subtotal:</span>
            <span>${{ total.toFixed(2) }}</span>
          </div>
          <div class="resumen-total">
            <strong>Total:</strong>
            <strong>${{ total.toFixed(2) }}</strong>
          </div>
        </div>
      </div>
      <div v-else class="carrito-vacio">
        <div class="carrito-vacio-icon">🛒</div>
        <p>Tu carrito está vacío</p>
        <small>Agrega productos desde la lista arriba</small>
      </div>
    </div>

    <!-- Selector de pago -->
    <div class="pago-selector">
      <label for="medio_pago" class="label-modern">Medio de Pago</label>
      <select id="medio_pago" v-model.number="datosVenta.medio_pago" class="select-modern">
        <option :value="null" disabled>Seleccione método de pago</option>
        <option v-for="mp in metodosPago" :key="mp.id" :value="mp.id">
          {{ mp.nombre }}
        </option>
      </select>
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
        
        async cargarProductos() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/productos/`); 
                this.productos = Array.isArray(res.data) ? res.data : [];
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
                        precio: parseFloat(producto.precio)
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

                const response = await axios.post(`${API_BASE_URL}/usuarios/api/ventas/`, payload);
                
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
            
            // Cerrar loading
            Swal.close();
            
            this.limpiarFormulario();
            await this.cargarProductos();
            
            // ✅ EMITIR PARA ACTUALIZAR LISTADO
            this.$emit('venta-registrada', ventaData);
            
            // ✅ MOSTRAR MODAL ELEGANTE CON SWEETALERT2
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
                                <span style="color: #28a745; font-weight: bold;">$${this.total.toFixed(2)}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <strong>Método de Pago:</strong>
                                <span>${this.metodoPagoSeleccionado?.nombre || ''}</span>
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
                // Abrir comprobante PDF
                this.abrirComprobante(ventaData.id);
            } else {
                // Continuar sin abrir comprobante
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
.venta-container { 
  max-width: 800px; 
  margin: 0 auto; 
  padding: 25px; 
  background: #fff; 
  border-radius: 16px; 
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #000000; 
}

.input-group {
    display: flex;
    gap: 12px;
    margin-bottom: 25px;
}

.input-modern, .select-modern { 
  flex: 1;
  padding: 12px 16px; 
  border-radius: 10px; 
  border: 2px solid #e1e5e9; 
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #000000; /* Texto negro */
}

.input-modern:focus, .select-modern:focus {
    border-color: #007bff;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
    outline: none;
    color: #000000; /* Texto negro */
}

/* Productos */
.productos-grid {
    display: grid;
    gap: 12px;
    margin-bottom: 25px;
}

.producto-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-radius: 12px;
    border: 2px solid #f1f3f4;
    background: #fff;
    transition: all 0.3s ease;
}

.producto-item:hover {
    border-color: #007bff;
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.producto-item.sin-stock {
    background-color: #f8f9fa;
    opacity: 0.7;
    border-color: #dee2e6;
}

.producto-info {
    flex-grow: 1;
}

.producto-nombre {
    font-weight: 600;
    display: block;
    color: #000000; /* Texto negro */
    font-size: 15px;
}

.producto-stock {
    font-size: 0.8em;
    margin-left: 5px;
    color: #000000; /* Texto negro */
}

.stock-bajo {
    color: #e67e22;
    font-weight: 600;
}

.sin-stock-text {
    color: #e74c3c;
    font-weight: 600;
}

.stock-carrito-info {
    font-size: 0.75em;
    color: #007bff;
    font-weight: 600;
    margin-left: 8px;
    background: #e7f3ff;
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid #b3d9ff;
}

.stock-bajo-badge, .sin-stock-badge {
    font-size: 0.7em;
    padding: 3px 8px;
    border-radius: 6px;
    margin-left: 6px;
    font-weight: 600;
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
    gap: 12px;
}

.producto-precio {
    color: #007bff;
    font-weight: 700;
    min-width: 70px;
    font-size: 15px;
}

.input-cantidad {
    width: 65px;
    text-align: center;
    padding: 8px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    background: #f8f9fa;
    font-weight: 600;
    color: #000000; /* Texto negro */
}

.input-cantidad.input-disabled {
    background-color: #e9ecef;
    cursor: not-allowed;
    opacity: 0.6;
}

.btn-agregar { 
    background: linear-gradient(135deg, #28a745, #20c997); 
    color: white; 
    border: none;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    white-space: nowrap;
    min-width: 90px;
    font-weight: 600;
    font-size: 13px;
}

.btn-agregar:hover:not(.btn-disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.btn-agregar.btn-disabled {
    background: #6c757d;
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
}

/* Carrito Mejorado */
.resumen-container {
    padding: 20px;
    border: 2px solid #e9ecef;
    border-radius: 16px;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.carrito-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #dee2e6;
}

.carrito-title {
    display: flex;
    align-items: center;
    gap: 12px;
}

.carrito-icon {
    font-size: 1.8em;
    background: linear-gradient(135deg, #007bff, #0056b3);
    padding: 10px;
    border-radius: 12px;
    color: white;
}

.carrito-title h3 {
    margin: 0;
    color: #000000; /* Texto negro */
    font-size: 1.4em;
    font-weight: 700;
}

.carrito-badge {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: 600;
}

.carrito-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.carrito-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: white;
    border-radius: 12px;
    border: 1px solid #e9ecef;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.carrito-item:hover {
    border-color: #007bff;
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.1);
    transform: translateY(-2px);
}

.carrito-producto-info {
    flex-grow: 1;
}

.carrito-producto-nombre {
    font-weight: 600;
    display: block;
    color: #000000; /* Texto negro */
    font-size: 15px;
    margin-bottom: 4px;
}

.carrito-detalles {
    display: flex;
    gap: 15px;
    align-items: center;
    font-size: 0.9em;
}

.carrito-precio-unitario {
    color: #6c757d;
}

.carrito-cantidad {
    color: #007bff;
    font-weight: 600;
    background: #e7f3ff;
    padding: 2px 8px;
    border-radius: 6px;
    border: 1px solid #b3d9ff;
}

.carrito-actions {
    display: flex;
    align-items: center;
    gap: 15px;
}

.carrito-subtotal {
    font-weight: 700;
    color: #28a745;
    font-size: 16px;
    min-width: 80px;
    text-align: right;
}

.btn-quitar { 
    background: linear-gradient(135deg, #dc3545, #c82333);
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-quitar:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
    background: linear-gradient(135deg, #c82333, #a71e2a);
}

.trash-icon {
    font-size: 1.1em;
}

.carrito-resumen {
    margin-top: 20px;
    padding: 20px;
    background: white;
    border-radius: 12px;
    border: 2px solid #e9ecef;
}

.resumen-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    color: #000000; /* Texto negro */
    font-size: 1em;
}

.resumen-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-top: 2px solid #e9ecef;
    margin-top: 8px;
    color: #000000; /* Texto negro */
    font-size: 1.2em;
}

.carrito-vacio {
    text-align: center;
    padding: 40px 20px;
    color: #6c757d;
}

.carrito-vacio-icon {
    font-size: 3em;
    margin-bottom: 15px;
    opacity: 0.5;
}

.carrito-vacio p {
    margin: 0 0 8px 0;
    font-size: 1.1em;
    color: #000000; /* Texto negro */
}

.carrito-vacio small {
    font-size: 0.9em;
    color: #6c757d;
}

.no-productos {
    text-align: center;
    color: #6c757d;
    font-style: italic;
    padding: 25px;
    font-size: 16px;
}

/* Información de pago */
.pago-selector {
    padding: 20px 0;
    border-top: 2px solid #f1f3f4;
    border-bottom: 2px solid #f1f3f4;
}

.label-modern {
    font-weight: 600;
    display: block;
    margin-bottom: 8px;
    color: #000000; /* Texto negro */
    font-size: 15px;
}

/* Botón final mejorado */
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

.btn-icon {
    font-size: 1.2em;
}

.btn-spinner {
    font-size: 1.2em;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
    .carrito-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
    
    .carrito-actions {
        width: 100%;
        justify-content: space-between;
    }
    
    .carrito-detalles {
        flex-direction: column;
        gap: 5px;
        align-items: flex-start;
    }
}
</style>