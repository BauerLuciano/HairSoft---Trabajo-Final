import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hairsoft.settings')

app = Celery('hairsoft')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuración adicional para Redis y manejo de tareas
app.conf.update(
    # Usar Redis como broker y backend (configurado en settings.py)
    broker_connection_retry_on_startup=True,
    # Configuración de reintentos para tareas
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,  # Importante para evitar que una tarea bloquee otras
)

# Tareas periódicas
app.conf.beat_schedule = {
    'verificar-ofertas-expiradas': {
        'task': 'usuarios.tasks.verificar_ofertas_expiradas',
        'schedule': 300.0,  # Cada 5 minutos
    },
    'reactivacion-clientes-inactivos': {
        'task': 'usuarios.tasks.procesar_reactivacion_clientes_inactivos',
        'schedule': 3600.0,  # Cada hora
    },
    'reposicion-automatica-stock': {
        'task': 'usuarios.tasks.chequear_stock_y_generar_solicitudes',
        'schedule': 60.0,  # Cada 1 minuto (para pruebas)
    },
    # Nueva tarea periódica para limpiar tokens expirados
    'limpiar-tokens-expirados': {
        'task': 'usuarios.tasks.limpiar_tokens_expirados',
        'schedule': 3600.0,  # Cada hora
    },
}

# Configuración de timezone (usará la de Django)
app.conf.timezone = 'America/Argentina/Buenos_Aires'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')