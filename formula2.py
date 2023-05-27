import requests
import json
from bs4 import BeautifulSoup
from typing import Union

import util

def scrape_calendar() -> dict[str, list[Union[str, list[str]]]]:
    """
    Scrapes the F2 schedule from the F2 ebsite. Returns a dictionary mapping
    the sunday dates to the event infos.
    All credit goes to ENils1: https://github.com/ENils1
    """
    f2_events = {}

    for i in range(1054, 1064):
        url = f'https://www.fiaformula2.com/Results?raceid={i}'
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            country = soup.find("div", {"class": "country-circuit-name"}).text
            if "-" in country: # If circuit name is more than the country like 'Italy-Emilia Romagna'
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
                            start = util.get_oslo_time(start, country)
                            stop = util.get_oslo_time(stop, country)
                            race[2] = f"{start}-{stop}"

                # Format times, add zero to beginning or end so the times are formatted as: "15:55-16:25"
                for j in range(len(race)):
                    jrace = race[j]
                    if not ":" in jrace:
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

def store_calendar_to_json(calendar: dict[str, list[Union[str, list[str]]]],
                           json_file: str = "f2_calendar.json") -> None:
    """Saves f2 calendar data taken from scrape_calendar() and saves it to json, but only if there is new information.
    Used to store old timing data since the timings dissapear on the f2 website as soon as the first weeks event starts.
    """
    if not util.check_file_exists(json_file):
        with open(json_file,"w") as outfile:
            json.dump(calendar,outfile,indent=3)
        return

    util.update_existing_json(calendar,json_file)


def extract_days(event:"fastf1.events.Event", f2_calendar) -> Union[dict,dict[str,list[list[str]]]]:
    """Extracts and sorts from dictionary the F2 sessions of given event as fastf1.Event object.
    Returns a dictionary mapping session days to session names and times.

    Input dictionary is formatted as such:
    'f2_calendar = {'21 May': ('Round 5', 'Italy-Emilia Romagna', 'Imola', '19-21 May 2023',
                          [['Qualifying Session', 'Friday', '15:55-16:25'],
                           ['Sprint Race', 'Saturday', '10:35-11:20'],
                           ['Feature Race', 'Sunday', 'TBC']])
                           }'
    Output dictionary is formatted as such:
    return  {'Friday': [['Qualifying Group A', '15:55-16:25'],['Qualifying Group B', 'TBC']],
            'Saturday': [['Sprint Race', '10:35-11:20']],
            'Sunday': [['Feature Race', 'TBC']]}
            }
    """
    event_date = util.get_event_date_str(event)
    event_Date = util.get_event_date_object(event)

    if check_race_week(event_Date, f2_calendar):
        f2_event = f2_calendar[event_date][4]

        session_days = {}
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
    else:
        return {}

def check_race_week(date_:"datetime.date", f2_calendar):
    """Boolean return for if the given date (datetime.date object) is a f2 race week."""
    sunday = util.get_sunday_date_str(date_)
    if util.format_date(str(sunday)) in list(f2_calendar.keys()):
        return True
    else:
        return False
