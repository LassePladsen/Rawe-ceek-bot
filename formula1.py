import numpy as np
import fastf1               # f1 api

from Util import *

Race_schedule = fastf1.get_event_schedule(today.year, include_testing=False)

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

def check_f1_race_week():
    """Boolean check for if the current week is a f1 race week."""
    if get_week_event(today) is not None:
        return True
    else:
        return False

def check_f1_sprint_session(Event):
    """Boolean check if a race event has a f1 sprint session.
    Input event must be a fastf1.Event object."""
    try:
        Event.get_sprint()
        return True
    except ValueError:
        return False

def sort_f1_sessions_by_day(Event):
    """Returns three lists for friday, saturday, and sunday containing the f1 sessions of each day."""
    # Initialize lists of sessions to sort
    friday = []
    saturday = []
    sunday = []

    Q_session = Event.get_qualifying()
    R_session = Event.get_race()

    # Get the two sprint sessions if the race week includes a sprint:
    if check_f1_sprint_session(Event):
        SPQ_session = Event.get_sprint_shootout()
        SP_session = Event.get_sprint()

        friday.append(Q_session)
        saturday.append(SPQ_session)
        saturday.append(SP_session)
    else:
        saturday.append(Q_session)

    sunday.append(R_session)

    return friday,saturday,sunday

def print_event_info(Event, discord_format="__**"):
    """Prints name and date for given race event, must be fastf1.Event object.
    Supports discord formatting given as optional argument."""
    name = Event["EventName"]
    date = str(Event["EventDate"])[:10]

    # Extract month number, find the month name, and translate to Norwegian
    month = month_to_norwegian(calendar.month_name[int(date[5:7])])

    end_day = str(int(date[-2:])) # gets rid of the leading zero if the day number is < 10
    start_day = str(int(end_day)-2)

    out_date = start_day + "-" + end_day + " " + month

    if discord_format is not None:
        # Print with given discord formatting
        print(f"{discord_format}{name} {out_date}{discord_format[::-1]}")
    else: # Print without
        print(f"{name} {out_date}")

def print_day_sessions(dayname, f2_sessions, f1_sessions):
    """Prints category and time for all F1 and F2 sessions from given list containing all sessions for that day.

    Parameters:
        f2_sessions: list containing a dictionary mapping days with session names and times
        f1_sessions: fastf1.Session object of the session
    """
    if len(f2_sessions) > 0 or len(f1_sessions)>0:
        print(dayname)

        # First print all f2 sessions
        if len(f2_sessions)>0:
            for f2_session in f2_sessions:
                # f2_session is a list with session name and time in order.
                name = f2_session[0]
                time = f2_session[1]
                print(f"F2 {name} {time}")

        # Then print the f1 sessions
        if len(f1_sessions)>0:
            for f1_session in f1_sessions:
                # Extract session name
                name = str(f1_session).split(" - ")[1]

                # Extract session time and convert to norwegian time zone
                local_time = f1_session.date
                out_time = convert_timezone_norwegian(local_time)
                print(f"F1 {name} - {out_time}")

        print("") # Final blank space to seperate the days in the output