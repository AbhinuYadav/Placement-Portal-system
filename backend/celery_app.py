# backend/celery_app.py
from celery import Celery
from celery.schedules import crontab
import socket

# Force IPv4 to avoid Windows dual-stack resolution issues
socket.getaddrinfo('127.0.0.1', 6379)

celery = Celery(
    'placement_portal',
    broker='redis://127.0.0.1:6379/1',
    backend='redis://127.0.0.1:6379/1',
    include=['tasks']
)

# Define beat schedule directly here (most reliable approach)
celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=00),  # 8 AM daily
    },
    'monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(hour=9, minute=00, day_of_month=1),  # 9 AM on 1st
    },
}

# Windows-specific settings
celery.conf.update(
    broker_pool_limit=None,
    redis_socket_keepalive=True,
    redis_retry_on_timeout=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_heartbeat=10,
    broker_heartbeat_checkrate=2.0,
    worker_pool='solo',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    timezone='Asia/Kolkata',  # Set your timezone
    enable_utc=False,  # Use local timezone
)

def make_celery(app=None):
    if app:
        celery.conf.update(app.config)
    return celery