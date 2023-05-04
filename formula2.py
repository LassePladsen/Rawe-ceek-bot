from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup

from Util import *


def get_calendar():
    formula_2 = {}

    for i in range(1054, 1064):
        url = f'https://www.fiaformula2.com/Results?raceid={i}'
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        country = soup.find("div", {"class": "country-circuit-name"}).text
        circuit = soup.find("div", {"class": "country-circuit"}).text
        round_number, date = soup.find("div", {"class": "schedule"}).text.split("|")
        raceday = date.split("-")[1][:-5]
        sessions = soup.find_all("div", {"class": "pin"})
        races = []
        print(raceday)
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
                        start = get_gmt_plus_one(start, country)
                        stop = get_gmt_plus_one(stop, country)
                        race[2] = f"{start}-{stop}"
                races.append(race)

        formula_2[raceday] = round_number.strip(), country, circuit, date, races
    return formula_2

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

def extract_f2_days(Event, dictionary):
    """Extracts and sorts from dictionary the F2 sessions of given event as fastf1.Event object.
    Returns a dictionary mapping session days to session names and times.

    Input dictionary is formatted as such:
    'dictionary = {'21 May': ('Round 5', 'Italy-Emilia Romagna', 'Imola', '19-21 May 2023',
                          [['Qualifying Session', 'Friday', '15:55-16:25'],
                           ['Sprint Race', 'Saturday', '10:35-11:20'],
                           ['Feature Race', 'Sunday', 'TBC']])
                           }'
    Output dictionary is formatted as such:
    return  {'Friday': ['Qualifying Session', '15:55-16:25'],
            'Saturday': ['Sprint Race', '10:35-11:20'],
            'Sunday': ['Feature Race', 'TBC']}
            }
    """
    event_date = get_event_date(Event)
    f2_event = dictionary[event_date][4]

    session_days = {}
    for day in f2_event:
        dayname = day.pop(1)
        session_days[dayname] = day
    return session_days


def check_f2_race_week():
    """Boolean check for if the current week is a f1 race week."""
    f2_cal = get_calendar()


def get_event_date(Event):
    """Gets event date from fastf1.Event object and cuts away the time info."""
    return reformat_date(str(Event["EventDate"]).split(" ")[0])