import random
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from config import settings

from .models import ActivationOtp
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string




