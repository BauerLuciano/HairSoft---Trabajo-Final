import axios from 'axios';

// 1. CONFIGURACIÓN DINÁMICA DE LA URL
// Si existe la variable de entorno (Vercel), usala. Si no, usá localhost (Tu PC).
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const axiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. Interceptor de Solicitud (Agrega el Token)
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token'); // Tu clave real
    if (token) {
      config.headers.Authorization = `Token ${token}`; // Tu prefijo real
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 3. Interceptor de Respuesta (Manejo de errores)
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("Error API:", error.response);
    return Promise.reject(error);
  }
);

export default axiosInstance;