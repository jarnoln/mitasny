from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tasks.models import Project, Task
from .ext_test_case import ExtTestCase


class TaskListTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:tasks'), '/tasks/')

    def test_default_content(self):
        response = self.client.get(reverse('tasks:tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasks')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('tasks:tasks'))
        self.assertTemplateUsed(response, 'tasks/task_list.html')

    def test_default_context(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:tasks'))
        self.assertEqual(response.context['task_list'].count(), 0)
        task = Task.objects.create(project=project, name='test_task', title='Test task', created_by=creator)
        response = self.client.get(reverse('tasks:tasks'))
        self.assertEqual(response.context['task_list'].count(), 1)
        self.assertEqual(response.context['task_list'][0], task)
        self.assertContains(response, task.title)
        Task.objects.create(project=project, name='test_task_2', created_by=creator)
        response = self.client.get(reverse('tasks:tasks'))
        self.assertEqual(response.context['task_list'].count(), 2)


class TaskPageTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:task', args=['test_project', 'test_task']),
                         '/project/test_project/task/test_task/')

    def test_uses_correct_template(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        task = Task.objects.create(project=project, name='test_task', title='Test task', created_by=creator)
        response = self.client.get(reverse('tasks:task', args=[project.name, task.name]))
        self.assertTemplateUsed(response, 'tasks/task_detail.html')

    def test_get_absolute_url(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        task = Task.objects.create(project=project, name='test_task', title='Test task', created_by=creator)
        self.assertEqual(task.get_absolute_url(), reverse('tasks:task', args=[project.name, task.name]))

    def test_default_context(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        task = Task.objects.create(project=project, name='test_task', title='Test task', created_by=creator)
        response = self.client.get(reverse('tasks:task', args=[project.name, task.name]))
        self.assertEqual(response.context['task'], task)
        self.assertEqual(response.context['message'], '')
        self.assertEqual(response.context['can_edit'], False)

    def test_404_not_found(self):
        response = self.client.get(reverse('tasks:task', args=['missing_project', 'missing_task']))
        self.assertTemplateUsed(response, '404.html')
