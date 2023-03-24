from django.db import models
from django.core.validators import FileExtensionValidator
# Create your models here.
import uuid
from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.contrib.postgres.fields import ArrayField
from django.db.models import Sum


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
    product_sku = models.CharField(max_length=255, null=True)
    ships_from = models.ManyToManyField("main.Location", blank=True, related_name="product_ships_from")
    battery_type = models.CharField(max_length=255, choices= (("Tubular", "Tubular"),
                                                              ("Lithium", "Lithium"),
                                                              ("Dry cell (SMF)", "Dry cell (SMF)")),
                                    null=True, blank=True)
    battery_cap_AH = models.FloatField(null=True, blank=True)
    total_power_kva = models.FloatField(null=True, blank=True)
    battery_voltage = models.FloatField(null=True, blank=True)
    qty_available = models.PositiveIntegerField(default=0)
    max_order_qty = models.PositiveIntegerField(null=True)
    dimension_measurement = models.CharField(max_length=255, null=True,
                                             choices=(("cmxcmxcm","cmxcmxcm"),
                                                      ("mmxmmxmm","mmxmmxmm")))
    panel_type = models.CharField(max_length=255, null=True)
    length  = models.FloatField(default=0)
    breadth  = models.FloatField(default=0)
    height  = models.FloatField(default=0)
    weight  = models.FloatField(default=0)
    locations = models.ManyToManyField("main.Location", blank=True)
    SE_delivery_fee  = models.FloatField(default=0)
    SW_delivery_fee  = models.FloatField(default=0)
    SS_delivery_fee  = models.FloatField(default=0)
    NE_delivery_fee  = models.FloatField(default=0)
    NW_delivery_fee  = models.FloatField(default=0)
    NC_delivery_fee  = models.FloatField(default=0)
    primary_img = models.ImageField(
        upload_to='products/primary_imgs', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ], blank=True)
    key_features = ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True)
    warranty = models.PositiveIntegerField(blank=True, null=True)
    disclaimer = models.TextField(blank=True, null=True)
    vendor  = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True, related_name="products")
    category = models.ForeignKey("main.ProductCategory", related_name="product_items",on_delete=models.CASCADE)
    installation_fee = models.FloatField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, 
                              choices= [("pending", "pending"),
                                        ("verified", "verified"),
                                        ("unapproved", "unapproved")],
                              default="pending")
    is_deleted = models.BooleanField(default=False)
    
    @property
    def primary_img_url(self):
        return self.primary_img.url
    
    @property
    def category_name(self):
        return self.category.name
    
    @property
    def gallery(self):
        
        return [{"id" : i.id,"image_url":i.image.url} for i in self.images.all()]
        
    
    @property
    def product_components(self):
        return self.components.values("item", "capacity", "item_type", "qty")
    
    @property
    def locations_list(self):
        return self.locations.values("id", "name", "region")
    
    @property
    def ships_from_list(self):
        return self.ships_from.values("id","name", "region")
    
    @property
    def store_detail(self):
        try:
            return self.vendor.store_profile
        except Exception as e:
            return {"data": str(e)}
    
    
    @property
    def total_order(self):
        
        items = self.order_items.filter(is_deleted=True).exclude(status__in=["pending","cancel-requested","user-canceled"])
        return items.count()
    

    @property
    def rating(self):
        all_ratings = self.ratings.filter(is_deleted=False)
        
        if all_ratings.count() > 0:
            total = all_ratings.aggregate(Sum("rating"))["rating__sum"]
            rating = total/all_ratings.count()
            return round(rating, 2)
        return 0
    
    
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
    unit = models.CharField(max_length=255, null=True)
    
    
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
    
    REGIONS = (
        ("NW", "NW"),
        ("NE", "NE"),
        ("NC", "NC"),
        ("SW", "SW"),
        ("SE", "SE"),
        ("SS", "SS"),
    )
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)   
    region = models.CharField(max_length=255, null=True, choices=REGIONS)
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
    
    def __str__(self):
        return self.name
    
    

class Address(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey("accounts.User", null=True, related_name="addresses", on_delete=models.CASCADE)
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
    is_default = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
        
        
    
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
    cancellation_reason = models.TextField(blank=True, null=True)
    cancellation_response_reason = models.TextField(blank=True, null=True)
    prev_status = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, 
                              choices=(("pending", "pending"),
                                       ("processing", "processing"),
                                       ("completed", "completed"),
                                       ("cancel-requested", "cancel-requested"),
                                       ("user-canceled", "user-canceled"),
                                    ), null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    cancel_requested_at = models.DateTimeField(null=True, blank=True)
    cancel_responded_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
        
        
    @property
    def address_data(self):
        return model_to_dict(self.address, exclude=["id", "user", "date_added", "is_deleted"])
    
    
    @property
    def payment_data(self):
        
        payment = PaymentDetail.objects.filter(order__id = self.id, is_deleted=False)
        
        if payment.exists():
            return model_to_dict(payment.first())
        
        return None
        
    
        
        
class OrderItem(models.Model):
    unique_id = models.CharField(max_length=20, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name="items")
    item = models.ForeignKey("main.Product", on_delete=models.DO_NOTHING, related_name="order_items")
    unit_price = models.FloatField(default=0)
    installation_fee = models.FloatField(default=0)
    qty = models.PositiveIntegerField()
    status = models.CharField(max_length=255, 
                              choices=(("pending", "pending"),
                                       ("confirmed", "confirmed"),
                                       ("processing", "processing"),
                                       ("in-transit", "in-transit"),
                                       ("delivered", "delivered"),
                                       ("installed", "installed"),
                                       ("cancel-requested", "cancel-requested"),
                                       ("user-canceled", "user-canceled"),
                                    ), default="pending")
    cancellation_reason = models.TextField(blank=True, null=True)
    cancellation_response_reason = models.TextField(blank=True, null=True)
    prev_status = models.CharField(max_length=255, null=True, blank=True)
    delivery_fee = models.FloatField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    in_transit_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    installed_at = models.DateTimeField(null=True, blank=True)
    cancel_requested_at = models.DateTimeField(null=True, blank=True)
    cancel_responded_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.item.name
    
    @property
    def item_name(self):
        return self.item.name
    
    @property
    def image_url(self):
        return self.item.primary_img_url
    
    @property
    def address_data(self):
        return self.order.address_data
    
    @property
    def store(self):
        return self.item.store
    
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
    note = models.TextField(null=True)
    status = models.CharField(max_length=20,choices=(
        ("pending", "pending"),
        ("approved", "approved"),
        ("declined", "declined")), default="pending")
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
        
        
    @property
    def user_detail(self):
        return {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "phone": self.user.phone,
            "email": self.user.email,
        }
    
    
    

class Cart(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    product =  models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    

class Commission(models.Model):
    percent = models.PositiveIntegerField(default=12)
   
    
    
class PayOuts(models.Model):
    vendor = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL, related_name="payouts")
    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True)
    amount = models.FloatField()
    order_booking_id = models.CharField(max_length=255)
    commission = models.FloatField()
    commission_percent = models.FloatField()
    status = models.CharField(max_length=255, choices=(("pending", "pending"),
                                                       ("paid", "paid"),
                                                       ("processing", "processing"),), default="pending")
    date_added = models.DateTimeField(auto_now_add=True)
    date_paid = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
        
        
    @property 
    def store(self):
        return self.vendor.store_profile
    
    
    @property
    def bank_data(self):
        return self.vendor.bank_detail
        
        
class ValidationOTP(models.Model):
    order_item = models.ForeignKey(OrderItem, related_name="validation_otp", on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_verified = models.BooleanField(default=False)
    
    
class Rating(models.Model):
    product = models.ForeignKey("main.Product", null=True, on_delete=models.SET_NULL, related_name="ratings")
    order_item = models.OneToOneField("main.OrderItem", null=True, on_delete=models.SET_NULL, related_name="rating")
    review = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
        
        
        
class CalculatorItem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    power_kw = models.FloatField()
    avg_hr_per_day = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()

class FrequentlyAskedQuestion(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
        
        
        
class UserInbox(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    heading = models.CharField(max_length=255)
    body = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    