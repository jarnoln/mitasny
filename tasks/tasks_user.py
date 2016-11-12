from django.core.urlresolvers import reverse, reverse_lazy
# from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.http import HttpResponse, HttpResponseRedirect, Http404
# from django.contrib.auth.models import User
from django.contrib import auth
# from django.contrib.auth.forms import UserCreationForm


class TasksUserRegister(FormView):
    template_name = 'registration/register.html'
    form_class = auth.forms.UserCreationForm
    success_url = reverse_lazy('tasks:projects')
    # slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super(TasksUserRegister, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        return context

    def form_valid(self, form):
        # form.instance.created_by = self.request.user
        user = form.save()
        cd = form.cleaned_data
        authenticated_user = auth.authenticate(username=user.username, password=cd['password1'])
        auth.login(self.request, authenticated_user)
        return super(TasksUserRegister, self).form_valid(form)


class TasksUserDelete(DeleteView):
    slug_field = 'username'
    model = auth.models.User
    success_url = reverse_lazy('tasks:projects')

    def get_object(self):
        user = super(TasksUserDelete, self).get_object()
        if user == self.request.user or self.request.user.is_staff:
            return user

        # Todo: Smarter way to handle this
        raise Http404

    def render_to_response(self, context, **response_kwargs):
        # if self.object.can_edit(self.request.user):
            # if self.object.articles().count() == 0:
        return super(TasksUserDelete, self).render_to_response(context, **response_kwargs)
        # return HttpResponseRedirect(reverse('tasks:project', args=[self.object.name]))
