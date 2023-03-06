from __future__ import absolute_import, unicode_literals

from celery.decorators import task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage




# Send email for activation user

def send_mail(mail_subject, message, to_email):
    send_email_task.delay(mail_subject, message, to_email)


def send_email(mail_subject, message, to_email):

    subject = mail_subject

    email_body = message

    email = EmailMessage(subject, email_body, settings.EMAIL_HOST_USER, to=[to_email, ])

    return email.send(fail_silently = False)



logger = get_task_logger(__name__)

@task(name="send_email_task")
def send_email_task(mail_subject, message, to_email):
    logger.info("sent %s email" %mail_subject)
    return send_email(mail_subject, message, to_email)
