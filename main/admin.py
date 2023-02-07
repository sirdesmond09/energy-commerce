from django.contrib import admin
from .models import *




class ComponentsAdmin(admin.TabularInline):
    model=ProductComponent
    
class GalleryAdmin(admin.TabularInline):
    model = ProductGallery
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "is_deleted"]
    list_editable = ["is_deleted"]
    inlines = [ComponentsAdmin,GalleryAdmin]
    

admin.site.register([ProductCategory, ProductGallery, Location, ProductComponent])