import { createRouter, createWebHistory } from 'vue-router'

// Auth
const Login = () => import('@/views/login.vue')
const SolicitarRecuperacion = () => import('@/views/auth/SolicitarRecuperacion.vue')
const NuevaPassword = () => import('@/views/auth/NuevaPassword.vue')

// --- VISTAS PÚBLICAS Y CLIENTE ---
const ServiciosPublico = () => import('@/views/publico/ServiciosPublico.vue')
const ProductosPublico = () => import('@/views/publico/ProductosPublico.vue')
const HomePublico = () => import('@/views/publico/HomePublico.vue')
const RegistroCliente = () => import('@/views/publico/RegistroCliente.vue')
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

const CompraExitosa = () => import('@/views/publico/CompraExitosa.vue')
const MisPedidos = () => import('@/views/cliente/MisPedidos.vue')
const GestionPedidosWeb = () => import('@/views/pedidos/GestionPedidosWeb.vue')

const ListadoAuditoria = () => import('@/views/auditoria/ListadoAuditoria.vue')
const LiquidacionSueldos = () => import('@/views/admin/LiquidacionSueldos.vue')

const routes = [
  { path: '/', redirect: '/web/home' },
  { path: '/login', name: 'Login', component: Login, meta: { hideNavbar: true } },
  { path: '/recuperar-password', name: 'RecuperarPassword', component: SolicitarRecuperacion, meta: { hideNavbar: true } },
  { path: '/recuperar-password/:token', name: 'NuevaPassword', component: NuevaPassword, meta: { hideNavbar: true } },

  // ZONA PÚBLICA
  { path: '/web/home', name: 'WebHome', component: HomePublico, meta: { layout: 'client' } },
  { path: '/web/servicios', name: 'ServiciosPublico', component: ServiciosPublico, meta: { layout: 'client' } },
  { path: '/web/productos', name: 'ProductosPublico', component: ProductosPublico, meta: { layout: 'client' } },
  { path: '/checkout', name: 'Checkout', component: Checkout, meta: { layout: 'client', requiresAuth: true } },
  { path: '/externo/pedido/:token', name: 'GestionPedidoExterno', component: GestionPedidoExterno, meta: { requiresAuth: false, hideNavbar: true } },
  { path: '/web/registro', name: 'RegistroCliente', component: RegistroCliente, meta: { layout: 'client' } },
  { path: '/proveedor/cotizar/:token', name: 'CotizarExterno', component: CotizarExterno, meta: { hideNavbar: true, public: true } },

  // ZONA CLIENTE
  { path: '/cliente/dashboard', name: 'DashboardCliente', component: DashboardCliente, meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } },
  { path: '/turnos/crear-web', name: 'RegistrarTurnoWeb', component: RegistrarTurnoWeb, meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } },
  { path: '/cliente/historial', name: 'HistorialTurnos', component: HistorialTurnos, meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } },
  { path: '/cliente/perfil', name: 'PerfilCliente', component: PerfilCliente, meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } },
  { path: '/client/mis-pedidos', name: 'MisPedidos', component: MisPedidos, meta: { layout: 'client', requiresAuth: true, role: 'CLIENTE' } },

  // ZONA ADMINISTRATIVA (Permitida para ADMIN, RECEPCIONISTA y PELUQUERO)
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/usuarios', name: 'ListadoUsuarios', component: ListadoUsuarios, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/usuarios/crear', name: 'RegistrarUsuario', component: RegistrarUsuario, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/usuarios/modificar/:id', name: 'ModificarUsuario', component: ModificarUsuario, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/turnos', name: 'ListadoTurnos', component: ListadoTurnos, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/turnos/crear-presencial', name: 'RegistrarTurnoPresencial', component: RegistrarTurnoPresencial, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/turnos/modificar/:id', name: 'ModificarTurno', component: ModificarTurno, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/aceptar-oferta/:turno_id/:token', name: 'AceptarOferta', component: AceptarOferta, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/servicios', name: 'ListadoServicios', component: ListadoServicios, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/servicios/crear', name: 'RegistrarServicio', component: RegistrarServicio, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/servicios/modificar/:id', name: 'ModificarServicio', component: ModificarServicio, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/categorias', name: 'ListadoCategorias', component: ListadoCategorias, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/categorias/crear', name: 'RegistrarCategoria', component: RegistrarCategoria, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/roles', name: 'ListadoRoles', component: ListadoRoles, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/roles/crear', name: 'RegistrarRol', component: RegistrarRol, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/roles/modificar/:id', name: 'ModificarRol', component: ModificarRol, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos', name: 'ListadoProductos', component: ListadoProductos, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/catalogo', name: 'CatalogoVisual', component: CatalogoVisual, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/crear', name: 'RegistrarProducto', component: RegistrarProducto, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/modificar/:id', name: 'ModificarProducto', component: ModificarProducto, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/marcas', name: 'ListadoMarcas', component: ListadoMarcas, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/marcas/crear', name: 'RegistrarMarca', component: RegistrarMarca, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/productos/marcas/modificar/:id', name: 'ModificarMarca', component: EditarMarca, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores', name: 'ListadoProveedores', component: ListadoProveedores, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/crear', name: 'RegistrarProveedor', component: RegistrarProveedor, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/modificar/:id', name: 'ModificarProveedor', component: ModificarProveedor, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/listas-precios', name: 'GestionListasPrecios', component: GestionListasPrecios, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/proveedores/evaluacion', name: 'EvaluacionPresupuestos', component: EvaluacionPresupuestos, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/ventas', name: 'ListadoVentas', component: ListadoVentas, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/ventas/crear', name: 'RegistrarVenta', component: RegistrarVenta, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/ventas/modificar/:id', name: 'ModificarVenta', component: ModificarVenta, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/ventas/detalle/:id', name: 'DetalleVenta', component: DetalleVenta, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos', name: 'ListadoPedidos', component: ListadoPedidos, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/crear', name: 'RegistrarPedido', component: RegistrarPedido, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/modificar/:id', name: 'ModificarPedido', component: ModificarPedido, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/recibir/:id', name: 'RecibirPedido', component: RecibirPedido, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/pedidos/detalle/:id', name: 'DetallePedido', component: DetallePedido, props: true, meta: { requiresAuth: true, role: 'ADMIN' } },
  { path: '/compra-exitosa', name: 'CompraExitosa', component: CompraExitosa, meta: { requiresAuth: true} },
  { path: '/pedidos-web-admin', name: 'GestionPedidosWeb', component: GestionPedidosWeb, meta: { requiresAuth: true, role: 'ADMIN', layout: 'admin' } },
  { path: '/auditoria', name: 'ListadoAuditoria', component: ListadoAuditoria, meta: { requiresAuth: true, role: 'ADMIN' }},
  { path: '/admin/liquidacion', name: 'LiquidacionSueldos', component: LiquidacionSueldos, meta: { requiresAuth: true, role: 'ADMIN' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRol = localStorage.getItem('user_rol'); // 'ADMINISTRADOR', 'RECEPCIONISTA', 'PELUQUERO'

  if (to.meta.requiresAuth && !token) {
    return next('/login');
  } 

  if (userRol === 'PELUQUERO') {
    if (to.path === '/dashboard' || to.path === '/') {
      return next('/turnos');
    }
  }

  const rolesGestion = ['ADMINISTRADOR', 'RECEPCIONISTA', 'PELUQUERO'];

  if (to.meta.role === 'ADMIN') {
    if (userRol === 'CLIENTE') {
      return next('/cliente/dashboard');
    }
    if (rolesGestion.includes(userRol)) {
      return next();
    }
  }

  next();
});

export default router;