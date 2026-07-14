import os
from flask import Flask, send_from_directory
from celery.schedules import crontab

from config import Config
from extensions import db, jwt, cache, celery
from models import User

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)

    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        timezone='Asia/Kolkata',
        beat_schedule={
            'daily-deadline-reminders': {
                'task': 'tasks.send_deadline_reminders',
                'schedule': crontab(hour=9, minute=0),  
            },
            'monthly-placement-report': {
                'task': 'tasks.generate_monthly_report',
                'schedule': crontab(hour=6, minute=0, day_of_month=1),  
            },
        },
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    from routes.auth import auth_bp
    from routes.routes_admin import admin_bp
    from routes.routes_company import company_bp
    from routes.routes_student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)


    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/<path:filename>')
    def serve_frontend(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin@123')
            db.session.add(admin)
            db.session.commit()

    return app


myapp = create_app()

if __name__ == '__main__':
    myapp.run(debug=True, port=5001)
