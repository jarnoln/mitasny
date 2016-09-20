import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User
from calculate_finish_date import calculate_finish_date


class Project(models.Model):
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_projects')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, null=True, related_name='edited_projects')

    @property
    def total_work_left(self):
        if self.tasks.count() == 0:
            return 0

        sum_dict = self.tasks.aggregate(models.Sum('work_left'))
        return sum_dict['work_left__sum']

    @property
    def finish_date(self):
        days_left = self.total_work_left
        start_date = datetime.date.today()
        return calculate_finish_date(start_date, days_left)

    def can_edit(self, user):
        if user == self.created_by:
            return True

        return False

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tasks:project', args=[self.name])


class Priority(models.Model):
    # Idea, Nice(to have), Minor, Normal, Major, Critical
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URLs.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    order = models.PositiveSmallIntegerField(default=0)


class TaskStatus(models.Model):
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URLs.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    order = models.PositiveSmallIntegerField(default=0)


class Phase(models.Model):
    # Blocked, Pending, Ongoing, (Recently)Finished, Done
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URLs.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    order = models.PositiveSmallIntegerField(default=0)
    element_class = models.CharField(default='', blank=True, max_length=250)  # CSS class to be used in HTML

    def __unicode__(self):
        return '%d:%s:%s' % (self.order, self.name, self.title)


    class Meta:
        ordering = ['order', 'title']


class Task(models.Model):
    project = models.ForeignKey(Project, null=False, related_name='tasks')
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('task'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    order = models.PositiveSmallIntegerField(default=0)
    priority = models.ForeignKey(Priority, null=True)
    phase = models.ForeignKey(Phase, null=True, blank=True)
    # status = models.ForeignKey(TaskStatus, null=True)
    owner = models.ForeignKey(User, null=True, related_name='tasks')
    work_done = models.PositiveSmallIntegerField(default=0)
    work_left = models.PositiveSmallIntegerField(default=1) #, help_text=ugettext_lazy('days'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_tasks')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, null=True, related_name='edited_tasks')

    @property
    def cumulative_work_left(self):
        preceding_tasks = Task.objects.filter(project=self.project, order__lt=self.order)
        if preceding_tasks.count() == 0:
            return self.work_left

        sum_dict = preceding_tasks.aggregate(models.Sum('work_left'))
        sum_value = sum_dict['work_left__sum']
        return sum_value + self.work_left

    @property
    def finish_date(self):
        days_left = self.cumulative_work_left
        start_date = datetime.date.today()
        return calculate_finish_date(start_date, days_left)

    def can_edit(self, user):
        if user == self.created_by or user == self.owner or user == self.project.created_by:
            return True

        return False

    def __unicode__(self):
        return '%s:%s' % (self.project.name, self.name)

    def get_absolute_url(self):
        return reverse('tasks:task', args=[self.project.name, self.name])

    def get_edit_url(self):
        return reverse('tasks:task_update', args=[self.project.name, self.name])

    class Meta:
        ordering = ['order', 'title']
