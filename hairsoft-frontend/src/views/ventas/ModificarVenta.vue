<template>
  <div class="venta-page">
    <div class="venta-wrapper">
      <div class="page-header">
        <div class="header-content">
          <div class="header-title">
            <div class="title-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
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
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
              <div class="metodo-pago-opciones">
                <div 
                  v-for="mp in metodosPago" 
                  :key="mp.id"
                  class="metodo-pago-card"
                  :class="{ 
                    'metodo-pago-selected': !esMixto && datosVenta.medio_pago === mp.id,
                    'metodo-pago-bloqueado': pagoEfectuado
                  }"
                  @click="seleccionarMetodo(mp)"
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
                    <span>{{ mp.nombre }}</span>
                  </div>
                  <div class="mp-radio">
                    <div class="radio-circle" :class="{ 'radio-active': !esMixto && datosVenta.medio_pago === mp.id }"></div>
                  </div>
                </div>

                <div 
                  v-if="hayMetodosMixto"
                  class="metodo-pago-card"
                  :class="{ 
                    'metodo-pago-selected': esMixto,
                    'metodo-pago-bloqueado': pagoEfectuado
                  }"
                  @click="seleccionarMixto"
                >
                  <div class="mp-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M4 6h16v12H4V6Z"/>
                      <path d="M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/>
                      <rect x="2" y="6" width="20" height="12" rx="2"/>
                      <path d="M2 10h20"/>
                    </svg>
                  </div>
                  <div class="mp-nombre">
                    <span>Mixto (MP + Efectivo)</span>
                    <small class="mp-subnombre">Parte con Mercado Pago y el resto en efectivo</small>
                  </div>
                  <div class="mp-radio">
                    <div class="radio-circle" :class="{ 'radio-active': esMixto }"></div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="esMedioPagoConRecargo || esMixto" class="datos-extra-pago slide-in">
              
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

              <!-- MERCADO PAGO SUB-OPTIONS -->
              <div v-if="esMercadoPago || esMixto" class="mp-options-wrapper">
                <label class="mp-sub-label">Elegí cómo cobrar con Mercado Pago:</label>

                <div v-if="esMixto" class="mixto-monto-group">
                  <div class="form-group">
                    <label>Monto a cobrar con Mercado Pago</label>
                    <div class="mixto-monto-row">
                      <input
                        type="number"
                        v-model.number="montoMP"
                        class="input-search input-monto-mp"
                        :min="0"
                        :max="total"
                        :disabled="pagoMixtoMpPagado"
                        step="0.01"
                      />
                      <button class="btn-mitad" @click="montoMP = redondear2(total / 2)" :disabled="pagoMixtoMpPagado">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        Mitad
                      </button>
                    </div>
                    <small class="mixto-hint">
                      El resto <strong>${{ restanteEfectivo.toFixed(2) }}</strong> se cobra en efectivo
                    </small>
                  </div>
                  <div class="mixto-aviso" v-if="!montoMPValido">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="8" x2="12" y2="12"></line>
                      <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <span>El monto con Mercado Pago debe ser mayor a $0 y menor al total</span>
                  </div>
                </div>

                <div class="mp-options">
                  <div class="mp-option-card" :class="{ 'mp-option-selected': mpSubOption === 'alias', 'mp-option-bloqueado': pagoEfectuado }" @click="seleccionarSubOpcionMP('alias')">
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

                  <div class="mp-option-card" :class="{ 'mp-option-selected': mpSubOption === 'qr', 'mp-option-bloqueado': pagoEfectuado }" @click="seleccionarSubOpcionMP('qr')">
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
                          <button @click.stop="generarQR" class="btn-generar-qr" :disabled="generandoQR || mpPagoEstado === 'confirmed'">
                            <template v-if="!generandoQR">
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="12" y1="8" x2="12" y2="16"></line>
                                <line x1="8" y1="12" x2="16" y2="12"></line>
                              </svg>
                              {{ mpPagoEstado === 'confirmed' ? 'Pago Confirmado' : (esMixto ? 'Generar QR (MP)' : 'Generar QR') }}
                            </template>
                            <template v-else>
                              <div class="spinner-sm"></div>
                              Generando...
                            </template>
                          </button>
                          <div v-if="mpQrData" class="qr-display">
                            <div class="qr-display-inner">
                              <qrcode-vue :value="mpQrData.init_point" :size="170" level="H" />
                            </div>
                            <div v-if="mpPagoEstado === 'confirmed'" class="qr-pago-confirmado">
                              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <polyline points="20 6 9 17 4 12"></polyline>
                              </svg>
                              <span>¡Pago confirmado!</span>
                            </div>
                            <div v-else-if="mpPagoEstado === 'pending'" class="qr-pago-pendiente">
                              <div class="pending-ring">
                                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                  <rect x="3" y="3" width="7" height="7"></rect>
                                  <rect x="14" y="3" width="7" height="7"></rect>
                                  <rect x="14" y="14" width="7" height="7"></rect>
                                  <rect x="3" y="14" width="7" height="7"></rect>
                                </svg>
                              </div>
                              <div class="pending-textos">
                                <span class="pending-title">Esperando pago...</span>
                                <span class="pending-sub">El QR se actualiza automáticamente</span>
                              </div>
                            </div>
                            <p v-else class="qr-hint">Escaneá el código QR con la cámara de tu billetera virtual</p>
                            <div class="qr-actions">
                              <button class="btn-ampliar-qr" @click="qrFullscreen = true">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                  <polyline points="15 3 21 3 21 9"></polyline>
                                  <polyline points="9 21 3 21 3 15"></polyline>
                                  <line x1="21" y1="3" x2="14" y2="10"></line>
                                  <line x1="3" y1="21" x2="10" y2="14"></line>
                                </svg>
                                Ver en pantalla completa
                              </button>
                              <button class="btn-regresar-qr" @click="regresarDelQR" :disabled="mpPagoEstado === 'confirmed'">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                  <line x1="19" y1="12" x2="5" y2="12"></line>
                                  <polyline points="12 19 5 12 12 5"></polyline>
                                </svg>
                                Regresar
                              </button>
                            </div>
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

              <div class="form-group" v-if="esTransferencia">
                <label>Código de Comprobante *</label>
                <input 
                  type="text" 
                  v-model="datosVenta.codigo_transaccion" 
                  class="input-search"
                  placeholder="Ej: A123B456789"
                  maxlength="25"
                />
                <small style="color: #6b7280; font-size: 0.8rem; margin-top: 4px; display: block;">
                  Copie el código del comprobante bancario.
                </small>
              </div>
            </div>

            <transition name="slide-fade">
              <div v-if="esEfectivo || esMixto" class="vuelto-section">
                <div class="vuelto-titulo" v-if="esMixto">
                  <span class="vuelto-titulo-label">Falta cobrar en efectivo</span>
                  <span class="vuelto-titulo-monto">${{ restanteEfectivo.toFixed(2) }}</span>
                </div>
                <div class="form-group">
                  <label>{{ esMixto ? 'Monto recibido en efectivo' : 'Monto recibido' }}</label>
                  <input
                    type="number"
                    v-model.number="montoRecibido"
                    class="input-search input-monto-recibido"
                    placeholder="$0.00"
                    min="0"
                    step="0.01"
                  />
                </div>
                <div class="montos-rapidos" v-if="!montoRecibido || montoRecibido < objetivoEfectivo">
                  <button
                    v-for="monto in montosRapidosEfectivo"
                    :key="monto"
                    class="btn-monto-rapido"
                    @click="montoRecibido = monto"
                  >
                    ${{ monto.toLocaleString() }}
                  </button>
                  <button class="btn-monto-rapido btn-monto-exacto" @click="montoRecibido = objetivoEfectivo">
                    Exacto
                  </button>
                </div>
                <div v-if="montoRecibido && montoRecibido >= objetivoEfectivo" class="vuelto-display">
                  <span class="vuelto-label">Vuelto</span>
                  <span class="vuelto-valor">${{ vuelto.toFixed(2) }}</span>
                </div>
                <div v-else-if="montoRecibido && montoRecibido < objetivoEfectivo" class="vuelto-faltante">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>
                  <span>Faltan ${{ (objetivoEfectivo - montoRecibido).toFixed(2) }}</span>
                </div>
              </div>
            </transition>

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

      <transition name="fade-overlay">
        <div v-if="qrFullscreen && mpQrData" class="qr-fullscreen-overlay">
          <div class="qr-fullscreen-content">
            <div class="qr-fullscreen-header">
              <h2>Escaneá el código QR</h2>
              <p>Con la cámara de tu billetera virtual</p>
            </div>

            <div class="qr-fullscreen-amount">
              <span class="fs-amount-label">Total a pagar</span>
              <span class="fs-amount-valor">${{ total.toFixed(2) }}</span>
            </div>

            <div class="qr-fullscreen-box">
              <div class="qr-box-white">
                <qrcode-vue :value="mpQrData.init_point" :size="300" level="H" />
              </div>
            </div>

            <div v-if="mpPagoEstado === 'confirmed'" class="qr-fullscreen-status status-ok">
              <div class="status-check">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
              <span class="status-text">¡Pago confirmado!</span>
              <span class="status-sub">Ya podés confirmar la venta</span>
            </div>
            <div v-else class="qr-fullscreen-status status-wait">
              <div class="fs-pending-ring"></div>
              <span class="status-text">Esperando pago...</span>
              <span class="status-sub">Se actualiza automáticamente al recibir el pago</span>
            </div>

            <button class="btn-regresar" @click="mpPagoEstado === 'confirmed' ? (qrFullscreen = false) : regresarDelQR">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              {{ mpPagoEstado === 'confirmed' ? 'Continuar' : 'Regresar' }}
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2'
import QrcodeVue from 'qrcode.vue'

// URLs relativas usando la base de axiosConfig
const API_URL_PRODUCTOS = '/usuarios/api/productos/'
const API_URL_METODOS = '/usuarios/api/metodos-pago/'
const API_URL_CATEGORIAS = '/usuarios/api/categorias/productos/'
const API_URL_VENTAS = '/usuarios/api/ventas/'

export default {
  name: 'ModificarVenta',
  components: { QrcodeVue },
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
      mp_alias: '',
      mpSubOption: null,
      mpQrData: null,
      generandoQR: false,
      mpPagoInterval: null,
      mpPagoEstado: null,
      qrFullscreen: false,
      pagoMixto: false,
      montoMP: null,
      montoRecibido: null,
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
    esEfectivo() {
        if (this.esMercadoPago || this.esTransferencia) return false;
        const mp = this.metodoPagoSeleccionado;
        if (!mp) return false;
        const tipo = (mp.tipo || '').toUpperCase();
        const nombre = (mp.nombre || '').toUpperCase();
        return tipo.includes('EFECTIVO') || nombre.includes('EFECTIVO');
    },
    maxCodigoLength() {
        return this.esMercadoPago ? 14 : 25;
    },

    // 🔥 PAGO MIXTO (MP + EFECTIVO)
    metodoMP() {
        return this.metodosPago.find(m => {
            const tipo = (m.tipo || '').toUpperCase();
            const nombre = (m.nombre || '').toUpperCase();
            return tipo.includes('MERCADO') || nombre.includes('MERCADO');
        });
    },
    metodoEfectivoObj() {
        return this.metodosPago.find(m => {
            const tipo = (m.tipo || '').toUpperCase();
            const nombre = (m.nombre || '').toUpperCase();
            return tipo.includes('EFECTIVO') || nombre.includes('EFECTIVO');
        });
    },
    hayMetodosMixto() {
        return !!(this.metodoMP && this.metodoEfectivoObj);
    },
    esMixto() {
        return this.pagoMixto && this.hayMetodosMixto;
    },
    montoMPValido() {
        if (!this.esMixto) return true;
        return !!(this.montoMP && this.montoMP > 0 && this.montoMP < this.total);
    },
    restanteEfectivo() {
        if (!this.esMixto || !this.montoMP) return this.total;
        return Math.max(0, this.total - this.montoMP);
    },
    objetivoEfectivo() {
        return this.esMixto ? this.restanteEfectivo : this.total;
    },
    vuelto() {
        if (!this.montoRecibido) return 0;
        return Math.max(0, this.montoRecibido - this.objetivoEfectivo);
    },
    montosRapidosEfectivo() {
        const t = this.objetivoEfectivo;
        const montos = [100, 500, 1000, 2000, 5000, 10000, 20000];
        return montos.filter(m => m > t);
    },

    // 🔥 BLOQUEO UNA VEZ QUE EL PAGO YA SE EFECTUÓ
    pagoEfectuado() {
        if (this.esMixto) {
            if (this.mpSubOption === 'qr' && this.mpPagoEstado === 'confirmed') return true;
            if (this.mpSubOption === 'alias' && this.datosVenta.codigo_transaccion) return true;
            if (this.montoRecibido && this.restanteEfectivo > 0 && this.montoRecibido >= this.restanteEfectivo) return true;
            return false;
        }
        if (this.esEfectivo) {
            return !!(this.montoRecibido && this.montoRecibido >= this.total);
        }
        if (this.esMercadoPago && this.mpSubOption === 'qr') {
            return this.mpPagoEstado === 'confirmed';
        }
        if (this.esMercadoPago && this.mpSubOption === 'alias') {
            return !!this.datosVenta.codigo_transaccion;
        }
        return false;
    },
    pagoMixtoMpPagado() {
        if (!this.esMixto) return false;
        if (this.mpSubOption === 'qr') return this.mpPagoEstado === 'confirmed';
        if (this.mpSubOption === 'alias') return !!this.datosVenta.codigo_transaccion;
        return false;
    },
    
    formularioValido() {
      if (this.carrito.length === 0) return false;
      if (!this.datosVenta.medio_pago) return false;

      if (this.esTransferencia && !this.datosVenta.codigo_transaccion) {
         return false;
      }

      if (this.esMercadoPago && !this.esMixto && this.mpSubOption === 'qr' && this.mpPagoEstado !== 'confirmed') {
        return false;
      }

      if (this.esEfectivo && !this.esMixto && (!this.montoRecibido || this.montoRecibido < this.total)) {
        return false;
      }

      if (this.esMixto) {
        if (!this.montoMPValido) return false;
        if (this.mpSubOption === 'qr' && this.mpPagoEstado !== 'confirmed') return false;
        if (!this.montoRecibido || this.montoRecibido < this.restanteEfectivo) return false;
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
             this.mpSubOption = null;
             this.mpQrData = null;
             this.mpPagoEstado = null;
             this.detenerPollingPago();
             return;
        }

        // Si cambia a Efectivo, limpiar todo
        if (!this.esMedioPagoConRecargo) {
            this.datosVenta.entidad_pago = '';
            this.datosVenta.codigo_transaccion = '';
            this.mpSubOption = null;
            this.mpQrData = null;
            this.mpPagoEstado = null;
            this.montoRecibido = null;
            this.pagoMixto = false;
            this.montoMP = null;
            this.detenerPollingPago();
        } else if (this.esMercadoPago) {
            this.datosVenta.entidad_pago = '';
            this.datosVenta.codigo_transaccion = '';
            this.mpSubOption = null;
            this.mpQrData = null;
            this.mpPagoEstado = null;
            this.montoRecibido = null;
            this.pagoMixto = false;
            this.montoMP = null;
            this.detenerPollingPago();
        }
    },

    total(nuevo, viejo) {
      if (this.mpQrData && nuevo !== viejo) {
        this.mpQrData = null;
        this.mpPagoEstado = null;
        this.detenerPollingPago();
        this.mostrarMensaje('El total cambió. Volvé a generar el QR');
      }
      if (this.esMixto && this.montoMP) {
        if (this.montoMP > this.total) this.montoMP = this.total;
      }
    },

    montoMP(nuevo, viejo) {
      if (this.esMixto && nuevo !== viejo) {
        this.mpQrData = null;
        this.mpPagoEstado = null;
        this.detenerPollingPago();
        this.mostrarMensaje('El monto a cobrar con Mercado Pago cambió. Volvé a generar el QR');
      }
    },

    mpQrData(nuevo) {
      if (!nuevo) this.qrFullscreen = false;
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

        // Restaurar sub-opción MP si corresponde
        const entidadOriginal = (ventaData.entidad_pago || '').toUpperCase();

        // 🔥 Restaurar pago mixto (entidad_pago = MIXTO)
        this.pagoMixto = false;
        this.montoMP = null;
        this.montoRecibido = null;
        if (entidadOriginal === 'MIXTO' && this.hayMetodosMixto) {
            this.pagoMixto = true;
            const monto = this.extraerMontoMP(ventaData.codigo_transaccion);
            this.montoMP = monto !== null ? monto : this.redondear2((ventaData.total || 0) / 2);
            this.montoRecibido = this.redondear2((ventaData.total || 0) - this.montoMP);
            const forma = String(ventaData.codigo_transaccion || '').split(':')[0].toUpperCase();
            this.mpSubOption = forma.includes('QR') ? 'qr' : 'alias';
        }

        if (this.esMercadoPago && !this.pagoMixto) {
            const entidad = (ventaData.entidad_pago || '').toUpperCase();
            this.mpSubOption = entidad === 'MERCADOPAGO_QR' ? 'qr' : 'alias';
        }
        
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

      // Validación extra para transferencia
      if (this.esTransferencia && !this.datosVenta.codigo_transaccion) {
          Swal.fire('Atención', 'Falta el código de transacción', 'warning');
          return;
      }

      if (this.esMercadoPago && !this.mpSubOption) {
          Swal.fire('Atención', 'Debe elegir entre alias o QR para cobrar con Mercado Pago', 'warning');
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
      if (this.esMixto) {
          entidadFinal = this.mpSubOption === 'qr' ? 'MERCADOPAGO_QR' : 'MERCADOPAGO_ALIAS';
      } else if (this.esMercadoPago) {
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
        motivo_modificacion: motivo,
        usuario_modificacion: 'usuario_actual',
        
        entidad_pago: entidadFinal,
        codigo_transaccion: this.esMixto ? null : (this.datosVenta.codigo_transaccion || null),

        pago_mixto: this.esMixto || undefined,
        monto_mp: this.esMixto ? parseFloat(this.montoMP) : undefined,
        monto_efectivo: this.esMixto ? parseFloat(this.montoRecibido >= this.restanteEfectivo ? this.restanteEfectivo : this.montoRecibido) : undefined
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

    esEfectivoMetodo(mp) {
      const tipo = (mp.tipo || '').toUpperCase();
      const nombre = (mp.nombre || '').toUpperCase();
      return tipo.includes('EFECTIVO') || nombre.includes('EFECTIVO');
    },

    redondear2(n) {
      return Math.round((Number(n) || 0) * 100) / 100;
    },

    extraerMontoMP(codigoTransaccion) {
      if (!codigoTransaccion) return null;
      const match = String(codigoTransaccion).match(/(?:MERCADOPAGO_[A-Z_]+):([\d.]+)/i);
      if (match) return parseFloat(match[1]);
      return null;
    },

    salirModoMixto() {
      this.pagoMixto = false;
      this.montoMP = null;
      this.montoRecibido = null;
      this.mpSubOption = null;
      this.mpQrData = null;
      this.mpPagoEstado = null;
      this.qrFullscreen = false;
      this.detenerPollingPago();
      this.datosVenta.codigo_transaccion = '';
    },

    confirmarCancelarMixto(onConfirm) {
      Swal.fire({
        icon: 'question',
        title: '¿Está seguro de que desea cancelar el pago con dos métodos de pago?',
        text: 'Se limpiarán los importes ingresados y volverá a la selección normal de métodos.',
        showCancelButton: true,
        confirmButtonText: 'Sí, cancelar',
        cancelButtonText: 'No, seguir',
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#6c757d',
        reverseButtons: true,
        allowOutsideClick: false
      }).then((result) => {
        if (result.isConfirmed) onConfirm();
      });
    },

    seleccionarMetodo(mp) {
      if (this.pagoEfectuado) {
        Swal.fire({
          icon: 'warning',
          title: 'El pago ya se efectuó',
          text: 'No podés cambiar el método de pago porque el cobro ya se realizó.',
          confirmButtonText: 'Entendido',
          confirmButtonColor: '#F59E0B'
        });
        return;
      }
      // 🔥 Si está en modo mixto, pedir confirmación para salir
      if (this.esMixto) {
        this.confirmarCancelarMixto(() => {
          this.salirModoMixto();
          this.datosVenta.medio_pago = mp.id;
        });
        return;
      }
      this.pagoMixto = false;
      this.montoMP = null;
      this.montoRecibido = null;
      if (this.datosVenta.medio_pago === mp.id) return;
      this.datosVenta.medio_pago = mp.id;
    },

    seleccionarMixto() {
      if (this.pagoEfectuado) {
        Swal.fire({
          icon: 'warning',
          title: 'El pago ya se efectuó',
          text: 'No podés cambiar el método de pago porque el cobro ya se realizó.',
          confirmButtonText: 'Entendido',
          confirmButtonColor: '#F59E0B'
        });
        return;
      }
      // 🔥 Si ya está en modo mixto, la tarjeta funciona como "salir"
      if (this.esMixto) {
        this.confirmarCancelarMixto(() => {
          this.salirModoMixto();
        });
        return;
      }
      if (!this.hayMetodosMixto) return;
      this.pagoMixto = true;
      this.montoMP = this.redondear2(this.total / 2);
      this.montoRecibido = null;
      this.datosVenta.medio_pago = this.metodoMP.id;
    },

    seleccionarSubOpcionMP(opcion) {
      if (this.pagoEfectuado) {
        Swal.fire({
          icon: 'warning',
          title: 'El pago ya se efectuó',
          text: 'No podés cambiar el método de cobro porque el pago ya se realizó.',
          confirmButtonText: 'Entendido',
          confirmButtonColor: '#F59E0B'
        });
        return;
      }
      if (this.mpSubOption === opcion) return;
      this.mpSubOption = opcion;
      this.datosVenta.codigo_transaccion = '';
      this.mpQrData = null;
      this.mpPagoEstado = null;
      this.detenerPollingPago();
    },

    async generarQR() {
      if (!this.total || this.total <= 0) return;
      const montoQR = this.esMixto ? (this.montoMP || 0) : this.total;
      if (montoQR <= 0) return;
      this.generandoQR = true;
      this.mpPagoEstado = null;
      this.detenerPollingPago();
      try {
        const res = await axios.post('/api/generar-qr-temporal/', {
          monto: montoQR,
          title: 'Venta de productos - HairSoft'
        });
        if (res.data.status === 'ok') {
          this.mpQrData = res.data;
          this.mpPagoEstado = 'pending';
          this.iniciarPollingPago(res.data.uid);
          this.qrFullscreen = true;
        } else {
          this.mostrarMensaje('Error al generar el QR', true);
        }
      } catch (err) {
        console.error("Error al generar QR:", err);
        this.mostrarMensaje('Error al generar el QR', true);
      } finally {
        this.generandoQR = false;
      }
    },

    iniciarPollingPago(uid) {
      this.detenerPollingPago();
      this.mpPagoInterval = setInterval(async () => {
        try {
          const res = await axios.get(`/api/check-pago-temporal/${uid}/`);
          if (res.data.pagado) {
            this.mpPagoEstado = 'confirmed';
            this.detenerPollingPago();
            this.mostrarMensaje('Pago confirmado');
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

    regresarDelQR() {
      if (this.mpPagoEstado === 'confirmed' || this.pagoEfectuado) {
        this.mostrarMensaje('El pago ya se efectuó, no se puede cancelar el QR', true);
        return;
      }
      this.qrFullscreen = false;
      this.mpQrData = null;
      this.mpPagoEstado = null;
      this.detenerPollingPago();
    },

    copiarAlias() {
      if (this.mp_alias) {
        navigator.clipboard.writeText(this.mp_alias).then(() => {
          this.mostrarMensaje('Alias copiado al portapapeles');
        }).catch(() => {
          this.mostrarMensaje('Alias copiado al portapapeles');
        });
      }
    },

    async cargarConfiguracionLocal() {
      try {
        const res = await axios.get('/api/configuracion-local/');
        this.mp_alias = res.data.mp_alias || '';
      } catch (err) {
        console.error("Error al cargar config local:", err);
      }
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
  
  beforeUnmount() {
    this.detenerPollingPago();
  },

  async mounted() {
    console.log('🚀 Componente ModificarVenta montado');
    this.cargarConfiguracionLocal();
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
  border-radius: 14px;
  padding: 14px 24px;
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
  gap: 14px;
}

.title-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.header-title h1 {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.venta-info-header {
  font-size: 12px;
  color: #94a3b8;
  margin: 4px 0 0 0;
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.badge-activa {
  background: #d1fae5;
  color: #065f46;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.badge-anulada {
  background: #fee2e2;
  color: #991b1b;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.btn-volver {
  background: rgba(6, 182, 212, 0.1);
  border: 2px solid rgba(6, 182, 212, 0.3);
  color: #06b6d4;
  padding: 9px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-volver:hover {
  background: rgba(6, 182, 212, 0.2);
  border-color: #06b6d4;
  transform: translateY(-2px);
}

/* MÉTODOS DE PAGO (TARJETAS) */
.metodo-pago-opciones {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.metodo-pago-card {
  background: #1e293b;
  border: 2px solid #334155;
  border-radius: 12px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.metodo-pago-card:hover {
  border-color: #06b6d4;
  transform: translateY(-1px);
}

.metodo-pago-selected {
  border-color: #06b6d4;
  background: rgba(6, 182, 212, 0.08);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
}

.metodo-pago-bloqueado {
  opacity: 0.55;
  cursor: not-allowed;
  filter: grayscale(0.3);
}

.mp-icon {
  width: 40px;
  height: 40px;
  background: #0f172a;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #06b6d4;
  flex-shrink: 0;
}

.mp-nombre {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.mp-nombre span {
  font-size: 13px;
  font-weight: 600;
  color: #f8fafc;
  line-height: 1.2;
}

.mp-subnombre {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.3;
}

.mp-radio {
  flex-shrink: 0;
}

.radio-circle {
  width: 18px;
  height: 18px;
  border: 2px solid #64748b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.radio-active {
  border-color: #06b6d4;
  background: #06b6d4;
  box-shadow: inset 0 0 0 3px #1e293b;
}

/* PAGO MIXTO */
.mixto-monto-group {
  background: rgba(6, 182, 212, 0.06);
  border: 1px dashed rgba(6, 182, 212, 0.4);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 14px;
}

.mixto-monto-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.input-monto-mp {
  flex: 1;
}

.btn-mitad {
  background: rgba(6, 182, 212, 0.12);
  border: 1px solid rgba(6, 182, 212, 0.4);
  color: #06b6d4;
  padding: 9px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-mitad:hover:not(:disabled) {
  background: rgba(6, 182, 212, 0.22);
}

.btn-mitad:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mixto-hint {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.mixto-hint strong {
  color: #f59e0b;
}

.mixto-aviso {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 10px;
  color: #fbbf24;
  font-size: 12px;
}

.mp-option-bloqueado {
  opacity: 0.55;
  cursor: not-allowed;
  filter: grayscale(0.3);
}

/* SECCIÓN VUELTO / EFECTIVO */
.vuelto-section {
  background: #1e293b;
  border: 2px solid #334155;
  border-radius: 12px;
  padding: 16px;
  margin-top: 4px;
}

.vuelto-titulo {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 10px 12px;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 10px;
}

.vuelto-titulo-label {
  font-size: 13px;
  color: #fbbf24;
  font-weight: 600;
}

.vuelto-titulo-monto {
  font-size: 18px;
  font-weight: 700;
  color: #fbbf24;
}

.input-monto-recibido {
  font-size: 18px !important;
  font-weight: 700 !important;
}

.montos-rapidos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.btn-monto-rapido {
  background: #334155;
  border: 1px solid #475569;
  color: #e2e8f0;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-monto-rapido:hover {
  background: #06b6d4;
  border-color: #06b6d4;
  color: #0f172a;
}

.btn-monto-exacto {
  background: rgba(6, 182, 212, 0.12);
  border-color: rgba(6, 182, 212, 0.4);
  color: #06b6d4;
}

.vuelto-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding: 12px 14px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 10px;
}

.vuelto-label {
  font-size: 14px;
  color: #6ee7b7;
  font-weight: 600;
}

.vuelto-valor {
  font-size: 22px;
  font-weight: 700;
  color: #34d399;
}

.vuelto-faltante {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 10px;
  color: #fbbf24;
  font-size: 13px;
  font-weight: 600;
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

.spinner-green {
  border-color: rgba(251, 191, 36, 0.3);
  border-top-color: #f59e0b;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.qr-pago-pendiente {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 14px;
  padding: 16px;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  border: 2px solid #fcd34d;
  border-radius: 14px;
}

.pending-ring {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b45309;
  flex-shrink: 0;
  position: relative;
}

.pending-ring::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid #fbbf24;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

.pending-ring::after {
  content: '';
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 2px solid rgba(251, 191, 36, 0.35);
  border-bottom-color: transparent;
  animation: spin 1.6s linear infinite reverse;
}

.pending-textos {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.pending-title {
  font-size: 15px;
  font-weight: 700;
  color: #92400e;
}

.pending-sub {
  font-size: 12px;
  font-weight: 500;
  color: #a16207;
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

/* MERCADO PAGO SUB-OPTIONS */
.mp-options-wrapper {
  margin: 12px 0;
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

.qr-display-inner {
  display: inline-flex;
  padding: 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
}

.qr-hint {
  font-size: 13px;
  color: #64748b;
  margin-top: 10px;
  font-weight: 600;
}

.btn-ampliar-qr {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 16px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-ampliar-qr:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.qr-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.qr-actions .btn-ampliar-qr {
  margin-top: 0;
  flex: 1;
}

.btn-regresar-qr {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1;
  padding: 8px 16px;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 10px;
  color: #e11d48;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-regresar-qr:hover:not(:disabled) {
  background: #ffe4e6;
  color: #be123c;
}

.btn-regresar-qr:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qr-fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #020617;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.qr-fullscreen-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  padding: 30px 20px;
  text-align: center;
}

.qr-fullscreen-header h2 {
  color: #f8fafc;
  font-size: 24px;
  margin: 0 0 6px;
  font-weight: 700;
}

.qr-fullscreen-header p {
  color: #64748b;
  margin: 0;
  font-size: 14px;
}

.qr-fullscreen-amount {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 30px;
  border-radius: 16px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid #334155;
}

.fs-amount-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: #64748b;
  font-weight: 600;
}

.fs-amount-valor {
  font-size: 34px;
  font-weight: 800;
  color: #34d399;
  line-height: 1.1;
}

.qr-fullscreen-box {
  padding: 16px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid #334155;
  border-radius: 20px;
}

.qr-box-white {
  background: white;
  padding: 16px;
  border-radius: 14px;
}

.qr-fullscreen-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.status-text {
  font-size: 17px;
  font-weight: 700;
  color: #f8fafc;
}

.status-sub {
  font-size: 13px;
  color: #94a3b8;
}

.status-ok .status-check {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #065f46;
  color: #34d399;
  border: 2px solid #10b981;
  animation: pop-in 0.4s ease;
}

.status-wait .fs-pending-ring {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 4px solid rgba(16, 185, 129, 0.2);
  border-top-color: #10b981;
  animation: spin 1s linear infinite;
  margin-bottom: 4px;
}

.btn-regresar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background: #10b981;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 6px;
}

.btn-regresar:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}

.fade-overlay-enter-active,
.fade-overlay-leave-active {
  transition: opacity 0.25s ease;
}

.fade-overlay-enter-from,
.fade-overlay-leave-to {
  opacity: 0;
}

@keyframes pop-in {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  70% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
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