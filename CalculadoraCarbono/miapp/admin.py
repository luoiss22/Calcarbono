from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, RegistroHuellaCarbono, DetalleConsumo, DetalleTransporte, 
    DetalleEnergia, DetalleResiduos, RegistroReciclaje, Material, 
    MaterialReciclable, FactorEmision, Recomendacion, RecomendacionUsuario
)

# Personalizar el Admin de Usuario
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {'fields': ('nombre_completo', 'region', 'pais')}),
    )
    list_display = ('username', 'email', 'nombre_completo', 'region', 'pais', 'is_staff')
    search_fields = ('username', 'email', 'nombre_completo', 'region', 'pais')

# Agregar detalle de consumo inline en el admin de RegistroHuellaCarbono
class DetalleConsumoInline(admin.StackedInline):
    model = DetalleConsumo
    can_delete = False

class DetalleTransporteInline(admin.StackedInline):
    model = DetalleTransporte
    can_delete = False

class DetalleEnergiaInline(admin.StackedInline):
    model = DetalleEnergia
    can_delete = False

class DetalleResiduosInline(admin.StackedInline):
    model = DetalleResiduos
    can_delete = False

class MaterialReciclableInline(admin.TabularInline):
    model = MaterialReciclable
    extra = 1

# Admin para RegistroHuellaCarbono
class RegistroHuellaCarbonoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'huella_total', 'huella_consumo', 'huella_transporte', 'huella_energia', 'huella_residuos')
    list_filter = ('fecha', 'usuario')
    search_fields = ('usuario__username', 'usuario__email')
    date_hierarchy = 'fecha'
    inlines = [DetalleConsumoInline, DetalleTransporteInline, DetalleEnergiaInline, DetalleResiduosInline]

# Admin para RegistroReciclaje
class RegistroReciclajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'kg_total_reciclado', 'valor_economico_total', 'reduccion_co2_total')
    list_filter = ('fecha', 'usuario')
    search_fields = ('usuario__username', 'usuario__email')
    date_hierarchy = 'fecha'
    inlines = [MaterialReciclableInline]

# Admin para Material
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'unidad_medida', 'valor_por_unidad', 'factor_reduccion_co2')
    list_filter = ('tipo',)
    search_fields = ('nombre', 'tipo')

# Admin para FactorEmision
class FactorEmisionAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'subcategoria', 'region', 'valor', 'unidad', 'fecha_actualizacion')
    list_filter = ('categoria', 'region', 'fecha_actualizacion')
    search_fields = ('categoria', 'subcategoria', 'region', 'descripcion')
    date_hierarchy = 'fecha_actualizacion'

# Admin para Recomendacion
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'descripcion', 'impacto_potencial', 'nivel_dificultad', 'beneficio_economico_estimado')
    list_filter = ('categoria', 'nivel_dificultad')
    search_fields = ('descripcion', 'categoria')

# Admin para RecomendacionUsuario
class RecomendacionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'recomendacion', 'estado', 'fecha_asignacion', 'fecha_implementacion', 'impacto_real')
    list_filter = ('estado', 'fecha_asignacion', 'fecha_implementacion')
    search_fields = ('usuario__username', 'usuario__email', 'recomendacion__descripcion')
    date_hierarchy = 'fecha_asignacion'

# Registrar los modelos en el admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(RegistroHuellaCarbono, RegistroHuellaCarbonoAdmin)
admin.site.register(RegistroReciclaje, RegistroReciclajeAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(FactorEmision, FactorEmisionAdmin)
admin.site.register(Recomendacion, RecomendacionAdmin)
admin.site.register(RecomendacionUsuario, RecomendacionUsuarioAdmin)
