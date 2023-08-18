from django.db import models
from django.contrib.auth import get_user_model


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

    

        
