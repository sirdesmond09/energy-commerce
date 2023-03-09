import random
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save, post_delete
from config import settings
from accounts.models import ActivityLog
from .models import *
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string




@receiver(post_save, sender=Product)
def log_product_actions(sender, instance:Product, created, **kwargs):
    
    if created:
        ActivityLog.objects.create(
            user=instance.vendor,
            action = f"Listed new product"
        )
        
        return
    
    ActivityLog.objects.create(
            user=instance.vendor,
            action = f"Edited a product"
        )
    
    
@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance:Product, created, **kwargs):

    ActivityLog.objects.create(
            user=instance.vendor,
            action = f"Deleted a product"
    )


    
    
@receiver(post_delete, sender=Cart)
def log_delete_delete(sender, instance:Product, created, **kwargs):

    ActivityLog.objects.create(
            user=instance.user,
            action = f"Deleted an item in cart"
    )
    



@receiver(post_save, sender=ValidationOTP)
def verification_otp(sender, instance:ValidationOTP, created, *args,**kwargs):
    
    if created:
        
        item = instance.order_item
        user = item.order.user
        item:OrderItem
        
        subject = f"OTP to validate your order"
            
        message = f"""Hi, {str(user.first_name).title()}.
    Your order is on the way.
    
    Complete your verification with the OTP below:

                    {instance.code}        

    Expires in 5 minutes!

    Cheers,
    Imperium Team            
    """   
        msg_html = render_to_string('email/verification_otp.html', {
                        'first_name': str(user.first_name).title(),
                        'code':instance.code,
                        'site_name':"Imperium",
                        "url":"imperium.com.ng",
                        "order_id" : item.unique_id})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        return