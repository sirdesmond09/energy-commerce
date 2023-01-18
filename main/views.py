from .serializers import AddProductSerializer, GallerySerializer, ProductSerializer, CategorySerializer
from .models import ProductCategory, Product, ProductGallery
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
        #TODO: implement filtering
        
        queryset = self.filter_queryset(self.get_queryset())

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
    