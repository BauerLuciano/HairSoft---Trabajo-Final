// src/services/backupService.js
import api from './api';

export default {
    // Listar copias existentes + resumen por tipo
    listar() {
        return api.get('/backups/');
    },

    // Disparar la generación de una copia (Diario | Semanal | Mensual)
    generar(tipo) {
        return api.post('/backups/generar/', { tipo }, { timeout: 60000 });
    },

    // Verificar una copia con pg_restore -l
    verificar(ruta) {
        return api.post(`/backups/${ruta}/verificar/`);
    },

    // Descargar una copia (.backup)
    descargar(ruta) {
        return api.get(`/backups/${ruta}/descargar/`, { responseType: 'blob' });
    },

    // Últimos registros de backup.log
    leerLog() {
        return api.get('/backups/log/');
    }
};