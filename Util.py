from datetime import date
import calendar

today = date.today()


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

def reformat_date(date):
    """Reformats a date given as 'year-mm-dd hh:mm:ss' to 'dd Month' with month names."""
    date = date.split(" ")[0]
    month = month_index_to_name(int(date[5:7]))
    day = date[8:]
    return day + " " + month

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





# DEBUGGING/TESTING:
if __name__ == "__main__":
    from formula2 import *
    from formula1 import *

    Event = get_week_event(today)
    # Event = get_week_event(date(2023,5,25))
    # print(Event)
    # print_event(Event)
    fri,satur,sun = sort_f1_sessions_by_day(Event)
    f2_test = {'21 May': ('Round 5', 'Italy-Emilia Romagna', 'Imola', '19-21 May 2023',
                          [['Qualifying Session', 'Friday', '15:55-16:25'],
                           ['Sprint Race', 'Saturday', '10:35-11:20'],
                           ['Feature Race', 'Sunday', 'TBC']]),
               '28 May': ('Round 6', 'Monaco', 'Monte Carlo', '25-28 May 2023',
                          [['Qualifying Group A', 'Thursday', 'TBC'],
                           ['Qualifying Group B', 'Thursday', 'TBC'],
                           ['Sprint Race', 'Friday', '10:40-10:40'],
                           ['Feature Race', 'Sunday', 'TBC']])}

    f2 = extract_f2_days(Event,f2_test)
    f2_fri = f2["Friday"]
    f2_satur = f2["Saturday"]
    f2_sun = f2["Sunday"]

    # print(f2_friday)
    # print(extract_f2_days(Event, f2_test))
    print_day_sessions("Fredag",f2_fri,fri)
    print_day_sessions("Lørdag",f2_satur,satur)
    print_day_sessions("Søndag",f2_sun,sun)
