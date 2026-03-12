<template>
  <div class="sub-module-container">
    <div class="section-header">
      <h3><i class="ri-instance-line icon-header"></i> Puestos de Trabajo (Sillas)</h3>
      <button class="register-button sm-btn" @click="abrirModalCrear" :disabled="cargando">
        <i class="ri-add-line"></i> Nueva Silla
      </button>
    </div>

    <div v-if="cargando" class="loading-state">
      <i class="ri-loader-4-line animate-spin"></i> Sincronizando...
    </div>

    <div v-else class="item-grid">
      <div v-if="sillas.length === 0" class="empty-state">
        <p>No hay sillas registradas. Agregá la primera para comenzar.</p>
      </div>

      <div 
        v-for="silla in sillas" 
        :key="silla.id" 
        class="item-card"
        :class="{'inactiva': !silla.activa}"
      >
        <div class="orden-badge" title="Prioridad de asignación">
          #{{ silla.orden }}
        </div>

        <div class="card-header">
          <div class="card-title">
            <i class="ri-wheelchair-line card-icon"></i>
            <h4>{{ silla.nombre }}</h4>
          </div>
          <span :class="['badge-estado', silla.activa ? 'estado-success' : 'estado-danger']">
            {{ silla.activa ? 'Disponible' : 'Fuera de Servicio' }}
          </span>
        </div>

        <div v-if="!silla.activa && silla.motivo_inactividad" class="motivo-box">
          <i class="ri-tools-fill"></i>
          <small>{{ silla.motivo_inactividad }}</small>
        </div>

        <div class="card-actions">
          <button @click="abrirModalEditar(silla)" class="action-btn edit" title="Editar Nombre y Prioridad">
            <i class="ri-pencil-line"></i>
          </button>

          <button 
            @click="toggleEstado(silla)" 
            :class="['action-btn', silla.activa ? 'delete' : 'success']" 
            :title="silla.activa ? 'Deshabilitar Silla' : 'Habilitar Silla'"
          >
            <i :class="silla.activa ? 'ri-shut-down-line' : 'ri-restart-line'"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/utils/axiosConfig';
import Swal from 'sweetalert2';

const sillas = ref([]);
const cargando = ref(false);

onMounted(() => {
  cargarSillas();
});

const cargarSillas = async () => {
  cargando.value = true;
  try {
    const res = await axios.get('/api/sillas/');
    // Ordenamos por activa primero y luego por orden de prioridad
    sillas.value = res.data.sort((a, b) => {
        if (a.activa === b.activa) return a.orden - b.orden;
        return b.activa - a.activa;
    });
  } catch (error) {
    console.error("Error cargando sillas", error);
  } finally {
    cargando.value = false;
  }
};

const abrirModalCrear = async () => {
  const { value: formValues } = await Swal.fire({
    title: 'Nueva Silla',
    background: '#0f172a',
    color: '#f8fafc',
    html: `
      <div style="text-align:left; font-family: 'Inter', sans-serif;">
        <label style="font-weight: 700; margin-bottom: 10px; display: block; color: #94a3b8; text-transform: uppercase; font-size: 0.75rem;">Nombre del Puesto</label>
        <input id="swal-nombre" class="swal2-input custom-swal-input" placeholder="Ej: Silla Principal" style="margin: 0 0 20px 0; width: 100%; box-sizing: border-box;">
        
        <label style="font-weight: 700; margin-bottom: 10px; display: block; color: #94a3b8; text-transform: uppercase; font-size: 0.75rem;">Orden de Prioridad</label>
        <input 
          id="swal-orden" 
          type="number" 
          min="1" 
          step="1" 
          onkeypress="return event.charCode >= 48 && event.charCode <= 57"
          class="swal2-input custom-swal-input" 
          placeholder="1" 
          value="${sillas.value.length + 1}" 
          style="margin: 0; width: 100%; box-sizing: border-box;"
        >
      </div>
    `,
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Crear Silla',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#0ea5e9',
    cancelButtonColor: '#334155',
    preConfirm: () => {
      const nombre = document.getElementById('swal-nombre').value.trim();
      const orden = parseInt(document.getElementById('swal-orden').value);

      if (!nombre) {
        Swal.showValidationMessage('El nombre de la silla es obligatorio.');
        return false;
      }

      if (isNaN(orden) || orden < 1) {
        Swal.showValidationMessage('El orden debe ser un número válido mayor a 0.');
        return false;
      }

      const ordenOcupado = sillas.value.some(s => s.orden === orden);
      if (ordenOcupado) {
        Swal.showValidationMessage(`El orden #${orden} ya está ocupado por otra silla.`);
        return false;
      }

      return { nombre, orden };
    }
  });

  if (formValues && formValues.nombre) {
    try {
      await axios.post('/api/sillas/', {
        nombre: formValues.nombre,
        orden: formValues.orden,
        activa: true
      });
      cargarSillas();
      Swal.fire({ icon: 'success', title: 'Silla creada', timer: 1500, showConfirmButton: false, background: '#0f172a', color: '#f8fafc' });
    } catch (e) {
      let mensajeError = 'No se pudo crear la silla.';
      if (e.response && e.response.data && e.response.data.nombre) mensajeError = e.response.data.nombre[0];
      Swal.fire({ title: 'Error', text: mensajeError, icon: 'warning', background: '#0f172a', color: '#f8fafc' });
    }
  }
};

const abrirModalEditar = async (silla) => {
  const { value: formValues } = await Swal.fire({
    title: 'Editar Silla',
    background: '#0f172a',
    color: '#f8fafc',
    html: `
      <div style="text-align:left; font-family: 'Inter', sans-serif;">
        <label style="font-weight: 700; margin-bottom: 10px; display: block; color: #94a3b8; text-transform: uppercase; font-size: 0.75rem;">Nombre del Puesto</label>
        <input id="swal-nombre" class="swal2-input custom-swal-input" value="${silla.nombre}" placeholder="Ej: Silla Principal" style="margin: 0 0 20px 0; width: 100%; box-sizing: border-box;">
        
        <label style="font-weight: 700; margin-bottom: 10px; display: block; color: #94a3b8; text-transform: uppercase; font-size: 0.75rem;">Orden de Prioridad</label>
        <input 
          id="swal-orden" 
          type="number" 
          min="1" 
          step="1" 
          onkeypress="return event.charCode >= 48 && event.charCode <= 57"
          class="swal2-input custom-swal-input" 
          value="${silla.orden}" 
          placeholder="1" 
          style="margin: 0; width: 100%; box-sizing: border-box;"
        >
      </div>
    `,
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Guardar Cambios',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#0ea5e9',
    cancelButtonColor: '#334155',
    preConfirm: () => {
      const nombre = document.getElementById('swal-nombre').value.trim();
      const orden = parseInt(document.getElementById('swal-orden').value);

      if (!nombre) {
        Swal.showValidationMessage('El nombre de la silla es obligatorio.');
        return false;
      }

      if (isNaN(orden) || orden < 1) {
        Swal.showValidationMessage('El orden debe ser un número válido mayor a 0.');
        return false;
      }

      const ordenOcupado = sillas.value.some(s => s.orden === orden && s.id !== silla.id);
      if (ordenOcupado) {
        Swal.showValidationMessage(`El orden #${orden} ya está ocupado por otra silla.`);
        return false;
      }

      return { nombre, orden };
    }
  });

  if (formValues && formValues.nombre) {
    try {
      await axios.patch(`/api/sillas/${silla.id}/`, {
        nombre: formValues.nombre,
        orden: formValues.orden
      });
      cargarSillas();
      Swal.fire({ icon: 'success', title: 'Silla actualizada', timer: 1500, showConfirmButton: false, background: '#0f172a', color: '#f8fafc' });
    } catch (e) {
      let mensajeError = 'No se pudo actualizar la silla.';
      if (e.response && e.response.data && e.response.data.nombre) mensajeError = e.response.data.nombre[0];
      Swal.fire({ title: 'Error', text: mensajeError, icon: 'warning', background: '#0f172a', color: '#f8fafc' });
    }
  }
};

const toggleEstado = async (silla) => {
  if (silla.activa) {
    const { value: motivo } = await Swal.fire({
      title: 'Deshabilitar Puesto',
      text: `¿Por qué vas a cerrar "${silla.nombre}"?`,
      icon: 'question',
      input: 'select',
      inputOptions: {
        'Reparación': '🔧 Reparación / Mantenimiento',
        'Falta de Personal': '👨‍ Barberos insuficientes',
      },
      inputPlaceholder: 'Seleccioná un motivo',
      showCancelButton: true,
      confirmButtonText: 'Confirmar Baja',
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#334155',
      background: '#0f172a',
      color: '#f8fafc',
      customClass: {
        input: 'swal-select-unified'
      },
      inputValidator: (value) => {
        return new Promise((resolve) => {
          if (value) resolve()
          else resolve('Debes seleccionar un motivo')
        })
      }
    });

    if (motivo) {
      try {
        await axios.patch(`/api/sillas/${silla.id}/`, { activa: false, motivo_inactividad: motivo });
        cargarSillas();
      } catch (e) {
        Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo actualizar', background: '#0f172a', color: '#f8fafc' });
      }
    }
  } else {
    try {
      await axios.patch(`/api/sillas/${silla.id}/`, { activa: true, motivo_inactividad: null });
      cargarSillas();
      Swal.fire({ icon: 'success', title: 'Puesto habilitado', timer: 1500, showConfirmButton: false, background: '#0f172a', color: '#f8fafc' });
    } catch (e) {
      Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo activar', background: '#0f172a', color: '#f8fafc' });
    }
  }
};
</script>

<style scoped>
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

.orden-badge { position: absolute; top: 15px; right: 15px; background: var(--bg-secondary); border: 1px solid var(--border-color); padding: 2px 8px; border-radius: 8px; font-size: 0.7rem; font-weight: 800; color: var(--text-secondary); }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-top: 5px; }
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

/* ESTILO DEL BOTÓN EDITAR QUE AGREGAMOS */
.action-btn.edit { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); }
.action-btn.edit:hover { background: var(--hover-bg); transform: translateY(-2px); border-color: var(--accent-color); color: var(--accent-color); }

.action-btn.delete { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.action-btn.delete:hover { background: #ef4444; color: white; transform: translateY(-2px); }
.action-btn.success { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.action-btn.success:hover { background: #10b981; color: white; transform: translateY(-2px); }

.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); font-size: 0.9rem;}
.register-button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); }
.sm-btn { padding: 8px 16px; font-size: 0.85rem; box-shadow: none; }

.loading-state, .empty-state { width: 100%; text-align: center; padding: 40px 0; color: var(--text-secondary); font-style: italic; }
.animate-spin { animation: spin 1s linear infinite; display: inline-block; font-size: 1.5rem; margin-right: 10px; vertical-align: middle;}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

</style>

<style>
.swal2-container .custom-swal-input {
  background-color: var(--bg-primary, #1e293b) !important;
  color: white !important;
  border: 2px solid var(--border-color, #334155) !important;
  border-radius: 10px !important;
  padding: 12px 14px !important;
  transition: all 0.3s;
}
.swal2-container .custom-swal-input:focus {
  border-color: #0ea5e9 !important;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.2) !important;
}

.swal2-container .swal-select-unified {
  background-color: var(--bg-primary, #1e293b) !important;
  color: white !important;
  border: 2px solid var(--border-color, #334155) !important;
  border-radius: 10px !important;
}
.swal2-container .swal-select-unified option {
  background-color: #0f172a !important;
  color: white !important;
}
</style>