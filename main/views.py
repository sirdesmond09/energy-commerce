from .serializers import AddProductSerializer, GallerySerializer, LocationSerializer, ProductSerializer, CategorySerializer
from .models import Location, ProductCategory, Product, ProductGallery
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import ListCreateAPIView, ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, ValidationError



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
            queryset = queryset.filter(category__id=category)
            
        if vendor:
            queryset = queryset.filter(vendor__id=category)
            
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
    
    
    
    
