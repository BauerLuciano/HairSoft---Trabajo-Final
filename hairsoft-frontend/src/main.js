// main.js - MODIFICADO
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

// Importar Bootstrap solo si lo necesitas
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

axios.defaults.withCredentials = true;

// Crear la app
const app = createApp(App);
app.use(router);

router.isReady().then(() => {
  console.log('✅ Router listo - montando app...');
  app.mount('#app');
});

