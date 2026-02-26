<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar || mostrarRegistrarMarca || mostrarHistorial }">
      
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de productos</h1>
          <p>Gestión de productos del sistema</p>
        </div>
        <div class="header-buttons" style="display: flex; gap: 12px;">
          <button @click="mostrarRegistrar = true" class="register-button">
            <Plus :size="18" />
            Registrar Producto
          </button>
          <button @click="mostrarRegistrarMarca = true" class="register-button">
            <Tag :size="18" />
            Registrar Marca
          </button>
        </div>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre o código..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Categoría</label>
            <select v-model="filtros.categoria" class="filter-input">
              <option value="">Todas</option>
              <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
                {{ categoria.nombre }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Marca</label>
            <select v-model="filtros.marca" class="filter-input">
              <option value="">Todas</option>
              <option v-for="marca in marcas" :key="marca.id" :value="marca.id">
                {{ marca.nombre }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos</option>
              <option value="ACTIVO">Activos</option>
              <option value="INACTIVO">Inactivos</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Stock bajo</label>
            <select v-model="filtros.stockBajo" class="filter-input">
              <option value="">Todos</option>
              <option value="si">Solo stock crítico</option>
            </select>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              <Trash2 :size="16" />
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>

      <div v-if="cargando" class="no-results">
        <Loader2 class="animate-spin no-results-icon" :size="48" />
        <p>Sincronizando con el servidor...</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th style="width: 90px;">Código</th>
                <th style="width: 160px;">Nombre</th>
                <th style="width: 100px;">Categoría</th>
                <th style="width: 100px;">Marca</th>
                <th style="width: 90px;">Precio</th>
                <th style="width: 110px;">Stock</th>
                <th style="width: 90px;">Estado</th>
                <th style="width: 150px;">Proveedores</th>
                <th style="width: 160px;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="producto in productosPaginados" :key="producto.id" 
                  :class="getRowClass(producto)">
                <td><strong>{{ producto.codigo || '–' }}</strong></td>
                <td class="nombre-cell">{{ producto.nombre || '–' }}</td>
                <td>
                  <span class="badge-estado estado-info">
                    {{ getCategoriaNombre(producto) }}
                  </span>
                </td>
                <td>
                  <span class="badge-estado estado-secondary">
                    {{ getMarcaNombre(producto) }}
                  </span>
                </td>
                <td><strong>${{ producto.precio ? producto.precio.toLocaleString() : '0' }}</strong></td>
                
                <td>
                  <span class="badge-estado" :class="getStockClass(producto)">
                    {{ producto.stock_actual || 0 }} 
                  </span>
                </td>

                <td>
                  <span class="badge-estado" :class="getEstadoClass(producto.estado)">
                    {{ producto.estado === 'ACTIVO' ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td>
                  <div class="proveedores-lista">
                    <div v-for="(proveedor, index) in getPrimerosProveedores(producto)" :key="proveedor.id" 
                         class="proveedor-item">
                      <span class="proveedor-nombre">{{ proveedor.nombre }}</span>
                    </div>
                    <div v-if="getProveedoresNombres(producto).length > 3" class="mas-proveedores">
                      +{{ getProveedoresNombres(producto).length - 3 }} más...
                    </div>
                    <div v-else-if="getProveedoresNombres(producto).length === 0" class="sin-proveedores">
                      Sin proveedor
                    </div>
                  </div>
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="abrirAjusteStock(producto)" class="action-button stock-btn" title="Ajustar stock físico">
                      <PackagePlus :size="14" />
                    </button>

                    <button @click="abrirHistorialStock(producto)" class="action-button historial-btn" title="Ver historial de stock">
                      <ClipboardList :size="14" />
                    </button>

                    <button @click="editarProducto(producto)" class="action-button edit" title="Editar producto">
                      <Edit3 :size="14" />
                    </button>
                    <button @click="cambiarEstadoProducto(producto)" class="action-button" 
                            :class="producto.estado === 'ACTIVO' ? 'delete' : 'success'" 
                            :title="producto.estado === 'ACTIVO' ? 'Desactivar producto' : 'Activar producto'">
                      <Power :size="14" v-if="producto.estado === 'ACTIVO'" />
                      <CheckCircle :size="14" v-else />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="productosPaginados.length === 0" class="no-results">
            <PackageX class="no-results-icon" :size="48" />
            <p>No se encontraron productos</p>
            <small>Intenta con otros términos de búsqueda</small>
          </div>
        </div>

        <div class="usuarios-count">
          <p>
            <Package :size="16" />
            Mostrando {{ productosPaginados.length }} de {{ productosFiltrados.length }} productos
          </p>
          <div class="alertas-container">
            <span v-if="productosStockBajo > 0" class="alerta-stock">
              <AlertTriangle :size="14" />
              {{ productosStockBajo }} con stock bajo
            </span>
            <span v-if="productosInactivos > 0" class="alerta-inactivo">
              <PowerOff :size="14" />
              {{ productosInactivos }} inactivos
            </span>
          </div>
        </div>

        <div class="pagination">
          <button @click="paginaAnterior" :disabled="pagina === 1">
            <ChevronLeft :size="16" />
            Anterior
          </button>
          <span>Página {{ pagina }} de {{ totalPaginas }}</span>
          <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">
            Siguiente
            <ChevronRight :size="16" />
          </button>
        </div>
      </div>
    </div>

    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <RegistrarProducto 
          @producto-registrado="productoRegistrado"
          @cancelar="cerrarModal"
        />
      </div>
    </div>

    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
        <ModificarProducto 
          :producto-id="productoEditando?.id" 
          @producto-actualizado="productoActualizado"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>

    <div v-if="mostrarRegistrarMarca" class="modal-overlay" @click.self="cerrarModalMarca">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModalMarca" title="Cerrar formulario">
          <X :size="20" />
        </button>
        <RegistrarMarca 
          @marca-registrada="marcaRegistrada"
          @cancelar="cerrarModalMarca"
        />
      </div>
    </div>

    <div v-if="mostrarHistorial" class="modal-overlay" @click.self="cerrarModalHistorial">
      <div class="modal-content modal-historial">
        <button class="modal-close" @click="cerrarModalHistorial" title="Cerrar historial">
          <X :size="20" />
        </button>
        
        <div class="historial-header">
          <h2>Auditoría de Stock</h2>
          <p><strong>Producto:</strong> {{ productoEditando?.nombre }}</p>
        </div>

        <div v-if="cargandoHistorial" class="loading-state" style="padding: 40px;">
          <Loader2 class="animate-spin" :size="32" style="color: #0ea5e9; margin: 0 auto 10px;" />
          <p>Cargando registros...</p>
        </div>

        <div v-else class="historial-body">
          <div v-if="historialStock.length > 0">
            <table class="users-table">
              <thead>
                <tr>
                  <th>Fecha y Hora</th>
                  <th>Usuario</th>
                  <th style="text-align: center;">Movimiento</th>
                  <th style="text-align: center;">Stock Resultante</th>
                  <th>Motivo Registrado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="reg in historialPaginado" :key="reg.id">
                  <td>{{ formatFechaHora(reg.fecha) }}</td>
                  <td><strong>{{ reg.usuario }}</strong></td>
                  <td style="text-align: center;">
                    <span :class="reg.diferencia > 0 ? 'badge-positivo' : 'badge-negativo'">
                      {{ reg.diferencia > 0 ? '+' : '' }}{{ reg.diferencia }}
                    </span>
                  </td>
                  <td style="text-align: center; font-weight: 800; color: var(--text-primary);">
                    {{ reg.cantidad_nueva }} u.
                  </td>
                  <td style="color: var(--text-secondary); font-style: italic;">
                    "{{ reg.motivo }}"
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="totalPaginasHistorial > 1" class="pagination" style="margin-top: 20px; padding-top: 15px; border-top: 1px solid var(--border-color);">
              <button @click="paginaAnteriorHistorial" :disabled="paginaHistorial === 1">
                <ChevronLeft :size="16" />
                Anterior
              </button>
              <span>Página {{ paginaHistorial }} de {{ totalPaginasHistorial }}</span>
              <button @click="paginaSiguienteHistorial" :disabled="paginaHistorial === totalPaginasHistorial">
                Siguiente
                <ChevronRight :size="16" />
              </button>
            </div>

          </div>
          <div v-else class="no-results" style="padding: 40px;">
            <ClipboardList :size="40" style="color: #94a3b8; margin: 0 auto 10px;" />
            <p>Este producto aún no tiene ajustes manuales registrados.</p>
          </div>
        </div>
      </div>
    </div>

</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from '@/utils/axiosConfig'
import { useRoute } from 'vue-router'
import Swal from 'sweetalert2'
import RegistrarProducto from './RegistrarProducto.vue'
import ModificarProducto from './ModificarProducto.vue'
import RegistrarMarca from './RegistrarMarca.vue'
import { 
  Package, PackageX, Plus, Tag, Edit3, Power, CheckCircle, PowerOff,
  ChevronLeft, ChevronRight, Trash2, X, AlertTriangle, Loader2, PackagePlus, ClipboardList
} from 'lucide-vue-next'

const route = useRoute()

// CONSTANTES API
const API_BASE = 'http://127.0.0.1:8000'; 

const productos = ref([])
const categorias = ref([])
const proveedores = ref([])
const marcas = ref([])

const filtros = ref({ busqueda: '', categoria: '', stockBajo: '', marca: '', estado: '' })

// Paginación principal
const pagina = ref(1)
const itemsPorPagina = 8

// Estados UI principales
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const mostrarRegistrarMarca = ref(false)
const productoEditando = ref(null)
const cargando = ref(true)

// --- ESTADOS PARA HISTORIAL ---
const mostrarHistorial = ref(false)
const historialStock = ref([])
const cargandoHistorial = ref(false)
const paginaHistorial = ref(1)
const itemsPorPaginaHistorial = 8

// --- CARGA DE DATOS ---
const cargarProductos = async () => {
  try {
    const res = await axios.get('/usuarios/api/productos/')
    const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
    productos.value = data.sort((a, b) => b.id - a.id)
  } catch (err) { 
    console.error(err) 
  }
}

const cargarAuxiliares = async () => {
  try {
    const [resC, resP, resM] = await Promise.all([
      axios.get('/usuarios/api/categorias/productos/'),
      axios.get('/usuarios/api/proveedores/'),
      axios.get('/usuarios/api/marcas/')
    ])
    categorias.value = resC.data
    proveedores.value = resP.data
    marcas.value = resM.data
  } catch (e) {
    console.error(e)
  }
}

// --- LOGICA VISUAL ---
const getCategoriaNombre = (p) => p.categoria_nombre || categorias.value.find(c => c.id === p.categoria)?.nombre || '–'
const getMarcaNombre = (p) => p.marca_nombre || marcas.value.find(m => m.id === p.marca)?.nombre || '–'

const getProveedoresNombres = (p) => {
  if (!p.proveedores) return []
  return p.proveedores.map(id => proveedores.value.find(pr => pr.id === id)?.nombre).filter(Boolean)
}
const getPrimerosProveedores = (p) => getProveedoresNombres(p).slice(0, 3).map((n, i) => ({ id: i, nombre: n }))

const getEstadoClass = (e) => (e === 'ACTIVO' ? 'estado-success' : 'estado-danger')

const getStockClass = (p) => {
  const actual = p.stock_actual || 0
  const minimo = p.stock_minimo || 5 
  
  if (actual === 0) return 'estado-danger'
  if (actual <= minimo) return 'estado-warning'
  return 'estado-success'
}

const getRowClass = (p) => {
  if ((p.stock_actual || 0) <= (p.stock_minimo || 5)) return 'stock-bajo-row'
  return ''
}

const formatFechaHora = (isoString) => {
  const f = new Date(isoString);
  return f.toLocaleString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// --- FILTROS Y PAGINACIÓN PRINCIPAL ---
const productosFiltrados = computed(() => {
  return productos.value.filter(p => {
    const term = filtros.value.busqueda.toLowerCase()
    const matchSearch = !term || p.nombre?.toLowerCase().includes(term) || p.codigo?.toLowerCase().includes(term)
    const matchCat = !filtros.value.categoria || p.categoria == filtros.value.categoria
    const matchMarca = !filtros.value.marca || p.marca == filtros.value.marca
    const matchEstado = !filtros.value.estado || p.estado == filtros.value.estado
    
    const minimo = p.stock_minimo || 5
    const matchStock = !filtros.value.stockBajo || p.stock_actual <= minimo
    
    return matchSearch && matchCat && matchStock && matchMarca && matchEstado
  })
})

const productosStockBajo = computed(() => 
  productosFiltrados.value.filter(p => p.stock_actual <= (p.stock_minimo || 5)).length
)
const productosInactivos = computed(() => productosFiltrados.value.filter(p => p.estado === 'INACTIVO').length)

const totalPaginas = computed(() => Math.max(1, Math.ceil(productosFiltrados.value.length / itemsPorPagina)))
const productosPaginados = computed(() => {
  const start = (pagina.value - 1) * itemsPorPagina
  return productosFiltrados.value.slice(start, start + itemsPorPagina)
})

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }

// --- LOGICA DE PAGINACIÓN HISTORIAL ---
const totalPaginasHistorial = computed(() => Math.max(1, Math.ceil(historialStock.value.length / itemsPorPaginaHistorial)))
const historialPaginado = computed(() => {
  const start = (paginaHistorial.value - 1) * itemsPorPaginaHistorial
  return historialStock.value.slice(start, start + itemsPorPaginaHistorial)
})

const paginaAnteriorHistorial = () => { if (paginaHistorial.value > 1) paginaHistorial.value-- }
const paginaSiguienteHistorial = () => { if (paginaHistorial.value < totalPaginasHistorial.value) paginaHistorial.value++ }

// --- ACCIONES ---

// 🔥 FUNCIÓN: AJUSTE DE STOCK (+ / -)
const abrirAjusteStock = async (producto) => {
  const stockActual = producto.stock_actual || 0;

  const { value: formValues } = await Swal.fire({
    title: `
      <div style="display:flex; align-items:center; gap:12px; color:#0f172a; font-weight:800; font-size:1.4rem;">
        <span style="background:#e0f2fe; padding:8px; border-radius:10px; color:#0ea5e9; display:flex;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
        </span>
        Ajuste de Inventario
      </div>`,
    html: `
      <div style="text-align: left; font-family: 'Inter', sans-serif; margin-top: 15px;">
        
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; margin-bottom: 20px;">
          <p style="margin: 0; font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Producto Seleccionado</p>
          <p style="margin: 4px 0 12px 0; font-size: 1.15rem; color: #0f172a; font-weight: 800;">${producto.nombre}</p>
          
          <div style="display: flex; justify-content: space-between; align-items: center; background: white; padding: 12px 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Stock Actual Fijo</span>
            <span style="font-size: 1.2rem; color: #64748b; font-weight: 900;">${stockActual} u.</span>
          </div>
        </div>

        <div style="margin-bottom: 20px;">
          <label style="display: block; font-size: 0.8rem; font-weight: 800; color: #475569; margin-bottom: 8px; letter-spacing: 0.5px;">CANTIDAD A SUMAR O RESTAR (+ / -) <span style="color:#ef4444">*</span></label>
          <div style="position: relative; display: flex; align-items: center;">
            <input id="swal-input-diferencia" type="number" 
                   style="width: 100%; box-sizing: border-box; padding: 14px 15px; border: 2px solid #cbd5e1; border-radius: 10px; background-color: #ffffff; font-size: 0.95rem; font-weight: 600; color: #0f172a; outline: none; transition: border-color 0.2s;" 
                   placeholder="Ej: 5 (para sumar) o -2 (para restar)"
                   onfocus="this.style.borderColor='#0ea5e9'" onblur="this.style.borderColor='#cbd5e1'">
          </div>
          
          <div id="swal-resultado-label" style="margin-top: 10px; font-size: 0.9rem; font-weight: 600; color: #64748b; background: #e0f2fe; padding: 10px; border-radius: 8px; border: 1px solid #bae6fd;">
            Ingresá un valor para ver cómo quedará el stock.
          </div>
        </div>

        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 800; color: #475569; margin-bottom: 8px; letter-spacing: 0.5px;">MOTIVO DEL AJUSTE <span style="color:#ef4444">*</span></label>
          <textarea id="swal-input-motivo" 
                    style="width: 100%; box-sizing: border-box; padding: 12px 15px; border: 2px solid #cbd5e1; border-radius: 10px; background-color: #ffffff; font-size: 0.95rem; font-family: inherit; color: #0f172a; outline: none; resize: vertical; min-height: 85px; transition: border-color 0.2s;" 
                    placeholder="Ej: Producto roto, mercadería de regalo, ajuste de inventario..."
                    onfocus="this.style.borderColor='#0ea5e9'" onblur="this.style.borderColor='#cbd5e1'"></textarea>
        </div>
      </div>
    `,
    showCancelButton: true,
    confirmButtonText: 'Confirmar Ajuste',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#10b981',
    customClass: { popup: 'swal-rounded-popup', cancelButton: 'swal-cancel-btn-custom' },
    
    didOpen: () => {
      const input = document.getElementById('swal-input-diferencia');
      const label = document.getElementById('swal-resultado-label');
      
      input.addEventListener('input', (e) => {
        const valorAgregado = parseInt(e.target.value);
        if (isNaN(valorAgregado)) {
          label.innerHTML = "Ingresá un valor para ver cómo quedará el stock.";
          label.style.background = "#e0f2fe";
          label.style.borderColor = "#bae6fd";
          return;
        }
        
        const stockFinalCalculado = stockActual + valorAgregado;
        if (stockFinalCalculado < 0) {
          label.innerHTML = `⚠️ ERROR: El stock no puede quedar negativo (Quedaría en ${stockFinalCalculado}).`;
          label.style.background = "#fef2f2";
          label.style.color = "#dc2626";
          label.style.borderColor = "#fecaca";
        } else {
          const operacion = valorAgregado > 0 ? 'SUMARÁN' : 'RESTARÁN';
          label.innerHTML = `✅ Se <b>${operacion}</b> unidades. Stock final quedará en: <strong style="color:#059669; font-size:1.1rem;">${stockFinalCalculado} u.</strong>`;
          label.style.background = "#ecfdf5";
          label.style.color = "#065f46";
          label.style.borderColor = "#a7f3d0";
        }
      });
    },

    preConfirm: () => {
      const diferencia = parseInt(document.getElementById('swal-input-diferencia').value);
      const motivo = document.getElementById('swal-input-motivo').value.trim();
      
      if (isNaN(diferencia)) {
        Swal.showValidationMessage('❌ Ingresá la cantidad que querés sumar o restar.');
        return false;
      }

      const stockFinalCalculado = stockActual + diferencia;
      if (stockFinalCalculado < 0) {
        Swal.showValidationMessage(`❌ El stock resultante no puede ser negativo (${stockFinalCalculado}).`);
        return false;
      }

      if (!motivo || motivo.length < 5) {
        Swal.showValidationMessage('❌ Debe detallar un motivo válido (mínimo 5 caracteres).');
        return false;
      }
      return { nuevo_stock: stockFinalCalculado, motivo: motivo };
    }
  });

  if (formValues) {
    try {
      Swal.fire({ title: 'Actualizando sistema...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
      const token = localStorage.getItem('token');
      await axios.post(`${API_BASE}/api/productos/${producto.id}/ajustar-stock/`, formValues, {
        headers: { Authorization: `Token ${token}` }
      });
      
      Swal.fire({ icon: 'success', title: '¡Inventario Actualizado!', text: 'El ajuste se registró en la auditoría.', confirmButtonColor: '#10b981' });
      producto.stock_actual = parseInt(formValues.nuevo_stock); 
    } catch (error) {
      Swal.fire('Error', error.response?.data?.error || 'No se pudo actualizar.', 'error');
    }
  }
};

// 🔥 FUNCIÓN PARA ABRIR HISTORIAL
const abrirHistorialStock = async (producto) => {
  productoEditando.value = producto;
  mostrarHistorial.value = true;
  cargandoHistorial.value = true;
  paginaHistorial.value = 1; // Reseteamos la página al abrir
  
  try {
    const token = localStorage.getItem('token');
    const res = await axios.get(`${API_BASE}/api/productos/${producto.id}/historial-stock/`, {
      headers: { Authorization: `Token ${token}` }
    });
    historialStock.value = res.data || [];
  } catch (error) {
    console.error("Error al cargar historial:", error);
    Swal.fire('Error', 'No se pudo cargar la auditoría del producto.', 'error');
    mostrarHistorial.value = false;
  } finally {
    cargandoHistorial.value = false;
  }
}

const cerrarModalHistorial = () => {
  mostrarHistorial.value = false;
  historialStock.value = [];
  productoEditando.value = null;
}

const editarProducto = (p) => { productoEditando.value = p; mostrarEditar.value = true }
const productoRegistrado = async () => { await cargarProductos(); cerrarModal(); pagina.value = 1 }
const productoActualizado = async () => { await cargarProductos(); cerrarModalEditar() }

const cambiarEstadoProducto = async (producto) => {
  const nuevo = producto.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'
  const res = await Swal.fire({ title: `¿Cambiar a ${nuevo}?`, icon: 'question', showCancelButton: true })
  if (!res.isConfirmed) return
  
  try {
    await axios.patch(`/usuarios/api/productos/${producto.id}/`, { estado: nuevo })
    await cargarProductos()
    Swal.fire('¡Listo!', 'Estado actualizado', 'success')
  } catch (e) { Swal.fire('Error', 'No se pudo cambiar', 'error') }
}

const limpiarFiltros = () => { filtros.value = { busqueda: '', categoria: '', stockBajo: '', marca: '', estado: '' } }
const cerrarModal = () => mostrarRegistrar.value = false
const cerrarModalEditar = () => mostrarEditar.value = false
const cerrarModalMarca = () => mostrarRegistrarMarca.value = false
const marcaRegistrada = async () => { cerrarModalMarca(); await cargarAuxiliares() }

watch(filtros, () => { pagina.value = 1 }, { deep: true })

onMounted(async () => {
  cargando.value = true
  await cargarAuxiliares()
  await cargarProductos()
  cargando.value = false
  if (route.query.filtro === 'stock_bajo') filtros.value.stockBajo = 'si'
})
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - PRODUCTOS
   ======================================== */

.list-container { padding: 32px; max-width: 1600px; margin: 0 auto; min-height: 100vh; font-family: 'Inter', sans-serif; }
.list-card { background: var(--bg-secondary); color: var(--text-primary); border-radius: 24px; padding: 40px; width: 100%; max-width: 1600px; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; transition: all 0.4s ease; border: 1px solid var(--border-color); }
.list-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9); border-radius: 24px 24px 0 0; }

.badge-estado { padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; letter-spacing: 0.5px; white-space: nowrap; }
.estado-warning { background: var(--bg-tertiary); color: #f59e0b; border: 2px solid #f59e0b; box-shadow: 0 0 12px rgba(245, 158, 11, 0.3); }
.estado-info { background: var(--bg-tertiary); color: #0ea5e9; border: 2px solid #0ea5e9; box-shadow: 0 0 12px rgba(14, 165, 233, 0.3); }
.estado-success { background: var(--bg-tertiary); color: #10b981; border: 2px solid #10b981; box-shadow: 0 0 12px rgba(16, 185, 129, 0.3); }
.estado-danger { background: var(--bg-tertiary); color: var(--error-color); border: 2px solid var(--error-color); box-shadow: 0 0 12px rgba(239, 68, 68, 0.3); text-decoration: line-through; opacity: 0.75; }
.estado-secondary { background: var(--bg-tertiary); color: var(--text-tertiary); border: 2px solid var(--text-tertiary); box-shadow: 0 0 8px rgba(156, 163, 175, 0.2); }

.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; flex-wrap: wrap; gap: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 25px; }
.header-content h1 { margin: 0; font-size: 2.2rem; background: linear-gradient(135deg, var(--text-primary), #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; }
.header-content p { color: var(--text-secondary); font-weight: 500; margin-top: 8px; letter-spacing: 0.5px; }

/* 🔥 ESTILOS PARA LOS BOTONES NUEVOS DE STOCK Y AUDITORÍA */
.action-button.stock-btn { background: var(--bg-tertiary, #f8fafc); border: 1px solid #8b5cf6; color: #8b5cf6; transition: all 0.3s ease; }
.action-button.stock-btn:hover { background: #f5f3ff; border-color: #7c3aed; color: #7c3aed; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3); }

.action-button.historial-btn { background: var(--bg-tertiary, #f8fafc); border: 1px solid #0ea5e9; color: #0ea5e9; transition: all 0.3s ease; }
.action-button.historial-btn:hover { background: #f0f9ff; border-color: #0284c7; color: #0284c7; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3); }

.register-button { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; font-size: 0.95rem; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35); position: relative; overflow: hidden; display: flex; align-items: center; gap: 8px; }
.register-button::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent); transition: left 0.5s; }
.register-button:hover::before { left: 100%; }
.register-button:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5); background: linear-gradient(135deg, #0284c7, #0369a1); }

.filters-container { margin-bottom: 30px; background: var(--hover-bg); padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; align-items: end; }
.filter-group { display: flex; flex-direction: column; }
.filter-group label { font-weight: 700; margin-bottom: 10px; color: var(--text-secondary); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }
.filter-input, .filter-select { padding: 12px 14px; border: 2px solid var(--border-color); border-radius: 10px; background: var(--bg-primary); color: var(--text-primary); transition: all 0.3s ease; font-weight: 500; font-size: 0.95rem; }
.filter-input:focus, .filter-select:focus { outline: none; border-color: var(--accent-color); box-shadow: 0 0 0 4px var(--accent-light); background: var(--bg-secondary); }
.clear-filters-btn { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 18px; border-radius: 10px; cursor: pointer; font-weight: 700; transition: all 0.3s ease; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.8px; display: flex; align-items: center; gap: 6px; }
.clear-filters-btn:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }

.table-container { overflow-x: auto; margin-bottom: 25px; border-radius: 16px; }
.users-table { width: 100%; border-collapse: collapse; background: var(--bg-primary); border-radius: 16px; overflow: hidden; box-shadow: var(--shadow-md); border: 1px solid var(--border-color); }
.users-table th { background: var(--accent-color); color: white; padding: 16px 12px; text-align: left; font-weight: 900; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; white-space: nowrap; }
.users-table tr { border-bottom: 1px solid var(--border-color); }
.users-table td { padding: 12px; vertical-align: middle; color: var(--text-secondary); font-weight: 500; font-size: 0.9rem; }
.users-table td strong { color: var(--text-primary); font-weight: 800; letter-spacing: 0.3px; }
.users-table tr:hover { background: var(--hover-bg); transition: all 0.2s ease; }

.nombre-cell { max-width: 160px; overflow-x: auto; white-space: nowrap; scrollbar-width: thin; }
.nombre-cell::-webkit-scrollbar { height: 4px; }
.nombre-cell::-webkit-scrollbar-thumb { background-color: var(--border-color); border-radius: 4px; }
.nombre-cell::-webkit-scrollbar-track { background: transparent; }

.stock-bajo-row { background: rgba(245, 158, 11, 0.05); border-left: 3px solid #f59e0b; }

.proveedores-lista { max-width: 150px; }
.proveedor-item { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid var(--border-color); }
.proveedor-item:last-child { border-bottom: none; }
.proveedor-nombre { color: var(--text-primary); font-size: 0.8rem; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 8px; }
.mas-proveedores { color: var(--text-tertiary); font-size: 0.75rem; font-style: italic; text-align: center; padding: 4px 0; background: var(--hover-bg); border-radius: 4px; margin-top: 4px; }
.sin-proveedores { color: var(--text-tertiary); font-size: 0.8rem; font-style: italic; text-align: center; padding: 6px 0; }

.action-buttons { display: flex; gap: 6px; }
.action-button { padding: 8px; border: none; border-radius: 10px; font-size: 0.8rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; width: 36px; height: 36px; }
.action-button.edit { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); }
.action-button.edit:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.action-button.delete { background: var(--bg-tertiary); border: 1px solid var(--error-color); color: var(--error-color); }
.action-button.delete:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4); border-color: var(--error-color); }
.action-button.success { background: var(--bg-tertiary); border: 1px solid #10b981; color: #10b981; }
.action-button.success:hover { background: var(--hover-bg); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4); border-color: #10b981; }

.usuarios-count { display: flex; justify-content: space-between; align-items: center; margin: 25px 0; padding: 18px; background: var(--hover-bg); border-radius: 12px; flex-wrap: wrap; gap: 15px; border: 1px solid var(--border-color); }
.usuarios-count p { color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; margin: 0; display: flex; align-items: center; gap: 8px; }
.alertas-container { display: flex; gap: 10px; flex-wrap: wrap; }
.alerta-stock { background: var(--bg-tertiary); color: #f59e0b; border: 2px solid #f59e0b; padding: 8px 16px; border-radius: 20px; font-weight: 700; letter-spacing: 0.5px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; }
.alerta-inactivo { background: var(--bg-tertiary); color: #ef4444; border: 2px solid #ef4444; padding: 8px 16px; border-radius: 20px; font-weight: 700; letter-spacing: 0.5px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; }

.animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.no-results { text-align: center; padding: 80px; color: var(--text-secondary); }
.no-results-icon { margin-bottom: 15px; opacity: 0.5; color: var(--text-tertiary); }
.no-results p { margin: 0 0 8px 0; font-size: 1.1em; color: var(--text-primary); }
.no-results small { font-size: 0.9em; color: var(--text-tertiary); }

.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 25px; }
.pagination button { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 800; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }
.pagination button:hover:not(:disabled) { background: var(--hover-bg); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.pagination button:disabled { background: var(--bg-tertiary); color: var(--text-tertiary); cursor: not-allowed; transform: none; border: 1px solid var(--border-color); opacity: 0.5; }
.pagination span { color: var(--text-primary); font-weight: 700; letter-spacing: 0.8px; font-size: 0.95rem; }

.overlay-activo { opacity: 0.3; filter: blur(5px); pointer-events: none; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.88); backdrop-filter: blur(12px); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeInModal 0.3s ease; }
@keyframes fadeInModal { from { opacity: 0; } to { opacity: 1; } }
.modal-content { position: relative; animation: slideUp 0.3s ease; max-height: 85vh; max-width: 90vw; width: auto; overflow-y: auto; border-radius: 16px; background: var(--bg-secondary); box-shadow: var(--shadow-lg); border: 2px solid var(--border-color); padding: 0; margin: 20px; }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }

/* 🔥 ESTILOS PARA EL MODAL DEL HISTORIAL */
.modal-historial { width: 1200px; max-width: 96vw; padding: 0; background: var(--bg-primary) }
.historial-header { padding: 25px 30px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 16px 16px 0 0; }
.historial-header h2 { margin: 0 0 5px 0; color: var(--text-primary); font-size: 1.5rem; font-weight: 800; }
.historial-header p { margin: 0; color: var(--text-secondary); font-size: 1rem; }
.historial-body { padding: 20px; max-height: 60vh; overflow-y: auto; }

.badge-positivo { background: #d1fae5; color: #059669; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.9rem; }
.badge-negativo { background: #fee2e2; color: #dc2626; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.9rem; }

.modal-close { position: absolute; top: 20px; right: 20px; background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-secondary); border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; z-index: 10; }
.modal-close:hover { background: var(--error-color); color: white; border-color: var(--error-color); transform: rotate(90deg); }

.modal-content::-webkit-scrollbar, .table-container::-webkit-scrollbar, .historial-body::-webkit-scrollbar { width: 8px; height: 8px; }
.modal-content::-webkit-scrollbar-track, .table-container::-webkit-scrollbar-track, .historial-body::-webkit-scrollbar-track { background: var(--bg-primary); border-radius: 4px; }
.modal-content::-webkit-scrollbar-thumb, .table-container::-webkit-scrollbar-thumb, .historial-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
.modal-content::-webkit-scrollbar-thumb:hover, .table-container::-webkit-scrollbar-thumb:hover, .historial-body::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* FIX PARA EL MODAL SWAL: Que los botones no queden transparentes */
:deep(.swal-rounded-popup) { border-radius: 20px !important; padding: 1.5rem !important; }
:deep(.swal-cancel-btn-custom) { background-color: #f1f5f9 !important; color: #475569 !important; font-weight: 700 !important; }

@media (max-width: 768px) {
  .list-card { padding: 25px; border-radius: 20px; }
  .list-header { flex-direction: column; align-items: flex-start; }
  .header-content h1 { font-size: 1.6rem; }
  .filters-grid { grid-template-columns: 1fr; }
  .modal-content { max-width: 95vw; margin: 12px; border-radius: 12px; }
  .users-table { font-size: 0.85rem; }
  .users-table th { font-size: 0.7rem; padding: 14px 10px; }
  .action-buttons { flex-direction: column; gap: 6px; }
  .usuarios-count { flex-direction: column; align-items: flex-start; gap: 10px; }
  .alertas-container { flex-direction: column; width: 100%; }
  .pagination { flex-direction: column; gap: 12px; }
}

@media (max-width: 480px) {
  .list-card { padding: 18px; border-radius: 16px; }
  .header-content h1 { font-size: 1.4rem; }
  .users-table { display: block; overflow-x: auto; white-space: nowrap; }
  .filter-input, .filter-select { font-size: 0.9rem; }
  .badge-estado { font-size: 0.65rem; padding: 5px 10px; }
  .action-button { width: 36px; height: 36px; }
  .header-buttons { flex-direction: column; width: 100%; }
  .register-button { width: 100%; justify-content: center; }
}
</style>