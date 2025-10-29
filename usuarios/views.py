from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.db import IntegrityError
from .serializers import UsuarioSerializer
from rest_framework import generics
from .models import Usuario

def _to_bool(val):
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    v = str(val).strip().lower()
    return v in ('true', '1', 'yes', 'on')

# Listar usuarios
class UsuarioListAPIView(generics.ListCreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                'error': 'Datos invalidos',
                'detalles': serializer.errors
            }, status=400)
        try:
            self.perform_create(serializer)
            return JsonResponse(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({
                'error': 'Error interno del servidor',
                'detalles': str(e)}, status=500)

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

class UsuarioDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return JsonResponse(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({
            'error': 'Usuario no encontrado',
            'detalles': str(e)}, status=404)
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if not serializer.is_valid():
                return JsonResponse({
                    'error': 'Datos invalidos',
                    'detalles': serializer.errors
                }, status=400)
            self.perform_update(serializer)
            return JsonResponse(serializer.data, status=200)
        except Usuario.DoesNotExist:
            return JsonResponse({
                'error': 'Usuario no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }, status=500)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return JsonResponse({'mensaje': 'Usuario eliminado exitosamente.'}, status=204)
        except Usuario.DoesNotExist:
            return JsonResponse({
                'error': 'Usuario no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': 'Error interno del servidor',
                'detalles': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class UsuarioAjaxView(generics.GenericAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def post(self, request, *args, **kwargs):
        """Crear nuevo usuario via AJAX (espera FormData)"""
        try:
            nombre = request.POST.get('nombre')
            identificacion = request.POST.get('identificacion')
            email = request.POST.get('email')
            activo_str = request.POST.get('activo', 'true')
            activo = _to_bool(activo_str)

            if not nombre or not identificacion or not email:
                return JsonResponse({'error': 'Faltan campos requeridos: nombre, identificacion o email.'}, status=400)

            try:
                usuario = Usuario.objects.create(
                    nombre=nombre,
                    identificacion=identificacion,
                    email=email,
                    activo=activo
                )
            except IntegrityError as ie:
                return JsonResponse({'error': 'Identificación o email ya registrados.'}, status=400)

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
        """Actualizar usuario via AJAX (acepta JSON o form-encoded)"""
        try:
            usuario = get_object_or_404(Usuario, pk=pk)

            # Soportar JSON (Content-Type: application/json) o form-encoded
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' in content_type:
                try:
                    payload = json.loads(request.body.decode('utf-8') or '{}')
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'JSON inválido'}, status=400)
                nombre = payload.get('nombre', usuario.nombre)
                identificacion = payload.get('identificacion', usuario.identificacion)
                email = payload.get('email', usuario.email)
                activo = _to_bool(payload.get('activo', usuario.activo))
            else:
                # form-encoded (puede venir como FormData)
                nombre = request.POST.get('nombre', usuario.nombre)
                identificacion = request.POST.get('identificacion', usuario.identificacion)
                email = request.POST.get('email', usuario.email)
                activo = _to_bool(request.POST.get('activo', usuario.activo))

            # Validaciones mínimas
            if not nombre or not identificacion or not email:
                return JsonResponse({'error': 'Los campos nombre, identificacion y email no pueden quedar vacíos.'}, status=400)

            # Aplicar cambios
            usuario.nombre = nombre
            usuario.identificacion = identificacion
            usuario.email = email
            usuario.activo = activo

            try:
                usuario.save()
            except IntegrityError:
                return JsonResponse({'error': 'Identificación o email ya registrados por otro usuario.'}, status=400)

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
