// Mapeo de códigos de error de disponibilidad del backend a mensajes
// naturales para el usuario. Single source of truth usado por las vistas
// de reserva web y presencial.
const MAPEO = {
  PELUQUERO_OCUPADO: {
    title: 'Peluquero no disponible',
    message: 'El peluquero seleccionado ya tiene un turno en ese horario. Probá con otro horario.',
  },
  SILLA_OCUPADA: {
    title: 'Puesto no disponible',
    message: 'El puesto seleccionado ya está ocupado en ese horario. Probá con otro puesto u horario.',
  },
  SIN_SILLA_DISPONIBLE: {
    title: 'Horario no disponible',
    message: 'En ese horario ya no hay puestos de trabajo disponibles. Probá seleccionando otro horario.',
  },
  CLIENTE_YA_TIENE_TURNO: {
    title: 'Turno ya reservado',
    message: 'Ya tenés una reserva para esa fecha y hora. Elegí otro horario.',
  },
  FUERA_HORARIO_ATENCION: {
    title: 'Horario fuera de atención',
    message: 'El local no está disponible en ese horario. Elegí otro día u horario.',
  },
}

// Devuelve { title, message } si el code es conocido, o null para usar
// el comportamiento por defecto (fallback).
export function obtenerErrorDisponibilidad(code) {
  if (!code) return null
  return MAPEO[code] || null
}
