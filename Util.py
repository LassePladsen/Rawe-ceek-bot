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

def print_event(Event,discord_format="__**"):
    """Prints name and date for given race event, must be fastf1.Event object.
    Supports discord formatting given as optional argument."""
    name = Event["EventName"]
    date = str(Event["EventDate"])[:10]

    # Extract month number, find the month name, and translate to Norwegian
    month = translate_month_to_norwegian(calendar.month_name[int(date[5:7])])

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
        f2_sessions: list containing a dictionary with session name and time
        f1_sessions: fastf1.Session object of the session
    """
    if len(f2_sessions) > 0 or len(f1_sessions)>0:
        print(dayname)

        # First print all f2 sessions
        if len(f2_sessions)>0:
            for f2_session in f2_sessions:
                time = f2_session["time"]
                print(f"F2 {f2_session} time")

        # Then print the f1 sessions
        if len(f1_sessions)>0:
            for f1_session in f1_sessions:
                # Extract session name
                name = str(f1_session).split(" - ")[1]

                # Extract session time and convert to norwegian time zone
                local_time = f1_session.date
                norwegian_time = local_time.tz_localize("Europe/Oslo")
                out_time = str(norwegian_time).split(" ")[1]

                # Add the timezone conversion to the total time (f.ex: 20:00:00+02:00 to 22:00:00)
                hour = int(out_time[:2])
                hour_add = int(out_time[8:11])
                hour_corrected = hour+hour_add

                out_time = str(hour_corrected) + out_time[2:5]
                print(f"F1 {name} - {out_time}")

        print("") # Final blank space to seperate the days in the output

def month_index_to_name(monthindex,language="English"):
    if language == "English":
        months = ["January", "February", "March", "April", "May", "June", "July",
                 "August", "September", "October", "November", "December"]
    elif language == "Norwegian":
        months = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli",
              "August", "September", "Oktober", "November", "Desember"]
    else: # Fallback to English
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
    return months[monthindex-1]


def translate_month_to_norwegian(month):
    no_months = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli",
              "August", "September", "Oktober", "November", "Desember"]
    en_months = ["January", "February", "March", "April", "May", "June", "July",
                 "August", "September", "October", "November", "December"]
    return no_months[en_months.index(month)]

def reformat_date(date):
    """Reformats a date given as 'year-mm-dd hh:mm:ss' to 'day month' with month names."""
    date = date.split(" ")[0]
    month = month_index_to_name(int(date[5:7]))
    day = date[8:]
    return day + " " + month

def extract_f2_days(Event,dictionary):
    """Extracts and sorts from dictionary the F2 sessions of given event as fastf1.Event object.
    Returns a dictionary mapping session days to session names and times.

    Input dictionary is formatted as such:
    'dictionary = {'21 May': ('Round 5', 'Italy-Emilia Romagna', 'Imola', '19-21 May 2023',
                          [['Qualifying Session', 'Friday', 'TBC'],
                           ['Sprint Race', 'Saturday', 'TBC'],
                           ['Feature Race', 'Sunday', 'TBC']]),  '
    """
    event_date = reformat_date(str(Event["EventDate"]).split(" ")[0])
    f2_event = dictionary[event_date][4]

    session_days = []
    for day in f2_event:
        day.pop(1)
        session_days.append(day)

    return session_days



# DEBUGGING/TESTING:
if __name__ == "__main__":
    Event = get_week_event(today)
    Event = get_week_event(date(2023,5,25))
    # print(Event)
    # print_event(Event)
    fri,satur,sun = sort_sessions_by_day(Event)
    f2_test = {'21 May': ('Round 5', 'Italy-Emilia Romagna', 'Imola', '19-21 May 2023',
                          [['Qualifying Session', 'Friday', '15:55-16:25'],
                           ['Sprint Race', 'Saturday', '10:35-11:20'],
                           ['Feature Race', 'Sunday', 'TBC']]),
               '28 May': ('Round 6', 'Monaco', 'Monte Carlo', '25-28 May 2023',
                          [['Qualifying Group A', 'Thursday', 'TBC'],
                           ['Qualifying Group B', 'Thursday', 'TBC'],
                           ['Sprint Race', 'Friday', '10:40-10:40'],
                           ['Feature Race', 'Sunday', 'TBC']])}

    # f2_friday = f2_test[][3][0]
    # f2_friday.pop(1)

    # print(f2_friday)
    print(extract_f2_days(Event, f2_test))
    # print_day_sessions("Fredag",[],fri)
    # print_day_sessions("Lørdag",[],satur)
    # print_day_sessions("Søndag",[],sun)

