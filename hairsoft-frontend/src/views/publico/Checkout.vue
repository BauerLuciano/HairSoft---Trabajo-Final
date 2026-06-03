<template>
  <div class="checkout-page">
    <div class="checkout-container">

      <div class="page-header">
        <h1>Finalizar Compra</h1>
        <p>Completá los datos para recibir tus productos.</p>
      </div>

      <div class="checkout-grid">

        <div class="form-column">

          <section class="checkout-section">
            <h2 class="section-title"><span class="step-number">1</span> Método de Entrega</h2>
            <div class="delivery-cards">
              <label class="delivery-card" :class="{ active: tipoEntrega === 'RETIRO' }">
                <input type="radio" v-model="tipoEntrega" value="RETIRO" hidden>
                <div class="card-icon">🏪</div>
                <div class="card-content">
                  <span class="card-title">Retiro en el Local</span>
                  <span class="card-desc">Pasás a buscarlo por la peluquería.</span>
                </div>
                <div class="card-price free">Gratis</div>
              </label>

              <label class="delivery-card" :class="{ active: tipoEntrega === 'MOTO' }">
                <input type="radio" v-model="tipoEntrega" value="MOTO" hidden>
                <div class="card-icon">🛵</div>
                <div class="card-content">
                  <span class="card-title">Moto Mandado</span>
                  <span class="card-desc">Te lo llevamos a casa.</span>
                </div>
                <div class="card-price" :class="{ 'price-calculated': costoEnvioCalculado > 0 }">
                  {{ costoEnvioCalculado > 0 ? `$${costoEnvioCalculado.toLocaleString('es-AR')}` : 'A calcular' }}
                </div>
              </label>
            </div>
          </section>

          <transition name="fade">
            <section v-if="tipoEntrega === 'MOTO'" class="checkout-section">
              <h2 class="section-title"><span class="step-number">2</span> Dirección de Entrega</h2>

              <div class="local-address-card" v-if="localDireccion">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                <div>
                  <strong>Peluquería</strong>
                  <span>{{ localDireccion }}</span>
                  <span v-if="referenciaLocal" style="font-size: 0.85em; color: #0ea5e9; font-weight: 600;">
                    {{ referenciaLocal }}
                  </span>
                </div>
              </div>

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
                    placeholder="Buscá tu dirección (ej. Avenida Libertador 500)"
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
                    @click="seleccionarDireccion(sug)"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    <span>{{ sug.display_name }}</span>
                  </div>
                </div>
              </div>

              <div class="map-hint">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>También podés hacer clic en el mapa o arrastrar el marcador para ajustar la dirección.</span>
              </div>

              <div v-if="errorGPS" class="error-msg">{{ errorGPS }}</div>

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
                  </div>
                  <p class="address-detected-text">{{ direccionDetectada }}</p>
                  <div v-if="detalleDireccion" class="address-detected-details">
                    <span><strong>Calle:</strong> {{ detalleDireccion.calle }}</span>
                    <span v-if="detalleDireccion.ciudad"><strong>Ciudad:</strong> {{ detalleDireccion.ciudad }}</span>
                    <span v-if="detalleDireccion.provincia"><strong>Provincia:</strong> {{ detalleDireccion.provincia }}</span>
                  </div>
                </div>
              </transition>

              <div class="coords-display" v-if="deliveryLatLng">
                <small>Lat: {{ deliveryLatLng[0].toFixed(4) }}, Lng: {{ deliveryLatLng[1].toFixed(4) }}</small>
              </div>

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
                <span>Esta dirección está fuera de nuestra zona de cobertura. Por el momento solo realizamos envíos dentro de San Vicente, Misiones.</span>
              </div>

              <div v-if="costoEnvioCalculado > 0 && !calculandoCosto" class="costo-card">
                <div class="costo-item">
                  <span class="costo-label">Distancia</span>
                  <span class="costo-value">{{ distanciaKm }} km</span>
                </div>
                <div class="costo-divider"></div>
                <div class="costo-item">
                  <span class="costo-label">Costo de envío</span>
                  <span class="costo-value costo-price">${{ costoEnvioCalculado.toLocaleString('es-AR') }}</span>
                </div>
              </div>

              <transition name="fade">
                <div v-if="deliveryLatLng" class="obs-section">
                  <label for="obs">Observaciones para la entrega <span class="optional">(opcional)</span></label>
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

              <div v-if="errorCalculo" class="error-msg">{{ errorCalculo }}</div>

              <div v-if="!deliveryLatLng && !calculandoCosto && !localCargando" class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5">
                  <path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7z"></path>
                  <circle cx="12" cy="9" r="2.5"></circle>
                </svg>
                <p>Usá el GPS o hacé clic en el mapa para indicar dónde querés recibir el pedido.</p>
              </div>

            </section>
          </transition>

        </div>

        <div class="summary-column">
          <div class="summary-card">
            <h3>Resumen del Pedido</h3>

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
                <span v-if="tipoEntrega === 'MOTO' && calculandoCosto" class="shipping-loading">Calculando...</span>
                <span v-else-if="tipoEntrega === 'MOTO' && costoEnvioCalculado > 0" class="shipping-cost">${{ costoEnvioCalculado.toLocaleString('es-AR') }}</span>
                <span v-else class="shipping-none">—</span>
              </div>
              <div class="total-row final">
                <span>Total a Pagar</span>
                <span>${{ totalFinal.toLocaleString('es-AR') }}</span>
              </div>
            </div>

            <button class="btn-checkout-action" @click="procesarPedido" :disabled="procesando || cartStore.items.length === 0 || (tipoEntrega === 'MOTO' && !deliveryLatLng) || (tipoEntrega === 'MOTO' && calculandoCosto)">
              <span v-if="!procesando">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg>
                Pagar con Mercado Pago
              </span>
              <span v-else>
                <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
                Procesando...
              </span>
            </button>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCartStore } from '@/stores/cart'
import api from '@/services/api'
import { envioService } from '@/services/envioService'
import Swal from 'sweetalert2'
import { LMap, LTileLayer, LMarker, LTooltip, LPolyline, LControlLayers } from '@vue-leaflet/vue-leaflet'
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
const tipoEntrega = ref('RETIRO')
const observaciones = ref('')
const procesando = ref(false)

const localLat = ref(null)
const localLng = ref(null)
const localCargando = ref(true)
const localDireccion = ref('')
const referenciaLocal = ref('')

const deliveryLatLng = ref(null)
const costoEnvioCalculado = ref(0)
const distanciaKm = ref(0)
const dentroCobertura = ref(true)
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

const zoom = ref(14)
const mapRef = ref(null)
let dragTimeout = null

const NOMINATIM_UA = 'HairSoft/1.0'

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
    const res = await envioService.getConfigLocal()
    if (res.data && res.data.latitud_local && res.data.longitud_local) {
      localLat.value = parseFloat(res.data.latitud_local)
      localLng.value = parseFloat(res.data.longitud_local)
      referenciaLocal.value = res.data.direccion_referencia || ''

      reverseGeocode(localLat.value, localLng.value).then(data => {
        if (data && data.address) {
          localDireccion.value = formatearDireccion(data) || `${localLat.value.toFixed(4)}, ${localLng.value.toFixed(4)}`
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

const mapCenter = computed(() => {
  if (deliveryLatLng.value && localLat.value) {
    const midLat = (localLat.value + deliveryLatLng.value[0]) / 2
    const midLng = (localLng.value + deliveryLatLng.value[1]) / 2
    return [midLat, midLng]
  }
  return [localLat.value || -26.8083, localLng.value || -54.4362]
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

const onBuscarDireccion = () => {
  if (timeoutBusqueda) clearTimeout(timeoutBusqueda)
  const q = busquedaDir.value.trim()
  if (q.length < 4) { sugerencias.value = []; return }
  buscandoDir.value = true
  timeoutBusqueda = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)},+San+Vicente,+Misiones,+Argentina&limit=10&addressdetails=1&viewbox=-54.6341,-26.8458,-54.3341,-27.1458&bounded=1`,
          { headers: { 'User-Agent': NOMINATIM_UA, 'Accept-Language': 'es' } }
        )
        const data = await res.json()
        sugerencias.value = (data || []).filter(s => s.lat && s.lon)
      } catch {
      sugerencias.value = []
      } finally {
        buscandoDir.value = false
      }
  }, 400)
}

const confirmarDireccion = () => {
  if (sugerencias.value.length > 0) {
    seleccionarDireccion(sugerencias.value[0])
  }
}

const onBlurBusqueda = () => {
  setTimeout(() => {
    if (sugerencias.value.length > 0 && !deliveryLatLng.value) {
      seleccionarDireccion(sugerencias.value[0])
    }
  }, 200)
}

const seleccionarDireccion = (sug) => {
  busquedaDir.value = sug.display_name
  sugerencias.value = []
  if (timeoutBusqueda) clearTimeout(timeoutBusqueda)
  const lat = parseFloat(sug.lat)
  const lng = parseFloat(sug.lon)
  deliveryLatLng.value = [lat, lng]
  errorGPS.value = ''
  errorCalculo.value = ''
  const addr = sug.address || {}
  direccionDetectada.value = sug.display_name || `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
  detalleDireccion.value = {
    calle: addr.road || addr.pedestrian || '',
    altura: addr.house_number || '',
    ciudad: addr.city || addr.town || addr.village || '',
    provincia: addr.state || '',
  }
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
    direccionDetectada.value = formatearDireccion(geo) || `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
    detalleDireccion.value = {
      calle: addr.road || addr.pedestrian || '',
      altura: addr.house_number || '',
      ciudad: addr.city || addr.town || addr.village || '',
      provincia: addr.state || '',
    }
  } else {
    direccionDetectada.value = `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
    detalleDireccion.value = { calle: '', altura: '', ciudad: '', provincia: '' }
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
  }
})

const costoEnvio = computed(() => {
  if (tipoEntrega.value === 'MOTO' && costoEnvioCalculado.value > 0) return costoEnvioCalculado.value
  return 0
})

const totalFinal = computed(() => cartStore.precioTotal + costoEnvio.value)

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

  if (tipoEntrega.value === 'MOTO' && !dentroCobertura.value) {
    Swal.fire({
      title: 'Fuera de cobertura',
      text: 'Esta dirección está fuera de San Vicente. Por el momento solo realizamos envíos dentro de la ciudad.',
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
.page-header { margin-bottom: 40px; text-align: center; }
.page-header h1 { font-size: 2.5rem; color: #0f172a; margin-bottom: 8px; font-weight: 800; letter-spacing: -0.02em; }
.page-header p { font-size: 1.1rem; color: #64748b; }
.checkout-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px; align-items: start; }
@media (max-width: 968px) { .checkout-grid { grid-template-columns: 1fr; } }

.checkout-section {
  background: white; padding: 30px; border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
  border: 1px solid #f1f5f9; margin-bottom: 24px;
}
.section-title {
  font-size: 1.35rem; color: #1e293b; margin-bottom: 24px;
  display: flex; align-items: center; gap: 12px; font-weight: 700;
}
.step-number {
  background: #0ea5e9; color: white; width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 700;
  box-shadow: 0 2px 8px rgba(14,165,233,0.3);
}

.delivery-cards { display: flex; flex-direction: column; gap: 16px; }
.delivery-card {
  display: flex; align-items: center; gap: 20px; padding: 20px;
  border: 2px solid #e2e8f0; border-radius: 12px; cursor: pointer;
  transition: all 0.2s ease; background: #f8fafc;
}
.delivery-card:hover { border-color: #cbd5e1; background: white; }
.delivery-card.active { border-color: #0ea5e9; background: #f0f9ff; }
.card-icon { font-size: 2.5rem; line-height: 1; filter: grayscale(1); opacity: 0.5; transition: all 0.2s ease; }
.delivery-card.active .card-icon { filter: grayscale(0); opacity: 1; }
.card-content { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.card-title { font-weight: 700; color: #1e293b; font-size: 1.1rem; }
.card-desc { font-size: 0.9rem; color: #64748b; }
.card-price {
  font-weight: 700; color: #0f172a; font-size: 1.15rem;
  padding: 6px 12px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;
}
.card-price.free { color: #059669; background: #ecfdf5; border-color: #a7f3d0; }
.card-price.price-calculated { color: #0ea5e9; background: #f0f9ff; border-color: #bae6fd; }

.local-address-card {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 16px; margin-bottom: 16px;
  background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px;
}
.local-address-card svg { flex-shrink: 0; margin-top: 2px; }
.local-address-card div { display: flex; flex-direction: column; font-size: 0.9rem; color: #334155; gap: 2px; }
.local-address-card strong { color: #0284c7; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }

.cobertura-warning {
  display: flex; align-items: flex-start; gap: 10px; padding: 14px 16px;
  margin: 12px 0; background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px;
  color: #b91c1c; font-size: 0.9rem; font-weight: 500;
}
.cobertura-warning svg { flex-shrink: 0; margin-top: 2px; stroke: #ef4444; }

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
.suggestion-item { display: flex; align-items: center; gap: 10px; padding: 12px 14px; cursor: pointer; color: #e2e8f0; font-size: 0.85rem; border-bottom: 1px solid #334155; transition: background 0.15s; }
.suggestion-item:last-child { border-bottom: none; border-radius: 0 0 12px 12px; }
.suggestion-item:hover { background: #334155; }
.suggestion-item svg { flex-shrink: 0; color: #0ea5e9; }

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
  background: white; padding: 30px; border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; position: sticky; top: 24px;
}
.summary-card h3 { font-size: 1.35rem; color: #1e293b; margin-bottom: 24px; font-weight: 700; }
.empty-cart-msg { text-align: center; padding: 20px 0; color: #94a3b8; font-size: 0.9rem; }
.summary-items-list { display: flex; flex-direction: column; gap: 12px; max-height: 350px; overflow-y: auto; padding-right: 5px; }
.summary-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px; }
.item-info { display: flex; align-items: center; gap: 10px; }
.item-qty { background: #e0f2fe; color: #0284c7; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
.item-name { color: #334155; font-weight: 500; font-size: 0.95rem; }
.item-price { color: #0f172a; font-weight: 700; font-size: 1rem; }

.divider { height: 1px; background: #e2e8f0; margin: 20px 0; }
.summary-totals { display: flex; flex-direction: column; gap: 12px; }
.total-row { display: flex; justify-content: space-between; align-items: center; font-size: 1rem; color: #475569; }
.total-row.shipping .shipping-cost { font-weight: 700; color: #0ea5e9; }
.total-row.shipping .shipping-none { color: #94a3b8; }
.total-row.shipping .shipping-loading { font-style: italic; color: #94a3b8; }
.total-row.final { padding-top: 16px; border-top: 2px dashed #e2e8f0; font-size: 1.25rem; font-weight: 800; color: #0f172a; }

.btn-checkout-action {
  width: 100%; margin-top: 24px; padding: 16px;
  background: #0ea5e9; color: white; border: none; border-radius: 10px;
  font-weight: 700; font-size: 1.05rem; cursor: pointer;
  transition: all 0.2s ease; display: flex; align-items: center; justify-content: center;
}
.btn-checkout-action:hover:not(:disabled) { background: #0284c7; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(14,165,233,0.3); }
.btn-checkout-action:disabled { background: #cbd5e1; cursor: not-allowed; }

.animate-spin { animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }

:deep(.local-marker) { filter: hue-rotate(120deg) saturate(1.5); }
:deep(.destino-marker) { filter: hue-rotate(0deg); }
</style>
