from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib import auth


class HomePageTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:home'), '/')

    def test_default_content(self):
        response = self.client.get(reverse('tasks:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')


class UserTest(TestCase):
    def test_login(self):
        user = auth.models.User.objects.create(username='creator', email='creator@iki.fi')
        user.set_password('pw')
        user.save()
        response = self.client.post(reverse('login'), {'username': user.username, 'password': 'pw', 'next': reverse('tasks:home')}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertEqual(response.context['user'], user)
        self.assertTemplateUsed(response, 'tasks/project_list.html')
