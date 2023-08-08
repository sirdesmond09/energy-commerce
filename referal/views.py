from accounts.permissions import ReferralBonusTablePermissions
from .models import ReferralBonus, ReferrerReward
from .serializers import ReferralBonusSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from main.models import Order
from rest_framework.response import Response

User=  get_user_model()

class ReferralBonusList(generics.ListAPIView):
    serializer_class = ReferralBonusSerializer
    queryset =ReferralBonus.objects.all()
    permission_classes = [ReferralBonusTablePermissions]
    authentication_classes = [JWTAuthentication]
    
    
class ReferralBonusUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = ReferralBonusSerializer
    queryset =ReferralBonus.objects.all()
    permission_classes = [ReferralBonusTablePermissions]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def referral_data(request):
    
    referred_users  = User.objects.filter(is_deleted=False,
                                          referred_by=request.user,
                                          role="user").count()
    active_users = ReferrerReward.objects.filter(referrer=request.user).count()
    
    data= {
       "referred_users" : referred_users,
       "active_users" : active_users,
       "balance" : request.user.referral_bonus
    }
    
    return Response(data, status=200)
    
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_first_order(request):
    
    orders  = Order.objects.filter(is_deleted=False, user=request.user)
    return Response({"has_order":orders.exists()}, status=200)
    
    
    
