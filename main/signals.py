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
from firebase_admin import messaging




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
    



@receiver(post_save, sender=UserInbox)
def send_notification(sender, instance:UserInbox, created, *args,**kwargs):
    
    if created:
        user = instance.user
        
        if user.fcm_token:
        
            notification = messaging.Notification(title=instance.heading, body=instance.body, image=instance.image_url)
            messaging.send(messaging.Message(notification=notification, token=user.fcm_token))
        
        
        return