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

    <div class="filtros-container">
      <div class="filtro-busqueda">
        <div class="search-wrapper">
          <Search :size="18" class="search-icon" />
          <input 
            v-model="filtros.busqueda" 
            placeholder="Buscar productos por nombre o descripción..." 
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
            <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
              {{ categoria.nombre }}
            </option>
          </select>
        </div>

        <div class="filtro-group">
          <label>Marca</label>
          <select v-model="filtros.marca" class="select-filtro">
            <option value="">Todas las marcas</option>
            <option v-for="marca in marcas" :key="marca.id" :value="marca.id">
              {{ marca.nombre }}
            </option>
          </select>
        </div>

        <div class="filtro-group">
          <label>Ordenar por</label>
          <select v-model="filtros.orden" class="select-filtro">
            <option value="nombre">Nombre A-Z</option>
            <option value="precio_asc">Precio: Menor a mayor</option>
            <option value="precio_desc">Precio: Mayor a menor</option>
          </select>
        </div>

        <button @click="limpiarFiltros" class="btn-limpiar-filtros" :disabled="!hayFiltrosActivos">
          <Trash2 :size="16" />
          Limpiar filtros
        </button>
      </div>
    </div>

    <div v-if="productosFiltrados.length > 0" class="productos-grid">
      <div 
        v-for="producto in productosPaginados" 
        :key="producto.id" 
        class="producto-card"
        :class="{ 'sin-stock': producto.stock_actual <= 0 }"
      >
        <div class="producto-img-container">
          <img 
            :src="producto.imagen || '/placeholder.png'" 
            :alt="producto.nombre"
            class="producto-img"
            @error="$event.target.src = 'https://via.placeholder.com/300x300?text=Sin+Imagen'"
          />
          <span v-if="producto.stock_actual > 0 && producto.stock_actual < 5" class="badge-stock-bajo">
            ¡Últimos {{ producto.stock_actual }}!
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
             {{ producto.descripcion ? (producto.descripcion.substring(0, 60) + '...') : '' }}
          </p>
        </div>

        <div class="producto-footer">
            <div class="producto-precio">
                <span class="precio-label">Precio</span>
                <span class="precio-actual">${{ Number(producto.precio).toLocaleString() }}</span>
            </div>
            <button class="btn-ver-detalle">Ver Detalle</button>
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

    <div v-if="totalPaginas > 1" class="paginacion">
      <div class="paginacion-info">
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <span class="separador">•</span>
        <span>{{ productosPaginados.length }} de {{ productosFiltrados.length }} productos</span>
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

    <div v-if="hayFiltrosActivos && productosFiltrados.length > 0" class="filtros-activos-bar">
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
            Categoría: {{ getCategoriaNombreById(filtros.categoria) }}
            <button @click="filtros.categoria = ''" class="chip-remove">
              <X :size="10" />
            </button>
          </span>
          
          <span v-if="filtros.marca" class="filtro-chip activo">
            Marca: {{ getMarcaNombreById(filtros.marca) }}
            <button @click="filtros.marca = ''" class="chip-remove">
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
import api from '@/services/api' // Tu instancia de Axios configurada
import { 
  Package, PackageSearch, Search, X, AlertTriangle, 
  ChevronLeft, ChevronRight, Trash2, XCircle, Tag
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

// --- CARGA DE DATOS ---
const cargarProductos = async () => {
  try {
    // ✅ CORREGIDO: Usamos solo la parte final de la URL
    // Axios agrega '/usuarios/api' automáticamente
    const res = await api.get('/catalogo/')
    productos.value = res.data
  } catch (err) {
    console.error('❌ Error al cargar el catálogo:', err)
  }
}

const cargarCategorias = async () => {
  try {
    // ✅ CORREGIDO
    const res = await api.get('/categorias/productos/')
    categorias.value = res.data
  } catch (err) { console.error('Error categorias', err) }
}

const cargarMarcas = async () => {
  try {
    // ✅ CORREGIDO
    const res = await api.get('/marcas/')
    marcas.value = res.data
  } catch (err) { console.error('Error marcas', err) }
}

// --- HELPERS ---
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

// --- CICLO DE VIDA ---
onMounted(async () => {
  await cargarCategorias()
  await cargarMarcas()
  await cargarProductos()
})

// --- LÓGICA DE FILTRADO Y ORDENAMIENTO ---
const productosFiltrados = computed(() => {
  let filtrados = productos.value.filter(p => {
    const busca = filtros.value.busqueda.toLowerCase()
    
    // Búsqueda por nombre o descripción
    const matchBusqueda = !busca || 
      (p.nombre?.toLowerCase().includes(busca) || 
       p.descripcion?.toLowerCase().includes(busca))
    
    // Filtros exactos
    const matchCategoria = !filtros.value.categoria || p.categoria == filtros.value.categoria
    const matchMarca = !filtros.value.marca || p.marca == filtros.value.marca
    
    return matchBusqueda && matchCategoria && matchMarca
  })

  // Ordenar
  switch(filtros.value.orden) {
    case 'precio_asc':
      // ✅ CORREGIDO: Usamos 'precio' que es el campo de tu modelo
      filtrados.sort((a, b) => Number(a.precio) - Number(b.precio))
      break
    case 'precio_desc':
      filtrados.sort((a, b) => Number(b.precio) - Number(a.precio))
      break
    default: // Nombre A-Z
      filtrados.sort((a, b) => a.nombre?.localeCompare(b.nombre || ''))
  }

  return filtrados
})

// --- PAGINACIÓN ---
const totalPaginas = computed(() => 
  Math.max(1, Math.ceil(productosFiltrados.value.length / itemsPorPagina))
)

const productosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  return productosFiltrados.value.slice(inicio, inicio + itemsPorPagina)
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
  return filtros.value.busqueda || filtros.value.categoria || filtros.value.marca
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }
const cambiarPagina = (num) => { if (num !== '...') pagina.value = num }

const limpiarFiltros = () => { 
  filtros.value = { busqueda: '', categoria: '', marca: '', orden: 'nombre' }
  pagina.value = 1 
}

watch(filtros, () => { pagina.value = 1 }, { deep: true })
</script>

<style scoped>
/* ========================================
   🏪 CATÁLOGO DE PRODUCTOS - HAIRSOFT
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
}

.estadistica-item svg { color: #0ea5e9; }

/* FILTROS */
.filtros-container {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid var(--border-color);
}

.filtro-busqueda { margin-bottom: 25px; }

.search-wrapper { position: relative; max-width: 600px; }

.search-icon {
  position: absolute; left: 18px; top: 50%;
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
  position: absolute; right: 16px; top: 50%;
  transform: translateY(-50%);
  background: none; border: none;
  color: var(--text-tertiary);
  cursor: pointer;
}

.filtros-avanzados {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  align-items: end;
}

.filtro-group { display: flex; flex-direction: column; }

.filtro-group label {
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
}

.select-filtro {
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  width: 100%;
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
  height: 46px;
  transition: all 0.3s ease;
}

.btn-limpiar-filtros:hover:not(:disabled) {
  background: var(--hover-bg);
  border-color: var(--error-color);
  color: var(--error-color);
}

/* GRID DE PRODUCTOS */
.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.producto-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.producto-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  border-color: #0ea5e9;
}

.producto-card.sin-stock { opacity: 0.8; }

/* IMAGEN DEL PRODUCTO */
.producto-img-container {
  width: 100%;
  height: 220px;
  background: white;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  position: relative;
  overflow: hidden;
}

.producto-img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.producto-card:hover .producto-img { transform: scale(1.05); }

.badge-stock-bajo {
  position: absolute; top: 10px; right: 10px;
  background: #f59e0b; color: white;
  padding: 4px 8px; border-radius: 20px;
  font-size: 0.7rem; font-weight: 800;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.badge-agotado {
  position: absolute; top: 10px; right: 10px;
  background: #ef4444; color: white;
  padding: 4px 8px; border-radius: 20px;
  font-size: 0.7rem; font-weight: 800;
}

/* INFO PRODUCTO */
.producto-header {
  display: flex; justify-content: space-between;
  margin-bottom: 10px;
}

.producto-categoria {
  background: rgba(14, 165, 233, 0.1);
  color: #0ea5e9;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.producto-info { flex: 1; margin-bottom: 15px; }

.producto-nombre {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  color: var(--text-primary);
  font-weight: 800;
}

.producto-marca {
  display: flex; align-items: center; gap: 6px;
  color: var(--text-tertiary);
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.producto-descripcion {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

/* FOOTER CARD */
.producto-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
}

.producto-precio { display: flex; flex-direction: column; }

.precio-label { font-size: 0.7rem; color: var(--text-tertiary); text-transform: uppercase; }
.precio-actual { font-size: 1.4rem; font-weight: 900; color: var(--text-primary); }

.btn-ver-detalle {
  background: var(--text-primary);
  color: var(--bg-primary);
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-ver-detalle:hover {
  background: #0ea5e9;
  transform: translateY(-2px);
}

/* PAGINACIÓN & EXTRAS */
.paginacion {
  display: flex; justify-content: space-between; align-items: center;
  padding: 25px; background: var(--bg-secondary);
  border-radius: 16px; border: 1px solid var(--border-color);
  margin-top: 20px;
}

.paginacion-numeros button {
  min-width: 40px; height: 40px; border-radius: 8px;
  background: var(--bg-primary); border: 1px solid var(--border-color);
  cursor: pointer; font-weight: 600;
}

.paginacion-numeros button.active {
  background: #0ea5e9; color: white; border-color: #0ea5e9;
}

.btn-pagina {
  background: var(--bg-primary); border: 1px solid var(--border-color);
  width: 40px; height: 40px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}

.btn-pagina:disabled { opacity: 0.5; cursor: not-allowed; }

.sin-resultados {
  text-align: center; padding: 60px;
  background: var(--bg-secondary); border-radius: 16px;
}

.filtros-activos-bar {
  margin-top: 20px; padding: 15px;
  background: rgba(14, 165, 233, 0.05);
  border-radius: 12px; border: 1px solid rgba(14, 165, 233, 0.2);
}

.filtro-chip.activo {
  background: white; padding: 5px 12px; border-radius: 20px;
  font-size: 0.85rem; font-weight: 600; color: #0ea5e9;
  border: 1px solid rgba(14, 165, 233, 0.3); display: inline-flex; align-items: center; gap: 5px; margin-right: 10px;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .catalogo-header { flex-direction: column; text-align: center; }
  .productos-grid { grid-template-columns: 1fr; }
  .paginacion { flex-direction: column; gap: 15px; }
}
</style>