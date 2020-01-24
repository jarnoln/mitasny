from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib import auth
from .ext_test_case import ExtTestCase


class UserListTest(ExtTestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:users'), '/users/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('tasks:users'))
        self.assertTemplateUsed(response, 'tasks/tasks_base.html')
        self.assertTemplateUsed(response, 'auth/user_list.html')

    def test_default_context(self):
        response = self.client.get(reverse('tasks:users'))
        self.assertEqual(response.context['user_list'].count(), 0)
        user_1 = auth.models.User.objects.create(username='user_1')
        response = self.client.get(reverse('tasks:users'))
        self.assertEqual(response.context['user_list'].count(), 1)
        self.assertEqual(response.context['user_list'][0], user_1)
        self.assertContains(response, user_1.username)
        user_2 = auth.models.User.objects.create(username='user_2')
        response = self.client.get(reverse('tasks:users'))
        self.assertEqual(response.context['user_list'].count(), 2)


class UserPageTest(ExtTestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:user', args=['test_user']), '/user/test_user/')

    def test_uses_correct_template(self):
        user = auth.models.User.objects.create(username='test_user')
        response = self.client.get(reverse('tasks:user', args=[user.username]))
        self.assertTemplateUsed(response, 'auth/user_detail.html')

    def test_default_context(self):
        user = auth.models.User.objects.create(username='test_user')
        response = self.client.get(reverse('tasks:user', args=[user.username]))
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['message'], '')
        self.assertEqual(response.context['can_edit'], False)

    def test_404_not_found(self):
        response = self.client.get(reverse('tasks:user', args=['missing_user']))
        self.assertTemplateUsed(response, '404.html')


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
        user_model = auth.get_user_model()
        self.assertEqual(user_model.objects.count(), 0)
        response = self.client.post(reverse('tasks:register'), data={
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123'}, follow=True)
        self.assertEqual(user_model.objects.count(), 1)
        user = user_model.objects.all()[0]
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertEqual(response.context['user'], user)
        self.assertTemplateUsed(response, 'auth/user_form.html')


class UpdateUserTest(ExtTestCase):
    def test_reverse_task_edit(self):
        self.assertEqual(reverse('tasks:user_update', args=['test_user']),
                         '/user/test_user/edit/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('tasks:user_update', args=[user.username]))
        self.assertTemplateUsed(response, 'auth/user_form.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('tasks:user_update', args=[user.username]))
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['message'], '')

    def test_can_update_user(self):
        user = self.create_and_log_in_user()
        response = self.client.post(reverse('tasks:user_update', args=[user.username]), {
            'username': 'batman',
            'email': 'bruce@waynetech.com',
            'first_name': 'Bruce',
            'last_name': 'Wayne'
        }, follow=True)
        self.assertEqual(auth.models.User.objects.all().count(), 1)
        user = auth.models.User.objects.all()[0]
        self.assertEqual(user.email, 'bruce@waynetech.com')
        self.assertEqual(user.first_name, 'Bruce')
        self.assertEqual(user.last_name, 'Wayne')
        self.assertTemplateUsed(response, 'auth/user_detail.html')

    def test_cant_update_user_if_not_logged_in(self):
        user = auth.models.User.objects.create(username='user', email='user@default.com')
        response = self.client.post(reverse('tasks:user_update', args=[user.username]),
                                    {'username': 'batman', 'email': 'bruce@waynetech.com' },
                                    follow=True)
        self.assertEqual(auth.models.User.objects.all().count(), 1)
        user = auth.models.User.objects.all()[0]
        self.assertEqual(user.email, 'user@default.com')
        self.assertTemplateUsed(response, '404.html')

    def test_cant_update_other_users(self):
        logged_user = self.create_and_log_in_user()
        other_user = auth.models.User.objects.create(username='other', email='other@default.com')
        self.assertEqual(auth.models.User.objects.all().count(), 2)
        response = self.client.post(reverse('tasks:user_update', args=[other_user.username]),
                                    {'username': 'other', 'email': 'bruce@waynetech.com' },
                                    follow=True)
        self.assertEqual(auth.models.User.objects.all().count(), 2)
        user = auth.models.User.objects.get(username='other')
        self.assertEqual(user.email, 'other@default.com')
        self.assertTemplateUsed(response, '404.html')


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
