from celery import shared_task
from django.utils import timezone
from .models import Table
from datetime import timedelta

@shared_task
def close_abandoned_tables():
    old_tables = Table.objects.filter(
        status='occupied',
        updated_at__lt=timezone.now() - timedelta(hours=2)
    )
    for t in old_tables:
        t.status = 'closed'
        t.save()
