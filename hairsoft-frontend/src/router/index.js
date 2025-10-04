import { createRouter, createWebHistory } from 'vue-router'
import RegistrarTurno from '../views/RegistrarTurno.vue'
import Login from '../views/login.vue'
import RegistrarUsuario from '../views/RegistrarUsuario.vue'
import ListadoUsuarios from '../views/ListadoUsuarios.vue'

const routes = [
  {
    path: '/',
    name: 'RegistrarTurno',
    component: RegistrarTurno
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/usuarios/crear',
    name: 'RegistrarUsuario',
    component: RegistrarUsuario
  },
  {
    path: '/usuarios',
    name: 'ListadoUsuarios',
    component: ListadoUsuarios
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
