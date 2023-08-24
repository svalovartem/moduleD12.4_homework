from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.core.mail import get_connection, EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import datetime


@receiver(post_save, sender=Post)
def subscribers_mails(sender, instance, **kwargs):
    conns = PostCategory.objects.filter(post_connect_id=instance.id).values_list('category_connect_id')
    catid = ''.join(str(*x) for x in conns)
    mails = list()
    for i in catid:
        subs = Category.objects.get(id=i).subscribers.all()
        for sub in subs:
            html_content = render_to_string(
                'email-subcats.html', {'category': Category.objects.get(id=i),
                                       'news_title': instance.news_title,
                                       'news_text': instance.news_text,
                                       'pk': instance.id})
            text_message = f'Здравствуй, {sub.username}. Новая статья в твоём любимом разделе!'
            mail = sub.email
            msg = EmailMultiAlternatives(
                subject=instance.news_title,
                body=text_message,
                from_email='ShinyBlackArrow@yandex.ru',
                to=[mail],
            )
            msg.attach_alternative(text_message + html_content, "text/html")
            mails.append(msg)

    get_connection().send_messages(mails)


@receiver(post_save, sender=User)
def hello_mail(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Welcome to NewsPaper',
            f'Hello, {instance.username}. You have successfully registered on NewsPaper. Welcome on board!',
            'ShinyBlackArrow@yandex.ru',
            [f'{instance.email}'],
            fail_silently=False,
        )
