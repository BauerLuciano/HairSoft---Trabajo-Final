import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

const BASE = API_BASE_URL;

const authAxios = () => {
    const token = localStorage.getItem('token');
    return axios.create({
        baseURL: BASE,
        headers: { 
            Authorization: token ? `Token ${token}` : '',
            'Content-Type': 'application/json'
        }
    });
};

export const obtenerClientes = () => authAxios().get('/api/clientes/');
export const crearCliente = (cliente) => authAxios().post('/api/clientes/', cliente);
export const eliminarCliente = (id) => authAxios().delete(`/api/clientes/${id}/`);
export const actualizarCliente = (id, cliente) => authAxios().put(`/api/clientes/${id}/`, cliente);
