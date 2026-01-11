import axios from 'axios';

// === CONFIGURACIÓN INTELIGENTE ===
// 1. Detectamos si estamos en Vercel o en tu compu
const isProduction = window.location.hostname.includes('vercel.app');

// 2. Elegimos la dirección correcta automáticamente
const CURRENT_URL = isProduction 
  ? 'https://web-production-ac47c.up.railway.app/usuarios/api' // URL NUBE
  : 'http://127.0.0.1:8000/usuarios/api';                       // URL LOCAL

console.log('🔌 API Conectada a:', CURRENT_URL);

// Instancia base
const api = axios.create({
  baseURL: CURRENT_URL,
  timeout: 10000,
  withCredentials: true, // <--- ¡ESTA ES LA LÍNEA QUE TE FALTA!
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor (El portero que pone el sello)
api.interceptors.request.use(config => {
  // 1. Buscamos la clave EXACTA que usa tu Login ('token')
  const token = localStorage.getItem('token'); 
  
  if (token) {
    // 2. Usamos el prefijo 'Token' que espera Django REST Framework
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