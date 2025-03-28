from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Model for User
class Usuario(AbstractUser):
    nombre_completo = models.CharField(max_length=255, blank=True)
    fecha_registro = models.DateField(default=timezone.now)
    region = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, blank=True)
    
    def obtener_huella_promedio(self):
        registros = self.registrohuellacarbono_set.all()
        if not registros:
            return 0
        total = sum(registro.huella_total for registro in registros)
        return total / len(registros)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

# Model for Carbon Footprint Record
class RegistroHuellaCarbono(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    huella_total = models.FloatField(default=0)
    huella_consumo = models.FloatField(default=0)
    huella_transporte = models.FloatField(default=0)
    huella_energia = models.FloatField(default=0)
    huella_residuos = models.FloatField(default=0)
    reduccion_por_reciclaje = models.FloatField(default=0)
    
    def calcular_huella_total(self):
        self.huella_total = (
            self.huella_consumo + 
            self.huella_transporte + 
            self.huella_energia + 
            self.huella_residuos - 
            self.reduccion_por_reciclaje
        )
        return self.huella_total
    
    def obtener_datos_historicos(self):
        return RegistroHuellaCarbono.objects.filter(
            usuario=self.usuario
        ).order_by('fecha')
    
    def comparar_con_promedio(self):
        promedio_usuario = self.usuario.obtener_huella_promedio()
        return {
            'huella_actual': self.huella_total,
            'promedio_personal': promedio_usuario,
            'diferencia': self.huella_total - promedio_usuario
        }
    
    class Meta:
        verbose_name = 'Registro de Huella de Carbono'
        verbose_name_plural = 'Registros de Huella de Carbono'
        ordering = ['-fecha']

# Model for Consumption Details
class DetalleConsumo(models.Model):
    registro_huella = models.OneToOneField(RegistroHuellaCarbono, on_delete=models.CASCADE, related_name='detalle_consumo')
    consumo_carne_roja = models.FloatField(default=0)  # en kg/semana
    consumo_aves = models.FloatField(default=0)  # en kg/semana
    consumo_pescado = models.FloatField(default=0)  # en kg/semana
    consumo_lacteos = models.FloatField(default=0)  # en kg/semana
    consumo_frutas_verduras = models.FloatField(default=0)  # en kg/semana
    porcentaje_alimentos_importados = models.FloatField(default=0)  # en porcentaje
    compras_ropa_nuevas = models.IntegerField(default=0)  # prendas/mes
    compras_electronicos = models.IntegerField(default=0)  # dispositivos/año
    compras_online = models.IntegerField(default=0)  # compras/mes
    
    def calcular_emisiones_alimentacion(self):
        # Valores de ejemplo para factores de emisión (kg CO2 por kg de alimento)
        factor_carne_roja = 27.0
        factor_aves = 6.9
        factor_pescado = 5.4
        factor_lacteos = 1.9
        factor_frutas_verduras = 0.5
        factor_importacion = 1.1  # multiplicador para alimentos importados
        
        emisiones_base = (
            self.consumo_carne_roja * factor_carne_roja +
            self.consumo_aves * factor_aves +
            self.consumo_pescado * factor_pescado +
            self.consumo_lacteos * factor_lacteos +
            self.consumo_frutas_verduras * factor_frutas_verduras
        )
        
        # Ajustar por porcentaje de alimentos importados
        factor_ajuste = 1 + (self.porcentaje_alimentos_importados / 100) * (factor_importacion - 1)
        return emisiones_base * factor_ajuste * 4.35  # Convertir a mensual (4.35 semanas/mes)
    
    def calcular_emisiones_compras(self):
        # Factores de emisión para productos
        factor_ropa = 20  # kg CO2 por prenda
        factor_electronicos = 100  # kg CO2 por dispositivo
        factor_compras_online = 5  # kg CO2 por compra (incluye envío)
        
        return (
            self.compras_ropa_nuevas * factor_ropa +
            self.compras_electronicos * factor_electronicos / 12 +  # Anualizar
            self.compras_online * factor_compras_online
        )
    
    class Meta:
        verbose_name = 'Detalle de Consumo'
        verbose_name_plural = 'Detalles de Consumo'

# Model for Transport Details
class DetalleTransporte(models.Model):
    registro_huella = models.OneToOneField(RegistroHuellaCarbono, on_delete=models.CASCADE, related_name='detalle_transporte')
    km_vehiculo_gasolina = models.FloatField(default=0)  # km/mes
    km_vehiculo_diesel = models.FloatField(default=0)  # km/mes
    km_vehiculo_hibrido = models.FloatField(default=0)  # km/mes
    km_vehiculo_electrico = models.FloatField(default=0)  # km/mes
    km_autobus = models.FloatField(default=0)  # km/mes
    km_tren_metro = models.FloatField(default=0)  # km/mes
    vuelos_cortos = models.IntegerField(default=0)  # número de vuelos < 1000km/año
    vuelos_medianos = models.IntegerField(default=0)  # número de vuelos 1000-3000km/año
    vuelos_largos = models.IntegerField(default=0)  # número de vuelos > 3000km/año
    
    def calcular_emisiones_vehiculo_privado(self):
        # Factores de emisión (kg CO2 por km)
        factor_gasolina = 0.192
        factor_diesel = 0.171
        factor_hibrido = 0.106
        factor_electrico = 0.053  # Depende del mix eléctrico
        
        return (
            self.km_vehiculo_gasolina * factor_gasolina +
            self.km_vehiculo_diesel * factor_diesel +
            self.km_vehiculo_hibrido * factor_hibrido +
            self.km_vehiculo_electrico * factor_electrico
        )
    
    def calcular_emisiones_transporte_publico(self):
        # Factores de emisión (kg CO2 por km por pasajero)
        factor_autobus = 0.105
        factor_tren_metro = 0.041
        
        return (
            self.km_autobus * factor_autobus +
            self.km_tren_metro * factor_tren_metro
        )
    
    def calcular_emisiones_vuelos(self):
        # Factores de emisión (kg CO2 por vuelo)
        factor_vuelo_corto = 200  # Aproximadamente para vuelos < 1000km
        factor_vuelo_mediano = 600  # Aproximadamente para vuelos 1000-3000km
        factor_vuelo_largo = 1600  # Aproximadamente para vuelos > 3000km
        
        emision_anual = (
            self.vuelos_cortos * factor_vuelo_corto +
            self.vuelos_medianos * factor_vuelo_mediano +
            self.vuelos_largos * factor_vuelo_largo
        )
        
        # Convertir a mensual
        return emision_anual / 12
    
    class Meta:
        verbose_name = 'Detalle de Transporte'
        verbose_name_plural = 'Detalles de Transporte'

# Model for Energy Details
class DetalleEnergia(models.Model):
    TIPOS_CALEFACCION = [
        ('GAS', 'Gas Natural'),
        ('ELEC', 'Eléctrica'),
        ('LEÑA', 'Leña'),
        ('GASOLEO', 'Gasóleo'),
        ('BIOMASA', 'Biomasa'),
        ('NOCALEF', 'Sin Calefacción')
    ]
    
    registro_huella = models.OneToOneField(RegistroHuellaCarbono, on_delete=models.CASCADE, related_name='detalle_energia')
    consumo_electricidad_kwh = models.FloatField(default=0)  # kWh/mes
    porcentaje_energia_renovable = models.FloatField(default=0)  # porcentaje de energía verde
    consumo_gas_natural_m3 = models.FloatField(default=0)  # m³/mes
    consumo_agua_m3 = models.FloatField(default=0)  # m³/mes
    tipo_calefaccion = models.CharField(max_length=10, choices=TIPOS_CALEFACCION, default='NOCALEF')
    consumo_calefaccion = models.FloatField(default=0)  # depende del tipo (kWh o m³)
    
    def calcular_emisiones_electricidad(self):
        # Factor de emisión estándar para electricidad (kg CO2 por kWh)
        factor_electricidad = 0.31  # Depende del mix eléctrico del país
        
        # Ajustar por porcentaje de energía renovable
        factor_ajustado = factor_electricidad * (1 - self.porcentaje_energia_renovable / 100)
        
        return self.consumo_electricidad_kwh * factor_ajustado
    
    def calcular_emisiones_calefaccion(self):
        # Factores de emisión para diferentes tipos de calefacción
        factores = {
            'GAS': 0.20,  # kg CO2 por kWh
            'ELEC': 0.31,  # kg CO2 por kWh
            'LEÑA': 0.02,  # kg CO2 por kWh
            'GASOLEO': 0.27,  # kg CO2 por kWh
            'BIOMASA': 0.01,  # kg CO2 por kWh
            'NOCALEF': 0,  # Sin emisiones
        }
        
        return self.consumo_calefaccion * factores.get(self.tipo_calefaccion, 0)
    
    def calcular_emisiones_agua(self):
        # Factor de emisión para tratamiento y distribución de agua (kg CO2 por m³)
        factor_agua = 0.344
        
        return self.consumo_agua_m3 * factor_agua
    
    class Meta:
        verbose_name = 'Detalle de Energía'
        verbose_name_plural = 'Detalles de Energía'

# Model for Waste Details
class DetalleResiduos(models.Model):
    registro_huella = models.OneToOneField(RegistroHuellaCarbono, on_delete=models.CASCADE, related_name='detalle_residuos')
    kg_residuos_totales = models.FloatField(default=0)  # kg/mes
    kg_compostaje = models.FloatField(default=0)  # kg/mes
    
    def calcular_emisiones_residuos(self):
        # Factor de emisión para residuos (kg CO2 por kg de residuos)
        factor_residuos = 0.58
        
        # Calcular residuos netos (excluyendo compostaje)
        residuos_netos = max(0, self.kg_residuos_totales - self.kg_compostaje)
        
        return residuos_netos * factor_residuos
    
    def calcular_reduccion_compostaje(self):
        # Factor de reducción por compostaje (kg CO2 evitados por kg compostado)
        factor_compostaje = 0.24
        
        return self.kg_compostaje * factor_compostaje
    
    class Meta:
        verbose_name = 'Detalle de Residuos'
        verbose_name_plural = 'Detalles de Residuos'

# Model for Recycling Record
class RegistroReciclaje(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    registro_huella = models.ForeignKey(RegistroHuellaCarbono, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)
    kg_total_reciclado = models.FloatField(default=0)
    valor_economico_total = models.FloatField(default=0)  # en pesos MXN
    reduccion_co2_total = models.FloatField(default=0)  # en kg CO2
    
    def calcular_valor_economico(self):
        materiales = self.materialreciclable_set.all()
        total = sum(material.valor_economico for material in materiales)
        self.valor_economico_total = total
        return total
    
    def calcular_reduccion_co2(self):
        materiales = self.materialreciclable_set.all()
        total = sum(material.reduccion_co2 for material in materiales)
        self.reduccion_co2_total = total
        return total
    
    def obtener_estadisticas_reciclaje(self):
        materiales = self.materialreciclable_set.all()
        estadisticas = {}
        
        for material in materiales:
            tipo = material.material.tipo
            if tipo not in estadisticas:
                estadisticas[tipo] = {
                    'cantidad': 0,
                    'valor_economico': 0,
                    'reduccion_co2': 0
                }
            
            estadisticas[tipo]['cantidad'] += material.cantidad
            estadisticas[tipo]['valor_economico'] += material.valor_economico
            estadisticas[tipo]['reduccion_co2'] += material.reduccion_co2
        
        return estadisticas
    
    class Meta:
        verbose_name = 'Registro de Reciclaje'
        verbose_name_plural = 'Registros de Reciclaje'
        ordering = ['-fecha']

# Model for Material
class Material(models.Model):
    TIPOS_MATERIAL = [
        ('PAPEL', 'Papel y Cartón'),
        ('VIDRIO', 'Vidrio'),
        ('PLASTICO', 'Plástico'),
        ('METAL', 'Metal'),
        ('ORGANICO', 'Orgánico'),
        ('ELECTRONICO', 'Electrónico'),
        ('TEXTIL', 'Textil'),
        ('OTRO', 'Otro')
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15, choices=TIPOS_MATERIAL, default='OTRO')
    unidad_medida = models.CharField(max_length=10, default='kg')
    valor_por_unidad = models.FloatField(default=0)  # en pesos MXN por unidad
    factor_reduccion_co2 = models.FloatField(default=0)  # kg CO2 evitados por unidad
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'

# Model for Recyclable Material
class MaterialReciclable(models.Model):
    registro_reciclaje = models.ForeignKey(RegistroReciclaje, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.FloatField(default=0)
    unidad = models.CharField(max_length=10, default='kg')
    valor_economico = models.FloatField(default=0)  # en pesos MXN
    reduccion_co2 = models.FloatField(default=0)  # en kg CO2
    
    def calcular_valor_material(self):
        if self.unidad == self.material.unidad_medida:
            self.valor_economico = self.cantidad * self.material.valor_por_unidad
        else:
            # Si las unidades son diferentes, se necesitaría un factor de conversión
            # Por simplicidad, asumimos mismas unidades por ahora
            self.valor_economico = self.cantidad * self.material.valor_por_unidad
        return self.valor_economico
    
    def calcular_reduccion_co2_material(self):
        if self.unidad == self.material.unidad_medida:
            self.reduccion_co2 = self.cantidad * self.material.factor_reduccion_co2
        else:
            # Similar al caso anterior
            self.reduccion_co2 = self.cantidad * self.material.factor_reduccion_co2
        return self.reduccion_co2
    
    class Meta:
        verbose_name = 'Material Reciclable'
        verbose_name_plural = 'Materiales Reciclables'

# Model for Emission Factor
class FactorEmision(models.Model):
    categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    valor = models.FloatField()
    unidad = models.CharField(max_length=50)
    region = models.CharField(max_length=100, blank=True)
    fecha_actualizacion = models.DateField(default=timezone.now)
    fuente = models.CharField(max_length=255, blank=True)
    
    @classmethod
    def obtener_factor_por_region(cls, categoria, subcategoria=None, region=None):
        query = cls.objects.filter(categoria=categoria)
        
        if subcategoria:
            query = query.filter(subcategoria=subcategoria)
        
        if region:
            query = query.filter(region=region)
            if query.count() == 0:  # Si no hay factor específico para la región
                query = cls.objects.filter(categoria=categoria, region='')  # Factor por defecto
                if subcategoria:
                    query = query.filter(subcategoria=subcategoria)
        
        return query.order_by('-fecha_actualizacion').first()
    
    def __str__(self):
        return f"{self.categoria} - {self.subcategoria} ({self.region}): {self.valor} {self.unidad}"
    
    class Meta:
        verbose_name = 'Factor de Emisión'
        verbose_name_plural = 'Factores de Emisión'
        ordering = ['-fecha_actualizacion']

# Model for Recommendation
class Recomendacion(models.Model):
    CATEGORIAS = [
        ('CONSUMO', 'Consumo'),
        ('TRANSPORTE', 'Transporte'),
        ('ENERGIA', 'Energía'),
        ('RESIDUOS', 'Residuos'),
        ('RECICLAJE', 'Reciclaje'),
        ('GENERAL', 'General')
    ]
    
    categoria = models.CharField(max_length=15, choices=CATEGORIAS, default='GENERAL')
    descripcion = models.TextField()
    impacto_potencial = models.FloatField(default=0)  # kg CO2 que se podrían reducir
    nivel_dificultad = models.IntegerField(default=1)  # 1 (fácil) a 5 (difícil)
    beneficio_economico_estimado = models.FloatField(default=0)  # en pesos MXN
    
    @classmethod
    def obtener_recomendaciones_para_usuario(cls, usuario, limite=5):
        # Obtener el último registro de huella de carbono
        ultimo_registro = RegistroHuellaCarbono.objects.filter(usuario=usuario).order_by('-fecha').first()
        
        if not ultimo_registro:
            return cls.objects.filter(categoria='GENERAL').order_by('-impacto_potencial')[:limite]
        
        # Identificar el área con mayor huella
        emisiones = {
            'CONSUMO': ultimo_registro.huella_consumo,
            'TRANSPORTE': ultimo_registro.huella_transporte,
            'ENERGIA': ultimo_registro.huella_energia,
            'RESIDUOS': ultimo_registro.huella_residuos,
            'RECICLAJE': -ultimo_registro.reduccion_por_reciclaje
        }
        
        area_prioritaria = max(emisiones, key=emisiones.get)
        
        # Obtener recomendaciones personalizadas
        recomendaciones_prioritarias = cls.objects.filter(categoria=area_prioritaria).order_by('-impacto_potencial')[:limite]
        
        # Si no hay suficientes recomendaciones específicas, añadir generales
        if recomendaciones_prioritarias.count() < limite:
            recomendaciones_generales = cls.objects.filter(categoria='GENERAL').order_by('-impacto_potencial')
            return list(recomendaciones_prioritarias) + list(recomendaciones_generales[:limite - recomendaciones_prioritarias.count()])
        
        return recomendaciones_prioritarias
    
    def calcular_impacto_potencial_para_usuario(self, usuario):
        # Implementación básica, se podría mejorar con datos reales del usuario
        ultimo_registro = RegistroHuellaCarbono.objects.filter(usuario=usuario).order_by('-fecha').first()
        
        if not ultimo_registro:
            return self.impacto_potencial
        
        # Ajustar el impacto potencial según la categoría y la huella del usuario
        factor_ajuste = 1.0
        
        if self.categoria == 'CONSUMO':
            factor_ajuste = min(2.0, max(0.5, ultimo_registro.huella_consumo / 100))
        elif self.categoria == 'TRANSPORTE':
            factor_ajuste = min(2.0, max(0.5, ultimo_registro.huella_transporte / 150))
        elif self.categoria == 'ENERGIA':
            factor_ajuste = min(2.0, max(0.5, ultimo_registro.huella_energia / 120))
        elif self.categoria == 'RESIDUOS':
            factor_ajuste = min(2.0, max(0.5, ultimo_registro.huella_residuos / 50))
        elif self.categoria == 'RECICLAJE':
            factor_ajuste = min(2.0, max(0.5, 30 / (ultimo_registro.reduccion_por_reciclaje + 1)))
        
        return self.impacto_potencial * factor_ajuste
    
    def __str__(self):
        return f"{self.get_categoria_display()}: {self.descripcion[:50]}..."
    
    class Meta:
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'

# Model for User Recommendation
class RecomendacionUsuario(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
        ('DESCARTADA', 'Descartada')
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.CASCADE)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_implementacion = models.DateTimeField(null=True, blank=True)
    impacto_real = models.FloatField(null=True, blank=True)
    
    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        
        if nuevo_estado == 'COMPLETADA' and not self.fecha_implementacion:
            self.fecha_implementacion = timezone.now()
            self.calcular_impacto_real()
    
    def calcular_impacto_real(self):
        # En una implementación real, esto podría basarse en mediciones antes/después
        # Por ahora, usamos una aproximación simple basada en el impacto potencial
        if self.estado != 'COMPLETADA':
            self.impacto_real = 0
            return 0
        
        # Calculamos un impacto real que varía entre 70% y 120% del impacto potencial
        from random import uniform
        factor_efectividad = uniform(0.7, 1.2)
        
        self.impacto_real = self.recomendacion.impacto_potencial * factor_efectividad
        return self.impacto_real
    
    def __str__(self):
        return f"{self.usuario.username} - {self.recomendacion} ({self.get_estado_display()})"
    
    class Meta:
        verbose_name = 'Recomendación de Usuario'
        verbose_name_plural = 'Recomendaciones de Usuario'
        unique_together = ('usuario', 'recomendacion')
