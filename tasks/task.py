from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
import models


class TaskList(ListView):
    model = models.Task

    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        return context
