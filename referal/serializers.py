from rest_framework import serializers
from .models import ReferralBonus, UserBankAccount, Withdrawal
from django.forms import model_to_dict

class ReferralBonusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReferralBonus
        fields = "__all__"
        
        
class UserBankAccountSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model=UserBankAccount
        fields = "__all__"
        
    def get_user_info(self, obj):
        return model_to_dict(obj.user, fields=['id', 'first_name', 'last_name', 'email', 'phone'])
    
    

class WithdrawalSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        fields = "__all__"
        model = Withdrawal
        
    
    def get_user_info(self, obj):
        return model_to_dict(obj.user, fields=['id', 'first_name', 'last_name', 'email', 'phone'])
    