from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tasks.models import Project


class ProjectListTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:projects'), '/projects/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('tasks:projects'))
        self.assertTemplateUsed(response, 'tasks/tasks_base.html')
        self.assertTemplateUsed(response, 'tasks/project_list.html')

    def test_default_context(self):
        response = self.client.get(reverse('tasks:projects'))
        self.assertEqual(response.context['project_list'].count(), 0)
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:projects'))
        self.assertEqual(response.context['project_list'].count(), 1)
        self.assertEqual(response.context['project_list'][0], project)
        self.assertContains(response, project.title)
        Project.objects.create(name='test_project_2', created_by=creator)
        response = self.client.get(reverse('tasks:projects'))
        self.assertEqual(response.context['project_list'].count(), 2)
