"""
Run the background worker:   celery -A celery_worker.celery worker --loglevel=info
Run the periodic scheduler:  celery -A celery_worker.celery beat --loglevel=info
(Requires Redis running locally: redis-server)
"""
from app import create_app
from extensions import celery

flask_app = create_app()

# tasks module registers 'tasks.*' task names with the shared celery instance
import tasks  # noqa: F401,E402
