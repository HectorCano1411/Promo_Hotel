import os
from celery import Celery

# Establece el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_app.settings')

app = Celery('lottery_app')

# Carga la configuración desde el archivo settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carga tareas de todas las aplicaciones registradas en Django
app.autodiscover_tasks()
