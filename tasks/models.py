from django.db import models
from django.utils import timezone

class Task(models.Model):
    class BotType(models.TextChoices):
        PDF_GENERATOR = 'pdf', 'Генератор PDF'
        EMAIL_PARSER = 'email', 'Парсер email'

    class Status(models.TextChoices):
        PENDING = 'pending', 'В очереди'
        PROCESSING = 'processing', 'Выполняется'
        SUCCESS = 'success', 'Успешно'
        FAILURE = 'failure', 'Ошибка'

    bot_type = models.CharField('Тип бота', max_length=20, choices=BotType.choices)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.PENDING)
    input_data = models.JSONField('Входные данные', default=dict, blank=True)
    result_file = models.FileField('Файл результата', upload_to='results/%Y/%m/%d/', null=True, blank=True)
    result_log = models.TextField('Лог выполнения', blank=True, default='')
    error_message = models.TextField('Сообщение об ошибке', blank=True, default='')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    started_at = models.DateTimeField('Начало выполнения', null=True, blank=True)
    finished_at = models.DateTimeField('Завершена', null=True, blank=True)

    def __str__(self):
        return f"Task #{self.id} - {self.get_bot_type_display()} ({self.get_status_display()})"

    def duration_seconds(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['bot_type']),
        ]
        ordering = ['-created_at']