import datetime
from celery import shared_task
import time

from django.core.mail import EmailMultiAlternatives
from .models import Product


@shared_task
def printer(N):
    for i in range(N):
        time.sleep(1)
        print(i+1)


@shared_task
def create_product(id):
    instance = Product.objects.get(id=id)
    subscribers_emails = []
    subject = f'Создан новый пост {instance.id}'

    ext_content = (
        f'Статья: {instance.name}\n'
        f'Текст: {instance.description}\n\n'
        f'Ссылка на пост: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )

    html_content = (
        f'Товар: {instance.name}<br>'
        f'Цена: {instance.price}<br><br>'
        f'<a href="http://127.0.0.1{instance.get_absolute_url()}">'
        f'Ссылка на пост</a>'
    )

    msg = EmailMultiAlternatives(subject, text_content, None)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
