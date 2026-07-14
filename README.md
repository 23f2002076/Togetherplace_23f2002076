# Placement Portal Application (PPA-V2)

## How to Run Locally

### 1. Start Redis
Celery and caching require Redis. Since you are on Windows, use WSL (Windows Subsystem for Linux) to run the Redis server in the background:

```bash
wsl -e sudo service redis-server start
wsl -e redis-server --daemonize yes
```

### 2. Start the Web Server
Open a terminal in the project root folder and run the following commands to start the main Flask server:

```powershell
cd backend
.\venv\Scripts\activate
python app.py
```

The application will be accessible at **http://localhost:5001**.

### 3. Start Background Jobs (Celery)
To enable features like CSV exports and email reminders, you must run the Celery worker and beat scheduler. Open **two additional terminal windows** and navigate to the project root in both.

**Terminal 2 (Celery Worker):**
```powershell
cd backend
.\venv\Scripts\activate
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

**Terminal 3 (Celery Beat):**
```powershell
cd backend
.\venv\Scripts\activate
celery -A celery_worker.celery beat --loglevel=info
```
