import calendar
import json
import os
from datetime import date, datetime, timedelta
from typing import Union

import fastf1
import pytz

F2CalendarType = dict[str, list[Union[str, list[str]]]]


def get_json_data(key: str, file: str = "data/discord_data.json") -> str:
    """Extracts string value from given datakey from a given .json filename. Defaults to discord_data.json"""
    with open(file, "r") as infile:
        data = json.load(infile)
    return data[key]


def day_string_formatting(day: str) -> str:
    """Gives a string containing a day number formatted like '05' instead of '5' (example).
    Does nothing if the day number is over 10. Argument can be int or str."""
    day = int(day)
    if day < 10:
        return "0" + str(day)
    else:
        return str(day)


def get_sunday_date_str(date_: Union[str, datetime.date]) -> str:
    """Returns a string with sundays date of the same week as the given date formatted '2023-05-07'"""
    if isinstance(date_, str):
        date_ = get_date_object(date_)
    weekday = date.weekday(date_)  # the weekday number of the week beginning at 0 (monday)
    days_until_sunday = 6 - weekday

    # Create new day date and fix the formatting (f.ex 07 instead of 7)
    new_day = date_.day + days_until_sunday
    new_day = day_string_formatting(str(new_day))

    date_sunday = str(date_)[:-2] + str(new_day)

    # Roll over to next month if day number exceeds days in the given month:
    days_in_month = calendar.monthrange(date_.year, date_.month)[1]
    if int(date_sunday[-2:]) > days_in_month:
        # Find new day number
        days_exceeded = int(date_sunday[-2:]) - days_in_month
        new_day = day_string_formatting(str(days_exceeded))  # format day number
        date_sunday = date_sunday[:-2] + new_day  # roll to new day number

        date_sunday = date_sunday.replace(str(date_.month), str(date_.month + 1))  # roll to next month
    return date_sunday


def get_sunday_date_object(date_: Union[str, datetime.date]) -> datetime.date:
    """Returns a datetime.date object with sundays date of the same week as the given date."""
    if isinstance(date_, str):
        return get_date_object(date_)
    return get_date_object(get_sunday_date_str(date_))


def month_index_to_name(monthindex: int, language: str = "English") -> str:
    """Converts a index to the corresponding month name. Defaults to English,
    but also supports Norwegian."""
    if language == "English":
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
    elif language == "Norwegian":
        months = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli",
                  "August", "September", "Oktober", "November", "Desember"]

    else:  # Fallback to English
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
    return months[monthindex - 1]


def month_name_to_index(monthname: str) -> int:
    """Converts an english month name to the corresponding index."""
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return months.index(monthname)


def month_to_norwegian(month: str, caps: bool = True) -> str:
    """Translates month name from english to norwegian names, defaults to using caps letters."""
    if caps:
        no_months = ["JANUAR", "FEBRUAR", "MARS", "APRIL", "MAI", "JUNI", "JULI",
                     "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
    else:
        no_months = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli",
                     "August", "September", "Oktober", "November", "Desember"]
    en_months = ["january", "february", "march", "april", "may", "june", "july",
                 "august", "september", "october", "november", "december"]
    return no_months[en_months.index(month.lower())]


def day_to_norwegian(day: str) -> str:
    """Translates day name from english to norwegian, no case-sensitive input."""
    no_days = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
    en_days = ["monday", "tuesay", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return no_days[en_days.index(day.lower())]


def day_to_english(day: str) -> str:
    """Translates day name from norwegian to english, no case-sensitive input."""
    en_days = ["Monday", "Tuesay", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    no_days = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
    return en_days[no_days.index(day.lower())]


def format_date(date_: str) -> str:
    """Reformats a date string given as 'year-mm-dd hh:mm:ss' to 'dd Month' (with month names)."""
    date_ = date_.split(" ")[0]
    month = month_index_to_name(int(date_[5:7]))
    day = date_[8:]
    return day + " " + month


def get_date_object(date_: str) -> datetime.date:
    """Creates a datatime.date object from given date string.
    String can either be in the 'yyyy-mm-dd' format or 'dd Month' (with month names) format, in
    the latter case the year will be the current year.."""
    if "-" in date_:
        year, monthi, day = date_.split("-")
    else:
        year = date.today().year
        day, month = date_.split(" ")
        monthi = month_name_to_index(month)
    return date(int(year), int(monthi), int(day))


def timezone_to_oslo(time: "pandas.Timestamp") -> str:
    """Converts a time of pandas.Timestamp object to norwegian timezone."""
    no_time = time.tz_localize("Europe/Oslo")
    out_time = str(no_time).split(" ")[1]

    # Add the timezone conversion to the total time (f.ex: 20:00:00+02:00 to 22:00:00)
    hour = int(out_time[:2])
    hour_add = int(out_time[8:11])
    hour_corrected = hour + hour_add

    out_time = str(hour_corrected) + out_time[2:5]
    return out_time


def get_event_date_str(event: fastf1.events.Event) -> str:
    """Gets event date string and cuts away the time info from a fast.f1.events.Events object.
    Formatted like '07 May'"""
    return format_date(str(event["EventDate"]).split(" ")[0])


def get_event_date_object(event: Union[str, fastf1.events.Event]) -> datetime.date:
    """Get the sunday event date as datetime.date object."""
    if not isinstance(event, str):
        event = str(event["EventDate"]).split(" ")[0]
    date_ = get_sunday_date_object(event)
    return date_


def local_time_to_oslo(local_time: str, country: str) -> str:
    """Converts local time to Oslo time."""
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

    return oslo_time.time().isoformat(timespec="minutes")


def get_country_code(country_name: str) -> Union[str, None]:
    """Returns the ISO code for a given country name."""
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


def get_number_remaining_events(date_: datetime.date) -> int:
    """Returns int of how many remaining f1 events there are from a given date."""
    dt = datetime.combine(date_, datetime.min.time())
    remaining_schedule = fastf1.get_events_remaining(dt, include_testing=False)
    return len(remaining_schedule)


def file_exists(filename: str) -> bool:
    """Checks if a file exists."""
    try:
        with open(filename, "r"):
            pass
        return True
    except FileNotFoundError:
        return False


def get_default_archive_filename(filename: str, folder: str = "archived_data") -> str:
    """Returns an archive filename for a given json filename, defaults into folder 'archived_data'."""
    year = date.today().year - 1
    temp = filename.replace(".json", "")
    return f"{folder}/archived_{temp}_{year}.json"


def archive_json(filename: str, archive_filename: str = None) -> None:
    """Archives the given json and creates a new blank json with the same name. If the archived file
    already exist, update it instead of creating a new one."""
    if archive_filename is None:
        archive_filename = get_default_archive_filename(filename)

    if file_exists(archive_filename):  # if archive already exists update it
        with open(filename, "r") as infile:
            data = json.load(infile)
            update_existing_json(data, archive_filename)

    else:
        os.rename(filename, archive_filename)

        # Create new blank file
    with open(filename, "w") as new_file:
        json.dump({}, new_file, indent=3)


def extract_json_data(json_file: str = "data/f2_calendar.json") -> F2CalendarType:
    """Extracts data from the given json file."""
    with open(json_file, "r") as infile:
        return json.load(infile)


def get_hours_between_datetimes(datetime1, datetime2):
    """Returns the hours between two datetime objects."""
    return abs((datetime1 - datetime2).total_seconds() / 3600)


def get_hours_until_next_scheduled_hour(scheduled_hour: int) -> float:
    """Returns the hours until the next given scheduled hour."""
    now = datetime.now()
    scheduled_datetime = datetime(now.year, now.month, now.day, scheduled_hour, 0, 0)
    if get_hours_between_datetimes(now, scheduled_datetime) > 24:
        scheduled_datetime += timedelta(days=1)
    return get_hours_between_datetimes(now, scheduled_datetime)


async def startup_check() -> None:
    """Checks if the 'discord_data' and 'f2_race_ids' json files exists, asks the user if they want to create them.
    If they exists, then it also checks if all the keys are present."""
    discord_data_values, f2_race_id_values = False, False
    discord_data_exists = file_exists("data/discord_data.json")
    if not discord_data_exists:
        print("No 'data/discord_data.json' file found, do you want to create one? (y/n)")
        answer = input("> ")
        if answer.lower() == "y":
            await create_json("data/discord_data.json")
    discord_data_exists = file_exists("data/discord_data.json")
    if discord_data_exists:   # was the file was created above?
        discord_data_values = await check_json_values("data/discord_data.json")  # missing values?

    f2_race_ids_exists = file_exists("data/f2_race_ids.json")
    if not f2_race_ids_exists:
        print("No 'data/f2_race_ids.json' file found, do you want to create one? (y/n)")
        answer = input("> ")
        if answer.lower() == "y":
            await create_json("data/f2_race_ids.json")
    f2_race_ids_exists = file_exists("data/f2_race_ids.json")
    if f2_race_ids_exists:  # was the file was created above?
        f2_race_id_values = await check_json_values("data/f2_race_ids.json")  # missing values?

    # Check which of the files are missing, or both:
    missing_files = []
    if not discord_data_exists:
        missing_files.append("data/discord_data.json")
    if not f2_race_ids_exists:
        missing_files.append("data/f2_race_ids.json")
    if missing_files:
        print(f"Missing the following json files: {missing_files}. Please restart the bot "
              f"or add them manually.\nExiting...")
        exit(1)
    # Check which of the files are missing required values, or both:
    missing_file_values = []
    if not discord_data_values:
        missing_file_values.append("data/discord_data.json")
    if not f2_race_id_values:
        missing_file_values.append("data/f2_race_ids.json")
    if missing_file_values:
        print(f"The following json files are missing required values: {missing_file_values}. Please restart the bot"
              f" or add them manually.\nExiting...")
        exit(1)


async def create_json(file: str, default_data: dict[str: str] = None) -> None:
    """Creates a new json file."""
    if default_data is None:
        if file == "data/discord_data.json":
            with open("data/template_discord_data.json", "r") as infile:
                default_data = json.load(infile)
        elif file == "data/f2_race_ids.json":
            default_data = {
                "f2_first_raceid": "1050",
                "f2_last_raceid": "1063"
            }
        else:
            raise NotImplementedError(f"util.create_json() default data not implemented for '{file}',"
                                      f"please input a dictionary with key-value pairs.")
    print(f"Creating new {file} file...")
    with open(file, "w") as outfile:
        json.dump(default_data, outfile, indent=3)


async def check_json_values(file: str, required_value_keys: list[str] = None) -> bool:
    """Checks if every needed value is present in a given json file."""
    if required_value_keys is None:
        if file == "data/discord_data.json":
            required_value_keys = ["bot_token", "bot_id", "channel_id"]
        elif file == "data/f2_race_ids.json":
            required_value_keys = ["f2_first_raceid", "f2_last_raceid"]
        else:
            raise NotImplementedError(f"util.check_json_values() list of required value keys not implemented"
                                      f"for '{file}, please input a list of strings with the required keys.")
    with open(file, "r") as infile:
        data = json.load(infile)
        for key in required_value_keys:
            if not data.get(key):   # empty value
                print(f"'{key}' value not found in '{file}', do you want to add it? (y/n)")
                answer = input("> ")
                if answer.lower() == "y":
                    print(f"Enter the value for '{key}':")
                    value = input("> ")
                    data[key] = value
    with open(file, "w") as outfile:
        json.dump(data, outfile, indent=3)
    with open(file, "r") as infile:  # now check if all the required values are present
        data = json.load(infile)
        all_values_set = all(data.get(key) for key in required_value_keys)
    return all_values_set