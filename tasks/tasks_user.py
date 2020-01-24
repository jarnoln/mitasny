from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.http import HttpResponse, HttpResponseRedirect, Http404
# from django.contrib.auth.models import User
from django.contrib import auth
# from django.contrib.auth.forms import UserCreationForm


def can_edit_user(logged_user, target_user):
    ''' Is logged in user allowed to edit target user '''
    if logged_user == target_user:
        return True
    if logged_user.is_staff:
        return True
    return False


class TasksUserList(ListView):
    model = auth.get_user_model()

    def get_context_data(self, **kwargs):
        context = super(TasksUserList, self).get_context_data(**kwargs)
        context['messages'] = self.request.GET.get('message', '')
        return context


class TasksUserDetail(DetailView):
    model = auth.get_user_model()
    slug_field = 'username'
    fields = ['username', 'first_name', 'last_name', 'email']
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super(TasksUserDetail, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        # context['can_edit'] = self.object.can_edit(self.request.user)
        context['can_edit'] = can_edit_user(logged_user=self.request.user, target_user=self.object)
        return context


class TasksUserRegister(FormView):
    template_name = 'registration/register.html'
    form_class = auth.forms.UserCreationForm
    # success_url = reverse_lazy('tasks:projects')
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

    def get_success_url(self):
        if self.request.user:
            return reverse_lazy('tasks:user_update', args=[self.request.user.username])
        else:
            return reverse('tasks:users')


class TasksUserUpdate(UpdateView):
    model = auth.get_user_model()
    slug_field = 'username'
    fields = ['username', 'email', 'first_name', 'last_name']

    def get_object(self):
        target_user = super(TasksUserUpdate, self).get_object()
        if can_edit_user(logged_user=self.request.user, target_user=target_user):
            return target_user

        # Todo: Smarter way to handle this
        raise Http404

    def get_context_data(self, **kwargs):
        context = super(TasksUserUpdate, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        return context

    def get_success_url(self):
        if self.object:
            return reverse_lazy('tasks:user', args=[self.object.username])
        else:
            return reverse('tasks:users')


class TasksUserDelete(DeleteView):
    slug_field = 'username'
    model = auth.get_user_model()
    success_url = reverse_lazy('tasks:projects')

    def get_object(self):
        target_user = super(TasksUserDelete, self).get_object()
        if can_edit_user(logged_user=self.request.user, target_user=target_user):
            return target_user

        # Todo: Smarter way to handle this
        raise Http404

    def render_to_response(self, context, **response_kwargs):
        # if self.object.can_edit(self.request.user):
            # if self.object.articles().count() == 0:
        return super(TasksUserDelete, self).render_to_response(context, **response_kwargs)
        # return HttpResponseRedirect(reverse('tasks:project', args=[self.object.name]))
