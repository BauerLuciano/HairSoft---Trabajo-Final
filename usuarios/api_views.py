# usuarios/api_views.py
from rest_framework import generics
from .models import Servicio, Turno, Usuario
from .serializers import ServicioSerializer, TurnoSerializer, UsuarioSerializer
from rest_framework.permissions import AllowAny

# Servicios
class ServicioListAPIView(generics.ListAPIView):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]

# Turnos
class TurnoListAPIView(generics.ListCreateAPIView):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [AllowAny]

# Peluqueros
class PeluqueroListAPIView(generics.ListAPIView):
    queryset = Usuario.objects.filter(rol='PEL')
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

# TODOS los usuarios (con filtro opcional)
class UsuarioListAPIView(generics.ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Usuario.objects.all()
        q = self.request.GET.get('q')
        rol = self.request.GET.get('rol')
        if rol:
            queryset = queryset.filter(rol=rol)
        if q:
            queryset = queryset.filter(nombre__icontains=q) | queryset.filter(apellido__icontains=q)
        return queryset
