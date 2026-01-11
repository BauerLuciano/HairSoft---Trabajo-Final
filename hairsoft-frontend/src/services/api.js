import axios from 'axios';

// === CONFIGURACIÓN INTELIGENTE Y CORREGIDA ===
const isProduction = window.location.hostname.includes('vercel.app');

// CORRECCIÓN: Usamos window.location.hostname para que coincida con tu navegador (localhost)
// y así las cookies de Admin funcionen.
const CURRENT_URL = isProduction 
  ? 'https://web-production-ac47c.up.railway.app/usuarios/api' 
  : `http://${window.location.hostname}:8000/usuarios/api`;

console.log('🔌 API Conectada a:', CURRENT_URL);

// Instancia base
const api = axios.create({
  baseURL: CURRENT_URL,
  timeout: 10000,
  withCredentials: true, // Vital para que el Admin local funcione
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor (El portero)
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token'); 
  
  // Detectar si estamos logueados como ADMIN en local (para no mandar token de cliente)
  // Si la URL es local y no hay token, dejamos que pasen las cookies.
  if (token) {
    config.headers.Authorization = `Token ${token}`; 
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Interceptor de respuesta
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      console.warn('Sesión expirada o token inválido');
    }
    return Promise.reject(error);
  }
);

export default api;