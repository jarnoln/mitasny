from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView


# class TaskList(ListView):
class TaskList(TemplateView):
    template_name = 'tasks/tasks.html'

    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        return context
