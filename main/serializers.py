from rest_framework import serializers

from main.generators import generate_booking_id
from .models import Address, Location, Order, OrderItem, ProductComponent, ProductGallery, ProductCategory, Product
from rest_framework.exceptions import ValidationError


class ProductSerializer(serializers.ModelSerializer):
    # gallery = serializers.ReadOnlyField()
    # product_components = serializers.ReadOnlyField()
    primary_img_url = serializers.ReadOnlyField()
    category_name = serializers.ReadOnlyField()
    
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
        
class ProductComponentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ProductComponent
         
class AddProductSerializer(serializers.Serializer):
    product  = ProductSerializer()
    gallery = GallerySerializer(many=True, required=False)
    components = ProductComponentSerializer(many=True, required=False)
    
    
    def create(self, validated_data):
        product = Product.objects.create(**validated_data['product'])
        
        try:
            gallery = []
            components = []
            for data in validated_data.get("gallery"):
                gallery.append(ProductGallery(**data, product=product))
            for data in validated_data.get("components"):
                components.append(ProductComponent(**data, product=product))

            ProductGallery.objects.bulk_create(gallery)
            ProductComponent.objects.bulk_create(components)
        except Exception as e:
            raise ValidationError(str(e))
        
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
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = OrderItem
        
        
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Order
        
        
       
       
class AddOrderSerializer(serializers.Serializer):
    order_data = OrderSerializer()
    order_items = OrderItemSerializer(many=True)
    
    
    def create(self, validated_data):
        booking_id = generate_booking_id()
        order = Order.objects.create(**validated_data.get('order_data'), booking_id=booking_id)
        
        order_items = []
        for item in validated_data.get('order_items'):
            
            product = item.item #get the product 
            
            if product.qty_available >= item.qty:
                item["unit_price"] = product.price
                order_items.append(OrderItem(**item, order=order))
            else:
                order.delete_permanently()
                raise ValidationError({"message": f"product '{product.name}' is out of stock. Please try again."})
            
        OrderItem.objects.bulk_create(order_items)
        
        return order
        
        
        

class EnergyCalculatorSerializer(serializers.Serializer ):
    total_wattage = serializers.IntegerField()
    total_watt_hour = serializers.IntegerField()
    
    
    
class MultipleProductSerializer(serializers.Serializer ):
    uids = serializers.ListField()