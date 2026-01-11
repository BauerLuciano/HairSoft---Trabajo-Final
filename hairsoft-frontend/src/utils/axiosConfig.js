import axios from 'axios';

/**
 * LÓGICA INTELIGENTE DE URL:
 * 1. Si estamos en Vercel (Producción), usa la variable de entorno VITE_API_URL.
 * 2. Si estamos en tu PC (Local), usa 'http://localhost:8000'.
 */
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const axiosInstance = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // Importante para cookies y sesiones si las usas
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el Token automáticamente si existe
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axiosInstance;