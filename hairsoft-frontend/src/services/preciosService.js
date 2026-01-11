// hairsoft-frontend/src/services/preciosService.js
import axios from 'axios'

// --- DETECCIÓN AUTOMÁTICA DE ENTORNO ---
// Si estamos en Vercel (Nube), usa Railway.
// Si estamos en tu PC (Local), usa 127.0.0.1.
const isProduction = window.location.hostname.includes('vercel.app');

const API_BASE = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://127.0.0.1:8000';

export const preciosService = {
  // Obtener listas de precios de un proveedor
  async obtenerListasPorProveedor(proveedorId) {
    try {
      const response = await axios.get(
        `${API_BASE}/usuarios/api/listas-precios/por-proveedor/?proveedor_id=${proveedorId}`
      )
      return response.data
    } catch (error) {
      console.error('Error cargando listas de precios:', error)
      throw error
    }
  },

  // Crear nueva lista de precios
  async crearListaPrecio(datos) {
    try {
      const response = await axios.post(
        `${API_BASE}/usuarios/api/listas-precios/`,
        datos
      )
      return response.data
    } catch (error) {
      console.error('Error creando lista de precios:', error)
      throw error
    }
  },

  // Actualizar lista de precios existente
  async actualizarListaPrecio(id, datos) {
    try {
      const response = await axios.put(
        `${API_BASE}/usuarios/api/listas-precios/${id}/`,
        datos
      )
      return response.data
    } catch (error) {
      console.error('Error actualizando lista de precios:', error)
      throw error
    }
  },

  // Desactivar lista de precios
  async desactivarListaPrecio(id) {
    try {
      const response = await axios.post(
        `${API_BASE}/usuarios/api/listas-precios/${id}/desactivar/`
      )
      return response.data
    } catch (error) {
      console.error('Error desactivando lista de precios:', error)
      throw error
    }
  },

  // Calcular precios sugeridos para un pedido
  async calcularPreciosPedido(items) {
    try {
      const response = await axios.post(
        `${API_BASE}/usuarios/api/calcular-precios-pedido/`,
        { items }
      )
      return response.data
    } catch (error) {
      console.error('Error calculando precios:', error)
      throw error
    }
  },

  // Obtener historial de precios
  async obtenerHistorial(filtros = {}) {
    try {
      const params = new URLSearchParams()
      Object.keys(filtros).forEach(key => {
        if (filtros[key]) {
          params.append(key, filtros[key])
        }
      })
      
      const response = await axios.get(
        `${API_BASE}/usuarios/api/historial-precios/?${params}`
      )
      return response.data
    } catch (error) {
      console.error('Error cargando historial:', error)
      throw error
    }
  },

  // Calcular precio sugerido individual
  async calcularPrecioSugerido(productoId, proveedorId, cantidad) {
    try {
      const response = await axios.get(
        `${API_BASE}/usuarios/api/calcular-precio-sugerido/?producto_id=${productoId}&proveedor_id=${proveedorId}&cantidad=${cantidad}`
      )
      return response.data
    } catch (error) {
      console.error('Error calculando precio sugerido:', error)
      throw error
    }
  }
}

// Función helper para calcular descuentos por volumen
export const calcularDescuentoVolumen = (cantidad) => {
  if (cantidad >= 100) return 15.0
  if (cantidad >= 50) return 10.0
  if (cantidad >= 25) return 5.0
  return 0.0
}