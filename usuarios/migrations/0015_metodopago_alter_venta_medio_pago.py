# usuarios/migrations/0016_metodopago_alter_venta_medio_pago.py (o el que te haya generado)
# ⚠️ ADVERTENCIA: Reemplaza este código con el contenido de tu nuevo archivo,
# pero asegúrate de mantener las importaciones originales (apps, migrations, etc.)

from django.db import migrations, models
import django.db.models.deletion

def migrar_medios_pago(apps, schema_editor):
    Venta = apps.get_model('usuarios', 'Venta')
    MetodoPago = apps.get_model('usuarios', 'MetodoPago')

    # 1. Crear el método de pago 'EFECTIVO' y guardarlo.
    # Asumimos que es el valor por defecto que tienen todas las ventas viejas.
    metodo_efectivo, creado = MetodoPago.objects.get_or_create(
        nombre='EFECTIVO',
        defaults={'descripcion': 'Pagos antiguos en efectivo.'}
    )
    
    # 2. Actualizar todas las ventas viejas para que apunten al nuevo ID.
    # El campo medio_pago sigue siendo CharField aquí, ¡así que podemos leer el texto!
    Venta.objects.filter(medio_pago='EFECTIVO').update(medio_pago_id=metodo_efectivo.pk)

    # 3. Eliminar los valores antiguos que ya no sirven (si hay otros valores, fallará, 
    # pero este es el caso más simple y directo para el valor 'EFECTIVO').
    # Si tienes otros valores como 'TARJETA' también debes crearlos aquí.


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0014_venta_detalleventa'), # <--- ⚠️ IMPORTANTE: Mantén la dependencia anterior
    ]

    operations = [
        # 1. Crear la tabla MetodoPago
        migrations.CreateModel(
            name='MetodoPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Método de Pago',
                'db_table': 'metodos_pago',
            },
        ),
        
        # 2. Añadir la nueva columna medio_pago_id (temporal) y hacerla nula.
        migrations.AddField(
            model_name='venta',
            name='medio_pago_id',
            field=models.ForeignKey(blank=True, help_text='Método de pago utilizado para esta transacción.', null=True, on_delete=django.db.models.deletion.PROTECT, to='usuarios.metodopago'),
        ),

        # 3. Ejecutar la función de migración de datos (esto llena la nueva columna con IDs)
        migrations.RunPython(migrar_medios_pago, migrations.RunPython.noop),
        
        # 4. Eliminar la columna de texto antigua
        migrations.RemoveField(
            model_name='venta',
            name='medio_pago',
        ),
        
        # 5. Renombrar la nueva columna de clave foránea a 'medio_pago' (el nombre original)
        migrations.RenameField(
            model_name='venta',
            old_name='medio_pago_id',
            new_name='medio_pago',
        ),
    ]