from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.forms import model_to_dict

from .managers import UserManager
import uuid
import random
from django.contrib.auth.models import Group as DjangoGroup


class User(AbstractBaseUser, PermissionsMixin):
    
    """
    Database schema for User model.

    Fields:
        - id (UUID): Unique identifier for the user.
        - first_name (str): First name of the user
        - last_name (str): Last name of the user
        - email (str): Email address of the user.
        - role (str): User type i.e admin, user, vendor.
        - favourite (Fk): Many to many relationship of user's favorite products
        - vendor_status (str): status of user who are vendors
        - image (img): profile picture of users
        - password (str): Password of the users
        - is_staff (bool): Field to mark an admin user as a super admin
        - is_admin (bool): Field to mark the  user as an admin
        - is_active (bool): Active status of the user
        - is_deleted (bool): Deleted status of the user
        - sent_vendor_email (bool): Helps to know if a vendor has been sent an email upon account status change to avoid multiple sending.
        - fcm_token (str): User's device firebase token for push notification
        - provider (str): Channel through which user signed up.
        - date_joined (datetime): Time at which the user signed up.
    """
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('vendor', 'Vendor'),
    )   
    
    VENDOR_STATUS = (
        ('applied', 'applied'),
        ('approved', 'approved'),
        ('unapproved', 'unapproved'),
        ('blocked', 'blocked'),
    )  
    
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+2341234567890'. Up to 15 digits allowed.")
    
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    first_name    = models.CharField(_('first name'),max_length = 250)
    last_name     = models.CharField(_('last name'),max_length = 250)
    role          = models.CharField(_('role'), max_length = 255, choices=ROLE_CHOICES)
    email         = models.EmailField(_('email'), unique=True)
    phone         = models.CharField(_('phone'), max_length = 100, null = True, validators=[phone_regex])
    favourite    = models.ManyToManyField("main.Product", blank=True)
    vendor_status = models.CharField(max_length=250, 
                                     blank=True, 
                                     null=True, 
                                     choices=VENDOR_STATUS)
    image = models.ImageField(
        upload_to='profile_photos/', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ], 
        blank=True, null=True)
    password      = models.CharField(_('password'), max_length=300)
    is_staff      = models.BooleanField(_('staff'), default=False)
    is_admin      = models.BooleanField(_('admin'), default= False)
    is_active     = models.BooleanField(_('active'), default=True)
    is_deleted    = models.BooleanField(_('deleted'), default=False)
    date_joined   = models.DateTimeField(_('date joined'), auto_now_add=True)
    sent_vendor_email = models.BooleanField(default=False)
    fcm_token = models.TextField(null=True)
    provider = models.CharField(_('provider'), max_length=255, default="email", choices=(('email',"email"),
                                                                                         ('google',"google")))
    
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['id','first_name', 'last_name', 'role', 'phone', ]
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.email} -- {self.role}"
    
    @property
    def module_access(self):
        """Fetches all the modules that an admin can view

        Returns:
            arr: List of all unique modules assigned to an admin's role type
        """
        unique_modules = ModuleAccess.objects.filter(group__user=self.id).distinct().values()
        
        return unique_modules
    
    @property
    def image_url(self):
        
        """See the image url of the user

        Returns:
            str: Image url of the  user or empty string if no image uploaded
        """
        
        if self.image:
            return self.image.url
        return ""
    
    def delete(self):
        
        """
        Performs soft delete on the user model
        Delete the user by flagging it as deleted and adding updating the email and phone with delete flags.
        """
        
        self.is_deleted = True
        self.email = f"{random.randint(0,100000)}-deleted-{self.email}"
        self.phone = f"{self.phone}-deleted-{random.randint(0,100000)}"
        self.save()
        
        return 
        
    def delete_permanently(self):
        
        """
        Performs hard delete on the user model.
        To be used with caution!
        """
        
        super().delete()
        
        return
        

    
    @property
    def store_profile(self):
        """
        Shows the store data of the user if the user type is "vendor"
        """
        
        if self.role == "vendor":
            profile = model_to_dict(self.store, exclude=["logo", "cac_doc", "is_deleted", "vendor" ])
            profile["id"] = self.store.id
            
            if bool(self.store.logo) != False:
                profile['logo_url'] = self.store.logo.url
            else:
                profile['logo_url'] = ""
            profile['cac_doc_url'] = self.store.cac_doc.url
            profile['date_joined'] = self.store.date_joined
            
            return profile    
        else:
            return None    
    
    
    @property
    def bank_detail(self):
        """
        Shows the bank data of the user if the user type is "vendor"
        """
        
        if self.role == "vendor":
            detail = model_to_dict(self.store.bank_detail, exclude=[ "is_deleted", "store" ])
            detail["id"] = self.store.id
            
            return detail    
        else:
            return None   
        
        
    class Meta:
        """additional permission to the  user model for viewing dashboards"""
        permissions = [
            ("view_dashboard", "Can view all dashboards"),
        ]
        
    
    
        
        
class ActivationOtp(models.Model):
    """
    Database schema for Activation Otp model.

    Fields:
        - id (int): Unique identifier for the OTP.
        - code (str): OTP for the user
        - user (FK): User attached to the  otp
        - expiry_date (datetime): Time at which the OTP expires.
    """

    user  =models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiry_date = models.DateTimeField()
    
    
    def is_valid(self):
        """Checks if the OTP has expires or not

        Returns:
            bool: Result of OTP check.
        """
        
        return bool(self.expiry_date > timezone.now())




class StoreProfile(models.Model):
    """
    Database schema for Store Profile model.

    Fields:
        - id (UUID): Unique identifier for the user.
        - first_name (str): First name of the user
        - last_name (str): Last name of the user
        - email (str): Email address of the user.
        - role (str): User type i.e admin, user, vendor.
        - favourite (Fk): Many to many relationship of user's favorite products
        - vendor_status (str): status of user who are vendors
        - image (img): profile picture of users
        - password (str): Password of the users
        - is_staff (bool): Field to mark an admin user as a super admin
        - is_admin (bool): Field to mark the  user as an admin
        - is_active (bool): Active status of the user
        - is_deleted (bool): Deleted status of the user
        - sent_vendor_email (bool): Helps to know if a vendor has been sent an email upon account status change to avoid multiple sending.
        - fcm_token (str): User's device firebase token for push notification
        - provider (str): Channel through which user signed up.
        - date_joined (datetime): Time at which the user signed up.
    """
    
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    vendor = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name="store", null=True)
    store_name = models.CharField(max_length=250, unique=True)
    logo = models.ImageField(blank=True, upload_to='store_logos', 
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['png', "jpg", "jpeg"])])
    store_desc= models.TextField()
    num_of_employee = models.PositiveIntegerField()
    state = models.CharField(max_length=100)
    line_1 = models.TextField()
    line_2 = models.TextField(blank=True, null=True)
    zip_code = models.CharField(max_length=50)
    cac_num  = models.CharField(max_length=50)
    cac_doc = models.FileField(upload_to='cac_documents', validators=[
        FileExtensionValidator(allowed_extensions=['pdf','doc', "jpg", "jpeg"])])
    is_deleted    = models.BooleanField( default=False)
    date_joined   = models.DateTimeField(auto_now_add=True)
    
    
    
    def __str__(self):
        return f"{self.store_name} for {self.vendor}"
    
    
    @property
    def logo_url(self):
        if self.logo:
            return self.logo.url
        return ""
    
    @property
    def cac_doc_url(self):
        return self.cac_doc.url
    
    @property
    def bank_data(self):
        detail = model_to_dict(self.bank_detail, exclude=[ "is_deleted", "store" ])
        detail["id"] = self.bank_detail.id
            
        return detail    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
        
        
class StoreBankDetail(models.Model):
    """
    Database schema for Store Profile model.

    Fields:
        - id (UUID): Unique identifier for the bank detail.
        - account_name (str): Name of the store account
        - account_num (str): Sterling bank account number of the vendor's store
        - phone (str): phone number associated with the account
        - store (FK): Foreign key relationship to the store
        - is_deleted (bool): Deleted status of the bank detail
        - date_joined (datetime): Time at which the bank data was added
    """
    
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    account_name = models.CharField(max_length=300)
    account_num = models.CharField(max_length=12,
                                   validators=[ MinLengthValidator(10, 'the field must contain at least 10 characters')
                                               ])
    phone = models.CharField(max_length=15, 
                             validators=[ MinLengthValidator(10, 'the field must contain at least 12 characters')
                                         ])
    bank_branch = models.CharField(max_length=300)
    store = models.OneToOneField("accounts.StoreProfile", on_delete=models.CASCADE, related_name="bank_detail", null=True)
    is_deleted    = models.BooleanField(_('deleted'), default=False)
    date_joined   = models.DateTimeField(_('date joined'), auto_now_add=True)
    
    
    
    def __str__(self):
        return f"Account Details for {self.store}"
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
        
    
class ModuleAccess(models.Model):
    """
    Database schema for modules available on the frontend.

    Fields:
        - url (str): frontend relative path 
        - name (str): name of the module (menu) on the admin site
        
    N/B: This is a set field and cannot be altered except new modules are created on the FE, 
    then the developer can add them on the DB.
    This table is used for permissions
    """
    
    url = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    
    
    def __str__(self):
        return self.name

DjangoGroup.add_to_class('module_access', models.ManyToManyField(ModuleAccess,  blank=True))


class ActivityLog(models.Model):
    """
    Database schema for user activity logs.

    Fields:
        - user (FK): User that the log belongs to
        - action (str): action performed by user
        - date_created (timestamp): date the log was created
        - is_deleted (bool): flags the log as deleted
    
    """
    
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
        
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} {self.action}"
    
    
    
class TempStorage(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    json_data  = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.user.email}"
    