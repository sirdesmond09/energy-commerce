from django.db import models
from django.core.validators import FileExtensionValidator
# Create your models here.
import uuid
from pprint import pprint


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=300, unique=True)
    desc = models.TextField()
    img = models.ImageField(
        upload_to='categories', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ])
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    @property
    def img_url(self):
        return self.img.url
        
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
    
    
    
class Product(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=300)
    amount = models.CharField(max_length=300)
    desc = models.TextField()
    price = models.FloatField()
    battery_type = models.CharField(max_length=255, choices= (("Tubular", "Tubular"),
                                                              ("lithium", "Lithium")),
                                    null=True)
    battery_cap = models.FloatField(null=True)
    total_power = models.FloatField(null=True)
    qty_available = models.PositiveIntegerField(default=0)
    locations = models.ManyToManyField("main.Location", blank=True)
    primary_img = models.ImageField(
        upload_to='products/primary_imgs', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ])
    vendor  = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    category = models.ForeignKey("main.ProductCategory", on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    @property
    def primary_img_url(self):
        return self.primary_img.url
    
    @property
    def category_name(self):
        return self.category.name
    
    @property
    def gallery(self):
        
        return self.images.all()
        
    
    @property
    def product_components(self):
        return self.components.all()
        
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
    

class ProductComponent(models.Model):
    item = models.CharField(max_length=200)
    capacity = models.FloatField()
    qty = models.PositiveIntegerField()
    item_type = models.CharField(max_length=255)
    product = models.ForeignKey("main.Product", on_delete=models.CASCADE, null=True, related_name="components")
    
    
class ProductGallery(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    product = models.ForeignKey("main.Product", on_delete=models.CASCADE, related_name="images", null=True)
    image = models.ImageField(
        upload_to='products/gallery', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ])
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.image.url
    
    
    
    
class Location(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)   
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    

class Address(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey("accounts.User", null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    address_1 = models.CharField(max_length=500)
    address_2 = models.CharField(max_length=500)
    delivery_instruction = models.TextField(blank=True, null=True)
    additional_instruction = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.address
    



class Order(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey("accounts.User", null=True, on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=10, unique=True,null=True)
    address = models.ForeignKey("main.Address", null=True, on_delete=models.CASCADE)
    shipping_fee = models.FloatField()
    installation_fee = models.FloatField()
    price = models.FloatField()
    payment_method=models.CharField(max_length=10)
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
        
        
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name="items")
    item = models.ForeignKey("main.Product", on_delete=models.DO_NOTHING)
    unit_price = models.FloatField(default=0)
    qty = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
    
    
    
class PaymentDetail(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, related_name="payment")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="payment")
    payment_type = models.CharField(max_length=300,
                                    choices=(("specta", "Specta"),
                                             ("outright", "Outright"),
                                              ("lease", "Lease To Own"),
                                              ("power-as-a-service", "Power as a service")))
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
    
    
    

class Cart(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    product =  models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    

    
   
    