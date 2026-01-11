import axios from 'axios';

// --- CÓDIGO INTELIGENTE ---
// Si la web es "vercel.app", usa la Nube. Si no, usa tu PC.
const isProduction = window.location.hostname.includes('vercel.app');
const BASE = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://127.0.0.1:8000'; // <--- ¡TU LOCAL SIGUE ACÁ!

const API_URL = `${BASE}/usuarios/api/clientes/`;

export const obtenerClientes = async () => {
    try {
        const response = await axios.get(API_URL);
        return response.data;
    } catch (error) {
        console.error('Error al obtener clientes:', error);
        return [];
    }
};