from accounts.models import ActivityLog
from accounts.permissions import ReferralBonusTablePermissions, UserBankAccountTablePermissions, WithdrawalTablePermissions
from .models import ReferralBonus, ReferrerReward, UserBankAccount, Withdrawal
from .serializers import ReferralBonusSerializer, UserBankAccountSerializer, WithdrawalSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from main.models import Order, UserInbox
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime

User=  get_user_model()

class ReferralBonusList(generics.ListAPIView):
    serializer_class = ReferralBonusSerializer
    queryset =ReferralBonus.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
class ReferralBonusUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = ReferralBonusSerializer
    queryset =ReferralBonus.objects.all()
    permission_classes = [ReferralBonusTablePermissions]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"




@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
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
@authentication_classes([JWTAuthentication])
def check_first_order(request):
    
    orders  = Order.objects.filter(is_deleted=False, user=request.user)
    return Response({"has_order":orders.exists()}, status=200)
    
    
    
class UserAccountView(generics.ListCreateAPIView):
    serializer_class = UserBankAccountSerializer
    queryset = UserBankAccount.objects.filter(is_deleted=False).order_by("-date_added")
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request, *args, **kwargs):
        
        if UserBankAccount.objects.filter(is_deleted=False, user=request.user).exists():
            raise ValidationError(detail={"error":"bank already exists for this user"})
        
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        obj = serializer.save()
        
        obj.user = request.user
        obj.save()
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Added bank account"
            )
            
        return Response({"message":"created"}, status=201)
    
    
    
    def list(self, request, *args, **kwargs):
        

        try:
            bank = UserBankAccount.objects.get(user=request.user)
            data = UserBankAccountSerializer(bank).data
            return Response({"message":"created", "data":data}, status=201)
        
        except UserBankAccount.DoesNotExist:
            return Response({}, status=200)







class UserAccountUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserBankAccountSerializer
    queryset = UserBankAccount.objects.filter(is_deleted=False).order_by("-date_added")
    authentication_classes = [JWTAuthentication]
    permission_classes = [UserBankAccountTablePermissions]
    lookup_field = "id"

            

class WithdrawalView(generics.ListCreateAPIView):
    queryset = Withdrawal.objects.filter(is_deleted=False).order_by("-date_requested")
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        
        status = self.request.GET.get('status')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')
        
        
        if request.user.role != "admin":
            queryset = queryset.filter(user=request.user)
            
            
        if status:
            queryset = queryset.filter(status=status)
            
        
        if startDate and endDate:
            startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
            endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
            
            queryset = queryset.filter(date_requested__range=[startDate, endDate])
        
        
        return super().list(request, queryset=queryset, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        amount = serializer.validated_data.get("amount")

        if request.user.referral_bonus < 10000:
            raise ValidationError(detail={"error":"you can only withdraw when you have up to NGN10,000"})
    
        get_object_or_404(UserBankAccount, user=request.user)
        
        if amount > request.user.referral_bonus:
            raise ValidationError(detail={"error":"insufficient funds"})
        
        if request.user.withdrawal_set.filter(is_deleted=False, status="pending").exists():
            raise ValidationError(detail={"error":"You already have a pending withdrawal request"})
        
        
        obj = serializer.save()
        
        obj.user = request.user
        obj.save()
        
        ActivityLog.objects.create(
            user=request.user,
            action = f"Created withdrawal request"
            )
            
        return Response(serializer.data, status=201)
    

@api_view(["PATCH"])
@permission_classes([WithdrawalTablePermissions])
@authentication_classes([JWTAuthentication])
def confirm_withdrawal(request, token):
    if request.method == "PATCH":
        try:
            instance = Withdrawal.objects.get(hash_id=token, is_deleted=False)
        except Withdrawal.DoesNotExist:
            raise NotFound(detail={"error":"withdrawal request not found"})
        
        if instance.status == "completed":
            raise ValidationError({"detail": "this request has been approved before"})
        
        instance.status = "completed"
        instance.date_fulfilled = timezone.now()
        instance.save()
        
        instance.user.referral_bonus-=instance.amount
        instance.user.save()
        
        UserInbox.objects.create(user=instance.user, heading="Withdrawal Approved", body=f"Your request to withdraw NGN{instance.amount} has been approved.")
        
        return Response({"message":"success"}, status=202)