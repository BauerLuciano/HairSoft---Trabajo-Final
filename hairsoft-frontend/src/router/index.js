import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  
  // Auth - login está directamente en views/
  { path: '/login', name: 'Login', component: () => import('@/views/login.vue'), meta:{hideNavbar: true} },
  
  // Usuarios
  { path: '/usuarios', name: 'ListadoUsuarios', component: () => import('@/views/usuarios/ListadoUsuarios.vue') },
  { path: '/usuarios/crear', name: 'RegistrarUsuario', component: () => import('@/views/usuarios/RegistrarUsuario.vue') },
  { path: '/usuarios/modificar/:id', name: 'ModificarUsuario', component: () => import('@/views/usuarios/ModificarUsuario.vue') },
  
  // Turnos
  { path: '/turnos', name: 'ListadoTurnos', component: () => import('@/views/turnos/ListadoTurnos.vue') },
  { path: '/turnos/crear-presencial', name: 'RegistrarTurnoPresencial', component: () => import('@/views/turnos/RegistrarTurnoPresencial.vue') },
  { path: '/turnos/crear-web', name: 'RegistrarTurnoWeb', component: () => import('@/views/turnos/RegistrarTurnoWeb.vue') },
  { path: '/turnos/modificar/:id', name: 'ModificarTurno', component: () => import('@/views/turnos/ModificarTurno.vue') },
  { path: '/aceptar-oferta/:turno_id/:token', name: 'AceptarOferta', component: () => import('@/views/turnos/AceptarOferta.vue') },

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

  //Marcas
  { path: '/marcas', name: 'ListadoMarcas', component: () => import('@/views/productos/ListadoMarcas.vue') },
  { path: '/marcas/crear', name: 'RegistrarMarca', component: () => import('@/views/productos/RegistrarMarca.vue') },
  { path: '/marcas/modificar/:id', name: 'ModificarMarca', component: () => import('@/views/productos/RegistrarMarca.vue'), props: true },


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
  { path: '/proveedores/modificar/:id', name: 'ModificarProveedor', component: () => import('@/views/proveedores/ModificarProveedor.vue'), props: true },

  // ✅ NUEVA RUTA: GESTIÓN DE LISTAS DE PRECIOS
  { path: '/proveedores/listas-precios', name: 'GestionListasPrecios', component: () => import('@/views/proveedores/GestionListasPrecios.vue') },

  // ================================
  // Ventas
  // ================================

  { path: '/ventas', name: 'ListadoVentas', component: () => import('@/views/ventas/ListadoVentas.vue') },
  { path: '/ventas/crear', name: 'RegistrarVenta', component: () => import('@/views/ventas/RegistrarVenta.vue') },
  { path: '/ventas/modificar/:id', name: 'ModificarVenta', component: () => import('@/views/ventas/ModificarVenta.vue'), props: true },

  // ================================
  // PEDIDOS - NUEVAS RUTAS
  // ================================
  { path: '/pedidos', name: 'ListadoPedidos', component: () => import('@/views/pedidos/ListadoPedidos.vue') },
  { path: '/pedidos/crear', name: 'RegistrarPedido', component: () => import('@/views/pedidos/RegistrarPedido.vue') },
  { path: '/pedidos/modificar/:id', name: 'ModificarPedido', component: () => import('@/views/pedidos/ModificarPedido.vue'), props: true },
  { path: '/pedidos/recibir/:id', name: 'RecibirPedido', component: () => import('@/views/pedidos/RecibirPedido.vue'), props: true }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router