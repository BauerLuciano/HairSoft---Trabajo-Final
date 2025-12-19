import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hairsoft.settings')

app = Celery('hairsoft')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Tareas periódicas
app.conf.beat_schedule = {
    'verificar-ofertas-expiradas': {
        'task': 'usuarios.tasks.verificar_ofertas_expiradas', # Asegúrate que esta tarea exista o cámbiala si tiene otro nombre
        'schedule': 300.0,
    },
    'reactivacion-clientes-inactivos': {
        'task': 'usuarios.tasks.procesar_reactivacion_clientes_inactivos',
        'schedule': 3600.0, 
    },
    'reposicion-automatica-stock': {
        'task': 'usuarios.tasks.chequear_stock_y_generar_solicitudes',
        'schedule': 60.0,  # Lo bajé a 1 minuto para que pruebes rápido si se dispara
    },
}