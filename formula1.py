import numpy as np
import fastf1       # f1 api
from datetime import date,datetime
import calendar

import util

today = date.today()
Race_schedule = fastf1.get_event_schedule(today.year, include_testing=False)

def get_week_event(Date):
    """Returns the fastf1 event object for the week of the given date.
    Returns None if there is no event in that week.
    Input date must be a datetime.date object."""
    sunday_date = util.get_sunday_date(Date)

    race_dates = np.asarray(Race_schedule["EventDate"].to_string(index=False).split()) # array of all season race dates
    if sunday_date in race_dates:
        race_index = np.where(sunday_date == race_dates)[0][0] + 1
        return fastf1.get_event(Date.year, race_index)

    else:# If the given date is not a race week
        return None

def get_next_week_event(Date):
    """Returns the next race week event from a given date"""
    dates = get_remaining_dates(Date)
    sunday = util.get_sunday_date(Date)

    if check_race_week(Date):
        return get_week_event(Date)

    while sunday not in dates:
        # Increase week by 1 and check again
        sunday = sunday[:-2] + str(int(sunday[-2:]) + 7)

        # Roll over to next month if day number exceeds days in the given month:
        days_in_month = calendar.monthrange(Date.year, Date.month)[1]
        if int(sunday[-2:]) > days_in_month:
            # Find new day number
            days_exceeded = int(sunday[-2:]) - days_in_month
            new_day = util.day_string_formatting(days_exceeded)  # format day number
            sunday = sunday[:-2] + new_day  # roll to new day number

            sunday = sunday.replace(str(Date.month), str(Date.month + 1))
    return get_week_event(util.make_Date(sunday))


def get_remaining_dates(Date):
    dt = datetime.combine(Date, datetime.min.time())
    Remaining_schedule = fastf1.get_events_remaining(dt, include_testing=False)
    dates = str(Remaining_schedule["EventDate"]).split("\n")    # get list of column strings
    dates = [i.split(" ")[-1] for i in dates]   # seperate the dates in the string with column numbers
    return dates

def check_race_week(Date,old_implementation=False):
    """Boolean return for if the given date is a f1 race week."""
    if old_implementation:
        if get_week_event(Date) is not None:
            return True
        else:
            return False
    else:
        Sunday = util.get_sunday_Date(Date)
        dates = get_remaining_dates(Date)
        return str(Sunday) in dates

def check_sprint_session(Event):
    """Boolean check if a race event has a f1 sprint session.
    Input event must be a fastf1.Event object."""
    try:
        Event.get_sprint()
        return True
    except ValueError:
        return False

def sort_sessions_by_day(Event):
    """Returns a dictionary mapping days to list containing all f1 fastf1.Session objects
     for the corresponding days"""
    # Initialize the dictionary
    session_days = {"Friday":[],"Saturday":[],"Sunday":[]}

    Q_session = Event.get_qualifying()
    R_session = Event.get_race()

    # Qualifying is friday if there is a sprint race, else it is saturday
    # Get the two sprint sessions if the race week includes a sprint:
    if check_sprint_session(Event):
        SPQ_session = Event.get_sprint_shootout()
        SP_session = Event.get_sprint()

        session_days["Friday"].append(Q_session)
        session_days["Saturday"].append(SPQ_session)
        session_days["Saturday"].append(SP_session)
    else:
        session_days["Saturday"].append(Q_session)

    session_days["Sunday"].append(R_session)    # Race is always sunday

    return session_days

def print_event_info(Event,upper_case=True,discord_format="__**"):
    """Prints name and date for given race event, must be fastf1.Event object.
    Supports discord formatting given as optional argument."""
    name = Event["EventName"]
    if upper_case:
        name = name.upper()
    date = str(Event["EventDate"])[:10]

    # Extract month number, find the month name, and translate to Norwegian
    month = util.month_to_norwegian(calendar.month_name[int(date[5:7])])

    end_day = str(int(date[-2:])) # gets rid of the leading zero if the day number is < 10
    start_day = str(int(end_day)-2)

    out_date = start_day + "-" + end_day + " " + month

    if discord_format is not None:
        # Print with given discord formatting
        return f"{discord_format}{name} {out_date}{discord_format[::-1]}\n"
    else: # Print without
        return f"{name} {out_date}\n"

