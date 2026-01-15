import factory
from django.contrib.auth import get_user_model
from .models import Rol, Producto, Marca, CategoriaProducto, MetodoPago, Servicio

User = get_user_model()

class RolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rol
    nombre = factory.Iterator(['Administrador', 'Peluquero', 'Recepcionista', 'Cliente'])

class UsuarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    nombre = factory.Faker('first_name')
    apellido = factory.Faker('last_name')
    correo = factory.Sequence(lambda n: f"user{n}@hairsoft.com")
    dni = factory.Sequence(lambda n: f"{30000000 + n}")
    telefono = "12345678"
    rol = factory.SubFactory(RolFactory)
    is_active = True

class MarcaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Marca
    nombre = factory.Faker('company')

class CategoriaProductoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoriaProducto
    nombre = factory.Sequence(lambda n: f"Categoria {n}")

class ProductoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Producto
    nombre = factory.Faker('word')
    precio = 1500.00
    stock_actual = 10
    stock_minimo = 2
    lote_reposicion = 5
    categoria = factory.SubFactory(CategoriaProductoFactory)
    marca = factory.SubFactory(MarcaFactory)

class MetodoPagoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetodoPago
    nombre = "Efectivo"
    tipo = "EFECTIVO"

class ServicioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Servicio
    nombre = "Corte de Pelo"
    precio = 2000.00
    duracion = 30