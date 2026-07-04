
from django import forms

from .models import Task



class TaskCreateForm(forms.ModelForm):

    class Meta:

        model = Task

        fields = ['bot_type', 'input_data']

        widgets = {

            'input_data': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите параметры в формате JSON'})

        }

