import logging
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.text import slugify
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
    fields = ['title', 'description', 'work_left']
    project = None

    def dispatch(self, request, *args, **kwargs):
        project_name = kwargs['project_name']
        self.project = models.Project.objects.get(name=project_name)
        return super(TaskCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.name = slugify(form.instance.title)
        form.instance.project = self.project
        form.instance.created_by = self.request.user
        form.instance.order = self.project.tasks.count()
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


class TaskUpdate(UpdateView):
    model = models.Task
    slug_field = 'name'
    fields = ['title', 'description', 'work_left']

    def dispatch(self, request, *args, **kwargs):
        #logger = logging.getLogger(__name__)
        self.project = get_object_or_404(models.Project, name=self.kwargs['project_name'])
        #logger.warning("Registered:%s Creator:%s" % (self.request.user.username, self.blog.created_by.username))
        return super(TaskUpdate, self).dispatch(request,*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.object.can_edit(self.request.user):
            return super(TaskUpdate, self).render_to_response(context, **response_kwargs)
        else:
            return HttpResponseRedirect(reverse('tasks:task', args=[self.project.name, self.object.name]))

    def form_valid(self, form):
        logger = logging.getLogger(__name__)
        #logger.warning("Posting valid form")
        if self.object.can_edit(self.request.user):
            #logger.warning("Allowed to edit. Registered:%s Creator:%s" % (self.request.user.username, self.blog.created_by.username))
            return super(TaskUpdate, self).form_valid(form)
        else:
            logger.info("Not allowed to edit. Registered:%s Creator:%s" % (self.request.user.username, self.object.created_by.username))
            return HttpResponseRedirect(reverse('tasks:task', args=[self.project.name, self.object.name]))

    def get_context_data(self, **kwargs):
        context = super(TaskUpdate, self).get_context_data(**kwargs)
        context['project'] = self.object.project
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
