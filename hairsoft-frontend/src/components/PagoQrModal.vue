<template>
  <transition name="fade-overlay">
    <div class="qr-fullscreen-overlay">
      <div class="qr-fullscreen-content">
        <div class="qr-fullscreen-header">
          <h2>Escaneá el código QR</h2>
          <p>Con la cámara de tu billetera virtual</p>
        </div>

        <div class="qr-fullscreen-amount">
          <span class="fs-amount-label">{{ montoLabel }}</span>
          <span class="fs-amount-valor">${{ montoFormateado }}</span>
          <span v-if="montoExtra" class="fs-amount-extra">{{ montoExtra }}</span>
          <span v-if="montoAviso" class="fs-amount-aviso">{{ montoAviso }}</span>
        </div>

        <div class="qr-fullscreen-box">
          <div class="qr-box-white">
            <qrcode-vue :value="initPoint" :size="300" level="H" />
          </div>
        </div>

        <div v-if="estado === 'confirmed'" class="qr-fullscreen-status status-ok">
          <div class="status-check">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <span class="status-text">¡Pago confirmado!</span>
          <span class="status-sub">{{ statusOkSub }}</span>
        </div>
        <div v-else class="qr-fullscreen-status status-wait">
          <div class="fs-pending-ring"></div>
          <span class="status-text">Esperando pago...</span>
          <span class="status-sub">Se actualiza automáticamente al recibir el pago</span>
        </div>

        <button
          class="btn-regresar"
          :disabled="botonDeshabilitado"
          @click="estado === 'confirmed' ? emit('continuar') : emit('cancelar')"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          {{ estado === 'confirmed' ? botonContinuar : botonCancelar }}
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue'
import QrcodeVue from 'qrcode.vue'

const props = defineProps({
  initPoint: { type: String, required: true },
  monto: { type: Number, default: 0 },
  montoLabel: { type: String, default: 'Total a pagar' },
  montoExtra: { type: String, default: '' },
  montoAviso: { type: String, default: '' },
  estado: { type: String, default: 'pending' },
  botonCancelar: { type: String, default: 'Cancelar' },
  botonContinuar: { type: String, default: 'Continuar' },
  statusOkSub: { type: String, default: 'El pago quedó registrado' },
  botonDeshabilitado: { type: Boolean, default: false },
})

const emit = defineEmits(['cancelar', 'continuar'])

const montoFormateado = computed(() => Number(props.monto || 0).toFixed(2))
</script>

<style scoped>
/* ============================================
   FULLSCREEN QR OVERLAY (misma estética que Registrar Venta)
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

.btn-regresar:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.fade-overlay-enter-active,
.fade-overlay-leave-active {
  transition: opacity 0.25s ease;
}
.fade-overlay-enter-from,
.fade-overlay-leave-to {
  opacity: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pop-in {
  0% { transform: scale(0.4); opacity: 0; }
  80% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}
</style>