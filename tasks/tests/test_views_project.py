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


class CreateProjectTest(TestCase):
    def test_reverse_project_create(self):
        self.assertEqual(reverse('tasks:project_create'), '/project/create/')

    def test_uses_correct_template(self):
        # user = self.register_named_user()
        response = self.client.get(reverse('tasks:project_create'))
        self.assertTemplateUsed(response, 'tasks/project_form.html')

    def test_default_context(self):
        # user = self.register_named_user()
        response = self.client.get(reverse('tasks:project_create'))
        # self.assertEqual(response.context['title'], 'Create new blog')
        self.assertEqual(response.context['message'], '')

    def test_can_create_new_blog(self):
        self.assertEqual(Project.objects.all().count(), 0)
        # user = self.register_named_user()
        creator = User.objects.create(username='creator')
        response = self.client.post(reverse('tasks:project_create'), {
            'created_by': creator,
            'name': 'test_project',
            'title': 'Test project',
            'description': 'For testing'},
                                    follow=True)
        # self.assertEqual(Project.objects.all().count(), 1)
        # self.assertEqual(response.context['project'].name, 'test_project')
        # self.assertEqual(response.context['project'].title, 'Test project')
        # self.assertEqual(response.context['project'].description, 'For testing')

    def test_cant_create_blog_with_existing_name(self):
        creator = User.objects.create(username='creator')
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