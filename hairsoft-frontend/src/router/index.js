import { createRouter, createWebHistory } from 'vue-router'

// =============================================================================
// IMPORTACIONES (Lazy Loading)
// =============================================================================

// Auth
const Login = () => import('@/views/login.vue')
const SolicitarRecuperacion = () => import('@/views/auth/SolicitarRecuperacion.vue')
const NuevaPassword = () => import('@/views/auth/NuevaPassword.vue')

// --- VISTAS PÚBLICAS Y CLIENTE ---
const ServiciosPublico = () => import('@/views/publico/ServiciosPublico.vue')
const ProductosPublico = () => import('@/views/publico/ProductosPublico.vue')
const HomePublico = () => import('@/views/publico/HomePublico.vue')
const RegistroCliente = () => import('@/views/publico/RegistroCliente.vue')
// ✅ AGREGADO: La vista de Checkout
const Checkout = () => import('@/views/publico/Checkout.vue') 

const DashboardCliente = () => import('@/views/cliente/DashboardCliente.vue')
const HistorialTurnos = () => import('@/views/cliente/HistorialTurnos.vue')
const PerfilCliente = () => import('@/views/cliente/PerfilCliente.vue')

// --- VISTAS ADMINISTRATIVAS ---
const Dashboard = () => import('@/views/Dashboard.vue')

// Usuarios
const ListadoUsuarios = () => import('@/views/usuarios/ListadoUsuarios.vue')
const RegistrarUsuario = () => import('@/views/usuarios/RegistrarUsuario.vue')
const ModificarUsuario = () => import('@/views/usuarios/ModificarUsuario.vue')

// Turnos (Gestión Admin)
const ListadoTurnos = () => import('@/views/turnos/ListadoTurnos.vue')
const RegistrarTurnoPresencial = () => import('@/views/turnos/RegistrarTurnoPresencial.vue')
const RegistrarTurnoWeb = () => import('@/views/turnos/RegistrarTurnoWeb.vue') 
const ModificarTurno = () => import('@/views/turnos/ModificarTurno.vue')
const AceptarOferta = () => import('@/views/turnos/AceptarOferta.vue')

// Servicios
const ListadoServicios = () => import('@/views/servicios/ListadoServicios.vue')
const RegistrarServicio = () => import('@/views/servicios/RegistrarServicio.vue')
const ModificarServicio = () => import('@/views/servicios/ModificarServicio.vue')

// Categorías
const ListadoCategorias = () => import('@/views/categorias/ListadoCategorias.vue')
const RegistrarCategoria = () => import('@/views/categorias/RegistrarCategoria.vue')

// Roles
const ListadoRoles = () => import('@/views/roles/ListadoRoles.vue')
const RegistrarRol = () => import('@/views/roles/RegistrarRol.vue')
const ModificarRol = () => import('@/views/roles/ModificarRol.vue')

// Productos y Marcas
const ListadoProductos = () => import('@/views/productos/ListadoProductos.vue')
const RegistrarProducto = () => import('@/views/productos/RegistrarProducto.vue')
const ModificarProducto = () => import('@/views/productos/ModificarProducto.vue')
const ListadoMarcas = () => import('@/views/productos/ListadoMarcas.vue')
const RegistrarMarca = () => import('@/views/productos/RegistrarMarca.vue')
const EditarMarca = () => import('@/views/productos/ModificarMarca.vue')
const CatalogoVisual = () => import('@/views/productos/CatalogoProductos.vue')

// Proveedores
const ListadoProveedores = () => import('@/views/proveedores/ListadoProveedores.vue')
const RegistrarProveedor = () => import('@/views/proveedores/RegistrarProveedor.vue')
const ModificarProveedor = () => import('@/views/proveedores/ModificarProveedor.vue')
const GestionListasPrecios = () => import('@/views/proveedores/GestionListasPrecios.vue')
const EvaluacionPresupuestos = () => import('@/views/proveedores/EvaluacionPresupuestos.vue')
const CotizarExterno = () => import('@/views/proveedores/CotizarExterno.vue')
const GestionPedidoExterno = () => import('@/views/proveedores/GestionPedidoExterno.vue')

// Ventas
const ListadoVentas = () => import('@/views/ventas/ListadoVentas.vue')
const RegistrarVenta = () => import('@/views/ventas/RegistrarVenta.vue')
const ModificarVenta = () => import('@/views/ventas/ModificarVenta.vue')
const DetalleVenta = () => import('@/views/ventas/DetalleVenta.vue')

// Pedidos
const ListadoPedidos = () => import('@/views/pedidos/ListadoPedidos.vue')
const RegistrarPedido = () => import('@/views/pedidos/RegistrarPedido.vue')
const ModificarPedido = () => import('@/views/pedidos/ModificarPedido.vue')
const RecibirPedido = () => import('@/views/pedidos/RecibirPedido.vue')
const DetallePedido = () => import('@/views/pedidos/DetallePedido.vue')

//Compra Cliente
const CompraExitosa = () => import('@/views/publico/CompraExitosa.vue')
const MisPedidos = () => import('@/views/cliente/MisPedidos.vue')
const GestionPedidosWeb = () => import('@/views/pedidos/GestionPedidosWeb.vue')

// Auditoría
const ListadoAuditoria = () => import('@/views/auditoria/ListadoAuditoria.vue')

// 💰 Liquidación de Sueldos (NUEVO)
const LiquidacionSueldos = () => import('@/views/admin/LiquidacionSueldos.vue')

// =============================================================================
// DEFINICIÓN DE RUTAS CON SEGURIDAD
// =============================================================================

const routes = [
  // Redirección inicial
  { path: '/', redirect: '/web/home' },
  
  // Login
  { path: '/login', name: 'Login', component: Login, meta: { hideNavbar: true } },

  // RECUPERACIÓN DE CONTRASEÑA
  { 
    path: '/recuperar-password', 
    name: 'RecuperarPassword', 
    component: SolicitarRecuperacion, 
    meta: { hideNavbar: true } 
  },
  { 
    path: '/recuperar-password/:token', 
    name: 'NuevaPassword', 
    component: NuevaPassword, 
    meta: { hideNavbar: true } 
  },

  // ---------------------------------------------------------------------------
  // 🌍 ZONA PÚBLICA (Acceso libre)
  // ---------------------------------------------------------------------------
  { 
    path: '/web/home', 
    name: 'WebHome', 
    component: HomePublico, 
    meta: { layout: 'client' } 
  },
  { 
    path: '/web/servicios', 
    name: 'ServiciosPublico', 
    component: ServiciosPublico, 
    meta: { layout: 'client' } 
  },
  { 
    path: '/web/productos', 
    name: 'ProductosPublico', 
    component: ProductosPublico, 
    meta: { layout: 'client' } 
  },
  // ✅ AGREGADO: Ruta para el Checkout (Requiere Auth de cliente)
  { 
    path: '/checkout', 
    name: 'Checkout', 
    component: Checkout, 
    meta: { layout: 'client', requiresAuth: true } 
  },
  {
    path: '/externo/pedido/:token',
    name: 'GestionPedidoExterno',
    component: GestionPedidoExterno,
    meta: { 
      requiresAuth: false, 
      hideNavbar: true     
    }
  },
  { 
    path: '/web/registro', 
    name: 'RegistroCliente', 
    component: RegistroCliente, 
    meta: { layout: 'client' } 
  },
  { 
    path: '/proveedor/cotizar/:token', 
    name: 'CotizarExterno', 
    component: CotizarExterno,
    meta: { hideNavbar: true, public: true } 
  },

  // ---------------------------------------------------------------------------
  // 👤 ZONA CLIENTE (Requiere Auth + Rol CLIENTE)
  // ---------------------------------------------------------------------------
  { 
    path: '/cliente/dashboard', 
    name: 'DashboardCliente', 
    component: DashboardCliente, 
    meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } 
  },
  { 
    path: '/turnos/crear-web', 
    name: 'RegistrarTurnoWeb', 
    component: RegistrarTurnoWeb, 
    meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } 
  },
  { 
    path: '/cliente/historial', 
    name: 'HistorialTurnos', 
    component: HistorialTurnos, 
    meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } 
  },
  { 
    path: '/cliente/perfil', 
    name: 'PerfilCliente', 
    component: PerfilCliente, 
    meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } 
  },

  { 
  path: '/client/mis-pedidos', 
  name: 'MisPedidos', 
  component: MisPedidos, 
  meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } 
  },

  // ---------------------------------------------------------------------------
  // 🛡️ ZONA ADMINISTRATIVA (Requiere Auth + Rol ADMIN/STAFF)
  // ---------------------------------------------------------------------------
  
  // Dashboard
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true, role: 'ADMIN' } },

  // Usuarios
  { path: '/usuarios', name: 'ListadoUsuarios', component: ListadoUsuarios, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/usuarios/crear', name: 'RegistrarUsuario', component: RegistrarUsuario, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/usuarios/modificar/:id', name: 'ModificarUsuario', component: ModificarUsuario, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  
  // Turnos Admin
  { path: '/turnos', name: 'ListadoTurnos', component: ListadoTurnos, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/turnos/crear-presencial', name: 'RegistrarTurnoPresencial', component: RegistrarTurnoPresencial, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/turnos/modificar/:id', name: 'ModificarTurno', component: ModificarTurno, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/aceptar-oferta/:turno_id/:token', name: 'AceptarOferta', component: AceptarOferta, meta: { requiresAuth: true, role: 'ADMIN' } },

  // Servicios
  { path: '/servicios', name: 'ListadoServicios', component: ListadoServicios, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/servicios/crear', name: 'RegistrarServicio', component: RegistrarServicio, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/servicios/modificar/:id', name: 'ModificarServicio', component: ModificarServicio, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },

  // Categorías
  { path: '/categorias', name: 'ListadoCategorias', component: ListadoCategorias, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/categorias/crear', name: 'RegistrarCategoria', component: RegistrarCategoria, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/categorias/modificar/:id', name: 'ModificarCategoria', component: RegistrarCategoria, props: true, meta: { requiresAuth: true, role: 'ADMIN' } }, 

  // Roles
  { path: '/roles', name: 'ListadoRoles', component: ListadoRoles, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/roles/crear', name: 'RegistrarRol', component: RegistrarRol, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/roles/modificar/:id', name: 'ModificarRol', component: ModificarRol, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },

  // Productos y Marcas
  { path: '/productos', name: 'ListadoProductos', component: ListadoProductos, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/catalogo', name: 'CatalogoVisual', component: CatalogoVisual, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/crear', name: 'RegistrarProducto', component: RegistrarProducto, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/modificar/:id', name: 'ModificarProducto', component: ModificarProducto, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/marcas', name: 'ListadoMarcas', component: ListadoMarcas, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/marcas/crear', name: 'RegistrarMarca', component: RegistrarMarca, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/marcas/modificar/:id', name: 'ModificarMarca', component: EditarMarca, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },

  // Proveedores
  { path: '/proveedores', name: 'ListadoProveedores', component: ListadoProveedores, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/crear', name: 'RegistrarProveedor', component: RegistrarProveedor, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/modificar/:id', name: 'ModificarProveedor', component: ModificarProveedor, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/listas-precios', name: 'GestionListasPrecios', component: GestionListasPrecios, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/evaluacion', name: 'EvaluacionPresupuestos', component: EvaluacionPresupuestos, meta: { requiresAuth: true, role: 'ADMIN' } },
  
  // Ventas
  { path: '/ventas', name: 'ListadoVentas', component: ListadoVentas, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/ventas/crear', name: 'RegistrarVenta', component: RegistrarVenta, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/ventas/modificar/:id', name: 'ModificarVenta', component: ModificarVenta, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/ventas/detalle/:id', name: 'DetalleVenta', component: DetalleVenta, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },

  // Pedidos
  { path: '/pedidos', name: 'ListadoPedidos', component: ListadoPedidos, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/crear', name: 'RegistrarPedido', component: RegistrarPedido, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/modificar/:id', name: 'ModificarPedido', component: ModificarPedido, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/recibir/:id', name: 'RecibirPedido', component: RecibirPedido, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/detalle/:id', name: 'DetallePedido', component: DetallePedido, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },

  // Compra Cliente - Pedidos
  { path: '/compra-exitosa', name: 'CompraExitosa', component: CompraExitosa, meta: { requiresAuth: true} },
  { path: '/pedidos-web-admin', name: 'GestionPedidosWeb', component: GestionPedidosWeb, meta: { requiresAuth: true, role: 'ADMIN', layout: 'admin' } },
  
  // Auditoría
  { path: '/auditoria', name: 'ListadoAuditoria', component: ListadoAuditoria, meta: { requiresAuth: true, role: 'ADMIN' }},

  // 💰 Liquidación Sueldos (Nueva Ruta)
  { path: '/admin/liquidacion', name: 'LiquidacionSueldos', component: LiquidacionSueldos, meta: { requiresAuth: true, role: 'ADMIN' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// =============================================================================
// 🛡️ GUARDIA DE SEGURIDAD
// =============================================================================
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRol = localStorage.getItem('user_rol');

  // 1. Si la ruta requiere auth y NO hay token -> LOGIN
  if (to.meta.requiresAuth && !token) {
    return next('/login');
  } 

  // 2. Si la ruta es ZONA ADMIN (Staff)
  if (to.meta.role === 'ADMIN') {
    // Si el usuario es CLIENTE -> EXPULSAR A SU DASHBOARD
    if (userRol === 'CLIENTE') {
      return next('/cliente/dashboard');
    }
  }

  if (to.meta.role === 'CLIENTE') {
    // Se permite el acceso
  }

  next();
});

export default router;