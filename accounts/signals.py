import random
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from config import settings
from djoser.signals import user_registered, user_activated

from .models import ActivationOtp, TempStorage
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
import os
import  requests


User = get_user_model()
site_name = "Imperium"
url="https://imperium-market-place.vercel.app/"
energy_url=os.getenv("ENERGY_BASE_URL")
# energy_url="https://www.imperiumdev.wyreng.com"

def generate_otp(n):
    return "".join([str(random.choice(range(10))) for _ in range(n)])


@receiver(post_save, sender=User)
def send_details(sender, instance, created, **kwargs):
    if (created and instance.is_superuser!=True) and instance.is_admin==True:
        data =  instance.__dict__
        # print(instance.password)
        subject = f"YOUR ADMIN ACCOUNT FOR {site_name}".upper()
        
        message = f"""Hi, {str(instance.first_name).title()}.
You have just been onboarded on the {site_name} platform. Your login details are below:
E-mail: {data.get('email')} 
password: {data.get('_password')}    

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
        print(data)
        data.pop('_state')
        data['id'] = str(instance.id)
        data['image'] = None
        data['date_joined']  =  instance.date_joined.isoformat()
        data['_password'] = data.get('_password')[::-1]
        json_data=json.dumps(data)
        TempStorage.objects.create(
            json_data=json_data,
            user=instance
            )

            
@receiver(user_registered)
def activate_otp(user, request, *args,**kwargs):
    
    if user.role == "user":
        user.is_active = False
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
                        'first_name': user,
                        'code':code,
                        'site_name':site_name,
                        "url":url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        return


def send_data(user):
    temp_data  =  TempStorage.objects.get(user=user)
    data  =  json.loads(temp_data.json_data)

    payload = {
        "email": data.get('email'),
        "password": data.get('_password')[::-1],
        "first_name": data.get('first_name'),
        "last_name": data.get('last_name'),
        "phone": data.get('phone')
    }
    
    # print(payload)
    
    requests.post(f"{energy_url}/auth/post-user",
                    data=payload,)
    temp_data.delete()
    

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
                        'user': str(user.first_name).title(),
                        'site_name':site_name,
                        "url":url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        
        send_data(user=user)
        

        return
        
        
        

@receiver(post_save, sender=User)
def send_vendor_details(sender, instance, created, **kwargs):
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
                        "url":url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        instance.sent_vendor_email =True
        instance.save()
                
        return
    
    
    
@receiver(post_save, sender=User)
def send_vendor_details(sender, instance, created, **kwargs):
    if (instance.role =="vendor" and instance.vendor_status=="unapproved") and instance.sent_vendor_email is False:
        # print(instance.password)
        subject = "Oops! Something went wrong with your account"
            
        message = f"""Hi, {str(instance.first_name).title()}.
Your vendor account was not approved on imperium. Please contact the administrator on our contact us page.

Cheers,
{site_name} Team            
    """   
        # msg_html = render_to_string('email/vendor_confirm.html', {
        #                 'first_name': str(instance.first_name).title(),
        #                 'site_name':site_name,
        #                 "url":url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        send_mail( subject, message, email_from, recipient_list)
        
        instance.sent_vendor_email =True
        instance.save()
                
        return