from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sd_server.settings')

app = Celery('sd_server')  # celery app
app.config_from_object('django.conf:settings', namespace='CELERY')  # celery config
app.autodiscover_tasks()
