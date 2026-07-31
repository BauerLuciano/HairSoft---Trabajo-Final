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
                <div class="input-icon-wrapper">
                  <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                  </svg>
                  <input
                    v-model="filtroNombre"
                    placeholder="Buscar producto..."
                    class="input-search input-search-icon"
                    @input="filtrarProductos"
                  />
                </div>
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
                    <div class="qty-stepper">
                      <button 
                        @click="disminuirCantidad(producto)" 
                        class="qty-btn"
                        :disabled="(cantidades[producto.id] || 1) <= 1 || producto.stock === 0"
                      >−</button>
                      <span class="qty-value">{{ cantidades[producto.id] || 1 }}</span>
                      <button 
                        @click="aumentarCantidad(producto)" 
                        class="qty-btn"
                        :disabled="(cantidades[producto.id] || 1) >= stockDisponibleReal(producto) || producto.stock === 0"
                      >+</button>
                    </div>
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
                  <div class="item-left">
                    <h4>{{ item.producto.nombre }}</h4>
                    <div class="item-detalles">
                      <span class="item-cantidad">{{ item.cantidad }}</span>
                      <span class="item-sep">×</span>
                      <span class="item-precio-unitario">${{ parseFloat(item.producto.precio).toFixed(2) }}</span>
                    </div>
                  </div>
                  <div class="item-right">
                    <span class="item-subtotal">${{ parseFloat(item.subtotal).toFixed(2) }}</span>
                    <button @click="quitarDelCarrito(item.producto.id)" class="btn-quitar">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
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

            <div class="total-destacado">
              <span class="total-label">TOTAL A PAGAR</span>
              <span class="total-valor">${{ total.toFixed(2) }}</span>
            </div>

            <div class="section-divider"></div>

            <div class="form-group">
              <label>Método de Pago *</label>
              <div class="metodo-pago-opciones">
                <div 
                  v-for="mp in metodosPago" 
                  :key="mp.id"
                  class="metodo-pago-card"
                  :class="{ 'metodo-pago-selected': datosVenta.medio_pago === mp.id }"
                  @click="datosVenta.medio_pago = mp.id; mpSubOption = null; mpQrData = null; mpPagoEstado = null; detenerPollingPago(); datosVenta.codigo_transaccion = ''"
                >
                  <div class="mp-icon">
                    <svg v-if="esEfectivoMetodo(mp)" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M4 6h16v12H4V6Z"/>
                      <path d="M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/>
                    </svg>
                    <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="2" y="6" width="20" height="12" rx="2"/>
                      <path d="M2 10h20"/>
                    </svg>
                  </div>
                  <div class="mp-nombre">
                    <span v-if="esEfectivoMetodo(mp)">AR$ Efectivo</span>
                    <span v-else>Mercado Pago</span>
                  </div>
                  <div class="mp-radio">
                    <div class="radio-circle" :class="{ 'radio-active': datosVenta.medio_pago === mp.id }"></div>
                  </div>
                </div>
              </div>
            </div>

            <transition name="slide-fade">
              <div v-if="esMercadoPago" class="datos-extra-pago">
                <label class="mp-sub-label">Elegí cómo cobrar con Mercado Pago:</label>

              <div class="mp-options">
                <div class="mp-option-card" :class="{ 'mp-option-selected': mpSubOption === 'alias' }" @click="mpSubOption = 'alias'; datosVenta.codigo_transaccion = ''">
                  <div class="mp-option-content">
                    <div class="mp-option-icon">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="8.5" cy="7" r="4"></circle>
                        <polyline points="17 11 19 13 23 9"></polyline>
                      </svg>
                    </div>
                    <div class="mp-option-info">
                      <h4>Transferencia por alias</h4>
                      <p>Mostrale el alias al cliente para que te transfiera</p>
                      <div v-if="mp_alias" class="mp-alias-display">
                        <span class="mp-alias-label">Alias:</span>
                        <span class="mp-alias-value">{{ mp_alias }}</span>
                        <button @click.stop="copiarAlias" class="btn-copy-alias" title="Copiar alias">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                          </svg>
                        </button>
                      </div>

                      <div v-if="mpSubOption === 'alias'" class="mp-id-opcional">
                        <label>ID de transacción <span class="opcional-tag">opcional</span></label>
                        <input
                          type="text"
                          v-model="datosVenta.codigo_transaccion"
                          class="input-search"
                          placeholder="Ej: 145025893768"
                          maxlength="14"
                          @input="datosVenta.codigo_transaccion = datosVenta.codigo_transaccion.replace(/\D/g, '')"
                        />
                        <small>Solo números, 14 dígitos — si el cliente te pasa el comprobante</small>
                      </div>
                    </div>
                  </div>
                  <div class="mp-option-radio">
                    <div class="radio-circle" :class="{ 'radio-active': mpSubOption === 'alias' }"></div>
                  </div>
                </div>

                <div class="mp-option-card" :class="{ 'mp-option-selected': mpSubOption === 'qr' }" @click="mpSubOption = 'qr'; datosVenta.codigo_transaccion = ''">
                  <div class="mp-option-content">
                    <div class="mp-option-icon">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="7" height="7"></rect>
                        <rect x="14" y="3" width="7" height="7"></rect>
                        <rect x="14" y="14" width="7" height="7"></rect>
                        <rect x="3" y="14" width="7" height="7"></rect>
                      </svg>
                    </div>
                    <div class="mp-option-info">
                      <h4>Código QR</h4>
                      <p>Generá un QR para que el cliente escanee con su celular</p>
                      <div v-if="mpSubOption === 'qr'" class="mp-qr-section">
                        <button @click.stop="generarQR" class="btn-generar-qr" :disabled="generandoQR">
                          <template v-if="!generandoQR">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                              <line x1="12" y1="8" x2="12" y2="16"></line>
                              <line x1="8" y1="12" x2="16" y2="12"></line>
                            </svg>
                            Generar QR
                          </template>
                          <template v-else>
                            <div class="spinner-sm"></div>
                            Generando...
                          </template>
                        </button>
                        <div v-if="mpQrData" class="qr-display">
                          <qrcode-vue :value="mpQrData.init_point" :size="200" level="H" />
                          <div v-if="mpPagoEstado === 'confirmed'" class="qr-pago-confirmado">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                              <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                            <span>¡Pago confirmado!</span>
                          </div>
                          <div v-else-if="mpPagoEstado === 'pending'" class="qr-pago-pendiente">
                            <div class="spinner-sm spinner-green"></div>
                            <span>Esperando pago...</span>
                            <button @click.stop="confirmarPagoManual" class="btn-confirmar-manual">Confirmar manualmente</button>
                          </div>
                          <p v-else class="qr-hint">Escaneá con Mercado Pago</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="mp-option-radio">
                    <div class="radio-circle" :class="{ 'radio-active': mpSubOption === 'qr' }"></div>
                  </div>
                </div>
              </div>
            </div>
            </transition>

            <transition name="slide-fade">
            <div v-if="esEfectivo" class="vuelto-section">
              <div class="form-group">
                <label>Monto recibido</label>
                <input
                  ref="montoInput"
                  type="number"
                  v-model.number="montoRecibido"
                  class="input-search input-monto-recibido"
                  placeholder="$0.00"
                  min="0"
                  step="0.01"
                  @keydown.enter="confirmarSiAlcanza"
                />
              </div>
              <div class="montos-rapidos" v-if="!montoRecibido || montoRecibido < total">
                <button
                  v-for="monto in montosRapidos"
                  :key="monto"
                  class="btn-monto-rapido"
                  @click="montoRecibido = monto"
                >
                  ${{ monto.toLocaleString() }}
                </button>
                <button class="btn-monto-rapido btn-monto-exacto" @click="montoRecibido = total">
                  Exacto
                </button>
              </div>
              <div v-if="montoRecibido && montoRecibido >= total" class="vuelto-display">
                <span class="vuelto-label">Vuelto</span>
                <span class="vuelto-valor">${{ vuelto.toFixed(2) }}</span>
              </div>
              <div v-else-if="montoRecibido && montoRecibido < total" class="vuelto-faltante">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <span>Faltan ${{ (total - montoRecibido).toFixed(2) }}</span>
              </div>
            </div>
            </transition>

            <div class="section-divider"></div>

            <button 
              @click="registrarVenta" 
              :disabled="!formularioValido || procesandoVenta || carrito.length === 0" 
              class="btn-confirmar"
              :class="{ 'btn-procesando': procesandoVenta }"
            >
              <template v-if="!procesandoVenta">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
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
import AsignarEnvio from '@/components/AsignarEnvio.vue';
import { envioService } from '@/services/envioService';
import QrcodeVue from 'qrcode.vue'

const API_BASE_URL = 'http://127.0.0.1:8000';

export default {
    name: 'RegistrarVenta',
    
    components: { AsignarEnvio, QrcodeVue },
    
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
            envioData: null,
            mp_alias: '',
            mpSubOption: null,
            mpQrData: null,
            generandoQR: false,
            mpPagoInterval: null,
            mpPagoEstado: null,
            mensaje: '',
            mensajeTipo: 'success',
            montoRecibido: null
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
            const subtotal = this.carrito.reduce((acc, item) => acc + item.subtotal, 0)
            return this.envioData ? subtotal + this.envioData.costo_envio : subtotal
        },
        vuelto() {
            if (!this.esEfectivo || !this.montoRecibido) return 0;
            return Math.max(0, this.montoRecibido - this.total);
        },
        montosRapidos() {
            const t = this.total;
            const montos = [5000, 10000, 20000, 50000];
            return montos.filter(m => m > t);
        },
        
        // 🔥 LOGICA MÉTODOS DE PAGO
        metodoPagoSeleccionado() {
            if (!this.datosVenta.medio_pago) return null;
            return this.metodosPago.find(mp => mp.id === this.datosVenta.medio_pago);
        },
        esMercadoPago() {
            if (!this.metodoPagoSeleccionado) return false;
            const tipo = (this.metodoPagoSeleccionado.tipo || '').toUpperCase();
            const nombre = (this.metodoPagoSeleccionado.nombre || '').toUpperCase();
            return tipo === 'MERCADOPAGO' || tipo === 'MERCADO_PAGO' || nombre.includes('MERCADO');
        },
        esTransferencia() {
            if (!this.metodoPagoSeleccionado) return false;
            if (this.esMercadoPago) return false;

            const tipo = (this.metodoPagoSeleccionado.tipo || '').toUpperCase();
            const nombre = (this.metodoPagoSeleccionado.nombre || '').toUpperCase();
            return tipo === 'TRANSFERENCIA' || nombre.includes('TRANSF');
        },
        esEfectivo() {
            if (!this.metodoPagoSeleccionado) return false;
            const tipo = (this.metodoPagoSeleccionado.tipo || '').toUpperCase();
            const nombre = (this.metodoPagoSeleccionado.nombre || '').toUpperCase();
            return tipo === 'EFECTIVO' || nombre.includes('EFECTIVO');
        },
        
        formularioValido() {
            if (this.carrito.length === 0) return false;
            if (!this.datosVenta.medio_pago) return false;
            
            if (this.esTransferencia && !this.datosVenta.entidad_pago) {
                return false;
            }

            if (this.esTransferencia && !this.datosVenta.codigo_transaccion) {
                return false;
            }

            if (this.esMercadoPago && this.mpSubOption === 'qr' && this.mpPagoEstado !== 'confirmed') {
                return false;
            }

            if (this.esEfectivo && (!this.montoRecibido || this.montoRecibido < this.total)) {
                return false;
            }

            return true;
        }
    },
    
    watch: {
        'datosVenta.medio_pago'(newVal) {
            this.datosVenta.entidad_pago = '';
            this.datosVenta.codigo_transaccion = '';
            this.mpSubOption = null;
            this.mpQrData = null;
            this.mpPagoEstado = null;
            this.detenerPollingPago();
        }
    },
    
    methods: {
        async verificarCajaAbierta() {
            try {
                const res = await axios.get(`${API_BASE_URL}/api/estado-caja/`);
                
                if (!res.data.abierta) {
                    this.bloquearPantallaYRedirigirACaja();
                }
            } catch (err) {
                console.error("Error al verificar estado de caja:", err);
                this.bloquearPantallaYRedirigirACaja();
            }
        },

        bloquearPantallaYRedirigirACaja() {
            Swal.fire({
                icon: 'warning',
                title: '¡Caja Cerrada!',
                html: `
                    <p style="color: #6c757d; margin-bottom: 20px;">
                        No podés registrar ventas porque <strong>no hay ninguna caja abierta</strong> en este momento.
                    </p>
                    <p style="color: #6c757d;">
                        Por favor, realizá la apertura de caja diaria primero.
                    </p>
                `,
                background: '#0f172a',
                color: '#f8fafc',
                confirmButtonText: 'Ir a Caja Diaria',
                confirmButtonColor: '#3b82f6',
                allowOutsideClick: false, 
                allowEscapeKey: false,    
                showCancelButton: false   
            }).then((result) => {
                if (result.isConfirmed) {
                    this.$router.push('/caja'); 
                }
            });
        },

        navegarAListado() {
            if (this.$route.path === '/ventas') {
                window.location.reload();
                return;
            }
            this.$router.push('/ventas').catch(err => {
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
                cancelButtonText: '➡️ Continuar ',
                confirmButtonColor: '#3b82f6',
                cancelButtonColor: '#6c757d',
                reverseButtons: true,
                backdrop: true,
                allowOutsideClick: false
            });

            if (result.isConfirmed) {
                await this.abrirComprobante(ventaData.id);
                setTimeout(() => {
                    this.navegarAListado();
                }, 1500);
            } else {
                this.navegarAListado();
            }
        },

        async abrirComprobante(ventaId) {
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/usuarios/api/ventas/${ventaId}/comprobante-pdf/`, 
                    { responseType: 'blob' }
                );
                
                const file = new Blob([response.data], { type: 'application/pdf' });
                const fileURL = URL.createObjectURL(file);
                
                window.open(fileURL, '_blank');
            } catch (error) {
                console.error("Error al descargar el PDF:", error);
                this.mostrarMensaje('No se pudo generar el comprobante (Error de Permisos o Red)', 'error');
            }
        },

        obtenerNombreCategoria(categoriaId) {
            const categoria = this.categorias.find(c => c.id === categoriaId);
            return categoria ? categoria.nombre : 'Sin categoría';
        },

        esEfectivoMetodo(mp) {
            const tipo = (mp.tipo || '').toUpperCase();
            const nombre = (mp.nombre || '').toUpperCase();
            return tipo === 'EFECTIVO' || nombre.includes('EFECTIVO');
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
        
        aumentarCantidad(producto) {
            const actual = this.cantidades[producto.id] || 1;
            const maxAgregar = this.stockDisponibleReal(producto);
            if (actual < maxAgregar) {
                this.cantidades[producto.id] = actual + 1;
            }
        },
        disminuirCantidad(producto) {
            const actual = this.cantidades[producto.id] || 1;
            if (actual > 1) {
                this.cantidades[producto.id] = actual - 1;
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
                if (Array.isArray(res.data)) {
                    this.metodosPago = res.data.filter(mp => {
                        if (mp.activo === false) return false; 
                        
                        const tipoStr = (mp.tipo || '').toUpperCase();
                        const nombreStr = (mp.nombre || '').toUpperCase();
                        
                        const esEfectivo = tipoStr.includes('EFECTIVO') || nombreStr.includes('EFECTIVO');
                        const esMercadoPago = tipoStr.includes('MERCADO') || nombreStr.includes('MERCADO');
                        
                        return esEfectivo || esMercadoPago;
                    });
                }
                
                if (this.metodosPago.length > 0) {
                    const efectivo = this.metodosPago.find(m => (m.tipo || '').toUpperCase().includes('EFECTIVO'));
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

          if (this.esEfectivo) {
            return true;
          }

          if (this.esMercadoPago && !this.mpSubOption) {
            this.mostrarMensaje('Debe elegir entre alias o QR para cobrar con Mercado Pago', 'warning');
            return false;
          }

          if (this.esTransferencia && !this.datosVenta.entidad_pago) {
             this.mostrarMensaje('Debe seleccionar la entidad bancaria', 'warning');
             return false;
          }

          if (this.esTransferencia && !this.datosVenta.codigo_transaccion) {
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
            
            let entidadFinal = null;
            if (this.esMercadoPago) {
                entidadFinal = this.mpSubOption === 'qr' ? 'MERCADOPAGO_QR' : 'MERCADOPAGO_ALIAS';
            } else if (this.esTransferencia) {
                entidadFinal = this.datosVenta.entidad_pago;
            }

            const payload = { 
                total: parseFloat(this.total),
                tipo: 'PRODUCTO', 
                medio_pago: parseInt(this.datosVenta.medio_pago),
                detalles,
                cliente: null,
                usuario: this.datosVenta.usuario,
                entidad_pago: entidadFinal,
                codigo_transaccion: this.datosVenta.codigo_transaccion || null
            };

            if (this.envioData) {
                payload.costo_envio = this.envioData.costo_envio
                payload.direccion_entrega = this.envioData.direccion_entrega
                payload.latitud_destino = this.envioData.latitud_destino
                payload.longitud_destino = this.envioData.longitud_destino
                payload.distancia_km = this.envioData.distancia_km
            }

            return payload
        },

        manejarErrorVenta(err) {
            Swal.close();
            let errorMessage = 'Error desconocido al registrar venta.';
            
            if (err.response) {
                if (err.response.status === 401) {
                    errorMessage = 'Permiso denegado. Debe iniciar sesión.';
                } else if (err.response.data) {
                    if (err.response.data.error) {
                        errorMessage = err.response.data.error;
                    } 
                    else if (err.response.data.message) {
                        errorMessage = err.response.data.message;
                    }
                    else {
                         try {
                            const data = err.response.data;
                            errorMessage = Object.entries(data).map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`).join('; ');
                         } catch (e) {
                             errorMessage = JSON.stringify(err.response.data);
                         }
                    }
                }
            }
            
            Swal.fire({
                icon: 'warning',
                title: 'Atención',
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

        onEnvioConfirmado(data) {
            this.envioData = data
        },

        onEnvioQuitado() {
            this.envioData = null
        },

        quitarEnvio() {
            this.envioData = null
        },

        async cargarConfiguracionLocal() {
            try {
                const res = await axios.get(`${API_BASE_URL}/api/configuracion-local/`);
                this.mp_alias = res.data.mp_alias || '';
            } catch (err) {
                console.error("Error al cargar config local:", err);
            }
        },

        async generarQR() {
            if (!this.total || this.total <= 0) return;
            this.generandoQR = true;
            this.mpPagoEstado = null;
            this.detenerPollingPago();
            try {
                const res = await axios.post(`${API_BASE_URL}/api/generar-qr-temporal/`, {
                    monto: this.total,
                    title: 'Venta de productos - HairSoft'
                });
                if (res.data.status === 'ok') {
                    this.mpQrData = res.data;
                    this.mpPagoEstado = 'pending';
                    this.iniciarPollingPago(res.data.uid);
                } else {
                    this.mostrarMensaje('Error al generar el QR', 'error');
                }
            } catch (err) {
                console.error("Error al generar QR:", err);
                this.mostrarMensaje('Error al generar el QR', 'error');
            } finally {
                this.generandoQR = false;
            }
        },

        iniciarPollingPago(uid) {
            this.detenerPollingPago();
            this.mpPagoInterval = setInterval(async () => {
                try {
                    const res = await axios.get(`${API_BASE_URL}/api/check-pago-temporal/${uid}/`);
                    if (res.data.pagado) {
                        this.mpPagoEstado = 'confirmed';
                        this.detenerPollingPago();
                        this.mostrarMensaje('Pago confirmado', 'success');
                    }
                } catch (err) {
                    console.error("Error al verificar pago:", err);
                }
            }, 3000);
        },

        detenerPollingPago() {
            if (this.mpPagoInterval) {
                clearInterval(this.mpPagoInterval);
                this.mpPagoInterval = null;
            }
        },

        confirmarPagoManual() {
            this.mpPagoEstado = 'confirmed';
            this.detenerPollingPago();
            this.mostrarMensaje('Pago confirmado manualmente', 'success');
        },

        confirmarSiAlcanza() {
            if (!this.esEfectivo) return;
            if (this.montoRecibido && this.montoRecibido >= this.total) {
                this.registrarVenta();
            }
        },

        copiarAlias() {
            if (this.mp_alias) {
                navigator.clipboard.writeText(this.mp_alias).then(() => {
                    this.mostrarMensaje('Alias copiado al portapapeles', 'success');
                }).catch(() => {
                    this.mostrarMensaje('Alias copiado al portapapeles', 'success');
                });
            }
        },

        limpiarFormulario() {
            this.carrito = [];
            this.envioData = null;
            if (this.metodosPago.length > 0) {
                const efectivo = this.metodosPago.find(m => m.tipo === 'EFECTIVO');
                this.datosVenta.medio_pago = efectivo ? efectivo.id : this.metodosPago[0].id;
            }
            this.datosVenta.codigo_transaccion = '';
            this.datosVenta.entidad_pago = '';
            this.filtroNombre = '';
            this.filtroCategoria = '';
            this.mpSubOption = null;
            this.mpQrData = null;
            this.mpPagoEstado = null;
            this.montoRecibido = null;
            this.detenerPollingPago();
        }
    },
    
    watch: {
        esEfectivo(nuevo) {
            if (nuevo) {
                this.$nextTick(() => {
                    if (this.$refs.montoInput) this.$refs.montoInput.focus();
                });
            }
        }
    },

    beforeUnmount() {
        this.detenerPollingPago();
    },

    mounted() {
        this.verificarCajaAbierta();

        this.cargarProductos();
        this.cargarCategorias();
        this.cargarMetodosPago();
        this.cargarConfiguracionLocal();
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
  grid-template-columns: 1fr 520px;
  gap: 30px;
}

/* ============================================
   SECCIÓN DE BÚSQUEDA
   ============================================ */
.carrito-section {
  position: sticky;
  top: 30px;
  align-self: start;
  background: #1e293b;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid #334155;
}

.search-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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

.input-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #94a3b8;
  pointer-events: none;
  z-index: 1;
}

.input-search-icon {
  padding-left: 42px !important;
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
}

.productos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
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

.qty-stepper {
  display: flex;
  align-items: center;
  gap: 0;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  background: #f7fafc;
}

.qty-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: #475569;
  font-size: 20px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  line-height: 1;
}

.qty-btn:hover:not(:disabled) {
  background: #06b6d4;
  color: white;
}

.qty-btn:disabled {
  color: #cbd5e0;
  cursor: not-allowed;
}

.qty-value {
  min-width: 36px;
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  background: white;
  padding: 4px 0;
  border-left: 2px solid #e2e8f0;
  border-right: 2px solid #e2e8f0;
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
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 20px;
}

.carrito-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
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
  background: transparent;
  border-bottom: 1px solid #e2e8f0;
  padding: 14px 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
}

.carrito-item:last-child {
  border-bottom: none;
}

.carrito-item:hover {
  background: #f8fafc;
  margin: 0 -4px;
  padding: 14px 8px;
  border-radius: 8px;
  border-bottom-color: transparent;
}

.item-left {
  flex: 1;
  min-width: 0;
}

.item-left h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-detalles {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
}

.item-cantidad {
  font-weight: 700;
  color: #0891b2;
  background: #ecfeff;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
}

.item-sep {
  color: #cbd5e1;
}

.item-precio-unitario {
  color: #64748b;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.item-subtotal {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  min-width: 70px;
  text-align: right;
}

.btn-quitar {
  background: transparent;
  border: none;
  color: #94a3b8;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0.5;
}

.carrito-item:hover .btn-quitar {
  opacity: 1;
}

.btn-quitar:hover {
  background: #fef2f2;
  color: #ef4444;
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
  border-radius: 14px;
  padding: 28px;
}

.pago-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  color: #06b6d4;
}

.pago-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.total-destacado {
  background: linear-gradient(135deg, #0e7490, #0891b2);
  border-radius: 16px;
  padding: 24px 28px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.total-destacado .total-label {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.75);
  letter-spacing: 1.5px;
}

.total-destacado .total-valor {
  font-size: 40px;
  font-weight: 800;
  color: white;
  line-height: 1.1;
}

/* ============================================
   SECTION DIVIDER
   ============================================ */
.section-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 20px 0;
}

/* ============================================
   SLIDE-FADE TRANSITION
   ============================================ */
.slide-fade-enter-active {
  transition: all 0.25s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.15s ease-in;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* ============================================
   VUELTO (EFECTIVO)
   ============================================ */
.vuelto-section {
  margin-bottom: 20px;
}

.vuelto-section .form-group label {
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  letter-spacing: 0.5px;
}

.montos-rapidos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.btn-monto-rapido {
  flex: 1;
  min-width: 70px;
  background: #f8fafc;
  border: 2px solid #cbd5e1;
  color: #1e293b;
  padding: 12px 6px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-monto-rapido:hover {
  background: #06b6d4;
  border-color: #06b6d4;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(6, 182, 212, 0.3);
}

.btn-monto-exacto {
  background: #f0fdf4;
  border-color: #86efac;
  color: #166534;
}

.btn-monto-exacto:hover {
  background: #16a34a;
  border-color: #16a34a;
  color: white;
}

.input-monto-recibido {
  font-size: 26px;
  font-weight: 700;
  text-align: center;
  padding: 14px 16px !important;
  height: 56px;
}

.vuelto-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border: 2px solid #86efac;
  border-radius: 14px;
  padding: 20px 24px;
  margin-top: 14px;
}

.vuelto-label {
  font-size: 13px;
  font-weight: 700;
  color: #166534;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.vuelto-valor {
  font-size: 38px;
  font-weight: 800;
  color: #16a34a;
  line-height: 1.1;
}

.vuelto-faltante {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  margin-top: 14px;
  padding: 18px 24px;
  background: #fef2f2;
  border: 2px solid #fca5a5;
  border-radius: 14px;
  color: #dc2626;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.vuelto-faltante span {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: 0;
}

.metodo-pago-opciones {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metodo-pago-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.metodo-pago-card:hover {
  border-color: #06b6d4;
  background: #ecfeff;
}

.metodo-pago-selected {
  border-color: #06b6d4;
  background: #ecfeff;
}

.metodo-pago-selected .mp-icon {
  color: #0891b2;
}

.mp-icon {
  width: 44px;
  height: 44px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  flex-shrink: 0;
  border: 2px solid #e2e8f0;
}

.metodo-pago-selected .mp-icon {
  border-color: #06b6d4;
  background: white;
}

.mp-nombre {
  flex: 1;
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}

.mp-radio {
  flex-shrink: 0;
}

.btn-confirmar {
  width: 100%;
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: none;
  padding: 18px 16px;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
  letter-spacing: 0.3px;
}

.btn-confirmar:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(16, 185, 129, 0.45);
}

.btn-confirmar:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  opacity: 0.6;
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

.spinner-green {
  border-color: rgba(251, 191, 36, 0.3);
  border-top-color: #f59e0b;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.qr-pago-pendiente {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 14px;
  background: #fefce8;
  border: 2px solid #fcd34d;
  border-radius: 10px;
  color: #92400e;
  font-weight: 600;
  font-size: 14px;
}

.qr-pago-confirmado {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
  padding: 14px;
  background: #d1fae5;
  border: 2px solid #34d399;
  border-radius: 10px;
  color: #065f46;
  font-weight: 700;
  font-size: 15px;
}

.btn-confirmar-manual {
  background: white;
  border: 1px solid #d1d5db;
  color: #6b7280;
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirmar-manual:hover {
  border-color: #9ca3af;
  color: #374151;
  background: #f9fafb;
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
   MERCADO PAGO SUB-OPTIONS
   ============================================ */
.datos-extra-pago {
  margin-top: 16px;
}

.mp-sub-label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 12px;
  display: block;
}

.mp-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mp-option-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  background: #f7fafc;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.mp-option-card:hover {
  border-color: #06b6d4;
  background: #ecfeff;
  box-shadow: 0 2px 12px rgba(6, 182, 212, 0.1);
}

.mp-option-selected {
  border-color: #06b6d4;
  background: #ecfeff;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
}

.mp-option-content {
  display: flex;
  gap: 14px;
  flex: 1;
  align-items: flex-start;
}

.mp-option-icon {
  width: 44px;
  height: 44px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #06b6d4;
  flex-shrink: 0;
  border: 1px solid #e2e8f0;
}

.mp-option-selected .mp-option-icon {
  background: #06b6d4;
  color: white;
  border-color: #06b6d4;
}

.mp-option-info {
  flex: 1;
}

.mp-option-info h4 {
  font-size: 15px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 4px 0;
}

.mp-option-info p {
  font-size: 13px;
  color: #718096;
  margin: 0 0 12px 0;
}

.mp-option-radio {
  padding-top: 6px;
  flex-shrink: 0;
}

.radio-circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #cbd5e0;
  transition: all 0.3s ease;
  position: relative;
}

.radio-circle::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #06b6d4;
  transform: translate(-50%, -50%) scale(0);
  transition: all 0.3s ease;
}

.radio-active {
  border-color: #06b6d4;
}

.radio-active::after {
  transform: translate(-50%, -50%) scale(1);
}

.mp-alias-display {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  padding: 10px 14px;
  border-radius: 10px;
  border: 2px dashed #06b6d4;
  margin-bottom: 12px;
}

.mp-alias-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.mp-alias-value {
  font-size: 18px;
  font-weight: 800;
  color: #0891b2;
  letter-spacing: 0.5px;
  font-family: 'Courier New', monospace;
}

.btn-copy-alias {
  background: #ecfeff;
  border: 1px solid #a5f3fc;
  color: #0891b2;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: auto;
  flex-shrink: 0;
}

.btn-copy-alias:hover {
  background: #06b6d4;
  color: white;
  border-color: #06b6d4;
}

.mp-id-opcional {
  margin-top: 4px;
}

.mp-id-opcional label {
  font-size: 13px;
  font-weight: 600;
  color: #4a5568;
  display: block;
  margin-bottom: 6px;
}

.opcional-tag {
  font-size: 11px;
  font-weight: 600;
  color: #f59e0b;
  background: #fffbeb;
  padding: 2px 8px;
  border-radius: 6px;
  margin-left: 6px;
  border: 1px solid #fcd34d;
}

.mp-id-opcional input {
  margin-bottom: 4px;
}

.mp-id-opcional small {
  color: #9ca3af;
  font-size: 12px;
}

.mp-qr-section {
  margin-top: 4px;
}

.btn-generar-qr {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-generar-qr:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
}

.btn-generar-qr:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.qr-display {
  margin-top: 16px;
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.qr-hint {
  font-size: 13px;
  color: #64748b;
  margin-top: 10px;
  font-weight: 600;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1400px) {
  .content-grid {
    grid-template-columns: 1fr 480px;
  }
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .carrito-section {
    order: -1;
    position: static;
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