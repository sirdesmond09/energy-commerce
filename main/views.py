from .serializers import AddOrderSerializer, AddProductSerializer, AddressSerializer, CartSerializer, EnergyCalculatorSerializer, GallerySerializer, LocationSerializer, MultipleProductSerializer, ProductComponentSerializer, ProductSerializer, CategorySerializer
from .models import Address, Cart, Location, ProductCategory, Product, ProductComponent, ProductGallery
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.generics import ListCreateAPIView, ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied



class CategoryView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = ProductCategory.objects.filter(is_deleted=False).order_by('-date_added')
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    


class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = ProductCategory.objects.filter(is_deleted=False).order_by('-date_added')
    lookup_field = "id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    
    
    
@swagger_auto_schema(method="post", request_body=AddProductSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def add_product(request):
    
    serializer = AddProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    
class ProductList(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    
    
    def list(self, request, *args, **kwargs):
        
        category = request.GET.get('category', None)
        vendor = request.GET.get('vendor', None)
        min_price = request.GET.get("min_price", None)
        max_price = request.GET.get("max_price", None)
        location = request.GET.get("location", None)
        
        
        
        queryset = self.filter_queryset(self.get_queryset())
        
        
        if category:
            queryset = queryset.filter(category__name=category)
            
        if vendor:
            queryset = queryset.filter(vendor__id=vendor)
            
        if min_price and max_price:
            queryset = queryset.filter(price__gte=min_price).filter(price__lte=max_price)
            
        if location:
            queryset = queryset.filter(locations__id__in=[location])
            

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    

class ProductDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    lookup_field="id"
    



@swagger_auto_schema(method="delete", request_body=GallerySerializer())
@api_view(["POST", "DELETE"])
def update_galley(request, product_id, img_id=None):
    
    if request.method == "POST":
        serializer = GallerySerializer(data=request.data, many=True)
        
        serializer.is_valid(raise_exception=True)
        
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
            
            images = []
            for data in serializer.validated_data:
                images.append(ProductGallery(**data, product=product))
            ProductGallery.objects.bulk_create(images)
            
        except Product.DoesNotExist:
            raise NotFound(detail={"message": "Product not found or does not exist"})
    
    
        except Exception as e:
            raise ValidationError(str(e))
        
        return Response({"message": "success"}, status=status.HTTP_202_ACCEPTED)
    
    
    
    elif request.method == "DELETE":
        
        if img_id is None:
            raise ValidationError({"message": "image_id is required"})
        
        try:
            img = ProductGallery.objects.get(id=img_id, product__id=product_id,is_deleted=False)
            
            img.delete()
            
        except ProductGallery.DoesNotExist:
            raise NotFound(detail={"message": "Image not found or does not exist"})
        
        
        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)
    
    

class LocationView(ListCreateAPIView):
    serializer_class = LocationSerializer
    queryset = Location.objects.all().order_by('-date_added')
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]
    


class LocationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    queryset = Location.objects.all().order_by('-date_added')
    lookup_field = "id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    
    
    
class ComponentsDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductComponentSerializer
    queryset = ProductComponent.objects.all()
    lookup_field = "id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    

class AddressListCreateView(ListCreateAPIView):
    
    """Get and create a list of addresses. When getting, the most recent ones are returned on top"""
    
    queryset = Address.objects.all().order_by('-date_added')
    serializer_class =  AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.validated_data["user"] = request.user
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
    
class AddressesDetailView(RetrieveUpdateDestroyAPIView):
    
    """Edit, retrieve, and delete an address"""

    queryset = Address.objects.all().order_by('-date_added')
    serializer_class =  AddressSerializer
    lookup_field = "id"
    
    
    @swagger_auto_schema(method="put", request_body=AddressSerializer())
    @action(methods=["put"], detail=True)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.user != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to edit this address"})
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(method="patch", request_body=AddressSerializer())
    @action(methods=["patch"], detail=True)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.user != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to edit this address"})
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.user != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to edit this address"})
        return super().delete(request, *args, **kwargs)
    
    
    
    

@swagger_auto_schema(method="post", request_body=AddOrderSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def new_order(request):
    
    if request.method == "POST":
        serializer = AddOrderSerializer(data=request.data)
        serializer.is_valid(raise_exceptions=True)
        # TODO: verify payment
        order = serializer.save()
        order.user = request.user
        order.save()
        
        return Response({"message": "order successfully made"})
    
    
    
    

@swagger_auto_schema(method="post", request_body=EnergyCalculatorSerializer(many=True))
@api_view(["POST"])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def energy_calculator(request):
    
    if request.method == "POST":
        battery = request.GET.get('battery_type')
        serializer = EnergyCalculatorSerializer(data=request.data, many=True)
        
        if serializer.is_valid():
        
            if battery == "tubular":
                discharge_depth = 0.50
            elif battery == "lithium":
                discharge_depth = 0.92
            
            else:
                raise ValidationError(detail={"message":"select battery type"})
            
            energy_loss = 0.3
            power_factor = 0.8
        
            sys_cap_limit = 0.7
            volt = 24
            batt_unit = 150
            
            total_load = round(sum([data["wattage"] for data in serializer.validated_data])/(1-energy_loss), 2)
            
            watt_hr = [data["wattage"] * data["hours"] for data in serializer.validated_data]
            
            total_watt_hr = round(sum(watt_hr)/(1-energy_loss), 2)
            
            
            inverter_capacity = round(total_load/(sys_cap_limit*power_factor*1000), 2)
            
            battery_cap = round((total_watt_hr/volt)/discharge_depth, 2)
            
            batt_total = round(battery_cap/batt_unit, 2)
            
            data = {"total_load": total_load,
                    "total_watt_hr": total_watt_hr,
                    "suggested_inverter_capacity":inverter_capacity,
                    "estimated_battery_cap": battery_cap,
                    "suggested_unit_battery_total":batt_total}
            
            return Response(data)
        
        else:
            raise ValidationError(detail=serializer.errors)
            
            
            
@swagger_auto_schema(method="post", request_body=MultipleProductSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def multiple_products_by_id(request):
    
    if request.method == "POST":
        serializer = MultipleProductSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        products = Product.objects.filter(id__in=serializer.validated_data.get("uids"), is_deleted=False)
        
        return Response(ProductSerializer(products, many=True).data, status=status.HTTP_200_OK)
    
    
    
class CartListCreateView(ListCreateAPIView):
    
    """Get and create a list of addresses. When getting, the most recent ones are returned on top"""
    
    queryset = Cart.objects.all().order_by('-date_added')
    serializer_class =  CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        for data in serializer.validated_data:
            data["user"] = request.user
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
    
class CartDetailView(RetrieveUpdateDestroyAPIView):
    
    """Edit, retrieve, and delete an address"""

    queryset = Cart.objects.all().order_by('-date_added')
    serializer_class =  CartSerializer
    lookup_field = "id"
    
    
    @swagger_auto_schema(method="put", request_body=CartSerializer())
    @action(methods=["put"], detail=True)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.user != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to edit this Cart"})
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(method="patch", request_body=CartSerializer())
    @action(methods=["patch"], detail=True)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.user != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to edit this Cart"})
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.user != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to edit this Cart"})
        return super().delete(request, *args, **kwargs)