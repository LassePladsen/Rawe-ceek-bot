import numpy as np
import fastf1               # f1 api
from datetime import date
import calendar

today = date.today()
Race_schedule = fastf1.get_event_schedule(today.year, include_testing=False)

def day_string_formatting(day):
    """Gives a string containing a day number formatted like, for example; '05' instead of '5'.
    Does nothing if the day number is equal to or above 10. Argument can be int or str."""
    day = int(day)
    if day < 10:
        return "0" + str(day)
    else:
        return str(day)

def get_sunday_date(Date):
    """Returns a string with sundays date of the same week as the given date.
    Input date must be a datetime.date object."""

    weekday = date.weekday(Date)  # the weekday number of the week beginning at 0 (monday)
    days_until_sunday = 6 - weekday

    # Create new day date and fix the formatting (f.ex 07 instead of 7)
    new_day = int(str(Date)[-2:]) + days_until_sunday
    new_day = day_string_formatting(new_day)


    date_sunday = str(Date)[:-2] + new_day

    # Roll over to next month if day number exceeds days in the given month:
    days_in_month = calendar.monthrange(Date.year, Date.month)[1]
    if int(date_sunday[-2:]) > days_in_month:
        # Find new day number
        days_exceeded = int(date_sunday[-2:]) - days_in_month
        new_day = day_string_formatting(days_exceeded)    # format day number
        date_sunday = date_sunday[:-2] + new_day   # roll to new day number

        date_sunday = date_sunday.replace(str(Date.month), str(Date.month + 1))  # roll to next month
    return date_sunday

def get_week_event(Date):
    """Returns the fastf1 event object for the week of the given date.
    Returns None if there is no event in that week.
    Input date must be a datetime.date object."""
    sunday_date = get_sunday_date(Date)

    race_dates = np.asarray(Race_schedule["EventDate"].to_string(index=False).split()) # array of all season race dates
    if sunday_date in race_dates:
        race_index = np.where(sunday_date == race_dates)[0][0] + 1
        return fastf1.get_event(Date.year, race_index)

    else:# If the given date is not a race week
        return None

def check_race_week():
    """Boolean check for it todays week is a race week."""
    if get_week_event(today) is not None:
        return True
    else:
        return False

def check_sprint_session(Event):
    """Boolean check if the race event has a sprint session.
    Input event must be a fastf1.Event object."""
    try:
        Event.get_sprint()
        return True
    except ValueError:
        return False

def sort_sessions_by_day(Event):
    """Returns three lists for friday, saturday, and sunday containing the sessions of each day."""
    # Initialize lists of sessions to sort
    friday = []
    saturday = []
    sunday = []

    Q_session = Event.get_qualifying()
    R_session = Event.get_race()

    # Get the two sprint sessions if the race week includes a sprint:
    if check_sprint_session(Event):
        SPQ_session = Event.get_sprint_shootout()
        SP_session = Event.get_sprint()

        friday.append(Q_session)
        saturday.append(SPQ_session)
        saturday.append(SP_session)
    else:
        saturday.append(Q_session)

    sunday.append(R_session)

    return friday,saturday,sunday


# DEBUGGING/TESTING:
if __name__ == "__main__":
    Event = get_week_event(today)
    Event = get_week_event(date(2023,4,25))
