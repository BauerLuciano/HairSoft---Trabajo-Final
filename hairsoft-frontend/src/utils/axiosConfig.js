import axios from 'axios';

// 1. Apuntamos a la RAÍZ del servidor (importante para no duplicar 'usuarios/api')
const API_BASE = 'http://127.0.0.1:8000';

const axiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. Interceptor igual al de tu api.js (Usa 'token' y 'Token ' prefijo)
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

// 3. Interceptor de respuesta para evitar errores si la data viene sucia
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