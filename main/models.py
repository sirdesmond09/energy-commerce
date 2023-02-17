from django.db import models
from django.core.validators import FileExtensionValidator
# Create your models here.
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

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
        
    def __str__(self):
        return self.name

    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
    
    
    
class Product(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=300)
    brand = models.CharField(max_length=300)
    desc = models.TextField()
    price = models.FloatField()
    battery_type = models.CharField(max_length=255, choices= (("Tubular", "Tubular"),
                                                              ("lithium", "Lithium")),
                                    null=True, blank=True)
    battery_cap = models.FloatField(null=True, blank=True)
    total_power = models.FloatField(null=True, blank=True)
    qty_available = models.PositiveIntegerField(default=0)
    # locations = models.ManyToManyField("main.DeliveryDetail", blank=True)
    primary_img = models.ImageField(
        upload_to='products/primary_imgs', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ])
    vendor  = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    category = models.ForeignKey("main.ProductCategory", related_name="product_items",on_delete=models.CASCADE)
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
        
        return [i.image.url for i in self.images.all()]
        
    
    @property
    def product_components(self):
        return self.components.values("item", "capacity", "item_type", "qty")
    
    @property
    def locations_list(self):
        return self.locations.values("location__name", "delivery_fee")
    
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
    
    
    
# class DeliveryDetail(models.Model):
#     location = models.ForeignKey("main.Location", on_delete=models.CASCADE)
#     delivery_fee = models.FloatField()
#     vendor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    
#     def __str__(self):
#         return self.location.name
    
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
    phone = models.CharField(max_length=20, null=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    address_1 = models.CharField(max_length=500)
    address_2 = models.CharField(max_length=500,null=True, blank=True)
    delivery_instruction = models.TextField(blank=True, null=True)
    additional_instruction = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.address_1
    



class Order(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey("accounts.User", null=True, on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=100, unique=True,null=True)
    address = models.ForeignKey("main.Address", null=True, on_delete=models.CASCADE)
    shipping_fee = models.FloatField()
    installation_fee = models.FloatField()
    total_price = models.FloatField()
    is_paid_for = models.BooleanField(default=False)
    status = models.CharField(max_length=255, 
                              choices=(("pending", "pending"),
                                       ("processing", "processing"),
                                       ("completed", "completed"),
                                       ("user-canceled", "user-canceled"),
                                    ), null=True,blank=True)
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
    status = models.CharField(max_length=255, 
                              choices=(("pending", "pending"),
                                       ("processing", "processing"),
                                       ("completed", "completed"),
                                       ("user-canceled", "user-canceled"),
                                    ), default="pending")
    delivery_fee = models.FloatField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True)
    accepted_at = models.DateTimeField(null=True)
    processed_at = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.item.name
    
    @property
    def item_name(self):
        return self.item.name
    
    @property
    def image_url(self):
        return self.item.primary_img_url
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
    
    
    
class PaymentDetail(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, related_name="payment",)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="payment", null=True)
    transaction_id = models.CharField(max_length=350, blank=True, null=True)
    payment_type = models.CharField(max_length=300,
                                    choices=(("specta", "Specta"),
                                             ("outright", "Outright"),
                                              ("lease", "Lease To Own"),
                                              ("power-as-a-service", "Power as a service")),
                                    null=True, blank=True)
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
    
    
    

    
   
    