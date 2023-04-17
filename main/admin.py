from django.contrib import admin
from .models import *




class ComponentsAdmin(admin.TabularInline):
    model=ProductComponent
    
class GalleryAdmin(admin.TabularInline):
    model = ProductGallery
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price","qty_available","is_deleted"]
    list_editable = ["price", "qty_available","is_deleted"]
    inlines = [ComponentsAdmin,GalleryAdmin]
    save_as = True
    
    

class OrderItemAdmin(admin.TabularInline):
    model=OrderItem 
    
 
class PaymentAdmin(admin.TabularInline):
    model=PaymentDetail 
    
@admin.register(Order)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["booking_id", "is_deleted"]
    list_editable = ["is_deleted"]
    inlines = [OrderItemAdmin,PaymentAdmin]
    
@admin.register(OrderItem)
class ItemAdmin(admin.ModelAdmin):
    model = OrderItem
    list_display = ["order", "status",]
    list_filter = ["order", "status"]
    
admin.site.register([ProductCategory, ProductGallery, Location, ProductComponent, Cart, PayOuts, Commission, CaseSubCategory, CaseType, CaseMinorCategory, TermAndCondition])