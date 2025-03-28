from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UsuarioViewSet, RegistroHuellaCarbonoViewSet, MaterialViewSet, 
    RegistroReciclajeViewSet, FactorEmisionViewSet, RecomendacionViewSet,
    RecomendacionUsuarioViewSet, api_root, token_tester
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'huella-carbono', RegistroHuellaCarbonoViewSet, basename='huella-carbono')
router.register(r'materiales', MaterialViewSet, basename='material')
router.register(r'reciclaje', RegistroReciclajeViewSet, basename='reciclaje')
router.register(r'factores-emision', FactorEmisionViewSet, basename='factor-emision')
router.register(r'recomendaciones', RecomendacionViewSet, basename='recomendacion')
router.register(r'mis-recomendaciones', RecomendacionUsuarioViewSet, basename='mis-recomendaciones')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token-tester/', token_tester, name='token_tester'),
]
