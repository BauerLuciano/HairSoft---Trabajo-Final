import axios from 'axios';

// ============================================================
// CONFIGURACIÓN DE CONEXIÓN (MODO NUCLEAR)
// ============================================================

// 1. Ponemos la URL de Render A FUEGO. 
// Así es imposible que el celular se confunda con localhost.
// REEMPLAZÁ esta URL por la tuya de Render si es diferente.
const API_URL = 'https://hairsoft-backend.onrender.com'; 

// NOTA: Si querés volver a probar en tu compu (local), descomentá la línea de abajo:
// const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  // Aseguramos que apunte a la carpeta correcta de la API
  baseURL: `${API_URL}/usuarios/api`, 
  
  // Aumentamos el tiempo de espera a 15 segundos (los datos móviles a veces son lentos)
  timeout: 15000, 
  
  headers: {
    'Content-Type': 'application/json',
  }
});

// ============================================================
// INTERCEPTORES (Igual que antes, esto funciona bien)
// ============================================================

// 2. Interceptor de Solicitud (Inyecta el Token)
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token'); 
  
  if (token) {
    // Django espera 'Token <tu_codigo>', no 'Bearer'
    config.headers.Authorization = `Token ${token}`; 
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 3. Interceptor de Respuesta (Maneja errores de sesión)
api.interceptors.response.use(
  response => response,
  error => {
    // Si la respuesta es 401, el token no sirve
    if (error.response && error.response.status === 401) {
      console.warn('Sesión expirada o token inválido');
      // Si querés que lo saque al login automáticamente, descomentá esto:
      // localStorage.removeItem('token');
      // window.location.href = '/login'; 
    }
    return Promise.reject(error);
  }
);

export default api;