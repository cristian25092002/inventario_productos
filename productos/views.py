from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .serializers import ProductoSerializer
from rest_framework import generics
from .models import Producto



#Listar productos
class ProductoListAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

#Eliminar productos
class ProductoDeleteAPIView(generics.DestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

#HTML Viewas para frontend  

class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/producto_list-html'
    context_object_name = 'productos'
    ordering = ['-creado']

class DemoView(ListView):
    model = Producto
    template_name = 'productos/demo.html'
    context_object_name = 'productos'

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('producto-list-html')
    context_object_name = 'producto'

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        messages.success(request, f'El producto "{producto.nombre}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
    


@method_decorator(csrf_exempt, name='dispatch')
class ProductoAjaxView(generics.GenericAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def post(self, request, *args, **kwargs):
        """Crear nuevo producto via AJAX"""
        try:
            data = {
                'nombre': request.POST.get('nombre'),
                'descripcion': request.POST.get('descripcion', ''),
                'precio': request.POST.get('precio'),
            }
        
            producto = Producto.objects.create(**data)
            return JsonResponse({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': str(producto.precio),
            'creado': producto.creado.strftime('%d/%m/%Y %H:%M'),
        })
        except Exception as e:  
            return JsonResponse({'error': str(e)}, status=400)
        

    def put(self, request, pk, *args, **kwargs):
        """Actualizar producto via AJAX"""
        try:
            producto = get_object_or_404(Producto, pk=pk)
            data = json.loads(request.body)

            producto.nombre = data.get('nombre', producto.nombre)
            producto.descripcion = data.get('descripcion', producto.descripcion)
            producto.precio = data.get('precio', producto.precio)
            producto.save()
            return JsonResponse({
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': str(producto.precio),
                'creado': producto.creado.strftime('%d/%m/%Y %H:%M'),
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


    def get(self, request, *args, **kwargs):
        productos = self.get_queryset()
        serializer = self.get_serializer(productos, many=True)
        return JsonResponse(serializer.data, safe=False)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        producto = get_object_or_404(Producto, pk=pk)
        producto.delete()
        return JsonResponse({'message': 'Producto eliminado exitosamente.'}, status=204)
