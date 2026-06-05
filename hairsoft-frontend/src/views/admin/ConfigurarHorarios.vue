<template>
  <div class="list-container">
    <div class="list-card">
      <header class="list-header">
        <div class="header-content">
          <h1>Horarios de Atenci&oacute;n</h1>
          <p>Configur&aacute; los d&iacute;as y franjas horarias en las que el local atiende al p&uacute;blico</p>
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
        <p>Cargando horarios...</p>
      </div>

      <div v-else class="fade-in">

        <div class="info-banner">
          <Info :size="18" />
          <span>Los cambios se aplican inmediatamente a la validaci&oacute;n de nuevos turnos. Los turnos ya existentes no se ven afectados.</span>
        </div>

        <div class="rango-reserva-card">
          <div class="rango-reserva-content">
            <Calendar :size="20" />
            <label>Anticipaci&oacute;n m&aacute;xima para reservar turnos</label>
            <input v-model.number="diasMaximosReserva" type="number" class="filter-input rango-input" min="1" max="30" />
            <span class="rango-badge">D&iacute;as</span>
            <span class="rango-hint">M&aacute;x. 30 d&iacute;as</span>
          </div>
        </div>

        <div v-for="(h, idx) in horarios" :key="h.id">
          <div class="usuarios-count">
            <p>
              <span class="dia-nro">{{ h.dia_semana + 1 }}</span>
              {{ h.dia_nombre }}
            </p>
            <div class="toggle-wrapper">
              <label class="switch">
                <input type="checkbox" v-model="h.trabaja" />
                <span class="switch-slider"></span>
              </label>
              <span :class="['toggle-label', h.trabaja ? 'activo' : 'inactivo']">
                {{ h.trabaja ? 'Abierto' : 'Cerrado' }}
              </span>
            </div>
          </div>

          <div v-if="h.trabaja" class="filters-container">
            <div class="row-2-cols">
              <div class="filter-group">
                <label>
                  Turno Ma&ntilde;ana
                  <span class="range-hint">(00:00 - 12:00)</span>
                </label>
                <div class="time-pair">
                  <select
                    v-model="h.hora_apertura_manana"
                    class="filter-input time-select"
                    @change="ajustarManana(h)"
                  >
                    <option value="">&mdash;</option>
                    <option
                      v-for="t in filtrarMananaApertura(h)"
                      :key="t"
                      :value="t"
                    >{{ t }}</option>
                  </select>
                  <span class="time-sep">a</span>
                  <select
                    v-model="h.hora_cierre_manana"
                    class="filter-input time-select"
                    @change="ajustarTardeApertura(h)"
                  >
                    <option value="">&mdash;</option>
                    <option
                      v-for="t in filtrarMananaCierre(h)"
                      :key="t"
                      :value="t"
                    >{{ t }}</option>
                  </select>
                </div>
              </div>

              <div class="filter-group">
                <label>
                  Turno Tarde/Noche
                  <span class="range-hint">(12:00 - 23:59)</span>
                </label>
                <div class="time-pair">
                  <select
                    v-model="h.hora_apertura_tarde"
                    class="filter-input time-select"
                    @change="ajustarTarde(h)"
                  >
                    <option value="">&mdash;</option>
                    <option
                      v-for="t in filtrarTardeApertura(h)"
                      :key="t"
                      :value="t"
                    >{{ t }}</option>
                  </select>
                  <span class="time-sep">a</span>
                  <select
                    v-model="h.hora_cierre_tarde"
                    class="filter-input time-select"
                  >
                    <option value="">&mdash;</option>
                    <option
                      v-for="t in filtrarTardeCierre(h)"
                      :key="t"
                      :value="t"
                    >{{ t }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="filters-container dia-cerrado">
            <div class="cerrado-msg">
              <Clock :size="18" />
              <span>Sin atenci&oacute;n este d&iacute;a</span>
            </div>
          </div>

          <div v-if="idx < horarios.length - 1" class="divider"></div>
        </div>

        <div class="footer-actions">
          <button @click="guardarCambios" :disabled="guardando" class="register-button">
            <Save v-if="!guardando" :size="20" />
            <Loader2 v-else class="animate-spin" :size="20" />
            <span>{{ guardando ? 'Guardando...' : 'Guardar Cambios' }}</span>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '../../utils/axiosConfig'
import { Save, Loader2, Info, Clock, Calendar } from 'lucide-vue-next'
import Swal from 'sweetalert2'

const horarios = ref([])
const cargando = ref(true)
const guardando = ref(false)
const diasMaximosReserva = ref(7)

const generarOpciones = (inicio, fin, paso = 10) => {
  const arr = []
  for (let m = inicio; m <= fin; m += paso) {
    arr.push(`${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`)
  }
  return arr
}

const opcionesManana = computed(() => generarOpciones(0, 720))
const opcionesTarde = computed(() => generarOpciones(720, 1430))

const filtrarMananaApertura = (h) =>
  opcionesManana.value.filter(t => !h.hora_cierre_manana || t < h.hora_cierre_manana)

const filtrarMananaCierre = (h) =>
  opcionesManana.value.filter(t => !h.hora_apertura_manana || t > h.hora_apertura_manana)

const filtrarTardeApertura = (h) => {
  let opts = opcionesTarde.value
  if (h.hora_cierre_manana) opts = opts.filter(t => t > h.hora_cierre_manana)
  if (h.hora_cierre_tarde) opts = opts.filter(t => t < h.hora_cierre_tarde)
  return opts
}

const filtrarTardeCierre = (h) =>
  opcionesTarde.value.filter(t => !h.hora_apertura_tarde || t > h.hora_apertura_tarde)

const ajustarManana = (h) => {
  if (h.hora_cierre_manana && h.hora_cierre_manana <= h.hora_apertura_manana) {
    h.hora_cierre_manana = ''
  }
}

const ajustarTardeApertura = (h) => {
  if (h.hora_apertura_tarde && h.hora_cierre_manana && h.hora_apertura_tarde <= h.hora_cierre_manana) {
    h.hora_apertura_tarde = ''
  }
}

const ajustarTarde = (h) => {
  if (h.hora_cierre_tarde && h.hora_cierre_tarde <= h.hora_apertura_tarde) {
    h.hora_cierre_tarde = ''
  }
}

const cargarHorarios = async () => {
  cargando.value = true
  try {
    const [res, resConfig] = await Promise.all([
      axios.get('/api/horarios/'),
      axios.get('/api/configuracion/'),
    ])
    const t = v => v ? v.split(':').slice(0, 2).join(':') : ''
    horarios.value = res.data.map(h => ({
      ...h,
      hora_apertura_manana: t(h.hora_apertura_manana),
      hora_cierre_manana: t(h.hora_cierre_manana),
      hora_apertura_tarde: t(h.hora_apertura_tarde),
      hora_cierre_tarde: t(h.hora_cierre_tarde),
    }))
    if (resConfig.data?.dias_maximos_reserva) {
      diasMaximosReserva.value = resConfig.data.dias_maximos_reserva
    }
  } catch {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudieron cargar los horarios de atenci\u00f3n',
      background: '#0f172a',
      color: '#f8fafc',
      confirmButtonColor: '#0ea5e9',
    })
  } finally {
    cargando.value = false
  }
}

const validar = () => {
  const errores = []
  for (const h of horarios.value) {
    if (!h.trabaja) continue

    const mA = h.hora_apertura_manana
    const mC = h.hora_cierre_manana
    const tA = h.hora_apertura_tarde
    const tC = h.hora_cierre_tarde

    const tieneManana = mA && mC
    const tieneTarde = tA && tC

    if (!tieneManana && !tieneTarde) {
      errores.push(`${h.dia_nombre}: debe tener al menos un turno configurado`)
      continue
    }

    if (tieneManana) {
      if (mA >= mC) {
        errores.push(`${h.dia_nombre}: el turno ma\u00F1ana debe terminar despu\u00e9s de empezar`)
      }
      if (mA > '12:00' || mC > '12:00') {
        errores.push(`${h.dia_nombre}: el turno ma\u00F1ana excede el rango 00:00 - 12:00`)
      }
    }

    if (tieneTarde) {
      if (tA >= tC) {
        errores.push(`${h.dia_nombre}: el turno tarde/noche debe terminar despu\u00e9s de empezar`)
      }
      if (tA < '12:00') {
        errores.push(`${h.dia_nombre}: el turno tarde/noche debe iniciar despu\u00e9s de las 12:00`)
      }
    }

    if (tieneManana && tieneTarde && mC > tA) {
      errores.push(`${h.dia_nombre}: el turno ma\u00F1ana y tarde/noche no deben superponerse`)
    }
  }
  return errores
}

const guardarCambios = async () => {
  const errores = validar()
  if (errores.length) {
    return Swal.fire({
      icon: 'warning',
      title: 'Validaci\u00f3n',
      html: errores.map(e => `<div style="text-align:left;padding:2px 0">&bull; ${e}</div>`).join(''),
      background: '#0f172a',
      color: '#f8fafc',
      confirmButtonColor: '#0ea5e9',
    })
  }

  guardando.value = true
  try {
    await Promise.all([
      ...horarios.value.map(h =>
        axios.put(`/api/horarios/${h.id}/`, {
          dia_semana: h.dia_semana,
          trabaja: h.trabaja,
          hora_apertura_manana: h.trabaja && h.hora_apertura_manana ? h.hora_apertura_manana : null,
          hora_cierre_manana: h.trabaja && h.hora_cierre_manana ? h.hora_cierre_manana : null,
          hora_apertura_tarde: h.trabaja && h.hora_apertura_tarde ? h.hora_apertura_tarde : null,
          hora_cierre_tarde: h.trabaja && h.hora_cierre_tarde ? h.hora_cierre_tarde : null,
        })
      ),
      axios.post('/api/configuracion/', { dias_maximos_reserva: diasMaximosReserva.value }),
    ])
    await Swal.fire({
      icon: 'success',
      title: '\u00a1Horarios guardados!',
      text: 'Los horarios de atenci\u00f3n se actualizaron correctamente.',
      timer: 2000,
      showConfirmButton: false,
      background: '#0f172a',
      color: '#f8fafc',
    })
  } catch (e) {
    const detalle = e.response?.data
    let msg = 'Ocurri\u00f3 un error inesperado'
    if (typeof detalle === 'string') msg = detalle
    else if (detalle && typeof detalle === 'object') {
      const partes = Object.values(detalle).flat().filter(Boolean)
      if (partes.length) msg = partes.join('. ')
    }
    Swal.fire({
      icon: 'error',
      title: 'Error al guardar',
      text: msg,
      background: '#0f172a',
      color: '#f8fafc',
      confirmButtonColor: '#0ea5e9',
    })
  } finally {
    guardando.value = false
  }
}

onMounted(cargarHorarios)
</script>

<style scoped>
.list-container {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}
.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color);
}
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
}
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 25px;
  flex-wrap: wrap;
  gap: 20px;
}
.header-content h1 {
  margin: 0;
  font-size: 2.2rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}
.header-content p {
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 8px;
  font-size: 0.95rem;
}

/* Botón guardar */
.register-button {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  font-size: 0.9rem;
  white-space: nowrap;
}
.register-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
}
.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Info banner */
.info-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: 30px;
}
.info-banner svg {
  color: #0ea5e9;
  flex-shrink: 0;
}

/* Rango de reserva */
.rango-reserva-card {
  display: flex;
  align-items: center;
  padding: 14px 24px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  margin-bottom: 30px;
}
.rango-reserva-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  flex-wrap: wrap;
}
.rango-reserva-content label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.85rem;
  white-space: nowrap;
}
.rango-input {
  width: 80px !important;
  text-align: center;
  padding: 10px !important;
}
.rango-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.rango-reserva-content svg {
  color: #0ea5e9;
  flex-shrink: 0;
}
.rango-hint {
  font-size: 0.7rem;
  color: var(--text-tertiary);
  font-style: italic;
}

/* Sección por día */
.usuarios-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 30px 0 0;
  padding: 15px 25px;
  background: var(--bg-primary);
  border-radius: 12px;
  border-left: 5px solid var(--accent-color);
}
.usuarios-count p {
  color: var(--text-primary);
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.dia-nro {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent-color);
  color: white;
  font-size: 0.75rem;
  font-weight: 800;
}

/* Toggle */
.toggle-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
}
.switch input { opacity: 0; width: 0; height: 0; }
.switch-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: #334155;
  border-radius: 24px;
  transition: 0.3s;
}
.switch-slider::before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: #94a3b8;
  border-radius: 50%;
  transition: 0.3s;
}
.switch input:checked + .switch-slider {
  background: #0ea5e9;
}
.switch input:checked + .switch-slider::before {
  transform: translateX(20px);
  background: white;
}
.toggle-label {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 4px 12px;
  border-radius: 20px;
  transition: all 0.3s ease;
}
.toggle-label.activo {
  color: #10b981;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.toggle-label.inactivo {
  color: #94a3b8;
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.15);
}

/* Contenedor horarios */
.filters-container {
  margin-bottom: 0;
  background: var(--hover-bg);
  padding: 24px 30px;
  border-radius: 0 0 16px 16px;
  border: 1px solid var(--border-color);
  border-top: none;
}
.dia-cerrado {
  padding: 16px 30px;
}
.cerrado-msg {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #94a3b8;
  font-size: 0.9rem;
  font-style: italic;
  padding: 6px 14px;
  background: rgba(148, 163, 184, 0.06);
  border-radius: 10px;
  border: 1px dashed rgba(148, 163, 184, 0.2);
  width: fit-content;
}
.cerrado-msg svg { color: #94a3b8; }

.row-2-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}
.filter-group {
  display: flex;
  flex-direction: column;
}
.filter-group label {
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}
.range-hint {
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
  color: var(--text-tertiary);
  font-size: 0.7rem;
}
.filter-input {
  padding: 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s;
  width: 100%;
  font-family: inherit;
}
.time-select {
  min-width: 110px;
  cursor: pointer;
  appearance: auto;
}
.filter-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
}
.filter-input option {
  color: #1e293b;
  background: #ffffff;
}
.time-pair {
  display: flex;
  align-items: center;
  gap: 10px;
}
.time-sep {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-weight: 600;
  flex-shrink: 0;
}

/* Divider entre días */
.divider {
  border: 0;
  height: 1px;
  background: var(--border-color);
  margin: 0;
  opacity: 0.3;
}

/* Footer */
.footer-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 30px;
  margin-top: 10px;
}

/* Loading */
.no-results {
  text-align: center;
  padding: 100px 0;
  color: var(--text-secondary);
}
.no-results-icon {
  margin-bottom: 20px;
  color: var(--accent-color);
}
.animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Animación fade-in */
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 768px) {
  .row-2-cols { grid-template-columns: 1fr; }
  .list-header { flex-direction: column; }
  .header-content h1 { font-size: 1.6rem; }
  .filters-container { padding: 20px; }
}
</style>
