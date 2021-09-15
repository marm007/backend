from celery import shared_task
from celery.utils.log import get_task_logger

from datetime import datetime

logger = get_task_logger(__name__)


@shared_task
def remove_old_relations_task():
    from api.models import Relation
    logger.info("Old relations will be deleted...")
    relations = Relation.objects.filter(end__lte=datetime.now())
    relations.delete()
