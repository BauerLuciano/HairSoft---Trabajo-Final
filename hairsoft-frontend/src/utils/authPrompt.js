import Swal from 'sweetalert2'
import router from '@/router'

export function limpiarSesionLocal() {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  localStorage.removeItem('user_rol')
  localStorage.removeItem('user_nombre')
  localStorage.removeItem('user_apellido')
  localStorage.removeItem('login_fresh')
}

// Validación real del token contra el backend.
// Devuelve:
//  true  -> sesión válida
//  false -> sesión inválida (ya limpiada)
//  null  -> no se pudo verificar (red caída): se procede con la lógica normal
export async function sesionValida(api) {
  try {
    await api.get('/api/auth/verificar/')
    return true
  } catch (error) {
    if (error.response?.status === 401) {
      limpiarSesionLocal()
      return false
    }
    return null
  }
}

const ALERTAS = {
  booking: {
    titulo: 'Iniciá sesión para reservar tu turno',
    texto: 'Para reservar un turno necesitás tener una cuenta e iniciar sesión.',
    extra: '¿Todavía no tenés una? Podés registrarte para continuar con tu reserva.',
  },
  checkout: {
    titulo: 'Iniciá sesión para continuar con tu compra',
    texto: 'Para realizar tu compra necesitás tener una cuenta e iniciar sesión.',
    extra: '¿Todavía no tenés una? Podés registrarte para continuar con tu compra.',
    nota: 'Tus productos del carrito se conservarán.',
  },
}

// Alerta fija del sistema (no configurable): explica el motivo antes de ir a Login/Registro.
export function requireAuth({ action = 'booking', redirect = '/' }) {
  const cfg = ALERTAS[action] || ALERTAS.booking
  const notaHtml = cfg.nota
    ? `<br><br><small style="color:#64748b">${cfg.nota}</small>`
    : ''
  Swal.fire({
    title: `🔐 ${cfg.titulo}`,
    html: `${cfg.texto}<br><br>${cfg.extra}${notaHtml}`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Iniciar sesión',
    cancelButtonText: 'Crear cuenta',
    confirmButtonColor: '#0ea5e9',
    cancelButtonColor: '#64748b',
    reverseButtons: true,
  }).then((result) => {
    if (result.isConfirmed) {
      router.push({ name: 'Login', query: { redirect } })
    } else if (result.isDismissed && result.dismiss === Swal.DismissReason.cancel) {
      router.push({ path: '/web/registro', query: { redirect } })
    }
  })
}
