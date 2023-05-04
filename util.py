from datetime import date,datetime
import calendar

import fastf1
import pytz

import formula2 as f2
import formula1 as f1

def get_discord_bot_token(filename):
    with open(filename,"r") as file:
        return file.read()

def day_string_formatting(day):
    """Gives a string containing a day number formatted like '05' instead of '5' (example).
    Does nothing if the day number is over 10. Argument can be int or str."""
    day = int(day)
    if day < 10:
        return "0" + str(day)
    else:
        return str(day)

def get_sunday_date(Date):
    """Returns a string with sundays date of the same week as the given date formatted '2023-05-07'.
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

def get_sunday_Date(Date):
    return make_Date(get_sunday_date(Date))

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

def format_date(date_str):
    """Reformats a date given as 'year-mm-dd hh:mm:ss' to 'dd Month' (with month names)."""
    date_str = date_str.split(" ")[0]
    month = month_index_to_name(int(date_str[5:7]))
    day = date_str[8:]
    return day + " " + month

def make_Date(date_str):
    """Creates a datatime.date object from given string.
    String can either be in the 'yyyy-mm-dd' format or 'dd Month' (with month names) format, in
    the latter case the year will be the current year.."""

    if "-" in date_str:
        year,monthi,day = date_str.split("-")
    else:
        year = date.today().year
        day,month = date_str.split(" ")
        monthi = month_name_to_index(month)
    return date(int(year),int(monthi),int(day))

def convert_timezone_norwegian(time):
    """Converts a time of panda.Timestamp object to norwegian timezone."""
    no_time = time.tz_localize("Europe/Oslo")
    out_time = str(no_time).split(" ")[1]

    # Add the timezone conversion to the total time (f.ex: 20:00:00+02:00 to 22:00:00)
    hour = int(out_time[:2])
    hour_add = int(out_time[8:11])
    hour_corrected = hour + hour_add

    out_time = str(hour_corrected) + out_time[2:5]
    return out_time

def get_event_date_str(Event):
    """Gets event date from fastf1.Event object and cuts away the time info.
    Formatted like '07 May'"""
    return format_date(str(Event["EventDate"]).split(" ")[0])

def get_event_Date(Event):
    """Get the sunday event date as datetime.date object from given fastf1.Event object."""
    string = str(Event["EventDate"]).split(" ")[0]
    Date = make_Date(get_sunday_date(make_Date(string)))
    return Date

def print_day_sessions(Event, day, f2_calendar, f2_event,
                       f1_event, time_sort=True,discord_format="__"):
    """Prints category and time for all F1 and F2 sessions from given list containing all sessions for that day.
    If 'time_sort' defaults to true and will sort the print by time instead of as F2 sessions -> F1 sessions

    Parameters:
        Event: fastf1.Event object
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

    Date = get_event_Date(Event)
    # Get the day sessions if they exist
    if f2.check_race_week(Date, f2_calendar):
        try:
            f2_day = f2_event[day]
        except KeyError:
            f2_day = []
    else:
        f2_day = []

    try:
        f1_day = f1_event[day]
    except KeyError:
        f1_day = []

    output = ""

    # Firstly print the day if there is a session
    if len(f2_day)>0 or len(f1_day)>0:
        output += discord_format + daytitle.capitalize() + discord_format[::-1] + "\n"

        timing_dict = {}
        TBC_sessions = []
        if time_sort:
            # Secondly save all f2 sessions mapped by time
            if len(f2_day) > 0:
                for name, time in f2_day:
                    if name == "Race":
                        name = "**Feature Race**"

                    if time == "TBC":
                        TBC_sessions.append(f"F2 {name}: {time}")

                    else:
                        hour = int(time.split(":")[0])
                        timing_dict[hour] = f"F2 {name}: {time}"

            # Lastly save all f1 sessions mapped by time
            if len(f1_day) > 0:
                for f1_session in f1_day:
                    # Extract session name
                    name = str(f1_session).split(" - ")[1]
                    if name == "Race":
                        name = "**Feature Race**"

                    # Extract session time and convert to norwegian time zone
                    local_time = f1_session.date
                    out_time = convert_timezone_norwegian(local_time)
                    hour = int(out_time.split(":")[0])
                    timing_dict[hour] = f"F1 {name}: {out_time}"

            # Now first print the F2 sessions which have TBC start times
            if len(TBC_sessions) > 0:
                for f2_tbc_session in TBC_sessions:
                    output += f2_tbc_session + "\n"

            # Then print the others in ascending time order by using the dict keys
            hours_sort = list(timing_dict.keys())
            hours_sort.sort()

            for hour in hours_sort:
                output += timing_dict[hour] + "\n"


        elif not time_sort:
            # Secondly print all f2 sessions that day
            if len(f2_day) > 0:
                for name,time in f2_day:
                    if name == "Race":
                        name = "Feature Race"
                    output += f"F2 {name}: {time}" + "\n"

            # Lastly print the f1 sessions that day
            if len(f1_day) > 0:
                for f1_session in f1_day:
                    # Extract session name
                    name = str(f1_session).split(" - ")[1]
                    if name == "Race":
                        name = "Feature Race"

                    # Extract session time and convert to norwegian time zone
                    local_time = f1_session.date
                    out_time = convert_timezone_norwegian(local_time)
                    output += f"F1 {name}: {out_time}" + "\n"

        output += "\n"  # Final blank space to seperate the days in the output
        return output

def print_all_days(Event,f2_calendar,f2_days,f1_days):
    output = ""
    thursday = print_day_sessions(Event, "Torsdag", f2_calendar, f2_days, f1_days)
    friday = print_day_sessions(Event, "Fredag", f2_calendar, f2_days, f1_days)
    saturday = print_day_sessions(Event, "Lørdag", f2_calendar, f2_days, f1_days)
    sunday = print_day_sessions(Event, "Søndag", f2_calendar, f2_days, f1_days)

    for day in [thursday,friday,saturday,sunday]:
        if day is not None:
            output += day
    return output

def get_gmt_plus_one(local_time, country):
    local_time = f"2023-01-01 {local_time}"

    # Map country to its timezone
    timezone = pytz.country_timezones[get_country_code(country)][0]

    # Convert local time to datetime object
    dt = datetime.strptime(local_time, '%Y-%m-%d %H:%M')

    # Create timezone object for local timezone
    local_tz = pytz.timezone(timezone)

    # Create timezone object for GMT+1
    gmt_plus_one = pytz.timezone('Europe/Oslo')

    # Convert local time to GMT+1 time
    gmt_plus_one_time = local_tz.localize(dt).astimezone(gmt_plus_one)

    # Return GMT+1 time in ISO format
    return f"{gmt_plus_one_time.hour}:{gmt_plus_one_time.minute}"

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

def until_next_race_week(Date):
    """Returns how many weeks until next race week from given date"""
    dates = f1.get_remaining_dates(Date)
    sunday = get_sunday_date(Date)
    if sunday in dates:
        return 0

    counter = 0
    while sunday not in dates:
        # Increase week by 1 and check again
        sunday = sunday[:-2] + str(int(sunday[-2:]) + 7)

        # Roll over to next month if day number exceeds days in the given month:
        days_in_month = calendar.monthrange(Date.year, Date.month)[1]
        if int(sunday[-2:]) > days_in_month:
            # Find new day number
            days_exceeded = int(sunday[-2:]) - days_in_month
            new_day = day_string_formatting(days_exceeded)  # format day number
            sunday = sunday[:-2] + new_day  # roll to new day number

            sunday = sunday.replace(str(Date.month), str(Date.month + 1))
        counter += 1
    return counter

def get_remaining_events(Date):
    dt = datetime.combine(Date, datetime.min.time())
    Remaining_schedule = fastf1.get_events_remaining(dt, include_testing=False)
    return len(Remaining_schedule)

def print_all_week_info(Date,weeks_left=True,norwegian=True):
    Event = f1.get_week_event(Date)

    f1_days = f1.sort_sessions_by_day(Event)
    f2_calendar = f2.get_calendar()
    f2_days = f2.extract_days(Event, f2_calendar)

    eventtitle = f1.print_event_info(Event)
    eventinfo = print_all_days(Event, f2_calendar, f2_days, f1_days)

    if weeks_left: # Print remaining race weeks in the season
        if norwegian:
            eventinfo += "-Races igjen: " + str(get_remaining_events(Date))
        else:
            pass    # add other language(s) for 'remaining eventts' here

    return eventtitle,eventinfo

