<template>
  <div class="sillas-wrapper">
    <div class="header-sillas">
      <div class="titulo-icon">
        <div class="icon-box">🪑</div>
        <div>
          <h3>Infraestructura</h3>
          <p>Gestioná la disponibilidad de tus puestos de trabajo.</p>
        </div>
      </div>
      <button class="btn-neon" @click="abrirModalCrear" :disabled="cargando">
        <span>+ Nueva Silla</span>
      </button>
    </div>

    <div v-if="cargando" class="loading-state">
      <span class="spinner"></span> Sincronizando...
    </div>

    <div v-else-if="sillas.length === 0" class="empty-state">
      <i class="ri-information-line"></i>
      <p>No hay sillas registradas. Agregá la primera para comenzar.</p>
    </div>

    <div v-else class="grid-sillas">
      <div 
        v-for="silla in sillas" 
        :key="silla.id" 
        class="card-silla"
        :class="silla.activa ? 'status-active' : 'status-inactive'"
      >
        <div class="orden-badge" title="Prioridad de asignación">
          #{{ silla.orden }}
        </div>

        <div class="card-content">
          <div class="icon-status">
            <i :class="silla.activa ? 'ri-checkbox-circle-fill' : 'ri-tools-fill'"></i>
          </div>
          
          <h4 class="silla-nombre">{{ silla.nombre }}</h4>
          
          <div class="status-text">
            <span v-if="silla.activa" class="text-success">Disponible</span>
            <span v-else class="text-danger">
              Fuera de Servicio
              <br>
              <small class="motivo-tag">"{{ silla.motivo_inactividad || 'Mantenimiento' }}"</small>
            </span>
          </div>
        </div>

        <div class="card-actions">
          <button 
            class="action-btn"
            :class="silla.activa ? 'btn-shutdown' : 'btn-powerup'"
            @click="toggleEstado(silla)"
          >
            {{ silla.activa ? 'Deshabilitar' : 'Habilitar' }}
          </button>
          
          <button class="action-btn btn-delete" @click="eliminar(silla)">
            <i class="ri-delete-bin-line"></i>
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
    sillas.value = res.data;
  } catch (error) {
    console.error("Error cargando sillas", error);
  } finally {
    cargando.value = false;
  }
};

const abrirModalCrear = async () => {
  const { value: formValues } = await Swal.fire({
    title: 'Nueva Silla',
    background: '#1e293b',
    color: '#fff',
    html: `
      <div style="text-align:left">
        <label class="swal-label">Nombre del Puesto</label>
        <input id="swal-nombre" class="swal2-input custom-input" placeholder="Ej: Silla Principal">
        <label class="swal-label">Orden de Prioridad</label>
        <input id="swal-orden" type="number" class="swal2-input custom-input" placeholder="1" value="${sillas.value.length + 1}">
      </div>
    `,
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Crear',
    confirmButtonColor: '#3b82f6',
    preConfirm: () => {
      return {
        nombre: document.getElementById('swal-nombre').value,
        orden: document.getElementById('swal-orden').value
      }
    }
  });

  if (formValues && formValues.nombre) {
    try {
      await axios.post('/api/sillas/', {
        nombre: formValues.nombre,
        orden: formValues.orden || 1,
        activa: true
      });
      cargarSillas();
      const Toast = Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 3000, timerProgressBar: true });
      Toast.fire({ icon: 'success', title: 'Silla creada con éxito' });
    } catch (e) {
      Swal.fire('Error', 'No se pudo crear la silla, ya existe una silla con ese nombre', 'error');
    }
  }
};

const toggleEstado = async (silla) => {
  // Si la silla está ACTIVA, la vamos a DESACTIVAR (Pedir motivo)
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
      background: '#1e293b', // Fondo oscuro del modal
      color: '#fff', // Texto general blanco
      customClass: {
        input: 'swal-select-dark' // Clase custom para arreglar el select
      },
      inputValidator: (value) => {
        return new Promise((resolve) => {
          if (value) {
            resolve()
          } else {
            resolve('Debes seleccionar un motivo')
          }
        })
      }
    });

    if (motivo) {
      try {
        await axios.patch(`/api/sillas/${silla.id}/`, { activa: false, motivo_inactividad: motivo });
        cargarSillas();
      } catch (e) {
        Swal.fire('Error', 'No se pudo actualizar', 'error');
      }
    }
  } 
  // Si la silla está INACTIVA, la vamos a ACTIVAR (Borrar motivo)
  else {
    try {
      // Mandamos motivo_inactividad: null para limpiar
      await axios.patch(`/api/sillas/${silla.id}/`, { activa: true, motivo_inactividad: null });
      cargarSillas();
      const Toast = Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 });
      Toast.fire({ icon: 'success', title: 'Puesto habilitado nuevamente' });
    } catch (e) {
      Swal.fire('Error', 'No se pudo activar', 'error');
    }
  }
};

const eliminar = async (silla) => {
  const result = await Swal.fire({
    title: '¿Eliminar definitivamente?',
    text: "Esta acción no se recomienda si ya hay turnos históricos en esta silla.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    confirmButtonText: 'Sí, eliminar',
    background: '#1e293b',
    color: '#fff'
  });

  if (result.isConfirmed) {
    try {
      await axios.delete(`/api/sillas/${silla.id}/`);
      cargarSillas();
      Swal.fire({ title: 'Eliminado', icon: 'success', timer: 1500, showConfirmButton: false, background: '#1e293b', color: '#fff' });
    } catch (e) {
      Swal.fire('Error', 'No se pudo eliminar', 'error');
    }
  }
};
</script>

<style scoped>
/* Contenedor Principal con efecto Glass */
.sillas-wrapper {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

/* Header */
.header-sillas {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.titulo-icon {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-box {
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.header-sillas h3 { margin: 0; color: #fff; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.5px; }
.header-sillas p { margin: 0; color: #94a3b8; font-size: 0.9rem; }

/* Botón Neon */
.btn-neon {
  background: transparent;
  border: 2px solid #3b82f6;
  color: #3b82f6;
  padding: 10px 25px;
  border-radius: 50px;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.1);
}

.btn-neon:hover:not(:disabled) {
  background: #3b82f6;
  color: white;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
  transform: translateY(-2px);
}

/* Grid */
.grid-sillas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

/* Tarjetas */
.card-silla {
  background: #1e293b;
  border-radius: 16px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 200px;
  border: 1px solid transparent;
}

.card-silla:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.4);
}

/* Estados de la tarjeta (Bordes de Neon) */
.status-active {
  border-color: rgba(34, 197, 94, 0.3);
  box-shadow: inset 0 0 20px rgba(34, 197, 94, 0.05);
}
.status-active:hover { border-color: #22c55e; }

.status-inactive {
  border-color: rgba(239, 68, 68, 0.3);
  box-shadow: inset 0 0 20px rgba(239, 68, 68, 0.05);
  opacity: 0.9;
}
.status-inactive:hover { border-color: #ef4444; }

/* Contenido Interno */
.orden-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(255,255,255,0.1);
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 800;
  color: #64748b;
}

.card-content { text-align: center; margin-top: 10px; }

.icon-status {
  font-size: 2.5rem;
  margin-bottom: 10px;
  transition: 0.3s;
}
.status-active .icon-status { color: #22c55e; text-shadow: 0 0 15px rgba(34, 197, 94, 0.5); }
.status-inactive .icon-status { color: #ef4444; text-shadow: 0 0 15px rgba(239, 68, 68, 0.5); }

.silla-nombre {
  font-size: 1.2rem;
  color: #f8fafc;
  margin: 0 0 5px 0;
  font-weight: 700;
}

.motivo-tag {
  display: inline-block;
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  padding: 3px 8px;
  border-radius: 4px;
  margin-top: 5px;
  font-style: italic;
}

/* Botones del Card */
.card-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  border: none;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: 0.2s;
}

.btn-shutdown {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}
.btn-shutdown:hover { background: #ef4444; color: white; }

.btn-powerup {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}
.btn-powerup:hover { background: #22c55e; color: white; }

.btn-delete {
  flex: 0;
  min-width: 40px;
  background: transparent;
  color: #64748b;
  border: 1px solid #334155;
}
.btn-delete:hover { color: #fff; border-color: #fff; }

/* Helpers */
.loading-state, .empty-state { text-align: center; padding: 40px; color: #94a3b8; }
.swal-label { color: #ccc; display: block; margin-top: 10px; margin-bottom: 5px; font-size: 0.9rem; }
.custom-input { width: 100% !important; margin: 0 !important; background: #0f172a !important; color: white !important; border: 1px solid #334155 !important; }
</style>

<style>
/* Estilos globales para SweetAlert que no se pueden scopear */
.swal2-container .swal-select-dark {
  background-color: #0f172a !important;
  color: white !important;
  border: 1px solid #3b82f6 !important;
}
.swal2-container .swal-select-dark option {
  background-color: #0f172a !important;
  color: white !important;
}
</style>