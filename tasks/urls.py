from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .project import ProjectList, ProjectDetail, ProjectCreate, ProjectDelete
from .task import TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskDelete


urlpatterns = [
    url(r'^$', ProjectList.as_view(), name='home'),
    url(r'^project/create/$', login_required(ProjectCreate.as_view()), name='project_create'),
    url(r'^project/(?P<project_name>[\w\.]+)/task/create/$', login_required(TaskCreate.as_view()), name='task_create'),
    url(r'^project/(?P<project_name>[\w\.]+)/task/(?P<slug>[\w\.]+)/update/$', TaskUpdate.as_view(), name='task_update'),
    url(r'^project/(?P<project_name>[\w\.]+)/task/(?P<slug>[\w\.]+)/delete/$', TaskDelete.as_view(), name='task_delete'),
    url(r'^project/(?P<project_name>[\w\.]+)/task/(?P<slug>[\w\.]+)/$', TaskDetail.as_view(), name='task'),
    url(r'^project/(?P<slug>[\w\.]+)/delete/$', login_required(ProjectDelete.as_view()), name='project_delete'),
    url(r'^project/(?P<slug>[\w\.]+)/$', ProjectDetail.as_view(), name='project'),
    url(r'^projects/$', ProjectList.as_view(), name='projects'),
    url(r'^tasks/$', TaskList.as_view(), name='tasks'),
]
