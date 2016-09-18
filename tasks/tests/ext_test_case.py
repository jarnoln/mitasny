from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class ExtTestCase(TestCase):
    def create_and_log_in_user(self):
        user = User.objects.create(username='test_user', email='tuser@iki.fi')
        user.set_password('pw')
        user.save()
        self.client.post(reverse('login'), {'username': user.username, 'password': 'pw'})
        return user
