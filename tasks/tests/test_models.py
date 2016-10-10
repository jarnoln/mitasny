import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from ext_test_case import ExtTestCase
from tasks.models import Project, Priority, TaskStatus, Phase, Task


class ProjectModelTest(ExtTestCase):
    def test_can_save_and_load(self):
        creator = User.objects.create(username='creator')
        project = Project(name='test_project', created_by=creator)
        project.save()
        self.assertEqual(Project.objects.all().count(), 1)
        self.assertEqual(Project.objects.all()[0], project)

    def test_absolute_url(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.get_absolute_url(), '/project/test_project/')

    def test_convert_to_string(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(str(project), 'test_project')

    def test_total_work_left(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.total_work_left, 0)
        expected_finish_date = datetime.date.today()
        if expected_finish_date.weekday() < 5:
            self.assertEqual(project.finish_date, expected_finish_date)  # Does not work on weekends
        Task.objects.create(project=project, name='task_1', work_left=1, created_by=creator)
        self.assertEqual(project.total_work_left, 1)
        Task.objects.create(project=project, name='task_2', work_left=2, created_by=creator)
        self.assertEqual(project.total_work_left, 3)
        Task.objects.create(project=project, name='task_3', work_left=3, created_by=creator)
        self.assertEqual(project.total_work_left, 6)

    def test_total_work_left_string(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.total_work_left_string, '0 day(s)')
        Task.objects.create(project=project, name='task_1', work_left=1, created_by=creator)
        self.assertEqual(project.total_work_left, 1)
        self.assertEqual(project.total_work_left_string, '1 day(s)')
        Task.objects.create(project=project, name='task_2', work_left=5, created_by=creator)
        self.assertEqual(project.total_work_left, 6)
        self.assertEqual(project.total_work_left_string, '1 week(s), 1 day(s)')
        Task.objects.create(project=project, name='task_3', work_left=20, created_by=creator)
        self.assertEqual(project.total_work_left, 26)
        self.assertEqual(project.total_work_left_string, '1 month(s), 1 week(s), 1 day(s)')

    def test_finish_date(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.total_work_left, 0)
        today = datetime.date.today()
        if today.weekday() < 5:  # Does not work on weekends
            self.assertEqual(project.finish_date, today)

    def test_get_tasks_by_phase(self):
        self.create_default_phases()
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.tasks_by_phase_name('finished').count(), 0)
        self.assertEqual(project.tasks_by_phase_name('ongoing').count(), 0)
        self.assertEqual(project.tasks_by_phase_name('continuing').count(), 0)
        self.assertEqual(project.tasks_by_phase_name('pending').count(), 0)
        self.assertEqual(project.tasks_finished.count(), 0)
        self.assertEqual(project.tasks_ongoing.count(), 0)
        self.assertEqual(project.tasks_continuing.count(), 0)
        self.assertEqual(project.tasks_pending.count(), 0)
        self.assertEqual(project.tasks_unfinished.count(), 0)
        self.assertEqual(project.tasks_not_done.count(), 0)
        self.assertEqual(project.tasks.count(), 0)
        done = Phase.objects.get(name='done')
        finished = Phase.objects.get(name='finished')
        ongoing = Phase.objects.get(name='ongoing')
        continuing = Phase.objects.get(name='continuing')
        pending = Phase.objects.get(name='pending')
        task_1 = Task.objects.create(project=project, name='task_1', work_left=0, created_by=creator, phase=finished)
        self.assertEqual(project.tasks_done.count(), 0)
        self.assertEqual(project.tasks_finished.count(), 1)
        self.assertEqual(project.tasks_ongoing.count(), 0)
        self.assertEqual(project.tasks_pending.count(), 0)
        self.assertEqual(project.impediments.count(), 0)
        self.assertEqual(project.tasks_unfinished.count(), 0)
        self.assertEqual(project.tasks_not_done.count(), 1)
        self.assertEqual(project.tasks.count(), 1)
        self.assertEqual(project.tasks_finished[0], task_1)
        task_2 = Task.objects.create(project=project, name='task_2', work_left=1, created_by=creator, phase=ongoing)
        self.assertEqual(project.tasks_done.count(), 0)
        self.assertEqual(project.tasks_finished.count(), 1)
        self.assertEqual(project.tasks_ongoing.count(), 1)
        self.assertEqual(project.tasks_pending.count(), 0)
        self.assertEqual(project.tasks_unfinished.count(), 1)
        self.assertEqual(project.tasks_not_done.count(), 2)
        self.assertEqual(project.tasks.count(), 2)
        self.assertEqual(project.tasks_ongoing[0], task_2)
        task_3 = Task.objects.create(project=project, name='task_3', work_left=1, created_by=creator, phase=pending)
        self.assertEqual(project.tasks_done.count(), 0)
        self.assertEqual(project.tasks_finished.count(), 1)
        self.assertEqual(project.tasks_ongoing.count(), 1)
        self.assertEqual(project.tasks_pending.count(), 1)
        self.assertEqual(project.tasks_unfinished.count(), 2)
        self.assertEqual(project.tasks_not_done.count(), 3)
        self.assertEqual(project.tasks.count(), 3)
        self.assertEqual(project.tasks_pending[0], task_3)
        task_4 = Task.objects.create(project=project, name='task_4', work_left=1, created_by=creator, phase=done)
        self.assertEqual(project.tasks_done.count(), 1)
        self.assertEqual(project.tasks_finished.count(), 1)
        self.assertEqual(project.tasks_ongoing.count(), 1)
        self.assertEqual(project.tasks_pending.count(), 1)
        self.assertEqual(project.tasks_unfinished.count(), 2)
        self.assertEqual(project.tasks_not_done.count(), 3)
        task_5 = Task.objects.create(project=project, name='task_5', work_left=1, created_by=creator, phase=continuing)
        self.assertEqual(project.tasks_done.count(), 1)
        self.assertEqual(project.tasks_finished.count(), 1)
        self.assertEqual(project.tasks_ongoing.count(), 1)
        self.assertEqual(project.tasks_continuing.count(), 1)
        self.assertEqual(project.tasks_pending.count(), 1)
        self.assertEqual(project.tasks_unfinished.count(), 3)
        self.assertEqual(project.tasks_not_done.count(), 4)
        self.assertEqual(project.tasks.count(), 5)
        self.assertEqual(project.tasks_by_phase_name('finished').count(), 1)
        self.assertEqual(project.tasks_by_phase_name('ongoing').count(), 1)
        self.assertEqual(project.tasks_by_phase_name('continuing').count(), 1)
        self.assertEqual(project.tasks_by_phase_name('pending').count(), 1)
        self.assertEqual(project.tasks_by_phase_name('done').count(), 1)

    def test_get_impediments(self):
        self.create_default_phases()
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        self.assertEqual(project.tasks_by_phase_name('impediment').count(), 0)
        self.assertEqual(project.impediments.count(), 0)
        impediment = Phase.objects.get(name='impediment')
        task_1 = Task.objects.create(project=project, name='impediment', work_left=0, created_by=creator, phase=impediment)
        self.assertEqual(project.tasks_by_phase_name('impediment').count(), 1)
        self.assertEqual(project.impediments.count(), 1)
        self.assertEqual(project.tasks_unfinished.count(), 0)


class PriorityModelTest(TestCase):
    def test_can_save_and_load(self):
        priority = Priority(name='critical', title='Critical')
        priority.save()
        self.assertEqual(Priority.objects.all().count(), 1)
        self.assertEqual(Priority.objects.all()[0], priority)


class TaskStatusModelTest(TestCase):
    def test_can_save_and_load(self):
        status = TaskStatus(name='ongoing', title='Ongoing')
        status.save()
        self.assertEqual(TaskStatus.objects.all().count(), 1)
        self.assertEqual(TaskStatus.objects.all()[0], status)


class PhaseModelTest(TestCase):
    def test_can_save_and_load(self):
        phase = Phase(name='ongoing', title='Ongoing')
        phase.save()
        self.assertEqual(Phase.objects.all().count(), 1)
        self.assertEqual(Phase.objects.all()[0], phase)

    def test_convert_to_string(self):
        phase = Phase.objects.create(name='ongoing', title='Ongoing', order=2)
        # self.assertEqual(str(phase), '2:ongoing:Ongoing')
        self.assertEqual(str(phase), 'Ongoing')


class TaskModelTest(TestCase):
    def test_can_save_and_load(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task = Task(project=project, name='test_task', title='Test task', created_by=creator)
        task.save()
        self.assertEqual(Task.objects.all().count(), 1)
        self.assertEqual(Task.objects.all()[0], task)

    def test_absolute_url(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task = Task.objects.create(project=project, name='test_task', title='Test task', created_by=creator)
        self.assertEqual(task.get_absolute_url(), '/project/test_project/task/test_task/')

    def test_convert_to_string(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task = Task.objects.create(project=project, name='test_task', title='Test task', created_by=creator)
        self.assertEqual(str(task), 'test_project:test_task')

    def test_work_left_list(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task = Task.objects.create(project=project, order=1, name='task_1', work_left=0, created_by=creator)
        self.assertEqual(task.work_left_list, [])
        task.work_left = 1
        task.save()
        self.assertEqual(len(task.work_left_list), 1)
        task.work_left = 2
        task.save()
        self.assertEqual(len(task.work_left_list), 2)
        task.work_left = 1337
        task.save()
        self.assertEqual(len(task.work_left_list), 1337)

    def test_cumulative_work_left(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task_1 = Task.objects.create(project=project, order=1, name='task_1', work_left=1, created_by=creator)
        self.assertEqual(task_1.cumulative_work_before, 0)
        self.assertEqual(task_1.cumulative_work_before_list, [])
        self.assertEqual(task_1.cumulative_work_left, 1)
        task_3 = Task.objects.create(project=project, order=3, name='task_3', work_left=2, created_by=creator)
        self.assertEqual(task_3.cumulative_work_before, 1)
        self.assertEqual(len(task_3.cumulative_work_before_list), 1)
        self.assertEqual(task_3.cumulative_work_left, 3)
        task_2 = Task.objects.create(project=project, order=2, name='task_2', work_left=3, created_by=creator)
        self.assertEqual(task_2.cumulative_work_before, 1)
        self.assertEqual(task_2.cumulative_work_left, 4)
        self.assertEqual(task_3.cumulative_work_before, 4)
        self.assertEqual(len(task_3.cumulative_work_before_list), 4)
        self.assertEqual(task_3.cumulative_work_left, 6)

    def test_finish_date(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task_1 = Task.objects.create(project=project, order=1, name='task_1', work_left=0, created_by=creator)
        today = datetime.date.today()
        if today.weekday() < 5:    # Does not work on weekends
            self.assertEqual(task_1.finish_date, today)

    def test_set_phase(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task = Task.objects.create(project=project, order=1, name='task_1', work_left=0, created_by=creator)
        self.assertEqual(task.phase, None)
        phase = Phase.objects.create(name='ongoing', title='Ongoing', order=2)
        task.set_phase('ongoing')
        self.assertEqual(task.phase, phase)

    def test_warnings(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        ongoing = Phase.objects.create(name='ongoing', title='Ongoing')
        finished = Phase.objects.create(name='finished', title='Finished')
        done = Phase.objects.create(name='done', title='Done')
        task = Task.objects.create(project=project, order=1, name='task_1', work_left=1, created_by=creator, phase=ongoing)
        self.assertEqual(task.warnings, '')
        task.set_phase('finished')
        self.assertEqual(task.warnings, 'Task has remaining work: 1')
        task.set_phase('done')
        self.assertEqual(task.warnings, 'Task has remaining work: 1')

    def test_next_and_previous(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task_1 = Task.objects.create(project=project, order=1, name='task_1', created_by=creator)
        self.assertEqual(task_1.next, None)
        self.assertEqual(task_1.prev, None)
        task_2 = Task.objects.create(project=project, order=2, name='task_2', created_by=creator)
        self.assertEqual(task_1.prev, None)
        self.assertEqual(task_1.next, task_2)
        self.assertEqual(task_2.prev, task_1)
        self.assertEqual(task_2.next, None)
        task_0 = Task.objects.create(project=project, order=0, name='task_0', created_by=creator)
        self.assertEqual(task_0.prev, None)
        self.assertEqual(task_0.next, task_1)
        self.assertEqual(task_1.prev, task_0)
        self.assertEqual(task_1.next, task_2)

    def test_move_up(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task_1 = Task.objects.create(project=project, order=1, name='task_1', created_by=creator)
        is_success = task_1.move_up()
        self.assertFalse(is_success)
        task_2 = Task.objects.create(project=project, order=2, name='task_2', created_by=creator)
        self.assertEqual(task_1.next, task_2)
        self.assertEqual(task_2.prev, task_1)
        is_success = task_2.move_up()
        self.assertTrue(is_success)
        task_1 = Task.objects.get(name='task_1')
        task_2 = Task.objects.get(name='task_2')
        self.assertEqual(task_1.order, 2)
        self.assertEqual(task_2.order, 1)
        self.assertEqual(task_2.next, task_1)
        self.assertEqual(task_1.prev, task_2)
        is_success = task_2.move_up()
        self.assertFalse(is_success)
        self.assertEqual(task_1.order, 2)
        self.assertEqual(task_2.order, 1)

    def test_move_down(self):
        creator = User.objects.create(username='creator')
        project = Project.objects.create(name='test_project', created_by=creator)
        task_1 = Task.objects.create(project=project, order=1, name='task_1', created_by=creator)
        is_success = task_1.move_down()
        self.assertFalse(is_success)
        task_2 = Task.objects.create(project=project, order=2, name='task_2', created_by=creator)
        self.assertEqual(task_1.next, task_2)
        self.assertEqual(task_2.prev, task_1)
        is_success = task_1.move_down()
        self.assertTrue(is_success)
        task_1 = Task.objects.get(name='task_1')
        task_2 = Task.objects.get(name='task_2')
        self.assertEqual(task_1.order, 2)
        self.assertEqual(task_2.order, 1)
        self.assertEqual(task_2.next, task_1)
        self.assertEqual(task_1.prev, task_2)
        is_success = task_1.move_down()
        self.assertFalse(is_success)
        self.assertEqual(task_1.order, 2)
        self.assertEqual(task_2.order, 1)