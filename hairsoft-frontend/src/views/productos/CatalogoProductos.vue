<template>
  <div class="catalogo-container">
    <div class="catalogo-header">
      <div class="header-content">
        <h1>Nuestros Productos</h1>
        <p class="subtitulo">Descubre nuestra línea premium para el cuidado masculino</p>
      </div>
      <div class="header-estadisticas">
        <div class="estadistica-item">
          <Package :size="20" />
          <span>{{ productosFiltrados.length }} productos</span>
        </div>
      </div>
    </div>

    <!-- FILTROS MEJORADOS -->
    <div class="filtros-container">
      <div class="filtro-busqueda">
        <div class="search-wrapper">
          <Search :size="20" class="search-icon" />
          <input 
            v-model="filtros.busqueda" 
            placeholder="Buscar productos por nombre o descripción..." 
            class="search-input"
          />
          <button v-if="filtros.busqueda" @click="filtros.busqueda = ''" class="clear-search">
            <X :size="18" />
          </button>
        </div>
      </div>

      <div class="filtros-avanzados">
        <div class="filtro-group">
          <label>
            <Tag :size="14" />
            Categoría
          </label>
          <div class="select-wrapper">
            <select v-model="filtros.categoria" class="select-filtro">
              <option value="">Todas las categorías</option>
              <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
                {{ categoria.nombre }}
              </option>
            </select>
            <ChevronDown :size="16" class="select-arrow" />
          </div>
        </div>

        <div class="filtro-group">
          <label>
            <Package :size="14" />
            Marca
          </label>
          <div class="select-wrapper">
            <select v-model="filtros.marca" class="select-filtro">
              <option value="">Todas las marcas</option>
              <option v-for="marca in marcas" :key="marca.id" :value="marca.id">
                {{ marca.nombre }}
              </option>
            </select>
            <ChevronDown :size="16" class="select-arrow" />
          </div>
        </div>

        <div class="filtro-group">
          <label>
            <ArrowUpDown :size="14" />
            Ordenar por
          </label>
          <div class="select-wrapper">
            <select v-model="filtros.orden" class="select-filtro">
              <option value="nombre">📝 Nombre A-Z</option>
              <option value="precio_asc">💰 Precio: Menor a mayor</option>
              <option value="precio_desc">💎 Precio: Mayor a menor</option>
            </select>
            <ChevronDown :size="16" class="select-arrow" />
          </div>
        </div>

        <button 
          @click="limpiarFiltros" 
          class="btn-limpiar-filtros" 
          :class="{ 'has-filters': hayFiltrosActivos }"
          :disabled="!hayFiltrosActivos"
        >
          <Trash2 :size="18" />
          <span>Limpiar</span>
        </button>
      </div>

      <!-- CHIPS DE FILTROS ACTIVOS -->
      <transition name="chips-fade">
        <div v-if="hayFiltrosActivos" class="filtros-chips">
          <span class="chips-label">
            <Filter :size="14" />
            Filtros aplicados:
          </span>
          <div class="chips-container">
            <div v-if="filtros.busqueda" class="filter-chip">
              <Search :size="12" />
              <span>"{{ filtros.busqueda }}"</span>
              <button @click="filtros.busqueda = ''" class="chip-remove">
                <X :size="12" />
              </button>
            </div>
            
            <div v-if="filtros.categoria" class="filter-chip">
              <Tag :size="12" />
              <span>{{ getCategoriaNombreById(filtros.categoria) }}</span>
              <button @click="filtros.categoria = ''" class="chip-remove">
                <X :size="12" />
              </button>
            </div>
            
            <div v-if="filtros.marca" class="filter-chip">
              <Package :size="12" />
              <span>{{ getMarcaNombreById(filtros.marca) }}</span>
              <button @click="filtros.marca = ''" class="chip-remove">
                <X :size="12" />
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <div v-if="productosFiltrados.length > 0" class="productos-grid">
      <div 
        v-for="producto in productosPaginados" 
        :key="producto.id" 
        class="producto-card"
        :class="{ 'sin-stock': producto.stock_actual <= 0 }"
        @click="abrirModalProducto(producto)"
      >
        <div class="producto-img-container">
          <img 
            :src="getImageUrl(producto.imagen)" 
            :alt="producto.nombre"
            class="producto-img"
            @error="$event.target.src = '/placeholder.png'"
          />
          <span v-if="producto.stock_actual > 0 && producto.stock_actual < 5" class="badge-stock-bajo">
            ¡Últimas unidades!
          </span>
          <span v-if="producto.stock_actual <= 0" class="badge-agotado">
            AGOTADO
          </span>
        </div>

        <div class="producto-header">
          <div class="producto-categoria">
            {{ getCategoriaNombre(producto) }}
          </div>
        </div>

        <div class="producto-info">
          <h3 class="producto-nombre">{{ producto.nombre }}</h3>
          
          <div class="producto-marca">
            <Tag :size="12" />
            <span>{{ getMarcaNombre(producto) }}</span>
          </div>
          
          <p class="producto-descripcion">
             {{ producto.descripcion ? (producto.descripcion.substring(0, 60) + '...') : 'Sin descripción' }}
          </p>
        </div>

        <div class="producto-footer">
            <div class="producto-precio">
                <span class="precio-label">Precio</span>
                <span class="precio-actual">${{ Number(producto.precio).toLocaleString() }}</span>
            </div>
            <button class="btn-ver-detalle" @click.stop="abrirModalProducto(producto)">Ver Detalle</button>
        </div>
      </div>
    </div>

    <div v-else class="sin-resultados">
      <PackageSearch :size="64" />
      <h3>No encontramos productos</h3>
      <p>Prueba con otros términos de búsqueda o selecciona diferentes filtros</p>
      <button @click="limpiarFiltros" class="btn-limpiar-todos">
        <Trash2 :size="16" />
        Limpiar todos los filtros
      </button>
    </div>

    <div v-if="totalPaginas > 1" class="paginacion-container">
      <div class="paginacion">
        <div class="paginacion-info">
          <span>Mostrando <strong>{{ productosPaginados.length }}</strong> de <strong>{{ productosFiltrados.length }}</strong> productos</span>
        </div>
        
        <div class="paginacion-controles">
          <button 
            @click="paginaAnterior" 
            :disabled="pagina === 1" 
            class="btn-pagina prev"
            aria-label="Página anterior"
          >
            <ChevronLeft :size="18" />
          </button>
          
          <div class="paginacion-numeros">
            <span 
              v-if="pagina > 3" 
              class="paginacion-puntos"
              @click="cambiarPagina(1)"
            >1</span>
            <span 
              v-if="pagina > 4" 
              class="paginacion-puntos"
            >...</span>
            
            <button 
              v-for="num in getPaginasVisibles" 
              :key="num"
              @click="cambiarPagina(num)"
              :class="['numero-pagina', { active: num === pagina }]"
              :aria-label="`Ir a página ${num}`"
            >
              {{ num }}
            </button>
            
            <span 
              v-if="pagina < totalPaginas - 3" 
              class="paginacion-puntos"
            >...</span>
            <span 
              v-if="pagina < totalPaginas - 2" 
              class="paginacion-puntos"
              @click="cambiarPagina(totalPaginas)"
            >{{ totalPaginas }}</span>
          </div>
          
          <button 
            @click="paginaSiguiente" 
            :disabled="pagina === totalPaginas" 
            class="btn-pagina next"
            aria-label="Página siguiente"
          >
            <ChevronRight :size="18" />
          </button>
        </div>
        
        <div class="paginacion-salto">
          <span>Ir a:</span>
          <input 
            type="number" 
            :min="1" 
            :max="totalPaginas" 
            v-model.number="inputPagina"
            @keyup.enter="irAPaginaEspecifica"
            @blur="irAPaginaEspecifica"
            class="input-salto"
            aria-label="Número de página"
          />
        </div>
      </div>
    </div>

    <Transition name="modal-fade">
      <div v-if="mostrarModal && productoSeleccionado" class="modal-backdrop" @click="cerrarModal">
        <div class="modal-card" @click.stop>
          
          <button class="btn-cerrar-modal" @click="cerrarModal">
            <X :size="24" />
          </button>

          <div class="modal-layout">
            
            <div class="modal-image-col">
              <img 
                :src="getImageUrl(productoSeleccionado.imagen)" 
                :alt="productoSeleccionado.nombre"
                class="modal-img-full"
                @error="$event.target.src = '/placeholder.png'"
              />
              <div class="modal-badges">
                <span class="modal-badge-marca">
                  <Tag :size="14" />
                  {{ getMarcaNombre(productoSeleccionado) }}
                </span>
              </div>
            </div>

            <div class="modal-info-col">
              <div class="modal-scroll-content">
                <div class="modal-header-info">
                  <h2 class="modal-title">{{ productoSeleccionado.nombre }}</h2>
                </div>

                <div class="modal-precio-box">
                  <span class="modal-symbol">$</span>
                  <span class="modal-price">{{ Number(productoSeleccionado.precio).toLocaleString() }}</span>
                </div>

                <div class="modal-stock-status">
                  <span v-if="productoSeleccionado.stock_actual > 5" class="status-ok">
                    <span class="dot ok"></span> Disponible
                  </span>
                  <span v-else-if="productoSeleccionado.stock_actual > 0" class="status-low">
                    <span class="dot low"></span> ¡Últimas unidades!
                  </span>
                  <span v-else class="status-out">
                    <span class="dot out"></span> Agotado
                  </span>
                </div>

                <div class="separator"></div>

                <div class="modal-description-section">
                  <h3>Información del Producto</h3>
                  
                  <div class="modal-desc-text">
                    {{ productoSeleccionado.descripcion || 'Sin descripción detallada.' }}
                  </div>
                </div>

                <div class="modal-features">
                  <div class="modal-feature-item">
                    <div class="feature-icon"></div>
                    <span class="feature-text">Producto original</span>
                  </div>
                  <div class="modal-feature-item">
                    <div class="feature-icon"></div>
                    <span class="feature-text">Calidad garantizada</span>
                  </div>
                </div>
              </div>

              <div class="modal-actions">
                <button class="btn-volver" @click="cerrarModal">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                  </svg>
                  Volver al Catálogo
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/services/api' 
import { 
  Package, PackageSearch, Search, X, 
  ChevronLeft, ChevronRight, Trash2, Tag,
  Filter, ArrowUpDown, ChevronDown
} from 'lucide-vue-next'

const productos = ref([])
const categorias = ref([])
const marcas = ref([])

const filtros = ref({ 
  busqueda: '', 
  categoria: '', 
  marca: '',
  orden: 'nombre'
})

const pagina = ref(1)
const itemsPorPagina = 8
const inputPagina = ref(1)

const mostrarModal = ref(false)
const productoSeleccionado = ref(null)

const abrirModalProducto = (producto) => {
  productoSeleccionado.value = producto
  mostrarModal.value = true
  document.body.style.overflow = 'hidden'
}

const cerrarModal = () => {
  mostrarModal.value = false
  setTimeout(() => { productoSeleccionado.value = null }, 300)
  document.body.style.overflow = ''
}

const cargarProductos = async () => {
  try {
    const res = await api.get('/catalogo/')
    productos.value = res.data
  } catch (err) { console.error(err) }
}

const cargarCategorias = async () => {
  try {
    const res = await api.get('/categorias/productos/')
    categorias.value = res.data
  } catch (err) { console.error(err) }
}

const cargarMarcas = async () => {
  try {
    const res = await api.get('/marcas/')
    marcas.value = res.data
  } catch (err) { console.error(err) }
}

const getImageUrl = (img) => {
  if (!img) return '/placeholder.png'; 
  if (img.startsWith('http')) return img;
  return `http://127.0.0.1:8000${img}`; 
}

const getCategoriaNombre = (producto) => {
  if (producto.categoria_nombre) return producto.categoria_nombre
  if (producto.categoria) {
    const categoria = categorias.value.find(c => c.id === producto.categoria)
    return categoria ? categoria.nombre : 'General'
  }
  return 'General'
}

const getCategoriaNombreById = (id) => {
  const categoria = categorias.value.find(c => c.id == id)
  return categoria ? categoria.nombre : ''
}

const getMarcaNombre = (producto) => {
  if (producto.marca_nombre) return producto.marca_nombre
  if (producto.marca) {
    const marca = marcas.value.find(m => m.id === producto.marca)
    return marca ? marca.nombre : 'Genérico'
  }
  return 'Genérico'
}

const getMarcaNombreById = (id) => {
  const marca = marcas.value.find(m => m.id == id)
  return marca ? marca.nombre : ''
}

onMounted(async () => {
  await cargarCategorias()
  await cargarMarcas()
  await cargarProductos()
})

const productosFiltrados = computed(() => {
  let filtrados = productos.value.filter(p => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || (p.nombre?.toLowerCase().includes(busca) || p.descripcion?.toLowerCase().includes(busca))
    const matchCategoria = !filtros.value.categoria || p.categoria == filtros.value.categoria
    const matchMarca = !filtros.value.marca || p.marca == filtros.value.marca
    return matchBusqueda && matchCategoria && matchMarca
  })

  switch(filtros.value.orden) {
    case 'precio_asc': filtrados.sort((a, b) => Number(a.precio) - Number(b.precio)); break
    case 'precio_desc': filtrados.sort((a, b) => Number(b.precio) - Number(a.precio)); break
    default: filtrados.sort((a, b) => a.nombre?.localeCompare(b.nombre || ''))
  }
  return filtrados
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(productosFiltrados.value.length / itemsPorPagina)))
const productosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return productosFiltrados.value.slice(inicio, inicio + itemsPorPagina)
})

const getPaginasVisibles = computed(() => {
  const total = totalPaginas.value;
  const current = pagina.value;
  const paginas = [];
  
  let start = Math.max(1, current - 2);
  let end = Math.min(total, start + 4);
  
  if (end - start < 4) {
    start = Math.max(1, end - 4);
  }
  
  for (let i = start; i <= end; i++) {
    paginas.push(i);
  }
  
  return paginas;
});

const hayFiltrosActivos = computed(() => filtros.value.busqueda || filtros.value.categoria || filtros.value.marca)
const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }
const cambiarPagina = (num) => { if (num !== '...') pagina.value = num }

const irAPaginaEspecifica = () => {
  if (!inputPagina.value || inputPagina.value < 1) {
    inputPagina.value = 1;
  } else if (inputPagina.value > totalPaginas.value) {
    inputPagina.value = totalPaginas.value;
  }
  
  if (pagina.value !== inputPagina.value) {
    pagina.value = inputPagina.value;
  }
};

const limpiarFiltros = () => { filtros.value = { busqueda: '', categoria: '', marca: '', orden: 'nombre' }; pagina.value = 1 }

watch(pagina, (newVal) => {
  inputPagina.value = newVal;
}, { immediate: true });

watch(filtros, () => {
  pagina.value = 1
  inputPagina.value = 1
}, { deep: true })
</script>

<style scoped>
.catalogo-container { padding: 30px; max-width: 1400px; margin: 0 auto; font-family: 'Segoe UI', sans-serif; }
.catalogo-header { background: var(--bg-secondary); border-radius: 20px; padding: 40px; margin-bottom: 30px; border: 1px solid var(--border-color); position: relative; overflow: hidden; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
.catalogo-header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); }
.header-content h1 { margin: 0; font-size: 2.8rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1px; margin-bottom: 10px; }
.subtitulo { color: var(--text-secondary); font-size: 1.1rem; }
.estadistica-item { display: flex; align-items: center; gap: 10px; background: var(--bg-primary); padding: 12px 20px; border-radius: 12px; border: 1px solid var(--border-color); color: var(--text-primary); font-weight: 700; }
.estadistica-item svg { color: #0ea5e9; }

/* ==================== FILTROS MEJORADOS ==================== */
.filtros-container { 
  background: var(--bg-secondary); 
  border-radius: 20px; 
  padding: 32px; 
  margin-bottom: 30px; 
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.filtro-busqueda { 
  margin-bottom: 28px; 
}

.search-wrapper { 
  position: relative; 
  max-width: 700px; 
}

.search-icon { 
  position: absolute; 
  left: 20px; 
  top: 50%; 
  transform: translateY(-50%); 
  color: #0ea5e9;
  pointer-events: none;
  z-index: 1;
}

.search-input { 
  width: 100%; 
  padding: 18px 56px 18px 56px; 
  background: var(--bg-primary); 
  border: 2px solid var(--border-color); 
  border-radius: 14px; 
  color: var(--text-primary); 
  font-size: 1.05rem; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  box-sizing: border-box;
  font-weight: 500;
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

.search-input:focus { 
  outline: none; 
  border-color: #0ea5e9; 
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.12), 0 8px 16px rgba(14, 165, 233, 0.08); 
  transform: translateY(-1px);
}

.clear-search { 
  position: absolute; 
  right: 16px; 
  top: 50%; 
  transform: translateY(-50%); 
  background: rgba(239, 68, 68, 0.1);
  border: none; 
  color: #ef4444;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-search:hover {
  background: #ef4444;
  color: white;
  transform: translateY(-50%) scale(1.1);
}

.filtros-avanzados { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
  gap: 20px; 
  align-items: end; 
}

.filtro-group { 
  display: flex; 
  flex-direction: column;
  gap: 10px;
}

.filtro-group label { 
  font-weight: 700; 
  color: var(--text-primary);
  font-size: 0.9rem; 
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.filtro-group label svg {
  color: #0ea5e9;
}

.select-wrapper {
  position: relative;
}

.select-filtro { 
  width: 100%;
  padding: 14px 40px 14px 16px; 
  background: var(--bg-primary); 
  border: 2px solid var(--border-color); 
  border-radius: 12px; 
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.select-arrow {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #0ea5e9;
  pointer-events: none;
  transition: transform 0.3s ease;
}

.select-filtro:hover {
  border-color: #0ea5e9;
  background: var(--bg-secondary);
}

.select-filtro:focus { 
  outline: none; 
  border-color: #0ea5e9; 
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12); 
}

.select-filtro:focus + .select-arrow {
  transform: translateY(-50%) rotate(180deg);
}

.btn-limpiar-filtros { 
  background: var(--bg-primary); 
  color: var(--text-secondary); 
  border: 2px solid var(--border-color); 
  padding: 14px 24px; 
  border-radius: 12px; 
  font-weight: 700; 
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  gap: 10px; 
  min-height: 50px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-limpiar-filtros:hover:not(:disabled) { 
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border-color: #ef4444;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(239, 68, 68, 0.25);
}

.btn-limpiar-filtros:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-limpiar-filtros.has-filters {
  animation: pulse-button 2s ease-in-out infinite;
}

@keyframes pulse-button {
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% { 
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}

/* ==================== CHIPS DE FILTROS ==================== */
.filtros-chips {
  margin-top: 24px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.05), rgba(59, 130, 246, 0.05));
  border-radius: 14px;
  border: 2px dashed rgba(14, 165, 233, 0.3);
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.chips-label {
  font-weight: 800;
  color: #0ea5e9;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.chips-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
}

.filter-chip {
  background: white;
  padding: 8px 14px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  border: 2px solid #0ea5e9;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.15);
  animation: chipSlideIn 0.3s ease;
}

@keyframes chipSlideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.filter-chip svg {
  color: #0ea5e9;
  flex-shrink: 0;
}

.chip-remove {
  background: rgba(239, 68, 68, 0.1);
  border: none;
  color: #ef4444;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.chip-remove:hover {
  background: #ef4444;
  color: white;
  transform: scale(1.15);
}

.chips-fade-enter-active, .chips-fade-leave-active {
  transition: all 0.3s ease;
}

.chips-fade-enter-from, .chips-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.productos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; margin-bottom: 40px; }
.producto-card { background: var(--bg-secondary); border-radius: 16px; overflow: hidden; border: 1px solid var(--border-color); transition: all 0.3s ease; display: flex; flex-direction: column; padding: 20px; cursor: pointer; }
.producto-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1); border-color: #0ea5e9; }
.producto-card.sin-stock { opacity: 0.8; }
.producto-img-container { width: 100%; height: 220px; background: white; border-radius: 12px; display: flex; justify-content: center; align-items: center; margin-bottom: 15px; position: relative; overflow: hidden; }
.producto-img { max-width: 90%; max-height: 90%; object-fit: contain; transition: transform 0.3s ease; }
.producto-card:hover .producto-img { transform: scale(1.05); }
.badge-stock-bajo { position: absolute; top: 10px; right: 10px; background: #f59e0b; color: white; padding: 4px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.badge-agotado { position: absolute; top: 10px; right: 10px; background: #ef4444; color: white; padding: 4px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; }
.producto-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.producto-categoria { background: rgba(14, 165, 233, 0.1); color: #0ea5e9; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; }
.producto-info { flex: 1; margin-bottom: 15px; }
.producto-nombre { margin: 0 0 8px 0; font-size: 1.2rem; color: var(--text-primary); font-weight: 800; }
.producto-marca { display: flex; align-items: center; gap: 6px; color: var(--text-tertiary); font-size: 0.85rem; font-weight: 600; margin-bottom: 10px; }
.producto-descripcion { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.4; }
.producto-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 15px; border-top: 1px solid var(--border-color); }
.producto-precio { display: flex; flex-direction: column; }
.precio-label { font-size: 0.7rem; color: var(--text-tertiary); text-transform: uppercase; }
.precio-actual { font-size: 1.4rem; font-weight: 900; color: var(--text-primary); }
.btn-ver-detalle { background: var(--text-primary); color: var(--bg-primary); border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-ver-detalle:hover { background: #0ea5e9; transform: translateY(-2px); }

/* Estilos para la paginación */
.paginacion-container {
  margin-top: 40px;
}

.paginacion {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 24px 32px;
  border: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.paginacion-info {
  color: var(--text-secondary);
  font-size: 0.95rem;
  min-width: 200px;
}

.paginacion-info strong {
  color: var(--text-primary);
  font-weight: 700;
}

.paginacion-controles {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-pagina {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-primary);
}

.btn-pagina:hover:not(:disabled) {
  background: #0ea5e9;
  border-color: #0ea5e9;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.2);
}

.btn-pagina:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
}

.btn-pagina.prev:hover:not(:disabled) {
  transform: translateX(-2px) translateY(-2px);
}

.btn-pagina.next:hover:not(:disabled) {
  transform: translateX(2px) translateY(-2px);
}

.paginacion-numeros {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 12px;
}

.numero-pagina {
  min-width: 44px;
  height: 44px;
  border: 2px solid transparent;
  background: transparent;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.numero-pagina:hover:not(.active) {
  background: var(--bg-primary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.numero-pagina.active {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
  border: none;
}

.paginacion-puntos {
  color: var(--text-tertiary);
  font-weight: 600;
  padding: 0 8px;
  cursor: default;
  user-select: none;
}

.paginacion-puntos:first-child,
.paginacion-puntos:last-child {
  cursor: pointer;
  color: var(--text-secondary);
}

.paginacion-puntos:first-child:hover,
.paginacion-puntos:last-child:hover {
  color: var(--text-primary);
  text-decoration: underline;
}

.paginacion-salto {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  min-width: 160px;
  justify-content: flex-end;
}

.input-salto {
  width: 70px;
  padding: 10px 14px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-weight: 600;
  text-align: center;
  transition: all 0.3s ease;
}

.input-salto:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
}

.input-salto::-webkit-outer-spin-button,
.input-salto::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .filtros-avanzados {
    grid-template-columns: 1fr;
  }
  
  .paginacion {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
    padding: 20px;
  }
  
  .paginacion-info,
  .paginacion-salto {
    text-align: center;
    justify-content: center;
  }
  
  .paginacion-controles {
    justify-content: center;
    order: 2;
  }
  
  .paginacion-numeros {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .paginacion-salto {
    order: 1;
  }
}

.sin-resultados { text-align: center; padding: 60px; background: var(--bg-secondary); border-radius: 16px; }

/* ========== MODAL PREMIUM ========== */
.modal-backdrop {
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100vw; 
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex; 
  justify-content: center; 
  align-items: center;
  z-index: 9999;
  padding: 20px;
  animation: backdropFadeIn 0.3s ease;
}

@keyframes backdropFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  width: 95%;
  max-width: 1200px;
  height: 90vh;
  max-height: 850px;
  border-radius: 32px;
  box-shadow: 
    0 0 0 1px rgba(255, 255, 255, 0.1),
    0 50px 100px -20px rgba(0, 0, 0, 0.5),
    0 30px 60px -30px rgba(14, 165, 233, 0.3);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, 
    #0ea5e9 0%, 
    #06b6d4 25%, 
    #3b82f6 50%, 
    #06b6d4 75%, 
    #0ea5e9 100%);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.btn-cerrar-modal {
  position: absolute; 
  top: 24px; 
  right: 24px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  width: 48px; 
  height: 48px;
  display: flex; 
  align-items: center; 
  justify-content: center;
  cursor: pointer; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  z-index: 10; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #6b7280;
}

.btn-cerrar-modal:hover { 
  transform: scale(1.1) rotate(90deg);
  background: #ef4444;
  border-color: #ef4444;
  color: white;
  box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4);
}

.btn-cerrar-modal:active {
  transform: scale(0.95) rotate(90deg);
}

.modal-layout { 
  display: flex; 
  height: 100%; 
}

/* ========== COLUMNA DE IMAGEN ========== */
.modal-image-col {
  width: 48%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e0f2fe 100%);
  position: relative;
  display: flex; 
  justify-content: center; 
  align-items: center;
  padding: 60px 50px;
  overflow: hidden;
}

.modal-image-col::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: 
    radial-gradient(circle at 30% 40%, rgba(14, 165, 233, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, rgba(59, 130, 246, 0.06) 0%, transparent 50%);
}

.modal-img-full {
  max-width: 90%; 
  max-height: 90%;
  object-fit: contain;
  filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.12));
  position: relative;
  z-index: 2;
}

.modal-badges {
  position: absolute; 
  top: 30px; 
  left: 30px;
  display: flex; 
  flex-direction: column;
  gap: 12px;
  z-index: 3;
}

.modal-badge-cat, 
.modal-badge-marca {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 10px 18px; 
  border-radius: 24px;
  font-size: 0.85rem; 
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.modal-badge-cat {
  color: #0ea5e9;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(14, 165, 233, 0.05));
}

.modal-badge-marca {
  color: #8b5cf6;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
}

.modal-badge-cat:hover,
.modal-badge-marca:hover {
  transform: translateX(5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

/* ========== COLUMNA DE INFORMACIÓN ========== */
.modal-info-col {
  width: 52%;
  display: flex;
  flex-direction: column;
  background: white;
  position: relative;
}

.modal-info-col::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 1px;
  background: linear-gradient(to bottom, transparent, #e5e7eb 20%, #e5e7eb 80%, transparent);
}

/* Contenedor scrolleable */
.modal-scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 60px 50px 30px;
  scroll-behavior: smooth;
}

.modal-scroll-content::-webkit-scrollbar {
  width: 6px;
}

.modal-scroll-content::-webkit-scrollbar-track {
  background: transparent;
}

.modal-scroll-content::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #cbd5e1, #94a3b8);
  border-radius: 10px;
}

.modal-scroll-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #94a3b8, #64748b);
}

.modal-header-info { 
  margin-bottom: 24px;
  position: relative;
}

.modal-title { 
  font-size: 2.75rem; 
  font-weight: 900; 
  margin: 0 0 12px 0; 
  color: #0f172a;
  line-height: 1.1;
  letter-spacing: -1.5px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.modal-precio-box { 
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 28px 32px;
  border-radius: 20px;
  margin-bottom: 24px;
  border: 2px solid rgba(14, 165, 233, 0.15);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.08);
}

.modal-precio-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgba(14, 165, 233, 0.05) 0%, 
    rgba(6, 182, 212, 0.03) 100%);
  pointer-events: none;
}

.modal-symbol { 
  font-size: 1.8rem; 
  font-weight: 700;
  color: #0284c7;
  vertical-align: top;
  margin-right: 4px;
}

.modal-price { 
  font-size: 3.5rem; 
  font-weight: 900;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -2px;
  line-height: 1;
}

.modal-stock-status { 
  margin-bottom: 32px;
  display: inline-flex;
  align-items: center;
}

.modal-stock-status span {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-radius: 24px;
  font-weight: 700;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.status-ok { 
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
  color: #059669;
  border: 2px solid rgba(16, 185, 129, 0.2);
}

.status-low { 
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05));
  color: #d97706;
  border: 2px solid rgba(245, 158, 11, 0.2);
}

.status-out { 
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
  color: #dc2626;
  border: 2px solid rgba(239, 68, 68, 0.2);
}

.dot { 
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  position: relative;
}

.dot.ok { 
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.dot.low { 
  background: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
  animation: pulse-dot-warning 1.5s ease-in-out infinite;
}

.dot.out { 
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

@keyframes pulse-dot-warning {
  0%, 100% { 
    transform: scale(1);
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
  }
  50% { 
    transform: scale(1.15);
    box-shadow: 0 0 0 6px rgba(245, 158, 11, 0.1);
  }
}

.separator { 
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    #e5e7eb 20%, 
    #cbd5e1 50%, 
    #e5e7eb 80%, 
    transparent 100%);
  margin: 32px 0;
  width: 100%;
  border: none;
}

.modal-description-section { 
  margin-bottom: 28px;
}

.modal-description-section h3 { 
  font-size: 1.25rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-desc-text { 
  font-size: 1.05rem;
  color: #475569;
  line-height: 1.8;
  white-space: pre-line;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
}

/* Features adicionales */
.modal-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 24px;
}

.modal-feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-radius: 12px;
  border: 1px solid rgba(34, 197, 94, 0.2);
  transition: all 0.3s ease;
}

.modal-feature-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
}

.feature-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(34, 197, 94, 0.3);
}

.feature-icon::after {
  content: '✓';
  color: white;
  font-size: 1.1rem;
  font-weight: 900;
}

.feature-text {
  color: #166534;
  font-weight: 600;
  font-size: 0.95rem;
}

.modal-actions { 
  padding: 28px 50px;
  border-top: 2px solid #f1f5f9;
  background: linear-gradient(to bottom, white 0%, #f9fafb 100%);
  display: flex;
  gap: 12px;
}

.btn-volver {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 18px 32px;
  background: white;
  border: 3px solid #e5e7eb;
  color: #374151;
  border-radius: 16px;
  font-weight: 800;
  font-size: 1.1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.btn-volver::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.btn-volver:hover::before {
  left: 100%;
}

.btn-volver:hover { 
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  border-color: #1f2937;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 12px 24px rgba(31, 41, 55, 0.3);
}

.btn-volver:active {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(31, 41, 55, 0.3);
}

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .modal-card { animation: modal-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.modal-fade-leave-active .modal-card { animation: modal-pop 0.3s reverse ease-in; }

@keyframes modal-pop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.btn-limpiar-todos {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-limpiar-todos:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4);
}

@media (max-width: 900px) {
  .modal-layout { flex-direction: column; }
  .modal-image-col, .modal-info-col { width: 100%; }
  .modal-image-col { height: 40%; padding: 30px 20px; }
  .modal-info-col { height: 60%; }
  .modal-scroll-content { padding: 30px 25px; }
  .modal-actions { padding: 20px 25px; }
  .modal-card { height: 90vh; }
  .modal-title { font-size: 2rem; }
  .modal-price { font-size: 2.5rem; }
  .modal-features { grid-template-columns: 1fr; }
}
</style>