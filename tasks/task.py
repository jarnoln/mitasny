from django.views.generic import ListView, DetailView, TemplateView
import models


class TaskList(ListView):
    model = models.Task

    def get_context_data(self, **kwargs):
        context = super(TaskList, self).get_context_data(**kwargs)
        return context


class TaskDetail(DetailView):
    model = models.Task
    slug_field = 'name'
    fields = ['name', 'title', 'description']
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        context['can_edit'] = self.object.can_edit(self.request.user)
        return context
