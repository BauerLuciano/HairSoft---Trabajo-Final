<template>
  <div class="envio-panel">
    <div class="envio-header" @click="abierto = !abierto">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
        width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        class="chevron" :class="{ rotado: abierto }"
      >
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </div>

    <div v-if="abierto" class="envio-body">
      <div class="envio-form-row">
        <div class="envio-field" style="flex: 1;">
          <label>Dirección de Entrega</label>
          <input
            v-model="direccion"
            type="text"
            class="envio-input"
            placeholder="Calle y número, barrio, referencias..."
          />
        </div>
      </div>

      <div style="height: 280px; border-radius: 10px; overflow: hidden; border: 2px solid var(--border-color); margin-top: 10px;">
        <l-map
          :zoom="14"
          :center="centroMapa"
          @click="seleccionarDestino"
          style="height: 100%; width: 100%;"
        >
          <l-tile-layer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            layer-type="base"
            name="OpenStreetMap"
          ></l-tile-layer>
          <l-marker
            v-if="destino"
            :lat-lng="destino"
            draggable
            @dragend="marcadorDestinoArrastrado"
          ></l-marker>
        </l-map>
      </div>

      <div class="envio-coords" v-if="destino">
        <small>Lat: {{ destino.lat.toFixed(4) }} | Lng: {{ destino.lng.toFixed(4) }}</small>
      </div>

      <div class="envio-actions">
        <button
          @click="calcular"
          :disabled="calculando || !destino"
          class="btn-calcular"
        >
          <svg v-if="!calculando" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 20h9"></path>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
          </svg>
          <Loader2 v-else class="animate-spin" :size="18" />
          {{ calculando ? 'Calculando...' : 'Calcular Costo' }}
        </button>
        <button
          v-if="costoCalculado"
          @click="confirmarEnvio"
          class="btn-confirmar-envio"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Aplicar Envío (${{ costoCalculado.toFixed(2) }})
        </button>
      </div>

      <div v-if="error" class="envio-error">{{ error }}</div>

      <div v-if="costoCalculado && distanciaInfo" class="envio-resumen">
        <div class="resumen-item">
          <span>Distancia</span>
          <strong>{{ distanciaInfo }} km</strong>
        </div>
        <div class="resumen-item">
          <span>Costo de Envío</span>
          <strong>${{ costoCalculado.toFixed(2) }}</strong>
        </div>
        <button @click="quitarEnvio" class="btn-quitar-envio">
          Quitar envío
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { LMap, LTileLayer, LMarker } from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { Loader2 } from 'lucide-vue-next'
import { envioService } from '@/services/envioService'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const emit = defineEmits(['envio-confirmado', 'envio-quitado'])

const abierto = ref(false)
const direccion = ref('')
const destino = ref(null)
const centroMapa = ref([-26.8083, -54.4362])
const costoCalculado = ref(null)
const distanciaInfo = ref(null)
const calculando = ref(false)
const error = ref('')

const seleccionarDestino = (event) => {
  destino.value = { lat: event.latlng.lat, lng: event.latlng.lng }
  error.value = ''
}

const marcadorDestinoArrastrado = (event) => {
  const ll = event.target.getLatLng()
  destino.value = { lat: ll.lat, lng: ll.lng }
}

const calcular = async () => {
  if (!destino.value) return
  calculando.value = true
  error.value = ''
  try {
    const res = await envioService.calcularCosto(destino.value.lat, destino.value.lng)
    costoCalculado.value = res.data.costo_envio
    distanciaInfo.value = res.data.distancia_km
  } catch (e) {
    error.value = 'Error al calcular costo de envío'
    console.error(e)
  } finally {
    calculando.value = false
  }
}

const confirmarEnvio = () => {
  if (!costoCalculado.value || !direccion.value.trim()) {
    error.value = 'Completá la dirección antes de confirmar'
    return
  }
  emit('envio-confirmado', {
    direccion_entrega: direccion.value,
    latitud_destino: destino.value.lat,
    longitud_destino: destino.value.lng,
    costo_envio: costoCalculado.value,
    distancia_km: distanciaInfo.value
  })
}

const quitarEnvio = () => {
  costoCalculado.value = null
  distanciaInfo.value = null
  destino.value = null
  direccion.value = ''
  emit('envio-quitado')
}
</script>

<style scoped>
.envio-panel {
  background: var(--hover-bg, #1e293b);
  border: 1px solid var(--border-color, #334155);
  border-radius: 16px;
  overflow: hidden;
  margin-top: 15px;
}

.envio-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  cursor: pointer;
  color: var(--text-primary, #f8fafc);
  font-weight: 600;
  transition: 0.3s;
}

.envio-header:hover {
  background: rgba(59, 130, 246, 0.08);
}

.envio-costo-badge {
  margin-left: auto;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
}

.chevron { transition: transform 0.3s; margin-left: 8px; }
.rotado { transform: rotate(180deg); }

.envio-body {
  padding: 16px 18px 18px;
  border-top: 1px solid var(--border-color, #334155);
}

.envio-form-row {
  display: flex;
  gap: 12px;
}

.envio-field label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-secondary, #94a3b8);
  margin-bottom: 6px;
  font-weight: 700;
}

.envio-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid var(--border-color, #334155);
  border-radius: 10px;
  background: var(--bg-primary, #0f172a);
  color: var(--text-primary, #f8fafc);
  font-size: 0.9rem;
}

.envio-input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
}

.envio-coords {
  margin-top: 8px;
  text-align: center;
  color: var(--text-secondary, #94a3b8);
  font-size: 0.8rem;
}

.envio-actions {
  display: flex;
  gap: 12px;
  margin-top: 14px;
}

.btn-calcular, .btn-confirmar-envio {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: 0.3s;
}

.btn-calcular {
  background: var(--bg-tertiary, #1e293b);
  color: var(--text-primary, #f8fafc);
  border: 2px solid var(--border-color, #334155);
}

.btn-calcular:hover:not(:disabled) {
  border-color: #0ea5e9;
  background: rgba(14, 165, 233, 0.1);
}

.btn-confirmar-envio {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
}

.btn-confirmar-envio:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
}

.envio-error {
  margin-top: 10px;
  padding: 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #ef4444;
  font-size: 0.85rem;
  text-align: center;
}

.envio-resumen {
  margin-top: 14px;
  padding: 14px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.resumen-item {
  display: flex;
  flex-direction: column;
  color: var(--text-secondary, #94a3b8);
  font-size: 0.8rem;
}

.resumen-item strong {
  color: #10b981;
  font-size: 1rem;
}

.btn-quitar-envio {
  background: transparent;
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  transition: 0.3s;
}

.btn-quitar-envio:hover {
  background: rgba(239, 68, 68, 0.1);
}

.animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>
