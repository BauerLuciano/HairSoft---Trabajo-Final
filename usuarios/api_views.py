from rest_framework import viewsets, filters, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Auditoria, Servicio, Turno, Usuario, Rol
from .serializers import AuditoriaSerializer, ServicioSerializer, TurnoSerializer, UsuarioSerializer

# ============================================
# ✅ 1. API DE AUDITORÍA (LO NUEVO)
# ============================================
class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar y consultar detalles de auditoría.
    """
    # Optimizamos la consulta trayendo datos del usuario y su rol de una vez
    queryset = Auditoria.objects.select_related('usuario', 'usuario__rol').all().order_by('-fecha')
    serializer_class = AuditoriaSerializer
    permission_classes = [AllowAny] 
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['accion', 'modelo_afectado']
    # Buscamos por modelo, nombre de usuario o email
    search_fields = ['modelo_afectado', 'usuario__nombre', 'usuario__apellido', 'usuario__correo', 'objeto_id']

# ============================================
# ✅ 2. API VIEJA CORREGIDA (SOLUCIÓN AL ERROR)
# ============================================

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

# Peluqueros - ✅ CORREGIDO
class PeluqueroListAPIView(generics.ListAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # USAMOS rol__nombre PARA BUSCAR DENTRO DE LA TABLA RELACIONADA
        # Usamos 'icontains' para que encuentre "Peluquero", "peluquero" o "PELUQUERO"
        return Usuario.objects.filter(rol__nombre__icontains='Peluquero')

# Todos los usuarios con filtros - ✅ CORREGIDO
class UsuarioListAPIView(generics.ListAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Usuario.objects.all()
        q = self.request.GET.get('q')
        rol = self.request.GET.get('rol') # Ej: ?rol=Administrador

        if rol:
            # Corrección aquí también: filtrar por nombre del rol
            queryset = queryset.filter(rol__nombre__icontains=rol)
        
        if q:
            queryset = queryset.filter(nombre__icontains=q) | queryset.filter(apellido__icontains=q)
        
        return queryset