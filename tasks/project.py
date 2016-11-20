from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Project
from .check_validity import check_validity


class ProjectList(ListView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectList, self).get_context_data(**kwargs)
        context['messages'] = check_validity()
        return context


class ProjectListWeekly(ListView):
    model = Project
    template_name = 'tasks/project_list_weekly.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectListWeekly, self).get_context_data(**kwargs)
        context['messages'] = check_validity()
        context['hide_chart'] = self.request.GET.get('hide_chart', '')
        context['hide_text'] = self.request.GET.get('hide_text', '')
        return context


class ProjectDetail(DetailView):
    model = Project
    slug_field = 'name'
    fields = ['name', 'title', 'description']
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetail, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        context['can_edit'] = self.object.can_edit(self.request.user)
        context['tab'] = self.kwargs.get('tab', 'table')
        return context


class ProjectWeekly(DetailView):
    model = Project
    slug_field = 'name'
    fields = ['name', 'title', 'description']
    context_object_name = 'project'
    template_name = 'tasks/project_weekly.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectWeekly, self).get_context_data(**kwargs)
        context['hide_chart'] = self.request.GET.get('hide_chart', '')
        context['hide_text'] = self.request.GET.get('hide_text', '')
        return context


class ProjectCreate(CreateView):
    model = Project
    slug_field = 'name'
    fields = ['name', 'title', 'description']

    def get_context_data(self, **kwargs):
        context = super(ProjectCreate, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(ProjectCreate, self).form_valid(form)


class ProjectUpdate(UpdateView):
    model = Project
    slug_field = 'name'
    fields = ['name', 'title', 'description']
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdate, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        context['can_edit'] = self.object.can_edit(self.request.user)
        context['tab'] = self.kwargs.get('tab', 'table')
        return context


class ProjectDelete(DeleteView):
    slug_field = 'name'
    model = Project
    success_url = reverse_lazy('tasks:projects')

    def get_object(self):
        project = super(ProjectDelete, self).get_object()
        if project.can_edit(self.request.user):
            if project.tasks.count() == 0:
                return project

        # Todo: Smarter way to handle this
        raise Http404

    def render_to_response(self, context, **response_kwargs):
        # if self.object.can_edit(self.request.user):
            # if self.object.articles().count() == 0:
        return super(ProjectDelete, self).render_to_response(context, **response_kwargs)
        # return HttpResponseRedirect(reverse('tasks:project', args=[self.object.name]))
