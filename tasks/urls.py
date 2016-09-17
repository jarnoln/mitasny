from django.conf.urls import url

from . import views
from .task import TaskList

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^tasks/$', TaskList.as_view(), name='tasks'),
]
