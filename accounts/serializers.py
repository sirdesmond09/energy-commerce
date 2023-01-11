from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.signals import user_activated
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import ActivationOtp, StoreBankDetail, StoreProfile
from .signals import generate_otp, site_name,url
from rest_framework.exceptions import ValidationError

from config import settings
 
User = get_user_model()

        

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ['id',"first_name", "last_name", "email", "role","phone", "password", "is_active"]
        
    
   

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=300, required=False)
    
    class Meta():
        model = User
        fields = ['id',"first_name", "last_name", "email", "phone", "password", "is_active", "role"]
        extra_kwargs = {
            'password': {'write_only': True}
        }
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=300)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=700)
    

class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    
    
    def verify_otp(self, request):
        otp = self.validated_data['otp']
        
        if ActivationOtp.objects.filter(code=otp).exists():
            try:
                otp = ActivationOtp.objects.get(code=otp)
            except Exception:
                ActivationOtp.objects.filter(code=otp).delete()
                raise serializers.ValidationError(detail='Cannot verify otp. Please try later')
            
            if otp.is_valid():
                if otp.user.is_active == False:
                    otp.user.is_active=True
                    otp.user.save()
                    
                    #clear all otp for this user after verification
                    all_otps = ActivationOtp.objects.filter(user=otp.user)
                    all_otps.delete()
                    user_activated.send(User, user=otp.user, request=request)
                    return {'message': 'Verification Complete'}
                else:
                    raise serializers.ValidationError(detail='User with this otp has been verified before.')
            
                
            else:
                raise serializers.ValidationError(detail='OTP expired')
                    
        
        else:
            raise serializers.ValidationError(detail='Invalid OTP')
    

class NewOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
     
    def get_new_otp(self):
        try:
            user = User.objects.get(email=self.validated_data['email'], is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='Please confirm that the email is correct and has not been verified')
        
        code = generate_otp(6)
        expiry_date = timezone.now() + timezone.timedelta(minutes=10)
        
        ActivationOtp.objects.create(code=code, user=user, expiry_date=expiry_date)
        subject = f"NEW OTP FOR {site_name}"
        
        message = f"""Hi, {str(user.first_name).title()}.

    Complete your verification on {site_name} with the OTP below:

                    {code}        

    Expires in 5 minutes!

    Thank you,
    SmartParcel                
    """
        msg_html = render_to_string('email/new_otp.html', {
                        'first_name': str(user.first_name).title(),
                        'code':code,
                        'url':url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        return {'message': 'Please check your email for OTP.'}
    
    


        
class StoreProfileSerializer(serializers.ModelSerializer):
    logo_url = serializers.ReadOnlyField()
    cac_doc_url = serializers.ReadOnlyField()
    
    class Meta:
        fields = '__all__'
        model = StoreProfile
        extra_kwargs = {
            'logo': {'write_only': True},
            'cac_doc': {'write_only': True}
        }


class BankDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = StoreBankDetail
        
        
        
class AddVendorSerializer(serializers.Serializer):
    vendor_data = CustomUserSerializer()
    store_profile = StoreProfileSerializer()
    bank_detail = BankDetailSerializer()
    
    
    def create(self, validated_data):
        
        store_profile = validated_data.pop('store_profile')
        bank_detail = validated_data.pop('bank_detail')
        vendor_data = validated_data.pop('vendor_data')
        
        if "role" in vendor_data.keys():
            vendor_data.pop("role") 
            
        vendor = User.objects.create(**vendor_data, role="vendor")
        print(vendor)
        
        try:
        
            if "vendor" in store_profile.keys():
                store_profile.pop("vendor")
                
            store = StoreProfile.objects.create(**store_profile, vendor=vendor)
        except Exception as e:
            print("error")
            vendor.delete_permanently()
            raise ValidationError(str(e))
        
        try:
            if "store" in bank_detail.keys():
                bank_detail.pop("store")
                
            StoreBankDetail.objects.create(**bank_detail, store=store)
        except Exception as e:
            print("another errror")
            store.delete_permanently()
            raise ValidationError(str(e))
        return 