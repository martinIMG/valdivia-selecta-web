from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, CarritoProducto, Pedido, DetallePedido, Categoria # Agregamos Categoria
from django.contrib.auth.decorators import login_required
from django.db.models import Q      # Necesario para búsquedas
import operator                     # Nuevo
from functools import reduce        # Nuevo

# Asegúrate de tener estos imports arriba:
from django.db.models import Q
import operator
from functools import reduce

def catalogo(request):
    query = request.GET.get('q')
    productos = Producto.objects.all()

    if query:
        # 1. Separamos las palabras (Ej: "mujer verano" -> ["mujer", "verano"])
        palabras = query.split()
        
        # 2. Creamos un filtro para cada palabra
        # Busca que la palabra esté en: Nombre O Descripción O Categoría
        filtros = []
        for palabra in palabras:
            filtros.append(
                Q(nombre__icontains=palabra) | 
                Q(descripcion__icontains=palabra) |
                Q(categoria__nombre__icontains=palabra)
            )
        
        # 3. Aplicamos TODOS los filtros a la vez (AND)
        # Debe cumplir con "mujer" Y con "verano"
        if filtros:
            productos = productos.filter(reduce(operator.and_, filtros))
    
    return render(request, 'catalogo.html', {'productos': productos})

# --- NUEVA FUNCIÓN: AGREGAR AL CARRITO ---
def agregar_al_carrito(request, producto_id):
    # 1. Obtener el producto o dar error 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)

    # 2. Obtener el carrito del usuario (Lógica de Sesión vs Login)
    try:
        if request.user.is_authenticated:
            # Si está logueado, buscamos su carrito por usuario
            carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        else:
            # Si es visitante, buscamos por su ID de sesión
            if not request.session.session_key:
                request.session.create()
            session_id = request.session.session_key
            carrito, created = Carrito.objects.get_or_create(id_sesion=session_id)
        
        # 3. Agregar el producto al carrito
        # Buscamos si ya existe ese producto en este carrito
        item, created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto
        )
        
        # Si ya existía, no sumamos cantidad (es ropa americana única, stock 1)
        # O si prefieres sumar: item.cantidad += 1
        # item.save()

    except Exception as e:
        print(f"Error al agregar al carrito: {e}")

    # 4. Volver al catálogo
    return redirect('catalogo')
def ver_carrito(request):
    try:
        # 1. Intentamos obtener el carrito del usuario o sesión
        if request.user.is_authenticated:
            carrito = Carrito.objects.get(usuario=request.user)
        else:
            session_id = request.session.session_key
            carrito = Carrito.objects.get(id_sesion=session_id)
        
        # 2. Recuperamos los items y calculamos el total
        items = carrito.carritoproducto_set.all()
        total = sum(item.producto.precio * item.cantidad for item in items)
    
    except Carrito.DoesNotExist:
        # Si no hay carrito, mostramos todo vacío
        items = []
        total = 0

    return render(request, 'carrito.html', {'items': items, 'total': total})
def procesar_compra(request):
    # 1. Recuperar el carrito (misma lógica de siempre)
    try:
        if request.user.is_authenticated:
            carrito = Carrito.objects.get(usuario=request.user)
        else:
            session_id = request.session.session_key
            carrito = Carrito.objects.get(id_sesion=session_id)
    except Carrito.DoesNotExist:
        return redirect('catalogo') # Si no hay carrito, volver al inicio

    items = carrito.carritoproducto_set.all()
    if not items:
        return redirect('catalogo') # Carrito vacío

    # 2. Calcular total
    total_venta = sum(item.producto.precio * item.cantidad for item in items)

    # 3. Crear el Pedido (Simulamos que el pago fue exitoso)
    # Nota: Si el usuario es anónimo, asignamos None o un usuario genérico.
    # Para este ejemplo, asumiremos que si es anónimo, el pedido queda sin usuario vinculado (null).
    pedido = Pedido.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        total=total_venta,
        estado='PAGADO'
    )

    # 4. Mover items del Carrito a DetallePedido y Descontar Stock
    for item in items:
        # Crear detalle
        DetallePedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio
        )
        
        # DESCONTAR STOCK (Crítico para fardos únicos)
        item.producto.stock -= item.cantidad
        item.producto.save()

    # 5. Borrar el carrito (Limpieza)
    carrito.delete()

    # 6. Redirigir a pantalla de éxito
    return render(request, 'exito.html', {'id_pedido': pedido.id})
    # --- GESTIÓN DE USUARIOS (HU-01) ---

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Iniciar sesión automáticamente tras registrarse
            return redirect('catalogo')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        form = LoginUsuarioForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('catalogo')
    else:
        form = LoginUsuarioForm()
    return render(request, 'login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    return redirect('catalogo')

@login_required
def mis_pedidos(request):
    # Buscamos los pedidos ordenados del más reciente al más antiguo
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos})

# --- FUNCIÓN PARA ELIMINAR DEL CARRITO ---
def eliminar_item(request, producto_id):
    try:
        # 1. Buscamos el carrito del usuario
        if request.user.is_authenticated:
            carrito = Carrito.objects.get(usuario=request.user)
        else:
            carrito = Carrito.objects.get(id_sesion=request.session.session_key)
        
        # 2. Buscamos el producto específico dentro de ese carrito
        producto = get_object_or_404(Producto, id=producto_id)
        item = CarritoProducto.objects.get(carrito=carrito, producto=producto)
        
        # 3. Lo borramos
        item.delete()
    
    except Exception as e:
        print(f"Error al eliminar: {e}")

    # 4. Volvemos a mostrar el carrito actualizado
    return redirect('ver_carrito')

def catalogo_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    # Filtramos los productos que pertenecen a esa categoría
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'catalogo.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'detalle_producto.html', {'p': producto})