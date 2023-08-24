import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from datetime import datetime, timedelta
from news.models import *
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def send_subsmail():
    categories = Category.objects.all()

    for category in categories:
        mails = list()
        posts = Post.objects.filter(create_time__gte=(datetime.today() - timedelta(days=7)),
                                    category=category).order_by('-create_time')
        subs = category.subscribers.all()
        if posts:
            if subs:
                for sub in subs:
                    html_content = render_to_string(
                        'weeklycat.html', {'category': category,
                                           'categories': categories,
                                           'posts': posts,
                                           })
                    mail = sub.email
                    msg = EmailMultiAlternatives(
                        subject=f'Еженедельная новостная рассылка в категории {category}',
                        body='',
                        from_email='ShinyBlackArrow@yandex.ru',
                        to=[mail],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    mails.append(msg)

            get_connection().send_messages(mails)
    print('done')


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_subsmail,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="send_subsmail",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_subsmail'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
