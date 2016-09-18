from django.conf.urls import url

from .task import TaskList

urlpatterns = [
    url(r'^$', TaskList.as_view(), name='home'),
    url(r'^tasks/$', TaskList.as_view(), name='tasks'),
    url(r'^project/(?P<project_name>[\w\.]+)/$', TaskList.as_view(), name='project'),
]
