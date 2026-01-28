<template>
  <div class="page-container">
    <div class="offer-card animate-in">
      
      <div class="card-header">
        <div class="brand-tag">✂️ Los Últimos Serán Los Primeros</div>
        <h1>¡Turno Disponible!</h1>
        <p>Tu oportunidad exclusiva ha llegado.</p>
      </div>

      <div class="card-body">
        
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <p>Verificando disponibilidad...</p>
        </div>

        <div v-else-if="errorMsg" class="state-box error">
          <div class="icon">⚠️</div>
          <h3>Lo sentimos</h3>
          <p>{{ errorMsg }}</p>
          <button @click="volver" class="btn-outline">Volver</button>
        </div>

        <div v-else-if="successMsg" class="state-box success">
          <div class="icon">🎉</div>
          <h3>¡Felicitaciones!</h3>
          <p class="msg-text">{{ successMsg }}</p>
          <button @click="volver" class="btn-primary full">Ir a Mis Turnos</button>
        </div>

        <div v-else>
          <div class="info-group">
            <div class="row">
              <span class="label">Profesional</span>
              <span class="data">{{ info.profesional }}</span>
            </div>
            <div class="row">
              <span class="label">Fecha y Hora</span>
              <span class="data highlight">{{ info.fecha }} - {{ info.hora }} hs</span>
            </div>
            <div class="row">
              <span class="label">Servicio</span>
              <span class="data">{{ info.servicio }}</span>
            </div>
          </div>

          <div class="pricing-box">
            <div class="price-row">
              <span>Precio Regular</span>
              <span class="old-price">${{ info.precio_original }}</span>
            </div>
            <div class="price-row main">
              <span>Con 15% OFF</span>
              <span class="new-price">${{ info.precio_final }}</span>
            </div>
            <div class="sena-info">
              Seña requerida: ${{ info.monto_sena }}
            </div>
          </div>

          <div class="alert-info">
            <span class="emoji">🔄</span>
            <p>
              Al aceptar, <strong>cancelaremos tu turno anterior</strong> automáticamente y 
              usaremos tu pago previo para cubrir este nuevo turno.
            </p>
          </div>

          <div class="actions">
            <button @click="confirmarOferta" class="btn-primary full" :disabled="procesando">
              <span v-if="!procesando">✅ ACEPTAR Y CANJEAR</span>
              <span v-else>Procesando...</span>
            </button>
            <button @click="volver" class="btn-text">No gracias, mantengo el anterior</button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const info = ref({});
const errorMsg = ref("");

const turnoId = route.params.turno_id;
const token = route.params.token;

onMounted(async () => {
  console.log('🔗 ACCESO DESDE WHATSAPP DETECTADO');
  
  // 🔥 PASO 1: NUCLEAR TOTAL - BORRAR ABSOLUTAMENTE TODO
  localStorage.removeItem('token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('user_rol');
  localStorage.removeItem('user_nombre');
  localStorage.removeItem('fresh_token');
  sessionStorage.clear();
  
  // 🔥 PASO 2: Verificar si tenemos credenciales válidas
  const hasValidToken = localStorage.getItem('token') && localStorage.getItem('user_id');
  
  // 🔥 PASO 3: SIEMPRE ir a login cuando viene de WhatsApp
  if (!hasValidToken || route.query.force_login === 'true') {
    console.log('🔐 FORZANDO LOGIN DESDE WHATSAPP');
    
    // Guardar la oferta que queremos ver
    sessionStorage.setItem('pending_offer', JSON.stringify({
      turno_id: turnoId,
      token: token,
      timestamp: new Date().getTime()
    }));
    
    // 🔴 REDIRIGIR OBLIGATORIAMENTE AL LOGIN
    router.push({ 
      name: 'Login', 
      query: { 
        redirect: `/aceptar-oferta/${turnoId}/${token}?from_whatsapp=true`,
        force_whatsapp: 'true'
      }
    });
    return; // ❌ NO CONTINUAR
  }
  
  // ✅ PASO 4: Si llegamos aquí, YA estamos logueados
  try {
    const userToken = localStorage.getItem('token');
    const userId = localStorage.getItem('user_id');
    
    const res = await axios.get(`http://localhost:8000/api/turnos/${turnoId}/oferta-info/${token}/`, {
      headers: { 'Authorization': `Token ${userToken}` }
    });
    
    info.value = res.data;
    
    // Verificar que el usuario logueado sea el dueño
    if (parseInt(userId) !== parseInt(res.data.cliente_id)) {
      errorMsg.value = "Esta oferta no te pertenece";
      loading.value = false;
      return;
    }
    
  } catch (error) {
    if (error.response?.status === 401) {
      // Token inválido, volver a login
      localStorage.clear();
      router.push({ name: 'Login' });
    } else {
      errorMsg.value = "Oferta expirada o inválida";
    }
  } finally {
    loading.value = false;
  }
});

const confirmarOferta = async () => {
  try {
    const userToken = localStorage.getItem('token');
    
    const res = await axios.post(`http://localhost:8000/api/turnos/${turnoId}/aceptar-oferta/${token}/`, {}, {
      headers: { 'Authorization': `Token ${userToken}` }
    });
    
    if (res.data.success && res.data.mp_init_point) {
      // 🔥 Guardar en sessionStorage que después del pago vamos al dashboard
      sessionStorage.setItem('post_payment_action', 'redirect_to_dashboard');
      sessionStorage.setItem('post_payment_turno_id', turnoId);
      
      // Ir a Mercado Pago
      window.location.href = res.data.mp_init_point;
    } else if (res.data.success) {
      // Si no requiere pago, directo al dashboard
      router.push('/cliente/dashboard');
    }
  } catch (error) {
    Swal.fire('Error', error.response?.data?.error || 'Error al aceptar oferta', 'error');
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

.page-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #121212; /* Fondo oscuro elegante */
  font-family: 'Montserrat', sans-serif;
  padding: 20px;
}

.offer-card {
  background: #ffffff;
  width: 100%;
  max-width: 420px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.card-header {
  background: #000;
  color: #D4AF37; /* Dorado */
  padding: 30px 20px;
  text-align: center;
  border-bottom: 3px solid #D4AF37;
}

.brand-tag {
  background: rgba(212, 175, 55, 0.15);
  color: #D4AF37;
  display: inline-block;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 12px;
  text-transform: uppercase;
  border: 1px solid #D4AF37;
}

.card-header h1 { margin: 0; font-size: 1.6rem; color: #fff; }
.card-header p { margin: 8px 0 0; color: #ccc; font-size: 0.95rem; }

.card-body { padding: 30px 25px; }

/* ESTADOS */
.state-box { text-align: center; padding: 20px 0; }
.icon { font-size: 3.5rem; margin-bottom: 15px; display: block; }
.state-box.error { color: #d63031; }
.state-box.success { color: #00b894; }
.msg-text { font-weight: 600; color: #2d3436; margin-bottom: 20px; }

/* INFO */
.info-group { margin-bottom: 25px; }
.row {
  display: flex; justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  font-size: 0.95rem;
}
.label { color: #636e72; font-weight: 600; }
.data { color: #2d3436; font-weight: 700; text-align: right; }
.highlight { color: #0984e3; }

/* PRECIOS */
.pricing-box {
  background: #fdfbf7; /* Tono crema muy suave */
  border: 1px dashed #D4AF37;
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 25px;
}
.price-row { display: flex; justify-content: space-between; margin-bottom: 5px; color: #2d3436; }
.price-row.main { margin-top: 10px; font-size: 1.1rem; border-top: 1px solid #eee; padding-top: 10px; }
.old-price { text-decoration: line-through; color: #b2bec3; }
.new-price { color: #00b894; font-weight: 800; font-size: 1.4rem; }
.sena-info { text-align: center; margin-top: 10px; font-size: 0.85rem; color: #636e72; background: #fff; padding: 5px; border-radius: 5px; border: 1px solid #eee; }

/* ALERTA */
.alert-info {
  background: #e3f2fd;
  border-left: 4px solid #0984e3;
  padding: 12px;
  border-radius: 6px;
  display: flex;
  gap: 12px;
  font-size: 0.85rem;
  color: #0c5460;
  margin-bottom: 25px;
  line-height: 1.4;
  align-items: flex-start;
}

/* BOTONES */
.actions { display: flex; flex-direction: column; gap: 12px; }

.btn-primary {
  background: #D4AF37;
  color: #000;
  border: none;
  padding: 16px;
  border-radius: 50px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
}
.btn-primary:hover { background: #c5a028; transform: translateY(-2px); }
.btn-primary:disabled { background: #ccc; cursor: not-allowed; box-shadow: none; }

.btn-outline {
  background: transparent; border: 2px solid #D4AF37; color: #D4AF37;
  padding: 12px; border-radius: 50px; font-weight: 700; cursor: pointer;
}

.btn-text {
  background: none; border: none; color: #636e72;
  cursor: pointer; font-size: 0.9rem; text-decoration: underline;
}

.spinner {
  border: 4px solid #eee; border-top: 4px solid #D4AF37;
  border-radius: 50%; width: 40px; height: 40px;
  animation: spin 1s linear infinite; margin: 0 auto 15px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.animate-in { animation: fadeInUp 0.5s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>