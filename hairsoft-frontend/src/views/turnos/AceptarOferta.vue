<template>
  <div class="oferta-container">
    <div class="card-oferta animate-in">
      
      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <p>Cargando oferta...</p>
      </div>

      <div v-else-if="errorMsg" class="state-box error">
        <div class="icon">😢</div>
        <h3>Lo sentimos</h3>
        <p>{{ errorMsg }}</p>
        <button @click="irAlHome" class="btn-outline">Volver al inicio</button>
      </div>

      <div v-else class="content-box">
        <div class="header-oferta">
          <div class="badge-descuento">🔥 {{ oferta.descuento }}% OFF</div>
          <h2>¡Hola {{ oferta.cliente }}!</h2>
          <p>Se liberó un turno para vos.</p>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span class="label">📅 Fecha</span>
            <span class="value">{{ oferta.fecha }}</span>
          </div>
          <div class="info-item">
            <span class="label">⏰ Hora</span>
            <span class="value">{{ oferta.hora }}</span>
          </div>
          <div class="info-item">
            <span class="label">💈 Profesional</span>
            <span class="value">{{ oferta.profesional }}</span>
          </div>
          <div class="info-item full-width">
            <span class="label">✂️ Servicio</span>
            <span class="value">{{ oferta.servicio }}</span>
          </div>
        </div>

        <div class="precios-box">
          <div class="precio-viejo">${{ oferta.precio_original }}</div>
          <div class="precio-nuevo">${{ oferta.precio_final }}</div>
          <small class="ahorro">¡Ahorras ${{ oferta.precio_original - oferta.precio_final }}!</small>
        </div>

        <div class="pago-selector">
          <p class="pago-titulo">¿Cómo deseas confirmar?</p>
          
          <div 
            class="opcion-pago" 
            :class="{ active: tipoPago === 'SENA_50' }"
            @click="tipoPago = 'SENA_50'"
          >
            <div class="radio-circle"></div>
            <div class="texto-pago">
              <span class="titulo">Pagar Seña (50%)</span>
              <span class="monto">${{ oferta.monto_sena }} ahora</span>
            </div>
          </div>

          <div 
            class="opcion-pago"
            :class="{ active: tipoPago === 'TOTAL' }"
            @click="tipoPago = 'TOTAL'"
          >
            <div class="radio-circle"></div>
            <div class="texto-pago">
              <span class="titulo">Pagar Total (100%)</span>
              <span class="monto">${{ oferta.precio_final }} ahora</span>
            </div>
          </div>
        </div>

        <button 
          @click="aceptarYPagar" 
          class="btn-aceptar"
          :disabled="procesando"
        >
          <span v-if="!procesando">💳 Confirmar y Pagar</span>
          <span v-else>🔄 Procesando...</span>
        </button>

        <button @click="irAlHome" class="btn-link">No me interesa</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const API_URL = 'http://localhost:8000/usuarios/api'; // O tu IP si pruebas en móvil

const loading = ref(true);
const procesando = ref(false);
const errorMsg = ref('');
const oferta = ref({});
const tipoPago = ref('SENA_50'); // Por defecto seña

const { turno_id, token } = route.params;

onMounted(async () => {
  if (!turno_id || !token) {
    errorMsg.value = "Enlace inválido";
    loading.value = false;
    return;
  }

  try {
    // 1. Obtener Info de la Oferta (GET)
    const res = await fetch(`${API_URL}/turnos/${turno_id}/oferta-info/${token}/`);
    const data = await res.json();

    if (res.ok) {
      oferta.value = data;
    } else {
      errorMsg.value = data.error || "La oferta ya no está disponible.";
    }
  } catch (e) {
    errorMsg.value = "Error de conexión.";
  } finally {
    loading.value = false;
  }
});

const aceptarYPagar = async () => {
  procesando.value = true;
  try {
    // 2. Aceptar Oferta (POST)
    const res = await fetch(`${API_URL}/turnos/${turno_id}/aceptar-oferta/${token}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tipo_pago: tipoPago.value })
    });

    const data = await res.json();

    if (res.ok && data.success) {
      if (data.mp_link) {
        // Redirigir a Mercado Pago
        window.location.href = data.mp_link;
      } else {
        // Fallback si no hay link (ej: error MP)
        alert("Turno confirmado, pero hubo un error generando el pago. Acércate al local.");
        window.location.href = '/turnos'; // O tu URL de frontend
      }
    } else {
      errorMsg.value = data.error || "Error al confirmar.";
    }
  } catch (e) {
    errorMsg.value = "Error de conexión al procesar el pago.";
  } finally {
    procesando.value = false;
  }
};

const irAlHome = () => {
  window.location.href = '/';
};
</script>

<style scoped>
.oferta-container {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  font-family: 'Segoe UI', sans-serif;
}

.card-oferta {
  background: white;
  width: 100%;
  max-width: 400px;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  overflow: hidden;
  position: relative;
}

.header-oferta {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 30px 20px;
  text-align: center;
  position: relative;
}

.badge-descuento {
  background: #ffc107;
  color: #333;
  font-weight: 800;
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  margin-bottom: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

.header-oferta h2 { margin: 0; font-size: 1.5em; }
.header-oferta p { margin: 5px 0 0; opacity: 0.9; }

.content-box { padding: 20px; }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 12px;
}

.info-item.full-width { grid-column: span 2; }

.label { display: block; font-size: 0.8em; color: #6c757d; font-weight: 600; text-transform: uppercase; }
.value { display: block; font-size: 1em; color: #333; font-weight: 600; margin-top: 2px; }

.precios-box {
  text-align: center;
  margin-bottom: 25px;
  padding: 15px;
  background: #f0fff4;
  border: 1px dashed #28a745;
  border-radius: 12px;
}

.precio-viejo { text-decoration: line-through; color: #999; font-size: 1em; }
.precio-nuevo { color: #28a745; font-weight: 800; font-size: 2em; line-height: 1; margin: 5px 0; }
.ahorro { color: #155724; font-weight: 600; font-size: 0.9em; }

.pago-selector { margin-bottom: 25px; }
.pago-titulo { font-weight: 600; margin-bottom: 10px; color: #333; }

.opcion-pago {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.opcion-pago.active {
  border-color: #007bff;
  background: #e7f3ff;
}

.radio-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #ccc;
  position: relative;
}

.opcion-pago.active .radio-circle {
  border-color: #007bff;
  background: #007bff;
}

.texto-pago .titulo { display: block; font-weight: 600; color: #333; }
.texto-pago .monto { display: block; font-size: 0.9em; color: #666; }

.btn-aceptar {
  width: 100%;
  background: #28a745;
  color: white;
  border: none;
  padding: 16px;
  border-radius: 12px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  transition: transform 0.2s;
}

.btn-aceptar:active { transform: scale(0.98); }
.btn-aceptar:disabled { background: #ccc; box-shadow: none; }

.btn-link {
  width: 100%;
  background: none;
  border: none;
  color: #6c757d;
  margin-top: 15px;
  cursor: pointer;
  text-decoration: underline;
}

.state-box {
  padding: 40px;
  text-align: center;
  color: black;
}
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>