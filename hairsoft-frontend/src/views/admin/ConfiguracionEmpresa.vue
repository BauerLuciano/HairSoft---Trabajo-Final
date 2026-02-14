<template>
  <div class="list-container">
    <div class="list-card">
      <header class="list-header">
        <div class="header-content">
          <h1>Ajustes del Local</h1>
          <p>Gestión de identidad corporativa y políticas de reserva</p>
        </div>
        <div class="header-buttons">
          <button @click="guardarCambios" :disabled="guardando || cargando" class="register-button">
            <Save v-if="!guardando" :size="20" />
            <Loader2 v-else class="animate-spin" :size="20" />
            <span>{{ guardando ? 'Guardando...' : 'Guardar Cambios' }}</span>
          </button>
        </div>
      </header>

      <div v-if="cargando" class="no-results">
        <Loader2 class="animate-spin no-results-icon" :size="48" />
        <p>Sincronizando con el servidor...</p>
      </div>

      <div v-else class="fade-in">
        
        <div class="usuarios-count">
          <p><Info :size="20" /> Logo y Marca Visual</p>
        </div>

        <div class="filters-container">
          <div class="logo-upload-section">
            <div class="logo-preview-container">
              <img v-if="previewLogo || config.logo" :src="previewLogo || config.logo" class="logo-img-preview" />
              <Building2 v-else :size="40" class="placeholder-icon" />
            </div>
            
            <div class="upload-controls">
              <label class="upload-btn">
                <i class="ri-image-add-line"></i>
                <span>Seleccionar Logo</span>
                <input type="file" @change="handleFileUpload" accept="image/*" style="display: none;" />
              </label>
              <p class="upload-hint">Recomendado: Imagen cuadrada (PNG/JPG) sobre fondo oscuro.</p>
            </div>
          </div>
        </div>

        <div class="usuarios-count">
          <p><Building2 :size="20" /> Información de Facturación y Contacto</p>
        </div>

        <div class="filters-container">
          <div class="vertical-stack">
            
            <div class="filter-group">
              <label>Razón Social</label>
              <input v-model="config.razon_social" type="text" class="filter-input" placeholder="Nombre legal" />
            </div>

            <div class="row-2-cols">
              <div class="filter-group">
                <label>CUIL / CUIT</label>
                <input v-model="config.cuil_cuit" type="text" class="filter-input" placeholder="XX-XXXXXXXX-X" maxlength="13" />
              </div>
              <div class="filter-group">
                <label>Teléfono</label>
                <input v-model="config.telefono" type="text" class="filter-input" placeholder="3755xxxxxx" maxlength="15" />
              </div>
            </div>

            <div class="filter-group">
              <label>Dirección Comercial</label>
              <input v-model="config.direccion" type="text" class="filter-input" placeholder="Ubicación física del local" />
            </div>
            
            <div class="filter-group">
              <label>Email de Contacto</label>
              <input v-model="config.email" type="email" class="filter-input" placeholder="correo@ejemplo.com" />
            </div>

          </div>
        </div>

        <div class="usuarios-count">
          <p><Clock :size="20" /> Reglas de Negocio y Automatización</p>
        </div>

        <div class="filters-container">
          <div class="vertical-stack">
            
            <div class="process-group">
              
              <div class="filter-group">
                <label style="color: #0ea5e9;">Automatización: Cancelaciones y Reembolsos</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <input v-model.number="config.margen_horas_cancelacion" type="number" class="filter-input input-short" min="1" />
                  <span class="badge-estado estado-info">Horas antes del turno</span>
                </div>
              </div>

              <div class="filter-group mt-3">
                <label>Texto Informativo de Política de Señas</label>
                <textarea 
                  v-model="config.politica_senia" 
                  class="filter-input" 
                  style="height: 100px; resize: none; padding: 15px; line-height: 1.6;"
                  placeholder="Escribí aquí lo que el cliente leerá antes de pagar la seña..."
                ></textarea>
              </div>

            </div>

            <hr class="divider">

            <div class="process-group">
              <div class="filter-group">
                <label style="color: #f97316;">Automatización: Reactivación de Clientes</label>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <input v-model.number="config.dias_inactividad_clientes" type="number" class="filter-input input-short" min="1" />
                  <span class="badge-estado estado-alert">Días sin asistir</span>
                </div>
                <small style="color: var(--text-secondary); margin-top: 8px;">
                  * Al superar estos días, se envía un WhatsApp automático con promo.
                </small>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../../utils/axiosConfig'
import { Building2, Clock, Save, Loader2, Info } from 'lucide-vue-next'
import Swal from 'sweetalert2'

const config = ref({
  razon_social: '',
  cuil_cuit: '',
  direccion: '',
  telefono: '',
  email: '',
  margen_horas_cancelacion: 3,
  dias_inactividad_clientes: 60,
  politica_senia: '',
  logo: null
})

const cargando = ref(true)
const guardando = ref(false)
const previewLogo = ref(null)
const logoFile = ref(null)

const obtenerConfig = async () => {
  try {
    const res = await axios.get('/api/configuracion/')
    const data = res.data

    if (data.logo) {
      data.logo = `${data.logo}?t=${new Date().getTime()}`;
    }

    config.value = data
  } catch (e) {
    console.error(e)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo cargar la configuración',
      background: '#0f172a',
      color: '#f8fafc'
    })
  } finally {
    cargando.value = false
  }
}

// ✅ Manejo de selección de archivo
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    logoFile.value = file
    previewLogo.value = URL.createObjectURL(file) // Crear URL temporal para previsualización
  }
}

const validarFormulario = () => {
  const cuitRegex = /^\d{2}-\d{8}-\d{1}$/;
  
  if (!config.value.razon_social.trim()) return "La Razón Social es obligatoria.";
  if (!cuitRegex.test(config.value.cuil_cuit)) return "El CUIT debe tener el formato exacto XX-XXXXXXXX-X.";
  if (config.value.telefono.length > 15) return "El teléfono no puede superar los 15 dígitos.";
  if (!config.value.email.includes('@')) return "El email debe ser válido.";
  if (config.value.dias_inactividad_clientes < 1) return "Los días de inactividad deben ser al menos 1.";

  return null; 
}

const guardarCambios = async () => {
  const errorMsg = validarFormulario();
  if (errorMsg) {
    return Swal.fire({
      icon: 'warning',
      title: 'Validación',
      text: errorMsg,
      background: '#0f172a',
      color: '#f8fafc'
    });
  }

  guardando.value = true

  // ✅ Uso de FormData para enviar archivo de imagen + textos
  const formData = new FormData();
  formData.append('razon_social', config.value.razon_social);
  formData.append('cuil_cuit', config.value.cuil_cuit);
  formData.append('direccion', config.value.direccion);
  formData.append('telefono', config.value.telefono);
  formData.append('email', config.value.email);
  formData.append('margen_horas_cancelacion', config.value.margen_horas_cancelacion);
  formData.append('dias_inactividad_clientes', config.value.dias_inactividad_clientes);
  formData.append('politica_senia', config.value.politica_senia);
  
  // Si el usuario seleccionó un archivo nuevo, lo adjuntamos
  if (logoFile.value) {
    formData.append('logo', logoFile.value);
  }

  try {
    await axios.post('/api/configuracion/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    await Swal.fire({
      icon: 'success',
      title: '¡Ajustes guardados!',
      text: 'La configuración del local ha sido actualizada.',
      timer: 2000,
      showConfirmButton: false,
      background: '#0f172a',
      color: '#f8fafc'
    })

    // ✅ Forzar recarga para que el Sidebar actualice el logo
    window.location.reload();

  } catch (e) {
    console.error(e)
    Swal.fire({
      icon: 'error',
      title: 'Fallo al guardar',
      text: 'Ocurrió un error al procesar la solicitud.',
      background: '#0f172a',
      color: '#f8fafc'
    })
  } finally {
    guardando.value = false
  }
}

onMounted(obtenerConfig)
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE 
   ======================================== */

.list-container { padding: 32px; max-width: 1200px; margin: 0 auto; min-height: 100vh; font-family: 'Inter', sans-serif; }
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; }

.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; display: flex; align-items: center; gap: 10px; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); }
.register-button:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); }

/* SECCIÓN UPLOAD LOGO */
.logo-upload-section { display: flex; align-items: center; gap: 30px; }
.logo-preview-container { width: 120px; height: 120px; border: 2px dashed var(--border-color); border-radius: 18px; display: flex; align-items: center; justify-content: center; overflow: hidden; background: var(--bg-primary); }
.logo-img-preview { width: 100%; height: 100%; object-fit: cover; }
.placeholder-icon { opacity: 0.3; color: var(--text-secondary); }
.upload-btn { background: var(--bg-tertiary); color: white; padding: 10px 20px; border-radius: 10px; border: 1px solid var(--border-color); cursor: pointer; font-weight: 700; display: flex; align-items: center; gap: 8px; transition: 0.3s; font-size: 0.9rem; }
.upload-btn:hover { background: var(--hover-bg); transform: translateY(-2px); border-color: #0ea5e9; }
.upload-hint { font-size: 0.8rem; color: var(--text-tertiary); margin-top: 8px; font-style: italic; }

.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 30px; border-radius: 16px; border: 1px solid var(--border-color); }
.vertical-stack { display: flex; flex-direction: column; gap: 25px; }
.row-2-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.filter-group { display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 12px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }
.filter-input { padding: 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); font-size: 1rem; transition: all 0.3s; width: 100%; }
.input-short { width: 120px !important; text-align: center; font-weight: bold; }
.filter-input:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); }

.usuarios-count { display: flex; justify-content: space-between; align-items: center; margin: 40px 0 20px; padding: 15px 25px; background: var(--bg-primary); border-radius: 12px; border-left: 5px solid var(--accent-color); }
.usuarios-count p { color: #fff; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 10px; font-size: 1.1rem; }

.badge-estado { padding: 8px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
.estado-info { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; border: 2px solid #0ea5e9; }
.estado-alert { background: rgba(249, 115, 22, 0.1); color: #f97316; border: 2px solid #f97316; }
.divider { border: 0; height: 1px; background: var(--border-color); margin: 15px 0; opacity: 0.3; }

.animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.no-results { text-align: center; padding: 100px 0; color: var(--text-secondary); }
.no-results-icon { margin-bottom: 20px; color: var(--accent-color); }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .row-2-cols { grid-template-columns: 1fr; }
  .logo-upload-section { flex-direction: column; text-align: center; }
}
</style>