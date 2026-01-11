import axios from 'axios';

// --- CONFIGURACIÓN FIJA (HARDCODEADA) ---
// Ponemos la URL de Railway directo. Así obligamos al celular a ir a la nube.
const API_URL = 'https://web-production-ac47c.up.railway.app';

console.log('🚀 Conectando DIRECTO a la Nube:', API_URL);

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para el Token
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