from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db import connection
import csv
import redis
import os
from .models import Task
from .forms import TaskCreateForm
from .tasks import generate_pdf_task, parse_email_task, debug_task

class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        bot_type = self.request.GET.get('bot_type')
        if status:
            queryset = queryset.filter(status=status)
        if bot_type:
            queryset = queryset.filter(bot_type=bot_type)
        return queryset

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = 'tasks/task_create.html'
    success_url = reverse_lazy('tasks:task_list')

    def form_valid(self, form):
        task = form.save(commit=False)
        task.status = Task.Status.PENDING
        task.save()
        if task.bot_type == Task.BotType.PDF_GENERATOR:
            generate_pdf_task.delay(task.id)
        elif task.bot_type == Task.BotType.EMAIL_PARSER:
            parse_email_task.delay(task.id)
        messages.success(self.request, f'Задача #{task.id} создана и поставлена в очередь.')
        return redirect(self.success_url)

def dashboard(request):
    total_tasks = Task.objects.count()
    status_counts = Task.objects.values('status').annotate(count=Count('status'))
    status_dict = {item['status']: item['count'] for item in status_counts}
    
    avg_duration = Task.objects.filter(
        started_at__isnull=False,
        finished_at__isnull=False
    ).annotate(
        duration=ExpressionWrapper(
            F('finished_at') - F('started_at'),
            output_field=fields.DurationField()
        )
    ).aggregate(avg=Avg('duration'))['avg']
    
    if avg_duration:
        avg_duration = avg_duration.total_seconds()
    else:
        avg_duration = 0
    
    context = {
        'total_tasks': total_tasks,
        'status_counts': status_dict,
        'avg_duration': avg_duration,
    }
    return render(request, 'tasks/dashboard.html', context)

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Тип', 'Статус', 'Создана', 'Результат'])
    tasks = Task.objects.all()
    for task in tasks:
        writer.writerow([
            task.id,
            task.get_bot_type_display(),
            task.get_status_display(),
            task.created_at.strftime('%Y-%m-%d %H:%M'),
            task.result_file.url if task.result_file else task.result_log[:50]
        ])
    return response

def health_check(request):
    # Проверка БД
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "ok"
    except Exception:
        db_status = "error"

    # Проверка Redis
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"

    # Проверка Celery
    try:
        result = debug_task.delay()
        celery_status = "ok"
    except Exception:
        celery_status = "error"

    status_code = 200 if all(s == "ok" for s in [db_status, redis_status, celery_status]) else 500
    return JsonResponse({
        "database": db_status,
        "redis": redis_status,
        "celery": celery_status,
        "status": "healthy" if status_code == 200 else "unhealthy"
    }, status=status_code)