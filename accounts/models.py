from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from django_rest_passwordreset.signals import reset_password_token_created, post_password_reset
from accounts.managers import CustomUserManager
from celery import shared_task
from predict.settings import DEFAULT_FROM_EMAIL


class User(AbstractUser):

    """User Model"""
    username = models.CharField(blank=True, null=True, max_length=100)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username",]

    def __str__(self):
        return self.email

    # def unique_username(self):
    #     if not username:
    #         self.username = 


class UserProfile(models.Model):

    """User Profile Model"""
    user = models.OneToOneField("accounts.User", related_name="profiles", on_delete=models.CASCADE)
    # image = models.ImageField(
    #     upload_to='images/user/%Y/%m/', blank=True, null=True, related_name="profile_photo")

    def __str__(self):
        return self.user.first_name

def send_email_notification(sender, subject, body, plaintext_message=None, to=None):

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plaintext_message,
            from_email=sender,
            to=to
        )
        msg.attach_alternative(body, 'text/html')
        return msg.send(fail_silently=False)
    except:
        return {'detail': 'Email notification not sent'}

@shared_task
def _send_email(*args, **kwargs):
    send_email_notification(*args, **kwargs)

def send_email(*args, **kwargs):
    _send_email(*args, **kwargs)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    '''Send link to reset user's Password'''
    # send email to the user
    context = {
        'first_name': reset_password_token.user.first_name,
        'email': reset_password_token.user.email,
        'reset_password_url': f"?token={reset_password_token.key}"
    }

    # render email text
    email_sender = DEFAULT_FROM_EMAIL
    email_subject = 'Password Reset'
    email_body = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    send_email(
        email_sender, email_subject, email_body, email_plaintext_message,
        to=[reset_password_token.user.email]
    )
