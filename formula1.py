import calendar
from datetime import date, datetime
from typing import Union

import fastf1  # f1 api
import numpy as np

import util
from formula2 import extract_days

fastf1.set_log_level('ERROR')  # lower log level to remove "default cache enabled" warning


def get_week_event(date_: Union[str, datetime.date]):
    """Returns the fastf1 event object for the week of the given date.
    Returns None if there is no event in that week.
    Input date must be a datetime.date object."""
    if isinstance(date_, str):
        date_ = util.get_date_object(date_)
    sunday_date = util.get_sunday_date_str(date_)

    today = date.today()
    race_schedule = fastf1.get_event_schedule(today.year, include_testing=False)

    race_dates = np.asarray(race_schedule["EventDate"].to_string(index=False).split())
    if sunday_date in race_dates:
        race_index = np.where(sunday_date == race_dates)[0][0] + 1
        return fastf1.get_event(date_.year, race_index)

    else:  # If the given date is not a race week
        return None


def get_next_week_event(date_: datetime.date):
    """Returns the next race week event from a given date"""
    dates = get_remaining_dates(date_)
    sunday = util.get_sunday_date_str(date_)

    date_str = str(date_)
    if check_f1_race_week(date_str):
        return get_week_event(date_str)

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
    return get_week_event(util.get_date_object(sunday))


def get_remaining_dates(date_: Union[str, datetime.date]):
    if isinstance(date_, str):
        date_ = util.get_date_object(date_)
    dt = datetime.combine(date_, datetime.min.time())
    remaining_schedule = fastf1.get_events_remaining(dt, include_testing=False)
    dates = str(remaining_schedule["EventDate"]).split("\n")  # get list of column strings
    dates = [i.split(" ")[-1] for i in dates]  # seperate the dates in the string with column numbers
    return dates


def check_f1_race_week(date_: Union[str, datetime.date]):
    """Boolean return for if the given date is a f1 race week."""
    if not isinstance(date_, str):
        date_ = str(date_)

    sunday = util.get_sunday_date_str(date_)
    remaining_dates = get_remaining_dates(date_)
    return sunday in remaining_dates


def check_sprint_session(event: fastf1.events.Event):
    """Boolean check if a race event has a f1 sprint session.
    Input event must be a fastf1.Event object."""
    try:
        event.get_sprint()
        return True
    except ValueError:
        return False


def sort_sessions_by_day(event: fastf1.events.Event):
    """Returns a dictionary mapping days to list containing all f1 fastf1.Session objects
     for the corresponding days"""
    # Initialize the dictionary
    session_days = {"Friday": [], "Saturday": [], "Sunday": []}

    q_session = event.get_qualifying()
    r_session = event.get_race()

    # Qualifying is friday if there is a sprint race, else it is saturday
    # Get the two sprint sessions if the race week includes a sprint:
    if check_sprint_session(event):
        spq_session = event.get_sprint_shootout()
        sp_session = event.get_sprint()

        session_days["Friday"].append(q_session)
        session_days["Saturday"].append(spq_session)
        session_days["Saturday"].append(sp_session)
    else:
        session_days["Saturday"].append(q_session)

    session_days["Sunday"].append(r_session)  # Race is always sunday

    return session_days


def print_event_info(event: fastf1.events.Event, upper_case=True, event_discord_format="**"):
    """Prints name and date for given race event, must be fastf1.Event object.
    Supports discord formatting given as optional argument."""
    name = event["EventName"]
    if upper_case:
        name = name.upper()
    date_ = str(event["EventDate"])[:10]

    # Extract month number, find the month name, and translate to Norwegian
    month = util.month_to_norwegian(calendar.month_name[int(date_[5:7])])

    end_day = str(int(date_[-2:]))  # gets rid of the leading zero if the day number is < 10
    start_day = str(int(end_day) - 2)

    out_date = start_day + "-" + end_day + " " + month

    if event_discord_format is not None:
        # Print with given discord formatting
        return f"{event_discord_format}{name} {out_date}{event_discord_format[::-1]}\n"
    else:  # Print without
        return f"{name} {out_date}\n"


def until_next_race_week(date_: datetime.date):
    """Returns integer of how many weeks until next race week from given date."""
    dates = get_remaining_dates(date_)
    sunday = util.get_sunday_date_str(date_)
    if sunday in dates:
        return 0

    counter = 0
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
        counter += 1
    return counter


def get_all_week_info(date_: Union[str, datetime.date], weeks_left=True, language="norwegian"):
    """Returns two strings containing print title and print text for sending in discord."""
    if isinstance(date_, str):
        date_ = util.get_date_object(date_)

    event = get_week_event(date_)
    f1_days = sort_sessions_by_day(event)
    f2_calendar = util.extract_json_data()
    f2_days = extract_days(event, f2_calendar)

    eventtitle = print_event_info(event)
    eventinfo = print_all_days(event, f2_days, f1_days)

    if weeks_left:  # Print remaining race weeks in the season
        if language.lower() == "norwegian":
            eventinfo += "-Races igjen: " + str(util.get_remaining_events(date_))
        else:
            pass  # add other language(s) for 'remaining events' here

    return eventtitle, eventinfo


def print_day_sessions(event: fastf1.events.Event, day, f2_event,
                       f1_event, time_sort=True, discord_day_format="__"):
    """Prints category and time for all F1 and F2 sessions from given list containing all sessions for that day.
    If 'time_sort' defaults to true and will sort the print by time instead of as F2 sessions -> F1 sessions

    Parameters:
        event: fastf1.Event object
        day: string specifying which day of the Event to print
        f2_event: dictionary mapping days with list containing all f2 sessions names and times for each day.
        f1_event: dictionary mapping days with list containing all f1 fastf1.Session objects for each day.
                     for the corresponding days.
        time_sort: boolean deciding whether to sort the print by time.
        discord_day_format: string containing discord formatting for the day print.
    """
    import formula2 as f2

    # First check if the day is given in norwegian, the dictionary keys are in english.
    no_days = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
    daytitle = day

    if day.lower() in no_days:
        day = util.day_to_english(day)

    date_ = util.get_event_date_object(event)

    if f2.check_f2_race_week(str(date_)):
        f2_day = f2_event.get(day)
    else:
        f2_day = None
    f1_day = f1_event.get(day)

    if f2_day is None and f1_day is None:
        return None

    if time_sort:  # sort output by time
        timing_dict = {}
        tbc_sessions = []
        # Firstly save all f2 sessions mapped by time
        if f2_day is not None:
            for name, time in f2_day:
                if name == "Feature Race":
                    title = "**F2 Feature Race**"
                elif name == "Qualifying Session":
                    title = "F2 Qualifying"
                else:
                    title = f"F2 {name}"

                # special case for it the f2 timing is TBC
                if time == "TBC":
                    tbc_sessions.append(f"{title}: {time}")
                else:  # now sort the sessions by hour
                    hour = int(time.split(":")[0])
                    if timing_dict.get(hour) is not None:  # check if there already is a session on the same hour
                        timing_dict[hour + 1] = f"{title}: {time}"  # then add it as the next hour instead
                    else:  # if not then add it as the hour
                        timing_dict[hour] = f"{title}: {time}"

        # Lastly save all f1 sessions mapped by time
        if f1_day is not None:
            for f1_session in f1_day:
                # Extract session name
                name = str(f1_session).split(" - ")[1]
                if name == "Race":
                    title = "**F1 Feature Race**"
                else:
                    title = f"F1 {name}"

                # Extract session time and convert to norwegian time zone
                local_time = f1_session.date
                out_time = util.timezone_to_oslo(local_time)
                hour = int(out_time.split(":")[0])
                timing_dict[hour] = f"{title}: {out_time}"

        output = discord_day_format + daytitle.capitalize() + discord_day_format[::-1] + "\n"

        # Now first print the F2 sessions which have TBC start times
        if tbc_sessions:
            for f2_tbc_session in tbc_sessions:
                output += f2_tbc_session + "\n"

        # Then print the others in ascending time order by using the dict keys
        hours_sort = list(timing_dict.keys())
        hours_sort.sort()

        for hour in hours_sort:
            output += timing_dict[hour] + "\n"


    else:  # dont time sort
        output = discord_day_format + daytitle.capitalize() + discord_day_format[::-1] + "\n"
        # Secondly print all f2 sessions that day
        if f2_day is not None:
            for name, time in f2_day:
                if name == "Feature Race":
                    title = "**F2 Feature Race**"
                elif name == "Qualifying Session":
                    title = "F2 Qualifying"
                else:
                    title = f"F2 {name}"
                output += f"{title}: {time}\n"

        # Lastly print the f1 sessions that day
        if f1_day is not None:
            for f1_session in f1_day:
                # Extract session name
                name = str(f1_session).split(" - ")[1]
                if name == "Race":
                    title = "**F1 Feature Race**"
                else:
                    title = f"F1 {name}"

                # Extract session time and convert to norwegian time zone
                local_time = f1_session.date
                out_time = util.timezone_to_oslo(local_time)
                output += f"{title}: {out_time}\n"

    output += "\n"  # Final blank space to seperate different days in the output
    return output


def print_all_days(event: fastf1.events.Event, f2_days, f1_days):
    output = ""

    thursday_title = "Torsdag"
    friday_title = "Fredag"
    saturday_title = "Lørdag"
    sunday_title = "Søndag"

    thursday = print_day_sessions(event, thursday_title, f2_days, f1_days)
    friday = print_day_sessions(event, friday_title, f2_days, f1_days)
    saturday = print_day_sessions(event, saturday_title, f2_days, f1_days)
    sunday = print_day_sessions(event, sunday_title, f2_days, f1_days)

    for day in [thursday, friday, saturday, sunday]:
        if day is not None:
            output += day
    return output
