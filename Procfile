web: gunicorn myproj.wsgi

worker: celery -A myproj worker --pool=solo -l info
beat: celery -A myproj beat -l info
