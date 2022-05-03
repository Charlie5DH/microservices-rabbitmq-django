from django.urls import path, include
from . import views

urlpatterns = [
    path('products/', views.get_products),
    path('products/id=<int:id>/', views.get_product),
    path('products/title=<str:title>/', views.get_product_by_title),
    path('products/random/', views.get_random_product),
    path('products/create/', views.create_product),
    path('products/update/', views.update_product),
    path('users/', views.get_random_user),
]