from django.contrib import admin
from django.urls import path
from . import views

app_name='Products_app'
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_page, name='login_page'),
    path('login-api/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('list/', views.product_list, name='product_list'),
    path('register/', views.user_registration, name='user_registration'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:id>/', views.product_update, name='product_update'),
    path('delete/<int:id>/', views.product_delete, name='product_delete'),
    # Admin: Manage products (add/update/delete)
    path('manage/', views.manage_products, name='manage_products'),
    path('manage/add/', views.add_product_page, name='add_product_page'),
    path('manage/edit/<int:id>/', views.edit_product_page, name='edit_product_page'),
    path('manage/delete/<int:id>/', views.delete_product_confirm, name='delete_product_confirm'),
    path('create-sample-products/', views.create_sample_products, name='create_sample_products'),
]