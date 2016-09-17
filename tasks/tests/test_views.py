from django.test import TestCase
from django.core.urlresolvers import reverse


class HomePageTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('home'), '/')

    def test_default_content(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasks')


class TaskListTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks'), '/tasks/')

    def test_default_content(self):
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasks')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('tasks'))
        self.assertTemplateUsed(response, 'tasks/tasks.html')
