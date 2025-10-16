<template>
  <div class="list-container">
    <div class="list-card">
      <div class="list-header">
        <div class="header-content">
          <h1>Lista de Usuarios Registrados</h1>
          <p>Gestión completa de usuarios del sistema</p>
        </div>
        <button @click="irARegistrar" class="register-button">
          <span class="btn-text">➕ Registrar Usuario</span>
        </button>
      </div>

      <!-- Filtros Mejorados -->
      <div class="filters-container">
        <div class="filters-grid">
          <!-- Búsqueda general -->
          <div class="filter-group">
            <label>Buscar</label>
            <div class="input-with-icon">
              <input 
                v-model="filtros.busqueda" 
                type="text" 
                placeholder="Nombre o DNI..." 
                class="filter-input" 
              />
              <span class="input-icon">🔍</span>
            </div>
          </div>

          <!-- Filtro por rol -->
          <div class="filter-group">
            <label>Rol</label>
            <select v-model="filtros.rol" class="filter-select">
              <option value="">Todos los roles</option>
              <option value="ADMIN">Administrador</option>
              <option value="REC">Recepcionista</option>
              <option value="PEL">Peluquero</option>
              <option value="CLI">Cliente</option>
            </select>
          </div>

          <!-- Filtro por fecha desde -->
          <div class="filter-group">
            <label>Fecha desde</label>
            <input 
              v-model="filtros.fechaDesde" 
              type="date" 
              class="filter-input" 
            />
          </div>

          <!-- Filtro por fecha hasta -->
          <div class="filter-group">
            <label>Fecha hasta</label>
            <input 
              v-model="filtros.fechaHasta" 
              type="date" 
              class="filter-input" 
            />
          </div>

          <!-- Botón limpiar filtros DEBAJO de las fechas -->
          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">
              🗑️ Limpiar Filtros
            </button>
          </div>
        </div>
      </div>

      <!-- Tabla Mejorada -->
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Apellido</th>
              <th>DNI</th>
              <th>Teléfono</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Fecha Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usuario in usuariosFiltradosPaginados" :key="usuario.id" class="table-row">
              <td class="user-name">{{ usuario.nombre || '–' }}</td>
              <td>{{ usuario.apellido || '–' }}</td>
              <td class="user-dni">{{ usuario.dni || '–' }}</td>
              <td class="user-phone">{{ usuario.telefono || 'No registrado' }}</td>
              <td class="user-email">{{ usuario.correo || '–' }}</td>
              <td>
                <span class="role-badge" :class="getRoleClass(usuario.rol)">
                  {{ getRoleDisplayName(usuario.rol) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="getStatusClass(usuario.estado)">
                  {{ getStatusDisplayName(usuario.estado) }}
                </span>
              </td>
              <td class="fecha-registro">
                {{ formatFecha(usuario.fecha_creacion || usuario.created_at || usuario.fecha_registro) }}
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editarUsuario(usuario)" class="action-button edit">
                    <span class="btn-icon">✏️</span>
                    Editar
                  </button>
                  <button @click="eliminarUsuario(usuario)" class="action-button delete">
                    <span class="btn-icon">🗑️</span>
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Mensaje cuando no hay resultados -->
        <div v-if="usuariosFiltradosPaginados.length === 0" class="no-results">
          <p>No se encontraron usuarios con los filtros aplicados</p>
          <button @click="limpiarFiltros" class="clear-filters-btn">
            Limpiar filtros
          </button>
        </div>
      </div>

      <!-- Información de resultados DEBAJO de la tabla -->
      <div class="results-info">
        <p>Mostrando {{ usuariosFiltradosPaginados.length }} de {{ usuariosFiltrados.length }} usuarios</p>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1" class="pagination-btn">
          <span class="btn-icon">←</span> Anterior
        </button>
        <span class="pagination-info">Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas" class="pagination-btn">
          Siguiente <span class="btn-icon">→</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const usuarios = ref([])
const pagina = ref(1)
const itemsPorPagina = 8
const filtros = ref({ 
  busqueda: '',
  rol: '',
  fechaDesde: '',
  fechaHasta: ''
})

// Cargar usuarios desde el backend
const cargarUsuarios = async () => {
  try {
    console.log('🔄 Cargando usuarios con filtros:', filtros.value)
    const params = new URLSearchParams()
    if (filtros.value.busqueda) params.append('q', filtros.value.busqueda)
    if (filtros.value.rol) params.append('rol', filtros.value.rol)
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`, { params })
    usuarios.value = res.data
    console.log('✅ Usuarios cargados:', usuarios.value)
    usuarios.value.forEach(u => console.log('Rol recibido:', u.rol))
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
    console.error('📝 Data:', JSON.stringify(err.response?.data, null, 2))
    alert('No se pudo cargar la lista de usuarios')
  }
}

onMounted(cargarUsuarios)

// Observar cambios en los filtros
watch(filtros, () => {
  pagina.value = 1 // Resetear la página al cambiar filtros
  cargarUsuarios()
}, { deep: true })

// Función para formatear fecha
const formatFecha = (fechaString) => {
  if (!fechaString) {
    return '–'
  }
  try {
    const fecha = new Date(fechaString)
    if (isNaN(fecha.getTime())) {
      return '–'
    }
    return fecha.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch {
    return '–'
  }
}

// Función para obtener nombre display del rol
const getRoleDisplayName = (rol) => {
  // Normalizar el rol a mayúsculas para manejar variaciones
  const rolNormalizado = rol ? rol.toUpperCase() : ''
  const roles = {
    'ADMIN': 'Administrador',
    'RECEPCIONISTA': 'Recepcionista',
    'PELUQUERO': 'Peluquero',
    'CLIENTE': 'Cliente',
    'ADM': 'Administrador',
    'REC': 'Recepcionista',
    'RECEP': 'Recepcionista',
    'PEL': 'Peluquero',
    'CLI': 'Cliente'
  }
  const nombreRol = roles[rolNormalizado] || rol || 'Sin rol'
  console.log('Rol:', rol, '→ Mapeado a:', nombreRol) // Log para depurar mapeo
  return nombreRol
}

// Función para obtener clase CSS del rol
const getRoleClass = (rol) => {
  const rolNormalizado = rol ? rol.toLowerCase() : ''
  const roles = {
    'admin': 'admin',
    'administrador': 'admin',
    'adm': 'admin',
    'recepcionista': 'recepcionista',
    'rec': 'recepcionista',
    'recep': 'recepcionista',
    'peluquero': 'peluquero',
    'pel': 'peluquero',
    'cliente': 'cliente',
    'cli': 'cliente'
  }
  return roles[rolNormalizado] || 'default'
}

// Función para obtener estado
const getStatusDisplayName = (estado) => {
  const estados = {
    'ACTIVO': 'Activo',
    'INACTIVO': 'Inactivo',
    'activo': 'Activo',
    'inactivo': 'Inactivo'
  }
  return estados[estado] || 'Activo'
}

// Función para obtener clase del estado
const getStatusClass = (estado) => {
  const estadoLower = (estado || 'activo').toLowerCase()
  return estadoLower === 'activo' ? 'activo' : 'inactivo'
}

// Función para filtrar por fecha
const filtrarPorFecha = (usuario) => {
  if (!filtros.value.fechaDesde && !filtros.value.fechaHasta) return true
  
  const fechaUsuarioStr = usuario.fecha_creacion || usuario.created_at || usuario.fecha_registro
  if (!fechaUsuarioStr) return true
  
  try {
    const fechaUsuario = new Date(fechaUsuarioStr)
    if (isNaN(fechaUsuario.getTime())) return true
    
    if (filtros.value.fechaDesde) {
      const fechaDesde = new Date(filtros.value.fechaDesde)
      if (fechaUsuario < fechaDesde) return false
    }
    
    if (filtros.value.fechaHasta) {
      const fechaHasta = new Date(filtros.value.fechaHasta)
      fechaHasta.setDate(fechaHasta.getDate() + 1)
      if (fechaUsuario >= fechaHasta) return false
    }
    
    return true
  } catch {
    return true
  }
}

// FILTRADO SOLO POR DNI Y NOMBRE
const usuariosFiltrados = computed(() => {
  let filtered = usuarios.value

  // SOLO nombre y DNI
  if (filtros.value.busqueda) {
    const term = filtros.value.busqueda.toLowerCase()
    filtered = filtered.filter(u =>
      (u.nombre?.toLowerCase().includes(term) || '') ||
      (u.dni?.toLowerCase().includes(term) || '')
    )
  }

  // Filtro por rol
  if (filtros.value.rol) {
    filtered = filtered.filter(u => (u.rol || '').toUpperCase() === filtros.value.rol)
  }

  // Filtro por fecha
  filtered = filtered.filter(filtrarPorFecha)

  return filtered
})

// Paginación
const totalPaginas = computed(() =>
  Math.ceil(usuariosFiltrados.value.length / itemsPorPagina)
)

const usuariosFiltradosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return usuariosFiltrados.value.slice(inicio, fin)
})

const paginaAnterior = () => {
  if (pagina.value > 1) pagina.value--
}

const paginaSiguiente = () => {
  if (pagina.value < totalPaginas.value) pagina.value++
}

// Limpiar filtros
const limpiarFiltros = () => {
  filtros.value.busqueda = ''
  filtros.value.rol = ''
  filtros.value.fechaDesde = ''
  filtros.value.fechaHasta = ''
  pagina.value = 1
  cargarUsuarios() // Recargar usuarios con filtros limpios
}

// Acciones
const irARegistrar = () => router.push('/usuarios/crear')

const editarUsuario = (usuario) => {
  console.log('🔄 Editando usuario:', usuario.id, usuario.nombre)
  router.push(`/usuarios/modificar/${usuario.id}`)
}

const eliminarUsuario = async (usuario) => {
  if (!confirm(`¿Estás seguro de desactivar al usuario ${usuario.nombre} ${usuario.apellido}?`)) return
  try {
    console.log('🔄 Desactivando usuario ID:', usuario.id)
    const response = await axios.post(`${API_BASE}/usuarios/api/usuarios/eliminar/${usuario.id}/`)
    console.log('✅ Respuesta del servidor:', JSON.stringify(response.data, null, 2))
    // Actualizar el estado en la lista
    usuarios.value = usuarios.value.map(u => 
      u.id === usuario.id ? { ...u, estado: 'INACTIVO' } : u
    )
    alert('✅ Usuario desactivado con éxito')
  } catch (err) {
    console.error('❌ Error al desactivar usuario:', err)
    console.error('📊 Status:', err.response?.status)
    console.error('📝 Data:', JSON.stringify(err.response?.data, null, 2))
    alert('No se pudo desactivar el usuario: ' + (err.response?.data?.message || err.message))
  }
}
</script>

<style scoped>
/* Estilos base */
.list-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 40px 20px;
  background: transparent;
}

.list-card {
  background: rgba(23, 23, 23, 0.8);
  border: 2px solid #374151;
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #6b7280, #9ca3af, #6b7280);
  border-radius: 24px 24px 0 0;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.header-content h1 {
  font-size: 2.2rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.header-content p {
  color: #d1d5db;
  font-size: 1rem;
  font-weight: 500;
}

.register-button {
  padding: 14px 28px;
  background: linear-gradient(135deg, #0099ff 0%, #0066cc 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 153, 255, 0.3);
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(0, 153, 255, 0.4);
}

/* Filtros Mejorados */
.filters-container {
  margin-bottom: 25px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  color: #f3f4f6;
  font-weight: 600;
  font-size: 0.9rem;
}

.input-with-icon {
  position: relative;
}

.input-with-icon .input-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.filter-input, .filter-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #4b5563;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: #4f4f4f;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.filter-input:focus, .filter-select:focus {
  outline: none;
  border-color: #6b7280;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.2);
}

.filter-input::placeholder {
  color: #9ca3af;
}

/* Botón limpiar filtros */
.clear-filters-btn {
  padding: 12px 16px;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.clear-filters-btn:hover {
  background: #4b5563;
  transform: translateY(-1px);
}

/* Tabla RESPONSIVE */
.table-container {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #374151;
  background: rgba(255, 255, 255, 0.02);
  margin-bottom: 20px;
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: transparent;
  min-width: 1000px;
  font-family: inherit; /* ← ASEGURA FUENTE UNIFORME EN TODA LA TABLA */
}

.users-table th {
  background: rgba(55, 65, 81, 0.5);
  color: #f3f4f6;
  font-weight: 700;
  font-size: 0.85rem;
  padding: 16px 12px;
  text-align: left;
  border-bottom: 2px solid #4b5563;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.users-table td {
  padding: 14px 12px;
  color: #e5e7eb;
  border-bottom: 1px solid #374151;
  font-weight: 500;
  font-size: 0.9rem;
  white-space: nowrap;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* Badges Mejorados CON NUEVOS COLORES */
.role-badge, .status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  display: inline-block;
}

/* NUEVOS COLORES PARA ROLES */
.role-badge.admin {
  background: linear-gradient(135deg, #ef4444, #dc2626); /* ROJO */
  color: white;
}

.role-badge.recepcionista {
  background: linear-gradient(135deg, #f59e0b, #d97706); /* AMARILLO/NARANJA */
  color: white;
}

.role-badge.peluquero {
  background: linear-gradient(135deg, #f97316, #ea580c); /* NARANJA */
  color: white;
}

.role-badge.cliente {
  background: linear-gradient(135deg, #10b981, #059669); /* VERDE */
  color: white;
}

.role-badge.default {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: white;
}

.status-badge.activo {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.status-badge.inactivo {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

/* Información de resultados DEBAJO de la tabla */
.results-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.results-info p {
  color: #9ca3af;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Fecha registro */
.fecha-registro {
  font-size: 0.85rem;
  color: #9ca3af;
  white-space: nowrap;
}

/* Teléfono - CORREGIDO: misma fuente que todo */
.user-phone {
  font-weight: 600;
  color: #e5e7eb;
  /* SE ELIMINÓ LA FUENTE ESPECÍFICA - usa la misma que toda la tabla */
}

/* Acciones */
.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.action-button {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.action-button.edit {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.action-button.delete {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.action-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

/* Paginación */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 25px;
  padding: 20px 0;
  flex-wrap: wrap;
  gap: 15px;
}

.pagination-btn {
  padding: 10px 20px;
  background: #374151;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  white-space: nowrap;
}

.pagination-btn:hover:not(:disabled) {
  background: #4b5563;
  transform: translateY(-2px);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-info {
  color: #d1d5db;
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
}

/* No results */
.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
  font-size: 1.1rem;
}

.no-results .clear-filters-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #374151;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.no-results .clear-filters-btn:hover {
  background: #4b5563;
}

/* Modo claro - CORREGIDO SELECT */
body.light-mode .list-card {
  background: #ffffff;
  border: 2px solid #000000;
}

body.light-mode .list-card::before {
  background: linear-gradient(90deg, #000000, #333333, #000000);
}

body.light-mode .header-content h1 {
  color: #000000;
}

body.light-mode .header-content p {
  color: #666666;
}

body.light-mode .filter-group label {
  color: #374151;
}

body.light-mode .filter-input,
body.light-mode .filter-select {
  background: #ffffff;
  border: 2px solid #d1d5db;
  color: #000000; /* ← CORREGIDO: texto negro en modo claro */
}

body.light-mode .filter-input:focus,
body.light-mode .filter-select:focus {
  border-color: #000000;
}

/* Asegurar que las opciones del select también sean legibles */
body.light-mode .filter-select option {
  background: #ffffff;
  color: #000000;
}

body.light-mode .clear-filters-btn {
  background: #6b7280;
  color: white;
}

body.light-mode .table-container {
  border-color: #d1d5db;
  background: #f8fafc;
}

body.light-mode .users-table th {
  background: #e5e7eb;
  color: #1f2937;
  border-bottom-color: #d1d5db;
}

body.light-mode .users-table td {
  color: #374151;
  border-bottom-color: #e5e7eb;
}

body.light-mode .table-row:hover {
  background: #f1f5f9;
}

body.light-mode .fecha-registro {
  color: #6b7280;
}

body.light-mode .user-phone {
  color: #374151; /* ← Misma fuente que todo en modo claro */
}

body.light-mode .pagination-btn {
  background: #000000;
  color: #ffffff;
}

body.light-mode .pagination-btn:hover:not(:disabled) {
  background: #333333;
}

body.light-mode .pagination-info {
  color: #666666;
}

/* RESPONSIVE MEJORADO */
@media (max-width: 1200px) {
  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .list-container {
    padding: 20px 10px;
  }
  
  .list-card {
    padding: 20px 15px;
    border-radius: 20px;
  }
  
  .list-header {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .results-info {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .users-table {
    min-width: 900px;
    font-size: 0.8rem;
  }
  
  .users-table th,
  .users-table td {
    padding: 10px 8px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-button {
    padding: 4px 8px;
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .list-card {
    padding: 15px 10px;
  }
  
  .header-content h1 {
    font-size: 1.8rem;
  }
  
  .register-button {
    padding: 10px 20px;
    font-size: 0.9rem;
  }
  
  .users-table {
    min-width: 800px;
  }
  
  .role-badge, .status-badge {
    font-size: 0.7rem;
    padding: 4px 8px;
  }
}
</style>
