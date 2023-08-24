from django.db import models
from django.contrib.auth import get_user_model
from django_hashids import HashidsField

User=  get_user_model()
# Create your models here.


class ReferralBonus(models.Model):
    OWNER_CHOICES = (("referred", "referred"),
                     ("referrer", "referrer"))
    
    percent = models.FloatField(default=0)
    owner = models.CharField(max_length=50, choices=OWNER_CHOICES)
    
    
    def __str__(self):
        return f"{self.percent} bonus for {self.owner}"
    
    

class ReferrerReward(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey("main.Order", on_delete=models.CASCADE)
    percent = models.FloatField() #percent at the time calculation was made

    

        
class UserBankAccount(models.Model):
    account_name = models.CharField(max_length=255)
    account_num = models.CharField(max_length=255)
    bank_code = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()



class Withdrawal(models.Model):
    STATUS_CHOICES = (("pending", "pending"),
                      ("completed", "completed"))
    
    
    hash_id = HashidsField(real_field_name="id", min_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    amount = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    date_fulfilled = models.DateTimeField(null=True)
    date_requested = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()