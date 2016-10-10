from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from tasks import models


class ExtTestCase(TestCase):
    def create_and_log_in_user(self):
        user = User.objects.create(username='test_user', email='tuser@iki.fi')
        user.set_password('pw')
        user.save()
        self.client.post(reverse('login'), {'username': user.username, 'password': 'pw'})
        return user

    def create_default_phases(self):
        models.Phase.objects.create(name='pending', title='Pending', order=1)  # First of order is the initial phase
        models.Phase.objects.create(name='ongoing', title='Ongoing', order=2)
        models.Phase.objects.create(name='continuing', title='Continuing', order=3)
        models.Phase.objects.create(name='finished', title='Finished', order=4)
        models.Phase.objects.create(name='done', title='Done', order=5)
        models.Phase.objects.create(name='blocked', title='Blocked', order=6)
        models.Phase.objects.create(name='impediment', title='Impediment', order=7)
        self.assertEqual(models.Phase.objects.all().count(), 7)
