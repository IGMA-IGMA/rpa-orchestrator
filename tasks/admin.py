from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot_type', 'status', 'created_at', 'updated_at')
    list_filter = ('bot_type', 'status')
    search_fields = ('input_data', 'result_log')
    readonly_fields = ('created_at', 'updated_at')