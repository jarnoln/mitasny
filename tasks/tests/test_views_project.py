from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Project, Task
from .ext_test_case import ExtTestCase


class ProjectListTest(ExtTestCase):
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

    def test_messages(self):
        response = self.client.get(reverse('tasks:projects'))
        self.assertEqual(len(response.context['messages']), 7)
        self.create_default_phases()
        response = self.client.get(reverse('tasks:projects'))
        self.assertEqual(len(response.context['messages']), 0)


class ProjectListWeeklyReportTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:projects_weekly'), '/projects/weekly/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('tasks:projects_weekly'))
        self.assertTemplateUsed(response, 'tasks/project_list_weekly.html')

    def test_default_context(self):
        response = self.client.get(reverse('tasks:projects_weekly'))
        self.assertEqual(response.context['project_list'].count(), 0)
        self.assertEqual(response.context['hide_chart'], '')
        self.assertEqual(response.context['hide_text'], '')
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:projects_weekly'))
        self.assertEqual(response.context['project_list'].count(), 1)
        self.assertEqual(response.context['project_list'][0], project)
        self.assertContains(response, project.title)
        Project.objects.create(name='test_project_2', created_by=creator)
        response = self.client.get(reverse('tasks:projects_weekly'))
        self.assertEqual(response.context['project_list'].count(), 2)


class ProjectPageTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:project', args=['test_project']), '/project/test_project/')
        self.assertEqual(reverse('tasks:project_tab', args=['test_project', 'table']),
                         '/project/test_project/tab/table/')

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
        self.assertEqual(response.context['tab'], 'table')
        self.assertEqual(response.context['message'], '')
        self.assertEqual(response.context['can_edit'], False)

    def test_tab(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:project_tab', args=[project.name, 'table']))
        self.assertEqual(response.context['project'], project)
        self.assertEqual(response.context['tab'], 'table')
        self.assertTemplateUsed(response, 'tasks/project_detail.html')
        self.assertTemplateUsed(response, 'tasks/project/table.html')
        response = self.client.get(reverse('tasks:project_tab', args=[project.name, 'chart']))
        self.assertEqual(response.context['tab'], 'chart')
        self.assertTemplateUsed(response, 'tasks/project/chart.html')
        response = self.client.get(reverse('tasks:project_tab', args=[project.name, 'archive']))
        self.assertEqual(response.context['tab'], 'archive')
        self.assertTemplateUsed(response, 'tasks/project/archive.html')

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
        self.assertEqual(response.context['hide_chart'], '')
        self.assertEqual(response.context['hide_text'], '')
        self.assertContains(response, project.title)

    def test_hide_text(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:project_weekly', args=[project.name]) + '?hide_text=1')
        self.assertEqual(response.context['project'], project)
        self.assertEqual(response.context['hide_chart'], '')
        self.assertEqual(response.context['hide_text'], '1')

    def test_hide_chart(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', title='Test project', created_by=creator)
        response = self.client.get(reverse('tasks:project_weekly', args=[project.name]) + '?hide_chart=1')
        self.assertEqual(response.context['project'], project)
        self.assertEqual(response.context['hide_chart'], '1')
        self.assertEqual(response.context['hide_text'], '')
        self.assertContains(response, project.title)

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
        creator = self.create_and_log_in_user()
        response = self.client.post(reverse('tasks:project_create'), {
            'name': 'test_project',
            'title': 'Test project',
            'description': 'For testing'}, follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(response.context['project'].name, 'test_project')
        self.assertEqual(response.context['project'].title, 'Test project')
        self.assertEqual(response.context['project'].description, 'For testing')
        self.assertEqual(response.context['project'].created_by, creator)

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


class UpdateProjectTest(ExtTestCase):
    def test_reverse_task_edit(self):
        self.assertEqual(reverse('tasks:project_update', args=['test_project']),
                         '/project/test_project/edit/')

    def test_uses_correct_template(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project")
        response = self.client.get(reverse('tasks:project_update', args=[project.name]))
        self.assertTemplateUsed(response, 'tasks/project_form.html')

    def test_default_context(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project")
        response = self.client.get(reverse('tasks:project_update', args=[project.name]))
        self.assertEqual(response.context['project'], project)
        self.assertEqual(response.context['message'], '')

    def test_can_update_project(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project", description="Testing")
        self.assertEqual(Project.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:project_update', args=[project.name]),
                                    {'name': 'updated_name', 'title': 'Project updated', 'description': 'Updated'},
                                    follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        project = Project.objects.all()[0]
        self.assertEqual(project.name, 'updated_name')
        self.assertEqual(project.title, 'Project updated')
        self.assertEqual(project.description, 'Updated')
        self.assertTemplateUsed(response, 'tasks/project_detail.html')


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

    def test_cant_delete_project_if_not_creator(self):
        creator = User.objects.create(username='creator')
        Project.objects.create(created_by=creator, name="test_project", title="Test project",
                                    description="Testing")
        self.assertEqual(Project.objects.all().count(), 1)
        user = self.create_and_log_in_user()
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
