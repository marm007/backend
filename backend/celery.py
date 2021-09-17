from celery import Celery
from celery.signals import worker_ready

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_ready.connect
def at_start(sender, **k):
    with sender.app.connection() as conn:
         sender.app.send_task('backend.tasks.remove_old_relations_task', connection=conn)