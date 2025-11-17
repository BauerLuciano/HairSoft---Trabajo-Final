<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>🎯 Listas de Precios por Proveedor</h1>
          <p>Gestión de precios base y márgenes de ganancia</p>
        </div>
        <button 
          @click="abrirFormulario" 
          class="register-button"
          :disabled="!proveedorSeleccionado"
        >
          ➕ Agregar Productos
        </button>
      </div>

      <!-- Selector de Proveedor -->
      <div class="filters-container">
        <div class="filter-group">
          <label>Seleccionar Proveedor</label>
          <select 
            v-model="proveedorSeleccionado" 
            @change="cargarListasPrecios"
            class="filter-select"
          >
            <option value="">Seleccione un proveedor</option>
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

      <!-- Lista de Precios -->
      <div v-if="proveedorSeleccionado && listasPrecios.length > 0" class="table-container">
        <table class="users-table">
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
            <tr v-for="lista in listasPrecios" :key="lista.id">
              <td>
                <strong>{{ lista.producto_nombre }}</strong>
                <br>
                <small class="codigo-producto">Cód: {{ lista.producto_codigo || 'N/A' }}</small>
              </td>
              <td class="precio-base">${{ lista.precio_base }}</td>
              <td class="margen">{{ lista.margen_ganancia }}%</td>
              <td class="precio-sugerido">${{ lista.precio_sugerido_venta }}</td>
              <td>
                <span :class="lista.activo ? 'activo' : 'inactivo'">
                  {{ lista.activo ? 'ACTIVO' : 'INACTIVO' }}
                </span>
              </td>
              <td>{{ formatFecha(lista.fecha_actualizacion) }}</td>
              <td>
                <button 
                  @click="editarLista(lista)" 
                  class="action-button edit"
                  :disabled="!lista.activo"
                >
                  ✏️
                </button>
                <button 
                  @click="desactivarLista(lista)" 
                  class="action-button delete"
                  v-if="lista.activo"
                >
                  🗑️
                </button>
                <button 
                  @click="activarLista(lista)" 
                  class="action-button activate"
                  v-else
                >
                  🔄
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Estados vacíos -->
      <div v-if="!proveedorSeleccionado" class="no-results">
        <p>👆 Selecciona un proveedor para ver sus listas de precios</p>
      </div>

      <div v-else-if="listasPrecios.length === 0 && !cargando" class="no-results">
        <p>📝 Este proveedor no tiene listas de precios registradas</p>
        <button @click="abrirFormulario" class="btn-primary">
          ➕ Agregar Productos
        </button>
      </div>

      <!-- Formulario Múltiple de Productos -->
      <div v-if="mostrarFormulario" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal-content" style="max-width: 1000px;">
          <div class="form-card">
            <div class="form-header">
              <h2>📦 Agregar Productos a {{ proveedorSeleccionadoNombre }}</h2>
              <button @click="cerrarModal" class="modal-close">×</button>
            </div>

            <!-- Tabla para múltiples productos -->
            <div class="productos-agregar-table">
              <div class="table-header">
                <button @click="agregarFilaProducto" class="btn-agregar-fila">
                  ➕ Agregar Fila
                </button>
                <small class="hint-text">Productos disponibles: {{ productosSinLista.length }}</small>
              </div>

              <table class="tabla-productos">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Precio Base</th>
                    <th>Margen %</th>
                    <th>Precio Sugerido</th>
                    <th>Precio Final</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(fila, index) in filasProductos" :key="index">
                    <td>
                      <select v-model="fila.producto_id" @change="onProductoSeleccionado(fila)" class="select-producto">
                        <option value="">Seleccionar producto</option>
                        <option 
                          v-for="producto in productosSinLista" 
                          :key="producto.id" 
                          :value="producto.id"
                          :disabled="esProductoSeleccionado(producto.id, index)"
                        >
                          {{ producto.nombre }}
                          {{ esProductoSeleccionado(producto.id, index) ? ' (Ya seleccionado)' : '' }}
                        </option>
                      </select>
                    </td>
                    <td>
                      <input 
                        v-model.number="fila.precio_base" 
                        type="number" 
                        step="0.01" 
                        min="0"
                        placeholder="0.00"
                        class="input-precio"
                        @input="actualizarPrecioFinal(fila)"
                      />
                    </td>
                    <td>
                      <input 
                        v-model.number="fila.margen_ganancia" 
                        type="number" 
                        step="0.1" 
                        min="0"
                        max="100"
                        placeholder="30.0"
                        class="input-margen"
                        @input="actualizarPrecioFinal(fila)"
                      />
                    </td>
                    <td class="precio-sugerido-cell">
                      ${{ calcularPrecioSugeridoFila(fila) }}
                    </td>
                    <td>
                      <input 
                        v-model.number="fila.precio_final" 
                        type="number" 
                        step="0.01" 
                        min="0"
                        placeholder="0.00"
                        class="input-precio-final"
                        @input="actualizarMargenDesdePrecioFinal(fila)"
                      />
                    </td>
                    <td>
                      <button 
                        @click="eliminarFila(index)" 
                        class="btn-eliminar-fila"
                        :disabled="filasProductos.length === 1"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Botones -->
            <div class="form-actions">
              <button type="button" @click="cerrarModal" class="btn btn-secondary">
                Cancelar
              </button>
              <button @click="guardarListasMultiples" :disabled="guardando || filasValidas.length === 0" class="btn btn-primary">
                {{ guardando ? 'Guardando...' : `Guardar ${filasValidas.length} Productos` }}
              </button>
            </div>
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
    fila.producto_id && fila.precio_base && fila.precio_base > 0
  )
})

// Métodos
const cargarProveedores = async () => {
  try {
    const response = await axios.get(`${API_BASE}/usuarios/api/proveedores/`)
    proveedores.value = response.data.filter(p => p.estado === 'ACTIVO')
  } catch (error) {
    console.error('Error cargando proveedores:', error)
    alert('Error al cargar proveedores')
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
    alert('Error al cargar productos del proveedor')
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
  } finally {
    cargando.value = false
  }
}

// ✅ NUEVO: Método para abrir el formulario con validación
const abrirFormulario = () => {
  if (!proveedorSeleccionado.value) {
    alert('Primero seleccioná un proveedor')
    return
  }
  
  if (productosSinLista.value.length === 0) {
    alert('Este proveedor no tiene productos disponibles para agregar')
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

const guardarListasMultiples = async () => {
  if (filasValidas.value.length === 0) {
    alert('Agregá al menos un producto con precio base válido')
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
          activo: true  // ✅ CORREGIDO: AGREGADO ESTE CAMPO
        }
        
        await axios.post(`${API_BASE}/usuarios/api/listas-precios/`, datos)
        exitosas++
      } catch (error) {
        console.error(`Error guardando producto ${fila.producto_id}:`, error.response?.data)
        errores++
        
        if (error.response?.status === 400) {
          const productoNombre = productosDisponibles.value.find(p => p.id == fila.producto_id)?.nombre
          alert(`❌ El producto "${productoNombre}" ya tiene una lista de precios activa`)
        }
      }
    }
    
    if (exitosas > 0) {
      alert(`✅ ${exitosas} productos agregados correctamente${errores > 0 ? `, ${errores} con errores` : ''}`)
      await cargarListasPrecios()
      cerrarModal()
    } else {
      alert('❌ No se pudo guardar ningún producto. Verifica que no estén duplicados.')
    }
    
  } catch (error) {
    console.error('Error general guardando listas:', error)
    alert('Error al guardar las listas de precios')
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
    alert('Lista desactivada correctamente')
    await cargarListasPrecios()
  } catch (error) {
    console.error('Error desactivando lista:', error)
    alert('Error al desactivar la lista')
  }
}

const activarLista = async (lista) => {
  try {
    await axios.put(`${API_BASE}/usuarios/api/listas-precios/${lista.id}/`, {
      ...lista,
      activo: true
    })
    alert('Lista activada correctamente')
    await cargarListasPrecios()
  } catch (error) {
    console.error('Error activando lista:', error)
    alert('Error al activar la lista')
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

// Inicialización
onMounted(() => {
  cargarProveedores()
})
</script>

<style scoped>
/* Estilos base */
.list-container {
  margin-left: 250px;
  padding: 20px;
  min-height: 100vh;
}

.list-card {
  background: rgba(23, 23, 23, 0.8);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1800px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05) inset;
  position: relative;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.register-button {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.register-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filters-container {
  margin-bottom: 30px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-select {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #374151;
  background: rgba(17, 24, 39, 0.8);
  color: white;
  max-width: 400px;
}

/* Tabla de productos en modal */
.productos-agregar-table {
  margin: 20px 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.btn-agregar-fila {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.tabla-productos {
  width: 100%;
  border-collapse: collapse;
  background: rgba(17, 24, 39, 0.8);
  border-radius: 8px;
  overflow: hidden;
}

.tabla-productos th,
.tabla-productos td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #374151;
}

.tabla-productos th {
  background: #1f2937;
  font-weight: 600;
}

.select-producto,
.input-precio,
.input-margen {
  width: 100%;
  padding: 8px;
  border: 1px solid #4b5563;
  border-radius: 4px;
  background: rgba(31, 41, 55, 0.8);
  color: white;
}

.precio-sugerido-cell {
  font-weight: 600;
  color: #10b981;
}

.btn-eliminar-fila {
  background: #ef4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-eliminar-fila:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Estados */
.precio-base {
  font-weight: 600;
  color: #3b82f6;
}

.precio-sugerido {
  font-weight: 700;
  color: #10b981;
}

.margen {
  color: #6b7280;
  font-weight: 500;
}

.codigo-producto {
  color: #6b7280;
  font-size: 0.8rem;
}

.activo, .inactivo {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.activo {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.inactivo {
  color: #6b7280;
  background: rgba(107, 114, 128, 0.1);
}

.action-button {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  margin: 2px;
}

.action-button.edit {
  background: #3b82f6;
  color: white;
}

.action-button.delete {
  background: #ef4444;
  color: white;
}

.action-button.activate {
  background: #10b981;
  color: white;
}

.input-precio-final {
  width: 100%;
  padding: 8px;
  border: 1px solid #10b981;
  border-radius: 4px;
  background: rgba(16, 185, 129, 0.1);
  color: white;
  font-weight: 600;
}

.hint-text {
  color: #6b7280;
  font-size: 0.9rem;
}

.select-producto option:disabled {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* Estados vacíos */
.no-results {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  max-height: 85vh;
  max-width: 90vw;
  overflow-y: auto;
  border-radius: 16px;
  background: rgba(23, 23, 23, 0.98);
  box-shadow: 0 20px 40px rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 0;
  margin: 20px;
}

.form-card {
  padding: 30px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-close {
  background: #ef4444;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  background: #10b981;
  color: white;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .list-container {
    margin-left: 80px;
    padding: 10px;
  }
  
  .list-card {
    padding: 20px;
  }
  
  .list-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .modal-content {
    margin: 10px;
    max-width: 95vw;
  }
}
</style>