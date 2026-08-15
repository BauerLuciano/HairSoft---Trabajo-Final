<template>
  <div class="checkout-page">
    <div class="checkout-container">

      <div class="page-header">
        <span class="header-eyebrow">Último paso de tu compra</span>
        <h1>Finalizá tu compra</h1>
        <p>Revisá tu pedido, elegí cómo recibirlo y completá el pago.</p>
      </div>

      <div class="checkout-grid">

        <div class="form-column">

          <section class="checkout-section">
            <h2 class="section-title"><span class="step-number">1</span> Método de entrega</h2>
            <div class="delivery-cards">
              <label class="delivery-card" :class="{ active: tipoEntrega === 'RETIRO' }">
                <input type="radio" v-model="tipoEntrega" value="RETIRO" hidden>
                <span class="delivery-radio" :class="{ 'radio-checked': tipoEntrega === 'RETIRO' }">
                  <span v-if="tipoEntrega === 'RETIRO'" class="radio-dot"></span>
                </span>
                <span class="delivery-icon">
                  <Store :size="22" />
                </span>
                <div class="card-content">
                  <span class="card-title">Retiro en el local</span>
                  <span class="card-desc">Pasás a buscarlo por la peluquería, sin esperas.</span>
                </div>
                <div class="card-price free">Gratis</div>
              </label>

              <label class="delivery-card" :class="{ active: tipoEntrega === 'MOTO' }">
                <input type="radio" v-model="tipoEntrega" value="MOTO" hidden>
                <span class="delivery-radio" :class="{ 'radio-checked': tipoEntrega === 'MOTO' }">
                  <span v-if="tipoEntrega === 'MOTO'" class="radio-dot"></span>
                </span>
                <span class="delivery-icon">
                  <Bike :size="22" />
                </span>
                <div class="card-content">
                  <span class="card-title">Moto mandado</span>
                  <span class="card-desc">Te lo llevamos hasta tu domicilio.</span>
                </div>
                <div class="card-price" :class="{ 'price-calculated': costoEnvioCalculado > 0 && dentroCobertura, 'price-error': !dentroCobertura && costoEnvioCalculado > 0 }">
                  <span v-if="!dentroCobertura && costoEnvioCalculado > 0">No disponible</span>
                  <span v-else>{{ costoEnvioCalculado > 0 ? `$${costoEnvioCalculado.toLocaleString('es-AR')}` : 'A calcular' }}</span>
                </div>
              </label>
            </div>
          </section>

          <transition name="fade">
            <section v-if="tipoEntrega === 'RETIRO'" class="checkout-section retiro-section">
              <h2 class="section-title"><span class="step-number">2</span> Retiro en el local</h2>
              <div class="retiro-card">
                <span class="retiro-icon"><Store :size="22" /></span>
                <div class="retiro-info">
                  <strong>Retirás tu pedido en la peluquería</strong>
                  <span v-if="localDireccion">{{ localDireccion }}</span>
                  <span v-else>Te avisamos cuando tu pedido esté listo para retirar.</span>
                </div>
                <span class="retiro-badge">Gratis</span>
              </div>
            </section>
          </transition>

          <transition name="fade">
            <section v-if="tipoEntrega === 'MOTO'" class="checkout-section">
              <h2 class="section-title"><span class="step-number">2</span> Dirección de entrega</h2>

              <div v-if="radioCoberturaKm" class="cobertura-info">
                <span class="cobertura-icon"><Bike :size="18" /></span>
                <div class="cobertura-text">
                  <strong>Cobertura de Moto Mandado</strong>
                  <span>Realizamos entregas dentro de un radio de hasta {{ radioCoberturaDisplay }} km desde nuestro local.</span>
                </div>
              </div>

              <div class="sub-block">
                <h3 class="sub-title">¿Dónde querés recibirlo?</h3>

                <div class="gps-btn-container">
                  <button class="btn-gps" @click="obtenerGPS" :disabled="buscandoGPS">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7z"></path>
                      <circle cx="12" cy="9" r="2.5"></circle>
                    </svg>
                    <span>{{ buscandoGPS ? 'Obteniendo ubicación...' : 'Usar mi ubicación GPS' }}</span>
                  </button>
                </div>

                <div class="search-divider"><span>o</span></div>

                <div class="address-search-container">
                  <div class="address-search-input-wrapper">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-addr-icon">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input
                      v-model="busquedaDir"
                      type="text"
                      class="filter-input address-search-input"
                      placeholder="Buscá tu dirección (ej. calle y número)"
                      @input="onBuscarDireccion"
                      @keydown.enter="confirmarDireccion"
                      @blur="onBlurBusqueda"
                    />
                    <div v-if="buscandoDir" class="search-spinner"></div>
                  </div>
                  <div v-if="sugerencias.length > 0" class="suggestions-dropdown">
                    <div
                      v-for="sug in sugerencias"
                      :key="sug.lat + ',' + sug.lon"
                      class="suggestion-item"
                      @mousedown.prevent
                      @click="seleccionarDireccion(sug)"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="suggestion-icon">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                      </svg>
                      <span class="suggestion-text">
                        <span class="suggestion-title">{{ sug.titulo || sug.display_name }}</span>
                        <span v-if="sug.subtitulo" class="suggestion-sub">{{ sug.subtitulo }}</span>
                      </span>
                    </div>
                  </div>
                  <div v-else-if="sinResultados" class="no-results-msg">
                    No encontramos esa dirección. Probá con otra búsqueda o usá el GPS / el mapa.
                  </div>
                </div>

                <div v-if="errorGPS" class="error-msg">{{ errorGPS }}</div>
              </div>

              <div class="sub-block">
                <h3 class="sub-title">Confirmá la ubicación</h3>

                <div class="map-hint">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                  </svg>
                  <span>Hacé clic en el mapa o arrastrá el marcador para ajustar la dirección.</span>
                </div>

                <div v-if="localCargando" class="map-loading">Cargando mapa...</div>

                <div v-else class="map-wrapper">
                  <l-map
                    ref="mapRef"
                    :zoom="zoom"
                    :center="mapCenter"
                    @click="colocarMarcador"
                    style="height: 300px; width: 100%; border-radius: 12px;"
                  >
                    <l-tile-layer
                      v-for="tile in tilesBase" :key="tile.name"
                      :name="tile.name"
                      :visible="tile.visible"
                      :url="tile.url"
                      :attribution="tile.att"
                      layer-type="base"
                    ></l-tile-layer>
                    <l-control-layers></l-control-layers>

                    <l-marker
                      :lat-lng="[localLat, localLng]"
                      :icon="localIcon"
                    >
                      <l-tooltip>Peluquería</l-tooltip>
                    </l-marker>

                    <l-marker
                      v-if="deliveryLatLng"
                      :lat-lng="deliveryLatLng"
                      :icon="deliveryIcon"
                      draggable
                      @dragend="marcadorArrastrado"
                    >
                      <l-tooltip>Dirección de entrega</l-tooltip>
                    </l-marker>

                    <l-polyline
                      v-if="deliveryLatLng"
                      :lat-lngs="rutaCoords || [[localLat, localLng], deliveryLatLng]"
                      color="#0ea5e9"
                      :weight="rutaCoords ? 4 : 3"
                      :dash-array="rutaCoords ? null : '8, 6'"
                    ></l-polyline>
                  </l-map>
                </div>

                <transition name="fade">
                  <div v-if="deliveryLatLng && direccionDetectada" class="address-detected-card">
                    <div class="address-detected-header">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      <span>Dirección detectada</span>
                      <span v-if="confianzaInfo" class="confianza-chip" :class="confianzaInfo.clase">{{ confianzaInfo.texto }}</span>
                    </div>
                    <p class="address-detected-text">{{ direccionDetectada }}</p>
                    <div v-if="detalleDireccion" class="address-detected-details">
                      <span><strong>Calle:</strong> {{ detalleDireccion.calle }}</span>
                      <span v-if="detalleDireccion.altura"><strong>Altura:</strong> {{ detalleDireccion.altura }}</span>
                      <span v-if="detalleDireccion.ciudad"><strong>Ciudad:</strong> {{ detalleDireccion.ciudad }}</span>
                      <span v-if="detalleDireccion.provincia"><strong>Provincia:</strong> {{ detalleDireccion.provincia }}</span>
                    </div>

                    <div v-if="confianzaDireccion === 'parcial'" class="address-confirm-warning">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#b45309" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
                      </svg>
                      <span>Encontramos la calle, pero no pudimos determinar automáticamente el punto exacto de la altura. Arrastrá el marcador para confirmar la ubicación antes de confirmar el pedido.</span>
                    </div>

                    <div v-if="deliveryLatLng && !calculandoCosto && distanciaKm > 0" class="delivery-status">
                      <span class="status-item"><strong>Distancia al local:</strong> {{ distanciaDisplay }} km</span>
                      <span class="status-badge" :class="dentroCobertura ? 'ok' : 'bad'">
                        <svg v-if="dentroCobertura" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                        {{ dentroCobertura ? 'Cobertura disponible' : 'Fuera de cobertura' }}
                      </span>
                    </div>
                  </div>
                </transition>

                <div class="coords-display" v-if="deliveryLatLng">
                  <small>Lat: {{ deliveryLatLng[0].toFixed(4) }}, Lng: {{ deliveryLatLng[1].toFixed(4) }}</small>
                </div>

                <div v-if="!deliveryLatLng && !calculandoCosto && !localCargando" class="empty-state">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5">
                    <path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7z"></path>
                    <circle cx="12" cy="9" r="2.5"></circle>
                  </svg>
                  <p>Usá el GPS o hacé clic en el mapa para indicar dónde querés recibir el pedido.</p>
                </div>
              </div>

              <div class="sub-block">
                <h3 class="sub-title">Información del envío</h3>

                <div v-if="calculandoCosto" class="costo-loading">
                  <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                  </svg>
                  Calculando costo de envío...
                </div>

                <div v-if="!dentroCobertura && costoEnvioCalculado > 0 && !calculandoCosto" class="cobertura-warning">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>
                  <span>{{ fueraCoberturaMsg }}</span>
                </div>

                 <div v-if="costoEnvioCalculado > 0 && !calculandoCosto" class="costo-card">
                   <div class="costo-item">
                     <span class="costo-label">Distancia</span>
                     <span class="costo-value">{{ distanciaKm }} km</span>
                   </div>
                   <div class="costo-divider"></div>
                   <div class="costo-item">
                     <span class="costo-label">Costo de envío</span>
                     <span v-if="dentroCobertura" class="costo-value costo-price">${{ costoEnvioCalculado.toLocaleString('es-AR') }}</span>
                     <span v-else class="costo-value" style="color: #ef4444; font-weight: 700; font-size: 0.95rem;">Envío no disponible</span>
                   </div>
                 </div>

                <div v-if="errorCalculo" class="error-msg">{{ errorCalculo }}</div>
              </div>

              <div class="sub-block">
                <h3 class="sub-title">Observaciones <span class="optional">(opcional)</span></h3>
                <transition name="fade">
                  <div v-if="deliveryLatLng" class="obs-section">
                    <label for="obs">¿Tenés alguna indicación para el repartidor?</label>
                    <textarea
                      id="obs"
                      v-model="observaciones"
                      class="modern-textarea"
                      rows="2"
                      placeholder="Ej: Casa color blanca, timbre lado izquierdo, portón verde..."
                    ></textarea>
                    <small class="obs-hint">Ayudá al motomandado a encontrar la dirección.</small>
                  </div>
                </transition>
              </div>

            </section>
          </transition>

        </div>

        <div class="summary-column">
          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">
                <span class="summary-icon"><ShoppingBag :size="18" /></span>
                <h3>Tu pedido</h3>
              </div>
              <span v-if="usuarioNombre" class="comprando-como">
                Comprando como <strong>{{ usuarioNombre }}</strong>
              </span>
            </div>

            <div v-if="cartStore.items.length === 0" class="empty-cart-msg">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" style="margin: 0 auto 10px; display: block;">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
              <p>Tu carrito está vacío.</p>
            </div>

            <div v-else class="summary-items-list">
              <div v-for="item in cartStore.items" :key="item.id" class="summary-item">
                <div class="item-info">
                  <span class="item-qty">{{ item.cantidad }}x</span>
                  <span class="item-name">{{ item.nombre }}</span>
                </div>
                <span class="item-price">${{ (item.precio * item.cantidad).toLocaleString('es-AR') }}</span>
              </div>
            </div>

            <div class="divider"></div>

            <div class="summary-totals">
              <div class="total-row">
                <span>Subtotal</span>
                <span>${{ cartStore.precioTotal.toLocaleString('es-AR') }}</span>
              </div>
              <div class="total-row shipping">
                <span>Envío</span>
                <span v-if="tipoEntrega === 'MOTO' && calculandoCosto" class="shipping-loading">
                  <svg class="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
                  Calculando...
                </span>
                <span v-else-if="tipoEntrega === 'MOTO' && !dentroCobertura && costoEnvioCalculado > 0" class="shipping-fuera">
                  Fuera de cobertura
                </span>
                <span v-else-if="tipoEntrega === 'MOTO' && costoEnvioCalculado > 0" class="shipping-cost">${{ costoEnvioCalculado.toLocaleString('es-AR') }}</span>
                <span v-else-if="tipoEntrega === 'RETIRO'" class="shipping-free">Gratis</span>
                <span v-else class="shipping-none">—</span>
              </div>

              <div class="total-final-box">
                <div class="total-final-label">Total a pagar</div>
                <div class="total-final-amount">${{ totalFinal.toLocaleString('es-AR') }}</div>
              </div>
            </div>

            <button class="btn-checkout-action" @click="procesarPedido" :disabled="procesando || cartStore.items.length === 0 || (tipoEntrega === 'MOTO' && !deliveryLatLng) || (tipoEntrega === 'MOTO' && calculandoCosto)">
              <span v-if="!procesando">
                <Lock :size="17" />
                Pagar con Mercado Pago
              </span>
              <span v-else class="btn-processing">
                <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
                Procesando...
              </span>
            </button>

            <p class="mp-note">Serás redirigido a Mercado Pago para completar el pago.</p>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import api from '@/services/api'
import { envioService } from '@/services/envioService'
import Swal from 'sweetalert2'
import { limpiarSesionLocal } from '@/utils/authPrompt'
import { LMap, LTileLayer, LMarker, LTooltip, LPolyline, LControlLayers } from '@vue-leaflet/vue-leaflet'
import { Store, Bike, ShoppingBag, Lock, ShieldCheck } from 'lucide-vue-next'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const localIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: 'local-marker'
})

const deliveryIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: 'destino-marker'
})

const cartStore = useCartStore()
const router = useRouter()
const tipoEntrega = ref('RETIRO')
const observaciones = ref('')
const procesando = ref(false)

const usuarioNombre = [localStorage.getItem('user_nombre'), localStorage.getItem('user_apellido')].filter(Boolean).join(' ').trim() || null

const localLat = ref(null)
const localLng = ref(null)
const localCargando = ref(true)
const localDireccion = ref('')
const referenciaLocal = ref('')

const deliveryLatLng = ref(null)
const costoEnvioCalculado = ref(0)
const distanciaKm = ref(0)
const dentroCobertura = ref(true)
const radioCoberturaKm = ref(null)
const rutaCoords = ref(null)
const tiempoEstimadoMinutos = ref(0)
const calculandoCosto = ref(false)
const buscandoGPS = ref(false)
const errorGPS = ref('')
const busquedaDir = ref('')
const sugerencias = ref([])
const buscandoDir = ref(false)
let timeoutBusqueda = null
const errorCalculo = ref('')
const direccionDetectada = ref('')
const detalleDireccion = ref(null)
const numeroIngresado = ref('')
const calleConfirmada = ref('')
const confianzaDireccion = ref('')

const zoom = ref(14)
const mapRef = ref(null)
let dragTimeout = null

const NOMINATIM_UA = 'HairSoft/1.0'

const localCiudad = ref('')
const localProvincia = ref('')
const localPais = ref('')
const sinResultados = ref(false)
let secuenciaBusqueda = 0

const TIPOS_DIRECCION = new Set([
  'house', 'residential', 'apartments', 'building', 'retail', 'commercial',
  'industrial', 'hotel', 'detached', 'terrace', 'semidetached_house', 'houseboat',
  'apartment', 'garage', 'roof', 'ger', 'dormitory', 'bungalow', 'cabin',
  'service', 'warehouse', 'office', 'clinic', 'hospital', 'school', 'college',
  'university', 'church', 'factory', 'kiosk', 'hut', 'shack', 'station',
  'substation', 'sports_centre', 'address',
])

const tilesBase = [
  { name: 'Calle', url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', visible: true, att: '&copy; <a href="https://osm.org">OpenStreetMap</a>' },
  { name: 'Satelital', url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', visible: false, att: '&copy; <a href="https://esri.com">Esri</a>' },
  { name: 'Relieve', url: 'https://tile.opentopomap.org/{z}/{x}/{y}.png', visible: false, att: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a>' },
]

function formatearDireccion(data) {
  if (!data || !data.address) return null
  const a = data.address
  const calle = a.road || a.pedestrian || ''
  const altura = a.house_number || ''
  const direccion = [calle, altura].filter(Boolean).join(' ')
  const ciudad = a.city || a.town || a.village || ''
  const provincia = a.state || ''
  const pais = a.country || ''
  const partes = [direccion, ciudad, provincia, pais].filter(Boolean)
  return partes.length ? partes.join(', ') : null
}

function normalizarTexto(texto) {
  if (!texto) return ''
  return String(texto)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim()
}

function normalizarDivision(texto) {
  return normalizarTexto(texto)
    .replace(/^(provincia|province|departamento|department|municipio|municipality|partido|ciudad|city|comuna|region|estado|state|distrito|district|localidad)\s+(del|de|la|el|los|las)\s+/, '')
    .replace(/^(provincia|province|departamento|department|municipio|municipality|partido|ciudad|city|comuna|region|estado|state|distrito|district|localidad)\s+/, '')
}

function normalizarCalle(texto) {
  return normalizarTexto(texto)
    .replace(/^(avda\.?|avenida|av\.|calle|ruta|boulevard|bulevar|bvd\.|paseo|pasaje|plaza|camino|esquina|calzada)\s+(de|del|la|el|los|las)\s+/, '')
    .replace(/^(avda\.?|avenida|av\.|calle|ruta|boulevard|bulevar|bvd\.|paseo|pasaje|plaza|camino|esquina|calzada)\s+/, '')
    .trim()
}

function callesCoinciden(a, b) {
  const na = normalizarCalle(a)
  const nb = normalizarCalle(b)
  if (!na || !nb) return false
  if (na === nb) return true
  if (na.length >= 5 && nb.includes(na)) return true
  if (nb.length >= 5 && na.includes(nb)) return true
  return false
}

function haversineKm(lat1, lng1, lat2, lng2) {
  const R = 6371
  const toRad = (g) => (g * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function extraerLocalidad(addr) {
  return (addr && (addr.city || addr.town || addr.village || addr.municipality)) || ''
}

function esTipoDireccion(sug) {
  const a = sug.address || {}
  if (a.house_number) return true
  if (TIPOS_DIRECCION.has(sug.type)) return true
  if (sug.class === 'building') return true
  if (sug.class === 'highway') return true
  return false
}

function sugerenciaEnriquecida(sug) {
  const a = sug.address || {}
  const calle = a.road || a.pedestrian || a.pedestrians || ''
  const altura = a.house_number || ''
  const titulo =
    [calle, altura].filter(Boolean).join(' ') ||
    (sug.display_name ? sug.display_name.split(',')[0].trim() : '') ||
    sug.name ||
    ''
  const localidad = extraerLocalidad(a)
  const provincia = a.state || ''
  const pais = a.country || ''
  const subtitulo = [localidad, provincia, pais].filter(Boolean).join(', ')
  return { ...sug, titulo, subtitulo }
}

function reordenarSugerencias(data) {
  const normCiudad = normalizarDivision(localCiudad.value)
  const normProvincia = normalizarDivision(localProvincia.value)
  const normPais = normalizarTexto(localPais.value)
  const tienenLocal = localLat.value != null && localLng.value != null

  const ordenadas = (data || [])
    .map((sug, idx) => {
      const a = sug.address || {}
      const lat = parseFloat(sug.lat)
      const lng = parseFloat(sug.lon)
      const latOk = !isNaN(lat) && !isNaN(lng)
      const distLocal = latOk && tienenLocal
        ? haversineKm(lat, lng, localLat.value, localLng.value)
        : Infinity

      const localidad = extraerLocalidad(a)
      const provincia = a.state || ''
      const pais = a.country || ''

      let score = 0
      if (esTipoDireccion(sug)) score += 200
      if (normCiudad && normalizarDivision(localidad) === normCiudad) score += 1000
      else if (normProvincia && normalizarDivision(provincia) === normProvincia) score += 300
      if (normPais && normalizarTexto(pais) === normPais) score += 20
      if (distLocal <= 5) score += 60
      else if (distLocal <= 15) score += 40
      else if (distLocal <= 40) score += 20

      return { sug, score, idx }
    })
    .sort((x, y) => {
      if (y.score !== x.score) return y.score - x.score
      return x.idx - y.idx
    })
    .map(({ sug }) => sugerenciaEnriquecida(sug))

  return ordenadas
}

function separarCalleNumero(q) {
  const m = q.match(/^(.+?)\s+(\d{1,5})\s*$/)
  if (m) return { street: m[1].trim(), housenumber: m[2] }
  return { street: q, housenumber: null }
}

function extraerNumero(q) {
  const m = String(q || '').trim().match(/^(.*?)\s+(\d{1,5})\s*(?:,.*)?$/)
  return m ? { calle: m[1].trim(), numero: m[2] } : { calle: String(q || '').trim(), numero: '' }
}

function etiquetaDireccion(detalle, pais = '') {
  if (!detalle) return ''
  const direccion = [detalle.calle, detalle.altura].filter(Boolean).join(' ')
  return [direccion, detalle.ciudad, detalle.provincia, pais].filter(Boolean).join(', ')
}

async function reverseGeocode(lat, lng) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&addressdetails=1`,
      { headers: { 'User-Agent': NOMINATIM_UA } }
    )
    return await res.json()
  } catch {
    return null
  }
}

onMounted(async () => {
  try {
    // Validar que el token sea real (no solo presencia en localStorage)
    try {
      await api.get('/api/auth/verificar/')
    } catch (error) {
      if (error.response?.status === 401) {
        limpiarSesionInvalida('/checkout')
        return
      }
    }

    const res = await envioService.getConfigLocal()
    if (res.data && res.data.latitud_local && res.data.longitud_local) {
      localLat.value = parseFloat(res.data.latitud_local)
      localLng.value = parseFloat(res.data.longitud_local)
      referenciaLocal.value = res.data.direccion_referencia || ''
      radioCoberturaKm.value = res.data.radio_cobertura_km ? parseFloat(res.data.radio_cobertura_km) : null

      reverseGeocode(localLat.value, localLng.value).then(data => {
        if (data && data.address) {
          localDireccion.value = formatearDireccion(data) || `${localLat.value.toFixed(4)}, ${localLng.value.toFixed(4)}`
          localCiudad.value = extraerLocalidad(data.address)
          localProvincia.value = data.address.state || ''
          localPais.value = data.address.country || ''
        } else {
          localDireccion.value = `${localLat.value.toFixed(4)}, ${localLng.value.toFixed(4)}`
        }
      })
    }
  } catch {
    console.error('No se pudo obtener ubicación del local')
  }
  localCargando.value = false
})

// Sesión inválida/expirada: limpiar credenciales (SIN tocar el carrito) y volver a Login
const limpiarSesionInvalida = (redirect) => {
  limpiarSesionLocal()
  router.replace({ name: 'Login', query: { redirect } })
}

const mapCenter = computed(() => {
  if (deliveryLatLng.value && localLat.value) {
    const midLat = (localLat.value + deliveryLatLng.value[0]) / 2
    const midLng = (localLng.value + deliveryLatLng.value[1]) / 2
    return [midLat, midLng]
  }
  return [localLat.value || 0, localLng.value || 0]
})

const obtenerGPS = () => {
  if (!navigator.geolocation) {
    errorGPS.value = 'Tu dispositivo no soporta geolocalización. Hacé clic en el mapa.'
    return
  }
  buscandoGPS.value = true
  errorGPS.value = ''
  errorCalculo.value = ''
  navigator.geolocation.getCurrentPosition(
    (position) => {
      colocarEnPosicion(position.coords.latitude, position.coords.longitude)
      buscandoGPS.value = false
    },
    () => {
      errorGPS.value = 'No se pudo obtener tu ubicación. Hacé clic en el mapa.'
      buscandoGPS.value = false
    },
    { enableHighAccuracy: true, timeout: 10000 }
  )
}

const buscarEnNominatim = async (params) => {
  const res = await fetch(
    `https://nominatim.openstreetmap.org/search?${params.toString()}`,
    { headers: { 'User-Agent': NOMINATIM_UA, 'Accept-Language': 'es' } }
  )
  if (!res.ok) throw new Error('Error en Nominatim')
  return await res.json()
}

const viewboxPara = (span) => {
  if (localLat.value == null || localLng.value == null) return null
  const lonMin = localLng.value - span
  const latMin = localLat.value - span
  const lonMax = localLng.value + span
  const latMax = localLat.value + span
  return `${lonMin},${latMin},${lonMax},${latMax}`
}

const buscarLibre = async (q, span, acotada) => {
  const params = new URLSearchParams({
    format: 'json',
    q,
    limit: acotada ? '8' : '10',
    addressdetails: '1',
    countrycodes: 'ar',
    dedupe: '1',
    'accept-language': 'es',
  })
  const viewbox = viewboxPara(span)
  if (viewbox) {
    params.set('viewbox', viewbox)
    if (acotada) params.set('bounded', '1')
  }
  return await buscarEnNominatim(params)
}

const intentarBusquedaEstructurada = async (q, miSecuencia) => {
  if (!localProvincia.value && !localCiudad.value) return []
  try {
    const { street, housenumber } = separarCalleNumero(q)
    const params = new URLSearchParams({
      format: 'json',
      street,
      country: 'Argentina',
      limit: '5',
      addressdetails: '1',
      dedupe: '1',
      'accept-language': 'es',
    })
    if (housenumber) params.set('housenumber', housenumber)
    if (localProvincia.value) params.set('state', localProvincia.value)
    if (localCiudad.value) params.set('city', localCiudad.value)
    const data = await buscarEnNominatim(params)
    return miSecuencia === secuenciaBusqueda ? data : []
  } catch {
    return []
  }
}

const onBuscarDireccion = () => {
  if (timeoutBusqueda) clearTimeout(timeoutBusqueda)
  const q = busquedaDir.value.trim()
  if (q.length < 3) {
    sugerencias.value = []
    sinResultados.value = false
    return
  }
  buscandoDir.value = true
  sinResultados.value = false
  const miSecuencia = ++secuenciaBusqueda

  timeoutBusqueda = setTimeout(async () => {
    try {
      // 1) Primero: búsqueda acotada alrededor del comercio (prioriza la localidad, no bloquea).
      let data = await buscarLibre(q, 0.08, true)
      if (miSecuencia !== secuenciaBusqueda) return

      // 2) Si no hay resultados locales, abrir a toda Argentina con sesgo local.
      if (!data || data.length === 0) {
        data = await buscarLibre(q, 0.3, false)
        if (miSecuencia !== secuenciaBusqueda) return
      }

      // 3) Rescate final: búsqueda estructurada acotada a la provincia/localidad del comercio.
      if (!data || data.length === 0) {
        data = await intentarBusquedaEstructurada(q, miSecuencia)
        if (miSecuencia !== secuenciaBusqueda) return
      }

      const conCoord = (data || []).filter(s => s.lat && s.lon)
      sugerencias.value = reordenarSugerencias(conCoord)
      sinResultados.value = conCoord.length === 0
    } catch {
      if (miSecuencia === secuenciaBusqueda) {
        sugerencias.value = []
        sinResultados.value = true
      }
    } finally {
      if (miSecuencia === secuenciaBusqueda) buscandoDir.value = false
    }
  }, 350)
}

const confirmarDireccion = () => {
  if (sugerencias.value.length > 0) {
    seleccionarDireccion(sugerencias.value[0])
  }
}

const onBlurBusqueda = () => {
  setTimeout(() => {
    sugerencias.value = []
    sinResultados.value = false
  }, 150)
}

const seleccionarDireccion = (sug) => {
  const queryOriginal = busquedaDir.value
  const addr = sug.address || {}
  const calle = addr.road || addr.pedestrian || ''
  const { calle: calleQuery, numero } = extraerNumero(queryOriginal)
  let altura = addr.house_number || ''
  if (!altura && numero && callesCoinciden(calleQuery, calle)) {
    altura = numero
  }
  const localidad = extraerLocalidad(addr)
  const provincia = addr.state || ''
  const pais = addr.country || ''
  detalleDireccion.value = { calle, altura, ciudad: localidad, provincia }
  const etiqueta = etiquetaDireccion(detalleDireccion.value, pais) || sug.display_name || ''
  busquedaDir.value = etiqueta
  sugerencias.value = []
  sinResultados.value = false
  if (timeoutBusqueda) clearTimeout(timeoutBusqueda)
  secuenciaBusqueda++
  const lat = parseFloat(sug.lat)
  const lng = parseFloat(sug.lon)
  deliveryLatLng.value = [lat, lng]
  errorGPS.value = ''
  errorCalculo.value = ''
  direccionDetectada.value = etiqueta || `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
  numeroIngresado.value = altura
  calleConfirmada.value = normalizarCalle(calle)
  confianzaDireccion.value = addr.house_number ? 'alta' : 'parcial'
  calcularCostoEnvio(lat, lng)
}

const colocarMarcador = (event) => {
  const { lat, lng } = event.latlng
  colocarEnPosicion(lat, lng)
}

const colocarEnPosicion = async (lat, lng) => {
  deliveryLatLng.value = [lat, lng]
  errorGPS.value = ''
  errorCalculo.value = ''

  const geo = await reverseGeocode(lat, lng)
  if (geo && geo.address) {
    const addr = geo.address
    const calle = addr.road || addr.pedestrian || ''
    const nuevaCalleNorm = normalizarCalle(calle)
    const mismaCalle = !!(calleConfirmada.value && nuevaCalleNorm && nuevaCalleNorm === calleConfirmada.value)
    const altura = addr.house_number || (mismaCalle ? numeroIngresado.value : '')
    const pais = addr.country || ''
    detalleDireccion.value = {
      calle,
      altura,
      ciudad: addr.city || addr.town || addr.village || '',
      provincia: addr.state || '',
    }
    direccionDetectada.value = etiquetaDireccion(detalleDireccion.value, pais) || `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
    calleConfirmada.value = calle ? nuevaCalleNorm : ''
    numeroIngresado.value = altura
    confianzaDireccion.value = 'manual'
  } else {
    direccionDetectada.value = `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
    detalleDireccion.value = { calle: '', altura: '', ciudad: '', provincia: '' }
    numeroIngresado.value = ''
    calleConfirmada.value = ''
    confianzaDireccion.value = 'manual'
  }

  calcularCostoEnvio(lat, lng)
}

const marcadorArrastrado = (event) => {
  const { lat, lng } = event.target.getLatLng()
  deliveryLatLng.value = [lat, lng]
  if (dragTimeout) clearTimeout(dragTimeout)
  dragTimeout = setTimeout(() => {
    colocarEnPosicion(lat, lng)
  }, 600)
}

const calcularCostoEnvio = async (lat, lng) => {
  if (!localLat.value) {
    errorCalculo.value = 'El local no tiene configurada su ubicación.'
    return
  }
  calculandoCosto.value = true
  errorCalculo.value = ''
  try {
    const res = await envioService.calcularCosto(lat, lng)
    costoEnvioCalculado.value = parseFloat(res.data.costo_envio)
    distanciaKm.value = parseFloat(res.data.distancia_km)
    dentroCobertura.value = res.data.dentro_cobertura !== false
    rutaCoords.value = res.data.ruta_coords || null
    tiempoEstimadoMinutos.value = parseInt(res.data.tiempo_estimado_minutos) || 0
  } catch (e) {
    errorCalculo.value = 'Error al calcular el costo de envío. Verificá la configuración del local.'
    console.error(e)
  } finally {
    calculandoCosto.value = false
  }
}

watch(tipoEntrega, () => {
  if (tipoEntrega.value === 'RETIRO') {
    costoEnvioCalculado.value = 0
    distanciaKm.value = 0
    rutaCoords.value = null
    tiempoEstimadoMinutos.value = 0
    deliveryLatLng.value = null
    observaciones.value = ''
    direccionDetectada.value = ''
    detalleDireccion.value = null
    numeroIngresado.value = ''
    calleConfirmada.value = ''
    confianzaDireccion.value = ''
  }
})

const costoEnvio = computed(() => {
  if (tipoEntrega.value === 'MOTO' && dentroCobertura.value && costoEnvioCalculado.value > 0) return costoEnvioCalculado.value
  return 0
})

const totalFinal = computed(() => cartStore.precioTotal + costoEnvio.value)

const radioCoberturaDisplay = computed(() => {
  if (!radioCoberturaKm.value) return null
  return radioCoberturaKm.value.toLocaleString('es-AR', { maximumFractionDigits: 1 })
})

const distanciaDisplay = computed(() =>
  distanciaKm.value ? distanciaKm.value.toLocaleString('es-AR', { maximumFractionDigits: 1 }) : '0'
)

const confianzaInfo = computed(() => {
  if (confianzaDireccion.value === 'alta') return { texto: 'Exacta', clase: 'alta' }
  if (confianzaDireccion.value === 'parcial') return { texto: 'Aproximada', clase: 'parcial' }
  if (confianzaDireccion.value === 'manual') return { texto: 'Ubicación confirmada', clase: 'manual' }
  return null
})

const fueraCoberturaMsg = computed(() => {
  let msg = `Esta dirección se encuentra a ${distanciaDisplay.value} km del local.`
  if (radioCoberturaKm.value) msg += ` La cobertura máxima para Moto Mandado es de ${radioCoberturaDisplay.value} km.`
  return msg
})

const procesarPedido = async () => {
  if (cartStore.items.length === 0) return

  if (tipoEntrega.value === 'MOTO' && !deliveryLatLng.value) {
    Swal.fire({
      title: 'Falta la dirección',
      text: 'Usá el GPS o hacé clic en el mapa para indicar la dirección de entrega.',
      icon: 'warning',
      confirmButtonColor: '#0ea5e9'
    })
    return
  }

  if (tipoEntrega.value === 'MOTO' && confianzaDireccion.value === 'parcial') {
    Swal.fire({
      title: 'Ubicación aproximada',
      text: 'No pudimos determinar automáticamente la altura exacta de esta dirección. Arrastrá el marcador o hacé clic en el mapa para confirmar la ubicación.',
      icon: 'warning',
      confirmButtonColor: '#0ea5e9'
    })
    return
  }

  if (tipoEntrega.value === 'MOTO' && !dentroCobertura.value) {
    Swal.fire({
      title: 'Fuera de cobertura',
      text: fueraCoberturaMsg.value,
      icon: 'error',
      confirmButtonColor: '#0ea5e9'
    })
    return
  }

  procesando.value = true

  try {
    let payload

    if (tipoEntrega.value === 'RETIRO') {
      payload = {
        tipo_entrega: 'RETIRO',
        costo_envio: 0,
        direccion_envio: 'Retiro en Local',
        detalles: cartStore.items.map(item => ({ producto: item.id, cantidad: item.cantidad }))
      }
    } else {
      const coords = deliveryLatLng.value
      const partes = []
      if (observaciones.value.trim()) partes.push(`Obs: ${observaciones.value.trim()}`)
      partes.push(`GPS: ${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`)
      const direccionCompleta = [direccionDetectada.value, ...partes].join(' | ')

      payload = {
        tipo_entrega: 'MOTO',
        costo_envio: costoEnvio.value,
        direccion_envio: direccionCompleta,
        latitud_entrega: coords[0],
        longitud_entrega: coords[1],
        calle_entrega: detalleDireccion.value?.calle || '',
        altura_entrega: detalleDireccion.value?.altura || '',
        ciudad_entrega: detalleDireccion.value?.ciudad || '',
        provincia_entrega: detalleDireccion.value?.provincia || '',
        observaciones_entrega: observaciones.value,
        detalles: cartStore.items.map(item => ({ producto: item.id, cantidad: item.cantidad }))
      }
    }

    const response = await api.post('/web/pedidos/', payload)

    if (response.data.url_pago) {
      cartStore.limpiarCarrito()
      window.location.href = response.data.url_pago
    } else {
      throw new Error('No se recibió el link de pago.')
    }

  } catch (error) {
    console.error('Error checkout:', error)
    if (error.response?.status === 401) {
      limpiarSesionInvalida('/checkout')
      return
    }
    Swal.fire({
      title: 'Error',
      text: error.response?.data?.message || 'No se pudo procesar la compra.',
      icon: 'error',
      confirmButtonColor: '#ef4444'
    })
  } finally {
    procesando.value = false
  }
}
</script>

<style scoped>
.checkout-page {
  background: linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh; padding: 50px 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  color: #0f172a;
}
.checkout-container { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 36px; text-align: center; }
.header-eyebrow {
  display: inline-block; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;
  color: #0284c7; background: #e0f2fe; border: 1px solid #bae6fd; padding: 5px 14px; border-radius: 999px; margin-bottom: 14px;
}
.page-header h1 { font-size: 2.2rem; color: #0f172a; margin-bottom: 8px; font-weight: 800; letter-spacing: -0.02em; }
.page-header p { font-size: 1.05rem; color: #64748b; max-width: 560px; margin: 0 auto; }
.checkout-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px; align-items: start; }

.checkout-section {
  background: white; padding: 28px; border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
  border: 1px solid #f1f5f9; margin-bottom: 22px;
}
.section-title {
  font-size: 1.25rem; color: #1e293b; margin-bottom: 20px;
  display: flex; align-items: center; gap: 12px; font-weight: 700;
}
.step-number {
  background: #0ea5e9; color: white; width: 30px; height: 30px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 0.95rem; font-weight: 700;
  box-shadow: 0 2px 8px rgba(14,165,233,0.3);
}

.delivery-cards { display: flex; flex-direction: column; gap: 14px; }
.delivery-card {
  display: flex; align-items: center; gap: 16px; padding: 18px 20px;
  border: 2px solid #e2e8f0; border-radius: 14px; cursor: pointer;
  transition: all 0.2s ease; background: #f8fafc;
}
.delivery-card:hover { border-color: #cbd5e1; background: white; }
.delivery-card.active { border-color: #0ea5e9; background: #f0f9ff; box-shadow: 0 2px 12px rgba(14,165,233,0.12); }
.delivery-radio {
  width: 20px; height: 20px; border-radius: 50%; border: 2px solid #cbd5e1; background: white;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s ease;
}
.delivery-radio.radio-checked { border-color: #0ea5e9; }
.radio-dot { width: 10px; height: 10px; border-radius: 50%; background: #0ea5e9; }
.delivery-icon {
  width: 46px; height: 46px; border-radius: 12px; background: #e0f2fe; color: #0284c7;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s ease;
}
.delivery-card.active .delivery-icon { background: #0ea5e9; color: white; }
.card-content { flex: 1; display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.card-title { font-weight: 700; color: #1e293b; font-size: 1.05rem; }
.card-desc { font-size: 0.88rem; color: #64748b; }
.card-price {
  font-weight: 700; color: #0f172a; font-size: 1.05rem;
  padding: 5px 12px; background: white; border-radius: 8px; border: 1px solid #e2e8f0; white-space: nowrap;
}
.card-price.free { color: #059669; background: #ecfdf5; border-color: #a7f3d0; }
.card-price.price-calculated { color: #0ea5e9; background: #f0f9ff; border-color: #bae6fd; }
.card-price.price-error { color: #ef4444; background: #fef2f2; border-color: #fecaca; }

.retiro-section { background: linear-gradient(to bottom, #ffffff, #f0f9ff); }
.retiro-card {
  display: flex; align-items: center; gap: 16px; padding: 18px 20px;
  background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 12px;
}
.retiro-icon {
  width: 44px; height: 44px; border-radius: 12px; background: #0ea5e9; color: white;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.retiro-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.retiro-info strong { font-size: 1rem; color: #1e293b; }
.retiro-info span { font-size: 0.9rem; color: #64748b; }
.retiro-badge {
  font-weight: 700; color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0;
  padding: 6px 14px; border-radius: 999px; font-size: 0.95rem; white-space: nowrap;
}

.sub-block { margin-top: 22px; }
.sub-block:first-of-type { margin-top: 0; }
.sub-title {
  font-size: 0.85rem; font-weight: 700; color: #1e293b; text-transform: uppercase; letter-spacing: 0.5px;
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}
.sub-title::before { content: ''; width: 4px; height: 15px; border-radius: 2px; background: #0ea5e9; flex-shrink: 0; }
.sub-title .optional { font-weight: 400; color: #94a3b8; font-size: 0.78rem; text-transform: none; }

.cobertura-warning {
  display: flex; align-items: flex-start; gap: 10px; padding: 14px 16px;
  margin: 12px 0; background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px;
  color: #b91c1c; font-size: 0.9rem; font-weight: 500;
}
.cobertura-warning svg { flex-shrink: 0; margin-top: 2px; stroke: #ef4444; }

.cobertura-info {
  display: flex; align-items: flex-start; gap: 12px;
  margin-bottom: 20px; padding: 14px 16px;
  background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 12px;
}
.cobertura-icon {
  width: 34px; height: 34px; border-radius: 10px; background: #e0f2fe; color: #0284c7;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;
}
.cobertura-text { display: flex; flex-direction: column; gap: 2px; }
.cobertura-text strong { font-size: 0.85rem; color: #0284c7; text-transform: uppercase; letter-spacing: 0.5px; }
.cobertura-text span { font-size: 0.92rem; color: #334155; line-height: 1.45; }

.gps-btn-container { margin-bottom: 12px; }
.btn-gps {
  width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;
  padding: 16px; border: 2px solid #0ea5e9; border-radius: 12px;
  background: #f0f9ff; color: #0284c7; font-weight: 700; font-size: 1.05rem;
  cursor: pointer; transition: all 0.2s ease;
}
.btn-gps:hover:not(:disabled) { background: #0ea5e9; color: white; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(14,165,233,0.3); }
.btn-gps:disabled { opacity: 0.6; cursor: wait; }

.search-divider { display: flex; align-items: center; gap: 12px; margin: 8px 0 12px; color: #94a3b8; font-size: 0.8rem; font-weight: 600; }
.search-divider::before, .search-divider::after { content: ''; flex: 1; height: 1px; background: #e2e8f0; }

.address-search-container { position: relative; margin-bottom: 12px; }
.address-search-input-wrapper { position: relative; display: flex; align-items: center; }
.search-addr-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; z-index: 1; }
.address-search-input { padding-left: 42px !important; padding-right: 40px !important; background: #fff; color: #0f172a; }
.address-search-input::placeholder { color: #94a3b8; }
.search-spinner { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); width: 18px; height: 18px; border: 3px solid #e2e8f0; border-left-color: #0ea5e9; border-radius: 50%; animation: spin 0.6s linear infinite; }
.suggestions-dropdown { position: absolute; top: 100%; left: 0; right: 0; background: #1e1e2e; border: 1px solid #334155; border-radius: 0 0 12px 12px; max-height: 220px; overflow-y: auto; z-index: 1000; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.suggestion-item { display: flex; align-items: flex-start; gap: 10px; padding: 12px 14px; cursor: pointer; color: #e2e8f0; font-size: 0.85rem; border-bottom: 1px solid #334155; transition: background 0.15s; }
.suggestion-item:last-child { border-bottom: none; border-radius: 0 0 12px 12px; }
.suggestion-item:hover { background: #334155; }
.suggestion-icon { flex-shrink: 0; color: #0ea5e9; margin-top: 2px; }
.suggestion-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.suggestion-title { color: #f1f5f9; font-weight: 600; line-height: 1.3; }
.suggestion-sub { color: #94a3b8; font-size: 0.78rem; line-height: 1.3; }
.no-results-msg {
  position: absolute; top: 100%; left: 0; right: 0; background: #1e1e2e;
  border: 1px solid #334155; border-radius: 0 0 12px 12px;
  padding: 14px 16px; color: #cbd5e1; font-size: 0.85rem;
  z-index: 1000; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

.map-hint {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; padding: 10px 14px;
  background: #f8fafc; border-radius: 8px;
  color: #64748b; font-size: 0.85rem;
}

.map-wrapper { margin-bottom: 12px; }
.map-wrapper .leaflet-container { border-radius: 12px; }

.coords-display { margin-top: 6px; text-align: center; color: #94a3b8; font-size: 0.8rem; }

.address-detected-card {
  margin-top: 12px; padding: 16px;
  background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;
}
.address-detected-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
}
.address-detected-header span { font-weight: 700; color: #059669; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
.address-detected-text { font-size: 0.95rem; color: #0f172a; margin: 0 0 8px; font-weight: 500; }
.address-detected-details {
  display: flex; flex-wrap: wrap; gap: 6px 16px;
  font-size: 0.85rem; color: #475569;
}
.address-detected-details strong { color: #334155; }
.confianza-chip {
  display: inline-flex; align-items: center;
  margin-left: auto; padding: 3px 10px; border-radius: 999px;
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px;
}
.confianza-chip.alta { color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; }
.confianza-chip.parcial { color: #b45309; background: #fffbeb; border: 1px solid #fde68a; }
.confianza-chip.manual { color: #0369a1; background: #f0f9ff; border: 1px solid #bae6fd; }
.address-confirm-warning {
  display: flex; align-items: flex-start; gap: 8px;
  margin-top: 10px; padding: 10px 12px;
  background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px;
  font-size: 0.85rem; color: #92400e; line-height: 1.4;
}
.address-confirm-warning svg { flex-shrink: 0; margin-top: 1px; }
.delivery-status {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px;
  margin-top: 12px; padding-top: 12px; border-top: 1px dashed #bbf7d0;
}
.status-item { font-size: 0.9rem; color: #334155; }
.status-item strong { color: #0f172a; }
.status-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 700;
}
.status-badge.ok { color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; }
.status-badge.bad { color: #b91c1c; background: #fef2f2; border: 1px solid #fecaca; }
.altura-input {
  width: 90px; padding: 4px 8px; border: 2px solid #cbd5e1; border-radius: 6px;
  font-size: 0.85rem; background: #fff; color: #0f172a; outline: none; transition: border-color 0.2s;
  margin-left: 4px;
}
.altura-input:focus { border-color: #0ea5e9; }

.costo-loading {
  display: flex; align-items: center; gap: 10px; margin-top: 12px;
  padding: 14px; background: #f8fafc; border-radius: 10px;
  color: #64748b; font-size: 0.9rem;
}

.costo-card {
  display: flex; align-items: center; gap: 20px; margin-top: 12px;
  padding: 16px 20px; background: #f0f9ff; border: 2px solid #bae6fd; border-radius: 12px;
}
.costo-item { display: flex; flex-direction: column; }
.costo-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
.costo-value { font-size: 1.1rem; font-weight: 700; color: #0f172a; }
.costo-price { color: #059669; font-size: 1.3rem; }
.costo-divider { width: 1px; height: 40px; background: #bae6fd; }

.obs-section { margin-top: 16px; }
.obs-section label { display: block; margin-bottom: 8px; color: #475569; font-weight: 600; font-size: 0.9rem; }
.obs-section .optional { font-weight: 400; color: #94a3b8; font-size: 0.8rem; }
.modern-textarea {
  width: 100%; padding: 14px 16px; border: 1.5px solid #cbd5e1; border-radius: 10px;
  background-color: white; font-size: 1rem; color: #1e293b; transition: all 0.2s ease; resize: vertical;
}
.modern-textarea:focus { outline: none; border-color: #0ea5e9; box-shadow: 0 0 0 3px rgba(14,165,233,0.15); }
.obs-hint { display: block; margin-top: 6px; color: #94a3b8; font-size: 0.8rem; }

.error-msg { margin-top: 12px; padding: 10px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; color: #ef4444; font-size: 0.85rem; text-align: center; }

.map-loading { text-align: center; padding: 60px; color: #94a3b8; font-style: italic; }

.empty-state {
  text-align: center; padding: 30px 20px; margin-top: 12px;
  background: #f8fafc; border-radius: 12px; border: 2px dashed #e2e8f0;
}
.empty-state p { color: #94a3b8; font-size: 0.9rem; margin-top: 10px; }

.summary-column { position: relative; }
.summary-card {
  background: white; padding: 28px; border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; position: sticky; top: 24px;
}
.summary-header { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.summary-title { display: flex; align-items: center; gap: 10px; }
.summary-icon {
  width: 34px; height: 34px; border-radius: 10px; background: #e0f2fe; color: #0284c7;
  display: flex; align-items: center; justify-content: center;
}
.summary-card h3 { font-size: 1.15rem; color: #1e293b; margin: 0; font-weight: 700; }
.comprando-como {
  font-size: 0.85rem; color: #64748b; padding: 8px 12px;
  background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px;
}
.comprando-como strong { color: #334155; font-weight: 600; }
.empty-cart-msg { text-align: center; padding: 20px 0; color: #94a3b8; font-size: 0.9rem; }
.summary-items-list { display: flex; flex-direction: column; gap: 10px; max-height: 320px; overflow-y: auto; padding-right: 5px; }
.summary-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px; }
.item-info { display: flex; align-items: center; gap: 10px; }
.item-qty { background: #e0f2fe; color: #0284c7; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
.item-name { color: #334155; font-weight: 500; font-size: 0.95rem; }
.item-price { color: #0f172a; font-weight: 700; font-size: 1rem; }

.divider { height: 1px; background: #e2e8f0; margin: 18px 0; }
.summary-totals { display: flex; flex-direction: column; gap: 12px; }
.total-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.98rem; color: #475569; }
.total-row.shipping .shipping-cost { font-weight: 700; color: #0ea5e9; }
.total-row.shipping .shipping-none { color: #94a3b8; }
.total-row.shipping .shipping-free { font-weight: 700; color: #059669; }
.total-row.shipping .shipping-fuera { font-weight: 700; color: #dc2626; font-size: 0.85rem; }
.total-row.shipping .shipping-loading { font-style: italic; color: #94a3b8; display: inline-flex; align-items: center; gap: 6px; }
.total-final-box {
  margin-top: 8px; padding: 16px 18px; border-radius: 12px;
  background: linear-gradient(135deg, #0c4a6e, #0ea5e9); color: white;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 4px 14px rgba(14,165,233,0.25);
}
.total-final-label { font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.92; }
.total-final-amount { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em; }

.btn-checkout-action {
  width: 100%; margin-top: 22px; padding: 16px 20px; min-height: 54px;
  background: #0ea5e9; color: white; border: none; border-radius: 12px;
  font-weight: 700; font-size: 1.05rem; cursor: pointer;
  transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 14px rgba(14,165,233,0.25);
}
.btn-checkout-action:hover:not(:disabled) { background: #0284c7; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(14,165,233,0.35); }
.btn-checkout-action:active:not(:disabled) { transform: translateY(0); }
.btn-checkout-action:disabled { background: #cbd5e1; box-shadow: none; cursor: not-allowed; }
.btn-processing { display: inline-flex; align-items: center; gap: 8px; }
.mp-note { margin-top: 12px; text-align: center; font-size: 0.8rem; color: #94a3b8; }
.trust-note {
  margin-top: 8px; display: flex; align-items: center; justify-content: center; gap: 6px;
  font-size: 0.78rem; color: #64748b;
}

@media (max-width: 968px) {
  .checkout-grid { grid-template-columns: 1fr; }
  .checkout-page { padding: 28px 14px; }
  .page-header h1 { font-size: 1.7rem; }
  .delivery-card { padding: 16px; gap: 12px; }
  .delivery-icon { width: 40px; height: 40px; }
  .card-price { font-size: 0.95rem; padding: 4px 10px; }
  .retiro-card { align-items: flex-start; flex-wrap: wrap; }
  .retiro-badge { align-self: flex-end; }
  .checkout-section { padding: 22px; }
  .summary-card { padding: 22px; position: static; }
  .total-final-amount { font-size: 1.35rem; }
}

.animate-spin { animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }

:deep(.local-marker) { filter: hue-rotate(120deg) saturate(1.5); }
:deep(.destino-marker) { filter: hue-rotate(0deg); }
</style>
