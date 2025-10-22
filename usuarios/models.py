from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre