import axios from 'axios';

// === CONFIGURACIÓN INTELIGENTE (NO TOCA TU LÓGICA) ===
// 1. Detectamos si estamos en Vercel o en tu compu
const isProduction = window.location.hostname.includes('vercel.app');

// 2. Elegimos la dirección correcta automáticamente
const CURRENT_URL = isProduction 
  ? 'https://web-production-ac47c.up.railway.app/usuarios/api' // URL NUBE (Railway)
  : 'http://127.0.0.1:8000/usuarios/api';                       // URL LOCAL (Tu PC - Intacta)

console.log('🔌 API Conectada a:', CURRENT_URL);

// Instancia base
const api = axios.create({
  baseURL: CURRENT_URL, // <--- Acá está la magia
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor (El portero que pone el sello) - ESTO SIGUE IGUAL
api.interceptors.request.use(config => {
  // 1. Buscamos la clave EXACTA que usa tu Login ('token')
  const token = localStorage.getItem('token'); 
  
  if (token) {
    // 2. Usamos el prefijo 'Token' que espera Django REST Framework (no 'Bearer')
    config.headers.Authorization = `Token ${token}`; 
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Interceptor de respuesta (Para detectar sesión expirada) - ESTO SIGUE IGUAL
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      console.warn('Sesión expirada o token inválido');
      // Opcional: Redirigir al login si quieres automatizarlo
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;