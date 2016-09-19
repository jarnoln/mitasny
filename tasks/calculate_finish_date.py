import datetime


def calculate_finish_date(start_date, days_of_work):
    # Calculate when a task is finished
    # -it is started on start_date
    # -it requires days_of_work
    # and working only from Mon to Fri
    one_day = datetime.timedelta(days=1)
    # If start date is Sat or Sun, fast forward to Mon
    if start_date.weekday() == 5:
        start_date += one_day
    if start_date.weekday() == 6:
        start_date += one_day

    finish_date = start_date
    for day in range(0, days_of_work):
        finish_date += one_day
        if finish_date.weekday() == 6:  # Sunday. add one extra day to skip to Monday
            finish_date += one_day
        elif finish_date.weekday() == 5: # Saturday, add two extra days to skip to Monday
            finish_date += one_day
            finish_date += one_day
    return finish_date
