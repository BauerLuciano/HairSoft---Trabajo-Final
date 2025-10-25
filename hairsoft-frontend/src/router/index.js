import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  
  // Auth - login está directamente en views/
  { path: '/login', name: 'Login', component: () => import('@/views/login.vue') },
  
  // Usuarios
  { path: '/usuarios', name: 'ListadoUsuarios', component: () => import('@/views/usuarios/ListadoUsuarios.vue') },
  { path: '/usuarios/crear', name: 'RegistrarUsuario', component: () => import('@/views/usuarios/RegistrarUsuario.vue') },
  { path: '/usuarios/modificar/:id', name: 'ModificarUsuario', component: () => import('@/views/usuarios/ModificarUsuario.vue') },
  
  // Turnos
  { path: '/turnos', name: 'ListadoTurnos', component: () => import('@/views/turnos/ListadoTurnos.vue') },
  { path: '/turnos/crear-presencial', name: 'RegistrarTurnoPresencial', component: () => import('@/views/turnos/RegistrarTurnoPresencial.vue') },
  { path: '/turnos/crear-web', name: 'RegistrarTurnoWeb', component: () => import('@/views/turnos/RegistrarTurnoWeb.vue') },
  //{ path: '/turnos/modificar/:id', name: 'ModificarTurno', component: () => import('@/views/turnos/ModificarTurno.vue') },

  // Servicios
  { path: '/servicios', name: 'ListadoServicios', component: () => import('@/views/servicios/ListadoServicios.vue') },
  { path: '/servicios/crear', name: 'RegistrarServicio', component: () => import('@/views/servicios/RegistrarServicio.vue') },
  //{ path: '/servicios/modificar/:id', name: 'ModificarServicios', component: () => import('@/views/servicios/ModificarServicios.vue') },

  // Categorías
  { path: '/categorias', name: 'ListadoCategorias', component: () => import('@/views/categorias/ListadoCategorias.vue') },
  { path: '/categorias/crear', name: 'RegistrarCategoria', component: () => import('@/views/categorias/RegistrarCategoria.vue') },
  { path: '/categorias/modificar/:id', name: 'ModificarCategoria', component: () => import('@/views/categorias/RegistrarCategoria.vue'), props: true }, 

  // ================================
  // Roles
  // ================================
  { path: '/roles', name: 'ListadoRoles', component: () => import('@/views/roles/ListadoRoles.vue') },
  { path: '/roles/crear', name: 'RegistrarRol', component: () => import('@/views/roles/RegistrarRol.vue') },
  { path: '/roles/modificar/:id', name: 'ModificarRol', component: () => import('@/views/roles/RegistrarRol.vue'), props: true },

  // Dashboard
  { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },

   // ================================
  // Productos
  // ================================ 
  { path: '/productos', name: 'ListadoProductos', component: () => import('@/views/productos/ListadoProductos.vue') },
  { path: '/productos/crear', name: 'RegistrarProducto', component: () => import('@/views/productos/RegistrarProducto.vue') },
  { path: '/productos/modificar/:id', name: 'ModificarProducto', component: () => import('@/views/productos/ModificarProducto.vue'), props: true },


   // ================================
  // Proveedores
  // ================================

  { path: '/proveedores', name: 'ListadoProveedores', component: () => import('@/views/proveedores/ListadoProveedores.vue') },
  { path: '/proveedores/crear', name: 'RegistrarProveedor', component: () => import('@/views/proveedores/RegistrarProveedor.vue') },
  { path: '/proveedores/modificar/:id', name: 'ModificarProveedor', component: () => import('@/views/proveedores/ModificarProveedor.vue'), props: true }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
