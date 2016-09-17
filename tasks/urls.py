from django.conf.urls import url

from .task import TaskList

urlpatterns = [
    url(r'^$', TaskList.as_view(), name='home'),
    url(r'^tasks/$', TaskList.as_view(), name='tasks'),
]
