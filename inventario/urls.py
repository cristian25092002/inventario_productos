from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('productos.urls')),
    path('', include('productos.urls')),
    path('usuarios/', include('usuarios.urls')),
]