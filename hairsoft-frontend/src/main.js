// src/main.js

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios'; // 🛑 1. Importar Axios

// Importar CSS globales
import './styles/reset.css';
import './styles/base.css';
import './styles/formularios.css';
import './styles/login.css';
import './styles/modos.css';

// 🛑 2. Configuración Global de Axios
// Esto le dice a Axios que incluya las cookies (incluida la cookie de sesión de Django)
// en todas las peticiones, resolviendo los errores 401/403.
axios.defaults.withCredentials = true;

const app = createApp(App);

app.use(router);

app.mount('#app');