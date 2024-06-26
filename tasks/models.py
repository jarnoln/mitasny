import datetime
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User
from .calculate_finish_date import calculate_finish_date


class Project(models.Model):
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_projects', on_delete=models.CASCADE)
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, null=True, related_name='edited_projects', on_delete=models.CASCADE)

    @property
    def total_work_left(self):
        if self.tasks.count() == 0:
            return 0

        sum_dict = self.tasks.aggregate(models.Sum('work_left'))
        return sum_dict['work_left__sum']

    @property
    def total_work_left_list(self):
        day_list = []
        total_work = self.total_work_left
        if total_work == 0:
            return day_list

        day = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        for i in range(0, self.total_work_left):
            day_list.append(day)
            day += one_day
            if day.weekday() == 5:
                day += one_day
            if day.weekday() == 6:
                day += one_day

        return day_list

    @property
    def total_work_left_weeks_list(self):
        return range(0, self.total_work_left / 5)

    @property
    def total_work_left_string(self):
        days = self.total_work_left
        weeks = int(days / 5)
        days = days % 5
        months = int(weeks / 4)
        weeks = weeks % 4
        if months > 0:
            return '%d month(s), %d week(s), %d day(s)' % (months, weeks, days)
        elif weeks > 0:
            return '%d week(s), %d day(s)' % (weeks, days)
        else:
            return '%d day(s)' % days

    @property
    def finish_date(self):
        days_left = self.total_work_left
        start_date = datetime.date.today()
        return calculate_finish_date(start_date, days_left)

    def can_edit(self, user):
        if user == self.created_by:
            return True
        return False

    def tasks_by_phase(self, phase):
        return Task.objects.filter(project=self, phase=phase).order_by('order')

    def tasks_by_phase_name(self, phase_name):
        phases = Phase.objects.filter(name=phase_name)
        if phases.count() == 1:
            phase = phases.first()
            return self.tasks_by_phase(phase)
        return Task.objects.none()

    @property
    def tasks_done(self):
        return self.tasks_by_phase_name('done')

    @property
    def tasks_finished(self):
        return self.tasks_by_phase_name('finished')

    @property
    def tasks_ongoing(self):
        return self.tasks_by_phase_name('ongoing')

    @property
    def tasks_continuing(self):
        return self.tasks_by_phase_name('continuing')

    @property
    def tasks_pending(self):
        return self.tasks_by_phase_name('pending')

    @property
    def impediments(self):
        return self.tasks_by_phase_name('impediment')

    @property
    def tasks_unfinished(self):
        excluded_phases = ['finished', 'done', 'impediment']
        tasks = Task.objects.filter(project=self)
        for phase_name in excluded_phases:
            tasks = tasks.exclude(phase__name=phase_name)

        return tasks

    @property
    def tasks_not_done(self):
        done = Phase.objects.get(name='done')
        return Task.objects.filter(project=self).exclude(phase=done)

    @property
    def tasks_last_week(self):
        finished_or_continuing = models.Q(phase__name='finished') | models.Q(phase__name='continuing')
        tasks = Task.objects.filter(project=self).filter(finished_or_continuing)
        return tasks

    @property
    def tasks_this_week(self):
        ongoing_or_continuing = models.Q(phase__name='ongoing') | models.Q(phase__name='continuing')
        tasks = Task.objects.filter(project=self).filter(ongoing_or_continuing)
        return tasks

    def __str__(self):
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

    def __str__(self):
        # return '%d:%s:%s' % (self.order, self.name, self.title)
        return self.title

    class Meta:
        ordering = ['order', 'title']


class Task(models.Model):
    project = models.ForeignKey(Project, null=False, related_name='tasks', on_delete=models.CASCADE)
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('task'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    order = models.PositiveSmallIntegerField(default=0)
    priority = models.ForeignKey(Priority, null=True, on_delete=models.CASCADE)
    phase = models.ForeignKey(Phase, null=True, blank=True, on_delete=models.CASCADE)
    # status = models.ForeignKey(TaskStatus, null=True)
    owner = models.ForeignKey(User, null=True, related_name='tasks', on_delete=models.CASCADE)
    work_done = models.PositiveSmallIntegerField(default=0)
    work_left = models.PositiveSmallIntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, null=True, related_name='edited_tasks', on_delete=models.CASCADE)

    @property
    def work_left_list(self):
        """ List with as many items as days of work left. For looping in templates """
        if self.work_left > 0:
            return range(0, self.work_left)
        else:
            return []

    @property
    def cumulative_work_before(self):
        """ How many days of work in tasks before this one """
        preceding_tasks = Task.objects.filter(project=self.project, order__lt=self.order)
        if preceding_tasks.count() == 0:
            return 0

        sum_dict = preceding_tasks.aggregate(models.Sum('work_left'))
        sum_value = sum_dict['work_left__sum']
        return sum_value

    @property
    def cumulative_work_before_list(self):
        """ List with as many items as days of work left. For looping in templates """
        if self.cumulative_work_before > 0:
            return range(0, self.cumulative_work_before)
        else:
            return []

    @property
    def cumulative_work_left(self):
        """ How many days of work until this and all the previous tasks are done """
        return self.cumulative_work_before + self.work_left

    @property
    def finish_date(self):
        days_left = self.cumulative_work_left
        start_date = datetime.date.today()
        return calculate_finish_date(start_date, days_left)

    @property
    def next(self):
        following_tasks = Task.objects.filter(project=self.project, order__gt=self.order).order_by('order')
        if following_tasks.count() == 0:
            return None
        else:
            return following_tasks.first()

    @property
    def prev(self):
        preceding_tasks = Task.objects.filter(project=self.project, order__lt=self.order).order_by('-order')
        if preceding_tasks.count() == 0:
            return None
        else:
            return preceding_tasks.first()

    @property
    def warnings(self):
        if self.phase:
            if self.phase.name == 'finished' or self.phase.name == 'done':
                if self.work_left > 0:
                    return "Task has remaining work: %d" % self.work_left
        return ''


    @property
    def next_phase_url(self):
        if self.phase:
            if self.phase.name == 'pending':
                url = reverse('tasks:task_set_phase_to', args=[self.project.name, self.name, 'ongoing'])
                return { 'title': 'Start', 'url': url}
            elif self.phase.name == 'ongoing' or self.phase.name == 'continuing':
                url = reverse('tasks:task_set_phase_to', args=[self.project.name, self.name, 'finished'])
                return { 'title': 'Finish', 'url': url}
            elif self.phase.name == 'finished':
                url = reverse('tasks:task_set_phase_to', args=[self.project.name, self.name, 'done'])
                return { 'title': 'Archive', 'url': url}
        return None

    def can_edit(self, user):
        if user == self.created_by or user == self.owner or user == self.project.created_by:
            return True

        return False

    def set_phase(self, phase_name):
        phases = Phase.objects.filter(name=phase_name)
        if phases.count() == 1:
            self.phase = phases.first()
            self.save()

    def switch_with(self, task):
        old_order = self.order
        self.order = task.order
        task.order = old_order
        task.save()
        self.save()

    def move_up(self):
        prev_task = self.prev
        if not prev_task:
            return False

        self.switch_with(prev_task)
        return True

    def move_down(self):
        next_task = self.next
        if not next_task:
            return False

        self.switch_with(next_task)
        return True

    def __str__(self):
        return '%s:%s' % (self.project.name, self.name)

    def get_absolute_url(self):
        return reverse('tasks:task', args=[self.project.name, self.name])

    def get_edit_url(self):
        return reverse('tasks:task_update', args=[self.project.name, self.name])

    class Meta:
        ordering = ['order', 'title']
