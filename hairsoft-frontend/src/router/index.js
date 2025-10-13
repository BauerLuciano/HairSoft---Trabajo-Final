import { createRouter, createWebHistory } from 'vue-router'
import RegistrarTurno from '../views/RegistrarTurno.vue'
import Login from '../views/login.vue'
import RegistrarUsuario from '../views/RegistrarUsuario.vue'
import ListadoUsuarios from '../views/ListadoUsuarios.vue'

const routes = [
  // Ruta principal (home)
  {
    path: '/',
    redirect: '/usuarios'  // redirige automáticamente al listado
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/usuarios',
    name: 'Usuarios',
    component: ListadoUsuarios
  },
  {
    path: '/usuarios/crear',
    name: 'RegistrarUsuario',
    component: RegistrarUsuario
  },
  {
    path: '/turnos/registrar',
    name: 'RegistrarTurno',
    component: RegistrarTurno
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
