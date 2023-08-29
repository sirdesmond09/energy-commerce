from accounts.permissions import CustomDjangoModelPermissions, DashboardPermission, IsUserOrVendor, IsVendor, StoreBankDetailTablePermissions, StoreProfileTablePermissions, UserTablePermissions, VendorPermissions
from main.serializers import ProductSerializer
from .serializers import AddVendorSerializer, AssignRoleSerializer, FirebaseSerializer, GroupSerializer, ImageUploadSerializer, LoginSerializer, LogoutSerializer, ModuleAccessSerializer, NewOtpSerializer, OTPVerifySerializer, CustomUserSerializer, PermissionSerializer, StoreProfileSerializer, BankDetailSerializer, VendorStatusSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from .helpers.generators import generate_password
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate, logout
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView , RetrieveUpdateAPIView
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.views import APIView
from .models import ActivityLog, ModuleAccess, StoreBankDetail, StoreProfile
from django.contrib.auth.hashers import check_password
from main.models import Product, UserInbox
from django.contrib.auth.models import Permission, Group
from django.db.models import Q
import requests
import os
from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings
from main.helpers.signals import password_changed
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.utils.timezone import now



 
 
User = get_user_model()


def get_query():
    
    """returns query to be used to in the permissions view"""
    
    exclude_words = [ "activationotp", "activitylog", "moduleaccess", "logentry","group", "permission", "contenttype", "userinbox", "validationotp", "session", "blacklistedtoken", "outstandingtoken", "cart", ]
    
    query = Q()
    for word in exclude_words:
        query |= Q(codename__icontains=word)
        
    return query
    
   



class CustomUserViewSet(UserViewSet):
    queryset = User.objects.filter(is_deleted=False)
    
    def perform_create(self, serializer):
        referral = serializer.validated_data.pop("referral_code")

        user = serializer.save()
        if referral is not None:
            ref = User.objects.filter(referral_code=referral).first()
            user.referred_by = ref
            user.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)
            
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(role="user")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get("current_password")
        
        if check_password(password, instance.password):
            
            self.perform_destroy(instance)
            ActivityLog.objects.create(
                user=instance,
                action = f"Deleted account"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        elif request.user.role == "admin" and check_password(password, request.user.password):
            self.perform_destroy(instance)
            ActivityLog.objects.create(
                user=request.user,
                action = f"Deleted account with ID {instance.id}"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # elif password=="google" and request.user.provider=="google":
        #     self.perform_destroy(instance)
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise AuthenticationFailed(detail={"message":"incorrect password"})
        
    
    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        
        user_data = request.user.__dict__
        user_data['password'] = serializer.data["new_password"]
        password_changed.send(sender=User, user_data=user_data)
        

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
            
        serializer.user.save()
        user_data = request.user.__dict__
        user_data['password'] = serializer.data["new_password"]
        password_changed.send(sender=User, user_data=user_data)

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminListCreateView(ListCreateAPIView):
    
    
    queryset = User.objects.filter(is_deleted=False, is_active=True, role="admin").order_by('-date_joined')
    serializer_class =  CustomUserSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [CustomDjangoModelPermissions]
    
    
    @swagger_auto_schema(method="post", request_body= CustomUserSerializer())
    @action(methods=["post"], detail=True)
    def post(self, request, *args, **kwargs):
        
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            
            if serializer.validated_data.get('is_superuser') == True and request.user.is_superuser == True:
                
                serializer.validated_data['is_superuser'] = True
                serializer.validated_data['is_staff'] = True
                
                
            elif serializer.validated_data.get('is_superuser', None) != True  :
                serializer.validated_data['is_superuser'] = False
                serializer.validated_data['is_staff'] = False
            
            else:
                raise PermissionDenied(detail={"message": "you do not have permission to perform this action"})
            password = generate_password()
            serializer.validated_data['password'] = password
            serializer.validated_data['is_active'] = True
            serializer.validated_data['is_admin'] = True
            serializer.validated_data['role'] = "admin"
            instance = serializer.save()
            
            
            data = {
                'message' : "success",
                'data' : serializer.data,
            }
            
            ActivityLog.objects.create(
            user=request.user,
            action = f"Created admin with email {instance.email}"
            )

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {

                'message' : "failed",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)
            
            



@swagger_auto_schema(method='post', request_body=LoginSerializer())
@api_view([ 'POST'])
def user_login(request):
    
    """Allows users to log in to the platform. Sends the jwt refresh and access tokens. Check settings for token life time."""
    
    if request.method == "POST":
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = authenticate(request, email = data['email'], password = data['password'], is_deleted=False)

            if user:
                if user.is_active==True:
                
                    if user.role == "vendor" and user.vendor_status != "approved":
                        raise PermissionDenied(detail='cannot login as vendor. your current status is {}'.format(user.vendor_status))
                    
                    try:
                        
                        refresh = RefreshToken.for_user(user)

                        user_detail = {}
                        user_detail['id']   = user.id
                        user_detail['first_name'] = user.first_name
                        user_detail['last_name'] = user.last_name
                        user_detail['email'] = user.email
                        user_detail['phone'] = user.phone
                        user_detail['role'] = user.role
                        user_detail['last_login'] = now()
                        user_detail['is_admin'] = user.is_admin
                        user_detail['is_superuser'] = user.is_superuser
                        user_detail['access'] = str(refresh.access_token)
                        user_detail['refresh'] = str(refresh)
                        user_logged_in.send(sender=user.__class__,
                                            request=request, user=user)

                        if user.role == 'admin':
                            user_detail["modules"] = user.module_access
                            
                        data = {
    
                        "message":"success",
                        'data' : user_detail,
                        }
             
                        return Response(data, status=status.HTTP_200_OK)
                    

                    except Exception as e:
                        raise e
                
                else:
                    data = {
                    
                    'error': 'This account has not been activated'
                    }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

            else:
                data = {
                    
                    'error': 'Please provide a valid email and a password'
                    }
                return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        else:
                data = {
                    
                    'error': serializer.errors
                    }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
            
@swagger_auto_schema(method="post",request_body=LogoutSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Log out a user by blacklisting their refresh token then making use of django's internal logout function to flush out their session and completely log them out.

    Returns:
        Json response with message of success and status code of 204.
    """
    
    serializer = LogoutSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    
    try:
        token = RefreshToken(token=serializer.validated_data["refresh_token"])
        token.blacklist()
        user=request.user
        user_logged_out.send(sender=user.__class__,
                                        request=request, user=user)
        logout(request)
        
        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)
    except TokenError:
        return Response({"message": "failed", "error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="patch",request_body=FirebaseSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_firebase_token(request):
    """Update the FCM token for a logged in use to enable push notifications

    Returns:
        Json response with message of success and status code of 200.
    """
    
    serializer = FirebaseSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    
    fcm_token = serializer.validated_data.get("fcm_token")

    request.user.fcm_token = fcm_token
    request.user.save()
        
    return Response({"message": "success"}, status=status.HTTP_200_OK)
    



@swagger_auto_schema(methods=['POST'],  request_body=NewOtpSerializer())
@api_view(['POST'])
def reset_otp(request):
    if request.method == 'POST':
        serializer = NewOtpSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.get_new_otp()
            
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        
            
@swagger_auto_schema(methods=['POST'], request_body=OTPVerifySerializer())
@api_view(['POST'])
def otp_verification(request):
    
    """Api view for verifying OTPs """

    if request.method == 'POST':

        serializer = OTPVerifySerializer(data = request.data)

        if serializer.is_valid():
            data = serializer.verify_otp(request)
            
            return Response(data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


    



class AddVendorView(APIView):
    
    serializer_class = AddVendorSerializer
    

    @swagger_auto_schema(method="post", request_body= AddVendorSerializer())
    @action(methods=["post"], detail=True)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(serializer.validated_data)
            ActivityLog.objects.create(
                user=instance,
                action = f"Signed up as a vendor"
                )
            return Response({"message":"success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

@swagger_auto_schema(methods=['PATCH'], request_body=VendorStatusSerializer())
@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([VendorPermissions])
def update_vendor_status(request, vendor_id):
    
    """Api view for marking a vendor as approved, blocked or unapproved"""

    if request.method == 'PATCH':
        
        try:
            user = User.objects.get(id=vendor_id, role="vendor", is_deleted=False)
        except User.DoesNotExist:
            raise NotFound(detail={"message": "vendor not found"})

        serializer = VendorStatusSerializer(data = request.data)

        serializer.is_valid(raise_exception=True)
        
        user.vendor_status = serializer.validated_data.get("status")
        user.sent_vendor_email = False
        user.save()
        
        return Response({"message":"success"}, status=status.HTTP_200_OK)
        

class VendorListView(ListAPIView):
    
    
    queryset = User.objects.filter(is_deleted=False, role="vendor").order_by('-date_joined')
    serializer_class =  CustomUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [VendorPermissions]
    
    
    def list(self, request, *args, **kwargs):
        
        status = self.request.GET.get('status')
        queryset = self.filter_queryset(self.get_queryset())
      
        if status:
            queryset = queryset.filter(vendor_status=status)
            
        
       

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
  
class StoreListView(ListAPIView):
    
    
    queryset = StoreProfile.objects.filter(is_deleted=False).order_by('-date_joined')
    serializer_class =  StoreProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [StoreProfileTablePermissions]
    

class StoreDetailView(RetrieveUpdateAPIView):
    queryset = StoreProfile.objects.filter(is_deleted=False).order_by('-date_joined')
    serializer_class =  StoreProfileSerializer
    lookup_field = "id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsVendor | StoreProfileTablePermissions ]
    

class BankDetailView(RetrieveUpdateDestroyAPIView):
    queryset = StoreBankDetail.objects.filter(is_deleted=False).order_by('-date_joined')
    serializer_class =  BankDetailSerializer
    lookup_field = "id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [StoreBankDetailTablePermissions]
    
    
    def put(self, request, *args, **kwargs):
        
        if request.user.payouts.filter(is_deleted=False, status="processing").exists():
            raise PermissionDenied(detail={"your bank details cannot be updated at this time. Please contact support"})
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        
        if request.user.payouts.filter(is_deleted=False, status="processing").exists():
            raise PermissionDenied(detail={"your bank details cannot be updated at this time. Please contact support"})
        
        return self.partial_update(request, *args, **kwargs)
    
    
    
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOrVendor])
def user_favourites(request):
    
    if  request.method == "GET":
        serializer = ProductSerializer(request.user.favourite, many=True)
        
        return Response( {"data":serializer.data}, status=status.HTTP_200_OK)
    



@api_view(["PUT", "DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_favorite(request, product_id=None):
    
    """Use this method to add or remove favourite products"""
    
    user = request.user
    
    try:
        product = Product.objects.get(id=product_id, is_deleted=False)
    except Product.DoesNotExist:
        raise NotFound('Product not found')
    
    if request.method == 'PUT':
        user.favourite.add(product)
        
        ActivityLog.objects.create(
                user=request.user,
                action = f"Added a product to favorites"
                )
        
        return Response({"message": "successfully added"}, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        user.favourite.remove(product)
        ActivityLog.objects.create(
                user=request.user,
                action = f"Removed a product from favorites"
                )
        return Response({"message": "successfully removed"}, status=status.HTTP_200_OK) 
    
    
    

class PermissionList(ListAPIView):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.exclude(get_query())
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    
    
class ModuleAccessList(ListAPIView):
    serializer_class = ModuleAccessSerializer
    queryset = ModuleAccess.objects.all()
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]


class GroupListCreate(ListCreateAPIView):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]


class GroupDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    lookup_field = "id"
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    
    


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([DashboardPermission])
def dashboard_vendor_stat(request):
    
    """Gives admin a statistc of vendor information"""
    vendors = User.objects.filter(role="vendor", is_deleted=False)
    
  
    data = {
        "total" :  vendors.count(),
        "approved"  : vendors.filter(vendor_status="approved").count(),
        "applied"  : vendors.filter(vendor_status="applied").count(),
        "blocked"  :  vendors.filter(vendor_status="blocked").count(),
        
        
    }
    
    
    return Response(data, status=status.HTTP_200_OK)






@swagger_auto_schema(method="patch", request_body=AssignRoleSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([UserTablePermissions])
def assign_role(request, user_id):
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
    
    except User.DoesNotExist:
        raise NotFound(detail={"message":"Admin not found"})
    
    
    if user.role != "admin":
        raise ValidationError(detail={"message":"this is not an admin user"})
    
    if request.method == "PATCH":
    
        serializer = AssignRoleSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        roles = serializer.validated_data.get("roles")
        user.groups.add(*roles)
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Updated roles for {user.email}"
            )
        
        return Response({"message":"success"}, status=status.HTTP_200_OK)
        
        
        
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activity_logs(request):
    
    """shows 10 most recent logged user activities"""
    
    logs = ActivityLog.objects.filter(is_deleted=False, user=request.user).order_by("-date_created").values("action")[:10]
    
    
    
    return Response(logs, status=status.HTTP_200_OK)



@swagger_auto_schema(method="post", request_body=ImageUploadSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def image_upload(request):
    
    if request.method == "POST":
        serializer = ImageUploadSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        user.image = serializer.validated_data.get("image")
        
        user.save()
        
        return Response({"message": "upload successful"}, status=status.HTTP_200_OK)
    
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_mono_token(request):
    
    res = requests.post(url=os.getenv("MONO_URL"), data={
        "client_id": os.getenv('MONO_CLIENT_ID'),
        "client_secret": os.getenv('MONO_CLIENT_SECRET'),
        "audience":os.getenv('MONO_AUDIENCE'),
        "grant_type":"client_credentials"}
                  )
    
    
    return Response(res.json())


@api_view(["GET"])
def check_ref_code(request):
    
    referralCode = request.GET.get("ref")
    if referralCode is not None:
        ref = User.objects.filter(referral_code=referralCode).first()
        
        return Response({"first_name":ref.first_name,
                        "last_name":ref.last_name,
                        "image":ref.image_url})
    return Response({"error":"invalid"}, status=404)
    