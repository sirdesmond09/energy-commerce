from rest_framework import serializers
from .models import Address, Location, ProductGallery, ProductCategory, Product


class ProductSerializer(serializers.ModelSerializer):
    gallery = serializers.ReadOnlyField()
    primary_img_url = serializers.ReadOnlyField()
    
    class Meta:
        fields = '__all__'
        model = Product
        extra_kwargs = {
            'primary_img': {'write_only': True}
        }
        
class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ProductGallery
        
        
class AddProductSerializer(serializers.Serializer):
    product  = ProductSerializer()
    gallery = GallerySerializer(many=True)
    
    
    def create(self, validated_data):
        product = Product.objects.create(**validated_data['product'])
        
        for data in validated_data.get("gallery"):
            ProductGallery.objects.create(**data, product=product)
            
        return product
    
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ProductCategory
        

class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = "__all__"
        model = Location



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Address