<template>
  <div class="pedido-container">
    <div class="card-modern">
      <!-- Header -->
      <div class="header-section">
        <h2>
          ✏️ Modificar Turno
        </h2>
        <p class="subtitle">Editar turno existente</p>
      </div>

      <div v-if="cargando" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando datos del turno...</p>
      </div>


      <div v-else-if="error" class="error-state">
        <div class="error-icon">❌</div>
        <h3>Error</h3>
        <p>{{ error }}</p>
        <button @click="$router.back()" class="btn-volver">
          ← Volver
        </button>
      </div>

      <div v-else class="form-content">
        <!-- ==================== -->
        <!-- SECCIÓN CLIENTE (SOLO LECTURA) -->
        <!-- ==================== -->
        <div class="input-group cliente-section">
          <label class="section-label">
            Cliente:   
          </label>
          <div class="cliente-info-display">
            <span class="cliente-avatar">{{ turnoData.cliente_nombre?.charAt(0) }}</span>
            <div class="cliente-info">
              <span class="cliente-nombre">{{ turnoData.cliente_nombre }} {{ turnoData.cliente_apellido }}</span>
              <span class="cliente-dni">DNI: {{ turnoData.cliente_dni }}</span>
            </div>
          </div>
        </div>

        <!-- ==================== -->
        <!-- SECCIÓN PELUQUERO -->
        <!-- ==================== -->
        <div class="input-group">
          <label class="section-label">
            Peluquero:
          </label>
          <select v-model="form.peluquero" @change="limpiarFechaHora" class="select-modern-rounded">
            <option value="">Seleccione un peluquero</option>
            <option v-for="p in peluqueros" :key="p.id" :value="p.id">
              {{ p.nombre }} {{ p.apellido }}
            </option>
          </select>
        </div>

        <!-- ==================== -->
        <!-- SECCIÓN CATEGORÍAS (HORIZONTAL) -->
        <!-- ==================== -->
        <div class="input-group">
          <label class="section-label">
            Seleccionar Categorías
          </label>
          <div class="categorias-container-horizontal">
            <div class="categorias-grid-horizontal">
              <div 
                v-for="categoria in categorias" 
                :key="categoria.id"
                class="categoria-card-horizontal"
                :class="{ selected: categoriasSeleccionadas.includes(categoria.id) }"
                @click="toggleCategoria(categoria.id)"
              >
                <div class="categoria-checkbox-horizontal">
                  <span class="checkmark-horizontal" :class="{ checked: categoriasSeleccionadas.includes(categoria.id) }">
                    ✓
                  </span>
                </div>
                <div class="categoria-content-horizontal">
                  <span class="categoria-nombre-horizontal">{{ categoria.nombre }}</span>
                  <span class="categoria-desc-horizontal">{{ categoria.descripcion || 'Servicios de calidad' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="categoriasSeleccionadas.length === 0" class="no-selection">
            <span>📝</span>
            <p>Selecciona al menos una categoría para ver los servicios</p>
          </div>
        </div>

        <!-- ==================== -->
        <!-- SECCIÓN SERVICIOS -->
        <!-- ==================== -->
        <transition name="scale-fade">
          <div v-if="categoriasSeleccionadas.length > 0" class="input-group">
            <label class="section-label">
              Servicios Disponibles
              <span class="selected-categories">({{ categoriasSeleccionadasNombres }})</span>
            </label>
            
            <!-- Búsqueda de servicios -->
            <div class="busqueda-servicios">
              <input
                type="text"
                v-model="busquedaServicio"
                placeholder="Buscar servicio..."
                class="input-busqueda"
              />
            </div>
            
            <!-- Grid de Servicios Filtrados -->
            <div class="servicios-grid-horizontal" v-if="serviciosFiltrados.length > 0">
              <div 
                v-for="servicio in serviciosFiltrados" 
                :key="servicio.id"
                class="servicio-item-horizontal"
                :class="{ selected: form.servicios_ids.includes(servicio.id) }"
                @click="toggleServicio(servicio)"
              >
                <div class="servicio-checkbox">
                  <span class="checkmark" :class="{ checked: form.servicios_ids.includes(servicio.id) }">
                    ✓
                  </span>
                </div>
                <div class="servicio-info">
                  <span class="servicio-nombre">{{ servicio.nombre }}</span>
                  <div class="servicio-details">
                    <span class="servicio-precio">${{ servicio.precio }}</span>
                    <span class="servicio-duracion">{{ servicio.duracion }}min</span>
                  </div>
                  <span class="servicio-categoria">{{ getCategoriaNombre(servicio.categoria) }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="no-servicios">
              <p v-if="busquedaServicio">No se encontraron servicios con "{{ busquedaServicio }}"</p>
              <p v-else>No hay servicios en las categorías seleccionadas</p>
            </div>
          </div>
        </transition>

        <!-- ==================== -->
        <!-- RESUMEN -->
        <!-- ==================== -->
        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0" class="resumen-pedido">
            <div class="resumen-grid">
              <div class="resumen-item" v-for="servicioId in form.servicios_ids" :key="servicioId">
                <span>{{ getServicioNombre(servicioId) }}</span>
                <span>${{ getServicioPrecio(servicioId) }}</span>
              </div>
              <div class="resumen-item total">
                <span>Total</span>
                <span>${{ calcularTotal() }}</span>
              </div>
            </div>
          </div>
        </transition>

        <!-- ==================== -->
        <!-- CALENDARIO -->
        <!-- ==================== -->
        <transition name="scale-fade">
          <div v-if="form.servicios_ids.length > 0 && form.peluquero" class="input-group">
            <label class="section-label">
              Seleccionar Fecha
            </label>
            
            <div class="calendar-container-horizontal">
              <div class="calendar-grid-horizontal">
                <div 
                  v-for="dateInfo in fechasDisponibles" 
                  :key="dateInfo.fullDate"
                  class="date-card-horizontal"
                  :class="{ 
                    selected: form.fecha === dateInfo.fullDate,
                    today: dateInfo.isToday 
                  }"
                  @click="seleccionarFecha(dateInfo)"
                >
                  <div v-if="dateInfo.isToday" class="today-badge">Hoy</div>
                  <div class="date-content">
                    <span class="day-name">{{ dateInfo.dayName }}</span>
                    <span class="day-number">{{ dateInfo.dayNum }}</span>
                    <span class="month-name">{{ dateInfo.month }}</span>
                  </div>
                  <div class="shine-effect"></div>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <!-- ==================== -->
        <!-- HORARIO -->
        <!-- ==================== -->
        <transition name="scale-fade">
          <div v-if="form.fecha" class="input-group">
            <label class="section-label">
              Seleccionar Horario
            </label>
            
            <div class="time-picker-trigger" @click="abrirModalHora">
              <div class="time-display">
                <span class="time-icon">⏰</span>
                <span class="time-text">{{ form.hora || 'Seleccionar hora' }}</span>
                <span class="time-arrow">▼</span>
              </div>
            </div>
          </div>
        </transition>

        <!-- ==================== -->
        <!-- FORMA DE PAGO -->
        <!-- ==================== -->
        <transition name="scale-fade">
          <div v-if="form.hora" class="input-group">
            <label class="section-label">
              <span class="label-icon">💳</span>
              Forma de Pago
            </label>
            
            <div class="pago-container-horizontal">
              <div class="pago-options-horizontal">
                <label class="pago-option-horizontal" :class="{ selected: form.tipo_pago === 'SENA_50' }">
                  <input type="radio" v-model="form.tipo_pago" value="SENA_50" />
                  <div class="pago-content-horizontal">
                    <span class="pago-nombre-horizontal">Seña 50%</span>
                    <span class="pago-monto-horizontal">${{ calcularSena() }}</span>
                    <span class="pago-desc-horizontal">Cliente paga seña ahora</span>
                  </div>
                </label>

                <label class="pago-option-horizontal" :class="{ selected: form.tipo_pago === 'TOTAL' }">
                  <input type="radio" v-model="form.tipo_pago" value="TOTAL" />
                  <div class="pago-content-horizontal">
                    <span class="pago-nombre-horizontal">Pago Total</span>
                    <span class="pago-monto-horizontal">${{ calcularTotal() }}</span>
                    <span class="pago-desc-horizontal">Cliente paga todo ahora</span>
                  </div>
                </label>
              </div>

              <transition name="slide-fade">
                <div v-if="form.tipo_pago" class="medio-pago-section-horizontal">
                  <label class="section-label">Medio de Pago</label>
                  <div class="medio-pago-options-horizontal">
                    <button 
                      class="medio-pago-btn-horizontal" 
                      :class="{ active: form.medio_pago === 'EFECTIVO' }"
                      @click="form.medio_pago = 'EFECTIVO'"
                    >
                      <span class="medio-icon-horizontal">💵</span>
                      <span class="medio-text-horizontal">Efectivo</span>
                    </button>
                    <button 
                      class="medio-pago-btn-horizontal"
                      :class="{ active: form.medio_pago === 'TARJETA' }"
                      @click="form.medio_pago = 'TARJETA'"
                    >
                      <span class="medio-icon-horizontal">💳</span>
                      <span class="medio-text-horizontal">Tarjeta</span>
                    </button>
                    <button 
                      class="medio-pago-btn-horizontal"
                      :class="{ active: form.medio_pago === 'TRANSFERENCIA' }"
                      @click="form.medio_pago = 'TRANSFERENCIA'"
                    >
                      <span class="medio-icon-horizontal">📱</span>
                      <span class="medio-text-horizontal">Transferencia</span>
                    </button>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </transition>

        <!-- ==================== -->
        <!-- BOTÓN ACTUALIZAR -->
        <!-- ==================== -->
        <div class="form-actions">
          <button 
            @click="$router.back()" 
            class="btn-cancelar-premium"
          >
            <span class="btn-content">
              <span>❌</span>
              Cancelar
            </span>
          </button>

          <button 
            @click="modificarTurno" 
            class="btn-registrar-premium"
            :disabled="!formularioValido || guardando"
          >
            <span class="btn-content">
              <span>💾</span>
              {{ guardando ? 'Actualizando...' : textoBoton }}
            </span>
          </button>
        </div>

        <!-- ==================== -->
        <!-- MENSAJES -->
        <!-- ==================== -->
        <transition name="bounce">
          <div v-if="mensaje" class="mensaje-premium" :class="{ error: mensaje.includes('❌') }">
            <span class="mensaje-icon">{{ mensaje.includes('❌') ? '❌' : '✅' }}</span>
            <span class="mensaje-text">{{ mensaje }}</span>
          </div>
        </transition>
      </div>
    </div>

    <!-- Modal de Hora - IDÉNTICO AL DE REGISTRAR -->
    <div v-if="mostrarModalHora" class="modal-overlay" @click="cerrarModalHora">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🕐 Seleccionar Horario</h3>
          <button class="modal-close-btn" @click="cerrarModalHora">×</button>
        </div>
        <div class="modal-body">
          <div class="time-selector-modal-content">
            <!-- Selector de hora manual -->
            <div class="time-inputs-modal">
              <div class="input-group-modal">
                <label class="input-label-modal">HORA</label>
                <select v-model="horaSeleccionada" class="time-select-modal">
                  <option value="">--</option>
                  <option v-for="h in horasDisponibles" :key="h" :value="h">
                    {{ h.toString().padStart(2, '0') }}
                  </option>
                </select>
              </div>
              
              <div class="separator-modal">:</div>
              
              <div class="input-group-modal">
                <label class="input-label-modal">MINUTOS</label>
                <select v-model="minutoSeleccionado" class="time-select-modal">
                  <option value="">--</option>
                  <option v-for="m in minutosDisponibles" :key="m" :value="m">
                    {{ m.toString().padStart(2, '0') }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Hora seleccionada -->
            <div v-if="horaSeleccionada && minutoSeleccionado" class="selected-time-display-modal">
              <div class="display-content-modal">
                <div class="display-icon-modal">⏰</div>
                <div class="display-text-modal">
                  <div class="display-label-modal">Horario Seleccionado</div>
                  <div class="display-time-modal">
                    {{ horaSeleccionada.toString().padStart(2, '0') }}:{{ minutoSeleccionado.toString().padStart(2, '0') }}
                  </div>
                </div>
              </div>
              <button 
                class="confirm-time-btn-modal" 
                @click="confirmarHora"
                :disabled="!horaValida"
              >
                {{ horaValida ? '✅ Confirmar Horario' : '❌ Horario No Disponible' }}
              </button>
              
              <div v-if="!horaValida && horaSeleccionada && minutoSeleccionado" class="time-error-modal">
                Este horario no está disponible. Por favor selecciona otro.
              </div>
            </div>

            <!-- Horarios rápidos -->
            <div class="quick-times-modal">
              <h4>🕐 Horarios Disponibles</h4>
              <div class="quick-time-grid-modal">
                <div 
                  v-for="hora in horariosDisponibles" 
                  :key="hora"
                  class="quick-time-option-modal"
                  :class="{ 
                    selected: form.hora === hora,
                    disabled: !estaHorarioDisponible(hora)
                  }"
                  @click="seleccionarHoraRapida(hora)"
                >
                  {{ hora }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Swal from 'sweetalert2'

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()
    const turnoId = route.params.id

    const cargando = ref(true)
    const guardando = ref(false)
    const error = ref(null)
    const turnoData = ref({})
    const peluqueros = ref([])
    const servicios = ref([])
    const serviciosFiltradosPorCategoria = ref([])
    const categorias = ref([])
    const turnosOcupados = ref([])
    const mensaje = ref("")
    const horariosDisponibles = ref([])
    const categoriasSeleccionadas = ref([])
    const busquedaServicio = ref("")
    const mostrarModalHora = ref(false)
    const horaSeleccionada = ref("")
    const minutoSeleccionado = ref("")
    const horasDisponibles = Array.from({ length: 13 }, (_, i) => i + 8)
    const minutosDisponibles = [0, 15, 30, 45]

    const form = ref({
      canal: 'PRESENCIAL',
      cliente: null,
      peluquero: "",
      servicios_ids: [],
      tipo_pago: "SENA_50",
      medio_pago: "EFECTIVO",
      hora: "",
      fecha: ""
    })

    // =============================
    //   COMPUTED
    // =============================
    const formularioValido = computed(() => {
    return (
        form.value.peluquero &&
        form.value.servicios_ids.length > 0 &&
        form.value.fecha &&
        form.value.hora &&
        form.value.tipo_pago &&
        form.value.medio_pago
    );
    })

    const textoBoton = computed(() => {
      const monto = form.value.tipo_pago === 'SENA_50' ? calcularSena() : calcularTotal();
      const medio = getMedioPagoTexto();

      if (form.value.tipo_pago === 'SENA_50') {
        return `Actualizar - $${monto} (${medio})`;
      } else {
        return `Actualizar - $${monto} (${medio})`;
      }
    })

    const fechasDisponibles = computed(() => {
      const dates = []
      const today = new Date()

      for (let i = 0; i < 14; i++) {
        const date = new Date(today)
        date.setDate(today.getDate() + i)

        if (date.getDay() !== 0) {
          dates.push(formatDate(date))
          if (dates.length === 7) break
        }
      }
      return dates
    })

    const serviciosFiltrados = computed(() => {
      let filtrados = serviciosFiltradosPorCategoria.value

      if (busquedaServicio.value) {
        const termino = busquedaServicio.value.toLowerCase()
        filtrados = filtrados.filter(s =>
          s.nombre.toLowerCase().includes(termino)
        )
      }

      return filtrados
    })

    const categoriasSeleccionadasNombres = computed(() => {
      return categoriasSeleccionadas.value.map(catId => {
        const categoria = categorias.value.find(c => c.id === catId)
        return categoria ? categoria.nombre : ''
      }).join(', ')
    })

    const horaValida = computed(() => {
      if (!horaSeleccionada.value || !minutoSeleccionado.value) return false

      const horaStr = `${horaSeleccionada.value.toString().padStart(2, '0')}:${minutoSeleccionado.value.toString().padStart(2, '0')}`
      return estaHorarioDisponible(horaStr)
    })

    // =============================
    //    MÉTODOS
    // =============================
    const formatDate = (date) => {
      const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
      const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
      const today = new Date()

      return {
        dayName: days[date.getDay()],
        dayNum: date.getDate(),
        month: months[date.getMonth()],
        fullDate: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`,
        isToday: date.toDateString() === today.toDateString(),
        dateObj: date
      }
    }

    const getMedioPagoTexto = () => {
      switch (form.value.medio_pago) {
        case 'EFECTIVO': return 'Efectivo'
        case 'TARJETA': return 'Tarjeta'
        case 'TRANSFERENCIA': return 'Transferencia'
        default: return 'Efectivo'
      }
    }

    const toggleCategoria = (categoriaId) => {
      const index = categoriasSeleccionadas.value.indexOf(categoriaId)
      if (index === -1) categoriasSeleccionadas.value.push(categoriaId)
      else categoriasSeleccionadas.value.splice(index, 1)

      cargarServiciosPorCategorias()
    }

    const toggleServicio = (servicio) => {
      const index = form.value.servicios_ids.indexOf(servicio.id)
      if (index === -1) form.value.servicios_ids.push(servicio.id)
      else form.value.servicios_ids.splice(index, 1)
    }

    const getServicioNombre = (servicioId) => {
      const servicio = servicios.value.find(s => s.id === servicioId)
      return servicio ? servicio.nombre : ''
    }

    const getServicioPrecio = (servicioId) => {
      const servicio = servicios.value.find(s => s.id === servicioId)
      return servicio ? servicio.precio : 0
    }

    const getCategoriaNombre = (categoria) => {
      if (!categoria) return 'General'

      const cat = categorias.value.find(c => c.id === categoria)
      return cat ? cat.nombre : 'General'
    }

    const calcularTotal = () => {
      return form.value.servicios_ids.reduce((total, servicioId) => {
        return total + parseFloat(getServicioPrecio(servicioId) || 0)
      }, 0)
    }

    const calcularSena = () => calcularTotal() * 0.5

    const seleccionarFecha = (dateInfo) => {
      form.value.fecha = dateInfo.fullDate
      form.value.hora = ""
      generarHorarios()
    }

    const generarHorarios = () => {
      const horarios = []
      for (let h = 8; h < 12; h++)
        for (let m = 0; m < 60; m += 20)
          horarios.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)

      for (let h = 15; h < 20; h++)
        for (let m = 0; m < 60; m += 20)
          horarios.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)

      horariosDisponibles.value = horarios
    }

    const estaHorarioDisponible = (horario) => {
      if (!form.value.fecha || !form.value.peluquero) return false

      const turnoOcupado = turnosOcupados.value.find(t =>
        t.fecha_turno === form.value.fecha &&
        t.hora_turno === horario &&
        t.peluquero_id == form.value.peluquero &&
        t.estado !== 'CANCELADO' &&
        t.id !== parseInt(turnoId)
      )
      return !turnoOcupado
    }

    const seleccionarHora = (hora) => {
      if (estaHorarioDisponible(hora)) {
        form.value.hora = hora
      }
    }

    const abrirModalHora = () => {
      mostrarModalHora.value = true
    }

    const cerrarModalHora = () => {
      mostrarModalHora.value = false
    }

    const cargarDatosTurno = async () => {
      try {
        cargando.value = true

        const [turnosRes, peluquerosRes, serviciosRes, categoriasRes] = await Promise.all([
          fetch('http://localhost:8000/usuarios/api/turnos/'),
          fetch('http://localhost:8000/usuarios/api/peluqueros/'),
          fetch('http://localhost:8000/usuarios/api/servicios/'),
          fetch('http://localhost:8000/usuarios/api/categorias/servicios/')
        ])

        const todosTurnos = await turnosRes.json()
        peluqueros.value = await peluquerosRes.json()
        servicios.value = await serviciosRes.json()
        categorias.value = await categoriasRes.json()
        turnosOcupados.value = todosTurnos

        const turnoEncontrado = todosTurnos.find(t => t.id === parseInt(turnoId))

        turnoData.value = turnoEncontrado

        // 💇 Peluquero — comparar con acentos normalizados
        const normalizar = (str) =>
          str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()

        const peluqueroEncontrado = peluqueros.value.find(p => {
          const turnoFull = normalizar(`${turnoEncontrado.peluquero_nombre} ${turnoEncontrado.peluquero_apellido}`)
          const peluFull = normalizar(`${p.nombre} ${p.apellido}`)
          return turnoFull === peluFull
        })

        form.value.peluquero = peluqueroEncontrado ? peluqueroEncontrado.id.toString() : ""

        // 🧴 Servicios
        form.value.servicios_ids = turnoEncontrado.servicios.map(s => s.id)

        // 🏷 Categorías de los servicios cargados
        const categoriasDelTurno = new Set()
        turnoEncontrado.servicios.forEach(servicio => {
          categoriasDelTurno.add(servicio.categoria_id || servicio.categoria)
        })
        categoriasSeleccionadas.value = Array.from(categoriasDelTurno)

        cargarServiciosPorCategorias()

        form.value.fecha = turnoEncontrado.fecha_turno
        form.value.hora = turnoEncontrado.hora_turno

        form.value.tipo_pago = turnoEncontrado.tipo_pago
        form.value.medio_pago = turnoEncontrado.medio_pago

        form.value.cliente = turnoEncontrado.cliente_id

        if (form.value.fecha) generarHorarios()

      } catch (err) {
        console.error("Error cargando turno:", err)
      } finally {
        cargando.value = false
      }
    }

    const cargarServiciosPorCategorias = () => {
    if (categoriasSeleccionadas.value.length === 0) {
        serviciosFiltradosPorCategoria.value = [...servicios.value];
    } else {
        serviciosFiltradosPorCategoria.value = servicios.value.filter(servicio => {
        const categoriaNombre = servicio.categoria; // El backend manda STRING
        const categoriasSeleccionadasNombres = categoriasSeleccionadas.value.map(
            id => categorias.value.find(c => c.id === id)?.nombre
        );
        return categoriasSeleccionadasNombres.includes(categoriaNombre);
        });
    }
    };


    const modificarTurno = async () => {
      if (!formularioValido.value) {
        mensaje.value = "❌ Completa todos los campos."
        return
      }

      const totalCalculado = calcularTotal()
      const montoSeña = form.value.tipo_pago === 'SENA_50'
        ? totalCalculado * 0.5
        : totalCalculado

      const payload = {
        cliente_id: form.value.cliente,
        peluquero_id: parseInt(form.value.peluquero),
        servicios_ids: form.value.servicios_ids,
        fecha_turno: form.value.fecha,
        hora_turno: form.value.hora,
        tipo_pago: form.value.tipo_pago,
        medio_pago: form.value.medio_pago,
        monto_total: totalCalculado,
        monto_seña: montoSeña
      }

      try {
        guardando.value = true

        const res = await fetch(`http://localhost:8000/usuarios/api/turnos/${turnoId}/modificar/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        })

        const data = await res.json()

        if (res.ok) {
          await Swal.fire({
            icon: 'success',
            title: 'Turno Actualizado',
            text: 'El turno se actualizó correctamente'
          })
          router.push('/turnos')
        } else {
          throw new Error(data.message || "Error al actualizar")
        }

      } catch (err) {
        console.error(err)
      } finally {
        guardando.value = false
      }
    }

    onMounted(() => {
      cargarDatosTurno()
    })
    

    return {
      cargando, guardando, error, turnoData, form,
      peluqueros, servicios, serviciosFiltrados, categorias,
      categoriasSeleccionadas, busquedaServicio,
      mostrarModalHora, horaSeleccionada, minutoSeleccionado,
      horasDisponibles, minutosDisponibles,
      horariosDisponibles, mensaje, formularioValido,
      textoBoton, fechasDisponibles,
      categoriasSeleccionadasNombres, horaValida,
      toggleCategoria, toggleServicio,
      getServicioNombre, getServicioPrecio,
      getCategoriaNombre, calcularTotal, calcularSena,
      seleccionarFecha, estaHorarioDisponible,
      seleccionarHora, seleccionarHoraRapida: seleccionarHora,
      abrirModalHora, cerrarModalHora,
      modificarTurno
    }
  }
}
</script>

<style scoped>
/* ESTILOS EXACTAMENTE IGUALES AL REGISTRAR TURNO */

/* CORRECCIÓN: Campo cliente ligeramente a la derecha */
.cliente-section {
  margin-left: 10px;
}

/* NUEVO ESTILO: Categorías en disposición horizontal */
.categorias-container-horizontal {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.categorias-grid-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 20px;
  overflow-x: auto;
}

.categoria-card-horizontal {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
  min-width: 200px;
  flex-shrink: 0;
}

.categoria-card-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.categoria-card-horizontal.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.categoria-checkbox-horizontal {
  flex-shrink: 0;
}

.checkmark-horizontal {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
  font-size: 12px;
  font-weight: bold;
}

.checkmark-horizontal.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.categoria-content-horizontal {
  flex: 1;
}

.categoria-nombre-horizontal {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 4px;
  font-size: 1em;
}

.categoria-desc-horizontal {
  font-size: 0.8em;
  color: #6c757d;
}

/* Mantener todos los otros estilos existentes del código anterior... */
/* [Aquí van todos los otros estilos que ya tenías] */

.pedido-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 25px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.header-section h2 {
  margin: 0 0 8px 0;
  color: #1a1a1a;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.subtitle {
  color: #6c757d;
  font-size: 1.1em;
  margin: 0;
}

.header-icon {
  color: #007bff;
}

.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #007bff;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15);
}

.input-group {
  margin-bottom: 25px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1a1a1a;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 1.1em;
}

.search-box-improved {
  position: relative;
  margin-bottom: 8px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 2;
}

.input-modern-improved {
  width: 100%;
  padding: 16px 16px 16px 48px;
  border-radius: 12px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 16px;
  transition: all 0.3s ease;
  color: #1a1a1a;
}

.input-modern-improved:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.sugerencias-list-improved {
  position: absolute;
  width: 100%;
  background: white;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  margin-top: 8px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
}

.sugerencia-item-improved {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f1f3f4;
}

.sugerencia-item-improved:hover {
  background: #f8f9fa;
}

.sugerencia-item-improved:last-child {
  border-bottom: none;
}

.cliente-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1em;
  flex-shrink: 0;
}

.cliente-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.cliente-nombre {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 1em;
}

.cliente-dni {
  font-size: 0.85em;
  color: #6c757d;
}

.select-modern-rounded {
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 16px;
  transition: all 0.3s ease;
  color: #1a1a1a;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'><path fill='%23666' d='M2 0L0 2h4zm0 5L0 3h4z'/></svg>");
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 12px;
}

.select-modern-rounded:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.busqueda-servicios {
  margin-bottom: 15px;
}

.input-busqueda {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
}

.input-busqueda:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.servicios-grid-horizontal {
  display: flex;
  overflow-x: auto;
  gap: 12px;
  padding: 10px 5px;
  margin-bottom: 15px;
  scrollbar-width: thin;
  scrollbar-color: #007bff #f1f3f4;
}

.servicios-grid-horizontal::-webkit-scrollbar {
  height: 6px;
}

.servicios-grid-horizontal::-webkit-scrollbar-track {
  background: #f1f3f4;
  border-radius: 3px;
}

.servicios-grid-horizontal::-webkit-scrollbar-thumb {
  background: #007bff;
  border-radius: 3px;
}

.servicio-item-horizontal {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
  min-width: 280px;
  flex-shrink: 0;
}

.servicio-item-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.servicio-item-horizontal.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.servicio-checkbox {
  flex-shrink: 0;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
  font-size: 12px;
  font-weight: bold;
}

.checkmark.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.servicio-info {
  flex: 1;
}

.servicio-nombre {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 6px;
  font-size: 1em;
}

.servicio-details {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.servicio-precio {
  color: #28a745;
  font-weight: 700;
  font-size: 1em;
}

.servicio-duracion {
  color: #6c757d;
  font-size: 0.9em;
}

.servicio-categoria {
  font-size: 0.75em;
  background: #f1f3f4;
  color: #6c757d;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

.no-servicios {
  text-align: center;
  padding: 30px 20px;
  color: #6c757d;
}

.no-servicios span {
  font-size: 2em;
  margin-bottom: 10px;
  display: block;
}

.no-servicios p {
  margin: 0;
  font-size: 1.1em;
}

.no-selection {
  text-align: center;
  padding: 30px 20px;
  color: #6c757d;
  border: 2px dashed #e9ecef;
  border-radius: 12px;
  margin-top: 10px;
}

.no-selection span {
  font-size: 2em;
  margin-bottom: 10px;
  display: block;
}

.no-selection p {
  margin: 0;
  font-size: 1em;
}

.selected-categories {
  color: #007bff;
  font-weight: 500;
  font-size: 0.9em;
  margin-left: 8px;
}

.calendar-container-horizontal {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.calendar-grid-horizontal {
  display: flex;
  overflow-x: auto;
  padding: 20px;
  gap: 12px;
  scrollbar-width: thin;
  scrollbar-color: #007bff #f1f3f4;
}

.calendar-grid-horizontal::-webkit-scrollbar {
  height: 6px;
}

.calendar-grid-horizontal::-webkit-scrollbar-track {
  background: #f1f3f4;
  border-radius: 3px;
}

.calendar-grid-horizontal::-webkit-scrollbar-thumb {
  background: #007bff;
  border-radius: 3px;
}

.date-card-horizontal {
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  padding: 20px 15px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 3px solid transparent;
  min-width: 120px;
  flex-shrink: 0;
  overflow: hidden;
}

.date-card-horizontal:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(79, 172, 254, 0.3);
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.date-card-horizontal.selected {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: #4facfe;
  box-shadow: 0 25px 50px rgba(79, 172, 254, 0.5);
  transform: scale(1.05);
}

.date-card-horizontal.today {
  border-color: #ffd700;
}

.today-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: linear-gradient(135deg, #24948c 0%, #e08618 100%);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
}

.date-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  position: relative;
  z-index: 1;
}

.day-name {
  font-size: 0.8rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: color 0.3s;
}

.date-card-horizontal.selected .day-name {
  color: rgba(255, 255, 255, 0.9);
}

.day-number {
  font-size: 2rem;
  font-weight: 900;
  color: #1e293b;
  line-height: 1;
  transition: color 0.3s;
}

.date-card-horizontal.selected .day-number {
  color: white;
}

.month-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: color 0.3s;
}

.date-card-horizontal.selected .month-name {
  color: rgba(255, 255, 255, 0.85);
}

.shine-effect {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 30%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 70%
  );
  transform: translateX(-100%);
  transition: transform 0.6s;
}

.date-card-horizontal:hover .shine-effect {
  transform: translateX(100%);
}

.time-picker-trigger {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.time-picker-trigger:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.15);
}

.time-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #1a1a1a;
  font-weight: 600;
}

.time-icon {
  font-size: 1.2em;
}

.time-text {
  flex: 1;
  text-align: center;
  font-size: 1.1em;
}

.time-arrow {
  color: #6c757d;
  transition: transform 0.3s ease;
}

.time-picker-trigger:hover .time-arrow {
  transform: rotate(180deg);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-radius: 20px 20px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4em;
  font-weight: 700;
}

.modal-close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 1.8em;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 30px;
}

.time-selector-modal-content {
  text-align: center;
}

.time-inputs-modal {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.input-group-modal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.input-label-modal {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.time-select-modal {
  width: 120px;
  height: 90px;
  font-size: 2.5rem;
  font-weight: 900;
  color: #1e293b;
  background: white;
  border: 3px solid #e1e5e9;
  border-radius: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  appearance: none;
  outline: none;
}

.time-select-modal:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 15px 40px rgba(79, 172, 254, 0.3);
  border-color: #4facfe;
}

.time-select-modal:focus {
  border-color: #4facfe;
  box-shadow: 0 15px 40px rgba(79, 172, 254, 0.4);
}

.separator-modal {
  font-size: 3rem;
  font-weight: 900;
  color: #4facfe;
  margin: 0 15px;
  animation: blink 2s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.selected-time-display-modal {
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 25px;
  animation: slideUp 0.4s ease-out;
}

.display-content-modal {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.display-icon-modal {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(79, 172, 254, 0.3);
  flex-shrink: 0;
  color: white;
  font-weight: bold;
  font-size: 1.2em;
}

.display-text-modal {
  flex: 1;
  text-align: left;
}

.display-label-modal {
  font-size: 1rem;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.display-time-modal {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1e293b;
}

.confirm-time-btn-modal {
  width: 100%;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 18px;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 20px rgba(79, 172, 254, 0.4);
}

.confirm-time-btn-modal:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 15px 40px rgba(79, 172, 254, 0.5);
}

.confirm-time-btn-modal:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.time-error-modal {
  margin-top: 15px;
  padding: 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  text-align: center;
  font-size: 1em;
}

.quick-times-modal {
  margin-top: 25px;
}

.quick-times-modal h4 {
  margin: 0 0 20px 0;
  color: #1a1a1a;
  font-size: 1.2em;
  font-weight: 600;
}

.quick-time-grid-modal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
  gap: 12px;
}

.quick-time-option-modal {
  padding: 15px 10px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  color: #1a1a1a;
  text-align: center;
  font-size: 1em;
}

.quick-time-option-modal:hover:not(.disabled) {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.quick-time-option-modal.selected {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.quick-time-option-modal.disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.pago-container-horizontal {
  background: #fff;
  border-radius: 16px;
  border: 2px solid #f1f3f4;
  padding: 25px;
}

.pago-options-horizontal {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.pago-option-horizontal {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 25px 20px;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
  text-align: center;
}

.pago-option-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.1);
}

.pago-option-horizontal.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.pago-content-horizontal {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.pago-nombre-horizontal {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 1.2em;
}

.pago-monto-horizontal {
  color: #28a745;
  font-weight: 800;
  font-size: 1.4em;
}

.pago-desc-horizontal {
  color: #6c757d;
  font-size: 0.9em;
}

.medio-pago-section-horizontal {
  margin-top: 25px;
  padding-top: 25px;
  border-top: 2px solid #f1f3f4;
}

.medio-pago-options-horizontal {
  display: flex;
  gap: 15px;
}

.medio-pago-btn-horizontal {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 25px 20px;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.medio-pago-btn-horizontal:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.1);
}

.medio-pago-btn-horizontal.active {
  border-color: #007bff;
  background: #e7f3ff;
}

.medio-icon-horizontal {
  font-size: 2.5em;
}

.medio-text-horizontal {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 1.1em;
}

.resumen-pedido {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  border: 2px solid #e9ecef;
}

.resumen-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  color: #1a1a1a;
  font-size: 1em;
}

.resumen-item.total {
  border-top: 2px solid #dee2e6;
  margin-top: 10px;
  padding-top: 12px;
  font-size: 1.2em;
  font-weight: 700;
}

/* Estilos específicos para ModificarTurno */
.cliente-info-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px solid #e9ecef;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.error-state {
  text-align: center;
  padding: 40px;
  color: #dc3545;
}

.error-icon {
  font-size: 3em;
  margin-bottom: 15px;
}

.btn-volver {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 15px;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.btn-cancelar-premium {
  flex: 1;
  background: #6c757d;
  color: white;
  font-size: 1.1em;
  padding: 18px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.btn-cancelar-premium:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

.btn-registrar-premium {
  flex: 2;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  font-size: 1.1em;
  padding: 18px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.btn-registrar-premium:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, #0056b3, #004085);
}

.btn-registrar-premium:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.mensaje-premium {
  margin-top: 20px;
  padding: 15px 20px;
  border-radius: 10px;
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mensaje-premium.error {
  background: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

.mensaje-icon {
  font-size: 1.2em;
}

.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.scale-fade-enter-active {
  transition: all 0.3s ease;
}
.scale-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.scale-fade-enter-from,
.scale-fade-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

.bounce-enter-active {
  animation: bounce-in 0.5s;
}
.bounce-leave-active {
  animation: bounce-in 0.5s reverse;
}
@keyframes bounce-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@media (max-width: 768px) {
  .pedido-container {
    padding: 15px;
  }
  
  .calendar-grid-horizontal {
    padding: 15px;
  }
  
  .servicios-grid-horizontal {
    flex-direction: column;
    overflow-x: visible;
  }
  
  .servicio-item-horizontal {
    min-width: auto;
  }
  
  .categorias-grid-horizontal {
    flex-direction: column;
  }
  
  .categoria-card-horizontal {
    min-width: auto;
  }
  
  .pago-options-horizontal {
    flex-direction: column;
  }
  
  .medio-pago-options-horizontal {
    flex-direction: column;
  }
  
  .quick-time-grid-modal {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .time-inputs-modal {
    flex-direction: column;
    gap: 20px;
  }
  
  .separator-modal {
    margin: 0;
  }
  
  .modal-content {
    margin: 10px;
    max-height: 95vh;
  }
  
  .cliente-section {
    margin-left: 0;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>