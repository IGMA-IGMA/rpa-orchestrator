from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Task
import io
import random

@shared_task
def generate_pdf_task(task_id):
    from reportlab.pdfgen import canvas
    task = Task.objects.get(id=task_id)
    task.status = Task.Status.PROCESSING
    task.started_at = timezone.now()
    task.save()

    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, f"Отчёт для задачи #{task.id}")
        c.drawString(100, 700, f"Создан в {timezone.now()}")
        c.save()
        buffer.seek(0)
        filename = f"task_{task.id}_report.pdf"
        task.result_file.save(filename, ContentFile(buffer.read()))
        task.status = Task.Status.SUCCESS
        task.result_log = "PDF успешно сгенерирован"
    except Exception as e:
        task.status = Task.Status.FAILURE
        task.error_message = str(e)
        task.result_log = f"Ошибка: {e}"
    finally:
        task.finished_at = timezone.now()
        task.save()

@shared_task
def parse_email_task(task_id):
    import requests
    from bs4 import BeautifulSoup
    task = Task.objects.get(id=task_id)
    task.status = Task.Status.PROCESSING
    task.started_at = timezone.now()
    task.save()

    try:
        url = task.input_data.get('url', 'https://example.com')
        html = f"<html><body><h1>Задача #{task.id}</h1><p>Данные для {url}</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        parsed_data = soup.get_text()
        task.result_log = f"Парсинг выполнен. Данные: {parsed_data[:100]}..."
        task.status = Task.Status.SUCCESS
    except Exception as e:
        task.status = Task.Status.FAILURE
        task.error_message = str(e)
        task.result_log = f"Ошибка: {e}"
    finally:
        task.finished_at = timezone.now()
        task.save()

@shared_task
def debug_task():
    return "OK"