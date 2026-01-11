import axios from 'axios';

// 1. DETECCIÓN AUTOMÁTICA DE ENTORNO
// Si en la barra de direcciones dice "vercel.app", usa Railway.
// Si dice "localhost", usa tu PC.
const isProduction = window.location.hostname.includes('vercel.app');

const API_URL = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://localhost:8000';

console.log('🔌 Conectando a:', API_URL); // Para que veas en la consola a dónde apunta

const axiosInstance = axios.create({
  baseURL: API_URL,
  // 2. IMPORTANTE: Sacamos 'withCredentials' por ahora. 
  // Con Token Auth no es obligatorio y suele dar problemas de CORS con "Allowed Hosts *".
  // withCredentials: true, 
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el Token automáticamente
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