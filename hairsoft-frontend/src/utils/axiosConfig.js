import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

console.log('📡 Axios configurado en:', API_BASE_URL);

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  withCredentials: true, // Crucial para que el Admin local use Cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');

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