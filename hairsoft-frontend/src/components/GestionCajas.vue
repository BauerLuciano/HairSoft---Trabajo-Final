<template>
  <div class="sub-module-container">
    <div class="section-header">
      <h3><i class="ri-bank-card-line icon-header"></i> Cajas</h3>
      <button @click="abrirModalCrear" class="register-button sm-btn">
        <i class="ri-add-line"></i> Nueva Caja
      </button>
    </div>

    <div v-if="cargando" class="loading-state">
      <i class="ri-loader-4-line animate-spin"></i> Cargando cajas...
    </div>

    <div v-else class="item-grid">
      <div v-if="cajas.length === 0" class="empty-state">
        <p>No hay cajas configuradas. Deberías agregar al menos una.</p>
      </div>
      
      <div v-for="caja in cajas" :key="caja.id" class="item-card" :class="{'inactiva': !caja.activa}">
        <div class="card-header">
          <div class="card-title">
            <i class="ri-mac-line card-icon"></i>
            <h4>{{ caja.nombre }}</h4>
          </div>
          <span :class="['badge-estado', caja.activa ? 'estado-success' : 'estado-danger']">
            {{ caja.activa ? 'Operativa' : 'Inactiva' }}
          </span>
        </div>
        
        <div v-if="!caja.activa && caja.motivo_inactividad" class="motivo-box">
          <i class="ri-error-warning-line"></i>
          <small>{{ caja.motivo_inactividad }}</small>
        </div>

        <div class="card-actions">
          <button @click="abrirModalEditar(caja)" class="action-btn edit" title="Editar Nombre">
            <i class="ri-pencil-line"></i>
          </button>
          <button @click="toggleEstado(caja)" :class="['action-btn', caja.activa ? 'delete' : 'success']" :title="caja.activa ? 'Desactivar Caja' : 'Reactivar Caja'">
            <i :class="caja.activa ? 'ri-shut-down-line' : 'ri-restart-line'"></i>
          </button>
        </div>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content fade-in">
        <div class="modal-header">
          <h2>{{ modoEdicion ? 'Editar Caja' : 'Nueva Caja' }}</h2>
          <button class="modal-close" @click="cerrarModal"><i class="ri-close-line"></i></button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="guardarCaja" class="vertical-stack">
            <div class="filter-group">
              <label>Nombre del Punto de Cobro</label>
              <input type="text" v-model="formCaja.nombre" required class="filter-input" placeholder="Ej: Mostrador Principal, Caja 2...">
            </div>
            
            <div class="filter-group" v-if="!formCaja.activa">
              <label>Motivo de Inactividad (Opcional)</label>
              <input type="text" v-model="formCaja.motivo_inactividad" class="filter-input" placeholder="Ej: PC en reparación...">
            </div>

            <div class="modal-footer-btns">
              <button type="button" @click="cerrarModal" class="btn-outline">Cancelar</button>
              <button type="submit" class="register-button" :disabled="guardando">
                <i class="ri-save-line"></i> {{ guardando ? 'Guardando...' : 'Guardar Caja' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import cajaService from '@/services/cajaService'; 
import Swal from 'sweetalert2';

const cajas = ref([]);
const cargando = ref(true);
const mostrarModal = ref(false);
const modoEdicion = ref(false);
const guardando = ref(false);

const formCaja = ref({
  id: null,
  nombre: '',
  activa: true,
  motivo_inactividad: ''
});

const cargarCajas = async () => {
  cargando.value = true;
  try {
    const res = await cajaService.getCajas();
    cajas.value = res.data.sort((a, b) => b.activa - a.activa);
  } catch (error) {
    console.error("Error al cargar cajas", error);
  } finally {
    cargando.value = false;
  }
};

const abrirModalCrear = () => {
  modoEdicion.value = false;
  formCaja.value = { id: null, nombre: '', activa: true, motivo_inactividad: '' };
  mostrarModal.value = true;
};

const abrirModalEditar = (caja) => {
  modoEdicion.value = true;
  formCaja.value = { ...caja };
  mostrarModal.value = true;
};

const cerrarModal = () => {
  mostrarModal.value = false;
};

const guardarCaja = async () => {
  guardando.value = true;
  try {
    const token = localStorage.getItem('token');
    const headers = { 
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json' 
    };
    
    let response;
    
    if (modoEdicion.value) {
      response = await fetch(`http://localhost:8000/api/cajas/${formCaja.value.id}/`, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(formCaja.value)
      });
    } else {
      response = await fetch(`http://localhost:8000/api/cajas/`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(formCaja.value)
      });
    }
    
    if (!response.ok) {
        const errorData = await response.json();
        let mensajeError = 'Verifique los datos ingresados.';
        if (errorData.nombre) {
            mensajeError = errorData.nombre[0];
        }
        
        Swal.fire({ 
            icon: 'warning', 
            title: 'Error de validación', 
            text: mensajeError, 
            background: '#0f172a', 
            color: '#f8fafc' 
        });
        return; 
    }
    
    Swal.fire({ icon: 'success', title: 'Guardado', timer: 1500, showConfirmButton: false, background: '#0f172a', color: '#f8fafc' });
    cerrarModal();
    cargarCajas();
    
  } catch (error) {
    Swal.fire({ icon: 'error', title: 'Error de conexión', text: 'No se pudo contactar al servidor', background: '#0f172a', color: '#f8fafc' });
  } finally {
    guardando.value = false;
  }
};

const toggleEstado = async (caja) => {
  const nuevoEstado = !caja.activa;
  let motivo = '';

  if (!nuevoEstado) {
    const { value: texto } = await Swal.fire({
      title: 'Desactivar Caja',
      input: 'text',
      inputLabel: 'Motivo de inactividad (opcional)',
      inputPlaceholder: 'Ej: PC Rota',
      showCancelButton: true,
      background: '#0f172a',
      color: '#f8fafc'
    });
    if (texto === undefined) return; 
    motivo = texto;
  } else {
    const confirm = await Swal.fire({
      title: '¿Activar caja?',
      icon: 'question',
      showCancelButton: true,
      background: '#0f172a',
      color: '#f8fafc'
    });
    if (!confirm.isConfirmed) return;
  }

  try {
    const token = localStorage.getItem('token');
    await fetch(`http://localhost:8000/api/cajas/${caja.id}/`, {
        method: 'PATCH',
        headers: { 
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ activa: nuevoEstado, motivo_inactividad: motivo })
    });
    cargarCajas();
  } catch (error) {
    console.error(error);
  }
};

onMounted(cargarCajas);
</script>

<style scoped>
/* ESTILOS COMPARTIDOS ENTRE CAJAS Y SILLAS */
.sub-module-container { width: 100%; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid var(--border-color); }
.section-header h3 { margin: 0; color: var(--text-primary); font-size: 1.3rem; font-weight: 800; display: flex; align-items: center; gap: 10px; }
.icon-header { color: #0ea5e9; font-size: 1.5rem; }

.item-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
.item-card { background: var(--bg-primary); border: 2px solid var(--border-color); border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 15px; transition: all 0.3s ease; position: relative; overflow: hidden; min-height: 160px; }
.item-card:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); border-color: var(--accent-color); }
.item-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--accent-color); opacity: 0; transition: 0.3s; }
.item-card:hover::before { opacity: 1; }
.item-card.inactiva { opacity: 0.7; filter: grayscale(30%); border-color: var(--border-color) !important; }
.item-card.inactiva:hover::before { background: var(--error-color); }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.card-title { display: flex; align-items: center; gap: 12px; }
.card-icon { font-size: 1.8rem; color: var(--text-secondary); background: var(--bg-secondary); padding: 8px; border-radius: 10px; border: 1px solid var(--border-color); }
.card-title h4 { margin: 0; color: var(--text-primary); font-size: 1.1rem; font-weight: 700; word-break: break-word;}

.badge-estado { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; white-space: nowrap; }
.estado-success { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.estado-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }

.motivo-box { background: rgba(239, 68, 68, 0.1); padding: 10px 12px; border-radius: 8px; color: #ef4444; display: flex; gap: 8px; align-items: flex-start; border: 1px dashed rgba(239, 68, 68, 0.3); font-size: 0.85rem; }
.motivo-box i { font-size: 1rem; margin-top: 2px; }

.card-actions { display: flex; gap: 10px; justify-content: flex-end; border-top: 1px solid var(--border-color); padding-top: 15px; margin-top: auto; }
.action-btn { padding: 8px; border: none; border-radius: 10px; font-size: 1.1rem; cursor: pointer; transition: 0.2s; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; }
.action-btn.edit { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); }
.action-btn.edit:hover { background: var(--hover-bg); transform: translateY(-2px); border-color: var(--accent-color); color: var(--accent-color); }
.action-btn.delete { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.action-btn.delete:hover { background: #ef4444; color: white; transform: translateY(-2px); }
.action-btn.success { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.action-btn.success:hover { background: #10b981; color: white; transform: translateY(-2px); }

/* BOTONES GLOBALES */
.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); font-size: 0.9rem;}
.register-button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); }
.sm-btn { padding: 8px 16px; font-size: 0.85rem; box-shadow: none; }
.btn-outline { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 700; text-transform: uppercase; transition: 0.3s; display: flex; align-items: center; justify-content: center; font-size: 0.9rem;}
.btn-outline:hover { background: var(--hover-bg); border-color: var(--text-secondary); }

/* UTILIDADES Y MODAL */
.loading-state, .empty-state { width: 100%; text-align: center; padding: 40px 0; color: var(--text-secondary); font-style: italic; }
.animate-spin { animation: spin 1s linear infinite; display: inline-block; font-size: 1.5rem; margin-right: 10px; vertical-align: middle;}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeInModal 0.2s ease; }
@keyframes fadeInModal { from { opacity: 0; } to { opacity: 1; } }
.modal-content { max-width: 450px; width: 90%; background: var(--bg-secondary); border-radius: 16px; border: 1px solid var(--border-color); overflow: hidden; box-shadow: var(--shadow-lg);}
.fade-in { animation: slideUp 0.3s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.modal-header { padding: 20px 25px; background: var(--bg-primary); border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
.modal-header h2 { margin: 0; color: var(--text-primary); font-size: 1.2rem; font-weight: 800;}
.modal-close { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-secondary); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; cursor: pointer; transition: 0.2s; }
.modal-close:hover { background: var(--error-color); color: white; border-color: var(--error-color); transform: rotate(90deg); }
.modal-body { padding: 25px; }

.vertical-stack { display: flex; flex-direction: column; gap: 20px; }
.filter-group { display: flex; flex-direction: column; text-align: left;}
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }
.filter-input { padding: 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 1rem; transition: all 0.3s; width: 100%; box-sizing: border-box; outline: none;}
.filter-input:focus { border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); }
.modal-footer-btns { display: flex; gap: 15px; margin-top: 10px; }
.modal-footer-btns > * { flex: 1; }
</style>