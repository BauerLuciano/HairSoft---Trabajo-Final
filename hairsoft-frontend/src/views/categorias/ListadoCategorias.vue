<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Gestión de categorías</h1>
          <p>Gestión completa de categorías de servicios y productos</p>
        </div>
        <button @click="abrirModalCrear" class="register-button">
          <span class="btn-text">➕ Registrar Categoría</span>
        </button>
      </div>

      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" type="text" placeholder="Nombre..." class="filter-input" />
          </div>
          <div class="filter-group">
            <label>Tipo</label>
            <select v-model="filtros.tipo" class="filter-select">
              <option value="">Todos</option>
              <option value="Servicio">Servicio</option>
              <option value="Producto">Producto</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Estado</label>
            <select v-model="filtros.estado" class="filter-select">
              <option value="todos">Todos</option>
              <option value="activos">Solo Activos</option>
              <option value="inactivos">Solo Inactivos</option>
            </select>
          </div>
          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar</button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="categories-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Tipo</th>
              <th>Estado</th> 
              <th style="width: 120px; text-align: center;">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in categoriasPaginadas" :key="cat.id + cat.tipo" :class="{'row-inactiva': !cat.activo}">
              <td><strong>{{ cat.nombre }}</strong></td>
              <td class="descripcion-cell">{{ cat.descripcion || 'Sin descripción' }}</td>
              <td>
                <span class="badge-tipo" :class="getTipoClass(cat.tipo)">{{ cat.tipo }}</span>
              </td>
              <td>
                <span class="badge-estado" :class="cat.activo ? 'estado-success' : 'estado-danger'">
                  {{ cat.activo ? 'ACTIVO' : 'INACTIVO' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="abrirModalEditar(cat)" class="action-button edit" title="Editar">
                    <Edit3 :size="14" />
                  </button>

                  <button 
                    @click="toggleEstado(cat)" 
                    :class="['action-button', cat.activo ? 'delete' : 'activate']" 
                    :title="cat.activo ? 'Desactivar' : 'Activar'"
                  >
                    <Trash2 v-if="cat.activo" :size="14" />
                    <CheckCircle v-else :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="categoriasPaginadas.length === 0" class="no-results">
          <p>No se encontraron categorías</p>
          <button @click="limpiarFiltros" class="clear-filters-btn">Limpiar filtros</button>
        </div>
      </div>

      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1" class="pagination-btn">← Anterior</button>
        <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="pagination-btn">Siguiente →</button>
      </div>
    </div>

    <div v-if="modalVisible" class="modal-backdrop">
      <div class="modal-card">
        <h2>{{ form.id ? 'Editar Categoría' : 'Registrar Categoría' }}</h2>
        <form @submit.prevent="guardarCategoria">
          <div class="form-group">
            <label>Nombre:</label>
            <input v-model="form.nombre" type="text" class="modal-input" required />
            <span class="error" v-if="errores.nombre">{{ errores.nombre }}</span>
          </div>
          <div class="form-group">
            <label>Descripción:</label>
            <input v-model="form.descripcion" type="text" class="modal-input" />
          </div>
          <div class="form-group">
            <label>Tipo:</label>
            <select v-model="form.tipo" class="modal-input" :disabled="form.id !== null">
              <option value="">-- Seleccione --</option>
              <option value="Servicio">Servicio</option>
              <option value="Producto">Producto</option>
            </select>
          </div>
          <div v-if="form.id" class="form-group-checkbox">
             <label class="switch-container">
                <input type="checkbox" v-model="form.activo">
                <span class="switch-label">¿Categoría Activa?</span>
             </label>
          </div>

          <div class="modal-actions">
            <button type="submit" class="modal-btn primary">{{ form.id ? 'Actualizar' : 'Crear' }}</button>
            <button type="button" @click="cerrarModal" class="modal-btn secondary">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { Edit3, Trash2, CheckCircle } from 'lucide-vue-next'

const API_BASE = 'http://127.0.0.1:8000';

const categorias = ref([])
// 🔥 CAMBIO: Estado 'todos' para ver las 11 manicuras de entrada
const filtros = ref({ busqueda: '', tipo: '', estado: 'todos' }) 
const pagina = ref(1)
const itemsPorPagina = 8
const modalVisible = ref(false)

const form = reactive({ 
  id: null, nombre: '', descripcion: '', tipo: '', activo: true 
})

const errores = reactive({ nombre: '' })

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { headers: { Authorization: `Token ${token}` } } : {};
}

const cargarCategorias = async () => {
  try {
    const [resS, resP] = await Promise.all([
      axios.get(`${API_BASE}/api/categorias/servicios/`, getHeaders()),
      axios.get(`${API_BASE}/api/categorias/productos/`, getHeaders())
    ])
    
    const s = Array.isArray(resS.data) ? resS.data : (resS.data.results || []);
    const p = Array.isArray(resP.data) ? resP.data : (resP.data.results || []);

    categorias.value = [
      ...s.map(c => ({ ...c, tipo: 'Servicio' })),
      ...p.map(c => ({ ...c, tipo: 'Producto' }))
    ]
  } catch (err) { console.error("Error al cargar:", err) }
}

const categoriasFiltradas = computed(() => {
  return categorias.value.filter(c => {
    const b = c.nombre.toLowerCase().includes(filtros.value.busqueda.toLowerCase())
    const t = !filtros.value.tipo || c.tipo === filtros.value.tipo
    
    let matchEstado = true
    if (filtros.value.estado === 'activos') matchEstado = c.activo === true
    else if (filtros.value.estado === 'inactivos') matchEstado = c.activo === false
    
    return b && t && matchEstado
  })
})

const totalPaginas = computed(() => Math.max(1, Math.ceil(categoriasFiltradas.value.length / itemsPorPagina)))
const categoriasPaginadas = computed(() => {
  const i = (pagina.value - 1) * itemsPorPagina
  return categoriasFiltradas.value.slice(i, i + itemsPorPagina)
})

const abrirModalCrear = () => {
  Object.assign(form, { id: null, nombre: '', descripcion: '', tipo: '', activo: true })
  errores.nombre = ''
  modalVisible.value = true
}

const abrirModalEditar = (cat) => {
  // 🔥 ASIGNAMOS EL TIPO para que guardarCategoria sepa a qué URL ir
  Object.assign(form, { 
    id: cat.id, 
    nombre: cat.nombre, 
    descripcion: cat.descripcion || '', 
    tipo: cat.tipo, 
    activo: cat.activo 
  })
  errores.nombre = ''
  modalVisible.value = true
}

const cerrarModal = () => { modalVisible.value = false }

const guardarCategoria = async () => {
  if (!form.nombre.trim()) return errores.nombre = 'El nombre es requerido'
  try {
    const endpoint = form.tipo === 'Servicio' ? 'servicios' : 'productos'
    const accion = form.id ? `editar/${form.id}` : 'crear'
    const url = `${API_BASE}/api/categorias/${endpoint}/${accion}/`
    
    await axios.post(url, { ...form }, getHeaders())
    cerrarModal()
    await cargarCategorias()
    
    Swal.fire({ icon: 'success', title: '¡Guardado!', timer: 1000, showConfirmButton: false })
  } catch (err) {
    errores.nombre = err.response?.data?.message || 'Error al guardar'
  }
}

// 🔥 FUNCIÓN PARA ACTIVAR/DESACTIVAR DESDE LA TABLA
const toggleEstado = async (cat) => {
  const nuevoEstado = !cat.activo
  const titulo = nuevoEstado ? '¿Reactivar?' : '¿Desactivar?'
  
  const res = await Swal.fire({
    title: titulo,
    text: nuevoEstado ? "La categoría volverá a aparecer." : "Se ocultará de los formularios.",
    icon: nuevoEstado ? 'question' : 'warning',
    showCancelButton: true,
    confirmButtonText: nuevoEstado ? 'Sí, activar' : 'Sí, desactivar',
    confirmButtonColor: nuevoEstado ? '#10b981' : '#ef4444'
  })

  if (res.isConfirmed) {
    try {
      const endpoint = cat.tipo === 'Servicio' ? 'servicios' : 'productos'
      const url = `${API_BASE}/api/categorias/${endpoint}/editar/${cat.id}/`
      
      // Enviamos el estado cambiado a la ruta de edición
      await axios.post(url, { ...cat, activo: nuevoEstado }, getHeaders())
      await cargarCategorias()
      Swal.fire(nuevoEstado ? 'Activada' : 'Desactivada', '', 'success')
    } catch (err) {
      Swal.fire('Error', 'No se pudo cambiar el estado', 'error')
    }
  }
}

const paginaAnterior = () => { if (pagina.value > 1) pagina.value-- }
const paginaSiguiente = () => { if (pagina.value < totalPaginas.value) pagina.value++ }
const limpiarFiltros = () => { filtros.value = { busqueda: '', tipo: '', estado: 'todos' }; pagina.value = 1 }
const getTipoClass = (t) => t === 'Servicio' ? 'estado-info' : 'estado-success'

onMounted(cargarCategorias)
watch(filtros, () => { pagina.value = 1 }, { deep: true })
</script>

<style scoped>
/* ========================================
   🔥 ESTILO BARBERÍA MASCULINO ELEGANTE - CATEGORÍAS
   ======================================== */

/* Tarjeta principal - CON VARIABLES */
.list-card {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1200px;
  margin: auto;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
  border: 1px solid var(--border-color);
}

/* Borde superior azul acero */
.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7, #0369a1, #0284c7, #0ea5e9);
  border-radius: 24px 24px 0 0;
}

/* BADGES DE ESTADO - CON VARIABLES */
.badge-estado {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.estado-info {
  background: var(--bg-tertiary);
  color: #0ea5e9;
  border: 2px solid #0ea5e9;
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.3);
}

.estado-success {
  background: var(--bg-tertiary);
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

/* HEADER - CON VARIABLES */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 25px;
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
  letter-spacing: 0.5px;
}

/* Botón registrar */
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
  letter-spacing: 1px;
  font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 8px;
}

.register-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.register-button:hover::before {
  left: 100%;
}

.register-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.5);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

/* FILTROS - CON VARIABLES */
.filters-container {
  margin-bottom: 30px;
  background: var(--hover-bg);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 18px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}

.filter-input, .filter-select {
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.filter-input:focus, .filter-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

.clear-filters-btn {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.clear-filters-btn:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.row-inactiva { opacity: 0.6; background: rgba(0,0,0,0.05); }
.badge-tipo { padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }

/* El Switch del Modal */
.form-group-checkbox { margin: 15px 0; display: flex; align-items: center; }
.switch-container { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.switch-label { font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }

/* Estilos de tabla ya los tenés, solo asegurate que .badge-estado tenga colores para danger */
.estado-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; }

/* TABLA - CON VARIABLES */
.table-container {
  overflow-x: auto;
  margin-bottom: 25px;
  border-radius: 16px;
}

.categories-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

.categories-table th {
  background: var(--accent-color);
  color: white;
  padding: 18px 14px;
  text-align: left;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1.2px;
}

.categories-table tr {
  border-bottom: 1px solid var(--border-color);
}

.categories-table td {
  padding: 14px;
  vertical-align: middle;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
}

.categories-table td strong {
  color: var(--text-primary);
  font-weight: 800;
  letter-spacing: 0.3px;
}

.categories-table tr:hover {
  background: var(--hover-bg);
  transition: all 0.2s ease;
}

/* Estilos específicos de categorías */
.descripcion-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 🔥 BOTONES DE ACCIÓN MEJORADOS - ESTILO VENTAS */
.action-buttons { 
  display: flex; 
  gap: 6px;
  justify-content: center;
}

.action-button {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.action-button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.action-button.edit:hover {
  color: #3b82f6;
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.action-button.delete:hover {
  color: #ef4444;
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* CONTADOR Y MENSAJES - CON VARIABLES */
.results-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0;
  padding: 18px;
  background: var(--hover-bg);
  border-radius: 12px;
  flex-wrap: wrap;
  gap: 15px;
  border: 1px solid var(--border-color);
}

.results-info p {
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.5px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ESTADOS DE CARGA - CON VARIABLES */
.no-results {
  text-align: center;
  padding: 80px;
  color: var(--text-secondary);
}

.no-results p {
  margin: 0 0 8px 0;
  font-size: 1.1em;
  color: var(--text-primary);
}

.no-results small {
  font-size: 0.9em;
  color: var(--text-tertiary);
}

/* PAGINACIÓN - CON VARIABLES */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
}

.pagination-btn {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 800;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.pagination-btn:disabled {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  cursor: not-allowed;
  transform: none;
  border: 1px solid var(--border-color);
  opacity: 0.5;
}

.pagination-info {
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: 0.8px;
  font-size: 0.95rem;
}

/* MODAL - CON VARIABLES */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.88);
  backdrop-filter: blur(12px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeInModal 0.3s ease;
}

@keyframes fadeInModal {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  position: relative;
  animation: slideUp 0.3s ease;
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--border-color);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-card h2 {
  margin: 0 0 25px 0;
  font-size: 1.5rem;
  background: linear-gradient(135deg, var(--text-primary), #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.8px;
}

.modal-input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.modal-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px var(--accent-light);
  background: var(--bg-secondary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
}

.modal-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-size: 0.85rem;
}

.modal-btn.primary {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  color: white;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.modal-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

.modal-btn.secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.modal-btn.secondary:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.error {
  color: var(--error-color);
  font-size: 0.8rem;
  margin-top: 5px;
  display: block;
  font-weight: 600;
}

/* SCROLLBAR PERSONALIZADO - CON VARIABLES */
.table-container::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.table-container::-webkit-scrollbar-track {
  background: var(--bg-primary);
  border-radius: 6px;
}

.table-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 6px;
  border: 2px solid var(--bg-primary);
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .list-card {
    padding: 25px;
    border-radius: 20px;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-content h1 {
    font-size: 1.6rem;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-card {
    max-width: 95vw;
    margin: 12px;
    border-radius: 12px;
  }
  
  .categories-table {
    font-size: 0.85rem;
  }
  
  .categories-table th {
    font-size: 0.7rem;
    padding: 14px 10px;
  }
  
  .action-buttons {
    flex-direction: row;
    gap: 6px;
  }
  
  .results-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .list-card {
    padding: 18px;
    border-radius: 16px;
  }
  
  .header-content h1 {
    font-size: 1.4rem;
  }
  
  .categories-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .filter-input, .filter-select {
    font-size: 0.9rem;
  }
  
  .badge-estado {
    font-size: 0.65rem;
    padding: 5px 10px;
  }
  
  .action-button {
    width: 32px;
    height: 32px;
  }
  
  .register-button {
    width: 100%;
    justify-content: center;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>