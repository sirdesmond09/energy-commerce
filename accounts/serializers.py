from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.signals import user_activated
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import ActivationOtp, ModuleAccess, StoreBankDetail, StoreProfile
from .signals import generate_otp, site_name,url
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import Permission, Group

from config import settings
 
User = get_user_model()

        

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ['id',"first_name", "last_name", "email", "role","phone", "password", "is_active"]
        
    
class UserDeleteSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"})

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True, required=False)
    store_profile = serializers.ReadOnlyField()
    bank_detail = serializers.ReadOnlyField()
    favourite_detail = serializers.ReadOnlyField()
    vendor_rating = serializers.SerializerMethodField()
    
    class Meta():
        model = User
        fields = ['id',"first_name", "last_name", "email", "phone", "password", "is_active", "role", "bank_detail", "store_profile", "favourite_detail", "groups", "user_permissions", "vendor_rating", "vendor_status", "date_joined"]
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
        
    def get_vendor_rating(self, vendor):
        
        if vendor.role == "vendor":
        
            products = vendor.products.filter(is_deleted=False)
            
            if len(products) > 0:
                non_zero = list(filter(lambda x: x.rating != 0, products))
                ratings =  list(map(lambda product : product.rating, non_zero))

                return round(sum(ratings)/len(ratings), 2)

            return 0
        
        return 

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=300)
    
    
class FirebaseSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length=5000)


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
    Imperium                
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
    bank_data = serializers.ReadOnlyField()
    vendor_data = serializers.SerializerMethodField()
    
    class Meta:
        fields = '__all__'
        model = StoreProfile
        extra_kwargs = {
            'logo': {'write_only': True},
            'cac_doc': {'write_only': True}
        }
        

    def get_vendor_data(self, obj):
        data = CustomUserSerializer(obj.vendor).data
        data.pop("user_permissions")
        data.pop("store_profile")
        data.pop("bank_details")
        data.pop("groups")
        
        return data
    
    
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
            
        vendor = User.objects.create(**vendor_data, role="vendor", vendor_status="applied")
        
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
    
    
class PermissionSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = "__all__"
        model = Permission

class ModuleAccessSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = "__all__"
        model = ModuleAccess


class GroupSerializer(serializers.ModelSerializer):
    module_access_data = serializers.SerializerMethodField()
    permissions_data = serializers.SerializerMethodField()
    
    class Meta:
        fields = "__all__"
        model = Group
        
        
    def get_module_access_data(self, obj):
        return ModuleAccessSerializer(obj.module_access, many=True).data
    
    def get_permissions_data(self, obj):
        return PermissionSerializer(obj.permissions, many=True).data
        
        
    
class VendorStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=200)
    
    
    def validate_status(self, value):
        if value not in ('approved','unapproved','blocked'):
            raise ValidationError(detail={"message": "status must be either ('approved','unapproved','blocked')" })
        
        
class AssignRoleSerializer(serializers.Serializer):
    roles = serializers.ListField()
    
    
    def __to_int(self, obj):
        return list(map(int, obj))
    
    def validate_roles(self, data):
        data = self.__to_int(data)
        group_ids = set(data)
        groups = Group.objects.filter(id__in=group_ids)
        roles = list(groups)

        if len(roles) != len(group_ids):
            missing_ids = group_ids - set(g.id for g in roles)
            raise ValidationError(detail={"message": f"roles with ids {missing_ids} not found"})
        
        return [role.id for role in roles]