import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/login.vue'
import ListadoUsuarios from '../views/ListadoUsuarios.vue'
import RegistrarUsuario from '../views/RegistrarUsuario.vue'
import ModificarUsuario from '../views/ModificarUsuario.vue'

const routes = [
  { path: '/', redirect: '/usuarios' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/usuarios', name: 'ListadoUsuarios', component: ListadoUsuarios },
  { path: '/usuarios/crear', name: 'RegistrarUsuario', component: RegistrarUsuario },
  { path: '/usuarios/modificar/:id', name: 'modificar-usuario', component: ModificarUsuario }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
