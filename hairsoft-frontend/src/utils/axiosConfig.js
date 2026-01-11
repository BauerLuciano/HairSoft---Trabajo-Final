import axios from 'axios';

// 1. Detección automática (No más URLs fijas)
const isProduction = window.location.hostname.includes('vercel.app');

const baseURL = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://localhost:8000';

console.log('📡 Axios configurado en:', baseURL);

const axiosInstance = axios.create({
  baseURL: baseURL,
  timeout: 15000,
  withCredentials: true, // Crucial para que el Admin local use Cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. Interceptor (El portero)
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    
    // CORRECCIÓN AUTOMÁTICA DE RUTAS
    // Si la ruta viene con /usuarios/api/ y NO es el perfil 'me', se lo sacamos
    // para que coincida con tu urls.py que usa 'api/'
    if (config.url && config.url.includes('/usuarios/api/') && !config.url.includes('/me/')) {
        config.url = config.url.replace('/usuarios/api/', '/api/');
    }

    if (token) {
      config.headers['Authorization'] = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;