from datetime import date,datetime
import calendar
import fastf1
import pytz
import json
import os
from typing import Union

import formula2 as f2
import formula1 as f1


def get_discord_data(key: str, file: str = "discord_data.json") -> str:
    """Extracts value from given datakey from a given .json filename """
    with open(file, "r") as infile:
        data = json.load(infile)
    return data[key]

def day_string_formatting(day):
    """Gives a string containing a day number formatted like '05' instead of '5' (example).
    Does nothing if the day number is over 10. Argument can be int or str."""
    day = int(day)
    if day < 10:
        return "0" + str(day)
    else:
        return str(day)

def get_sunday_date_str(date_: "datetime.date") -> str:
    """Returns a string with sundays date of the same week as the given date formatted '2023-05-07'.
    Input date must be a datetime.date object."""

    weekday = date.weekday(date_)  # the weekday number of the week beginning at 0 (monday)
    days_until_sunday = 6 - weekday

    # Create new day date and fix the formatting (f.ex 07 instead of 7)
    new_day = int(str(date_)[-2:]) + days_until_sunday
    new_day = day_string_formatting(new_day)


    date_sunday = str(date_)[:-2] + new_day

    # Roll over to next month if day number exceeds days in the given month:
    days_in_month = calendar.monthrange(date_.year, date_.month)[1]
    if int(date_sunday[-2:]) > days_in_month:
        # Find new day number
        days_exceeded = int(date_sunday[-2:]) - days_in_month
        new_day = day_string_formatting(days_exceeded)    # format day number
        date_sunday = date_sunday[:-2] + new_day   # roll to new day number

        date_sunday = date_sunday.replace(str(date_.month), str(date_.month + 1))  # roll to next month
    return date_sunday

def get_sunday_date_object(date_: "datetime.date") -> "datetime.date":
    return make_date_object(get_sunday_date_str(date_))

def month_index_to_name(monthindex,language="English"):
    """Converts a index to the corresponding month name. Defaults to English,
    but also supports Norwegian."""
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

def month_name_to_index(monthname):
    """Converts an english month name to the corresponding index."""
    months = ["January", "February", "March", "April", "May", "June", "July",
                 "August", "September", "October", "November", "December"]
    return months.index(monthname)

def month_to_norwegian(month, caps=True):
    """Translates month name from English to norwegian names, defaults to using caps letters."""
    if caps:
        no_months = ["JANUAR", "FEBRUAR", "MARS", "APRIL", "MAI", "JUNI", "JULI",
              "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
    else:
        no_months = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli",
                  "August", "September", "Oktober", "November", "Desember"]
    en_months = ["january", "february", "march", "april", "may", "june", "july",
                 "august", "september", "october", "november", "december"]
    return no_months[en_months.index(month.lower())]

def day_to_norwegian(day):
    """Translates day name from english to norwegian, no case-sensitive input."""
    no_days = ["Mandag","Tirsdag","Onsdag","Torsdag","Fredag","Lørdag","Søndag"]
    en_days = ["monday","tuesay","wednesday","thursday","friday","saturday","sunday"]
    return no_days[en_days.index(day.lower())]

def day_to_english(day):
    """Translates day name from norwegian to english, no case-sensitive input."""
    en_days = ["Monday","Tuesay","Wednesday","Thursday","Friday","Saturday","Sunday"]
    no_days = ["mandag","tirsdag","onsdag","torsdag","fredag","lørdag","søndag"]
    return en_days[no_days.index(day.lower())]

def format_date(date_: str) -> str:
    """Reformats a date string given as 'year-mm-dd hh:mm:ss' to 'dd Month' (with month names)."""
    date_ = date_.split(" ")[0]
    month = month_index_to_name(int(date_[5:7]))
    day = date_[8:]
    return day + " " + month

def make_date_object(date_: str) -> "datetime.date":
    """Creates a datatime.date object from given date string.
    String can either be in the 'yyyy-mm-dd' format or 'dd Month' (with month names) format, in
    the latter case the year will be the current year.."""

    if "-" in date_:
        year,monthi,day = date_.split("-")
    else:
        year = date_.today().year
        day,month = date_.split(" ")
        monthi = month_name_to_index(month)
    return date(int(year), int(monthi), int(day))

def timezone_to_oslo(time):
    """Converts a time of panda.Timestamp object to norwegian timezone."""
    no_time = time.tz_localize("Europe/Oslo")
    out_time = str(no_time).split(" ")[1]

    # Add the timezone conversion to the total time (f.ex: 20:00:00+02:00 to 22:00:00)
    hour = int(out_time[:2])
    hour_add = int(out_time[8:11])
    hour_corrected = hour + hour_add

    out_time = str(hour_corrected) + out_time[2:5]
    return out_time

def get_event_date_str(event: "fastf1.events.Event") -> str:
    """Gets event date string from fastf1.Event object and cuts away the time info.
    Formatted like '07 May'"""
    return format_date(str(event["EventDate"]).split(" ")[0])

def get_event_date_object(event: "fastf1.events.Event") -> "datetime.date":
    """Get the sunday event date as datetime.date object from given fastf1.Event object."""
    string = str(event["EventDate"]).split(" ")[0]
    date_ = make_date_object(get_sunday_date_str(make_date_object(string)))
    return date_

def print_day_sessions(event: "fastf1.events.Event", day, f2_calendar, f2_event,
                       f1_event, time_sort=True, discord_day_format="__"):
    """Prints category and time for all F1 and F2 sessions from given list containing all sessions for that day.
    If 'time_sort' defaults to true and will sort the print by time instead of as F2 sessions -> F1 sessions

    Parameters:
        event: fastf1.Event object
        day: string specifying which day of the Event to print
        f2_event: dictionary mapping days with list containing all f2 sessions names and times for each day.
        f1_event: dictionary mapping days with list containing all f1 fastf1.Session objects for each day.
                     for the corresponding days.
    """
    # First check if the day is given in norwegian, the dictionary keys are in english.
    no_days = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
    daytitle = day

    if day.lower() in no_days:
        day = day_to_english(day)

    date_ = get_event_date_object(event)

    if f2.check_race_week(date_, f2_calendar):
        f2_day = f2_event.get(day)
    else:
        f2_day = None
    f1_day = f1_event.get(day)

    if f2_day is None and f1_day is None:
        return None

    if time_sort:  # sort output by time
        timing_dict = {}
        TBC_sessions = []
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
                    TBC_sessions.append(f"{title}: {time}")
                else: # now sort the sessions by hour
                    hour = int(time.split(":")[0])
                    if timing_dict.get(hour) is not None: # check if there already is a session on the same hour
                        timing_dict[hour + 1] = f"{title}: {time}" # then add it as the next hour instead
                    else:   # if not then add it as the hour
                        timing_dict[hour] = f"{title}: {time}"#

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
                out_time = timezone_to_oslo(local_time)
                hour = int(out_time.split(":")[0])
                timing_dict[hour] = f"{title}: {out_time}"

        output = discord_day_format + daytitle.capitalize() + discord_day_format[::-1] + "\n"

        # Now first print the F2 sessions which have TBC start times
        if TBC_sessions:
            for f2_tbc_session in TBC_sessions:
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
            for name,time in f2_day:
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
                out_time = timezone_to_oslo(local_time)
                output += f"{title}: {out_time}\n"

    output += "\n"  # Final blank space to seperate different days in the output
    return output

def print_all_days(event: "fastf1.events.Event", f2_calendar, f2_days, f1_days):
    output = ""

    thursday_title = "Torsdag"
    friday_title = "Fredag"
    saturday_title = "Lørdag"
    sunday_title = "Søndag"

    thursday = print_day_sessions(event, thursday_title, f2_calendar, f2_days, f1_days)
    friday = print_day_sessions(event, friday_title, f2_calendar, f2_days, f1_days)
    saturday = print_day_sessions(event, saturday_title, f2_calendar, f2_days, f1_days)
    sunday = print_day_sessions(event, sunday_title, f2_calendar, f2_days, f1_days)

    for day in [thursday,friday,saturday,sunday]:
        if day is not None:
            output += day
    return output

def get_oslo_time(local_time, country):
    local_time = f"2023-01-01 {local_time}"

    # Map country to its timezone
    timezone = pytz.country_timezones[get_country_code(country)][0]

    # Convert local time to datetime object
    dt = datetime.strptime(local_time, '%Y-%m-%d %H:%M')

    # Create timezone object for local timezone
    local_tz = pytz.timezone(timezone)

    # Create timezone object for Oslo time
    gmt_plus_one = pytz.timezone('Europe/Oslo')

    # Convert local time to Oslo time
    oslo_time = local_tz.localize(dt).astimezone(gmt_plus_one)

    # Return Oslo time in ISO format
    return f"{oslo_time.hour}:{oslo_time.minute}"

def get_country_code(country_name):
    # Dictionary mapping country names to ISO codes
    country_codes = {'Argentina': 'AR',
                     'Austria': 'AT',
                     'Australia': 'AU',
                     'Azerbaijan': 'AZ',
                     'Belgium': 'BE',
                     'Brazil': 'BR',
                     'Bahrain': 'BH',
                     'Canada': 'CA',
                     'Switzerland': 'CH',
                     'China': 'CN',
                     'Germany': 'DE',
                     'Denmark': 'DK',
                     'Algeria': 'DZ',
                     'Spain': 'ES',
                     'France': 'FR',
                     'Great Britain': 'GB',
                     'Hungary': 'HU',
                     'Indonesia': 'ID',
                     'Ireland': 'IE',
                     'Israel': 'IL',
                     'India': 'IN',
                     'Italy': 'IT',
                     'Japan': 'JP',
                     'South Korea': 'KR',
                     'Kuwait': 'KW',
                     'Luxembourg': 'LU',
                     'Morocco': 'MA',
                     'Monaco': 'MC',
                     'Mexico': 'MX',
                     'Malaysia': 'MY',
                     'Netherlands': 'NL',
                     'Portugal': 'PT',
                     'Russia': 'RU',
                     'Saudi Arabia': 'SA',
                     'Sweden': 'SE',
                     'Singapore': 'SG',
                     'Thailand': 'TH',
                     'Turkey': 'TR',
                     'Ukraine': 'UA',
                     'United States': 'US',
                     'Vietnam': 'VN',
                     'South Africa': 'ZA'}

    # Check if input country name is in dictionary
    if country_name in country_codes:
        return country_codes[country_name]
    else:
        return None

def until_next_race_week(date_: "datetime.date"):
    """Returns integer of how many weeks until next race week from given date."""
    dates = f1.get_remaining_dates(date_)
    sunday = get_sunday_date_str(date_)
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
            new_day = day_string_formatting(days_exceeded)  # format day number
            sunday = sunday[:-2] + new_day  # roll to new day number

            sunday = sunday.replace(str(date_.month), str(date_.month + 1))
        counter += 1
    return counter

def get_remaining_events(date_: "datetime.date"):
    """Returns int of how many remaining f1 events there are from a given date.

    """
    dt = datetime.combine(date_, datetime.min.time())
    Remaining_schedule = fastf1.get_events_remaining(dt, include_testing=False)
    return len(Remaining_schedule)

def get_all_week_info(date_: "datetime.date", weeks_left=True, language="norwegian"):
    """Returns two strings containing print title and print text
    for sending in discord."""
    event = f1.get_week_event(date_)

    f1_days = f1.sort_sessions_by_day(event)
    f2_calendar = f2.extract_json_data()
    f2_days = f2.extract_days(event, f2_calendar)

    eventtitle = f1.print_event_info(event)
    eventinfo = print_all_days(event, f2_calendar, f2_days, f1_days)

    if weeks_left: # Print remaining race weeks in the season
        if language.lower() == "norwegian":
            eventinfo += "-Races igjen: " + str(get_remaining_events(date_))
        else:
            pass    # add other language(s) for 'remaining eventts' here

    return eventtitle,eventinfo


def check_file_exists(filename):
    try:
        with open(filename, "r") as infile:
            pass
        return True
    except FileNotFoundError:
        return False


def get_default_archive_filename(filename: str) -> str:
    year = date.today().year - 1
    folder = "Archive"
    temp = filename.replace(".json", "")
    return f"{folder}/archived_{temp}_{year}.json"


def archive_json(filename: str, archive_filename: str = None) -> None:
    """Archives the given json and creates a new blank json with the same name. If the archived file
    already exist, update it instead of creating a new one."""
    if archive_filename is None:
        archive_filename = get_default_archive_filename(filename)

    if check_file_exists(archive_filename):  # if archive already exists update it
        with open(filename, "r") as infile:
            data = json.load(infile)
            update_existing_json(data, archive_filename)

    else:
        os.rename(filename, archive_filename)

        # Create new blank file
    with open(filename, "w") as new_file:
        json.dump({}, new_file,indent=3)


def update_existing_json(json_dict: dict, filename: str) -> None:
    """Updates an existing json file with new keys-value pairs, if they exist."""
    if not check_file_exists(filename):
        return
    with open(filename, "r") as infile:
        data = json.load(infile)
        for key in json_dict:
            if key in data:  # dont overwrite if date already is in the json
                continue
            data[key] = json_dict[key]
    with open(filename, "w") as outfile:
        json.dump(data, outfile,indent=3)

def extract_json_data(json_file: str = "f2_calendar.json") -> dict[str, list[Union[str, list[str]]]]:
    """Extracts data from the given json file."""
    with open(json_file, "r") as infile:
        return json.load(infile)