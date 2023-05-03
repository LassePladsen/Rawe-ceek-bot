import numpy as np
import fastf1               # f1 api
import datetime as dt       # time and dates
import calendar             # used to find number of days in a certain month

today = dt.date.today()
Race_schedule = fastf1.get_event_schedule(today.year, include_testing=False)

def day_string_formatting(day):
    """Gives a string containing a day number formatted like, for example; '05' instead of '5'.
    Does nothing if the day number is equal to or above 10. Argument can be int or str."""
    day = int(day)
    if day < 10:
        return "0" + str(day)
    else:
        return str(day)

def get_sunday_date(date):
    """Returns a string with sundays date of the same week as the given date.
    Input date must be a datetime.datetime object."""

    weekday = dt.date.weekday(date)  # the weekday number of the week beginning at 0 (monday)
    days_until_sunday = 6 - weekday

    # Create new day date and fix the formatting (f.ex 07 instead of 7)
    new_day = int(str(date)[-2:]) + days_until_sunday
    new_day = day_string_formatting(new_day)


    date_sunday = str(date)[:-2] + new_day

    # Roll over to next month if day number exceeds days in the given month:
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    if int(date_sunday[-2:]) > days_in_month:
        # Find new day number
        days_exceeded = int(date_sunday[-2:]) - days_in_month
        new_day = day_string_formatting(days_exceeded)    # format day number
        date_sunday = date_sunday[:-2] + new_day   # roll to new day number

        date_sunday = date_sunday.replace(str(date.month), str(date.month + 1))  # roll to next month
    return date_sunday

def get_week_event(date, printerror=True):
    """Returns the fastf1 event object for the week of the given date.
    Returns None if there is no event in that week."""
    sunday_date = get_sunday_date(date)

    race_dates = np.asarray(Race_schedule["EventDate"].to_string(index=False).split()) # array of all season race dates
    if sunday_date in race_dates:
        race_index = np.where(sunday_date == race_dates)[0][0] + 1
        return fastf1.get_event(date.year, race_index)

    # If the given date is not a race week
    if printerror:
        print(f"Error in 'get_week_event()': given date '{date}' is not a race week.")
    return None

def check_race_week(prnt=False):
    """Simple boolean check for it todays week is a race week.
    If 'print' is true and its a race week: prints 'RAWE CEEK!'."""
    if get_week_event(today) is not None:
        result = True
    else:
        result = False

    if prnt and result:
        print("RAWE CEEK!")
    return result



