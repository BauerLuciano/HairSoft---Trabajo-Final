<template>
  <!-- FONDO DEGRADADO Y TARJETA BLANCA -->
  <div class="page-background">
    <div class="main-card-container">
      <div class="venta-container">
        <div class="header-section">
          <h2>
            <span class="header-icon">💰</span>
            Registrar Venta de Productos
          </h2>
          <button @click="volverAlListado" class="btn-back">
            <span>←</span>
            Volver
          </button>
        </div>

        <!-- Filtros de productos -->
        <div class="card-modern">
          <div class="card-header">
            <div class="card-icon">🔍</div>
            <h3>Filtros de Búsqueda</h3>
          </div>
          <div class="input-group">
            <div class="row-search">
              <div class="search-wrapper">
                <span class="search-icon">🔍</span>
                <input
                  v-model="filtroNombre"
                  placeholder="Buscar producto por nombre"
                  class="input-modern"
                />
              </div>
              <select v-model="filtroCategoria" class="select-modern">
                <option value="">Todas las categorías</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
              </select>
            </div>
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
            <div 
              v-for="producto in productosFiltrados" 
              :key="producto.id" 
              class="card-producto"
              :class="{
                'producto-sin-stock': producto.stock === 0,
                'producto-selected': productoEnCarrito(producto.id)
              }"
            >
              <div class="producto-check" v-if="productoEnCarrito(producto.id)">
                ✓
              </div>
              <div class="producto-content">
                <div class="producto-header">
                  <span class="producto-nombre">{{ producto.nombre }}</span>
                  <span class="producto-precio">${{ producto.precio }}</span>
                </div>
                
                <div class="producto-details">
                  <div class="detail-chip">
                    <span>ID:</span>
                    <strong>{{ producto.id }}</strong>
                  </div>
                  <div class="detail-chip">
                    <span>Categoría:</span>
                    <strong>{{ obtenerNombreCategoria(producto.categoria_id) }}</strong>
                  </div>
                  <div class="detail-chip" :class="{
                    'stock-critico': producto.stock === 0,
                    'stock-bajo': producto.stock > 0 && producto.stock <= 5,
                    'stock-normal': producto.stock > 5
                  }">
                    <span>Stock:</span>
                    <strong>{{ producto.stock }}</strong>
                    <span v-if="producto.stock === 0" class="stock-badge">SIN STOCK</span>
                    <span v-else-if="producto.stock <= 5" class="stock-badge">BAJO</span>
                  </div>
                </div>

                <div class="producto-controls">
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
                      class="input-cantidad-small"
                      :class="{'input-disabled': producto.stock === 0}"
                      @change="validarCantidad(producto)"
                    />
                  </div>
                  <button 
                    @click="agregarAlCarrito(producto)" 
                    :disabled="!puedeAgregarAlCarrito(producto)"
                    class="btn-agregar-producto"
                    :class="{'btn-disabled': !puedeAgregarAlCarrito(producto)}"
                  >
                    {{ obtenerTextoBoton(producto) }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="no-resultados">
            <div class="no-resultados-icon">📦</div>
            <p>No hay productos disponibles</p>
            <small>Intenta ajustar los filtros de búsqueda</small>
          </div>
        </div>

        <!-- Carrito de Compras -->
        <div class="card-modern" v-if="carrito.length > 0">
          <div class="card-header">
            <div class="card-icon">🛒</div>
            <h3>Carrito de Compras</h3>
            <div class="badge-count">
              {{ carrito.length }} {{ carrito.length === 1 ? 'producto' : 'productos' }}
            </div>
          </div>
          
          <div class="detalles-carrito">
            <div v-for="item in carrito" :key="item.producto.id" class="item-carrito">
              <div class="item-info">
                <div class="item-header">
                  <span class="item-nombre">{{ item.producto.nombre }}</span>
                  <span class="item-categoria">
                    {{ obtenerNombreCategoria(item.producto.categoria_id) }}
                  </span>
                </div>
                <div class="item-details">
                  <div class="detail-small">
                    <span>ID:</span>
                    <strong>{{ item.producto.id }}</strong>
                  </div>
                  <div class="detail-small">
                    <span>Precio:</span>
                    <strong>${{ item.producto.precio }}</strong>
                  </div>
                  <div class="detail-small">
                    <span>Cantidad:</span>
                    <strong>{{ item.cantidad }}</strong>
                  </div>
                </div>
              </div>
              <div class="item-actions">
                <div class="item-subtotal">
                  <span>Subtotal:</span>
                  <strong>${{ item.subtotal }}</strong>
                </div>
                <button @click="quitarDelCarrito(item.producto.id)" class="btn-eliminar-item" title="Quitar del carrito">
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Información de Pago -->
        <div class="card-modern slide-in" v-if="carrito.length > 0">
          <div class="card-header">
            <div class="card-icon">💳</div>
            <h3>Información de Pago</h3>
          </div>
          
          <div class="resumen-venta">
            <div class="resumen-item total">
              <span>Total a Pagar:</span>
              <strong>${{ total.toFixed(2) }}</strong>
            </div>
          </div>

          <div class="pago-section">
            <div class="input-group">
              <label class="label-modern">Método de Pago</label>
              <select v-model.number="datosVenta.medio_pago" class="select-modern">
                <option :value="null" disabled>Seleccione método de pago</option>
                <option v-for="mp in metodosPago" :key="mp.id" :value="mp.id">
                  {{ mp.nombre }}
                </option>
              </select>
            </div>
          </div>

          <button 
            @click="registrarVenta" 
            :disabled="!datosVenta.medio_pago || procesandoVenta" 
            class="btn-confirmar-premium"
            :class="{'btn-processing': procesandoVenta}"
          >
            <span v-if="!procesandoVenta">
              <span class="btn-icon">💳</span>
              Registrar Venta - ${{ total.toFixed(2) }}
            </span>
            <span v-else>
              <span class="btn-spinner">⏳</span>
              Procesando...
            </span>
          </button>
        </div>

        <!-- Estado vacío del carrito -->
        <div class="card-modern" v-if="carrito.length === 0">
          <div class="no-resultados">
            <div class="no-resultados-icon">🛒</div>
            <p>Tu carrito está vacío</p>
            <small>Agrega productos desde la lista arriba</small>
          </div>
        </div>

        <!-- Mensajes de confirmación -->
        <transition name="fade">
          <div v-if="mensaje" class="toast-message" :class="mensajeTipo">
            <span v-if="mensajeTipo === 'success'">✅</span>
            <span v-else>❌</span>
            {{ mensaje }}
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
            
            return 'Agregar al Carrito';
        },

        validarCantidad(producto) {
          const cantidad = this.cantidades[producto.id] || 0;
          const stockDisponible = this.stockDisponibleReal(producto);
          
          if (cantidad > stockDisponible) {
            this.cantidades[producto.id] = stockDisponible;
            this.mostrarMensaje('Cantidad ajustada al stock disponible', 'info');
          }
        },

        async cargarMetodosPago() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/metodos-pago/`); 
                const todosMetodos = Array.isArray(res.data) ? res.data : [];
                
                // ✅ CORRECCIÓN: Filtrar y agrupar para mostrar SOLO 3 tipos básicos
                // Igual que en los turnos: EFECTIVO, TARJETA, TRANSFERENCIA
                
                // 1. Filtrar solo métodos activos
                const metodosActivos = todosMetodos.filter(mp => mp.activo !== false);
                
                // 2. Mapear a los 3 tipos básicos
                const metodosAgrupados = [];
                const tiposUsados = new Set(); // Para evitar duplicados
                
                metodosActivos.forEach(mp => {
                    let tipoMostrar = '';
                    let idMostrar = mp.id;
                    
                    // Determinar el tipo básico según el nombre
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
                    
                    // Solo agregar si encontramos un tipo válido y no está duplicado
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
                
                // ✅ Asegurar que tengamos al menos los 3 básicos
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
                
                // Ordenar: Efectivo, Tarjeta, Transferencia
                const orden = ['Efectivo', 'Tarjeta', 'Transferencia'];
                this.metodosPago = metodosAgrupados.sort((a, b) => 
                    orden.indexOf(a.nombre) - orden.indexOf(b.nombre)
                );
                
                // ✅ Establecer Efectivo como seleccionado por defecto
                if (this.metodosPago.length > 0) {
                    const efectivo = this.metodosPago.find(mp => mp.nombre === 'Efectivo') || this.metodosPago[0];
                    this.datosVenta.medio_pago = efectivo.id;
                }
                
                console.log('✅ Métodos de pago cargados (simplificados):', this.metodosPago);
                
            } catch (err) { 
                console.error("❌ Error al cargar métodos de pago:", err);
                
                // ✅ Fallback: Mostrar los 3 básicos aunque falle la API
                this.metodosPago = [
                    { id: 1, nombre: 'Efectivo', tipo_original: 'EFECTIVO', descripcion: 'Pago en efectivo', requiere_confirmacion: false },
                    { id: 2, nombre: 'Tarjeta', tipo_original: 'TARJETA', descripcion: 'Pago con tarjeta', requiere_confirmacion: true },
                    { id: 3, nombre: 'Transferencia', tipo_original: 'TRANSFERENCIA', descripcion: 'Transferencia bancaria o QR', requiere_confirmacion: true }
                ];
                
                this.datosVenta.medio_pago = 1; // Efectivo por defecto
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

            this.mostrarMensaje(`${producto.nombre} agregado al carrito`, 'success');
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
            this.filtroNombre = '';
            this.filtroCategoria = '';
            this.mostrarMensaje('Venta registrada exitosamente', 'success');
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
        },

        mostrarMensaje(texto, tipo = 'info') {
            this.mensaje = texto;
            this.mensajeTipo = tipo;
            
            setTimeout(() => {
                this.mensaje = '';
            }, 3000);
        },

        volverAlListado() {
            this.$emit('volver-al-listado');
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
   FONDO DE PÁGINA Y CONTENEDOR PRINCIPAL
   ============================================ */
.page-background {
  min-height: 100vh;
  padding: 0px 1px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.main-card-container {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 1500px;
  margin: 0 auto;
  padding: 20px;
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

/* ============================================
   HEADER SECTION
   ============================================ */
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

/* ============================================
   CARDS MODERNAS
   ============================================ */
.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #3b82f6;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
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
  font-size: 1.2em;
}

.card-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
  letter-spacing: -0.5px;
}

.badge-count {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 600;
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* ============================================
   INPUTS Y CONTROLES
   ============================================ */
.input-group {
  margin-bottom: 15px;
}

.row-search {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-wrapper {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 1.1em;
}

.input-modern, .select-modern {
  width: 100%;
  padding: 14px 16px;
  padding-left: 46px;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 15px;
  transition: all 0.3s ease;
  color: #1f2937;
}

.select-modern {
  padding-left: 16px;
}

.input-modern:focus, .select-modern:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.label-modern {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
  color: #1f2937;
  font-size: 1rem;
}

/* ============================================
   PRODUCTOS GRID
   ============================================ */
.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.card-producto {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
}

.card-producto:hover {
  border-color: #3b82f6;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
}

.producto-selected {
  border-color: #10b981;
  background: #f0fdf4;
}

.producto-sin-stock {
  opacity: 0.7;
  background: #f3f4f6;
}

.producto-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.producto-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.producto-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.producto-nombre {
  font-weight: 700;
  color: #1f2937;
  font-size: 1.1rem;
  flex: 1;
  margin-right: 10px;
}

.producto-precio {
  color: #059669;
  font-weight: 700;
  font-size: 1.2rem;
}

.producto-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-chip {
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.85em;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.detail-chip.stock-critico {
  background: #fee2e2;
  color: #dc2626;
}

.detail-chip.stock-bajo {
  background: #fef3c7;
  color: #d97706;
}

.detail-chip.stock-normal {
  background: #d1fae5;
  color: #059669;
}

.stock-badge {
  font-size: 0.8em;
  font-weight: 700;
  margin-left: 4px;
  padding: 2px 6px;
  border-radius: 4px;
}

.stock-critico .stock-badge {
  background: #dc2626;
  color: white;
}

.stock-bajo .stock-badge {
  background: #d97706;
  color: white;
}

.producto-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.control-group label {
  font-size: 0.85em;
  color: #6b7280;
  font-weight: 500;
}

.input-cantidad-small {
  width: 70px;
  text-align: center;
  padding: 8px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  font-weight: 600;
  color: #1f2937;
}

.input-cantidad-small:focus {
  border-color: #3b82f6;
  outline: none;
}

.input-cantidad-small.input-disabled {
  background: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-agregar-producto {
  flex: 1;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9em;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-agregar-producto:hover:not(.btn-disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-agregar-producto.btn-disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
}

/* ============================================
   CARRITO DE COMPRAS
   ============================================ */
.detalles-carrito {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-carrito {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.item-carrito:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.item-info {
  flex: 1;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.item-nombre {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.05em;
}

.item-categoria {
  background: #e7f3ff;
  color: #1d4ed8;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8em;
  font-weight: 500;
  border: 1px solid #b3d9ff;
}

.item-details {
  display: flex;
  gap: 12px;
  align-items: center;
}

.detail-small {
  font-size: 0.9em;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.item-subtotal {
  text-align: center;
  min-width: 100px;
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
  font-size: 1.1em;
}

.btn-eliminar-item {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  height: 44px;
}

.btn-eliminar-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

/* ============================================
   RESUMEN Y PAGO
   ============================================ */
.resumen-venta {
  margin: 20px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.resumen-item.total {
  font-size: 1.3em;
  font-weight: 700;
  border-top: 2px solid #e5e7eb;
  margin-top: 15px;
  padding-top: 15px;
  border-bottom: none;
}

.pago-section {
  margin: 25px 0;
}

/* ============================================
   BOTÓN FINAL PREMIUM
   ============================================ */
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-confirmar-premium:hover:not(.btn-processing):not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(5, 150, 105, 0.4);
  background: linear-gradient(135deg, #047857, #065f46);
}

.btn-confirmar-premium:disabled,
.btn-confirmar-premium.btn-processing {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  opacity: 0.7;
}

.btn-icon {
  font-size: 1.2em;
}

.btn-spinner {
  animation: spin 1s linear infinite;
  font-size: 1.2em;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ============================================
   ESTADOS VACÍOS
   ============================================ */
.no-resultados {
  text-align: center;
  padding: 50px 20px;
  color: #6b7280;
}

.no-resultados-icon {
  opacity: 0.4;
  margin-bottom: 15px;
  font-size: 3em;
  color: #9ca3af;
}

.no-resultados p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: #1f2937;
}

.no-resultados small {
  font-size: 0.9em;
  color: #6b7280;
}

/* ============================================
   TOAST MESSAGES
   ============================================ */
.toast-message {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 18px 24px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 9999;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  min-width: 300px;
  backdrop-filter: blur(10px);
}

.toast-message.success {
  background: rgba(16, 185, 129, 0.95);
  color: white;
  border-left: 4px solid #059669;
}

.toast-message.error {
  background: rgba(239, 68, 68, 0.95);
  color: white;
  border-left: 4px solid #dc2626;
}

.toast-message.warning {
  background: rgba(245, 158, 11, 0.95);
  color: white;
  border-left: 4px solid #d97706;
}

.toast-message.info {
  background: rgba(59, 130, 246, 0.95);
  color: white;
  border-left: 4px solid #1d4ed8;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* ============================================
   ANIMACIONES
   ============================================ */
.slide-in {
  animation: slideInRight 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .main-card-container {
    padding: 30px;
    margin: 20px;
  }
  
  .productos-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-background {
    padding: 20px 15px;
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
  
  .btn-back {
    width: 100%;
    justify-content: center;
  }
  
  .productos-grid {
    grid-template-columns: 1fr;
  }
  
  .row-search {
    flex-direction: column;
  }
  
  .item-carrito {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .item-actions {
    justify-content: space-between;
    width: 100%;
  }
  
  .toast-message {
    left: 15px;
    right: 15px;
    bottom: 15px;
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .page-background {
    padding: 15px 10px;
  }
  
  .main-card-container {
    padding: 20px;
    border-radius: 16px;
  }
  
  .card-modern {
    padding: 20px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-icon {
    width: 40px;
    height: 40px;
  }
  
  .producto-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn-agregar-producto {
    width: 100%;
  }
}
</style>