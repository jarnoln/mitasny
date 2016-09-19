import datetime
from django.test import TestCase
from tasks.calculate_finish_date import calculate_finish_date


class CalculateFinishDateTest(TestCase):
    def test_add_zero(self):
        start_date = datetime.date.today()
        finish_date = calculate_finish_date(start_date, 0)
        self.assertEqual(start_date, finish_date)

    def test_add_one(self):
        start_date = datetime.date(2016, 9, 19)
        finish_date = calculate_finish_date(start_date, 1)
        self.assertEqual(finish_date, datetime.date(2016, 9, 20))

    def test_skips_over_weekend(self):
        start_date = datetime.date(2016, 9, 23)
        self.assertEqual(start_date.weekday(), 4) # Friday
        finish_date = calculate_finish_date(start_date, 1)
        self.assertEqual(finish_date, datetime.date(2016, 9, 26))
        self.assertEqual(finish_date.weekday(), 0) # Monday

    def test_add_five_ends_up_with_same_weekday(self):
        start_date = datetime.date.today()
        finish_date = calculate_finish_date(start_date, 5)
        self.assertEqual(start_date.weekday(), finish_date.weekday())

    def test_can_handle_month_change(self):
        start_date = datetime.date(2016, 9, 30)  # Last day of month (Friday)
        self.assertEqual(start_date.weekday(), 4)  # Friday
        finish_date = calculate_finish_date(start_date, 1)
        self.assertEqual(finish_date, datetime.date(2016, 10, 3))
        self.assertEqual(finish_date.weekday(), 0) # Monday
