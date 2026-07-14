import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def _load_dotenv():
    env_path = os.path.join(BASE_DIR, '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # already set env var (e.g. from terminal) ko override mat karo
            os.environ.setdefault(key, value)


_load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'placement@vitb2027')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'placement.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'static', 'exports')

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'ppa-jwt-secret-2027')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    # Redis cache
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    CACHE_DEFAULT_TIMEOUT = 60

    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')

    # Notification channels (optional — falls back to console log if unset)
    GCHAT_WEBHOOK_URL = os.environ.get('GCHAT_WEBHOOK_URL', '')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@placementportal.local')

    # Days before deadline to start reminding
    REMINDER_WINDOW_DAYS = 2