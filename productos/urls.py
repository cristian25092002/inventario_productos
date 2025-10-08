from django.urls import path, include
from.views import (ProductoListView, ProductoDeleteView, DemoView,ProductoListAPIView,ProductoDeleteView,ProductoDeleteAPIView,ProductoDeleteAPIView,ProductoAjaxView)

urlpatterns = [

    #Api Endpoints
    path('api/productos/', ProductoListAPIView.as_view(), name='producto-list-api'),
    path('api/productos/<int:pk>/', ProductoDeleteAPIView.as_view(), name='producto-delete-api'),
    path('api/productos/<int:pk>/delete/', ProductoDeleteAPIView.as_view(), name='producto-delete-api'),

    #AJAX ENDPOINTS para el frontend
    path('ajax/productos/', ProductoAjaxView.as_view(), name='producto-ajax'),
    path('ajax/productos/<int:pk>/', ProductoAjaxView.as_view(), name='producto-ajax'),


    #HTML Frontend
    path('productos/', ProductoListView.as_view(), name='producto-list-html'),
    path('productos/<int:pk>/delete/', ProductoDeleteView.as_view(), name='producto-delete-html'),
    path('demo/', DemoView.as_view(), name='demo'),
    path('',ProductoListView.as_view(), name='home')
]

