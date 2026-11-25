web: gunicorn hairsoft.wsgi --bind 0.0.0.0:$PORT --log-file -
worker: celery -A hairsoft worker --beat -l info --concurrency 2