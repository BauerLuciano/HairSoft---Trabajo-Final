import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
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

  if (typeof navigator !== 'undefined' && navigator.brave !== undefined) {
    config.headers['X-Navegador-Real'] = 'Brave';
  }

  return config;
});

export default api;