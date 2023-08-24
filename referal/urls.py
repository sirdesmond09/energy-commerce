from django.urls import path
from . import views


urlpatterns = [
    path("referral-bonus/", views.ReferralBonusList.as_view()),
    path("referral-bonus/<int:id>/", views.ReferralBonusUpdate.as_view()),
    path("referral-bonus/check-orders/", views.check_first_order),
    path("referral-bonus/data/", views.referral_data),
    path("banks/user-account/", views.UserAccountView.as_view()),
    path("banks/user-account/<int:id>/update/", views.UserAccountUpdateView.as_view()),
    path('withdrawals/',views.WithdrawalView.as_view()),
    path('withdrawals/<str:token>/approve/',views.confirm_withdrawal),
    
    
]
