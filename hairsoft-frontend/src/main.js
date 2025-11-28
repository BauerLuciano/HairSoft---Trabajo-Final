// main.js - AGREGAR router.isReady()
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

// Importar CSS globales
import './styles/reset.css';
import './styles/base.css';
import './styles/formularios.css';
import './styles/modos.css';
import './styles/themes.css';

axios.defaults.withCredentials = true;

const app = createApp(App);
app.use(router);

router.isReady().then(() => {
  console.log('✅ Router listo - montando app...');
  app.mount('#app');
});