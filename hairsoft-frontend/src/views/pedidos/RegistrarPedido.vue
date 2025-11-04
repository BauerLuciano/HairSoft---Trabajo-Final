<template>
  <div class="pedido-container">
    <div class="header-section">
      <h2>
        <Package class="header-icon" />
        Nuevo Pedido a Proveedor
      </h2>
      <button @click="volverAlListado" class="btn-back">
        <ArrowLeft :size="18" />
        Volver al Listado
      </button>
    </div>

    <!-- Selección de Proveedor -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <Building2 :size="20" />
        </div>
        <h3>Proveedor</h3>
      </div>
      <div class="input-group">
        <select
          v-model="pedido.proveedor"
          required
          class="select-modern"
          :disabled="cargandoProveedores"
          @change="onProveedorChange"
        >
          <option value="">Seleccione un proveedor</option>
          <option 
            v-for="proveedor in proveedoresActivos" 
            :key="proveedor.id" 
            :value="proveedor.id"
          >
            {{ proveedor.nombre }} - {{ proveedor.contacto || 'Sin contacto' }}
          </option>
        </select>
      </div>

      <!-- Info del Proveedor Seleccionado -->
      <div v-if="proveedorSeleccionado" class="proveedor-info">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">
              <User :size="16" />
              Contacto:
            </span>
            <span class="info-value">{{ proveedorSeleccionado.contacto || 'No especificado' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">
              <Phone :size="16" />
              Teléfono:
            </span>
            <span class="info-value">{{ proveedorSeleccionado.telefono || 'No especificado' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">
              <Mail :size="16" />
              Email:
            </span>
            <span class="info-value">{{ proveedorSeleccionado.email || 'No especificado' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros de Productos -->
    <div v-if="pedido.proveedor" class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <ClipboardList :size="20" />
        </div>
        <h3>Selección de Productos</h3>
      </div>

      <!-- Filtro por Categorías -->
      <div class="filtros-section">
        <h4>
          <Tag :size="18" />
          Filtrar por Categorías
        </h4>
        <div class="categorias-grid">
          <div 
            v-for="categoria in categoriasDelProveedor" 
            :key="categoria.id"
            class="categoria-item"
            :class="{ 'selected': categoriasSeleccionadas.includes(categoria.id) }"
            @click="toggleCategoria(categoria.id)"
          >
            <div class="categoria-checkbox">
              <div class="checkmark" :class="{ 'checked': categoriasSeleccionadas.includes(categoria.id) }">
                <Check v-if="categoriasSeleccionadas.includes(categoria.id)" :size="14" />
              </div>
            </div>
            <div class="categoria-info">
              <span class="categoria-nombre">{{ categoria.nombre }}</span>
              <span class="productos-count">
                <Package2 :size="12" />
                {{ contarProductosPorCategoria(categoria.id) }} productos
              </span>
            </div>
          </div>
        </div>

        <div class="filtro-actions">
          <button @click="seleccionarTodasCategorias" class="btn-outline">
            <CheckSquare :size="16" />
            Seleccionar Todas
          </button>
          <button @click="deseleccionarTodasCategorias" class="btn-outline">
            <RotateCcw :size="16" />
            Limpiar
          </button>
        </div>
      </div>

      <!-- Búsqueda y Productos -->
      <div v-if="categoriasSeleccionadas.length > 0" class="productos-section">
        <div class="search-header">
          <div class="search-box">
            <Search class="search-icon" :size="18" />
            <input
              v-model="busquedaProducto"
              type="text"
              placeholder="Buscar producto por nombre o código..."
              class="input-modern"
            />
          </div>
          <div class="productos-stats">
            <span class="stats-badge">
              <Boxes :size="14" />
              {{ productosFiltrados.length }} productos
            </span>
          </div>
        </div>

        <!-- Lista de Productos -->
        <div v-if="productosFiltrados.length > 0" class="productos-grid">
          <div 
            v-for="producto in productosFiltrados" 
            :key="producto.id"
            class="producto-item"
            :class="{ 'selected': productosSeleccionados.includes(producto.id) }"
            @click="toggleSeleccionProducto(producto.id)"
          >
            <div class="producto-seleccion">
              <div class="producto-checkbox" :class="{ 'checked': productosSeleccionados.includes(producto.id) }">
                <Check v-if="productosSeleccionados.includes(producto.id)" :size="14" />
              </div>
            </div>
            
            <div class="producto-info">
              <div class="producto-header">
                <span class="producto-nombre">{{ producto.nombre }}</span>
                <span class="producto-precio">
                  <DollarSign :size="16" />
                  {{ producto.precio }}
                </span>
              </div>
              <div class="producto-details">
                <span class="producto-codigo">
                  <Hash :size="12" />
                  {{ producto.codigo || 'SIN-CODIGO' }}
                </span>
                <span class="producto-stock" :class="getStockClass(getProductStock(producto))">
                  <Warehouse :size="12" />
                  Stock: {{ getProductStock(producto) }}
                </span>
                <span class="producto-categoria">
                  <FolderOpen :size="12" />
                  {{ obtenerNombreCategoria(producto.categoria_id) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="no-resultados">
          <SearchX class="no-resultados-icon" :size="48" />
          <p>No se encontraron productos</p>
          <small>Intenta con otros términos de búsqueda</small>
        </div>

        <!-- Botón Agregar Seleccionados -->
        <div v-if="productosSeleccionados.length > 0" class="agregar-section">
          <button @click="agregarProductosSeleccionados" class="btn-agregar-masivo">
            <ShoppingCart :size="18" />
            Agregar {{ productosSeleccionados.length }} Productos al Pedido
          </button>
        </div>
      </div>

      <div v-else-if="categoriasDelProveedor.length > 0" class="seleccion-categoria">
        <FolderSearch class="seleccion-icon" :size="48" />
        <p>Selecciona al menos una categoría para ver los productos</p>
      </div>
    </div>

    <!-- Carrito del Pedido -->
    <div v-if="pedido.detalles.length > 0" class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <ShoppingBag :size="20" />
        </div>
        <h3>Productos en el Pedido</h3>
        <span class="badge-count">{{ pedido.detalles.length }}</span>
      </div>

      <div class="detalles-list">
        <div 
          v-for="(detalle, index) in pedido.detalles" 
          :key="index"
          class="detalle-item"
        >
          <div class="detalle-info">
            <div class="detalle-header">
              <span class="detalle-nombre">{{ detalle.producto_nombre }}</span>
              <span class="detalle-categoria">
                <Tag :size="12" />
                {{ obtenerNombreCategoria(detalle.producto_categoria_id) }}
              </span>
            </div>
            <div class="detalle-details">
              <span class="detalle-codigo">
                <Barcode :size="12" />
                {{ detalle.producto_codigo || 'SIN-CODIGO' }}
              </span>
              <span class="detalle-stock">
                <Package :size="12" />
                Stock actual: {{ detalle.producto_stock_actual }}
              </span>
            </div>
          </div>
          
          <div class="detalle-controls">
            <div class="control-group">
              <label>
                <Layers :size="14" />
                Cantidad
              </label>
              <input
                v-model.number="detalle.cantidad"
                type="number"
                min="1"
                class="input-cantidad"
                @change="actualizarSubtotal(detalle)"
              />
            </div>
            
            <div class="control-group">
              <label>
                <CreditCard :size="14" />
                Precio Unit.
              </label>
              <input
                v-model.number="detalle.precio_unitario"
                type="number"
                step="0.01"
                min="0"
                class="input-precio"
                @change="actualizarSubtotal(detalle)"
              />
            </div>
            
            <div class="detalle-subtotal">
              <span class="subtotal-label">
                <Calculator :size="14" />
                Subtotal
              </span>
              <span class="subtotal-value">${{ detalle.subtotal }}</span>
            </div>
            
            <button 
              @click="eliminarProducto(index)" 
              class="btn-eliminar"
              title="Eliminar producto"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>
      </div>

      <!-- Resumen del Pedido -->
      <div class="resumen-pedido">
        <div class="resumen-grid">
          <div class="resumen-item">
            <span>
              <Package2 :size="18" />
              Total de Productos:
            </span>
            <strong>{{ pedido.detalles.length }}</strong>
          </div>
          <div class="resumen-item total">
            <span>
              <Wallet :size="18" />
              Total del Pedido:
            </span>
            <strong>${{ totalPedido }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Notas Opcionales -->
    <div class="card-modern">
      <div class="card-header">
        <div class="card-icon">
          <FileText :size="20" />
        </div>
        <h3>Notas del Pedido (Opcional)</h3>
      </div>
      <textarea
        v-model="pedido.observaciones"
        rows="3"
        placeholder="Ej: Productos urgentes, instrucciones especiales de entrega, contacto específico..."
        class="textarea-modern"
        maxlength="500"
      ></textarea>
      <div class="textarea-footer">
        <small>
          <AlignLeft :size="12" />
          {{ pedido.observaciones.length }}/500 caracteres
        </small>
      </div>
    </div>

    <!-- Botón Final -->
    <button 
      @click="registrarPedido" 
      :disabled="!puedeRegistrar || cargando" 
      class="btn-registrar-premium"
      :class="{'btn-processing': cargando}"
    >
      <span v-if="!cargando" class="btn-content">
        <CheckCircle2 :size="20" />
        Registrar Pedido - ${{ totalPedido }}
      </span>
      <span v-else class="btn-content">
        <Loader2 :size="20" class="btn-spinner" />
        Procesando...
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'
import { 
  Package, ArrowLeft, Building2, User, Phone, Mail, 
  ClipboardList, Tag, Check, CheckSquare, RotateCcw,
  Search, Boxes, DollarSign, Hash, Warehouse, FolderOpen,
  SearchX, FolderSearch, ShoppingCart, ShoppingBag,
  Barcode, Layers, CreditCard, Calculator, Trash2,
  Package2, Wallet, FileText, AlignLeft, CheckCircle2, Loader2
} from 'lucide-vue-next'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

// Estados
const pedido = ref({
  proveedor: '',
  observaciones: '',
  detalles: []
})

const proveedores = ref([])
const productos = ref([])
const categorias = ref([])
const cargando = ref(false)
const cargandoProveedores = ref(false)
const busquedaProducto = ref('')
const categoriasSeleccionadas = ref([])
const productosSeleccionados = ref([])

// Computed
const proveedoresActivos = computed(() => {
  return proveedores.value.filter(p => p.estado === 'ACTIVO')
})

const proveedorSeleccionado = computed(() => {
  return proveedores.value.find(p => p.id === pedido.value.proveedor)
})

const categoriasDelProveedor = computed(() => {
  if (!pedido.value.proveedor) return []
  
  const proveedorId = parseInt(pedido.value.proveedor)
  const categoriasUnicas = {}
  
  productos.value
    .filter(producto => producto.proveedores && producto.proveedores.includes(proveedorId))
    .forEach(producto => {
      if (producto.categoria_id && !categoriasUnicas[producto.categoria_id]) {
        const categoria = categorias.value.find(c => c.id === producto.categoria_id)
        if (categoria) {
          categoriasUnicas[producto.categoria_id] = categoria
        }
      }
    })
  
  return Object.values(categoriasUnicas).sort((a, b) => a.nombre.localeCompare(b.nombre))
})

const productosFiltrados = computed(() => {
  if (!pedido.value.proveedor || categoriasSeleccionadas.value.length === 0) return []
  
  const busqueda = busquedaProducto.value.toLowerCase()
  const proveedorId = parseInt(pedido.value.proveedor)
  
  return productos.value.filter(producto => {
    const coincideProveedor = producto.proveedores && producto.proveedores.includes(proveedorId)
    const coincideCategoria = categoriasSeleccionadas.value.includes(producto.categoria_id)
    const coincideBusqueda = !busqueda || 
      producto.nombre.toLowerCase().includes(busqueda) || 
      (producto.codigo && producto.codigo.toLowerCase().includes(busqueda))
    
    return coincideProveedor && coincideCategoria && coincideBusqueda &&
           !pedido.value.detalles.some(d => d.producto === producto.id)
  })
})

const totalPedido = computed(() => {
  return pedido.value.detalles.reduce((total, detalle) => total + detalle.subtotal, 0)
})

const puedeRegistrar = computed(() => {
  return pedido.value.proveedor && 
         pedido.value.detalles.length > 0 && 
         pedido.value.detalles.every(d => d.cantidad > 0 && d.precio_unitario > 0)
})

// Métodos
const cargarDatosIniciales = async () => {
  try {
    cargandoProveedores.value = true
    const response = await axios.get(`${API_BASE}/usuarios/api/pedidos/datos-crear/`)
    proveedores.value = response.data.proveedores
    productos.value = response.data.productos
    categorias.value = response.data.categorias || []
    
    // Debug para verificar estructura de productos
    console.log('Estructura completa de productos:', productos.value)
    if (productos.value.length > 0) {
      console.log('Primer producto:', productos.value[0])
      console.log('Campos disponibles:', Object.keys(productos.value[0]))
    }
    
  } catch (error) {
    console.error('Error cargando datos:', error)
    Swal.fire('Error', 'No se pudieron cargar los datos del formulario', 'error')
  } finally {
    cargandoProveedores.value = false
  }
}

// ✅ FUNCIÓN: Maneja consistentemente el stock
const getProductStock = (producto) => {
  // Intenta con stock_actual, luego con stock, luego default 0
  if (producto.stock_actual !== undefined && producto.stock_actual !== null) {
    return producto.stock_actual
  } else if (producto.stock !== undefined && producto.stock !== null) {
    return producto.stock
  }
  return 0
}

const onProveedorChange = () => {
  categoriasSeleccionadas.value = []
  productosSeleccionados.value = []
  busquedaProducto.value = ''
  
  if (pedido.value.detalles.length > 0) {
    Swal.fire({
      title: '¿Cambiar proveedor?',
      text: 'Se eliminarán los productos agregados al pedido',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, cambiar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        pedido.value.detalles = []
      } else {
        pedido.value.proveedor = ''
      }
    })
  }
}

const toggleCategoria = (categoriaId) => {
  const index = categoriasSeleccionadas.value.indexOf(categoriaId)
  if (index > -1) {
    categoriasSeleccionadas.value.splice(index, 1)
  } else {
    categoriasSeleccionadas.value.push(categoriaId)
  }
  productosSeleccionados.value = []
}

const contarProductosPorCategoria = (categoriaId) => {
  if (!pedido.value.proveedor) return 0
  const proveedorId = parseInt(pedido.value.proveedor)
  return productos.value.filter(producto => 
    producto.proveedores && 
    producto.proveedores.includes(proveedorId) &&
    producto.categoria_id === categoriaId
  ).length
}

const obtenerNombreCategoria = (categoriaId) => {
  const categoria = categorias.value.find(c => c.id === categoriaId)
  return categoria ? categoria.nombre : 'Sin categoría'
}

const seleccionarTodasCategorias = () => {
  categoriasSeleccionadas.value = categoriasDelProveedor.value.map(c => c.id)
}

const deseleccionarTodasCategorias = () => {
  categoriasSeleccionadas.value = []
}

const getStockClass = (stock) => {
  const stockValue = parseInt(stock) || 0
  if (stockValue === 0) return 'stock-critico'
  if (stockValue < 10) return 'stock-bajo'
  if (stockValue < 20) return 'stock-medio'
  return 'stock-alto'
}

const toggleSeleccionProducto = (productoId) => {
  const index = productosSeleccionados.value.indexOf(productoId)
  if (index > -1) {
    productosSeleccionados.value.splice(index, 1)
  } else {
    productosSeleccionados.value.push(productoId)
  }
}

const agregarProductosSeleccionados = () => {
  productosSeleccionados.value.forEach(productoId => {
    const producto = productos.value.find(p => p.id === productoId)
    if (producto) {
      pedido.value.detalles.push({
        producto: producto.id,
        producto_nombre: producto.nombre,
        producto_codigo: producto.codigo,
        producto_stock_actual: getProductStock(producto),
        producto_categoria_id: producto.categoria_id,
        cantidad: 1,
        precio_unitario: producto.precio,
        subtotal: producto.precio
      })
    }
  })

  Swal.fire({
    icon: 'success',
    title: 'Productos Agregados',
    text: `${productosSeleccionados.value.length} productos agregados al pedido`,
    timer: 2000,
    showConfirmButton: false
  })

  productosSeleccionados.value = []
  busquedaProducto.value = ''
}

const eliminarProducto = (index) => {
  pedido.value.detalles.splice(index, 1)
  Swal.fire({
    icon: 'info',
    title: 'Producto Eliminado',
    timer: 1500,
    showConfirmButton: false
  })
}

const actualizarSubtotal = (detalle) => {
  detalle.subtotal = detalle.cantidad * detalle.precio_unitario
}

const registrarPedido = async () => {
  try {
    cargando.value = true
    
    const payload = {
      proveedor: pedido.value.proveedor,
      observaciones: pedido.value.observaciones || '',
      detalles: pedido.value.detalles.map(detalle => ({
        producto: detalle.producto,
        cantidad: detalle.cantidad,
        precio_unitario: detalle.precio_unitario
      }))
    }

    const response = await axios.post(`${API_BASE}/usuarios/api/pedidos/`, payload)
    
    await Swal.fire({
      title: '✅ Pedido Registrado',
      text: 'El pedido se ha creado exitosamente',
      icon: 'success',
      confirmButtonText: 'Continuar'
    })
    
    router.push('/pedidos')
    
  } catch (error) {
    console.error('Error registrando pedido:', error)
    let errorMessage = 'Error al registrar el pedido'
    
    if (error.response?.status === 400) {
      const errors = error.response.data
      errorMessage = Object.entries(errors).map(([field, messages]) => 
        `• ${field}: ${messages.join(', ')}`
      ).join('\n')
    }
    
    Swal.fire('Error', errorMessage, 'error')
  } finally {
    cargando.value = false
  }
}

const volverAlListado = () => {
  router.push('/pedidos')
}

onMounted(() => {
  cargarDatosIniciales()
})
</script>

<style scoped>
/* Estilos base mejorados */
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.header-section h2 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: #007bff;
}

.btn-back {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-back:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Cards modernas */
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

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f1f3f4;
}

.card-icon {
  background: linear-gradient(135deg, #007bff, #0056b3);
  padding: 10px;
  border-radius: 10px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
}

.badge-count {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 600;
}

/* Inputs y selects */
.input-group {
  margin-bottom: 20px;
}

.select-modern, .input-modern {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
}

.select-modern:focus, .input-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

/* Info del proveedor */
.proveedor-info {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #dee2e6;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-value {
  color: #1a1a1a;
  font-weight: 500;
  padding-left: 22px;
}

/* Filtros */
.filtros-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1a1a1a;
  margin-bottom: 15px;
}

/* Categorías */
.categorias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.categoria-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.categoria-item:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.categoria-item.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.categoria-checkbox {
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
}

.checkmark.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.categoria-info {
  flex: 1;
}

.categoria-nombre {
  font-weight: 600;
  color: #1a1a1a;
  display: block;
  margin-bottom: 4px;
}

.productos-count {
  font-size: 0.8em;
  color: #6c757d;
  background: #f8f9fa;
  padding: 3px 8px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.filtro-actions {
  display: flex;
  gap: 10px;
}

.btn-outline {
  background: transparent;
  border: 2px solid #007bff;
  color: #007bff;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-outline:hover {
  background: #007bff;
  color: white;
  transform: translateY(-1px);
}

/* Búsqueda */
.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.search-box {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-box .input-modern {
  padding-left: 40px;
}

.stats-badge {
  background: linear-gradient(135deg, #6c757d, #5a6268);
  color: white;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 600;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Productos */
.productos-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.producto-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.producto-item:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.producto-item.selected {
  border-color: #007bff;
  background: #e7f3ff;
}

.producto-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: transparent;
  flex-shrink: 0;
}

.producto-checkbox.checked {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.producto-info {
  flex: 1;
}

.producto-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.producto-nombre {
  font-weight: 600;
  color: #1a1a1a;
  flex: 1;
  margin-right: 10px;
}

.producto-precio {
  color: #28a745;
  font-weight: 700;
  font-size: 1.1em;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 2px;
}

.producto-details {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.producto-codigo, .producto-stock, .producto-categoria {
  font-size: 0.85em;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.producto-codigo {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #e9ecef;
}

.producto-categoria {
  background: #e7f3ff;
  color: #0056b3;
  border: 1px solid #b3d9ff;
}

.stock-critico {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.stock-bajo {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.stock-medio {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.stock-alto {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.agregar-section {
  margin-top: 20px;
  text-align: center;
}

.btn-agregar-masivo {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1em;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-agregar-masivo:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
}

/* Detalles del pedido */
.detalles-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detalle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.detalle-item:hover {
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}

.detalle-info {
  flex: 1;
}

.detalle-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.detalle-nombre {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 1.1em;
}

.detalle-categoria {
  background: #e7f3ff;
  color: #0056b3;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8em;
  font-weight: 500;
  border: 1px solid #b3d9ff;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.detalle-details {
  display: flex;
  gap: 15px;
  align-items: center;
}

.detalle-codigo, .detalle-stock {
  font-size: 0.9em;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 4px;
}

.detalle-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: center;
}

.control-group label {
  font-size: 0.8em;
  color: #6c757d;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-cantidad, .input-precio {
  width: 80px;
  text-align: center;
  padding: 8px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  background: #fff;
  font-weight: 600;
  color: #1a1a1a;
}

.input-cantidad:focus, .input-precio:focus {
  border-color: #007bff;
  outline: none;
}

.detalle-subtotal {
  text-align: center;
  min-width: 100px;
}

.subtotal-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 0.8em;
  color: #6c757d;
  margin-bottom: 4px;
}

.subtotal-value {
  font-weight: 700;
  color: #28a745;
  font-size: 1.1em;
}

.btn-eliminar {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-eliminar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

/* Resumen */
.resumen-pedido {
  margin-top: 25px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  border: 2px solid #e9ecef;
}

.resumen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  color: #1a1a1a;
  font-size: 1em;
}

.resumen-item span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.resumen-item.total {
  border-top: 2px solid #dee2e6;
  margin-top: 10px;
  padding-top: 15px;
  font-size: 1.2em;
  font-weight: 700;
}

/* Textarea */
.textarea-modern {
  width: 100%;
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #1a1a1a;
  resize: vertical;
  min-height: 80px;
}

.textarea-modern:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  outline: none;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.textarea-footer small {
  color: #6c757d;
  font-size: 0.8em;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Estados vacíos */
.no-resultados, .seleccion-categoria {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.no-resultados-icon, .seleccion-icon {
  margin-bottom: 15px;
  opacity: 0.5;
  color: #6c757d;
}

.no-resultados p, .seleccion-categoria p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: #1a1a1a;
}

.no-resultados small, .seleccion-categoria small {
  font-size: 0.9em;
  color: #6c757d;
}

/* Botón final premium */
.btn-registrar-premium {
  width: 100%;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  font-size: 1.1em;
  padding: 18px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 25px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-registrar-premium:hover:not(:disabled):not(.btn-processing) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
  background: linear-gradient(135deg, #0056b3, #004085);
}

.btn-registrar-premium:disabled,
.btn-registrar-premium.btn-processing {
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

.btn-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .pedido-container {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .search-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .detalle-item {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .detalle-controls {
    justify-content: space-between;
    flex-wrap: wrap;
  }
  
  .categorias-grid {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>