import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Importar CSS globales
import './styles/reset.css';
import './styles/base.css';
import './styles/formularios.css';
import './styles/login.css';
import './styles/modos.css';

const app = createApp(App);

app.use(router);

app.mount('#app');
