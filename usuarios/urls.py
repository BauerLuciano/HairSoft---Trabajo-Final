from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, TurnoViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'turnos', TurnoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
