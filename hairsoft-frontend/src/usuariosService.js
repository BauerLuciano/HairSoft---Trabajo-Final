import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/usuarios/api/clientes/';

export const obtenerClientes = async () => {
    try {
        const response = await axios.get(API_URL);
        return response.data;  // devuelve la lista de clientes en JSON
    } catch (error) {
        console.error('Error al obtener clientes:', error);
        return [];
    }
};
