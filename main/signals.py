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
from .helpers.signals import payment_approved, payment_declined, order_canceled, cancel_approved, cancel_rejected
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
        if instance.user.fcm_token is not None:
        
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
def send_invoice(sender, user, **kwargs):
    
    subject = "Imperium Payment Invoice"
            
    message = ""
    msg_html = render_to_string('email/invoice.html', {
                    'first_name': str(user.first_name).title(),
                    'site_name':site_name,
                    "MARKET_PLACE_URL":MARKET_PLACE_URL,
                    "order_items":sender.items.filter(is_deleted=False),
                    "order":sender})
    
    email_from = settings.Common.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
    
            
    return 



@receiver(payment_declined)
def send_decline_notice(sender, user, **kwargs):
    
    subject = "Your Loan Request was Declined"
            
    message = ""
    msg_html = render_to_string('email/declined.html', {
                    'first_name': str(user.first_name).title(),
                    'site_name':site_name,
                    "MARKET_PLACE_URL":MARKET_PLACE_URL,
                    "order":sender})
    
    email_from = settings.Common.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
    
            
    return 


@receiver(order_canceled)
def send_canceled_notice(sender, order_item, **kwargs):
    
    subject = "Update on your Imperium Order"
            
    message = ""
    order = order_item.order
    user = order.user
    msg_html = render_to_string('email/canceled.html', {
                    'first_name': str(user.first_name).title(),
                    'site_name':site_name,
                    "MARKET_PLACE_URL":MARKET_PLACE_URL,
                    "reason":order_item.cancellation_response_reason,
                    "order_id":order_item.unique_id,
                    "order":order})
    
    email_from = settings.Common.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
    
            
    return 


@receiver(cancel_approved)
def send_cancel_approved_notice(sender, order_item, **kwargs):
    
    subject = "Your Cancel Request was Approved"
            
    message = ""
    order = order_item.order
    user = order.user
    msg_html = render_to_string('email/cancel_accepted.html', {
                    'first_name': str(user.first_name).title(),
                    'site_name':site_name,
                    "MARKET_PLACE_URL":MARKET_PLACE_URL,
                    "reason":order_item.cancellation_response_reason,
                    "order_id":order_item.unique_id,
                    "order":order})
    
    email_from = settings.Common.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
    
            
    return 


@receiver(cancel_rejected)
def send_cancel_rejected_notice(sender, order_item, **kwargs):
    
    subject = "Your Cancel Request was Declined"
            
    message = ""
    order = order_item.order
    user = order.user
    msg_html = render_to_string('email/cancel_rejected.html', {
                    'first_name': str(user.first_name).title(),
                    'site_name':site_name,
                    "MARKET_PLACE_URL":MARKET_PLACE_URL,
                    "reason":order_item.cancellation_response_reason,
                    "order_id":order_item.unique_id,
                    "order":order})
    
    email_from = settings.Common.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
    
            
    return 




@receiver(post_save, sender=ValidationOTP)
def send_delivery_code(sender, instance, **kwargs):
    
    subject = "Imperium Delivery Code"
            
    message = ""
    
    order = instance.order_item.order
    msg_html = render_to_string('email/verification_otp.html', {
                    'first_name': str(order.user.first_name).title(),
                    'site_name':site_name,
                    "MARKET_PLACE_URL":MARKET_PLACE_URL,
                    "code":instance.code,
                    "order_id":instance.order_item.unique_id})
    
    email_from = settings.Common.DEFAULT_FROM_EMAIL
    recipient_list = [order.user.email]
    send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
    
            
    return 
        