// src/services/cajaService.js
import api from './api'; // Asegurate de que la ruta a tu instancia de axios sea correcta

export default {
    // Obtener las cajas físicas configuradas
    getCajas() {
        return api.get('/cajas/');
    },

    // Obtener la sesión abierta actualmente (si la hay)
    getSesionActual() {
        return api.get('/sesiones-caja/actual/');
    },

    // Abrir la caja (envía caja_id y saldo_inicial_efectivo)
    abrirCaja(data) {
        return api.post('/sesiones-caja/abrir/', data);
    },

    // Cerrar la caja / Arqueo (envía los saldos reales que contó el cajero)
    cerrarCaja(sesionId, data) {
        return api.post(`/sesiones-caja/${sesionId}/cerrar/`, data);
    },

    // Trae lo que el sistema dice que DEBERÍA haber en la caja
    getBalance(sesionId) {
        return api.get(`/sesiones-caja/${sesionId}/balance/`);
    },

    // Chequea si hay plata de turnos web que entró a la madrugada
    getPendientes() {
        return api.get('/movimientos-caja/pendientes/');
    },

    // Trae el historial de movimientos de una sesión específica
    getMovimientos(sesionId) {
        return api.get(`/movimientos-caja/?sesion_caja=${sesionId}`);
    },

    // Para cargar gastos manuales (yerba, retiros, etc)
    crearMovimientoManual(data) {
        return api.post('/movimientos-caja/', data);
    }
};