from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task
from .tasks import generate_pdf_task, parse_email_task
from unittest.mock import patch, MagicMock
import io

class TaskModelTest(TestCase):
    def test_create_task(self):
        task = Task.objects.create(
            bot_type=Task.BotType.PDF_GENERATOR,
            status=Task.Status.PENDING,
            input_data={"test": "data"}
        )
        self.assertEqual(task.bot_type, Task.BotType.PDF_GENERATOR)
        self.assertEqual(task.status, Task.Status.PENDING)
        self.assertIsNotNone(task.created_at)
        self.assertEqual(str(task), f"Task #{task.id} - Генератор PDF (В очереди)")

class TaskViewsTest(TestCase):
    def test_task_list_view(self):
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')

    def test_dashboard_view(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/dashboard.html')

class CeleryTasksTest(TestCase):
    def test_generate_pdf_task(self):
        task = Task.objects.create(
            bot_type=Task.BotType.PDF_GENERATOR,
            status=Task.Status.PENDING
        )
        
        # Мокируем canvas.Canvas через sys.modules
        with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
            mock_canvas.return_value = MagicMock()
            generate_pdf_task(task.id)
        
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.SUCCESS)

    def test_parse_email_task(self):
        task = Task.objects.create(
            bot_type=Task.BotType.EMAIL_PARSER,
            status=Task.Status.PENDING,
            input_data={"url": "https://example.com"}
        )
        
        # Мокируем requests.get
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><h1>Test</h1><p>Data</p></body></html>"
            mock_get.return_value = mock_response
            
            # Мокируем BeautifulSoup
            with patch('bs4.BeautifulSoup') as mock_bs:
                mock_soup = MagicMock()
                mock_soup.get_text.return_value = "Test Data"
                mock_bs.return_value = mock_soup
                parse_email_task(task.id)
        
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.SUCCESS)