import api from './api'

export const envioService = {
  getConfigLocal() {
    return api.get('/api/configuracion-local/')
  },

  saveConfigLocal(data) {
    return api.post('/api/configuracion-local/', data)
  },

  calcularCosto(latitud, longitud) {
    return api.post('/api/envios/calcular/', { latitud, longitud })
  },

  crearEnvio(data) {
    return api.post('/api/envios/', data)
  },

  listarEnvios() {
    return api.get('/api/envios/')
  },

  cambiarEstado(id, estado) {
    return api.patch(`/api/envios/${id}/cambiar_estado/`, { estado })
  }
}
