from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from .models import Project


class ProjectList(ListView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectList, self).get_context_data(**kwargs)
        return context


class ProjectDetail(DetailView):
    model = Project
    slug_field = 'name'
    fields = ['name', 'title', 'description']
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetail, self).get_context_data(**kwargs)
        #context['article_list'] = Article.objects.filter(blog=self.object)
        context['message'] = self.request.GET.get('message', '')
        # context['can_edit'] = self.object.can_edit(self.request.user)
        # context['articles'] = self.object.articles()
        return context
