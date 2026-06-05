from django.db import migrations
from datetime import time


def poblar_horarios(apps, schema_editor):
    HorarioAtencion = apps.get_model('usuarios', 'HorarioAtencion')
    dias = [
        {'dia_semana': 0, 'trabaja': True,  'apertura_m': time(8, 0),  'cierre_m': time(12, 0), 'apertura_t': time(15, 0), 'cierre_t': time(20, 0)},
        {'dia_semana': 1, 'trabaja': True,  'apertura_m': time(8, 0),  'cierre_m': time(12, 0), 'apertura_t': time(15, 0), 'cierre_t': time(20, 0)},
        {'dia_semana': 2, 'trabaja': True,  'apertura_m': time(8, 0),  'cierre_m': time(12, 0), 'apertura_t': time(15, 0), 'cierre_t': time(20, 0)},
        {'dia_semana': 3, 'trabaja': True,  'apertura_m': time(8, 0),  'cierre_m': time(12, 0), 'apertura_t': time(15, 0), 'cierre_t': time(20, 0)},
        {'dia_semana': 4, 'trabaja': True,  'apertura_m': time(8, 0),  'cierre_m': time(12, 0), 'apertura_t': time(15, 0), 'cierre_t': time(20, 0)},
        {'dia_semana': 5, 'trabaja': True,  'apertura_m': time(8, 0),  'cierre_m': time(12, 0), 'apertura_t': time(15, 0), 'cierre_t': time(20, 0)},
        {'dia_semana': 6, 'trabaja': False, 'apertura_m': None,        'cierre_m': None,        'apertura_t': None,        'cierre_t': None},
    ]
    for d in dias:
        HorarioAtencion.objects.create(
            dia_semana=d['dia_semana'],
            trabaja=d['trabaja'],
            hora_apertura_manana=d['apertura_m'],
            hora_cierre_manana=d['cierre_m'],
            hora_apertura_tarde=d['apertura_t'],
            hora_cierre_tarde=d['cierre_t'],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0116_horarioatencion'),
    ]

    operations = [
        migrations.RunPython(poblar_horarios),
    ]
