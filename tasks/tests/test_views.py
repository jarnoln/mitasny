from django.test import TestCase
from django.urls import reverse


class HomePageTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:home'), '/')

    def test_default_content(self):
        response = self.client.get(reverse('tasks:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')
