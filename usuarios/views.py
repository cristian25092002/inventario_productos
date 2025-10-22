from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .serializers import UsuarioSerializer
from rest_framework import generics
from .models import Usuario

# Listar usuarios
class UsuarioListAPIView(generics.ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

# Eliminar usuarios
class UsuarioDeleteAPIView(generics.DestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

# Vistas HTML para frontend

class UsuarioListView(ListView):
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    ordering = ['-fecha_registro']

class DemoView(ListView):
    model = Usuario
    template_name = 'usuarios/demo.html'
    context_object_name = 'usuarios'

class UsuarioDeleteView(DeleteView):
    model = Usuario
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario-list-html')
    context_object_name = 'usuario'

    def form_valid(self, form):
        usuario = self.get_object()
        print("----------------------------------------------------------")
        print(f"DELETE request received - Eliminando Usuario: {usuario.nombre} (ID: {usuario.id})")
        messages.success(self.request, f'El usuario "{usuario.nombre}" eliminado exitosamente.')
        return super().form_valid(form)

@method_decorator(csrf_exempt, name='dispatch')
class UsuarioAjaxView(generics.GenericAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def post(self, request, *args, **kwargs):
        """Crear nuevo usuario via AJAX"""
        try:
            nombre = request.POST.get('nombre')
            identificacion = request.POST.get('identificacion')
            email = request.POST.get('email')
            activo_str = request.POST.get('activo', 'true')
            activo = True if activo_str == 'true' else False

            if not nombre or not identificacion or not email:
                return JsonResponse({'error': 'Faltan campos requeridos.'}, status=400)

            usuario = Usuario.objects.create(
                nombre=nombre,
                identificacion=identificacion,
                email=email,
                activo=activo
            )
            return JsonResponse({
                'id': usuario.id,
                'nombre': usuario.nombre,
                'identificacion': usuario.identificacion,
                'email': usuario.email,
                'fecha_registro': usuario.fecha_registro.strftime('%d/%m/%Y %H:%M'),
                'activo': usuario.activo,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def put(self, request, pk, *args, **kwargs):
        """Actualizar usuario via AJAX"""
        try:
            usuario = get_object_or_404(Usuario, pk=pk)
            data = json.loads(request.body)
            usuario.nombre = data.get('nombre', usuario.nombre)
            usuario.identificacion = data.get('identificacion', usuario.identificacion)
            usuario.email = data.get('email', usuario.email)
            usuario.activo = data.get('activo', usuario.activo)
            usuario.save()
            return JsonResponse({
                'id': usuario.id,
                'nombre': usuario.nombre,
                'identificacion': usuario.identificacion,
                'email': usuario.email,
                'fecha_registro': usuario.fecha_registro.strftime('%d/%m/%Y %H:%M'),
                'activo': usuario.activo,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get(self, request, *args, **kwargs):
        usuarios = self.get_queryset()
        serializer = self.get_serializer(usuarios, many=True)
        return JsonResponse(serializer.data, safe=False)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.delete()
        return JsonResponse({'message': 'Usuario eliminado exitosamente.'}, status=204)