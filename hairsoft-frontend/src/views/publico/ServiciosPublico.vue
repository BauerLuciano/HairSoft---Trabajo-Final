<template>
  <div class="catalogo-container">
    <!-- Header del catálogo -->
    <div class="catalogo-header">
      <div class="header-content">
        <h1>Nuestros Servicios ✂️</h1>
        <p class="subtitulo">Descubre todos nuestros servicios profesionales para el cuidado masculino</p>
      </div>
      <div class="header-estadisticas">
        <div class="estadistica-item">
          <Scissors :size="20" />
          <span>{{ serviciosFiltrados.length }} servicios</span>
        </div>
      </div>
    </div>

    <!-- Filtros mejorados -->
    <div class="filtros-container">
      <div class="filtro-busqueda">
        <div class="search-wrapper">
          <Search :size="18" class="search-icon" />
          <input 
            v-model="filtros.busqueda" 
            placeholder="Buscar servicios por nombre o descripción..." 
            class="search-input"
          />
          <button v-if="filtros.busqueda" @click="filtros.busqueda = ''" class="clear-search">
            <X :size="14" />
          </button>
        </div>
      </div>

      <div class="filtros-avanzados">
        <div class="filtro-group">
          <label>Categoría</label>
          <select v-model="filtros.categoria" class="select-filtro">
            <option value="">Todas las categorías</option>
            <option v-for="categoria in categoriasUnicas" :key="categoria" :value="categoria">
              {{ categoria }}
            </option>
          </select>
        </div>

        <div class="filtro-group">
          <label>Ordenar por</label>
          <select v-model="filtros.orden" class="select-filtro">
            <option value="nombre">Nombre A-Z</option>
            <option value="precio_asc">Precio: Menor a mayor</option>
            <option value="precio_desc">Precio: Mayor a menor</option>
            <option value="duracion_asc">Duración: Corto a largo</option>
            <option value="duracion_desc">Duración: Largo a corto</option>
          </select>
        </div>

        <button @click="limpiarFiltros" class="btn-limpiar-filtros" :disabled="!hayFiltrosActivos">
          <Trash2 :size="16" />
          Limpiar filtros
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="loading-state">
      <div class="spinner-container">
        <div class="spinner"></div>
        <p>Cargando servicios...</p>
      </div>
    </div>

    <!-- Grid de servicios -->
    <div v-else-if="serviciosFiltrados.length > 0" class="servicios-grid">
      <div 
        v-for="servicio in serviciosPaginados" 
        :key="servicio.id" 
        class="servicio-card"
      >
        <!-- Badge destacado -->
        <div v-if="servicio.destacado" class="badge badge-destacado">
          <Star :size="12" />
          Destacado
        </div>

        <!-- Encabezado del servicio -->
        <div class="servicio-header">
          <div class="servicio-codigo">
            #{{ servicio.id.toString().padStart(4, '0') }}
          </div>
          <div class="servicio-categoria">
            {{ servicio.categoria || 'General' }}
          </div>
        </div>

        <!-- Información principal -->
        <div class="servicio-info">
          <h3 class="servicio-nombre">{{ servicio.nombre }}</h3>


          <div class="servicio-detalles">
            <div class="detalle-item">
              <Clock :size="14" />
              <span>{{ servicio.duracion || 30 }} minutos</span>
            </div>
            <div v-if="servicio.productos_necesarios?.length > 0" class="detalle-item">
              <Package :size="14" />
              <span>{{ servicio.productos_necesarios.length }} productos</span>
            </div>
          </div>
        </div>

        <!-- Precio y acción -->
        <div class="servicio-footer">
          <div class="servicio-precio">
            <span class="precio-actual">${{ formatPrice(servicio.precio) }}</span>
            <span class="precio-unitario">por servicio</span>
          </div>

        </div>
      </div>
    </div>

    <!-- Sin resultados -->
    <div v-else-if="!cargando" class="sin-resultados">
      <Scissors :size="64" />
      <h3>No encontramos servicios</h3>
      <p>Prueba con otros términos de búsqueda o selecciona diferentes filtros</p>
      <button @click="limpiarFiltros" class="btn-limpiar-todos">
        <Trash2 :size="16" />
        Limpiar todos los filtros
      </button>
    </div>

    <!-- Paginación -->
    <div v-if="!cargando && totalPaginas > 1" class="paginacion">
      <div class="paginacion-info">
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <span class="separador">•</span>
        <span>{{ serviciosPaginados.length }} de {{ serviciosFiltrados.length }} servicios</span>
      </div>

      <div class="paginacion-controles">
        <button 
          @click="paginaAnterior" 
          :disabled="pagina === 1" 
          class="btn-pagina prev"
        >
          <ChevronLeft :size="16" />
        </button>
        
        <div class="paginacion-numeros">
          <button
            v-for="num in paginasVisibles"
            :key="num"
            :class="{ active: num === pagina, dots: num === '...' }"
            @click="num !== '...' && cambiarPagina(num)"
            :disabled="num === '...'"
          >
            {{ num }}
          </button>
        </div>
        
        <button 
          @click="paginaSiguiente" 
          :disabled="pagina === totalPaginas" 
          class="btn-pagina next"
        >
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- Filtros activos -->
    <div v-if="!cargando && hayFiltrosActivos && serviciosFiltrados.length > 0" class="filtros-activos-bar">
      <div class="filtros-activos-content">
        <span class="filtros-activos-label">Filtros aplicados:</span>
        
        <div class="filtros-activos-chips">
          <span v-if="filtros.busqueda" class="filtro-chip activo">
            Búsqueda: "{{ filtros.busqueda }}"
            <button @click="filtros.busqueda = ''" class="chip-remove">
              <X :size="10" />
            </button>
          </span>
          
          <span v-if="filtros.categoria" class="filtro-chip activo">
            Categoría: {{ filtros.categoria }}
            <button @click="filtros.categoria = ''" class="chip-remove">
              <X :size="10" />
            </button>
          </span>
        </div>
        
        <button @click="limpiarFiltros" class="btn-limpiar-todos-chips">
          <Trash2 :size="14" />
          Limpiar todo
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { 
  Scissors, Package, Clock, Search, X, 
  ChevronLeft, ChevronRight, Trash2, Star
} from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000/usuarios/api'

const servicios = ref([])
const cargando = ref(true)

const filtros = ref({ 
  busqueda: '', 
  categoria: '', 
  orden: 'nombre'
})

const pagina = ref(1)
const itemsPorPagina = 8

const cargarServicios = async () => {
  try {
    const response = await axios.get(`${API_BASE}/servicios/`)
    servicios.value = response.data
      .filter(s => s.estado === 'ACTIVO' || !s.estado) // Solo servicios activos o sin estado definido
    
    console.log('Servicios cargados:', servicios.value)
  } catch (error) {
    console.error('Error cargando servicios:', error)
  } finally {
    cargando.value = false
  }
}

const formatPrice = (value) => {
  const num = Number(value)
  return isNaN(num) ? '0.00' : num.toFixed(2)
}


onMounted(() => {
  cargarServicios()
})

// Computed: categorías únicas de los servicios
const categoriasUnicas = computed(() => {
  const categorias = servicios.value
    .map(s => s.categoria)
    .filter((cat, index, self) => 
      cat && cat.trim() && self.indexOf(cat) === index
    )
    .sort()
  return categorias
})

// Computed: servicios filtrados
const serviciosFiltrados = computed(() => {
  let filtrados = servicios.value.filter(s => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      (s.nombre?.toLowerCase().includes(busca) || 
       s.descripcion?.toLowerCase().includes(busca))
    
    const matchCategoria = !filtros.value.categoria || s.categoria === filtros.value.categoria
    
    return matchBusqueda && matchCategoria
  })

  // Ordenar
  switch(filtros.value.orden) {
    case 'precio_asc':
      filtrados.sort((a, b) => (a.precio || 0) - (b.precio || 0))
      break
    case 'precio_desc':
      filtrados.sort((a, b) => (b.precio || 0) - (a.precio || 0))
      break
    case 'duracion_asc':
      filtrados.sort((a, b) => (a.duracion || 0) - (b.duracion || 0))
      break
    case 'duracion_desc':
      filtrados.sort((a, b) => (b.duracion || 0) - (a.duracion || 0))
      break
    default:
      filtrados.sort((a, b) => a.nombre?.localeCompare(b.nombre || ''))
  }

  return filtrados
})

// Computed: paginación
const totalPaginas = computed(() => 
  Math.max(1, Math.ceil(serviciosFiltrados.value.length / itemsPorPagina))
)

const serviciosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return serviciosFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

const paginasVisibles = computed(() => {
  const total = totalPaginas.value
  const current = pagina.value
  const pages = []
  
  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
      pages.push('...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...')
      for (let i = total - 3; i <= total; i++) pages.push(i)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }
  
  return pages
})

const hayFiltrosActivos = computed(() => {
  return filtros.value.busqueda || filtros.value.categoria
})

// Métodos
const paginaAnterior = () => { 
  if (pagina.value > 1) pagina.value-- 
}

const paginaSiguiente = () => { 
  if (pagina.value < totalPaginas.value) pagina.value++ 
}

const cambiarPagina = (num) => {
  if (num !== '...') pagina.value = num
}

const limpiarFiltros = () => { 
  filtros.value = { busqueda: '', categoria: '', orden: 'nombre' }
  pagina.value = 1 
}

// Watchers
watch(filtros, () => { 
  pagina.value = 1 
}, { deep: true })
</script>

<style scoped>
/* ========================================
   ✂️ CATÁLOGO DE SERVICIOS - MISMO ESTILO
   ======================================== */

.catalogo-container {
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

/* HEADER */
.catalogo-header {
  background: var(--bg-secondary);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.catalogo-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
}

.header-content {
  flex: 1;
  min-width: 300px;
}

.header-content h1 {
  margin: 0;
  font-size: 2.8rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.subtitulo {
  color: var(--text-secondary);
  font-size: 1.1rem;
  max-width: 600px;
  line-height: 1.5;
}

.estadistica-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-primary);
  padding: 12px 20px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-weight: 700;
  white-space: nowrap;
}

.estadistica-item svg {
  color: #0ea5e9;
}

/* FILTROS MEJORADOS */
.filtros-container {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
}

.filtro-busqueda {
  margin-bottom: 25px;
}

.search-wrapper {
  position: relative;
  max-width: 600px;
}

.search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 16px 20px 16px 50px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.15);
}

.clear-search {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-search:hover {
  background: var(--hover-bg);
  color: var(--error-color);
}

.filtros-avanzados {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  align-items: end;
}

.filtro-group {
  display: flex;
  flex-direction: column;
}

.filtro-group label {
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.select-filtro {
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.select-filtro:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
}

.btn-limpiar-filtros {
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 2px solid var(--border-color);
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  height: 46px;
}

.btn-limpiar-filtros:hover:not(:disabled) {
  background: var(--hover-bg);
  border-color: var(--error-color);
  color: var(--error-color);
  transform: translateY(-2px);
}

.btn-limpiar-filtros:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* LOADING STATE */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: var(--bg-secondary);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.spinner-container {
  text-align: center;
  color: var(--text-secondary);
}

.spinner {
  border: 3px solid rgba(255,255,255,0.1);
  border-radius: 50%;
  border-top: 3px solid #0ea5e9;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* GRID DE SERVICIOS (8 por página) */
.servicios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.servicio-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 24px;
}

.servicio-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  border-color: #0ea5e9;
}

/* BADGES */
.badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 5px;
  z-index: 2;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.badge-destacado {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.8; }
  100% { opacity: 1; }
}

/* HEADER DEL SERVICIO */
.servicio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.servicio-codigo {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.servicio-categoria {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.75rem;
  font-weight: 700;
}

/* INFO DEL SERVICIO */
.servicio-info {
  flex: 1;
  margin-bottom: 20px;
}

.servicio-nombre {
  margin: 0 0 12px 0;
  font-size: 1.3rem;
  color: var(--text-primary);
  font-weight: 800;
  line-height: 1.3;
}

.servicio-descripcion {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.servicio-detalles {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.detalle-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.detalle-item svg {
  color: var(--text-tertiary);
  opacity: 0.7;
}

/* FOOTER DEL SERVICIO */
.servicio-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.servicio-precio {
  display: flex;
  flex-direction: column;
}

.precio-actual {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.precio-unitario {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-weight: 500;
}

/* SIN RESULTADOS */
.sin-resultados {
  text-align: center;
  padding: 80px 20px;
  background: var(--bg-secondary);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  margin: 40px 0;
}

.sin-resultados svg {
  color: var(--text-tertiary);
  margin-bottom: 25px;
  opacity: 0.5;
}

.sin-resultados h3 {
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: 1.8rem;
  font-weight: 800;
}

.sin-resultados p {
  color: var(--text-secondary);
  margin-bottom: 30px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  font-size: 1.1rem;
  line-height: 1.5;
}

.btn-limpiar-todos {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-limpiar-todos:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  border-color: var(--error-color);
  color: var(--error-color);
}

/* PAGINACIÓN */
.paginacion {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  margin: 40px 0;
  flex-wrap: wrap;
  gap: 20px;
}

.paginacion-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.95rem;
}

.separador {
  color: var(--border-color);
  font-size: 1.2rem;
}

.paginacion-controles {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-pagina {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-pagina:hover:not(:disabled) {
  background: var(--hover-bg);
  border-color: #0ea5e9;
  color: #0ea5e9;
  transform: translateY(-2px);
}

.btn-pagina:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.paginacion-numeros {
  display: flex;
  gap: 6px;
}

.paginacion-numeros button {
  min-width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.paginacion-numeros button:hover:not(:disabled) {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.paginacion-numeros button.active {
  background: #0ea5e9;
  color: white;
  border-color: #0ea5e9;
}

.paginacion-numeros button.dots {
  background: none;
  border: none;
  cursor: default;
  color: var(--text-tertiary);
  min-width: 30px;
}

.paginacion-numeros button.dots:hover {
  background: none;
}

/* FILTROS ACTIVOS BAR */
.filtros-activos-bar {
  background: rgba(14, 165, 233, 0.05);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 16px;
  padding: 20px;
  margin-top: 20px;
}

.filtros-activos-content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.filtros-activos-label {
  color: #0ea5e9;
  font-weight: 700;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.filtros-activos-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  flex: 1;
}

.filtro-chip.activo {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(14, 165, 233, 0.3);
}

.chip-remove {
  background: none;
  border: none;
  color: #0ea5e9;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: all 0.2s;
}

.chip-remove:hover {
  opacity: 1;
  background: rgba(14, 165, 233, 0.2);
}

.btn-limpiar-todos-chips {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-limpiar-todos-chips:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-2px);
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .servicios-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .catalogo-container {
    padding: 20px 15px;
  }
  
  .catalogo-header {
    padding: 30px 25px;
    flex-direction: column;
    text-align: center;
    gap: 25px;
  }
  
  .header-content {
    min-width: auto;
  }
  
  .header-content h1 {
    font-size: 2.2rem;
  }
  
  .filtros-container {
    padding: 25px;
  }
  
  .filtros-avanzados {
    grid-template-columns: 1fr;
  }
  
  .servicios-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
  
  .paginacion {
    flex-direction: column;
    text-align: center;
    gap: 25px;
  }
  
  .paginacion-info {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .servicios-grid {
    grid-template-columns: 1fr;
  }
  
  .servicio-card {
    padding: 20px;
  }
  
  .header-content h1 {
    font-size: 1.8rem;
  }
  
  .subtitulo {
    font-size: 1rem;
  }
  
  .filtros-activos-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filtros-activos-chips {
    width: 100%;
  }
  
  .precio-actual {
    font-size: 1.5rem;
  }
}
</style>