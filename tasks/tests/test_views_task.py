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
