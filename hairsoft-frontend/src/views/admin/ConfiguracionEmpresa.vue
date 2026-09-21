<template>
  <div class="list-container">
    <div class="list-card">
      <header class="list-header">
        <div class="header-content">
          <h1>Ajustes del Local</h1>
          <p>Gestión de identidad corporativa y políticas de reserva</p>
        </div>
        <div class="header-buttons">
          <button @click="guardarCambios" :disabled="guardando || cargando" class="register-button">
            <Save v-if="!guardando" :size="20" />
            <Loader2 v-else class="animate-spin" :size="20" />
            <span>{{ guardando ? 'Guardando...' : 'Guardar Cambios' }}</span>
          </button>
        </div>
      </header>

      <div v-if="cargando" class="no-results">
        <Loader2 class="animate-spin no-results-icon" :size="48" />
        <p>Sincronizando con el servidor...</p>
      </div>

      <div v-else class="fade-in">
        
        <div class="usuarios-count">
          <p><Info :size="20" /> Logo y Marca Visual</p>
        </div>

        <div class="filters-container">
          <div class="logo-upload-section">
            <div class="logo-preview-container">
              <img v-if="previewLogo || config.logo" :src="previewLogo || config.logo" class="logo-img-preview" />
              <Building2 v-else :size="40" class="placeholder-icon" />
            </div>
            
            <div class="upload-controls">
              <label class="upload-btn">
                <i class="ri-image-add-line"></i>
                <span>Seleccionar Logo</span>
                <input type="file" @change="handleFileUpload" accept="image/*" style="display: none;" />
              </label>
              <p class="upload-hint">Inserte su logo con formato: (PNG/JPG)</p>
            </div>
          </div>

          <hr class="divider" style="margin: 26px 0;">

          <div class="login-img-section">
            <div class="login-img-header">
              <div>
                <label class="label-info">Imagen del Login</label>
                <p class="hint-text" style="margin-top: 4px;">
                  Imagen de fondo de la pantalla de ingreso. Si está desactivada o no hay imagen, se usa el fallback visual de marca.
                </p>
              </div>
              <div class="login-img-toggle">
                <button
                  type="button"
                  class="pos-toggle"
                  :class="{ 'pos-toggle-on': config.mostrar_imagen_login }"
                  :aria-pressed="config.mostrar_imagen_login"
                  @click="config.mostrar_imagen_login = !config.mostrar_imagen_login"
                >
                  <span class="pos-toggle-track"></span>
                  <span class="pos-toggle-thumb"></span>
                </button>
                <span class="hint-text" style="margin: 0;">{{ config.mostrar_imagen_login ? 'Activada' : 'Desactivada' }}</span>
              </div>
            </div>

            <div v-if="config.mostrar_imagen_login" class="login-img-controls">
              <div class="login-img-preview-container">
                <img v-if="previewLoginImg || config.imagen_login" :src="previewLoginImg || config.imagen_login" class="login-img-preview" alt="Vista previa de la imagen del Login" />
                <div v-else class="portada-placeholder">
                  <i class="ri-image-line" style="font-size: 1.6rem;"></i>
                  <span>Sin imagen<br/>Se usará el fallback de marca</span>
                </div>
              </div>

              <div class="upload-controls login-img-actions">
                <label class="upload-btn">
                  <i class="ri-image-add-line"></i>
                  <span>{{ previewLoginImg || config.imagen_login ? 'Reemplazar imagen' : 'Seleccionar imagen' }}</span>
                  <input type="file" @change="handleLoginImgUpload" accept="image/*" style="display: none;" />
                </label>
                <button
                  v-if="previewLoginImg || config.imagen_login"
                  type="button"
                  class="login-img-delete"
                  @click="eliminarImagenLogin"
                >
                  <i class="ri-delete-bin-line"></i> Eliminar imagen
                </button>
                <p class="upload-hint">JPG/PNG — recomendado apaisado (16:9 o similar).</p>
              </div>
            </div>
          </div>
        </div>

        <div class="usuarios-count">
          <p><Building2 :size="20" /> Información de Facturación y Contacto</p>
        </div>

        <div class="filters-container">
          <div class="vertical-stack">
            
            <div class="filter-group">
              <label>Razón Social</label>
              <input v-model="config.razon_social" type="text" class="filter-input" placeholder="Nombre legal" />
            </div>

            <div class="row-2-cols">
              <div class="filter-group">
                <label>CUIL / CUIT</label>
                <input v-model="config.cuil_cuit" type="text" class="filter-input" placeholder="XX-XXXXXXXX-X" maxlength="13" />
              </div>
              <div class="filter-group">
                <label>Teléfono</label>
                <input v-model="config.telefono" type="text" class="filter-input" placeholder="3755xxxxxx" maxlength="15" />
              </div>
            </div>

            <div class="filter-group">
              <label>Dirección Comercial</label>
              <input v-model="config.direccion" type="text" class="filter-input" placeholder="Ubicación física del local" />
            </div>
            
            <div class="filter-group">
              <label>Email de Contacto</label>
              <input v-model="config.email" type="email" class="filter-input" placeholder="correo@ejemplo.com" />
            </div>

          </div>
        </div>

        <div class="usuarios-count">
          <p><Clock :size="20" /> Reglas de Negocio y Automatización</p>
        </div>

        <div class="filters-container">
          <div class="vertical-stack">
            
            <div class="process-group">
              <div class="filter-group">
                <label class="label-info">Automatización: Cancelaciones, Modificaciones y Reembolsos</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <input v-model.number="config.margen_horas_cancelacion" type="number" class="filter-input input-short" min="0" />
                  <span class="badge-estado estado-info">Margen de anticipación para cancelación y modificación</span>
                </div>
              </div>

              <div class="filter-group mt-3">
                <label class="label-info">Descuento por Reoferta (Lista de espera)</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <input v-model.number="config.porcentaje_descuento_reoferta" type="number" class="filter-input input-short" min="0" max="100" />
                  <span class="badge-estado estado-info badge-large">%</span>
                </div>
                <small class="hint-text">
                  * Descuento ofrecido a los clientes en lista de espera cuando se libera un turno.
                </small>
              </div>

              <div class="filter-group mt-3">
                <textarea 
                  v-model="config.politica_senia" 
                  class="filter-input" 
                  style="height: 100px; resize: none; padding: 15px; line-height: 1.6;"
                  placeholder="Escribí aquí lo que el cliente leerá antes de pagar la seña..."
                ></textarea>
              </div>
            </div>

            <hr class="divider">

            <div class="process-group">
              <div class="filter-group">
                <label class="label-alert">Automatización: Reactivación de Clientes</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <input v-model.number="config.dias_inactividad_clientes" type="number" class="filter-input input-short" min="1" />
                  <span class="badge-estado estado-alert">Días sin asistir</span>
                </div>
                <small class="hint-text">
                  * Al superar estos días, se envía un WhatsApp automático con promo.
                </small>
              </div>

              <div class="filter-group mt-3">
                <label class="label-alert">Descuento por Reactivación</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <input v-model.number="config.porcentaje_descuento_promo" type="number" class="filter-input input-short" min="0" max="100" />
                  <span class="badge-estado estado-alert badge-large">%</span>
                </div>
              </div>

              <div class="filter-group mt-3">
                <label class="label-alert">Validez del Cupón (días)</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <input v-model.number="config.dias_validez_promo_reactivacion" type="number" class="filter-input input-short" min="1" />
                  <span class="badge-estado estado-alert">Días de validez</span>
                </div>
                <small class="hint-text">
                  * Tiempo límite para que el cliente use el cupón antes de que venza.
                </small>
              </div>
            </div>

            <hr class="divider">

            <div class="process-group">
              <div class="filter-group">
                <label class="label-success">Logística: Motomandados / Envíos</label>
                <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #94a3b8;">El costo se calcula como: Tarifa base + (distancia en km × precio por km)</p>

                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 15px;">
                  <div>
                    <label>Tarifa Base ($)</label>
                    <input v-model.number="configEnvios.tarifa_base_envio" type="number" class="filter-input input-short" min="0" step="50" style="width: 100% !important;" />
                  </div>
                  <div>
                    <label>Precio por Km ($)</label>
                    <input v-model.number="configEnvios.precio_por_km" type="number" class="filter-input input-short" min="0" step="10" style="width: 100% !important;" />
                  </div>
                  <div>
                    <label>Radio de Cobertura (km)</label>
                    <input v-model.number="configEnvios.radio_cobertura_km" type="number" class="filter-input input-short" min="0" step="1" style="width: 100% !important;" />
                    <small style="color: #94a3b8; display: block; margin-top: 4px;">Máx. distancia para envío</small>
                  </div>
                </div>

                <div style="margin-top: 15px;">
                  <label>Ubicación del Local (arrastrá el marcador)</label>
                  <div style="height: 350px; border-radius: 12px; overflow: hidden; border: 2px solid var(--border-color); margin-top: 8px;">
                    <l-map
                      ref="mapRef"
                      :zoom="15"
                      :center="[configEnvios.latitud_local, configEnvios.longitud_local]"
                      @click="moverMarcador"
                      style="height: 100%; width: 100%;"
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
                        :lat-lng="[configEnvios.latitud_local, configEnvios.longitud_local]"
                        draggable
                        @dragend="marcadorArrastrado"
                      ></l-marker>
                    </l-map>
                  </div>
                  <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 10px;">
                    <small class="hint-text">Lat: {{ configEnvios.latitud_local?.toFixed(4) }} &mdash; Lng: {{ configEnvios.longitud_local?.toFixed(4) }}</small>
                    <small v-if="direccionLocal" class="hint-text" style="color: #10b981; font-weight: 600;">
                      <i class="fas fa-map-pin"></i> {{ direccionLocal }}
                    </small>
                  </div>
                  <div class="filter-group" style="margin-top: 10px;">
                    <label>Referencia / Detalle del Local</label>
                    <input v-model="configEnvios.direccion_referencia" type="text" class="filter-input" placeholder="Ej: Galería Colón, Local 5, 1er Piso" />
                  </div>
                  <div class="filter-group" style="margin-top: 10px;">
                    <label>Alias de Mercado Pago</label>
                    <input v-model="configEnvios.mp_alias" type="text" class="filter-input" placeholder="Ej: hairsoft.mp" />
                  </div>
                </div>

              </div>
            </div>

          </div>
        </div>

        <div class="usuarios-count">
          <p><DollarSign :size="20" /> Punto de Venta (POS) — Montos rápidos de efectivo</p>
        </div>

        <div class="filters-container">
          <div style="display: flex; flex-direction: column; gap: 25px;">

            <div class="filter-group">
              <label class="label-info">Montos rápidos de efectivo</label>
              <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                <button
                  type="button"
                  class="pos-toggle"
                  :class="{ 'pos-toggle-on': config.montos_rapidos_activos }"
                  :aria-pressed="config.montos_rapidos_activos"
                  @click="config.montos_rapidos_activos = !config.montos_rapidos_activos"
                >
                  <span class="pos-toggle-track"></span>
                  <span class="pos-toggle-thumb"></span>
                </button>
                <span class="hint-text" style="margin: 0;">
                  {{ config.montos_rapidos_activos
                      ? 'Activados: el POS muestra los botones con los montos configurados.'
                      : 'Desactivados: el cajero escribe el importe manualmente en el POS.' }}
                </span>
              </div>
              <small v-if="config.montos_rapidos_activos" class="hint-text">
                * Los botones aparecen al cobrar en el POS, tanto para el pago en efectivo como para el primer paso del pago mixto.
              </small>
            </div>

            <template v-if="config.montos_rapidos_activos">
              <hr class="divider">

              <div class="filter-group">
                <label class="label-info">Montos configurados</label>
                <div v-if="config.montos_rapidos_efectivo.length === 0" class="pos-vacio">
                  <p><i class="ri-information-line"></i> No hay montos configurados. En el POS no se mostrarán botones y el importe se ingresará manualmente.</p>
                </div>
                <div v-else class="pos-chips">
                  <div
                    v-for="(monto, idx) in config.montos_rapidos_efectivo"
                    :key="idx"
                    class="pos-chip"
                  >
                    <template v-if="montoEditandoIdx === idx">
                      <span class="monto-symbol">$</span>
                      <input
                        v-model.number="montoEditandoValor"
                        type="number"
                        class="filter-input pos-chip-input"
                        min="0"
                        step="0.01"
                        @keydown.enter="guardarEdicionMonto"
                      />
                      <button type="button" class="pos-chip-btn pos-chip-ok" title="Guardar monto" @click="guardarEdicionMonto">
                        <i class="ri-check-line"></i>
                      </button>
                      <button type="button" class="pos-chip-btn" title="Cancelar edición" @click="cancelarEdicionMonto">
                        <i class="ri-close-line"></i>
                      </button>
                    </template>
                    <template v-else>
                      <span class="pos-chip-monto">${{ monto.toLocaleString() }}</span>
                      <button type="button" class="pos-chip-btn" title="Editar monto" @click="iniciarEdicionMonto(idx)">
                        <i class="ri-pencil-line"></i>
                      </button>
                      <button type="button" class="pos-chip-btn" title="Eliminar monto" @click="eliminarMonto(idx)">
                        <i class="ri-delete-bin-line"></i>
                      </button>
                    </template>
                  </div>
                </div>
              </div>

              <div class="filter-group">
                <label class="label-info">Agregar monto</label>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                  <span class="monto-symbol" style="font-size: 1.2rem;">$</span>
                  <input
                    v-model.number="nuevoMonto"
                    type="number"
                    class="filter-input pos-add-input"
                    min="0"
                    step="0.01"
                    placeholder="Ej: 10000"
                    @keydown.enter="agregarMonto"
                  />
                  <button type="button" class="pos-btn-add" @click="agregarMonto">
                    <i class="ri-add-line"></i> Agregar monto
                  </button>
                </div>
                <div v-if="errorMonto" class="pos-error">
                  <i class="ri-error-warning-line"></i> {{ errorMonto }}
                </div>
              </div>
            </template>

          </div>
        </div>

        <div class="usuarios-count">
          <p><Store :size="20" /> Infraestructura del Local</p>
        </div>

        <div class="filters-container">
          <div style="display: flex; flex-direction: column; gap: 30px;">
            <GestionSillas />
            
            <hr class="divider">
            
            <GestionCajas />  
          </div>
        </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from '../../utils/axiosConfig'
import { Building2, Clock, Save, Loader2, Info, Store, DollarSign } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import GestionSillas from '@/components/GestionSillas.vue'; 
import GestionCajas from '@/components/GestionCajas.vue';
import { LMap, LTileLayer, LMarker, LControlLayers } from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const config = ref({
  razon_social: '',
  cuil_cuit: '',
  direccion: '',
  telefono: '',
  email: '',
  margen_horas_cancelacion: 3,
  porcentaje_descuento_reoferta: 15,
  dias_inactividad_clientes: 60,
  porcentaje_descuento_promo: 15,
  dias_validez_promo_reactivacion: 7,
  politica_senia: '',
  logo: null,
  imagen_portada: null,
  imagen_login: null,
  mostrar_imagen_login: true,
  costo_envio_moto: 1500,
  montos_rapidos_activos: true,
  montos_rapidos_efectivo: [],
})

const configEnvios = ref({
  latitud_local: -26.8083,
  longitud_local: -54.4362,
  tarifa_base_envio: 500,
  precio_por_km: 300,
  radio_cobertura_km: 10,
  direccion_referencia: '',
  mp_alias: ''
})

const direccionLocal = ref('')

const cargando = ref(true)
const guardando = ref(false)
const previewLogo = ref(null)
const logoFile = ref(null)
const previewPortada = ref(null)
const portadaFile = ref(null)
const previewLoginImg = ref(null)
const loginImgFile = ref(null)
const eliminarLoginImg = ref(false)

// Estado del editor de montos rápidos (POS)
const nuevoMonto = ref(null)
const montoEditandoIdx = ref(null)
const montoEditandoValor = ref(null)
const errorMonto = ref('')

const tilesBase = [
  { name: 'Calle', url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', visible: true, att: '&copy; <a href="https://osm.org">OpenStreetMap</a>' },
  { name: 'Satelital', url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', visible: false, att: '&copy; <a href="https://esri.com">Esri</a>' },
  { name: 'Relieve', url: 'https://tile.opentopomap.org/{z}/{x}/{y}.png', visible: false, att: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a>' },
]

const reverseGeocode = async (lat, lng) => {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`,
      { headers: { 'Accept-Language': 'es' } }
    )
    const data = await res.json()
    if (data && data.display_name) {
      direccionLocal.value = data.display_name
    } else {
      direccionLocal.value = ''
    }
  } catch {
    direccionLocal.value = ''
  }
}

const actualizarCoordenadas = (lat, lng) => {
  configEnvios.value.latitud_local = lat
  configEnvios.value.longitud_local = lng
  reverseGeocode(lat, lng)
}

const moverMarcador = (event) => {
  actualizarCoordenadas(event.latlng.lat, event.latlng.lng)
}

const marcadorArrastrado = (event) => {
  actualizarCoordenadas(event.target.getLatLng().lat, event.target.getLatLng().lng)
}

const obtenerConfig = async () => {
  try {
    const [resConfig, resEnvios] = await Promise.all([
      axios.get('/api/configuracion/'),
      axios.get('/api/configuracion-local/').catch(() => ({ data: {} }))
    ])
    const data = resConfig.data

    if (data.logo) {
      data.logo = `${data.logo}?t=${new Date().getTime()}`;
    }
    
    if (data.imagen_login) {
      data.imagen_login = `${data.imagen_login}?t=${new Date().getTime()}`;
    }
    if(data.mostrar_imagen_login === undefined) data.mostrar_imagen_login = true;
    if(data.imagen_login === undefined) data.imagen_login = null;
    
    if(data.costo_envio_moto === undefined) data.costo_envio_moto = 1500;
    if(data.porcentaje_descuento_promo === undefined) data.porcentaje_descuento_promo = 15;
    if(data.porcentaje_descuento_reoferta === undefined) data.porcentaje_descuento_reoferta = 15;
    if(data.dias_validez_promo_reactivacion === undefined) data.dias_validez_promo_reactivacion = 7;
    if(data.montos_rapidos_activos === undefined) data.montos_rapidos_activos = true;
    if(!Array.isArray(data.montos_rapidos_efectivo)) data.montos_rapidos_efectivo = [];

    config.value = data

    if (resEnvios.data && Object.keys(resEnvios.data).length > 0) {
      configEnvios.value = resEnvios.data
    }
    reverseGeocode(configEnvios.value.latitud_local, configEnvios.value.longitud_local)
  } catch (e) {
    console.error(e)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar la configuración',
      background: '#0f172a',
      color: '#f8fafc'
    })
  } finally {
    cargando.value = false
  }
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    logoFile.value = file
    previewLogo.value = URL.createObjectURL(file)
  }
}

const handlePortadaUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    portadaFile.value = file
    previewPortada.value = URL.createObjectURL(file)
  }
}

// ============================================
// IMAGEN DEL LOGIN
// ============================================
const handleLoginImgUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    loginImgFile.value = file
    previewLoginImg.value = URL.createObjectURL(file)
    eliminarLoginImg.value = false
  }
}

const eliminarImagenLogin = () => {
  loginImgFile.value = null
  previewLoginImg.value = null
  config.value.imagen_login = null
  eliminarLoginImg.value = true
}

// ============================================
// MONTOS RÁPIDOS DE EFECTIVO (POS)
// ============================================
const normalizarMonto = (valor) => {
  const num = Number(valor)
  if (!Number.isFinite(num)) return null
  return Number.isInteger(num) ? num : Math.round(num * 100) / 100
}

const validarMonto = (valor, excluirIdx = null) => {
  if (valor === null || valor === undefined || valor === '') {
    return 'Ingresá un monto válido.'
  }
  const num = normalizarMonto(valor)
  if (num === null || num <= 0) {
    return 'El monto debe ser un número positivo.'
  }
  const duplicado = config.value.montos_rapidos_efectivo.findIndex(
    (m, i) => i !== excluirIdx && Number(m) === num
  )
  if (duplicado !== -1) {
    return `El monto $${num.toLocaleString()} ya está configurado.`
  }
  return null
}

const agregarMonto = () => {
  errorMonto.value = ''
  const err = validarMonto(nuevoMonto.value)
  if (err) {
    errorMonto.value = err
    return
  }
  const num = normalizarMonto(nuevoMonto.value)
  config.value.montos_rapidos_efectivo.push(num)
  nuevoMonto.value = null
}

const iniciarEdicionMonto = (idx) => {
  errorMonto.value = ''
  montoEditandoIdx.value = idx
  montoEditandoValor.value = config.value.montos_rapidos_efectivo[idx]
}

const guardarEdicionMonto = () => {
  if (montoEditandoIdx.value === null) return
  errorMonto.value = ''
  const err = validarMonto(montoEditandoValor.value, montoEditandoIdx.value)
  if (err) {
    errorMonto.value = err
    return
  }
  const num = normalizarMonto(montoEditandoValor.value)
  config.value.montos_rapidos_efectivo[montoEditandoIdx.value] = num
  montoEditandoIdx.value = null
  montoEditandoValor.value = null
}

const cancelarEdicionMonto = () => {
  montoEditandoIdx.value = null
  montoEditandoValor.value = null
  errorMonto.value = ''
}

const eliminarMonto = (idx) => {
  config.value.montos_rapidos_efectivo.splice(idx, 1)
  if (montoEditandoIdx.value === idx) cancelarEdicionMonto()
}

const validarFormulario = () => {
  const cuitRegex = /^\d{2}-\d{8}-\d{1}$/;
  
  if (!config.value.razon_social.trim()) return "La Razón Social es obligatoria.";
  if (!cuitRegex.test(config.value.cuil_cuit)) return "El CUIT debe tener el formato exacto XX-XXXXXXXX-X.";
  if (config.value.telefono.length > 15) return "El teléfono no puede superar los 15 dígitos.";
  if (!config.value.email.includes('@')) return "El email debe ser válido.";
  if (config.value.dias_inactividad_clientes < 1) return "Los días de inactividad deben ser al menos 1.";
  if (config.value.costo_envio_moto < 0) return "El costo de envío no puede ser negativo.";
  if (config.value.porcentaje_descuento_promo < 0 || config.value.porcentaje_descuento_promo > 100) return "El descuento de promo debe ser entre 0 y 100.";
  if (config.value.porcentaje_descuento_reoferta < 0 || config.value.porcentaje_descuento_reoferta > 100) return "El descuento de reoferta debe ser entre 0 y 100.";
  if (config.value.dias_validez_promo_reactivacion < 1) return "La validez del cupón debe ser al menos 1 día.";

  return null; 
}

const guardarCambios = async () => {
  const errorMsg = validarFormulario();
  if (errorMsg) {
    return Swal.fire({
      icon: 'warning',
      title: 'Validación',
      text: errorMsg,
      background: '#0f172a',
      color: '#f8fafc'
    });
  }

  guardando.value = true

  const formData = new FormData();
  formData.append('razon_social', config.value.razon_social);
  formData.append('cuil_cuit', config.value.cuil_cuit);
  formData.append('direccion', config.value.direccion);
  formData.append('telefono', config.value.telefono);
  formData.append('email', config.value.email);
  formData.append('margen_horas_cancelacion', config.value.margen_horas_cancelacion);
  formData.append('porcentaje_descuento_reoferta', config.value.porcentaje_descuento_reoferta);
  formData.append('dias_inactividad_clientes', config.value.dias_inactividad_clientes);
  formData.append('porcentaje_descuento_promo', config.value.porcentaje_descuento_promo);
  formData.append('dias_validez_promo_reactivacion', config.value.dias_validez_promo_reactivacion);
  formData.append('politica_senia', config.value.politica_senia);
  formData.append('costo_envio_moto', config.value.costo_envio_moto);
  formData.append('montos_rapidos_activos', config.value.montos_rapidos_activos ? 'true' : 'false');
  formData.append('montos_rapidos_efectivo', JSON.stringify(config.value.montos_rapidos_efectivo || []));
  
  if (logoFile.value) {
    formData.append('logo', logoFile.value);
  }

  if (portadaFile.value) {
    formData.append('imagen_portada', portadaFile.value);
  }

  if (loginImgFile.value) {
    formData.append('imagen_login', loginImgFile.value);
  } else if (eliminarLoginImg.value) {
    // Cadena vacía → el backend borra la imagen (ImagenBorrableField)
    formData.append('imagen_login', '');
  }
  formData.append('mostrar_imagen_login', config.value.mostrar_imagen_login ? 'true' : 'false');

  try {
    await Promise.all([
      axios.post('/api/configuracion/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      }),
      axios.post('/api/configuracion-local/', {
        latitud_local: configEnvios.value.latitud_local,
        longitud_local: configEnvios.value.longitud_local,
        tarifa_base_envio: configEnvios.value.tarifa_base_envio,
        precio_por_km: configEnvios.value.precio_por_km,
        radio_cobertura_km: configEnvios.value.radio_cobertura_km,
        direccion_referencia: configEnvios.value.direccion_referencia,
        mp_alias: configEnvios.value.mp_alias
      })
    ])
    
    await Swal.fire({
      icon: 'success',
      title: '¡Ajustes guardados!',
      text: 'La configuración del local ha sido actualizada.',
      timer: 2000,
      showConfirmButton: false,
      background: '#0f172a',
      color: '#f8fafc'
    })

    window.location.reload();

  } catch (e) {
    console.error(e)
    Swal.fire({
      icon: 'error',
      title: 'Fallo al guardar',
      text: 'Ocurrió un error al procesar la solicitud.',
      background: '#0f172a',
      color: '#f8fafc'
    })
  } finally {
    guardando.value = false
  }
}

onMounted(obtenerConfig)
</script>

<style scoped>
.list-container { padding: 32px; max-width: 1200px; margin: 0 auto; min-height: 100vh; font-family: 'Inter', sans-serif; }
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; }
.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; display: flex; align-items: center; gap: 10px; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); }
.register-button:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); }
.logo-upload-section { display: flex; align-items: center; gap: 30px; }
.logo-preview-container { width: 120px; height: 120px; border: 2px dashed var(--border-color); border-radius: 18px; display: flex; align-items: center; justify-content: center; overflow: hidden; background: var(--bg-primary); }
.logo-img-preview { width: 100%; height: 100%; object-fit: cover; }
.portada-preview-container { width: 320px; height: 140px; border: 2px dashed var(--border-color); border-radius: 18px; display: flex; align-items: center; justify-content: center; overflow: hidden; background: var(--bg-primary); }
.portada-img-preview { width: 100%; height: 100%; object-fit: cover; }
.portada-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; opacity: 0.4; color: var(--text-secondary); font-size: 0.8rem; text-align: center; padding: 0 20px; }
.placeholder-icon { opacity: 0.3; color: var(--text-secondary); }
.upload-btn { background: var(--bg-tertiary); color: var(--text-primary); padding: 10px 20px; border-radius: 10px; border: 1px solid var(--border-color); cursor: pointer; font-weight: 700; display: flex; align-items: center; gap: 8px; transition: 0.3s; font-size: 0.9rem; }
.upload-btn:hover { background: var(--hover-bg); transform: translateY(-2px); border-color: #0ea5e9; }
.upload-hint { font-size: 0.8rem; color: var(--text-tertiary); margin-top: 8px; font-style: italic; }
.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 30px; border-radius: 16px; border: 1px solid var(--border-color); }
.vertical-stack { display: flex; flex-direction: column; gap: 25px; }
.row-2-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.filter-group { display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 12px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }
.filter-input { padding: 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 1rem; transition: all 0.3s; width: 100%; }
.input-short { width: 120px !important; text-align: center; font-weight: bold; }
.filter-input:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); }

/* Etiquetas de colores — ahora usan clases en vez de style inline */
.label-info  { color: #0ea5e9 !important; }
.label-alert { color: #f97316 !important; }
.label-success { color: #10b981 !important; }

/* Símbolo $ */
.currency-symbol { font-weight: bold; color: var(--text-secondary); font-size: 1.2rem; }

/* Hints */
.hint-text { color: var(--text-secondary); margin-top: 8px; font-size: 0.85rem; }

/* Sección de título — FIX PRINCIPAL: reemplaza color: #fff hardcodeado */
.usuarios-count { display: flex; justify-content: space-between; align-items: center; margin: 40px 0 20px; padding: 15px 25px; background: var(--bg-primary); border-radius: 12px; border-left: 5px solid var(--accent-color); }
.usuarios-count p { color: var(--text-primary); font-weight: 700; margin: 0; display: flex; align-items: center; gap: 10px; font-size: 1.1rem; }

.badge-estado { padding: 8px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
.badge-large { font-size: 1.2rem !important; }
.estado-info { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border: 2px solid #0ea5e9; }
.estado-alert { background: rgba(249, 115, 22, 0.1); color: #f97316; border: 2px solid #f97316; }
.divider { border: 0; height: 1px; background: var(--border-color); margin: 15px 0; opacity: 0.3; }
.animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.no-results { text-align: center; padding: 100px 0; color: var(--text-secondary); }
.no-results-icon { margin-bottom: 20px; color: var(--accent-color); }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@media (max-width: 768px) {
  .row-2-cols { grid-template-columns: 1fr; }
  .logo-upload-section { flex-direction: column; text-align: center; }
  .portada-preview-container { width: 100%; max-width: 320px; }
}

/* ===== PUNTO DE VENTA (POS): Montos rápidos de efectivo ===== */
.pos-toggle { position: relative; width: 54px; height: 28px; border: none; background: var(--bg-tertiary); border-radius: 20px; cursor: pointer; padding: 0; transition: background 0.25s ease; flex-shrink: 0; }
.pos-toggle-thumb { position: absolute; top: 3px; left: 3px; width: 22px; height: 22px; background: #fff; border-radius: 50%; transition: transform 0.25s ease; box-shadow: 0 2px 6px rgba(0,0,0,.35); }
.pos-toggle-on { background: linear-gradient(135deg, #0ea5e9, #0284c7); }
.pos-toggle-on .pos-toggle-thumb { transform: translateX(26px); }

.pos-chips { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 6px; }
.pos-chip { display: flex; align-items: center; gap: 6px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 12px; padding: 6px 8px 6px 14px; }
.pos-chip-monto { font-weight: 800; font-size: 1rem; color: var(--text-primary); }
.pos-chip-input { width: 130px !important; padding: 8px 10px; font-weight: 700; }
.pos-chip-btn { width: 30px; height: 30px; border-radius: 8px; border: none; background: var(--bg-tertiary); color: var(--text-secondary); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: all .2s; font-size: .95rem; }
.pos-chip-btn:hover { background: var(--hover-bg); color: var(--text-primary); }
.pos-chip-ok { color: #10b981; }
.pos-chip-ok:hover { background: rgba(16,185,129,.12); color: #10b981; }

.pos-add-input { width: 200px !important; }
.pos-btn-add { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 12px 22px; border-radius: 10px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all .25s; }
.pos-btn-add:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(14,165,233,.35); }

.pos-vacio { background: var(--bg-primary); border: 1px dashed var(--border-color); border-radius: 12px; padding: 16px; margin-top: 6px; }
.pos-vacio p { margin: 0; color: var(--text-secondary); font-size: .9rem; display: flex; align-items: center; gap: 8px; }
.pos-error { margin-top: 10px; color: #f87171; font-size: .88rem; font-weight: 600; display: flex; align-items: center; gap: 6px; background: rgba(248,113,113,.08); border: 1px solid rgba(248,113,113,.3); border-radius: 10px; padding: 8px 12px; width: fit-content; }

/* ===== IMAGEN DEL LOGIN (Ajustes del Local) ===== */
.login-img-section { display: flex; flex-direction: column; gap: 18px; }
.login-img-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; flex-wrap: wrap; }
.login-img-toggle { display: flex; align-items: center; gap: 10px; padding-top: 4px; }
.login-img-controls { display: flex; align-items: flex-start; gap: 24px; flex-wrap: wrap; }
.login-img-preview-container { width: 340px; max-width: 100%; height: 150px; border: 2px dashed var(--border-color); border-radius: 18px; display: flex; align-items: center; justify-content: center; overflow: hidden; background: var(--bg-primary); }
.login-img-preview { width: 100%; height: 100%; object-fit: cover; }
.login-img-actions { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; }
.login-img-delete { background: transparent; color: #f87171; border: 1.5px solid rgba(248,113,113,.45); padding: 10px 18px; border-radius: 10px; cursor: pointer; font-weight: 700; font-size: 0.88rem; display: flex; align-items: center; gap: 8px; transition: all .25s; font-family: inherit; }
.login-img-delete:hover { background: rgba(248,113,113,.12); border-color: #f87171; transform: translateY(-1px); }
</style>