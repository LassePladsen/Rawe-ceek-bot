import calendar
from datetime import date, datetime

import fastf1  # f1 api
import numpy as np

import util

fastf1.set_log_level('ERROR')  # lower log level to remove "default cache enabled" warning

def get_week_event(date_:"datetime.date"):
    """Returns the fastf1 event object for the week of the given date.
    Returns None if there is no event in that week.
    Input date must be a datetime.date object."""
    sunday_date = util.get_sunday_date_str(date_)

    TODAY = date.today()
    Race_schedule = fastf1.get_event_schedule(TODAY.year, include_testing=False)

    race_dates = np.asarray(Race_schedule["EventDate"].to_string(index=False).split())
    if sunday_date in race_dates:
        race_index = np.where(sunday_date == race_dates)[0][0] + 1
        return fastf1.get_event(date_.year, race_index)

    else:# If the given date is not a race week
        return None

def get_next_week_event(date_:"datetime.date"):
    """Returns the next race week event from a given date"""
    dates = get_remaining_dates(date_)
    sunday = util.get_sunday_date_str(date_)

    if check_race_week(date_):
        return get_week_event(date_)

    while sunday not in dates:
        # Increase week by 1 and check again
        sunday = sunday[:-2] + str(int(sunday[-2:]) + 7)

        # Roll over to next month if day number exceeds days in the given month:
        days_in_month = calendar.monthrange(date_.year, date_.month)[1]
        if int(sunday[-2:]) > days_in_month:
            # Find new day number
            days_exceeded = int(sunday[-2:]) - days_in_month
            new_day = util.day_string_formatting(days_exceeded)  # format day number
            sunday = sunday[:-2] + new_day  # roll to new day number

            sunday = sunday.replace(str(date_.month), str(date_.month + 1))
    return get_week_event(util.make_date_object(sunday))

def get_remaining_dates(date_:"datetime.date"):
    dt = datetime.combine(date_, datetime.min.time())
    Remaining_schedule = fastf1.get_events_remaining(dt, include_testing=False)
    dates = str(Remaining_schedule["EventDate"]).split("\n")    # get list of column strings
    dates = [i.split(" ")[-1] for i in dates]   # seperate the dates in the string with column numbers
    return dates

def check_race_week(date_:"datetime.date", old_implementation=False):
    """Boolean return for if the given date is a f1 race week."""
    if old_implementation:
        if get_week_event(date_) is not None:
            return True
        else:
            return False
    else:
        Sunday = util.get_sunday_date_object(date_)
        dates = get_remaining_dates(date_)
        return str(Sunday) in dates

def check_sprint_session(event:"fastf1.events.Event"):
    """Boolean check if a race event has a f1 sprint session.
    Input event must be a fastf1.Event object."""
    try:
        event.get_sprint()
        return True
    except ValueError:
        return False

def sort_sessions_by_day(event:"fastf1.events.Event"):
    """Returns a dictionary mapping days to list containing all f1 fastf1.Session objects
     for the corresponding days"""
    # Initialize the dictionary
    session_days = {"Friday":[],"Saturday":[],"Sunday":[]}

    Q_session = event.get_qualifying()
    R_session = event.get_race()

    # Qualifying is friday if there is a sprint race, else it is saturday
    # Get the two sprint sessions if the race week includes a sprint:
    if check_sprint_session(event):
        SPQ_session = event.get_sprint_shootout()
        SP_session = event.get_sprint()

        session_days["Friday"].append(Q_session)
        session_days["Saturday"].append(SPQ_session)
        session_days["Saturday"].append(SP_session)
    else:
        session_days["Saturday"].append(Q_session)

    session_days["Sunday"].append(R_session)    # Race is always sunday

    return session_days

def print_event_info(event:"fastf1.events.Event", upper_case=True, event_discord_format="**"):
    """Prints name and date for given race event, must be fastf1.Event object.
    Supports discord formatting given as optional argument."""
    name = event["EventName"]
    if upper_case:
        name = name.upper()
    date = str(event["EventDate"])[:10]

    # Extract month number, find the month name, and translate to Norwegian
    month = util.month_to_norwegian(calendar.month_name[int(date[5:7])])

    end_day = str(int(date[-2:])) # gets rid of the leading zero if the day number is < 10
    start_day = str(int(end_day)-2)

    out_date = start_day + "-" + end_day + " " + month

    if event_discord_format is not None:
        # Print with given discord formatting
        return f"{event_discord_format}{name} {out_date}{event_discord_format[::-1]}\n"
    else: # Print without
        return f"{name} {out_date}\n"

