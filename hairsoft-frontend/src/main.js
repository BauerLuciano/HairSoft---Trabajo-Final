// main.js - MODIFICADO
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import axios from 'axios';

// 1. Importar la librería de Google Login que instalaste
import vue3GoogleLogin from 'vue3-google-login';

// Importar Bootstrap solo si lo necesitas
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

axios.defaults.withCredentials = true;

// Crear la app
const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// 2. Inicializar Google Login con tu Client ID oficial
app.use(vue3GoogleLogin, {
  clientId: '537753408019-uhdhpoqgkqtbkaj25d90601n1f3qguth.apps.googleusercontent.com'
});

router.isReady().then(() => {
  console.log('✅ Router listo - montando app...');
  app.mount('#app');
});