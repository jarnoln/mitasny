import logging
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect, Http404
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


class TaskCreate(CreateView):
    model = models.Task
    slug_field = 'name'
    fields = ['name', 'title', 'description']
    project = None

    def dispatch(self, request, *args, **kwargs):
        project_name = kwargs['project_name']
        self.project = models.Project.objects.get(name=project_name)
        return super(TaskCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = self.project
        form.instance.created_by = self.request.user
        if models.Task.objects.filter(project=self.project, name=form.instance.name).exists():
            logger = logging.getLogger(__name__)
            logger.warning("Task already exists: project=%s name=%s" % (self.project.name, form.instance.name))
            return super(TaskCreate, self).form_invalid(form)
        else:
            return super(TaskCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TaskCreate, self).get_context_data(**kwargs)
        context['project'] = self.project
        context['message'] = self.request.GET.get('message', '')
        return context


class TaskDelete(DeleteView):
    slug_field = 'name'
    model = models.Task
    success_url = reverse_lazy('tasks:projects')

    def get_object(self):
        task = super(TaskDelete, self).get_object()
        if task.can_edit(self.request.user):
            return task

        # Todo: Smarter way to handle this
        raise Http404

    def render_to_response(self, context, **response_kwargs):
        # if self.object.can_edit(self.request.user):
            # if self.object.articles().count() == 0:
        return super(TaskDelete, self).render_to_response(context, **response_kwargs)
        # return HttpResponseRedirect(reverse('tasks:project', args=[self.object.name]))
