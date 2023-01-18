from django.db import models
from django.core.validators import FileExtensionValidator
# Create your models here.
import uuid


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
    qty_available = models.PositiveIntegerField(default=0)
    locations = models.ManyToManyField("main.Location", blank=True)
    primary_img = models.ImageField(
        upload_to='products/primary_imgs', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ])
    vendor  = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    box_details = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    @property
    def primary_img_url(self):
        return self.primary_img.url
    
    @property
    def gallery(self):
        return self.images.all().values(["image__url", "id"])
        
    def delete(self):
        self.is_deleted = True
        self.save()
        
    def delete_permanently(self):
        super().delete()
    
    
    
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

