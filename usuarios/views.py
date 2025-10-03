from rest_framework import viewsets, filters
from .models import Usuario, Turno
from .serializers import UsuarioSerializer, TurnoSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'email']


class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['fecha', 'servicio', 'usuario__nombre']
