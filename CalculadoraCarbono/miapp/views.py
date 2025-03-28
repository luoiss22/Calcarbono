from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import (
    Usuario, RegistroHuellaCarbono, DetalleConsumo, DetalleTransporte, 
    DetalleEnergia, DetalleResiduos, RegistroReciclaje, Material, 
    MaterialReciclable, FactorEmision, Recomendacion, RecomendacionUsuario
)
from .serializers import (
    UsuarioSerializer, UsuarioRegistroSerializer, RegistroHuellaCarbonoSerializer,
    DetalleConsumoSerializer, DetalleTransporteSerializer, DetalleEnergiaSerializer,
    DetalleResiduosSerializer, RegistroReciclajeSerializer, MaterialSerializer,
    MaterialReciclableSerializer, FactorEmisionSerializer, RecomendacionSerializer,
    RecomendacionUsuarioSerializer
)

# Usuario ViewSet
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'nombre_completo']
    
    def get_permissions(self):
        if self.action == 'create' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioRegistroSerializer
        return UsuarioSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        user = request.user
        
        # Obtener el último registro de huella de carbono
        ultimo_registro = RegistroHuellaCarbono.objects.filter(usuario=user).order_by('-fecha').first()
        
        # Obtener estadísticas de reciclaje
        registros_reciclaje = RegistroReciclaje.objects.filter(usuario=user).order_by('-fecha')[:5]
        
        # Obtener recomendaciones
        recomendaciones = Recomendacion.obtener_recomendaciones_para_usuario(user)
        
        # Construir respuesta
        response_data = {
            'huella_carbono': RegistroHuellaCarbonoSerializer(ultimo_registro).data if ultimo_registro else None,
            'reciclaje_reciente': RegistroReciclajeSerializer(registros_reciclaje, many=True).data,
            'recomendaciones': RecomendacionSerializer(recomendaciones, many=True).data
        }
        
        return Response(response_data)

# RegistroHuellaCarbono ViewSet
class RegistroHuellaCarbonoViewSet(viewsets.ModelViewSet):
    serializer_class = RegistroHuellaCarbonoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RegistroHuellaCarbono.objects.filter(usuario=self.request.user).order_by('-fecha')
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        registro = self.get_object()
        
        detalles = {
            'consumo': DetalleConsumoSerializer(registro.detalle_consumo).data if hasattr(registro, 'detalle_consumo') else None,
            'transporte': DetalleTransporteSerializer(registro.detalle_transporte).data if hasattr(registro, 'detalle_transporte') else None,
            'energia': DetalleEnergiaSerializer(registro.detalle_energia).data if hasattr(registro, 'detalle_energia') else None,
            'residuos': DetalleResiduosSerializer(registro.detalle_residuos).data if hasattr(registro, 'detalle_residuos') else None
        }
        
        return Response(detalles)
    
    @action(detail=False, methods=['get'])
    def historico(self, request):
        registros = self.get_queryset()
        
        # Datos para gráficos
        datos_historicos = []
        
        for registro in registros:
            datos_historicos.append({
                'fecha': registro.fecha,
                'huella_total': registro.huella_total,
                'huella_consumo': registro.huella_consumo,
                'huella_transporte': registro.huella_transporte,
                'huella_energia': registro.huella_energia,
                'huella_residuos': registro.huella_residuos,
                'reduccion_por_reciclaje': registro.reduccion_por_reciclaje
            })
        
        return Response(datos_historicos)
    
    @action(detail=True, methods=['get'])
    def comparar_promedio(self, request, pk=None):
        registro = self.get_object()
        comparacion = registro.comparar_con_promedio()
        return Response(comparacion)

# Material ViewSet
class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'tipo']
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        tipos = Material.TIPOS_MATERIAL
        
        resultado = {}
        for tipo_codigo, tipo_nombre in tipos:
            materiales = Material.objects.filter(tipo=tipo_codigo)
            resultado[tipo_codigo] = MaterialSerializer(materiales, many=True).data
        
        return Response(resultado)

# RegistroReciclaje ViewSet
class RegistroReciclajeViewSet(viewsets.ModelViewSet):
    serializer_class = RegistroReciclajeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RegistroReciclaje.objects.filter(usuario=self.request.user).order_by('-fecha')
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def agregar_material(self, request, pk=None):
        registro = self.get_object()
        
        serializer = MaterialReciclableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(registro_reciclaje=registro)
            
            # Recalcular totales
            registro.kg_total_reciclado = sum(m.cantidad for m in registro.materialreciclable_set.all())
            registro.calcular_valor_economico()
            registro.calcular_reduccion_co2()
            registro.save()
            
            # Si está vinculado a un registro de huella, actualizar reducción
            if registro.registro_huella:
                registro.registro_huella.reduccion_por_reciclaje = sum(
                    r.reduccion_co2_total for r in RegistroReciclaje.objects.filter(
                        registro_huella=registro.registro_huella
                    )
                )
                registro.registro_huella.calcular_huella_total()
                registro.registro_huella.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        # Obtener datos de reciclaje para generar estadísticas
        registros = self.get_queryset()
        
        # Estadísticas generales
        total_kg_reciclados = sum(r.kg_total_reciclado for r in registros)
        total_valor_economico = sum(r.valor_economico_total for r in registros)
        total_reduccion_co2 = sum(r.reduccion_co2_total for r in registros)
        
        # Estadísticas por tipo de material
        materiales_reciclados = MaterialReciclable.objects.filter(registro_reciclaje__in=registros)
        tipos_materiales = {}
        
        for material in materiales_reciclados:
            tipo = material.material.tipo
            if tipo not in tipos_materiales:
                tipos_materiales[tipo] = {
                    'nombre': material.material.get_tipo_display(),
                    'cantidad': 0,
                    'valor_economico': 0,
                    'reduccion_co2': 0
                }
            
            tipos_materiales[tipo]['cantidad'] += material.cantidad
            tipos_materiales[tipo]['valor_economico'] += material.valor_economico
            tipos_materiales[tipo]['reduccion_co2'] += material.reduccion_co2
        
        # Datos históricos mensuales
        # Esta implementación es simplificada, se podría mejorar con agregación de base de datos
        import datetime
        datos_mensuales = {}
        
        for registro in registros:
            mes_año = registro.fecha.strftime('%Y-%m')
            if mes_año not in datos_mensuales:
                datos_mensuales[mes_año] = {
                    'kg_reciclados': 0,
                    'valor_economico': 0,
                    'reduccion_co2': 0
                }
            
            datos_mensuales[mes_año]['kg_reciclados'] += registro.kg_total_reciclado
            datos_mensuales[mes_año]['valor_economico'] += registro.valor_economico_total
            datos_mensuales[mes_año]['reduccion_co2'] += registro.reduccion_co2_total
        
        return Response({
            'resumen': {
                'total_kg_reciclados': total_kg_reciclados,
                'total_valor_economico': total_valor_economico,
                'total_reduccion_co2': total_reduccion_co2,
                'numero_registros': registros.count()
            },
            'por_tipo_material': tipos_materiales,
            'historico_mensual': datos_mensuales
        })

# FactorEmision ViewSet
class FactorEmisionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FactorEmision.objects.all()
    serializer_class = FactorEmisionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['categoria', 'subcategoria', 'region']
    
    @action(detail=False, methods=['get'])
    def por_region(self, request):
        categoria = request.query_params.get('categoria')
        subcategoria = request.query_params.get('subcategoria')
        region = request.query_params.get('region')
        
        if not categoria:
            return Response({"error": "Debe especificar una categoría"}, status=status.HTTP_400_BAD_REQUEST)
        
        factor = FactorEmision.obtener_factor_por_region(categoria, subcategoria, region)
        
        if not factor:
            return Response({"error": "No se encontró un factor de emisión para los parámetros especificados"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(FactorEmisionSerializer(factor).data)

# Recomendacion ViewSet
class RecomendacionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Recomendacion.objects.all()
    serializer_class = RecomendacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['categoria', 'descripcion']
    
    @action(detail=False, methods=['get'])
    def personalizadas(self, request):
        limite = int(request.query_params.get('limite', 5))
        recomendaciones = Recomendacion.obtener_recomendaciones_para_usuario(request.user, limite)
        return Response(RecomendacionSerializer(recomendaciones, many=True).data)
    
    @action(detail=True, methods=['post'])
    def asignar(self, request, pk=None):
        recomendacion = self.get_object()
        
        # Verificar si ya existe una asignación
        existente = RecomendacionUsuario.objects.filter(usuario=request.user, recomendacion=recomendacion).first()
        
        if existente:
            return Response({"error": "Esta recomendación ya está asignada al usuario"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear nueva asignación
        recomendacion_usuario = RecomendacionUsuario.objects.create(
            usuario=request.user,
            recomendacion=recomendacion,
            estado='PENDIENTE'
        )
        
        serializer = RecomendacionUsuarioSerializer(recomendacion_usuario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# RecomendacionUsuario ViewSet
class RecomendacionUsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = RecomendacionUsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RecomendacionUsuario.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def actualizar_estado(self, request, pk=None):
        recomendacion_usuario = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado or nuevo_estado not in dict(RecomendacionUsuario.ESTADOS).keys():
            return Response({"error": "Estado no válido"}, status=status.HTTP_400_BAD_REQUEST)
        
        recomendacion_usuario.actualizar_estado(nuevo_estado)
        recomendacion_usuario.save()
        
        serializer = RecomendacionUsuarioSerializer(recomendacion_usuario)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def token_tester(request):
    """
    Vista para la página de prueba de token JWT.
    """
    return render(request, 'miapp/token_tester.html')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    """
    Punto de entrada principal a la API de Calculadora de Huella de Carbono.
    Para acceder a los endpoints protegidos, necesitas autenticarte:
    
    1. Obtén un token JWT en /api/token/
    2. Incluye el token en el encabezado Authorization: Bearer <token>
    """
    return Response({
        'endpoints_disponibles': {
            'usuarios': reverse('usuario-list', request=request, format=format),
            'huella_carbono': reverse('huella-carbono-list', request=request, format=format),
            'materiales': reverse('material-list', request=request, format=format),
            'reciclaje': reverse('reciclaje-list', request=request, format=format),
            'factores_emision': reverse('factor-emision-list', request=request, format=format),
            'recomendaciones': reverse('recomendacion-list', request=request, format=format),
            'mis_recomendaciones': reverse('mis-recomendaciones-list', request=request, format=format),
        },
        'autenticacion': {
            'obtener_token': reverse('token_obtain_pair', request=request, format=format),
            'refrescar_token': reverse('token_refresh', request=request, format=format),
            'probador_de_token': reverse('token_tester', request=request, format=format),
        },
        'documentacion': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
        },
        'mensaje': 'Para acceder, utiliza el login proporcionado o incluye un token JWT con el formato "Bearer <token>" en el encabezado Authorization.'
    })
