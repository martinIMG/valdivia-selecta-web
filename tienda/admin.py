from django.contrib import admin
from .models import Usuario, Categoria, Producto, Pedido, DetallePedido, AuditLog, Carrito, CarritoProducto
from django.db.models import Sum
from django.utils import timezone
# Configuración para Usuarios
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'telefono', 'is_staff')
    search_fields = ('email', 'username')

# Configuración para Fardos con Filtros
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'calidad', 'peso_kg', 'precio', 'stock')
    list_filter = ('calidad', 'categoria') # Filtros laterales para gestión rápida
    search_fields = ('nombre',)

# Configuración para ver los productos dentro del pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = [DetallePedidoInline]
    list_display = ('id', 'usuario', 'fecha', 'total', 'estado')
    list_filter = ('fecha', 'estado')
    
    # --- AQUI ESTÁ LA MAGIA DEL DASHBOARD ---
    change_list_template = 'admin/tienda/pedido/change_list.html'

    def changelist_view(self, request, extra_context=None):
        # 1. Calculamos datos
        total_ingresos = Pedido.objects.filter(estado='PAGADO').aggregate(Sum('total'))['total__sum'] or 0
        ventas_hoy = Pedido.objects.filter(fecha__date=timezone.now().date()).count()
        stock_bajo = Producto.objects.filter(stock__lte=3, stock__gt=0).count()
        
        # 2. Los empaquetamos para mandarlos al HTML
        extra_context = extra_context or {}
        extra_context['total_ingresos'] = total_ingresos
        extra_context['ventas_hoy'] = ventas_hoy
        extra_context['stock_bajo'] = stock_bajo
        
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Categoria)
admin.site.register(AuditLog)

class CarritoProductoInline(admin.TabularInline):
    model = CarritoProducto
    extra = 0

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'id_sesion', 'fecha_creacion')
    inlines = [CarritoProductoInline]