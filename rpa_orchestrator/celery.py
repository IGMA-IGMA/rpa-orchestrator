import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rpa_orchestrator.settings')

app = Celery('rpa_orchestrator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()