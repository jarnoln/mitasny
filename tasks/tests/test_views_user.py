from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib import auth
from .ext_test_case import ExtTestCase


class UserLoginLogoutTest(TestCase):
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


class UserRegisterTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:register'), '/register/')

    def test_register_view(self):
        response = self.client.get(reverse('tasks:register'))
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_user(self):
        self.assertEqual(auth.models.User.objects.count(), 0)
        response = self.client.post(reverse('tasks:register'), data={
            'username': 'testuser',
            'password1': 'pass',
            'password2': 'pass'}, follow=True)
        self.assertEqual(auth.models.User.objects.count(), 1)
        user = auth.models.User.objects.all()[0]
        self.assertEqual(user.username, 'testuser')
        self.assertTemplateUsed(response, 'tasks/project_list.html')
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertEqual(response.context['user'], user)


class DeleteUserPageTest(ExtTestCase):
    def test_reverse_blog_delete(self):
        self.assertEqual(reverse('tasks:user_delete', args=['test_user']), '/user/test_user/delete/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        # project = Project.objects.create(created_by=creator, name="test_project")
        response = self.client.get(reverse('tasks:user_delete', args=[user.username]))
        self.assertTemplateUsed(response, 'auth/user_confirm_delete.html')

    def test_can_delete_user(self):
        user = self.create_and_log_in_user()
        self.assertEqual(auth.models.User.objects.count(), 1)
        response = self.client.post(reverse('tasks:user_delete', args=[user.username]), {}, follow=True)
        self.assertEqual(auth.models.User.objects.count(), 0)

    def test_404_no_user(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('tasks:user_delete', args=['dummy_user']))
        self.assertTemplateUsed(response, '404.html')

    def test_cant_delete_user_if_not_logged_in(self):
        user = auth.models.User.objects.create(username='user')
        self.assertEqual(auth.models.User.objects.all().count(), 1)
        response = self.client.post(reverse('tasks:user_delete', args=[user.username]), {}, follow=True)
        self.assertEqual(auth.models.User.objects.all().count(), 1)
        self.assertTemplateUsed(response, '404.html')

    def test_cant_delete_other_users(self):
        user = self.create_and_log_in_user()
        other_user = auth.models.User.objects.create(username='other_user')
        self.assertEqual(auth.models.User.objects.all().count(), 2)
        response = self.client.post(reverse('tasks:user_delete', args=[other_user.username]), {}, follow=True)
        self.assertEqual(auth.models.User.objects.all().count(), 2)
        self.assertTemplateUsed(response, '404.html')