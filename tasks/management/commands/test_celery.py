from django.core.management.base import BaseCommand
from tasks.tasks import debug_task

class Command(BaseCommand):
    help = 'Test Celery connection'

    def handle(self, *args, **options):
        self.stdout.write("Testing Celery...")
        result = debug_task.delay()
        self.stdout.write(f"Task ID: {result.id}")
        self.stdout.write("Celery is working!")
        