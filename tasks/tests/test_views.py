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
    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_post(self):
        user = auth.models.User.objects.create(username='creator', email='creator@iki.fi')
        user.set_password('pw')
        user.save()
        response = self.client.post(reverse('login'), {'username': user.username, 'password': 'pw', 'next': reverse('tasks:home')}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertEqual(response.context['user'], user)
        self.assertTemplateUsed(response, 'tasks/project_list.html')

    def test_logout(self):
        user = auth.models.User.objects.create(username='creator', email='creator@iki.fi')
        user.set_password('pw')
        user.save()
        response = self.client.post(reverse('login'), {'username': user.username, 'password': 'pw', 'next': reverse('tasks:home')}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated())
        response = self.client.get(reverse('logout'))
        self.assertFalse(response.context['user'].is_authenticated())
        self.assertTemplateUsed(response, 'registration/logged_out.html')

    def test_logout_redirect(self):
        user = auth.models.User.objects.create(username='creator', email='creator@iki.fi')
        user.set_password('pw')
        user.save()
        response = self.client.post(reverse('login'), {'username': user.username, 'password': 'pw', 'next': reverse('tasks:home')}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated())
        response = self.client.get(reverse('logout') + '?next=' + reverse('tasks:projects'), follow=True)
        self.assertFalse(response.context['user'].is_authenticated())
        self.assertTemplateUsed(response, 'tasks/project_list.html')

    def test_register_get(self):
        response = self.client.get(reverse('tasks:register'))
        self.assertTemplateUsed(response, 'registration/register.html')
