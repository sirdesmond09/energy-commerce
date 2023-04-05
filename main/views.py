from datetime import datetime
import random
from accounts.models import ActivityLog
from main.helpers import payment_is_verified, calculate_start_date
from .serializers import AddOrderSerializer, AddProductSerializer, AddressSerializer, CalculatorItemSerializer, CancelResponseSerializer, CancelSerializer, CartSerializer, CommissionSerializer, EnergyCalculatorSerializer, FAQSerializer, GallerySerializer, LocationSerializer, MultipleProductSerializer, OrderItemSerializer, OrderSerializer, PayOutSerializer, PaymentSerializer, ProductComponentSerializer, ProductSerializer, CategorySerializer, RatingSerializer, StatusSerializer, TermAndConditionSerializer, UpdateStatusSerializer, UserInboxSerializer
from .models import Address, CalculatorItem, Cart, Commission, FrequentlyAskedQuestion, Location, Order, OrderItem, PayOuts, PaymentDetail, ProductCategory, Product, ProductComponent, ProductGallery, Rating, TermAndCondition, UserInbox, ValidationOTP
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.generics import ListCreateAPIView, ListAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView, UpdateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from accounts.permissions import CalculatorItemTablePermissions, CommissionTablePermissions, CustomDjangoModelPermissions, DashboardPermission, FAQTablePermissions, IsUserOrVendor, IsVendor, IsVendorOrReadOnly, OrderItemTablePermissions, OrderTablePermissions, PaymentTablePermissions, ProductCategoryPermissions, ProductTablePermissions, RatingTablePermissions
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from django.utils import timezone
from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination
import calendar
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.utils import ProgrammingError
from django.db.models import Case, F, Value, When


User = get_user_model()

pagination_class = LimitOffsetPagination()

try:
    commission = Commission.objects.all()

    if commission.count() == 0:
        Commission.objects.create(percent=12)
        
    COMMISSION = round(Commission.objects.first().percent / 100, 2)
except ProgrammingError:
    COMMISSION = 0.12

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
    permission_classes = [ProductCategoryPermissions]
    
    
    
@swagger_auto_schema(method="post", request_body=AddProductSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsVendor])
def add_product(request):
    
    """Allows only vendors to add their products"""
    
    serializer = AddProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.validated_data['product']['vendor'] = request.user
    serializer.save()
    
    return Response({"message": "successful"}, status=status.HTTP_201_CREATED)
    
    

class ProductList(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_deleted=False, status="verified",  vendor__vendor_status="approved",)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        
        category = request.GET.get('category', None)
        store = request.GET.get('store', None)
        min_price = request.GET.get("min_price", None)
        max_price = request.GET.get("max_price", None)
        location = request.GET.get("location", None)
        
        
        
        queryset = self.filter_queryset(self.get_queryset())
        
        
        if category:
            queryset = queryset.filter(category__name=category)
            
        if store:
            queryset = queryset.filter(vendor__store__id=store)
            
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
    queryset = Product.objects.filter(is_deleted=False).order_by("-date_added", "status")
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsVendor | ProductTablePermissions]
    
    def list(self, request, *args, **kwargs):
        
        category = request.GET.get('category', None)
        status = request.GET.get('status', None)
        vendor = request.GET.get('vendor', None)
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if request.user.role == "vendor":
            queryset = queryset.filter(vendor=request.user)
            
        if category:
            queryset = queryset.filter(category__name=category)
            
        if status:
            queryset = queryset.filter(status=status)
            
        if vendor:
            if request.user.role=="admin":
                queryset = queryset.filter(vendor__id=vendor)
            else:
                raise PermissionDenied(detail={"message": "Permission denied"})
            
            
            

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    

class ProductDetail(RetrieveDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_deleted=False)
    lookup_field="id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsVendorOrReadOnly]
    
    
    
@swagger_auto_schema(method="patch", request_body=AddProductSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsVendor])
def edit_product(request, product_id):
    
    """Allows only vendors to edit their products"""
    
    try:
        product  = Product.objects.get(id=product_id, is_deleted=False)
    except Product.DoesNotExist:
        raise NotFound(detail={"message": "Product not found"})
    
    serializer = AddProductSerializer(product, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    product.status = "pending"
    product.save()
    
    return Response({"message": "successful"}, status=status.HTTP_201_CREATED)
    

@swagger_auto_schema(method="patch", request_body=StatusSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([ProductTablePermissions])
def update_product_status(request, product_id):
    
    """Admin use this endpoint to update the status of a product. You can send either `verified` or  `unapproved` to mark the product as approved or unapproved"""
    
    try:
        product = Product.objects.get(id=product_id, is_deleted=False)
        
    except Product.DoesNotExist:
        raise NotFound(detail={"message": "Product not found or does not exist"})
    
    
    if request.method == "PATCH":
        serializer = StatusSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data.get("status")
        
        if new_status not in ("verified",  "unapproved"):
            raise ValidationError({"message": "status must be 'verified' or 'unapproved'"})
        
        product.status = new_status
        product.save()
        
        # TODO: send notice to vendor about status
        UserInbox.objects.create(
                user = product.vendor,
                heading = f"Product '{product.name}' update",
                body = f"Your product has been {new_status}"
                )
        
        return Response({"message": "Status updated"}, status=status.HTTP_200_OK)



@swagger_auto_schema(method="delete", request_body=GallerySerializer(many=True))
@api_view(["POST", "DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsVendor])
def update_galley(request, product_id, img_id=None):
    
    if request.method == "POST":
        serializer = GallerySerializer(data=request.data, many=True)
        images = []
        serializer.is_valid(raise_exception=True)
        
        try:
            product = Product.objects.get(id=product_id, is_deleted=False)
            
            for data in serializer.validated_data:
                images.append(ProductGallery(**data, product=product))
            ProductGallery.objects.bulk_create(images)
            
        except Product.DoesNotExist:
            raise NotFound(detail={"message": "Product not found or does not exist"})
    
    
        except Exception as e:
            raise ValidationError(str(e))
        
        
        ActivityLog.objects.create(
                user=request.user,
                action = f"Added {len(images)} image(s) to product gallery"
            )
        
        return Response({"message": "success"}, status=status.HTTP_202_ACCEPTED)
    
    
    
    elif request.method == "DELETE":
        
        if img_id is None:
            raise ValidationError({"message": "image_id is required"})
        
        try:
            img = ProductGallery.objects.get(id=img_id, product__id=product_id,is_deleted=False)
            
            img.delete()
            
        except ProductGallery.DoesNotExist:
            raise NotFound(detail={"message": "Image not found or does not exist"})
        
        ActivityLog.objects.create(
                user=request.user,
                action = f"Removed image from product gallery"
            )
        
        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)
    
    

class LocationView(ListCreateAPIView):
    serializer_class = LocationSerializer
    queryset = Location.objects.all().order_by('-date_added')
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    


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
    permission_classes = [IsVendorOrReadOnly]
    
    

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
        
        ActivityLog.objects.create(
                user=request.user,
                action = f"created new delivery address"
            )
        
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
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
            PaymentDetail.objects.create(**serializer.validated_data, order=order, user=request.user, payment_type='outright', status="approved")
            
            
            #mark order as paid
            order.is_paid_for =True
            order.status = "pending"
            order.save()
            
            payouts = [PayOuts(vendor=order_item.item.vendor,
                               item= order_item,
                               amount = ((order_item.unit_price * order_item.qty) - ((order_item.unit_price * order_item.qty) * COMMISSION)) + ((order_item.delivery_fee + order_item.installation_fee)* order_item.qty),
                               order_booking_id = order.booking_id,
                               commission = (order_item.unit_price * order_item.qty) * COMMISSION,commission_percent = COMMISSION,
                                                    ) for order_item in order.items.filter(is_deleted=False)]
            
            
            PayOuts.objects.bulk_create(payouts)
            
            ActivityLog.objects.create(
                user=request.user,
                action = f"Created and paid outright for order {order.booking_id}"
            )
            
            data = {
                "message": "success",
                "booking_id": order.booking_id,
                "total_amount" : order.total_price
            }
            
            return Response(data, status=status.HTTP_201_CREATED)
        
        else:
            return Response({"message":"payment not successful"}, status=status.HTTP_201_CREATED)
                
    
    
@swagger_auto_schema(method="post", request_body=PaymentSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def lease_to_own_payment(request, booking_id):
    
    if request.method == "POST":
        
        try:
            order = Order.objects.get(booking_id=booking_id, is_deleted=False)
        except KeyError:
            raise ValidationError(detail={"message": "order was not found"})
        
        if order.is_paid_for:
            raise ValidationError(detail={"message": "multiple payment not allowed. order has been paid for"})
        
        if PaymentDetail.objects.filter(order=order).exists():
            raise ValidationError(detail={"message": "payment already initiated for this order. please contact support"})
            
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        try:
            trans_id = serializer.validated_data["transaction_id"]
        except KeyError:
            raise ValidationError(detail={"message": "transaction_id was not provided"})
        
            
    
        #create payment record
        PaymentDetail.objects.create(**serializer.validated_data, order=order, user=request.user, payment_type='lease', status="pending")
        
        
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Created and request lease to own for order {order.booking_id}"
        )
        
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
def power_as_a_service_payment(request, booking_id):
    
    if request.method == "POST":
        
        try:
            order = Order.objects.get(booking_id=booking_id, is_deleted=False)
        except KeyError:
            raise ValidationError(detail={"message": "order was not found"})
        
        if order.is_paid_for:
            raise ValidationError(detail={"message": "multiple payment not allowed. order has been paid for"})
        
        if PaymentDetail.objects.filter(order=order).exists():
            raise ValidationError(detail={"message": "payment already initiated for this order. please contact support"})
            
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        try:
            trans_id = serializer.validated_data["transaction_id"]
        except KeyError:
            raise ValidationError(detail={"message": "transaction_id was not provided"})
        
            
    
        #create payment record
        PaymentDetail.objects.create(**serializer.validated_data, order=order, user=request.user, payment_type='power-as-a-service', status="pending")
        
        
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Created and request power as a service for order {order.booking_id}"
        )
        
        data = {
            "message": "success",
            "booking_id": order.booking_id,
            "total_amount" : order.total_price
        }
        
        return Response(data, status=status.HTTP_201_CREATED)
        


@swagger_auto_schema(method="patch", request_body=PaymentSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([PaymentTablePermissions])
def validate_payment(request, payment_id):  
    
    try:
        payment = PaymentDetail.objects.get(id=payment_id, is_deleted=False, status="pending") 
    except PaymentDetail.DoesNotExist:
        raise NotFound(detail={"message":"payment not found"})
    
    serializer  = PaymentSerializer(payment, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data.get("status", None)
    
    if data and data in ("approved", "declined"):
                
        order = payment.order
        action = ""
        
        if payment.payment_type == "lease":
            action = "lease to own"
        
        elif payment.payment_type == "power-as-a-service":
            action = "power as a service"
        
        if data == "approved":
            payment.status = data
            payment.save()
            
            #mark order as paid
            order.is_paid_for =True
            order.status = "pending"
            order.save()

            # create payout
            
            payouts = [PayOuts(vendor=order_item.item.vendor,
                                item= order_item,
                                amount = ((order_item.unit_price * order_item.qty) - ((order_item.unit_price * order_item.qty) * COMMISSION)) + ((order_item.delivery_fee + order_item.installation_fee)* order_item.qty),
                                order_booking_id = order.booking_id,
                                commission = (order_item.unit_price * order_item.qty) * COMMISSION,commission_percent = COMMISSION,
                                                    ) for order_item in order.items.filter(is_deleted=False)]
            
            
            PayOuts.objects.bulk_create(payouts)
            

            
            UserInbox.objects.create(
                user = order.user,
                heading = f"Order {order.booking_id} update",
                body = f"Your {action} has been approved"
                )
            
        else:
            payment.status = data
            payment.save()
            
            order.status = "canceled"
            order.cancellation_response_reason = f"{action} was declined"
            order.cancel_responded_at = timezone.now()
            order.save()
            
            
            
            ##check if all other items are canceled, then mark order as canceled
            for order_item in order.items.filter(is_deleted=False):
                order_item.status="canceled"
                order_item.cancellation_response_reason = f"{action} was declined"
                order_item.cancel_responded_at = timezone.now()
                order.save()
                
                order_item.item.qty_available += order_item.qty
                order_item.item.save()
                
                
            UserInbox.objects.create(
                user = order.user,
                heading = f"Order {order.booking_id} update",
                body = f"Your {action} has been declined"
                )
        
        
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"{data.title()} {action} for order {order.booking_id}"
        )
        
        return Response({"message": "success"}, status=status.HTTP_200_OK)
    
    
    raise ValidationError(detail={"message": "status cannot be {} it should be either verified or declined".format(data)})
        
    
               
                

@swagger_auto_schema(method="post", request_body=EnergyCalculatorSerializer(many=True))
@api_view(["POST"])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def energy_calculator(request):
    
    if request.method == "POST":
        
        serializer = EnergyCalculatorSerializer(data=request.data)
        
        if serializer.is_valid():
            
            # battery = serializer.validated_data.get('battery_type')
        
            # if battery == "Tubular":
            #     discharge_depth = 0.50
            # elif battery == "Lithium":
            #     discharge_depth = 0.92
            # elif battery == "Dry cell (SMF)":
            #     discharge_depth = 0.3
            # else:
            #     raise ValidationError(detail={"message":"select battery type"})
            
            energy_loss = 0.3
            power_factor = 0.8
        
            sys_cap_limit = 0.7
            # volt = 24
            # batt_unit = 150
            
            # total_load = round(sum([data["wattage"] for data in serializer.validated_data])/(1-energy_loss), 2)
            
            # watt_hr = [data["wattage"] * data["hours"] for data in serializer.validated_data]
            
            total_load = serializer.validated_data.get("total_wattage")
            # watt_hr = serializer.validated_data.get("total_watt_hour")
            # total_watt_hr = round(sum(watt_hr)/(1-energy_loss), 2)
            
            
            inverter_capacity = round(total_load/(sys_cap_limit*power_factor*1000), 2)
            
            
            # battery_cap = round((total_watt_hr/volt)/discharge_depth, 2)
            
            # batt_total = round(battery_cap/batt_unit, 2)
            
            products = Product.objects.filter(category__name__icontains='complete solution', 
                                   total_power_kva__range=[inverter_capacity, inverter_capacity+1],
                                   status="verified",
                                   vendor__vendor_status="approved",
                                   is_deleted=False)
            
            
            # products = Product.objects.filter(category__name='Complete Solution').annotate(
            #     effective_capacity=Case(
            #         When(battery_type='Tubular', then=F('battery_capacity') * 0.5),
            #         When(battery_type='Lithium', then=F('battery_capacity') * 0.92),
            #         When(battery_type='SMF', then=F('battery_capacity') * 0.3),
            #         default=F('battery_capacity')
                
            # ).annotate(
            #     effective_power=F('output_power') * 1000,  # convert from KVA to VA (volt-ampere)
            #     effective_WH=F('effective_capacity') * F('voltage') * F('effective_power') * 0.8 / 1000,  # convert from VA to Wh (watt-hour)
            #     limit_WH=F('effective_WH') * 0.7  # assuming product limit of 70%
            # ).filter(effective_WH_gte=WH, effective_power_gte=W).order_by('-effective_WH')[:4]
            
            
            
            
            data = {"total_load": total_load,
                    #"total_watt_hr": total_watt_hr,
                    "suggested_inverter_capacity":inverter_capacity,
                    # "estimated_battery_cap": battery_cap,
                    # "suggested_unit_battery_total":batt_total,
                    "recommendations": ProductSerializer(products, many=True).data}
            
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
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Created a new cart"
            )
            
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
@permission_classes([IsUserOrVendor])
def request_order_cancel(request, booking_id):
    
    """Use this endpoint to request to cancel the whole order"""
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)
    except Order.DoesNotExist:
        raise ValidationError(detail={"message": "order was not found"})
    
    if order.status == "cancel-requested":
        raise PermissionDenied(detail={"message":"cancel already requested"})
    
    if order.status == "canceled":
        raise PermissionDenied(detail={"message":"order is already canceled"})
    
    if request.method == "DELETE":
        serializer = CancelSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        
        order.prev_status = order.status
        order.status = "cancel-requested"
        order.cancellation_reason = serializer.validated_data.get("reason")
        order.cancel_requested_at = timezone.now()
        order.save()
        
        ActivityLog.objects.create(
                user=request.user,
                action = f"Requested to cancel order {booking_id}"
                )
        
        return Response({"message":"success"},status=status.HTTP_202_ACCEPTED)
    
    
    
    
@swagger_auto_schema(method="delete", request_body=CancelSerializer())
@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def request_order_item_cancel(request, booking_id, item_id):
    
    """Use this endpoint to request cancel  for an item in the order or admin can use this endpoint to cancel directly."""
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)
        order_item = OrderItem.objects.get(id=item_id, order=order,is_deleted=False)
        
    except Order.DoesNotExist:
        raise ValidationError(detail={"message": "order was not found"})
    
    except OrderItem.DoesNotExist:
        raise ValidationError(detail={"message": "item was not found"})
    
    if request.method == "DELETE":
        serializer = CancelSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
            
        if request.user.role == "admin":
            order_item.status = "canceled"
            order_item.cancellation_response_reason = serializer.validated_data.get("reason")
            order_item.cancel_responded_at = timezone.now()
            order_item.save()
            
            order_item.item.qty_available += order_item.qty
            order_item.item.save()
            
            ##check if all other items are canceled, then mark order as canceled
            order = order_item.order
            if all(i.status == "canceled" for i in order.items.filter(is_deleted=False)):
                order.status="canceled"
                order.cancellation_response_reason = "all items were cancelled"
                order.cancel_responded_at = timezone.now()
                order.save()
            
            ActivityLog.objects.create(
                        user=request.user,
                        action = f"Cancel order item ID {item_id} from order {booking_id}"
                        )
            
            
            UserInbox.objects.create(
                user = order.user,
                heading = f"Order {order_item.unique_id} canceled",
                body = f"Your order has been disapproved by an administrator"
                )
                
            
        else:
            if order_item.status == "cancel-requested":
                raise PermissionDenied(detail={"message":"cancel already requested"})
            if order_item.status == "canceled":
                raise PermissionDenied(detail={"message":"item is already canceled"})
            
                
            order_item.prev_status = order_item.status
            order_item.status = "cancel-requested"
            order_item.cancellation_reason = serializer.validated_data.get("reason")
            order_item.cancel_requested_at = timezone.now()
            order_item.save()
            
            ActivityLog.objects.create(
                    user=request.user,
                    action = f"Requested to cancel order item ID {item_id} from order {booking_id}"
                    )
            
                
        return Response({"message":"success"},status=status.HTTP_202_ACCEPTED)
    
    
    
@swagger_auto_schema(method="patch", request_body=CancelResponseSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def respond_to_cancel_request(request, booking_id, item_id):
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)       
        obj = OrderItem.objects.get(id=item_id, order=order,is_deleted=False)
    
    except Order.DoesNotExist:
        raise NotFound(detail={"Not found"})
      
    except OrderItem.DoesNotExist:
        raise NotFound(detail={"Not found"})
    
    if obj.status != "cancel-requested":
        raise ValidationError(detail={"message":"owner did not request to cancel"})
        
    serializer = CancelResponseSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    
    response = serializer.validated_data.get("status")
    
    
    if response == "accepted":
        obj.status = "canceled"
        obj.cancellation_response_reason = serializer.validated_data.get("reason")
        obj.cancel_responded_at = timezone.now()
        obj.save()
        
        # if isinstance(obj, Order):
            
        #     products = []
            
        #     for order_item in obj.items.all():
        #         order_item.item.qty_available += order_item.qty
        #         order_item.prev_status = order_item.status
        #         order_item.status = "canceled"
        #         order_item.cancel_responded_at = timezone.now()
        #         order_item.cancellation_response_reason = "order was canceled"
        #         order_item.save()
        #         products.append(order_item.item)
                
        #     Product.objects.bulk_update(products, ["qty_available"])
            
        #     ActivityLog.objects.create(
        #         user=request.user,
        #         action = f"Accepted to cancel order {booking_id}"
        #         )
        
        # elif isinstance(obj, OrderItem):
            
            ### return the products and save
        obj.item.qty_available += obj.qty
        obj.item.save()
        
        ##check if all other items are canceled, then mark order as canceled
        order = obj.order
        if all(i.status == "canceled" for i in order.items.filter(is_deleted=True)):
            order.status="canceled"
            order.cancellation_response_reason = "all items were cancelled"
            order.cancel_responded_at = timezone.now()
            order.save()
            
        ActivityLog.objects.create(
        user=request.user,
        action = f"Accepted to cancel order {obj.unique_id}"
        )
        
        UserInbox.objects.create(
            user = order.user,
            heading = f"Order {obj.unique_id} updated",
            body = f"You request to cancel order {obj.unique_id} was accepted"
            )
        
        UserInbox.objects.create(
            user = obj.item.vendor,
            heading = f"Order {obj.unique_id} canceled",
            body = f"Admin has approved Order {obj.unique_id} to be cancelled."
            )
        
        
                
    elif response == "rejected":  
                
        obj.status = obj.prev_status
        obj.cancellation_response_reason = serializer.validated_data.get("reason")
        obj.cancel_responded_at = timezone.now()
        obj.save()    
        ActivityLog.objects.create(
                user=request.user,
                action = f"Declined a cancel item request"
        )

        UserInbox.objects.create(
                            user = order.user,
                            heading = f"Order {obj.unique_id} updated",
                            body = f"You request to cancel order {obj.unique_id} was declined"
                            )
        
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

    
    if order.is_paid_for == True:
        raise ValidationError(detail={"message":"order has been paid for"})
    
    products = []
    
    for order_item in order.items.all():
        order_item.item.qty_available += order_item.qty
        products.append(order_item.item)
        order_item.delete_permanently()
        
    Product.objects.bulk_update(products, ["qty_available"])
    
    order.delete_permanently()
    return Response({},status=status.HTTP_204_NO_CONTENT)
    
    
    
class OrderList(ListAPIView):
    
    queryset = OrderItem.objects.filter(is_deleted=False).order_by("-date_added")
    
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrVendor |  OrderItemTablePermissions  ]
    
    
    def list(self, request, *args, **kwargs):
        filterBy = request.GET.get('filterBy')
        status = self.request.GET.get('status')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        user_id = request.GET.get('user')
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if request.user.role == "user" or request.user.role == "vendor":
            queryset = queryset.filter(order__user=request.user)
            
        if filterBy == "open":
            queryset = queryset.filter(status__in=["pending",  "confirmed","processing", "in-transit"])
        if  filterBy == "completed":
            queryset = queryset.filter(status__in=["installed",  "delivered"])
        
        if  filterBy == "cancellations":
                queryset = queryset.filter(status__in=["cancel-requested","canceled"])   
                        
        if status:
            queryset = queryset.filter(status=status)
            
        if startDate and endDate:
            startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
            endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
            queryset = queryset.filter(date_added__range=[startDate, endDate])
        
        if user_id:
            if request.user.role=="admin":
                queryset = queryset.filter(order__user__id=user_id)
            else:
                raise PermissionDenied(detail={"message": "Permission denied"})
        

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    

class OrderDetail(RetrieveAPIView):
    queryset = OrderItem.objects.filter(is_deleted=False)
    
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrVendor | OrderItemTablePermissions]
    lookup_field = "id"
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user.role == "user" and instance.order.user != request.user:
            raise PermissionDenied({"message": "cannot retrieve details for another user's order"})
        
            
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    


class PaidOrdersView(ListAPIView):
    
    queryset = Order.objects.filter(is_deleted=False).order_by("-date_added")
    
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrVendor |  OrderTablePermissions  ]
    
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset()) 
            
        
        if request.user.role == "user" or request.user.role == "vendor":
            queryset = queryset.filter(user=request.user, is_paid_for=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    

@api_view(["GET", "PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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
        
        #log activity
        ActivityLog.objects.create(
                user=request.user,
                action = f"Edited an item in order {order.booking_id}"
        )
        
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
    
    
    #log activity
    ActivityLog.objects.create(
            user=request.user,
            action = f"Set an address as default"
    )
            
            
    return Response({"message" : "success"}, status=status.HTTP_200_OK)
    
    
    
    
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([OrderTablePermissions])
def accept_order(request,  booking_id, item_id):
    
   
    
    try:
        order = Order.objects.get(booking_id=booking_id, is_deleted=False)
        item = OrderItem.objects.get(id=item_id, order=order, is_deleted=False)
    except Order.DoesNotExist:
        raise NotFound(detail={"message": "order not found"})
    except OrderItem.DoesNotExist:
        raise NotFound(detail={"message": "Item ordered not found"})
    
    if request.method == "PATCH":
        if order.is_paid_for and item.status == "pending":
            
        
            item.status="confirmed"
            item.confirmed_at = timezone.now()
            item.save()
            
            
                    
            #log activity
            ActivityLog.objects.create(
                    user=request.user,
                    action = f"Accepted order {order.booking_id}"
            )
            
            UserInbox.objects.create(
                            user = order.user,
                            heading = f"Order {item.unique_id} updated",
                            body = f"You order is now {item.status}"
                            )
            
            
            UserInbox.objects.create(
                            user = item.item.vendor,
                            heading = f"Yayyy! You made a sale!",
                            body = f"An order with OrderID {item.unique_id} has been placed"
                            )
            
                    
            return Response({"message" : "success"}, status=status.HTTP_200_OK)
        
        
        else:
            raise ValidationError(detail={"message" : "cannot accept an unpaid order"})
    


        
class VendorItemListView(ListAPIView):
    """Returns a list of order items for vendor to attend to"""
    
    queryset = OrderItem.objects.filter(is_deleted=False).exclude(status="canceled").exclude(status="pending").exclude(status="cancel-requested").order_by("-date_added")
    
   
    serializer_class = OrderItemSerializer
    authentication_classes([JWTAuthentication])
    permission_classes([IsVendor])
    
    
    def list(self, request, *args, **kwargs):
        
        status = self.request.GET.get('status')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        queryset = self.filter_queryset(self.get_queryset()).filter(item__vendor=self.request.user)
        
        if status:
            queryset = queryset.filter(status=status)
            
        
        if startDate and endDate:
            startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
            endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
            queryset = queryset.filter(date_added__range=[startDate, endDate])


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    




@swagger_auto_schema(method="patch", request_body=UpdateStatusSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsVendor | OrderItemTablePermissions ])
def vendor_update_item_status(request, id):
    """Allows vendor to update the status of an order item"""
    
    try:
        item = OrderItem.objects.get(id=id, is_deleted=False)
    except OrderItem.DoesNotExist:
        raise ValidationError(detail={"message":"order item is not valid or has been deleted"})
    
    user_role = request.user.role 
        
    if (item.item.vendor != request.user) and (user_role != "admin"):
        raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
   
    if item.status == "canceled":
        raise ValidationError(detail={"message":"item has been canceled from the order"})
    
    if item.status == "cancel-requested":
        raise ValidationError(detail={"message":"owner has requested to cancel"})
    
    if request.method == "PATCH":
        serializer = UpdateStatusSerializer(data = request.data)
        
        serializer.is_valid(raise_exception=True)
        
        status_ = serializer.validated_data.pop("status")
        
        
        rules = {
            "processing" : "confirmed",
            "in-transit" : "processing",
            "delivered"  : "in-transit",
            "installed" : "delivered",
        }
        
        time_rule = {
             "processing" : "processed_at",
            "in-transit" : "in_transit_at",
            "delivered"  : "delivered_at",
            "installed" : "installed_at",
        }
        
        if item.status == rules.get(status_):
            
            if status_ == "in-transit" and user_role != "admin":
                code = "".join([str(random.choice(range(10))) for _ in range(6)])
                ValidationOTP.objects.create(order_item=item, code = code, vendor=request.user )
                
            
            if status_ == "delivered" and user_role != "admin":
                code = serializer.validated_data.get("verification_code", None)
                
                if code is None:
                    raise ValidationError(detail={"message": "verification code needed to mark order as delivered"})
                
                try:
                    otp = ValidationOTP.objects.get(code=code, order_item=item,vendor=request.user,is_verified=False )
                    
                except ValidationOTP.DoesNotExist:
                    raise ValidationError(detail={"message": "verification code invalid"})
                
                
                otp.is_verified = True
                otp.save()
                
            item.status = status_
            time_field = time_rule.get(status_)
            setattr(item, time_field, timezone.now())
            item.save()

            #log activity
            ActivityLog.objects.create(
                    user=request.user,
                    action = f"Changed order {item.unique_id} status to {item.status}"
            )
            
            UserInbox.objects.create(
                    user =item.order.user,
                    heading = f"Order {item.unique_id}",
                    body = f"You order is now {item.status}"
                    )
            
            return Response({"message":"success"}, status=status.HTTP_200_OK)
        
        else:
            raise ValidationError(detail={"message" : f"Order has to be {rules.get(status_)} before {status_}"})
        
        
        
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([DashboardPermission])
def dashboard_stat(request):
    
    today = timezone.now().date()
    
    payments = PaymentDetail.objects.all()
    
    
    payment_data = {
        "specta" : payments.filter(payment_type="specta").count(),
        "outright" : payments.filter(payment_type="outright").count(),
        "lease" :payments.filter(payment_type="lease").count(),
        "powerService" : payments.filter(payment_type="power-as-a-service").count(),
        }
    
    # orders = Order.objects.filter(is_deleted=False)
    orders = OrderItem.objects.filter(is_deleted=False)
    order_data = {
        "total_order" :  orders.count(),
        "pending"  : orders.filter(status="pending").count(),
        "processing"  : orders.filter(status="processing").count(),
        "completed"  : orders.filter(status="installed").count() + orders.filter(status="delivered").count(),
        
        
    }
    start_date = calculate_start_date(6)
    order_items = OrderItem.objects.filter(is_deleted=False,
                                           date_added__date__range=[start_date, today])
    
    product_orders = {
        "pending" : order_items.filter(status="pending").count(),
        "processing" : order_items.filter(status="processing").count(),
        "delivered" : order_items.filter(status="delivered").count(),
    }
    
    payout = PayOuts.objects.filter(is_deleted=False)
    
    payout_data = {
        "total" : payout.count(),
        "pending" : payout.filter(status="pending").count(),
        "paid" : payout.filter(status="paid").count(),
    }
    
    data = {
        'order_data' : order_data,
        "payment_data" : payment_data,
        "product_orders" : product_orders,
        "payout_data" : payout_data
    }
    
    return Response(data, status=status.HTTP_200_OK)



class PayOutList(ListAPIView):
    serializer_class = PayOutSerializer
    queryset = PayOuts.objects.all()
    
    
    def list(self, request, *args, **kwargs):
        
        status = self.request.GET.get('status')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if status:
            queryset = queryset.filter(status=status)
    
            
        
        if startDate and endDate:
            startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
            endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
            queryset = queryset.filter(date_added__range=[startDate, endDate])


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data)



class PayOutDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = PayOutSerializer
    queryset = PayOuts.objects.all()
    lookup_field = "id"    
    
    


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([DashboardPermission]) 
def admin_dashboard_graph(request):
    """
    Give ADMIN a graph analytics.
    Can add url query `start_date` and `end_date` with the date to start from in the format `YY-MM-DD` e.g `?start_date=2022-01-11&start_date=2022-01-17` to see data from 11th to 17th of january.
    If no query is provided, it gives data for last 7 days
    """
    
    startDate = request.GET.get('start_date')
    endDate = request.GET.get('end_date')
   
    if startDate and endDate:
        start_date = datetime.strptime(startDate, "%Y-%m-%d").date()
        end_date = datetime.strptime(endDate, "%Y-%m-%d").date()

    else:
        start_date = timezone.now() - timezone.timedelta(days=7)
        end_date= timezone.now() 
        
    
    all_orders = OrderItem.objects.filter(is_deleted=False, date_added__date__range=[start_date, end_date])
    sign_ups = User.objects.filter(is_deleted=False, role="user", date_joined__date__range=[start_date, end_date])
    revenues = Order.objects.filter(is_deleted=False, is_paid_for=True, date_added__date__range=[start_date, end_date])
    
    
    
    date_list = [start_date +  timezone.timedelta(days=x) for x in range((end_date-start_date).days)]
    
    array = []
    
    for date in date_list:
        data = {}
        orders = all_orders.filter(date_added__date = date)
        signup = sign_ups.filter(date_joined__date = date)
        revenue = revenues.filter(date_added__date = date)
        data["date"] = date 
        data["num_of_orders"] = orders.count()
        data["total_signup"] =signup.count()
        data['revenue']   = revenue.aggregate(Sum('total_price')).get("total_price__sum", 0)
    
        
        array.append(data)
        
    return Response(array, status=status.HTTP_200_OK)



class PaymentListView(ListAPIView):
    
    """Get a list of payments. You can filter by: `status`, `start_date`, `end_date`, `payment_type`"""
    
    queryset = PaymentDetail.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [PaymentTablePermissions]
    
    
    
    def list(self, request, *args, **kwargs):
        
        status = self.request.GET.get('status')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        payment_type = request.GET.get('payment_type')
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if status:
            queryset = queryset.filter(status=status)
        
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
            
        
        if startDate and endDate:
            startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
            endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
            queryset = queryset.filter(date_added__range=[startDate, endDate])


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
    
    
class PaymentDetailView(RetrieveAPIView):
    
    """Get a payment detail"""

    queryset = PaymentDetail.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [PaymentTablePermissions]
    lookup_field = "id"
    

class RatingCreate(CreateAPIView):
    serializer_class = RatingSerializer
    queryset =Rating.objects.filter(is_deleted=False)
    permission_classes = [IsUserOrVendor]
    authentication_classes = [JWTAuthentication]
    
    
    

class RatingList(ListAPIView):
    serializer_class = RatingSerializer
    queryset =Rating.objects.filter(is_deleted=False)
    permission_classes = [IsVendor | RatingTablePermissions]
    authentication_classes = [JWTAuthentication]
    
    
    def list(self, request, *args, **kwargs):
        
        product = self.request.GET.get('product', None)
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        
        queryset = self.filter_queryset(self.get_queryset())
        
        
        if product:
            queryset = queryset.filter(product__id=product)
            
        
        if startDate and endDate:
            startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
            endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
            queryset = queryset.filter(date_added__range=[startDate, endDate])


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
    
class RatingDetailView(RetrieveUpdateAPIView):
    serializer_class = RatingSerializer
    queryset =Rating.objects.filter(is_deleted=False)
    permission_classes = [IsUserOrVendor]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"
    
    
    
    


class CalculatorItemCreateView(CreateAPIView):
    
    """create a new calculator items."""
    
    queryset = CalculatorItem.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  CalculatorItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [CalculatorItemTablePermissions]
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        self.perform_create(serializer)
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Created calculator item(s)"
            )
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    
class CalculatorItemListView(ListAPIView):
    
    """get all calculator items."""
    
    queryset = CalculatorItem.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  CalculatorItemSerializer




    
    
    
class CalculatorItemDetailView(RetrieveUpdateDestroyAPIView):
    
    """Edit, retrieve, and delete a calculator item"""

    queryset = CalculatorItem.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  CalculatorItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [CalculatorItemTablePermissions]
    
    
    @swagger_auto_schema(method="put", request_body=CalculatorItemSerializer())
    @action(methods=["put"], detail=True)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    
    @swagger_auto_schema(method="patch", request_body=CalculatorItemSerializer())
    @action(methods=["patch"], detail=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):

        return super().delete(request, *args, **kwargs)
    
    


class UserInboxListView(ListAPIView):
    
    """get all inbox."""
    
    queryset = UserInbox.objects.all().order_by('-date_added')
    serializer_class =  UserInboxSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def list(self, request, *args, **kwargs):
        
       
        queryset = self.filter_queryset(self.get_queryset()).filter(user=self.request.user)
        


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
    


class FAQCreateView(CreateAPIView):
    
    """create a new calculator items."""
    
    queryset = FrequentlyAskedQuestion.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  FAQSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [FAQTablePermissions]
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        self.perform_create(serializer)
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Created FAQ"
            )
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    
class FAQListView(ListAPIView):
    
    """get all calculator items."""
    
    queryset = FrequentlyAskedQuestion.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  FAQSerializer




    
    
    
class FAQDetailView(RetrieveUpdateDestroyAPIView):
    
    """Edit, retrieve, and delete a calculator item"""

    queryset = FrequentlyAskedQuestion.objects.filter(is_deleted=False).order_by('-date_added')
    serializer_class =  FAQSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [FAQTablePermissions]
    
    
    @swagger_auto_schema(method="put", request_body=FAQSerializer())
    @action(methods=["put"], detail=True)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    
    @swagger_auto_schema(method="patch", request_body=FAQSerializer())
    @action(methods=["patch"], detail=True)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    
    

class CommissionList(ListAPIView):
    serializer_class = CommissionSerializer
    queryset =Commission.objects.all()
    permission_classes = [CommissionTablePermissions]
    authentication_classes = [JWTAuthentication]
    
    
class CommissionUpdate(RetrieveUpdateAPIView):
    serializer_class = CommissionSerializer
    queryset =Commission.objects.all()
    permission_classes = [CommissionTablePermissions]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"


class TermAndConditionList(ListAPIView):
    serializer_class = TermAndConditionSerializer
    queryset =TermAndCondition.objects.all()
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    
    
class TermAndConditionUpdate(RetrieveUpdateAPIView):
    serializer_class = TermAndConditionSerializer
    queryset =TermAndCondition.objects.all()
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"