from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    RegistroHuellaCarbono, DetalleConsumo, DetalleTransporte, 
    DetalleEnergia, DetalleResiduos, RegistroReciclaje, 
    Material, MaterialReciclable, FactorEmision, 
    Recomendacion, RecomendacionUsuario
)

Usuario = get_user_model()

# Usuario Serializer
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'nombre_completo', 'fecha_registro', 'region', 'pais')
        read_only_fields = ('fecha_registro',)

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'password', 'nombre_completo', 'region', 'pais')
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

# DetalleConsumo Serializer
class DetalleConsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleConsumo
        fields = '__all__'

# DetalleTransporte Serializer
class DetalleTransporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleTransporte
        fields = '__all__'

# DetalleEnergia Serializer
class DetalleEnergiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleEnergia
        fields = '__all__'

# DetalleResiduos Serializer
class DetalleResiduosSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleResiduos
        fields = '__all__'

# RegistroHuellaCarbono Serializer
class RegistroHuellaCarbonoSerializer(serializers.ModelSerializer):
    detalle_consumo = DetalleConsumoSerializer(required=False)
    detalle_transporte = DetalleTransporteSerializer(required=False)
    detalle_energia = DetalleEnergiaSerializer(required=False)
    detalle_residuos = DetalleResiduosSerializer(required=False)
    
    class Meta:
        model = RegistroHuellaCarbono
        fields = '__all__'
        read_only_fields = ('huella_total', 'huella_consumo', 'huella_transporte', 'huella_energia', 'huella_residuos', 'reduccion_por_reciclaje')
    
    def create(self, validated_data):
        detalle_consumo_data = validated_data.pop('detalle_consumo', None)
        detalle_transporte_data = validated_data.pop('detalle_transporte', None)
        detalle_energia_data = validated_data.pop('detalle_energia', None)
        detalle_residuos_data = validated_data.pop('detalle_residuos', None)
        
        # Crear el registro principal
        registro = RegistroHuellaCarbono.objects.create(**validated_data)
        
        # Crear detalles si se proporcionaron
        if detalle_consumo_data:
            DetalleConsumo.objects.create(registro_huella=registro, **detalle_consumo_data)
            registro.huella_consumo = self._calcular_huella_consumo(registro)
        
        if detalle_transporte_data:
            DetalleTransporte.objects.create(registro_huella=registro, **detalle_transporte_data)
            registro.huella_transporte = self._calcular_huella_transporte(registro)
        
        if detalle_energia_data:
            DetalleEnergia.objects.create(registro_huella=registro, **detalle_energia_data)
            registro.huella_energia = self._calcular_huella_energia(registro)
        
        if detalle_residuos_data:
            DetalleResiduos.objects.create(registro_huella=registro, **detalle_residuos_data)
            registro.huella_residuos = self._calcular_huella_residuos(registro)
        
        # Calcular la huella total
        registro.calcular_huella_total()
        registro.save()
        
        return registro
    
    def update(self, instance, validated_data):
        detalle_consumo_data = validated_data.pop('detalle_consumo', None)
        detalle_transporte_data = validated_data.pop('detalle_transporte', None)
        detalle_energia_data = validated_data.pop('detalle_energia', None)
        detalle_residuos_data = validated_data.pop('detalle_residuos', None)
        
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar o crear detalles
        if detalle_consumo_data:
            detalle_consumo, created = DetalleConsumo.objects.get_or_create(
                registro_huella=instance,
                defaults=detalle_consumo_data
            )
            if not created:
                for attr, value in detalle_consumo_data.items():
                    setattr(detalle_consumo, attr, value)
                detalle_consumo.save()
            instance.huella_consumo = self._calcular_huella_consumo(instance)
        
        if detalle_transporte_data:
            detalle_transporte, created = DetalleTransporte.objects.get_or_create(
                registro_huella=instance,
                defaults=detalle_transporte_data
            )
            if not created:
                for attr, value in detalle_transporte_data.items():
                    setattr(detalle_transporte, attr, value)
                detalle_transporte.save()
            instance.huella_transporte = self._calcular_huella_transporte(instance)
        
        if detalle_energia_data:
            detalle_energia, created = DetalleEnergia.objects.get_or_create(
                registro_huella=instance,
                defaults=detalle_energia_data
            )
            if not created:
                for attr, value in detalle_energia_data.items():
                    setattr(detalle_energia, attr, value)
                detalle_energia.save()
            instance.huella_energia = self._calcular_huella_energia(instance)
        
        if detalle_residuos_data:
            detalle_residuos, created = DetalleResiduos.objects.get_or_create(
                registro_huella=instance,
                defaults=detalle_residuos_data
            )
            if not created:
                for attr, value in detalle_residuos_data.items():
                    setattr(detalle_residuos, attr, value)
                detalle_residuos.save()
            instance.huella_residuos = self._calcular_huella_residuos(instance)
        
        # Calcular la huella total
        instance.calcular_huella_total()
        instance.save()
        
        return instance
    
    def _calcular_huella_consumo(self, registro):
        try:
            detalle_consumo = registro.detalle_consumo
            return detalle_consumo.calcular_emisiones_alimentacion() + detalle_consumo.calcular_emisiones_compras()
        except DetalleConsumo.DoesNotExist:
            return 0
    
    def _calcular_huella_transporte(self, registro):
        try:
            detalle_transporte = registro.detalle_transporte
            return (
                detalle_transporte.calcular_emisiones_vehiculo_privado() +
                detalle_transporte.calcular_emisiones_transporte_publico() +
                detalle_transporte.calcular_emisiones_vuelos()
            )
        except DetalleTransporte.DoesNotExist:
            return 0
    
    def _calcular_huella_energia(self, registro):
        try:
            detalle_energia = registro.detalle_energia
            return (
                detalle_energia.calcular_emisiones_electricidad() +
                detalle_energia.calcular_emisiones_calefaccion() +
                detalle_energia.calcular_emisiones_agua()
            )
        except DetalleEnergia.DoesNotExist:
            return 0
    
    def _calcular_huella_residuos(self, registro):
        try:
            detalle_residuos = registro.detalle_residuos
            return detalle_residuos.calcular_emisiones_residuos()
        except DetalleResiduos.DoesNotExist:
            return 0

# Material Serializer
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

# MaterialReciclable Serializer
class MaterialReciclableSerializer(serializers.ModelSerializer):
    material_nombre = serializers.CharField(source='material.nombre', read_only=True)
    material_tipo = serializers.CharField(source='material.get_tipo_display', read_only=True)
    
    class Meta:
        model = MaterialReciclable
        fields = '__all__'
    
    def create(self, validated_data):
        material_reciclable = MaterialReciclable.objects.create(**validated_data)
        # Calcular valores económicos y de reducción
        material_reciclable.calcular_valor_material()
        material_reciclable.calcular_reduccion_co2_material()
        material_reciclable.save()
        return material_reciclable

# RegistroReciclaje Serializer
class RegistroReciclajeSerializer(serializers.ModelSerializer):
    materiales = MaterialReciclableSerializer(source='materialreciclable_set', many=True, required=False)
    
    class Meta:
        model = RegistroReciclaje
        fields = '__all__'
        read_only_fields = ('kg_total_reciclado', 'valor_economico_total', 'reduccion_co2_total')
    
    def create(self, validated_data):
        materiales_data = validated_data.pop('materialreciclable_set', [])
        registro = RegistroReciclaje.objects.create(**validated_data)
        
        # Crear materiales asociados
        for material_data in materiales_data:
            MaterialReciclable.objects.create(registro_reciclaje=registro, **material_data)
        
        # Actualizar valores calculados
        registro.kg_total_reciclado = sum(m.cantidad for m in registro.materialreciclable_set.all())
        registro.calcular_valor_economico()
        registro.calcular_reduccion_co2()
        registro.save()
        
        return registro

# FactorEmision Serializer
class FactorEmisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactorEmision
        fields = '__all__'

# Recomendacion Serializer
class RecomendacionSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Recomendacion
        fields = '__all__'

# RecomendacionUsuario Serializer
class RecomendacionUsuarioSerializer(serializers.ModelSerializer):
    recomendacion_detalle = RecomendacionSerializer(source='recomendacion', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = RecomendacionUsuario
        fields = '__all__'
        read_only_fields = ('fecha_asignacion', 'impacto_real')
    
    def update(self, instance, validated_data):
        if 'estado' in validated_data and validated_data['estado'] != instance.estado:
            instance.actualizar_estado(validated_data['estado'])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
