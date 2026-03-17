# backend/controllers/config.py
import os
from datetime import timedelta
from celery.schedules import crontab

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = 'your_password_salt_here'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'

    # Redis cache settings (for Flask-Caching)
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300

    # Redis connection settings
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 1

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')

    # ===== CELERY SETTINGS (NEW STYLE - lowercase) =====
    broker_url = 'redis://127.0.0.1:6379/1'
    result_backend = 'redis://127.0.0.1:6379/1'
    timezone = 'Asia/Kolkata'
    task_track_started = True
    task_time_limit = 30 * 60               # 30 minutes
    task_soft_time_limit = 25 * 60          # optional soft limit
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']

    # Windows‑optimized settings
    broker_pool_limit = None
    redis_socket_keepalive = True
    redis_retry_on_timeout = True
    broker_connection_retry_on_startup = True
    broker_connection_max_retries = 10
    broker_heartbeat = 10
    broker_heartbeat_checkrate = 2.0
    worker_pool = 'solo'
    broker_transport_options = {
        'max_connections': 1,
        'socket_keepalive': True,
    }

    # Email settings
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = ('Placement Portal', 'noreply@placement.local')