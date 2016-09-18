from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from .models import Project


# class TaskList(ListView):
class ProjectList(ListView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectList, self).get_context_data(**kwargs)
        return context
