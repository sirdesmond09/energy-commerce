
from .models import ReferrerReward, ReferralBonus
from main.models import Order, OrderItem

def record_reward(referrer, order:Order):
    
    """When the first order is payed for, this function is called to record the user's bonus for that order item"""
    
    percent = ReferralBonus.objects.get(owner="referrer")
    
    ReferrerReward.objects.create(
        referrer=referrer,
        order =order,
        percent = percent.percent
    )
    
    return
    
    

def update_wallet(order_item:OrderItem, referrer):
    
    """When order is flagged as intransit, this function is called to actually give the user their bonus for that order item"""
    
    try:
        referral = ReferrerReward.objects.get(
            referrer=referrer,
            order =order_item.order
        )
        
        amount = order_item.unit_price * (referral.percent/100)
        
        referrer.referral_bonus += amount
        referrer.save()
        return
    
    except Exception as e:
        return
    
    
     
    
    
    
    
    