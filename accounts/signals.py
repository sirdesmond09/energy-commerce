import random
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from accounts.helpers.generators import generate_referral_code
from config import settings
from djoser.signals import user_registered, user_activated

from .models import ActivationOtp, TempStorage, StoreProfile
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
import os
import  requests
from main.helpers.signals import password_changed, post_store_delete, vendor_created
from main.helpers.encryption import password_encryptor


User = get_user_model()
site_name = "Imperium"
MARKET_PLACE_URL = settings.Common.MARKETPLACE_URL
energy_url=os.getenv("ENERGY_BASE_URL")


def generate_otp(n):
    return "".join([str(random.choice(range(10))) for _ in range(n)])


@receiver(post_save, sender=User)
def send_details(sender, instance, created, **kwargs):
    if (created and instance.is_superuser!=True) and instance.is_admin==True:

        password = instance.password
        
        instance.set_password(password)
        instance.save()
        # print(instance.password)
        subject = f"YOUR ADMIN ACCOUNT FOR {site_name}".upper()
        
        message = f"""Hi, {str(instance.first_name).title()}.
You have just been on boarded on the {site_name} platform. Your login details are below:
E-mail: {instance.email} 
password: {password}    


Please login via: https://imperiumadmin-getmobile.sterlingapps.p.azurewebsites.net

Regards,
{site_name} Support Team   
"""   
        # msg_html = render_to_string('signup_email.html', {
        #                 'first_name': str(instance.first_name).title(),
        #                 'code':code,
        #                 'url':url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        send_mail( subject, message, email_from, recipient_list)
        
        return
    
    


@receiver(post_save, sender=User)
def temporarily_store(sender, instance, created, *args, **kwargs):

    if created and instance.role=="user":

        data = instance.__dict__.copy()

        data.pop('_state')
        data['id'] = str(instance.id)
        data['image'] = None
        data['date_joined']  =  instance.date_joined.isoformat()
        data['_password'] = password_encryptor.encrypt(data.get('_password'))
        json_data=json.dumps(data)
        TempStorage.objects.create(
            json_data=json_data,
            user=instance
            )

            
@receiver(user_registered)
def activate_otp(user, request, *args,**kwargs):
    
    if user.role == "user":
        user.is_active = False
        user.referral_code = generate_referral_code()
        user.save()
        
        code = generate_otp(6)
        expiry_date = timezone.now() + timezone.timedelta(minutes=10)
        ActivationOtp.objects.create(code=code, expiry_date=expiry_date, user=user)
        
        
        subject = f"ACCOUNT VERIFICATION FOR {site_name}".upper()
            
        message = f"""Hi, {str(user.first_name).title()}.
    Thank you for signing up!
    Complete your verification on the {site_name} with the OTP below:

                    {code}        

    Expires in 5 minutes!

    Cheers,
    {site_name} Team            
    """   
        msg_html = render_to_string('email/activation.html', {
                        'first_name': str(user.first_name),
                        'code':code,
                        'site_name':site_name,
                        "MARKET_PLACE_URL":MARKET_PLACE_URL})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        return


def send_data(user):
    temp_data  =  TempStorage.objects.get(user=user)
    data  =  json.loads(temp_data.json_data)

    payload = {
        "email": data.get('email'),
        "password": password_encryptor.decrypt(data.get('_password')),
        "first_name": data.get('first_name'),
        "last_name": data.get('last_name'),
        "phone": data.get('phone')
    }
    
    # print(payload)
    
    res = requests.post(f"{energy_url}/auth/post-user",
                    data=payload,)
    
    temp_data.delete()
    
    print(res.content)

    return payload

@receiver(user_activated)
def comfirmaion_email(user, request, *args,**kwargs):
    
    if user.role == "user":
        subject = "VERIFICATION COMPLETE"
            
        message = f"""Hi, {str(user.first_name).title()}.
    Your account has been activated and is ready to use!

    Cheers,
    {site_name} Team            
    """   
        msg_html = render_to_string('email/confirmation.html', {
                        'first_name': str(user.first_name).title(),
                        'site_name':site_name,
                        "MARKET_PLACE_URL":MARKET_PLACE_URL})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        
        send_data(user=user)
        

        return
        
        
        

@receiver(post_save, sender=User)
def send_approved_mail(sender, instance, created, **kwargs):
    if (instance.role =="vendor" and instance.vendor_status=="approved") and instance.sent_vendor_email is False:
        # print(instance.password)
        subject = "You can now sell on imperium"
            
        message = f"""Hi, {str(instance.first_name).title()}.
    Your vendor account has been approved and is ready to use!

    Cheers,
    {site_name} Team            
    """   
        msg_html = render_to_string('email/vendor_confirm.html', {
                        'first_name': str(instance.first_name).title(),
                        'site_name':site_name,
                        "MARKET_PLACE_URL":MARKET_PLACE_URL})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        instance.sent_vendor_email =True
        instance.save()
                
        return


@receiver(vendor_created)
def send_applied_mail(sender, vendor, **kwargs):

        subject = "Your Imperium Vendor Application Has Been Received"
            
        message = f"""Hi, {str(vendor.first_name).title()}.
    Your vendor account application has been received!

    Cheers,
    {site_name} Team            
    """   
        msg_html = render_to_string('email/vendor.html', {
                        'first_name': str(vendor.first_name).title(),
                        'site_name':site_name,
                        "MARKET_PLACE_URL":MARKET_PLACE_URL})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [vendor.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
                
        return
    
    
    
@receiver(post_save, sender=User)
def send_blocked_mail(sender, instance, created, **kwargs):
    if (instance.role =="vendor" and instance.vendor_status=="blocked") and instance.sent_vendor_email is False:
        # print(instance.password)
        subject = "Oops! Something went wrong with your account"
            
        message = f"""Hi, {str(instance.first_name).title()}.
Your vendor account was not approved on imperium. Please contact the administrator on our contact us page.

Cheers,
{site_name} Team            
    """   
        msg_html = render_to_string('email/vendor_decline.html', {
                        'first_name': str(instance.first_name).title(),
                        'site_name':site_name,
                        "MARKET_PLACE_URL":MARKET_PLACE_URL})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        instance.sent_vendor_email =True
        instance.save()
                
        return
    
    

@receiver(post_save, sender=User)
def update_energy_analytics(sender, instance, created, **kwargs):
    if not created and instance.role=="user":
        
        data  =  instance.__dict__

        payload = {
            "email": data.get('email'),
            "first_name": data.get('first_name'),
            "last_name": data.get('last_name'),
            "phone": data.get('phone')
        }
        
        res = requests.patch(f"{energy_url}/auth/update-user",
                        data=payload,)
        
        print(res.status_code)

        return payload



@receiver(password_changed)
def update_energy_analytics(sender, user_data, **kwargs):

    if user_data.get("role")=="user":
        


        payload = {
            "email": user_data.get('email'),
            "first_name": user_data.get('first_name'),
            "last_name": user_data.get('last_name'),
            "phone": user_data.get('phone'),
            "password":user_data.get("password")
        }
        
        res = requests.patch(f"{energy_url}/auth/update-user",
                        data=payload,)
        


        return payload
                    


@receiver(post_store_delete)
def delete_products(sender, vendor, **kwargs):
    #when a store or vendor is deleted, get all the products belonging to that entity and flag as deleted
        
    vendor.products.filter(is_deleted=False).update(is_deleted=True)
    
                    
