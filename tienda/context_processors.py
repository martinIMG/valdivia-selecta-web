from .models import Carrito

def contador_carrito(request):
    total_items = 0
    try:
        # 1. Buscamos el carrito (Misma lógica que en las vistas)
        if request.user.is_authenticated:
            carrito = Carrito.objects.get(usuario=request.user)
        else:
            # Si no hay sesión iniciada, retornamos 0
            if not request.session.session_key:
                return {'cantidad_carrito': 0}
            carrito = Carrito.objects.get(id_sesion=request.session.session_key)

        # 2. Sumamos las cantidades de todos los productos
        items = carrito.carritoproducto_set.all()
        for item in items:
            total_items += item.cantidad

    except Carrito.DoesNotExist:
        total_items = 0
    
    # 3. Devolvemos la variable disponible para TODO el sitio
    return {'cantidad_carrito': total_items}