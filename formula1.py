import calendar
from datetime import date, datetime
from typing import Union

import fastf1  # f1 api
import numpy as np

import util
from formula2 import extract_days

fastf1.set_log_level('ERROR')  # lower log level to remove "default cache enabled" warning


def get_week_event(date_: Union[str, datetime.date]) -> Union[fastf1.events.Event, None]:
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


def get_next_week_event(date_: datetime.date) -> fastf1.events.Event:
    """Returns the next race week event from a given date."""
    dates = get_remaining_dates(date_)
    sunday = util.get_sunday_date_str(date_)

    date_str = str(date_)
    if is_f1_race_week(date_str):
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


def get_remaining_dates(date_: Union[str, datetime.date]) -> list[str]:
    """Returns a list of all the remaining dates of the f1 season."""
    if isinstance(date_, str):
        date_ = util.get_date_object(date_)
    dt = datetime.combine(date_, datetime.min.time())
    remaining_schedule = fastf1.get_events_remaining(dt, include_testing=False)
    dates = str(remaining_schedule["EventDate"]).split("\n")  # get list of column strings
    dates = [i.split(" ")[-1] for i in dates]  # seperate the dates in the string with column numbers
    return dates


def is_f1_race_week(date_: Union[str, datetime.date]) -> bool:
    """Boolean return for if the given date is a f1 race week."""
    if not isinstance(date_, str):
        date_ = str(date_)

    sunday = util.get_sunday_date_str(date_)
    remaining_dates = get_remaining_dates(date_)
    return sunday in remaining_dates


def is_sprint_week(event: fastf1.events.Event) -> bool:
    """Boolean check if a race event has a f1 sprint session."""
    try:
        event.get_sprint()
        return True
    except ValueError:
        return False


def sort_sessions_by_day(event: fastf1.events.Event) -> dict[str, list[fastf1.core.Session]]:
    """Returns a dictionary mapping days to list containing all f1 fastf1.Session objects
     for the corresponding days"""
    session_days = {"Friday": [], "Saturday": [], "Sunday": []}

    q_session = event.get_qualifying()
    r_session = event.get_race()

    # Qualifying is friday if there is a sprint race, else it is saturday
    # Get the two sprint sessions if the race week includes a sprint:
    if is_sprint_week(event):
        spq_session = event.get_sprint_shootout()
        sp_session = event.get_sprint()

        session_days["Friday"].append(q_session)
        session_days["Saturday"].append(spq_session)
        session_days["Saturday"].append(sp_session)
    else:
        session_days["Saturday"].append(q_session)

    session_days["Sunday"].append(r_session)  # Race is always sunday

    return session_days


def get_event_info(event: fastf1.events.Event, upper_case=True, event_discord_format="**") -> str:
    """Returns name and date for given race event.
    Supports discord formatting given as optional argument."""
    name = event["EventName"]
    if upper_case:
        name = name.upper()
    date_ = event["EventDate"].date()

    end_day = date_.day
    start_day = end_day - 2
    month = date_.month
    month_string = util.month_to_norwegian(util.month_index_to_name(month))
    if start_day <= 0:
        # If the start day is less than 0, it means the event starts in the previous month
        days_in_prev_month = calendar.monthrange(date_.year, month - 1)[1]
        prev_month_string = util.month_to_norwegian(util.month_index_to_name(month - 1))
        start_day = days_in_prev_month + start_day
        out_date = f"{start_day} {prev_month_string} - {end_day} {month_string}"
    else:
        out_date = f"{start_day} - {end_day} {month_string}"

    if event_discord_format is not None:
        # Print with given discord formatting
        return f"{event_discord_format}{name} {out_date}{event_discord_format[::-1]}\n"
    else:  # Print without
        return f"{name} {out_date}\n"


def until_next_race_week(date_: datetime.date) -> int:
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


def get_all_week_info(date_: Union[str, datetime.date], weeks_left: bool = True,
                      language: str = "norwegian") -> tuple[str, str]:
    """Returns two strings containing title and description for sending in discord."""
    if isinstance(date_, str):
        date_ = util.get_date_object(date_)

    event = get_week_event(date_)
    f1_days = sort_sessions_by_day(event)
    f2_calendar = util.extract_json_data()
    f2_days = extract_days(event, f2_calendar)

    eventtitle = get_event_info(event)
    eventinfo = get_all_days(event, f2_days, f1_days)

    if weeks_left:  # Print remaining race weeks in the season
        if language.lower() == "norwegian":
            eventinfo += "-Løp igjen: " + str(util.get_number_remaining_events(date_))
        else:
            pass  # add other language(s) for 'remaining events' here

    return eventtitle, eventinfo


def get_day_sessions(event: fastf1.events.Event,
                     day: str, f2_event: dict[str, list[list[str]]],
                     f1_event: dict[str, list[fastf1.core.Session]],
                     time_sort: bool = True,
                     discord_day_format: str = "__"):
    """Returns string containing category and time for all F1 and F2 sessions for a given day.
    If 'time_sort' sort the print by time instead of as F2 sessions -> F1 sessions, defaults to true.
    """
    import formula2 as f2

    # First check if the day is given in norwegian, the dictionary keys are in english.
    no_days = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
    daytitle = day

    if day.lower() in no_days:
        day = util.day_to_english(day)

    date_ = util.get_event_date_object(event)

    if f2.is_f2_race_week(str(date_)):
        f2_day = f2_event.get(day)
    else:
        f2_day = None
    f1_day = f1_event.get(day)

    if not f2_day and not f1_day:
        return None

    if time_sort:  # sort output by time
        timing_dict = {}
        tbc_sessions = []
        # Firstly save all f2 sessions mapped by time
        if f2_day:
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
        if f1_day:
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
        if f2_day:
            for name, time in f2_day:
                if name == "Feature Race":
                    title = "**F2 Feature Race**"
                elif name == "Qualifying Session":
                    title = "F2 Qualifying"
                else:
                    title = f"F2 {name}"
                output += f"{title}: {time}\n"

        # Lastly print the f1 sessions that day
        if f1_day:
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


def get_all_days(event: fastf1.events.Event,
                 f2_days: dict[str, list[list[str]]],
                 f1_days: dict[str, list[fastf1.core.Session]]):
    """Returns a string containing all sessions for each day for a given event."""
    output = ""

    thursday_title = "Torsdag"
    friday_title = "Fredag"
    saturday_title = "Lørdag"
    sunday_title = "Søndag"

    thursday = get_day_sessions(event, thursday_title, f2_days, f1_days)
    friday = get_day_sessions(event, friday_title, f2_days, f1_days)
    saturday = get_day_sessions(event, saturday_title, f2_days, f1_days)
    sunday = get_day_sessions(event, sunday_title, f2_days, f1_days)

    for day in [thursday, friday, saturday, sunday]:
        if day is not None:
            output += day
    return output
