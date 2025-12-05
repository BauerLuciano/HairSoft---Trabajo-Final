import axios from 'axios';

// Instancia base
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/usuarios/api', // Asegúrate que este puerto sea el tuyo
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor (El portero que pone el sello)
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

// Interceptor de respuesta (Para detectar sesión expirada)
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