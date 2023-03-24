from rest_framework import serializers

from main.generators import generate_booking_id, generate_order_id
from .models import Address, CalculatorItem, Cart, FrequentlyAskedQuestion, Location, Order, OrderItem, PayOuts, PaymentDetail, ProductComponent, ProductGallery, ProductCategory, Product, Rating, UserInbox
from rest_framework.exceptions import ValidationError
from accounts.serializers import StoreProfileSerializer
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField


class ProductSerializer(serializers.ModelSerializer):
    primary_img = Base64ImageField()
    gallery = serializers.ReadOnlyField()
    product_components = serializers.ReadOnlyField()
    primary_img_url = serializers.ReadOnlyField()
    category_name = serializers.ReadOnlyField()
    locations_list = serializers.ReadOnlyField()
    ships_from_list = serializers.ReadOnlyField()
    vendor_detail = serializers.SerializerMethodField()
    store_detail = serializers.SerializerMethodField()
    rating = serializers.ReadOnlyField()
    class Meta:
        fields = '__all__'
        model = Product
        extra_kwargs = {
            'primary_img': {'write_only': True},
            'locations': {'write_only': True}
        }
        
        
    def get_vendor_detail(self, obj):
        return UserSerializer(obj.vendor).data
    
    def get_store_detail(self, obj):
        
        try:
            
            return StoreProfileSerializer(obj.store).data
        
        except Exception as e:
            return {"data": str(e)}
        
        
    
        

        
class GallerySerializer(serializers.ModelSerializer):

    image = Base64ImageField()
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
        locations = validated_data['product'].pop("locations")
        primary_img = validated_data['product'].pop('primary_img')
        product = Product.objects.create(**validated_data['product'], primary_img=primary_img)
        product.locations.set(locations)
        product.save() 
        
        try:
            if  "gallery" in validated_data.keys():
                gallery = []
            
                for data in validated_data.get("gallery"):
                    image = data.pop("image")
                    gallery.append(ProductGallery(**data, product=product, image=image))
                    
                ProductGallery.objects.bulk_create(gallery)
                
            if  "components" in validated_data.keys():
                components = []
                for data in validated_data.get("components"):
                    components.append(ProductComponent(**data, product=product))

                ProductComponent.objects.bulk_create(components)
            
        except Exception as e:
            product.delete_permanently()
            raise ValidationError(str(e))
        
        return product
    
    
    def update(self, instance, validated_data):
        fields = self.fields.keys()

        # update locations
        locations = validated_data.get('product', {}).pop('locations')
        if locations:
            instance.product.locations.set(locations)
        
        # update product fields
        for field in fields:
            if field in validated_data.get('product', {}):
                setattr(instance.product, field, validated_data['product'][field])

        
        instance.product.save()
            
        # Updating components
        if 'components' in validated_data:
            instance.components.all().delete()
            components = []
            for data in validated_data['components']:
                components.append(ProductComponent(**data, product=instance.product))
            ProductComponent.objects.bulk_create(components)
            
        return instance
    
class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        fields = "__all__"
        model = ProductCategory
        
        
    def get_products(self, category):
        return ProductSerializer(category.product_items.filter(is_deleted=False, status="verified"), many=True).data[:4]
    
    
    def get_product_count(self, category):
        return category.product_items.filter(is_deleted=False).count()
        

class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = "__all__"
        model = Location



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Address
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField()
    image_url = serializers.ReadOnlyField()
    address_data = serializers.ReadOnlyField()
    store = serializers.ReadOnlyField()
    product_sku = serializers.SerializerMethodField()
    booking_id = serializers.SerializerMethodField()
    total_order = serializers.ReadOnlyField() 
    rating_made = serializers.SerializerMethodField()
    class Meta:
        fields = "__all__"
        model = OrderItem
        
        
    def get_product_sku(self, obj):
        return obj.item.product_sku
    
    def get_booking_id(self,obj):
        return obj.order.booking_id
    
    def get_rating_made(self,obj):
        rating = Rating.objects.filter(order_item=obj, is_deleted=False)
        
        if rating.exists():
            rating = rating.first()
            return {
                "id" : rating.id,
                "rating": rating.rating,
                "review" : rating.review
            }
            
        return None

class UpdateStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=200)
        
        
class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    address_data = serializers.ReadOnlyField()
    payment_data  = serializers.ReadOnlyField()
        
    class Meta:
        fields = "__all__"
        model = Order
        
        
    
    def validate_delivery_fee(self, value):
        if value is None:
            raise ValidationError("delivery_fee is required")
        return value
        
        
    def get_order_items(self, order):
        return OrderItemSerializer(order.items.all(), many=True).data
    
    
    def validate_address(self, value):
        if value is None:
            raise ValidationError("This field is required")
        
        return value
        
        
       
       
class AddOrderSerializer(serializers.Serializer):
    order_data = OrderSerializer()
    order_items = OrderItemSerializer(many=True)
    
    
    def create(self, validated_data):
        booking_id = generate_booking_id()
        
        order = Order.objects.create(**validated_data.get('order_data'), booking_id=booking_id)
        
        order_items = []
        products = []
        
        total_price = 0
        
        try:
            for item in validated_data.get('order_items'):
                                
                product = item.get("item") #get the product 
                qty = item.get('qty')
                
                if product.qty_available >= qty:
                    item["unique_id"] = generate_order_id()
                    item["unit_price"] = product.price
                    item["installation_fee"] = product.installation_fee
                    product.qty_available  -= qty
                    
                    order_items.append(OrderItem(**item, order=order))
                    products.append(product)
                    
                    total_price += ((item["unit_price"] +  item["installation_fee"] + item["delivery_fee"]) * qty)
                else:
                    order.delete_permanently()
                    raise ValidationError({"message": f"product '{product.name}' is out of stock. Please try again."})
                
            OrderItem.objects.bulk_create(order_items)
            Product.objects.bulk_update(products, ["qty_available"])
            
            order.total_price = total_price
            order.save()
            
            return order
        except Exception as e:
            order.delete_permanently()
            
            raise  ValidationError(str(e))
        
        
        

class EnergyCalculatorSerializer(serializers.Serializer ):
    total_wattage = serializers.FloatField()
    total_watt_hour = serializers.FloatField()
    battery_type = serializers.CharField()
    
    
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
    order_detail = serializers.SerializerMethodField()
    user_detail = serializers.ReadOnlyField()
    
    class Meta:
        fields = "__all__"
        model = PaymentDetail
        
        
    def get_order_detail(self, payment):
        return OrderSerializer(payment.order).data
        
        

class PayOutSerializer(serializers.ModelSerializer):
    
    store = serializers.ReadOnlyField()
    bank_data = serializers.ReadOnlyField()
    
    class Meta:
        fields = "__all__"
        model = PayOuts
        
        

# class DeliveryDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = "__all__"
#         model = DeliveryDetail
        
        

class UpdateStatusSerializer(serializers.Serializer):
    
    status = serializers.CharField(max_length=50)
    verification_code = serializers.CharField(max_length=6, required=False)
    
    
    def validate_status(self, value):
        if value not in ("processing","in-transit", "delivered"):
            raise ValidationError(detail="status can only be 'processing' or 'in-transit' or 'delivered'")
    
        return value
    
    
class StatusSerializer(serializers.Serializer):
    
    status = serializers.CharField(max_length=50)

class CancelSerializer(serializers.Serializer):
    
    reason = serializers.CharField(max_length=50000)


class CancelResponseSerializer(serializers.Serializer):
    
    status = serializers.CharField(max_length=50)
    reason = serializers.CharField(max_length=1000)
    
    
    def validate_status(self, value):
        if value not in ("accepted","rejected"):
            raise ValidationError(detail={"status can only be 'accepted' or 'rejected'"})
        
        return value
    
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Rating
        fields = "__all__"
    
    
    
class CalculatorItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CalculatorItem
        fields = "__all__"



class UserInboxSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserInbox
        fields = "__all__"


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FrequentlyAskedQuestion
        fields = "__all__"