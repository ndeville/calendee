####################
# CALENDEE

import os
import sys

from dotenv import load_dotenv
load_dotenv()
USER_PATH = os.getenv("USER_PATH")

import pprint
pp = pprint.PrettyPrinter(indent=4)

from datetime import datetime, time, timezone, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import subprocess

# for pasting
from pynput.keyboard import Key, Controller
keyb = Controller()

# Email addresses of calendars to check
EMAIL_BB = os.getenv("EMAIL_BB")
EMAIL_DV = os.getenv("EMAIL_DV")
EMAIL_DR = os.getenv("EMAIL_DR")

print("\n\n")

####################
# GLOBAL VARIABLES

test = True

slot = 30 # minutes

# How many weekdays forward to check for availability
weekdays_forward = 3 

available_days = [ 
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri",
]

# Comment lines below to make unavailable
available_hours = [ 
    # "08:00",
    # "09:00",
    # "10:00",
    "11:00",
    # "11:30",
    "12:00",
    # "13:00",
    # "14:00",
    # "15:00",
    "16:00",
    # "16:30",
    "17:00",
    # "18:00",
    # "19:00",
]

# This will define the return time & format
timezones = { 
    "CET": 0, # default
    "AP": 0, # NOT a timezone. Short for Am/Pm / returns CET timezone but in am/pm format
    "UK": -1, # timezone offset in hours
    "ET": -6,
    "MT": -7,
    "PT": -9,
    "IST": 4.5, # Indian Standard Time (New Delhi)
    "IT": 4.5, # Indian Standard Time (New Delhi)
}

####################

# OUTPUT FUNCTIONS

def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))
    print(f"\nOUTPUT COPIED TO CLIPBOARD\n")

def paste():
    with keyb.pressed(Key.cmd):
        keyb.press('f')
        keyb.release('f')

# DAY FUNCTIONS

def is_weekday(date):
    """
    Returns True if the given date is a weekday (Monday to Friday),
    and False if it's a weekend day (Saturday or Sunday).
    """
    return date.weekday() < 5

def suffix(day): # day == datetime object
    if 11 <= day.day <= 13:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day.day % 10, 'th')

def format_day(datetime_object):
    
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)

    day = datetime_object.day

    # Use the custom suffix() function to determine the appropriate suffix for the day
    suffix_str = suffix(datetime_object)
    # Final day name format
    day_name = datetime_object.strftime("%a %e" + suffix_str)

    if day == tomorrow.day:
        formatted_day = f"tomorrow"
    else:
        formatted_day = f"{day_name}"

    return formatted_day

def format_time(datetime_object, ampm=False):

    if not ampm:
        formatted_time = datetime_object.strftime("%H:%M")
    else:
        formatted_time = datetime_object.strftime("%-I%p").lower()

        if formatted_time.endswith(":00"):
            formatted_time = formatted_time[:-3]
        if formatted_time.startswith("0"):
            formatted_time = formatted_time[1:]

    return formatted_time

# EXISTING EVENTS

def get_all_events(calendar_id, token, test=False):
    """
    Gets all future events from a Google Calendar
    """
    # Set up Google API credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(token, scopes=SCOPES)
    creds = credentials.with_subject(calendar_id)

    # Build the Google Calendar API client
    service = build('calendar', 'v3', credentials=creds)


    # Get the current time in UTC
    now = datetime.utcnow()
    now_formatted = now.isoformat() + 'Z'

    # Set the maximum time to be 1 month in the future (covers potential holidays)
    max_time = now + timedelta(days=30)
    max_time_formatted = max_time.isoformat() + 'Z'

    # Call the Google Calendar API to get events
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now_formatted,
        timeMax=max_time_formatted,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    if test:
        print(f"\n{events_result}:")
        pp.pprint(events_result)

    # Get the events from the response
    events = events_result.get('items', [])

    return events

def list_of_events_datetimes(events):
    """
    Takes list of events dicts from Google Calendar
    Returns list of datetimes tuples with start & end times for each event
    """
    events_datetimes_list = []
    for event in events:
        try:
            start = event['start']['dateTime']
            start_datetime = datetime.fromisoformat(start).replace(tzinfo=None) # Timezone-naive

            end = event['end']['dateTime']
            end_datetime = datetime.fromisoformat(end).replace(tzinfo=None) # Timezone-naive

            events_datetimes_list.append((start_datetime, end_datetime))
        except KeyError:
            print("\nNo start time for this event: ", event['summary'], "\n")
            pass

    return events_datetimes_list


# FINAL AVAILABILITIES

def get_final_availabilities(availabilities, consolidated_events):
    final_availabilities = []
    for start_time, end_time in availabilities:
        available = True
        for booked_start, booked_end in consolidated_events:
            if start_time < booked_end and booked_start < end_time:
                available = False
                break
        if available:
            final_availabilities.append(start_time)
    return final_availabilities

def generate_availabilities(final_availabilities, timezone='CET'): # CET timezone is default
    """
    Generate text output of availabilities to be pasted 
    """

    # Intro line, indicating timezone of availabilities
    if timezone == 'CET':
        output = "(CET / Germany time)\n"
        ampm = False
    elif timezone == 'AP': # short for Am/Pm / returns CET timezone in am/pm format
        output = "(CET / Germany time)\n"
        ampm = True
    elif timezone == 'UK':
        output = "(UK time)\n"
        ampm = True
    elif timezone == 'ET':
        output = "(ET)\n"
        ampm = True
    elif timezone == 'MT':
        output = "(MT)\n"
        ampm = True
    elif timezone == 'PT':
        output = "(PT)\n"
        ampm = True
    elif timezone in ['IST', 'IT']:
        output = "(IST)\n"
        ampm = True

    time_offset = timezones[timezone]

    # Generate the availabilities
    day = False
    for a in final_availabilities:
        a = a + timedelta(hours=time_offset) # convert to recipient timezone
        if day != a.date():
            output = f"{output}\n- {format_day(a)}\t{format_time(a, ampm=ampm)}"
            day = a.date()
        else:
            output = f"{output}, {format_time(a, ampm=ampm)}"
    
    # Outro line: Add a link to the calendar
    # output = f"{output}\n\nor see all at https://cal.com/ndeville"
        
    # Replace the last comma with "or"
    lines = output.split('\n')  # Split the text into lines
    for i in range(1, len(lines)):  # Skip the first line (header)
        if ',' in lines[i]:  # Check if there is a comma in the line
            lst = lines[i].rsplit(", ", 1)  # Split the line from the right side by the last comma
            lines[i] = " or ".join(lst)  # Join the resulting list with "or" as the last element
    final_output = '\n'.join(lines)  # Join the lines back into a single string

    print(final_output)
    return final_output

# MAIN FUNCTION

def get_my_availabilities(timezone="CET", slot=slot, weekdays_forward=weekdays_forward, test=False):
    """
    slot = 30 # minutes
    weekdays_forward = 3 # number of weekdays to look forward and return availabilities for
    """
    global available_days
    global available_hours
    global timezones

    # DAYS

    now = datetime.now()

    today = now.date()

    days_to_check = []
    for x in range(1,20): # random high number of days to check for availability
        day_to_check = today + timedelta(days=x)
        if is_weekday(day_to_check) and len(days_to_check) < weekdays_forward:
            days_to_check.append(day_to_check)

    if test:
        print("\ndays_to_check:")
        pp.pprint(days_to_check)
        print()

    # BLANK AVAILABILITIES (CET)

    availabilities = []

    for day_string in days_to_check:
        for hour in available_hours:

            # Create a START datetime object from the input date and time
            datetime_object_start = datetime.combine(day_string, time.fromisoformat(hour))
            # Create a timedelta object from the global slot variable
            delta = timedelta(minutes=slot)
            # Add the timedelta to the END datetime object
            datetime_object_end = datetime_object_start + delta

            availabilities.append((datetime_object_start, datetime_object_end))

    if test:
        print(f"\navailabilities:")
        pp.pprint(availabilities)

    # CONSOLIDATED EVENTS

    datetimes_list_bb = []
    datetimes_list_dv = []


    # BB
    all_future_events_bb = get_all_events(EMAIL_BB, f'{USER_PATH}creds_bb/service_key.json')
    datetimes_list_bb = list_of_events_datetimes(all_future_events_bb)
        
    if test:
        print(f"\ndatetimes_list_bb:")
        pp.pprint(datetimes_list_bb)


    # DV
    all_future_events_dv = get_all_events(EMAIL_DV, f'{USER_PATH}creds_dv/service_key.json')
    datetimes_list_dv = list_of_events_datetimes(all_future_events_dv)
        
    if test:
        print(f"\ndatetimes_list_dv:")
        pp.pprint(datetimes_list_dv)


    # # DR
    # all_future_events_dr = get_all_events(EMAIL_DR, f'{USER_PATH}creds_dr/service_key.json')
    # datetimes_list_dr = list_of_events_datetimes(all_future_events_dr)

    # if test:
    #     print(f"\ndatetimes_list_dr:")
    #     pp.pprint(datetimes_list_dr)


    # Consolidate all events
    consolidated_events = datetimes_list_bb + datetimes_list_dv
    consolidated_events = sorted(consolidated_events, key=lambda x: x[0]) # sorted by start time

    if test:
        print(f"\nconsolidated_events:")
        pp.pprint(consolidated_events)
        print()

    # FINAL AVAILABILITIES

    final_availabilities = get_final_availabilities(availabilities, consolidated_events)

    if test:
        print(f"\nfinal_availabilities:")
        pp.pprint(final_availabilities)

    print("\n\n")
    output_my_availabilities = generate_availabilities(final_availabilities, timezone=timezone)

    return output_my_availabilities

########################################################################################################

if __name__ == '__main__':
    print()
    arguments = sys.argv

    # Get timezone argument, if passed
    if len(sys.argv) > 1: 
        tz = sys.argv[1].upper()
    else:
        tz = "CET"
    print(f"tz: {tz}")

    # Generate availabilities
    my_availabilities = get_my_availabilities(timezone=tz)

    # Write to clipboard
    write_to_clipboard(my_availabilities)

    # Paste availabilities
    paste()