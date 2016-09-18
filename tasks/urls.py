from django.conf.urls import url
from .project import ProjectList, ProjectDetail
from .task import TaskList


urlpatterns = [
    url(r'^$', TaskList.as_view(), name='home'),
    url(r'^project/(?P<slug>[\w\.]+)/$', ProjectDetail.as_view(), name='project'),
    url(r'^projects/$', ProjectList.as_view(), name='projects'),
    url(r'^tasks/$', TaskList.as_view(), name='tasks'),
]
