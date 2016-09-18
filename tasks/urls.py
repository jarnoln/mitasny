from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .project import ProjectList, ProjectDetail, ProjectCreate, ProjectDelete
from .task import TaskList


urlpatterns = [
    url(r'^$', ProjectList.as_view(), name='home'),
    url(r'^project/create/$', login_required(ProjectCreate.as_view()), name='project_create'),
    url(r'^project/(?P<slug>[\w\.]+)/delete/$', ProjectDelete.as_view(), name='project_delete'),
    url(r'^project/(?P<slug>[\w\.]+)/$', ProjectDetail.as_view(), name='project'),
    url(r'^projects/$', ProjectList.as_view(), name='projects'),
    url(r'^tasks/$', TaskList.as_view(), name='tasks'),
]
