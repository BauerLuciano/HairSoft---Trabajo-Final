<template>
  <div class="venta-page">
    <!-- ============ PASO 1: ARMAR VENTA ============ -->
    <div v-if="paso === 'venta'" class="pos-grid">
      <section class="productos-panel">
        <div class="filtros-panel">
          <div class="panel-header">
            <div class="header-info">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="4" y1="21" x2="4" y2="14"></line>
                <line x1="4" y1="10" x2="4" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12" y2="3"></line>
                <line x1="20" y1="21" x2="20" y2="16"></line>
                <line x1="20" y1="12" x2="20" y2="3"></line>
                <line x1="1" y1="14" x2="7" y2="14"></line>
                <line x1="9" y1="8" x2="15" y2="8"></line>
                <line x1="17" y1="16" x2="23" y2="16"></line>
              </svg>
              <h2>Filtros</h2>
            </div>
            <button class="btn-limpiar-filtros" @click="restablecerFiltros" title="Limpiar filtros">
              Limpiar
            </button>
          </div>
          <div class="filtros-body">
          <div class="search-row">
          <div class="form-group search-field">
            <label>Buscar producto o código</label>
            <div class="input-icon-wrapper">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <input
                v-model="filtroNombre"
                placeholder="Buscar..."
                class="input-search input-search-icon"
                @input="filtrarProductos"
              />
            </div>
          </div>
          <div class="form-group search-field">
            <label>Categoría</label>
            <select v-model="filtroCategoria" class="input-select">
              <option value="">Todas</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                {{ cat.nombre }}
              </option>
            </select>
          </div>
          <div class="form-group search-field">
            <label>Más vendidos</label>
            <select v-model="filtroMasVendidos" class="input-select" @change="cargarMasVendidos">
              <option v-for="n in [0,1,2,3,4,5,6,7,8,9,10]" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
        </div>

        <div v-if="masVendidos.length" class="mas-vendidos">
          <span class="mas-vendidos-title">Acceso rápido</span>
          <div class="mas-vendidos-chips">
            <button
              v-for="p in masVendidos"
              :key="'mv' + p.id"
              class="chip-mas-vendido"
              :class="{
                'chip-agotado': p.stock === 0,
                'chip-agregado': productoAgregadoId === p.id
              }"
              @click="agregarDirecto(p); feedbackAgregar(p)"
            >
              <span class="chip-nombre">{{ p.nombre }}</span>
            </button>
          </div>
        </div>
          </div>
        </div>

        <div class="productos-header">
          <span class="productos-title">Productos disponibles</span>
          <span class="productos-count">{{ productosFiltrados.length }}</span>
        </div>

        <div class="productos-lista" v-if="productosFiltrados.length > 0">
          <div
            v-for="producto in productosFiltrados"
            :key="producto.id"
            class="producto-item"
            :class="{
              'producto-seleccionado': productoEnCarrito(producto.id),
              'producto-sin-stock': producto.stock === 0,
              'producto-feedback': productoAgregadoId === producto.id
            }"
          >
            <div class="producto-info">
              <div class="producto-nombre-row">
                <h3 class="producto-nombre">{{ producto.nombre }}</h3>
                <span class="producto-categoria">{{ obtenerNombreCategoria(producto.categoria) }}</span>
              </div>
              <div class="producto-detalles">
                <span class="producto-precio">${{ parseFloat(producto.precio).toFixed(2) }}</span>
                <span class="producto-stock" :class="getStockClass(producto.stock)">{{ producto.stock }} uds</span>
              </div>
            </div>

            <div class="producto-acciones">
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
              <button
                @click="agregarAlCarrito(producto); feedbackAgregar(producto)"
                :disabled="!puedeAgregarAlCarrito(producto)"
                class="btn-agregar"
                :class="{
                  'btn-disabled': !puedeAgregarAlCarrito(producto),
                  'btn-agregado-ok': productoAgregadoId === producto.id
                }"
              >
                <svg v-if="productoAgregadoId === producto.id" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                {{ productoAgregadoId === producto.id ? 'Agregado' : obtenerTextoBoton(producto) }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="productos-vacio">
          <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <p>No se encontraron productos</p>
        </div>
      </section>

      <aside class="carrito-panel" :class="{ 'carrito-flash': carritoFlash }">
        <div class="panel-header">
          <div class="header-info">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="9" cy="21" r="1"></circle>
              <circle cx="20" cy="21" r="1"></circle>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
            </svg>
            <h2>Carrito</h2>
          </div>
          <div class="header-actions">
            <button @click="irAlListadoVentas" class="btn-ver-ventas" title="Ir al listado de ventas">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
              </svg>
              Ventas
            </button>
            <span class="carrito-badge" :key="badgeAnimKey">{{ carrito.length }}</span>
          </div>
        </div>

        <div v-if="carrito.length === 0" class="carrito-vacio">
          <div class="vacio-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="9" cy="21" r="1"></circle>
              <circle cx="20" cy="21" r="1"></circle>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
            </svg>
          </div>
          <h3>Carrito vacío</h3>
          <p>Agregá productos para comenzar</p>
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
                <button @click="quitarDelCarrito(item.producto.id)" class="btn-quitar" title="Quitar del carrito">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <button @click="vaciarCarrito" class="btn-vaciar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            Vaciar Carrito
          </button>
        </div>

        <div class="carrito-footer">
          <div class="footer-row">
            <span class="footer-label">Total</span>
            <span class="footer-total">${{ total.toFixed(2) }}</span>
          </div>
          <template v-if="carrito.length > 0">
            <button class="btn-continuar" @click="abrirCobro">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 12h14"></path>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
              Continuar al Cobro
            </button>
          </template>
          <div v-else class="btn-continuar-vacio">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            Seleccioná un producto para continuar
          </div>
        </div>
      </aside>
    </div>

    <!-- ============ PASO 2: COBRO ============ -->
    <transition name="panel-slide">
      <div v-if="paso === 'cobro'" class="cobro-panel">
        <div class="cobro-inner">
          <div class="cobro-header">
            <button @click="volverAlPasoVenta" class="cobro-back">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              Volver a la venta
            </button>

            <div class="cobro-steps">
              <div class="cobro-step" :class="(metodoPagoSeleccionado || esMixto) ? 'cobro-step-done' : 'cobro-step-active'">
                <span class="cobro-step-num">1</span>
                <span class="cobro-step-label">Método</span>
              </div>
              <span class="cobro-step-connector" :class="{ 'cobro-step-connector-done': pagoEfectuado }"></span>
              <div class="cobro-step" :class="!(metodoPagoSeleccionado || esMixto) ? '' : (pagoEfectuado ? 'cobro-step-done' : 'cobro-step-active')">
                <span class="cobro-step-num">2</span>
                <span class="cobro-step-label">Cobrar</span>
              </div>
              <span class="cobro-step-connector" :class="{ 'cobro-step-connector-done': pagoEfectuado }"></span>
              <div class="cobro-step" :class="{ 'cobro-step-active': pagoEfectuado }">
                <span class="cobro-step-num">3</span>
                <span class="cobro-step-label">Confirmar</span>
              </div>
            </div>
          </div>

          <div class="cobro-layout">
            <div class="cobro-left">
              <div class="cobro-body">
            <div class="form-group" ref="metodosPagoSection">
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
                  <div class="mp-icon" :class="esEfectivoMetodo(mp) ? 'mp-icon-efectivo' : 'mp-icon-mercadopago'">
                    <svg v-if="esEfectivoMetodo(mp)" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="5.6" y="4" width="14.4" height="8.6" rx="1.6" opacity="0.3" transform="rotate(-8 12.8 8.3)"></rect>
                      <rect x="4.6" y="7.8" width="14.4" height="8.6" rx="1.6" opacity="0.55" transform="rotate(7 11.8 12.1)"></rect>
                      <rect x="5.8" y="10.8" width="14.4" height="9" rx="1.9"></rect>
                      <circle cx="13" cy="15.3" r="1.7"></circle>
                      <path d="M13 12.2v.8M13 18.4v.8M9.9 15.3h.8M16.1 15.3h.8M10.9 13l.55.55M15.2 17.3l.55.55M15.2 13l-.55.55M10.9 17.3l-.55.55"></path>
                      <text x="13" y="16.6" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="4" font-weight="900" fill="currentColor" stroke="none">$</text>
                    </svg>
                    <svg v-else width="26" height="26" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="11.6" fill="currentColor"></circle>
                      <text x="12" y="15.7" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10.5" font-weight="900" fill="#ffffff" letter-spacing="-0.3">MP</text>
                    </svg>
                  </div>
                  <div class="mp-nombre">
                    <span v-if="esEfectivoMetodo(mp)">Efectivo</span>
                    <span v-else>Mercado Pago</span>
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
                  <div class="mp-icon mp-icon-mixto">
                    <svg width="30" height="24" viewBox="0 0 30 24" fill="none" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="10.5" cy="12" r="9.5" fill="#10b981"></circle>
                      <path d="M7 12.4l2.4 2.4 4.2-5" stroke="#ffffff" stroke-width="1.9"></path>
                      <circle cx="19.5" cy="12" r="9.5" fill="#009ee3"></circle>
                      <path d="M16 12.4l2.4 2.4 4.2-5" stroke="#ffffff" stroke-width="1.9"></path>
                    </svg>
                  </div>
                  <div class="mp-nombre">
                    <span>Mixto</span>
                    <small class="mp-subnombre">MP + Efectivo</small>
                  </div>
                  <div class="mp-radio">
                    <div class="radio-circle" :class="{ 'radio-active': esMixto }"></div>
                  </div>
                </div>
              </div>
            </div>

            <transition name="slide-fade">
              <div v-if="esEfectivo || esMixto" class="cobro-paso">
                <div v-if="esMixto" class="cobro-paso-titulo" :class="{ 'paso-titulo-done': efectivoRegistrado }">
                  <span class="paso-badge">{{ efectivoRegistrado ? '✓' : '1' }}</span>
                  <span class="paso-titulo-text">Pago en efectivo</span>
                  <span class="paso-monto">En efectivo: ${{ restanteEfectivo.toFixed(2) }}</span>
                </div>
                <div class="vuelto-section">
                  <div class="form-group">
                    <label>{{ esMixto ? 'Monto recibido en efectivo' : 'Monto recibido' }}</label>
                    <div class="monto-input-wrap">
                      <span class="monto-symbol">$</span>
                      <input
                        ref="montoInput"
                        type="number"
                        v-model.number="montoRecibido"
                        class="input-search input-monto-recibido"
                        placeholder="0.00"
                        min="0"
                        step="0.01"
                        :disabled="esMixto && efectivoRegistrado"
                        @keydown.enter="confirmarSiAlcanza"
                      />
                      <button
                        v-if="montoRecibido"
                        type="button"
                        class="btn-limpiar-monto"
                        :disabled="esMixto && efectivoRegistrado"
                        @click="montoRecibido = null"
                        title="Limpiar monto"
                        aria-label="Limpiar monto"
                      >
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <polyline points="3 6 5 6 21 6"></polyline>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                          <line x1="10" y1="11" x2="10" y2="17"></line>
                          <line x1="14" y1="11" x2="14" y2="17"></line>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div class="montos-rapidos">
                    <button
                      v-for="monto in montosRapidosEfectivo"
                      :key="monto"
                      class="btn-monto-rapido"
                      :disabled="esMixto && efectivoRegistrado"
                      @click="montoRecibido = monto"
                    >
                      ${{ monto.toLocaleString() }}
                    </button>
                    <button class="btn-monto-rapido btn-monto-exacto" :disabled="esMixto && efectivoRegistrado" @click="montoRecibido = objetivoEfectivo">
                      Exacto
                    </button>
                    <button v-if="esMixto" class="btn-monto-rapido btn-monto-mitad" @click="aplicarMitad" :disabled="pagoMixtoMpPagado || efectivoRegistrado">
                      Mitad
                    </button>
                  </div>
                  <div v-if="(!esMixto || efectivoCubreTotal) && montoRecibido && montoRecibido >= objetivoEfectivo" class="vuelto-display">
                    <span class="vuelto-label">Vuelto</span>
                    <span class="vuelto-valor">${{ vuelto.toFixed(2) }}</span>
                  </div>
                  <div v-else-if="(!esMixto || efectivoCubreTotal) && montoRecibido && montoRecibido < objetivoEfectivo" class="vuelto-faltante">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="8" x2="12" y2="12"></line>
                      <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <span>Faltan ${{ (objetivoEfectivo - montoRecibido).toFixed(2) }}</span>
                  </div>

                  <button
                    v-if="esMixto && !efectivoRegistrado"
                    class="btn-registrar-efectivo"
                    :disabled="!montoRecibido || montoRecibido <= 0"
                    @click="registrarEfectivo"
                  >
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    Registrar efectivo
                  </button>

                  <div v-if="esMixto && efectivoRegistrado" class="mixto-efectivo-resumen">
                    <div class="mixto-resumen-check">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    </div>
                    <div class="mixto-resumen-textos">
                      <strong>Efectivo registrado: ${{ montoRecibido.toFixed(2) }}</strong>
                      <small v-if="!efectivoCubreTotal">Saldo restante por Mercado Pago: <strong>${{ montoMP ? montoMP.toFixed(2) : '—' }}</strong> — cobralo en el Paso 2</small>
                      <small v-else>El efectivo cubre el total de <strong>${{ total.toFixed(2) }}</strong>. No hace falta Mercado Pago.</small>
                    </div>
                    <button class="btn-editar-efectivo" @click="editarEfectivo" :disabled="pagoEfectuado">Modificar</button>
                  </div>
                </div>
              </div>
            </transition>

            <transition name="slide-fade">
              <div v-if="(esMercadoPago && !esMixto) || (esMixto && efectivoRegistrado && !efectivoCubreTotal)" class="cobro-paso" ref="mpCobroSection">
                <div v-if="esMixto" class="cobro-paso-titulo">
                  <span class="paso-badge">2</span>
                  <span class="paso-titulo-text">Mercado Pago</span>
                </div>
                <div v-if="esMixto" class="resta-pagar-card">
                  <span class="resta-pagar-label">Saldo pendiente</span>
                  <span class="resta-pagar-valor">${{ montoMP ? montoMP.toFixed(2) : '—' }}</span>
                </div>
                <div class="datos-extra-pago">
                  <div v-if="pagoParcialMP" class="pago-parcial-resumen">
                    <div class="parcial-resumen-saldo-box">
                      <span class="parcial-saldo-label">Saldo pendiente</span>
                      <span class="parcial-saldo-valor">${{ saldoPendiente.toFixed(2) }}</span>
                    </div>
                    <div class="parcial-resumen-fila">
                      <span>Total</span>
                      <strong>${{ total.toFixed(2) }}</strong>
                    </div>
                    <div class="parcial-resumen-fila parcial-resumen-abonado">
                      <span>Abonado</span>
                      <strong>${{ pagoParcialMP.toFixed(2) }}</strong>
                    </div>
                  </div>

                <div class="mp-options">
                  <div class="mp-option-card" :class="{ 'mp-option-selected': mpSubOption === 'alias', 'mp-option-bloqueado': pagoEfectuado }" @click="seleccionarSubOpcion('alias')">
                    <div class="mp-option-content">
                      <div class="mp-option-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                          <circle cx="8.5" cy="7" r="4"></circle>
                          <polyline points="17 11 19 13 23 9"></polyline>
                        </svg>
                      </div>
                      <div class="mp-option-info">
                        <h4>Alias</h4>
                        <div v-if="mpSubOption === 'alias' && mp_alias" class="mp-alias-display">
                          <span class="mp-alias-label">Alias:</span>
                          <span class="mp-alias-value">{{ mp_alias }}</span>
                          <button @click.stop="copiarAlias" class="btn-copy-alias" title="Copiar alias">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                          </button>
                        </div>

                        <div v-if="mpSubOption === 'alias'" class="mp-confirmar-transferencia">
                          <button
                            v-if="mpPagoEstado !== 'confirmed'"
                            class="btn-confirmar-transferencia"
                            @click.stop="confirmarTransferencia"
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                              <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                            Registrar transferencia
                          </button>
                          <div v-else class="transferencia-confirmada">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                              <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                            <strong>Transferencia registrada</strong>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="mp-option-radio">
                      <div class="radio-circle" :class="{ 'radio-active': mpSubOption === 'alias' }"></div>
                    </div>
                  </div>

                  <div class="mp-option-card" :class="{ 'mp-option-selected': mpSubOption === 'qr', 'mp-option-bloqueado': pagoEfectuado }" @click="seleccionarSubOpcion('qr')">
                    <div class="mp-option-content">
                      <div class="mp-option-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <rect x="3" y="3" width="7" height="7"></rect>
                          <rect x="14" y="3" width="7" height="7"></rect>
                          <rect x="14" y="14" width="7" height="7"></rect>
                          <rect x="3" y="14" width="7" height="7"></rect>
                        </svg>
                      </div>
                      <div class="mp-option-info">
                        <h4>QR</h4>
                        <div v-if="mpSubOption === 'qr'" class="mp-qr-section">
                          <button @click.stop="generarQR" class="btn-generar-qr" :disabled="generandoQR || mpPagoEstado === 'confirmed'">
                            <template v-if="!generandoQR">
                              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                  <rect x="3" y="3" width="7" height="7"></rect>
                                  <rect x="14" y="3" width="7" height="7"></rect>
                                  <rect x="14" y="14" width="7" height="7"></rect>
                                  <rect x="3" y="14" width="7" height="7"></rect>
                                </svg>
                              </div>
                              <div class="pending-textos">
                                <span class="pending-title">Esperando pago...</span>
                              </div>
                            </div>
                            <div class="qr-actions">
                              <button class="btn-ampliar-qr" @click="qrFullscreen = true">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                  <polyline points="15 3 21 3 21 9"></polyline>
                                  <polyline points="9 21 3 21 3 15"></polyline>
                                  <line x1="21" y1="3" x2="14" y2="10"></line>
                                  <line x1="3" y1="21" x2="10" y2="14"></line>
                                </svg>
                                Pantalla completa
                              </button>
                              <button class="btn-regresar-qr" @click.stop="regresarDelQR" :disabled="mpPagoEstado === 'confirmed'">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
            </div>
            </transition>

                </div>
              </div>

            <div class="cobro-right">
              <div class="cobro-total-card">
                <div class="cobro-total">
                  <span class="total-label">TOTAL A PAGAR</span>
                  <span class="total-valor">${{ total.toFixed(2) }}</span>
                </div>

                <button
                  ref="btnConfirmar"
                  @click="registrarVenta"
                  :disabled="!formularioValido || procesandoVenta || carrito.length === 0"
                  class="btn-confirmar"
                  :class="{ 'btn-procesando': procesandoVenta, 'btn-confirmar-destacado': destacarConfirmar }"
                >
                  <template v-if="!procesandoVenta">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
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
        </div>
      </div>
    </transition>

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

      <transition name="fade-overlay">
        <div v-if="qrFullscreen && mpQrData" class="qr-fullscreen-overlay">
          <div class="qr-fullscreen-content">
            <div class="qr-fullscreen-header">
              <h2>Escaneá el código QR</h2>
              <p>Con la cámara de tu billetera virtual</p>
            </div>

            <div class="qr-fullscreen-amount">
              <span class="fs-amount-label">{{ esMixto ? 'Monto a transferir' : (pagoParcialMP ? 'Saldo pendiente a transferir' : 'Total a pagar') }}</span>
              <span class="fs-amount-valor">${{ montoQRMostrar.toFixed(2) }}</span>
              <span v-if="esMixto" class="fs-amount-extra">Resto ${{ restanteEfectivo.toFixed(2) }} en efectivo</span>
              <span v-else-if="pagoParcialMP" class="fs-amount-extra">Total ${{ total.toFixed(2) }} − ya abonado ${{ pagoParcialMP.toFixed(2) }}</span>
              <span v-if="pagoParcialMP" class="fs-amount-aviso">Este QR cobra únicamente el saldo pendiente</span>
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
              <span class="status-sub">Ahora confirmá la venta</span>
            </div>
            <div v-else class="qr-fullscreen-status status-wait">
              <div class="fs-pending-ring"></div>
              <span class="status-text">Esperando pago...</span>
              <span class="status-sub">Se actualiza automáticamente al recibir el pago</span>
            </div>

            <button class="btn-regresar" @click="manejarBotonFullscreen" :disabled="procesandoVenta">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              {{ mpPagoEstado === 'confirmed' ? 'Confirmar venta' : 'Cancelar' }}
            </button>
          </div>
        </div>
      </transition>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig'
import Swal from 'sweetalert2';
import AsignarEnvio from '@/components/AsignarEnvio.vue';
import { envioService } from '@/services/envioService';
import QrcodeVue from 'qrcode.vue'

// 🔥 El z-index del modal de SweetAlert se sube por CSS global (base.css):
//    .swal2-container { z-index: 100000 !important; }
//    (SweetAlert2 v11.26+ ya no acepta el parámetro zIndex, por eso va por CSS)
const API_BASE_URL = 'http://127.0.0.1:8000';

export default {
    name: 'RegistrarVenta',
    
    components: { AsignarEnvio, QrcodeVue },
    
    data() {
        return {
            productos: [],
            masVendidos: [],
            categorias: [],
            metodosPago: [],
            filtroNombre: '',
            filtroCategoria: '',
            filtroMasVendidos: 0,
            cantidades: {},
            carrito: [],
            procesandoVenta: false,
            destacarConfirmar: false,
            paso: 'venta',
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
            qrFullscreen: false,
            pagoMixto: false,
            montoMP: null,
            mensaje: '',
            mensajeTipo: 'success',
            montoRecibido: null,
            efectivoRegistrado: false,
            pagoParcialMP: null,
            productoAgregadoId: null,
            carritoFlash: false,
            badgeAnimKey: 0
        }
    },
    
    computed: {
        productosFiltrados() {
            return this.productos
                .filter(p => {
                    const nombreMatch = p.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase())
                    const categoriaMatch = this.filtroCategoria ? p.categoria === parseInt(this.filtroCategoria) : true 
                    return nombreMatch && categoriaMatch && p.estado === 'ACTIVO' 
                })
                .sort((a, b) => (b.stock > 0) - (a.stock > 0))
        },
        total() {
            const subtotal = this.carrito.reduce((acc, item) => acc + item.subtotal, 0)
            return this.envioData ? subtotal + this.envioData.costo_envio : subtotal
        },
        vuelto() {
            if (!this.montoRecibido) return 0;
            return Math.max(0, this.montoRecibido - this.objetivoEfectivo);
        },
        montosRapidosEfectivo() {
            return [1000, 10000, 15000, 20000, 30000];
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
        // 🔥 El efectivo recibido cubre el 100% del total: no hace falta Mercado Pago
        efectivoCubreTotal() {
            return this.esMixto && this.montoRecibido && this.montoRecibido >= this.total;
        },
        restanteEfectivo() {
            if (!this.esMixto || !this.montoMP) return this.total;
            return Math.max(0, this.total - this.montoMP);
        },
        objetivoEfectivo() {
            return this.esMixto ? this.restanteEfectivo : this.total;
        },
        montoQRMostrar() {
            if (this.esMixto) return this.montoMP || 0;
            if (this.pagoParcialMP) return this.saldoPendiente;
            return this.total;
        },
        saldoPendiente() {
            return this.redondear2(Math.max(0, this.total - (this.pagoParcialMP || 0)));
        },
        
        // 🔥 ¿El usuario ya cargó algo en el modo mixto? Si no, no hace falta confirmación al salir
        mixtoTieneDatos() {
            if (this.mpQrData || this.mpPagoEstado) return true;
            if (this.efectivoRegistrado) return true;
            if (this.montoRecibido) return true;
            if (this.montoMP != null) return true;
            return false;
        },
        
        // 🔥 BLOQUEO UNA VEZ QUE EL PAGO YA SE EFECTUÓ
        pagoEfectuado() {
            if (this.esMixto) {
                const efectivoCubierto = !!(this.montoRecibido && this.restanteEfectivo > 0 && this.montoRecibido >= this.restanteEfectivo);
                return efectivoCubierto && this.pagoMixtoMpPagado;
            }
            if (this.esEfectivo) {
                return !!(this.montoRecibido && this.montoRecibido >= this.total);
            }
            if (this.esMercadoPago && this.mpSubOption === 'qr') {
                return this.mpPagoEstado === 'confirmed';
            }
            if (this.esMercadoPago && this.mpSubOption === 'alias') {
                return this.mpPagoEstado === 'confirmed';
            }
            return false;
        },
        pagoMixtoMpPagado() {
            if (!this.esMixto) return false;
            return this.mpPagoEstado === 'confirmed';
        },
        
        // 🔥 ¿Hay datos cargados en el formulario de pago? Si los hay, al cambiar de método hay que confirmar
        hayDatosPagoIngresados() {
            if (this.esMixto) return this.mixtoTieneDatos;
            return !!(this.montoRecibido || this.mpSubOption || this.mpQrData || this.mpPagoEstado || this.pagoParcialMP || this.datosVenta.codigo_transaccion);
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

            if (this.esMercadoPago && !this.esMixto && (!this.mpSubOption || this.mpPagoEstado !== 'confirmed')) {
                return false;
            }

            if (this.esEfectivo && !this.esMixto && (!this.montoRecibido || this.montoRecibido < this.total)) {
                return false;
            }

            if (this.esMixto) {
                if (this.efectivoCubreTotal) return true;
                if (!this.efectivoRegistrado) return false;
                if (!this.montoMPValido) return false;
                if (!this.pagoMixtoMpPagado) return false;
                if (!this.montoRecibido || this.montoRecibido < this.restanteEfectivo) return false;
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
        },
        total(nuevo, viejo) {
            if (this.mpQrData && nuevo !== viejo) {
                this.mpQrData = null;
                this.mpPagoEstado = null;
                this.detenerPollingPago();
                this.mostrarMensaje('El total cambió. Volvé a generar el QR', 'warning');
            }
            if (this.esMixto) {
                if (this.montoRecibido) {
                    const resto = this.redondear2(this.total - this.montoRecibido);
                    this.montoMP = resto > 0 ? resto : null;
                } else if (this.montoMP != null && this.montoMP > this.total) {
                    this.montoMP = null;
                }
            }
        },
        montoMP(nuevo, viejo) {
            if (this.mpQrData && nuevo !== viejo) {
                this.mpQrData = null;
                this.mpPagoEstado = null;
                this.detenerPollingPago();
                this.mostrarMensaje('El monto a cobrar con Mercado Pago cambió. Volvé a generar el QR', 'warning');
            }
        },
        mpQrData(nuevo) {
            if (!nuevo) this.qrFullscreen = false;
        },
        montoRecibido(nuevo) {
            if (this.esMixto) {
                if (nuevo && nuevo > 0) {
                    const resto = this.redondear2(this.total - nuevo);
                    this.montoMP = resto > 0 ? resto : null;
                } else {
                    this.montoMP = null;
                }
                if (this.mpPagoEstado === 'confirmed' && nuevo && nuevo >= this.restanteEfectivo) {
                    this.dirigirAlBotonConfirmar();
                }
            }
        },
        esEfectivo(nuevo) {
            if (nuevo) {
                this.$nextTick(() => {
                    if (this.$refs.montoInput) this.$refs.montoInput.focus();
                });
            }
        }
    },
    
    methods: {
        feedbackAgregar(producto) {
            if (!producto || producto.stock === 0) return;
            this.productoAgregadoId = producto.id;
            this.carritoFlash = true;
            this.badgeAnimKey++;
            clearTimeout(this._feedbackTimer);
            this._feedbackTimer = setTimeout(() => {
                this.productoAgregadoId = null;
                this.carritoFlash = false;
            }, 600);
        },
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
                color: 'var(--text-primary)',
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

        irAlListadoVentas() {
            if (this.carrito.length > 0) {
                Swal.fire({
                    icon: 'warning',
                    title: '¿Salir al listado de ventas?',
                    text: 'El carrito actual se perderá',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, salir',
                    cancelButtonText: 'Quedarme',
                    confirmButtonColor: '#ef4444',
                    cancelButtonColor: '#6c757d',
                    reverseButtons: true,
                    allowOutsideClick: false
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.navegarAListado();
                    }
                });
                return;
            }
            this.navegarAListado();
        },

        abrirCobro() {
            if (this.carrito.length === 0) {
                this.mostrarMensaje('Agregá al menos un producto para cobrar', 'warning');
                return;
            }
            if (!this.datosVenta.medio_pago) {
                const efectivo = this.metodosPago.find(m => (m.tipo || '').toUpperCase().includes('EFECTIVO'));
                if (efectivo) this.datosVenta.medio_pago = efectivo.id;
            }
            this.paso = 'cobro';
        },

        volverAlPasoVenta() {
            if (this.pagoEfectuado) {
                this.mostrarMensaje('El pago ya se efectuó. Confirmá la venta para continuar.', 'warning');
                return;
            }
            this.paso = 'venta';
        },

        async procesarVentaExitosa(ventaData) {
            Swal.close();
            this.limpiarFormulario(); 
            await this.cargarProductos(); 
            this.cargarMasVendidos();
            sessionStorage.setItem('ultima_venta_pos', ventaData.id);

            const totalConfirmado = parseFloat(ventaData.total);
            
            const result = await Swal.fire({
                title: '¡Venta Registrada Exitosamente!',
                html: `
                    <div style="text-align: left; margin: 20px 0;">
                        <div style="background: var(--text-primary); padding: 15px; border-radius: 10px; border-left: 4px solid #059669; color: #1f2937;">
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
            }
            // La venta queda registrada: nos quedamos en el Punto de Venta listos para la próxima
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

        redondear2(valor) {
            return Math.round((parseFloat(valor) || 0) * 100) / 100;
        },

        salirModoMixto() {
            this.pagoMixto = false;
            this.montoMP = null;
            this.montoRecibido = null;
            this.efectivoRegistrado = false;
            this.mpSubOption = null;
            this.mpQrData = null;
            this.mpPagoEstado = null;
            this.qrFullscreen = false;
            this.detenerPollingPago();
            this.datosVenta.codigo_transaccion = '';
        },

        confirmarCambioMetodo(onConfirm, textoCustom = null) {
            const texto = textoCustom || (this.esMixto
                ? 'Los datos ingresados para el pago mixto podrán perderse o recalcularse.'
                : 'Dependiendo del método seleccionado, algunos datos ingresados podrán recalcularse o descartarse.');
            Swal.fire({
                icon: 'question',
                title: '¿Está seguro de que desea cambiar el método de pago?',
                text: texto,
                showCancelButton: true,
                confirmButtonText: 'Sí, cambiar método',
                cancelButtonText: 'No, seguir',
                confirmButtonColor: '#ef4444',
                cancelButtonColor: '#6c757d',
                reverseButtons: true,
                allowOutsideClick: false
            }).then((result) => {
                if (result.isConfirmed) onConfirm();
            });
        },

        // 🔥 Alias: el cajero marca que el cliente ya transfirió → habilita "Confirmar Venta"
        // (mismo estado que el QR: mpPagoEstado === 'confirmed')
        confirmarTransferencia() {
            if (this.pagoEfectuado) return;
            if (!this.esMercadoPago) return;
            if (this.esMixto && !this.efectivoRegistrado) {
                this.mostrarMensaje('Primero registrá el efectivo recibido en el Paso 1', 'warning');
                return;
            }
            this.mpPagoEstado = 'confirmed';
            this.detenerPollingPago();
            this.mostrarMensaje('Transferencia registrada. Confirmá la venta para finalizarla', 'success');
            this.dirigirAlBotonConfirmar();
        },

        esMercadoPagoMetodo(mp) {
            const tipo = (mp.tipo || '').toUpperCase();
            const nombre = (mp.nombre || '').toUpperCase();
            return tipo === 'MERCADOPAGO' || tipo === 'MERCADO_PAGO' || nombre.includes('MERCADO');
        },

        salirMixtoConservandoParcial() {
            if (this.pagoMixtoMpPagado && this.montoMP) {
                this.pagoParcialMP = this.redondear2(this.montoMP);
            } else {
                this.pagoParcialMP = null;
            }
            this.salirModoMixto();
        },

        aplicarMitad() {
            const mitad = this.redondear2(this.total / 2);
            this.montoMP = mitad;
            this.montoRecibido = mitad;
        },

        // 🔥 Paso 1 del mixto: se registra el efectivo recibido y recién ahí se habilita Mercado Pago
        registrarEfectivo() {
            if (!this.esMixto) return;
            if (!this.montoRecibido || this.montoRecibido <= 0) {
                this.mostrarMensaje('Ingresá el monto de efectivo recibido para registrarlo', 'warning');
                return;
            }
            // 🔥 Cálculo automático del saldo pendiente: saldo MP = total − efectivo registrado
            const resto = this.redondear2(this.total - this.montoRecibido);
            this.montoMP = resto > 0 ? resto : null;
            this.efectivoRegistrado = true;
            if (this.efectivoCubreTotal) {
                this.mostrarMensaje('Total cubierto con efectivo. Confirmá la venta para finalizarla', 'success');
                return;
            }
            this.$nextTick(() => {
                const seccion = this.$refs.mpCobroSection;
                if (seccion && seccion.scrollIntoView) {
                    seccion.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        },

        editarEfectivo() {
            this.efectivoRegistrado = false;
            if (this.mpQrData || this.mpPagoEstado) {
                this.mpQrData = null;
                this.mpPagoEstado = null;
                this.detenerPollingPago();
                this.mostrarMensaje('El efectivo cambió: volvé a generar el QR con el nuevo saldo', 'warning');
            }
        },

        seleccionarMetodo(mp) {
            const destinoMP = this.esMercadoPagoMetodo(mp);
            // 🔥 Mixto → Mercado Pago: si el MP ya está confirmado se permite el cambio
            // conservando ese pago; el nuevo QR/alias cobra solo la diferencia (total − ya pagado)
            const mixtoAMercadoPago = this.esMixto && destinoMP && this.pagoMixtoMpPagado;

            if (this.pagoEfectuado && !mixtoAMercadoPago) {
                Swal.fire({
                    icon: 'warning',
                    title: 'El pago ya se efectuó',
                    text: 'No podés cambiar el método de pago porque ya se registró el cobro de esta venta.',
                    confirmButtonColor: '#ef4444',
                    confirmButtonText: 'Entendido'
                });
                return;
            }
            if (!this.esMixto && this.datosVenta.medio_pago === mp.id) return;

            const aplicar = () => {
                if (this.esMixto) {
                    if (destinoMP && this.pagoMixtoMpPagado && this.montoMP) {
                        this.pagoParcialMP = this.redondear2(this.montoMP);
                    } else {
                        this.pagoParcialMP = null;
                    }
                    this.salirModoMixto();
                } else {
                    this.pagoParcialMP = null;
                    this.pagoMixto = false;
                    this.montoMP = null;
                    this.efectivoRegistrado = false;
                }
                this.montoRecibido = null;
                this.mpSubOption = null;
                this.mpQrData = null;
                this.mpPagoEstado = null;
                this.detenerPollingPago();
                this.datosVenta.codigo_transaccion = '';
                this.datosVenta.medio_pago = mp.id;
            };

            if (this.hayDatosPagoIngresados) {
                this.confirmarCambioMetodo(aplicar, mixtoAMercadoPago
                    ? 'El pago de Mercado Pago ya realizado se conservará y solo se cobrará la diferencia restante. Los datos de efectivo se descartarán.'
                    : null);
            } else {
                aplicar();
            }
        },

        seleccionarMixto() {
            if (this.pagoEfectuado && !(this.esMixto && this.pagoMixtoMpPagado)) {
                Swal.fire({
                    icon: 'warning',
                    title: 'El pago ya se efectuó',
                    text: 'No podés cambiar el método de pago porque ya se registró el cobro de esta venta.',
                    confirmButtonColor: '#ef4444',
                    confirmButtonText: 'Entendido'
                });
                return;
            }
            // 🔥 Si ya está en modo mixto, la tarjeta funciona como "salir" → continúa como Mercado Pago.
            // Si el MP ya está confirmado, ese pago se conserva y solo se vuelve a cobrar la diferencia.
            if (this.esMixto) {
                if (this.mixtoTieneDatos) {
                    const conservaParcial = this.pagoMixtoMpPagado;
                    this.confirmarCambioMetodo(() => {
                        this.salirMixtoConservandoParcial();
                    }, conservaParcial
                        ? 'El pago de Mercado Pago ya realizado se conservará y solo se cobrará la diferencia restante. Los datos de efectivo se descartarán.'
                        : null);
                } else {
                    this.salirMixtoConservandoParcial();
                }
                return;
            }
            if (!this.hayMetodosMixto) return;
            this.pagoMixto = true;
            this.montoMP = null;
            this.pagoParcialMP = null;
            this.datosVenta.medio_pago = this.metodoMP.id;
            this.mpSubOption = null;
            this.mpQrData = null;
            this.mpPagoEstado = null;
            this.montoRecibido = null;
            this.efectivoRegistrado = false;
            this.detenerPollingPago();
            this.datosVenta.codigo_transaccion = '';
        },

        seleccionarSubOpcion(opcion) {
            if (this.pagoEfectuado) {
                Swal.fire({
                    icon: 'warning',
                    title: 'El pago ya se efectuó',
                    text: 'No podés cambiar el tipo de cobro porque ya se registró el pago de esta venta.',
                    confirmButtonColor: '#ef4444',
                    confirmButtonText: 'Entendido'
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

        async cargarMasVendidos() {
            // Con límite 0 no se muestran accesos rápidos
            if (!this.filtroMasVendidos || this.filtroMasVendidos <= 0) {
                this.masVendidos = [];
                return;
            }
            try {
                const res = await axios.get(`${API_BASE_URL}/api/productos/mas-vendidos/?limite=${this.filtroMasVendidos}`);
                const lista = Array.isArray(res.data) ? res.data : [];
                this.masVendidos = lista.map(prod => ({
                    ...prod,
                    stock: parseInt(prod.stock_actual) || 0,
                    precio: parseFloat(prod.precio) || 0,
                }));
            } catch (err) {
                console.error("Error al cargar productos más vendidos:", err);
                this.masVendidos = [];
            }

            // Si no hay historial de ventas, mostramos productos por defecto
            if (this.masVendidos.length === 0) {
                await this.cargarMasVendidosPorDefecto();
            }
        },

        async cargarMasVendidosPorDefecto() {
            try {
                const res = await axios.get(`${API_BASE_URL}/usuarios/api/productos/`);
                const lista = Array.isArray(res.data) ? res.data : [];
                const activos = lista
                    .filter(p => String(p.estado).toUpperCase() === 'ACTIVO' && parseInt(p.stock_actual) > 0)
                    .sort((a, b) => (parseInt(b.stock_actual) || 0) - (parseInt(a.stock_actual) || 0))
                    .slice(0, this.filtroMasVendidos);
                this.masVendidos = activos.map(prod => ({
                    ...prod,
                    stock: parseInt(prod.stock_actual) || 0,
                    precio: parseFloat(prod.precio) || 0,
                }));
            } catch (err) {
                console.error("Error al cargar productos por defecto:", err);
                this.masVendidos = [];
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

        agregarDirecto(producto) {
            if (!producto || producto.stock === 0) return;
            const enCarrito = this.cantidadEnCarrito(producto.id);
            if (enCarrito >= producto.stock) {
                this.mostrarMensaje('Ya agregaste todo el stock disponible de este producto', 'warning');
                return;
            }
            this.cantidades[producto.id] = 1;
            this.agregarAlCarrito(producto);
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

          if (this.esMixto) {
            if (this.efectivoCubreTotal) {
              return true;
            }
            if (!this.efectivoRegistrado) {
              this.mostrarMensaje('Debe registrar el efectivo recibido en el Paso 1', 'warning');
              return false;
            }
            if (!this.montoMPValido) {
              this.mostrarMensaje('El monto con Mercado Pago debe ser mayor a $0 y menor al total', 'warning');
              return false;
            }
            if (!this.pagoMixtoMpPagado) {
              this.mostrarMensaje('Debe cobrar el saldo con Mercado Pago (generar el QR o registrar la transferencia por alias)', 'warning');
              return false;
            }
            if (!this.montoRecibido || this.montoRecibido < this.restanteEfectivo) {
              this.mostrarMensaje('El efectivo recibido no cubre el resto de la venta', 'warning');
              return false;
            }
            return true;
          }

          if (this.esEfectivo) {
            return true;
          }

          if (this.esMercadoPago && !this.mpSubOption) {
            this.mostrarMensaje('Debe elegir entre alias o QR para cobrar con Mercado Pago', 'warning');
            return false;
          }

          if (this.esMercadoPago && this.mpPagoEstado !== 'confirmed') {
            this.mostrarMensaje('Debe confirmar el pago con Mercado Pago (generar el QR o registrar la transferencia por alias)', 'warning');
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
            let medioPagoFinal = parseInt(this.datosVenta.medio_pago);
            let pagoMixtoPayload = false;
            let montoMPPayload = null;
            let montoEfectivoPayload = null;

            if (this.esMixto) {
                if (this.efectivoCubreTotal) {
                    // 🔥 El efectivo cubre el 100% del total: se cobra solo en efectivo, sin Mercado Pago
                    const efectivo = this.metodoEfectivoObj;
                    if (efectivo) medioPagoFinal = parseInt(efectivo.id);
                    pagoMixtoPayload = false;
                    montoEfectivoPayload = this.redondear2(this.total);
                } else {
                    entidadFinal = this.mpSubOption === 'qr' ? 'MERCADOPAGO_QR' : 'MERCADOPAGO_ALIAS';
                    pagoMixtoPayload = true;
                    montoMPPayload = this.redondear2(this.montoMP);
                    montoEfectivoPayload = this.redondear2(this.restanteEfectivo);
                }
            } else if (this.esMercadoPago) {
                entidadFinal = this.mpSubOption === 'qr' ? 'MERCADOPAGO_QR' : 'MERCADOPAGO_ALIAS';
            } else if (this.esTransferencia) {
                entidadFinal = this.datosVenta.entidad_pago;
            }

            const payload = { 
                total: parseFloat(this.total),
                tipo: 'PRODUCTO', 
                medio_pago: medioPagoFinal,
                detalles,
                cliente: null,
                usuario: this.datosVenta.usuario,
                entidad_pago: entidadFinal,
                codigo_transaccion: this.datosVenta.codigo_transaccion || null
            };

            if (pagoMixtoPayload) {
                payload.pago_mixto = true;
                payload.monto_mp = montoMPPayload;
                payload.monto_efectivo = montoEfectivoPayload;
            }

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
            if (this.efectivoCubreTotal) {
                this.mostrarMensaje('El total ya está cubierto con el efectivo. No hace falta generar QR', 'info');
                return;
            }
            const montoQR = this.esMixto ? this.montoMP : (this.pagoParcialMP ? this.saldoPendiente : this.total);
            if (!montoQR || montoQR <= 0) {
                this.mostrarMensaje('Ingresá un monto válido para generar el QR', 'warning');
                return;
            }
            this.generandoQR = true;
            this.mpPagoEstado = null;
            this.detenerPollingPago();
            try {
                const res = await axios.post(`${API_BASE_URL}/api/generar-qr-temporal/`, {
                    monto: montoQR,
                    title: 'Venta de productos - HairSoft'
                });
                if (res.data.status === 'ok') {
                    this.mpQrData = res.data;
                    this.mpPagoEstado = 'pending';
                    this.iniciarPollingPago(res.data.uid);
                    this.qrFullscreen = true;
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
                        this.dirigirAlBotonConfirmar();
                    }
                } catch (err) {
                    console.error("Error al verificar pago:", err);
                }
            }, 3000);
        },

        // 🔥 Cuando el pago se confirma, cierra el fullscreen y lleva al botón "Confirmar Venta"
        manejarBotonFullscreen() {
            if (this.procesandoVenta) return;
            if (this.mpPagoEstado === 'confirmed') {
                this.dirigirAlBotonConfirmar();
            } else {
                this.regresarDelQR();
            }
        },

        dirigirAlBotonConfirmar() {
            if (this.procesandoVenta) return;
            this.qrFullscreen = false;
            this.paso = 'cobro';
            this.destacarConfirmar = true;
            this.$nextTick(() => {
                const btn = this.$refs.btnConfirmar;
                if (btn && btn.scrollIntoView) {
                    btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
            setTimeout(() => {
                this.destacarConfirmar = false;
            }, 5000);
        },

        // 🔥 Cancela el QR (solo si el pago aún no se efectuó) y vuelve a la selección de métodos
        regresarDelQR() {
            if (this.mpPagoEstado === 'confirmed' || this.pagoEfectuado) {
                this.mostrarMensaje('El pago ya se efectuó, no se puede cancelar el QR', 'warning');
                return;
            }
            this.qrFullscreen = false;
            this.mpSubOption = null;
            this.mpQrData = null;
            this.mpPagoEstado = null;
            this.datosVenta.codigo_transaccion = '';
            this.detenerPollingPago();
            this.mostrarMensaje('QR cancelado. Elegí otro método de pago.', 'info');
            this.paso = 'cobro';
            this.$nextTick(() => {
                const seccion = this.$refs.metodosPagoSection;
                if (seccion && seccion.scrollIntoView) {
                    seccion.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        },

        detenerPollingPago() {
            if (this.mpPagoInterval) {
                clearInterval(this.mpPagoInterval);
                this.mpPagoInterval = null;
            }
        },

        confirmarSiAlcanza() {
            if (!this.esEfectivo && !this.esMixto) return;
            if (this.esMixto) {
                if (this.efectivoCubreTotal) {
                    this.registrarVenta();
                    return;
                }
                if (!this.efectivoRegistrado) {
                    this.registrarEfectivo();
                    return;
                }
                this.mostrarMensaje('Cobrá el saldo restante con Mercado Pago (Paso 2)', 'info');
                return;
            }
            if (this.montoRecibido && this.montoRecibido >= this.objetivoEfectivo) {
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
            this.qrFullscreen = false;
            this.pagoMixto = false;
            this.montoMP = null;
            this.montoRecibido = null;
            this.efectivoRegistrado = false;
            this.pagoParcialMP = null;
            this.detenerPollingPago();
            this.paso = 'venta';
        }
    },

    beforeUnmount() {
        this.detenerPollingPago();
    },

    mounted() {
        this.verificarCajaAbierta();

        this.cargarProductos();
        this.cargarMasVendidos();
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
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: var(--bg-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  position: relative;
}

.venta-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7);
  z-index: 5;
}

/* ============================================
   PASO 1: GRID
   ============================================ */
.pos-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.22fr) minmax(380px, 1fr);
  gap: 22px;
  padding: 18px 4px 40px;
  max-width: 1700px;
  margin: 0 auto;
  height: 100%;
}

/* ---------- Panel de productos ---------- */
.productos-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.filtros-panel {
  position: sticky;
  top: 20px;
  z-index: 10;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.filtros-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 16px 16px 14px;
}

.search-row {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 0.8fr);
  gap: 14px;
}

.btn-limpiar-filtros {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-limpiar-filtros:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
  background: var(--hover-bg);
}

.btn-limpiar-filtros:active {
  transform: translateY(1px);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.input-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-tertiary);
  pointer-events: none;
  z-index: 1;
}

.input-search-icon {
  padding-left: 40px !important;
}

.input-search,
.input-select {
  width: 100%;
  height: 44px;
  padding: 0 16px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  transition: all 0.2s ease;
  line-height: 1;
}

.input-search:focus,
.input-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
}

.input-search::placeholder {
  color: var(--text-tertiary);
}

.input-select option {
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* ---------- Más vendidos ---------- */
.mas-vendidos {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mas-vendidos-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.mas-vendidos-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-mas-vendido {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: linear-gradient(180deg, var(--bg-primary), var(--bg-secondary));
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 8px 13px;
  cursor: pointer;
  font-family: inherit;
  color: var(--text-primary);
  box-shadow: 0 1px 2px rgba(2, 6, 23, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  transition: border-color 0.15s ease, background 0.15s ease, transform 0.12s ease, box-shadow 0.15s ease;
}

.chip-mas-vendido:focus-visible {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.25);
}

.chip-mas-vendido:hover {
  border-color: var(--accent-color);
  background: linear-gradient(180deg, var(--hover-bg), var(--active-bg));
  color: var(--accent-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.22);
}

.chip-mas-vendido:active {
  transform: translateY(0) scale(0.97);
  box-shadow: 0 1px 3px rgba(2, 6, 23, 0.1);
}

.chip-mas-vendido.chip-agregado {
  border-color: var(--accent-color);
  background: var(--active-bg);
  color: var(--accent-color);
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.28);
  animation: chip-pop 0.3s ease;
}

.chip-nombre {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.chip-agotado {
  opacity: 0.65;
  cursor: not-allowed;
  border-color: rgba(245, 158, 11, 0.45);
}

.chip-agotado:hover,
.chip-agotado:active {
  transform: none;
  border-color: rgba(245, 158, 11, 0.45);
  background: var(--bg-primary);
  box-shadow: none;
}

/* ---------- Lista de productos ---------- */
.productos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 14px;
  padding: 14px 4px 10px;
}

.productos-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.productos-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 22px;
  padding: 0 9px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.productos-lista {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 6px;
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.25) transparent;
}

.productos-lista::-webkit-scrollbar {
  width: 3px;
}

.productos-lista::-webkit-scrollbar-track {
  background: transparent;
}

.productos-lista::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.25);
  border-radius: 3px;
}

.productos-lista::-webkit-scrollbar-thumb:hover {
  background: rgba(14, 165, 233, 0.5);
}

.producto-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 6px 10px;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.producto-item:hover {
  border-color: rgba(14, 165, 233, 0.45);
  background: var(--hover-bg);
  box-shadow: 0 4px 14px rgba(2, 6, 23, 0.12);
  transform: translateY(-1px);
}

.producto-seleccionado {
  border-color: var(--accent-color);
  background: var(--active-bg);
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.12);
}

.producto-item.producto-feedback {
  animation: producto-feedback 0.45s ease;
}

.producto-sin-stock {
  opacity: 0.9;
  background: rgba(245, 158, 11, 0.09);
  border-color: rgba(245, 158, 11, 0.4);
}

.producto-sin-stock:hover {
  border-color: rgba(245, 158, 11, 0.65);
  background: rgba(245, 158, 11, 0.14);
}

.producto-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.producto-nombre-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.producto-nombre {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.producto-categoria {
  flex-shrink: 0;
  background: rgba(148, 163, 184, 0.08);
  color: var(--text-tertiary);
  border: 1px solid rgba(148, 163, 184, 0.18);
  padding: 0 5px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 600;
  line-height: 1.7;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.producto-detalles {
  display: flex;
  gap: 8px;
  align-items: center;
}

.producto-precio {
  font-size: 17px;
  font-weight: 800;
  color: var(--accent-color);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.producto-stock {
  font-size: 10px;
  font-weight: 500;
  opacity: 0.7;
  font-variant-numeric: tabular-nums;
}

.stock-disponible {
  color: #34d399;
}

.stock-bajo {
  color: #fbbf24;
}

.stock-agotado {
  color: #fbbf24;
}

.producto-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.qty-stepper {
  display: flex;
  align-items: center;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-primary);
}

.qty-btn {
  width: 24px;
  height: 26px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  line-height: 1;
}

.qty-btn:hover:not(:disabled) {
  background: var(--accent-color);
  color: white;
}

.qty-btn:disabled {
  color: var(--border-color);
  cursor: not-allowed;
}

.qty-value {
  min-width: 24px;
  text-align: center;
  font-size: 13px;
  font-weight: 800;
  color: var(--text-primary);
  background: var(--bg-secondary);
  padding: 2px 0;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
  font-variant-numeric: tabular-nums;
}

.btn-agregar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 4px 9px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-agregar:hover:not(.btn-disabled) {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
  transform: translateY(-1px);
}

.btn-agregar:active:not(.btn-disabled) {
  transform: translateY(0);
}

.btn-agregar.btn-disabled {
  background: #26314a;
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.btn-agregar.btn-agregado-ok,
.btn-agregar.btn-agregado-ok:hover:not(.btn-disabled) {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
}

.btn-agregar.btn-agregado-ok {
  animation: btn-ok 0.4s ease;
}

.productos-vacio {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.productos-vacio svg {
  margin-bottom: 10px;
  color: var(--border-color);
}

.productos-vacio p {
  font-size: 14px;
  color: var(--text-tertiary);
}

/* ---------- Carrito ---------- */
.carrito-panel {
  align-self: start;
  height: auto;
  max-height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.carrito-panel.carrito-flash {
  animation: carrito-flash 0.6s ease;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
}

.header-info h2 {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.carrito-badge {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);
  min-width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  animation: badge-pop 0.4s ease;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-ver-ventas {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  padding: 7px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.btn-ver-ventas:hover {
  border-color: var(--accent-color);
  color: var(--text-primary);
  background: var(--hover-bg);
}

.carrito-vacio {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 20px;
}

.vacio-icon {
  color: var(--border-color);
  margin-bottom: 8px;
}

.carrito-vacio h3 {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.carrito-vacio p {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

.carrito-contenido {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.carrito-items {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding: 8px 20px;
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.28) transparent;
}

.carrito-items::-webkit-scrollbar {
  width: 3px;
}

.carrito-items::-webkit-scrollbar-track {
  background: transparent;
}

.carrito-items::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.25);
  border-radius: 3px;
}

.carrito-items::-webkit-scrollbar-thumb:hover {
  background: rgba(14, 165, 233, 0.5);
}

.carrito-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 2px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.carrito-item:last-child {
  border-bottom: none;
}

.item-left {
  flex: 1;
  min-width: 0;
}

.item-left h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-detalles {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.item-cantidad {
  font-weight: 700;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-variant-numeric: tabular-nums;
}

.item-sep {
  color: var(--border-color);
}

.item-precio-unitario {
  color: var(--text-tertiary);
}

.item-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.item-subtotal {
  font-size: 17px;
  font-weight: 800;
  color: var(--text-primary);
  min-width: 66px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.btn-quitar {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  width: 28px;
  height: 28px;
  border-radius: 7px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0.6;
}

.carrito-item:hover .btn-quitar {
  opacity: 1;
}

.btn-quitar:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.btn-vaciar {
  flex-shrink: 0;
  margin: 10px 20px 8px;
  background: rgba(239, 68, 68, 0.04);
  border: 1px solid rgba(239, 68, 68, 0.28);
  color: rgba(248, 113, 113, 0.9);
  padding: 7px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  transition: all 0.25s ease;
}

.btn-vaciar:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.5);
  color: #fca5a5;
}

.btn-vaciar:active {
  transform: translateY(1px);
}

.carrito-footer {
  flex-shrink: 0;
  border-top: 1px solid var(--border-color);
  padding: 16px 20px 20px;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.footer-total {
  font-size: 30px;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.btn-continuar {
  width: 100%;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 16px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 10px 26px rgba(14, 165, 233, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn-continuar:hover:not(:disabled) {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.btn-continuar:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 6px 18px rgba(14, 165, 233, 0.4);
}

.btn-continuar:disabled {
  background: #26314a;
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.btn-continuar-vacio {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border: 1px dashed var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 600;
  line-height: 1.3;
  text-align: center;
}

.btn-continuar-vacio svg {
  flex-shrink: 0;
  color: var(--text-tertiary);
}

/* ---------- Microanimaciones de feedback ---------- */
@keyframes badge-pop {
  0% { transform: scale(1); }
  45% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

@keyframes carrito-flash {
  0% {
    box-shadow: inset 0 0 0 2px rgba(14, 165, 233, 0);
    background-color: transparent;
  }
  30% {
    box-shadow: inset 0 0 0 2px rgba(14, 165, 233, 0.4);
    background-color: rgba(14, 165, 233, 0.07);
  }
  100% {
    box-shadow: inset 0 0 0 2px rgba(14, 165, 233, 0);
    background-color: transparent;
  }
}

@keyframes producto-feedback {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(14, 165, 233, 0);
    background-color: transparent;
  }
  35% {
    transform: scale(1.02);
    box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.22), 0 6px 18px rgba(14, 165, 233, 0.14);
    background-color: var(--active-bg);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(14, 165, 233, 0);
    background-color: transparent;
  }
}

@keyframes btn-ok {
  0% { transform: scale(1); }
  45% { transform: scale(1.08); }
  100% { transform: scale(1); }
}

@keyframes chip-pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.07); }
  100% { transform: scale(1); }
}

/* ============================================
   PASO 2: PANEL DE COBRO
   ============================================ */
.cobro-panel {
  position: fixed;
  inset: 0;
  z-index: 1400;
  background: rgba(2, 6, 23, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

.cobro-inner {
  width: min(1200px, 100%);
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.5);
  padding: 14px 20px 20px;
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.28) transparent;
}

.cobro-inner::-webkit-scrollbar {
  width: 3px;
}

.cobro-inner::-webkit-scrollbar-track {
  background: transparent;
}

.cobro-inner::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.25);
  border-radius: 3px;
}

.cobro-inner::-webkit-scrollbar-thumb:hover {
  background: rgba(14, 165, 233, 0.5);
}

.cobro-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 2px 0 10px;
}

.cobro-steps {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.cobro-step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  opacity: 0.55;
  transition: opacity 0.3s ease, border-color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.cobro-step-num {
  position: relative;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--border-color);
  color: var(--bg-primary);
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.cobro-step-label {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.cobro-step-active {
  opacity: 1;
  border-color: rgba(14, 165, 233, 0.6);
  background: rgba(14, 165, 233, 0.1);
  box-shadow: 0 2px 12px rgba(14, 165, 233, 0.2);
}

.cobro-step-active .cobro-step-num {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: #fff;
  box-shadow: 0 2px 6px rgba(14, 165, 233, 0.4);
}

.cobro-step-done {
  opacity: 1;
  border-color: rgba(16, 185, 129, 0.5);
  background: rgba(16, 185, 129, 0.1);
}

.cobro-step-done .cobro-step-num {
  background: linear-gradient(135deg, #34d399, #10b981);
  color: #fff;
}

.cobro-step-done .cobro-step-num::after {
  content: '✓';
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #34d399, #10b981);
  border-radius: 50%;
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
  animation: pop-in 0.25s ease;
}

.cobro-step-connector {
  width: 26px;
  height: 2px;
  border-radius: 2px;
  background: var(--border-color);
  transition: background 0.3s ease;
}

.cobro-step-connector-done {
  background: linear-gradient(90deg, #34d399, #10b981);
}

.cobro-back {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 10px 16px;
  border-radius: 12px;
  flex-shrink: 0;
}

.cobro-back:hover {
  color: var(--text-primary);
  border-color: var(--accent-color);
  background: var(--hover-bg);
  transform: translateX(-2px);
}

.cobro-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cobro-title-main {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.cobro-title-sub {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-tertiary);
}

.cobro-total-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(160deg, var(--bg-primary) 0%, var(--bg-secondary) 120%);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  padding: 24px 20px 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: var(--shadow-lg);
}

.cobro-total-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #009ee3);
}

.cobro-total {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-color);
}

.cobro-total .total-label {
  font-size: 11px;
  font-weight: 800;
  color: var(--text-tertiary);
  letter-spacing: 2px;
}

.cobro-total .total-valor {
  font-size: 42px;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1.08;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 18px rgba(14, 165, 233, 0.15);
}

.cobro-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(300px, 0.85fr);
  gap: 18px;
  align-items: start;
}

.cobro-left {
  min-width: 0;
  padding-top: 24px;
}

.cobro-right {
  position: sticky;
  top: 12px;
}

.cobro-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-divider {
  height: 1px;
  background: var(--border-color);
}

.cobro-paso {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cobro-paso-titulo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.paso-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(14, 165, 233, 0.15);
  border: 1px solid rgba(14, 165, 233, 0.4);
  color: #7dd3fc;
  font-size: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.paso-titulo-text {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.paso-monto {
  margin-left: auto;
  font-size: 13px;
  font-weight: 800;
  color: #34d399;
}

.paso-titulo-done .paso-badge {
  background: rgba(16, 185, 129, 0.18);
  border-color: rgba(16, 185, 129, 0.55);
  color: #34d399;
}

.paso-titulo-done .paso-titulo-text {
  color: #34d399;
}

.resta-pagar-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin: 14px 0 16px;
  padding: 18px 16px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.22), rgba(245, 158, 11, 0.05));
  border: 1px solid rgba(245, 158, 11, 0.55);
  box-shadow: 0 6px 26px rgba(245, 158, 11, 0.18), inset 0 0 50px rgba(245, 158, 11, 0.05);
}

.resta-pagar-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: #fcd34d;
}

.resta-pagar-valor {
  font-size: 48px;
  font-weight: 900;
  color: #fbbf24;
  line-height: 1.05;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
  text-shadow: 0 0 24px rgba(251, 191, 36, 0.35);
  animation: saldo-glow 2.6s ease-in-out infinite;
}

.pago-parcial-resumen {
  background: linear-gradient(160deg, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0.04));
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 16px;
  padding: 16px 16px 10px;
}

.parcial-resumen-saldo-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 18px 12px;
  margin-bottom: 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.24), rgba(245, 158, 11, 0.06));
  border: 1px solid rgba(245, 158, 11, 0.55);
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.16), inset 0 0 40px rgba(245, 158, 11, 0.04);
}

.parcial-saldo-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: #fcd34d;
}

.parcial-saldo-valor {
  font-size: 46px;
  font-weight: 900;
  color: #fbbf24;
  line-height: 1.05;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
  animation: saldo-glow 2.6s ease-in-out infinite;
}

.parcial-resumen-fila {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 2px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.parcial-resumen-fila strong {
  color: var(--text-secondary);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.parcial-resumen-fila.parcial-resumen-abonado strong {
  color: #34d399;
}

@keyframes saldo-glow {
  0%, 100% { text-shadow: 0 0 30px rgba(251, 191, 36, 0.3); }
  50% { text-shadow: 0 0 46px rgba(251, 191, 36, 0.55); }
}

/* ============================================
   TRANSITIONS
   ============================================ */
.panel-slide-enter-active {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.32s ease;
}
.panel-slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.panel-slide-enter-from,
.panel-slide-leave-to {
  transform: scale(0.92) translateY(12px);
  opacity: 0;
}

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
.vuelto-section .form-group label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
}

.montos-rapidos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.btn-monto-rapido {
  flex: 1;
  min-width: 62px;
  background: linear-gradient(180deg, var(--bg-primary), var(--bg-secondary));
  border: 1px solid var(--border-hover);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
  padding: 14px 6px;
  border-radius: 11px;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  font-variant-numeric: tabular-nums;
  box-shadow: 0 3px 0 rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: transform 0.08s ease, box-shadow 0.08s ease, background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.btn-monto-rapido:hover:not(:disabled) {
  border-color: var(--accent-color);
  background: linear-gradient(180deg, var(--hover-bg), var(--bg-secondary));
}

.btn-monto-rapido:active:not(:disabled) {
  transform: translateY(2px);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.28);
}

.btn-monto-rapido:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-monto-exacto {
  flex-grow: 1.25;
  min-width: 100px;
  background: linear-gradient(180deg, #38bdf8, #0284c7);
  border-color: #0369a1;
  border-top-color: rgba(255, 255, 255, 0.35);
  color: #fff;
  box-shadow: 0 3px 0 rgba(3, 105, 161, 0.6), 0 6px 18px rgba(14, 165, 233, 0.35);
}

.btn-monto-exacto:hover:not(:disabled) {
  background: linear-gradient(180deg, #0ea5e9, #0369a1);
  color: #fff;
  border-color: #075985;
  box-shadow: 0 4px 0 rgba(3, 105, 161, 0.6), 0 8px 22px rgba(14, 165, 233, 0.45);
}

.monto-input-wrap {
  position: relative;
}

.monto-input-wrap .monto-symbol {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  font-size: 26px;
  font-weight: 800;
  color: var(--text-tertiary);
  pointer-events: none;
  font-variant-numeric: tabular-nums;
}

.input-monto-recibido {
  font-size: 34px;
  font-weight: 800;
  text-align: right;
  padding: 8px 46px 8px 44px !important;
  height: 62px;
  border-radius: 14px;
  letter-spacing: 0.5px;
  font-variant-numeric: tabular-nums;
  background: var(--bg-primary);
  -moz-appearance: textfield;
  appearance: textfield;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-monto-recibido::-webkit-outer-spin-button,
.input-monto-recibido::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-monto-recibido:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15), 0 8px 24px rgba(14, 165, 233, 0.12);
}

.input-monto-recibido:disabled {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.45);
  color: #34d399;
  cursor: not-allowed;
}

.btn-limpiar-monto {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-limpiar-monto:hover:not(:disabled) {
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.5);
  background: rgba(239, 68, 68, 0.1);
}

.btn-limpiar-monto:active:not(:disabled) {
  transform: translateY(-50%) scale(0.9);
}

.btn-limpiar-monto:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.vuelto-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 12px;
  padding: 12px 18px;
  margin-top: 10px;
  animation: estado-pop 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.vuelto-label {
  font-size: 12px;
  font-weight: 700;
  color: #34d399;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.vuelto-valor {
  font-size: 30px;
  font-weight: 800;
  color: #34d399;
  line-height: 1.1;
}

.vuelto-faltante {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  margin-top: 10px;
  padding: 12px 18px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 12px;
  color: #f87171;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  animation: estado-pop 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.vuelto-faltante span {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0;
}

.vuelto-titulo {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: 12px;
  margin-bottom: 14px;
}

.vuelto-titulo-label {
  font-size: 13px;
  font-weight: 700;
  color: #fbbf24;
}

.vuelto-titulo-monto {
  font-size: 20px;
  font-weight: 800;
  color: #fbbf24;
}

/* ============================================
   MÉTODOS DE PAGO
   ============================================ */
.metodo-pago-opciones {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.metodo-pago-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 62px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 10px 14px;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.metodo-pago-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 14px;
  bottom: 14px;
  width: 3px;
  border-radius: 3px;
  background: linear-gradient(180deg, #0ea5e9, #0284c7);
  opacity: 0;
  transform: scaleY(0.4);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.metodo-pago-card:hover:not(.metodo-pago-bloqueado) {
  border-color: var(--border-hover);
  background: var(--hover-bg);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
}

.metodo-pago-card:active {
  transform: translateY(0) scale(0.99);
}

.metodo-pago-selected {
  border-color: rgba(14, 165, 233, 0.7);
  background: rgba(14, 165, 233, 0.08);
  box-shadow: 0 6px 18px rgba(14, 165, 233, 0.14);
}

.metodo-pago-selected::before {
  opacity: 1;
  transform: scaleY(1);
}

.mp-icon {
  width: 42px;
  height: 42px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.mp-icon-efectivo {
  color: #34d399;
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.mp-icon-mercadopago {
  color: #009ee3;
  background: rgba(0, 158, 227, 0.1);
  border-color: rgba(0, 158, 227, 0.3);
}

.mp-icon-mixto {
  width: auto;
  min-width: 42px;
  padding: 0 4px;
  border: none;
  background: transparent;
}

.metodo-pago-selected .mp-icon-efectivo {
  background: rgba(16, 185, 129, 0.18);
  border-color: rgba(16, 185, 129, 0.6);
}

.metodo-pago-selected .mp-icon-mercadopago {
  background: rgba(0, 158, 227, 0.18);
  border-color: rgba(0, 158, 227, 0.6);
}

.mp-nombre {
  flex: 1;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.mp-subnombre {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-tertiary);
}

.metodo-pago-bloqueado,
.mp-option-bloqueado {
  opacity: 0.7;
  cursor: not-allowed;
}

.mp-radio {
  flex-shrink: 0;
}

.radio-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
  position: relative;
}

.radio-circle::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent-color);
  transform: translate(-50%, -50%) scale(0);
  transition: all 0.3s ease;
}

.radio-active {
  border-color: var(--accent-color);
}

.radio-active::after {
  transform: translate(-50%, -50%) scale(1);
}

/* ============================================
   PAGO MIXTO (MP + EFECTIVO)
   ============================================ */
.btn-monto-mitad {
  background: linear-gradient(180deg, rgba(14, 165, 233, 0.22), rgba(14, 165, 233, 0.08));
  border-color: rgba(14, 165, 233, 0.45);
  color: #7dd3fc;
  box-shadow: 0 3px 0 rgba(2, 6, 23, 0.35);
}

.btn-monto-mitad:hover:not(:disabled) {
  background: rgba(14, 165, 233, 0.3);
  color: #bae6fd;
}

.btn-monto-mitad:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-registrar-efectivo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 12px;
  padding: 12px 18px;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
}

.btn-registrar-efectivo:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn-registrar-efectivo:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mixto-efectivo-resumen {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 12px;
  padding: 14px 16px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 12px;
  animation: estado-pop 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.mixto-resumen-check {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.mixto-resumen-textos {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.mixto-resumen-textos strong {
  color: #34d399;
}

.mixto-resumen-textos small {
  color: var(--text-secondary);
  font-size: 12px;
}

.btn-editar-efectivo {
  flex-shrink: 0;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid rgba(14, 165, 233, 0.4);
  border-radius: 8px;
  color: #7dd3fc;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-editar-efectivo:hover:not(:disabled) {
  background: rgba(14, 165, 233, 0.12);
}

.btn-editar-efectivo:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================
   MERCADO PAGO SUB-OPTIONS
   ============================================ */
.datos-extra-pago {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mp-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mp-option-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.25s ease, background 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}

.mp-option-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 3px;
  background: linear-gradient(180deg, #0ea5e9, #0284c7);
  opacity: 0;
  transform: scaleY(0.4);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.mp-option-card:hover:not(.mp-option-bloqueado) {
  border-color: var(--border-hover);
  background: var(--hover-bg);
  transform: translateY(-1px);
}

.mp-option-selected {
  border-color: rgba(14, 165, 233, 0.7);
  background: rgba(14, 165, 233, 0.08);
  box-shadow: 0 6px 18px rgba(14, 165, 233, 0.12);
}

.mp-option-selected::before {
  opacity: 1;
  transform: scaleY(1);
}

.mp-option-content {
  display: flex;
  gap: 12px;
  flex: 1;
  align-items: flex-start;
}

.mp-option-icon {
  width: 34px;
  height: 34px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.mp-option-selected .mp-option-icon {
  background: rgba(14, 165, 233, 0.15);
  color: #38bdf8;
  border-color: rgba(14, 165, 233, 0.5);
}

.mp-option-info {
  flex: 1;
}

.mp-option-info h4 {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 2px 0;
}

.mp-option-info p {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0 0 6px 0;
}

.mp-option-radio {
  padding-top: 5px;
  flex-shrink: 0;
}

.mp-alias-display {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-primary);
  padding: 8px 8px 8px 12px;
  border-radius: 10px;
  border: 1px solid rgba(0, 158, 227, 0.35);
  margin-bottom: 10px;
}

.mp-alias-label {
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.mp-alias-value {
  flex: 1;
  font-size: 13px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 0.3px;
  font-family: 'Courier New', monospace;
}

.btn-copy-alias {
  background: rgba(0, 158, 227, 0.12);
  border: 1px solid rgba(0, 158, 227, 0.35);
  color: #38bdf8;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-copy-alias:hover {
  background: #009ee3;
  color: white;
  border-color: #009ee3;
}

.mp-confirmar-transferencia {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.btn-confirmar-transferencia {
  width: 100%;
  justify-content: center;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.25s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
}

.btn-confirmar-transferencia:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
}

.btn-confirmar-transferencia:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-confirmar-transferencia:disabled {
  background: #26314a;
  cursor: not-allowed;
  box-shadow: none;
}

.transferencia-confirmada {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(16, 185, 129, 0.14);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
  font-size: 13px;
  font-weight: 800;
  animation: estado-pop 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.transferencia-confirmada svg {
  flex-shrink: 0;
}

@keyframes estado-pop {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(4px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.btn-generar-qr {
  width: 100%;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.25s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.3);
}

.btn-generar-qr:hover:not(:disabled) {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4);
}

.btn-generar-qr:disabled {
  background: #26314a;
  color: var(--text-tertiary);
  cursor: not-allowed;
  box-shadow: none;
}

.qr-display {
  margin-top: 12px;
  text-align: center;
  padding: 14px;
  background: var(--bg-primary);
  border-radius: 14px;
  border: 1px solid var(--border-color);
}

.qr-display-inner {
  display: inline-block;
  background: white;
  padding: 8px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

.btn-ampliar-qr {
  margin-top: 12px;
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-hover);
  color: var(--text-secondary);
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-ampliar-qr:hover {
  border-color: var(--accent-color);
  color: #7dd3fc;
  background: var(--hover-bg);
}

.qr-actions {
  display: flex;
  gap: 8px;
  width: 100%;
}

.qr-actions .btn-ampliar-qr {
  margin-top: 12px;
  flex: 1;
}

.btn-regresar-qr {
  margin-top: 12px;
  flex: 1;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #f87171;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-regresar-qr:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}

.btn-regresar-qr:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qr-pago-pendiente {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 14px;
  padding: 16px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: 14px;
}

.pending-ring {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fbbf24;
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
  border: 2px solid rgba(251, 191, 36, 0.3);
  border-bottom-color: transparent;
  animation: spin 1.6s linear infinite reverse;
}

.pending-textos {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.pending-title {
  font-size: 14px;
  font-weight: 700;
  color: #fbbf24;
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
  background: rgba(16, 185, 129, 0.14);
  border: 1px solid rgba(16, 185, 129, 0.45);
  border-radius: 12px;
  color: #34d399;
  font-weight: 800;
  font-size: 14px;
  animation: estado-pop 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

/* ============================================
   BOTÓN CONFIRMAR
   ============================================ */
.btn-confirmar {
  position: relative;
  width: 100%;
  background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 55%, #0369a1 100%);
  color: white;
  border: none;
  padding: 17px 16px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 900;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: transform 0.15s ease, background 0.3s ease, box-shadow 0.3s ease;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  box-shadow: 0 10px 26px rgba(14, 165, 233, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.25);
}

.btn-confirmar:hover:not(:disabled) {
  background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%);
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.btn-confirmar:active:not(:disabled) {
  transform: scale(0.985);
}

.btn-confirmar:disabled {
  background: linear-gradient(180deg, #1e293b, #0f172a);
  color: #64748b;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.9;
}

.btn-confirmar.btn-procesando {
  background: var(--border-color);
  box-shadow: none;
}

.btn-confirmar:not(:disabled) {
  animation: confirmar-alive 2.4s ease-in-out infinite;
}

.btn-confirmar.btn-confirmar-destacado {
  animation: confirmar-pulse 0.9s ease-in-out infinite;
}

@keyframes confirmar-alive {
  0%, 100% {
    box-shadow: 0 10px 26px rgba(14, 165, 233, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  }
  50% {
    box-shadow: 0 10px 32px rgba(14, 165, 233, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  }
}

@keyframes confirmar-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.55);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 0 14px rgba(14, 165, 233, 0);
    transform: scale(1.03);
  }
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
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
  z-index: 3000;
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
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border-left-color: #0369a1;
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
   FULLSCREEN QR OVERLAY
   ============================================ */
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
  gap: 22px;
  padding: 40px 24px;
  max-width: 560px;
  width: 100%;
}

.qr-fullscreen-header {
  text-align: center;
}

.qr-fullscreen-header h2 {
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 6px 0;
  letter-spacing: 1px;
  text-transform: uppercase;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}

.qr-fullscreen-header p {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

.qr-fullscreen-amount {
  background: #111827;
  border: 1px solid #27272a;
  border-radius: 16px;
  padding: 14px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.fs-amount-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.fs-amount-valor {
  font-size: 34px;
  font-weight: 800;
  color: white;
  line-height: 1.1;
}

.fs-amount-extra {
  font-size: 13px;
  font-weight: 600;
  color: #fbbf24;
  margin-top: 4px;
}

.fs-amount-aviso {
  margin-top: 10px;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.qr-fullscreen-box {
  background: white;
  padding: 20px;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.qr-box-white {
  background: white;
}

.qr-fullscreen-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 18px 32px;
  border-radius: 16px;
  min-width: 300px;
}

.qr-fullscreen-status.status-wait {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.qr-fullscreen-status.status-ok {
  background: rgba(16, 185, 129, 0.14);
  border: 1px solid rgba(16, 185, 129, 0.45);
}

.fs-pending-ring {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 3px solid rgba(245, 158, 11, 0.25);
  border-top-color: #f59e0b;
  animation: spin 0.9s linear infinite;
}

.status-check {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #10b981;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pop-in 0.3s ease;
}

.status-text {
  font-size: 18px;
  font-weight: 800;
  color: white;
}

.status-wait .status-text {
  color: #fbbf24;
}

.status-sub {
  font-size: 13px;
  color: var(--text-secondary);
}

.btn-regresar {
  margin-top: 6px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 14px 36px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.25s ease;
}

.btn-regresar:hover {
  background: var(--border-color);
  border-color: var(--text-tertiary);
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
  0% { transform: scale(0.4); opacity: 0; }
  80% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1100px) {
  .venta-page {
    height: auto;
    overflow: visible;
  }

  .pos-grid {
    grid-template-columns: 1fr;
    height: auto;
  }

  .productos-panel {
    height: auto;
    overflow: visible;
  }

  .productos-lista {
    flex: none;
    max-height: calc(100vh - 250px);
  }

  .carrito-panel {
    height: auto;
  }

  .cobro-layout {
    grid-template-columns: 1fr;
  }

  .cobro-right {
    position: static;
  }
}

@media (max-width: 768px) {
  .pos-grid {
    padding: 16px 16px 32px;
    gap: 16px;
  }

  .search-row {
    grid-template-columns: 1fr;
  }

  .cobro-inner {
    padding: 18px 16px 48px;
  }

  .cobro-step-label {
    display: none;
  }

  .cobro-step {
    padding: 5px 10px;
  }

  .cobro-step-connector {
    width: 14px;
  }

  .metodo-pago-opciones {
    grid-template-columns: 1fr;
  }

  .input-monto-recibido {
    font-size: 28px;
    height: 56px;
  }

  .producto-item {
    flex-direction: column;
    align-items: stretch;
  }

  .producto-acciones {
    justify-content: flex-end;
  }
}
</style>