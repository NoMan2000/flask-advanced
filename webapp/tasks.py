import datetime
import smtplib
from email.mime.text import MIMEText

from flask import render_template
from flask_mail import Message

from webapp.extensions import celery, mail
from webapp.models import Category
from .models import Reminder


@celery.task()
def log(msg):
    return msg


@celery.task()
def multiply(x, y):
    return x * y


@celery.task(
    bind=True,
    ignore_result=True,
    default_retry_delay=300,
    max_retries=5
)
def remind(self, pk):
    reminder = Reminder.query.get(pk)
    msg = MIMEText(reminder.text)
    msg = Message("Your reminder",
                  sender="from@example.com",
                  recipients=[reminder.email])

    msg.body = reminder.text
    mail.send(msg)


@celery.task(
    bind=True,
    ignore_result=True,
    default_retry_delay=300,
    max_retries=5
)
def digest(self):
    # find the start and end of this week
    year, week = datetime.datetime.now().isocalendar()[0:2]
    date = datetime.date(year, 1, 1)
    if (date.weekday() > 3):
        date = date + datetime.timedelta(7 - date.weekday())
    else:
        date = date - datetime.timedelta(date.weekday())
    delta = datetime.timedelta(days=(week - 1) * 7)
    start, end = date + delta, date + delta + datetime.timedelta(days=6)

    categories = Category.query.filter(
        Category.publish_date >= start,
        Category.publish_date <= end
    ).all()

    if (len(categories) == 0):
        return

    msg = MIMEText(render_template("digest.html", categories=categories), 'html')

    msg['Subject'] = "Weekly Digest"
    msg['From'] = ""

    try:
        smtp_server = smtplib.SMTP('localhost')
        smtp_server.starttls()
        # smtp_server.login(user, password)
        smtp_server.sendmail("", [""], msg.as_string())
        smtp_server.close()

        return
    except Exception as e:
        self.retry(exc=e)


def on_reminder_save(mapper, connect, self):
    remind.apply_async(args=(self.id,), eta=self.date)
