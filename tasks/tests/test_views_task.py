from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tasks.models import Project, Task, Phase
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


class CreateTaskTest(ExtTestCase):
    def test_reverse_task_create(self):
        self.assertEqual(reverse('tasks:task_create', args=['test_project']), '/project/test_project/task/create/')

    def test_uses_correct_template(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project")
        response = self.client.get(reverse('tasks:task_create', args=[project.name]))
        self.assertTemplateUsed(response, 'tasks/task_form.html')

    def test_default_context(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project")
        response = self.client.get(reverse('tasks:task_create', args=[project.name]))
        self.assertEqual(response.context['project'], project)
        self.assertEqual(response.context['message'], '')

    def test_can_create_new_task(self):
        self.assertEqual(Task.objects.all().count(), 0)
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project")
        response = self.client.post(reverse('tasks:task_create', args=[project.name]), {
            'title': 'Test task',
            'work_left': '5',
            'description': 'For testing'}, follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertEqual(response.context['task'].project, project)
        self.assertEqual(response.context['task'].name, 'test-task')
        self.assertEqual(response.context['task'].title, 'Test task')
        self.assertEqual(response.context['task'].description, 'For testing')
        self.assertEqual(response.context['task'].work_left, 5)
        self.assertEqual(response.context['task'].order, 0)
        self.assertEqual(response.context['task'].phase, None)

    def test_order_increases_with_task_count(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project")
        response = self.client.post(reverse('tasks:task_create', args=[project.name]),
                                    {'title': 'Test task 1',
                                     'description': '',
                                     'work_left': '1'}, follow=True)
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertEqual(response.context['task'].order, 0)
        response = self.client.post(reverse('tasks:task_create', args=[project.name]),
                                    {'title': 'Test task 2',
                                     'description': '',
                                     'work_left': '1'}, follow=True)
        self.assertEqual(Task.objects.all().count(), 2)
        self.assertEqual(response.context['task'].order, 1)
        response = self.client.post(reverse('tasks:task_create', args=[project.name]),
                                {'title': 'Test task 3',
                                 'description': '',
                                 'work_left': '1'}, follow=True)
        self.assertEqual(Task.objects.all().count(), 3)
        self.assertEqual(response.context['task'].order, 2)

    def test_initial_phase_set_to_pending(self):
        self.create_default_phases()
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project")
        response = self.client.post(reverse('tasks:task_create', args=[project.name]), {
            'title': 'Test task',
            'work_left': '5',
            'description': 'For testing'}, follow=True)
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertEqual(response.context['task'].phase.name, 'pending')

    def test_cant_create_task_if_not_logged_in(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project")
        response = self.client.get(reverse('tasks:task_create', args=[project.name]), follow=True)
        self.assertTemplateUsed(response, '404.html')
        response = self.client.post(
            reverse('tasks:task_create', args=[project.name]),
                {
                    'title': 'Test task',
                    'description': 'For testing'
                }, follow=True)
        self.assertEqual(Task.objects.all().count(), 0)
        self.assertTemplateUsed(response, '404.html')

    def test_cant_create_task_with_existing_name(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project")
        task = Task.objects.create(project=project, created_by=creator, name="test-task", title="Test task")
        self.assertEqual(Task.objects.all().count(), 1)
        response = self.client.post(
            reverse('tasks:task_create', args=[project.name]),
            {
                'title': 'Test task',
                'description': 'For testing',
                'work_left': '5'
            },
            follow=True)
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertTemplateUsed(response, 'tasks/task_form.html')
        # self.assertContains(response, 'Task with this Name already exists')


class UpdateTaskTest(ExtTestCase):
    def test_reverse_task_edit(self):
        self.assertEqual(reverse('tasks:task_update', args=['test_project', 'test_task']),
                         '/project/test_project/task/test_task/update/')

    def test_get_edit_url(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_blog")
        task = Task.objects.create(project=project, created_by=creator, name="test_task")
        self.assertEqual(task.get_edit_url(), reverse('tasks:task_update', args=[project.name, task.name]))

    def test_uses_correct_template(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project")
        task = Task.objects.create(project=project, created_by=creator, name="test_task")
        response = self.client.get(reverse('tasks:task_update', args=[project.name, task.name]))
        self.assertTemplateUsed(response, 'tasks/task_form.html')

    def test_default_context(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project")
        task = Task.objects.create(project=project, created_by=creator, name="test_task")
        response = self.client.get(reverse('tasks:task_update', args=[project.name, task.name]))
        self.assertEqual(response.context['task'], task)
        self.assertEqual(response.context['task'].project, project)
        self.assertEqual(response.context['project'], project)
        self.assertEqual(response.context['message'], '')

    def test_can_update_task(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project", description="Testing")
        task = Task.objects.create(project=project, created_by=creator, name="test_task", title="Test task")
        self.assertEqual(Project.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:task_update', args=[project.name, task.name]),
                                    {'title': 'Task updated', 'description': 'Updated', 'work_left': '5', 'order': '9'},
                                    follow=True)
        self.assertEqual(Task.objects.all().count(), 1)
        task = Task.objects.all()[0]
        self.assertEqual(task.title, 'Task updated')
        self.assertEqual(task.description, 'Updated')
        self.assertEqual(task.work_left, 5)
        self.assertEqual(task.order, 9)
        self.assertTemplateUsed(response, 'tasks/project_detail.html')

    def test_can_update_phase(self):
        self.create_default_phases()
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project",
                                         description="Testing")
        task = Task.objects.create(project=project, created_by=creator, name="test_task", title="Test task")
        phase = Phase.objects.get(name='ongoing')
        response = self.client.post(reverse('tasks:task_update', args=[project.name, task.name]),
                                {'title': 'Task updated', 'description': '', 'work_left': '5', 'order': '9', 'phase': phase.id},
                                follow=True)
        self.assertTemplateUsed(response, 'tasks/project_detail.html')
        self.assertEqual(Task.objects.all().count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, 'Task updated')
        self.assertEqual(task.phase.name, 'ongoing')


class DeleteTaskPageTest(ExtTestCase):
    def test_reverse_blog_delete(self):
        self.assertEqual(reverse('tasks:task_delete', args=['test_project', 'test_task']),
                         '/project/test_project/task/test_task/delete/')

    def test_uses_correct_template(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project")
        task = Task.objects.create(project=project, created_by=creator, name="test_task", title="Test task")
        response = self.client.get(reverse('tasks:task_delete', args=[project.name, task.name]))
        self.assertTemplateUsed(response, 'tasks/task_confirm_delete.html')

    def test_can_delete_task(self):
        creator = self.create_and_log_in_user()
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project", description="Testing")
        task = Task.objects.create(project=project, created_by=creator, name="test_task", title="Test task")
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Task.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:task_delete', args=[project.name, task.name]), {}, follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Task.objects.all().count(), 0)

    def test_404_no_project(self):
        creator = self.create_and_log_in_user()
        response = self.client.get(reverse('tasks:task_delete', args=['test_project', 'test_task']))
        self.assertTemplateUsed(response, '404.html')

    def test_cant_delete_task_if_not_logged_in(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(created_by=creator, name="test_project", title="Test project", description="Testing")
        task = Task.objects.create(project=project, created_by=creator, name="test_task", title="Test task")
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Task.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:task_delete', args=[project.name, task.name]), {}, follow=True)
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertTemplateUsed(response, '404.html')
