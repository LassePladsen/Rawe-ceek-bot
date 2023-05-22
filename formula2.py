import requests
from bs4 import BeautifulSoup

import util

def get_calendar():
    """
    Scrapes the F2 schedule from the F2 ebsite. Returns a dictionary mapping
    the sunday dates to the event infos.
    All credit goes to ENils1: https://github.com/ENils1
    """
    formula_2 = {}

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
                    races.append(race)

            formula_2[raceday] = round_number.strip(), country, circuit, date, races
        except AttributeError:  # catch exception for if race weekend has been cancelled
            continue
        return formula_2

def extract_days(Event, f2_calendar):
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
    event_date = util.get_event_date_str(Event)
    event_Date = util.get_event_Date(Event)

    if check_race_week(event_Date, f2_calendar):
        f2_event = f2_calendar[event_date][4]

        session_days = {}
        for day in f2_event:
            dayname = day.pop(1)

            # Initialize list in the dictionary for seperate each day if it hasnt already
            if dayname not in list(session_days.keys()):
                session_days[dayname] = [day]
            else:
                session_days[dayname].append(day)
        return session_days
    else:
        return []

def check_race_week(Date, f2_calendar):
    """Boolean return for if the given date (datetime.date object) is a f2 race week."""
    sunday = util.get_sunday_date(Date)
    if util.format_date(str(sunday)) in list(f2_calendar.keys()):
        return True
    else:
        return False
