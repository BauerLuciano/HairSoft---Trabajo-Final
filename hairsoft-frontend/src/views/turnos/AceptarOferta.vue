<template>
  <div class="page-container">
    <div class="offer-card animate-in">
      
      <div class="card-header">
        <h1>¡Turno Disponible!</h1>
        <p class="subtitle" v-if="info.descuento_porcentaje">
          Se liberó un espacio y tenés el <span class="highlight-text">{{ info.descuento_porcentaje }}% de descuento</span>.
        </p>
        <p class="subtitle" v-else>
          ¡Se liberó un espacio exclusivo para vos!
        </p>
        <div class="header-glow"></div>
      </div>

      <div class="card-body">
        
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <p>Calculando tu saldo a favor...</p>
        </div>

        <div v-else-if="errorMsg" class="state-box error">
          <div class="emoji-icon">😢</div>
          <h3>¡Uh, qué pena!</h3>
          <p>{{ errorMsg }}</p>
          <button @click="volver" class="btn-outline">Volver al inicio</button>
        </div>

        <div v-else-if="successMsg" class="state-box success">
          <div class="emoji-icon">✨</div>
          <h3>¡Turno Canjeado!</h3>
          <p class="msg-text">{{ successMsg }}</p>
          <div class="ticket-cut"></div>
          <p class="sub-msg">Te esperamos el <strong>{{ formatFecha(info.fecha) }}</strong> a las <strong>{{ formatHora(info.hora) }}hs</strong>.</p>
          <button @click="volver" class="btn-primary full">{{ autenticado ? 'Ver en Mis Turnos' : 'Iniciar Sesión' }}</button>
        </div>

        <div v-else>
          
          <div class="turno-preview">
            <div class="tp-row">
              <span class="tp-label">Profesional</span>
              <span class="tp-val">{{ info.profesional }}</span>
            </div>
            <div class="tp-row">
              <span class="tp-label">Fecha</span>
              <span class="tp-val date-val">{{ formatFecha(info.fecha) }}</span>
            </div>
            <div class="tp-row">
              <span class="tp-label">Hora</span>
              <span class="tp-val time-val">{{ formatHora(info.hora) }}hs</span>
            </div>
            <div class="tp-row">
              <span class="tp-label">Servicio</span>
              <span class="tp-val">{{ info.servicio }}</span>
            </div>
          </div>

          <div class="offer-box" v-if="info.descuento_porcentaje">
            <div class="offer-badge">-{{ info.descuento_porcentaje }}% OFF</div>
            <div class="price-compare">
              <div class="p-old">
                <span>Precio Regular</span>
                <del>${{ formatPrecio(info.precio_original) }}</del>
              </div>
              <div class="p-divider">
                <i class="bi bi-arrow-right"></i>
              </div>
              <div class="p-new">
                <span>Precio Oferta</span>
                <strong>${{ formatPrecio(info.precio_final) }}</strong>
              </div>
            </div>
          </div>

          <div class="wallet-section">
            <div class="wallet-header">
              <div class="wallet-title">
                <i class="bi bi-wallet2 me-2"></i> Tu Pago Anterior
              </div>
              <span class="wallet-amount">${{ formatPrecio(info.pagado_anterior) }}</span>
            </div>

            <div v-if="info.saldo_a_favor > 0" class="result-box winner">
              <div class="result-icon"><i class="bi bi-check-circle-fill"></i></div>
              <div class="result-title">¡TE SOBRA DINERO!</div>
              <div class="result-amount">
                + ${{ formatPrecio(info.saldo_a_favor) }}
              </div>
              <p class="result-desc">
                Este saldo queda a tu favor. <strong>¡El cambio te sale GRATIS!</strong>
              </p>
            </div>

            <div v-else-if="info.monto_final_a_pagar > 0" class="result-box owing">
              <div class="result-icon"><i class="bi bi-exclamation-circle-fill"></i></div>
              <div class="result-title">Solo abonás la diferencia</div>
              <div class="result-amount">
                ${{ formatPrecio(info.monto_final_a_pagar) }}
              </div>
              <p class="result-desc">Se descuenta lo que ya pagaste. Pagarás el resto en el local.</p>
            </div>
            
            <div v-else class="result-box zero">
              <div class="result-icon"><i class="bi bi-shield-check"></i></div>
              <div class="result-title">¡Cubierto al 100%!</div>
              <div class="result-amount">$0.00</div>
              <p class="result-desc">Tu pago anterior cubre todo el costo.</p>
            </div>
          </div>

          <div class="actions">
            <button @click="confirmarOferta" class="btn-primary full shine-effect" :disabled="procesando">
              <span v-if="!procesando" class="btn-content">
                <i class="bi bi-check2-circle"></i> 
                {{ info.saldo_a_favor > 0 ? 'ACEPTAR Y CANJEAR GRATIS' : 'CONFIRMAR CANJE' }}
              </span>
              <span v-else class="btn-content">
                <i class="bi bi-arrow-repeat spin"></i> Procesando...
              </span>
            </button>
            <button @click="volver" class="btn-text">Mantener mi turno anterior</button>
          </div>
          
          <p class="disclaimer">Al aceptar, tu turno anterior se cancelará automáticamente y conservaremos tu pago para este nuevo horario.</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from '../../utils/axiosConfig';
import Swal from 'sweetalert2';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const info = ref({});
const errorMsg = ref("");
const successMsg = ref("");
const procesando = ref(false);

const turnoId = route.params.turno_id;
const token = route.params.token;

const autenticado = ref(false);

const formatPrecio = (v) => {
  if (v === undefined || v === null) return '0.00';
  const num = parseFloat(v);
  return isNaN(num) ? '0.00' : num.toFixed(2);
};

const formatFecha = (f) => { 
  if(!f) return '-'; 
  if (typeof f === 'string' && f.includes('-')) {
    try {
      const [year, month, day] = f.split('-');
      return `${day}/${month}/${year}`;
    } catch (e) {
      return f;
    }
  }
  if (f instanceof Date || (typeof f === 'string' && Date.parse(f))) {
    try {
      const dateObj = new Date(f);
      return dateObj.toLocaleDateString('es-AR', {
        day: '2-digit', month: '2-digit', year: 'numeric'
      });
    } catch (e) {}
  }
  return f;
};

const formatHora = (h) => { 
  if(!h) return '-';
  if (typeof h === 'string') {
    const match = h.match(/(\d{1,2}):(\d{2})/);
    if (match) {
      return `${match[1].padStart(2, '0')}:${match[2]}`;
    }
  }
  return h;
};

onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/turnos/${turnoId}/oferta-info/${token}/`);
    info.value = data;
    autenticado.value = data.autenticado || false;
  } catch (error) {
    errorMsg.value = error.response?.data?.error || "La oferta ya no está disponible o expiró.";
  } finally {
    loading.value = false;
  }
});

const confirmarOferta = async () => {
  procesando.value = true;
  try {
    const { data } = await axios.post(`/api/turnos/${turnoId}/aceptar-oferta/${token}/`);
    
    if (data.success || data.status === 'ok') {
      // Bloque de saldo a favor con colores fuertes y fondo verde clarito para que resalte
      const saldoMsg = data.saldo_a_favor > 0 ? 
        `<div style="margin-top: 15px; padding: 12px; background: #ecfdf5; border: 1px dashed #10b981; border-radius: 12px; color: #059669; font-weight: 800; font-size: 1.15rem;">
          💚 Saldo a favor: $${formatPrecio(data.saldo_a_favor)}
        </div>` : '';
      
      successMsg.value = data.message || "¡Listo! Tu turno ha sido canjeado.";

      const estaLogueado = autenticado.value;
      
      if (estaLogueado) {
        await Swal.fire({
          title: '<span style="color: #1e3a8a; font-weight: 800; font-size: 1.8rem;">¡Felicitaciones! 🎉</span>',
          html: `
            <div style="font-family: 'Inter', sans-serif; text-align: center;">
              <p style="color: #334155; font-size: 1.1rem; font-weight: 500; margin-bottom: 5px;">
                Tu turno fue canjeado con éxito y ya está confirmado.
              </p>
              ${saldoMsg}
            </div>
          `,
          icon: 'success',
          background: '#ffffff',
          confirmButtonColor: '#1e3a8a',
          confirmButtonText: 'Genial',
          customClass: { popup: 'swal-custom-radius' }
        });
        router.push('/cliente/historial');
      } else {
        await Swal.fire({
          title: '<span style="color: #1e3a8a; font-weight: 800; font-size: 1.8rem;">¡Turno Canjeado! 🎉</span>',
          html: `
            <div style="font-family: 'Inter', sans-serif; text-align: center;">
              <p style="color: #334155; font-size: 1.1rem; font-weight: 500; margin-bottom: 10px;">
                Tu turno fue canjeado con éxito y ya está confirmado.
              </p>
              ${saldoMsg}
              <div style="margin-top: 20px; padding: 16px; background: #f8fafc; border-radius: 12px;">
                <p style="color: #475569; font-size: 0.95rem; margin: 0 0 12px;">
                  Iniciá sesión para ver tu historial de turnos.
                </p>
                <a href="/login" style="display: inline-block; background: #1e3a8a; color: #fff; padding: 10px 32px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 1rem;">
                  Iniciar Sesión
                </a>
              </div>
            </div>
          `,
          icon: 'success',
          background: '#ffffff',
          showConfirmButton: false,
          showCloseButton: true,
          customClass: { popup: 'swal-custom-radius' }
        });
      }
    } else {
      throw new Error(data.error || 'Error desconocido');
    }
  } catch (error) {
    Swal.fire({
      title: '<span style="color: #b91c1c; font-weight: 800;">Error</span>',
      html: `<span style="color: #475569; font-size: 1.05rem;">${error.response?.data?.error || 'No se pudo procesar el canje.'}</span>`,
      icon: 'error',
      background: '#ffffff',
      confirmButtonColor: '#1e3a8a'
    });
  } finally {
    procesando.value = false;
  }
};

const volver = () => {
  if (autenticado.value) {
    router.push('/cliente/historial');
  } else {
    router.push({ name: 'login', query: { redirect: route.fullPath } });
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.page-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f5f9;
  background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
  background-size: 24px 24px;
  font-family: 'Inter', sans-serif;
  padding: 40px 20px;
}

.offer-card {
  background: #ffffff;
  width: 100%;
  max-width: 580px;
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.15), 0 0 0 1px rgba(15, 23, 42, 0.05);
}

/* HEADER AZUL PROFUNDO Y MODERNO */
.card-header {
  background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
  color: #ffffff;
  padding: 45px 35px;
  text-align: center;
  position: relative;
}

.header-glow {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 100px;
  background: #3b82f6;
  filter: blur(80px);
  opacity: 0.4;
  pointer-events: none;
}

.brand-tag {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: #fbbf24; /* Ámbar/Oro sutil */
  display: inline-block;
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 800;
  margin-bottom: 20px;
  letter-spacing: 1px;
  border: 1px solid rgba(251, 191, 36, 0.3);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.card-header h1 { 
  margin: 0; 
  font-size: 2.2rem; 
  color: #ffffff; 
  font-weight: 800; 
  letter-spacing: -0.5px;
}

.subtitle { 
  margin: 12px 0 0; 
  color: #94a3b8; 
  font-size: 1.05rem; 
  line-height: 1.5;
}

.highlight-text {
  color: #fbbf24;
  font-weight: 700;
}

.card-body { 
  padding: 40px 35px; 
  background: #ffffff;
}

/* TURNO PREVIEW - LIMPIO Y ELEGANTE */
.turno-preview { 
  background: #f8fafc;
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 25px; 
  border: 1px solid #e2e8f0;
}

.tp-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px dashed #cbd5e1;
}

.tp-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.tp-row:first-child {
  padding-top: 0;
}

.tp-label { 
  color: #64748b; 
  font-weight: 600;
  font-size: 0.95rem;
}

.tp-val { 
  font-weight: 700; 
  color: #0f172a; 
  font-size: 1.05rem;
  text-align: right;
}

.date-val, .time-val {
  color: #1e3a8a;
}

/* OFFER BOX - PREMIUM */
.offer-box { 
  background: linear-gradient(to right, #eff6ff, #f0fdf4); 
  border-radius: 20px; 
  padding: 25px; 
  position: relative;
  margin-bottom: 25px;
  border: 1px solid #bae6fd;
}

.offer-badge {
  position: absolute;
  top: -15px; 
  right: 25px;
  background: linear-gradient(135deg, #ef4444, #b91c1c); 
  color: white;
  font-weight: 800; 
  font-size: 0.85rem;
  padding: 6px 16px; 
  border-radius: 50px;
  box-shadow: 0 8px 15px rgba(239, 68, 68, 0.25);
}

.price-compare { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}

.p-old, .p-new { 
  display: flex; 
  flex-direction: column; 
}

.p-old span { font-size: 0.85rem; color: #64748b; font-weight: 600; margin-bottom: 4px;}
.p-old del { font-size: 1.2rem; color: #94a3b8; font-weight: 700;}

.p-divider {
  color: #94a3b8;
  font-size: 1.5rem;
  opacity: 0.5;
}

.p-new { text-align: right; }
.p-new span { font-size: 0.85rem; color: #1e3a8a; font-weight: 700; margin-bottom: 4px;}
.p-new strong { font-size: 2.2rem; color: #1e3a8a; font-weight: 900; line-height: 1;}

/* WALLET SECTION */
.wallet-section { 
  background: #ffffff; 
  border-radius: 20px; 
  margin-bottom: 35px; 
  border: 2px solid #f1f5f9;
  overflow: hidden;
}

.wallet-header { 
  background: #f8fafc;
  display: flex; 
  justify-content: space-between; 
  align-items: center;
  padding: 18px 25px;
  border-bottom: 2px solid #f1f5f9;
}

.wallet-title {
  color: #475569;
  font-weight: 700;
  font-size: 0.95rem;
}

.wallet-amount {
  color: #0f172a;
  font-weight: 800;
  font-size: 1.2rem;
}

.result-box { 
  text-align: center; 
  padding: 30px 25px; 
  position: relative;
}

.result-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.winner .result-icon { color: #10b981; }
.owing .result-icon { color: #f59e0b; }
.zero .result-icon { color: #3b82f6; }

.result-title { 
  font-size: 1rem; 
  font-weight: 800; 
  text-transform: uppercase; 
  margin-bottom: 10px; 
  letter-spacing: 0.5px;
}

.winner .result-title { color: #059669; }
.owing .result-title { color: #d97706; }
.zero .result-title { color: #1d4ed8; }

.result-amount { 
  font-size: 3rem; 
  font-weight: 900; 
  margin-bottom: 15px; 
  line-height: 1;
  letter-spacing: -1px;
}

.winner .result-amount { color: #10b981; }
.owing .result-amount { color: #f59e0b; }
.zero .result-amount { color: #3b82f6; }

.result-desc { 
  font-size: 0.95rem; 
  line-height: 1.5; 
  color: #64748b; 
  margin: 0; 
}

/* BOTONES */
.actions { 
  display: flex; 
  flex-direction: column; 
  gap: 15px; 
  margin-bottom: 25px;
}

.btn-primary {
  background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
  color: #ffffff; 
  border: none;
  padding: 20px; 
  border-radius: 16px; 
  font-weight: 700; 
  font-size: 1.1rem;
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.4);
}

.btn-primary .btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-primary:hover:not(:disabled) { 
  transform: translateY(-3px); 
  box-shadow: 0 20px 35px -5px rgba(30, 58, 138, 0.5); 
}

.btn-primary:disabled {
  background: #cbd5e1;
  box-shadow: none;
  cursor: not-allowed;
}

.btn-text { 
  background: none; 
  border: none; 
  color: #64748b; 
  cursor: pointer; 
  font-size: 0.95rem; 
  padding: 10px;
  font-weight: 600;
  transition: color 0.2s;
}

.btn-text:hover {
  color: #0f172a;
}

.disclaimer { 
  font-size: 0.8rem; 
  text-align: center; 
  color: #94a3b8; 
  margin: 0;
  line-height: 1.5;
}

/* EXTRA ANIMATIONS */
.spin {
  animation: spin 1s linear infinite;
}

.animate-in { 
  animation: scaleUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; 
}

@keyframes scaleUp { 
  0% { opacity: 0; transform: scale(0.95) translateY(20px); } 
  100% { opacity: 1; transform: scale(1) translateY(0); } 
}

@media (max-width: 640px) {
  .card-body { padding: 30px 20px; }
  .card-header { padding: 35px 20px; }
  .card-header h1 { font-size: 1.8rem; }
  .result-amount { font-size: 2.5rem; }
  .p-new strong { font-size: 1.8rem; }
}

/* 🔥 CORRECCIÓN PARA ESTADOS: CARGA, ERROR Y ÉXITO 🔥 */

.state-box { 
  text-align: center; 
  padding: 40px 20px; 
}

.state-box h3 {
  font-weight: 800;
  font-size: 1.8rem;
  margin-bottom: 10px;
}

/* Color para el texto de Error (Pena) */
.state-box.error h3 { color: #b91c1c; }
.state-box.error p { color: #475569; font-weight: 500; }

/* Color para el texto de Éxito */
.state-box.success h3 { color: #1e3a8a; }
.state-box.success .msg-text { color: #334155; font-weight: 600; }
.state-box.success .sub-msg { color: #64748b; }

/* Color para el texto de Carga */
.state-box p { color: #1e3a8a; font-weight: 600; }

.emoji-icon { 
  font-size: 4rem; 
  margin-bottom: 15px; 
  display: block;
}

/* Botón de "Volver al inicio" en el error */
.btn-outline {
  background: transparent;
  border: 2px solid #1e3a8a;
  color: #1e3a8a;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 20px;
}

.btn-outline:hover {
  background: #1e3a8a;
  color: #ffffff;
}

.spinner { 
  border: 4px solid #f1f5f9; 
  border-top: 4px solid #1e3a8a; 
  border-radius: 50%; 
  width: 45px; 
  height: 45px; 
  animation: spin 1s linear infinite; 
  margin: 0 auto 20px; 
}

@keyframes spin { 
  0% { transform: rotate(0deg); } 
  100% { transform: rotate(360deg); } 
}
</style>