import axios from 'axios';

const isProduction = window.location.hostname.includes('vercel.app');

// 💡 DEJAMOS LA URL LIMPIA (Sin el /usuarios/api al final)
const CURRENT_URL = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://localhost:8000';

const api = axios.create({
  baseURL: CURRENT_URL,
  timeout: 15000,
  withCredentials: true, // Para que el Admin local funcione con cookies
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  // Si la ruta no tiene /api/ ni /usuarios/, se lo ponemos nosotros
  if (config.url && !config.url.startsWith('http') && !config.url.startsWith('/api/') && !config.url.startsWith('/usuarios/')) {
    config.url = `/api${config.url.startsWith('/') ? '' : '/'}${config.url}`;
  }
  
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default api;