import axios from 'axios';

// 1. Definimos la URL correcta automáticamente
// Si Vercel tiene la variable configurada, usa esa (Render). Si no, usa tu compu (Localhost).
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Nos aseguramos de que termine apuntando a /usuarios/api
// Si la variable de entorno ya trae la barra al final, se la sacamos para evitar errores (//)
const baseURL = `${API_URL.replace(/\/$/, '')}/usuarios/api`;

// 2. Instancia base de Axios
const api = axios.create({
  baseURL: baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 3. Interceptor de Solicitud (El que inyecta el Token)
api.interceptors.request.use(config => {
  // Buscamos el token guardado en el navegador
  const token = localStorage.getItem('token'); 
  
  if (token) {
    // Django REST Framework usa el prefijo 'Token ', no 'Bearer '
    config.headers.Authorization = `Token ${token}`; 
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 4. Interceptor de Respuesta (Manejo de errores globales)
api.interceptors.response.use(
  response => response,
  error => {
    // Si el error es 401 (No autorizado), significa que el token venció o es falso
    if (error.response && error.response.status === 401) {
      console.warn('Sesión expirada o token inválido');
      
      // Opcional: Forzar cierre de sesión si el token no sirve
      // localStorage.removeItem('token');
      // window.location.href = '/'; 
    }
    return Promise.reject(error);
  }
);

export default api;