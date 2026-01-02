from django.contrib import admin
from django.urls import path
from . import views

app_name='Products_app'
urlpatterns = [
    path('list/', views.product_list, name='product_list'),
    path('register/', views.user_registration, name='user_registration'),
    path('login/', views.user_login, name='user_login'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:id>/', views.product_update, name='product_update'),
    path('delete/<int:id>/', views.product_delete, name='product_delete'),
]