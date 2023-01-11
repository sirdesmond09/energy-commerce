from .serializers import AddVendorSerializer, LoginSerializer, LogoutSerializer, NewOtpSerializer, OTPVerifySerializer, CustomUserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from .helpers.generators import generate_password
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, logout
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.views import APIView


 
 
User = get_user_model()



class CustomUserViewSet(UserViewSet):
    queryset = User.objects.filter(is_deleted=False)


class AdminListCreateView(ListCreateAPIView):
    
    
    queryset = User.objects.filter(is_deleted=False, is_active=True, role="admin").order_by('-date_joined')
    serializer_class =  CustomUserSerializer
    authentication_classes([JWTAuthentication])
    permission_classes([IsAdminUser])
    
    
    @swagger_auto_schema(method="post", request_body= CustomUserSerializer())
    @action(methods=["post"], detail=True)
    def post(self, request, *args, **kwargs):
        if serializer.is_valid():
                serializer = CustomUserSerializer(data=request.data)
                
                serializer.validated_data['password'] = generate_password()
                serializer.validated_data['is_active'] = True
                serializer.validated_data['is_admin'] = True
                serializer.validated_data['role'] = "admin"
                serializer.save()
                
                data = {
                    'message' : "success",
                    'data' : serializer.data,
                }

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
            print(user)
            if user:
                if user.is_active==True:
                
                    
                    try:
                        
                        refresh = RefreshToken.for_user(user)

                        user_detail = {}
                        user_detail['id']   = user.id
                        user_detail['first_name'] = user.first_name
                        user_detail['last_name'] = user.last_name
                        user_detail['email'] = user.email
                        user_detail['phone'] = user.phone
                        user_detail['role'] = user.role
                        user_detail['is_admin'] = user.is_admin
                        user_detail['access'] = str(refresh.access_token)
                        user_detail['refresh'] = str(refresh)
                        user_logged_in.send(sender=user.__class__,
                                            request=request, user=user)

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
    

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    



