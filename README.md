1. redis-server --daemonize yes    (Windows: run inside WSL)

2. cd backend
   python -m venv venv
   venv\Scripts\activate            (Windows)
   source venv/bin/activate         (Linux/Mac)
   pip install -r requirements.txt

3. python app.py
   open http://localhost:5001
   admin login: admin / admin@123

4. (optional, for background jobs) two more terminals, same venv:
   celery -A celery_worker.celery worker --loglevel=info
   celery -A celery_worker.celery beat --loglevel=info