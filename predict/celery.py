import os

from celery import Celery
from django.conf import settings
import predict.settings as project_settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'predict.settings')

app = Celery('predict')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: project_settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
