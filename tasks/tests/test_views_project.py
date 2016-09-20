from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tasks.models import Project, Task
from .ext_test_case import ExtTestCase


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


class ProjectPageTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:project', args=['test_project']), '/project/test_project/')

    def test_uses_correct_template(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:project', args=[project.name]))
        self.assertTemplateUsed(response, 'tasks/project_detail.html')

    def test_get_absolute_url(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        self.assertEqual(project.get_absolute_url(), reverse('tasks:project', args=[project.name]))

    def test_default_context(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:project', args=[project.name]))
        self.assertEqual(response.context['project'], project)
        # self.assertEqual(response.context['blog'].articles().count(), 0)
        # self.assertEqual(response.context['message'], '')
        # self.assertEqual(response.context['can_edit'], True)

    def test_404_not_found(self):
        response = self.client.get(reverse('tasks:project', args=['missing_project']))
        self.assertTemplateUsed(response, '404.html')


class ProjectWeeklyReportTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:project_weekly', args=['test_project']),
                         '/project/test_project/weekly_report.html')

    def test_uses_correct_template(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:project_weekly', args=[project.name]))
        self.assertTemplateUsed(response, 'tasks/project_weekly.html')

    def test_default_context(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:project_weekly', args=[project.name]))
        self.assertEqual(response.context['project'], project)

    def test_404_not_found(self):
        response = self.client.get(reverse('tasks:project', args=['missing_project']))
        self.assertTemplateUsed(response, '404.html')


class CreateProjectTest(ExtTestCase):
    def test_reverse_project_create(self):
        self.assertEqual(reverse('tasks:project_create'), '/project/create/')

    def test_uses_correct_template(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse('tasks:project_create'))
        self.assertTemplateUsed(response, 'tasks/project_form.html')

    def test_default_context(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse('tasks:project_create'))
        self.assertEqual(response.context['message'], '')

    def test_can_create_new_project(self):
        self.assertEqual(Project.objects.all().count(), 0)
        self.create_and_log_in_user()
        response = self.client.post(reverse('tasks:project_create'), {
            'name': 'test_project',
            'title': 'Test project',
            'description': 'For testing'}, follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(response.context['project'].name, 'test_project')
        self.assertEqual(response.context['project'].title, 'Test project')
        self.assertEqual(response.context['project'].description, 'For testing')

    def test_cant_create_project_if_not_logged_in(self):
        response = self.client.get(reverse('tasks:project_create'), follow=True)
        self.assertTemplateUsed(response, '404.html')
        response = self.client.post(
            reverse('tasks:project_create'),
                {
                    'name': 'test_project',
                    'title': 'Test project',
                    'description': 'For testing'
                }, follow=True)
        self.assertEqual(Project.objects.all().count(), 0)
        self.assertTemplateUsed(response, '404.html')

    def test_cant_create_project_with_existing_name(self):
        creator = self.create_and_log_in_user()
        Project.objects.create(created_by=creator, name="test_project", title="Test project")
        self.assertEqual(Project.objects.all().count(), 1)
        response = self.client.post(
            reverse('tasks:project_create'),
            {
                'name': 'test_project',
                'title': 'Test project',
                'description': 'For testing'
            },
            follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertTemplateUsed(response, 'tasks/project_form.html')
        self.assertContains(response, 'Project with this Name already exists')


class DeleteProjectPageTest(ExtTestCase):
    def test_reverse_blog_delete(self):
        self.assertEqual(reverse('tasks:project_delete', args=['test_project']), '/project/test_project/delete/')

    def test_uses_correct_template(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project")
        response = self.client.get(reverse('tasks:project_delete', args=[project.name]))
        self.assertTemplateUsed(response, 'tasks/project_confirm_delete.html')

    def test_can_delete_project(self):
        creator = self.create_and_log_in_user()
        Project.objects.create(created_by=creator, name="test_project", title="Test project", description="Testing")
        self.assertEqual(Project.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:project_delete', args=['test_project']), {}, follow=True)
        self.assertEqual(Project.objects.all().count(), 0)

    def test_404_no_project(self):
        creator = self.create_and_log_in_user()
        response = self.client.get(reverse('tasks:project_delete', args=['test_project']))
        self.assertTemplateUsed(response, '404.html')

    def test_cant_delete_project_if_not_logged_in(self):
        creator = User.objects.create(username='creator')
        Project.objects.create(created_by=creator, name="test_project", title="Test project", description="Testing")
        self.assertEqual(Project.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:project_delete', args=['test_project']), {}, follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertTemplateUsed(response, '404.html')

    def test_cant_delete_project_if_contains_tasks(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project", description="Testing")
        task = Task.objects.create(project=project, created_by=creator, name="test_task", title="Test task")
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Task.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:project_delete', args=['test_project']), {}, follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertTemplateUsed(response, '404.html')
