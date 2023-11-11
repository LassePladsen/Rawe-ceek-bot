import json
import logging
from typing import Union

import requests
from bs4 import BeautifulSoup

from util import (local_time_to_oslo, file_exists, update_f2cal_json, format_date, extract_json_data,
                  get_sunday_date_str, get_event_date_str, get_json_data)

F2CalendarType = dict[str, list[Union[str, list[str]]]]


def scrape_calendar(logger: Union[logging.Logger, None] = None) -> F2CalendarType:
    """
    Scrapes the F2 schedule from the F2 website. Returns a dictionary mapping
    the sunday dates to the event infos.
    All credit goes to ENils1: https://github.com/ENils1

    Optional argument is a logging.Logger to log to.
    """
    f2_events = {}

    race_ids_json_filename = "data/f2_race_ids.json"
    first_race_id = int(get_json_data("f2_first_raceid", file=race_ids_json_filename))
    last_race_id = int(get_json_data("f2_last_raceid", file=race_ids_json_filename))
    for i in range(first_race_id, last_race_id + 1):
        url = f'https://www.fiaformula2.com/Results?raceid={i}'
        response = requests.get(url)

        # response is not ok -> skip this race event 
        if not 200 <= response.status_code < 300:
            if logger:
                logger.error(f"formula2.scrape_calendar(): reponse.status_code not in [200, 300) for url '{url}', continuing next event.")
            continue


        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            country = soup.find("div", {"class": "country-circuit-name"}).text
            if "-" in country:  # If circuit name is more than the country like 'Italy-Emilia Romagna'
                country = country.split("-")[0]

            circuit = soup.find("div", {"class": "country-circuit"}).text
            round_number, date = soup.find("div", {"class": "schedule"}).text.split("|")
            raceday = date.split("-")[1][:-5]
            sessions = soup.find_all("div", {"class": "pin"})
            races = []
            for session in sessions:
                race = []
                for elements in session:
                    if "displayed" in elements.text:
                        continue
                    race.append(elements.text)
                if "Free Practice" in race:
                    continue
                if len(race) > 0:
                    if len(race) == 3:
                        time = race[2]
                        if time != "TBC":
                            start, stop = time.split("-")
                            start = local_time_to_oslo(start, country)
                            stop = local_time_to_oslo(stop, country)
                            race[2] = f"{start}-{stop}"
                # Format times, add zero to beginning or end so the times are formatted as: "15:55-16:25"
                for j in range(len(race)):
                    jrace = race[j]
                    if ":" not in jrace:
                        continue
                    if len(jrace) != 11:
                        if jrace[-2] == ":":  # missing trailing zero
                            jrace += "0"
                        elif jrace[0] != "0":  # missing beginning zero
                            jrace = "0" + jrace
                    race[j] = jrace
                    races.append(race)

            f2_events[raceday] = [round_number.strip(), country, circuit, date, races]

        except AttributeError:  # catch exception for if race weekend has been cancelled
            continue

    return f2_events


def store_calendar_to_json(calendar: F2CalendarType,
                           json_file: str = "data/f2_calendar.json") -> None:
    """Saves f2 calendar data taken from scrape_calendar() and saves it to a json file.
    Used to store old timing data since the timings dissapear on the f2 website as soon as the first weeks event starts.
    """
    if not file_exists(json_file):
        with open(json_file, "w") as outfile:
            json.dump(calendar, outfile, indent=3)
    else:
        update_f2cal_json(calendar, json_file)


def extract_days(event: "fastf1.events.Event",
                 f2_calendar: F2CalendarType) -> Union[dict, dict[str, list[list[str]]]]:
    """Extracts and sorts from dictionary the F2 sessions of given event as fastf1.Event object.
    Returns a dictionary mapping session days to session names and times.
    """
    event_date = get_event_date_str(event)
    session_days = {}
    try:
        f2_event = f2_calendar[event_date][4]
    except KeyError:
        return session_days

    for day in f2_event:
        try:
            dayname = day.pop(1)
        except IndexError:
            continue

        # Initialize list in the dictionary for seperate each day if it hasnt already
        if dayname not in list(session_days.keys()):
            session_days[dayname] = [day]
        else:
            session_days[dayname].append(day)
    return session_days


def is_f2_race_week(date_: Union[str, "datetime.date"]) -> bool:
    """Boolean return for if the given date is a f2 race week."""
    if not isinstance(date_, str):
        date_ = str(date_)
    sunday = get_sunday_date_str(date_)
    f2_calendar = extract_json_data()
    if format_date(sunday) in list(f2_calendar.keys()):
        return True
    else:
        return False
