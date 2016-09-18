from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib import auth


class HomePageTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:home'), '/')

    def test_default_content(self):
        response = self.client.get(reverse('tasks:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasks')


class UserTest(TestCase):
    def test_login(self):
        creator = auth.models.User.objects.create(username='creator', email='creator@iki.fi', password='password')
        response = self.client.post(reverse('login'), { 'username': creator.username, 'password': 'password'})


class TaskListTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:tasks'), '/tasks/')

    def test_default_content(self):
        response = self.client.get(reverse('tasks:tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasks')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('tasks:tasks'))
        self.assertTemplateUsed(response, 'tasks/tasks.html')
