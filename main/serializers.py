from rest_framework import serializers

from main.generators import generate_booking_id
from .models import Address, Cart, Location, Order, OrderItem, PaymentDetail, ProductComponent, ProductGallery, ProductCategory, Product
from rest_framework.exceptions import ValidationError


class ProductSerializer(serializers.ModelSerializer):
    gallery = serializers.ReadOnlyField()
    product_components = serializers.ReadOnlyField()
    primary_img_url = serializers.ReadOnlyField()
    category_name = serializers.ReadOnlyField()
    locations_list = serializers.ReadOnlyField()
    
    class Meta:
        fields = '__all__'
        model = Product
        extra_kwargs = {
            'primary_img': {'write_only': True},
            'locations': {'write_only': True}
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
    products = serializers.SerializerMethodField()
    
    class Meta:
        fields = "__all__"
        model = ProductCategory
        
        
    def get_products(self, category):
        return ProductSerializer(category.product_items.filter(is_deleted=False), many=True).data[:4]

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
    order_items = serializers.ReadOnlyField()
        
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
        products = []
        
        for item in validated_data.get('order_items'):
            
            product = item.item #get the product 
            
            if product.qty_available >= item.qty:
                item["unit_price"] = product.price
                product.qty_available  -= item.qty
                
                order_items.append(OrderItem(**item, order=order))
                products.append(product)
            else:
                order.delete_permanently()
                raise ValidationError({"message": f"product '{product.name}' is out of stock. Please try again."})
            
        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(products)
        
        return order
        
        
        

class EnergyCalculatorSerializer(serializers.Serializer ):
    total_wattage = serializers.IntegerField()
    total_watt_hour = serializers.IntegerField()
    
    
    
class MultipleProductSerializer(serializers.Serializer ):
    uids = serializers.ListField()
    
    
class CartSerializer(serializers.ModelSerializer):
    product_detail = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Cart
        
        
    def get_product_detail(self, cart):
         return ProductSerializer(cart.product).data
        
        
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = PaymentDetail
        
        

    