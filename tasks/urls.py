from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .tasks_user import TasksUserList, TasksUserDetail, TasksUserRegister, TasksUserUpdate, TasksUserDelete
from .project import ProjectList, ProjectListWeekly, ProjectDetail, ProjectWeekly, ProjectCreate, ProjectUpdate, ProjectDelete
from .task import TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskMove, TaskSetPhaseTo, TaskDelete

app_name = 'tasks'

urlpatterns = [
    url(r'^$', ProjectList.as_view(), name='home'),
    url(r'^register/$', TasksUserRegister.as_view(), name='register'),
    url(r'^user/(?P<slug>[\w\.-]+)/delete/$', login_required(TasksUserDelete.as_view()), name='user_delete'),
    url(r'^user/(?P<slug>[\w\.-]+)/edit/$', login_required(TasksUserUpdate.as_view()), name='user_update'),
    url(r'^user/(?P<slug>[\w\.-]+)/$', TasksUserDetail.as_view(), name='user'),
    url(r'^project/create/$', login_required(ProjectCreate.as_view()), name='project_create'),
    url(r'^project/(?P<project_name>[\w\.-]+)/task/create/$', login_required(TaskCreate.as_view()), name='task_create'),
    url(r'^project/(?P<project_name>[\w\.-]+)/task/(?P<slug>[\w\.-]+)/set_phase_to/(?P<phase>[\w\.-]+)/$', login_required(TaskSetPhaseTo.as_view()), name='task_set_phase_to'),
    url(r'^project/(?P<project_name>[\w\.-]+)/task/(?P<slug>[\w\.-]+)/move/(?P<dir>[\w\.-]+)/$', login_required(TaskMove.as_view()), name='task_move'),
    url(r'^project/(?P<project_name>[\w\.-]+)/task/(?P<slug>[\w\.-]+)/edit/$', TaskUpdate.as_view(), name='task_update'),
    url(r'^project/(?P<project_name>[\w\.-]+)/task/(?P<slug>[\w\.-]+)/delete/$', TaskDelete.as_view(), name='task_delete'),
    url(r'^project/(?P<project_name>[\w\.-]+)/task/(?P<slug>[\w\.-]+)/$', TaskDetail.as_view(), name='task'),
    url(r'^project/(?P<slug>[\w\.-]+)/tab/(?P<tab>[\w\.-]+)/$', ProjectDetail.as_view(), name='project_tab'),
    url(r'^project/(?P<slug>[\w\.-]+)/weekly_report.html$', ProjectWeekly.as_view(), name='project_weekly'),
    url(r'^project/(?P<slug>[\w\.-]+)/edit/$', login_required(ProjectUpdate.as_view()), name='project_update'),
    url(r'^project/(?P<slug>[\w\.-]+)/delete/$', login_required(ProjectDelete.as_view()), name='project_delete'),
    url(r'^project/(?P<slug>[\w\.-]+)/$', ProjectDetail.as_view(), name='project'),
    url(r'^projects/weekly/$', ProjectListWeekly.as_view(), name='projects_weekly'),
    url(r'^projects/$', ProjectList.as_view(), name='projects'),
    url(r'^users/$', TasksUserList.as_view(), name='users'),
    url(r'^tasks/$', TaskList.as_view(), name='tasks'),
]
