<template>
  <div class="list-container">
    <div class="list-card" :class="{ 'overlay-activo': mostrarRegistrar || mostrarEditar }">
      <!-- Header -->
      <div class="list-header">
        <div class="header-content">
          <h1>Usuarios Registrados</h1>
          <p>Gestión de usuarios del sistema</p>
        </div>
        <button @click="mostrarRegistrar = true" class="register-button">➕ Registrar Usuario</button>
      </div>

      <!-- Filtros -->
      <div class="filters-container">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input v-model="filtros.busqueda" placeholder="Nombre o DNI..." class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Rol</label>
            <select v-model="filtros.rol" class="filter-select">
              <option value="">Todos</option>
              <option v-for="rol in roles" :key="rol.id" :value="rol.id">
                {{ rol.nombre }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Fecha desde</label>
            <input type="date" v-model="filtros.fechaDesde" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>Fecha hasta</label>
            <input type="date" v-model="filtros.fechaHasta" class="filter-input"/>
          </div>

          <div class="filter-group">
            <label>&nbsp;</label>
            <button @click="limpiarFiltros" class="clear-filters-btn">🗑️ Limpiar filtros</button>
          </div>
        </div>
      </div>

      <!-- Tabla de usuarios -->
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
            <tr v-for="usuario in usuariosPaginados" :key="usuario.id">
              <td>{{ usuario.nombre || '–' }}</td>
              <td>{{ usuario.apellido || '–' }}</td>
              <td>{{ usuario.dni || '–' }}</td>
              <td>{{ usuario.telefono || 'No registrado' }}</td>
              <td>{{ usuario.correo || '–' }}</td>
              <td><span class="role-badge">{{ usuario.rol_nombre || 'Sin rol' }}</span></td>
              <td><span :class="usuario.estado.toLowerCase()">{{ usuario.estado }}</span></td>
              <td>{{ formatFecha(usuario.fecha_creacion) }}</td>
              <td>
                <button @click="editarUsuario(usuario)">✏️</button>
                <button @click="eliminarUsuario(usuario)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="usuariosPaginados.length === 0" class="no-results">
          <p>No se encontraron usuarios</p>
        </div>
      </div>

      <!-- Mostrando cantidad -->
      <p class="usuarios-count">
        Mostrando {{ usuariosPaginados.length }} de {{ usuariosFiltrados.length }} usuarios
      </p>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="paginaAnterior" :disabled="pagina === 1">← Anterior</button>
        <span>Página {{ pagina }} de {{ totalPaginas }}</span>
        <button @click="paginaSiguiente" :disabled="pagina === totalPaginas">Siguiente →</button>
      </div>
    </div>

    <!-- Modal Registrar Usuario -->
    <div v-if="mostrarRegistrar" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <button class="modal-close" @click="cerrarModal" title="Cerrar formulario">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        
        <RegistrarUsuario @usuario-registrado="refrescarUsuarios"/>
      </div>
    </div>

    <!-- Modal Editar Usuario - SIN CRUZ -->
    <div v-if="mostrarEditar" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content">
        <!-- Usar ModificarUsuario como componente -->
        <ModificarUsuario 
          :usuario-id="usuarioEditando?.id" 
          @usuario-actualizado="usuarioActualizado"
          @cancelar="cerrarModalEditar"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import RegistrarUsuario from './RegistrarUsuario.vue'
import ModificarUsuario from './ModificarUsuario.vue'

const API_BASE = 'http://127.0.0.1:8000'

const usuarios = ref([])
const roles = ref([])
const filtros = ref({ busqueda: '', rol: '', fechaDesde: '', fechaHasta: '' })

const pagina = ref(1)
const itemsPorPagina = 8
const mostrarRegistrar = ref(false)
const mostrarEditar = ref(false)
const usuarioEditando = ref(null)
const hayAdminActivo = ref(false)

// 🔹 Cargar usuarios desde backend - SOLO ORDEN POR FECHA
const cargarUsuarios = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/usuarios/`)
    // 🔹 ORDENAR SOLO POR FECHA (más reciente primero)
    usuarios.value = res.data.sort((a, b) => {
      const fechaA = new Date(a.fecha_creacion || 0)
      const fechaB = new Date(b.fecha_creacion || 0)
      return fechaB - fechaA // Más reciente primero
    })
    
    hayAdminActivo.value = usuarios.value.some(
      u => u.rol_nombre?.toLowerCase() === 'administrador' && u.estado === 'ACTIVO'
    )
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
    alert('No se pudo cargar la lista de usuarios')
  }
}

// 🔹 Cargar roles
const cargarRoles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/usuarios/api/roles/`)
    roles.value = res.data.filter(r => r.activo || r.nombre.toLowerCase() === 'administrador')
  } catch (err) {
    console.error('Error al cargar roles:', err)
  }
}

onMounted(async () => {
  await cargarUsuarios()
  await cargarRoles()
})

// 🔹 Filtros por fecha
const filtrarPorFecha = (usuario) => {
  const fecha = usuario.fecha_creacion ? new Date(usuario.fecha_creacion) : null
  if (!fecha) return true
  if (filtros.value.fechaDesde && fecha < new Date(filtros.value.fechaDesde)) return false
  if (filtros.value.fechaHasta) {
    const hasta = new Date(filtros.value.fechaHasta)
    hasta.setDate(hasta.getDate() + 1)
    if (fecha >= hasta) return false
  }
  return true
}

// 🔹 Filtrar usuarios - CON ORDENAMIENTO POR ESTADO
const usuariosFiltrados = computed(() => {
  const filtrados = usuarios.value.filter(u => {
    const busca = filtros.value.busqueda.toLowerCase()
    const matchBusqueda = !busca || 
      (u.nombre?.toLowerCase().includes(busca) || 
       u.dni?.toLowerCase().includes(busca))
    const matchRol = !filtros.value.rol || (u.rol_id && u.rol_id == filtros.value.rol)
    const matchFecha = filtrarPorFecha(u)
    return matchBusqueda && matchRol && matchFecha
  })
  
  // 🔹 ORDENAR POR ESTADO: ACTIVOS primero, INACTIVOS al final
  return filtrados.sort((a, b) => {
    if (a.estado === b.estado) return 0
    return a.estado === 'ACTIVO' ? -1 : 1
  })
})

// 🔹 Paginación (mantener igual)
const totalPaginas = computed(() => {
  return Math.max(1, Math.ceil(usuariosFiltrados.value.length / itemsPorPagina))
})

const usuariosPaginados = computed(() => {
  const inicio = (pagina.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return usuariosFiltrados.value.slice(inicio, fin)
})

// 🔹 Navegación paginación
const paginaAnterior = () => { 
  if (pagina.value > 1) pagina.value--
}

const paginaSiguiente = () => { 
  if (pagina.value < totalPaginas.value) pagina.value++
}

// 🔹 Acciones sobre usuarios - CORREGIDO (ahora abre modal)
const editarUsuario = (usuario) => {
  usuarioEditando.value = usuario
  mostrarEditar.value = true
}

// 🔹 Cuando se actualiza el usuario
const usuarioActualizado = async () => {
  await cargarUsuarios() // Recargar la lista
  cerrarModalEditar()
}

const eliminarUsuario = async (usuario) => {
  if (!confirm(`¿Desactivar al usuario ${usuario.nombre}?`)) return
  try {
    await axios.post(`${API_BASE}/usuarios/api/usuarios/eliminar/${usuario.id}/`)
    // 🔹 SOLO cambiar estado - el ordenamiento en usuariosFiltrados se encarga
    usuario.estado = 'INACTIVO'
    
    // 🔹 Forzar recálculo del computed
    await nextTick()
    
    alert('Usuario desactivado con éxito')
  } catch (err) {
    console.error(err)
    alert('No se pudo desactivar el usuario')
  }
}

// 🔹 Limpiar filtros
const limpiarFiltros = () => {
  filtros.value = { busqueda: '', rol: '', fechaDesde: '', fechaHasta: '' }
  pagina.value = 1
}

// 🔹 Formato de fecha
const formatFecha = (fecha) => fecha ? new Date(fecha).toLocaleString() : '–'

// 🔹 Cerrar modales
const cerrarModal = () => mostrarRegistrar.value = false

const cerrarModalEditar = () => {
  mostrarEditar.value = false
  usuarioEditando.value = null
}

// 🔹 Refrescar usuarios 
const refrescarUsuarios = async (nuevoUsuario = null) => {
  if (nuevoUsuario) {
    // Recargar toda la lista para garantizar orden
    await cargarUsuarios()
    
    // Forzar página 1
    pagina.value = 1
    
    await nextTick()
  }
  mostrarRegistrar.value = false
}

// 🔹 Resetear página al cambiar filtros
watch(filtros, () => {
  pagina.value = 1
}, { deep: true })
</script>
<style scoped>
/* Tarjeta principal */
.list-card {
  /* Cambio clave: Usar variable para fondo de tarjeta (bg-secondary) */
  background: var(--bg-secondary);
  color: var(--text-primary); /* Para que el texto interno cambie */
  
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 1600px;
  /* Cambio clave: Usar variable para sombra (shadow-color) y borde sutil (border-color) */
  box-shadow: 0 25px 50px var(--shadow-color),
              0 0 0 1px var(--border-color) inset;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease; /* Transición para que el cambio de tema se vea suave */
}

.list-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  /* Cambio clave: Usar variable para el acento del degradado */
  background: linear-gradient(90deg, 
              var(--text-secondary), 
              var(--accent-color), 
              var(--text-secondary));
  border-radius: 24px 24px 0 0;
}

/* Botones específicos de esta tabla */
.action-buttons { display: flex; gap: 6px; flex-wrap: wrap; }
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
  color: white; /* Mantenemos blanco para contraste en gradientes */
}
.action-button.edit {
  /* Usamos colores fijos para gradientes de acción (azul/verde) */
  background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
  /* Sugerencia: Añade hover con var(--accent-shadow) si usas el botón de Header.vue */
}
.action-button.delete {
  /* Usamos colores fijos para gradientes de peligro (rojo) */
  background: linear-gradient(135deg, #ef4444, #dc2626); 
}

/* 🔹 Efecto de oscurecimiento elegante cuando se abre el modal */
.overlay-activo {
  /* Mantenemos la opacidad y el blur, pero no afectamos los colores */
  opacity: 0.4;
  filter: blur(3px);
  pointer-events: none;
}

/* 🔹 Modal overlay - fondo oscuro semitransparente */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* Cambio clave: Usar el fondo principal con transparencia para el overlay */
  background: var(--bg-primary); 
  opacity: 0.9;
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 🔹 Contenedor del formulario - MÁS COMPACTO */
.modal-content {
  position: relative;
  animation: slideUp 0.3s ease;
  max-height: 85vh;
  max-width: 60vw;
  overflow-y: auto;
  border-radius: 16px;
  
  /* Cambio clave: Usar fondo secundario para el modal */
  background: var(--bg-secondary); 
  /* Cambio clave: Usar variables de tema para sombra y borde */
  box-shadow: 0 20px 40px var(--shadow-color);
  border: 1px solid var(--border-color);
  
  padding: 0;
  margin: 20px;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 🔹 Botón de cerrar BIEN PEGADO AL BORDE - COMPACTO */
.modal-close {
  position: absolute;
  top: 8px;
  right: 8px;
  /* Mantenemos el rojo fijo para indicar "cerrar" o "peligro" */
  background: linear-gradient(135deg, #ef4444, #dc2626); 
  border: none;
  border-radius: 10px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 100;
  box-shadow: 0 3px 8px rgba(239, 68, 68, 0.4);
  overflow: hidden;
}

.modal-close::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  /* Usamos el color de texto primario con transparencia para el brillo (funciona en ambos modos) */
  background: linear-gradient(90deg, transparent, var(--text-primary), transparent);
  opacity: 0.2;
  transition: left 0.5s ease;
}

.modal-close:hover {
  transform: scale(1.15) rotate(90deg);
  box-shadow: 0 5px 15px rgba(239, 68, 68, 0.6);
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

/* Animaciones no necesitan cambios */
@keyframes subtlePulse {
  0%, 100% { box-shadow: 0 3px 8px rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 3px 12px rgba(239, 68, 68, 0.6); }
}

.modal-close {
  animation: subtlePulse 3s infinite;
}

/* Asegurar que el formulario interno se adapte */
.modal-content ::v-deep .form-container {
  margin: 0;
  padding: 20px;
  border-radius: 16px;
  /* IMPORTANTE: Si .form-container tiene fondo, DEBE usar var(--bg-secondary) o var(--bg-primary) */
}
</style>