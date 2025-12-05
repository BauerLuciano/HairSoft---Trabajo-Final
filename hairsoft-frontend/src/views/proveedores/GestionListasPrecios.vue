<template>
  <!-- FONDO DEGRADADO -->
  <div class="page-background">
    <!-- TARJETA BLANCA QUE ENVUELVE TODO -->
    <div class="main-card-container">
      <div class="pricing-container">
        <!-- HEADER -->
        <div class="header-section">
          <div class="header-content">
            <h2>
              Listas de Precios por Proveedor
            </h2>
            <p class="header-subtitle">Gestión de precios base y márgenes de ganancia</p>
          </div>
          <button 
            @click="abrirFormulario" 
            class="btn-primary"
            :disabled="!proveedorSeleccionado"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Agregar Productos
          </button>
        </div>

        <!-- SELECTOR DE PROVEEDOR -->
        <div class="card-modern slide-in">
          <div class="card-header">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
            <h3>Seleccionar Proveedor</h3>
          </div>
          
          <div class="input-group">
            <label class="label-modern">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              Proveedor
            </label>
            <select 
              v-model="proveedorSeleccionado" 
              @change="cargarListasPrecios"
              class="select-modern"
            >
              <option value="">-- Seleccionar proveedor --</option>
              <option 
                v-for="proveedor in proveedores" 
                :key="proveedor.id" 
                :value="proveedor.id"
              >
                {{ proveedor.nombre }} - {{ proveedor.contacto }}
              </option>
            </select>
          </div>
        </div>

        <!-- LISTA DE PRECIOS -->
        <div v-if="proveedorSeleccionado && listasPrecios.length > 0" class="card-modern slide-in">
          <div class="card-header">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 1v22M17 5H9.5a3.5 3.5 0 1 0 0 7h5a3.5 3.5 0 1 1 0 7H6"/>
              </svg>
            </div>
            <h3>Listas de Precios Activas</h3>
            <span class="badge-count">
              {{ listasPrecios.filter(l => l.activo).length }} / {{ listasPrecios.length }}
            </span>
          </div>

          <div class="table-container">
            <div class="table-responsive">
              <table class="table-modern">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Precio Base</th>
                    <th>Margen %</th>
                    <th>Precio Sugerido</th>
                    <th>Estado</th>
                    <th>Última Actualización</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="lista in listasPrecios" :key="lista.id" :class="{ 'row-inactive': !lista.activo }">
                    <td>
                      <div class="producto-info">
                        <strong class="producto-nombre">{{ lista.producto_nombre }}</strong>
                        <small class="codigo-producto">Cód: {{ lista.producto_codigo || 'N/A' }}</small>
                      </div>
                    </td>
                    <td class="precio-cell">
                      <span class="precio-base">${{ lista.precio_base }}</span>
                    </td>
                    <td>
                      <span class="margen-badge" :class="getMargenClass(lista.margen_ganancia)">
                        {{ lista.margen_ganancia }}%
                      </span>
                    </td>
                    <td class="precio-cell">
                      <span class="precio-sugerido">${{ lista.precio_sugerido_venta }}</span>
                    </td>
                    <td>
                      <span class="status-badge" :class="lista.activo ? 'status-active' : 'status-inactive'">
                        {{ lista.activo ? 'ACTIVO' : 'INACTIVO' }}
                      </span>
                    </td>
                    <td>
                      <div class="fecha-actualizacion">
                        {{ formatFecha(lista.fecha_actualizacion) }}
                      </div>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button 
                          @click="editarLista(lista)" 
                          class="btn-action btn-edit"
                          :disabled="!lista.activo"
                          :title="lista.activo ? 'Editar' : 'No editable'"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                        </button>
                        <button 
                          @click="lista.activo ? desactivarLista(lista) : activarLista(lista)" 
                          class="btn-action"
                          :class="lista.activo ? 'btn-deactivate' : 'btn-activate'"
                          :title="lista.activo ? 'Desactivar' : 'Activar'"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle v-if="lista.activo" cx="12" cy="12" r="10"/>
                            <path v-if="lista.activo" d="M8 12l3 3 5-5"/>
                            <path v-else d="M18 6L6 18M6 6l12 12"/>
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ESTADOS VACÍOS -->
        <div v-if="!proveedorSeleccionado" class="card-modern empty-state">
          <div class="empty-state-content">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="empty-icon">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <h3>Selecciona un proveedor</h3>
            <p>👆 Elige un proveedor para ver sus listas de precios</p>
          </div>
        </div>

        <div v-else-if="listasPrecios.length === 0 && !cargando" class="card-modern empty-state">
          <div class="empty-state-content">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="empty-icon">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <h3>Sin listas de precios</h3>
            <p>Este proveedor no tiene listas de precios registradas</p>
            <button @click="abrirFormulario" class="btn-primary">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              Agregar Productos
            </button>
          </div>
        </div>

        <!-- FORMULARIO MÚLTIPLE DE PRODUCTOS -->
        <div v-if="mostrarFormulario" class="modal-overlay" @click.self="cerrarModal">
          <div class="modal-content">
            <div class="form-card">
              <div class="form-header">
                <div class="form-icon-title">
                  <div class="card-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 1v22M17 5H9.5a3.5 3.5 0 1 0 0 7h5a3.5 3.5 0 1 1 0 7H6"/>
                    </svg>
                  </div>
                  <h2>📦 Agregar Productos a {{ proveedorSeleccionadoNombre }}</h2>
                </div>
                <button @click="cerrarModal" class="modal-close-btn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <!-- TABLA PARA MÚLTIPLES PRODUCTOS -->
              <div class="form-section">
                <div class="section-header">
                  <h4>Productos Disponibles</h4>
                  <div class="header-actions">
                    <button @click="agregarFilaProducto" class="btn-secondary">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 5v14M5 12h14"/>
                      </svg>
                      Agregar Fila
                    </button>
                    <small class="hint-text">Disponibles: {{ productosSinLista.length }}</small>
                  </div>
                </div>

                <div class="table-responsive">
                  <table class="form-table">
                    <thead>
                      <tr>
                        <th>Producto</th>
                        <th>Precio Base</th>
                        <th>Margen %</th>
                        <th>Precio Sugerido</th>
                        <th>Precio Final</th>
                        <th style="width: 60px;"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(fila, index) in filasProductos" :key="index" class="fila-producto">
                        <td>
                          <select v-model="fila.producto_id" @change="onProductoSeleccionado(fila)" 
                                  class="select-modern small" :class="{ 'error': esProductoDuplicado(fila.producto_id, index) }">
                            <option value="">-- Seleccionar --</option>
                            <option 
                              v-for="producto in productosSinLista" 
                              :key="producto.id" 
                              :value="producto.id"
                              :disabled="esProductoSeleccionado(producto.id, index)"
                            >
                              {{ producto.nombre }}
                            </option>
                          </select>
                          <small v-if="esProductoDuplicado(fila.producto_id, index)" class="error-message">
                            Producto ya seleccionado
                          </small>
                        </td>
                        <td>
                          <div class="input-with-icon">
                            <span class="input-icon">$</span>
                            <input 
                              v-model.number="fila.precio_base" 
                              type="number" 
                              step="0.01" 
                              min="0"
                              placeholder="0.00"
                              class="input-modern small"
                              @input="actualizarPrecioFinal(fila)"
                            />
                          </div>
                        </td>
                        <td>
                          <div class="input-with-icon">
                            <input 
                              v-model.number="fila.margen_ganancia" 
                              type="number" 
                              step="0.1" 
                              min="0"
                              max="100"
                              placeholder="30.0"
                              class="input-modern small"
                              @input="actualizarPrecioFinal(fila)"
                            />
                            <span class="input-icon">%</span>
                          </div>
                        </td>
                        <td>
                          <div class="suggested-price">
                            ${{ calcularPrecioSugeridoFila(fila) }}
                          </div>
                        </td>
                        <td>
                          <div class="input-with-icon">
                            <span class="input-icon">$</span>
                            <input 
                              v-model.number="fila.precio_final" 
                              type="number" 
                              step="0.01" 
                              min="0"
                              placeholder="0.00"
                              class="input-modern small final-price"
                              @input="actualizarMargenDesdePrecioFinal(fila)"
                            />
                          </div>
                        </td>
                        <td>
                          <button 
                            @click="eliminarFila(index)" 
                            class="btn-action btn-danger"
                            :disabled="filasProductos.length === 1"
                            title="Eliminar fila"
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="filasValidas.length > 0" class="form-summary">
                  <div class="summary-item">
                    <span>Productos válidos:</span>
                    <strong>{{ filasValidas.length }}</strong>
                  </div>
                  <div class="summary-item">
                    <span>Total estimado:</span>
                    <strong>${{ calcularTotalEstimado() }}</strong>
                  </div>
                </div>
              </div>

              <!-- BOTONES -->
              <div class="form-actions">
                <button type="button" @click="cerrarModal" class="btn-secondary">
                  Cancelar
                </button>
                <button @click="guardarListasMultiples" :disabled="guardando || filasValidas.length === 0" 
                        class="btn-primary" :class="{ 'loading': guardando }">
                  <span v-if="!guardando">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                      <polyline points="17 21 17 13 7 13 7 21"/>
                      <polyline points="7 3 7 8 15 8"/>
                    </svg>
                    Guardar {{ filasValidas.length }} Producto{{ filasValidas.length !== 1 ? 's' : '' }}
                  </span>
                  <span v-else>
                    <svg class="spinner" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10" stroke-opacity="0.3"/>
                      <path d="M12 2a10 10 0 0 1 10 10"/>
                    </svg>
                    Guardando...
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- LOADING STATE -->
        <div v-if="cargando" class="card-modern loading-state">
          <div class="loading-content">
            <svg class="spinner large" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-opacity="0.3"/>
              <path d="M12 2a10 10 0 0 1 10 10"/>
            </svg>
            <p>Cargando listas de precios...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

// Estados
const proveedores = ref([])
const productosDisponibles = ref([])
const proveedorSeleccionado = ref('')
const listasPrecios = ref([])
const mostrarFormulario = ref(false)
const cargando = ref(false)
const guardando = ref(false)

// Formulario múltiple
const filasProductos = ref([{ 
  producto_id: '', 
  precio_base: '', 
  margen_ganancia: 30.0,
  precio_final: '' 
}])

// Computed
const proveedorSeleccionadoNombre = computed(() => {
  const prov = proveedores.value.find(p => p.id === proveedorSeleccionado.value)
  return prov ? prov.nombre : ''
})

// Productos que NO tienen lista de precios activa
const productosSinLista = computed(() => {
  const productosConLista = listasPrecios.value
    .filter(lista => lista.activo)
    .map(lista => lista.producto)
  
  return productosDisponibles.value.filter(producto => 
    !productosConLista.includes(producto.id)
  )
})

// Validar si hay filas válidas
const filasValidas = computed(() => {
  return filasProductos.value.filter(fila => 
    fila.producto_id && fila.precio_base && fila.precio_base > 0 && !esProductoDuplicado(fila.producto_id, -1)
  )
})

// Métodos
const cargarProveedores = async () => {
  try {
    const response = await axios.get(`${API_BASE}/usuarios/api/proveedores/`)
    proveedores.value = response.data.filter(p => p.estado === 'ACTIVO')
  } catch (error) {
    console.error('Error cargando proveedores:', error)
    mostrarToast('Error al cargar proveedores', 'error')
  }
}

const cargarProductosDelProveedor = async (proveedorId) => {
  try {
    const response = await axios.get(`${API_BASE}/usuarios/api/productos/`)
    const todosProductos = response.data
    
    productosDisponibles.value = todosProductos.filter(producto => 
      producto.proveedores && producto.proveedores.includes(parseInt(proveedorId))
    )
  } catch (error) {
    console.error('Error cargando productos del proveedor:', error)
    mostrarToast('Error al cargar productos', 'error')
  }
}

const cargarListasPrecios = async () => {
  if (!proveedorSeleccionado.value) {
    listasPrecios.value = []
    productosDisponibles.value = []
    return
  }

  cargando.value = true
  try {
    await cargarProductosDelProveedor(proveedorSeleccionado.value)
    
    const response = await axios.get(`${API_BASE}/usuarios/api/listas-precios/por-proveedor/?proveedor_id=${proveedorSeleccionado.value}`)
    listasPrecios.value = response.data
  } catch (error) {
    console.error('Error cargando listas de precios:', error)
    listasPrecios.value = []
    mostrarToast('Error al cargar listas de precios', 'error')
  } finally {
    cargando.value = false
  }
}

const abrirFormulario = () => {
  if (!proveedorSeleccionado.value) {
    mostrarToast('Primero seleccioná un proveedor', 'warning')
    return
  }
  
  if (productosSinLista.value.length === 0) {
    mostrarToast('Este proveedor no tiene productos disponibles para agregar', 'warning')
    return
  }
  
  mostrarFormulario.value = true
}

// Métodos para el formulario mejorado
const agregarFilaProducto = () => {
  filasProductos.value.push({ 
    producto_id: '', 
    precio_base: '', 
    margen_ganancia: 30.0,
    precio_final: '' 
  })
}

const eliminarFila = (index) => {
  if (filasProductos.value.length > 1) {
    filasProductos.value.splice(index, 1)
  }
}

// Verificar si un producto ya está seleccionado en otra fila
const esProductoSeleccionado = (productoId, currentIndex) => {
  return filasProductos.value.some((fila, index) => 
    index !== currentIndex && fila.producto_id === productoId.toString()
  )
}

// Verificar si es producto duplicado
const esProductoDuplicado = (productoId, currentIndex) => {
  if (!productoId) return false
  return filasProductos.value.some((fila, index) => 
    index !== currentIndex && fila.producto_id === productoId.toString()
  )
}

const onProductoSeleccionado = (fila) => {
  actualizarPrecioFinal(fila)
}

const calcularPrecioSugeridoFila = (fila) => {
  const precioBase = parseFloat(fila.precio_base) || 0
  const margen = parseFloat(fila.margen_ganancia) || 0
  const precioCalculado = (precioBase * (1 + margen / 100)).toFixed(2)
  
  // Actualizar el precio final automáticamente
  if (!fila.precio_final) {
    fila.precio_final = precioCalculado
  }
  
  return precioCalculado
}

const actualizarPrecioFinal = (fila) => {
  fila.precio_final = calcularPrecioSugeridoFila(fila)
}

// Calcular margen cuando se edita el precio final
const actualizarMargenDesdePrecioFinal = (fila) => {
  const precioBase = parseFloat(fila.precio_base) || 0
  const precioFinal = parseFloat(fila.precio_final) || 0
  
  if (precioBase > 0 && precioFinal > 0) {
    const margenCalculado = ((precioFinal - precioBase) / precioBase) * 100
    fila.margen_ganancia = Math.max(0, Math.min(100, parseFloat(margenCalculado.toFixed(1))))
  }
}

// Calcular total estimado
const calcularTotalEstimado = () => {
  return filasValidas.value.reduce((total, fila) => {
    return total + (parseFloat(fila.precio_final) || 0)
  }, 0).toFixed(2)
}

const guardarListasMultiples = async () => {
  if (filasValidas.value.length === 0) {
    mostrarToast('Agregá al menos un producto con precio base válido', 'warning')
    return
  }

  guardando.value = true
  try {
    let exitosas = 0
    let errores = 0
    
    for (const fila of filasValidas.value) {
      try {
        const datos = {
          proveedor: proveedorSeleccionado.value,
          producto: fila.producto_id,
          precio_base: parseFloat(fila.precio_base),
          margen_ganancia: parseFloat(fila.margen_ganancia),
          activo: true
        }
        
        await axios.post(`${API_BASE}/usuarios/api/listas-precios/`, datos)
        exitosas++
      } catch (error) {
        console.error(`Error guardando producto ${fila.producto_id}:`, error.response?.data)
        errores++
        
        if (error.response?.status === 400) {
          const productoNombre = productosDisponibles.value.find(p => p.id == fila.producto_id)?.nombre
          mostrarToast(`❌ El producto "${productoNombre}" ya tiene una lista de precios activa`, 'error')
        }
      }
    }
    
    if (exitosas > 0) {
      mostrarToast(`✅ ${exitosas} productos agregados correctamente${errores > 0 ? `, ${errores} con errores` : ''}`, 'success')
      await cargarListasPrecios()
      cerrarModal()
    } else {
      mostrarToast('❌ No se pudo guardar ningún producto. Verifica que no estén duplicados.', 'error')
    }
    
  } catch (error) {
    console.error('Error general guardando listas:', error)
    mostrarToast('Error al guardar las listas de precios', 'error')
  } finally {
    guardando.value = false
  }
}

const editarLista = (lista) => {
  filasProductos.value = [{
    producto_id: lista.producto,
    precio_base: lista.precio_base,
    margen_ganancia: lista.margen_ganancia,
    precio_final: lista.precio_sugerido_venta
  }]
  mostrarFormulario.value = true
}

const desactivarLista = async (lista) => {
  if (!confirm(`¿Desactivar la lista de precios de ${lista.producto_nombre}?`)) return
  
  try {
    await axios.post(`${API_BASE}/usuarios/api/listas-precios/${lista.id}/desactivar/`)
    mostrarToast('Lista desactivada correctamente', 'success')
    await cargarListasPrecios()
  } catch (error) {
    console.error('Error desactivando lista:', error)
    mostrarToast('Error al desactivar la lista', 'error')
  }
}

const activarLista = async (lista) => {
  try {
    await axios.put(`${API_BASE}/usuarios/api/listas-precios/${lista.id}/`, {
      ...lista,
      activo: true
    })
    mostrarToast('Lista activada correctamente', 'success')
    await cargarListasPrecios()
  } catch (error) {
    console.error('Error activando lista:', error)
    mostrarToast('Error al activar la lista', 'error')
  }
}

const cerrarModal = () => {
  mostrarFormulario.value = false
  filasProductos.value = [{ 
    producto_id: '', 
    precio_base: '', 
    margen_ganancia: 30.0,
    precio_final: '' 
  }]
}

const formatFecha = (fecha) => {
  return fecha ? new Date(fecha).toLocaleDateString('es-AR') : '-'
}

const getMargenClass = (margen) => {
  if (margen < 20) return 'margen-low'
  if (margen < 40) return 'margen-medium'
  return 'margen-high'
}

const calcularPrecioPromedio = () => {
  const activas = listasPrecios.value.filter(l => l.activo)
  if (activas.length === 0) return '0.00'
  
  const total = activas.reduce((sum, lista) => sum + parseFloat(lista.precio_sugerido_venta), 0)
  return (total / activas.length).toFixed(2)
}

const calcularMargenPromedio = () => {
  const activas = listasPrecios.value.filter(l => l.activo)
  if (activas.length === 0) return '0.0'
  
  const total = activas.reduce((sum, lista) => sum + parseFloat(lista.margen_ganancia), 0)
  return (total / activas.length).toFixed(1)
}

const mostrarToast = (mensaje, tipo) => {
  // Implementar sistema de notificaciones si es necesario
  alert(mensaje)
}

// Inicialización
onMounted(() => {
  cargarProveedores()
})
</script>

<style scoped>
/* ============================================
   FONDO DE PÁGINA Y CONTENEDOR PRINCIPAL
   ============================================ */
.page-background {
  min-height: 100vh;
  padding: 30px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.main-card-container {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.pricing-container {
  width: 100%;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* ============================================
   HEADER
   ============================================ */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #1f2937, #374151);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.header-content h2 {
  margin: 0;
  color: white;
  font-size: 1.8em;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header-subtitle {
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8px;
  font-size: 1rem;
}

.header-icon {
  color: #60a5fa;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

/* ============================================
   BOTONES
   ============================================ */
.btn-primary {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 2px solid #d1d5db;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* ============================================
   CARDS MODERNAS
   ============================================ */
.card-modern {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.card-modern:hover {
  border-color: #3b82f6;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 12px;
  color: white;
  box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
}

.card-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3em;
  font-weight: 700;
  flex: 1;
  letter-spacing: -0.5px;
}

.badge-count {
  background: #10b981;
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* ============================================
   INPUTS Y SELECTS
   ============================================ */
.input-modern, .select-modern {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: #f8f9fa;
  font-size: 15px;
  transition: all 0.3s ease;
  color: #1f2937;
}

.input-modern:focus, .select-modern:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.select-modern {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 20px;
  padding-right: 50px;
  cursor: pointer;
}

.label-modern {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1f2937;
  font-size: 1rem;
}

.input-group {
  margin-bottom: 20px;
}

/* ============================================
   TABLA MODERNA
   ============================================ */
.table-responsive {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.table-modern {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.table-modern thead {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
}

.table-modern th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  white-space: nowrap;
}

.table-modern td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.table-modern tbody tr {
  transition: all 0.2s ease;
}

.table-modern tbody tr:hover {
  background: #f9fafb;
}

.table-modern tbody tr.row-inactive {
  opacity: 0.7;
  background: #f9fafb;
}

/* ============================================
   COMPONENTES DE TABLA
   ============================================ */
.producto-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.producto-nombre {
  font-weight: 600;
  color: #1f2937;
}

.codigo-producto {
  color: #6b7280;
  font-size: 0.85rem;
}

.precio-cell {
  font-weight: 600;
}

.precio-base {
  color: #3b82f6;
}

.precio-sugerido {
  color: #10b981;
}

.margen-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.margen-low {
  background: #fef3c7;
  color: #d97706;
}

.margen-medium {
  background: #dbeafe;
  color: #1d4ed8;
}

.margen-high {
  background: #dcfce7;
  color: #065f46;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-block;
}

.status-active {
  background: #dcfce7;
  color: #065f46;
}

.status-inactive {
  background: #f3f4f6;
  color: #6b7280;
}

.fecha-actualizacion {
  color: #6b7280;
  font-size: 0.9rem;
}

/* ============================================
   BOTONES DE ACCIÓN
   ============================================ */
.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-action {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-edit {
  background: #dbeafe;
  color: #1d4ed8;
}

.btn-edit:hover:not(:disabled) {
  background: #bfdbfe;
}

.btn-deactivate {
  background: #fee2e2;
  color: #dc2626;
}

.btn-deactivate:hover:not(:disabled) {
  background: #fecaca;
}

.btn-activate {
  background: #dcfce7;
  color: #065f46;
}

.btn-activate:hover:not(:disabled) {
  background: #bbf7d0;
}

.btn-danger {
  background: #fee2e2;
  color: #dc2626;
}

.btn-danger:hover:not(:disabled) {
  background: #fecaca;
}

/* ============================================
   RESUMEN DE PRECIOS
   ============================================ */
.resumen-precios {
  display: flex;
  gap: 30px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  margin-top: 20px;
  border: 1px solid #e5e7eb;
}

.resumen-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.resumen-item span {
  color: #6b7280;
  font-size: 0.9rem;
}

.resumen-item strong {
  color: #1f2937;
  font-size: 1.2rem;
  font-weight: 700;
}

/* ============================================
   ESTADOS VACÍOS
   ============================================ */
.empty-state {
  text-align: center;
  padding: 60px 40px;
  background: #f8fafc;
  border: 2px dashed #d1d5db;
}

.empty-state-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.empty-icon {
  color: #9ca3af;
  opacity: 0.5;
}

.empty-state h3 {
  color: #374151;
  margin: 0;
}

.empty-state p {
  color: #6b7280;
  margin: 0;
}

/* ============================================
   MODAL
   ============================================ */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 24px;
  padding: 32px;
  max-width: 1200px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.1);
  animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.form-card {
  width: 100%;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.form-icon-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.form-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
}

.modal-close-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close-btn:hover {
  background: #e5e7eb;
}

/* ============================================
   FORMULARIO
   ============================================ */
.form-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 1.2rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hint-text {
  color: #6b7280;
  font-size: 0.9rem;
}

/* ============================================
   TABLA DEL FORMULARIO
   ============================================ */
.form-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.form-table th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  background: #f8fafc;
  border-bottom: 2px solid #e5e7eb;
}

.form-table td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.fila-producto {
  transition: all 0.2s ease;
}

.fila-producto:hover {
  background: #f9fafb;
}

.input-modern.small, .select-modern.small {
  padding: 10px 12px;
  font-size: 14px;
}

.select-modern.small {
  padding-right: 40px;
  background-size: 16px;
  background-position: right 12px center;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-icon .input-icon {
  position: absolute;
  left: 12px;
  color: #6b7280;
  font-weight: 600;
}

.input-with-icon:last-child .input-icon {
  left: auto;
  right: 12px;
}

.input-with-icon input {
  padding-left: 30px;
  padding-right: 30px;
}

.suggested-price {
  font-weight: 600;
  color: #10b981;
  font-size: 1rem;
}

.final-price {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}

.error-message {
  color: #dc2626;
  font-size: 0.8rem;
  margin-top: 4px;
  display: block;
}

.select-modern.error {
  border-color: #dc2626;
}

/* ============================================
   RESUMEN DEL FORMULARIO
   ============================================ */
.form-summary {
  display: flex;
  gap: 30px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  margin-top: 20px;
  border: 1px solid #e5e7eb;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item span {
  color: #6b7280;
  font-size: 0.9rem;
}

.summary-item strong {
  color: #1f2937;
  font-size: 1.2rem;
  font-weight: 700;
}

/* ============================================
   ACCIONES DEL FORMULARIO
   ============================================ */
.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

/* ============================================
   LOADING STATES
   ============================================ */
.loading-state {
  text-align: center;
  padding: 60px 40px;
  background: #f8fafc;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  animation: spin 1s linear infinite;
}

.spinner.large {
  width: 48px;
  height: 48px;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

.btn-primary.loading {
  opacity: 0.8;
  cursor: wait;
}

/* ============================================
   ANIMACIONES
   ============================================ */
.slide-in {
  animation: slideInRight 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideInRight {
  from {
    transform: translateX(30px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .main-card-container {
    padding: 30px;
    margin: 20px;
  }
  
  .resumen-precios {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .page-background {
    padding: 20px 15px;
  }
  
  .main-card-container {
    padding: 25px;
    border-radius: 20px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-summary {
    flex-direction: column;
    gap: 20px;
  }
  
  .modal-content {
    padding: 24px;
    width: 95%;
  }
}

@media (max-width: 480px) {
  .page-background {
    padding: 15px 10px;
  }
  
  .main-card-container {
    padding: 20px;
    border-radius: 16px;
  }
  
  .card-modern {
    padding: 20px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-icon {
    width: 40px;
    height: 40px;
  }
  
  .form-table th,
  .form-table td {
    padding: 12px 8px;
    font-size: 0.9rem;
  }
}
</style>