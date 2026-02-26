<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Notas de Crédito</h1>
          <p>Registro de ventas anuladas y devoluciones de stock</p>
        </div>
        
        <button @click="$router.push('/ventas')" class="btn-volver">
          <ArrowLeft :size="18" />
          Volver a Ventas
        </button>
      </div>

      <div v-if="cargando" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Cargando notas de crédito...</p>
      </div>

      <div v-else class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th style="width: 80px;">Nro Nota</th>
              <th style="width: 80px;">Nro Venta</th>
              <th style="width: 150px;">Fecha Emisión</th>
              <th>Usuario / Cajero</th>
              <th>Productos Devueltos</th>
              <th>Motivo de Anulación</th>
              <th style="text-align: right;">Monto Devuelto</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="nota in notasPaginadas" :key="nota.id">
              <td class="id-cell">#NC-{{ nota.id }}</td>
              <td class="id-cell">#{{ nota.venta_id }}</td>
              <td class="fecha-cell">
                <span class="fecha-dia">{{ formatFechaDia(nota.fecha) }}</span>
                <span class="fecha-hora">{{ formatFechaHora(nota.fecha) }}</span>
              </td>
              <td><strong>{{ nota.usuario_nombre }} {{ nota.usuario_apellido }}</strong></td>
              <td class="productos-cell">{{ nota.detalles_venta }}</td>
              <td class="motivo-cell">"{{ nota.motivo }}"</td>
              <td class="total-cell" style="text-align: right; color: #ef4444;">
                -${{ formatPrecio(nota.monto_devuelto) }}
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="notasCredito.length === 0 && !cargando" class="no-results">
          <FileX class="no-results-icon" :size="48" />
          <p>No se han registrado anulaciones ni notas de crédito aún.</p>
        </div>
      </div>

      <div v-if="!cargando && notasCredito.length > 0" class="list-footer">
        <div class="footer-left">
          <p class="count-text">
            Mostrando <strong>{{ notasPaginadas.length }}</strong> de <strong>{{ notasCredito.length }}</strong> notas de crédito
          </p>
        </div>

        <div v-if="totalPaginas > 1" class="pagination">
          <button @click="paginaAnterior" :disabled="pagina === 1" class="page-btn">
            <ChevronLeft :size="18" />
          </button>
          <span class="page-info">Página {{ pagina }} de {{ totalPaginas }}</span>
          <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="page-btn">
            <ChevronRight :size="18" />
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/utils/axiosConfig';
import { ArrowLeft, FileX, ChevronLeft, ChevronRight } from 'lucide-vue-next';

const router = useRouter();
const notasCredito = ref([]);
const cargando = ref(true);

// --- ESTADOS Y LÓGICA DE PAGINACIÓN ---
const pagina = ref(1);
const itemsPorPagina = 8;

const totalPaginas = computed(() => {
  return Math.max(1, Math.ceil(notasCredito.value.length / itemsPorPagina));
});

const notasPaginadas = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina;
  const fin = inicio + itemsPorPagina;
  return notasCredito.value.slice(inicio, fin);
});

const paginaAnterior = () => {
  if (pagina.value > 1) {
    pagina.value--;
  }
};

const paginaSiguiente = () => {
  if (pagina.value < totalPaginas.value) {
    pagina.value++;
  }
};
// --------------------------------------

const cargarNotas = async () => {
  try {
    const res = await axios.get('/api/notas-credito/');
    notasCredito.value = res.data;
    // Reiniciamos a página 1 cada vez que cargamos datos nuevos
    pagina.value = 1;
  } catch (error) {
    console.error("Error al cargar notas de crédito:", error);
  } finally {
    cargando.value = false;
  }
};

onMounted(() => {
  cargarNotas();
});

const formatFechaDia = (f) => f ? new Date(f).toLocaleDateString('es-AR', {day: '2-digit', month: '2-digit', year: 'numeric'}) : '-';
const formatFechaHora = (f) => f ? new Date(f).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : '';
const formatPrecio = (p) => p ? parseFloat(p).toLocaleString('es-AR', { minimumFractionDigits: 2 }) : '0.00';
</script>

<style scoped>
/* Aprovechamos tus estilos Premium (Celestes en lugar de dorado) */
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; border: 1px solid var(--border-color); margin: 0 auto;}
/* Línea superior celeste/azul (igual al de ventas) */
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1); border-radius: 24px 24px 0 0; }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
/* Título con gradiente celeste */
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; letter-spacing: 0.5px; }

.btn-volver { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 20px; border-radius: 12px; font-weight: 700; cursor: pointer; transition: 0.3s; display: flex; align-items: center; gap: 8px; }
.btn-volver:hover { background: var(--hover-bg); transform: translateY(-2px); }

/* TABLA */
.table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow-md); border: 1px solid var(--border-color); }
/* Header de la tabla con el color principal del sistema */
.users-table th { background: var(--accent-color, #1e293b); color: white; padding: 18px 14px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px; white-space: nowrap; }
.users-table tr { border-bottom: 1px solid var(--border-color); }
.users-table td { padding: 16px 14px; vertical-align: middle; color: var(--text-secondary); font-weight: 500; font-size: 0.9rem; }
.users-table tr:hover { background: var(--hover-bg); transition: 0.2s; }

.fecha-cell { display: flex; flex-direction: column; }
.fecha-dia { font-weight: 700; color: var(--text-primary); }
.fecha-hora { font-size: 0.75rem; color: var(--text-tertiary); }

.id-cell { font-family: 'Courier New', Courier, monospace; color: #94a3b8; font-weight: 700; background: rgba(148, 163, 184, 0.1); padding: 4px 8px; border-radius: 6px; }
.total-cell { font-size: 1.1rem; font-weight: 900; }
.motivo-cell { font-style: italic; color: #cbd5e1; max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.productos-cell { color: #0ea5e9; font-weight: 600; font-size: 0.85rem;}

.loading-state { text-align: center; padding: 80px; color: var(--text-tertiary); font-weight: 600; }
/* Spinner celeste */
.loading-spinner { width: 40px; height: 40px; border: 3px solid var(--border-color); border-top-color: #0ea5e9; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px; }
.no-results { text-align: center; padding: 60px; color: var(--text-tertiary); }
.no-results-icon { margin-bottom: 15px; opacity: 0.5; }

/* ESTILOS DE PAGINACIÓN Y FOOTER (Iguales a los de Ventas) */
.list-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 15px; background: var(--hover-bg); border-radius: 12px; flex-wrap: wrap; gap: 15px; }
.footer-left { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.count-text { color: var(--text-secondary); font-size: 0.9rem; margin: 0; }

.pagination { display: flex; gap: 10px; align-items: center; }
.page-btn { background: var(--bg-tertiary); border: 1px solid var(--border-color); width: 36px; height: 36px; border-radius: 8px; cursor: pointer; color: var(--text-primary); display: flex; justify-content: center; align-items: center; transition: 0.2s; }
.page-btn:hover:not(:disabled) { background: var(--accent-color); color: white; border-color: var(--accent-color); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .list-footer { flex-direction: column; align-items: flex-start; }
  .footer-left { flex-direction: column; align-items: flex-start; gap: 10px; }
  .pagination { width: 100%; justify-content: space-between; }
}
</style>