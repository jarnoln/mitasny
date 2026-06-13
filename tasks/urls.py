from django.urls import path
from django.contrib.auth.decorators import login_required
from .tasks_user import TasksUserList, TasksUserDetail, TasksUserRegister, TasksUserUpdate, TasksUserDelete
from .project import ProjectList, ProjectListWeekly, ProjectDetail, ProjectWeekly, ProjectCreate, ProjectUpdate, ProjectDelete
from .task import TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskMove, TaskSetPhaseTo, TaskDelete

app_name = 'tasks'

urlpatterns = [
    path('', ProjectList.as_view(), name='home'),
    path('register/', TasksUserRegister.as_view(), name='register'),
    path('user/<slug:slug>/delete/', login_required(TasksUserDelete.as_view()), name='user_delete'),
    path('user/<slug:slug>/edit/', login_required(TasksUserUpdate.as_view()), name='user_update'),
    path('user/<slug:slug>/', TasksUserDetail.as_view(), name='user'),
    path('project/create/', login_required(ProjectCreate.as_view()), name='project_create'),
    path('project/<slug:project_name>/task/create/', login_required(TaskCreate.as_view()), name='task_create'),
    path('project/<slug:project_name>/task/<slug:slug>/set_phase_to/<slug:phase>/', login_required(TaskSetPhaseTo.as_view()), name='task_set_phase_to'),
    path('project/<slug:project_name>/task/<slug:slug>/move/<slug:dir>/', login_required(TaskMove.as_view()), name='task_move'),
    path('project/<slug:project_name>/task/<slug:slug>/edit/', TaskUpdate.as_view(), name='task_update'),
    path('project/<slug:project_name>/task/<slug:slug>/delete/', TaskDelete.as_view(), name='task_delete'),
    path('project/<slug:project_name>/task/<slug:slug>/', TaskDetail.as_view(), name='task'),
    path('project/<slug:slug>/tab/<slug:tab>/', ProjectDetail.as_view(), name='project_tab'),
    path('project/<slug:slug>/weekly_report.html', ProjectWeekly.as_view(), name='project_weekly'),
    path('project/<slug:slug>/edit/', login_required(ProjectUpdate.as_view()), name='project_update'),
    path('project/<slug:slug>/delete/', login_required(ProjectDelete.as_view()), name='project_delete'),
    path('project/<slug:slug>/', ProjectDetail.as_view(), name='project'),
    path('projects/weekly/', ProjectListWeekly.as_view(), name='projects_weekly'),
    path('projects/', ProjectList.as_view(), name='projects'),
    path('users/', TasksUserList.as_view(), name='users'),
    path('tasks/', TaskList.as_view(), name='tasks'),
]