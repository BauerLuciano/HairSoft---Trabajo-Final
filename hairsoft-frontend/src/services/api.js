// src/services/api.js - VERSIÓN CORREGIDA Y DEFINITIVA
import axios from 'axios';

// === CONFIGURACIÓN INTELIGENTE Y CORREGIDA ===
const isProduction = window.location.hostname.includes('vercel.app');
const isLocalhost = window.location.hostname.includes('localhost') || 
                    window.location.hostname.includes('127.0.0.1');

// CORRECCIÓN: URL base
const CURRENT_URL = isProduction 
  ? 'https://web-production-ac47c.up.railway.app/usuarios/api' 
  : `http://${window.location.hostname}:8000/usuarios/api`;

console.log('🔌 API Conectada a:', CURRENT_URL);
console.log('🌍 Entorno:', isProduction ? 'Producción' : 'Local');
console.log('🏠 Localhost:', isLocalhost ? 'Sí' : 'No');

// ==============================================
// 🎯 DETECCIÓN INTELIGENTE DE ENDPOINTS
// ==============================================

// Lista de patrones de URLs que son EXCLUSIVOS de ADMIN (backend)
// Estos endpoints NO deben llevar token cuando estás en localhost
const ADMIN_ENDPOINTS = [
  '/admin/', // Django admin
  '/api/admin/', // API admin
  '/dashboard/', // Panel admin
  '/usuarios/lista', // Listado usuarios (admin)
  '/turnos/lista', // Listado turnos (admin)
  '/ventas/lista', // Listado ventas (admin)
  '/servicios/crear', // Crear servicio (admin)
  '/productos/crear', // Crear producto (admin)
  '/pedidos/lista', // Listado pedidos (admin)
  '/auditoria/', // Auditoría (admin)
  '/proveedores/', // Proveedores (admin)
  '/roles/', // Roles (admin)
  '/categorias/crear', // Categorías (admin)
  '/liquidacion/' // Liquidación sueldos (admin)
];

// Lista de patrones de URLs que son de CLIENTE/WEB
// Estos endpoints SÍ deben llevar token siempre
const CLIENT_ENDPOINTS = [
  '/usuarios/login', // Login cliente
  '/usuarios/registro', // Registro cliente
  '/turnos/crear', // Crear turno (web)
  '/turnos/registrar-interes', // Interés en horarios
  '/servicios/', // Listar servicios (público)
  '/categorias/servicios/', // Categorías servicios (público)
  '/peluqueros/', // Listar peluqueros (público)
  '/cliente/', // Perfil cliente
  '/web/', // Web pública
  '/checkout/', // Checkout cliente
  '/pedidos-web/', // Pedidos web cliente
  '/compra/' // Compra cliente
];

// Función para detectar si una URL es de ADMIN
const isAdminEndpoint = (url) => {
  if (!url) return false;
  
  // Verifica si la URL coincide con algún patrón de ADMIN
  return ADMIN_ENDPOINTS.some(endpoint => 
    url.includes(endpoint) && !url.includes('/crear-web') // Excepción: crear turno web es de cliente
  );
};

// Función para detectar si una URL es de CLIENTE
const isClientEndpoint = (url) => {
  if (!url) return false;
  
  // Verifica si la URL coincide con algún patrón de CLIENTE
  return CLIENT_ENDPOINTS.some(endpoint => url.includes(endpoint));
};

// ==============================================
// 🚀 CONFIGURACIÓN DE AXIOS
// ==============================================

// Instancia base de Axios
const api = axios.create({
  baseURL: CURRENT_URL,
  timeout: 15000, // Aumentado para desarrollo
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// ==============================================
// 🛡️ INTERCEPTOR DE PETICIONES INTELIGENTE
// ==============================================

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  const requestUrl = config.url || '';
  
  console.log(`📤 Petición a: ${requestUrl}`);
  console.log(`🔐 Token presente: ${token ? 'Sí' : 'No'}`);
  console.log(`🏠 Localhost: ${isLocalhost ? 'Sí' : 'No'}`);
  console.log(`👔 Endpoint Admin: ${isAdminEndpoint(requestUrl) ? 'Sí' : 'No'}`);
  console.log(`👤 Endpoint Cliente: ${isClientEndpoint(requestUrl) ? 'Sí' : 'No'}`);
  
  // 🎯 LÓGICA PRINCIPAL CORREGIDA:
  
  // 1. SI ES PRODUCCIÓN → SIEMPRE usar token si existe
  if (isProduction && token) {
    console.log('🚀 Producción: Enviando token');
    config.headers.Authorization = `Token ${token}`;
    config.withCredentials = false; // En producción no necesitamos cookies
  }
  
  // 2. SI ES LOCALHOST
  else if (isLocalhost) {
    // 2A. Si es endpoint de ADMIN → usar COOKIES, NO token
    if (isAdminEndpoint(requestUrl)) {
      console.log('💼 Localhost + Admin: Usando cookies (sin token)');
      config.withCredentials = true; // ¡IMPORTANTE! Para enviar cookies
      
      // 🚨 ELIMINAR EL TOKEN si existe (esto es clave)
      if (config.headers.Authorization) {
        delete config.headers.Authorization;
      }
    }
    
    // 2B. Si es endpoint de CLIENTE y hay token → usar token
    else if (isClientEndpoint(requestUrl) && token) {
      console.log('📱 Localhost + Cliente: Enviando token');
      config.headers.Authorization = `Token ${token}`;
      config.withCredentials = false; // No necesitamos cookies para cliente
    }
    
    // 2C. Si no es ni admin ni cliente conocido → lógica por defecto
    else {
      console.log('🤔 Localhost + Ruta desconocida: Usando lógica por defecto');
      
      // Si hay token y la ruta NO parece ser de admin, usar token
      if (token && !requestUrl.includes('/admin/')) {
        config.headers.Authorization = `Token ${token}`;
      } else {
        config.withCredentials = true; // Por defecto, cookies para localhost
      }
    }
  }
  
  // 3. SI NO ES LOCALHOST NI PRODUCCIÓN (otro entorno)
  else {
    console.log('🌐 Otro entorno: Usando token si existe');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
  }
  
  console.log(`📨 Headers finales:`, {
    Authorization: config.headers.Authorization ? 'Presente' : 'Ausente',
    withCredentials: config.withCredentials
  });
  
  return config;
  
}, error => {
  console.error('❌ Error en interceptor de petición:', error);
  return Promise.reject(error);
});

api.interceptors.response.use(
  response => {
    console.log(`📥 Respuesta de ${response.config.url}:`, response.status);
    return response;
  },
  error => {
    console.error('❌ Error de API:', {
      URL: error.config?.url,
      Status: error.response?.status,
      Message: error.response?.data?.message || error.message
    });
    
    // Manejo específico de errores 401 (No autorizado)
    if (error.response && error.response.status === 401) {
      console.warn('⚠️ Sesión expirada o token inválido');
      
      // Si estamos en localhost y es endpoint de admin, podría ser problema de cookies
      if (isLocalhost && isAdminEndpoint(error.config?.url)) {
        console.error('💥 ERROR CRÍTICO: Admin en localhost sin sesión de Django');
        console.info('💡 Solución: Asegurate de haber iniciado sesión en http://localhost:8000/admin');
      }
      
      // Si es endpoint de cliente, redirigir a login
      else if (isClientEndpoint(error.config?.url)) {
        console.warn('🔐 Cliente no autenticado, redirigiendo a login...');
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        
        // Solo redirigir si estamos en el cliente (no en admin)
        if (window.location.pathname.includes('/cliente') || 
            window.location.pathname.includes('/web')) {
          window.location.href = '/login';
        }
      }
    }
    
    // Manejo de errores 403 (Prohibido) - común cuando cliente intenta acceder a admin
    if (error.response && error.response.status === 403) {
      console.error('🚫 Acceso prohibido: Posible conflicto de autenticación');
      
      // Si es localhost y admin, podría ser que se envió token de cliente
      if (isLocalhost && isAdminEndpoint(error.config?.url)) {
        console.error('💥 CONFLICTO: Token de cliente enviado a endpoint de admin');
        console.info('💡 Solución: El interceptor debería haber eliminado el token');
        
        // Forzar recarga sin token
        localStorage.removeItem('token');
        window.location.reload();
      }
    }
    
    return Promise.reject(error);
  }
);

export const checkAuthStatus = () => {
  const token = localStorage.getItem('token');
  console.log('🔍 Estado de autenticación:');
  console.log('  - Token:', token ? 'Presente' : 'Ausente');
  console.log('  - Entorno:', isProduction ? 'Producción' : 'Local');
  console.log('  - Localhost:', isLocalhost ? 'Sí' : 'No');
  console.log('  - URL actual:', window.location.href);
  
  return {
    hasToken: !!token,
    isProduction,
    isLocalhost,
    currentUrl: window.location.href
  };
};

// Función para limpiar autenticación (útil para testing)
export const clearAuth = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user_id');
  console.log('🧹 Autenticación limpiada');
};

// Función para establecer modo de desarrollo (testing)
export const setDevMode = (mode) => {
  console.log(`⚙️ Modo desarrollo: ${mode}`);
  if (mode === 'admin') {
    // Para probar como admin, eliminar token
    localStorage.removeItem('token');
  } else if (mode === 'client') {
    // Para probar como cliente, necesitarías un token válido
    console.warn('⚠️ Para modo cliente, necesitas iniciar sesión primero');
  }
};



export default api;
export { isAdminEndpoint, isClientEndpoint, isLocalhost, isProduction };