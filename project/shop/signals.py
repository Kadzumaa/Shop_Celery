from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from tasks import create_product

from .models import Product


@receiver(sender=Product)
def signal_product_cr(instance, sender, **kwargs):
    if kwargs['action'] == 'product_add':
        subscribers_emails = []

        for category in instance.Post.all():
            subscribers_emails += User.objects.values_list('email', flat=True)
        create_product.delay(instance.id)

