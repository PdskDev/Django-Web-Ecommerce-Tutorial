import os
from celery import Celery

#set default Django settings module for Celery program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finesauces_project.settings')

#Application instance
app=Celery('finesauces_project')

#Prefix Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

#Load task modules
app.autodiscover_tasks()