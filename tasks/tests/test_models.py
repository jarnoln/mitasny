from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tasks.models import Project


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
