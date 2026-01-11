import axios from 'axios';

// --- DETECCIÓN DE ENTORNO (NO TOCA TU LÓGICA LOCAL) ---
// Si estamos en Vercel, usa Railway. Si no, usa tu 127.0.0.1 de siempre.
const isProduction = window.location.hostname.includes('vercel.app');
const BASE = isProduction 
  ? 'https://web-production-ac47c.up.railway.app' 
  : 'http://127.0.0.1:8000';

// Concatenamos la base con tu ruta original
const API_URL = `${BASE}/usuarios/api/clientes/`;

export const obtenerClientes = async () => {
    try {
        const response = await axios.get(API_URL);
        return response.data;  // devuelve la lista de clientes en JSON
    } catch (error) {
        console.error('Error al obtener clientes:', error);
        return [];
    }
};