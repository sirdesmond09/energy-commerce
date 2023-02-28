from main.helpers import payment_is_verified
from .serializers import AddOrderSerializer, AddProductSerializer, AddressSerializer, CancelResponseSerializer, CancelSerializer, CartSerializer, DeliveryDetailSerializer, EnergyCalculatorSerializer, GallerySerializer, LocationSerializer, MultipleProductSerializer, OrderItemSerializer, OrderSerializer, PayOutSerializer, PaymentSerializer, ProductComponentSerializer, ProductSerializer, CategorySerializer, UpdateStatusSerializer
from .models import Address, Cart, Commission, DeliveryDetail, Location, Order, OrderItem, PayOuts, PaymentDetail, ProductCategory, Product, ProductComponent, ProductGallery
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.generics import ListCreateAPIView, ListAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from accounts.permissions import CustomDjangoModelPermissions
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from django.utils import timezone
from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination

pagination_class = LimitOffsetPagination()

COMMISSION = round(Commission.objects.first().percent / 100, 2)

class CategoryView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = ProductCategory.objects.filter(is_deleted=False).order_by('-date_added')
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    


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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
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
    
    

class VendorProductList(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        if request.user.role == "vendor":
            queryset = queryset.filter(vendor=request.user)

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]



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
    
    queryset = Address.objects.all().order_by('-is_default','-date_added')
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
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        order.user = request.user
        order.save()
        data = {
            "message": "success",
            "booking_id": order.booking_id,
            "total_amount" : order.total_price
        }
        
        return Response(data, status=status.HTTP_201_CREATED)
    
    

@swagger_auto_schema(method="post", request_body=PaymentSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def outright_payment(request, booking_id):
    
    if request.method == "POST":
        
        try:
            order = Order.objects.get(booking_id=booking_id, is_deleted=False)
        except KeyError:
            raise ValidationError(detail={"message": "order was not found"})
        
        if order.is_paid_for:
            raise ValidationError(detail={"message": "multiple payment not allowed. order has been paid for"})
        
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        try:
            trans_id = serializer.validated_data["transaction_id"]
        except KeyError:
            raise ValidationError(detail={"message": "transaction_id was not provided"})
        result = payment_is_verified(trans_id)
        if isinstance(result, dict):
            raise ValidationError(detail={"message": result})
            
        elif payment_is_verified(trans_id):
            #create payment record
            PaymentDetail.objects.create(**serializer.validated_data, order=order, user=request.user, payment_type='outright')
            
            
            #mark order as paid
            order.is_paid_for =True
            order.status = "pending"
            order.save()
            
            payouts = [PayOuts(vendor=order_item.item.vendor,
                                                       item= order_item,
                                                       amount = (order_item.unit_price * order_item.qty) - ((order_item.unit_price * order_item.qty) * COMMISSION) ,
                                                       order_booking_id = order.booking_id,
                                                       commission = (order_item.unit_price * order_item.qty) * COMMISSION,
                                                       commission_percent = COMMISSION,
                                                    ) for order_item in order.items.filter(is_deleted=False)]
            
            
            PayOuts.objects.bulk_create(payouts)
            
            data = {
                "message": "success",
                "booking_id": order.booking_id,
                "total_amount" : order.total_price
            }
            
            return Response(data, status=status.HTTP_201_CREATED)
        
        else:
            return Response({"message":"payment not successful"}, status=status.HTTP_201_CREATED)
                
    

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
        
            product = data.get("product")
            
            if self.queryset.filter(product=product, user=request.user).exists():
                item = self.queryset.get(product=product, user=request.user)
                item.qty = data.get("qty")
                item.date_added = timezone.now()
                item.save()
                serializer.validated_data.remove(data)
        else:
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
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
    
    

@swagger_auto_schema(method="delete", request_body=CancelSerializer())
@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def request_order_cancel(request, booking_id):
    
    """Use this endpoint to request to cancel the whole order"""
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)
    except Order.DoesNotExist:
        raise ValidationError(detail={"message": "order was not found"})
    
    if order.status == "cancel-requested":
        raise PermissionDenied(detail={"message":"cancel already requested"})
    
    if order.status == "user-canceled":
        raise PermissionDenied(detail={"message":"order is already canceled"})
    
    if request.method == "DELETE":
        serializer = CancelSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        
        order.prev_status = order.status
        order.status = "cancel-requested"
        order.cancellation_reason = serializer.validated_data.get("reason")
        order.cancel_requested_at = timezone.now()
        order.save()
        return Response({"message":"success"},status=status.HTTP_202_ACCEPTED)
    
    
    
    
@swagger_auto_schema(method="delete", request_body=CancelSerializer())
@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def request_order_item_cancel(request, booking_id, item_id):
    
    """Use this endpoint to request cancel  for an item in the order"""
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)
        order_item = OrderItem.objects.get(id=item_id, order=order,is_deleted=False)
        
    except Order.DoesNotExist:
        raise ValidationError(detail={"message": "order was not found"})
    
    except OrderItem.DoesNotExist:
        raise ValidationError(detail={"message": "item was not found"})
    
    if order_item.status == "cancel-requested":
        raise PermissionDenied(detail={"message":"cancel already requested"})
    if order_item.status == "user-canceled":
        raise PermissionDenied(detail={"message":"item is already canceled"})
    
    if request.method == "DELETE":
        serializer = CancelSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        order_item.prev_status = order_item.status
        order_item.status = "cancel-requested"
        order_item.cancellation_reason = serializer.validated_data.get("reason")
        order_item.cancel_requested_at = timezone.now()
        order_item.save()
        return Response({"message":"success"},status=status.HTTP_202_ACCEPTED)
    
    
@swagger_auto_schema(method="patch", request_body=CancelResponseSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def respond_to_cancel_request(request, booking_id=None, item_id=None):
    
    if booking_id:
        obj = Order.objects.get(booking_id=booking_id, is_deleted=False)
    
    if item_id:    
        obj = OrderItem.objects.get(id=item_id, order=obj,is_deleted=False)
    
    if obj.status != "cancel-requested":
        raise ValidationError(detail={"message":"owner did not request to cancel"})
        
    serializer = CancelResponseSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    
    response = serializer.validated_data.get("status")
    
    
    if response == "accepted":
        obj.status = "user-canceled"
        obj.cancellation_response_reason = serializer.validated_data.get("reason")
        obj.cancel_responded_at = timezone.now()
        obj.save()
        
        if isinstance(obj, Order):
        
            products = []
            
            for order_item in obj.items.all():
                order_item.item.qty_available += order_item.qty
                order_item.prev_status = order_item.status
                order_item.status = "user-canceled"
                order_item.cancel_responded_at = timezone.now()
                order_item.cancellation_response_reason = "order was canceled"
                order_item.save()
                products.append(order_item.item)
                
            Product.objects.bulk_update(products, ["qty_available"])
        
        elif isinstance(obj, OrderItem):
            
            ### return the products and save
            obj.item.qty_available += obj.qty
            obj.item.save()
            
            ##check if all other items are canceled, then mark order as canceled
            order = obj.order
            if all(i.status == "user-canceled" for i in order.items.filter(is_deleted=True)):
                order.status="user-canceled"
                order.cancellation_response_reason = "all items were cancelled"
                order.cancel_responded_at = timezone.now()
                order.save()
    
                
    elif response == "rejected":  
                
        obj.status = obj.prev_status
        obj.cancellation_response_reason = serializer.validated_data.get("reason")
        obj.cancel_responded_at = timezone.now()
        obj.save()    
        
    
    return Response({"message": "{} successfully".format(response)}, status=status.HTTP_200_OK)
                
    
    
    





@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def permanently_delete_order(request, booking_id):
    """Perform a hard delete. This cannot be undone because it completely deletes the record from the database"""
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)
    except KeyError:
        raise ValidationError(detail={"message": "order was not found"})

    
    products = []
    
    for order_item in order.items.all():
        order_item.item.qty_available += order_item.qty
        products.append(order_item.item)
        order_item.delete_permanently()
        
    Product.objects.bulk_update(products, ["qty_available"])
    
    order.delete_permanently()
    return Response({},status=status.HTTP_204_NO_CONTENT)
    
    
    
class OrderList(ListAPIView):
    
    queryset = Order.objects.filter(is_deleted=False).order_by("-date_added")
    
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [ IsAuthenticated | CustomDjangoModelPermissions]
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if request.user.role == "user":
            queryset = queryset.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    

class OrderDetail(RetrieveAPIView):
    queryset = Order.objects.filter(is_deleted=False)
    
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user.role == "user" and instance.user != request.user:
            raise PermissionDenied({"message": "cannot retrieve details for another user's order"})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    




class DeliveryDetailListCreateView(ListCreateAPIView):
    
    
    
    queryset = DeliveryDetail.objects.all()
    serializer_class =  DeliveryDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.validated_data["vendor"] = request.user    
        self.perform_create(serializer)
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(vendor=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
    
class DeliveryDetailView(RetrieveUpdateDestroyAPIView):
    
    """Edit, retrieve, and delete an address"""

    queryset = DeliveryDetail.objects.all()
    serializer_class =  DeliveryDetailSerializer
    lookup_field = "id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    @swagger_auto_schema(method="put", request_body=DeliveryDetailSerializer())
    @action(methods=["put"], detail=True)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.vendor != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to perform this action"})
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(method="patch", request_body=DeliveryDetailSerializer())
    @action(methods=["patch"], detail=True)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.vendor != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to perform this action"})
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.vendor != request.user:
            raise PermissionDenied(detail={"message": "you do not have permission to perform this action"})
        return super().delete(request, *args, **kwargs)
    
    
    

@api_view(["GET", "PUT"])
def order_item_detail(request, booking_id, item_id):
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)
    except Order.DoesNotExist:
        raise NotFound(detail={"message": "order not found"})
    
    
    try:
        item = OrderItem.objects.get(order=order, id=item_id, is_deleted=False)
    except OrderItem.DoesNotExist:
        raise NotFound(detail={"message": "order not found"})
    
    
    if request.method == "GET":
        serializer = OrderItemSerializer(item)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    elif request.method == "PUT":
        serializer = OrderItemSerializer(item, data=request.data, partial=True)
        
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({"message" : "success"}, status=status.HTTP_200_OK)
    
    
    


# @api_view(["PUT"])
# def update_orderitem_status(request, booking_id, item_id):
    
#     try:
#         order = Order.objects.get(booking_id=booking_id, is_deleted=False)
#     except Order.DoesNotExist:
#         raise NotFound(detail={"message": "order not found"})
    
    
#     try:
#         item = OrderItem.objects.get(order=order, id=item_id, is_deleted=False)
#     except OrderItem.DoesNotExist:
#         raise NotFound(detail={"message": "order not found"})
    
    
#     if request.method == "PUT":
#         serializer = OrderItemSerializer(item, data=request.data, partial=True)
        
#         serializer.is_valid(raise_exception=True)
        
#         serializer.save()
        
#         return Response({"message" : "success"}, status=status.HTTP_200_OK)



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_default_address(request, id):
    
    user = request.user
    
    try:
        address = Address.objects.get(id=id, user=user ,is_deleted=False)
    except Address.DoesNotExist:
        raise NotFound(detail={"message": "address not found"})
    
    
    user.addresses.filter(is_deleted=False).update(is_default=False)
    
    address.is_default=True
    address.save()
    
    
            
            
    return Response({"message" : "success"}, status=status.HTTP_200_OK)
    
    
    
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def accept_order(request, booking_id):
    
   
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_paid_for=True ,is_deleted=False, status='pending')
    except Order.DoesNotExist:
        raise NotFound(detail={"message": "order not found"})
    
    if order.is_paid_for and order.status == "pending":
        
    
        order.status="processing"
        order.processed_at = timezone.now()
        order.save()
        
        
        order.items.filter(status="pending", is_deleted=False).update(status="confirmed",
                                                    confirmed_at= timezone.now())
        
        
                
                
        return Response({"message" : "success"}, status=status.HTTP_200_OK)
    
    
    else:
        raise ValidationError(detail={"message" : "cannot accept and unpaid order"})
    

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_items(request):
    """Returns a list of order items for vendor to attend to"""
    
    items = OrderItem.objects.filter(item__vendor=request.user, status="confirmed", is_deleted=False).order_by("-date_added")
    
   
    serializer = OrderItemSerializer(items, many=True)
    
    
    

    return Response(serializer.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_update_item_status(request, id):
    """Allows vendor to update the status of an order item"""
    
    try:
        item = OrderItem.objects.get(id=id, is_deleted=False)
    except OrderItem.DoesNotExist:
        raise ValidationError(detail={"message":"order item is not valid or has been deleted"})
    
        
    if item.vendor != request.user:
        raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
   
    if item.status == "user-canceled":
        raise ValidationError(detail={"message":"item has been canceled from the order"})
    
    if request.method == "POST":
        serializer = UpdateStatusSerializer(data = request.data)
        
        serializer.is_valid(raise_exception=True)
        
        status = serializer.validated_data.pop("status")
        
        
        rules = {
            "processing" : "confirmed",
            "in-transit" : "processing",
            "delivered"  : "in-transit",
        }
        
        if item.status == rules.get(status):
            item.status = status
            item.save()
    

            return Response({"message":"success"}, status=status.HTTP_200_OK)
        
        else:
            raise ValidationError(detail={"message" : f"Order has to be {rules.get(status)} before {status}"})
        
        
        
@api_view(["GET"])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAdminUser])
def dashboard_stat(request):
    payments = PaymentDetail.objects.all()
    
    
    payment_data = {
        "specta" : payments.filter(payment_type="specta").count(),
        "outright" : payments.filter(payment_type="outright").count(),
        "lease" :payments.filter(payment_type="lease").count(),
        "power-as-a-service" : payments.filter(payment_type="power-as-a-service").count(),
        }
    
    orders = Order.objects.filter(is_deleted=False)
    order_data = {
        "total_order" :  orders.count(),
        "pending"  : orders.filter(status="pending").count(),
        "processing"  : orders.filter(status="processing").count(),
        "completed"  : orders.filter(status="completed").count(),
        
        
    }
    
    data = {
        'order_data' : order_data,
        "payment_data" : payment_data
    }
    
    return Response(data, status=status.HTTP_200_OK)



class PayOutList(ListAPIView):
    serializer_class = PayOutSerializer
    queryset = PayOuts.objects.all()



class PayOutDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = PayOutSerializer
    queryset = PayOuts.objects.all()
    lookup_field = "id"