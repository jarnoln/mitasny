from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User


# Create your models here.
class Project(models.Model):
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_projects')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, null=True, related_name='edited_projects')

    def can_edit(self, user):
        if user == self.created_by:
            return True

        return False

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tasks:project', args=[self.name])
