from jobcoin import create_app
from jobcoin.celery_utils import make_celery

app = create_app()
celery = make_celery(app)
