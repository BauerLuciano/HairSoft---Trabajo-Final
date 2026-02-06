<template>
  <div class="page-container">
    <div class="offer-card animate-in">
      
      <div class="card-header">
        <div class="brand-tag">✨ OPORTUNIDAD EXCLUSIVA</div>
        <h1>¡Turno Disponible!</h1>
        <p class="subtitle">Se liberó un espacio y tenés el 15% de descuento!</p>
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
          <div class="emoji-icon">🥳</div>
          <h3>¡Turno Canjeado!</h3>
          <p class="msg-text">{{ successMsg }}</p>
          <div class="ticket-cut"></div>
          <p class="sub-msg">Te esperamos el {{ formatFecha(info.fecha) }} a las {{ formatHora(info.hora) }}hs.</p>
          <button @click="volver" class="btn-primary full">Ver en Mis Turnos</button>
        </div>

        <div v-else>
          
          <div class="turno-preview">
            <div class="tp-row">
              <span class="tp-label">Profesional:</span>
              <span class="tp-val">{{ info.profesional }}</span>
            </div>
            <div class="tp-row">
              <span class="tp-label">Fecha:</span>
              <span class="tp-val highlight">{{ formatFecha(info.fecha) }}</span>
            </div>
            <div class="tp-row">
              <span class="tp-label">Hora:</span>
              <span class="tp-val highlight">{{ formatHora(info.hora) }}hs</span>
            </div>
            <div class="tp-row">
              <span class="tp-label">Servicio:</span>
              <span class="tp-val">{{ info.servicio }}</span>
            </div>
          </div>

          <div class="offer-box">
            <div class="offer-badge">-15% OFF</div>
            <div class="price-compare">
              <div class="p-old">
                <span>Precio Regular</span>
                <del>${{ formatPrecio(info.precio_original) }}</del>
              </div>
              <div class="p-new">
                <span>Precio Oferta</span>
                <strong>${{ formatPrecio(info.precio_final) }}</strong>
              </div>
            </div>
          </div>

          <div class="wallet-section">
            <div class="wallet-header">
              <span>💳 Tu Pago Anterior</span>
              <span class="wallet-amount">${{ formatPrecio(info.pagado_anterior) }}</span>
            </div>

            <div v-if="info.saldo_a_favor > 0" class="result-box winner">
              <div class="result-title">¡TE SOBRA DINERO! 🎉</div>
              <div class="result-amount">
                + ${{ formatPrecio(info.saldo_a_favor) }}
              </div>
              <p class="result-desc">
                Este saldo queda a tu favor para usar en productos o retirar en el local.
                <strong>¡El cambio de turno te sale GRATIS!</strong>
              </p>
            </div>

            <div v-else-if="info.monto_final_a_pagar > 0" class="result-box owing">
              <div class="result-title">Solo abonas la diferencia</div>
              <div class="result-amount">
                ${{ formatPrecio(info.monto_final_a_pagar) }}
              </div>
              <p class="result-desc">Se descuenta lo que ya pagaste. Pagarás en el local.</p>
            </div>
            
            <div v-else class="result-box zero">
              <div class="result-title">¡Cubierto al 100%!</div>
              <div class="result-amount">$0.00</div>
              <p class="result-desc">Tu pago anterior cubre todo el costo.</p>
            </div>
          </div>

          <div class="actions">
            <button @click="confirmarOferta" class="btn-primary full shine-effect" :disabled="procesando">
              <span v-if="!procesando">
                <i class="bi bi-stars"></i> 
                {{ info.saldo_a_favor > 0 ? 'ACEPTAR Y CANJEAR GRATIS' : 'CONFIRMAR CANJE' }}
              </span>
              <span v-else>Procesando canje...</span>
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

// Helpers de formato
const formatPrecio = (v) => {
  if (v === undefined || v === null) return '0.00';
  const num = parseFloat(v);
  return isNaN(num) ? '0.00' : num.toFixed(2);
};

// 🔥 ARREGLO COMPLETO DE FECHA
const formatFecha = (f) => { 
  if(!f) return '-'; 
  
  // Si es un string ISO
  if (typeof f === 'string' && f.includes('-')) {
    try {
      const [year, month, day] = f.split('-');
      return `${day}/${month}/${year}`;
    } catch (e) {
      return f;
    }
  }
  
  // Si es un objeto Date
  if (f instanceof Date || (typeof f === 'string' && Date.parse(f))) {
    try {
      const dateObj = new Date(f);
      return dateObj.toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit', 
        year: 'numeric'
      });
    } catch (e) {}
  }
  
  return f;
};

const formatHora = (h) => { 
  if(!h) return '-';
  if (typeof h === 'string') {
    // Extraer solo HH:MM
    const match = h.match(/(\d{1,2}):(\d{2})/);
    if (match) {
      return `${match[1].padStart(2, '0')}:${match[2]}`;
    }
  }
  return h;
};

onMounted(async () => {
  const userToken = localStorage.getItem('token'); 
  
  if (!userToken) {
    router.push({ name: 'login', query: { redirect: route.fullPath } });
    return;
  }

  try {
    const { data } = await axios.get(`/api/turnos/${turnoId}/oferta-info/${token}/`);
    info.value = data;
    console.log("Datos de oferta recibidos:", info.value);
  } catch (error) {
    console.error("Error cargando oferta:", error);
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
      // Mostrar saldo a favor si existe
      const saldoMsg = data.saldo_a_favor > 0 ? 
        `<br><strong>💚 Saldo a favor: $${formatPrecio(data.saldo_a_favor)}</strong>` : '';
      
      successMsg.value = data.message || "¡Listo! Tu turno ha sido canjeado.";
      
      await Swal.fire({
        title: '¡Felicitaciones!',
        html: `Tu turno fue canjeado con éxito.${saldoMsg}`,
        icon: 'success',
        confirmButtonColor: '#D4AF37',
        confirmButtonText: 'Genial'
      });
      
      router.push('/cliente/dashboard');
    } else {
      throw new Error(data.error || 'Error desconocido');
    }
  } catch (error) {
    console.error("Error aceptando oferta:", error);
    Swal.fire({
      title: 'Error',
      text: error.response?.data?.error || 'No se pudo procesar el canje.',
      icon: 'error'
    });
  } finally {
    procesando.value = false;
  }
};

const volver = () => router.push('/cliente/dashboard');
</script>

<style scoped>
/* ESTILOS PREMIUM PARA LA EXPERIENCIA DE "GANAR" */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');

.page-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  font-family: 'Montserrat', sans-serif;
  padding: 20px;
}

.offer-card {
  background: #ffffff;
  width: 100%;
  max-width: 450px;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  border: 1px solid rgba(0,0,0,0.05);
}

.card-header {
  background: #111827;
  color: #D4AF37;
  padding: 35px 25px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.card-header::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(45deg, transparent 45%, rgba(212, 175, 55, 0.1) 50%, transparent 55%);
    background-size: 200% 200%;
    animation: shine 3s infinite;
}

@keyframes shine { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

.brand-tag {
  background: #D4AF37;
  color: #000;
  display: inline-block;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 800;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.card-header h1 { 
  margin: 0; 
  font-size: 1.8rem; 
  color: #fff; 
  font-weight: 800; 
  line-height: 1.2;
}

.subtitle { 
  margin: 8px 0 0; 
  color: #9ca3af; 
  font-size: 0.9rem; 
  line-height: 1.4;
}

.card-body { 
  padding: 30px 25px; 
}

/* TURNO PREVIEW */
.turno-preview { 
  margin-bottom: 25px; 
  border-bottom: 1px solid #f3f4f6; 
  padding-bottom: 20px; 
}

.tp-row { 
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 12px; 
  font-size: 0.95rem; 
  line-height: 1.4;
}

.tp-label { 
  color: #6b7280; 
  font-weight: 600;
}

.tp-val { 
  font-weight: 600; 
  color: #1f2937; 
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

.highlight { 
  color: #D4AF37; 
  font-weight: 700;
}

/* OFFER BOX */
.offer-box { 
    background: #fdfbf7; 
    border: 2px dashed #D4AF37; 
    border-radius: 16px; 
    padding: 20px; 
    position: relative;
    margin-bottom: 25px;
}

.offer-badge {
    position: absolute;
    top: -12px; 
    right: 15px;
    background: #ef4444; 
    color: white;
    font-weight: 800; 
    font-size: 0.8rem;
    padding: 4px 10px; 
    border-radius: 20px;
    transform: rotate(2deg);
}

.price-compare { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}

.p-old { 
  display: flex; 
  flex-direction: column; 
  font-size: 0.85rem; 
  color: #9ca3af; 
}

.p-old del {
  font-size: 1rem;
  color: #9ca3af;
}

.p-new { 
  display: flex; 
  flex-direction: column; 
  text-align: right; 
}

.p-new span { 
  font-size: 0.85rem; 
  color: #059669; 
  font-weight: 600; 
}

.p-new strong { 
  font-size: 1.8rem; 
  color: #059669; 
  font-weight: 900; 
}

/* WALLET SECTION */
.wallet-section { 
  background: #f9fafb; 
  border-radius: 16px; 
  padding: 20px; 
  margin-bottom: 25px; 
  border: 1px solid #e5e7eb;
}

.wallet-header { 
  display: flex; 
  justify-content: space-between; 
  font-size: 0.95rem; 
  color: #4b5563; 
  margin-bottom: 20px; 
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e7eb;
}

.wallet-amount {
  color: #1f2937;
  font-weight: 700;
}

.result-box { 
  text-align: center; 
  padding: 20px; 
  border-radius: 12px; 
  margin-top: 15px;
}

.result-box.winner { 
  background: #ecfdf5; 
  border: 2px solid #10b981; 
}

.result-box.owing { 
  background: #fffbeb; 
  border: 2px solid #f59e0b; 
}

.result-box.zero { 
  background: #eff6ff; 
  border: 2px solid #3b82f6; 
}

.result-title { 
  font-size: 0.9rem; 
  font-weight: 800; 
  text-transform: uppercase; 
  margin-bottom: 8px; 
  letter-spacing: 0.5px;
}

.winner .result-title { color: #059669; }
.owing .result-title { color: #d97706; }
.zero .result-title { color: #1d4ed8; }

.result-amount { 
  font-size: 2.2rem; 
  font-weight: 900; 
  margin-bottom: 12px; 
  line-height: 1;
}

.winner .result-amount { color: #059669; }
.owing .result-amount { color: #d97706; }
.zero .result-amount { color: #1d4ed8; }

.result-desc { 
  font-size: 0.85rem; 
  line-height: 1.5; 
  color: #6b7280; 
  margin: 0; 
}

/* BOTONES */
.actions { 
  display: flex; 
  flex-direction: column; 
  gap: 15px; 
  margin-bottom: 20px;
}

.btn-primary {
  background: #111827; 
  color: #D4AF37; 
  border: none;
  padding: 18px; 
  border-radius: 50px; 
  font-weight: 700; 
  font-size: 1rem;
  cursor: pointer; 
  transition: all 0.3s;
  display: flex; 
  justify-content: center; 
  align-items: center; 
  gap: 10px;
}

.btn-primary:hover { 
  transform: translateY(-3px); 
  box-shadow: 0 10px 20px rgba(0,0,0,0.2); 
  background: #1f2937;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-text { 
  background: none; 
  border: none; 
  color: #9ca3af; 
  cursor: pointer; 
  text-decoration: underline; 
  font-size: 0.9rem; 
  padding: 10px;
}

.btn-text:hover {
  color: #6b7280;
}

.disclaimer { 
  font-size: 0.75rem; 
  text-align: center; 
  color: #9ca3af; 
  margin-top: 15px;
  line-height: 1.4;
  padding: 0 10px;
}

/* LOADING & MESSAGES */
.state-box { 
  text-align: center; 
  padding: 40px 20px; 
}

.emoji-icon { 
  font-size: 3rem; 
  margin-bottom: 15px; 
}

.spinner { 
  border: 4px solid #f3f4f6; 
  border-top: 4px solid #D4AF37; 
  border-radius: 50%; 
  width: 40px; 
  height: 40px; 
  animation: spin 1s linear infinite; 
  margin: 0 auto 15px; 
}

@keyframes spin { 
  0% { transform: rotate(0deg); } 
  100% { transform: rotate(360deg); } 
}

.animate-in { 
  animation: fadeInUp 0.6s ease-out; 
}

@keyframes fadeInUp { 
  from { opacity: 0; transform: translateY(30px); } 
  to { opacity: 1; transform: translateY(0); } 
}

.shine-effect {
  position: relative;
  overflow: hidden;
}

.shine-effect::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transform: rotate(30deg);
  animation: shine 2s infinite;
}
</style>