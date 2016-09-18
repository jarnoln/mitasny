from django.test import TestCase
from django.core.urlresolvers import reverse


class ProjectListTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('tasks:projects'), '/projects/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('tasks:projects'))
        self.assertTemplateUsed(response, 'tasks/project_list.html')

    def test_default_content(self):
        response = self.client.get(reverse('tasks:projects'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')
