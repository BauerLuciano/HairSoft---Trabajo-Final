import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hairsoft.settings')

app = Celery('hairsoft')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Tareas periódicas
app.conf.beat_schedule = {
    'verificar-ofertas-expiradas': {
        'task': 'usuarios.tasks.verificar_ofertas_expiradas',
        'schedule': 300.0,  # Cada 5 minutos
    },
    # ✅ AGREGÁ ESTO para que se ejecute automáticamente cada 5 minutos:
    'reactivacion-clientes-inactivos': {
        'task': 'usuarios.tasks.procesar_reactivacion_clientes_inactivos',
        'schedule': 300.0,  # Cada 5 minutos (igual que la otra)
    },
}