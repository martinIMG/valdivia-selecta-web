from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('pagar/', views.procesar_compra, name='procesar_compra'),
    path('registro/', views.registro, name='registro'), 
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('eliminar/<int:producto_id>/', views.eliminar_item, name='eliminar_item'),
    path('categoria/<int:categoria_id>/', views.catalogo_por_categoria, name='filtrar_categoria'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
]