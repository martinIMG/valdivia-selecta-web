from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

# HU-01: Usuario
class Usuario(AbstractUser):
    email = models.EmailField("Correo Electrónico", unique=True)
    telefono = models.CharField("Teléfono", max_length=15, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

# HU-02: Fardos
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self): return self.nombre

class Producto(models.Model):
    CALIDAD_OPCIONES = [('PREMIUM', 'Premium'), ('PRIMERA', 'Primera'), ('SEGUNDA', 'Segunda')]
    nombre = models.CharField("Nombre", max_length=100)
    descripcion = models.TextField("Descripción")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    calidad = models.CharField(max_length=20, choices=CALIDAD_OPCIONES, default='PRIMERA')
    peso_kg = models.DecimalField("Peso Kg", max_digits=5, decimal_places=2, default=45.00)
    precio = models.IntegerField("Precio", validators=[MinValueValidator(0)])
    stock = models.IntegerField("Stock", default=0, validators=[MinValueValidator(0)])
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    def __str__(self): return f"{self.nombre} ({self.peso_kg}kg)"

# HU-03: Pedidos
class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, default='PENDIENTE')

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.IntegerField()

class Carrito(models.Model):
    # Vinculamos el carrito a un usuario (si está registrado) o lo dejamos null si es visitante
    # Nota: Según tu PDF, se vincula a la sesión, pero el modelo pide Usuario.
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    id_sesion = models.CharField(max_length=100, null=True, blank=True) # Para usuarios no registrados
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Carrito de {self.usuario if self.usuario else self.id_sesion}"

class CarritoProducto(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

# Logs JSON
class AuditLog(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict)