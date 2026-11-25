import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

const BASE = API_BASE_URL;

export const preciosService = {
  async aplicarPorcentaje(payload) {
    const response = await axios.post(`${BASE}/api/precios/aplicar-porcentaje/`, payload);
    return response.data;
  },
  async simularAumento(payload) {
    const response = await axios.post(`${BASE}/api/precios/simular-aumento/`, payload);
    return response.data;
  },
  async simularBajada(payload) {
    const response = await axios.post(`${BASE}/api/precios/simular-bajada/`, payload);
    return response.data;
  },
  async simularRevertir(payload) {
    const response = await axios.post(`${BASE}/api/precios/simular-revertir/`, payload);
    return response.data;
  },
  async aplicarBajada(payload) {
    const response = await axios.post(`${BASE}/api/precios/aplicar-bajada/`, payload);
    return response.data;
  },
  async revertirPrecios(payload) {
    const response = await axios.post(`${BASE}/api/precios/revertir/`, payload);
    return response.data;
  },
  async getConteos() {
    const response = await axios.get(`${BASE}/api/precios/conteos/`);
    return response.data;
  },
  async getEstadisticas(filtros = {}) {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value);
      }
    });
    const response = await axios.get(`${BASE}/api/precios/estadisticas/?${params.toString()}`);
    return response.data;
  },
};
