import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from tasks.models import Project, Priority, TaskStatus, Task


class ProjectModelTest(TestCase):
    def test_can_save_and_load(self):
        creator = User.objects.create(username='creator')
        project = Project(name='test_project', created_by=creator)
        project.save()
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Project.objects.all()[0], project)

    def test_absolute_url(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.get_absolute_url(), '/project/test_project/')

    def test_total_work_left(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.total_work_left, 0)
        self.assertEqual(project.finish_date, datetime.date.today())  # Does not work on weekends
        Task.objects.create(project=project, name='task_1', work_left=1, created_by=creator)
        self.assertEqual(project.total_work_left, 1)
        Task.objects.create(project=project, name='task_2', work_left=2, created_by=creator)
        self.assertEqual(project.total_work_left, 3)
        Task.objects.create(project=project, name='task_3', work_left=3, created_by=creator)
        self.assertEqual(project.total_work_left, 6)

    def test_finish_date(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.total_work_left, 0)
        today = datetime.date.today()
        if today.weekday() < 5:  # Does not work on weekends
            self.assertEqual(project.finish_date, today)


class PriorityModelTest(TestCase):
    def test_can_save_and_load(self):
        priority = Priority(name='critical', title='Critical')
        priority.save()
        self.assertEqual(Priority.objects.all().count(), 1)
        self.assertEqual(Priority.objects.all()[0], priority)


class TaskStatusModelTest(TestCase):
    def test_can_save_and_load(self):
        status = TaskStatus(name='ongoing', title='Ongoing')
        status.save()
        self.assertEqual(TaskStatus.objects.all().count(), 1)
        self.assertEqual(TaskStatus.objects.all()[0], status)


class TaskModelTest(TestCase):
    def test_can_save_and_load(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task = Task(project=project, name='test_task', title='Test task', created_by=creator)
        task.save()
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertEqual(Task.objects.all()[0], task)

    def test_absolute_url(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task = Task.objects.create(project=project, name='test_task', title='Test task', created_by=creator)
        self.assertEqual(task.get_absolute_url(), '/project/test_project/task/test_task/')

    def test_cumulative_work_left(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task_1 = Task.objects.create(project=project, order=1, name='task_1', work_left=1, created_by=creator)
        self.assertEqual(task_1.cumulative_work_left, 1)
        task_3 = Task.objects.create(project=project, order=3, name='task_3', work_left=2, created_by=creator)
        self.assertEqual(task_3.cumulative_work_left, 3)
        task_2 = Task.objects.create(project=project, order=2, name='task_2', work_left=3, created_by=creator)
        self.assertEqual(task_2.cumulative_work_left, 4)
        self.assertEqual(task_3.cumulative_work_left, 6)

    def test_finish_date(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task_1 = Task.objects.create(project=project, order=1, name='task_1', work_left=0, created_by=creator)
        today = datetime.date.today()
        if today.weekday() < 5:    # Does not work on weekends
            self.assertEqual(task_1.finish_date, today)
