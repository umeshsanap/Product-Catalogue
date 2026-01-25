from django.contrib import admin

# Register your models here.
from .models import Product

admin.site.site_header = "Product Catalog Admin"
admin.site.site_title = "Product Catalog"
admin.site.index_title = "Product Catalog Administration"

admin.site.register(Product)
