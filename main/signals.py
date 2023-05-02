import random
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save, post_delete
from accounts.signals import MARKET_PLACE_URL, site_name
from config import settings
from accounts.models import ActivityLog
from .models import *
import json
from firebase_admin import messaging
import os
import requests
from .helpers.signals import payment_approved
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
    



@receiver(post_save, sender=UserInbox)
def send_notification(sender, instance:UserInbox, created, *args,**kwargs):
    
    if created:        
        if instance.user.fcm_token:
        
            notification = messaging.Notification(title=instance.heading, body=instance.body, image=instance.image_url)
            messaging.send(messaging.Message(notification=notification, token=instance.user.fcm_token))
        
        return


def send_message(token):
    notification = messaging.Notification(title="New Product", body="A new product is here! Check it out.", image="https://res.cloudinary.com/univel/image/upload/v1/media/products/primary_imgs/Placeholder-18_gdbubg")
    messaging.send(messaging.Message(notification=notification, token=token))



@receiver(post_save, sender=SupportTicket)
def send_notification(sender, instance:SupportTicket, created, *args,**kwargs):
    
    url = os.getenv("CRM_URL")
    data = json.dumps({"CaseMinorCategory": instance.case_minor.name if instance.case_minor else "",
            "CaseSubCategory": instance.sub_category.name,
            "CaseType": instance.case_type.name,
            "Description": instance.desc,
            "Email": instance.email,
            "FirstName": instance.first_name,
            "Phone": instance.phone,
            "Surname": instance.last_name
        })
    res = requests.post(
        url=url,
        data = data ,
        headers = {'Content-type': 'application/json'}
    )
    
    if res.status_code == 200:
        body = res.json().get("ResponseText")
        instance.crm_id = body.split()[1]
        instance.save()
        
    
    print(data)
    print(res.status_code)
    print(res.content)
    
    
    

@receiver(payment_approved)
def send_invoice(sender, payment, user, **kwargs):
    
    subject = "Imperium Payment Invoice"
            
    message = ""
    msg_html = render_to_string('email/invoice.html', {
                    'first_name': str(user.first_name).title(),
                    'site_name':site_name,
                    "MARKET_PLACE_URL":MARKET_PLACE_URL,
                    "order_items":sender.items.filter(is_deleted=False)})
    
    email_from = settings.Common.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
    
            
    return 
        